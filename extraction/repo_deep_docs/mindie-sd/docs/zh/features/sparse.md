# 稀疏

> 仓 `mindie-sd` · 路径 `docs/zh/features/sparse.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/sparse.md

# mindie-sd `sparse.md` 深度解读

## 【定位】

本文档定义了 mindie-sd（昇腾亲和的多模态加速套件）中面向 DiT 类模型推理的**稀疏注意力（sparse attention）能力**：通过 `sparse_attention` 统一接口暴露 rf_v2（RainFusion2.0）和 ada_bsa（自适应块稀疏）两种方案，以"在线生成稀疏掩码 + 硬件对齐的稀疏模式"双管齐下，**跳过 Q/K 注意力分数矩阵中冗余的 Token 对计算**，从而在昇腾 NPU 上获得端到端推理加速。

---

## 【技术要点】

1. **稀疏注意力的核心挑战二元论**：文档明确指出实现稀疏注意力必须同时解决两个问题——**"哪些计算可跳过"（稀疏掩码生成方式）**与**"跳过计算能否带来真实硬件加速"（稀疏模式是否对齐硬件计算单元）**。任何只解决一边的方案都不完整。

2. **块代表 Token 预测（rf_v2 的掩码生成策略）**：不计算完整注意力分数矩阵，而是将 Q/K 按空间形状分块，**取每块均值作为代表 Token**，通过代表 Token 间的相似度预测稀疏掩码，从源头压低掩码预测开销。

3. **空时感知 Token 重排（rf_v2 的硬件对齐策略）**：解决视频帧间"相同空间位置 Token 因光栅展平而相距很远、破坏块内自相似性"的问题，按 `[t, h, w]` 三维窗口重排 Token，使块内 Token 更相似，从而提升稀疏掩码的**命中率与硬件效率**。

4. **首帧 Sink 机制（rf_v2 的质量保障）**：类比 LLM 中的 attention sink 现象，**强制首帧 Token 参与全注意力计算**，使 RainFusion2.0 在 80% 稀疏率下仍能保持生成质量基本无损。

5. **ada_bsa 的 CDF 阈值动态估计**：通过累积分布函数（CDF）阈值动态估计稀疏块集合，**适用于需要灵活调节稀疏粒度**的场景，可作为 rf_v2 不满足模型兼容性时的备选。

6. **统一接口与硬性约束**：所有稀疏能力通过 `sparse_attention` 暴露；`block_size` 参数**当前仅支持 128**；接口**仅提供前向推理，不支持反向梯度计算**——这定义了其在训练链路中的不可用边界。

---

## 【关键机制与数据】

**工作原理与数据流**（原文叙述还原）：

- **入口**：`sparse_attention(q, k, v, head_num=24, input_layout="BNSD", sparse_type="rf_v2", sparsity=0.8)`
- **掩码生成路径**（rf_v2）：Q/K → 空间分块 → 块均值代表 Token → 代表 Token 相似度 → 稀疏掩码（不经过完整注意力矩阵计算）
- **硬件对齐路径**（rf_v2）：原始 Token → `[t, h, w]` 三维窗口重排 → 自相似性提升的块结构 → 命中率更高的稀疏模式 → 昇腾 NPU 真实加速
- **ada_bsa 路径**：CDF 阈值动态估计 → 稀疏块集合
- **质控旁路**（rf_v2）：首帧 Token 旁路直连全注意力计算

**性能数据**（原文有据可查）：
- rf_v2 在昇腾 NPU 上达到 **80% 稀疏率下 1.5–1.8× 端到端加速**
- 生成质量指标与全注意力**基本持平**
- 默认稀疏率推荐：**图像任务 0.6 起步，视频任务 0.8 起步**，根据生成质量微调

---

## 【表格解读】

原文包含一张「常用参数速查」表，**逐字还原**如下：

| 参数 | 必选 | 说明 |
|------|------|------|
| `sparse_type` | 否 | 稀疏策略：`None`（全注意力）、`"rf_v2"`、`"ada_bsa"` |
| `sparsity` | 否 | 稀疏率，取值范围 `[0, 1]`，`0` 表示不稀疏 |
| `txt_len` | 否 | 文本 Token 长度，仅在 `sparse_type="rf_v2"` 时生效 |
| `latent_shape_q` | 否 | Query 潜空间形状 `[t, h, w]`，仅在 `sparse_type="rf_v2"` 时生效 |
| `latent_shape_k` | 否 | Key 潜空间形状 `[t, h, w]`，仅在 `sparse_type="rf_v2"` 时生效 |
| `keep_sink` | 否 | 是否保留 Sink Token，仅在 `sparse_type="ada_bsa"` 时生效 |
| `keep_recent` | 否 | 是否保留 Recent Token，仅在 `sparse_type="ada_bsa"` 时生效 |
| `cdf_threshold` | 否 | CDF 阈值，仅在 `sparse_type="ada_bsa"` 时生效 |

**逐行解读**：

- **`sparse_type`**：三态开关，`None` 等价于退化为全注意力（即禁用稀疏），是用户做 A/B 对比的基准入口。
- **`sparsity`**：核心调参旋钮，`[0, 1]` 闭区间——`0` 是全注意力锚点，`1` 是极限稀疏；与文档推荐的"图像 0.6、视频 0.8 起步"经验值直接对应。
- **`txt_len`** / **`latent_shape_q`** / **`latent_shape_k`**：三者**专门服务于 rf_v2**，是空时感知重排的输入——`latent_shape_*` 告诉接口 Q/K 在 `[t, h, w]` 三维潜空间中的真实形态，`txt_len` 用于区分文本前缀 Token 与图像/视频 Token。这三个参数的存在证明了 rf_v2 不是"黑盒掩码预测"，而是需要用户显式提供几何信息才能正确重排。
- **`keep_sink`** / **`keep_recent`**：ada_bsa 专属。`keep_sink` 与 rf_v2 的"首帧 Sink 机制"在思想上同源（都是保护重要 Token 不被剪掉），但 ada_bsa 让用户自己控制开关；`keep_recent` 则暗示 ada_bsa 还会保护最近帧/最近 Token——这是 rf_v2 文档未明说、但 ada_bsa 作为通用方案具备的额外保护维度。
- **`cdf_threshold`**：ada_bsa 的核心调参旋钮，CDF 阈值决定"累积到多少概率质量就停止选块"，**与 `sparsity` 形成"目标驱动 vs 阈值驱动"的两种调参范式**——这也是文档将 ada_bsa 定位为"灵活调节稀疏粒度"的具体体现。

---

## 【公式解读】

**原文无公式**。文档未给出任何 LaTeX 数学公式或伪代码形式的量化表达式，性能数字（80% 稀疏率、1.5–1.8× 加速）均为实验观测值而非推导所得。

---

## 【关联】

- **上游技术细节 →** [`../../tech_report/RainFusion2.0.pdf`](../../tech_report/RainFusion2.0.pdf)：RainFusion2.0 的完整技术报告，包含块代表 Token 预测、空时感知重排、首帧 Sink 机制的算法细节与实验数据。本文档是其在 mindie-sd 中的接口侧摘要。
- **接口定义 →** [`core_layers.md#sparse_attention`](core_layers.md#sparse_attention)：本文档的 `常用参数速查表` 与 `调用示例` 明确指向该锚点获取**完整参数说明**——意味着本文档刻意省略了部分高级参数，把权威定义下放到 core_layers.md 中。
- **横向定位**：rf_v2 与 ada_bsa 是同一接口下的**并列方案**，文档给出明确的选型优先级——rf_v2 优先（覆盖图像和视频，1.5–1.8× 加速，质量无损），ada_bsa 仅在 rf_v2 不满足模型兼容性时备选，体现了 RainFusion2.0 在 mindie-sd 稀疏能力栈中的**旗舰地位**。

---

## 【使用方法】

**接口入口**：`from mindiesd import sparse_attention`

**最小调用模板**（视频模型，原文）：
```python
out = sparse_attention(
    q, k, v,
    head_num=24,
    input_layout="BNSD",
    sparse_type="rf_v2",
    sparsity=0.8,
    latent_shape_q=[t, h, w],
    latent_shape_k=[t, h, w],
)
```

**图像模型调用模板**（原文）：
```python
out = sparse_attention(q, k, v, head_num=24, input_layout="BNSD", sparse_type="rf_v2", sparsity=0.6)
```

**配置选型速查**（原文有据）：
- **策略选择**：`sparse_type="rf_v2"`（默认推荐） / `"ada_bsa"`（兼容性备选） / `None`（全注意力基线）
- **稀疏率起步值**：图像 `0.6`，视频 `0.8`，根据质量微调
- **硬件约束**：`block_size` 当前**仅支持 128**
- **推理方向约束**：**仅前向推理，不支持反向梯度计算**——意味着该接口**不可用于训练**，仅服务于推理加速场景
- **调试原则**：在加速比与生成质量间权衡，先小稀疏率起步，再视质量提升稀疏率
