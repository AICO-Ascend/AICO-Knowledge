# 项目目录

> 仓 `msserviceprofiler` · 路径 `docs/zh/dir_structure.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/docs/zh/dir_structure.md

# msserviceprofiler 项目目录结构文档深度解读

## 【定位】
本文档以树状结构呈现 msserviceprofiler（MindStudio 推理服务化性能数据采集工具）整个代码仓库的目录布局，标明每个目录/文件的职责注解，帮助开发者快速理解项目的模块划分与文件组织关系。

---

## 【技术要点】

1. **依赖目录分层**：项目根下设 `3rdparty/` 目录统一管理外部依赖，又进一步分为昇腾 AI 计算平台（`ascend/`，含 `acl`、`mspti`、`mstx` 三类头文件）和 OpenTelemetry 可观测性框架（含 `proto/` 中的 `collector/trace`、`common`、`resource`、`trace` 等 Protobuf 定义）。
2. **C++ 基础采集层**：以 `cpp/` 为核心，含 `include/msServiceProfiler/`（`Profiler.h`、`ServiceProfilerInterface.h`、`ServiceTracer.h`、`Tracer.h`、`Config.h`、`msServiceProfiler.h`、DBExecutor 子目录）与 `src/` 实现，构成"采集配置解析—Trace 追踪—数据落盘"完整链路。
3. **Python 数据处理层**：`ms_service_profiler/` 目录下提供 `mstx.py`、`parse.py`、`profiler.py`、`trace.py`、`analyze.py`、`compare.py`、`split.py` 等模块，覆盖"采集 → 解析 → 分析 → 对比 → 拆解"全流程；另有 `parse_helper/`、`pipeline/`、`plugins/`（含 `sort_plugins.py`）、`processor/`、`task/`、`tracer/`、`utils/`（含 `check/`、`secur/` 下的 `constraints/` 与 `utils/`，以及 `trace_to_db.py`）支撑模块。
4. **插件化框架适配**：`patcher/` 子目录实现 hook 采集，针对 `vllm/`（含 `v0/` 与 `v1/` 两版 `handlers/`、`service_profiler.py` 入口）和 `sglang/`（含 `handlers/`、`service_patcher.py` 入口）两类推理框架分别注入采集点；同级提供 `config/` 目录下的 `custom_handler_example.py` 与 `hooks_example.yaml` 示例。
5. **专家建议与自动寻优模块**：顶层 `msservice_advisor/`（含 `advisor.py` 与 `profiling_analyze/`）负责给出专家建议，`ms_serviceparam_optimizer/`（含 `pyproject.toml`）负责自动寻优。
6. **测试体系**：`test/` 目录下含 `CMakeLists.txt`、`run_st.py`、`run_st.sh`、`run_ut.sh`，以及 `fuzz/`（含 `FuzzMain.cpp`、`run_fuzz.sh`、`manager/` 下 `${name}_fuzz.cpp`）和 `st/`（C++ 端 `cpp/test.cpp`、Python 端含 `conftest.py`、`analyze/`、`checker/`、`collect/`）分层测试结构。

---

## 【关键机制与数据】

原文为纯目录树文档，未涉及具体的数据流图、性能指标、运行时机制描述。仅能根据目录命名推断出以下工作原理性的归口（标注"原文:"）：

- **原文:** `cpp/include/msServiceProfiler/` 下 `Profiler.h`、`ServiceProfilerInterface.h`、`Tracer.h`、`ServiceTracer.h` 的并列存在，说明项目在 C++ 端同时提供"数据采集"与"Trace 追踪"两条对外接口路径。
- **原文:** `cpp/include/msServiceProfiler/DBExecutor/` 子目录被单独列出，表明"采集数据落盘"在 C++ 端是独立模块。
- **原文:** `3rdparty/opentelemetry/proto/` 下 `collector/trace`、`common`、`resource`、`trace` 四类 Protobuf 定义同时存在，说明 OpenTelemetry 接入覆盖"采集端—资源—通用—追踪"完整协议面。
- **原文:** `ms_service_profiler/utils/trace_to_db.py` 与 `cpp/DBExecutor/` 形成跨语言对照，C++ 端落盘 + Python 端 `json→db` 转换是文档明确的两条落盘路径。
- **原文:** `patcher/vllm/handlers/` 同时存在 `v0/` 与 `v1/` 子目录，表明 vLLM 框架至少需要同时兼容两个版本进行 hook 注入。

原文未给出任何性能数据、吞吐量、延迟、采集开销等数字指标。

---

## 【表格解读】

**原文无表格**（原文仅以 `text` 代码块形式呈现一棵目录树注释，不含任何参数表、性能对比表、配置项表格）。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档为项目根目录概览，未提供任何内部超链接，但根据目录并列关系可梳理以下关联结构：

- **C++ 采集 ↔ Python 处理链路**：`cpp/`（采集，含 `Profiler.h`、`Tracer.h`、`ServiceProfilerInterface.h`、`DBExecutor/`）为上游数据源，`ms_service_profiler/` 下 `parse.py`、`trace.py`、`analyze.py`、`compare.py`、`split.py` 以及 `utils/trace_to_db.py` 为下游解析/处理链路。
- **第三方可观测性协议 ↔ Trace 模块**：`3rdparty/opentelemetry/`（含 `proto/collector/trace`、`trace`、`resource`、`common`）直接服务于 `cpp/include/msServiceProfiler/ServiceTracer.h`、`Tracer.h` 以及 `ms_service_profiler/trace.py`、`tracer/`。
- **昇腾依赖 ↔ 采集入口**：`3rdparty/ascend/include/`（`acl/`、`mspti/`、`mstx/`）支撑 `cpp/src/` 中对昇腾 NPU 的数据采集；`ms_service_profiler/mstx.py` 命名与之呼应。
- **patcher ↔ 推理框架**：`ms_service_profiler/patcher/vllm/`（`service_profiler.py` + `handlers/v0/`、`handlers/v1/`）与 `patcher/sglang/`（`service_patcher.py` + `handlers/`）并列，分别对接 vLLM 与 SGLang 两个推理引擎的 hook 注入。
- **advisor / optimizer ↔ analyze**：`msservice_advisor/advisor.py` 与 `profiling_analyze/` 子目录属于"专家建议"层，消费 `ms_service_profiler/analyze.py` 的扩展分析结果；`ms_serviceparam_optimizer/` 独立提供自动寻优能力。
- **文档 ↔ 实现**：`docs/zh/cpp_api/`（含 `serving_tuning/`、`trace_data_monitoring/`，其下均含 `${api_name}.md`、`macro_definitions.md`、`sample_code.md`、`public_sys-resources/`、`serving_tuning.md`）对应 `cpp/include/msServiceProfiler/` 中的接口；`docs/zh/python_api/context/` 对应 `ms_service_profiler/` 下 Python 模块。
- **测试 ↔ 源码**：`test/` 下 `cpp/test.cpp` 对应 `cpp/src/`、`run_st.py`/`run_st.sh`/`run_ut.sh` 对应 `ms_service_profiler/` 各 Python 模块、`fuzz/` 对应 C++ 端健壮性测试。

---

## 【使用方法】

**原文未涉及**。本文档为静态目录结构说明，不包含任何启用步骤、配置项、命令行参数或运行指南。
