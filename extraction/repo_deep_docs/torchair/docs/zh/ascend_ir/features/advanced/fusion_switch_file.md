# 算子融合规则配置功能（fusion\_switch\_file）

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/fusion_switch_file.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/fusion_switch_file.md

# 「fusion_switch_file 算子融合规则配置功能」深度解读

## 【定位】

这篇文档解决的是 TorchAir 在 GE 图模式下"算子融合规则如何被用户自定义控制"的问题——通过提供一个 `.cfg` 配置文件，使用户能够按 pass 粒度启用/关闭图融合（GraphFusion）与 UB 融合（UBFusion）规则，并配合产物 `fusion_result.json` 进行融合命中与生效统计。

---

## 【技术要点】

1. **两种融合类型**：文档区分**图融合（Graph Fusion）** 与 **UB 融合（Unified Buffer Fusion）**。前者由融合引擎按融合规则改图（拆分/合并算子），与硬件无关；后者针对 UB 算子进行融合，以节省 DDR 搬移开销。

2. **使用范围限定**：功能**仅适用于 GE 图模式场景**；配置文件路径必须真实存在且具备**读、写权限**。

3. **配置结构**：配置文件顶层为 `Switch`，下分 `GraphFusion` 与 `UBFusion` 两个子项；每条 pass 取值为 `"on"`（开启）或 `"off"`（关闭）。示例内置 pass 共 8 个 GraphFusion 项（`ConvToFullyConnectionFusionPass`/`SoftmaxFusionPass`/`ConvConcatFusionPass`/`MatMulBiasAddFusionPass`/`PoolingFusionPass`/`ZConcatv2dFusionPass`/`ZConcatExt2FusionPass`/`TfMergeSubFusionPass`）和 1 个 UBFusion 项（`FusionVirtualOpSetSwitch`）。

4. **一键关闭/开启与优先级**：支持 `"ALL":"off"` 一键关闭；**单条 pass 配置优先级高于 "ALL"**，可实现"全局关 + 单开"组合。但**"ALL":"off" 并不能关闭所有融合规则**——文档明确指出"配置 ALL:off 后，部分融合算子仍旧会生效，因为关闭部分融合规则会导致功能问题"。

5. **生效入口**：通过 `torchair.CompilerConfig().fusion_config.fusion_switch_file = "<path>"` 设置路径，再经 `torchair.get_npu_backend(compiler_config=config)` 拿到 backend，最后 `torch.compile(model, backend=npu_backend)`。

6. **生效验证方式**：需设置 `export TNG_LOG_LEVEL=0`，在日志中搜索关键字 `ge.fusionSwitchFile:`，若打印出所配路径即代表配置被加载（如 `concrete_graph/session.cpp:28   ge.fusionSwitchFile: /home/test/fusion_switch.cfg`）。

7. **产物统计**：图编译完成后默认在当前执行路径生成 `fusion_result.json`，记录**实际生效**的融合规则（已扣除用户在 `fusion_switch.cfg` 中关闭的 pass）。字段含义：`match_times`（匹配次数）、`effect_times`（生效次数）、`repository_hit_times`（UB 融合知识库命中次数）。

---

## 【关键机制与数据】

### 工作原理（UB 融合核心机制）

原文对 UB 融合的描述（原文）：
> "两个算子单独运行时，算子1的计算结果存储在UB上，需搬移到DDR……算子2执行时，需要将算子1的输出从DDR搬移到UB……完成后再从UB搬移回DDR。"
>
> "算子1的结果经历了从 **UB→DDR→UB→DDR**，过程中的DDR数据搬移是不必要的。可以将算子1和算子2合并成一个算子，融合后算子1的数据**直接保留在UB中**，算子2直接从UB获取数据进行算子2的计算，这样就**节省了一次输出DDR和一次输入DDR**，减少了数据搬移时间，提高运算效率，有效降低了带宽。"

即数据流路径：未融合为 `UB → DDR → UB → DDR`（2 次 DDR 搬移），融合后压缩为 `UB → UB`（0 次 DDR 搬移）。

### 数据流（配置生效链路）

```
用户 .cfg 文件
   ↓ fusion_config.fusion_switch_file 赋值
torchair.CompilerConfig
   ↓ 作为 compiler_config 参数传入
torchair.get_npu_backend
   ↓ 返回 npu_backend
torch.compile(model, backend=npu_backend)
   ↓ 图编译初始化阶段
日志打印 "ge.fusionSwitchFile: <path>"  (TNG_LOG_LEVEL=0)
   ↓ 图编译完成
当前路径生成 fusion_result.json
```

### 性能数据

原文未提供具体性能数字（如加速比、带宽节省比例），仅有定性描述"降低网络推理时间"、"提高整网性能"、"有效降低了带宽"。**

---

## 【表格解读】

### 原文表格：表 1 参数说明

|参数名|说明|
|--|--|
|fusion_switch_file|指定算子融合规则文件。|

逐行解读：

- **`fusion_switch_file`**：这是 `CompilerConfig.fusion_config` 子对象下的属性，类型为字符串路径。其唯一作用是把外部 `.cfg` 配置文件路径注入到 GE 图编译器，使编译器在图初始化阶段读取其中的 `Switch.GraphFusion` / `Switch.UBFusion` 项作为开关表。文档示例路径为 `/home/test/fusion_switch.cfg`，文件名由用户自定义（后缀需为 `.cfg`）。

> 原文无其他表格。文档中出现的其他表格化内容（`fusion_switch.cfg` 示例、`fusion_result.json` 示例）均为配置/产物样例而非参数说明表，故不在此处还原为表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

1. **上游/调用入口关联**：[`../../api/torchair/get_npu_backend.md`](../../api/torchair/get_npu_backend.md) —— 本文档的核心配置生效链路 `torchair.get_npu_backend(compiler_config=config)` 由此 API 文档定义；`compiler_config` 参数接收 `CompilerConfig` 对象，从而承载 `fusion_switch_file`。

2. **日志/可观测性关联**：[`../basic/cplus_log_print.md`](../basic/cplus_log_print.md) —— 文档明确指出"在运行前需提前设置日志环境变量（参见 TorchAir C++ 层日志打印）"，并通过 `TNG_LOG_LEVEL=0` 与关键字 `ge.fusionSwitchFile:` 来**验证配置是否被框架正确读取**。换言之，没有正确开启 C++ 日志，就无法确认 fusion_switch_file 是否真的生效。

3. **底层规则关联**：文档引用《CANN 图融合和 UB 融合规则参考》—— 所有在 `.cfg` 中出现的 pass 名（如 `SoftmaxFusionPass`、`PoolingFusionPass`、`FusionVirtualOpSetSwitch` 等）均来源于 CANN 融合引擎内置规则集；TorchAir 仅通过 `fusion_switch_file` 提供"按名开/关"的透传能力。

4. **产物关联**：`fusion_result.json` 与 `fusion_switch.cfg` 是**互补关系**——前者记录"配置关闭后剩余仍生效"的规则与命中情况，用于辅助用户调优配置。

---

## 【使用方法】

### 步骤 1：创建 `*.cfg` 配置文件

文件名自定义（如 `fusion_switch.cfg`），标准示例：

```txt
{
    "Switch":{
        "GraphFusion":{
            "ConvToFullyConnectionFusionPass":"on",
            "SoftmaxFusionPass":"on",
            "ConvConcatFusionPass":"on",
            "MatMulBiasAddFusionPass":"on",
            "PoolingFusionPass":"on",
            "ZConcatv2dFusionPass":"on",
            "ZConcatExt2FusionPass":"on",
            "TfMergeSubFusionPass":"on"
        },
        "UBFusion":{
            "FusionVirtualOpSetSwitch":"on"
        }
    }
}
```

一键关闭 + 单开示例：

```txt
{
    "Switch":{
        "GraphFusion":{
            "ALL":"off",
            "SoftmaxFusionPass":"on"
        },
        "UBFusion":{
            "ALL":"off",
            "TbePool2dQuantFusionPass":"on"
        }
    }
}
```

### 步骤 2：Python 代码启用

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 指定融合配置文件的路径
config.fusion_config.fusion_switch_file = "/home/test/fusion_switch.cfg"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

### 步骤 3：验证配置生效

```bash
export TNG_LOG_LEVEL=0
```

在日志中搜索 `ge.fusionSwitchFile:`，应见类似：
```txt
concrete_graph/session.cpp:28   ge.fusionSwitchFile: /home/test/fusion_switch.cfg
```

### 步骤 4：查看融合产物

图编译完成后，在当前执行目录下读取 `fusion_result.json`，其中：
- `graph_fusion` / `ub_fusion` 分别对应两种融合类型；
- `match_times` = 匹配到的融合规则次数；
- `effect_times` = 实际生效次数；
- `repository_hit_times` = UB 融合知识库命中次数；
- 顶层 key `session_and_graph_id_<thread>_<graph>` 标识融合结果所属线程与图编号。

> 注意事项：原文标注 `"ALL":"off"` **并非关闭所有融合规则**；单条 pass 配置优先级高于 `ALL`；配置文件路径必须真实存在并具备读/写权限；本功能**仅适用于 GE 图模式**。
