# FA_Power_Cap 技术

> 仓 `mindie-sd` · 路径 `docs/zh/features/fa_power_cap.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/fa_power_cap.md

# FA_Power_Cap 技术文档深度解读

## 【定位】

这篇文档面向长时长、高清多模态视频生成中 FA 算子耗时与功耗过高的痛点，介绍如何通过**切分 FA 算子并重排 FA 与通信执行顺序**来撑大 FA 计算间隙、打破 AI 处理器持续高密计算，从而把整网平均功耗压在 PCIE 板卡 TDP 上限内、避免 PMC 触发降频、提升整网性能，并以 Wan2.2 + Ulysses 序列并行为载体给出 `--comm_type` 三种模式的接入方法。

## 【技术要点】

- **作用对象与前提**：仅适用于已开启 Ulysses 序列并行的 Wan 推理任务，要求 `ulysses_size > 1` 且 attention head 数能被 Ulysses 并行度整除；统一通过新增入口 `--comm_type` 在 baseline / insertcomm / blockattn 三条路径之间分发，不改变 `attention_forward` 输出投影与整体 attention 语义。
- **核心思想**：将 FA 算子按 attention head 切分为多块（`loop_time = 10`），在每块 FA 之间插入 `A2A`（AlltoAll）通信与必要的旋转/量化操作，撑大 FA 与 FA 之间的间隙，让 AI 处理器"计算一段时间 → 休息一下 → 再继续"，降低持续高密计算带来的瞬时功耗。
- **三种模式递进**：
  - `comm_type=0`（Baseline）：保持原始 `AlltoAll → FA → AlltoAll` 单轮路径；
  - `comm_type=1`（InsertComm）：在单卡上先按 attention head 分块，再逐块执行 `AlltoAll → FA`；
  - `comm_type=2`（BlockAttn）：在 head 分块基础上，把本地 query sequence 固定切成 `block_count = 2` 个 block 分别做 FA（K/V 不切 sequence），进一步细分 FA 计算单元。
- **关键工程约束**：`heads_per_chunk = heads_per_npu // loop_time`、`global_chunk_size = heads_per_chunk * world_size`；`loop_time=10` 与 `block_count=2` 均为写死的固定常量，不再暴露额外拆分粒度参数；同时保留原 attention 路径里的 ring、padding、RainFusion、FA 算子选择和量化分支，不能用简化代码直接替换完整实现。
- **FSDP/双 transformer 适配**：当 `args.dit_fsdp` 为真时，需要把 `args` 挂到 `_fsdp_wrapped_module.blocks[i]._fsdp_wrapped_module.args`；Wan2.2 若同时使用 high-noise / low-noise 两个 transformer，必须对两者都执行相同的挂载/分支注入。
- **启用方式**：在 `generate.py` 的 argparse 中以 `choices=[0, 1, 2]` 注册 `--comm_type`（默认 0），并在参数校验处加入 `if args.comm_type != 0 and args.ulysses_size <= 1: raise ValueError(...)`，避免单卡或未开启 Ulysses 时误开优化。

## 【关键机制与数据】

- 原文：长序列负载所需功耗若超过 **PCIE 板卡 TDP（Thermal Design Power）上限**，**PMC（Power Management Controller）** 可能触发降频以控制平均功耗，因此本技术目标是"把功耗按在 TDP 以内"。
- 原文：FA 算子被切分为 **`loop_time = 10`** 轮（即 head 分块粒度）；BlockAttn 在此基础上再把 query sequence 切成 **`block_count = 2`** 块，两块 query 共享同一份完整 K/V。
- 原文：head 分块尺寸由 `heads_per_chunk = heads_per_npu // loop_time` 与 `global_chunk_size = heads_per_chunk * world_size` 决定，并要求 `head_count % world_size == 0` 与 `heads_per_rank % loop_time == 0` 两个整除条件同时成立，否则会抛出 `ValueError`。
- 原文：InsertComm 路径的执行顺序为 "按 head 切块 → 每块 `AlltoAll(scatter=2, gather=1)` Q/K/V → `attention_forward(opt_mode="manual", op_type="fused_attn_score", layout="BNSD")` → `AlltoAll(scatter=1, gather=2)` → `torch.cat(dim=2)` 拼接"。
- 原文：BlockAttn 路径在 InsertComm 之上，对每块的 `query_layer` 再用 `torch.tensor_split(query_layer, 2, dim=1)` 切两半，每半 query 都对完整的 `key_layer` / `value_layer` 做一次 FA，最终在 `dim=1` 上 cat 还原。
- 原文：流水线包含输入处理、通信、矩阵乘法、量化、注意力计算、拼接、输出投影等阶段（见 `figures/fa_power_cap_pipeline.png`）；baseline 保持原始 `QKV 投影 → RoPE → A2A QKV → 旋转/量化 → FA` 路径，insertcomm / blockattn 在此基础上对循环位置进行调整。
- 原文未提供任何具体的功耗下降百分比、加速比、tokens/s 或温度/频率数值等性能数据，因此本文档不引用任何性能指标。

## 【表格解读】

**原文表格逐字还原**：

| 模式 | 参数 | 行为 |
| --- | --- | --- |
| Baseline | `--comm_type 0` | 保持原始基线路径：一次 `AlltoAll -> FA -> AlltoAll`。 |
| InsertComm | `--comm_type 1` | 单卡上先按 attention head 分块，再逐块执行 `AlltoAll -> FA`。 |
| BlockAttn | `--comm_type 2` | 单卡上先按 attention head 分块，再把本地 query sequence 固定切成 2 个 block 分别做 FA。 |

**逐行解读**：

- **Baseline / `--comm_type 0`**：等价于不开启本特性的默认行为，一个 attention 层内只发生一次完整的 Q/K/V `AlltoAll(scatter=2, gather=1)`、一次 FA、一次输出 `AlltoAll(scatter=1, gather=2)`；功耗与原方案相同，无 FA 切分间隙，是性能与功耗的"参照点"。
- **InsertComm / `--comm_type 1`**：在原本"一次性 A2A + 一次性 FA"的连续高密计算块中间插入 `loop_time=10` 次 head 分块循环，每轮独立做 A2A 与小规模 FA，用通信把小块 FA 撑开，目的是打断持续高密计算、降低平均功耗。
- **BlockAttn / `--comm_type 2`**：在 InsertComm 的 head 分块之上再叠加一层 query sequence 二分（`block_count=2`，K/V 不切），把 FA 计算单元进一步拆细，FA 与 FA 之间的间隙更大，更有利于在 TDP 边缘徘徊的长序列负载下压低峰值功耗；三种模式互斥，一次只能选其一。

## 【公式解读】

原文无 LaTeX 数学公式，也未给出独立的伪代码公式段；与"计算粒度"相关的关键量仅以代码赋值形式出现，等价记号如下（符号含义与作用列在公式后）：

- `loop_time = 10`：固定切分轮数（即 head 分块后外层循环次数），用于撑大 FA 间隙，原文要求"不再暴露额外参数"。
- `heads_per_chunk = heads_per_npu // loop_time`：每张卡每轮负责的 attention head 数；其中 `heads_per_npu = head_count // world_size`，`head_count` 为模型 attention head 总数，`world_size` 为 Ulysses 并行度（`dist.get_world_size(group=self.ulysses_pg)`）。
- `global_chunk_size = heads_per_chunk * world_size`：单次 `query.split(..., dim=2)` 在 head 维度上切出的全局 chunk 尺寸，对应"按 head 分块"的总粒度。
- `block_count = 2`：仅在 BlockAttn 中使用，把本地 `query_layer` 用 `torch.tensor_split(query_layer, 2, dim=1)` 切成两段，每段 query 对完整 K/V 独立做 FA。

约束/校验公式（亦以代码形式给出）：

- `head_count % world_size != 0` ⇒ `ValueError`：要求 Ulysses 并行度能整除 head 总数。
- `heads_per_rank % loop_time != 0` ⇒ `ValueError`：要求单卡 head 数能被 10 整除，否则 head 分块不均。

## 【关联】

文档未在文末提供任何内部 Markdown 链接（"内部链接: (无)"），但正文里出现了以下上下游/相关模块，可作为关联梳理：

- **目标模型**：Wan2.2（含 high-noise 与 low-noise 两个 transformer），作为 `FA_Power_Cap` 的接入示例载体。
- **并行框架**：Wan Ulysses 序列并行（`ulysses_pg`、`ulysses_size`），是本特性的硬性前提。
- **算子/通信原语**：`attention_forward`（来自 `mindiesd`，签名 `opt_mode="manual", op_type="fused_attn_score", layout="BNSD"`）、`all_to_all_4D`（来自用户仓库的 sequence parallel 模块）、`torch.distributed` 的 `ulysses_pg` 进程组。
- **不改动但需保留的 attention 周边路径**：QKV 投影、RoPE/旋转编码、量化、ring、padding、RainFusion、输出投影、`fused_attn_score` FA 算子选择。
- **训练/分布式封装层**：FSDP（`args.dit_fsdp` 分支下 `_fsdp_wrapped_module`），需要在挂 `args` 时对 `_fsdp_wrapped_module.blocks[i]._fsdp_wrapped_module` 做一次解包。
- **三类执行路径的代码合流点**：`attnlayer.py` 中的 `comm_type` 分发（`baseline / _run_insertcomm / _run_blockattn`），是本特性在仓库内唯一的统一入口。
- **上游约束**：PCIE 板卡 TDP 与 PMC 功耗保护机制（昇腾/板卡级硬件功耗管理能力），是本技术存在的原因；下游用户面表现为整网平均功耗下降与整网性能提升，但原文未给出量化数据。

## 【使用方法】

原文提供了完整的五步接入流程与 `attnlayer.py` 整合示例，关键命令/配置如下：

- **新增命令行参数**（在 `generate.py` 的 argparse 中）：
  ```python
  parser.add_argument(
      "--comm_type",
      type=int,
      default=0,
      choices=[0, 1, 2],
      help="FA_Power_Cap attention communication mode: 0 disables it, 1 enables insertcomm, 2 enables block attention.")
  ```
- **参数校验**：在参数校验处加入
  `if args.comm_type != 0 and args.ulysses_size <= 1: raise ValueError("comm_type optimization requires ulysses_size > 1.")`
  以禁止单卡/未开 Ulysses 时误用 `comm_type=1/2`。
- **把 `args` 挂到 attention block**（普通模型 vs FSDP 包装模型分别处理；双 transformer 需对 high/low 都执行）：
  ```python
  if args.dit_fsdp:
      for block in transformer._fsdp_wrapped_module.blocks:
          block._fsdp_wrapped_module.args = args
  else:
      for block in transformer.blocks:
          block.args = args
  ```
- **在 attention 类中读取并分发**：
  ```python
  self.comm_type = int(getattr(self.args, "comm_type", 0))
  ...
  if self.fa_alltoall_overlap: ...
  elif self.comm_type == 1: ...
  elif self.comm_type == 2: ...
  else: ...
  ```
- **运行模式选择**：通过 `--comm_type 0|1|2` 互斥启用 Baseline / InsertComm / BlockAttn；InsertComm 内置 `loop_time=10` 且要求 `heads_per_rank % 10 == 0`，BlockAttn 在此之上把 query 切成 2 块。

## 图文联合解读

- `fa_power_cap_pipeline.png`: 图示Baseline/insertcomm/blockattn三种路径：insertcomm将A2A→旋转→量化→FA→A2A按head分块循环；blockattn在此基础上再拆分Q，内层循环重复"Matmul旋转Q→量化Q→FA"。通过把通信插入FA之间、撑大FA间隙，使处理器间歇休息打断持续高密计算，从而降低整网平均功耗、避免PMC触发降频，与文档"切分FA并重排通信顺序降功耗提性能"的论点完全对应。
