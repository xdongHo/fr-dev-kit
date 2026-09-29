# -*- coding: utf-8 -*-
"""知识回归检查: 指定文档必须包含全部给定关键词。

用法: python evals/helpers/kb_doc_check.py <doc_path> <关键词1> <关键词2> ...
退出码: 0=全部命中  1=有缺失  2=文档读取异常
P0-1 主线补位(2026-09-14): 把"错误案例知识仍在库、结论未被误删"变成可回归断言。
"""
import io
import sys


def main():
    if len(sys.argv) < 3:
        print("usage: kb_doc_check.py <doc_path> <kw1> [kw2 ...]")
        return 2
    path, kws = sys.argv[1], sys.argv[2:]
    try:
        text = io.open(path, "r", encoding="utf-8", errors="replace").read()
    except OSError as e:
        print("doc 读取失败: %r" % e)
        return 2
    missing = [k for k in kws if k not in text]
    rc = 1 if missing else 0
    if missing:
        print("missing keywords: %s" % " | ".join(missing))
    else:
        print("OK %s 含全部 %d 个关键词" % (path, len(kws)))
    # BG-EV-08: errors=replace 会把编码损坏(如文档被转存为 GBK)静默吞成 U+FFFD,
    # 表现为"关键词缺失"却看不出真因; 追加告警帮助调用方区分, 退出码不变。
    n_bad = text.count("\ufffd")
    if n_bad:
        print("警告: 文档含 %d 个替换符，疑似编码损坏" % n_bad)
    return rc


if __name__ == "__main__":
    sys.exit(main())
