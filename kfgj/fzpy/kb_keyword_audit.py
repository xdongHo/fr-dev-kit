# -*- coding: utf-8 -*-
"""
KB_INDEX keywords 可检索性压测与回填工具

用法:
    python kb_keyword_audit.py [--dry-run] [--backfill] [--report FILE]

功能:
    1. 扫描 ckzl/bb/外部依赖与归档声明.md官方插件逆向笔记/*.md
    2. 用正则提取正文中的实体词候选:
       - com.fr.* / com.tptj.* / com.fanruan.* / com.ray.* / com.finebi.* / com.finedsl.* / com.little.* / com.orphan.* / com.third.* 全限定类名
       - 扩展点标签名 (如 PresentKindProvider, ExtensionButtonProvider 等大驼峰标识)
       - 显著异常/特征文案 (如 LockOfFunctionRecorder, PLUGIN.FD 等)
    3. 对每个候选词测: 是否已在同篇 KB_INDEX keywords 或 title/summary 中(命中即可检索); 不在=盲区
    4. 输出按篇统计: 实体词总数/盲区数/盲区率; 全库盲区 TOP20 词
    5. --backfill: 对盲区率>30% 且盲区词>=5 的篇, 把盲区词追加到 KB_INDEX keywords 区,
       单篇 keywords 总数控制在 25 个内, 优先级: 类名>标签>异常文案; 不改 title/summary/正文
    6. 幂等: 可重复运行, --backfill 只追加不重复

环境变量:
    PYTHONIOENCODING=utf-8
    PYTHONUTF8=1
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

import os
import re
import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

# ── 常量 ──
KB_ROOT = Path(r"<工具包根目录>(个人版)")
NOTES_DIR = KB_ROOT / "插件开发" / "官方插件逆向笔记"
KB_INDEX_PATH = KB_ROOT / "jcxt/data/_kb_index.yaml"
MAX_KEYWORDS = 25
BACKFILL_THRESHOLD_RATE = 0.30
BACKFILL_THRESHOLD_COUNT = 5

# ── 正则 ──
# 全限定类名: com.fr.xxx.Yyy / com.tptj.xxx / com.fanruan.xxx / com.ray.xxx / com.finebi.xxx / com.finedsl.xxx / com.little.xxx / com.orphan.xxx / com.third.xxx
RE_FQCN = re.compile(
    r'\b(com\.(?:fr|tptj|fanruan|ray|finebi|finedsl|little|orphan|third)\.[a-zA-Z0-9_.]+(?:\.[A-Z][a-zA-Z0-9]*))\b'
)
# 扩展点标签名: 大驼峰单词, 长度>=12 或以 Provider/Handler/Filter/Monitor/Recorder/Listener/Actor/Factory/Processor/Interceptor/Creator/Builder/Manager/Service/Component 结尾
RE_EXTENSION_POINT = re.compile(
    r'\b([A-Z][a-zA-Z0-9]*(?:Provider|Handler|Filter|Monitor|Recorder|Listener|Actor|Factory|Processor|Interceptor|Creator|Builder|Manager|Service|Component|Exporter|Importer|Processor|Finder|Locator|Resolver|Loader|Executor|Runner|Scheduler|Dispatcher|Registry|Registry|Register|Registrar|Registry|Registry))\b'
)
# 显著异常/特征文案: 大写字母+数字+下划线组合, 长度>=8
RE_EXCEPTION_TEXT = re.compile(
    r'\b([A-Z][A-Z0-9_]{7,})\b'
)
# PLUGIN.FD 等带点号的特征标识
RE_PLUGIN_FD = re.compile(
    r'\b(PLUGIN\.[A-Z][A-Z0-9_.]*)\b'
)

def extract_entity_candidates(text: str) -> dict:
    """从文本中提取实体词候选, 返回 {type: [words]}"""
    candidates = {
        'fqcn': [],           # 全限定类名
        'extension_point': [], # 扩展点标签名
        'exception_text': [],  # 显著异常文案
    }
    
    # 提取全限定类名
    fqcn_matches = RE_FQCN.findall(text)
    # 去重并过滤常见噪音
    noise_fqcn = {
        'com.fr.web.core', 'com.fr.json.JSONObject', 'com.fr.general.Inter',
        'com.fr.stable.web.Repository', 'com.fr.form.ui.Widget',
        'com.fr.design.mainframe', 'com.fr.io.collection.ExportCollection',
    }
    for m in fqcn_matches:
        # 取完整匹配的前缀部分(去掉最后一段小写开头的包名)
        parts = m.split('.')
        # 找到第一个大写开头的部分, 取到那里为止
        for i, p in enumerate(parts):
            if p and p[0].isupper():
                fqcn = '.'.join(parts[:i+1])
                if fqcn not in noise_fqcn and len(fqcn) > 15:
                    candidates['fqcn'].append(fqcn)
                break
    
    # 提取扩展点标签名
    ep_matches = RE_EXTENSION_POINT.findall(text)
    candidates['extension_point'] = list(set(ep_matches))
    
    # 提取显著异常文案
    exc_matches = RE_EXCEPTION_TEXT.findall(text)
    # 过滤常见噪音
    noise_exc = {
        'COMPUTER_NAME', 'DEFAULT_VALUE', 'CHANGE_NOTES', 'ENV_VERSION',
        'JAR_TIME', 'PLUGIN_ID', 'PLUGIN_NAME', 'FUNCTION_RECORDER',
        'EXTRA_CORE', 'EXTRA_REPORT', 'EXTRA_DESIGNER', 'EXTRA_MOBILE',
    }
    candidates['exception_text'] = [w for w in exc_matches if w not in noise_exc and len(w) >= 8]
    
    # 提取 PLUGIN.FD 等特征标识
    plugin_fd_matches = RE_PLUGIN_FD.findall(text)
    candidates['exception_text'].extend(plugin_fd_matches)
    
    # 去重
    for key in candidates:
        candidates[key] = list(set(candidates[key]))
    
    return candidates

def parse_kb_index_keywords(path: Path) -> dict:
    """解析 jcxt/data/_kb_index.yaml, 返回 {path: {title, summary, keywords}}"""
    # 简单的 YAML 解析(不依赖 PyYAML)
    result = {}
    current_node = None
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            
            # 匹配 path 行
            m = re.match(r'\s+-\s+path:\s+"([^"]+)"', line)
            if m:
                current_node = {'path': m.group(1), 'title': '', 'summary': '', 'keywords': []}
                result[m.group(1)] = current_node
                continue
            
            if current_node is None:
                continue
            
            # 匹配 title
            m = re.match(r'\s+title:\s+"([^"]*)"', line)
            if m:
                current_node['title'] = m.group(1)
                continue
            
            # 匹配 summary
            m = re.match(r'\s+summary:\s+"([^"]*)"', line)
            if m:
                current_node['summary'] = m.group(1)
                continue
            
            # 匹配 keywords
            m = re.match(r'\s+keywords:\s+\[(.+)\]', line)
            if m:
                kw_str = m.group(1)
                # 提取引号内的词
                keywords = re.findall(r'"([^"]*)"', kw_str)
                current_node['keywords'] = keywords
                continue
    
    return result

def check_keyword_in_index(keyword: str, node: dict) -> bool:
    """检查关键词是否在 KB_INDEX 的 keywords/title/summary 中"""
    kw_lower = keyword.lower()
    
    # 检查 keywords
    for kw in node.get('keywords', []):
        if kw_lower in kw.lower():
            return True
    
    # 检查 title
    if kw_lower in node.get('title', '').lower():
        return True
    
    # 检查 summary
    if kw_lower in node.get('summary', '').lower():
        return True
    
    return False

def analyze_note(note_path: Path, kb_index: dict) -> dict:
    """分析单篇笔记, 返回统计结果"""
    with open(note_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 KB_INDEX 块中的现有 keywords
    existing_keywords = []
    m = re.search(r'<!--\s*KB_INDEX:\s*\{[^}]*keywords:\s*\[([^\]]*)\][^}]*\}\s*-->', content)
    if m:
        existing_keywords = re.findall(r'"([^"]*)"', m.group(1))
    
    # 提取实体词候选
    candidates = extract_entity_candidates(content)
    
    # 获取 KB_INDEX 中的节点信息
    rel_path = note_path.relative_to(KB_ROOT)
    node = kb_index.get(str(rel_path).replace('\\', '/'), {})
    
    # 统计
    total_entities = 0
    blind_entities = []
    blind_details = {'fqcn': [], 'extension_point': [], 'exception_text': []}
    
    for entity_type, words in candidates.items():
        for word in words:
            total_entities += 1
            # 检查是否在现有 keywords 中
            if word in existing_keywords:
                continue
            # 检查是否在 KB_INDEX 的 keywords/title/summary 中
            if check_keyword_in_index(word, node):
                continue
            # 盲区
            blind_entities.append(word)
            blind_details[entity_type].append(word)
    
    blind_count = len(blind_entities)
    blind_rate = blind_count / total_entities if total_entities > 0 else 0.0
    
    return {
        'path': str(rel_path).replace('\\', '/'),
        'filename': note_path.name,
        'total_entities': total_entities,
        'blind_count': blind_count,
        'blind_rate': blind_rate,
        'blind_entities': blind_entities,
        'blind_details': blind_details,
        'existing_keywords': existing_keywords,
        'candidates': candidates,
    }

def backfill_note(note_path: Path, blind_entities: list, existing_keywords: list, dry_run: bool = False) -> bool:
    """回填盲区词到 KB_INDEX keywords 区, 返回是否修改"""
    if not blind_entities:
        return False
    
    # 优先级: 类名>标签>异常文案
    # 这里简单按长度排序(长的优先, 通常是更具体的类名)
    sorted_blind = sorted(blind_entities, key=lambda x: -len(x))
    
    # 计算可追加的数量
    current_count = len(existing_keywords)
    available = MAX_KEYWORDS - current_count
    if available <= 0:
        return False
    
    to_add = sorted_blind[:available]
    if not to_add:
        return False
    
    with open(note_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 KB_INDEX 块
    m = re.search(r'(<!--\s*KB_INDEX:\s*\{[^}]*keywords:\s*\[)([^\]]*)(\][^}]*\}\s*-->)', content)
    if not m:
        # 没有 KB_INDEX 块, 需要添加
        # 查找文件开头是否有 # 标题
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                insert_pos = i + 1
                break
        
        # 构建 KB_INDEX 块
        kw_str = ', '.join(f'"{kw}"' for kw in to_add)
        kb_block = f'<!-- KB_INDEX: {{"keywords": [{kw_str}]}} -->\n'
        
        lines.insert(insert_pos, kb_block)
        new_content = '\n'.join(lines)
    else:
        # 已有 KB_INDEX 块, 追加 keywords
        prefix = m.group(1)
        existing_kw_str = m.group(2)
        suffix = m.group(3)
        
        # 解析现有 keywords
        existing = re.findall(r'"([^"]*)"', existing_kw_str)
        
        # 去重
        all_keywords = list(existing)
        for kw in to_add:
            if kw not in all_keywords:
                all_keywords.append(kw)
        
        # 限制总数
        if len(all_keywords) > MAX_KEYWORDS:
            all_keywords = all_keywords[:MAX_KEYWORDS]
        
        new_kw_str = ', '.join(f'"{kw}"' for kw in all_keywords)
        new_content = content[:m.start()] + prefix + new_kw_str + suffix + content[m.end():]
    
    if not dry_run:
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return True

def main():
    parser = argparse.ArgumentParser(description='KB_INDEX keywords 可检索性压测与回填工具')
    parser.add_argument('--dry-run', action='store_true', help='只分析不修改文件')
    parser.add_argument('--backfill', action='store_true', help='执行回填操作')
    parser.add_argument('--report', type=str, help='输出报告文件路径')
    args = parser.parse_args()
    
    # 解析 KB_INDEX
    print("解析 jcxt/data/_kb_index.yaml...")
    kb_index = parse_kb_index_keywords(KB_INDEX_PATH)
    print(f"  解析完成, 共 {len(kb_index)} 个条目")
    
    # 扫描笔记
    print(f"\n扫描 {NOTES_DIR}...")
    note_files = sorted(NOTES_DIR.glob("*.md"))
    print(f"  找到 {len(note_files)} 篇笔记")
    
    # 分析每篇笔记
    results = []
    for i, note_path in enumerate(note_files, 1):
        print(f"  [{i}/{len(note_files)}] 分析 {note_path.name}...")
        result = analyze_note(note_path, kb_index)
        results.append(result)
    
    # 统计汇总
    total_notes = len(results)
    total_entities = sum(r['total_entities'] for r in results)
    total_blind = sum(r['blind_count'] for r in results)
    overall_blind_rate = total_blind / total_entities if total_entities > 0 else 0.0
    
    # 全库盲区词 TOP20
    all_blind_words = []
    for r in results:
        all_blind_words.extend(r['blind_entities'])
    blind_counter = Counter(all_blind_words)
    top20_blind = blind_counter.most_common(20)
    
    # 输出统计
    print("\n" + "="*60)
    print("统计汇总 (回填前)")
    print("="*60)
    print(f"总笔记数: {total_notes}")
    print(f"总实体词数: {total_entities}")
    print(f"总盲区词数: {total_blind}")
    print(f"整体盲区率: {overall_blind_rate:.2%}")
    
    print(f"\n全库盲区 TOP20 词:")
    for i, (word, count) in enumerate(top20_blind, 1):
        print(f"  {i:2d}. {word} (出现 {count} 篇)")
    
    # 按篇统计
    print(f"\n按篇盲区率统计:")
    print(f"{'文件名':<60} {'实体词':>6} {'盲区':>6} {'盲区率':>8}")
    print("-"*80)
    for r in sorted(results, key=lambda x: -x['blind_rate']):
        print(f"{r['filename']:<60} {r['total_entities']:>6} {r['blind_count']:>6} {r['blind_rate']:>8.2%}")
    
    # 执行回填
    if args.backfill:
        print("\n" + "="*60)
        print("执行回填")
        print("="*60)
        
        backfill_count = 0
        for r in results:
            if r['blind_rate'] > BACKFILL_THRESHOLD_RATE and r['blind_count'] >= BACKFILL_THRESHOLD_COUNT:
                note_path = NOTES_DIR / r['filename']
                print(f"  回填 {r['filename']} (盲区率 {r['blind_rate']:.2%}, 盲区词 {r['blind_count']} 个)...")
                if backfill_note(note_path, r['blind_entities'], r['existing_keywords'], args.dry_run):
                    backfill_count += 1
        
        print(f"\n回填完成: {backfill_count} 篇笔记被修改")
        
        # 重新分析
        if not args.dry_run:
            print("\n重新分析回填后的结果...")
            results_after = []
            for note_path in note_files:
                result = analyze_note(note_path, kb_index)
                results_after.append(result)
            
            total_entities_after = sum(r['total_entities'] for r in results_after)
            total_blind_after = sum(r['blind_count'] for r in results_after)
            overall_blind_rate_after = total_blind_after / total_entities_after if total_entities_after > 0 else 0.0
            
            print(f"\n回填后统计:")
            print(f"  总实体词数: {total_entities_after}")
            print(f"  总盲区词数: {total_blind_after}")
            print(f"  整体盲区率: {overall_blind_rate_after:.2%}")
            print(f"  盲区率下降: {overall_blind_rate - overall_blind_rate_after:.2%}")
    
    # 生成报告
    if args.report:
        print(f"\n生成报告: {args.report}")
        report_lines = []
        report_lines.append("# 插件开发笔记 keywords 可检索性压测报告\n")
        report_lines.append(f"## 统计汇总\n")
        report_lines.append(f"- 总笔记数: {total_notes}")
        report_lines.append(f"- 总实体词数: {total_entities}")
        report_lines.append(f"- 总盲区词数: {total_blind}")
        report_lines.append(f"- 整体盲区率: {overall_blind_rate:.2%}\n")
        
        report_lines.append(f"## 全库盲区 TOP20 词\n")
        report_lines.append("| 排名 | 词 | 出现篇数 |")
        report_lines.append("|---:|---|---:|")
        for i, (word, count) in enumerate(top20_blind, 1):
            report_lines.append(f"| {i} | `{word}` | {count} |")
        report_lines.append("")
        
        report_lines.append(f"## 按篇盲区率统计\n")
        report_lines.append("| 文件名 | 实体词 | 盲区 | 盲区率 |")
        report_lines.append("|---|---:|---:|---:|")
        for r in sorted(results, key=lambda x: -x['blind_rate']):
            report_lines.append(f"| {r['filename']} | {r['total_entities']} | {r['blind_count']} | {r['blind_rate']:.2%} |")
        report_lines.append("")
        
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"  报告已生成: {args.report}")

if __name__ == '__main__':
    main()
