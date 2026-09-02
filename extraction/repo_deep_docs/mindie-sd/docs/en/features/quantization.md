# Quantization

> 仓 `mindie-sd` · 路径 `docs/en/features/quantization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/quantization.md

# 一体化深度解读：mindie-sd Quantization 文档

## 【定位】

这篇文档定义了 MindIE SD 中两类量化能力的统一接入方式：**Linear Quantization（线性层权重/激活的离线低比特量化）** 与 **FA Quantization（Flash Attention 中 Q/K/V 激活的 FP8 动态量化）**，解决昇腾 NPU 上大模型推理的存储、带宽与吞吐瓶颈。

---

## 【技术要点】

1. **两套量化并行体系**：Linear Quantization 作用于 `nn.Linear` 层的 W/A（W=weight, A=activation），FA Quantization 作用于 Attention 内部的 Q/K/V 激活；二者均通过统一的 `quantize` API 入口触发。
2. **PTQ 三大子类**：Dynamic Quantization（仅权重量化离线，激活量化因子推理时动态计算）、Static Quantization（W/A 都离线量化）、Time-Aware Quantization（按 timestep 维度动态切换策略）。
3. **10 类 Linear 量化算法**：覆盖纯权重路线（W8A16/W4A16/W4A16_AWQ/W8A16_GPTQ/W4A16_GPTQ，共 5 项）与权激活同时量化路线（W8A8/W8A8_TIMESTEP/W8A8_DYNAMIC/W8A8_PER_CHANNEL/W8A8_PER_TENSOR/W8A8_MXFP8/W4A4_DYNAMIC/W4A4_MXFP4_SVD/W4A4_MXFP4_DUALSCALE/W4A4_MXFP4_DYNAMIC，共 10 项）。
4. **INT8 量化区间映射**：将 FP32 浮点区间 $[-max(x_f),\,max(x_f)]$ 映射到 INT8 区间 $[-128,\,127]$，通过 msmodelslim 工具离线导出。
5. **FA 量化三步流水线**：Rotate（用预训练旋转矩阵 $q_{rot}$/$k_{rot}$ 将离群点扩散到各维度）→ Block Quantization（按块调用 `npu_dynamic_block_quant` 算子做 FP8 动态量化，Q 块大小 128，K/V 块大小 256）→ FP8 Attention（调用 `torch.ops.mindiesd.fused_infer_attention_score_v2`，输出反量化回原精度）。
6. **量化产物的命名约定**：权重重命名 `quant_model_weight_{quant_algo.lower()}_{rank}.safetensors`，描述文件 `quant_model_description_{quant_algo.lower()}_{rank}.json`；单卡场景 `rank=0`，多卡并行场景按 rank 号一一对应。

---

## 【关键机制与数据】

- **原文：精度档位**：Linear 层量化最低到 **INT4（W4A16 / W4A4_DYNAMIC / W4A4_MXFP4_SVD / W4A4_MXFP4_DUALSCALE / W4A4_MXFP4_DYNAMIC）**，W/A 同时量化的最低组合为 **W4A4**；FA 量化专门选择 **FP8（float8_e4m3fn）** 这一个 dtype。
- **原文：分块粒度**：FA 量化对 Q 的分块大小为 **128**，对 K/V 的分块大小为 **256**，由 `npu_dynamic_block_quant` 算子执行。
- **原文：FA 量化的 Attention 算子**：MindIE SD 自有算子 `torch.ops.mindiesd.fused_infer_attention_score_v2`，路由到仓内迁移的 `FusedInferAttentionScore` 实现。
- **原文：旋转矩阵来源**：FA 量化所需的 `q_rot` / `k_rot` 权重必须通过 msmodelslim 模型压缩工具提前导出。
- **原文：硬件要求**：FA 量化目前**仅**支持 Atlas 800I A2 推理服务器。
- **原文：Layout 兼容性**：Q/K/V 输入 layout 同时支持 **BNSD** 与 **BSND**。
- **原文：量化描述 JSON 内容**：包含 `algorithm`、`layer configuration` 等配置（`model` 参数与 `quant_json_path` 参数，类型分别为 `nn.Module` 与 `str`，均**为必填**且无默认值）。
- **原文：Linear 量化与 timestep 调度**：Timestep quantization 需配合 `mindiesd.TimestepManager` 的 `set_timestep_idx(i)` 调用，并在 `quantize` 时传入 `TimestepPolicyConfig(...)`。
- **原文：FA 量化的自动注入机制**：`quantize` 内部遍历模型层，自动对匹配的 Attention 层调用 `add_fa_quant`，注入 `FP8RotateQuantFA` 模块并替换 forward 为 rotate → block quantize → FP8 Attention 流程，**对外无需额外的 FA 量化 API 调用**。
- **原文**：文档未给出具体的推理吞吐、显存节省、延迟等量化性能数字，仅描述原理与功能。

---

## 【表格解读】

### 表 1：Weight Quantization 算法（纯权重路线）

| Algorithm | Weight Precision | Description |
| ------ | ---------- | ------ |
| W8A16 | INT8 | Basic weight quantization |
| W4A16 | INT4 | Higher compression ratio |
| W4A16_AWQ | INT4 + AWQ | Activation-aware weight quantization |
| W8A16_GPTQ | INT8 + GPTQ | GPTQ post-training weight quantization |
| W4A16_GPTQ | INT4 + GPTQ | Same as above, INT4 version |

**逐行解读**：
- **W8A16 / INT8**：最基础的权重量化方案，激活保持原精度（FP16/BF16），主要面向兼容性优先、对精度更敏感的场景。
- **W4A16 / INT4**：相比 W8A16 进一步压缩权重存储，描述强调"Higher compression ratio"，适合带宽受限场景。
- **W4A16_AWQ / INT4 + AWQ**：在 INT4 基础上引入 **AWQ（Activation-aware Weight Quantization）**，利用激活分布信息保护重要权重，是 INT4 路线中精度更友好的选择。
- **W8A16_GPTQ / INT8 + GPTQ**：在 INT8 精度上叠加 **GPTQ（Generative Pre-trained Transformer Quantization）** 后训练算法，通过二阶信息调整量化参数。
- **W4A16_GPTQ / INT4 + GPTQ**：与上一行同算法思想，但压缩到 INT4，是表中精度-压缩比最激进的纯权重选项。

### 表 2：Weight-Activation Quantization 算法（W/A 同时量化路线）

| Algorithm | Quantization Granularity | Description |
| ------ | ---------- | ------ |
| W8A8 | Per-layer | Basic INT8 weight-activation quantization |
| W8A8_TIMESTEP | Per-layer + timestep | Dynamically switch quantization strategy during inference |
| W8A8_DYNAMIC | Per-layer | Dynamic activation quantization |
| W8A8_PER_CHANNEL | Per-channel | Channel-granularity quantization |
| W8A8_PER_TENSOR | Per-tensor | Tensor-granularity quantization |
| W8A8_MXFP8 | Per-layer | MXFP8 format quantization |
| W4A4_DYNAMIC | Per-token + per-channel | INT4 weight-activation quantization |
| W4A4_MXFP4_SVD | Per-layer | MXFP4 format quantization |
| W4A4_MXFP4_DUALSCALE | Per-layer | MXFP4 dual-scale quantization |
| W4A4_MXFP4_DYNAMIC | Per-token + per-channel | MXFP4 dynamic quantization |

**逐行解读**：
- **W8A8 / Per-layer**：最基础的 INT8 权激活同时量化，每层共享一组量化因子。
- **W8A8_TIMESTEP / Per-layer + timestep**：在 Per-layer 基础上叠加 **timestep 维度**的策略切换，是与 Time-Aware Quantization 原理直接对应的算法入口。
- **W8A8_DYNAMIC / Per-layer**：激活量化因子在推理时动态计算，是 Dynamic Quantization 思路在 W8A8 档位上的实现。
- **W8A8_PER_CHANNEL / Per-channel**：将粒度从层细化到 **通道**，对每个通道独立计算量化参数，精度上限更高。
- **W8A8_PER_TENSOR / Per-tensor**：与 Per-channel 对偶，采用更粗的 **整张 tensor 共享**量化参数，硬件更友好。
- **W8A8_MXFP8 / Per-layer**：使用 **MXFP8（Microscaling FP8）** 格式做层粒度量化。
- **W4A4_DYNAMIC / Per-token + per-channel**：进入 INT4 档位，激活按 token、权重按 channel 做细粒度量化。
- **W4A4_MXFP4_SVD / Per-layer**：MXFP4 格式下的 **SVD 分解**量化方案。
- **W4A4_MXFP4_DUALSCALE / Per-layer**：MXFP4 的 **双缩放因子（dual-scale）** 方案。
- **W4A4_MXFP4_DYNAMIC / Per-token + per-channel**：MXFP4 格式下的动态量化，激活/权重的粒度组合与 W4A4_DYNAMIC 一致。

### 表 3：`quantize` API 参数

| Parameter | Type | Required | Default | Description |
| ------ | ------ | ------ | -------- | ------ |
| `model` | `nn.Module` | Yes | - | Initialized floating-point model |
| `quant_json_path` | `str` | Yes | - | Path to quantization descriptor JSON containing algorithm, layer configuration, etc. |

**逐行解读**：
- **`model` / `nn.Module` / 必填 / 无默认值**：传入由 `from_pretrain()` 之类的工厂函数返回的**未量化**浮点模型实例，`quantize` 会**原地转换**并返回新的模型对象（由 `model = quantize(...)` 的写法可见）。
- **`quant_json_path` / `str` / 必填 / 无默认值**：指向 msmodelslim 工具导出的 JSON 描述文件，里面携带 algorithm 名称（如 `w8a16`、`w8a8_timestep`、`fp8_dynamic` 等）与逐层 layer-type 配置，是量化行为的事实"配方"。

---

## 【公式解读】

原文给出的量化映射可写为：

$$
\text{quantize}: \ [-max(x_f),\ max(x_f)] \ \longrightarrow \ [-128,\ 127]
$$

其中：
- $x_f$：原始 FP32 张量（可以是 weight 也可以是 activation）。
- $max(x_f)$：该张量在量化前统计得到的最大绝对值（calibration 阶段得到）。
- 左侧 $[-max(x_f),\ max(x_f)]$：量化前的浮点值域。
- 右侧 $[-128,\ 127]$：INT8 的有符号 8-bit 表示范围（$-2^7$ 到 $2^7-1$）。

**作用**：原文以 INT8 为例说明"高精度 → 低精度"的线性仿射量化基本形态——通过把 $[-max(x_f),\,max(x_f)]$ 线性映射到 $[-128,\,127]$，任意浮点值都能被 round/clamp 到最近的有符号 INT8 表示，从而以远小于 FP32 的存储/带宽开销承载模型推理中的数值。需要注意的是，文档仅以区间形式描述了**端点对齐**，未给出 scale / zero-point 的具体闭式表达。

> 原文无其他 LaTeX/伪代码形式的数学公式。

---

## 【关联】

- **与 msmodelslim 模型压缩工具的关系**：Linear 量化的描述 JSON 文件（`quant_model_description_*.json`）、量化权重（`quant_model_weight_*.safetensors`），以及 FA 量化所需的 `q_rot` / `k_rot` 旋转矩阵，**均依赖 msmodelslim 离线导出**——也就是说，mindie-sd 自身只负责推理侧加载与执行，真正的"压缩"动作在前置工具中完成。
- **与 TimestepManager 的关系**：Time-Aware Quantization 路径必须配合 `mindiesd.TimestepManager` 的 `set_timestep_idx(i)` 调用，在推理循环中显式同步 timestep 索引；策略细节通过 `TimestepPolicyConfig(...)` 注入 `quantize`。
- **与 Attention 算子栈的关系**：FA 量化最终落到 `torch.ops.mindiesd.fused_infer_attention_score_v2`，该算子路由到仓内迁移的 `FusedInferAttentionScore` 实现，形成"FP8 域内 Attention 计算 → 输出反量化回原精度"的链路，与仓内 vLLM Omni / Diffusers+CacheDit / lightx2v 等被加速框架共同服务于多模态推理。
- **与硬件平台的关系**：FA 量化目前**仅**支持 Atlas 800I A2 推理服务器，是仓内"线性层量化（W/A）"与"Attention 量化（Q/K/V）"在硬件可用性上的分界线。
- **内部链接**：原文及文档元信息中**未提供任何内部链接**（无相关章节交叉引用、无锚点跳转）。

---

## 【使用方法】

### 1. 通用入口（Linear / FA 通用）

```python
from mindiesd import quantize

model = from_pretrain()                           # 加载原始浮点模型
model = quantize(model, "quant_model_description_<algo>_<rank>.json")
model.to("npu")                                    # 迁移到 NPU 推理
```

### 2. Linear Quantization —— 基础量化

```python
from mindiesd import quantize

model = from_pretrain()
model = quantize(model, "quant_model_description_w8a16_0.json")
model.to("npu")
```

### 3. Linear Quantization —— Timestep（Time-Aware）量化

```python
from mindiesd import quantize, TimestepManager

model = quantize(
    model,
    "quant_model_description_w8a8_timestep_0.json",
    timestep_policy=TimestepPolicyConfig(...),     # 原文用 ... 占位，未给出具体字段
)

for i, t in enumerate(timesteps):
    TimestepManager.set_timestep_idx(i)            # 推理循环里同步 timestep
    ...
```

### 4. FA Quantization（自动识别 + 注入）

```python
from mindiesd import quantize

model = from_pretrain()
model = quantize(model, "path/to/exported/quantization/config")   # 触发 add_fa_quant + FP8RotateQuantFA 注入
model.to("npu")
```

### 5. 关键配置项与前置条件

- **算法选择**：通过 `quant_json_path` 指向的 JSON 描述文件指定，命名遵循 `quant_model_description_{quant_algo.lower()}_{rank}.json`。
- **权重文件**：与描述 JSON 同前缀，命名 `quant_model_weight_{quant_algo.lower()}_{rank}.safetensors`；单卡 `rank=0`，多卡并行时按 rank 号一一对应。
- **硬件**：FA 量化仅支持 **Atlas 800I A2** 推理服务器；Linear 量化未在文档中标注额外硬件限制。
- **Layout**：FA 量化 Q/K/V 输入支持 **BNSD** 与 **BSND**。
- **前置工具**：量化权重、描述 JSON、`q_rot` / `k_rot` 旋转矩阵**必须**先用 msmodelslim 模型压缩工具导出，具体字段需参考 msmodelslim 工具文档（本文未展开）。
- **API 参数**：`model`（`nn.Module`，必填，原始浮点模型）与 `quant_json_path`（`str`，必填，量化描述 JSON 路径），均无默认值。

## 图文联合解读

- `int8_image.png`: **图文联合解读：**

图示展示了**INT8线性量化**的核心原理：上方为FP32浮点域`[-max(|Xf|), max(|Xf|)]`（含0中点），下方为INT8整数域`[-128, 127]`，红点表示数据分布。虚线箭头揭示了**带饱和截断的非线性映射**关系——位于`max(|Xf|)`之外的浮点值会被截断并压缩到-128或127，而非严格线性外推；中间区域的样本则近似线性对应。

该图论证了：Linear Quantization通过缩放因子将高精度权重/激活映射到低精度表示，既保留数值动态范围，又通过截断抑制离群点对量化精度的干扰，从而降低存储与计算开销。这直接支撑文档论点——量化是"高→低精度映射以减少内存与带宽、提升推理吞吐"的关键手段。
