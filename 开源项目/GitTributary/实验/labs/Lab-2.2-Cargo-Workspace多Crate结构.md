# Lab 2.2: Cargo Workspace 多 Crate 结构

**Phase 2 — Tauri 项目骨架**
**预计耗时：** 1-2 天
**前置：** Lab 1.1, 1.2（使用其类型定义）、Lab 2.1（Tauri 项目模板）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 配置 Cargo workspace，组织多 crate 项目
- [ ] 在 crate 之间使用 `path` 依赖
- [ ] 理解 `pub` 可见性在 crate 边界的作用
- [ ] 用 `cargo test -p <crate>` 测试单个 crate

## 2. Background

GitTributary 的代码会增长到多个模块：核心类型、插件宿主、Git 操作、WASM 运行时……如果全部放在一个 crate 中，编译时间会很长，修改一处会导致全量重编译。

Cargo workspace 允许将项目拆成多个 crate，每个 crate 独立编译，只在需要时依赖其他 crate。

**关键概念：**
- workspace `Cargo.toml` 只声明成员和共享配置，不含 `[dependencies]`
- crate 之间用 `path` 依赖：`core = { path = "../core" }`
- `pub` 类型可以从依赖 crate 中被访问
- workspace 级别的 `cargo build` / `cargo test` 会编译/测试所有成员

## 3. Procedure

### Step 1: 创建 workspace 目录结构

```bash
mkdir -p gittributary-lab/crates/{core,plugin-host,git-ops}
mkdir -p gittributary-lab/src-tauri/src
```

### Step 2: workspace Cargo.toml

```toml
# gittributary-lab/Cargo.toml
[workspace]
resolver = "2"
members = [
    "crates/core",
    "crates/plugin-host",
    "crates/git-ops",
    "src-tauri",
]
```

### Step 3: core crate

```toml
# gittributary-lab/crates/core/Cargo.toml
[package]
name = "core"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "1"
```

将 Lab 1.1 的 `PluginManifest` 和 Lab 1.2 的 `PluginError` 放入 `crates/core/src/lib.rs`：

```rust
// 核心共享类型
pub mod manifest;
pub mod error;

// Re-export
pub use manifest::{PluginManifest, CommandDecl};
pub use error::PluginError;
```

### Step 4: plugin-host crate

```toml
# gittributary-lab/crates/plugin-host/Cargo.toml
[package]
name = "plugin-host"
version = "0.1.0"
edition = "2021"

[dependencies]
core = { path = "../core" }
```

实现一个简单的插件注册表：

```rust
// gittributary-lab/crates/plugin-host/src/lib.rs
use std::collections::HashMap;
use core::{PluginManifest, PluginError};

pub struct PluginRegistry {
    plugins: HashMap<String, PluginManifest>,
}

impl PluginRegistry {
    pub fn new() -> Self {
        Self { plugins: HashMap::new() }
    }

    pub fn register(&mut self, manifest: PluginManifest) {
        self.plugins.insert(manifest.name.clone(), manifest);
    }

    pub fn get(&self, name: &str) -> Result<&PluginManifest, PluginError> {
        self.plugins.get(name)
            .ok_or_else(|| PluginError::PluginNotFound(name.to_string()))
    }

    pub fn list(&self) -> Vec<&PluginManifest> {
        self.plugins.values().collect()
    }
}
```

### Step 5: src-tauri crate

```toml
# gittributary-lab/src-tauri/Cargo.toml
[package]
name = "gittributary-lab"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "2", features = [] }
core = { path = "../crates/core" }
plugin-host = { path = "../crates/plugin-host" }
```

把 plugin-host 暴露为 Tauri command：

```rust
use tauri::State;
use plugin_host::PluginRegistry;

#[tauri::command]
fn plugin_list(state: State<'_, PluginRegistry>) -> Result<Vec<core::PluginManifest>, String> {
    Ok(state.list().into_iter().cloned().collect())
}
```

### Step 6: 编译与测试

```bash
cd gittributary-lab
cargo build          # 编译所有 crate
cargo test           # 测试所有 crate
cargo test -p core   # 只测试 core crate
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| workspace 配置 | `gittributary-lab/Cargo.toml` | workspace root |
| core crate | `crates/core/` | 共享类型 |
| plugin-host crate | `crates/plugin-host/` | 插件注册表 |
| src-tauri crate | `src-tauri/` | Tauri 入口 |

## 5. Evaluation Criteria

- [ ] `cargo build` 整个 workspace 编译通过
- [ ] `cargo test -p core` 通过
- [ ] `cargo test -p plugin-host` 通过
- [ ] crate 依赖关系清晰：`src-tauri → plugin-host → core`

## 6. Extensions (Optional)

- [ ] 在 workspace 级别 `Cargo.toml` 中设置共享的 `[profile]` 配置
- [ ] 添加 `crates/git-ops/` crate（暂时只有空壳）
- [ ] 尝试用 `cargo tree` 查看依赖树

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- workspace 和单 crate 项目各有什么优缺点？ -->

**可复用的代码：**

<!-- 这个 workspace 结构就是 GitTributary 的骨架 -->
