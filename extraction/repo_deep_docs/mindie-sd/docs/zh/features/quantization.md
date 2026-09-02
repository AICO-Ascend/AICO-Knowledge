# 量化

> 仓 `mindie-sd` · 路径 `docs/zh/features/quantization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/quantization.md

# 《量化》文档深度解读

## 【定位】
本文档系统描述 mindie-sd 仓库的量化能力，覆盖两类作用位置不同的量化方案：**Linear 量化**（作用于线性层 weight/activation，权重离线量化 + 激活值可选静态/动态/时间步策略）与 **FA 量化**（作用于注意力层 Q/K/V 激活值的 FP8/MXFP4 块量化），并统一通过 `quantize` 接口入口触发，为推理显存/带宽压缩与吞吐提升提供量化算法选型清单与可执行代码模板。

---

## 【技术要点】

1. **Linear 量化按作用范围分两类**：权重量化（W8A16、W4A16、W4A16_AWQ、W8A16_GPTQ、W4A16_GPTQ——激活值保持原精度）与权重激活量化（W8A8、W8A8_TIMESTEP、W8A8_DYNAMIC、W8A8_PER_CHANNEL、W8A8_PER_TENSOR、W8A8_MXFP8、W4A4_DYNAMIC、W4A4_MXFP4_SVD、W4A4_MXFP4_DUALSCALE、W4A4_MXFP4_DYNAMIC——权重和激活同时量化）。
2. **PTQ 三大范式**：动态量化（仅离线量化权重，激活值在线计算量化因子）、静态量化（权值和激活值都离线量化）、Time-Aware 量化（按时间步切换量化策略）。
3. **量化统一入口 `mindiesd.quantize`**：先解析 JSON 描述符为 `QuantConfig`，再与用户传入 `quant_config` 合并，同字段以用户传入为准；旧接口的 `timestep_config`、`timestep_policy`、`dtype`、`use_nz` 仍兼容。
4. **时间步调度机制**：`TimestepManager.set_timestep_idx(i)` 在每个 denoise step 前调用；Linear/MM 仅在同一 MXFP4 权重下切换激活精度（如 `W4A4` ↔ `W4A8`），FA 则无离线权重约束，可任意在 `MXFP4/FP8/FLOAT` 间切换。
5. **FA 量化三段式流程**：旋转（Q/K 施加 `q_rot`/`k_rot` 预训练旋转矩阵分散异常值）→ 块量化（Q 块大小=128，K/V 块大小=256，经 `npu_dynamic_block_quant` 量化为 `float8_e4m3fn`）→ FP8 Attention（经 `torch.ops.mindiesd.fused_infer_attention_score_v2` 算子走 `FusedInferAttentionScore` 实现 FP8 域内计算，反量化输出）。
6. **MXFP4 量化通过 `mxfp4_scale_alg=2`** 对齐 CANN `aclnnDynamicQuantV2` 的 C7 推理参数，未设置时保持旧接口默认行为；FA 量化权重 `q_rot`/`k_rot` 与量化描述符需由 msmodelslim 预导出。

---

## 【关键机制与数据】

### Linear 量化
- **通用原理**：将 weight 和 activation 从高精度（如 FP32）映射到低精度（INT8、FP8），降低显存占用和带宽、提升吞吐。
- **INT8 映射示例**：浮点范围 `[-max(xf), max(xf)]` → 量化后 `[-128, 127]`。
- **量化描述符合并语义**：`quantize` 内先解析 JSON 描述符为 `QuantConfig`，再与传入 `quant_config` 合并，同字段以用户传入为准；旧接口字段（`timestep_config`、`timestep_policy`、`dtype`、`use_nz`）会被自动收口到 `QuantConfig`。
- **导出文件命名**：权重 `quant_model_weight_{quant_algo.lower()}_{rank}.safetensors`，描述符 `quant_model_description_{quant_algo.lower()}_{rank}.json`，单卡 `rank=0`。

### FA 量化
- **处理对象**：推理时动态生成的 Q/K/V 激活值，需块级别动态量化平衡精度与加速。
- **旋转（Rotate）**：对 Q、K 施加预训练旋转矩阵 `q_rot`、`k_rot`，将异常值分散到各维度，缓解 FP8 对异常值的敏感性。
- **块量化（Block Quant）**（原文参数）：
  - Q 的量化块大小 = **128**
  - K/V 的量化块大小 = **256**
  - 数据类型 = **`float8_e4m3fn`**
  - 实现算子 = **`npu_dynamic_block_quant`**
- **FP8 Attention 算子链路**：通过 `torch.ops.mindiesd.fused_infer_attention_score_v2` 进入本仓迁移的 `FusedInferAttentionScore` 实现，在 FP8 域内完成注意力计算后反量化输出。
- **MXFP4 时间步切换示例**（原文）：`range(0, 2)` → `FLOAT`；`range(2, 8)` → `FP8`；`range(8, 50)` → `MXFP4`，target 均为 `fa`。

### 硬件与布局约束（原文）
- 仅 **Atlas 800I A2 推理服务器**支持 FA 量化。
- Q/K/V 输入布局支持 **`BNSD` 和 `BSND`** 两种。
- FA 量化权重（`q_rot`、`k_rot`）需通过 msmodelslim 大模型压缩工具预先导出。

原文未给出具体的吞吐量/精度提升百分比等性能数据。

---

## 【表格解读】

### 表 1：Linear 量化的权重量化算法

| 算法 | 权重精度 | 说明 |
|------|----------|------|
| W8A16 | INT8 | 基础权重量化 |
| W4A16 | INT4 | 更高压缩比 |
| W4A16_AWQ | INT4 + AWQ | 激活感知的权重量化 |
| W8A16_GPTQ | INT8 + GPTQ | 基于 GPTQ 后训练的权重量化 |
| W4A16_GPTQ | INT4 + GPTQ | 同上，INT4 版本 |

**解读**：本组算法仅量化权重，激活值 A16 表示保持原始精度。从 W8A16 → W4A16 是同种基础方法的压缩比升级；带 `_AWQ` 后缀表示引入激活感知的权重量化（AWA），带 `_GPTQ` 后缀表示使用 GPTQ 后训练方式导出的权重。Linear 量化算法通过统一 `quantize` 接口触发。

### 表 2：Linear 量化的权重激活量化算法

| 算法 | 量化粒度 | 说明 |
|------|----------|------|
| W8A8 | 逐层 | 基础 INT8 权重激活量化 |
| W8A8_TIMESTEP | 逐层 + 时间步 | 推理中动态切换量化策略 |
| W8A8_DYNAMIC | 逐层 | 激活值动态量化 |
| W8A8_PER_CHANNEL | 逐通道 | 按通道粒度量化 |
| W8A8_PER_TENSOR | 按张量粒度量化（原表"逐张量"） | 按张量粒度量化 |
| W8A8_MXFP8 | 逐层 | MXFP8 格式量化 |
| W4A4_DYNAMIC | 逐 token + 逐通道 | INT4 权重激活量化 |
| W4A4_MXFP4_SVD | 逐层 | MXFP4 格式量化 |
| W4A4_MXFP4_DUALSCALE | 逐层 | MXFP4 双尺度量化 |
| W4A4_MXFP4_DYNAMIC | 逐 token + 逐通道 | MXFP4 动态量化 |

**解读**：本组算法权重和激活值同时量化（W8A8、W4A4）并在低精度下完成计算。粒度维度上区分逐层、逐通道、逐 token（细粒度 → 精度更稳但计算复杂度更高）。MXFP 系列（MXFP8、MXFP4）使用微缩格式（Microscaling）量化方案，其中 `_DUALSCALE` 表示引入双尺度量化，`_DYNAMIC` 表示激活值在线动态计算 scale，`_SVD` 表示使用 SVD 分解获得 MXFP4 量化参数。`_TIMESTEP` 后缀是时间步策略的入口，配合 `TimestepPolicyConfig` 使用。

### 表 3：`quantize` 接口参数说明

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | `nn.Module` | 是 | - | 已初始化的浮点模型 |
| `quant_des_path` | `str` | 否 | `None` | 量化描述符 JSON 路径；未作为位置参数传入时，需要配置 `QuantConfig.quant_des_path` |
| `quant_config` | `QuantConfig` | 否 | `None` | 统一量化配置，可承载 `quant_des_path`、`dtype`、`use_nz`、时间步策略和 `mxfp4_scale_alg` |

**解读**：`quantize` 是 Linear 与 FA 两类量化的统一入口。`model` 为必选位置参数；`quant_des_path` 既可作为第二位置参数（字符串路径），也可嵌入 `QuantConfig.quant_des_path`，路径在量化前由 `quantize` 解析为 `QuantConfig`。`QuantConfig` 承载的字段覆盖：描述符路径、数据精度 dtype、NZ 存储 `use_nz`、时间步策略 `timestep_config` 以及 MXFP4 缩放算法 `mxfp4_scale_alg`。同名字段同时存在时，**用户传入的 `quant_config` 优先级高于描述符 JSON**。

---

## 【公式解读】

原文无 LaTeX 公式或伪代码形式的数学表达。仅以 INT8 量化示例给出区间描述：

- 浮点取值范围：`[-max(xf), max(xf)]`（量化前）
- 量化后范围：`[-128, 127]`（INT8 有符号 8-bit 的理论域）

这两个区间描述展示的是线性映射区间端点，并非完整公式；文档未给出 scale/zero-point 的具体计算式或量化反量化公式。

---

## 【关联】

- **`quantize` 统一入口**：同一接口同时触发 Linear 量化与 FA 量化，量化描述符 JSON 路径既作第二位置参数，也可在 `QuantConfig.quant_des_path` 给出，两者解析后合并。
- **`QuantConfig` 作为收口容器**：取代旧接口零散参数（`timestep_config`、`timestep_policy`、`dtype`、`use_nz`），统一承载量化描述符路径、dtype、NZ 存储、时间步策略与 MXFP4 缩放算法 `mxfp4_scale_alg`。
- **`TimestepManager` 与 `TimestepPolicyConfig`**：构成时间步调度核心；通过 `timestep_policy.register(range(...), "算法名", target=...)` 将时间步区间与策略绑定，对 Linear 切 `W4A4 ↔ W4A8` 激活精度、对 FA 切 `MXFP4/FP8/FLOAT`。模型侧调用 `TimestepManager.set_timestep_idx(i)` 与 Wan2.2 文本生成视频推理循环遍历 `timesteps` 的用法相同但策略语义不同（详见原文：「本仓 Linear 是 `W4A4` 与 `W4A8` 切换，不是原有动静态量化切换」）。
- **CANN `aclnnDynamicQuantV2`**：`mxfp4_scale_alg` 透传到动态 MX 量化路径，对齐其 C7 推理参数；外链文档可作为参数语义参考。
- **`add_fa_quant` / `FP8RotateQuantFA` 模块**：`quantize` 内部遍历各层，识别 Attention 层并注入 `FP8RotateQuantFA`，前向流程被替换为「旋转 → 块量化 → FP8 Attention」三段式。
- **`torch.ops.mindiesd.fused_infer_attention_score_v2`**：FA 量化进入 FP8 Attention 内核的算子入口，对接本仓迁移的 `FusedInferAttentionScore`。
- **`npu_dynamic_block_quant`**：FP8 块量化的执行算子（Q 块大小 128，K/V 块大小 256）。
- **msmodelslim 大模型压缩工具**：上游离线导出工具，负责生成 FA 量化权重（`q_rot`、`k_rot`）、量化权重文件与描述符 JSON（命名规范 `quant_model_weight_{quant_algo.lower()}_{rank}.safetensors`、`quant_model_description_{quant_algo.lower()}_{rank}.json`）。
- **Wan2.2 文本生成视频推理循环**：`wan/text2video.py` 遍历 `timesteps` 的方式与本仓 `TimestepManager.set_timestep_idx(i)` 的用法对齐（外部 modelers 仓库参考）。

---

## 【使用方法】

### 1. 启用 Linear 量化（基础）

```python
from mindiesd import quantize

model = from_pretrain()
model = quantize(model, "quant_model_description_w8a16_0.json")
model.to("npu")
```

等价写法（通过 `QuantConfig`）：

```python
from mindiesd import QuantConfig, quantize

quant_config = QuantConfig(quant_des_path="quant_model_description_w8a16_0.json")
model = quantize(model, quant_config=quant_config)
model.to("npu")
```

### 2. 启用 Linear 时间步量化

```python
from mindiesd import QuantConfig, TimestepManager, TimestepPolicyConfig, quantize

timestep_policy = TimestepPolicyConfig()
timestep_policy.register(range(0, 10), "static", target="w8a8_static_linear")

quant_config = QuantConfig(timestep_config=timestep_policy)
model = quantize(model, "quant_model_description_w8a8_timestep_0.json", quant_config=quant_config)

for i, t in enumerate(timesteps):
    TimestepManager.set_timestep_idx(i)
    ...
```

### 3. 启用 MXFP4 Linear 时间步回退

```python
from mindiesd import QuantConfig, TimestepManager, TimestepPolicyConfig, quantize

timestep_policy = TimestepPolicyConfig()
timestep_policy.register(range(0, 4), "W4A8", target="w4a4_linear")
timestep_policy.register(range(4, 50), "W4A4", target="w4a4_linear")

quant_config = QuantConfig(
    timestep_config=timestep_policy,
    mxfp4_scale_alg=2,
)

model = quantize(model, "quant_model_description_w4a4_mxfp4_0.json", quant_config=quant_config)

for i, timestep in enumerate(timesteps):
    TimestepManager.set_timestep_idx(i)
    noise_pred = model(latents, timestep, encoder_hidden_states)
```

**注意**：模型侧需在每个 denoise step 前调用 `TimestepManager.set_timestep_idx(i)`。Linear 回退仅切换激活量化精度（`W4A4` ↔ `W4A8`），权重保持 MXFP4。

### 4. 启用 FA 量化（FP8 旋转 + 块量化）

```python
from mindiesd import quantize

model = from_pretrain()
model = quantize(model, "导出的量化配置文件路径")
model.to("npu")
```

`quantize` 内部会自动识别 Attention 层并注入 `FP8RotateQuantFA`。

### 5. 启用 MXFP4 FA 时间步策略

```python
from mindiesd import QuantConfig, TimestepManager, TimestepPolicyConfig, quantize

timestep_policy = TimestepPolicyConfig()
timestep_policy.register(range(0, 2), "FLOAT", target="fa")
timestep_policy.register(range(2, 8), "FP8", target="fa")
timestep_policy.register(range(8, 50), "MXFP4", target="fa")

quant_config = QuantConfig(
    timestep_config=timestep_policy,
    mxfp4_scale_alg=2,
)

model = quantize(model, "quant_model_description_mxfp4_dynamic_0.json", quant_config=quant_config)

for i, timestep in enumerate(timesteps):
    TimestepManager.set_timestep_idx(i)
    noise_pred = model(latents, timestep, encoder_hidden_states)
```

### 6. 环境与导出前置
- **硬件**：仅 Atlas 800I A2 推理服务器支持 FA 量化。
- **输入布局**：Q/K/V 支持 `BNSD` 和 `BSND`。
- **离线权重导出**：FA 量化权重（`q_rot`、`k_rot`）及量化描述符 JSON 均需通过 msmodelslim 大模型压缩工具预导出（命名规范见上文），单卡时 `rank=0`，多卡并行时各 rank 取对应编号。
- **MXFP4 scale 算法对齐**：通过 `QuantConfig.mxfp4_scale_alg` 字段透传到动态 MX 量化路径，对应 CANN `aclnnDynamicQuantV2` C7 推理参数；未设置时维持旧接口默认行为（见上文 CANN 文档外链）。

## 图文联合解读

- `int8_image.png`: **图文联合解读：**

1) **图示内容**：上轴为FP32连续浮点范围 [-max(|X_f|), max(|X_f|)]，下轴为INT8离散整数范围 [-128, 127]；两侧虚线表示对称线性映射，红色散点示意FP32采样值经缩放舍入后落入INT8格点。

2) **技术结论**：INT8量化采用对称线性映射（以0为中心），将高精度浮点按比例压缩至8位有符号整数空间。

3) **与文档关系**：图示呼应"Linear量化通用原理"段落，以INT8为例直观展示FP32→INT8的量化映射过程，为后续W8A8系列算法（逐层/逐通道/逐张量）提供基础原理铺垫。
