# msTT Quick Start in MindSpore Scenarios

> 仓 `mstt` · 路径 `docs/en/quick_start/mindspore_mstt_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mstt/docs/en/quick_start/mindspore_mstt_quick_start.md

# msTT Quick Start in MindSpore Scenarios — 一体化深度解读

---

## 【定位】

这篇文档是 msTT 工具链在 **MindSpore 训练场景**下的快速入门指南,围绕「模型开发与迁移 → 模型精度调试 → 模型性能调优」三条主线,系统介绍 **msProbe（精度调试）、MindSpore Profiler（性能采集）、msprof-analyze（性能分析）、MindStudio Insight（性能可视化）** 四款工具的使用流程、API 插入点与命令,帮助用户在 Ascend NPU 环境下对训练脚本进行端到端的精度定界与性能调优。

---

## 【技术要点】

1. **工具链构成**：精度侧 msProbe（`mindstudio-probe` 包）→ 性能采集 MindSpore Profiler API → 性能分析 msprof-analyze → 性能可视化 MindStudio Insight；覆盖「采-比-析-看」全链路。

2. **支持的 MindSpore 版本示例**：原文以 **MindSpore 2.7.2 与 2.8.0** 作为同环境跨版本精度对比的两个样本（"examples"），并以此说明预期产生的差异项。

3. **训练脚本入口约定**：以 `mindspore_main.py` 作为训练脚本文件名，上传至训练服务器任意可读写目录后通过 `python mindspore_main.py` 直接执行，结束日志为 `train finish`。

4. **msProbe 安装命令**：`pip install mindstudio-probe --pre`，需在 Ascend NPU 环境中执行。

5. **预训练配置检查的两段式 API 注入**：
   - 在训练进程**第一个 Python 脚本开头**插入 `from msprobe.core.config_check import ConfigChecker; ConfigChecker.apply_patches(fmk)`；
   - 在**模型初始化之后**插入 `ConfigChecker(model=model, output_zip_path="", fmk="")`。
   - 关键参数 `fmk` 取字符串 `"mindspore"`（另可选 `"pytorch"`）；`output_zip_path` 默认 `"./config_check_pack.zip"`，必须显式指定 zip 包名。

6. **配置比对命令**：`msprobe config_check -c bench_zip_path cmp_zip_path -o output_path`；`output_path` 默认 `"./config_check_result"`，运行后产出三件套：`bench/`（基准侧数据）、`cmp/`（待比对侧数据）、`result.xlsx`（汇总 + 明细多 sheet，`step` 维度为 `micro_step`）。

7. **精度检查五项必过项**：environment variables、third-party library versions（pip）、datasets、weights、random operations；任一不一致即需调整环境。原文示例中 MindSpore 2.7.2 vs 2.8.0 的比对，仅 `pip` 项显示 `error`（其余四项 `pass`），符合跨版本预期。

8. **训练状态监控起步**：以**权值梯度监控**为例，需在训练脚本所在目录创建 `monitor_v2_config.json` 配置文件（原文此处被截断，未给出完整 JSON）。

---

## 【关键机制与数据】

**工作原理与数据流（仅基于原文可推断内容）：**

- **预训练配置检查（Pre-training Configuration Check）**：在两个环境（基准侧 + 待比对侧）分别跑同一份训练脚本，调用 `ConfigChecker.apply_patches(fmk="mindspore")` 注入框架补丁，并在模型初始化后调用 `ConfigChecker(...)` 抓取**影响训练精度的环境配置**——原文明确列出五类：**环境变量、第三方库版本、权重、数据集、随机函数**。抓取结果按 `rank` 与 `micro_step` 维度落盘到 `.zip` 包。**原文：*"environment variables, third-party library versions, weights, datasets, random functions"*、*"Data is stored by rank and step, where step refers to micro_step."***

- **跨环境比对**：将两份包转到同一环境执行 `msprobe config_check -c bench_zip_path cmp_zip_path -o output_path`，产出 `result.xlsx`。**原文：*"comparison result. It contains multiple sheets, where the summary sheet provides an overview of the check results, and other sheets contain details of specific check items, where step is micro_step."***

- **跨版本特殊说明**：本指南示例为 **同一环境**下两个 MindSpore 版本（2.7.2 / 2.8.0）的精度比对，因此"两套检查结果的唯一差异仅为版本号"，可跳过预训练配置检查步骤。**原文：*"the scenario involves accuracy comparison between different MindSpore versions in the same environment. Therefore, the only difference in the results checked for the two scenarios will be the version number, so you can skip this step."***

- **精度比对后续步骤**：执行训练→使用 msProbe 在 NPU 侧与基准侧做 forward/backward 输入输出对比→快速定位精度异常 API（原文此处为流程描述，未给出具体数值或性能数据）。

- **性能调优三步法**：① MindSpore Profiler 采集性能数据 → ② msprof-analyze 统计分析并给出调优建议 → ③ MindStudio Insight 可视化呈现。

**性能数据**：原文未提供任何具体的吞吐/时延/加速比等性能数值，仅有功能流程描述。

---

## 【表格解读】

**原文无传统参数表/性能对比表，但存在一段类 ASCII 形式的检查结果输出**。以下用 markdown 表格逐字还原并逐行解读：

| filename | ass_check | 解读 |
|---|---|---|
| env | pass | **环境变量**检查通过；同一台机器的两个 MindSpore 版本环境下，`env` 维度无差异。 |
| pip | error | **第三方库版本**检查报错；这是预期内的，因为 MindSpore 2.7.2 与 2.8.0 各自依赖的第三方包版本不同，本项差异即对应框架版本差异。 |
| dataset | pass | **数据集**检查通过；两版本共用同一份数据集，未引入差异。 |
| weights | pass | **权重**检查通过；两版本下加载的权重一致。 |
| random | pass | **随机操作**检查通过；随机种子与随机行为一致，未引入精度偏移。 |

**说明**：原文示例的检查结果用于演示——在跨 MindSpore 版本场景下，`pip` 报 error 不代表真实精度问题，而是版本差异导致的预期差异；其余四项通过则说明训练前环境已对齐，可进入精度数据采集与比对环节。

---

## 【公式解读】

**原文无公式**（既无 LaTeX 表达式，也无伪代码形式的数学公式）。仅出现少量 Python API 调用与 CLI 命令，已在【技术要点】与【使用方法】中还原。

---

## 【关联】

**工具/模块上下游关系（基于原文提及）：**

- **msProbe（MindStudio Probe）**：精度调试工具，原文给出外部链接 `https://gitcode.com/Ascend/msprobe`，更多功能需跳转该链接查阅；本文档中其能力被拆为 5 个子步骤——①预训练配置检查、②训练状态监控、③精度数据采集、④精度预检（扫 API 找异常）、⑤精度对比（NPU vs 基准环境）。
- **MindSpore Profiler API**：性能数据采集端，产出物交由 msprof-analyze 处理。
- **msprof-analyze**：消费 Profiler 原始数据，进行统计分析并产出**调优建议**。
- **MindStudio Insight**：性能数据可视化工具，承接 msprof-analyze 的输出做图形化呈现。
- **CANN Toolkit / ops operator package**：性能/精度工具运行所依赖的底层套件，需安装兼容版本并配置环境变量，原文链接到 CANN Software Installation Guide（Ubuntu 本地安装路径）。
- **MindSpore 框架本身**：本文档示例版本为 **2.7.2 与 2.8.0**，需按 MindSpore Installation Guide 安装。
- **训练脚本样本 `mindspore_main.py`**：上游脚本模板，源码参见原文锚点 `#MindSpore-Ascend-NPU-Environment-Training-Script-Sample`（原文未展开内容）。
- **预训练配置检查代码样本**：位于原文锚点 `#MindSpore-Pre-training-Configuration-Check-Code-Sample`，原文注明可"直接复制完整代码执行"。

**流程串联（性能调优侧）**：MindSpore Profiler 采集 → msprof-analyze 分析 → MindStudio Insight 可视化，三者构成性能调优的完整闭环。

**精度调试侧串联**：ConfigChecker 采集 → msprobe config_check 比对 → result.xlsx 查看 → 不一致项调整环境 → 进入训练状态监控与精度数据采集/对比。

> 注：原文末尾 `monitor_v2_config.json` 内容被截断，"Training Status Monitoring"及后续小节（精度数据采集、精度预检、精度对比、性能调优步骤）的具体命令、参数表与示例均未在原文中给出，故本解读未涵盖后续细节。

---

## 【使用方法】

**1. 环境准备（前置）**
- 准备基于 Ascend NPU 的训练服务器（如 Atlas A2 训练产品），安装 NPU 驱动与固件。
- 安装兼容版本的 CANN Toolkit 与 ops operator 包，并配置 CANN 环境变量。
- 安装 MindSpore 框架（原文示例版本 2.7.2、2.8.0）。

**2. 模型开发与迁移**
- 暂未提供 MindSpore 迁移工具；直接在 Ascend 环境编写训练脚本，文件名约定为 `mindspore_main.py`，上传至训练服务器任意可读写目录。
- 执行训练：`python mindspore_main.py`；完成时打印 `train finish`。

**3. 模型精度调试**

**3.1 预训练配置检查**
- 安装 msProbe：`pip install mindstudio-probe --pre`
- 脚本开头插入：
  ```python
  from msprobe.core.config_check import ConfigChecker
  ConfigChecker.apply_patches(fmk)        # fmk="mindspore"
  ```
- 模型初始化后插入：
  ```python
  from msprobe.core.config_check import ConfigChecker
  ConfigChecker(model=model, output_zip_path="", fmk="")   # fmk="mindspore"
  ```
  - `output_zip_path` 默认值 `"./config_check_pack.zip"`，**必须显式指定 zip 包名**。
  - `model`：已初始化的模型；权重与数据集默认**不采集**。
- 执行训练：`python mindspore_main.py`，结束后产出 `.zip` 包（按 `rank`、`micro_step` 维度组织）。
- 在两个环境分别产出 zip 后，转到同一环境执行比对：
  ```bash
  msprobe config_check -c bench_zip_path cmp_zip_path -o output_path
  ```
  - `bench_zip_path`：基准侧 zip 包名；`cmp_zip_path`：待比对侧 zip 包名。
  - `output_path` 默认 `"./config_check_result"`，生成 `bench/`、`cmp/`、`result.xlsx`。
- 检查通过标准：五项（env、pip、dataset、weights、random）必须全部 `pass`；若 `pip` 因跨 MindSpore 版本导致 `error`，属预期情况（本示例场景）。

**3.2 训练状态监控（原文此处被截断）**
- 需在训练脚本所在目录创建 `monitor_v2_config.json` 配置文件，示例功能为"权值梯度监控"；**JSON 内容原文未给出**。

**3.3 精度数据采集 / 精度预检 / 精度对比**
- 原文仅描述流程（API/Module 级 forward/backward 输入输出采集 → 精度预检 → NPU vs 基准对比），**具体命令、参数表原文未给出（处于截断部分）**。

**4. 模型性能调优（原文仅描述流程）**
- 性能采集 MindSpore Profiler → 性能分析 msprof-analyze → 性能可视化 MindStudio Insight；**具体启用命令与配置项原文未给出（处于截断部分）**。

## 图文联合解读

- `5.png`: **图文联合解读：**

1）图为msProbe精度比对输出的表格，包含vpp_stage、step、module_name、scope、micro_step、min、max、mean、norm、nans等列，记录fc.bias与fc.weight在step=2、scope=unreduced时的张量统计量，min=0、max≈5.71E-35、mean≈2.85E-35，数值极小。

2）论证了fc层权重与偏置出现严重数值下溢（数量级1E-35），norm为0，表明模型存在精度异常，可快速定位问题模块。

3）契合文档论点：在Ascend环境训练精度调试场景下，msProbe通过逐模块统计量对比，能够辅助用户快速界定精度异常模块，支撑模型迁移与精度调优流程。
- `6.png`: ## 图文联合解读

**1) 图中内容**
表格对比 NPU 与 Bench（基准）环境下算子的精度表现，列含算子名、dtype、tensor shape、requires_grad 及**Cosine 相似度**。示例：Float32 的 `Primitive.sh`/`Primitive.ma` 在 [2,2] shape 下 Cosine=1（一致），而 int 类型的 `Primitive.sh` 标记为 unsupport。

**2) 技术结论**
msProbe 通过逐算子比对 NPU 与 Bench 的 dtype、shape、梯度属性及 Cosine 相似度，自动判定：
- 数值一致性（Cosine=1 表明精度对齐）；
- 类型/算子兼容性（int 类型 unsupported 即暴露迁移缺口）。

**3) 与文档论点关系**
直接支撑文档"模型迁移精度快速定界"的核心流程——当训练出现精度损失时，msProbe 以此粒度数据迅速定位异常算子，而非依赖训练 loss 模糊排查，实现精准归因。
- `7.png`: 1) 图示为msProbe精度比对结果表格，含EucDist、MaxAbsErr、MaxRelativeErr等误差指标及NPU张量统计(max/min/mean/l2norm)，前两行记录完整比对数据，后两行因不支持而显示"unsupported"。

2) 论证在迁移场景中，msProbe可对NPU与基准环境的张量逐项做精度比对：当算子支持时输出量化误差，不支持时标记"unsupported"以便定位问题模块。

3) 呼应文档"模型开发与迁移"及"精度调试快速定界"论点，为msProbe收集和比较训练精度数据、识别环境差异提供实测佐证。
- `8.png`: 1) 图中展示msProbe工具输出的精度对比表格，列含Bench max/min/mean/l2norm、Requires_grad、Consistent、Result、Err_message、NPU_Stack_Info、Data_name，各行Result均为"pass"，Err为空，数据来源于"File /root/mini"和"['-1','-1']"等Primitive算子。

2) 论证了NPU环境与基准环境在指定算子上的张量统计量一致（max/min/mean/l2norm相同、梯度需求一致），精度比对通过，无异常。

3) 与文档论点对应：体现msProbe通过比对基准与NPU精度数据快速定位异常模块的能力，是"模型精度调测"流程中比对环节的示例输出。
