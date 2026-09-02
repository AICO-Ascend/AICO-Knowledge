# 图结构dump功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/graph_dump.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/graph_dump.md

# 图结构dump功能 深度解读

## 【定位】

这篇文档描述 TorchAir 图模式场景下「图结构导出（dump）」能力：当模型执行出现异常（如精度不准确）时，通过开启 Python 层日志或配置 `compiler_config`，将原生 FX 图、ATen IR 转 Ascend IR 后的构图信息、以及最终的 TorchAir 构图结果导出为可读文件，供开发者定位与分析模型问题。

---

## 【技术要点】

1. **三层图导出能力**：
   - 层级一：开启 Python 层 logger (`logging.DEBUG`) 打印原生 **FX 图**结构（节点、args、kwargs）；
   - 层级二：通过 `CompilerConfig().debug.graph_dump` 配置 dump TorchAir 构图结果（支持 `py` / `txt` / `pbtxt` 三种格式）；
   - 层级三：（可选）通过 CANN 环境变量 `DUMP_GE_GRAPH` 查看 GE 图编译与执行后结构。

2. **三种导出格式及对应阶段**：
   - `py`：dump **ATen IR 转换为 Ascend IR 后的构图信息**（图1中的「阶段2构图信息」），VSCode 等可查看；
   - `txt`：dump 最终接收到的 TorchAir 构图结果，VSCode 等可查看；
   - `pbtxt`：dump 最终接收到的 TorchAir 构图结果的 **Protobuf 格式**，可用 TensorBoard、Netron 查看；
   - 默认值为 `None`，即不导出。

3. **核心配置参数**：
   - `config.debug.graph_dump.type`：字符串型，格式选项如上；
   - `config.debug.graph_dump.path`：字符串型，导出文件路径，默认当前执行路径；
   - 不支持三种格式同时导出，多次定义时以**最后一次**定义为准。

4. **产物文件命名规范**：
   - 原始图：`dynamo_original_graph_${graph_id}_rank_${rank_id}_pid_${pid}_ts_${timestamp}.${graph_dump_type}`
   - 优化图：`dynamo_optimized_graph_${graph_id}_rank_${rank_id}_pid_${pid}_ts_${timestamp}.${graph_dump_type}`
   - 变量含义：`graph_id`（第几张图）、`rank_id`（通信卡 id）、`pid`（进程号）、`timestamp`（时间戳）。

5. **典型 FX 图示例节点**：`placeholder`、`call_function`（如 `torch.ops.aten.select_scatter.default`、`torch.ops.aten.mul.Tensor`），每个节点带 `num_users`、args、kwargs 等元信息。

6. **`py` 导出文件核心 API**：使用 `torchair._ge_concrete_graph.ge_apis as ge` 与 `torchair.ge._ge_graph.get_default_ge_graph`，节点构造示例：`ge.Data`、`ge.Shape`、`ge.BroadcastTo`、`ge.ExpandDims`、`ge.ScatterElements`、`ge.Mul`、`ge.Cast`、`ge.NetOutput`。

---

## 【关键机制与数据】

**工作原理（原文叙述串联）**：

1. **FX 图打印机制**（原文）：设置 `logger.setLevel(logging.DEBUG)` 后，TorchAir 在 `npu_fx_compiler.py` 第 364 行附近输出原生 FX 图结构，内容形如：

   ```
   graph():
       %arg0_1 : [num_users=1] = placeholder[target=arg0_1]
       %arg1_1 : [num_users=1] = placeholder[target=arg1_1]
       %select_scatter : [num_users=1] = call_function[target=torch.ops.aten.select_scatter.default](args = (%arg0_1, %arg1_1, 0, 1), kwargs = {})
       %mul : [num_users=1] = call_function[target=torch.ops.aten.mul.Tensor](args = (%select_scatter, 10), kwargs = {})
       return (mul,)
   ```

   其中 `select_scatter` 的 args 为 `(%arg0_1, %arg1_1, 0, 1)`，`mul` 的 args 为 `(%select_scatter, 10)`。

2. **TorchAir 构图 dump 机制**（原文）：通过 `torchair.get_npu_backend(compiler_config=config)` 传入 `CompilerConfig`，触发 `config.debug.graph_dump.type` 与 `config.debug.graph_dump.path` 两项配置生效，从而在图执行完成后落盘构图文件。原文明确：**仅供参考，不支持直接拷贝运行**。

3. **GE 图 dump 机制**（原文）：通过 CANN 环境变量参考中的 `DUMP_GE_GRAPH` 章节开启，属于 GE 编译执行后的图信息导出。

4. **数据流（`py` 文件样例体现）**：FX `select_scatter` → ATen 算子分解为 `Shape` → `BroadcastTo`(标量1) → `ExpandDims`(对 arg1) → `BroadcastTo_1` → `ScatterElements`；FX `mul = select_scatter * 10` → `Mul`(`ScatterElements_0`, `Const(10)`) → `Cast` → `NetOutput`。

5. **示例数据**（原文）：`arg0_1` 的 shape 为 `[2, 2, 2]`，`arg1_1` 的 shape 为 `[2]`，dtype 编码 0（`DT_FLOAT`），placement 为 `"NPU"`。

6. **性能数据**：原文未涉及性能数据（如耗时、吞吐等）。

---

## 【表格解读】

**表1  参数说明**（逐字还原）

|参数名|参数说明|
|--|--|
|graph_dump.type|设置导出图结构文件的格式，字符串型，支持如下选项：<br>py：dump ATen IR转换为Ascend IR后的构图信息，即[图1](#fig1)中**阶段2构图信息**，可通过VSCode等工具查看。<br>txt：dump最终接收到的TorchAir构图结果，可通过VSCode等工具查看。<br>pbtxt：dump最终接收到的TorchAir构图结果，为Protobuf格式，可通过TensorBoard、Netron等工具查看。<br>graph_dump.type默认值为None，表示不导出图结构信息。|
|graph_dump.path|设置图结构文件生成的路径，字符串型。可选配置，如果不设置，默认路径为当前执行路径。|

**逐行解读**：

- **graph_dump.type 行**：唯一控制导出格式的开关。`py` 对应**编译期** ATen IR→Ascend IR 转换后的中间表达（最贴近问题源），适合排查算子分解、节点命名问题；`txt` 与 `pbtxt` 都是 TorchAir **最终构图结果**，区别仅在序列化方式——`pbtxt` 是 Protobuf 文本格式，可被 Netron/TensorBoard 渲染为可视化图结构，`txt` 是纯文本。默认 `None` 即不导出，避免运行时落盘开销。
- **graph_dump.path 行**：决定两类文件（`dynamo_original_graph_*` 与 `dynamo_optimized_graph_*`）的存放位置。原文强调需保证路径存在且用户具备读写权限，否则会写入失败。

---

## 【公式解读】

原文无数学公式。涉及的**伪代码/IR 表示**如下（按原文逐字保留）：

- **FX 图节点表示**：
  ```
  %arg0_1 : [num_users=1] = placeholder[target=arg0_1]
  %arg1_1 : [num_users=1] = placeholder[target=arg1_1]
  %select_scatter : [num_users=1] = call_function[target=torch.ops.aten.select_scatter.default](args = (%arg0_1, %arg1_1, 0, 1), kwargs = {})
  %mul : [num_users=1] = call_function[target=torch.ops.aten.mul.Tensor](args = (%select_scatter, 10), kwargs = {})
  return (mul,)
  ```
  **符号含义**：`%xxx` 为节点名（SSA 值）；`[num_users=1]` 表示该值被消费次数；`placeholder` 为图输入占位符；`call_function[...]` 调用 ATen 算子；`args` 为位置参数，`kwargs` 为关键字参数；本例中 `select_scatter` 的参数语义为 `(input, src, dim=0, index=1)`，`mul` 的参数为 `(input, other=10)`。

- **产物文件名模板**：
  ```
  dynamo_{original|optimized}_graph_${graph_id}_rank_${rank_id}_pid_${pid}_ts_${timestamp}.${graph_dump_type}
  ```
  **符号含义**：`graph_id` 为图序号；`rank_id` 为分布式通信卡 id；`pid` 为进程号；`timestamp` 为时间戳；`graph_dump_type` 为导出格式后缀（`py`/`txt`/`pbtxt`）。

---

## 【关联】

- **上游 API 关联**：第二节示例调用 `torchair.get_npu_backend(compiler_config=config)`（链接：`../../api/torchair/get_npu_backend.md`），本文档中 `CompilerConfig` 通过该入口生效，dump 参数位于 `config.debug.graph_dump` 子配置下。
- **下游生态关联**：与 CANN 《CANN环境变量参考》中 `DUMP_GE_GRAPH` 章节互补——本文档覆盖 TorchAir/FX/ATen→Ascend IR 阶段的图导出，GE dump 则覆盖**图编译与执行后**的 GE IR 图结构，二者形成「前端 FX → TorchAir 构图 → GE 编译执行」的完整排查链路。
- **与图1关系**：参数表中 `py` 格式明确指向「图1中的**阶段2构图信息**」，即 ATen IR → Ascend IR 转换后的中间表示，是排查算子分解阶段问题的主要依据。
- **算子映射关系**：FX `select_scatter` → Ascend IR `Shape + BroadcastTo + ExpandDims + BroadcastTo_1 + ScatterElements`，FX `mul` → `Mul + Cast`，体现 TorchAir 算子分解与类型转换过程。

---

## 【使用方法】

**方式一：开启 Python 层日志打印原生 FX 图**（原文）：

```python
import logging
from torchair import logger
logger.setLevel(logging.DEBUG)
```

**方式二：通过 `compiler_config` dump TorchAir 构图**（原文，**仅供参考，不支持直接拷贝运行**）：

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 设置图结构Dump参数
config.debug.graph_dump.type = "pbtxt"
config.debug.graph_dump.path = "./test"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

可替换的 `type` 值：`"py"` / `"txt"` / `"pbtxt"`（默认 `None` 不导出）。

**方式三：（可选）查看 GE 图结构**（原文）：参考《CANN环境变量参考》中「DUMP_GE_GRAPH」章节开启 GE 的 dump 图信息。

**约束与注意**（原文）：
- 多次定义导出格式时，**以最后一次定义为准**；
- **不支持** `txt`、`pbtxt`、`py` 三种格式同时导出；
- 必须确保 `path` 指定的路径**真实存在**，且运行用户具有**读取和写入权限**；
- 默认路径为当前执行路径（当 `path` 未设置时）。

## 图文联合解读

- `graph_dump_1.png`: **图文联合解读：**

**图示内容：** 流程图标题"torch.compile"，纵向展示6步编译流水线：①Dynamo trace生成FX图 → ②TorchAir公共图优化 → ③ATen IR转Ascend IR生成GE protobuf图 → ④TorchAir GE图优化 → ⑤protobuf图传给GE → ⑥GE编译与执行。右侧三个标注框分别对应三个dump介入点：阶段1-2通过`logger.setLevel(logging.DEBUG)`打印FX图；阶段4通过`config.debug.graph_dump.type`配置dump TorchAir构图；阶段6通过CANN环境变量`DUMP_GE_GRAPH=1`导出GE图。

**技术结论：** 图结构dump贯穿编译全链路，形成FX层→TorchAir构图层→GE图层的三段式诊断能力，覆盖从Python前端到底层执行的完整排查路径。

**与文档关系：** 该图作为"图1"直观呈现了"使用方法"小节中两种dump方案（Python日志打印与`compiler_config`配置）的代码执行时机与作用阶段，佐证文档论点——异常时可在不同编译阶段导出对应层级的图结构以辅助分析。
- `zh-cn_image_0000002237738428.png`: **图文联合解读：**

1) **图的内容**：该图展示了一个计算图（Graph）的拓扑结构。顶部有3个`Data`输入节点和1个`Const`常量节点；中间包含`TensorMove`、`ScatterNdUpdate`、`Assign`、`Add`等算子节点；最底部汇聚为`NetOutput`输出节点，箭头清晰表示数据流向。

2) **论证的技术结论**：图直观呈现了MindSpore/TorchAir IR中算子之间的**依赖关系与数据流**，证明dump功能可完整还原图中所有节点（含Const/TensorMove/Assign等中间算子），便于定位异常算子。

3) **与文档论点关系**：文档阐述"图模式异常时通过dump查看节点信息"——此图正是dump输出（即`graph_dump.type`导出）的可视化示例，佐证"导出图结构可辅助模型问题排查"的论点。
