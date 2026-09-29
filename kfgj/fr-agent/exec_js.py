#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exec_js.py - run a .js file through fr-agent /exec (localhost:19000)

Usage:
    python exec_js.py <script.js>
    echo '<js>' | python exec_js.py -

Read-only helper: sends the JS source to the Nashorn exec endpoint and prints
the raw JSON response. Used to probe Designer runtime state without GUI.
"""
import json
import sys
import urllib.request

EXEC_URL = "http://localhost:19000/exec"
TIMEOUT = 30


def run(script):
    payload = json.dumps({"script": script}).encode("utf-8")
    req = urllib.request.Request(
        EXEC_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return raw


def main():
    if len(sys.argv) < 2:
        print("usage: python exec_js.py <script.js|->")
        return 2
    arg = sys.argv[1]
    if arg == "-":
        script = sys.stdin.read()
    else:
        with open(arg, "r", encoding="utf-8") as f:
            script = f.read()
    try:
        raw = run(script)
    except Exception as e:
        print("REQUEST FAILED: %s" % e)
        return 1
    # Pretty print if JSON
    try:
        obj = json.loads(raw)
    except Exception:
        print(raw)
        return 0
    if isinstance(obj, dict) and "result" in obj:
        print(obj["result"])
        if obj.get("status") != "ok":
            print("[status=%s type=%s]" % (obj.get("status"), obj.get("type")))
    else:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
