# 算子开发工具链快速入门

> 仓 `msot` · 路径 `docs/zh/quick_start/op_tool_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/zh/quick_start/op_tool_quick_start.md

# msot — `op_tool_quick_start.md` 深度解读

---

## 【定位】

本文档是 MindStudio 算子开发工具链的"十分钟贯通式"quick start 指南，以一个简单加法算子为线索，按"环境准备 → 算子建模 → 工程生成 → 异常检测 → 原生调试 → 性能调优"六个环节串联起 msKPP / msOpGen / msSanitizer / msDebug / msOpProf 五款工具，让开发者通过 Copy/Paste 即可在 10 分钟左右完成一次端到端体验。

---

## 【技术要点】

1. **强制前置：标准化 CANN 容器环境** —— 教程明确"不支持裸机、虚拟机或其他非标准容器部署"，需先安装 CANN 容器镜像，并在容器内执行自检脚本检查 `$ASCEND_HOME_PATH`、`$ATB_HOME_PATH`、`$MY_STUDY_VAR_CHIP_SOC_TYPE` 以及 `msopgen` / `mssanitizer` / `msdebug` / `msopprof` 四个核心命令是否齐备，全部 `[PASS]` 才可继续。

2. **msKPP 是 Python 类库而非可执行程序** —— 用户通过 `import` 导入 Tensor、Chip 及指令（如 vadd），用 `with` 语句进入算子实现上下文来编写 DSL 脚本；内部预先采集真实环境中各指令的性能数据，对算子执行流程进行开销建模，结果以 `MSKPP{timestamp}/` 目录（含 `Instruction_statistic.csv`、`Pipe_statistic.csv`、`trace.json`）输出。**仅支持昇腾 910B 系列芯片**。

3. **msOpGen 用 JSON 配置 + 命令行生成 C++ 工程** —— 配置文件类比 C 函数声明（函数名、入参/返回值类型）；生成命令为 `msopgen gen -i <json> -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom`，其中 `-lan cpp` 指定生成 Ascend C 代码，`-c` 指定芯片 SoC 型号；生成结果中仅有 3 个【用户扩展点】文件需开发者实现：`op_host/add_custom.cpp`、`op_kernel/add_custom.cpp`、`op_kernel/add_custom_tiling.h`，其余均为框架代码。

4. **编译产物为自解压 `.run` 包** —— 通过 `bash ./build.sh` 编译，在 `build_out` 下生成 `custom_opp_openEuler_aarch64.run`；部署即是把二进制拷贝到 CANN 公共目录，需追加 `export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH`；运行验证命令支持通过 `bash ./run.sh <NPU序号>` 指定卡号（取值范围 `[0, NPU数量-1]`），未指定时自动随机选一张空闲 NPU。

5. **体验环节的依赖关系** —— 步骤 4、5、6（msSanitizer / msDebug / msOpProf）均依赖步骤 3（msOpGen）生成的工程，但三者之间相互独立、可按需选学；步骤 2（msKPP）独立于后续环节，可在完成步骤 1 后选学。

6. **环境内 SoC 信息自动同步** —— 通过 `keep_soc_info.py get/set` 脚本自动获取当前 SoC 型号并刷新到 `op_host/add_custom.cpp` 中，避免手动维护芯片宏。

---

## 【关键机制与数据】

### 工具链工作流（按文档的 6 步体验地图组织）

```
[Step 1] 环境准备 (CANN 容器镜像, 3 min)
        │
        ▼
[Step 2] 算子设计 (msKPP, 30 s)  ← 独立可选, 仅 Ascend 910B
        │
        ▼
[Step 3] 工程开发 (msOpGen, 1 min)  ──→ 生成 AddCustom 工程 (3 个用户扩展点)
        │
        ├─→ [Step 4] 异常检测 (msSanitizer, 1 min)
        ├─→ [Step 5] 原生调试 (msDebug, 1 min)
        └─→ [Step 6] 性能调优 (msOpProf, 1 min)
                                       │
                                       ▼
                              build_out/*.run (自解压部署包)
                                       │
                                       ▼
                              注册到 CANN, 被 PyTorch 等框架发现调用
```

### 关键性能建模数据（原文给出的示例）

文档以加法算子的 `Instruction_statistic.csv` 为例展示了 msKPP 输出：

- **MOV-GM_TO_UB**（Global Memory → Unified Buffer 搬运）：0.3081 us / 570 cycles / 6144 B
- **VADD**（向量加法指令）：0.0135 us / 25 cycles / 1536 Ops
- **MOV-UB_TO_GM**（Unified Buffer → Global Memory 搬回）：0.4254 us / 787 cycles / 3072 B

原文结论：**MOV-UB_TO_GM 耗时最长、指令周期数最多**，是性能优化中的关键路径；实际开发中若发现此类内存搬运占比过高，应优先优化数据复用（Tiling）或使用更高效的搬运指令。

### 自检脚本检查项（4 大类，全部 PASS 才可继续）

1. 容器环境标记 `/.dockerenv` + `$ASCEND_HOME_PATH` + `$ATB_HOME_PATH`
2. 芯片型号变量 `$MY_STUDY_VAR_CHIP_SOC_TYPE`
3. 示例代码仓 `~/ot_demo/msot/example/quick_start`
4. 4 个核心工具命令 `msopgen` / `mssanitizer` / `msdebug` / `msopprof`

### 工程目录结构（生成结果的"用户扩展点"标注）

```
AddCustom/
├── build.sh                 # 编译入口
├── CMakeLists.txt
├── framework/               # 框架插件 (无需关注)
├── op_host/
│   ├── add_custom.cpp       # 【用户扩展点】原型注册 / shape 推导 / tiling
│   └── CMakeLists.txt
├── op_kernel/
│   ├── add_custom.cpp       # 【用户扩展点】算子 Kernel 实现 (GM→UB→VADD→UB→GM)
│   ├── add_custom_tiling.h  # 【用户扩展点】tiling 数据结构
│   └── CMakeLists.txt
└── CMakePresets.json
```

---

## 【表格解读】

### 表格 1：体验地图（6 步骤总览）

| 步骤 | 环节 | 核心工具 | 实测操作耗时 | 建议原理学习 |
|:---:|:---:|:---|:---:|:---:|
| **1** | **环境准备** | `CANN 容器镜像` | 3 分钟 | 5 分钟 |
| **2** | **算子设计** | `msKPP` | 30 秒 | 5 分钟 |
| **3** | **工程开发** | `msOpGen` | 1 分钟 | 20 分钟 |
| **4** | **异常检测** | `msSanitizer` | 1 分钟 | 10 分钟 |
| **5** | **原生调试** | `msDebug` | 1 分钟 | 10 分钟 |
| **6** | **性能调优** | `msOpProf` | 1 分钟 | 10 分钟 |

**逐行解读：**

- **第 1 行（环境准备）**：使用 `CANN 容器镜像` 作为前置依赖，操作实测耗时 3 分钟（含约 3 分钟的公网环境安装时间，受网络影响），原理学习建议 5 分钟；该步骤是强制前置，缺失将导致后续大量失败。
- **第 2 行（算子设计）**：使用 `msKPP` 性能建模工具，实操只需 30 秒即可生成 `MSKPP{timestamp}/` 结果目录，但需 5 分钟了解其 DSL 用法；仅支持 Ascend 910B 系列芯片。
- **第 3 行（工程开发）**：使用 `msOpGen` 自动生成 C++ 工程框架，实操 1 分钟，原理学习 20 分钟（耗时最长，因为涉及 Host/Kernel/Tiling 三大用户扩展点的协作机制）；是步骤 4/5/6 的共同前置。
- **第 4 行（异常检测）**：使用 `msSanitizer`，实操 1 分钟、原理 10 分钟；依赖步骤 3 生成的工程。
- **第 5 行（原生调试）**：使用 `msDebug`，实操 1 分钟、原理 10 分钟；依赖步骤 3 生成的工程，与步骤 4 独立。
- **第 6 行（性能调优）**：使用 `msOpProf`，实操 1 分钟、原理 10 分钟；依赖步骤 3 生成的工程，与步骤 4、5 独立可任选其一或全选。

> 原文补充的依赖关系：**步骤 4、5、6 均依赖步骤 3**，但三者之间**相互独立**，可按需选学；步骤 2 也独立，可在完成步骤 1 后任选 2 或 3 开始体验。

---

### 表格 2：`Instruction_statistic.csv` 示例（msKPP 建模结果）

| Instruction  | Duration(us) | Cycle | Size(B) | Ops  |
|:--------------:|:--------------:|:-------:|:---------:|:------:|
| MOV-GM_TO_UB |    0.3081    |  570  |  6144   |  -   |
|     VADD     |    0.0135    |  25   |    -    | 1536 |
| MOV-UB_TO_GM |    0.4254    |  787  |    -    |  -   |

> （注：原文第三列 Size(B) 与第四列 Ops 标签为 `Duration/Cycle/Size/Ops`，逐行已按原文呈现；MOV-UB_TO_GM 行的 Size(B) 原文为 " -"，已逐字保留）

**逐行解读：**

- **MOV-GM_TO_UB**：执行了 1 次 GM→UB 的数据搬运，耗时 **0.3081 us**，占用 **570 cycles**，搬运 **6144 B** 数据；这是典型的把输入数据从 Global Memory 搬进片上 Unified Buffer 的前导步骤。
- **VADD**：向量加法指令，执行 **1536 次 Ops**，耗时仅 **0.0135 us**、**25 cycles**；是本次任务的实际计算动作，**算上数据搬运的开销，计算本身占总耗时的比例极小**。
- **MOV-UB_TO_GM**：把结果从 UB 搬回 GM，耗时 **0.4254 us**、**787 cycles**，搬运 **3072 B**；**这是耗时与周期数最高的指令，是性能优化的关键路径**。

**表格 2 整体结论（原文给出）**：在加法算子场景中，MOV-UB_TO_GM 的耗时（Duration）和指令周期数（Cycle）都最大，是性能瓶颈；优化方向是改善数据复用（Tiling）或选用更高效的搬运指令。

---

## 【公式解读】

**原文无公式。** 文档未包含任何 LaTeX 数学公式或伪代码公式；其核心"计算逻辑"以表格（耗时、周期、字节数、Ops）和工程命令（`msopgen gen ...`、`bash ./build.sh` 等）的形式呈现，不涉及推导式。

---

## 【关联】

本文档是 msot 仓"快速上手"路径的入口之一，主要上下游关系如下：

### 上游前置（强依赖）

- **`installation_guide.md`**（《昇腾 AI 算子开发工具链学习环境安装指南》）—— 在 §2.1.1 作为强制前置引用：👉 [installation_guide.md](installation_guide.md)，描述完整安装步骤。
- **`./installation_guide.md#5-容器内设置芯片-soc-型号`** —— 在 §2.2.3 当 msKPP 报 `Chip is unsupported` 时，作为环境变量 `$MY_STUDY_VAR_CHIP_SOC_TYPE` 的修复指引被引用。

### 上下游（并行体验/可选路径）

- **`msKPP` 工具**（§2.2）：本文档是其快速体验入口；深入学习需参考上游仓库的 [msKPP 工具接口说明](https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/api_reference/mskpp_api_reference.md)。
- **`msOpGen` 工具**（§2.3）：参数详细含义请参阅其 [msOpGen 代码仓库](https://gitcode.com/Ascend/msopgen) 的《使用指南》。
- **Ascend C 编程入门**：文档在 §2.3.2 提示，若要深入理解 3 个用户扩展点文件的协作机制（Host 侧 tiling + Kernel 侧 GM→UB→VADD→UB→GM + tiling 数据结构），推荐阅读外部博客《昇腾 Ascend C 编程入门教程（纯干货）》[https://www.hiascend.com/developer/blog/details/0239124507827469022]。

### 下游延伸（依赖本文档生成的工程）

- §2.3（msOpGen）生成的 `AddCustom/` 工程是后续 §2.4（异常检测）、§2.5（原生调试）、§2.6（性能调优）的前置；这三节在文末被截断（原文 `\cp -rf ~/ot_demo/ms` 处中断），但从体验地图表格可知它们分别对应 `msSanitizer`、`msDebug`、`msOpProf` 三款工具。

### 同仓内的依赖资源

- 示例代码仓 `~/ot_demo/msot/example/quick_start/` 是本文档所有"Copy/Paste"步骤的素材源（含 `mskpp/mskpp_demo.py`、`msopgen/msopgen_demo.json`、`msopgen/keep_soc_info.py`、`msopgen/code/` 下的 3 个 C++ 文件等）。

---

## 【使用方法】

### 启用方式

1. **先决条件**：按 [installation_guide.md](installation_guide.md) 安装 CANN 容器镜像（含全部算子工具、示例代码、依赖库），公网环境预计 3 分钟。
2. **环境自检**（必须全部 PASS）：复制 §2.1.2 的整段 bash 脚本到容器内终端执行，检查容器标记、`$ASCEND_HOME_PATH`、`$ATB_HOME_PATH`、`$MY_STUDY_VAR_CHIP_SOC_TYPE`、`~/ot_demo/msot/example/quick_start` 目录、以及 `msopgen` / `mssanitizer` / `msdebug` / `msopprof` 4 个命令是否就绪。

### 各工具的关键命令

| 工具 | 用途 | 关键命令 |
|:---|:---|:---|
| **msKPP** | 性能建模（仅 Ascend 910B） | `python3 mskpp_demo.py` → 生成 `MSKPP{timestamp}/` |
| **msOpGen** | 生成算子工程 | `msopgen gen -i msopgen_demo.json -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom` |
| **（编译）** | 编译算子 | `bash ./build.sh` |
| **（部署）** | 安装到 CANN | `bash ./build_out/custom_opp_openEuler_aarch64.run` |
| **（动态库）** | 追加依赖路径 | `export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH` |
| **（验证）** | 运行算子（可选卡号） | `bash ./run.sh [NPU序号]`，序号取值 `[0, NPU数量-1]` |

### 关键配置项 / 环境变量

- **`$MY_STUDY_VAR_CHIP_SOC_TYPE`**：芯片 SoC 型号变量，被 `msopgen` 命令的 `-c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE}` 直接引用；缺失时按 [installation_guide.md 第 5 节](./installation_guide.md#5-容器内设置芯片-soc-型号) 配置。
- **`$ASCEND_HOME_PATH`** / **`$ATB_HOME_PATH`**：容器内 CANN 安装路径相关变量，自检脚本检查其非空。
- **`msopgen_demo.json`**：算子定义配置文件（自定义 JSON 格式，类比 C 函数声明），含算子名称、输入/输出变量名、类型与数据排布格式；函数体为空，需开发者自行实现。
- **`keep_soc_info.py`**：辅助脚本，先 `get ./op_host/add_custom.cpp` 获取当前 SoC，再 `set ./op_host/add_custom.cpp` 写回，实现 SoC 信息与 C++ 文件的自动同步。

### 目录约定

- **容器内工作区**：`~/ot_demo/workspace/`（含 `mskpp/`、`src/AddCustom/` 子目录）
- **示例素材仓**：`~/ot_demo/msot/example/quick_start/`（msKPP 脚本、msOpGen 配置、3 个 C++ 文件、辅助脚本均在此处）
- **编译产物**：`build_out/custom_opp_openEuler_aarch64.run`（自解压部署包）
