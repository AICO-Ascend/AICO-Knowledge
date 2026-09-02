# 训练开发工具链快速入门

> 仓 `mstt` · 路径 `docs/zh/quick_start/mstt_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mstt/docs/zh/quick_start/mstt_quick_start.md

# mstt 训练开发工具链快速入门 · 一体化深度解读

---

## 【定位】

本文档是 **msTT（MindStudio Training Tools）训练开发工具链的总览式快速入门**，面向昇腾 AI 训练开发场景，按"精度 / 性能 / 监控 / 迁移"四大环节汇总各子工具的功能定位与快速入门入口索引，帮助开发者依据当前开发阶段和业务需求，**快速定位并上手相应工具**。

---

## 【技术要点】

msTT 围绕训练开发的四大关键阶段提供能力覆盖：

1. **精度调试**：支持 **全场景精度采集** 与 **分级对比分析**，结合可视化手段定位精度偏差根因（对应工具：`msProbe`、`TensorBoard`）。
2. **性能调优**：覆盖 **数据采集、瓶颈分析、可视化诊断、内存调优、性能剖析**，提供从 **单算子到集群** 的多层级性能优化手段（对应工具：`msProf`、`msprof-analyze`、`msMemScope`、`msInsight`、`msPTI`）。
3. **在线监控**：面向 **集群的实时性能监控与故障定位**，同时支持 **落盘与在线采集** 两种模式，保障训练任务稳定运行（对应工具：`msMonitor`）。
4. **脚本迁移**：提供 **PyTorch 训练脚本的 NPU 兼容性分析与适配能力**，支持 **少量改码或零改码** 完成从 GPU 到昇腾 NPU 的迁移（对应工具：`msTransplant`）。

---

## 【关键机制与数据】

原文为工具链总览文档，未涉及具体的工作原理、采集数据流图、性能基准数字或采样率/吞吐参数等量化指标，仅给出工具能力描述与外部分发仓链接，无可标注的"原文数据"。**原文无具体性能数据 / 工作机制细节**。

---

## 【表格解读】

原文包含一张核心工具清单表（第 2 节），逐字还原如下：

| 类别 | 工具名称 | 功能简介 | 快速入门链接 |
|:--:|:----------------------|:---------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------:|
| 精度 | **msProbe** | **【精度调试】** 昇腾全场景精度工具，用于训练精度调试与问题定位。 | [点击查看](https://gitcode.com/Ascend/msprobe/blob/master/docs/zh/quick_start/pytorch_quick_start.md) |
| 精度 | **TensorBoard** | **【分级可视】** 分级展示模型结构与精度，支持调试与标杆模型对比以定位精度问题。 | [点击查看](https://gitcode.com/Ascend/msprobe/blob/master/docs/zh/quick_start/pytorch_quick_start.md) |
| 性能 | **msProf** | **【模型调优】** 全场景性能调优底座，采集 CANN 与 NPU 数据，提升设备调优效率。 | [点击查看](https://gitcode.com/Ascend/msprof/blob/master/docs/zh/quick_start/msprof_quick_start.md) |
| 性能 | **msprof-analyze** | **【性能分析】** 基于采集数据做性能分析，快速识别性能瓶颈。 | [点击查看](https://gitcode.com/Ascend/msprof-analyze/blob/master/docs/zh/quick_start/msprof-analyze_quick_start.md) |
| 性能 | **msMemScope** | **【内存调优】** 内存调优专用工具：整网级多维度内存采集，支持自动诊断与优化分析。 | [点击查看](https://gitcode.com/Ascend/msmemscope/blob/master/docs/zh/quick_start/quick_start.md) |
| 性能 | **msInsight** | **【可视调优】** 可视化性能分析，覆盖系统、算子、服务化等场景，辅助完成性能诊断。 | [点击查看](https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/quick_start/system_tuning_quick_start.md) |
| 性能 | **msPTI** | **【性能剖析】** 面向昇腾的 Profiling API，可据此开发 NPU 应用性能分析工具。 | [点击查看](https://gitcode.com/Ascend/mspti/blob/master/docs/zh/quick_start/mspti_quick_start.md) |
| 监控 | **msMonitor** | **【在线监控】** 一站式监控，支持落盘与在线采集，面向集群的监测与问题定位。 | [点击查看](https://gitcode.com/Ascend/msmonitor/blob/master/docs/zh/quick_start/msmonitor_quick_start.md) |
| 迁移 | **msTransplant** | **【分析迁移】** PyTorch 训练脚本一键迁移至昇腾 NPU，支持少量改码或零改码完成迁移。 | [点击查看](../../../msfmktransplt/README.md#快速入门) |

**逐行解读**：

- **第 1 行 · msProbe（精度）**：定位为"昇腾全场景精度工具"，承担训练精度调试与问题定位的入口职责；快速入门链接指向 msprobe 仓的 `pytorch_quick_start.md`。
- **第 2 行 · TensorBoard（精度）**：定位为"分级可视化"，除精度展示外还强调 **与标杆模型对比**，用于精度问题定位；该行的链接复用 msProbe 的文档，体现两者在精度场景下的协同关系。
- **第 3 行 · msProf（性能）**：作为"**全场景性能调优底座**"，明确 **采集 CANN 与 NPU 数据**，是其他性能分析工具的数据上游。
- **第 4 行 · msprof-analyze（性能）**：明确依赖 msProf 的采集数据进行 **性能瓶颈识别**，是 msProf 的下游分析组件。
- **第 5 行 · msMemScope（性能）**：聚焦 **内存调优**，覆盖 **整网级多维度** 内存采集并带 **自动诊断** 能力，是性能链路的专用内存分支。
- **第 6 行 · msInsight（性能）**：提供 **可视化** 性能分析，覆盖 **系统 / 算子 / 服务化** 三类场景，是面向"诊断结果展示"的可视化层。
- **第 7 行 · msPTI（性能）**：定位为 **Profiling API** 而非应用层工具，开发者可基于它开发 NPU 应用性能分析工具，体现"SDK 底座"性质。
- **第 8 行 · msMonitor（监控）**：唯一属于"监控"类的工具，强调 **落盘 + 在线** 双采集模式和 **集群级** 故障定位，与"性能调优"环节（多为离线分析）形成对比。
- **第 9 行 · msTransplant（迁移）**：唯一属于"迁移"类的工具，明确 **PyTorch → 昇腾 NPU** 方向，支持 **少量改码或零改码**；链接为相对路径 `../../../msfmktransplt/README.md#快速入门`，说明该工具的文档 **内嵌于本仓库** 而非外挂到 gitcode，是表中唯一的内部链接。

**表格结构性观察**：表中共 **9 行 4 列**，覆盖"精度 2 / 性能 5 / 监控 1 / 迁移 1"的结构分布，与第 1.2 节"四大核心能力"完全对应；外链全部为 gitcode.com/Ascend/ 域下的子仓，唯独 msTransplant 的链接指向仓库内路径，提示该工具与其他 8 个工具的发布/文档组织方式存在差异。

---

## 【公式解读】

原文无公式（LaTeX 或伪代码形式均未出现）。

**原文无公式**。

---

## 【关联】

本文档作为 mstt 工具链的"目录页/入口页"，与下游各子工具的快速入门文档形成 **一对多** 的扇出关系：

- **msProbe / TensorBoard（精度）** → 都指向 `https://gitcode.com/Ascend/msprobe/blob/master/docs/zh/quick_start/pytorch_quick_start.md`，两者在精度调试场景中 **共享同一份入门文档**，提示 TensorBoard 的精度可视化能力集成在 msProbe 中。
- **msProf（性能底座）** → 是 `msprof-analyze` 的数据上游："采集 CANN 与 NPU 数据" → "基于采集数据做性能分析"，形成 **采集 → 分析** 的两段式流水线。
- **msMemScope / msInsight / msPTI（性能分支）** → 与 msProf + msprof-analyze 共同构成 **多维度性能工具矩阵**（内存、可视化、Profiling API），并列服务于"性能调优"核心能力。
- **msMonitor（监控）** → 与性能调优链路并行，强调 **集群级实时性** 与 **落盘/在线双采集**，是覆盖训练任务"稳定运行"维度的工具。
- **msTransplant（迁移）** → 与所有其他 8 个工具的"已运行训练任务调优"定位形成互补，专注 **GPU → 昇腾 NPU** 的脚本适配场景。
- **内部链接 `../../../msfmktransplt/README.md#快速入门`** → 表明 msTransplant 的详细文档以 **仓库内相对路径** 形式嵌入本仓库的 `msfmktransplt` 目录，与其他外挂到 gitcode 的子仓文档的组织方式不同；这是文末唯一被显式标注的内部链接。

---

## 【使用方法】

原文作为**索引型总览文档**，未给出具体的命令、配置项、CLI 调用或 API 用法。其所提供"启用方式"即 **第 2 节表格中的"快速入门链接"列**：用户根据"精度 / 性能 / 监控 / 迁移"四类需求，在表格中选择对应工具，点击链接跳转至各子工具的快速入门文档完成上手。

各工具的具体启动命令、环境变量、配置参数、采集开关等均未在本文档中给出，需跳转至对应子工具文档获取 —— **原文未涉及具体命令/配置项**。
