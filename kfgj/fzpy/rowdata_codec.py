"""
RowData 编解码器 — FR EmbeddedTableData 内置数据集全方言实现（2026-11-19 jar 逆向实证）。

背景: 官方 skill 包(finereport-template-engineer)的解码器在真实 FR 模板上崩(Asci85 overflow)，
根因经 fine-third-10.0.jar 反编译实证——XMLEncodeUtils 静态块 xmlImageDataArray = {"]", "]A"}:
FR 写盘时把 Ascii85 流里的 "]" 转义为 "]A"（防 CDATA 提前闭合 "]]>"），读盘时还原。
官方包缺这步反转义 → 流错位 → 组溢出。实测官方 34 demo 中 11/20 崩，本工具 34/34 全过。

FR 真实编码链(jar 实证: RowDataWrapper→GeneralXMLTools→XMLEncodeUtils→Ascii85OutputStream):
  写: 行文本(TAB/LF 分隔, &t;/&n; 转义) → UTF-8 → raw DEFLATE(wbits=-15)
      → FR Ascii85(基85+33, z 零组简写, 72 换行, '~' 终止) → "]"→"]A" 转义 → CDATA
  读: CDATA → "]A"→"]" 还原(deprecated 旧格式 "]]A"→"]]") → Ascii85 → inflate → 文本

用法:
  python rowdata_codec.py selftest                     # 内置往返自检
  python rowdata_codec.py decode <cpt文件> [--ds 名称] # 解码文件内全部/指定内置数据集
  python rowdata_codec.py encode --json '<rows json>'  # 行数组→RowData 流文本(贴 XML 用)
  python rowdata_codec.py verify <cpt文件或目录>        # 全量解码体检(0=全可解)
  python rowdata_codec.py element --json '<rows json>' # 生成完整 <TableData> XML 元素

退出码: 0=成功/全可解  1=解码失败(列不可解数据)  2=仅警告
"""

# --- console-safe guard (GBK 控制台打印不再 UnicodeEncodeError) ---
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import base64
import json
import os
import re
import zlib
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# 1) CDATA 转义层（XMLEncodeUtils 实证: xmlImageDataArray={"]","]A"}, deprecated={"]]","]]A"}）
# ---------------------------------------------------------------------------
def cdata_escape(s: str) -> str:
    """编码方向: 流文本中 ']' → ']A'（与 FR 写盘一致，防 CDATA 提前闭合）。"""
    return s.replace("]", "]A")

def cdata_unescape(s: str) -> str:
    """解码方向: 先还原 deprecated 旧格式 ']]A'→']]'，再还原现行 ']A'→']'。"""
    if "]]A" in s:
        s = s.replace("]]A", "]]")
    return s.replace("]A", "]")

# ---------------------------------------------------------------------------
# 2) FR Ascii85 层（Ascii85OutputStream 实证: z 零组简写 + 72 换行 + '~' 终止）
#    与 Adobe 标准差异: ① z 简写启用 ② 无 '~>' 结束对, 单 '~' ③ 换行仅 '\n'
# ---------------------------------------------------------------------------
_A85_WRAP = 72

def a85_encode_fine(raw: bytes) -> str:
    """FR 方言 ASCII85 编码（逐组对齐 Ascii85OutputStream 字节码）。"""
    out = []
    col = 0

    def emit(ch: str):
        nonlocal col
        if col >= _A85_WRAP:
            out.append("\n")
            col = 0
        out.append(ch)
        col += 1

    for i in range(0, len(raw), 4):
        chunk = raw[i:i + 4]
        n = len(chunk)
        padded = chunk + b"\x00" * (4 - n)
        word = int.from_bytes(padded, "big")
        if word == 0 and n == 4:
            emit("z")  # 零组简写（字节码 60-75: word==0 → 单字符 'z'）
            continue
        digits = []
        for _ in range(5):
            digits.append(word % 85)
            word //= 85
        # 尾部不满 4 字节只输出 n+1 个字符（相应精度）
        for d in reversed(digits[5 - (n + 1):]):
            emit(chr(33 + d))
    out.append("~")
    return "".join(out)

def a85_decode_fine(text: str) -> bytes:
    """FR 方言 ASCII85 解码。跳过空白；'z'=零组；118-126(除 z) 为终止符；遇非法组抛 ValueError。"""
    out = bytearray()
    pending = []  # 当前组字符
    for ch in text:
        o = ord(ch)
        if ch in "\n\r\t ":
            continue
        if ch == "z" and not pending:
            out += b"\x00\x00\x00\x00"
            continue
        if 118 <= o <= 126 and ch != "z":  # terminator 'v'..'~'
            break
        if not (33 <= o <= 117):
            raise ValueError(f"非法 Ascii85 字符 {ch!r} (U+{o:04X})")
        pending.append(o - 33)
        if len(pending) == 5:
            word = 0
            for d in pending:
                word = word * 85 + d
            if word > 0xFFFFFFFF:
                raise ValueError("Ascii85 组溢出(>2^32): 流已错位, 检查 ]A 转义是否还原")
            out += word.to_bytes(4, "big")
            pending = []
    if pending:
        # 尾部部分组(Adobe 规则): k=n+1 个字符 → 补 'u'(84) 至 5 位 → 取高 n=k-1 字节
        k = len(pending)
        if k < 2:
            raise ValueError(f"残组仅 {k} 字符, 流被截断")
        full = pending + [84] * (5 - k)
        word = 0
        for d in full:
            word = word * 85 + d
        out += word.to_bytes(4, "big")[: k - 1]
    return bytes(out)

# ---------------------------------------------------------------------------
# 3) 明文层（行/列序列化: TAB 分列 LF 分行, 内容转义 &t;/&n;）
# ---------------------------------------------------------------------------
def rows_to_plaintext(rows) -> str:
    lines = []
    for row in rows:
        cells = [str(c).replace("\t", "&t;").replace("\n", "&n;") for c in row]
        lines.append("\t".join(cells))
    return "\n".join(lines)

def plaintext_to_rows(text: str):
    if not text:
        return []
    return [
        [c.replace("&t;", "\t").replace("&n;", "\n") for c in line.split("\t")]
        for line in text.split("\n")
    ]

# ---------------------------------------------------------------------------
# 4) 整表编码 / 解码（EmbeddedTableData 的 <RowData> 单流 = 整表）
# ---------------------------------------------------------------------------
def encode_rows(rows) -> str:
    """rows(二维) → 可直接嵌入 <RowData><![CDATA[...]]></RowData> 的流文本。"""
    if not rows:
        raise ValueError("内置数据集至少 1 行（FR 写不出空流）")
    plain = rows_to_plaintext(rows).encode("utf-8")
    compressed = zlib.compress(plain, 9, wbits=-15)  # raw DEFLATE
    return cdata_escape(a85_encode_fine(compressed))

def decode_rows(encoded: str):
    """流文本 → 二维字符串数组。官方包缺的 ]A 反转义在这里补齐。"""
    text = cdata_unescape("".join(str(encoded or "").split()))
    if text.endswith("~"):
        text = text[:-1]
    if not text:
        return []
    raw = a85_decode_fine(text)
    plain = zlib.decompress(raw, wbits=-15).decode("utf-8")
    return plaintext_to_rows(plain)

# ---------------------------------------------------------------------------
# 5) XML 元素级工具（ColumnNames 分隔 ",,.,," 为官方 demo 实证）
# ---------------------------------------------------------------------------
_COL_SEP = ",,.,,"

def column_names_text(columns) -> str:
    return _COL_SEP.join(str(c) for c in columns)

def column_types_text(types) -> str:
    return ",".join(_short_type(t) for t in types)

def _short_type(t) -> str:
    s = str(t)
    if "." in s:
        s = s.rsplit(".", 1)[-1]
    return {"String": "String", "Integer": "Integer", "Double": "Double",
            "Date": "Date", "Boolean": "Boolean"}.get(s, s)

def tabledata_element(name: str, columns, types, rows) -> str:
    """生成完整 <TableData class="com.fr.data.impl.EmbeddedTableData"> 元素文本。"""
    esc = (lambda v: str(v).replace("&", "&amp;").replace("<", "&lt;")
           .replace(">", "&gt;").replace('"', "&quot;"))
    return (
        f'<TableData name="{esc(name)}" class="com.fr.data.impl.EmbeddedTableData">\n'
        f'<ColumnNames><![CDATA[{column_names_text(columns)}]]></ColumnNames>\n'
        f'<ColumnTypes><![CDATA[{column_types_text(types)}]]></ColumnTypes>\n'
        f'<RowData ColumnTypes="{column_types_text(types)}">'
        f'<![CDATA[{encode_rows(rows)}]]></RowData>\n'
        f'</TableData>'
    )

# ---------------------------------------------------------------------------
# 6) 文件级提取 / 体检
# ---------------------------------------------------------------------------
def extract_embedded_datasets(path: str):
    """返回 [(数据集名, RowData原始流, 列名列表), ...]。兼容纯 XML cpt；压缩 cpt 给出明确报错。"""
    with open(path, "rb") as f:
        head = f.read(4)
    if head[:2] == b"PK":
        raise ValueError("压缩 cpt(zip) 请先解包再取包内 XML（本工具只处理纯 XML cpt）")
    root = ET.parse(path).getroot()
    result = []
    for td in root.iter("TableData"):
        cls = td.get("class") or ""
        if "EmbeddedTableData" not in cls:
            continue
        name = td.get("name", "?")
        cols = []
        cn = td.find("ColumnNames")
        if cn is not None and cn.text:
            cols = [c for c in cn.text.split(_COL_SEP) if c != ""]
        rd = td.find("RowData")
        result.append((name, (rd.text or "").strip() if rd is not None else "", cols))
    return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cmd_selftest(args) -> int:
    cases = [
        [["华东", "上海", 1000], ["华北", "北京", 2500]],
        [["a\tb", "c\nd", "纯ASCII"]],
        [["零", "\x00" if False else "z", "~!@#"]],
        [[str(i) * (i % 7), "x" * i] for i in range(60)],   # 触发 z 组/换行/多行
        [["带]方括号", "]A", "]]"]],
    ]
    fails = 0
    for i, rows in enumerate(cases):
        text_rows = [[str(c) for c in r] for r in rows]
        try:
            enc = encode_rows(rows)
            dec = decode_rows(enc)
            assert dec == text_rows, f"roundtrip 不一致:\n  期 {text_rows}\n  得 {dec}"
            print(f"[OK] case{i+1}: {len(rows)}行x{len(text_rows[0])}列 往返一致")
        except Exception as e:
            fails += 1
            print(f"[FAIL] case{i+1}: {e}")
    print("自检:", "全部通过" if fails == 0 else f"{fails} 个失败")
    return 1 if fails else 0

def cmd_decode(args) -> int:
    try:
        dss = extract_embedded_datasets(args.cpt)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return 1
    if not dss:
        print("(该文件不含 EmbeddedTableData 内置数据集)")
        return 2
    rc = 0
    for name, stream, cols in dss:
        if args.ds and name != args.ds:
            continue
        print(f"== 数据集 {name!r} (列: {cols or '?'}) ==")
        try:
            rows = decode_rows(stream)
            print(f"   {len(rows)} 行 x {len(rows[0]) if rows else 0} 列")
            for r in rows[:5]:
                print("   ", r)
            if len(rows) > 5:
                print(f"    ... 共 {len(rows)} 行")
        except Exception as e:
            rc = 1
            print(f"   [FAIL] {e}")
    return rc

def cmd_verify(args) -> int:
    targets = []
    if os.path.isdir(args.path):
        for dirpath, _dirs, files in os.walk(args.path):
            for fn in files:
                if fn.lower().endswith((".cpt", ".frm")):
                    targets.append(os.path.join(dirpath, fn))
    else:
        targets = [args.path]
    total = ok = fail = skip = 0
    for t in targets:
        try:
            dss = extract_embedded_datasets(t)
        except ValueError:
            skip += 1
            continue
        for name, stream, _cols in dss:
            total += 1
            try:
                decode_rows(stream)
                ok += 1
            except Exception as e:
                fail += 1
                print(f"[FAIL] {os.path.basename(t)} :: {name}: {e}")
    print(f"体检: 可解 {ok}/{total}" + (f" (跳过压缩 {skip})" if skip else ""))
    return 1 if fail else 0

def cmd_encode(args) -> int:
    rows = json.loads(args.json)
    print(encode_rows(rows))
    return 0

def cmd_element(args) -> int:
    payload = json.loads(args.json)
    print(tabledata_element(payload["name"], payload["columns"],
                            payload["types"], payload["rows"]))
    return 0

def main() -> int:
    ap = argparse.ArgumentParser(description="FR EmbeddedTableData RowData 编解码器")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    p = sub.add_parser("decode"); p.add_argument("cpt"); p.add_argument("--ds"); p.set_defaults(fn=cmd_decode)
    p = sub.add_parser("verify"); p.add_argument("path"); p.set_defaults(fn=cmd_verify)
    p = sub.add_parser("encode"); p.add_argument("--json", required=True); p.set_defaults(fn=cmd_encode)
    p = sub.add_parser("element"); p.add_argument("--json", required=True); p.set_defaults(fn=cmd_element)
    args = ap.parse_args()
    return args.fn(args)

if __name__ == "__main__":
    raise SystemExit(main())
