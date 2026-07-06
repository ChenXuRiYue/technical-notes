# Knowledge Distillation Notes Skill

> 记录时间: 2026-07-06
> 所属: 人工智能 / 提效经验 / skill
> Skill 名称: `knowledge-distillation-notes`

## 这个 skill 固化的思想

我的理解是: 学习一个 vibe coding 项目时, 不应该只堆项目笔记, 也不应该一上来就抽象成通用理论。

更好的模式是三层沉淀:

```text
1. 开源项目 / GitTributary / 技术经验
   项目为出发点到知识

2. 语言基础
   偏语法基础特性

3. 全栈工程
   偏对技术框架的理解
```

项目现场提供真实问题, 语言基础补基本功, 全栈工程沉淀框架和架构判断。

## 为什么要形成 skill

这套策略是一个长期复用的协作模式。

如果每次都要重新告诉 Codex:

```text
先从项目导读经验写起,
再抽语言基础,
再抽全栈工程,
并区分三者侧重点。
```

成本会很高, 也容易在长会话中漂移。

所以将它做成 Codex skill:

```text
~/.codex/skills/knowledge-distillation-notes
```

以后只要任务涉及:

```text
项目导读
技术经验沉淀
语言基础抽取
全栈工程抽取
知识沉淀策略
```

Codex 就可以复用这套方法。

## 三层笔记边界

### 1. 项目导读经验

路径:

```text
technical-note/开源项目/GitTributary/技术经验/
```

侧重点:

```text
从 GitTributary 的具体代码、具体文件、具体用户动作出发。
```

适合写:

```text
App.tsx 在项目里承担什么职责
GitPanel 如何组织 Git 模块
某个按钮点击后状态如何变化
invoke("xxx") 在当前项目里通向哪里
```

### 2. 语言基础

路径:

```text
technical-note/语言基础/
```

侧重点:

```text
语法、类型系统、语言机制。
```

适合写:

```text
TypeScript import/export
interface 与 type
unknown / Partial / satisfies
React JSX 基础
Rust Result / Option / trait
```

要求:

```text
脱离具体项目, 用更小的例子讲清规则。
```

### 3. 全栈工程

路径:

```text
technical-note/全栈工程/
```

侧重点:

```text
框架理解、架构模型、工程组织方式。
```

适合写:

```text
React 组件模型
React state 和重新渲染
Vite 应用入口
Tauri invoke 前后端桥接
插件式 Shell 设计
本地状态持久化
```

要求:

```text
讲清技术框架的心智模型, 而不是只解释语法。
```

## 复用流程

每次读项目代码时:

```text
1. 从具体文件或用户动作开始
2. 先写项目现场和项目链路
3. 识别当场需要补的语法知识
4. 识别可以抽象成工程模型的知识
5. 分别沉淀到对应目录
6. 在项目导读中回链语言基础和全栈工程
```

判断放哪一层:

```text
只在 GitTributary 语境里成立?
  -> 开源项目/GitTributary/技术经验

离开项目仍然是语言规则?
  -> 语言基础

离开项目仍然是框架/架构经验?
  -> 全栈工程
```

## Skill 使用方式

显式调用:

```text
Use $knowledge-distillation-notes to ...
```

自然语言触发:

```text
帮我把这次项目导读沉淀成笔记
从这个文件里抽取语言基础和全栈工程知识
把技术经验整理到 GitTributary/技术经验
形成项目到知识的沉淀
```

默认输出策略:

```text
先项目导读, 再语言基础, 再全栈工程。
```

默认不做的事:

```text
不把所有知识混在一篇项目笔记里。
不把语言基础写成项目日志。
不把全栈工程写成语法手册。
```

## 当前落地文件

Codex skill:

```text
/Users/mi/.codex/skills/knowledge-distillation-notes/SKILL.md
```

项目本地指令:

```text
/Users/mi/rust_code/GitTributary/AGENTS.md
```

方法论记录:

```text
technical-note/人工智能/提效经验/skill/knowledge-distillation-notes.md
```

GitTributary 项目策略文档:

```text
technical-note/开源项目/GitTributary/技术经验/知识沉淀策略与复用规则.md
```
