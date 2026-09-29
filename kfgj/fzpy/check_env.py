#!/usr/bin/env python3
"""FR Headless 开发环境检测脚本（开源版：适配任意用户环境）

环境解析优先级（与 kfgj/init_user_env.py、fzpy/userdir.py 一致）：
  ~/.fr_dev_kit/fr_env.toml > 环境变量(FR_HOME/JDK_HOME/JAVA_HOME) > 常见安装位置扫描
未初始化用户目录时提示先跑: python kfgj/init_user_env.py
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

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import userdir

# ── 颜色输出 ──────────────────────────────────────────────
GREEN, RED, YELLOW, CYAN, RESET, BOLD = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[0m", "\033[1m"

ok_count = warn_count = fail_count = 0


def ok(msg):
    global ok_count
    ok_count += 1
    print(f"  {GREEN}✓{RESET} {msg}")


def warn(msg):
    global warn_count
    warn_count += 1
    print(f"  {YELLOW}⚠{RESET} {msg}")


def fail(msg):
    global fail_count
    fail_count += 1
    print(f"  {RED}✗{RESET} {msg}")


def check_section(title):
    print(f"\n{CYAN}{BOLD}{title}{RESET}")


# ═══════════════════════════════════════════════════════════
check_section("0. 用户私有环境（~/.fr_dev_kit）")
# ═══════════════════════════════════════════════════════════

if userdir.USER_DIR.is_dir():
    ok(f"{userdir.USER_DIR} 已初始化")
else:
    fail("用户目录未初始化 → 先跑: python kfgj/init_user_env.py")
if userdir.EMBEDDING_TOML.is_file() or userdir.EMBEDDING_TOML_LEGACY.is_file():
    ok("Embedding key 个人档存在（向量检索可用）")
else:
    warn("无 Embedding key（关键词检索可用；配 key 见 jcxt/js/首次配置指南.md）")

# ═══════════════════════════════════════════════════════════
check_section("1. Python 环境")
# ═══════════════════════════════════════════════════════════

ver = sys.version_info
if ver >= (3, 11):
    ok(f"Python {ver.major}.{ver.minor}.{ver.micro}")
else:
    warn(f"Python {ver.major}.{ver.minor}.{ver.micro}（建议 >= 3.11：检索工具用 tomllib）")

try:
    import xml.etree.ElementTree  # noqa: F401
    ok("xml.etree.ElementTree 可用")
except ImportError:
    fail("xml.etree.ElementTree 不可用")

# ═══════════════════════════════════════════════════════════
check_section("2. JDK 8 (javac)")
# ═══════════════════════════════════════════════════════════

jdk_home = userdir.resolve_jdk_home()
javac = None
if jdk_home:
    javac = str(jdk_home / "bin" / "javac.exe")
    try:
        r = subprocess.run([javac, "-version"], capture_output=True, text=True, timeout=10)
        ok(f"javac 可用 → {(r.stderr or r.stdout).strip()}（{jdk_home}）")
    except Exception as e:
        warn(f"javac 探测异常: {e}")
else:
    try:
        r = subprocess.run(["javac", "-version"], capture_output=True, text=True, timeout=10)
        javac = "javac"
        ok(f"javac 在 PATH → {(r.stderr or r.stdout).strip()}")
    except Exception:
        warn("javac 未找到（仅重建 fr-agent jar 时需要；成品 jar 已随包附带，可跳过）")

# ═══════════════════════════════════════════════════════════
check_section("3. FR 设计器安装（FR_HOME）")
# ═══════════════════════════════════════════════════════════

fr_home = userdir.resolve_fr_home()
lib_dir = None
if fr_home:
    ok(f"FR 安装根: {fr_home}（fr_env.toml / FR_HOME / 扫描）")
    lib_dir = fr_home / "webapps" / "webroot" / "WEB-INF" / "lib"
    if lib_dir.is_dir():
        ok(f"WEB-INF/lib/ 有 {len(list(lib_dir.glob('*.jar')))} 个 jar（编译 classpath 来源）")
    else:
        warn("WEB-INF/lib/ 不存在（检查安装完整性）")
    plugins = fr_home / "plugins"
    if plugins.is_dir():
        ok(f"plugins/ 有 {len([d for d in plugins.iterdir() if d.is_dir()])} 个插件")
else:
    warn("未检测到 FR 安装（在线验证/渲染需要；离线生成模板可不装）")
    warn("装了但没扫到 → 编辑 ~/.fr_dev_kit/fr_env.toml 的 fr_home 后重跑")

# ═══════════════════════════════════════════════════════════
check_section("4. FR Java API 编译验证")
# ═══════════════════════════════════════════════════════════

if lib_dir and lib_dir.is_dir() and javac:
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as td:
        test_file = Path(td) / "TestCompile.java"
        test_file.write_text(
            "import com.fr.main.impl.WorkBook;\n"
            "import com.fr.report.worksheet.WorkSheet;\n"
            "public class TestCompile { public static void main(String[] a) {\n"
            "  WorkBook wb = new WorkBook(); WorkSheet ws = new WorkSheet();\n"
            "  wb.addReport(\"test\", ws); System.out.println(\"Compile OK\"); } }\n",
            encoding="utf-8")
        cp = ";".join(str(f) for f in lib_dir.glob("*.jar"))
        try:
            r = subprocess.run([javac, "-cp", cp, str(test_file), "-d", td],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                ok("Java API 编译验证通过 → WorkBook / WorkSheet 类可用")
            else:
                warn(f"编译失败: {r.stderr[:200]}")
        except Exception as e:
            warn(f"编译验证异常: {e}")
else:
    warn("跳过编译验证（需 FR 安装 + JDK8）")

# ═══════════════════════════════════════════════════════════
check_section("5. 原开发者私有布局（可选，仅参考）")
# ═══════════════════════════════════════════════════════════

for p, label in ((Path("C:/frjars"), "C:/frjars（扁平 jar 仓）"),
                 (Path("C:/fr_boot_ws"), "C:/fr_boot_ws（工作目录）"),
                 (Path("D:/design-persist-10.0/design"), "D:/design-persist-10.0（设计器反编译源码）")):
    if p.exists():
        ok(f"{label} 存在")
    else:
        print(f"  {YELLOW}·{RESET} {label} 不存在（原开发者机器布局，开源版不要求）")

# ═══════════════════════════════════════════════════════════
print(f"\n{BOLD}" + "=" * 50)
print(f"检测结果: {GREEN}{ok_count} OK{RESET}  {YELLOW}{warn_count} WARN{RESET}  {RED}{fail_count} FAIL{RESET}")
print("=" * 50 + f"{RESET}\n")

if fail_count == 0:
    print(f"{GREEN}✓ 环境就绪（WARN 项均为可选能力，按需补齐）！{RESET}")
else:
    print(f"{RED}✗ 有 {fail_count} 项缺失，请按上方提示修复。{RESET}")
