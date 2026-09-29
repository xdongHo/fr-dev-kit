#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 js 文件内容发到 fr-agent /exec 并打印结果"""
import json
import sys
import urllib.request

js = open(sys.argv[1], encoding="utf-8").read()
req = urllib.request.Request("http://localhost:19000/exec",
                             data=json.dumps({"script": js}).encode("utf-8"),
                             headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=180) as r:
    res = json.loads(r.read().decode("utf-8"))
print(res.get("result") or res.get("error"))
