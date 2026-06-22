# SSE 协议

SSE 协议是一种用于维护服务端客户端交互的协议

## 📄 SSE 的历史背景

故事从 Web 的"先天缺陷"讲起——**HTTP 天然是无状态、请求-响应模式的**。客户端不问，服务器就不说话。

但 Web 应用越来越实时化了。聊天室、股票行情、消息通知……服务器想主动推消息，怎么办？

---

最早的土办法是 **轮询（Polling）**——客户端定时问"有新消息没？"，大部分请求换来一句"没有"。浪费带宽，延迟也高。改良版叫**长轮询（Long Polling）**：服务器憋着不响应，有数据才返回，客户端收到后立刻再发一个。好一些，但本质还是在"假装"流式通信。再 hack 一点，用隐藏 `<iframe` + `chunked` 传输硬撑，能用但脆弱。

2011 年前后，**WebSocket** 横空出世——全双工、实时、双向通信。听起来完美，但它是一个全新的协议，需要从 HTTP 升级，不复用 HTTP 语义（缓存、认证、代理都得重新处理）。对很多**只需要服务端推送**的场景来说，杀鸡用牛刀。

---

于是 **SSE（Server-Sent Events）** 登场。HTML5 规范引入了它 + `EventSource` API，核心思想极其朴素：

```text
客户端用普通 HTTP GET 连上服务器
服务器保持连接不关闭，以 Content-Type: text/event-stream 响应
持续发送事件（event: / data: / id: / retry:）
浏览器自动处理重连
```

本质上就是**一个不结束的 HTTP 响应**。复用已有的 HTTP 生态，对服务端几乎零额外要求。

但 SSE 诞生后并没有立刻流行——IE / Edge 不支持 `EventSource`，前端框架没有原生集成，WebSocket 的声量又太大。那个年代，它是"冷门但正确"的技术选择。

---

转折点是 **2022 年底 ChatGPT 的爆发**。大模型推理是典型的单向流式场景——模型一边生成 token，一边推给前端渲染：

```text
data: {"choices":[{"delta":{"content":"你"}}]}
data: {"choices":[{"delta":{"content":"好"}}]}
data: [DONE]
```

SSE 完美契合：单向推送、流式传输、HTTP 兼容——不改协议，不改基础设施，即插即用。随后 OpenAI API、Anthropic API、MCP 协议的 Streamable HTTP 传输层全部拥抱了 SSE。它从冷门协议一跃成为 **AI 应用的事实标准传输方案**。

> 🌱 Web 有了推送需求 → 土办法 → WebSocket 太重 → SSE 回归简单 → 被冷落多年 → 被 AI 重新发现。核心哲学始终没变：**不发明新协议，用 HTTP 已有能力解决问题**。



## 📄 SSE 协议规范

SSE 由 WHATWG 组织定义在 **HTML Living Standard §9.2 Server-sent events** 中。它不是一个独立的 RFC 协议，而是 Web 标准的一部分。

---

**协议本质**：客户端发起一个普通 HTTP GET 请求，服务端以 `Content-Type: text/event-stream` 响应，并**保持连接不关闭**，持续向客户端推送事件。连接建立后，数据流是**单向的**——只有服务端向客户端发送，客户端不能通过同一连接向服务端发送数据。

**事件流格式（text/event-stream）**：规范定义了一种基于文本的行格式。每个字段占一行，格式为 `字段名: 值`，字段之间用空行（`\n\n`、`\r\r` 或 `\r\n\r\n`）分隔。一次完整的空行标志着一个事件的结束。

规范定义了且仅定义了以下四个字段：

| 字段 | 含义 | 默认值 |
|------|------|--------|
| `event` | 事件类型，用于 `addEventListener` 分类监听 | `"message"` |
| `data` | 事件数据，可多行，每行一个 `data:` 前缀 | （必填） |
| `id` | 事件 ID，设置后客户端会记住，断线重连时通过 `Last-Event-ID` 请求头回传 | 空 |
| `retry` | 重连间隔，单位毫秒，仅接受整数 | 3000 |

以 `:` 开头的行是**注释**，服务端通常用它发送心跳（`: heartbeat\n\n`）以防止连接被中间代理超时断开。

一个完整的事件示例：

```text
id: 42
event: chat
retry: 5000
data: 第一行内容
data: 第二行内容
\n
```

其中 `data` 字段的多行值在客户端会被拼接为 `"第一行内容\n第二行内容"` 交给 `MessageEvent.data`。

---

**客户端 API — EventSource**：浏览器原生提供 `EventSource` 对象，构造时传入 URL：

```javascript
const es = new EventSource('/stream')
es.onmessage = e => console.log(e.data)        // 默认 event: message
es.addEventListener('chat', e => {})            // 自定义事件类型
es.onerror = e => { /* 自动重连中 */ }
es.close()                                      // 主动断开
```

`EventSource` 的关键行为由规范强制规定：

- **自动重连**：连接断开后，客户端按 `retry` 字段指定的间隔自动重新发起请求，并在请求头中携带 `Last-Event-ID`，服务端可据此补发丢失的事件。
- **跨域**：支持 CORS，构造时可传 `{ withCredentials: true }` 携带 Cookie。
- **只读**：`EventSource` 只能接收数据，不能发送。如需双向通信，应使用 WebSocket。
- **状态机**：`readyState` 有三个值：`CONNECTING(0)`、`OPEN(1)`、`CLOSED(2)`。

---

**与 HTTP 的关系**：SSE 不是独立协议，它完全运行在 HTTP 之上。一个合规的 SSE 响应只需要满足：

```text
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

后续的事件数据作为响应体以 chunked 方式持续发送。这意味着 SSE 天然兼容 HTTP/1.1 和 HTTP/2，能穿过绝大多数代理和负载均衡器，不需要特殊的网络配置。

## 📄 协议标识与开发实践

**协议栈中的位置**：SSE 并不是一个独立的传输层或应用层协议，它没有自己的端口号，也没有像 WebSocket 那样的 `Upgrade` 握手。它完全运行在 HTTP 之上，唯一的标识就是响应头中的 `Content-Type: text/event-stream`。换句话说，**一个 SSE 连接就是一个没有写完的 HTTP 响应**——服务端发完状态码和头部后，不断往响应体里写数据，就是不发结束标记。

中间设备（代理、网关、负载均衡器）看到的是一个普通的 HTTP 200 响应，只不过响应体一直在增长。这也是它兼容性好的原因，也是它容易被超时断开的原因——需要靠心跳（注释行 `: keepalive\n\n`）来续命。

---

**JavaScript 开发**：浏览器原生支持 `EventSource`，这是最简单的方式：

```javascript
const es = new EventSource('/api/stream')

// 监听默认事件
es.onmessage = (e) => {
  console.log('收到:', JSON.parse(e.data))
}

// 监听自定义事件类型
es.addEventListener('heartbeat', (e) => {
  console.log('心跳:', e.data)
})

// 错误处理（含自动重连）
es.onerror = (e) => {
  if (es.readyState === EventSource.CONNECTING) {
    console.log('断线，正在重连...')
  }
}

// 主动关闭
es.close()
```

当需要更精细的控制（如自定义请求头、POST 请求、手动处理流）时，用 `fetch` + `ReadableStream`：

```javascript
const res = await fetch('/api/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: '你好' })
})

const reader = res.body.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  const text = decoder.decode(value)
  // 按 "\n\n" 拆分事件，解析 "data:" 字段
}
```

AI 应用（ChatGPT、Claude）普遍采用后者，因为需要 POST 请求体和自定义头部。

---

**Java 开发**：主流框架都提供了 SSE 支持。

Spring MVC 使用 `SseEmitter`，它是对异步响应的封装：

```java
@GetMapping("/stream")
public SseEmitter stream() {
    SseEmitter emitter = new SseEmitter(60_000L); // 超时 60s

    // 异步推送事件
    CompletableFuture.runAsync(() -> {
        try {
            for (int i = 0; i < 10; i++) {
                emitter.send(SseEmitter.event()
                    .id(String.valueOf(i))
                    .name("message")
                    .data("第 " + i + " 条消息"));
                Thread.sleep(1000);
            }
            emitter.complete();
        } catch (Exception e) {
            emitter.completeWithError(e);
        }
    });

    return emitter;
}
```

> 🌱 核心要点：SSE 不需要特殊的 SDK 或协议库。任何能往 HTTP 响应体里写文本的后端框架都能实现 SSE，区别只在于封装的便利程度。选型上，Spring Boot 项目优先用 `SseEmitter`（简单场景）或 WebFlux（高并发流式场景）。

## 📄 SSE vs WebSocket

两者都用于实时通信场景，但设计哲学截然不同：

| | SSE | WebSocket |
|---|---|---|
| **方向** | 单向（服务端 → 客户端） | 双向（全双工） |
| **协议** | HTTP（`text/event-stream`） | 独立协议（`ws://` / `wss://`） |
| **握手** | 普通 HTTP GET | HTTP Upgrade 握手后切换协议 |
| **自动重连** | ✅ 浏览器原生支持（`Last-Event-ID`） | ❌ 需手动实现心跳 + 重连逻辑 |
| **数据格式** | 纯文本 | 文本 + 二进制 |
| **代理/防火墙** | 友好（普通 HTTP 流量） | 可能被拦截（非标准 HTTP） |
| **连接数限制** | HTTP/1.1 下同域约 6 个并发连接 | 无此限制 |
| **实现复杂度** | 低（一个不结束的 HTTP 响应） | 较高（帧协议、心跳、状态管理） |

**选型原则**：客户端需要频繁向服务端发消息（聊天、游戏、协同编辑）→ WebSocket；只需服务端推送（通知、数据流、AI 流式输出）→ SSE 更简单可靠。

> 🌱 SSE 历史上被认为功能不足，但 AI 时代证明了大量场景只需要单向推送。WebSocket 的全双工能力是优势也是成本——协议升级、连接管理、中间设备兼容都是额外负担。**够用的协议就是最好的协议**。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

对发散的自由捕捉、精确化

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

---

##### Q1：SSE 基于 HTTP，那 IP 够用吗？设备 IP 稳定吗？

→ 见 [[局域网#Q2：那 IPv4 地址够用吗？我设备的 IP 是什么，稳定吗？]]

##### Q2：SSE 为什么能保持长时间连接？能保持多久？

SSE 没有"长握手"。本质是**服务端一直没写完这个 HTTP 响应**——chunked 编码下，服务端可以持续往响应体写数据而不发结束标记，协议本身不限制响应时长。

瓶颈在中间设备：Nginx 默认 `proxy_read_timeout` 60s、云负载均衡通常 60~300s 会断开空闲连接。实际靠心跳续命——每 15~30s 发一个注释行 `: heartbeat\n\n`，有数据流过就不会被断。理论上心跳不断，连接可持续数天。

##### Q3：既然 IP 不固定，通过 SSE 协议怎么找到我？

→ 见 [[局域网#Q3：既然 IP 不固定，服务器怎么找到我？]]

## 🗺️ 修订记录

重要修订记录

## 🛠️ 实践经历

记录实践经历： demo + 工作经历 + 第三方优秀经验反思

### SSE 实现踩坑：代理缓冲导致连接失败

**场景**：实现基于 SSE 的 MCP 服务，客户端通过网关访问。

**现象**：SSE 连接始终无法建立，客户端收不到任何事件。

**根因**：网关设置了缓存队列，会先把响应数据攒在内存里，达到一定条件（缓冲区满/超时/请求结束）才集中转发。SSE 的前提是数据写一点就立刻到达客户端，两者天然冲突。

**排查思路**：绕过网关直连应用，确认 SSE 本身没问题；再逐层加回中间设备，定位哪一层在缓冲。

**常见缓冲源及解法**：

| 缓冲源 | 解法 |
|--------|------|
| Nginx `proxy_buffering`（默认 on） | `proxy_buffering off` 或响应头加 `X-Accel-Buffering: no` |
| gzip 压缩 | SSE 响应禁用 gzip |
| Spring 输出缓冲 | 手动 flush：`response.flushBuffer()`（`SseEmitter` 已处理） |
| CDN / 多层网关 | 每一层单独关闭缓冲 |

> 🌱 SSE 的难点不在协议本身，在于**让沿途所有中间设备都别攒数据**。这是运维问题多过开发问题。



## ⚙️ prompt

探究该文档模块过程中的 prompt 记录
模版如下：
```markdown
# 背景
我是一名追求效率的学习者。我从事于Java后端开发工程师的工作。
我认为学习本质上就是 大量正确信息的消化 + 关键结论的感受 + 自由的发散。
依托这样的思想，我希望和你来进行一场talk。

我们的 talk 基于以下原则
1. 你是 该talk 主题下的专家
2. 我是一名在其他领域具有通用性技能的工程师，如 Java、传统算法、后端工程、C++ 语法、Go 语法等。拥有一定计算机基础的知识。
3. 我们是不同领域的擅长者，这是一场圆桌会议式的talk。就和索尔维会议一样，阿尔伯特·爱因斯坦与尼尔斯·玻尔之间的交流。
4. 以你的权重为主前提下，我希望我们相互的问询感兴趣的内容。这样可以推动 talk 的进度。
# talk 主题


# 思维链
1. 我对信息的要求是，你应该减少幻觉，即信息是足够正确的
2. 我总是对一件事物的是什么、从哪里来感到好奇。所以，你可以简略说明它的历史阶段以及发展哲学
3. 我一边和你 talk，一边做草稿笔记。因此你的言语足够开阔，具有阐述性的同时，也要让我容易从中记录归纳总结。但是请你不要直接给我总结笔记，因为我希望可以主动消化。

# 输入格式
我将会输入一个问题

# 输出格式
不需要特殊的模版。参照思维链
# 当前问题


# 问题阶段(记录了 talk 的过程，方便复用)


--------
以下内容是我方便复制粘贴模版，请你忽略
## 问题X：
### 问题描述：

### 关键结论：
```

## 调研

AI 创建笔记时，调研结果追加到此处。仅记录相关经验和信息，由用户自行整理。
