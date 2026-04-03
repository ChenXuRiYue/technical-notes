# Lab 1.1: Plugin Manifest Parser

**Phase 1 — Rust 基础与 Serde**
**预计耗时：** 2-3 天
**前置：** 无（本阶段第一个实验）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 用 `#[derive(Deserialize)]` 将 JSON 映射到 Rust 结构体
- [ ] 使用 `#[serde(rename)]` / `#[serde(default)]` 处理字段映射和可选字段
- [ ] 用 `Result` + `?` 实现错误传播
- [ ] 遍历目录、读取文件、批量解析

## 2. Background

GitTributary 的每个插件由一个 `manifest.json` 描述其元数据（名称、版本、命令列表、UI 声明等）。宿主启动时需要扫描插件目录，批量加载并校验这些 manifest。

Serde 是 Rust 生态的标准序列化框架。本实验是你第一次将 Serde 用于实际场景。

**关键概念：**
- Serde `Deserialize` derive 宏如何将 JSON 字段映射到 Rust 字段
- `#[serde(rename = "camelCase")]` 处理命名风格差异
- `#[serde(default)]` 让缺失字段使用默认值而非报错
- `std::fs::read_dir` 遍历目录

## 3. Procedure

### Step 1: 项目初始化

```bash
cargo new manifest-parser && cd manifest-parser
```

在 `Cargo.toml` 中添加依赖：

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

### Step 2: 定义类型

（定义一个标准化的插件描述结构体）

```json
{
  "name": "名称", // 名称
  "type": "类型", // 类型
  "version": "1.x", // 版本：形如 1.x
  "github_url": "", // github url github 仓库位置
  "pluign_version": "", // 插件版本。避免后续迭代，仓库结构发生变更
}
```



在 `src/main.rs` 中定义以下结构体：

```rust
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct PluginManifest {
    pub name: String,
    pub version: String,
    #[serde(default)]
    pub commands: Vec<CommandDecl>,
    // TODO: 添加更多字段
}

#[derive(Debug, Deserialize)]
pub struct CommandDecl {
    pub id: String,
    pub description: String,
}
```

**思考：** 如果前端 JSON 用 camelCase（如 `minHostVersion`），Rust 用 snake_case，怎么处理？

### Step 3: 实现单文件解析

编写函数：

```rust
pub fn parse_manifest(path: &std::path::Path) -> Result<PluginManifest, Box<dyn std::error::Error>> {
    // TODO: 读取文件 → serde_json::from_str → 返回
}
```

### Step 4: 实现目录批量扫描

```rust
pub fn scan_plugins(dir: &std::path::Path) -> Vec<(String, Result<PluginManifest, String>)> {
    // TODO:
    // 1. read_dir 遍历 dir 下的子目录
    // 2. 每个子目录尝试读取 manifest.json
    // 3. 解析成功 → Ok，解析失败 → Err(错误信息)
    // 4. 收集所有结果返回
}
```

### Step 5: 编写测试用例

准备以下测试 fixture：

```
test-fixtures/
├── valid-plugin/
│   └── manifest.json        ← 合法 JSON
├── another-plugin/
│   └── manifest.json        ← 合法但字段更多
└── broken-plugin/
    └── manifest.json        ← 缺少必填字段 name
```

测试用例：
1. 合法 manifest 能正确解析
2. 缺少 `name` 字段时返回错误，错误信息包含 `missing field`
3. 未知字段默认被拒绝（`#[serde(deny_unknown_fields)]`）

### Step 6: 主程序输出

最终程序应输出：

```
✓ valid-plugin: v0.1.0, 3 commands
✓ another-plugin: v0.2.0, 1 command
✗ broken-plugin: 解析失败 - missing field `name`
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 源代码 | `manifest-parser/src/` | 完整可编译的 Rust 项目 |
| 测试 fixture | `manifest-parser/test-fixtures/` | 3 个示例 manifest |
| 单元测试 | `src/main.rs` 底部 `#[cfg(test)]` | ≥ 3 个测试 |

## 5. Evaluation Criteria

- [ ] `cargo test` 全部通过
- [ ] `cargo run` 能扫描 test-fixtures 目录并输出正确结果
- [ ] 错误 case（broken-plugin）有清晰的错误信息
- [ ] 代码中有适当的 `#[serde]` 属性注解

## 6. Extensions (Optional)

- [ ] 支持 `#[serde(deny_unknown_fields)]`，并测试未知字段被拒绝
- [ ] 为 `PluginManifest` 添加 `#[serde(default)]` 的 `capabilities` 字段（`Vec<String>`）
- [ ] 用 `walkdir` crate 支持递归扫描（插件目录可能嵌套）

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- 用自己的话总结 Serde 的工作方式 -->

**可复用的代码：**

<!-- 哪些代码可以直接搬到 GitTributary 的 core crate 中？ -->
