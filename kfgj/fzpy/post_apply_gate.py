# -*- coding: utf-8 -*-
"""post_apply_gate.py — patches 提案应用后统一验收闸门（P0-P2 优化执行收口）。

用法（仓库根执行）:  python 辅助python脚本/post_apply_gate.py
退出码: 0=全过  1=有 FAIL
断言清单对应 8 份 patches 提案的落地锚点（AGENTS/接口规范/委派方案/维护流程/CHANGELOG/
17 文件元数据/fr11 主题≥16/manifest/评测集）。改文档后重跑本脚本即可回归。
"""
import io, json, os, sqlite3, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def exists(rel):
    return os.path.isfile(os.path.join(KIT, rel))

def head20(text, n=20):
    """前 n 行文本（BG-EV-10: 取代钉死前 400 字符的头部定位，抗头部加行误报）。"""
    return "\n".join(text.splitlines()[:n])

def kbindex_block(text):
    """定位 KB_INDEX 块文本（KB_INDEX: 起、注释闭合 --> 止），供字段级断言；无块返回空串。"""
    i = text.find("KB_INDEX:")
    if i < 0:
        return ""
    j = text.find("-->", i)
    return text[i:j] if j > i else text[i:i + 1500]

FM_FILES = ([r"工作流节点/%02d_%s.md" % (i, n) for i, n in
             enumerate(["工作流节点导航", "需求与数据判定", "数据集", "参数面板", "报表主体_明细展示",
                        "填报模块", "图表模块", "导入导出", "交互联动", "FRM决策报表", "预览与验证"], 0)] +
            [r"任务路由-专项主题.md", r"行级数据权限控制模式.md", r"官方文档沉淀增补-验收与判级.md",
             r"任务决策树-扩展分支.md", r"知识库治理/知识管理规范-维护流程.md",
             r"知识库治理/知识管理规范-深挖判据.md"])

FR11 = os.path.join(KIT, "pipeline", "fr11_knowledge")

def main():
    R = []

    def chk(cid, cond, note=""):
        R.append((cid, "PASS" if cond else "FAIL", note))

    def rd(rel):
        # BG-EV-05: 锚点文件缺失记 FAIL 条目（"文件缺失"）继续跑完矩阵，不再裸崩丢矩阵
        p = os.path.join(KIT, rel)
        if not os.path.isfile(p):
            R.append((rel, "FAIL", "文件缺失"))
            return ""
        return io.open(p, encoding="utf-8", errors="replace").read()

    # a) AGENTS.md
    ag = rd("AGENTS.md")
    chk("AG-STEP0", "STEP 0" in ag, "P1-3 档位表")
    chk("AG-NOCRED", ("YOUR_PG_PASSWORD" not in ag) and ("password=YOUR_PG_PASSWORD" not in ag), "P1-1#1 凭据不驻留 kernel")
    chk("AG-SCREEN", "receipt_screen" in ag, "P1-6 路由行")
    chk("AG-CONFLICT", "两级裁决" in ag, "P1-2 指针行")
    chk("AG-TODO", "todo.md" in ag, "P2-3 纪律行")
    chk("AG-KBINDEX", "KB_INDEX" in head20(ag), "kernel 元数据头保留（前 20 行）")

    # b) 接口规范
    spec = rd(r"多agent架构/接口规范.md")
    chk("SP-PRE", "派单前置校验" in spec and "委派四要素" in spec, "P0-4 四要素+定档")
    chk("SP-LIGHT", "轻引用回传协议" in spec, "P0-4/P1-4 回传协议")
    chk("SP-RETRY", "上次失败摘要" in spec, "P2-4B 重派补强")
    chk("SP-SCREEN", "receipt_screen" in spec, "P1-6B 筛查行")
    chk("SP-KBINDEX", "KB_INDEX" in head20(spec), "元数据头（前 20 行，本轮补）")

    # c) 委派方案
    dl = rd("外部AI子agent委派方案.md")
    chk("DL-DID", "数据/指令分离" in dl, "P1-6A")
    chk("DL-COMPACT", "压缩保留清单" in dl, "P2-4A")
    chk("DL-SUMMARY", "上次失败摘要" in dl, "P2-4A")

    # d) 维护流程
    mt = rd(r"知识库治理/知识管理规范-维护流程.md")
    chk("MT-CONFLICT", "4.7 规则冲突两级裁决" in mt, "P1-2")
    chk("MT-SLIM", "4.8 Kernel 季度瘦身轮" in mt, "P1-1 制度")
    chk("MT-DUAL", "双写（P2-5" in mt, "P2-5 指针")

    # e) CHANGELOG + README
    cl_ok = exists(r"版本变更/CHANGELOG.md") and ("v3.0-20260914" in rd(r"版本变更/CHANGELOG.md"))
    chk("CL-EXIST", cl_ok, "P2-5 建档")
    chk("RM-VER", "v3.0-20260914" in rd("README.md"), "README 版本行")

    # f) 17 元数据文件（FM-17 字段级：KB_INDEX 块内 trigger/when_not 两键各自存在才过，不再全文子串弱断言）
    miss = []
    for f in FM_FILES:
        blk = kbindex_block(rd(f))
        if '"trigger"' not in blk or '"when_not"' not in blk:
            miss.append(f)
    chk("FM-17", not miss, "缺失: %s" % (miss if miss else "无"))

    # g) fr11 主题 compatibility（≥16 防误杀新增；新增主题须同步登记本闸门与 SKILL.md compatibility 段）
    topics = [d for d in sorted(os.listdir(FR11))
              if os.path.isdir(os.path.join(FR11, d)) and not d.startswith("_")]
    bad = [d for d in topics
           if "compatibility" not in rd(os.path.join("pipeline", "fr11_knowledge", d, "SKILL.md"))]
    chk("F11-COMPAT", (len(topics) >= 16) and not bad,
        "主题数=%d(>=16, 新增主题须同步登记) 缺失=%s" % (len(topics), bad or "无"))

    # h) manifest + fts
    man_ok = False
    try:
        man = json.load(io.open(os.path.join(KIT, "工程知识库", "script_manifest.json"), encoding="utf-8"))
        man_ok = man.get("count", 0) > 100
    except Exception as e:
        man_ok = False
    chk("MF-EXIST", man_ok, "P1-7 manifest")
    fts_ok = False
    try:
        fts_ok = sqlite3.connect(os.path.join(KIT, "向量检索", "_kb_fts.db")).execute(
            "SELECT COUNT(*) FROM chunks_fts").fetchone()[0] > 10000
    except Exception:
        pass
    chk("FTS-OK", fts_ok, "P0-2 快照")

    # i) 评测集
    n_cases = sum(1 for l in rd("evals/cases.jsonl").splitlines() if l.strip())
    chk("EV-CASES", n_cases >= 36, "用例数=%d" % n_cases)

    # 汇总
    print("=" * 66)
    print("post_apply_gate 验收矩阵（patches 应用收口）")
    print("-" * 66)
    n_pass = 0
    for cid, st, note in R:
        n_pass += (st == "PASS")
        print("  [%s] %-12s %s" % (st, cid, note))
    print("-" * 66)
    print("  汇总: %d/%d PASS" % (n_pass, len(R)))
    print("=" * 66)
    return 0 if n_pass == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
