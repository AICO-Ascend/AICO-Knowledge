# msTT Quick Start in PyTorch Scenarios

> 仓 `mstt` · 路径 `docs/en/quick_start/pytorch_mstt_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mstt/docs/en/quick_start/pytorch_mstt_quick_start.md

```markdown
# msTT PyTorch Quick Start 文档深度解读

> ⚠️ 原文在 "Pre-training Configuration Check" 章节末尾处被截断（停留在 `output_zip_path` 默认值 `"./config_check"`），下文解读仅基于已提供的原文内容，未出现章节（如 "Training Status Monitoring"、"Accuracy Data Collection" 等）不臆测展开。

---

## 【定位】

本篇是 msTT（MindStudio Training Tools）工具链在 PyTorch 训练场景下的**入门级端到端 Quick Start**，聚焦 Ascend NPU 环境，覆盖三大主流程：模型开发与迁移、模型精度调试、模型性能调优，并以 ResNet-50 + CANN 8.5.0 为可运行示例，把"环境准备 → GPU 脚本迁移 NPU → 精度比对工具接入"完整串通。

---

## 【技术要点】

1. **msTT 工具链四件套及其分工**
   - **msProbe**：精度调试工具，跨基准环境（CPU/GPU）与 Ascend NPU 采集并比对训练精度数据。
   - **Ascend PyTorch Profiler API**：在 PyTorch 训练场景采集性能数据。
   - **msprof-analyze**：对性能数据做统计/分析并输出调优建议。
   - **MindStudio Insight**：性能数据可视化。

2. **三条主线流程**
   - 模型开发与迁移：借助迁移工具自动迁移 GPU 训练脚本至 Ascend NPU。
   - 模型精度调试：预训练配置检查 → 训练状态监控 → 精度数据采集 → 精度预检 → 精度比对。
   - 模型性能调优：Profiler 采集 → msprof-analyze 分析 → MindStudio Insight 可视化。

3. **示例环境规格（原文声明）**
   - 硬件：基于 Ascend NPU 的训练服务器（如 Atlas A2 训练产品）。
   - 软件栈版本：**CANN 8.5.0**；**PyTorch 2.9.0 + Python 3.12 + AArch64 + torchvision==0.24.0**。

4. **GPU→NPU 自动迁移的两行关键改动**
   插在训练脚本的 **第 24、25 行**：
   ```python
   24 import torch_npu
   25 from torch_npu.contrib import transfer_to_npu
   ```
   即可直接在 Ascend NPU 环境执行训练。

5. **示例训练命令与运行结果指标**
   - 命令：`python pytorch_main.py -a resnet50 -b 32 --gpu 1 --dummy`
   - dummy 数据、batch size 32、单卡（GPU/NPU 标志 `--gpu 1` 实际跑 NPU），total iter = **40037**。

6. **msProbe 安装与配置检查 API**
   - 安装：`pip install mindstudio-probe --pre`
   - 脚本首行插桩：`from msprobe.core.config_check import ConfigChecker` + `ConfigChecker.apply_patches(fmk)`
   - 模型初始化后调用：`ConfigChecker(model=model, output_zip_path="", fmk="")`
   - 关键参数：`fmk` 支持 `"pytorch"` 与 `"mindspore"`；默认不收集权重与数据集。

---

## 【关键机制与数据】

### 工作原理 / 数据流（原文表述）

- **整体机制**：msTT 把训练开发拆为"开发迁移 → 精度调试 → 性能调优"三个独立闭环，每个闭环对应一组工具协同工作。
- **精度调试机制**（原文表述）：
  - **Pre-training Configuration Check**：先收集两套环境（基准环境 vs Ascend NPU 环境）的环境变量、第三方库版本、权重、数据集、随机函数等可能影响精度的配置项，并打成 zip 包做差异比对。原文要求"在 GPU 与 Ascend NPU 环境分别执行，且两个 zip 包必须取不同名字"。
  - 后续步骤（训练状态监控/精度数据采集/精度预检/精度比对）原文未给出具体命令（文档被截断）。
- **性能调优机制**（原文表述）：Ascend PyTorch Profiler 采集 → msprof-analyze 分析与调优建议输出 → MindStudio Insight 可视化。

### 数据流（迁移 + 训练日志）

GPU 训练脚本 → 添加 2 行 `torch_npu` 桥接代码 → 直接在 Ascend NPU 执行 → 输出迭代日志。原文给出的 3 条样本日志（原文逐字）：

| Iteration | Time (cur/avg) | Data (cur/avg) | Loss (cur/avg) | Acc@1 (cur/avg) | Acc@5 (cur/avg) |
|---|---|---|---|---|---|
| `[ 1/40037]` | `4.923 ( 4.923)` | `0.502 ( 0.502)` | `7.0165e+00 (7.0165e+00)` | `0.00 (  0.00)` | `0.00 (  0.00)` |
| `[ 11/40037]` | `0.061 ( 0.996)` | `0.000 ( 0.541)` | `1.2860e+01 (1.9566e+01)` | `0.00 (  0.00)` | `0.00 (  0.85)` |
| `[ 21/40037]` | `0.063 ( 0.551)` | `0.000 ( 0.285)` | `9.5061e+00 (1.5033e+01)` | `0.00 (  0.00)` | `0.00 (  0.74)` |

解读：cur/avg 是"当前迭代值 / 累计均值"的双值格式；Acc@1/Acc@5 在 dummy 数据下均为 0，符合 dummy 模式预期；Log 表明迁移成功（NPU 设备识别为 `Using device: npu`）。

### 性能数据

> 原文未提供量化性能数据（如吞吐/FPS/对比基准）。

---

## 【表格解读】

**原文无表格**（文中的"列对齐数字块"是训练日志输出，非结构化表格，故不作为表格还原）。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

依据文中显式给出的链接/锚点，梳理依赖与上下游：

| 关联对象 | 类型 | 用途 |
|---|---|---|
| `MindStudio Probe`（https://gitcode.com/Ascend/msprobe） | 外部仓库 | msProbe 功能总览与详细文档入口 |
| `CANN Software Installation Guide` | 外部文档 | CANN 8.5.0 Toolkit/ops-operator 安装与 env 配置方法 |
| `Ascend Extension for PyTorch Software Installation Guide`（"Installing PyTorch > Method 1: Binary Package"） | 外部文档 | PyTorch 2.9.0 + torchvision 0.24.0 的二进制安装路径 |
| `Migration Tools`（https://www.hiascend.com/.../atlasfmkt_16_0001.html） | 外部文档 | GPU→Ascend NPU 自动迁移工具的详细说明 |
| `#environment-setup` | 内部锚点 | "Environment Setup" 章节，作为前置条件被多节引用 |
| `#model-development-and-migration` | 内部锚点 | "Model Development and Migration" 章节，作为精度调试的前置条件 |
| `#pytorch-gpu-environment-training-script-sample` | 内部锚点 | GPU 训练脚本示例，迁移前的模板来源 |
| `#pytorch-ascend-npu-environment-training-script-sample` | 内部锚点 | 已添加 `torch_npu` 桥接的 NPU 训练脚本示例（可直接拷贝） |
| `#pytorch-gpu-pre-training-configuration-check-code-sample` | 内部锚点 | GPU 端 Pre-training Configuration Check 的代码示例 |
| `#pytorch-ascend-npu-pre-training-configuration-check-code-sample` | 内部锚点 | Ascend NPU 端 Pre-training Configuration Check 的代码示例 |
| `msProbe Tool Installation Guide`（https://gitcode.com/Ascend/msprobe/.../msprobe_install_guide.md） | 外部文档 | `pip install mindstudio-probe --pre` 的安装详情 |

关联图（自顶向下）：

```
msTT Toolchain
├── Model Development & Migration
│     └─ Migration Tools（外部）── GPU Script Sample（内部锚点）── NPU Script Sample（内部锚点）
├── Model Accuracy Debugging
│     ├─ Pre-training Configuration Check ── msProbe（外部仓库 & Install Guide）
│     │     ├─ GPU Check Code Sample（内部锚点）
│     │     └─ NPU Check Code Sample（内部锚点）
│     ├─ Training Status Monitoring（原文未展开）
│     ├─ Accuracy Data Collection（原文未展开）
│     ├─ Accuracy Pre-check（原文未展开）
│     └─ Accuracy Comparison（原文未展开）
└─ Model Performance Tuning
      ├─ Ascend PyTorch Profiler API
      ├─ msprof-analyze
      └─ MindStudio Insight

前置依赖（所有流程）
└─ Environment Setup（CANN 8.5.0 + PyTorch 2.9.0 + Python 3.12 + AArch64 + torchvision 0.24.0）
```

---

## 【使用方法】

### 环境准备

| 步骤 | 操作 | 命令/动作 |
|---|---|---|
| 1 | 准备训练服务器 | 安装 Ascend NPU 驱动与固件（如 Atlas A2） |
| 2 | 安装 CANN | CANN 8.5.0 Toolkit + ops 包，并配置 CANN 环境变量 |
| 3 | 安装框架 | PyTorch 2.9.0 + Python 3.12 + AArch64 + torchvision==0.24.0（二进制包方式） |

### 模型开发与迁移（GPU → Ascend NPU）

1. 创建 `pytorch_main.py`，内容拷贝自 **PyTorch GPU Environment Training Script Sample**。
2. 上传 `pytorch_main.py` 到 Ascend NPU 训练服务器任意可读写目录。
3. 在脚本的 **第 24、25 行** 加入：
   ```python
   24 import torch_npu
   25 from torch_npu.contrib import transfer_to_npu
   ```
   （或直接拷贝 **PyTorch Ascend NPU Environment Training Script Sample**）
4. 执行训练：
   ```bash
   python pytorch_main.py -a resnet50 -b 32 --gpu 1 --dummy
   ```
5. 若日志首行出现 `Using device: npu`，并能正常打印迭代日志，权重也能成功落盘 → 迁移完成。

### 模型精度调试 — 预训练配置检查（Pre-training Configuration Check）

> 原文要求：必须在 **GPU 与 Ascend NPU 两侧分别执行**，并给出**不同的 zip 包名**。

**安装**
```bash
pip install mindstudio-probe --pre
```

**GPU 端 + NPU 端共同插桩点（原文逐字）**

- **点位 A**——训练流程中**第一个 Python 脚本的最开头**（示例为 `pytorch_main.py`）：
  ```python
  1 from msprobe.core.config_check import ConfigChecker
  2 ConfigChecker.apply_patches(fmk)
  ```
  - `fmk`：训练框架，字符串，可选 `"pytorch"` 或 `"mindspore"`；此处配 `"pytorch"`。

- **点位 B**——**模型初始化之后**（示例为第 172、173 行）：
  ```python
  172 from msprobe.core.config_check import ConfigChecker
  173 ConfigChecker(model=model, output_zip_path="", fmk="")
  ```
  - `model`：已初始化的模型；默认**不收集权重与数据集**。
  - `output_zip_path`：输出 zip 包路径（字符串，**必须显式指定 zip 包名**）。默认值原文截断为 `"./config_check`（被截断）。
  - `fmk`：同上。

**完整代码示例来源**：GPU 端从 `PyTorch GPU Pre-training Configuration Check Code Sample` 拷贝；Ascend NPU 端从 `PyTorch Ascend NPU Pre-training Configuration Check Code Sample` 拷贝。

### 模型精度调试 — 训练状态监控 / 精度数据采集 / 精度预检 / 精度比对
> **原文未涉及**（文档被截断）。

### 模型性能调优
> **原文未涉及具体命令**（仅说明流程为 Profiler → msprof-analyze → MindStudio Insight）。
```

## 图文联合解读

- `4.png`: **1) 图中内容：** 表格展示msProbe在训练step=99对conv1.weight、bn1.weight、bn1.bias三个模块的统计输出，列含ppp_stage、step、module_name、scope、micro_step、min、max、mean、norm、nans。

**2) 技术结论：** 三行nans均为0，max/min幅度（如conv1.weight的±0.02）和norm量级合理，论证训练数值精度处于正常区间，无溢出或发散异常。

**3) 与文档论点的关系：** 印证文档所述msProbe可逐模块采集精度统计、对比基线环境的能力，为Ascend NPU训练中精度异常的快速定界提供数据支撑。
- `zh-cn_image_0000002446546936.png`: **图文联合解读：**

1）图为算子级精度比对结果表，包含API名称、正反向测试状态、提示信息列，覆盖Tensor.to（跳过）、conv（反向error）、add_/batchnorm/relu（正反向pass）等典型PyTorch算子。

2）该表论证：精度问题可下沉到**算子粒度**定位，通过逐算子正反向比对，能快速圈定异常模块。

3）与文档呼应：直接支撑msProbe"精度问题快速界定"的核心论点，展示其从训练loss宏观异常下钻到具体算子（如conv反向报错）的调试路径。
- `zh-cn_image_0000002480026577.png`: 图示为msProbe精度比对结果表，列出Functional、Tensor._ia等API在均方根误差、相对误差、inf/nan率等多维度误差指标下的比值与判定结果。所有API判定均为"pass"，表明基准环境与昇腾NPU环境精度一致，论证了模型迁移/训练后精度可信，呼应文档"用msProbe快速定界精度异常"的核心论点。
- `zh-cn_image_0000002479906833.png`: # 图文联合解读

**图中所画**：表格呈现msProbe精度比对工具的输出结果，包含相对误差、绝对错误率、二进制一致错误率、ULP误差平均值/阈值占比、双千指标等多维度精度度量项，并列出标杆比对法、绝对阈值法、二进制一致法三种比对策略，判定结果均为"pass"。

**技术结论**：在昇腾NPU与基准环境（GPU/CPU）对比中，多种精度指标均通过验证，说明模型数值一致性良好，无精度溢出或发散问题，验证了msProbe多算法并行比对的有效性。

**与文档关系**：作为msProbe精度调测流程的输出示例，支撑"快速定位异常模块、对比基准环境与昇腾NPU训练数据"的核心论点。
- `1.png`: **图文联合解读：**

1) 图中展示msProbe对比表格，列包含NPU/Bench两端的张量名称、dtype（float32/int64）、shape（如[32,3,224,224]）、requires_grad及Cosine相似度，数值范围0.74–0.85（unsupport标注非可比项）。

2) 论证：dtype、shape、grad属性逐项对齐验证后，Cosine相似度可作为数值精度比对的核心指标，量化NPU与Bench输出一致性。

3) 与文档呼应：表格正是msProbe在精度调试场景下的产物——通过结构属性匹配筛除不可比张量，聚焦可疑层进行精度定界，支撑"快速定位问题模块"的论点。
- `2.png`: **图文联合解读：**

1）**图内容**：表格呈现msProbe工具输出的精度比对数据，包含欧氏距离(EucDist)、最大绝对误差(MaxAbsErr)、最大相对误差(MaxRelativeErr)、千分位/万分位误差比、NPU张量统计量(max/min/mean/l2norm)及TRUE/FALSE越界标记。数据按EucDist=900.85和1992.19两组呈现，并含"unsupported"未支持算子条目。

2）**技术结论**：相同输入下两组数据误差指标存在数量级差异（MaxAbsErr从4.5e+15降至716），NPU均值与l2norm对应变化，表明Ascend NPU与基准环境存在精度偏差，可据此定位异常模块。

3）**与文档论点关系**：呼应"精度溢出可借助msProbe快速定界"的核心论点，通过结构化误差数据为模型迁移中的精度调测提供可量化依据。
- `3.png`: 1) 图示内容：表格对比msProbe工具输出的精度比对数据，列包含Bench_max、min、mean、l2norm（基准侧统计量）、Requires_grad、Consistent（一致性判断）、Result、Err_message、NPU_Stack_Info、Data_name。

2) 技术结论：展示了msProbe对算子张量进行基准环境与NPU环境的逐项精度对比，所有行Result均为pass，l2norm值极小，表明迁移后精度一致。

3) 与文档关系：佐证"模型迁移到Ascend NPU后可用msProbe快速定位精度问题"，体现工具对比基准与NPU数据、验证一致性的核心能力。
- `zh-cn_image_0000002446706788.png`: **1) 图示内容**：TensorBoard GRAPH_ASCEND 双栏对比视图，左侧"调试侧"与"右侧标杆侧"并列展示 DefaultModel 的同名算子节点（如 Conv2d、BatchNorm2d 高亮、ReLU、MaxPool、Sequential 等），底部"比对详情"列出 Module.bn1.BatchNorm2d.forward.0 的 input.0/parameter 张量统计（shape、Max/Min/Mean、Norm、Cosine、EucDist、MaxAbsErr 等），节点状态为绿色"已匹配"。

**2) 技术结论**：通过算子级张量统计与距离度量（Cosine=1.0、MaxAbsErr=0.0）证明两侧 BatchNorm2d 节点在指定 step 下精度完全一致，可逐节点下钻定位异常。

**3) 与文档关系**：印证 msProbe 在 PyTorch 训练中"以 Benchmark 与 Ascend NPU 端算子输入/输出逐节点比对、迅速界定异常来源"的精度调测能力，是快速入门流程的可视化体现。
- `zh-cn_image_0000002446706840.png`: **图文联合解读：**

1) **画面内容**：MindStudio Insight 工具的 Timeline（时间线）视图，左侧为 Data Manager（导入 profiling_data），主面板按线程/硬件层级展开：Python(1784298) CPU 执行 ProfilerStep#1、aten::item、aten::local_scalar_dense；Thread 1785017 显示 Dequeue@Conv2DBackprop…操作；Ascend Hardware NPU 1 Stream 2、AI Core Freq（粉色频谱条）记录 NPU 算力使用；底部 Overlap Analysis 显示 Computing/Free（绿色空闲占比），时间轴 00:02.375–00:04.875。

2) **技术结论**：可视化揭示 CPU 侧 Python 算子调用、NPU Stream 任务调度、AI Core 算力与计算/空闲间隙并存，呈现 CPU↔NPU 流水线并行情况。

3) **与文档关系**：对应文中"Ascend PyTorch Profiler API 采集性能数据 → MindStudio Insight 可视化"环节，为模型性能调优提供瓶颈定位依据。
