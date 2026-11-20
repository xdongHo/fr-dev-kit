import { spawn } from "node:child_process";
import path from "node:path";
import type { CallToolResult } from "@modelcontextprotocol/server";
import type { KitEnv } from "./env";

export interface RunResult {
  exit_code: number | null;
  stdout: string;
  stderr: string;
  duration_ms: number;
  timed_out: boolean;
  /** 启动失败原因（python 缺失 / 套件根未配置等）；非 null 时视为 isError */
  spawn_error: string | null;
  command: string;
}

export interface RunOptions {
  /** 套件根相对脚本路径（用 / 分隔） */
  script: string;
  /** 脚本参数 */
  programArgs?: string[];
  /** 毫秒，默认 120000 */
  timeoutMs?: number;
  /** 经 stdin 传给脚本的内容（exec_js.py - 通道） */
  stdin?: string;
  /** 子进程 cwd，缺省套件根 */
  cwd?: string;
}

const STDOUT_CAP = 65536;

export function truncateText(text: string, max = STDOUT_CAP): string {
  if (text.length <= max) return text;
  const head = Math.floor(max * 0.75);
  const tail = max - head;
  return (
    text.slice(0, head) +
    `\n\n[fr-dev-kit] 输出超长（${text.length} 字符）已截断：保留头 ${head} + 尾 ${tail} 字符。\n\n` +
    text.slice(-tail)
  );
}

/** 运行套件 Python 脚本。kit_root 不可用时直接返回带指引的错误结果，不启动进程。 */
export function runPython(env: KitEnv, opts: RunOptions): Promise<RunResult> {
  const started = Date.now();
  const base: RunResult = {
    exit_code: null,
    stdout: "",
    stderr: "",
    duration_ms: 0,
    timed_out: false,
    spawn_error: null,
    command: "",
  };
  if (!env.root) {
    return Promise.resolve({ ...base, spawn_error: env.problem, duration_ms: 0 });
  }
  const cwd = opts.cwd ?? env.root;
  const scriptAbs = path.join(env.root, ...opts.script.split("/"));
  const argv = ["-X", "utf8", scriptAbs, ...(opts.programArgs ?? [])];
  const display = `python -X utf8 ${opts.script} ${(opts.programArgs ?? [])
    .map((a) => (a.length > 60 ? a.slice(0, 57) + "..." : a))
    .join(" ")}`.trimEnd();

  return new Promise<RunResult>((resolve) => {
    const child = spawn(env.python, argv, {
      cwd,
      windowsHide: true,
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env, PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
    });
    const out: Buffer[] = [];
    const err: Buffer[] = [];
    let timedOut = false;
    let spawnError: string | null = null;
    let settled = false;

    const timer = setTimeout(() => {
      timedOut = true;
      if (child.pid != null) {
        if (process.platform === "win32") {
          // /T 连子孙进程一起杀（guard 会再拉子工具）
          spawn("taskkill", ["/pid", String(child.pid), "/T", "/F"], { windowsHide: true });
        } else {
          child.kill("SIGKILL");
        }
      } else child.kill("SIGKILL");
    }, opts.timeoutMs ?? 120000);

    child.stdout.on("data", (c: Buffer) => out.push(c));
    child.stderr.on("data", (c: Buffer) => err.push(c));
    child.on("error", (e: Error) => {
      spawnError = `${e.message}（python_cmd 当前为 "${env.python}"，可在 设置→插件→fr-dev-kit 修改）`;
    });
    child.on("close", (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve({
        exit_code: code,
        stdout: Buffer.concat(out).toString("utf8"),
        stderr: Buffer.concat(err).toString("utf8"),
        duration_ms: Date.now() - started,
        timed_out: timedOut,
        spawn_error: spawnError,
        command: display,
      });
    });

    if (opts.stdin != null) {
      child.stdin.write(opts.stdin, "utf8");
    }
    child.stdin.end();
  });
}

export type ToolOutcome = CallToolResult;

/**
 * RunResult → MCP 工具结果。
 * @param errorCodes 视为失败的退出码集合；缺省 [1]（退出 2 = WARN 通过）。
 *                   verify_sql 例外：G08 语义下 0 行（退出 2）也算不通过。
 */
export function pythonToolResult(r: RunResult, errorCodes: number[] = [1]): ToolOutcome {
  const failed =
    r.spawn_error != null || r.timed_out || errorCodes.includes(r.exit_code ?? -1);

  let text = (r.stdout ?? "").replace(/\r\n/g, "\n").trim();
  const errTail = (r.stderr ?? "").replace(/\r\n/g, "\n").trim();
  if (errTail) text += `${text ? "\n" : ""}[stderr]\n${errTail}`;
  if (r.timed_out) text += `\n[fr-dev-kit] 执行超时（已限制 ${r.duration_ms}ms），子进程已终止。可用更小的参数范围重试。`;
  if (r.spawn_error != null) text = `[fr-dev-kit] ${r.spawn_error}`;

  return {
    content: [{ type: "text", text: truncateText(text) || "(无输出)" }],
    structuredContent: {
      ok: !failed,
      exit_code: r.exit_code,
      duration_ms: r.duration_ms,
      command: r.command,
    },
    isError: failed,
  };
}

/** 直接构造失败结果（参数校验类错误，未起进程） */
export function failOutcome(message: string): ToolOutcome {
  return {
    content: [{ type: "text", text: `[fr-dev-kit] ${message}` }],
    structuredContent: { ok: false, exit_code: null, duration_ms: 0, command: "" },
    isError: true,
  };
}
