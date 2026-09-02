# PyTorch FSDP2 后端特性介绍

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/fsdp2/fsdp2_basic_features.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/fsdp2/fsdp2_basic_features.md

# mindspeed-llm 知识库深度解读：PyTorch FSDP2 后端特性介绍

---

## 【定位】

这篇文档面向昇腾 LLM 分布式训练框架 mindspeed-llm 的使用者，系统介绍 PyTorch **FSDP2（Fully Sharded Data Parallel v2）** 后端的能力——即用 `torch.distributed.fsdp.fully_shard` 原位 API 替代 FSDP1 的 `FlatParameter` 包装器范式，通过逐参数分片（Per-Parameter Sharding）+ DTensor 底层 + 多精度策略 + 通信计算掩盖，构建一种"高组合性、可与 TP/Checkpointing 共存"的下一代分布式数据并行方案。

---

## 【技术要点】

1. **API 范式转变**：FSDP2 使用 `torch.distributed.fsdp.fully_shard` 对模型进行**原位（In-place）**并行化，不再需要 Python 类包装器；底层基石是 `torch.distributed.tensor.DTensor`。
2. **分片策略升级**：从 FSDP1 的"层内所有参数 flatten 为 1D `FlatParameter` 再切分"，升级为 FSDP2 的 **Per-Parameter Sharding**——每个 `nn.Parameter` 单独切分、管理，保留模型原始参数结构。
3. **参数生命周期五态**：`Fully Sharded`（静止，1/N 切片）→ `All-Gather`（准备，聚合为完整参数）→ `Compute`（计算，使用完整参数）→ `Reduce-Scatter`（同步，梯度切片归约）→ `Update`（更新，优化器用切片梯度更新切片参数）。本质是把 DDP 的 All-Reduce 拆为 **Reduce-Scatter + All-Gather**。
4. **逻辑/物理视图分离**：逻辑上参数仍呈现为完整 Tensor（例如 `[4096, 4096]`），编程体验与单卡一致；物理上由 `DeviceMesh` 定义设备拓扑，每卡持有 Local Tensor（例如 `[512, 4096]`，即 4096/512=8 倍分片，但原文示例用 [512, 4096] 暗示 4096/512=8，或更常见地 4096/512=8 倍 dim 0 分片；详见后文标注）。
5. **三精度策略**：通过 `MixedPrecisionPolicy(param_dtype, reduce_dtype, buffer_dtype)` 严格区分 **计算精度 / 通信精度 / Buffer 精度**。示例：`param_dtype=torch.bfloat16`（计算）+ `reduce_dtype=torch.float32`（通信累加）。
6. **组合性与多维并行**：天然支持 2D FSDP、FSDP+TP 等多维并行，因为 `DeviceMesh` 本身是多维描述的；与 Checkpointing 组合也因为不再有 `FlatParameter` 包装而变得容易。

> 注：原文示例给出"逻辑 [4096, 4096] / 物理 [512, 4096]"。按 4096÷512=8，若使用 8 卡分片则 1/N 比例成立；原文未显式说明 N=8，仅作形状示例使用，不应过度推断。

---

## 【关键机制与数据】

### 1. 显存优化的根本逻辑（原文）
> FSDP 通过对模型参数、梯度和优化器状态进行**切片 (Sharding)**，显著降低了显存占用……使得在单卡显存受限的情况下训练超大模型成为可能。

FSDP 相对于 DDP 的核心收益：**三类状态（参数 / 梯度 / 优化器状态）全部按 1/N 切片**，因此单卡静态显存约为 DDP 的 1/N（参数）+ 1/N（梯度）+ 1/N（优化器状态）。

### 2. 通信算子替换（原文）
DDP 的 `All-Reduce` 在 FSDP 中被分解为：
- 前向/反向前：**All-Gather**（把切片参数聚合成完整参数）
- 反向中：**Reduce-Scatter**（把完整梯度归约并切分为切片梯度）

### 3. 状态机驱动的生命周期（原文 图 `process.png` 描述）
| 阶段 | 显存内容 | 通信动作 |
|---|---|---|
| Fully Sharded | 切片参数 (1/N) | 无 |
| All-Gather | 完整参数 (临时) | All-Gather |
| Compute | 完整参数 | 无 |
| Reduce-Scatter | 切片梯度 | Reduce-Scatter |
| Update | 切片参数 + 切片优化器状态 | 无 |

### 4. 混合精度数据流（原文 代码注释）
```
Forward : Parameters (FP32 storage) → Cast to BF16 → Compute
Backward: Gradients (BF16)          → Cast to FP32 → AllReduce/Reduce
```
存储保持 FP32（精度无损），计算用 BF16（速度/显存收益），通信累加用 FP32（数值稳定）。

### 5. 版本与覆盖面（原文）
- FSDP2 自 **PyTorch 2.4** 起以**技术预览**形式引入。
- 本文示例基于 **PyTorch 2.7** 及以上版本。

### 6. 通信计算掩盖（原文 图 `prefetch.png` 描述）
FSDP2 实现 **Prefetching** 机制：在当前层 Compute 的同时，预取下一层的参数（提前发起 All-Gather），形成计算与通信的流水重叠，提升训练吞吐。

---

## 【表格解读】

**原文无表格。**

（原文仅包含两张示意图 `process.png` 与 `prefetch.png`，分别用于说明"参数生命周期五态"和"Prefetching 掩盖"，无可逐字还原的参数表/性能对比/配置项表。）

---

## 【公式解读】

**原文无公式。**

（文档全程为概念性叙述与代码示例，未出现任何 LaTeX 公式或伪代码形式的数学表达式。参数分片的尺寸关系仅以张量 shape 形如 `[4096, 4096] / [512, 4096]` 作示例性说明，未写作显式公式。）

---

## 【关联】

文档虽然未提供文末内部链接（原文标注"内部链接: (无)"），但通篇提到了多个上下游特性与组件，可梳理如下关系网：

### 上游/并列特性
- **FSDP1（Legacy）**：FSDP2 的前任，使用 `FlatParameter` 包装器；FSDP2 是为了解决其在"灵活性 + 组合性"上的痛点而被设计。
- **DDP（DistributedDataParallel）**：FSDP 的对比基准；FSDP 本质上是 DDP 的显存优化变体（All-Reduce → Reduce-Scatter + All-Gather）。
- **Tensor Parallel (TP)**：FSDP2 因 Per-Parameter Sharding 不破坏参数结构，可与 TP 自由组合（同属 mindspeed-llm 并行体系）。
- **Checkpointing（激活重计算）**：同理，FSDP2 的组合性使其容易与 Activation Checkpointing 叠加，进一步降显存。

### 底层依赖
- **`torch.distributed.tensor.DTensor`**：FSDP2 的底层基石，提供逻辑/物理视图分离。
- **`DeviceMesh`**：描述设备拓扑，使 FSDP2 天然支持多维并行（2D FSDP、FSDP+TP）。
- **`MixedPrecisionPolicy`**：来自 `torch.distributed.fsdp`，统一管理三类精度。

### 框架层映射（mindspeed-llm 上下文）
- FSDP2 在 mindspeed-llm 中作为可启用的并行后端选项之一，应与该框架内的 **TP / PP / EP / CP** 等并行维度共存，由统一的 DeviceMesh 配置驱动。
- 文档归类于 `docs/zh/pytorch/features/fsdp2/`，表明这是 PyTorch 后端下的 FSDP2 特性专题，与同目录下其他 FSDP2 进阶文档（如 `fsdp2_basic_features.md` 仅是基础篇，应还存在混合并行、调优等姊妹篇）形成系列。

---

## 【使用方法】

原文给出的可直接复用的配置入口较有限，仅涉及混合精度策略的一段示例代码：

```python
import torch
from torch.distributed.fsdp import MixedPrecisionPolicy

# FSDP2 混合精度转换流程
mp_policy = MixedPrecisionPolicy(
    param_dtype=torch.bfloat16,   # 计算精度：前向/反向时 cast
    reduce_dtype=torch.float32,   # 通信精度：Reduce-Scatter 时累加用
    # buffer_dtype=...            # Buffer 精度（原文提及但示例未设值）
)
```

### 关键 API（原文出现）
| API | 作用 |
|---|---|
| `torch.distributed.fsdp.fully_shard` | FSDP2 入口：对模型进行原位并行化 |
| `torch.distributed.fsdp.MixedPrecisionPolicy(param_dtype, reduce_dtype, buffer_dtype)` | 混合精度策略 |
| `torch.distributed.tensor.DTensor` | 分布式张量（逻辑/物理视图分离） |
| `DeviceMesh` | 设备拓扑描述（支撑多维并行） |

### 启用所需的版本前提（原文）
- 最低版本：**PyTorch 2.4**（FSDP2 技术预览起点）
- 推荐版本：**PyTorch 2.7+**（本文示例所用）

### 未涉及项（原文）
- **如何构造 `DeviceMesh` 并将其传入 `fully_shard`**——原文未给出示例；
- **如何与 TP/Checkpointing 组合的具体调用顺序与配置项**——原文仅概念性提及；
- **性能调优参数**（如 `forward_prefetch`、`backward_prefetch`、`limit_all_gathers` 等 FSDP2 关键开关）——原文未涉及；
- **mindspeed-llm 中如何启用 FSDP2 后端**（启动命令、配置文件 yaml 字段等）——原文未涉及，应需查阅该仓 `docs/` 下 FSDP2 系列的姊妹篇或启动器相关文档。
