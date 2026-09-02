# ms\_service\_metric 设计文档

> 仓 `msserviceprofiler` · 路径 `ms_service_metric/DESIGN.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/ms_service_metric/DESIGN.md

# ms_service_metric 设计文档 深度解读

---

## 【定位】

这篇文档描述从 `ms_service_profiler/patcher` 中提取并独立化的 metric 功能模块 `ms_service_metric` 的设计——一个**纯 Python 的独立库**，用于对 vLLM/SGLang 等推理服务的性能指标进行**动态可开关**的监控与采集，同时保留原项目对外接口与配置的兼容性。

---

## 【技术要点】

1. **从 patcher 抽取并独立发布**：将原 `ms_service_profiler/patcher` 中的 metric 功能抽离为独立 Python 库；目标之一是**纯 Python 部署**（不再依赖 C++），同时**保持功能、对外接口与配置兼容**。
2. **动态开关机制**：用**共享内存 + SIGUSR1 信号**替换原 C++ 回调控制方式，实现运行时启停 metric 采集（无需重启服务）。
3. **核心管理类 SymbolHandlerManager**：作为串联所有组件（Symbol、Handler、MetricsManager、SymbolWatcher、MetricConfigWatch）的中心，负责按配置动态加载/卸载 handler 和 symbol，并采用**批量 apply_hook** 而非每次 handler 变化都 reapplied，简化并发锁（仅保护 `_enabled` 与批量操作原子性）。
4. **Symbol × Handler 多对多管理**：Symbol 直接监听模块加载事件（**不通过 Manager 中转**）；同一符号多个 handler 用 **HookChain（双向链表）** 组织，支持在链表头部插入（`insert_at_head=True`），wrap 链采用**洋葱模型**多层调用。
5. **字节码级 Hook**：通过 `hook/inject.py`（字节码注入）+ `hook_helper.py`（函数替换辅助）实现对目标函数的无侵入 hook；并提供 `SymbolWatcher` 单例统一监听模块导入事件。
6. **优雅停止 (graceful stop)**：通过 `lock_patch` 属性决定停止时是否保留已 patch 的 handler；区分 `_stop_all_symbols` 与 `_stop_all_symbols_graceful` 两种停机路径，避免关闭/重启用之间出现 hook 状态不一致。
7. **多框架适配层**：`adapters/` 子目录对 **vLLM**（含 V1 metrics 配置 `v1_metrics.yaml`）与 **SGLang** 分别提供 `adapter.py` 入口与 `default.yaml` 配置；vLLM 还细分 `metric_handlers.py` 与 `meta_handlers.py` 两类 handler。

---

## 【关键机制与数据】

**工作原理 / 数据流**：

- **控制信号流**：外部 CLI (`control/cli.py` 对应命令 `ms-service-metric`) 写入共享内存并发送 SIGUSR1 → `MetricConfigWatch` 监听 → 触发 `SymbolHandlerManager._on_control_state_change(is_start, timestamp)` → 根据当前 `_enabled` 状态与时间戳判断「普通开启 / 重启 / 关闭 / 无操作」。
- **Symbol 加载流**：`SymbolWatcher`（单例）监听目标模块导入事件 → `Symbol.hook()` 触发 → 内部 `_apply_hook()` 利用 `HookChain` 将所有 handler 的 wrap 函数按洋葱模型串接 → 通过 `hook_helper` 完成函数替换（字节码注入由 `inject.py` 提供支持）。
- **Handler 生命周期管理**：`_add_handler` / `_remove_handler` / `_update_handler` 三类操作；移除 handler 时若 Symbol 已无 handler 则自动删除 Symbol；开启过程中以 `_updating` 标志暂停各 Symbol 的逐次 hook/unhook，全部配置就绪后再 `_apply_all_hooks()` 一次性应用。
- **Metrics 上报流**：通过 `get_metrics_manager()`（单例）汇总 metric 数据，handler 调用统一出口写入。

**原文要点摘录**（控制状态处理逻辑）：

> 关闭命令 (is_start=False): 如果当前已启用，根据 `lock_patch` 属性决定是否保留 handler；如果当前已禁用，无操作。
> 开启命令 (is_start=True): 如果当前已启用且时间戳相同→重复命令，无操作；如果当前已启用且时间戳不同→重启（关闭所有→重载配置→重新应用）；如果当前已禁用→普通开启（重载配置→应用）。

> Symbol 直接监听模块加载事件（不通过 SymbolHandlerManager 中转），根据 Manager 状态决定是否执行 hook/unhook。

> 批量 `apply_hook`，而不是每个 handler 变化都 reapply。

**性能相关约束**（原文措辞）：「**性能优先，简化 hook 函数内部逻辑**」——文档未给出具体基准数字，故无量化性能数据。

---

## 【表格解读】

### 表 1：`ms_service_profiler` vs `ms_service_metric` 特性对比（原文 §1.3）

| 特性 | ms_service_profiler | ms_service_metric |
| --- | :-: | :-: |
| Profiling | ✅ 支持 | ❌ 不支持 |
| Metrics   | ✅ 支持 | ✅ 支持 |
| 动态开关   | C++ 回调 | 共享内存+信号 |
| 独立部署   | ❌ 依赖 C++ | ✅ 纯 Python |

**逐行解读**：
- **Profiling 行**：拆分后 metric 模块**有意剔除 profiling 能力**，定位更聚焦在 metrics 子集；如需 profiling 需回到原 `ms_service_profiler`。
- **Metrics 行**：核心保留功能——这是抽取独立模块的根本价值所在，原项目有的 metric 能力须 1:1 保留。
- **动态开关行**：实现机制发生**实质变化**——从「C++ 回调」迁移到「共享内存 + 信号」，意味着控制链路完全 Python 化、可远程触达，但控制粒度/语义需在测试中验证兼容（参见 `test_config_compatibility.py`）。
- **独立部署行**：抽取后的关键收益——**纯 Python 部署**，不再有 C++ 编译/链接依赖，便于 pip 安装与跨平台分发。

### 表 2：项目目录结构（原文 §2）

该结构以代码块（`text`）形式呈现，非表格形式；按层次组织如下（**逐字保留目录树并补充解读**）：

- **`ms_service_metric/` 主包**
  - `core/`：四大核心类（`SymbolHandlerManager`、`Symbol`、`Handler`、`SymbolConfig`/`MetricConfigWatch`、Hook/Module 子模块）。
  - `handlers/builtin.py`：内置 handler（如 `default_handler`），作为适配层与业务逻辑之间的默认实现。
  - `adapters/vllm/` 与 `adapters/sglang/`：**框架适配层**，分别含 `adapter.py` 入口、YAML 配置；vLLM 额外有 `metrics_init.py`、`metric_handlers.py`、`meta_handlers.py`，并提供 `v1_metrics.yaml` 应对 vLLM V1 架构差异。
  - `metrics/`：`MetricsManager` + `meta_state.py` 元数据状态。
  - `utils/`：`expr_eval`（表达式求值，用于配置中动态表达式）、`function_context`、`shm_manager`（共享内存管理器，支撑动态开关）、`exceptions`、`logger`。
  - `control/cli.py`：暴露为 `ms-service-metric` 命令行工具，用于发送共享内存+信号以开启/关闭采集。
- **`tests/`**：含 `test_config_compatibility.py`（验证与原项目配置兼容）与 `tests/unit/` 单元测试，覆盖核心类与工具模块。

> 补充说明：原文为目录树而非参数表/性能表，故**无参数对比或性能数字表格**。

---

## 【公式解读】

**原文无公式**。文档未给出任何 LaTeX 公式或伪代码数学表达式；类方法签名（如 `_build_wrap_chain`）虽含参数列表，但属代码结构而非计算公式，不在此节展开。

---

## 【关联】

文档为独立模块的 design，未提供文末内部链接，但根据文中引用可识别以下关联关系：

- **上游来源**：从 `ms_service_profiler/patcher`（原项目）中抽取 metric 功能；与原项目保持**对外接口与配置兼容**（由 `tests/test_config_compatibility.py` 验证）。
- **框架适配下游**：
  - **vLLM** — 通过 `adapters/vllm/adapter.py` 接入，配置入口为 `adapters/vllm/config/default.yaml`；另支持 V1 引擎（`v1_metrics.yaml`）；handler 拆分到 `metric_handlers.py`（采集）与 `meta_handlers.py`（元数据）。
  - **SGLang** — 通过 `adapters/sglang/adapter.py` 接入，配置为 `adapters/sglang/config/default.yaml`。
- **核心模块间依赖**（基于单例与持有关系）：
  - `SymbolHandlerManager` 持有：`SymbolConfig`、`SymbolWatcher`（**单例**）、`get_metrics_manager()`（**单例**）、`MetricConfigWatch`。
  - `Symbol` 持有：`SymbolWatcher`、`SymbolHandlerManager`；并通过 `HookChain` 维护同一符号上的多 handler 调用链。
  - `HookChain`（双向链表）由 `hook/hook_chain.py` 提供，配合 `hook_helper.py` 与 `inject.py`（字节码注入）共同完成函数替换。
- **控制链路关联**：`utils/shm_manager.py`（共享内存） ↔ `MetricConfigWatch`（信号监听） ↔ `SymbolHandlerManager._on_control_state_change` ↔ 批量 hook/unhook；控制端 CLI 由 `control/cli.py` 提供（命令名 `ms-service-metric`）。
- **测试关联**：`tests/unit/` 中 `test_handler.py` / `test_hook_chain.py` / `test_symbol_config.py` / `test_symbol_watcher.py` / `test_metrics_manager.py` 等分别对应核心类的单元覆盖；`test_config_compatibility.py` 对应与 `ms_service_profiler` 的兼容性保证。

---

## 【使用方法】

- **启用方式**：通过命令 `ms-service-metric`（由 `ms_service_metric/control/cli.py` 提供）向目标进程写入共享内存并发送 SIGUSR1 信号以触发开启/关闭；无需重启服务。
- **配置项**：
  - **通用配置**：`SymbolConfig`（`core/config/symbol_config.py`）定义 handler 列表与符号路径（`module_path:attr_path` 形式，由 `Symbol.__init__` 中 `symbol_path.split(':', 1)` 拆解）。
  - **动态开关开关量**：`lock_patch`（Symbol/Handler 级别属性）——关闭命令到达时，若 `lock_patch=True` 则保留已 patch 的 handler。
  - **框架配置**：
    - vLLM：`adapters/vllm/config/default.yaml`；vLLM V1：`adapters/vllm/config/v1_metrics.yaml`。
    - SGLang：`adapters/sglang/config/default.yaml`。
  - **动态表达式**：配置中可通过 `utils/expr_eval.py`（`ExprEval`）求值。
- **初始化 API**（按文档伪代码）：
  - `SymbolHandlerManager.initialize(config_path=None, default_config_path=None)`：加载配置文件（可显式指定主配置与默认配置路径）。
  - `SymbolHandlerManager.shutdown()`：关闭管理器。
  - 查询接口：`is_enabled()` / `is_updating()`。
- **测试运行**：测试由 `tests/conftest.py` 提供 pytest fixture 与配置；具体用例详见 `tests/test_config_compatibility.py` 与 `tests/unit/` 下各 `test_*.py`。

> 注：文档未给出 `pip install` 或 `python -m ms_service_metric` 的具体命令模板；`__main__.py` 作为命令行入口存在，但具体 CLI 形参原文未展开。

---

*注：原文在 `_build_sync` 方法签名处截断，本次解读仅基于已提供文本，未对截断后内容做臆测。*
