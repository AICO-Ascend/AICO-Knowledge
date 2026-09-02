# Feature Design

> 仓 `msmodeling` · 路径 `docs/design/ut_refactor.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/ut_refactor.md

# msmodeling UT 重构设计文档深度解读

---

## 【定位】

这篇文档解决 `msmodeling` 测试体系中 **UT 与 ST 职责不清、整体执行耗时偏高、慢用例集中、测试代码与功能验证重复、部分路径触发权重下载导致缓存膨胀** 的工程问题，通过统一的目录分层、入口拆分、覆盖率守护与缓存治理机制，**只重构测试体系、不新增建模能力、不扩展精度采集链路**。

---

## 【技术要点】

1. **三层目录分层（替代 pytest marker 表达层级）**
   - `tests/smoke/` = UT，`tests/regression/` = UT/ST，`tests/benchmark/` = ST
   - 层级判定依据 **目录位置**，marker 仅保留三类横切约束：`nightly`（长时编译）、`npu`（硬件依赖）、`network`（需访问 Hub）
   - 模型精度守护放 `tests/benchmark/models/`，算子精度守护放 `tests/benchmark/ops/perf_database/`
   - 增量 CI 仅覆盖满足 `not npu and not nightly and not network` 的 smoke/regression 用例，benchmark 永不进增量路径

2. **五个 shell 入口脚本的拆分执行模型**
   - `run_smoke.sh` / `run_regression.sh` / `run_benchmark.sh` / `run_nightly.sh` / `run_ci_gate.sh`
   - 本地开发者默认跑完整 smoke + regression；CI PR 增量选择被 **隔离在 `run_ci_gate.sh`** 中，读取由 nightly 维护的外部 `test_map` 文件
   - benchmark 与 nightly 脚本始终跑全量

3. **覆盖率与守护机制**
   - nightly phase 1 收覆盖率时同时刷新 `test_map`，按 **60% 行 / 40% 分支** 阈值上报行+分支总计
   - `run_ci_gate.sh` 强制 `test_map` 策略与 pytest 通过/失败；通过率、耗时漂移、慢用例数通过 nightly JUnit XML 与飞书通知跟踪

4. **慢用例与冗余治理**
   - 通过 `pytest -n auto` 并行、session/module 级 fixture、参数化、用例合并
   - 与 nightly `duration_sec` 及 pytest `--durations=20` 输出对比；不为收集基线重跑完整 regression

5. **集中化的权重与 Hub 访问控制**
   - 本地未设置 `MSMODELING_OFFLINE` 时允许 Hub 访问；CI 设置 `MSMODELING_OFFLINE=1` 禁止隐式下载
   - 缓存目录限定在仓库根的 `.msmodeling_cache`
   - 会话结束后可通过 `MSMODELING_TEST_WEIGHTS_PRUNE=1` 清理权重分片

6. **可量化的整改目标**
   - 现状基线：混合基线总耗时 960 秒，行覆盖率 74%，分支覆盖率 61.8%，15 个用例 > 300 秒
   - 整改目标：增量 CI gate 约 180 秒、单次完整 regression ≤ 300 秒、完整 nightly ≤ 480 秒、全量相对基线提速 ≥ 50%、> 300 秒用例 ≤ 3 个

---

## 【关键机制与数据】

### 整改前后量化对比（原文）

| 指标 | 现状（基线） | 整改目标 |
|------|------|------|
| 混合基线总耗时 | 960 秒（原文） | 全量提速 ≥ 50%（即 ≤ 480 秒级别，与 nightly ≤ 480 秒对应） |
| 单次完整 regression | — | ≤ 300 秒（原文） |
| 增量 CI gate | — | ≈ 180 秒（原文） |
| 行覆盖率 | 74%（原文） | 阈值 60%（原文） |
| 分支覆盖率 | 61.8%（原文） | 阈值 40%（原文） |
| 超过 300 秒的用例数 | 15 个（原文） | ≤ 3 个（原文） |

### 工作原理（原文）

- **层级表达方式**：从"marker 表达层级"切换为"目录表达层级"；marker 退化为只标注三类横切约束
- **增量 CI 选择机制**：`run_ci_gate.sh` 通过外部 `test_map`（由 nightly job 维护）决定本次 PR 跑哪些 smoke/regression 用例；`build_test_map` 收集作用域被硬编码为 `not npu and not nightly and not network`，覆盖 `tests/smoke/` 与 `tests/regres[sion]`
- **pytest 全局 addopts**：`addopts = "-m 'not npu and not nightly and not network'"`，默认排除三类 marker，对应 nightly 中提到的"排除 npu/nightly/network"
- **覆盖率采集**：`tool.coverage.run` 配置 `parallel = true` 与 `branch = true`（开启并行模式与分支覆盖）
- **通知链路**：通过 nightly JUnit XML 报告与 Feishu 通知上报通过率、耗时漂移、慢用例数

### 测试分层与目录映射（原文）

- 模型级精度守护 → `tests/benchmark/models/`
- 算子级精度守护 → `tests/benchmark/ops/perf_database/`
- 长时编译路径 → 加 `@pytest.mark.nightly`，并在 `tests/smoke/` 写对应 smoke 守护
- NPU 依赖 → 加 `@pytest.mark.npu`，被所有 `run_*.sh` 入口排除
- network 依赖 → 加 `@pytest.mark.network`，默认排除，仅 nightly phase 2c 在 `tests/` 范围内跑

### 共享资产布局（原文）

- 共享模型配置：`tests/assets/model_config/`（含 `num_hidden_layers_override=1` 的本地小配置示例）
- 可复用 builder 与断言：`tests/helpers/`
- 工具链 UT：`tests/regression/scripts/helpers/`（镜像 `scripts/helpers/`）
- 新用例指南：`tests/README.md`
- LLM 辅助生成测试 prompt：`tests/SKILL.md`

---

## 【表格解读】

### 表 1：Directory Semantics（目录语义）

| Directory | Layer | Semantics | Typical Content | Local / Full CI | Incremental CI |
|------|------|------|----------|------|------|
| `tests/smoke/` | UT | Minimum viable paths; PR guard for `@pytest.mark.nightly` compile paths | Core API reachability, lightweight compile, local tiny configs, CLI smoke | `run_smoke.sh` | Selected via `run_ci_gate.sh` when mapped |
| `tests/regression/` | UT / ST | Module function and integration verification; default destination for new cases | Graph compilation, pass transforms, ServingCast, CLI, Web UI, toolchain UT | `run_regression.sh` | Selected via `run_ci_gate.sh` when mapped |
| `tests/benchmark/` | ST | Precision and performance baselines | `models/` model-level cases, `ops/perf_database/` operator-level cases | `run_benchmark.sh` | Never selected incrementally |
| All three layers | ST | Nightly guardianship | Long compile paths, precision baselines, mapping refresh | `run_nightly.sh` | — |

**逐行解读：**
- 第 1 行 `tests/smoke/` 是 UT 层，承担最小可行路径以及对 nightly 编译路径的 PR 守护，内容是核心 API 可达性、轻量编译、本地小配置与 CLI 冒烟，本地/CI 全量由 `run_smoke.sh` 驱动；增量 CI 仅在 `test_map` 命中时被 `run_ci_gate.sh` 选中。
- 第 2 行 `tests/regression/` 是 UT/ST 混合层，是新用例默认落点，覆盖图编译、pass 变换、ServingCast、CLI、Web UI 与工具链 UT；执行由 `run_regression.sh` 负责，增量 CI 仅在 `test_map` 命中时由 `run_ci_gate.sh` 选中。
- 第 3 行 `tests/benchmark/` 是 ST 层，承载精度与性能基线（含 `models/` 模型级与 `ops/perf_database/` 算子级），由 `run_benchmark.sh` 全量执行；**永不被增量 CI 选中**——这是与前两层的关键区别。
- 第 4 行 "All three layers" 表示 nightly 守护跨越三层，承担长编译路径、精度基线与 `test_map` 映射刷新，由 `run_nightly.sh` 驱动；增量 CI 列标注 `—`，即 nightly 不进增量路径。

### 表 2：Marker Semantics（marker 语义）

| Marker | Semantics | Relationship with Directory |
|--------|------|------------|
| None | Default case; layer is determined by directory | Most cases in all three directories carry no marker |
| `nightly` | Long-running compile or optimization paths | Allowed under `tests/smoke/` or `tests/regression/`; excluded from ci_gate mapped/guard wave; included in local full smoke/regression, changed-test ci_gate wave (`-m not npu`), and nightly phase 2a |
| `npu` | Requires NPU hardware | Excluded from all `run_*.sh` entry scripts |
| `network` | Requires live model Hub access (HuggingFace/ModelScope) | Excluded by default and from all UT entry scripts; run only in nightly phase 2c over `tests/` |

**逐行解读：**
- 第 1 行 "None" 是默认态，层级由目录决定，三层目录下多数用例都不打 marker——这与"目录表达层级"的核心原则一致。
- 第 2 行 `nightly` 用于长时编译或优化路径，允许出现在 `tests/smoke/` 或 `tests/regression/` 下；它被 ci_gate 的 mapped/guard 波次排除，但被本地完整 smoke/regression 包含，且被 changed-test ci_gate 波次（`-m not npu`）包含，最终在 nightly phase 2a 运行。
- 第 3 行 `npu` 表示需 NPU 硬件，被所有 `run_*.sh` 入口排除（即任何本地/CI shell 入口都不会主动跑）。
- 第 4 行 `network` 表示需访问 HuggingFace/ModelScope，默认排除且被所有 UT 入口排除，仅在 nightly phase 2c 于 `tests/` 全域运行。

### 表 3：Smoke Guard for Nightly Compile Paths（nightly 编译路径的 smoke 守护分层）

| Layer | Role | Typical Scope |
|-------|------|---------------|
| `tests/smoke/` | PR-level basic guard | Local tiny configs in `tests/assets/model_config/` with `num_hidden_layers_override=1`, or remote `config.json` only; asserts `build_model`, `ModelRunner.run_inference`, or CLI exit code |
| `tests/regression/` + `@pytest.mark.nightly` | Full compile regression | Full model IDs, multi-shape sweeps, fused-op event counts, bandwidth tables, ModelScope load paths |

**逐行解读：**
- 第 1 行 smoke 层是 PR 级基础守护，作用域是 `tests/assets/model_config/` 中的本地小配置（参数 `num_hidden_layers_override=1`）或仅远程 `config.json`；断言点收敛在 `build_model`、`ModelRunner.run_inference` 或 CLI 退出码——目的就是用最小代价验证编译路径可达。
- 第 2 行 regression 层加 `@pytest.mark.nightly` 后承担完整编译回归，作用域包括全量模型 ID、多 shape 扫描、融合算子事件计数、带宽表、ModelScope 加载路径——这是 nightly phase 2a 才跑的全量重活。

### 表 4：Smoke 与 Nightly 用例映射示例

| Smoke case | Guards nightly |
|------------|----------------|
| `tests/smoke/test_compile_paths_smoke.py::test_compile_with_mtp_tokens_deepseek` | `MtpNightlyTestCase`, `MtpEpNightlyTestCase` |
| `tests/smoke/test_compile_remote_models_smoke.py::test_compile_qwen3_moe` | `GmmPassTestCase`, `SwiGLUFusionPassNightlyTestCase` |
| `tests/smoke/test_model_runner_compile_smoke.py::test_model_runner_compile_deepseek` | `TestTextGenerateNightly`, `PerfAnalysisNightlyTestCase` |
| `tests/smoke/test_throughput_optimizer_smoke.py::TestThroughputOptimizerSmoke.test_vl_model_image_args` | `TestThroughputOptimizerNightly` VL paths |

**逐行解读：**
- 第 1 行：`test_compile_with_mtp_tokens_deepseek` 这条 smoke 用例守护 `MtpNightlyTestCase` 与 `MtpEpNightlyTestCase` 两条 nightly 用例——smoke 用 MTP token 路径的低成本试跑替代 nightly 中的对应全量回归。
- 第 2 行：`test_compile_qwen3_moe` 守护 `GmmPassTestCase` 与 `SwiGLUFusionPassNightlyTestCase`——smoke 覆盖 Qwen3 MoE 远程编译入口，nightly 覆盖 GMM pass 与 SwiGLU 融合 pass 的完整回归。
- 第 3 行：`test_model_runner_compile_deepseek` 守护 `TestTextGenerateNightly` 与 `PerfAnalysisNightlyTestCase`——smoke 验证 ModelRunner 编译 DeepSeek 路径可达，nightly 跑文本生成与性能分析全量。
- 第 4 行：`TestThroughputOptimizerSmoke.test_vl_model_image_args` 守护 `TestThroughputOptimizerNightly` 的 VL 路径——smoke 用 VL 模型图像参数跑通入口，nightly 跑完整吞吐优化器回归。

### 表 5：pytest 配置（pyproject.toml 片段）

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
markers = [
  "nightly: do_compile=True large model cases, only run in nightly",
  "npu: requires NPU hardware",
  "network: requires live model Hub access (HuggingFace/ModelScope); excluded by default, run in nightly",
]
addopts = "-m 'not npu and not nightly and not network'"
testpaths = ["tests"]

[tool.coverage.run]
parallel = true
branch = true
```

**逐行解读：**
- `pythonpath = ["."]`：把仓库根加入 Python 模块搜索路径，使测试可直接 import 项目代码。
- `markers` 三条声明：`nightly`（`do_compile=True` 的大模型用例，仅 nightly 跑）、`npu`（需 NPU 硬件）、`network`（需访问 HuggingFace/ModelScope，默认排除，仅 nightly 跑）。
- `addopts = "-m 'not npu and not nightly and not network'"`：pytest 全局默认排除三类 marker，即"默认不加任何参数直接跑 pytest"就只跑无 marker 的 smoke/regression 用例。
- `testpaths = ["tests"]`：限定 pytest 仅在 `tests/` 目录收集用例。
- `[tool.coverage.run] parallel = true`：coverage 并行模式，配合 `pytest-xdist` 的多 worker 各自落 `.coverage.*` 文件。
- `[tool.coverage.run] branch = true`：开启分支覆盖，与文档中"行覆盖率 60%、分支覆盖率 40%"阈值直接对应。

---

## 【公式解读】

原文无公式（仅有一处伪配置 toml 片段，已在"表格解读"中按配置块逐项解读）。

---

## 【关联】

原文未给出文末内部链接清单，但文中明确提到了以下上下游模块与配套文档，可作为关联路径：

- **配套指南文档**
  - `tests/README.md`：新用例添加的分步指南（五步流程：选目录 → 复用 helpers → 命名约定 → 本地用 `run_*.sh` 验证 → 确认下次 nightly 出现在 `test_map`）
  - `tests/SKILL.md`：LLM 辅助生成测试用例的 prompt 模板，编码了目录分层、marker 语义、共享 helper API 与 smoke/regression/benchmark 代码模板

- **共享资产目录**
  - `tests/assets/model_config/`：共享模型配置（含 `num_hidden_layers_override=1` 的本地小配置示例，以及远程 `config.json` 引用）
  - `tests/helpers/`：可复用 builder 与断言
  - `tests/regression/scripts/helpers/`：工具链 UT，镜像生产代码 `scripts/helpers/`

- **入口脚本与 CI/nightly 链路**
  - `run_smoke.sh` → `run_regression.sh` → `run_benchmark.sh` → `run_nightly.sh` → `run_ci_gate.sh` 五脚本协作
  - 外部 `test_map` 文件（由 nightly job 维护，被 `run_ci_gate.sh` 读取）构成 PR 增量 CI 与 nightly 之间的桥梁
  - nightly JUnit XML 报告 + Feishu 通知，构成"通过率/耗时漂移/慢用例数"的反馈闭环

- **覆盖范围角色分工**
  - 目录（smoke/regression/benchmark）= 层级表达
  - marker（nightly/npu/network）= 横切约束
  - 三者协同后，benchmark 永不入增量路径，network 仅在 nightly phase 2c 跑，npu 不进任何 `run_*.sh` 入口

---

## 【使用方法】

### 启用方式与入口命令（原文）

| 场景 | 命令/脚本 | 行为 |
|------|----------|------|
| 本地完整 smoke | `run_smoke.sh` | 跑 `tests/smoke/` 全量，含 `@pytest.mark.nightly` 但排除 npu/network |
| 本地完整 regression | `run_regression.sh` | 跑 `tests/regression/` 全量，含 `@pytest.mark.nightly` 但排除 npu/network |
| 本地 benchmark | `run_benchmark.sh` | 跑 `tests/benchmark/` 全量（含 `models/`、`ops/perf_database/`） |
| Nightly 守护 | `run_nightly.sh` | 跑三层全量 + nightly 标记用例 + benchmark + phase 1 收集覆盖率与刷新 `test_map` |
| CI PR 增量 | `run_ci_gate.sh` | 读取外部 `test_map`，跑被映射到的 smoke/regression 用例，强制 `test_map` 策略与 pytest 通过/失败 |

### 关键配置项（原文）

| 配置项 | 取值 | 作用 |
|------|------|------|
| `addopts` | `"-m 'not npu and not nightly and not network'"` | pytest 默认排除三类 marker |
| `tool.coverage.run.parallel` | `true` | coverage 并行收集 |
| `tool.coverage.run.branch` | `true` | 开启分支覆盖 |
| 行覆盖率阈值 | 60%（原文） | nightly phase 1 上报与守护 |
| 分支覆盖率阈值 | 40%（原文） | nightly phase 1 上报与守护 |

### 环境变量（原文）

| 环境变量 | 取值/行为 | 适用场景 |
|------|------|------|
| `MSMODELING_OFFLINE` | 未设置 → 允许 Hub 访问 | 本地运行 |
| `MSMODELING_OFFLINE` | `1` → 禁止隐式权重下载 | CI 环境 |
| `MSMODELING_TEST_WEIGHTS_PRUNE` | `1` → 会话结束后清理权重分片 | 任何场景，按需开启 |

### 缓存目录（原文）

- 缓存限定路径：仓库根的 `.msmodeling_cache/`
- 治理手段：CI 禁止隐式下载 + 可选会话后剪枝权重分片

### `build_test_map` 收集作用域（原文）

- 硬编码 marker 表达式：`not npu and not nightly and not network`
- 收集目录范围：`tests/smoke/` 与 `tests/regres[sion/]`
- 与 ci_gate 选择 marker 完全一致——这是增量 CI 与 `test_map` 维护之间的一致性约束

> 备注：原文 "Implementation Ideas" 部分仅展示了 Step 1 的内容（Solidify Directory Layering and Marker Semantics），后续步骤在给出的原文中未呈现；以上解读严格基于已给出的原文事实。
