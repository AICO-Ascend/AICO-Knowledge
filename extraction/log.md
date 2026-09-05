# 🕐 知识库编年日志（append-only）

> `## [YYYY-MM-DD] op | detail` 统一前缀，`grep "^## \[" log.md | tail -5` 查最近动态。

## [2026-08-24] lint | 表格全量重扫收口：33 信号表重裁 + deepseek-r1 tab24/26 改 manual-pdf-region 原排版；117 改动+25 新增裁剪 M3 图文联合解读全量重生成（142/142 失败 0）；disk==referenced==1115，0 缺解读

## [2026-08-25] crop | 全量机审 6 轮收敛 95.5% OK (1065/1115) — autofix 4 轮 + ar5iv 13 张 + 19 张 manual-pdf-region 登记

## [2026-08-25] tool | 工具方案最优性分析见 /tmp/tool_analysis.md — 当前 5 段流水线已收敛 Pareto 前沿（95.5% OK），借鉴 ResearchPaper-Analyzer 的 MinerU + 多风格生成器，否决代码级分析

## [2026-09-02] web | 第三知识域 web-extraction 落地 — 5 页试跑全通（vLLM serve CLI 95k 字符全量深读 312 参数 / vllm-ascend 中文快速上手 / Ascend PyTorch 2600 环境变量 22 变量 / CANN 商用 900 + 社区 910beta1 环境变量索引 132 表行）；三级抓取路由（.md 直出 / 服务端渲染 / hiascend SPA→doc_center/source/ 原始内容路由）+ 表格逐字还原 M3 七节深读；版本对照发现：CANN 两版环境变量清单一致（diff 仅锚点 ID）；产物 web_docs/ + web_deep_docs/ + web_index.json + web_moc.md；SKILL.md 沉淀

## [2026-09-04] bookshelf | 知识书架双入口落地 — SHELF.md 142 条目(69/69 论文全覆盖, 技术栈六层主线 L1 Agent→L6 硬件集群) + ascend_infra.md AscendInfra 昇腾专区 193 条目(134 仓 9 族分组+知识对照表+AscendV 引用地图); bookshelf_build.py 从三域注册表幂等生成+死链 lint 0; 发表时间改以 arXiv ID 派生为权威(papers.json date 对 2026-01 批次混入入库日期 34/66); P3 补抓 HCCL 用户指南页(hcclug 真实内链)+达芬奇架构缺口由 agent-skills hardware-architecture 深读关闭

## [2026-09-04] bookshelf v4 | 双入口拆为两体系 — SHELF.md 新增「原始出处」列(论文→arXiv原文/仓文档→gitcode blob 原始位置/网页→原页面, 135 条目 0 死链); AscendInfra 废止 markdown 生成方案, 改为独立手工可视化 HTML(bookshelf/ascend_infra.html): 自绘 AI Core 架构 SVG(910B+950 实测数值)/CANN 分层/算子全景/AscendC 概念卡/知识对照表(概念↔本页锚点↔深读↔仓实现)/9 族仓全景; 79 本地链接+锚点 lint 0 死链; 不含第三方平台名与链接; 修正手写外链 4 处(vllm-ascend→gh_mirrors/vl, catlass/hccl_transfer→xLLM-AI, 950 白皮书 arXiv 无索引不伪造)

## [2026-09-04] bookshelf v5 | 书架表格重构(知识源列直链原始出处/摘要列链萃取总结/其他列归拢) + 横向专题解散归并分层 + 模型卡片改造(结构组件关键词/InfraTech 式总体模型结构页 6 篇收纳 bookshelf/models/带出处头, 缺失 5 模型空链待生成) + 辅助工具区(自建 MFU 计算器 + 显存&KV cache 计算器在线 HTML + 社区工具收录) + NvidiaInfra 第三入口(货架式, BasicCUDA 收录+GPU 栈论文) + README 三入口卡片化 + 三流水线 SVG(节点可点跳代码, README 降级链接表) + 图谱生长动图 GIF(13 帧按 arXiv 月份回放, render_graph_growth.py)

## [2026-09-05] bookshelf v6 | README 美化(三入口名简化/PNG流水线图(英文标签,本机无CJK字体)/流水线描述分行/删上线日期/二级标题emoji统一/动图width=720提速220ms) + 全仓去除人名字样(模型页出处改 InfraTech 项目名, GitHub 人名 URL 全移除) + 模型结构图 11 张全部本地化(尺寸+JPEG magic 双验) + 5 缺失模型卡用 model-arch 技能生成(DeepSeek-V4-Flash/R1/Kimi-Linear/Qwen2.5-VL/GLM-5.3-Flash: HF config 实时解析→HTML+PNG+README, GLM 复合 config text_config 下钻/V4 全 MoE 补丁/R1 bf16 存储参数估算纠偏 ≈671B) + 摘要列文字改 link + 950 白皮书无 arXiv 原始出处回退内部链修复

## [2026-09-05] bookshelf v6.1 | 工具名去自建区分 + 图谱动图加密(概念页 hub 菱形节点 19 页按 tag 机械映射挂边, 69→88 节点) + README 增量更新节改三类源清单直链表(论文 bib/repos/webs 点击直达) + 删除主题覆盖章节

## [2026-09-05] agents | 双类入口确立 — AGENTS.md 机器消费契约(三铁律/9 注册表字段表/RAG 摄取建议/技能导航/三域产物对照) + README 两类入口分区(人类学习者 3 + AI 系统 4); 全仓审视落地 4 优化: ① papers.json 新增 pub_month 权威字段(arXiv YYMM 机械派生, extract_phase1 写入逻辑固化, 修 34 篇 date 混入入库日期问题) ② wiki_index.py 加三域指引附录(index.md 重生成不再丢仓/网页域入口) ③ git 仓瘦身 855MB→696MB(gc.log 清除+prune, 松散对象 8936→5) ④ extraction/README.md 加双入口指针

## [2026-09-05] docs | "先知道有什么,才知道能问什么"理念融入 — README 两类入口节/书架导语/AGENTS.md 三处

## [2026-09-05] docs | AI 入口措辞修正(明示未内置 RAG 系统+三种使用姿势表: Agent 直读/RAG 自接入/报告取用) + 移除遗留文件 repo-inventory.md/uniinfer_deck_references.md(仅历史文档提及, 无功能依赖)

## [2026-09-05] bookshelf v6.2 | 书架表格升级 — 知识源标题策展级覆盖(vllm serve→vLLM serve CLI 参数手册 等 38 处)/框架类分类修正(训练框架·推理框架)/行按知识分类排序/其他列改摘要列(论文=发表月+原文摘要截两句机械提取·仓=定位+最新tag+更新日期)/原摘要列改深读列/概念页标题美化; 摘要清洗顺序修复(先剥反斜杠再剥序号) + repocard 版本号去重

## [2026-09-05] bookshelf v6.3 | 摘要列重排(🔥⚡→日期→内容)+仓卡标题去括号注释+昇腾注记去重字

## [2026-09-05] bookshelf v7 | 摘要列全中文(deep核心问题首段≤3句)+L2合并单表+MindIE归并推理+低信息量条目下架(14概念页/11骨架仓卡入泊车场)+ascend_infra.md主入口(html转备份)

## [2026-09-05] ascend_infra | 硬件节 AI Core 数据通路改动图(render_ai_core.py): 三路数据流闭环动画+三阶段高亮+风扇, 替换 ASCII 图
