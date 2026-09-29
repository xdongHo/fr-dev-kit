"""
FR 导出产物自动校验闸门（export_gate）— ENH-1 Lane K1 新增（2026-09-11）。

编码来源: ckzl/gf/yspj.md「收尾产物校验」条款——
  「导出类任务必做产物魔数校验——HTTP 200 / 文件非空 ≠ 成功，必须校验产物真实文件类型（doc-1120）」
  验收断言 4「File(...).isFile() && length()>0」防假阳性（doc-2804/1698）。
逐条条款对照见本文件 DOC_REFS 与 v41_campaign/enh1/K1/REPORT.md。

用法:
  python export_gate.py --file <产物> [--kind auto|xlsx|docx|pdf|csv]
                        [--expect-rows N] [--expect-text "水印词"] [--min-pages N]
                        [--out 报告.json]

断言集（每项独立 PASS/FAIL/SKIPPED，绝不编造；SKIPPED 必须带原因）:
  G1 存在且非空      文件缺失/0 字节 = FAIL（doc-2804/1698: length()>0，防保存中断假阳性）
  G2 魔数/真实类型   xlsx/docx=PK\\x03\\x04（docx 另验 [Content_Types].xml 含 wordprocessingml，
                     xlsx 侧对称验 spreadsheetml 防 docx 改名）；pdf=%PDF- 前缀；
                     csv=utf-8/gbk 可解码文本。魔数不符=FAIL（防改名伪装，doc-1120）
  G3 行数比对        xlsx 解压 xl/worksheets/sheet1.xml 数 <row> 元素（±0 精确）；
                     csv 有效数据行数（去引号内换行）。仅 --expect-rows 给出时执行
  G4 水印/文本检索   pdf 搜原始字节（元数据/未压缩流）+ zlib 解压 FlateDecode 流；
                     xlsx 查 headerFooter；docx 查 document.xml 文本；
                     csv 按字节变体（utf-8/utf-16）全文件检索。
                     找不到通道=SKIPPED 并注明原因（不许 FAIL 也不许假 PASS）
  G5 页数(pdf)       字节流 /Type /Pages /Count 启发式取最大值；解析失败=SKIPPED。
                     仅 --min-pages 给出时执行

依赖失败链: G1 FAIL → 其余 SKIPPED；G2 FAIL → G3/G4/G5 SKIPPED（伪装产物结构断言无意义，
对齐 fr_check.py Layer 1「病灶文件直接判死」前置闸哲学）。

判级汇总（对齐 fr_check.py 退出码风格）:
  退出码 0 = 全 PASS；1 = 有 FAIL；2 = 有 SKIPPED 无 FAIL（警告级）。

标准库 only（argparse/json/re/zlib/zipfile/xml.etree）。UTF-8 输出（入口 reconfigure）。
本文件为 ENH-1 K1 纯新增，kit 既有文件零改动。
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji 不再 UnicodeEncodeError) ---
try:
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass
# --- end guard ---
import sys, os, io, re, json, zlib, zipfile, argparse
import datetime
import xml.etree.ElementTree as ET

# ── 退出码三态（对齐 fr_check.py: 0=过 1=错 2=仅警告） ──
EXIT_ALL_PASS = 0
EXIT_HAS_FAIL = 1
EXIT_HAS_SKIPPED = 2

ZIP_MAGIC = b"PK\x03\x04"
PDF_MAGIC = b"%PDF-"

# 判级文档条款引用（报告对照表同源，勿改字）
DOC_REFS = {
    "G1": "验收断言4: File(...).isFile() && length()>0 防假阳性（ckzl/gf/yspj.md, doc-2804/1698）",
    "G2": "收尾产物校验: 导出类任务必做产物魔数校验——HTTP 200 / 文件非空 ≠ 成功，必须校验产物真实文件类型（ckzl/gf/yspj.md, doc-1120）",
    "G3": "K1 任务书规定断言（±0 精确行数；落实验收断言『回读须反查、不许假 PASS』精神）",
    "G4": "K1 任务书规定断言（水印/文本通道检索；找不到通道=SKIPPED 诚实降级）",
    "G5": "K1 任务书规定断言（pdf 页数启发式；解析失败=SKIPPED）",
}


# ════════════════════
# 工具函数
# ════════════════════

def text_byte_variants(word):
    """待检索文本的字节变体: utf-8 / utf-16-le / utf-16-be（覆盖 PDF 字符串与 UTF-16 元数据）。"""
    out = []
    for enc in ("utf-8", "utf-16-le", "utf-16-be"):
        try:
            b = word.encode(enc)
            if b not in out:
                out.append(b)
        except Exception:
            pass
    return out


def decode_text_file(data):
    """csv 可解码性: utf-8-sig → gbk（对齐 fr_check.py L1 编码探测风格）。
    返回 (ok, text, encoding)。注意不引入 utf-16 等恒可解码编码，否则二进制伪装无法拒绝。"""
    for enc in ("utf-8-sig", "gbk"):
        try:
            return True, data.decode(enc), enc
        except (UnicodeDecodeError, ValueError):
            continue
    return False, None, None


def sniff_kind(data):
    """扩展名不可知时按内容嗅探（auto 模式回落）。无法判定返回 None。"""
    if data.startswith(ZIP_MAGIC):
        try:
            zf = zipfile.ZipFile(io.BytesIO(data))
            ct = zf.read("[Content_Types].xml").decode("utf-8", "replace")
            if "wordprocessingml" in ct:
                return "docx"
            if "spreadsheetml" in ct:
                return "xlsx"
        except Exception:
            pass
        return None
    if data.startswith(PDF_MAGIC):
        return "pdf"
    ok, _, _ = decode_text_file(data)
    return "csv" if ok else None


def detect_kind(path, data):
    """auto: 扩展名优先（魔数不符由 G2 兜住），扩展名不可知再按内容嗅探。"""
    ext = os.path.splitext(path)[1].lower()
    ext_map = {".xlsx": "xlsx", ".xlsm": "xlsx", ".docx": "docx", ".docm": "docx",
               ".pdf": "pdf", ".csv": "csv", ".txt": "csv"}
    if ext in ext_map:
        return ext_map[ext]
    return sniff_kind(data)


# ════════════════════
# G2 魔数/真实类型
# ════════════════════

def check_magic(data, kind):
    """返回 (status, detail)。kind 已解析（非 auto）。"""
    if kind in ("xlsx", "docx"):
        if not data.startswith(ZIP_MAGIC):
            return "FAIL", "前 4 字节 %r ≠ PK\\x03\\x04（非 OOXML zip 容器，疑改名伪装）" % data[:4]
        # docx 按判级 prescription 必验 [Content_Types].xml；xlsx 对称验（防 docx/xlsx 互改）
        try:
            zf = zipfile.ZipFile(io.BytesIO(data))
            ct = zf.read("[Content_Types].xml").decode("utf-8", "replace")
        except Exception as e:
            if kind == "docx":
                return "FAIL", "PK 头符合但 [Content_Types].xml 不可读（%s），docx 家族无法确认" % str(e)[:60]
            return "PASS", "PK\\x03\\x04 头符合（zip 不可读，OOXML 家族未验，仅最小魔数判据）"
        if kind == "docx":
            if "wordprocessingml" in ct:
                return "PASS", "PK\\x03\\x04 + [Content_Types].xml 含 wordprocessingml（docx 家族确认）"
            if "spreadsheetml" in ct:
                return "FAIL", "[Content_Types].xml 为 spreadsheetml（疑 xlsx 改名 docx），无 wordprocessingml"
            return "FAIL", "[Content_Types].xml 存在但不含 wordprocessingml（非 docx 家族）"
        # xlsx
        if "wordprocessingml" in ct:
            return "FAIL", "[Content_Types].xml 为 wordprocessingml（疑 docx 改名 xlsx），无 spreadsheetml"
        if "spreadsheetml" in ct:
            return "PASS", "PK\\x03\\x04 + [Content_Types].xml 含 spreadsheetml（xlsx 家族确认）"
        return "PASS", "PK\\x03\\x04 头符合（Content_Types 无 OOXML 家族标记，家族未确认）"
    if kind == "pdf":
        if data.startswith(PDF_MAGIC):
            return "PASS", "%PDF- 前缀符合"
        return "FAIL", "前 5 字节 %r ≠ %PDF-（非 PDF，疑改名伪装）" % data[:5]
    if kind == "csv":
        ok, _, enc = decode_text_file(data)
        if ok:
            return "PASS", "可解码文本（%s，%d 字符）" % (enc, len(data))
        return "FAIL", "utf-8/gbk 均不可解码（疑二进制伪装 csv）"
    return "FAIL", "无法识别文件类型（既非 PK/%PDF 头，亦非可解码文本）"


# ════════════════════
# G3 行数
# ════════════════════

def count_xlsx_rows(data):
    """xlsx sheet1.xml <row> 精确计数。返回 (status, detail, count)。
    status 指"计数通道"是否可用: PASS=计数成功（行数比对由调用方做），SKIPPED=通道缺失。"""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
        names = zf.namelist()
    except Exception as e:
        return "SKIPPED", "zip 打开失败，无法解压工作表（%s）" % str(e)[:60], None
    target = None
    note = ""
    if "xl/worksheets/sheet1.xml" in names:
        target = "xl/worksheets/sheet1.xml"
    else:
        sheets = [n for n in names if re.fullmatch(r"xl/worksheets/[^/]+\.xml", n.replace("\\", "/"))]
        if len(sheets) == 1:
            target = sheets[0]
            note = "（sheet1.xml 缺失，回退唯一工作表 %s）" % sheets[0]
        else:
            return ("SKIPPED",
                    "未找到 xl/worksheets/sheet1.xml（%d 个工作表命名不规则: %s），行数通道不可用"
                    % (len(sheets), ", ".join(sheets[:3]) or "无"), None)
    try:
        root = ET.fromstring(zf.read(target))
        rows = sum(1 for el in root.iter()
                   if isinstance(el.tag, str) and (el.tag == "row" or el.tag.endswith("}row")))
    except Exception as e:
        return "SKIPPED", "工作表 XML 解析失败（%s），行数通道不可用" % str(e)[:60], None
    return "PASS", "行数=%d%s" % (rows, note), rows


def count_csv_records(text):
    """csv 有效数据行数: 引号内换行不计行界，"" 为引号转义；全空记录（空行）不计。"""
    records = 0
    has_content = False
    in_quote = False
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if in_quote:
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':  # "" 转义
                    has_content = True
                    i += 2
                    continue
                in_quote = False
            else:
                has_content = True
            i += 1
        elif ch == '"':
            in_quote = True
            has_content = True
            i += 1
        elif ch in "\r\n":
            if has_content:
                records += 1
            has_content = False
            in_quote = False
            i += 2 if (ch == "\r" and i + 1 < n and text[i + 1] == "\n") else 1
        else:
            has_content = True
            i += 1
    if has_content:  # 末记录无换行收尾（含未闭合引号兜底）
        records += 1
    return records


# ════════════════════
# G4 水印/文本通道
# ════════════════════

def pdf_text_corpus(data, max_total=256 * 1024 * 1024):
    """PDF 可检索语料: 原始字节（元数据/未压缩流）+ zlib 解压的 FlateDecode 流。
    返回 (joined_bytes, ok_inflate, fail_inflate)。"""
    corpus = [data]
    total = len(data)
    ok_n = fail_n = 0
    for m in re.finditer(rb"(?<!end)stream(?:\r\n|\n|\r)", data):
        start = m.end()
        end = data.find(b"endstream", start)
        if end < 0:
            break
        raw = data[start:end].rstrip(b"\r\n")
        if total + len(raw) > max_total:
            break
        inflated = None
        for wbits in (15, -15):  # zlib 头格式 / 裸 deflate
            try:
                inflated = zlib.decompress(raw, wbits)
                break
            except Exception:
                continue
        if inflated is not None:
            corpus.append(inflated)
            total += len(inflated)
            ok_n += 1
        else:
            fail_n += 1
    return b"\n".join(corpus), ok_n, fail_n


def check_watermark_pdf(data, word):
    """pdf: 原始字节+解压流检索水印词。通道找不到（加密/纯图像/CID 编码）=SKIPPED。"""
    if b"/Encrypt" in data:
        return "SKIPPED", "PDF 含 /Encrypt（加密文档），文本通道不可检索"
    corpus, ok_n, fail_n = pdf_text_corpus(data)
    variants = text_byte_variants(word)
    for v in variants:
        if v in corpus:
            return "PASS", "命中水印词（原始字节+ %d 个解压流中检索到，变体编码 %d 字节）" % (ok_n, len(v))
    has_literal = bool(re.search(rb"\((?:[^()\\]|\\.){1,}\)\s*T[Jj]", corpus))
    if has_literal:
        return ("FAIL",
                "可检索通道（原始字节 + %d 个解压流，%d 流解压失败）含字面文本算子但未命中『%s』"
                % (ok_n, fail_n, word))
    if ok_n == 0 and fail_n > 0:
        return "SKIPPED", "文本流全部为压缩格式且解压失败，无可检索文本通道"
    if b"/Identity-H" in data or b"/Type0" in data or b"/UniGB" in data:
        return "SKIPPED", "未发现字面文本算子且检测到 CID 字体（Identity-H/Type0/UniGB），文本可能以字形索引编码，无法机械判定"
    return "SKIPPED", "未发现任何文本绘制算子（疑图像型 PDF），无文本通道可检索"


def check_watermark_xlsx(data, word):
    """xlsx: 水印通道=工作表 headerFooter。无工作表或无 headerFooter 节=SKIPPED。"""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
        names = [n for n in zf.namelist()
                 if re.fullmatch(r"xl/worksheets/[^/]+\.xml", n.replace("\\", "/"))]
    except Exception as e:
        return "SKIPPED", "zip 打开失败，水印通道不可用（%s）" % str(e)[:60]
    if not names:
        return "SKIPPED", "zip 内无 xl/worksheets/*.xml，headerFooter 通道不存在"
    texts = []
    has_hf = False
    for n in names:
        try:
            t = zf.read(n).decode("utf-8", "replace")
        except Exception:
            continue
        texts.append(t)
        if re.search(r"<headerFooter[\s/>]", t):
            has_hf = True
    joined = "\n".join(texts)
    if word in joined:
        return "PASS", "工作表 XML 命中水印词（%d 个工作表）" % len(texts)
    if has_hf:
        return "FAIL", "headerFooter 节存在但未含『%s』（页眉页脚水印缺失或用词不符）" % word
    return "SKIPPED", "所有工作表均无 headerFooter 节（水印通道不存在，无法机械判定）"


def check_watermark_docx(data, word):
    """docx: 水印通道=word/document.xml 文本。成员缺失=SKIPPED。"""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
        if "word/document.xml" not in zf.namelist():
            return "SKIPPED", "zip 内无 word/document.xml，文本通道不存在"
        raw = zf.read("word/document.xml")
    except Exception as e:
        return "SKIPPED", "zip 打开失败，水印通道不可用（%s）" % str(e)[:60]
    if word in raw.decode("utf-8", "replace"):
        return "PASS", "document.xml 命中水印词"
    for v in text_byte_variants(word):
        if v in raw:
            return "PASS", "document.xml 按字节变体命中水印词"
    return "FAIL", "document.xml 可检索但未含『%s』（正文文本缺失或用词不符）" % word


def check_watermark_csv(data, word):
    """csv: 全文件字节按变体检索（通道=文件本身，恒存在）。"""
    for v in text_byte_variants(word):
        if v in data:
            return "PASS", "文件字节命中文本（变体编码 %d 字节）" % len(v)
    return "FAIL", "全文件可检索但未含『%s』" % word


# ════════════════════
# G5 页数（pdf 启发式）
# ════════════════════

def check_pdf_pages(data, min_pages):
    """/Type /Pages 对象窗口内找 /Count，取最大值（页树根=总页数）。解析失败=SKIPPED。"""
    if b"/Encrypt" in data:
        return "SKIPPED", "PDF 含 /Encrypt（加密文档），页数通道不可解析"
    counts = []
    for m in re.finditer(rb"/Type\s*/Pages\b", data):
        # 窗口截到本对象 endobj（长 /Kids 数组不会挤出 /Count；也不误吞相邻对象的 /Count）
        obj_end = data.find(b"endobj", m.end())
        win_end = obj_end if 0 < obj_end - m.end() <= 65536 else m.end() + 65536
        window = data[m.end(): win_end]
        cm = re.search(rb"/Count\s+(\d+)", window)
        if cm:
            counts.append(int(cm.group(1)))
    if not counts:
        return "SKIPPED", "未发现 /Type /Pages + /Count 对象（线性化/对象流/结构异常），启发式解析失败"
    pages = max(counts)
    if pages >= min_pages:
        return "PASS", "启发式页数=%d ≥ 期望 %d" % (pages, min_pages)
    return "FAIL", "启发式页数=%d < 期望 %d" % (pages, min_pages)


# ════════════════════
# 主流程
# ════════════════════

def run_gate(file_path, kind="auto", expect_rows=None, expect_text=None, min_pages=None):
    """执行闸门，返回结构化结果 dict（不打印）。退出码 = result["exit_code"]。"""
    assertions = []

    def add(aid, name, status, detail):
        assertions.append({"id": aid, "name": name, "status": status,
                           "detail": detail, "doc": DOC_REFS.get(aid, "")})

    def dep_skip(aid, name, because):
        add(aid, name, "SKIPPED", "依赖前置失败，跳过: " + because)

    size = 0
    if not os.path.isfile(file_path):
        add("G1", "存在且非空", "FAIL", "文件不存在: %s" % file_path)
    else:
        size = os.path.getsize(file_path)
        if size == 0:
            add("G1", "存在且非空", "FAIL", "0 字节空文件（疑似导出中断，doc-2804/1698 length()>0）")
        else:
            add("G1", "存在且非空", "PASS", "文件存在，%d 字节" % size)

    g1_pass = assertions[-1]["status"] == "PASS"
    data = b""
    if g1_pass:
        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except OSError as e:
            g1_pass = False
            assertions[-1] = {"id": "G1", "name": "存在且非空", "status": "FAIL",
                              "detail": "文件不可读: %s" % str(e)[:80], "doc": DOC_REFS["G1"]}

    # G2 类型解析 + 魔数
    g2_pass = False
    resolved_kind = kind if kind != "auto" else None
    if not g1_pass:
        dep_skip("G2", "魔数/真实类型", "G1 文件缺失/为空/不可读")
    else:
        try:
            if resolved_kind is None:
                resolved_kind = detect_kind(file_path, data)
            status, detail = check_magic(data, resolved_kind)
            add("G2", "魔数/真实类型(%s)" % resolved_kind, status, detail)
            g2_pass = (status == "PASS")
        except Exception as e:
            add("G2", "魔数/真实类型", "SKIPPED", "校验器内部异常（诚实降级）: %s" % str(e)[:80])

    # G3 行数
    if expect_rows is None:
        pass  # 未给参不执行、不入报告（"给了才断言"）
    elif not g1_pass:
        dep_skip("G3", "行数比对", "G1 文件缺失/为空/不可读")
    elif not g2_pass:
        dep_skip("G3", "行数比对", "G2 魔数不符，伪装产物结构断言无意义")
    else:
        try:
            if resolved_kind == "xlsx":
                st, detail, rows = count_xlsx_rows(data)
                if st != "PASS":
                    add("G3", "行数比对", "SKIPPED", detail)
                elif rows == expect_rows:
                    add("G3", "行数比对", "PASS", detail + "，与期望 %d 精确一致（±0）" % expect_rows)
                else:
                    add("G3", "行数比对", "FAIL",
                        "实际 %d 行 ≠ 期望 %d 行（±0 精确比对）" % (rows, expect_rows))
            elif resolved_kind == "csv":
                ok, text, enc = decode_text_file(data)
                if not ok:
                    add("G3", "行数比对", "SKIPPED", "csv 不可解码，行数通道不可用")
                else:
                    rows = count_csv_records(text)
                    if rows == expect_rows:
                        add("G3", "行数比对", "PASS",
                            "有效数据行=%d（去引号内换行，%s 解码），与期望精确一致" % (rows, enc))
                    else:
                        add("G3", "行数比对", "FAIL",
                            "有效数据行=%d ≠ 期望 %d（去引号内换行后精确比对）" % (rows, expect_rows))
            else:
                add("G3", "行数比对", "SKIPPED",
                    "行数通道仅定义 xlsx/csv，当前类型 %s 无行数通道" % resolved_kind)
        except Exception as e:
            add("G3", "行数比对", "SKIPPED", "校验器内部异常（诚实降级）: %s" % str(e)[:80])

    # G4 水印/文本
    if expect_text is None:
        pass
    elif not g1_pass:
        dep_skip("G4", "水印/文本检索", "G1 文件缺失/为空/不可读")
    elif not g2_pass:
        dep_skip("G4", "水印/文本检索", "G2 魔数不符，伪装产物结构断言无意义")
    else:
        try:
            if resolved_kind == "pdf":
                st, detail = check_watermark_pdf(data, expect_text)
            elif resolved_kind == "xlsx":
                st, detail = check_watermark_xlsx(data, expect_text)
            elif resolved_kind == "docx":
                st, detail = check_watermark_docx(data, expect_text)
            elif resolved_kind == "csv":
                st, detail = check_watermark_csv(data, expect_text)
            else:
                st, detail = "SKIPPED", "类型 %s 未定义水印文本通道" % resolved_kind
            add("G4", "水印/文本检索", st, detail)
        except Exception as e:
            add("G4", "水印/文本检索", "SKIPPED", "校验器内部异常（诚实降级）: %s" % str(e)[:80])

    # G5 页数
    if min_pages is None:
        pass
    elif not g1_pass:
        dep_skip("G5", "页数(pdf)", "G1 文件缺失/为空/不可读")
    elif not g2_pass:
        dep_skip("G5", "页数(pdf)", "G2 魔数不符，伪装产物结构断言无意义")
    elif resolved_kind != "pdf":
        add("G5", "页数(pdf)", "SKIPPED", "页数通道仅 pdf，当前类型 %s" % resolved_kind)
    else:
        try:
            st, detail = check_pdf_pages(data, min_pages)
            add("G5", "页数(pdf)", st, detail)
        except Exception as e:
            add("G5", "页数(pdf)", "SKIPPED", "校验器内部异常（诚实降级）: %s" % str(e)[:80])

    n_pass = sum(1 for a in assertions if a["status"] == "PASS")
    n_fail = sum(1 for a in assertions if a["status"] == "FAIL")
    n_skip = sum(1 for a in assertions if a["status"] == "SKIPPED")
    if n_fail:
        rc = EXIT_HAS_FAIL
    elif n_skip:
        rc = EXIT_HAS_SKIPPED
    else:
        rc = EXIT_ALL_PASS
    return {
        "file": file_path,
        "kind_input": kind,
        "kind": resolved_kind,
        "size": size,
        "assertions": assertions,
        "summary": {"PASS": n_pass, "FAIL": n_fail, "SKIPPED": n_skip},
        "exit_code": rc,
    }


# ════════════════════
# 输出（fr_check.py 风格: ✅/❌/⚠️ + ═══ 分节 + 尾部汇总）
# ════════════════════

ICON = {"PASS": "✅", "FAIL": "❌", "SKIPPED": "⚠️ "}


def print_report(result):
    print("═" * 55)
    print("  FR 导出产物自动校验闸门 (export_gate)")
    print("  文件: %s" % os.path.basename(result["file"]))
    print("  类型: %s (输入 --kind %s)  大小: %d B" % (result["kind"], result["kind_input"], result["size"]))
    print("═" * 55)
    cur = None
    for a in result["assertions"]:
        if a["id"] != cur:
            cur = a["id"]
            print("─── %s %s ───" % (a["id"], a["name"]))
        print("  %s %s" % (ICON.get(a["status"], "?"), a["detail"]))
    s = result["summary"]
    print("═" * 55)
    if s["FAIL"]:
        print("  ❌ %d FAIL / %d PASS / %d SKIPPED → 退出码 %d（产物不通过闸门）"
              % (s["FAIL"], s["PASS"], s["SKIPPED"], result["exit_code"]))
    elif s["SKIPPED"]:
        print("  ⚠️  无 FAIL 但 %d 项 SKIPPED（诚实降级）/ %d PASS → 退出码 2（警告级，需人工复核）"
              % (s["SKIPPED"], s["PASS"]))
    else:
        print("  ✅ %d/%d 断言全 PASS → 退出码 0（产物通过闸门）" % (s["PASS"], s["PASS"]))
    print("═" * 55)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser(description="FR 导出产物自动校验闸门（魔数/行数/水印/页数，三态退出码）")
    p.add_argument("--file", required=True, help="产物文件路径")
    p.add_argument("--kind", default="auto", choices=["auto", "xlsx", "docx", "pdf", "csv"],
                   help="产物类型（默认 auto: 扩展名优先，内容嗅探回落）")
    p.add_argument("--expect-rows", type=int, default=None, help="期望行数（xlsx sheet1/csv 有效数据行，±0 精确）")
    p.add_argument("--expect-text", default=None, help="期望水印/文本词")
    p.add_argument("--min-pages", type=int, default=None, help="pdf 最少页数（启发式）")
    p.add_argument("--out", default=None, help="结构化报告 JSON 输出路径")
    args = p.parse_args(argv)

    result = run_gate(args.file, args.kind, args.expect_rows, args.expect_text, args.min_pages)
    print_report(result)

    if args.out:
        payload = dict(result)
        payload["generated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print("  报告已写出: %s" % args.out)
        except OSError as e:
            print("  ❌ 报告写出失败: %s" % e)

    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
