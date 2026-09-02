# 高维张量并行

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/tensor_parallel_2d.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/tensor_parallel_2d.md

# 高维张量并行 (tensor_parallel_2d) 文档深度解读

---

## 【定位】

这篇文档针对昇腾LLM分布式训练框架中**2D张量并行（TP-2D）**特性的使用方法进行说明，描述了在超大集群与超大TP域场景下（如 A3 训练 llama3-405B、TP=16），如何通过二维切分（x 轴 × y 轴）替代传统一维张量并行来切分权重与计算，并配合通信-计算重叠/融合算子实现加速的工程化配置方式。

---

## 【技术要点】

1. **2D 张量并行开启三件套**：通过 `--tp-2d` 启用开关，配合 `--tp-x N1` 和 `--tp-y N2` 分别设定 x、y 轴切分维度，需满足 `tp = N1 × N2` 且 `N1 > 1`、`N2 > 1`。
2. **典型推荐配置**：原文中以 `llama3-405B / TP=16` 为例，给出 `tp-x=8`、`tp-y=2` 的推荐组合（即 8×2 的二维切分）。
3. **forward 通信-计算隐藏三选一**：提供 `--enable-overlap-ag-with-matmul`（all-gather 通信与 matmul 重叠）、`--enable-overlap-matmul-with-rs`（matmul 与 reduce-scatter 重叠）、`--coc-fused-kernel`（计算-通信算子级融合）三项，**三者只能同时开启 1 个**。
4. **backward 通信-计算隐藏**：`--enable-backward-overlap-ag-with-matmul` 在 linear 层反向梯度计算时开启 all-gather 与 matmul 重叠。
5. **融合算子依赖**：原文中明确 `--coc-fused-kernel` 与前两个 forward 优化参数**不兼容**，并依赖 ATB 加速库，且仅支持 `micro-batch-size=1`；融合算子需要 **CANN 8.0.1.B020 及以上版本**，并需安装 `CANN-NNAL`。
6. **使用约束与互斥**：与 `--sequence-parallel`、`--use-fused-rmsnorm` 不兼容；不支持 MoE 类模型；仅推荐**超大稠密模型 + 大 TP 域**场景，否则会引起性能下降。

---

## 【关键机制与数据】

以下仅整理原文中明确给出的机理/场景描述，不引入未出现的数字：

- 原文：2D 张量并行的开启条件是 `--tp-2d` 与切分轴 `--tp-x N1`、`--tp-y N2` 同时设置，且约束 `tp = N1 × N2 (N1 > 1, N2 > 1)`。
- 原文：典型推荐用例为「A3 训练 llama3-405B、TP=16」，并建议切分为 `tp-x=8, tp-y=2`。
- 原文：通信-计算重叠与融合机制分别在 linear 层的 `forward`（`--enable-overlap-ag-with-matmul` / `--enable-overlap-matmul-with-rs` / `--coc-fused-kernel`）和 `backward`（`--enable-backward-overlap-ag-with-matmul`）阶段生效，目的是"加速"。
- 原文：融合算子 `--coc-fused-kernel` 的作用域是 linear 层 forward，将 matmul 与 all-gather、reduce-scatter 做算子级融合，且"不与前两个特性兼容"，"依赖 ATB 加速库"。
- 原文：`--enable-backward-overlap-ag-with-matmul` 也"依赖 ATB 加速库"。
- 原文：融合算子对 CANN 版本的要求是 **8.0.1.B020 及以上**，并需安装 **CANN-NNAL**、完成初始化与环境变量配置；融合算子场景**仅支持 micro-batch-size=1**。
- 原文：性能方面仅给出定性描述——推荐场景是"超大稠密模型、TP 域较大"；"较小模型、较小的 TP 域设置会引起性能下降"；其他场景"需要根据 tp-x 和 tp-y 实际调优情况进行配置，部分配置不能保证效率提升"。**原文未给出具体的吞吐/加速比等量化性能数据。**

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**（原文中仅以自然语言形式给出了约束关系 `tp = N1 × N2`、条件 `N1 > 1, N2 > 1`，未以 LaTeX/伪代码形式给出公式。）

---

## 【关联】

- **特性介绍文档**：原文开篇即以链接形式引用了同仓的「高维张量并行」介绍文档
  `https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/tensor-parallel-2d.md`，本文件是其使用方法与约束清单，与该介绍文档构成"原理 + 用法"的配套关系。
- **互斥特性**：
  - `--sequence-parallel`（序列并行）：与 TP-2D 不兼容，使用 TP-2D 时需关闭。
  - `--use-fused-rmsnorm`：与 TP-2D 不兼容，使用 TP-2D 时需关闭。
- **模型范围**：与 MoE 类模型及其相关特性不兼容，适用范围限定为**稠密**模型。
- **依赖底层库**：
  - ATB 加速库：被 `--coc-fused-kernel` 与 `--enable-backward-overlap-ag-with-matmul` 依赖。
  - CANN ≥ 8.0.1.B020 与 `CANN-NNAL`：融合算子的版本与组件前置依赖。
- **典型目标集群/模型**：文中点名"A3 集群 + llama3-405B + TP=16"为推荐场景，体现其与上层模型/集群特性的对接关系。

---

## 【使用方法】

### 1. 基础启用（必备参数）

在训练脚本参数列表中加入以下三组参数：

```bash
    --tensor-model-parallel-size 16 \
    --tp-2d \
    --tp-x 8 \
    --tp-y 2 \
```

要点：
- 必须同时给出 `--tp-2d`、`--tp-x`、`--tp-y`；
- 需满足 `--tensor-model-parallel-size = tp-x × tp-y`，且 `tp-x > 1`、`tp-y > 1`；
- 上述示例对应 `TP=16`、`tp-x=8`、`tp-y=2`，是 llama3-405B 的推荐配置。

### 2. 可选的通信-计算重叠 / 融合算子参数

仅在开启 `--tp-2d` 后生效：

| 参数 | 作用阶段 | 说明 |
| --- | --- | --- |
| `--enable-overlap-ag-with-matmul` | linear 层 forward | 开启 all-gather 与 matmul 重叠以加速 |
| `--enable-overlap-matmul-with-rs` | linear 层 forward | 开启 matmul 与 reduce-scatter 重叠以加速 |
| `--coc-fused-kernel` | linear 层 forward | 开启计算-通信融合算子，将 matmul 与 all-gather、reduce-scatter 算子级融合，进一步加速；依赖 ATB 加速库 |
| `--enable-backward-overlap-ag-with-matmul` | linear 层 backward | 在反向梯度计算时开启 all-gather 与 matmul 重叠以加速；依赖 ATB 加速库 |

约束：以上三个 forward 优化参数 `--enable-overlap-ag-with-matmul`、`--enable-overlap-matmul-with-rs`、`--coc-fused-kernel` **只能同时开启 1 个**。

### 3. 使用约束清单

- 互斥：需关闭 `--sequence-parallel` 与 `--use-fused-rmsnorm`；
- 模型限制：不支持 MoE 类模型及其相关特性；
- 场景限制：仅推荐超大稠密模型 + 大 TP 域（如 llama3-405B TP=16）；较小模型或较小 TP 域会引发性能下降；
- 调优要求：除推荐场景外，需要根据 `tp-x`、`tp-y` 实际调优，部分配置不保证效率提升；
- 融合算子版本与组件要求：CANN ≥ **8.0.1.B020**，需安装 **CANN-NNAL** 并完成初始化与环境变量配置；
- 融合算子批大小限制：仅支持 `micro-batch-size=1`。
