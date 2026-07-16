# 📌 Tauri 通信

>Tauri 采用 IPC （进程通信架构）。程序逻辑架构为双核模型：
>
>- Rust Core （Rust 后端中枢）
>- WebView （前端渲染环境）

该文档作为官方文档困惑点的补充。快速回顾浏览，深化记忆

- [从前端调用 rust - offical doc](https://v2.tauri.app/zh-cn/develop/calling-rust/#%E5%9F%BA%E7%A1%80%E7%A4%BA%E4%BE%8B)
- [从 Rust 调用前端](https://v2.tauri.app/zh-cn/develop/calling-frontend/)

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

## ✔️ 从 Rust 调用前端

### ➖ 事件系统

事件系统支持 前端、Rust 之间的双向通信。
事件系统有效负载始终是 JSON 字符串，没有强类型支持。

- **全局事件**

  发给全局监听者：

  ```rust
  use tauri::{AppHandle, Emitter};
  
  #[tauri::command]
  fn download(app: AppHandle, url: String) {
    app.emit("download-started", &url).unwrap();
    for progress in [1, 15, 50, 80, 100] {
      app.emit("download-progress", progress).unwrap();
    }
    app.emit("download-finished", &url).unwrap();
  }
  ```

- **Webview 事件**

  使用 [Emitter#emit_to](https://docs.rs/tauri/2.0.0/tauri/trait.Emitter.html#tymethod.emit_to) 函数，向 特定 web view 注册的监听器触发事件

  通过调用 [Emitter#emit_filter](https://docs.rs/tauri/2.0.0/tauri/trait.Emitter.html#tymethod.emit_filter) 来触发 webview 列表事件

- **事件负载**

  任何可序列化的类型，（实现 Clone 接口）

- 监听事件

  - 全局事件

    ```typescript
    import { listen } from '@tauri-apps/api/event';
    
    type DownloadStarted = {
      url: string;
      downloadId: number;
      contentLength: number;
    };
    
    listen<DownloadStarted>('download-started', (event) => {
      console.log(
        `downloading ${event.payload.contentLength} bytes from ${event.payload.url}`
      );
    });
    ```

  - 特定 webview 事件

    ```typescript
    import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';
    
    const appWebview = getCurrentWebviewWindow();
    appWebview.listen<string>('logged-in', (event) => {
      localStorage.setItem('session-token', event.payload);
    });
    ```

  - 一次事件

    ```typescript
    import { once } from '@tauri-apps/api/event';
    import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';
    
    once('ready', (event) => {});
    
    const appWebview = getCurrentWebviewWindow();
    appWebview.once('ready', () => {});
    ```

### ➖ 通道

通道旨在快速传递有序数据。它们在内部用于流式传输操作， 例如下载进度、子进程输出和 WebSocket 消息

```rust
use tauri::{AppHandle, ipc::Channel};
use serde::Serialize;

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase", rename_all_fields = "camelCase", tag = "event", content = "data")]
enum DownloadEvent<'a> {
  Started {
    url: &'a str,
    download_id: usize,
    content_length: usize,
  },
  Progress {
    download_id: usize,
    chunk_length: usize,
  },
  Finished {
    download_id: usize,
  },
}

#[tauri::command]
fn download(app: AppHandle, url: String, on_event: Channel<DownloadEvent>) {
  let content_length = 1000;
  let download_id = 1;

  on_event.send(DownloadEvent::Started {
    url: &url,
    download_id,
    content_length,
  }).unwrap();

  for chunk_length in [15, 150, 35, 500, 300] {
    on_event.send(DownloadEvent::Progress {
      download_id,
      chunk_length,
    }).unwrap();
  }

  on_event.send(DownloadEvent::Finished { download_id }).unwrap();
}
```

## 🛠️ GitTributary 实践回链

- `#[tauri::command]` 是属性过程宏,但命令还需要进入 `generate_handler!` 注册列表。Rust 宏分类见 [宏](../../../../语言基础/rust/20.高级特性/20.5.宏.md)。
- Command 通过 `State<'_, AppState>` 访问受管应用状态,见 [Tauri State 与应用状态](../../核心概念/State%20与应用状态.md)。
- IPC 请求和响应依赖 Serde trait,见 [Serde 序列化与反序列化](../../../../语言基础/rust/生态库/Serde%20序列化与反序列化.md)。
- 项目完整解读见 [Command 层代码阅读与架构演进](../../../../开源项目/GitTributary/技术经验/Command%20层代码阅读与架构演进.md)。
