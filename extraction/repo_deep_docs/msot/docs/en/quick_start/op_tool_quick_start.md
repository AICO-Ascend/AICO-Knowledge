# Operator Development Toolchain Quick Start

> 仓 `msot` · 路径 `docs/en/quick_start/op_tool_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/en/quick_start/op_tool_quick_start.md

# 一体化深度解读: Operator Development Toolchain Quick Start

## 【定位】

本文是 MindStudio 算子开发工具链的「端到端体验型快速入门」指南:以一个最简加法算子(add)为例,把算子开发拆成 6 个阶段(环境准备 → 算子设计 → 工程生成 → 异常检测 → 原生调试 → 性能调优),用 10 分钟级操作让用户"先跑通、后理解",从而直观感受 `msKPP / msOpGen / msSanitizer / msDebug / msOpProf` 等工具带来的效率提升。

---

## 【技术要点】

1. **6 阶段工具链流水线**:Step 1=CANN 环境准备(容器 ≤5 min,裸机 ≥20 min) → Step 2=`msKPP` 算子性能建模(30 秒) → Step 3=`msOpGen` 工程生成(1 分钟) → Step 4=`msSanitizer` 异常检测(1 分钟) → Step 5=`msDebug` 原生调试(1 分钟) → Step 6=`msOpProf` 性能调优(1 分钟)。Step 1 是前置基础;Step 2、3 完成后可独立分支;Step 4、5、6 都依赖 Step 3 的工程,但三者相互独立,可按需学习。

2. **学习专用环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE`**:必须正确配置(如 `910B4`、`910_9392`);变量为空会导致后续步骤频繁报运行时错误。原文强调:该变量**仅用于学习环境,严禁用于官方商用版本**。

3. **Python 依赖与版本硬约束**:需安装 `numpy / sympy / scipy / attrs / psutil / decorator` 六个包,且 `numpy.__version__ <= '1.26.4'`,通过 `python3 -c "..."` 单行命令一次性校验,输出 `All is OK` 才算通过。

4. **`msKPP` 的本质是 Python 类库而非可执行程序**:用户需自行 import `Tensor / Chip` 及所需指令(如 `vadd`),用 `with` 语句进入算子实现上下文,创建 Tensor 完成操作;其内部原理是"在真实环境中预采集各指令性能数据,再根据用户定义的算子执行流进行建模与耗时估算"。

5. **`msKPP` DSL 是 Ascend 专属"方言"**:不能用通用 Python 语法直接写,需专门学习;但接口较简单,简短学习即可上手,且**支持复制粘贴命令执行**(全文以 `cp -f` / `mkdir -p` 等 shell 命令驱动)。

6. **`msOpGen` 通过自定义 JSON 输入配置文件生成算子工程**:类比 C 函数声明,需定义函数名、输入参数、返回值类型;工具只生成空壳函数(仅有签名),函数体由用户实现,可避免重复的项目搭建与编译配置工作。

---

## 【关键机制与数据】

- **原文(性能瓶颈判定)**:在 `Instruction_statistic.csv` 中,MOV-UB_TO_GM 时延 0.4254 µs / 周期 787,均为三项指令中最高,是优化的关键路径(数据从 UB 搬回 GM 的开销)。优化方向为**数据复用(Tiling)**或换用更高效的搬运指令。

- **原文(建模输入数据规模)**:算例中 VADD 指令 `Ops=1536`;MOV-GM_TO_UB 的搬运 Size=6144 B,MOV-UB_TO_GM 的搬运 Size=3072 B(典型 GM↔UB 非对称的输入/输出数据量)。

- **原文(`msKPP` 内部原理)**:在真实硬件上**预采集各类指令操作的性能数据**,再基于用户定义的算子执行流进行**性能开销的建模与估算**,从而实现"无需硬件即可估时"。

- **原文(`msKPP` 产物结构)**:
  ```
  MSKPP{timestamp}/
  ├── Instruction_statistic.csv   # 每条指令的耗时/周期/字节数/算子数
  ├── Pipe_statistic.csv          # 流水线级统计
  └── trace.json                  # 建模 trace
  ```

- **原文(`msOpGen` 输入与产物)**:输入是自定义 JSON 配置(如 `msopgen_demo.json`,含算子名、输入/输出变量名/类型/数据排布格式);产物是带空壳函数体的算子工程,函数体需用户自行实现。

- **原文(`msSanitizer / msDebug / msOpProf` 的角色)**:三者在 Step 3 生成的工程之上**相互独立**地工作,分别承担异常检测、原生调试、性能调优的职责(原文未给出三者具体技术细节,本文档被截断于 2.3.1)。

> **注意**:原文在 2.3.1 第 2 步"开发算子定义配置文件"处被截断,Step 4/5/6 的具体机制、数据、命令均未在原文提供范围内。

---

## 【表格解读】

### 表 1:Experience Map(核心操作 10 分钟)

> **Recommended Procedure**: Step 1 is the foundation; after completing Step 1, you can experience Step 2 or Step 3; Steps 4, 5, and 6 all depend on the project generated in Step 3, but these three are independent of each other and can be learned as needed.

| Step | Phase | Core Tools | Measured Operation Time | Recommended Theory Learning |
|:---:|:---:|:---|:---|:---|
| **1** | **Environment Preparation** | `CANN` | Container ≤ 5 minutes, Bare metal ≥ 20 minutes | 5 minutes |
| **2** | **Operator Design** | `msKPP` | 30 seconds | 5 minutes |
| **3** | **Project Development** | `msOpGen` | 1 minute | 20 minutes |
| **4** | **Anomaly Detection** | `msSanitizer` | 1 minute | 10 minutes |
| **5** | **Native Debugging** | `msDebug` | 1 minute | 10 minutes |
| **6** | **Performance Tuning** | `msOpProf` | 1 minute | 10 minutes |

**逐行解读**:
- **Row 1(Step 1,Environment Preparation)**:使用 `CANN` 完成环境就绪,**容器环境快(≤5 min),裸机慢(≥20 min)**——是流程唯一可能拖长总时长的环节;理论学习仅需 5 分钟,因为本文档提供了 1.2 节"环境准备"指引。
- **Row 2(Step 2,Operator Design)**:用 `msKPP` 在 30 秒内即可获得算子的性能建模结果——这正是工具链"秒级反馈"的核心卖点;理论 5 分钟足矣。
- **Row 3(Step 3,Project Development)**:用 `msOpGen` 在 1 分钟内自动生成完整算子工程框架,但**理论学习需 20 分钟**(6 步中最长),因涉及 JSON 输入规范、工程结构理解。
- **Row 4(Step 4,Anomaly Detection)**:用 `msSanitizer` 在已有工程上做 1 分钟异常检测,理论 10 分钟。
- **Row 5(Step 5,Native Debugging)**:用 `msDebug` 做 1 分钟原生调试,理论 10 分钟。
- **Row 6(Step 6,Performance Tuning)**:用 `msOpProf` 做 1 分钟性能调优,理论 10 分钟。

**结构性观察**:原文用"实测操作时间"(都是秒/分钟级)与"理论学习时间"(5–20 分钟)分离的方式,刻意区分"动手跑通"与"理解原理",引导读者**先体验后学习**——这是整篇 quick start 的方法论核心。

---

### 表 2:`Instruction_statistic.csv` 示例(原文逐字还原)

| Instruction | Duration (µs) | Cycle | Size(B) | Ops |
|:---:|:---:|:---:|:---:|:---:|
| MOV-GM_TO_UB | 0.3081 | 570 | 6144 | - |
| VADD | 0.0135 | 25 | - | 1536 |
| MOV-UB_TO_GM | 0.4254 | 787 | 3072 | - |

**逐行解读**:
- **Row 1(MOV-GM_TO_UB)**:从 Global Memory 搬运到 Unified Buffer,耗时 **0.3081 µs / 570 cycles**,搬运 **6144 B**;Ops 列为 `-`(搬运指令不计 Ops)。这是算子**输入侧**的数据搬运。
- **Row 2(VADD)**:核心计算指令,仅 **0.0135 µs / 25 cycles**,完成 **1536 个加法操作**;Size 列为 `-`(计算指令不计搬运字节)。计算本身的耗时占比极低——这是典型"算子瓶颈不在算、在搬"的体现。
- **Row 3(MOV-UB_TO_GM)**:从 UB 写回 GM,耗时 **0.4254 µs / 787 cycles**,搬运 **3072 B**;Ops 列为 `-`。**这是三条指令中耗时与周期都最长的**,被原文明确标注为"critical path"。
- **结构性观察**:输入 6144 B + 输出 3072 B = 总搬运 9216 B,而 VADD 仅 0.0135 µs,验证了"数据搬运占比远高于计算"这一 Ascend 算子优化的基本规律。

---

## 【公式解读】

**原文无公式**。原文中仅有以下伪代码/代码片段,均为命令或断言,不含数学公式:

- `assert version.parse(numpy.__version__) <= version.parse('1.26.4')` —— 这是 Python 版本断言,**不是公式**,仅表示"numpy 版本必须 ≤ 1.26.4"的硬约束。

---

## 【关联】

本文档是工具链的 **quick start 总览**,在结构上引用了以下资源,共同构成完整的上手链路:

1. **《Ascend AI Operator Development Toolchain Learning Environment Installation Guide》(installation_guide.md)** —— **1.2 节唯一强依赖**:环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 的配置方式、Python 包安装步骤、代码仓库 `~/ot_demo/msot/example/quick_start` 的就位方法,均在此文中说明;本文档 2.1.1 / 2.1.2 / 2.1.3 三处一旦校验失败,均回链到该文。

2. **《msKPP Tool Interface Description》(https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/api_reference/mskpp_api_reference.md)** —— 2.2.1 提及,用于查阅 DSL 中各类指令接口的详细说明(本文档不展开指令 API)。

3. **下游 6 阶段流水线内部依赖**(由原文"Recommended Procedure"明示):
   - Step 1 → Step 2 / Step 3(Step 1 是前置)
   - Step 2 → Step 3(msKPP 设计完成后做 msOpGen 工程生成)
   - Step 3 → Step 4 / Step 5 / Step 6(三者都依赖 Step 3 产出的工程,但**三者相互独立**,可任意选择学习顺序)
   - Step 4 / Step 5 / Step 6 三者**彼此独立**,无依赖

4. **隐式上下游**:
   - **上游**:CANN(Step 1 工具,提供 Ascend 算子开发基础运行时)。
   - **下游**:算子开发者实际交付的算子二进制/工程(经由 `msOpGen` → `msSanitizer` → `msDebug` → `msOpProf` 闭环产出)。

---

## 【使用方法】

> 以下均为**原文已显式给出的命令/配置**;原文未涉及之处标注"原文未涉及"。

### Step 0 工作区准备(原文已涉及)

```shell
mkdir -p ~/ot_demo/workspace/mskpp && cd ~/ot_demo/workspace/mskpp   # Step 2 工作区
mkdir -p ~/ot_demo/workspace/src && cd ~/ot_demo/workspace/src/      # Step 3 工作区
```

### Step 1 环境校验(原文已涉及,3 条命令)

```shell
# 1) 校验 SoC 环境变量
echo $MY_STUDY_VAR_CHIP_SOC_TYPE     # 期望非空,如 910B4 / 910_9392

# 2) 校验 Python 依赖(原文逐字保留)
python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"

# 3) 校验代码仓库就位
ls -al ~/ot_demo/msot/example/quick_start
```

### Step 2 算子建模设计 `msKPP`(原文已涉及)

```shell
# 复制预置 DSL 脚本
\cp -f ~/ot_demo/msot/example/quick_start/mskpp/mskpp_demo.py ./

# 执行建模,产物自动生成 MSKPP{timestamp}/ 目录(含 Instruction_statistic.csv / Pipe_statistic.csv / trace.json)
python3 mskpp_demo.py
```

### Step 3 算子工程生成 `msOpGen`(原文仅给出第 1 步;**第 2 步及之后在原文范围内被截断**)

- 已给出:创建 `~/ot_demo/workspace/src` 作为源码根目录。
- 已给出:复制 `msopgen_demo.json`(原文被截断于"copying the prepared configuration file")。
- **原文未涉及**:`msopgen` 的具体调用命令、生成的工程目录结构、算子空壳函数签名等(因原文截断)。

### Step 4 / 5 / 6:`msSanitizer / msDebug / msOpProf`

- **原文未涉及具体启用方式与命令**(原文表格中仅列出工具名与耗时,未给出步骤细节;Step 4/5/6 的具体操作在原文被截断部分之外)。

### FAQ(原文已提及但未展开)

- 原文 1.2 节末尾提到 **"3. FAQ"** 锚点 `#3-faq`,但**原文未提供 FAQ 内容**(原文截断前未触及该节)。
