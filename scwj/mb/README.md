<!--
KB_INDEX: {
    "title": "scwj/mb",
    "stage": "output",
    "tags": [
      "产出",
      "落地",
      "reportlets"
    ],
    "keywords": [
      "生成器产出",
      "reportlets",
      "部署流程"
    ],
    "summary": "模板生成器产出的落地目录：gen_*.py 生成 .cpt 后经此复制到 FR reportlets 预览测试"
  }
-->

# scwj/mb

> 模板生成器（Python/Java）的产出处落地目录。

← [返回主路由](../../gf/FR_HEADLESS_GUIDE.md)

---

## 用途

`gen_fill_v2.py`、`gen_import.py` 等生成器产出的 .cpt 文件放在这里，
之后复制到 FR 服务器 reportlets 目录进行预览测试。

> **产物归置约定（2026-09-29）**：按项目组织的产物（契约 JSON / 骨架 xlsx·cpt /
> 组装脚本 / 项目版模板）放用户目录 `%USERPROFILE%\.fr_dev_kit\projects\<项目名>\`，
> **不放本目录**——套件外发/交接不带项目数据。本目录仅存套件自带演示与临时落地。
> 运行痕迹（闸门报告/探查快照/LLM trace）同理归 `~/.fr_dev_kit/runs/`。

## 工作流

```
kfgj/fzpy/gen_xxx.py    kfgj/tygs/widen_all.py    FR reportlets/
        │                           │                           │
        ▼                           ▼                           ▼
    生成 .cpt ──────────────→ 格式化布局 ──────────────→ 预览验证
                                 ↑                           │
                                 │                           ▼
                            scwj/mb/ ←─── 修改后回存 ──── localhost:8075
```

## 文件命名建议

| 类型 | 命名 | 说明 |
|------|------|------|
| 查看 | `xxx_查看.cpt` | 只有查询+导出按钮 |
| 填报 | `xxx_填报.cpt` | 含提交按钮+单元格控件 |
| 导入 | `xxx_导入.cpt` | 含 Import showDialog |

## 下一步

生成后的步骤：
1. 运行格式化脚本 → [../kfgj/tygs/索引目录.md](../kfgj/tygs/索引目录.md)
2. 预览验证 → [../ckzl/zsk/csff/README.md](../ckzl/zsk/csff/README.md)
3. 部署到 FR 服务器 → `C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\`
