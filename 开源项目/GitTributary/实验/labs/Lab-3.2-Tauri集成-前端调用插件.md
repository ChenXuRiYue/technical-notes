# Lab 3.2: Tauri 集成 — 前端调用插件

**Phase 3 — 插件系统核心**
**预计耗时：** 2-3 天
**前置：** Lab 2.1（Tauri IPC）、Lab 3.1（PluginHostManager）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 用 `app.manage()` 在 Tauri 中管理全局状态
- [ ] 用 `tauri::State<'_, T>` 在 command 中访问状态
- [ ] 设计命名空间化的 IPC 命令格式
- [ ] 让前端通过 invoke 调用后端的插件系统

## 2. Background

Lab 3.1 实现了纯 Rust 的 PluginHostManager。现在需要把它接入 Tauri，让前端能通过 IPC 调用插件系统。

核心挑战：Tauri command 是扁平的（全局命名空间），但插件系统需要 `plugin:{name}|{command}` 的命名空间格式。

**关键概念：**
- `app.manage(state)` 注册全局状态
- `tauri::State<'_, T>` 在 command 函数中提取状态
- 命名空间解析：从 command 名称中提取 plugin name 和 command id
- 错误从 Rust 传递到前端的格式

## 3. Procedure

### Step 1: 注册状态

在 `src-tauri/src/lib.rs` 中：

```rust
use plugin_host::PluginHostManager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let mut phm = PluginHostManager::new();
    // 加载插件...

    tauri::Builder::default()
        .manage(phm)
        .invoke_handler(tauri::generate_handler![
            plugin_list,
            plugin_dispatch,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Step 2: 实现 Tauri Commands

```rust
#[tauri::command]
fn plugin_list(state: tauri::State<'_, PluginHostManager>) -> Result<Vec<PluginManifest>, String> {
    Ok(state.list().into_iter().cloned().collect())
}

#[tauri::command]
fn plugin_dispatch(
    plugin_name: String,
    command: String,
    args: Option<serde_json::Value>,
    state: tauri::State<'_, PluginHostManager>,
) -> Result<serde_json::Value, String> {
    state.dispatch(&plugin_name, &command, args)
        .map_err(|e| serde_json::to_string(&e).unwrap_or_else(|_| e.to_string()))
}
```

### Step 3: 前端封装 PluginHost

```typescript
// src/lib/pluginHost.ts
import { invoke } from '@tauri-apps/api/core';

interface PluginManifest {
  name: string;
  version: string;
  commands: { id: string; description: string }[];
}

class PluginHost {
  async listPlugins(): Promise<PluginManifest[]> {
    return invoke('plugin_list');
  }

  async invoke(pluginName: string, command: string, args?: Record<string, unknown>): Promise<unknown> {
    return invoke('plugin_dispatch', {
      pluginName,
      command,
      args,
    });
  }
}

export const pluginHost = new PluginHost();
```

### Step 4: 前端页面

```tsx
// src/App.tsx
import { useEffect, useState } from 'react';
import { pluginHost, PluginManifest } from './lib/pluginHost';

function App() {
  const [plugins, setPlugins] = useState<PluginManifest[]>([]);
  const [selectedPlugin, setSelectedPlugin] = useState<string | null>(null);
  const [result, setResult] = useState<unknown>(null);

  useEffect(() => {
    pluginHost.listPlugins().then(setPlugins);
  }, []);

  async function handleCommand(pluginName: string, command: string) {
    try {
      const r = await pluginHost.invoke(pluginName, command);
      setResult(r);
    } catch (e) {
      setResult({ error: String(e) });
    }
  }

  return (
    <div style={{ display: 'flex' }}>
      {/* 侧边栏 */}
      <aside style={{ width: '200px' }}>
        {plugins.map(p => (
          <div key={p.name} onClick={() => setSelectedPlugin(p.name)}>
            {p.name} ({p.commands.length} commands)
          </div>
        ))}
      </aside>

      {/* 主视图 */}
      <main>
        {selectedPlugin && (
          <>
            <h2>{selectedPlugin}</h2>
            {plugins.find(p => p.name === selectedPlugin)?.commands.map(cmd => (
              <button key={cmd.id} onClick={() => handleCommand(selectedPlugin, cmd.id)}>
                {cmd.id}
              </button>
            ))}
          </>
        )}
        {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
      </main>
    </div>
  );
}

export default App;
```

### Step 5: 测试

准备 mock 插件目录，启动应用，验证：
1. 侧边栏显示加载的插件名
2. 点击插件名，显示其命令列表
3. 点击命令，显示 mock 返回的结果

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| Rust commands | `src-tauri/src/lib.rs` | `plugin_list` + `plugin_dispatch` |
| 前端封装 | `src/lib/pluginHost.ts` | PluginHost class |
| 前端页面 | `src/App.tsx` | 侧边栏 + 主视图 |

## 5. Evaluation Criteria

- [ ] 启动应用，侧边栏显示从 manifest 加载的插件名
- [ ] 点击插件名，主视图显示 mock 数据
- [ ] 打开不存在的插件，显示错误信息
- [ ] TypeScript 类型完整，无编译错误

## 6. Extensions (Optional)

- [ ] 为 PluginHost 添加错误解析（将 JSON 字符串错误转为 Error 对象）
- [ ] 添加 loading 状态（调用时显示 loading）
- [ ] 用 `app.manage(PluginHostManager::new())` 的初始化改为从配置文件读取插件目录

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- Tauri State Management 的工作方式 -->

**可复用的代码：**

<!-- pluginHost.ts 和 Tauri command 注册模式可直接用于 GitTributary -->
