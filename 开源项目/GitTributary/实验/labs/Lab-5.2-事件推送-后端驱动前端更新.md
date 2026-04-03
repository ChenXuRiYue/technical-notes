# Lab 5.2: 事件推送 — 后端驱动前端更新

**Phase 5 — 前后端联动**
**预计耗时：** 2-3 天
**前置：** Lab 2.1（Tauri 事件基础）、Lab 5.1（完整 CRUD 流程）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 在 Rust 端用 `app.emit()` 推送事件到前端
- [ ] 在前端用 `listen()` 接收事件并更新 UI
- [ ] 实现异步 command + 进度事件的组合
- [ ] 理解请求-响应和事件推送两条通道的区别和配合

## 2. Background

Lab 5.1 只用到了请求-响应通道（前端主动调用）。但很多场景需要后端主动通知前端：

- 长时间任务的进度（Git 同步、部署）
- 文件变更通知
- 插件状态变化

这就是事件推送通道：`app.emit()` + `listen()`。

**关键概念：**
- `app.emit(event, payload)` 向所有监听者广播
- `listen()` 返回 unlisten 函数，需要在组件卸载时调用
- 异步 command 中可以边执行边 emit
- 事件命名空间：`plugin:{name}:{event}`

## 3. Procedure

### Step 1: Rust 端 — 异步 Command + 进度推送

```rust
#[tauri::command]
async fn start_sync(app: tauri::AppHandle) -> Result<String, String> {
    let total_steps = 100;

    for i in 0..=total_steps {
        // 模拟工作
        tokio::time::sleep(std::time::Duration::from_millis(50)).await;

        // 推送进度事件
        app.emit("plugin:git-sync:progress", serde_json::json!({
            "percent": i,
            "message": if i < total_steps {
                format!("Processing step {}/{}...", i, total_steps)
            } else {
                "Sync complete!".to_string()
            },
        })).map_err(|e| e.to_string())?;
    }

    Ok("done".to_string())
}
```

注册 command：

```rust
.invoke_handler(tauri::generate_handler![plugin_list, plugin_dispatch, start_sync])
```

### Step 2: 前端 — 监听事件 + 更新进度条

```tsx
import { listen, type UnlistenFn } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';
import { useState, useEffect, useRef } from 'react';

interface ProgressPayload {
  percent: number;
  message: string;
}

function SyncPanel() {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState<'idle' | 'running' | 'done'>('idle');
  const unlistenRef = useRef<UnlistenFn | null>(null);

  useEffect(() => {
    // 注册事件监听
    listen<ProgressPayload>('plugin:git-sync:progress', (event) => {
      setProgress(event.payload.percent);
      setMessage(event.payload.message);
    }).then(unlisten => {
      unlistenRef.current = unlisten;
    });

    // 清理
    return () => {
      unlistenRef.current?.();
    };
  }, []);

  async function handleSync() {
    setStatus('running');
    setProgress(0);
    try {
      await invoke('start_sync');
      setStatus('done');
    } catch (e) {
      setStatus('idle');
      setMessage(`Error: ${e}`);
    }
  }

  return (
    <div className="sync-panel">
      <h2>Git Sync</h2>
      <button onClick={handleSync} disabled={status === 'running'}>
        {status === 'running' ? 'Syncing...' : 'Start Sync'}
      </button>

      {/* 进度条 */}
      <div className="progress-bar" style={{ width: '100%', height: '20px', background: '#eee' }}>
        <div style={{
          width: `${progress}%`,
          height: '100%',
          background: status === 'done' ? '#4caf50' : '#2196f3',
          transition: 'width 0.1s',
        }} />
      </div>

      <p>{progress}% — {message}</p>
      {status === 'done' && <p className="success">Sync completed!</p>}
    </div>
  );
}
```

### Step 3: 验证

1. 点击 "Start Sync" 按钮
2. 进度条平滑从 0% 到 100%
3. 消息每 50ms 更新一次
4. 进度条更新期间 UI 仍然响应
5. 完成后显示 "Sync completed!"

### Step 4: 错误处理

测试异常场景：

```rust
#[tauri::command]
async fn start_sync_with_error(app: tauri::AppHandle) -> Result<String, String> {
    for i in 0..=50 {
        tokio::time::sleep(std::time::Duration::from_millis(50)).await;
        app.emit("plugin:git-sync:progress", serde_json::json!({
            "percent": i,
            "message": format!("Step {}/50", i),
        })).map_err(|e| e.to_string())?;

        if i == 30 {
            // 模拟错误
            app.emit("plugin:git-sync:error", serde_json::json!({
                "message": "Remote repository unreachable"
            })).map_err(|e| e.to_string())?;
            return Err("Sync failed".to_string());
        }
    }
    Ok("done".to_string())
}
```

前端添加错误监听：

```tsx
useEffect(() => {
  listen('plugin:git-sync:error', (event) => {
    const { message } = event.payload as { message: string };
    setStatus('idle');
    setMessage(`Error: ${message}`);
  }).then(unlisten => { /* 收集 */ });
}, []);
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| Rust command | `src-tauri/src/lib.rs` | `start_sync` |
| 前端组件 | `src/components/SyncPanel.tsx` | 进度条 + 事件监听 |

## 5. Evaluation Criteria

- [ ] 点击按钮，进度条平滑从 0% 到 100%
- [ ] 进度条更新不影响 UI 响应（非阻塞）
- [ ] 完成后有明确的完成状态
- [ ] unlisten 函数在组件卸载时被调用（无内存泄漏）

## 6. Extensions (Optional)

- [ ] 添加 "Cancel" 按钮，能取消正在进行的同步
- [ ] 支持多个并行任务的进度（每个任务有独立的事件命名空间）
- [ ] 用 `once()` 替代 `listen()` 处理一次性事件

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- 请求-响应和事件推送如何配合工作 -->

**可复用的代码：**

<!-- 进度事件的模式可用于 Git 同步、部署等多种场景 -->
