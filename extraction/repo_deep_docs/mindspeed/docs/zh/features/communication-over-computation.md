# 计算通信并行 CoC (Communication Over Computation)

> 仓 `mindspeed` · 路径 `docs/zh/features/communication-over-computation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/communication-over-computation.md

# 「计算通信并行 CoC (Communication Over Computation)」Feature 文档深度解读

---

## 【定位】

这篇文档解决大模型训练中 Transformer 的 **ColumnParallelLinear / RowParallelLinear** 层中"计算（Matmul）与集合通信（AllReduce / AllGather / ReduceScatter）"因顺序依赖被串行执行、导致流水气泡（空闲等待）的问题，提供两种覆盖方案——**Python 脚本切分子张量**与**融合大 Kernel 算子**——实现通信与计算的细粒度流水并行（Communication-over-Computation）。

---

## 【技术要点】

1. **依赖关系与优化对象**：在大模型训练中，`ColumnParallelLinear` 与 `RowParallelLinear` 的前向/反向均包含"互相毗邻、顺序依赖"的 Matmul + 集合通信组合，后一个算子的输入依赖前一个输出，因此常被串行调度，**计算流与通信流均存在空闲等待**。文档的目标就是把这两类算子拆成更细粒度的子任务，使通信"叠"在计算上。

2. **两条实现路径并存**：
   - **Python 脚本侧**：将左矩阵沿 m 轴切成 **2 / 4 / 8 份**，通过脚本控制每个子 tensor 的计算与通信交替推进。要求 **m 必须是切分数的倍数**。
   - **融合算子侧**：基于 NPU 的 **MTE 远端内存访问**能力，将计算与通信封装在单个大 Kernel 内做内部流水掩盖，吞吐更高但仅 **TP=8** 场景支持。

3. **支持的三类通信语义**：`ALL_REDUCE`、`ALL_GATHER`、`REDUCE_SCATTER`；并允许灵活选择"**先通信后计算**"或"**先计算后通信**"。

4. **已落地的融合算子清单**（含确定性计算版本）：
   - `MATMUL_ALL_REDUCE`（先计算后通信）
   - `MATMUL_REDUCE_SCATTER`（先计算后通信）
   - `ALL_GATHER_MATMUL`、`ALL_GATHER_MATMUL_V2`（先通信后计算，**V2 接口可获取 ALL_GATHER 中间结果**）

5. **量化支持**：融合算子 `MATMUL_ALL_REDUCE` 支持 **fp16 格式的 w8A16 伪量化**，粒度涵盖 **per tensor / per channel / per group**。

6. **配置项语义**：用户可通过 `user_config.py` 中的 `coc_cfgs` 字典实现按 shape 自定义切分份数、对张量做 NPU 亲和的 transpose/padding（`matmul_soc_friendly`，默认 True）、开关 ColumnParallelLinear 反向 COC、开关反向 all gather 的重计算（默认 True，会降低峰值显存占用）。

---

## 【关键机制与数据】

### 工作原理

- **问题根源**：`ColumnParallelLinear` / `RowParallelLinear` 中的 Matmul 与集合通信因输入输出依赖被串行调度，形成 compute bubble 与 comm bubble。原文：**"这些计算通信的组合因为存在顺序依赖（即后一个的输入是前一个输出），常常被串行执行，但这时候计算和通信流都存在一定的空闲等待时间，该过程的执行效率没有被最大化。"**

- **解决思路总述**：原文：**"通过将计算和通信任务分别拆分成更细粒度的子任务来实现相互的流水掩盖。"**
  - Python 脚本侧：把张量进一步切成 **2/4/8 份**，让子 tensor 之间的计算与通信错峰推进。原文：**"增大计算和通信流的利用率。"**
  - 融合算子侧：原文：**"基于MTE远端内存访问能力，以融合大Kernel方式在算子实现的内部将计算和通信任务分别拆分成更细粒度的子任务来实现相互的流水掩盖。"**

- **替换点**：两种实现都需替换原 Megatron 框架的 `ColumnParallelLinear` 与 `RowParallelLinear` 的 forward，适配脚本位于 `mindspeed/core/tensor_parallel/lcal_coc/` 目录下。

### 端到端性能数据（原文）

| 模型 | 端到端收益 |
|---|---|
| BLOOM 7B | **约 3.20%** |
| BLOOM 176B | **约 5.47%** |
| LLAMA2 70B | **约 7.85%** |

原文：**"精度相对误差控制在2%的范围内。"**

### 适用与不适用条件

- **适用**：Attention 与 MLP 串行执行，且计算-通信存在顺序依赖与位置毗邻关系的训练场景。
- **不适用 / 受限**：
  - Python 脚本实现：**m 必须为切分数（2/4/8）的倍数**；**不适用于计算与通信片段耗时相差较大的情况**；原文：**"脚本侧实现在切分矩阵、切分数量较大时，容易出现host bound问题，从而不能得到预期的收益。"**
  - 融合算子实现：**仅支持 TP=8**；**不支持 Ascend 950 系列产品**；需安装 ATB（`source /usr/local/Ascend/nnal/atb/set_env.sh`）。
  - 通用：**不兼容 `--use-ascend-mc2`**，**暂未适配 MoE 模型**。

---

## 【表格解读】

**原文无表格**（文档中未出现结构化表格，仅有若干命令片段与上述性能列表。性能数据已在「关键机制与数据」中以表格形式还原；CFG 配置项为键值对字典而非表格，故此处不强行还原为表格。）

如需以表格形式查阅**全部配置项**，根据原文整理如下（**非原文表格，仅为信息归集**）：

| 配置项 | 适用范围 | 默认值 | 作用（原文） |
|---|---|---|---|
| `matmul_soc_friendly` | 仅 Python 脚本 | `True` | 是否对输入 matmul 的张量做 transpose/padding，使其以 NPU 亲和的 shape 进入 Matmul 算子 |
| `customized_coc` | 仅 Python 脚本 | `{}` | 自定义指定 shape 的 matmul 的 COC 切分份数；示例 `{"[16384, 5120, 1920]": 8, "[16384, 1920, 5120]": 1}` |
| `enable_coc_in_column_backward` | 仅融合算子 | `False` | 是否在 ColumnParallelLinear 的反向中使用 COC（其反向中本就有非互相依赖的计算通信并行） |
| `recompute_all_gather` | 脚本与融合算子均适用 | `True` | 是否在 ColumnParallelLinear 反向中重算 all gather；若 False 则从前向保存结果，会减少反向计算时间但增加峰值显存占用 |

---

## 【公式解读】

**原文无公式**（文档未出现 LaTeX 或伪代码形式的数学公式）。

文档中唯一接近"伪公式"的元素是 `customized_coc` 的字典映射示例：

```
'customized_coc': {"[16384, 5120, 1920]": 8, "[16384, 1920, 5120]": 1}
```

可解读为：键是一个三元素 shape 列表 `[M, K, N]`，值是对应 Matmul 的 COC 切分份数（`8` 开启 COC 并切 8 份；`1` 表示不开 COC，沿用默认通信路径）。允许按 shape 单独指定与全局 `--coc-parallel-num` 不同的份数。

---

## 【关联】

文末内部链接标注为「无」，因此下述关联基于正文上下文提炼：

- **上游框架 / 被替换对象**：依赖 **Megatron** 的 `ColumnParallelLinear` 与 `RowParallelLinear` 两个 class——文档中明确指出"**替换脚本已经根据 MindSpeed 指定 Megatron 版本进行编码和适配，位于 `mindspeed/core/tensor_parallel/lcal_coc/` 目录下**"，说明 CoC 是 Megatron 张量并行的**非侵入式增强**。

- **同包内模块路径**：
  - `mindspeed/core/tensor_parallel/lcal_coc/`：CoC 替换脚本与配置目录。
  - `mindspeed/core/tensor_parallel/lcal_coc/user_config.py`：用户自定义 `coc_cfgs` 字典的入口。

- **不兼容特性**：`--use-ascend-mc2`（MC2 是昇腾上另一种 Matmul-通信融合路径，与 CoC 融合算子在同一通信语义上互斥，启用其一即可）。两者在功能定位上属于"同源替代"关系。

- **硬件依赖**：
  - **ATB**（Ascend Transformer Boost）：融合算子实现的运行前置，需 `source /usr/local/Ascend/nnal/atb/set_env.sh`。
  - **Atlas A2 训练系列产品 / Atlas A3 训练系列产品**：完全支持（含融合算子）。
  - **Ascend 950 系列产品**：不支持融合算子。

- **训练流水线中的位置**：Attention 模块与 MLP 模块串行执行时作用最显著，因为这两段都是 `ColumnParallelLinear` → `RowParallelLinear` 的标准结构，CoC 的覆盖收益在这两段累积。MoE 模型暂未适配，故与 MoE 路径**互斥**。

---

## 【使用方法】

### 启用总开关

两种实现共用同一总开关，原文：

```
设置 --use-ascend-coc 使能计算通信并行功能
```

### 方式 1：Python 脚本实现

```shell
--use-ascend-coc
--coc-parallel-num 2   # 或者 4，或者 8
```

要求 m 轴长度为切分数的倍数；不支持"计算与通信耗时差异巨大"的场景。

### 方式 2：融合算子实现

前置：安装 ATB（`source /usr/local/Ascend/nnal/atb/set_env.sh`）。

```shell
--use-ascend-coc
--coc-fused-kernel   # 当前只支持 TP=8 的场景
```

**优先级规则（原文）**："**融合算子方式拥有更高优先级，即当同时设置 `--coc-parallel-num` 和 `--coc-fused-kernel` 时，将采用融合算子实现，`--coc-parallel-num` 参数不生效。**"

### 自定义配置

编辑 `mindspeed/core/tensor_parallel/lcal_coc/user_config.py` 中的 `coc_cfgs` 字典，可调项见「表格解读」中的配置项表：`matmul_soc_friendly`（仅脚本）、`customized_coc`（仅脚本）、`enable_coc_in_column_backward`（仅融合算子）、`recompute_all_gather`（通用）。

### 不兼容性开关

- `--use-ascend-mc2`：暂不兼容。
- MoE 模型：暂未适配。
