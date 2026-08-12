# 📌 Iceberg Spark SQL 操作

这一篇把前面画在纸上的 Snapshot 真正跑出来。你会从一个本地空目录开始，依次完成建表、写入、查看 Snapshot、`MERGE`、时间旅行和元数据排查。

生产示例沿用 `prod.analytics.user_events`；零基础练习先使用本地 `local.analytics.user_events`。`local` 和 `prod` 是当前 Spark 环境中的 Catalog 别名，实际表由别名背后的 Catalog 配置与 Warehouse 共同确定。

## 📄 学完后的验收标准

完成练习时，亲自观察下面四个结果：

1. 第一次 `INSERT` 后出现一个 Snapshot。
2. 第二次写入后出现另一个 Snapshot。
3. 当前查询有三行，查询旧 Snapshot 只有两行。
4. `.files` 能看到业务数据文件，`.snapshots` 能看到提交历史。

这四点把“Snapshot 是版本化文件集合”从一句定义变成了可观察事实。

## 📄 零基础本地环境

### 🔖 1. 先确认版本链

需要 Java、Spark SQL 命令行和 Iceberg Spark runtime 包。先运行：

```bash
java -version
spark-sql --version
```

若 `spark-sql` 提示 `command not found`，说明本机尚未安装 Spark，或 Spark 的 `bin` 目录未加入 `PATH`。先从 [Apache Spark Downloads](https://spark.apache.org/downloads.html) 选择与 Iceberg 支持矩阵兼容的预编译发行版，按 [Spark 官方入门](https://spark.apache.org/docs/latest/index.html) 完成安装，再回到这里确认版本。确定 Spark 和 Scala 版本后，再选择匹配的 Iceberg runtime。

记下 Spark 大版本和 Scala 二进制版本。Iceberg runtime 的 artifact 名称包含它们，例如：

```text
iceberg-spark-runtime-3.5_2.12
                      |    |
                  Spark 3.5 Scala 2.12
```

再从 [Iceberg multi-engine support](https://iceberg.apache.org/multi-engine-support/) 和 [Spark getting started](https://iceberg.apache.org/docs/latest/spark-getting-started/) 选择与本机 Spark 匹配的稳定 Iceberg 版本。Spark、Scala、runtime 任一不匹配，都可能在启动或执行时出现类找不到、方法不存在等错误。

这里的 **runtime 包**让 Spark 在运行时获得 Iceberg 实现；**artifact** 是 Maven 依赖仓库中一个可下载组件的坐标和构建产物；Scala 是 Spark 使用的 JVM 编程语言之一，Scala 二进制版本表示这个包面向哪一代编译接口。这些属于程序依赖版本。Iceberg 表的 `format-version` 则表示数据存储协议版本。

### 🔖 2. 启动本地 Catalog

下面用 `ICEBERG_VERSION` 表示你刚确认的版本。命令会下载对应 runtime；首次执行需要能访问 Maven 仓库。

`/tmp/iceberg-zero-to-one` 应是本轮练习专用的空目录。每次从头练习时换一个新的 Warehouse 路径，以获得教程中的固定行数和 Snapshot 数；其他表目录保持原样。

```bash
ICEBERG_VERSION='<与本机 Spark 匹配的 Iceberg 版本>'

spark-sql \
  --packages "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:${ICEBERG_VERSION}" \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.local=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.local.type=hadoop \
  --conf spark.sql.catalog.local.warehouse=/tmp/iceberg-zero-to-one
```

artifact 中的 Spark、Scala 和 Iceberg 三个版本需要相互匹配。例如本机使用其他 Spark 或 Scala 版本时，同步替换 `3.5_2.12` 和 Iceberg 版本号。

这几个配置分别在做什么：

| 配置 | 白话作用 |
| --- | --- |
| `spark.sql.extensions` | 让 Spark 认识 Iceberg 扩展 SQL 和过程 |
| `spark.sql.catalog.local` | 注册名为 `local` 的 Spark Catalog |
| `local.type=hadoop` | 用 Hadoop Catalog 规则管理本地练习表 |
| `local.warehouse` | 指定练习表文件写到哪里 |

Hadoop Catalog 提供本地单机练习所需的简单表入口。多引擎生产环境还要评估原子提交、权限、高可用和兼容性，具体见 [Catalog 原理与选型](05-Catalog原理与选型.md)。

### 🔖 3. 创建 Namespace 和表

Namespace 是表的逻辑分组，近似数据库中的“库”。在 `spark-sql` 提示符中执行：

```sql
CREATE NAMESPACE IF NOT EXISTS local.analytics;

CREATE TABLE local.analytics.user_events (
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
    'write.format.default' = 'parquet'
);
```

建空表通常先产生初始 Metadata JSON。第一次业务数据写入后，表才出现表示数据文件视图的 Snapshot。

### 🔖 4. 第一次写入

```sql
INSERT INTO local.analytics.user_events VALUES
  (1, 7, 'page_view', TIMESTAMP '2026-08-01 10:00:00', '{}'),
  (2, 7, 'purchase',  TIMESTAMP '2026-08-01 10:05:00', '{"amount":99}');

SELECT *
FROM local.analytics.user_events
ORDER BY event_id;

SELECT committed_at, snapshot_id, operation
FROM local.analytics.user_events.snapshots
ORDER BY committed_at;
```

现在先停下来预测：再插入一行时，旧 Snapshot 会不会改变？正确模型是旧 Snapshot 保持原有视图，新写入发布一个新 Snapshot。

### 🔖 5. 第二次写入并验证时间旅行

```sql
INSERT INTO local.analytics.user_events VALUES
  (3, 8, 'page_view', TIMESTAMP '2026-08-02 09:00:00', '{}');

SELECT committed_at, snapshot_id, parent_id, operation
FROM local.analytics.user_events.snapshots
ORDER BY committed_at;
```

从结果中复制第一次 `INSERT` 产生的 `snapshot_id`，替换下面的占位值：

```sql
-- 当前版本应有 3 行
SELECT COUNT(*) AS current_count
FROM local.analytics.user_events;

-- 第一次 INSERT 后的旧版本应有 2 行
SELECT COUNT(*) AS old_count
FROM local.analytics.user_events
VERSION AS OF <第一次 INSERT 的 snapshot_id>;
```

如果结果分别是 3 和 2，你已经亲手验证：时间旅行改变查询选用的 Snapshot，不修改当前表。

### 🔖 6. 看见数据文件

```sql
SELECT file_path, file_format, record_count, file_size_in_bytes
FROM local.analytics.user_events.files
ORDER BY file_path;

SELECT *
FROM local.analytics.user_events.partitions;
```

`.files`、`.snapshots` 等是 **元数据表**：Iceberg 自动把内部元数据以可查询的虚拟表暴露出来。

到这里，本地最小闭环已经完成。下面进入生产形态的 SQL 和更新场景。

## 📄 运行前确认

开始前确认：

- Spark 能加载 Iceberg runtime 依赖，且依赖版本与表格式能力匹配。
- `prod` 指向正确的 REST、Hive、Glue、JDBC 或 Hadoop Catalog。
- 当前身份同时拥有 Catalog 的表操作权限和 Warehouse 的文件读写权限。
- `analytics` Namespace 已存在，或使用目标引擎支持的建 Namespace 语句创建。
- `staging.user_events` 的列类型和 `MERGE` 源数据已做去重。

这里的 `staging` 表示暂存区：数据先落到中间表完成类型校验和去重，再合并进正式表。团队可以按自己的分层规范命名这张表。

`CREATE TABLE`、Append、`MERGE`、时间旅行、回滚和维护过程先在隔离表上跑通，再触碰生产表。

## 📄 建表

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

`512 MiB` 在本示例中作为目标文件大小的初始基线。生产值结合单分区数据量、对象存储请求开销、执行并行度、压缩率和查询延迟测试。

执行并行度表示同时运行的 Task 数量。写入并行度过高且每个 Task 数据很少时，许多 Task 可能各写一个小文件；目标文件大小只是目标，还受单个 Task 实际可聚合数据量影响。

建表后先确认：

```sql
DESCRIBE TABLE prod.analytics.user_events;
SHOW TBLPROPERTIES prod.analytics.user_events;
```

不同 Spark 版本对 `SHOW TBLPROPERTIES` 的调用形式可能有差异，以目标版本语法为准。

## 📄 Append 写入

```sql
INSERT INTO prod.analytics.user_events
SELECT event_id, user_id, event_type, event_time, payload
FROM staging.user_events;
```

Append 会写出新的 Data File、Manifest 和 Snapshot，再通过 Catalog 提交新的 Metadata JSON。新 Snapshot 引用原有文件和本次追加文件，原有 Parquet 文件保持原样。

写入后先做最小验证：

```sql
SELECT COUNT(*)
FROM prod.analytics.user_events;

SELECT event_id, event_time
FROM prod.analytics.user_events
WHERE event_time >= TIMESTAMP '2026-08-01 00:00:00'
  AND event_time <  TIMESTAMP '2026-08-02 00:00:00'
LIMIT 20;
```

查询直接过滤业务列 `event_time`，Iceberg 根据 `day(event_time)` 分区变换推导候选分区。分区值由表格式维护，SQL 中使用原始时间列。

## 📄 MERGE upsert

先保证 `staging.user_event_changes` 对每个 `event_id` 至多有一行，再执行：

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

`event_id` 在这条 `MERGE` 中是源表与目标表的匹配条件。业务唯一性由写入前的去重规则维护；源数据对同一目标行产生多次匹配时，Spark 可能拒绝执行。可以用窗口函数、去重表或业务序列号选出唯一版本。

**Upsert** 是 update-or-insert 的简称：目标行存在就更新，不存在就插入。它描述业务意图，不表示 Iceberg 会像 MySQL 一样原地修改某个数据页；底层仍按 Copy-on-Write 或 Merge-on-Read 生成新文件。

### 🔖 在本地练习 MERGE

临时视图只在当前 Spark 会话中存在，适合自造两条变更数据：

```sql
CREATE OR REPLACE TEMP VIEW user_event_changes AS
SELECT 2L AS event_id, 7L AS user_id, 'refund' AS event_type,
       TIMESTAMP '2026-08-01 10:06:00' AS event_time,
       '{"amount":99}' AS payload, 'UPDATE' AS op
UNION ALL
SELECT 4L, 9L, 'page_view', TIMESTAMP '2026-08-02 11:00:00', '{}', 'INSERT';

MERGE INTO local.analytics.user_events AS target
USING user_event_changes AS source
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

SELECT event_id, event_type, event_time
FROM local.analytics.user_events
ORDER BY event_id;
```

执行前先预测：`event_id=2` 会被更新，`event_id=4` 会被插入，其他行保持不变；执行后再用 `.snapshots` 查看这次提交产生的 Snapshot。

## 📄 时间旅行、快照与回滚

### 🔖 只读查询历史

```sql
-- 只读历史时刻
SELECT *
FROM prod.analytics.user_events
TIMESTAMP AS OF '2026-08-01 10:00:00';

-- 精确查询某个快照
SELECT *
FROM prod.analytics.user_events
VERSION AS OF 1234567890123456789;
```

时间旅行只能访问仍然存在且可达的 Snapshot。快照保留策略同时决定回滚窗口、增量消费窗口和存储成本。

### 🔖 回滚当前表

```sql
CALL prod.system.rollback_to_snapshot(
    table => 'analytics.user_events',
    snapshot_id => 1234567890123456789
);
```

时间旅行在查询计划中选择历史 Snapshot，当前表引用保持原值。回滚则新建一次元数据提交，把当前表引用调整到历史 Snapshot，底层继续引用已有历史数据文件。执行回滚前先确认下游增量任务、Branch/Tag 引用和保留策略，避免恢复后下游继续消费错误的版本。

### 🔖 Branch 和 Tag

Branch 与 Tag 是 Snapshot 的命名引用，它们与 Snapshot 共享底层数据文件：

- Branch 的指向可以随新提交前进，适合隔离写入或审核后发布。
- Tag 通常固定某个 Snapshot，适合只读标记和复现。
- 只要 Snapshot 仍被有效引用保护，快照过期任务就不应清理相关文件。

## 📄 增量读取语义

Iceberg 增量扫描的基本单位是两个 Snapshot 之间的文件变化。对纯 Append 表，它很适合读取两个 Snapshot 之间新增的数据；但 UPDATE、DELETE 和 Overwrite 不一定会自然还原成数据库 CDC 的行级 `before/after` 事件。

需要行级变更流时，必须确认：

1. 目标引擎是否提供 changelog 或增量扫描能力。
2. 非 Append Snapshot 如何表示被替换和删除的行。
3. 上游消费者是否能在快照过期前完成消费。
4. Delete File 与重写文件是否被当前引擎正确处理。

## 📄 用元数据表排查

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

元数据表是文件数量、分区布局和 Snapshot 历史的第一排查入口。`.files`、`.partitions` 和 `.manifests` 默认反映当前 Snapshot；历史追溯使用 `.snapshots`、`.history`、时间旅行或引擎提供的 `all_*` 元数据表，具体名称以引擎版本为准。

## 📄 检查结果

| 检查项 | 预期结果 |
| --- | --- |
| 建表 | 表可被 Catalog 加载，Schema 和分区规则符合预期 |
| Append | 行数增加，产生新 Snapshot |
| MERGE | 更新、删除、插入分支符合源数据语义 |
| 时间旅行 | 能读取保留窗口内的历史 Snapshot，当前表不受影响 |
| 回滚 | 产生新的元数据提交，当前结果恢复到目标 Snapshot |
| 元数据表 | 能解释文件数、快照历史和 Manifest 变化 |

## 📄 常见启动问题

| 现象 | 先检查什么 |
| --- | --- |
| `ClassNotFoundException` | runtime artifact 是否与 Spark/Scala 匹配，包是否下载成功 |
| `NoSuchMethodError` | Spark、Iceberg runtime 或其他依赖是否混入了不兼容版本 |
| `Cannot find catalog plugin class` | `spark.sql.catalog.local` 的类名和 runtime 是否已加载 |
| `MERGE INTO TABLE is not supported temporarily` | Iceberg Spark extensions 是否配置，目标表是否真是 Iceberg 表 |
| 表能创建但文件写入失败 | Warehouse 路径权限、磁盘空间或对象存储凭证 |
| 重启后本地表找不到 | 是否仍使用同一个 Catalog 类型和 Warehouse 路径 |

排错时一次只验证一层：Java/Spark 能否启动 → runtime 能否加载 → Catalog 能否列出 → Warehouse 能否读写 → SQL 能力是否支持。

## 📄 费曼复述

不看命令，向同事解释一次 `INSERT` 后发生了什么。答案应按顺序出现：Spark 生成 Data File → Iceberg 生成清单和 Snapshot → Catalog 发布新元数据入口 → 新查询加载新 Snapshot。再解释为什么时间旅行不需要复制一份旧表。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> SQL 能力与版本兼容问题统一收录在 [07-常见问题](07-常见问题.md) 和 [06-生产运维与版本治理](06-生产运维与版本治理.md)。

## 🗺️ 修订记录

- 2026-08-12：补充本地零基础环境、无外部依赖的样例数据、两次快照验证、MERGE 练习、排错表和费曼复述。
- 2026-08-06：从 Iceberg 主笔记拆出 Spark SQL 建表、写入、历史查询和元数据排查操作。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- [Spark DDL](https://iceberg.apache.org/docs/latest/spark-ddl/)
- [Spark Queries](https://iceberg.apache.org/docs/latest/spark-queries/)
- [Spark Procedures](https://iceberg.apache.org/docs/latest/spark-procedures/)

---

[上一篇：表设计与数据变更](03-表设计与数据变更.md) | [返回 Iceberg 目录](README.md) | [下一篇：Catalog 原理与选型](05-Catalog原理与选型.md)
