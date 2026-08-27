# 📌 Spark 怎样读写 Iceberg

Spark 提供计算资源、SQL 解析和任务调度。Iceberg 提供表的 Schema、Snapshot、文件清单和提交规则。Spark 通过 Iceberg Runtime 把计算计划与表格式连接起来。

> Iceberg 的文件层级、Snapshot 和 Catalog 已在 [Iceberg 教程](../../../数据存储/Iceberg/教程/README.md) 详细讲解。本篇只追踪 Spark 在读写链路中做了什么。

## 📄 三段表名怎样找到数据

`prod.sales.orders` 可以拆为：

```text
prod       sales       orders
Catalog    Namespace   Table
```

`prod` 是当前 Spark 运行环境中的 Catalog 别名。这个别名的 Spark 配置指定 Iceberg Catalog 实现、服务地址、Warehouse 和认证方式。

```text
Spark 中的 prod 配置
  -> Iceberg Catalog 后端
  -> sales.orders 的当前 Metadata JSON
  -> 查询选定的 Snapshot
  -> Manifest List / Manifest
  -> 候选 Data File / Delete File
```

表名解析在 Driver 规划阶段发生。Executor 获得的扫描 Task 已包含要读的文件和范围，它们使用集群配置的存储凭证直接读取对象存储或 HDFS。

## 📄 读取链：从 Snapshot 到 Task

日报任务带有一天的时间条件。读取链按这个顺序缩小数据：

1. Driver 通过 Catalog 加载 `orders` 的当前元数据。
2. 查询规划绑定一个 Snapshot，后续扫描以这个版本为一致视图。
3. Iceberg 用日期条件比较分区摘要和列统计，排除不可能命中的 Manifest 与文件。
4. Spark 将保留的文件范围组织成扫描分区与 Task。
5. Executor 按列读取 Parquet 等 Data File，应用 Delete File 和剩余过滤条件。

查询开始后有其他写者提交新 Snapshot 时，这份已规划的查询继续沿原 Snapshot 读取，从而避免同一次扫描混合两个表版本。

## 📄 写入链：从 Task 到新 Snapshot

```text
Executor Task
  -> 写新 Data File
  -> 返回文件路径、分区值、行数和统计
Driver
  -> 汇总所有成功 Task 的文件信息
Iceberg
  -> 生成 Manifest、Manifest List 和新表元数据
Catalog
  -> 原子地把当前入口从旧元数据切到新元数据
```

Executor 把 Parquet 写成功只证明数据文件已存在。Catalog 提交成功后，新 Snapshot 才成为新查询的表版本。在文件写完与 Snapshot 提交之间失败，可能留下未被有效元数据引用的文件，后续由 Iceberg 安全维护流程识别孤儿文件。

## 📄 为什么日报使用动态分区覆盖

目标表按 `report_date` 分区。一次任务只产生 `2026-08-12` 的结果：

```java
result.writeTo("prod.analytics.daily_order_report")
        .overwritePartitions();
```

DataFrameWriterV2 的 `overwritePartitions()` 表达：覆盖这份 DataFrame 实际包含的目标分区。同一日期重试时，新 Snapshot 替换该日期的文件，其他日期继续引用原文件。

这份幂等性依赖两个前提：

1. DataFrame 只含本次允许覆盖的 `report_date`。
2. 目标表的分区规则和 Spark/Iceberg 版本已在隔离表中验证。

一个条件漏掉边界，让 DataFrame 同时带上两天数据时，两天分区都会进入本次覆盖范围。因此写入前要验证最小、最大 `report_date` 和分区数。

## 📄 Runtime 与版本链

Spark 需要加载与自身 Spark 主版本和 Scala 二进制版本匹配的 Iceberg Runtime。Artifact 名中常能看到这两个坐标：

```text
iceberg-spark-runtime-3.5_2.12
                      |    |
                  Spark  Scala
```

生产中记录并联合验证：

- Spark 版本与 Scala 二进制版本。
- Iceberg Runtime 版本。
- Catalog 类型与服务版本。
- 表 `format-version` 与实际用到的特性。
- 存储连接器、认证和文件系统客户端。

版本不匹配常表现为 `ClassNotFoundException`、`NoSuchMethodError`、扩展 SQL 不可用或某个表特性不被当前引擎识别。使用时按目标环境的实际版本查阅 [Iceberg multi-engine support](https://iceberg.apache.org/multi-engine-support/)，并在隔离表运行建表、读、写、时间旅行和重试用例。

## 📄 先预测再看答案

三个 Executor 已经成功写出 `A.parquet`、`B.parquet`、`C.parquet`，Driver 在 Catalog 提交前崩溃。

**预测：新查询能看到这三个文件中的行吗？**

不能。当前 Metadata JSON 仍然指向旧 Snapshot，新文件没有进入已发布的有效文件集合。

改变一个条件：Catalog 提交新 Snapshot 后，Submitter 在回写任务库前崩溃。表结果已可见，Spring 任务状态可能仍是 `RUNNING`。这需要下一篇的状态校准机制修复。

## 📄 实践入口

要亲手观察建表、插入、Snapshot、时间旅行和 `MERGE INTO`，进入 [Iceberg Spark SQL 实战](../../../数据存储/Iceberg/教程/04-Spark-SQL实战.md)。实战先核对 Spark、Scala 和 Iceberg Runtime 版本，不盲目复用过期坐标。

---

[上一篇：SQL、DataFrame 与惰性计算](02-SQL-DataFrame-与惰性计算.md) | [返回 Spark 目录](README.md) | [下一篇：Spring 异步任务体系](04-Spring-异步任务体系.md)

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-08-13：补齐 Spark 读取 Snapshot、写 Data File 和提交新 Snapshot 的闭环。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- [Apache Iceberg Spark](https://iceberg.apache.org/docs/latest/spark-getting-started/)
- [Apache Iceberg Writes](https://iceberg.apache.org/docs/latest/spark-writes/)
- [Apache Iceberg Multi-engine Support](https://iceberg.apache.org/multi-engine-support/)
