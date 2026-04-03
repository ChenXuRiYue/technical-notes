# Lab 4.3: Plugin Host Manager 接入 WASM 插件

**Phase 4 — WASM 插件**
**预计耗时：** 3-4 天
**前置：** Lab 3.1（PluginHostManager）、Lab 4.1（Extism）、Lab 4.2（Host Function）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 扩展 PluginHostManager 同时支持内部插件和 WASM 插件
- [ ] 实现统一的 dispatch 路由（内部 vs WASM）
- [ ] 使用 Adapter 模式统一两种插件的接口
- [ ] 理解枚举 + trait object 实现异构集合的方法

## 2. Background

GitTributary 的插件系统有两个层级：
- **内部插件**：编译时集成，直接调用 Rust 函数
- **WASM 插件**：运行时加载，通过 Extism 调用

两者需要对外暴露统一的接口 — 这就是 Adapter 模式的应用场景。

**关键概念：**
- Adapter 模式：让不兼容的接口统一
- 枚举 vs trait object 的取舍
- Extism `Plugin::new()` 和 `call()` 的生命周期管理
- 插件目录结构：`plugin-name/manifest.json + plugin.wasm`

## 3. Procedure

### Step 1: 定义统一插件接口

```rust
// crates/plugin-host/src/lib.rs

/// 统一的插件 dispatch 接口
pub trait PluginAdapter {
    fn manifest(&self) -> &PluginManifest;
    fn dispatch(&self, command: &str, args: Option<Value>) -> Result<Value, PluginError>;
}

/// 内部插件（直接调用 Rust 函数）
pub struct InternalPlugin {
    pub manifest: PluginManifest,
    pub handler: Box<dyn Fn(&str, Option<Value>) -> Result<Value, PluginError>>,
}

impl PluginAdapter for InternalPlugin {
    fn manifest(&self) -> &PluginManifest { &self.manifest }
    fn dispatch(&self, command: &str, args: Option<Value>) -> Result<Value, PluginError> {
        (self.handler)(command, args)
    }
}

/// WASM 插件（通过 Extism 调用）
pub struct WasmPlugin {
    pub manifest: PluginManifest,
    pub wasm_path: std::path::PathBuf,
}

impl PluginAdapter for WasmPlugin {
    fn manifest(&self) -> &PluginManifest { &self.manifest }

    fn dispatch(&self, command: &str, args: Option<Value>) -> Result<Value, PluginError> {
        let wasm = extism::Wasm::file(&self.wasm_path);
        let manifest = extism::Manifest::new([wasm]);
        let mut plugin = extism::Plugin::new(&manifest, true)
            .map_err(|e| PluginError::Internal(e.to_string()))?;

        let input = args.unwrap_or(Value::Null).to_string();
        let result: &str = plugin.call(command, input)
            .map_err(|e| PluginError::Internal(e.to_string()))?;

        serde_json::from_str(result)
            .map_err(|e| PluginError::Internal(e.to_string()))
    }
}
```

### Step 2: 重构 PluginHostManager

```rust
pub struct PluginHostManager {
    plugins: HashMap<String, Box<dyn PluginAdapter>>,
}

impl PluginHostManager {
    pub fn new() -> Self {
        Self { plugins: HashMap::new() }
    }

    /// 注册内部插件
    pub fn register_internal(&mut self, plugin: InternalPlugin) {
        let name = plugin.manifest.name.clone();
        self.plugins.insert(name, Box::new(plugin));
    }

    /// 加载 WASM 插件目录
    pub fn load_wasm_dir(&mut self, dir: &Path) -> Result<Vec<String>, PluginError> {
        let mut loaded = Vec::new();

        for entry in std::fs::read_dir(dir)
            .map_err(|e| PluginError::Internal(e.to_string()))?
        {
            let entry = entry.map_err(|e| PluginError::Internal(e.to_string()))?;
            let plugin_dir = entry.path();

            let manifest_path = plugin_dir.join("manifest.json");
            let wasm_path = plugin_dir.join("plugin.wasm");

            if manifest_path.exists() && wasm_path.exists() {
                let content = std::fs::read_to_string(&manifest_path)?;
                let manifest: PluginManifest = serde_json::from_str(&content)?;

                let name = manifest.name.clone();
                self.plugins.insert(name.clone(), Box::new(WasmPlugin {
                    manifest,
                    wasm_path,
                }));
                loaded.push(name);
            }
        }

        Ok(loaded)
    }

    pub fn list(&self) -> Vec<&PluginManifest> {
        self.plugins.values().map(|p| p.manifest()).collect()
    }

    pub fn dispatch(&self, plugin: &str, command: &str, args: Option<Value>) -> Result<Value, PluginError> {
        let adapter = self.plugins.get(plugin)
            .ok_or_else(|| PluginError::PluginNotFound(plugin.to_string()))?;

        // 检查命令是否存在
        let _cmd = adapter.manifest().commands.iter()
            .find(|c| c.id == command)
            .ok_or_else(|| PluginError::CommandNotFound {
                plugin: plugin.to_string(),
                command: command.to_string(),
            })?;

        adapter.dispatch(command, args)
    }
}
```

### Step 3: 编写测试

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_list_returns_both_plugin_types() {
        let mut phm = PluginHostManager::new();

        // 注册内部插件
        phm.register_internal(InternalPlugin {
            manifest: PluginManifest {
                name: "mock-deploy".to_string(),
                version: "0.1.0".to_string(),
                commands: vec![CommandDecl { id: "deploy".to_string(), description: "Deploy".to_string() }],
                ..Default::default()
            },
            handler: Box::new(|cmd, _| Ok(serde_json::json!({"result": format!("mock:{}", cmd)}))),
        });

        // 加载 WASM 插件（需要准备 fixture）
        // phm.load_wasm_dir(Path::new("test-fixtures/wasm-plugins")).unwrap();

        let list = phm.list();
        assert!(list.iter().any(|m| m.name == "mock-deploy"));
    }

    #[test]
    fn test_dispatch_internal_plugin() { /* ... */ }

    #[test]
    fn test_dispatch_wasm_plugin() { /* 需要 WASM fixture */ }

    #[test]
    fn test_dispatch_nonexistent_plugin() { /* ... */ }
}
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 统一接口 | `crates/plugin-host/src/lib.rs` | PluginAdapter trait + 实现 |
| 重构 PHM | 同上 | 支持两种插件 |
| 测试 | 同上 `#[cfg(test)]` | ≥ 4 个测试 |

## 5. Evaluation Criteria

- [ ] `list()` 同时返回内部插件和 WASM 插件的 manifest
- [ ] `dispatch('mock-deploy', 'deploy')` 正确路由到内部 mock
- [ ] `dispatch('wasm-plugin', 'command')` 正确路由到 WASM
- [ ] 错误情况（插件/命令不存在）有清晰的错误

## 6. Extensions (Optional)

- [ ] 考虑用枚举替代 trait object：

```rust
pub enum PluginType {
    Internal(InternalPlugin),
    Wasm(WasmPlugin),
}
```

比较两种方案的优缺点。

- [ ] 添加插件热重载（检测 .wasm 文件变化后重新加载）

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- Adapter 模式的实际应用 -->

**可复用的代码：**

<!-- 统一 dispatch 路由是 GitTributary 插件系统的核心 -->
