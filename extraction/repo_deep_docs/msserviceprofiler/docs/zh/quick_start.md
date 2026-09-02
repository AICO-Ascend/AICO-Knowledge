# 服务化性能调优工具快速入门<a name="ZH-CN_TOPIC_0000002475358702"></a>

> 仓 `msserviceprofiler` · 路径 `docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/docs/zh/quick_start.md

# msserviceprofiler/docs/zh/quick_start.md 深度解读

---

## 【定位】

本文是 msServiceProfiler（服务化调优工具）的**快速入门指南**，面向已完成工具安装的用户，介绍如何在部署 MindIE Motor、vLLM-Ascend、SGLang 三类服务化推理框架前通过环境变量与 JSON 配置文件启用全链路性能采集，并通过解析命令与 MindStudio Insight 完成数据可视化与瓶颈定位。

---

## 【技术要点】

1. **环境变量驱动采集开关**：必须在服务进程启动**之前**通过 `export SERVICE_PROF_CONFIG_PATH="./ms_service_profiler_config.json"` 设置配置路径，否则采集能力不会生效；若路径无配置文件则工具自动生成默认配置（采集开关默认关闭）。

2. **多框架覆盖与差异化集成**：
   - **MindIE Motor**：原生启动方式即可，识别标志为输出 `[msservice_profiler]` 开头日志（如 `[ParseEnable:179] profile enable_: false`）。
   - **vLLM-Ascend**：按 vLLM 原生方式启动（如 `vllm serve Qwen/Qwen2.5-0.5B-Instruct &`）。
   - **SGLang**：因采用 `spawn` 多进程、主/调度/解码三进程独立 Python 解释器，**必须在三个入口文件**（`launch_server.py`、`scheduler.py`、`detokenizer_manager.py`）中分别调用 `register_service_profiler()`，并可选用 `PROFILING_SYMBOLS_PATH` 指定符号文件（默认 `ms_service_profiler/patcher/sglang/config/service_profiling_symbols.yaml`）。

3. **JSON 核心三字段**：原文给出的最小配置示例包含 `enable`、`prof_dir`、`acl_task_time` 三个字段，其中 `enable` 为必选总开关（`0` 关闭/`1` 开启），`prof_dir` 默认 `${HOME}/.ms_server_profiler`，`acl_task_time` 控制算子下发/执行耗时采集（默认 `0`）。

4. **动态重载机制**：`enable` 从 0→1 切换时，工具会重新加载配置文件中所有字段，实现不重启服务的动态控制，对应日志为 `[DynamicControl:407] Profiler Enabled Successfully!` 或 `[DynamicControl:411] Profiler Disabled Successfully!`。

5. **算子采集耗时代价**：`acl_task_time=1` 会占用设备性能导致采集数据失真，因此**仅在模型执行耗时异常时**开启；推荐采集时长 **3~5s**，默认算子采集等级为 **L0**，更高等级需查阅"服务化调优工具"完整参数。

6. **数据解析与多格式输出**：通过 `python3 -m ms_service_profiler.parse --input-path=${PATH}/prof_dir` 解析（依赖 `python>=3.10`、`pandas>=2.2`、`numpy>=1.24.3`、`psutil>=5.9.5`），解析后同时产出 **db / csv / json** 三种格式，分别用于 MindStudio Insight 可视化与基于 csv 的快速分析。

---

## 【关键机制与数据】

- **工作原理（配置 → 采集 → 解析 → 可视化）**：
  原文流程为：① 部署前 `SERVICE_PROF_CONFIG_PATH` 指向 JSON 配置 → ② 启动推理服务，工具读取配置并在 `prof_dir` 生成 `xxxx-xxxx` 形式的原始数据目录 → ③ 运行时通过修改配置 `enable` 字段动态启停采集 → ④ 调用 `ms_service_profiler.parse` 将原始数据转换为 db/csv/json → ⑤ 通过 MindStudio Insight 加载 db/json 进行可视化。

- **日志特征（原文）**：原文给出了 MindIE Motor 启动时的 4 条示例日志（`[msservice_profiler] [PID:225] [INFO] [ParseEnable:179] profile enable_: false`、`[ParseAclTaskTime:264] profile enableAclTaskTime_: false`、`[ParseAclTaskTime:265] profile msptiEnable_: false`、`[LogDomainInfo:357] profile enableDomainFilter_: false`），表明工具默认所有细粒度开关（ACL 算子时间、MSPTI、域过滤）均为 `false`。

- **目录约束（原文）**：原文 NOTE 明确指出多机部署时**不建议**将配置文件或数据存储路径放在网络共享目录，原因涉及数据写入存在额外网络/缓冲环节，可能导致非预期的系统行为。

- **性能开销（原文）**：`acl_task_time` 开启时占用设备性能，且算子采集数据量大，时间过长会占用磁盘并拉长解析时间，因此推荐 3~5s 集中采集。

---

## 【表格解读】

**原文表 1「参数说明」**（逐字还原）：

| 参数 | 说明 | 是否必选 |
| --- | --- | --- |
| enable | 性能数据采集总开关。取值为：<br>0：关闭。<br/>1：开启。<br/>即便其他开关开启，该开关不开启，仍然不会进行任何数据采集；如果只有该开关开启，只采集服务化性能数据。 | 是 |
| prof_dir | 采集到的性能数据的存放路径，默认值为 ${HOME}/.ms_server_profiler。<br/>该路径下存放的是性能原始数据，需要继续执行后续解析步骤，才能获取可视化的性能数据文件进行分析。<br/>在 enable 为 0 时，对 prof_dir 进行自定义修改，随后修改 enable 为 1 时生效；在 enable 为 1 时，直接修改 prof_dir，则修改不生效。 | 否 |
| acl_task_time | 开启采集算子下发耗时、算子执行耗时数据的开关，取值为：<br/>0：关闭。默认值，配置为 0 或其他非法值均表示关闭。<br/>1：开启。<br/>该功能开启时会占用一定的设备性能，导致采集的性能数据不准确，建议在模型执行耗时异常时开启，用于更细致的分析。<br/>算子采集数据量较大，一般推荐集中采集 3 ~ 5s，时间过长会导致占用额外磁盘空间，消耗额外的解析时间，从而导致性能定位时间拉长。<br/>默认算子采集等级为 L0，如果需要开启其他算子采集等级，请参见"服务化调优工具"的完整参数介绍。 | 否 |

**逐行解读**：

- **enable 行**：是唯一必选参数，扮演"总闸门"角色。语义关键点是"逻辑与"——其他开关（含 `acl_task_time`、域过滤等）即使开启，只要 `enable=0` 就**完全不会采集**；反之仅 `enable=1` 时，仅采集服务化层（调度、请求级）数据，不下钻算子层。值域为离散 0/1 二值。

- **prof_dir 行**：非必选但需要理解其"时序耦合"约束——**必须先改路径、再开采集**（`enable` 0→1 触发全字段重载）；若在采集进行中（`enable=1`）直接改 `prof_dir`，修改**不生效**。默认路径 `${HOME}/.ms_server_profiler` 下的子目录以 `xxxx-xxxx` 形式命名（原文中如 `${HOME}/.ms_server_profiler/xxxx-xxxx`），是工具运行时自动创建的一次性会话目录。原文还强调此处只存原始数据，必须经解析步骤才能可视化。

- **acl_task_time 行**：非必选，控制算子级耗时采集。其设计有两层权衡：① **采集代价**——开启会占用设备资源使采集数据失真，因此原文建议仅在"模型执行耗时异常"时启用；② **时长权衡**——算子数据量大，原文给出 **3~5s** 的集中采集窗口建议；③ **采集等级**——默认 **L0**，L0 之上还有其他等级，需查阅"服务化调优工具"完整文档。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **安装前置 →** [msserviceprofiler_install_guide.md](msserviceprofiler_install_guide.md)：原文在"前提条件"段明确要求在使用本文档之前必须先完成该安装指南，并验证服务可用性。
- **vLLM 专用指南 →** [vLLM_service_oriented_performance_collection_tool.md](vLLM_service_oriented_performance_collection_tool.md)：用于 vLLM-Ascend 的环境准备与服务验证，与本文 2.2 节互补。
- **SGLang 专用指南 →** [SGLang_service_oriented_performance_collection_tool.md](SGLang_service_oriented_performance_collection_tool.md)：用于 SGLang 的环境准备与服务验证，与本文 2.3 节互补。
- **MindIE Motor 安装 →** 外部链接 `https://gitcode.com/Ascend/MindIE-Motor/blob/master/docs/zh/user_guide/maintenance/build_motor_image_from_vllm_ascend.md`：MindIE Motor 部署与 MindIE 镜像构建的官方指南。
- **可视化后端 →** [MindStudio Insight 工具用户指南](https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/user_guide/overview.md) 与其"[服务化调优](https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/user_guide/service_optimization.md)"章节：解析后 db/json 文件需导入 Insight 才能完成框架/算子层瓶颈定位，是采集链路的下游消费方。
- **NOTE 指向的"服务化调优工具"完整参数文档**：原文多处提到 `enable`、`prof_dir`、`acl_task_time` 之外的字段以及其他算子采集等级（如 L0 之外）需查阅此文档，为本文的上层详细参考。

---

## 【使用方法】

**1. 环境变量（必做）**：
```bash
export SERVICE_PROF_CONFIG_PATH="./ms_service_profiler_config.json"
# SGLang 还需设置（可选）：
export PROFILING_SYMBOLS_PATH=service_profiling_symbols.yaml
```
- 必须在服务启动**之前**设置；拼写错误或不设置均不生效。

**2. SGLang 三个入口文件 patch（仅 SGLang 必需）**：
- `launch_server.py`：在所有 `import` 之后插入 `from ms_service_profiler.patcher.sglang import register_service_profiler; register_service_profiler()`。
- `scheduler.py`：在 `run_scheduler_process` 函数体最开头（`dp_rank = configure_scheduler_process(...)` 之前）插入相同代码（包在 `try/except ImportError` 内）。
- `detokenizer_manager.py`：在 `run_detokenizer_process` 函数体最开头（`kill_itself_when_parent_died()` 之前）插入相同代码（同样包 `try/except`）。
- 路径前缀 `/usr/local/pythonx.xx.xx/lib/pythonx.xx/site-packages` 由 `pip show sglang` 回显确定。

**3. 启动服务（按框架）**：
```bash
# MindIE Motor：按 MindIE 官方文档启动
# vLLM-Ascend：
cd ${path_to_store_profiling_files}
vllm serve Qwen/Qwen2.5-0.5B-Instruct &
# SGLang：
python3 -m sglang.launch_server --model-path=/Qwen2.5-0.5B-Instruct --device npu
```

**4. 配置采集（最小示例 JSON）**：
```json
{
  "enable": 1,
  "prof_dir": "${PATH}/prof_dir/",
  "acl_task_time": 0
}
```
字段说明见上"表格解读"。

**5. 数据解析（依赖 `python>=3.10`、`pandas>=2.2`、`numpy>=1.24.3`、`psutil>=5.9.5`）**：
```bash
# 通用形式
python3 -m ms_service_profiler.parse --input-path=${PATH}/prof_dir
# vLLM-Ascend / SGLang on NPU 推荐（默认 prof_dir 在 ~/.ms_server_profiler/xxxx-xxxx 下）：
cd ${HOME}/.ms_server_profiler/xxxx-xxxx
msserviceprofiler parse --input-path=./ --output-path output
# 或等价
python3 -m ms_service_profiler.parse --input-path=$PWD
```
解析完成后在执行目录下产出 db/csv/json 三种格式文件。

**6. 调优分析**：
- csv 格式可用于请求、调度等多维度快速分析。
- db/json 格式导入 MindStudio Insight 的"服务化调优"模块进行可视化。

## 图文联合解读

- `zh-cn_image_0000002478067012.png`: **图示内容**：Timeline 时间线视图，跨度约219.4ms，展示进程121095（含 KVCache-dp0.0/dpNone、batchFrameworkProcessing、continueBatching、http、instanceExecute、modelExec、preprocessBatch、sendExecuteMessage、workerRun 等）及进程121298/121300的并行调度；紫色三角标注PENDING/Queue、绿色三角标注RUNNING、蓝色标记STOP，色块长度直观呈现各阶段耗时与依赖时序。

**论证结论**：msServiceProfiler 能跨进程、跨线程并行捕获服务化推理框架调度（批处理、消息发送）与模型推理（instanceExecute/modelExec）的全链路时序与队列状态。

**与文档关系**：直接印证文档"全链路性能剖析，清晰展示框架调度、模型推理等环节表现"的核心论点，为快速定位瓶颈提供可视化依据。
