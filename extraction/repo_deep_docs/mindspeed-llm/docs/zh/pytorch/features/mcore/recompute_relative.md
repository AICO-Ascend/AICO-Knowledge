# 重计算

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/recompute_relative.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/recompute_relative.md

# 重计算文档深度解读

## 【定位】
这篇文档描述 MindSpeed-LLM 昇腾 LLM 分布式训练框架为减少大模型训练时 NPU 显存占用所提供的**多种重计算（recompute）策略**及其启用方法，覆盖全量、选择性和激活函数重计算三种粒度。

---

## 【技术要点】

1. **核心目的**：通过丢弃中间激活值并在反向传播时重算，用计算开销换取 NPU 显存节省，以训练更大的模型。

2. **全量重计算（Full Recomputation）**
   - 启用标志：`--recompute-granularity full`
   - 仅保存 Transformer 层或层组的输入激活值，其余全部重新计算
   - 两种分配方法（通过 `--recompute-method` 切换）：
     - **均匀方法（uniform）**：将 Transformer 层按 `--recompute-num-layers` 大小均匀分组，按组保存输入和激活值
     - **分块方法（block）**：仅对前 `--recompute-num-layers` 个 Transformer 层进行重计算，剩余层不重计算

3. **选择性重计算（Selective Recomputation，官方推荐）**
   - 启用标志：`--recompute-granularity selective`
   - 只重计算 Transformer 中的 **`core attention`** 部分
   - 策略：保留"低显存占用但重计算开销高"的激活，重算"高显存占用但重计算开销低"的激活

4. **激活函数重计算（Activation Function Recomputation）**
   - 启用标志：`--recompute-activation-function`
   - 指定层数：`--recompute-activation-function-num-layers ${num}`

5. **组合使用限制（激活函数重计算 + 全量重计算）**
   - 仅 `--recompute-method block` 受支持
   - 任一层不会同时做全重计算和激活函数重计算，二者各做各的类型
   - 执行优先级：**先全量重计算层，后激活函数重计算层**
   - 在流水线并行未开启时：**全重计算层数 + 激活函数重计算层数 = 总层数**

6. **理论算法依据**：Megatron 重计算论文（`https://arxiv.org/abs/2205.05198`）。

---

## 【关键机制与数据】

**工作原理（原文描述）**：

- **全量重计算** 将 Transformer 层分为可重计算的单元组，每个单元只保留入口激活（input activation），单元内部的中间激活全部在反向时按需重算。
- **均匀方法（uniform）**：组数 = ⌈总层数 / `--recompute-num-layers`⌉，每组大小即 `--recompute-num-layers`，存储粒度为"组输入"。
- **分块方法（block）**：重计算段 = 前 N 层（N = `--recompute-num-layers`），其余层保持正常前向，相当于"前缀重计算"。
- **选择性重计算** 针对 `core attention` 这一显存占用大、但重算代价相对偏低的子模块进行精确重算，对其他子模块保留激活，以求在显存节省与重算开销之间取得更好平衡——文档中明确将其标为 **"推荐使用"**。
- **组合模式下的"不重叠"原则**：同一层只能属于全重计算层集合或激活函数重计算层集合，不可两类叠加。
- **组合模式下的"层数封顶"约束**：原文"在流水线并行未开启的情况下，全重计算层数和激活函数重计算层数之和应该等于总层数"，表明该约束依赖非流水线场景；开启 PP 时二者之和与总层数的关系原文未给出。
- **执行顺序**：组合模式下先完成全重计算层，再处理激活函数重计算层，反映二者以独立通道并行/串行调度，避免重复计算。

**性能数据**：原文**未给出**任何显存/吞吐/加速比的量化数字，仅在概念层面描述了"减少内存使用"。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档文末给出了两条外部/内部关联：

1. **算法原理 → Megatron 重计算**
   链接：`https://arxiv.org/abs/2205.05198`
   性质：外部 arXiv 论文，提供重计算策略的理论依据（"以时间换空间"的激活重算机制）。选择性重计算中"按成本/显存权衡决定哪些激活需重算"的思路即源于该论文。

2. **激活函数重计算详细章节 → MindSpeed 主仓文档**
   链接：`https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/activation-function-recompute.md`
   性质：上游 MindSpeed 框架对该能力的单独说明文档。本文档中给出的 `--recompute-activation-function` 与 `--recompute-activation-function-num-layers` 在该章节中应有更详细的适用算子、配置示例与约束，本文档仅作摘要指引。

3. **组合关系 → 全量重计算（`--recompute-granularity full`）**
   文档明确指出激活函数重计算可与**全量重计算**叠加使用，但限制了 `--recompute-method` 只能是 `block`，因此该组合文档内自封闭形成约束链，与同一文档中的"选择性重计算"路径互斥（文档未明示，但参数名均使用 `--recompute-granularity` 互斥取值可推断）。

4. **流水线并行的隐式耦合**
   文档提及"在流水线并行未开启的情况下，全重计算层数和激活函数重计算层数之和应该等于总层数"，暗示该约束与 PP（pipeline parallel）调度相关，需结合 MindSpeed-LLM 的流水线并行文档理解。

---

## 【使用方法】

以下命令/参数均为原文明确给出：

| 配置项 | 取值/说明 | 适用场景 |
|---|---|---|
| `--recompute-granularity full` | 启用全量重计算 | 显存极度紧张 |
| `--recompute-granularity selective` | 启用选择性重计算（推荐） | 一般显存受限时首选 |
| `--recompute-method uniform` | 配合 `full` 使用，层组均匀划分 | 显存极致节省 |
| `--recompute-method block` | 配合 `full` 使用，仅重算前 N 层 | 与激活函数重计算叠加时**唯一允许**的方法 |
| `--recompute-num-layers N` | 配合 `full` 使用，指定每组大小（uniform）或前缀层数（block） | 按层数控制重算粒度 |
| `--recompute-activation-function` | 启用激活函数重计算 | 单独使用或与全量 `block` 组合 |
| `--recompute-activation-function-num-layers ${num}` | 指定激活函数重计算的层数 | 控制激活函数重算覆盖范围 |

**组合用法约束**（原文）：
- 同时开启 `--recompute-granularity full` + `--recompute-activation-function` 时，`--recompute-method` **仅支持 `block`**。
- 同一层不会既属于全重计算又属于激活函数重计算。
- 执行顺序：全重计算层先，激活函数重计算层后。
- 非流水线并行场景下：`全重计算层数 + 激活函数重计算层数 == 总层数`。
