# 📌 import / export 模块语法

`export` 定义一个模块对外提供什么，`import` 把这些导出连接到当前文件的局部作用域。读 TypeScript / React 文件时，文件顶部的一组 `import` 就像一张依赖清单：它告诉我们当前文件要使用哪些框架能力、第三方库、项目内组件、类型定义和工具函数。

最核心的心智模型不是“把另一份代码复制进来”，而是：

```text
导出方建立模块接口
        ↓
模块系统解析并连接导入、导出绑定
        ↓
导入方在当前文件中使用这些绑定
```

在 GitTributary 的 `src/App.tsx` 中，`import` 区基本回答了一个问题：

```text
App.tsx 这个前端应用外壳，依赖哪些外部能力和本地模块？
```

## 📄 30 秒快速回顾

看到一条 `import`，从右向左读：

```tsx
import { useState } from "react";
```

```text
"react"          -> 去哪个模块找
{ useState }      -> 拿该模块的哪个具名导出
useState          -> 在当前文件中用什么名字访问
```

常用语法可以压缩成下表：

| 目的 | 导出方 | 导入方 | 快速记忆 |
| --- | --- | --- | --- |
| 默认导入 | `export default App` | `import App from "./App"` | 无花括号，局部名可改 |
| 具名导入 | `export const foo = 1` | `import { foo } from "./x"` | 有花括号，名字要对应 |
| 导入时改名 | `export const foo = 1` | `import { foo as localFoo } from "./x"` | `as` 只改变当前文件中的名字 |
| 类型导入 | `export interface User {}` | `import type { User } from "./types"` | 只参与类型检查，通常不进入运行时 |
| 值与类型混合 | 分别导出值和类型 | `import { fn, type User } from "./x"` | 一行区分运行时值和编译期类型 |
| 命名空间导入 | 多个导出 | `import * as api from "./api"` | 通过 `api.foo` 访问 |
| 只触发模块执行 | 模块含顶层代码 | `import "./setup"` | 不取名字，只求值模块 |
| 动态导入 | 正常导出 | `await import("./feature")` | 执行到此处时异步加载 |

快速判断默认导入和具名导入，只看花括号：

```text
没有 { }  -> 默认导入
带有 { }  -> 具名导入
```

但 `import type`、`import * as` 和 `import "./setup"` 还分别表达类型、命名空间和副作用语义，不能只靠花括号覆盖所有情况。

### 🔖 一条 import 的四步阅读路径

以后遇到陌生导入，固定问四个问题：

```text
第一步：来源是谁？
  第三方包、包内子入口、路径别名，还是相对路径？

第二步：导入什么？
  默认导出、具名导出、全部导出，还是只触发模块执行？

第三步：运行时存在吗？
  是值导入，还是只在 TypeScript 编译期存在的类型导入？

第四步：当前文件拿它做什么？
  渲染组件、调用函数、读取数据、约束类型，还是完成初始化？
```

这条路径把“识别语法”推进为“理解当前文件在系统中的角色”。

## 📄 从 App.tsx 看到的 import 现场

`App.tsx` 顶部的导入大致如下：

```tsx
import { useCallback, useEffect, useRef, useState } from "react";
import { ExternalLink, PanelLeftClose, PanelLeft, MoreHorizontal } from "lucide-react";
import { openUrl } from "@tauri-apps/plugin-opener";
import { invoke } from "@tauri-apps/api/core";

import { IconNav, type NavItem } from "@/components/IconNav";

import { modules } from "./plugins/registry";
import type { ModuleDescriptor } from "./plugins/types";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  TooltipProvider,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
```

先从右边看：

```tsx
from "react"
from "lucide-react"
from "@tauri-apps/api/core"
from "@/components/IconNav"
from "./plugins/registry"
```

`from` 后面描述“模块从哪里来”。大致分三类：

| 写法 | 来源 | App.tsx 例子 |
| --- | --- | --- |
| 包名 | `node_modules` 中的第三方包 | `"react"`, `"lucide-react"` |
| 包内路径 | 第三方包暴露的子入口 | `"@tauri-apps/api/core"` |
| 项目别名 | 项目配置的路径别名 | `"@/components/IconNav"` |
| 相对路径 | 当前文件附近的项目文件 | `"./plugins/registry"` |

这里最容易混的是：

```text
@tauri-apps/api/core
@/components/IconNav
```

它们都以 `@` 开头，但含义完全不同。

| 写法 | 本质 | 谁定义的 | 去哪里找 |
| --- | --- | --- | --- |
| `"@tauri-apps/api/core"` | 第三方 npm 包的子入口 | Tauri 包作者 | `node_modules` |
| `"@/components/IconNav"` | 当前项目自己的路径别名 | GitTributary 项目配置 | `src/components/IconNav` |

`@tauri-apps/api/core` 中，`@tauri-apps/api` 是一个完整的 npm 包名：

```text
@tauri-apps  组织/作用域
api          包名
core         包内子入口
```

所以它表示：

```text
从 node_modules 里的 @tauri-apps/api 这个第三方包中，
导入 core 入口暴露的能力。
```

`@/components/IconNav` 中，`@` 是 GitTributary 自己配置的路径别名：

```text
@ = src
```

所以它表示：

```text
从当前项目的 src/components/IconNav 中导入组件或类型。
```

最短判断法：

```text
@xxx/yyy  多半是 npm scoped package，也就是第三方包。
@/xxx     多半是项目 src 别名，也就是项目内部文件。
```

再看左边：

```tsx
import { useState } from "react";
```

`{ useState }` 描述“从这个模块里拿哪个具名导出”。拿进来以后，当前文件就可以直接写：

```tsx
const [collapsed, setCollapsed] = useState(true);
```

## 📄 具名导入

最常见的写法：

```tsx
import { useCallback, useEffect, useRef, useState } from "react";
```

含义：

```text
从 react 这个模块里，引入 useCallback、useEffect、useRef、useState 这几个具名导出。
```

这些名字必须和模块导出的名字对应。引入后，当前文件可以直接使用：

```tsx
useState(true)
useEffect(() => {}, [])
useRef<HTMLElement>(null)
```

`App.tsx` 里的图标也是同一类写法：

```tsx
import { ExternalLink, PanelLeftClose, PanelLeft, MoreHorizontal } from "lucide-react";
```

这里引入的是 React 图标组件，所以后面可以像 JSX 标签一样使用：

```tsx
<PanelLeft className="size-[18px]" />
<ExternalLink className="text-muted-foreground size-4 shrink-0" />
```

## 📄 类型导入

TypeScript 中有一种特殊写法：

```tsx
import type { ModuleDescriptor } from "./plugins/types";
```

`import type` 表示“只导入类型，不导入运行时代码”。也就是说，`ModuleDescriptor` 只用于 TypeScript 类型检查，编译成 JavaScript 后不会作为真实变量存在。

在 `App.tsx` 中，它用于给组件参数标注类型：

```tsx
function ExpandedButton({ module }: { module: ModuleDescriptor }) {
  const Icon = module.icon;
  // ...
}
```

这里 `ModuleDescriptor` 的作用是告诉 TypeScript：

```text
module 应该具有 id、name、icon、panel 等模块描述字段。
```

它不是运行时对象，所以适合用 `import type`。

## 📄 值导入和类型导入混写

`App.tsx` 里还有一行很典型：

```tsx
import { IconNav, type NavItem } from "@/components/IconNav";
```

这行同时做了两件事：

```text
IconNav  是值导入：运行时真的要渲染这个组件。
NavItem  是类型导入：只给 TypeScript 做类型检查。
```

后面可以看到两种用法：

```tsx
const navItems: NavItem[] = modules.map((module) => ({
  id: module.id,
  name: module.name,
  icon: module.icon,
  pinned: module.pinned,
  group: module.group === "system" ? "system" : "main",
}));
```

这里 `NavItem[]` 是类型，说明 `navItems` 是一个导航项数组。

```tsx
<IconNav
  items={navItems}
  activeId={activeId}
  onSelect={setActiveId}
/>
```

这里 `<IconNav />` 是组件值，运行时要真实渲染到页面上。

## 📄 默认导入与默认导出

默认导入的形态是：

```tsx
import React from "react";
```

它的意思是：

```text
从某个模块中拿默认导出的那个东西，并在当前文件里给它起一个名字。
```

`App.tsx` 当前没有使用默认导入。因为项目的 `tsconfig.json` 中配置了：

```json
"jsx": "react-jsx"
```

React 17 以后常见的 JSX 转换模式下，写 JSX 不一定需要手动导入整个 `React` 对象，所以文件里只导入实际使用的 Hooks：

```tsx
import { useCallback, useEffect, useRef, useState } from "react";
```

### 🔖 默认导出与默认导入是一对

文件想让其他文件使用自己定义的值，需要先导出。

```tsx
function App() {
  return <main>Git Tributary</main>;
}

export default App;
```

`export default App` 表示：

```text
把 App 这个值设为当前模块的默认导出。
```

其他文件就能用默认导入拿到它：

```tsx
import App from "./App";
```

两边的关系是：

```text
App.tsx                          main.tsx
export default App;   <------   import App from "./App";
```

每个模块最多只能有一个默认导出。默认导入时不写花括号，而且导入方可以自己命名：

```tsx
// 写法一
import App from "./App";

// 或者写法二：对同一个默认导出使用另一个局部名字
import RootApp from "./App";
```

上面是两种可选写法，不是建议同时导入两次。它们拿到的是同一个默认导出值，只是在当前文件中取的局部名字不同。

具名导出则可以有多个：

```tsx
export const MIN_WIDTH = 180;
export function parseState() {}
```

导入时要写花括号，名字默认也要对应：

```tsx
import { MIN_WIDTH, parseState } from "./layout";
```

| 导出方 | 导入方 | 数量 | 导入名字 |
| --- | --- | --- | --- |
| `export default App` | `import App from "./App"` | 每个模块最多一个 | 可自定义 |
| `export function foo()` | `import { foo } from "./x"` | 可以有多个 | 需与导出名对应，除非使用 `as` |

要注意，`export default App` 只是把函数值暴露给其他模块，它不会自动调用 `App()`。在 GitTributary 中，是 `main.tsx` 导入 `App`，然后通过 `<App />` 把它交给 React 渲染。

### 🔖 为什么需要默认导出

默认导出的主要价值不只是让导入语法更简洁，而是表达模块的 API 设计意图：

```text
这个模块有一个主要产物，其他导出只是辅助能力。
```

例如，一个组件文件通常以组件本身作为主要产物：

```tsx
export const DEFAULT_TITLE = "Git Tributary";

function App() {
  return <main>{DEFAULT_TITLE}</main>;
}

export default App;
```

这里 `App` 是模块的主角，`DEFAULT_TITLE` 是附加能力。每个模块最多只能有一个默认导出，这条限制也使模块只能声明一个“主要入口”。

默认导入允许使用方根据当前上下文选择局部名称：

```tsx
import App from "./App";
import RootApp from "./App";
```

这在包装第三方库、处理文件名冲突或为同一概念选择更贴近当前上下文的名称时很方便。不过它也意味着同一个导出可能在不同文件中出现不同名字，使全局搜索和批量重构不如具名导出直接。

### 🔖 default 本质上是一个特殊导出名

从模块系统的角度看，默认导出可以理解为模块导出表中名为 `default` 的特殊槽位。因此下面两种写法表达的接口很接近：

```tsx
export default App;
```

```tsx
export { App as default };
```

默认导入也可以改写成具名导入形式：

```tsx
import App from "./App";

// 等价的低频写法
import { default as App } from "./App";
```

使用命名空间导入时，默认导出会出现在模块对象的 `default` 属性上：

```tsx
import * as appModule from "./App";

const App = appModule.default;
```

这解释了为什么默认导出能够被重命名、重导出以及和具名导出同时存在。

### 🔖 默认导出的重导出

中间模块可以把另一个模块的默认导出继续暴露出去：

```tsx
export { default } from "./App";
```

也可以把默认导出转换为一个具名导出：

```tsx
export { default as App } from "./App";
```

这类写法常见于统一出口文件：

```text
components/
  App.tsx
  index.ts
```

```tsx
// components/index.ts
export { default as App } from "./App";
```

调用方随后可以通过具名导入使用它：

```tsx
import { App } from "./components";
```

### 🔖 两种默认导出写法的绑定差异

ES Module 的具名导出通常是实时绑定：导出变量发生变化后，导入方读取到的也是新值。但下面两种默认导出写法存在细微差别。

直接导出表达式的结果：

```ts
let count = 1;
export default count;

count = 2;
```

`export default count` 会计算当时的表达式结果，并用它初始化默认导出。后续修改原变量 `count`，不会让这个默认导出自动变成 `2`。

把变量绑定导出为 `default`：

```ts
let count = 1;
export { count as default };

count = 2;
```

这里导出的是 `count` 的实时绑定，导入方之后读取到的是更新后的值。日常组件代码很少依赖这个差异，但理解它有助于区分“导出表达式的结果”和“导出变量绑定”。

### 🔖 默认导出并不天然影响 tree-shaking

默认导出和具名导出都属于静态的 ES Module 语法，构建工具都可以分析。不能简单地认为“默认导出无法 tree-shaking”。

真正不利于按成员裁剪的是把许多独立能力先包装进一个对象，再整体默认导出：

```ts
export default {
  formatDate,
  parseDate,
  isValidDate,
};
```

调用方拿到的是一个整体对象，构建工具不一定能可靠证明其中哪些属性永远不会被访问。对于工具函数集合，更适合直接使用具名导出：

```ts
export function formatDate() {}
export function parseDate() {}
export function isValidDate() {}
```

### 🔖 如何选择默认导出和具名导出

| 场景 | 更适合的方式 | 原因 |
| --- | --- | --- |
| 一个文件主要表示一个组件、类、配置或路由器 | 默认导出 | 能明确表达模块唯一的主要产物 |
| 一个文件提供多个并列工具函数或常量 | 具名导出 | 名字统一，自动补全、搜索和重构更直接 |
| 希望项目中所有调用方使用同一个名称 | 具名导出 | 导入名默认必须与导出名一致 |
| 需要根据使用场景灵活设置局部名称 | 默认导出 | 导入方可以自行命名 |

默认导出不是必须设置的功能，也没有比具名导出更强的运行时能力。是否使用它，核心取决于模块是否真的存在一个明确的“主角”。

## 📄 路径别名导入

`App.tsx` 中有很多 `@/` 开头的路径：

```tsx
import { IconNav, type NavItem } from "@/components/IconNav";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
```

在这个项目里，`@` 被配置成指向 `src` 目录。

`vite.config.ts` 中：

```ts
resolve: {
  alias: {
    "@": path.resolve(__dirname, "./src"),
  },
},
```

`tsconfig.json` 中：

```json
"paths": {
  "@/*": ["./src/*"]
}
```

所以：

```tsx
@/components/IconNav
```

等价于：

```text
src/components/IconNav
```

使用路径别名的好处是，文件移动以后不用写很长的相对路径：

```tsx
../../../components/IconNav
```

而是稳定地写：

```tsx
@/components/IconNav
```

注意，`@/` 是路径别名的明显信号。它和 `@tauri-apps/api/core` 这种第三方包名不是一类东西。

## 📄 相对路径导入

相对路径以 `./` 或 `../` 开头：

```tsx
import { modules } from "./plugins/registry";
import type { ModuleDescriptor } from "./plugins/types";
```

它们从当前文件附近寻找模块。

`App.tsx` 位于：

```text
src/App.tsx
```

所以：

```text
./plugins/registry
```

指向：

```text
src/plugins/registry.tsx 或 src/plugins/registry.ts
```

读这种导入时，可以把 `./` 理解成：

```text
从当前文件所在目录出发。
```

## 📄 多行导入

当导入内容较长时，可以拆成多行：

```tsx
import {
  TooltipProvider,
} from "@/components/ui/tooltip";
```

它和下面这种写法含义一样：

```tsx
import { TooltipProvider } from "@/components/ui/tooltip";
```

只是格式上更容易追加新的导入项。

## 📄 import 语法背后的三个问题

一条 `import` 同时涉及三个层次。把它们分开，很多疑问就不会混在一起。

| 层次 | 回答的问题 | 典型线索 |
| --- | --- | --- |
| 模块解析 | 字符串最终指向哪个文件或包入口？ | `./`、`../`、`@/`、包名、`package.json` |
| 模块接口 | 目标模块对外导出了哪些名字？ | `default`、具名导出、`export type` |
| 模块执行 | 目标模块何时求值，顶层代码执行几次？ | 静态导入、动态导入、循环依赖、顶层 `await` |

例如：

```tsx
import { invoke } from "@tauri-apps/api/core";
```

可以拆成：

```text
模块解析：找到 @tauri-apps/api 包暴露的 core 子入口。
模块接口：确认这个入口存在名为 invoke 的导出。
模块执行：模块系统先连接依赖，再在求值阶段提供可使用的绑定。
```

本文主要处理前两个问题。第三个问题属于模块加载与执行机制，继续阅读：[ES Module 的加载与执行机制](./ES%20Module%20的加载与执行机制.md)。

### 🔖 import 不是复制值的语法糖

静态 ESM 导入建立的是模块绑定，不是把导出方的源码粘贴进当前文件，也不总是复制一份独立值。

```ts
// counter.ts
export let count = 0;

export function increase() {
  count += 1;
}
```

```ts
// main.ts
import { count, increase } from "./counter";

increase();
console.log(count); // 1
```

`count` 是只读的导入绑定：当前文件不能写 `count = 2`，但可以观察导出模块对原绑定的更新。这就是 ES Module 的实时绑定。

## 📄 用 import 区快速判断文件职责

读一个前端文件时，不必立刻进入组件实现。先扫 import 区，并按“来源、形态、性质、用途”分类：

| 观察维度 | App.tsx 中的线索 | 能得到的判断 |
| --- | --- | --- |
| 框架能力 | `useState`, `useEffect`, `useRef`, `useCallback` | 文件包含状态、副作用、引用和回调逻辑 |
| 第三方能力 | `lucide-react`, Tauri API | 文件使用图标，并与桌面端能力交互 |
| 项目内组件 | `IconNav`, `ScrollArea`, `Separator` | 文件主要负责组合现有 UI |
| 项目内数据 | `modules` | 页面结构由模块注册表驱动 |
| 类型约束 | `NavItem`, `ModuleDescriptor` | 导航项和模块描述存在明确数据契约 |
| 工具函数 | `cn` | JSX 样式类名需要组合处理 |

由此可以先形成假设：

```text
App.tsx 是应用外壳，而不是单一业务组件。
它负责组合导航和模块面板，并连接 Tauri 桌面端能力。
```

然后进入正文代码验证这个假设。完整阅读路径是：

```text
扫 import 区建立文件职责假设
        ↓
找组件入口、公开函数或顶层初始化
        ↓
沿关键导入追到项目内模块
        ↓
回到当前文件验证数据流和调用关系
```

这比逐行阅读更快，因为先建立了“这个文件为什么存在”的方向感。

## 📄 后续思考路径

掌握语法后，可以沿下面几条路线继续追问。它们分别把 `import` 从语法连接到语言机制和工程设计。

### 🔖 路线一：从依赖清单走向模块图

```text
单条 import
  -> 一个文件的直接依赖
  -> 多个文件构成模块图
  -> 入口模块如何驱动整个应用加载
```

可以继续问：为什么静态 `import` 必须位于顶层？构建工具如何在运行前发现完整依赖图？动态 `import()` 又为什么能形成独立代码块？

### 🔖 路线二：从语法选择走向 API 设计

```text
默认导出：强调一个主要产物
具名导出：强调多个稳定、并列的公开能力
类型导出：声明只存在于编译期的数据契约
```

可以继续问：一个模块应该暴露多少能力？什么时候说明模块职责过重？统一出口文件 `index.ts` 带来了更清晰的 API，还是隐藏了真实依赖来源？

### 🔖 路线三：从静态语法走向构建优化

```text
静态 import / export
  -> 构建期分析
  -> tree-shaking
  -> 代码分割
  -> 按需加载
```

可以继续问：tree-shaking 删除的是“没有导入的名字”，还是“没有副作用的代码”？为什么模块顶层副作用会限制裁剪？`package.json` 中的 `sideEffects` 又在向构建工具承诺什么？

### 🔖 路线四：从实时绑定走向循环依赖

实时绑定使循环依赖在语义上成为可能，但不保证任意循环都能正常运行。可以继续追问：

```text
A 导入 B，B 又导入 A 时，绑定何时建立？
为什么函数声明有时可用，尚未初始化的 const 却会触发 TDZ？
如何通过拆分共享模块解除循环依赖？
```

### 🔖 路线五：从 ESM 走向生态兼容

真实项目还会遇到 ES Module、CommonJS 和构建工具之间的互操作：

```text
ESM：import / export
CommonJS：require / module.exports
```

可以继续问：为什么某些 CommonJS 包能默认导入，某些却需要具名导入或 `.default`？`esModuleInterop`、运行环境和构建工具分别改变了哪一层行为？这属于兼容策略，不应和 ESM 原生的默认导出语义混为一谈。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-07-13：按“快速回顾、理解路径、概念边界、后续思考”重构笔记入口，并补充命名空间导入、副作用导入、模块职责判断及进阶问题地图。
- 2026-07-13：补充默认导出的设计语义、`default` 导出槽位、重导出、实时绑定差异及工程选型。
- 2026-07-12：补充 `export default` 与默认导入的配对关系，并区分默认导出和具名导出。
- 2026-07-09：基于 GitTributary `src/App.tsx` 的 import 区创建笔记。

## 🛠️ 实践经历

来源案例：

```text
/Users/mi/rust_code/GitTributary/src/App.tsx
```

实践目标：

```text
通过阅读 App.tsx 顶部 import 区，先判断这个文件依赖哪些框架能力、第三方库、本地组件、类型和工具函数。
```

## ⚙️ prompt

```markdown
帮我在语法基础中，添加关于 import 模块的语法笔记
import 阐述 APP.tsx 的语法细节
```

```markdown
帮我优化这篇笔记。笔记需要帮助我快速回顾概念、恢复理解和思考路径，并拓展后续可以继续追问的问题。
```

## 调研

- `src/App.tsx` 使用了具名导入、类型导入、值与类型混合导入、路径别名导入、相对路径导入。
- `vite.config.ts` 将 `@` 映射到 `./src`。
- `tsconfig.json` 将 `@/*` 映射到 `./src/*`，并启用 `"jsx": "react-jsx"`。
