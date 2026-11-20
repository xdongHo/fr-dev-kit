import fs from "node:fs/promises";
import path from "node:path";
import { McpServer } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import { registerAppResource, RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";
import { PLUGIN_ROOT, PLUGIN_VERSION } from "./env";
import { registerTools } from "./tools";

const CONSOLE_URI = "ui://fr-dev-kit/console.html";

async function main(): Promise<void> {
  const server = new McpServer({ name: "fr-dev-kit", version: PLUGIN_VERSION });

  registerTools(server);

  // 控制台面板（单文件 HTML 由 vite-plugin-singlefile 产出到 dist/console.html）
  registerAppResource(
    server,
    "FR Dev Kit 控制台",
    CONSOLE_URI,
    { description: "套件自检状态、最近闸门报告、知识检索工作台", mimeType: RESOURCE_MIME_TYPE },
    async () => {
      let html: string;
      try {
        html = await fs.readFile(path.join(PLUGIN_ROOT, "dist", "console.html"), "utf8");
      } catch {
        html =
          "<!doctype html><html><body style=\"font-family:system-ui;padding:24px\">" +
          "<h1>fr-dev-kit 控制台</h1><p>console.html 缺失：请在插件源码目录执行 <code>npm run build</code> 重建。</p></body></html>";
      }
      return { contents: [{ uri: CONSOLE_URI, mimeType: RESOURCE_MIME_TYPE, text: html }] };
    },
  );

  await server.connect(new StdioServerTransport());
}

main().catch((err: unknown) => {
  console.error("[fr-dev-kit] server fatal:", err);
  process.exit(1);
});
