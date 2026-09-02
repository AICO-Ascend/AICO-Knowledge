# msOpGen 架构设计说明书

> 仓 `msopgen` · 路径 `docs/zh/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopgen/docs/zh/development_guide/architecture.md

# msOpGen 架构设计说明书 — 一体化深度解读

## 【定位】

这篇文档描述 msOpGen 作为 Ascend 算子工程的代码自动化生成工具的整体架构——通过解析 JSON 算子原型定义，自动产出可直接编译部署的多框架算子工程、TIMING 仿真流水图和 ST 测试用例，使开发者从框架代码中解放出来、聚焦核心算法逻辑。

---

## 【技术要点】

1. **模板替换机制（Template Replacement）**：根据 JSON 原型定义中的算子名称、输入输出参数类型和格式，自动替换 C++ 源码模板中的占位符，一次性生成 Host 侧（原型注册、Shape 推导、Tiling 实现、信息库）和 Kernel 侧（算子计算逻辑）的框架代码。

2. **统一 JSON 接口适配多框架**：通过同一份 JSON 原型定义，可生成对接 TensorFlow、PyTorch、MindSpore、ONNX 四种 AI 框架的算子工程；底层算子类型覆盖 AscendC、TBE、AI CPU 三类。

3. **CLI 三入口分层设计**：入口层包含三个子命令——`msopgen gen`（生成算子工程）、`msopgen sim`（解析仿真 dump 流水图）、`msopst`（生成并运行硬件测试）。

4. **算子追加模式**：支持 `-m 1` 模式，在已有算子工程中追加新算子，无需重头搭建工程。

5. **命名严格映射**：算子类型（OpType）→ 文件名/核函数名采用 PascalCase → snake_case 的固定转换规则，例如 `AddCustom` → `add_custom.cpp` / `add_custom`。

6. **双发布模式**：源码发布（保留 Kernel 源码 `.cpp`，支持在线编译和 ATC 模型转换）与二进制发布（仅交付 `.o` 与 `.json` 信息文件，直接调用算子二进制）。

7. **CMakePresets.json 灵活配置**：通过该文件统一管理编译选项、芯片型号（soc_version）、发布方式等。

---

## 【关键机制与数据】

### 数据流（原文 §3.3）

> 原文：
> ```
> 算子原型 JSON ──→ [JSON Parser] ──→ 算子描述结构体
>                                        │
>                                 [Template Engine] ──→ 算子工程目录
>                                        │
>                                 [用户编写 Kernel 实现]
>                                        │
>                               [build.sh 编译] ──→ .run 部署包
>                                        │                               
>                                 [msopst create]                       
>                                        │                                     
>                                 ST 用例 .json                          
>                                 [msopst run]                       
>                                        │                                 
>                                 st_report.json                           
> ```

数据流是一条**单向串联的自动化流水线**，可分解为四个阶段：

| 阶段 | 关键节点 | 输入 | 输出 |
|---|---|---|---|
| ① 原型解析 | JSON Parser | `*.json` 原型定义 | 结构化算子描述（内存对象） |
| ② 工程生成 | Template Engine | 算子描述 + soc_version | 完整算子工程目录（含 CMakeLists、Host/Kernel 模板源码） |
| ③ 编译打包 | build.sh / Project Builder | 用户填充的 Kernel 实现 + CMakePresets.json | `.run` 部署包 |
| ④ 测试闭环 | msopst create → msopst run | `op_host/*.cpp` + `.run` 包 + 硬件 | `*_case.json` 测试用例 → `st_report.json` 报表 |

> 原文要点：Dump Analyzer 是独立分支（被 `msopgen sim` 调用），输入为仿真 dump 数据，输出为 trace.json，可在 Chrome tracing 中查看流水图——这一支路与上述主链路**并行而非串联**。

### 模块职责矩阵（原文 §3.2）

| 模块 | 职责 | 输入 | 输出 |
|---|---|---|---|
| **JSON Parser** | 解析算子原型定义文件，校验字段合法性 | `*.json` 原型定义 | 结构化算子描述 |
| **Template Engine** | 基于算子描述和芯片型号生成工程模板 | 算子描述 + soc_version | 完整算子工程目录 |
| **Dump Analyzer** | 解析性能仿真 dump 数据 | dump 数据文件 | trace.json 流水图 |
| **Project Builder** | 生成 CMakeLists.txt、CMakePresets.json、build.sh | 算子描述 + 编译选项 | 可编译的工程 |
| **ST Test Generator** | 解析 Host 侧源码生成 ST 测试用例 | `op_host/*.cpp` | `*_case.json` |
| **ST Test Runner** | 执行硬件测试并生成报表 | `*_case.json` + soc | `st_report.json` |

### 性能/数据指标

原文未提供任何数字（如生成耗时、模板数量、测试覆盖率等），本节无数字可解读。

---

## 【表格解读】

### 表 1 — 功能清单（原文 §1.2，逐字还原）

| 类型 | 功能 | 描述 |
|-----|------|------|
| 业务功能 | 算子工程生成 | 基于 JSON 原型定义生成完整的 AscendC/TBE/AI CPU 算子工程 |
| 业务功能 | 多框架适配 | 支持 TensorFlow、PyTorch、MindSpore、ONNX 框架 |
| 业务功能 | 算子追加 | 支持在已有算子工程中追加新算子（`-m 1` 模式） |
| 业务功能 | 仿真流水图解析 | 解析性能仿真 dump 数据，生成可在 Chrome tracing 中查看的流水图 |
| 业务功能 | 编译部署集成 | 生成 build.sh 编译脚本和 .run 算子部署包 |
| 配套工具 | ST 测试 | msOpST 工具自动生成测试用例并在硬件环境中执行 |

**逐行解读**：
- 第 1 行说明**产物形态多样性**——同一 JSON 可生成三种底层算子实现（AscendC/TBE/AI CPU），覆盖不同硬件抽象层。
- 第 2 行说明**前端框架广度**——四大主流框架通过统一 JSON 抽象被一致化处理，降低了多框架适配的学习成本。
- 第 3 行点明**增量式工作流**——`-m 1` 参数使 msopgen 具备"追加"而非只能"重建"的能力，契合算子库长期演进的实际场景。
- 第 4 行指出**性能分析闭环**——通过 Chrome tracing（浏览器原生 perfetto 工具）提供可视化流水图，免去自研可视化组件。
- 第 5 行强调**端到端交付**——`.run` 是最终交付包形态，build.sh 是编译入口，体现"生成即可用"的设计目标。
- 第 6 行说明**质量保障闭环**——msOpST 与 msOpGen 在文档中虽分章呈现，但通过 `op_host/*.cpp → *_case.json → st_report.json` 这条链路形成测试自动化闭环。

---

### 表 2 — 设计目标（原文 §2，逐字还原）

| 设计目标 | 描述 |
|---------|------|
| **工程完整性** | 生成的工程可直接编译部署，无需手动补充框架代码 |
| **多框架覆盖** | 统一 JSON 接口适配多种 AI 框架，降低学习成本 |
| **编译可配置** | 通过 CMakePresets.json 灵活配置编译选项、芯片型号、发布方式 |
| **命令行易用性** | 参数设计清晰直观，支持默认值和自动推断 |

**逐行解读**：
- **工程完整性**是核心承诺——这是模板替换机制（§4.1）存在的根本理由：消除"生成后还需手动补 Host/Tiling"的痛点。
- **多框架覆盖**与功能清单第 2 行呼应，体现了"以 JSON 为中心的抽象层"是连接多框架与底层硬件的关键设计。
- **编译可配置**具体落地为 CMakePresets.json——它是 Project Builder 模块的输出之一，负责把 soc_version、发布模式等编译维度声明化。
- **命令行易用性**对应 CLI 入口层的设计原则，与 §3.1 的 CLI 入口层（`msopgen gen / msopgen sim / msopst`）相互印证。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档末尾给出的内部链接信息为**（无）**，即该 overview 文档没有显式的内部链接条目。但根据文中内容可以梳理出以下**隐含的模块/特性关联**：

| 上游/被调用方 | 下游/调用方 | 关联依据 |
|---|---|---|
| **JSON Parser** | Template Engine、Project Builder | §3.3 数据流中，Parser 是所有后续模块的输入源 |
| **Template Engine** | Project Builder | §3.2 中 Template Engine 产出工程目录，Project Builder 在此基础上叠加 CMake/编译文件 |
| **Template Engine** | ST Test Generator | §3.3 中 ST 用例生成依赖 `op_host/*.cpp`，而 Host 源码由 Template Engine 生成 |
| **msopgen gen / msopgen sim** | msopgen CLI | §3.1 架构图中 CLI 入口层统一调度 |
| **msopgen** | msopst（配套工具） | §1.2 功能清单明确 msOpST 为配套工具；§3.3 数据流中 msOpST 接力 msOpGen 完成测试 |
| **CMakePresets.json** | build.sh → .run | §2 设计目标与 §3.2 Project Builder 共同指出 CMakePresets 是编译配置载体 |
| **soc_version** | Template Engine、Project Builder、ST Test Runner | 芯片型号贯穿工程生成、编译、测试三个阶段 |
| **§6 msOpGen 类图（figures/msOpGenClass.png）** | 全部模块 | 类图是 §3.2 模块表与 §3.1 架构图的 OO 视角细化，但原文未对类图做文字说明 |

---

## 【使用方法】

> 原文涉及的启用方式/配置项/命令如下：

| 类别 | 内容 | 原文依据 |
|---|---|---|
| **CLI 子命令** | `msopgen gen`、`msopgen sim`、`msopst` | §3.1 架构图入口层 |
| **算子追加参数** | `-m 1` 模式（在已有算子工程中追加新算子） | §1.2 功能清单第 3 行 |
| **编译入口脚本** | `build.sh`（由 Project Builder 生成） | §1.2 / §3.3 |
| **部署包形态** | `.run` 算子部署包 | §1.2 |
| **编译配置载体** | `CMakePresets.json`（配置编译选项、芯片型号、发布方式） | §2 设计目标第 3 条 |
| **可视化工具** | Chrome tracing（查看 trace.json 流水图） | §1.2 仿真流水图解析 |
| **ST 测试入口** | `msopst create`（生成用例）→ `msopst run`（执行测试） | §3.3 数据流 |
| **源代码组织** | `example/`、`docs/`、`msopgen/`、`tools/msopst/`、`test/msopgen/`、`test/msopst/`、`output/`、`setup.py`、`build.py` | §5 目录结构 |
| **Whl 包构建** | `setup.py`（msopgen whl 构建脚本）、`build.py`（构建入口脚本） | §5 目录结构 |

> 注：原文未涉及具体命令的完整参数列表、必填项与默认值等使用细节，这些信息需查阅其他子文档。

## 图文联合解读

- `msOpGenClass.png`: **1) 图中内容**：分层类依赖图。顶层 OpFileGenerator 与 ArgsParser 互依，生成四类交付件（MindSporeAiCore/AiCore/AiCpu/MindSporeAiCpu）均实现 OpFile 基类；中层 OpFile→OpInfoParser→ArgsParser 链路选择 IR 类型；底层六种解析器（IROpInfo、MSIROpInfo、TFOpInfo、MSTFOpInfo、JsonIROpInfo、JsonMSIROpInfo）最终继承 OpInfo 算子基类。关系含"依赖/实现/继承"三类连线。

**2) 技术结论**：采用"生成器入口＋文件基类＋策略分发＋多 IR 适配"的解耦分层架构，新增框架/芯片仅需扩展子类，符合开闭原则。

**3) 与文档关系**：直接支撑"多框架覆盖（TF/MindSpore/ONNX 分支）、工程完整性（基类统一输出）、编译可配置（ArgsParser 解耦命令行）"三项设计目标。
