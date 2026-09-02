# Qwen3-VL-30B-A3B-Instruct

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-VL-30B-A3B-Instruct.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-VL-30B-A3B-Instruct.md

# Qwen3-VL-30B-A3B-Instruct 文档深度解读

## 【定位】

这篇文档是 vllm-ascend `v0.13.0` 验证周期为 `Qwen3-VL-30B-A3B-Instruct`（稀疏 MoE 视觉-语言模型）撰写的部署与验证教程,解决如何在 Ascend 硬件（Atlas 800 A3 / A2 / 950DT）上完成该模型的环境准备、Docker/源码安装、在线服务部署、离线推理、功能验证、精度与性能评估、性能调优及 FAQ 全流程的问题。

---

## 【技术要点】

1. **模型基座属性**:稀疏 MoE 架构,总参数量约 30B、每 token 激活参数约 3B;归属 Qwen3-VL 系列,支持图像理解、视频理解、多模态对话、长上下文在线服务。
2. **三档硬件需求**:
   - BF16 版需要 1× Atlas 800 A3 (64G × 16) 或 1× Atlas 800 A2 (64G × 8)
   - 量化版 `Qwen3-VL-30B-A3B-Instruct-w8a8-mxfp8` 需要 1× Ascend 950DT (96G × 8)
3. **Docker 镜像分机型对应**:950DT 用 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-950DT`,A3 用 `-a3` 标签,A2 使用默认标签;三套命令分别挂载 8/16/8 个 `/dev/davinci*` 设备;950DT 还需挂载 `/dev/devmm_svm` 等专用设备。
4. **在线服务关键环境变量**:`VLLM_USE_MODELSCOPE=True`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、950DT 上设 `HCCL_BUFFSIZE=400`,A3 上设 `HCCL_BUFFSIZE=1024`。
5. **关键 vllm serve 参数(950DT 量化版示例)**:`--tensor-parallel-size 8`、`--enable-expert-parallel`、`--quantization ascend`、`--max-model-len 32768`、`--max-num-seqs 32`、`--max-num-batched-tokens 8192`、`--limit-mm-per-prompt.image 1`、`--limit-mm-per-prompt.video 0`、`--gpu-memory-utilization 0.9`、`--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`,并显式 `--no-enable-prefix-caching`、`--mm-processor-cache-gb 0`。
6. **多模态资源配额**:示例中 `--limit-mm-per-prompt.image 1` 同时 `--limit-mm-per-prompt.video 0`,说明当前单节点示例仅适配图像在线服务(原文描述:"The following examples are suitable for image-only online serving")。

---

## 【关键机制与数据】

> ⚠️ **原文在第 5.1 节 A3 系列命令中部截断**,以下严格基于原文已提供的部分解析。

- **工作原理(原文 Section 1)**:`Qwen3-VL-30B-A3B-Instruct` 是一个稀疏 MoE 视觉-语言模型;通过 `--enable-expert-parallel` 在 Ascend NPU 上做专家并行,配合 `--tensor-parallel-size` 做张量并行。
- **数据流关键约束(原文 Section 5.1)**:`--max-model-len 32768`、`--max-num-batched-tokens 8192` 控制上下文与批处理上限;`--max-num-seqs 32` 限制并发序列;多模态配额 `image=1 / video=0`。
- **CUDA Graph 策略**:`--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'` 仅在 Decode 阶段启用整图捕获,降低 Prefill 阶段编译开销。
- **专家并行 + 量化叠加**:量化版必须配 `--quantization ascend`,BF16 版不需要该参数(原文:"The W8A8 version needs `--quantization ascend`")。
- **AIV 通信优化**:`HCCL_OP_EXPANSION_MODE="AIV"` 启用 HCCL 的 AIV 通信扩展模式,Ascend 950DT 与 A3 都使用此设置。
- **性能/精度数据**:原文未提供具体的吞吐量、延迟、精度数字(被截断,或本节本身未列出)。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

| 关联链接 | 关联角色 |
|---|---|
| `../../user_guide/support_matrix/supported_features.md` | 给出该模型的支持特性矩阵(Section 2) |
| `../../user_guide/feature_guide/index.md` | 给出对应特性的配置说明(Section 2) |
| `../../getting_started/installation.md#installation-prebuilt-image` | 4.1 节 Docker 安装的根指南,三种机型 Docker 命令均基于此 |
| `../../getting_started/installation.md` | 4.2 节源码安装的根指南 |
| `../../faqs.md` | 文末预留的常见问题入口(原文未展开) |
| `../../developer_guide/evaluation/using_ais_bench.md` | 性能/精度评估方法(原文未展开,但目录提及) |
| `../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation` | 性能评估执行入口(原文未展开) |
| `../../developer_guide/performance_and_debug/optimization_and_tuning.md` | 性能调优参考(原文未展开) |
| `../../user_guide/support_matrix/feature_matrix.md` | 特性矩阵(原文未展开) |

文档整体定位为"教程型 guide",向上游依赖 `installation.md` 与 `support_matrix/supported_features.md` 获取环境与特性基线;向下游预留 `evaluation` 与 `performance_and_debug` 的衔接入口。

---

## 【使用方法】

**1. 模型权重下载(原文 Section 3.1)**
- BF16:`https://www.modelscope.cn/models/Qwen/Qwen3-VL-30B-A3B-Instruct`
- 量化 W8A8 MXFP8:`https://modelscope.cn/models/Eco-Tech/Qwen3-VL-30B-A3B-Instruct-w8a8-mxfp8`
- 建议下载到多节点共享目录。

**2. Docker 启动(原文 Section 4.1)** —— 原文给出了三套完整 `docker run` 命令,关键参数:

| 机型 | 镜像标签 | 设备数 | shm-size |
|---|---|---|---|
| Ascend 950DT | `{{ vllm_ascend_version }}-950DT` | 8×davinci + davinci_manager + hisi_hdc + ummu + uburma | 1g |
| Atlas 800 A3 | `{{ vllm_ascend_version }}-a3` | 16×davinci + davinci_manager + devmm_svm + hisi_hdc | 512g |
| Atlas 800 A2 | `{{ vllm_ascend_version }}`(默认) | 8×davinci + davinci_manager + devmm_svm + hisi_hdc | 512g |

**3. 安装验证(原文 Section 4.1)**
```bash
docker ps | grep vllm-ascend     # 期望:容器状态 Up
pip show vllm-ascend             # 期望:版本与镜像标签一致
```

**4. 源码安装(原文 Section 4.2)**
```bash
git clone https://github.com/vllm-project/vllm.git && cd vllm && pip install -e .
git clone https://github.com/vllm-project/vllm-ascend.git && cd vllm-ascend && pip install -e .
pip show vllm vllm-ascend        # 多节点需每节点都执行
```

**5. 单节点在线部署(原文 Section 5.1)**
- 950DT 量化版启动脚本(原文已给出,见【技术要点】第 5 条的参数列表)。
- A3 系列脚本:**原文截断未完**,完整命令请参考原文。
- A2 系列脚本:**原文未提供**(原文在 A3 段中途中断)。

**6. 后续章节(离线推理/功能验证/精度评估/性能评估/性能调优/FAQ)**

> **原文未涉及(被截断)** —— Section 5.1 之后的内容(从 A3 系列的 `vllm serve` 命令中部起,以及 A2 系列、5.2 多节点部署、第 6~9 节)在所提供原文中未出现,无法解析。
