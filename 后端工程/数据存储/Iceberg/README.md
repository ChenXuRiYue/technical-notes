# 📌 Apache Iceberg

Iceberg 是一种开放表格式（Open Table Format），它把对象存储或 HDFS 上的 Parquet、ORC、Avro 文件组织成可以安全并发读写、演进和回滚的表。

Iceberg 不是数据库，不负责存储和计算，也不是 Parquet 的替代品。它主要解决的问题是：**如何把大量文件变成一张具有事务语义的表**。

```text
查询引擎：Spark / Flink / Trino / Presto ...
                   |
Catalog：表名 -> 当前 metadata.json
                   |
Iceberg：快照、Manifest、Schema、分区规则、统计信息
                   |
文件格式：Parquet / ORC / Avro
                   |
存储：S3 / OSS / HDFS ...
```

先记住三句话：

1. 读表以快照记录的文件集合为准，不靠遍历目录猜测表中有什么。
2. 写入先产生新文件和新元数据，最后原子替换表的当前元数据指针。
3. 分区、Schema 和排序规则都能演进，但旧数据不会因为元数据变更而自动重写。

## 📄 什么场景值得使用

### 🔖 适合

- 数据主体在对象存储或 HDFS，并且已经达到 TB/PB 级。
- Spark、Flink、Trino 等多个计算引擎需要读写同一份数据。
- 需要批流一体写入、快照隔离、时间旅行、回滚或增量扫描。
- 表结构、分区策略会持续演进，不希望一次变更就重写整表。
- 希望数据和计算引擎解耦，避免被单一引擎的私有存储格式绑定。

### 🔖 不适合

- 毫秒级点查、高频单行更新和主键约束：优先看 MySQL、PostgreSQL、HBase 等系统。
- 数据规模小、只有一个批处理任务：直接管理 Parquet 可能更简单。
- 需要跨表强事务：Iceberg 的原子提交边界通常是单表，不等价于 OLTP 数据库事务。
- 团队不准备运行小文件合并、快照过期等维护任务。Iceberg 不是接入后就无需维护。

## 📄 元数据结构

Iceberg 把一张表组织成一棵元数据树：

```text
Catalog
└── table -> metadata/vN.metadata.json
    ├── Schema / Partition Spec / Sort Order
    ├── Snapshot Log
    └── Current Snapshot
        └── Manifest List
            └── Manifest Files
                ├── Data Files
                └── Delete Files
```

| 对象 | 实用理解 |
| --- | --- |
| Catalog | 维护“表名 -> 当前 metadata.json”的指针，并提供原子更新能力 |
| Metadata JSON | 保存表的 Schema、分区规则、快照历史和当前快照 |
| Snapshot | 表在某次原子提交后的状态，新快照会尽量复用旧元数据 |
| Manifest List | 列出某快照使用的 Manifest，并带有分区范围摘要 |
| Manifest | 记录数据文件和删除文件，包括分区值、列上下界、空值数等统计信息 |
| Data File | 真正的 Parquet、ORC 或 Avro 数据 |
| Delete File | v2 表用来表达行级删除的位置删除或等值删除文件 |

这棵树同时是表的索引。查询不需要遍历整个存储目录，而是从当前快照开始，逐层用分区摘要和列统计裁剪不相关文件。

### 🔖 一次读取如何发生

```text
1. 通过 Catalog 找到当前 metadata.json
2. 确定要读的 Snapshot
3. 用查询条件裁剪 Manifest
4. 用分区值和列统计裁剪 Data File
5. 引擎读取候选文件，应用 Delete File 和剩余过滤条件
```

所以查询慢时不能只看 Parquet 扫描量，还要区分：

- 规划慢：Manifest 过多、元数据大、Catalog 或对象存储延迟高。
- 执行慢：分区或列统计没有裁剪掉多少文件、小文件多、Delete File 多。
- 读放大：排序和查询条件不匹配，或一个宽分区内的数据布局太散。

## 📄 原子提交与并发写

一次写入的核心流程：

```text
1. 读取基础快照 S0
2. 写出新的 Data/Delete File
3. 生成新 Manifest、Snapshot 和 Metadata
4. 请求 Catalog 把指针从 S0 原子替换到 S1
5. 若指针已被其他写者更改，刷新状态、检查冲突并重试
```

这是乐观并发控制。读者始终看到完整快照，不会看到一半旧文件、一半新文件的中间状态。

工程上需要注意：

- Append 一般更容易安全重试；Overwrite、DELETE、MERGE 和数据压缩需要检查被改写的文件是否已变化。
- 提交重试只能处理“可以重放”的冲突，不是所有并发写都会自动成功。
- 提交失败可能留下已写出但未被快照引用的孤儿文件，后续由维护任务处理。
- 不要手工移动或删除表目录下的文件，这会让元数据指向不存在的数据。
- Catalog 是提交协调点。多引擎生产环境不要让各引擎使用互不兼容的 Catalog 视图。

## 📄 Schema、分区与排序演进

### 🔖 Schema 演进

Iceberg 用稳定的字段 ID 识别列，而不只靠列名或位置。因此添加列、重命名列、删除列和部分安全的类型扩宽可以只修改元数据，不立即重写旧数据文件。

实用约束：

- 不要通过“删掉旧列再添加同名新列”代替类型修改，新旧列的字段 ID 不同。
- 先检查所有读写引擎是否支持目标类型和演进操作。
- 元数据上的列删除不代表字节立即从旧文件中消失；涉及合规擦除时需要重写数据并清理可引用旧数据的快照。

### 🔖 隐藏分区

建表时可以定义 `day(event_time)`，但业务查询仍然写：

```sql
WHERE event_time >= TIMESTAMP '2026-08-01 00:00:00'
  AND event_time <  TIMESTAMP '2026-08-02 00:00:00'
```

Iceberg 根据分区变换自动推导需要读取哪些分区，业务 SQL 不需要知道或手动维护 `dt` 这类物理分区列。

分区设计的起点：

| 查询特征 | 候选变换 | 注意 |
| --- | --- | --- |
| 按事件时间查最近几天 | `day(event_time)` | 默认从天级开始，每小时数据量足够大再考虑 `hour` |
| 按高基数 ID 等值查 | `bucket(N, user_id)` | N 必须结合数据量、并行度和文件大小验证 |
| 按有限地域或类型过滤 | identity 分区 | 先检查值域和倾斜，避免产生大量碎分区 |
| 按字符串前缀或数值区间查 | `truncate(L, col)` | 适合范围裁剪，不等于业务索引 |

不要照搬 Hive 的“时间 + 地域 + 类型”多层目录思维。分区过细会带来小文件、Manifest 膨胀和调度开销。

### 🔖 分区和排序演进

- 修改分区规则后，旧文件保持原布局，新数据使用新规则。查询规划会分别处理各版本分区规则。
- 修改排序规则后，旧文件也不会自动排序。要让历史数据获得新布局的性能收益，需要后续重写目标数据文件。
- 元数据演进解决“今后怎么写”，数据重写解决“历史数据怎么摆”，两者不是一件事。

## 📄 行级更新：Copy-on-Write 与 Merge-on-Read

Iceberg 表格式 v2 支持行级 DELETE、UPDATE 和 MERGE 所需的删除表达。实际能否执行及如何执行，由计算引擎和表属性共同决定。

| 模式 | 写入方式 | 优势 | 代价 | 更适合 |
| --- | --- | --- | --- | --- |
| Copy-on-Write | 重写包含受影响行的数据文件 | 查询简单、读性能稳定 | 频繁小范围更新会放大写 I/O | 读多写少、批量修正 |
| Merge-on-Read | 保留数据文件，另写 Delete File | 更新提交更快 | 查询时合并删除，需要定期合并数据和删除文件 | 变更频繁、能承担后台维护 |

实用决策：

- 不要因为 Merge-on-Read 写得快就默认使用。先验证主要读引擎对 Delete File 的支持和性能。
- 上游 CDC 有大量小批次 upsert 时，把实时性、小文件和后台合并作为一组参数调整。
- `MERGE INTO` 前先保证源数据对每个目标键至多匹配一行，否则 Spark 会报错。
- 生产上优先显式设定 `write.delete.mode`、`write.update.mode` 和 `write.merge.mode`，不依赖不同版本的默认值。

## 📄 用 Spark SQL 跑通最小闭环

> 以已配置好的 Iceberg Catalog `prod` 为例。SQL 能力受 Spark 和 Iceberg 版本影响，上线前先对照兼容矩阵。

### 🔖 建表

```sql
CREATE TABLE prod.analytics.user_events (
    event_id     BIGINT NOT NULL,
    user_id      BIGINT,
    event_type   STRING,
    event_time   TIMESTAMP,
    payload      STRING
)
USING iceberg
PARTITIONED BY (day(event_time))
TBLPROPERTIES (
    'format-version' = '2',
    'write.format.default' = 'parquet',
    'write.target-file-size-bytes' = '536870912'
);
```

`512 MiB` 是 Iceberg 当前数据文件目标大小的默认值，不是对所有业务的最优答案。生产中应结合单分区数据量、对象存储开销和查询并行度测试。

### 🔖 写入与 upsert

```sql
INSERT INTO prod.analytics.user_events
SELECT event_id, user_id, event_type, event_time, payload
FROM staging.user_events;
```

```sql
MERGE INTO prod.analytics.user_events AS target
USING staging.user_event_changes AS source
ON target.event_id = source.event_id
WHEN MATCHED AND source.op = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET
    user_id = source.user_id,
    event_type = source.event_type,
    event_time = source.event_time,
    payload = source.payload
WHEN NOT MATCHED AND source.op <> 'DELETE' THEN INSERT (
    event_id, user_id, event_type, event_time, payload
) VALUES (
    source.event_id, source.user_id, source.event_type,
    source.event_time, source.payload
);
```

### 🔖 时间旅行与回滚

```sql
-- 查历史时刻，不改变当前表
SELECT *
FROM prod.analytics.user_events
TIMESTAMP AS OF '2026-08-01 10:00:00';

-- 精确查某个快照
SELECT *
FROM prod.analytics.user_events
VERSION AS OF 1234567890123456789;

-- 把当前表指针回滚到指定快照，是写操作
CALL prod.system.rollback_to_snapshot(
    table => 'analytics.user_events',
    snapshot_id => 1234567890123456789
);
```

时间旅行只能访问未过期且仍可达的快照。快照保留策略同时决定了回滚窗口、增量消费窗口和存储成本。

### 🔖 用元数据表排查

```sql
-- 提交历史和当前快照
SELECT * FROM prod.analytics.user_events.history;
SELECT * FROM prod.analytics.user_events.snapshots;

-- 当前数据文件：看文件数、大小、记录数和分区
SELECT * FROM prod.analytics.user_events.files;

-- 当前分区统计
SELECT * FROM prod.analytics.user_events.partitions;

-- 当前 Manifest
SELECT * FROM prod.analytics.user_events.manifests;
```

元数据表是 Iceberg 的第一排查入口。不要一上来就去对象存储里数文件。

## 📄 Catalog 选型

| 类型 | 适合场景 | 主要取舍 |
| --- | --- | --- |
| REST Catalog | 多引擎、多语言、需要统一权限和服务化治理 | 解耦引擎与底层元存储，但需要运行高可用 Catalog 服务 |
| Hive Catalog | 已有 Hive Metastore 和 Hadoop 生态 | 迁移成本低，但架构继续依赖 HMS |
| Hadoop Catalog | 实验、单引擎或简单 HDFS 环境 | 部署简单，多引擎协作和对象存储场景需要更谨慎 |
| JDBC / 云厂商 Catalog | 已有数据库或云上数据治理体系 | 便于复用现有基础设施，同时要评估锁定效应和各引擎兼容性 |

实用上，Catalog 不只是“放表名的地方”，它是提交的一致性边界和数据治理入口。选型时至少检查：高可用、原子提交、权限、多引擎兼容、凭证下发、审计和灾备。

## 📄 生产维护 SOP

### 🔖 先观察

建议按表监控：

- 每次提交新增的数据文件、Delete File 和 Manifest 数量。
- 数据文件大小的 P50/P95，以及远低于目标大小的文件占比。
- 快照数、最旧快照时间、元数据文件大小。
- 查询规划耗时、扫描文件数和实际读取字节数。
- 提交耗时、冲突率、重试次数和失败率。

### 🔖 合并小文件

```sql
CALL prod.system.rewrite_data_files(
    table => 'analytics.user_events',
    options => map(
        'target-file-size-bytes', '536870912',
        'min-input-files', '5'
    )
);
```

优先处理最近且仍活跃的分区，不要每次重写整表。执行周期应由小文件产生速度和查询性能目标驱动，而不是固定照搬“每天一次”。

### 🔖 过期旧快照

```sql
CALL prod.system.expire_snapshots(
    table => 'analytics.user_events',
    older_than => TIMESTAMP '2026-07-28 00:00:00',
    retain_last => 20,
    stream_results => true
);
```

保留周期必须长于：

- 业务承诺的回滚和时间旅行窗口。
- 下游增量任务可能停顿的最长时间。
- 审计、复现和灾备流程需要的历史周期。

Snapshots 被 branch 或 tag 引用时不会被普通过期操作删除，所以还要监控长期存活的引用。

### 🔖 清理孤儿文件

```sql
-- 先只列出候选文件
CALL prod.system.remove_orphan_files(
    table => 'analytics.user_events',
    older_than => TIMESTAMP '2026-07-31 00:00:00',
    dry_run => true
);
```

核对 dry run 结果后再执行真实删除。

> ⚠️ `older_than` 必须早于任何可能仍在运行的写入任务的开始时间。保留期短于最长写入时间，可能把未提交但仍在写入的文件当成孤儿删掉。官方默认是 3 天，生产值还应额外留安全余量。

如果更换过存储 URI 的 scheme 或 authority，必须先处理路径等价性，否则同一文件可能因字符串路径不同而被误判为孤儿。

### 🔖 重写 Manifest

```sql
CALL prod.system.rewrite_manifests(
    table => 'analytics.user_events'
);
```

这不是每张表的高频例行任务。只有当 Manifest 很多，或写入布局与主要查询过滤条件不对齐，且查询规划已成为瓶颈时再做。

### 🔖 建议的安全顺序

```text
1. 用元数据表和查询指标确认问题
2. 按需合并数据文件 / Delete File / Manifest
3. 按业务保留策略过期快照
4. 孤儿文件先 dry run、复核，再删除
```

## 📄 版本选择

- v1：基础表能力，不支持 v2 的行级删除文件语义。
- v2：增加行级删除和更完整的更新能力，是当前多引擎生产互操作的实用起点。
- v3：规范增加 Deletion Vector、Row Lineage 等扩展能力。不要只因为规范已存在就直接升级，必须确认所有生产读写引擎、Catalog 和工具链都支持。

表格式版本是表级协议，不是 Iceberg 依赖包的版本号。升级前建立一张兼容矩阵：

| 组件 | 版本 | 可读格式版本 | 可写格式版本 | DELETE/MERGE | 分支/Tag | 维护过程 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Spark | | | | | | |
| Flink | | | | | | |
| Trino/Presto | | | | | | |
| Catalog | | | | | | |

## 📄 常见错误

| 错误 | 后果 | 改法 |
| --- | --- | --- |
| 把 Iceberg 当成计算引擎 | 只建表，却没有解决查询资源和调度问题 | 分开评估表格式、Catalog、引擎和存储 |
| 沿用 Hive 过细分区 | 小文件和元数据膨胀 | 从主要查询条件出发，用隐藏变换和文件统计裁剪 |
| 只看数据总量 | 100 GB 也可能因几十万小文件而很慢 | 同时看文件数、大小分布、Manifest 和规划时间 |
| 将时间旅行当永久备份 | 快照过期或存储故障后无法恢复 | 快照用于表内版本，灾备仍需要独立备份和跨域复制 |
| 不做保留策略就过期快照 | 下游增量任务断点丢失，无法回滚 | 把业务 RPO/RTO、最长停顿和审计需求写成表级策略 |
| 直接执行孤儿文件删除 | 误删进行中的写入文件 | 先 dry run，保留时间大于最长任务时间并留余量 |
| 不检查多引擎兼容就升格式版本 | 部分引擎无法读表或语义不一致 | 先在隔离表验证完整读写链路，再升级生产表 |

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-08-04：新建 Iceberg 实用知识主笔记。

## 🛠️ 实践经历

## ⚙️ prompt

```text
我希望补充一些关于 Iceberg 数据湖的知识。
对于新建文档不需要落到调研区，直接说明。注意我的思维是实用性思维。
```

## 📄 参考资料

- [Apache Iceberg Table Specification](https://iceberg.apache.org/spec/)
- [Reliability](https://iceberg.apache.org/docs/latest/reliability/)
- [Evolution](https://iceberg.apache.org/docs/latest/evolution/)
- [Maintenance](https://iceberg.apache.org/docs/latest/maintenance/)
- [Spark DDL](https://iceberg.apache.org/docs/latest/spark-ddl/)
- [Spark Queries](https://iceberg.apache.org/docs/latest/spark-queries/)
- [Spark Procedures](https://iceberg.apache.org/docs/latest/spark-procedures/)
