# Qwen3-Coder-30B-A3B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-Coder-30B-A3B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Coder-30B-A3B.md

# Qwen3-Coder-30B-A3B 文档深度解读

## 【定位】
本文档描述如何在 vLLM-Ascend 环境中验证和部署 Qwen3-Coder-30B-A3B（Qwen3 Coder 系列的混合专家 (MoE) 模型,具备 agentic coding 优化、最高 1M tokens 上下文与函数调用能力）,涵盖环境准备、单节点部署、精度与性能评估等主要步骤。

## 【技术要点】

1. **模型规格**:Qwen3-Coder-30B-A3B 是 MoE 模型,总参数 30.5B、每 token 激活 3.3B,基于 Qwen3 base 架构,首次支持版本为 **v0.10.0rc1**,本文档基于 **vLLM-Ascend v0.22.1rc** 验证,**v0.22.1rc 及之后版本可稳定运行**。

2. **硬件要求**:Atlas 800I A3 (64G, 1\~2 cards) 或 Atlas 800I A2 (64G, 2\~4 cards);A3 系列有 8 个 NPU 采用 dual-die 设计,共 16 个芯片 (`/dev/davinci[0-15]`);Eagle3 Draft Model 硬件需求为 NA。

3. **W8A8 混合量化策略**(按模型结构分块):
   - **Embedding 层**:BF16(不量化)
   - **Q/K normalization** (q_norm、k_norm):BF16(权重与偏置)
   - **Attention projections** (q/k/v/o_proj):静态 W8A8,预计算 per-tensor scales,biases 保留为 BF16
   - **MoE routing gate** (mlp.gate):BF16
   - **MoE expert projections** (gate/up/down_proj):动态 W8A8,推理时 on-the-fly 计算输入 scales

4. **部署必备**:MoE 模型必须在 NPUs 间分布 experts,因此必须启用 **Expert Parallelism (EP)** (`--enable-expert-parallel`);搭配 **tensor-parallel-size 4**、`--quantization ascend` 量化、`--distributed_executor_backend "mp"` 等关键参数。

5. **推测解码 (Speculative Decoding)**:支持 Eagle3,通过 `--speculative-config '{"method": "eagle3", "model": "your_eagle3_model_path", "num_speculative_tokens": 3}'` 启用。

6. **编译与内存配置**:`--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'` 限定 cudagraph 模式仅在 decode 阶段启用;`--additional-config '{"weight_nz_mode": 2}'` 控制权重 NZ(非零)布局;`--gpu-memory-utilization 0.95` 调整显存利用率;显式 `--no-enable-prefix-caching` 关闭前缀缓存(原文标注:默认禁用,但被截断)。

## 【关键机制与数据】

- **上下文窗口**:最高支持 1M tokens(原文:"extended context support of up to 1M tokens")。
- **版本约束**:首次支持版本 v0.10.0rc1;验证版本 v0.22.1rc;"all **v0.22.1rc and later versions** can run stably"。
- **Docker 镜像**(原文):`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`(A3 系列)、`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`(A2 系列)。
- **设备挂载**(原文):A3 完整挂载 `/dev/davinci[0-15]` 16 个芯片及 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`;A2 仅挂载 `/dev/davinci[0-7]` 8 个芯片(注:原文将 A2 范围写作 `[0-7]`,但与 A3 "dual-die 16 chips" 的表述无直接对应,原文以 A2 容器命令块为准)。
- **环境变量**(原文):`HCCL_BUFFSIZE=1024`、`HCCL_OP_EXPANSION_MODE="AIV"`(原文标注 "not needed on A2")、`ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`。
- **服务参数**(原文):`--max-num-seqs 100`、`--max-model-len 40960`、`--max-num-batched-tokens 16384`、`--tensor-parallel-size 4`、`--enable-expert-parallel`、`--quantization ascend`、`--distributed_executor_backend "mp"`、`--no-enable-prefix-caching`、`--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`、`--additional-config '{"weight_nz_mode": 2}'`、`--gpu-memory-utilization 0.95`、`--port 8000`。
- **数据流**(原文):工作目录默认为 `/workspace`;vLLM 与 vLLM-Ascend 作为 Python packages 安装于 site-packages;`vllm serve` 提供在线服务,Serve 后可通过 HTTP 客户端调用 `--port 8000` 接口。
- **注意**:文档在 "prefix c" 处被截断,后续关于 `--no-enable-prefix-caching` 的详细解释及后面的章节(精度评估、性能评估、Eagle3 多卡部署等)原文未提供。

## 【表格解读】

原文表格(模型权重变体)逐字还原:

| Model                               | Hardware Requirement                                                                             | Download                                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| Qwen3-Coder-30B-A3B-Instruct (BF16) | Atlas 800I A3 (64G, 1\~2 cards)<br>Atlas 800I A2 (64G, 2\~4 cards) | [Download](https://www.modelscope.cn/models/Qwen/Qwen3-Coder-30B-A3B-Instruct)          |
| Qwen3-Coder-30B-A3B-Instruct-W8A8   | Atlas 800I A3 (64G, 1\~2 cards)<br>Atlas 800I A2 (64G, 2\~4 cards)                               | [Download](https://www.modelscope.cn/models/Eco-Tech/Qwen3-Coder-30B-A3B-Instruct-w8a8) |
| Eagle3 Draft Model                  | NA                                                                                               | [Download](https://huggingface.co/AngelSlim/Qwen3-a3B_eagle3)                           |

逐行解读:

- **第 1 行 (BF16 Instruct)**:基础指令调优模型,精度未量化;适合 A3 单/双卡、A2 2\~4 卡部署;权重从 ModelScope 官方仓库下载。
- **第 2 行 (W8A8 Instruct)**:已经量化好的 INT8 版本(权重与激活均 8-bit),适合显存受限场景,硬件需求与 BF16 一致;若该权重不可下载,可用 **msmodelslim** 将 BF16 模型自行量化(参见 Quantization Guide);文档所有模型路径均需替换为本地实际路径。
- **第 3 行 (Eagle3 Draft Model)**:用作推测解码的 draft 模型,需配合 vLLM 的 `--speculative-config` 使用,`num_speculative_tokens: 3` 表示每轮生成 3 个候选 token;硬件需求为 NA(由主模型所在 NPUs 承载)。

> 注:原文表格标注 "These are the recommended numbers of cards, which can be adjusted according to the actual situation"(卡片数为推荐值,可按实际调整)。

## 【公式解读】

原文无公式。

## 【关联】

本文档与以下内部文档存在链接或主题关联(均来自原文内部链接列表):

- `../../user_guide/support_matrix/supported_models.md` — **Supported Models 矩阵**:被 §2 "Supported Features" 直接引用,用于查询该模型在 vLLM-Ascend 中的兼容性矩阵。
- `../../user_guide/feature_guide/index.md` — **Feature Guide 索引**:被 §2 引用,提供所有特性配置的总入口(EP、量化、推测解码、cudagraph 等均在此体系内)。
- `../../user_guide/feature_guide/quantization.md` — **Quantization Guide**:被 §3 引用,描述如何用 **msmodelslim** 自行从 BF16 量化得到 W8A8 权重(W8A8 混合量化策略即由该指南支撑)。
- `../../getting_started/installation.md` — **Installation Guide**:被 §4.2 末尾引用,提供 Docker 与源码安装的详细补充步骤。
- `../../user_guide/configuration/env_vars.md` — **Environment Variables 文档**:与 §5 中 `HCCL_BUFFSIZE`、`HCCL_OP_EXPANSION_MODE`、`ASCEND_RT_VISIBLE_DEVICES`、`PYTORCH_NPU_ALLOC_CONF` 等环境变量的语义与取值范围对应。
- `../../user_guide/configuration/additional_config.md` — **Additional Config 文档**:与 `--additional-config '{"weight_nz_mode": 2}'` 对应,提供 `weight_nz_mode` 等扩展配置字段说明。
- `../../developer_guide/evaluation/using_ais_bench.md` / `using_lm_eval.md` / `using_opencompass.md` / `using_evalscope.md` — **评估工具链**:文档 §1 明确提到 "accuracy and performance evaluation",这四个链接(在文末链接列表中提供)对应 vLLM-Ascend 官方支持的 4 种精度/性能评估框架(分别为 AIS-Bench、LM-Eval、OpenCompass、EvalScope),构成下游评估的关联模块。

## 【使用方法】

### 安装(原文 §4)

- **Docker 方式**(原文):
  - A3:`docker run` 命令挂载 16 个 davinci 设备及驱动路径,镜像为 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`。
  - A2:`docker run` 命令挂载 8 个 davinci 设备,镜像为 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`。
  - 验证:`docker ps | grep vllm-ascend-env`(容器 `Up`)、`pip show vllm-ascend`(版本匹配)。
- **源码方式**(原文 §4.2):
  ```bash
  git clone https://github.com/vllm-project/vllm.git && cd vllm && pip install -e .
  git clone https://github.com/vllm-project/vllm-ascend.git && cd vllm-ascend && pip install -e .
  pip show vllm vllm-ascend
  ```
  验证命令同上,确认两个包均显示版本信息即安装成功。多节点部署需在每个节点执行相同步骤。

### 在线服务部署(原文 §5.1,Atlas 800I A2/A3)

环境变量与启动命令(原文逐字保留):

```bash
export HCCL_BUFFSIZE=1024
export HCCL_OP_EXPANSION_MODE="AIV"  # not needed on A2
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True

vllm serve your_model_path \
    --served-model-name qwen3-coder \
    --trust-remote-code \
    --max-num-seqs 100 \
    --max-model-len 40960 \
    --max-num-batched-tokens 16384 \
    --tensor-parallel-size 4 \
    --enable-expert-parallel \
    --quantization ascend \
    --distributed_executor_backend "mp" \
    --no-enable-prefix-caching \
    --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
    --additional-config '{"weight_nz_mode": 2}' \
    --gpu-memory-utilization 0.95 \
    --port 8000 \
    --speculative-config '{"method": "eagle3", "model": "your_eagle3_model_path", "num_speculative_tokens": 3}'
```

### 关键配置项说明(原文)

- `--enable-expert-parallel`:MoE 模型必开,跨 NPU 分布 experts。
- `--tensor-parallel-size 4`:张量并行度,与 4 张 NPU 对应。
- `--quantization ascend`:启用 Ascend W8A8 量化路径(若模型已是 W8A8)。
- `--distributed_executor_backend "mp"`:使用 multiprocessing 分布式执行器。
- `--no-enable-prefix-caching`:关闭前缀缓存(原文截断处提到"disabled by default as prefix c...",详细解释未完整呈现)。
- `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`:仅 decode 阶段使用 CUDAGraph。
- `--additional-config '{"weight_nz_mode": 2}'`:权重 NZ 布局模式 2(细节见 additional_config 文档)。
- `--gpu-memory-utilization 0.95`:显存利用率 95%。
- `--speculative-config '{...eagle3...}'`:启用 Eagle3 推测解码,`num_speculative_tokens: 3`。
- `--port 8000`:服务端口,原文提示需根据实际情况调整以避免冲突。
- 注释:`your_model_path` 与 `your_eagle3_model_path` 需替换为本地实际模型路径;`ASCEND_RT_VISIBLE_DEVICES` 需与分配的 NPU chip ID 一致(如 `0,1,2,3` 对应 4 卡)。

> 备注:原文 §5 后续内容(如多节点部署、精度/性能评估步骤)未在提供片段中给出,如有需要请参照文档后续章节或上文提到的四个评估指南链接。
