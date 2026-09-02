# 图优化特性介绍

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/graph_optimization/overview.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/graph_optimization/overview.md

# 图优化特性文档深度解读

## 【定位】

这篇文档介绍了 TorchNPU 在昇腾 NPU 上为弥补开源 PyTorch 对昇腾适配性不足、图优化能力欠缺的问题，所实现的一套基于 PyTorch Inductor 编译器的自定义图优化 pass 体系，并说明了其前置条件、调用示例、调试日志方式与优化效果。

---

## 【技术要点】

1. **背景与动机**：开源 PyTorch 对昇腾适配性较弱、对不同模型的图优化能力不足；TorchNPU 通过自定义优化 pass 增强 Inductor 的图优化能力以提升模型性能。当前 pass 主要应用于**模型推理**阶段。
2. **两阶段 Pass 划分**：优化 pass 分为 **pre（前置）** 与 **post（后置）** 两个图优化阶段。
3. **Pre 阶段 Pass（共 3 个）**：`cat_slice_cat_fold_pass`、`pad_slice_fold`、`fusion_attention_v3_pass`。
4. **Post 阶段 Pass（共 21 个）**：`fold_four_op_pass`、`fold_cast`、`fold_cat`、`fold_clone`、`fold_expand`、`fold_detach`、`fold_reduce`、`fold_sink_view`、`fold_slice`、`fold_squeeze`、`fold_to_copy`、`view_fold_pass`、`fold_where`、`fold_redundant_ops`、`dtype_optimal_pass`、`cat_to_view_pass`、`repeat_to_expand_pass`、`fold_iota_arithmetic_pass`、`broadcast_const_mask_compress`、`masked_add_compose_pass`、`bool_cast_mul_to_where_pass`、`sign_diff_hamming_fuse_pass`、`batch_embedding_fusion_pass`。（原文 post 列表共 23 项，含 `fold_four_op_pass` 在内。）
5. **前置条件三条**：① 已安装 TorchNPU 包（版本需匹配 PyTorch）；② 机器配备 Ascend NPU 并正确安装驱动和运行时；③ PyTorch 版本 **>= 2.0** 以支持 `torch.compile`。
6. **编译调用核心三要素**：`torch.compile(..., backend="inductor", dynamic=False)`，编译时**默认即使能**图优化 pass，无需额外开关；日志级别通过环境变量 `INDUCTOR_ASCEND_LOG_LEVEL=DEBUG` 打开以观察 pass 生效情况。
7. **Pass 注册机制（来自日志原文）**：所有 pass 均通过 `torch_npu._inductor.fx_passes.ascend_custom_passes.ascend_graph_pass` 模块注册，统一标记为 `pass_type=PassType.PRE` 或 `PassType.POST`，粒度为 `fx_pass_level=FxPassLevel.LEVEL1`。

---

## 【关键机制与数据】

**工作原理 / 数据流（原文描述）：**

1. 整体链路：CANN 异构计算架构 → 开源 PyTorch 框架 → TorchNPU 适配插件接入 Ascend AI 处理器 → 利用 PyTorch Inductor 编译器能力 → 在 Inductor 的 pre/post 图优化阶段插入昇腾自定义 pass → 进一步提升模型性能（原文："TorchNPU 利用 PyTorch 中的 Inductor 编译器能力，实现模型的加速编译…通过自定义的优化 pass…增强图优化能力"）。
2. Pass 作用阶段（原文）："当前 pass 主要应用在模型推理过程中，pre/post 两个图优化阶段"。
3. 效果验证方式（原文）：通过 `INDUCTOR_ASCEND_LOG_LEVEL=DEBUG` 打印 `Registering function … from module torch_npu._inductor.fx_passes.ascend_custom_passes.ascend_graph_pass with pass_type=…, fx_pass_level=FxPassLevel.LEVEL1` 日志来判断 pass 是否生效。

**性能数据**：原文未提供任何量化性能数据（无 latency、吞吐、加速比等数字），仅给出"优化前/优化后"的代码形态对比作为效果示例，因此无可引用数据可写。

**优化效果示例（原文代码逐字）：** 以 `pad_slice_fold` 为例：

```python
# 优化前
def op_calc(self, t1):
    inputPad = torch._C._nn.pad(t1, [0, 0, 0, 50], "constant", 0.0)
    inputSlice = inputPad[:50, :]
    output = torch.relu(inputSlice)
    return output
```
↓
```python
# 优化后
def op_calc(self, t1):
    inputSlice = t1[:50, :]
    output = torch.relu(inputSlice)
    return output
```

含义：`pad + slice` 组合被折叠为直接 slice，原 `pad` 节点被消除，避免冗余内存分配。

---

## 【表格解读】

**原文无表格。**（文档以 pass 名称列表（plain text 代码块）与代码示例形式呈现，无表格化结构。）

---

## 【公式解读】

**原文无公式。**（文档仅含 Python 代码示例、plain text 列表、bash 环境变量命令，无 LaTeX/伪代码形式的公式。）

---

## 【关联】

1. **上游架构**：CANN（华为计算加速网络）异构计算架构 → 支撑多种 AI 框架；本特性属于"基于开源 PyTorch + TorchNPU 适配昇腾 AI 处理器"这条链路上的编译优化层。
2. **编译器依赖**：PyTorch `torch.compile` 与 Inductor 后端（`backend="inductor"`）是承载这些自定义 pass 的容器；pass 接入点在 Inductor 的 pre/post 阶段。
3. **模块定位**：所有自定义 pass 统一注册自 `torch_npu._inductor.fx_passes.ascend_custom_passes.ascend_graph_pass` 模块，构成一个集中的 pass 注册表。
4. **Pass 类型体系**：pass 通过 `PassType.PRE` / `PassType.POST` 标记其作用阶段，通过 `FxPassLevel.LEVEL1` 标记在 FX Graph 上的优化层级（即属于 Inductor 框架层面 Level 1 的 FX pass）。
5. **覆盖的算子语义族**：从 pass 命名可读出多个优化维度——常量/类型折叠（`fold_cast`/`fold_cat`/`fold_clone`/`fold_detach`/`fold_expand`/`fold_reduce`/`fold_squeeze`/`fold_to_copy`）、视图合并（`view_fold_pass`/`fold_sink_view`/`cat_to_view_pass`/`repeat_to_expand_pass`）、算术与掩码优化（`fold_iota_arithmetic_pass`/`broadcast_const_mask_compress`/`masked_add_compose_pass`/`bool_cast_mul_to_where_pass`）、融合类（`fold_four_op_pass`/`fusion_attention_v3_pass`/`batch_embedding_fusion_pass`/`sign_diff_hamming_fuse_pass`）、冗余消除（`fold_redundant_ops`）、数据通路（`pad_slice_fold`/`cat_slice_cat_fold_pass`）、精度/类型优化（`dtype_optimal_pass`）。
6. **配套日志机制**：`INDUCTOR_ASCEND_LOG_LEVEL` 环境变量与 Inductor DEBUG 日志配合，用于在编译期观察每个 pass 的注册与生效。
7. **文档内/文末链接**：原文标注"内部链接: (无)"，未显式给出与其他文档的交叉引用。

---

## 【使用方法】

1. **环境前置**（原文）：① 安装 TorchNPU 包，版本需与 PyTorch 匹配；② 配备 Ascend NPU 并装好驱动与运行时；③ PyTorch 版本 **>= 2.0**。
2. **编译调用方式**（原文示例）：
   ```python
   import torch
   from torch._dynamo.testing import rand_strided
   import torch_npu

   shapeA, strideA = (50, 100), (100, 1)
   a = rand_strided(shapeA, strideA, device="npu", dtype=torch.float32)
   with torch.no_grad():
       optimized = torch.compile(
           op_calc, backend="inductor", dynamic=False
       )  # 使用PyTorch编译模式，选择后端backend="inductor",
           # 编译时默认使能图优化pass
       compile_result = optimized(a)  # 获取运行结果
   ```
   关键点：`backend="inductor"`、`dynamic=False`，**图优化 pass 默认即开启**，无需额外参数。
3. **调试日志开关**（原文）：通过环境变量 `INDUCTOR_ASCEND_LOG_LEVEL=DEBUG`（支持 `export INDUCTOR_ASCEND_LOG_LEVEL=DEBUG` 或在 Python 内 `os.environ["INDUCTOR_ASCEND_LOG_LEVEL"] = "DEBUG"`）打开 DEBUG 级别日志，观察 `Registering function ... from module torch_npu._inductor.fx_passes.ascend_custom_passes.ascend_graph_pass` 的打印以确认 pass 是否生效。
4. **当前适用范围**（原文）："当前 pass 主要应用在模型推理过程中"——明确为**推理**场景，未覆盖训练。

## 图文联合解读

- `image.png`: **1) 图中内容**
展示TorchNPU图优化编译流水线：xxx Model→Dynamo→**pre_grad_pass**（IR规范化，pre_grad_custom_pass扩展）→FallBack/Decompose→Decompose分解→**joint_graph_pass**（公共子表达式消除，joint_custom_post_pass扩展）→Graph Partitioning→**post_grad_pass**（kernel fuse/替换pointwise，post_grad_custom_pre_pass扩展）→Lowering融合→scheduler→CodeGen→Triton编译器。

**2) 技术结论**
图优化分为pre/joint/post三阶段递进式处理：AQT Autograd先规范化IR便于分析；联合阶段双向优化并加多重安全检查；post阶段做局部清理与算子降级。三个阶段均开放自定义pass扩展点，体现"标准化+可扩展"的编译架构。

**3) 与文档论点关系**
文档列出pre/post各pass名称，图中三个阶段恰好对应文档pre/post两组pass列表，并通过joint_graph_pass补全前向-后向联合优化环节，说明文档所列pass如何嵌入Inductor流水线，实现昇腾适配加速。
