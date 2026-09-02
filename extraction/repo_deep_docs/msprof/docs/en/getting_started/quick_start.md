# Quick Start

> 仓 `msprof` · 路径 `docs/en/getting_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprof/docs/en/getting_started/quick_start.md

# msProf Quick Start 文档深度解读

## 【定位】

这篇文档是 msProf（昇腾 AI 处理器性能分析工具）的快速上手指南，面向首次接触 msProf 的用户，帮助其在最短路径内完成**环境搭建 → profile 数据采集 → 性能瓶颈分析**的完整闭环，是使用 msProf 进行模型调优/性能调优的入口文档。

---

## 【技术要点】

1. **环境依赖**：需安装 **CANN Toolkit 与 ops operator 包**；通过 `source ${install_path}/set_env.sh`（如 `/usr/local/Ascend/ascend-toolkit`）加载环境变量；用 `which msprof` 和 `msprof --help` 验证安装。
2. **核心采集命令**：
   ```bash
   msprof --application="python train.py" --output=/home/prof_output
   ```
   - `--application`：待采集的用户应用。
   - `--output`：profile 数据落盘路径。
3. **采集产物结构**：在 `--output` 下生成 `PROF_XXX` 目录，内含 `host/data`（主机原始数据）、`device_{id}/data`（设备原始数据）、`msprof_{timestamp}.db`（数据库格式）、以及 `mindstudio_profiler_output/`（汇总目录，内含 `msprof_{timestamp}.json` 时间线数据与 `op_summary_{timestamp}.csv` 算子数据）。
4. **执行成功标识**：终端依次输出 `[INFO] Start profiling` → `[INFO] Start export data` → `[INFO] Export all data ... done` → `[INFO] Start query data` → `[INFO] Profiling finished` 五阶段日志，并以 `PROF_000001_<timestamp>_<hash>` 命名落盘。
5. **可视化与分析工具**：使用 **MindStudio Insight** 加载 `PROF_XXX` 文件夹进行时间线分析；时间线划分三层——CANN 层 API/算子时长、底层 NPU 任务流/AICore 数据、算子与 API 明细区。
6. **两类 CSV 汇总分析**：
   - `op_statistic_*.csv`：按 **Op Type** 聚合，提供 **Total Time** 与调用次数，用于定位耗时最长的算子类型。
   - `op_summary_*.csv`：单算子粒度，记录输入/输出 shape、**PMU 数据** 与 **Task Duration**；支持按 **Task Duration** 或 **Task Type**（AI Core / AICPU）排序。

---

## 【关键机制与数据】

**采集-解析-导出工作流（原文逐字日志佐证）**：
```
[INFO] Start profiling....        → 采集启动
[INFO] Using device: npu:0       → 自动识别昇腾 NPU 设备 0
[Epoch 1/2] Average Loss: 2.4961 → 训练侧反馈（与 ResNet-50 示例脚本对应）
[Epoch 2/2] Average Loss: 2.2166
[INFO] Start export data in PROF_000001_...  → 导出阶段
[INFO] Start query data in PROF_000001_...   → 检索/索引阶段
Job Info        ...    Rank ID   → 输出元信息表（host + device_0 两行）
[INFO] Profiling finished.                  → 流程结束
```
（原文：采集过程产生"采集 → 导出 → 检索 → 完成"四阶段流水线，最终目录命名遵循 `PROF_<序列号>_<时间戳>_<哈希>` 规则，如示例 `PROF_000001_20260323031749197_00815596RKPKAHRB`）

**时间线三层视图机制（原文 Figure 1）**：
- **Area 1 — CANN 层**：展示 Runtime 等组件与算子节点的执行时长。
- **Area 2 — 底层 NPU 层**：展示 **Ascend Hardware** 下任务流（Task Stream）的执行时长、迭代轨迹（Iteration Trace），以及 Ascend AI Processor 系统数据；通过 **HostToDevice** 连线呈现下发关系。
- **Area 3 — 算子/API 明细层**：点击时间线上的彩色块即可查看每个算子/API 调用的详细参数。

**API 状态**：无内部链接。

---

## 【表格解读】

原文 CLI 输出中包含一张 **Job Info 元信息表**（采集成功后自动打印），逐字还原如下：

| Job Info | Device ID | Dir Name | Collection Time | Model ID | Iteration Number | Top Time Iteration | Rank ID |
|---|---|---|---|---|---|---|---|
| NA | *(空)* | host | 2026-03-23 03:17:50.944273 | N/A | N/A | N/A | -1 |
| NA | 0 | device_0 | 2026-03-23 03:17:50.954390 | N/A | N/A | N/A | -1 |

**逐行解读**：
- **表头**：`Job Info`（作业信息标识）、`Device ID`（设备编号）、`Dir Name`（数据目录名）、`Collection Time`（采集时间，精度到微秒）、`Model ID`（模型标识）、`Iteration Number`（迭代次数）、`Top Time Iteration`（耗时最长迭代）、`Rank ID`（分布式 Rank 编号，-1 表示非分布式/单机）。
- **第 1 行（host）**：`Device ID` 留空、`Dir Name=host`、`Collection Time=2026-03-23 03:17:50.944273`，记录 **Host 侧** profile 数据的采集时刻；模型/迭代字段为 `N/A`（host 维度无此信息）；`Rank ID=-1`。
- **第 2 行（device_0）**：`Device ID=0`、`Dir Name=device_0`、`Collection Time=2026-03-23 03:17:50.954390`（比 host 晚约 10 微秒，符合"先 host 启动 → 后续 device 数据落盘"的时序逻辑），记录 **NPU 0 设备侧** 的采集时刻。

> 备注：本表所列数据（时间戳、Iteration、Rank ID 等）原文均为示例演示值（N/A 或 -1），并不代表真实业务负载。原文还通过 Figure 2、Figure 3 分别给出 `op_statistic_*.csv` 与 `op_summary_*.csv` 的截图示例，但未提供具体字段数值，因此不另行建表还原。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档原文标注 **(无) 内部链接**，但其文档体系内存在的**外部依赖/跳转**如下（保留原文链接以便建立认知地图）：

| 关联对象 | 类型 | 原文角色 |
|---|---|---|
| **CANN 软件安装指南** | 上游依赖 | 安装 CANN Toolkit + ops 算子包的官方指引，msProf 运行的底层依赖 |
| **Profile Data Collection（采集进阶文档）** | 同模块扩展 | 文档明确指出："上述命令是基础采集命令，其他采集需求请参见此文档"，承担**采集参数高级用法**的角色 |
| **MindStudio Insight（msinsight）** | 下游可视化工具 | 加载 `PROF_XXX` 目录进行时间线分析的 GUI 工具；原文建议使用其完成 API/算子/任务流定位及 HostToDevice 下发关系分析 |
| **ResNet-50 Model Training Sample** | 同文档附录 | 提供 `--application="python train.py"` 中的 `train.py` 真实样例；含设备自动选择（NPU > CUDA > CPU）、ResNet50 IMAGENET1K_V1 预训练权重加载、可选 backbone 冻结、Adam 优化器、CrossEntropyLoss、2 epoch 训练（示例 Loss: 2.4961 → 2.2166）等完整工程要素 |

逻辑链路：**CANN 运行环境** → **msProf 采集（Quick Start）** → **PROF_XXX 数据产物** → **MindStudio Insight 可视化 / CSV 汇总分析** → **Performance Profiling 调优决策**。

---

## 【使用方法】

原文涉及的启用方式/配置项/命令如下：

**1. 环境生效**
```bash
source ${install_path}/set_env.sh   # ${install_path} 示例：/usr/local/Ascend/ascend-toolkit
```

**2. 安装自检**
```bash
which msprof
msprof --help
```

**3. 基础采集命令**
```bash
msprof --application="python train.py" --output=/home/prof_output
```
| 参数 | 含义 |
|---|---|
| `--application` | 待采集的用户应用（命令行字符串） |
| `--output` | profile 数据输出目录 |

**4. 附录示例脚本入口**
```python
# 文件名：train.py（即 --application 参数指向的目标）
train()  →  trainer = ResNet50(num_classes=10)
          →  DataLoader(batch_size=8, shuffle=True)
          →  trainer.train(loader, epochs=2, lr=1e-3, freeze_backbone=True)
```
关键训练超参（原文明确给出）：`epochs=2`、`lr=1e-3`、`freeze_backbone=True`、`num_classes=10`、`batch_size=8`。

**5. 可视化分析**
- 使用 MindStudio Insight 加载 `PROF_XXX` 文件夹。
- 排序策略：在 `op_statistic_*.csv` 中按 **Total Time** 降序定位耗时算子类型；在 `op_summary_*.csv` 中按 **Task Duration** 定位耗时算子、按 **Task Type** 区分 **AI Core / AICPU** 耗时分布。

> 关于性能调优或更多采集模式（如指定采集范围、采样率等），原文明确指引跳转至《Profile Data Collection》文档，**Quick Start 本体不展开**。

## 图文联合解读

- `en-us_image_0000002502558722.png`: **图文解读：**

**图示内容：** msProf的Timeline时间线视图，分三区呈现。①Area 1（主机侧）：CANN轨道下CPU多线程（809060/809566等）执行AscendCL算子调用（如aclnnInplaceRelu、aclnnMaxPool2dWithMaskGetWorkspaceSize）；②Area 2（设备侧）：Ascend Hardware轨道下NPU Stream 46/49上acl任务执行；③Area 3：Slice Detail面板显示选中算子的精确时戳、Wall Duration（14μs800ns）、Task Type（AI_VECTOR_CORE）等元数据。曲线箭头关联主机Node@launch与设备acl任务，体现调度关系。

**技术结论：** msProf能同时捕获Host-Device双侧时序，精准刻画算子下发与执行的因果链，为性能瓶颈定位提供微观数据。

**文档关联：** 对应Quick Start第三步"Analysis"，示范如何借助Timeline可视化与切片详情进行初始性能分析。
- `en-us_image_0000002534398593.png`: **图文联合解读：**

1）图里画了什么：一张算子级性能剖析表格，包含 Device id、OP Type、Core Type、Count、Total/Min/Avg/Max Time(us) 及 Ratio(%) 等列，按耗时占比降序展示；数据来源于 ResNet-50 训练任务的 msProf 采集结果，主要算子包括 TransData(39.451%)、Conv2D(22.44%)、BatchNormV3(21.886%)、Relu(6.052%)、Add(4.957%) 等，执行核以 AI_VECTOR_CORE 为主。

2）论证了什么：TransData、Conv2D、BatchNormV3 三类算子累计占比超 83%，是训练耗时热点；MaxPool3DWithArgmaxV2 单次平均耗时 121.605μs，存在明显长尾；MIX_AIV 算子总耗时相对较低，AI_VECTOR_CORE 算子是性能瓶颈主要所在。

3）与文档关系：作为"Quick Start"第三步"分析"环节的示例输出，印证了"通过 msProf 采集后可基于结果文件定位性能瓶颈"这一论点，为初学者展示典型的瓶颈识别方法。
- `en-us_image_0000002502718556.png`: **图示解读：**

1. **画面内容**：图为 msProf 工具生成的算子级 Profile 数据表格（CSV/Excel 视图），列涵盖 Device_id、Model_ID、Op Name（trans_TransData、Conv2D、aiclnAddsAdd 等）、Op Type、Task Type、Task Start/Duration、Input/Output Shape（如 NCHW、NCDHW）、DataType、Format、Context 等指标，多行算子以时间戳呈现执行轨迹。

2. **技术结论**：msProf 可针对每个算子生成结构化的运行时元数据（含形状、数据类型、耗时、阻塞等待等），支持精细化性能溯源。

3. **与文档关系**：作为 Quick Start「Analysis」步骤的可视化示例，直观展示 `msprof --application` 执行后可解析输出的字段结构与算子粒度，呼应"基于结果文件定位瓶颈"的论点。
