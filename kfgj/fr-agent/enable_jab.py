#!/usr/bin/env python
"""启用 Java Access Bridge for FR Designer — 启用后 pywinauto 可访问所有 Swing 内部组件"""
import os, sys, shutil
from pathlib import Path

FR_HOME = Path(r"C:\Program Files\FineReport_10.0")
ACC_PROPS = FR_HOME / "jre" / "lib" / "accessibility.properties"

def check():
    print("JAB status:")
    if ACC_PROPS.exists():
        content = ACC_PROPS.read_text(encoding="utf-8", errors="ignore")
        enabled = "assistive_technologies=com.sun.java.accessibility.AccessBridge" in content
        commented = content.strip().startswith("#assistive_technologies")
        print(f"  File: {ACC_PROPS}")
        print(f"  {'DISABLED (commented)' if commented and not enabled else 'ENABLED' if enabled else 'NOT CONFIGURED'}")
        return not commented and enabled
    return False

def enable():
    if check(): print("Already enabled"); return
    backup = ACC_PROPS.with_suffix(".properties.bak")
    if not backup.exists(): shutil.copy2(ACC_PROPS, backup)
    content = ACC_PROPS.read_text(encoding="utf-8", errors="ignore")
    new_c = content.replace("#assistive_technologies=com.sun.java.accessibility.AccessBridge",
                              "assistive_technologies=com.sun.java.accessibility.AccessBridge")
    ACC_PROPS.write_text(new_c, encoding="utf-8")
    print("ENABLED. Restart FR Designer required.")

if __name__ == "__main__":
    check()
    if "--enable" in sys.argv: enable()
    elif "--disable" in sys.argv:
        c = ACC_PROPS.read_text(encoding="utf-8", errors="ignore")
        ACC_PROPS.write_text(c.replace("assistive_technologies=", "#assistive_technologies="), encoding="utf-8")
        print("DISABLED")
