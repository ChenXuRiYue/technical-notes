# 📌 Iceberg Catalog 原理与选型

Iceberg Catalog 维护“表标识 -> 当前 Metadata JSON”的权威映射。读取时，引擎通过 Catalog 找到表的当前元数据入口；写入时，Catalog 比较当前入口与写入者的基础版本，并原子提交新入口。

## 📄 这一篇要解决什么问题

在本地练习中，`local.analytics.user_events` 靠本地 Warehouse 路径就能工作。进入生产后，Spark、Flink、Trino 可能运行在不同集群。它们必须共同回答：

- `analytics.user_events` 到底是哪张表？
- 当前有效的 Metadata JSON 在哪里？
- 两个写者同时提交时，谁有资格把新版本设为当前版本？
- 谁能建表、删表、读取元数据和访问数据文件？

Catalog 为这些问题提供权威入口：它根据表名查找地址，也通过版本检查协调新版本发布。

学完后，你应该能从一条三段式 SQL 表名一直追到 Warehouse 中的数据文件，并根据名称解析链路排查“Spark 能看到、Trino 看不到”的问题。

## 📄 从表名走到文件

先拆解：

```text
prod.analytics.user_events
 |       |          |
Catalog  Namespace  Table
别名     逻辑分组    表名
```

这里的 `prod` 首先是 Spark 当前进程中的配置别名。它指向某种 Catalog 实现；Catalog 再定位当前 Metadata JSON；Metadata JSON 最后引用 Warehouse 中的下游元数据与数据文件。

判断两个引擎是否访问同一张表，要比较 Catalog 后端、Warehouse、Namespace 映射和身份配置。SQL 别名可以相同或不同，它只负责在各自引擎中选择配置。

## 📄 Catalog 与表

```text
prod.analytics.user_events
          |
          v
Catalog：解析表标识，找到当前 Metadata JSON
          |
          v
v17.metadata.json -> Current Snapshot -> Manifest -> Data File
```

Catalog 中的当前元数据入口是一个逻辑引用，它给出当前 Metadata JSON 的位置。表的 Snapshot、Manifest 和数据文件保存在 Warehouse 中。

“指针”是逻辑模型，不一定对应 Catalog 数据库中的固定字段。Hive、Glue、JDBC 等实现通常显式保存 Metadata JSON 的位置；Hadoop Catalog 则根据表目录和文件系统规则解析当前版本。实现方式不同，但都必须满足“加载当前表”和“安全提交新版本”的契约。

所谓 **契约**，是各种 Catalog 实现对 Iceberg 客户端承诺的共同外部行为。内部可以用数据库记录位置，也可以按文件系统规则解析；外部必须能可靠加载当前版本，并阻止旧写者静默覆盖新版本。

## 📄 Catalog 记录什么

| 对象或能力 | Catalog 中的情况 | 说明 |
| --- | --- | --- |
| Namespace、表名和表是否存在 | 由 Catalog 登记 | 创建、加载、列举、重命名和删除等表级操作 |
| 当前 Metadata JSON 入口 | 由 Catalog 提供 | 直接保存位置，或提供解析当前位置的机制 |
| 提交新元数据版本 | 由 Catalog 协调 | 防止基于旧版本的写者静默覆盖新版本 |
| Namespace 与 Catalog 级属性 | 视实现而定 | Iceberg 表属性主要随 Metadata JSON 保存 |
| Snapshot、Manifest、Data/Delete File | 文件仍在 Warehouse | 文件本体一般位于 S3、OSS、HDFS |
| SQL 解析、Join、聚合和任务调度 | 由计算引擎完成 | Spark、Flink、Trino 执行这些操作 |
| Parquet、ORC、Avro 内部编码 | 由文件格式规定 | 读写库负责具体编码和解码 |
| 企业资产搜索、血缘和标签治理 | 由 Data Catalog 提供 | 可与 Iceberg Catalog 集成 |

Catalog 提供进入 Iceberg 元数据树的稳定入口。Schema、Snapshot 历史、Partition Spec 和 Manifest 引用保存在 Metadata JSON 及其下游文件中。

## 📄 读取时 Catalog 的位置

```text
1. 引擎将 SQL 名称解析为 Catalog + Namespace + Table
2. Catalog 加载当前 Metadata JSON 位置
3. 引擎读取 Metadata JSON，选择当前或指定 Snapshot
4. 引擎读取 Manifest，规划需要扫描的 Data File
5. Worker/Task 从对象存储或 HDFS 读取数据文件
```

Catalog 位于查询规划入口，返回表元数据位置；Worker 根据规划结果直接从 Warehouse 读取业务数据。Catalog 延迟高或不可用时，新查询的表加载、元数据刷新和新提交会受影响。已完成规划并获得文件列表的任务可能继续读取，生产可用性仍以 Catalog 的 HA 与恢复设计为准。

引擎通常会缓存已加载的表元数据。缓存能降低延迟，也可能让新提交在短时间内不可见。多引擎环境要明确刷新策略、缓存 TTL 和“多久必须看到新快照”的业务要求。

TTL（Time To Live）是缓存项允许存活的时间。TTL 越长，Catalog 压力通常越小，但读取新 Snapshot 的延迟窗口可能越长；具体行为还取决于引擎是否主动刷新或在查询边界重新加载。

## 📄 写入时 Catalog 的位置

两个写者都从 `M0` 开始时，Catalog 必须阻止后提交者静默覆盖先提交者：

```text
Writer A：基于 M0 生成 M1 -> 提交成功，当前入口变为 M1
Writer B：基于 M0 生成 M2 -> Catalog 发现当前已不是 M0，拒绝提交
Writer B：刷新到 M1 -> 检查业务冲突 -> 可以安全重放时生成 M3 再提交
```

Catalog 执行带预期版本的条件更新：当前入口仍是 M0 时才接受 M1，并保证入口切换的原子性。写入任务生成的 Data File、Manifest 和 Metadata JSON 先落到存储中。提交最终失败时，未被有效 Snapshot 引用的文件可能成为孤儿文件。

程序设计中常把这种思路称为 compare-and-swap（比较并交换）：

```text
只有当前值仍等于我读到的 M0，才把它替换成 M1；
否则拒绝，让我刷新后重新判断。
```

因此 Catalog 需要提供带预期版本的条件更新，统一协调所有写者发布当前入口。

Catalog 处理提交入口上的版本竞争。两个 `MERGE` 的业务语义冲突由 Iceberg 冲突检查、引擎实现、隔离级别和业务规则共同判定。Append、Overwrite、DELETE 和 MERGE 需要分别设计重试策略。

## 📄 建表、改名和删表的变更范围

| 操作 | Catalog 层变更 | Warehouse 或运行时影响 |
| --- | --- | --- |
| `CREATE TABLE` | 注册表标识、初始 Metadata JSON 和表位置 | 建立表元数据，查询资源仍由计算引擎提供 |
| `RENAME TABLE` | 修改 Catalog 中的逻辑标识 | 已有数据文件通常保持原 Warehouse 位置 |
| `DROP TABLE` | 取消 Catalog 中的表注册 | 元数据和数据文件的删除由 `PURGE`、引擎和 Catalog 语义决定 |
| `REGISTER TABLE` | 将已有 Iceberg 元数据注册到 Catalog，前提是实现支持 | 以现有元数据的完整性为基础建立入口 |

生产执行 `DROP`、`PURGE`、表迁移或重新注册前，先在目标引擎和 Catalog 上确认真实语义。表入口通过 Catalog 支持的 API 或过程修复；直接修改 HMS、Glue 或 JDBC 中的 `metadata_location` 会绕过提交检查，容易制造不可恢复的不一致。

## 📄 三种容易混淆的 Catalog

| 名称 | 例子 | 作用 |
| --- | --- | --- |
| 计算引擎中的 Catalog 名称 | Spark 的 `prod`、Trino 的 `iceberg` | SQL 名称空间第一段，选择引擎插件或 Connector 配置 |
| Iceberg Catalog 实现 | REST、Hive、Glue、JDBC、Hadoop、Nessie | 加载 Iceberg 表并协调元数据提交 |
| 企业 Data Catalog | Apache Atlas、DataHub、云厂商数据目录 | 资产发现、Owner、标签、血缘、搜索和治理 |

Connector 或插件是计算引擎连接外部系统的适配代码。它把 Spark/Trino 的查询与写入接口转换成 Iceberg Catalog 和表操作；所以“规范支持某能力”之后，还要确认当前引擎的 Connector 是否实现并启用了它。

Spark 示例：

```text
prod.analytics.user_events
  |
  +-> prod：Spark 中配置的 Catalog 别名
        |
        +-> SparkCatalog
              |
              +-> type=rest / hive / hadoop ...
```

Trino 示例：

```text
iceberg.analytics.user_events
   |
   +-> iceberg：Trino Catalog 配置名
         |
         +-> Iceberg Connector
               |
               +-> REST / HMS / Glue / JDBC ... Catalog 后端
```

Spark 中的 `prod` 和 Trino 中的 `iceberg` 可以作为各自引擎的本地别名，并连接到同一个 Catalog 后端、Warehouse 和认证域，从而访问同一张表。判定共享表视图时以后端配置为准，引擎内的别名只用于 SQL 解析。

`Namespace` 和 `Schema` 是不同引擎对逻辑命名层的常见称呼。Iceberg 常用 `Catalog.Namespace.Table`，Trino SQL 更常表述为 `Catalog.Schema.Table`；同一性核对以 Catalog 后端、Warehouse、Namespace 映射和认证配置为准。

## 📄 常见 Catalog 实现

| 类型 | 表入口如何维护 | 适合场景 | 主要取舍 |
| --- | --- | --- | --- |
| REST Catalog | 独立 REST 服务处理表加载、提交和权限请求 | 多引擎、多语言、服务化治理 | 解耦客户端；Catalog 服务需高可用、鉴权、限流和灾备 |
| Hive Catalog | 在 Hive Metastore 登记表及当前元数据位置 | 已有 HMS 和 Hadoop/Hive 生态 | 接入成本低；继续依赖 HMS 容量、可用性和权限模型 |
| Glue Catalog | 在 AWS Glue 登记表及元数据位置 | AWS 数据湖和跨服务集成 | 免自建元存储；需评估 IAM、API 配额、跨账号和云绑定 |
| JDBC Catalog | 在关系数据库表中维护 Namespace 和表入口 | 已有高可用数据库，希望部署简单 | 需要负责数据库 HA、事务、连接池、备份和兼容性 |
| Hadoop Catalog | 由 Warehouse 路径和文件系统规则解析表版本 | 实验、单引擎或文件系统语义可靠的简单环境 | 无中心服务；对象存储和非原子 rename 要特别谨慎 |
| Nessie / 版本化 Catalog | 提供类似 Git 的 Branch、Tag 和 Commit | 跨表版本引用、隔离变更、审核发布 | 引入额外版本语义和服务，需确认全链路兼容 |

HMS 是 Hive Metastore，保存 Hive 生态中的库表登记信息；IAM 是身份与访问管理，控制谁能调用 Glue 或读写 S3；JDBC 是应用访问关系数据库的标准接口。它们表示 Catalog 依赖的不同基础设施；Iceberg 数据文件仍按表配置使用 Parquet、ORC 或 Avro。

## 📄 选型时看这些

Catalog 位于所有表读写的入口，重点看下面几项：

- **提交正确性**：是否提供 Iceberg 要求的原子更新和并发检查。
- **多引擎兼容**：Spark、Flink、Trino 使用的版本和 Catalog 实现是否一致。
- **高可用与恢复**：服务、数据库或 Metastore 故障时如何切换和恢复。
- **权限与凭证**：Catalog 权限与对象存储权限是否分层，是否支持临时凭证。
- **规模与延迟**：表数、Namespace 数、并发加载与提交量、P95/P99 延迟和 API 配额。
- **缓存一致性**：不同引擎多久刷新一次，是否允许短暂读旧元数据。
- **审计与治理**：谁创建、删除、重命名或修改了表入口，能否追踪。
- **迁移边界**：更换 Catalog、Warehouse URI 或云账号时如何验证和回滚。

高可用（HA）表示部分实例或节点故障时，服务仍能继续提供正确能力。P95/P99 表示 95%/99% 的请求延迟不超过该值，比平均值更容易暴露少量特别慢的请求。API 配额是外部服务限制的调用速率或总量。

### 🔖 用约束推导选型

先回答问题，再缩小候选范围：

```text
有几个引擎和语言客户端？
  -> 是否已有 HMS、Glue 或高可用数据库？
  -> 权限和临时凭证在哪里签发？
  -> Catalog 故障允许中断多久、能丢多少状态？
  -> 表数、加载量和提交并发有多大？
  -> 迁移和灾备怎样演练？
```

例如“已经有 HMS”说明 Hive Catalog 的接入成本可能较低。继续核对它的容量、权限、恢复目标和多引擎兼容，才能完成生产选型。

## 📄 从故障现象判断问题

| 现象 | 优先检查 |
| --- | --- |
| Spark 能看到表，Trino 报 `table not found` | Catalog 后端、Warehouse、Namespace 映射和大小写规则 |
| 查询规划阶段长时间卡住 | Catalog/HMS/Glue 延迟、客户端重试、元数据缓存和 Metadata JSON 读取延迟 |
| 提交频繁冲突 | 是否有多个写者修改同一表、提交重试参数和操作是否可安全重放 |
| 能查到表但读文件报 403 | Catalog 权限与对象存储读取权限，检查执行身份和临时凭证 |
| Catalog 中没有表但文件仍在 | 表可能只是取消注册；确认 DROP/PURGE 语义后再恢复或清理 |
| Catalog 有表但 Metadata JSON 不存在 | 停止写入，从审计、备份和历史元数据恢复表入口 |

## 📄 小结

- SQL Catalog 别名经过引擎插件和 Iceberg Catalog 后端，最终指向 Metadata JSON。
- Catalog 是表标识到当前 Metadata JSON 的入口；Metadata JSON、Data File 和企业 Data Catalog 分别承载表版本、业务数据和数据资产治理。
- `table not found`、403 和提交冲突，分别优先检查名称映射、两层权限和并发提交。
- `DROP`、迁移和注册表操作前，先确认 Catalog 和 Warehouse 各自会发生什么变化。

## 📄 费曼推演

请分别解释下面两个现象，答案中要画出表名到文件的路径：

1. Spark 用 `prod`、Trino 用 `iceberg`，却能读到同一批 Snapshot。
2. Spark 和 Trino 都写 `prod.analytics.user_events`，结果却互相看不到新数据。

第一个现象可能是两个本地别名连接了同一 Catalog 后端；第二个现象可能是同名别名背后连接了不同后端、Warehouse 或 Namespace 映射。若解释停在“刷新缓存”，先回到本篇开头核对整条名称解析链路，再判断是否真是 TTL 问题。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> 易混概念集中整理在 [07-常见问题](07-常见问题.md)。

## 🗺️ 修订记录

- 2026-08-12：增加名称解析问题场景、Catalog 契约、compare-and-swap、基础缩写、约束推导和费曼故障推演。
- 2026-08-06：从 Iceberg 主笔记拆出 Catalog 的表入口、提交协调、实现选型和故障诊断，并以表标识到 Metadata JSON 的映射作为叙述起点。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- [Catalog Configuration](https://iceberg.apache.org/docs/latest/configuration/#catalog-properties)
- [REST Catalog OpenAPI](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml)

---

[上一篇：Spark SQL 实战](04-Spark-SQL实战.md) | [返回 Iceberg 目录](README.md) | [下一篇：生产运维与版本治理](06-生产运维与版本治理.md)
