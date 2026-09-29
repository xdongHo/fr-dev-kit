# -*- coding: utf-8 -*-
"""query_kb.py 加 semantic 命令：自然语言语义检索 parts/materials"""
import re
import os

Q = os.path.join(BASE, "query_kb.py")
src = open(Q, encoding="utf-8").read()

new_func = '''

def cmd_semantic(question, top=5, mock=False):
    """语义检索：自然语言 -> embedding -> 余弦相似度 top-k（parts + materials）"""
    import struct, math, sys
    from pathlib import Path
    VEC_DIR = Path(__file__).resolve().parent.parent / "jcxt/js"
    sys.path.insert(0, str(VEC_DIR))
    from build_vector_index import embed_texts, load_config
BASE = os.path.dirname(os.path.abspath(__file__))

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
'''
src = src.replace("\nif __name__ == \"__main__\":", new_func + "\nif __name__ == \"__main__\":", 1)

# 命令分发加 semantic
old_dispatch = '''    elif cmd == "echarts": cmd_echarts(kw)'''
new_dispatch = '''    elif cmd == "echarts": cmd_echarts(kw)
    elif cmd == "semantic":
        q = " ".join(args[1:])
        cmd_semantic(q, top=5, mock=("--mock" in args))'''
src = src.replace(old_dispatch, new_dispatch, 1)
open(Q, "w", encoding="utf-8").write(src)
print("query_kb.py 已加 semantic 命令")
