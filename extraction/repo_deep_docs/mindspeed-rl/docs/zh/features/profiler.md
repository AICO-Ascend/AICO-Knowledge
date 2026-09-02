# 性能调优（Profiler）

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/profiler.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/profiler.md

# mindspeed-rl Profiler Feature 文档深度解读

---

## 【定位】

本文档描述 mindspeed-rl 昇腾强化学习加速库中的**性能调优（Profiler）模块**——该模块为 RL 训练流程提供性能数据采集、分析与可视化能力，帮助用户识别训练流程中的性能瓶颈并进行优化，定位为面向 RL 训练流程（覆盖 GRPO、DPO 等算法，含训练与推理多 worker 交互场景）的可配置性能剖析工具。

---

## 【技术要点】

1. **配置文件结构**：通过 YAML 中的 `profiler_config` 进行集中配置，键 `integrated` 标识「共卡模式」，其下覆盖 `profile` 总开关、`mstx` 轻量化打点开关、`stage` 阶段选择、`profile_*` 各类采集维度开关等共 14 个左右参数。
2. **作用域与场景约束**：
   - 性能数据采集**仅支持 integrated（共卡模式）**；
   - **PPO 场景**下 `stage` **不能设为 all**（单卡多进程），需手动指定 stage；
   - **DPO 场景**下部分参数未支持，且采集会多 warmup 1 步——实际采集步数 = `profile_step_end - profile_step_start + 1`。
3. **阶段（stage）维度**：可选值为 `all`、`actor_generate`、`actor_compute_log_prob`、`reference_compute_log_prob`、`critic_compute_values`、`actor_update`、`critic_update`，**支持列表传参**一次性采集多个 stage，默认值为 `all`。
4. **采集级别（profile_level）**：可选 `level_none / level0 / level1 / level2`，默认 `level0`；`level_none` 与 `mstx=true` 组合即轻量化采集模式。
5. **导出格式与存储优化**：`profile_export_type` 支持 `text` 与 `db` 两种格式；db 格式相对 text 可**减少约 70% 磁盘空间**（原文用词："可减少约70%磁盘空间"）。
6. **自定义打点两种方式**：① 用 `mindspeed_rl.utils.utils.mstx_timer_decorator` 装饰目标函数；② 调用 `torch_npu.npu.mstx.range_start("tag")` 与 `range_end(id)` 框住代码片段。

---

## 【关键机制与数据】

- **采集步数计算机制**（原文）：
  > "实际采集步数为 `profile_step_end - profile_step_start`，不包含 `profile_step_end`"
  - 即区间为半开区间 `[profile_step_start, profile_step_end)`；
  - `profile_step_start` 从 1 开始计数；
  - DPO 场景额外 warmup 1 步，采集步数变体为 `profile_step_end - profile_step_start + 1`。
- **mstx 轻量化打点覆盖范围**（原文）：
  > "MindSpeed RL 已集成所有 worker 的关键计算函数、`dispatch_transfer_dock_data`、`resharding` 等关键函数的自定义打点"
  - 轻量级采集**仅需打开** `profile: true, mstx: true, profile_level: level_none, profile_with_cpu: false, profile_with_npu: true`，包含自定义打点 + 所有通信算子内置打点。
- **大规模数据瓶颈场景**（原文）：GRPO 算法涉及多个 worker 模块交互（训练、推理），完整训练过程性能数据量可能较大，因此文档给出三条优化路径。
- **解析方式**：
  - 离线：`torch_npu.profiler.profiler.analyse(profiler_path="./profiler_data")`，**支持多份性能数据并行解析**；
  - 在线：设 `profile_analysis=true`，采集完成后自动解析（数据量大时耗时较长）。
- **可视化链路**：解析结果保存到 `profile_save_path` 指定目录 → 使用 **MindStudio Insight** 查看时间线视图、算子分析、通信分析。
- **CANN 版本依赖**（原文）：需更新至 **8.1.RC1 CANN 包**后使用轻量化数据解析功能。

> 原文未给出具体的端到端性能数字（如采集耗时下降百分比、内存占用绝对值等），仅提供"db 格式减少约 70% 磁盘空间"这一条量化数据。

---

## 【表格解读】

原文「主要配置参数说明」表格逐字还原如下：

| 参数 | 说明 | 可选值 |
|------|------|--------|
| profile | 性能分析开关 | true/false，默认值false，所有性能数据采集均依赖该开关开启 |
| mstx | 轻量化打点采集开关 | true/false，默认值false，启用/关闭轻量化打点采集，需要查看轻量化打点性能数据时需开启 |
| stage | 性能数据采集阶段 | 可选参数包括all(采集所有阶段性能数据)、actor_generate(采集actor模型生成阶段性能数据)、actor_compute_log_prob(采集actor模型计算log概率阶段性能数据)、reference_compute_log_prob(采集reference参考模型计算log概率阶段性能数据)、critic_compute_values(采集critic模型计算values阶段性能数据)、actor_update(采集模型更新阶段性能数据)、critic_update(采集模型更新阶段性能数据)；stage参数支持列表传参，一次性采集多个stage；stage参数默认值为all |
| profile_save_path | 性能数据输出目录 | 任意有效路径，默认为"./profiler_data" |
| profile_export_type | 导出格式 | text、db(性能数据交付件为db格式，可减少约70%磁盘空间)，默认值text |
| profile_step_start | 开启采集数据的步骤 | 任意正整数，默认为1，profile_step_start从1开始 |
| profile_step_end | 结束采集数据的步骤 | 任意正整数，默认为2，实际采集步数为 profile_step_end - profile_step_start，不包含profile_step_end |
| profile_level | 采集级别 | level_none、level0、level1、level2，默认值level0 |
| profile_with_memory | 内存分析开关 | true/false，默认值false，启用/关闭内存分析 |
| profile_record_shapes | 张量形状记录开关 | true/false，默认值false，是否记录张量形状 |
| profile_with_cpu | Host侧性能数据开关 | true/false，默认值true，是否包含Host侧性能数据 |
| profile_with_npu | Device侧性能数据开关 | true/false，默认值true，是否包含NPU侧性能数据 |
| profile_with_module | Python调用栈信息开关 | true/false，默认值false，是否包含Python侧调用栈信息 |
| profile_analysis | 自动解析开关 | true/false，默认值false，是否在采集后自动解析数据 |
| profile_ranks | 采集数据的卡号 | all表示所有rank，默认值all，可以通过列表指定，如[0, 1] |

**逐行解读**：

- **profile**：所有采集行为的总入口；`false` 时其它参数实际不起作用。
- **mstx**：与 `profile_level: level_none` 配合形成轻量化采集；采集对象是「打点」而非完整算子 timeline。
- **stage**：覆盖 RL 训练的核心流水线节点；其中 `actor_update` 与 `critic_update` 在原文中都被标注为"采集模型更新阶段性能数据"，可结合多 worker 流程理解。**PPO 场景不允许 all**。
- **profile_export_type**：db 格式是**交付件**形式，适合大规模数据归档与传输；text 适合直接人眼阅读。
- **profile_step_start / profile_step_end**：默认 `1→2` 即采集单步；半开区间意味着想采集第 N 步需设 `start=N, end=N+1`。
- **profile_level**：4 级粒度，配合 mstx 使用时通常选 `level_none`。
- **profile_with_memory / profile_record_shapes**：会显著放大数据量，按需开启。
- **profile_with_cpu / profile_with_npu**：默认都开；纯 mstx 模式建议关 cpu。
- **profile_with_module**：开关 Python 侧调用栈，对定位上层瓶颈有意义但开销更大。
- **profile_ranks**：通过 `[0, 1]` 列表裁剪目标 rank，是减少数据量的关键开关之一（与「最佳实践」第 3 条呼应）。

---

## 【公式解读】

原文未提供 LaTeX 形式的数学公式，仅有如下类公式/算式表达，逐字保留并解释：

| 原式 | 含义 |
|------|------|
| `profile_step_end - profile_step_start` | integrated 共卡模式下实际采集步数，**半开区间，不包含 profile_step_end** |
| `profile_step_end - profile_step_start + 1` | DPO 场景下的实际采集步数（含多 warmup 的 1 步修正） |
| `sampling_config.max_tokens <= 128` | 性能调优经验建议：减少单条 response 的最大生成 token 数（用于减小训练参数规模） |
| `megatron_training.global_batch_size <= 8` | 性能调优经验建议：全局 batch 不超过 8（适用于阶段级分析） |
| `megatron_training.global_batch_size <= 4` | 性能调优经验建议：按阶段分段采集时 batch 不超过 4，避免性能数据过大 |
| `db 格式可减少约70%磁盘空间` | 量化收益：db 格式相对 text 格式的磁盘占用比 |

> 注：上述 6 项均为文档中的算式/数值描述，**不是**严格数学公式；这里采用「逐字保留原式」方式呈现。

---

## 【关联】

- **算法层关联**：文档在两处直接关联算法——
  1. **GRPO**："GRPO 算法涉及多个 worker 模块交互，包含训练、推理等流程" → 是文档默认适配场景，`stage` 的 7 个枚举值对应 GRPO 的多 worker 流水线；
  2. **DPO（直接偏好对齐）**：有独立的精简配置样例，且明确标注「其他未罗列的参数目前对应功能都未支持」。
- **场景层关联**：
  - **PPO**：「PPO 场景单卡多进程特性」导致 `stage` 不能为 `all`，需手动指定；
  - **integrated（共卡模式）**：所有 profiling 采集的唯一支持场景。
- **下游工具关联**：
  - **MindStudio Insight**：可视化层配套工具，提供 timeline、算子、通信三类视图；
  - **CANN 8.1.RC1 包**：轻量化数据解析功能的运行时依赖；
  - **`torch_npu`**：底层 profiling API 载体（`torch_npu.profiler.profiler.analyse`、`torch_npu.npu.mstx.range_start/end`）。
- **代码层关联**：
  - `mindspeed_rl.utils.utils.mstx_timer_decorator` — 装饰器形式自定义打点 API；
  - 关键函数 `dispatch_transfer_dock_data`、`resharding` — 已内置 mstx 自定义打点。
- **内部链接信息**：原文未提供任何站内/文内跳转链接，仅给出一个外部链接 `https://www.hiascend.com/document/detail/zh/mindstudio/80RC1/index/index.html`（MindStudio 文档）。

---

## 【使用方法】

**1. integrated 共卡模式（完整配置示例，原文）：**

```yaml
profiler_config:
  integrated:
    profile: false
    mstx: false
    stage: all
    profile_save_path: ./profiler_data
    profile_export_type: text
    profile_step_start: 1
    profile_step_end: 2
    profile_level: level1
    profile_with_memory: false
    profile_record_shapes: false
    profile_with_cpu: true
    profile_with_npu: true
    profile_with_module: false
    profile_analysis: false
    profile_ranks: all
```

**2. DPO 算法配置示例（原文）：**

```yaml
profiler_config:
  integrated:
    profile: true
    profile_save_path: ./profiler_data
    profile_export_type: text
    profile_step_start: 1
    profile_step_end: 2
    profile_level: level1
    profile_with_memory: false
    profile_record_shapes: false
    profile_with_cpu: true
    profile_ranks: all
```
> 注意：DPO 场景仅罗列的参数被支持；采集会多 warmup 1 步，实际采集步数 = `profile_step_end - profile_step_start + 1`。

**3. 轻量化采集模式（原文）：**

```yaml
profile: true
mstx: true
profile_level: level_none
profile_with_cpu: false
profile_with_npu: true
```

**4. 自定义打点接入（两种方式，原文）：**

```python
# 方式一：装饰器
from mindspeed_rl.utils.utils import mstx_timer_decorator

@mstx_timer_decorator
def your_function():
    pass

# 方式二：range 框选
import torch_npu

id = torch_npu.npu.mstx.range_start("your_tag_name")
result = complex_operation()
torch_npu.npu.mstx.range_end(id)
```

**5. 性能数据解析（两种方式，原文）：**

```python
# 离线解析（推荐大规模集群，支持多份数据并行）
import torch_npu
torch_npu.profiler.profiler.analyse(profiler_path="./profiler_data")

# 在线解析：在 YAML 中设 profile_analysis: true
```

**6. 最佳实践路径（原文三步）：**
1. 从轻量级分析（mstx 模式）开始识别训练的瓶颈模块；
2. 使用特定阶段分析聚焦于问题区域；
3. 分析特定 rank 而非所有 rank，以减少数据量。

**7. 环境前置条件（原文）：** 需更新至最新 **8.1.RC1 CANN 包**后方可使用轻量化数据解析功能。

> 原文未涉及：CLI/命令行启动方式、容器内挂载目录建议、与 `torchrun`/`msrun` 启动命令的耦合方式、跨节点时间戳对齐方法。
