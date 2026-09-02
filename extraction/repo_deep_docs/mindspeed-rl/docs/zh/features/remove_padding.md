# 特性说明

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/remove_padding.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/remove_padding.md

# 一体化深度解读：mindspeed-rl `remove_padding.md`

---

## 【定位】

本文档系统介绍了昇腾强化学习加速库 `mindspeed-rl` 中三项为大语言模型训练服务、用于**加速计算并节省显存**的关键特性——**填充移除（Remove Padding）**、**动态批量大小（Dynamic Batch Size）** 与 **数据并行负载均衡（DP Batch Balance）**，并给出各自的实现原理、参数约束与配置方式。

---

## 【技术要点】

1. **Remove Padding（填充移除）**：在预处理阶段移除每条样本的 padding，将所有有效 token 拼接为一条长序列，记录每个子序列的"起始位置 + 长度"用于后处理还原；前向阶段构造 attention mask 或借助 FlashAttention 自动生成；后处理阶段按记录信息将 logits 拆解回原始样本维度。配套配置项：`megatron_training.no_pad_to_seq_lengths=true`、`megatron_training.reset_attention_mask=true`、`rl_config.use_remove_padding=true`。

2. **Dynamic Batch Size（动态批量大小）**：在 `remove_padding` 拼接后，以 `max_packing_token_size` 为上限，对一个 batch 内每条样本的 `prompt_length + response_length` 进行分组，使每个 micro batch 拼接后的 token 总数不超限；分组算法采用 **Karmarkar-Karp 近似平衡分组算法**；分布式场景下对 `max_packing_token_size` 通过广播同步，保证各 rank 划分一致。

3. **DP Batch Balance（数据并行负载均衡）**：在数据并行训练中，先收集当前批次所有样本序列长度，再以**堆排序装箱算法**按长度从大到小依次装入当前总长度最小的分组，使各 DP 节点总序列长度均衡，缓解"木桶效应"。

4. **核心约束**（原文）：`prompt_length[i] + response_length[i] <= max_packing_token_size`，否则无法装入单一 micro batch。

5. **建议取值公式**（原文）：`max_packing_token_size = (rl_config.max_prompt_length + generate_config.sampling_config.max_tokens) * 2`，即序列最大长度的 2 倍。

6. **辅助参数与限制**（原文）：`ref/actor/update_dynamic_max_batch_size` 用于控制 Dynamic batch size 分箱后每个 micro batch 的最大**序列条数**（避免长序列场景下 micro batch size 过大造成 OOM），可选；最小建议值 2，设为 1 则 Dynamic Batch Size 失去意义。

---

## 【关键机制与数据】

**整体数据流（三特性递进关系，原文）：**

```
原始不等长序列
  ↓  [特性 1: Remove Padding]
    预处理：移除 padding → 拼接有效 token → 记录子序列起止
    前向：拼接长序列 + 构造 attention mask（或借助 FlashAttention）
    后处理：按记录还原 logits 到原样本维度
  ↓  [特性 2: Dynamic Batch Size]（防止拼接后 OOM）
    计算每条 prompt_length + response_length
    Karmarkar-Karp 近似平衡分组 → 划分 micro batch
    约束：每组总 token ≤ max_packing_token_size；可选每组序列条数 ≤ *_dynamic_max_batch_size
    分布式：max_packing_token_size 跨 rank 广播同步
  ↓  [特性 3: DP Batch Balance]（均衡数据并行各 rank 负载）
    收集当前批次所有样本序列长度
    堆排序装箱：按从大到小依次装入当前总长度最小的分组
    分配到各 DP 节点 → 各节点计算量均衡
```

**原文性能/数据说明**：
- 原文未给出实测加速比、显存节省比例、吞吐量数字等量化性能数据。
- 原文仅以定性方式说明 Remove Padding "消除了 padding token 带来的资源浪费，提升了训练效率"；Dynamic Batch Size 在"保持高吞吐的同时，有效避免显存溢出"；DP Batch Balance "减少节点间等待时间，提升分布式训练效率"。
- 文档配图 3 张（均为引用，未在文中给出参数化说明）：`packing.png`（拼接示意）、`attention_mask.png`（attention mask 构造）、`dp_balance.png`（DP 装箱示意）。

---

## 【表格解读】

> **原文无表格**。
>
> 文档未提供任何 markdown 表格（参数表 / 性能对比表 / 配置项总览表均无）。所有参数、约束、配置均以 YAML 代码块或纯文本形式给出（已在上文【技术要点】与【使用方法】中按原文逐字保留）。

---

## 【公式解读】

原文无 LaTeX 公式，仅给出两段**伪代码形式**的文本公式，逐字保留并解读如下：

**式 ① — 单样本装入约束**（原文 `prompt_length[i] + response_length[i] <= max_packing_token_size`）

- `prompt_length[i]`：batch 中第 `i` 条样本的 prompt（提示）token 长度。
- `response_length[i]`：该样本 response（响应）token 长度。
- `max_packing_token_size`：动态批大小机制对每个 micro batch 拼接后 token 总数的上限。
- 作用：**硬性约束**——任意单条样本的 prompt 与 response token 总和不得超过 `max_packing_token_size`，否则无法被装入任何一个 micro batch 分组。

**式 ② — 推荐取值公式**（原文 `max_packing_token_size = (rl_config.max_prompt_length + generate_config.sampling_config.max_tokens) * 2`）

- `rl_config.max_prompt_length`：RL 配置中允许的最大 prompt 长度。
- `generate_config.sampling_config.max_tokens`：生成配置中采样阶段允许生成的最大 token 数（即 response 最大长度）。
- 二者相加代表"单条样本序列可能的最大总长"；乘以 `* 2` 即"序列最大长度的 2 倍"。
- 作用：**建议值**——为 `max_packing_token_size` 提供经验取值，以便在典型 RL 训练场景下兼顾吞吐与显存。

> 文档不包含其他数学公式（如 Karmarkar-Karp 或堆排序装箱的算法伪代码、FlashAttention 数学定义等），相关算法名称仅在文字叙述中出现。

---

## 【关联】

文档开篇即声明三项特性属于同一组合并介绍，**核心因果链**如下：

1. **Remove Padding → Dynamic Batch Size**：Remove Padding 通过拼接消除 padding，但无限制拼接可能触发 OOM；Dynamic Batch Size 正是为 Remove Padding 的拼接结果提供"micro batch 切分 + token 上限 + 序列条数上限"三重保险，二者**强耦合**。
2. **Dynamic Batch Size → DP Batch Balance**：Dynamic Batch Size 在单个 batch 内做 micro batch 切分；DP Batch Balance 进一步在**数据并行的多个 rank 之间**做装箱均衡，二者分别位于"批内"与"跨节点"两个层级，**正交互补**。
3. **三者 → RL 训练整体流程**：均通过 `rl_config.*` 字段启用，配合 `megatron_training.no_pad_to_seq_lengths` / `reset_attention_mask` 等 Megatron 侧参数共同生效，作用于 RL 训练中的 `ref`（参考模型）、`actor`（策略模型）、`update`（更新阶段）三类典型计算位置（见 `ref_/actor_/update_` 前缀参数）。

> 文档内部链接信息：原文未提供任何内部链接（无章节交叉引用、无相关文档锚点）。

---

## 【使用方法】

**通用启用开关**：`rl_config` 下三个独立布尔开关 `use_remove_padding`、`use_dynamic_bsz`、`use_dp_batch_balance`，可按需启用其中一项或多项。

### 1) Remove Padding（原文 yaml）
```yaml
megatron_training:
  no_pad_to_seq_lengths: true
  reset_attention_mask: true

rl_config:
  use_remove_padding: true
```

### 2) Dynamic Batch Size（原文 yaml，参数值 8192 / 8 均为示例）
```yaml
rl_config:
  use_dynamic_bsz: true
  ref_max_packing_token_size: 8192
  ref_dynamic_max_batch_size: 8     # 可选参数
  actor_max_packing_token_size: 8192
  actor_dynamic_max_batch_size: 8   # 可选参数
  update_max_packing_token_size: 8192
  update_dynamic_max_batch_size: 8  # 可选参数
```

原文对 `*_dynamic_max_batch_size` 的调参指引：若长序列训练在**计算 logits 之后**仍发生显存溢出，可调小该值以减少显存占用；**最小建议值为 2**，设为 1 则 Dynamic Batch Size 无意义。

### 3) DP Batch Balance（原文 yaml）
```yaml
rl_config:
  use_dp_batch_balance: true
```

> 注 — 上述 `8192`、微批序列条数 `8` 均为原文给出的 YAML 示例值，**非性能基准**；文档未提供推荐硬件/规模下的调优对照表。
