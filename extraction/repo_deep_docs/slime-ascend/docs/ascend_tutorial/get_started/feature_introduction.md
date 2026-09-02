# ...

> 仓 `slime-ascend` · 路径 `docs/ascend_tutorial/get_started/feature_introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/slime-ascend/docs/ascend_tutorial/get_started/feature_introduction.md

# 「slime-ascend」文档 `docs/ascend_tutorial/get_started/feature_introduction.md` 深度解读

---

## 【定位】

本文档是 **slime 框架在 NPU 上所支持训练特性的总览（Feature Introduction）**，为开发者集中说明 OPD、TIS、MOE Routing Replay、Context Parallel、Retool 共五项特性的功能定位、核心机制、关键参数配置方式与脚本/示例入口，并指引高级特性（如 PD Disaggregation）跳转至 `advanced` 章节。

---

## 【技术要点】

1. **OPD（On-Policy Distillation）**：通过 `RM_ARGS` 注入三组参数 `--custom-rm-path`、`--custom-reward-post-process-path`、`--rm-url`，调用教师模型推理服务（`/generate` 端点）获取 token 级 log probability，并在 `sample.teacher_log_probs` 中供训练引擎计算蒸馏损失（KL 散度）。要求师生模型基于**相同词表**。

2. **TIS（Truncated Importance Sampling）**：在 `GRPO_ARGS` 中启用 `--use-tis` 与 `--grpo-clip 0.2`，通过对 rollout 与 train 之间的策略版本偏差施加重要性采样权重并截断，限制方差、稳定训练。

3. **MOE Routing Replay**（原文标题写作 "Reply"）：在 `SGLANG_ARGS` 中加入 `--use-rollout-routing-replay`，在训练时重放 rollout 阶段的路由以解决 MoE RL 训练中前向/反向、训练/推理路由不一致问题。

4. **Context Parallel**：在 `ROLLOUT_ARGS` 设置 `--rollout-max-response-len $((1024 * 32))`、`--rollout-max-prompt-len $((1024 * 128))`；在 `PERF_ARGS` 设置 `--context-parallel-algo megatron_cp_algo`、`--context-parallel-size 4`，将超长序列沿 token 维度切分到多张 NPU。

5. **Retool**：在 `CUSTOM_ARGS` 中配置 `--custom-generate-function-path generate_with_retool.generate`、`--custom-rm-path generate_with_retool.reward_func`；同时**必须从 `ROLLOUT_ARGS` 中删除 `--apply-chat-template`**，因为 ReTool 生成函数内部自行处理工具调用格式与消息拼接。

6. **高级特性入口**：pd-disaggregation 等高级特性文档位于 `../advanced/`。

---

## 【关键机制与数据】

> 本节内容均标注为原文转述，未做臆造补充。

### OPD
- **数据流（原文）**：
  1. 自定义奖励函数将样本的完整 token 序列（prompt + response）发送至教师模型服务，请求返回**每个 token 的 log probability**；
  2. 后处理函数从教师返回结果中提取 response 部分的 token 级 log probabilities，存入 `sample.teacher_log_probs`；
  3. 训练引擎在计算蒸馏损失（**通常为 KL 散度**）时使用该字段。
- **约束（原文）**：教师模型与学生模型使用相同 tokenizer 对应的 token id 序列作为输入，因此**两者必须基于相同词表**；教师模型**不生成新 token，仅对输入序列的每个 token 返回 log probability**；教师模型通常部署为**单独的推理服务**。

### TIS
- **作用对象（原文）**：针对 rollout 阶段与 train 阶段之间的**策略版本不匹配**（training-inference mismatch）。
- **做法（原文）**：对旧策略样本施加**重要性采样权重并截断**，在限制方差的同时提高训练稳定性。

### MOE Routing Replay
- **问题（原文）**：路由机制的不稳定性：训练的前向与反向传播路由可能不一致，且训练和推理阶段的路由分布也存在显著偏差，**严重时会导致训练崩溃**。
- **解决方式（原文）**：在训练时**重放 rollout 阶段的路由**。

### Context Parallel
- **机制（原文）**：将超长序列**沿 token 维度切分到多张 NPU 上并行计算**，突破单卡显存对序列长度的限制。
- **使用提示（原文）**：上下文并行**通常与张量并行（`--tensor-model-parallel-size`）结合使用**，需根据总 NPU 数量和序列长度合理分配并行维度。

### Retool
- **场景（原文）**：面向工具调用、代码执行等多步交互的智能体场景。
- **机制（原文）**：使用 ReTool 框架，让模型在 rollout 过程中**自由调用外部工具**，并根据工具使用结果计算奖励。
- **关闭聊天模板的原因（原文）**：因为 ReTool 的生成函数内部会自行处理工具调用格式和消息拼接，无需 slime 再应用默认的聊天模板。

> 原文未提供任何量化性能数据（loss 曲线、token/s、NPU 利用率等）。

---

## 【表格解读】

**原文无表格**。所有特性均通过 bash 脚本代码块 + 项目符号列表的方式呈现，无 markdown 表格结构。

---

## 【公式解读】

**原文无公式**。文中仅出现 "KL 散度" 这一术语名词，未给出数学表达式或伪代码公式。

---

## 【关联】

| 上游/下游模块 | 文档链接 | 关联性质 |
|---|---|---|
| 高级特性总览 | `../advanced/` | 跳转入口，原文指引"高级特性在 advanced 进行详细介绍" |
| PD Disaggregation | `../advanced/pd-disaggregation.md` | 被列入高级特性列表中 |
| OPD 自定义奖励函数实现 | `../../../examples/on_policy_distillation/on_policy_distillation.py` | 解释 `--custom-rm-path` / `--custom-reward-post-process-path` 时指向，承载 reward_func 与 post_process_rewards 实际逻辑 |
| OPD 启动脚本示例 | `../../../examples/on_policy_distillation/run-glm4.7-30B-opd.sh` | 给出 OPD 的可运行配置样例（基于 GLM4.7-30B） |
| TIS / 训练-推理不一致专题 | `../../../examples/train_infer_mismatch_helper/README.md` | "Rollout Correction Methods.md"，作为 TIS 原理的本地详细文档 |
| Retool 自定义生成函数实现 | `../../../examples/retool/generate_with_retool.py` | 解释 `--custom-generate-function-path` 时指向，承载 `generate` 主流程 |
| Retool 启动脚本示例 | `../../../examples/retool/retool_glm4.7_flash_rl_npu.sh` | 给出 Retool 的可运行配置样例（基于 GLM4.7-flash） |
| MOE 路由重放（外部文档） | `https://gitcode.com/Ascend/slime-ascend/blob/main/docs/zh/get_started/customization.md#18-moe-路由重放` | 跳转到 customization.md 的 1.8 章节，补充 MOE Routing Replay 详情 |
| TIS 原理参考（外部文献） | `https://ionides.github.io/pubs/ionides08-jcgs.pdf` 与 `https://fengyao.notion.site/off-policy-rl` | TIS 数学背景与 off-policy RL 博客 |
| sglang-router 0.3.2 Bug | `https://github.com/THUDM/slime/issues/1909` 与 `https://github.com/zhuzilin/sgl-router` | MOE Routing Replay 章节中的兼容性提示，指向 issue 与替代仓库 |

**关联脉络**（原文出现的层级关系）：
- 本文 `feature_introduction.md` 列出 5 个核心特性 + 1 个高级特性入口。
- "On-Policy Distillation"、"Retool" 两条特性各自有完整的示例脚本（`.sh`）和实现（`.py`），构成 **"文档 → 示例脚本 → 自定义函数实现"** 的三层引用链。
- TIS 没有本地 `.py` 实现指引，仅指向 `train_infer_mismatch_helper` 的 README 和外部论文。
- MOE Routing Replay 没有 `.py` 实现，仅指向 `customization.md` 的具体小节。

---

## 【使用方法】

### 启用 OPD
在训练脚本中配置 `RM_ARGS`：
```bash
RM_ARGS=(
   --custom-rm-path examples.on_policy_distillation.on_policy_distillation.reward_func
   --custom-reward-post-process-path examples.on_policy_distillation.on_policy_distillation.post_process_rewards
   --rm-url http://$TEACHER_IP:$TEACHER_PORT/generate
)
```
然后通过 `ray job submit ... -- python3 train.py ${RM_ARGS[@]}` 提交任务。可参考 `run-glm4.7-30B-opd.sh`。

### 启用 TIS
在 `GRPO_ARGS` 中开启：
```bash
GRPO_ARGS=(
   --use-tis
   --grpo-clip 0.2
   ...
)
```

### 启用 MOE Routing Replay
在 `SGLANG_ARGS` 中加入：
```bash
SGLANG_ARGS=(
   --use-rollout-routing-replay
   ...
)
```
**注意**：当前 sglang-router 0.3.2 存在已知 Bug，建议访问 sgl-router 仓库获取最新 release 或源码安装。

### 启用 Context Parallel
在训练脚本中同时配置 rollout 长度限制与 Megatron CP 参数：
```bash
ROLLOUT_ARGS=(
   --rollout-max-response-len $((1024 * 32))   # 最大回复长度
   --rollout-max-prompt-len $((1024 * 128))    # 最大输入长度
   ...
)

PERF_ARGS=(
   --context-parallel-algo megatron_cp_algo
   --context-parallel-size 4
   ...
)
```

### 启用 Retool
```bash
CUSTOM_ARGS=(
   --custom-generate-function-path generate_with_retool.generate
   --custom-rm-path generate_with_retool.reward_func
)

ROLLOUT_ARGS=(
   ... # 原有其他 ROLLOUT 参数
   # 注意：此处需要删除 --apply-chat-template
)
```
可参考 `retool_glm4.7_flash_rl_npu.sh`。

---

> **忠实性说明**：本文档解读严格遵循原文表述，未补充任何原文未出现的性能数字、机制细节或外部知识；标题 "MOE Routing Reply" 与命令行 `--use-rollout-routing-replay` 之间的不一致，按原文照实呈现。
