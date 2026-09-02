# Minitron-8B-Base

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Minitron-8B-Base.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Minitron-8B-Base.md

# Minitron-8B-Base 一体化深度解读

## 【定位】
这篇文档面向在 Ascend NPU 上通过 vllm-ascend 部署 NVIDIA Minitron-8B-Base 模型的使用者,系统性描述环境准备、单节点部署、功能性验证与 GSM8K 基准准确率评估的完整流程,作为该模型在昇腾平台上的端到端验证指南。

## 【技术要点】
- **模型与权重**: `Minitron-8B-Base` BF16 版本,源自 [ModelScope nv-community/Minitron-8B-Base](https://www.modelscope.cn/models/nv-community/Minitron-8B-Base);推荐存放路径 `/root/.cache/` 或 `/data/vllm-workspace/models/Minitron-8B-Base`。
- **硬件要求**: 1 张 Ascend 910B,搭配 1 × 64GB NPU。
- **运行镜像**: 官方 Docker 镜像 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`,需挂载 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 等设备及 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、Ascend driver lib64/version.info、`/etc/ascend_install.info`,挂载 `/root/.cache` 与 `/data/vllm-workspace/models` 并映射 `-p 8000:8000`。
- **启动推理服务**: `vllm serve "nv-community/Minitron-8B-Base"` 关键参数 `--served-model-name minitron-8b-base --tensor-parallel-size 1 --max-model-len 4096 --gpu-memory-utilization 0.9 --enforce-eager --port 8000`。
- **功能验证**: 通过 `curl http://localhost:8000/v1/completions` 发送 prompt(火车速度示例题),`max_tokens=64`、`temperature=1.0`。
- **准确率评估**: GSM8K test split,1000 样本,5-shot;`apply_chat_template=False`、`fewshot_as_multiturn=False`;`exact_match,strict-match=0.5436`、`exact_match,flexible-extract=0.5451`。

## 【关键机制与数据】
- **工作原理(原文)**: Minitron-8B-Base 通过 vllm-ascend 在 Ascend NPU 上做在线推理服务,核心流程为「加载权重 → 启动 vLLM OpenAI 兼容服务 → 通过 /v1/completions 端点完成生成式验证 → GSM8K 5-shot 评测」。
- **数据流(原文)**: 模型权重 → vllm-ascend 推理引擎 → 暴露在 8000 端口的 HTTP 服务 → 客户端 curl/评测脚本访问 → 生成结果用于严格/宽松格式匹配。
- **性能数据(原文)**: 文档未给出具体吞吐量、时延、长上下文推理或显存利用率数字,仅在 "Remarks" 中声明 "Actual throughput and latency depend on hardware resources, prompt length, output length, concurrency, and runtime configuration.",并建议后续补充 request latency、并发吞吐、长上下文、显存利用率、连续服务稳定性等基准。
- **准确率数据(原文)**: GSM8K / test,Total Samples=1000;`exact_match,strict-match=0.5436`;`exact_match,flexible-extract=0.5451`。两种评估口径只差 0.0015,说明模型输出在数字答案层面稳定性较高,主要差异来自最终数值周边格式(标点、空行、$ 符号、单位等)。

## 【表格解读】
原文表格逐字还原:

| Category | Dataset | Metric | Result |
|----------|---------|--------|--------|
| Accuracy | gsm8k / test | Total Samples | 1000 |
| Accuracy | gsm8k / test | exact_match,strict-match | 0.5436 |
| Accuracy | gsm8k / test | exact_match,flexible-extract | 0.5451 |

**逐行解读:**
- **第 1 行**:Category=Accuracy,Dataset=`gsm8k / test`,Metric=`Total Samples`,Result=`1000`。含义为本次准确率评测是在 GSM8K 数据集 test 切分上完成,共 1000 条样本(GSM8K test 标准集大小),作为后续两项指标的分母基准。
- **第 2 行**:Metric=`exact_match,strict-match`,Result=`0.5436`。含义为采用"严格匹配"规则判定答对——只有预测文本与期望"最终答案抽取格式"完全一致才算正确;在该口径下 1000 题中有 543.6 题(约 544 题)被记为正确,反映模型输出对评测脚本期望格式的贴合度。
- **第 3 行**:Metric=`exact_match,flexible-extract`,Result=`0.5451`。含义为采用"宽松抽取"规则,容忍轻微格式差异(只要最终数值正确即可),答对样本约 545.1 题(约 545 题)。该数值略高于严格口径 0.0015,说明模型大多数情况下能给出正确数值,少数错误源自末尾格式(如多余句号、单位词、换行等),而非推理错误本身。

## 【公式解读】
原文无公式。

## 【关联】
- **依赖安装(上游)**:文档在 "If you do not want to use the docker image, you can also build from source" 一节明确指向 [`../../getting_started/installation.md`](../../getting_started/installation.md),说明 vllm-ascend 源码构建与依赖安装是本文档部署路径的"前置章节"。
- **运行时(本体)**:vllm-ascend 是 vLLM 在 Ascend NPU 上的后端插件,本文档对其调用方式为标准 `vllm serve` CLI + OpenAI `/v1/completions` HTTP 接口,因此可与任何兼容 OpenAI API 的客户端/评测框架对接(例如 lm-evaluation-harness)。
- **模型来源(外部)**:权重托管在 ModelScope 的 `nv-community/Minitron-8B-Base` 仓库,与 Hugging Face `nv-community/Minitron-8B-Base` 同源,均来自 NVIDIA 官方社区账号。
- **评测方法(下游)**:GSM8K 评测口径在文档 "Remarks on Metrics" 中明确两类 `exact_match` 的判定差异,这是与 lm-evaluation-harness 中 `gsm8k` 任务 `strict-match` / `flexible-extract` 配置一致的约定。

## 【使用方法】

### 1. 拉取并启动 Docker 容器(原文)
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
docker run --rm \
  --name vllm-ascend \
  --shm-size=1g \
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
  -v /data/vllm-workspace/models:/data/vllm-workspace/models \
  -p 8000:8000 \
  -it $IMAGE bash
```
若不想用 Docker,可参考 [installation](../../getting_started/installation.md) 走源码构建。

### 2. 启动在线推理服务(原文)
```bash
vllm serve "nv-community/Minitron-8B-Base" \
  --served-model-name minitron-8b-base \
  --tensor-parallel-size 1 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9 \
  --enforce-eager \
  --port 8000
```

### 3. 功能验证请求(原文)
```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minitron-8b-base",
    "prompt": "Question: If a train travels 60 miles in 2 hours, what is its average speed in miles per hour?\nAnswer:",
    "max_tokens": 64,
    "temperature": 1.0
  }'
```
收到有效响应即代表部署成功。

### 4. 准确率评估配置(原文)
- Dataset:`gsm8k`
- Split:`test`
- Number of samples:`1000`
- Few-shot setting:`5-shot`
- `apply_chat_template`:`False`
- `fewshot_as_multiturn`:`False`
