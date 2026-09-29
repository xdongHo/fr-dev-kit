<!--
KB_INDEX: {
  "title": "freeze_header.py — 冻结表头（通配规则）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["freeze_header", "CPT", "rows", "kfgj", "tygs", "freeze"],
  "summary": "--- name: freeze-header description: CPT 冻结表头/冻结前 N 行时使用：浏览滚动时表头固定、明细表长列表交付前标配时触发。关键词：冻结、FrozenColumnRow、freeze_header、f"
}
-->

---
name: freeze-header
description: CPT 冻结表头/冻结前 N 行时使用：浏览滚动时表头固定、明细表长列表交付前标配时触发。关键词：冻结、FrozenColumnRow、freeze_header、freeze-rows、表头固定。
keywords: [重复与冻结, 重复与冻结设置, 重复表头, 冻结表头, 冻结窗格, 表头固定, FrozenColumnRow]
---

# freeze_header.py — 冻结表头（通配规则）

一句话：在 `<ReportSettings>` 内加 `<FrozenColumnRow columnrow="A{N+1}"/>` 冻结前 N 行表头；坐标级修改，自动备份 + XML 校验。

## 用法（逐字）

```
python freeze_header.py <cpt路径> [--rows N]   （默认 N=2，即冻结 2 行表头）
```

幂等：已存在冻结配置则跳过（输出「已有冻结配置，跳过」，exit 0）；run_defaults.py 编排时经 `--freeze-rows` 透传。

## 典型调用

```
python kfgj/tygs/CPT模板/默认格式/freeze_header.py <cpt>            # 冻结 2 行
python kfgj/tygs/CPT模板/默认格式/freeze_header.py <cpt> --rows 3   # 双行表头冻结 3 行
```

## references（细节指路）

- 脚本本体: `kfgj/tygs/CPT模板/默认格式/freeze_header.py`（39 行，全文可直读）
- 知识背景: `ckzl/lc/03_报表构建.md` §6 冻结窗格
- 一键编排入口: `kfgj/tygs/skills/run_defaults/SKILL.md`
