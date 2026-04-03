# Lab 5.3: 命令面板

**Phase 5 — 前后端联动**
**预计耗时：** 2-3 天
**前置：** Lab 3.3（PluginRegistry）、Lab 3.4（AppShell）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 实现 VSCode 风格的命令面板（Cmd+K / Ctrl+K）
- [ ] 处理键盘事件（快捷键、上下键导航、回车执行）
- [ ] 实现实时过滤（输入即过滤）
- [ ] 设计模态框的状态管理

## 2. Background

命令面板是现代开发工具的标配交互模式（VSCode、Figma、Raycast）。它解决了"功能太多找不到"的问题 — 用户不需要记住菜单路径，只需要模糊搜索。

在 GitTributary 中，命令面板是插件命令的主要入口之一。所有插件注册的 commands + 系统内置命令都可以通过命令面板触发。

**关键概念：**
- React 受控组件（输入框的值由 state 驱动）
- 键盘事件处理（onKeyDown）
- 模态框的打开/关闭状态管理
- 列表项的高亮和导航

## 3. Procedure

### Step 1: 收集命令

```typescript
interface CommandItem {
  pluginName: string;
  commandId: string;
  label: string;
  description: string;
}

function collectCommands(): CommandItem[] {
  const items: CommandItem[] = [];

  // 从 PluginRegistry 收集所有插件的命令
  for (const plugin of pluginRegistry.all()) {
    for (const cmd of plugin.manifest.commands) {
      items.push({
        pluginName: plugin.manifest.name,
        commandId: cmd.id,
        label: `${plugin.manifest.name}: ${cmd.id}`,
        description: cmd.description,
      });
    }
  }

  // 添加系统内置命令
  items.push(
    { pluginName: 'system', commandId: 'reload-plugins', label: 'Reload Plugins', description: 'Reload all plugins' },
    { pluginName: 'system', commandId: 'open-settings', label: 'Open Settings', description: 'Open settings panel' },
  );

  return items;
}
```

### Step 2: 命令面板组件

```tsx
import { useState, useEffect, useRef, useMemo } from 'react';

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
  onSelect: (item: CommandItem) => void;
}

function CommandPalette({ open, onClose, onSelect }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [highlightIndex, setHighlightIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const allCommands = useMemo(() => collectCommands(), []);

  // 过滤结果
  const filtered = useMemo(() => {
    if (!query) return allCommands;
    const q = query.toLowerCase();
    return allCommands.filter(
      c => c.label.toLowerCase().includes(q) || c.description.toLowerCase().includes(q)
    );
  }, [query, allCommands]);

  // 打开时聚焦输入框
  useEffect(() => {
    if (open) {
      setQuery('');
      setHighlightIndex(0);
      inputRef.current?.focus();
    }
  }, [open]);

  // 键盘处理
  function handleKeyDown(e: React.KeyboardEvent) {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightIndex(i => Math.min(i + 1, filtered.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightIndex(i => Math.max(i - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (filtered[highlightIndex]) {
          onSelect(filtered[highlightIndex]);
          onClose();
        }
        break;
      case 'Escape':
        onClose();
        break;
    }
  }

  if (!open) return null;

  return (
    <div className="command-palette-overlay" onClick={onClose}>
      <div className="command-palette" onClick={e => e.stopPropagation()}>
        <input
          ref={inputRef}
          value={query}
          onChange={e => { setQuery(e.target.value); setHighlightIndex(0); }}
          onKeyDown={handleKeyDown}
          placeholder="Type a command..."
        />
        <ul className="command-list">
          {filtered.map((item, i) => (
            <li
              key={`${item.pluginName}:${item.commandId}`}
              className={i === highlightIndex ? 'highlighted' : ''}
              onClick={() => { onSelect(item); onClose(); }}
            >
              <span className="label">{item.label}</span>
              <span className="description">{item.description}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

### Step 3: 快捷键绑定

```tsx
function App() {
  const [paletteOpen, setPaletteOpen] = useState(false);

  useEffect(() => {
    function handleGlobalKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setPaletteOpen(prev => !prev);
      }
    }
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  async function handleCommandSelect(item: CommandItem) {
    if (item.pluginName === 'system') {
      // 系统命令处理
    } else {
      await pluginHost.invoke(item.pluginName, item.commandId);
    }
  }

  return (
    <>
      <AppShell />
      <CommandPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        onSelect={handleCommandSelect}
      />
    </>
  );
}
```

### Step 4: CSS 样式

```css
.command-palette-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; padding-top: 100px;
}

.command-palette {
  width: 500px; max-height: 400px;
  background: white; border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  overflow: hidden;
}

.command-palette input {
  width: 100%; padding: 12px; border: none; outline: none;
  font-size: 16px; border-bottom: 1px solid #eee;
}

.command-list { list-style: none; margin: 0; padding: 0; overflow-y: auto; max-height: 340px; }
.command-list li { padding: 8px 12px; cursor: pointer; display: flex; justify-content: space-between; }
.command-list li.highlighted { background: #e3f2fd; }
.command-list .label { font-weight: 500; }
.command-list .description { color: #888; font-size: 13px; }
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 命令面板组件 | `src/components/CommandPalette.tsx` | 核心组件 |
| 命令收集 | `src/lib/commands.ts` | collectCommands |
| 快捷键 | `src/App.tsx` | Cmd+K 绑定 |
| 样式 | `src/components/CommandPalette.css` | 基本样式 |

## 5. Evaluation Criteria

- [ ] Cmd+K 打开命令面板
- [ ] 输入 "deploy" 能过滤出部署相关命令
- [ ] 上下键导航，回车执行
- [ ] Escape 关闭命令面板
- [ ] 命令面板关闭后 UI 状态正确恢复

## 6. Extensions (Optional)

- [ ] 添加 `when` 条件过滤（只在特定页面显示某些命令）
- [ ] 支持命令分组（按插件名分组显示）
- [ ] 最近使用的命令排在最前面
- [ ] 添加键盘快捷键提示（如 "Ctrl+Shift+D" → Deploy）

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- 模态框和键盘交互的设计模式 -->

**可复用的代码：**

<!-- 命令面板是 GitTributary 的核心交互组件 -->
