# 📌 Promise 与异步调用处理

`Promise<T>` 不是最终的 `T`，而是一个“将来可能成功得到 `T`，也可能失败”的对象。

调用返回 Promise 的函数后，当前这一层必须做出责任选择：

```text
当前层需要结果？
  ├─ 需要       -> await，并决定是否在这里处理失败
  └─ 不需要
       ├─ 调用者需要知道完成与否 -> return Promise
       └─ 调用者也无需等待       -> void Promise，但失败仍要有归宿
```

`await`、`return`、`.then/.catch` 和 `void` 不是四种随意互换的写法。它们表达的是：当前层是否等待、谁使用结果、谁处理失败。

## 📄 Promise 表示一个将来的结果

### 🔖 三种状态

Promise 只会从等待中转向成功或失败，状态一旦确定就不再改变：

```text
pending
  ├─ fulfilled -> 得到成功值
  └─ rejected  -> 得到失败原因
```

`fulfilled` 和 `rejected` 合称 `settled`。

```ts
const userPromise: Promise<User> = loadUser();
```

`userPromise` 不是 `User`。只有当 Promise 成功后，才能通过 `await` 或 `.then()` 取得 `User`。

### 🔖 async 函数一定返回 Promise

```ts
async function getCount() {
  return 1;
}

const count = getCount(); // Promise<number>
```

`async` 会把普通返回值包装成 Promise。但没有 `async` 的普通函数也可以直接返回 Promise：

```ts
function getCount(): Promise<number> {
  return Promise.resolve(1);
}
```

因此，判断一次调用是否产生异步结果，最可靠的依据是返回类型 `Promise<T>`，而不是函数名。

## 📄 当前层如何接住 Promise

### 🔖 await：当前步骤需要结果

```ts
async function showCurrentUser() {
  const user = await loadUser();
  renderUser(user);
}
```

`await` 暂停的是当前 `async` 函数的后续执行，不会阻塞 JavaScript 线程。当后续逻辑依赖成功值时，使用 `await`。

如果 Promise 失败，`await` 会抛出该失败。当前层能恢复或转换错误时，再在这里捕获：

```ts
async function showCurrentUser() {
  try {
    const user = await loadUser();
    renderUser(user);
  } catch (error) {
    renderLoadFailure(error);
  }
}
```

### 🔖 return：把完成与失败交给调用者

```ts
function loadCurrentUser(): Promise<User> {
  return loadUser();
}
```

当前函数不消费结果，也不隐藏失败，而是返回同一条 Promise 链。上层可以继续 `await`、返回或捕获它。

```text
return promise
  = 当前层不等待结果
  = 调用者仍能观察成功或失败
```

### 🔖 then/catch：用回调组织后续步骤

```ts
loadUser()
  .then((user) => renderUser(user))
  .catch((error) => renderLoadFailure(error));
```

`.then()` 注册成功后的步骤，`.catch()` 注册失败后的步骤。它们每次都会返回一个新 Promise，因此可以继续组成链。

```ts
const namePromise = loadUser().then((user) => user.name);
// Promise<string>
```

`await + try/catch` 和 `.then/.catch` 是两种组织 Promise 流程的方式。一条业务链通常选一种主要写法，避免无必要的来回切换。

### 🔖 void：明确表示当前层不等待

```ts
void savePreference().catch(reportSaveFailure);
```

这里的 `void` 是 JavaScript 一元运算符。它会执行右侧表达式，并把整个表达式的值变成 `undefined`。

```ts
const result = void savePreference();
// result 是 undefined，savePreference 仍然已经被调用
```

`void` 不会启动、取消或处理 Promise，它只是明确丢弃返回值。异步操作在函数被调用时就已经开始。

## 📄 失败必须有明确归宿

### 🔖 void 不等于错误处理

```ts
void savePreference();
```

这只表示不使用返回值。如果 `savePreference()` 失败，仍可能产生未处理的 Promise rejection。

对于不影响主流程的任务，可以不等待，但应记录、上报或转换失败：

```ts
void savePreference().catch((error) => {
  console.error("偏好保存失败", error);
});
```

适合不等待的任务包括非关键 UI 偏好持久化、辅助统计和可丢失缓存。付款、订单提交、关键数据写入等操作不能使用这种方式隐藏完成状态。

### 🔖 catch 之后也是新 Promise

```ts
const handled = savePreference().catch(reportSaveFailure);
void handled;
```

`.catch()` 返回新 Promise。如果错误处理函数自己抛错或返回失败的 Promise，新 Promise 仍会失败。因此 fire-and-forget 的最终错误处理器应尽量简单、可靠。

### 🔖 不要和 TypeScript 返回类型 void 混淆

```ts
function logMessage(message: string): void {
  console.log(message);
}

void logMessage("hello");
```

| 写法 | 含义 |
| --- | --- |
| `function f(): void` | TypeScript 返回类型，调用者不应依赖返回值 |
| `void f()` | JavaScript 一元运算符，执行调用并丢弃表达式的值 |

## 📄 一套稳定的判断顺序

阅读异步调用时，按下列顺序判断：

```text
1. 返回类型是什么？
   Promise<T> 表示将来的 T。

2. 当前层需要 T 吗？
   需要就 await 或 then。

3. 不需要 T 时，调用者需要知道完成与否吗？
   需要就 return Promise。

4. 整条调用链都不等待时，失败去哪里？
   使用可靠的 catch 记录、上报或降级，再用 void 表明丢弃结果。
```

最终检查的不是“有没有写 `await`”，而是：

```text
成功结果是否有消费者？
失败是否有处理者？
不等待是否符合业务语义？
```

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-07-14：从 GitTributary `App.tsx` 的 `void invoke(...).catch(...)` 提炼 Promise 主动忽略与 `void` 一元运算符知识。
- 2026-07-14：以“Promise 返回后的责任归属”重构全文，移除复杂表达式拆解等偏离主线的内容。

## 🛠️ 实践经历

- GitTributary：[App.tsx 前端应用外壳解读](../../../开源项目/GitTributary/技术经验/App.tsx%20前端应用外壳解读.md) 中，`void invoke("store_set", ...).catch(...)` 用于保存非关键 UI 状态。界面可立即更新，持久化失败不阻断当前操作，但仍由 `catch` 承接失败。
- 对象参数与 `satisfies` 属于类型系统主题，参见 [TypeScript interface 与对象类型安全](../类型系统/interface%20与对象类型安全.md)。

## ⚙️ prompt

```markdown
JavaScript / TypeScript 函数返回 Promise 后，当前调用层应该如何处理？

请以“结果与失败的责任归属”为主线，解释 `await`、`return Promise`、`.then/.catch` 和 `void Promise` 的适用条件与错误传播边界。
```

## 调研

暂无未提升的调研材料。
