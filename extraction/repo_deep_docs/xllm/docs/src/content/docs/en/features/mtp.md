# ... same other configurations

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/mtp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/mtp.md

# xllm MTP 推测式推理文档深度解读

---

## 【定位】

本文档系统性地阐述了 xllm 推理引擎中 **MTP (Multi-Token Prediction) 推测式推理** 特性:说明其作为 DeepSeek 系列与 GLM4 MoE 等模型的 draft 模型导出与部署能力,并以 ShareGPT 数据集上的基准对比数据证明其在长序列生成场景下对吞吐与延迟的优化效果。

---

## 【技术要点】

1. **预训练阶段的 Draft Token 设计**:MTP 并非推理时外挂的推测模块 (如 Eagle / Medusa),而是通过"specialized pre-training designs"将 draft token 预测能力内建到模型权重中,从根本上解决后训练 draft 模块"低 token 接受率"的痛点。

2. **Batch Verification 机制**:主模型对 MTP 生成的多个 draft tokens **并行一次性验证** (而非逐 token 处理),将传统的自回归生成转为一次"批量校验 + 多 token 接受"的过程,显著减少主模型前向次数。

3. **支持的模型与 model_type 映射**(原文):
   - DeepSeek-V3 / R1:`deepseek_v3` → `deepseek_v3_mtp`
   - DeepSeek-V3.2:`deepseek_v3` → `deepseek_v32_mtp` (可由 `index_head_dim` 字段自动识别)
   - GLM4 MoE (如 GLM-4.5-Air):`glm4_moe_mtp`

4. **Draft 模型导出工具**:`python3 tools/export_mtp.py --input-dir <原模型路径> --output-dir <MTP 模型路径> [--model-type deepseek_v3|deepseek_v32|glm4_moe]`。支持自动检测,失败时可手动指定 `--model-type`。

5. **推测推理启动核心参数**(原文命令中关键项):
   - `--draft_model $DRAFT_MODEL_PATH`:挂载 MTP draft 模型
   - `--num_speculative_tokens 1`:每个 step 推测的 token 数(示例中为 1)
   - `--max_memory_utilization=0.90`
   - `--max_tokens_per_batch=10000`
   - `--max_seqs_per_batch=256`
   - `--block_size=128`
   - `--ep_size=1` / `--dp_size=1`(专家并行 / 数据并行均为 1)
   - `--enable_prefix_cache=false` / `--enable_chunked_prefill=false`(在 MTP 场景下均关闭)
   - 分布式:`--master_node_addr`、`--nnodes=16`、`--node_rank=$i`

6. **量化基模型的 draft 导出**:原文提及存在 "Exporting a draft model from a quantized model" 流程,提示量化基模型直接导出的 draft 模型**不会自动量化**,需要导出后再单独施加量化(原文该小节被截断,完整步骤未给出)。

---

## 【关键机制与数据】

**工作原理(原文语义重建)**:

1. **预训练侧**:`export_mtp.py` 将基础模型 (如 DeepSeek-V3) 转换为带 MTP 头的 draft 模型,产物写入独立的 `--output-dir`,具备独立 `model_type`。
2. **推理侧**:`./xllm` 同时加载主模型 (`--model`) 与 draft 模型 (`--draft_model`)。MTP 生成 draft tokens → 主模型一次性并行验证这些候选 → 接受符合主模型分布的部分,实现"一次前向推进多步"。
3. **资源权衡**:MTP 通过预训练内化 draft 能力,相比 Eagle / Medusa 等后训练外挂模块,**额外计算资源更少**,因此适合资源受限部署。

**性能数据(原文:ShareGPT, input length=2500, output length=1500, total requests=80)**:

| 并发度 | Mean TPOT 降幅 | Total Tokens/s 提升 |
|:---:|:---:|:---:|
| 1 | 40.61 → 28.33 ms (-30.2%) | 65.77 → 95.52 (+45.2%) |
| 8 | 53.16 → 40.99 ms (-22.9%) | 300.81 → 419.34 (+39.4%) |
| 16 | 68.50 → 57.04 ms (-16.7%) | 390.84 → 548.04 (+40.2%) |
| 80 | 180.89 → 152.19 ms (-15.9%) | 522.06 → 755.12 (+44.7%) |

值得注意的是,TTFT 在高并发 (80) 下从 2996.21 ms 降到 2163.72 ms (-27.8%);但在中等并发 (16、20、40) 下,MTP 的 TTFT 反而略高于 baseline,反映出 draft 阶段的额外开销与主模型验证开销在不同并发区间存在动态权衡。

---

## 【表格解读】

下表为**原文逐字还原**:

| method    | Concurrency | Mean TPOT(ms) | Mean TTFT(ms) | Output Tokens/s | Total Tokens/s |
|:---------:|:-----------:|:-------------:|:-------------:|:---------------:|:--------------:|
| baseline  |      1      |     40.61     |    141.80     |      24.20      |     65.77      |
| mtp       |      1      |     28.33     |    142.35     |      35.19      |     95.52      |
| baseline  |      2      |     42.69     |    178.59     |      45.16      |    122.74      |
| mtp       |      2      |     29.81     |    187.97     |      64.75      |    175.78      |
| baseline  |      4      |     46.18     |    172.34     |      79.83      |    216.96      |
| mtp       |      4      |     33.54     |    194.22     |     111.18      |    301.81      |
| baseline  |      8      |     53.16     |    181.49     |     110.68     |    300.81      |
| mtp       |      8      |     40.99     |    203.37     |     154.46     |    419.34      |
| baseline  |     16      |     68.50     |    213.89     |     143.81     |    390.84      |
| mtp       |     16      |     57.04     |    254.99     |     201.89     |    548.04      |
| baseline  |     20      |     74.72     |    228.80     |     154.77     |    420.65      |
| mtp       |     20      |     61.73     |    264.34     |     206.24     |    559.84      |
| baseline  |     40      |    119.68     |    559.32     |     180.22     |    489.80      |
| mtp       |     40      |    105.70     |    544.54     |     252.91     |    686.74      |
| baseline  |     80      |    180.89     |   2996.21     |     192.09     |    522.06      |
| mtp       |     80      |    152.19     |   2163.72     |     278.07     |    755.12      |

**逐行解读**:

- **Concurrency = 1 (单请求)**:MTP 在 Mean TPOT 上从 40.61 ms 降到 28.33 ms,降幅 **30.2%**;Output Tokens/s 从 24.20 升至 35.19,**+45.4%**。TTFT 几乎不变 (141.80 → 142.35 ms),说明 MTP 不影响首 token 延迟,收益集中在稳态生成阶段。
- **Concurrency = 2**:TPOT 降幅约 **30.2%**,Total Tokens/s 从 122.74 升至 175.78 (+43.2%)。
- **Concurrency = 4**:TPOT 降幅约 **27.4%**,Total Tokens/s 从 216.96 升至 301.81 (+39.1%)。TTFT 略增 (+21.88 ms)。
- **Concurrency = 8**:TPOT 降幅约 **22.9%**,Total Tokens/s 从 300.81 升至 419.34 (+39.4%)。
- **Concurrency = 16**:TPOT 降幅约 **16.7%**,Total Tokens/s 从 390.84 升至 548.04 (+40.2%)。TTFT 首次明显恶化 (+41.10 ms),提示在中等并发下 draft 步骤尚未被充分摊薄。
- **Concurrency = 20**:TPOT 降幅约 **17.4%**,Total Tokens/s 从 420.65 升至 559.84 (+33.1%)。
- **Concurrency = 40**:TPOT 降幅约 **11.7%**,Total Tokens/s 从 489.80 升至 686.74 (+40.2%)。TTFT 反而优于 baseline (559.32 → 544.54 ms),主模型已被充分并行,MTP 的额外草稿开销被覆盖。
- **Concurrency = 80**:TPOT 降幅约 **15.9%**,但 **TTFT 大幅改善**(2996.21 → 2163.72 ms,**-27.8%**),Total Tokens/s 从 522.06 升至 755.12 (+44.7%)——高并发下 MTP 优势最全面。

**整体趋势**:在所有并发档位下,MTP 都带来 **40% 左右的 Total Tokens/s 提升**,且 **TPOT 持续优于 baseline**;TTFT 仅在中等并发 (4–20) 出现轻微回退。

---

## 【公式解读】

**原文无公式**。

(文档以叙述与表格形式给出机制说明,未包含任何 LaTeX 或伪代码形式的数学表达式。)

---

## 【关联】

> **内部链接**:原文文档 (en/features/mtp.md) 在文末**未提供内部链接** (用户已标注 "无")。但文档中存在以下锚点:

- 同页锚点:`#exporting-a-draft-model-from-a-quantized-model` —— 指向本页关于"量化基模型导出 draft 模型"的章节,但原文该章节内容在本文档片段中被截断(只出现 "```bash\npy" 后戛然而止)。
- 外部链接:列出了 4 个 Hugging Face 模型仓库 (DeepSeek-V3、V3.2、R1、GLM-4.5-Air),用于下载基模型后再执行 `export_mtp.py`。

**特性间隐含关系**(基于文档语义推断,严格源于原文表述):

- 与 **OpenAI-compatible Chat Completions API** 兼容:文档中嵌入了一段关于 `response_format: {"type": "json_object"}` 的说明,明确 "This mode supports ordinary generation and **MTP**, including streaming and non-streaming responses"——表明 MTP 与 JSON 约束解码在运行时层正交兼容。
- 与 **PD 分离 (Prefill-Decode 分离)** 协同:文中提到 "With PD separation enabled, the prefill instance forwards the format flag and reasoning mode to the decode instance. The decode sequence commits and validates the first token produced by prefill before building its next-token mask"——说明 MTP 在 PD 分离架构下仍可工作,且首 token 验证逻辑与 draft 模型验证是相互独立的两层校验。
- 与 **Eagle / Medusa** 等后训练 draft 模块形成对比:文档明确把 MTP 的 "high sampling accuracy" 定位为对 Eagle / Medusa "low token acceptance rates" 痛点的替代方案,但**未给出 MTP 与 Eagle/Medusa 的直接对比数据**。

---

## 【使用方法】

### 1. 导出 MTP Draft 模型

```bash
# DeepSeek-V3
python3 tools/export_mtp.py \
    --input-dir /path/to/DeepSeek-V3 \
    --output-dir /path/to/DeepSeek-V3-mtp

# DeepSeek-V3.2
python3 tools/export_mtp.py \
    --input-dir /path/to/DeepSeek-V3.2 \
    --output-dir /path/to/DeepSeek-V3.2-mtp

# DeepSeek-R1
python3 tools/export_mtp.py \
    --input-dir /path/to/DeepSeek-R1 \
    --output-dir /path/to/DeepSeek-R1-mtp

# GLM4 MoE
python3 tools/export_mtp.py \
    --input-dir /path/to/GLM-4.5-Air \
    --output-dir /path/to/GLM-4.5-Air-mtp

# 自动检测失败时手动指定
python3 tools/export_mtp.py \
    --input-dir /path/to/model \
    --output-dir /path/to/model-mtp \
    --model-type deepseek_v3   # deepseek_v3 (V3/R1) | deepseek_v32 (V3.2) | glm4_moe
```

### 2. 启动带 MTP 的推理服务

```bash
MODEL_PATH="/models/DeepSeek-V3"
DRAFT_MODEL_PATH="/models/DeepSeek-V3-mtp"
MASTER_NODE_ADDR="127.0.0.1:42123"
START_PORT=13222
LOG_DIR="log"
NNODES=16

for (( i=0; i<$NNODES; i++ )); do
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

GLM4 MoE 启动方式相同,只需替换 `MODEL_PATH` / `DRAFT_MODEL_PATH`。

### 3. 关键开关与含义

| 参数 | 示例值 | 作用(原文语义) |
|---|---|---|
| `--draft_model` | `$DRAFT_MODEL_PATH` | 挂载 MTP draft 模型 |
| `--num_speculative_tokens` | `1` | 每步推测 token 数 |
| `--max_memory_utilization` | `0.90` | KV cache 内存占比上限 |
| `--max_tokens_per_batch` | `10000` | 单 batch token 上限 |
| `--max_seqs_per_batch` | `256` | 单 batch 序列上限 |
| `--block_size` | `128` | KV cache block 大小 |
| `--ep_size` / `--dp_size` | `1` / `1` | 专家并行 / 数据并行规模 |
| `--enable_prefix_cache` | `false` | MTP 场景下禁用前缀缓存 |
| `--enable_chunked_prefill` | `false` | MTP 场景下禁用分块 prefill |

### 4. 量化基模型导出(原文片段不完整)

原文标题为 "Exporting a draft model from a quantized model",提示需要**先导出临时 draft 模型,再单独施加一次量化**,但完整命令在该文档片段中**被截断** (原文末尾仅留 "```bash\npy")。**完整步骤原文未涉及**。
