# -*- coding: utf-8 -*-
"""E-W915-DESC13-QC4 助手: desc13 emit 产物的 QC 四查要素断言（W915 泳道 A8_eval）。

对 desc13.py emit 落盘的 <outdir>/2.md 断言四查要素在文档级可见:
  ①事件三要素  ②SQL 全文零截断  ③壳层穷举断言  ④字数声明
兼容 L0 常规档与密度档两种文案变体（正则交替分支）。
用法: python evals/fixtures/w915/desc13_qc4_check.py <emit_outdir>
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

CHECKS = [
    ("①事件三要素", r"事件[=×]\s*控件名×事件名×JS 全文三要素|事件×\d+三要素✓|事件 \d+ 个三要素"),
    ("②SQL全文零截断", r"SQL 全文逐字不截|SQL×\d+全文零截断✓|（SQL 全文零截断）✓"),
    ("③壳层穷举断言", r"壳层载体逐项|壳层\d+族断言✓|壳层断言 \d+ 族"),
    ("④字数声明", r"字数 Word 式 ≤3000|字数见 §0|\[密度档L\d+声明✓\]"),
]


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else ""
    path = os.path.join(outdir, "2.md")
    if not os.path.isfile(path):
        print("[FAIL] emit 产物不存在: %s" % path)
        return 1
    text = io.open(path, encoding="utf-8").read()
    misses = []
    for name, pat in CHECKS:
        if re.search(pat, text):
            print("  OK  %s 命中 /%s/" % (name, pat[:36]))
        else:
            misses.append(name)
            print("  MISS %s 未命中 /%s/" % (name, pat[:36]))
    if misses:
        print("[FAIL] 四查要素缺: %s" % ", ".join(misses))
        return 1
    print("[PASS] 四查: 2.md 四查要素齐(①事件三要素 ②SQL全文 ③壳层穷举 ④字数)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
