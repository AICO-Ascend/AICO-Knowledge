# Qwen3-Dense (Qwen3-0.6B/1.7B/4B/8B/14B/32B)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-Dense.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Dense.md

# Qwen3-Dense 部署指南深度解读

## 【定位】

本文档是 vLLM-Ascend 环境下 Qwen3 Dense 系列模型（Qwen3-0.6B/1.7B/4B/8B/14B/32B 及其量化版本 W8A8、W4A4、W8A8SC-310）在 Atlas 系列 NPU 上进行**部署、量化与验证**的端到端操作指南，配套版本为 vLLM-Ascend v0.21.0。

## 【技术要点】

1. **支持的模型规模与量化方式**：涵盖 Qwen3 6 种 BF16 稠密规模（0.6B–32B），并提供针对 Atlas A2/A3 的 W4A4/W8A8 量化版本（仅 32B），以及针对 Atlas 300I DUO 的 W8A8SC 量化版本（8B/14B/32B）。
2. **版本支持时间线**：Qwen3 Dense 首次支持于 v0.8.4rc2；W8A8 量化首次支持于 v0.8.4rc2；W4A4 量化自 v0.11.0rc1 起支持。
3. **硬件需求**：所有 BF16 版本均需 1 台 Atlas A3（64GB × 16，共 16 卡）或 1 台 Atlas A2（64GB × 8，共 8 卡）；Atlas 300I DUO 仅支持 W8A8SC 量化（8B/14B 用 TP1，32B 用 TP4）。
4. **Docker 镜像策略**：区分 `-a3`、`默认`（A2）、`-310p`（Atlas 300I DUO）三种镜像标签，启动时按硬件映射 `/dev/davinci*` 设备节点。
5. **Atlas A3 双 die 特性**：Atlas A3 推理产品具有 8 个 NPU 双 die 设计（共计 16 个芯片 `/dev/davinci[0-15]`），共享机器需按需映射芯片。
6. **多节点前置**：多节点部署前必须验证多节点通信环境（链接到 installation.md 的相应章节）。

## 【关键机制与数据】

本文档定位为操作型 guide，并未描述算法层面的工作机制。**原文**涉及的关键性能/支持数据如下：

- **原文**：首次支持版本 v0.8.4rc2；W8A8 首次支持 v0.8.4rc2；W4A4 首次支持 v0.11.0rc1。
- **原文**：本文档基于 **vLLM-Ascend v0.21.0** 验证；所有 v0.21.0 及之后版本均可稳定运行。
- **原文**：Atlas A3 推理产品硬件形态 = 8 NPUs × dual-die = 16 chips（`/dev/davinci[0-15]`）；Atlas A2 = 8 chips（`/dev/davinci[0-7]`）；Atlas 300I DUO 同样映射 8 个设备节点。
- **原文**：默认工作目录 `/workspace`；vLLM 与 vLLM-Ascend 以 Python site-packages 方式安装。
- **原文**：Atlas 300I DUO 容器 `--shm-size=10g` 与端口 `-p 8080:8080`，与其他硬件 `1g` shm 形成差异。
- **原文**：硬件卡数可根据实际调整（"These are the recommended numbers of cards, which can be adjusted according to the actual situation"）。

## 【表格解读】

**表 1：BF16 版本（Atlas A2/A3 通用）**

| Model | Hardware Requirement | Download |
|-------|---------------------|----------|
| Qwen3-0.6B | 1 Atlas A3 inference products (64GB × 16), 1 Atlas A2 inference products (64GB × 8) | [Download](https://modelers.cn/models/Modelers_Park/Qwen3-0.6B) |
| Qwen3-1.7B | 1 Atlas A3 inference products (64GB × 16), 1 Atlas A2 inference products (64GB × 8) | [Download](https://modelers.cn/models/Modelers_Park/Qwen3-1.7B) |
| Qwen3-4B | 1 Atlas A3 inference products (64GB × 16), 1 Atlas A2 inference products (64GB × 8) | [Download](https://modelers.cn/models/Modelers_Park/Qwen3-4B) |
| Qwen3-8B | 1 Atlas A3 inference products (64GB × 16), 1 Atlas A2 inference products (64GB × 8) | [Download](https://modelers.cn/models/Modelers_Park/Qwen3-8B) |
| Qwen3-14B | 1 Atlas A3 inference products (64GB × 16), 1 Atlas A2 inference products (64GB × 8) | [Download](https://modelers.cn/models/Modelers_Park/Qwen3-14B) |
| Qwen3-32B | 1 Atlas A3 inference products (64GB × 16), 1 Atlas A2 inference products (64GB × 8) | [Download](https://modelers.cn/models/Modelers_Park/Qwen3-32B) |

**解读**：BF16 精度下，6 个模型规模的硬件需求完全一致，均要求 1 台 Atlas A3（16 卡，64GB × 16 即总内存约 1TB）或 1 台 Atlas A2（8 卡，64GB × 8 即总内存 512GB）。模型权重均来自 modelers.cn 的 Modelers_Park 仓库。值得注意的是，即便是 0.6B 最小模型也建议占用整台 A3/A2 机器，反映了 BF16 权重对显存/内存的最低底线约束主要来自框架与 KV Cache 等开销，而非模型参数本身。

**表 2：Atlas A2/A3 推理产品的量化版本**

| Model | Quantization | Hardware Requirement | Download |
|-------|-------------|---------------------|----------|
| Qwen3-32B-W4A4 | W4A4 | 1 Atlas A3 inference products (64GB × 16) or 1 Atlas A2 inference products (64GB × 8) | [Download](https://www.modelscope.cn/models/vllm-ascend/Qwen3-32B-W4A4) |
| Qwen3-32B-W8A8 | W8A8 | 1 Atlas A3 inference products (64GB × 16) or 1 Atlas A2 inference products (64GB × 8) | [Download](https://www.modelscope.cn/models/vllm-ascend/Qwen3-32B-W8A8) |

**解读**：A2/A3 的量化仓库仅提供 32B 一种规模的两种精度变体，权重来自 ModelScope 的 `vllm-ascend` 官方仓库。硬件形态与 BF16 一致，但实际显存占用可大幅降低——W4A4（权重量化 4bit、激活量化 4bit）相比 BF16 压缩约 8 倍，为单卡部署更大模型创造可能；W8A8（8bit/8bit）则提供精度与性能的折中。

**表 3：Atlas 300I DUO 的量化版本**

| Model | Quantization | Hardware Requirement | Download |
|-------|-------------|---------------------|----------|
| Qwen3-8B-W8A8SC | W8A8SC | Atlas 300I DUO (TP1) | [Download](https://www.modelscope.cn/models/Eco-Tech/Qwen3-8B-w8a8sc-310-vllm) |
| Qwen3-14B-W8A8SC | W8A8SC | Atlas 300I DUO (TP1) | [Download](https://www.modelscope.cn/models/Eco-Tech/Qwen3-14B-w8a8sc-310-vllm) |
| Qwen3-32B-W8A8SC | W8A8SC | Atlas 300I DUO (TP4) | [Download](https://www.modelscope.cn/models/Eco-Tech/Qwen3-32B-w8a8sc-310-vllm) |

**解读**：Atlas 300I DUO 使用 W8A8SC（"SC" 指 SmoothQuant 或类似融合方案，专为 310P 处理器优化）量化权重。8B/14B 用 TP1（单卡张量并行即可）即可部署，32B 则需 TP4（4 卡张量并行）。权重来自 Eco-Tech 第三方仓库而非官方，反映该量化方案为社区/合作伙伴提供。W8A8SC 后缀 `-310` 对应昇腾 310P 处理器（Atlas 300I DUO）。

## 【公式解读】

原文无公式。

## 【关联】

本文档作为 Qwen3 Dense 系列模型的"端到端"部署指南，处于 vllm-ascend 文档体系的中游节点，向上/向外引用：

- **【模型支持矩阵】**（`../../user_guide/support_matrix/supported_models.md`）：用于查询 Qwen3 Dense 模型的官方支持状态、特性分级。
- **【特性配置指南】**（`../../user_guide/feature_guide/index.md`）：本文档第 2 节直接指向，介绍具体特性如何启用。
- **【多节点通信验证】**（`../../getting_started/installation.md#installation-multi-node-interconnect`）：第 3.2 节引用的多节点部署前置条件；同一文件 `../../getting_started/installation.md` 也是源码安装的总入口（4.2 节隐含依赖）。
- **【环境变量】**（`../../user_guide/configuration/env_vars.md`）：部署性能调优时常用的 vLLM-Ascend 环境变量（如 `VLLM_ASCEND_*`）的参考。
- **【AIS Bench 评估】**（`../../developer_guide/evaluation/using_ais_bench.md` 及 `#execute-performance-evaluation`）：用于本文档后续将涉及的精度/性能评测章节（原文在末尾被截断，但配套的 ais_bench 工具链是评估必选）。
- **【性能优化与调优】**（`../../developer_guide/performance_and_debug/optimization_and_tuning.md`）：与量化、服务级别配置（max-num-seqs、max-model-len 等）调优相关。
- **【特性矩阵】**（`../../user_guide/support_matrix/feature_matrix.md`）：从横向特性维度（如 chunked prefill、prefix caching、LoRA 等）确认 Qwen3 Dense 在 vLLM-Ascend 上的支持情况。
- **【FAQ】**（`../../faqs.md`）：用户级常见问题排查入口。

整体上，本文是"模型维度的纵向指南"，串联了 *支持矩阵 → 环境准备 → 部署 → 量化 → 评估* 闭环，其上下游全部由上述内部链接覆盖。

## 【使用方法】

**镜像拉取**（原文）：

```bash
docker pull quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
```

**镜像启动**（三选一，按硬件）：
- **Atlas A3**：使用 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`，映射 `/dev/davinci0` 至 `/dev/davinci15` 共 16 个芯片。
- **Atlas A2**：使用默认镜像 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，映射 `/dev/davinci0` 至 `/dev/davinci7` 共 8 个芯片。
- **Atlas 300I DUO**：使用 `-310p` 镜像，映射 `/dev/davinci0` 至 `/dev/davinci7`，同时设置 `--shm-size=10g` 与 `-p 8080:8080`。

三种启动命令均需挂载的卷（原文）：
- `/usr/local/dcmi`
- `/usr/local/Ascend/driver/tools/hccn_tool`（A2/A3 需要，300I DUO 未列）
- `/usr/local/bin/npu-smi`
- `/usr/local/Ascend/driver/lib64/`
- `/usr/local/Ascend/driver/version.info`
- `/etc/ascend_install.info`
- `/root/.cache`

必带设备：`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`。

**安装校验**（原文）：

```bash
docker ps | grep vllm-ascend-env   # 容器状态应为 Up
pip show vllm-ascend               # 版本应与镜像一致
```

**源码安装**：原文在 4.2 节被截断（原文："If you prefer to build from source instead of using the Docker image, install vLLM-Ascend"），具体命令需查阅 `../../getting_started/installation.md`。

**多节点前置**：部署前需按 `../../getting_started/installation.md#installation-multi-node-interconnect` 验证多节点通信。

**部署/量化/评估具体命令**（vllm serve、量化脚本、ais_bench 评测）：原文在第 4.2 节后被截断，未涉及具体启动与评测命令，请参考上文【关联】中列出的 ais_bench 与 optimization_and_tuning 文档。
