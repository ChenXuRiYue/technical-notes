# 📌 subagent

总结 Claude 中的：subagent 机制

官方文档：https://code.claude.com/docs/zh-CN/sub-agents



## 📄 Claude subagent

考虑到一种通用的事实场景：
对任务拆分，有一些特定的任务是不依赖上下文的，它们可以开一个专用的 agent 会话来处理。

Subagents 是处理特定类型任务的专门 AI 助手。有以下优势：

- **控制成本**：简单任务使用更快、更便宜的模型
- **保留上下文**：探索和实现保持到主对话之外
- 跨项目重用 agent 配置
- 专门化行为，为特定问题使用专注的系统提示词
- 强制执行约束，限制 subagent 可以使用的工具



## 📄 内置 subagents

(可能后续会补充，截止 4.16)

### 🔖 Explore

一个快速的、只读的代理，针对搜索和分析代码库进行了优化。

当 Claude 需要搜索或理解代码库而不进行更改时，它会委托给 Explore。这样可以将探索结果保持在主对话上下文之外

调用方式：

1. 显式调用

- `/agents` 命令
- 选择或调用 Explore 子代理 

2. 对话中指定使用子代理：

```markdown
use the explore subagent to analyze the codebase
```

### 🔖 Plan

一个研究代理，在 [plan mode](https://code.claude.com/docs/zh-CN/common-workflows#use-plan-mode-for-safe-code-analysis) 期间使用，以在呈现计划之前收集上下文。

- **Model**: 从主对话继承
- **Tools**: 只读工具（拒绝访问 Write 和 Edit 工具）
- **Purpose**: 用于规划的代码库研究

当您处于 plan mode 并且 Claude 需要理解您的代码库时，它会将研究委托给 Plan subagent。这可以防止无限嵌套（subagents 无法生成其他 subagents），同时仍然收集必要的上下文。



### 🔖 General-purpose

当任务需要探索和修改、复杂推理来解释结果或多个依赖步骤时，Claude 会委托给 general-purpose。



### 🔖 Other

Claude Code 包括用于特定任务的其他辅助代理。这些通常会自动调用，因此您不需要直接使用它们。

| Agent             | Model  | Claude 何时使用它                         |
| :---------------- | :----- | :---------------------------------------- |
| statusline-setup  | Sonnet | 当您运行 `/statusline` 来配置您的状态行时 |
| Claude Code Guide | Haiku  | 当您提出关于 Claude Code 功能的问题时     |



## 📄 自定义 subagent

### 🔖 /agents 命令

- 查看所有可用 subagents
- 使用引导式设置 或 Claude 生成新的 subagents
- 编辑现有 subagent 配置和工具访问
- 删除自定义 subagents
- 查看当存在重复时哪些 subagents 是活跃的

### 🔖 创建

简要说明：详细操作看官方文档

1. 运行 `/agents`
2. 选择 agent （create new agent）-> personal
3. Claude 生成（Generate With Claude）出现提示时，描述 subagent
4. 选择工具 （如果只读，只选 Read-only tools）全选则继承主对话
5. 选择模型
6. 选择颜色（通过背景颜色识别）
7. 配置内存
8. 保存并尝试

### 🔖 配置
**subagent 范围**

- 项目 subagents (.claude/agents/) 
- 用户 subagents (./.claude/agents/) 所有项目可用的个人 subagents
- Cli 定义的 subagents
  在启动 Claude Code 时作为 JSON 传递。它们仅存在于该会话中，不会保存到磁盘，使其对快速测试或自动化脚本很有用
- 托管 subagents 由组织管理员部署
  - managed setting 部署
  - 托管定义优先于具有相同名称的项目和用户 subagents。
- plugin subagents 来自已安装的 p plugins。

### 🔖 subagent 文件编写

Subagent 是基于 YAML frontematter 

一个简单的例子：

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

结构分析：

- Frontmatter 字段 ： 类似于 头文件的 KV （name、description）有哪些值具体看官方文档
- 系统提示词

📝 控制 subagent 能力

- 可用工具控制 tools 限定
- 限制可以生成 哪些 subagent `tools: Agent(worker, researcher), Read, Bash `
- MCP 服务期限定于 subagent

📝 权限模式

- PermissionMode：控制 subagent 如何处理权限提示

📝 将 Skills 加载到 subagent 上下文

```markdown
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

📝 启用持久缓存

`memory` 字段为 subagent 提供一个在对话中幸存的持久目录

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

给定不同的值，内容持久化位置不同，生效的位置也不同

| Scope     | Location                                      | 使用时机                                          |
| :-------- | :-------------------------------------------- | :------------------------------------------------ |
| `user`    | `~/.claude/agent-memory/<name-of-agent>/`     | subagent 应该在所有项目中记住学习                 |
| `project` | `.claude/agent-memory/<name-of-agent>/`       | subagent 的知识是特定于项目的并可通过版本控制共享 |
| `local`   | `.claude/agent-memory-local/<name-of-agent>/` | subagent 的知识是特定于项目的但不应检入版本控制   |

另外还有一些配置提示：

1. 推荐什么范围
2. 怎么让 subagent 持续维护数据库

详情看 官方文档

### 🔖 使用 hooks 的条件规则

使用 hooks 可以更动态地控制工具使用，在 `PreToolUse`  hooks 执行前验证操作。

```yml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

如下：每次执行 Bash 命令前运行 command 中指定脚本。

Ps：claude  还提供了 stdin 将 hook 输入作为 Json 传递给 hook 命令。



### 🔖 禁止特定 subagents

可以配置内容来防止 Claude 使用特定 subagents.



### 🔖 为 subagents 定义 hooks

Subagents 也有生命周期模型，可以定义一些 hooks。配置方式有两种

1. subagent 的 frontmatter 中
2. Settings.json 中

截点有以下几个角度：

使用工具前后 + 任务完成后

demo：

```yaml
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```



## 📄 使用 subagents

- 理解自动委托

  Claude 根据您请求中的任务描述、subagent 配置中的 `description` 字段和当前上下文自动委托任务。要鼓励主动委托，在您的 subagent 的 description 字段中包含”use proactively”之类的短语。

- 显示调用 subagents

  - 自然语言，引导 claude 委托

    >Use the test-runner subagent to fix failing tests
    >Have the code-reviewer subagent look at my recent changes

  - @-mention: 保证 subagent 为一个任务运行

    >@"code-reviewer (agent)" look at the auth changes

  - 会话范围：整个绘画使用该 subagent 的系统提示，工具限制和模型

    >claude --agent code-reviewer

### 🔖 前台或后台运行 subagents

概念澄清：

- **前台 subagents** 阻塞主对话直到完成。权限提示和澄清问题（如 [`AskUserQuestion`](https://code.claude.com/docs/zh-CN/tools-reference)）会传递给您。
- **后台 subagents** 在您继续工作时并发运行。启动前，Claude Code 会提示您 subagent 需要的任何工具权限，确保它具有必要的批准。一旦运行，subagent 继承这些权限并自动拒绝任何未预先批准的内容。如果后台 subagent 需要提出澄清问题，该工具调用失败，但 subagent 继续。

启用后台 subagents 的方式：

- 要求 Claude "run this in the backgroupnd"
- 按照 Ctrl + B 将运行中的任务放在后台

## 📄 实践推荐

**隔离高容量模式：** 隔离产生大量输出的操作。运行测试、获取文档或处理日志文件可能会消耗大量上下文。通过将这些委托给 subagent，详细输出保留在 subagent 的上下文中，而只有相关摘要返回到您的主对话。

```txt
Use a subagent to run the test suite and report only the failing tests with their error messages
```

**运行并研究：** 对于独立的调查，生成多个 subagents 以同时工作：

```txt
Research the authentication, database, and API modules in parallel using separate subagents
```

**链接 subagents：** 对于多步骤工作流，要求 Claude 按顺序使用 subagents。每个 subagent 完成其任务并将结果返回给 Claude，然后将相关上下文传递给下一个 subagent

```txt
Use the code-reviewer subagent to find performance issues, then use the optimizer subagent to fix them
```



在以下情况下使用 **主对话**：

- 任务需要频繁的来回或迭代细化
- 多个阶段共享重要上下文（规划 → 实现 → 测试）
- 您正在进行快速、有针对性的更改
- 延迟很重要。Subagents 从头开始，可能需要时间来收集上下文

在以下情况下使用 **subagents**：

- 任务产生您不需要在主上下文中的详细输出
- 您想强制执行特定的工具限制或权限
- 工作是自包含的，可以返回摘要



## 📄 示例 Subagent

- 代码审查者
- 调试器
- 数据科学家
- 数据库查询检查器

详看官方文档

## 🌳 生长思考

对发散的自由捕捉、精确化

## 💭 反复绊脚

1. Plan mode 和 Plan Subagent 的区别是什么

   - Plan Mode 是一种工作模式或状态，是一种操作环境
   - Plan subagent 是一个具体的执行实体

   >文档说"Plan subagent在plan mode期间使用"是因为：
   >
   >1. **分工明确**：Plan Mode是触发条件，Plan Subagent是执行者
   >2. **职责分离**：Mode定义环境规则，Subagent执行具体任务
   >3. **防止递归**：明确说明subagent不能生成其他subagent，避免无限嵌套

## 🗺️ 修订记录

重要修订记录

## 🛠️ 实践经历

记录实践经历： demo + 工作经历 + 第三方优秀经验反思



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



