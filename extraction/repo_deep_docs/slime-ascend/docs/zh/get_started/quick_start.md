# 快速使用

> 仓 `slime-ascend` · 路径 `docs/zh/get_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/slime-ascend/docs/zh/get_started/quick_start.md

# slime-ascend 快速使用文档深度解读

## 【定位】

本篇是一份面向新用户的「一小时内上手」实战指南，解决从零到 RL（强化学习）训练跑通的全链路工程问题：环境搭建（Docker）→ 模型/数据下载 → 权重格式转换（HF ↔ Megatron torch_dist）→ 启动训练脚本 → 解读关键参数，最终帮助用户在 slime 框架上以"训推一体/分离"两种模式完成第一次 GRPO 类算法训练。

## 【技术要点】

1. **容器化环境**：使用 `slimerl/slime:latest` 镜像启动交互式容器，附带 `--gpus all --ipc=host --shm-size=16g --ulimit memlock=-1 --ulimit stack=67108864` 等参数，避免 sglang/megatron 的 patch 引发依赖冲突。
2. **硬件平台**：B200 系列完全支持（与 H 卡步骤相同）；H100/H200 官方支持，Megatron 后端在 H 卡上经过完整 CI 测试。
3. **模型权重转换**：HF ↔ Megatron `torch_dist` 双向转换使用 `tools/convert_hf_to_torch_dist.py` / `tools/convert_torch_dist_to_hf.py`，大模型可用 `torchrun` 多 GPU 转换；kimi-k2 需将 `config.json` 中 `model_type` 改写为 `deepseek_v3`。
4. **八类训练参数**：训练脚本被拆为 `MODEL_ARGS`、`CKPT_ARGS`、`ROLLOUT_ARGS`、`EVAL_ARGS`、`PERF_ARGS`、`GRPO_ARGS`、`OPTIMIZER_ARGS`、`SGLANG_ARGS` 八组，分别对应模型超参、检查点路径、采样、评估、并行/性能、GRPO 算法、优化器、推理服务。
5. **采样-训练闭环约束**：`rollout-batch-size × n-samples-per-prompt = global-batch-size × num-steps-per-rollout`，slime 会在 `num-steps-per-rollout` 设置时自动/校验 `global-batch-size`。
6. **训推协同**：默认训推分离（Actor 与 Rollout 各占一组 GPU）；通过 `--colocate` 开启训推一体化（共享 GPU）；调度使用 `sgl-router` 多 SGLang Server。

## 【关键机制与数据】

- **采样闭环机制**（原文: "整个训练流程可视为一个 **'数据采样 → 权重更新'** 的闭环"）：阶段一 Rollout 阶段通过 `--rollout-batch-size=16` × `--n-samples-per-prompt=8` = 128 条样本；阶段二 Training 阶段通过 `--global-batch-size=128` × `--num-steps-per-rollout=1` 一次性消费完毕；`--num-rollout=3000` 控制总循环轮数。
- **Rollout/Training 边界区分**（原文: "这里的 **参数更新** 指训练环节的 optimizer.step()，不同于训练引擎向推理引擎发起的权重同步(Weight Sync)"）：明确了 RL 中两种 step 的语义区别。
- **Dynamic Batch Size**（原文: "`--max-tokens-per-gpu 4608`"）：启用后系统按 token 数动态打包样本，使每 micro-batch 总 token 接近该上限；CP 模式下 `N` 张 CP 卡共享 `N × max-tokens-per-gpu`；并强调 "开启 dynamic batch size 不会对 loss 计算有影响"。
- **KL 散度控制**（原文: "`--kl-loss-coef 0.00`"）：KL 散度作为监控指标存在；只有当 `kl-loss-coef > 0` 才会参与损失计算。
- **GRPO 关键超参**（原文: "`--eps-clip 0.2`、`--eps-clip-high 0.28`、`--entropy-coef 0.00`"）：双侧 clip 范围（PPO-style 与 upper-bound）。
- **SGLang 调度**（原文: "`dp_size` 会通过 `rollout-num-gpus / rollout-num-gpus-per-engine` 计算得到"）：`--rollout-num-gpus-per-engine 2` 等同 SGLang 的 `tp_size`；任何 SGLang 参数通过 `--sglang-` 前缀透传（如 `--sglang-log-level INFO`）。
- **数据均衡**（原文: "`--balance-data`"）：保证 DP rank 间计算量大致相等，可能提升训练速度。
- **Megatron 并行配置**（原文示例值）：`--tensor-model-parallel-size 2`、`--sequence-parallel`、`--context-parallel-size 2`、`--expert-model-parallel-size 1`、`--expert-tensor-parallel-size 1`、`--recompute-granularity full`、`--recompute-method uniform`、`--recompute-num-layers 1`。
- **优化器配置**（原文示例值）：`--optimizer adam`、`--lr 1e-6`、`--lr-decay-style constant`、`--weight-decay 0.1`、`--adam-beta1 0.9`、`--adam-beta2 0.98`。
- **评估参数**（原文示例值）：`--eval-interval 5`、`--n-samples-per-eval-prompt 16`、`--eval-max-response-len 16384`、`--eval-top-p 0.7`。
- **数据集下载**（原文示例）：`zai-org/GLM-Z1-9B-0414`（模型）、`zhuzilin/dapo-math-17k`（训练）、`zhuzilin/aime-2024`（评估）。
- **保存策略**（原文: "`--save-interval 20`"）：每 20 步保存一次模型 checkpoint。
- **文档截断说明**：原文最末段关于"训推一体化模式"的注意项在"会占据一定量的"处被截断，Megatron offload 后内存占用的具体数值与后续说明未在原文给出。

## 【表格解读】

原文无表格。所有配置项以 bash 数组（`MODEL_ARGS=()`、`CKPT_ARGS=()` 等）的代码块形式呈现，未采用 markdown 表格。

## 【公式解读】

**原文无标准数学公式**，但存在一处核心**闭环平衡约束**（伪代码形式）：

$$
(\text{rollout-batch-size} \times \text{n-samples-per-prompt}) = (\text{global-batch-size} \times \text{num-steps-per-rollout})
$$

符号含义：

- `rollout-batch-size`：每轮采样阶段的 **Prompt 数量**（即采样的"题目数"）。
- `n-samples-per-prompt`：每个 Prompt 生成的 **回复样本数**（GRPO 类算法对同一 Prompt 多采样）。
- 左侧乘积 = 单轮 Rollout 阶段产出的 **总样本数**（16 × 8 = 128）。
- `global-batch-size`：执行一次 `optimizer.step()` 所需要的样本数（一个完整更新单元）。
- `num-steps-per-rollout`：使用同一批采样数据连续做几次参数更新（默认为 1，on-policy 训练）。
- 右侧乘积 = 单轮训练消耗的 **总样本数**（128 × 1 = 128）。
- **作用**：保证每轮"采样产出"恰好等于"训练消耗"，避免采样浪费或数据不足。slime 会在 `num-steps-per-rollout` 已设置时，自动补齐或校验 `global-batch-size`，防止二者不一致导致训练异常。

## 【关联】

- **AMD 平台支持** → [amd_tutorial.md](../../en/platform_support/amd_tutorial.md)：当用户不便使用 Docker / 在 AMD GPU 上运行时，作为替代方案。文档中明确"对于 AMD 支持，请参考"该教程，构成 quick_start 的分支延展。
- **模型实战示例（GLM 系列）** → [glm4.7-30B-A3B.md](../examples/glm4.7-30B-A3B.md)、[glm4.7-355B-A32B.md](../examples/glm4.7-355B-A32B.md)：GLM4-9B.sh 之外更复杂 MoE 架构的端到端示例文档，对应 `scripts/models/` 中不同规模配置文件。
- **DeepSeek-R1 复现** → [deepseek-r1.md](../examples/deepseek-r1.md)：作为大型推理模型 RL 训练的应用案例。
- **非 Docker 环境** → [`build_conda.sh`](https://github.com/THUDM/slime/blob/main/build_conda.sh)：与 Docker 并列的 Conda 安装方式。
- **上游依赖**：slime 内部使用 [sglang](https://arxiv.org/abs/2507.18071) 推理 + Megatron-LM 训练，通过 `sgl-router` 调度，并附带临时 patch（这就是为何强烈建议使用官方 Docker 镜像）。
- **下游支持算法**：除 GRPO 外，还支持 [GSPO](https://arxiv.org/abs/2507.18071)、[Reinforce++](https://arxiv.org/abs/2501.03262)、[Reinforce++ Baseline](https://arxiv.org/abs/2501.03262)、[PPO](https://arxiv.org/abs/1707.06347)。
- **TIS（截断重要性采样）**：参考 [fengyao 的博客](https://fengyao.notion.site/off-policy-rl)，由 `--use-tis` 开启，用于 off-policy RL 训练。

## 【使用方法】

**启动 Docker 容器**（原文命令）：
```bash
docker pull slimerl/slime:latest
docker run --rm --gpus all --ipc=host --shm-size=16g \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  -it slimerl/slime:latest /bin/bash
```

**更新 slime 到最新版**（原文命令）：
```bash
cd /root/slime
git pull
pip install -e . --no-deps
```

**下载资源**（原文命令）：
```bash
hf download zai-org/GLM-Z1-9B-0414 --local-dir /root/GLM-Z1-9B-0414
hf download --repo-type dataset zhuzilin/dapo-math-17k --local-dir /root/dapo-math-17k
hf download --repo-type dataset zhuzilin/aime-2024 --local-dir /root/aime-2024
```

**HF → Megatron 转换**（原文命令，GLM4-9B 示例）：
```bash
cd /root/slime
source scripts/models/glm4-9B.sh
PYTHONPATH=/root/Megatron-LM python tools/convert_hf_to_torch_dist.py \
    ${MODEL_ARGS[@]} \
    --hf-checkpoint /root/GLM-Z1-9B-0414 \
    --save /root/GLM-Z1-9B-0414_torch_dist
```

**Megatron → HF 反向转换**（原文命令）：
```bash
PYTHONPATH=/root/Megatron-LM python tools/convert_torch_dist_to_hf.py \
  --input-dir /path/to/torch_dist_ckpt/iter_xxx/ \
  --output-dir /root/GLM-Z1-9B-0414-iter_xxx \
  --origin-hf-dir /root/GLM-Z1-9B-0414
```
> Embedding 形状不匹配时需指定 `--vocab-size`。

**启动训练**（原文命令）：
```bash
cd /root/slime
bash scripts/run-glm4-9B.sh
```

**训推分离 → 训推一体化切换**（原文命令）：在 `ray job submit` 中加入 `--colocate`，并把 `--actor-num-gpus-per-node` 提到所有可用卡数；启用后 `--rollout-num-gpus` 被忽略。

**关键覆盖示例**（原文代码片段）：如果需要修改模型配置文件中的参数，可在 `source` 之后直接追加，例如：
```bash
source "${SCRIPT_DIR}/models/glm4-9B.sh"
MODEL_ARGS+=(--rotary-base 10000)
```

**未涉及内容**：
- 多机分布式启动的完整命令（原文仅提及大模型可用 `torchrun` 多 GPU/多机转换，但未给出完整 `ray job submit` 多机模板）。
- 训推一体化模式下 Megatron offload 后的具体内存占用与调优建议（原文对应段落被截断）。
