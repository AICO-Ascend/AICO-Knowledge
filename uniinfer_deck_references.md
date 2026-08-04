# UniInfer Deck — 已验证技术引用源

> 来源：UniInfer 汇报 deck 的 8 份源码级调研，2026-08-04 用 MiniMax web_search 逐篇验证 arXiv ID。
> 用途：知识仓库收录 + 后续从原论文取插图替换 deck 定制 SVG。

## ✅ 已验证（7 篇，arXiv ID 确认）

| 标题 | arXiv ID | 会议/年 | 含可引用插图 | 对应 deck 页 |
|---|---|---|---|---|
| Gated Delta Networks: Improving Mamba2 with Delta Rule | [2412.06464](https://arxiv.org/abs/2412.06464) | ICLR'25 | GDN cell 结构图（β门控+Δ(K⊗V)状态更新） | P7 概念·recurrent |
| DeepSeek-V3 Technical Report | [2412.19437](https://arxiv.org/abs/2412.19437) | 2024 | MTP 层结构图、MoE router 图 | P10 投机推理/P9 MoE |
| NanoFlow: Towards Optimal LLM Serving Throughput | [2408.12757](https://arxiv.org/abs/2408.12757) | OSDI'25 | compute/memory/network overlap 图 | Part C 跨层 pipeline |
| Sarathi-Serve: Taming Throughput-Latency Tradeoff | [2403.02310](https://arxiv.org/abs/2403.02310) | OSDI'24 | chunked prefill + stall-free batching 时间线 | P14/prefill |
| Parallel Scan on Ascend | [2505.15112](https://arxiv.org/abs/2505.15112) | 2025 | 910B AI Core 结构（1AIC+2AIV+MTE） | Part C 硬件约束 |
| DeFT: Decoding with Flash Tree-Attention | [2404.00242](https://arxiv.org/abs/2404.00242) | ICLR'25 | KV-guided grouping + flattened tree KV splitting | P19 accept-fold |
| Efficient Memory Management with PagedAttention (vLLM) | [2309.06180](https://arxiv.org/abs/2309.06180) | SOSP'23 | paged KV cache block 图（经典） | P18 前缀缓存 |

## ✅ URL 型（2 个，可直接打开）

| 标题 | URL | 含可引用插图 | 对应 deck 页 |
|---|---|---|---|
| Stanford Hazy "Look Ma, No Bubbles" megakernel | [hazyresearch.stanford.edu/blog/2025-05-27-no-bubbles](https://hazyresearch.stanford.edu/blog/2025-05-27-no-bubbles) | paged SMEM 分页图 + counter sync + chunked MLP 流水 | Part C 死路判断 |
| 华为 FlashComm 1/2/3 技术文档 | [gitcode.com/ascend-tribe/ascend-inference-cluster/FlashComm](https://gitcode.com/ascend-tribe/ascend-inference-cluster/tree/main/FlashComm) | FC1/2/3 机制总览图 | Part C 通信融合 |

## ⚠️ 存疑（2 篇，论文存在但 arXiv ID 未验证）

| 标题 | 待核 ID | 说明 |
|---|---|---|
| Gated DeltaNet-2 (decoupled erase/write gates) | ~~2605.22791~~ | fla GitHub 2026-05 加了实现+paper 链接，CSDN 有架构图描述，但此 arXiv ID 搜不到。去 [fla repo](https://github.com/fla-org/flash-linear-attention) 看 paper 链接拿正确 ID |
| POD-Attention (fused prefill+decode kernel) | ~~2410.18038~~ | agent 提到 ASPLOS'25，但此 ID 搜不到。去 ASPLOS'25 proceedings 查 |

## 其他已引用但未单独验证的论文（来自 8 份调研报告）

| 标题 | arXiv ID | 用途 |
|---|---|---|
| EAGLE-1/2/3 | 2401.15077 / 2406.16858 / 2508.08192 | spec decode draft head |
| Medusa | 2401.10774 | tree draft |
| SpecInfer | 2305.09781 | tree attention |
| FlashInfer | 2401.02055 | cascade/sampling |
| Mamba2/SSD | 2405.21060 | chunked parallel form |
| RetNet | 2307.08621 | diagonal decay |
| DistServe | 2401.09670 | PD disagg |
| Comet | 2502.19811 | MoE comm overlap |
| Lancet | 2404.19429 | whole-graph overlap |
| CMU Mirage MPK | 2512.22219 | compiler megakernel |
| AscendCraft | 2601.22760 | LLM AscendC generation |
| AMLA | 2509.25224 | UB 192KB 实证 |

## 插图引用规则

未来 deck 里每个插图必须带引用链接与出处：
```
图源: [论文标题] arXiv:XXXX.XXXXX / [博客URL]
```
无论定制 SVG 还是原论文图，均需标注。
