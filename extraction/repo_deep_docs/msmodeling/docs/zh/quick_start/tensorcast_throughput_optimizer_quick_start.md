# msModeling快速入门

> 仓 `msmodeling` · 路径 `docs/zh/quick_start/tensorcast_throughput_optimizer_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/zh/quick_start/tensorcast_throughput_optimizer_quick_start.md

# 文档深度解读：msModeling 快速入门（TensorCast + Throughput Optimizer）

---

## 【定位】

本文档是 msModeling 工具的**面向首次使用用户的"一体化"快速入门指南**，目标是让用户在约 10 分钟内，从环境准备开始，依次跑通 **TensorCast（模型推理性能仿真）** 与 **Throughput Optimizer（服务化性能仿真）** 两条核心链路，理解工具的输入、输出、关键指标与适用场景，最终形成对 msModeling 能力全貌的初步认识。

---

## 【技术要点】

1. **运行环境约束**：所有命令默认在 msModeling 仓库根目录执行；非根目录执行需先 `export PYTHONPATH=/path/to/msmodeling:$PYTHONPATH`，否则会报 `No module named cli` / `No module named tensor_cast`。访问 Hugging Face 受限时需设镜像：`export HF_ENDPOINT="https://hf-mirror.com"`。

2. **TensorCast 仿真执行（LLM 文本生成）**：
   ```bash
   python -m cli.inference.text_generate Qwen/Qwen3-32B \
       --num-queries 2 --query-length 3500 --device TEST_DEVICE
   ```
   关键参数：`--num-queries=2`、`--query-length=3500`、`--device TEST_DEVICE`（先用 `TEST_DEVICE` 跑通流程再替换为目标硬件）。

3. **TensorCast 输出物**：算子级性能汇总表（`analytic total` / `analytic avg` / `# of Calls`）、`Total time for analytic`、`[analytic] TPS/Device`、`Total device memory`；可选 `--chrome-trace-file ./tensorcast_trace.json` 生成 Chrome Trace 文件，可用 `chrome://tracing` 或 MindStudio Insight 打开。

4. **Throughput Optimizer 仿真执行（服务化性能）**：
   ```bash
   python -m cli.inference.throughput_optimizer Qwen/Qwen3-32B \
       --device TEST_DEVICE --num-devices 8 \
       --input-length 3500 --output-length 1500 \
       --quantize-linear-action W8A8_DYNAMIC \
       --quantize-attention-action disabled \
       --tpot-limit 50
   ```
   关键参数：`--num-devices 8`、`--quantize-linear-action W8A8_DYNAMIC`、`--quantize-attention-action disabled`、`--tpot-limit 50`（TPOT 上限 ms）；默认使用 TP 搜索范围，耗时过长时可减少 `--num-devices` 或显式指定 `--tp-sizes`。

5. **PD 混部概念**：Throughput Optimizer 入门命令跑的是 Prefill + Decode 同实例混部场景，用于快速评估整体服务吞吐；如需分别评估 Prefill 与 Decode，需进入进阶使用指南。

6. **Throughput Optimizer 输出物**：`Input Configuration`、`Overall Best Configuration`（含 `Best Throughput` / `TTFT` / `TPOT`），以及 `Top N PD Aggregated Configurations` 候选表，含 `TP/PP/DP`、`batch_size`、`concurrency`、`Throughput`、`TTFT`、`TPOT`。

7. **Web UI 可选入口**：`python -m web_ui.web_ui_start --port 2345`，浏览器访问 `http://127.0.0.1:2345`，可视化配置模型/芯片/并行/量化/workload 参数。

---

## 【关键机制与数据】

### TensorCast 工作机制
- **原理（原文）**：*"TensorCast（模型推理性能仿真）面向 PyTorch 程序进行性能建模。它不会在真实加速器上执行模型，而是拦截计算图，并基于目标设备画像估算算子耗时、显存占用和整体推理性能。"*——即 **不真实执行**，而是基于「目标设备画像」做算子级估算。
- **默认输出（原文）**：*"算子级性能汇总、总执行时间、TPS/Device 与显存占用。"*
- **示例终端输出（原文摘录）**：
  - `Model compilation and execution time: 0.192 s`
  - `tensor_cast.static_quant_linear.default`：analytic total `884.004ms`、avg `1.973ms`、calls `448`
  - `tensor_cast.attention.default`：analytic total `259.855ms`、avg `4.060ms`、calls `64`
  - `Total time for analytic: 1.744s`
  - `[analytic] TPS/Device: 4013 token/s`
  - `Total device memory: 64.000 GB`
- **指标语义（原文）**：`analytic total`=算子估算总耗时；`analytic avg`=单次调用平均耗时；`# of Calls`=算子被调用次数；`TPS/Device`=每设备每秒 token 数；`Total device memory`=权重/KV cache/activation 等显存估算。

### Throughput Optimizer 工作机制
- **原理（原文）**：*"Throughput Optimizer（服务化性能仿真）可在 TTFT、TPOT 等 SLO 约束下，自动搜索最优并行策略和 batch 配置，帮助评估给定模型在目标硬件上的最大服务吞吐。"*
- **示例终端输出（原文摘录）**：
  - `Model: Qwen/Qwen3-32B`
  - `Devices: 8 TEST_DEVICE`
  - `TPOT Limits: 50.0 ms`
  - `Best Throughput: 2161.56 tokens/s`
  - `TTFT: 13848.08 ms`
  - `TPOT: 49.98 ms`
  - Top1 候选：`Throughput 2161.56`、`TTFT 13848.08`、`TPOT 49.98`、`concurrency 128`、`num_devices 8`、`parallel TP=4 | PP=1 | DP=2`、`batch_size 64`
- **字段语义（原文）**：`TP/DP`=并行策略；`concurrency`=该候选配置支持的并发请求数；`batch size`=满足 SLO 的批大小；`TTFT`=首 token 时间；`TPOT`=每输出 token 时间；`Throughput (token/s)`=系统级输出 token 吞吐（越大越好）。

---

## 【表格解读】

### 表 1：体验地图（步骤 / 环节 / 核心模块 / 耗时）

逐字还原：

| 步骤 | 环节 | 核心模块 | 参考操作耗时 | 建议原理学习 |
| :---: | :---: | :--- | :---: | :---: |
| **1** | **环境准备** | `msModeling` | 2 分钟 | 5 分钟 |
| **2** | **模型推理性能仿真** | `TensorCast` | 1 分钟 | 10 分钟 |
| **3** | **服务化性能仿真** | `Throughput Optimizer` | 2 分钟 | 15 分钟 |

**逐行解读**：
- **第 1 行（步骤 1）**：环境准备，模块为 `msModeling`，操作约 2 分钟，原理学习约 5 分钟——这是后两步的前置基础。
- **第 2 行（步骤 2）**：模型推理性能仿真，对应 `TensorCast` 模块，操作约 1 分钟，原理学习约 10 分钟——重在理解"拦截计算图 + 设备画像估算"机制。
- **第 3 行（步骤 3）**：服务化性能仿真，对应 `Throughput Optimizer` 模块，操作约 2 分钟，原理学习约 15 分钟——SLO 约束 + 并行/batch 搜索，复杂度最高。
- **整体含义**：文档明确给出"操作 < 原理学习"的预期时间分布，提示用户不要跳过原理学习。

### 表 2：Top PD Aggregated Configurations（示例输出节选）

原文示例（仅给出 Top 1 一行，并提到"Top 4"标签，原文未列出 2/3/4 行）：

| Top | Throughput (token/s) | TTFT (ms) | TPOT (ms) | concurrency | num_devices | parallel | batch_size |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 2161.56 | 13848.08 | 49.98 | 128 | 8 | TP=4 \| PP=1 \| DP=2 | 64 |

**逐行解读**：
- **Top 1 行**：吞吐 `2161.56 tokens/s`、TTFT `13848.08 ms`、TPOT `49.98 ms`、并发 `128`、设备数 `8`、并行策略 `TP=4 | PP=1 | DP=2`、批大小 `64`。在 TPOT 上限 50 ms 约束下，TPOT 实测 49.98 ms 恰好满足 SLO，TTFT 偏高（13.8 s），吞吐 2161.56 tokens/s 为本搜索范围内的最优解。

---

## 【公式解读】

**原文无公式。** 文档中所有定量信息均以命令行参数、示例终端表格和数字的形式呈现，未出现任何 LaTeX 公式或伪代码形式的推导表达式。

---

## 【关联】

本文档在 msmodeling 文档体系中处于**入门导览**位置，明确将读者引向以下上下游文档，构成完整的"安装 → 快速体验 → 深入使用 → 可视化"链路：

1. **前置依赖**：[《msModeling 安装指南》](../install_guide/msmodeling_install_guide.md)
   - 在 §1.2 与 §2.1 两次强提示用户**必须先完成**该文档的环境安装/虚拟环境/依赖/`PYTHONPATH` 配置；这是跑通本文所有命令的硬性前提。

2. **TensorCast 深入使用**：[《模型推理性能仿真使用指南》](../user_guide/msmodeling_tensor_cast_user_guide.md)
   - §3「结果校验与下一步」明确指向：若需进一步用法（如更多参数、更多设备画像、PD 分离评估等），进入此文档。

3. **Throughput Optimizer 深入使用**：[《服务化性能仿真使用指南》](../user_guide/msmodeling_throughput_optimizer_user_guide.md)
   - §2.3「PD 混部」注释中明确指出：*"若需要分别评估 Prefill 与 Decode，可继续阅读《服务化性能仿真使用指南》"*；§3 再次指向该文档。
   - 即本文档默认仅演示 **PD 混部** 场景；Prefill/Decode 分离评估属于该进阶文档的范畴。

4. **可视化入口**：[《Web UI 使用指南》](../user_guide/msmodeling_web_ui_user_guide.md)
   - §4 给出 Web UI 启动命令与入口 URL，并明确指出"更多页面说明、参数配置与结果解读"在该指南中。

**模块间数据流向**：`TensorCast` 提供"单次推理"层面的算子耗时与显存估算，作为下层基础；`Throughput Optimizer` 在此之上叠加 **SLO（TTFT/TPOT）约束 + 并行（TP/PP/DP）+ batch + 量化** 搜索，输出系统级吞吐——两者共同构成"推理性能 → 服务性能"的能力阶梯，Web UI 则为两者提供统一的可视化前端。

---

## 【使用方法】

### 1. 环境前置命令（原文有）
```bash
export PYTHONPATH=/path/to/msmodeling:$PYTHONPATH
export HF_ENDPOINT="https://hf-mirror.com"      # 网络受限时
python -m cli.inference.text_generate --help    # 验证 CLI 入口
python -m cli.inference.throughput_optimizer --help
```

### 2. TensorCast 推理性能仿真（原文有）
```bash
# 基础执行
python -m cli.inference.text_generate Qwen/Qwen3-32B \
    --num-queries 2 --query-length 3500 --device TEST_DEVICE

# 生成 Chrome Trace（可选）
python -m cli.inference.text_generate Qwen/Qwen3-32B \
    --num-queries 2 --query-length 3500 --device TEST_DEVICE \
    --chrome-trace-file ./tensorcast_trace.json
```
**关键配置项**：`--num-queries`、`--query-length`、`--device`、`--chrome-trace-file`。
**成功标准（原文）**：终端输出算子级性能表；输出 `Total time for analytic` 或 `[analytic] TPS/Device`；输出 `Total device memory`。

### 3. Throughput Optimizer 服务化仿真（原文有）
```bash
python -m cli.inference.throughput_optimizer Qwen/Qwen3-32B \
    --device TEST_DEVICE --num-devices 8 \
    --input-length 3500 --output-length 1500 \
    --quantize-linear-action W8A8_DYNAMIC \
    --quantize-attention-action disabled \
    --tpot-limit 50
```
**关键配置项**：`--device`、`--num-devices`、`--input-length`、`--output-length`、`--quantize-linear-action`（如 `W8A8_DYNAMIC`）、`--quantize-attention-action`（如 `disabled`）、`--tpot-limit`（TPOT 上限 ms）、`--tp-sizes`（进阶，显式指定缩小搜索范围）。
**成功标准（原文）**：终端输出 `Overall Best Configuration` 或候选配置表；输出 `Throughput` / `TTFT` / `TPOT`；无模型配置加载失败或参数冲突报错。

### 4. Web UI 启动（原文有）
```bash
python -m web_ui.web_ui_start --port 2345
# 浏览器访问 http://127.0.0.1:2345
```
**关键配置项**：`--port`（端口号）。

### 5. 故障排查指引（原文有）
- 无法下载模型配置 → 访问 Hugging Face 或设 `HF_ENDPOINT` 镜像。
- 找不到 `cli` / `tensor_cast` 模块 → 确认在仓库根目录，或检查 `PYTHONPATH`。
- 服务化仿真耗时过长 → 减小 `--num-devices`，或显式指定 `--tp-sizes`。

> 原文未涉及：HTTP/gRPC 服务部署、Kubernetes 集成、Prometheus 指标导出等运维相关配置项（这些可能属于 Throughput Optimizer 进阶指南范畴，本文未展开）。
