// 控制台面板逻辑（DOM 渲染 + 工具调用编排）。宿主接线在 app.ts（官方 App 客户端）。

export interface ToolCall {
  ok: boolean;
  isError: boolean;
  text: string;
  structured?: Record<string, unknown>;
}

export interface PanelDeps {
  /** 经官方 App 客户端调用本插件 server 的工具 */
  callTool(name: string, args: Record<string, unknown>): Promise<ToolCall>;
  /** 保存会话面板状态（宿主内存，视图重挂载存活；缺能力时由 app.ts 决定不调用） */
  saveState(state: PanelState): void;
}

export interface PanelState {
  selectedReport?: string;
  lastQuery?: string;
}

export interface PanelApi {
  applyTheme(theme: string): void;
  setConnected(mode: "ok" | "degraded", detail?: string): void;
  restore(state: PanelState | undefined): void;
  /** 模型侧调用带 _meta.ui 工具时，宿主把结果推给页面（ontoolresult） */
  onExternalToolResult(text: string): void;
}

function el<T extends HTMLElement>(id: string): T {
  const e = document.getElementById(id);
  if (!e) throw new Error(`#${id} missing`);
  return e as T;
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c] as string,
  );
}

/** 轻量 markdown 渲染（标题/加粗/行内码/列表/分隔线/PASS-FAIL 着色），先转义再替换 */
export function renderMarkdown(src: string): string {
  const lines = escapeHtml(src.replace(/\r\n/g, "\n")).split("\n");
  const out: string[] = [];
  let inList = false;
  const inline = (s: string): string =>
    s
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\[(PASS|通过)\]/g, '<span class="pass">[$1]</span>')
      .replace(/\[(FAIL|未通过)\]/g, '<span class="fail">[$1]</span>')
      .replace(/\[(WARN|SKIP)\]/g, '<span class="warn">[$1]</span>');
  for (const raw of lines) {
    const line = raw.trimEnd();
    const liMatch = /^(\s*)[-*] /.exec(line);
    if (liMatch) {
      if (!inList) {
        out.push("<ul>");
        inList = true;
      }
      out.push(`<li>${inline(line.slice(liMatch[0].length))}</li>`);
      continue;
    }
    if (inList) {
      out.push("</ul>");
      inList = false;
    }
    const h = /^(#{1,4})\s+(.*)$/.exec(line);
    if (h) {
      const level = Math.min(h[1].length + 1, 4);
      out.push(`<h${level}>${inline(h[2])}</h${level}>`);
    } else if (/^\s*(-{3,}|={3,})\s*$/.test(line)) {
      out.push("<hr/>");
    } else if (line === "") {
      out.push("");
    } else {
      out.push(`<p>${inline(line)}</p>`);
    }
  }
  if (inList) out.push("</ul>");
  return out.join("\n");
}

interface ReportEntry {
  name: string;
  mtime: string;
  size: number;
}

export function initConsole(deps: PanelDeps): PanelApi {
  const light = el<HTMLSpanElement>("statusLight");
  const kitRootEl = el<HTMLSpanElement>("kitRoot");
  const connBadge = el<HTMLSpanElement>("connBadge");
  const reportList = el<HTMLUListElement>("reportList");
  const reportView = el<HTMLElement>("reportView");
  const searchForm = el<HTMLFormElement>("searchForm");
  const questionInput = el<HTMLInputElement>("question");
  const pageInput = el<HTMLInputElement>("pageInput");
  const pageBtn = el<HTMLButtonElement>("pageBtn");
  const searchBtn = el<HTMLButtonElement>("searchBtn");
  const searchResult = el<HTMLElement>("searchResult");
  const lastToolBox = el<HTMLDetailsElement>("lastToolBox");
  const lastToolText = el<HTMLPreElement>("lastToolText");
  const hintbar = el<HTMLElement>("hintbar");

  let selectedReport: string | null = null;
  let degraded = false;

  const state = (): PanelState => ({
    selectedReport: selectedReport ?? undefined,
    lastQuery: questionInput.value || undefined,
  });
  const persist = () => deps.saveState(state());

  function setResult(html: string): void {
    searchResult.innerHTML = html;
  }

  function showTextResult(title: string, call: ToolCall): void {
    const cls = call.isError ? "fail" : "";
    setResult(
      `<p class="${cls}"><strong>${escapeHtml(title)}</strong>${call.isError ? "（失败）" : ""}</p>` +
      `<pre>${escapeHtml(call.text)}</pre>`,
    );
  }

  // ── 套件自检（状态灯） ───────────────────────────────────────
  async function runSelftest(): Promise<void> {
    if (degraded) {
      light.className = "light unknown";
      kitRootEl.textContent = "独立预览模式";
      return;
    }
    light.className = "light unknown";
    kitRootEl.textContent = "自检中…";
    const call = await deps.callTool("kit_selftest", {});
    const text = call.text;
    if (call.isError) {
      light.className = "light fail";
      light.title = "自检失败";
      kitRootEl.textContent = "自检失败";
      reportView.classList.remove("hidden");
      reportView.innerHTML = renderMarkdown(text);
      return;
    }
    const failMatch = /FAIL\s*(\d+)?/i.exec(text);
    const passAll = /全 ?PASS|全部 ?PASS/i.test(text) || (!/FAIL/i.test(text) && /PASS/i.test(text));
    light.className = `light ${passAll && !failMatch ? "ok" : failMatch ? "fail" : "unknown"}`;
    light.title = passAll && !failMatch ? "自检通过" : "自检存在问题项";
    const m = /KIT_ROOT[=：:]\s*(\S+)/i.exec(text);
    kitRootEl.textContent = m ? m[1] : "套件自检完成";
    hintbar.textContent = "自检报告全文可在模型侧调用 kit_selftest 查看；环境详情见 kfgj/env.md。";
  }

  // ── 闸门报告 ─────────────────────────────────────────────────
  async function loadReports(): Promise<void> {
    if (degraded) return;
    const call = await deps.callTool("list_gate_reports", { limit: 30 });
    if (call.isError) {
      reportList.innerHTML = `<li class="muted">${escapeHtml(call.text)}</li>`;
      return;
    }
    const reports = ((call.structured?.reports as ReportEntry[]) ?? []).slice(0, 20);
    if (!reports.length) {
      reportList.innerHTML = '<li class="muted">（暂无闸门报告）</li>';
      return;
    }
    reportList.innerHTML = "";
    for (const r of reports) {
      const li = document.createElement("li");
      li.innerHTML =
        `<span class="rname">${escapeHtml(r.name)}</span>` +
        `<span class="rdate">${escapeHtml(r.mtime.slice(0, 16).replace("T", " "))}</span>`;
      li.addEventListener("click", () => void selectReport(r.name));
      reportList.appendChild(li);
    }
  }

  async function selectReport(name: string): Promise<void> {
    selectedReport = name;
    for (const li of reportList.children) {
      (li as HTMLElement).classList.toggle(
        "active",
        (li.querySelector(".rname") as HTMLElement)?.textContent === name,
      );
    }
    persist();
    reportView.classList.remove("hidden");
    reportView.innerHTML = '<p class="muted">读取中…</p>';
    const call = await deps.callTool("read_gate_report", { name });
    reportView.innerHTML = call.isError
      ? `<p class="fail">${escapeHtml(call.text)}</p>`
      : renderMarkdown(call.text);
  }

  // ── 知识检索 ─────────────────────────────────────────────────
  async function doSearch(): Promise<void> {
    const q = questionInput.value.trim();
    if (!q) return;
    searchBtn.disabled = true;
    setResult('<p class="muted">检索中…</p>');
    try {
      const call = await deps.callTool("kb_query", { question: q, top: 10 });
      showTextResult(`关键词检索：${q}`, call);
      // 命中行里通常带 .md 路径 → 预填精读框
      const md = /[A-Za-z0-9_\/\\.\-\u4e00-\u9fa5]+\.md\b/.exec(call.text);
      if (md) pageInput.value = md[0];
      persist();
    } finally {
      searchBtn.disabled = false;
    }
  }

  async function doPage(): Promise<void> {
    const p = pageInput.value.trim();
    if (!p) return;
    pageBtn.disabled = true;
    setResult('<p class="muted">读取整页…</p>');
    try {
      const call = await deps.callTool("kb_query", { mode: "page", page: p, full: true });
      showTextResult(`整页精读：${p}`, call);
    } finally {
      pageBtn.disabled = false;
    }
  }

  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    void doSearch();
  });
  pageBtn.addEventListener("click", () => void doPage());
  pageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") void doPage();
  });

  return {
    applyTheme(theme: string): void {
      document.documentElement.dataset.theme = theme === "dark" ? "dark" : "light";
    },
    setConnected(mode, detail): void {
      degraded = mode === "degraded";
      connBadge.textContent = degraded ? "独立预览（无宿主）" : "已连接";
      connBadge.className = `badge ${degraded ? "degraded" : "ok"}`;
      if (degraded) {
        light.className = "light unknown";
        light.title = "未连接宿主";
        kitRootEl.textContent = "独立预览模式";
        setResult(
          '<p class="muted">独立预览模式：未连接 ZCode 宿主，工具调用不可用。' +
          "面板正常入口：ZCode 内打开 fr-dev-kit 控制台面板（ui.surfaces），或模型调用 kit_selftest 工具。</p>",
        );
        hintbar.textContent = detail ?? "";
      } else {
        void runSelftest();
        void loadReports();
      }
    },
    restore(s): void {
      if (s?.lastQuery) questionInput.value = s.lastQuery;
      if (s?.selectedReport) void selectReport(s.selectedReport);
    },
    onExternalToolResult(text): void {
      lastToolBox.classList.remove("hidden");
      lastToolBox.open = true;
      lastToolText.textContent = text.slice(0, 20000);
    },
  };
}
