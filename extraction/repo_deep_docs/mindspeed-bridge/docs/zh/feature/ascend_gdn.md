# Ascend GDN

> 仓 `mindspeed-bridge` · 路径 `docs/zh/feature/ascend_gdn.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-bridge/docs/zh/feature/ascend_gdn.md

# Ascend GDN Feature 文档深度解读

---

## 【定位】

本文档描述 mindspeed-bridge 仓中 **Ascend GDN 特性**：针对 Linear Attention 中 Gated Delta Net（GDN）模块在 Ascend NPU 上训练效率不足的问题，通过新增 AscendC 自定义算子实现 `flash_gated_delta_rule` 接口，在保留原 GDN 调用方式的同时，将核心计算路径替换为 NPU 亲和的自定义算子，从而提升 Qwen3-VL / Qwen3.5-VL / Qwen3-Next 等 Linear Attention 模型在 NPU 上的训练性能。

---

## 【技术要点】

1. **接口接入方式**：通过 `flash_gated_delta_rule` 接口接入 GDN 模块，将原 PyTorch 通用算子替换为 AscendC 自定义算子，实现"调用方式不变、底层算子替换"的透明优化（原文："在保留原有 GDN 调用方式的基础上，将部分核心计算替换为 AscendC 自定义算子实现"）。

2. **前向计算流程（6 步）**：
   - 步骤 1：`chunk_local_cumsum` 对 gating tensor 做 chunk 内局部累积；
   - 步骤 2：`chunk_scaled_dot_kkt_fwd` 构造 WY representation 所需的中间矩阵；
   - 步骤 3：`solve_tril` 求解下三角矩阵，得到 WY representation 矩阵 `A`；
   - 步骤 4：将输入 tensor 转换为 AscendC 算子所需的数据布局；
   - 步骤 5：调用 AscendC 自定义算子计算 `w`、`u`、hidden state、`v_new` 和最终输出；
   - 步骤 6（反向）：重计算前向中间结果，再通过 AscendC 自定义算子计算 `dq`、`dk`、`dv`、`dg`、`db`、`dh0`。

3. **算子混合策略**：当前实现采用 **Triton 辅助算子 + AscendC 自定义算子** 的混合方案完成整体计算流程（原文："结合已有 Triton 辅助算子和 AscendC 自定义算子完成整体计算流程"）。

4. **依赖的 NPU 自定义算子清单**（共 9 个，需编译后注册到 `torch.ops.npu.*`）：
   - `npu_recompute_wu_fwd`
   - `npu_chunk_gated_delta_rule_fwd_h`
   - `npu_chunk_fwd_o`
   - `npu_chunk_bwd_dv_local`
   - `npu_chunk_gated_delta_rule_bwd_dhu`
   - `npu_chunk_bwd_dqkwg`
   - `npu_prepare_wy_repr_bwd_da`
   - `npu_prepare_wy_repr_bwd_full`

5. **编译参数 `--soc` 取值**（必选，三种芯片型号）：
   - `ascend910b`：Atlas A2 训练系列产品；
   - `ascend910_93`：Atlas A3 训练系列产品；
   - `ascend950`：Ascend 950 系列产品。

6. **适配范围**：应用于 Qwen3-VL / Qwen3.5-VL / Qwen3-Next 等包含 Linear Attention 的模型训练场景，且要求模型中启用了 Gated Delta Net。

---

## 【关键机制与数据】

### 1. 文档识别出的性能热点（原文表述）

- **问题链路长**：GDN 计算链路较长，包含 gating 累积、WY representation 构造、hidden state 更新、输出计算四类步骤（原文："包含 chunk-wise gated delta rule 计算，涉及 gating 累积、WY representation 构造、hidden state 更新以及输出计算等步骤"）。
- **通用算子开销**：默认 PyTorch 实现中存在较多通用算子组合，带来额外调度开销和中间张量开销（原文："默认 PyTorch 实现中存在较多通用算子组合，可能带来额外的调度开销和中间张量开销"）。
- **场景敏感**：在长序列、多头以及较大 hidden dimension 场景下，GDN 前向和反向成为性能热点（原文："尤其在长序列、多头以及较大 hidden dimension 场景下，GDN 前向和反向计算会成为模型训练中的性能热点之一"）。
- **Triton 不亲和**：现有 Triton 优化方案在 NPU 上存在不亲和问题，性能收益不符合预期（原文："现有 Triton 优化方案在 NPU 芯片上存在不亲和问题，导致性能收益不符合预期"）。

### 2. 数据流概览（基于"解决思路" 6 步）

```
输入 gating tensor ──► chunk_local_cumsum ──┐
输入 K/Q tensor    ──► chunk_scaled_dot_kkt_fwd ──► solve_tril ──► 矩阵 A
                                                            │
                                                            ▼
输入 tensor ───────► AscendC 自定义算子 ◄── 布局转换 ◄───────┘
                         │
                         ▼
                 w, u, hidden state, v_new, 最终输出
```

反向过程：重计算前向中间结果 ──► AscendC 自定义算子 ──► dq, dk, dv, dg, db, dh0。

### 3. 预期性能收益（原文："使用效果"节）

原文只描述**定性**收益，未给出具体加速比/数字：

1. 减少 GDN 计算中的通用算子调度开销；
2. 优化 chunk-wise gated delta rule 的前向计算；
3. 优化 GDN 反向梯度计算；
4. 提升 Linear Attention 中 GDN 模块的训练效率。

**性能依赖因素**（原文明确列出）：实际收益与 **模型规模、序列长度、batch size、head 数量、输入 dtype、运行环境** 有关（原文未给出量化数据）。

### 4. 兼容性约束（原文："注意事项"）

- 精度前提：使用 **v26.1.0.beta2 及以后** 的 `torch_npu` 版本（原文："为避免已知精度问题，请使用 v26.1.0.beta2 及以后 torch_npu 版本"）。
- 算子未正确安装或注册时，开启后会触发运行时错误（原文："若 AscendC 算子未正确安装或注册，在开启 Ascend GDN 后可能会触发运行时错误"）。
- 编译必须指定匹配芯片型号，否则编译失败（原文："算子编译需指定具体芯片型号，芯片不匹配会导致编译失败"）。

---

## 【表格解读】

原文无表格。

（说明：文中虽在"算子编译"处列出了 `--soc` 可选值清单和 NPU 算子清单，但均以文本/列表形式给出，未构成 markdown 表格结构。）

---

## 【公式解读】

原文无公式。

（说明：文档未给出 LaTeX 或伪代码形式的数学公式。GDN 计算的内部数学定义——如 gating 累积公式、WY representation 构造、下三角矩阵求解等——仅以文字描述形式提及，未显式列出公式。）

---

## 【关联】

1. **上游模型 / 适用场景关联**（基于"使用场景"节）：
   - **Qwen3-VL**、**Qwen3.5-VL**、**Qwen3-Next** 等包含 Linear Attention 的模型训练场景；
   - 文档点名"Gated Delta Net"模块被启用是前置条件；
   - Ascend NPU 硬件 + AscendC 自定义算子已正确安装是底层依赖。

2. **代码仓内部关联**（原文指向的实现路径）：
   - `mindspeed_bridge/models/qwen_vl/modelling_qwen3_vl/flash_gated_delta_rule.py` —— Ascend GDN 主入口实现（原文："具体实现参见"）。

3. **外部仓库依赖**：
   - 算子源仓：`https://github.com/flashserve/flash-linear-attention-npu`，需切到 tag **`v26.1.0`**（原文 step1）；
   - 最新编译方式参考：`https://github.com/flashserve/flash-linear-attention-npu/tree/v26.1.0`（原文末尾引用）。

4. **示例脚本关联**：
   - 参考启用脚本：链接指向 `tests/st/shell_scripts/qwen35_9B_sft_tp1pp2_layer4.sh`（位于 `Ascend/MindSpeed-Bridge` 仓）；
   - 文中实际示例：`mindspeed_bridge/examples/models/vlm/qwen35_vl/qwen35_vl_9b_sft_4k_A3.sh`。

5. **与同类优化方案的隐含关联**：
   - 文档指出"现有 Triton 优化方案在 NPU 上不亲和"，Ascend GDN 因此被设计为 **Triton 辅助 + AscendC 主算子** 的混合实现，而非纯 AscendC 替代——这表明该特性与仓内其他可能存在的 Triton 优化路径构成"分工/补充"关系。

---

## 【使用方法】

### 启用方式（原文："使用方法"节）

在训练脚本中添加一行：

```python
model.use_ascend_gdn = True
```

即可使能该特性。

### 启用前提（原文："使用前提"节，三步编译）

**Step 1 — 仓库拉取**：
```shell
git clone https://github.com/flashserve/flash-linear-attention-npu
cd flash-linear-attention-npu
git checkout v26.1.0
```

**Step 2 — Run 包编译与安装**（以 Atlas A3 `ascend910_93` 为例）：
```shell
bash build.sh --soc=ascend910_93 --pkg \
  --ops=chunk_bwd_dv_local,chunk_bwd_dqkwg,chunk_gated_delta_rule_bwd_dhu, \
  prepare_wy_repr_bwd_da,prepare_wy_repr_bwd_full,chunk_fwd_o, \
  chunk_gated_delta_rule_fwd_h,recurrent_gated_delta_rule, \
  recompute_wu_fwd,causal_conv1d

./build_out/cann-ops-transformer-custom_linux-aarch64.run
```
（`--soc` 必选，可选 `ascend910b` / `ascend910_93` / `ascend950`）

**Step 3 — WHL 包编译**：
```shell
cd torch_custom/fla_npu
bash build.sh   # 一键脚本：torchnpugen 接入算子 → setup 编 whl → 安装 whl
```

### 验证算子可用（原文 Python 断言形式）

```python
torch.ops.npu.npu_recompute_wu_fwd
torch.ops.npu.npu_chunk_gated_delta_rule_fwd_h
torch.ops.npu.npu_chunk_fwd_o
torch.ops.npu.npu_chunk_bwd_dv_local
torch.ops.npu.npu_chunk_gated_delta_rule_bwd_dhu
torch.ops.npu.npu_chunk_bwd_dqkwg
torch.ops.npu.npu_prepare_wy_repr_bwd_da
torch.ops.npu.npu_prepare_wy_repr_bwd_full
```

### 推荐启用条件（原文："使用场景"节，4 条）

1. Qwen3-VL / Qwen3.5-VL / Qwen3-Next 训练场景；
2. 模型中启用了 Gated Delta Net；
3. 当前环境支持 AscendC 自定义算子；
4. 希望优化 GDN 前向和反向计算性能。

### 风险/版本要求（原文："注意事项"）

- 必须使用 **torch_npu v26.1.0.beta2 及以后** 版本以规避已知精度问题。
