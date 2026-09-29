# -*- coding: utf-8 -*-
"""Final verification: 21 files, ID authenticity, 2289 coverage, concept traceability."""
import json, os, re, glob

BASE = os.path.dirname(os.path.abspath(__file__))
NOTE_DIR = BASE
OUT_DIR = os.path.join(BASE, '_parsed')

with open(os.path.join(OUT_DIR, 'all_docs.json'), encoding='utf-8') as f:
    docs = json.load(f)
doc_by_id = {d['did']: d for d in docs}
all_ids = set(doc_by_id.keys())
print(f'all_docs: {len(docs)}')

EXPECTED = [
    'README.md', 'chart_summary.md', 'data_source_summary.md', 'deploy_cluster_summary.md',
    'export_summary.md', 'fill_submit_summary.md', 'formula_summary.md', 'frm_decision_summary.md',
    'mobile_summary.md', 'permission_summary.md', 'param_control_summary.md', 'print_summary.md',
    'js_api_summary.md', 'skin_theme_summary.md', 'performance_summary.md', 'other_summary.md',
    'fr11_java_api_i18n.md', 'fr11_i18n_api_optimization.md', 'fr11_install_survey_report.md',
    'fvs_dashboard_summary.md', 'fr10_i18n_verification_report.md',
]
missing = [e for e in EXPECTED if not os.path.exists(os.path.join(NOTE_DIR, e))]
print(f'expected files: {len(EXPECTED)}, missing: {missing}')

# 1. all doc IDs in category notes must be real; collect coverage
CAT_FILES = ['chart_summary.md', 'data_source_summary.md', 'deploy_cluster_summary.md',
             'export_summary.md', 'fill_submit_summary.md', 'formula_summary.md',
             'frm_decision_summary.md', 'mobile_summary.md', 'permission_summary.md',
             'param_control_summary.md', 'print_summary.md', 'js_api_summary.md',
             'skin_theme_summary.md', 'performance_summary.md', 'other_summary.md']
covered = {}
fabricated = []
for fn in CAT_FILES:
    with open(os.path.join(NOTE_DIR, fn), encoding='utf-8') as f:
        text = f.read()
    ids = re.findall(r'\*\*doc-view ID\*\*：(\d+)', text)
    for i in ids:
        if i not in doc_by_id:
            fabricated.append((fn, i))
        covered.setdefault(i, []).append(fn)

print(f'category notes doc entries: {len(covered)}')
dups = {k: v for k, v in covered.items() if len(v) > 1}
print(f'duplicated across categories: {len(dups)} {dict(list(dups.items())[:5])}')
uncovered = all_ids - set(covered)
print(f'uncovered by category notes: {len(uncovered)} {sorted(uncovered, key=int)[:10]}')
print(f'fabricated IDs: {fabricated[:10]}')

# 2. every category total == actual distribution
from collections import Counter
actual = Counter(d['category'] for d in docs)
total_in_notes = 0
for fn in CAT_FILES:
    with open(os.path.join(NOTE_DIR, fn), encoding='utf-8') as f:
        text = f.read()
    n = len(re.findall(r'\*\*doc-view ID\*\*：(\d+)', text))
    total_in_notes += n
print(f'total entries in 15 category notes: {total_in_notes} (should be 2289)')

# 3. concept traceability: greedy char coverage for a random sample of entries
import random
random.seed(7)
sample = random.sample(list(covered.keys()), 60)

def greedy_coverage(sentence, raw):
    s = re.sub(r'\s+', '', sentence)
    r = re.sub(r'\s+', '', raw)
    pos = 0
    hit = 0
    for ch in s:
        found = r.find(ch, pos)
        if found != -1:
            hit += 1
            pos = found + 1
    return hit / max(1, len(s))

bad = []
for did in sample:
    doc = doc_by_id[did]
    with open(os.path.join(NOTE_DIR, [f for f in CAT_FILES if did in covered and f == [cf for cf in covered[did]][0]][0]), encoding='utf-8') as f:
        pass
    # simpler: find the entry in whichever file covers it
    entry_text = ''
    for fn in covered[did]:
        with open(os.path.join(NOTE_DIR, fn), encoding='utf-8') as f:
            t = f.read()
        m = re.search(rf'### doc-view-{did}｜(.+?)\n(.*?)(?=\n### doc-view-|\n## 总结|$)', t, re.S)
        if m:
            entry_text = m.group(2)
            break
    cm = re.search(r'\*\*核心概念\*\*：(.+)', entry_text)
    if not cm:
        bad.append((did, 'no concept'))
        continue
    concept = cm.group(1)
    # split into sentences and check each
    for sent in re.split(r'(?<=[。！？])', concept):
        if len(sent) < 8:
            continue
        cov = greedy_coverage(sent, doc['text'])
        if cov < 0.85:
            bad.append((did, sent[:40], round(cov, 2)))
print(f'concept traceability sample: {len(sample)} docs, bad: {len(bad)}')
for b in bad[:10]:
    print('  BAD:', b)

# 4. supplementary notes: all IDs real
sup_bad = []
for fn in ['fr11_java_api_i18n.md', 'fr11_install_survey_report.md', 'fvs_dashboard_summary.md',
           'fr11_i18n_api_optimization.md', 'fr10_i18n_verification_report.md']:
    with open(os.path.join(NOTE_DIR, fn), encoding='utf-8') as f:
        text = f.read()
    ids = re.findall(r'doc-view-(\d+)', text)
    for i in ids:
        if i not in doc_by_id:
            sup_bad.append((fn, i))
print(f'supplementary fabricated IDs: {sup_bad[:10]}')

# 5. unparseable check in notes
unparseable_count = 0
for fn in EXPECTED:
    with open(os.path.join(NOTE_DIR, fn), encoding='utf-8') as f:
        t = f.read()
    unparseable_count += t.count('无法解析')
print(f'"无法解析" occurrences in all notes: {unparseable_count}')

# 6. file sizes
print('--- file sizes ---')
for fn in EXPECTED:
    sz = os.path.getsize(os.path.join(NOTE_DIR, fn))
    print(f'  {fn}: {sz/1024:.1f}KB')
