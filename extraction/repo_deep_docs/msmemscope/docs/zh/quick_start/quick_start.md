# **msMemScope快速入门**

> 仓 `msmemscope` · 路径 `docs/zh/quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmemscope/docs/zh/quick_start/quick_start.md

# msMemScope 快速入门文档深度解读

---

## 【定位】

这篇文档面向首次使用 msMemScope 的开发者，以一个简单的 PyTorch 脚本为例，引导用户完成"环境变量配置 → 进入示例目录 → 选择 Python 接口或命令行方式执行采集脚本 → 查看输出结果"的端到端最小可用链路，目的是让用户在最短时间内跑通工具并初步接触其内存事件采集与五类分析能力（泄漏检测、内存对比、内存块监测、内存拆解、低效内存识别）。

---

## 【技术要点】

1. **五项分析能力**（原文 §概述·简介）：msMemScope 在采集内存事件之上提供内存泄漏检测、内存对比、内存块监测、内存拆解、低效内存识别共 5 类分析能力，本文档是这些能力的入门入口。

2. **三套环境变量分层加载**（原文 §操作步骤·步骤1）：
   - **CANN 层**：`source <cann-path>/Ascend/cann/set_env.sh` —— 加载 Ascend CANN 基础环境。
   - **msMemScope 工具层**：`source <path>/msmemscope/set_env.sh` —— 启用内存数据采集能力。
   - **Python 接口层**：`source msmemscope --load-api-env` 与 `--unload-api-env` —— 仅在使用 Python API 时按需加载/卸载，避免与其他工具冲突。

3. **两种使用方式**（原文 §操作步骤·步骤3）：
   - **Python 接口方式**（推荐）：提供 4 个 API —— `config`（参数配置，未指定走默认值）、`start`（开始采集）、`stop`（结束采集）、`step`（mstx 的"step start"固化信息接口）。
   - **命令行方式**：通过 `msmemscope` 命令后跟工具参数 + 待执行脚本，直接对目标 Python 脚本插桩执行。

4. **命令行参数集合**（原文 §操作步骤·步骤3·命令行示例）：
   `--events=alloc,free,access,launch`（事件类型） + `--level=kernel,op`（粒度） + `--call-stack=c,python`（调用栈语言） + `--analysis=leaks,inefficient,decompose`（分析维度） + `--output-path=./output`（输出路径） + `--format=csv`（输出格式）。

5. **依赖框架**：示例基于 **PyTorch + Ascend for PyTorch 插件**，需根据 HUAWEI Ascend 官网下载页面完成安装；完整工具参数参考《内存采集》文档。

6. **输出文件与分析的文档指引**（原文 §操作步骤·步骤4）：输出文件结构与内存分析结果分别参见《输出文件说明》与《内存分析》文档，本文档不展开。

---

## 【关键机制与数据】

- **采集—分析两阶段架构**（原文 §概述·简介）：msMemScope 工作流先"采集内存事件"，再"基于采集事件开展 …分析"，即工具由"事件采集器"和"分析器"两层组成，本文档只覆盖如何把采集器跑起来，分析能力的具体使用交给 user_guide。

- **Python API 的 4 个核心调用语义**（原文 §操作步骤·步骤3·Python 接口表格）：
  - `config` → **配置**阶段，设置参数，未指定走默认值；
  - `start` → **采集开始**；
  - `stop` → **采集结束**；
  - `step` → 与 **mstx 的 "step start"** 对齐的固化信息接口，用于在训练循环中标记阶段边界。

- **Python 环境隔离机制**（原文 §操作步骤·步骤1.3）：`--load-api-env` 与 `--unload-api-env` 是配套动作，前者设置 Python API 所需环境变量、后者在使用完毕后清除，以"按需加载—按需卸载"的方式避免污染全局环境或与其他基于同一运行时的工具产生冲突。

- **命令行参数语义映射**（原文 §操作步骤·步骤3·命令行示例）：示例命令一次性传齐 6 个维度的参数，覆盖"采什么（events）、采多细（level）、栈追到哪（call-stack）、分析啥（analysis）、存到哪（output-path）、存成啥格式（format）"，原文未给出每个参数的可选枚举清单，标注"原文未涉及"留给《内存采集》文档补充。

- **示例代码定位**（原文 §操作步骤·步骤2）：示例代码统一放在仓库 `./example` 目录下，分别用 `example_api.py` 与 `example_cmd.py` 对应两种使用方式，作为新用户唯一被指引运行的脚本入口。

---

## 【表格解读】

**原文逐字还原**：

| 接口   | 功能说明                         |
| ------ | -------------------------------- |
| config | 设置参数，未指定的参数为默认值。 |
| start  | 开始采集。                       |
| stop   | 结束采集。                       |
| step   | mstx的"step start"固化信息接口。 |

**逐行解读**：

- **`config` 行**：`config` 是 4 个 API 中唯一具有"状态变更但不产生事件"的接口，作用是把后续采集行为所需的参数一次性写入；原文明确"未指定的参数为默认值"，说明该工具内部存在一套默认参数表，用户只需覆盖关心的维度（例如 `events`、`level`），其余走隐式默认 —— 这与命令行方式"必须显式传齐所有参数"的风格形成互补，让 Python API 更适合嵌入既有训练脚本做精细化控制。

- **`start` 行**：`start` 是事件采集生命周期的起点，对应原文"开始采集"的描述；语义上等价于命令行方式中"调用 `msmemscope` 命令后工具自动开始挂钩"的那一刻，但 `start` 把开关交还给用户脚本，从而支持"训练 N 个 epoch 才采集其中某一段"等场景。

- **`stop` 行**：`stop` 与 `start` 配对，关闭采集并触发落盘/分析；原文仅写"结束采集"，未细化是否同步进行泄漏/低效等分析，原文未涉及，留待《内存分析》文档说明。

- **`step` 行**：`step` 在 4 个接口中最特殊 —— 它不是采集生命周期接口，而是 **mstx 框架 "step start" 固化信息的对接点**，用于在 PyTorch 训练 step 边界处打点，使内存事件能与训练 step 对齐；这是 msMemScope 与 mstx 在训练循环层耦合的唯一入口。

---

## 【公式解读】

**原文无公式**（本文档为快速入门型 guide，未涉及任何数学表达式或伪代码算法，仅含 shell/Python 调用命令）。

---

## 【关联】

- **上游 / 安装入口**：[`../install_guide/install_guide.md`](../install_guide/install_guide.md) —— 文档 §环境准备 直接引用，作为 msMemScope 工具本体的安装前置条件。

- **示例代码源**：
  - [`../../../example/example_api.py`](../../../example/example_api.py) —— Python 接口方式的最小可运行示例，对应文档"通过 `python example_api.py` 执行"。
  - [`../../../example/example_cmd.py`](../../../example/example_cmd.py) —— 命令行方式的最小可运行示例，对应文档命令行示例中 `python ./example_cmd.py` 末尾位置。

- **下游 / 深入使用**：
  - [`../user_guide/memory_profile.md`](../user_guide/memory_profile.md) —— 文档 §操作步骤·步骤3 末尾以"完整工具参数参考"形式引用，承担命令行参数（`--events/--level/--call-stack/--analysis/--output-path/--format` 等）的枚举与默认值说明。
  - [`../user_guide/output_file_spec.md`](../user_guide/output_file_spec.md) —— 文档 §操作步骤·步骤4 中"输出文件 … 详细说明"的引用对象，承接示例运行后 `./output` 目录下 csv 等产物的字段定义。
  - [`../user_guide/memory_analysis.md`](../user_guide/memory_analysis.md) —— 同 §操作步骤·步骤4 中"内存分析"的引用对象，承接 `--analysis=leaks,inefficient,decompose` 三类分析能力的结果解读。

- **外部依赖**：文档 §环境准备 指向 HUAWEI Ascend 官网的 **Ascend for PyTorch 下载页**，作为 PyTorch + Ascend 插件链路的下载入口；CANN 安装包则通过 `set_env.sh` 路径在 §操作步骤·步骤1.1 中间接触达。

整体文档在"安装指南 → 快速入门（本文）→ 用户指南（采集/分析/输出）→ 示例代码"的文档树中处于 **第 2 层桥梁位置**：既把安装文档的成果（已安装的 msmemscope 环境）转化为可执行的命令序列，又把用户引向 user_guide 三篇深度文档以补齐参数与分析细节。

---

## 【使用方法】

**1. 启用方式（原文 §操作步骤·步骤1，原文有则写）**：

- CANN 环境变量：`source <cann-path>/Ascend/cann/set_env.sh`
- msMemScope 环境变量：`source <path>/msmemscope/set_env.sh`
- Python 接口专用加载：`source msmemscope --load-api-env`
- Python 接口专用卸载：`source msmemscope --unload-api-env`

**2. 配置项 / 命令（原文 §操作步骤·步骤3，原文有则写）**：

- **Python 接口方式**：在脚本内调用 4 个 API —— `config`（参数配置）、`start`（开始采集）、`stop`（结束采集）、`step`（mstx step start 固化信息）；未指定的 `config` 参数走默认值。脚本执行命令：

  ```bash
  python example_api.py
  ```

- **命令行方式**：一次性传入全部参数，格式为 `msmemscope <参数列表> python <目标脚本>`。原文给出的示例命令（6 个维度参数全开）：

  ```bash
  msmemscope --events=alloc,free,access,launch --level=kernel,op --call-stack=c,python --analysis=leaks,inefficient,decompose --output-path=./output --format=csv python ./example_cmd.py
  ```

  参数维度含义：采什么事件（events）、采多细的粒度（level）、调用栈语言（call-stack）、启用哪些分析（analysis）、输出路径（output-path）、输出格式（format）。完整可选枚举与默认值 **原文未涉及**，须查《内存采集》文档。

**3. 清理与冲突规避（原文 §操作步骤·步骤1.3）**：

- Python API 使用完毕后必须执行 `source msmemscope --unload-api-env` 清除接口层环境变量，避免与其他工具产生环境冲突 —— 这是文档中唯一明确的"善后"动作。
