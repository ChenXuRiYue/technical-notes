# Lab 4.1: Extism Hello World

**Phase 4 — WASM 插件**
**预计耗时：** 2-3 天
**前置：** Lab 1.3（Trait 概念）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 用 Extism PDK 编写一个 WASM 插件
- [ ] 用 Extism Host SDK 加载 .wasm 文件并调用函数
- [ ] 理解 WASM 和宿主之间的数据传递机制
- [ ] 用 `wasm32-wasip1` 编译目标构建 WASM 模块

## 2. Background

WASM 插件是 GitTributary 的第二层插件系统。相比内部 Rust 插件（编译时集成），WASM 插件提供：

- **运行时隔离**：插件在沙箱中运行，不能直接访问宿主资源
- **热加载**：不需要重新编译宿主程序
- **跨语言**：理论上任何能编译为 WASM 的语言都能写插件

Extism 是一个通用的插件运行时，简化了 WASM 宿主的开发。

**关键概念：**
- Extism PDK（Plugin Development Kit）：插件端
- Extism Host SDK：宿主端
- WASM 内存模型：宿主和 WASM 之间通过内存偏移量传递数据
- JSON 字符串是常用的 WASM 宿主通信载体

## 3. Procedure

### Step 1: 安装工具链

```bash
rustup target add wasm32-wasip1
cargo install extism-cli  # 可选，用于调试
```

### Step 2: 创建插件项目

```bash
cargo new word-count-plugin --lib
```

`Cargo.toml`：

```toml
[package]
name = "word-count-plugin"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
extism-pdk = "1"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

### Step 3: 编写插件

```rust
// src/lib.rs
use extism_pdk::*;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct Input {
    text: String,
}

#[derive(Serialize)]
struct Output {
    count: usize,
    words: Vec<String>,
}

#[plugin_fn]
pub fn word_count(Json(input): Json<Input>) -> FnResult<Json<Output>> {
    let words: Vec<String> = input
        .text
        .split_whitespace()
        .map(|s| s.to_string())
        .collect();

    Ok(Json(Output {
        count: words.len(),
        words,
    }))
}
```

### Step 4: 编译插件

```bash
cd word-count-plugin
cargo build --target wasm32-wasip1 --release
# 输出: target/wasm32-wasip1/release/word_count_plugin.wasm
```

### Step 5: 创建宿主项目

```bash
cargo new wasm-host
```

`Cargo.toml`：

```toml
[dependencies]
extism = "1"
serde_json = "1"
```

### Step 6: 编写宿主

```rust
// src/main.rs
use extism::{Manifest, Plugin, Wasm};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let wasm = Wasm::file("../word-count-plugin/target/wasm32-wasip1/release/word_count_plugin.wasm");
    let manifest = Manifest::new([wasm]);
    let mut plugin = Plugin::new(&manifest, true)?;

    let input = serde_json::json!({ "text": "Hello World 你好世界" });
    let result: &str = plugin.call("word_count", input.to_string())?;

    let output: serde_json::Value = serde_json::from_str(result)?;
    println!("Word count: {}", output["count"]);
    println!("Words: {:?}", output["words"]);

    Ok(())
}
```

### Step 7: 运行

```bash
cd wasm-host
cargo run
```

期望输出：

```
Word count: 4
Words: ["Hello", "World", "你好世界"]
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 插件项目 | `word-count-plugin/` | WASM 插件源码 |
| WASM 文件 | `target/wasm32-wasip1/release/*.wasm` | 编译产物 |
| 宿主项目 | `wasm-host/` | 宿主加载 + 调用 |

## 5. Evaluation Criteria

- [ ] `cargo run`（宿主端）输出正确的字数
- [ ] 改变输入文本，输出正确变化
- [ ] 理解 PDK 和 Host SDK 的区别

## 6. Extensions (Optional)

- [ ] 添加一个 `reverse` 函数，将输入字符串反转
- [ ] 尝试传入 JSON 数组作为输入
- [ ] 用 `extism-pdk` 的 `http` 功能做一次 HTTP 请求（需要宿主允许）

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- WASM 宿主和插件之间的数据传递方式 -->

**可复用的代码：**

<!-- Extism 的加载和调用模式可以直接用于 GitTributary -->
