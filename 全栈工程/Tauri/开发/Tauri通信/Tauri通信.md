# 📌 Tauri 通信

>Tauri 采用 IPC （进程通信架构）。程序逻辑架构为双核模型：
>
>- Rust Core （Rust 后端中枢）
>- WebView （前端渲染环境）

该文档作为官方文档困惑点的补充。快速回顾浏览，深化记忆

- [从前端调用 rust - offical doc](https://v2.tauri.app/zh-cn/develop/calling-rust/#%E5%9F%BA%E7%A1%80%E7%A4%BA%E4%BE%8B)
- 

## ✔️ 前端调用Rust

多种方式

### ➖ 命令

Tauri 通过命令模型来处理调用。

**大概过程**

- `#[tauri::command]` 对 rust 中的函数添加注释，将其标记为命令。

  默认写在 lib.rs 中。也可以分模块自定义在其它文件中。区别在构造函数中提供命令定位方式

  ```rust
  #[tauri::command]
  fn my_custom_command() {
    println!("I was invoked from JavaScript!");
  }
  ```

- 在构建函数中提供命令列表

  ```rust
  #[cfg_attr(mobile, tauri::mobile_entry_point)]
  pub fn run() {
    tauri::Builder::default()
  +    .invoke_handler(tauri::generate_handler![my_custom_command])
      .run(tauri::generate_context!())
      .expect("error while running tauri application");
  }
  ```

- 前端调用命令

  ```rust
  // 使用 Tauri API npm 包时:
  import { invoke } from '@tauri-apps/api/core';
  
  // 使用 Tauri 全局脚本（不使用 npm 包时）
  // 确保在 `tauri.conf.json` 中设置 `app.withGlobalTauri` 为 true
  const invoke = window.__TAURI__.core.invoke;
  
  // 调用命令
  invoke('my_custom_command');
  ```

**传递参数**

带参数命令
```rust
#[tauri::command]
fn my_custom_command(invoke_message: String) {
  println!("I was invoked from JavaScript, with this message: {}", invoke_message);
}
```

**返回数据**

```rust
#[tauri::command]
fn my_custom_command() -> String {
  "Hello from Rust!".into()
}
```

- 普通数据

```rust
invoke('my_custom_command').then((message) => console.log(message));
```

- 缓冲区数组

一般情况下，数据都是序列化为 Json 格式返回。如果数据量太大，会减慢应用程序的速度。可以使用优化的方式返回数组缓冲区

```rust
use tauri::ipc::Response;
#[tauri::command]
fn read_file() -> Response {
  let data = std::fs::read("/path/to/file").unwrap();
  tauri::ipc::Response::new(data)
}
```

**错误处理**

处理程序如果失败，使用 Result 封装错误，并完善错误捕捉处理逻辑

```rust
#[tauri::command]
fn login(user: String, password: String) -> Result<String, String> {
  if user == "tauri" && password == "tauri" {
    // resolve
    Ok("logged_in".to_string())
  } else {
    // reject
    Err("invalid credentials".to_string())
  }
}
```

```rust
invoke('login', { user: 'tauri', password: '0j4rijw8=' })
  .then((message) => console.log(message))
  .catch((error) => console.error(error));
```



**异步命令**

如果您的命令需要异步运行，只需将其声明为 `async` 。
编写命令时，应该考虑它是否可以异步化，避免 UI 冻结减速。

异步相关的特殊情况

- 不能简单使用包含借用类型的参数

  解决方式：

  - 将类型转换为非借用类型
  - 将返回类型包装在 Result 中



**通道**
通道是 Tauri 推荐的流式数据传输机制.

```rust
use tokio::io::AsyncReadExt;

#[tauri::command]
async fn load_image(path: std::path::PathBuf, reader: tauri::ipc::Channel<&[u8]>) {
  // 为了简单起见，本示例未包含错误处理
  let mut file = tokio::fs::File::open(path).await.unwrap();

  let mut chunk = vec![0; 4096];

  loop {
    let len = file.read(&mut chunk).await.unwrap();
    if len == 0 {
      // 读到文件末尾时结束循环
      break;
    }
    reader.send(&chunk).unwrap();
  }
}
```



**命令中访问 前端元素**

- WebviewWindow

命令可以访问调用该消息的 WebviewWindow 实例

```rust
#[tauri::command]
async fn my_custom_command(webview_window: tauri::WebviewWindow) {
  println!("WebviewWindow: {}", webview_window.label());
}
```

- 访问  APPName

```rust
#[tauri::command]
async fn my_custom_command(app_handle: tauri::AppHandle) {
  let app_dir = app_handle.path_resolver().app_dir();
  use tauri::GlobalShortcutManager;
  app_handle.global_shortcut_manager().register("CTRL + U", move || {});
}
```

**创建多个命令：**

```rust
#[tauri::command]
fn cmd_a() -> String {
  "Command a"
}
#[tauri::command]
fn cmd_b() -> String {
  "Command b"
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![cmd_a, cmd_b])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
```

### ➖ 事件系统

事件系统是前端和 Rust 之间更简单的通信机制。 与命令不同，事件不是类型安全的，始终是异步的，无法返回值，并且仅支持 JSON 格式的负载。

- **全局事件**
- **Webview 事件** 向特定 webview 注册的监听器触发事件
- 监听事件
