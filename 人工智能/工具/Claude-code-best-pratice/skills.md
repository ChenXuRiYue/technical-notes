# 📌 SKILLS

Claude-code-best-practice Skills 教程

https://github.com/shanraisshan/claude-code-best-practice?tab=readme-ov-file

官方文档：https://code.claude.com/docs/zh-CN/features-overview

了解何时使用 CLAUDE.md、Skills、subagents、hooks、MCP 和 plugins。

官方文档对 skillsd的讲述

https://code.claude.com/docs/zh-CN/skills

## 📄 SKILL 基础

通用性 SKILL 定义： [SKILL.md](../../知识专项/skill/SKILL.md) 

## 📄 扩展 Claude Code

**Lab: 安装几个常用插件**
一个 git skill

## 📄 自定义 SKILL

### 🔖 SkILL.md

1. 个人 skills 文件夹中创建目录

   `mkdir -p ~./claude/skills/{skill-name}`

2. 编写 SKILL.md

   - YAML frontmatter `描述何时使用该 skill`。一个 demo：explain-code

     ```markdown
     ---
     name: explain-code
     description: Explains code with visual diagrams and analogies. Use when explaining how code works, teaching about a codebase, or when the user asks "how does this work?"
     ---
     
     When explaining code, always include:
     
     1. **Start with an analogy**: Compare the code to something from everyday life
     2. **Draw a diagram**: Use ASCII art to show the flow, structure, or relationships
     3. **Walk through the code**: Explain step-by-step what happens
     4. **Highlight a gotcha**: What's a common mistake or misconception?
     
     Keep explanations conversational. For complex concepts, use multiple analogies.
     ```
     Frontmatter 参考：
     | 字段                       | 必需 | 描述                                                         |
     | :------------------------- | :--- | :----------------------------------------------------------- |
     | `name`                     | 否   | Skill 的显示名称。如果省略，使用目录名称。仅小写字母、数字和连字符（最多 64 个字符）。 |
     | `description`              | 推荐 | Skill 的功能以及何时使用它。Claude 使用它来决定何时应用该 skill。如果省略，使用 markdown 内容的第一段。前置关键用例，因为每个条目在技能列表中被截断为 250 个字符以减少上下文使用。 |
     | `argument-hint`            | 否   | 自动完成期间显示的提示，指示预期的参数。示例：`[issue-number]` 或 `[filename] [format]`。 |
     | `disable-model-invocation` | 否   | 设置为 `true` 以防止 Claude 自动加载此 skill。用于你想使用 `/name` 手动触发的工作流。默认值：`false`。 |
     | `user-invocable`           | 否   | 设置为 `false` 以从 `/` 菜单中隐藏。用于用户不应直接调用的背景知识。默认值：`true`。 |
     | `allowed-tools`            | 否   | 当此 skill 处于活动状态时，Claude 可以使用而无需请求权限的工具。接受空格分隔的字符串或 YAML 列表。 |
     | `model`                    | 否   | 当此 skill 处于活动状态时要使用的模型。                      |
     | `effort`                   | 否   | 当此 skill 处于活动状态时的[工作量级别](https://code.claude.com/docs/zh-CN/model-config#adjust-effort-level)。覆盖会话工作量级别。默认值：继承自会话。选项：`low`、`medium`、`high`、`max`（仅 Opus 4.6）。 |
     | `context`                  | 否   | 设置为 `fork` 以在分叉的 subagent 上下文中运行。             |
     | `agent`                    | 否   | 当设置 `context: fork` 时要使用的 subagent 类型。            |
     | `hooks`                    | 否   | 限定于此 skill 生命周期的 hooks。有关配置格式，请参阅 [Skills 和代理中的 Hooks](https://code.claude.com/docs/zh-CN/hooks#hooks-in-skills-and-agents)。 |
     | `paths`                    | 否   | Glob 模式，限制何时激活此 skill。接受逗号分隔的字符串或 YAML 列表。设置后，Claude 仅在处理与模式匹配的文件时自动加载该 skill。使用与[路径特定规则](https://code.claude.com/docs/zh-CN/memory#path-specific-rules)相同的格式。 |
     | `shell`                    | 否   | 用于此 skill 中 `!`command`` 块的 shell。接受 `bash`（默认）或 `powershell`。设置 `powershell` 在 Windows 上通过 PowerShell 运行内联 shell 命令。需要 `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`。 |

   - SKILL 支持 skill 内容中动态值的字符串替换。

     如下：$ARGUMENTS。替换值一般从命令行工具调用 skill、会话上下文，配置上下文中拿。claude 提供了不同的关键字。详看官方文档：

     ```makrdown
     ---
     name: session-logger
     description: Log activity for this session
     ---
     
     Log the following to logs/${CLAUDE_SESSION_ID}.log:
     
     $ARGUMENTS
     ```

### 🔖 Skill 作用域

![image-20260412140505095](https://raw.githubusercontent.com/ChenXuRiYue/image-cloud/main/global/image-20260412140505095.png)

当 skills 在各个级别共享相同的名称时，更高优先级的位置获胜：企业 > 个人 > 项目。



### 🔖 使用 Skills

调用方法：

- 直接如 SKILL.md 中描述的询问 How does this code work?
- 调用 skill 名称访问：`/explain-code ...`

### 🔖 **常用结构：**

```txt
my-skill/
├── SKILL.md           # 主要说明（必需）
├── template.md        # Claude 要填写的模板
├── examples/
│   └── sample.md      # 显示预期格式的示例输出
└── scripts/
    └── validate.sh    # Claude 可以执行的脚本
```

### 🔖 配置 skills

Skills 可以在其目录中包含多个文件。好处：

- SKILL.md 专注关键要点
- Claude 仅在需要时访问详细的参考资料

Demo：

**文件目录：**

```txt
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)
```

从 `SKILL.md` 中引用支持文件，以便 Claude 知道每个文件包含什么以及何时加载它

```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

## 📄 高级用法

### 🔖 注入动态上下文

!`<command>` 语法：将 skill 内容发送 Claude 之前运行 shell 命令。命令输出替换占位符，因此 Claude 接收实际数据，而不是命令本身。

如下：

```markdown
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

当此 skill 运行时：

1. 每个 `!`<command>`` 立即执行（在 Claude 看到任何内容之前）
2. 输出替换 skill 内容中的占位符
3. Claude 接收带有实际 PR 数据的完全呈现的提示

### 🔖 subagent 中运行 skills

当你想让 skill 在隔离中运行时，在你的 frontmatter 中添加 `context: fork`。skill 内容变成驱动 subagent 的提示。它将无法访问你的对话历史



## 📄 共享 skills

Skills 可以根据你的受众在不同范围内分发：

- **项目 skills**：将 `.claude/skills/` 提交到版本控制
- **插件**：在你的[插件](https://code.claude.com/docs/zh-CN/plugins)中创建 `skills/` 目录
- **托管**：通过[托管设置](https://code.claude.com/docs/zh-CN/settings#settings-files)部署组织范围内

## 🌳 生长思考

对发散的自由捕捉、精确化

## 💭 反复绊脚

记录回顾、使用文档时，遇到的困惑



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



