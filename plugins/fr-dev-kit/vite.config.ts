import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const PLUGIN_DIR = path.dirname(fileURLToPath(import.meta.url));

// 面板构建：单文件 HTML（内联 JS/CSS），产出到 dist/（不清空 dist——server.mjs 同目录）。
// INPUT 环境变量指定入口文件名（如 console.html），与官方 quickstart 口径一致。
export default defineConfig(() => {
  const input = process.env.INPUT;
  if (!input) throw new Error("vite.config: 缺少 INPUT 环境变量（如 INPUT=console.html）");
  return {
    root: path.resolve(PLUGIN_DIR, "src/ui"),
    plugins: [viteSingleFile()],
    build: {
      outDir: path.resolve(PLUGIN_DIR, "dist"),
      emptyOutDir: false,
      minify: true,
      rollupOptions: {
        input: { console: path.resolve(PLUGIN_DIR, "src/ui", input) },
      },
    },
  };
});
