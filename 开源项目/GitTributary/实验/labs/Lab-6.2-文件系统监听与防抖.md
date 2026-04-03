# Lab 6.2: 文件系统监听 + 防抖

**Phase 6 — 专项功能**
**预计耗时：** 2-3 天
**前置：** Lab 5.2（事件推送）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 用 `notify` crate 监听目录变化
- [ ] 实现防抖逻辑（同一文件 500ms 内多次变更只触发一次）
- [ ] 将文件变更事件通过 Tauri event 推送到前端
- [ ] 理解事件驱动架构在实际场景中的应用

## 2. Background

GitTributary 需要监听笔记目录的变化（文件保存、新增、删除），并在前端实时反映。

`notify` crate 是 Rust 生态最常用的文件监听库。但文件保存时会触发多个事件（写入 + 属性变更），需要防抖处理。

**关键概念：**
- `notify::RecommendedWatcher` 跨平台文件监听
- 防抖（Debounce）：合并短时间内的多次事件
- `tokio::sync::mpsc` 在异步环境中传递事件
- 与 Tauri event system 集成

## 3. Procedure

### Step 1: 添加依赖

```toml
[dependencies]
notify = "7"
tokio = { version = "1", features = ["sync", "time"] }
tauri = { version = "2" }
serde = { version = "1", features = ["derive"] }
```

### Step 2: 实现防抖监听器

```rust
use notify::{RecommendedWatcher, RecursiveMode, Watcher, Event, EventKind};
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::{Duration, Instant};
use tokio::sync::mpsc;

#[derive(Debug, Clone, serde::Serialize)]
pub struct FileChangeEvent {
    pub path: String,
    pub kind: String, // "modified" | "created" | "deleted"
    pub timestamp: u64,
}

pub struct DebouncedWatcher {
    watcher: RecommendedWatcher,
    rx: mpsc::Receiver<notify::Result<Event>>,
}

impl DebouncedWatcher {
    pub fn new() -> Result<Self, notify::Error> {
        let (tx, rx) = mpsc::channel(100);

        let watcher = RecommendedWatcher::new(
            move |res: notify::Result<Event>| {
                let _ = tx.blocking_send(res);
            },
            notify::Config::default(),
        )?;

        Ok(Self { watcher, rx })
    }

    pub fn watch(&mut self, path: &std::path::Path) -> Result<(), notify::Error> {
        self.watcher.watch(path, RecursiveMode::Recursive)
    }

    pub fn unwatch(&mut self, path: &std::path::Path) -> Result<(), notify::Error> {
        self.watcher.unwatch(path)
    }
}
```

### Step 3: 防抖处理

```rust
pub async fn run_debounced_events(
    mut watcher: DebouncedWatcher,
    app: tauri::AppHandle,
    debounce_ms: u64,
) {
    let mut last_events: HashMap<PathBuf, Instant> = HashMap::new();
    let debounce_duration = Duration::from_millis(debounce_ms);

    while let Some(event) = watcher.rx.recv().await {
        if let Ok(event) = event {
            for path in event.paths {
                let now = Instant::now();

                // 防抖：如果同一路径在 debounce 窗口内已触发，跳过
                if let Some(last) = last_events.get(&path) {
                    if now.duration_since(*last) < debounce_duration {
                        continue;
                    }
                }

                last_events.insert(path.clone(), now);

                let kind = match event.kind {
                    EventKind::Create(_) => "created",
                    EventKind::Modify(_) => "modified",
                    EventKind::Remove(_) => "deleted",
                    _ => continue,
                };

                let change = FileChangeEvent {
                    path: path.to_string_lossy().to_string(),
                    kind: kind.to_string(),
                    timestamp: now.elapsed().as_secs(),
                };

                let _ = app.emit("fs:change", &change);
            }
        }
    }
}
```

### Step 4: 集成到 Tauri

```rust
#[tauri::command]
async fn start_watching(
    app: tauri::AppHandle,
    path: String,
) -> Result<String, String> {
    let mut watcher = DebouncedWatcher::new().map_err(|e| e.to_string())?;
    watcher.watch(std::path::Path::new(&path)).map_err(|e| e.to_string())?;

    tokio::spawn(run_debounced_events(watcher, app, 500));

    Ok(format!("Watching: {}", path))
}
```

### Step 5: 前端

```tsx
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';
import { useState, useEffect } from 'react';

interface FileChangeEvent {
  path: string;
  kind: 'created' | 'modified' | 'deleted';
}

function FileWatcher() {
  const [changes, setChanges] = useState<FileChangeEvent[]>([]);
  const [watching, setWatching] = useState(false);

  useEffect(() => {
    const unlisten = listen<FileChangeEvent>('fs:change', (event) => {
      setChanges(prev => [event.payload, ...prev].slice(0, 50));
    });
    return () => { unlisten.then(fn => fn()); };
  }, []);

  async function handleStart() {
    await invoke('start_watching', { path: '/path/to/notes' });
    setWatching(true);
  }

  return (
    <div>
      <button onClick={handleStart} disabled={watching}>
        {watching ? 'Watching...' : 'Start Watching'}
      </button>
      <ul>
        {changes.map((c, i) => (
          <li key={i}>
            <span className={`kind ${c.kind}`}>{c.kind}</span>
            {c.path}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Step 6: 验证

1. 启动监听
2. 在监听目录中用编辑器保存文件 → 前端显示 1 条变更
3. 快速连续保存同一个文件 → 前端只显示 1 条变更
4. 批量操作（`touch a.txt b.txt c.txt`）→ 各显示 1 条

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| DebouncedWatcher | `src-tauri/src/watcher.rs` | 防抖监听器 |
| Tauri command | `src-tauri/src/lib.rs` | `start_watching` |
| 前端组件 | `src/components/FileWatcher.tsx` | 变更列表 |

## 5. Evaluation Criteria

- [ ] 在监听目录中保存文件，前端实时显示变更
- [ ] 快速连续保存同一个文件，只显示一次变更事件
- [ ] 批量文件操作能正确触发多个独立事件

## 6. Extensions (Optional)

- [ ] 实现更智能的节流（Throttle）：每 200ms 最多触发一次
- [ ] 添加文件变更的行数/大小信息
- [ ] 监听多个目录

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- 防抖 vs 节流的区别和适用场景 -->

**可复用的代码：**

<!-- 文件监听是 GitTributary 的核心功能之一 -->
