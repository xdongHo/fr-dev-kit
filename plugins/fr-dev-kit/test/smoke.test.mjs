// stdio 协议冒烟：用官方 client SDK 连 dist/server.mjs（与 ZCode 宿主同一路径），
// 打真实套件验证工具行为。运行前需 npm run build:server。
import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport, getDefaultEnvironment } from "@modelcontextprotocol/client/stdio";

const PLUGIN_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SERVER = path.join(PLUGIN_DIR, "dist", "server.mjs");

async function connect(envOverrides = {}) {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [SERVER],
    cwd: PLUGIN_DIR,
    env: { ...getDefaultEnvironment(), ...envOverrides },
  });
  const client = new Client({ name: "smoke-test", version: "0.0.0" });
  await client.connect(transport);
  return { client, transport };
}

function textOf(res) {
  return (res.content ?? []).filter((c) => c.type === "text").map((c) => c.text).join("\n");
}

test("initialize + tools/list 暴露 17 个工具", { timeout: 60000 }, async () => {
  const { client, transport } = await connect();
  try {
    const { tools } = await client.listTools();
    const names = tools.map((t) => t.name).sort();
    assert.equal(tools.length, 17);
    assert.ok(names.includes("kb_query"));
    assert.ok(names.includes("dsl_build"));
    assert.ok(names.includes("read_gate_report"));
  } finally {
    await client.close();
    await transport.close();
  }
});

test("kb_query keyword 命中知识库", { timeout: 120000 }, async () => {
  const { client, transport } = await connect();
  try {
    const res = await client.callTool({ name: "kb_query", arguments: { question: "参数面板 控件", top: 3 } });
    const text = textOf(res);
    assert.equal(res.isError, false);
    assert.match(text, /参数面板|控件/);
    assert.ok(res.structuredContent && res.structuredContent.ok === true);
    assert.match(String(res.structuredContent.command), /query_kb\.py/);
  } finally {
    await client.close();
    await transport.close();
  }
});

test("kb_query 缺 question → isError + 参数说明", { timeout: 60000 }, async () => {
  const { client, transport } = await connect();
  try {
    const res = await client.callTool({ name: "kb_query", arguments: { mode: "keyword" } });
    assert.equal(res.isError, true);
    assert.match(textOf(res), /question/);
  } finally {
    await client.close();
    await transport.close();
  }
});

test("非法 kit_root → 配置指引", { timeout: 60000 }, async () => {
  const { client, transport } = await connect({ FR_DEV_KIT_ROOT: "C:/definitely/not/a/kit" });
  try {
    const res = await client.callTool({ name: "kb_query", arguments: { question: "任意" } });
    assert.equal(res.isError, true);
    assert.match(textOf(res), /kit_root/);
  } finally {
    await client.close();
    await transport.close();
  }
});

test("layout_grid 输出 JSON rects", { timeout: 60000 }, async () => {
  const { client, transport } = await connect();
  try {
    const res = await client.callTool({
      name: "layout_grid",
      arguments: { width: 1280, height: 720, count: 4 },
    });
    const text = textOf(res);
    assert.equal(res.isError, false);
    assert.match(text, /"x"|"rects"|w\b|h\b/);
  } finally {
    await client.close();
    await transport.close();
  }
});

test("kit_selftest 跑通（0/退出 2=WARN 均不算失败）", { timeout: 240000 }, async () => {
  const { client, transport } = await connect();
  try {
    const res = await client.callTool({ name: "kit_selftest", arguments: {} });
    assert.notEqual(res.isError, true);
    const text = textOf(res);
    assert.match(text, /PASS|自检|selftest/i);
  } finally {
    await client.close();
    await transport.close();
  }
});

test("list_gate_reports 与 read_gate_report 闭环", { timeout: 60000 }, async () => {
  const { client, transport } = await connect();
  try {
    const res = await client.callTool({ name: "list_gate_reports", arguments: { limit: 5 } });
    assert.notEqual(res.isError, true);
    const reports = res.structuredContent?.reports ?? [];
    if (reports.length > 0) {
      const one = await client.callTool({ name: "read_gate_report", arguments: { name: reports[0].name } });
      assert.notEqual(one.isError, true);
      assert.ok(textOf(one).length > 0);
    }
    // 越权名拒绝
    const bad = await client.callTool({ name: "read_gate_report", arguments: { name: "../secret.md" } });
    assert.equal(bad.isError, true);
  } finally {
    await client.close();
    await transport.close();
  }
});

test("resources/read 返回控制台 HTML（或构建缺失提示）", { timeout: 60000 }, async () => {
  const { client, transport } = await connect();
  try {
    const res = await client.readResource({ uri: "ui://fr-dev-kit/console.html" });
    const text = (res.contents ?? []).map((c) => c.text ?? "").join("");
    assert.match(text, /fr-dev-kit|console\.html 缺失/);
  } finally {
    await client.close();
    await transport.close();
  }
});
