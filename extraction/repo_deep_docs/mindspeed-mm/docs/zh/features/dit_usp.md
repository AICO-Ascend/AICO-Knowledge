# Ulysses SP混合序列并行（Ulysses + RingAttention）

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/dit_usp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/dit_usp.md

# 深度解读：Ulysses SP 混合序列并行（Ulysses + RingAttention）

---

## 【定位】

本文档描述 mindspeed-mm 中面向长序列训练场景的 Ulysses + RingAttention 混合序列并行方案，回答"在视频生成等长上下文任务中如何对序列维度做并行扩展、降低单卡内存压力"的问题。

---

## 【技术要点】

- **核心思路**：Ulysses 将样本在**序列维度**上切分到多个计算设备上，配合 all-to-all 通信使各设备在计算 attention 时持有完整序列、但只覆盖**非重叠的注意力头子集**，从而并行计算不同注意力头并最终在两个维度上完成重组。
- **触发场景**：当视频分辨率 / 帧数设置很大、单卡无法完成 DiT 计算时开启 DiT-RingAttention（与本文档配套的序列并行能力）。
- **关键启动参数**（在 `pretrain.sh` 中）：
  - `CP=8`（示例值，控制 context-parallel 总规模）
  - `--context-parallel-size ${CP}`
  - `--context-parallel-algo hybrid_cp_algo`
  - `--use-cp-send-recv-overlap`（可选，建议开启 → 支持 send/recv overlap）
  - `--ulysses-degree-in-cp [int]`
  - `--megatron-cp-in-bnsd`（可选，建议开启，切换为 `[B, N, S, D]` layout）
  - `--attention-mask-type [str]`（取值 `general` / `causal`）
- **整除约束**（关键工程限制，原文明确给出）：
  - `--context-parallel-size` 必须能被 `--ulysses-degree-in-cp` 整除且大于 1；例如 `CP=8` 时，`--ulysses-degree-in-cp` 可取 2 或 4。
  - `num-attention-heads` 必须能被 `--ulysses-degree-in-cp` 整除。
- **性能特性**（定性，原文表述）：通过多设备并行切分输入序列降低单设备内存消耗；同时**单步耗时相比不开序列并行会增加**；**相比重计算（recomputation）计算效率有提升**。
- **外部实现参考**：方法来自微软 DeepSpeed Ulysses（文末给出 GitHub 项目地址作为鸣谢）。

---

## 【关键机制与数据】

**工作原理（Ulysses 数据流，原文要点整合）：**

1. **序列切分**：Ulysses 将每个样本的序列维度（`S`）切分到参与并行的 N 台计算设备上，每台设备只持有完整序列的一个分片。
2. **第一次 all-to-all（attention 之前）**：对已切分的 Q、K、V 执行 all-to-all，交换的目标是让**每台设备拿到完整的序列**，但**只覆盖全部注意力头的一个非重叠子集**。这样 N 台设备可以并行计算不同的 head。
3. **attention 计算**：每台设备在自己的 head 子集上独立完成 attention 计算（含所需的 mask 规则，由 `--attention-mask-type` 控制）。
4. **第二次 all-to-all（attention 之后）**：再执行一次 all-to-all，把各设备算完的 head 结果在 head 维度汇聚，同时**重新在序列维度上做分区**，还原出"按 head 完整、按序列分片"的输出布局，供后续模块继续使用。

**关键数据 / 性能数据（原文表述，逐字标注）：**

- 原文：**"相比不开启序列并行单步耗时增加"** —— 即开启序列并行后会带来通信与切分开销，单步训练耗时相对无序列并行的基线会变大。
- 原文：**"相比重计算计算效率提升"** —— 即相对于用 activation recomputation 来缓解显存压力的方案，Ulysses 方案在计算效率上更优。
- 原文未给出具体的加速比、显存节省百分比、吞吐量数字、基准 batch size / sequence length 等量化数据，本文不做臆造。

---

## 【表格解读】

**原文无表格**（文档中仅含一段 shell 形式的启动参数示例，未列出 markdown 格式的参数表）。下面对原文以分点方式给出的参数与约束做结构化整理（内容均来自原文，非新增信息）：

| 参数 / 约束项 | 原文内容要点 | 解读 |
|---|---|---|
| `CP=8` | 示例环境变量设置 | 演示用的 context-parallel 总规模，仅作示例，并非硬性要求 |
| `--context-parallel-size ${CP}` | 必设，控制 CP 总度数 | 序列并行的总并行度 |
| `--context-parallel-algo hybrid_cp_algo` | 必设 | 选择 hybrid CP 算法（即 Ulysses + RingAttention 混合） |
| `--use-cp-send-recv-overlap` | 可选，**建议开启** | 开启后支持 send/recv overlap，用通信掩盖延迟 |
| `--ulysses-degree-in-cp [int]` | 必设 | 指定 Ulysses 在混合 CP 中占据的并行度（剩余部分留给 RingAttention 维度） |
| `--megatron-cp-in-bnsd` | 可选，**建议开启** | 默认 `fa_layout` 为 `sbh`；开启后切换到 `[B,N,S,D]` layout，可提升性能 |
| `--attention-mask-type [str]` | 可选 `general` / `causal` | `general` = 全 attention；`causal` = causal attention |
| 约束 1 | `--context-parallel-size` 必须能被 `--ulysses-degree-in-cp` 整除，且 `>1` | 保证 CP 总度数能被 Ulysses 度数整除 |
| 约束 2 | `num-attention-heads` 必须能被 `--ulysses-degree-in-cp` 整除 | 保证 head 能被均匀切到每台 Ulysses 设备上 |
| 约束示例 | `CP=8` 时，`--ulysses-degree-in-cp` 可取 **2** 或 **4** | 给出具体可取值，便于工程配置时验证 |

---

## 【公式解读】

**原文无公式**（既无 LaTeX 也无伪代码公式）。相关的数学/通信动作以文字描述呈现：

- "Q、K、V 执行 all-to-all" — 涉及的是分布式集合通信原语（all-to-all），本质上是一次**重排**（scatter–gather），把按序列切分的数据重排成按 head 切分（或反向）。原文未给出数据量计算或通信量公式，本文不补充。

---

## 【关联】

> 注：原文为独立的 feature doc，**文末未提供任何内部特性/模块的链接**，因此"内部关联"仅基于文中实际出现的引用进行整理；不引入文档之外臆造的上下游。

**文中实际指向的关联（按出现顺序）：**

1. **视频生成 / 长序列任务** — 触发本文方案的上游应用场景。"视频分辨率/帧数设置的很大时，单卡无法完成 DiT 的计算" → 直接对应 mindspeed-mm 中 DiT 模型的训练通路（即文档开头的"使用场景：……开启 DiT-RingAttention"）。
2. **其他并行方法的边界** — 原文明确"现有的数据、张量和流水线等并行方法无法解决序列维度的扩展问题"，说明本文方案是对现有 DP / TP / PP 的**补充（orthogonal）**，而不是替代。
3. **外部算法实现** — 文末鸣谢指向 `github.com/microsoft/DeepSpeed/tree/master/blogs/deepspeed-ulysses`，即本文所描述 Ulysses 机制的原始出处，mindspeed-mm 在此基础上做了与 RingAttention 混合的工程化整合（`hybrid_cp_algo`）。
4. **与 `--megatron-cp-in-bnsd` 的耦合** — 文档提示默认 `fa_layout="sbh"`，开启该参数后会切到 `[B,N,S,D]`，这暗示本文实现与 FlashAttention 的 layout 设置以及 Megatron-LM 的 CP 实现存在交互，但文档本身未给出更多内部模块链接。

---

## 【使用方法】

以下内容**完全来自原文「使用方法」一节**，未做任何改动或外延：

1. **使用场景**
   - 视频分辨率/帧数很大时，单卡无法完成 DiT 的计算，需要开启 DiT-RingAttention。

2. **使能方式** — 修改启动脚本 `pretrain.sh` 中的如下变量：

   ```shell
   CP=8

   GPT_ARGS="
       --context-parallel-size ${CP} \
       --context-parallel-algo hybrid_cp_algo \
       --use-cp-send-recv-overlap \
       --ulysses-degree-in-cp [int] \
       --megatron-cp-in-bnsd \
       --attention-mask-type [str] \
   ...
   "
   ```

3. **逐项说明（原文要点）**
   - `--use-cp-send-recv-overlap`：**可选**，建议开启，开启后支持 send/recv overlap 功能。
   - 整除约束：`--context-parallel-size` 必须能被 `--ulysses-degree-in-cp` 整除且大于 1（例如 `CP=8` 时，`--ulysses-degree-in-cp` 可取 2 或 4）；同时 `num-attention-heads` 也必须能被 `--ulysses-degree-in-cp` 整除。
   - `--megatron-cp-in-bnsd`：**可选**，建议开启，因为默认 `fa_layout` 为 `"sbh"`，开启后可支持 `[B, N, S, D]` 格式计算，性能更优。
   - `--attention-mask-type`：设置 attention 计算时 mask 的类型，可选值为 `general`（全 attention）或 `causal`（causal attention）。

4. **预期效果（原文表述）**
   - 利用多个计算设备对输入序列做并行切分 → 降低单设备内存消耗；
   - 单步耗时相比不开序列并行**增加**；
   - 相比重计算（recomputation）路径**计算效率提升**。

5. **外部参考**
   - DeepSpeed Ulysses：<https://github.com/microsoft/DeepSpeed/tree/master/blogs/deepspeed-ulysses>（原文「鸣谢」节给出）。
