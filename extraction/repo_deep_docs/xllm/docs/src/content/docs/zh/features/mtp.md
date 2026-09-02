# ... 其他配置相同

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/mtp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/mtp.md

# MTP 投机推理 — 一体化深度解读

## 【定位】

本文档系统介绍 xllm 推理引擎中 **MTP（Multi-Token Prediction）投机推理** 能力：从 MTP 训练设计原理（用于推理阶段加速）、功能优势（draft 生成 + 批量验证）、支持的模型结构（DeepSeek‑V3/V3.2/R1、GLM4 MoE）、MTP 模型导出流程（`tools/export_mtp.py`）、xllm 服务启动方式，到 sharegpt 数据集上的端到端性能基准——是一篇面向"如何为 LLM 服务开启 MTP 投机解码加速"的端到端使用与验证手册。

---

## 【技术要点】

1. **投机推理范式**：MTP 在推理阶段先以**低成本结构生成多个草稿 token**，再交由**主模型一次前向批量验证**，将原本串行的自回归过程转化为"draft → verify"双阶段流水，这是 xllm 显著提速的根本机制。
2. **相比 Eagle/Medusa 的关键差异**：原文明确点出 MTP 的核心优势是"**预训练阶段就优化了草稿生成能力**"，从而解决了 Eagle、Medusa 等**训练后外挂 draft 模块导致采样率（acceptance rate）偏低**的痛点 → 草稿 token 命中率更高 → 主模型验证负担更小。
3. **加速 / 质量平衡**：MTP 文档定位为"**平衡推理效率与输出质量**"——即在不引入额外采样偏差的前提下获得加速，无明显劣化的产出质量描述。
4. **支持模型的导出 schema**（输入/输出 `model_type` 映射，源自原文）：
   | 源模型 | 输入 model_type | 输出 MTP model_type |
   |---|---|---|
   | DeepSeek-V3 | `deepseek_v3` | `deepseek_v3_mtp` |
   | DeepSeek-R1 | `deepseek_v3` | `deepseek_v3_mtp` |
   | DeepSeek-V3.2 | `deepseek_v3`（可由 `index_head_dim` 等字段自动识别）| `deepseek_v32_mtp` |
   | GLM4 MoE（GLM-4.5-Air） | — | `glm4_moe_mtp` |
5. **xllm 启动必填项**：必须同时声明 `--model $MODEL_PATH`（主模型）与 `--draft_model $DRAFT_MODEL_PATH`（MTP 草稿模型），并通过 `--num_speculative_tokens` 控制投机步数（示例取值为 `1`）。
6. **配套调度/内存参数**（原文示例 DeepSeek‑V3/V3.2/R1 启动脚本中给出）：`--max_memory_utilization=0.90`、`--max_tokens_per_batch=10000`、`--max_seqs_per_batch=256`、`--block_size=128`、`--ep_size=1`、`--dp_size=1`、`--enable_prefix_cache=false`、`--enable_chunked_prefill=false`，多节点并行时叠加 `--master_node_addr`、`--nnodes`、`--node_rank`。

---

## 【关键机制与数据】

**工作原理（基于原文描述还原）**
1. **预训练阶段**：MTP 结构被嵌入到模型本身训练，目标是为推理阶段提供更准的 next-token 草稿生成器（区别于 Eagle/Medusa 在训练后再插入 draft head 的做法）。
2. **推理阶段双流**：
   - **草稿流**（低成本 MTP）：快速生成若干个候选 token；
   - **验证流**（主模型）：一次性把候选 token 拼成序列做一次前向，与主模型自身分布对齐后批量接受或拒绝。
3. **收益路径**：① 草稿命中率高 → 主模型一次前向可确认多个 token → ② 自回归步数下降 → ③ TPOT 与 Output Tokens/s 改善（验证见下表）。

**性能数据（原文:**基于 sharegpt 数据集，输入长度 2500，输出长度 1500，请求总数 80**）**

为方便对照，下表给出每个并发档位下 baseline vs mtp 的**加速百分比**（基于原文原文表格数据派生，未出现原文未提供的数值）：

| Concurrency | Metric | baseline (原文) | mtp (原文) | 提升幅度（派生）|
|:-:|---|---:|---:|---:|
| 1 | Output Tokens/s | 24.20 | 35.19 | +45.4% |
| 1 | Total Tokens/s | 65.77 | 95.52 | +45.2% |
| 8 | Output Tokens/s | 110.68 | 154.46 | +39.6% |
| 8 | Total Tokens/s | 300.81 | 419.34 | +39.4% |
| 16 | Output Tokens/s | 143.81 | 201.89 | +40.4% |
| 40 | Output Tokens/s | 180.22 | 252.91 | +40.3% |
| 80 | Output Tokens/s | 192.09 | 278.07 | +44.8% |
| 80 | Mean TPOT(ms) | 180.89 | 152.19 | −15.9% |
| 80 | Mean TTFT(ms) | 2996.21 | 2163.72 | −27.8% |

- **TPOT（Time Per Output Token）**：所有并发档位 mtp 均低于 baseline，平均下降约 **15–22%**，与"多 token 一次性验证"减少每 token 的前向次数一致。
- **TTFT（Time To First Token）**：在低并发（1–20）下 mtp **略高**于 baseline（多出来的部分来自 MTP 草稿生成开销）；在 **concurrency=80** 出现明显反转（544.54→看似与原文顺序… 实际为 baseline=2996.21ms、mtp=2163.72ms，TTFT 反而下降约 **27.8%**），原文未给出原因解释。
- **吞吐**：Output Tokens/s 与 Total Tokens/s 在所有并发档位均显著提升，提升幅度集中在 **39%–46%** 区间，是该 benchmark 的核心数据结论。

> **注意**：上述加速百分比为基于原文表格内的 baseline / mtp 两行数值计算派生，原文未给出加速比的整段描述。

---

## 【表格解读】

### 表格 1 — MTP 性能基准（原文字逐字还原）

> 测试条件：**sharegpt 数据集，输入长度 2500，输出长度 1500，请求总数 80**

| method    | Concurrency | Mean TPOT(ms) | Mean TTFT(ms) | Output Tokens/s | Total Tokens/s |
|:---------:|:-----------:|:-------------:|:-------------:|:---------------:|:--------------:|
| baseline  |      1      |     40.61     |    141.80     |      24.20      |     65.77      |
| mtp       |      1      |     28.33     |    142.35     |      35.19      |     95.52      |
| baseline  |      2      |     42.69     |    178.59     |      45.16      |    122.74      |
| mtp       |      2      |     29.81     |    187.97     |      64.75      |    175.78      |
| baseline  |      4      |     46.18     |    172.34     |      79.83      |    216.96      |
| mtp       |      4      |     33.54     |    194.22     |     111.18      |    301.81      |
| baseline  |      8      |     53.16     |    181.49     |     110.68     |     300.81     |
| mtp       |      8      |     40.99     |    203.37     |     154.46     |     419.34     |
| baseline  |     16      |     68.50     |    213.89     |     143.81     |     390.84     |
| mtp       |     16      |     57.04     |    254.99     |     201.89     |     548.04     |
| baseline  |     20      |     74.72     |    228.80     |     154.77     |     420.65     |
| mtp       |     20      |     61.73     |    264.34     |     206.24     |     559.84     |
| baseline  |     40      |    119.68     |    559.32     |     180.22     |     489.80     |
| mtp       |     40      |    105.70     |    544.54     |     252.91     |     686.74     |
| baseline  |     80      |    180.89     |   2996.21     |     192.09     |     522.06     |
| mtp       |     80      |    152.19     |   2163.72     |     278.07     |     755.12     |

### 逐行 / 分组解读

- **C=1 行**：单请求孤岛状态，mtp 的 Output Tokens/s 已 **45%** 相对加速（24.20 → 35.19），但 TTFT 几近持平（141.80 → 142.35），说明单请求下 MTP 草稿生成的开销几乎抹平了它对首字延迟的优化。
- **C=2 行**：Output Tokens/s 加速比 **+43.4%**（45.16 → 64.75），Total Tokens/s +43.2%（122.74 → 175.78），TPOT 同步下降 **30%**（42.69 → 29.81），验证了"draft–verify 双阶段摊薄单 token 成本"的机理。
- **C=4 行**：吞吐量突破 100 Tokens/s（111.18）；TPOT 从 46.18 → 33.54，加速比 +38.9%。
- **C=8 行**：Total Tokens/s 接近 419（接近 420 Tokens/s 单实例吞吐门槛），可以视为中并发甜区。
- **C=16 行**：Output Tokens/s 翻倍加速已告一段落（201.89 vs 143.81，**+40.4%**），Total Tokens/s 接近 550；TTFT 出现回落到 254.99，但仍在可接受范围。
- **C=20 行**：与 C=16 接近，Total Tokens/s 接近 560，MTP 在 16–20 并发区间吞吐边际增益开始收敛。
- **C=40 行**：TTFT 同步压力显现（≈544–559 ms），TPOT 跨入 >100 ms 区间；但 mtp 仍保持 Total Tokens/s ≈ 686 vs baseline ≈ 489，加速 +40.3%。
- **C=80 行**（**最值得关注的极值**）：
  - **TTFT 出现 mirror 翻转**：baseline 2996.21 → mtp 2163.72，mtp 反而 **快 27.8%**（在低并发时 mtp TTFT 是慢的）。原文未给出机制解释，**应理解为高并发下 MTP 的 draft 阶段对调度排队产生了缓解**，使得首 token 阻塞变短。
  - **Total Tokens/s 达 755 vs baseline 522（+44.6%）**，是文档中展示的最高吞吐。
  - **TPOT 仍优于 baseline**（152.19 vs 180.89，−15.9%），但已不是最大相对增益的并发点。

### 其他表格

除上述性能表外，原文无其他参数表 / 配置项对照表（启动参数以脚本代码块形式给出，不构成 Markdown 表格）。

---

## 【公式解读】

**原文无公式**（无 LaTeX、无伪代码数学公式）。

可计算的派生量（来源仅限原表格数据，作为辅助说明，非原文给出）：

- 每请求平均出字 = 1500（原文给定）。
- 静态吞吐期望上界 ≈ `concurrency × 1000 / Mean TPOT(ms)`，与表内 Output Tokens/s 量级一致（如 C=80 时 `80 × 1000 / 180.89 ≈ 442`，与 baseline 192.09 仍存在差距，反映 batch 调度与投机验证共同决定的实际效率）。
- MTP 加速比（在每条数据对中保持稳定区间，详见上方分档位派生表）。

---

## 【关联】

依据原文末"内部链接: (无)"提示，**本文档未提供内部交叉链接**，下列关联由原文明文提及的对象归纳：

- **下游依赖（外部资源）**：
  - HuggingFace 模型：`DeepSeek-V3`、`DeepSeek-V3.2`、`DeepSeek-R1`、`GLM-4.5-Air` —— 是 MTP 导出的输入来源。
- **xllm 内部组件 / 脚本**：
  - `tools/export_mtp.py` —— 模型导出工具，自动检测模型类型，支持 `--model-type` 手动覆盖（取值 `deepseek_v3`、`deepseek_v32`、`glm4_moe`）。
  - `./xllm` —— 服务启动二进制；MTP 路径下必须配合 `--model`（主）与 `--draft_model`（草稿）两个模型路径。
- **关键运行时开关（与 MTP 共同出现于启动脚本示例）**：
  - `--num_speculative_tokens 1` —— 投机步数（文档示例值）。
  - `--ep_size` / `--dp_size` —— 专家并行 / 数据并行；示例取 1，未启用多机并行专家调度。
  - `--enable_prefix_cache=false`、`--enable_chunked_prefill=false` —— 关闭 prefix cache 与 chunked prefill（可能为该测试场景下为隔离 MTP 收益而设）。
  - `--block_size=128`、`--max_tokens_per_batch=10000`、`--max_seqs_per_batch=256` —— KV block / 批容量参数。
  - `--max_memory_utilization=0.90` —— GPU 显存水位。
- **横向参照（同类技术）**：
  - Eagle、Medusa —— 文档用作对比对象，指出 MTP 通过"预训练阶段优化"避开了它们的低采样率痛点；xllm 当前未在 MTP 文档中给出对这两者的实现入口。
- **同级特性**（同文档内共存但与 MTP 不同主题）：
  - "**JSON 对象输出**" 节（OpenAI 兼容 `response_format.type=json_object`，涉及 PD 分离 / thinking 边界 / tokenizer 稳定 token piece 要求）—— 与 MTP 文档并列，但本文档将二者放在同一 `mtp.md` 中，说明 xllm 在启用 MTP 时仍可叠加 JSON 约束。原文称："该模式支持普通生成和 MTP，也支持流式与非流式返回。" `json_schema`、正则 / 自定义 grammar、legacy Completion、C API、tool-call 标签等列入当前 MVP 限制。
- **PD 分离**（Prefill–Decode disaggregation）：JSON 节中提到 "prefill 把格式标志和 reasoning 状态传递给 decode；decode 侧先校验 prefill 产出的第一个 token 再生成后续约束 mask"。这是与 MTP 同属服务侧能力，但在本文档中只在 JSON 段提及，**未涉及 MTP + PD 分离的启动示例**。

---

## 【使用方法】

### 1. 导出 MTP 模型（原文 §使用示例 → 导出模型）

- **基础调用**：`python3 tools/export_mtp.py --input-dir <源模型目录> --output-dir <输出目录>`；脚本会自动检测模型类型。
- **覆盖检测**：当自动检测失败时使用 `--model-type` 参数，可选值（原文明示）：`deepseek_v3`（用于 V3 / R1）、`deepseek_v32`（用于 V3.2）、`glm4_moe`。
- 4 个模型分别给出的命令：
  - DeepSeek-V3：`--input-dir /path/to/DeepSeek-V3`、`--output-dir /path/to/DeepSeek-V3-mtp`
  - DeepSeek-V3.2：`--input-dir /path/to/DeepSeek-V3.2`、`--output-dir /path/to/DeepSeek-V3.2-mtp`
  - DeepSeek-R1：`--input-dir /path/to/DeepSeek-R1`、`--output-dir /path/to/DeepSeek-R1-mtp`
  - GLM4 MoE（GLM-4.5-Air）：`--input-dir /path/to/GLM-4.5-Air`、`--output-dir /path/to/GLM-4.5-Air-mtp`

> ⚠️ **同名注意（原文note 强调）**：DeepSeek‑V3 与 R1 输入 `model_type` 都为 `deepseek_v3`，导出的 MTP model_type 为 `deepseek_v3_mtp`；V3.2 仍输 `deepseek_v3`，但通过 `index_head_dim` 等字段自动识别，输出 `deepseek_v32_mtp`。

### 2. 启动推理服务（原文 §启动脚本）

**DeepSeek‑V3 / V3.2 / R1 通用示例（原文逐字保留）**：

```bash
MODEL_PATH="/models/DeepSeek-V3"
DRAFT_MODEL_PATH="/models/DeepSeek-V3-mtp"
MASTER_NODE_ADDR="127.0.0.1:42123"
START_PORT=13222
LOG_DIR="log"
NNODES=16

for (( i=0; i<$NNODES; i++ ))
do
  PORT=$((START_PORT + i))
  LOG_FILE="$LOG_DIR/node_$i.log"
  nohup ./xllm \
    --model $MODEL_PATH \
    --port $PORT \
    --master_node_addr=$MASTER_NODE_ADDR \
    --nnodes=$NNODES \
    --draft_model $DRAFT_MODEL_PATH \
    --num_speculative_tokens 1 \
    --max_memory_utilization=0.90 \
    --max_tokens_per_batch=10000 \
    --max_seqs_per_batch=256 \
    --block_size=128 \
    --ep_size=1 \
    --dp_size=1 \
    --enable_prefix_cache=false \
    --enable_chunked_prefill=false \
    --node_rank=$i > $LOG_FILE 2>&1 &
  sleep 0.5
done
```

- **关键参数语义**：
  - `--model` / `--draft_model`：分别指向**主模型**与**MTP 草稿模型**（缺一不可）。
  - `--num_speculative_tokens 1`：单次投机生成的草稿 token 数；该文档示例固定为 1。
  - `--nnodes` / `--master_node_addr` / `--node_rank`：多节点 master-worker 协调，示例 NNODES=16，端口从 13222 起递增。
  - 其他调度参数（`--max_memory_utilization=0.90`、`--max_tokens_per_batch=10000`、`--max_seqs_per_batch=256`、`--block_size=128`、`--ep_size=1`、`--dp_size=1`、`--enable_prefix_cache=false`、`--enable_chunked_prefill=false`）：参上节"关联"。

**GLM4 MoE 启动示例（原文仅给出变量，注释提示"其他配置相同"）**：

```bash
MODEL_PATH="/models/GLM-4.5-Air"
DRAFT_MODEL_PATH="/models/GLM-4.5-Air-mtp"
# ... 其他配置相同
```

### 3. MTP 与 JSON 约束叠加（原文 §JSON 对象输出）

启用 MTP 的服务可直接接受 OpenAI 兼容的 Chat Completions 请求并叠加：

```json
{ "response_format": { "type": "json_object" } }
```

- 适用：MTP 推理 + 流式 / 非流式返回。
- 要求：模型 tokenizer 必须能提供构建 grammar 所需的稳定 token piece，否则请求会被拒绝；启用 reasoning 的模型还需 tokenizer 能编码已有的 `</think>` 边界。
- 当前 MVP 边界：仅支持 `json_object`；**不支持** `json_schema`、正则 / 自定义 grammar、legacy Completion、C API、tool-call 结构化标签。
- 与 PD 分离联动：开启 PD 分离时 prefill 把格式标志与 reasoning 状态传递给 decode；decode 侧先提交并校验 prefill 的第一个 token，再构造后续 token 的约束 mask。MTP 与 PD 分离的官方启动组合示例 **原文未涉及**。

### 4. 验证已启用 MTP 的客观指标

利用性能数据节的 sharegpt 基准（输入 2500 / 输出 1500 / 80 请求），可逐并发档位比对 Output Tokens/s、Total Tokens/s、Mean TPOT、Mean TTFT 四个指标是否符合原文表格的相对关系（如 Total Tokens/s 出现 **+39%~+46%** 量级提升即可视为 MTP 生效）。

---

## 参考引用 / 原文未涉及事项

- 文档 sidebar order = 80，位于 xllm 文档"zh/features/"路径下，但**本摘要的内部链接表为空（原文无内部交叉链接）**。
- 文档**未提供** MTP 在 `chat-template` 中切换 thinking 行为时的 MTP 相关示例。
- 文档**未提供** `--num_speculative_tokens > 1` 的示例与数据；示例恒为 1。
- 文档**未提供** `index_head_dim` 等字段的取值规范，仅声明 V3.2 可被该字段识别。
- 文档**未提供** MTP + PD 分离的完整启动配置组合，仅在 JSON 节中描述行为约定。
