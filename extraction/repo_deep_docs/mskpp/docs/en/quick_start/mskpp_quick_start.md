# msKPP Quick Start

> 仓 `mskpp` · 路径 `docs/en/quick_start/mskpp_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mskpp/docs/en/quick_start/mskpp_quick_start.md

# msKPP Quick Start 深度解读

## 【定位】

本文档是 msKPP（Ascend 算子性能建模工具）的快速入门指南，聚焦于"算子开发前的性能建模设计"环节：开发者基于专用 DSL 编写算子执行流程的 Python 脚本，在无需真实硬件与实际计算的情况下，仅凭输入/输出规模即可在秒级获得性能预测数据，从而快速验证算子实现方案的可行性。

---

## 【技术要点】

1. **工具本质**：msKPP 不是可执行程序，而是面向 Ascend 的 Python 类库，需导入模块、编写并执行 Python 脚本来生成 profiling 结果文件（`trace.json`、`Instruction_statistic.csv`、`Pipe_statistic.csv`）。
2. **核心机制**：内部预先采集真实环境中各指令操作的 profile 数据，再基于用户自定义的算子执行流程进行建模估算；典型流程为"导入指令（如 `vadd`）+ tensor + chip → `with` 语句进入上下文 → 创建 tensor → 执行具体操作"。
3. **Python 依赖校验命令**（一次性命令）：
   ```shell
   python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"
   ```
   要求输出 `All is OK`；其中 `numpy` 版本必须 **≤ 1.26.4**。
4. **工作空间**：示例脚本创建于 `~/ot_demo/workspace/mskpp`；通过 `with Chip("xxx") as chip` 上下文管理器进入，其中 `xxx` 需替换为实际芯片 SoC 类型（格式为 `Ascendxxxyy`）。
5. **示例数据形态**：三个 GM tensor `in_x / in_y / in_z`，dtype 均为 `FP16`，shape 均为 `[32, 48]`，format 为 `ND`；算子数据通路为 `GM-UB`（输入 `x`、`y` 加载）→ UB 上 `vadd` 计算 → `UB-GM`（结果 `z` 回写）。
6. **示例建模结果摘要**（来自示例脚本生成）：
   - `MOV-UB_TO_GM` 用时最长、cycle 数最多（**Duration 0.4254 µs / 787 cycle**），为关键路径；
   - `VADD` 计算最快（**0.0135 µs / 25 cycle / 1536 Ops**）；
   - `MOV-GM_TO_UB` 居中（**0.3081 µs / 570 cycle**）。

---

## 【关键机制与数据】

**工作原理**（原文："The internal principle involves pre-collecting profile data of various instruction operations in real environments, then modeling and estimating various performance overheads based on the user-defined operator execution flow."）：msKPP 基于"预采集的真实指令 profile"+"用户用 DSL 描述的执行流"两路输入，对每条指令的耗时/cycle/数据搬运量等指标做估算。

**数据流（以 `my_vadd` 为例）**：
1. 在 UB 上定义三个 Tensor `x / y / z`；
2. `x.load(gm_x)`、`y.load(gm_y)`：把 GM 输入搬到 UB（对应 `MOV-GM_TO_UB`）；
3. `out = vadd(x, y, z)()`：调用 vector add 指令计算，结果保留在 UB（对应 `VADD`）；
4. `gm_z.load(out[0])`：把结果从 UB 写回 GM（对应 `MOV-UB_TO_GM`）；
5. `chip.enable_trace()` 与 `chip.enable_metrics()` 分别启用流水线图（`trace.json`）与单指令/流水线统计（`Instruction_statistic.csv`、`Pipe_statistic.csv`）。

**性能数据**（原文）：示例规模 `[32, 48] FP16` 下，三条指令的 Duration/Cycle/Size/Ops 见上节第 6 条；其中回写阶段 cycle 数（787）大于加载（570）+计算（25）之和，回写确为瓶颈。

**运行命令**（原文）：`python3 mskpp_demo.py`，执行成功后自动在当前目录生成 `MSKPP{timestamp}/` 结果目录。

---

## 【表格解读】

> 原文无表格。
>
> 说明：原文中以 markdown 表格形式展示的 `Instruction_statistic.csv` 内容，按原文逐字还原如下：

| Instruction    | Duration(us) | Cycle | Size(B) | Ops  |
|:--------------:|:------------:|:-----:|:-------:|:----:|
| MOV-GM_TO_UB   | 0.3081       | 570   | 6144    | -    |
| VADD           | 0.0135       | 25    | -       | 1536 |
| MOV-UB_TO_GM   | 0.4254       | 787   | 3072    | -    |

**逐行解读**：
- **MOV-GM_TO_UB（GM → UB 搬运）**：耗时 0.3081 µs、cycle 570、搬运 6144 字节（≈ `32×48×2B × 2` 个 FP16 tensor 总和）。是两次 GM→UB 加载操作的合计开销，属于算子的"输入侧"开销。
- **VADD（向量加）**：耗时 0.0135 µs、cycle 25、Ops=1536（即 `32×48=1536` 个元素的逐元素加法）。计算本身极快，远小于搬运开销，体现出该规模下算子是"搬运受限"而非"计算受限"。
- **MOV-UB_TO_GM（UB → GM 搬运）**：耗时 0.4254 µs、cycle 787、搬运 3072 字节（≈ `32×48×2B` 单个 FP16 tensor）。耗时与 cycle 数在三行中均为最高，是当前配置下的关键路径（critical path）。

**关键洞察**（原文）：当 `MOV-UB_TO_GM` 这类搬运指令主导执行时间时，优化方向应优先考虑调整 **data tiling 策略**或选用 **更高效的搬运指令**，而不是去优化计算指令本身。

---

## 【公式解读】

原文无公式。

> 备注：文档未给出任何 LaTeX/伪代码形式的数学公式；建模结果以 CSV 表格呈现，无显式公式推导。

---

## 【关联】

**文档内引用**：
- **msKPP API Reference**（`../api_reference/mskpp_api_reference.md`）：用于查阅 `vadd`、`Tensor`、`Chip` 等"指令 API"的详细参数；本文示例仅展示了 DSL 的最小用法，更复杂指令需以此 API 参考为准。
- **Ascend Operator Development Toolchain Quick Start**（外部 `op_tool_quick_start.md`）：本文假设读者已完成该前置教程中的所有操作，是阅读本文的前置条件。
- **Ascend AI Operator Development Toolchain Learning Environment Installation Guide**（外部 `installation_guide.md`）：本文要求严格按该指南完成环境安装与工作空间配置；即使用户已具备相似环境，仍建议重新执行一次以保证依赖与环境变量一致。
- **Chip SoC Type Obtaining Method**（外部 `get_chip_soc_type.md`）：用于获取实际芯片类型并替换示例代码 `with Chip("xxx")` 中的 `xxx`。

**上下游关系**：
- **上游**：本文属 "quick_start" 系列，承接算子工具链的安装与环境配置（`installation_guide.md`、`op_tool_quick_start.md`）。
- **下游**：示例脚本 `my_vadd` 依赖 `mskpp_api_reference.md` 中定义的指令/类 API；输出的 `Instruction_statistic.csv` / `Pipe_statistic.csv` / `trace.json` 将用于后续性能分析与算子实现方案调优。

---

## 【使用方法】

**1. 前置环境校验（一次性命令）**：
```shell
python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"
```
输出 `All is OK` 方可继续；否则按 §1.2 的安装指南修复。

**2. 创建建模工作空间**：
```shell
rm -rf ~/ot_demo/workspace/mskpp && mkdir -p ~/ot_demo/workspace/mskpp && cd ~/ot_demo/workspace/mskpp
```

**3. 编写建模脚本**（`mskpp_demo.py`）：
- `from mskpp import vadd, Tensor, Chip` 导入 DSL；
- 在 `with Chip("xxx") as chip:` 上下文中建模（`xxx` 按 `get_chip_soc_type.md` 获取并替换为实际值）；
- `chip.enable_trace()` —— 启用"算子模拟流水线图"，生成 `trace.json`；
- `chip.enable_metrics()` —— 启用"单指令与流水线信息"，生成 `Instruction_statistic.csv` 与 `Pipe_statistic.csv`；
- 创建示例 GM tensor：`Tensor("GM", "FP16", [32, 48], format="ND")`，共三个（`in_x`、`in_y`、`in_z`），调用自定义函数 `my_vadd(in_x, in_y, in_z)` 完成一次加法算子的端到端建模。

**4. 执行建模**：
```shell
python3 mskpp_demo.py
```
成功后当前目录自动生成 `MSKPP{timestamp}/`，内含：
```
MSKPP{timestamp}/
├── Instruction_statistic.csv
├── Pipe_statistic.csv
└── trace.json
```

**5. 查看与解读**：
- 打开 `Instruction_statistic.csv`，关注 `Duration(us)` 与 `Cycle` 两列，定位耗时最长、cycle 最多的指令；
- 原文示例中 `MOV-UB_TO_GM`（0.4254 µs / 787 cycle）即为关键路径；
- 进一步优化方向（按原文）：**优先调整 data tiling 策略，或改用更高效的搬运指令**。
