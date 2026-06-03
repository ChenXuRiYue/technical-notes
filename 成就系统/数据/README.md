# 数据存储区

结构化数据，用于审计、对账、未来迁移至 GitTributary。

## 文件说明

| 文件 | 用途 |
|------|------|
| `exp.jsonl` | 经验流水（收入），只追加 |
| `coin.jsonl` | 金币流水（收入+支出），只追加 |
| `state.json` | 当前状态快照 |

## exp.jsonl 格式（经验账本）

```json
{"ts":"2026-06-04T00:00:00+08:00","type":"genesis","desc":"Game Begin","exp":0}
{"ts":"2026-06-05T14:00:00+08:00","type":"task","desc":"学 SSE 协议","tier":"🟡","base":7,"rate":15,"roll":7,"crit":true,"exp":14,"combo":2,"combo_bonus":1}
{"ts":"2026-06-05T14:00:00+08:00","type":"achievement","desc":"初出茅庐","exp":5}
{"ts":"2026-06-30T23:59:00+08:00","type":"season","period":"2026-06","level":"🚩登顶","exp_total":65}
{"ts":"2026-06-10T10:00:00+08:00","type":"project_complete","desc":"gitNoter","size":"中","exp":25}
```

type：`genesis` | `task` | `achievement` | `combo` | `project_complete` | `season`

task 暴击字段：`base`基础经验 / `rate`爆率% / `roll`掷出点数 / `crit`是否暴击 / `exp`最终经验（暴击则 base×2）。可由 `ts`+`desc` 复算 roll 验证。

## coin.jsonl 格式（金币账本）

```json
{"ts":"2026-06-04T00:00:00+08:00","type":"genesis","desc":"Game Begin","coin":0}
{"ts":"2026-06-05T14:00:00+08:00","type":"earn","desc":"学 SSE 协议","coin":3}
{"ts":"2026-06-05T14:00:00+08:00","type":"earn","desc":"成就：初出茅庐","coin":2}
{"ts":"2026-06-15T10:00:00+08:00","type":"redeem","desc":"一杯好咖啡","coin":-15}
```

type：`genesis` | `earn`(收入) | `redeem`(支出，负数)

## state.json 格式

```json
{
  "realm": "🔥 火种",
  "exp_total": 0,
  "coin_balance": 0,
  "combo": 0,
  "last_active_date": null,
  "daily_streak": 0,
  "active_days_total": 0,
  "tasks_completed": 0,
  "notes_count": 0,
  "achievements": [],
  "season": {
    "month": "2026-06", "month_exp": 0, "month_next": 16,
    "quarter": "2026-Q2", "quarter_exp": 0, "quarter_next": 61,
    "year": "2026", "year_exp": 0, "year_next": 201,
    "month_challenge": null
  }
}
```

字段说明（计数器供成就/挑战/境界廉价判定）：
- `realm`：当前生涯境界（星辰）。靠里程碑试炼进阶，不由积分驱动
- `last_active_date` / `daily_streak`：最近活跃日 / 连续活跃天数 → 「每日一更」
- `active_days_total`：累计活跃天数 → 境界二「微光」试炼
- `notes_count`：累计沉淀笔记数（教授沉淀笔记时 +1）→ 「知识沉淀」
- `month_challenge`：当月挑战槽，月初设定、月末清空
- 各 `*_next` 是**缓存的赛季下一档阈值**，供第一层单次比较判断是否跨档，无需读赛季表。

## 设计原则

1. **ledger 只追加不修改**：像银行流水，历史记录不可篡改
2. **state 是 ledger 的投影**：任何时刻 state 都可以从 ledger 重算
3. **格式为 JSON**：方便程序解析，未来 GitTributary 可直接导入
4. **一个仓库一份 ledger**：多仓库各自维护，GitTributary 负责聚合
