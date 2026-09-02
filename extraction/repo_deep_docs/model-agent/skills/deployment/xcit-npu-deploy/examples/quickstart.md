# XCiT NPU Deployment Quick Start

> 仓 `model-agent` · 路径 `skills/deployment/xcit-npu-deploy/examples/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/deployment/xcit-npu-deploy/examples/quickstart.md

# XCiT NPU Deployment Quick Start — 一体化深度解读

## 【定位】

本篇文档是 **XCiT 模型在昇腾 NPU 上部署的快速入门指南**，围绕三个核心动作（单模型推理、精度对比、批量跑全模型）以及 NPU 环境校验，向用户提供可直接复制的命令行模板，使其能在最短路径上完成 XCiT 在 NPU 上的推理验证与多模型横向比对。

---

## 【技术要点】

1. **多设备推理入口**：通过 `scripts/run_inference.py` 配合 `--device` 参数，既支持 NPU（`npu:0`）也支持 CPU 推理，且可指向同一模型进行跨平台对照。
2. **可调推理超参**：支持 `--batch-size`、`--warmup`、`--iters` 三个参数对单次推理的批量大小、预热轮次、迭代次数进行精细控制，原文示例给出 `batch-size=4, warmup=5, iters=50` 的组合。
3. **CPU vs NPU 精度对比脚本**：通过 `scripts/run_compare.py --model <model_name>` 实现同一模型在 CPU 与 NPU 上的输出对比，用于核验 NPU 落地的数值一致性。
4. **批量全模型运行器**：`bash scripts/run_all.sh` 默认串行执行全部 **5 个 XCiT 模型**，涵盖精度对比与 NPU 基准测试；支持 `--skip-benchmark` 跳过基准测试以加速，并支持 `--model` 参数指定只跑某一个模型。
5. **NPU 环境就绪检查**：通过 `torch.npu.is_available()` / `torch.npu.device_count()` / `torch.npu.get_device_name(0)` 三连检查，确认 Torch NPU 扩展可用、可见设备数量以及设备名称。
6. **模型命名约定**：文档给出两个具名示例 —— `xcit_tiny_12_p16_384`（tiny，12 层，patch16，输入 384）与 `xcit_large_24_p8_224`（large，24 层，patch8，输入 224），暗示该仓库覆盖的 XCiT 系列至少包含这两个变体，加上 "5 个模型" 的总数说明还有其它变体（如 small、medium、xlarge 等），但原文未列出全部名称。

---

## 【关键机制与数据】

- **工作原理（按文档呈现的视角）**：文档本身是"操作模板"，并不描述底层算子映射或图编译细节。其隐含的数据流为 —— 调用 `run_inference.py` 加载指定 XCiT 模型到目标设备（CPU/NPU），按设定批量与迭代执行前向推理；`run_compare.py` 在两种设备上各跑一遍再对比输出；`run_all.sh` 则将多模型串行调度，统一完成"精度对比 + NPU benchmark"两阶段任务。
- **性能数据 / 数值基线**：原文仅以"示例参数"形式给出 `batch-size=4, warmup=5, iters=50`，并未给出吞吐量、延迟、加速比等可量化性能数字，因此**不引入任何原文没有的数字**。
- **NPU 环境检测三元组**：原文给出的判定维度是"可用性 + 数量 + 名称"，对应调用的是 PyTorch 的 `torch.npu` 命名空间扩展（昇腾适配层）。
- **原文提到的脚本与标志位**：`scripts/run_inference.py`、`scripts/run_compare.py`、`bash scripts/run_all.sh`，关键 flag 包括 `--model`、`--device npu:0|cpu`、`--batch-size`、`--warmup`、`--iters`、`--skip-benchmark`。
- **模型总数**：原文明确 "Run all 5 XCiT models"，即此 XCiT NPU 部署包覆盖 **5** 个预集成变体。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档以"无内部链接"形式提供关联信息（原文标注"内部链接: (无)"）。可从文档自身语义推断的关联如下：

- **上游脚本依赖**：所有命令均以 `scripts/run_inference.py`、`scripts/run_compare.py`、`scripts/run_all.sh` 为入口，这三个脚本是本 quickstart 的执行主体；其内部实现（如何加载 XCiT checkpoint、如何做精度对齐、如何调用 NPU benchmark）原文未展开，归属本目录的其它文档。
- **模型选择维度**：文档示例所列 `xcit_tiny_12_p16_384`、`xcit_large_24_p8_224` 与 "5 个 XCiT 模型" 的总数暗示该部署包提供了一份 XCiT 家族的预置模型清单（命名约定包含 depth / patch-size / image-size 三段信息），清单的完整索引在原文中未列出。
- **环境校验 → 推理 → 对比 → 批量** 构成一条递进的"单点 → 全量"工作流：`torch.npu.is_available()` 等价于预检查；`run_inference.py` 是单点执行；`run_compare.py` 是单点精度对照；`run_all.sh` 是全模型自动化批跑。

> 因原文未提供任何内部超链接，无法定位到其它章节或兄弟文档做进一步交叉引用。

---

## 【使用方法】

文档原文直接给出了完整命令行模板，按使用场景可归纳如下：

**单模型推理**
```bash
# NPU 推理
python3 scripts/run_inference.py --model xcit_tiny_12_p16_384 --device npu:0

# CPU 推理
python3 scripts/run_inference.py --model xcit_tiny_12_p16_384 --device cpu

# 自定义 batch size / warmup / iters
python3 scripts/run_inference.py --model xcit_large_24_p8_224 --device npu:0 --batch-size 4 --warmup 5 --iters 50
```

**单模型 CPU vs NPU 精度对比**
```bash
python3 scripts/run_compare.py --model xcit_tiny_12_p16_384
```

**批量跑全模型（默认含精度对比 + NPU benchmark）**
```bash
# 全部 5 个 XCiT 模型
bash scripts/run_all.sh

# 跳过 benchmark 以加速
bash scripts/run_all.sh --skip-benchmark

# 仅跑某一个模型
bash scripts/run_all.sh --model xcit_tiny_12_p16_384
```

**NPU 环境校验**
```bash
python3 -c "
import torch
print('NPU available:', torch.npu.is_available())
print('NPU count:', torch.npu.device_count())
print('NPU name:', torch.npu.get_device_name(0))
"
```

**配置项汇总（原文显式提及）**：`--model`、`--device`、`--batch-size`、`--warmup`、`--iters`、`--skip-benchmark`；其中 `--device` 取值为 `npu:0` 或 `cpu`。文档未涉及 YAML/JSON 配置文件、环境变量或 Docker 启动方式。
