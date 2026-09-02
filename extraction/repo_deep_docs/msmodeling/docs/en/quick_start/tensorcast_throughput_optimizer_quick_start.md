# msModeling Quick Start

> 仓 `msmodeling` · 路径 `docs/en/quick_start/tensorcast_throughput_optimizer_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/en/quick_start/tensorcast_throughput_optimizer_quick_start.md

# msmodeling Quick Start 文档一体化深度解读

---

## 【定位】

这篇文档是 **msmodeling 中 TensorCast 与 Throughput Optimizer 两个核心模块的入门级 Quick Start**，面向首次使用者，按照「环境验证 → 单模型文本生成性能仿真 → 服务级吞吐寻优」三步走，帮助用户在约 10 分钟内跑通命令行工作流，理解两个模块的输入参数、输出指标与典型使用场景。文档定位为"先跑通、再细看"，强调复制粘贴即可执行，并以 `TEST_DEVICE` 作为快速体验的占位硬件。

---

## 【技术要点】

1. **双 CLI 入口**：TensorCast 通过 `python -m cli.inference.text_generate` 运行，Throughput Optimizer 通过 `python -m cli.inference.throughput_optimizer` 运行；运行前必须从仓库根目录执行，否则需 `export PYTHONPATH=/path/to/msmodeling:$PYTHONPATH`。
2. **Hugging Face 模型配置依赖**：TensorCast 从 Hugging Face 读取模型配置，无法直连时需设置 `export HF_ENDPOINT="https://hf-mirror.com"` 镜像。
3. **TensorCast 静态性能仿真**：不真正执行模型在加速器上的运行，而是拦截计算图（computation graph），结合目标硬件 profile 估算算子时延、显存与吞吐；默认输出算子级汇总、总时延、TPS/Device、显存；带 `--chrome-trace-file` 可生成 Chrome Trace 时间线。
4. **关键参数（TensorCast 示例）**：`Qwen/Qwen3-32B`、`--num-queries 2`、`--query-length 3500`、`--device TEST_DEVICE`、`--chrome-trace-file ./tensorcast_trace.json`（可选）。
5. **Throughput Optimizer 服务级寻优**：在 TTFT / TPOT 等 SLO 约束下搜索最优并行策略与 batch 配置；`PD colocated`（Prefill/Decode 同实例）用于快速评估整体吞吐，分开评估需参考 Throughput Optimizer User Guide。
6. **关键参数（Throughput Optimizer 示例）**：`--device TEST_DEVICE`、`--num-devices 8`、`--input-length 3500`、`--output-length 1500`、`--quantize-linear-action W8A8_DYNAMIC`、`--quantize-attention-action disabled`、`--tpot-limit 50`；首跑不指定 `--tp-sizes` 时使用默认 TP 搜索范围，过慢可通过降低 `--num-devices` 或显式指定 `--tp-sizes` 缩小搜索空间。

---

## 【关键机制与数据】

### 工作原理

- **TensorCast**（原文："performs performance modeling for PyTorch programs. It does not execute the model on a real accelerator. Instead, it intercepts the computation graph and estimates operator latency, memory usage, and overall inference performance based on the target device profile."）：基于计算图拦截与硬件 profile 的**离线估算器**，输出算子级延迟汇总、端到端时延、TPS/Device、显存占用（包含 weights、KV cache、activations）。
- **Throughput Optimizer**（原文："searches for the best parallel strategy and batch configuration under SLO constraints such as TTFT and TPOT. It helps estimate the maximum serving throughput of a target model on target hardware."）：在 SLO（TTFT/TPOT）约束下的**寻优器**，先打印输入配置与最佳配置汇总，再列出候选并行配置表。

### 数据流

1. **CLI 输入** → 模型 ID（HF）+ 设备 profile + 输入/输出长度 + 量化策略 + SLO 约束；
2. **TensorCast** 拦截计算图 → 算子级 latency 估算 → 聚合出 `analytic total` / `analytic avg` / `# of Calls` / `Total time for analytic` / `[analytic] TPS/Device` / `Total device memory`；
3. **Throughput Optimizer** 枚举并行/批配置 → 在 SLO 下筛选 → 输出最佳 `Throughput`、`TTFT`、`TPOT`，以及候选 Top N 表（含 `TP/PP/DP`、`concurrency`、`batch_size`）。

### 性能数据（原文示例输出，直接采自原文）

TensorCast 算子级示例：
- 原文：`tensor_cast.static_quant_linear.default  analytic total=884.004ms  analytic avg=1.973ms  # of Calls=448`
- 原文：`tensor_cast.attention.default  analytic total=259.855ms  analytic avg=4.060ms  # of Calls=64`
- 原文：`Total time for analytic: 1.744s`
- 原文：`[analytic] TPS/Device: 4013 token/s`
- 原文：`Total device memory: 64.000 GB`
- 原文：`Model compilation and execution time: 0.192 s`

Throughput Optimizer 服务级示例：
- 原文：`Best Throughput: 2161.56 tokens/s`
- 原文：`TTFT: 13848.08 ms`
- 原文：`TPOT: 49.98 ms`
- 原文（Top 1）：`Throughput=2161.56 token/s, TTFT=13848.08 ms, TPOT=49.98 ms, concurrency=128, num_devices=8, parallel=TP=4 | PP=1 | DP=2, batch_size=64`
- 原文：`TPOT Limits: 50.0 ms`（输入约束，与最佳 `49.98 ms` 紧贴 SLO 上限）。

---

## 【表格解读】

### 表格 1：Experience Map（核心操作约 10 分钟）— 逐字还原

| Step | Stage | Core Module | Reference Operation Time | Suggested Concept Study |
| :---: | :---: | :--- | :---: | :---: |
| **1** | **Environment setup** | `msModeling` | 2 minutes | 5 minutes |
| **2** | **Model inference performance simulation** | `TensorCast` | 1 minute | 10 minutes |
| **3** | **Service-level performance simulation** | `Throughput Optimizer` | 2 minutes | 15 minutes |

**逐行解读：**
- 第 1 行：环境准备阶段，使用 `msModeling` 自身作为入口模块，操作 2 分钟 / 概念学习 5 分钟，是后两步的前置条件。
- 第 2 行：单模型推理性能仿真，由 `TensorCast` 承担，操作 1 分钟 / 概念学习 10 分钟——耗时最短，因为命令模板化。
- 第 3 行：服务级性能仿真，由 `Throughput Optimizer` 承担，操作 2 分钟 / 概念学习 15 分钟——概念学习最长，因为涉及并行策略、SLO、量化等概念最多。

### 表格 2：Top PD Aggregated Configurations（原文示例，仅展示 Top 1）— 逐字还原

| Top | Throughput (token/s) | TTFT (ms) | TPOT (ms) | concurrency | num_devices | parallel           | batch_size |
|  1  | 2161.56              | 13848.08  | 49.98     | 128         | 8           | TP=4 \| PP=1 \| DP=2 | 64         |

**逐行解读：**
- Top 1：在 8 张 TEST_DEVICE、`TPOT ≤ 50 ms` 约束下，最佳系统吞吐为 **2161.56 token/s**；TTFT 13848.08 ms、TPOT 49.98 ms（紧贴 SLO 上限 50 ms），说明寻优器把 TPOT 压到了约束边界以最大化吞吐。
- 并行策略采用 `TP=4 / PP=1 / DP=2`，即 4 路张量并行 + 2 路数据并行，无流水线并行；`concurrency=128`、`batch_size=64` 表明在该并行下，每实例 batch 64、2 个 DP 实例共支持 128 路并发请求。

> 原文中的样例仅显示了 Top 1 一行；表格标题为 "Top **4**"，但原文未给出 Top 2~4 的数据，因此本表只还原 Top 1，不臆造其余候选。

---

## 【公式解读】

**原文无公式。** 文档未给出任何数学公式或伪代码表达式，性能估算结果（`analytic total`、`TPS/Device`、`Best Throughput` 等）均由工具内部基于硬件 profile 计算后直接打印，文档未公开其数学形式。

---

## 【关联】

利用文末内部链接信息，文档与上下游的关系如下：

- **前置依赖**：
  - `[msModeling Install Guide](../install_guide/msmodeling_install_guide.md)` — 文首与 §2.1 各引用一次，强制要求先完成仓库克隆、虚拟环境、依赖安装与 `PYTHONPATH` 配置，否则会出现 `No module named cli` / `No module named tensor_cast` 错误。
- **进阶模块 User Guide**：
  - `[TensorCast User Guide](../user_guide/msmodeling_tensor_cast_user_guide.md)` — §3 "Next Steps" 中给出，作为算子级细节、profile 切换、更多参数的深入阅读入口。
  - `[Throughput Optimizer Guide](../user_guide/msmodeling_throughput_optimizer_user_guide.md)` — §2.3 备注（Prefill/Decode 分开评估）与 §3 Next Steps 双重引用，承接 `--tp-sizes` 等高级寻优维度。
- **可视化层（Web UI）**：
  - §4 描述了 `python -m web_ui.web_ui_start --port 2345` 启动浏览器可视化的工作流；内部链接列表中还包含 `../user_guide/msmodeling_web_ui_user_guide.md`，对应 Web UI 的完整使用手册（本 Quick Start 中未直接以相对路径形式给出该链接，但通过文末链接信息可确认其存在）。
- **同模块上下游关系**：TensorCast 提供单模型延迟/显存估算 → Throughput Optimizer 消费这些估算、在多机多卡并行+ SLO 约束下做寻优 → Web UI 在前端统一封装两者；PD colocated 是 Throughput Optimizer 的最简子模式。

---

## 【使用方法】

> 以下命令均为原文给出的、复制即可执行的用法；如需更多高级参数，请参考 §【关联】中的 User Guide。

### 启用前准备（环境）
```bash
# 1. 切到仓库根目录（或设置 PYTHONPATH）
export PYTHONPATH=/path/to/msmodeling:$PYTHONPATH

# 2. Hugging Face 镜像（按需）
export HF_ENDPOINT="https://hf-mirror.com"

# 3. 验证 CLI 可用
python -m cli.inference.text_generate --help
python -m cli.inference.throughput_optimizer --help
```

### TensorCast：LLM 文本生成性能仿真
```bash
# 基础运行
python -m cli.inference.text_generate Qwen/Qwen3-32B \
    --num-queries 2 \
    --query-length 3500 \
    --device TEST_DEVICE

# 可选：生成 Chrome Trace
python -m cli.inference.text_generate Qwen/Qwen3-32B \
    --num-queries 2 \
    --query-length 3500 \
    --device TEST_DEVICE \
    --chrome-trace-file ./tensorcast_trace.json
```
**配置项说明（原文）：** `--num-queries`（请求条数）、`--query-length`（输入长度）、`--device`（目标设备，先用 `TEST_DEVICE` 后替换）、`--chrome-trace-file`（Chrome Trace 输出路径）。原文示例成功标准：终端打印算子级表 + `Total time for analytic` / `[analytic] TPS/Device` + 显存估算。

### Throughput Optimizer：服务级吞吐寻优
```bash
python -m cli.inference.throughput_optimizer Qwen/Qwen3-32B \
    --device TEST_DEVICE \
    --num-devices 8 \
    --input-length 3500 \
    --output-length 1500 \
    --quantize-linear-action W8A8_DYNAMIC \
    --quantize-attention-action disabled \
    --tpot-limit 50
```
**配置项说明（原文）：** `--device`、`--num-devices`（设备数）、`--input-length` / `--output-length`（输入/输出 token 长度）、`--quantize-linear-action W8A8_DYNAMIC`（线性层量化策略）、`--quantize-attention-action disabled`（注意力层量化关闭）、`--tpot-limit 50`（TPOT SLO 上限 ms）；原文提示首跑不指定 `--tp-sizes` 即用默认 TP 搜索范围，过慢时降低 `--num-devices` 或显式指定 `--tp-sizes` 以缩窄搜索空间。

### Web UI（可选，§4）
```bash
python -m web_ui.web_ui_start --port 2345
# 浏览器打开 http://127.0.0.1:2345
```
> 注：原文 §4 在 "an" 处被截断（疑似 Markdown 渲染截断），浏览器内可配置 model、chip、parallelism、quantization 等任务的描述基于原文已出现的部分，更完整字段以 `../user_guide/msmodeling_web_ui_user_guide.md` 为准。
