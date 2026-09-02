# Cohere Transcribe

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Cohere-Transcribe.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Cohere-Transcribe.md

# Cohere Transcribe 文档深度解读

## 【定位】

本文档描述了 Cohere Transcribe 这一**自动语音识别 (ASR) 模型族**在 Ascend NPU 上的端到端部署流程,涵盖环境准备、单节点服务部署、功能验证与精度评估,旨在指导用户在 Atlas A2 产品上落地该 2B 参数 Conformer encoder-decoder 架构的多语种语音识别服务。

---

## 【技术要点】

1. **模型架构与规模**:基于 **2B 参数的 Conformer encoder-decoder 架构**,支持 **14 种语言**(英语、法语、德语、意大利语、西班牙语、葡萄牙语、希腊语、荷兰语、波兰语、中文普通话、日语、韩语、越南语、阿拉伯语)。

2. **两个已验证版本**:
   - `CohereLabs/cohere-transcribe-03-2026` — 基础多语种模型(14 语言)
   - `CohereLabs/cohere-transcribe-arabic-07-2026` — 阿拉伯语微调模型(在 Atlas A2 上测得 WER/RTFx)

3. **硬件部署条件**:**BF16 模型可在单张 Atlas A2 64 GB NPU 上部署**;当前版本适配 Atlas A2 推理产品,**Ascend 950DT 系列支持规划于下一阶段**。

4. **上游实现**:Cohere Transcribe 由上游 vLLM 通过 `cohere_asr` 模型实现提供支持,需使用与 vLLM 版本匹配的 vLLM-Ascend 镜像。

5. **关键运行时约束**:`--trust-remote-code`(模型仓库自带自定义建模代码)与 `--block-size 128`(模型必须以**至少 128** 的块大小服务)为强约束。

6. **额外依赖**:容器内需安装 `librosa`(使用自定义镜像时),模型权重目录在多节点部署时需为共享目录(如 `/root/.cache/`)。

---

## 【关键机制与数据】

**工作机制(原文)**:
- 服务通过 vLLM 的 `vllm serve` 命令启动,采用张量并行(`--tensor-parallel-size 1` 即单 NPU)、BF16 数据类型、Eager 模式(`--enforce-eager`)与 KV 块大小 128。
- 推理调用走 **OpenAI 兼容的 Chat Completions API**,通过 `audio_url` 字段传递音频。
- 离线变量 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1` 在本地已下载权重时推荐开启。
- 启动成功标志:日志出现 `Application startup complete`。

**性能/精度数据(原文)**:

| 评估场景 | 数据集 | 关键指标 |
|---|---|---|
| `cohere-transcribe-03-2026`(基础多语种) | 100 Common Voice Arabic 样本 | **WER 9.06%, CER 2.96%** |
| `cohere-transcribe-arabic-07-2026`(阿拉伯语微调) | CV18 Arabic 测试集(10,471 样本) | **WER 5.69%**(官方参考 5.82%) |
| 同上 | 100 Common Voice Arabic 样本(同上) | **WER 5.28%, CER 1.27%** |

WER 分布(CV18 Arabic, 07-2026):完美识别(WER=0)占 **28.0%**;WER<5% 占 **66.8%**;WER<10% 占 **77.5%**;WER<20% 占 **87.3%**。对比结论:07-2026 在阿拉伯语上显著优于 03-2026(WER 5.28% vs 9.06%, CER 1.27% vs 2.96%)。

> 注:文档第 8 节"Performance Evaluation"在原文中被截断(仅显示 "Measure ASR "),未提供 RTFx/吞吐等性能数据原文。

---

## 【表格解读】

### 表 1:已验证模型版本(原文逐字还原)

| Version | Description | Verified by |
| --- | --- | --- |
| `CohereLabs/cohere-transcribe-03-2026` | Base multilingual model (14 languages) | Colleague verification, results recorded in the internal evaluation report |
| `CohereLabs/cohere-transcribe-arabic-07-2026` | Arabic fine-tuned model | Internal evaluation report (WER / RTFx measured on Atlas A2 products) |

**解读**:该表给出文档覆盖的两个模型版本及其验证主体。`03-2026` 为 14 语种通用基础模型,由同事在统一基准上验证;`07-2026` 为针对阿拉伯语微调的版本,在 Atlas A2 上进行 WER/RTFx 测量。两者形成"通用基础版 vs. 阿拉伯语专项版"的对照基线。

### 表 2:03-2026 在 100 Common Voice Arabic 样本上的指标(原文逐字还原)

| Metric | Result (100 Common Voice Arabic samples) |
| --- | --- |
| WER | 9.06% |
| CER | 2.96% |

**解读**:作为阿拉伯语子集上的基线对照点,在与 07-2026 完全一致的 100 样本上,基础多语种模型取得 WER 9.06%、CER 2.96%,为后续微调版本对比提供锚点。

### 表 3:07-2026 在 CV18 Arabic(10,471 样本)上的 WER 分布(原文逐字还原)

| Metric | Result |
| --- | --- |
| WER = 0 (perfect recognition) | 2,931 / 10,471 (28.0%) |
| WER < 5% | 6,990 / 10,471 (66.8%) |
| WER < 10% | 8,116 / 10,471 (77.5%) |
| WER < 20% | 9,145 / 10,471 (87.3%) |

**解读**:在大规模 CV18 测试集上,模型在**近三分之一样本上达到完美识别**;约 **2/3** 样本 WER 低于 5%;**近 90%** 样本 WER 低于 20%。这一累积分布显示错误主要来自少数长尾样本(剩余约 12.7% 的样本 WER ≥ 20%)。

### 表 4:07-2026 在 100 Common Voice Arabic 样本上的指标(原文逐字还原)

| Metric | Result (100 Common Voice Arabic samples) |
| --- | --- |
| WER | 5.28% |
| CER | 1.27% |

**解读**:与表 2 同口径对比,07-2026 在 100 样本上 WER 从 9.06% 降至 5.28%(相对降幅 ~41.7%),CER 从 2.96% 降至 1.27%(相对降幅 ~57.1%),证明显著优势,**为阿拉伯语生产场景推荐使用 07-2026 版本**。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游模型支持矩阵** → [Supported Features List](../../user_guide/support_matrix/supported_models.md):用于查询 Cohere Transcribe 在 support matrix 中的当前发布状态。
- **特性配置参考** → [Feature Guide](../../user_guide/feature_guide/index.md):提供特性开关/配置项说明。
- **CANN 源码安装路径** → [Installation Guide](../../getting_started/installation.md#installation-existing-cann-install):在不使用 Docker 镜像、改为源码构建时引用。
- **故障排查入口** → [Public FAQs](../../faqs.md)(出现两次):服务于启动失败诊断及常见问题解答。
- **性能调优下游** → [Optimization and Tuning](../../developer_guide/performance_and_debug/optimization_and_tuning.md):虽然原文未直接引用该链接(被截断的第 8 节可能涉及),但作为 ASR 性能调优的常规下游文档,该链接属于 vLLM-Ascend 开发者指南,与本文档的"Performance Evaluation"主题对应。

---

## 【使用方法】

### 启用方式(原文已给出)

**1. 拉取并启动 Docker 镜像(Atlas A2)**
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}

docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --net host \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64 \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it -d $IMAGE bash
```
验证:`docker ps --filter name=vllm-ascend` 应显示 `Up`;`pip show vllm vllm-ascend` 应返回版本号。

**2. 自定义镜像中补装依赖**
```bash
pip install librosa
```

**3. 单节点在线部署(`vllm serve`)**
```shell
export ASCEND_RT_VISIBLE_DEVICES=0
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

vllm serve /data/llm-workspace/cohere-transcribe-03-2026 \
  --served-model-name cohere-transcribe \
  --trust-remote-code \
  --tensor-parallel-size 1 \
  --dtype bfloat16 \
  --enforce-eager \
  --block-size 128 \
  --host 0.0.0.0 \
  --port 8000
```
阿拉伯语版本仅需替换权重路径为 `/data/llm-workspace/cohere-transcribe-arabic-07-2026`。

### 关键配置项(原文)

| 参数 | 取值 | 作用 |
|---|---|---|
| `--trust-remote-code` | 必选 | 仓库包含自定义建模代码 |
| `--block-size` | **128**(至少) | 模型 KV 块大小下限 |
| `--tensor-parallel-size` | 1 | 单 NPU 部署,可按拓扑调大 |
| `--dtype` | bfloat16 | 匹配 Atlas A2 验证的 BF16 精度 |
| `--enforce-eager` | — | 关闭 CUDA graph,适配 eager 执行 |
| `--served-model-name` | cohere-transcribe | 客户端请求使用的模型名 |
| `--host / --port` | 0.0.0.0 / 8000 | 监听地址 |
| `HF_HUB_OFFLINE` / `TRANSFORMERS_OFFLINE` | 1 | 离线模式,本地权重已下载时推荐 |

### 功能验证调用(原文)
```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "cohere-transcribe",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "audio_url", "audio_url": {"url": "https://example.com/your_audio.wav"}}
                ]
            }
        ]
    }'
```
预期:HTTP 200,`choices` 字段返回转写文本。

### 源码安装方式(原文)
按 [Installation Guide](../../getting_started/installation.md#installation-existing-cann-install) 流程构建;完成后用 `pip show vllm-ascend` 校验。

### 故障诊断
启动失败请参阅 [Public FAQs](../../faqs.md)。**性能基准测试命令**(第 8 节)原文未涉及,文档在此处被截断。
