#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""advisory 文件锁 —— 跨会话/跨 Agent 的线上 cpt 写入协调（AGENTS.md §7 文件锁纪律，2026-09-07 用户裁决增补）

用法（任意目录执行）:
  python kfgj/fzpy/file_lock.py acquire <目标文件> --holder <会话/agent标识> [--task <任务名>] [--ttl 30]
  python kfgj/fzpy/file_lock.py release <目标文件> --holder <会话/agent标识>
  python kfgj/fzpy/file_lock.py check   <目标文件>
  python kfgj/fzpy/file_lock.py list

规则:
  - 锁文件落 <仓根>/_runs/locks/<basename>.<sha1前12>.lock（JSON: holder/task/acquired/heartbeat/ttl分钟）
  - acquire 遇有效锁（heartbeat 距今 < ttl 分钟）→ 退出码 1 并打印持有者（排队/STANDBY，禁止强写）
  - 锁过期（超 ttl 无心跳）→ 自动抢占，旧锁改名 .stale-N 留痕
  - release 仅持有者本人可解（防误释放他人锁）
  - advisory 性质：挡不住不读锁的进程，配套防线（写前 mtime/md5 快照 + 收尾复验）不可省
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
import argparse, hashlib, json, os, sys, time

def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def lock_path(target):
    ap = os.path.abspath(target)
    key = hashlib.sha1(ap.encode("utf-8")).hexdigest()[:12]
    return os.path.join(repo_root(), "_runs", "locks",
                        os.path.splitext(os.path.basename(ap))[0] + "." + key + ".lock")

def read_lock(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def stale(p, d):
    age_min = (time.time() - d.get("heartbeat", d.get("acquired", 0))) / 60.0
    return age_min > d.get("ttl", 30)

def cmd_acquire(a):
    p = lock_path(a.target)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    d = read_lock(p)
    if d and d.get("holder") != a.holder and not stale(p, d):
        print(f"LOCKED by {d.get('holder')} (task={d.get('task')}) since {time.strftime('%H:%M:%S', time.localtime(d.get('acquired',0)))} —— 排队/STANDBY，禁止强写")
        sys.exit(1)
    if d and stale(p, d) and d.get("holder") != a.holder:
        for i in range(1, 100):
            sp = f"{p}.stale-{i}"
            if not os.path.exists(sp):
                os.rename(p, sp); break
        print(f"旧锁已过期，抢占并留痕 {sp}")
    now = time.time()
    data = {"holder": a.holder, "task": a.task or "", "acquired": now, "heartbeat": now, "ttl": a.ttl}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"ACQUIRED {os.path.abspath(a.target)} holder={a.holder} ttl={a.ttl}min")

def cmd_release(a):
    p = lock_path(a.target)
    d = read_lock(p)
    if not d:
        print("无锁可解"); return
    if d.get("holder") != a.holder:
        print(f"拒绝：锁属 {d.get('holder')}，非本人（{a.holder}）"); sys.exit(1)
    os.remove(p)
    print(f"RELEASED {os.path.abspath(a.target)}")

def cmd_check(a):
    p = lock_path(a.target)
    d = read_lock(p)
    if not d:
        print("FREE"); return
    state = "STALE(可抢占)" if stale(p, d) else "LOCKED"
    print(f"{state} holder={d.get('holder')} task={d.get('task')} heartbeat={time.strftime('%m-%d %H:%M:%S', time.localtime(d.get('heartbeat',0)))}")

def cmd_list(_):
    ld = os.path.join(repo_root(), "_runs", "locks")
    if not os.path.isdir(ld):
        print("(无锁目录)"); return
    for fn in sorted(os.listdir(ld)):
        if not fn.endswith(".lock"):
            continue
        d = read_lock(os.path.join(ld, fn)) or {}
        state = "STALE" if stale(fn, d) else "LOCKED"
        print(f"{state:5} {fn:44} holder={d.get('holder')} task={d.get('task')}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="advisory 文件锁")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("acquire", "release", "check"):
        s = sub.add_parser(name); s.add_argument("target")
        if name != "check": s.add_argument("--holder", required=True)
        if name == "acquire":
            s.add_argument("--task", default=""); s.add_argument("--ttl", type=int, default=30)
    s = sub.add_parser("list")
    a = ap.parse_args()
    {"acquire": cmd_acquire, "release": cmd_release, "check": cmd_check, "list": cmd_list}[a.cmd](a)
