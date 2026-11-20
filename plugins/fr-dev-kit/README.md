# fr-dev-kit — ZCode 插件（MCP App）

把 [FR Dev Kit](../../AGENTS.md)（FineReport 报表开发工具包）封装为 ZCode 插件：
**17 个 MCP 工具 + 控制台面板**。套件仓库仍是唯一事实源，插件只是协议层——
每个工具调用最终都落到套件的 Python 脚本（`python -X utf8 <脚本> ...`，cwd=套件根）。

## 工具面（17 个）

| 工具 | 用途 | 底层脚本 |
|------|------|---------|
| `kb_query` | 知识检索（关键词 / 树导航 / 页精读 / 视图） | `jcxt/js/query_kb.py` |
| `part_query` | 工程零件库 5M1E 查询（part/methods/class/bom…） | `ckzl/zsk/gczsk/query_kb.py` |
| `guard` | 收尾闸门（create/modify/format/error/kb + attest） | `kfgj/guard.py` |
| `kit_selftest` | 套件环境自检（面板状态灯同源） | `kfgj/guard.py --selftest` |
| `fr_check` | 模板三层检测（离线 XML → HTTP → 浏览器） | `kfgj/fzpy/fr_check.py` |
| `template_snapshot` | 模板结构快照（数据集/参数/图表 JSON） | `kfgj/fzpy/template_snapshot.py` |
| `backup_template` | 改前备份（G04） | `kfgj/fzpy/backup_template.py` |
| `db_schema` | 表结构探查（G11，JSON） | `kfgj/fzpy/db_schema.py` |
| `verify_sql` | SQL 验证（G08：执行失败与 0 行都算不通过） | `kfgj/fzpy/verify_sql.py` |
| `layout_grid` | 多组件栅格布局计算（JSON / BoundsWidget Java） | `kfgj/fzpy/layout_grid.py` |
| `eval_formula` | 公式三态判定（G09，需设计器已注入 19000） | `kfgj/fr-agent/exec_js.py eval_formula.js` |
| `designer_status` | 设计器存活/当前模板状态（18999） | `kfgj/fr-agent/fr_agent_client.py` |
| `designer_exec_js` | 向设计器 19000 /exec 投递 Nashorn JS（谨慎） | `kfgj/fr-agent/exec_js.py` |
| `dsl_build` | DSL 标准生成器（dataset/panel/chart，spec→cpt） | `kfgj/dsl/skills/*_skill.py` |
| `dsl_types` | 图表生成器支持/暂不支持清单 | `kfgj/dsl/skills/chart_skill.py --types` |
| `list_gate_reports` | 最近闸门报告列表（面板共用） | 扫 `~/.fr_dev_kit/runs/gate/` |
| `read_gate_report` | 读单份闸门报告 | 同上 |

控制台面板（`ui://fr-dev-kit/console.html`）：套件自检状态灯、最近闸门报告浏览、知识检索工作台。

## 安装（首次）

1. ZCode → 插件市场 → 添加 → **添加插件市场**，粘贴本目录（含 marketplace.json 的
   `plugins/` 目录）的绝对路径。
2. 个人 → fr-dev-kit-local → fr-dev-kit → **安装**。
3. 设置 → 插件 → fr-dev-kit → 填 **kit_root**（套件仓库根目录，含 AGENTS.md/kfgj/ckzl/jcxt）；
   Python 不在 PATH 时另填 **python_cmd** 完整路径。
4. 新开会话，确认出现 `mcp__fr-dev-kit__*` 工具；面板从工具入口或面板列表打开。

## 更新纪律（本地市场不热更新）

改源码后：`npm run build` → 递增 `.zcode-plugin/plugin.json` 的 version →
同步 `../marketplace.json` 条目 version → 市场页刷新该市场 → 插件详情页点更新。
版本三处同步：plugin.json / marketplace.json / git tag（可选）。

## 开发

```bash
cd plugins/fr-dev-kit
npm install          # 首次；SDK 版本在 lockfile 精确 pin，勿混主版本
npm run build        # tsc 类型检查 + esbuild 打 dist/server.mjs + vite 单文件打 dist/console.html
npm test             # node --test：参数映射 / 退出码语义 / stdio 协议冒烟（打真实套件）
```

源码：`src/server.ts`（服务器入口）、`src/tools/`（工具定义 + Python 桥）、`src/ui/`（面板）。
`dist/` 构建产物**提交进 git**（本地市场安装即目录快照，必须自带产物）；`node_modules/` 忽略。

## 依赖要求

- Node 20+（构建期；运行期走 ZCode 托管的 node）
- Python 3.11+（套件侧；核心检索/闸门工具纯标准库）
- 面板/数据库类工具的额外依赖同套件 `kfgj/env.md`（psycopg2、设计器注入等按需）
