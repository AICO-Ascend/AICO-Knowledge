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

---

## 🔄 2026-08-17 回灌：v4 deck 精确裁剪图 + 实际页位

> 来源：另一 project `InferArch/uniinfer_low_latency_gxli_qwen36` 的
> `task-qwen36-35B-A3B/01_总结与汇报/TECH_DEEPDIVE_REFERENCES_20260817.md`（汇报 deck v4 配套深读材料）。
> 该 deck 植入时从原论文 PDF 精确裁剪了 6 张图（仓内整页渲染 `extraction/assets/` 不便直接植入 deck，故裁剪版另存）。

### 6 张精确裁剪图（已回灌 `extraction/assets_cropped/`）

| 裁剪图 | 源论文 / arXiv | 原图定位 | deck 技术点 |
|---|---|---|---|
| `gated-delta-networks-...__block-design.png` | Gated Delta Networks · [2412.06464] | Fig.1 GDN block（q/k 路径+α/β门控） | §1 线性注意力 recurrent state |
| `deepseek-v3-technical-report__mtp.png` | DeepSeek-V3 · [2412.19437] | Fig.3 MTP 链式结构 | §3 投机解码 / accept-fold（deck P19） |
| `sarathi-...__roofline.png` | Sarathi-Serve · [2403.02310] | Fig.5 算术强度 roofline | §2 decode memory-bound 证据 |
| `sarathi-...__genstall.png` | Sarathi-Serve · [2403.02310] | Fig.7 generation stall 时间线 | §5 stall-free 调度 |
| `efficient-memory-management-...__block-table.png` | PagedAttention(vLLM) · [2309.06180] | Fig.6 块表 | §4 前缀缓存 / host-offload（旧标 P18） |
| `parallel-scan-on-ascend-...__910b-aicore.png` | Parallel Scan on Ascend · [2505.15112] | Fig.3.1 910B AI Core | §6 硬件约束（deck P16/17 NPUGraph） |

### v4 deck 实际页位（对位旧 P7/P10 标签）

旧 deck（v1, 08-03）页码映射已过期。v4 deck（08-17）可验证的页位（TECH_DEEPDIVE 正文显式标注）：
- **P16/17** — 全链路 NPUGraph（~3000 kernel 单图，§6）
- **P19** — accept-fold / 免回滚（§1 GDN state snapshot + §3 MTP verify）

> ⚠️ 其余 §2/§3/§4/§5/§7 的精确 v4 页位在 TECH_DEEPDIVE 正文未显式标注——如需完整页位表，去上述另一 project 的
> `TECH_DEEPDIVE_REFERENCES_20260817.md` 或 v4 deck 源文件对位，**不要从旧 P7/P10 标签推断**。

### 边界（仓不能完全替代核读，下次植入前仍需人工）

- **页图不全**：DSV3 仓内整页只抽了 p12/15/48，MTP 图在 p10——本次裁剪图已补；后续他论文若 deck 需要特定页，用 `fitz` 从 `papers/<slug>.pdf` 现裁即可。
- **公式有损**：GDN gated delta rule 在 fulltext txt 里断行错位——精确公式见上方 §1 块（已核），或走 e-print LaTeX（`eprint_formulas.py`）。
- **2 张存疑 ID 仍存疑**：Gated DeltaNet-2、POD-Attention（见上方「⚠️ 存疑」表）——本次 deck 植入已绕开，未引用。
