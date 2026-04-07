# Lab 1.1: Plugin Manifest Parser

**Phase:** 1 - Rust Foundations and Serde  
**Estimated Time:** 2-3 days  
**Prerequisites:** None  
**Recommended Submission:** Source code, fixture set, unit tests, short reflection note

---

## 1. Learning Objectives

完成本实验后，你应能够：

- 用 `serde` 将 JSON manifest 映射为 Rust 结构体
- 设计一个最小但可扩展的 `PluginManifest` 数据模型
- 实现单文件解析与目录批量扫描
- 为成功路径与失败路径编写基础测试
- 解释字段命名、默认值和未知字段策略的取舍

## 2. Why This Lab Matters

GitTributary 的插件系统以 manifest 为入口。后续所有实验几乎都依赖这个事实：

- 宿主需要读取 manifest 来发现插件
- 前端需要读取 manifest 来渲染命令和界面
- 权限、WASM 集成、命令面板都依赖 manifest 中的元数据

如果这个实验做得松散，后续所有实验都会出现“接口不稳定”“字段不一致”“错误难定位”的问题。

## 3. Preparation

开始前请确认：

- 你已安装稳定版 Rust 工具链
- 你可以成功执行 `cargo new`、`cargo run` 和 `cargo test`
- 你理解 `Result<T, E>`、`Option<T>` 和 `?` 的基本用法

建议先运行：

```bash
rustc --version
cargo --version
```

建议工作目录：

```bash
cargo new manifest-parser
cd manifest-parser
```

## 4. Procedure

### Step 1: Create the Project

在 `Cargo.toml` 中加入依赖：

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"

[dev-dependencies]
tempfile = "3"
```

### Step 2: Define a Stable Manifest Model

本课程统一使用如下最小 manifest 结构：

```json
{
  "name": "word-count",
  "version": "0.1.0",
  "pluginType": "wasm",
  "githubUrl": "https://github.com/example/word-count",
  "pluginVersion": "1",
  "commands": [
    {
      "id": "count",
      "description": "Count words in a document"
    }
  ]
}
```

注意：

- 上面的示例使用合法 JSON，不包含注释
- 前端字段风格使用 `camelCase`
- Rust 类型字段风格使用 `snake_case`

在 `src/lib.rs` 中定义类型：

```rust
use serde::Deserialize;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct PluginManifest {
    pub name: String,
    pub version: String,
    pub plugin_type: PluginType,
    pub github_url: Option<String>,
    pub plugin_version: String,
    #[serde(default)]
    pub commands: Vec<CommandDecl>,
}

#[derive(Debug, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum PluginType {
    Internal,
    Wasm,
}

#[derive(Debug, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct CommandDecl {
    pub id: String,
    pub description: String,
}

pub fn parse_manifest(path: &Path) -> Result<PluginManifest, Box<dyn std::error::Error>> {
    let raw = fs::read_to_string(path)?;
    let manifest = serde_json::from_str(&raw)?;
    Ok(manifest)
}

pub fn scan_plugins(
    dir: &Path,
) -> Vec<(PathBuf, Result<PluginManifest, String>)> {
    let mut results = Vec::new();

    let entries = match fs::read_dir(dir) {
        Ok(entries) => entries,
        Err(err) => {
            results.push((dir.to_path_buf(), Err(err.to_string())));
            return results;
        }
    };

    for entry in entries {
        match entry {
            Ok(entry) => {
                let plugin_dir = entry.path();
                if !plugin_dir.is_dir() {
                    continue;
                }

                let manifest_path = plugin_dir.join("manifest.json");
                let parsed = parse_manifest(&manifest_path).map_err(|err| err.to_string());
                results.push((plugin_dir, parsed));
            }
            Err(err) => results.push((dir.to_path_buf(), Err(err.to_string()))),
        }
    }

    results
}
```

### Step 3: Explain the Serde Mapping

本实验中有三个关键注解：

- `#[serde(rename_all = "camelCase")]`
  让 Rust 的 `plugin_type` 对应 JSON 的 `pluginType`
- `#[serde(default)]`
  让缺失的 `commands` 字段自动回落为空数组
- `#[serde(deny_unknown_fields)]`
  避免 manifest 静默接受拼写错误或无效字段

这三点体现了工程文档的重要原则：字段映射要显式，默认行为要可预测，错误要尽早暴露。

### Step 4: Add a Small CLI Entry Point

在 `src/main.rs` 中加入一个最小驱动程序：

```rust
use manifest_parser::scan_plugins;
use std::path::Path;

fn main() {
    let fixtures = Path::new("test-fixtures");

    for (plugin_dir, result) in scan_plugins(fixtures) {
        let display_name = plugin_dir
            .file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("<unknown>");

        match result {
            Ok(manifest) => {
                println!(
                    "OK {display_name}: v{}, {} commands",
                    manifest.version,
                    manifest.commands.len()
                );
            }
            Err(error) => {
                println!("ERR {display_name}: {error}");
            }
        }
    }
}
```

### Step 5: Build Test Fixtures

目录建议如下：

```text
test-fixtures/
├── valid-plugin/
│   └── manifest.json
├── default-commands/
│   └── manifest.json
└── broken-plugin/
    └── manifest.json
```

`valid-plugin/manifest.json`：

```json
{
  "name": "valid-plugin",
  "version": "0.1.0",
  "pluginType": "internal",
  "githubUrl": "https://github.com/example/valid-plugin",
  "pluginVersion": "1",
  "commands": [
    {
      "id": "run",
      "description": "Run the plugin"
    }
  ]
}
```

`default-commands/manifest.json`：

```json
{
  "name": "default-commands",
  "version": "0.2.0",
  "pluginType": "wasm",
  "pluginVersion": "1"
}
```

`broken-plugin/manifest.json`：

```json
{
  "version": "0.1.0",
  "pluginType": "internal",
  "pluginVersion": "1",
  "extraField": true
}
```

### Step 6: Write Unit Tests

在 `src/lib.rs` 底部加入测试：

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn write_manifest(dir: &TempDir, folder: &str, content: &str) {
        let plugin_dir = dir.path().join(folder);
        fs::create_dir_all(&plugin_dir).unwrap();
        fs::write(plugin_dir.join("manifest.json"), content).unwrap();
    }

    #[test]
    fn parses_valid_manifest() {
        let dir = TempDir::new().unwrap();
        write_manifest(
            &dir,
            "valid-plugin",
            r#"{
                "name": "valid-plugin",
                "version": "0.1.0",
                "pluginType": "internal",
                "pluginVersion": "1",
                "commands": [{ "id": "run", "description": "Run the plugin" }]
            }"#,
        );

        let manifest = parse_manifest(&dir.path().join("valid-plugin/manifest.json")).unwrap();
        assert_eq!(manifest.name, "valid-plugin");
        assert_eq!(manifest.commands.len(), 1);
    }

    #[test]
    fn missing_commands_uses_default_empty_vec() {
        let dir = TempDir::new().unwrap();
        write_manifest(
            &dir,
            "default-commands",
            r#"{
                "name": "default-commands",
                "version": "0.2.0",
                "pluginType": "wasm",
                "pluginVersion": "1"
            }"#,
        );

        let manifest = parse_manifest(&dir.path().join("default-commands/manifest.json")).unwrap();
        assert!(manifest.commands.is_empty());
    }

    #[test]
    fn unknown_or_missing_required_fields_fail() {
        let dir = TempDir::new().unwrap();
        write_manifest(
            &dir,
            "broken-plugin",
            r#"{
                "version": "0.1.0",
                "pluginType": "internal",
                "pluginVersion": "1",
                "extraField": true
            }"#,
        );

        let err = parse_manifest(&dir.path().join("broken-plugin/manifest.json"))
            .unwrap_err()
            .to_string();

        assert!(
            err.contains("missing field") || err.contains("unknown field"),
            "unexpected error: {err}"
        );
    }
}
```

### Step 7: Verify the Result

运行：

```bash
cargo test
cargo run
```

预期：

- `cargo test` 全部通过
- `cargo run` 能输出成功插件和失败插件的扫描结果

## 5. Deliverables

| Item | Path | Requirement |
|------|------|-------------|
| Manifest parser | `src/lib.rs` | 包含类型定义、解析函数、扫描函数 |
| CLI entry | `src/main.rs` | 能扫描 `test-fixtures` 并输出结果 |
| Fixture set | `test-fixtures/` | 至少 2 个成功例子和 1 个失败例子 |
| Unit tests | `src/lib.rs` | 至少 3 个测试，覆盖成功和失败路径 |
| Reflection note | 任意实验记录位置 | 说明字段设计与错误策略 |

## 6. Assessment and Rubric

- **Correctness**
  解析逻辑正确，目录扫描能区分成功与失败样本
- **Code Quality**
  命名统一，类型定义稳定，Serde 注解使用合理
- **Verification**
  至少有 3 个测试，包含失败路径
- **Reflection**
  能解释为何选择 `deny_unknown_fields` 和 `default`

## 7. Common Failure Modes

- JSON 中带注释
  `serde_json` 不接受带注释的 JSON，请保证 fixture 是合法 JSON
- Rust 字段名和 JSON 字段名不一致
  优先用 `#[serde(rename_all = "camelCase")]` 统一映射
- 把“未知字段拒绝”写进目标，却没有实际加注解
  请确认 `PluginManifest` 和需要严格校验的子结构都加了 `deny_unknown_fields`

## 8. Extensions

- 用 `walkdir` 支持递归扫描
- 为 `PluginManifest` 增加 `capabilities: Vec<String>` 字段
- 返回自定义错误类型，替换 `Box<dyn std::error::Error>`

## 9. Notes and Reflection

至少记录以下三点：

- 哪个字段最容易在前后端之间产生命名漂移
- 你如何在“允许演进”和“严格拒绝错误输入”之间做平衡
- 哪些代码后续可以抽到 `core` crate 中复用
