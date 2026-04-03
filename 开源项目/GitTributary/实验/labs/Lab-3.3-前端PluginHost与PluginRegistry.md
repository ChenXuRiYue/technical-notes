# Lab 3.3: 前端 PluginHost + PluginRegistry

**Phase 3 — 插件系统核心**
**预计耗时：** 2-3 天
**前置：** Lab 3.2（Tauri 集成）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 定义与 Rust Serde 输出严格对应的 TypeScript 类型
- [ ] 实现前端侧的插件注册中心（PluginRegistry）
- [ ] 封装带 loading/error 状态的自定义 Hook
- [ ] 组合以上部分构建完整的插件管理页面

## 2. Background

Lab 3.2 实现了最基本的前后端通信。但前端代码直接散落在 App.tsx 中，没有类型安全、没有状态管理、没有复用。

本实验要把前端侧的插件系统规范化：类型定义 → PluginRegistry → 自定义 Hook → 页面组件。

**关键概念：**
- TypeScript interface 与 Rust Serde 输出的一一对应
- 前端注册中心模式（Registry）
- 自定义 Hook 封装异步调用逻辑（loading/error/execute）
- 未来可升级为 Zustand 全局状态

## 3. Procedure

### Step 1: TypeScript 类型定义

创建 `src/types/plugin.ts`：

```typescript
export interface CommandDecl {
  id: string;
  description: string;
}

export interface PluginUIDecl {
  sidebarEntry?: {
    label: string;
    icon: string;
    order?: number;
  };
  mainView?: {
    type: 'form' | 'list' | 'custom' | 'webview';
    component?: string;
  };
}

export interface PluginManifest {
  name: string;
  version: string;
  commands: CommandDecl[];
  ui?: PluginUIDecl;
}

export type PluginStatus = 'active' | 'inactive' | 'error';

export interface RegisteredPlugin {
  manifest: PluginManifest;
  status: PluginStatus;
}
```

### Step 2: PluginRegistry

创建 `src/lib/PluginRegistry.ts`：

```typescript
import { PluginManifest, RegisteredPlugin } from '../types/plugin';

export class PluginRegistry {
  private plugins = new Map<string, RegisteredPlugin>();

  register(manifest: PluginManifest): void {
    this.plugins.set(manifest.name, { manifest, status: 'inactive' });
  }

  get(name: string): RegisteredPlugin | undefined {
    return this.plugins.get(name);
  }

  all(): RegisteredPlugin[] {
    return Array.from(this.plugins.values());
  }

  sidebarEntries() {
    return this.all()
      .filter(p => p.manifest.ui?.sidebarEntry)
      .map(p => ({
        name: p.manifest.name,
        label: p.manifest.ui!.sidebarEntry!.label,
        icon: p.manifest.ui!.sidebarEntry!.icon,
        order: p.manifest.ui!.sidebarEntry!.order ?? 99,
      }))
      .sort((a, b) => a.order - b.order);
  }

  allCommands() {
    return this.all().flatMap(p =>
      p.manifest.commands.map(cmd => ({
        pluginName: p.manifest.name,
        command: cmd,
      }))
    );
  }
}
```

### Step 3: 自定义 Hooks

创建 `src/hooks/usePlugins.ts`：

```typescript
import { useState, useEffect, useCallback } from 'react';
import { pluginHost } from '../lib/pluginHost';
import { pluginRegistry } from '../lib/PluginRegistry';
import { PluginManifest } from '../types/plugin';

export function usePlugins() {
  const [plugins, setPlugins] = useState<PluginManifest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    pluginHost.listPlugins()
      .then(list => {
        list.forEach(m => pluginRegistry.register(m));
        setPlugins(list);
      })
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  return { plugins, loading, error, registry: pluginRegistry };
}

export function useActivePlugin() {
  const [active, setActive] = useState<string | null>(null);
  return { active, setActive, plugin: active ? pluginRegistry.get(active) : null };
}

export function usePluginCommand(pluginName: string, command: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<unknown>(null);

  const execute = useCallback(async (args?: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    try {
      const result = await pluginHost.invoke(pluginName, command, args);
      setData(result);
      return result;
    } catch (e) {
      setError(e as Error);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [pluginName, command]);

  return { execute, data, loading, error };
}
```

### Step 4: 组合页面

更新 `src/App.tsx`，使用 hooks：

```tsx
import { usePlugins, useActivePlugin, usePluginCommand } from './hooks/usePlugins';

function App() {
  const { plugins, loading, error } = usePlugins();
  const { active, setActive, plugin } = useActivePlugin();

  if (loading) return <div>Loading plugins...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div style={{ display: 'flex' }}>
      <aside>
        {plugins.map(p => (
          <div
            key={p.name}
            onClick={() => setActive(p.name)}
            style={{ fontWeight: active === p.name ? 'bold' : 'normal' }}
          >
            {p.ui?.sidebarEntry?.label ?? p.name}
          </div>
        ))}
      </aside>
      <main>
        {plugin ? <PluginDetail pluginName={active!} /> : <p>Select a plugin</p>}
      </main>
    </div>
  );
}

function PluginDetail({ pluginName }: { pluginName: string }) {
  const plugin = pluginRegistry.get(pluginName)!;
  const { execute, data, loading, error } = usePluginCommand(pluginName, 'status');

  return (
    <div>
      <h2>{plugin.manifest.name} v{plugin.manifest.version}</h2>
      <p>Commands: {plugin.manifest.commands.map(c => c.id).join(', ')}</p>
      <button onClick={() => execute()} disabled={loading}>
        {loading ? 'Loading...' : 'Get Status'}
      </button>
      {error && <p style={{ color: 'red' }}>{error.message}</p>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 类型定义 | `src/types/plugin.ts` | PluginManifest 等 interface |
| 注册中心 | `src/lib/PluginRegistry.ts` | PluginRegistry class |
| 自定义 Hooks | `src/hooks/usePlugins.ts` | usePlugins, useActivePlugin, usePluginCommand |
| 页面 | `src/App.tsx` | 使用以上组件 |

## 5. Evaluation Criteria

- [ ] TypeScript 类型与 Rust Serde 输出对应，无类型错误
- [ ] `usePlugins()` 返回 manifest 列表
- [ ] `usePluginCommand` 返回带 loading/error 的执行函数
- [ ] 页面无 TypeScript 编译错误

## 6. Extensions (Optional)

- [ ] 将 PluginRegistry 升级为 Zustand store
- [ ] 添加 `usePluginEvent` hook（监听后端事件）
- [ ] 为 `usePluginCommand` 添加自动重试逻辑

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- 自定义 Hook 的设计模式 -->

**可复用的代码：**

<!-- 类型定义、PluginRegistry、Hooks 都是 GitTributary 前端的核心 -->
