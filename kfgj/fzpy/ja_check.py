# -*- coding: utf-8 -*-
"""ja_check.py — 主表 CDATA 格式感知体检（v4, 2026-11-04 ]A 全案翻案版）

⛔ 翻案声明(2026-11-04, 推翻 2026-09-19 v3 的 ]A 损伤定性):
  ]A 不是损伤 —— 是 FineReport 自有的 CDATA 盘上转义格式。
  铁证: fine-third-10.0.jar/com.fr.stable.xml.XMLEncodeUtils 反编译
    xmlImageDataArray = {"]", "]A"}
    cdataEncode: 写出时每个 ] → ]A (防 CDATA 内容出现 ]]> 终结符)
    cdataDecode: 读回时 ]A → ]  (对称还原; "]AA"→"]A" 替换自愈=计数恒定)
  引擎读回解码(WorkBook4 盘上 =JOINARRAY([1,2]A,",") 导出 xlsx 实算 "1,2" 实证)。
  历史结论: Designer 保存/LLM/生成脚本/生产环境 全部无罪;
  14 个月 14 轮 "deA 清偿" 均为裸读工具(python/node/grep)不认识盘上格式的误诊。

v4 行为:
  L0 XML 合法性 — ET 解析(裸写手术产出内容若含 ]]> 会破坏结构, 此处兜住)
  L1 残留损伤形态 — 仅保留 ": : int"(format_sql_pretty 拆裂, 与 ]A 转义无关的
                    真实损伤家族); 原 ]A 九族/泛化扫描/白名单全部退役
  L2 JS 块体检 — CDATA 内容先按 cdataDecode(]A→]) 解码再提取 → node --check,
                 保留真实语法错误捕获力, 转义不再误报
  转义计数 — INFO 级展示(格式合规观察项, 不告警)

用法:
  python ja_check.py <cpt路径> [...]        # 指定文件
  python ja_check.py --dir <目录>           # 目录内全部 .cpt(跳过 *.bak*)
  python ja_check.py --all                  # 默认 两率分析报表\明细报表
  python ja_check.py <cpt> --json           # 机读输出(guard/CI 挂载用)

退出码(对齐 fr_check): 0=通过  1=有 ERROR  2=仅 WARN

本脚本只读不修。
"""
import io
import os
import re
import sys
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET

DEFAULT_DIR = r"."  # --all 默认当前目录;社区版请用 --dir <你的reportlets目录> 或直接传文件

# ---- L1 残留损伤家族(ERROR 级) ----------------------------------------------
# 仅保留与 ]A 转义无关的真实损伤形态; ]A 族已定性为 FR CDATA 转义格式(v4 退役)
DAMAGE_FORMS = [
    ("::int拆裂", re.compile(r":\s+:\s+int")),  # format_sql_pretty 家族(09-08 实发)
]

CDATA_RX = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)
JS_HINTS = ("function", "addEventListener", "setTimeout(", "$(", "document.", "window.")


def cdata_decode(s):
    """FR XMLEncodeUtils.cdataDecode 的 Python 镜像: ]A → ] (含 ]AA→]A 自愈语义)"""
    return s.replace("]A", "]")


def decode_cdata(text):
    """CDATA 内容就地解码(保持行号/其余字节不变), 供内容级检查使用"""
    return CDATA_RX.sub(lambda m: "<![CDATA[" + m.group(1).replace("]A", "]") + "]]>", text)


def find_node():
    for cand in ("node", "node.exe"):
        try:
            subprocess.run([cand, "--version"], capture_output=True, timeout=10)
            return cand
        except Exception:
            continue
    return None


def js_blocks(text):
    """提取疑似真实 JS 的 CDATA 块(剔除 FR 公式/SQL 伪捕获); 输入须为解码后文本"""
    out = []
    for m in CDATA_RX.finditer(text):
        blk = m.group(1)
        head = blk.lstrip()
        if head.startswith("="):          # =SWITCH(...) 等 FR 公式伪捕获
            continue
        if head[:6].upper() in ("SELECT", "-- ", "WITH "):  # SQL
            continue
        if not any(h in blk for h in JS_HINTS):
            continue
        out.append((m.start(1), blk))
    return out


def check_file(path, node_bin):
    name = os.path.basename(path)
    errors, warns, infos = [], [], []
    try:
        raw = io.open(path, "r", encoding="utf-8", errors="replace", newline="").read()
    except OSError as e:
        return {"file": name, "errors": ["无法读取: %s" % e], "warns": [], "infos": [], "js": []}

    # L0 XML 合法性(裸写内容含 ]]> 破坏结构时兜住)
    try:
        ET.fromstring(io.open(path, "rb").read())
    except Exception as e:
        errors.append("XML 非法: %s" % str(e)[:120])

    # L1 残留损伤形态(在解码后文本上扫描, 与引擎视角一致)
    decoded = decode_cdata(raw)
    for label, rx in DAMAGE_FORMS:
        hits = [m.start() for m in rx.finditer(decoded)]
        if hits:
            ln = decoded.count("\n", 0, hits[0]) + 1
            errors.append("%s ×%d (首现行 %d, 字节 %d)" % (label, len(hits), ln, hits[0]))

    # 转义计数(INFO 观察项: FR CDATA 盘上格式, 合规, 不告警)
    n_esc = raw.count("]A") - decoded.count("]A")
    if n_esc > 0:
        infos.append("FR CDATA 转义 ]A ×%d (盘上格式合规, 已解码后检查)" % n_esc)

    # L2 node --check(解码后 JS 块)
    js_result = []
    blocks = js_blocks(decoded)
    if node_bin and blocks:
        for idx, (pos, blk) in enumerate(blocks):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
                tf.write(blk)
                tmp = tf.name
            try:
                r = subprocess.run([node_bin, "--check", tmp], capture_output=True, timeout=20)
                ok = (r.returncode == 0)
                first_err = ""
                if not ok:
                    el = (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])
                    first_err = el[-1][:120]
                js_result.append({"i": idx, "bytes": len(blk), "ok": ok, "err": first_err})
                if not ok:
                    ln = decoded.count("\n", 0, pos) + 1
                    errors.append("JS块#%d(%dB,行%d) node --check FAIL: %s" % (idx, len(blk), ln, first_err))
            finally:
                os.unlink(tmp)
    elif blocks:
        warns.append("node 不可用,跳过 L2(node --check) — 仅静态形态扫描")
    return {"file": name, "errors": errors, "warns": warns, "infos": infos, "js": js_result}


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    if as_json:
        args = [a for a in args if a != "--json"]
    files = []
    if not args or args == ["--all"]:
        args = ["--dir", DEFAULT_DIR]
    if args[0] == "--dir":
        d = args[1] if len(args) > 1 else DEFAULT_DIR
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".cpt") and ".bak" not in fn:
                files.append(os.path.join(d, fn))
    else:
        files = args

    node_bin = find_node()
    results, worst = [], 0
    for p in files:
        r = check_file(p, node_bin)
        results.append(r)
        if r["errors"]:
            worst = 1
        elif r["warns"] and worst == 0:
            worst = 2

    if as_json:
        print(json.dumps({"exit": worst, "results": results}, ensure_ascii=False, indent=1))
    else:
        for r in results:
            tag = "PASS" if not r["errors"] and not r["warns"] else ("ERROR" if r["errors"] else "WARN ")
            print("[%s] %s" % (tag, r["file"]))
            for e in r["errors"]:
                print("   E: " + e)
            for w in r["warns"]:
                print("   W: " + w)
            if r["infos"]:
                print("   i: " + "; ".join(r["infos"]))
        print("exit=%d (%d 文件, %d 有损伤, L2=%s)" % (
            worst, len(results), sum(1 for r in results if r["errors"]),
            "node" if node_bin else "不可用"))
    sys.exit(worst)


if __name__ == "__main__":
    main()
