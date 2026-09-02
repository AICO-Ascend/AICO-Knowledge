# Suffix Speculative Decoding

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/features/suffix_speculative_decoding.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/features/suffix_speculative_decoding.md

# vllm-ascend Suffix Speculative Decoding 文档深度解读

---

## 【定位】

这篇文档解决"如何在 Atlas A2 硬件上基于 vllm-ascend 部署并量化评估 Suffix Speculative Decoding（基于模式匹配的后缀解码）推理加速能力"的问题，描述了 vllm-ascend 通过集成 Arctic Inference 插件、不引入额外 draft 模型即可在 CPU 端完成推测性解码的能力。

---

## 【技术要点】

1. **机制定位**：Suffix Decoding 是基于模式匹配的推测解码优化方法，同时从 prompt 和已生成内容中检索重复序列，使用频率统计预测最可能的 token 续写；运行完全在 CPU 上，不需要额外 GPU 资源或 draft 模型。

2. **硬件与模型**：使用单台 Atlas 800T A2 节点、4 卡部署 Qwen3-32B 模型实例；启动命令通过 `--device /dev/davinci0..3` 暴露 4 张 NPU。

3. **关键插件依赖**：必须先在容器内 `pip install arctic-inference`，再通过 `--speculative-config '{"method": "suffix", "num_speculative_tokens": 3}'` 启用；本测试统一设置 `num_speculative_tokens = 3`。

4. **核心环境变量**：`ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`、`TASK_QUEUE_ENABLE=1`、`HCCL_OP_EXPANSION_MODE="AIV"`（启用 AIVector core 直接调度 ROCE 通信）。

5. **附加配置**：`--additional-config '{"pa_shape_list":[48,64,72,80], "weight_prefetch_config":{"enable":true}}'`；`--max-model-len 5500`、`--max-num-batched-tokens 40960`、`--gpu-memory-utilization 0.9`、`--tensor-parallel-size 4`。

6. **基准方法**：使用 AISBench 对 6 个开源数据集进行吞吐/TPOT 对比，SLO 条件为 TPOT < 50ms，覆盖并发度从 1 到 26；原文汇总结论为 Qwen3-32B 在各真实数据集上吞吐提升约 **20%–80%**。

---

## 【关键机制与数据】

**工作原理（原文概述）**：
- Suffix Decoding 在 prompt 与已生成内容两侧并行检索**重复序列**，通过**频率统计**选出最可能的 token 续写作为 draft；不同于传统推测解码，draft 阶段全程在 CPU 完成，无需 draft 模型。
- 在 vllm-ascend 中通过加载 Arctic Inference 插件获得该能力，再由 vLLM 的 `--speculative-config` 暴露 `method: suffix` 路径。

**数据流与角色分工**：
- **CPU 侧**（原文）：执行后缀模式检索与频次统计，产出候选 token。
- **NPU 侧**（原文）：Atlas A2 4 卡 TP=4 并行推理目标模型 Qwen3-32B，对候选 token 做 verify。
- **通信**（原文）：通过 `HCCL_OP_EXPANSION_MODE="AIV"` 启用 AIVector core 直接调度 ROCE 通信。

**性能数据（原文给出的总结区间）**：
- 原文：「吞吐量提升约 20% ~ 80%」；在满足 SLO TPOT < 50ms 前提下：
  - **High Gain**：AGIEval、GSM8K → 吞吐提升 > 50%。
  - **Medium-Low Gain**：ARC、ShareGPT → 吞吐提升 20% ~ 30%。
- 原文表格中给出的可验证样本（HumanEval BS=1）：Base TPOT 55.1ms → Suffix TPOT 37.9ms（TPOT Gain 45.2%），Base Throughput 18.1 TPS → Suffix Throughput 26.3 TPS（TPS Gain 45.1%），Accept Rate 27.0%。
- ARC BS=1：Base 52.8ms → Suffix 39.5ms（TPOT Gain 33.7%）；Accept Rate 23.9%。

**适用场景（原文）**：AI agents、code generation 等具有重复模式的任务，加速效果显著。

---

## 【表格解读】

### 表格 1：基准测试覆盖的数据集类别（原文逐字还原）

| **Dataset Category**           | **Dataset Name** |
| ------------------------------ | ---------------- |
| Code Generation                | HumanEval        |
| Common Sense Reasoning         | ARC              |
| Mathematical Reasoning         | gsm8k            |
| Natural Language Understanding | SuperGLUE_BoolQ  |
| Comprehensive Examination      | AGIEval          |
| Multi-turn Dialogue            | ShareGPT         |

**逐行解读**：
- 原文用 6 类任务覆盖代码、常识、数学、NLU、综合考试与多轮对话，避免单一类型偏置；AISBench 工具对全 6 个数据集都支持性能测试。
- 代码生成（HumanEval）与综合考试（AGIEval）原文归入 High Gain；常识（ARC）与多轮对话（ShareGPT）归入 Medium-Low Gain；说明 Suffix Decoding 的收益与"重复/模板化"程度高度相关。

### 表格 2：吞吐提升汇总（原文逐字还原）

| **Dataset Category** | **Typical Representative** | **Throughput Improvement (BS=1-10)** | **SLO TPOT** |
| -------------------- | -------------------------- | ------------------------------------ | ------------ |
| **High Gain**        | AGIEval, GSM8K             | **> 50%**                            | < 50ms       |
| **Medium-Low Gain**  | ARC, ShareGPT              | **20% ~ 30%**                        | < 50ms       |

**逐行解读**：
- 第一行：AGIEval、GSM8K 在 BS=1–10 范围内吞吐提升 >50%，同时 TPOT 仍低于 50ms 的 SLO；属"高收益"档位。
- 第二行：ARC、ShareGPT 提升 20%~30%，同样满足 TPOT<50ms SLO；属"中低收益"档位。
- 注意：BS 范围限定为 1–10，与表格 3 中 HumanEval 测试跑到 BS=26 不同——汇总区间是更保守的表述。

### 表格 3：六数据集原始详细结果（原文逐字还原，原文在 GSM8K BS=1 处截断）

| Concurrency | Avg Input | Avg Output | Requests | Base TPOT(ms) | Base Throughput(TPS) | Suffix TPOT(ms) | Suffix Throughput(TPS) | Accept Rate | TPOT Gain | TPS Gain |
| ----------- | --------- | ---------- | -------- | ------------- | -------------------- | --------------- | ---------------------- | ----------- | --------- | -------- |
| **HumanEval** |         |            |          |               |                      |                 |                        |             |           |          |
| 1           | 150       | 2700       | 100      | 55.1          | 18.1                 | 37.9            | 26.3                   | 27.0%       | 45.2%     | 45.1%    |
| 15          | 150       | 2700       | 100      | 61.6          | 233.8                | 45.8            | 318.2                  | 27.0%       | 34.6%     | 36.1%    |
| 26          | 150       | 2700       | 100      | 64.7          | 403.8                | 50.9            | 519.2                  | 27.0%       | 27.2%     | 28.6%    |
| **ARC**      |           |            |          |               |                      |                 |                        |             |           |          |
| 1           | 76        | 960        | 100      | 52.8          | 18.9                 | 39.5            | 25.4                   | 23.9%       | 33.7%     | 34.6%    |
| 8           | 76        | 960        | 100      | 59.1          | 125.4                | 47.0            | 163.1                  | 23.9%       | 25.7%     | 30.0%    |
| 15          | 76        | 960        | 100      | 59.8          | 245.8                | 48.9            | 311.7                  | 23.9%       | 22.3%     | 26.8%    |
| **GSM8K**    |           |            |          |               |                      |                 |                        |             |           |          |
| 1           |           |            |          |               |                      |                 |                        |             |           |          |

**逐行解读**：
- **列含义**：Concurrency=并发请求数；Avg Input/Output=平均输入/输出 token 数；Requests=请求条数（均为 100）；Base/Suffix TPOT(ms)=启用前后每 token 平均耗时；Base/Suffix Throughput(TPS)=每秒 token 吞吐；Accept Rate=draft token 被目标模型接受的比率；TPOT/TPS Gain=相对基线的提升百分比。
- **HumanEval**：BS=1→15→26 时 Accept Rate 稳定在 27.0%，但 TPOT Gain 由 45.2% 衰减到 27.2%，说明高并发下 draft 命中带来的边际收益收窄；输出 2700 token 较长，代码生成任务天然重复片段多，Accept Rate 较高。
- **ARC**：Accept Rate 23.9%（低于 HumanEval），TPS Gain 仍维持 22.3%–34.6%，说明即使中等 Accept Rate 也能稳定带来吞吐提升。
- **GSM8K**：原文表格在此处被截断，仅给出并发度=1 的行标签，未提供数值；后续行（与 SuperGLUE_BoolQ、AGIEval、ShareGPT）也未在原文中展示。

---

## 【公式解读】

原文无公式。

（文档中所有量化结论均以表格或自然语言形式给出，未出现 LaTeX 或伪代码公式。）

---

## 【关联】

文档涉及的外部/模块关系（基于原文链接与文中引用）：

1. **vllm-ascend 官方镜像**（`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`）：本功能要求在官方容器镜像内运行，是上游 vLLM + Ascend NPU 后端的组合。
2. **Arctic Inference 插件**（Snowflake 开源）：提供 Suffix Decoding 的 CPU 端 draft 实现，是 vLLM 推测解码的扩展插件，原文给出技术原理参考文章 *Fastest Speculative Decoding in vLLM with Arctic Inference and Arctic Training*。
3. **AISBench 基准工具**：用于评估所有数据集性能，原文指向 vLLM-Ascend 文档 *Using AISBench for performance evaluation* 作为子流程的详细说明。
4. **vLLM 推测解码框架**：`--speculative-config '{"method": "suffix", ...}'` 表明 Suffix Decoding 是 vLLM 推测解码 method 的一种取值，因此同样受 `num_speculative_tokens` 等通用参数控制。
5. **ACLGraph 与 weight prefetch**：通过 `--additional-config` 中的 `pa_shape_list` 与 `weight_prefetch_config.enable=true` 与 Ascend 特有的 ACLGraph 预取机制联动。
6. **HCCL 通信栈**：`HCCL_OP_EXPANSION_MODE="AIV"` 表明本方案利用 AIVector core 直接调度 RDMA/ROCE 通信，与 TP=4 的张量并行耦合。
7. **下游 / 内部链接**：原文未给出仓库内部交叉链接。

---

## 【使用方法】

原文给出的启用方式与配置项如下：

1. **拉取镜像**
   ```bash
   docker pull quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
   ```
2. **启动容器**：按原文 `docker run` 模板挂载 `/etc/hccn.conf`、`/usr/local/dcmi`、`/usr/local/Ascend/driver/...`、`/root/.cache` 等，并 `--device /dev/davinci0..3` 与 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`。
3. **安装 Arctic Inference 插件**
   ```bash
   pip install arctic-inference
   ```
4. **启动 vLLM 实例并启用 Suffix Decoding**
   ```bash
   export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
   export TASK_QUEUE_ENABLE=1
   export HCCL_OP_EXPANSION_MODE="AIV"
   vllm serve /data/Qwen3-32B \
     --served-model-name qwen3 \
     --trust-remote-code \
     --distributed-executor-backend mp \
     --tensor-parallel-size 4 \
     --max-model-len 5500 \
     --max-num-batched-tokens 40960 \
     --speculative-config '{"method": "suffix", "num_speculative_tokens": 3}' \
     --gpu-memory-utilization 0.9 \
     --additional-config '{"pa_shape_list":[48,64,72,80], "weight_prefetch_config":{"enable":true}}' \
     --port 8011
   ```
5. **AISBench 基准配置关键项**（原文要求）：
   - `ignore_eos = False`（必须）。
   - `max_out_len` 设为较大值（原文示例 `4000`）以允许自然完整输出。
   - `temperature = 0`、`batch_size = 16`、`retry = 2`、`request_rate = 0`。
   - 性能测试示例命令：`ais_bench --models vllm-api-stream-chat --datasets gsm8k_gen_0_shot_cot_str_perf --debug --summarizer default_perf --mode perf --num-prompts 100`。
