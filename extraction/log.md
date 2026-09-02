# 🕐 知识库编年日志（append-only）

> `## [YYYY-MM-DD] op | detail` 统一前缀，`grep "^## \[" log.md | tail -5` 查最近动态。

## [2026-08-24] lint | 表格全量重扫收口：33 信号表重裁 + deepseek-r1 tab24/26 改 manual-pdf-region 原排版；117 改动+25 新增裁剪 M3 图文联合解读全量重生成（142/142 失败 0）；disk==referenced==1115，0 缺解读

## [2026-08-25] crop | 全量机审 6 轮收敛 95.5% OK (1065/1115) — autofix 4 轮 + ar5iv 13 张 + 19 张 manual-pdf-region 登记

## [2026-08-25] tool | 工具方案最优性分析见 /tmp/tool_analysis.md — 当前 5 段流水线已收敛 Pareto 前沿（95.5% OK），借鉴 ResearchPaper-Analyzer 的 MinerU + 多风格生成器，否决代码级分析

## [2026-09-02] web | 第三知识域 web-extraction 落地 — 5 页试跑全通（vLLM serve CLI 95k 字符全量深读 312 参数 / vllm-ascend 中文快速上手 / Ascend PyTorch 2600 环境变量 22 变量 / CANN 商用 900 + 社区 910beta1 环境变量索引 132 表行）；三级抓取路由（.md 直出 / 服务端渲染 / hiascend SPA→doc_center/source/ 原始内容路由）+ 表格逐字还原 M3 七节深读；版本对照发现：CANN 两版环境变量清单一致（diff 仅锚点 ID）；产物 web_docs/ + web_deep_docs/ + web_index.json + web_moc.md；SKILL.md 沉淀
