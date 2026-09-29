#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原实现完整保留在同目录 query_kb_origin.py(未改一字)。

无感保障(为什么它不会影响 agent 会话):
  1. CLI/参数/输出/退出码与原版一致: 经 exec(compile(原文件源码, 原文件路径)) 以
     __main__ 运行, argv[0] 不变(argparse 用法串/usage 完全一致),
     stdout 用 Tee 直写同一 fd(不经管道, 无编码/缓冲变化)。
  2. 审计写入全程 try/except 静默: 日志盘满/路径失效/平台目录被移动时
     行为退化为原版直通(审计缺失但不报错)。
     导入失败则静默无审计, 绝不影响宿主工具。
  4. SystemExit 原样 re-raise, 退出码不变; 非常规异常记录后原样上抛
     (traceback 帧指向 query_kb_origin.py, 源码行号真实可查)。
"""
import re
import sys
import time
from pathlib import Path

ORIGIN = Path(__file__).resolve().parent / "query_kb_origin.py"
PARSER = "engkb"            # vector | engkb (安装时注入)
AUDIT_LOG = Path(__file__).resolve().parents[1] / "kb_platform" / "audit" / "events.jsonl"   # 本仓(2026-09-04 由 v2.1 字面路径改为动态推导)

try:  # 复用平台审计核心(含哈希链); 平台目录被移走则退化为无审计
    sys.path.insert(0, str(AUDIT_LOG.parent.parent / "proxy"))
    from audit_log import log_event as _log_event
except Exception:
    _log_event = None


# ---------------------------------------------------------------- stdout Tee
class _Tee:
    """包装 sys.stdout: 字节原样透写给真实 stdout, 同时留一份供命中解析。

    刻意用普通类而非 io.TextIOBase 子类, 避免 encoding 等 property 遮蔽;
    未显式定义的属性一律 __getattr__ 透传(reconfigure/fileno/isatty/...)。
    """
    def __init__(self, orig):
        self._orig = orig
        self.chunks = []

    def write(self, s):
        try:
            self.chunks.append(s)
        except Exception:
            pass
        return self._orig.write(s)

    def writelines(self, seq):
        for s in seq:
            self.write(s)

    def flush(self):
        return self._orig.flush()

    def __getattr__(self, name):
        return getattr(self._orig, name)


# ---------------------------------------------------------------- 命中解析
def _parse_vector(out_text, argv):
    """解析 jcxt/js/query_kb.py 输出: 命中行 ` N. [分数] 路径  >  章节`。"""
    hits, mode, zero = [], None, False
    for line in out_text.splitlines():
        m = re.match(r"\s*\d+\.\s+\[[^\]]*\]\s+(.+?)\s{2,}>\s+(.+)$", line)
        if m:
            p = m.group(1).strip()
            if p not in hits:
                hits.append(p)
            continue
        m = re.match(r"^模式:\s*(\w+)", line.strip())
        if m:
            mode = m.group(1)
        if "命中 0" in line:
            zero = True
    return {"hits": hits, "mode": mode, "zero_result": zero and not hits,
            "query": argv[0] if argv else ""}


def _parse_engkb(out_text, argv):
    """解析 ckzl/zsk/gczsk/query_kb.py 输出: 收集 [P-xxxx]/[E-xx] 编号 + 子命令。"""
    hits = []
    for m in re.finditer(r"\[([A-Z]{1,2}-\d+)\]", out_text):
        pno = m.group(1)
        if pno not in hits:
            hits.append(pno)
    sub = argv[0] if argv else ""
    return {"hits": hits, "mode": sub, "zero_result": ("未找到" in out_text) and not hits,
            "query": (argv[1] if len(argv) > 1 else sub)}


_PARSERS = {"vector": _parse_vector, "engkb": _parse_engkb}


def _finish(tee, start_ms, code, argv):
    try:
        if not _log_event:
            return
        out_text = "".join(tee.chunks)
        info = _PARSERS[PARSER](out_text, list(argv))
        _log_event("query",
                   tool="vector_kb" if PARSER == "vector" else "eng_kb",
                   argv=[str(a)[:500] for a in argv],
                   query=str(info.get("query", ""))[:500],
                   mode=info.get("mode"),
                   hits=info["hits"], hit_count=len(info["hits"]),
                   zero_result=bool(info.get("zero_result")),
                   duration_ms=int(time.perf_counter() * 1000 - start_ms),
                   exit_code=code, ok=code == 0,
                   cwd=str(Path.cwd()))
    except Exception:
        pass  # 无感铁律: 审计失败静默


def _run_origin():
    """以 __main__ 执行原实现。

    exec(compile(源码, 原文件绝对路径)) 而非 runpy: traceback 帧直接指向
    query_kb_origin.py 且源码行真实可读; __file__ 取原文件绝对路径,
    原实现里所有 Path(__file__).parent 推导(库/配置定位)结果不变。
    """
    src = ORIGIN.read_text(encoding="utf-8-sig")  # -sig: 兼容带 BOM 的原文件
    code = compile(src, str(ORIGIN), "exec")
    g = {"__name__": "__main__", "__file__": str(ORIGIN),
         "__builtins__": __builtins__, "__doc__": None, "__package__": None}
    exec(code, g)


def main():
    start_ms = time.perf_counter() * 1000
    argv = sys.argv[1:]
    tee = _Tee(sys.stdout)
    sys.stdout = tee
    code = 0
    try:
        _run_origin()
    except SystemExit as e:
        code = 0 if e.code is None else (e.code if isinstance(e.code, int) else 1)
        _finish(tee, start_ms, code, argv)
        raise
    except BaseException:
        _finish(tee, start_ms, 1, argv)
        raise
    _finish(tee, start_ms, 0, argv)


if __name__ == "__main__":
    main()
