<!--
KB_INDEX: {
  "title": "kfgj/env.md — 环境与配置指南（comm 版）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["kfgj", "agent", "key", "JDK", "fzpy", "jar"],
  "summary": "> 本包是'随身工具箱'：工具全部随包分发，外部依赖按需安装。 > **本包不内置任何凭据（API key / 数据库密码 / 账号）**，所有需要凭据的位置都有占位说明。"
}
-->

# kfgj/env.md — 环境与配置指南（comm 版）

> 本包是"随身工具箱"：工具全部随包分发，外部依赖按需安装。
> **本包不内置任何凭据（API key / 数据库密码 / 账号）**，所有需要凭据的位置都有占位说明。

---

## 1. 外部依赖清单（按需安装）

| # | 依赖 | 用途 | 必需性 |
|---|------|------|--------|
| 1 | **FineReport 10.0 设计器** | 唯一的"设计器本体"；`webapps\webroot\WEB-INF\lib\*.jar` 是编译 fr-agent 与 Java 示例的 classpath 来源；内置服务器(8075)用于在线预览 | 在线验证/渲染需要；离线生成可不装 |
| 2 | **JDK 8**（任意发行版） | `javac` 编译 fr-agent（`kfgj/fr-agent/build.cmd`）与 `ckzl/frapi/ex/` 示例 | 重建 fr-agent jar 时需要（成品 jar 已随包附带） |
| 3 | **Python 3.11+** | 运行全部 Python 工具 | 必需 |
| 4 | **PyYAML** | `kfgj/dsl/compile.py` DSL 编译、web_kit 体检 | DSL 编译需要（`pip install pyyaml`） |
| 5 | **psycopg2 / playwright / openpyxl** | 数据库直连验 SQL / 浏览器级体检 / Excel 断言 | 可选（仅对应功能需要） |

> 检索核心（`jcxt/js/`）、闸门（`kfgj/guard.py`）、断链检查（`kfgj/check_refs.py`）、fr_check/template_snapshot 等日常工具**纯标准库零依赖**，无需 pip。检索已无向量化（2026-09-29：FTS5 关键词 + 树索引导航 + 页级阅读），无需任何向量引擎插件或 API key。

## 2. 环境自检

```
python kfgj/fzpy/check_env.py        # 逐项检测 Python/FR jars/JDK/工作目录
python kfgj/guard.py --selftest      # 环境 + 断链 + 契约同源自检
```

## 3. 数据库连接（可选，按你自己的环境填写）

部分工具（`kfgj/fzpy/db_schema.py`、`verify_sql.py`）支持连接你的数据库做表结构探查与 SQL 冒烟。
**连接方式**：按脚本头部说明填入你自己的主机/账号（支持读取本地配置文件），包内不预置任何主机与凭据。

## 4. FineReport 路径约定

- 默认安装路径 `C:\Program Files\FineReport_10.0\`（与官方默认一致；如自定义，改 `kfgj/fr-agent/cp.txt` 与 inject 脚本中的路径）。
- 报表存放 `...\webapps\webroot\WEB-INF\reportlets\`。
- fr-agent 注入通道：18999(事件) / 19000(/exec)；必须经 `designer.bat`（自动注入）或 `inject.py` 启动，直接双击 designer.exe 不会注入。

## 5. 凭据纪律（重要）

1. 任何 key/密码**只放本机**：使用 `*.local` / `*.local.md` 命名（`.gitignore` 已排除）。
2. 不要把真实凭据写进将提交仓库的文件；交接/外发前用本包 `kfgj/check_refs.py` + 全库搜索复核。
3. 曾把密钥提交进 git 历史的，**换 key 而不是删文件**（历史里仍可翻到）。

## 6. 用户私有数据目录（`%USERPROFILE%\.fr_dev_kit\`）

"随人走、不随套件走"的数据统一放本机用户目录，套件拷贝/外发时自动不带走（目录自带 README）：

| 子项 | 内容 | 写入方 |
|------|------|--------|
| `backup\` | 模板修改前备份（`<模板名>\<时间戳>\`，每模板默认留 20 份） | `kfgj/fzpy/backup_template.py` |
| `snapshot\` | 模板结构快照存档（`<时间戳>_<模板名>.json`） | `kfgj/fzpy/template_snapshot.py --save` |
| `experience\` | 项目经验/复盘（按项目建子目录，不进套件知识索引） | 人工（用该目录下自带的复盘模板起笔） |
| `memory\` | 用户记忆（跨会话事实：环境偏好/常用连接/团队约定） | 人工/工具 |
| `embedding.toml` | （历史遗留）旧向量检索 key 档；2026-09-29 检索无向量化后不再使用，见到可删 | —（旧版 `kfgj/init_user_env.py` 或人工） |
| `fr_env.toml` | 本机 FR/JDK 路径与端口登记（检测不对直接手改） | `kfgj/init_user_env.py` 自动探测生成 |

> 初始化向导：`python kfgj/init_user_env.py`（首次使用必跑；`--status` 查看现状）。
> 路径助手：`kfgj/fzpy/userdir.py`（kfgj 侧脚本 `import userdir` 取各子目录与 FR/JDK 解析）。
> FR/JDK 解析优先级：`fr_env.toml` > 环境变量（FR_HOME/JDK_HOME/JAVA_HOME）> 常见安装位置扫描。
