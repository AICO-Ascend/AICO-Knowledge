# 🔄 源列表同步报告（sync_report.md）

> 生成：2026-08-18 ｜ 源 archive/paper_source_moonlight.bib（BibTeX，69 条）｜ 已有 61 → 70 篇

## ✅ 新增入库（9）

| # | arXiv | 论文 | 页数 |
|---|---|---|---|
| 62 | 2603.20397 | KV CACHE OPTIMIZATION STRATEGIES FOR SCALABLE AND EFFICIENT LLM INFERENCE | 24 |
| 63 | 2510.26692 | KIMI LINEAR: AN EXPRESSIVE, EFFICIENT ATTENTION ARCHITECTURE | 28 |
| 64 | 2502.16982 | MUON IS SCALABLE FOR LLM TRAINING | 19 |
| 65 | 2603.15031 | ATTENTION RESIDUALS | 21 |
| 66 | 2508.02520 | Huawei Cloud Model-as-a-Service on the CloudMatrix384 | 32 |
| 67 | 2405.16444 | CacheBlend: Fast LLM Serving for RAG with Cached Knowledge Fusion | 16 |
| 68 | 2602.24286 | CUDA Agent: Large-Scale Agentic RL for CUDA Kernel Generation | 32 |
| 69 | 2607.07508 | Single-Rollout Asynchronous Optimization for Agentic RL | 14 |
| 70 | 2407.20157 | rLLM: Relational Table Learning with LLMs | 6 |

## ⚠️ 待确认（2）— 网页剪藏碎片，非有效论文，按「绝不猜来源」跳过

- Delivery Note — 截断碎片，arxiv 无 ≥0.8 匹配（阈值正确拦截）。
- Reinforcement learning — 截断/泛化短语，无可信匹配，留空。

> 旧 paper_source_moonlight.md 网页剪藏遗留；改用 .bib 源后不再产生。已确认非论文，不入库。

## 同步踩坑（已进 SKILL.md pitfalls）

1. arxiv title-search URL 改版：旧 &abstracts=hide&size=10 现返回 HTTP 400 → 裸 ?query=...&searchtype=title。结果标题带 <span class="search-hit"> 标签，jaccard 前必须去标签。
2. arxiv PDF 下载 ~17 KB/s（非被墙，HTTP 206 正常）：大文件单篇 5-8 分钟。chunk_download.py 已加 skip-if-valid + 300s deadline。并行 curl 兜底。
3. eprint_formulas.py 是 sync 慢瓶颈：下载 LaTeX e-print tarball 易超时拖死整个 sync（index 更新都没跑到）。解法：index 更新 + extract 从 sync 解耦，eprint 留后台 nohup。
4. 管道缓冲吞日志：python|tee|grep 时 stdout 全缓冲，log 空。诊断时直接重定向无下游管道。
5. Bash 工具里 & 后台会让工具立刻返回，python 被 detach。要后台用 run_in_background:true 或 nohup+日志+pgrep 轮询。

## 🖼️ 待深度解读图候选

新增 9 篇 ~69 张图（extract 已渲染 caption+页码）。架构/流程图候选（夜间 m3_caption.py --save）：
kv-cache(#62) kimi-linear(#63) muon(#64) attention-residuals(#65) huawei-cloudmatrix(#66) cacheblend(#67) cuda-agent(#68) single-rollout(#69) rllm(#70)。

> 8 篇新论文 LaTeX e-print 公式抽取（eprint_formulas.py）后台运行中，完成后下次 extract_phase1 自动并入 formulas.json。
