# moe_ep Design

> 仓 `flashinfer` · 路径 `docs/design_docs/moe_ep_architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/flashinfer/docs/design_docs/moe_ep_architecture.md

# FlashInfer moe_ep 架构文档深度解读

## 【定位】

本篇文档刻画 FlashInfer 中 **moe_ep (Expert-Parallel MoE)** 的统一架构与可插拔后端矩阵: 围绕「Split (dispatch → inner kernel → combine)」与「Mega (fused comm + MoE kernel)」两条执行路径, 汇总所有可注册的 SM100 / SM90 后端、其量化格式约束、Comm 传输限制, 以及 Mega CuTeDSL 专属的 knob 调优与缓存机制, 为用户提供单点入口 `MoEEpLayer(...)` 与对应配置类的能力全景图。

---

## 【技术要点】

1. **单一入口 + 双形态调度**: `MoEEpLayer(bootstrap, fleet_params, weights, fleet_knobs=(), backend=...)` 在初始化时根据 `backend` 解析为 `MoEEpSplitLayer` 或 `MoEEpMegaLayer`; 后端名通过 config 的 `kernel_name` / `backend_name` 字段从三个注册表 (mega kernels / split kernels / split comm fleets) 解析, 过期别名仍可解析但会告警。
2. **Mega 后端矩阵 (融合 comm + MoE kernel, 输出恒为 BF16 `[num_tokens, hidden]`)**: 通过 `MegaConfig(megakernel=<config>)` 选择, 涵盖 `sm100_nvfp4_nvfp4_bf16_cutedsl`、`sm100_mxfp8_mxfp8_bf16_cutedsl`、`sm100_fp8_fp4_bf16_deepgemm`、`sm90_fp8_fp8_bf16_pull_cutedsl`、`sm90_fp8_fp8_bf16_push_cuda`; SM90 pull-style CuTeDSL 树与 SM100 CuTeDSL 树模块名冲突, 进程内互斥; 权重默认接受 canonical BF16 `MoEWeightPack` 并由 `preprocess_weights` 量化, 也可直传已预量化权重。
3. **Split 后端 = Comm × Kernel 完全解耦**: 通过 `SplitConfig(comm=..., kernel=...)` 组合; Comm 层搬运 token (默认 BF16, 内核后端自行打包), Kernel 层在本 rank 的 expert shard 上计算。Comm 后端含 `nccl_ep` (`NcclEpConfig`, NCCL/nccl4py) 与 `nixl_ep` (`NvepConfig`, NIXL over UCX device API); Kernel 后端含 `identity`、`fused_moe` 配 `TrtllmBf16Config` / `TrtllmFp4Config` / `CuteDslConfig`, 以及独立的 `sm100_mxfp8_mxfp4_bf16_cutedsl`。
4. **硬约束清单**: `nccl_ep` 的 LL device kernel 对 per-token row width 有白名单且 top-k ≤ 8; `nixl_ep` 要求 `BUILD_NIXL_EP=1` (UCX v1.21+ device headers) 与 `BootstrapConfig.tcp_store`, 限制 `max_tokens_per_rank ≤ 1024`、hidden ∈ {2048, 2560, 3072, 4096, 5120, 6144, 7168, 8192}、支持 top-k > 8; `fused_moe` 每个 `MoEConfig` 只能接受恰好一个后端候选; W4A8 split kernel 要求 hidden 与 intermediate 为 128 的倍数。
5. **双调优系统并立**: Split 走通用 FlashInfer `AutoTuner`, 每个 `fused_moe` runner 按 token bucket (上限 `ExecutionConfig.tune_max_num_tokens`) 枚举 tactic, `MoELayer` 再按桶选跨后端 winner; Mega CuTeDSL 走 moe_ep 专属 **knob** 系统 — knob 空间远大于 tactic id, 覆盖 tile / cluster / warp-role / scheduling 等需在 `cute.compile` 期固定的参数, 每次测量都是 collective (kernel 跨所有 EP rank, 候选须在所有 rank 上 lockstep 编译并启动)。
6. **Knob 三态解析 + 缓存机制**: `Sm100_*_Cutedsl_MegaMoeConfig.knobs` 接受 `dict` (按值 pin, 经 `tuner.is_valid` 校验) / `None` (默认, 先查 `FLASHINFER_MOE_EP_KNOB_CACHE`, 命中即纯 dict 查表无 compile / 无 collective, miss 时按 `tuner.default_knobs(max_tokens)` 的 token-count profiles 选择, NVFP4 有 4 档、MXFP8 有 2 档) / `"auto"` (延后到首次 `compute()`, 全 EP rank 同步跑候选 sweep → `cute.compile → barrier → timed launches → barrier → all-reduce(MAX) 取 argmin → rank 0 写回缓存)。Knob 划分为 correctness (必须 pin: `mma_tiler_mnk` / `cluster_shape_mnk` / `token_back_mode` / `load_balance_mode` / `non_ubulk_fc2_store` / `in_kernel_fc2_reduce` — 后者使累加顺序非确定性, 需 `False` 以保 bit-reproducibility) 与 perf (输出中性, 可自由扫描: `group_hint` / `flag_batch` / `epi_flag_batch`); 合法性由 `tuner.is_valid` 镜像 `inference_solver.filter_invalid` 规则。

---

## 【关键机制与数据】

**工作原理 — Knob 解析流程 (Mega CuTeDSL)**:
- 解析时机: symmetric-memory session 创建时; `"auto"` 模式额外在首次 `compute()` 时执行 collective sweep (见原文 mermaid 图)。
- Cache key 维度 (原文): `device, dtype, world_size, geometry, combine_dtype + max_tokens bucket`。
- 候选测量协议: per candidate, on every rank in lockstep → `cute.compile → barrier → timed launches → barrier` → `all-reduce per-candidate time with MAX` (原文: "slowest rank = real collective latency") → argmin winner, 全 rank 一致。
- 默认 token-count profiles (`sm100_nvfp4_nvfp4_bf16_cutedsl`, 4 档, 原文): `< 512` → 小批量延迟档 (128-wide N tile, `token_back_mode="epi_warps"`); `512–1023` → 中档 (`reuse_dispatch_warps`); `1024–2047` → 中大档 (256-wide N tile, `standalone_warps`); `≥ 2048` → 大吞吐档 (`flag_batch=8`, `reuse_dispatch_warps`)。
- 原文点出 pinned knobs 示例: `mma_tiler_mnk=(256, 128, 256)`, `cluster_shape_mnk=(2, 1, 1)`, `token_back_mode="reuse_dispatch_warps"`, `flag_batch=8`, `group_hint=512`, `epi_flag_batch=(2, 4)`, `load_balance_mode="atomic_counter"`, `in_kernel_fc2_reduce=False`。
- 原文点出 `"auto"` 模式: 首次 `compute()` 时跑约 24 个候选的 sweep (`nvfp4_candidates()` — 原文此处截断)。
- 分桶上限 (split AutoTuner): 每个 token bucket 上限 `ExecutionConfig.tune_max_num_tokens`。
- 原文未给出的数据: 性能数值 / 吞吐 / latency 等 benchmark 数字 (TUNING.md 负责)。

---

## 【表格解读】

### 表格 1: 执行模式总览 (原文逐字还原)

| Mode | Flow | When to use |
|------|------|-------------|
| **Split** | dispatch → inner kernel → combine | Pluggable comm + compute; NCCL-EP / NIXL-EP transport |
| **Mega** | fused comm + MoE kernel | Single symmetric-memory kernel; no separate Fleet/Handle |

**逐行解读**: 模式分流的判据在于是否需要「comm 与 compute 的解耦」: Split 提供可插拔的 comm 栈 (NCCL-EP / NIXL-EP) 与 compute 后端的自由组合, 适合需要灵活传输层或多级调度的场景; Mega 把 dispatch、expert 计算、combine 全部沉入单一 symmetric-memory kernel, 免去 Fleet/Handle 这一层间接, 适合追求最低 kernel launch 次数与最低端到端 latency 的推理主路径。

### 表格 2: Mega 后端矩阵 (原文逐字还原)

| Backend (alias) | Activation | Weight | Output | Arch | Tuning |
|---|---|---|---|---|---|
| `sm100_nvfp4_nvfp4_bf16_cutedsl` (`nvfp4_cutedsl`) | NVFP4 (block-16) | NVFP4 (block-16) | BF16 | SM100 family | `knobs=None` → token-count heuristic; `knobs=dict` → pinned; `knobs="auto"` → collective compile+time sweep at first forward (never in serving); winners cacheable via `FLASHINFER_MOE_EP_KNOB_CACHE` |
| `sm100_mxfp8_mxfp8_bf16_cutedsl` (`mxfp8_cutedsl`) | MXFP8 (block-32 UE8M0) | MXFP8 (block-32 UE8M0) | BF16 | SM100 family | same `knobs` surface as the NVFP4 backend |
| `sm100_fp8_fp4_bf16_deepgemm` (`deep_gemm_mega`) | FP8 (E4M3, block-32 UE8M0) | FP4 (int8-packed, block-32) | BF16 | SM100 family | — (DeepGEMM selects its own JIT configs internally) |
| `sm90_fp8_fp8_bf16_pull_cutedsl` (`sm90_pull_fp8`) | FP8 (E4M3/E5M2; per-tensor or DeepGEMM-style blockwise scales) | FP8 (same `fp8_scale_mode`) | BF16 | SM90 exactly | explicit geometry knobs on the config (`swap_ab`, `mma_tiler_mnk`); no tuner/knob-cache yet |
| `sm90_fp8_fp8_bf16_push_cuda` (`sm90_push_fp8`) | FP8 (E4M3) | FP8 (E4M3) | BF16 | SM90 | — (static dimensions/protocol choices only) |

**逐行解读**:
- NVFP4 / MXFP8 CuTeDSL 后端输出恒为 BF16, 同享 `knobs` 三态接口, 是 moe_ep 主推的 Mega 路径; `knobs="auto"` 明确写「never in serving」(不适合线上服务), 暗示其应仅用于离线/首次校准。
- `deep_gemm_mega` 把调优责任下放给 DeepGEMM 自身的 JIT 配置选择, moe_ep 这一层不介入。
- SM90 pull 端调优面最窄 — 只有 `swap_ab` 与 `mma_tiler_mnk` 两个显式几何参数, 尚无 tuner / knob-cache。
- SM90 push CUDA 端最静态, 仅维度/协议固定。
- 量化粒度: NVFP4 block-16, MXFP8 block-32 (UE8M0 scale), FP4 int8-packed block-32; FP8 后端支持 per-tensor 或 DeepGEMM-style blockwise scales。

### 表格 3: Split Comm 后端 (原文逐字还原)

| Backend | Config | Transport | Modes | Constraints |
|---|---|---|---|---|
| `nccl_ep` | `NcclEpConfig` | NCCL (nccl4py wheel) | LL `EXPERT_MAJOR` / `RANK_MAJOR`, HT `FLAT` | LL device kernel whitelists per-token row widths and caps top-k at 8 — see the runbook's "NCCL-EP low-latency device-kernel limits" |
| `nixl_ep` | `NvepConfig` | NIXL over UCX device API (GPU-initiated RDMA) | LL `EXPERT_MAJOR` only | needs `BUILD_NIXL_EP=1` (UCX v1.21+ device headers) and `BootstrapConfig.tcp_store`; `max_tokens_per_rank ≤ 1024`; hidden ∈ {2048, 2560, 3072, 4096, 5120, 6144, 7168, 8192}; handles top-k > 8 |

**逐行解读**:
- `nccl_ep`: 走 NCCL over nccl4py wheel, 同时支持 Low-Latency (LL) 的 `EXPERT_MAJOR` / `RANK_MAJOR` 与 High-Throughput (HT) 的 `FLAT` 三种 mode; LL 路径有 per-token row width 白名单且 top-k ≤ 8, 这是与 NIXL-EP 的核心差异。
- `nixl_ep`: 走 NIXL over UCX device API, 本质是 GPU-initiated RDMA; 仅支持 LL `EXPERT_MAJOR`, 但放宽了 top-k 限制 (>8 可), 前提是满足三项硬约束 — 构建标志、TCP store bootstrap、以及隐藏维度仅限离散集合; `max_tokens_per_rank` 上限 1024。

### 表格 4: Split Kernel 后端 (原文逐字还原)

| Backend | Activation | Weight | Output | Arch | Tuning |
|---|---|---|---|---|---|
| `identity` (`IdentityConfig`) | passthrough | none | dispatch tensor unchanged | any | — |
| `fused_moe` (`FusedMoeKernelConfig`) with `TrtllmBf16Config` | BF16 | BF16 | BF16 | SM100 family | inner `MoELayer` AutoTuner: per-runner tactic search + cross-backend winner per token bucket, up to `ExecutionConfig.tune_max_num_tokens` |
| `fused_moe` with `TrtllmFp4Config` | NVFP4 (block-16, quantized post-dispatch in the bridge) | NVFP4 (block-16) | BF16 | SM100/SM103/SM107 | same `MoELayer` AutoTuner |
| `fused_moe` with `CuteDslConfig` | NVFP4 (block-16) or BF16 (W4A16) | NVFP4 or 4-bit (W4A16) | BF16 | SM100/SM103 | same `MoELayer` AutoTuner |
| `sm100_mxfp8_mxfp4_bf16_cutedsl` (`Sm100_Mxfp8_Mxfp4_Bf16_Cutedsl_SplitConfig`) | MXFP8 (block-32 UE8M0; quantized post-dispatch, or pre-dispatch packed payload with `mxfp8_dispatch=True`, nccl_ep only, bit-identical) | MXFP4 (block-32 UE8M0) | BF16 | SM100/SM103 | `tactic=` pins a kernel tactic; unpinned runs the AutoTuner default tactic (tactic sweep only under an autotune context — not tuned in the shipped benchmarks) |

**逐行解读**:
- `identity` 是无操作直通后端, 主要用于调试与占位。
- `fused_moe` 三种 config (`TrtllmBf16Config` / `TrtllmFp4Config` / `CuteDslConfig`) 共享同一调优机制: 内层 `MoELayer` AutoTuner 先做 per-runner tactic 搜索, 再做 per-bucket 跨后端 winner 选择, 上限由 `ExecutionConfig.tune_max_num_tokens` 决定。
- `TrtllmFp4Config` 在 bridge 中 post-dispatch 才量化, 这意味着 comm 层仍以 BF16 搬运, 量化在接收端进行; 支持架构跨 SM100/SM103/SM107。
- `CuteDslConfig` 是 W4A16 (BF16 activation + 4-bit weight) 与 NVFP4 的双模入口。
- `sm100_mxfp8_mxfp4_bf16_cutedsl` 提供两条互斥但 bit-identical 的等价路径: ① post-dispatch 在 bridge 内量化 MXFP8; ② 预打包 payload + `mxfp8_dispatch=True` (仅 `nccl_ep` 可用); 这条路径明确写明 — 默认 tactic 在 shipped benchmarks 中并未调优, 仅在 autotune context 下才会触发 tactic sweep。

---

## 【公式解读】

**原文无公式** (文档中无 LaTeX 数学公式或带等价的伪代码公式; 仅含一段 Python 配置示例, 已作为 pinned-knob 例子在【技术要点】中转写)。

---

## 【关联】

- **执行入口 → runbook**: 文档开篇即指引「build/test/how-to-extend」全部在 [moe_ep_runbook.md](./moe_ep_runbook.md) 中, 包含本文中提到的 NCCL-EP low-latency device-kernel limits、`BootstrapConfig.tcp_store` 用法、以及 `MoEEpLayer` 的具体构造示例。
- **Mega CuTeDSL 调优 → TUNING.md**: 所有 Mega 后端的 knob 调优面、实测性能数据、benchmark 方法论都委派到 [kernel_src/cutedsl_megamoe/TUNING.md](../../flashinfer/moe_ep/kernel_src/cutedsl_megamoe/TUNING.md) — 本文提到「winners cacheable via `FLASHINFER_MOE_EP_KNOB_CACHE`」、MXFP8 2 档 profile 等细节都需要到 TUNING.md 中获取数字。
- **扩展新 Mega kernel 后端 → runbook anchor**: 「adding a new mega kernel backend」小节 ([anchor](./moe_ep_runbook.md#adding-a-new-mega-kernel-backend)) 是注册新 Mega 后端到 mega kernels 注册表的官方路径, 与本文后端表行一一对应。
- **构建与测试环境 → runbook anchor**: 「build & test environment」([anchor](./moe_ep_runbook.md#build--test-environment)) 是启用 `BUILD_NIXL_EP=1`、跑测套件的前提条件; 本文中 `nixl_ep` 的约束 (UCX v1.21+ device headers) 即在此处展开。
- **跨文档互引**: 本文与 runbook、TUNING.md 形成「架构 (本文) → 操作 (runbook) → 数据 (TUNING.md)」的三层链路; 三者共同构成 moe_ep 的完整知识面, 单一文档不足以独立使用。

---

## 【使用方法】

**启用方式 (原文有)**:
- 顶层入口: 构造 `MoEEpLayer(bootstrap, fleet_params, weights, fleet_knobs=(), backend=...)`, 由 `backend` 决定分发至 `MoEEpSplitLayer` 或 `MoEEpMegaLayer`。
- Mega 路径: `MegaConfig(megakernel=<Sm100_*_Cutedsl_MegaMoeConfig>)`, 重点配置 `knobs` 字段:
  - `knobs=None` (默认): 先查 `FLASHINFER_MOE_EP_KNOB_CACHE`, miss 时按 `tuner.default_knobs(max_tokens)` 选 token-count profile。
  - `knobs=dict`: 直接 pin, 须经 `tuner.is_valid` 校验。
  - `knobs="auto"`: 首次 `compute()` 时执行 collective sweep, **never in serving** (原文)。
- Split 路径: `SplitConfig(comm=<NcclEpConfig|NvepConfig>, kernel=<...>)`, comm 与 kernel 后端可任意组合; `fused_moe` 每个 `MoEConfig` 仅接受一个后端候选。
- 调优上限: split AutoTuner 受 `ExecutionConfig.tune_max_num_tokens` 约束。
- NIXL-EP 构建开关: `BUILD_NIXL_EP=1` + `BootstrapConfig.tcp_store`。
- W4A8 split kernel: hidden 与 intermediate 须为 128 的倍数 (原文)。
- 缓存环境变量: `FLASHINFER_MOE_EP_KNOB_CACHE` (Mega 路径 knob winner 跨 session 复用)。

**原文未涉及**: 具体 benchmark 跑法、性能数字、CI 触发命令、python import 路径与 pip 安装步骤等均未在本文档给出, 需跳转至 runbook 与 TUNING.md。
