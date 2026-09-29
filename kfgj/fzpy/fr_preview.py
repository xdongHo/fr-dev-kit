"""
FR 报表预览工具 — 轻量级 API 登录 + 报表数据获取（不开浏览器）。

用法:
  python fr_preview.py login                      # 登录获取 token
  python fr_preview.py panel <cpt_path>           # 离线解析参数面板布局（最轻量）
  python fr_preview.py report <viewlet>           # 在线获取报表 HTML（需先 login）
  python fr_preview.py coords <viewlet>           # 获取渲染后控件坐标（API 方式）

环境变量:
  FR_HOST      默认 http://localhost:8075
  FR_USER      默认 admin
  FR_PASSWORD  默认 admin
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
import sys, os, re, json, urllib.request, urllib.parse, http.cookiejar

# ═══════════════════════════════════════════
# Config
# ═══════════════════════════════════════════
FR_HOST = os.environ.get("FR_HOST", "http://localhost:8075")
FR_USER = os.environ.get("FR_USER", "admin")
FR_PWD  = os.environ.get("FR_PASSWORD", "admin")

# 布局常量（与 widen_all.py 一致）
MARGIN = 12
CTRL_H = 26
CTRL_W = 180
ROW_H_GAP = 8


# ═══════════════════════════════════════════
# 1. 登录（API 方式，不开浏览器）
# ═══════════════════════════════════════════

_login_state = {"token": None, "cookies": None, "opener": None}

def login():
    """通过 cross/domain API 登录，返回 (token, cookiejar)。"""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    url = "%s/webroot/decision/login/cross/domain?%s" % (
        FR_HOST,
        urllib.parse.urlencode({
            "fine_username": FR_USER,
            "fine_password": FR_PWD,
            "validity": -1,
            "callback": "cb"
        })
    )
    resp = opener.open(url, timeout=10)
    raw = resp.read().decode("utf-8")

    m = re.search(r'"accessToken"\s*:\s*"([^"]+)"', raw)
    if not m:
        raise RuntimeError("登录失败: %s" % raw[:200])

    token = m.group(1)
    _login_state["token"] = token
    _login_state["cookies"] = cj
    _login_state["opener"] = opener
    return token


def get_token():
    """获取当前 token，如果未登录则自动登录。"""
    if _login_state["token"]:
        return _login_state["token"]
    return login()


def fetch_report_html(viewlet, op="write"):
    """带 token 获取报表页面 HTML（轻量级，不开浏览器）。"""
    token = get_token()
    opener = _login_state["opener"]
    url = "%s/webroot/decision/view/report?%s" % (
        FR_HOST,
        urllib.parse.urlencode({
            "viewlet": viewlet,
            "op": op,
            "fine_auth_token": token
        })
    )
    resp = opener.open(url, timeout=15)
    return resp.read().decode("utf-8")


# ═══════════════════════════════════════════
# 2. 离线参数面板布局分析（零网络开销）
# ═══════════════════════════════════════════

def analyze_panel(cpt_path):
    """直接解析 CPT XML 中的参数面板坐标，检测布局问题。不需要网络。"""
    xml = open(cpt_path, encoding="utf-8").read()

    # 面板尺寸
    dm = re.search(r'<DesignAttr width="(\d+)" height="(\d+)"/>', xml)
    panel_w = int(dm.group(1)) if dm else 0
    panel_h = int(dm.group(2)) if dm else 0

    # 提取参数面板
    pm = re.search(r'(<ParameterUI.*?</ParameterUI>)', xml, re.S)
    if not pm:
        print("⚠️  无 ParameterUI")
        return
    pui = pm.group(0)

    # 提取所有控件的 BoundsAttr + WidgetName
    # 格式: <Widget ...BoundsWidget><InnerWidget ...><WidgetName name="X"/>...</InnerWidget><BoundsAttr x y w h/>
    widget_re = re.compile(
        r'<Widget class="[^"]*\x24BoundsWidget">'
        r'.*?<InnerWidget class="([^"]+)">.*?'
        r'<WidgetName name="([^"]+)"/>.*?'
        r'<BoundsAttr x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)"/>',
        re.S
    )

    items = []
    for m in widget_re.finditer(pui):
        cls = m.group(1).split(".")[-1]
        name = m.group(2)
        x, y, w, h = int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6))
        items.append({
            "cls": cls, "name": name,
            "x": x, "y": y, "w": w, "h": h,
            "right": x + w, "bottom": y + h
        })

    items.sort(key=lambda i: (i["y"], i["x"]))

    print("═" * 60)
    print("  参数面板布局分析: %s" % os.path.basename(cpt_path))
    print("═" * 60)
    print("  面板尺寸: %dx%d" % (panel_w, panel_h))
    print("  控件数量: %d" % len(items))
    print()

    # 按行分组
    rows = {}
    for item in items:
        rows.setdefault(item["y"], []).append(item)

    issues = 0
    for y in sorted(rows.keys()):
        row_items = sorted(rows[y], key=lambda i: i["x"])
        print("  ── 行 y=%d (%d 个控件) ──" % (y, len(row_items)))
        for item in row_items:
            marker = ""
            if item["right"] > panel_w:
                marker = " ❌ 溢出!"
                issues += 1
            print("    %-22s %-20s [%4d-%4d]%s" % (
                item["cls"], item["name"], item["x"], item["right"], marker))

        # 检查同行重叠
        for i in range(len(row_items) - 1):
            a, b = row_items[i], row_items[i + 1]
            if a["right"] > b["x"]:
                print("    ❌ 重叠: %s(right=%d) > %s(x=%d)" % (a["name"], a["right"], b["name"], b["x"]))
                issues += 1

    # 溢出检查
    print()
    all_max_right = max(i["right"] for i in items) if items else 0
    all_max_bottom = max(i["bottom"] for i in items) if items else 0
    print("  内容范围: right=%d bottom=%d" % (all_max_right, all_max_bottom))
    if all_max_right > panel_w:
        print("  ❌ 右侧溢出: %d > %d (超出 %dpx)" % (all_max_right, panel_w, all_max_right - panel_w))
        issues += 1
    else:
        print("  ✅ 右侧无溢出")
    if all_max_bottom > panel_h:
        print("  ❌ 底部溢出: %d > %d (超出 %dpx)" % (all_max_bottom, panel_h, all_max_bottom - panel_h))
        issues += 1
    else:
        print("  ✅ 底部无溢出")

    # 按钮行检查
    btn_items = [i for i in items if "Button" in i["cls"] or "Submit" in i["cls"]]
    if btn_items:
        print()
        btn_y_vals = set(i["y"] for i in btn_items)
        if len(btn_y_vals) == 1:
            print("  ✅ 按钮全部在同一行 (y=%d)" % list(btn_y_vals)[0])
        else:
            print("  ⚠️  按钮分布在多行: %s" % str(sorted(btn_y_vals)))

    print()
    if issues == 0:
        print("  ✅ 布局检查通过，无问题")
    else:
        print("  ❌ 发现 %d 个问题" % issues)
    print("═" * 60)
    return issues


# ═══════════════════════════════════════════
# 3. 在线报表 HTML 获取（轻量级）
# ═══════════════════════════════════════════

def report_html(viewlet, op="write", save=None):
    """获取报表页面 HTML。"""
    html = fetch_report_html(viewlet, op)
    print("报表 HTML: %d chars" % len(html))
    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write(html)
        print("已保存到: %s" % save)
    else:
        # 只打印关键信息
        title_m = re.search(r'<title>([^<]*)</title>', html)
        print("标题: %s" % (title_m.group(1) if title_m else "?"))
        # 检查是否有错误
        if "404" in html[:500] or "找不到" in html[:500]:
            print("❌ 报表未找到")
        elif "login" in html[:500].lower():
            print("⚠️  被重定向到登录页")
        else:
            print("✅ 页面加载正常")
    return html


# ═══════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "login":
        token = login()
        print("✅ 登录成功")
        print("Token: %s...%s (%d chars)" % (token[:20], token[-10:], len(token)))

    elif cmd == "panel":
        if len(sys.argv) < 3:
            print("用法: python fr_preview.py panel <cpt_path>")
            return
        analyze_panel(sys.argv[2])

    elif cmd == "report":
        if len(sys.argv) < 3:
            print("用法: python fr_preview.py report <viewlet> [op]")
            return
        viewlet = sys.argv[2]
        op = sys.argv[3] if len(sys.argv) > 3 else "write"
        save = sys.argv[4] if len(sys.argv) > 4 else None
        report_html(viewlet, op, save)

    else:
        print("未知命令: %s" % cmd)
        print(__doc__)


if __name__ == "__main__":
    main()
