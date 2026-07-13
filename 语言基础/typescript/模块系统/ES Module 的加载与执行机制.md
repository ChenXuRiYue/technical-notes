# 📌 ES Module 的加载与执行机制

ES Module（ESM）是 JavaScript 的标准模块系统。

理解模块执行顺序时，不能只按单个文件从上到下阅读。运行环境会先处理模块之间的依赖，再执行模块顶层代码。

## 📄 核心结论

ES Module 的处理过程可以分为三个阶段：

| 阶段 | 作用 |
| --- | --- |
| 解析 | 读取静态 `import` 和 `export`，建立模块依赖图 |
| 实例化与链接 | 创建模块绑定，将导入连接到对应的导出 |
| 求值 | 按依赖关系执行模块顶层代码 |

需要记住：

1. 静态 `import` 不是执行到该行时才加载。
2. 依赖模块通常先于当前模块求值。
3. 模块顶层语句在模块求值时执行。
4. 函数体只有在函数被调用时才执行。
5. 同一个模块实例通常只求值一次。
6. 导入的是只读的实时绑定，不是独立副本。
7. `interface`、`type` 和 `import type` 通常不会进入运行时。

语法形式参见：[import / export 模块语法](./import%20模块语法.md)。

## 📄 模块的处理过程

### 🔖 解析

运行环境从入口模块开始，读取静态 `import`，递归查找依赖：

```text
main.ts
  ├── settings.ts
  └── formatter.ts
        └── settings.ts
```

此时建立的是模块图，还没有执行普通的业务代码。

模块路径的具体解析方式由运行环境决定。例如：

- 浏览器通常按 URL 查找模块。
- Node.js 根据文件路径、包名和 `package.json` 查找模块。
- Vite 可以通过 `alias` 处理路径别名。

### 🔖 实例化与链接

模块系统为模块级声明创建绑定，并将导入绑定连接到导出绑定。

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

`count` 是实时绑定。导出模块修改 `count` 后，导入方可以读到新值。

导入方不能直接修改这个绑定：

```ts
count = 2; // 报错
```

### 🔖 求值

链接完成后，运行环境开始执行模块顶层代码。

一般情况下：

1. 先求值依赖模块。
2. 再求值当前模块。
3. 当前模块的顶层语句按顺序执行。

循环依赖和顶层 `await` 会使执行顺序更复杂，不能只套用简单的先后关系。

### 🔖 模块通常只求值一次

```ts
// shared.ts
console.log("shared 执行");

export const cache = new Map();
```

多个文件导入同一个 `shared.ts` 时，通常共享同一个模块实例：

- 顶层日志只打印一次。
- `cache` 是同一个对象。

“同一个模块”取决于运行环境如何识别模块。不同 URL、查询参数、重复安装的依赖或测试隔离可能产生不同实例。开发环境中的 HMR 也可能重新执行模块。

## 📄 不同代码的执行时机

| 代码 | 运行时行为 |
| --- | --- |
| `interface`、`type` | 编译后通常被删除 |
| `function foo() {}` | 实例化时完成绑定初始化，函数体在调用时执行 |
| `var value` | 实例化时初始化为 `undefined` |
| `let`、`const`、`class` | 绑定已创建，但声明执行前不能读取 |
| 模块顶层表达式 | 求值执行到该行时运行 |
| 函数内部语句 | 函数被调用时运行 |

关键区别：

```text
建立绑定、完成初始化、执行函数体是三个不同阶段。
```

### 🔖 TypeScript 类型

```ts
interface User {
  id: string;
}

type Status = "idle" | "ready";
```

这些内容用于编译期类型检查，通常不会出现在生成的 JavaScript 中，因此不参与运行时执行顺序。

### 🔖 函数声明

```ts
run();

function run() {
  console.log("run");
}
```

函数声明在模块实例化时已经完成初始化，所以顶层代码执行到 `run()` 时可以调用它。函数体仍然只在调用时执行。

### 🔖 `let`、`const` 和暂时性死区

```ts
console.log(message); // ReferenceError

const message = "hello";
```

`message` 的绑定已经存在，但在声明完成初始化前不能读取。这段区域称为暂时性死区（TDZ）。

### 🔖 顶层表达式

```ts
const items = source.map(transform);
```

模块求值执行到这一行时，会立即调用 `map` 和 `transform`。它不会等到其他文件使用 `items` 时再计算。

### 🔖 函数内表达式

```ts
export function createItems(source: number[]) {
  return source.map(transform);
}
```

`map` 会在每次调用 `createItems` 时执行。

模块顶层适合模块级共享数据。依赖调用参数或需要重复计算的数据，更适合放在函数内。

## 📄 执行顺序示例

`settings.ts`：

```ts
console.log("1. settings 开始");

export let count = 0;

export function increase() {
  count += 1;
}

console.log("2. settings 结束");
```

`main.ts`：

```ts
import { count, increase } from "./settings";

interface Result {
  value: number;
}

console.log("3. main 开始");

function read(): Result {
  return { value: count };
}

increase();

console.log("4. count =", count);
console.log("5. result =", read());
console.log("6. main 结束");
```

执行结果：

```text
1. settings 开始
2. settings 结束
3. main 开始
4. count = 1
5. result = { value: 1 }
6. main 结束
```

这个例子说明：

- `settings.ts` 先于 `main.ts` 求值。
- `Result` 不参与运行时执行。
- `read` 的绑定提前建立，函数体在调用时执行。
- `count` 是实时绑定。

## 📄 特殊情况

### 🔖 动态导入

```ts
const feature = await import("./feature");
```

`import()` 是运行时表达式。代码执行到这里时，才异步加载并求值目标模块。

它可以用于：

- 条件加载
- 路由拆分
- 较大功能的延迟加载

### 🔖 顶层 await

```ts
const config = await loadConfig();

export { config };
```

顶层 `await` 会使模块求值变成异步过程。依赖这个模块的其他模块，需要等待它完成求值。

顶层 `await` 会影响启动时间，也会增加循环依赖的复杂度。

### 🔖 循环依赖

```ts
// a.ts
import { b } from "./b";

export const a = "A";
console.log(b);
```

```ts
// b.ts
import { a } from "./a";

export const b = `B uses ${a}`;
```

ESM 可以完成两个模块之间的链接，但求值时仍可能在 `a` 初始化前读取它，从而触发 `ReferenceError`。

常见处理方式：

- 将共享内容提取到第三个模块。
- 避免在模块顶层读取对方尚未初始化的值。
- 将读取动作放到函数中。
- 重新划分模块职责，消除双向依赖。

### 🔖 顶层副作用

```ts
registerPlugin();
window.addEventListener("resize", handleResize);
startTimer();
```

这些语句在模块求值时立即执行，不需要导入方显式调用。

顶层副作用会影响：

- 测试隔离
- 加载性能
- tree-shaking
- 执行顺序的可预测性

通用模块通常更适合导出函数，由调用方决定何时启动行为。

### 🔖 类型导入

```ts
import type { User } from "./types";
```

`import type` 只用于类型检查，通常不会形成运行时依赖。具体输出仍受 TypeScript 配置和构建工具影响。

### 🔖 组件执行和模块求值

```ts
const staticOptions = rawOptions.map(normalize);

function View(props: { options: Option[] }) {
  const visibleOptions = props.options.filter(isVisible);
  return renderOptions(visibleOptions);
}
```

`staticOptions` 在模块求值时计算一次。

`visibleOptions` 在每次调用 `View` 时重新计算。组件重新渲染不等于模块重新求值。

## 📄 排查顺序

遇到执行顺序问题时，按以下顺序检查：

1. 确认相关代码编译后是否仍然存在。
2. 区分模块顶层代码和函数内部代码。
3. 画出最小模块依赖图。
4. 检查 `let`、`const`、`class` 是否在初始化前被读取。
5. 检查是否存在循环依赖。
6. 检查是否使用动态导入或顶层 `await`。
7. 检查开发服务器 HMR、测试隔离或模块路径差异。

| 现象 | 常见原因 |
| --- | --- |
| 依赖模块日志先出现 | 依赖模块先求值 |
| 多处导入但日志只出现一次 | 共享同一个模块实例 |
| 导入值随后发生变化 | 实时绑定 |
| 出现初始化前访问错误 | TDZ 或循环依赖 |
| 未调用函数却发生注册或监听 | 顶层副作用 |
| 组件重复执行，模块日志没有重复 | 组件生命周期和模块生命周期不同 |

## 📄 后续理解

- 模块路径解析：浏览器 URL、Node.js 包解析、`package.json exports`、Vite alias。
- 构建优化：静态模块图、tree-shaking、`sideEffects`。
- 循环依赖：实时绑定、TDZ、模块职责拆分。
- 异步模块：动态导入、代码分割、顶层 `await`。
- 模块状态：模块级共享对象与进程、Worker、SSR 请求、测试隔离之间的关系。

## 📄 实践回链

GitTributary 中可以观察：

```text
src/App.tsx
开源项目/GitTributary/技术经验/App.tsx 前端应用外壳解读.md
```

`navItems` 展示模块顶层初始化，`parseNavMoreUiState` 展示函数声明与调用时机，`NavMoreUiState` 展示 TypeScript 类型擦除。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-07-13：统一叙述风格，减少重复提示和层级，保留核心原理、示例与边界。
- 2026-07-12：从 GitTributary 的代码阅读经验中提取通用的 ES Module 加载与执行知识。

## 🛠️ 实践经历

## ⚙️ prompt

```markdown
优化 ES Module 的加载与执行机制笔记。要求朴素、简洁、清晰，叙述风格统一。
```

## 调研
