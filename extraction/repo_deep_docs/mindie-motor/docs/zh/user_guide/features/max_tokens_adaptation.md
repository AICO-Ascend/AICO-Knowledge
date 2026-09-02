# max_tokens 自适应

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/max_tokens_adaptation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/max_tokens_adaptation.md

# mindie-motor `max_tokens` 自适应 一体化深度解读

## 【定位】

这篇文档解决的是 **推理请求中输入 token 数 + 客户端指定的输出 token 上限可能超过模型上下文窗口** 的问题：描述 Coordinator 在路由前用模型 tokenizer 计算实际输入 token 数，并在超出上下文时按剩余空间对 `max_tokens` / `max_completion_tokens` 做"只削不增"的自动裁剪能力。

---

## 【技术要点】

1. **核心作用对象与生效范围**：作用于 `load_balance`、`round_robin`、`kv_cache_affinity` 三种调度策略；不依赖 KV Cache 亲和调度，也不要求部署 kv-conductor 服务。默认关闭，关闭时 Coordinator 不改请求，由后端推理引擎自行校验上下文。
2. **唯一开关**：在 `user_config.json` 的 `motor_coordinator_config.context_budget_mode` 取值 `"off"`（默认，不修改）/ `"on"`（按剩余上下文裁剪）。
3. **上下文上限获取优先级**：PD 分离场景自动从 Prefill、Decode 引擎的 `max_model_len` 填充 `aigw.p_max_seqlen`、`aigw.d_max_seqlen`；PD 混部等无法自动获取的场景，需在 `motor_coordinator_config.aigw` 中显式配置 `p_max_seqlen` 与 `d_max_seqlen`（Union 引擎示例均为 `114688`）。
4. **参数选择优先级（裁剪谁）**：Chat 请求含有效 `max_completion_tokens` 时只动 `max_completion_tokens`（即使同时携带 `max_tokens` 也不修改后者）；否则在 Chat 仅有 `max_tokens` 或 Completion 请求时动 `max_tokens`。**仅处理有效正整数**，非正整数会被移除并打 WARNING，不返回 400。
5. **tokenizer 加载方式**：每个 Coordinator Inference worker 启动阶段在进程内初始化 `TokenizerManager` 单例并从 `engine_config.model` 加载 tokenizer；不创建独立 tokenizer 服务进程；`hostPath` 挂载要求 Coordinator 可能调度到的每台节点都存在 `weight_mount_path` 目录。
6. **裁剪日志特征**：发生裁剪时输出 `Context budget clamped req_id=… parameter=… requested=… effective=… prompt_tokens=… max_model_len=…`；`max_model_len` 字段取 Prefill、Decode 上下文上限中的较小值；未发生裁剪则不打日志。

---

## 【关键机制与数据】

**工作原理（数据流，按原文复述）**：
1. Coordinator 收到推理请求 → 先 tokenization → 再计算实际输出上限 → 然后调度转发。Chat 请求走模型 chat template 并包含 `messages`、`tools`、`chat_template_kwargs`、`reasoning_effort` 等影响引擎输入的字段；Completion 请求支持字符串 `prompt` 与 token ID 列表两种形式。
2. 同一请求计算得到的 token ID 会在"上下文裁剪"与"KV Cache 亲和调度"之间复用，避免重复计算。

**裁剪示例（原文给的端到端算例）**：
- Prefill 最大序列长度 = `131072`，Decode 最大序列长度 = `114688`；
- 请求经 tokenizer 计算后输入 token = `100000`，客户端 `max_tokens: 20000`；
- 上下文上限 = `min(131072, 114688) = 114688`；
- 剩余上下文 = `114688 - 100000 = 14688`；
- 实际 `max_tokens = min(20000, 14688) = 14688`；
- Coordinator 将 `max_tokens` 改为 `14688` 后再调度转发。

**边界行为（原文明确的不裁剪场景）**：
- 输入 token 数 ≥ 模型上下文上限时 Coordinator 不动输出上限，由后端推理引擎返回上下文错误（**不会把 `max_tokens` 强制设为 1** 来掩盖超长输入）。
- `TokenizerManager` 无法得到有效 token ID 时，不基于估算值裁剪，保留原始输出上限交由后端校验。
- 客户端输出上限未超过剩余上下文时，不打裁剪日志，请求参数不变。
- Prefill 与 Decode 必须使用兼容 tokenizer；两端 `max_model_len` 不一致时按较小值裁剪。

**性能/数据指标**：原文未给出吞吐量、时延、显存等性能数字，仅给出 `131072 / 114688 / 100000 / 20000 / 14688` 这一组用于说明算法的示例数值。

---

## 【表格解读】

### 表 1：参数选择规则（原文逐字还原）

| 请求形式 | 参与裁剪的参数 |
|---------|---------------|
| Chat 请求包含有效的 `max_completion_tokens` | `max_completion_tokens` |
| Chat 请求未提供有效的 `max_completion_tokens`，但提供有效的 `max_tokens` | `max_tokens` |
| Completion 请求 | `max_tokens` |

**逐行解读**：
- 第 1 行：Chat 协议下 `max_completion_tokens` 是最高优先级裁剪目标，原文明确"即使 Chat 请求同时携带 `max_completion_tokens` 和 `max_tokens`，也只调整前者，不修改后者"。
- 第 2 行：仅当 `max_completion_tokens` 无效时回落到 `max_tokens`，体现了"高级参数优先"的覆盖语义。
- 第 3 行：Completion 协议只有 `max_tokens` 一个字段，因此它就是唯一裁剪对象。

### 表 2：配置项说明（原文逐字还原）

| 配置项 | 取值 | 说明 |
|-------|------|------|
| `motor_coordinator_config.context_budget_mode` | `off` | 默认值，不修改请求中的输出 token 上限 |
| `motor_coordinator_config.context_budget_mode` | `on` | 按模型剩余上下文裁剪输出 token 上限 |
| Prefill 或 Union 的 `engine_config.model` | 模型目录 | Inference worker 中 `TokenizerManager` 加载 tokenizer 的路径 |
| `motor_engine_prefill_config.engine_config.max_model_len` | 正整数 | Prefill 端最大序列长度 |
| `motor_engine_decode_config.engine_config.max_model_len` | 正整数 | Decode 端最大序列长度 |

**逐行解读**：
- 第 1–2 行：唯一开关的二值语义对照——`off` 是"完全透传"，`on` 是"按剩余上下文裁剪"。
- 第 3 行：`engine_config.model` 不仅供引擎加载模型，还被 Coordinator 用于加载与引擎一致的 tokenizer；要求 Prefill/Union 配置中的 `model` 指向 Coordinator 可访问的目录。
- 第 4–5 行：在 PD 分离场景下，这两个 `max_model_len` 会分别填入 `aigw.p_max_seqlen` / `aigw.d_max_seqlen`，作为裁剪算法的输入；两者都必须是正整数。

### 表 3：裁剪日志字段说明（原文逐字还原）

| 字段 | 说明 |
|------|------|
| `parameter` | 本次调整的请求参数 |
| `requested` | 客户端请求的输出 token 上限 |
| `effective` | Coordinator 实际转发给引擎的输出 token 上限 |
| `prompt_tokens` | Coordinator 使用模型 tokenizer 计算的输入 token 数 |
| `max_model_len` | Prefill、Decode 上下文上限中的较小值 |

**逐行解读**：
- 第 1 行：`parameter` 是 `max_tokens` 或 `max_completion_tokens`，与"参数选择规则表"对应。
- 第 2–4 行：把客户端原值与 Coordinator 实际下发值并排暴露，便于运维验证裁剪幅度；`prompt_tokens` 印证算法使用的是真实 tokenizer 计算结果而非估算。
- 第 5 行：直接告诉运维本次裁剪所采纳的上下文上限来源，便于排查 Prefill/Decode 长度不一致场景。

---

## 【公式解读】

原文给出了三行伪代码形式的计算式，**逐字保留原式**：

```text
模型上下文上限 = min(p_max_seqlen, d_max_seqlen)
剩余上下文     = 模型上下文上限 - 输入 token 数
实际输出上限   = min(客户端请求的输出上限, 剩余上下文)
```

符号含义与作用解释：
- **`p_max_seqlen`**：Prefill 引擎的上下文上限（即 `motor_engine_prefill_config.engine_config.max_model_len` 或 `motor_coordinator_config.aigw.p_max_seqlen`）。在 PD 混部中用 Union 引擎对应的 `p_max_seqlen`。
- **`d_max_seqlen`**：Decode 引擎的上下文上限（即 `motor_engine_decode_config.engine_config.max_model_len` 或 `motor_coordinator_config.aigw.d_max_seqlen`）。
- **`min(p_max_seqlen, d_max_seqlen)`**：原文规定"两者只有一个有效正整数时使用有效值；两者均有效时取较小值"，目的是保证请求同时满足 Prefill 和 Decode 实例的上下文约束。
- **输入 token 数**：Coordinator 用 `TokenizerManager` 加载的、与推理引擎同版本的 tokenizer 计算得到的 token 数；Chat 请求按 chat template 计算，Completion 请求按 `prompt` 计算；同一请求的 token ID 会在"上下文裁剪"与"KV Cache 亲和调度"间复用。
- **`min(客户端请求的输出上限, 剩余上下文)`**：体现"只削不增"——若客户端上限 ≤ 剩余上下文则透传；若超出则截到剩余上下文大小。原文补充约束："仅在客户端请求的输出 token 上限超出剩余上下文时进行裁剪，不会增大客户端指定的值"。

---

## 【关联】

- **完整配置字段**：文末内部链接 `../configuration/config_reference.md`（"全量配置参数说明"），与本特性相关的字段 `motor_coordinator_config.context_budget_mode`、`motor_coordinator_config.aigw.p_max_seqlen` / `aigw.d_max_seqlen`、`motor_engine_prefill_config.engine_config.model` / `engine_config.max_model_len`、`motor_engine_decode_config.engine_config.max_model_len`、`motor_deploy_config.weight_mount_path`、`coordinator_node_selector` 均在该参考中给出全量定义。
- **调度策略**：本功能对 `load_balance`、`round_robin`、`kv_cache_affinity` 三种 `scheduler_type` 均生效；与 KV Cache 亲和调度共享 token ID 计算结果。
- **部署形态**：覆盖 PD 分离（独立 Prefill/Decode）与 PD 混部（Union）两种部署形态，并依赖 `examples/deployer/deploy.py` 的 `weight_mount_path` 容器路径挂载机制。
- **替代路径**：不依赖 `kv-events-config` 与 `conductor_service`（kv-conductor），TokenizerManager 以单例形式内嵌在每个 Coordinator Inference worker 中。

---

## 【使用方法】

**启用方式**：在 `user_config.json` 的 `motor_coordinator_config` 中将 `context_budget_mode` 设置为 `"on"`（默认 `"off"`）。PD 分离场景下 `aigw.p_max_seqlen` / `aigw.d_max_seqlen` 会从 Prefill/Decode 的 `engine_config.max_model_len` 自动填充；PD 混部（Union）等无法自动填充的场景需在 `motor_coordinator_config.aigw` 中显式配置 `p_max_seqlen` 与 `d_max_seqlen`（Union 示例均为 `114688`）。

**最小配置示例（原文给出）**：
```json
{
  "motor_coordinator_config": {
    "context_budget_mode": "on",
    "scheduler_config": { "scheduler_type": "load_balance" }
  },
  "motor_engine_prefill_config": {
    "engine_type": "vllm",
    "engine_config": {
      "model": "/mnt/weight/your-model",
      "served_model_name": "your-model",
      "max_model_len": 131072
    }
  },
  "motor_engine_decode_config": {
    "engine_type": "vllm",
    "engine_config": {
      "model": "/mnt/weight/your-model",
      "served_model_name": "your-model",
      "max_model_len": 114688
    }
  }
}
```

**前置命令/部署要求**（原文给出）：
- 使用 `examples/deployer/deploy.py` 部署时，将 `motor_deploy_config.weight_mount_path` 配置为包含 `engine_config.model` 的宿主机目录（模型路径 `/data/weights/model-a` 时配 `"weight_mount_path": "/data/weights"`），保证 P/D（或 Union）引擎和 Coordinator 以同一容器路径挂载；Coordinator 至少需可读 tokenizer 文件，建议完整模型目录以只读方式挂载。
- Kubernetes 场景 `weight_mount_path` 走 `hostPath`，Coordinator 可能调度到的每一台节点都必须存在该宿主机路径与模型文件；若权重只存在于部分节点，需用 `coordinator_node_selector` 把 Coordinator 调度到可访问权重的节点，P/D（或 Union）引擎节点同样适用。
- 使用自定义 YAML、旧版部署产物或其他部署工具时，需在 Coordinator Pod 中显式添加与 `engine_config.model` 一致的模型目录挂载。
- 每个 Coordinator Inference worker 启动阶段会初始化进程内 `TokenizerManager` 单例并从模型目录加载 tokenizer；模型目录不可访问或 tokenizer 加载失败时，对应 Inference worker 将无法启动。

**验证命令（原文给出）**：向 Coordinator 发送一个输出上限大于模型剩余上下文的请求：
```bash
curl -X POST http://{coordinator-ip}:1025/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model",
    "messages": [{"role": "user", "content": "your-long-prompt"}],
    "max_tokens": 20000
  }'
```
发生裁剪时 Coordinator 会输出 INFO 日志（原文给出样例）：
```text
Context budget clamped req_id=<request-id> parameter=max_tokens requested=20000 effective=14688 prompt_tokens=100000 max_model_len=114688
```
若输出上限未超剩余上下文，则不打日志、参数不变。
