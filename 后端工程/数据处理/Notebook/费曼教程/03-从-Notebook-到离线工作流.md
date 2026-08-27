# 📌 把 Notebook 发布为可调度的离线作业

急减速 Notebook 已经稳定筛出 `E101`、`E103`。团队接下来希望每天自动运行同一规则，把结果交给场景切片节点。工程师点击“配置调度”后，数据工场会固定代码版本、参数、环境、资源、输入输出和失败策略，建立一个可重复执行的 Notebook 作业。

学完本篇，你应该能解释“配置调度”创建了什么，并判断修改 Notebook 开发页面中的源文件后，离线作业会执行旧内容还是新内容。

## 📄 交互 Runtime 与离线作业的生命周期

| 维度 | Notebook 开发页面 | AI 数据开发中的 Notebook 作业 |
| --- | --- | --- |
| 主要目的 | 逐 Cell 探索、验证和查看结果 | 按固定配置完整执行 Notebook |
| 代码来源 | 当前编辑的 Notebook 文件 | 复制到 AI 数据开发的项目文件快照 |
| 计算会话 | 手动启动、连接和切换 Runtime | 每次执行由 Spark 或 Ray Runner 创建计算任务 |
| 参数 | 参数 Cell 中的默认值 | `Arguments` 覆盖默认值 |
| 输出 | 页面结果、临时文件 | 声明的 `outputFiles`，供工作流后续节点读取 |
| 运维 | Runtime 状态和 Cell 日志 | 工作流实例、节点状态、重试、超时和输出 |

Notebook 开发页面用于逐步验证规则，离线作业用于按固定配置重复执行。两者使用同一种 `.ipynb` 文件，但保存的代码版本和运行周期彼此独立。

## 📄 两条创建路径最终到达同一种作业

集团文档给出两条入口：

1. 工程师在 Notebook 开发页面完成调试，点击“配置调度”。平台用当前 Notebook 内容创建离线作业。
2. 在 AI 数据开发中直接新建 Notebook 作业，再选择已经复制到项目文件中的 `.ipynb`。

两条路径最终都得到一个工作流节点。节点名称只能使用小写字母、数字和下划线，入口文件只支持 `.ipynb`。

## 📄 调度保存的是作业快照

第一次配置调度时，源 Notebook 内容进入 Notebook 作业。之后继续编辑开发页面中的源文件，离线作业不会自动把每次编辑当成已发布版本。

更新路径是：

```text
编辑已调度 Notebook
  -> 在 Notebook 作业中“对比当前 Notebook 文件”
  -> 更新作业中的 Notebook 文件
  -> 保存并重新上线工作流
```

先预测：上午 10 点把阈值从 `20` 改为 `15`，交互运行命中更多事件，但没有更新和上线作业。晚上调度执行哪个阈值？

答案是作业快照中的旧版本。交互文件的新内容只证明开发区发生了变化，还没有证明离线作业已经发布新版本。

这个边界接近编译型语言中的“源码已经修改，但线上仍运行旧制品”。区别是这里的制品仍是 Notebook 文件快照和作业配置。

## 📄 工作流节点声明哪些运行条件

下面是根据集团文档简化的阅读示例，不应直接复制到生产。真实创建或修改前要获取目标空间最新插件 Schema，并通过平台校验：

```yaml
tasks:
  - id: mine_hard_braking
    type: io.kestra.plugin.scripts.notebook.Notebook
    namespace: dt-10008-notebook-demo-18069
    timeout: PT48H
    retry:
      type: constant
      interval: PT5M
      maxAttempts: 1

    baseEnvironment: python3_9-scala2_12-spark3_3-v2
    mainNotebook: git/hard-braking/hard-braking.ipynb
    namespaceFiles:
      enabled: true
      include:
        - /git/hard-braking/hard-braking.ipynb

    notebookRunner:
      type: spark
      sparkConfiguration:
        queue: root.development.example
        driverMemory: 6G
        executorMemory: 3G
        dynamicAllocationEnabled: true
        dynamicAllocationMinExecutors: 1
        dynamicAllocationMaxExecutors: 20

    outputFiles:
      - git/hard-braking/scene-manifest.csv
```

关键字段的责任：

| 字段 | 回答的问题 |
| --- | --- |
| `mainNotebook` | 从哪个 `.ipynb` 开始执行？ |
| `namespaceFiles` | 哪些项目文件要进入作业工作目录？ |
| `baseEnvironment` | Python、Scala、Spark 等基础版本是什么？ |
| `notebookRunner` | 使用 Spark 还是 Ray，资源从哪里取得？ |
| `retry` | 临时失败后何时、最多重新执行几次？ |
| `timeout` | 最长允许执行多久？ |
| `outputFiles` | 哪些生成文件要登记为节点输出？ |

资源字段和队列名会随空间、区域及平台版本变化。集团 skill 中曾同时出现 `io.kestra.plugin.scripts.notebook.Notebook` 与 `io.kestra.plugin.dt.notebook.Notebook` 两种类型；当前产品文档的完整示例使用前者。实际创建时以最新 Schema 为准，可以避免把历史文档中的类名写进新工作流。

## 📄 CWD 决定相对路径落在哪里

集团文档规定：Notebook 文件所在目录是当前工作目录 CWD。

假设入口文件是：

```text
git/hard-braking/hard-braking.ipynb
```

Notebook 中写：

```python
with open("scene-manifest.csv", "w") as output:
    output.write("event_id\nE101\nE103\n")
```

那么作业配置需要按平台实际生成路径声明输出，例如：

```yaml
outputFiles:
  - git/hard-braking/scene-manifest.csv
```

后续节点通过当前平台支持的输出表达式引用它。集团文档示例为：

```text
outputs["mine_hard_braking"]["outputFiles"]["git/hard-braking/scene-manifest.csv"]
```

路径必须同时满足两件事：Notebook 确实在 CWD 下生成文件，作业也用相同规范把它列入 `outputFiles`。只写文件而不声明输出，下游节点不会自动知道它是工作流产物。

## 📄 工作流把多个责任连接起来

一个完整的场景挖掘 Flow 可以包含：

```text
Sensor：确认当天数据已到齐
  -> Notebook：筛选急减速候选并输出清单
  -> 切片任务：沿 raw_log_path 生成片段
  -> DataOutput：发送结果或登记数据集
```

工作流负责执行顺序和状态传播，Notebook 负责场景规则。业务逻辑集中在 Notebook 或项目代码中，编排层声明输入、输出、资源、重试和超时。

重试意味着同一 Notebook 可能再次运行，所以输出策略要能抵抗重复执行。覆盖同一日期的结果、使用执行 ID 隔离目录，或在下游按 `event_id` 去重，都是需要明确选择的幂等策略。

## 📄 运维时观察什么

保存并执行 Flow 后，至少记录：

- Flow ID 与工作流 revision。
- executionId 和 Notebook 节点状态。
- 实际参数、基础环境、Spark/Ray 资源配置。
- 输入日期、输入表或 Fileset。
- 输出文件路径与候选数量。
- 失败时的节点日志、重试次数和超时状态。

工作流成功说明声明的节点已经按平台状态机完成。业务结果是否正确还要检查输出行数、样本和下游消费证据。

## 📄 费曼检查

向一位熟悉 CI/CD 的同事解释：

> 源 Notebook、Notebook 作业中的项目文件、工作流 revision 和一次 execution 分别记录了哪一层状态？

如果解释里“保存文件”和“上线作业”是同一个动作，请回到[调度保存的是作业快照](#-调度保存的是作业快照)。如果找不到下游文件，请回到[CWD 决定相对路径落在哪里](#-cwd-决定相对路径落在哪里)。

---

[上一篇：交互式场景挖掘](02-交互式场景挖掘.md) | [返回教程目录](README.md) | [下一篇：参数 Cell 的注入机制](04-参数-Cell-注入.md)

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-08-14：建立交互文件、作业快照、工作流执行和输出文件之间的版本与责任链。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- [集团：AI数据开发-Notebook作业](https://mi.feishu.cn/wiki/NzoRwUNj5iwhomknpk3c3YFMnee)
- [集团：Notebook 使用指南](https://mi.feishu.cn/wiki/Qk7WwAwPyinAaSkvyhjc8reenzf)
