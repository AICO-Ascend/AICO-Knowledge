# Qwen2VL/InternVL支持非均匀Sequence Parallel切分

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/unaligned_sequence_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/unaligned_sequence_parallel.md

# 「Qwen2VL/InternVL支持非均匀Sequence Parallel切分」深度解读

---

## 【定位】

这篇文档面向多模态大模型训练中的**长序列非均匀场景**，描述在 Qwen2VL 与 InternVL 系列模型上启用**非均匀（unaligned）Sequence Parallel（SP）切分**能力的开启方式与适用范围，解决传统均匀序列切分难以适配多模态变长序列的问题。

---

## 【技术要点】

1. **SP 的作用范围**：Sequence Parallel 主要作用于 TransformerLayer 内部的 **Dropout** 与 **LayerNorm** 模块，仅在 **sequence（序列）维度** 对数据进行切分。
2. **切分方式**：提供"**非均匀切分**"模式（即 unaligned SP），区别于传统的均匀切分，专门适配多模态场景下序列长度不一致的输入。
3. **支持的模型范围**：当前明确支持 **qwen2vl** 系列与 **InternVL** 系列模型。
4. **依赖的并行维度**：需要开启 **TP（Tensor Parallel，张量并行）**，SP 是建立在 TP 之上的序列维切分。
5. **启动开关（GPT_ARGS 中两个关键参数）**：
   - `--sequence-parallel`：启用 SP 功能本身；
   - `--unaligned-linear`：仅在需要非均匀 SP 时追加，控制 linear 层使用非均匀切分逻辑。
6. **入口脚本**：以 `examples/qwen2vl/finetune_qwen2vl_72b.sh` 为例进行配置（举例对象为 72B 规模的 Qwen2VL 微调脚本）。

---

## 【关键机制与数据】

- **工作原理（原文表述）**：
  > "Sequence Parallel 主要作用于 TransformerLayer 中的 Dropout 和 LayerNorm 模块，在序列维度对数据进行非均匀切分。"
  - 即 SP 不重切 attn / MLP 主权重，仅在 sequence 维度切分"无需严格权重对齐"的子模块计算与数据流，因此可以用非均匀方式处理变长 token 序列，规避多模态 pad/截断带来的浪费。
- **性能/量化数据**：原文未给出具体的加速比、显存收益或吞吐数字（文档未涉及基准测试结果）。
- **架构示意**：原文以 `sources/images/sp.png` 作为 SP 切分位置示意（图未在文本中展开描述细节）。

---

## 【表格解读】

**原文无表格。**（该文档以"问题分析 → 解决方案 → 使用方法"三段叙述为主，未包含参数表、性能对比表或配置项表。）

---

## 【公式解读】

**原文无公式。**（文档未给出 LaTeX 或伪代码形式的数学公式，未涉及具体的切分长度计算式或负载均衡表达式。）

---

## 【关联】

- **上游/同级特性**：
  - 与 **TP（Tensor Parallel）** 强耦合：必须先开 TP 才能在 sequence 维度做 SP 切分；两者共同构成长序列训练的并行基础。
  - SP 作用于 Transformer 内部的 **Dropout / LayerNorm**，因此与这些算子的分布式实现（mindspeed-mm 中的 LayerNorm/Dropout SP 通信原语）紧密关联。
- **下游/被支持模型**：
  - 明确覆盖 **Qwen2VL**（含 72B 微调脚本 `examples/qwen2vl/finetune_qwen2vl_72b.sh`）与 **InternVL** 系列，是 mindspeed-mm 多模态套件中的"长序列非均匀适配"能力。
- **典型场景关联**：多模态数据中图像块（visual tokens）与文本 token 拼接后序列长度多变，传统均匀 SP 会造成各 rank 负载不均，本特性提供解决路径。
- 文档未提供文末内部链接（原文内部链接标注为「无」）。

---

## 【使用方法】

原文给出明确启用步骤（以 Qwen2VL 72B 为示例）：

1. **修改脚本**：打开 `examples/qwen2vl/finetune_qwen2vl_72b.sh`。
2. **开启 TP**：在该脚本中启用 `TP`（张量并行）。
3. **在 `GPT_ARGS` 中追加参数**：
   ```shell
       --sequence-parallel
       # add only if unaligned SP is required
       --unaligned-linear
   ```
   - `--sequence-parallel` 为必选，启用 SP；
   - `--unaligned-linear` 仅在"需要非均匀 SP"时添加。
4. **适用范围**：InternVL 系列按相同方式在对应模型入口脚本中开启即可（原文注明"当前支持 qwen2vl、InternVL 系列模型"）。

## 图文联合解读

- `sp.png`: **1) 图示内容**：Transformer Layer 数据流，含两次子层；第一子层 LayerNorm→f→[TP区：Self Attention+Linear]→f̄→Dropout+残差⊕；第二子层 LayerNorm→f→[TP区：Linear+GeLU+Linear]→f̄→Dropout+残差⊕。`f/f̄` 标示序列切分/合并，灰色虚线框圈出 TP 区域。

**2) 技术结论**：SP 在序列维度对 LayerNorm/Dropout 前后进行切分(f)与聚合(f̄)；TP 仅作用于 Self Attention 与 Linear 内的矩阵运算，二者职责正交、互不干扰。

**3) 与文档论点关系**：印证"SP 主要作用于 Dropout 和 LayerNorm，在序列维度非均匀切分"的方案——图示精确框定 SP 介入点与 TP 边界。
