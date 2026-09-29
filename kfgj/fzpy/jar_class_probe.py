#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
jar_class_probe.py — FR jar 类探针（2026-09-11 补齐: NODE-10「版本/jar 归属判据」既有引用的工具本体）

用途: NoClassDefFoundError / NoSuchMethod 排查时,判断一个类到底在不在本地 jar 集、在哪个 jar——
  0 命中 = 版本/插件不匹配(补 jar 无解,须换整套); 有命中 = classpath 顺序或 ClassLoader 问题(补 jar 有解)。

用法:
  python kfgj/fzpy/jar_class_probe.py --jars C:/frjars find Calculator
  python kfgj/fzpy/jar_class_probe.py --jars C:/frjars --jars D:/morejars find digest --contains
  python kfgj/fzpy/jar_class_probe.py --jars C:/frjars which com.fr.script.Calculator
子命令:
  find <类简单名>   按类简单名查(--contains 改为不区分大小写子串匹配)
  which <全限定名>  按全限定名定位 jar(内部类以 $ 表示)
参数:
  --jars <路径>     必填,可重复(--jars A --jars B);目录自动展开其下全部 *.jar,或单个 .jar
  --limit N         find 输出条数上限(默认 50)
  --verbose         输出 jar 完整路径而非文件名
退出码: 0=有命中 1=无命中 2=用法/IO 错误(对齐 fr_check/guard 约定)
实现: 纯标准库 zipfile 扫 jar 内 .class 条目,无 JVM 依赖;方法签名级探查走 fr-agent(19000)。
"""
import argparse, glob, os, sys, zipfile

try:  # console-safe guard
    for _s in (sys.stdout, sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass

def expand_jars(paths):
    jars = []
    for p in paths:
        if os.path.isdir(p):
            jars.extend(sorted(glob.glob(os.path.join(p, "**", "*.jar"), recursive=True)))
        elif os.path.isfile(p) and p.lower().endswith(".jar"):
            jars.append(p)
    seen, out = set(), []
    for j in jars:
        r = os.path.realpath(j)
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out

def iter_classes(jar):
    """yield (fqn, entry) — .class 条目转全限定名(内部类保留 $)。跳过 module-info/package-info。"""
    try:
        with zipfile.ZipFile(jar) as z:
            for name in z.namelist():
                if not name.endswith(".class"):
                    continue
                base = name[:-6]
                if base.endswith("module-info") or base.endswith("package-info"):
                    continue
                yield base.replace("/", "."), name
    except zipfile.BadZipFile:
        return
    except OSError:
        return

def main():
    ap = argparse.ArgumentParser(description="FR jar 类探针(类存在性/jar 归属)")
    ap.add_argument("--jars", action="append", required=True, help="jar 目录或 .jar 文件,可重复")
    ap.add_argument("--limit", type=int, default=50, help="find 输出上限(默认 50)")
    ap.add_argument("--verbose", action="store_true", help="显示 jar 完整路径")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("name", help="类简单名,如 Calculator")
    f.add_argument("--contains", action="store_true", help="改为不区分大小写子串匹配")
    w = sub.add_parser("which")
    w.add_argument("fqn", help="全限定名,如 com.fr.script.Calculator")
    a = ap.parse_args()

    jars = expand_jars(a.jars)
    if not jars:
        print("未找到任何 jar(检查 --jars 路径)", file=sys.stderr)
        sys.exit(2)
    hits = []
    if a.cmd == "find":
        needle = a.name
        for j in jars:
            for fqn, entry in iter_classes(j):
                simple = fqn.rsplit(".", 1)[-1]
                ok = (needle.lower() in simple.lower()) if a.contains else (simple == needle)
                if ok:
                    hits.append((fqn, j))
                    if not a.contains and len(hits) >= a.limit * 4:
                        break
    else:
        target = a.fqn.replace(".", "/") + ".class"
        for j in jars:
            for fqn, entry in iter_classes(j):
                if entry == target:
                    hits.append((fqn, j))
    hits = hits[: a.limit] if a.cmd == "find" else hits
    shown = 0
    for fqn, j in hits:
        loc = j if a.verbose else os.path.basename(j)
        print(f"{fqn}  <-  {loc}")
        shown += 1
    print(f"-- jars 扫描 {len(jars)} 个,命中 {len(hits)} 条(显示 {shown})"
          + ("" if hits else " —— 0 命中=版本/插件不匹配(补 jar 无解,须换整套);有命中=classpath/ClassLoader 问题(补 jar 有解)"))
    sys.exit(0 if hits else 1)

if __name__ == "__main__":
    main()
