# PDMIX量化

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/pdmix.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/pdmix.md

# PDMIX 量化文档深度解读

## 【定位】

这篇文档描述了 PDMIX（Prefill-Decode-MIX）量化能力——在大模型推理的 Prefill 与 Decode 两个阶段分别采用不同 W8A8 量化策略（动态 per-token 与静态 per-tensor）的方案，以同时兼顾长序列/Prompt 阶段的精度与逐 Token 生成阶段的吞吐率。

---

## 【技术要点】

1. **双阶段异构量化**：Prefill 阶段使用 **W8A8 Dynamic (Per-token)**（每个 Token 独立 Input Scale）；Decode 阶段使用 **W8A8 Static (Per-tensor)**（整个 Tensor 统一 Input Scale，参数固定）。
2. **相对标准 W8A8 的差异**：PDMIX 量化权重中**新增** `weight_scale` 与 `weight_offset` 两个张量，专门用于对 **Matmul 计算结果**进行反量化。
3. **量化标识**：权重描述文件中所有相关字段统一标记为 `W8A8_MIX`；权重文件名为 `quant_model_weight_w8a8_mix.safetensors`。
4. **适用模型精度**：原文明确"此量化方式支持量化 **bfloat16** 类型的原始权重"。
5. **Bias 存在性约束**：原文说明"**仅当浮点权重存在 bias 场景时**，量化权重才会有 bias"——即 bias 为可选字段。
6. **生成与执行工具链**：使用 **msModelSlim** 工具生成量化权重，调用入口 `msmodelslim quant`；推理入口为 `${ATB_SPEED_HOME_PATH}` 下的 `examples.run_pa`。

---

## 【关键机制与数据】

- **工作原理（原文）**：PDMIX 量化在 Prefill 与 Decode 阶段使用**不同**的量化方式。Prefill 阶段处理长序列或 Prompt 时激活值分布变化较大，动态 per-token 量化可显著减少精度损失；Decode 阶段由于**计算访存比（Compute-to-Memory Ratio）较低**，静态 per-tensor 量化能最大化推理吞吐率。
- **推理流程（原文）**：量化权重推理流程同 W8A8 量化（PDMIX 未引入额外推理算子差异，区别仅在量化侧）。
- **量化粒度（原文）**：Per-token → 每 Token 一份 Input Scale；Per-tensor → 整 Tensor 一份 Input Scale 且参数固定、计算开销最小。
- **性能数字（原文）**：原文未涉及任何具体性能数据（吞吐率、精度损失百分比、加速比等均未给出）。

---

## 【表格解读】

### 表 1：PDMIX 量化两阶段方案对比

| 量化方式 | 推理阶段 | 量化特点 | 适用场景 |
|---|---|---|---|
| **W8A8 Dynamic (Per-token)** | Prefill | 每个 Token 使用独立的 Input Scale 进行量化，能够动态适应不同 Token 的激活值范围。 | **精度优先**。在处理长序列或 Prompt 阶段，激活值分布变化较大，动态量化能显著减少精度损失。 |
| **W8A8 Static (Per-tensor)** | Decode | 整个 Tensor 使用统一的 Input Scale 进行量化，参数固定，计算开销最小。 | **性能优先**。在逐个生成 Token 的阶段，计算访存比（Compute-to-Memory Ratio）较低，静态量化能最大化推理吞吐率。 |

**逐行解读**：
- **第 1 行**：定义 Prefill 阶段所用方案。Per-token 动态量化保留每个 Token 自己的 Input Scale，因此能随激活分布漂移自适应；以"精度优先"为目标场景。
- **第 2 行**：定义 Decode 阶段所用方案。Per-tensor 静态量化整个 Tensor 共用一个固定 Input Scale，避免逐 Token 的标量计算开销；以"性能优先"为目标场景。
- **整体设计**：通过把"精度敏感、计算密集"的 Prefill 与"性能敏感、访存密集"的 Decode 分离量化，PDMIX 在不引入额外推理算子前提下取得精度/吞吐的折中。

---

### 表 2：bfloat16 权重量化后 dtype 及 shape 信息（原始权重 shape 假设为 `[n, k]`）

| Tensor 信息 | weight | quant_bias | input_scale | input_offset | deq_scale | weight_scale | weight_offset |
|---|---|---|---|---|---|---|---|
| dtype | int8 | int32 | bf16 | bf16 | fp32 | bf16 | bf16 |
| shape | `[n,k]` | `[n]` | `[1]` | `[1]` | `[n]` | `[n,1]` | `[n,1]` |

**逐行解读**：
- **dtype 行**：量化后主权重 `weight` 为 int8；`quant_bias` 为 int32（与标准 W8A8 一致）；激活侧 `input_scale`/`input_offset` 保留 bf16（与原始权重的精度类型一致，便于低开销还原）；`deq_scale` 采用 fp32 以保证反量化数值精度；PDMIX 新增的 `weight_scale`/`weight_offset` 为 bf16。
- **shape 行**：权重 `[n, k]` 与量化 bias `[n]` 与常规量化一致；激活侧 `input_scale`/`input_offset` 形状为 `[1]`（静态 per-tensor 量化对应单一标量），但文档说明两种模式均存在，此处需结合 Table 1 中 Per-token 模式理解——PDMIX 实际在量化描述中采用统一的存储结构，运行时再按阶段采用不同应用方式；`deq_scale` 形状 `[n]`（per-channel），与权重输出通道对齐；PDMIX 新增的 `weight_scale`/`weight_offset` 形状为 `[n, 1]`，即每个输出通道对应一个标量，用于 Matmul 结果的反量化。

---

## 【公式解读】

**原文无公式**。

（文档未给出 LaTeX 或伪代码形式的量化/反量化数学表达式，仅以文字与表格形式描述机制。）

---

## 【关联】

- **W8A8 量化**：PDMIX 与 W8A8 共享相同的推理流程，差异仅在量化侧新增 `weight_scale`/`weight_offset` 两个张量（用于 Matmul 计算结果的反量化）。
- **msModelSlim 量化工具**：PDMIX 量化权重由 Ascend msModelSlim 工具生成，文档给出外部链接 <https://gitcode.com/Ascend/msit/blob/master/msmodelslim/README.md>，并提示"如需了解更多量化参数配置，请参考 msModelSlim 工具文档"。
- **ATB_SPEED_HOME_PATH 推理入口**：推理执行依赖 `${ATB_SPEED_HOME_PATH}` 下的 `examples.run_pa` 入口（`torchrun` 启动），表明 PDMIX 在推理运行时框架（ATB Speed）中以 `run_pa` 路径承载。
- **文末内部链接**：原文未提供仓库内的内部链接（题目标注内部链接为"无"）。

---

## 【使用方法】

### 1. 生成 PDMIX 量化权重（原文命令）

```sh
msmodelslim quant --model_path {浮点权重路径} --save_path {W8A8PDMIX量化权重路径} --device npu --model_type Qwen3-14B --quant_type w8a8 --trust_remote_code True
```

- **适用模型示例**：Qwen3-14B（bfloat16 浮点权重）。
- **关键参数（原文）**：`--quant_type w8a8`（量化类型标识）、`--model_type Qwen3-14B`、`--device npu`、`--trust_remote_code True`。
- **前置依赖**：需先安装 msModelSlim 工具。
- **提示**：原文注明"上述命令是 msModelSlim 工具的一个最佳实践"。

### 2. 执行对话推理（原文命令）

```sh
cd ${ATB_SPEED_HOME_PATH}
torchrun --nproc_per_node 2 --master_port 12350 -m examples.run_pa --model_path {pdmix量化权重路径}
```

- **适用模型示例**：Qwen3-14B-W8A8PDMIX 权重。
- **关键参数（原文）**：`--nproc_per_node 2`（进程数）、`--master_port 12350`、`-m examples.run_pa`（推理入口模块）。
- **示例输入输出（原文）**：输入问题 "What's deep learning?"，最长输出 20 个 token。

### 3. 其它配置项（原文未涉及）

原文未提供 PDMIX 独立的运行时开关、环境变量或额外 YAML/JSON 配置项说明——所有量化配置均通过 msModelSlim 的命令行参数指定。
