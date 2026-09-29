#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_user_env.py — 开源版首次初始化向导（用户私有环境一键配置）

检测 %USERPROFILE%\\.fr_dev_kit\\，不存在或残缺则引导补齐：
  1. 目录骨架：backup/ snapshot/ experience/ memory/
  2. FR/JDK 路径：自动扫描并登记 fr_env.toml（检测错了可手改该文件）
  3. 种子文件：experience 复盘模板、memory 说明
  4. 提示建索引（FTS5 关键词 + 树索引，零 key 零配置；2026-09-29 起检索无向量，无需登记任何 key）

用法：
    python kfgj/init_user_env.py                  # 交互向导
    python kfgj/init_user_env.py --status         # 只看状态不改动
    python kfgj/init_user_env.py --mock           # 已无效果（保留仅为兼容；检索本就零 key 零配置）
"""

# --- console-safe guard (GBK 控制台打印 emoji 不再 UnicodeEncodeError) ---
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
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "fzpy"))
import userdir

MEMORY_README = """# memory — 用户记忆

> 存放跨会话要记住的事实：你的环境偏好、常用连接名、团队约定、踩过的坑。
> 属用户私有，不随套件分发。文件格式自由（建议一主题一文件 + 日期）。
"""


def status():
    print(f"用户私有数据目录: {userdir.USER_DIR}  ({'已初始化' if userdir.USER_DIR.is_dir() else '未初始化'})")
    for name, d in (("backup", userdir.BACKUP_DIR), ("snapshot", userdir.SNAPSHOT_DIR),
                    ("experience", userdir.EXPERIENCE_DIR), ("memory", userdir.MEMORY_DIR)):
        print(f"  {'✓' if d.is_dir() else '✗'} {name:10} {d}")
    print(f"  {'✓' if userdir.FR_ENV_TOML.is_file() else '✗'} fr_env    {userdir.FR_ENV_TOML}")
    fr, jdk = userdir.resolve_fr_home(), userdir.resolve_jdk_home()
    print(f"  FR_HOME 检测: {fr or '未检测到（装了 FR 但没扫到就手填 fr_env.toml 的 fr_home）'}")
    print(f"  JDK_HOME 检测: {jdk or '未检测到（仅重建 fr-agent jar 时需要）'}")


def step_embedding(args):
    """（已废弃，2026-09-29 检索无向量改造）向量/Embedding key 登记已移除，保留函数仅为兼容旧调用。"""
    print("ℹ 检索已无向量化（FTS5 关键词 + 树索引 + 页导航），零 key 零配置，无需登记任何 Embedding key。")


def step_fr_env():
    if userdir.FR_ENV_TOML.is_file():
        print("✅ fr_env.toml 已存在，跳过")
        return
    fr, jdk = userdir.resolve_fr_home(), userdir.resolve_jdk_home()
    lines = [
        "# 本机 FR/JDK 环境登记（init_user_env.py 生成；检测不对就直接改这里）",
        f'fr_home = "{str(fr) if fr else ""}"',
        f'jdk_home = "{str(jdk) if jdk else ""}"',
        "# fr-agent 注入通道端口（默认 18999/19000，被占用才改）",
        "agent_event_port = 18999",
        "agent_exec_port = 19000",
        "# FR 内置服务器端口（默认 8075）",
        "fr_server_port = 8075",
    ]
    userdir.FR_ENV_TOML.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    print(f"✅ 已写 {userdir.FR_ENV_TOML}（FR={'检测到' if fr else '未检测到，离线生成模板可不装'}）")


def step_seeds():
    tpl = userdir.EXPERIENCE_DIR / "_模板_项目复盘.md"
    if not tpl.is_file():
        tpl.write_text("# <项目名> 复盘 — <日期>\n\n- 任务背景：\n- 关键决策：\n- 踩坑与解法：\n- 值得沉淀进套件知识库的（复制到 ckzl/ 后跑索引命令）：\n",
                       encoding="utf-8", newline="")
        print("✅ 已生成 experience/_模板_项目复盘.md")
    m = userdir.MEMORY_DIR / "README.md"
    if not m.is_file():
        m.write_text(MEMORY_README, encoding="utf-8", newline="")
        print("✅ 已生成 memory/README.md")


def main():
    ap = argparse.ArgumentParser(description="开源版首次初始化向导（~/.fr_dev_kit）")
    ap.add_argument("--status", action="store_true", help="只看状态")
    ap.add_argument("--mock", action="store_true",
                    help="已无效果（保留仅为兼容；检索零 key 零配置，无需任何 key）")
    # 以下旧 Embedding 参数保留占位仅为兼容旧命令行，均无效果
    ap.add_argument("--provider", help=argparse.SUPPRESS)
    ap.add_argument("--api-key", help=argparse.SUPPRESS)
    ap.add_argument("--base-url", help=argparse.SUPPRESS)
    ap.add_argument("--model", help=argparse.SUPPRESS)
    ap.add_argument("--dims", type=int, help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.status:
        status()
        return
    if args.provider or args.api_key or args.base_url or args.model or args.dims:
        print("⚠ --provider/--api-key/--base-url/--model/--dims 已无效果：向量路已移除（2026-09-29）。")
    print("=" * 60)
    print("FR 报表模板开发工具包 · 用户环境初始化")
    print("=" * 60)
    userdir.ensure()
    print(f"✅ 目录骨架就绪: {userdir.USER_DIR}")
    step_embedding(args)
    step_fr_env()
    step_seeds()
    print("\n── 下一步 ──")
    print("  1. 建知识索引: python jcxt/js/build_fts_index.py + python jcxt/js/build_tree_index.py（零 key 零配置）")
    print("  2. 环境自检:   python kfgj/guard.py --selftest")
    print("  3. 开始使用:   读 AGENTS.md（唯一入口）")
    print("\n说明：数据/路径都在 ~/.fr_dev_kit/ 下，套件拷贝/外发不会带走；换机拷整个 .fr_dev_kit 即延续。")


if __name__ == "__main__":
    main()
