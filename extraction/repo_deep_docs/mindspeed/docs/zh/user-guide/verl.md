# Verl 使用 MindSpeed 训练后端

> 仓 `mindspeed` · 路径 `docs/zh/user-guide/verl.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/user-guide/verl.md

【定位】
本篇文档解决"如何在 Verl 强化学习/训练框架中切换到 MindSpeed（昇腾大模型加速库）作为 Megatron 风格训练后端，并按需启用 MindSpeed 提供的并行维度与融合优化特性"这一问题，是 MindSpeed 作为 Verl 后端的接入指南与特性支持清单。

【技术要点】
1. **环境准备双组件**：需先安装 MindSpeed（参见 `install_guide.md`），再安装 Verl（参见 verl 官方 Ascend 教程）；当所用 CANN 版本高于 `8.3.RC1` 时，`vllm` 与 `vllm-ascend` 安装版本须 ≥ `0.9.1`。
2. **后端策略开关**：在 Verl 配置中将模型对应的 `strategy` 配置为 `megatron`，例如 `actor_rollout_ref.actor.strategy=megatron`，可在 shell 脚本或 config 配置文档中设置。
3. **MindSpeed 自定义入参透传机制**：MindSpeed 自定义参数统一通过 `override_transformer_config` 命名空间传入，格式为 `+actor_rollout_ref.actor.megatron.override_transformer_config.<key>=<value>`（`+` 为 OmegaConf/Hydra 风格的"不存在则创建"前缀，原文示例即如此书写）。
4. **FA 为前置必需项**：特性支持列表中明确标注"FA（必须开）"，对应 `use_flash_attn=True`，其余并行/融合特性均依赖此先决条件。
5. **mbridge ↔ VPP 互斥**：mbridge 暂不支持同时开启 VPP，启用 VPP 时必须先关闭 mbridge（原文："同理VPP请在未开启mbridge时使用"）。
6. **特性状态统一为 Preview**：本篇文档列举的全部 15 项特性当前均处于 Preview（预览非正式发布）状态；正式发布（Released）与开发中（Dev）状态原文未给出具体适用项。

【关键机制与数据】
- **性能数据**：原文未涉及任何基准测试结果、吞吐数据或加速比。
- **数据流/工作原理**（仅复述原文陈述的事实，不外推）：
  - Verl 训练链路通过 `actor_rollout_ref.actor.strategy=megatron` 这一个配置项，将 actor 模型的后端路由切换为 MindSpeed（Megatron 风格）实现。
  - MindSpeed 自定义配置通过 `actor_rollout_ref.actor.megatron.override_transformer_config.*` 子树统一注入，覆盖 Megatron/MindSpeed 默认 Transformer Engine 配置。
  - 并行维度配置（TP/PP/EP/ETP/CP）挂在 `actor_rollout_ref.actor.megatron.*_size` 之下；其中 CP 同时存在 `actor_rollout_ref.actor.megatron.context_parallel_size` 与 `actor_rollout_ref.actor.megatron.override_transformer_config.context_parallel_size` 两个同名参数，原文未解释二者关系。
  - 融合优化类参数（FA/SP/RMSNorm/SwiGLU/RoPE/MoE Grouped GEMM/MoE Token Permute/Unpermute、分布式优化器、重计算）均挂在 `override_transformer_config` 子树之下；其中 RoPE、SwiGLU、RMSNorm 三类融合优化需"算子类型 + 融合开关"双键联动配置（详见【表格解读】）。

【表格解读】
下表为原文"特性支持列表"逐字还原：

| 特性名称     | 配置参数                                                     | 状态    |
| ------------ | ------------------------------------------------------------ | ------- |
| FA（必须开） | +actor_rollout_ref.actor.megatron.override_transformer_config.use_flash_attn=True | Preview |
| TP           | actor_rollout_ref.actor.megatron.tensor_model_parallel_size  | Preview |
| PP           | actor_rollout_ref.actor.megatron.pipeline_model_parallel_size | Preview |
| EP           | actor_rollout_ref.actor.megatron.expert_model_parallel_size  | Preview |
| ETP          | actor_rollout_ref.actor.megatron.expert_tensor_parallel_size | Preview |
| SP           | actor_rollout_ref.actor.megatron.override_transformer_config.sequence_parallel | Preview |
| 分布式优化器 | actor_rollout_ref.actor.megatron.override_transformer_config.use_distributed_optimizer | Preview |
| 重计算       | actor_rollout_ref.actor.megatron.override_transformer_config.recompute_method<br>actor_rollout_ref.actor.megatron.override_transformer_config.recompute_granularity<br>actor_rollout_ref.actor.megatron.override_transformer_config.recompute_num_layers | Preview |
| CP           | actor_rollout_ref.actor.megatron.context_parallel_size<br>actor_rollout_ref.actor.megatron.override_transformer_config.context_parallel_size | Preview |
| mbridge           | actor_rollout_ref.actor.megatron.use_mbridge | Preview |
| RoPE融合优化           | +actor_rollout_ref.actor.megatron.override_transformer_config.position_embedding_type=rope<br>+actor_rollout_ref.actor.megatron.override_transformer_config.use_fused_rotary_pos_emb=True | Preview |
| SwiGLU融合优化   | +actor_rollout_ref.actor.megatron.override_transformer_config.swiglu=True<br>+actor_rollout_ref.actor.megatron.override_transformer_config.use_fused_swiglu=True | Preview |
| RMSNorm融合优化  | +actor_rollout_ref.actor.megatron.override_transformer_config.normalization=RMSNorm<br>+actor_rollout_ref.actor.megatron.override_transformer_config.use_fused_rmsnorm=True | Preview |
| MoE Grouped GEMM  | +actor_rollout_ref.actor.megatron.override_transformer_config.moe_grouped_gemm=True | Preview |
| MoE Token Permute and Unpermute 融合优化  | +actor_rollout_ref.actor.megatron.override_transformer_config.use_fused_moe_token_permute_and_unpermute=True | Preview |

逐行解读：
- **FA（必须开）**：开启 FlashAttention，对应 `override_transformer_config.use_flash_attn=True`；表格中以 `+` 前缀书写，是该特性列表中**唯一**标注"必须开"的前置依赖。
- **TP**：`tensor_model_parallel_size` 张量并行度；**PP**：`pipeline_model_parallel_size` 流水线并行度；**EP**：`expert_model_parallel_size` 专家并行度（MoE 场景）；**ETP**：`expert_tensor_parallel_size` 专家张量并行度；**CP**：上下文并行度，同时存在顶层 `megatron.context_parallel_size` 与 `override_transformer_config.context_parallel_size` 两个同名参数。原文均未展开取值范围或与 TP 的耦合约束。
- **SP**：序列并行，对应 `override_transformer_config.sequence_parallel`；原文未明示其与 TP 的依赖关系。
- **分布式优化器**：`override_transformer_config.use_distributed_optimizer`，原文未解释其工作机制。
- **重计算**：三项参数联动——`recompute_method`（策略）、`recompute_granularity`（粒度）、`recompute_num_layers`（层数），原表用 `<br>` 在同一单元格内并列。
- **mbridge**：`actor_rollout_ref.actor.megatron.use_mbridge`；注意其在表外补充说明中与 VPP 互斥。
- **RoPE 融合优化**：需先设置 `position_embedding_type=rope` 指定位置编码类型，再设置 `use_fused_rotary_pos_emb=True` 启用融合实现，双键缺一不可。
- **SwiGLU 融合优化**：`swiglu=True`（启用 SwiGLU 算子）+ `use_fused_swiglu=True`（启用融合 kernel）双开关。
- **RMSNorm 融合优化**：`normalization=RMSNorm`（指定归一化类型）+ `use_fused_rmsnorm=True`（启用融合 kernel）双开关。
- **MoE Grouped GEMM**：`override_transformer_config.moe_grouped_gemm=True`，将 MoE 多个专家的 GEMM 计算合并以提升效率。
- **MoE Token Permute and Unpermute 融合优化**：`override_transformer_config.use_fused_moe_token_permute_and_unpermute=True`，对 MoE 的 token 重排与恢复过程做算子融合。

表后注：状态分为 Preview（预览非正式发布）、Released（正式发布）、Dev（开发中）；本表所列全部为 Preview。

【公式解读】
原文无公式。

【关联】
- **内部链接**：
  - [install_guide.md](install_guide.md) — MindSpeed 安装指导，是本文档"环境准备"第一步的依赖入口；本文档假定读者已先按该指引完成 MindSpeed 安装。
- **外部链接**：
  - Verl 官方 Ascend 快速上手（`https://github.com/verl-project/verl/blob/main/docs/ascend_tutorial/get_start/quick_start.rst`）— 本文档"环境准备"第二步所指，对应 Verl 框架自身的安装方法。
  - vllm-ascend 中文安装文档（`https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/latest/installation.html`）— 当 CANN 版本 > 8.3.RC1 时，确认 vllm 0.9.1 安装方法所用。
- **特性/模块间耦合关系**（原文有陈述）：
  - **FA ↔ 其余特性**：FA 标注"必须开"，是其余并行与融合特性的前置条件。
  - **mbridge ↔ VPP**：mbridge 暂不支持与 VPP 同时开启；启用 VPP 时必须未开启 mbridge。
  - **RoPE / SwiGLU / RMSNorm 融合优化**：每个融合优化由"算子类型/编码类型 + 融合实现开关"两条配置联动启用，原文以多行 `+` 参数形式给出。
  - **CP**：通过 `context_parallel_size` 与 `override_transformer_config.context_parallel_size` 两个同名键同时存在，原文未说明二者差别。
- **上下游栈关系**：Verl（上层 RL 训练框架） → `strategy=megatron` 路由 → MindSpeed（昇腾 Megatron 风格后端，含 `override_transformer_config` 透传入口） → vllm-ascend（推理侧依赖，受 CANN 版本约束）。

【使用方法】
1. **安装阶段**：
   - MindSpeed：参见 `install_guide.md`（原文"参见[MindSpeed安装指导](install_guide.md)"）。
   - Verl：参见 `https://github.com/verl-project/verl/blob/main/docs/ascend_tutorial/get_start/quick_start.rst`。
   - 若 CANN 版本 > 8.3.RC1，安装 vllm / vllm-ascend ≥ 0.9.1，安装方法见 `https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/latest/installation.html`。
2. **启用 MindSpeed 后端**：
   - 在 shell 脚本或 config 配置文档中设置 `actor_rollout_ref.actor.strategy=megatron`。
   - MindSpeed 自定义入参一律通过 `+actor_rollout_ref.actor.megatron.override_transformer_config.<key>=<value>` 形式追加。
   - **必须项**：启用 FA → `+actor_rollout_ref.actor.megatron.override_transformer_config.use_flash_attn=True`。
3. **按需启用特性**：按【表格解读】中表格的"配置参数"列原样写入配置即可：
   - 并行类：TP/PP/EP/ETP/CP 直接设对应 `actor_rollout_ref.actor.megatron.*_size`（CP 同时需要 `override_transformer_config.context_parallel_size`）；SP 通过 `override_transformer_config.sequence_parallel` 开启。
   - 优化器：`override_transformer_config.use_distributed_optimizer`。
   - 重计算：联动配置 `recompute_method` / `recompute_granularity` / `recompute_num_layers`。
   - 融合优化类（RoPE / SwiGLU / RMSNorm / MoE Grouped GEMM / MoE Token Permute and Unpermute）：按表格中给出的多键组合同时配置。
   - mbridge：`actor_rollout_ref.actor.megatron.use_mbridge`，注意不可与 VPP 同开。
4. **状态判断**：本篇列举的全部特性均为 Preview；其余状态（Released / Dev）原文未涉及具体适用项。
