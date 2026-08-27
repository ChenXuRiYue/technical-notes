# 📌 从 SQL 和 DataFrame 到执行计划

基础谈资。日报计算要把一张订单表变成一张按商户汇总的结果表。SQL 可以直接描述结果；Java 程序则需要一个对象，保存表的列结构和接下来要执行的过滤、分组与聚合步骤。

## 📄 先用 SQL 说清意图

```sql
SELECT
    DATE(created_at) AS report_date,
    merchant_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount
FROM prod.sales.orders
WHERE created_at >= TIMESTAMP '2026-08-12 00:00:00'
  AND created_at <  TIMESTAMP '2026-08-13 00:00:00'
GROUP BY DATE(created_at), merchant_id;
```

这条 SQL 的职责链很明确：

```text
选择表 -> 限定一天 -> 按日期与商户分组 -> 计数与求和
```

SQL 只表达结果应满足什么关系。Spark 还要结合表元数据、统计信息和配置，选择扫描、聚合、Shuffle 和写出方式。

## 📄 Java 程序怎样拿住一张表

日报收到 `reportDate=2026-08-12` 后，需要由 Java 代码动态填入时间范围，再继续组合过滤、分组和写入操作。先看程序面对的订单表：

| order_id | merchant_id | amount | created_at |
| --- | --- | ---: | --- |
| O1001 | M01 | 80.00 | 2026-08-12 09:10:00 |
| O1002 | M01 | 20.00 | 2026-08-12 10:30:00 |
| O1003 | M02 | 45.00 | 2026-08-12 11:15:00 |

Java 程序需要拿住三类信息：

1. **表从哪里来**：这里是 `prod.sales.orders`。
2. **表有哪些列**：例如 `merchant_id` 是商户编号，`amount` 是金额。列名、类型以及是否允许空值合在一起叫 **Schema**。
3. **怎样得到下一张表**：先按日期过滤，再按商户分组，最后计算订单数与总金额。

Spark 把这种**有明确列结构、能够继续进行表格转换的数据对象**称为 **DataFrame**。从 Java 程序看，它像一张可以连续加工的表；从 Spark 的执行过程看，它还携带“怎样生成这张表”的逻辑计划。订单的实际数据仍在 Iceberg 对应的数据文件中，Driver 不会因为创建 DataFrame 就容纳所有订单。

Java API 使用 `Dataset<Row>` 表示 DataFrame：

| 名称 | 在订单例子中的含义 |
| --- | --- |
| `Row` | 一行订单，例如 `O1001, M01, 80.00, 2026-08-12 09:10:00` |
| `Dataset<Row>` | 由多行组成、带 Schema，并且可以继续转换的表格对象 |
| `Schema` | `order_id`、`merchant_id`、`amount`、`created_at` 的列名、类型和空值约束 |

## 📄 用 DataFrame 表达同一份计算

```java
Dataset<Row> orders = spark.table("prod.sales.orders");

Dataset<Row> result = orders
        .filter(
                col("created_at").geq(lit(start))
                        .and(col("created_at").lt(lit(end)))
        )
        .groupBy(
                to_date(col("created_at")).alias("report_date"),
                col("merchant_id")
        )
        .agg(
                count(lit(1)).alias("order_count"),
                sum(col("amount")).alias("total_amount")
        );
```

逐行对应前面的三类信息：

- `spark.table(...)` 记录数据来源，并取得表的 Schema。
- `filter(...)` 追加日期过滤步骤。
- `groupBy(...)` 追加分组规则。
- `agg(...)` 追加计数与求和规则，返回描述汇总结果的新 DataFrame。

先停在第一行做一次预测：

> 执行 `Dataset<Row> orders = spark.table("prod.sales.orders");` 后，数 TB 订单是否已经进入 Driver 内存？

答案是没有。Driver 此时拿到表的结构和逻辑计划，还没有启动 Executor 扫描全部订单。后面的 `filter`、`groupBy` 和 `agg` 继续扩充计划；需要看到结果或写出结果时，Spark 才会启动计算。

改变一个条件：调用 `orders.collect()` 会立刻要求得到所有行。Spark 将启动 Job，并把结果送回 Driver。它只适合已经确认很小的结果；对数 TB 订单调用会耗尽 Driver 内存。

## 📄 惰性计算

`select`、`filter`、`withColumn`、`join` 和 `groupBy(...).agg(...)` 等转换通常先返回新 DataFrame，并把操作加入逻辑计划。它们不立即扫描数据。

Action 要求产生可观察结果，因此触发 Job：

| Action | 结果去向 | 风险 |
| --- | --- | --- |
| `show()` | Driver 日志或终端 | 用于小量查看，可能额外触发一份 Job |
| `count()` | 返回 Driver 一个数值 | 仍需执行必要的扫描与聚合 |
| `collect()` | 把全部结果拉到 Driver | 结果大时可以耗尽 Driver 内存 |
| `write` / `writeTo` | 外部文件或表 | 需要设计提交和重试语义 |

## 📄 一份计划经历哪些形态

```text
SQL 文本 / DataFrame API
        |
        v
未解析计划：还没有确认表和列
        |
        v
已分析逻辑计划：表、列和类型已绑定
        |
        v
优化逻辑计划：下推过滤、裁剪列、化简表达式
        |
        v
物理计划：具体扫描、聚合、Join 与 Exchange
        |
        v
Job / Stage / Task
```

Iceberg 参与表的加载和扫描规划：它让 Spark 从选定的 Snapshot 开始，根据分区与列统计裁剪文件。Spark 继续把保留的扫描任务交给 Executor。

## 📄 用 `explain` 核对模型

```java
result.explain("formatted");
```

重点观察：

- 扫描的表名与读取列。
- 日期过滤是否靠近扫描端，能否下推。
- 聚合前后是否有 `Exchange`，它常对应 Shuffle 重分区。
- 输出分区数是否与数据量匹配。

计划中的具体名称会随 Spark 版本、Adaptive Query Execution 和数据源变化。核心是沿着“读什么 -> 哪里重分布 -> 如何写出”查看计划。

## 📄 SQL、DataFrame、Dataset 和 RDD 怎样选

| 入口 | 优先使用的场景 | 对优化器的可见性 |
| --- | --- | --- |
| Spark SQL | 分析、ETL、团队已有 SQL 治理 | 列与表达式结构清晰 |
| DataFrame | 动态组合转换、Java/Python 工程化 | 与 SQL 共用结构化优化体系 |
| Dataset | Java/Scala 中需要类型编码的对象转换 | 结构化操作可见，对象编解码有额外成本 |
| RDD | 结构化 API 无法表达的底层算法 | 记录内部语义对 Spark SQL 优化器不透明 |

日报、数据清洗、Join 和聚合优先用 SQL 或 DataFrame。当问题确实需要底层分区或自定义记录算法时，再引入 RDD。

## 📄 先预测再实验

```java
Dataset<Row> result = buildDailyReport(spark, reportDate);
System.out.println("plan-created");
result.writeTo("prod.analytics.daily_order_report")
        .overwritePartitions();
```

预测这两行日志之间发生什么：

1. `buildDailyReport` 返回时，主要完成计划构建。
2. `plan-created` 可以在 Executor 扫描前打印。
3. `writeTo` 触发 Job，数据在 Executor 上被读取、聚合和写出。

练习时在 Action 前后各打一条日志，同时打开 Spark UI 观察 Job 出现的时机。

## 📄 费曼复述

先不用“分布式”和“惰性”两个词，向一位熟悉 `List<Order>` 的同事解释：

> DataFrame 保存了哪三类信息？创建它时订单在哪里？什么操作才会让 Spark 真正读取订单？

再向一位熟悉 Java Stream 的同事解释：

> DataFrame 方法链为什么可以先构建计划，以及 Spark 为什么能把日期过滤推向文件扫描端。

如果解释中直接跳到“Spark 是惰性的”，回到 `spark.table(...)` 执行后 Driver、Executor 和数据文件分别处于什么状态，再说惰性给优化器带来了什么重排和下推机会。

---

[上一篇：执行模型与 Shuffle](01-执行模型与-Shuffle.md) | [返回 Spark 目录](README.md) | [下一篇：Spark 与 Iceberg](03-Spark-与-Iceberg.md)

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-08-13：建立 SQL、DataFrame、逻辑计划、物理计划与 Action 的因果链。
- 2026-08-13：在 Java 首次需要表格对象的位置引入 DataFrame，并补充 Schema、`Dataset<Row>`、读取时机与预测练习。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- [Spark SQL, DataFrames and Datasets Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Spark SQL Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
