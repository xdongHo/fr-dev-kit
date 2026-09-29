#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
submit_config_check.py — 填报提交配置内容校验器 v1.1（2026-09-12 P1，用户确认）
补 NODE-05 最大覆盖缺口: fr_check 只识别"提交配置存在+类型"，本工具做内容级断言。

规格依据: ckzl/gzjd/05填报模块.md + ckzl/lc/05 §9/§22 + 填报提交规范提取报告
(_runs/填报提交规范提取报告_20260912.md: 17,676 cpt 全量扫描, 7,433 含 RWA/42%)
三种 RWA 形态全识别:
  A 经典  SubmitVisitor(BuiltInSQLSubmiter)+DMLConfig(Table/ColumnConfig/ColumnRow)
  B 空形态 <ReportWriteAttr/> 自闭合(实测 1,399 个, 合法: 填报展示型/自定义提交)
  C 新形态 WriteType="2"+DBSubmiter+DMLConfig type="upsert"+ColumnRowDict(61 个, kit 生成器)
绑定三形态: ColumnRow / ColumnConfig 内 <Parameter>(列值=模板参数) / ColumnRowDict
其他语义: isKey=更新/删除 WHERE 条件(≠数据库主键); DMLConfig XML 顺序=事务顺序;
         ≥2 SubmitVisitor 且 dsName 不同+Table 相同 = 双环境提交(S17 WARN)

校验项:
  S1 填报特征互证   含 verifyReportSubmit 提交 JS 但无 ReportWriteAttr → FAIL
  S2 提交器完整性   SubmitVisitor 无 class / BuiltInSQLSubmiter 无 dsName → FAIL
                    (dsName 为数据连接名, 服务端配置——cpt 内无法校验存在性)
  S3 目标表定义     DMLConfig 无 Table 或 name 空 → FAIL
  S4 提交列非空     无 ColumnConfig 且无 ColumnRowDict → FAIL
  S5 主键(WHERE)覆盖 无 isKey=true → WARN; DeleteConfig 无 key → FAIL
  S6 绑定存在性     ColumnConfig 三种绑定形态(ColumnRow/Parameter/ColumnRowDict)均无 → FAIL
  S17 双环境        ≥2 SubmitVisitor 且 dsName 不同 + Table 相同 → WARN
  S7 --db 库级校验  Table(schema.name) 存在性(不在当前 DSN 库→WARN 口径提示);
                    提交列(classic=ColumnConfig name / upsert=DSColumn columnName) ⊄ 表列 → FAIL

用法:
  python kfgj/fzpy/submit_config_check.py <cpt路径> [--db] [--out report.json]
退出码: 0=通过 1=有 FAIL 2=有 WARN/SKIP(对齐 fr_check/guard 约定)
依赖: 静态模式纯标准库; --db 需 Python311+psycopg2+DWS 网络(复用 db_schema)
"""
import argparse, json, os, sys, xml.etree.ElementTree as ET

try:  # console-safe guard
    for _s in (sys.stdout, sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass

_HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    ap = argparse.ArgumentParser(description="填报提交配置内容校验器 v1.1")
    ap.add_argument("cpt", help="cpt 模板路径")
    ap.add_argument("--db", action="store_true", help="库级校验: 目标表存在 + 提交列⊆表列(需 psycopg2/DWS)")
    ap.add_argument("--out", default="", help="JSON 报告输出路径")
    a = ap.parse_args()

    if not os.path.isfile(a.cpt):
        print("[FAIL] 文件不存在: %s" % a.cpt)
        return 1
    raw = open(a.cpt, encoding="utf-8").read()
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print("[FAIL] XML 解析失败: %s" % e)
        return 1

    findings = []
    def add(level, cid, msg, ev=""):
        findings.append({"level": level, "id": cid, "message": msg, "evidence": ev[:280]})
        print("  [%s] %s  %s" % (level, msg, ("| " + ev[:120]) if ev else ""))

    rwas = list(root.iter("ReportWriteAttr"))
    has_submit_js = "verifyReportSubmit" in raw
    # 模板单元格坐标——四种形态全收: <Cell col row> / 缩写 <C c r> / FixCell / 任意 col+row 属性元素
    cells = set()
    for el in root.iter():
        for pair in ((el.get("col"), el.get("row")), (el.get("c"), el.get("r"))):
            try:
                cells.add((int(pair[0]), int(pair[1])))
            except (TypeError, ValueError):
                pass
    ds_names = {td.get("name") for td in root.iter("TableData") if td.get("name")}

    if not rwas:
        if has_submit_js:
            add("FAIL", "S1", "存在提交 JS(verifyReportSubmit) 但模板无 ReportWriteAttr —— 提交不会生效(NODE-05 期望规则)")
        else:
            add("info", "S0", "非填报模板: 无 ReportWriteAttr 且无提交 JS, 无需提交配置校验")
            return _finish(a, findings, db_used=False)

    db_targets = []
    for ri, rwa in enumerate(rwas, 1):
        tag = "RWA%d" % ri if len(rwas) > 1 else "RWA"
        rwa_children = list(rwa)
        if not rwa_children:
            lvl = "WARN" if has_submit_js else "info"
            add(lvl, tag + "-S2", "空形态 ReportWriteAttr(未配置提交器)%s" %
                ("—— 但存在提交 JS, 请确认自定义提交通道" if has_submit_js else ""))
            continue
        wtel = rwa.find("WriteType")
        if wtel is not None:
            add("info", tag, "WriteType=%s" % wtel.text)
        committers = [("classic", sv) for sv in rwa.findall("SubmitVisitor")] + \
                     [("api", db) for db in rwa.findall("DBSubmiter")]
        if not committers:
            tvs = rwa.findall(".//TopVerifier")
            if tvs:
                add("info", tag + "-S2", "校验型 RWA: 仅 TopVerifier(%d 条校验规则), 无 DML 提交配置" % len(tvs))
            else:
                add("WARN", tag + "-S2", "ReportWriteAttr 存在但无 SubmitVisitor/DBSubmiter/TopVerifier(结构不完整)")
            continue
        env_ds, env_tbl = set(), set()
        for si, (kind, el) in enumerate(committers, 1):
            sid = "%s-SV%d" % (tag, si)
            cls = el.get("class", "")
            add("info", sid, "提交器(%s): %s" % (kind, cls or "<无 class>"))
            if not cls:
                add("FAIL", sid + "-S2", "提交器缺 class 属性")
            dmls = []
            if kind == "classic":
                if "BuiltInSQLSubmiter" in cls:
                    at = el.find("Attributes")
                    ds = (at.get("dsName") or "").strip() if at is not None else ""
                    if not ds:
                        add("FAIL", sid + "-S2", "BuiltInSQLSubmiter 缺 Attributes@dsName(数据连接)")
                    else:
                        add("info", sid + "-S2", "dsName='%s' 为数据连接名(服务端配置, cpt 内不校验存在性)" % ds)
                        env_ds.add(ds)
                dmls = el.findall("DMLConfig")
            else:
                dn = el.find(".//DatabaseName")
                conn = (dn.text or "").strip() if dn is not None else ""
                if conn:
                    add("info", sid + "-S2", "数据连接: %s" % conn)
                    env_ds.add(conn)
                else:
                    add("WARN", sid + "-S2", "DBSubmiter 缺 DataSource/DatabaseName(数据连接)")
                crd = el.find("ColumnRowDict")
                crs = crd.findall("ColumnRow") if crd is not None else []
                add("info", sid + "-S6", "ColumnRowDict 绑定: %d 条" % len(crs))
                for cr in crs:
                    try:
                        cc, rr = int(cr.get("column")), int(cr.get("row"))
                        if (cc, rr) not in cells:
                            add("FAIL", sid + "-S6", "ColumnRow 绑定单元格 (%d,%d) 不在模板中" % (cc, rr))
                    except (TypeError, ValueError):
                        add("FAIL", sid + "-S6", "ColumnRow 坐标非法: %r" % dict(cr.attrib))
                rtn = el.find("ReportTableName/Name")
                if rtn is not None and rtn.text:
                    add("info", sid + "-S2", "数据集: %s" % rtn.text.strip())
                if not crs:
                    add("WARN", sid + "-S6", "ColumnRowDict 为空(无提交绑定)")
            if len(committers) > 1:
                add("info", sid, "多提交器: 自上而下串行执行、同一事务, XML 顺序即执行顺序(ckzl/lc/05 §9)")

            for di, dml in enumerate(dmls, 1):
                did = "%s-DM%d" % (sid, di)
                dcls = dml.get("class", "")
                dtype = dml.get("type", "")
                if kind == "api":
                    tn = dml.find("TableName")
                    full = (tn.text or "").strip() if tn is not None else ""
                    env_tbl.add(full)
                    if not full:
                        add("FAIL", did + "-S3", "DMLConfig(type=%s) 无 TableName" % (dtype or "?"))
                        continue
                    add("info", did + "-S3", "目标表: %s [upsert]" % full)
                    dscols = sorted({a.get("columnName") for a in dml.iter("Attributes") if a.get("columnName")})
                    if not dscols:
                        add("WARN", did + "-S4", "upsert DMLConfig 未提取到提交列(DSColumn)")
                    db_targets.append({"did": did, "full": full, "cols": dscols})
                    continue
                tbl = dml.find("Table")
                t_schema = (tbl.get("schema") or "").strip() if tbl is not None else ""
                t_name = (tbl.get("name") or "").strip() if tbl is not None else ""
                full = ("%s.%s" % (t_schema, t_name)) if t_schema else t_name
                env_tbl.add(full)
                if tbl is None or not t_name:
                    add("FAIL", did + "-S3", "DMLConfig(%s) 无目标表定义(Table@name)" % (dcls or "?"))
                else:
                    add("info", did + "-S3", "目标表: %s" % full)
                cols = dml.findall("ColumnConfig")
                if not cols:
                    add("FAIL", did + "-S4", "DMLConfig 无任何 ColumnConfig(提交列)")
                    continue
                keys = [c for c in cols if (c.get("isKey") or "").lower() == "true"]
                if not keys:
                    lvl = "FAIL" if "DeleteConfig" in dcls else "WARN"
                    add(lvl, did + "-S5", "无 isKey=true 列" +
                        ("—— DeleteConfig 删除语义必须 WHERE 条件" if "DeleteConfig" in dcls
                         else "—— 若涉及修改/删除必须勾选(isKey=WHERE 条件, 非数据库主键)"))
                else:
                    add("info", did + "-S5", "isKey 列: %s" % ", ".join(c.get("name", "?") for c in keys))
                for c in cols:
                    cname = c.get("name", "")
                    bound = False
                    cr = c.find("ColumnRow")
                    if cr is not None:
                        try:
                            cc, rr = int(cr.get("column")), int(cr.get("row"))
                            if cc < 0 or rr < 0:
                                raise ValueError
                            if (cc, rr) in cells:
                                bound = True
                            else:
                                add("FAIL", did + "-S6", "列 '%s' 绑定单元格 (%d,%d) 不在模板中(坐标错/单元格被删)" % (cname, cc, rr))
                        except (TypeError, ValueError):
                            add("FAIL", did + "-S6", "列 '%s' 的 ColumnRow 非法: %r" % (cname, dict(cr.attrib)))
                            continue
                    if c.find("Parameter") is not None:
                        bound = True   # 列值=模板参数(ckzl/lc/05 §22: Parameter 替代 ColumnRow)
                    if not bound and cr is None:
                        add("FAIL", did + "-S6", "列 '%s' 无绑定(ColumnRow/Parameter 均缺)" % cname)
                if tbl is not None and t_name:
                    db_targets.append({"did": did, "full": full, "cols": [c.get("name", "") for c in cols]})

        # S17: 双环境提交(≥2 提交器且 dsName/连接 不同、Table 相同)
        if len(env_ds) >= 2 and env_tbl:
            add("WARN", tag + "-S17", "双环境提交: %d 个不同数据连接写同表(%s)——确认生产/测试双写意图"
                % (len(env_ds), sorted(t for t in env_tbl if t)[:2]))


    # S7 --db
    db_used = False
    if a.db and db_targets:
        add("info", "S7", "--db 口径: 基于 LOCAL_ENV 的 DWS 连接;若模板 dsName 的数据连接指向其他库, 表级结果需按该连接另行核验")
        try:
            sys.path.insert(0, _HERE)
            import db_schema
            seen = {}
            for t in db_targets:
                if t["full"] in seen:
                    tc = seen[t["full"]]
                else:
                    try:
                        tc_raw = db_schema.table_columns(t["full"])
                        colnames = {c["name"] for c in tc_raw.get("columns", [])}
                        tc = {"ok": bool(colnames), "colnames": colnames}
                    except Exception as e:
                        tc = {"ok": False, "error": str(e)[:160]}
                    seen[t["full"]] = tc
                if not tc.get("ok"):
                    add("WARN", t["did"] + "-S7", "目标表在当前 DSN 库中未找到: %s(若模板连接指向其他库, 请按该连接核验)" % t["full"],
                        tc.get("error", ""))
                    continue
                colnames = tc["colnames"]
                miss = [c for c in t["cols"] if c and c not in colnames]
                if miss:
                    add("FAIL", t["did"] + "-S7", "提交列不在表列中: %s (表 %s 共 %d 列)" % (
                        ", ".join(miss), t["full"], len(colnames)))
                else:
                    add("info", t["did"] + "-S7", "表 %s 存在, %d 个提交列全部在表列中" % (t["full"], len(t["cols"])))
            db_used = True
        except ImportError as e:
            add("SKIP", "S7", "--db 需要 db_schema(本目录), 导入失败: %s" % str(e)[:120])
        except Exception as e:
            add("SKIP", "S7", "--db 连接失败(网络/凭据): %s" % str(e)[:160])

    return _finish(a, findings, db_used=db_used)

def _finish(a, findings, db_used=False):
    n_fail = sum(1 for f in findings if f["level"] == "FAIL")
    n_warn = sum(1 for f in findings if f["level"] == "WARN")
    n_skip = sum(1 for f in findings if f["level"] == "SKIP")
    print("---")
    print("submit_config_check: FAIL=%d WARN=%d SKIP=%d info=%d%s" % (
        n_fail, n_warn, n_skip, sum(1 for f in findings if f["level"] == "info"),
        "  (--db 已执行)" if db_used else ""))
    if a.out:
        d = os.path.dirname(os.path.abspath(a.out))
        os.makedirs(d, exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump({"cpt": a.cpt, "db_used": db_used, "findings": findings}, f, ensure_ascii=False, indent=2)
        print("报告: %s" % a.out)
    if any(f["level"] == "FAIL" for f in findings):
        return 1
    if any(f["level"] in ("WARN", "SKIP") for f in findings):
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
