# Communication over Computation for Computation-Communication Parallelism

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/communication-over-computation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/communication-over-computation.md

# Communication over Computation for Computation-Communication Parallelism 深度解读

## 【定位】
本文档描述 mindspeed-llm 在 LLM 分布式训练中解决 ColumnParallelLinear / RowParallelLinear 层内「Matmul 计算」与「集合通信（AllReduce / AllGather / ReduceScatter）」因顺序依赖而串行执行、导致计算流与通信流互相空等问题的能力，通过细粒度拆分与流水化重叠（两种实现：Python 脚本切分 / 融合算子）提升执行效率。

## 【技术要点】

1. **问题根源**：ColumnParallelLinear、RowParallelLinear 的前向与反向中存在相邻的计算-通信对，且为顺序依赖（下一阶段输入依赖上一阶段输出），常见串行执行使得计算流与通信流互等。
2. **核心思想**：将计算与通信任务切分为更细粒度的子任务，通过流水（pipelining）实现重叠，提升 SM 计算单元与通信引擎的利用率。
3. **Python 脚本实现**：将张量沿 `m` 维度进一步拆为 2 / 4 / 8 份，对每份子张量交叠计算与通信；要求 Matmul 左矩阵的 `m` 维是切分数的整数倍；切分过细易出现 host bound，反而得不偿失。
4. **融合算子实现**：基于昇腾 MTE 远程内存访问能力，在算子内部以大核融合方式实现更细粒度的计算-通信子任务流水重叠，绕过 host 调度开销。
5. **三类通信场景全覆盖**：支持 `ALL_REDUCE`、`ALL_GATHER`、`REDUCE_SCATTER`；用户可灵活选择「先通信后计算」或「先计算后通信」。
6. **已支持的融合算子矩阵**：① `MATMUL_ALL_REDUCE`（先计算后通信，含确定性计算变体）② `MATMUL_REDUCE_SCATTER`（先计算后通信，含确定性计算变体）③ `ALL_GATHER_MATMUL` 与 `ALL_GATHER_MATMUL_V2`（先通信后计算，`V2` 可访问 `ALL_GATHER` 中间结果）④ 量化场景：`MATMUL_ALL_REDUCE` 支持 FP16 格式下的 W8A16 伪量化，粒度涵盖 per tensor / per channel / per group。
7. **优先级与约束**：同时设置 `coc-fused-kernel` 与 `coc-parallel-num > 1` 时，前者优先生效并覆盖后者；融合算子目前仅支持 TP=8；尚未兼容 `--use-ascend-mc2`；尚未适配 MoE 模型；HDK ≥ 2024 RC2、CANN ≥ 2024 RC4。

## 【关键机制与数据】

**工作原理（原文驱动逻辑链）**：
- 顺序依赖的「Matmul ↔ 集合通信」相邻对在 TP（张量并行）层中天然存在：原文将其形式化为「输入依赖输出」的串行链路。
- 解决路径：把链路切成 N 段（N∈{2,4,8}），让「段 i 的通信」与「段 i+1 的计算」在同一时间窗内并发，理论上可将原本串行时延近似压缩为 max(总计算，总通信)+ 一段启动开销。
- 两种工程路径：① 脚本侧切分——简单、灵活，但调度受 Python host 端限制；② 融合算子侧——借助 MTE 远程内存访问直接在 device 端 kernel 内拉起通信流水，绕开 host bound。

**关键配置数值（原文直接给出）**：
- 切分数（`--coc-parallel-num`）：**2、4 或 8**。
- Matmul 左矩阵 `m` 维约束：必须是切分数的整数倍。
- 融合算子 `coc-fused-kernel` 当前仅支持 **TP=8** 场景。
- ATB 依赖：随 CANN-NNAL 安装后执行 `source /usr/local/Ascend/nnal/atb/set_env.sh`。
- 软件版本基线：HDK ≥ **2024 RC2**，CANN ≥ **2024 RC4**。

**数据流形态（原文归纳的三类 fused op）**：
- 「先算后通」：`MATMUL_ALL_REDUCE`、`MATMUL_REDUCE_SCATTER`。
- 「先通后算」：`ALL_GATHER_MATMUL` / `ALL_GATHER_MATMUL_V2`。
- 量化链路：`MATMUL_ALL_REDUCE` 在 FP16 通路下承担 W8A16 伪量化（per tensor / per channel / per group）。

**性能前提警告（原文提示）**：
- 「计算与通信段耗时差异很大」的场景不适用脚本侧实现——因为重叠后整体仍受限于较长那段，难以摊薄开销。
- 切分数量过大时易转为 host bound，收益消失。

## 【表格解读】
原文无表格（全文以散文与命令片段形式给出，未提供参数表、性能对比表或配置矩阵）。与表格相关的「关键参数对照」可由读者据命令片段自行整理为：`--coc-parallel-num ∈ {2,4,8}`、`--coc-fused-kernel` 要求 TP=8、`coc-fused-kernel` 优先级高于 `coc-parallel-num > 1`。

## 【公式解读】
原文无公式（不含 LaTeX 表达式或伪代码公式）。

## 【关联】

- **作用对象**：`ColumnParallelLinear` 与 `RowParallelLinear`（Megatron-Core / mcore 路径下的张量并行线性层），覆盖其前向与反向中的 Matmul-AllReduce / Matmul-AllGather / Matmul-ReduceScatter 相邻对。
- **触发模块**：`Attention` 与 `MLP`（原文明确指出适用于这两个模块串行执行且存在相邻顺序依赖的场景）。
- **并行维度耦合**：与张量并行（TP）紧耦合——`coc-fused-kernel` 当前限 TP=8；与序列并行（SP）正交，SP 启用时通信形式由 AllReduce 切换为 AllGather/ReduceScatter，原文方案仍需覆盖此分支。
- **互斥/未适配项**：① 与 `--use-ascend-mc2` 互斥；② 尚未适配 MoE 模型；③ 依赖昇腾硬件运行时（HDK ≥ 2024 RC2）与 CANN 软件栈（≥ 2024 RC4），并依赖 ATB（NNAL 子包）以使用融合算子路径。
- **内部链接信息**：原文文末标注「(无)」，未提供其他特性的内部跳转链接，故无法依据链接拓扑进一步推断上下游。

## 【使用方法】

**总开关**：`--use-ascend-coc`（启用计算-通信并行）。

**方式一：Python 脚本实现**
```shell
--use-ascend-coc
--coc-parallel-num 2 # 或 4，或 8
```
前置约束：Matmul 左矩阵 `m` 维需为所选切分数的整数倍；计算与通信段耗时差异较大时不适合。

**方式二：融合算子实现**
```shell
--use-ascend-coc
--coc-fused-kernel   # 注：当前仅支持 TP=8 场景
```
前置依赖：必须先安装 ATB；安装路径为安装 CANN-NNAL 包后执行：
```shell
source /usr/local/Ascend/nnal/atb/set_env.sh
```

**优先级规则**：当同时使用 `coc-parallel-num > 1` 与 `coc-fused-kernel` 时，`coc-fused-kernel` 优先生效并覆盖 `coc-parallel-num > 1`。

**互斥与版本约束（原文注意事项）**：
- 与 `--use-ascend-mc2` 暂不兼容。
- 尚未适配 MoE 模型。
- HDK 需 2024 RC2 及以上版本；CANN 需 2024 RC4 及以上版本。
