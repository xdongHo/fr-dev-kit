# -*- coding: utf-8 -*-
"""embed_parts.py v2: 断点续传 + 重试增强
- 已嵌入的零件跳过（embed_model 匹配当前模型）
- 每批失败自动重试（指数退避）
- 中断后重跑只补缺失
"""
import os, sqlite3, struct, sys, time
from pathlib import Path

BASE = Path(os.path.dirname(os.path.abspath(__file__))).parent  # 仓库根(ckzl/zsk/gczsk的上一级)
VEC_DIR = BASE / "jcxt/js"
sys.path.insert(0, str(VEC_DIR))
from build_vector_index import embed_texts, load_config  # noqa

DB = BASE / "ckzl/zsk/gczsk" / "api_kb.sqlite"
USE_MOCK = "--mock" in sys.argv
BATCH = 10
MAX_RETRY = 5

def vec2blob(vec):
    return struct.pack(f"<{len(vec)}f", *vec)

def embed_batches(texts, keys, cfg, mock, conn, table, id_col):
    """分批嵌入，支持断点续传（keys 里已嵌入的跳过）"""
    todo = []
    for key, text in zip(keys, texts):
        has = conn.execute(f"SELECT 1 FROM {table} WHERE {id_col}=? AND embed_vec IS NOT NULL AND embed_model=?", (key, model)).fetchone()
        if not has:
            todo.append((key, text))
    print(f"  待嵌入: {len(todo)}（跳过已完成的 {len(texts)-len(todo)}）")
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i+BATCH]
        ok = False
        for attempt in range(1, MAX_RETRY+1):
            try:
                vecs = embed_texts([t for _, t in chunk], cfg, mock=mock)
                for (key, _), vec in zip(chunk, vecs):
                    conn.execute(f"UPDATE {table} SET embed_vec=?, embed_dim=?, embed_model=? WHERE {id_col}=?", (vec2blob(vec), dim, model, key))
                conn.commit()
                ok = True
                break
            except Exception as e:
                wait = 2 ** attempt
                print(f"    批 {i//BATCH+1} 失败({type(e).__name__}): {str(e)[:80]} → {wait}s 后重试 {attempt}/{MAX_RETRY}")
                time.sleep(wait)
        if not ok:
            print(f"    批 {i//BATCH+1} 最终失败，跳过（重跑可续）")
        if (i//BATCH+1) % 20 == 0:
            print(f"    进度: {i+len(chunk)}/{len(todo)}")

def main():
    global dim, model
    if USE_MOCK:
        cfg, dim, model = None, 512, "mock-bigram-512"
    else:
        cfg = load_config()
        emb = cfg["embedding"]
        dim = int(emb.get("dimensions", 1024))
        model = emb["model"]

    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT part_no, name, class_name, signature, description, pitfalls, cn_name FROM parts").fetchall()
    texts = [f"{p[0]} {p[1]} {p[2]} {p[3] or ''} {p[4] or ''} {p[5] or ''} 中文名:{p[6] or ''}" for p in rows]
    keys = [p[0] for p in rows]
    print(f"parts: {len(texts)} 条 → ({model}, {dim}D)")
    embed_batches(texts, keys, cfg, USE_MOCK, conn, "parts", "part_no")
    print("  parts 完成")

    rows2 = conn.execute("SELECT mat_no, name, type, category, path, description FROM materials").fetchall()
    texts2 = [f"{m[0]} {m[1]} {m[2] or ''} {m[3] or ''} {m[4] or ''} {m[5] or ''}" for m in rows2]
    keys2 = [m[0] for m in rows2]
    print(f"materials: {len(texts2)} 条")
    embed_batches(texts2, keys2, cfg, USE_MOCK, conn, "materials", "mat_no")
    print("  materials 完成")

    n1 = conn.execute("SELECT count(*) FROM parts WHERE embed_vec IS NOT NULL").fetchone()[0]
    n2 = conn.execute("SELECT count(*) FROM materials WHERE embed_vec IS NOT NULL").fetchone()[0]
    print(f"向量已写入: parts={n1}/{len(rows)}, materials={n2}/{len(rows2)}")
    conn.close()

if __name__ == "__main__":
    main()
