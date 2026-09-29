#!/usr/bin/env python3
import urllib.request, re, html as html_mod, json, time, sys

docs = [
    (4244, "计算入门指南", "报表专题 > 函数 > 函数概念"),
    (253, "函数计算格式", "报表专题 > 函数 > 函数概念"),
    (249, "计算操作符说明", "报表专题 > 函数 > 函数概念"),
    (252, "正则表达式示例", "报表专题 > 函数 > 函数概念"),
    (3930, "设计器函数汇总", "报表专题 > 函数 > 函数列表"),
    (831, "常用函数概述", "报表专题 > 函数 > 函数列表 > 常用函数"),
    (869, "Count函数", "报表专题 > 函数 > 函数列表 > 常用函数"),
    (867, "Range函数", "报表专题 > 函数 > 函数列表 > 常用函数"),
    (827, "数学函数概述", "报表专题 > 函数 > 函数列表 > 数学函数"),
    (840, "Round函数", "报表专题 > 函数 > 函数列表 > 数学函数"),
    (3598, "三角函数概述", "报表专题 > 函数 > 函数列表 > 三角函数"),
    (824, "文本函数概述", "报表专题 > 函数 > 函数列表 > 文本函数"),
    (1897, "字符串拼接函数", "报表专题 > 函数 > 函数列表 > 文本函数"),
    (880, "截取、替换字符串", "报表专题 > 函数 > 函数列表 > 文本函数"),
    (819, "日期和时间函数概述", "报表专题 > 函数 > 生成日期和时间函数"),
]

results = {}

for did, name, path in docs:
    url = f"https://help.fanruan.com/finereport10.0/doc-view-{did}.html"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        raw = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
        
        # Extract title
        title_m = re.search(r'<title>(.*?)</title>', raw)
        title = html_mod.unescape(title_m.group(1).strip()) if title_m else "N/A"
        
        # Method 1: meta description
        meta = re.search(r'<meta name="description" content="(.*?)"', raw)
        meta_desc = html_mod.unescape(meta.group(1)).strip() if meta else ""
        
        # Method 2: doctitle content
        start = raw.find("id='doctitle'")
        if start >= 0:
            start = raw.find('>', start) + 1
            end = raw.find('<div class="comment"', start)
            if end < 0:
                end = start + 30000
            content = raw[start:end]
        else:
            content = ""
        
        # Also try viewBox
        vb_start = raw.find("id='viewBox'")
        if vb_start >= 0:
            vb_start = raw.find('>', vb_start) + 1
            vb_end = raw.find('</div>', vb_start)
            if vb_end > vb_start and vb_end - vb_start > 100:
                viewbox = raw[vb_start:vb_end]
            else:
                viewbox = content
        else:
            viewbox = content
        
        # Also try content_topp
        ct_start = raw.find('class="content_topp"')
        if ct_start >= 0:
            ct_start = raw.find('>', ct_start) + 1
            ct_end = raw.find('</div>', ct_start)
            if ct_end > ct_start and ct_end - ct_start > 100:
                content_topp = raw[ct_start:ct_end]
            else:
                content_topp = viewbox
        else:
            content_topp = viewbox
        
        # Use the longest content
        best = viewbox if len(viewbox) > len(content_topp) else content_topp
        if len(best) < 50:
            best = meta_desc
        
        # Clean HTML
        text = re.sub(r'<style[^>]*>.*?</style>', '', best, flags=re.DOTALL)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html_mod.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        results[did] = {
            "name": name,
            "path": path,
            "title": title,
            "content_len": len(text),
            "content": text[:8000],
            "meta_desc": meta_desc[:500] if meta_desc else ""
        }
        print(f"OK did={did} | {name} | title='{title}' | len={len(text)} | meta={len(meta_desc)}")
    except Exception as e:
        results[did] = {"name": name, "path": path, "title": "ERROR", "content_len": 0, "content": str(e), "meta_desc": ""}
        print(f"FAIL did={did} | {name} | ERROR: {e}")
    time.sleep(0.3)

with open("/tmp/fr10_func_docs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nTotal: {len(results)} docs fetched")
