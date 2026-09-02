# LLaVA-OneVision-Qwen2-0.5B-OV

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/LLaVA-OneVision-Qwen2-0.5B-OV.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/LLaVA-OneVision-Qwen2-0.5B-OV.md

# 深度解读：LLaVA-OneVision-Qwen2-0.5B-OV on vLLM Ascend

---

## 【定位】

这篇文档描述如何在 vLLM Ascend 上对 `llava-hf/llava-onevision-qwen2-0.5b-ov-hf` 这一基于 Qwen2 的紧凑型多模态模型进行端到端验证，涵盖环境准备、单 NPU 部署、功能（纯文本 + 图像理解）验证以及仓库内置精度基线对齐。

---

## 【技术要点】

1. **模型定位**：原文明确指出该模型为"compact multimodal model built on top of Qwen2"，同时支持 text-only generation、image understanding、multi-image reasoning 与 visual dialogue 四种能力。
2. **硬件要求**：经实测的单卡部署使用 **一块 Atlas A2 NPU**；Docker 启动命令中将 `--device /dev/davinci0` 绑定，即对应单 NPU 卡 0。
3. **权重缓存路径**：建议提前将模型权重缓存在 `/root/.cache` 下，并通过 `-v /root/.cache:/root/.cache` 挂载进容器，以缩短启动时间。
4. **服务启动参数**：`vllm serve` 使用 `--gpu-memory-utilization 0.8`、`--served-model-name LLaVA-OneVision-0.5B`、`--trust-remote-code`、`--host 0.0.0.0`、`--port 8000`。
5. **多 NPU / PD 分离**：原文明确说明"Single-NPU deployment is recommended for this 0.5B model"，且 Prefill-Decode Disaggregation "Not supported yet"。
6. **推理接口**：基于 OpenAI 兼容 API，端点为 `/v1/models`（模型列举）与 `/v1/chat/completions`（对话补全），请求载荷使用多模态消息结构（`type: text` + `type: image_url` 列表）。

---

## 【关键机制与数据】

- **数据流（原文视角）**：模型权重 → `/root/.cache` 缓存 → vLLM 容器 → `vllm serve` 拉起 OpenAI 兼容服务 → 用户通过 `curl` 调用 `/v1/chat/completions`，以 messages 数组形式提交 text + image_url 多模态 prompt，服务端回传 `choices[0].message.content`。
- **示例响应（原文）**：
  - 纯文本示例回复：`"Hello! How can I assist you today?"`
  - 图像理解示例回复：`"The image features a logo consisting of a stylized geometric figure and the text \"TONGYI\" and \"Qwen\"..."`
- **生成参数（原文）**：纯文本请求 `max_completion_tokens=16`，`temperature=0`；图像理解请求 `max_completion_tokens=64`，`temperature=0`。
- **测试图片（原文）**：`https://modelscope.oss-cn-beijing.aliyuncs.com/resource/qwen.png`。
- **精度基线数据（原文）**：`ceval-valid` 数据集，A2 平台，指标 `acc,none`，**value = 0.42**，配置文件位于 `tests/e2e/models/configs/llava-onevision-qwen2-0.5b-ov-hf.yaml`。
- **服务启动日志（原文）**：出现 `INFO: Started server process [8173]`、`Application startup complete.` 即代表启动成功。

---

## 【表格解读】

原文仅含一张精度基线表格，逐字还原如下：

| dataset | platform | metric | value |
| --- | --- | --- | --- |
| ceval-valid | A2 | acc,none | 0.42 |

**逐行解读**：
- **dataset = ceval-valid**：CEval 基准的验证集，是中文大模型常用学科知识评测集，原文未列出子集或样本量。
- **platform = A2**：表示在 Atlas A2 系列 NPU 上跑出的结果，对应前文单 NPU 部署形态。
- **metric = acc,none**：CEval 框架中的整体（none 聚合）准确率指标，原文未注明 few-shot 或 chain-of-thought 设定。
- **value = 0.42**：在该 NPU 平台上获得的整体准确率，作为仓库内置基线，用于回归对比；原文未给出 CPU/GPU 参考数值。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **Supported Models 矩阵**：原文链接到 `../../user_guide/support_matrix/supported_models.md`，用于查询该模型在 vLLM Ascend 上的官方能力矩阵（支持哪些 feature 组合、哪些 NPU 型号等），是判断部署可行性的入口。
- **Feature Guide**：`../../user_guide/feature_guide/index.md`，对应"Supported Features"小节中提到的具体功能开关/参数说明，与本文中 `--gpu-memory-utilization 0.8`、`--trust-remote-code` 等配置项存在参数语义上的映射。
- **Installation / Prebuilt Image**：`../../getting_started/installation.md#installation-prebuilt-image` 是"Environment Preparation → Installation"小节的来源，文中 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}` 镜像占位符由该文档定义。
- **仓库内 e2e 配置文件**：`tests/e2e/models/configs/llava-onevision-qwen2-0.5b-ov-hf.yaml` 与"Accuracy Evaluation"小节直接对应，是端到端精度测试的下游入口。
- **上游权重源**：HuggingFace 上的 `llava-hf/llava-onevision-qwen2-0.5b-ov-hf` 仓库为权重来源，下游接入 vLLM Ascend 推理服务。

---

## 【使用方法】

**镜像启动（原文）**：
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
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
```

**服务启动（原文）**：
```bash
export MODEL_PATH="llava-hf/llava-onevision-qwen2-0.5b-ov-hf"
vllm serve "${MODEL_PATH}" \
    --host 0.0.0.0 \
    --port 8000 \
    --served-model-name LLaVA-OneVision-0.5B \
    --trust-remote-code \
    --gpu-memory-utilization 0.8
```

**功能验证（原文）**：
- 模型列举：`curl http://127.0.0.1:8000/v1/models`
- 纯文本对话：POST `/v1/chat/completions`，messages 仅含 `text` 类型，`max_completion_tokens=16`、`temperature=0`。
- 图像理解：POST `/v1/chat/completions`，messages 内含 `type: text` + `type: image_url`（`url` 指向 `https://modelscope.oss-cn-beijing.aliyuncs.com/resource/qwen.png`），`max_completion_tokens=64`、`temperature=0`。

**精度回归（原文）**：运行仓库内置配置 `tests/e2e/models/configs/llava-onevision-qwen2-0.5b-ov-hf.yaml`，对齐基线 `ceval-valid / A2 / acc,none = 0.42`。

**限制（原文）**：Multi-NPU 部署不被推荐；Prefill-Decode Disaggregation 当前不支持。
