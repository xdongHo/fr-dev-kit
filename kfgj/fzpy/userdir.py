#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
userdir.py — 用户私有数据目录定位与环境解析（%USERPROFILE%\\.fr_dev_kit）

"随人走、不随套件走"的数据统一放本机用户目录，套件拷贝/外发时自动不带走：

    backup\\       模板开发备份   ← backup_template.py
    snapshot\\     模板结构快照   ← template_snapshot.py --save
    experience\\   项目经验/复盘  ← 人工（模板见 experience\\_模板_项目复盘.md）
    memory\\       用户记忆（agent 长期笔记，人工/工具维护）
    # embedding（2026-09-29 无向量改造后不再登记）.toml Embedding key 个人档（jcxt/js 检索工具读，见首次配置指南.md）
    fr_env.toml    本机 FR/JDK 路径登记（init_user_env.py 生成，可手改）

初始化向导：python kfgj/init_user_env.py

用法（kfgj 侧脚本，同目录 import）：
    import userdir
    userdir.ensure()                       # 幂等建齐目录，返回 USER_DIR
    out = userdir.SNAPSHOT_DIR / "x.json"  # 直接拼路径
    env = userdir.load_fr_env()            # fr_env.toml（无则 {}）
    fr  = userdir.resolve_fr_home()        # FR 安装根（fr_env > 环境变量 > 常见位置扫描）
    jdk = userdir.resolve_jdk_home()       # JDK8 根（同上）
"""

import glob
import os
from pathlib import Path

_HOME = Path(os.environ.get("USERPROFILE", str(Path.home())))

USER_DIR = _HOME / ".fr_dev_kit"
BACKUP_DIR = USER_DIR / "backup"
SNAPSHOT_DIR = USER_DIR / "snapshot"
EXPERIENCE_DIR = USER_DIR / "experience"
MEMORY_DIR = USER_DIR / "memory"
EMBEDDING_TOML = USER_DIR / "embedding.toml"
FR_ENV_TOML = USER_DIR / "fr_env.toml"

# 旧位置（2026-09-28 前）：文档目录；读取方做向后兼容，检测到新位置即不再看这里
EMBEDDING_TOML_LEGACY = _HOME / "Documents" / "fr_dev_kit_embedding.toml"

# FR 安装根常见位置（扫描用；fr_env.toml / FR_HOME 环境变量优先）
_FR_HOME_CANDIDATES = [
    r"C:\Program Files\FineReport_10.0",
    r"C:\Program Files\FineReport 10.0",
    r"D:\FineReport_10.0",
    r"C:\FineReport_10.0",
    r"C:\FineReport_11.0",
    r"D:\FineReport_11.0",
    r"/opt/FineReport_10.0",
]


def ensure():
    """幂等创建全部子目录，返回 USER_DIR。"""
    for d in (USER_DIR, BACKUP_DIR, SNAPSHOT_DIR, EXPERIENCE_DIR, MEMORY_DIR):
        d.mkdir(parents=True, exist_ok=True)
    return USER_DIR


def load_fr_env():
    """读 fr_env.toml（缺失/损坏返回 {}）。已知键：fr_home / jdk_home / agent_event_port / agent_exec_port / fr_server_port。"""
    try:
        import tomllib
        with open(FR_ENV_TOML, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def resolve_fr_home():
    """FR 安装根定位：fr_env.toml > 环境变量 FR_HOME > 常见位置扫描。找不到返回 None。"""
    cand = []
    env = load_fr_env()
    if env.get("fr_home"):
        cand.append(env["fr_home"])
    if os.environ.get("FR_HOME"):
        cand.append(os.environ["FR_HOME"])
    cand.extend(_FR_HOME_CANDIDATES)
    cand.extend(glob.glob(r"C:\Program Files\FineReport*\webapps", recursive=False))
    for c in cand:
        p = Path(str(c))
        if (p / "webapps" / "webroot" / "WEB-INF").is_dir() or (p / "bin" / "designer.bat").is_file() or p.is_dir():
            # 目录存在且看起来像 FR 根（有 webapps 或 bin/designer）
            if (p / "webapps").is_dir() or (p / "bin").is_dir():
                return p
    return None


def resolve_jdk_home():
    """JDK8 根定位：fr_env.toml > JAVA_HOME/JDK_HOME 环境变量 > 常见位置扫描。找不到返回 None。"""
    cand = []
    env = load_fr_env()
    if env.get("jdk_home"):
        cand.append(env["jdk_home"])
    for var in ("JDK_HOME", "JAVA_HOME"):
        if os.environ.get(var):
            cand.append(os.environ[var])
    cand.extend(glob.glob(r"C:\Program Files\Java\jdk*"))
    cand.extend(glob.glob(r"C:\Program Files\Amazon Corretto\jdk*"))
    cand.extend(glob.glob(r"C:\Program Files\Zulu\zulu-8*"))
    cand.extend(glob.glob(r"D:\jdk*\jdk*"))
    for c in cand:
        p = Path(str(c))
        if (p / "bin" / "javac.exe").is_file() or (p / "bin" / "javac").is_file():
            return p
    return None


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(f"用户私有数据目录: {ensure()}")
    print(f"  backup      → {BACKUP_DIR}")
    print(f"  snapshot    → {SNAPSHOT_DIR}")
    print(f"  experience  → {EXPERIENCE_DIR}")
    print(f"  memory      → {MEMORY_DIR}")
    print(f"  embedding   → {EMBEDDING_TOML} "
          f"({'存在' if EMBEDDING_TOML.is_file() or EMBEDDING_TOML_LEGACY.is_file() else '缺失'})"
          + (f"；旧位置仍存在: {EMBEDDING_TOML_LEGACY}" if EMBEDDING_TOML_LEGACY.is_file() else ""))
    fr = resolve_fr_home()
    jdk = resolve_jdk_home()
    print(f"  fr_env.toml → {FR_ENV_TOML} ({'存在' if FR_ENV_TOML.is_file() else '未生成（跑 init_user_env.py）'})")
    print(f"  FR_HOME     → {fr or '未检测到'}")
    print(f"  JDK_HOME    → {jdk or '未检测到'}")
