# 基于Megatron并行策略的性能优化

> 仓 `mindspeed` · 路径 `docs/zh/user-guide/megatron_performance_optimization.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/user-guide/megatron_performance_optimization.md

# 深度解读: docs/zh/user-guide/megatron_performance_optimization.md

## 【定位】

这篇文档是 MindSpeed 昇腾大模型加速库中面向 Megatron-LM 并行策略的"性能优化总纲",系统化描述了从**性能指标定义、profiling 数据采集、瓶颈定位**,到**长文本场景下序列并行(Ascend Ulysses / Ring Attention / Double Ring Attention / 混合并行)四种优化方案选型与启用方法**的完整方法论与操作手册。

---

## 【技术要点】

1. **单 batch 性能分解公式**(原文):
   `单batch总时间 = 数据加载时间 + 模型前反向时间 + 优化器时间 + 模型后处理时间 + 通信时间 + 调度时间`
   其中"通信时间"特指"未被计算掩盖的部分"(受 PyTorch 异步机制影响)。

2. **五步调优流程**(原文):
   `采集profiling数据 → 分析算子耗时 → 分析通信耗时 → 分析内存使用 → 选择优化策略`

3. **Profiling 参数体系**: 通过 `--profile / --profile-step-start / --profile-step-end / --profile-ranks / --profile-level`(`level0`=算子耗时、`level1`=算子+通信、`level2`=完整数据)等参数控制采集范围;`--profile-with-cpu`、`--profile-record-shapes`、`--profile-save-path ./profile_dir` 控制 CPU/shape 信息与落盘路径。

4. **四类瓶颈判定**: 计算瓶颈(算子耗时占比高)、通信瓶颈(通信时间占比高)、内存瓶颈(显存占用接近上限)、数据加载瓶颈(GPU/NPU 空闲等待数据)。

5. **四种长序列并行方案**:
   - **Ascend Ulysses**:`--context-parallel-algo ulysses_cp_algo`,依赖 `num_head % (tp_size * cp_size) == 0`。
   - **Ascend Ring Attention**:`--context-parallel-algo megatron_cp_algo`,理论上序列长度无限拓展;计算块序列长度需满足 `c ≥ F/B`(F=device FLOPS,B=device 间带宽)。
   - **Ascend Double Ring Attention**:在 Ring Attention 基础上开启 `--cp-window-size > 1` 的双层 Ring 结构,要求 `cp_size % cp-window-size == 0`。
   - **Ascend 混合并行**:`--context-parallel-algo hybrid_cp_algo`,需配合 `--ulysses-degree-in-cp`,要求 `cp_size % ulysses-degree-in-cp == 0` 且 `num-attention-heads % (ulysses-degree-in-cp * tp_size) == 0`。

6. **序列长度 / 并行度黄金下限**(原文): 建议配置 `seq-length / context-parallel-size > 8k` 以确保通信可被计算掩盖;理论公式 `S/(Tα) ≥ 1/(Wβ)`,其中 `S=seq-length/context-parallel-size`,`T`=芯片理论算力,`α`=计算效率,`W`=理论通信带宽,`β`=带宽利用率。

---

## 【关键机制与数据】

**性能分解**(原文):
- "单 batch 总时间"包含 6 段:数据加载、前反向、优化器、后处理、通信、调度。
- "通信时间"特殊含义:由于 PyTorch 的特殊机制,通信与计算并行发生时,该值表示**未被计算掩盖**的那部分通信时间(原文)。

**调优流程**(原文):
- "采集profiling数据 → 分析算子耗时 → 分析通信耗时 → 分析内存使用 → 选择优化策略",五步闭环。

**Profiling 默认值**(原文表):
- `--profile` 默认 `False`;`--profile-step-start` 默认 `0`(包含);`--profile-step-end` 默认 `-1`(采集到训练结束);`--profile-ranks` 默认 `[0]`(`-1` 表示全部 rank);`--profile-level` 默认 `level0`;`--profile-with-cpu` 默认 `False`;`--profile-record-shapes` 默认 `False`;`--profile-save-path` 默认 `./profile_dir`。

**瓶颈类型 → 典型表现对照**(原文):
- 计算瓶颈 → 单卡训练速度慢,GPU/NPU 利用率低。
- 通信瓶颈 → 多卡训练加速比不理想。
- 内存瓶颈 → 训练过程中出现 OOM。
- 数据加载瓶颈 → 训练过程中 GPU/NPU 空闲等待数据。

**Ulysses 机制**(原文): 沿序列维度切分样本 → all-to-all QKV,使各卡持有完整序列但仅 attention head 子集 → 各卡并行 head 维 attention → 再一次 all-to-all 沿序列维度回收结果。前提:`num_head % (tp_size * cp_size) == 0`。

**Ring Attention 机制**(原文): 基于分块 Softmax,各卡持本地 QKV 块 → 沿环形拓扑向后发 KV、向前收 KV → 逐块遍历 → 通信与 attention 计算互相掩盖;**全程不需数据拼接**,序列长度理论上可无限拓展;兼容 FlashAttention,目前默认开启。

**Double Ring Attention 机制**(原文): 在 Ring Attention 基础上采用分布式注意力 + 双环结构(DRA),通过 `--cp-window-size > 1` 启用;`cp_size` 必须能被该参数整除。

**混合并行机制**(原文): 将 CP 维度拆为 Ulysses 维度 × Ring Attention 维度;保留 send/recv overlap、Mask 计算类型等 Ring Attention 特性。

**使用效果**(原文): 上述四种序列并行方案均"降低单设备内存消耗","相比不开启序列并行单步耗时增加,相比重计算计算效率提升"(混合并行原文措辞相同); 混合/Double Ring 还明确"通过双环结构提升计算效率"。

**经验性能数据**(原文): 在 LLaMA2 裁剪模型、32k 序列、`cp=16` 且无其他并行切分的实测中,`--cp-window-size=2` 性能最优;继续增大窗口因片上内存带宽抢占反而整体效率下降(原文)。

---

## 【表格解读】

### 表 1:Profiling 参数说明(原文逐字还原)

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--profile` | 启用性能数据采集 | False |
| `--profile-step-start` | 开始采集的 step 数(包含) | 0 |
| `--profile-step-end` | 结束采集的 step 数(不包含),设置为 -1 表示采集到训练结束 | -1 |
| `--profile-ranks` | 指定采集的 rank,设置为 -1 时表示采集所有 rank 的 profiling 数据 | [0] |
| `--profile-level` | 采集级别:level0(仅算子耗时)、level1(算子+通信耗时)、level2(完整数据) | level0 |
| `--profile-with-cpu` | 是否采集 CPU 数据 | False |
| `--profile-record-shapes` | 是否采集计算 shape(用于分析显存和计算量) | False |
| `--profile-save-path` | 采集数据保存路径 | ./profile_dir |

**逐行解读**:
- `--profile` 是总开关,默认关闭,需显式传入。
- `--profile-step-start/end` 控制采集窗口,采用左闭右开区间,`end=-1` 表示"采集到训练结束"。
- `--profile-ranks` 支持单 rank(如 `0`)或全部 rank(`-1`),默认仅 `0`,适合快速定位瓶颈,深入分析时建议扩展到全部 rank。
- `--profile-level` 提供三种粒度:轻量级(`level0` 仅算子耗时)→ 中等(`level1` 含通信)→ 完整(`level2`),随粒度提升,采集开销也会增大。
- `--profile-with-cpu` 用于抓取 host 侧耗时,排查调度瓶颈时建议开启。
- `--profile-record-shapes` 记录张量 shape,用于反推显存/计算量,排查内存瓶颈时必备。
- `--profile-save-path` 默认落盘 `./profile_dir`,后续通过 MindStudio Insight 导入分析。

### 表 2:性能分析维度(原文逐字还原)

| 分析维度 | 分析内容 | 定位目标 |
| --- | --- | --- |
| 算子耗时分析 | 识别耗时较长的算子 | 计算瓶颈 |
| 通信耗时分析 | 分析通信与计算的时间占比 | 通信瓶颈 |
| 内存分析 | 查看显存使用情况 | 显存瓶颈 |
| 流水线分析 | 分析流水线并行的空泡比例 | 并行效率 |

**逐行解读**:
- 算子耗时分析 → 计算瓶颈: 找出 Top-K 算子,通常对应 FlashAttention、MatMul 等。
- 通信耗时分析 → 通信瓶颈: 比对通信时间 vs. 计算时间的占比,若通信未被掩盖占比过高,需调整并行策略或开启 overlap。
- 内存分析 → 显存瓶颈: 监控峰值显存,排查 OOM 风险点。
- 流水线分析 → 并行效率: PP 空泡(bubble)比例,用于判断是否需要重排 stage 数或开启虚拟流水线。

### 表 3:瓶颈类型判断(原文逐字还原)

| 瓶颈类型 | 判断依据 | 典型表现 |
| --- | --- | --- |
| **计算瓶颈** | 算子耗时占比高 | 单卡训练速度慢,GPU/NPU 利用率低 |
| **通信瓶颈** | 通信时间占比高 | 多卡训练加速比不理想 |
| **内存瓶颈** | 显存占用接近上限 | 训练过程中出现 OOM 错误 |
| **数据加载瓶颈** | 数据加载时间占比高 | 训练过程中 GPU/NPU 空闲等待数据 |

**逐行解读**:
- 计算瓶颈: 算子耗时主导;表现"算得快但卡利用率低"常因算子本身优化不足,可用 FlashAttention / FP8 解决。
- 通信瓶颈: 通信未被掩盖的占比高;加速比不理想说明通信/计算未充分 overlap,需调 CP/TP/PP 组合或开启 send-recv overlap。
- 内存瓶颈: 显存接近上限→ OOM;需借助序列并行(本文四种方案)或激活值卸载。
- 数据加载瓶颈: 卡在等数据;需要异步加载、预取、dataset cache 等手段。

### 表 4:Ascend Ring Attention 重要参数(原文逐字还原)

| 重要参数 | 参数说明 | 是否可选 | 取值范围 |
| --- | --- | --- | --- |
| `--context-parallel-size [int]` | 开启 CP 对应的数量,根据用户需求配置。 | 是 | 默认为 1 |
| `--seq-length [int]` | 输入序列的长度。 | 否 | - |
| `--use-cp-send-recv-overlap` | 建议开启,开启后支持 send receive overlap 功能。 | 是 | 默认为 True |
| `--attention-mask-type` | 设置 Mask 计算类型。 | 是 | 默认是 causal(倒三角)Mask 计算,设置 general 代表全量计算 |
| `--context-parallel-algo` | 长序列并行算法选项,当设置为 `megatron_cp_algo` 时开启 Ring Attention。 | 是 | 默认值为 `ulysses_cp_algo`,其他取值可为 `megatron_cp_algo`、`hybrid_cp_algo`、`adaptive_cp_algo`、`hybrid_adaptive_cp_algo` |
| `--megatron-cp-in-bnsd` | 开启后,FA 使用 BNSD 计算。 | 是 | 默认为 True |
| `--cp-window-size [int]` | 使用原始的 Ring Attention 算法;当设置为大于 `1` 时,即使用 Double Ring Attention 算法,优化原始 Ring Attention 性能,`--cp-window-size` 即为算法中双层 Ring Attention 的内层窗口大小,需要确保 `cp_size` 能被该参数整除。 | 是 | 默认为 1 |

**逐行解读**:
- `--context-parallel-size`: CP 路数,默认 1(关闭)。
- `--seq-length`: 必填,训练输入序列长度。
- `--use-cp-send-recv-overlap`: 默认开启,实现 send/recv 与计算的重叠,**建议保持开启**。
- `--attention-mask-type`: 默认 `causal`,GPT 训练建议保持 `causal`;`general` 用于非因果场景。
- `--context-parallel-algo`: 算法路由器,可选 `ulysses_cp_algo` / `megatron_cp_algo` / `hybrid_cp_algo` / `adaptive_cp_algo` / `hybrid_adaptive_cp_algo`。
- `--megatron-cp-in-bnsd`: 控制 FA 的 layout,默认 BNSD。
- `--cp-window-size`: `=1` 退化为原生 Ring Attention;`>1` 启用 Double Ring Attention,需 `cp_size` 能被其整除。

### 表 5:算法选择指南(原文逐字还原)

| 场景条件 | 推荐算法 | 原因 |
| --- | --- | --- |
| head 数能被 cp_size 整除 | Ulysses | 通信效率高 |
| 序列长度 8K 以上 | Ring Attention | 无 head 数限制 |
| 需要进一步优化 Ring Attention 性能 | Double Ring Attention | 双环结构提升效率 |
| 需要兼顾 Ulysses 和 Ring Attention 优势 | 混合序列并行 | 融合两种算法优点 |

**逐行解读**:
- Ulysses 优势: 通信效率高(单次 all-to-all),但要求 `num_head % cp_size == 0`,head 数受限时无法扩展 cp。
- Ring Attention 优势: 无 head 数限制,理论上无限长序列;但序列块小(<8K)时带宽利用不充分。
- Double Ring Attention: 在 Ring Attention 基础上进一步优化,适合对 RA 性能仍不满意的场景。
- 混合并行: 兼具两者优势,适合大 head 数 + 长序列的复杂场景。

### 表 6:常见优化策略(原文逐字还原)

| 瓶颈类型 | 优化策略 | 适用场景 |
| --- | --- | --- |
| 计算瓶颈 | 开启 FlashAttention、使用 FP8 混合精度 | 计算密集型场景 |
| 通信瓶颈 | 调整并行策略、开启通信计算重叠 | 多卡/多节点训练 |
| 内存瓶颈 | 使用序列并行、激活值卸载 | 长序列训练、大模型训练 |
| 数据加载瓶颈 | 使用异步数据加载、预取机制 | I/O 密集型场景 |

**逐行解读**:
- 计算瓶颈 → FlashAttention + FP8: 算子级加速,适用于 attention-heavy 和大矩阵乘。
- 通信瓶颈 → 调并行策略 + overlap: 平衡 TP/CP/PP,开启 send-recv overlap。
- 内存瓶颈 → 序列并行 + 激活卸载: 序列维度切分降显存,激活卸载缓解 OOM。
- 数据加载瓶颈 → 异步加载 + 预取: 解耦 IO 与计算,避免 GPU/NPU 空转。

---

## 【公式解读】

### 公式 1:单 batch 总时间分解

```text
单batch总时间 = 数据加载时间 + 模型前反向时间 + 优化器时间 + 模型后处理时间 + 通信时间 + 调度时间
```

- **数据加载时间**: 从存储→CPU→device 的端到端时间,在多卡切分模型中还包含"数据加载卡广播到其他卡"的开销。
- **模型前反向时间**: 包含前向计算与反向梯度计算。
- **优化器时间**: 参数更新(如 AdamW 的动量/方差计算与 apply)耗时。
- **模型后处理时间**: 优化器之后的数据后处理或同步操作,通常与模型特有逻辑耦合。
- **通信时间**: 节点内卡间 + 节点间通信时间;由于 PyTorch 异步机制,该值特指**未被计算掩盖**的部分。
- **调度时间**: 指令从 CPU 派发到 NPU Kernel 的耗时。

**作用**: 给出 profiling 数据后做"分项耗时归因"的总账本,任何一项占比异常即对应一类瓶颈。

### 公式 2:调优五步流程

```text
采集profiling数据 → 分析算子耗时 → 分析通信耗时 → 分析内存使用 → 选择优化策略
```

- 箭头方向代表执行顺序;每一步为下一步提供输入,形成"采集 → 定位 → 优化"的闭环。
- 第三步"通信耗时"与第四步"内存使用"分别映射"通信瓶颈"和"内存瓶颈"的判定维度。

### 公式 3:计算/通信掩盖条件

```text
c ≥ F/B
```

- `c`: 每个计算块分到的序列长度。
- `F`: 每个 device 的 FLOPS。
- `B`: 每个 device 间的带宽。
- **含义**: 只有当单块 attention 计算量足够大(≥ F/B),才能在理论意义上"完全掩盖"通信开销。
- **作用**: 用于判断 Ring Attention 的"算力-带宽"匹配关系,作为设计 CP 维度的下界。

### 公式 4:经验黄金下限

```text
seq-length / context-parallel-size > 8k
```

- **含义**: 经验值,要求每卡分到的序列长度 > 8K,否则 send/recv 时间反而长于计算时间,导致性能下降。
- **作用**: 工程经验值,简化"公式 3"的判断,在 8K 上下给出"开关 CP"的明确边界。

### 公式 5:通用判据(原文)

```text
S / (T·α) ≥ 1 / (W·β)
```

- `S = seq-length / context-parallel-size`: 单卡分到的序列长度。
- `T`: 芯片理论算力。
- `α`: 计算效率(0 < α ≤ 1)。
- `W`: 理论通信带宽。
- `β`: 带宽利用率(0 < β ≤ 1)。
- **含义**: 单卡序列长度对应的计算时间 `S/(T·α)` 必须 ≥ 通信时间 `1/(W·β)`,才能实现通信被计算完全掩盖;与公式 3 等价但更通用(把"计算块大小"扩展为"单卡序列长度")。
- **作用**: 作为"`seq-length/cp_size > 8K`"的理论依据,在更长序列(如 32K、128K)场景中可直接套算。

---

## 【关联】

- **上游/历史依赖**: 文档引用的 [Megatron-LM](https://github.com/NVIDIA/Megatron-LM) 是 MindSpeed 在昇腾平台上兼容性适配的基础,提供数据并行、模型并行、序列并行等原生并行能力。
- **可视化分析工具**: 性能数据通过 [MindStudio Insight](https://www.hiascend.com/document/detail/zh/mindstudio/2600/GUI_baseddevelopmenttool/MindStudioInsight/docs/zh/user_guide/overview.md) 进行可视化分析,本文的"性能分析流程"明确依赖此工具。
- **核心内链(下游特性文档)**:`../features/ring-attention-context-parallel.md` —— Double Ring Attention 章节明确"使用方式可参考 Ring Attention 长序列并行"链接到该文档,说明 Ring Attention 在特性层有独立专章,本文档与之形成"用户指南→特性详解"的两层结构。
- **横向并列特性**:
  - **Ascend Ulysses / Ring Attention / Double Ring Attention / 混合并行** 互为并列,通过 `--context-parallel-algo` 同一开关进行算法路由(`ulysses_cp_algo` / `megatron_cp_algo` / `hybrid_cp_algo` / `adaptive_cp_algo` / `hybrid_adaptive_cp_algo`)。
  - **混合并行** 内部依赖 Ring Attention 的 send/recv overlap、Mask 类型等能力。
  - **Double Ring Attention** 复用 Ring Attention 训练场景,通过 `--cp-window-size` 升级。
- **配套优化项**: 表格 6 提到的 FlashAttention、FP8 混合精度、激活值卸载、异步数据加载/预取等并非本文档展开,但作为"常见优化策略"与序列并行方案协同使用。

---

## 【使用方法】

**性能诊断**(原文):
- 启用 profiling:`python your_train_script.py --profile --profile-step-start 5 --profile-step-end 6 --profile-ranks 0 --profile-level level1 --profile-with-cpu --profile-record-shapes --profile-save-path ./profile_dir`
- 可视化分析:将采集数据导入 **MindStudio Insight** 进行瓶颈定位。

**Ascend Ulysses 长序列并行**(原文):
```shell
# 配置项
--context-parallel-size <N>          # 默认 1,按需设置
--context-parallel-algo ulysses_cp_algo
```
- 步骤: 拷贝 `MindSpeed/tests_extend` 到 `Megatron` → 修改 `tests_extend/system_tests/feature_tests/ulysses.sh` 中的 `TOKENIZER_MODEL`/`DATA_PATH` → 执行 `bash tests_extend/system_tests/feature_tests/ulysses.sh`。
- 约束: `num_head % (tp_size * cp_size) == 0`。

**Ascend Ring Attention 长序列并行**(原文):
```shell
--context-parallel-size <N>          # 序列并行路数,默认 1
--seq-length <S>                     # 必填,输入序列长度
--use-cp-send-recv-overlap           # 默认 True,建议开启
--attention-mask-type causal|general # GPT 训练建议 causal
--context-parallel-algo megatron_cp_algo
--megatron-cp-in-bnsd                # 默认 True,FA 使用 BNSD
--cp-window-size 1                   # =1 为原始 RA;>1 启用 Double Ring
```
- 步骤: 同上,执行 `bash tests_extend/system_tests/feature_tests/ring_attention.sh`,并在脚本中将 `--cp-window-size` 设为 `1`。
- 约束: 需同时开启 FlashAttention;经验值 `seq-length / context-parallel-size > 8k`;理论判据 `S/(T·α) ≥ 1/(W·β)`。

**Ascend Double Ring Attention 长序列并行**(原文):
- 在 Ring Attention 训练场景中,将 `--cp-window-size` 设为大于 1 的整数(如 2)即可启用;`cp_size` 必须能被 `--cp-window-size` 整除。
- 步骤: 同 Ring Attention 流程,`ring_attention.sh` 中 `--cp-window-size=2`。

**Ascend 混合长序列并行**(原文):
```shell
--context-parallel-size <N>          # 默认 1
--context-parallel-algo hybrid_cp_algo
--ulysses-degree-in-cp <U>           # cp_size % U == 0 且 U > 1
                                     # 同时 num-attention-heads % (U * tp_size) == 0
```
- 步骤: 拷贝 `tests_extend` → 修改 `tests_extend/system_tests/feature_tests/hybrid.sh` 中的 `TOKENIZER_MODEL`/`DATA_PATH` → 执行 `bash tests_extend/system_tests/feature_tests/hybrid.sh`。
- 例:`--context-parallel-size=8` 时,`--ulysses-degree-in-cp` 可设为 `2` 或 `4`。
