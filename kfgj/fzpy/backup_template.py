#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backup_template.py — 模板修改前统一备份（用户目录 %USERPROFILE%\\.fr_dev_kit\\backup\\）

SOP STEP 4 要求"改模板前先取结构快照"；本工具补齐另一半：动手改文件前先做备份。
备份落用户私有目录（不进套件，套件外发/拷贝不带用户数据；替代散落的 _backup_时间戳 就地目录）。

用法：
    python kfgj/fzpy/backup_template.py <模板.cpt|frm> [更多文件...] [-m "本次要改什么"]
    python kfgj/fzpy/backup_template.py --list [模板名]              # 查看备份（每模板最近5份）
    python kfgj/fzpy/backup_template.py --prune [模板名] --keep 20   # 清理旧备份

归档结构：
    ~/.fr_dev_kit/backup/<模板名>/<YYYYmmdd_HHMMSS>/<原文件名> (+ _note.txt 备注可选)
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
import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import userdir


def do_backup(files, note=None):
    userdir.ensure()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    made = []
    for f in files:
        src = Path(f)
        if not src.is_file():
            print(f"⚠ 跳过（不存在）: {src}")
            continue
        dest_dir = userdir.BACKUP_DIR / src.stem / stamp
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
        if note:
            (dest_dir / "_note.txt").write_text(note, encoding="utf-8")
        made.append(dest)
        print(f"✅ {src.name} → {dest}")
    return made


def do_list(name=None):
    root = userdir.BACKUP_DIR
    if not root.is_dir() or not any(root.iterdir()):
        print("(暂无备份)")
        return
    names = [root / name] if name else sorted(p for p in root.iterdir() if p.is_dir())
    for d in names:
        if not d.is_dir():
            print(f"⚠ 没有该模板的备份: {d.name}")
            continue
        vers = sorted(p for p in d.iterdir() if p.is_dir())
        print(f"{d.name}（{len(vers)} 份）")
        for v in vers[-5:]:
            files = sorted(p.name for p in v.iterdir() if p.name != "_note.txt")
            note = ""
            np = v / "_note.txt"
            if np.is_file():
                note = " — " + np.read_text(encoding="utf-8").strip()[:40]
            print(f"  {v.name}  {files}{note}")


def do_prune(name=None, keep=20):
    root = userdir.BACKUP_DIR
    targets = [root / name] if name else (sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else [])
    removed = 0
    for d in targets:
        if not d.is_dir():
            continue
        vers = sorted(p for p in d.iterdir() if p.is_dir())
        for old in (vers[:-keep] if keep > 0 else vers):
            shutil.rmtree(old)
            removed += 1
            print(f"🗑 已清理: {old}")
    print(f"共清理 {removed} 份（每模板保留最近 {keep} 份）")


def main():
    ap = argparse.ArgumentParser(description="模板修改前统一备份（用户目录 ~/.fr_dev_kit/backup）")
    ap.add_argument("files", nargs="*", help="要备份的模板文件（可多个；--list/--prune 时可传模板名过滤）")
    ap.add_argument("-m", "--note", help="备注（写入 _note.txt）")
    ap.add_argument("--list", action="store_true", help="列出备份")
    ap.add_argument("--prune", action="store_true", help="清理旧备份（配合 --keep）")
    ap.add_argument("--keep", type=int, default=20, help="每模板保留份数（默认 20，--prune 时生效）")
    args = ap.parse_args()

    if args.list:
        do_list(args.files[0] if args.files else None)
        return
    if args.prune:
        do_prune(args.files[0] if args.files else None, args.keep)
        return
    if not args.files:
        ap.error("请传入要备份的文件，或用 --list / --prune")
    made = do_backup(args.files, args.note)
    sys.exit(0 if made else 1)


if __name__ == "__main__":
    main()
