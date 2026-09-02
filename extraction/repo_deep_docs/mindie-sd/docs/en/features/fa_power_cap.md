# FA_Power_Cap Technology

> 仓 `mindie-sd` · 路径 `docs/en/features/fa_power_cap.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/fa_power_cap.md

# 一体化深度解读：FA_Power_Cap Technology

## 【定位】
本文档面向长序列（百万 token 量级）多模态视频生成场景，介绍 `FA_Power_Cap` 技术——通过拆分 Flash Attention 算子并重排 FA/通信顺序，在 PCIe 卡的 TDP 预算约束下降低端到端平均功耗、改善端到端性能，并以 Wan2.2 + Ulysses 序列并行为例给出可落地的代码改造步骤。

---

## 【技术要点】

1. **问题背景与触发机制**：当长序列工作负载所需功率超过 PCIe 卡的 TDP 上限时，PMC（Power Management Controller）会触发**降频（frequency throttling）**以维持平均功率在 TDP 预算内。`FA_Power_Cap` 旨在缓解该问题。
2. **核心机制**：在 FA 算子内部进行拆分，并在分片之间的 FA 执行前**插入通信**（insert communication），从而拉长相邻 FA 执行之间的间隔，打断 AI 处理器上的持续高密度计算。
3. **作用范围与约束**：仅在 **Wan Ulysses 序列并行** 场景下有意义；运行时必须满足 `ulysses_size > 1`，且 **attention head 数量必须能被 Ulysses world size 整除**。
4. **三种模式（由 `--comm_type` 单一切换）**：
   - `--comm_type 0`（Baseline）：保持原始路径，单次 `AlltoAll -> FA -> AlltoAll`。
   - `--comm_type 1`（InsertComm）：每卡内按 attention head 分片，按 chunk 顺序执行 `AlltoAll -> FA`。
   - `--comm_type 2`（BlockAttn）：先按 head 分片，再把本地 query 序列拆为 **2 个 FA 块**。
5. **关键参数（原文给出）**：
   - InsertComm：`loop_time = 10`，`heads_per_chunk = heads_per_npu // loop_time`，`global_chunk_size = heads_per_chunk * world_size`。
   - BlockAttn：`block_count = 2`（固定为 2，不需要用户再调）。
6. **保持不动的语义与路径**：`attention_forward` 仍为 FA 计算入口；不改变 output projection 路径与整体 attention 语义；只调整 `A2A` 通信、RoPE/rotation、量化与 FA 计算在 **head-chunk 或 Q-block 循环** 内的放置位置。

---

## 【关键机制与数据】

**工作原理（数据流）：**
- **Baseline** 路径：原始的 QKV 投影 → RoPE → `A2A QKV` → rotation/quantization → FA → `A2A` → 输出投影。
- **InsertComm** 路径：将 `A2A -> rotation/quantization -> FA -> A2A` 移入"按 attention head chunk"的循环内，每次循环处理一小段 head chunk。
- **BlockAttn** 路径：在 InsertComm 基础上，将 Q 再拆为若干 Q 块，每个 Q 块重复执行 rotation、quantization、FA，最后把 Q 块与 head 的结果拼接起来。
- 通信细节：InsertComm 使用 `all_to_all_4D(q_chunks[chunk_id], scatter_idx=2, gather_idx=1, group=self.ulysses_pg)` 做 scatter→gather，回程使用 `scatter_idx=1, gather_idx=2`；BlockAttn 中 K、V 不按 sequence 切分，每个 query 块都 attend 到完整的本地 K/V。
- 调度入口：`attnlayer.py` 仅需按 `comm_type` 在 baseline、`_run_insertcomm`、`_run_blockattn` 之间 dispatch。

**性能数据（原文有的部分）：**
- 原文未提供具体功耗/性能数字（例如平均功率下降幅度、吞吐加速比等），仅以定性方式描述其效果为"reduces end-to-end model average power consumption and improves end-to-end performance"。
- 场景规模参考：原文出现"百万 token 量级或以上（million-token scale or beyond）"以及"长时长高分辨率视频生成（long-duration high-definition video generation）"。

---

## 【表格解读】

**原文表格：三种模式对比**

| Mode | Argument | Behavior |
| --- | --- | --- |
| Baseline | `--comm_type 0` | Keep the original baseline path: one `AlltoAll -> FA -> AlltoAll`. |
| InsertComm | `--comm_type 1` | Within each card, split by attention heads, then run `AlltoAll -> FA` chunk by chunk. |
| BlockAttn | `--comm_type 2` | Within each card, split by attention heads first, then split the local query sequence into 2 FA blocks. |

**逐行解读：**
- **Baseline 行（`--comm_type 0`）**：默认模式，保留原有 Ulysses 序列并行路径，单次 `AlltoAll → FA → AlltoAll`，整段 attention 头一次性参与计算与通信。当序列长度急剧拉长、FA 长时间占用 AI 处理器时，容易触发 PMC 降频保护。
- **InsertComm 行（`--comm_type 1`）**：在每张卡内**先按 attention head 切片**，把原本集中的 `AlltoAll → FA` 流程拆成多次按 chunk 执行的小循环。其关键作用是把"FA 高密度计算"在时间轴上分散开，给 AI 处理器留出恢复窗口；与此同时每次集合通信的数据量更小。
- **BlockAttn 行（`--comm_type 2`）**：在 InsertComm 的 head 切分之上，**进一步将本地 query 序列拆成 2 块**，每块独立完成 attention 计算后再拼接（K/V 不切）。这是更激进的时间分散策略，由 `--comm_type 2` 单一切换，用户无需额外调参。

文档其余部分以代码形式给出，未再出现其他表格。

---

## 【公式解读】

原文无公式（LaTeX 或伪代码形式的数学公式）。

文中出现的 `loop_time = 10`、`heads_per_chunk = heads_per_npu // loop_time`、`global_chunk_size = heads_per_chunk * world_size` 以及 `block_count = 2` 均为代码中的整型赋值/形状推导表达式，属于实现细节参数而非独立公式；相关含义已并入【技术要点】与【关键机制与数据】节。

---

## 【关联】

原文未提供内部链接（"内部链接: (无)"）。以下关系基于原文正文中的明确引用：

- **上游/前置条件**：
  - Wan2.2 模型仓库（"This guide uses Wan2.2 as an example"），且默认用户已能跑通该仓库。
  - Wan Ulysses 序列并行（"`FA_Power_Cap` targets Wan Ulysses sequence parallelism"），依赖 `ulysses_pg` 进程组。
  - `mindiesd.attention_forward`（`from mindiesd import attention_forward`），为 FA 计算统一入口。
  - `all_to_all_4D`（来自用户的 `your_wan_sequence_parallel_module`），用于 Ulysses 的 AlltoAll 通信。
- **与注意力子结构的耦合**：
  - QKV 投影、RoPE、padding、ring、RainFusion、量化（quantization）等分支在改造中**保留**，仅重新编排它们与 FA、`A2A` 在 head-chunk / Q-block 循环内的相对顺序。
  - 不修改 `attention_forward` 入口与 output projection 路径，保持整体 attention 语义不变。
- **与训练/并行栈的耦合**：
  - 同时兼容 FSDP 包装（`dit_fsdp=True`）与非 FSDP 路径，需分别写入 `transformer._fsdp_wrapped_module.blocks` 或 `transformer.blocks`。
  - Wan2.2 存在 high-noise 与 low-noise 两套 transformer 时，需对两者都执行 args 注入。
- **不重叠的并行优化**：
  - 与 `fa_alltoall_overlap` 互斥分支：在 `__init__` 中通过 `if self.fa_alltoall_overlap ... elif comm_type==1 ... elif comm_type==2 ... else` 的优先级组织。

---

## 【使用方法】

> 以下步骤对应原文 Step 1 – Step 5 及 `attnlayer.py` 整合示例。

**1. 在 `generate.py` 中注册命令行参数：**

```python
parser.add_argument(
    "--comm_type",
    type=int,
    default=0,
    choices=[0, 1, 2],
    help="FA_Power_Cap attention communication mode: 0 disables it, 1 enables insertcomm, 2 enables block attention.")
```

并加入校验：

```python
if args.comm_type != 0 and args.ulysses_size <= 1:
    raise ValueError("comm_type optimization requires ulysses_size > 1.")
```

**2. 把 `args` 注入到 transformer 的每个 block**（FSDP 与非 FSDP 分支都要覆盖；双 transformer 时两套都设）：
```python
if args.dit_fsdp:
    for block in transformer._fsdp_wrapped_module.blocks:
        block._fsdp_wrapped_module.args = args
else:
    for block in transformer.blocks:
        block.args = args
```

**3. 在 attention 类中读取 `comm_type`**：
```python
self.comm_type = int(getattr(self.args, "comm_type", 0))
```
并按 `fa_alltoall_overlap → comm_type==1 → comm_type==2 → else` 的优先级 dispatch。

**4. `--comm_type 1`（InsertComm）的核心循环结构**：
- 按 `heads_per_chunk = heads_per_npu // loop_time`（`loop_time = 10`）切分 Q/K/V；
- 循环内执行 `all_to_all_4D` → `attention_forward(..., opt_mode="manual", op_type="fused_attn_score", layout="BNSD")` → 回程 `all_to_all_4D`；
- 最后 `torch.cat(output_chunks, dim=2)`。
- 原文明确提醒："Do not replace the complete attention implementation with this simplified snippet"——需保留 ring、padding、RainFusion、FA 后端选择、量化分支等。

**5. `--comm_type 2`（BlockAttn）的核心结构**：
- `block_count = 2`（固定）；
- `query_blocks = torch.tensor_split(query_layer, block_count, dim=1)`；
- 每个 block 独立调用 `attention_forward`，最后 `torch.cat(block_outputs, dim=1)`；
- K、V 不按 sequence 切分。

**6. 运行入口（原文给出的对外开关）：**
- 整个改造流程对外只新增一个参数 `--comm_type`（取值 0/1/2）；
- 启用条件：`--ulysses_size > 1` 且 `attention head count % ulysses_size == 0`；
- 启用 `insertcomm`：`--comm_type 1`；
- 启用 `blockattn`：`--comm_type 2`（无需额外调参，`block_count` 固定为 2）。

**注意事项（原文给出）：**
- `comm_type` 仅在 Ulysses 序列并行开启时才有意义；
- 把示例整合进真实仓库时，必须保留目标代码中真实的类名、`all_to_all_4D` 导入路径、attention 周围的投影、RoPE、padding、ring、RainFusion、量化分支；
- 整篇改造**不修改** `attention_forward` 入口与 output projection 路径，因此不破坏整体 attention 语义。

## 图文联合解读

- `fa_power_cap_pipeline.png`: 图示三行流程对比：①基线FA前无通信，FA后直接A2A；②insertcomm将A2A提前至FA前，外层蓝色虚线框示长序列循环；③blockattn拆分Q为多块，内层绿色虚线框为子循环（含旋转、量化、FA），通信进一步前置并切分FA。论证通过重排通信与切分FA，拉开FA执行间隔、避免持续高密度计算触发PMC降频，与文档"降低平均功耗、提升端到端性能"的论点一致。
