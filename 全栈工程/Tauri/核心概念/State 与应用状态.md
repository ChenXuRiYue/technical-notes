# 📌 Tauri State 与应用状态

Tauri 通过 `Builder::manage` 让应用托管一个长期存活的 Rust 状态值,command 再通过 `State<'_, T>` 借用该值。`State` 解决的是框架内状态定位与注入;`'_`、引用和 `Deref` 是 Rust 语言机制;内部是否需要 `Mutex` 则由共享可变性和并发访问方式决定。

## 📄 状态的注册与提取

注册:

```rust
use std::sync::Mutex;

struct AppState {
    counter: Mutex<u64>,
}

tauri::Builder::default()
    .manage(AppState {
        counter: Mutex::new(0),
    });
```

command 提取:

```rust
use tauri::State;

#[tauri::command]
fn increment(state: State<'_, AppState>) -> u64 {
    let mut counter = state.counter.lock().unwrap();
    *counter += 1;
    *counter
}
```

链路:

```text
Builder::manage(AppState)
  -> Tauri 运行时拥有 AppState
  -> command 执行时按类型查找 AppState
  -> State<'_, AppState> 在该次调用中借用状态
```

Tauri 管理的状态类型需要满足框架的线程安全和存活期要求,因为它可能被多个 command 共享访问。

## 📄 拆解 `State<'_, AppState>`

```text
State<..., ...>
  -> Tauri 提供的状态守卫/包装器

AppState
  -> 应用注册到 Tauri 的具体状态类型

'_ 
  -> 该 State 内部借用的匿名生命周期
  -> 由编译器在 command 调用中推断
```

`State<'_, AppState>` 不是拷贝一份 `AppState`,也不是把应用状态的所有权交给 command。command 只在使用期间获得一个借用包装器。

`'_` 不表示应用状态只存活很短。它描述的是“当前 `State` 借用有效多久”;底层受管状态由 Tauri 运行时长期拥有。

## 📄 `State` 为什么能像 `AppState` 一样访问

```rust
let counter = state.counter.lock().unwrap();
```

`State<'_, T>` 实现了向 `T` 的 `Deref`,因此 Rust 可以自动解引用:

```text
state.counter
大致可理解为
(*state).counter
```

同样,helper 接收 `&AppState` 时,通常可以传入:

```rust
fn use_state(state: &AppState) {}

#[tauri::command]
fn command(state: State<'_, AppState>) {
    use_state(&state);
}
```

`&State<'_, AppState>` 可通过 deref coercion 转成 `&AppState`。这是 Rust 借用与智能指针机制,不是 Tauri 再次查询了一份状态。

## 📄 为什么 `&AppState` 内部仍能修改数据

`State<'_, AppState>` 提供的主要是共享引用,command 通常不会拿到整个 `&mut AppState`。但多个 command 又需要修改共享数据,所以字段使用内部可变性容器:

```rust
struct AppState {
    repo: Mutex<Option<Repository>>,
}
```

```text
&AppState
  -> 不允许随意修改 AppState 字段

Mutex<Option<Repository>>
  -> 允许在运行时获得可变访问
  -> 要求先 lock
  -> 同一时刻只有一个修改者
```

`Mutex` 不是 `State` 语法的固定组成部分。完全不需要修改的配置可以直接放入状态;不同并发模型也可能使用 channel、RwLock 或专用服务对象。

## 📄 状态字段的设计问题

将数据放入全局 `AppState` 前应问:

| 问题 | 影响 |
| --- | --- |
| 它是否需要跨 command 长期存活? | 临时数据不应升格为全局状态 |
| 谁拥有修改权? | 决定是否暴露裸锁还是封装方法 |
| 访问是读多写少还是频繁写? | 影响 Mutex、RwLock、channel 等选型 |
| 操作是否包含长 I/O? | 不应长时持有状态锁 |
| 是否需要持久化? | `State` 只是内存所有者,不是持久化机制 |
| 测试是否必须启动 Tauri? | 可将应用逻辑提取为接收 `&AppState` 或更小依赖的 helper |

## 📄 Command 边界与可测试 helper

Tauri `State` 是框架提取器,普通 Rust 单元测试不宜为了测试业务规则而手动伪造它。可将函数分成:

```rust
fn do_work(state: &AppState, input: Input) -> Result<Output, Error> {
    // 可在纯 Rust 测试中调用
}

#[tauri::command]
fn command(
    input: Input,
    state: State<'_, AppState>,
) -> Result<Output, String> {
    do_work(&state, input).map_err(|error| error.to_string())
}
```

这个拆分将:

```text
State 提取与 IPC 错误转换 -> Tauri 边界
用例行为                         -> 普通 Rust helper/应用层
```

如果 helper 仍需要整个 `AppState`,随着项目增长还可继续缩小为具体依赖或 trait 端口。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写,AI 创建笔记时只保留占位,不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写,AI 创建笔记时只保留占位,不填充具体内容。

## 🗺️ 修订记录

| 日期 | 内容 |
| --- | --- |
| 2026-07-16 | 建立 Tauri 状态注册、提取、Rust 借用和内部可变性模型 |

## 🛠️ 实践经历

- GitTributary 的 `AppState` 包含 `repo`、`store`、`event_pool` 和 `node_registry`,由 Tauri 在启动时通过 `.manage(...)` 托管。
- Command 使用 `State<'_, AppState>` 提取状态,helper 改用 `&AppState` 后可以脱离 Tauri runtime 做单元测试。
- 项目回链: [Command 层代码阅读与架构演进](../../../开源项目/GitTributary/技术经验/Command%20层代码阅读与架构演进.md)
- Rust 生命周期: [生命周期确保引用有效](../../../语言基础/rust/9.泛型数据类型/9.3.生命周期确保引用有效.md)
- Rust 共享状态: [Mutex 与共享状态并发](../../../语言基础/rust/16.无畏并发/16.3.Mutex与共享状态并发.md)

## ⚙️ prompt

```markdown
请分析一个 Tauri State:
1. 找到 Builder::manage 的注册点和 command 的提取点。
2. 拆解 State<'_, T> 中的框架类型、生命周期和借用关系。
3. 标出 T 内部每个共享可变字段的同步机制。
4. 检查锁作用域、多锁顺序与长时 I/O。
5. 区分 Tauri 边界与可脱离 runtime 测试的应用 helper。
```

## 调研

当前内容已直接推广为稳定知识,暂无未晋升的调研材料。

