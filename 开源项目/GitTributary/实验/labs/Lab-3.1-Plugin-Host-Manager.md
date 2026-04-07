# Lab 3.1: Plugin Host Manager

**Phase:** 3 - Plugin System Core  
**Estimated Time:** 3-4 days  
**Prerequisites:** Lab 1.1, Lab 1.2, Lab 1.3, Lab 2.2  
**Recommended Submission:** `plugin-host` crate implementation, tests, design note

---

## 1. Learning Objectives

完成本实验后，你应能够：

- 设计一个集中管理插件注册表的后端核心组件
- 为插件加载、查询和命令分发建立清晰接口
- 用 trait object 建模宿主能力依赖
- 为主路径和异常路径编写可重复的单元测试
- 说明“最小可用 PHM”和“最终生产级 PHM”的差异

## 2. Why This Lab Matters

Plugin Host Manager 是 GitTributary 的后端中枢。它至少承担三类职责：

- 管理插件元数据
- 校验调用请求是否合法
- 将命令分发到正确的插件实现

后续 Tauri 集成、WASM 接入、权限系统都建立在这个组件之上。因此这里最重要的不是“功能尽可能多”，而是接口边界要稳定，错误信息要清楚，测试要可信。

## 3. Preparation

开始前请确认：

- `core` crate 已提供 `PluginManifest`、`PluginError` 与 `CommandDecl`
- 你已经理解 trait object 和 `HashMap` 的基本使用方式
- 你知道本实验先做“内部插件 + mock dispatch”，暂不直接追求完整 WASM 调度

建议先执行：

```bash
cargo test -p core
cargo test -p plugin-host
```

如果 `plugin-host` crate 还不存在，请先完成工作区骨架。

## 4. Procedure

### Step 1: Define the Minimal Host Abstraction

在本实验中，我们先把“可执行插件”建模为统一 trait：

```rust
use serde_json::Value;

pub trait Plugin: Send + Sync {
    fn manifest(&self) -> &PluginManifest;
    fn dispatch(&self, command: &str, args: Option<Value>) -> Result<Value, PluginError>;
}
```

说明：

- `manifest()` 用于查询命令和 UI 元数据
- `dispatch()` 负责执行插件命令
- `Send + Sync` 是为了后续接入 Tauri 状态管理时保持扩展空间

### Step 2: Define the Registry and Status Types

在 `crates/plugin-host/src/lib.rs` 中实现基础结构：

```rust
use std::collections::HashMap;
use std::fs;
use std::path::Path;

use core::{PluginError, PluginManifest};
use serde_json::Value;

pub enum PluginStatus {
    Active,
    Inactive,
    Error(String),
}

pub struct PluginEntry {
    pub status: PluginStatus,
    plugin: Box<dyn Plugin>,
}

impl PluginEntry {
    pub fn manifest(&self) -> &PluginManifest {
        self.plugin.manifest()
    }
}

pub struct PluginHostManager {
    plugins: HashMap<String, PluginEntry>,
}

impl PluginHostManager {
    pub fn new() -> Self {
        Self {
            plugins: HashMap::new(),
        }
    }

    pub fn register(&mut self, plugin: Box<dyn Plugin>) {
        let name = plugin.manifest().name.clone();
        self.plugins.insert(
            name,
            PluginEntry {
                status: PluginStatus::Active,
                plugin,
            },
        );
    }

    pub fn get(&self, name: &str) -> Option<&PluginEntry> {
        self.plugins.get(name)
    }

    pub fn list(&self) -> Vec<&PluginManifest> {
        self.plugins.values().map(|entry| entry.manifest()).collect()
    }
}
```

这里刻意不引入复杂的 capability 存储；那是后续实验的主题。本实验先把插件注册表本身做扎实。

### Step 3: Add a File-Based Loader

如果你已经在 `core` crate 中有 manifest 解析函数，可以直接复用；否则在本实验里先内联一个最小版本：

```rust
pub struct ManifestOnlyPlugin {
    manifest: PluginManifest,
}

impl ManifestOnlyPlugin {
    pub fn new(manifest: PluginManifest) -> Self {
        Self { manifest }
    }
}

impl Plugin for ManifestOnlyPlugin {
    fn manifest(&self) -> &PluginManifest {
        &self.manifest
    }

    fn dispatch(&self, command: &str, _args: Option<Value>) -> Result<Value, PluginError> {
        let known = self
            .manifest
            .commands
            .iter()
            .any(|candidate| candidate.id == command);

        if !known {
            return Err(PluginError::CommandNotFound {
                plugin: self.manifest.name.clone(),
                command: command.to_string(),
            });
        }

        Ok(serde_json::json!({
            "status": "ok",
            "plugin": self.manifest.name,
            "command": command
        }))
    }
}

impl PluginHostManager {
    pub fn load_plugins(&mut self, dir: &Path) -> Result<Vec<String>, PluginError> {
        let mut loaded = Vec::new();

        for entry in fs::read_dir(dir).map_err(|err| PluginError::Internal(err.to_string()))? {
            let entry = entry.map_err(|err| PluginError::Internal(err.to_string()))?;
            let plugin_dir = entry.path();
            if !plugin_dir.is_dir() {
                continue;
            }

            let manifest_path = plugin_dir.join("manifest.json");
            if !manifest_path.exists() {
                continue;
            }

            let raw = fs::read_to_string(&manifest_path)
                .map_err(|err| PluginError::Internal(err.to_string()))?;
            let manifest: PluginManifest = serde_json::from_str(&raw)?;
            let name = manifest.name.clone();

            self.register(Box::new(ManifestOnlyPlugin::new(manifest)));
            loaded.push(name);
        }

        Ok(loaded)
    }
}
```

### Step 4: Implement Command Dispatch

分发逻辑要尽量简单明确：

```rust
impl PluginHostManager {
    pub fn dispatch(
        &self,
        plugin: &str,
        command: &str,
        args: Option<Value>,
    ) -> Result<Value, PluginError> {
        let entry = self
            .plugins
            .get(plugin)
            .ok_or_else(|| PluginError::PluginNotFound(plugin.to_string()))?;

        match entry.status {
            PluginStatus::Active => entry.plugin.dispatch(command, args),
            PluginStatus::Inactive => Err(PluginError::Internal(format!(
                "Plugin `{plugin}` is inactive"
            ))),
            PluginStatus::Error(ref message) => Err(PluginError::Internal(format!(
                "Plugin `{plugin}` is in error state: {message}"
            ))),
        }
    }
}
```

### Step 5: Write Tests with Temporary Directories

测试要覆盖：

- 成功加载
- manifest 解析失败
- 成功分发
- 插件不存在
- 命令不存在

示例测试：

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn create_test_plugin(dir: &TempDir, name: &str, manifest_json: &str) {
        let plugin_dir = dir.path().join(name);
        fs::create_dir_all(&plugin_dir).unwrap();
        fs::write(plugin_dir.join("manifest.json"), manifest_json).unwrap();
    }

    #[test]
    fn loads_valid_plugins() {
        let dir = TempDir::new().unwrap();
        create_test_plugin(
            &dir,
            "mock-plugin",
            r#"{
                "name": "mock-plugin",
                "version": "0.1.0",
                "pluginType": "internal",
                "pluginVersion": "1",
                "commands": [{ "id": "ping", "description": "Ping" }]
            }"#,
        );

        let mut phm = PluginHostManager::new();
        let loaded = phm.load_plugins(dir.path()).unwrap();

        assert_eq!(loaded, vec!["mock-plugin".to_string()]);
        assert!(phm.get("mock-plugin").is_some());
    }

    #[test]
    fn load_fails_for_invalid_manifest() {
        let dir = TempDir::new().unwrap();
        create_test_plugin(
            &dir,
            "broken-plugin",
            r#"{
                "version": "0.1.0",
                "pluginType": "internal",
                "pluginVersion": "1"
            }"#,
        );

        let mut phm = PluginHostManager::new();
        assert!(phm.load_plugins(dir.path()).is_err());
    }

    #[test]
    fn dispatch_existing_command_returns_mock_payload() {
        let dir = TempDir::new().unwrap();
        create_test_plugin(
            &dir,
            "mock-plugin",
            r#"{
                "name": "mock-plugin",
                "version": "0.1.0",
                "pluginType": "internal",
                "pluginVersion": "1",
                "commands": [{ "id": "ping", "description": "Ping" }]
            }"#,
        );

        let mut phm = PluginHostManager::new();
        phm.load_plugins(dir.path()).unwrap();

        let result = phm.dispatch("mock-plugin", "ping", None).unwrap();
        assert_eq!(result["status"], "ok");
        assert_eq!(result["command"], "ping");
    }

    #[test]
    fn dispatch_nonexistent_plugin_returns_error() {
        let phm = PluginHostManager::new();
        assert!(matches!(
            phm.dispatch("missing", "ping", None),
            Err(PluginError::PluginNotFound(_))
        ));
    }

    #[test]
    fn dispatch_nonexistent_command_returns_error() {
        let dir = TempDir::new().unwrap();
        create_test_plugin(
            &dir,
            "mock-plugin",
            r#"{
                "name": "mock-plugin",
                "version": "0.1.0",
                "pluginType": "internal",
                "pluginVersion": "1",
                "commands": [{ "id": "ping", "description": "Ping" }]
            }"#,
        );

        let mut phm = PluginHostManager::new();
        phm.load_plugins(dir.path()).unwrap();

        assert!(matches!(
            phm.dispatch("mock-plugin", "missing", None),
            Err(PluginError::CommandNotFound { .. })
        ));
    }
}
```

### Step 6: Verify and Discuss Scope

运行：

```bash
cargo test -p plugin-host
```

本实验的边界要说清楚：

- 这里的 `ManifestOnlyPlugin` 只是教学阶段的过渡实现
- 真正的内部插件与 WASM 插件会在后续 Lab 中替换掉它
- 但 `PluginHostManager` 的注册、查询、分发接口应尽量保持稳定

## 5. Deliverables

| Item | Path | Requirement |
|------|------|-------------|
| PHM implementation | `crates/plugin-host/src/lib.rs` | 包含 `Plugin` trait、`PluginEntry`、`PluginHostManager` |
| Loader | 同上 | 支持扫描目录并注册插件 |
| Tests | 同上 `#[cfg(test)]` | 至少 5 个测试 |
| Design note | 任意实验记录位置 | 说明为何先采用 mock plugin abstraction |

## 6. Assessment and Rubric

- **Correctness**
  加载、查询、分发的主路径成立，异常路径能返回清晰错误
- **Code Quality**
  组件边界明确，注册表职责单一，不提前引入过多抽象
- **Verification**
  使用 `tempfile` 保证测试可重复，覆盖成功与失败路径
- **Reflection**
  能解释为何在此阶段使用 `Plugin` trait 而非直接耦合到具体实现

## 7. Common Failure Modes

- 把 `PluginHostManager` 同时做成“注册表”“能力容器”“WASM 运行时”
  当前 Lab 请克制范围，优先保证注册与调度接口稳定
- 示例代码中的类型名与真实 crate 不一致
  若 `core` crate 的定义不同，请统一到一个真实版本，不要在不同 Lab 中漂移
- 为了返回引用而写出难维护的生命周期结构
  初版可以优先返回 `Vec<String>` 或简单查询接口，避免不必要的复杂借用设计

## 8. Extensions

- 增加 `unload_plugin`、`activate`、`deactivate`
- 引入 capability registry，并改成真实 trait object
- 让 `PluginStatus` 实现 `Display`

## 9. Notes and Reflection

至少记录：

- 注册表设计中最难的一处边界是什么
- 你如何决定 `Plugin` trait 的最小接口
- 哪部分代码最可能在接入 WASM 后需要重构
