import fs from "node:fs";
import fsp from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/server";
import { registerAppTool } from "@modelcontextprotocol/ext-apps/server";
import { kitEnv } from "./env";
import {
  failOutcome,
  pythonToolResult,
  runPython,
  truncateText,
  type ToolOutcome,
} from "./bridge";

const CONSOLE_URI = "ui://fr-dev-kit/console.html";
const DESIGNER_HINT =
  "（提示：该能力需 FineReport 设计器已注入运行——经 designer.bat 启动，或 python kfgj/fr-agent/inject.py 手动注入；详见 kfgj/fr-agent/README.md）";

/** eval_formula.js 同款逻辑动态生成（公式列表经 JSON.stringify 安全内嵌） */
function buildEvalFormulaScript(formulas: string[]): string {
  const arr = formulas.map((f) => JSON.stringify(f)).join(", ");
  return (
    `(function () {\n` +
    `    var Calculator = Java.type("com.fr.script.Calculator");\n` +
    `    var Primitive = Java.type("com.fr.stable.Primitive");\n` +
    `    var formulas = [${arr}];\n` +
    `    var out = [];\n` +
    `    var calc = Calculator.createCalculator();\n` +
    `    for (var i = 0; i < formulas.length; i++) {\n` +
    `        var f = formulas[i];\n` +
    `        try {\n` +
    `            var v = calc.evalValue(f);\n` +
    `            var state;\n` +
    `            if (v === null) state = "NULL";\n` +
    `            else if (v instanceof Primitive && (v.isError() || v.isErrorValue())) state = "ERROR";\n` +
    `            else state = "OK";\n` +
    `            out.push("[eval_formula] " + f + "  =>  " + state + "  value=" + v);\n` +
    `        } catch (e) {\n` +
    `            out.push("[eval_formula] " + f + "  =>  EXCEPTION: " + e);\n` +
    `        }\n` +
    `    }\n` +
    `    return out.join("\\n");\n` +
    `})();`
  );
}

function kbQueryArgs(a: {
  question?: string;
  mode?: string;
  top?: number;
  full?: boolean;
  page?: string;
  dir?: string;
  view?: string;
}): string[] | string {
  const mode = a.mode ?? "keyword";
  const out: string[] = [];
  switch (mode) {
    case "keyword":
      if (!a.question) return "keyword 模式必须提供 question（检索问题/关键词）";
      out.push(a.question, "--mode", "keyword", "--top", String(a.top ?? 8));
      if (a.full) out.push("--full");
      return out;
    case "tree":
      out.push("--tree");
      if (a.dir) out.push(a.dir);
      return out;
    case "page":
      if (!a.page) return "page 模式必须提供 page（页 id 或文件路径）";
      out.push("--page", a.page);
      if (a.full) out.push("--full");
      return out;
    case "view":
      if (a.view) out.push("--view", a.view);
      else out.push("--views");
      return out;
    case "hot":
    case "cold":
      return [`--${mode}`];
    default:
      return `不认识的 mode：${mode}`;
  }
}

const GATE_REPORT_NAME_RE = /^gate_report_[A-Za-z0-9_.\-]+\.md$/;

function gateReportsDir(): string {
  return path.join(os.homedir(), ".fr_dev_kit", "runs", "gate");
}

export function registerTools(server: McpServer): void {
  const env = kitEnv();

  // ── 1. 知识检索 ────────────────────────────────────────────────

  server.registerTool(
    "kb_query",
    {
      title: "知识库检索",
      description:
        "FR Dev Kit 知识检索（无向量三件套：FTS5 关键词 + 树导航 + 页精读）。典型工作流：" +
        "keyword 命中拿页 id → tree 看目录位置 → page --full 整页精读。命中后只读命中块，不要整文件读。",
      inputSchema: z.object({
        question: z.string().optional().describe("检索问题/关键词（mode=keyword 时必填）"),
        mode: z
          .enum(["keyword", "tree", "page", "view", "hot", "cold"])
          .optional()
          .describe(
            "keyword=关键词检索(默认)；tree=目录树导航(可选 dir 如 ckzl/lc)；" +
            "page=页级精读(需 page，配合 full)；view=视图(可选 view 名，缺省列全部)；hot/cold=冷热快捷",
          ),
        top: z.number().int().min(1).max(30).optional().describe("keyword 命中条数（默认 8）"),
        full: z.boolean().optional().describe("打印命中块/整页全文"),
        page: z.string().optional().describe("页 id 或路径（mode=page 必填）"),
        dir: z.string().optional().describe("目录（mode=tree 可选）"),
        view: z.string().optional().describe("视图名，中文名或 key（mode=view 可选）"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const argv = kbQueryArgs(args);
      if (typeof argv === "string") return failOutcome(argv);
      const r = await runPython(env, { script: "jcxt/js/query_kb.py", programArgs: argv });
      return pythonToolResult(r);
    },
  );

  server.registerTool(
    "part_query",
    {
      title: "工程零件库查询",
      description:
        "com.fr.* 零件/装配关系结构化查询（5M1E 知识库，api_kb.sqlite）。P-xxxx 零件编号与全限定类名不入关键词索引，走本通道。",
      inputSchema: z.object({
        sub: z
          .enum(["part", "methods", "class", "cat", "bom", "route", "mat", "machine", "env", "person", "5m1e", "usage", "echarts", "semantic"])
          .describe(
            "part=按编号/关键字查零件；methods=零件全部方法；class=按全限定类名；cat=按类别；" +
            "bom=装配父子树；route=工艺；mat/machine/env/person/5m1e=5M1E 维度；usage=使用记录；echarts=图表；semantic=语义",
          ),
        arg: z.string().optional().describe("查询参数（编号/关键字/全限定类名/工艺号等）"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const r = await runPython(env, {
        script: "ckzl/zsk/gczsk/query_kb.py",
        programArgs: args.arg ? [args.sub, args.arg] : [args.sub],
      });
      return pythonToolResult(r);
    },
  );

  // ── 2. 闸门与自检 ─────────────────────────────────────────────

  server.registerTool(
    "guard",
    {
      title: "收尾闸门",
      description:
        "任务收尾闸门（不可跳过）。退出码 0=通过 / 1=FAIL 任务未完成 / 2=通过但有 WARN。契约见套件 kfgj/EXEC_CONTRACT.md。",
      inputSchema: z.object({
        task: z.enum(["create", "modify", "format", "error", "kb"]).describe("任务类型"),
        cpt: z.string().optional().describe("产物模板路径（error 任务可缺省）"),
        doc: z.string().optional().describe("kb 任务的知识文件"),
        attest: z.string().optional().describe("过程闸门声明，逗号分隔（如 G08,G09,G11）"),
        draft: z.boolean().optional().describe("草稿模式（过程闸门降 WARN；禁止正式交付）"),
        no_backup: z.boolean().optional().describe("跳过改前备份（连续两次=流程违规）"),
        render: z.boolean().optional().describe("G12 由渲染体检替代人工"),
        roundtrip: z.boolean().optional().describe("G12 roundtrip 替代人工"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const argv: string[] = ["--task", args.task];
      if (args.cpt) argv.push("--cpt", args.cpt);
      if (args.doc) argv.push("--doc", args.doc);
      if (args.attest) argv.push("--attest", args.attest);
      if (args.draft) argv.push("--draft");
      if (args.no_backup) argv.push("--no-backup");
      if (args.render) argv.push("--render");
      if (args.roundtrip) argv.push("--roundtrip");
      const r = await runPython(env, { script: "kfgj/guard.py", programArgs: argv, timeoutMs: 300000 });
      return pythonToolResult(r);
    },
  );

  registerAppTool(
    server,
    "kit_selftest",
    {
      title: "套件自检",
      description:
        "环境/断链/契约同源自检（guard.py --selftest），全 PASS 即就绪。调用后可在控制台面板查看套件状态。",
      inputSchema: z.object({}),
      _meta: { ui: { resourceUri: CONSOLE_URI } },
    },
    async (): Promise<ToolOutcome> => {
      const r = await runPython(env, { script: "kfgj/guard.py", programArgs: ["--selftest"], timeoutMs: 180000 });
      return pythonToolResult(r);
    },
  );

  server.registerTool(
    "list_gate_reports",
    {
      title: "闸门报告列表",
      description: "列出最近的 guard 闸门报告（~/.fr_dev_kit/runs/gate/gate_report_*.md，按时间倒序）。",
      inputSchema: z.object({
        limit: z.number().int().min(1).max(100).optional().describe("最多返回条数（默认 30）"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const limit = args.limit ?? 30;
      const dir = gateReportsDir();
      const reports: { name: string; mtime: string; size: number }[] = [];
      try {
        for (const name of fs.readdirSync(dir)) {
          if (!name.startsWith("gate_report_") || !name.endsWith(".md")) continue;
          const st = fs.statSync(path.join(dir, name));
          reports.push({ name, mtime: new Date(st.mtimeMs).toISOString(), size: st.size });
        }
        reports.sort((a, b) => b.mtime.localeCompare(a.mtime));
      } catch {
        // 目录不存在 = 空列表
      }
      const top = reports.slice(0, limit);
      const text = top.length
        ? top.map((e, i) => `${i + 1}. ${e.name}  (${(e.size / 1024).toFixed(1)}KB, ${e.mtime})`).join("\n")
        : "(暂无闸门报告；guard 收尾后生成于 ~/.fr_dev_kit/runs/gate/)";
      return {
        content: [{ type: "text", text }],
        structuredContent: { ok: true, count: top.length, dir, reports: top },
        isError: false,
      };
    },
  );

  server.registerTool(
    "read_gate_report",
    {
      title: "读闸门报告",
      description: "读取单份闸门报告全文（name 来自 list_gate_reports）。",
      inputSchema: z.object({
        name: z.string().describe("报告文件名（gate_report_*.md）"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      if (!GATE_REPORT_NAME_RE.test(args.name) || args.name.includes("..")) {
        return failOutcome(`非法报告名：${args.name}（只接受 gate_report_*.md 基名）`);
      }
      try {
        const text = await fsp.readFile(path.join(gateReportsDir(), args.name), "utf8");
        return {
          content: [{ type: "text", text: truncateText(text, 131072) }],
          structuredContent: { ok: true, name: args.name, size: text.length },
          isError: false,
        };
      } catch (e) {
        return failOutcome(`读取失败：${args.name}（${(e as Error).message}）；可先 list_gate_reports 查看现有报告`);
      }
    },
  );

  // ── 3. 模板校验与备份 ─────────────────────────────────────────

  server.registerTool(
    "fr_check",
    {
      title: "模板三层检测",
      description:
        "模板快速自检：离线 XML → HTTP(--online) → 浏览器 JS(--browser)。退出码 0=无错 / 1=有错 / 2=仅警告。部署前用 --online 全检。",
      inputSchema: z.object({
        cpt: z.string().describe("模板文件路径（.cpt/.frm）"),
        online: z.boolean().optional().describe("HTTP 层检测（部署前）"),
        browser: z.boolean().optional().describe("浏览器 JS 层检测"),
        verbose: z.boolean().optional().describe("详细输出"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const argv = [args.cpt];
      if (args.online) argv.push("--online");
      if (args.browser) argv.push("--browser");
      if (args.verbose) argv.push("--verbose");
      const r = await runPython(env, { script: "kfgj/fzpy/fr_check.py", programArgs: argv, timeoutMs: 180000 });
      return pythonToolResult(r);
    },
  );

  server.registerTool(
    "template_snapshot",
    {
      title: "模板结构快照",
      description:
        "模板结构快照（JSON：数据集/参数/图表/KPI）。缺省 file 时经设计器 /exec 取当前打开模板（需已注入）。--save 存档到 ~/.fr_dev_kit/snapshot/。",
      inputSchema: z.object({
        file: z.string().optional().describe("模板路径；缺省取设计器当前打开的模板"),
        save: z.boolean().optional().describe("快照存档"),
        fields: z.boolean().optional().describe("增强：探查数据集字段+样例数据（DWS）"),
        max_fields: z.number().int().min(1).max(50).optional().describe("fields 最多探查数据集数（默认 5）"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const argv: string[] = args.file ? [args.file] : [];
      argv.push("--json");
      if (args.save) argv.push("--save");
      if (args.fields) argv.push("--fields");
      if (args.max_fields != null) argv.push("--max-fields", String(args.max_fields));
      const r = await runPython(env, { script: "kfgj/fzpy/template_snapshot.py", programArgs: argv, timeoutMs: 120000 });
      return pythonToolResult(r);
    },
  );

  server.registerTool(
    "backup_template",
    {
      title: "模板备份",
      description: "改模板前先备份（G04 铁律）。备份落 ~/.fr_dev_kit/backup/<模板>/<时间戳>/；--list 查看，--prune 清理。",
      inputSchema: z.object({
        files: z.array(z.string()).min(1).describe("要备份的模板文件（可多个）"),
        note: z.string().optional().describe("备注（写入 _note.txt）"),
        list: z.boolean().optional().describe("列出备份（此时 files 可传模板名过滤）"),
        prune: z.boolean().optional().describe("清理旧备份（配合 keep）"),
        keep: z.number().int().min(1).max(200).optional().describe("每模板保留份数（默认 20）"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const argv: string[] = [...args.files];
      if (args.note) argv.push("-m", args.note);
      if (args.list) argv.push("--list");
      if (args.prune) argv.push("--prune");
      if (args.keep != null) argv.push("--keep", String(args.keep));
      const r = await runPython(env, { script: "kfgj/fzpy/backup_template.py", programArgs: argv, timeoutMs: 120000 });
      return pythonToolResult(r);
    },
  );

  // ── 4. 数据与布局 ─────────────────────────────────────────────

  server.registerTool(
    "db_schema",
    {
      title: "表结构探查",
      description:
        "写数据集 SQL 前先探表结构（G11 铁律）。JSON 输出。默认连接 DWS；表名 schema.table。",
      inputSchema: z.object({
        table: z.string().optional().describe("表名（schema.table；缺省 demo_ads）"),
        tables: z.boolean().optional().describe("列出连接所有表（默认仅 demo_ads schema）"),
        all_schema: z.boolean().optional().describe("tables 时列出所有 schema（可能权限受限）"),
        search: z.string().optional().describe("按关键字模糊搜表"),
        sql: z.string().optional().describe("任意 SQL 探查字段"),
        sample: z.boolean().optional().describe("附带前 3 行样例数据"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const argv: string[] = args.table ? [args.table] : [];
      if (args.tables) argv.push("--tables");
      if (args.all_schema) argv.push("--all-schema");
      if (args.search) argv.push("--search", args.search);
      if (args.sql) argv.push("--sql", args.sql);
      if (args.sample) argv.push("--sample");
      argv.push("--json");
      const r = await runPython(env, { script: "kfgj/fzpy/db_schema.py", programArgs: argv, timeoutMs: 300000 });
      return pythonToolResult(r);
    },
  );

  server.registerTool(
    "verify_sql",
    {
      title: "SQL 验证",
      description:
        "新数据集 SQL 必须过验证（G08 铁律）：宏替换后真库执行。退出码 0=成功 / 1=执行失败 / 2=0 行（0 行视为不通过，重试≤3）。重试换参数前先想清楚过滤条件。",
      inputSchema: z.object({
        sql: z.string().optional().describe("SQL 字符串（与 sql_file 二选一）"),
        sql_file: z.string().optional().describe("SQL 文件路径"),
        params: z.record(z.string(), z.string()).optional().describe("参数静态值 {参数名: 值}"),
        conn: z.string().optional().describe("连接名（默认 DWS）"),
        limit: z.number().int().min(1).max(100).optional().describe("显示行数（默认 5）"),
        dry: z.boolean().optional().describe("只替换宏不执行"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const argv: string[] = [];
      if (args.sql) argv.push("-s", args.sql);
      if (args.sql_file) argv.push(args.sql_file);
      for (const [k, v] of Object.entries(args.params ?? {})) argv.push("-p", `${k}=${v}`);
      if (args.conn) argv.push("--conn", args.conn);
      if (args.limit != null) argv.push("--limit", String(args.limit));
      if (args.dry) argv.push("--dry");
      const r = await runPython(env, { script: "kfgj/fzpy/verify_sql.py", programArgs: argv, timeoutMs: 300000 });
      // G08：执行失败(1) 与 0 行(2) 都算不通过
      return pythonToolResult(r, [1, 2]);
    },
  );

  server.registerTool(
    "layout_grid",
    {
      title: "多组件布局计算",
      description:
        "多组件布局坐标计算（铁律：勿手算坐标）。默认输出 JSON rects；rect=true 输出 FR BoundsWidget Java 构造代码。",
      inputSchema: z.object({
        width: z.number().int().min(100).max(20000).describe("画布宽 px"),
        height: z.number().int().min(100).max(20000).describe("画布高 px"),
        count: z.number().int().min(1).max(60).describe("组件数量"),
        span: z.string().optional().describe("重点组件占格，逗号分隔（如 2,1,1,1,1,2）"),
        row: z.boolean().optional().describe("单行模式（参数面板按钮/横排控件）"),
        gap: z.number().min(0).optional().describe("格间距（默认 0 无缝）"),
        margin: z.number().min(0).optional().describe("画布边距（默认 0）"),
        names: z.array(z.string()).optional().describe("组件名（配合 rect，按序对应）"),
        rect: z.boolean().optional().describe("输出 FR BoundsWidget Java 代码"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const argv = ["-W", String(args.width), "-H", String(args.height), "-n", String(args.count)];
      if (args.span) argv.push("--span", args.span);
      if (args.row) argv.push("--row");
      if (args.gap != null) argv.push("--gap", String(args.gap));
      if (args.margin != null) argv.push("--margin", String(args.margin));
      if (args.names?.length) argv.push("--names", args.names.join(","));
      if (args.rect) argv.push("--rect");
      else argv.push("--json");
      const r = await runPython(env, { script: "kfgj/fzpy/layout_grid.py", programArgs: argv, timeoutMs: 30000 });
      return pythonToolResult(r);
    },
  );

  // ── 5. 设计器代理（需注入） ───────────────────────────────────

  server.registerTool(
    "eval_formula",
    {
      title: "公式引擎验证",
      description:
        "新公式写入模板前用 FR Calculator 引擎实际求值（G09 铁律），三态判定 OK/NULL/ERROR。需设计器已注入（19000 /exec）。",
      inputSchema: z.object({
        formulas: z.array(z.string()).min(1).max(20).describe("待验证公式列表"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const r = await runPython(env, {
        script: "kfgj/fr-agent/exec_js.py",
        programArgs: ["-"],
        stdin: buildEvalFormulaScript(args.formulas),
        timeoutMs: 90000,
      });
      const outcome = pythonToolResult(r);
      if (outcome.isError && outcome.content[0] && outcome.content[0].type === "text") {
        outcome.content[0].text += `\n${DESIGNER_HINT}`;
      }
      return outcome;
    },
  );

  server.registerTool(
    "designer_status",
    {
      title: "设计器状态",
      description: "FineReport 设计器存活与当前状态（18999 ping + status：事件数/Recording/当前工作簿）。需设计器已注入。",
      inputSchema: z.object({}),
    },
    async (): Promise<ToolOutcome> => {
      const ping = await runPython(env, {
        script: "kfgj/fr-agent/fr_agent_client.py",
        programArgs: ["ping"],
        timeoutMs: 10000,
      });
      if (ping.spawn_error || (ping.exit_code ?? -1) !== 0) {
        const outcome = pythonToolResult(ping);
        const idx = outcome.content.findIndex((c) => c.type === "text");
        if (idx >= 0) (outcome.content[idx] as { text: string }).text += `\n${DESIGNER_HINT}`;
        return outcome;
      }
      const status = await runPython(env, {
        script: "kfgj/fr-agent/fr_agent_client.py",
        programArgs: ["status"],
        timeoutMs: 15000,
      });
      const text =
        `[ping]\n${ping.stdout.trim()}\n\n[status]\n${status.stdout.trim()}` +
        (status.stderr.trim() ? `\n[stderr]\n${status.stderr.trim()}` : "");
      return {
        content: [{ type: "text", text: truncateText(text) }],
        structuredContent: {
          ok: true,
          exit_code: status.exit_code,
          duration_ms: ping.duration_ms + status.duration_ms,
          command: "fr_agent_client ping + status",
        },
        isError: false,
      };
    },
  );

  server.registerTool(
    "designer_exec_js",
    {
      title: "设计器 JS 执行（高危）",
      description:
        "向设计器 JVM 投递 Nashorn JS（19000 /exec），可反射调用 FR 类做探查/验证。高危：仅用于只读探查或已备份后的验证，返回值需 return 字符串。需设计器已注入。",
      inputSchema: z.object({
        script: z.string().min(1).describe("Nashorn JS 脚本（IIFE，return 结果字符串）"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const r = await runPython(env, {
        script: "kfgj/fr-agent/exec_js.py",
        programArgs: ["-"],
        stdin: args.script,
        timeoutMs: 90000,
      });
      const outcome = pythonToolResult(r);
      if (outcome.isError && outcome.content[0] && outcome.content[0].type === "text") {
        outcome.content[0].text += `\n${DESIGNER_HINT}`;
      }
      return outcome;
    },
  );

  // ── 6. DSL 标准生成器（R29 首批 tools） ───────────────────────

  server.registerTool(
    "dsl_build",
    {
      title: "DSL 标准生成器",
      description:
        "spec（JSON）→ 标准 FR XML 组件：dataset=数据集（numeric/ORG+PERM/period CASE 自动织入）、panel=参数面板（para_* 铁律/165px 栅格）、" +
        "chart=图表（改写在库设计器模板，22 型）。内建 guardrails，未过即 SkillError 不出坏产物。spec 契约见套件 kfgj/dsl/skills/README.md。",
      inputSchema: z.object({
        kind: z.enum(["dataset", "panel", "chart"]).describe("生成器类型"),
        spec: z.record(z.string(), z.unknown()).describe("spec 契约（JSON 对象，契约见 dsl/skills/README.md）"),
        out: z.string().min(1).describe("输出 cpt 路径（相对路径相对套件根；建议绝对路径放项目产物目录）"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const script = `kfgj/dsl/skills/${args.kind}_skill.py`;
      const r = await runPython(env, {
        script,
        programArgs: [JSON.stringify(args.spec), args.out],
        timeoutMs: 120000,
      });
      return pythonToolResult(r);
    },
  );

  server.registerTool(
    "dsl_types",
    {
      title: "图表生成器支持清单",
      description: "chart_skill 支持的 22 型图表清单（types）或暂不支持清单及原因（unsupported）。",
      inputSchema: z.object({
        which: z.enum(["types", "unsupported"]).optional().describe("默认 types"),
      }),
    },
    async (args): Promise<ToolOutcome> => {
      const r = await runPython(env, {
        script: "kfgj/dsl/skills/chart_skill.py",
        programArgs: [args.which === "unsupported" ? "--unsupported" : "--types"],
        timeoutMs: 30000,
      });
      return pythonToolResult(r);
    },
  );
}
