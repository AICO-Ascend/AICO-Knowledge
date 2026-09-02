# msKL 代码仓架构说明

> 仓 `mskl` · 路径 `docs/zh/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mskl/docs/zh/development_guide/architecture.md

# msKL 代码仓架构说明 — 深度解读

---

## 【定位】

本文档是对 msKL（MindStudio Kernel Launcher）整个代码仓的**架构级总览**，解决"用户/开发者面对一个以 whl 包发布的昇腾算子 Kernel 轻量化调用与自动调优工具，如何理解其目录划分、子系统职责、模块依赖、数据流与构建测试方式"的问题。

---

## 【技术要点】

1. **工具定位与发布形态**：msKL 是面向**昇腾 AI 处理器**的算子 Kernel 轻量化调用与自动调优工具，采用 **Python** 实现，以 **whl 包**形式发布，包名 `mindstudio-kl`、顶层模块名 `mskl`，许可证为**木兰宽松许可证 v2**。
2. **三大子系统分层**：
   - `mskl/launcher/` — **算子调用子系统**，提供 `tiling_func` 与 `get_kernel_from_binary` 两条主路径；
   - `mskl/optune/` — **自动调优子系统**，在调用子系统的编译产物上做参数替换、编译、性能采集、对比；
   - `mskl/utils/` — **公共工具**，提供参数校验、文件 I/O、CANN 路径获取、runtime 能力检测、安全检查与日志。
3. **代码生成 + 即时编译两段式调用链路**：Python 配置 → `Launcher.code_gen()` 生成 **C++ 下发代码** → `compile_tiling()` / `compile_kernel_binary()` 编译为 **.so** → `NPULauncher` 加载并下发到 NPU 执行。
4. **两类调优装饰器**：`@mskl.autotune`（**Kernel 级调优**，使用 `CompiledKernel` 模式）与 `@mskl.autotune_v2`（**应用级调优**，使用 `CompiledExecutable` 模式）。
5. **源码级参数替换机制**：`Replacer` 通过识别 C++ 源码中的 `// tunable` 与 `// tunable: 别名` 两种标记，对参数进行替换并写入临时 `.cpp` 文件。
6. **基于 MSPTI 的性能采集**：通过 `Monitor.start()` / `Monitor.stop()` 捕获 Kernel 实际执行耗时，并支持 `warmup` 与 `repeat` 控制采样稳定性。
7. **构建与测试入口统一**：`python3 build.py` 生成 `output/mindstudio_kl-{version}-py3-none-any.whl`；`python3 build.py test` 使用 **pytest** 执行全量单测。

---

## 【关键机制与数据】

### 1. 算子调用子系统的双路径数据流（原文 §3.1）

**路径 A — `tiling_func` 路径**：

```
tiling_func(op_type, inputs, ...)
   → [config.py] TilingConfig 解析参数
   → [code_generator.py] Launcher.code_gen() 生成 C++ tiling 调用代码
   → [compiler.py] compile_tiling() 编译为 .so
   → [opgen_workflow.py] TilingOutput 返回 blockdim / workspace / tiling_data
```

**路径 B — `get_kernel_from_binary` 路径**：

```
get_kernel_from_binary(kernel.o)
   → [config.py] KernelBinaryInvokeConfig
   → [code_generator.py] Launcher.code_gen() 生成 C++ kernel 下发代码
   → [compiler.py] compile_kernel_binary() 编译为 .so → CompiledKernel
   → [driver.py] NPULauncher 加载 .so 并调用 NPU 执行
   → 返回 CompiledKernel 实例（支持 kernel[blockdim](args) 调用）
```

### 2. 自动调优子系统的五阶段工作流（原文 §3.2）

```
1. Autotuner.pre_launch() → 预启动一次，捕获 kernel 上下文
2. 遍历 configs 中的每组参数：
   ├─ Replacer.replace_src_with_config() 查找 // tunable 标记 → 替换参数 → 写入临时 .cpp
   ├─ compile() 编译修改后的代码
   ├─ Monitor.start() 启动 MSPTI 监控
   ├─ Autotuner.launch() 执行 Kernel + warmup
   ├─ Monitor.stop() 获取耗时
   └─ 记录耗时与参数组合
3. 输出所有组合的耗时对比和最优组合
```

### 3. 模块依赖层级（原文 §4）

- `mskl.utils` **独立**，被 `launcher` 与 `optune` 共同依赖；
- `launcher` 内：`config.py` 与 `context.py` 独立；`code_generator.py` 依赖 `config, context, utils`；`compiler.py` 依赖 `config, driver, utils`；`driver.py` 依赖 `code_generator, utils`；`opgen_workflow.py` 是最重的聚合点，依赖 `config, code_generator, compiler, context, utils`；
- `optune` 内：`tuner.py` 反向依赖 `launcher` 的 `compiler, code_generator, config, context, driver`，并依赖 `utils`；`kernel_modifier.py` 仅依赖 `utils`；`kernel_prof.py` 依赖 `utils` 与外部 `mspti`。

> 性能数据原文未涉及具体数字。

---

## 【表格解读】

### 表格 1：算子调用子系统核心类/函数（原文 §3.1）

| 组件 | 文件 | 职责 |
|------|------|------|
| `TilingConfig` | `config.py` | 解析 tiling_func 的所有入参，生成 C++ 所需的结构化配置 |
| `KernelInvokeConfig` | `config.py` | 封装 kernel 源码文件路径和函数名 |
| `Launcher` | `code_generator.py` | 将 Python 配置转为 C++ 下发代码（code_gen 方法） |
| `CompiledKernel` | `compiler.py` | 编译后的 Kernel 对象，支持 `kernel[blockdim](args)` 调用 |
| `CompiledExecutable` | `compiler.py` | 编译后的可执行程序对象（应用级调优场景） |
| `NPULauncher` | `driver.py` | 运行时加载 .so 并在 NPU 上执行 Kernel |
| `Context` | `context.py` | 全局上下文，维护 tiling_output / op_type / kernel_args 等状态 |
| `TilingOutput` | `opgen_workflow.py` | tiling_func 的返回值封装 |

**逐行解读**：

- `TilingConfig` / `KernelInvokeConfig` 同位于 `config.py`，前者面向**算子级配置**（tiling 阶段参数），后者面向 **kernel 源码级别**（路径+函数名），二者构成调用子系统的配置层入口。
- `Launcher` 是**代码生成中枢**，其 `code_gen()` 方法是把 Python 端的配置"翻译"成可在昇腾 NPU 下发的 C++ 源码的关键步骤。
- `CompiledKernel` 与 `CompiledExecutable` 是**编译产物对象**：前者面向**单 Kernel 调用**（通过 `kernel[blockdim](args)` 调用方式暴露给用户）；后者面向**应用级可执行程序**，主要被 `autotune_v2` 使用。
- `NPULauncher` 位于 `driver.py`，是**真正与 NPU 设备交互的驱动层**，负责 .so 加载与执行。
- `Context` 是**跨模块状态总线**，维护 `tiling_output`（tiling 结果）、`op_type`（算子类型）、`kernel_args`（kernel 实参）等关键中间态，避免参数在多个模块间重复传递。
- `TilingOutput` 是 tiling_func 的**返回值封装类**，将 `blockdim` / `workspace` / `tiling_data` 三个核心输出统一打包。

### 表格 2：自动调优子系统核心类/函数（原文 §3.2）

| 组件 | 文件 | 职责 |
|------|------|------|
| `autotune` | `tuner.py` | Kernel 级调优装饰器，使用 `CompiledKernel` 模式 |
| `autotune_v2` | `tuner.py` | 应用级调优装饰器，使用 `CompiledExecutable` 模式 |
| `Replacer` | `kernel_modifier.py` | C++ 源码参数替换引擎，支持 `// tunable` 和 `// tunable: 别名` 两种标记 |
| `Monitor` | `kernel_prof.py` | 基于 MSPTI 的 Kernel 执行时间采集器 |

**逐行解读**：

- `autotune` / `autotune_v2` 是**两套装饰器入口**，分别对应**单 Kernel 调优**（颗粒度细）与**应用整体调优**（颗粒度粗，编译为可执行程序后整体运行）。
- `Replacer` 通过识别 C++ 源码中的两种 `// tunable` 标记（**匿名**与**带别名**两种形式），实现非侵入式的参数替换。
- `Monitor` 是性能采集器，依赖昇腾平台专属的 **MSPTI**（MindStudio Profiling Tool Interface）库采集 Kernel 真实耗时。

### 表格 3：公共工具模块（原文 §3.3）

| 组件 | 文件 | 职责 |
|------|------|------|
| 参数校验 | `autotune_utils.py` | configs / warmup / repeat / device_ids 等参数合法性检查 |
| Tensor 工具 | `autotune_utils.py` | `is_torch_or_numpy_tensor` / `canonical_tensor` 等 tensor 类型判断和转换 |
| 文件 I/O | `autotune_utils.py` | `get_file_lines` / `load_json` 等文件读写辅助 |
| CANN 路径 | `launcher_utils.py` | `get_cann_path()` 从环境变量获取 CANN 安装路径 |
| Runtime 检测 | `launcher_utils.py` | `check_runtime_impl()` 检测 NPU runtime 是否支持 V2 接口 |
| 安全检查 | `safe_check.py` | `FileChecker` 类：文件权限/属主/大小/软链接等安全检查 |
| 日志 | `logger.py` | 统一日志输出 |

**逐行解读**：

- `autotune_utils.py` 是**调优相关通用工具的聚合**，涵盖入参校验（`configs / warmup / repeat / device_ids` 是关键校验对象）、Tensor 类型归一化、文件 I/O；
- `launcher_utils.py` 是**与 CANN runtime 交互的桥接层**：`get_cann_path()` 通过环境变量定位 CANN 安装路径；`check_runtime_impl()` 用于判断 NPU runtime 是否支持 V2 接口（影响 API 选型）；
- `FileChecker` 提供**多维安全检查**（权限/属主/大小/软链接），是工具加载用户文件前的"安全门"；
- `logger.py` 提供**统一日志**，便于跨子系统追踪调用链路。

### 表格 4：外部依赖（原文 §5）

| 依赖 | 用途 |
|------|------|
| `numpy` | Tensor 数据处理 |
| `torch`（可选） | PyTorch Tensor 支持 |
| `mspti`（昇腾） | Kernel 性能监控（`Monitor` 使用） |
| `acl`（昇腾） | AscendCL 设备管理 |
| `CANN`（昇腾） | NPU 驱动和运行时（通过 `ASCEND_HOME_PATH` 环境变量定位） |

**逐行解读**：

- `numpy` 为**必选**依赖，覆盖基础 Tensor 数据处理；
- `torch` 标注为**可选**，说明 msKL 不强绑定 PyTorch，但可识别 PyTorch Tensor 输入；
- `mspti`、`acl`、`CANN` 均为**昇腾平台依赖**，分别对应性能监控、设备管理与底层驱动/运行时；其中 `CANN` 路径通过环境变量 `ASCEND_HOME_PATH` 定位（与 `launcher_utils.get_cann_path()` 呼应）。

### 表格 5：构建与测试要点（原文 §6）

| 步骤 | 命令 | 产物/效果 |
|------|------|-----------|
| 编译打包 | `python3 build.py` | `output/mindstudio_kl-{version}-py3-none-any.whl` |
| 安装 | `pip3 install output/mindstudio_kl-*.whl` | 装入 Python 环境 |
| 运行 UT | `python3 build.py test` | pytest 全量单测 |
| 测试框架 | pytest（配置见 `test/pytest.ini`） | — |

**逐行解读**：

- 打包命令产物命名遵循 PEP 427 命名规范：`mindstudio_kl`（包名连字符转下划线）+ `{version}` + `py3` + `none-any`（无平台限制，纯 Python 包）；
- 测试入口通过 `build.py` 统一代理（而非直接 `pytest`），便于在 CI 中以单一入口触发；
- pytest 配置文件位于 `test/pytest.ini`，与全局 fixtures / hooks 配置（`conftest.py`）配合使用。

---

## 【公式解读】

**原文无公式**（无 LaTeX 数学公式或伪代码公式定义）。文档中的"公式性"内容均为**目录树与数据流文本图**（使用 ```text 代码块包裹），用于描述模块结构而非数值计算，故不作 LaTeX 符号化解读。

---

## 【关联】

本文档作为**架构总览**，明确连接了以下上下游与模块间关系：

- **msKL 与昇腾生态的边界**：通过 `mspti`（性能监控）、`acl`（设备管理）、`CANN`（驱动与运行时，由 `ASCEND_HOME_PATH` 环境变量定位）三大外部依赖与昇腾平台对接；这意味着 msKL **不能脱离昇腾 NPU 环境运行**，但可在不需要 torch 的最小依赖下工作。

- **三个子系统的依赖层级**：
  - `utils` 是**最底层**，被 `launcher` 与 `optune` 共同依赖；
  - `launcher` 是**核心能力层**，提供 Kernel 调用与编译；
  - `optune` 是**增强层**，通过反向依赖 `launcher` 的 `compiler / code_generator / config / context / driver`，在调用子系统的产物之上叠加自动调优能力——这意味着 `optune` 不能脱离 `launcher` 单独使用。

- **同仓内与 `args` 的关联**：根据文末提供的内部链接 `args`，在文档中 `args` 作为参数占位符出现在 `kernel[blockdim](args)` 调用形式中（即 `CompiledKernel` 暴露给用户的调用接口），是连接 `CompiledKernel` 编译产物与 `Context.kernel_args` 状态、`Launcher.code_gen()` 生成的 C++ 实参列表三者之间的**参数传递契约**。

- **测试覆盖与代码结构的对应关系**：测试目录 `test/launcher/`、`test/op_tune/`、`test/utils/` 与源码目录 `mskl/launcher/`、`mskl/optune/`、`mskl/utils/` **一一对应**，覆盖粒度细至 `code_generator` / `compiler` / `config` / `driver` / `opgen_workflow` 五个模块。

- **构建脚本的统一入口**：`build.py` 同时承担**打包**（`python3 build.py`）与**测试**（`python3 build.py test`）两个职责，是用户/开发者与仓库交互的**唯一入口脚本**。

---

## 【使用方法】

> 以下命令/配置项均严格来自原文 §6 与各表格"职责"列。

- **编译打包 whl**：
  ```bash
  python3 build.py
  ```
  产物：`output/mindstudio_kl-{version}-py3-none-any.whl`

- **安装 whl**：
  ```bash
  pip3 install output/mindstudio_kl-*.whl
  ```
  装入 Python 环境后，可使用顶层模块名 `mskl` 与包名 `mindstudio-kl`。

- **运行单元测试**：
  ```bash
  python3 build.py test
  ```
  内部使用 **pytest**，配置位于 `test/pytest.ini`。

- **使用算子调用能力（用户入口）**：
  - `tiling_func(op_type, inputs, ...)` — 通过 `mskl.launcher` 导出，用于 tiling 阶段，返回 `TilingOutput`（含 `blockdim` / `workspace` / `tiling_data`）；
  - `get_kernel_from_binary(kernel.o)` — 通过 `mskl.launcher` 导出，加载预编译的 kernel 对象文件，返回 `CompiledKernel` 实例；
  - 编译后调用形式：`kernel[blockdim](args)`（与 `args` 内部链接对应）。

- **使用自动调优能力（用户入口）**：
  - `@mskl.autotune(configs=[...])` — **Kernel 级调优**装饰器，基于 `CompiledKernel` 模式（导出自 `mskl.optune`）；
  - `@mskl.autotune_v2(configs=[...])` — **应用级调优**装饰器，基于 `CompiledExecutable` 模式（导出自 `mskl.optune`）；
  - 源码侧需要使用 `// tunable` 或 `// tunable: 别名` 标记需要被调优的参数；
  - 调优配置项：`configs`（参数组合列表）、`warmup`（预热次数）、`repeat`（重复次数）、`device_ids`（设备列表）——这些参数会经过 `autotune_utils.py` 的合法性校验。

- **环境变量**：`ASCEND_HOME_PATH` — 用于 `launcher_utils.get_cann_path()` 定位 CANN 安装路径（原文 §5）。

- **预留/未启用模块**（原文标注 `[预留]`）：`dtype_convert.py`（数据类型转换）、`dump_parser.py`（dump 数据解析）、`utils/const_variables.py`（常量定义）——这些模块**当前未实际启用**，使用方式原文未涉及。
