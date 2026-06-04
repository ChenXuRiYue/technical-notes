# Get 和 Post 对比

基础谈资：面试中最常见的 HTTP 问题之一。很多人能说出"GET 参数在 URL 里，POST 参数在 body 里"，但这只是表象。真正区分它们的是**语义**——GET 是"取"，POST 是"交"。



## 📄 语义与设计哲学

GET 和 POST 的根本区别不在技术实现，而在**语义定义**（RFC 7231）：

| 维度 | GET | POST |
|------|-----|------|
| 语义 | 获取资源的**表示**（representation） | 向目标资源**提交数据**进行处理 |
| 幂等性 | ✅ 幂等 — 多次请求结果一致 | ❌ 非幂等 — 每次请求可能产生不同副作用 |
| 安全性 | ✅ 安全 — 不修改服务器资源状态 | ❌ 不安全 — 可能创建/修改资源 |

> **"安全"在这里是 HTTP 术语**：指不会改变服务器上的资源状态，跟"防攻击"的安全不是一回事。

**设计哲学**：HTTP 方法的设计遵循"关注点分离"思想。GET 是"只读"的，浏览器可以放心地预取、缓存、重试；POST 是"写入"的，浏览器必须谨慎对待，不能随意重复发送。



## 📄 参数传递方式

| 维度 | GET | POST |
|------|-----|------|
| 参数位置 | URL 查询字符串 `?key=value&...` | 请求体（Body） |
| Content-Type | 无需指定（或 `application/x-www-form-urlencoded`） | 必须指定，如 `application/json`、`multipart/form-data` |
| 参数可见性 | URL 中明文可见 | Body 中，URL 不可见 |

**一个常见误解**：GET 请求也可以带 Body（RFC 没有禁止），只是大部分服务器和框架会忽略它。POST 也可以带 URL 参数。技术上两者都可以，但约定俗成不这么做。



## 📄 数据大小限制

| 维度 | GET | POST |
|------|-----|------|
| 理论限制 | RFC 未规定长度上限 | RFC 未规定大小上限 |
| 实际限制 | 浏览器/服务器对 URL 长度有限制（通常 2KB~8KB） | 服务器配置限制（如 Nginx `client_max_body_size`） |

**为什么 GET 有"长度限制"**：不是 HTTP 协议规定的，而是浏览器、代理服务器、Web 服务器对 URL 长度做了截断处理。IE 的老限制是 2083 字符，现代浏览器一般支持到 64KB+，但实际场景中 URL 不应该那么长。



## 📄 缓存与书签

| 维度 | GET | POST |
|------|-----|------|
| 浏览器缓存 | ✅ 默认会被缓存 | ❌ 默认不缓存 |
| 浏览器历史 | ✅ 参数保留在历史记录中 | ❌ 不保留 |
| 书签 | ✅ 可以收藏为书签 | ❌ 不能 |
| 浏览器后退 | ✅ 无害，可重复执行 | ⚠️ 浏览器会提示"重新提交表单" |

这正是语义带来的实际影响：GET 被设计为"安全且幂等"，所以浏览器可以放心地缓存它、重试它、收藏它。



## 📄 TCP 传输行为

一个流传很广的说法是"GET 发一个 TCP 包，POST 发两个"。**这个说法过于简化，不完全准确**。

- **GET**：浏览器通常将 Header 和 Body（如果有）一起发送，确实倾向于一个包。
- **POST**：
  - 如果 Body 较小且在 `TCP_NODELAY` 模式下，也可能一个包发完。
  - 部分浏览器/服务器实现会先发 Header，等服务器返回 `100 Continue` 后再发 Body，看起来像两个包。
  - 但这取决于具体的浏览器实现和服务器配置，不是协议强制的。

**结论**：POST 不一定比 GET 多一个网络往返。实际差异取决于实现，不取决于方法本身。



## 📄 RESTful API 设计中的角色

在 REST 架构风格中，HTTP 方法映射到 CRUD 操作：

| HTTP 方法 | CRUD 操作 | 语义 | 示例 |
|-----------|-----------|------|------|
| GET | Read | 读取资源 | `GET /users/123` 获取用户信息 |
| POST | Create | 创建资源 | `POST /users` 创建新用户 |
| PUT | Update | 全量更新 | `PUT /users/123` 更新整个用户 |
| DELETE | Delete | 删除资源 | `DELETE /users/123` 删除用户 |

**POST 的延伸用途**：
- 创建子资源：`POST /users/123/orders` 为用户创建订单
- 触发操作：`POST /orders/456/cancel` 取消订单（无法用 PUT/DELETE 表达的动作）
- 复杂查询：当查询条件太长不适合放 URL 时，有些 API 设计会用 `POST /users/search`



## 📄 前端发送方式

### 原生 fetch

```javascript
// GET — 参数拼在 URL 上
fetch('/api/users?page=1&size=10')

// POST — 参数放在 body 中
fetch('/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Alice', age: 25 })
})
```

### Axios

```javascript
// GET — params 自动拼接到 URL
axios.get('/api/users', { params: { page: 1, size: 10 } })

// POST — data 自动放到 body
axios.post('/api/users', { name: 'Alice', age: 25 })
```

> **注意**：Axios 的 `get` 方法不支持传 `body`，这是有意为之——遵循 HTTP 语义。



## 📄 Spring 后端接收

```java
// GET — 用 @RequestParam 或 @PathVariable 接收
@GetMapping("/users")
public List<User> getUsers(@RequestParam int page, @RequestParam int size) { ... }

@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) { ... }

// POST — 用 @RequestBody 接收
@PostMapping("/users")
public User createUser(@RequestBody UserDTO userDTO) { ... }
```

**常见坑**：GET 请求用 `@RequestBody` 接收参数是能编译通过的，但大部分 HTTP 客户端不会在 GET 请求中带 Body，导致参数为 `null`。



## 📄 Spring 参数绑定全景盘点

### 核心注解一览

| 注解 | 数据来源 | 说明 |
|------|----------|------|
| `@RequestParam` | URL 查询参数 / 表单字段 | `?key=value` 形式 |
| `@PathVariable` | URL 路径片段 | `/users/{id}` 中的 `{id}` |
| `@RequestBody` | 请求体（Body） | 通过 `HttpMessageConverter` 反序列化 |
| `@ModelAttribute`（默认） | URL 查询参数 / 表单字段 | POJO 不加注解时的默认行为 |
| `@RequestHeader` | 请求头 | 取 Header 中的某个值 |
| `@CookieValue` | Cookie | 取 Cookie 中的某个值 |

### 组合矩阵

| 组合 | GET | POST | PUT | DELETE | 说明 |
|------|:---:|:----:|:---:|:------:|------|
| `@RequestParam` 单个参数 | ✅ | ✅ | ✅ | ✅ | 最通用，所有方法都行 |
| `@PathVariable` 路径参数 | ✅ | ✅ | ✅ | ✅ | 跟 HTTP 方法无关 |
| `@RequestParam` + `@PathVariable` | ✅ | ✅ | ✅ | ✅ | 可以同时用 |
| `@RequestBody` 接收 JSON | ⚠️ | ✅ | ✅ | ✅ | GET 能编译，但客户端一般不发 Body |
| `@RequestBody` + `@RequestParam` | ⚠️ | ✅ | ✅ | ✅ | 混合绑定，GET 同理有问题 |
| `@RequestBody` + `@PathVariable` | ⚠️ | ✅ | ✅ | ✅ | 混合绑定，GET 同理有问题 |
| POJO 默认（`@ModelAttribute`） | ✅ | ✅ | ✅ | ✅ | 从 query/form 自动绑定字段 |
| 两个 `@RequestBody` | ❌ | ❌ | ❌ | ❌ | Body 只能读一次，不支持 |

### 详细说明

#### `@RequestParam` — 最通用的方式

```java
// GET /users?page=1&size=10
@GetMapping("/users")
public List<User> list(@RequestParam int page, @RequestParam int size) { ... }

// POST 也能用（参数在 URL 上，不在 Body 里）
// POST /users?page=1   body: {"name":"Alice"}
@PostMapping("/users")
public User create(@RequestParam int page, @RequestBody UserDTO dto) { ... }
```

- 来源是 URL query string 或 `application/x-www-form-urlencoded` 的表单字段
- **跟 HTTP 方法无关**，GET/POST/PUT/DELETE 都能用
- 简单类型（String、int 等）直接用，省略注解时默认就是 `@RequestParam`

#### `@PathVariable` — 路径参数

```java
// GET /users/123
@GetMapping("/users/{id}")
public User get(@PathVariable Long id) { ... }
```

- 来源是 URL 路径中的占位符
- **跟 HTTP 方法完全无关**

#### `@RequestBody` — 请求体反序列化

```java
// POST /users   body: {"name":"Alice","age":25}
@PostMapping("/users")
public User create(@RequestBody UserDTO dto) { ... }
```

- 来源是 HTTP 请求体
- 通过 `HttpMessageConverter`（如 Jackson）反序列化为 Java 对象
- **必须配合 `Content-Type` 头**（如 `application/json`），否则框架不知道怎么解析
- 只能出现**一次**（Body 只能读一次流）

#### POJO 默认绑定（`@ModelAttribute`）

```java
// GET /users?name=Alice&age=25
@GetMapping("/users")
public List<User> search(UserQuery query) { ... }
// 等价于 @ModelAttribute UserQuery query
```

- 不加注解的 POJO 参数，默认走 `@ModelAttribute`
- 数据来源是 **query string 或 form data**，不是 Body
- **跟 HTTP 方法无关**，GET/POST 都行
- POST 提交 `application/x-www-form-urlencoded` 表单时，也是从这里取

### 关键区分：`@RequestBody` vs POJO 默认绑定

这是最容易混淆的点：

```
场景：POST /users   Content-Type: application/json   body: {"name":"Alice"}

// 写法 A — 能收到
@PostMapping("/users")
public User create(@RequestBody UserDTO dto) { ... }

// 写法 B — 收不到！dto 字段全为 null
@PostMapping("/users")
public User create(UserDTO dto) { ... }
```

| | `@RequestBody` | POJO 默认（`@ModelAttribute`） |
|---|---|---|
| 数据来源 | Body（请求体） | Query string / Form data |
| Content-Type | `application/json`、`application/xml` 等 | `application/x-www-form-urlencoded` |
| 序列化工具 | `HttpMessageConverter`（Jackson 等） | `WebDataBinder`（属性绑定） |
| 能否用于 GET | 能编译，但客户端一般不发 Body | ✅ 完全可以 |

**一句话**：想接 JSON Body 就加 `@RequestBody`；想接 URL 参数或表单字段就不加（或加 `@RequestParam`）。

### 真实场景速查

| 场景 | 方法 | 注解 | 示例 |
|------|------|------|------|
| 分页查询 | GET | `@RequestParam` | `GET /users?page=1` |
| 路径查询 | GET | `@PathVariable` | `GET /users/123` |
| 复杂条件查询 | GET | POJO 默认 | `GET /users?name=Alice&age=25` |
| 提交 JSON | POST | `@RequestBody` | `POST /users` body: JSON |
| 提交表单 | POST | `@RequestParam` 或 POJO 默认 | `POST /login` form data |
| 文件上传 | POST | `@RequestParam MultipartFile` | `POST /upload` multipart |
| 创建资源 + 分页 | POST | `@RequestBody` + `@RequestParam` | `POST /search?page=1` body: JSON |
| URL 带 ID + JSON Body | PUT | `@PathVariable` + `@RequestBody` | `PUT /users/123` body: JSON |



## 🌳 生长思考

对发散的自由捕捉、精确化

## 💭 反复绊脚

**Q1：GET 和 POST 下后端到底怎么接参数？哪些组合能用哪些不能？**

（已补充 Spring 参数绑定全景盘点，见上文）

---

**Q2：工作中遇到 GET + @RequestBody 能跑通，为什么？**

前端传的是 GET URL 参数，后端却用 `@RequestBody` 接收。追查发现是网关 Filter 在转发前把 URL 参数搬到了 Body 里，并把 Content-Type 改成 JSON。这不是 GET + Body 的能力，是网关做的转换。

```java
// 网关层：将 GET 的 query param 写入 body
if (HttpMethod.GET == context.getMethod()) {
    context.getQueryParams().forEach((key, value) -> addColumn(objectNode, key, value));
}
```

---

**Q3：客户端发 GET+Body 和微服务间发 GET+Body，风险一样吗？**

不一样。客户端到服务端中间隔了 CDN、负载均衡、网关，任何一层都可能丢弃 GET 的 Body。微服务间链路短、客户端可控，Body 被丢弃的概率低得多。所以内部接口可以灵活，对外接口应严格遵守语义——GET 不带 Body。

## 🗺️ 修订记录

- 2026-06-04：初版创建
