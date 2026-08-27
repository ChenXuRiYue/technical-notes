# 📌 Apache Iceberg：从数据文件到可靠的表

Apache Iceberg 是一种开放表格式。最朴素地说，它给散落在 S3、OSS、HDFS 等存储中的数据文件增加了一本**带版本的总账**：总账记录哪些文件属于当前表、表有哪些列，以及一次修改如何完整生效。

Spark、Flink、Trino 执行计算，S3/OSS/HDFS 保存文件，Iceberg 把这些文件组织成可安全读写和演进的表。三层各自独立扩展，共同组成完整的数据链路。

## 📄 这套教程怎样学

本系列按费曼学习法组织。每一篇都做五件事：

1. 从一个具体问题开始，观察现象并提出问题。
2. 用普通语言建立模型，再给正式术语。
3. 用同一张 `user_events` 表逐层验证模型。
4. 主动预测结果或解释反例，暴露理解缺口。
5. 最后不用原文措辞，向“只用过 MySQL 的同事”复述。

遇到陌生词时，先回到 [零基础前置课](00-零基础前置课.md)，确认自己能说明这个概念解决了什么问题。

### 🔖 费曼学习法的核心循环

费曼学习法通过主动解释暴露知识缺口，再用补学和验证完成纠错：

```text
选一个小问题
    |
    v
不看资料，向零基础的人解释或预测结果
    |
    v
发现跳步、含糊词、矛盾或答不出的“为什么”
    |
    v
只回去补这个缺口
    |
    v
换一个例子重新解释，并用操作或反例验证
```

例如，直接回答：“S0=[A,B]、S1=[A,B,C] 时，删除 B 会影响哪两个版本，为什么？”答不出时，缺口位于“Snapshot 如何引用文件”这一机制。类比和白话解释用于辅助理解，最终以能否推导具体结果为准。

## 📄 贯穿全篇的例子

教程一直使用用户事件表：

| event_id | user_id | event_type | event_time |
| --- | --- | --- | --- |
| 1 | 7 | `page_view` | 2026-08-01 10:00:00 |
| 2 | 7 | `purchase` | 2026-08-01 10:05:00 |

假设每天都有新事件，偶尔还要修正或删除旧事件。随着数据增长，我们依次遇到这些问题：

```text
文件越来越多，怎样知道哪些文件属于表？
          |
          v
写到一半失败，读者怎样避开半成品？
          |
          v
列名和分区变了，旧文件怎样继续读取？
          |
          v
怎样实际建表、写入、查询旧版本？
          |
          v
多个引擎怎样找到同一张表并安全提交？
          |
          v
小文件和旧快照越来越多，怎样维护？
```

## 📄 零基础学习路线

| 顺序 | 文档 | 学完应该能回答 |
| --- | --- | --- |
| 0 | [零基础前置课](00-零基础前置课.md) | 存储、文件格式、表格式和计算引擎分别做什么？数据湖、湖仓、ETL、CDC 是什么？ |
| 1 | [基础概念与适用场景](01-基础概念与适用场景.md) | 一堆 Parquet 要成为可靠的表还缺什么？Iceberg 的适用范围是什么？ |
| 2 | [元数据与事务原理](02-元数据与事务原理.md) | 一条查询怎样找到文件？两个写者同时提交会怎样？ |
| 3 | [表设计与数据变更](03-表设计与数据变更.md) | 列、分区、排序分别影响什么？更新一行为什么会产生新文件？ |
| 4 | [Spark SQL 实战](04-Spark-SQL实战.md) | 怎样从本地启动 Spark 到建表、写入、查快照跑通一次闭环？ |
| 5 | [Catalog 原理与选型](05-Catalog原理与选型.md) | SQL 中的三段表名怎样定位到文件？Catalog 为什么参与提交？ |
| 6 | [生产运维与版本治理](06-生产运维与版本治理.md) | 为什么会有小文件和孤儿文件？各类维护操作分别清理什么？ |
| 7 | [常见问题与综合复述](07-常见问题.md) | 能否不看原文，解释整条读写链路并区分相近概念？ |

第一次学习按 `00` 到 `06` 顺序阅读。读完后使用 `07` 做综合测试和查漏补缺；其中的术语对照用于快速定位对应专题。

## 📄 先看一张全局图

```text
应用提交 SQL
      |
      v
Spark / Flink / Trino        解析并执行计算
      |
      v
Iceberg Catalog              表名 -> 当前 Metadata JSON
      |
      v
Iceberg 元数据               当前 Snapshot -> Manifest -> 文件集合
      |
      v
Parquet / ORC / Avro         单个数据文件的内部格式
      |
      v
S3 / OSS / HDFS              保存所有文件的字节
```

图中各组件的职责边界如下：

- Catalog 提供表入口并协调提交，数据文件保存在 Warehouse 指定的存储位置。
- Iceberg 提供元数据结构和读写规则，Spark、Flink、Trino 等引擎负责扫描与聚合数据。

## 📄 三句话抓住 Iceberg

1. **读表从 Snapshot 开始**：Catalog 定位 Snapshot，查询读取这个版本记录的文件。
2. **写表通过新版本发布**：先写新文件和新元数据，最后原子发布新的表版本。
3. **规则演进作用于后续写入**：Schema、分区和排序规则可以演进；历史文件通过数据重写获得新布局。

## 📄 学习检查点

### 🔖 读完 00～01

画出“存储 → 文件格式 → Iceberg → Catalog → 计算引擎”，并为每层只写一句职责。如果一句话中出现三个以上未解释的专业词，重新改写。

### 🔖 读完 02～03

拿三张纸分别写 `A.parquet`、`B.parquet`、`C.parquet`，再用两张纸表示：

```text
S0 = [A, B]
S1 = [A, B, C]
```

尝试解释追加、时间旅行、回滚、快照过期分别改变什么。能在纸面上推演文件引用关系，才算真正理解 Snapshot。

### 🔖 读完 04

在隔离环境完成：建表、插入两行、查看 Snapshot、再插入一行、读取旧 Snapshot。实际观察每条 SQL 产生的结果。

### 🔖 读完 05～06

针对“Spark 能看到表但 Trino 看不到”和“存储费用不断上涨”两个故障，各画一条排查链路。解释每一步为什么检查它。

## 📄 什么时候值得使用

### 🔖 适合

- 数据主体在对象存储或 HDFS，文件数量和规模已使裸文件管理困难。
- Spark、Flink、Trino 等多个计算引擎需要共享一致的表版本。
- 需要时间旅行、回滚、批流协作或 Schema/分区持续演进。
- 可以建立小文件合并、Snapshot 保留、权限、监控和升级流程。

### 🔖 适用边界

- 需要毫秒级主键点查、高频随机单行更新和唯一约束，应先评估 MySQL、PostgreSQL、HBase 等系统。
- 数据很少，只有一个简单批处理脚本，直接管理 Parquet 可能成本更低。
- Iceberg 的原子提交以单表为主要边界；跨表强事务由事务数据库或上层协调机制实现。
- 团队没有人负责表维护。Iceberg 接入后仍需治理小文件、旧 Snapshot 和版本兼容。

## 📄 术语速查

这张表用于阅读过程中快速回看。第一次学习以理解各对象如何协作为主。

| 术语 | 白话定义 |
| --- | --- |
| Schema | 表的结构说明书：列名、类型和约束 |
| Catalog | 从逻辑表名找到当前元数据，并协调安全提交的入口 |
| Metadata JSON | 某一版完整的表级说明，包含 Schema、分区规则和 Snapshot 历史 |
| Snapshot | 一次数据提交后可见的文件集合版本；各版本可以复用未变化的数据文件 |
| Manifest List | 某个 Snapshot 使用了哪些 Manifest |
| Manifest | 记录 Data/Delete File 及其统计信息的清单 |
| Data File | 真正保存业务记录的 Parquet、ORC 或 Avro 文件 |
| Delete File | 记录哪些旧行需要在读取时排除 |
| 隐藏分区 | Iceberg 自动算分区值，查询仍使用原始业务列 |
| 时间旅行 | 只读查询历史 Snapshot，不改变当前表 |
| 回滚 | 提交一次变更，让当前表重新引用历史 Snapshot |
| 孤儿文件 | 已写入存储、但不被任何有效表元数据引用的文件 |

## 📄 相关笔记

- [数据处理与查询引擎](../../数据处理/README.md)：Spark、Flink、Trino 的独立教程与选型。
- [Parquet、ORC 与 Avro](../数据文件格式/Parquet、ORC 与 Avro.md)：三种数据文件格式的结构和选择。
- [Apache Spark](../../../数据处理/Spark/费曼教程/README.md)：批处理、ETL、Spring 异步任务和 Iceberg 读写的计算基础。
- [Apache Flink](../../数据处理/Flink.md)：流处理、状态与 Checkpoint 基础。
- [Trino](../../数据处理/Trino.md)：交互式 SQL 与 Connector 基础。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> 新问题先判断属于存储、文件格式、表格式、Catalog 还是计算引擎，再回到对应专题。

## 🗺️ 修订记录

- 2026-08-13：统一改为正面陈述职责与机制，再补充适用边界和风险。
- 2026-08-12：按费曼学习法重组为零基础路线，加入贯穿案例、学习检查点和白话术语。
- 2026-08-06：将原 Iceberg 长文按主题拆开。
- 2026-08-04：新建 Iceberg 实用知识主笔记。

## 🛠️ 实践经历

## ⚙️ prompt

```text
我希望补充一些关于 Iceberg 数据湖的知识。
对于新建文档不需要落到调研区，直接说明。注意我的思维是实用性思维。
```

## 调研

- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)
- [Apache Iceberg Table Specification](https://iceberg.apache.org/spec/)
- [Reliability](https://iceberg.apache.org/docs/latest/reliability/)
- [Evolution](https://iceberg.apache.org/docs/latest/evolution/)
- [Partitioning](https://iceberg.apache.org/docs/latest/partitioning/)
- [Branching and Tagging](https://iceberg.apache.org/docs/latest/branching/)
- [Catalog Configuration](https://iceberg.apache.org/docs/latest/configuration/#catalog-properties)
- [Maintenance](https://iceberg.apache.org/docs/latest/maintenance/)
- [Spark DDL](https://iceberg.apache.org/docs/latest/spark-ddl/)
- [Spark Queries](https://iceberg.apache.org/docs/latest/spark-queries/)
- [Spark Procedures](https://iceberg.apache.org/docs/latest/spark-procedures/)
