# Seqpack

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/seqpack.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/seqpack.md

# Seqpack 文档深度解读

## 【定位】
本篇文档描述 Seqpack 功能：通过将多条异构长度的多模态样本拼接成接近 `max-seq-len` 的批次，并以 TND layout 模式送入模型，从而在多模态大模型训练中同时解决**「批次内 padding 显存浪费」**与**「DP 组间 token 数量负载不均」**两个问题。

---

## 【技术要点】

1. **核心问题诊断**：训练多模态大模型时，输入序列长度因**图像 token 数量**与**文本长度**的差异呈现高度异构性。传统按批次内最大长度 padding 的方式造成显存浪费，且未考虑 DP 组间 token 数量关系，容易引入**卡间负载不均**。
2. **核心机制——序列拼接成近似 `max-seq-len`**：将多条序列拼接成总长近似 `max-seq-len` 的批次，作为一个 batch 输入模型；模型以 **TND layout** 模式处理拼接后的数据。
3. **核心机制——buffer 弹出式拼接**：为保证有足够可选样本进行拼接，采用 **buffer 存储**待拼接数据；拼接时从 buffer 内**弹出**能够组合成长度近似 `max-seq-len` 的序列批次。
4. **运行后端**：当前通过基于 Megatron 的 FSDP2（即 **megatron-FSDP2**）后端使用；文档明确标注**该路线为过渡方案，后续将逐步退出**。
5. **支持模型示例**：文档以 **Qwen3 VL** 模型为例给出配置。
6. **三参数开关与默认值**：`use_txt_dynamic_batching`（默认 `false`，开启 Seqpack）、`max_seq_len`（默认 `2048`）、`dynamic_batch_buffer_size`（默认 `200`）。

---

## 【关键机制与数据】

**工作原理与数据流（依原文）：**

- **原文：「**将多条序列拼接成近似于 `max-seq-len` 的长度，并将拼接后的数据作为一个批次数据输入模型，模型以 TND 的 layout 模式处理拼接后的数据。**」**
  → 输入侧：多条原始序列 → 拼接为总长 ≈ `max-seq-len` 的单 batch；模型侧：以 **TND layout** 处理拼接结果。
- **原文：「**为确保有足够可选择的样本用于序列拼接，采用 `buffer` 存储数据，在拼接序列过程中，从 `buffer` 内弹出能够拼接成长度近似于 `max-seq-len` 的序列批次。**」**
  → 数据流：原始样本持续进入 `buffer` → 拼接逻辑从 `buffer` 中按"近似 `max-seq-len`"的目标弹出样本组合 → 形成 batch 送入模型。
- **原文：「**这样一来，每张卡上的 token 总数一致，在节约 padding 的显存的同时，均衡卡间数据负载。**」**
  → 效果声明两点：① 每张卡上 token 总数一致（消除 DP 组间负载不均）；② 减少 padding 带来的显存浪费。
- **原文中可标注的性能/量化数据**：除上文提到的 `max_seq_len` 默认 `2048`、`dynamic_batch_buffer_size` 默认 `200` 外，文档**未给出具体的显存占用、训练吞吐、加速比等性能数字**。

---

## 【表格解读】

**原文无表格。**（原文档以正文段落与代码块呈现，无任何 markdown 表格或对比表。）

---

## 【公式解读】

**原文无公式。**（文档未给出任何 LaTeX 公式、伪代码公式或符号化定义。唯一接近"参数化"的内容为配置项 `max_seq_len` 与 `dynamic_batch_buffer_size`，但它们是配置项数值而非数学公式。）

---

## 【关联】

本篇文档原文**未提供任何内部链接**，文末的"内部链接"标注为「（无）」。基于文档正文中提及的若干线索，可推断如下关联关系（非新增事实，仅复述原文出现的信息）：

- **运行后端**：与 **Megatron-FSDP2** 后端耦合运行；文档声明该路线为**过渡方案，后续将逐步退出**，意味着该特性后续将迁移至其他后端实现。
- **支持模型**：以 **Qwen3 VL** 作为示例模型；该特性适用于多模态大模型（含图像 token + 文本 token 输入）。
- **下游处理**：拼接后的数据以 **TND layout** 模式进入模型，即与依赖 TND 数据布局的模型组件/算子存在数据契约关系（文档未给出具体算子或模块名）。
- **上下文**：篇名为 `Seqpack`，归属于多模态训练 feature 类别（`docs/zh/features/`），与同目录下其他多模态训练相关特性在文档体系上并列（具体并列项原文未列出）。

---

## 【使用方法】

**启用方式（原文有）：** 在 **Qwen3 VL 模型**配置文件的 `gpt_args` 段设置以下参数：

```shell
gpt_args:
    ....
    use_txt_dynamic_batching: true
    max_seq_len: MAX_SEQ_LEN
    dynamic_batch_buffer_size: BUFFER_SIZE
```

**配置项（原文有）：**

| 参数名 | 作用 | 默认值 |
|---|---|---|
| `use_txt_dynamic_batching` | seqpack 的开关；设置为 `true` 视为开启 seqpack 功能 | `false` |
| `max_seq_len` | 设定拼接后序列的长度（即拼接目标总长） | `2048` |
| `dynamic_batch_buffer_size` | `buffer` 的大小（用于存放待拼接样本的缓冲区容量） | `200` |

**补充说明（依原文）：** 当前 SeqPack 需通过 **megatron-FSDP2** 后端使用；该后端为**过渡方案，后续将逐步退出**。文档未涉及其他启用方式、命令行参数、或者不同模型的差异化配置写法。
