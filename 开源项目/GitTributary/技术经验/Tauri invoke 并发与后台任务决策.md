# Tauri invoke 并发与后台任务决策

> 记录时间: 2026-07-14
> 项目: GitTributary
> 问题起点: 希望非关键动作不阻碍前端主流程，同时弄清 Promise、`await`、Tauri IPC 和 Rust 后台执行之间的关系。

## 项目现场

GitTributary 的 React 前端会通过 Tauri `invoke` 调用 Rust 命令。例如，`App.tsx` 会保存“更多”菜单的展开状态：

```tsx
void invoke("store_set", {
  namespace: NAV_MORE_STATE_NS,
  key: NAV_MORE_STATE_KEY,
  value: {
    version: 1,
    open,
    updatedAt: Date.now(),
  } satisfies NavMoreUiState,
}).catch(() => {
  // 存储失败不能阻止用户展开或收起菜单。
});
```

这段代码的业务决策是：

```text
页面展开 / 收起是主流程
状态持久化是次要动作

先更新页面
  -> 发出存储请求
  -> 当前函数不等待存储结果
  -> 但仍然用 catch 承接失败
```

Rust 中对应的 `store_set` 会获取 Store 互斥锁，写入数据后发布变更事件：

```rust
#[tauri::command]
pub(crate) fn store_set(...) -> Result<(), String> {
    {
        let mut store = state.store.lock().unwrap();
        store.set(&namespace, &key, value)?;
    }

    // 公开命名空间还会发布 store.key.changed 事件。
    Ok(())
}
```

## 先分清四个概念

### 1. 异步

最终结果不在调用当下直接交付，而是稍后通过 Promise、回调或事件交付。

```ts
const resultPromise = invoke("store_set", options);
```

`resultPromise` 是未来的结果，不是 `store_set` 已经完成的证明。

### 2. 并发

多个任务的生命周期在时间上重叠。

```text
任务 A  |----------------|
任务 B      |---------|
```

它们不一定在同一时刻占用不同 CPU 核心，但 B 在 A 完成前已经启动。

### 3. 并行

多个任务真正在同一时刻执行，通常需要多线程、多进程或多核调度。

Promise 不能保证并行。实际是否并行，由 WebView、Tauri、Rust Runtime 和操作系统共同决定。

### 4. 当前函数是否等待

这是调用层的业务顺序选择：

```ts
await invoke("store_set", options);
doNextThing();
```

`doNextThing` 必须等待存储成功后执行。

```ts
void invoke("store_set", options).catch(reportError);
doNextThing();
```

`doNextThing` 不等待存储结果。

## 关键认知: await 不等于阻塞 UI 主线程

```ts
await invoke("store_set", options);
```

这句代码只会暂停当前 `async` 函数后续的执行，不会把整个 JavaScript UI 线程占住等待。在等待期间：

```text
当前 async 函数  -> 暂停在 await
React / WebView UI   -> 仍可渲染和处理其他事件
Tauri / Rust         -> 处理 invoke 请求
```

所以，删除 `await` 不是优化 UI 响应性的通用手段。它改变的主要是当前业务函数的执行顺序和错误责任。

## GitTributary 中的两类现有实践

### 次要 UI 状态: fire-and-forget

```ts
void invoke("store_set", options).catch((error) => {
  console.warn("状态保存失败", error);
});
```

适合：

```text
菜单展开状态
上次选中的标签
窗口布局
可丢失缓存
辅助日志和非关键统计
```

这里的 `void` 只表示当前层不使用 Promise 返回值。它不会启动异步、不会创建线程，也不会处理失败。

### Rust 阻塞工作: async command + spawn_blocking

GitTributary 的站点构建会调用同步的构建逻辑。它被放入 `spawn_blocking`：

```rust
#[tauri::command]
pub(crate) async fn site_build(
    config: SiteBuildConfig,
) -> Result<SiteBuildReport, String> {
    tauri::async_runtime::spawn_blocking(move || {
        gt_site::build_site(config).map_err(|e| e.to_string())
    })
    .await
    .map_err(|e| e.to_string())?
}
```

这个模式适合：

```text
同步文件 I/O
Git 操作
压缩 / 解压
站点构建
长时间 CPU 计算
其他可能长时间占用执行线程的同步库调用
```

完整路径是：

```text
React UI
  -> invoke("site_build")
  -> Tauri async command
  -> spawn_blocking 线程池
  -> gt_site::build_site
  -> Promise 收到结果
```

## 如何选型

```text
后续逻辑依赖这次结果吗？
  |
  +-- 是 --> await invoke(...)
  |          并在当前层处理或上抛失败
  |
  +-- 否 --> 这个任务失败后可以被忽略吗？
              |
              +-- 可降级 --> void invoke(...).catch(reportError)
              |
              +-- 不可丢 --> 返回 Promise，交给更合适的上层等待
```

Rust 侧再问：

```text
命令内部是否包含长时间同步阻塞工作？
  |
  +-- 否 --> 普通命令或 async command
  |
  +-- 是 --> async command + spawn_blocking
```

## 多个任务的并发与串行

### 并发发起

```ts
const first = invoke("command_a");
const second = invoke("command_b");

const [a, b] = await Promise.all([first, second]);
```

`command_a` 未完成时，`command_b` 已经启动，两个任务的生命周期可以重叠。

### 串行发起

```ts
const a = await invoke("command_a");
const b = await invoke("command_b");
```

`command_b` 只会在 `command_a` 完成后启动。如果 B 依赖 A，这种串行就是必要的。

## Store 中的并发与串行边界

多次 `invoke("store_set")` 可以同时处于“已发出、未完成”的状态，因此请求生命周期可以并发。

但 Rust 内部的 Store 由 Mutex 保护：

```rust
let mut store = state.store.lock().unwrap();
```

多个写入在真正进入 Store 修改区域时，需要竞争同一把锁：

```text
请求 A  ---- 获得锁 -- 写入 -- 释放锁
请求 B  ---- 等待锁 ---------- 写入 -- 释放锁
```

因此要分层表述：

```text
前端请求生命周期  -> 可以并发
Tauri 命令是否并行    -> 取决于 Runtime 调度
Store 关键区写入         -> 被 Mutex 串行化
```

## 不等待模式的主要风险

### 1. 失败无人处理

```ts
void invoke("store_set", options);
```

`void` 不会处理 Promise rejection。即使业务允许失败，也应该至少记录、上报或明确降级。

### 2. 写入顺序与最终状态

频繁发出多个不等待写入时，不能只凭调用外观假设完成顺序。对“最后一次状态必须生效”的场景，需要考虑：

```text
防抖 debounce
合并 coalesce
序列号 / updatedAt
在后端明确串行化
```

### 3. 应用退出时任务丢失

真正的后台 detached task 可能在应用退出时被中断。重要数据不能仅依赖“发出后不等待”。

### 4. 过量并发

拖拽、输入和滚动等高频事件不应每次都发起 IPC 写入。可先防抖：

```ts
clearTimeout(saveTimer);

saveTimer = setTimeout(() => {
  void invoke("store_set", options).catch(reportError);
}, 300);
```

防抖解决“少发请求”，异步解决“如何交付结果”，并发解决“任务生命周期是否重叠”。

## 项目中的简化决策表

| 任务 | 前端模式 | Rust 模式 |
| --- | --- | --- |
| 菜单展开状态、布局偏好 | `void invoke(...).catch(...)` | 快速命令 |
| 后续逻辑依赖的保存 | `await invoke(...)` | 返回明确的 `Result` |
| 删除、切分支、凭据修改 | `await invoke(...)` | 失败不能静默忽略 |
| Git、构建、压缩、同步文件 I/O | 可以 `await invoke(...)` | `async fn + spawn_blocking` |
| 长时间后台任务 | 启动后持有任务 ID | 后台执行 + 状态/进度事件 |
| 高频非关键保存 | debounce 后 `void invoke` | 必要时合并写入 |

## 当场需要补的知识

```text
JavaScript Promise 的结果与错误责任
await 暂停当前函数而非阻塞 UI 线程
异步、并发和并行的区别
Tauri invoke 的 IPC 请求/响应模型
Rust async runtime 与 spawn_blocking
Mutex 对关键区的串行化
fire-and-forget 的错误、顺序和生命周期风险
```

## 可抽取的通用知识

- 语言基础: Promise 是异步结果的表示，不是并发或并行本身。
- 语言基础: `await` 决定当前函数的后续顺序，`void` 只丢弃表达式结果。
- 全栈工程: UI 响应性、业务顺序、后端阻塞任务是三个不同的设计维度。
- 全栈工程: fire-and-forget 是一种业务可靠性取舍，不只是语法简写。
- 全栈工程: 外层请求可并发，内层关键区仍可由锁串行化。

## 回链

- 项目现场: `src/App.tsx`
- Rust Store 命令: `src-tauri/src/commands/store.rs`
- Rust 阻塞任务实践: `src-tauri/src/commands/site.rs`
- 项目导读: [App.tsx 前端应用外壳解读](./App.tsx%20前端应用外壳解读.md)
- 语言基础: [Promise 与异步调用处理](../../../语言基础/typescript/异步编程/Promise%20与异步调用处理.md)
- 全栈工程: [Tauri 进程模型](../../../全栈工程/Tauri/核心概念/进程模型.md)
- 全栈工程: [Tauri 进程间通信](../../../全栈工程/Tauri/核心概念/进程间通信.md)
