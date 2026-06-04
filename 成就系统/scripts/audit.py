#!/usr/bin/env python3
"""审计脚本：完成任务时自动记账、移动任务、清理废弃条目。

用法：
    python3 audit.py "任务名" <档位1-5> [爆率百分比]

示例：
    python3 audit.py "优化 Mac 终端使其更高效" 3 5
    python3 audit.py "软链接" 2         # 爆率默认 5%
"""

import json
import sys
import hashlib
from datetime import datetime, date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # 成就系统/
ROOT = BASE.parent                              # 仓库根目录
DATA = BASE / "数据"
TASK_PANEL = ROOT / "任务面板.md"
TRASH = BASE / "垃圾桶.md"

TIER_TABLE = {
    1: ("⚡", "顺手", 1, 0),
    2: ("🟢", "轻松", 3, 1),
    3: ("🟡", "投入", 7, 3),
    4: ("🔴", "硬仗", 15, 7),
    5: ("💀", "鏖战", 25, 12),
}

ZONE_RATES = {"🎰头奖": 30, "🎯有趣": 15, "🎲普通": 5}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def bar(cur, nxt, width=6):
    """按 cur/nxt 比例渲染进度条，避免固定空槽造成误解。"""
    n = min(width, round(width * cur / nxt)) if nxt else 0
    return "▰" * n + "▱" * (width - n)


def dice_roll(ts_str, task_name):
    h = 0
    for c in ts_str + task_name:
        h = (31 * h + ord(c)) % 100
    return h


def calc_combo(state, today_str):
    last = state.get("last_active_date", "")
    if last == today_str:
        return state["combo"] + 1
    elif last == (date.today().replace(day=date.today().day - 1)).isoformat():
        return state["combo"] + 1
    else:
        return 1


def calc_daily_streak(state, today_str):
    last = state.get("last_active_date", "")
    if last == today_str:
        return state["daily_streak"]
    try:
        yesterday = (date.today().replace(day=date.today().day - 1)).isoformat()
    except ValueError:
        yesterday = ""
    if last == yesterday:
        return state["daily_streak"] + 1
    return 1


def calc_active_days(state, today_str):
    if state.get("last_active_date") == today_str:
        return state["active_days_total"]
    return state["active_days_total"] + 1


def update_season(season, exp_gain):
    now = datetime.now()
    season["month_exp"] += exp_gain
    season["quarter_exp"] += exp_gain
    season["year_exp"] += exp_gain
    # 检查赛季突破
    upgrades = []
    if season["month_exp"] >= season["month_next"]:
        old = season["month_exp"] - exp_gain
        upgrades.append(f"⛰️ 月赛季突破！{old}→{season['month_exp']}")
    if season["quarter_exp"] >= season["quarter_next"]:
        old = season["quarter_exp"] - exp_gain
        upgrades.append(f"🌊 季赛季突破！{old}→{season['quarter_exp']}")
    if season["year_exp"] >= season["year_next"]:
        old = season["year_exp"] - exp_gain
        upgrades.append(f"🌍 年赛季突破！{old}→{season['year_exp']}")
    return upgrades


def update_task_panel(task_name, tier_emoji, zone, roll, exp, coin, crit, state):
    """一次读写：刷新顶栏、删除已完成任务、清理废弃(删除线)条目、追加到已征服区。
    返回 (removed, trashed_items)。"""
    lines = TASK_PANEL.read_text(encoding="utf-8").split("\n")
    today = date.today().isoformat()

    # 顶栏按 state 重渲染（与结算卡同源，保持一致）
    sea = state["season"]
    em, _, nm = state["realm"].partition(" ")
    topbar = {
        ("经验", "连击"): f"> {em} **{nm}** ｜ 经验 {state['exp_total']} · 金币 {state['coin_balance']} · 连击 {state['combo']}",
        ("⛰️ 月",): f"> ⛰️ 月 `⛺扎营` {bar(sea['month_exp'], sea['month_next'])} {sea['month_exp']}/{sea['month_next']}",
        ("🌊 季",): f"> 🌊 季 `🏖️港湾` {bar(sea['quarter_exp'], sea['quarter_next'])} {sea['quarter_exp']}/{sea['quarter_next']}",
        ("🌍 年",): f"> 🌍 年 `🌱苔原` {bar(sea['year_exp'], sea['year_next'])} {sea['year_exp']}/{sea['year_next']}",
    }

    removed = False
    trashed = []
    kept = []
    for line in lines:
        s = line.strip()
        # 刷新顶栏行
        if line.startswith(">"):
            repl = next((v for ks, v in topbar.items() if all(k in s for k in ks)), line)
            kept.append(repl)
            continue
        # 清理废弃任务（带 ~~删除线~~）
        if s.startswith("- [") and "~~" in s:
            a = s.find("~~")
            b = s.find("~~", a + 2)
            if a != -1 and b != -1:
                reason = s[b + 2:].strip() or "废弃"
                trashed.append(f"- {s[a:b+2]} ｜ {reason}（{today}）")
                continue
        # 删除本次完成的任务
        if not removed and (s.startswith("- [ ]") or s.startswith("- [x]")):
            content = s.split("]", 1)[1].strip()
            parts = content.rsplit(" ", 1)
            if len(parts) > 1 and parts[-1].isdigit():
                content = parts[0].strip()
            if content == task_name:
                removed = True
                continue
        kept.append(line)

    if not removed:
        print(f"⚠️  未在任务面板找到任务：{task_name}")

    # 在已征服区最后一条记录后插入
    crit_mark = " 🎰" if crit else ""
    conquered = f"{tier_emoji} {task_name}   `{zone} 掷{roll}`  `+{exp}exp +{coin}coin`{crit_mark}"
    insert_idx = len(kept)
    for i, line in enumerate(kept):
        if "🏆 已征服" in line:
            for j in range(i + 1, len(kept)):
                if kept[j].strip().startswith(("⚡", "🟢", "🟡", "🔴", "💀")):
                    insert_idx = j + 1
            break
    kept.insert(insert_idx, conquered)
    TASK_PANEL.write_text("\n".join(kept), encoding="utf-8")

    # 废弃条目落入垃圾桶
    if trashed:
        trash_text = TRASH.read_text(encoding="utf-8").rstrip()
        TRASH.write_text(trash_text + "\n" + "\n".join(trashed) + "\n", encoding="utf-8")

    return removed, trashed


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    task_name = sys.argv[1]
    tier = int(sys.argv[2])
    zone_rate = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    if tier not in TIER_TABLE:
        print(f"档位必须是 1-5，收到：{tier}")
        sys.exit(1)

    tier_emoji, tier_name, base_exp, base_coin = TIER_TABLE[tier]
    now = datetime.now()
    ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    today = now.strftime("%Y-%m-%d")

    # 加载状态
    state = load_json(DATA / "state.json")

    # 掷骰
    roll = dice_roll(ts, task_name)
    crit = roll < zone_rate
    exp_gain = base_exp * 2 if crit else base_exp
    coin_gain = base_coin

    # 计算新状态
    new_combo = calc_combo(state, today)
    new_streak = calc_daily_streak(state, today)
    new_active = calc_active_days(state, today)

    combo_bonus = 0
    if new_combo >= 5:
        combo_bonus = 2
    elif new_combo >= 2:
        combo_bonus = 1

    # 更新赛季
    season = state.get("season", {})
    upgrades = update_season(season, exp_gain)

    # 写入记录
    zone_name = f"🎲普通{zone_rate}%" if zone_rate == 5 else f"{'🎰头奖' if zone_rate == 30 else '🎯有趣'}{zone_rate}%"
    append_jsonl(DATA / "exp.jsonl", {
        "ts": today, "task": task_name, "tier": tier,
        "tier_name": tier_name, "exp": exp_gain,
        "zone": zone_name, "roll": roll, "crit": crit,
    })
    append_jsonl(DATA / "coin.jsonl", {
        "ts": today, "type": "earn", "task": task_name, "coin": coin_gain,
    })

    # 更新 state
    state["exp_total"] += exp_gain
    state["coin_balance"] += coin_gain
    state["combo"] = new_combo
    state["last_active_date"] = today
    state["daily_streak"] = new_streak
    state["active_days_total"] = new_active
    state["tasks_completed"] += 1
    state["season"] = season
    save_json(DATA / "state.json", state)

    # 移动任务到已征服 + 清理废弃任务 + 刷新顶栏（单次读写）
    _, trashed = update_task_panel(task_name, tier_emoji, zone_name, roll, exp_gain, coin_gain, crit, state)

    # 输出结算卡
    old_exp = state["exp_total"] - exp_gain
    old_coin = state["coin_balance"] - coin_gain
    print()
    print("┌─ 结算 ─────────────────")
    print(f"│ ✅ {task_name}  [{tier_emoji}{tier_name}] +{exp_gain}经验 +{coin_gain}金币")
    print(f"│ 🎲 掷{roll}  (爆率{zone_rate}%{' 暴击！' if crit else ' 未中'})")
    if crit:
        print(f"│ 🎰 暴击！经验 ×2  (爆率{zone_rate}% 掷出{roll})")
    if new_combo >= 2:
        print(f"│ 🔥 连击 ×{new_combo}  (+{combo_bonus})")
    print("│ ──────────────────────")
    me, mn = season.get("month_exp", 0), season.get("month_next", 16)
    qe, qn = season.get("quarter_exp", 0), season.get("quarter_next", 61)
    ye, yn = season.get("year_exp", 0), season.get("year_next", 201)
    print(f"│ 🔥 境界 {state['realm']} ｜ 经验 {old_exp}→{state['exp_total']} · 金币 {old_coin}→{state['coin_balance']}")
    print(f"│ ⛰️ 月 ⛺扎营 {bar(me, mn)} {me}/{mn}")
    print(f"│ 🌊 季 🏖️港湾 {bar(qe, qn)} {qe}/{qn}")
    print(f"│ 🌍 年 🌱苔原 {bar(ye, yn)} {ye}/{yn}")
    if upgrades:
        for u in upgrades:
            print(f"│ 🎉 {u}")
    if trashed:
        print(f"│ 🗑️  清理废弃任务 ×{len(trashed)}")
    print("└────────────────────────")
    print()


if __name__ == "__main__":
    main()
