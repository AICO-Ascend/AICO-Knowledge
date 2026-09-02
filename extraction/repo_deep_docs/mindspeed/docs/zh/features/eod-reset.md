# 支持EOD Reset训练场景

> 仓 `mindspeed` · 路径 `docs/zh/features/eod-reset.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/eod-reset.md

# 文档深度解读：mindspeed EOD Reset 训练场景

---

## 【定位】

本文档描述 mindspeed 昇腾大模型加速库如何在**多文档拼接为同一序列**的训练场景下，让不同文档之间的 self-attention 互相独立（即在每个文档结束 EOD 位置重置 attention mask 与 position ids），并在此基础上叠加 Ring Attention 长序列并行能力。

---

## 【技术要点】

1. **触发场景**：一个序列由多个 doc 拼接而成时，默认 doc 之间不做 attention 掩码；开启 EOD Reset 后，需在每个文档末尾（EOD 处）重置 attention mask 和 position ids，使文档之间 self-attention 互相独立。
2. **底层算子**：通过调用底层 **flash-attention 算子的可变长（variable-length）模式** 实现 EOD Reset 训练，长序列并行进一步叠加 **Ring Attention**。
3. **关键开关 ① `--reset-attention-mask`**：打开后启用文档间 attention mask 重置。
4. **关键开关 ② `--reset-position-ids`**：关闭时整段序列统一计算位置编码；开启时**在每个序列内独立**计算位置编码。
5. **关键开关 ③ `--attention-mask-type`**：可指定为 `causal` 或 `general`，**两者计算结果等价**——`causal` 是加速实现，`general` 是基线方案。
6. **`causal` 模式的在线 pad 约束**：当 `--attention-mask-type=causal` 时，因内部实现需求，**每个子序列的长度会被在线 pad 到 `CP * lcm(2, TP)` 的倍数**（lcm 为最小公倍数），因此该场景必须开启 `--variable-seq-lengths`。
7. **数据前置条件**：每个文档的末尾都需**预先添加 EOD Token**。
8. **性能现象（Ascend 平台）**：mask-type=`general` 时，Ring/Hybrid Attention 比 Ulysses 性能下降较多（原文标注为"正常现象"）；mask-type=`causal` 时使用加速方案。

---

## 【关键机制与数据】

### 工作原理（原文整合）

- **默认行为**：多个 doc 拼接为同一序列后，doc 之间不做 self-attention 掩码，position id 沿整段序列连续累加。
- **EOD Reset 行为**：
  - 在每个 doc 的结束位置（EOD）处**重置 attention mask** → 阻止跨文档的 self-attention；
  - 在每个 doc 的结束位置（EOD）处**重置 position id**（受 `--reset-position-ids` 控制）→ 每个文档内独立从 0 开始计算位置编码。
- **算子实现路径**：调用 flash-attention 的 **variable-length（可变长）模式**，从而天然支持"同一序列内多段子序列各自独立 attention"的需求。
- **长序列扩展**：在 EOD Reset 场景之上叠加 **Ring Attention 长序列并行**，对超长序列做进一步加速。

### 性能/选型数据（原文摘录）

| 来源 | 现象 | 原文表述 |
|------|------|----------|
| 原文 NOTE | Ascend + mask-type=`general` 下，Ring/Hybrid Attention 比 Ulysses 下降较多 | "为正常现象" |
| 原文 NOTE | Ascend + mask-type=`causal` | "使用加速方案" |
| 原文 Usage | causal 模式的内部 pad 规则 | "每个子序列的长度会被在线 pad 到 `CP*lcm(2, TP)` 的倍数" |

> 原文未给出具体的加速倍数、吞吐数据或基准测试数字，故不臆造。

---

## 【表格解读】

**原文无表格**。

（文档内容以文字段落、参数说明与一条 NOTE 提示组成，未包含任何 markdown 表格。）

---

## 【公式解读】

**原文无公式**。

（文档中未给出任何 LaTeX 或伪代码形式的数学公式；唯一涉及数值表达的是参数说明中的 `CP*lcm(2, TP)`，但其作为配置约束以文字描述形式给出，不构成独立公式。）

---

## 【关联】

本文档为 mindspeed 长序列/注意力并行训练特性的细分文档。涉及到的**内部特性模块关联**如下（依据原文表述提炼）：

1. **flash-attention 算子（可变长模式）**——EOD Reset 的底层算子实现依赖项；EOD Reset 通过其 variable-length 能力实现文档间 attention 隔离。
2. **Ring Attention（长序列并行）**——在 EOD Reset 训练场景之上叠加使用，专门面向"超长序列"加速。
3. **Ulysses（序列并行方案）**——文中作为 Ring/Hybrid Attention 的对比基线被提及，用于说明在 Ascend + mask-type=`general` 下的性能差异现象。
4. **`--variable-seq-lengths` 配置项**——并非 EOD Reset 独有，但在 `--attention-mask-type=causal` 模式下因引入在线 pad、序列长度发生变化而被强制要求开启。
5. **attention mask type（causal / general）**——作为通用参数被复用，本文档约定其两种取值在 EOD Reset 下结果等价、仅在性能/实现路径上有差异。

> 原文未提供文末"相关特性链接"列表，内部链接字段为空（`(无)`），故上述关联完全来自正文中提及的其他特性/模块名称。

---

## 【使用方法】

### 1. 数据准备（原文 Step 1）

- 确保**每一个文档的末尾都添加了 EOD Token**。
- 若 `--attention-mask-type=causal`：
  - 因内部实现会做在线 pad，使每个子序列长度对齐到 `CP * lcm(2, TP)` 的倍数；
  - 因此**必须开启 `--variable-seq-lengths`**（pad 会改变序列长度）。

### 2. 参数设置（原文 Step 2）

| 命令行参数 | 取值/作用 | 原文表述 |
|------------|-----------|----------|
| `--reset-attention-mask` | 打开 | "打开 `--reset-attention-mask` 选项" |
| `--reset-position-ids` | 决定位置编码是否 reset | "使用 `--reset-position-ids` 选项，来代表位置编码是否 reset" |
| `--attention-mask-type` | `causal` 或 `general`（两者等价；causal 为加速实现，general 为基线方案） | "可以指定为 causal 或者 general，两者计算结果等价。causal 为加速实现，general 为基线方案" |
| `--variable-seq-lengths` | causal 模式下必须开启 | "该场景需要开启 `--variable-seq-lengths`，因为 pad 会使得序列长度发生变化" |

### 3. 选型建议（原文 NOTE）

- **Ascend 平台 + mask-type=`causal`**：使用加速方案。
- **Ascend 平台 + mask-type=`general`**：Ring/Hybrid Attention 比 Ulysses 下降较多为正常现象，可按需选择 Ulysses 或 Hybrid 方案。
