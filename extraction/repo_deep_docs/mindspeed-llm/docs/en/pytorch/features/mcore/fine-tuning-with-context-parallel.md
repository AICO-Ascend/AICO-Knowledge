# Long-Sequence Fine-Tuning

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/fine-tuning-with-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/fine-tuning-with-context-parallel.md

# 深度解读:Long-Sequence Fine-Tuning

---

## 【定位】

本篇文档聚焦"昇腾 NPU 上 LLM 的长序列微调能力":在引入 **Context Parallel (CP)** 将超长序列沿 seq 维度切分到多卡的同时,配合 **Multi-Sample Pack** 打包训练范式,通过 `--reset-position-ids` / `--reset-attention-mask` 等参数处理"样本拼接后位置不连续、注意力掩码非下三角"的问题,使 32k、131k 等长序列的指令微调成为可能。

---

## 【技术要点】

1. **数据预处理复用**:与 `Multi-Sample Pack Fine-Tuning` 共用同一种打包方式,即将多条样本首尾相连形成单个 data item,样本间用 EOD(End-Of-Document)分隔。

2. **`--reset-position-ids`**:因打包后位置 ID 不再连续,该参数以 EOD 为边界,每段独立从 0 重新编号,实现样本间位置编码的"隔离",影响 Attention 中 Q/K 的 position encoding。

3. **`--reset-attention-mask`**:同上,attention mask 不再是简单下三角;系统按 EOD 划句界并生成 `actual-seq-len`,传给 FA 算子生成 **jagged(锯齿状) mask**,再以 TND 格式做计算。

4. **`--context-parallel-size`**:CP 切分数,**配置的 CP size 必须能整除 seq-length**;示例中 seq-length 131072 × CP 8 即每卡 16384 tokens。

5. **`--attention-mask-type`**:支持 `causal` 与 `general` 两种。
   - `general`:从数据本身生成 attention mask(贴合 jagged 形状)。
   - `causal`:在 FA 前生成 **固定长度 2048 的压缩 mask**,性能更好、显存更省,**官方推荐**。

6. **`--context-parallel-algo`**:三选一算法——`megatron_cp_algo`、`ulysses_cp_algo`、`hybrid_cp_algo`;文档明确提示:**CP ≤ 4 时 ulysses_cp_algo 是性能更优的选择**。

7. **指令数据 / 模板**:通过 `--is-instruction-dataset` 显式声明走指令数据,`--prompt-type` 指定模型模板(模板枚举见 `templates.json`),用于让 base model 微调后更具对话性。

---

## 【关键机制与数据】

- **核心工作流**:Multi-Sample Pack 把多条短样本拼成一个长样本 → EOD 分隔 → `--reset-position-ids` 让每段位置从 0 重计,避免跨样本位置语义污染 → `--reset-attention-mask` 在 FA 算子侧产出 jagged mask → CP 沿 seq 维切分到多卡 → 注意力按 `general`/`causal` 策略在 NPU 上完成 TND 格式计算。

- **`general` vs `causal` mask 的本质差异**:原文指出,`general` 是"按数据生成 jagged mask"(语义更精确,但显存与算力开销更大);`causal` 是"在 FA 前预生成 2048 长度的压缩定长 mask"(更省、更快,推荐)。

- **性能数据(原文 Results 表)**:
  - 原文:Llama-2-7B / seq-len 32k / 分布式 2/1/4(TP/PP/CP)/ gbs 16,均使用 `general` mask + `reset-attention-mask=True`。
  - 原文:`megatron_cp_algo` → **Memory 52777 MB、Throughput 102.7 TFLOP/s/GPU**。
  - 原文:`ulysses_cp_algo` → **Memory 53681 MB、Throughput 192.3 TFLOP/s/GPU**。
  - 即在相同 32k + CP=4 配置下,**ulysses 吞吐约为 megatron 的 1.87 倍**,但显存多占用约 904 MB。

---

## 【表格解读】

**原文表格逐字还原**(Llama-2-7B,长序列微调下两种 CP 算法对比):

| Model | Sequence Length | Distributed Strategy (TP/PP/CP) | gbs | CP Type | attention-mask-type | reset-attention-mask | Memory Usage | Throughput TFLOP/s/GPU |
|:-----:|:---------------:|:-------------------------------:|:---:|:-------:|:-------------------:|:--------------------:|:------------:|:----------------------:|
| Llama-2-7B | 32k | 2/1/4 | 16 | megatron_cp_algo | general | True | 52777 | 102.7 |
| Llama-2-7B | 32k | 2/1/4 | 16 | ulysses_cp_algo | general | True | 53681 | 192.3 |

**逐行解读**:

- **行 1(megatron_cp_algo)**:32k 序列长度、TP×PP×CP = 2×1×4 = 8 卡,gbs=16;采用 general mask + reset mask;显存占用 **52777 MB**,单卡吞吐 **102.7 TFLOP/s**。这是 ring-attention 系 CP 的典型表现:显存友好、但跨步通信限制了吞吐。
- **行 2(ulysses_cp_algo)**:同样 32k / 2/1/4 / gbs=16 / general mask / reset mask;显存 **53681 MB**(略高),吞吐跃升至 **192.3 TFLOP/s**——与文档正文"**CP ≤ 4 时 ulysses_cp_algo 性能更优**"的提示一致;可以观察到 ulysses 通过 all-to-all 在 head 维切分,通信开销与 CP 阶数呈线性而非平方关系,因此在 CP=4 规模下吞吐优势显著。

---

## 【公式解读】

**原文无公式**(无 LaTeX 或伪代码形式的数学公式)。

---

## 【关联】

- **上游/数据依赖**:本特性的数据预处理直接复用 [**Multi-Sample Pack Fine-Tuning**](../../training/finetune/mcore/multi_sample_pack_finetune.md),因此 `--reset-position-ids` 与 `--reset-attention-mask` 两个参数的语义在该文档中已有更详细说明。

- **CP 算法三选一**:在 `--context-parallel-algo` 中由用户自行决定底层并行策略,各自有独立 feature 文档:
  - **megatron_cp_algo** → [ring-attention-context-parallel](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/ring-attention-context-parallel.md)(环形 attention、显存友好)
  - **ulysses_cp_algo** → [ulysses-context-parallel](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/ulysses-context-parallel.md)(head 维 all-to-all、CP 较小时吞吐占优)
  - **hybrid_cp_algo** → [hybrid-context-parallel](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/hybrid-context-parallel.md)(上述二者混合)

- **模板来源**:`--prompt-type` 的可选项由仓库 [**templates.json**](../../../../../configs/finetune/templates.json) 提供,与 SFT/微调脚本共享同一份模板配置。

---

## 【使用方法】

**数据预处理**:与 `Multi-Sample Pack Fine-Tuning` 保持一致(详见同仓相关文档)。

**最小示例命令(原文给出)**:

```shell
--seq-length 131072
--context-parallel-size 8
--context-parallel-algo megatron_cp_algo  # When CP is small (CP <= 4), using ulysses_cp_algo is a good performance choice.
--attention-mask-type general
```

**典型配置矩阵(基于原文整理)**:

- 长序列微调关键开关
  - `--is-instruction-dataset`:声明指令数据
  - `--prompt-type <id>`:选择模型对话模板(枚举见 `templates.json`)
  - `--reset-position-ids`:开启 EOD 重置位置编码
  - `--reset-attention-mask`:开启 jagged mask + TND 计算
  - `--attention-mask-type {causal|general}`:`causal` 默认且更省,`general` 更精确
  - `--context-parallel-size N`:**N 必须整除 seq-length**
  - `--context-parallel-algo {megatron_cp_algo|ulysses_cp_algo|hybrid_cp_algo}`:**CP ≤ 4 时推荐 ulysses_cp_algo**

**选择建议(原文)**:
- 想极限省显存 → `causal` mask + megatron 系算法
- 想极限吞吐(CP ≤ 4) → `general` mask + ulysses_cp_algo(原文表格:32k / CP=4 下可达 **192.3 TFLOP/s/GPU**)
- 想精度/语义对齐 jagged → `general` mask
- 极致长序列(131072)且无模板特殊需求 → 按示例默认 megatron + general
