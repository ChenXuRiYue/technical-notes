# Lab 1.2: Custom Error Types

**Phase 1 — Rust 基础与 Serde**
**预计耗时：** 1-2 天
**前置：** Lab 1.1（使用其 manifest 类型）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 用 `thiserror` 定义分层错误枚举
- [ ] 为错误类型实现 `Display` 和 `std::error::Error`
- [ ] 将错误序列化为 JSON（为 Tauri IPC 做准备）
- [ ] 理解 `thiserror`（库/框架层）vs `anyhow`（应用层）的取舍

## 2. Background

插件系统是错误的高发区：插件 manifest 解析失败、命令不存在、权限拒绝、WASM trap……如果每层都用 `String` 传递错误，调试将是噩梦。

自定义错误枚举让每种错误有清晰的类型、上下文字段和一致的序列化格式。

**关键概念：**
- `thiserror` 的 `#[derive(Error)]` 自动实现 `Display` 和 `std::error::Error`
- `#[error("...")]` 属性定义错误消息模板
- `#[from]` 自动实现 `From` trait（错误转换）
- 错误需要序列化为 JSON 传给前端（`serde::Serialize`）

## 3. Procedure

### Step 1: 添加依赖

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "1"
```

### Step 2: 定义错误枚举

```rust
use serde::Serialize;

#[derive(Debug, thiserror::Error, Serialize)]
#[serde(tag = "error", content = "message")]
pub enum PluginError {
    #[error("Manifest parse failed: {0}")]
    ManifestParse(String),

    #[error("Plugin '{0}' is not installed")]
    PluginNotFound(String),

    #[error("Command '{command}' not found in plugin '{plugin}'")]
    CommandNotFound { plugin: String, command: String },

    #[error("Permission denied: {capability}")]
    PermissionDenied { capability: String },

    #[error("Internal error: {0}")]
    Internal(String),
}
```

**思考：** 为什么 `ManifestParse` 存的是 `String` 而不是 `serde_json::Error`？

### Step 3: 实现错误转换

```rust
impl From<serde_json::Error> for PluginError {
    fn from(e: serde_json::Error) -> Self {
        PluginError::ManifestParse(e.to_string())
    }
}
```

### Step 4: 测试错误序列化

编写测试，验证每种错误序列化后的 JSON 格式：

```rust
#[test]
fn test_plugin_not_found_serialization() {
    let err = PluginError::PluginNotFound("git-deploy".to_string());
    let json = serde_json::to_value(&err).unwrap();

    assert_eq!(json["error"], "PLUGIN_NOT_FOUND");
    assert_eq!(json["message"], "Plugin 'git-deploy' is not installed");
    assert_eq!(json["plugin"], "git-deploy");
}
```

**注意：** 你可能需要调整 `#[serde(tag)]` 的写法来得到期望的 JSON 结构。

### Step 5: 错误链示范

模拟真实场景：manifest 解析失败 → 包装为 PluginError → 序列化为 JSON：

```rust
#[test]
fn test_error_chain() {
    let bad_json = "{ invalid json }";
    let parse_result: Result<PluginManifest, _> = serde_json::from_str(bad_json);
    let err: PluginError = parse_result.unwrap_err().into();

    let json = serde_json::to_value(&err).unwrap();
    assert_eq!(json["error"], "MANIFEST_PARSE");
}
```

### Step 6: 前端期望的错误格式

最终输出的 JSON 应该符合这个结构：

```json
{
  "error": "PLUGIN_NOT_FOUND",
  "message": "Plugin 'git-deploy' is not installed",
  "plugin": "git-deploy"
}
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 错误类型定义 | `src/error.rs` 或 `src/main.rs` | `PluginError` 枚举 |
| 单元测试 | 同上 `#[cfg(test)]` | ≥ 5 个测试（每种错误一个） |

## 5. Evaluation Criteria

- [ ] `cargo test` 全部通过
- [ ] 每种错误变体都有对应的测试
- [ ] 错误序列化后有 `error` 和 `message` 字段
- [ ] 错误消息模板包含上下文信息（插件名、命令名等）

## 6. Extensions (Optional)

- [ ] 用 `#[serde(rename_all = "SCREAMING_SNAKE_CASE")]` 统一错误码风格
- [ ] 添加 `context` 字段，记录错误发生的位置（文件、行号）
- [ ] 对比 `anyhow`：用 `anyhow::Result` 重写 Step 5 的错误链，感受区别

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- thiserror 和 anyhow 分别适合什么场景？ -->

**可复用的代码：**

<!-- PluginError 枚举可以直接搬到 GitTributary 的 core crate -->
