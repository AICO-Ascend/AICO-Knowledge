# msOpGen Architecture Design Specifications

> 仓 `msopgen` · 路径 `docs/en/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopgen/docs/en/development_guide/architecture.md

```markdown
# msOpGen 架构设计文档 · 一体化深度解读

---

## 【定位】

本文档系统阐述 msOpGen 算子工程代码生成工具的架构设计,解决"手写 Host 侧原型注册、Tiling 策略、Kernel 实现与编译配置繁琐易错"的核心痛点,使开发者仅凭 JSON 原型定义即可一键获得可直接编译部署的完整算子工程。

---

## 【技术要点】

1. **JSON 驱动的算子工程自动生成**: 基于 JSON 原型定义文件,由 JSON Parser → Template Engine 流水线产出含 Host 侧(原型注册、Shape 推断、Tiling、info 库)与 Kernel 侧(算子逻辑)在内的完整 C++ 工程目录。
2. **多框架统一适配**: 通过统一 JSON 接口覆盖 TensorFlow、PyTorch、MindSpore、ONNX 四大 AI 框架,以及 aclnn 直调通路。
3. **命名转换硬约束**: 算子类型名遵循 PascalCase → snake_case 严格映射,如 `AddCustom` → `add_custom.cpp` / `add_custom`,保证文件命名与 kernel 函数名的一致性。
4. **双分发模式**: 支持 Source Distribution(保留 .cpp 源码,可在线编译与 ATC 模型转换)与 Binary Distribution(编译为 .o + .json info,供算子二进制直调)两种交付形态。
5. **性能仿真可视化**: Dump Analyzer 解析性能仿真 dump 数据,产出 trace.json,可在 Chrome tracing 中查看 pipeline 可视化。
6. **可配置构建 + ST 测试闭环**: 通过 CMakePresets.json 配置编译选项、芯片型号、分发模式;配合 msOpST / msOpST ascendc_test 自动生成 ST 用例并上板执行,产出 st_report.json。

---

## 【关键机制与数据】

### 三层系统架构(原文 3.1)

```
┌──────────────────────────────────────────────┐
│                CLI Layer                      │
│   msopgen gen    msopgen sim    msopst        │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│              Core Engine Layer                 │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ JSON     │  │ Template │  │ Dump       │  │
│  │ Parser   │  │ Engine   │  │ Analyzer   │  │
│  └──────────┘  └──────────┘  └────────────┘  │
│  ┌──────────┐  ┌──────────────────────────┐  │
│  │ ST Test  │  │ Project Builder          │  │
│  │ Generator│  │ (CMake/Build Integration)│  │
│  └──────────┘  └──────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│                Output Layer                    │
│  Operator project / .run package /             │
│  trace.json / ST case.json / st_report.json   │
└──────────────────────────────────────────────┘
```

**工作机制(原文逐字保留)**:
- **CLI 层** 接收用户命令,作为整个工具链的统一入口(`msopgen gen` / `msopgen sim` / `msopst`)。
- **核心引擎层** 由五大功能模块协同:JSON Parser 负责解析与校验;Template Engine 依据算子描述 + soc_version 生成工程目录;Dump Analyzer 解析 dump 数据生成 trace.json;ST Test Generator 扫描 `op_host/*.cpp` 产出 `*_case.json`;Project Builder 整合 CMakeLists.txt / CMakePresets.json / build.sh 形成可构建工程。
- **输出层** 统一产出算子工程目录、`.run` 部署包、trace.json、ST case.json、st_report.json 五类制品,分别对应"代码、部署包、性能可视化、测试输入、测试报告"全生命周期。

### 端到端数据流(原文 3.3)

```
Operator JSON ──→ [JSON Parser] ──→ 算子描述结构体
                                       │
                                [Template Engine] ──→ 算子工程目录
                                       │
                                [用户编写 Kernel 实现]
                                       │
                              [build.sh 编译] ──→ .run 部署包
                                       │                               
                                [msopst create]                       
                                       │                                     
                                ST 用例 .json   
                                       │                         
                                [msopst run]                       
                                       │                                 
                                st_report.json                           
```

**数据流解读(原文)**:
该数据流刻画了从 JSON 原型到测试报告的完整闭环:首先将 Operator JSON 经 JSON Parser 转为内部"算子描述结构体";再交由 Template Engine 生成算子工程目录;随后开发者专注 Kernel 实现,通过 `build.sh` 编译产出 `.run` 部署包;继而由 `msopst create` 派生 ST 用例 `.json`;最终由 `msopst run` 在硬件上执行测试并落地 `st_report.json`。该流水线覆盖了"原型 → 工程 → 二进制 → 测试用例 → 测试报告"的五个阶段。

---

## 【表格解读】

### 表格 1:Feature List(原文 1.2)

| Type | Feature | Description |
|-----|------|------|
| Core | Operator Project Generation | Generates complete Ascend C/TBE/AI CPU operator projects from JSON prototypes |
| Core | Multi-Framework Adaptation | Supports TensorFlow, PyTorch, MindSpore, ONNX frameworks and aclnn direct invocation |
| Core | Operator Append | Supports appending new operators to existing projects (`-m 1` mode) |
| Core | Simulation Pipeline Visualization | Parses performance simulation dump data to generate Chrome tracing views |
| Core | Compilation & Deployment | Generates build.sh compilation scripts and .run deployment packages |
| Support | ST Testing | msOpST tool auto-generates test cases and executes them on hardware |
| Support | On-Board Test Framework | msOpST ascendc_test generates kernel direct-invoke test framework |

**逐行解读**:
- 第 1 行 **Operator Project Generation**:msOpGen 的核心能力,从 JSON 原型直接产出 Ascend C / TBE / AI CPU 三类算子工程,覆盖最常用的算子开发形态。
- 第 2 行 **Multi-Framework Adaptation**:通过统一 JSON 接口屏蔽 TensorFlow / PyTorch / MindSpore / ONNX / aclnn 框架差异,降低多框架适配学习成本。
- 第 3 行 **Operator Append**:以 `-m 1` 模式向已有工程增量追加新算子,避免每次都重新生成整个工程。
- 第 4 行 **Simulation Pipeline Visualization**:对接性能仿真链路,把 dump 数据解析为 Chrome tracing 可视化视图,辅助性能瓶颈定位。
- 第 5 行 **Compilation & Deployment**:产物级封装,自动生成 `build.sh` 编译脚本与 `.run` 部署包,使生成工程"开箱即用"。
- 第 6 行 **ST Testing**:msOpST 子工具自动生成 ST 测试用例并上板执行,打通测试闭环。
- 第 7 行 **On-Board Test Framework**:`msOpST ascendc_test` 产出 kernel 直调测试框架,用于绕过整图直接验证 kernel 行为。

### 表格 2:Design Goals(原文 2)

| Design Goal | Description |
|---------|------|
| **Completeness** | Generated projects can be compiled and deployed directly without manual framework code |
| **Multi-Framework Coverage** | Unified JSON interface adapts to multiple AI frameworks, reducing learning costs |
| **Configurable Build** | Flexible configuration of build options, chip models, and distribution modes via CMakePresets.json |
| **CLI Usability** | Clear and intuitive parameter design with sensible defaults |

**逐行解读**:
- **Completeness**:把"无需手动编写框架代码"作为底线指标,确保生成物即可编译、即可部署,杜绝"半成品工程"。
- **Multi-Framework Coverage**:强调以统一 JSON 接口屏蔽框架差异,把学习曲线收敛到 JSON 协议本身。
- **Configurable Build**:将构建选项、芯片型号、分发模式三者的灵活性统一收敛到 `CMakePresets.json`,提供声明式配置入口。
- **CLI Usability**:命令参数设计追求"清晰直观 + 合理默认值",降低使用者上手门槛。

### 表格 3:Module Division(原文 3.2)

| Module | Responsibility | Input | Output |
|------|------|------|------|
| JSON Parser | Parse and validate operator prototype definition files | `*.json` prototype | Structured operator description |
| Template Engine | Generate project templates from operator description and chip model | Operator description + soc_version | Complete operator project directory |
| Dump Analyzer | Parse performance simulation dump data | Dump data files | trace.json pipeline visualization |
| Project Builder | Generate CMakeLists.txt, CMakePresets.json, build.sh | Operator description + build options | Buildable project |
| ST Test Generator | Parse Host-side source code to generate ST test cases | `op_host/*.cpp` | `*_case.json` |
| ST Test Runner | Execute hardware tests and generate reports | `*_case.json` + soc | `st_report.json` |

**逐行解读**:
- **JSON Parser**:工具链的最上游,把 `*.json` 原型文件解析、校验为结构化"算子描述",是后续所有模块的输入源。
- **Template Engine**:核心生成模块,根据"算子描述 + soc_version(芯片型号)"生成完整工程目录,把芯片平台差异封装在模板层。
- **Dump Analyzer**:独立于代码生成链路的旁路分析器,负责把性能仿真 dump 文件解析成 trace.json,供 Chrome tracing 展示。
- **Project Builder**:与 Template Engine 协作,专门生成构建系统文件(CMakeLists.txt / CMakePresets.json / build.sh),把"代码生成"与"工程集成"解耦。
- **ST Test Generator**:通过扫描 `op_host/*.cpp` 自动派生测试用例 `*_case.json`,体现"用工程反推测试用例"的设计思路。
- **ST Test Runner**:上板测试执行器,接受 `*_case.json` + 芯片型号,产出 `st_report.json`,完成测试闭环。

---

## 【公式解读】

**原文无公式**。

(说明:本文档为架构设计说明性质,未涉及任何数学公式、伪代码公式或算法表达式;所有机制均以表格、ASCII 架构图与文字段落形式呈现。)

---

## 【关联】

> 内部链接说明:本文档原文标注 **(无)**,即不含任何站内 anchor 链接。本节改以"模块/工具/产物"维度梳理文档内出现的全部横向引用关系。

### 横向模块依赖关系

- **CLI 层 ↔ 核心引擎层**:`msopgen gen` 触发 JSON Parser + Template Engine + Project Builder 组合;`msopgen sim` 单独触发 Dump Analyzer;`msopst` 触发 ST Test Generator + ST Test Runner。
- **Template Engine ↔ Project Builder**:前者产出"代码层"目录,后者产出"构建系统层"文件,二者协同才能形成可编译工程。
- **JSON Parser ↔ Template Engine**:JSON Parser 的输出("算子描述结构体")是 Template Engine 的输入,二者形成严格的"解析 → 生成"管道。
- **Dump Analyzer ↔ 性能仿真**:独立于代码生成主链路,与"性能优化"工作流绑定,与主生成链路无强耦合。

### 上下游工具/产物关系

- **msOpGen ↔ msOpST**:本文档明确将 msOpST 定位为 Support 级配套工具,与 msOpGen 形成"工程生成 → 测试验证"上下游。msOpST 内部又细分为 `msOpST`(上板用例生成与执行)与 `msOpST ascendc_test`(kernel 直调测试框架)两个子能力。
- **工程产物 ↔ 部署产物**:Template Engine 产出算子工程目录 → Project Builder 产出 build.sh → 用户触发 build.sh → 产出 `.run` 部署包;该链路体现"生成 → 构建 → 部署"的纵向串联。
- **测试链路上下游**:ST Test Generator(`op_host/*.cpp` → `*_case.json`)→ ST Test Runner(`*_case.json` + soc → `st_report.json`),二者形成"用例生成 → 用例执行"的两阶段闭环。
- **分发模式 ↔ 上层应用**:Source Distribution 模式向上服务于"在线编译 + ATC 模型转换"场景;Binary Distribution 模式向上服务于"算子二进制直调"场景,二者在 CMakePresets.json 中按需切换。

---

## 【使用方法】

(以下内容均出自原文,未引入任何文档外信息)

### CLI 命令入口(原文 3.1 + 1.2)

- `msopgen gen`:生成算子工程(默认模式)。
- `msopgen gen -m 1`:以"Operator Append"模式向已有工程追加新算子。
- `msopgen sim`:解析性能仿真 dump 数据,生成 Chrome tracing 可视化所需的 trace.json。
- `msopst`:ST 测试入口,内部又分两个子能力:
  - `msopst create`:从 `op_host/*.cpp` 自动生成 ST 测试用例 `*_case.json`。
  - `msopst run`:在指定 soc(芯片型号)上执行 `*_case.json`,产出 `st_report.json`。
- `msOpST ascendc_test`:生成 kernel 直调测试框架,用于绕过整图直接验证 kernel 行为。

### 构建与分发配置(原文 2 + 4.3)

- **构建配置入口**:通过 `CMakePresets.json` 灵活配置 build options、chip models、distribution modes。
- **两种分发模式(由 CMakePresets.json 切换)**:
  - **Source Distribution**:保留 kernel 源码 `.cpp`,支持在线编译与 ATC 模型转换。
  - **Binary Distribution**:编译产出 `.o` 与 `.json` info 文件,用于算子二进制直调。

### 输出制品清单(原文 3.1 + 3.3)

| 触发方式 | 产出制品 |
|---------|---------|
| `msopgen gen` | 算子工程目录(含 CMakeLists.txt / CMakePresets.json / build.sh) |
| `build.sh` 编译 | `.run` 部署包 |
| `msopgen sim` | `trace.json`(Chrome tracing 可视化输入) |
| `msopst create` | `*_case.json` ST 测试用例 |
| `msopst run` | `st_report.json` 上板测试报告 |

### 工程构建脚本(原文 5)

- `setup.py`:msOpGen 自身的 WHL 包构建脚本。
- `build.py`:msOpGen 自身的构建入口脚本。

### 命名规则(原文 4.2)

- 算子类型名采用 PascalCase,生成的文件名与 kernel 函数名采用 snake_case。
- 转换示例:`AddCustom` → `add_custom.cpp` / `add_custom`。该映射在 Template Engine 中由命名规则模块强制执行,避免手工命名漂移。
```

---

> **解读小结**:整篇文档以"CLI → Core Engine → Output"三层骨架为经,以"JSON 解析 → 模板生成 → 工程构建 → ST 测试"的流水线为纬,把算子工程从原型定义到测试报告的全生命周期做了端到端的职责切分。表格系统(feature / design goal / module)三件套共同支撑了"能力清单—设计原则—模块边界"的自洽闭环;而内部无 anchor 链接这一事实本身,说明该架构文档是一份"独立完备的总览图",不依赖仓内其他页面即可独立阅读。

## 图文联合解读

- `msopgenclass.png`: **1) 图示内容**：双层级UML类图。上层为`OpFileGenerator`通过`OpFile`基类派生出4个交付件生成器（MindSporeAiCore/AiCore/AiCpu/MindSporeAiCpu）；下层为`OpInfoParser`通过`OpInfo`基类派生出6个IR解析器（excel/txt/json × MindSpore/通用）。标注含"依赖""实现""继承"。

**2) 技术结论**：采用"工厂+策略+模板方法"架构——生成器按硬件平台分流，解析器按IR源格式分流，基类封装公共逻辑，ArgsParser统一驱动。

**3) 与文档对应**：直观印证特性表中"多框架适配"（TF/MindSpore/IR/JSON）与"算子项目生成"两项核心功能的设计落地路径。
