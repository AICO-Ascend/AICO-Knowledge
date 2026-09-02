# Qwen3-Omni-30B-A3B-Thinking

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-Omni-30B-A3B-Thinking.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Omni-30B-A3B-Thinking.md

# Qwen3-Omni-30B-A3B-Thinking 文档深度解读

## 【定位】
本文档是 vLLM-Ascend 平台上 Qwen3-Omni-30B-A3B-Thinking 多模态 MoE 模型（原生端到端多语言全模态基础模型，支持文本/图像/音频/视频输入与文本/语音流式输出，含思维链推理）的**端到端部署与验证指南**，覆盖特性支持矩阵确认、模型权重准备（BF16 与 W8A8 量化两种形态）、Docker/源码两种安装路径、单节点在线服务部署（Prefill 与 Decode 同节点）等关键环节，明确指出该模型首次支持版本为 v0.12.0rc1，文档基于 vLLM-Ascend v0.22.1rc 验证。

## 【技术要点】
- **多模态定位与 MoE 架构**：Qwen3-Omni-30B-A3B 属于 MoE 模型，因总参数规模相对较小，**不涉及 PD 分离**（Prefill 与 Decode 同节点完成），但部署时**必须使用 Expert Parallelism (EP)**，把专家分散到各 NPU 上。
- **硬件与卡数推荐**：BF16 与 W8A8 两个变体硬件要求相同 —— **Atlas 800I A3（64G，推荐 1~2 卡）** 或 **Atlas 800I A2（64G，推荐 2~4 卡）**，卡数可根据实际情况调整。
- **W8A8 混合量化策略**（按模型结构分层）：
  - Embedding 层：BF16（不量化）
  - Q/K 归一化（q_norm / k_norm）：BF16
  - Attention 投影（q/k/v/o_proj）：**Static W8A8**，采用预先计算的 per-tensor scales
  - MoE 路由门（mlp.gate）：BF16
  - MoE 专家投影（gate/up/down_proj）：**Dynamic W8A8**，推理时实时计算 input scales
  - W8A8 权重无直接下载源，需基于 BF16 通过 **msmodelslim** 自量化生成（见 Quantization Guide）。
- **Docker 部署关键差异**：A3 采用 dual-die 设计（每台 8 NPU 物理卡，对应 `/dev/davinci[0-15]` 共 16 die），共享机器上可按需映射子集（如 `/dev/davinci[0-7]`）；A2 仅 8 个 die（`/dev/davinci0-7`）。
- **关键环境变量**（部署在线服务时必设）：
  - `ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`（A2/A3 示例）
  - `HCCL_OP_EXPANSION_MODE="AIV"`（A3 需要，A2 注释为 not needed），用于规避默认 FFTS+ 模式下 HcclAllreduce 因流与 shape 限制导致的失败
  - `HCCL_BUFFSIZE=1024`
  - `OMP_PROC_BIND=false`、`OMP_NUM_THREADS=1`
  - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`
- **vllm serve 关键参数（示例配置，A2/A3）**：
  - `--served-model-name qwen3-omni`
  - `--trust-remote-code`
  - `--max-num-seqs 100`
  - `--max-model-len 40960`
  - `--max-num-batched-tokens 16384`
  - `--tensor-parallel-size 4`
  - `--enable-expert-parallel`
  - `--quantization ascend`
  - `--distributed_executor_backend "mp"`
  - `--no-enable-prefix-caching`
  - `--compilation-config '{"...`（原文在该位置被截断，未给出完整 JSON）
- **系统依赖**：`pip install qwen_omni_utils modelscope`；音频处理需 `apt-get install -y ffmpeg` 并用 `ffmpeg -version` 校验。

## 【关键机制与数据】
**模型能力机制（原文）**：Qwen3-Omni 是 *native end-to-end multilingual omni-modal foundation model*，处理文本/图像/音频/视频，输出文本与自然语音的实时流式响应；Thinking 变体仅包含 thinker 组件，启用 chain-of-thought 推理，支持音频/视频/文本输入、仅文本输出。

**混合量化机制（原文）**：W8A8 是「分层混合」方案 —— Attention 部分用预先静态算好的 per-tensor scale 做静态量化以省去推理时开销，MoE 专家层则改用动态量化（输入 scale 推理时即时计算），换取在专家权重上的更高压缩比。Embedding、归一化、路由门这三条「敏感 / 小体积」通路保留 BF16 以保护精度。

**HCCL 通信机制（原文）**：`HCCL_OP_EXPANSION_MODE="AIV"` 显式将 allreduce 等集合通信搬到 AIV 引擎，目的是规避默认 FFTS+ 模式在某些 stream/shape 组合下出现的 HcclAllreduce 失败。

**A3 die 拓扑（原文）**：Atlas 800I A3 为 dual-die 设计，物理 8 卡对应逻辑 16 die，设备文件命名 `/dev/davinci[0-15]`；映射时**不是按「卡」而是按「die」**挂载 `--device`，这是和 A2 部署最显著的差异。

**vllm serve 关键阈值（原文）**：`--max-num-seqs 100`、`--max-model-len 40960`、`--max-num-batched-tokens 16384`、`--tensor-parallel-size 4`、TP 与 EP 组合使用；context 长度 40960 与 batched-tokens 16384 是本次官方验证的配置基线。

**性能/精度评估数据**：原文 §1 提到本文档包含「accuracy and performance evaluation」步骤，但**提供原文的章节内容在第 4.2 节末尾 / 第 5.1 节命令中途被截断**，未给出可引用的具体指标数字与吞吐量数据，故本文不臆造。

## 【关联】
- 与 **Quantization Guide**（`../../user_guide/feature_guide/quantization.md`）耦合：W8A8 权重需通过 msmodelslim 从 BF16 模型量化得到，本文反复提醒「本文所有 model path 应替换为本地实际路径」。
- 与 **env vars**（`../../user_guide/configuration/env_vars.md`）耦合：部署章节密集列出 `HCCL_OP_EXPANSION_MODE`、`HCCL_BUFFSIZE`、`OMP_*`、`PYTORCH_NPU_ALLOC_CONF`、`ASCEND_RT_VISIBLE_DEVICES` 等，建议结合 env_vars 章节做完整环境核查。
- 与 **additional config**（`../../user_guide/configuration/additional_config.md`）耦合：`--compilation-config`、量化选项（`ascend`）、`--no-enable-prefix-caching` 等属于附加配置范畴。
- 与 **optimization_and_tuning**（`../../developer_guide/performance_and_debug/optimization_and_tuning.md`）耦合：上文提到本文档会做性能评估，预期会指引用户跳转到性能调优指南比对基线。
- 与 **feature_matrix**（`../../user_guide/support_matrix/feature_matrix.md）/ supported_models** 联动：§2 明确把「特性矩阵」与「特性配置」两类信息分别外链到支持模型页与 feature guide 索引，作为本文档的前置查询入口。
- 与 **FAQs**（`../../faqs.md`）耦合：作为兜底排错入口（HcclAllreduce、FFmpeg、容器设备映射等典型问题沉淀处）。

## 【使用方法】
**原文给出的启用方式（按章节）**：

1. **查特性矩阵**：先访问 [Supported Features List](https://docs.vllm.ai/projects/ascend/zh-cn/latest/user_guide/support_matrix/supported_models.html) 与 [Feature Guide](https://docs.vllm.ai/projects/ascend/zh-cn/latest/user_guide/feature_guide/index.html) 确认目标软硬件特性。
2. **准备权重**：
   - BF16：从 ModelScope `Qwen/Qwen3-Omni-30B-A3B` 下载。
   - W8A8：无下载源，用 msmodelslim 从 BF16 量化得到（细节见 Quantization Guide）。
   - 将权重放置到多节点共享目录。
3. **安装**（二选一）：
   - **Docker**：`docker pull quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，再分别按 A3 / A2 模板 `docker run`；A3 注意挂 `/dev/davinci[0-15]` 与 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`、相关 `/usr/local/Ascend/...` 与 `/etc/ascend_install.info`、`/etc/hccn.conf` 目录；默认工作目录 `/workspace`。验证：`docker ps | grep vllm-ascend-env` 与容器内 `pip show vllm-ascend`。
   - **源码**：先 `git clone https://github.com/vllm-project/vllm.git && pip install -e .`，再 `git clone https://github.com/vllm-project/vllm-ascend.git && pip install -e .`；多节点需逐节点重复。验证：`pip show vllm vllm-ascend`。
4. **系统依赖（必装）**：`pip install qwen_omni_utils modelscope`；`apt-get update && apt-get install -y ffmpeg`，然后 `ffmpeg -version` 校验。
5. **导出 HCCL 模式（推荐 A3）**：`export HCCL_OP_EXPANSION_MODE="AIV"`。
6. **单节点在线部署（Prefill + Decode 同节点）**：
   ```bash
   export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
   export HCCL_OP_EXPANSION_MODE="AIV"
   export HCCL_BUFFSIZE=1024
   export OMP_PROC_BIND=false
   export OMP_NUM_THREADS=1
   export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True

   vllm serve your_model_path \
       --served-model-name qwen3-omni \
       --trust-remote-code \
       --max-num-seqs 100 \
       --max-model-len 40960 \
       --max-num-batched-tokens 16384 \
       --tensor-parallel-size 4 \
       --enable-expert-parallel \
       --quantization ascend \
       --distributed_executor_backend "mp" \
       --no-enable-prefix-caching \
       --compilation-config '{"...（原文被截断）'
   ```
   提示：因模型参数量较小，**本模型不做 PD 分离**；EP 必须开启以分散 MoE 专家。

**注意事项**：原文第 5.1 节的 `vllm serve` 命令在 `--compilation-config '{"cuda` 处被截断，**后续内容（完整 JSON、Accuracy / Performance 评估章节、多节点部署章节等）在提供的原文范围内未出现**，故不做展开。
