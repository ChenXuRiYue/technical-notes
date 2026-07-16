# 📌 async、await 与阻塞任务

Rust 的 `async`/`.await` 用来表达可暂停并在稍后继续的计算。`async fn` 本身不会创建线程,`.await` 也不代表阻塞整个程序。Future 由异步 runtime 调度;如果 Future 内部直接调用长时同步 I/O 或重 CPU 函数,执行它的 runtime 线程仍会被阻塞。

## 📄 `async fn` 返回 Future

普通函数调用时立即执行函数体:

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

let value = add(1, 2);
```

`async fn` 调用时会返回一个 Future:

```rust
async fn load() -> Result<String, LoadError> {
    Ok("data".to_string())
}

let future = load();
```

等价的简化类型理解:

```rust
fn load() -> impl Future<Output = Result<String, LoadError>>
```

Future 是“未来可能产生一个 `Output` 的计算”。它需要被 runtime 持续 poll 才能向前执行。Rust 标准库定义 Future 机制,但通常由 Tokio、async-std、Tauri runtime 等提供 executor、定时器和异步 I/O。

## 📄 `.await` 暂停当前异步任务

```rust
async fn load_user() -> Result<User, LoadError> {
    let bytes = read_bytes().await?;
    let user = decode(bytes)?;
    Ok(user)
}
```

`.await` 可读成:

```text
当 read_bytes 尚未准备好
  -> 保存 load_user 的暂停状态
  -> 把执行权还给 runtime
  -> runtime 可以执行其他已就绪任务

当 read_bytes 准备好
  -> runtime 再次 poll load_user
  -> 从 await 后继续
```

`.await` 只能在 async 上下文中使用。它暂停的是当前 Future,不是整个操作系统线程的语法等价物。

## 📄 任务、Future 与线程不是同一概念

```text
Future  -> 可暂停计算的状态表示
Task    -> runtime 调度的 Future
Thread  -> 操作系统执行单元
```

一个线程可以交错执行多个异步 task;一个多线程 runtime 也可以在多个线程上调度 task。

```rust
async fn work() { /* ... */ }
```

只能说 `work()` 产生 Future,不能仅凭 `async` 断定它将在哪个线程运行或是否与其他工作并行。

## 📄 async 函数中仍可能有阻塞代码

```rust
async fn build_site() -> Result<Report, Error> {
    std::fs::read_to_string("large-file.md")?;
    expensive_render()?;
    Ok(Report::new())
}
```

虽然函数是 `async`,同步文件 I/O 和长时 CPU 计算执行期间不会自动 `.await` 让出执行权。如果它们运行在 runtime worker 上,同一 worker 上的其他 task 可能无法及时运行。

判断标准:

| 工作 | 优先方式 |
| --- | --- |
| 有异步 API 的网络/文件 I/O | 使用 runtime 的异步 API |
| 必须使用同步库的较长任务 | `spawn_blocking` |
| 非常重的 CPU 任务 | 专用计算线程池或任务系统 |
| 极短的同步操作 | 直接执行通常更简单 |

## 📄 `spawn_blocking` 的作用

伪代码:

```rust
let output = runtime::spawn_blocking(move || {
    blocking_work(input)
})
.await;
```

```text
spawn_blocking
  -> 将同步闭包交给 runtime 的 blocking 线程池

move ||
  -> 把闭包需要的拥有值移进任务

.await
  -> 当前 async 任务等待 blocking 任务的返回值
```

`spawn_blocking` 不会把同步库变成真正的异步 I/O;它是将阻塞工作从主要异步 worker 隔离出去。

多数 runtime 中,一个 blocking 闭包已经开始执行后不能像普通 Future 那样在 `.await` 点协作取消。放弃 JoinHandle 可以表示不再等待结果,但同步闭包的文件、Git 或网络副作用可能仍会继续到函数返回。

## 📄 读懂 `spawn_blocking` 的两层 Result

如果闭包返回 `Result<T, WorkError>`:

```rust
let handle = runtime::spawn_blocking(move || blocking_work(input));
```

JoinHandle 的输出可简化为:

```text
Result<Result<T, WorkError>, JoinError>
       ^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^
       工作本身的结果      任务调度/panic 结果
```

因此常见:

```rust
runtime::spawn_blocking(move || blocking_work(input))
    .await
    .map_err(|join_error| AppError::Join(join_error))?
```

步骤:

```text
.await
  -> Result<Result<T, WorkError>, JoinError>

.map_err(...)?
  -> JoinError 被转型并提前返回
  -> 留下 Result<T, WorkError>
```

如果当前函数也能转换 `WorkError`,可能看到 `.await??`;Tauri command 中也常看到第一层 `?` 解开 join error 后,直接把内层 `Result<T, String>` 作为函数结果返回。

## 📄 借用、`move` 与任务生命周期

被 spawn 的任务可能比创建它的当前函数活得更久,因此 runtime 常要求闭包拥有自己使用的数据:

```rust
let input = String::from("data");

runtime::spawn_blocking(move || {
    process(input)
});
```

`move` 会把 `input` 移入闭包,之后外层不能再使用它。需要在多处使用时,应先判断是否真的需要独立副本、`Arc` 共享,或重新设计任务输入。

## 📄 持锁跨 `.await` 的风险

```rust
let guard = shared.lock().unwrap();
network_call().await;
use_value(&guard);
```

这表示网络等待期间锁一直未释放。其他任务可能长时等待,而 `std::sync::MutexGuard` 也可能导致 Future 不满足 `Send`。

优先方式:

```rust
let snapshot = {
    let guard = shared.lock().unwrap();
    guard.required_data().clone()
};

network_call(snapshot).await;
```

异步 mutex 允许等锁时让出执行权,但仍不意味着应该长时持锁跨外部 I/O。

## 📄 取消与副作用

Future 可能在 `.await` 边界被取消和销毁。一条用例如果是:

```text
写文件 A -> await -> 写文件 B
```

取消可能发生在两次副作用之间,留下部分完成的状态。异步语法不提供自动事务;重要流程需要单独设计幂等、原子替换、回滚或恢复机制。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写,AI 创建笔记时只保留占位,不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写,AI 创建笔记时只保留占位,不填充具体内容。

## 🗺️ 修订记录

| 日期 | 内容 |
| --- | --- |
| 2026-07-16 | 建立 Future、task、thread、spawn_blocking 和两层 Result 的阅读模型 |

## 🛠️ 实践经历

- GitTributary 的 `site_build` 和 `site_publish_pages` 是 async Tauri command,并使用 `tauri::async_runtime::spawn_blocking` 隔离同步 Git 和文件工作。
- `.await.map_err(|e| e.to_string())?` 处理 blocking 任务的 join error,内层 `Result<Report, String>` 继续作为 command 结果返回。
- 项目回链: [Tauri invoke 并发与后台任务决策](../../../开源项目/GitTributary/技术经验/Tauri%20invoke%20并发与后台任务决策.md)
- Command 链路: [Command 层代码阅读与架构演进](../../../开源项目/GitTributary/技术经验/Command%20层代码阅读与架构演进.md)

## ⚙️ prompt

```markdown
请分析一段 Rust 异步代码:
1. 列出每个 async fn 的 Future Output 类型。
2. 标出每个 await 的暂停点和可能取消点。
3. 区分异步 I/O、同步阻塞 I/O 和 CPU 工作。
4. 解释 spawn 的闭包为什么需要 move。
5. 展开 JoinHandle 和业务 Result 的每一层错误。
6. 检查是否持锁跨 await 以及取消后的部分副作用。
```

## 调研

当前内容已直接推广为稳定知识,暂无未晋升的调研材料。
