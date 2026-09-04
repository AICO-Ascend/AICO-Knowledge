# 🕐 知识库编年日志（append-only）

> `## [YYYY-MM-DD] op | detail` 统一前缀，`grep "^## \[" log.md | tail -5` 查最近动态。

## [2026-08-24] lint | 表格全量重扫收口：33 信号表重裁 + deepseek-r1 tab24/26 改 manual-pdf-region 原排版；117 改动+25 新增裁剪 M3 图文联合解读全量重生成（142/142 失败 0）；disk==referenced==1115，0 缺解读

## [2026-08-25] crop | 全量机审 6 轮收敛 95.5% OK (1065/1115) — autofix 4 轮 + ar5iv 13 张 + 19 张 manual-pdf-region 登记

## [2026-08-25] tool | 工具方案最优性分析见 /tmp/tool_analysis.md — 当前 5 段流水线已收敛 Pareto 前沿（95.5% OK），借鉴 ResearchPaper-Analyzer 的 MinerU + 多风格生成器，否决代码级分析

## [2026-09-02] web | 第三知识域 web-extraction 落地 — 5 页试跑全通（vLLM serve CLI 95k 字符全量深读 312 参数 / vllm-ascend 中文快速上手 / Ascend PyTorch 2600 环境变量 22 变量 / CANN 商用 900 + 社区 910beta1 环境变量索引 132 表行）；三级抓取路由（.md 直出 / 服务端渲染 / hiascend SPA→doc_center/source/ 原始内容路由）+ 表格逐字还原 M3 七节深读；版本对照发现：CANN 两版环境变量清单一致（diff 仅锚点 ID）；产物 web_docs/ + web_deep_docs/ + web_index.json + web_moc.md；SKILL.md 沉淀

## [2026-09-04] bookshelf | 知识书架双入口落地 — SHELF.md 142 条目(69/69 论文全覆盖, 技术栈六层主线 L1 Agent→L6 硬件集群) + ascend_infra.md AscendInfra 昇腾专区 193 条目(134 仓 9 族分组+知识对照表+AscendV 引用地图); bookshelf_build.py 从三域注册表幂等生成+死链 lint 0; 发表时间改以 arXiv ID 派生为权威(papers.json date 对 2026-01 批次混入入库日期 34/66); P3 补抓 HCCL 用户指南页(hcclug 真实内链)+达芬奇架构缺口由 agent-skills hardware-architecture 深读关闭

## [2026-09-04] bookshelf v4 | 双入口拆为两体系 — SHELF.md 新增「原始出处」列(论文→arXiv原文/仓文档→gitcode blob 原始位置/网页→原页面, 135 条目 0 死链); AscendInfra 废止 markdown 生成方案, 改为独立手工可视化 HTML(bookshelf/ascend_infra.html): 自绘 AI Core 架构 SVG(910B+950 实测数值)/CANN 分层/算子全景/AscendC 概念卡/知识对照表(概念↔本页锚点↔深读↔仓实现)/9 族仓全景; 79 本地链接+锚点 lint 0 死链; 不含第三方平台名与链接; 修正手写外链 4 处(vllm-ascend→gh_mirrors/vl, catlass/hccl_transfer→xLLM-AI, 950 白皮书 arXiv 无索引不伪造)

## [2026-09-04] bookshelf v5 | 书架表格重构(知识源列直链原始出处/摘要列链萃取总结/其他列归拢) + 横向专题解散归并分层 + 模型卡片改造(结构组件关键词/CalvinXKY 总体模型结构页 6 篇收纳 bookshelf/models/带出处头, 缺失 5 模型空链待生成) + 辅助工具区(自建 MFU 计算器 + 显存&KV cache 计算器在线 HTML + 社区工具收录) + NvidiaInfra 第三入口(货架式, BasicCUDA 收录+GPU 栈论文) + README 三入口卡片化 + 三流水线 SVG(节点可点跳代码, README 降级链接表) + 图谱生长动图 GIF(13 帧按 arXiv 月份回放, render_graph_growth.py)
