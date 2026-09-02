# TFLOPS计算

> 仓 `mindspeed` · 路径 `docs/zh/features/ops_flops_cal.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/ops_flops_cal.md

# 深度解读：mindspeed TFLOPS计算功能

---

## 【定位】

这篇文档描述 mindspeed 提供的一个**算子级 FLOPs 统计能力**：通过接口自动汇总所有 MatMul 相关算子的浮点运算次数（含正反向训练与重计算），解决大模型在 MFU/HFU 评估时依赖框架理论 TFLOPS（不适用于改动模型结构）与 HFU 需手动计算的痛点。

---

## 【技术要点】

1. **算子覆盖范围**：支持 7 类 MatMul 相关算子的浮点计算次数统计——`MatMul`、`BatchMatMul`、`FlashAttention`、`MC2 相关融合算子`、`CoC 相关融合算子`、`GEMM 相关融合算子`、`matmul_add_fp32 融合算子`。
2. **启用方式**：通过命令行参数 `--op-cal-tflops` 开启统计功能。
3. **输出指标**：打印 `actual throughput per NPU (TFLOP/s/NPU)` 与 `actual throughput per NPU with recompute (TFLOP/s/NPU)` 两个值，分别对应普通训练与含重计算的吞吐，用于计算 MFU 和 HFU。
4. **分布式聚合约束**：在 CP/EP/PP 切分场景下，各卡计算量不一致，需额外做一次 `all_reduce` 通信后取平均才能得到全局结果。
5. **Ring Attention 偏差**：causal 场景下由于算法优化，FA 实际计算量相对理论值减少 **`(CP-1)/(2×CP)`**（原文给出），导致理论与实际统计值不符。
6. **不支持场景**：明确声明该功能**暂不支持 MLA**（Multi-Latent Attention）场景。

---

## 【关键机制与数据】

### 工作原理（基于原文）

- **背景问题**：原文指出当前大模型 MFU 计算"依赖框架理论打印值 TFLOPS/有效算力得到，但理论值计算适用于一般模型，如果针对模型结构进行变动，将不再适用，同时 HFU 的计算目前需要手动计算"。
- **解决方案机制**：提供"统计所有涉及 MatMul 计算的算子的浮点计算次数"的接口，并"能统计到模型正反向训练以及重计算的总浮点计算次数"。
- **数据流**：开启 `--op-cal-tflops` → 各卡独立统计各自 MatMul 类算子的 FLOPs → 在 CP/EP/PP 场景下各卡统计值不同 → 需通过额外的 `all_reduce` 汇总后求平均 → 输出每卡实际吞吐（TFLOP/s/NPU）。
- **性能代价**（原文）："使用此功能由于会增加一个额外通信以及计算各算子的浮点计算次数，可能影响性能"——即有两方面开销：额外的 all_reduce 通信 + 每算子 FLOPs 统计计算本身。

### 性能/数据

- 原文未给出具体的加速比、吞吐数字、统计误差率等量化性能数据。
- 唯一可量化的偏差系数来自 NOTE 中 Ring Attention 场景：FA 计算减少比例 = `(CP-1)/(2×CP)`。

---

## 【表格解读】

**原文无表格**

（整篇文档由背景、解决方案、使用方法、使用效果、NOTE 五个段落构成，未出现任何 markdown 表格或参数表/性能对比表/配置表。）

---

## 【公式解读】

原文仅含一处数值比例表达式，以 NOTE 文字形式给出：

$$\text{Ring Attention causal 场景下 FA 计算减少比例} = \frac{CP - 1}{2 \times CP}$$

**符号含义与作用：**

| 符号 | 含义 | 作用 |
|---|---|---|
| $CP$ | Context Parallel size，上下文并行度（即并行处理的序列分片数） | 表示序列被切分的份数；CP 越大，参与并行的卡数越多 |
| $CP - 1$ | 上下文并行中"非末尾分片"的数量（除去最后一个分片） | 反映哪些分片会因 causal mask 而跳过对角区域的计算 |
| $2 \times CP$ | 分母 2×CP 中的 2 | 对应 causal mask 的双向（左下三角 + 右上三角对称去掉）维度归一化因子 |

**解读**：在 Ring Attention 的 causal 场景下，每个非末尾分片都有一段"未来信息"无需计算（被 causal mask 裁掉），优化算法会跳过这段冗余计算。理论减少值与 CP 相关——CP 越大，减少比例趋近于 1/2；CP=2 时为 1/4；CP=1 时为 0（即无并行、无减少）。这也是导致"理论 TFLOPS"与"--op-cal-tflops 实际统计值"出现偏差的根源。

---

## 【关联】

原文未提供内部链接，也未显式引用其他特性/模块。基于原文可推断的关联关系：

- **上游/并列能力**：
  - 与 **MC2（MatMul-Communication-Computation 融合）相关融合算子** 关联——属于 mindspeed 集合通信融合特性的一部分，本功能需要能统计这些融合算子的 FLOPs。
  - 与 **CoC 相关融合算子** 关联——属于 mindspeed 的 CoC（Compute-over-Communication）系列融合算子。
  - 与 **GEMM 相关融合算子** 关联——mindspeed 中针对 GEMM 进行的算子融合。
- **下游使用方**：
  - 与 **MFU（Model FLOPs Utilization）计算**关联——`actual throughput per NPU` 用于计算 MFU。
  - 与 **HFU（Hardware FLOPs Utilization）计算**关联——含重计算的吞吐值用于 HFU 计算，文档指出 HFU "目前需要手动计算"，本功能为其自动化提供基础数据。
- **受影响的并行策略**：
  - **CP（Context Parallelism）**：决定各卡计算量是否相同，是 Ring Attention 偏差公式 `(CP-1)/(2×CP)` 的输入参数。
  - **EP（Expert Parallelism）/ PP（Pipeline Parallelism）**：与 CP 共同构成"各卡计算量不同"的场景。
- **不支持场景**：
  - **MLA（Multi-Latent Attention）**：明确不在本功能支持范围，使用时需注意。

---

## 【使用方法】

原文给出了明确的启用方式：

- **命令行参数**：在启动训练时添加 `--op-cal-tflops` 参数即可启用该统计功能。

**输出日志关键字**（用于提取统计结果）：
- `actual throughput per NPU (TFLOP/s/NPU)`：不含重计算的实际每卡吞吐，用于计算 MFU。
- `actual throughput per NPU with recompute (TFLOP/s/NPU)`：含重计算的每卡吞吐，用于计算 HFU。

**使用注意事项**（原文 NOTE 原文摘录）：
- CP/EP/PP 场景下需通过 `all_reduce` 汇总后求平均。
- 此功能因额外通信与统计计算"可能影响性能"。
- Ring Attention causal 场景的统计值会相对理论值偏少，理论偏差为 `(CP-1)/(2×CP)`。
- 暂不支持 MLA 场景。

原文未涉及：具体的 Python API 调用方式、配置文件写法、采样频率/统计粒度参数、与其他 profiler 工具的协同使用方法。
