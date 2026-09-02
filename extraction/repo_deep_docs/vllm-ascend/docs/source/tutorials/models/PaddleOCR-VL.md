# PaddleOCR-VL

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/PaddleOCR-VL.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/PaddleOCR-VL.md

# PaddleOCR-VL 部署文档深度解读

## 【定位】

这篇文档解决 **如何在 vLLM-Ascend 框架上完成 PaddleOCR-VL 模型的完整部署与功能验证** 问题,涵盖环境准备、单节点部署 (Docker 镜像与源码两种安装路径)、启动参数配置以及离线推理与 PP-DocLayoutV2 联合推理的特殊部署模式,目标用户是需要快速完成该 SOTA 文档解析 VLM 模型在 Ascend NPU 上落地的工程师。

---

## 【技术要点】

1. **模型架构与定位**: PaddleOCR-VL 的核心组件是 `PaddleOCR-VL-0.9B`,集成 **NaViT 风格动态分辨率视觉编码器 (NaViT-style dynamic resolution visual encoder)** 与 **ERNIE-4.5-0.3B 语言模型**,实现精准的元素识别 (document parsing),属"compact yet powerful"的小型 VLM。
2. **版本基线**: 文档基于 **vLLM-Ascend v0.21.0rc1** 验证与撰写,推荐使用该版本或更新的官方版本部署。
3. **模型权重来源**: `PaddleOCR-VL-0.9B` 来自 ModelScope (`PaddlePaddle/PaddleOCR-VL`),推荐设置 `VLLM_USE_MODELSCOPE=True` 自动加载;若本地已有权重需修改 `MODEL_PATH`。
4. **部署形态**: 目前仅支持 **单节点单卡 (single-node single-card)** 在线部署,Prefill 与 Decode 在同一节点内完成;**多节点 PD 分离部署明确标注"Not supported yet"**。
5. **硬件平台分支**: 文档给出两套独立的 `docker run` / `vllm serve` 脚本——`A2 series`(如 Atlas 800 A2 / 910B) 与 `Atlas 300I DUO (310P)`;Atlas 300I DUO 仅支持 `float16`,且 `--compilation-config` 需 **CANN >= 9.0.0**,否则必须回退到 `--enforce-eager` 走 eager 模式。
6. **联合推理 (Offline Inference)**: 通过在 **独立虚拟环境** 中安装 PaddlePaddle 框架,调用 `PP-DocLayoutV2` 配合 PaddleOCR-VL-0.9B 做版面分析,以贴合 PaddlePaddle 官方示例的能力。

---

## 【关键机制与数据】

- **数据流 (Single-Node Online)**:
  原文: "Single-node deployment completes both Prefill and Decode within the same node." → Prefill 阶段 (视觉/文本 prompt 编码) 与 Decode 阶段 (token 自回归生成) 都在同一 NPU 卡上串行/交替执行,无跨节点拆分。
- **多模态处理器缓存**:
  原文: `--mm-processor-cache-gb 0` → 设置为 `0` 即 **完全禁用 multimodal processor cache**,意味着每次请求都会重新执行图像预处理 (动态分辨率 NaViT 编码),换得更大的可用显存。
- **前缀缓存开关**:
  原文: `--no-enable-prefix-caching` → 默认关闭 prefix caching;若要开启,删除该参数即可,提示文档解析类请求间 prefix 复用率通常不高。
- **编译图模式**:
  原文: `--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'` → **仅对 Decode 阶段做 CUDAGraph 全图捕获编译**,Prefill 走动态 shape 不进 graph,以平衡首 token 时延与稳态吞吐。
- **CPU 亲和性绑定**:
  原文: `--additional_config '{"enable_cpu_binding":true}'` → 启用 CPU 绑定,改善 host 端数据预处理与 NPU 计算的并行度。
- **NPU 显存分配**:
  原文: `PYTORCH_NPU_ALLOC_CONF="expandable_segments:True"` → 启用可扩展段分配,降低显存碎片 (对长 context + 图像 token 场景尤其重要)。
- **任务队列与 CPU 亲和性**:
  原文: A2 脚本额外设置 `TASK_QUEUE_ENABLE=1` 与 `CPU_AFFINITY_CONF=1` → 启用任务队列与 CPU 亲和性配置,共同服务于上述 `enable_cpu_binding`。
- **批处理上界 (A2)**:
  原文: `--max-num-batched-tokens 16384` → 单次 forward 的最大 batched token 数 16384,作为吞吐调优旋钮。
- **最大上下文长度 (Atlas 300I DUO)**:
  原文: `--max_model_len 16384` → 单请求输入+输出总长上限 16384 tokens。
- **dtype 限制 (Atlas 300I DUO)**:
  原文: "On Atlas 300I DUO: Only `float16` dtype is supported." → 该平台不支持 bf16/fp32 的指定,必须显式 `--dtype float16`。
- **设备挂载清单**: 两个 docker run 都将 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 全部挂入,并 bind mount `/usr/local/dcmi`、`hccn_tool`、`npu-smi`、`Ascend/driver/lib64`、`Ascend/driver/version.info`、`/etc/ascend_install.info` 以及 `/root/.cache`,后者用于 ModelScope 权重缓存复用。
- **CANN 镜像 (PaddlePaddle 离线路径)**:
  原文: `docker pull ccr-2vdh3abv-pub.cnc.bj.baidubce.com/device/paddle-npu:cann800-ubuntu20-npu-910b-base-aarch64-gcc84` → A2 系列需要拉取 CANN 8.0.0 + Ubuntu 20 + NPU 910B (aarch64, gcc 8.4) 的 PaddlePaddle 兼容镜像;容器启动参数含 `--privileged --network=host --shm-size=128G`,与 vLLM 容器配置形成对照。
- **性能数据**: **原文未提供** 任何 TPS / 延迟 / 显存占用 / 准确率数字。
- **多节点 PD 分离数据**: **原文未涉及** 任何性能或带宽指标,只标注 "Not supported yet"。

---

## 【表格解读】

**原文无表格** (文档以参数化启动脚本 + 环境变量清单 + 两条平行的 docker/vllm 命令块呈现,没有 markdown 表格)。

---

## 【公式解读】

**原文无公式** (整篇文档未出现 LaTeX、伪代码公式或数学表达式,核心都是 shell 命令与参数键值对)。

---

## 【关联】

| 引用锚点 | 路径 | 与本文的关系 |
|---|---|---|
| Supported Features List | `../../user_guide/support_matrix/supported_models.md` | 文档第 2 节显式要求读者跳转此处,获取 **PaddleOCR-VL 在 vLLM-Ascend 上支持的能力矩阵** (哪些 feature flag / 算子 / 量化方案对该模型生效),是模型级支持情况的上游权威表 |
| Feature Guide | `../../user_guide/feature_guide/index.md` | 第 2 节引导读者到此处获取各 feature 的 **配置说明**,意味着本文 `vllm serve` 命令中的 `--compilation-config`、`--additional_config` 等键值对的具体语义需要回查该 feature guide |
| using docker | `../../getting_started/installation.md#installation-prebuilt-image` | 第 4.1 节镜像安装方式 (`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`) 来自该章节,本文是该 prebuilt image 的 **具体模型落地示例** |
| installation (source) | `../../getting_started/installation.md` | 第 4.2 节源码安装 `vllm-ascend` 直接链接到此,是 docker 之外的替代入口 |
| Public FAQs | `../../faqs.md` | 启动问题排错入口,本文以 "Common Issues Tip" 形式显式指向该 FAQ 集合 (文末链表中出现两次,说明其作为公共排错中枢被反复引用) |
| optimization_and_tuning | `../../developer_guide/performance_and_debug/optimization_and_tuning.md` | 出现在内部链接清单中,应作为本文 `--max-num-batched-tokens`、`--mm-processor-cache-gb`、CPU 绑定等 **调优旋钮的详细说明出处** |
| feature_matrix | `../../user_guide/support_matrix/feature_matrix.md` | 出现在内部链接清单中,与 `supported_models.md` 配合,提供 **feature × model** 的二维兼容性视图 |

整体链路:**安装入口** (`installation.md`) → **镜像/环境** → **本文 (具体模型部署脚本)** → **能力验证** (`supported_models.md` + `feature_matrix.md`) → **参数调优** (`optimization_and_tuning.md`) → **故障排查** (`faqs.md`)。

---

## 【使用方法】

### 一、Docker 镜像安装 (A2 系列 — 例)
原文:
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --net=host \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
```
镜像标签:`{{ vllm_ascend_version }}` (与文档基线 `v0.21.0rc1` 对齐);Atlas 300I DUO 使用同结构但带 `-310p` 后缀的镜像。

### 二、源码安装
原文: "Install `vllm-ascend` from source, refer to [installation](../../getting_started/installation.md)." → 即按 `installation.md` 通用流程编译/安装 wheel。

### 三、单节点在线服务启动脚本 (`deploy.sh`)

**A2 series**:
```bash
#!/bin/sh
export VLLM_USE_MODELSCOPE=True
export MODEL_PATH="PaddlePaddle/PaddleOCR-VL"
export TASK_QUEUE_ENABLE=1
export CPU_AFFINITY_CONF=1
export PYTORCH_NPU_ALLOC_CONF="expandable_segments:True"

vllm serve ${MODEL_PATH} \
          --max-num-batched-tokens 16384 \
          --served-model-name PaddleOCR-VL-0.9B \
          --trust-remote-code \
          --no-enable-prefix-caching \
          --mm-processor-cache-gb 0 \
          --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' \
          --additional_config '{"enable_cpu_binding":true}' \
          --port 8000
```

**Atlas 300I DUO**:
```bash
#!/bin/sh
export VLLM_USE_MODELSCOPE=True
export MODEL_PATH="PaddlePaddle/PaddleOCR-VL"
export TASK_QUEUE_ENABLE=1
export PYTORCH_NPU_ALLOC_CONF="expandable_segments:True"

vllm serve ${MODEL_PATH} \
          --max_model_len 16384 \
          --served-model-name PaddleOCR-VL-0.9B \
          --trust-remote-code \
          --no-enable-prefix-caching \
          --mm-processor-cache-gb 0 \
          --dtype float16 \
          --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' \
          --additional_config '{"enable_cpu_binding":true}' \
          --port 8000
```

### 四、关键配置项速查 (原文给出的)
- `--max-num-batched-tokens 16384` (A2) / `--max_model_len 16384` (300I DUO):吞吐 / 上下文上限
- `--no-enable-prefix-caching`:关闭 prefix caching;**开启方式为删除此参数**
- `--mm-processor-cache-gb 0`:禁用多模态处理器缓存
- `--dtype float16`:**仅 Atlas 300I DUO 强制要求**
- `--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`:Decode 阶段全图编译;**CANN < 9.0.0 时改用 `--enforce-eager`**
- `--additional_config '{"enable_cpu_binding":true}'`:CPU 绑定开关
- `--port 8000`:OpenAI 兼容服务端口

### 五、PaddlePaddle 联合推理 (PP-DocLayoutV2) — A2 系列
原文 (节选):
```bash
docker pull ccr-2vdh3abv-pub.cnc.bj.baidubce.com/device/paddle-npu:cann800-ubuntu20-npu-910b-base-aarch64-gcc84
```
容器启动:
```bash
docker run -it --name paddle-npu-dev -v $(pwd):/work \
    --privileged --network=host --shm-size=128G -w=/work \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/dcmi:/
```
该段原文在仓库内被截断 (后续步骤未在提供文本中出现),**原文未涉及** PP-DocLayoutV2 的具体推理代码与 PaddleOCR-VL HTTP 调用细节,但已明确要求**在独立虚拟环境中**运行 PP-DocLayoutV2 以避免与 vLLM 依赖冲突。

### 六、多节点 PD 分离部署
原文: **"Not supported yet."** → 当前不可用,无需配置。
