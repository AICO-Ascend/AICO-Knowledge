# Qwen2.5-Math-RM-72B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen2.5-Math-RM-72B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen2.5-Math-RM-72B.md

# 深度解读：Qwen2.5-Math-RM-72B 部署与验证指南

---

## 【定位】

这篇文档解决**如何在 vllm-ascend 平台上完整部署、启动并功能验证 Qwen2.5-Math-RM-72B 这一数学专用奖励模型**的问题，涵盖从环境准备、镜像选择、单节点部署、curl 接口验证到批量打分对比的端到端工作流，为在 Ascend NPU 上运行 72B 参数级 RM（Reward Model）提供标准化操作手册。

---

## 【技术要点】

1. **模型规格**：720 亿参数奖励模型，专为数学推理评分设计，最大上下文窗口 128k tokens；自 `vllm-ascend:v0.9.0` 起支持。

2. **硬件要求（BF16 版本）**：
   - 启用 CPU offloading：至少 **1 张 Atlas 910B4 (32GB × 1)**
   - 不启用 CPU offloading：至少 **4 张 Atlas 910B4 (32GB × 4)**

3. **部署载体**：使用官方 Docker 镜像 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，需挂载 `/dev/davinci0–3`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 以及驱动/工具相关路径，支持多 NPU 利用。

4. **推理服务命令**：通过 `vllm serve` 启动，关键参数包括：
   - `--served-model-name qwen2.5-math-rm-72b`
   - `--trust-remote-code`
   - `--max-model-len 32768`（部署上下文长度为 32k）
   - `--task reward`（**必须**，启用奖励模型模式）
   - `ASCEND_RT_VISIBLE_DEVICES=0`（单卡部署示例）

5. **功能验证接口**：通过 `POST /v1/reward` 单条打分；批量打分走 `POST /v1/reward/batch`，支持在请求体中传入预计算 `score` 与 `reasoning` 用于对比。

6. **模型权重来源**：ModelScope 下载链接 `https://www.modelscope.cn/models/Qwen/Qwen2.5-Math-RM-72B`，建议本地路径 `./Qwen2.5-Math-RM-72B/`。

---

## 【关键机制与数据】

- **RM 工作原理**：模型接收多轮对话（含 system/user/assistant 消息），对 assistant 的回答输出一个标量 reward 分数，分数越高代表数学解答越准确。例如原文示例对 "2+2 equals 4" 返回 `{"reward_score": 1.69}`（原文标注的有效响应）。

- **批量对比机制**：在 `/v1/reward/batch` 请求中，`batch_rewards` 字段由调用方提供期望分数及理由，模型对 `conversations` 中每条对话重新打分，实现模型打分与人工/参考打分的对比验证。原文示例分数：
  - 正确答案 2+2=4 → 参考 9.85（理由：数学正确且简洁）
  - 错误答案 2+2=5 → 参考 1.20（理由：存在数学事实错误）

- **上下文长度差异**：模型原生支持 128k tokens，但部署时通过 `--max-model-len 32768` 设为 32k（原文给出参数），用于平衡显存与推理需求。

- **多 NPU 利用**：原文指出镜像版本支持 multi-NPU 部署，"allowing the model to utilize all available NPU devices (e.g., 4 NPUs) for improved performance"——即在 4 卡配置下可拆分模型获得更高吞吐。

- **数据流**：本地权重目录 → Docker 容器 → `vllm serve` 启动 HTTP 服务（端口 8000）→ curl 调用 `/v1/reward*` 端点 → 返回 JSON 中的 `reward_score`。

---

## 【表格解读】

**原文无表格**。文档以参数化列表（环境准备、安装、部署、验证）形式组织，未包含任何 markdown 表格或结构化对比表。硬件需求虽以"X cards or higher"形式列出，但原文并未将其整理为表格结构。

---

## 【公式解读】

**原文无公式**。文档不包含任何 LaTeX 表达式或伪代码公式；reward 评分机制以标量 `reward_score` 形式直接返回数值，未给出数学定义。

---

## 【关联】

文档通过三处内部链接形成完整依赖链：

1. **[Supported Models 矩阵](../../user_guide/support_matrix/supported_models.md)** —— 提供 Qwen2.5-Math-RM-72B 在 vllm-ascend 上的功能支持矩阵（如 LoRA、量化、并行策略等是否启用），是"Supported Features"章节的实际数据来源。

2. **[Feature Guide 索引](../../user_guide/feature_guide/index.md)** —— 提供各项功能（如 reward 任务、CPU offloading、多 NPU 并行）的具体配置说明，本文中提及的 `--task reward` 参数细节、CPU offloading 硬件选择逻辑需要回到此处查阅。

3. **[Installation Prebuilt Image](../../getting_started/installation.md#installation-prebuilt-image)** —— Docker 镜像选择、机器型号匹配、`docker run` 启动流程的权威指南，是"Installation"小节的执行依据。

外部依赖方面，模型权重来自 ModelScope，技术报告引自 arXiv 论文 `2409.12122`，并通过 HuggingFace 模型卡和 vLLM 官方文档补充模型能力说明。

---

## 【使用方法】

### 1. 下载模型权重
从 ModelScope 下载 BF16 版本至本地 `./Qwen2.5-Math-RM-72B/` 目录。

### 2. 启动 Docker 容器
设置 `IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，挂载 4 个 `/dev/davinci*` 设备及驱动路径后启动容器（原文给出完整 docker run 命令）。

### 3. 部署推理服务（单节点单卡示例）
执行 `deploy.sh`：
```shell
export ASCEND_RT_VISIBLE_DEVICES=0
export MODEL_PATH="Qwen/Qwen2.5-Math-RM-72B"
vllm serve ${MODEL_PATH} \
    --host 0.0.0.0 --port 8000 \
    --served-model-name qwen2.5-math-rm-72b \
    --trust-remote-code \
    --max-model-len 32768 \
    --task reward
```

### 4. 单条打分验证
`curl http://localhost:8000/v1/reward`，提交包含 system/user/assistant 的消息体，期望返回 `{"reward_score": ...}`。

### 5. 批量对比打分
`curl http://localhost:8000/v1/reward/batch`，在 `conversations` 数组中传入多条对话，并在 `batch_rewards` 中提供参考分数与理由。

### 6. 启用 CPU offloading（低显存场景）
硬件配置降为 1 张 910B4 时需启用 CPU offloading（具体配置项需参阅 Feature Guide，原文未给出 CLI 参数）。

> 注：原文未涉及 `--tensor-parallel-size`、`--quantization` 等进阶参数以及性能基准测试的具体命令。
