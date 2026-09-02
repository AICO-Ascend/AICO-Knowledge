# matmul_add融合优化

> 仓 `mindspeed` · 路径 `docs/zh/features/npu_matmul_add.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/npu_matmul_add.md

# mindspeed `matmul_add` 融合优化 — 一体化深度解读

---

## 【定位】

本文档描述 MindSpeed（昇腾大模型加速库）针对**大模型训练中梯度累加环节效率较慢、Add 算子占比偏高**这一瓶颈所提供的能力：将 `matmul` 操作与 `add`（累加）操作融合为单一算子 `npu_matmul_add`，从而在 LLaMA / GPT 类大模型训练中削减显式 Add 算子开销并提升训练吞吐。

---

## 【技术要点】

1. **融合对象**：将独立的 `matmul` 矩阵乘法算子与后续 `add` 累加算子融合为一个算子（`npu_matmul_add`），算子接口详见 `../ops/npu_matmul_add.md`。
2. **优化目标场景**：模型训练中开启了梯度累加（gradient accumulation）、且其中 Add 算子占比较高导致累加效率较慢的场景。
3. **依赖组件**：使能该融合算子**必须安装 ATB（Ascend Transformer Boost）**，参见 `../user-guide/install_guide.md`。
4. **使能方式**：在启动命令中**去掉 `--no-gradient-accumulation-fusion`** 即可调用 Matmul_Add 融合算子。
5. **限制项（精度）**：融合算子与小算子之间存在一定精度差异；根本原因是小算子链路中 `fp32→bf16→fp32` 的"降—升精度"会损失精度，而融合算子跳过该降升过程直接累加。
6. **限制项（统计）**：**`npu_matmul_add_fp32` 暂不支持 MFU（Model FLOPS Utilization，模型算力利用率）统计**。

---

## 【关键机制与数据】

### 工作原理与数据流

- **问题侧（原文）**：模型训练开启梯度累加时，累加效率较慢，**Add 算子占比偏高**——也就是单独调度一个 Add 算子执行累加的开销可观。
- **解决侧（原文）**：MindSpeed 将 `matmul` 与紧随其后的 `add` 合并为**一个融合算子**，跳过中间多余的精度转换与算子调度。
- **精度链路差异（原文）**：文档明确给出两类 dtype 变化路径（小算子 vs 融合算子，见下方【公式解读】）。核心差异在于小算子路径在 matmul 完成后会**先降精度（fp32→bf16）再升精度（bf16→fp32）**后才进行 add；而融合算子**直接在 fp32 上累加**，因此保留更高精度但数值结果与小算子存在差异。

### 性能数据

- **原文**：「在内存未占满的情况下，开启 Matmul_Add 融合算子，模型训练的性能将得到提升，**在 Llama-2-7b 模型下，性能增益约 2%**。」
- **生效前提（原文）**：「在内存未占满的情况下」——即融合算子并非在所有内存状态下都给出收益。

---

## 【表格解读】

**原文无表格。**

（原文主要以说明性文字 + 两条 dtype 变化伪公式呈现，无参数表、配置项表或性能对比表。）

---

## 【公式解读】

原文包含**两条 dtype 变化过程的伪公式**（原文以等式/箭头形式书写，并非数学意义公式，而是"算子内 dtype 走向"的描述），逐字保留如下：

### 公式 1：小算子的 dtype 变化过程

$$
\texttt{bf16} \times \texttt{bf16} = \texttt{fp32} \;\to\; \texttt{bf16} \;\to\; \texttt{fp32} + \texttt{fp32} = \texttt{fp32}
$$

**符号与作用解释（按出现顺序）**：

- `bf16 × bf16 = fp32`：两个 bf16 输入矩阵相乘，结果按硬件约定累加到 **fp32**（这是 matmul 算子内部的常规精度提升）。
- `→ bf16`：matmul 的 fp32 结果**被降精度到 bf16**（典型地是为与下游张量 dtype 对齐，或为节省存储/带宽）。
- `→ fp32`：紧接着又**升精度回 fp32**，准备与累加项相加。
- `+ fp32 = fp32`：在 fp32 上做加法完成累加。

> 文档指出，这一步 "**先降再升**" 会损失一部分精度——这是融合算子与原小算子产生数值差异的**根本原因**。

### 公式 2：融合算子的 dtype 变化过程

$$
\texttt{bf16} \times \texttt{bf16} = \texttt{fp32} + \texttt{fp32} = \texttt{fp32}
$$

**符号与作用解释**：

- `bf16 × bf16 = fp32`：同样，两个 bf16 矩阵相乘得到 fp32 累加器。
- `+ fp32 = fp32`：**跳过中间 fp32→bf16→fp32 的降升精度往返**，直接在 fp32 上完成与累加项的加法。
- 因此融合算子的累加结果**不会引入额外的舍入误差**，但与原小算子链路产生的 fp32 结果数值上**不完全相等**——这是文档明确声明的"精度差异"。

> 两个公式的对比，直观地揭示了融合算子的优化点：**消除冗余的精度往返**，减少了一次降精度与一次升精度操作，并省去了对应的算子调度与访存开销。

---

## 【关联】

- **算子实现层**（下游）：本文所述融合算子的接口与详细说明指向 `../ops/npu_matmul_add.md`——即 `npu_matmul_add` 算子页是该 feature 的真正"落地点"，本文档只是 MindSpeed 中的 feature 介绍与启用指南。
- **环境依赖层**（上游/前置）：使能该融合算子需要安装 ATB（Ascend Transformer Boost），安装入口为 `../user-guide/install_guide.md`——`install_guide.md` 是本 feature 启用之前的必读依赖说明。
- **训练流水线层（语义关联）**：本文针对的是**梯度累加（gradient accumulation）**环节中的 Add 算子优化，因此它与 MindSpeed 中负责梯度累加的逻辑紧耦合；控制开关正是 `--no-gradient-accumulation-fusion`（去掉该 flag 即开启融合）。
- **适用模型范围**：文档明确指出 **LLaMA 及 GPT 大模型均可使用**，因此该 feature 属于 MindSpeed 在主流 dense Transformer 类大模型训练中的通用优化。

---

## 【使用方法】

> 以下内容均直接来源于原文，未做引申。

### 1. 前置条件（原文）

> "融合算子使能要求安装 ATB（Ascend Transformer Boost），请参考[软件安装](../user-guide/install_guide.md)完成安装。"

即必须先按 `install_guide.md` 完成 **ATB** 的安装。

### 2. 启用命令（原文）

> "去掉 `--no-gradient-accumulation-fusion` 即可调用 Matmul_Add 融合算子。"

含义：在 MindSpeed 训练启动参数中，**移除 `--no-gradient-accumulation-fusion` 这一禁用开关**，融合算子即被调用；反之若显式带上该 flag，则回退到未融合的小算子链路。

### 3. 注意事项（原文）

- `npu_matmul_add_fp32` **暂不支持 MFU 统计**，在意 Model FLOPS Utilization 指标的流水线需注意。
- 融合算子与小算子之间存在**一定精度差异**（参见【公式解读】中两条 dtype 路径差异）。
- 性能增益的**生效前提**为「内存未占满」：原文未给出"内存占满"的判定阈值与具体配置项，故此处不臆造。
