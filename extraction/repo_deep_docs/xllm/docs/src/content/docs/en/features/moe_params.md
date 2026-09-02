# moe_params

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/moe_params.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/moe_params.md

# 深度解读：EP Parallelism（专家并行）

---

## 【定位】

这篇文档针对 DeepSeek-R1 这类 671B 参数量级 MoE（混合专家）大模型在分布式部署时面临的显存利用率低、通信开销大、硬件成本高的核心瓶颈，介绍 xllm 通过 **Expert Parallelism (EP)** 提升 KV Cache 容量、降低冗余通信、并改善硬件利用率的方案与参数配置。

---

## 【技术要点】

- **EP 的三个核心优势（原文摘录）**：
  1. 资源相同时，每 GPU 承载的 Expert 越少，可用于 KV Cache 的显存越多，从而缓存更多 token；
  2. 由于 MLA 特性，相同资源下 TP Size 越小，KV Cache 冗余越少，同样可缓存更多 token；
  3. 大规模 EP 部署可将同一 Expert 的 token 计算集中到同一设备上，提升硬件利用率。

- **三个核心可配参数**：
  - **`dp_size`**：Attention 部分的数据并行规模。默认 `1`，可设为 2 的幂次；当 `dp_size` 不等于设备总数时，DP 组内启用 TP 并行。
  - **`ep_size`**：MoE 部分的专家并行规模。默认 `1`，可设为 2 的幂次；当 `ep_size` 不等于设备总数时，DP 组内启用 TP 并行。
  - **`expert_parallel_degree`**：EP 等级开关。默认 `0`（关闭 EP）；开启 EP 时默认 `1`（EP Level 1）；当 `ep_size` 等于设备总数时，可设为 `2` 启用 EP Level 2。

- **两种 EP 等级对应不同通信模式**：
  - **EP Level 1**（默认）：Attention 与 MoE 计算完成后，通过 **All Gather** 在所有设备间汇总数据再送入下一阶段。
  - **EP Level 2**（仅在 `ep_size = 设备总数` 时可用）：Attention 与 MoE 之间的通信切换为 **All-to-All (ALL2ALL)**，仅向真正需要的设备发送数据，从而降低通信量与开销。

- **典型规模示例**：64 卡场景下 EP Level 1 采用 `Attention: dp32tp2, MoE: ep32tp2` 的拆分组合；EP Level 2 同样以 64 卡为例展示。

---

## 【关键机制与数据】

**工作原理与数据流（按原文展开）**：

- **背景动机（原文）**：
  - 场景：DeepSeek-R1 671B 参数量级模型。
  - 传统分布式部署瓶颈：① GPU 显存利用率低；② 通信开销高；③ 硬件成本高。
  - 解决方向：引入 Expert Parallelism (EP)。

- **EP 与显存/KV Cache 的关系（原文）**：
  - 每 GPU 上的 Expert 数减少 → 留给 KV Cache 的显存增大 → 可缓存 token 数增加。
  - MLA 特性 + 更小的 TP Size → KV Cache 冗余下降 → 同样可缓存更多 token。

- **EP Level 1 的数据流（原文）**：
  - 触发条件：EP 启用（默认即为 Level 1）。
  - 计算路径：先计算 Attention，再计算 MoE。
  - 通信操作：计算完成后使用 **All Gather** 在所有设备间同步数据，再送往下一阶段（pipeline 意义上的下一 stage）。
  - 示例配置：64 卡下 `Attention: dp32tp2, MoE: ep32tp2`（参看 `figures/moe_eplevel1.jpg`）。

- **EP Level 2 的数据流（原文）**：
  - 触发条件：`ep_size == 设备总数` 且 `expert_parallel_degree = 2`。
  - 通信变更：Attention 与 MoE 之间的通信由 All Gather 替换为 **All-to-All**，只把数据发往真正需要的设备。
  - 收益：减少通信数据量、降低通信开销（参看 `figures/moe_eplevel2.jpg`）。

- **EP 对硬件利用率的提升机制（原文）**：大规模 EP 下，同一 Expert 对应的 token 计算被汇聚到同一设备上执行，提升整体硬件利用率。

> 注：原文未提供具体的性能数字（如吞吐、时延、显存节省百分比等），以上仅为机制层面的描述，未做超出原文的量化。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **关联到的模型/特性**：
  - **DeepSeek-R1**：本文档以部署该 671B 模型为动机背景，说明 EP 设计的实际应用对象。
  - **MLA（Multi-Latent Attention）**：在介绍 EP 第二个优势时被显式引用——正是 MLA 的特性使得"更小 TP Size ⇒ 更少 KV Cache 冗余"这一收益成立。
  - **MoE（Mixture of Experts）**：EP 的直接作用对象，`ep_size` 即控制 MoE 部分的专家并行规模。
  - **TP（Tensor Parallel）**：当 `dp_size` 或 `ep_size` 不等于设备总数时，在 DP 组内退化为 TP 并行，构成与 EP 协同的张量并行通道。
  - **Attention 部分的 DP（Data Parallel）**：`dp_size` 控制 Attention 端的数据并行。
- **图示资源**：
  - `figures/moe_eplevel1.jpg`：对应 EP Level 1（All Gather）64 卡示例。
  - `figures/moe_eplevel2.jpg`：对应 EP Level 2（All-to-All）64 卡示例。
- **内部链接**：原文未提供内部链接。

---

## 【使用方法】

依据原文「Parameter Configuration」章节：

| 参数 | 作用范围 | 默认值 | 取值约束 |
|---|---|---|---|
| `dp_size` | Attention 部分的数据并行 | `1` | 2 的幂次；不等于设备总数时，DP 组内启用 TP |
| `ep_size` | MoE 部分的专家并行 | `1` | 2 的幂次；不等于设备总数时，DP 组内启用 TP |
| `expert_parallel_degree` | EP 等级开关 | `0`（关闭） | 开启 EP 时默认 `1`（Level 1）；`ep_size == 设备总数`时可设为 `2` 启用 Level 2 |

- **启用 EP**：将 `expert_parallel_degree` 从 `0` 调整为 `1`（默认即 Level 1），并按需设置 `dp_size` / `ep_size`（建议为 2 的幂次）。
- **升级到 EP Level 2**：在 `ep_size` 等于总设备数的前提下，将 `expert_parallel_degree` 设为 `2`，此时 Attention↔MoE 通信自动切换为 All-to-All。
- **典型 64 卡配置（原文示例）**：Level 1 时使用 `Attention: dp32tp2, MoE: ep32tp2`；Level 2 时按对应示意图调整。
- 原文未涉及具体的命令行、配置文件路径或 API 调用形式，仅给出参数语义。

## 图文联合解读

- `moe_eplevel1.jpg`: **图示结构**：顶部Schedule接收KVCache Block Manager调度，纵向展示64卡（DP32×TP2）混合并行：每列NPU含EMB→MLA(TP2)→MLP(TP2)循环3次的ATTN段（DP32,TP2），经All Gather后接58层MOE段（EP32,TP2）的"8+1+1"专家模块，末尾再All Gather收尾。

**技术结论**：Attention部分采用DP32+TP2小切分以降低KV Cache冗余；MoE部分通过EP32将256专家分散部署并配合AllGather通信汇集token，验证"小TP省缓存、大EP聚计算"的设计。

**与文档呼应**：直观对应文档中dp_size=32、ep_size=32、TP2的参数配置，并佐证MLA特性+大EP部署带来的KV扩展与硬件利用率优势。
- `moe_eplevel2.jpg`: **图文联合解读：**

图示64卡NPU按**DP64+EP64混合并行**排布：每卡承载EMB+3层MLP+58层MLA（均TP1）走Attention，经ALL2LL切换至MoE（4+1+1专家，EP64），再ALL2LL回流，由Schedule与KVCache Block Manager协同调度。

**技术结论：** EP Level 1下，Attention与MoE解耦并行——前者以数据并行处理，后者以专家并行使同一专家的token集中于同卡，减少冗余KV Cache并提升硬件利用率。

**与文档论点对应：** 可视化印证了"每卡专家少→腾出内存给KV Cache""MLA+小TP→KV Cache无冗余""大EP→同专家集中本卡→提升利用率"三条核心优势。
