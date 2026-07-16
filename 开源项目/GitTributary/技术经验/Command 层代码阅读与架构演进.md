# Command 层代码阅读与架构演进

> 记录时间: 2026-07-16  
> 项目: GitTributary  
> 问题起点: 理解 `src-tauri/src/commands/` 的分层作用、Rust 语法以及后续架构演进方向。

## 项目现场

GitTributary 的一条典型调用链是:

```text
用户操作 React 界面
  -> TypeScript invoke("command_name", payload)
  -> #[tauri::command]
  -> 读取 AppState
  -> 调用 gt-git / gt-store / gt-site / gt-flow
  -> Git、文件系统或 ~/.git-tributary
  -> Result 序列化后返回前端
```

Command 层相关的主要位置:

| 位置 | 当前职责 |
| --- | --- |
| `src-tauri/src/lib.rs` | 创建 `AppState`,注册 command,组装 Tauri 应用 |
| `src-tauri/src/commands/mod.rs` | 声明 command 子模块及层次原则 |
| `src-tauri/src/commands/git.rs` | 本地 Git 命令与提交用例编排 |
| `src-tauri/src/commands/remote.rs` | Git 远端、凭据绑定与配置聚合 |
| `src-tauri/src/commands/store.rs` | Store 读写命令与变更事件 |
| `src-tauri/src/commands/sync.rs` | 数据中心同步用例编排 |
| `src-tauri/src/commands/site.rs` | 站点构建、Pages 发布和跨 crate 编排 |
| `src-tauri/src/commands/flow.rs` | Flow 读写命令与宿主 Action 执行器 |
| `src-tauri/crates/gt-*` | 尽量脱离 Tauri 的业务能力 |

## 一个 command 怎么读

以 `get_status` 为例:

```rust
#[tauri::command]
pub(crate) fn get_status(
    state: State<'_, AppState>,
) -> Result<Vec<FileStatus>, String> {
    let lock = state.repo.lock().unwrap();
    let repo = lock.as_ref().ok_or("尚未打开仓库")?;
    repo.status().map_err(|e| e.to_string())
}
```

不要按字符逐个翻译,而要分成五步:

```text
#[tauri::command]
  -> 这是前端可调用的 IPC 入口

pub(crate) fn get_status
  -> 在当前 crate 内可见的同步函数

State<'_, AppState>
  -> 借用 Tauri 管理的应用状态

Mutex<Option<GitRepo>>
  -> 先获得锁,再判断是否已打开仓库

Result<Vec<FileStatus>, String>
  -> 成功返回文件状态,失败返回可序列化字符串
```

读完签名后,再看函数体只做了哪些动作:

```text
拿 repo 锁 -> 取出 GitRepo -> 调用 gt-git -> 转换错误
```

这是当前最接近“薄适配层”的 command。

## 当前分层的真实含义

从物理目录看,项目是四层:

```text
React UI
  -> Tauri commands
  -> gt-* crates
  -> Git / 文件系统 / 本地数据
```

从逻辑职责看,实际是五层:

```text
用户界面
  -> IPC 接口适配
  -> 应用用例编排
  -> 领域/基础能力
  -> 外部资源
```

现阶段的 `commands/` 同时容纳了“IPC 接口适配”和“应用用例编排”。这不是概念上只有四层,而是两种逻辑职责暂时共用一个物理目录。

## 薄转发与应用编排的分界

### 薄转发

`get_status` 的主要职责是:

```text
取参数 -> 拿状态 -> 调一个 crate -> 转错误 -> 返回
```

这类逻辑留在 command 层很自然。

### 应用用例编排

`commit_all` 完成的是:

```text
获得仓库与分支
  -> 选择提交身份
  -> stage_all
  -> commit_with_identity
  -> 释放 repo 锁
  -> 发布 git.commit.created 事件
```

`sync_data_center_now` 完成的是:

```text
读取配置和 Token
  -> ensure_config_repo
  -> pull
  -> import
  -> export
  -> commit
  -> push
```

这些代码不是单个 Git 或 Store 原语,而是“GitTributary 完成一次用户意图”的顺序。因此它们属于应用层编排,只是当前还放在 command 文件中。

### 宿主接口实现

`AppFlowActionExecutor` 实现 `gt-flow` 定义的 `FlowActionExecutor` trait:

```rust
impl FlowActionExecutor for AppFlowActionExecutor<'_> {
    fn execute(...) -> gt_flow::Result<FlowActionOutcome> {
        // 把 Flow 节点映射到 GitTributary 的真实能力
    }
}
```

`gt-flow` 只负责解析和编排,不知道如何获取 GitTributary 凭据、状态或仓库。由宿主实现 trait 能保持 `gt-flow` 的依赖方向。

这段逻辑留在宿主 crate 是合理的,但未必需要永远留在 `commands/flow.rs` 中。

## Command 层重复出现的 Rust 阅读点

| 语法 | 项目中的含义 | 阅读问题 |
| --- | --- | --- |
| `#[tauri::command]` | 将 Rust 函数暴露为 IPC command | 前端用哪个 `invoke` 调用它? |
| `pub(crate)` | 当前 crate 内可见 | 是否只为 `lib.rs` 注册或内部复用? |
| `State<'_, AppState>` | 借用 Tauri 管理状态 | 这个命令访问了哪些共享资源? |
| `Mutex<T>` | 串行化共享可变状态 | 锁持有了多久,是否跨 I/O? |
| `Option<T>` | 值可能不存在 | `None` 是正常状态还是错误? |
| `Result<T, E>` | 操作可能失败 | 错误在哪一层被转换? |
| `?` | 失败时提前返回 | 前面成功的步骤需要回滚吗? |
| `&T` / `&mut T` | 只读/可变借用 | 数据是被借用还是被移动? |
| `drop(lock)` / `{}` | 提前释放锁 | 后续操作是否需要另一把锁? |
| `Serialize` / `Deserialize` | Rust 类型与 JSON 之间转换 | 这是输入 DTO 还是输出 DTO? |
| `async` / `spawn_blocking` | 异步命令与阻塞工作隔离 | 同步 Git/文件 I/O 运行在哪里? |
| `impl Trait for Type` | 宿主实现领域层扩展点 | trait 定义与具体实现分别在哪? |

这些语法不再全部挤在一篇项目笔记中,而是回到 Rust/Tauri 知识树:

| 项目代码 | 稳定知识 |
| --- | --- |
| `#[tauri::command]` | [Rust 宏与属性过程宏](../../../语言基础/rust/20.高级特性/20.5.宏.md) |
| `pub(crate)` | [模块与受限可见性](../../../语言基础/rust/6.使用包、Crate和模块管理不断增长的项目/6.2.定义模块来控制作用域和私有性.md) |
| `State<'_, AppState>` | [Tauri State 与应用状态](../../../全栈工程/Tauri/核心概念/State%20与应用状态.md) / [Rust 生命周期](../../../语言基础/rust/9.泛型数据类型/9.3.生命周期确保引用有效.md) |
| `&state`、`&path`、`&mut store` | [引用和借用](../../../语言基础/rust/3.所有权/3.2.引用和借用.md) |
| `Option<GitRepo>` | [Option 枚举与常用操作](../../../语言基础/rust/5.枚举和模式匹配/5.1.枚举的定义.md) |
| `Result<T, String>`、`?` | [用 Result 处理可恢复的错误](../../../语言基础/rust/8.错误处理/8.1.2用%20Result%20处理可恢复的错误.md) |
| `Mutex<Option<GitRepo>>` | [Mutex 与共享状态并发](../../../语言基础/rust/16.无畏并发/16.3.Mutex与共享状态并发.md) |
| `Serialize` / `Deserialize` | [Serde 序列化与反序列化](../../../语言基础/rust/生态库/Serde%20序列化与反序列化.md) |
| `async` / `spawn_blocking` | [async、await 与阻塞任务](../../../语言基础/rust/异步编程/async、await%20与阻塞任务.md) |
| `#[cfg(test)] mod tests` | [Rust 自动化测试](../../../语言基础/rust/10.编写自动化测试/10.1.如何编写测试.md) |

总阅读顺序仍由 [Rust 项目代码阅读地图](../../../语言基础/rust/Rust%20项目代码阅读地图.md) 负责串联。

## 测试为什么跟着实现文件

Command 文件底部常见:

```rust
#[cfg(test)]
mod tests {
    use super::*;
}
```

这是 Rust 的模块内单元测试:

```text
#[cfg(test)]  -> 只在 cargo test 时编译
mod tests     -> 与正式代码分开的子模块
use super::*  -> 引入父模块的项,可测试私有 helper
```

GitTributary 还有 `src-tauri/crates/*/tests/` 和 `src-tauri/tests/`。它们被当成独立 crate 编译,更适合通过公开 API 测试模块协作和完整链路。

## 推荐阅读路线

对一个前端操作,使用以下顺序:

```text
1. 在 React 中找 invoke("...")
2. 在 commands/*.rs 中找 #[tauri::command]
3. 先读函数签名,写下输入、输出、状态和失败
4. 把函数体改写成动作链
5. 标记每个动作属于哪个 gt-* crate
6. 进入 crate 的 public API,再跟到具体模块
7. 最后查看状态写入、事件发布、错误和测试
```

阅读时建议为每个 command 记录一张小表:

| 观察项 | 问题 |
| --- | --- |
| 入口 | 哪个前端动作触发? |
| 输入输出 | DTO 和错误类型是什么? |
| 状态 | 读写了 `AppState` 中哪个字段? |
| 能力 | 调用了哪个 `gt-*` crate? |
| 编排 | 有几个步骤,顺序是否是业务规则? |
| 副作用 | 写文件、Git、Store 还是发事件? |
| 并发 | 拿了哪些锁,何时释放? |
| 验证 | 是单元测试还是集成测试? |

## 当前结构判断

### 可以继续保留在 command 的代码

- 参数接收与 DTO 转换。
- `State` 提取和短时锁访问。
- 调用一个能力并把错误转成 IPC 边界类型。
- 与 Tauri 直接相关的操作,例如打开本地路径。

### 增长后应优先抽离的代码

- 同时协调两个以上 `gt-*` crate。
- 包含明确业务顺序、回滚、重试或幂等规则。
- 被 Tauri command、Flow Action 和后台任务多个入口复用。
- 需要构造大量 `AppState` 才能测试。
- 长时持有锁或需要管理多把锁。
- command 文件已经难以同时展示入口清单和业务意图。

## 建议的演进方向

当前不需要为了形式立即增加一整套抽象。应按真实复杂度演进:

```text
阶段 1
保持薄 command,单领域能力下沉到 gt-* crate

阶段 2
将增长的跨 crate 用例抽成 src/application/*.rs
command 只负责提取 State 和调用用例

阶段 3
当 Tauri、Flow、CLI 或后台任务需要共用用例时
用明确的应用服务和 trait 端口取代对 AppState 的直接依赖
```

优先候选:

```text
sync_data_center_now
  -> DataCenterSyncService / application::sync

site_publish_pages
  -> PublishSiteUseCase / application::site_publish

AppFlowActionExecutor
  -> host_actions / application::flow_actions

commit_all + commit_selected 的共享部分
  -> application::commit
```

这是方向候选,不是要求立即重构的任务清单。每次抽离都应以“降低复杂度、支持复用或提高可测试性”为理由。

## 回链

- Rust 语法阅读: [Rust 项目代码阅读地图](../../../语言基础/rust/Rust%20项目代码阅读地图.md)
- 通用架构判断: [从调用链到项目边界](../../../全栈工程/架构设计/从调用链到项目边界.md)
- 已有并发实践: [Tauri invoke 并发与后台任务决策](./Tauri%20invoke%20并发与后台任务决策.md)
- 仓库架构导读: `doc/架构/项目梳理导读.md`
- 命令层重构背景: `doc/开发日志/重构记录.md`
