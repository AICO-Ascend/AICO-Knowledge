# Kimi-K2-Thinking

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Kimi-K2-Thinking.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Kimi-K2-Thinking.md

# Kimi-K2-Thinking 部署指南深度解读

---

## 【定位】

本文档是 vLLM-Ascend v0.9.0rc1 及以上版本在 Atlas 800 A3 (64GB × 16) 节点上部署 MoonShot AI 大规模混合推理 MoE 模型 **Kimi-K2-Thinking** 的端到端验证指南,覆盖模型权重准备、Docker/源码安装、单节点在线服务部署、参数调优及 FAQ 等完整流程。

---

## 【技术要点】

1. **模型性质与硬件门槛**:Kimi-K2-Thinking 是由 Moonshot AI 开发的**混合推理架构 MoE 模型**,在 `bfloat16` 精度下至少需要 **1 台 Atlas 800 A3 (64GB × 16) 节点**,通过 HuggingFace 下载权重后建议放在共享目录 `/mnt/sfs_turbo/.cache/`。

2. **量化配置前置修改**:下载权重后需将原始 `config.json` 中 `quantization_config.config_groups.group_0.targets` 从 `["Linear"]` 改为 `["MoE"]`,才能以量化方式运行(原文以 JSON 代码块给出了修改后的结构)。

3. **安装双路径**:
   - **Docker 路径**:使用官方镜像 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`(注意 `-a3` 后缀),需 `--net=host`、暴露 16 个 `/dev/davinci[0-15]` 设备及 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,并挂载 DCMI、npu-smi、Ascend 驱动库、版本文件和共享缓存 `/mnt/sfs_turbo/.cache:/home/cache`,`--shm-size=1g`。
   - **源码路径**:`git clone --depth 1 --branch {{ vllm_version }}` 拉 vLLM,以 `VLLM_TARGET_DEVICE=empty pip install -e .` 安装;再拉 vllm-ascend 同样 `-e` 安装;最后用 `python -c "import vllm; import vllm_ascend; print('vllm and vllm_ascend import ok')"` 校验。

4. **单节点在线部署**:Prefill 与 Decode 在同一节点完成,适用中等并发在线推理;`tensor-parallel-size` 至少为 **16**(覆盖整节点 NPU)。

5. **关键性能/版本敏感参数(原文给出验证值)**:
   - `HCCL_BUFFSIZE=1024`(HCCL 通信缓冲)
   - `TASK_QUEUE_ENABLE=1`(Ascend 任务队列调度)
   - `OMP_PROC_BIND=false`(避免过严的 OpenMP CPU 绑定)
   - `HCCL_OP_EXPANSION_MODE=AIV`(启用 AIV 通信路径)
   - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`(减少 NPU 内存碎片)
   - `--max-model-len 8192`(单请求最大输入+输出 token)
   - 服务端口 `SERVER_PORT=8000`

6. **API 命名约定**:因启动脚本未设置 `--served-model-name`,API 请求必须使用 **`moonshotai/Kimi-K2-Thinking`** 作为模型名(除非显式覆盖),具体见第 10 章 FAQ。

---

## 【关键机制与数据】

- **数据流(原文)**:
  1. 从 HuggingFace 拉取 `moonshotai/Kimi-K2-Thinking` 权重(共 62 个分片,`model-00001-of-00062.safetensors` … `model-00062-of-00062.safetensors`)。
  2. 原地编辑 `config.json` 的 `quantization_config.config_groups.group_0.targets` → `["MoE"]`。
  3. 通过 Docker 镜像启动容器,把共享缓存挂载为 `/home/cache`,权重以 `/home/cache` 下路径传入。
  4. `vllm serve` 以 `tensor-parallel-size=16` 拉起模型,启动 OpenAI 兼容服务在 `8000` 端口。

- **量化原理(原文)**:把 quant target 从 `Linear` 改为 `MoE`,意味着仅对模型中的 **MoE 专家层** 进行量化(而非所有 `Linear` 层),以适配 Kimi-K2-Thinking 这类混合推理 MoE 的结构特点。

- **性能数据**:原文**未给出**具体的吞吐量、TTFT、TPOT 或 HCCL 稳定性数字,仅说明上述各项参数的"验证值",其他取值需另行验证。

- **设备健康验证(原文)**:容器内执行 `npu-smi info`,期望命令成功、列出全部 NPU 设备且状态健康。

---

## 【表格解读】

原文给出的关键表格为单节点部署的 **"Parameter and Environment Variable Descriptions"**(部署参数与说明),**逐字还原**如下(注:原文此表在 `--max-model-len` 行处被截断,后续行未给出):

| Parameter | Validated Value | Category | Description and Tuning Guidance |
| --- | --- | --- | --- |
| `moonshotai/Kimi-K2-Thinking` | model path | Model-specific | Specifies the model weight path passed to `vllm serve`. Because `--served-model-name` is not set in the script, API requests must use `moonshotai/Kimi-K2-Thinking` as the model name unless you add an explicit served-model-name override; see the FAQ in Chapter 10. |
| `HCCL_BUFFSIZE` | `1024` | Performance | Configures the HCCL communication buffer used by distributed NPU communication. This document validates `1024`; other values need separate throughput, TTFT, TPOT, and HCCL stability validation. |
| `TASK_QUEUE_ENABLE` | `1` | Version-sensitive / Performance | Enables task queue scheduling on Ascend. This document validates `1`; other values or version changes need startup and first-request validation. |
| `OMP_PROC_BIND` | `false` | Performance | Avoids overly strict OpenMP CPU binding. This document validates `false`; other values need separate CPU affinity, NPU health, and HCCL stability validation. |
| `HCCL_OP_EXPANSION_MODE` | `AIV` | Performance | Enables the AIV communication path. This document validates `AIV`; other values need separate throughput and latency validation. |
| `PYTORCH_NPU_ALLOC_CONF` | `expandable_segments:True` | Memory / Performance | Reduces NPU memory fragmentation. This document validates `expandable_segments:True`; other allocator settings need separate startup, memory, and runtime stability validation. |
| `SERVER_PORT` and `--port` | `8000` | Service | Sets the OpenAI-compatible service port. The documentation generator maps `DEFAULT_PORT` in the YAML to `8000`; update the curl examples if you change this value. |
| `--tensor-parallel-size` | `16` | Model-specific / Performance | Uses all 16 NPUs on one Atlas 800 A3 node. This document validates `tp16`; other topologies need separate memory, accuracy, and communication validation. |
| `--max-model-len` | `8192` | Performance | Sets the maximum input plus output tokens for one request and determines KV cache reservation. This *(原文此行被截断)* |

**逐行解读**:

- **`moonshotai/Kimi-K2-Thinking`(Model-specific)**:决定 `vllm serve` 加载的权重路径。脚本未设置 `--served-model-name`,因此 OpenAI 兼容 API 请求体里 `model` 字段必须用字符串 `moonshotai/Kimi-K2-Thinking` 才能命中;若想自定义,可在启动命令中显式追加 `--served-model-name`,具体可参考第 10 章 FAQ。
- **`HCCL_BUFFSIZE=1024`(Performance)**:控制 HCCL(昇腾集合通信库)在 NPU 间通信时使用的缓冲区大小。值越大通常对带宽吞吐越有利,但占用更多内存;本文档以 `1024` 为验证基线。
- **`TASK_QUEUE_ENABLE=1`(Version-sensitive/Performance)**:开启 Ascend 上的任务队列调度;属于版本敏感项,版本升级或取值变更都需重新做启动与首请求验证。
- **`OMP_PROC_BIND=false`(Performance)**:关闭 OpenMP 的紧绑核策略,避免过严的 CPU 亲和性导致 NPU 健康/HCCL 稳定性异常;验证值为 `false`。
- **`HCCL_OP_EXPANSION_MODE=AIV`(Performance)**:启用 AIV(Ascend 集合通信的 AIV 通路)通信路径,可改善集合通信性能;其他模式需另行吞吐与延迟验证。
- **`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`(Memory/Performance)**:让 PyTorch NPU 内存分配器使用可扩展段,降低显存碎片,改善长序列或长服务运行下的稳定性。
- **`SERVER_PORT` / `--port=8000`(Service)**:OpenAI 兼容服务监听端口;生成文档时把 YAML 中的 `DEFAULT_PORT` 映射为 `8000`,curl 示例默认按此端口编写。
- **`--tensor-parallel-size 16`(Model-specific/Performance)**:张量并行度 16,把整节点 16 张 NPU 全部用上;Kimi-K2-Thinking 的 `bfloat16` 部署被验证为 `tp16`,其他拓扑需要单独验证内存、精度与通信。
- **`--max-model-len 8192`(Performance)**:限制单请求"输入+输出"的 token 总长,并据此预留 KV cache;原文档在此行被截断,完整说明以原文档为准。

> 备注:除上述参数表外,文档中无其他表格(无性能对比表、配置项矩阵等)。

---

## 【公式解读】

**原文无公式**(既无 LaTeX 公式,也无伪代码公式)。涉及数值的地方(如 `HCCL_BUFFSIZE=1024`、`tensor-parallel-size=16`、`max-model-len=8192`)均以参数/环境变量形式给出,不属于数学公式。

---

## 【关联】

依据文末给出的内部链接与正文引用,可梳理出如下上下游/横向关系:

- **模型支持矩阵** → 文档 §2 指向 `../../user_guide/support_matrix/supported_models.md`,用于查看 Kimi-K2-Thinking 在 vllm-ascend 中的**已支持特性矩阵**;同时 `../../user_guide/support_matrix/feature_matrix.md` 提供整体功能矩阵视图。
- **特性配置指南** → 文档 §2 指向 `../../user_guide/feature_guide/index.md`,用于查阅各特性(如 Prefill/Decode、量化、调度等)的具体**配置方法**(本指南中的性能参数均依赖该文档)。
- **安装路径** → 文档 §4.1 指向 `../../getting_started/installation.md#installation-prebuilt-image`,指导如何选择和拉取**预构建 Docker 镜像**(`-a3` 后缀)。
- **源码安装** → 文档 §4.2 内联给出 `vllm` 与 `vllm-ascend` 的 git clone 与 `pip install -e .` 命令,与 `getting_started/installation.md` 中的源码安装部分互补。
- **FAQ** → 文档 §5.1 参数表脚注、§10 章节均显式引用 `../../faqs.md`(共两处引用),主要解答 `--served-model-name` 等运行时疑问。
- **功能/性能验证评估** → 文档 §1 介绍提到的"functional verification""accuracy evaluation""performance evaluation""performance tuning"分别对应以下指南:
  - **精度评测**:`../../developer_guide/evaluation/using_ais_bench.md`(使用 AISBench)、`../../developer_guide/evaluation/using_lm_eval.md`(使用 LM Evaluation Harness)。
  - **性能调优**:`../../developer_guide/performance_and_debug/optimization_and_tuning.md`(本指南中的 `HCCL_BUFFSIZE`、`TASK_QUEUE_ENABLE`、`PYTORCH_NPU_ALLOC_CONF` 等均为其下钻主题)。

简言之,本指南是"模型维度"的入口文档,向上接 **支持矩阵/特性矩阵**,向左接 **特性配置/安装**,向下接 **评测与调优** 三大开发者子域。

---

## 【使用方法】

原文给出的可执行启用/配置方式如下:

1. **下载权重**(HuggingFace,`bfloat16`):
   ```bash
   # https://huggingface.co/moonshotai/Kimi-K2-Thinking
   ```
   推荐存放至 `/mnt/sfs_turbo/.cache/`。

2. **修改 `config.json`**(启用 MoE 量化):
   ```json
   {
     "quantization_config": {
       "config_groups": {
         "group_0": {
           "targets": ["MoE"]
         }
       }
     }
   }
   ```

3. **Docker 启动**(完整命令已在原文给出,核心点):
   ```bash
   export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
   docker run --rm --name $NAME --net=host --shm-size=1g \
     --device /dev/davinci0 … --device /dev/davinci15 \
     --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
     -v /usr/local/dcmi:/usr/local/dcmi \
     -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
     -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
     -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
     -v /etc/ascend_install.info:/etc/ascend_install.info \
     -v /mnt/sfs_turbo/.cache:/home/cache \
     -it $IMAGE bash
   ```

4. **容器与设备校验**:
   ```bash
   # 主机上查看容器状态
   docker ps --filter name=vllm-ascend --format "table {{.Names}}\t{{.Status}}"
   # 容器内查看 NPU
   npu-smi info
   ```

5. **源码安装(替代路径)**:
   ```bash
   git clone --depth 1 --branch {{ vllm_version }} https://github.com/vllm-project/vllm
   cd vllm && VLLM_TARGET_DEVICE=empty pip install -e . && cd ..
   git clone --depth 1 --branch {{ vllm_ascend_version }} https://github.com/vllm-project/vllm-ascend.git
   cd vllm-ascend && pip install -e .
   python -c "import vllm; import vllm_ascend; print('vllm and vllm_ascend import ok')"
   ```

6. **单节点在线部署(原文以 `model-code` 块引用 `tests/e2e/nightly/single_node/models/configs/Kimi-K2-Thinking.yaml` 生成启动脚本)**:
   - 模型路径:`moonshotai/Kimi-K2-Thinking`
   - 张量并行:`--tensor-parallel-size 16`
   - 上下文长度:`--max-model-len 8192`
   - 服务端口:`--port 8000`
   - 关键环境变量:`HCCL_BUFFSIZE=1024`、`TASK_QUEUE_ENABLE=1`、`OMP_PROC_BIND=false`、`HCCL_OP_EXPANSION_MODE=AIV`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`
   - API 调用模型名:必须使用 `moonshotai/Kimi-K2-Thinking`(因未设置 `--served-model-name`)

7. **版本要求**:仅在 **vLLM-Ascend v0.9.0rc1 及以上**稳定支持,建议搭配最新 RC 或稳定版使用。

> 文档关于**多节点部署、accuracy/performance 评估具体命令、进一步性能调优的具体步骤**等内容在原文此处已被截断,以原文后续章节及 `developer_guide/evaluation/*`、`developer_guide/performance_and_debug/optimization_and_tuning.md` 为准。
