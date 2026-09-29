#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_cp.py — 按本机 FR 安装重新生成 cp.txt（fr-agent 编译 classpath）

cp.txt 随包附带的是默认安装路径（C:\\Program Files\\FineReport_10.0）下的 jar 清单；
你的 FR 装在别处时跑一次本脚本即可：

    python kfgj/fr-agent/gen_cp.py            # 从 fr_env.toml / FR_HOME / 扫描定位
    python kfgj/fr-agent/gen_cp.py D:\\FineReport_10.0

定位优先级与 fzpy/userdir.py 一致（~/.fr_dev_kit/fr_env.toml > 环境变量 > 常见位置）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fzpy"))
import userdir


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    fr = Path(sys.argv[1]) if len(sys.argv) > 1 else userdir.resolve_fr_home()
    if not fr:
        print("未检测到 FR 安装。装好后重跑，或显式传路径：python gen_cp.py <FR_HOME>")
        sys.exit(1)
    lib = fr / "webapps" / "webroot" / "WEB-INF" / "lib"
    jars = sorted(lib.glob("*.jar"))
    if not jars:
        print(f"{lib} 下没有 jar，请确认这是 FR10 安装根目录")
        sys.exit(1)
    out = Path(__file__).resolve().parent / "cp.txt"
    out.write_text(";".join(str(j) for j in jars) + "\n", encoding="utf-8", newline="")
    print(f"✅ 已生成 {out}（{len(jars)} 个 jar，FR={fr}）")


if __name__ == "__main__":
    main()
