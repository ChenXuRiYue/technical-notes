# 📌 TypeScript 类型安全体系

TypeScript 的类型安全不是“给变量补几个类型”的零散语法，而是一套围绕 JavaScript 建立的静态分析体系：先描述程序中允许出现的值，再检查值如何创建、组合、传递和收窄，最后在外部数据进入程序时建立运行时校验边界。

它的核心目标不是证明程序绝对正确，而是尽量在运行前发现不合理的数据形状、状态流转和 API 调用。

## 📄 类型安全体系的总地图

TypeScript 类型安全可以分为七层：

```text
1. 类型建模
   primitive / literal / object / interface / type

2. 类型组合
   union / intersection / optional / nullable

3. 类型推导与控制流分析
   inference / narrowing / type guard

4. 类型参数化与类型变换
   generic / keyof / indexed access / mapped type / utility type

5. 程序边界
   unknown / runtime validation / type predicate

6. 编译器约束
   strict / null checks / unused checks / switch checks

7. 逃生口与局限
   any / assertion / non-null assertion / type erasure
```

可以用一条数据流理解它们的关系：

```text
外部世界中的未知数据
  -> unknown
  -> 运行时校验与类型收窄
  -> 明确的业务类型
  -> 泛型函数和组件安全传递
  -> 联合类型约束状态变化
  -> 编译器持续检查
```

## 📄 TypeScript 提供的是渐进式静态类型

### 🔖 静态类型

“静态”表示类型检查主要发生在代码运行之前：

```ts
const open: boolean = "yes";
// 编译期错误：string 不能赋给 boolean
```

TypeScript 编译后仍然是 JavaScript，类型声明通常不会出现在最终运行代码中。

### 🔖 渐进式类型

TypeScript 允许开发者逐步添加类型，不要求整个 JavaScript 项目一次性完成严格建模。没有明确类型时，编译器会尝试推导；使用 `any` 时，还可以暂时退出类型检查。

因此 TypeScript 的安全程度取决于：

```text
类型建模质量
+ 编译器严格程度
+ 是否控制 any 和类型断言
+ 外部数据是否经过运行时校验
```

### 🔖 结构类型系统

TypeScript 主要采用结构类型：一个值能否赋给某个类型，关键看它是否具有所需结构，而不是它是否显式声明“实现了这个类型”。

```ts
interface NavItem {
  id: string;
  name: string;
}

const module = {
  id: "git",
  name: "Git",
  description: "Git tools",
};

const item: NavItem = module;
```

`module` 即使没有写 `implements NavItem`，只要具有 `id` 和 `name`，就可以赋给 `NavItem`。

这种设计非常适合 JavaScript 的对象组合方式，但也意味着 TypeScript 关注的是“结构兼容”，不是 Java、C# 那种以类型名称为核心的名义类型。

## 📄 类型是允许值的集合

理解 TypeScript 的一个稳定视角是：类型描述某个位置允许出现哪些值。

```ts
boolean                 // true | false
"main" | "system"     // 两个字符串字面量
string | null           // 任意字符串或者 null
never                   // 没有任何合法值
unknown                 // 可能是任意值，但使用前必须检查
```

类型越具体，允许值的集合通常越小；检查条件可以把较大的集合收窄成较小的集合。

```ts
function print(value: string | null) {
  if (value === null) return;
  value.toUpperCase();
}
```

进入函数时，`value` 是 `string | null`；通过 `value === null` 检查后，剩余分支中的类型被收窄为 `string`。

## 📄 基础类型建模

### 🔖 原始类型与字面量类型

```ts
let name: string;
let count: number;
let open: boolean;

type ModuleGroup = "main" | "system";
type Version = 1 | 2;
```

`string` 表示所有字符串，`"main"` 只表示一个具体字符串。字面量类型可以把非法状态排除在模型之外。

GitTributary 中：

```ts
export type SitePhase =
  | "idle"
  | "scanning"
  | "ready"
  | "building"
  | "publishing"
  | "succeeded"
  | "failed";
```

相比普通 `string`，它能阻止拼写错误和未定义状态：

```ts
const phase: SitePhase = "buildng";
// 错误：buildng 不属于 SitePhase
```

### 🔖 对象类型、`interface` 与 `type`

```ts
interface ModuleDescriptor {
  id: string;
  name: string;
  group?: ModuleGroup;
  fullHeight?: boolean;
}
```

`interface` 适合描述可扩展的对象结构；`type` 可以为任意类型表达式命名，除了对象，还能表示联合类型、元组和条件类型。

```ts
type ModuleGroup = "main" | "system";

type Point = {
  x: number;
  y: number;
};
```

对象建模专题参见：[interface 与对象类型安全](./interface%20与对象类型安全.md)。

### 🔖 可选、只读和索引结构

```ts
interface Config {
  readonly id: string;
  description?: string;
}
```

- `description?: string`：字段可能不存在，读取结果通常是 `string | undefined`。
- `readonly id: string`：禁止通过该类型视角重新赋值，但不等同于运行时不可变。

动态键值对象可以使用：

```ts
const drafts: Record<string, RemoteDraft> = {};
```

它表示键是字符串、值是 `RemoteDraft` 的对象。

### 🔖 数组、元组和函数类型

```ts
const files: string[] = [];
const point: [number, number] = [10, 20];
const select: (id: string) => void = (id) => console.log(id);
```

- 数组描述同类元素序列。
- 元组描述固定位置和固定长度的元素类型。
- 函数类型同时约束参数和返回值，是保护模块接口的重要位置。

## 📄 联合类型把状态建模成有限选择

### 🔖 普通联合类型

```ts
let error: string | null = null;
```

这表示“错误信息存在”或“当前没有错误”。启用严格空值检查后，使用字符串方法前必须排除 `null`。

### 🔖 可辨识联合

GitTributary 中：

```ts
type FlowTreeSelection =
  | { type: "flow"; id: string }
  | { type: "folder"; path: string };
```

`type` 是判别字段。检查它以后，TypeScript 能确定当前对象的精确分支：

```ts
function label(selection: FlowTreeSelection): string {
  if (selection.type === "flow") {
    return selection.id;
  }
  return selection.path;
}
```

这种模型比下面的“多个可选字段”更安全：

```ts
interface UnsafeSelection {
  type: "flow" | "folder";
  id?: string;
  path?: string;
}
```

后者允许出现 `type: "flow"` 却没有 `id` 的对象。可辨识联合能让每个状态携带自己必需的数据。

### 🔖 交叉类型

交叉类型表示一个值必须同时满足多个类型：

```ts
type Timestamped = { updatedAt: number };
type Versioned = { version: 1 };
type StoredState = Timestamped & Versioned;
```

它适合组合相互独立的能力，但不应为了复用而制造难以理解的复杂交叉结构。

## 📄 类型推导与上下文类型

TypeScript 不要求每个位置都手写类型：

```ts
const open = true;            // 推导为 boolean
const names = ["git", "site"]; // 推导为 string[]
```

React 中的泛型参数会影响后续推导：

```ts
const [error, setError] = useState<string | null>(null);
```

如果只写 `useState(null)`，初始值提供的信息太窄。显式传入 `string | null`，才能表达状态未来可以保存字符串。

类型注解的实用原则：

```text
局部变量：优先推导
函数参数：通常明确声明
公共函数返回值：重要边界建议声明
空数组、null 初始状态：常需要泛型参数
配置对象：适合 satisfies
```

## 📄 类型收窄与控制流分析

TypeScript 会根据程序分支追踪变量可能的类型。

### 🔖 内置收窄手段

```ts
typeof value === "string"
value === null
Array.isArray(value)
"name" in value
value instanceof Error
```

例如：

```ts
function normalize(value: string | null | undefined): string {
  if (value == null) return "";
  return value.trim();
}
```

`value == null` 在这里同时排除 `null` 和 `undefined`。

### 🔖 自定义类型守卫

GitTributary 中：

```ts
export function isCaptureViewMode(value: unknown): value is CaptureViewMode {
  return value === "tree" || value === "list";
}
```

返回类型 `value is CaptureViewMode` 是类型谓词。函数返回 `true` 后，调用处会把 `value` 收窄为 `CaptureViewMode`。

类型谓词是一份开发者承诺：函数实现必须真的完成对应检查，否则编译器会被错误信息误导。

### 🔖 `never` 与穷尽检查

`never` 表示不可能出现的值，可以用来检查联合类型是否处理完整：

```ts
function assertNever(value: never): never {
  throw new Error(`Unexpected value: ${String(value)}`);
}

function selectionLabel(selection: FlowTreeSelection): string {
  switch (selection.type) {
    case "flow":
      return selection.id;
    case "folder":
      return selection.path;
    default:
      return assertNever(selection);
  }
}
```

以后新增联合分支却忘记修改 `switch` 时，编译器会在 `assertNever` 处提示错误。

## 📄 泛型让类型关系可以复用

泛型不是“任意类型”，而是把某个具体类型作为参数传入，同时保留输入与输出之间的关系。

```ts
function first<T>(items: T[]): T | undefined {
  return items[0];
}

const name = first(["git", "site"]);
// string | undefined
```

GitTributary 常见的泛型调用：

```ts
useState<RepoOverview | null>(null);
invoke<FileStatus[]>("get_status");
useRef<HTMLInputElement>(null);
```

这里的 `<T>` 告诉通用 API 当前场景使用的具体类型。

需要注意：

```ts
invoke<FileStatus[]>("get_status")
```

只是在前端声明“期望返回 `FileStatus[]`”，不会自动验证 Rust 返回的真实数据。跨进程边界仍应根据风险决定是否加入运行时校验。

### 🔖 泛型约束

```ts
function readId<T extends { id: string }>(value: T): string {
  return value.id;
}
```

`extends` 表示传入的类型至少必须包含 `id: string`，同时保留它的其他字段。

## 📄 从已有类型派生新类型

重复手写相似结构容易让类型逐渐不一致。TypeScript 提供类型运算，让新类型从旧类型派生。

### 🔖 `keyof` 与索引访问类型

```ts
type ModuleKey = keyof ModuleDescriptor;
// "id" | "name" | "description" | ...

type ModuleName = ModuleDescriptor["name"];
// string
```

`keyof` 取得对象类型的键集合；`T[K]` 取得某个字段对应的类型。

### 🔖 常用工具类型

```ts
Partial<T>       // 所有字段变为可选
Required<T>      // 所有字段变为必填
Readonly<T>      // 所有字段变为只读
Pick<T, K>       // 只选指定字段
Omit<T, K>       // 排除指定字段
Record<K, V>     // 构造键值对象
ReturnType<F>    // 提取函数返回类型
Parameters<F>    // 提取函数参数元组
```

GitTributary 示例：

```ts
function remoteKey(
  remote: Pick<RemoteInfo, "name" | "repo_path">,
): string {
  return `${remote.repo_path ?? "app"}:${remote.name}`;
}
```

函数只依赖 `RemoteInfo` 的两个字段，`Pick` 把依赖范围直接写进类型。

更新草稿时：

```ts
function updateRemoteDraft(
  key: string,
  patch: Partial<RemoteDraft>,
) {
  // patch 只需要携带本次要修改的字段
}
```

工具类型的价值不是少写几行，而是让派生类型随着源类型一起变化。

## 📄 `satisfies`、类型注解与 `as const`

三者作用不同：

```ts
const a: Config = value;
// 检查后，变量按 Config 类型使用

const b = value satisfies Config;
// 检查是否满足 Config，尽量保留 value 的精确推导

const c = { group: "main" } as const;
// 尽量把属性收窄为字面量并变为 readonly
```

`satisfies` 适合模块注册表、路由表、配置对象等“既要校验完整结构，又希望保留具体字段信息”的场景。

`as const` 是常量断言，不是普通的目标类型断言。它常用于从常量数据反推出字面量联合类型。

## 📄 `unknown`、`any` 与安全边界

### 🔖 `unknown` 是安全的未知值

```ts
function parse(value: unknown) {
  if (typeof value === "string") {
    return value.trim();
  }
  return null;
}
```

`unknown` 可以接收任何值，但不能在未检查前读取属性或调用方法。它迫使代码建立证据。

### 🔖 `any` 会传播不安全

```ts
function unsafe(value: any) {
  value.notExisting.deep.call();
}
```

`any` 基本关闭当前位置的类型检查，而且会把不确定性传播到后续表达式。迁移旧代码时可以临时使用，但业务边界应尽快收敛到明确类型或 `unknown`。

### 🔖 类型断言是承诺，不是证明

```ts
const state = value as NavMoreUiState;
```

它不会产生运行时检查。断言更适合“编译器缺少信息，但开发者已经通过其他方式得到保证”的场景，不应当用来跳过尚未完成的验证。

## 📄 运行时校验补足静态类型

浏览器存储、Tauri `invoke`、JSON、网络响应和用户输入都属于类型系统之外的数据源。

推荐边界模式：

```ts
function parseState(value: unknown): NavMoreUiState | null {
  if (!value || typeof value !== "object") return null;
  const state = value as Partial<NavMoreUiState>;
  if (state.version !== 1) return null;
  if (typeof state.open !== "boolean") return null;
  if (typeof state.updatedAt !== "number") return null;
  return {
    version: 1,
    open: state.open,
    updatedAt: state.updatedAt,
  };
}
```

复杂数据结构可以考虑使用成熟的 schema 校验库，让运行时 schema 与 TypeScript 类型保持关联。但是否引入依赖，应根据数据复杂度、边界风险和项目现有技术栈决定。

## 📄 编译器配置决定安全基线

GitTributary 的 `tsconfig.json` 启用了：

```json
{
  "strict": true,
  "noUnusedLocals": true,
  "noUnusedParameters": true,
  "noFallthroughCasesInSwitch": true,
  "isolatedModules": true,
  "noEmit": true
}
```

其中：

- `strict`：开启一组严格类型检查，是类型安全的核心总开关。
- `noUnusedLocals`：未使用的局部声明报错，减少失效代码。
- `noUnusedParameters`：未使用参数报错，帮助发现接口与实现偏差。
- `noFallthroughCasesInSwitch`：防止 `switch` 分支意外贯穿。
- `isolatedModules`：确保每个文件能被独立转换，适配 Vite 等构建链。
- `noEmit`：TypeScript 只做检查，不负责生成构建产物。

`strict` 会组合多项严格规则，其中对初学者最有感知的是严格空值、严格函数类型和更严格的隐式 `any` 检查。

## 📄 TypeScript 类型安全的局限

TypeScript 不能保证程序绝对安全，主要边界包括：

1. 类型在运行时通常被擦除。
2. `as`、`any`、非空断言 `!` 可以绕过检查。
3. 第三方类型声明可能与真实实现不一致。
4. 泛型返回类型只表达约定，不自动验证网络或后端数据。
5. 数组越界、业务规则和并发时序等问题不一定能由类型系统发现。
6. 结构兼容有时允许比预期更宽的对象进入系统。

因此更准确的认识是：

```text
TypeScript 提高程序正确性的下限，
但不能替代运行时校验、测试、代码审查和业务设计。
```

## 📄 建立类型安全代码的实践顺序

面对一个新功能，可以按以下顺序设计：

1. 先列出业务中真实存在的状态和值。
2. 用字面量联合排除无意义字符串。
3. 用对象类型描述每种数据形状。
4. 用可辨识联合表达互斥状态。
5. 在函数参数和返回值处建立模块边界。
6. 用泛型表达输入输出之间的关系。
7. 用工具类型从权威类型派生局部类型。
8. 外部数据从 `unknown` 开始，经过运行时校验。
9. 打开严格编译选项，减少 `any` 和无依据的断言。
10. 用测试验证类型系统覆盖不到的运行时行为。

阅读现有代码时，可以持续问：

```text
这个值允许出现哪些状态？
非法状态能否被构造出来？
编译器如何知道当前属于哪个分支？
类型信息是推导出来的，还是开发者断言出来的？
数据是否来自 TypeScript 无法控制的外部边界？
这里需要静态类型、运行时校验，还是两者都需要？
```

## 📄 GitTributary 类型安全阅读地图

| 类型机制 | 项目位置 | 阅读重点 |
| --- | --- | --- |
| 对象接口 | `src/App.tsx` | `NavMoreUiState` 如何描述持久化状态 |
| 字面量联合 | `src/plugins/site/types.ts` | `SitePhase` 如何限制页面阶段 |
| 可辨识联合 | `src/plugins/flow/FlowPanel.tsx` | `FlowTreeSelection` 如何绑定分支与字段 |
| 类型守卫 | `src/plugins/site/state.ts` | `value is CaptureViewMode` 如何完成收窄 |
| 泛型 | 多个 React 组件 | `useState<T>`、`useRef<T>`、`invoke<T>` |
| 工具类型 | `src/plugins/git/views/RemoteView.tsx` | `Pick`、`Partial`、`Record` 如何派生类型 |
| 未知数据校验 | `src/plugins/site/state.ts` | `unknown` 如何经过解析函数进入业务类型 |
| 严格配置 | `tsconfig.json` | 编译器如何建立整个项目的安全基线 |

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-07-11：建立 TypeScript 类型安全体系总纲，并关联 GitTributary 中的实际类型机制。

## 🛠️ 实践经历

- GitTributary：从 `App.tsx` 的 `NavMoreUiState` 出发，扩展阅读项目中的联合类型、类型守卫、泛型、工具类型、运行时校验和严格编译配置。

## ⚙️ prompt

```markdown
我关注的是 TypeScript 的一整个类型安全体系。请直接上升到知识区，建立体系化知识，并结合 GitTributary 中的实际代码提供阅读地图。
```

## 调研

暂无未提升的调研材料。
