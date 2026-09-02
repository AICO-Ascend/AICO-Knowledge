# Dynamo导图功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/dynamo_export.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/dynamo_export.md

# Dynamo导图功能 — 一体化深度解读

## 【定位】

本篇文档描述 TorchAir 的 `torchair.dynamo_export` 离线导图能力——将 TorchAir 在昇腾 NPU 上生成的计算图以 GE 图模式导出为 `.air` 文件，使推理模型脱离 PyTorch 框架，由 CANN 软件栈直接加载执行，从而降低框架调度开销并便于跨环境部署。

---

## 【技术要点】

1. **导出接口与产物形态**：通过 `torchair.dynamo_export(*args, model, export_path="export_file", export_name="export", dynamic=False, config=CompilerConfig(), **kwargs)` 调用；产出根目录 `export_file/` 内含 `dynamo.pbtxt`（可读）、`export.air`（不可读，部分场景含权重）、`weight_xx`、`options.json`，并在开启 `auto_atc_config_generated` 时额外生成 `model_relation_config.json` 与 `numa_config.json`。
2. **模式与互斥约束**：本功能仅适用于 **GE 图模式** 场景；且 **不允许同时配置** `frozen_parameter`（固定权重类输入地址功能）；Dynamo 自身约束——**不支持动态控制流 if/else**，且要求被导出部分能构成 **一张完整的图**。
3. **权重外置阈值（2G − 200MB）**：受第三方库 Protobuf 限制，`.air` 文件不得超过 **2G**；当模型权重参数量 **≤（2G − 200MB）** 时直接写入 `export.air`（在 `dynamo.pbtxt` 中以 **Const** 节点记录路径/dtype）；**>（2G − 200MB）** 时不再写入 `.air`，而是自动生成 `weight_xx` 文件，并在 `dynamo.pbtxt` 中以 **FileConstant** 节点记录路径/dtype（文件个数取决于网络中权重的定义）。
4. **两类 export 配置（experimental）**：
   - `config.export.experimental.auto_atc_config_generated`（默认 `False`）：前端切分场景下，是否自动生成 ATC 的 json 配置模板（含 `model_relation_config.json`/`numa_config.json`）。
   - `config.export.experimental.enable_record_nn_module_stack`（默认 `False`）：是否在导出图中携带 `nn_module_stack` 信息供后端切分模板用；要求 layer 以 **数组形式** 命名（`layer[0]=xxx, layer[1]=xxx`），且 `record_nn_module_stack` 只有在 **model 结构深度两层及以上** 才能获取到。
5. **多卡与通信算子**：支持单卡与多卡导图，**支持导出后图中携带 AllReduce 等通信类算子**；多卡示例使用 `torch.multiprocessing.spawn` 启动 `world_size=2`，最终产出按 `export_name + rank id` 拼接的子目录（如 `mp_rank0.air`/`mp_rank1.air`）与子目录 `rank_0`/`rank_1`。
6. **air → om 转换**：导出后由 ATC 工具将 `.air` 转为可执行 `.om`，命令关键参数为 `--model=*.air`、`--framework=1`（仅能取 1，代表来源即本功能导出的 `.air`）、`--output=`、`--soc_version=Ascend_xxxyy_`。
7. **路径敏感性**：相对路径要求在 ATC 编译/执行时处于相对路径的 **父路径** 中执行；绝对路径在拷贝到其他服务器时需保证路径一致，否则无法定位权重文件。

---

## 【关键机制与数据】

- **导出数据流**：PyTorch 模型 → `torchair.dynamo_export` 调用（按 GE 图模式编译）→ 生成 `dynamo.pbtxt`（图结构可读视图）+ `export.air`（不可读图/权重二进制）+ 附属 JSON 配置 → ATC（`--framework=1`）→ `.om` → CANN 加载运行。原文强调"导出的推理模型不再依赖 PyTorch 框架，可直接由 CANN 软件栈加载执行"。
- **权重存放二态决策（原文给出确切阈值）**：≤（2G − 200MB） → 嵌入 `.air`，`Const` 节点；>（2G − 200MB）→ 外置为 `weight_xx` 文件，`FileConstant` 节点。原文："导出的 air 文件大小不允许超过 2G（依赖的第三方库 Protobuf 存在限制导致）"。
- **通信算子保留**：原文："支持导出后带 AllReduce 等通信类算子"，由多卡示例中 `torch.distributed.all_reduce(x)` 落到 `mp_rank*.air` 中体现。
- **控制流约束**：原文："受 Dynamo 功能约束，不支持动态控制流 if/else"。
- **栈信息命名约束（原文）**："前端脚本定义 layer 时，需要以数组的形式，即类似 layer[0] = xxx，layer[1] = xxx。若不以数组形式表示变量名，相同模型结构被重复执行，从栈信息中将无法看出模型的 layer 结构，后端也无法切分。record_nn_module_stack 只有在 model 结构深度两层及以上才能获取到。"

---

## 【表格解读】

原文表 1：**导图功能配置说明**

| 支持的功能 | 功能说明 | 配置说明 |
|---|---|---|
| `auto_atc_config_generated` | 前端切分场景下（PyTorch 模型导出时包含集合通信逻辑），是否开启自动生成 ATC 的 json 配置文件样例模板。 | `False`（默认值）：不开启自动生成 json 模板，用户自行手动配置通信域信息。<br>`True`：开启自动生成 json 模板。 |
| `enable_record_nn_module_stack` | 导出的图是否携带 `nn_module_stack` 信息，方便后端切分（PyTorch 模型导出时不含集合通信逻辑，而由 GE 添加集合通信逻辑）运用模板。前端脚本定义 layer 时，需要以数组的形式，即类似 `layer[0] = xxx`，`layer[1] = xxx`。若不以数组形式表示变量名，相同模型结构被重复执行，从栈信息中将无法看出模型的 layer 结构，后端也无法切分。`record_nn_module_stack` 只有在 model 结构深度两层及以上才能获取到。 | `False`（默认值）：导出图不带 `nn_module_stack` 信息。<br>`True`：导出图带 `nn_module_stack` 信息。 |

**逐行解读：**

- **第一行（`auto_atc_config_generated`）**：定位在"前端切分（含集合通信）"场景。默认关闭，需用户手工配置通信域；开启后由工具自动产出 `model_relation_config.json`（多切片模型数据关联与分布式通信组关系）与 `numa_config.json`（目标部署环境逻辑拓扑）两个模板，但仍需用户按实际修改字段（原文："json 中相关字段用户需根据实际情况修改……针对多卡场景，item 节点被生成在 node_id 为 0 的表中，需要用户根据自己的需求手动划分至不同的 node 下"）。
- **第二行（`enable_record_nn_module_stack`）**：定位在"后端切分（GE 注入集合通信）"场景。开启后导出图携带 `nn_module_stack` 供后端模板切分；但需满足 **两个前置条件**——(1) layer 变量名以数组形式声明，否则重复执行相同结构时栈信息无法区分 layer；(2) model 结构深度 ≥ 2，否则信息获取不到。默认关闭。

配置示例（原文）：

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 开启自动生成ATC的json配置文件模板
config.export.experimental.auto_atc_config_generated = True
# 携带nn_module_stack信息
config.export.experimental.enable_record_nn_module_stack = True
```

产物结构目录树（原文逐字还原）：

```
└── export_file                         // 导出的文件夹，可自定义
    ├── dynamo.pbtxt                    // 导出的模型信息（可读格式）
    ├── export.air                      // 导出的模型文件（不可读），文件名默认值为"export"
    ├── weight_xx                       // 导出的权重文件
    ├── ......
    ├── options.json                    // 导出的GE options配置文件
    ├── model_relation_config.json      // 启用auto_atc_config_generated生成的文件
    └── numa_config.json                // 启用auto_atc_config_generated生成的文件
```

单卡导出实际目录树（原文）：

```
├── example1.py
└── export_file             // 指定导出的文件夹，当文件夹不存在时会自动创建
    ├── dynamo.pbtxt       // 导出可读的图信息，用于debug
    ├── export.air        // 导出的模型文件，ATC编译时的输入。其中通过fileconst节点记录了权重所在的路径与文件名
```

多卡导出实际目录树（原文）：

```
├── example1.py
├── example2.py
└── mp
    ├── model_relation_config.json
    ├── mp_rank0.air                  // 第一张卡导出的模型文件
    ├── mp_rank1.air                  // 第二张卡导出的模型文件
    ├── numa_config.json
    ├── rank_0                    // 第一张卡子目录
    │   ├── dynamo.pbtxt        // 导出可读的图信息，用于debug
    │   ├── options.json        // 导出的GE options配置文件
    │   ├── p1                 // 导出的权重文件
    │   └── p2                 // 导出的权重文件
    └── rank_1
        ├── dynamo.pbtxt
        ├── options.json
        ├── p1
        └── p2
```

---

## 【公式解读】

原文无公式。

（仅含命令形式的伪代码：ATC 调用——`atc --model=./export_file/export.air --framework=1 --output=./export_file/offline_module --soc_version=<soc_version>`，各参数含义见上文【技术要点】第 6 条。）

---

## 【关联】

- **frozen_parameter.md（固定权重类输入地址功能）**：互斥关系。原文："本功能仅适用于 GE 图模式场景，**暂不支持同时配置** [固定权重类输入地址功能](frozen_parameter.md)"——两者共享 GE 图模式但导出策略冲突，不能同开。
- **../../api/torchair/dynamo_export.md（API 参考）**：原文指向此链接获取 `dynamo_export` 详细参数说明；本文档的"关键参数说明"部分对该 API 原型做了简介（`export_path`、`export_name`、`dynamic`、`config` 等），完整定义需要跳转该 API 文档。
- **ATC 离线模型编译工具**：导出链路的下游消费方。原文将 `.air → .om` 转换、对 `model_relation_config.json`/`numa_config.json` 中字段含义的解读，均指向《CANN ATC 离线模型编译工具》（特别是 `--model_relation_config`、`--cluster_config` 章节）。
- **GE 图模式 / Dynamo / CANN 软件栈**：上游编译由 TorchAir + torch_npu 完成，导出后即脱离 PyTorch 框架，交由 CANN 直接加载；其中 `options.json` 是导出的 GE options 配置，按 `compile options` 与 `execute options` 两大类、各含 `global/session/graph` 三个作用域组织（global/session 来自全局初始化，graph 来自单图编译配置）。

---

## 【使用方法】

**接口调用（原文 Python 示例）**：

- **单卡场景**：
```python
import torch, torch_npu, torchair
class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.linear1 = torch.nn.Linear(2, 2)
        self.linear2 = torch.nn.Linear(2, 2)
        for param in self.parameters():
            torch.nn.init.ones_(param)
    def forward(self, x, y):
        return self.linear1(x) + self.linear2(y)
model = Model()
x = torch.randn(2, 2)
y = torch.randn(2, 2)
torchair.dynamo_export(x, y, model=model, dynamic=False)
```

- **多卡场景（含 AllReduce，启用两个 experimental 配置）**：
```python
import torch, os, torch_npu, torchair
from torchair import CompilerConfig

class AllReduceSingleGroup(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.p1 = torch.nn.Parameter(torch.tensor([[1.1, 1.1], [1.1, 1.1]]))
        self.p2 = torch.nn.Parameter(torch.tensor([[2.2, 2.2], [3.3, 3.3]]))
    def forward(self, x, y):
        x = x + y + self.p1 + self.p2
        torch.distributed.all_reduce(x)
        return x

def example(rank, world_size):
    torch.distributed.init_process_group("gloo", rank=rank, world_size=world_size)
    x = torch.ones([2, 2], dtype=torch.int32)
    y = torch.ones([2, 2], dtype=torch.int32)
    mod = AllReduceSingleGroup()
    config = CompilerConfig()
    config.export.experimental.auto_atc_config_generated = True
    config.export.experimental.enable_record_nn_module_stack = True
    torchair.dynamo_export(x, y, model=mod, dynamic=True,
                           export_path="./mp", export_name="mp_rank", config=config)

def mp():
    world_size = 2
    torch.multiprocessing.spawn(example, args=(world_size,), nprocs=world_size, join=True)

if __name__ == '__main__':
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29505"
    mp()
```

**air → om 转换命令（原文）**：
```bash
atc --model=./export_file/export.air --framework=1 --output=./export_file/offline_module --soc_version=<soc_version>
```

**关键配置项与默认值汇总**（综合自原文"表 1"）：
- `export_path`：相对路径（执行时需处于其父路径）或绝对路径（拷贝需保留原绝对路径）。
- `export_name`：默认 `"export"`；多卡场景按 `export_name + rank id` 拼接。
- `dynamic`：默认 `False`。
- `config.export.experimental.auto_atc_config_generated`：默认 `False`。
- `config.export.experimental.enable_record_nn_module_stack`：默认 `False`，且生效需 layer 数组命名 + model 深度 ≥ 2。
