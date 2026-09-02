# Quick Start of msProbe in the PyTorch Scenario

> 仓 `msprobe` · 路径 `docs/en/quick_start/pytorch_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprobe/docs/en/quick_start/pytorch_quick_start.md

# msprobe PyTorch 快速入门指南 深度解读

## 【定位】

本文档解决在 PyTorch 训练场景下，如何快速使用 MindStudio Probe（msProbe）精度调试工具完成"精度数据采集 + 精度比对"端到端流程的问题，使基于昇腾 NPU（尤其是从 GPU 迁移而来的）基础模型能够快速定位精度异常模块。

---

## 【技术要点】

1. **工具定位与适用场景**：msProbe 是面向昇腾的全场景精度工具链，用于 GPU→Ascend NPU 迁移训练时出现的精度溢出/下溢、loss 不收敛/发散等问题定位；典型场景包括 Atlas A2 训练服务器 + CANN 8.5.0 + PyTorch 2.9.0 + Python 3.12 + AArch64 + torchvision 0.24.0 的组合。
2. **五步精度调试流程**：①环境配置差异检查 → ②训练状态监控 → ③精度数据采集 → ④精度预检 → ⑤精度对比，本文聚焦于 ③ 和 ⑤。
3. **数据采集核心接口**：`msprobe.pytorch` 下的 `PrecisionDebugger` 与 `seed_all`，调用顺序为 `seed_all → PrecisionDebugger(config_path="./config.json") → debugger.start() → debugger.stop() → debugger.step()`；`seed_all(seed=1234, mode=True)` 用于固定随机种子并开启确定性计算。
4. **采集配置文件 `config.json`**：`task="statistics"`，`dump_path="/home/dump"`，`rank=[]`（表示全部 rank），`step=[0,1]`（dump 第 0、1 步），`level="L1"`，`async_dump=false`；统计子项 `data_mode=["all"]`，`summary_mode="statistics"`，`scope=[]` 与 `list=[]` 留空（采集全部 API）。
5. **GPU 端脚本补丁：`import torch_npu` 与 `from torch_npu.contrib import transfer_to_npu`（原文第 24、25 行），用于将 GPU 训练自动转移到 NPU。
6. **精度比对 CLI**：`msprobe compare -tp <gpu_dump.json> -gp <npu_dump.json> -o <output_dir>`，比对对象是 GPU 基准数据（`-gp`）与 NPU 待测数据（`-tp`），输出 Excel 结果文件 `compare_result_{timestamp}.xlsx`。

---

## 【关键机制与数据】

- **工作原理**：
  - **数据采集机制**：`PrecisionDebugger` 在训练迭代脚本中实例化并加载 `config.json`，通过 `start()` 开启前向/反向 API 输入输出数据的采集，`stop()`/`step()` 控制 dump 范围与 step 计数（同一 step 内多次开启会合并记录，跨 step 独立记录）。
  - **多 rank 目录策略**：原文指出"If the training process does not contain rank information, it will be saved in proc{pid} in the single-rank training scenario or rank{id} in the multi-rank training scenario"，即单 rank 用 `proc{pid}` 命名，多 rank 用 `rank{id}` 命名。
  - **固定随机种子机制**：`seed_all(seed=1234, mode=True)` 同步固定随机数并启用确定性计算，确保两次运行（GPU 与 NPU）模型执行数据一致，比对才有意义。
  - **比对结果机制**：`compare` 命令对每个 API 给出 `Result` 与 `Err_Message`，用于定位可疑算子；具体结果分析需参见 `pytorch_accuracy_compare_instruct.md#precision-comparison-result-analysis`。

- **数据流（dump 目录结构，原文逐字）**：

```txt
/home/dump/
├── step0
    └── proc3209296
        ├── construct.json          # 模块层级关系信息（当前场景下为空）
        ├── dump.json                # 前向/反向 API 输入输出统计与溢出/下溢信息
        └── stack.json               # API 调用栈信息
├── step1
...
```

- **性能/容量数据**（原文）：文档明确警告"Precision data occupies certain drive space"，其占用与"模型参数、采集配置、采集迭代次数"三项因素密切相关，未给出具体数字。

- **成功标志日志（原文）**：

```txt
****************************************************************************
*                        msprobe ends successfully.                        *
****************************************************************************
```

采集过程结束标志；比对过程结束标志为 `msprobe compare ends successfully.` 并附带 `compare_result_{timestamp}.xlsx` 路径。

---

## 【表格解读】

**原文无表格**。

（文档内仅存在配置示例、目录树、日志标志三类代码块/文本块，未提供参数表、对比表或配置项矩阵。）

---

## 【公式解读】

**原文无公式**。

（文档未出现任何 LaTeX 或伪代码形式的数学公式，所有数值与配置均以 JSON/代码/文字形式呈现。）

---

## 【关联】

- **上游依赖（环境与安装）**：
  - [msProbe 安装指南](../msprobe_install_guide.md) — 本文显式链接，给出 `pip install mindstudio-probe --pre` 这一安装入口。
  - *CANN Software Installation Guide*（CANN 软件安装指南） — 涉及 CANN 8.5.0 与 OPS 的安装及环境变量配置。
  - *Ascend Extension for PyTorch Installation Guide* 中的"Installing PyTorch > Method 1: Installation via a Binary Package" — 给出 PyTorch 2.9.0 / Python 3.12 / AArch64 / torchvision 0.24.0 的具体安装路径。
- **下游扩展（精度比对）**：
  - [Precision Comparison](#precision-comparison) — 本文内部跳转锚点，承接"数据采集 → 数据比对"的下一步。
  - [Precision Comparison Result Analysis](../accuracy_compare/pytorch_accuracy_compare_instruct.md#precision-comparison-result-analysis) — 本文显式链接，详述 `compare_result_{timestamp}.xlsx` 的结果分析（`Result`、`Err_Message` 的解读方法）。
- **横向关联**：
  - GPU 侧 `import torch_npu` 与 `from torch_npu.contrib import transfer_to_npu`（脚本第 24、25 行）—— 这是 `torch_npu` 提供的 GPU↔NPU 透明迁移接口，与 msProbe 的"采集 + 比对"流程形成上下游：先迁移执行，再统一 dump。
- **模块内引用锚点**：
  - `#environment-setup`、`#precision-data-collection`、`#precision-comparison`、`#pytorch-precision-data-collection-code-sample` —— 文档内部 markdown 锚点，构成自身章节导航。

---

## 【使用方法】

### 1. 安装命令（原文）

```bash
pip install mindstudio-probe --pre
```

### 2. GPU 端脚本注入（原文第 24、25 行）

```python
import torch_npu
from torch_npu.contrib import transfer_to_npu
```

### 3. 采集配置文件 `config.json`（原文逐字）

```json
{
    "task": "statistics",
    "dump_path": "/home/dump",
    "rank": [],
    "step": [0,1],
    "level": "L1",
    "async_dump": false,

    "statistics": {
        "scope": [],
        "list": [],
        "tensor_list": [],
        "data_mode": ["all"],
        "summary_mode": "statistics"
    }
}
```

**配置项含义（原文涉及）**：

| 字段 | 取值 | 作用（原文） |
|---|---|---|
| `task` | `"statistics"` | 任务类型为统计 |
| `dump_path` | `"/home/dump"` | dump 数据落盘目录 |
| `rank` | `[]` | 不指定则包含所有 rank |
| `step` | `[0,1]` | 在第 0、1 步进行 dump |
| `level` | `"L1"` | API/模块层级 |
| `async_dump` | `false` | 同步 dump |
| `statistics.scope` | `[]` | 空表示全部 |
| `statistics.list` | `[]` | 空表示全部 |
| `statistics.tensor_list` | `[]` | 空表示全部 |
| `statistics.data_mode` | `["all"]` | 采集所有数据类型 |
| `statistics.summary_mode` | `"statistics"` | 汇总模式为统计 |

### 4. 训练脚本中调用 msProbe（原文第 27、28 行 + 第 332、334、361、362 行）

```python
from msprobe.pytorch import PrecisionDebugger, seed_all
seed_all(seed=1234, mode=True)
...
debugger = PrecisionDebugger(config_path="./config.json")
...
debugger.start()
...
debugger.stop()
debugger.step()
```

### 5. 启动训练（原文）

```bash
python pytorch_main.py -a resnet50 -b 32 --gpu 1 --dummy
```

### 6. 执行精度比对（原文）

```bash
msprobe compare -tp /home/dump/dump_data_gpu/step0/rank/dump.json -gp /home/dump/dump_data_npu/step0/rank/dump.json -o /home/accuracy_compare
```

**参数说明**：

| 参数 | 含义（原文） |
|---|---|
| `-tp` | NPU 侧（test，待测）dump.json 路径 |
| `-gp` | GPU 侧（benchmark）dump.json 路径 |
| `-o` | 比对结果输出目录（本例为 `/home/accuracy_compare`） |

### 7. 结果分析路径（原文）

- 比对产物：`compare_result_{timestamp}.xlsx`（位于 `-o` 指定目录下）。
- 分析入口：参见 [`pytorch_accuracy_compare_instruct.md#precision-comparison-result-analysis`](../accuracy_compare/pytorch_accuracy_compare_instruct.md#precision-comparison-result-analysis)，通过 `Result` 与 `Err_Message` 两列定位可疑算子。

### 8. 原文未涉及的内容

- **未涉及**：`task` 取其他值（如 `"tensor"`、`"acc`"等）的配置说明、`level` 取 `L0`/`mix` 的区别、`async_dump=true` 的语义影响、`data_mode` 中 `"input"`/`"output"`/`"grad"` 等可选值——均未在本文档出现，需查阅其他文档。
- **未涉及**：`PrecisionDebugger` 的其它方法（如 `config` 字典入参形式、`tensor_list` 的具体 API 名称列表用法等）—— 原文未给出。

## 图文联合解读

- `compare_result_1.png`: 1) 图中是一张对比表格，列出 NPU 与 Bench（基准）两端张量的属性：Name、Dtype、Tensor Shape、Requires_grad，以及 Cosine 相似度指标。

2) 论证 msProbe 可对 API/模块级别的张量进行结构化对照——dtype、shape、requires_grad 完全一致时，通过余弦相似度量化精度差异（如 0.74739、0.845712 等），bool 标量则标记为 unsupported。

3) 该图对应文档第 5 步"Precision comparison"：展示 NPU vs 基准环境的精度数据比对结果，是快速定位精度问题的核心产出。
- `compare_result_2.png`: **1) 图内容**：表格展示 NPU 与标杆环境精度对比的多维度指标（欧氏距离、绝对误差最大值、相对误差最大值、千/万分位误差占比、NPU 最大/最小/均值/l2norm），对比坐标点对 (900,85093) 与 (1992,1908) 的逐项数值，并重复一次形成对照行。

**2) 技术结论**：高维稀疏坐标计算在 NPU 上产生显著精度偏差（EucDist 1992、MaxAbsErr 716、MaxRelativeErr 10.35），存在系统性溢出/精度劣化，非偶发噪声。

**3) 与文档关系**：作为"精度比对（Step 5）"输出示例，证明仅看 loss 无法定位问题，需通过 msProbe 在 API 级采集并量化对比，方可暴露 NPU 计算异常点。
- `compare_result_3.png`: **图文联合解读：**

图示为msProbe精度比对结果表，列出Bench_max/min/mean/l2norm、Requires_grad、Consistent、Result等字段，6行数据均显示"pass"且Err_message为空，Data_name含Tensor张量名与标量对。

**论证结论**：NPU与基准环境的API级输入输出在统计指标（最大/最小/均值/L2范数）上一致，无精度异常。

**与文档关系**：对应文档第5步"精度比对"，通过该表快速验证NPU与Bench环境精度一致，实现故障定位。
- `vis_result.png`: **图示内容**：TensorBoard界面，左侧"调试侧"与右侧"标杆侧"并排呈现同一DefaultModel网络结构（Conv2d→BatchNorm2d→ReLU→MaxPool→Sequential），bn1.BatchNorm2d.forward.0被高亮选中；下方表格列出该节点input与parameter张量的Max、Min、Mean、Norm、Cosine、EucDist、MaxAbsErr等多项统计指标及匹配状态。

**技术结论**：msProbe通过双图并排+节点级张量统计指标，可对NPU与标杆环境同一API的输入输出逐项比对，从而快速定位精度异常模块。

**与文档关系**：直接对应文档第5步"精度比对"——"对比NPU与标杆环境API数据以快速定位精度问题"，是msProbe快速上手流程中可视化比对能力的实证。
