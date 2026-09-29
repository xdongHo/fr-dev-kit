# -*- coding: utf-8 -*-
"""模板构件 BOM 查询工具：template_bom.sqlite（模板域装配图, CAR-014）
数据源: campaign/rebuild 产物 ET 解析(由 build_template_bom.py 建库), 承接旧 api_kb
bom 表的 装配查询+高频统计 职能(R-0002 旧表沉睡后由模板域活数据重造)。
用法:
  python query_template_bom.py node <名>        # 查构件(数据集/参数/控件类型/图表类型, 模糊)
  python query_template_bom.py edge <构件>      # 查某构件的全部关系(出入边)
  python query_template_bom.py assemble <seq>   # 某模板的装配结构(实体清单+关系全列)
  python query_template_bom.py usage <项目名>   # 项目会话裁剪: 只列该项目用到的构件/关系统计
  python query_template_bom.py highfreq [N]     # 高频构件 TopN(默认 10, 分数据集/参数/控件/图表)
  python query_template_bom.py dangling [项目]  # 悬挂引用检测(FS 408 形态: 引用未声明构件)
  python query_template_bom.py stats            # 库概况
"""
import os
import sys
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "template_bom.sqlite")


def conn():
    if not os.path.exists(DB):
        print("库不存在, 先跑: python build_template_bom.py"); sys.exit(1)
    return sqlite3.connect(DB)


def show_node(r):
    _id, kind, name, sub, proj, freq, attrs = r
    extra = f" 类型={sub}" if sub else ""
    att = f" 属性={attrs}" if attrs else ""
    print(f"[{kind}] {name}{extra}  项目={proj}  freq={freq}{att}")


def cmd_node(kw):
    c = conn()
    rows = c.execute("SELECT id,kind,name,subkind,project,freq,attrs FROM nodes "
                     "WHERE kind!='cell' AND (name LIKE ? OR subkind LIKE ?) "
                     "ORDER BY kind,freq DESC LIMIT 40",
                     (f"%{kw}%", f"%{kw}%")).fetchall()
    print(f"== 构件匹配 '{kw}': {len(rows)} 条(前 40) ==")
    for r in rows:
        show_node(r)
    c.close()


def cmd_edge(kw):
    c = conn()
    outs = c.execute("SELECT seq,project,src_kind,src,rel,dst_kind,dst,detail FROM edges "
                     "WHERE src LIKE ? OR dst LIKE ? LIMIT 60",
                     (f"%{kw}%", f"%{kw}%")).fetchall()
    print(f"== 构件 '{kw}' 的关系: {len(outs)} 条(前 60) ==")
    for seq, proj, sk, src, rel, dk, dst, det in outs:
        print(f"  #{seq}({proj})  {sk}:{src} --{rel}--> {dk}:{dst}"
              + (f"   [{det}]" if det else ""))
    c.close()


def cmd_assemble(seq):
    c = conn()
    rep = c.execute("SELECT kind,project,path,n_ds,n_param,n_widget,n_cell,n_chart,error "
                    "FROM reports WHERE seq=?", (seq,)).fetchone()
    if not rep:
        print(f"seq {seq} 不在抽样集内(重跑 build_template_bom.py --every N 或 --all)"); sys.exit(1)
    kind, proj, path, *n, err = rep
    print(f"== 模板 #{seq} {path} ({kind}, 项目={proj}) ==")
    print(f"   规模: 数据集{n[0]} 参数{n[1]} 控件{n[2]} 绑定单元格{n[3]} 图表{n[4]}"
          + (f"  ⚠解析异常:{err}" if err else ""))
    for title, sql, args in [
        ("数据集", "SELECT subkind,name,attrs FROM nodes WHERE kind='dataset' AND name IN "
                  "(SELECT dst FROM edges WHERE seq=? AND rel='USES' AND dst_kind='dataset') "
                  "ORDER BY name", (seq,)),
        ("参数", "SELECT '',name,attrs FROM nodes WHERE kind='param' AND name IN "
                "(SELECT dst FROM edges WHERE seq=? AND rel='HAS') ORDER BY name", (seq,)),
        ("控件", "SELECT subkind,name,'' FROM nodes WHERE kind='widget' AND project=? AND name IN "
                "(SELECT src FROM edges WHERE seq=? AND src_kind='widget') "
                "ORDER BY name LIMIT 50", (proj, seq)),
        ("图表", "SELECT subkind,name,attrs FROM nodes WHERE kind='chart' AND name LIKE ? "
                "ORDER BY name LIMIT 50", (f"{seq}:%",)),
    ]:
        rows = c.execute(sql, args).fetchall()
        print(f"   {title}({len(rows)}): " + "; ".join(
            f"{r[1]}{'<' + r[0] + '>' if r[0] else ''}" for r in rows[:20])
            + (" ..." if len(rows) > 20 else ""))
    print("   关系边:")
    for sk, src, rel, dk, dst, det in c.execute(
            "SELECT src_kind,src,rel,dst_kind,dst,detail FROM edges WHERE seq=? "
            "ORDER BY rel LIMIT 80", (seq,)):
        print(f"     {sk}:{src} --{rel}--> {dk}:{dst}" + (f"  [{det}]" if det else ""))
    dg = c.execute("SELECT typ,who,target FROM dangling WHERE seq=?", (seq,)).fetchall()
    print(f"   悬挂引用: {len(dg)} 条" + ("".join(f"\n     ⚠ {t} {w} -> {g}" for t, w, g in dg[:10]) if dg else " ✓"))
    c.close()


def cmd_usage(proj):
    c = conn()
    seqs = [r[0] for r in c.execute("SELECT seq FROM reports WHERE project LIKE ?",
                                    (f"%{proj}%",))]
    if not seqs:
        print(f"项目 '{proj}' 未命中(抽样集内无该项目, 尝试 dangling/highfreq 看全集)"); sys.exit(2)
    print(f"== 项目 '{proj}': {len(seqs)} 件模板在样(#{'#'.join(map(str, seqs[:15]))}"
          f"{'...' if len(seqs) > 15 else ''}) ==")
    q = "SELECT dst,COUNT(*) FROM edges WHERE project LIKE ? AND rel=? GROUP BY dst ORDER BY 2 DESC LIMIT 15"
    for rel, label in [("USES", "高频数据集"), ("HAS", "参数"), ("REFERENCES", "SQL 引用宏")]:
        rows = c.execute(q, (f"%{proj}%", rel)).fetchall()
        print(f"   {label}: " + ", ".join(f"{k}({v})" for k, v in rows))
    rows = c.execute("SELECT src_kind,src,rel,dst_kind,dst FROM edges WHERE project LIKE ? "
                     "AND rel='BINDS' LIMIT 30", (f"%{proj}%",)).fetchall()
    print("   绑定关系(前 30):")
    for sk, src, rel, dk, dst in rows:
        print(f"     {sk}:{src} --{rel}--> {dk}:{dst}")
    dg = c.execute("SELECT typ,COUNT(*) FROM dangling WHERE project LIKE ? GROUP BY typ",
                   (f"%{proj}%",)).fetchall()
    print("   悬挂: " + (", ".join(f"{t}({n})" for t, n in dg) if dg else "0 ✓"))
    c.close()


def cmd_highfreq(n=10):
    c = conn()
    print(f"== 高频构件 Top{n}（构件出现次数, 承接旧 bom 高频语义）==")
    for kind, label in [("dataset", "数据集"), ("param", "参数"),
                        ("widget", "控件类型"), ("chart", "图表类型")]:
        if kind in ("widget", "chart"):   # 按类型聚合(实例名随模板编号, 类型才是构件)
            rows = c.execute("SELECT subkind,COUNT(*) FROM nodes WHERE kind=? AND "
                             "subkind!='' GROUP BY subkind ORDER BY 2 DESC LIMIT ?",
                             (kind, n)).fetchall()
            print(f"   -- {label} --")
            for sub, freq in rows:
                print(f"     {freq:>3}x  <{sub}>")
        else:
            rows = c.execute("SELECT name,subkind,freq,project FROM nodes WHERE kind=? "
                             "ORDER BY freq DESC LIMIT ?", (kind, n)).fetchall()
            print(f"   -- {label} --")
            for name, sub, freq, proj in rows:
                print(f"     {freq:>3}x  {name}" + (f"  <{sub}>" if sub else ""))
    c.close()


def cmd_dangling(proj=None):
    c = conn()
    if proj:
        rows = c.execute("SELECT seq,project,typ,who,target FROM dangling "
                         "WHERE project LIKE ? ORDER BY typ,seq LIMIT 80",
                         (f"%{proj}%",)).fetchall()
        total = c.execute("SELECT COUNT(*) FROM dangling WHERE project LIKE ?",
                          (f"%{proj}%",)).fetchone()[0]
    else:
        rows = c.execute("SELECT seq,project,typ,who,target FROM dangling "
                         "ORDER BY typ,seq LIMIT 80").fetchall()
        total = c.execute("SELECT COUNT(*) FROM dangling").fetchone()[0]
    print(f"== 悬挂引用(引用了未声明构件, FS 408 事故形态): 共 {total} 条 ==")
    cur_typ = None
    for seq, p, typ, who, tgt in rows:
        if typ != cur_typ:
            print(f"   -- {typ} --")
            cur_typ = typ
        print(f"     #{seq}({p})  {who} -> {tgt}")
    if total > len(rows):
        print(f"   ...(其余 {total - len(rows)} 条用 dangling <项目名> 收窄)")
    print("提示: sql->param 命中≠必然报错(FR 运行时空串兜底), 但属「声明-引用闭合」缺陷, 建议人工确认")
    c.close()


def cmd_stats():
    c = conn()
    print("== template_bom.sqlite 概况 ==")
    for k, v in c.execute("SELECT key,value FROM meta"):
        print(f"   {k}: {v}")
    for kind, n in c.execute("SELECT kind,COUNT(*) FROM nodes GROUP BY kind"):
        print(f"   nodes[{kind}]: {n}")
    for rel, n in c.execute("SELECT rel,COUNT(*) FROM edges GROUP BY rel ORDER BY 2 DESC"):
        print(f"   edges[{rel}]: {n}")
    print(f"   抽样模板: {c.execute('SELECT COUNT(*) FROM reports').fetchone()[0]} 件, "
          f"项目族: {c.execute('SELECT COUNT(DISTINCT project) FROM reports').fetchone()[0]}")
    c.close()


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); sys.exit(0)
    cmd, kw = a[0], (a[1] if len(a) > 1 else None)
    if cmd == "node" and kw: cmd_node(kw)
    elif cmd == "edge" and kw: cmd_edge(kw)
    elif cmd == "assemble" and kw: cmd_assemble(int(kw))
    elif cmd == "usage" and kw: cmd_usage(kw)
    elif cmd == "highfreq": cmd_highfreq(int(kw) if kw else 10)
    elif cmd == "dangling": cmd_dangling(kw)
    elif cmd == "stats": cmd_stats()
    else: print(__doc__)
