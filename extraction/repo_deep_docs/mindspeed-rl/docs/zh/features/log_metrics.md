# 日志打点指标说明

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/log_metrics.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/log_metrics.md

# 日志打点指标说明 — 一体化深度解读

## 【定位】
本文档是 mindspeed-rl 强化学习加速库的**日志打点字典/参考手册**, 系统罗列训练过程中由框架打印的所有可观测指标 (metric) 名称及其含义, 供用户在做 RL 训练 (尤其是 GRPO、PPO 算法) 时进行性能监控、瓶颈定位、训练稳定性分析与异常排查, 本身不涉及任何算法或工程实现改动。

---

## 【技术要点】

1. **指标按四大类组织**: 时间相关 (`timing/*`)、算法基本指标、GRPO 算法相关指标、PPO 算法相关指标, 覆盖了 RL 训练一次迭代中 actor、reference、critic、reward、resarding、adv 计算等多个子阶段。
2. **时间指标区分「总耗时」与「非重叠 (non_overlap) 耗时」**: 普通 `timing/xxx` 记录的是该阶段实际占用 wall-clock; 以 `timing/non_overlap_xxx` 为前缀的指标则记录不被其它并行计算掩盖的、真正阻塞主流程的时间, 用于瓶颈识别。
3. **重明/重排指标显式列出**: `timing/resharding_to_train`、`timing/resharding_to_infer` 用于观察权重在训练/推理 mode 间切换的开销, 这在 actor 既做 rollout 又做 update 的 RLHF 流程中是常见热点。
4. **吞吐 (TPS) 三档分级**: 端到端 `e2e_tps`、训练段 `update_tps`、推理段 `vllm_tps`, 便于分别评估推理引擎 (vLLM) 与训练后端的吞吐贡献。
5. **基础训练统计覆盖 batch 维度**: `global_batch_size`、`n_samples_per_prompt`、`world_size` 等使用户可结合样本级指标 (如 `actor/kl_loss`) 还原每次迭代的实际计算规模。
6. **PPO 拥有最完整的指标集**: 在 GRPO 基础上额外提供 critic 的 `vf_loss`、`vf_clipfrac`、`lr`, 以及 `advantages/returns/values` 三组统计量 (mean/max/min), 因为 PPO 训练 actor 与 critic 两套模型。

---

## 【关键机制与数据】

### 工作原理与数据流
- **一次 RL 迭代在框架视角下的主流程 (依据指标顺序还原)**:
  1. `timing/rollout` — actor 在推理 mode 下采样生成 response;
  2. `timing/old_log_p` — actor 计算当前策略对 response 的 log 概率 (旧 log p);
  3. `timing/reference_model` — reference 模型计算 log p (用于 KL 约束);
     - 其中 `timing/ref_onload` / `timing/ref_offload` 单独记录该阶段的权重重加载耗时;
  4. `timing/rule_reward` / `timing/reward_model` — 分别统计规则奖励打分与 reward model 打分耗时;
  5. `timing/adv` — 计算 advantages;
  6. `timing/resharding_to_train` — 切回训练 mode;
  7. `timing/update` — actor 反向 + 参数更新;
  8. (仅 PPO) `timing/critic_model` 计算 value、`timing/update_critic` 更新 critic, 并在期间也发生 `resharding_to_infer` 回到下一次 rollout。
  - 端到端总耗时即为 `timing/all`。
- **非重叠耗时 (`non_overlap_*`) 的意义** (原文): 表达"该任务执行时间中未被其它并行任务掩盖的部分", 用于识别串行关键路径。
- **奖励聚合语义**:
  - 原文写明 `{verifier_function}_rewards/mean` 表示"规则奖励打分的平均总奖励值", 由用户自定义 verifier 函数名作为前缀;
  - `grpo/rewards/*` 与 `critic/rewards/*` 在原文同时出现两种来源的说明: "规则奖励的 reward 统计 / 奖励模型对样本的 reward 经过归一化后的统计", 即同一指标可由 rule-based 或 model-based reward 填充, 具体取决于是否开启奖励模型。

### 性能数据
- 原文未提供任何具体性能数字/benchmark, 仅有指标定义。**无具体 perf 数据**。

---

## 【表格解读】

原文共 4 个 markdown 表格, 下面逐字还原并逐行解读。

### 表 1 — 时间相关指标说明

| 指标 | 说明 |
| --- | --- |
| `timing/all` | 一次迭代总时间 |
| `timing/update` | 一次迭代中actor model进行update耗时 |
| `timing/rollout` | 一次迭代中actor model进行rollout耗时 |
| `timing/old_log_p` | 一次迭代中actor model计算log_p耗时 |
| `timing/reference_model` | 一次迭代中reference model计算log_p耗时 |
| `timing/resharding_to_train` | 权重转到训练mode耗时 |
| `timing/resharding_to_infer` | 权重转到推理mode耗时 |
| `timing/adv` | 计算advantages耗时 |
| `timing/non_overlap_reference_model` | reference model计算log_p耗时的未被掩盖时间 |
| `timing/non_overlap_rule_reward` | rule_reward耗时的未被掩盖时间 |
| `timing/non_overlap_reward_model` | reward_model耗时的未被掩盖时间 |
| `timing/non_overlap_adv` | advantages计算耗时的未被掩盖时间 |
| `timing/rule_reward` | rule reward打分耗时 |
| `timing/reward_model` | reward model打分耗时 |
| `timing/ref_onload` | reference model计算log_p过程中, onload耗时 |
| `timing/ref_offload` | reference model计算log_p过程中, offload耗时 |
| `timing/critic_model` | 一次迭代中critic model计算values耗时 |
| `timing/update_critic` | 一次迭代中critic model进行update耗时 |

**逐行解读**:
- `timing/all` 是迭代墙钟时间的"全集", 其它所有 `timing/*` 应大致可被它"覆盖" (含并行) 或不超出它。
- `update` / `rollout` / `old_log_p` 三项共同覆盖 actor 在一次迭代中"训练→推理→前向算 log_p"的三种典型 mode 切换行为。
- `reference_model` 与 `resharding_to_train`/`resharding_to_infer` 共同说明 reference 模型与 actor 共享权重的场景, 每次进/出 ref 计算都涉及一次 mode 切换开销。
- `non_overlap_*` 一族指标 (4 项: reference / rule_reward / reward_model / adv) 与对应的普通耗时成对出现, 用以反映在流水线并行/异步执行时被其它任务遮蔽的实际有效时间。
- `ref_onload` / `ref_offload` 是 reference 模型专属的子粒度计时, 说明 reference 模型权重采用了 on/offload 机制 (典型场景是放在 device 与 host 之间搬运以节省显存)。
- `critic_model` / `update_critic` 是 PPO 专属 (GRPO 无 critic), 对应 critic 的 value 前向与参数更新。

### 表 2 — 算法基本指标说明

| 指标 | 说明 |
| --- | --- |
| `actor/entropy` | 策略熵, 表示策略的随机性或探索能力 |
| `actor/kl_loss` | kl散度, 衡量当前策略与参考策略 (如旧策略或参考模型) 之间的偏离程度 |
| `actor/pg_loss` | pg_loss, 基于优势函数的策略梯度目标函数值, 表示当前策略对提升奖励的学习能力 |
| `actor/pg_clipfrac` | actor model裁剪机制生效的比例, 反映了策略更新幅度的稳定性 |
| `actor/ppo_kl` | PPO算法的实际 KL 散度 |
| `grad_norm` | 梯度范数, 表示当前反向传播中参数梯度的整体幅度 |
| `{verifier_function}_rewards/mean` | 规则奖励打分的平均总奖励值 |
| `actor/lr` | actor model学习率, 优化器当前使用的学习率 |
| `response_length/mean` | 平均生成长度, 模型生成回复 (response) 的平均 token 数 |
| `response_length/min` | 最短生成长度, 当前 batch 中生成最短的 response 长度 |
| `response_length/max` | 最长生成长度, 当前 batch 中生成最长的 response 长度 |
| `prompt_length/mean` | 平均输入长度, 输入 prompt 的平均长度 |
| `prompt_length/max` | 最长输入长度, 当前 batch 中最长的 prompt长度 |
| `prompt_length/min` | 最短输入长度, 当前 batch 中最短的 prompt长度 |
| `global_batch_size` | 每次训练迭代所处理的总prompt数量 |
| `n_samples_per_prompt` | 每条prompt在rollout阶段生成的response数量 |
| `world_size` | 在分布式训练中集群中总的设备数量 (并行训练的总进程数) |
| `e2e_tps` | 端到端的tokens/p/s指标 |
| `update_tps` | 训练的tokens/p/s指标 |
| `vllm_tps` | 推理的tokens/p/s指标 |

**逐行解读**:
- 前 5 项 (`entropy`/`kl_loss`/`pg_loss`/`pg_clipfrac`/`ppo_kl`) 是 actor 训练的核心训练信号, 其中 `pg_clipfrac` 越大代表 PPO 裁剪越频繁, 策略更新"被夹紧"的样本越多。
- `grad_norm` 与 `actor/lr` 是训练稳定性双指标: 监控是否出现梯度爆炸/消失、学习率是否按预期衰减。
- `{verifier_function}_rewards/mean` 中的 `{verifier_function}` 是占位符, 需替换为用户实际注册到框架中的规则奖励函数名, 体现 mindspeed-rl 的 rule-based reward 可插拔设计。
- 6 项 `*_length` 指标分别对 prompt 与 response 计算 mean/min/max, 用于监控生成质量/长度截断 (如超过 max_new_tokens) 情况。
- `global_batch_size`、`n_samples_per_prompt`、`world_size` 是并行/采样配置维度: 每个 prompt 采样 `n_samples_per_prompt` 条 response, 在 `world_size` 个设备上聚合后形成一次迭代的 `global_batch_size`。
- 三档 TPS (`e2e_tps` / `update_tps` / `vllm_tps`) 区分了整体吞吐、训练段吞吐、推理 (vLLM) 段吞吐, 便于分别优化生成后端与训练后端。

### 表 3 — GRPO算法相关指标

| 指标 | 说明 |
| --- | --- |
| `grpo/score/mean` | 开启奖励模型时的reward均值 |
| `grpo/score/max` | 奖励模型及规则奖励对同一个样本的reward最大值 |
| `grpo/score/min` | 奖励模型及规则奖励对同一个样本的reward最小值 |
| `grpo/rewards/mean` | 规则奖励的reward均值; 奖励模型对样本的reward经过归一化后的均值 |
| `grpo/rewards/max` | 规则奖励的reward最大值; 奖励模型对样本的reward经过归一化后的最大值 |
| `grpo/rewards/min` | 规则奖励的reward最小值; 奖励模型对样本的reward经过归一化后的最小值 |

**逐行解读**:
- `grpo/score/*` 三项在原文被限定为"开启奖励模型时"的 reward 聚合 (mean/max/min), 因此该组指标仅在用户启用 reward model 时才有值。
- `grpo/rewards/*` 三项是规则奖励与归一化后 reward model 打分的统称, 对 GRPO 中"同 prompt 采样多条 response 后取组内相对优势"的机制至关重要。
- 与 PPO 不同, GRPO 不输出 critic 相关的 value/advantage 指标, 完全依赖 group-relative 优势。

### 表 4 — PPO算法相关指标

| 指标 | 说明 |
| --- | --- |
| `critic/lr` | critic model学习率, 优化器当前使用的学习率 |
| `critic/vf_loss` | vf_loss, 基于优势函数的策略梯度目标函数值, 表示当前策略对提升奖励的学习能力 |
| `critic/vf_clipfrac` | PPO中critic model裁剪机制生效的比例, 反映了策略更新幅度的稳定性 |
| `critic/score/mean` | 开启奖励模型时的reward均值 |
| `critic/score/max` | 奖励模型及规则奖励对同一个样本的reward最大值 |
| `critic/score/min` | 奖励模型及规则奖励对同一个样本的reward最小值 |
| `critic/rewards/mean` | 规则奖励的reward均值; 奖励模型对样本的reward经过归一化后的均值 |
| `critic/rewards/max` | 规则奖励的reward最大值; 奖励模型对样本的reward经过归一化后的最大值 |
| `critic/rewards/min` | 规则奖励的reward最小值; 奖励模型对样本的reward经过归一化后的最小值 |
| `critic/advantages/mean` | 优势值均值; 奖励模型对样本的reward经过归一化后的均值 |
| `critic/advantages/max` | 优势值最大值; 奖励模型对样本的reward经过归一化后的最大值 |
| `critic/advantages/min` | 优势值最小值; 奖励模型对样本的reward经过归一化后的最小值 |
| `critic/returns/mean` | 所有未来奖励的折扣和均值; 奖励模型对样本的reward经过归一化后的均值 |
| `critic/returns/max` | 所有未来奖励的折扣和最大值; 奖励模型对样本的reward经过归一化后的最大值 |
| `critic/returns/min` | 所有未来奖励的折扣和最小值; 奖励模型对样本的reward经过归一化后的最小值 |
| `critic/values/mean` | 当前状态下未来收益均值; 奖励模型对样本的reward经过归一化后的均值 |
| `critic/values/max` | 当前状态下未来收益均值最大值; 奖励模型对样本的reward经过归一化后的最大值 |
| `critic/values/min` | 当前状态下未来收益均值最小值; 奖励模型对样本的reward经过归一化后的最小值 |

> 注: 原文此表中 `critic/vf_clipfrac`、`critic/score/min`、`critic/rewards/min`、`critic/advantages/min` 等若干行被重复列出 (原文列表里存在复行), 上表已照原样保留。

**逐行解读**:
- `critic/lr` 与 `critic/vf_loss` 是 critic 网络的核心训练信号, 衡量 value function 与实际回报的偏差。
- `critic/vf_clipfrac` 是 PPO 中对 value 估计同样施加 clip 的产物, 用于评估 critic 是否被反复夹紧。
- `critic/score/*` 与 `critic/rewards/*` 与 GRPO 表中同名指标语义一致 (原文说明文字逐字相同), 只是命名空间归属到 critic。
- `critic/advantages/*` 即 PPO 中 $A_t$ 的 mean/max/min 统计, 与 GAE 计算直接相关。
- `critic/returns/*` 是所有未来奖励的折扣和 (即 $R_t = \sum_{t'}\gamma^{t'-t} r_{t'}$), critic 学习的目标。
- `critic/values/*` 是 critic 网络对当前状态给出的价值预测 $V(s_t)$。
- 整体上 PPO 相比 GRPO 多出了 "value/advantage/return 三套 + vf_loss + vf_clipfrac" 的完整 critic 视图, 反映两算法在 actor-critic (PPO) vs group-relative (GRPO) 上的本质差异。

---

## 【公式解读】

原文无公式 (仅有自然语言指标说明, 未出现 LaTeX 或伪代码形式的数学表达式)。

---

## 【关联】

原文末尾未提供任何内部超链接 (`(无)`), 因此仅可基于指标语义推断其上下游模块关系, 不做额外臆测:

- **actor 模型相关指标** (`timing/rollout`、`timing/update`、`timing/old_log_p`、`actor/*`、`response_length/*`) → 对应 mindspeed-rl 中 actor 的 rollout/训练子模块。
- **reference 模型相关指标** (`timing/reference_model`、`timing/ref_onload`、`timing/ref_offload`) → 对应 reference log p 计算 (KL 约束) 子模块, 与 actor 共享权重的 offload/onload 路径。
- **reward 相关指标** (`timing/rule_reward`、`timing/reward_model`、`{verifier_function}_rewards/*`、`grpo|grpo|critic/score/*`、`grpo|critic/rewards/*`) → 对应 rule-based reward 与 reward model 两个 reward 来源, 框架支持二者并存。
- **critic 模型相关指标** (`timing/critic_model`、`timing/update_critic`、`critic/*`) → 仅 PPO 算法路径启用, 与 GRPO 路径互斥。
- **重排/重切指标** (`timing/resharding_to_train`、`timing/resharding_to_infer`) → 与 actor/ref 权重在 train/infer mode 间切换的并行/流水线调度相关。
- **吞吐指标** (`e2e_tps`、`update_tps`、`vllm_tps`) → 与 vLLM 推理后端及训练后端的端到端性能监控模块对接。

(以上关系仅依据原文中指标名字与说明文本推导, 不涉及具体模块文件名/类名。)

---

## 【使用方法】

原文未涉及 (本文档仅是字典式说明, 不包含任何启用方式、配置项或命令行示例)。
