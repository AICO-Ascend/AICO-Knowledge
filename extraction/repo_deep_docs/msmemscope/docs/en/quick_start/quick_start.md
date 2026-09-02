# Getting Started with msMemScope

> 仓 `msmemscope` · 路径 `docs/en/quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmemscope/docs/en/quick_start/quick_start.md

# 一体化深度解读：msMemScope Quick Start

---

## 【定位】

本文档是 msMemScope 工具的快速入门指南，面向需要在 CANN + PyTorch 环境下对整网内存进行采集、调试与调优的开发者，介绍从环境变量配置到内存数据采集（Python API 与 CLI 两种方式）的完整跑通流程，使读者能在最短路径上完成首次内存事件采集并查看产出结果。

---

## 【技术要点】

1. **工具能力定位（采集 + 诊断）**：msMemScope 基于采集到的内存事件，提供五类分析能力——内存泄漏检测（memory leak detection）、内存对比（memory comparison）、内存块监控（memory block monitoring）、内存使用分解（memory usage breakdown）、低效内存识别（inefficient memory identification）。

2. **三层环境变量加载顺序**：
   - 先加载 CANN 运行环境：`source <cann-path>/Ascend/cann/set_env.sh`（`cann-path` 为 CANN 安装目录）。
   - 再加载 msMemScope 采集环境：`source <path>/msmemscope/set_env.sh`（`path` 为 msMemScope 安装目录）。
   - 若使用 Python API，再加载 API 环境变量：`source msmemscope --load-api-env`；使用完毕后执行 `source msmemscope --unload-api-env` 清理以避免与其他工具冲突。

3. **Python API 四件套**：`config`（参数配置，未指定项取默认值）、`start`（开始数据采集）、`stop`（停止数据采集）、`step`（mstx 的 `step start` 固定信息 API），通过 `python example_api.py` 执行。

4. **CLI 一条命令等价封装**：CLI 入口直接以多开关方式指定采集与分析维度——`--events=alloc,free,access,launch`、`--level=kernel,op`、`--call-stack=c,python`、`--analysis=leaks,inefficient,decompose`、`--output=./output`、`--data-format=csv`，并以 `python ./example_cmd.py` 作为被分析脚本。

5. **示例代码位置**：`example/` 目录内提供两类示例——`example_api.py`（Python 路径）和 `example_cmd.py`（CLI 路径），需先 `cd ./example` 再执行。

6. **输出与后续分析入口**：采集结果落地为产出文件，由 [Output File Description](../user_guide/output_file_spec.md) 描述产出格式，由 [Memory Analysis](../user_guide/memory_analysis.md) 提供分析解读，工具参数细节见 [Memory Collection](../user_guide/memory_profile.md)。

---

## 【关键机制与数据】

**整体数据流（基于原文操作步骤推理）**：

```
PyTorch 脚本 / 用户代码
        │
        ▼
[msMemScope 采集层]  ← env: set_env.sh + --load-api-env
        │
        ├── events: alloc / free / access / launch
        ├── level : kernel / op
        └── call-stack: c / python
        │
        ▼
[产出文件 output]（默认 ./output, csv 格式）
        │
        ▼
[离线分析] →  leak / comparison / block monitor /
              usage breakdown / inefficient 识别
```

- 原文明确指出 msMemScope 的工作模式是 **"先采集内存事件 → 再基于事件做分析诊断"**，并将分析分为五类（leak、compare、block monitor、usage breakdown、inefficient identification）。
- 原文明确 Python API 与 CLI 在采集维度上是等价的（事件、层级、调用栈三类开关在 CLI 示例中均显式指定），区别仅在调用方式：API 嵌入脚本内，CLI 通过命令行参数外挂在任意 `python` 命令前。
- 性能数据 / 数值指标：原文未涉及。

---

## 【表格解读】

原文唯一的表格为 Python API 描述表，**逐字还原**：

| API  | Description                        |
| ------ | -------------------------------- |
| config | Sets parameters. For parameters not specified, use their default values.|
| start  | Starts data collection.                      |
| stop   | Stops data collection                      |
| step   | Fixed information API of `step start` for mstx.|

**逐行解读**：

- **`config`**：参数配置 API。其语义关键在于"未指定的参数使用默认值"，即调用者只需覆盖关心的字段，其余保持出厂默认，符合"快速跑通—按需调优"的渐进式使用范式。
- **`start`**：启动采集的入口。无入参描述，表明默认配置即可触发一次新的采集会话。
- **`stop`**：停止采集的入口，与 `start` 配对，构成最小生命周期单元（采集段 = `[start, stop]`），用户可围绕训练/推理的不同阶段插入多段采集。
- **`step`**:mstx `step start` 的固定信息 API，用于在采集过程中标记 `step start` 节点，便于按 step 维度做时间序列切片与对比，是把内存事件与训练 step / 调度阶段对齐的钩子。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档作为 Quick Start，处于文档树最浅层，与以下文档/模块形成上下游关系：

1. **前置依赖 → 安装文档**：[msMemScope Installation Guide](../install_guide/install_guide.md)
   - 本文 Step 1 中的 `<cann-path>` 与 `<path>` 安装目录说明把读者引向安装文档，是 Quick Start 的环境前提。

2. **执行载体 → 示例代码**：
   - [example_api.py](../../../example/example_api.py)：Python API 路径的最小可跑示例，与本文 `python example_api.py` 直接对应。
   - [example_cmd.py](../../../example/example_cmd.py)：CLI 路径的最小可跑示例，与本文 CLI 一行命令直接对应。

3. **参数细节 → 采集文档**：[Memory Collection](../user_guide/memory_profile.md)
   - 本文 CLI 示例中的 `--events / --level / --call-stack / --analysis / --output / --data-format` 六类开关的完整语义需查此文档。

4. **产出解读 → 输出与分析文档**：
   - [Output File Description](../user_guide/output_file_spec.md)：Step 4 中产出文件 schema/字段定义。
   - [Memory Analysis](../user_guide/memory_analysis.md)：Step 4 中 leak、inefficient、decompose、comparison、block monitor 五类分析能力的详细使用方法。

5. **能力面映射**：本文开篇列出的 5 大能力（leak / compare / block monitor / usage breakdown / inefficient）对应 CLI `--analysis=` 可选项中的 `leaks,inefficient,decompose`（其余能力在采集基础上由后续 Memory Analysis 文档展开）。

---

## 【使用方法】

**1. 环境变量（三段式加载）**

```bash
# 1) CANN 运行环境（以安装用户身份执行）
source <cann-path>/Ascend/cann/set_env.sh

# 2) msMemScope 采集环境
source <path>/msmemscope/set_env.sh

# 3) Python API 环境（仅在使用 API 时需要）
source msmemscope --load-api-env
# 使用完毕后清理，避免与其他工具冲突
source msmemscope --unload-api-env
```

**2. 进入示例目录**

```bash
cd ./example
```

**3. Python API 方式（推荐）**

- 脚本内可调用：`config` / `start` / `stop` / `step` 四个 API。
- 执行命令：
  ```bash
  python example_api.py
  ```

**4. CLI 方式**

- 一行命令同时指定采集维度与分析维度，并把 `./example_cmd.py` 作为被采集脚本：
  ```bash
  msmemscope --events=alloc,free,access,launch \
             --level=kernel,op \
             --call-stack=c,python \
             --analysis=leaks,inefficient,decompose \
             --output=./output \
             --data-format=csv \
             python ./example_cmd.py
  ```
- 配置项说明（按上述命令顺序）：
  - `--events`：要采集的内存事件类型，取值示例 `alloc,free,access,launch`。
  - `--level`：事件所属层级，取值示例 `kernel,op`。
  - `--call-stack`：调用栈采集语言，取值示例 `c,python`。
  - `--analysis`：要执行的分析项，取值示例 `leaks,inefficient,decompose`。
  - `--output`：产物输出目录，取值示例 `./output`。
  - `--data-format`：产物文件格式，取值示例 `csv`。
  - 末尾的 `python ./example_cmd.py` 为被采集的目标脚本。

**5. 查看产出**

- 采集结果文件位于 `--output` 所指目录（默认示例为 `./output`）。
- 文件 schema 解读：[Output File Description](../user_guide/output_file_spec.md)。
- 分析方法与解读：[Memory Analysis](../user_guide/memory_analysis.md)。

> 注：原文未涉及具体数值参数、默认参数取值、采集频率/采样率等量化指标；如需这些信息请参考 [Memory Collection](../user_guide/memory_profile.md)。
