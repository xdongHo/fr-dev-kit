import { build } from "esbuild";
import { rm } from "node:fs/promises";

// 打包服务器为单文件 dist/server.mjs（运行期零 node_modules 依赖）。
// 注意：不要清空 dist/（console.html 由 vite 单文件构建落到同目录）。
await rm("dist/server.mjs", { force: true });
await build({
  entryPoints: ["src/server.ts"],
  outfile: "dist/server.mjs",
  bundle: true,
  platform: "node",
  format: "esm",
  target: "node20",
  packages: "bundle",
  sourcemap: false,
  minify: false,
  banner: {
    js: "import { createRequire as __createRequire } from 'module'; const require = __createRequire(import.meta.url);",
  },
  logLevel: "info",
});
