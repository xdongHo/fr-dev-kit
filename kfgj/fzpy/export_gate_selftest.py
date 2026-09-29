"""
export_gate 自检 — ENH-1 Lane K1（≥10 例，覆盖任务书规定场景）。

场景清单:
  T01 xlsx 正例(魔数+行数+水印, 退出码 0)      T02 docx 正例(document.xml 水印)
  T03 pdf 正例(未压缩流+页数)                  T04 pdf 压缩流(FlateDecode)水印
  T05 伪魔数拒绝(txt 改名 .xlsx)               T06 docx 伪魔数(xlsx 内容改名 .docx)
  T07 行数不符(3≠5)                            T08 csv 正例(引号内换行精确计数)
  T09 csv 二进制伪装拒绝                       T10 xlsx 无 headerFooter → 水印 SKIPPED 诚实降级
  T11 docx 缺 document.xml → SKIPPED           T12 pdf CID 编码无字面文本 → SKIPPED
  T13 pdf 无 /Type /Pages → 页数 SKIPPED       T14 pdf 页数不足 → FAIL
  T15 空文件(G1 FAIL + 依赖链 SKIPPED)         T16 中文文件名(子进程真实 CLI)
  T17 退出码三态(0/1/2 子进程实测)             T18 --out JSON 结构化报告
  T19 文件不存在 → FAIL                        T20 xlsx sheet1.xml 缺失回退唯一工作表
  T21 pdf 长 /Kids 数组页数启发式回归（窗口截到 endobj）

所有产物为手造最小合法文件（zip 结构/最小 pdf 头），临时目录收尾自清。退出码: 0=全过 1=有失败。
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
import sys, os, io, json, zlib, zipfile, tempfile, shutil, subprocess
import importlib.util

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
GATE_PATH = os.path.join(HERE, "export_gate.py")
_spec = importlib.util.spec_from_file_location("export_gate", GATE_PATH)
eg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eg)

TMP = tempfile.mkdtemp(prefix="export_gate_selftest_")


# ════════════════
# 手造最小产物
# ════════════════

def wfile(name, data):
    path = os.path.join(TMP, name)
    with open(path, "wb") as f:
        f.write(data)
    return path


CT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="%s"/>'
            '</Types>')
CT_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
CT_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"


def make_xlsx(rows=3, footer_text=None, ct_family="spreadsheetml",
              sheet_member="xl/worksheets/sheet1.xml", include_document=True):
    buf = io.BytesIO()
    zf = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    zf.writestr("[Content_Types].xml", CT_TYPES % (CT_XLSX if ct_family == "spreadsheetml" else CT_DOCX))
    zf.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
    zf.writestr("xl/workbook.xml", '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>')
    sheet = ['<?xml version="1.0"?>',
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
             '<sheetData>']
    for r in range(1, rows + 1):
        sheet.append('<row r="%d"><c r="A%d" t="inlineStr"><is><t>r%d</t></is></c></row>' % (r, r, r))
    sheet.append('</sheetData>')
    if footer_text:
        sheet.append('<headerFooter><oddHeader>&amp;C&amp;KFF0000%s</oddHeader></headerFooter>' % footer_text)
    sheet.append('</worksheet>')
    if include_document:
        zf.writestr(sheet_member, "".join(sheet))
    zf.close()
    return buf.getvalue()


def make_docx(body_text=None, ct_family="wordprocessingml", include_document=True):
    buf = io.BytesIO()
    zf = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    zf.writestr("[Content_Types].xml", CT_TYPES % (CT_DOCX if ct_family == "wordprocessingml" else CT_XLSX))
    zf.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
    if include_document:
        body = "<w:t>%s</w:t>" % body_text if body_text else ""
        zf.writestr("word/document.xml",
                    '<?xml version="1.0"?>'
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    '<w:body><w:p><w:r>%s</w:r></w:p></w:body></w:document>' % body)
    zf.close()
    return buf.getvalue()


def make_pdf(literal=None, compressed=None, count=None, include_pages=True, cid_font=False):
    """最小合法 pdf 头。literal=未压缩流文本; compressed=压缩流文本; count=/Count 页数。"""
    out = [b"%PDF-1.4\n"]
    out.append(b"1 0 obj\n<< /Type /Catalog >>\nendobj\n")
    if include_pages:
        out.append(("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count %d >>\nendobj\n" % (count or 1)).encode("ascii"))
    res = b" /Resources << /Font << /F1 5 0 R >> >>" if cid_font else b""
    out.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R" + res + b" >>\nendobj\n")
    if literal is not None:
        content = ("BT (%s) Tj ET" % literal).encode("utf-8")
        out.append(b"4 0 obj\n<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream\nendobj\n")
    elif compressed is not None:
        content = zlib.compress(("BT (%s) Tj ET" % compressed).encode("utf-8"))
        out.append(b"4 0 obj\n<< /Filter /FlateDecode /Length %d >>\nstream\n" % len(content) + content + b"\nendstream\nendobj\n")
    else:
        content = b"BT /F1 12 Tf ET"
        out.append(b"4 0 obj\n<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream\nendobj\n")
    if cid_font:
        out.append(b"5 0 obj\n<< /Type /Font /Subtype /Type0 /BaseFont /SimSun /Encoding /Identity-H >>\nendobj\n")
    out.append(b"trailer\n<< /Root 1 0 R >>\n%%EOF\n")
    return b"".join(out)


# ════════════════
# 断言辅助
# ════════════════

def status_of(result, aid):
    for a in result["assertions"]:
        if a["id"] == aid:
            return a["status"]
    return None


def detail_of(result, aid):
    for a in result["assertions"]:
        if a["id"] == aid:
            return a["detail"]
    return None


def ids_of(result):
    return [a["id"] for a in result["assertions"]]


def run_cli(*argv):
    p = subprocess.run([sys.executable, GATE_PATH] + list(argv),
                       capture_output=True, timeout=60)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


# ════════════════
# 用例
# ════════════════

def t01_xlsx_all_pass():
    p = wfile("t01_产物.xlsx", make_xlsx(rows=3, footer_text="内部资料"))
    r = eg.run_gate(p, "auto", expect_rows=3, expect_text="内部资料")
    assert r["kind"] == "xlsx", r["kind"]
    for aid in ("G1", "G2", "G3", "G4"):
        assert status_of(r, aid) == "PASS", (aid, detail_of(r, aid))
    assert "G5" not in ids_of(r), "未给 --min-pages 不应出现 G5"
    assert r["exit_code"] == 0, r["exit_code"]


def t02_docx_pass():
    p = wfile("t02_产物.docx", make_docx(body_text="保密水印"))
    r = eg.run_gate(p, "auto", expect_text="保密水印")
    assert status_of(r, "G2") == "PASS", detail_of(r, "G2")
    assert status_of(r, "G4") == "PASS", detail_of(r, "G4")
    assert r["exit_code"] == 0


def t03_pdf_literal_pages():
    p = wfile("t03_产物.pdf", make_pdf(literal="内部资料", count=2))
    r = eg.run_gate(p, "auto", expect_text="内部资料", min_pages=2)
    assert status_of(r, "G4") == "PASS", detail_of(r, "G4")
    assert status_of(r, "G5") == "PASS", detail_of(r, "G5")
    assert r["exit_code"] == 0


def t04_pdf_compressed_watermark():
    p = wfile("t04_产物.pdf", make_pdf(compressed="内部资料", count=1))
    r = eg.run_gate(p, "auto", expect_text="内部资料")
    assert status_of(r, "G4") == "PASS", detail_of(r, "G4")
    assert r["exit_code"] == 0


def t05_txt_renamed_xlsx():
    p = wfile("t05_伪装.xlsx", b"hello, plain text world")
    r = eg.run_gate(p, "auto")
    assert status_of(r, "G2") == "FAIL", detail_of(r, "G2")
    assert r["exit_code"] == 1


def t06_xlsx_renamed_docx():
    p = wfile("t06_伪装.docx", make_xlsx(rows=1, ct_family="spreadsheetml"))
    r = eg.run_gate(p, "auto")
    assert status_of(r, "G2") == "FAIL", detail_of(r, "G2")
    assert "spreadsheetml" in detail_of(r, "G2"), detail_of(r, "G2")
    assert r["exit_code"] == 1


def t07_rows_mismatch():
    p = wfile("t07_产物.xlsx", make_xlsx(rows=3))
    r = eg.run_gate(p, "auto", expect_rows=5)
    assert status_of(r, "G3") == "FAIL", detail_of(r, "G3")
    assert r["exit_code"] == 1


def t08_csv_quoted_newline():
    p = wfile("t08_产物.csv", 'name,desc\na,"l1\nl2"\nb,ok\n'.encode("utf-8"))
    r = eg.run_gate(p, "auto", expect_rows=3)
    assert status_of(r, "G3") == "PASS", detail_of(r, "G3")
    assert r["exit_code"] == 0


def t09_csv_binary_disguise():
    p = wfile("t09_伪装.csv", bytes(range(256)))
    r = eg.run_gate(p, "auto")
    assert status_of(r, "G2") == "FAIL", detail_of(r, "G2")
    assert r["exit_code"] == 1


def t10_xlsx_no_headerfooter_skip():
    p = wfile("t10_产物.xlsx", make_xlsx(rows=2, footer_text=None))
    r = eg.run_gate(p, "auto", expect_text="内部资料")
    assert status_of(r, "G4") == "SKIPPED", detail_of(r, "G4")
    assert "headerFooter" in detail_of(r, "G4"), detail_of(r, "G4")
    assert r["exit_code"] == 2, r["exit_code"]


def t11_docx_no_document_xml():
    p = wfile("t11_产物.docx", make_docx(include_document=False))
    r = eg.run_gate(p, "auto", expect_text="保密水印")
    assert status_of(r, "G2") == "PASS", detail_of(r, "G2")
    assert status_of(r, "G4") == "SKIPPED", detail_of(r, "G4")
    assert r["exit_code"] == 2


def t12_pdf_cid_skip():
    p = wfile("t12_产物.pdf", make_pdf(cid_font=True, include_pages=True, count=1))
    r = eg.run_gate(p, "auto", expect_text="内部资料")
    assert status_of(r, "G4") == "SKIPPED", detail_of(r, "G4")
    assert r["exit_code"] == 2


def t13_pdf_no_pages_obj_skip():
    p = wfile("t13_产物.pdf", make_pdf(literal="x", include_pages=False))
    r = eg.run_gate(p, "auto", min_pages=1)
    assert status_of(r, "G5") == "SKIPPED", detail_of(r, "G5")
    assert r["exit_code"] == 2


def t14_pdf_pages_short():
    p = wfile("t14_产物.pdf", make_pdf(literal="x", count=2))
    r = eg.run_gate(p, "auto", min_pages=5)
    assert status_of(r, "G5") == "FAIL", detail_of(r, "G5")
    assert r["exit_code"] == 1


def t15_empty_file():
    p = wfile("t15_空.pdf", b"")
    r = eg.run_gate(p, "auto", expect_text="词", min_pages=1)
    assert status_of(r, "G1") == "FAIL", detail_of(r, "G1")
    for aid in ("G2", "G4", "G5"):
        assert status_of(r, aid) == "SKIPPED", (aid, detail_of(r, aid))
    assert r["exit_code"] == 1


def t16_chinese_filename_cli():
    p = wfile("中文水印_测试产物.xlsx", make_xlsx(rows=3, footer_text="内部资料"))
    rc, out, err = run_cli("--file", p, "--expect-rows", "3", "--expect-text", "内部资料")
    assert rc == 0, (rc, out[-400:], err[-200:])
    assert "全 PASS" in out, out[-300:]


def t17_exit_three_states():
    p0 = wfile("t17_pass.xlsx", make_xlsx(rows=2, footer_text="内部资料"))
    p1 = wfile("t17_fail.xlsx", make_xlsx(rows=2))
    p2 = wfile("t17_skip.xlsx", make_xlsx(rows=2, footer_text=None))
    rc0, _, _ = run_cli("--file", p0, "--expect-rows", "2", "--expect-text", "内部资料")
    rc1, _, _ = run_cli("--file", p1, "--expect-rows", "9")
    rc2, _, _ = run_cli("--file", p2, "--expect-text", "内部资料")
    assert (rc0, rc1, rc2) == (0, 1, 2), (rc0, rc1, rc2)


def t18_json_out():
    p = wfile("t18_产物.pdf", make_pdf(literal="内部资料", count=3))
    out_json = os.path.join(TMP, "t18_report.json")
    rc, _, _ = run_cli("--file", p, "--expect-text", "内部资料", "--min-pages", "3",
                       "--out", out_json)
    assert rc == 0
    with open(out_json, "r", encoding="utf-8") as f:
        payload = json.load(f)
    assert payload["exit_code"] == 0, payload["exit_code"]
    assert payload["summary"] == {"PASS": 4, "FAIL": 0, "SKIPPED": 0}, payload["summary"]
    assert payload["kind"] == "pdf"
    assert len(payload["assertions"]) == 4


def t19_missing_file():
    p = os.path.join(TMP, "不存在的产物.xlsx")
    r = eg.run_gate(p, "auto", expect_rows=1)
    assert status_of(r, "G1") == "FAIL", detail_of(r, "G1")
    assert status_of(r, "G3") == "SKIPPED", detail_of(r, "G3")
    assert r["exit_code"] == 1


def t20_sheet_fallback_single():
    p = wfile("t20_产物.xlsx", make_xlsx(rows=4, sheet_member="xl/worksheets/data1.xml"))
    r = eg.run_gate(p, "auto", expect_rows=4)
    assert status_of(r, "G3") == "PASS", detail_of(r, "G3")
    assert "回退唯一工作表" in detail_of(r, "G3"), detail_of(r, "G3")
    assert r["exit_code"] == 0


def t21_pdf_long_kids_count():
    """回归: /Kids 长数组把 /Count 挤出短窗口时，页数启发式仍可解析（窗口截到 endobj）。"""
    kids = b" ".join(b"%d 0 R" % i for i in range(3, 123))
    pdf = (b"%PDF-1.4\n"
           b"2 0 obj\n<< /Type /Pages /Kids [" + kids + b"] /Count 120 >>\nendobj\n"
           b"trailer\n<< /Root 2 0 R >>\n%%EOF\n")
    p = wfile("t21_产物.pdf", pdf)
    r = eg.run_gate(p, "auto", min_pages=120)
    assert status_of(r, "G5") == "PASS", detail_of(r, "G5")
    assert "120" in detail_of(r, "G5"), detail_of(r, "G5")


TESTS = [t01_xlsx_all_pass, t02_docx_pass, t03_pdf_literal_pages, t04_pdf_compressed_watermark,
         t05_txt_renamed_xlsx, t06_xlsx_renamed_docx, t07_rows_mismatch, t08_csv_quoted_newline,
         t09_csv_binary_disguise, t10_xlsx_no_headerfooter_skip, t11_docx_no_document_xml,
         t12_pdf_cid_skip, t13_pdf_no_pages_obj_skip, t14_pdf_pages_short, t15_empty_file,
         t16_chinese_filename_cli, t17_exit_three_states, t18_json_out, t19_missing_file,
         t20_sheet_fallback_single, t21_pdf_long_kids_count]


def main():
    print("═" * 55)
    print("  export_gate 自检 — ENH-1 Lane K1（%d 例）" % len(TESTS))
    print("═" * 55)
    n_pass = 0
    failures = []
    for t in TESTS:
        label = "%s (%s)" % (t.__name__, t.__doc__.strip().splitlines()[0] if t.__doc__ else "")
        try:
            t()
            n_pass += 1
            print("  ✅ %s" % label)
        except Exception as e:
            failures.append((t.__name__, repr(e)))
            print("  ❌ %s → %r" % (label, e))
    print("═" * 55)
    if failures:
        print("  ❌ %d/%d 例通过，失败: %s" % (n_pass, len(TESTS), [f[0] for f in failures]))
        rc = 1
    else:
        print("  ✅ %d/%d 例全过（每例含多条机械断言）" % (n_pass, len(TESTS)))
        rc = 0
    print("═" * 55)
    shutil.rmtree(TMP, ignore_errors=True)  # 临时目录收尾自清
    return rc


if __name__ == "__main__":
    sys.exit(main())
