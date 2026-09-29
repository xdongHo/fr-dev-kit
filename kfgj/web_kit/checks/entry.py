# -*- coding: utf-8 -*-
"""
checks/entry.py — 入口层体检：最终 URL、HTTP 状态、登录态、加载耗时。

依赖 probe.py 附加的 ctx.entry = {
    "status": int|None, "final_url": str, "elapsed_ms": int,
    "url_format": str, "login_kicked": bool, "note": 可选str}
若缺失（未采集）则输出 info 提示，不阻塞其他检查。
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji/符号不再 UnicodeEncodeError) ---
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


def run(ctx):
    findings = []
    info = getattr(ctx, "entry", None)

    if not info:
        findings.append({
            "check": "entry.response",
            "level": "info",
            "message": "入口响应未采集（ctx.entry 缺失，probe 未正常导航？）",
            "evidence": "url=%s" % (ctx.url or "")[:280],
        })
        return findings

    # 1. 最终 URL（info，作为其他证据的锚点）
    findings.append({
        "check": "entry.final_url",
        "level": "info",
        "message": "最终 URL: %s" % info.get("final_url", ""),
        "evidence": "url_format=%s status=%s" % (info.get("url_format"), info.get("status")),
    })

    # 2. HTTP 状态
    status = info.get("status")
    if status is None:
        findings.append({
            "check": "entry.status",
            "level": "warn",
            "message": "未获取到 HTTP 状态（导航异常或超时）",
            "evidence": str(info.get("note") or "")[:300],
        })
    elif int(status) >= 400:
        findings.append({
            "check": "entry.status",
            "level": "error",
            "message": "HTTP %s：页面入口失败" % status,
            "evidence": "final_url=%s" % (info.get("final_url") or "")[:280],
        })

    # 3. 被踢到登录页
    if info.get("login_kicked"):
        findings.append({
            "check": "entry.login",
            "level": "error",
            "message": "被踢到登录页（会话失效或登录失败）",
            "evidence": "final_url=%s" % (info.get("final_url") or "")[:280],
            "hint": "去掉 --skip-login 重跑，或检查账号/密码与服务器状态",
        })

    # 4. 加载耗时（>10s warn）
    elapsed_ms = info.get("elapsed_ms") or 0
    if elapsed_ms > 10000:
        findings.append({
            "check": "entry.elapsed",
            "level": "warn",
            "message": "整体加载耗时 %.1fs（>10s 阈值）" % (elapsed_ms / 1000.0),
            "evidence": "elapsed_ms=%s url_format=%s" % (elapsed_ms, info.get("url_format")),
            "hint": "大模板/慢 SQL/服务器负载均可能，结合数据集排查",
        })

    return findings
