# Sparse

> 仓 `mindie-sd` · 路径 `docs/en/features/sparse.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/sparse.md

# 深度解读：docs/en/features/sparse.md

## 【定位】

本文档系统介绍了 mindie-sd 套件中**面向 DiT 类模型的稀疏注意力（Sparse Attention）能力**，围绕「如何识别可跳过的计算」与「如何让稀疏模式真正映射到硬件加速」两大核心挑战，给出 rf_v2（RainFusion2.0）与 ada_bsa 两种稀疏策略，并通过统一的 `sparse_attention` API 暴露给上层推理框架使用。

---

## 【技术要点】

1. **稀疏注意力的目标**：跳过 Q-K 注意力分数矩阵中**相关性极低**的 token pair，只保留关键交互，从而降低 DiT 推理中的计算与延迟。
2. **两大策略并列**：rf_v2（RainFusion2.0）作为**推荐方案**，ada_bsa 作为**兼容性兜底**；分别通过三套技术与 CDF 阈值法解决两大挑战。
3. **rf_v2 三大技术**：
   - **Block Representative Token Prediction**：将 Q/K 按空间形状分块，用块均值作代表 token，通过代表 token 的相似度预测稀疏掩码，显著降低掩码预测开销（解决"如何确定"）。
   - **Spatio-Temporal Token Reordering**：按 `[t, h, w]` 三维窗口对 token 重排，让同一空间位置的相邻帧 token 在块内聚集，提高块自相似性与硬件效率（解决"如何对齐"）。
   - **First-Frame Sink Mechanism**：强制首帧参与全注意力计算，复用 LLM 注意力 sink 现象的经验，在 80% 稀疏率下保持近无损质量。
4. **ada_bsa 机制**：通过 **CDF 阈值化**动态估计稀疏块集合，适合需要灵活稀疏粒度的场景。
5. **性能与默认参数**：rf_v2 在 Ascend NPU 上以 **80% 稀疏率**实现 **1.5–1.8x 端到端加速**，质量接近全注意力；图像任务建议从 **sparsity=0.6** 起步，视频任务从 **0.8** 起步。
6. **API 约束**：`block_size` 当前**仅支持 128**；该 API **仅提供前向推理，不支持反向梯度**。

---

## 【关键机制与数据】

### 数据流与工作原理（按原文梳理）

- **输入端**：Q/K/V 张量（形状见下文使用示例，B×Head×Seq×Dim 形式 `BNSD`），外加 `sparse_type`、`sparsity`，视频任务还需传入 `latent_shape_q/k = [t, h, w]`。
- **掩码预测路径（rf_v2）**：
  1. Q、K 按空间形状分块 → 块均值作为代表 token；
  2. 代表 token 间相似度 → 预测稀疏掩码；
  3. token 通过 `[t, h, w]` 3D 窗口重排，使块内更相似，提升稀疏命中率与硬件效率；
  4. 保留首帧 sink token 做全注意力，其余按稀疏掩码执行。
- **掩码预测路径（ada_bsa）**：基于 CDF 阈值动态估计稀疏块集合，并通过 `keep_sink`、`keep_recent`、`cdf_threshold` 控制保留哪些 token。
- **执行路径**：在 Ascend NPU 上，仅对被掩码"命中"的关键 token pair 跑注意力计算，实现硬件级跳算。

### 性能数据（原文摘录）

- **原文**：rf_v2 在 Ascend NPU、**80% 稀疏率**下达成 **1.5–1.8x 端到端加速**，质量指标"近匹配"全注意力。
- **原文**：默认稀疏建议——图像任务从 **0.6** 起步、视频任务从 **0.8** 起步，需根据生成质量微调。

---

## 【表格解读】

**原文表格（逐字还原）：**

| Parameter | Required | Description |
| ------ | ------ | ------ |
| `sparse_type` | No | Sparse strategy: `None` (full attention), `"rf_v2"`, `"ada_bsa"` |
| `sparsity` | No | Sparsity rate, range `[0, 1]`, `0` means no sparsification |
| `txt_len` | No | Text token length, only effective when `sparse_type="rf_v2"` |
| `latent_shape_q` | No | Query latent space shape `[t, h, w]`, only effective when `sparse_type="rf_v2"` |
| `latent_shape_k` | No | Key latent space shape `[t, h, w]`, only effective when `sparse_type="rf_v2"` |
| `keep_sink` | No | Whether to keep sink tokens, only effective when `sparse_type="ada_bsa"` |
| `keep_recent` | No | Whether to keep recent tokens, only effective when `sparse_type="ada_bsa"` |
| `cdf_threshold` | No | CDF threshold, only effective when `sparse_type="ada_bsa"` |

**逐行解读：**

- **`sparse_type`**（非必填）：稀疏策略开关，取值 `None` 表示退化为全注意力，`"rf_v2"` 与 `"ada_bsa"` 对应两种实现——决定后续哪些参数生效。
- **`sparsity`**（非必填）：稀疏率，取值 `[0, 1]`，`0` 表示不稀疏化（即全注意力）。是控制加速–质量权衡的核心旋钮。
- **`txt_len`**（非必填，仅 `rf_v2` 有效）：文本 token 长度，用于在多模态 DiT 中区分文本/图像 token 段，影响掩码生成与重排。
- **`latent_shape_q`**（非必填，仅 `rf_v2` 有效）：Query 的潜空间三维形状 `[t, h, w]`，用于触发时空 token 重排。
- **`latent_shape_k`**（非必填，仅 `rf_v2` 有效）：Key 的潜空间三维形状 `[t, h, w]`，与 `latent_shape_q` 配合完成 3D 窗口重排。
- **`keep_sink`**（非必填，仅 `ada_bsa` 有效）：是否保留 sink token（即首帧等"注意力锚点"），是 ada_bsa 内置的质量保险机制。
- **`keep_recent`**（非必填，仅 `ada_bsa` 有效）：是否保留近期 token，控制局部性偏置。
- **`cdf_threshold`**（非必填，仅 `ada_bsa` 有效）：CDF 阈值，决定稀疏块集合的入选门槛，是 ada_bsa 灵活粒度的核心参数。

> 解读结论：该表清晰呈现了"**总开关 + 策略专属参数**"的两层设计：`sparse_type` 是顶层路由，`sparsity` 是通用调节旋钮，其余 6 项均按策略生效，体现了 rf_v2 重排/代表 token 路线与 ada_bsa CDF 路线在控制面上的解耦。

---

## 【公式解读】

**原文无公式**。

文档未给出任何 LaTeX 公式或伪代码形式的数学表达，所有机制均以自然语言描述呈现。

---

## 【关联】

依据原文末尾的内部链接，可识别如下上下游关系：

1. **指向 [RainFusion2.0 技术报告](../../tech_report/Rainfusion2.0.pdf)**：
   - rf_v2（RainFusion2.0）的完整技术细节——包括 Block Representative Token Prediction、Spatio-Temporal Token Reordering、First-Frame Sink Mechanism 的算法推导、稀疏模式构造与硬件映射分析——以 PDF 技术报告为准，本文档仅给出高层概述与关键性能结论（80% 稀疏、1.5–1.8x）。

2. **指向 [core_layers.md 的 sparse_attention 小节](core_layers.md#sparse_attention)**：
   - 本文 `sparse_attention` API 的**完整参数说明**（含默认值、取值约束、形状推导规则等）依赖该小节；本文表格仅给出"快速参数参考（Quick Parameter Reference）"，定位是精简速查表，详细定义需跳转 core_layers.md。

3. **与套件其他特性的隐含关系**：
   - 文档定位为"昇腾亲和的多模态加速系列套件"中的稀疏注意力模块，是面向 **DiT 类扩散模型**推理加速的核心算子之一，与 lightx2v、vLLM Omni、Diffusers+CacheDit 等上层框架通过统一 `sparse_attention` 接口对接，但本文档未直接展开这些上层框架的接入细节。

---

## 【使用方法】

### 启用方式（原文摘录）

通过 `sparse_attention` API 启用，原文给出最小调用形态：

```python
from mindiesd import sparse_attention
out = sparse_attention(q, k, v, head_num=24, input_layout="BNSD", sparse_type="rf_v2", sparsity=0.8)
```

### 图像模型示例（原文逐字）

```python
import torch
from mindiesd import sparse_attention

q = torch.randn(2, 24, 4096, 128, device="npu", dtype=torch.float16)
k = torch.randn(2, 24, 4096, 128, device="npu", dtype=torch.float16)
v = torch.randn(2, 24, 4096, 128, device="npu", dtype=torch.float16)

out = sparse_attention(q, k, v, head_num=24, input_layout="BNSD", sparse_type="rf_v2", sparsity=0.6)
```

### 视频模型示例（原文逐字）

```python
out = sparse_attention(
    q, k, v,
    head_num=24,
    input_layout="BNSD",
    sparse_type="rf_v2",
    sparsity=0.8,
    latent_shape_q=[t, h, w],
    latent_shape_k=[t, h, w],
)
```

### 调试与约束（原文逐字）

- **稀疏率–加速–质量权衡**：参考实验数据为 `sparsity=0.8` 下 **1.5–1.8x 端到端加速**且质量近匹配全注意力；图像任务建议从 **0.6** 开始调试，视频任务从 **0.8** 开始。
- **`block_size` 参数**：**当前仅支持 128**。
- **推理方向**：API **仅提供前向推理，不支持反向梯度计算**。
