# Quick Start

> 仓 `slime-ascend` · 路径 `docs/en/get_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/slime-ascend/docs/en/get_started/quick_start.md

# 「slime-ascend」Quick Start 文档深度解读

---

## 【定位】

本篇文档旨在**帮助用户在 1 小时内完成 slime 强化学习训练框架的端到端搭建与启动**，系统覆盖环境配置（Docker/Conda/AMD）、模型与数据集下载、HuggingFace ↔ Megatron 双向权重转换、以及训练脚本（以 `run-glm4-9B.sh` 为例）中 MODEL_ARGS / CKPT_ARGS / ROLLOUT_ARGS 三类关键参数的解读与改写指导。

---

## 【技术要点】

1. **Docker 优先策略**：强烈推荐使用 `slimerl/slime:latest` 镜像，因 slime 内含 sglang/megatron 的临时补丁（patches），直接用镜像可规避环境冲突。
2. **硬件支持双线**：
   - **B200 系列**：完全支持，安装与启动流程与 H 系列一致；基础功能稳定，但**尚无 CI 保护**，建议用于开发/测试。
   - **H 系列（H100/H200）**：官方支持 + 完整 CI 测试 + Megatron 后端 CI 保护，**推荐用于生产环境**。
3. **权重格式互转**：Megatron 后端要求 `torch_dist` 格式权重，必须通过 `tools/convert_hf_to_torch_dist.py`（HF→Megatron）和 `tools/convert_torch_dist_to_hf.py`（Megatron→HF）做双向转换；后者因 Megatron 对 embedding 做 padding，转换后可能不正确，需手动指定 `--vocab-size`。
4. **闭环训练结构**：训练被抽象为 **"Data Sampling（Rollout）→ Weight Update（Training）"** 闭环；默认 on-policy（`--num-steps-per-rollout=1`）。
5. **关键不变量约束**：每轮「产出 = 消费」，即 `rollout-batch-size × n-samples-per-prompt = global-batch-size × num-steps-per-rollout`；slime 在设置 `--num-steps-per-rollout` 时会自动设置或校验 `--global-batch-size`。
6. **特殊模型配置提示**：转换 `kimi-k2` 权重时需将 `config.json` 中 `"model_type": "kimi_k2"` 改为 `"model_type": "deepseek_v3"`。

---

## 【关键机制与数据】

### 数据流 / 工作原理

**原文：「The entire training process can be viewed as a closed loop of **"Data Sampling → Weight Update"**.」**

训练框架分两阶段循环：
- **Phase One – Rollout**：使用当前 Actor 模型对 Prompt 集采样生成响应，由 Reward Model 打分。`--rollout-batch-size` 控制每轮 Prompt 数，`--n-samples-per-prompt` 控制每个 Prompt 的响应数（用于 GRPO 类算法）。
- **Phase Two – Training**：基于 Rollout 产出样本执行 `optimizer.step()`。`--global-batch-size` 控制单次参数更新的样本量，`--num-steps-per-rollout` 控制使用当前 Rollout 数据做多少次参数更新（默认 1 = on-policy）。

**原文：「the parameter update here refers to the optimizer.step() in the training phase, which is different from the weight synchronization (Weight Sync) initiated by the training engine to the inference engine.」**

⚠️ **概念区分**：`optimizer.step()`（参数更新）≠ Weight Sync（训练引擎→推理引擎的权重同步），二者不要混淆。

### 性能与参数数值（原文给出的具体取值）

| 参数项 | 原文数值 | 含义 |
|---|---|---|
| `--num-rollout` | 3000 | 整个「采样→训练」循环总执行轮数 |
| `--rollout-batch-size` | 16 | 每轮采样的 Prompt 数 |
| `--n-samples-per-prompt` | 8 | 每个 Prompt 生成的响应数 |
| `--num-steps-per-rollout` | 1 | 默认 on-policy |
| `--global-batch-size` | 128 | 单次参数更新样本量 |
| `--save-interval` | 20 | 模型保存间隔（步数） |
| `--rollout-max-response-len` | 8192 | 采样最大响应长度 |
| `--rollout-temperature` | 1 | 采样温度 |
| Docker `--shm-size` | 16g | 共享内存大小 |
| Docker `--ulimit stack` | 67108864 | 栈大小（字节） |

按公式校验：16 × 8 = 128 = 128 × 1 ✓，与文档示例一致。

---

## 【表格解读】

**原文无表格。**

文档以 Bash 数组 + 注释块（`#`）的形式罗列参数，未呈现 `<table>` 标签的正式表格。文中所有参数分组（MODEL_ARGS / CKPT_ARGS / ROLLOUT_ARGS）均为代码块形式的命令行参数清单。

---

## 【公式解读】

原文唯一公式：

$$
\text{rollout-batch-size} \times \text{n-samples-per-prompt} = \text{global-batch-size} \times \text{num-steps-per-rollout}
$$

**逐符号解释**：

| 符号 | 原文含义 | 角色 |
|---|---|---|
| `rollout-batch-size` | 每轮 Rollout 的 Prompt 数量 | Rollout 阶段输入规模 |
| `n-samples-per-prompt` | 每个 Prompt 生成的响应数 | 单 Prompt 的样本扩展倍数（GRPO 类算法的关键） |
| `global-batch-size` | 单次 `optimizer.step()` 所需的样本量 | 训练阶段单次更新的消费 |
| `num-steps-per-rollout` | 使用当前 Rollout 数据执行的更新次数 | 训练阶段对样本的复用次数 |

**作用**：保证每轮 Rollout 产出（左侧 LHS）正好被该轮 Training 完全消费（右侧 RHS），不出现样本浪费或样本不足。原文明确指出：设置 `--num-steps-per-rollout` 时，`--global-batch-size` 若未设置则自动设置，若已设置则按此公式校验。

---

## 【关联】

依据文末提供的 4 条内部链接，结合文档上下文，可梳理出 slime 文档体系的上下游关系：

1. **硬件平台支线 → [../platform_support/amd_tutorial.md](../platform_support/amd_tutorial.md)**
   - 原文：「For AMD support, please refer to AMD Usage Tutorial.」与 Docker/NVIDIA 主线并行，文档主体讲解 NVIDIA GPU，AMD 是替代平台。

2. **示例模型案例集（三选一）→**
   - [../examples/glm4.7-30B-A3B.md](../examples/glm4.7-30B-A3B.md)：GLM-4.7 系列 MoE（30B-A3B）示例，与正文 `run-glm4-9B.sh` 同属「具体训练启动脚本」层级。
   - [../examples/glm4.7-355B-A32B.md](../examples/glm4.7-355B-A32B.md)：GLM-4.7 系列大尺寸 MoE（355B-A32B）示例，对应原文「For larger models, you can use `torchrun` to start the conversion script to convert with multi-gpus or even multi-nodes」的更大规模部署场景。
   - [../examples/deepseek-r1.md](../examples/deepseek-r1.md)：DeepSeek-R1 训练示例；正文中特别提及「kimi-k2 转换需将 model_type 改为 `deepseek_v3`」，暗示 DeepSeek 系列架构在 slime 中有专门适配。

3. **环境构建支线 → [build_conda.sh](https://github.com/THUDM/slime/blob/main/build_conda.sh)**
   - Docker 不可用时的 Conda 替代方案，与 AMD 教程并列于「环境配置」决策树。

4. **模型配置库 → `scripts/models/` 目录**
   - 正文以 `glm4-9B.sh` 为例 source 的模型配置脚本，与 examples 子页形成「通用机制（Quick Start）→ 特定模型（examples）」的层级关系。

---

## 【使用方法】

### 启动方式（原文命令照录）

**A. Docker 路线（推荐）**
```bash
docker pull slimerl/slime:latest
docker run --rm --gpus all --ipc=host --shm-size=16g \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  -it slimerl/slime:latest /bin/bash
```

**B. 容器内更新 slime**
```bash
cd /root/slime
git pull
pip install -e . --no-deps
```

**C. 下载模型与数据集（以 GLM-Z1-9B 为例）**
```bash
hf download zai-org/GLM-Z1-9B-0414 --local-dir /root/GLM-Z1-9B-0414
hf download --repo-type dataset zhuzilin/dapo-math-17k --local-dir /root/dapo-math-17k
hf download --repo-type dataset zhuzilin/aime-2024 --local-dir /root/aime-2024
```

**D. 权重转换**
```bash
# HF → Megatron
cd /root/slime
source scripts/models/glm4-9B.sh
PYTHONPATH=/root/Megatron-LM python tools/convert_hf_to_torch_dist.py \
    ${MODEL_ARGS[@]} \
    --hf-checkpoint /root/GLM-Z1-9B-0414 \
    --save /root/GLM-Z1-9B-0414_torch_dist

# Megatron → HF（回转）
PYTHONPATH=/root/Megatron-LM python tools/convert_torch_dist_to_hf.py \
  --input-dir /path/to/torch_dist_ckpt/iter_xxx/ \
  --output-dir /root/GLM-Z1-9B-0414-iter_xxx \
  --origin-hf-dir /root/GLM-Z1-9B-0414
```

**E. 启动训练**
```bash
cd /root/slime
bash scripts/run-glm4-9B.sh
```

### 关键配置项（原文 CKPT_ARGS / ROLLOUT_ARGS 摘录）

| 配置类别 | 关键配置项 | 说明 |
|---|---|---|
| CKPT_ARGS | `--hf-checkpoint` | 仅加载 tokenizer，不实际使用权重 |
| CKPT_ARGS | `--ref-load` | Reference Model 的 Megatron 格式 checkpoint |
| CKPT_ARGS | `--load` | Actor 模型加载路径；空/无效时 fallback 到 `--ref-load` |
| CKPT_ARGS | `--save` / `--save-interval 20` | 模型保存路径与间隔步数 |
| ROLLOUT_ARGS | `--prompt-data` + `--input-key` + `--label-key` | JSONL 数据集与字段映射 |
| ROLLOUT_ARGS | `--apply-chat-template` | OpenAI message 格式时启用 |
| ROLLOUT_ARGS | `--rollout-shuffle` | Rollout 阶段是否打乱 |
| ROLLOUT_ARGS | `--rm-type deepscaler`（可配 `--custom-rm-path`） | Reward Model 类型 |
| ROLLOUT_ARGS | `--rollout-max-response-len 8192` / `--rollout-temperature 1` | 采样超参 |

### ⚠️ 重要注意事项（原文告警）

- **使用前必须核对 `scripts/models/*.sh` 中的参数**（如 `--rotary-base`）是否与当前模型版本完全一致；不同版本的同结构模型配置可能不同。修改方式：`source` 后追加覆盖，例如 `MODEL_ARGS+=(--rotary-base 10000)`。
- **kimi-k2 特殊处理**：转换前手动修改 `config.json` 的 `"model_type"` 字段。
- **Megatron→HF embedding 异常时**：手动指定 `--vocab-size`。

> ⚠️ **原文截断说明**：本文档在 ROLLOUT_ARGS 示例末尾以「Load balancing for」被截断，后续关于「rollout 与训练引擎的负载均衡」配置内容未呈现于提供的文本中，故解读不延伸至该部分。
