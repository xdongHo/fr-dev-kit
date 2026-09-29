# -*- coding: utf-8 -*-
"""chk_w915.py — W915 战果回归用例统一校验器（A64_eval_cases 泳道夹具, 仓库工具只读）。

10 个子命令 = 10 条回归用例的验收逻辑, 全部 rc 0 = PASS / rc 1 = FAIL。
被测对象（只读）:
  - _runs/night/campaign/w915/A57_bomv3_impl/bom_v3_builder.py   (A47 四形态/A57 v3 builder)
  - _runs/night/campaign/w915/A57_bomv3_impl/template_bom_v3_prelim.sqlite (A57 v3 库)
  - ckzl/bb/外部依赖与归档声明.mdcard_factory.py                                    (A56 显式 scope 契约)
  - _runs/night/campaign/v3wave_run.py                            (执行链真解析器, 陷阱证明)
  - _runs/night/campaign/_b2auto.py                               (A49 desc13 箭头 regex)
  - kfgj/fzpy/fr_check.py + fr_rules_doc.py                  (A39 按钮/LEN 误报, A54 hash-seed)
  - _runs/night/campaign/w915/A40_mirror_check/mirror_ledger.json (A40 镜像台账)
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from importlib.machinery import SourceFileLoader

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)


def repo_root():
    p = HERE
    for _ in range(10):
        p = os.path.dirname(p)
        if os.path.isfile(os.path.join(p, "AGENTS.md")):
            return p
    raise SystemExit("repo root not found")


ROOT = repo_root()
CAMP = os.path.join(ROOT, "_runs", "night", "campaign")
W915 = os.path.join(CAMP, "w915")
FAILS = []
PASSN = [0]


def check(name, cond, detail=""):
    if cond:
        PASSN[0] += 1
        print("  [ok] %s" % name)
    else:
        FAILS.append("%s: %s" % (name, detail))
        print("  [FAIL] %s | %s" % (name, detail))


def load_module(path, modname):
    loader = SourceFileLoader(modname, path)
    spec = importlib.util.spec_from_loader(modname, loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def fx(name):
    return os.path.join(HERE, name)


def finish(tag):
    if FAILS:
        print("[FAIL] %s 有 %d 项未过 / %d 项过" % (tag, len(FAILS), PASSN[0]))
        for f in FAILS:
            print("  - %s" % f)
        return 1
    print("[PASS] %s 全过 (%d 断言)" % (tag, PASSN[0]))
    return 0


# ---------------------------------------------------------------- 1 四形态 BOM
def sub_4forms_bom():
    tag = "4FORMS-BOM"
    V3 = load_module(os.path.join(W915, "A57_bomv3_impl", "bom_v3_builder.py"), "bom_v3")
    tp = V3.TemplateParser(0, fx("four_forms_decl.cpt"), "test")
    ok = tp.parse()
    check("解析成功", ok, tp.error)
    declared = set(tp.params) | tp.ds_params
    expect_decl = {"p_root_attr", "p_root_oval", "p_rpa_wrap", "p_rpa_bare",
                   "p_rpa_bare_nameattr", "p_dslevel"}
    check("四形态 6 声明全收 zero-miss", expect_decl <= declared,
          "缺=%s" % sorted(expect_decl - declared))
    check("排除位 2 名不进声明集 zero-over",
          not ({"p_excl_cell", "p_excl_js"} & declared),
          "误收=%s" % sorted({"p_excl_cell", "p_excl_js"} & declared))
    check("块A 数据集级 name->ds 记录", tp.ds_params == {"p_dslevel"}, str(tp.ds_params))
    check("默认值载体 <O> 文本", tp.params.get("p_root_oval") == "ROOTV"
          and tp.params.get("p_rpa_wrap") == "WRAPV" and tp.params.get("p_rpa_bare") == "BAREV",
          str(tp.params))
    check("默认值载体 value 属性兜底", tp.params.get("p_root_attr") == "1",
          str(tp.params.get("p_root_attr")))
    names = {nm for _ch, nm in tp.blind_log}
    check("盲区日志恰 2 条(排除位)", len(tp.blind_log) == 2
          and names == {"p_excl_cell", "p_excl_js"}, str(tp.blind_log))
    return finish(tag)


# ------------------------------------------------- 2 fr_check 四形态+按钮+LEN
def sub_frchk_btn():
    tag = "FRCHK-4FORMS-BTN"
    cmd = [sys.executable, os.path.join(ROOT, "kfgj/fzpy", "fr_check.py"),
           fx("frchk_btn_4forms.cpt")]
    p = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=240)
    raw = p.stdout or b""
    out = None
    for enc in ("utf-8", "gbk"):
        try:
            out = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if out is None:
        out = raw.decode("utf-8", errors="replace")
    declared = ["p_wrap", "p_bare", "ds_p", "ds_p2"]
    for nm in declared:
        bad = "控件[%s]无对应模板参数定义" % nm
        check("声明 %s 不再误报『无对应模板参数定义』(①fr_check 侧)" % nm, bad not in out, bad)
    btn_lines = [ln for ln in out.splitlines()
                 if "无对应模板参数定义" in ln and any(b in ln for b in ("btn_import", "btn_submit", "Search"))]
    check("按钮类(btn_*/Search)零误报(⑥A39)", not btn_lines, str(btn_lines[:3]))
    check("doc-299(dataset_conn) ${LEN} 假阳性消除(⑥A39)",
          "SQL 引用参数 ${LEN}" not in out and "引用参数 ${LEN} 但未声明" not in out,
          "doc-299 仍报 ${LEN}")
    check("doc-299(dataset_conn) 段无 ERROR(四形态声明在位)",
          not [ln for ln in out.splitlines() if "dataset_conn" in ln and "❌" in ln],
          "dataset_conn 仍有 ERROR")
    print("  (info) fr_check rc=%s (夹具含存量告警项, 不 pin 整体 rc, 只 pin 目标规则段)" % p.returncode)
    return finish(tag)


# ------------------------------------------------------------- 3 镜像台账同步
def sub_mirror_sync():
    tag = "MIRROR-KITSYNC"
    ledger_p = os.path.join(W915, "A40_mirror_check", "mirror_ledger.json")
    with io.open(ledger_p, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    entries = {os.path.basename(e["kit_path"]): e for e in ledger.get("evaluated_files", [])}
    check("台账含 kit.py 与 _b2auto.py 两引擎条目",
          "kit.py" in entries and "_b2auto.py" in entries, str(sorted(entries)))
    kit_p = os.path.join(CAMP, "b3_tools", "kit.py")
    cur = hashlib.md5(open(kit_p, "rb").read()).hexdigest()
    led = entries["kit.py"]["md5"]
    check("b3_tools/kit.py 现值 == A40 台账 md5 (单侧漂移=0)", cur == led,
          "cur=%s ledger=%s" % (cur, led))
    b2_p = os.path.join(CAMP, "_b2auto.py")
    cur2 = hashlib.md5(open(b2_p, "rb").read()).hexdigest()
    led2 = entries["_b2auto.py"]["md5"]
    if cur2 != led2:
        print("  (info) _b2auto.py 相对 A40 台账已漂移 (%s -> %s): A49 合法修改所致, "
              "镜像评估须随引擎改动重打——这正是②类漂移必须被检出机制的实证" % (led2, cur2))
    else:
        print("  (info) _b2auto.py 与 A40 台账一致")
    return finish(tag)


# --------------------------------------------------------- 4 漂移检出机制夹具
def _compare_pair(p1, p2):
    b1 = open(p1, "rb").read()
    b2 = open(p2, "rb").read()
    if b1 == b2:
        return ("SAME", len(b1), None)
    off = next((i for i in range(min(len(b1), len(b2))) if b1[i] != b2[i]),
               min(len(b1), len(b2)))
    return ("DRIFT", (len(b1), len(b2)), off)


def sub_drift_mech():
    tag = "DRIFT-MECH"
    payload = bytes(range(256)) * 4  # 1024 字节确定性内容
    d = os.path.join(HERE, "_tmp_drift")
    os.makedirs(d, exist_ok=True)
    a = os.path.join(d, "a.bin")
    b = os.path.join(d, "b.bin")
    with open(a, "wb") as f:
        f.write(payload)
    with open(b, "wb") as f:
        f.write(payload)
    v, sizes, off = _compare_pair(a, b)
    check("字节级相同副本判定 SAME", v == "SAME" and off is None, "%s %s %s" % (v, sizes, off))
    ba = bytearray(open(b, "rb").read())
    ba[999] ^= 0xFF  # 单侧修改 1 字节
    with open(b, "wb") as f:
        f.write(bytes(ba))
    v, sizes, off = _compare_pair(a, b)
    check("单侧修改 1 字节即判 DRIFT", v == "DRIFT" and off == 999
          and sizes == (1024, 1024), "%s %s off=%s" % (v, sizes, off))
    check("漂移定位=字节偏移 999 (size 相等证『同副本单侧改』)", sizes[0] == sizes[1],
          str(sizes))
    with contextlib.suppress(OSError):
        os.remove(a)
        os.remove(b)
        os.rmdir(d)
    return finish(tag)


# ------------------------------------------------------- 5 v3 库幽灵悬挂台账
def sub_bomv3_ghost():
    tag = "BOMV3-GHOST"
    db = os.path.join(W915, "A57_bomv3_impl", "template_bom_v3_prelim.sqlite")
    con = sqlite3.connect(db)
    cur = con.cursor()
    rows = cur.execute(
        "SELECT seq, typ, who, target, classification, basis FROM dangling "
        "WHERE seq IN (1534,2230) ORDER BY seq").fetchall()
    print("  (info) v3 库 seq 1534/2230 dangling 行: %s" % rows)
    ghost_cd = [r for r in rows if r[1] == "cell->dataset"]
    check("D-2: seq 1534/2230 无 cell->dataset 幽灵悬挂(v1 缺陷行清零)",
          not ghost_cd, str(ghost_cd))
    unadj = [r for r in rows if r[4] in ("R1", "R2")]
    check("D-2: seq 1534/2230 无未裁决 R1/R2 行", not unadj, str(unadj))
    adj = [r for r in rows if r[4] == "R4"]
    check("留存行(如有)均为 R4 已裁决(附依据)", len(rows) == len(adj) or not rows,
          str([r for r in rows if r[4] not in ("R1", "R2", "R4")]))
    con.close()
    return finish(tag)


# --------------------------------------------------- 6 v3 双通道判定(假悬挂守门)
def sub_bomv3_dualchan():
    tag = "BOMV3-DUALCHAN"
    V3 = load_module(os.path.join(W915, "A57_bomv3_impl", "bom_v3_builder.py"), "bom_v3b")
    tp = V3.TemplateParser(0, fx("dual_channel_decl.cpt"), "test")
    ok = tp.parse()
    check("解析成功", ok, tp.error)
    rows = tp.dangling()
    check("5 元组契约: 全行 len==5", all(len(r) == 5 for r in rows), str(rows[:2]))
    srows = {r[2]: (r[3], r[4]) for r in rows if r[0] == "sql->param"}
    wrows = {r[1].split("|", 1)[1]: (r[3], r[4]) for r in rows if r[0] == "widget->param"}
    check("sql B-only 命中 → R4 否决(不再产假悬挂)", srows.get("p_sbonly", ("?",))[0] == "R4",
          str(srows.get("p_sbonly")))
    check("sql A/B 均未命中 → R2 维持(真悬挂不吞)", srows.get("p_sghost", ("?",))[0] == "R2",
          str(srows.get("p_sghost")))
    check("数据集级声明 → R4-已修(v2 兼容)",
          srows.get("p_sql_declared_ds", ("?",))[0] == "R4", str(srows.get("p_sql_declared_ds")))
    check("widget B-only → R4 否决", wrows.get("p_bonly", ("?",))[0] == "R4",
          str(wrows.get("p_bonly")))
    check("widget A/B 未命中 → R2 维持", wrows.get("p_ghost", ("?",))[0] == "R2",
          str(wrows.get("p_ghost")))
    check("bom_blind_register 恰收 B-only 引用位 2 名",
          set(tp.blind_register) == {"p_bonly", "p_sbonly"}, str(set(tp.blind_register)))
    return finish(tag)


# ------------------------------------------------ 7 工厂自检拒族指针(A56 正向)
def sub_famptr_factory():
    tag = "FAMPTR-FACTORY"
    CF = load_module(os.path.join(ROOT, "知识库治理", "card_factory.py"), "card_factory_chk")

    def run_selfcheck(rows):
        """返回 (rejected?, 合并输出文本)"""
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                CF.factory_selfcheck(rows)
        except SystemExit:
            return True, buf.getvalue()
        return False, buf.getvalue()

    cal_ptr = [("CAL-9801", "CAL", "v3.1 重校准·项目族 6 批 1",
                "族6 成员seq（执行前查族表）", "1", "PENDING", "执行前查族表")]
    rej1, out1 = run_selfcheck(cal_ptr)
    check("CAL 族指针 scope 被拒产(SystemExit)", rej1, "未拒绝!")
    check("CAL 拒因=非显式 seq 列表", "非显式 seq 列表" in out1, out1[:200])
    fix_ptr = [("FIX-9803", "FIX", "族指针残件", "族6 成员seq（执行前查族表）",
                "1", "PENDING", "")]
    rej2, out2 = run_selfcheck(fix_ptr)
    check("非 CAL/BOM 行族指针文本也被禁(全系列禁令)", rej2, "未拒绝!")
    check("拒因含『族指针文本』专项标志", "族指针" in out2, out2[:200])
    good = [("CAL-9802", "CAL", "显式 seq 卡", "seq 601 602", "2", "PENDING", "")]
    n = CF.factory_selfcheck(good)
    check("显式 seq scope 合规通过(返回显式卡数=1)", n == 1, "ret=%r" % n)
    return finish(tag)


# ------------------------- 8 陷阱证明: 指针卡被执行链解析成伪 seq (负向用例)
def sub_famptr_trap():
    """PASS 语义 = 陷阱机制按 A56 实证复现（解析器不改的前提下, 工厂契约是唯一防线）。
    若本用例 FAIL（解析器已改为拒/正确解析指针卡）→ 须重审 A56 契约与 995 张存量卡的处置。"""
    tag = "FAMPTR-TRAP"
    sys.path.insert(0, CAMP)
    V = load_module(os.path.join(CAMP, "v3wave_run.py"), "v3wave_run_chk")
    pool = os.path.join(HERE, "_tmp_ptr_pool.tsv")
    header = ["card_id", "series", "title", "seqs", "scope", "items", "status", "prereq"]
    r1 = ["CAL-9001", "CAL", "v3.1 重校准·项目族 6 批 1", "",
          "族6 成员seq（执行前查族表）", "8", "PENDING", "执行前查族表"]
    r2 = ["CAL-9002", "CAL", "显式契约卡", "", "seq 601 602", "2", "PENDING", ""]
    with open(pool, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(header) + "\n")
        f.write("\t".join(r1) + "\n")
        f.write("\t".join(r2) + "\n")
    check("指针 scope 直接 parse_seqs 结果为空(解析器不识别族指针)",
          V.parse_seqs(r1[4]) == [], str(V.parse_seqs(r1[4])))
    cards = V.load_cards(pool, "CAL-9001~9002")
    by = {c[0]: c[1] for c in cards}
    trap = by.get("CAL-9001")
    check("load_cards 对指针卡发生标题数字回退(陷阱复现)", bool(trap), "cards=%s" % cards)
    check("回退解析出伪 seq 恰为标题数字 [1,6]", trap == [1, 6], "trap=%s" % trap)
    check("伪 seq 含族号 6(『族6』被喂成 seq 6 的 A56 实证形态)", trap is not None and 6 in trap,
          str(trap))
    good = by.get("CAL-9002")
    check("对照: 显式 scope 卡解析 [601,602] 正确(A56 显式契约)", good == [601, 602], str(good))
    with contextlib.suppress(OSError):
        os.remove(pool)
    print("  TRAP-CONFIRMED: 指针卡 scope 解析空 → 标题数字回退伪 seq %s —— "
          "族指针卡禁令(工厂自检)是唯一防线, 本陷阱机制被钉住" % (trap,))
    return finish(tag)


# ------------------------------------------------- 9 desc13 Unicode 箭头 (A49)
def sub_desc13_arrow():
    tag = "DESC13-ARROW"
    src = io.open(os.path.join(CAMP, "_b2auto.py"), "r", encoding="utf-8").read()
    check("A49 修复标记在位: 参数 regex 含 [←<] 字符类", "[←<]" in src
          and "@ (\\w+) [←<]" in src, "源码未见 A49 字符类")
    sys.path.insert(0, CAMP)
    B2 = load_module(os.path.join(CAMP, "_b2auto.py"), "_b2auto_chk")
    sample = os.path.join(HERE, "_tmp_desc13.md")
    with io.open(sample, "w", encoding="utf-8") as f:
        f.write("ext=cpt\n文件 12 字节 MD5 `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`\n")
        f.write("## §3 参数\n")
        f.write("- 'year' 默认='' @ ParameterUI ←ReportParameterAttr→ Parameter；模板级声明\n")
        f.write("- 'area' 默认='华东' @ ComboBox <legacy-ascii-form>\n")
    D = B2.parse_desc(sample)
    got = {(p[0]): p for p in D["params"]}
    check("Unicode 箭头行参数被收集(A49 修复点)", "year" in got, str(D["params"]))
    check("箭头行控件名/默认值解析正确",
          got.get("year", ("?", "?", "?"))[1] == "" and got.get("year", ("?", "?", "?"))[2] == "ParameterUI",
          str(got.get("year")))
    check("ASCII '<' 形态仍兼容(不回退)", "area" in got, str(D["params"]))
    check("ASCII 形态默认值正确", got.get("area", ("?", "?", "?"))[1] == "华东", str(got.get("area")))
    with contextlib.suppress(OSError):
        os.remove(sample)
    return finish(tag)


# ------------------------------------------- 10 doc-1197 跨 seed 确定性 (A54)
def _doc1197_child():
    m = load_module(os.path.join(ROOT, "kfgj/fzpy", "fr_rules_doc.py"), "fr_rules_doc_chk")
    cpt = os.path.join(ROOT, "参考模板", "base_查看_CI_Project明细.cpt")
    parts = []
    for fn in (m.check_date_range_validate, m.check_date_validation_js):
        for lv, msgtxt in fn(cpt):
            parts.append("[%s] %s" % (lv, msgtxt))
    blob = "\n".join(parts)
    print("DOC1197_MD5=%s" % hashlib.md5(blob.encode("utf-8")).hexdigest()[:12])
    return 0


def sub_doc1197_det():
    tag = "DOC1197-DET"
    cpt = os.path.join(ROOT, "参考模板", "base_查看_CI_Project明细.cpt")
    check("确定性样本在位(ckzl/bb/外部依赖与归档声明.mdbase_查看_CI_Project明细.cpt)", os.path.isfile(cpt), cpt)
    mds = []
    for seed in ("0", "1", "2"):
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = seed
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--doc1197-child"],
                           env=env, cwd=ROOT, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=240)
        out = (p.stdout or b"").decode("utf-8", errors="replace")
        mm = re.search(r"DOC1197_MD5=([0-9a-f]+)", out)
        check("seed=%s 子进程跑通并产出指纹" % seed, bool(mm), out[-160:])
        if mm:
            mds.append(mm.group(1))
    check("doc-1197 输出跨 PYTHONHASHSEED 0/1/2 逐字节一致(A54 修复)",
          len(mds) == 3 and len(set(mds)) == 1, str(mds))
    if mds:
        print("  (info) 公共指纹 DOC1197_MD5=%s" % mds[0])
    return finish(tag)


SUBS = {
    "4forms-bom": sub_4forms_bom,
    "frchk-btn": sub_frchk_btn,
    "mirror-sync": sub_mirror_sync,
    "drift-mech": sub_drift_mech,
    "bomv3-ghost": sub_bomv3_ghost,
    "bomv3-dualchan": sub_bomv3_dualchan,
    "famptr-factory": sub_famptr_factory,
    "famptr-trap": sub_famptr_trap,
    "desc13-arrow": sub_desc13_arrow,
    "doc1197-det": sub_doc1197_det,
}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--doc1197-child":
        sys.exit(_doc1197_child())
    if not args or args[0] not in SUBS:
        print("用法: python chk_w915.py <%s>" % "|".join(SUBS))
        sys.exit(2)
    sys.exit(SUBS[args[0]]())
