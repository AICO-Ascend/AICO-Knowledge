# Quick Start of msProbe in the MindSpore Scenario

> 仓 `msprobe` · 路径 `docs/en/quick_start/mindspore_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprobe/docs/en/quick_start/mindspore_quick_start.md

# msProbe MindSpore 场景快速上手文档 — 深度解读

---

## 【定位】

这篇文档面向基于昇腾 NPU（或由 GPU 迁移至 NPU）的大模型训练场景，介绍 msProbe（MindStudio Probe）在 MindSpore 框架下"精度数据采集 → 精度比对"的最小化快速上手路径，帮助用户在训练出现精度溢出、loss 异常发散/不收敛时快速完成故障定界与定位。

---

## 【技术要点】

1. **典型使用流程五步**：①训练前配置检查 → ②训练状态监控 → ③精度数据采集 → ④精度预检 → ⑤精度比对。本 Quick Start 只覆盖"精度数据采集"和"精度比对"两环，其它能力需查阅其它文档。

2. **环境要求**：Atlas A2 训练服务器 + 配套 NPU 驱动固件；CANN Toolkit + OPS（示例版本 **CANN 8.5.0**）；MindSpore（示例版本 **2.7.2 与 2.8.0**）；通过 `pip install mindstudio-probe --pre` 安装 msProbe。

3. **精度数据采集入口（MindSpore）**：
   ```python
   from msprobe.mindspore import PrecisionDebugger
   debugger = PrecisionDebugger(config_path="./config.json")
   debugger.start(model)   # 开启 dump
   train_step(data, label)
   debugger.stop()         # 暂停；下次 start 仍记录到当前 step
   debugger.step()         # 步进；下次 start 记录到下一步 step
   ```

4. **采集配置 `config.json` 关键字段**：`task="statistics"`、`dump_path="/home/dump/dump_data"`、`rank=[]`、`step=[0,1]`、`level="L1"`、`async_dump=false`；`statistics` 子段含 `scope=[]`、`list=[]`、`tensor_list=[]`、`data_mode=["all"]`。

5. **dump 输出物（按 `dump_path` 路径组织）**：`stepN/rank/construct.json`（模块层级关系，文中标注"该场景下为空"）、`dump.json`（前反向 API 输入输出统计 + 溢出/下溢信息）、`dump_tensor_data/`（实际输入输出 `.npy` 张量）、`stack.json`（API 调用栈）。

6. **精度比对命令（CLI）**：
   ```bash
   msprobe compare -tp /home/dump/dump_data_2.8.0/step0/rank/dump.json \
                   -gp /home/dump/dump_data_2.7.2/step0/rank/dump.json \
                   -o ./compare_result/accuracy_compare
   ```
   输出 xlsx，命名 `compare_result_{timestamp}.xlsx`，通过 `Result` 列与 `Err_Message` 列定位可疑算子，但每个指标各自有判定门槛，需结合实际情况判断。

---

## 【关键机制与数据】

- **故障定界逻辑（原文）**："metrics such as the training loss cannot accurately locate the failed module, msProbe is recommended for rapid fault demarcation."——即当 loss 等宏观指标无法定位失败模块时，用 msProbe 做"快速故障定界"。

- **数据流**（原文整合）：
  - 用户脚本实例化 `PrecisionDebugger` → 加载 `config.json` → `debugger.start(model)` 在模型上挂载 hook（原文日志："The aip tensor hook function is successfully mounted to the model."）。
  - `Dump switch is turned on at step 0.` → 按 `step` 列表（示例 `[0,1]`）在指定 step 启用/暂停 dump。
  - 数据落盘到 `dump_path/stepN/rank/{construct.json, dump.json, dump_tensor_data/*.npy, stack.json}`。
  - 比对阶段：`compare` 命令读取两份 dump 中的 `dump.json`（`-tp` 测试侧 / `-gp` 基准侧），生成 `compare_result_{timestamp}.xlsx`。

- **采集开关语义（原文）**：
  - `debugger.stop()`——禁用 dump，若再次开启，采集数据仍记录到**同一个 step**（与下文 `debugger.step()` 的行为做对比）。
  - `debugger.step()`——结束当前 step 的 dump，若再次开启，采集数据记录到**下一个 step**。

- **存储成本提示（原文）**："Precision data occupies certain drive space. … The space required by precision data is closely related to model parameters, collection configurations, and number of collection iterations."——即占用与**模型参数量、采集配置、采集迭代次数**三者均相关，需预留磁盘。

- **比对结果判定（原文）**："each metric has a determination standard. Since each metric has its own evaluation criteria, make judgments based on actual circumstances."——xlsx 中的 `Result` 与 `Err_Message` 只提示可疑算子，是否确为问题需结合各指标自身判据。

> 注：原文未给出耗时、吞吐、显存/磁盘占用等量化性能数据。

---

## 【表格解读】

**原文无显式表格。** 文中唯一结构化信息是 `dump_data/` 的目录树，可还原为下表以便查阅：

| 路径 | 类型 | 含义（原文逐字释义） |
|---|---|---|
| `dump_data/step0/rank/construct.json` | 文件 | "Hierarchical relationship information of modules. **This file is empty in the current scenario.**"（模块层级关系信息；当前 MindSpore 场景下为空） |
| `dump_data/step0/rank/dump.json` | 文件 | "Input and output statistics and overflow/underflow information of forward and backward APIs."（前向与反向 API 的输入输出统计、溢出/下溢信息） |
| `dump_data/step0/rank/dump_tensor_data/` | 目录 | "Actual input and output tensor data of forward and backward APIs."（前向与反向 API 的实际输入输出张量） |
| `dump_data/step0/rank/dump_tensor_data/Jit.Momentum.0.forward.input.1.0.npy` | 示例文件 | 单个 forward 输入张量（命名示例如 Jit 算子） |
| `dump_data/step0/rank/dump_tensor_data/Primitive.matmul.MatMul.1.forward.input.1.npy` | 示例文件 | 单个 Primitive 算子（如 MatMul）forward 输入张量 |
| `dump_data/step0/rank/dump_tensor_data/Mint.add.1.backward.input.0.npy` | 示例文件 | 单个 backward 输入张量（命名示例如 add） |
| `dump_data/step0/rank/dump_tensor_data/Primitive.matmul.MatMul.1.forward.output.0.npy` | 示例文件 | 单个 Primitive 算子 forward 输出张量 |
| `dump_data/step0/rank/stack.json` | 文件 | "API call stack information"（API 调用栈信息） |
| `dump_data/step1/...` | 目录 | 第二个采集 step 的同名结构（与 `step0` 同构） |

逐行解读：
- `construct.json` 在 MindSpore 场景下为空，说明该场景不支持（或不需要）模块层级关系视图，仅保留 API 层信息。
- `dump.json` 是后续 `msprobe compare` 命令直接消费的文件（`-tp`/`-gp` 均指向它），含统计量与溢出/下溢信息，是"先做轻量预检"的关键文件。
- `dump_tensor_data/` 是后续精度比对时所引用张量的实际 `.npy` 落盘目录；命名约定包含 `<Jit/Mint/Primitive>.<OpName>.<idx>.{forward|backward}.{input|output}.<idx>.npy` 的风格，便于按算子类型与方向定位。
- `stack.json` 记录调用栈，便于把可疑算子还原回 Python 调用位置。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

依据文末与文中出现的内部链接：

- **`<>`（CANN Software Installation Guide）**：环境搭建第 2 步引用的占位链接，指向 CANN 安装说明，是 `pip install mindstudio-probe --pre` 之前必备的 CANN 配套环境。
- **`../msprobe_install_guide.md`**：环境搭建第 4 步明确要求"Install msProbe by referring to msProbe Installation Guide"，本文只给出一行安装命令 `pip install mindstudio-probe --pre`，完整安装细节依赖该上游文档。
- **`../accuracy_compare/mindspore_accuracy_compare_instruct.md#output-file-description`**：在 `compare` 命令产出 `compare_result_{timestamp}.xlsx` 之后，文档明确指引用户阅读该页"Output File Description"以了解 xlsx 中各列（`Result`、`Err_Message` 等）的判定细节与指标判据——即本文只做"生成"，具体"解读"在该下游文档。

**与本文中其它特性的关系（基于原文表述）**：
- "Usage Process" 中明确本文只覆盖**第 3 步精度数据采集**和**第 5 步精度比对**；第 1 步（配置检查）、第 2 步（训练状态监控）、第 4 步（精度预检）"please refer to the relevant documentation"——即本文与"训练状态监控""精度预检"等模块是平行并列关系，本文不展开。
- "Graph Comparison in Hierarchical Visualization Mode" 一节在原文末尾以"- The f"截断（疑似文档未渲染完整），因此与"compare 命令行比对"形成另一种比对形态，本节解读只能基于已展示的章节标题与前置条件做出，不臆造。

---

## 【使用方法】

### 1. 安装（原文）
```bash
pip install mindstudio-probe --pre
```

### 2. 准备 `config.json`（原文）
放置于训练脚本同目录，关键字段：
- `task="statistics"`
- `dump_path`：dump 落盘目录（示例 `/home/dump/dump_data`）
- `rank`：要采集的 rank 列表（示例 `[]`）
- `step`：要采集的 step 列表（示例 `[0,1]`）
- `level`：采集层级（示例 `"L1"`）
- `async_dump`：是否异步（示例 `false`）
- `statistics.scope` / `list` / `tensor_list` / `data_mode`：示例分别取 `[]` / `[]` / `[]` / `["all"]`

### 3. 改造训练脚本（原文 MindSpore 2.7.2 / 2.8.0）
- `from msprobe.mindspore import PrecisionDebugger`
- `debugger = PrecisionDebugger(config_path="./config.json")`
- 在每个 step 的训练逻辑前后分别调用 `debugger.start(model)`、`debugger.stop()`、训练结束或换 step 时调用 `debugger.step()`

### 4. 启动训练（原文）
```bash
python mindspore_main.py
```
成功日志示例：
```txt
The aip tensor hook function is successfully mounted to the model.
msprobe: debugger.start() is set successfully
Dump switch is turned on at step 0.
Dump data will be saved in /home/dump/dump_data/step0.
```

### 5. 精度比对（原文）
```bash
msprobe compare -tp /home/dump/dump_data_2.8.0/step0/rank/dump.json \
                -gp /home/dump/dump_data_2.7.2/step0/rank/dump.json \
                -o ./compare_result/accuracy_compare
```
成功日志示例：
```txt
Compare result is /xxx/compare_result/accuracy_compare/compare_result_{timestamp}.xlsx
...
msprobe compare ends successfully.
```
比对输出文件：`compare_result_{timestamp}.xlsx`，列含 `Result`、`Err_Message`（原文），解读需参见 `../accuracy_compare/mindspore_accuracy_compare_instruct.md#output-file-description`。

### 6. 注意事项（原文）
- 磁盘占用受模型参数量、采集配置、采集迭代数影响，需预留充足空间。
- `debugger.stop()` 与 `debugger.step()` 的差异：`stop` 后再 `start` 仍记入**当前 step**；`step` 后再 `start` 记入**下一 step**。
- 比对结果中各指标有各自判据，需结合实际情况判断（原文未给出具体阈值）。

> 原文未涉及：`async_dump=true` 时的行为细节、其它 `level` 取值含义、`scope/list/tensor_list` 非空时的配置示例、`compare` 的全部可选 flag 列表、以及截断的"Graph Comparison in Hierarchical Visualization Mode"小节的具体启用方式。

## 图文联合解读

- `compare_result_4.png`: **1) 图示内容**：一张NPU与Bench环境逐API精度对比表，列出NPU Name / Bench Name、数据类型、张量Shape、requires_grad、Cosine相似度等字段。Shape/MatMul等Float32算子形状[2,2]、余弦相似度=1；int类型显示"unsupport"。  

**2) 技术结论**：相同dtype与shape的Float32张量在两端数值完全一致；msProbe仅支持可计算余弦的浮点张量比对，整型跳过。  

**3) 与文档关联**：对应"精度比对"步骤，体现工具通过逐API元信息与数值比对，定位NPU与基准环境的精度差异。
- `compare_result_5.png`: **图文联合解读：**

1) **图中内容**：表格展示精度比对指标，含EucDist、MaxAbsErr、MaxRelativeErr、千/五千分位Err Ratio、NPU max/min/mean/l2norm等列，部分行显示"unsupported"（不支持），部分行数值为1、0或2。

2) **技术结论**：说明不同API对统计指标的支持情况存在差异——部分算子（如l2norm）所有行均支持，而MaxAbsErr等列多数API显示"unsupported"，需结合指标特性选用。

3) **与文档关系**：对应文档"精度比对"步骤，提示用户比对NPU与benchmark时需根据API类型选取支持的指标，实现快速精度问题定位。
- `compare_result_6.png`: 1) 图为精度比对结果表，列含Bench_max/min/mean/l2norm、Requires_grad、Consistent、Result、Err_message、MPU_Stack_Info、Data_name，记录基准环境与NPU各API张量统计量及一致性判定。 2) 数据行Result均为"pass"，表明当前采样API在两环境中张量分布一致、对比通过，未发现精度异常。 3) 对应文档"精度比对"步骤：示例如表展示msProbe逐API自动比对结果，帮助快速定位精度问题模块。
- `vis_result.png`: # 图文联合解读

**1) 图中内容**
TensorBoard的GRAPH_ASCEND页面，左右并列展示调试侧与标杆侧两个DefaultModel网络结构图，同步选中Module.bn1.BatchNorm2d.forward.0节点（蓝框高亮），下方"比对详情"表格列出该节点的input.0和parameter在两端的Max/Min/Mean/Norm及Cosine、EucDist、MaxAbsErr等精度指标。

**2) 技术结论**
该节点两端数据完全一致（Cosine=1.0、误差全为0、绿色已匹配），证明msProbe可在API/算子粒度对NPU与标杆环境进行并行结构对齐与逐张量精度比对。

**3) 与文档关系**
对应文档"精度比对"步骤，印证"逐API对比两侧输入输出可快速定位精度问题"的论点。
