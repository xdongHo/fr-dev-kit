// 插件清单结构校验（plugin-creator 的 validate-plugin.mjs 需 zcode CLI，此处做等价静态检查）
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("plugin.json 结构与引用完整", () => {
  const m = JSON.parse(fs.readFileSync(path.join(ROOT, ".zcode-plugin", "plugin.json"), "utf8"));
  for (const k of ["name", "version", "description", "author"]) {
    assert.ok(m[k], `缺字段 ${k}`);
  }
  assert.equal(m.name, path.basename(ROOT), "目录名须与 name 一致");
  assert.match(m.version, /^\d+\.\d+\.\d+$/, "version 三段式");
  assert.ok(m.userConfig?.kit_root, "userConfig 须含 kit_root");
  if (m.skills) assert.ok(fs.existsSync(path.join(ROOT, m.skills)), "skills 目录须存在");
});

test(".mcp.json stdio 声明与产物路径存在且不越出插件根", () => {
  const mc = JSON.parse(fs.readFileSync(path.join(ROOT, ".mcp.json"), "utf8"));
  const servers = Object.entries(mc.mcpServers ?? {});
  assert.ok(servers.length >= 1, "至少一个 mcp server");
  for (const [name, s] of servers) {
    assert.equal(s.type, "stdio", `${name} 须 stdio`);
    assert.equal(typeof s.command, "string", `${name} command 须字符串`);
    const joined = (s.args ?? []).join(" ");
    const rel = joined.replace(/\$\{ZCODE_PLUGIN_ROOT\}/g, "").split(/[\\/]/).filter(Boolean);
    if (rel.length) {
      const target = path.resolve(ROOT, ...rel);
      assert.ok(
        target === ROOT || target.startsWith(ROOT + path.sep),
        `${name} args 路径越出插件根: ${joined}`,
      );
      assert.ok(fs.existsSync(target), `${name} args 引用不存在: ${joined}`);
    }
    assert.equal(s.env?.PYTHONIOENCODING, "utf-8", "子进程须强制 utf-8");
  }
});

test("ui.surfaces 与 mcpServers/资源 URI 对齐", () => {
  const m = JSON.parse(fs.readFileSync(path.join(ROOT, ".zcode-plugin", "plugin.json"), "utf8"));
  const mc = JSON.parse(fs.readFileSync(path.join(ROOT, ".mcp.json"), "utf8"));
  for (const s of m.ui?.surfaces ?? []) {
    for (const k of ["id", "server", "resourceUri", "title"]) assert.ok(s[k], `surface 缺 ${k}`);
    assert.ok(mc.mcpServers?.[s.server], `surface.server 未声明: ${s.server}`);
  }
});

test("marketplace.json 版本与 plugin.json 同步", () => {
  const mp = JSON.parse(fs.readFileSync(path.join(ROOT, "..", "marketplace.json"), "utf8"));
  const m = JSON.parse(fs.readFileSync(path.join(ROOT, ".zcode-plugin", "plugin.json"), "utf8"));
  const entry = (mp.plugins ?? []).find((p) => p.name === m.name);
  assert.ok(entry, "marketplace 缺插件条目");
  assert.equal(entry.version, m.version, "marketplace 与 plugin.json 版本须一致");
});

test("构建产物存在（本地市场安装即目录快照）", () => {
  assert.ok(fs.existsSync(path.join(ROOT, "dist", "server.mjs")), "缺 dist/server.mjs");
  assert.ok(fs.existsSync(path.join(ROOT, "dist", "console.html")), "缺 dist/console.html");
});
