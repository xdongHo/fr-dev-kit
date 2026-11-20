import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

/** dist/server.mjs → dist/ → 插件根 */
export const PLUGIN_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

/** 版本号跟随插件清单，避免与 plugin.json 脱节 */
export const PLUGIN_VERSION = (() => {
  try {
    const j = JSON.parse(fs.readFileSync(path.join(PLUGIN_ROOT, ".zcode-plugin", "plugin.json"), "utf8"));
    return typeof j.version === "string" ? j.version : "0.0.0";
  } catch {
    return "0.0.0";
  }
})();

export interface KitEnv {
  /** 已解析的套件根目录；null = 不可用 */
  root: string | null;
  /** 不可用时的人读说明（含处置指引） */
  problem: string | null;
  /** Python 命令（默认 PATH 里的 python） */
  python: string;
}

export const KIT_ROOT_UNCONFIGURED =
  "[fr-dev-kit] 套件根目录未配置：请在 ZCode「设置 → 插件 → fr-dev-kit」填写 kit_root" +
  "（FR Dev Kit 仓库根目录，含 AGENTS.md / kfgj / ckzl / jcxt），保存后新开会话生效。";

function looksLikeKitRoot(p: string): boolean {
  return fs.existsSync(path.join(p, "kfgj", "guard.py")) && fs.existsSync(path.join(p, "AGENTS.md"));
}

/** 解析套件环境：user_config 注入的 env 优先，源码仓内直跑时向上回退探测 */
export function kitEnv(): KitEnv {
  const python = (process.env.FR_DEV_KIT_PYTHON ?? "").trim() || "python";
  const configured = (process.env.FR_DEV_KIT_ROOT ?? "").trim();
  if (configured) {
    if (looksLikeKitRoot(configured)) return { root: configured, problem: null, python };
    return {
      root: null,
      problem:
        `[fr-dev-kit] kit_root 指向的目录不像套件根（缺 AGENTS.md 或 kfgj/guard.py）：${configured}。` +
        "请在「设置 → 插件 → fr-dev-kit」修正后新开会话。",
      python,
    };
  }
  // 源码仓直跑回退：plugins/fr-dev-kit → 上溯找仓库根
  let dir = PLUGIN_ROOT;
  for (let i = 0; i < 5; i++) {
    if (looksLikeKitRoot(dir)) return { root: dir, problem: null, python };
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return { root: null, problem: KIT_ROOT_UNCONFIGURED, python };
}
