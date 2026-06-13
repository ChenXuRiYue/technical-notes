# 📌 MCP (Model Context Protocol)

## 📄 MCP 是什么

**一句话**：AI 应用的 USB-C——标准化 LLM 连接外部工具和数据源的方式。

**为什么需要它**：之前每家平台各给一套插件 API，工具开发者要对每个平台适配一次。MCP 把这件事统一了——写一个 Server，所有支持 MCP 的 Host 都能接。

**和 function calling 的区别**：

| | function calling | MCP |
|--|--|--|
| 工具从哪来 | 每次请求手写定义 | Server 启动时声明，Host 自动发现 |
| 谁执行 | 同一进程里 | Client/Server 分离，Host 只管转发 |
| 跨平台复用 | OpenAI 和 Anthropic 定义不一样 | 统一标准，写一次到处用 |
| 安全边界 | 靠应用自解 | 协议层定义 consent 机制 |
| 不止 tools | 只有函数调用 | 还标准化了 Resources 和 Prompts |
| 生命周期 | 单次请求内 | Server 常驻进程，可维持连接、推送通知 |


## 📄 协议架构

**核心架构：Hub-and-Spoke**（中心辐射）

```
┌──────────────────────────────────────┐
│              Host (Hub)              │  ← Claude Desktop、IDE、Cursor…
│  ┌──────────┐  ┌──────────┐         │
│  │ Client 1 │  │ Client 2 │  ...    │  ← 每个 Client 1:1 连接一个 Server
│  └────┬─────┘  └────┬─────┘         │
└───────┼──────────────┼──────────────┘
        │              │
   ┌────▼────┐   ┌─────▼────┐
   │ Server A│   │ Server B │          ← 暴露 tools / resources / prompts
   └─────────┘   └──────────┘
```

**为什么 Host 是中心？** 不是因为它强大，而是因为**安全必须经过它**。用户只和 Host 交互，Server 返回的数据 Host 决定要不要给 LLM 看，LLM 想调用工具 Host 先问用户"你确定吗？"。就像家里的路由器——所有流量经过它，不是因为它最聪明，而是它是你家网络的唯一入口。

**三大角色**

| 角色 | 是什么 | 职责 |
|------|--------|------|
| Host | 用户侧应用（Claude Desktop、IDE） | 管理权限、拦截敏感操作、聚合工具 |
| Client | Host 内部组件，1:1 绑定 Server | 连接管理、工具发现、请求转发 |
| Server | 外部服务，暴露工具和数据 | 响应工具调用、提供资源、不可信 |

**Server 暴露的三大原语**

| 原语 | 方向 | 用途 | 类比 |
| ---- | ---- | ---- | ---- |
| Tools | Client → Server | 模型可调用（需用户确认） | 函数 / API |
| Resources | Client → Server | 模型可读的数据 | GET 端点 |
| Prompts | Client → Server | 预置 prompt 模板，用户主动选用 | 命令面板 |

**Tools**：Server 声明"我能做什么"（name/description/inputSchema），LLM 决定"什么时候调"，Host 拦截"用户同不同意"。

**Resources**：Server 暴露数据（文件内容、DB 记录），LLM 可以主动拉取。每个 resource 有 URI（如 `file:///xxx`），支持订阅变更。

**Prompts**：预置的 prompt 模板，由用户主动触发（比如在 IDE 里选一个"代码审查"模板），模型不能直接调用。


## 📄 协议历史与演进

以 Git MCP Server 为例，贯穿四个版本。

| 版本 | 状态 | 核心主题 | 一句话 |
|:----:|:----:|:--------:|:------:|
| `2024-11-05` | Final | 初始协议 | "能调" |
| `2025-03-26` | Final | 架构升级 | "安全地调" |
| `2025-06-18` | Final | 安全与交互 | "有来有回地调" |
| `2025-11-25` | **Current** | 标准化与生态 | "自主地调" |

### 2024-11-05：能跑起来

Claude → tools/call → Git MCP → 返回结果。单向一问一答，没有认证，没有安全标注。

### 2025-03-26：安全 + 语义化

```
Claude                  OAuth Server              Git MCP
  │                          │                        │
  │── 请求授权 ─────────────→│                        │
  │←── 返回令牌 ─────────────│                        │
  │── tools/call (Token) ───────────────────────────→│
  │                          ⚠ destructive:true       │
  │←── 弹窗确认后返回结果 ───────────────────────────│
```

新增：OAuth 2.1 认证、工具注解（`destructive:true` 弹窗确认）、Streamable HTTP 传输。

### 2025-06-18：双向交互

这个版本的核心突破是 **Elicitation**——Server 能主动向 Client 发请求，让 Client 弹窗问用户。在此之前，Server 只能被动响应；有了 Elicitation，Server 变成了主动参与者。

```
Claude                         Git MCP
  │                              │
  │── git_merge("feature-x") ──→│
  │←── 💬 "要合并到哪个分支？" ──│  Server 主动反问
  │── "main" ──────────────────→│
  │←── 💬 "发现 3 个冲突" ──────│  Server 再次反问
  │── theirs/ours ─────────────→│  Client 逐文件决策
  │←── ✅ 合并完成 ─────────────│
```

**怎么做到的？**

MCP 基于 JSON-RPC 2.0，不区分 Client/Server 固定角色，只有 Request/Response 的对称关系。同一条线上，消息方向自由：

```json
// Client → Server（工具调用）
{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}

// Server → Client（Elicitation：反问用户）
{"jsonrpc": "2.0", "id": 2, "method": "elicitation/create", "params": {
  "message": "要合并到哪个分支？"
}}

// Server → Client（Sampling：调用 LLM）
{"jsonrpc": "2.0", "id": 3, "method": "sampling/createMessage", "params": {
  "messages": [{"role": "user", "content": "生成 commit message"}]
}}
```

传输层承载方式：stdio 本身就是两根管道（stdin/stdout），天然双向；Streamable HTTP 用 POST 发请求，用 SSE（Server-Sent Events）做服务端推送。

新增：Elicitation（Server 主动反问）、结构化输出、资源链接。Server 从"被动提供"变成"主动参与决策"。

### 2025-11-25：企业级智能体

```
┌─────────────────┐        ┌─────────────────┐
│  🤖 Claude      │        │  📦 Git MCP     │
│  🔧 工具调用    │        │  🧠 调用 LLM    │
│  📋 Task 异步   │ ⇄ 协商 ⇄│  🔍 自动发现    │
│  🎨 图标化 UI   │        │  📊 结构化输出   │
└─────────────────┘        └─────────────────┘
```

新增：Tasks（异步任务轮询）、Tool Calling in Sampling（Server 调用 LLM）、OpenID Connect、增量授权。

### 演进方向

`2024-11-05` 基础协议 → `2025-03-26` 安全+传输 → `2025-06-18` 交互+治理 → `2025-11-25` 企业级成熟

- **安全**：OAuth 2.1 → Resource Server → OpenID Connect
- **交互**：单向调用 → Elicitation + Sampling + Tool Calling
- **传输**：HTTP+SSE → Streamable HTTP → SSE 轮询 + 可断开
- **治理**：无 → 正式治理结构 + 工作组 + SDK 分级


## 📄 传输层

MCP 协议不绑定传输层，当前有两种官方传输方式，对应本地和远程两种部署形态。传输层只负责搬运，消息格式始终是 JSON-RPC 2.0。

### stdio vs Streamable HTTP

| 维度 | stdio（本地） | Streamable HTTP（远程） |
| --- | --- | --- |
| **通信方式** | stdin/stdout 管道，每行一条 JSON-RPC | POST `/mcp` 发请求，可选 SSE 流收推送 |
| **进程管理** | Host 直接 fork 子进程，生命周期跟着 Host 走 | Server 独立部署，Host 不管它的生死 |
| **认证** | 不需要（同一台机器，靠操作系统隔离） | OAuth 2.1（Server 返回 401 → Client 走 PKCE 授权） |
| **会话** | 进程活着 = 会话活着，断了就是断了 | 靠 `Mcp-Session-Id` 头维持，支持断线重连 |
| **延迟** | 微秒级（管道 IPC） | 网络延迟（几十到几百毫秒） |
| **信任模型** | 用户装了就信任，Host 可 auto-approve | 第三方服务器，必须 OAuth 授权 + 防 prompt injection |
| **适用场景** | 本地工具（git、文件系统、数据库客户端） | 团队共享服务、SaaS 集成、企业内部平台 |

**stdio 消息格式**

每行一条 JSON-RPC，通过管道读写：

```
stdin  →  {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{...}}
stdout ←  {"jsonrpc":"2.0","id":1,"result":{...}}
```

**Streamable HTTP 消息格式**

Client 发 POST，Server 可回 JSON 或升级为 SSE 流：

```
POST /mcp
Content-Type: application/json
Mcp-Session-Id: abc123

{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{...}}

--- Server 回复（普通 JSON） ---
200 OK
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"result":{...}}

--- 或 Server 回复（SSE 流，用于长时间任务） ---
200 OK
Content-Type: text/event-stream

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progress":50}}

event: message
data: {"jsonrpc":"2.0","id":1,"result":{...}}
```


## 📄 安全模型

核心原则：**Host 是信任边界，Server 不可信**。

1. **用户同意**：tool 调用默认需用户确认，Host 可 auto-approve 白名单
2. **OAuth 2.1**（远程场景）：Server 返回 401，Client 走 PKCE 流程获取 token
3. **沙箱**：stdio Server 建议容器运行，限制文件系统和网络
4. **Prompt Injection 防护**：Server 返回内容可能含恶意指令，Host 应当"数据"对待


## 📄 配置与注册

### 配置文件位置

| Host | 文件 | 作用域 |
| --- | --- | --- |
| Claude Desktop | `claude_desktop_config.json` | 全局 |
| Claude Code | `.mcp.json`（项目根目录） | 项目级 |
| Claude Code | `~/.claude/settings.json` | 用户级 |

### 配置结构

所有 Host 共用同一套 JSON 结构，顶层是 `mcpServers`，每个 key 是一个 Server 实例：

```json
{
  "mcpServers": {
    "<server-name>": {
      // --- 连接方式（二选一） ---
      "command": "npx",                          // 本地：可执行文件
      "args": ["-y", "my-mcp-server"],            // 本地：命令行参数数组
      // "type": "url",                           // 远程：声明类型为 url
      // "url": "https://mcp.example.com/mcp",    // 远程：Server 地址

      // --- 可选字段 ---
      "env": { "API_KEY": "${MY_KEY}" },          // 环境变量，${} 引用宿主机变量
      "allowedTools": ["search", "list_indices"],  // 工具白名单，只暴露这些给 LLM
      "autoApprove": ["git_status"]                // 自动放行，不弹确认框
    }
  }
}
```

### 逐字段解析

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `mcpServers` | ✅ | 顶层 map，key 是 Server 名称，一个 Host 可同时连多个 Server |
| `command` | ✅ | 程序名（本地模式），如 `npx`、`uvx`、`python`、绝对路径 |
| `args` | 否 | 启动参数数组，和终端敲命令一模一样，拆成数组写 |
| `env` | 否 | 注入给子进程的环境变量，`${VAR}` 从宿主机读取后替换（用于隐藏密钥） |
| `allowedTools` | 否 | 工具白名单，只暴露这些给 LLM，其余不可见 |
| `autoApprove` | 否 | 自动放行列表，这些工具调用不弹确认框 |
| `type` | 远程必填 | 设为 `"url"` 表示远程连接 |
| `url` | 远程必填 | 远程 Server 地址，Host 通过 HTTP 连接 |

### 本地 Server 配置

MCP Server 本质是一个普通可执行程序，只是通过 stdin/stdout 说 JSON-RPC。`command` + `args` 就是告诉 Host "用什么方式启动这个程序"，等价于在终端里敲命令：

```bash
npx -y @modelcontextprotocol/server-filesystem   # command: "npx", args: ["-y", "@modelcontextprotocol/server-filesystem"]
uvx mcp-server-git                                # command: "uvx", args: ["mcp-server-git"]
python -m my_mcp_server                           # command: "python", args: ["-m", "my_mcp_server"]
/usr/local/bin/my-mcp-server                      # command: "/usr/local/bin/my-mcp-server", args: []
docker run -i --rm my-mcp-image                   # command: "docker", args: ["run", "-i", "--rm", "my-mcp-image"]
```

| 来源 | command | args 示例 | 说明 |
| --- | --- | --- | --- |
| npm 包 | `npx` | `["-y", "@modelcontextprotocol/server-filesystem"]` | npm 生态，`-y` 跳过确认直接运行 |
| Python (uv) | `uvx` | `["mcp-server-git"]` | uv 包管理器，自动下载并运行 |
| Python (pip) | `python` | `["-m", "my_mcp_server"]` | 传统 pip 安装后用 `python -m` 运行 |
| 本地二进制 | 绝对路径 | `["/usr/local/bin/my-mcp-server"]` | 直接执行编译好的程序 |
| Docker | `docker` | `["run", "-i", "--rm", "my-mcp-image"]` | 容器化运行，环境隔离 |

### 远程 Server 配置

远程 Server 已经在某台服务器上运行，不需要你启动，只需要告诉 Host 去连它。用 `type: "url"` + `url` 替代 `command` + `args`：

```json
{
  "mcpServers": {
    "team-git": {
      "type": "url",
      "url": "https://mcp.internal.example.com/mcp"
    }
  }
}
```

首次连接时 Server 返回 401 → Host 自动弹浏览器走 OAuth 登录 → 拿到 token 后后续请求自动带上。

### 多实例：同一 Server 不同环境

Server 名称区分实例。本地模式通过 `env` 指向不同环境，远程模式直接连不同 URL：

```json
{
  "mcpServers": {
    "es-staging": {
      "command": "npx",
      "args": ["-y", "@awesome-ai/elasticsearch-mcp"],
      "env": { "ES_HOST": "http://staging.es.srv:80" },
      "allowedTools": ["search", "list_indices"]
    },
    "es-prod": {
      "command": "npx",
      "args": ["-y", "@awesome-ai/elasticsearch-mcp"],
      "env": { "ES_HOST": "http://prod.es.srv:80" },
      "allowedTools": ["search", "list_indices", "elasticsearch_health"]
    },
    "es-cloud": {
      "type": "url",
      "url": "https://es-mcp.example.com/mcp"
    }
  }
}
```

每个实例独立进程/连接，互不影响。


## 📄 MCP Server 实现模板

以 Git MCP Server 为例，完整展示如何从零实现。

### 设计工具清单

| 工具名 | 用途 | 安全标注 |
|--------|------|----------|
| `git_log` | 查看提交历史 | readOnly: true |
| `git_diff` | 查看文件差异 | readOnly: true |
| `git_status` | 查看工作区状态 | readOnly: true |
| `git_commit` | 创建提交 | destructive: false |
| `git_push` | 推送到远程 | destructive: true |
| `git_create_branch` | 创建分支 | destructive: false |

### 定义工具 Schema

每个工具需要一个 JSON Schema 定义输入参数：

```json
{
  "name": "git_log",
  "description": "查看 Git 提交历史",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": { "type": "number", "description": "返回的提交数量，默认 10" },
      "branch": { "type": "string", "description": "指定分支，默认当前分支" }
    },
    "required": []
  },
  "annotations": { "readOnlyHint": true }
}
```

`annotations` 是 v2025-03-26 引入的工具注解，`readOnlyHint: true` 告诉 Host 这个工具不会修改数据，可以 auto-approve。

### 实现 Server 核心（TypeScript）

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execSync } from "child_process";

const server = new McpServer({ name: "git-mcp", version: "1.0.0" });

// 注册工具：git_log
server.tool(
  "git_log",
  "查看 Git 提交历史",
  { limit: z.number().default(10), branch: z.string().optional() },
  async ({ limit, branch }) => {
    const output = execSync(`git log --oneline -n ${limit} ${branch ?? ""}`, { encoding: "utf-8" });
    return { content: [{ type: "text", text: output }] };
  }
);

// 注册工具：git_push（标注为 destructive）
server.tool(
  "git_push",
  "推送到远程仓库",
  { remote: z.string().default("origin"), branch: z.string().optional(), force: z.boolean().default(false) },
  async ({ remote, branch, force }) => {
    const output = execSync(`git push ${remote} ${branch ?? ""} ${force ? "--force" : ""}`, { encoding: "utf-8" });
    return { content: [{ type: "text", text: output }] };
  },
  { annotations: { destructiveHint: true } }  // Host 会弹窗确认
);

// 启动
const transport = new StdioServerTransport();
await server.connect(transport);
```

### 注册 Resources（可选）

```typescript
server.resource(
  "repo-info",
  "git://repo/info",
  { description: "当前 Git 仓库的基本信息" },
  async () => ({
    contents: [{
      uri: "git://repo/info",
      text: JSON.stringify({
        branch: execSync("git branch --show-current", { encoding: "utf-8" }).trim(),
        remote: execSync("git remote get-url origin", { encoding: "utf-8" }).trim(),
      }),
      mimeType: "application/json",
    }],
  })
);
```

### 配置 Host 使用（本地 stdio 模式）

```json
{
  "mcpServers": {
    "git": {
      "command": "node",
      "args": ["./git-mcp-server/dist/index.js"]
    }
  }
}
```

### 远程 Server 实现（Spring Boot）

以上 TypeScript 示例是本地 stdio 模式。远程 Server 需要实现 Streamable HTTP 传输——暴露一个 HTTP 端点，接收 JSON-RPC 请求，返回 JSON-RPC 响应（或 SSE 流）。

Spring AI 提供了开箱即用的 MCP Server Starter：

**1. Maven 依赖**

```xml
<!-- Servlet 模式（Streamable HTTP） -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-mcp-server-webmvc-spring-boot-starter</artifactId>
</dependency>
```

**2. application.yml**

```yaml
spring:
  ai:
    mcp:
      server:
        name: my-mcp-server
        version: 1.0.0
        type: SYNC          # ASYNC 用于响应式场景
```

**3. 注册工具**

用 `@Tool` 注解标记方法，Spring 自动将其注册为 MCP 工具：

```java
@Component
public class GitTools {

    @Tool(description = "查看 Git 提交历史", name = "git_log")
    public String gitLog(
        @ToolParam(description = "返回的提交数量") int limit,
        @ToolParam(description = "指定分支") String branch
    ) {
        String cmd = String.format("git log --oneline -n %d %s", limit, branch != null ? branch : "");
        return exec(cmd);
    }

    @Tool(description = "推送到远程仓库", name = "git_push",
          annotations = @ToolAnnotations(destructiveHint = true))
    public String gitPush(
        @ToolParam(description = "远程仓库名") String remote,
        @ToolParam(description = "是否强制推送") boolean force
    ) {
        String cmd = String.format("git push %s%s", remote, force ? " --force" : "");
        return exec(cmd);
    }
}
```

**4. 启动**

标准 Spring Boot 应用，启动后自动暴露 `/mcp` 端点：

```java
@SpringBootApplication
public class McpServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(McpServerApplication.class, args);
    }
}
```

启动后访问 `http://localhost:8080/mcp`，用 POST 发 JSON-RPC 即可通信。

**Starter 内部做了什么**

启动时：

```
1. 自动创建 McpServer 实例（等价于 TypeScript 的 new McpServer()）
2. 扫描所有 @Component 类，找到 @Tool 标注的方法
3. 从 @ToolParam + Java 类型自动生成 JSON Schema（等价于 TypeScript 的 zod schema）
4. 将每个方法注册为 MCP 工具（name/description/inputSchema/handler）
5. 在 /mcp 路径注册 POST 端点，接入 Streamable HTTP 传输层
```

收到请求时：

```
POST /mcp → 解析 JSON-RPC
  ├─ method: "initialize"  → 握手，返回 capabilities
  ├─ method: "tools/list"  → 返回已注册的工具清单
  └─ method: "tools/call"  → 从 params.name 找到对应方法
       ├─ 反序列化 params.arguments → Java 方法参数
       ├─ 反射调用 @Tool 方法
       └─ 将返回值包装为 JSON-RPC Response
```

和 TypeScript SDK 的对应关系：

| TypeScript（手动） | Spring Boot（自动） |
| --- | --- |
| `new McpServer()` | Starter 自动创建 |
| `server.tool("name", schema, handler)` | `@Tool` 注解 + 组件扫描 |
| `z.object({ ... })` 定义参数 | `@ToolParam` + Java 类型推断 |
| `new StdioServerTransport()` | `spring-ai-mcp-server-webmvc` 自动配置 |
| `server.connect(transport)` | Spring Boot 启动时自动连接 |

**5. 在 Claude 中配置为远程 Server**

```json
{
  "mcpServers": {
    "my-git-server": {
      "type": "url",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

### 开发流程

```
1. npm init && npm install @modelcontextprotocol/sdk zod
2. 编写 src/index.ts（注册工具、资源）
3. npx tsc 编译
4. 用 MCP Inspector 调试：npx @modelcontextprotocol/inspector node dist/index.js
5. 在 Host 中配置 .mcp.json
6. 重启 Host，让 LLM 调用测试
```

**调试要点**

- Inspector 展示所有注册的工具，可直接手动调用测试
- stderr 输出调试日志，stdout 只能走 JSON-RPC（任何 `print()` 都会搞烂协议）
- `inputSchema` 写错会导致 LLM 传参失败，用 Inspector 验证
- `description` 写清楚，LLM 靠它决定什么时候调用


## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

对发散的自由捕捉、精确化

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

记录回顾、使用文档时，遇到的困惑。Q&A 并列排布，每个问题直击要害，用分隔线区分，语言简洁朴素。

**Q1：MCP 通信基于 JSON-RPC 2.0，这东西怎么理解？**

极简远程调用协议，就三种消息：Request（有 id，等回复）、Response（id 对应哪个 Request）、Notification（没 id，火-and-forget）。传输层（stdio / HTTP）只负责搬运，消息格式始终是 JSON-RPC 2.0。

**Q2：为什么 MCP 选 JSON-RPC 2.0 而不是 REST？**

关键在**对等性**。REST 下只有 Client 能发 Request，Server 只能被动回答。JSON-RPC 2.0 双方都能发 Request——Server 能反向调 Client，才能支撑 Elicitation（Server 反问"要合并到哪个分支？"）和 Sampling（Server 请求 LLM 生成内容）。REST 做不到这个。

**Q3：Host 为什么是 Hub-and-Spoke 的中心？Host 不是本地应用吗？**

Host 确实是本地应用（Claude Desktop、VS Code、Cursor）。叫 "Host" 是因为它承载（host）了 LLM 和所有 Client。

它在中心不是因为强大，而是因为**安全必须经过它**——用户只和 Host 交互，不直接接触任何 Server。Server 返回的数据，Host 决定要不要给 LLM 看；LLM 想调用工具，Host 先问用户"你确定吗？"。就像家里的路由器——所有流量经过它，不是因为它最聪明，而是它是你家网络的唯一入口。

## 🗄️ 修订记录

重要修订记录

## 🛠️ 实践经历

记录实践经历： demo + 工作经历 + 第三方优秀经验反思

## ⚙️ prompt

探究该文档模块过程中的 prompt 记录

