# -*- coding: utf-8 -*-
"""E-W915-FRCHK-4LESION 助手: fr_check L1 前置闸四病灶矩阵回归（W915 泳道 A8_eval）。

对 evals/fixtures/fr_check/ 下四类病灶夹具逐个跑 fr_check, 断言每件:
  rc=1 且输出命中对应病灶关键词——
  0 字节空文件 / 裸&断裂实体(病灶行) / 二进制非文本 / GBK 编码
4/4 检出 → rc 0, 任一脱靶 → rc 1。
用法: python evals/fixtures/w915/frchk_lesion_matrix.py
"""
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

LESIONS = [
    ("zero_byte.cpt", "0 字节"),
    ("bare_amp.cpt", "病灶行"),
    ("binary.cpt", "非文本"),
    ("gbk_legacy.cpt", "GBK 编码"),
]


def decode(raw):
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def main():
    ok = 0
    for name, kw in LESIONS:
        p = subprocess.run([sys.executable, "kfgj/fzpy/fr_check.py",
                            "evals/fixtures/fr_check/" + name],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = decode(p.stdout or b"")
        hit = (p.returncode == 1) and (kw in out)
        print("  %s %-15s rc=%s 关键词%r %s"
              % ("OK  " if hit else "BAD ", name, p.returncode, kw,
                 "命中" if hit else "脱靶"))
        ok += hit
    if ok == len(LESIONS):
        print("[PASS] 四病灶检出 4/4 (0字节/裸&/二进制/GBK 全部 rc=1 且关键词命中)")
        return 0
    print("[FAIL] 四病灶检出 %d/4" % ok)
    return 1


if __name__ == "__main__":
    sys.exit(main())
