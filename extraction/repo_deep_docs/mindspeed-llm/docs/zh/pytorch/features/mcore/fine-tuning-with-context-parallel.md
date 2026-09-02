# 长序列微调

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/fine-tuning-with-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/fine-tuning-with-context-parallel.md

# 长序列微调 — 一体化深度解读

## 【定位】

本篇文档面向昇腾LLM分布式训练框架 mindspeed-llm,描述在 **MCore (Megatron-Core) 微调流程**中如何启用**长序列微调**能力——即通过 **Context Parallel (CP, 上下文并行)** 将过长的序列切分到多个设备上,并配合 **多样本 Pack**、**指令微调数据集** 与 **可重置的 position-ids / attention-mask**,实现 32k 及更长序列的 Llama2 等模型微调。简言之,文档解决的是:**长序列微调场景下如何用 CP 切分序列并正确处理打包样本的位置编码与注意力掩码**。

---

## 【技术要点】

1. **数据预处理复用多样本 Pack 流程**:数据预处理方式与"多样本 Pack 微调"一致,即把多个样本拼接为一条长序列,因此每条数据由不同样本拼接而成,位置 ID 不连续,attention mask 也不再是单纯下三角。
2. **`--is-instruction-dataset`**:指定微调使用指令微调数据集,确保模型按特定指令数据微调。
3. **`--prompt-type`**:指定模型对话模板(`templates.json` 中可选),使 base 模型具备更好对话能力。
4. **`--reset-position-ids`**:按 EOD 结尾重新生成 position-ids,使模型在每个 EOD 之后将 position-ids 从 0 重新编号,**隔离不同句子间的位置计算**,作用于 attention 中 query/key 的位置编码。
5. **`--reset-attention-mask` + `actual-seq-len`**:按 EOD 计算句子分隔位置,生成 `actual-seq-len` 传入 FlashAttention (FA) 算子,产生**锯齿状 mask**计算效果;FA 随后按 **TND 格式**计算。
6. **`--context-parallel-size`**:设置 CP 切分并行数,**要求序列长度能被该值整除**。
7. **`--attention-mask-type`**:`causal` (默认) 或 `general` 两种格式——
   - `general`:attention mask 从数据中生成;
   - `causal`:FA 前生成**压缩固定长度 (2048)** 的 mask,性能和显存均优于方案 1,**推荐使用**。
8. **`--context-parallel-algo`**:三种 CP 算法可选——`megatron_cp_algo`、`ulysses_cp_algo`、`hybrid_cp_algo`;**当 CP≤4 时,使用 `ulysses_cp_algo` 是性能不错的选择**。
9. **推荐配置示例**:`--seq-length 131072`、`--context-parallel-size 8`、`--context-parallel-algo megatron_cp_algo`、`--attention-mask-type general`。

---

## 【关键机制与数据】

**工作原理 / 数据流(原文涉及)**:

- Pack 后每条样本的 token 序列在多个样本边界处由 **EOD (End-of-Document) token** 分隔。
- `--reset-position-ids` 沿 EOD 边界将 position-ids 归零再递增,使得 attention 计算中 q/k 的位置编码只在**单个样本内部**有效,**跨样本的位置信息被隔离**,避免样本间的虚假注意力。
- `--reset-attention-mask` 在每个 EOD 截断,生成 `actual-seq-len`,FA 算子据此构建**锯齿状 (sawtooth) mask**——同一样本内呈下三角,跨样本处被切断,后按 **TND 格式**(Token-N-Dim,即按样本块归组)进行计算。
- `--attention-mask-type causal` 路径下,FA 在调用前生成**压缩固定长度 2048** 的 mask,减小 mask 的内存与计算开销。
- 序列由 `--context-parallel-size` 切分到多卡,**前提是 seq-length 能被 CP 大小整除**;CP 算法决定如何切分和通信——`megatron_cp_algo`(ring-attention 风格)、`ulysses_cp_algo`(head 维度 all-to-all)、`hybrid_cp_algo`(两者混合)。

**性能数据(原文给出)**:

- Llama2-7B / seq-len 32k / 分布式 TP2 PP1 CP4 / gbs 16 / `megatron_cp_algo` / `attention-mask-type general` / `reset-attention-mask True`:**显存 52777,吞吐 102.7 TFLOP/s/GPU**。
- Llama2-7B / seq-len 32k / 分布式 TP2 PP1 CP4 / gbs 16 / `ulysses_cp_algo` / `attention-mask-type general` / `reset-attention-mask True`:**显存 53681,吞吐 192.3 TFLOP/s/GPU**。
- 原文结论:**在 CP=4 的设定下,ulysses_cp_algo 的吞吐约为 megatron_cp_algo 的 1.87 倍 (192.3 / 102.7)**;显存开销两者接近(原文仅给出 52777 vs 53681,ulysses 略高 1.7%)。

---

## 【表格解读】

原文仅含一张性能对比表,逐字还原并解读如下:

| 模型 | 序列长度 | 分布式策略(TP/PP/CP) | gbs | CP类型 | attention-mask-type | reset-attention-mask | 显存 | 吞吐 TFLOP/s/GPU |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Llama2-7B | 32k | 2/1/4 | 16 | megatron_cp_algo | general | True | 52777 | 102.7 |
| Llama2-7B | 32k | 2/1/4 | 16 | ulysses_cp_algo | general | True | 53681 | 192.3 |

**逐行解读**:

- **第 1 行 — Llama2-7B + megatron_cp_algo**:7B 模型、32k 序列长度、TP=2 / PP=1 / CP=4、全局 batch size 16、采用 Megatron 风格的 ring-attention CP 算法、general 注意力 mask、开启 attention-mask 重置。单卡显存占用 **52777(MB,原文未标单位)**,单卡吞吐 **102.7 TFLOP/s**。
- **第 2 行 — Llama2-7B + ulysses_cp_algo**:仅 CP 类型切换为 Ulysses(head 维度 all-to-all 切分),其余配置与第 1 行完全一致。显存微增至 **53681**,而吞吐跃升至 **192.3 TFLOP/s/GPU**。
- **横向对比要点**:在 TP=2 / PP=1 / CP=4 固定条件下,**CP 算法本身是主要变量**;Ulysses 在 4 路 CP 下显著优于 Megatron-CP,验证了文档开头"**CP 较小时 (CP≤4),使用 ulysses_cp_algo 是性能不错的选择**"的结论。显存差异很小,可视为可忽略。
- **限定说明**:表头单位(MB / TFLOP·s⁻¹·GPU⁻¹)原文未在表头明示,仅以"显存"和"吞吐 TFLOP/s/GPU"出现,故解读时未引入原文未给出的单位换算。

---

## 【公式解读】

**原文无公式**(全文未出现任何数学公式或 LaTeX 表达式)。

---

## 【关联】

文档位于"长序列微调"这一特性页面,与以下模块/特性构成上下游或并列关系:

- **数据侧 — 多样本 Pack 微调(上游依赖)**
  `../../training/finetune/mcore/multi_sample_pack_finetune.md`
  本文档明确指出"数据预处理方法同 多样本 Pack 微调",即 Pack 后的"样本拼接 + EOD 边界"是触发 `--reset-position-ids` 与 `--reset-attention-mask` 的前提条件,**没有 Pack 就不需要这两组开关**,因此本页是 Pack 微调在"长序列"维度的延伸。

- **模型模板配置(配套配置)**
  `../../../../../configs/finetune/templates.json`
  `--prompt-type` 的可选值来自该 JSON 文件,决定对话模板的格式与 special token;它是微调链路中的**对话格式化层**,与 CP 计算本身正交但常同时启用。

- **CP 算法实现 — 三条具体算法文档(下游细化)**
  - `megatron_cp_algo` → `docs/zh/features/ring-attention-context-parallel.md`(ring-attention 风格)
  - `ulysses_cp_algo` → `docs/zh/features/ulysses-context-parallel.md`(head 维度切分)
  - `hybrid_cp_algo` → `docs/zh/features/hybrid-context-parallel.md`(两者混合)
  本文只负责"如何选与何时用",**算法的内部机制、显存与通信细节见对应子文档**。

- **与 MCore 微调主链路的关系**:本文路径位于 `docs/zh/pytorch/features/mcore/`,说明它绑定 MCore 后端的微调流程;非 MCore 路径或预训练路径的 CP 用法不在本文覆盖范围。

---

## 【使用方法】

### 启用步骤(原文涉及)

**Step 1 — 数据预处理**:与"多样本 Pack 微调"一致(链接见上)。

**Step 2 — 启动微调,关键参数如下表**(原文给出的参数清单逐项还原):

| 参数 | 作用 | 取值 / 说明 |
|:---|:---|:---|
| `--is-instruction-dataset` | 指定采用指令微调数据集 | flag 形式,原文未给默认值 |
| `--prompt-type` | 指定模型对话模板 | 可选值见 `configs/finetune/templates.json` |
| `--reset-position-ids` | EOD 后从 0 重新编号 position-ids | Pack 后必开,作用于 q/k 位置编码 |
| `--reset-attention-mask` | 按 EOD 生成锯齿状 mask 并输出 `actual-seq-len`,FA 按 TND 计算 | Pack 后必开 |
| `--context-parallel-size` | CP 切分数 | **seq-length 必须能被该值整除** |
| `--attention-mask-type` | `causal`(默认,生成 2048 压缩 mask,推荐) 或 `general`(从数据生成) | 二选一 |
| `--context-parallel-algo` | CP 算法 | `megatron_cp_algo` / `ulysses_cp_algo` / `hybrid_cp_algo`;**CP 较小时 (CP≤4) 推荐 `ulysses_cp_algo`** |

**Step 3 — 推荐 shell 片段(原文逐字)**:

```shell
    --seq-length 131072
    --context-parallel-size 8
    --context-parallel-algo megatron_cp_algo  # CP 较小时(CP<=4), 使用 ulysses_cp_algo 是性能不错的选择
    --attention-mask-type general
```

> 备注:原文未涉及版本依赖、显存最小需求、硬件亲和性(NPU 型号)、混合精度开关或学习率/优化器相关参数;若需更多上下文,请参考 `multi_sample_pack_finetune.md` 及三种 CP 算法的子文档。
