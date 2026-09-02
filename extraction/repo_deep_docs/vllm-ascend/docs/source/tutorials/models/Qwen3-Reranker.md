# Qwen3-Reranker

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-Reranker.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Reranker.md

# Qwen3-Reranker 文档深度解读

## 【定位】

本篇文档是 vllm-ascend 仓库中针对 **Qwen3-Reranker 系列**模型（0.6B / 4B / 8B 三种规模）在华为 Ascend NPU 平台上运行的官方部署与验证指南，覆盖环境准备、Docker 安装、在线服务部署、接口调用与结果验证等环节，是该 reranker 模型在 vLLM Ascend 生态落地的端到端操作手册。

---

## 【技术要点】

1. **支持版本门槛**：原文明确"only 0.9.2rc1 and higher versions of vLLM Ascend support the model"，低于此版本无法运行该模型。
2. **模型族规格**：基于 Qwen3 密集基模型，提供 **0.6B、4B、8B** 三种尺寸的 reranker 模型，权重均托管在 ModelScope。
3. **架构重写机制**：通过 `--hf_overrides` 强制将 HuggingFace 配置覆盖为 `"architectures": ["Qwen3ForSequenceClassification"]`，并附带 `"classifier_from_token": ["no", "yes"]` 与 `"is_original_qwen3_reranker": true` 两个标志位，以兼容 reranker 权重结构。
4. **Runner 模式**：使用 `--runner pooling`，表明模型以池化（pooling）方式提供打分能力，而非自回归生成。
5. **平台差异化部署**：文档给出三种硬件形态——**A3 系列、A2 系列、Atlas 300I DUO**——分别对应不同的 Docker 镜像 tag（`-a3` 后缀、无后缀、`-310p` 后缀），其中 Atlas 300I DUO 额外引入 `--compilation-config` 与 `--additional-config` 以适配受限硬件流。
6. **上下文长度控制**：推荐显式设置 `--max-model-len 1024`；原文特别警告 Atlas 300I DUO 若自动解析出大上下文，分配 attention mask（复杂度 O(max_model_len²)）会触发 NPU OOM。

---

## 【关键机制与数据】

### 工作原理（基于原文推断）

- **Reranker 本质**：通过一个序列分类头（sequence classification head）给 `(query, document)` 对打分，分数越高代表文档越相关。
- **Prompt 模板机制**：原文给出的示例模板由三段拼接而成：
  - `prefix`：固定系统指令，要求模型以 `"yes"` / `"no"` 形式判断文档是否满足需求。
  - `query_template`：`<Instruct>: {instruction}\n<Query>: {query}`，注入任务指令与查询。
  - `document_template`：`<Document>: {doc}{suffix}`，其中 `suffix = "\nassistant\n<think>\n\n\n\n"` 强制模型在指定标签后给出 token 输出，对应 `classifier_from_token=["no","yes"]` 的取位逻辑。
- **分类 token 决定分数**：`classifier_from_token: ["no", "yes"]` 表明 reranker 通过读取模型在 `no` / `yes` 两个特殊 token 位置上的 logits（通常转化为概率 / softmax 分数）来得到相关性。

### 性能数据（原文唯一一组实测）

来自 §6 Functional Verification 的 Expected Result：

| 文档 | relevance_score |
|------|-----------------|
| "The capital of China is Beijing." | **0.9994981288909912** |
| "Gravity is a force that attracts two bodies…" | **0.00000506485957885161** |

配合 `"prompt_tokens": 193, "total_tokens": 193` 可知该次请求消耗 token 数极小（pooling 类服务不计 output tokens），打分结果呈强烈两极分化，体现 reranker 判别能力。

---

## 【表格解读】

**原文无表格**。

原文中的 `--hf_overrides`、`--compilation-config`、`--additional-config` 等参数以 JSON 字符串 / 代码块形式呈现，并未组织为 markdown 表格；Docker 启动命令同样以 fenced code block 形式给出，因此不存在需要逐字还原的表格。

如需人工整理，可根据 §5 内容还原为下表（仅作辅助理解，非原文内容）：

| 参数 | A3 / A2 series | Atlas 300I DUO | 含义 |
|------|----------------|----------------|------|
| `--runner` | `pooling` | `pooling` | 运行模式为池化打分 |
| `--hf_overrides` | `Qwen3ForSequenceClassification` | 同 | 覆盖模型架构 |
| `--compilation-config` | — | `cudagraph_capture_sizes:[1024,512]` | 受限硬件流下的图捕获尺寸 |
| `--additional-config` | — | `ascend_compilation_config.fuse_norm_quant:false` | 关闭融合以兼容 DUO |
| `--dtype` | — | `float16` | 数据精度 |
| `--max-model-len` | `1024` | `1024` | 保守上下文长度，避免 OOM |
| `--port` | `8000` | `8000` | 服务监听端口 |

---

## 【公式解读】

**原文无公式**。

文档未涉及任何数学表达式或伪代码算法；reranker 打分机制通过自然语言 + 模板字符串描述，没有给出如 $\text{score} = \frac{P(\text{yes})}{P(\text{yes}) + P(\text{no})}$ 之类的显式公式。

---

## 【关联】

依据文末及文中出现的内部链接：

- **[Supported Features List](../../user_guide/support_matrix/supported_models.md)**：用于确认 Qwen3-Reranker 在 vLLM Ascend 支持矩阵中具体开启的能力（量化、多模态、张量并行等），是部署前的必查表。
- **[Installation / using docker](../../getting_started/installation.md#installation-prebuilt-image)**：镜像选型、容器运行基础流程的权威入口；本文 §4.1 的三种 docker run 模板是其衍生。
- **[Installation](../../getting_started/installation.md)**：源码编译安装路径（pip / 从源码构建 vllm-ascend），对应本文 §4.2 Source Code Installation。
- **[Public FAQs](../../faqs.md)**：排错兜底，文中以 "Common Issues Tip" 形式显式指引，遇到部署异常时回溯到此文档。
- **vLLM 上游 examples/pooling/score**：文末指向 `https://github.com/vllm-project/vllm/tree/main/examples/pooling/score`，表明 reranker 服务遵循 vLLM 主干的 pooling scoring 接口规范，与其他 embedding / rerank 模型共享一套调用范式。

上下游关系：**ModelScope 权重 → vllm-ascend 容器（Docker/源码安装）→ vllm serve（pooling runner）→ OpenAI 兼容 rerank 接口（/v1/rerank）→ 用户业务调用方**。

---

## 【使用方法】

### 启用方式（Docker，三选一）

**A3 series**：
```shell
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --net=host \
    --privileged=true \
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

**A2 series**：镜像 tag 改为 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`（无 `-a3` 后缀），其余同上。

**Atlas 300I DUO**：镜像 tag 改为 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p`，其余同上。

容器启动后可执行 `docker ps` 验证。

### 启动 Rerank 服务

**A3 / A2 series**：
```shell
vllm serve Qwen/Qwen3-Reranker-0.6B \
    --served-model-name Qwen/Qwen3-Reranker-0.6B \
    --runner pooling \
    --hf_overrides '{"architectures": ["Qwen3ForSequenceClassification"],"classifier_from_token": ["no", "yes"],"is_original_qwen3_reranker": true}' \
    --port 8000 \
    --max-model-len 1024
```

**Atlas 300I DUO**（额外加编译/精度配置）：
```shell
vllm serve Qwen/Qwen3-Reranker-0.6B \
    --served-model-name Qwen/Qwen3-Reranker-0.6B \
    --runner pooling \
    --hf_overrides '{"architectures": ["Qwen3ForSequenceClassification"],"classifier_from_token": ["no", "yes"],"is_original_qwen3_reranker": true}' \
    --compilation-config '{"cudagraph_capture_sizes": [1024,512]}' \
    --additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}' \
    --dtype float16 \
    --port 8000 \
    --max-model-len 1024
```

### 功能验证调用

向 `http://127.0.0.1:8000/v1/rerank` POST 一个 JSON，包含 `query`（已按 `query_template` 格式化）与 `documents`（已按 `document_template` 格式化），服务端返回 HTTP 200 与 `relevance_score` 字段数组（详见 §6 Python 示例）。

> 注：原文 §7 Accuracy Evaluation 仅以 "Here are two accuracy evaluation methods." 一句话开头，未展开具体方案，故**精度评测的具体命令/脚本原文未涉及**。
