# Efficiently Serving Large Multimodal Models Using EPD Disaggregation — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记，独立文件，extract_phase1 重跑不丢。
> 论文：Efficiently Serving Large Multimodal Models Using EPD Disaggregation · arXiv:2501.05460v4 (28 Jun 2025)
> 作者：Gursimran Singh, Xinglu Wang, Yifan Hu, Timothy Yu, Linzi Xing, Wei Jiang, Zhefeng Wang, Xiaolong Bai, Yi Li, Ying Xiong, Yong Zhang, Zhenan Fan — Huawei Technologies Canada × Simon Fraser Univ. × Huawei Cloud。ICML 2025 (PMLR 267)。代码开源 https://github.com/vbdi/epdserve。
> 9 张图 M3 caption 已织入分析（Figures 1–6, 9, 11, 12）；7 条核心公式（EPD pipeline 5 式 + Eq.1 优化器）以 formulas.json LaTeX 为权威源，`$$` 直引未改写，已与 M3 图解双源校验。

## 核心问题

EPD 解决的不是 LLM serving 优化，而是 **LMM (Large Multimodal Models) serving 中"编码阶段"被错误地耦合进 prefill 所造成的系统性低效**（§1）。具体矛盾由 Figure 1（p.1）直观呈现：M3 解读显示 aggregated 拓扑把 encoder E5 挤进 LLM⁴ 所在的 GPU 行，prefill 的 LLM⁴ 把 E5 推迟（视觉上 E5 被推到 LLM⁴ 之后），形成 inter-stage interference；而 disaggregated 拓扑把 E5 钉在独立 GPU 行、LLM¹–⁵ 分布到其他行，消除跨阶段争用——这正是 TTFT 膨胀的元凶。具体四点：

1. **LMM 引入了第三个阶段——encode**：LLM 推理只有 prefill + decode，LMM 额外需要 multimodal encoder (MME) 把图像/音频/视频转成 visual tokens。这一阶段 (a) 计算密集（尤其高分辨率输入），(b) 产生 token inflation——visual token 数量随分辨率爆炸式增长，导致下游 prefill attention 呈**二次方**计算膨胀（§1）。
2. **既有 disaggregation 只解了 P/D，没解 E**：DistServe / SplitWise / DéjàVu / Mooncake / PD-Serve 把 prefill 与 decode 分离（§2），但都**默认为纯文本 LLM 设计**——把 encode 与 prefill 捆绑在同一个 GPU 集合上同步执行（即 "aggregated" 设定，Figure 1 上）。后果：(a) **inter-stage 干扰**——prefill (LLM-4) 拖延 encode-heavy 请求 (E5)；(b) **内存挤兑**——MME 与 LLM weights + KV cache 同时驻留一卡，限制 batch size 与每请求图像数。Figure 2（p.2）的 M3 解读给出量化证据：MiniCPM-V 2.6 上 1 img/req 时 disaggregated（移除 LLM）batch size ~48 vs aggregated ~6（约 8× gap），≥15 img/req 时 aggregated 直接 OOM 而 disaggregated 仍能维持小批——这正是把 LLM 从 encoder GPU 拿走带来的量级跃迁，直接转化为 TTFT/TPOT SLO 合规度。
3. **encode 阶段的可并行性被浪费**：多图像请求（如自动驾驶、视频 QA）会被切成大量独立 patch，但 aggregated 系统顺序编码，造成 head-of-line blocking（§2）。
4. **资源需求随负载动态变化**：online 场景下图像数、输出长度随时变化，E/P/D 三阶段算力配比需要动态调整——冷启动重初始化会丢失已计算 KV/MM cache 并产生级联 SLO 违约（§3.2.4）。

SLO 指标体系：**TTFT**（首 token 时延，主要由 E+P 决定）、**TPOT**（token 间间隔，由 D 决定）、**SLO attainment**（同时满足 TTFT+TPOT 的请求比例）、**goodput**（满足 ≥90% SLO attainment 的最大请求速率，§4）。

## 关键创新点

1. **EPD 三阶段解耦：把 encode 从 prefill 中拆出来（§3.1, Figure 3 p.3）**——本文最根本创新。Figure 3 的 M3 解读揭示三池拓扑：E GPUs（黄）持 Encoding Queue + Encoding Stage → EP Bridge Queue → P GPUs（橙）持 Prefill Queue + Prefill Stage → PD Bridge Queue → D GPUs（绿）持 Decode Queue + Decode Stage，数据左→右流动，每池 data-parallel 自带 bridge queue 缓冲跨池迁移。EPD pipeline 形式化（§3.1，公式为 formulas.json 权威 LaTeX，逐字直引，未改写）：
   - Encoding: $$v_t^e = E(i_m)$$ — MME 把多模态输入 $i_m$ 转 high-dimensional embedding $v_t^e$；
   - **EP-migration**: $$v_t^p = \psi_{EP}(v_t^e)$$ — vision tokens 跨实例迁移到 prefill 节点；
   - Prefill: $$kv_1^p, o_1^p = P(v_t, i_p)$$ — 融合文本 prompt $i_p$，产生初始 KV cache 与首 token；
   - **PD-migration**: $$kv_1^d, o_1^d = \psi_{PD}(kv_1^p, o_1^p)$$ — KV cache + 首 token 迁移到 decode 节点；
   - Decode: $$kv_{t+1}^d, o_{t+1}^d = D(kv_t^d, o_t^d)$$ — 自回归生成下一 token 并更新 cache。
   五式与 Figure 3（p.3）三池拓扑互证：$\psi_{EP}$ 对应 EP Bridge Queue（E→P）、$\psi_{PD}$ 对应 PD Bridge Queue（P→D）——LaTeX↔M3 图双源一致。
   每个阶段独立实例，**实例间 data-parallel (DP)**；实例内 worker 跑 **tensor-parallel (TP) 与/或 pipeline-parallel (PP)**；E worker 只装 MME weights + MM cache，P worker 装 LLM weights + MM cache + KV cache，D worker 装 LLM weights + KV cache（§3.2, Figure 4 p.4）。Figure 4 的 M3 解读进一步显示每个 instance 自带 Scheduler + Block Manager，中央 Scheduler/Load Balancer 分发请求，**Monitoring & Dynamic Role Switching 模块**监督 bridge queue 并触发实例迁移（图中标注 "Migrate 1 D instance to P"），并行化标签（TP/PP、IRP、DP）置于 instance 下方——这正是 §3.2.4 动态切换的图形化表达。**关键内存收益**：E worker 不需 LLM weights 与 KV cache，仅 weight 部分实测省 ~95%/96.2%/78.3%（MiniCPM-V 2.6 / InternVL2-8B / InternVL2-26B），加 KV cache 后实测 **15× lower peak memory**（§4.3）。

2. **异步 token transfer + MMBlockManager（§3.2.1）**——解决 EP-migration 引入的额外传输延迟。机制：encode 完成后 tokens 存入 E worker 的 MM cache，E worker 立即可服务新请求；asynchronous event loop 监听完成事件并经 **NVLink / InfiniBand** 直接异步推送到 P worker 的 MM cache；确认后清空 E 端 cache 块释放内存。**MMBlockManager** 按请求需求预分配 cache 块，迁移后 reassign 或 de-allocate。两阶段（E 与 P）都维护 MM cache 以使 transfer overlap 于计算。该机制对应 Figure 4（p.4）中各 instance 间的 "Async Transfer" 高带宽链路与 EP/PD Bridge Queue 缓冲——M3 解读强调 bridge queue 把 cache 迁移与计算解耦，是 role 实时重配的前提。

3. **Intra-Request Parallelism (IRP)（§3.2.2）**——本文 TTFT 优化的核心机制。把**单个请求的多张高分辨率图像的 patch 集合**在多个 E worker 间按 data-parallel 方式分片；因 patch 编码彼此独立，可并发处理并异步传输；全部 patch-level tokens 到达 P 阶段后**对齐、project、merge** 成完整 multimodal tokens。这等价于把"请求间并行"扩展到"请求内并行"。IRP **不需要通信**（patch 间无依赖），优于 TP，故在 encode 阶段论文用 `p^IRP` 替代 `p^TP`（§D）。效果（§4.4 Table 4）：禁用 IRP 后 TTFT 在 2/4/6/8 images/request 下分别劣化 1.6×/2.4×/2.9×/2.5×——且图像越多收益越大。Figure 6（p.7）的 TTFT box plot 给出 IRP 的视觉证据：M3 解读显示 EPD 的蓝色 box 在三个模型子图中均明显低于 DistServe 绿色 box，且 gap 随 #I/R 增长而扩大——EPD 把 mean TTFT 降 71.9%/32.8%/44.9%（MiniCPM-V 2.6 / InternVL2-8B / InternVL2-26B vs DistServe），是唯一在 16 img/req 仍维持 sub-second 首 token 的系统。

4. **黑盒资源分配优化器（§3.2.3, §D）**——形式化为 Eq.1（公式为 formulas.json 权威 LaTeX，逐字直引）：
   $$\max_{(\mathbf{p},\mathbf{b},\mathbf{s}) \in \mathcal{X}} f(\mathbf{p},\mathbf{b},\mathbf{s}) - \beta cost(\mathbf{p})$$
   其中 `p`（并行配置：每实例 TP/PP，encode 阶段 `p^TP = p^IRP`）、`b`（每实例 max batch size）、`s`（调度策略：assignment 如 Round-Robin / Least-Loaded First；ordering 如 FCFS / SJF / SLO-aware）均为可变长度向量（实例数本身也待定）。`f(·)` 取 goodput，由扩展自 DistServe 的 simulator 评估，用 **Bayesian optimization** 求解。cost = `c·Σ(p^TP_i × p^PP_i)`，可用约束（如总 GPU 数 = 8 或 ≤ 16）缩减搜索空间。效果（§4.4 Table 5）：禁用优化器随机采 10 配置的期望，goodput 降 2.2×、TTFT 劣化 2.1×。该优化器在 Figure 10（§A.3）被验证能自动选出 5E2P 配置作为 offline E2E throughput 最优——证明黑盒搜索比人工配比更稳。

5. **Dynamic Role Switching（§3.2.4）**——应对 online workload 变化。监控全系统队列统计，把空闲阶段实例迁移到瓶颈阶段。**三步**：(a) **Offload**——源阶段 S 实例停止接新请求并把队列任务再分给同阶段兄弟；(b) **Migration**——按目标阶段 T 重配（如涉及 E 阶段需切换 LLM↔MME 模型与 KV↔MM cache；P↔D 可复用 LLM 与 KV cache，开销小）；(c) **Onload**——迁移后实例恢复处理 T 阶段任务。**单次迁移 < 0.7s**；P↔D 显著更快。该机制在 Figure 4（p.4）由 "Monitoring & Dynamic Role Switching" 模块图形化体现（M3 标注 "Migrate 1 D instance to P"），即监控 bridge queue 拥堵后触发实例重配。实验（§4.4 Table 6，前 10 请求 50 输出 tokens、后 90 请求 500 tokens，3 r/s，单 4K 图）：开 role switching 从 5E1P2D 自适应重配到 2E1P5D，端到端延迟 28.01s vs 61.10s（2.2×）、TPOT 0.05 vs 0.12（2.4×）；关 switching 卡在初始配置无法适配解码需求。

6. **NPU 适配（§4.5, §F）**——把 EPD 移植到 Huawei Ascend 910B3 NPU（64GB HBM）。两点差异：(a) 用 **Ascend-vLLM**（vLLM 的 NPU 适配，用 CANN 替代 CUDA）替代 vLLM；(b) **Container-based deployment**——每个 E/P/D 实例独立部署为 API，scheduler 发 POST 请求调度，提升云可移植性。关键发现（§F.1, Figure 12 p.16）：M3 解读的 stacked bar 显示 GPU 上 #I/R=8 时 encode 占 ~25%、prefill ~75%，而 NPU 仍保留 ~40% encode——即 **NPU 上 encode 占 TTFT 比重比 GPU 高 10–20%**，故 **EPD 在 NPU 上收益比 GPU 更显著**：EPD-NPU 相比 vLLM TTFT 降低 **35.2%**（GPU 上 24.4%，多 ~10pp）。SLO 实验（§4.5, Figure 9 p.9，InternVL2-8B，8 张 4K 图/请求，TTFT≤8.5s, TPOT≤0.12s，最优配 5E2P1D）：M3 解读显示 EPD（蓝）从接近 100% 缓慢衰减到 ~20%，而 DistServe（绿）与 vLLM（红）在所有 request rate 下均 flat 在 0% 附近——**EPD 是唯一满足 SLO 的配置**。

7. **模态泛化（§A.1）**——除视觉外，扩展到**音频模态**。用 ultravox-v0.3 (基于 LLaMA3.1-8B)，每请求 24 个音频文件，TTFT≤2.0s, TPOT≤0.025s，4 GPU 配置 vLLM=DP / DistServe=3P1D / EPD=2E1P1D。Table 7：EPD 在所有 request rate 下 SLO attainment ≥0.93（除 0.50 r/s 的 0.96），goodput 1.16 r/s，DistServe 仅 0.45 r/s——证明 EPD 不限视觉，encode-heavy 任意模态均受益。

## 表格（原文结构化）

### Table 1 — Video-MME 上 Mean TTFT (s)（§4.1, 100 samples, 1 req/s, MiniCPM-V 2.6）
| #Frames | 8 | 16 | 32 | 64 |
|---|---|---|---|---|
| vLLM | 0.42 | 0.82 | 1.59 | 3.11 |
| DistServe | 0.42 | 0.81 | 1.54 | 3.08 |
| **EPD** | **0.24** | **0.30** | **0.49** | **1.00** |

EPD 较 DistServe 降 42.9%（8 帧）→ 67.5%（64 帧）；随视频长度增加 gap 拉大——与 Figure 6（p.7）的 box plot 趋势一致（M3: gap 随 #I/R 扩大），共同证明 IRP 在长视频/多图像场景下的可扩展性。

### Table 2 — Maximum images per request（§4.3, batch=1, KV cache 占 80% free mem）
| Model | Image Reso. | DistServe | EPD |
|---|---|---|---|
| MiniCPM-V 2.6 | 313×234 | 77 | 490 |
| MiniCPM-V 2.6 | 787×444 | 26 | 165 |
| MiniCPM-V 2.6 | 4032×3024 | 7 | 49 |
| InternVL2-8B | 313×234 | 19 | 19 |
| InternVL2-8B | 787×444 | 19 | 19 |
| InternVL2-8B | 4032×3024 | 19 | 19 |
| InternVL2-26B | 313×234 | 1 | 10 |
| InternVL2-26B | 787×444 | 11 | 45 |
| InternVL2-26B | 4032×3024 | 1 | 10 |

InternVL2-8B 受最大 context length 限制恒为 19。EPD 在 InternVL2-26B 4K 分辨率下 10× DistServe。该结果呼应 Figure 2（p.2）的预实验：M3 显示 ≥15 img/req 时 aggregated 直接 OOM、disaggregated 仍维持小批——Table 2 是该现象在三个模型、三档分辨率上的系统化扩展。

### Table 3 — Maximum supported batch sizes for E and P stages（§4.3, 10 images/req, KV cache 占 80% free mem）
| Model | Image Reso. | #Patch | DistServe (E,P) | EPD E | EPD P |
|---|---|---|---|---|---|
| MiniCPMv 2.6 | 313×234 | 1 | (7, 49) | 86 | 86 |
| MiniCPMv 2.6 | 787×444 | 3 | (2, 16) | 29 | 29 |
| MiniCPMv 2.6 | 4032×3024 | 10 | (OOM, 4) | 9 | 9 |
| InternVL2-8B | 313×234 | 13 | (2, 15) | 2 | 2 |
| InternVL2-8B | 787×444 | 3 | (9, 67) | 10 | 10 |
| InternVL2-8B | 4032×3024 | 13 | (2, 15) | 2 | 2 |
| InternVL2-26B | 313×234 | 13 | (OOM, 6) | 1 | 1 |
| InternVL2-26B | 787×444 | 3 | (1, 22) | 4 | 4 |
| InternVL2-26B | 4032×3024 | 13 | (OOM, 6) | 1 | 1 |

InternVL2-26B 787×444 下 E batch 22 vs DistServe 1 → **22× improvement**（论文最大 batch size 收益）。

### Table 4 — IRP 消融对 TTFT (s) 影响（§4.4, MiniCPM-V 2.6, 100 req 平均）
| #I/R | 2 | 4 | 6 | 8 |
|---|---|---|---|---|
| EPD | 0.92 | 1.02 | 1.14 | 1.74 |
| w/o IRP | 1.46 (1.6×) | 2.47 (2.4×) | 3.37 (2.9×) | 4.27 (2.5×) |

degradation 随 #I/R 加重（1.6×→2.9×），印证 Figure 6（p.7）的 EPD-DistServe gap 扩张趋势——IRP 是 EPD 在多图像 TTFT 优势的核心机制。

### Table 5 — Offline optimizer 消融（§4.4）
| Metric | EPD | w/o Opt (random 10) |
|---|---|---|
| Goodput (r/s) ↑ | 1.25 | 0.56 (2.2×↓) |
| TTFT (s) ↓ | 2.12 | 4.48 (2.1×↓) |
| TPOT (s) ↓ | 0.031 | 0.025 (0.8×) |

### Table 6 — Dynamic role switching 消融（§4.4, workload shift 50→500 tokens）
| Metric | EPD | w/o Switch |
|---|---|---|
| Latency (s) ↓ | 28.01 | 61.10 (2.2×↓) |
| TTFT (s) ↓ | 1.42 | 1.33 (0.9×) |
| TPOT (s) ↓ | 0.05 | 0.12 (2.4×↓) |

### Table 7 — 音频模态 SLO attainment（§A.1, ultravox-v0.3, 24 audio/req）
| Rate (r/s) | 0.10 | 0.25 | 0.50 | 1.00 | 1.10 | 1.15 | Goodput (r/s) ↑ |
|---|---|---|---|---|---|---|---|
| vLLM | 0.99 | 1.00 | 0.99 | 0.91 | 0.87 | 0.87 | 1.01 |
| DistServe | 0.99 | 0.94 | 0.89 | 0.72 | 0.69 | 0.68 | 0.45 |
| EPD | 0.99 | 0.99 | 1.00 | 0.96 | 0.93 | 0.93 | 1.16 |

### Table 8 — Maximum KV cache size (% free mem)（§A.2, batch=1, 4K reso）
| Model | # Img/Req | 5 | 10 | 20 | 40 | 80 |
|---|---|---|---|---|---|---|
| MiniCPM-V 2.6 | DistServe | 86% | 74% | 49% | OOM | OOM |
| MiniCPM-V 2.6 | EPD | 99% | 97% | 95% | 92% | OOCL |
| InternVL2-8B | DistServe | 94% | 89% | OOCL | — | — |
| InternVL2-8B | EPD | 95% | 91% | OOCL | — | — |
| InternVL2-26B | DistServe | 67% | 36% | OOM | OOM | — |
| InternVL2-26B | EPD | 89% | 80% | 63% | OOCL | — |

InternVL2-26B 10 img/req 下 EPD 80% vs DistServe 36% → **2.2× larger KV cache**（论文摘要中 2.2× 来源）。

### Table 9 — SLO 阈值（§E.3, 经验设定）
| #I/R | MiniCPM-V 2.6 TTFT/TPOT | InternVL 8B TTFT/TPOT | InternVL 26B TTFT/TPOT |
|---|---|---|---|
| 2 | 1.40 / 0.04 | 1.20 / 0.05 | 3.50 / 0.07 |
| 4 | 2.60 / 0.04 | 2.40 / 0.06 | 7.05 / 0.08 |
| 6 | 3.90 / 0.06 | 3.55 / 0.09 | 11.00 / 0.95 |
| 8 | 5.10 / 0.06 | 5.00 / 0.18 | 15.00 / 0.15 |

TTFT 随 #I/R 近线性上升（encode 负载 + 更多 visual token）；TPOT 受影响小。该阈值用于 Figure 5/11 的 90% SLO 参考线。

### Figure 5 / Figure 11 — SLO attainment 全景（§4.1 / §A.4）
Figure 5（p.6）2×3 grid：列 = MiniCPM-V 2.6 / InternVL2-8B / InternVL2-26B，行 = 2 / 4 img/req；M3 解读显示 EPD（蓝）在所有 6 子图中均能在显著更高的 request rate 下维持 >90% SLO（90% 虚线），而 DistServe（绿）/vLLM（红）因跨阶段干扰塌缩到 ~10% 以下，且随模型 8B→26B、图像 2→4 恶化。Figure 11（p.13）是 6/8 img/req 的扩展：EPD 仍近 100% 持续到高 rate，baseline 在低 rate 即崩溃——证明 EPD 在多图像重负载下仍 scale gracefully。

### 实验硬件（§E.1）
8× NVIDIA A100 80GB（论文正文写 82GB），128 CPU/1TB RAM，CUDA 12.2，Flash-Attention-2，FP16。vLLM 0.6.1.post1。block size=16，max 2048 blocks/req，context cap 49,152，decoding token cap 81,920/batch，FCFS 调度，KV cache GPU util=50%，multimodal data cap=32/prompt，MM cache size=3000，eager mode。Online 实验中 batch size 设 1 以优化 TTFT/TPOT。

## 与同类对比

- **vs DistServe (Zhong et al., OSDI 2024)**——EPD 的主要 baseline 与 simulator 基础。DistServe 是 **P/D disaggregation**，但 E 与 P 仍同一 GPU 集合（aggregated）；EPD 把 E 也独立出来。论文为公平把 DistServe 扩展支持多模态（修改 block manager 容纳 multimodal token）。所有实验中 EPD 在 SLO attainment（Figure 5/11，M3: DistServe 绿线塌缩到 ~10%）、TTFT（Figure 6，M3: 绿 box 显著高于蓝 box）、batch size（Table 3: 22×）、KV cache size（Table 8: 2.2×）、images/req（Table 2: 10×）上全面优于 DistServe。DistServe 默认 7P1D 配置，EPD 默认 5E2P1D。
- **vs vLLM (Kwon et al., SOSP 2023)**——monolithic baseline，三阶段同 GPU。EPD 复用 vLLM 的分布式执行引擎（Ray actors 实现 GPU worker）与 OpenAI multimodal API；EPD 在所有 SLO 实验中远超 vLLM（Figure 5/9/11，M3: vLLM 红线在各 rate 下均远低于 EPD 蓝线）。注意：TTFT 单独实验（§4.2）中 vLLM 等价于 DistServe（decode 排除），故被省略。
- **vs SplitWise / DéjàVu**——同样是 P/D disagg，但只针对 LLM，未处理 encode 阶段（§2）。
- **vs Mooncake (Qin et al., 2024)**——KVCache-centric disagg，专注 LLM 长上下文 prefill（chunked pipeline parallelism）与 overload 下的 early rejection；不涉及 multimodal encode。EPD 借鉴其 disagg 思路，但创新在**把 disagg 维度从 P/D 扩展到 E/P/D 三阶段**，并在 multimodal 场景引入 IRP 与 role-switching。Mooncake 关注 prefix cache 复用与全局调度，EPD 关注 stage 间内存/算力配比与 encode 并行。
- **vs SARATHI / Sarathi-Serve (Agrawal et al., 2023/2024)**——collocated 路线，通过 chunked prefill + piggyback decode 提高单 GPU 利用率、消除 pipeline bubble。EPD 走相反方向（进一步 disagg），§B 局限中明确承认：**SLO 可放松、throughput 优先场景下 aggregated/collocated 因无 inter-stage 通信开销与 pipeline bubble，GPU 利用率更高、更省钱**——即 EPD 与 Sarathi-Serve 互为不同负载区间的最优解。
- **vs Inf-MLLM (Ning et al., 2024)**——单 GPU 上 LMM 流式推理 + KV cache eviction/compression，面向资源受限；EPD 面向云服务多 GPU，强调 SLO 而非单卡极限。
- **vs Mooncake / PD-Serve**——这两者虽把 disagg 扩展到 KV cache 管理与系统级优化，但仍限 LLM，未触 encode 阶段（§2）。

## 跨论文关系（→ MOC 谱系）

把 EPD 放在 **serving/disagg genealogy 的 multimodal-disagg 分支**：

- **Text disagg root（P/D disagg）**：[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]（KVCache-centric + prefix reuse + early rejection，overload 商业 MaaS）、DistServe、SplitWise、DéjàVu、PD-Serve。EPD 是这条根的**多模态延伸**——把 disagg 的切分维度从 2（P/D）扩到 3（E/P/D），并显式新增 EP-migration、MM cache、IRP 等机制（Figure 3 p.3 三池拓扑）。
- **Collocated/融合路线对比**：[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]（chunked prefill + piggyback decode，消除 bubble，单卡高利用率）——与 EPD 路线相反，但在 §B 局限中明确承认 throughput-priority/SLO-relaxed 场景下 collocated 更优。EPD 与 Sarathi-Serve 互补于不同负载区间。
- **硬件落地 / NPU disagg**：[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]（Huawei CloudMatrix 384 superpod 上 disagg MoE-Attention + PD separation）——EPD 的 NPU 适配（Ascend 910B3 + Ascend-vLLM + CANN）与 CloudMatrix 同属 Huawei Ascend 生态，可视为 EPD 框架在更大规模 superpod 上的工程化延伸；Figure 12（p.16）的发现"NPU 上 encode 占比高 10–20% → EPD 收益更显著"（M3: NPU encode ~40% vs GPU ~25% at #I/R=8），为 CloudMatrix 这类 NPU 集群的 disagg 设计提供理论依据。
- **Cross-DC disagg**：[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]（PaaS，KV cache 跨数据中心流转）——EPD 当前 EP/PD-migration 仍在机柜内（NVLink/InfiniBand），未来方向（§C）提到 visual token migration overhead 可用 token pruning 压缩，且 privacy-aware 场景下 encode 可下沉到 edge——即 EPD 的 E 阶段天然适合 edge-cloud 分离，与 PaaS 的 cross-DC KV cache 流转可组合。
- **被服务的多模态模型**：MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B（§E.2），与 [[qwen3-vl-technical-report]]、[[kimi-k2-5-visual-agentic-intelligence]] 同属 LMM 模型层，是 EPD 这类 serving 系统的"乘客"。
- **视觉 token 表示效率**：[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]（DeepStack，视觉 token 深堆叠）——与 EPD 正交，DeepStack 改 token 表示，EPD 改 serving 调度；但 §C 提到 visual token pruning（引 DivPrune, Alvar et al. 2025）可降低 EP-migration 开销，是 EPD 的未来增强方向。
- **chunked prefill 技术源**：[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]（SARATHI 原始 chunked prefill）——EPD 在 prefill 阶段未用 chunked prefill，但 simulator 基于 DistServe、调度策略可适配 chunked 方案，是潜在融合点。

## 局限与边界

1. **SLO 放松场景下不优（§B）**：当 throughput-per-dollar 是首要目标、latency SLO 可放松时，aggregated/collocated（如 Sarathi-Serve）因无 inter-stage 通信开销与 pipeline bubble、GPU 利用率更高，更省钱。EPD 适合 latency SLO 不可妥协的云服务场景。
2. **E 与 P 阶段均 compute-bound，收益敏感于 pipeline bubble（§B）**：E/P disagg 的增益主要来自 stage-specific 调度/批处理/并行优化（尤其 IRP）；若资源配比不均导致 pipeline bubble，latency 收益会被侵蚀。需要精细 tuning + 响应式 worker migration——这也是 dynamic role switching（Figure 4 p.4 的 Monitoring 模块）必需的原因。
3. **visual token migration 开销未优化（§C）**：当前 EP-migration 直接传 token，未压缩；高分辨率/多图像场景下 visual token 数量爆炸，迁移本身可成瓶颈（Figure 3 p.3 的 EP Bridge Queue 是潜在拥塞点）。未来方向：token pruning/compression（引 DivPrune, SnapKV, Gear 等）。
4. **E 与 P 内存特性不对称未利用（§C）**：encode 是低内存高算力、prefill 是高内存高算力，当前用同质 GPU；未来可用异构硬件（高内存 GPU 给 P，低内存高算力单元给 E）进一步提升 cost-efficiency。
5. **encode-only-at-edge 隐私场景未实现（§C）**：提出 encode 下沉 edge、原始图像不出端、只传 representation 到云的 privacy-preserving 架构想，但仅作为 future work。
6. **实验规模与负载覆盖**：所有 GPU 实验在 8×A100 上完成，最大 8 img/req（附录扩到 8，Figure 11 p.13）；NPU 8×910B3 仅测 InternVL2-8B；异构场景（§A.3）是受控模拟。生产级超大规模（如 CloudMatrix 384）未直接验证。
7. **SLO 阈值经验设定（§E.3）**：TTFT/TPOT 阈值由"该模型在该 8-GPU 集群上 EPD 与 baseline 都现实可达"反推（Table 9），存在自证风险——阈值与硬件强绑定，跨集群未必迁移。Figure 5/11 的 90% 参考线即基于该阈值。
