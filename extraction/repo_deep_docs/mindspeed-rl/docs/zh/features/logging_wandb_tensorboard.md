# MindSpeed RL 训练指标可视化

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/logging_wandb_tensorboard.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/logging_wandb_tensorboard.md

# MindSpeed RL 训练指标可视化 深度解读

## 【定位】

本文档说明 MindSpeed RL 如何通过 **WandB** 与 **TensorBoard** 两种可视化工具（二选一）记录并呈现强化学习训练指标，并给出对应的 yaml 配置项、启用步骤与查看方法。

## 【技术要点】

1. **二选一机制**：通过 yaml 中 `use_tensorboard` 与 `use_wandb` 同时配置时，`use_tensorboard` 不生效（即 TensorBoard 会被 WandB 覆盖）。
2. **TensorBoard 路径**：开启后，日志默认生成在**当前训练路径的 `runs` 目录**下，以 TensorBoard Event 格式记录。
3. **TensorBoard 查看命令**：`tensorboard --logdir=./runs --host=$your_host_ip`，随后浏览器访问该命令输出的 URL。
4. **WandB 前置条件**：① 注册 wandb 账号获取 API key；② 训练环境可联网；③ 在运行环境中实现「获取 wandb login key 的函数」（参考 `mindspeed_rl/utils/loggers.py` 中 `_init_wandb` 的注释示例），并通过 `export WANDB_API_KEY=$your_wandb_api_key` 设置；建议进一步做加密传输。
5. **WandB 离线降级**：若运行过程中 wandb 初始化失败，会自动切换到**离线模式**，仅在 `wandb_save_dir` 路径生成本地日志，不同步到云端；可在能联网机器上执行 `wandb sync $wandb日志保存路径` 手动同步。
6. **特殊限制**：`qwen3-30b dpo` 暂不支持 TensorBoard，必须使用 WandB 替代。
7. **WandB yaml 必填字段**：`use_wandb`、`wandb_project`、`wandb_exp_name`、`wandb_save_dir` 四个字段，开启 wandb 时均为必填。

## 【关键机制与数据】

- **TensorBoard 数据流**：训练运行时通过 PyTorch 原生 TensorBoard 能力写入 Event 文件 → 落盘到 `./runs` 目录 → 用户手动起 `tensorboard` 服务读取该目录。原文无具体性能或吞吐数据。
- **WandB 数据流**：训练运行时通过开源库 WandB 初始化 → 成功则向云端 project 上报数据并打印 project url；失败则降级为离线模式，仅在 `wandb_save_dir` 落本地日志 → 可用 `wandb sync` 后台上传。
- **降级触发条件（原文）：**「如果运行过程中 wandb 初始化失败则会默认切换到 wandb 离线模式」。
- **并发互斥规则（原文）：**「若 use_tensorboard 和 use_wandb 同时为 True，则 tensorboard 不生效」。
- **安全建议（原文）：**「出于安全考虑，建议进一步做加密传输」（针对 WANDB_API_KEY）。

## 【表格解读】

原文无表格。所有可配置字段已在「技术要点」中按 yaml 形式列出。

## 【公式解读】

原文无公式。

## 【关联】

- 与 `mindspeed_rl/utils/loggers.py` 中 `_init_wandb` 函数直接相关——文档明确建议用户**参考其中注释的实现方式**来完成 wandb 登录密钥的获取与注入。这是唯一明确的内部代码锚点。
- 与训练主流程（rl_config 配置）耦合：上述 yaml 字段全部位于 `rl_config` 字段之下，意味着可视化开关由强化学习训练配置统一管控，而非独立的 CLI 参数。
- 与 `qwen3-30b dpo` 训练流程存在特殊耦合：该特定模型/算法组合**屏蔽 TensorBoard 路径**，强制走 WandB，反映出底层日志后端可能与某些模型存在实现兼容性问题。
- 文末内部链接：原文未提供任何超链接或交叉引用。

## 【使用方法】

### TensorBoard 启用

1. 在训练 yaml 的 `rl_config` 字段下添加 `use_tensorboard: true`。
2. 启动训练，默认在当前路径 `runs/` 生成 Event 日志。
3. 终端执行 `tensorboard --logdir=./runs --host=$your_host_ip`。
4. 浏览器打开命令输出的 URL。

### WandB 启用

1. **前置准备**：
   - wandb 官网注册账号，获取 API key；
   - 确保训练环境可联网；
   - 参考 `mindspeed_rl/utils/loggers.py` 中 `_init_wandb` 注释实现获取 key 的函数；
   - 执行 `export WANDB_API_KEY=$your_wandb_api_key`（建议加密传输）。
2. **yaml 配置**（`rl_config` 字段下）：
   - `use_wandb: true`
   - `wandb_project: "The_wandb_project_name"`（必填）
   - `wandb_exp_name: "The_wandb_experiment_name"`（必填）
   - `wandb_save_dir: "Path_to_save_the_wandb_results_locally"`（必填）
3. **查看指标**：
   - 训练开始后，初始化成功会在终端打印 project url，浏览器打开即可；
   - 若联网失败，自动转离线模式，将日志拷贝至联网机器执行 `wandb sync $wandb日志保存路径` 手动同步。

### 互斥与例外

- 同时设置 `use_tensorboard: true` 与 `use_wandb: true` 时，**TensorBoard 不生效**。
- `qwen3-30b dpo` 必须使用 WandB。

## 图文联合解读

- `logging_1.PNG`: **图文联合解读：**

1) **图示内容**：TensorBoard SCALARS 视图，展示单个 Run（Mar20_11-01-19_devserver-bms-935b1807）在 Step≈10、耗时14.45min下的6张训练标量曲线，含 actor 端 pg_clipfrac/pg_loss/ppo_kl 与 GRPO 端 rewards max/mean/min；右侧为 General/Scalars 等设置面板。

2) **技术结论**：MindSpeed RL 已将 PPO（actor）与 GRPO（reward）核心训练指标实时写入 TensorBoard Event 日志，指标涵盖策略梯度裁剪比例、策略损失、KL 散度及奖励极值/均值，可在线下离线可视化监控训练动态。

3) **与文档论点的关系**：作为文档「`use_tensorboard: true` 配置生效后，可通过 `tensorboard --logdir=./runs` 查看训练指标」这一使用步骤的可视化效果实证，展示 RL 关键监控指标的呈现形式。
- `logging_4.PNG`: 图示终端日志展示wandb初始化成功的输出：登录账号、版本0.17.5、本地保存路径及红框高亮的两条URL（项目链接与单次运行链接）。这印证了文档"wandb初始化成功会打印project url"的步骤，说明训练指标已成功同步至WandB云端可视化平台，与"使用示例"中WandB段落形成图文对应。
- `logging_2.PNG`: 图示为WandB可视化面板，项目路径`mindspeed-rl-grpo`，运行名`qwen25_7b`，按"actor""grpo"两组共展示6个训练指标（ppo_kl、pg_loss、pg_clipfrac、score/min/mean/max）的Step-Value曲线。论证了MindSpeed RL可将RL训练中的actor策略指标与GRPO分组奖励评分统一上报WandB，实现一站式多指标监控。该图呼应文档论点：开启`use_wandb`并配置`wandb_project/exp_name/save_dir`后，可在云端面板直观观测RL训练全过程指标。
- `logging_3.PNG`: 1) 图为TensorBoard界面，左侧导航含Overview/Workspace/Runs等模块，运行名qwen25_7b；主面板分两组指标——grpo/rewards（min/mean/max）与response_length（min/mean/max），另含prompt_length=3，曲线沿Step轴展示GRPO训练数据。

2) 证明MindSpeed RL的TensorBoard集成可正常离线记录并渲染GRPO奖励与生成长度等多维度指标。

3) 对应文档"TensorBoard可视化训练指标效果示例"，印证`use_tensorboard:true`开启后能在`runs`目录查看指标曲线。
