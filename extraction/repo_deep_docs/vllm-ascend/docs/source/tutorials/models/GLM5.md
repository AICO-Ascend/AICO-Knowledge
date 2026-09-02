# GLM-5 & GLM-5.1

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/GLM5.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/GLM5.md

# GLM-5 & GLM-5.1 部署指南深度解读

## 【定位】

本文档解决如何在 vllm-ascend 镜像上部署并运行 GLM-5 / GLM-5.1 (Mixture-of-Experts 架构) 大模型的问题,涵盖特性支持矩阵、模型权重准备、Docker/源码安装、A3 与 A2 系列的在线服务部署命令与环境变量配置。

## 【技术要点】

1. **模型版本与软件要求**: GLM-5 / GLM-5.1 自 `vllm-ascend:v0.17.0rc1` 起被支持,所有 v0.17.0rc1 及之后版本可稳定运行;`transformers` 库需升级至 **5.2.0 或以上**;推荐使用最新 RC 版或正式版以获得 PD 分离、MTP 等新特性。
2. **模型权重**: 提供 BF16 (GLM-5/5.1) 与量化版 (GLM-5/5.1-w4a8、GLM-5/5.1-w8a8) 6 个权重下载源,推荐下载至多节点共享目录 `/root/.cache/`。
3. **Docker 镜像差异**: A3 系列使用 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3` 镜像并暴露 `/dev/davinci0` ~ `/dev/davinci15` 共 16 张 NPU;A2 系列使用无后缀镜像并暴露 8 张 NPU (`davinci0` ~ `davinci7`)。两者均挂载 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`。
4. **核心推理参数 (A3 / w4a8)**: `--tensor-parallel-size 16`、`--enable-expert-parallel`、`--max-num-seqs 16`、`--max-model-len 200000`、`--max-num-batched-tokens 4096`、`--gpu-memory-utilization 0.95`、`--quantization ascend`。
5. **核心推理参数 (A3 / w8a8)**: 同样 `--tensor-parallel-size 16`,但 `--max-model-len 40960`,并在 `--additional-config` 中额外开启 `"enable_mlapo":true`。
6. **MoE 与推测解码专用配置**: 通用 `additional-config` 为 `{"multistream_overlap_shared_expert":true,"scheduler_config":{"enable_balance_scheduling":true}}`;speculative 解码使用 `"method":"deepseek_mtp"`、`num_speculative_tokens=3`、`enforce_eager=true`;编译配置 `"cudagraph_mode":"FULL_DECODE_ONLY"`。

## 【关键机制与数据】

- **(原文) 环境变量机制**: 部署命令统一设置 `HCCL_OP_EXPANSION_MODE="AIV"` (HCCL 算子扩展模式)、`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=1`、`HCCL_BUFFSIZE=200`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`,用以约束 CPU 线程绑定与 NPU 内存分配行为。
- **(原文) 并行策略**: `--data-parallel-size 1` 配合 `--tensor-parallel-size 16` (A3) 或 `8` (A2),并通过 `--enable-expert-parallel` 启用 MoE 专家并行,意味着 GLM-5 的专家权重被切分到所有 NPU 卡。
- **(原文) 调度与缓存机制**: `--enable-chunked-prefill` 启用分块预填充;`--enable-prefix-caching` 启用前缀 KV 缓存;`enable_balance_scheduling` 在调度层做负载均衡;`multistream_overlap_shared_expert` 通过多流重叠共享专家计算以提升吞吐。
- **(原文) 推测解码**: MTP (Multi-Token Prediction) 方法 `deepseek_mtp`,每次额外猜测 3 个 token,且 `enforce_eager=true` 强制使用 eager 模式。
- **(原文) 显存占用率**: `--gpu-memory-utilization 0.95`,允许 vLLM 占用 95% 的 NPU 显存用于 KV cache 与权重。
- **(原文) 硬件匹配**: w4a8/w8a8 量化模型在 **1 台 Atlas 800 A3 (64GB × 16)** 即可部署单节点;A2 系列文档在此原文截断,未给出完整命令。

## 【表格解读】

**原文无表格**

## 【公式解读】

**原文无公式**

## 【关联】

- **上游特性矩阵**: `../../user_guide/support_matrix/supported_models.md` 用于查询 GLM-5/5.1 的完整功能兼容性 (受特性矩阵约束)。
- **特性配置入口**: `../../user_guide/feature_guide/index.md` 提供各项特性 (如 expert parallel、chunked prefill、prefix caching) 的具体开关与文档索引。
- **推测解码细节**: `../../user_guide/feature_guide/speculative_decoding.md` 对应本文中 `deepseek_mtp` 方法的配置语义。
- **安装与多节点互联**: `../../getting_started/installation.md` (被引用两次) 用于源码或镜像安装的总入口;`../../getting_started/installation.md#installation-multi-node-interconnect` (被引用两次) 给出多节点 RDMA/HCCN 通信验证步骤,是第 3.2 节的依赖。
- **常见问题**: `../../faqs.md` (被引用三次) 是 A3 / A2 部署命令旁标注的 "Common Issues Tip" 目标。

## 【使用方法】

**原文涉及的启用方式与命令如下:**

- **Docker 启动 (A3)**:
  ```shell
  export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
  export NAME=vllm-ascend
  docker run --rm --name $NAME --net=host --shm-size=1g \
    --device /dev/davinci0 … --device /dev/davinci15 \
    --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
  ```
  共 16 个 `/dev/davinci*` 设备。

- **Docker 启动 (A2)**:
  ```shell
  export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
  docker run --rm --name vllm-ascend --shm-size=1g --net=host \
    --device /dev/davinci0 … --device /dev/davinci7 \
    --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi … -v /root/.cache:/root/.cache \
    -it $IMAGE bash
  ```
  共 8 个 `/dev/davinci*` 设备;桥接网络需手动暴露端口供多节点通信。

- **在线推理 (A3 w4a8, 1×Atlas 800 A3)**:
  ```shell
  # pip install transformers==5.2.0 --upgrade
  export HCCL_OP_EXPANSION_MODE="AIV"
  export OMP_PROC_BIND=false
  export OMP_NUM_THREADS=1
  export HCCL_BUFFSIZE=200
  export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True

  vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/GLM5-w4a8 \
    --host 0.0.0.0 --port 8077 \
    --data-parallel-size 1 --tensor-parallel-size 16 \
    --enable-expert-parallel --seed 1024 \
    --served-model-name glm-5 \
    --max-num-seqs 16 --max-model-len 200000 \
    --max-num-batched-tokens 4096 \
    --trust-remote-code --gpu-memory-utilization 0.95 \
    --quantization ascend \
    --enable-chunked-prefill --enable-prefix-caching \
    --additional-config '{"multistream_overlap_shared_expert":true,"scheduler_config":{"enable_balance_scheduling":true}}' \
    --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
    --speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp", "enforce_eager": true}'
  ```

- **在线推理 (A3 w8a8, 1×Atlas 800 A3)**:
  命令与 w4a8 基本一致,差异在三点:
  1. 模型路径换为 `GLM5-w8a8`;2. `--max-model-len 40960`;3. `--additional-config` 中额外追加 `"enable_mlapo":true`。

- **在线推理 (A2)**: 原文 `glm-5-w4a8` 命令于 `--served-model-name g` 处被截断,后续内容 (含 `--tensor-parallel-size 8` 等) 未给出,**原文未涉及**完整命令。

- **多节点部署前提**: 需在每节点完成 3.2 节的通信环境验证,并按 4.1 / 4.2 节在每个节点分别配置 Docker / 源码环境。
