#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-click render: read render.js -> POST to fr-agent -> check output"""
import json, urllib.request, time, os

JS_FILE = r"C:\Users\<你的用户名>\AppData\Local\Temp\fr_injected_render\render.js"
OUTPUT_FILE = r"C:\Users\<你的用户名>\AppData\Local\Temp\fr_injected_render\out.html"

with open(JS_FILE, "r", encoding="utf-8") as f:
    script = f.read()

print(f"Script: {JS_FILE} ({len(script)} chars)")
print(f"POST http://localhost:19000/exec ...")

body = json.dumps({"script": script}).encode("utf-8")
req = urllib.request.Request("http://localhost:19000/exec", data=body,
                            headers={"Content-Type": "application/json"}, method="POST")
start = time.time()
with urllib.request.urlopen(req, timeout=120) as r:
    result = json.loads(r.read().decode("utf-8"))
elapsed = time.time() - start

print(f"\nElapsed: {elapsed*1000:.0f}ms")
print(json.dumps(result, ensure_ascii=False, indent=2))

if os.path.exists(OUTPUT_FILE):
    size = os.path.getsize(OUTPUT_FILE)
    print(f"\nOutput: {OUTPUT_FILE} ({size} bytes)")
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        head = f.read(500)
    print(f"First 500 chars:\n{head}")
else:
    print(f"\nOutput file NOT found: {OUTPUT_FILE}")
