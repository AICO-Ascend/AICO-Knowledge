# MiniMax-M2

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/MiniMax-M2.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/MiniMax-M2.md

# 深度解读：vllm-ascend 文档「MiniMax-M2」

> ⚠️ 提示：用户提供的原文在 A3 single-node 配置块末尾被截断（"—" 之后的内容未给出），后续 5.2 多节点部署、第 6–10 章（精度/性能评估、FAQ 等）原文未提供，因此下文中如涉及"原文未涉及"会按原样标注。

---

## 【定位】

**这篇文档解决什么问题/描述什么能力：**
本文是 vllm-ascend 仓库面向 MiniMax-M2 系列大语言模型（M2.5 与 M2.7）的端到端部署与验证指南，介绍在 Ascend NPU（A2/A3）硬件上的模型权重准备、Docker/源码安装、单/多节点在线服务部署流程，并引用相关功能矩阵、特性配置、安装、FAQ、评估等子文档以形成完整的使用闭环。

---

## 【技术要点】

1. **模型矩阵与强化场景（原文第 1 节）**：MiniMax-M2 是 MiniMax 旗舰 LLM 系列，包含 `MiniMax-M2.5` 与 `MiniMax-M2.7` 两个子版本，针对代码生成、Agentic tool calling/search、复杂办公工作流等高价值场景进行强化，强调推理效率与端到端速度。
2. **支持的特性（原文第 2 节）**：文档明确建议使用最新 vLLM-Ascend 版本以获得 PD 分离、EAGLE3 投机解码等新特性支持。
3. **模型权重与量化变体（原文第 3.1 节表格）**：M2.7 与 M2.5 均提供 W8A8 量化版本（`w8a8-QuaRot`），M2.7 额外提供 W8A8C8 量化版本；EAGLE3 投机解码头模型为 M2.7/M2.5 各一个独立权重，节点数与基模型一致。
4. **硬件建议（原文表格）**：推荐使用 `1× Atlas 800 A3 (64GB × 16)` 或 `1× Atlas 800I A2 (64GB × 8)`，对应 A3 系列 8 卡双 die 设计（实际为 16 个 `/dev/davinci[0-15]`）和 A2 系列 8 卡设计。
5. **Docker 安装 A3/A2 差异（原文第 4.1 节）**：
   - A3 镜像 tag：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`
   - A2 镜像 tag：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`
   - A3 需要暴露 `/dev/davinci[0-15]` 共 16 个设备；A2 只需 `/dev/davinci[0-7]` 8 个设备。
6. **A3 单节点 vLLM 启动核心配置（原文第 5.1 节）**：
   - 量化方式：`--quantization ascend`
   - TP/DP：`--tensor-parallel-size 4`，`--data-parallel-size 4`
   - 显存与批：`--max-num-seqs 48`，`--max-model-len 40690`，`--max-num-batched-tokens 16384`，`--gpu-memory-utilization 0.85`
   - 投机解码：`--speculative_config` 使用 `eagle3` 方法，`num_speculative_tokens=3`，并设置 `enforce_eager=true`
   - 短上下文低延迟变体：`--max-model-len 32768`，TP=4，DP=4

---

## 【关键机制与数据】

**1. 系统级性能调优（原文第 5.1 节 A3 单节点）**：
- 原文：CPU 调度器切换为 performance 模式：
  ```bash
  echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
  sysctl -w vm.swappiness=0
  sysctl -w kernel.numa_balancing=0
  sysctl kernel.sched_migration_cost_ns=50000
  ```
- 原文：HCCL 通信相关：
  - `HCCL_BUFFSIZE=1024`
  - `HCCL_OP_EXPANSION_MODE="AIV"`
- 原文：内存分配与 jemalloc：
  - `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD`
  - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`

**2. vLLM `additional-config` 高级配置（原文第 5.1 节）**：
- 原文：
  ```json
  {"scheduler_config":{"enable_balance_scheduling":false},
   "enable_cpu_binding":true,
   "enable_fused_mc2":1,
   "weight_nz_mode":1}
  ```
- 原文：`--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'` —— 限制 cudagraph 仅在 decode 阶段使用（短上下文推理场景的优化选择）。
- 原文：`--enable-expert-parallel` —— 启用专家并行（MoE 模型的常见优化）。

**3. 推荐上下文长度（原文第 5.1 节）**：
- 原文：典型场景为短上下文 3.5k 输入 / 1.5k 输出。
- 原文：`--max-model-len 40690`（默认配置）/ `32768`（短上下文低延迟变体）。

**4. 数据流/工作原理（基于原文）**：
- 权重路径：ModelScope 下载 → 推荐放至共享目录 `/root/.cache/`（原文）。
- 启动流程：环境调优 → HCCL 变量导出 → vllm serve 加载量化权重 → 启用 EAGLE3 投机解码 → 对外暴露 `:8000` 服务。
- 文档未提供具体的吞吐量（tokens/s）、时延（TTFT/TPOT）等性能数据数字（**原文未涉及**）。

**5. 多节点通信验证（原文第 3.2 节）**：
- 原文：多节点部署时需先按 [Verify Multi-node Communication Environment](../../getting_started/installation.md#installation-multi-node-interconnect) 进行通信验证；该步骤是 **optional**。

---

## 【表格解读】

### 原文表格 3.1：Model Weight

| Model | Description | Recommended Hardware | Source |
|-------|-------------|---------------------|--------|
| `MiniMax-M2.7-w8a8-QuaRot` | M2.7 W8A8 quantized version | 1× Atlas 800 A3 (64GB × 16) or 1× Atlas 800I A2 (64GB × 8) | [MiniMax-M2.7-w8a8-QuaRot](https://www.modelscope.ai/models/vllm-ascend/MiniMax-M2.7-w8a8-QuaRot) |
| `MiniMax-M2.5-w8a8-QuaRot` | M2.5 W8A8 quantized version | 1× Atlas 800 A3 (64GB × 16) or 1× Atlas 800I A2 (64GB × 8) | [MiniMax-M2.5-w8a8-QuaRot](https://www.modelscope.cn/models/Eco-Tech/MiniMax-M2.5-w8a8-QuaRot) |
| `MiniMax-M2.7-w8a8c8-QuaRot` | M2.7 W8A8C8 quantized version | 1× Atlas 800 A3 (64GB × 16) or 1× Atlas 800I A2 (64GB × 8) | [MiniMax-M2.7-w8a8c8-QuaRot](https://www.modelscope.ai/models/vllm-ascend/MiniMax-M2.7-w8a8c8-QuaRot) |
| `EAGLE3` (M2.7) | M2.7 speculative decoding head model | Matches the base model node count | [MiniMax-M2.7-eagle-model](https://www.modelscope.cn/models/Eco-Tech/MiniMax-M2.7-eagle-model-short) |
| `EAGLE3` (M2.5) | M2.5 speculative decoding head model | Matches the base model node count | [MiniMax-M2.5-eagle-model](https://www.modelscope.cn/models/vllm-ascend/MiniMax-M2.5-eagle-model-0318) |

**逐行解读**：
1. `MiniMax-M2.7-w8a8-QuaRot`：M2.7 的 W8A8（权重 8bit、激活 8bit）量化版，使用 QuaRot 旋转量化算法。推荐硬件为单节点 Atlas 800 A3（16 卡 64GB）或 Atlas 800I A2（8 卡 64GB）。
2. `MiniMax-M2.5-w8a8-QuaRot`：M2.5 的 W8A8 量化版，硬件建议同上，权重托管在 ModelScope 的 Eco-Tech 组织。
3. `MiniMax-M2.7-w8a8c8-QuaRot`：M2.7 额外变体，命名中 `c8` 表示 KV Cache 也量化为 8bit，进一步降低显存占用；硬件建议同前。
4. `EAGLE3` (M2.7)：M2.7 对应的 EAGLE3 投机解码头模型（draft model），节点数需与基模型一致。
5. `EAGLE3` (M2.5)：M2.5 对应的 EAGLE3 头模型，节点数需与基模型一致。

> 注：上述表格中的所有硬件配置、链接、命名均按原文逐字保留。

---

## 【公式解读】

**原文无公式**。

文档中出现的所有 `key=value` 环境变量（如 `HCCL_BUFFSIZE=1024`）、JSON 字符串（如 `--additional-config`）、cudagraph_mode 取值（`FULL_DECODE_ONLY`）、`num_speculative_tokens=3` 等均为**配置参数或命令行参数**，不属于数学公式范畴，按原文未涉及处理。

---

## 【关联】

根据原文中提供的内部链接与上下文，文档与以下模块/特性存在关联：

1. **模型支持矩阵 → [../../user_guide/support_matrix/supported_models.md](../../user_guide/support_matrix/supported_models.md)**
   - 用于查询 MiniMax-M2.5/M2.7 在 vllm-ascend 上的完整特性支持矩阵（如 PD 分离、EAGLE3、专家并行等是否官方认证）。

2. **特性配置指南 → [../../user_guide/feature_guide/index.md](../../user_guide/feature_guide/index.md)**
   - 用于获取 PD 分离、EAGLE3 投机解码等特性的具体配置方法；本指南第 1 节明确推荐使用最新版本以启用这些特性。

3. **多节点通信验证 → [../../getting_started/installation.md#installation-multi-node-interconnect](../../getting_started/installation.md#installation-multi-node-interconnect)**
   - 第 3.2 节明确多节点部署的前置依赖：先验证 HCCL/网卡互通性。

4. **Docker 镜像标签 → [../../getting_started/installation.md#installation-prebuilt-image](../../getting_started/installation.md#installation-prebuilt-image)**
   - 第 4.1 节使用 `{{ vllm_ascend_version }}` 模板变量指向官方 all-in-one 镜像的版本元数据。

5. **源码安装 → [../../getting_started/installation.md](../../getting_started/installation.md)**
   - 第 4.2 节提供源码安装路径，与第 4.1 节的 Docker 安装互为补充。

6. **公共 FAQ → [../../faqs.md](../../faqs.md)（出现两次引用）**
   - 第 5.1 节指出 OOM、HCCL 端口冲突、启动问题等常见问题排查入口。

7. **MiniMax 特定 FAQ → [Chapter 10 FAQ](#10-faq)（本文件内部锚点）**
   - 原文中提及但本篇文档截断未提供该章节内容。

8. **AIS-Bench 性能评估 → [../../developer_guide/evaluation/using_ais_bench.md](../../developer_guide/evaluation/using_ais_bench.md) 与 [using_ais_bench.md#execute-performance-evaluation](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation)**
   - 文末链接之一，预期用于第 6/7 章性能评估（原文截断未呈现具体评估命令）。

9. **LM-Eval 精度评估 → [../../developer_guide/evaluation/using_lm_eval.md](../../developer_guide/evaluation/using_lm_eval.md)**
   - 文末链接之一，预期用于第 6 章精度评估（原文截断未呈现具体评估命令）。

> 上游关系：本文以 vllm-ascend 镜像、`vllm serve` 命令、Ascend NPU 驱动为基础。  
> 下游关系：本文为后续 FAQ、评估（accuracy/perf）章节提供权重路径、启动参数基线。

---

## 【使用方法】

### 1. 模型权重获取（原文第 3.1 节）
- 来源：ModelScope（搜索模型名）。  
- 推荐存储路径：共享目录 `/root/.cache/`。

### 2. 安装方式选择（原文第 4 节）

**方式 A：Docker 一体化镜像（推荐）**

A3 系列：
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
docker run --name vllm-ascend-env --ipc host --net host \
  --device /dev/davinci0 ... --device /dev/davinci15 \
  --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /usr/local/sbin:/usr/local/sbin \
  -it -d $IMAGE bash
```

A2 系列：
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
docker run --name vllm-ascend-env --ipc host --net host \
  --device /dev/davinci0 ... --device /dev/davinci7 \
  --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /usr/local/sbin:/usr/local/sbin \
  -it -d $IMAGE bash
```

**安装验证**：
```bash
docker ps | grep vllm-ascend-env
pip show vllm-ascend
```

**方式 B：源码安装（原文第 4.2 节）**
```bash
# 依据安装指南
python -c "import vllm_ascend; print(vllm_ascend.__version__)"
```

### 3. 启动在线服务（原文第 5.1 节 A3 单节点）

环境准备：
```bash
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
sysctl -w vm.swappiness=0
sysctl -w kernel.numa_balancing=0
sysctl kernel.sched_migration_cost_ns=50000
export HCCL_BUFFSIZE=1024
export HCCL_OP_EXPANSION_MODE="AIV"
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
```

启动 vllm serve：
```bash
vllm serve /path/to/weight/MiniMax-M2.7-w8a8-QuaRot \
    --served-model-name "MiniMax-M2.7" \
    --host 0.0.0.0 \
    --port 8000 \
    --trust-remote-code \
    --quantization ascend \
    --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
    --additional-config '{"scheduler_config":{"enable_balance_scheduling":false},
                          "enable_cpu_binding":true,
                          "enable_fused_mc2":1,
                          "weight_nz_mode":1}' \
    --enable-expert-parallel \
    --tensor-parallel-size 4 \
    --data-parallel-size 4 \
    --max-num-seqs 48 \
    --max-model-len 40690 \
    --max-num-batched-tokens 16384 \
    --gpu-memory-utilization 0.85 \
    --speculative_config '{"enforce_eager": true, "method": "eagle3", "model": "/path/to/weight/Eagle3/", "num_speculative_tokens": 3}'
```

### 4. 短上下文低延迟变体（原文注释）
- 设置 `--max-model-len 32768`、`--tensor-parallel-size 4`、`--data-parallel-size 4`。

### 5. 注意事项（原文）
- 实际使用时应根据输入/输出长度、并发量、硬件配置调整 `--max-model-len`、`--max-num-seqs`、`--max-num-batched-tokens`、`--gpu-memory-utilization`。
- 共享机器上 A3 仅映射所需 NPU（如 `/dev/davinci[0-7]` 对应 NPU 0–3）。
- 模型权重路径需替换为 `/path/to/weight/` 实际值。
- 多节点部署前置：第 3.2 节通信验证。

### 6. 后续章节（原文未涉及）
- 5.2 多节点在线部署命令、第 6 章精度评估（`using_lm_eval`）、第 7 章性能评估（`using_ais_bench`）、第 8–10 章（含 MiniMax 特定 FAQ）的内容，原文截断后未提供。
