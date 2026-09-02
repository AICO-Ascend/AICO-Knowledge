# DeepSeek-V4-Flash

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/DeepSeek-V4-Flash.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-V4-Flash.md

# DeepSeek-V4-Flash 部署文档深度解读

---

## 【定位】

本篇文档是 **vllm-ascend 上 DeepSeek-V4-Flash 模型的端到端部署与验证指南**, 围绕该轻量级 MoE 模型的特性支持、软硬件前提、镜像/源码安装、单节点/多节点在线服务部署等环节给出可复现的步骤。文档聚焦"如何把 DeepSeek-V4-Flash 跑起来并完成精度/性能验证", 是一篇面向运维 + 算法工程师的工程落地手册。

---

## 【技术要点】

1. **模型谱系与架构升级 (相对 DeepSeek-V3)**
   - 引入 **Manifold-Constrained Hyper-Connections (mHC)** 强化残差连接
   - 采用 **混合注意力架构**: 包含 `Compress-4-Attention` 与 `Compress-128-Attention`, 以提升长上下文效率
   - MoE 部分沿用 **DeepSeekMoE**, 仅做小幅调整

2. **DeepSeek-V4-Flash 定位**
   - DeepSeek-V4 家族的轻量化版本, 面向**高吞吐、低延迟**推理服务场景

3. **两份权重 / 两个变体**
   - `DeepSeek-V4-Flash-w8a8-mtp` (量化版): 来自 ModelScope 链接 `Eco-Tech/DeepSeek-V4-Flash-w8a8-mtp`
   - `DeepSeek-V4-Flash-0731-w8a8` (**DSpark**): 2026 年 7 月 31 日 DeepSeek 发布的新权重, 链接 `Eco-Tech/DeepSeek-V4-Flash-0731-w8a8`

4. **硬件最低要求**
   - 1 × Atlas 800 **A3** (128GB × 8) 节点, 或 1 × Atlas 800 **A2** (64GB × 8) 节点

5. **DSpark 兼容性门**
   - 在 vLLM Ascend **v0.25.0** 及以上同时支持 A2 / A3
   - 对应专用镜像:
     - A2: `quay.io/ascend/vllm-ascend:DeepSeekV4-flash-0731`
     - A3: `quay.io/ascend/vllm-ascend:DeepSeekV4-flash-0731-a3`

6. **推理参数关键取值** (A2 主线脚本为例)
   - `--max-model-len 133120`, `--max-num-batched-tokens 8192`
   - `--gpu-memory-utilization 0.9`, `--max-num-seqs 32`
   - `--tensor-parallel-size 8`, `--enable-expert-parallel`, `--data-parallel-size 1`
   - `--quantization ascend`, `--block-size 128`
   - 推测解码走 **MTP (Multi-Token Prediction)**: `--speculative-config '{"num_speculative_tokens": 1,"method": "mtp","enforce_eager": true}'`
   - `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`
   - `--additional-config` 内开启 `enable_npugraph_ex`, `enable_cpu_binding`, `enable_dsa_cp`, `multistream_overlap_shared_expert`

7. **DSpark 推理差异化参数**
   - `--max-model-len 800000` (相比主线 133120 大幅放大, 体现更激进的超长上下文支持)
   - 增加了 `--no-disable-hybrid-kv-cache-manager` 开关
   - 加载路径变为 `/root/.cache/modelscope/hub/models/UploadWeight/DeepSeek-V4-Flash-DSpark-w4a8-test`
   - 其余并行/专家并行配置与主线一致 (TP=8, EP 开启)

8. **NPU/HCCL 关键环境变量**
   - `OMP_PROC_BIND=false` (DSpark 脚本里不再显式设置), `OMP_NUM_THREADS=10`
   - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`
   - `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2` (启用 jemalloc)
   - `HCCL_BUFFSIZE=1024`, `TASK_QUEUE_ENABLE=1`, `HCCL_OP_EXPANSION_MODE="AIV"` (集合通信走 AI Vector 核)

9. **解析器三件套** (DeepSeek-V4 专属)
   - `--tokenizer-mode deepseek_v4`
   - `--tool-call-parser deepseek_v4 --enable-auto-tool-choice`
   - `--reasoning-parser deepseek_v4`

---

## 【关键机制与数据】

- **mHC (Manifold-Constrained Hyper-Connections)** —— 原文: "The Manifold-Constrained Hyper-Connections (mHC) to strengthen conventional residual connections." 即在传统残差连接基础上引入流形约束, 强化跨层信息通路, 是 DeepSeek-V4 相对 V3 的首要结构升级。

- **Compress-4-Attention / Compress-128-Attention** —— 原文: "A hybrid attention architecture, which greatly improves long-context efficiency through Compress-4-Attention and Compress-128-Attention." 两种压缩注意力机制共存, 用于降低长序列注意力开销, 是 V4 标榜"长上下文高效"的核心。

- **DeepSeekMoE 沿用** —— 原文: "For the Mixture-of-Experts (MoE) components, it still adopts the DeepSeekMoE architecture, with only minor adjustments." 专家路由结构基本复用 V3。

- **MTP 推测解码** —— 原文通过 `--speculative-config '{"num_speculative_tokens": 1, "method": "mtp", "enforce_eager": true}'` 启用 Multi-Token Prediction 推测解码, 以单步草拟 token 形式压低解码时延, 与 `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'` 配套, 仅在 decode 阶段走 CUDA Graph。

- **`enable_multithread_load`** —— 原文: `--model-loader-extra-config='{"enable_multithread_load": true, "num_threads": 128}'`, 权重加载开启 128 线程并行, 加速大模型加载。

- **`multistream_overlap_shared_expert`** —— 在 `--additional-config` 中启用, 暗示 DeepSeekMoE 的共享专家计算与主流可做多流并行, 提升吞吐。

- **DSpark 长上下文** —— DSpark 脚本将 `--max-model-len` 从主线的 133120 提升到 800000, 表明该变体面向**超长上下文**场景 (对应 Compress-N 系列注意力机制)。

> 注: 文档未给出具体的吞吐量 (TPS)、TTFT、显存峰值等性能数字, 故此处不杜撰量化性能数据。

---

## 【表格解读】

**原文无表格。**

文档中存在的是两块等价的"代码围栏" (A3 / A2 的 `docker run` 命令, 以及 A2 / A2-DSpark 的 `vllm serve` 脚本), 这些是命令块而非 markdown 表格, 故按"无表格"处理。

---

## 【公式解读】

**原文无公式。**

整篇文档未出现 LaTeX 公式或数学伪代码, 仅以命令行参数与环境变量表达配置。

---

## 【关联】

根据文档正文与文末内部链接, 涉及以下上下游关系:

1. **支持矩阵 & 特性配置**
   - `../../user_guide/support_matrix/supported_models.md` —— 提供 DeepSeek-V4-Flash 在 vLLM Ascend 上的特性支持矩阵
   - `../../user_guide/feature_guide/index.md` —— 各功能特性的配置详解 (如 EP、MTP、量化、cudagraph 等)

2. **安装与多节点互联**
   - `../../getting_started/installation.md` —— `vllm-ascend` 从源码安装总入口
   - `../../getting_started/installation.md#installation-prebuilt-image` —— 预构建 Docker 镜像使用方式 (本文档 `docker run` 即从此处展开)
   - `../../getting_started/installation.md#installation-multi-node-interconnect` —— 多节点通信验证步骤, 仅在多节点部署时引用

3. **FAQ**
   - `../../faqs.md` —— 通用 FAQ, 文档未在正文展开但提供兜底入口

4. **PD 分离 / Mooncake 多节点部署 (被多次引用)**
   - `../features/pd_disaggregation_mooncake_multi_node.md` —— 在内部链接列表中出现 **4 次**, 说明本指南与 Mooncake 多节点 PD 分离部署特性深度耦合。该特性通常在 `5.x 多节点部署` / `6.x 精度与性能评估` 章节前后调用, 用于在多节点之间拆 Prefill / Decode。结合本文硬件要求 (A3/A2 各 8 卡) 和 Mooncake 传输 KV Cache 的典型场景, 推测 DeepSeek-V4-Flash 的多节点方案依赖此特性进行上下文缓存跨机共享。

5. **同一仓库结构**
   - 本文位于 `docs/source/tutorials/models/`, 与同目录其他模型 (如 DeepSeek-V3, Qwen 系列) 共享相同的 "Prerequisites → Installation → Online Service Deployment" 章节骨架, 说明 vllm-ascend 教程遵循统一的模型部署模板。

---

## 【使用方法】

以下命令与配置项均来自原文, 完整保留参数。

### (1) 下载权重 (任选其一)

```text
# 主线 w8a8 + MTP
https://www.modelscope.cn/models/Eco-Tech/DeepSeek-V4-Flash-w8a8-mtp

# DSpark (0731)
https://www.modelscope.cn/models/Eco-Tech/DeepSeek-V4-Flash-0731-w8a8
```

建议落地路径: `/root/.cache/modelscope/hub/models/vllm-ascend/...`

### (2) Docker 镜像启动 (每个节点)

A3 系列:

```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
docker run --rm \
    --name vllm-ascend --shm-size=512g --net=host --privileged=true \
    --device /dev/davinci0 ... /dev/davinci15 \
    --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /etc/hccn.conf:/etc/hccn.conf \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
```

A2 系列:

```bash
# DeepSeek-V4-Flash 主线
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
# DeepSeek-V4-Flash-DSpark
export IMAGE=quay.io/ascend/vllm-ascend:nightly-main
# 其余 docker run 形参与 A3 一致, 仅 davinci0..7 (8 张卡) 而非 16 张
```

验证容器: `docker ps`

### (3) 单节点在线推理 (A2 系列, 主线脚本, 节选关键项)

```shell
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=10
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD
export HCCL_BUFFSIZE=1024
export TASK_QUEUE_ENABLE=1
export HCCL_OP_EXPANSION_MODE="AIV"

vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/DeepSeek-V4-Flash-w8a8-mtp \
    --max-model-len 133120 \
    --max-num-batched-tokens 8192 \
    --served-model-name dsv4 \
    --gpu-memory-utilization 0.9 \
    --max-num-seqs 32 \
    --data-parallel-size 1 \
    --tensor-parallel-size 8 \
    --enable-expert-parallel \
    --tokenizer-mode deepseek_v4 \
    --tool-call-parser deepseek_v4 \
    --enable-auto-tool-choice \
    --reasoning-parser deepseek_v4 \
    --no-enable-prefix-caching \
    --model-loader-extra-config='{"enable_multithread_load": true, "num_threads": 128}' \
    --quantization ascend \
    --port 8900 \
    --block-size 128 \
    --speculative-config '{"num_speculative_tokens": 1,"method": "mtp","enforce_eager": true}' \
    --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
    --additional-config '
    {"ascend_compilation_config":{
        "enable_npugraph_ex":true,
        "enable_static_kernel":false
        },
    "enable_cpu_binding": true,
    "enable_dsa_cp": true,
    "multistream_overlap_shared_expert": true}'
```

### (4) 单节点在线推理 (A2 + DSpark 脚本)

```shell
export OMP_NUM_THREADS=10
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD
export HCCL_BUFFSIZE=1024
export TASK_QUEUE_ENABLE=1
export HCCL_OP_EXPANSION_MODE=AIV

vllm serve /root/.cache/modelscope/hub/models/UploadWeight/DeepSeek-V4-Flash-DSpark-w4a8-test \
    --max-model-len 800000 \
    --max-num-batched-tokens 8192 \
    --served-model-name dsv4-dspark \
    --gpu-memory-utilization 0.9 \
    --max-num-seqs 32 \
    --data-parallel-size 1 \
    --tensor-parallel-size 8 \
    --enable-expert-parallel \
    --tokenizer-mode deepseek_v4 \
    --tool-call-parser deepseek_v4 \
    --enable-auto-tool-choice \
    --reasoning-parser deepseek_v4 \
    --no-disable-hybrid-kv-cache-manager \
    --model-loader-extra-config='{"enable_multithread_load": true, "num_thr    # ←原文此处被截断
```

### (5) 源码安装替代路径

如不使用 Docker, 按 `../../getting_started/installation.md` 从源码编译 `vllm-ascend`; 多节点时需在**每个节点**重复执行。

### (6) 多节点相关

原文未在本文给出多节点 `vllm serve` 完整脚本, 但通过内部链接 `../features/pd_disaggregation_mooncake_multi_node.md` 与 `../../getting_started/installation.md#installation-multi-node-interconnect` 指向 PD 分离 + Mooncake 传输 / 多节点互联验证章节。**多节点具体命令原文未涉及。**

### (7) 服务端口与客户端

- `--port 8900` (A2 主线), 服务名 `dsv4`; A2-DSpark 服务名 `dsv4-dspark`
- 客户端可用 OpenAI 兼容协议访问, 例如 `http://<node_ip>:8900/v1/chat/completions`, header `model: dsv4` (或 `dsv4-dspark`)

> **原文未涉及**: 多节点 `vllm serve` 完整脚本、精度验证命令行 (如 OpenCompass / AIME / GSM8K)、性能压测脚本 (如 vllm benchmark)、故障排查流程 —— 这些通常在文档后续 6、7 章给出, 但原文已截断, 故不臆造。
