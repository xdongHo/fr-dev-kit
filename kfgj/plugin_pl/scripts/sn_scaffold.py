#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
sn_scaffold.py — 插件工程骨架生成器 v1.0（pipeline_v1 / SN-03）
一条命令生成符合流水线形制的插件工程骨架（对齐 demo_plugin_repo/aicopilot 实战形制）。
用法:
  python sn_scaffold.py --id com.fr.plugin.demo --version 0.1.0 --vendor your.co --out C:\work\demo_plugin
生成内容:
  plugin.xml(无BOM) / build.cmd(白名单清理) / src 包路径 / web\js+css / test / docs(需求卡+键清单+依赖实证+shell速查) /
  sn_gate.config.json(预填残留检查) / README.md
仅标准库；只新建目录，不覆盖已有文件（--force 才覆盖）。
"""
import argparse, json, os, datetime

PLUGIN_XML = """<?xml version="1.0" encoding="UTF-8" standalone="no"?><plugin>
  <id>{id}</id>
  <name><![CDATA[{name}]]></name>
  <active>yes</active>
  <hidden>no</hidden>
  <main-package>{pkg}</main-package>
  <version>{version}</version>
  <env-version>{env}</env-version>
  <vendor>{vendor}</vendor>
  <jartime>{today}</jartime>
  <description><![CDATA[（一句话定位——来自 docs/需求卡.md）]]></description>
  <!-- 扩展点按需启用并确保 class 源文件存在（sn_gate C04）:
  <extra-decision>
    <HttpHandlerProvider class="{pkg}.XxxHttpProvider"/>
  </extra-decision>
  <extra-designer>
    <MenuHandler class="{pkg}.XxxMenuHandler"/>
  </extra-designer>
  -->
</plugin>
"""

BUILD_CMD = """@echo off
REM 构建模板（SN-06 纪律）：JDK8 + FR jars。清理白名单：只清 build\\classes 与 dist，绝不删 jar/lib。
REM 陷阱备忘（台账 P03）：带 -D 参数必须走 cmd（本文件即是）；中文 JSON 发包用 --data-binary @file。
setlocal
set ID={id}
set VER={version}
set JAR=fr-plugin-{short}-%VER%.jar
set FRJARS=C:\\frjars;C:\\Program Files\\FineReport_10.0\\webapps\\webroot\\WEB-INF\\lib\\*
if "%FRJARS_OVERRIDE%" neq "" set FRJARS=%FRJARS_OVERRIDE%

REM ---- clean（白名单：只删可再生构建产物；用 mv 挪 .trash，不用递归强删）----
REM 手工清理法：把 build\\classes 整目录挪到 .trash\\<时间戳>\\ ，定期人工清空 .trash

REM ---- compile（SN-06：增量时显式列出改动源文件，防旧 class 假错误 P15）----
if not exist build\\classes mkdir build\\classes
javac -encoding UTF-8 -cp "%FRJARS%" -d build\\classes src\\{pkgpath}\\*.java
if errorlevel 1 ( echo COMPILE FAILED — 按 SN-06: git checkout 回滚损坏文件, 禁止坏文件上打补丁 & exit /b 1 )

REM ---- jar（在 classes 内打包, 保证无多余顶层目录）----
cd build\\classes && jar cf ..\\%JAR% . && cd ..\\..

REM ---- deploy（先停 FR 再动 plugins；运行中 jar 被锁属正常, 孤儿无害）----
echo 部署: 复制 build\\%JAR% + plugin.xml 到 WEB-INF\\plugins\\plugin-%ID%-%VER%\\
echo 重启设计器 → 轮询 8075 → 重取 token（SN-06 部署链）
endlocal
"""

README = """# {name}（{id}）

> 由 sn_scaffold.py 生成于 {today}。工程纪律见 `kfgj/plugin_pl/01_工艺流水线总纲.md`。

## 目录
- `plugin.xml` — 插件清单（四道门：无BOM/jartime/active/扩展点class存在）
- `src/{pkgpath}/` — Java 源码
- `web/js`, `web/css` — 前端资源（ScriptPath 用斜杠形式且无前导斜杠；HTTP URL 用点形式——SN-03 总表）
- `test/` — 无头测试（unit/e2e 双模式，沙箱隔离——SN-08）
- `docs/` — 需求卡 / 键清单 / 依赖实证 / shell速查
- `sn_gate.config.json` — 机器闸门配置（收尾必跑 SN-12）

## 收尾闸门
```
python <kit>\\kfgj/plugin_pl\\scripts\\sn_gate.py --config sn_gate.config.json --report _runs\\sn_gate_report.md
```
"""

REQ_CARD = """# 需求卡（SN-01）
1. 一句话定位：
2. 身份表：插件ID={id}｜包名={pkg}｜HTTP路径族=＿＿｜菜单id=＿＿｜配置目录=~/.＿＿/
3. 功能清单（v1 最小可用集）：
4. 不做清单（P23 教训——"将来可能要"不是需求）：
5. 用户确认记录（D1：日期/结论）：
"""

KEYS_DOC = """# 键清单（SN-05）
| 键 | 存储侧 | 查询侧 | normalize 规则 |
|---|---|---|---|
| （示例）模板路径 | locks json | 树渲染 | 小写 + \\→/ + 唯一 Norm.key() |
"""

DEPS_DOC = """# 依赖实证（SN-02）
| jar | 用途 | 已 javap 实证类 |
|---|---|---|
| fine-core-10.0.jar | 核心 | （先 javap 后写码——P11 教训） |
"""

def write(path, content, force):
    if os.path.exists(path) and not force:
        print(f"  跳过(已存在): {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:  # 无 BOM
        f.write(content)
    print(f"  写入: {path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="插件 ID（点形式）")
    ap.add_argument("--name", default=None)
    ap.add_argument("--version", default="0.1.0")
    ap.add_argument("--vendor", default="dev")
    ap.add_argument("--env-version", dest="env", default="10.0~")
    ap.add_argument("--out", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    pkg = a.id
    short = a.id.split(".")[-1]
    pkgpath = a.id.replace(".", os.sep)
    today = datetime.date.today().isoformat()
    out = os.path.abspath(a.out)
    print(f"生成工程骨架: {out}")
    write(os.path.join(out, "plugin.xml"), PLUGIN_XML.format(id=a.id, name=a.name or short, pkg=pkg, version=a.version, env=a.env, vendor=a.vendor, today=today), a.force)
    write(os.path.join(out, "build.cmd"), BUILD_CMD.format(id=a.id, version=a.version, short=short, pkgpath=pkgpath), a.force)
    write(os.path.join(out, "src", pkgpath, "README.md"), "# 源码包 " + pkg + "\n", a.force)
    write(os.path.join(out, "web", "js", "README.md"), "# 前端 JS（资源路径纪律见 SN-03 总表）\n", a.force)
    write(os.path.join(out, "web", "css", "README.md"), "# 前端 CSS\n", a.force)
    write(os.path.join(out, "test", "README.md"), "# 无头测试（unit/e2e 双模式；沙箱隔离红线见 SN-08）\n", a.force)
    write(os.path.join(out, "docs", "需求卡.md"), REQ_CARD.format(id=a.id, pkg=pkg), a.force)
    write(os.path.join(out, "docs", "键清单.md"), KEYS_DOC, a.force)
    write(os.path.join(out, "docs", "依赖实证.md"), DEPS_DOC, a.force)
    write(os.path.join(out, "docs", "shell速查.md"), "# shell 速查（SN-07：命令只从模板抄）\n见 kfgj/plugin_pl/03_标准节点包/SN-07\n", a.force)
    tail = short
    cfg = {
        "plugin_root": ".",
        "src": "src",
        "web": "web",
        "plugin_xml": "plugin.xml",
        "build_scripts": ["build.cmd"],
        "version_pairs": [["build.cmd", "VER=([^\\s\\r\\n]+)"]],
        "residual_greps": [{"pattern": tail, "scope": ["src"], "note": "改名残留示例——按身份表五项替换为真实旧名"}],
        "env_path_markers": ["C:\\Program Files\\FineReport", "C:\\frjars"]
    }
    write(os.path.join(out, "sn_gate.config.json"), json.dumps(cfg, ensure_ascii=False, indent=2), a.force)
    write(os.path.join(out, "README.md"), README.format(name=a.name or short, id=a.id, pkgpath=pkgpath, today=today), a.force)
    print("完成。下一步: 填 docs/需求卡.md → D1 确认 → 按 SN-02 出架构一页纸。")

if __name__ == "__main__":
    main()
