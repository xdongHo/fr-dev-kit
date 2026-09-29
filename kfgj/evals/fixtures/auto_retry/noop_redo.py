# -*- coding: utf-8 -*-
"""W915(A8_eval) auto-retry 失败路径夹具: 故意"修复但不修复"的 redo 命令。

E-W915-AUTORETRY-NOFIX 用它验证 --auto-retry 1 的失败半程:
redo 正常执行(退出码 0、输出被回显)但 G06 依旧 FAIL → 复检仍 FAIL → 转待裁决。
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

print("w915-noop-redo: 已执行但故意不补 KB_INDEX 头(测 auto-retry 失败路径)")
sys.exit(0)
