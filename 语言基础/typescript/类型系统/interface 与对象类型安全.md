# 📌 TypeScript interface 与对象类型安全

TypeScript 的类型安全主要发生在开发和编译阶段。`interface` 可以描述对象应当具备的字段、字段类型和结构约束，使编辑器与编译器能在程序运行前发现一部分错误。

本文是对象类型专题。类型安全的整体地图参见：[TypeScript 类型安全体系](./TypeScript%20类型安全体系.md)。

## 📄 interface 描述对象结构

### 🔖 `interface` 的基本语法

GitTributary 中的定义：

```ts
interface NavMoreUiState {
  version: 1;
  open: boolean;
  updatedAt: number;
}
```

可以把它读成：定义一种名为 `NavMoreUiState` 的对象结构。符合该结构的对象必须包含三个字段：

| 语法 | 含义 |
| --- | --- |
| `interface NavMoreUiState` | 声明一个对象结构类型，类型名通常使用大驼峰命名 |
| `{ ... }` | 类型的成员区域 |
| `version: 1` | `version` 必须存在，并且值只能是数字字面量 `1` |
| `open: boolean` | `open` 必须是 `true` 或 `false` |
| `updatedAt: number` | `updatedAt` 必须是 JavaScript 的数字 |
| `;` | 分隔类型成员，不是在给字段赋值 |

`interface` 只声明规则，不会创建对象，也不会为字段赋初值。

### 🔖 `version: 1` 是字面量类型

```ts
version: 1;
```

这里的 `1` 是类型，不是默认值。它把允许值从所有 `number` 收窄成唯一的数字 `1`：

```ts
const valid: NavMoreUiState = {
  version: 1,
  open: true,
  updatedAt: Date.now(),
};

const invalid: NavMoreUiState = {
  version: 2, // 类型错误：不能将 2 分配给类型 1
  open: true,
  updatedAt: Date.now(),
};
```

这适合表示协议版本、固定状态和有限选项。未来如果数据格式升级，可以定义新版本并明确区分。

## 📄 类型安全如何参与开发

### 🔖 类型安全提供了哪些检查

给变量添加类型注解：

```ts
const state: NavMoreUiState = {
  version: 1,
  open: false,
  updatedAt: Date.now(),
};
```

此时 TypeScript 会检查：

1. 必填字段是否缺失。
2. 字段值是否符合声明的类型。
3. 直接书写的对象是否包含未知字段。
4. 后续读取字段时，字段是否确实存在以及能做哪些操作。

典型错误：

```ts
const missing: NavMoreUiState = {
  version: 1,
  open: true,
  // 错误：缺少 updatedAt
};

const wrongType: NavMoreUiState = {
  version: 1,
  open: "yes", // 错误：string 不能赋给 boolean
  updatedAt: Date.now(),
};

state.open.toUpperCase();
// 错误：boolean 没有 toUpperCase 方法
```

这些错误主要由编辑器中的 TypeScript 语言服务和构建时的类型检查器发现。它们一般不会等到用户运行程序后才暴露。

### 🔖 三种常见使用方式

#### 1. 变量类型注解

```ts
const state: NavMoreUiState = {
  version: 1,
  open: true,
  updatedAt: Date.now(),
};
```

适合明确声明“这个变量就是该类型”。变量后续会按 `NavMoreUiState` 的视角使用。

#### 2. 函数参数和返回值

```ts
function saveState(state: NavMoreUiState): void {
  console.log(state.open);
}

function createState(open: boolean): NavMoreUiState {
  return {
    version: 1,
    open,
    updatedAt: Date.now(),
  };
}
```

参数类型保护函数入口，返回值类型保护函数出口。调用者传错对象或函数返回错结构时，编译器会报错。

#### 3. `satisfies` 检查对象

GitTributary 使用了：

```ts
value: {
  version: 1,
  open,
  updatedAt: Date.now(),
} satisfies NavMoreUiState
```

`satisfies` 表示“检查这个表达式是否满足该类型”，同时尽量保留表达式自身推导出的精确类型。它适合配置对象和传给其他 API 的对象：既获得结构检查，又不强制把整个表达式直接改看成目标类型。

### 🔖 类型断言不是数据校验

项目中还有：

```ts
const state = value as Partial<NavMoreUiState>;
```

`as` 是类型断言，含义更接近“开发者要求 TypeScript 暂时按这个类型看待该值”。它不会检查运行时对象，也不会修改对象。

`Partial<NavMoreUiState>` 会把全部字段暂时视为可选字段，便于逐项检查：

```ts
interface PartialNavMoreUiState {
  version?: 1;
  open?: boolean;
  updatedAt?: number;
}
```

断言应建立在已有检查或后续检查的基础上，不能用来掩盖类型错误。

## 📄 编译期类型与运行时数据的边界

### 🔖 为什么从 store 读取数据还要手动校验

```ts
const raw = await invoke<unknown>("store_get", ...);
```

TypeScript 类型在编译后会被擦除，不能自动验证来自后端、本地存储、网络或用户输入的真实数据。外部数据可能缺字段、类型错误、来自旧版本，甚至根本不是对象。

因此项目先把数据声明为 `unknown`：

```ts
function parseNavMoreUiState(value: unknown): NavMoreUiState | null {
  if (!value || typeof value !== "object") return null;
  const state = value as Partial<NavMoreUiState>;
  if (state.version !== 1) return null;
  if (typeof state.open !== "boolean") return null;
  if (typeof state.updatedAt !== "number" || !Number.isFinite(state.updatedAt)) return null;
  return {
    version: 1,
    open: state.open,
    updatedAt: state.updatedAt,
  };
}
```

这段代码形成两层保护：

```text
外部数据
  -> unknown：禁止未经检查直接使用
  -> 运行时逐字段校验
  -> NavMoreUiState：校验成功后进入类型安全区域
```

返回类型 `NavMoreUiState | null` 还会迫使调用者处理解析失败的情况。

### 🔖 实际使用类型安全的原则

1. 为重要的业务对象定义 `interface` 或 `type`。
2. 在函数参数和返回值处明确边界类型。
3. 优先让 TypeScript 自动推导局部变量，不必给每个变量手写类型。
4. 配置对象或 API 参数可以使用 `satisfies` 做结构检查。
5. 外部输入先使用 `unknown`，校验后再转成业务类型。
6. 谨慎使用 `as`，因为它可能绕过编译器保护。
7. 避免随意使用 `any`；`any` 会让相关位置基本失去类型检查。

### 🔖 GitTributary 项目回链

- 项目文件：`src/App.tsx`
- 项目阅读笔记：`technical-note/开源项目/GitTributary/技术经验/App.tsx 前端应用外壳解读.md`
- 对应场景：侧边栏“更多”菜单状态的保存、读取、版本判断和过期清理。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-07-11：从 GitTributary `App.tsx` 提炼 `interface` 与对象类型安全知识。
- 2026-07-11：根据用户偏好，将已确认内容从调研区提升为正式知识章节。
- 2026-07-11：定位为对象类型专题，并回链 TypeScript 类型安全体系总纲。

## 🛠️ 实践经历

- GitTributary：`src/App.tsx` 使用 `NavMoreUiState` 约束“更多菜单”持久化状态，并对从 Tauri store 读取的 `unknown` 数据执行运行时校验。

## ⚙️ prompt

```markdown
我开始关注 App.tsx 中的 TypeScript 语法。

请结合 NavMoreUiState，介绍 interface、boolean、number、字面量类型，以及如何实际使用 TypeScript 的类型安全机制，并将内容沉淀到笔记中。
```

## 调研

暂无未提升的调研材料。
