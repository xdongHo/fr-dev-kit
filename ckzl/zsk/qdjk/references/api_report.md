<!--
KB_INDEX: {
  "title": "帆软 FR 10.0 填报开发核心 JS API 清单（总导航）",
  "stage": "frontend",
  "tags": [
    "JS API",
    "填报",
    "导航"
  ],
  "keywords": [
    "FR.WritePane",
    "FR.Msg",
    "WLGP",
    "导航",
    "拆分"
  ],
  "summary": "FR 10.0 填报核心 JS API 总导航（原 653 行单文件 2026-09-29 拆分为 2 页）：弹窗与填报面板（Msg/Dialog/Window/WritePane，原 §1-§3）/ 报表面板与填报接口（Elementcase/PagePane/WLGP/Write/WriteEditor+附录，原 §4-§8）"
}
-->

# 帆软 FR 10.0 填报开发核心 JS API 清单（总导航）

> 本文件原为整篇单文件，2026-09-29 知识库治理时按章节拆分为多页（单页 ≤400 行，各页带 KB_INDEX 头）。
> 原路径保留本导航页防断链；内容未删除，按下方索引跳转。

| 分页 | 内容 |
|------|------|
| [FR填报JS API：消息弹窗/对话框/填报面板（FR.Msg/Dialog/Window/WritePane）](api_report_1_弹窗与填报面板.md) | FR 10.0 填报核心 JS API 第 1/2 页：FR.Msg（confirm/alert/prompt/toast 4 静态方法）、FR.Dialog 与 FR.Window（对话框属性/方法）、FR.WritePane 填报面板（1 属性 + 41 方法：提交/校验/单元格取值赋值等）——原 api_report.md §1-§3 |
| [FR填报JS API：报表面板与填报接口（Elementcase/PagePane/WLGP/Write/WriteEditor）](api_report_2_报表面板与填报接口.md) | FR 10.0 填报核心 JS API 第 2/2 页：FR.Elementcase 报表内容基类（31 方法）、FR.PagePane 分页预览（33 方法）、FR.WLGP 填报逻辑页面（getTDCell 等 19 方法）、FR.Write 填报控件管理（21 方法）、FR.WriteEditor 填报编辑器接口（36 方法）+ 通用基类方法速查附录——原 api_report.md §4-§8+附录 |


## 原章节 → 分页映射

| 原章节（§） | 现位置 |
|---|---|
| §1 FR.Msg | [api_report_1_弹窗与填报面板.md](api_report_1_弹窗与填报面板.md) |
| §2 FR.Dialog / FR.Window | [api_report_1_弹窗与填报面板.md](api_report_1_弹窗与填报面板.md) |
| §3 FR.WritePane | [api_report_1_弹窗与填报面板.md](api_report_1_弹窗与填报面板.md) |
| §4 FR.Elementcase | [api_report_2_报表面板与填报接口.md](api_report_2_报表面板与填报接口.md) |
| §5 FR.PagePane | [api_report_2_报表面板与填报接口.md](api_report_2_报表面板与填报接口.md) |
| §6 FR.WLGP | [api_report_2_报表面板与填报接口.md](api_report_2_报表面板与填报接口.md) |
| §7 FR.Write | [api_report_2_报表面板与填报接口.md](api_report_2_报表面板与填报接口.md) |
| §8 FR.WriteEditor | [api_report_2_报表面板与填报接口.md](api_report_2_报表面板与填报接口.md) |
| 附录 通用基类方法速查 | [api_report_2_报表面板与填报接口.md](api_report_2_报表面板与填报接口.md) |
