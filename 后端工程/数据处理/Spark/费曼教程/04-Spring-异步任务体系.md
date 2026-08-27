# 📌 Spring 怎样控制 Spark 任务

Spring 服务体系接收用户意图，把它转换为可持久化、可追踪、可重试和可取消的业务任务。Spark Application 作为独立计算进程运行，它的依赖、资源和生命周期与对外 Web 实例分开。

## 📄 HTTP 接口先建立任务身份

```http
POST /api/report-jobs
Content-Type: application/json
Idempotency-Key: daily-report-2026-08-12

{"reportDate":"2026-08-12"}
```

```http
HTTP/1.1 202 Accepted
Location: /api/report-jobs/6da2...

{"jobId":"6da2...","status":"PENDING"}
```

`202 Accepted` 表示服务已接收请求并创建任务，计算结果稍后发布。客户端通过稳定 `jobId` 查询：

```http
GET /api/report-jobs/6da2...
```

```json
{
  "jobId": "6da2...",
  "status": "RUNNING",
  "sparkApplicationId": "application_1723_0042",
  "jobVersion": "daily-order-report:2026.08.13.1",
  "resultTable": "prod.analytics.daily_order_report"
}
```

## 📄 任务表保存哪些证据

| 字段 | 用途 |
| --- | --- |
| `job_id` | Spring 侧的稳定身份，连接 API、MQ 和日志 |
| `idempotency_key` | 防止用户重复点击创建两份相同任务 |
| `job_type` | 例如 `DAILY_ORDER_REPORT` |
| `parameters` | 经过校验和规范化的日期、表名等参数 |
| `job_version` | JAR、镜像或 Git 版本，用于重现当时算法 |
| `status` | `PENDING` 到终态的业务状态 |
| `spark_application_id` | 对应集群中的 Spark Application |
| `input_snapshot_id` | 可选；记录任务绑定的输入版本 |
| `output_snapshot_id` | 可选；记录成功产出的结果表版本 |
| `result_table` | 结果的逻辑表名 |
| `error_code` / `error_message` | 可分类的失败摘要，完整日志放在日志系统 |
| 时间字段 | 区分排队、启动、运行与结束耗时 |

`parameters` 要保存已校验的业务参数，不接受任意 `mainClass`、JAR 路径、Spark 配置或 SQL 文本从外部直接穿透。Submitter 根据 `job_type + job_version` 选择已发布的白名单产物和资源模板。

## 📄 Outbox 把“记任务”和“发消息”接成一条可恢复链

Spring Service 在一个数据库事务中写两条记录：

```text
report_job: J42, PENDING, 2026-08-12
job_outbox: SparkJobRequested(J42)
```

Outbox Publisher 后续扫描未发布事件，把 `J42` 发到 MQ，成功后记录发布结果。这样可以从“任务行已提交，发 MQ 前进程崩溃”中恢复，后台可以继续发布未完成的 Outbox 记录。

MQ 传递任务意图：

```json
{
  "jobId": "J42",
  "jobType": "DAILY_ORDER_REPORT",
  "jobVersion": "2026.08.13.1"
}
```

订单数据依然留在 Iceberg 表中。这让 MQ 消息保持小而稳定，Spark 则使用表名与日期范围读取数据。

## 📄 Submitter 怎样启动 Application

Submitter 消费 `J42` 后：

1. 从任务库重读权威参数，不盲信 MQ 中的快照。
2. 检查 `J42` 是否已绑定运行中或已成功的 `applicationId`。
3. 根据环境使用一种受控提交适配器。
4. 获得 `applicationId` 后立即持久化，并转为 `SUBMITTED`。

| 集群入口 | Submitter 动作 | 持久化身份 |
| --- | --- | --- |
| YARN / Standalone | 调用 `spark-submit` 或 `SparkLauncher` | Application ID |
| Kubernetes + Spark Operator | 创建经过模板限制的 `SparkApplication` | 资源名 + Application ID |
| 托管平台 | 调用平台 Job API | 平台 Run ID / Application ID |

SparkLauncher Listener 可以加快状态更新，它是运行时信号。任务库和集群 API 共同构成可恢复的状态来源：Submitter 重启后，定时校准器使用持久化的 `applicationId` 重新查询集群。

## 📄 状态机连接业务与集群

```text
PENDING -> SUBMITTED -> RUNNING -> SUCCEEDED
                              \-> FAILED
PENDING / SUBMITTED / RUNNING -> CANCEL_REQUESTED -> CANCELLED
```

- `PENDING`：任务和 Outbox 已保存。
- `SUBMITTED`：已获得可查询的集群身份。
- `RUNNING`：集群报告 Application 开始运行。
- `SUCCEEDED`：Application 成功结束，且业务定义的输出证据已核对。对日报任务，证据是目标分区对应的新 Iceberg Snapshot 和基本质量检查。
- `FAILED`：Driver、Executor、Iceberg 提交或业务校验失败，保留分类原因和日志入口。
- `CANCEL_REQUESTED`：业务已接受取消，正在调用集群取消并核对终态。

对终态使用带条件更新，防止迟到的 `RUNNING` 回调把 `SUCCEEDED` 覆盖回去。

## 📄 责任边界

| 组件 | 负责 |
| --- | --- |
| Controller | 协议解析、基本输入校验、返回 `202` 和查询链接 |
| ReportJobService | 业务校验、幂等键、任务与 Outbox 事务 |
| Outbox Publisher / MQ | 可重试地传递任务意图 |
| Submitter | 产物选择、资源模板、提交、绑定 Application ID |
| Reconciler | 从集群与结果表校准任务状态 |
| Spark Job | 参数业务校验、分布式计算、幂等写入和输出证据 |

对外 Web 实例的扩缩容不影响已运行 Application。Spark 升级和大体积依赖也不进入 Web 应用的类路径，减少 Spring Boot 与 Spark/Hadoop 依赖冲突。

## 📄 先预测

Outbox 事件被 MQ 投递两次，两个消费线程同时读到 `J42`。

**预测：只在消息处理完成后 ACK，能否保证只提交一个 Application？**

不能。至少需要在提交前用 `jobId` 做并发幂等门闩，例如一个带版本或唯一约束的“获取提交权”更新。底层平台如果支持幂等请求键，同时传入 `jobId`。输出表仍要使用幂等写入，因为网络超时可能让 Submitter 无法立即确认第一次提交是否成功。

---

[上一篇：Spark 与 Iceberg](03-Spark-与-Iceberg.md) | [返回 Spark 目录](README.md) | [下一篇：端到端实现](05-端到端实现.md)

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-08-13：建立 Spring 任务、Outbox、Submitter、Application 与 Reconciler 的控制链。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- [Submitting Applications](https://spark.apache.org/docs/latest/submitting-applications.html)
- [SparkLauncher Java API](https://spark.apache.org/docs/latest/api/java/org/apache/spark/launcher/SparkLauncher.html)
- [Spring Transaction-bound Events](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html)
