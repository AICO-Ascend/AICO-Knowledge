# parallel_schedule

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/graph_optimization/parallel_schedule.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/graph_optimization/parallel_schedule.md

# parallel_schedule 深度解读

## 【定位】
本文档描述 TorchNPU 在 Inductor 编译流程中引入的**计算图多流并行调度**能力：针对原生 Inductor 将所有 kernel 强制串行下发到默认 stream、无法利用昇腾设备多计算单元并发的问题，在图下沉开启且 Kernel Fusion 完成之后，将无数据依赖的子图拆分到不同 stream 上并行执行，以提升推理性能。

## 【技术要点】

1. **问题背景与目标**：原生 torch Inductor compile 流程中，计算图执行被串行化到默认 stream，两个无依赖 kernel 也被强制串行，限制了设备多计算单元与异步引擎的并发能力，无法实现计算重叠，成为性能瓶颈。
2. **适用版本与平台**：面向 **A5（Atlas A5 系列产品） + Pytorch-v2.9.0**，仅适用于**模型推理过程**。
3. **总体流程**：在图下沉（graph sinking）开启、Kernel Fusion 完成之后，引入"对计算图并行能力的计算"，再下发算子。
4. **核心并行策略**：利用**收敛算法 + CV 分离并行策略**，将"组间计算单元不同、组内计算单元相同"的子图分流到不同 stream 上并行执行，最大化利用昇腾设备架构的 **CUBE / VECTOR** 并行计算能力。
5. **可扩展性**：支持用户基于并行策略基类 `ParallelStrategyBase` 编写自定义 `assign_parallel_groups` 函数，并通过 `register_custom_parallel_strategy` 注册，无需修改底层执行逻辑。
6. **运行时构造**：开启后，inductor 编译产物 `output_code.py` 中会自动生成 `main_stream`/`main_event` 以及 `stream_group_cube`/`event_group_cube`、`stream_group_vector`/`event_group_vector` 等 stream/event 定义及 `stream.wait_event` 同步原语。

## 【关键机制与数据】

**工作原理（原文梳理）：**
- 默认关闭；开启后，`parallel_scheduler` 会在 Inductor 调度体系内、Kernel Fusion 之后介入。
- 通过收敛算法 + CV 分离策略，把计算图节点分成若干"并行组"：**CUBE 组**、**VECTOR 组**、**MAIN 组**，每组绑定到各自的 stream。
- `main_event.record(main_stream)` 作为入口同步锚点，子 stream 通过 `wait_event(main_event)` 与主 stream 形成 producer–consumer 同步；kernel 调用末尾通过 `npu_stream` 参数（而非全局 stream）下发到对应 stream。

**原文日志数据（验证 1 的真实输出）：**
- `INFO - cv parallel group len: 3` —— 共划分出 3 个并行分组。
- `INFO - Group CUBE (11 nodes): ['op2', 'op3', 'op4', 'op5', 'op6', 'op7', 'op8', 'op9', 'op10', 'op11', 'op12']` —— CUBE 组含 11 个节点。
- `INFO - Group VECTOR (3 nodes): ['op25_op26_op27_op28_op29_op30_op31_op32_op33_op34_op35_op36_op37_op38_op39_op40_op41_op42_op43_op44_op45', 'op46_op47_op48_op49_op50_op51_op52_op53_op54_op55_op56_op57_op58_op59_op60_op61_op62_op63_op64_op65_op66', 'op67_op68_op69_op70_op71_op72_op73_op74']` —— VECTOR 组含 3 个融合节点（每个由多个原始 op 融合而成）。
- `INFO - Group MAIN (14 nodes): ['op0_op1', 'op13', 'op14_op15', 'op16_op17', 'op18_op19', 'op20_op21', 'op22_op23', 'op24', 'op75', 'op76', 'op77', 'op78', 'op79', 'op80']` —— MAIN 组含 14 个节点。

**原文编译产物片段数据：**
- buffer 形状示例：`(128, 6144)`、`(128, 3072)`、`(128, 1536)`，dtype 均为 `torch.float32`；device 为 `npu`。
- workspace 形状：`workspace_0 = empty_strided((14680064, ), (1, ), device='npu', dtype=torch.uint8)`。
- CUBE 组 kernel 的 stream 参数为 `c_void_p(stream_group_cube.npu_stream)`，MAIN 组 kernel 的 stream 参数为 `c_void_p(main_stream.npu_stream)`，与分组语义一致。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

文档**未提供文末内部链接**，但根据正文描述可梳理出与以下特性/模块的上下游关系：

- **图下沉（graph sinking）**：使用约束中明确指出"需要在图下沉开启时使用计算图多流调度能力"，并行调度是在图下沉流程之后介入的。
- **Kernel Fusion**：并行调度在 "完成 Kernel Fusion 后" 才引入，是 Fusion 的下游环节；同时，VECTOR 组的节点命名（如 `op25_op26_op27_…`）也说明 Fusion 是并行分组的前置步骤。
- **Inductor 调度体系**：自定义策略实现依赖 `torch._inductor.scheduler.BaseSchedulerNode` 作为输入类型，说明本特性深度耦合于 Inductor 的 scheduler 抽象。
- **torch_npu runtime**：`torch_npu.npu.Stream`、`torch_npu.npu.Event`、`torch_npu.npu.current_stream()` 是多流并行的运行时承载；同步原语 `stream.wait_event(event)` 由 `torch_npu` 提供。
- **`output_code.py` 编译产物**：通过观察该文件是否出现 stream/event 定义，是验证特性是否生效的两条手段之一（与日志并行打印并列）。
- **注册入口**：自定义策略在 `torch_npu\_inductor\__init__.py` 的"计算图多流并行调度入口处"注册，并调用 `parallel_scheduler()`，表明 `fx_passes.parallel_scheduler_pass` 与 `fx_passes.parallelism_strategy_framework` 是其内部支撑模块。

## 【使用方法】

**1. 开启 / 关闭特性（环境变量）：**

```shell
# 开启
export ENABLE_PARALLEL_SCHEDULER=True

# 关闭（默认）
export ENABLE_PARALLEL_SCHEDULER=False
```

**2. 验证手段：**
- **验证 1（日志）**：开启后日志出现 `cv parallel group len`、`Group CUBE`、`Group VECTOR`、`Group MAIN` 等并行分组打印；关闭后不再出现。
- **验证 2（编译产物）**：开启后 `XXX/model__1_inference_3.0/output_code.py` 中出现 `torch_npu.npu.Stream()`、`torch_npu.npu.Event()`、`main_stream`、`stream_group_cube`、`stream_group_vector` 等定义及 `stream.wait_event(event)` 等同步代码；关闭后不存在。

**3. 接入自定义并行调度策略：**

```python
# Step 1. 编写自定义策略：继承 ParallelStrategyBase 并实现 assign_parallel_groups
from typing import List, Dict
import torch
from torch._inductor.scheduler import BaseSchedulerNode
from .parallelism_strategy_base import ParallelStrategyBase

class CustomParallelStrategy(ParallelStrategyBase):
    def assign_parallel_groups(self, nodes: List[BaseSchedulerNode]) -> Dict[str, List[BaseSchedulerNode]]:
        final_groups = dict()
        # 编写自定义的并行分组调度策略代码
        return final_groups
```

```python
# Step 2. 在 torch_npu\_inductor\__init__.py 计算图多流并行调度入口处注册
    if os.environ.get("ENABLE_PARALLEL_SCHEDULER", "false").lower() == "true":
        from .fx_passes.parallel_scheduler_pass import parallel_scheduler

        # 添加自定义调度策略注册代码 begin
        from .fx_passes.parallelism_strategy_custom import CustomParallelStrategy
        from .fx_passes.parallelism_strategy_framework import register_custom_parallel_strategy
        register_custom_parallel_strategy("custom", CustomParallelStrategy)
        # 添加自定义调度策略注册代码 end

        parallel_scheduler()
```

**4. 使用约束：**
- 默认关闭；需在**图下沉开启**时使用；当前仅适用于**模型推理过程**。

**5. 支持的型号：**
- Atlas A5 系列产品。

## 图文联合解读

- `parallel_schedule.png`: **图文联合解读：**

1) 图展示了Inductor编译流水线的并行调度流程：XXX Model→Dynamo→pre_grad/joint/post_grad pass→kernel fusion→scheduler融合→**compute unit分类**(Cube/Vector/Scalar)→**Parallelism Strategy**(默认CVParallelStrategy/CommonParallelStrategy/用户自定义)→ParallelismCodegen→Triton编译器，并通过橙色注释标注各阶段功能。

2) 论证了并行调度需在**kernel fusion之后**插入，先为每个op标注计算单元类型，再按"组间单元不同、组内单元相同"原则分流，最终通过codegen生成多stream代码。

3) 与文档论点完全对应：图示的"CV分离策略→compute unit分流→并行codegen"流程，正是文档所述利用昇腾CV并行能力、突破串行瓶颈、实现推理加速的技术路径。
