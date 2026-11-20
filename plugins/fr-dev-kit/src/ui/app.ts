// 官方 App 客户端接线（@modelcontextprotocol/ext-apps）。
// 顺序铁律：handler 先注册，再 connect()，避免漏掉早期工具通知/宿主上下文。
import { App } from "@modelcontextprotocol/ext-apps";
import { initConsole, type PanelState, type ToolCall } from "./console";

const CONNECT_TIMEOUT_MS = 4000;

const app = new App({ name: "fr-dev-kit-console", version: "1.0.0" });

// 面板句柄由 main() 创建；handler 先占位再指向它
let panel: ReturnType<typeof initConsole> | null = null;

app.ontoolresult = (result: unknown): void => {
  const r = result as { content?: Array<{ type: string; text?: string }> };
  const text = (r.content ?? [])
    .filter((c) => c.type === "text")
    .map((c) => (c as { text: string }).text)
    .join("\n");
  panel?.onExternalToolResult(text);
};

app.onhostcontextchanged = (ctx: unknown): void => {
  const theme = (ctx as { theme?: string } | null)?.theme ?? "light";
  panel?.applyTheme(theme);
};

async function callTool(name: string, args: Record<string, unknown>): Promise<ToolCall> {
  const res = (await app.callServerTool({ name, arguments: args })) as {
    isError?: boolean;
    content?: Array<{ type: string; text?: string }>;
    structuredContent?: Record<string, unknown>;
  };
  return {
    ok: res.isError !== true,
    isError: res.isError === true,
    text: (res.content ?? [])
      .filter((c) => c.type === "text")
      .map((c) => (c as { text: string }).text)
      .join("\n"),
    structured: res.structuredContent,
  };
}

async function saveState(state: PanelState): Promise<void> {
  // zcode/widgetState 为可选宿主能力；缺失时静默跳过（面板状态不持久化，不影响功能）
  const caps = app.getHostCapabilities() as
    | { experimental?: Record<string, unknown> }
    | null
    | undefined;
  if (!caps?.experimental?.["zcode/widgetState"]) return;
  try {
    await (
      app as unknown as {
        request: (
          p: { method: string; params: Record<string, unknown> },
          schema: { type: "object" },
        ) => Promise<unknown>;
      }
    ).request({ method: "ui/set-widget-state", params: { widgetState: state } }, {
      type: "object",
    });
  } catch {
    // 保存失败不影响交互
  }
}

async function main(): Promise<void> {
  panel = initConsole({ callTool, saveState });

  // connect 可能因非宿主环境（本地直接打开 console.html）挂起或失败 → 超时降级
  let connected = false;
  try {
    connected = await Promise.race([
      app.connect().then(() => true),
      new Promise<boolean>((resolve) => setTimeout(() => resolve(false), CONNECT_TIMEOUT_MS)),
    ]);
  } catch {
    connected = false;
  }

  if (!connected) {
    panel.setConnected("degraded", "未检测到 ZCode 宿主桥接，面板以只读预览运行。");
    return;
  }

  panel.applyTheme((app.getHostContext() as { theme?: string } | null)?.theme ?? "light");
  panel.setConnected("ok");
  const initial = (app.getHostContext() as Record<string, unknown> | null)?.[
    "zcode/widgetState"
  ] as PanelState | undefined;
  panel.restore(initial);
}

void main();
