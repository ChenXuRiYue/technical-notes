# Lab 3.1: Plugin Host Manager（后端核心）

**Phase 3 — 插件系统核心**
**预计耗时：** 3-4 天
**前置：** Lab 1.1（Manifest）、Lab 1.2（Error）、Lab 1.3（Trait）、Lab 2.2（Workspace）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 设计一个集中管理插件的宿主管理器
- [ ] 实现插件的加载（扫描目录）、注册、查询、调度
- [ ] 用 `Box<dyn Trait>` 存储异构能力
- [ ] 编写完整的单元测试覆盖正常和异常路径

## 2. Background

Plugin Host Manager (PHM) 是 GitTributary 后端的核心。它负责：

1. **加载**：扫描插件目录，解析 manifest，注册插件
2. **管理**：维护插件状态（active/inactive/error）
3. **调度**：前端调用某个插件的某个命令时，PHM 负责路由到正确的实现
4. **能力注册**：持有 `Box<dyn Capability>`，供插件调用

**关键概念：**
- `HashMap<String, PluginEntry>` 管理注册表
- `Box<dyn Capability>` 实现运行时多态
- 文件系统扫描 (`std::fs::read_dir`)
- 单元测试组织（`#[cfg(test)] mod tests`）

## 3. Procedure

### Step 1: 定义核心结构体

在 `crates/plugin-host/src/lib.rs` 中：

```rust
use std::collections::HashMap;
use std::path::Path;
use serde_json::Value;
use core::{PluginManifest, PluginError, CommandDecl};

pub enum PluginStatus {
    Active,
    Inactive,
    Error(String),
}

pub struct PluginEntry {
    pub manifest: PluginManifest,
    pub status: PluginStatus,
}

pub struct PluginHostManager {
    plugins: HashMap<String, PluginEntry>,
    capabilities: HashMap<String, Box<dyn std::any::Any>>, // 简化版，实际用 trait object
}
```

### Step 2: 实现基本方法

```rust
impl PluginHostManager {
    pub fn new() -> Self {
        Self {
            plugins: HashMap::new(),
            capabilities: HashMap::new(),
        }
    }

    /// 从目录扫描并加载插件
    pub fn load_plugins(&mut self, dir: &Path) -> Result<Vec<&PluginManifest>, PluginError> {
        let mut loaded = Vec::new();

        for entry in std::fs::read_dir(dir)
            .map_err(|e| PluginError::Internal(format!("Cannot read dir: {}", e)))?
        {
            let entry = entry.map_err(|e| PluginError::Internal(e.to_string()))?;
            let manifest_path = entry.path().join("manifest.json");

            if manifest_path.exists() {
                let content = std::fs::read_to_string(&manifest_path)
                    .map_err(|e| PluginError::Internal(e.to_string()))?;
                let manifest: PluginManifest = serde_json::from_str(&content)?;

                let name = manifest.name.clone();
                loaded.push(
                    self.plugins
                        .entry(name.clone())
                        .or_insert(PluginEntry {
                            manifest,
                            status: PluginStatus::Active,
                        })
                        .manifest()
                );
            }
        }

        Ok(loaded)
    }

    /// 获取所有插件 manifest
    pub fn list(&self) -> Vec<&PluginManifest> {
        self.plugins.values().map(|e| &e.manifest).collect()
    }

    /// 分发命令
    pub fn dispatch(&self, plugin: &str, command: &str, _args: Option<Value>) -> Result<Value, PluginError> {
        let entry = self.plugins.get(plugin)
            .ok_or_else(|| PluginError::PluginNotFound(plugin.to_string()))?;

        let _cmd = entry.manifest.commands.iter()
            .find(|c| c.id == command)
            .ok_or_else(|| PluginError::CommandNotFound {
                plugin: plugin.to_string(),
                command: command.to_string(),
            })?;

        // Mock 实现：返回假数据
        Ok(serde_json::json!({
            "status": "ok",
            "plugin": plugin,
            "command": command,
        }))
    }
}
```

### Step 3: 编写测试用例

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn create_test_plugin(dir: &TempDir, name: &str, manifest_json: &str) {
        let plugin_dir = dir.path().join(name);
        std::fs::create_dir(&plugin_dir).unwrap();
        std::fs::write(plugin_dir.join("manifest.json"), manifest_json).unwrap();
    }

    #[test]
    fn test_load_valid_plugins() { /* ... */ }

    #[test]
    fn test_load_broken_manifest() { /* ... */ }

    #[test]
    fn test_dispatch_existing_command() { /* ... */ }

    #[test]
    fn test_dispatch_nonexistent_plugin() { /* ... */ }

    #[test]
    fn test_dispatch_nonexistent_command() { /* ... */ }
}
```

**你需要补全所有测试的实现。**

### Step 4: 使用 tempfile

```toml
[dev-dependencies]
tempfile = "3"
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| PHM 实现 | `crates/plugin-host/src/lib.rs` | PluginHostManager + PluginEntry |
| 单元测试 | 同上 `#[cfg(test)]` | ≥ 5 个测试 |

## 5. Evaluation Criteria

- [ ] `cargo test -p plugin-host` 全部通过
- [ ] 覆盖正常路径（加载、分发）和异常路径（插件不存在、命令不存在）
- [ ] 使用 `tempfile` 创建临时目录，测试可重复
- [ ] 代码结构清晰，方法职责单一

## 6. Extensions (Optional)

- [ ] 添加 `unload_plugin(&mut self, name: &str)` 方法
- [ ] 添加 `activate` / `deactivate` 方法切换插件状态
- [ ] 实现 `PluginStatus` 的 `Display` trait

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- HashMap 管理注册表的设计思路 -->

**可复用的代码：**

<!-- PluginHostManager 是 GitTributary 的核心组件 -->
