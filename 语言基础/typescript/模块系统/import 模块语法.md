# 📌 import 模块语法

`import` 的核心作用是把其他模块导出的东西引入当前文件作用域。读 TypeScript / React 文件时，文件顶部的一组 `import` 就像一张依赖清单：它告诉我们当前文件要使用哪些框架能力、第三方库、项目内组件、类型定义和工具函数。

在 GitTributary 的 `src/App.tsx` 中，`import` 区基本回答了一个问题：

```text
App.tsx 这个前端应用外壳，依赖哪些外部能力和本地模块？
```

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

## 📄 默认导入

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

## 📄 读 import 区的方法

读一个前端文件时，不要急着从第一行函数开始啃。可以先扫 import 区，问四个问题：

```text
1. 它用了哪些框架能力？
2. 它用了哪些第三方库？
3. 它依赖了哪些项目内组件？
4. 它只用了哪些类型？
```

以 `App.tsx` 为例：

| 问题 | 线索 |
| --- | --- |
| 框架能力 | `useState`, `useEffect`, `useRef`, `useCallback` |
| 第三方库 | `lucide-react`, `@tauri-apps/api/core`, `@tauri-apps/plugin-opener` |
| 项目内组件 | `IconNav`, `ScrollArea`, `Separator`, `TooltipProvider` |
| 项目内数据 | `modules` |
| 项目内类型 | `NavItem`, `ModuleDescriptor` |
| 项目内工具函数 | `cn` |

这会快速告诉我们：

```text
App.tsx 是一个 React 组件文件；
它使用 Tauri 调后端能力；
它复用项目内 UI 组件；
它从 modules 注册表中读取一级模块；
它用类型约束导航和模块描述数据。
```

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

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

## 调研

- `src/App.tsx` 使用了具名导入、类型导入、值与类型混合导入、路径别名导入、相对路径导入。
- `vite.config.ts` 将 `@` 映射到 `./src`。
- `tsconfig.json` 将 `@/*` 映射到 `./src/*`，并启用 `"jsx": "react-jsx"`。
