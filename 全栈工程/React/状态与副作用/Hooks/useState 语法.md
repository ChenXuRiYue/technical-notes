# 📌 useState 语法

`useState` 是 React 提供的 Hook，用来给函数组件加「局部状态」。读 React 组件时，组件函数顶部一组 `const [x, setX] = useState(...)` 就是在声明这个组件记住哪些会变的东西。

在 GitTributary 的 `src/App.tsx` 中，`useState` 回答了一个问题：

```text
App 这个外壳组件，需要在渲染之间记住哪些状态？
```

## 📄 从 App.tsx 看到的 useState 现场

`App` 组件函数开头：

```tsx
function App() {
  const [activeId, setActiveId] = useState(modules[0]?.id ?? "");
  const [collapsed, setCollapsed] = useState(true);
  const [width, setWidth] = useState(DEFAULT_WIDTH);
  const [dragging, setDragging] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const asideRef = useRef<HTMLElement>(null);
  ...
}
```

5 个 `useState` = 5 个独立状态槽：当前激活模块、侧边栏是否收起、侧边栏宽度、是否正在拖拽、「更多」面板是否展开。

### 🔖 返回值是元组 + 解构

```tsx
const [activeId, setActiveId] = useState(modules[0]?.id ?? "");
```

`useState<T>(initial)` 返回一个**元组** `[value, setter]`，用数组解构取出：

- `activeId` = 当前状态值。
- `setActiveId` = 改这个状态的函数。命名约定 `set` + 驼峰。

为什么是数组解构而不是对象？因为可以自由命名：

```tsx
const [activeId, setActiveId] = useState(...);   // 一对
const [width, setWidth] = useState(...);          // 另一对，名字不同
```

对象解构就得记住固定字段名，数组解构只看顺序。这是 React API 设计的一个取舍。

### 🔖 初始值的写法

```tsx
const [activeId, setActiveId] = useState(modules[0]?.id ?? "");
const [width, setWidth] = useState(DEFAULT_WIDTH);
const [collapsed, setCollapsed] = useState(true);
```

三种写法：

| 写法 | 含义 |
| --- | --- |
| `useState(true)` | 字面量初值 |
| `useState(DEFAULT_WIDTH)` | 引用模块级常量做初值 |
| `useState(modules[0]?.id ?? "")` | 表达式初值 |

表达式初值里有两个细节：

- `modules[0]?.id` 的 `?.` = 可选链，`modules` 为空数组时短路返回 `undefined`，不报 `Cannot read property of undefined`。
- `?? ""` = nullish 合并，仅当左侧是 `null`/`undefined` 时回退空串。注意它和 `||` 不同：`||` 会把 `0`/`""` 也当假值吞掉，`??` 不会。

初始值只在**首次渲染**求值一次，之后重渲染会忽略它（React 内部记住第一次的结果）。所以 `modules[0]?.id` 不会每次渲染都重新算。

### 🔖 泛型省略与推断

```tsx
const [collapsed, setCollapsed] = useState(true);   // 推断 boolean
const [width, setWidth] = useState(DEFAULT_WIDTH);  // 推断 number
```

泛型省略时，TS 从初始值推断类型：`true` → `boolean`，`DEFAULT_WIDTH`（number）→ `number`。需要显式约束时才写：

```tsx
const [activeId, setActiveId] = useState<string>(modules[0]?.id ?? "");
```

这里省略也能推断成 `string`，显式写是冗余但可读。项目里大多省略。

## 📄 Hooks 规则：调用顺序即状态槽

```tsx
const [activeId, setActiveId] = useState(...);   // 槽 0
const [collapsed, setCollapsed] = useState(...); // 槽 1
const [width, setWidth] = useState(...);         // 槽 2
const [dragging, setDragging] = useState(...);   // 槽 3
const [moreOpen, setMoreOpen] = useState(...);   // 槽 4
```

React 靠**调用顺序**把每次渲染的 `useState` 和上一次的状态槽对应起来。这带来硬约束：

- `useState` 不能放在 `if` / `for` / 三元里。条件分支会让某次渲染少调一个 `useState`，顺序错乱，状态串位。
- 必须在组件函数顶层、每次渲染都按相同顺序调用。

这是「Hooks 规则」的核心。App.tsx 里 5 个 `useState` 平铺在函数开头，没有条件，符合规则。

## 📄 setter 的两种用法

```tsx
setCollapsed(true);              // 直接给新值
setWidth((prev) => prev + 10);   // 函数式更新，拿前一个值算
```

- 直接给值：新状态和旧状态无关时用。
- 函数式更新 `setX(prev => ...)`：新状态依赖旧状态时用。连续多次调用时，React 会把它们排队依次算，避免读到脏值。

拖拽调宽度这类场景（`onMouseMove` 里连续改 `width`）就该用函数式更新，否则快速连续事件可能拿到同一个 `prev`。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- `src/App.tsx` 中 `App` 组件开头的 5 个 `useState` 现场。
- 元组解构、初始值只在首次渲染求值、Hooks 调用顺序约束，参考 React 官方文档 `useState` 与「Hooks 规则」。
- `?.` / `??` 与 `||` 的语义差异，见 [[变量声明]] 同源语言点。
