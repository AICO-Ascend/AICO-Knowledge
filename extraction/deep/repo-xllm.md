# 代码仓卡片 · xllm

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/xLLM-AI/xllm.git |
| 分支 / HEAD | `main` @ `9d471fd9e0f2` (2026-08-31) |
| 最新 tag | `v0.10.1` |
| 版本候选 |
  - git_tag: `v0.10.1`
| 文件数 / md 文档 / 图片 | 2425 / 170 / 39 |
| 语言分布 | {"C++": 893, "C/C++ hdr": 841, "Python": 184, "Markdown": 170, "CUDA": 37, "YAML": 12, "Shell": 11, "TypeScript": 2, "Rust": 2} |
| 备注 | A high-performance inference engine for LLMs, optimized for diverse AI accelerat |

## 1. 定位 (LLM)

**xLLM = 面向国产 AI 加速器（昇腾 NPU 为主）的高效 LLM 推理框架**（README.md「Overview」：
optimized for Chinese AI accelerators，企业级部署降本增效；京东 JD Co. 开源，Apache 2.0，
2026-07-06 正式捐赠 OpenAtom 基金会）。技术报告 arXiv:2510.14686。
与本知识库的直接关联（README News 逐条可证）：**2026-08-27 day-0 支持 GLM-5.3-Flash**
（部署文档 preview/glm-5.3-flash 分支）— 即 glm53 deck 记录的适配工作的官方仓；
此前 day-0 支持 MiniMax-M3 (2026-06-13)、DeepSeek-V4 (2026-04-24)、GLM-5/4.x 系列；
与 Mooncake 共建混合 KV cache 全局管理（2025-12-05）。

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

- `xllm/`（python 包：模型实现/调度/Worker/cache 管理 — glm5_3_flash.py 等模型文件所在）
- `csrc`+`cmake/`（C++ 核心与算子，ATB/自研 kernel 接入）· `third_party/`（brpc/etcd/spdlog 等依赖）
- `docs/`（170 篇：design 6 + feature 28 — 特性文档体系完整）· `examples/` · `scripts/`
- 工程：`.agents/.claude/.gemini`（三套 Agent 配置）· `cibuild/` · `docker/` · `tests/`
- 服务层分离：xllm-service（独立仓，服务层框架）/ xllm_ops（算子库）/ xllm_atb_layers

| 顶层路径 | 文件数 |
|---|---|
| `AGENTS.md` | 文件 |
| `CLAUDE.md` | 文件 |
| `CMakeLists.txt` | 文件 |
| `LICENSE` | 文件 |
| `MANIFEST.in` | 文件 |
| `README.md` | 文件 |
| `README_zh.md` | 文件 |
| `RELEASE.md` | 文件 |
| `THIRDPARTYNOTICES.md` | 文件 |
| `assets` | 文件 |
| `cibuild` | 文件 |
| `cmake` | 文件 |
| `docker` | 文件 |
| `docs/` | 191 |
| `examples/` | 6 |
| `pyproject.toml` | 文件 |
| `scripts/` | 9 |
| `setup.py` | 文件 |

## 3. 功能逻辑 · 特性地图 (机械层: 28 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| (核心) | 28 | async_schedule、chunked_scheduler、disagg_pd、eplb、flashcomm、global_kvcache、graph_mode、moe_params … |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

特性文档地图（docs/src/content/docs/en/features/，28 篇）：
- **调度**：async_schedule · chunked_scheduler — 异步调度 + chunked prefill 是性能主线
  （glm53 调优第 1/6 级的直接对应物）
- **图模式**：graph_mode（+ design/graph_mode_design.md）— aclgraph 静态图捕获，
  KDA 非幂等状态 snapshot/restore 的承载机制
- **MTP**：mtp.md — 投机解码（deepseek_v32_mtp.py 方案，draft 在 python、调度在 C++）
- **PD 分离**：disagg_pd.md — prefill/decode 分离部署
- **KV cache**：global_kvcache.md — 与 Mooncake 共建的全局 KV cache（offload + prefetch）
- **通信**：flashcomm.md · eplb.md（专家并行负载均衡）· moe_params.md

## 5. 版本与演进

- 最新 tag `v0.10.1`；HEAD 2026-08-31（活跃日更）
- 模型支持节奏（README News）：GLM-4.5/4.6 (2025-12) → GLM-5 (2026-02) → DeepSeek-V4 (2026-04)
  → MiniMax-M3 (2026-06) → **GLM-5.3-Flash (2026-08-27 day-0)**
- 治理：2026-07-06 捐赠 OpenAtom 基金会（从京东项目到基金会托管的演进节点）

  - (无 changelog)

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| doc | 117 |
| feature | 28 |
| readme | 13 |
| design | 6 |
| guide | 2 |
| overview | 2 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/xllm/ (168 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
