# Lab 5.1: 完整的插件 CRUD 流程

**Phase 5 — 前后端联动**
**预计耗时：** 3-4 天
**前置：** Lab 3.2（Tauri 集成）、Lab 3.4（AppShell）、Lab 4.3（PHM + WASM）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 走通"扫描目录 → 加载插件 → 前端展示 → 用户调用 → 结果展示"的完整链路
- [ ] 理解错误从 WASM → Rust → IPC → 前端的完整传播路径
- [ ] 在浏览器 DevTools 中观察 IPC 调用
- [ ] 处理边界情况（插件不存在、命令不存在、WASM panic）

## 2. Background

前面的实验分别实现了各个组件（PHM、Tauri IPC、AppShell、WASM 插件）。本实验是第一次把它们全部串联起来。

这是从"玩具 Demo"到"可工作产品"的关键一步。

**关键概念：**
- 完整数据流的端到端验证
- 错误传播链路的每一层
- 前端错误边界（React Error Boundary）
- IPC 调用的调试方法

## 3. Procedure

### Step 1: 准备磁盘上的插件目录

```
plugins/
├── mock-deploy/
│   └── manifest.json          ← 内部插件
├── word-count/
│   ├── manifest.json          ← WASM 插件
│   └── plugin.wasm
└── broken-plugin/
    └── manifest.json          ← 格式错误，用于测试错误处理
```

### Step 2: 启动时加载

在 Tauri 启动时扫描并加载：

```rust
pub fn run() {
    let mut phm = PluginHostManager::new();

    // 注册内部插件
    phm.register_internal(create_mock_deploy_plugin());

    // 加载 WASM 插件
    let plugin_dir = std::env::current_dir().unwrap().join("plugins");
    if plugin_dir.exists() {
        match phm.load_wasm_dir(&plugin_dir) {
            Ok(loaded) => println!("Loaded WASM plugins: {:?}", loaded),
            Err(e) => eprintln!("Failed to load WASM plugins: {}", e),
        }
    }

    tauri::Builder::default()
        .manage(phm)
        .invoke_handler(tauri::generate_handler![plugin_list, plugin_dispatch])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Step 3: 前端完整页面

更新 App.tsx 使用 Lab 3.4 的 AppShell 布局，但数据源从 mock 改为真实 invoke：

```tsx
import { AppShell } from './components/AppShell';
import { usePlugins } from './hooks/usePlugins';

function App() {
  const { plugins, loading, error } = usePlugins();

  if (loading) return <div>Loading plugins...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <AppShell />;
}
```

### Step 4: 错误处理

在前端添加错误边界：

```tsx
class PluginErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { error: Error | null }
> {
  state = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div className="plugin-error">
          <h3>Plugin Error</h3>
          <p>{this.state.error.message}</p>
          <button onClick={() => this.setState({ error: null })}>Retry</button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### Step 5: 端到端验证

逐项检查：

1. 启动应用，侧边栏显示 `mock-deploy` 和 `word-count`
2. 点击 `mock-deploy`，显示 deploy 命令
3. 点击 deploy 按钮，显示 mock 返回结果
4. 点击 `word-count`，显示 count 命令
5. 点击 count 按钮，显示 WASM 返回结果
6. `broken-plugin` 不出现在列表中（加载失败被跳过或显示错误）
7. 手动调用不存在的插件名，显示友好错误信息
8. 手动调用存在的插件但不存在的命令，显示友好错误信息

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 完整项目 | `gittributary-lab/` | 可运行的端到端项目 |
| 插件 fixture | `plugins/` | 2 个正常 + 1 个异常 |
| 错误处理 | 前端组件 | Error Boundary + 错误展示 |

## 5. Evaluation Criteria

- [ ] 启动即看到所有插件
- [ ] 点击任意插件，能看到其可用命令列表
- [ ] 点击命令，能看到 mock/WASM 返回的结果
- [ ] 错误情况有友好的错误提示

## 6. Extensions (Optional)

- [ ] 在 DevTools 中观察 IPC 调用的 payload 和耗时
- [ ] 添加 loading spinner（invoke 过程中显示加载状态）
- [ ] 记录最近的调用历史（最近 10 次 invoke 的命令和结果）

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- 端到端联调的经验和教训 -->

**可复用的代码：**

<!-- 整个链路的代码都是 GitTributary 的基础 -->
