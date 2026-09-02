# 集合通信入图

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/communication_graph.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/communication_graph.md

# 集合通信入图 — 一体化深度解读

---

## 【定位】
本文档描述 TorchAir NPU 图编译后端（`npu_backend`）对集合通信算子（collective communication）入图（graph capture）能力的支持：使 `torch.compile` 下游的图编译后端原生接管 `torch.distributed.*` 与 `torch_npu.distributed.*` 中的集合通信算子，避免因通信算子导致断图（graph break），并在整图层面获得通信-计算并行调度与算子融合收益。

---

## 【技术要点】

1. **入图范围扩展**：集合通信算子入图后，原 PyTorch 脚本中所有能以 Eager 模式正常运行的算子均可被纳入同一张计算图，从而相比默认按"遇到通信算子即断图"的策略拥有更大的成图范围。
2. **整图并行优化**：在整图（whole-graph）层面同时调度通信与计算，使通信流水与计算流能够以图级 IR 的形式进行并行/重排优化（原文："在整图层面实现通信与计算并行优化"）。
3. **Ascend Converter 实现**：TorchAir 在 NPU 图编译后端内部为集合通信算子实现了专用的 Ascend Converter，调用 `torch.compile` 时即默认生效，无需额外 API 开启。
4. **覆盖的集合通信 API**：同时覆盖 `torch.distributed` 与 `torch_npu.distributed` 两类命名空间下的常见算子，包括 `all_gather` / `all_reduce` / `broadcast` / `all_to_all` / `reduce_scatter` / `send` / `recv` 等 11 种（详见表 1）。
5. **动态 Shape 与 send/recv 的 FX 图分裂**：在 `dynamic=True` 场景下，`torch.distributed.send` 与 `torch.distributed.recv` 的不同 shape 会对应不同的 FX graph，即同一对 send/recv 节点会因为 shape 变化生成多张 FX 图。
6. **多 send/recv 时的图遍历顺序约束**：图中存在多个 `torch.distributed.send`、`torch.distributed.recv` 时，需要将图遍历顺序设置为 StableRDFS（稳定拓扑序策略），以保证调度顺序确定。

---

## 【关键机制与数据】

**工作原理（原文表述综合还原）**：

- 入口路径：用户在多卡模型上调用 `torch.compile(model, backend=npu_backend)` → `npu_backend`（即 `torchair.get_npu_backend(compiler_config=config)`）默认已携带"集合通信算子入图"的 Converter 链。
- 触发前提（原文）："`集合通信算子入图的前提是PyTorch脚本中所有算子均能正常以Eager模式运行`"——即脚本必须能在 Eager 模式下跑通，图编译才会尝试收集整图。
- 收益方向（原文）："`能够避免断图，并拥有更大的成图范围，从而获得更大的资源调度与融合收益，同时在整图层面实现通信与计算并行优化`"。该文档未给出量化的吞吐/延迟数字。
- 与原生 PyTorch 的对比（原文）："`原生PyTorch社区对集合通信算子入图的支持度尚不完善，功能正在持续增强中`"，TorchAir 通过自研 Converter 弥补这一缺口。

**关于 `send`/`recv` 的分组（group）约束（原文）**：

- 不传 `group` 参数（max-autotune 模式下）：所有节点必须都有 send/recv 或提前建好全局默认通信域。
- 传入 `group` 参数（max-autotune 模式下）：该 group 应当只包含参与该次通信的节点子集，避免错配。

**关于 `reduce_scatter_tensor_uneven` 的算子约束（原文）**：`op` 参数不支持配置为 `dist.ReduceOp.PRODUCT`。

> 原文未提供量化性能数据（无时延/吞吐/加速比数字）。

---

## 【表格解读】

**原文表 1 逐字还原**：

| PyTorch 集合通信 API | 支持情况 |
|---|---|
| torch.distributed.all_gather | √ |
| torch.distributed.all_gather_into_tensor | √ |
| torch.distributed.all_reduce | √ |
| torch.distributed.all_to_all | √ |
| torch.distributed.all_to_all_single | √ |
| torch.distributed.broadcast | √ |
| torch.distributed.reduce_scatter_tensor | √ |
| torch_npu.distributed.all_gather_into_tensor_uneven | √ |
| torch_npu.distributed.reduce_scatter_tensor_uneven | √ |
| torch.distributed.send | √ |
| torch.distributed.recv | √ |

**逐行解读**：

- **torch.distributed.all_gather** —— 标准 all_gather（list-of-tensors 形式），原生 `torch.distributed` 接口，入图支持。
- **torch.distributed.all_gather_into_tensor** —— tensor-in / tensor-out 形式的 all_gather，避免 list 包装开销，原生 `torch.distributed` 接口，入图支持。
- **torch.distributed.all_reduce** —— 跨卡归约（如 SUM/MAX/MIN/AVG），原生 `torch.distributed` 接口，入图支持。
- **torch.distributed.all_to_all** —— 通用 all_to_all（list-of-tensors），原生 `torch.distributed` 接口，入图支持。
- **torch.distributed.all_to_all_single** —— 单 tensor 版的 all_to_all（输入/输出各为一个 tensor），原生 `torch.distributed` 接口，入图支持。
- **torch.distributed.broadcast** —— 从 src rank 向同 group 其余 rank 广播 tensor，原生 `torch.distributed` 接口，入图支持。
- **torch.distributed.reduce_scatter_tensor** —— tensor-in / tensor-out 形式的 reduce_scatter，原生 `torch.distributed` 接口，入图支持。
- **torch_npu.distributed.all_gather_into_tensor_uneven** —— uneven 切分的 all_gather_into_tensor，昇腾 NPU 扩展接口（`torch_npu` 提供），用于各 rank 输入长度不一致的场景，入图支持。
- **torch_npu.distributed.reduce_scatter_tensor_uneven** —— uneven 切分的 reduce_scatter_tensor，昇腾 NPU 扩展接口（`torch_npu` 提供），但注意 `op` 参数不支持 `dist.ReduceOp.PRODUCT`。
- **torch.distributed.send** —— 点到点发送，原生 `torch.distributed` 接口，需与 `recv` 配套使用；`dynamic=True` 时按 shape 生成不同 FX 图。
- **torch.distributed.recv** —— 点到点接收，原生 `torch.distributed` 接口，需与 `send` 配套使用；约束与 `send` 对称。

**表格整体观察**：11 个 API 全部标注为 √（支持），按来源分——`torch.distributed` 主线接口 9 个，`torch_npu.distributed` 的 uneven 扩展接口 2 个；按语义分——集合类 9 个（all_*/broadcast/reduce_scatter），点到点类 2 个（send/recv）。

---

## 【公式解读】

**原文无公式**（无 LaTeX、伪代码或数学表达式）。

---

## 【关联】

本文档未提供内部链接，**无内嵌的超链接到其他特性/模块**，但从行文内容可推断出与之密切相关的上下游：

- **上游依赖**：`torch.compile`（PyTorch 官方 dynamo 图编译入口）、`torch.distributed` 与 `torch_npu.distributed`（集合通信算子来源）、`torch_npu` 插件本身。
- **下游关联**：`npu_backend = torchair.get_npu_backend(compiler_config=config)` 通过 `CompilerConfig` 接入——因此集合通信入图能力受 `CompilerConfig` 项的约束，例如其与 `mode='max-autotune'` 的交互（决定 send/recv 是否要默认通信组、是否需要 StableRDFS 拓扑序）。
- **并列特性**：文档以"NPU 图编译后端 `npu_backend` 默认已支持集合通信算子入图"这一句话与其他特性区分开来，暗示集合通信入图是 `npu_backend` 内置能力而非独立开关。
- **同仓其他 docs/zh/ascend_ir/features/basic 路径下的文档**：本文未点名引用，但属于同目录基础特性系列。

---

## 【使用方法】

**启用方式（原文表述）**：

> "无需修改PyTorch脚本，直接调用torch.compile，NPU图编译后端 npu_backend 默认集成了集合通信算子入图能力。"

即：**集合通信入图无需额外开关**，在调用 `torch.compile` 并使用 `npu_backend` 时自动生效。

**原文给出的最小示例代码（逐字保留）**：

```python
import torch
import torch_npu
import torchair
config = torchair.CompilerConfig()
npu_backend = torchair.get_npu_backend(compiler_config=config)
# ...
# 多卡模型调用compile，后端提供集合通信入图能力
model = torch.compile(model, backend=npu_backend)
```

**配置项与约束（原文）**：

1. **Eager 可运行性前提**：PyTorch 脚本中所有算子均能正常以 Eager 模式运行，否则会影响入图（甚至破坏编译）。

2. **`torch.distributed.send` / `torch.distributed.recv` 专项约束**：
   - 必须**配套使用**（成对出现）；
   - `dynamic=True` 场景下，**不同的 shape 会对应不同的 FX graph**——若要避免图数量膨胀，可关掉 dynamic shape；
   - `max-autotune` 模式下：
     - **不传 group 参数** 时，需要有默认通信组（`所有节点都有send/recv` **或** `提前建好全局默认通信域`）；
     - **传入 group 参数** 时，该 group 应当**只包含参与通信的节点**；
     - 图中存在 **多个** `send`/`recv` 时，需设置图遍历顺序为 **StableRDFS（稳定拓扑序策略）**。

3. **`torch_npu.distributed.reduce_scatter_tensor_uneven`** 算子级约束：**`op` 参数不支持配置为 `dist.ReduceOp.PRODUCT`**（除此之外的常见 op 应按 PyTorch 文档与昇腾支持情况使用）。

> 注：原文档未涉及更细粒度的 Config flag、环境变量、性能调优参数——若需要这些开关，需参考 `CompilerConfig` 的总体说明（本文未给出链接）。
