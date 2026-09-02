# 高维张量并行

> 仓 `mindspeed` · 路径 `docs/zh/features/tensor-parallel-2d.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/tensor-parallel-2d.md

# 高维张量并行 文档深度解读

## 【定位】

这篇文档描述了 MindSpeed 在昇腾平台上提供的**2D 张量并行（TP-2D）能力**，用于解决大模型训练中当 TP 通信域规模较大时 AllReduce 通信开销过高的问题——通过将原始 TP 通信域分解为 `tp_x` 与 `tp_y` 两个子通信域，对激活值和参数同时切分，从而缩小单次通信域、降低通信次数。

---

## 【技术要点】

1. **核心切分原则**：将原 Megatron TP 域拆分为两个子通信域 `tp_x` 和 `tp_y`，必须满足 `tp = tp_x * tp_y`，且 `N1 > 1, N2 > 1`，即不能退化为 1D-TP。在 Megatron 的 `ColumnParallelLinear` 与 `RowParallelLinear` 基础上增加一维切分维度。
2. **激活与参数同时切分**：相比 1D-TP 仅切分参数，2D-TP 同时对 first-dim 与 last-dim 做切分，使每个设备的子张量更小、对应通信域更小。
3. **分布式 Normalization**：为避免在 2D 切分后 LayerNorm/RMSNorm 之前需要先做两次 all-gather（沿 first-dim 与 last-dim 各一次）才能恢复完整输入，提出了 9 步分布式归约流程，通信仅在 `tp_y` 子通信域内做 AllReduce。
4. **通信-计算隐藏与融合参数**：
   - `--enable-overlap-ag-with-matmul`：forward 时 all-gather 与 matmul 流水重叠。
   - `--enable-overlap-matmul-with-rs`：forward 时 matmul 与 reduce-scatter 流水重叠。
   - `--coc-fused-kernel`：将 matmul 与 all-gather、reduce-scatter 在算子级融合（依赖 ATB）。
   - `--enable-backward-overlap-ag-with-matmul`：backward 时 all-gather 与 matmul 流水重叠（依赖 ATB）。
   - 上述三个 forward 优化参数**只能同时开启 1 个**。
5. **兼容性约束**：与 `--sequence-parallel`、`--use-fused-rmsnorm` 以及 MoE 相关特性**不兼容**。
6. **生效条件**：`--enable-overlap-ag-with-matmul` 等辅助优化参数**必须配合 `--tp-2d` 开启才生效**。

---

## 【关键机制与数据】

### 工作原理

- **背景机制（1D-TP 痛点）**：在传统 1D 张量并行中，参数被切分到 N 个设备，训练过程中需要引入 AllReduce 来同步梯度；当集群规模大、TP 域设置很大时，AllReduce 通信开销显著增大，导致训练效率下降。
- **2D-TP 解决方案**：通过对激活值与参数**同时切分**，并且把原 TP 通信域**分解为两个子通信域**（`tp_x`、`tp_y`），每个子通信域内仍使用 Megatron 的 Column/Row Parallel Linear 范式。这相当于把"大通信域"转换为"两个较小的通信域的乘积"，从而降低单域通信量与通信次数。
- **MLP 层 2D 切分**：文档以 MLP 层为例展示实现方式（原文配有 `figures/tensor-parallel-2d.png` 示意图，未在文字中给出伪代码）。
- **分布式 Normalization 数据流**：在 MLP 与 attention 层分别做 2D 切分后，输入输出已沿 first-dim 与 last-dim 分别被 `tp_x` 与 `tp_y` 切分。若继续沿用原生 LayerNorm/RMSNorm，必须先沿 first-dim 做 all-gather(x)、再沿 last-dim 做 all-gather(y) 才能恢复完整输入，这会带来额外通信开销。2D-TP 用 9 步分布式归约流程替代这两次 all-gather，其通信只在 `tp_y` 子通信域内进行 AllReduce，显著降低通信量。
- **通信-计算重叠/融合**：通过流水重叠（overlap）和算子级融合（fused kernel）进一步隐藏通信延迟，使通信时间被 matmul 计算时间掩盖。

### 性能数据

- **原文：Llama-3-405B 模型训练，tp=16 情况下，开启 2D 张量并行（`tp_x=8, tp_y=2`），相比原 Megatron 1D 张量并行性能提升 5%+。**
- **原文：在上述基础上进一步开启 `coc-fused-kernel` 和 `enable-backward-overlap-ag-with-matmul`（通信-计算融合优化），再额外提升 5%+。**
- **原文警告：其他场景下，由于计算效率和通信组的划分差异，需根据 `tp_x` 和 `tp_y` 实际调优情况进行配置，部分配置不能保证效率提升。**

---

## 【表格解读】

**原文无表格**。文档通过文字描述和示意图（`tensor-parallel-2d.png`）传达 2D-TP 的 MLP 层实现方式，未提供参数表或性能对比表格。

---

## 【公式解读】

以下逐字保留分布式 Normalization 9 步流程中的公式：

### 步骤 1：计算输入的总和

$$e_x = \sum_{i=1}^{H} x_i$$

- 符号：`x` 为输入张量；`x_i` 是张量在最后一个维度上第 `i` 个元素；`H` 是最后一个维度的长度；`e_x` 是当前进程持有的"局部"标量求和结果。

### 步骤 2：分布式归约操作（All-Reduce）

$$e_x^{\text{global}} = \text{AllReduce}\left( e_x \right) = \sum_{p=1}^{P} \sum_{i=1}^{H} x_i^{(p)}$$

- 符号：`P` 是 `tp_y` 子通信域中的进程总数；`x_i^{(p)}` 表示第 `p` 个进程上第 `i` 个元素的值；`e_x^{\text{global}}` 是该 `tp_y` 域内所有进程元素的总和（AllReduce 后每个进程都拥有相同值）。

### 步骤 3：计算输入元素的平方和

$$s_x = \sum_{i=1}^{H} x_i^2$$

- 符号：`s_x` 是当前进程对 `x` 中每个元素做平方后求和的局部结果。

### 步骤 4：分布式归约操作（All-Reduce）

$$s_x^{\text{global}} = \text{AllReduce}\left( s_x \right) = \sum_{p=1}^{P} \sum_{i=1}^{H} \left( x_i^{(p)} \right)^2$$

- 符号：`s_x^{\text{global}}` 是 `tp_y` 子通信域内的全局平方和；其余符号含义同上。

### 步骤 5：中心化输入数据

$$\mu = \frac{e_x^{\text{global}}}{H}$$

$$x'_i = x_i - \mu \quad \forall i \in \{1, 2, \dots, H\}$$

- 符号：`μ` 是全局均值（用 `tp_y` 域内全局总和除以维度长度 `H` 得到）；`x'_i` 是中心化后的元素值。注意这里 `x_i` 是**当前进程本地的部分**，故中心化只需在本地进行。

### 步骤 6：计算均值的平方

$$
e_x'^2 = \left( \frac{e_x^{\text{global}}}{H} \right)^2
$$

- 符号：`e_x'^2` 是全局均值的平方；本质即 `μ²`。

### 步骤 7：计算归一化因子

$$\gamma = \frac{1}{\sqrt{ \left( \frac{s_x^{\text{global}}}{H} \right) - \left( \frac{e_x^{\text{global}}}{H} \right)^2 + \epsilon }}$$

- 符号：
  - `s_x^{\text{global}} / H` = 全局平方和的平均值（即 `E[x²]`）；
  - `(e_x^{\text{global}} / H)²` = 全局均值的平方（即 `(E[x])²`）；
  - 二者之差即 `Var(x) = E[x²] - (E[x])²`；
  - `ε` 是数值稳定性常数，防止方差为零时分母为 0；
  - `γ` 即 `1 / √Var(x)`，用作标准化的乘性因子。

### 步骤 8：标准化输入数据

$$\hat{x}_i = x'_i \cdot \gamma \quad \forall i \in \{1, 2, \dots, H\}$$

- 符号：`\hat{x}_i` 是标准化后的元素。整体公式等价于 `(x_i - μ) / √Var(x)`。

### 步骤 9：应用权重和偏置

- 有偏置：`output_i = b_i + W_i · \hat{x}_i`
- 无偏置：`output_i = W_i · \hat{x}_i`

- 符号：`W` 是权重向量；`b` 是偏置向量；`output_i` 是最终输出元素。

**整体解读**：上述 9 步是 2D-TP 对 LayerNorm/RMSNorm 的等价改造。它用两次 `tp_y` 域内 AllReduce（步骤 2、4）替代了"先沿 first-dim 做 all-gather、再沿 last-dim 做 all-gather"的两次较大通信恢复完整张量的操作，从而在保持归一化数学等价性的前提下，把通信量限制在更小的子通信域中。

---

## 【关联】

文档本身没有提供内部链接，但根据文末给出的兼容性说明，可梳理出以下上下游关系：

- **与 Megatron-1D-TP 的关系**：2D-TP 是在 Megatron 的 `ColumnParallelLinear` 与 `RowParallelLinear` 基础上**增加一维切分**得到的，是 1D-TP 的"域分解 + 二维化"扩展，不是替代关系——某些场景下 `tp_x`、`tp_y` 划分不合理时效率可能反而下降，需实际调优。
- **与 normalization 的关系**：分布式 Normalization 是 2D-TP 的**配套机制**，专门为 LayerNorm/RMSNorm 设计的等价实现，避免切分后两次 all-gather 带来的额外开销。
- **与 ATB 加速库的依赖关系**：`--coc-fused-kernel` 与 `--enable-backward-overlap-ag-with-matmul` 都**依赖 ATB 加速库**才能生效。
- **互斥（不兼容）特性**：
  - `--sequence-parallel`（序列并行）；
  - `--use-fused-rmsnorm`（融合 RMSNorm）；
  - MoE 相关特性。
- **通信优化参数内部互斥**：三个 forward 优化参数（`--enable-overlap-ag-with-matmul`、`--enable-overlap-matmul-with-rs`、`--coc-fused-kernel`）**三者只能同时开启 1 个**。
- **使用场景定位**：当 TP 通信域需要设置得较大、通信效率偏低时启用，目的是**分解通信域以提升通信效率**。

---

## 【使用方法】

### 启用 2D 张量并行

在训练脚本参数列表中加入：

- `--tp-2d`：开启 2D 张量并行。
- `--tp-x N1`：设置 x 轴切分大小（`N1 > 1`）。
- `--tp-y N2`：设置 y 轴切分大小（`N2 > 1`）。
- 约束条件：`tp = N1 * N2`。

### 辅助通信隐藏/融合参数（必须配合 `--tp-2d` 生效）

- `--enable-overlap-ag-with-matmul`：linear 层 forward 时，all-gather 与 matmul 通信计算重叠。
- `--enable-overlap-matmul-with-rs`：linear 层 forward 时，matmul 与 reduce-scatter 通信计算重叠。
- `--coc-fused-kernel`：linear 层 forward 时，将 matmul 与 all-gather、reduce-scatter 进行算子级融合（**依赖 ATB 加速库**，**与前两个不兼容**）。
- `--enable-backward-overlap-ag-with-matmul`：linear 层 backward 时，all-gather 与 matmul 通信计算重叠（**依赖 ATB 加速库**）。

> 上述三个 forward 优化参数 `--enable-overlap-ag-with-matmul`、`--enable-overlap-matmul-with-rs`、`--coc-fused-kernel` **只能同时开启 1 个**。

### 兼容性注意

- 与 `--sequence-parallel`、`--use-fused-rmsnorm`、MoE 等特性**不兼容**，需根据实际情况调整配置。

### 已验证的推荐配置（原文给出）

- Llama-3-405B、tp=16：`--tp-2d` + `--tp-x 8` + `--tp-y 2`，再叠加 `--coc-fused-kernel` 与 `--enable-backward-overlap-ag-with-matmul` 可获得叠加加速。
- 其他模型/集群规模需根据 `tp_x`、`tp_y` 实际调优确定。

## 图文联合解读

- `tensor-parallel-2d.png`: 图示MLP双matmul数据流：activation[s/(cp*x),b,h/y]经all-gather(x)与weight1[h/y,E/x]相乘，输出reduce-scatter(y)聚合partialsum-y；再经gelu、all-gather(y)与weight2[E/x,h/y]相乘，由reduce-scatter(x)收尾。黄色椭圆为集合通信节点，灰色为计算节点，参数沿x/y双维切分。该图论证tp拆分为tp_x×tp_y双通信域的2D切分策略，对应文档"将原tp通信域分解为两个子通信域"的论点，体现"相对1D-TP降低通信域、减少通信次数"的性能优化结论。
