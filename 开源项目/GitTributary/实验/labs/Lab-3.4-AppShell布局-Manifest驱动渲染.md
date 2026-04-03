# Lab 3.4: AppShell 布局 — Manifest 驱动渲染

**Phase 3 — 插件系统核心**
**预计耗时：** 2-3 天
**前置：** Lab 3.3（PluginRegistry + Hooks）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 实现"根据配置动态渲染不同组件"的前端架构
- [ ] 使用 React 组合模式构建 AppShell 布局
- [ ] 用 switch/map 模式实现条件渲染
- [ ] 理解"manifest 就是 props"的核心思想

## 2. Background

GitTributary 的核心前端架构是：**manifest 驱动 UI**。不是硬编码哪些插件有哪些视图，而是从 manifest 的 `ui.mainView.type` 字段决定渲染什么组件。

这种模式的威力在于：新增一个插件时，不需要修改前端核心代码 — 只需要提供一个符合约定的 manifest。

**关键概念：**
- React 组合模式（Sidebar + MainView + StatusBar）
- 条件渲染（switch on manifest.ui.mainView.type）
- props 驱动 UI（manifest 就是 props）
- 组件解耦（每个视图组件独立，互不依赖）

## 3. Procedure

### Step 1: 准备 Mock 插件数据

创建 3 个 mock manifest，分别使用不同的 `mainView.type`：

```typescript
// src/mocks/plugins.ts
export const mockPlugins: PluginManifest[] = [
  {
    name: 'git-deploy',
    version: '0.1.0',
    commands: [
      { id: 'deploy', description: 'Deploy to GitHub Pages' },
      { id: 'preview', description: 'Preview deploy' },
    ],
    ui: {
      sidebarEntry: { label: 'Deploy', icon: 'rocket', order: 10 },
      mainView: { type: 'form', component: 'DeployForm' },
    },
  },
  {
    name: 'note-stats',
    version: '0.1.0',
    commands: [{ id: 'calculate', description: 'Calculate statistics' }],
    ui: {
      sidebarEntry: { label: 'Stats', icon: 'chart', order: 20 },
      mainView: { type: 'list', component: 'StatsList' },
    },
  },
  {
    name: 'custom-tool',
    version: '0.1.0',
    commands: [{ id: 'run', description: 'Run custom tool' }],
    ui: {
      sidebarEntry: { label: 'Tool', icon: 'wrench', order: 30 },
      mainView: { type: 'custom' },
    },
  },
];
```

### Step 2: AppShell 组件

```tsx
// src/components/AppShell.tsx
function AppShell() {
  const [activePlugin, setActivePlugin] = useState<string | null>(null);

  return (
    <div className="app-shell" style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gridTemplateRows: '1fr 30px', height: '100vh' }}>
      <Sidebar
        entries={pluginRegistry.sidebarEntries()}
        active={activePlugin}
        onSelect={setActivePlugin}
      />
      <MainView pluginName={activePlugin} />
      <StatusBar pluginName={activePlugin} />
    </div>
  );
}
```

### Step 3: Sidebar

```tsx
function Sidebar({ entries, active, onSelect }) {
  return (
    <nav className="sidebar">
      {entries.map(e => (
        <div
          key={e.name}
          className={`sidebar-item ${active === e.name ? 'active' : ''}`}
          onClick={() => onSelect(e.name)}
        >
          <span className="icon">{e.icon}</span>
          <span>{e.label}</span>
        </div>
      ))}
    </nav>
  );
}
```

### Step 4: MainView — 条件渲染分发

```tsx
function MainView({ pluginName }: { pluginName: string | null }) {
  if (!pluginName) return <WelcomeView />;

  const plugin = pluginRegistry.get(pluginName);
  if (!plugin) return <div>Plugin not found: {pluginName}</div>;

  const viewType = plugin.manifest.ui?.mainView?.type ?? 'custom';

  switch (viewType) {
    case 'form':    return <PluginFormView pluginName={pluginName} />;
    case 'list':    return <PluginListView pluginName={pluginName} />;
    case 'custom':  return <PluginCustomView pluginName={pluginName} />;
    case 'webview': return <PluginWebView pluginName={pluginName} />;
    default:        return <PluginCustomView pluginName={pluginName} />;
  }
}
```

### Step 5: 实现视图组件骨架

每个视图组件只需要实现基本结构：

```tsx
function PluginFormView({ pluginName }: { pluginName: string }) {
  const plugin = pluginRegistry.get(pluginName)!;
  return (
    <div>
      <h2>{plugin.manifest.name}</h2>
      <form onSubmit={e => { e.preventDefault(); /* invoke command */ }}>
        {plugin.manifest.commands.map(cmd => (
          <button key={cmd.id} type="submit">{cmd.description}</button>
        ))}
      </form>
    </div>
  );
}

function PluginListView({ pluginName }: { pluginName: string }) {
  // 类似实现
}

function PluginCustomView({ pluginName }: { pluginName: string }) {
  // 类似实现
}
```

### Step 6: StatusBar

```tsx
function StatusBar({ pluginName }: { pluginName: string | null }) {
  const plugin = pluginName ? pluginRegistry.get(pluginName) : null;
  return (
    <footer className="status-bar">
      {plugin ? `${plugin.manifest.name} v${plugin.manifest.version}` : 'Ready'}
    </footer>
  );
}
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| AppShell | `src/components/AppShell.tsx` | 主布局组件 |
| Sidebar | `src/components/Sidebar.tsx` | 侧边栏 |
| MainView | `src/components/MainView.tsx` | 条件渲染分发 |
| 视图组件 | `src/components/views/` | FormView, ListView, CustomView |
| StatusBar | `src/components/StatusBar.tsx` | 状态栏 |
| Mock 数据 | `src/mocks/plugins.ts` | 3 个 mock manifest |

## 5. Evaluation Criteria

- [ ] 侧边栏显示 3 个插件名（从 manifest 动态读取，不是硬编码）
- [ ] 点击不同插件，主视图切换为不同类型的组件
- [ ] StatusBar 显示当前插件名和版本
- [ ] 没有选中插件时显示 WelcomeView

## 6. Extensions (Optional)

- [ ] 添加 CSS 过渡动画（视图切换时的淡入淡出）
- [ ] 支持 manifest 中 `sidebarEntry.order` 排序
- [ ] 添加 404 处理（pluginName 存在但 manifest 加载失败）

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- "manifest 驱动渲染"这种架构模式的理解 -->

**可复用的代码：**

<!-- AppShell 布局和条件渲染分发是 GitTributary 前端的核心架构 -->
