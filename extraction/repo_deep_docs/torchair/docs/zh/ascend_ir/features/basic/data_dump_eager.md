# 算子data dump功能（Eager模式）

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/data_dump_eager.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/data_dump_eager.md

# 一体化深度解读：算子 data dump 功能（Eager 模式）

---

## 【定位】

本篇文档描述 TorchAir 在 **Eager 模式**下对图计算过程中算子的**输入/输出数据进行 dump** 的能力，用于后续对算子运行性能或精度问题进行定位与分析。

---

## 【技术要点】

1. **生效前提与互斥约束**：仅在 Eager 模式下生效；开启后，**GE 图模式相关的功能配置均不生效**（原文："开启该功能后，GE图模式相关的功能配置均不生效"）。
2. **启用入口**：通过 `torchair.get_npu_backend` 接收的 `CompilerConfig` 中的 `config.debug.data_dump.*` 子项配置。
3. **三个核心配置项**：
   - `data_dump.type`：指定 dump 文件类型，字符串，默认 `None`（不导出），当前仅支持 `"npy"`。
   - `data_dump.filter`：用户自定义过滤函数，输入为 `torch.fx.Node` 实例 `n`，返回 `Node` 实例或 `None`，默认 `None`（不过滤）。
   - `data_dump.path`：dump 文件生成路径，字符串，默认当前执行路径；要求路径存在并具备读/写权限。
4. **filter 过滤函数的工程实践**：依赖 `graph_dump`（`config.debug.graph_dump.type = "py"`）先 dump 出图，搜索"FX Code"后字段即对应 `n.name`（如 `add_1`、`sub`）。
5. **产物命名格式**： `${op_type}-${aten_ir}.${param_type}${param_idx}${timestamp}.npy`，附加 `${world_size}` 与 `${global_rank}` 标识集合通信上下文。
6. **产物目录组织**：以 `worldsize${world_size}_global_rank${global_rank}` → `graph_*` → 步次序号（从 0 开始）→ `.npy` 文件四级嵌套呈现；单卡时为 `worldsize1_global_rank0`。

---

## 【关键机制与数据】

**工作原理 / 数据流（基于原文推断的语义）**：

- 数据流发生在 **Eager 模式下的图计算过程**中，每个被命中（filter 命中或默认不过滤）的算子会针对其**输入张量与输出张量**分别落盘为 `.npy` 文件。
- 过滤决策点位于 `data_dump.filter`（`lambda n: ...`），其依据是 `Node` 实例的属性（如 `n.name`）。
- 命中后生成的 `.npy` 文件同时携带 **算子类型（op_type）**、**ATen 算子名（aten_ir）**、**参数方向（INPUT/OUTPUT）**、**参数索引** 与 **时间戳**。
- 在集合通信场景下，目录路径会携带 `${world_size}` 与 `${global_rank}`，便于多卡协同排查。

**性能数据**：原文未涉及。

---

## 【表格解读】

### 表 1 参数说明（原文逐字还原）

| 参数名 | 参数说明 |
|---|---|
| data_dump.type | 指定dump文件类型，字符串类型。默认为None，表示不导出dump数据。若设置，当前仅支持npy格式。 |
| data_dump.filter | 用户自定义过滤函数，保留满足函数条件的内容。<br>输入：PyTorch中的Node类的实例n。<br>输出：PyTorch中的Node类的实例n或者None。<br>默认值为None，表示不过滤任何内容。<br>说明：Node类实例化的各属性（如name、target等）获取方法主要通过图结构dump功能获取。<br>以常见的name属性为例，获取方法如下：<br>1. 先以py格式dump图信息。config.debug.graph_dump.type = "py"<br>2. 在当前执行路径下生成dynamo_*.py，示例如下，搜索关键词"FX Code"，其后面字段对应n.name属性信息。<br># File "/home/a.py", line 32, in forward    x=x+y<br>## FX Code: **add_1**: torch.float32[s0, s0]npu:0 = torch.ops.aten.add.Tensor(add: torch.float32[s0, s0]npu:0, arg2_1: torch.float32[s0, s0]npu:0)<br>Add_1_0 = ge.Add(Add_0, arg2_1_0, node_name="Add_1")<br># File "/home/a.py", line 36, in forward    x=x-1<br>## FX Code: **sub**: torch.float32[s0, s0]npu:0 = torch.ops.aten.sub.Tensor(mul_1: torch.float32[s0, s0]npu:0, 1)<br>Sub_0 = ge.Sub(Cast_1_0, ge.Const(1, dtype=0), node_name="Sub") |
| data_dump.path | 设置dump文件生成的路径，字符串型。可选配置，如果不设置，默认为当前执行路径。<br>请确保参数中指定的路径真实存在，并且运行用户具有读取和写入权限。 |

### 逐行解读

- **data_dump.type**：唯一受控开关；默认 `None` 即"不导出"。当前版本对文件类型的可选项是封闭的（仅 `npy`），其余取值会越界，因此若开启 dump 必须显式置为 `"npy"`。
- **data_dump.filter**：本质是一个**保留谓词**——返回 `Node` 表示保留该节点对应的 dump，返回 `None` 表示丢弃。它把"哪些算子的输入/输出需要落盘"开放给用户；其依赖的 `Node` 属性需要通过 `graph_dump` 提前导出（示例为 `py` 格式）后阅读 `dynamo_*.py` 中"FX Code"后的标识符获取（如 `add_1`、`sub`），再据此写过滤 lambda。
- **data_dump.path**：落盘路径；缺省为当前执行路径。原文以**前置可访问性**作为约束（路径必须存在、运行用户需有读/写权限），意味着路径不存在或权限不足时 dump 行为不在本文档的承诺范围之内。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **配置入口 / 上游**：[`torchair.get_npu_backend`](../../api/torchair/get_npu_backend.md)——`data_dump` 是其接收的 `compiler_config` 中 `config.debug` 子树的配置项，因此该特性需配合 `torch.compile(model, backend=npu_backend)` 一起生效。
- **互斥特性**：与"GE 图模式相关功能配置"互斥——开启 `data_dump` 后，所有 GE 图模式侧的功能配置（如 GE 侧 graph 优化、GE 侧 dump 等）均不再生效。
- **配套能力**：与 `config.debug.graph_dump.type = "py"` 形成**前后置依赖**——`graph_dump` 负责先 dump 出 `dynamo_*.py` 来探查 `Node.name`，`data_dump.filter` 再据此实现精确过滤 dump。

---

## 【使用方法】

### 代码示例（原文示例，仅供参考）

```python
import torch, torch_npu, torchair
config = torchair.CompilerConfig()
# Eager模式下数据dump功能
config.debug.data_dump.type = "npy"
config.debug.data_dump.path = "./test"
# 若只dump'add_1'和'sub'算子，n.name为Node类实例化的name属性
config.debug.data_dump.filter = lambda n: n if n.name in ['add_1', 'sub'] else None
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

### 启用步骤（按原文语义梳理）

1. 在 `CompilerConfig` 下设置 `config.debug.data_dump.type = "npy"`，开启 dump。
2. （可选）设置 `config.debug.data_dump.path = "<dir>"` 指定输出目录，要求目录存在且具备读/写权限。
3. （可选）设置 `config.debug.data_dump.filter = lambda n: ...`，按 `Node` 属性（如 `n.name`）进行算子过滤；过滤目标的 `name` 来源于 `config.debug.graph_dump.type = "py"` 导出的 `dynamo_*.py` 中"FX Code"字段。
4. 将上述 `config` 传入 `torchair.get_npu_backend(compiler_config=config)`，再以 `torch.compile(model, backend=npu_backend)` 编译目标模型即可生效。

### 产物形态（原文逐字）

- 文件名模板：`${op_type}-${aten_ir}.${param_type}${param_idx}${timestamp}.npy`，附加 `${world_size}` 与 `${global_rank}`。
- 目录组织：`worldsize${world_size}_global_rank${global_rank}` → `graph_*` → 步次序号（从 0 开始）→ `.npy` 文件；单卡示例为 `worldsize1_global_rank0`。
