# 算子data dump功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/data_dump.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/data_dump.md

# 算子 data dump 功能 — 一体化深度解读

---

## 【定位】

这篇文档描述了 TorchAir 中**算子级数据 dump 能力**——在 Ascend IR 图执行时把指定算子的输入/输出数据（或统计信息）落盘，用于在 GE 图模式下进行算子运行性能与精度的离线分析。它与已有的"图结构 dump"互补，二者可单独或共同使用。

---

## 【技术要点】

- **作用层级**：仅在 **GE 图模式**（即 `torch.compile` + `torchair.get_npu_backend`）下生效；非 GE 图模式不在覆盖范围。
- **主开关 `enable_dump`**：布尔型，默认 `False`，必须显式置 `True` 才能触发算子数据 dump。
- **三类控制维度**（同时生效）：
  1. **数据维度**：`dump_mode` 控制 dump 输入、输出或两者 (`input` / `output` / `all`，默认 `all`)；`dump_data` 控制内容类型 (`tensor` 实数据 / `stats` 统计 csv，默认 `tensor`)。
  2. **范围维度**：`dump_layer` 按算子名精确指定；`data_dump` scope 通过 Python `with` 语句块按代码区段指定；`dump_step` 按迭代号控制。
  3. **路径与精度维度**：`dump_path` 控制落盘根目录；`quant_dumpable` 控制是否保留"量化前"的可比对数据（默认 `False`，即采集量化后的数据）。
- **两种配置入口**：(a) 通过 `CompilerConfig.dump_config` 的多个 options 分散配置；(b) 通过单一 `dump_config_path` 指定 JSON 文件整体配置。文档**显式标注** JSON 方式为"推荐"，其余配置项"后续不再演进"，并且两者**不建议同时使用**——若同时配置则 `dump options` 优先级更高。
- **JSON 配置支持的三种 dump 场景**（互斥）：模型/单算子 Dump（`dump_op_switch`）、溢出算子 Dump（`dump_debug="on"`）、算子 Dump Watch 模式（`dump_scene="watcher"`），文档逐个给出完整 JSON 示例与使用约束。
- **`data_dump` scope 补充机制**：必须以 Python `with torchair.scope.data_dump():` 形式调用，与 `dump_layer` 取**并集**作为最终的 dump 算子集合，产物目录与 `dump_layer` 一致，可与表中**所有** dump options 配套使用。
- **算子名获取约定**：依赖 `DUMP_GE_GRAPH=3`（精简版 dump，仅打节点关系）导出 `ge_proto*.txt`，从 `op.name` 字段读取；文档给出精简示例 `Add1_in_0`、`Add2` 等。
- **dump 结果不可直读**：必须先转换为 numpy 格式，再通过 numpy 官方能力转为 txt 文档查看（文档最后一段未完，原文以"详细操作指导请参"截断）。
- **隐含约束**：`dump_layer` 中若算子输入涉及 `data` 算子，则 `data` 算子信息也会一并 dump 出来；watcher 模式下若 `layer` 与 `watcher_nodes` 同名或 `layer` 是集合通信类算子（`Hcom*`，例如 `HcomAllReduce`），则只导出 `watcher_nodes` 的 dump 文件。

---

## 【关键机制与数据】

- **工作流**：`torch.compile(model, backend=torchair.get_npu_backend(compiler_config=config))` → NPU 模型执行 → GE 引擎按配置将指定算子的 input/output 张量（或统计量）按既定目录结构落盘 → 用户通过 numpy 转换 + 文本查看对比精度/性能。
- **dump 数据目录结构（原文，非 dump_config_path 路径下的产物）**：

  ```
  ${dump_path}/${worldsize_global_rank}/${time}/${device_id}/${model_name}/${model_id}/${data_index}
  ```

  原文示例：`/home/dump/worldsize1_global_rank0/20241121145738/0/ge_default_20200808163719_121/1/0`。各字段含义文档明确定义：`${worldsize_global_rank}` 在单卡场景为 `worldsize1_global_rank0`；`${time}` 格式 `YYYYMMDDHHMMSS`；`${model_name}` 若包含 "."、"/"、"\\"、空格会被转换为下划线；`${data_index}` 与 `dump_step` 一致，未指定时从 0 起每次 +1。
- **`dump_data="stats"` 产物格式**：csv 文件，包含算子名称、输入/输出的数据类型、最大值、最小值等。文档给出工程方法学建议——"通常 dump 数据量太大并且耗耗时，可以先 dump stats 识别可能异常的算子，再 dump tensor 数据"。
- **量化场景（`quant_dumpable=True`）**：图编译过程可能优化量化前的输入/输出，因此默认 `False` 时无法保证获取量化前的 dump 数据；置 `True` 强制保留。
- **大模型调试建议**（原文）："对于大模型场景，通常 dump 数据量太大并且耗时长，建议 `dump_data` 配置为 `stats`"。
- **TorchNPU 默认行为交互**（原文）：TorchNPU 默认已开启 `exception` 类信息 dump（即 `dump_scene` 异常算子 Dump 配置），**通过 `dump_config_path` 配置的 exception dump 不会生效**。
- **原文未给出**：性能数据 benchmark、内存占用、dump 速度等数字指标（文档性质为功能说明）。

---

## 【表格解读】

### 表 1　`dump_config` 各参数说明（原文逐字还原）

| 参数名 | 说明 |
| --- | --- |
| enable_dump | 是否开启数据 dump 功能，bool 类型。<br>False（默认值）：不开启数据 dump。<br>True：开启数据 dump。 |
| dump_mode | dump 数据模式，用于指定 dump 算子的输入还是输出数据，字符串类型。<br>input：仅 dump 算子输入数据。<br>output：仅 dump 算子输出数据。<br>all（默认值）：同时 dump 算子输入和输出数据。 |
| dump_path | dump 数据的存放路径，字符串类型，默认值为当前执行路径。支持配置绝对路径或相对路径（相对执行命令行时的当前路径）。<br>绝对路径配置以"/"开头，例如：/home/HwHiAiUser/output。<br>相对路径配置直接以目录名开始，例如：output。 |
| quant_dumpable | 如果是量化后的网络，可通过此参数控制是否采集量化前的 dump 数据，bool 类型。<br>False（默认值）：不采集量化前的 dump 数据。因为图编译过程中可能优化量化前的输入/输出，此时无法获取量化前的 dump数据。<br>True：开启此配置后，可确保能够采集量化前的 dump 数据。 |
| dump_step | 指定采集哪些迭代的 dump 数据。字符串类型，默认值 None，表示所有迭代都会产生 dump 数据。<br>多个迭代用`\|`分割，例如：`0\|5\|10`；也可以用"-"指定迭代范围，例如：`0\|3-5\|10`。 |
| dump_layer | 指定需要 dump 的算子名，多个算子名之间使用空格分隔，形如"Add1_in_0 Add2 Mul2"。算子名获取方法参见 dump_layer 配置项说明。若指定的算子其输入涉及 data 算子，会同时将 data 算子信息 dump 出来。 |
| dump_data | 指定算子 dump 内容类型，字符串类型。<br>tensor（默认值）：dump 算子数据。<br>stats：dump 算子统计数据，保存结果为 csv 格式，文件中包含算子名称、输入/输出的数据类型、最大值、最小值等。<br>通常 dump 数据量太大并且耗时长，可以先 dump 算子统计数据，根据统计数据识别可能异常的算子，再 dump 算子数据。 |
| dump_config_path**（推荐）** | 指定 dump 配置文件（json 格式）路径，字符串类型，无默认值。支持绝对/相对路径（即相对执行命令时的当前路径）。上述 dump options（除了 enable_dump）均能通过 json 文件配置，**推荐 json 方式 dump，其余配置后续不再演进**。功能模式支持模型 Dump/单算子 Dump、溢出算子 Dump、算子 Dump Watch 模式等，具体使用方法和约束参见 dump_config_path 配置项说明。 |

#### 逐行解读

- **enable_dump**：唯一硬性必选开关；不打开即整个功能完全关闭；类型严格 `bool`，不接受字符串 `"True"` 之类。
- **dump_mode**：三值枚举字符串，默认 `all`——意味着初次打开调试时应直接拿到全量输入/输出张量对，是最"暴力"的精度比对源；如果只想对算子输出做校验（如检查激活分布），可选 `output` 把 I/O 减半。
- **dump_path**：与其他 dump 框架约定一致；以 `/` 开头为绝对，以目录名为相对（相对于执行 `python` 命令的 cwd）；默认值即"当前执行路径"，意味着不开 dump 时不会创建空目录。
- **quant_dumpable**：原文专门标注的"为何默认 False"——量化前 tensor 可能在图编译融合/常量折叠中被消除，无法稳定产出；只有 True 才能保证可比对的"原始量化前"输入/输出存在，**用于量化精度问题定位**的关键开关。
- **dump_step**：语法灵活——单点 `0|5|10` 与区间 `0|3-5|10` 同时支持；默认 `None`（注意是 Python `None` 而非字符串），会从 `data_index=0` 起每迭代都保存；典型用法：`dump_step="0"` 只保存第 0 步，避免大模型反复迭代的 IO 爆炸。
- **dump_layer**：空格分隔**精确匹配算子名**（来源是 `ge_proto*.txt` 中 `op.name`）；同名多算子机制隐含在"多个算子名"中，且会**级联 dump data 算子**（即网关/输入节点信息一并保留，方便回溯输入来源）。
- **dump_data**：默认 `tensor` 是性能/精度排查的源头，但 stats 才是大模型工程上的"探针"——先 `stats` 筛可疑算子、再 `tensor` 取证，文档把这一流程显式推荐。
- **dump_config_path（推荐）**：相当于"配置元配置"——把 dump_mode / dump_step / dump_layer 等统一为 JSON 一次声明；**唯一例外的选项是 `enable_dump` 仍只能通过 `dump_config` 中设**。文档点出**演进信号**——其它 options 后续不再演进，应迁移到此项。

### JSON 场景配置中的关键参数（解读；文档以多段 JSON 文本给出，非表格形式）

| 场景 | 关键 JSON 字段 | 取值/默认 | 作用 |
| --- | --- | --- | --- |
| 模型 Dump | `dump_list[].model_name`、`dump_list[].layer` | 必填 | 按子图/算子层名 dump |
| 单算子 Dump | `dump_op_switch` | `on`/`off`（on 时 `dump_list` 为空表示全网络） | 开关式简单 dump |
| 溢出算子 Dump | `dump_debug` | `on`（不配置或 `off` 即关闭） | 仅采集 AI Core 算子的溢出数据 |
| Watcher 模式 | `dump_list[].layer`、`dump_list[].watcher_nodes`、`dump_scene` | `watcher` | 输出与潜在踩踏算子配对 dump |

> 注：原文为 JSON 文本而非 markdown 表格，此处为辅助理解的归纳表格；JSON 原文逐字保留见【使用方法】节。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **互补关系：[图结构 dump 功能](../basic/graph_dump.md)**——文档首段 NOTE 明确指出"本功能与图结构 dump 功能是不同的功能，二者可以单独使用，也可共同用于用户定位精度问题"。前者关注**算子输入/输出数据**（值层面），后者关注**图拓扑结构**（结构层面），二者组合才能完成"图对了 + 值对不对"的双轴精度定位。
- **上游 API：[torchair.get_npu_backend](../../api/torchair/get_npu_backend.md)**——所有 dump 配置需要塞入 `CompilerConfig.dump_config.*`，并通过 `torchair.get_npu_backend(compiler_config=config)` 注入 `torch.compile`；文档给出的 Python 示例以这一链路作为唯一启动入口。
- **平级扩展接口：[data_dump](../../api/scope/data_dump.md)**——属于 `torchair.scope` 模块的上下文管理器接口，提供**基于 Python 代码区段**的算子 dump 范围控制；与 `dump_layer` 取并集，可与表中所有 dump options 配套使用，文档用一段完整 `Network(nn.Module)` 代码示例展示其 `with` 语句块用法。
- **下游工具链**：文档最后一段提及"解析 dump 数据文件"——需先将 dump 文件转换为 numpy 格式再查看（**原文该段在"详细操作指导请参"处截断**，未完成完整指引，但已点出 *numpy → txt* 的解析路径依赖 `numpy` 官方能力）。
- **环境变量依赖**：`dump_layer` 的算子名获取依赖 `DUMP_GE_GRAPH=3`（精简版 dump，仅打印节点关系），文档建议参见《CANN 环境变量参考》"DUMP_GE_GRAPH"章节；JSON 中 watcher 模式对**集合通信类算子（HcomAllReduce 等）**有特殊行为约束（仅导出 watcher_nodes 的 dump 文件）。
- **与 TorchNPU 默认行为的冲突**：TorchNPU 已默认开启 `exception` 信息 dump（即 `dump_scene` 异常算子 Dump 配置）——**通过 `dump_config_path` 配置的 exception dump 不会生效**，意味着使用 JSON 配置时不能依赖"覆盖默认 exception dump"的能力。

---

## 【使用方法】

### 方式一：通过 `CompilerConfig.dump_config` 选项式配置（Python）

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# data dump 开关：[必选]
config.dump_config.enable_dump = True
# dump 类型：[可选]，all 代表 dump 所有数据
config.dump_config.dump_mode = "all"
# dump 路径：[可选]，默认为当前执行目录
config.dump_config.dump_path = '/home/dump'
# 量化 data dump 开关：[可选]，是否采集量化前的 dump 数据
config.dump_config.quant_dumpable = True
# 保存 dump 的步数，否则每一步都会保存：[可选]
config.dump_config.dump_step = "0|1"
# 指定需要 dump 的算子：[可选]
config.dump_config.dump_layer = "Add_1Mul_1 Add2"
# 指定算子 dump 类型：[可选]，stats 表示 dump 输出 csv 文件
config.dump_config.dump_data = "stats"
# dump 配置文件的路径：[可选]，通过配置文件启用 data dump。不建议与其他 options 一起使用，否则此配置将失效。
config.dump_config.dump_config_path = "/home/dump_config.json"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

> 原文明确标注：**"示例仅供参考，不支持直接拷贝运行"**。

### 方式二：通过 `torchair.scope.data_dump()` 上下文管理器（Python，补充 dump 算子范围）

```python
import torch
import torchair
import logging
from torchair import logger
logger.setLevel(logging.DEBUG)

class Network(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, data0, data1):
        add_01 = torch.add(data0, data1)
        with torchair.scope.data_dump():
            sub_01 = torch.sub(data0, data1)
        return add_01, sub_01

input0 = torch.randn(2, 2, dtype=torch.float16).npu()
input1 = torch.randn(2, 2, dtype=torch.float16).npu()
config = torchair.CompilerConfig()
config.dump_config.enable_dump = True
config.dump_config.dump_layer = "Add"
npu_backend = torchair.get_npu_backend(compiler_config=config)
npu_mode = Network().npu()
npu_mode = torch.compile(npu_mode, fullgraph=True, backend=npu_backend, dynamic=False)
npu_out = npu_mode(input0, input1)
```

要点：`with torchair.scope.data_dump():` 必须以**语句块形式**调用；块内算子（如示例中 `torch.sub`）与 `dump_layer` 列表取**并集**；产物目录与 `dump_layer` 一致。

### 方式三：JSON 配置（推荐路径，`dump_config_path`）

文档给出三套**互斥**的 JSON 模板，原文逐字保留如下：

**(1) 模型 Dump 配置示例：**

```json
{
 "dump":{
  "dump_list":[
   { "model_name":"ResNet-101"
   },
   {
    "model_name":"ResNet-50",
    "layer":[
          "conv1conv1_relu",
          "res2a_branch2ares2a_branch2a_relu",
          "res2a_branch1",
          "pool1"
    ]
   }
  ],
  "dump_path":"/home/output",
                "dump_mode":"output",
  "dump_op_switch":"off",
                "dump_data":"tensor"
 }
}
```

**(2) 单算子 Dump 配置示例：**

```json
{
    "dump":{
        "dump_path":"/home/output",
        "dump_list":[],
 "dump_op_switch":"on",
        "dump_data":"tensor"
    }
}
```

**(3) 溢出算子 Dump 配置示例（`dump_debug="on"`）：**

```json
{
    "dump":{
        "dump_path":"output",
        "dump_debug":"on"
    }
}
```

约束：仅支持采集 AI Core 算子的溢出数据；**与模型 Dump / 单算子 Dump 互斥**（同时开启会报错）；解析依赖《CANN 精度调试工具》的"溢出算子数据采集与解析"章节。

**(4) 算子 Dump Watch 模式配置示例（`dump_scene="watcher"`）：**

```json
{
    "dump":{
        "dump_list":[
            {
                "layer":["A", "B"],
                "watcher_nodes":["C", "D"]
            }
        ],
        "dump_path":"/home/",
        "dump_mode":"output",
        "dump_scene":"watcher"
    }
}
```

语义：执行完 A、B 算子时，把 C、D 的输出 Dump；执行完 C、D 时也 dump 它们自身——比较两份 C、D 的 dump 产物，排查 A、B 是否踩踏 C、D 的输出内存。约束：与 `dump_debug`、`dump_op_switch` 互斥报错；`watcher_nodes` 若是融合算子必须用融合后算子名；`dump_mode` 当前仅支持 `output`；`dump_list` 内暂不支持 `model_name`。

### 环境变量：获取算子名（`dump_layer` 配套）

```bash
export DUMP_GE_GRAPH=3
```

执行后生成 `ge_proto*.txt`，`op.name` 字段为算子名，例如原文示例：

```text
graph {
  name: "online_0"
  input: "Add1_in_0:0"
  input: "Add1_in_1:0"
  op {
    name: "Add1_in_0"
    type: "Data"
    ...
  }
  op{
    name: "Add2"
    type: "Data"
    ...
  }
}
```

### 使用约束（原文）

- 本功能**仅适用于 GE 图模式场景**。
- 参数涉及文件路径时，请确保路径真实存在且具有**读取和写入权限**。
- `dump_config_path` 与表中其他 dump options **不建议同时使用**；同时配置时 `dump options` 优先级更高。
- 大模型场景推荐 `dump_data="stats"` 先筛选可疑算子。

## 图文联合解读

- `data_dump.png`: # 图文联合解读

**图示内容**：纵列展示torch.compile的6阶段流水线（Dynamo trace→Aten转Ascend IR→TorchAir优化→protobuf传GE→GE编译→GE执行），其中第6阶段"GE图执行"通过虚线箭头引出右侧说明框，指出该步通过`config.dump_config.enable_dump=True`获取运行后的dump数据。

**技术结论**：dump功能作用于**GE图执行阶段**，即在Ascend IR图真实运行后捕获算子输入/输出，而非在编译阶段静态获取。

**与文档论点关系**：印证文档"功能用于Dump Ascend IR图执行时的算子输入、输出数据"的定位——强调dump发生在运行时，与图结构dump（编译产物）形成功能区分，呼应开篇"二者是不同的功能"的说明。
