# msKPP 算子建模工具快速入门

> 仓 `mskpp` · 路径 `docs/zh/quick_start/mskpp_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mskpp/docs/zh/quick_start/mskpp_quick_start.md

# msKPP 算子建模工具快速入门 — 深度解读

## 【定位】

本文档是昇腾算子开发工具链中 **msKPP 性能建模工具** 的入门级指南，目标是让开发者以一个简易加法（vadd）算子为例，**在算子实现之前基于 DSL 仅靠输入/输出规模即可秒级获得性能预测**，从而快速验证算子实现方案的可行性，而无需真实硬件或执行真实计算。

---

## 【技术要点】

1. **DSL 驱动的秒级建模**：msKPP 不是传统可执行程序，而是一套 **专用于昇腾的 Python 类库**；用户 `import` 模块后编写并执行 Python 脚本，生成性能分析结果文件。内部原理是 **预先采集真实环境中各类指令操作的性能数据**，再基于用户定义的算子执行流程进行性能开销建模与估算。
2. **环境强约束**：教程 **仅支持标准化 CANN 容器环境**，不兼容裸机/虚拟机/非标容器；强制前置自检脚本检查 `/.dockerenv`、`$ASCEND_HOME_PATH`、`$ATB_HOME_PATH` 及 `~/ot_demo/msot/example/quick_start` 目录，必须全部 `[PASS]` 才可继续。
3. **DSL 三要素导入**：常规开发流程需要 **导入 `Tensor`、`Chip` 以及算子实现必需的指令**（例如 `vadd`），通过 `with` 语句进入算子实现上下文，再创建 Tensor 执行具体操作。
4. **芯片类型动态获取**：示例中 `with Chip("xxx") as chip` 的占位符须替换为真实 SoC 类型；通过 `python3 -c "import acl; print(acl.get_soc_name())"` 查询（示例形态：`Ascendxxxyy`）。
5. **建模流水线三件套输出**：执行成功后会在当前目录生成 `MSKPP{timestamp}` 结果目录，含 `instruction_cycle_consumption.html`、`Instruction_statistic.csv`、`Pipe_statistic.csv`、`trace.json` 四个产物。
6. **关键指令级 Profile 指标**：表格示例展示每条指令的 `Duration(us)`、`Cycle`、`Size(B)`、`Ops`，其中 `MOV-UB_TO_GM` 耗时 **0.4254 us / 787 cycle** 是 vadd 算子关键路径；优化方向是 **优先考虑数据复用（Tiling）策略或更高效的搬运指令**。

---

## 【关键机制与数据】

### 工作原理（原文表述）

> "msKPP 并非传统可执行程序，而是一套专用于昇腾的 Python 类库……其内部原理是：预先采集真实环境中各类指令操作的性能数据，再基于用户定义的算子执行流程，对各种性能开销进行建模与估算。"

- 用户输入：算子的**数学逻辑（DSL 表达式）**。
- 建模依据：**输入/输出规模**（Tensor 形状/格式/数据类型），无需真实计算。
- 输出：秒级性能预测结果 + trace 文件。

### 数据通路（以 vadd 为例，原文）

```
gm_x  ─GM→UB─►  x (UB)
gm_y  ─GM→UB─►  y (UB)
                    │
              vadd(x, y, z)()  ─►  out[0] (UB)
                    │
gm_z  ◄─UB→GM─  out[0]
```

### 环境自检关键路径（原文）

```bash
[ -f /.dockerenv ] && [ -n "$ASCEND_HOME_PATH" ] && [ -n "$ATB_HOME_PATH" ]
```
四项必须全 PASS：容器标志、ASCEND_HOME_PATH、ATB_HOME_PATH、示例代码仓 `~/ot_demo/msot/example/quick_start`。

### 性能数据（原文：Instruction_statistic.csv 真实样例）

| Instruction | Duration(us) | Cycle | Size(B) | Ops |
|:--:|:--:|:--:|:--:|:--:|
| MOV-GM_TO_UB | 0.3081 | 570 | 6144 | - |
| VADD | 0.0135 | 25 | - | 1536 |
| MOV-UB_TO_GM | 0.4254 | 787 | 3072 | - |

**耗时最长 → MOV-UB_TO_GM（0.4254 us / 787 cycle）**，原文判定为性能优化关键路径。

### 样例张量规格（原文）

| 变量 | 位置 | dtype | shape | format |
|:--:|:--:|:--:|:--:|:--:|
| `in_x` | GM | FP16 | `[32, 48]` | ND |
| `in_y` | GM | FP16 | `[32, 48]` | ND |
| `in_z` | GM | FP16 | `[32, 48]` | ND |

---

## 【表格解读】

原文给出两张关键表格，逐字还原并逐行解读。

### 表格 1：vadd 算子指令级统计（原文 `Instruction_statistic.csv` 样例）

| Instruction | Duration(us) | Cycle | Size(B) | Ops |
|:--:|:--:|:--:|:--:|:--:|
| MOV-GM_TO_UB | 0.3081 | 570 | 6144 | - |
| VADD | 0.0135 | 25 | - | 1536 |
| MOV-UB_TO_GM | 0.4254 | 787 | 3072 | - |

**逐行解读**：

- **MOV-GM_TO_UB（GM→UB 数据搬入）**：耗时 **0.3081 us / 570 cycle**，搬运数据 **6144 字节**。Ops 字段为空（搬运类指令无 Op 计数）。该步对应 `x.load(gm_x)` 与 `y.load(gm_y)`，分别搬运 32×48×2B=3072B 两次，总 6144B。
- **VADD（向量加法计算）**：耗时 **0.0135 us / 25 cycle**，**Ops = 1536**。Ops 反映向量加法的元素操作总数（即 32×48=1536 个 FP16 元素逐对相加）。计算耗时极短，远低于搬运耗时。
- **MOV-UB_TO_GM（UB→GM 数据搬出）**：耗时 **0.4254 us / 787 cycle**，搬运 **3072 字节**（单输出 z 的 32×48×2B）。Ops 字段为空。该指令是 **整个 vadd 算子的关键路径**，cycle 数最大。

> 原文结论：在算子时长结构中，**计算本身占比极低（仅 25 cycle），性能瓶颈完全来自内存搬运**；当搬运耗时占比过高时，应 **优先优化数据复用（Tiling）或选用更高效搬运指令**。

### 表格 2：样例张量规格（原文 DSL 代码中的实参）

| 变量 | 位置 | dtype | shape | format |
|:--:|:--:|:--:|:--:|:--:|
| `in_x` | GM | FP16 | `[32, 48]` | ND |
| `in_y` | GM | FP16 | `[32, 48]` | ND |
| `in_z` | GM | FP16 | `[32, 48]` | ND |

**解读**：三个张量在 GM（Global Memory，全局内存）上以 ND（默认稠密）布局、FP16 半精度存储，规模均为 32×48（即 1536 元素、3072 字节/张量）。这是 DSL `Tensor("GM", "FP16", [32, 48], format="ND")` 的字面参数示例，说明建模仅依赖 **形状 + dtype + format** 这类规模/布局信息，而非真实数据。

---

## 【公式解读】

**原文无公式**（无 LaTeX 数学式或伪代码公式块）。

但 DSL 中存在 **关键调用语法**（虽非公式，但作为算子表达式承载数学逻辑）：

```python
out = vadd(x, y, z)()
```

含义逐符号说明：
- `vadd` —— msKPP DSL 中预定义的 **向量加法指令类**（需 `from mskpp import vadd` 导入）。
- `(x, y, z)` —— 构造指令：传入三个 UB Tensor，`x`、`y` 为输入，`z` 为输出占位。
- `()` —— **触发执行**（DSL 中的可调用约定，调用后才建模其开销）。
- `out` —— 返回值为元组，通过 `out[0]` 取第 0 个元素（计算结果所在 UB Tensor）。

此外，DSL 中的 **上下文与使能语句**：

```python
with Chip("xxx") as chip:
    chip.enable_trace()     # 生成 trace.json
    chip.enable_metrics()   # 生成 Instruction_statistic.csv 与 Pipe_statistic.csv
```

- `Chip("xxx")` —— 建模目标芯片（SoC）。
- `enable_trace()` —— 使能 **算子模拟流水图** 输出。
- `enable_metrics()` —— 使能 **单指令级及分 PIPE 级流水统计** 输出。

---

## 【关联】

文档依托于昇腾算子开发工具链的上下游体系：

- **前置文档**（外部 gitcode 链接）：
  - 《算子开发工具链快速入门》——前提为已完成该全流程；意味着 msKPP 是 **算子开发流水线中"建模设计"阶段** 的工具，承接在环境搭建之后、算子实现之前。
  - 《昇腾 AI 算子开发工具链学习环境安装指南》——容器环境与示例代码仓来源。

- **下游/配套文档**（内部链接）：
  - 《msKPP 工具接口说明》（`../api_reference/mskpp_api_reference.md`）——本文中明确指引："其他指令接口说明请参考《msKPP 工具接口说明》"，用于查阅 DSL 中各类指令（如 `vadd` 之外的 `vsub`、`vmul`、各类 `MOV`、`Tensor.load` 等）的完整接口签名。

- **横向能力位置**：msKPP 与 msProf、msToolkit 等共同构成"算子开发工具链（msot）"；本文档位于该工具链的 **quick_start（入门）层**，对应的 **api_reference（接口参考）层** 即为上述 `mskpp_api_reference.md`。

- **数据流向关联**：建模输入（DSL 表达式 + Tensor 规模）→ 建模输出（trace.json + 两个 csv）→ 用户基于 `Instruction_statistic.csv` 中的指令耗时与 cycle 数 **识别关键路径** → 反馈到算子实现阶段的 **Tiling/搬运指令选型** 决策。

---

## 【使用方法】

### 启用方式（原文逐步骤）

1. **环境准备**：完成 CANN 容器安装（外网可达环境下约 **3 分钟**）。
2. **环境自检**：执行自检脚本，须 4 项全 `[PASS]`（容器标志、`ASCEND_HOME_PATH`、`ATB_HOME_PATH`、示例代码仓）。
3. **创建工作区**：
   ```shell
   rm -rf ~/ot_demo/workspace/mskpp && mkdir -p ~/ot_demo/workspace/mskpp && cd ~/ot_demo/workspace/mskpp
   ```
4. **编写 Python 脚本**：保存为 `mskpp_demo.py`，包含 `from mskpp import vadd, Tensor, Chip` 三要素、`Chip` 上下文、`enable_trace()` + `enable_metrics()` 两项使能。
5. **替换芯片占位符**：执行 `python3 -c "import acl; print(acl.get_soc_name())"` 查询 SoC 名（如 `Ascendxxxyy`），替换 `with Chip("xxx") as chip`。
6. **执行建模**：
   ```shell
   python3 mskpp_demo.py
   ```
   成功后将自动在当前目录生成 `MSKPP{timestamp}/` 结果目录。

### 关键配置项（原文涉及）

| 配置项 | 位置 | 作用 | 原值/示例 |
|:--|:--|:--|:--|
| `Tensor("UB"\|"GM", dtype, shape, format=...)` | DSL 参数 | 指定张量所在内存位置、类型与布局 | `"GM"/"UB"`、`"FP16"`、`[32,48]`、`format="ND"` |
| `Chip("xxx")` 上下文 | DSL 顶层 | 指定建模目标 SoC | 占位符 `xxx`，须用 `acl.get_soc_name()` 替换 |
| `chip.enable_trace()` | Chip 上下文内 | 使能模拟流水图，生成 `trace.json` | 开关式调用 |
| `chip.enable_metrics()` | Chip 上下文内 | 使能指令/PIPE 级流水统计，生成两个 csv | 开关式调用 |
| 指令调用 `vadd(x,y,z)()` | DSL 算子体 | 执行并建模一次向量加法 | `(x,y,z)` 构造 + `()` 触发 |

### 命令汇总（原文出现）

| 命令 | 用途 |
|:--|:--|
| `python3 -c "import acl; print(acl.get_soc_name())"` | 查询当前 SoC 名 |
| `python3 mskpp_demo.py` | 执行性能建模 |

> **注意事项**（原文强调）：msKPP 仅支持 CANN 容器环境；DSL 是昇腾专用"方言"，需专门学习，但"用法较简单，稍加学习即可应用"；结果目录命名格式为 `MSKPP{timestamp}`，其中 `instruction_cycle_consumption.html` 提供可视化的指令周期消耗流水图，便于结合 csv 一起判读关键路径。
