# Kimi-K2.6

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Kimi-K2.6.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Kimi-K2.6.md

# Kimi-K2.6 部署文档深度解读

## 【定位】
本文档是 vLLM-Ascend v0.20.0rc1 版本中 Kimi-K2.6 模型的端到端验证与部署指南，涵盖模型特性矩阵查询、环境准备（Docker/源码）、单节点与多节点在线服务部署、精度与性能评估的完整流程，属于该模型首次被官方支持的适配文档。

---

## 【技术要点】

1. **模型性质**：Kimi-K2.6 是开源原生多模态 Agentic 模型，在 Kimi-K2-Base 之上通过约 **15 万亿**（approximately 15 trillion）混合视觉与文本 token 进行持续预训练而成，支持视觉/语言融合理解、Agent 能力、即时与思考模式、对话与 Agent 范式。

2. **硬件拓扑**：量化版 `Kimi-K2.6-w4a8` 需要 **1 个 Atlas 800 A3（64GB × 16）节点** 或 **2 个 Atlas 800 A2（64GB × 8）节点**；建议将权重下载至多节点共享目录 `/root/.cache/`。

3. **三种权重变体**：
   - `Kimi-K2.6-w4a8`（w4a8 量化主模型）
   - `kimi-k2.6-eagle3`（Eagle3 MTP 推测解码 draft 模型）
   - `Kimi-K2.5-DFlash`（基于轻量级 block diffusion 的并行 draft 推测解码框架）

4. **环境变量关键参数**：原文给出 `HCCL_OP_EXPANSION_MODE="AIV"`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`HCCL_BUFFSIZE=600`、`TASK_QUEUE_ENABLE=1`，并可选 jemalloc 预加载 `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2`；同时设置 CPU 调度器为 `performance`、`vm.swappiness=0`、`kernel.numa_balancing=0`、`kernel.sched_migration_cost_ns=50000`。

5. **vLLM serve 关键参数**：`--tensor-parallel-size 4`、`--data-parallel-size 4`、`--enable-expert-parallel`、`--max-num-seqs 4`、`--max-model-len 34816`、`--max-num-batched-tokens 16384`、`--gpu-memory-utilization 0.87`、`--quantization ascend`；编译配置 `cudagraph_mode: FULL_DECODE_ONLY`；多模态编码器 `--mm-encoder-tp-mode data`；`--speculative-config '{"method": "dflash","model": "z-lab/Kimi-K2.5-DFlash", "num_speculative_tokens": 15}'`。

6. **版本约束**：使用 `tool_calls` 特性时 `transformers` 版本须 ≤ 4.57.6；若 vllm-ascend 升级至 v0.21 及以上，此限制解除。

---

## 【关键机制与数据】

**工作原理（原文要点抽取）**：
- 单节点部署时 Prefill 与 Decode 在同一节点内完成（原文："Single-node deployment completes both Prefill and Decode within the same node."）
- DFlash 推测解码（原文："a speculative decoding framework that leverages a lightweight block diffusion model for parallel drafting"）通过轻量级 block diffusion 模型实现并行 draft，配合主模型 `z-lab/Kimi-K2.5-DFlash`，每次生成 15 个推测 token。
- 平衡调度开关 `enable_balance_scheduling`（原文）：在 v1 scheduler 下开启可提高输出吞吐并降低 TPOT，但在部分场景下会劣化 TTFT；**PD 分离场景下不推荐启用**。
- 多模态编码器 TP 模式 `--mm-encoder-tp-mode data`：在测试多模态输入时推荐使用 data 模式以优化多模态编码器推理的张量并行。
- Prefix caching 默认关闭（原文通过 `--no-enable-prefix-caching` 实现），原文提示可通过移除该选项启用。

**性能/精度数据（原文标注）**：
- 性能测试：输入长度 3.5K、输出长度 1.5K 时，`--max-model-len` 设为 `16384` 即可（原文）；精度测试时该值至少需设为 `35000`。
- w4a8 权重下 kvcache 会获得更多显存配额（原文），可通过增大 `--max-num-seqs` 提升系统吞吐。

---

## 【表格解读】

**原文无表格。**

文档全文以命令、参数列表、链接为主，未出现结构化的参数表或性能对比表。

---

## 【公式解读】

**原文无公式。**

文档未给出任何 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

依据原文出现的内部链接，可梳理出 Kimi-K2.6 文档与仓库其他模块的关联关系：

| 关联模块 | 链接锚点 | 关系说明 |
|----------|----------|----------|
| Supported Models 矩阵 | `../../user_guide/support_matrix/supported_models.md` | 查询 Kimi-K2.6 支持的功能矩阵（特性开关） |
| Feature Guide 索引 | `../../user_guide/feature_guide/index.md` | 获取各项特性的具体配置方式 |
| Multi-node Interconnect 验证 | `../../getting_started/installation.md#installation-multi-node-interconnect` | 多节点部署前必做的节点间通信验证 |
| Prebuilt Image 使用 | `../../getting_started/installation.md#installation-prebuilt-image` | Docker 镜像选择与启动 |
| 总安装指南 | `../../getting_started/installation.md` | 源码安装 `vllm-ascend` 的入口 |
| 公共 FAQ | `../../faqs.md` | 部署/服务异常时的故障排查 |
| PD Disaggregation (Mooncake) 多节点 | `../features/pd_disaggregation_mooncake_multi_node.md` | PD 分离部署特性（在「5.1 单节点」段落中提示多节点部署可参考，且说明 `enable_balance_scheduling` 不推荐在 PD 分离下启用） |
| AIS Bench 性能评估 | `../../developer_guide/evaluation/using_ais_bench.md` 及 `#execute-performance-evaluation` | 模型精度与性能评估的执行方法 |

---

## 【使用方法】

**1. 模型权重下载（原文 §3.1）**：
- `Kimi-K2.6-w4a8`：`https://www.modelscope.cn/models/Eco-Tech/Kimi-K2.6-W4A8`
- `kimi-k2.6-eagle3`：`https://huggingface.co/lightseekorg/kimi-k2.6-eagle3`
- `Kimi-K2.5-DFlash`：`https://huggingface.co/z-lab/Kimi-K2.5-DFlash`

**2. Docker 安装（原文 §4.1）**：
- A3 系列镜像：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`，需挂载 16 个 `/dev/davinci0–15` 设备 + `davinci_manager`/`devmm_svm`/`hisi_hdc`，并映射 `/usr/local/dcmi`、`/usr/local/Ascend/driver/tools/hccn_tool`、`npu-smi`、driver lib64、version.info、`ascend_install.info`、`/root/.cache`。
- A2 系列镜像：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，需挂载 8 个 `/dev/davinci0–7` 设备 + 其余驱动路径。
- 通用参数：`--shm-size=1g --net=host --privileged=true`。
- 验证容器运行：`docker ps`。

**3. 源码安装（原文 §4.2）**：
- 参考 `installation` 章节；多节点需在每节点分别配置环境；如使用 `tool_calls`，确保 `transformers ≤ 4.57.6`（v0.21+ 自动解除）。

**4. 单节点在线服务（原文 §5.1）**：
- 设置环境变量（见【技术要点】4），然后执行 `vllm serve` 命令（详见上文【技术要点】5）。
- 服务验证命令（原文片段，文档在末尾被截断）：
  ```shell
  curl http://<node_ip>:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
          "model": "kimi_k26",
          "messages": [{
              "role": "user",
              "content": [
              {
                "type": "text",
                "text": "The future of AI is"
              }]
          }],
          "max_tokens": 1024,
  ```
  （注：原文此处内容不完整，后续字段如 `temperature`、请求结尾的 `}'` 未给出。）

**5. 多节点部署（原文 §3.2 提示）**：
- 须先按 `installation.md#installation-multi-node-interconnect` 验证节点间通信；具体多节点启动脚本原文未在本节给出（需参考 `5 Online Service Deployment` 后续小节，原文已截断）。

**6. 性能/精度评估（原文 §1 与文末链接）**：
- 入口：`../../developer_guide/evaluation/using_ais_bench.md` 与 `#execute-performance-evaluation` 锚点。

---

> ⚠️ **原文截断说明**：所提供的原文在 `v1/chat/completions` 的 curl 命令中途中断（`"max_tokens": 1024,` 后无后续内容），且 `5 Online Service Deployment` 章节的标题后只展示了 §5.1 单节点部署，§5.2 多节点部署及后续评估章节内容未包含在所提供的原文片段中。本解读严格基于所提供的原文，未对缺失部分进行任何臆测补全。
