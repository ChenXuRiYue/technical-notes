# 📌 Hooks 是什么

**Hook 是 React 提供的特殊函数，让函数组件能使用 React 的状态、副作用、上下文和性能优化等机制。**

例如：

```tsx
function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}
```

`Counter` 是函数组件，`useState` 是 Hook。`useState` 让这个组件能在多次渲染之间保存 `count`。

> 函数组件是 React 组件的一种实现方式；它的完整概念见 [[组件是什么]]。TypeScript 只提供类型检查，不是函数组件或 Hook 的来源。

## 📄 Hook 提供什么能力

| 需求 | 常用 Hook | 直接理解 |
| --- | --- | --- |
| 保存会影响 UI 的数据 | `useState` / `useReducer` | 让组件记住状态 |
| 与 React 外部系统同步 | `useEffect` | 请求、订阅、定时器、第三方库 |
| 保存不用于显示的可变值 | `useRef` | 存值，但改变时不触发渲染 |
| 读取跨层共享数据 | `useContext` | 读取 Context |
| 避免不必要的计算或函数重建 | `useMemo` / `useCallback` | 性能优化 |
| 处理非紧急更新 | `useTransition` / `useDeferredValue` | 调度更新优先级 |

快速判断：

```text
UI 需要记住它？        → useState / useReducer
需要和外部系统同步？  → useEffect
只想跨渲染存一个值？  → useRef
需要读跨层共享数据？  → useContext
已经确认有性能问题？  → useMemo / useCallback
```

## 📄 为什么需要 Hook

函数组件每次渲染都会重新执行。普通局部变量也会重新创建，不能作为组件状态：

```tsx
function Counter() {
  let count = 0;

  return (
    <button onClick={() => count += 1}>
      {count}
    </button>
  );
}
```

这段代码有两个问题：

1. 修改 `count` 不会通知 React 更新页面。
2. 如果组件因其他原因重新渲染，`count` 又会变回 `0`。

Hook 将需要跨渲染保留的数据交给 React 管理：

```tsx
const [count, setCount] = useState(0);
```

```text
setCount 提交新状态
        ↓
React 保存状态
        ↓
React 重新执行组件
        ↓
useState 返回当前状态
        ↓
组件返回新的 UI
```

因此，Hook 不是让函数局部变量突然有了记忆，而是让组件函数接入 React 保存的状态和其他机制。名称 Hook 来自 `hook into`：「接入 React」。

## 📄 Hook 与类组件的关系

React 16.8 之前，需要状态和生命周期的组件通常要写成类组件：

```tsx
class Counter extends React.Component {
  state = { count: 0 };

  render() {
    return (
      <button onClick={() => this.setState({ count: this.state.count + 1 })}>
        {this.state.count}
      </button>
    );
  }
}
```

Hook 引入后，函数组件也能使用这些 React 能力：

```tsx
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

Hook 不是「类组件 API 的换名版」。它的价值还在于：

- 不需要处理 `this`、构造函数和方法绑定。
- 可以按业务关注点组织逻辑，而不是拆到多个生命周期方法。
- 可以用自定义 Hook 复用有状态逻辑。

## 📄 两条硬规则

### 🔖 只在顶层调用

不要把 Hook 放进 `if`、`for`、嵌套函数或提前 `return` 之后：

```tsx
// 错误
if (loggedIn) {
  const [user, setUser] = useState(null);
}
```

Hook 必须在每次渲染时以相同顺序调用。

### 🔖 只在 React 函数中调用

Hook 只能在下面两种位置调用：

- React 函数组件。
- 自定义 Hook。

不能在普通工具函数、类组件或事件回调内临时调用。

## 📄 自定义 Hook

**自定义 Hook 是以 `use` 开头、内部可以组合其他 Hook 的函数，用来复用有状态逻辑。**

```tsx
function useWindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return width;
}
```

组件中可以像调用内置 Hook 一样使用：

```tsx
function Layout() {
  const width = useWindowWidth();
  return <div>{width}</div>;
}
```

自定义 Hook 复用的是**逻辑**，不是共享同一份状态。每个组件调用 `useWindowWidth()` 时，都会拥有自己的 Hook 状态。

## 📄 内部原理：调用顺序对应状态槽

React 在组件对应的 Fiber 节点上保存 Hook 状态。组件每次渲染时，React 按 Hook 的调用顺序取回对应状态：

```text
第 1 次渲染:  useState → 槽 0    useRef → 槽 1    useEffect → 槽 2
第 2 次渲染:  useState → 槽 0    useRef → 槽 1    useEffect → 槽 2
```

如果 Hook 被放进条件分支，某次渲染少调用一个 Hook，后面的调用就无法与上次渲染对应。这就是「只在顶层调用」的根本原因。

日常使用只需要从 `react` 导入：

```tsx
import { useEffect, useRef, useState } from "react";
```

更深入的实现在 `react-reconciler` 的 `ReactFiberHooks` 中。

## 📄 GitTributary 中的使用现场

`src/App.tsx` 导入了四种 Hook：

```tsx
import { useCallback, useEffect, useRef, useState } from "react";
```

| Hook | 在 App 中的责任 |
| --- | --- |
| `useState` | 保存激活模块、侧边栏宽度、展开状态等 UI 状态 |
| `useEffect` | 同步组件与异步流程、事件监听等外部系统 |
| `useRef` | 保存 DOM 引用或不需触发渲染的值 |
| `useCallback` | 在有必要时稳定函数引用 |

回看这段代码时，不需要先背 API，只需要问：

```text
这个组件需要记住什么？
它需要与哪个外部系统同步？
哪些值需要跨渲染保留，但不应触发 UI 更新？
哪些优化是有实际必要的？
```

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-07-12：按「显然结论 → 必要性推导 → 使用约束 → 内部原理」重写，压缩函数组件的前置说明。
- 2026-07-11：补充函数组件的概念，区分 JavaScript、TypeScript 与 React 的职责，并与 Hook 的引入动机衔接。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- Hook 概念、使用场景与两条规则参考 React 官方文档 Hooks 章节与 Rules of Hooks。
- Hook 调用顺序与状态保存机制对应 `react-reconciler` 的 `ReactFiberHooks`。
- 组件前置概念见 [[组件是什么]]，`useState` 语法与更新规则见 [[useState-语法]]。
