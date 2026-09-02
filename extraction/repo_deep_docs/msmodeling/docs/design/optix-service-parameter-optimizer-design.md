# 特性设计：服务化参数实测寻优功能

> 仓 `msmodeling` · 路径 `docs/design/optix-service-parameter-optimizer-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/optix-service-parameter-optimizer-design.md

# 设计文档深度解读：服务化参数实测寻优功能

## 【定位】

本文档描述 `optix` 服务化参数自动寻优子系统的端到端设计：把大模型推理服务（MindIE / vLLM）在上线前所需的大量手工调参工作，封装为以 **PSO 搜索 + 统一调度器 + 插件化 simulator/benchmark 接口** 为核心的自动化编排工具，并通过 `msmodeling optix` CLI 与 TOML 配置对外暴露能力。

---

## 【技术要点】

1. **CLI 与统一入口**：`msmodeling optix --engine {mindie|vllm} --benchmark_policy {ais_bench|vllm_benchmark} --config ./config.toml`，附加 `--backup`、`--load_breakpoint`；CLI 顶层由 `cli/main.py` 转发 `msmodeling inference` / `msmodeling optix`。
2. **PSO 连续空间 + 参数映射**：`PSOOptimizer` 只处理连续向量，由 `map_param_with_value()` 把粒子值转换为真实参数，覆盖 `int / float / bool / enum / range / ratio / factories / times / ternary_factories / ternary_times / share` 十一类 `OptimizerConfigField`，将服务框架特有约束剥离到映射层。
3. **Fitness 加权与惩罚**：默认权重 `w_gen=0.4`、`w_ft=0.2`、`w_pot=0.3`、`w_succ=0.1`，TTFT/TPOT 超出 SLO 使用指数惩罚，指标缺失或无效返回 `inf`；最终最佳参数策略在禁用/单开/双开 penalty 三种情形下分别退化为最大 generate_speed、最高吞吐、综合违约最小。
4. **调度与健康检查**：Scheduler 按 `params` + `target_field` 生成 `simulate_run_info`，在 `wait_start_time` 内轮询启动、`particles_time_out` 内监控运行；fatal 错误立即抛 `FatalError` 上抛，retryable 错误触发最多 **3 次**重试，未知错误按 fatal 处理。
5. **部署环境隔离与 fail-fast**：`resolve_deploy_context()` 生成运行上下文，`validate_deploy_stack()` 在创建 scheduler 前对 engine/benchmark 可执行文件做 fail-fast 校验，并将同一份剥离了 msmodeling venv 路径的 `RuntimeContext` / `deploy_env` 注入 simulator 与 benchmark。
6. **持久化与断点续跑**：`DataStorage` 将每轮参数、性能指标、fitness、错误信息、backup 路径写入 `result/store/data_storage_<timestamp>.csv`；可选 `result/back_up/` 备份服务配置、benchmark 输出和日志；支持历史 CSV 加载、重复参数跳过、fine tune 二次优化。

---

## 【关键机制与数据】

- **运行模式分层**：「配置模型 + 插件接口 + 调度器 + PSO 优化器」四层；配置层用 `pydantic-settings` 把 TOML 与环境变量合并为 `Settings`，插件层把推理服务抽象为 `SimulatorInterface`、把 benchmark 抽象为 `BenchmarkInterface`。
- **baseline → PSO → fine tune 三阶段**：先以默认配置跑 baseline 校验服务可启动并产出初始指标；PSO 做全局搜索；fine tune 对 top 候选做局部改进，最终按 SLO 与吞吐策略选择最佳。
- **优先级感知的 `ternary_factories` 修复**：用 `DecodeContext` 记录粒子编号、粒子数、迭代轮次；`priority_policy=fixed` 按显式优先级，`balanced` 按粒子编号/轮次切换以降低固定修复顺序带来的搜索偏置；修复两阶段——先固定高优先级只调低优先级，失败后再同时调整；最后 clamp 上下界，仍不满足整除约束则抛异常。
- **业务后处理映射**（原文）：
  - `maxPrefillBatchSize` 为 0 时强制设为 1；
  - `supportSelectBatch=false` 时把 `prefillTimeMsPerReq` 与 `decodeTimeMsPerReq` 置 0；
  - `CONCURRENCY` / `MAXCONCURRENCY` / `REQUESTRATE` 在 PSO 期间可固定，也可按 benchmark 结果二次调整。
- **插件依赖管理**（原文）：插件声明 `required_executable`，框架在构造插件前检查；插件自行创建部署子进程必须复用 `resolve_deploy_context()` 或 `build_deploy_env()`，并用 `materialize_command()` 解析显式命令路径，禁止直接传 `os.environ`。
- **Hook 检查点**（原文）：`ServiceHookPoint.STARTUP_POLLING`、`ServiceHookPoint.RUNTIME_MONITOR`、`BenchmarkHookPoint.RUNTIME_MONITOR` 三个 hook 点读取 simulator/benchmark 最新日志，按 TOML `[health_check.*]` 中配置的 fatal/retryable 模式生成 `HealthCheckResult`，匹配结果附带最新日志片段便于定位。
- **非目标**（原文）：不训练/改模型权重；不保证在缺 MindIE/vLLM/AISBench/NPU 环境下完成真实端到端压测；不替代 TensorCast/ServingCast 性能仿真；当前版本不提供 Web UI。

---

## 【表格解读】

### 表 1：OptimizerConfigField 字段说明

| 字段 | 说明 |
| -- | -- |
| `name` | 参数名称，同时用于 CSV 列名和环境变量名称 |
| `config_position` | 参数写入位置，支持 MindIE JSON 路径或 `env` |
| `min` / `max` | 搜索空间上下界 |
| `dtype` | 参数类型或派生规则 |
| `value` | 当前值 |
| `dtype_param` | 枚举列表、依赖字段名、乘除关系或派生规则配置 |
| `constant` | 固定值；固定字段不进入 PSO 维度 |

**逐行解读**：`name` 一名两用，使同一参数在结果 CSV 与运行期环境变量之间无歧义；`config_position` 用 JSON 路径或 `env` 区分 MindIE 静态配置改写与 vLLM 进程级环境变量注入；`min/max` 仅在非常数字段上有意义，是 PSO 搜索空间的边界；`dtype` 是参数语义的总开关，决定走哪种映射规则；`value` 既是 baseline 当前值，也是 PSO 粒子解码后回填的目标值；`dtype_param` 作为多用途载荷承载枚举列表/依赖字段/乘除关系等差异化配置；`constant=true` 让该字段在搜索时隐身，避免无意义维度污染 PSO。

### 表 2：PerformanceIndex 指标

| 指标 | 说明 |
| -- | -- |
| `generate_speed` | 输出 token 生成速度 |
| `time_to_first_token` | TTFT，单位为秒 |
| `time_per_output_token` | TPOT，单位为秒 |
| `success_rate` | 成功请求比例 |
| `throughput` | 请求吞吐 |

**逐行解读**：`generate_speed`（token/s）是核心收益指标，越高越优；`time_to_first_token` 与 `time_per_output_token` 用秒为单位，使其天然进入指数惩罚；`success_rate` 防止把崩溃/超时的高吞吐候选误判为最优；`throughput`（req/s）作为最终在多个满足 SLO 候选之间决胜的次级指标。

### 表 3：内置插件注册表（`register_ori_functions()`）

| 注册名 | 类型 | 实现类 | 说明 |
| -- | -- | -- | -- |
| `mindie` | simulator | `Simulator` | 修改 MindIE JSON 配置并启动 MindIE 服务 |
| `vllm` | simulator | `VllmSimulator` | 通过 `vllm serve` 启动服务 |
| `ais_bench` | benchmark | `AisBench` | 使用 `ais_bench` 运行 MindIE benchmark |
| `vllm_benchmark` | benchmark | `VllmBenchMark` | 使用 `vllm bench serve` 运行 vLLM benchmark |

**逐行解读**：前两行表明 simulator 层用「配置改写」与「命令行+环境变量」两种风格分别适配 MindIE 与 vLLM；后两行表明 benchmark 层也支持 AISBench（MindIE 主流压测）与 `vllm bench serve`（vLLM 自带压测）。四者均通过 `register_simulator` / `register_benchmarks` 注入到 CLI 的 `--engine` 与 `--benchmark_policy` 候选集合，构成当前版本的内置闭环。

### 表 4：Hook 点

| Hook 点 | 作用 |
| -- | -- |
| `ServiceHookPoint.STARTUP_POLLING` | 服务启动阶段检查服务日志 |
| `ServiceHookPoint.RUNTIME_MONITOR` | 服务运行阶段检查服务日志 |
| `BenchmarkHookPoint.RUNTIME_MONITOR` | benchmark 运行阶段检查 benchmark 日志 |

**逐行解读**：三个 hook 把健康检查切成启动期、服务运行期、压测运行期三类窗口，避免一种错误模式（如网络抖动）污染另一类模式（如 OOM）的判定；同名 `RUNTIME_MONITOR` 在服务侧与 benchmark 侧复用同一套日志匹配机制，减少重复配置。

### 表 5：数据模型与文件变更

| 路径 | 作用 |
| -- | -- |
| `pyproject.toml` | optix 独立包配置和 `msmodeling` 入口 |
| `cli/main.py` | CLI 顶层入口，转发 `msmodeling inference` / `msmodeling optix` |
| `optix/config.toml` | 默认配置模板 |
| `optix/config/config.py` | Settings、参数字段、性能指标、参数映射和派生字段规则 |
| `optix/config/custom_command.py` | vLLM/AISBench/vLLM benchmark 参数列表构造，不负责查找可执行文件 |
| `optix/deploy_env.py` | 运行上下文识别、部署环境隔离、命令物化与启动前部署栈校验 |
| `optix/optimizer/optimizer.py` | PSOOptimizer、fine tune 编排和主函数 |
| `optix/optimizer/scheduler.py` | 服务、benchmark、健康检查、重试和保存调度 |
| `optix/optimizer/store.py` | CSV 持久化、历史数据加载和最佳结果筛选 |
| `optix/optimizer/health_check.py` | 健康检查 hook 和错误分类 |
| `optix/optimizer/interfaces/` | simulator、benchmark、custom process 抽象接口 |
| `optix/optimizer/plugins/` | 内置 MindIE/vLLM simulator 与 AISBench/vLLM benchmark |
| `tests/regression/op…` | （原文截断）回归测试 |

**逐行解读**：文件组织严格遵循「配置 / 部署环境 / 优化器 / 调度 / 存储 / 健康检查 / 接口 / 插件 / 测试」的分层；`custom_command.py` 显式声明「不负责查找可执行文件」，把可执行文件解析职责收敛到 `deploy_env.py` 的 `materialize_command()`，避免命令查找分散；`interfaces/` 与 `plugins/` 分离保证新引擎/benchmark 通过注册而非修改核心代码接入。

---

## 【公式解读】

原文未给出严格的数学公式，但有六类参数映射规则式与一个 fitness 转换式，等价于伪代码层面的「公式」。逐字保留并解释如下：

- **ratio**：`actual = self_ratio * target.value`
  - 含义：当前字段值由「自身比值」乘以「目标字段当前值」得到，例如 `maxPrefillTokens = ratio * maxBatchSize`。
- **factories**：`actual = product / target.value`
  - 含义：分子是固定乘积，分母依赖另一个字段；常用于「整体吞吐固定、单维度反向求解」场景。
- **times**：`actual = product * target.value`
  - 含义：固定基数乘以目标字段当前值，用于线性放大类派生。
- **ternary_factories**：`actual = product / (field_a * field_b)`
  - 含义：三因子整除型派生，`product` 固定，分母是另外两个字段的乘积；支持 `min` / `max` / 整除约束，并在 `priority_policy` 控制下做两阶段修复 + clamp。
- **ternary_times**：`actual = product * field_a * field_b`
  - 含义：三因子乘积型派生，是 `ternary_factories` 的乘法对偶。
- **share**：`actual = target.min + target.max - target.value`
  - 含义：互补分配，常用于「两组共享一个总资源」场景——一个变大时另一个变小，但总和固定。
- **fitness（generate_speed 维度）**：`term = generate_speed_target / generate_speed`
  - 含义：把「越大越优」的 `generate_speed` 转成「越小越优」的 fitness 项；分母越小，项越大，对应生成速度越慢的候选被惩罚越重。

权重合并（原文）`w_gen=0.4, w_ft=0.2, w_pot=0.3, w_succ=0.1` 与上述项相乘后求和（TTFT/TPOT/success_rate 项通过指数惩罚实现），得到 `PerformanceTuner.minimum_algorithm()` 的输出；`inf` 表示「该候选非法，不应被选为最优」。

---

## 【关联】

- **`../RFC/rfc_optix_deploy_environment_isolation_zh.md`**（被引用两次，分别在「整体思路」与「核心流程」章节）：是本文档的强前置依赖。`optix/deploy_env.py` 提供的 `resolve_deploy_context()`、`validate_deploy_stack()`、`build_deploy_env()`、`materialize_command()` 等能力即来自该 RFC；CLI 在装配 simulator / benchmark 之前必经的「剥离 msmodeling venv 路径 + 子进程环境隔离 + engine/benchmark 可执行文件 fail-fast 校验」也由此 RFC 给出。
- **`../RFC/rfc_optix_optimizer_refactor_zh.md`**（文末内部链接信息中提及）：与本文档为同模块的姊妹 RFC，预期承担 `optix/optimizer/` 目录内 `optimizer.py` / `scheduler.py` / `store.py` 等核心代码的重构设计；二者共同构成 optix 子系统「环境隔离 + 优化器重构」的完整 RFC 集合。
- **与 msmodeling 工具自身关系**：本文档在「非目标」中明确区分——optix 面向**真实服务**的参数寻优编排，不替代 TensorCast / ServingCast 的性能仿真模型；同时 `cli/main.py` 与 `pyproject.toml` 让 optix 作为 msmodeling 的独立子包暴露 `msmodeling optix` 入口。

---

## 【使用方法】

**CLI 入口（原文）**：
```
msmodeling optix --engine mindie --benchmark_policy ais_bench --config ./config.toml
```
可选参数：`--backup`（启用 `result/back_up/` 备份）、`--load_breakpoint`（从历史 CSV 断点续跑）。`--engine` 可选 `mindie` / `vllm`，`--benchmark_policy` 可选 `ais_bench` / `vllm_benchmark`。

**TOML 配置覆盖范围（原文）**：优化参数（`OptimizerConfigField` 列表）、SLO（TTFT/TPOT/吞吐/成功率）、benchmark 命令、推理引擎命令、健康检查日志模式（`[health_check.*]` 中 fatal/retryable 模式）、输出目录、`[deploy].path_prefix` 或环境变量 `OPTIX_DEPLOY_PATH` 指定的部署路径前缀。

**运行时环境前置条件（原文）**：需准备 MindIE 或 vLLM 服务环境、模型路径、数据集路径以及 benchmark 工具；缺少 MindIE / vLLM / AISBench / NPU 运行时不保证完成真实端到端压测；预检失败时直接退出，不创建 Scheduler，也不启动或清理部署进程。

**自定义扩展（原文）**：新增引擎继承 `SimulatorInterface` 并实现 `base_url`、`update_command()`，按需重写 `update_config()` / `health()` / `stop()`；新增 benchmark 继承 `BenchmarkInterface` 并实现 `update_command()` 与 `get_performance_index()`；通过 `register_simulator(name, cls)` / `register_benchmarks(name, cls)` 注册；插件依赖 PATH 命令时声明 `required_executable`，自行创建部署子进程时必须复用 `resolve_deploy_context()` 或 `build_deploy_env()` 并经 `materialize_command()` 解析路径。

## 图文联合解读

- `plantuml-diagram__4_.png`: 图中以 `optix CLI` 为总入口，加载 TOML/环境变量，注入 PSO 优化器、Scheduler、benchmark 与 simulator 接口；优化器生成候选参数，调度器按策略启停服务并压测，采集性能指标后写入 CSV/日志。结论是配置、搜索、服务、评测、存储经接口解耦，形成可恢复、可追溯的自动寻优闭环，对应文档的 PSO、统一编排、错误恢复和断点续跑目标。
- `plantuml-diagram__3_.png`: 图展示 `optix` 流程：解析 CLI、注册插件并校验/覆盖 TOML，创建存储、调度器和 PSO 优化器；运行 baseline，失败则记录终止，成功后迭代生成、修复参数，调度服务与 benchmark，采集指标、计算 fitness 并保存 CSV；参数已评测时跳过。达到轮次后筛选 Top N、微调，按 SLO 选择最优配置并输出日志。流程体现“先基线、再搜索、逐轮留痕”的闭环，支撑统一编排、健康检查、PSO 寻优、断点续跑及结果可追溯。
