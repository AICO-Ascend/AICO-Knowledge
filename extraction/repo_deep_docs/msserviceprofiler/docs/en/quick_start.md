# Quick Start Guide for msServiceProfiler<a name="ZH-CN_TOPIC_0000002475358702"></a>

> 仓 `msserviceprofiler` · 路径 `docs/en/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/docs/en/quick_start.md

# msserviceprofiler Quick Start Guide — 一体化深度解读

## 【定位】

这篇文档是 msserviceprofiler（MindStudio 推理服务化性能数据采集工具）的快速上手指南，旨在解决推理服务框架性能调优时"看不见、调不动、瓶颈难定位"的黑盒问题，通过端到端性能采集让用户清晰看到框架调度与模型推理的关键耗时，从而快速定位性能瓶颈并提升服务质量。

---

## 【技术要点】

1. **核心定位是端到端性能采集**：msServiceProfiler 提供 framework scheduling 与 model inference 的端到端性能数据采集能力，帮助用户在请求量上升导致响应变慢、不同设备性能差异等场景下定位问题（原文: "provides end-to-end performance profiling"）。
2. **支持的推理服务框架（原文: 三类）**：MindIE Motor、vLLM-ascend、SGLang。其它类型服务框架不在本次快速入门范围。
3. **启用方式（关键机制）**：必须在**服务进程启动之前**设置环境变量 `SERVICE_PROF_CONFIG_PATH`，变量名拼错或未提前设置都无法启用采集功能。
4. **配置路径必须含 JSON 文件名**：`SERVICE_PROF_CONFIG_PATH` 的值必须是 JSON 文件路径（如 `./ms_service_profiler_config.json`），控制 profile 数据采集行为；若路径不存在，工具会自动生成一份默认配置（采集功能默认关闭）。
5. **初始化成功标志（原文日志示例）**：MindIE Motor 启动完成前会输出以 `[msservice_profiler]` 为前缀的日志（例如 `[ParseEnable:179] profile enable_: false`），表明 msServiceProfiler 已完成初始化；配置不存在时会自动落盘生成配置文件并打印 `Successfully saved profiler configuration to: ...`。
6. **SGLang 需要手工 patcher 接入（首次集成）**：在 `/usr/local/python3.11.13/lib/python3.11/site-packages/sglang/launch_server.py` 的所有 import 语句之后插入 `from ms_service_profiler.patcher.sglang import register_service_profiler; register_service_profiler()`（路径以 `pip show sglang` 实际输出为准）；vLLM-ascend 与 MindIE Motor 则无需此类手工 patch。
7. **多节点部署禁忌（原文明确警告）**：多节点部署时，不要把配置文件或其指定的数据存储路径放在共享目录（如网络共享盘），否则可能因数据写入走网络/缓冲而非直写盘，引发非预期行为或结果。
8. **数据采集时长建议（原文: 3 至 5 秒）**：操作子（acl_task_time）采集会产生大量数据，一般建议采集 3–5 秒；采集时间越长，磁盘占用越大、解析时间越长，越不利于排障。

---

## 【关键机制与数据】

### 工作原理 / 数据流

1. **配置下发阶段**（原文: Configure Environment Variables）：用户导出环境变量 `SERVICE_PROF_CONFIG_PATH`，指向一份 JSON 配置文件。该 JSON 至少控制三件事：① 是否启用采集（enable）；② profile 元数据/原始数据落盘路径（prof_dir）；③ 是否开启算子下发与执行耗时采集（acl_task_time）等其它设置。
2. **服务启动阶段**（原文: Start Services）：msServiceProfiler 在服务进程内被加载并完成初始化。MindIE Motor 通过日志前缀 `[msservice_profiler]` 标识；vLLM-ascend 在 `${path_to_store_profiling_files}` 目录下导出 `SERVICE_PROF_CONFIG_PATH` 后直接用 vLLM 原生方式启动；SGLang 首次需要在 `launch_server.py` 注册 patcher 再启动。配置不存在时自动生成默认 JSON（默认 enable = false）。
3. **数据采集阶段**（原文: Collect Data）：服务部署成功后，再次通过修改 `SERVICE_PROF_CONFIG_PATH` 指定的 JSON 字段来精准控制采集行为。`enable` 一旦为 1，工具会从服务收到请求那一刻起持续采集直到请求结束，`prof_dir` 下的目录体积会持续增长，因此建议**只在关键时间段内**开启采集。
4. **数据使用阶段（原文提示）**：`prof_dir` 存放的是**原始 profile 数据**，需要"后续解析步骤"才能得到可视化的 profile 数据文件以供分析——该文档本身未给出解析命令（截止到本节，文档在 "Whenever the `en" 处中断）。

### 性能数据 / 原文有的具体数字

- 默认 profile 数据目录：`${HOME}/.ms_server_profiler`（原文明确写出）。
- 操作子采集建议时长：**3 至 5 秒**（原文: "advised to collect data for 3 to 5 seconds"）。
- 默认算子采集等级：`L0`（原文明确写出）；更高等级需查阅完整参数说明。
- 操作子采集开销：原文仅定性描述为"引入性能开销，可能导致采集数据不准"，**未给出具体百分比**。

---

## 【表格解读】

### Table 1：Parameters（采集配置参数表，逐字还原）

| Parameters | Description | Mandatory (Yes/No) |
| --- | --- | --- |
| enable | 全局启用或禁用 profile 数据采集。取值：<br>`0`：禁用。<br>`1`：启用。<br>若该参数为 `0`，即使其它参数启用了对应功能，也不会采集任何数据。若仅将该参数设为 `1`，则仅采集 serving profile 数据。 | Yes. |
| prof_dir | 采集到的 profile 数据落盘路径。默认值为 `${HOME}/.ms_server_profiler`。<br>该路径存放原始 profile 数据，需经后续解析步骤才能得到可用于分析的、可视化的 profile 数据文件。<br>若 `enable` 为 `0` 时修改 `prof_dir`，变更会在后续 `enable` 切到 `1` 时生效；若 `enable` 为 `1` 时修改 `prof_dir`，变更不生效。 | No |
| acl_task_time | 启用或禁用算子下发耗时与算子执行耗时的采集。可选值：<br>`0`：禁用（默认）。设为 `0` 或任何其它非法值均视为禁用。<br>`1`：启用。<br>启用该功能会引入性能开销，可能导致 profile 数据不准；若需进一步细粒度分析，建议仅在模型执行出现异常时再开启。<br>算子采集会产生大量数据。一般建议采集 3 至 5 秒；采集时间越长，磁盘占用越大，解析时间越长，不利于排障。<br>默认算子采集等级为 `L0`。若需启用其它算子采集等级，请参阅 "msServiceProfiler" 的完整参数说明。 | No |

**逐行释义：**

- **enable（必填）**：整个采集链路的总开关。设 0 时，其它参数即使放开也不会真正采集数据；设 1 时默认至少采集 serving profile。`Mandatory = Yes` 意味着 JSON 中该字段必须有明确值。
- **prof_dir（非必填）**：原始数据落盘路径，留空时使用 `${HOME}/.ms_server_profiler`。**生效时机敏感**：必须在 `enable=0` 状态下修改，下次 `enable=1` 才会按新路径落盘；运行期热改无效——这是文档明确指出的生效时序约束。
- **acl_task_time（非必填）**：算子粒度耗时采集开关，引入性能开销，原文建议在模型异常时按需开启，并配合 3–5 秒短时采集。默认等级 L0，更高等级需查完整参数文档。

---

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的数学公式）。

---

## 【关联】

依据文档中出现的链接与上下文，msServiceProfiler 在整个工具链中的位置如下：

### 1. 上游前置依赖（必须先满足）

- **服务框架已部署并验证可用**：必须先安装对应的推理服务框架，并能用官方示例脚本或 API 跑通一次推理请求，否则后续 profiling 无对象可观测。
  - **MindIE Motor**：依赖 *MindIE Installation Guide*（外部链接：`gitcode.com/Ascend/MindIE-Motor/blob/master/docs/zh/README.md`）。
  - **vLLM-ascend**：依赖 *vLLM Service Profiler User Guide*（即同仓 `vLLM_service_oriented_performance_collection_tool.md`）与官方 vLLM-ascend 安装文档。
  - **SGLang**：依赖 *SGLang Service Profiler User Guide*（即同仓 `SGLang_service_oriented_performance_collection_tool.md`）与官方 SGLang 安装文档。

### 2. 内部链接（与本文档同仓）

- `msserviceprofiler_install_guide.md#constraints`：本文档 *Prerequisites* 章节显式要求读者**先阅读**该链接中的"Constraints"章节，了解使用限制后再继续——也就是说，安装指南的 Constraints 是本文档的前置条件。
- `msserviceprofiler_install_guide.md`（即 *msServiceProfiler Installation Guide*）：作为总安装指南，是本文档（Quick Start）的配套文档。

### 3. 文档内部的纵向引用

- 文档中 `[3. Collect Data](#3-collect-data)` 锚点指向本文档第 3 节，说明本快速入门是一份自包含的闭环手册。

### 4. 文档范围之外（明确不在本文档内）

- 原文档 NOTE 明确指出：本文档只是快速入门，**操作、API、参数、字段的详细说明**参见 *msServiceProfiler documentation*（更完整的总文档，本文档未给出该文档链接，需另行查找）。

---

## 【使用方法】

### 启用步骤（按文档 Procedure 顺序）

**步骤 1 — Configure Environment Variables（必做，原文强调"必须"在服务部署之前）**

```bash
export SERVICE_PROF_CONFIG_PATH="./ms_service_profiler_config.json"
```

- 变量值必须包含 JSON 文件名（指向控制 profile 数据采集的配置文件）。
- 若路径下不存在配置文件，工具会自动生成一份默认配置（默认 `enable = false`，采集关闭）。

**步骤 2 — Start Services（按框架选择各自小节）**

- **2.1 MindIE Motor**：按 *MindIE Installation Guide* 启动推理服务；若 `SERVICE_PROF_CONFIG_PATH` 配置正确，部署完成前会出现 `[msservice_profiler]` 前缀的日志，表示初始化成功；配置文件不存在时自动生成并落盘。
- **2.2 vLLM-ascend**：进入存放 profiling 文件的目录，设置 `export SERVICE_PROF_CONFIG_PATH=ms_service_profiler_config.json`，然后用 vLLM 原生方式启动，例如：
  ```bash
  vllm serve Qwen/Qwen2.5-0.5B-Instruct &
  ```
- **2.3 SGLang**（首次需手工集成 patcher）：编辑 SGLang 的 `launch_server.py`（路径以 `pip show sglang` 实际输出为准），在所有已有 import 语句之后插入：
  ```python
  from ms_service_profiler.patcher.sglang import register_service_profiler
  register_service_profiler()
  ```
  然后启动服务：
  ```bash
  python -m sglang.launch_server \
      --model-path=/Qwen2.5-0.5B-Instruct \
      --device npu
  ```

**步骤 3 — Collect Data（运行时通过修改 JSON 控制）**

修改 `SERVICE_PROF_CONFIG_PATH` 指向的 JSON 文件（原文示例列出三个字段）：

```json
{
  "enable": 1,
  "prof_dir": "${PATH}/prof_dir/",
  "acl_task_time": 0
}
```

- `enable=1` 后，从服务收到请求那一刻起开始采集直到请求结束；建议仅在关键时间段开启。
- 修改 `prof_dir` 必须确保 `enable=0`，否则变更不生效。
- `acl_task_time=1` 时建议采集 3–5 秒，避免长时间占用磁盘与解析时间。

### 配置项汇总（Table 1 中已逐字给出，此处简述）

- `enable`：0/1，必填，总开关。
- `prof_dir`：路径，非必填，默认 `${HOME}/.ms_server_profiler`，存放原始 profile 数据。
- `acl_task_time`：0/1，非必填，默认 0，开启算子粒度耗时采集，建议 3–5 秒短采，默认等级 L0。

### 禁忌事项（原文明确禁止）

- **多节点部署**：不要把配置 JSON 或 `prof_dir` 指向的网络共享盘等共享目录（数据写入可能走网络/缓冲而非直写盘，会引发非预期行为）。原文未涉及。
- **运行期热改 `prof_dir`**：`enable=1` 时改 `prof_dir` 不生效。

### 后续步骤（原文被截断）

文档在 "Whenever the `en" 处中断，关于 profile 数据采集完成后的解析、可视化、清理等步骤原文未给出，需参考同仓其它文档（如安装指南的完整参数说明与上层 msServiceProfiler 文档）——本文档未涉及。

## 图文联合解读

- `zh-cn_image_0000002478067012.png`: **1) 图示内容：** 时间线（Timeline）视图，横轴为时间（00:00.045–00:00.195，约219.4ms），纵轴按进程与事件分层：主进程 121095 含 KVCache-dp0.0（橙）与 KVCache-dpNone（紫）两段并行条，以及 http 子模块的 instanceExecute、modelExec、preprocessBatch、sendExecuteMessage、workerRun 等彩色色块，并标注 PENDING/Queue/RUNNING/STOP 触发点；下方为工作进程 121300、121298。

**2) 技术结论：** msServiceProfiler 能按进程/事件维度端到端可视化推理请求全链路时序、各阶段耗时与进程间通信依赖。

**3) 与文档论点关系：** 直观佐证"清晰呈现框架调度与模型推理性能、帮助快速定位瓶颈"的核心主张。
