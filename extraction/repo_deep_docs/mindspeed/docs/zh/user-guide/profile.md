# MindSpeed 中采集Profile数据

> 仓 `mindspeed` · 路径 `docs/zh/user-guide/profile.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/user-guide/profile.md

# MindSpeed Profile 采集文档深度解读

---

## 【定位】
这篇文档解决的是 **MindSpeed 框架下如何通过命令行方式按需开启性能 Profile（性能画像）采集** 的问题——即在大模型训练任务中，用户只需追加若干 `--profile-*` 命令行参数，即可控制采集开关、采集步范围、采集等级、附加信息维度、保存路径以及目标 rank，无需修改代码即可输出 profiling 数据。

---

## 【技术要点】

1. **命令式开启机制**：以 `--profile` 作为总开关，关闭（默认）时不产生任何采集开销，开启后才会有后续参数生效。
2. **采集步窗口控制**：`--profile-step-start` 与 `--profile-step-end` 限定采集发生在训练的第 N 步到第 M 步之间，默认窗口为 10→12（即训练第 10 至 12 步进行采集）。
3. **三级采集粒度**：`--profile-level` 提供 `level0 / level1 / level2` 三个等级，默认 `level0`，等级越高采集信息越详细。
4. **四类附加维度开关**：`--profile-with-cpu`（CPU 信息）、`--profile-with-stack`（调用栈）、`--profile-with-memory`（显存，需联动 `--profile-with-cpu`）、`--profile-record-shapes`（张量 shapes）。
5. **保存路径可配**：`--profile-save-path` 指定落盘目录，默认 `./profile_dir`。
6. **Rank 维度筛选**：`--profile-ranks` 用于选择采集哪些 rank 的 profiling 数据，默认 `-1` 表示采集全部 rank；显式指定时传入的是 **单机/集群内的全局 rank 值**，而非本地 rank。

---

## 【关键机制与数据】

- **工作机制（原文）**：文档明确指出 MindSpeed "支持命令式开启 Profile 采集数据"，整套能力通过命令行参数驱动，不涉及代码层 API。
- **默认值（原文）**：`--profile-step-start` 默认 10；`--profile-step-end` 默认 12；`--profile-level` 默认 `level0`；`--profile-save-path` 默认 `./profile_dir`；`--profile-ranks` 默认 `-1`（采集所有 rank 的 profiling 数据）。
- **联动约束（原文）**：`--profile-with-memory` 开启时必须同时打开 `--profile-with-cpu`。
- **Rank 语义（原文）**：`--profile-ranks` 的配置值是"每个 rank 在单机/集群中的全局值"。
- **数据流**：原文未提供 profile 数据的具体流转路径、采样周期、落盘格式或与昇腾 `msprof` / `torch_npu` profiler 的对接细节。
- **性能数据**：原文未给出任何性能开销、采集耗时或对比基准数据。

---

## 【表格解读】

### 原文表格：Profile 命令配置项一览

| 配置命令                    | 命令含义                                                                                                    |
|-------------------------|---------------------------------------------------------------------------------------------------------|
| --profile               | 打开profile开关                                                                                             |
| --profile-step-start    | 配置开始采集步，未配置时默认为10，配置举例：--profile-step-start 30                                                        |
| --profile-step-end      | 配置结束采集步，未配置时默认为12，配置举例：--profile-step-end 35                                                          |
| --profile-level         | 配置采集等级，未配置时默认为level0，可选配置：level0，level1，level2，配置举例：--profile-level level1                        |
| --profile-with-cpu      | 打开CPU信息采集开关                                                                                             |
| --profile-with-stack    | 打开stack信息采集开关                                                                                           |
| --profile-with-memory   | 打开memory信息采集开关，配置本开关时需打开--profile-with-cpu                                                              |
| --profile-record-shapes | 打开shapes信息采集开关                                                                                          |
| --profile-save-path     | 配置采集信息保存路径，未配置时默认为./profile_dir，配置举例：--profile-save-path ./result_dir                                |
| --profile-ranks         | 配置待采集的ranks，未配置时默认为-1，表示采集所有rank的profiling数据，配置举例：--profile-ranks 0 1 2 3，需注意：该配置值为每个rank在单机/集群中的全局值 |

### 逐行解读

| 行  | 配置项                | 类别           | 解读 |
|-----|---------------------|--------------|------|
| 1   | `--profile`         | 总开关          | 整组 profile 采集的主开关；未指定时所有采集逻辑不触发。 |
| 2   | `--profile-step-start` | 采集步窗口（起点）  | 控制从第几步开始采集；默认 10；示例值 30 表示从第 30 步开始。 |
| 3   | `--profile-step-end` | 采集步窗口（终点）  | 控制到第几步结束采集；默认 12；示例值 35 表示到第 35 步结束；与起点参数共同构成采集窗口。 |
| 4   | `--profile-level`   | 采集粒度         | 三档：`level0 / level1 / level2`；默认 `level0`；示例配置为 `level1`，级别越高采集内容越细（具体差异原文未展开）。 |
| 5   | `--profile-with-cpu`     | 附加维度 | 开启 CPU 侧信息的采集；独立开关。 |
| 6   | `--profile-with-stack`   | 附加维度 | 开启调用栈（stack）信息的采集；用于定位热点代码路径。 |
| 7   | `--profile-with-memory`  | 附加维度 | 开启内存/显存信息的采集；**有联动约束**——必须同时打开 `--profile-with-cpu`。 |
| 8   | `--profile-record-shapes` | 附加维度 | 开启算子输入/输出张量 shapes 的采集；用于分析张量规模与算子耗时关系。 |
| 9   | `--profile-save-path` | 输出路径         | 采集结果落盘目录；默认 `./profile_dir`；示例为 `./result_dir`。 |
| 10  | `--profile-ranks`   | 目标 rank 选择 | 多值参数，指定要采集的 rank 列表；默认 `-1` 表示采集全部；示例 `0 1 2 3` 表示采集全局 rank 0~3；**参数语义为全局 rank**，分布式场景下需按全局编号传入。 |

---

## 【公式解读】

原文无公式。

---

## 【关联】

- 文末标注"内部链接: (无)"，即该文档未显式提供与其他文档的交叉链接。
- 从命令体系推断的关联关系（基于原文表述，未做外推）：
  - 与**训练启动入口**关联：上述参数均为命令行形式，预期作为训练启动命令的附加参数传入，作用于训练脚本入口。
  - 与**分布式训练 rank 体系**关联：`--profile-ranks` 涉及"单机/集群中的全局值"，表明该能力作用于分布式训练场景，与 rank 编号体系耦合。
  - 与**多档采集粒度**关联：`--profile-level` 的 `level0/1/2` 三档暗示 MindSpeed 内部存在分级化的 profiling 实现细节（具体各级差异原文未说明）。
  - 其余上下游模块（如与昇腾 `msprof`、`torch_npu` profiler 的对接细节，与性能调优工具链的衔接等）原文均未涉及。

---

## 【使用方法】

**最小化用法（原文）**：在训练命令中追加 `--profile` 即可打开 profile 采集，使用默认 step 窗口（10→12）、默认 level（level0）、默认保存路径（`./profile_dir`）、默认采集全部 rank。

**典型组合示例（基于原文命令含义还原）**：

1. 自定义采集步窗口与等级：
   ```
   --profile --profile-step-start 30 --profile-step-end 35 --profile-level level1
   ```
2. 开启 CPU、stack、memory、shapes 全维度采集（注意 memory 需联动 cpu）：
   ```
   --profile --profile-with-cpu --profile-with-stack --profile-with-memory --profile-record-shapes
   ```
3. 自定义保存路径：
   ```
   --profile --profile-save-path ./result_dir
   ```
4. 仅采集指定全局 rank：
   ```
   --profile --profile-ranks 0 1 2 3
   ```

**注意事项（原文）**：
- `--profile-with-memory` 必须与 `--profile-with-cpu` 同时开启。
- `--profile-ranks` 传入的是**全局 rank** 编号，需按单机或集群中 rank 的全局序号指定，而非本地 rank。
