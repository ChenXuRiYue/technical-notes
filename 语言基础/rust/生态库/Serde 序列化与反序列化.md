# 📌 Serde 序列化与反序列化

Serde 是 Rust 生态中常用的序列化框架。`Serialize` 表示“可将 Rust 值转成某种数据格式”,`Deserialize` 表示“可从数据格式构造 Rust 值”。Serde 定义通用数据模型和 trait;JSON、YAML、TOML 等具体格式由对应 crate 实现。

## 📄 序列化与反序列化的方向

```text
Serialize
Rust value -> serializer -> JSON / YAML / TOML / binary

Deserialize
JSON / YAML / TOML / binary -> deserializer -> Rust value
```

例如:

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct User {
    id: u64,
    name: String,
}
```

`#[derive(Serialize, Deserialize)]` 会调用派生过程宏,为 `User` 生成对应 trait 实现。它不会立即转换数据;真正转换发生在调用具体格式库时:

```rust
let json = serde_json::to_string(&user)?;
let decoded: User = serde_json::from_str(&json)?;
```

## 📄 输入 DTO 与输出 DTO

一个类型不一定需要同时实现两个 trait:

```rust
#[derive(Deserialize)]
struct CreateUserRequest {
    name: String,
}

#[derive(Serialize)]
struct UserResponse {
    id: u64,
    name: String,
}
```

```text
Deserialize only -> 主要作为外部输入
Serialize only   -> 主要作为外部输出
两者都有       -> 既可输入也可输出,需要确认是否真的必要
```

将输入和输出类型分开,可以避免内部字段、敏感信息或只读字段意外进入协议边界。

## 📄 字段命名与默认值

### 🔖 `rename_all`

Rust 常使用 snake_case,JavaScript 常使用 camelCase:

```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PublishRequest {
    target_branch: String,
    publish_dir: String,
}
```

对应 JSON:

```json
{
  "targetBranch": "main",
  "publishDir": "dist"
}
```

`rename_all` 改变外部数据名称,不改变 Rust 代码中的字段名。

### 🔖 `default`

```rust
#[derive(Deserialize)]
struct Config {
    #[serde(default)]
    verbose: bool,
}
```

输入缺失 `verbose` 时,Serde 使用 `bool::default()`,也就是 `false`。也可指定函数:

```rust
fn default_port() -> u16 {
    8080
}

#[derive(Deserialize)]
struct Config {
    #[serde(default = "default_port")]
    port: u16,
}
```

`#[serde(default)]` 与 `Option<T>` 不同:

```text
Option<T>          -> 记住输入中可以没有值
#[serde(default)]  -> 输入缺失时直接构造一个默认值
```

### 🔖 跳过字段

```rust
#[derive(Serialize, Deserialize)]
struct Account {
    username: String,

    #[serde(skip_serializing)]
    password_hash: String,
}
```

对敏感数据,更稳妥的做法通常是使用专用输出 DTO,而不是完全依赖 `skip_serializing`。

## 📄 `Option<T>` 在反序列化中的含义

```rust
#[derive(Deserialize)]
struct PatchUser {
    display_name: Option<String>,
}
```

默认情况下,字段缺失或 JSON 值为 `null` 都可得到 `None`。对补丁 API,这可能无法区分:

```text
字段没传      -> 保持原值
显式传 null    -> 清空原值
```

需要区分时,应设计更明确的补丁类型,而不是默认认为一层 `Option<T>` 能表达三种状态。

## 📄 序列化是架构边界

序列化类型不只是数据类:

```text
字段名      -> 外部协议
字段是否可缺失 -> 兼容策略
enum 表示方式 -> 外部状态模型
错误信息     -> 调用方可观察性
```

读到 Serde 属性时应问:

```text
这个类型是持久化格式、网络/IPC 协议还是内部对象?
修改字段名会不会破坏旧数据或旧客户端?
是否把敏感字段暴露到了边界?
反序列化成功是否就代表业务校验通过?
```

Serde 负责数据形式转换,不会自动完成全部业务校验。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写,AI 创建笔记时只保留占位,不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写,AI 创建笔记时只保留占位,不填充具体内容。

## 🗺️ 修订记录

| 日期 | 内容 |
| --- | --- |
| 2026-07-16 | 建立 Serde trait、derive、字段属性与协议边界的通用模型 |

## 🛠️ 实践经历

- GitTributary command 的输入请求使用 `Deserialize`,输出报告使用 `Serialize`。
- `#[serde(rename_all = "camelCase")]` 在 Rust snake_case 与 TypeScript camelCase 之间建立 IPC 字段映射。
- `#[serde(default)]` 使旧版前端没有传递新字段时仍能构造 Rust 请求类型。
- 项目回链: [Command 层代码阅读与架构演进](../../../开源项目/GitTributary/技术经验/Command%20层代码阅读与架构演进.md)
- 上位概念: [序列化](../../../后端工程/序列化与格式化/序列化.md)

## ⚙️ prompt

```markdown
请分析一个 Rust Serde 类型:
1. 区分它是输入 DTO、输出 DTO、持久化对象还是内部类型。
2. 解释每个 serde 属性对外部数据格式的影响。
3. 标出字段缺失、null、默认值和兼容性语义。
4. 检查敏感字段、内部细节泄露和业务校验边界。
```

## 调研

当前内容已直接推广为稳定知识,暂无未晋升的调研材料。

