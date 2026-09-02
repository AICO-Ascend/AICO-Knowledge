# Megatron Transformer-engine

> 仓 `mindspeed` · 路径 `docs/zh/features/transformer_engine.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/transformer_engine.md

# Megatron Transformer-engine 文档深度解读

## 【定位】

本文档描述 MindSpeed 昇腾大模型加速库如何通过提供与 NVIDIA Transformer Engine 等价的接口，在 Ascend NPU 上支持 FP8 低精度训练、典型 Transformer 结构模块以及通信计算并行能力，从而兼容依赖 Megatron-TE API 的第三方框架训练/推理需求。

---

## 【技术要点】

1. **等效接口替换**：MindSpeed 提供 5 个 TE 模块以无缝替换 NVIDIA TE，包括 `MindSpeedTELayernorm`、`MindSpeedTELayerNormColumnParallelLinear`、`MindSpeedTEGroupedLinear`、`TEColumnParallelLinear`、`TERowParallelLinear`。

2. **三种 FP8 数据格式**：
   - **E4M3**：1 符号位 + 4 指数位 + 3 尾数位，范围 **-448 到 +448**
   - **E5M2**：1 符号位 + 5 指数位 + 2 尾数位，范围 **-57344 到 +57344**
   - **HiF8**：1 符号位 + 动态 Dot/指数/尾数位，最大可表示 **2^15**

3. **四种 Scaling 策略**：Delayed Scaling（基于历史 amax）、Tensorwise Scaling（在线实时 amax）、Blockwise Scaling（分块独立 amax）、MX Scaling（块级共享 scale + 低位宽元素组合的 MX 块动态量化）。

4. **混合精度训练流程**：整网训练仍以 BF16/FP16 AMP 流程执行，仅将 Linear 层中 Fprop、Dgrad、Wgrad 三类 GEMM 量化到 FP8 精度。

5. **通算融合（Communication Over Computation）**：将原通信/计算串行任务拆为更细粒度子任务，使计算与通信相互掩盖以提升吞吐。

6. **关键命令行参数**：`--transformer-impl`（默认 `transformer_engine`）、`--fp8-format`（支持 `e4m3`/`hybrid`/`hif8`）、`--fp8-recipe`（支持 `tensorwise`/`delayed`/`mxfp8`/`mxfp8-32x32`/`blockwise`，默认 `delayed`）。

---

## 【关键机制与数据】

**工作原理（原文）：** 低精度训练流程中主要是将前向传播（Fprop）、激活反向传播（Dgrad）和权重反向传播（Wgrad）中的 GEMM 量化为 FP8 精度执行运算。整网训练流程仍以 BF16/FP16 AMP 训练为主，但在特定算子（Linear 层的 Matmul）以 FP8 计算。

**状态管理（原文）：** TE 从模块内部维护低精度训练所需的缩放因子（scale factors）及其他低精度训练的状态值，帮助用户更容易从混合精度训练迁移到低精度训练。

**Scaling 策略细节（原文）：**
- Delayed Scaling：根据历史 amax 值计算 scaling factor，然后用其量化 tensor。
- Tensorwise Scaling：在线策略，实时计算 amax 并应用 scaling factor。
- Blockwise Scaling：对 tensor 分块，分别计算 amax 并量化。
- MX Scaling：通过块级共享 scale 与低位宽元素组合，将浮点向量转化为 MX 块，实现动态量化。

**Hybrid 格式语义（原文）：** 开启 `hybrid` 时，前向训练采用 E4M3 数据格式，反向传播采用 E5M2 数据格式。

**HiF8 范围（原文）：** 最大可表示 **2^15**。

**性能数据：** 原文未提供具体吞吐/加速比等量化性能数据。

---

## 【表格解读】

### 原文表格（逐字还原）

| TE 模块功能 | 组合方式 | 是否支持 |
|---|---|---|
| 低精度训练 | `--transformer-impl transformer_engine`<br>`--fp8-format e4m3/hybrid/hif8`<br>`--fp8-recipe tensorwise/delayed/mxfp8/mxfp8-32x32/blockwise` | 是 |
| 通信计算并行 | `--transformer-impl transformer_engine`<br>`--use-ascend-mc2` | 是 |
| 低精度通算并行 | `--transformer-impl transformer_engine`<br>`--fp8-format e4m3/hybrid/hif8`<br>`--fp8-recipe tensorwise/delayed/mxfp8/mxfp8-32x32/blockwise`<br>`--use-ascend-mc2` | 否 |

### 逐行解读

**第 1 行 — 低精度训练（支持）**：表示在标准 TE 实现路径下，可以同时启用 TE 接口 + 任意 FP8 数据格式 + 任意 5 种 scaling recipe 中的任一种。文档 Note 进一步补充：FP8 训练必须搭配 `--use-mcore-models`，且 HiF8 格式仅支持 `tensorwise` recipe，blockwise recipe 下低精度 GMM 不可用（可用 `--no-use-gmm-fp8` 关闭自动启用）。

**第 2 行 — 通信计算并行（支持）**：表示在 BF16/FP16 等高精度训练下，可同时启用 TE 接口与 `ascend-mc2` 通信计算并行。注意 `MindSpeedTELayerNormColumnParallelLinear` 是这一组合的承载模块（Note 中明示其与 `ascend-mc2` 兼容，但与 `ascend-coc` 不兼容）。

**第 3 行 — 低精度通算并行（不支持）**：将第 1 行（FP8）与第 2 行（mc2 通算并行）的参数叠加使用。原文 Note 直接说明"当前不支持低精度通算融合"，这是当前 FP8 训练栈的关键能力空白。

---

## 【公式解读】

原文无公式。

（注：Scaling 策略的描述属于机制性说明，未给出数学表达式或伪代码。）

---

## 【关联】

文档在文末「相关特性参考」中显式给出唯一一条内部链接：

- **[MXFP8 零冗余权重特性](mxfp8/Zero_Redundancy_Weight.md)**：原文表述为"TE 模块为模型构建了底层的 FP8 低精度计算基石……关于低精度训练的整体解决方案及其在特定并行架构下的适配细节，请参考 [MXFP8 零冗余权重特性]，以了解如何在 TE 基础上进一步释放 BF16 权重，从而节省显存。"

由此可推断的上下游关系：
- **TE 模块（本特性）** 是底层 FP8 计算基石，承担 Linear/LayerNorm 等结构层的低精度算子实现；
- **MXFP8 + 零冗余权重** 是在 TE 之上构建的进阶优化，针对 BF16 权重做进一步显存压缩，与 TE 中的 `mxfp8`/`mxfp8-32x32` recipe 共享 MX Scaling 量化基础。

文档中提及但未给出链接的关联模块/特性（基于 Note 内容）：
- `ascend-mc2` 通信计算并行（与 TE LayerNormColumnParallelLinear 互斥关系见上文表格）；
- `ascend-coc`（与 TE LayerNormColumnParallelLinear 不兼容）；
- `1f1b-overlap` 等重构 GMM 特性（可能令 `MindSpeedTEGroupedLinear` 失效）；
- `low-precision GMM`（在非 blockwise recipe 下自动启用，可用 `--no-use-gmm-fp8` 关闭）；
- `--use-flash-attn`（使用 TE 时必须同步开启）。

---

## 【使用方法】

**基础启用（原文）：**
- 脚本中设置 `--transformer-impl transformer_engine`，即可使用 TE 分支。同 Megatron 一致，该参数默认值即为 `transformer_engine`；如需回溯早期版本行为，请额外设置 `--transformer-impl local`。
- 设置 `--fp8-format e4m3` 选择低精度数据格式，目前支持 `e4m3`、`hybrid`、`hif8`。
- 设置 `--fp8-recipe delayed` 选择 scaling 策略，目前支持 `tensorwise`、`delayed`、`mxfp8`、`mxfp8-32x32`、`blockwise`，默认值为 `delayed`。

**强制配套参数（原文 Note）：**
- 低精度训练仅支持 mcore models：需开启 `--use-mcore-models`。
- 使用 transformer_engine 时需同时开启 `--use-flash-attn`。
- HiF8 数据格式训练仅支持 tensorwise 策略：需开启 `--fp8-recipe tensorwise`。
- 如不需要启用低精度 GMM 计算，可开启 `--no-use-gmm-fp8`。

**模块互斥（原文 Note）：**
- `MindSpeedTELayerNormColumnParallelLinear` 支持与 `ascend-mc2` 同时启用，但不支持与 `ascend-coc` 同时启用。
- `MindSpeedTEGroupedLinear` 在 1f1b-overlap 等重构 GMM 特性场景下可能失效。

**组合限制（原文表格）：**
- 低精度训练 + 通信计算并行（mc2）：当前不支持叠加使用。

## 图文联合解读

- `fp8.png`: **图文联合解读：**

1) **图示内容**：展示FP8训练中Linear层的数据流。weight、input、grads三条输入流经cast（量化）+ transpose后，并行送入三个黄色GEMM节点：Fprop（input×weightᵀ→output）、Wgrad（gradsᵀ×input→dw→Master Weight）、Dgrad（grad×weight→grads）。

2) **技术结论**：论证了Linear层的三大Matmul运算（Fprop/Dgrad/Wgrad）均在FP8低精度下执行，而weight需保留高精度Master Weight用于参数更新，实现"计算低精度、存储高精度"的混合策略。

3) **与文档关系**：直观对应文档所述"Linear层Matmul量化、Fprop/Dgrad/Wgrad三向FP8化"的论点，印证MindSpeed TE模块通过统一cast+transpose封装，实现低精度训练的无缝替换。
