# Lab 4.2: Host Function — 宿主向 WASM 暴露能力

**Phase 4 — WASM 插件**
**预计耗时：** 2-3 天
**前置：** Lab 4.1（Extism Hello World）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 在宿主端注册 host function，供 WASM 插件调用
- [ ] 理解 WASM 内存模型（宿主和 WASM 之间的数据传递）
- [ ] 实现基本的权限校验（宿主控制哪些路径允许访问）
- [ ] 理解 Capability API 在 WASM 场景的实现方式

## 2. Background

WASM 插件运行在沙箱中，不能直接访问宿主的文件系统、网络等资源。宿主需要通过 **host function** 暴露这些能力。

这正是 GitTributary Capability API 的 WASM 版实现：
- Rust trait `FileRead` → 内部插件直接实现
- WASM 插件 → 宿主注册 `host_read_file` → WASM 调用该函数

**关键概念：**
- Host function 的签名：`(inputs: &[Val], outputs: &mut [Val])`
- WASM 内存通过 `plugin.memory_get_val` / `plugin.memory_set_val` 读写
- 宿主可以实现白名单校验，控制 WASM 插件的访问范围

## 3. Procedure

### Step 1: 扩展宿主 — 注册 Host Function

```rust
use extism::{Manifest, Plugin, Wasm, Function, ValType, UserData};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 允许访问的路径白名单
    let allowed_paths = vec!["/tmp/sandbox".to_string()];

    let host_read_file = Function::new(
        "host_read_file",
        [ValType::I64],
        [ValType::I64],
        UserData::new(allowed_paths),
        |plugin: extism::CurrentPlugin,
         inputs: &[Val],
         outputs: &mut [Val],
         user_data: UserData<Vec<String>>| {
            // 从 WASM 内存读取文件路径
            let path_str = plugin.memory_get_val::<String>(&inputs[0])?;

            // 权限校验
            let allowed = user_data.get()?;
            let is_allowed = allowed.iter().any(|p| path_str.starts_with(p));
            if !is_allowed {
                let err = serde_json::json!({
                    "error": "PERMISSION_DENIED",
                    "message": format!("Access to '{}' is not allowed", path_str)
                }).to_string();
                plugin.memory_set_val(&mut outputs[0], &err)?;
                return Ok(());
            }

            // 读取文件
            match std::fs::read_to_string(&path_str) {
                Ok(content) => {
                    let result = serde_json::json!({ "content": content }).to_string();
                    plugin.memory_set_val(&mut outputs[0], &result)?;
                }
                Err(e) => {
                    let err = serde_json::json!({
                        "error": "FILE_READ_ERROR",
                        "message": e.to_string()
                    }).to_string();
                    plugin.memory_set_val(&mut outputs[0], &err)?;
                }
            }
            Ok(())
        },
    );

    let wasm = Wasm::file("line-counter.wasm");
    let manifest = Manifest::new([wasm])
        .with_function(host_read_file);

    let mut plugin = Plugin::new(&manifest, true)?;

    // 测试：允许的路径
    let result: &str = plugin.call("count_lines", r#"{"path":"/tmp/sandbox/test.txt"}"#)?;
    println!("Result: {}", result);

    Ok(())
}
```

### Step 2: 编写 WASM 插件 — line-counter

```rust
// line-counter-plugin/src/lib.rs
use extism_pdk::*;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct Input {
    path: String,
}

#[derive(Serialize)]
struct Output {
    line_count: usize,
    content_preview: String,
}

// 声明 host function
#[host_fn]
extern "ExtismHost" {
    fn host_read_file(path: String) -> String;
}

#[plugin_fn]
pub fn count_lines(Json(input): Json<Input>) -> FnResult<Json<Output>> {
    // 调用宿主的 host function
    let result_str = unsafe { host_read_file(input.path.clone())? };
    let result: serde_json::Value = serde_json::from_str(&result_str)?;

    if let Some(error) = result.get("error") {
        return Err(Error::msg(format!(
            "{}: {}",
            error,
            result["message"].as_str().unwrap_or("unknown")
        )).into());
    }

    let content = result["content"].as_str().unwrap_or("");
    let line_count = content.lines().count();

    Ok(Json(Output {
        line_count,
        content_preview: content.lines().take(3).collect::<Vec<_>>().join("\n"),
    }))
}
```

### Step 3: 准备测试文件

```bash
mkdir -p /tmp/sandbox
echo -e "line 1\nline 2\nline 3\nline 4" > /tmp/sandbox/test.txt
```

### Step 4: 编译并运行

```bash
cd line-counter-plugin
cargo build --target wasm32-wasip1 --release

cd ../wasm-host
cargo run
```

期望输出：

```
Result: {"line_count": 4, "content_preview": "line 1\nline 2\nline 3"}
```

### Step 5: 测试权限拒绝

修改宿主代码，尝试读取 `/etc/hosts`：

```rust
let result: &str = plugin.call("count_lines", r#"{"path":"/etc/hosts"}"#)?;
println!("Result: {}", result);
// 期望: {"error":"PERMISSION_DENIED","message":"Access to '/etc/hosts' is not allowed"}
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| line-counter 插件 | `line-counter-plugin/` | WASM 插件源码 |
| 扩展宿主 | `wasm-host/` | 含 host function + 权限校验 |
| 测试文件 | `/tmp/sandbox/test.txt` | 测试用文本文件 |

## 5. Evaluation Criteria

- [ ] WASM 插件能通过 host function 读取到宿主文件系统中的文件
- [ ] 宿主拒绝访问白名单之外的路径时，WASM 插件收到错误
- [ ] 行数统计正确

## 6. Extensions (Optional)

- [ ] 添加 `host_write_file` host function
- [ ] 实现更细粒度的权限（只允许读 `.txt` 和 `.md` 文件）
- [ ] 用 `UserData` 传递更多上下文（如当前用户的权限列表）

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- WASM 内存模型和 host function 的交互方式 -->

**可复用的代码：**

<!-- host function 注册和权限校验模式可直接用于 GitTributary -->
