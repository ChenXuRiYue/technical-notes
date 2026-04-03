# Lab 2.1: Tauri Hello World + IPC 双向通信

**Phase 2 — Tauri 项目骨架**
**预计耗时：** 1-2 天
**前置：** 无（独立 Tauri 项目）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 用 `create-tauri-app` 创建一个可运行的 Tauri 项目
- [ ] 在 Rust 端注册 `#[tauri::command]`
- [ ] 在前端通过 `invoke()` 调用 Rust 命令（请求-响应通道）
- [ ] 在 Rust 端通过 `app.emit()` 推送事件到前端（事件推送通道）
- [ ] 在前端通过 `listen()` 接收后端事件

## 2. Background

Tauri 的核心是前后端分离架构：Rust 后端 + Web 前端（WebView）。两者通过 IPC 通信，有两条通道：

1. **请求-响应**：前端调用 `invoke(command, args)` → Rust 端的 `#[tauri::command]` 函数处理 → 返回结果
2. **事件推送**：Rust 端调用 `app.emit(event, payload)` → 前端通过 `listen(event, handler)` 接收

这两条通道是 GitTributary 所有插件通信的基础。

**关键概念：**
- `#[tauri::command]` 宏将 Rust 函数暴露给前端
- `invoke()` 返回 Promise，对应 Rust 函数的 `Result<T, E>`
- `app.emit()` 可以在任意时刻推送事件（不限于 command 函数内部）
- `listen()` 是非阻塞的，事件到达时触发回调

## 3. Procedure

### Step 1: 创建项目

```bash
npm create tauri-app@latest my-tauri-lab
# 选择: React + TypeScript
cd my-tauri-lab
npm install
```

### Step 2: Rust 端 — 注册 Command

在 `src-tauri/src/lib.rs`（或 `main.rs`）中：

```rust
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to Tauri.", name)
}

#[tauri::command]
async fn start_timer(app: tauri::AppHandle, seconds: u64) -> Result<String, String> {
    for i in 0..=seconds {
        app.emit("timer:tick", serde_json::json!({
            "current": i,
            "total": seconds,
            "percent": (i as f64 / seconds as f64 * 100.0) as u64
        })).map_err(|e| e.to_string())?;

        if i < seconds {
            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        }
    }
    Ok("Timer completed!".to_string())
}
```

注册 command：

```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet, start_timer])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Step 3: 前端 — 调用 Command + 监听事件

```tsx
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { useState, useEffect } from 'react';

function App() {
  const [name, setName] = useState('');
  const [greeting, setGreeting] = useState('');
  const [progress, setProgress] = useState(0);
  const [timerStatus, setTimerStatus] = useState('');

  // 监听 timer:tick 事件
  useEffect(() => {
    const unlisten = listen('timer:tick', (event) => {
      const { percent } = event.payload as { percent: number };
      setProgress(percent);
    });

    return () => { unlisten.then(fn => fn()); };
  }, []);

  async function handleGreet() {
    const result = await invoke<string>('greet', { name });
    setGreeting(result);
  }

  async function handleStartTimer() {
    setProgress(0);
    setTimerStatus('Running...');
    const result = await invoke<string>('start_timer', { seconds: 5 });
    setTimerStatus(result);
  }

  return (
    <div>
      {/* Greet 部分 */}
      <input value={name} onChange={e => setName(e.target.value)} placeholder="Your name" />
      <button onClick={handleGreet}>Greet</button>
      {greeting && <p>{greeting}</p>}

      {/* Timer 部分 */}
      <button onClick={handleStartTimer}>Start 5s Timer</button>
      <div style={{ width: '300px', background: '#eee', height: '20px' }}>
        <div style={{ width: `${progress}%`, background: '#4caf50', height: '100%' }} />
      </div>
      <p>{progress}% — {timerStatus}</p>
    </div>
  );
}

export default App;
```

### Step 4: 运行验证

```bash
cargo tauri dev
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| Tauri 项目 | `my-tauri-lab/` | 完整可运行项目 |
| Rust commands | `src-tauri/src/lib.rs` | `greet` + `start_timer` |
| 前端组件 | `src/App.tsx` | 调用 + 监听事件 |

## 5. Evaluation Criteria

- [ ] 输入名字点按钮，看到问候语
- [ ] 点计时器按钮，进度条每秒更新
- [ ] 进度条到 100% 后显示 "Timer completed!"
- [ ] 进度条更新期间 UI 仍然响应（非阻塞）

## 6. Extensions (Optional)

- [ ] 添加一个 `stop_timer` command，能取消正在进行的计时器
- [ ] 用 `once()` 替代 `listen()`，让事件只触发一次
- [ ] 尝试从前端 `emit` 一个事件给后端，用 Tauri 的 `Event` 系统

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- invoke 和 emit/listen 分别解决什么问题？ -->

**可复用的代码：**

<!-- 这个项目的 Tauri 配置和 IPC 模式可以直接用于 GitTributary -->
