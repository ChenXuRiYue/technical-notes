# 📌 表、Fileset 与计算引擎分别负责什么

急减速场景挖掘同时需要两类数据：程序要按日期、车型和速度变化筛选事件，也要在命中后找到视频、点云和车辆原始日志。平台用不同的数据对象承接这两类责任。

学完本篇，你应该能给一份新数据选择表或 Fileset，并说明 Spark/Ray 为什么属于计算层，而不是数据的永久保存位置。

## 📄 表保存可按字段查询的记录

表适合保存具有稳定列结构的数据。急减速事件索引可以设计成：

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| `event_id` | 事件唯一标识 | `E101` |
| `event_date` | 事件日期 | `2026-08-12` |
| `vehicle_id` | 车辆标识 | `V001` |
| `speed_before_kmh` | 时间窗开始速度 | `72` |
| `speed_after_kmh` | 时间窗结束速度 | `42` |
| `raw_log_path` | 原始数据所在位置 | `gvfs://fileset/autodrive/raw/E101/` |

表的 Schema 记录列名与类型，SQL 或 DataFrame 可以按列过滤、聚合和 Join。集团 Notebook 左侧的“表数据”区支持搜索 Catalog、库、表，查看字段和分区。

如果真实平台使用 Iceberg 表，可以先把它理解成“表的版本与文件组织规则”。需要深入时阅读 [Iceberg 零基础前置课](../../../数据存储/Iceberg/教程/00-零基础前置课.md)。

## 📄 Fileset 保存按路径组织的文件

Fileset 面向非表格数据和文件集合，例如：

- 一段视频或多路相机帧。
- 点云、TFRecord、CSV、Parquet 或文本文件。
- 车辆原始日志、模型产物和场景切片。
- Notebook 需要下载或写出的中间文件。

平台用类似下面的 URI 表示 Fileset 路径：

```text
gvfs://fileset/autodrive/raw/E101/
```

URI 表示资源位置，类似 URL，但协议和访问方式由数据工场提供。Notebook 左侧的“非表数据”区可以搜索 Fileset 并复制路径。计算代码再用对应读取器打开 CSV、Parquet、文本或 TFRecord。

表与 Fileset 可以互相引用：事件表的一行保存 `raw_log_path`，命中规则后，后续节点沿这个路径取得原始片段。这样 SQL 负责高效筛选索引，不需要把整段视频塞进表字段。

## 📄 Spark 和 Ray 执行计算

集团 Notebook Runtime 和离线作业都支持 Spark、Ray 两种计算引擎：

| 计算引擎 | 更自然的入口 | 急减速案例中的任务 |
| --- | --- | --- |
| Spark | SQL、DataFrame、分布式表扫描与聚合 | 扫描一天事件表，计算速度差，输出候选清单 |
| Ray | 通用 Python 分布式任务、Actor、部分机器学习工作负载 | 并行调用 Python 处理器或模型评估逻辑 |

平台提供两者不表示任何任务都应随意切换。表查询、Join 和批量聚合通常先考虑 Spark；已有 Ray 算法或需要 Ray 执行模型时再选择 Ray。资源规格、基础环境和平台插件仍需按目标空间的当前配置验证。

## 📄 DataFrame 是计划，不是本地集合

PySpark 代码可能只有一行：

```python
events = spark.table("autodrive.vehicle_events")
```

这里的表名是教学占位符。`events` 是 DataFrame，它记录表的列结构和“从哪里读取”的逻辑计划。Spark 通常等到 `show()`、`count()`、`collect()` 或 `write` 这类 Action 出现时，才启动实际扫描。

先预测：执行上面一行后，一天数 TB 的事件数据是否已经全部进入 Notebook Runtime 的 Driver 内存？

答案是没有。Driver 此时主要持有计划。真正计算时，Executor 并行读取各自的输入分区。完整机制见 [SQL、DataFrame 与惰性计算](../../Spark/费曼教程/02-SQL-DataFrame-与惰性计算.md)。

## 📄 预览结果要限制规模

交互分析常需要把少量结果转成 Pandas 表格：

```python
preview = candidates.limit(20).toPandas()
preview
```

`toPandas()` 会把结果收回 Driver，所以前面的 `limit(20)` 是容量边界。下面的写法可能让 Driver 尝试容纳全部候选：

```python
all_rows = candidates.collect()
```

当结果必须逐行回到 Driver 处理时，集团文档建议用 `toLocalIterator()` 逐步迭代，避免 `collect()` 一次性返回过多数据。更大的生产结果通常直接写回表或 Fileset，让数据保持在分布式存储中。

## 📄 纸面练习

把下面对象分别交给“表”“Fileset”“计算引擎”：

1. 一亿条带日期、车型、速度差的事件索引。
2. 每个事件对应的 30 秒多路视频。
3. 按日期过滤并统计不同车型的候选数。
4. 一份供标注平台消费的 `scene-manifest.csv`。

参考推理：事件索引放表；视频和输出 CSV 放 Fileset；过滤统计交给 Spark 或 Ray。CSV 也可以读成表格对象参与计算，但它作为持久文件时仍由 Fileset/存储负责保存。

## 📄 费曼检查

向一位熟悉 MySQL 的同事解释：

> 为什么事件表里只保存 `raw_log_path`，仍然足以让后续节点找到视频？Spark 扫描表时，视频字节会经过 Driver 吗？

如果回答把 Fileset 说成数据库表，请回到[Fileset 保存按路径组织的文件](#-fileset-保存按路径组织的文件)。如果回答说 Spark 保存数据，请回到[Spark 和 Ray 执行计算](#-spark-和-ray-执行计算)。

---

[上一篇：为什么需要 Notebook](00-Notebook-Cell-与-Runtime.md) | [返回教程目录](README.md) | [下一篇：交互式场景挖掘](02-交互式场景挖掘.md)

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-08-14：用急减速事件索引和原始日志建立表、Fileset 与计算引擎的责任边界。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- [集团：Notebook 使用指南](https://mi.feishu.cn/wiki/Qk7WwAwPyinAaSkvyhjc8reenzf)
- [Apache Spark SQL 与 DataFrame](https://spark.apache.org/docs/latest/sql-programming-guide.html)
