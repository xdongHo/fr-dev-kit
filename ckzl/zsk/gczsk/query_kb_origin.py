# -*- coding: utf-8 -*-
"""ckzl/zsk/gczsk查询工具：api_kb.sqlite（人机料法环 5M1E）
用法:
  python query_kb.py part <关键词>       # 按 类名/方法名/说明 查零件
  python query_kb.py class <类名>         # 查某个类的所有方法
  python query_kb.py cat <类别>           # 按类别列零件
  python query_kb.py bom <零件号或关键词>  # 查某零件的装配关系（父->子）
  python query_kb.py route               # 列出全部工艺路线
  python query_kb.py route <工艺号>       # 查某工艺路线工序
  python query_kb.py mat [关键词]         # 查物料(料)
  python query_kb.py machine [关键词]     # 查机器(机/脚本)
  python query_kb.py env [关键词]         # 查环境(环)
  python query_kb.py person              # 查人员(人)
  python query_kb.py 5m1e                # 人机料法环总览
"""
import sqlite3, os, sys

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_kb.sqlite")

def conn():
    return sqlite3.connect(DB)

def show_part(row):
    pid, pno, name, cls, sig, cat, desc, params, ret, pit, src, ver = row[:12]
    print(f"[{pno}] {name}  ({cls})  {'★实测' if ver else '·文档'}")
    print(f"    签名: {sig}")
    if desc: print(f"    功能: {desc}")
    if params: print(f"    参数: {params}")
    if pit: print(f"    ⚠ 坑: {pit}")
    if src: print(f"    来源: {src}")
    print()

def cmd_part(kw):
    c = conn()
    rows = c.execute("SELECT part_id,part_no,name,class_name,signature,category,description,params,returns,pitfalls,source,verified FROM parts WHERE part_no LIKE ? OR name LIKE ? OR class_name LIKE ? OR description LIKE ?",
                     (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
    print(f"== 零件匹配 '{kw}': {len(rows)} 条 ==")
    for r in rows: show_part(r)
    c.close()

def cmd_class(cls):
    c = conn()
    rows = c.execute("SELECT part_id,part_no,name,class_name,signature,category,description,params,returns,pitfalls,source,verified FROM parts WHERE class_name LIKE ?", (f"%{cls}%",)).fetchall()
    print(f"== 类 '{cls}': {len(rows)} 个方法 ==")
    for r in rows: show_part(r)
    c.close()

def cmd_cat(cat):
    c = conn()
    rows = c.execute("SELECT part_id,part_no,name,class_name,signature,category,description,params,returns,pitfalls,source,verified FROM parts WHERE category LIKE ?", (f"%{cat}%",)).fetchall()
    print(f"== 类别 '{cat}': {len(rows)} 个零件 ==")
    for r in rows: show_part(r)
    c.close()

def cmd_bom(kw):
    c = conn()
    rows = c.execute("SELECT part_id,part_no,name,class_name,signature,category,description,params,returns,pitfalls,source,verified FROM parts WHERE part_no=? OR name LIKE ?", (kw, f"%{kw}%")).fetchall()
    if not rows:
        print(f"未找到零件: {kw}"); return
    for p in rows:
        pid, pno = p[0], p[1]
        print(f"== {pno} {p[2]} 的装配关系 ==")
        ch = c.execute("""SELECT b.rel_type, b.qty, b.note, p.part_no, p.name, p.class_name
                          FROM bom b JOIN parts p ON b.child_part_id=p.part_id
                          WHERE b.parent_part_id=? ORDER BY b.rel_type""", (pid,)).fetchall()
        comp = [x for x in ch if x[0] != "METHOD_OF"]
        meth = [x for x in ch if x[0] == "METHOD_OF"]
        for rel, qty, note, cpno, cname, ccls in comp:
            print(f"  └─{rel:8s} → [{cpno}] {cname} ({ccls}) {('· '+note) if note else ''}")
        if meth:
            print(f"  └─METHOD_OF → 该类 {len(meth)} 个方法（用 query_kb.py methods {pno} 查看）")
        pa = c.execute("""SELECT b.rel_type, p.part_no, p.name, p.class_name, b.note
                          FROM bom b JOIN parts p ON b.parent_part_id=p.part_id
                          WHERE b.child_part_id=?""", (pid,)).fetchall()
        for rel, ppno, pname, pcls, note in pa:
            print(f"  ┌─{rel:8s} ← [{ppno}] {pname} ({pcls}) {('· '+note) if note else ''}")
        print()
    c.close()

def cmd_route(no=None):
    c = conn()
    if no:
        rows = c.execute("""SELECT r.routing_no, r.routing_name, r.step_no, r.work_center, p.part_no, p.name, r.op_desc, r.output, r.machine
                            FROM routing r LEFT JOIN parts p ON r.part_id=p.part_id
                            WHERE r.routing_no=? ORDER BY r.step_no""", (no,)).fetchall()
        if not rows:
            print(f"未找到工艺: {no}"); return
        print(f"== 工艺 {rows[0][0]}: {rows[0][1]} ==")
        for r in rows:
            part = f"[{r[4]}] {r[5]}" if r[4] else "—"
            mach = f" [机:{r[8]}]" if r[8] else ""
            print(f"  {r[2]:2d}. [{r[3]:12s}] {part:30s} {r[6]}{mach}")
        print()
    else:
        names = c.execute("SELECT routing_no, routing_name, count(*) FROM routing GROUP BY routing_no ORDER BY routing_no").fetchall()
        print("== 全部工艺路线 ==")
        for no2, name, n in names:
            print(f"  {no2}: {name} ({n} 道工序)")
    c.close()

# ---------- 5M1E 查询 ----------
def cmd_mat(kw=None):
    c = conn()
    if kw:
        rows = c.execute("SELECT * FROM materials WHERE mat_no LIKE ? OR name LIKE ? OR category LIKE ? OR type LIKE ?",
                         (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
        print(f"== 物料(料)匹配 '{kw}': {len(rows)} 条 ==")
    else:
        rows = c.execute("SELECT * FROM materials ORDER BY usage_count DESC, type, mat_no").fetchall()
        print(f"== 全部物料(料): {len(rows)} 条 (按使用次数降序) ==")
    for m in rows:
        uc = m[13] if len(m) > 13 and m[13] else 0   # usage_count 列(新库)
        up = m[14] if len(m) > 14 and m[14] else ""  # used_projects 列(新库)
        used = f" 用量={uc}" if uc else ""
        if up: used += f" 项目=[{up}]"
        print(f"[{m[1]}] ({m[3]:8s}/{m[4] or '-':6s}) {m[2]:34s} {m[5] or ''}{used}")
    c.close()

def cmd_usage(project=None):
    """料的使用台账(WMS): query_kb.py usage [项目名]
    无参=全部台账; 有参=只显示该项目用到的物料(会话裁剪:开发时只加载本项目物料)"""
    c = conn()
    if project:
        rows = c.execute("""SELECT u.project, u.mat_no, m.name, m.path, u.role, u.count, u.note
                            FROM material_usage u JOIN materials m ON u.mat_no = m.mat_no
                            WHERE u.project LIKE ? ORDER BY u.role, u.count DESC""", (f"%{project}%",)).fetchall()
        print(f"== 料使用台账 匹配项目 '{project}': {len(rows)} 条 (会话裁剪: 只加载这些物料) ==")
    else:
        rows = c.execute("""SELECT u.project, u.mat_no, m.name, m.path, u.role, u.count, u.note
                            FROM material_usage u JOIN materials m ON u.mat_no = m.mat_no
                            ORDER BY u.project, u.role, u.count DESC""").fetchall()
        print(f"== 料使用台账(WMS): {len(rows)} 条 ==")
    for p, mno, name, path, role, cnt, note in rows:
        print(f"[{p}] {mno} ({role:7s}) x{cnt:3d}  {name}  {path or ''}  {note or ''}")
    if project:
        # 项目物料使用汇总(含半成品)
        r = c.execute("""SELECT SUM(count) FROM material_usage WHERE project LIKE ?""", (f"%{project}%",)).fetchone()
        w = c.execute("""SELECT SUM(count) FROM material_usage WHERE project LIKE ? AND role='WIP'""", (f"%{project}%",)).fetchone()
        print(f"  合计使用 {r[0] or 0} 次,其中半成品(WIP) {w[0] or 0} 次")
    c.close()

def cmd_machine(kw=None):
    c = conn()
    if kw:
        rows = c.execute("SELECT * FROM machines WHERE m_no LIKE ? OR name LIKE ? OR function LIKE ?",
                         (f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
        print(f"== 机器(机)匹配 '{kw}': {len(rows)} 条 ==")
    else:
        rows = c.execute("SELECT * FROM machines ORDER BY m_no").fetchall()
        print(f"== 全部机器(机): {len(rows)} 条 ==")
    for m in rows:
        print(f"[{m[1]}] {m[2]} ({m[5] or ''})")
        if m[7]: print(f"    对应工艺: {m[7]}")
    c.close()

def cmd_env(kw=None):
    c = conn()
    if kw:
        rows = c.execute("SELECT * FROM environments WHERE e_no LIKE ? OR name LIKE ? OR category LIKE ? OR version LIKE ? OR location LIKE ? OR note LIKE ?",
                         (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
        print(f"== 环境(环)匹配 '{kw}': {len(rows)} 条 ==")
    else:
        rows = c.execute("SELECT * FROM environments ORDER BY e_no").fetchall()
        print(f"== 全部环境(环): {len(rows)} 条 ==")
    for e in rows:
        print(f"[{e[1]}] {e[2]} ({e[3] or ''} {e[4] or ''}) {e[7] or ''}")
    c.close()

def cmd_person():
    c = conn()
    rows = c.execute("SELECT * FROM personnel ORDER BY code").fetchall()
    print(f"== 人员(人): {len(rows)} 条 ==")
    for p in rows:
        print(f"[{p[1]}] {p[2]} ({p[3]}) {p[4] or ''}")
    c.close()

def cmd_5m1e():
    print("=" * 60)
    print("人机料法环(5M1E) ckzl/zsk/gczsk总览")
    print("=" * 60)
    cmd_person(); cmd_mat(); cmd_machine(); cmd_env()
    c = conn()
    rows = c.execute("SELECT routing_no, routing_name, count(*), sum(case when machine is not null then 1 else 0 end) FROM routing GROUP BY routing_no ORDER BY routing_no").fetchall()
    print("== 法(工艺路线) + 机械化覆盖 ==")
    for rno, name, n, mech in rows:
        print(f"  {rno}: {name} ({n} 工序, 已机械化 {mech or 0} 道)")
    c.close()


def cmd_echarts(kw=None):
    c = conn()
    if kw:
        rows = c.execute("""SELECT echarts_type, echarts_variant, fr_name, fr_part_no, fr_class, key_mapping, status, notes
                            FROM echarts_fr_map WHERE echarts_type LIKE ? OR fr_name LIKE ? OR echarts_variant LIKE ?
                            ORDER BY echarts_type""", (f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
        print(f"== ECharts->FR 映射匹配 '{kw}': {len(rows)} 条 ==")
    else:
        rows = c.execute("""SELECT echarts_type, echarts_variant, fr_name, fr_part_no, fr_class, key_mapping, status, notes
                            FROM echarts_fr_map ORDER BY echarts_type""").fetchall()
        print(f"== 全部 ECharts->FR 映射: {len(rows)} 条 ==")
    for r in rows:
        print(f"[{r[0]}] {r[1] or ''} → {r[2]} ({r[3] or '-'})")
        if r[4] and r[4] != "-": print(f"    类: {r[4]}")
        if r[5]: print(f"    映射: {r[5]}")
        print(f"    状态: {r[6]}  {r[7] or ''}")
        print()
    c.close()


def cmd_semantic(question, top=5, mock=False):
    """语义检索：自然语言 -> embedding -> 余弦相似度 top-k（parts + materials）"""
    import struct, math, sys
    from pathlib import Path
    VEC_DIR = Path(__file__).resolve().parent.parent / "jcxt/js"
    sys.path.insert(0, str(VEC_DIR))
    from build_vector_index import embed_texts, load_config

    cfg = None
    if mock:
        cfg = None
    else:
        try:
            cfg = load_config()
        except FileNotFoundError:
            print("[提示] config.toml 不存在 → 自动用 --mock 降级")
            mock = True

    c = conn()
    # 收集所有带向量的行
    items = []  # (sim_payload, vec)
    parts = c.execute("SELECT part_no, name, class_name, description, embed_vec, embed_dim, embed_model FROM parts WHERE embed_vec IS NOT NULL").fetchall()
    mats  = c.execute("SELECT mat_no, name, category, description, embed_vec, embed_dim, embed_model FROM materials WHERE embed_vec IS NOT NULL").fetchall()

    for p in parts:
        dim = p[5] or 512
        vec = struct.unpack(f"<{dim}f", p[4])
        items.append((f"[{p[0]}] {p[1]} ({p[2]})", vec))
    for m in mats:
        dim = m[5] or 512
        vec = struct.unpack(f"<{dim}f", m[4])
        items.append((f"[{m[0]}] {m[1]} (料/{m[2]})", vec))

    if not items:
        print("向量为空，先运行: python embed_parts.py [--mock]"); return

    qvec = embed_texts([question], cfg, mock=mock)[0]
    qnorm = math.sqrt(sum(x*x for x in qvec)) or 1.0
    q = [x/qnorm for x in qvec]

    scored = []
    for label, vec in items:
        sim = sum(a*b for a, b in zip(q, vec))
        scored.append((sim, label))
    scored.sort(key=lambda s: -s[0])

    print(f"== 语义检索: {question} (top {top}) ==")
    for sim, label in scored[:top]:
        print(f"  {sim:.3f}  {label}")
    c.close()


def cmd_methods(kw):
    """列出组件(类)的所有方法: query_kb.py methods <零件号或类名关键词>"""
    c = conn()
    if kw.upper().startswith("P-"):
        row = c.execute("SELECT part_id, part_no, name, class_name FROM parts WHERE part_no=?", (kw.upper(),)).fetchone()
    else:
        # 先按类名找到类代表（name==类短名），取 part_id 最小的那个
        rows = c.execute("SELECT part_id, part_no, name, class_name FROM parts WHERE class_name LIKE ? ORDER BY part_id", (f"%{kw}%",)).fetchall()
        row = None
        for r in rows:
            short = r[3].split(".")[-1] if r[3] and "." in r[3] else ""
            if r[2] == short:
                row = r; break
        if row is None and rows:
            row = rows[0]
    if not row:
        print(f"未找到组件: {kw}"); return
    pid, pno, name, cls = row
    print(f"== {pno} {name} ({cls}) 的全部方法 ({len(list(c.execute('SELECT 1 FROM bom WHERE parent_part_id=? AND rel_type=?', (pid, 'METHOD_OF'))))} 个) ==")
    ms = c.execute("""SELECT p.part_no, p.name FROM bom b JOIN parts p ON b.child_part_id=p.part_id
                      WHERE b.parent_part_id=? AND b.rel_type='METHOD_OF' ORDER BY p.name""", (pid,)).fetchall()
    for mpno, mname in ms:
        print(f"  {mpno}  {mname}")
    c.close()

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(0)
    cmd = args[0]
    kw = args[1] if len(args) > 1 else None
    if cmd == "part" and kw: cmd_part(kw)
    elif cmd == "class" and kw: cmd_class(kw)
    elif cmd == "cat" and kw: cmd_cat(kw)
    elif cmd == "bom" and kw: cmd_bom(kw)
    elif cmd == "route": cmd_route(kw)
    elif cmd == "mat": cmd_mat(kw)
    elif cmd == "usage": cmd_usage(kw)
    elif cmd == "machine": cmd_machine(kw)
    elif cmd == "env": cmd_env(kw)
    elif cmd == "person": cmd_person()
    elif cmd == "5m1e": cmd_5m1e()
    elif cmd == "echarts": cmd_echarts(kw)
    elif cmd == "methods": cmd_methods(kw)
    elif cmd == "semantic":
        q = " ".join(args[1:])
        cmd_semantic(q, top=5, mock=("--mock" in args))
    else: print(__doc__)
