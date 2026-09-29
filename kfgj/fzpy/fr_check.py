"""
FR 报表全局错误检测工具 — 三层检测（离线→在线→浏览器）。

用法:
  python fr_check.py <cpt_path>             # 默认：离线XML检查
  python fr_check.py <cpt_path> --online     # 离线 + 在线HTTP检查（需FR服务器运行）
  python fr_check.py <cpt_path> --browser   # 离线 + 浏览器全局扫描（需浏览器+FR服务器）

分层设计:
  Layer 1: 离线 XML 结构检查（零网络，<1秒）
    - XML 合法性  - 无 $$ 双美元符  - WidgetName 唯一性
    - ParameterUI/TableDataMap 配对  - 结构完整性
  Layer 2: 在线 HTTP 检查（轻量 HTTP，<3秒，需FR服务器）
    - HTTP 状态码  - 页面HTML中错误文本扫描
    - 404/500/报表未找到  - 登录态有效性
  Layer 3: 浏览器全局扫描（开浏览器，需FR服务器，>10秒）
    - FR.Logger.error 调用  - FR.Events 失败事件
    - FR.ErrorMarkWidget 实例  - JS console 错误
    - 参数面板渲染验证  - 数据是否正常加载

退出码: 0=无错误 1=有错误 2=有警告
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

# v2: 本机路径优先读 kfgj/env.md（知识库治理/知识管理规范-维护流程.md §0.15），环境变量次之，硬编码仅作最后回落。
def _load_local_env_paths():
    """从仓库根 kfgj/env.md 提取 reportlets / FR_BIN 绝对路径（不存在则返回 None）。"""
    kit_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(kit_root, "kfgj/env.md")
    result = {}
    try:
        with open(env_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith("-") and ":" in line:
                    body = line.lstrip("- ").strip()
                    key_part, _, val = body.partition(":")
                    key_part = key_part.strip().lower()
                    val = val.strip().strip("`\"'")
                    # 去掉「名称(别名)」的括号说明
                    key_part = key_part.split("(")[0].strip()
                    if not os.path.isabs(val) or not val:
                        continue
                    for probe in ("reportlets", "bin", "web-inf"):
                        if probe in key_part and probe not in result:
                            result[probe] = val
    except OSError:
        pass
    return result

_LOCAL_ENV = _load_local_env_paths()
_ENV_REPORTLETS = _LOCAL_ENV.get("reportlets")
_ENV_FR_BIN = _LOCAL_ENV.get("bin")

FR_HOST = os.environ.get("FR_HOST", "http://localhost:8075")
FR_USER = os.environ.get("FR_USER", "admin")
FR_PWD = os.environ.get("FR_PASSWORD", "admin")
FR_BIN = os.environ.get("FR_BIN") or _ENV_FR_BIN or r"C:\Program Files\FineReport_10.0\bin"
# reportlets 目录：LOCAL_ENV > 环境变量 FR_REPORTLETS > FR_BIN 推导 > 旧硬编码回落
FR_REPORTLETS = (
    os.environ.get("FR_REPORTLETS")
    or _ENV_REPORTLETS
    or (os.path.abspath(os.path.join(FR_BIN, "..", "webapps", "webroot", "WEB-INF", "reportlets"))
        if os.path.isdir(FR_BIN) else None)
    or r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets"
)

errors = 0
warns = 0

def error(msg, layer=""):
    global errors
    errors += 1
    prefix = "  " + layer + " " if layer else "  "
    print(prefix + "❌ " + msg)

def warn(msg, layer=""):
    global warns
    warns += 1
    prefix = "  " + layer + " " if layer else "  "
    print(prefix + "⚠️  " + msg)

def ok(msg, layer=""):
    prefix = "  " + layer + " " if layer else "  "
    print(prefix + "✅ " + msg)


# ════════════════════════════════════
# Layer 1: 离线 XML 结构检查
# ════════════════════════════════════

def check_xml_structure(cpt_path):
    """离线检查 CPT XML 结构完整性。不需要 FR 服务器。
    返回 bool: XML 是否 well-formed。不合法时后续深度检查无意义，调用方应跳过。"""
    print("\n═══ Layer 1: XML 结构检查 ═══")

    if not os.path.isfile(cpt_path):
        error("文件不存在: %s" % cpt_path, "L1")
        return False

    # 1.0 前置闸: 空文件/编码/合法性——病灶文件直接判死，后续检查全是噪音
    if os.path.getsize(cpt_path) == 0:
        error("0 字节空文件（疑似保存中断或仓库残留物），跳过全部后续检查", "L1")
        return False

    import xml.etree.ElementTree as ET
    raw = open(cpt_path, "rb").read()
    try:
        xml = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            xml = raw.decode("gbk")
            warn("文件为 GBK 编码（FR 标准应为 UTF-8，混编码会导致服务器端解析异常）", "L1")
        except UnicodeDecodeError:
            error("非文本内容或未知编码（前 32 字节: %r），跳过全部后续检查" % raw[:32], "L1")
            return False

    fname = os.path.basename(cpt_path)

    # 1.1 XML 合法性（well-formed 前置检查，失败给行列号+病灶行预览）
    try:
        ET.fromstring(xml)
        ok("XML 解析通过", "L1")
    except ET.ParseError as e:
        lineno = getattr(e, "position", (0, 0))[0]
        lines = xml.split("\n")
        bad_line = lines[lineno - 1].strip()[:120] if 0 < lineno <= len(lines) else "<不可定位>"
        error("XML 解析失败（病灶文件）: 第%d行: %s | 病灶行: %s" % (lineno, str(e)[:80], bad_line), "L1")
        error("跳过 Layer 1 其余 %d 项结构检查与后续深度层（对不合法 XML 无意义）" % 9, "L1")
        return False

    # 1.2 关键元素配对
    checks = [
        ("<ParameterUI", "</ParameterUI>", "ParameterUI"),
        ("<TableDataMap", "</TableDataMap>", "TableDataMap"),
        ("<Report class=", "</Report>", "Report"),
        ("<CellElementList>", "</CellElementList>", "CellElementList"),
    ]
    for open_tag, close_tag, name in checks:
        o_count = xml.count(open_tag)
        c_count = xml.count(close_tag) if close_tag else 0
        if o_count == c_count:
            ok("%s: %d 配对正确" % (name, o_count), "L1")
        else:
            error("%s: 打开%d 关闭%d 不匹配" % (name, o_count, c_count), "L1")

    # 1.3 WidgetName 唯一性（白名单: delete 是增删行按钮共用名）
    widget_names = re.findall(r'<WidgetName name="([^"]+)"', xml)
    # 排除设计决策中的有意重复
    ALLOWED_DUPES = {"delete", "append", "add", "remove"}
    from collections import Counter
    name_counts = Counter(widget_names)
    real_dupes = {n: c for n, c in name_counts.items() if c > 1 and n not in ALLOWED_DUPES and "label" not in n.lower()}
    if real_dupes:
        warn("WidgetName 重复: %s" % str(list(real_dupes.keys())), "L1")
    else:
        intentional = {n: c for n, c in name_counts.items() if c > 1 and n in ALLOWED_DUPES}
        if intentional:
            ok("WidgetName 全部唯一（含设计决策重复: %s）" % str(list(intentional.keys())), "L1")
        else:
            ok("WidgetName 全部唯一 (%d个)" % len(widget_names), "L1")

    # 1.4 无 $$ 双美元符
    # ⚠$$$ 豁免(2026-08-20 反向验证): 公式字典显示值 EFormulaDict[CDATA[=$$$]] 是 FR 标准占位符
    #   (显示值=实际值),先剥离 $$$+ 序列再数 $$,否则字典控件全员误报(实测 para_lpvc 中招)
    dd_xml = re.sub(r'\${3,}', '', xml)
    dd_count = len(re.findall(r'\$\$', dd_xml))
    if dd_count > 0:
        error("发现 %d 处 $$ 双美元符（会导致 Widget 渲染报错）" % dd_count, "L1")
    else:
        ok("无 $$ 双美元符", "L1")

    # 1.5 无自闭合关键元素
    for tag in ["TableDataMap", "CellElementList"]:
        if re.search(r'<%s\s*/>' % tag, xml):
            error("<%s> 自闭合会导致运行时空指针" % tag, "L1")

    # 1.6 检查数据集数量
    ds_count = len(re.findall(r'<TableData name="', xml))
    if ds_count == 0:
        error("未找到任何数据集", "L1")
    else:
        ok("数据集: %d 个" % ds_count, "L1")

    # 1.7 检查提交配置
    if '<ReportWriteAttr>' in xml:
        if 'IntelliDMLConfig' in xml:
            ok("提交配置: IntelliDMLConfig 智能提交", "L1")
        elif 'InsertConfig' in xml:
            ok("提交配置: InsertConfig", "L1")
        elif 'DeleteConfig' in xml:
            ok("提交配置: DeleteConfig", "L1")
        else:
            warn("提交配置存在但未识别类型", "L1")
    else:
        warn("未找到提交配置（查看报表不需要）", "L1")

    # 1.8 检查级联参数格式
    cascade_count = len(re.findall(r'\x24\{if\(len\(', xml))
    db_count = len(re.findall(r'<Parameter>\s*<Attributes[^>]*name=', xml))
    ok("级联参数: %d 处 ${if(len(  %d 处级联Parameter" % (cascade_count, db_count), "L1")

    # 1.9 检查 FrozenColumnRow
    if 'FrozenColumnRow' in xml:
        if re.search(r'columnrow="A1"', xml):
            ok("冻结表头: A1", "L1")
        else:
            ok("冻结表头: 已设置", "L1")
    else:
        warn("未冻结表头", "L1")

    # 1.10 检查 __cutpage__
    if '__cutpage__' in xml:
        ok("分页: __cutpage__ 已配置", "L1")
    else:
        warn("未配置 __cutpage__（可选）", "L1")

    return True


# ════════════════════════════════════
# Layer 2: 在线 HTTP 检查
# ════════════════════════════════════

def login_fr():
    """API 登录，返回 (token, opener)。"""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    url = "%s/webroot/decision/login/cross/domain?%s" % (
        FR_HOST,
        urllib.parse.urlencode({"fine_username": FR_USER, "fine_password": FR_PWD, "validity": -1, "callback": "cb"})
    )
    resp = opener.open(url, timeout=10)
    raw = resp.read().decode("utf-8")
    m = re.search(r'"accessToken"\s*:\s*"([^"]+)"', raw)
    if not m:
        raise RuntimeError("登录失败: %s" % raw[:200])
    return m.group(1), opener


def check_http(viewlet, op="write"):
    """在线 HTTP 检查：获取报表页面，扫描错误文本。"""
    print("\n═══ Layer 2: HTTP 在线检查 ═══")

    # 检查 FR 服务器可达性
    try:
        resp = urllib.request.urlopen("%s/webroot/decision/login" % FR_HOST, timeout=5)
        ok("FR 服务器可达 (%s)" % resp.status, "L2")
    except Exception as e:
        error("FR 服务器不可达: %s" % str(e)[:80], "L2")
        return

    # 登录
    try:
        token, opener = login_fr()
        ok("API 登录成功 (%d chars token)" % len(token), "L2")
    except Exception as e:
        error("登录失败: %s" % str(e)[:80], "L2")
        return

    # 获取报表页面
    url = "%s/webroot/decision/view/report?%s" % (
        FR_HOST,
        urllib.parse.urlencode({"viewlet": viewlet, "op": op, "fine_auth_token": token})
    )
    try:
        resp = opener.open(url, timeout=15)
        html = resp.read().decode("utf-8")
    except urllib.request.HTTPError as e:
        error("HTTP %d: 访问报表失败" % e.code, "L2")
        return
    except Exception as e:
        error("网络错误: %s" % str(e)[:80], "L2")
        return

    # 检查错误模式
    error_patterns = {
        "page_404": (r"404\s*(找不到|未找到|NotFound)", "页面 404"),
        "page_500": (r"500\s*(服务器|内部|Internal)", "服务器 500 错误"),
        "redirect_login": (r"login.*redirect|redirect.*login", "被重定向到登录页"),
        "sql_error": (r"SQL\s*(错误|异常|error|exception|Syntax)", "SQL 异常"),
        "dataset_error": (r"(数据集|TableData)\s*(错误|异常|未找到|不存在)", "数据集错误"),
        "class_not_found": (r"ClassNotFoundException|NoClassDefFoundError", "类找不到"),
        "null_pointer": (r"NullPointerException|空指针", "空指针异常"),
        "widget_error": (r"WidgetErrorMarker|控件.*错误", "控件渲染错误"),
        "parse_error": (r"ParseException|解析.*错误|DOMException", "解析异常"),
        "java_exception": (r"java\.\w+\.\w+Exception", "Java 异常"),
        "fr_error": (r"Error:\s*[A-Z]", "FR 运行时错误"),
    }

    found_errors = []
    html_lower = html[:5000].lower()  # 只搜前5000字符

    for key, (pattern, desc) in error_patterns.items():
        if re.search(pattern, html_lower, re.I):
            found_errors.append(desc)

    if found_errors:
        for e in found_errors:
            error("页面包含: %s" % e, "L2")
    else:
        ok("页面 HTML 无已知错误模式 (%d chars)" % len(html), "L2")

    # 标题检查
    title_m = re.search(r'<title>([^<]*)</title>', html)
    if title_m:
        title = title_m.group(1)
        if "error" in title.lower() or "错误" in title:
            warn("页面标题包含错误: %s" % title, "L2")
        else:
            ok("页面标题: %s" % title, "L2")

    # 检查是否重定向
    if "login" in html[:1000].lower() and "redirect" in html[:1000].lower():
        warn("页面被重定向到登录（token 可能过期）", "L2")

    return html


# ════════════════════════════════════
# Layer 3: 浏览器全局扫描（最重，仅必要时用）
# ════════════════════════════════════

def check_browser_signals():
    """返回一段 JS 代码，在浏览器 console 中执行以探测所有错误信号。"""
    return """
// FR 全局错误信号探测（贴在浏览器 console 执行）
(function() {
    var report = {};

    // 1. 全局对象可用性
    report.g = typeof _g === 'function';
    report.FR = typeof FR === 'object';
    report.cp = typeof contentPane === 'object';
    report.sid = typeof sessionID !== 'undefined' ? sessionID : null;

    // 2. FR.Logger.error 是否被调用过
    if (typeof FR !== 'undefined' && FR.Logger) {
        report.logger_error = typeof FR.Logger.error === 'function';
    }

    // 3. 检查 FR.Events 失败事件是否被触发过
    if (typeof FR !== 'undefined' && FR.Events) {
        var failEvents = ['WF', 'AS'];
        report.failEventsActive = failEvents.filter(function(e) { return FR.Events[e]; });
    }

    // 4. 检查页面中的 ErrorMarkWidget 实例
    if (typeof FR !== 'undefined' && FR.ErrorMarkWidget) {
        var emw = document.querySelectorAll('[class*="error-mark"], [class*="errorMark"], [class*="errormark"]');
        report.errorMarkWidgets = emw.length;
    }

    // 4. JS console 错误（通过 window.onerror 捕获）
    report.jsErrors = (window.__fr_js_errors || []).length;
    window.onerror = function(msg) {
        window.__fr_js_errors = window.__fr_js_errors || [];
        window.__fr_js_errors.push(msg);
    };

    // 5. 参数面板渲染检查
    var paramInputs = document.querySelectorAll('input.fr-trigger-texteditor');
    report.paramControls = paramInputs.length;
    var btns = document.querySelectorAll('.fr-btn-up');
    report.buttons = btns.length;

    // 6. 数据表格检查
    var dataRows = document.querySelectorAll('table.fr-table tr, [class*=fr-table] tr');
    report.dataRows = dataRows.length;

    // 7. 页面中的 toast/alert 错误框
    var popups = document.querySelectorAll('.fr-msg-container, .fr-toast, .fr-alert, [class*=popup], [class*=dialog][class*=error]');
    report.popups = popups.length;
    if (popups.length > 0) {
        var popupTexts = [];
        popups.forEach(function(p) { popupTexts.push(p.textContent.trim().substring(0, 100)); });
        report.popupTexts = popupTexts;
    }

    return JSON.stringify(report, null, 2);
})();
"""


# ════════════════════════════════════
# Layer 1.5: 官方文档持续学习规则(2026-08 起,来自 fr_rules_doc / fr_rules_export)
# ════════════════════════════════════

def run_doc_rules(cpt_path, verbose=False):
    """运行官方文档学习沉淀的静态校验规则(两个独立模块,缺失自动跳过)。

    规则模块返回 run_all(cpt_path) -> list[dict],含 level(ERROR/WARN/OK) 与 msg;
    fr_rules_doc 用 name/doc/apply 键,fr_rules_export 用 rule 键,此处兼容两者。
    --no-rules 可整体关闭本层。
    """
    import importlib.util
    base = os.path.dirname(os.path.abspath(__file__))
    mods = []
    for name in ("fr_rules_doc", "fr_rules_export"):
        p = os.path.join(base, name + ".py")
        if os.path.exists(p):
            try:
                spec = importlib.util.spec_from_file_location(name, p)
                m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m)
                mods.append(m)
            except Exception as e:
                warn("规则模块 %s 加载失败: %s" % (name, e), "L1.5")
    if not mods:
        return
    print("\n═══ Layer 1.5: 官方文档规则(%d 个模块, --no-rules 关闭) ═══" % len(mods))
    for m in mods:
        try:
            results = m.run_all(cpt_path)
        except Exception as e:
            warn("规则模块 %s 执行异常: %s" % (m.__name__, e), "L1.5")
            continue
        for r in results:
            if not isinstance(r, dict):
                continue
            level = str(r.get("level", "OK")).upper()
            msg = r.get("msg", "")
            rname = r.get("name") or r.get("rule") or "?"
            doc = r.get("doc", "")
            tag = "%s(%s)" % (rname, doc) if doc else rname
            if level == "ERROR":
                error("[%s] %s" % (tag, msg), "L1.5")
            elif level == "WARN":
                warn("[%s] %s" % (tag, msg), "L1.5")
            elif verbose:
                ok("[%s] %s" % (tag, msg), "L1.5")


# ════════════════════════════════════
# 主入口
# ════════════════════════════════════

def main():
    global errors, warns

    if len(sys.argv) < 2:
        print(__doc__)
        return 0

    cpt_path = sys.argv[1]
    online = "--online" in sys.argv or "--browser" in sys.argv
    browser = "--browser" in sys.argv
    no_rules = "--no-rules" in sys.argv
    verbose = "--verbose" in sys.argv

    # 推导 viewlet 路径（v2: reportlets 根可来自 kfgj/env.md / 环境变量，见文件头 FR_REPORTLETS）
    reportlets_dir = FR_REPORTLETS
    viewlet = None
    try:
        if os.path.abspath(cpt_path).startswith(os.path.abspath(reportlets_dir)):
            viewlet = os.path.relpath(cpt_path, reportlets_dir).replace("\\", "/")
    except:
        pass

    print("═" * 55)
    print("  FR 报表全局错误检测")
    print("  文件: %s" % os.path.basename(cpt_path))
    if viewlet:
        print("  Viewlet: %s" % viewlet)
    print("═" * 55)

    # Layer 1: 离线 XML（well-formed 前置闸：病灶文件直接终判，后续层无意义）
    well_formed = check_xml_structure(cpt_path)
    if not well_formed:
        print("\n═══ 后续层已跳过 ═══")
        print("  ⛔ 文件不合法（空/编码错/XML 病灶），先修复文件本身再复查。")
        print("\n═" * 55)
        print("  ❌ 发现 %d 个错误 + %d 个警告（文件病灶，深度检查未执行）" % (errors, warns))
        print("═" * 55)
        return 1

    # Layer 1.5: 官方文档持续学习规则(静态,可选 --no-rules 关闭)
    if not no_rules:
        run_doc_rules(cpt_path, verbose)

    # Layer 2: 在线 HTTP
    if online and viewlet:
        check_http(viewlet)
    elif online and not viewlet:
        warn("无法推导 viewlet，跳过 HTTP 检查", "L2")

    # Layer 3: 浏览器
    if browser:
        print("\n═══ Layer 3: 浏览器全局扫描 ═══")
        print("  ⚠️  浏览器扫描需要手动操作：")
        print("  1. 打开报表页面 http://localhost:8075/webroot/decision/view/report?viewlet=%s&op=write" % (viewlet or "YOUR_PATH"))
        print("  2. 按 F12 打开开发者工具")
        print("  3. 粘贴以下 JS 到 Console 执行：")
        print()
        print(check_browser_signals())
        print()

    # 总结
    print("\n═" * 55)
    if errors == 0 and warns == 0:
        print("  ✅ 全局检查通过，无错误无警告")
        rc = 0
    elif errors == 0:
        print("  ⚠️  通过但有 %d 个警告" % warns)
        rc = 2
    else:
        print("  ❌ 发现 %d 个错误 + %d 个警告" % (errors, warns))
        rc = 1
    print("═" * 55)
    return rc


if __name__ == "__main__":
    sys.exit(main())
