# 特性设计：吞吐寻优多硬件展示与终端 ASCII Plot

> 仓 `msmodeling` · 路径 `docs/design/multi_device_throughput_optimizer_terminal_plot.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/multi_device_throughput_optimizer_terminal_plot.md

# 一体化深度解读：吞吐寻优多硬件展示与终端 ASCII Plot

## 【定位】

本文档定义 `throughput_optimizer` 的**多硬件横向对比 + 终端 ASCII 曲线展示**能力：让一次寻优命令同时跑多 `DeviceProfile`，并按"PD混部 / PD分离 / PD配比"三种模式分别输出表格与终端散点图，以解决当前结果仅是性能列表、不直观且无法横向对比多硬件的痛点。

---

## 【技术要点】

1. **CLI 多硬件入口**：新增 `--device DEVICE [DEVICE ...]`（`nargs="+"`），由 `cli/utils.py:check_device_targets()` 统一校验（去重、保序、空白校验、设备画像通信网格与 `--num-devices` 适配校验），未传时回填默认 `["TEST_DEVICE"]` 以兼容旧单设备行为。
2. **执行编排双模块拆分**：把展示职责集中到两个 service 模块 —— `optimizer_summary.py`（结果过滤、最佳配置提取、PrettyTable 表格输出）与 `optimizer_curve_plots.py`（终端曲线绘制、多设备执行编排、跨硬件汇总调度）。
3. **曲线仅单设备开启**：判定条件 `plot_curves_allowed = len(device_targets) == 1`，多设备模式**只输出表格、不输出 scatter 图**；单设备下每个 `profile_name` 完成 sweep 后立即绘制终端曲线。
4. **三种模式统一的图对象**：PD混部画 `Throughput vs Concurrency` 与 `Throughput vs TPOT (ms)` 双图；PD分离按 `data_config` 区分 Prefill（`ttft_limits is not None and tpot_limits is None`）与 Decode（`tpot_limits is not None and ttft_limits is None`），各自再画两张图；PD配比**只画 Decode 侧 TPS 双图**（不再输出 P/D QPS 四张）。
5. **过滤规则区分表格与曲线**：表格用 TTFT/TPOT SLA 过滤后排序选最优；曲线**不再用 SLA 过滤**，仅剔除 OOM 点（`memory_left_gb <= 0` 或 `device_memory_available_gb <= 0`），`ttft_limit`/`tpot_limit` 参数保留仅为接口兼容。
6. **绘图实现细节**：使用 `plotext` 模块级共享画布，marker 为实心圆点 `●`，按 `parallel` 轮转色板区分；图尺寸由内部常量 `_TERMINAL_PLOT_COLS = 128` 与 `_TERMINAL_PLOT_ROWS = 38` 控制；坐标完全重合的点会轻微错开，坐标轴按当前图内点自动留白；假设调用过程为串行单线程（与 CLI 顺序执行一致）。

---

## 【关键机制与数据】

### 工作原理与数据流

CLI 主流程串起三层：`throughput_optimizer.main` → `check_device_targets()` 校验 → 计算 `plot_curves_allowed` → `run_multi_device_loop()` 遍历 `device_targets`，对每个 profile 临时写回 `args.device` 并 `ParallelRunner(args).run_agg()` 或 `.run_disagg()` 跑寻优 → 每个 profile 完成后调 `res.report_final_result(args, silent=False)` 输出单设备结果 → 多硬件模式下从结果抽一行摘要 → 若 `plot_curves_allowed` 为真则立即绘制终端曲线 → 全跑完后 `render_cross_hardware_summary()` 输出跨硬件摘要。

### 跨硬件摘要数据结构

跨硬件汇总按四种类型分桶收集，存入 `MultiDeviceComparisonRows`：

```text
aggregation
pd_ratio
disagg_prefill
disagg_decode
```

每桶对应一种"行提取方法 + 排序指标"组合（PD配比排序指标为 `balanced_qps`，其余均为 `throughput_tps`）。

### 跨硬件表格渲染的"四张表"

`render_cross_hardware_summary()` 在 `len(device_targets) <= 1` 时直接返回；多设备时先 `render_hardware_profile_comparison(device_targets)` 输出设备画像参数表，再按模式分别输出：

- PD混部：`render_cross_device_comparison()`
- PD分离：`render_cross_hardware_disagg_prefill()` 与 `render_cross_hardware_disagg_decode()`
- PD配比：`render_cross_hardware_pd_ratio()`

对应模式下无有效行时只记 warning，不中断主流程。

### PD分离模式分流判据

| 子模式 | 判据 |
|--------|------|
| Prefill | `ttft_limits is not None and tpot_limits is None` |
| Decode | `tpot_limits is not None and ttft_limits is None` |

### PD分离汇总表 QPS 计算（原文给出明确公式，见【公式解读】）

PD配比最佳点选择：先 `ttft_p`/`tpot_d` SLA 过滤 → 对每个 `(parallel_p, parallel_d)` 组合仅保留 `balanced_qps` 最优项 → 按四舍五入到 2 位小数的 `balanced_qps` 再去重 → 按 `balanced_qps` 降序返回。

### PD配比表格 vs 曲线口径差异

原文：表格输出仍保留 `p_qps`、`d_qps`、`balanced_qps` 等 PD 指标；终端 plot 仅展示 Decode 侧 `token/s` 与 Concurrency/TPOT 的关系，不再输出 P/D QPS 曲线。

### 性能数据

原文未提供任何性能基准数据（无 TPS/QPS/耗时测量值），仅指出多设备模式"总耗时与设备数近似线性相关"。

---

## 【表格解读】

### 表 1：修订记录

| 日期 | 修订版本 | 修改描述 | 作者 | RFC 文档 |
| -- | -- | -- | -- | -- |
| 2026-05-09 | 1.0 | 初稿：多 `--device` 对比、`plotext` 曲线、拆解/PD 比例路径说明 | — | 本文档 |
| 2026-05-19 | 1.1 | 同步当前实现：PD配比仅输出 TPS 双图；多 device 仅输出跨硬件汇总表 | — | 本文档 |
| 2026-05-19 | 1.2 | 术语统一：聚合→PD混部，拆解→PD分离，PD 比例→PD配比 | — | 本文档 |

**逐行解读**：
- 1.0 版确立三大设计骨架：多 `--device` 入参、`plotext` 终端曲线、拆解/PD比例的并行绘图路径。
- 1.1 版反映"实际实现收敛"：PD配比不再画四张 QPS 图，只保留 Decode 侧 TPS 双图；多设备模式回归到纯表格输出。
- 1.2 版是术语标准化：`聚合→PD混部`、`拆解→PD分离`、`PD 比例→PD配比`，与中文术语对齐。

### 表 2：模块职责

| 模块 | 当前职责 |
|------|------|
| `cli/inference/throughput_optimizer.py` | 参数解析、模式校验、设备校验、调用执行入口 |
| `cli/utils.py` | `check_device_targets()` device参数校验 |
| `serving_cast/service/optimizer_curve_plots.py` | 终端 ASCII 曲线、单/多设备执行编排、跨硬件汇总调度 |
| `serving_cast/service/optimizer_summary.py` | 单设备结果过滤与打印、跨硬件表格渲染、PD分离/PD配比结果整理 |

**逐行解读**：
- CLI 入口文件聚合了三类职责：解析（argparse）、校验（模式/设备）、编排（调用执行入口）；其本身不绘制曲线或渲染表格。
- `cli/utils.py` 收口设备参数校验，CLI 主流程不必再关心去重/默认/网格适配等细节。
- `optimizer_curve_plots.py` 是本次设计的核心 service：单设备 sweep 散点绘图、多设备顺序执行编排、跨硬件汇总调度都在这里。
- `optimizer_summary.py` 是"数据整形+表格"层：负责 SLA 过滤、去重、排序、PrettyTable 渲染；与 `optimizer_curve_plots.py` 形成**直接依赖**而非仅数据耦合。

### 表 3：跨硬件摘要行提取方法

| 模式 | 行提取方法 | 排序指标 |
|------|------|------|
| PD混部 | `collect_comparison_row()` | `throughput_tps` |
| PD分离 Prefill | `collect_disagg_prefill_row()` | `throughput_tps` |
| PD分离 Decode | `collect_disagg_decode_row()` | `throughput_tps` |
| PD配比 | `collect_pd_ratio_comparison_row()` | `balanced_qps` |

**逐行解读**：
- PD混部、PD分离 Prefill、PD分离 Decode 三类的排序指标统一为 `throughput_tps`，体现"以吞吐为王"的横向对比哲学。
- PD配比单独用 `balanced_qps`，因为 PD 比例场景下 Prefill/Decode 两端必须协同（不能只看 Decode TPS），所以选取平衡后的 QPS 作为对比基准。
- 每个模式都有专门的行提取方法，说明"每模式最佳行"的判定逻辑各异，跨硬件汇总桶需要分模式独立采集。

### 表 4：单设备结果输出逻辑

| 模式 | 输出逻辑 |
|------|------|
| PD混部/PD分离 | `_get_agg_disagg_final_out()` |
| PD配比 | `_get_pd_ratio_final_out()` |
| `--dump-original-results` | 打印原始或过滤后的 DataFrame |

**逐行解读**：
- PD混部与 PD分离共用 `_get_agg_disagg_final_out()`，因为两者都使用 TTFT/TPOT SLA 过滤 + `token/s` 排序选最优的同一条路径。
- PD配比走 `_get_pd_ratio_final_out()`，对应其 `ttft_p`/`tpot_d` SLA 过滤 + `balanced_qps` 去重排序的独立路径。
- `--dump-original-results` 是一个调试/验收开关，用于打印 DataFrame 原始或过滤后形态，便于复现与问题定位。

### 表 5：单设备曲线模式分发表

| 模式 | 入口 |
|------|------|
| PD混部 | `plot_concurrency_curves_from_optimizer_summaries()` |
| PD分离 | `plot_disagg_terminal_curves()` |
| PD配比 | `plot_pd_ratio_terminal_curves()` |

**逐行解读**：
- 三个模式各自拥有独立的绘图入口函数，由 `_plot_single_device_optimizer_curves()` 统一分派。
- PD混部入口名 `plot_concurrency_curves_from_optimizer_summaries()` 暗示其从 `OptimizerSummary.get_summary_df()` 合并多 profile 结果后再绘图。
- PD分离与 PD配比入口命名带 `terminal_curves` 后缀，强调其是终端 ASCII 输出，与 PD混部入口命名风格略有差异，但实际渲染目标一致（plotext 终端画布）。

---

## 【公式解读】

### 公式 1：PD配比 Decode 侧 TPS

```text
token/s = concurrency_d / tpot_d * 1000
```

**符号含义**：
- `concurrency_d`：Decode 侧的并发数（请求级并发，由 sweep 配置产生）。
- `tpot_d`：Decode 侧的 TPOT（time per output token），单位为毫秒。
- `1000`：毫秒→秒的换算系数。
- `token/s`：每秒生成的 token 数（Decode 吞吐）。

**作用**：将 Decode 侧的 TPOT（ms/token）转化为吞吐视角（token/s），便于在终端图上以"吞吐量"作为纵轴对比不同 `parallel` 配置下的并发与时延-吞吐关系。

### 公式 2：PD分离汇总表 Prefill QPS

```text
QPS (req/s) = concurrency / ttft * 1000
```

**符号含义**：
- `concurrency`：Prefill 侧请求并发数。
- `ttft`：Time To First Token，单位为毫秒。
- `1000`：毫秒→秒换算系数。
- `QPS (req/s)`：Prefill 侧每秒能处理的请求数。

**作用**：在跨硬件 PD分离 Prefill 汇总表中呈现 Prefill 服务吞吐能力，是与 Decode 侧 `tpot * output_length` 分母的口径差异体现——Prefill 用首 token 时延，Decode 用"每 token × 输出长度"作为单请求总时延近似。

### 公式 3：PD分离汇总表 Decode QPS

```text
QPS (req/s) = concurrency / (tpot * output_length) * 1000
```

**符号含义**：
- `concurrency`：Decode 侧请求并发数。
- `tpot`：每输出 token 的时延（ms/token）。
- `output_length`：每个请求的输出 token 长度。
- `tpot * output_length`：单个请求在 Decode 阶段的总占用时延近似（ms/req）。
- `1000`：毫秒→秒换算系数。
- `QPS (req/s)`：Decode 侧每秒能处理的请求数。

**作用**：Decode 阶段需要逐 token 生成，整请求时延与 `output_length` 线性相关，因此分母用 `tpot * output_length` 来近似单请求服务时间，从而得到合理的 QPS 估值用于跨硬件对比。

---

## 【关联】

本文档是 `throughput_optimizer` 模块的纯展示层增强，与其上下游关系如下：

- **上游（参数与执行）**：
  - `cli/inference/throughput_optimizer.py`：CLI 入口，把 `--device` 多值与 `--dump-original-results` 等开关传透到 service 层。
  - `cli/utils.py:check_device_targets()`：通用工具函数，承担设备校验职责，是 CLI 入口的依赖。
  - `ParallelRunner(args)`：寻优执行器，由 `run_multi_device_loop()` 在编排循环中按设备/模式调用 `.run_agg()` 或 `.run_disagg()`。

- **平行 service 模块**：
  - `optimizer_summary.py`：本文档明确指出它与 `optimizer_curve_plots.py` 之间是**直接依赖关系**（不再是纯 DataFrame 间接耦合），跨硬件表格渲染与 PD配比/PD分离结果整理都在该模块。
  - `optimizer_curve_plots.py`：承载终端 ASCII 曲线、单/多设备执行编排、跨硬件汇总调度。

- **行提取方法**：`OptimizerSummary` 暴露 `collect_comparison_row()` / `collect_disagg_prefill_row()` / `collect_disagg_decode_row()` / `collect_pd_ratio_comparison_row()` 四个方法，对应四种 `MultiDeviceComparisonRows` 桶（`aggregation` / `pd_ratio` / `disagg_prefill` / `disagg_decode`），是跨硬件汇总的数据源。

- **测试**：
  - 已有 UT：`serving_cast/tests/ut/test_service/test_optimizer_summary.py`，覆盖 `OptimizerSummary` 初始化/读写、early stop、PD混部输出、PD配比模式判定与去重。
  - 缺失 UT：`test_optimizer_curve_plots.py` —— 终端曲线入口分发、OOM 过滤、缺列降级、单/多设备分支切换、`run_multi_device_loop()` 与 `render_cross_hardware_summary()` 的协同，目前主要依赖代码阅读与手工验收。

- **DFX 边界**：本文档明确未新增网络接口、未新增文件落盘；输出仅为 stdout 表格 + stdout ASCII 曲线 + warning/exception 日志；曲线绘制路径对 `ImportError` 与绘图异常有降级处理，缺列或过滤后为空时曲线入口返回 `False` 并记 warning，不中断寻优主流程。

---

## 【使用方法】

### CLI 参数

```bash
--device DEVICE [DEVICE ...]
```

`nargs="+"`，至少一个值，重复值去重并保留首次出现顺序。

### 典型用法

```bash
# 单设备（自动触发 sweep ASCII 图）
--device AtlasA2

# 多设备横向对比（仅输出跨硬件汇总表，不输出 scatter 图）
--device AtlasA2 Atlas800I
```

### 默认行为

- **不传 `--device`**：`args.device` 为 `None`，由 `check_device_targets()` 补全为 `["TEST_DEVICE"]`，与原有单设备默认行为保持一致。
- **显式写出 `--device` 但无值**：CLI 在参数解析阶段直接报错退出。
- **值含空白字符串**：在校验阶段判定为非法并退出。

### 模式开关（与原有 CLI 一致）

- `--disagg`：进入 PD分离模式。
- 不传 `--disagg`：按 PD混部处理。
- PD配比：由 `OptimizerSummary` 通过 `data_config` 自动判定，CLI 上不需要额外开关（原文未提供显式开关名）。
- `--dump-original-results`：打印原始或过滤后的 DataFrame，配合上述任一模式使用。

### 启用终端曲线的条件

- 必须是单设备场景（`plot_curves_allowed = len(device_targets) == 1`）。
- 必须是 sweep 场景。
- 多设备场景下曲线自动关闭，仅输出硬件画像表与跨硬件汇总表。
