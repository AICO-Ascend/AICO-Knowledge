# Root Mean Square Layer Normalization — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Root Mean Square Layer Normalization · arXiv:1910.07467 (NeurIPS 2019, Zhang & Sennrich)
> 公式权威源 = extraction/formulas.json（下方 $$ 内 LaTeX 直接引自该文件，索引对应原文 Eq.）。

## 核心问题
LayerNorm (Ba et al. 2016, [3]) 通过同时执行 **re-centering**（去均值 μ）与 **re-scaling**（除以标准差 σ）来稳定深层网络训练，但二者带来的计算开销随网络加深而显著放大，甚至抵消收敛加速带来的净收益。作者在 §1 用一个 GRU-RNNSearch 的对照实验（Figure 1, p.2）直观刻画了这一"加速被吞掉"的现象：以训练步数计，LayerNorm 把 loss 从 7.0 降到 5.4；但以训练**时间**计，相同 wall-clock 下只能降到 5.9——每步变贵了。M3 对 p.1 的解读亦指出该页正文即引入 Figure 1 作为"computational overhead diminishes net efficiency"的论据（M3: "the efficiency gain ... is counter-balanced by an increased computational cost per training step"），确立全文核心动机。核心追问随之而来：**LayerNorm 成功的根源究竟是 re-centering 还是 re-scaling？** 作者假设 re-centering 是可有可无的，re-scaling 不变性才是稳定激活与加速收敛的关键，据此提出 RMSNorm——仅用均方根统计量归一化，舍弃均值统计。

## 关键创新点

1. **RMSNorm：去掉 μ，只用 RMS 归一化（§4, Eq. 4）。** 给定神经元加权和与激活（feed-forward，Eq. 1）：

   $$a_i = \sum_{j=1}^m{w_{ij} x_j},\quad y_i = f\left(a_i + b_i\right),$$

   LayerNorm 计算 āᵢ = (aᵢ − μ)/σ · gᵢ，其中 μ、σ 均在层内 n 个神经元上估计（Eq. 2–3）：

   $$\bar{a}_i = \frac{a_i - \mu}{\sigma} g_i, \quad y_i = f\left(\bar{a}_i + b_i\right),$$

   $$\mu = \frac{1}{n}\sum_{i=1}^{n} a_i, \quad \sigma = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(a_i - \mu)^2}.$$

   RMSNorm 直接令（Eq. 4）：

   $$\begin{split} & \bar{a}_i = \frac{a_i}{\text{RMS}(\mathbf{a})} g_i, \quad \text{where}~~ \text{RMS}(\mathbf{a}) = \sqrt{\frac{1}{n} \sum_{i=1}^{n} a_i^2}. \end{split}$$

   即"只除 RMS、不减均值、再乘可学习 gain g、加 bias b"。当 μ=0 时 RMSNorm 与 LayerNorm 完全等价。直观上 RMSNorm 把 summed inputs 强制约束到 √n 缩放的单位球面上，使输出分布对输入/权重尺度不变。**作者明确指出**：欧氏 norm（L2-Norm，仅差 √n 因子）在层归一化中不奏效（§4，并由 Figure 2 p.6 的 L2-Norm 曲线佐证——M3 解读 L2-Norm "slowest startup, lowest final score"），假设"按输入向量大小 √n 缩放球面"对跨不同维度向量的鲁棒性是必要的——这也是 RMSNorm 区别于 WeightNorm [22] 的关键。

2. **理论：保留 re-scaling 不变性，放弃 re-centering（§4.1, Table 1）。** 取 RMSNorm 的通式（Eq. 5）：

   $$\mathbf{y} = f\left(\frac{\mathbf{Wx}}{\text{RMS}(\mathbf{a})} \odot \mathbf{g} + \mathbf{b}\right),$$

   由 RMS 的线性性质（Eq. 6）

   $$\text{RMS}(\alpha\mathbf{x}) = \alpha \text{RMS}(\mathbf{x}),$$

   权重整体缩放 W′=δW 时（Eq. 7）

   $$\small \begin{split} \mathbf{y}^\prime = f\left(\frac{\mathbf{W^{\prime}x}}{\text{RMS}(\mathbf{a}^\prime)} \odot \mathbf{g} + \mathbf{b}\right) = f\left(\frac{\delta\mathbf{Wx}}{\delta\text{RMS}(\mathbf{a})} \odot \mathbf{g} + \mathbf{b}\right) = \mathbf{y}. \end{split}$$

   输入缩放 x′=δx 同理。但若缩放只作用于**单个权重向量**，则破坏 RMS 的线性性，不变性不成立；RMSNorm 对所有 re-centering 操作均**不**不变。Table 1 系统对比 BatchNorm/WeightNorm/LayerNorm/RMSNorm/pRMSNorm 在"权重矩阵/权重向量/数据集/单样本"四个对象上的 re-scaling/re-centering 不变性。**LaTeX↔M3 双源校验**：M3 对 p.6（Figure 2）的解读概括为 "RMSNorm matches LayerNorm's re-scaling invariance while reducing compute by ~25% over LayerNorm in TensorFlow"，与 Eq. 6–7 给出的 re-scaling 不变性形式化结论一致——理论不变性 ↔ 实测同质量更快。

3. **梯度分析：隐式学习率自适应器（§4.2, Eq. 8–10）。** 反传得（Eq. 8）

   $$\small & \frac{\partial \mathcal{L}}{\partial \mathbf{b}} = \frac{\partial \mathcal{L}}{\partial \mathbf{v}}, \quad \frac{\partial \mathcal{L}}{\partial \mathbf{g}} = \frac{\partial \mathcal{L}}{\partial \mathbf{v}} \odot \frac{\mathbf{Wx}}{\text{RMS}(\mathbf{a})},$$

   ∂L/∂b、∂L/∂g 对输入和 W 的缩放**均不变**（∂L/∂g 因 Eq. 6 的线性性，且 g 的梯度正比于归一化后而非原始 summed inputs，稳定 g 的量级）。权重梯度更复杂（Eq. 9）：

   $$\small \begin{split} & \frac{\partial \mathcal{L}}{\partial \mathbf{W}} = \sum_{i=1}^n \left[\mathbf{x}^T \otimes \left(\text{diag}\left(\mathbf{g} \odot \frac{\partial \mathcal{L}}{\partial \mathbf{v}} \right) \times \mathbf{R}\right)\right]_{i}, \text{where}~~ \mathbf{R} = \frac{1}{{\text{RMS}(\mathbf{a})}} \left(\mathbf{I}-\frac{\left(\mathbf{Wx}\right)\left(\mathbf{Wx}\right)^T}{n\text{RMS}(\mathbf{a})^2}\right), \end{split}$$

   含矩阵项 R。当输入或权重缩放 δ 时 R′ = R/δ（Eq. 10）

   $$\small \begin{split} \mathbf{R}^\prime & = \frac{1}{{\delta \text{RMS}(\mathbf{a})}} \left(\mathbf{I}-\frac{\left(\mathbf{\delta Wx}\right)\left(\mathbf{\delta Wx}\right)^T}{n\delta^2 \text{RMS}(\mathbf{a})^2}\right) = \frac{1}{\delta}\mathbf{R}. \\ \end{split}$$

   代回得 ∂L/∂W **对输入缩放不变**，但对权重缩放保持**负相关**——这一负相关充当"隐式学习率适配器"，动态压住大权重范数、改善收敛。

4. **pRMSNorm：在子集上估计 RMS（§5, Figure 3 p.7）。** 假设同层神经元 iid，则 RMS 可只用前 p% 元素估计，k=⌈n·p⌉。由于线性性 Eq. 6 仍成立，pRMSNorm 继承 RMSNorm 全部不变性（Table 1）。理论上是 RMS 的有偏估计，小 m 下梯度易爆炸；实践中 p=6.25% 仍能满意收敛。Figure 3（p.7）的 M3 解读直接佐证了这一点：p 在 20–100% 区间以 10% 步长扫描，dev BLEU 几乎平直（~24，±1 BLEU），M3: "practitioners do not need to carefully tune p ... stable performance across a wide range"——这正是把"减少计算量"推到极致而几乎不付精度代价的实证依据。

5. **实证：质量与 LayerNorm 相当、7%~64% 加速（§6, Figure 2 p.6 / Figure 5 p.8 / Figure 7 p.13）。** 覆盖 RNNSearch (GRU)、Transformer、attentive reader (CNN/DailyMail)、order-embedding (COCO)、ConvPool-CNN-C (CIFAR-10)；框架覆盖 TensorFlow/PyTorch/Theano。Figure 2（p.6）的 M3 解读概括为 "RMSNorm matches LayerNorm's re-scaling invariance while reducing compute by ~25% over LayerNorm in TensorFlow"，并显示 RMSNorm 曲线取得 best final BLEU，pRMSNorm 与之相当、略慢（M3 列出 Table 2 wall-clock：Baseline 399s, LayerNorm 665s, RMSNorm 501s, pRMSNorm 493s）。Figure 5（p.8）在 attentive reader 上：M3 解读显示 BatchNorm-LSTM 在 ~25k 步前快速下降，LayerNorm/RMSNorm/pRMSNorm 在 ~50k 步收敛至 ~0.45，Baseline 最慢收敛至 ~0.48，"RMSNorm matches LayerNorm's final accuracy but converges substantially faster"。Figure 7（p.13 附录）M3 解读：WeightNorm 曲线 "converges noticeably slower and converges to a lower final BLEU than LayerNorm, RMSNorm, and pRMSNorm"，定量印证 WeightNorm 收敛慢、Test14/17=21.7/23.5 低于 (p)RMSNorm。RNN 上 LayerNorm 在 TF 中比 Baseline 慢约 67%，RMSNorm 提速尤为显著；pRMSNorm 理论更快但有时因 tensor slicing 实现不佳反而略慢。

6. **鲁棒性：异常初始化下比 LayerNorm 更稳（§6.1, Figure 4, Table 5）。** 把权重初始化中心移到 0.2 时（Figure 4, p.7），LayerNorm 极不稳定，RMSNorm 更鲁棒（二者均逊于原初始化）。Table 5 进一步支撑"re-centering 非必要"假设：RMSNorm 虽不显式归一化均值，实际均值（M@ALL=-0.73）比 Baseline（-1.60）更稳定、std（S@ALL=1.50）也被稳定到与 LayerNorm（1.51）同水平——即不归一化 μ 也能间接压住 μ 与 σ 的漂移。

7. **定位：LayerNorm 的 drop-in 替换件（§7）。** 计算简化带来的效率增益与低精度运算、GPU kernel fusion 正交，可叠加。作者明确 RMSNorm 是"对 LayerNorm 计算的简化"，而非新的归一化范式。

## 表格（原文结构化）

**Table 1 — 不同归一化方法的不变性属性（§4.1）。✓=不变，✗=相反。**

| 方法 | 权重矩阵 re-scaling | 权重矩阵 re-centering | 权重向量 re-scaling | 权重向量 re-centering | 数据集 re-scaling | 数据集 re-centering | 单样本 re-scaling | 单样本 re-centering |
|---|---|---|---|---|---|---|---|---|
| BatchNorm | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| WeightNorm | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| LayerNorm | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ |
| RMSNorm | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| pRMSNorm | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |

**Table 2 — RNNSearch (TensorFlow Nematus), WMT14 En-De（§6.1）。** Time = 每 1k 训练步秒数，p=6.25%。对应 Figure 2（p.6）收敛曲线。

| Model | Test14 BLEU | Test17 BLEU | Time |
|---|---|---|---|
| Baseline | 21.7 | 23.4 | 399±3.40s |
| LayerNorm | 22.6 | 23.6 | 665±32.5s |
| L2-Norm | 20.7 | 22.0 | 482±19.7s |
| RMSNorm | 22.4 | 23.7 | 501±11.8s (**24.7%** faster than LayerNorm) |
| pRMSNorm | 22.6 | 23.1 | 493±10.7s (**25.9%**) |

**Table 3 — RNNSearch 跨框架（§6.1）。** Th=Theano Nematus, Py=PyTorch。

| Framework/Model | Test14 | Test17 | Time (s/1k steps) |
|---|---|---|---|
| Th Baseline | 21.8 | 22.9 | 596±20.8 |
| Th LayerNorm | 22.3 | 23.8 | 988±1.10 |
| Th RMSNorm | 22.5 | 23.2 | 652±24.1 (**34.0%**) |
| Th pRMSNorm | 22.7 | 24.0 | 658±17.9 (**33.4%**) |
| Py Baseline | 22.7 | 24.7 | 427±6.50 |
| Py LayerNorm | 23.2 | 24.3 | 857±17.2 |
| Py RMSNorm | 22.9 | 24.5 | 763±16.2 (**11.0%**) |
| Py pRMSNorm | 23.2 | 24.6 | 754±36.1 (**12.0%**) |

**Table 4 — Transformer (TensorFlow, Tesla V100)（§6.1）。** 训练 300k 步，base setting [31]。

| Model | Test14 | Test17 | Time (s/1k steps) |
|---|---|---|---|
| Baseline | — | — | 210±0.23 (训练失败, BLEU=0) |
| LayerNorm | 26.6 | 27.7 | 248±1.31 |
| RMSNorm | 26.8 | 27.7 | 231±0.04 (**6.9%**) |
| pRMSNorm | 26.5 | 27.8 | 225±1.63 (**9.3%**) |

**Table 5 — RNNSearch decoder GRU hidden-to-hidden 映射的均值 M 与标准差 S（§6.1, newstest2013）。** 1-4 为 token 位置，ALL 为全位置平均。

| Model | M@1 | M@2 | M@3 | M@4 | M@ALL | S@1 | S@2 | S@3 | S@4 | S@ALL |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | -2.60 | -1.19 | -1.43 | -1.53 | -1.60 | 7.35 | 2.33 | 2.61 | 2.73 | 3.04 |
| LayerNorm | -0.43 | -0.48 | -0.50 | -0.50 | -0.51 | 1.19 | 1.51 | 1.51 | 1.51 | 1.51 |
| RMSNorm | -0.40 | -0.60 | -0.69 | -0.74 | -0.73 | 1.27 | 1.51 | 1.50 | 1.49 | 1.50 |

**Table 6 — Attentive Reader (CNN/DailyMail, Theano)（§6.2）。** Time = 每 0.1k 步秒数。对应 Figure 5（p.8）。注：BatchNorm 用 cuDNN 实现，时间不可直接对比。

| Model | Time |
|---|---|
| Baseline | 315±6.30s |
| BatchNorm-Everywhere | 348±10.5s |
| BatchNorm-LSTM | 345±11.2s |
| LayerNorm | 392±5.70s |
| RMSNorm | 333±5.20s (**15.1%**) |
| pRMSNorm | 330±5.50s (**15.8%**) |

**Table 7 — Order-Embedding (Microsoft COCO, 跨 5 个测试集平均)（§6.3）。** R@K 越高越好，Mean r 越低越好。

| Model | Cap R@1 | Cap R@5 | Cap R@10 | Cap Mean r | Img R@1 | Img R@5 | Img R@10 | Img Mean r |
|---|---|---|---|---|---|---|---|---|
| OE + Baseline | 45.8 | 79.7 | 88.8 | 5.4 | 37.6 | 73.6 | 85.8 | 7.7 |
| OE + LayerNorm | 47.9 | 79.5 | 89.2 | 5.3 | 38.4 | 74.6 | 86.7 | 7.5 |
| OE + RMSNorm | 48.7 | 79.7 | 89.5 | 5.3 | 39.0 | 74.8 | 86.3 | 7.5 |
| OE + pRMSNorm | 46.8 | 79.8 | 90.3 | 5.2 | 39.0 | 74.5 | 86.3 | 7.4 |

**Table 8 — Order-Embedding 时间（§6.3）。** 每 0.1k 步秒数。

| Model | Time |
|---|---|
| Baseline | 2.11±0.047s |
| LayerNorm | 12.02±0.191s |
| RMSNorm | 7.12±0.207s (**40.8%**) |
| pRMSNorm | 4.34±0.168s (**63.9%**) |

**Table 10 — CIFAR-10 (ConvPool-CNN-C, RTX 2080 Ti)（§6.4）。** Test error 与每 epoch 秒数。p=12.5%。

| Model | Test Error | Time |
|---|---|---|
| Baseline | 8.96% | 21±0.0s |
| BatchNorm | 8.25% | 38±0.0s |
| WeightNorm | 8.28% | 23±0.0s |
| LayerNorm | 10.49% | 39±0.4s |
| RMSNorm | 8.83% | 31±0.5s (**20.5%**) |
| pRMSNorm | 10.37% | 30±0.4s (**23.1%**) |

## 与同类对比
- **vs LayerNorm [3]**：唯一区别是去掉 μ（re-centering）。质量相当或 RMSNorm 略优；RNN 上 LayerNorm 在 TF 中比 Baseline 慢 ~67%，RMSNorm 提速 7~64%。Figure 2（p.6）M3 解读直接给出 RMSNorm 取得 "best final BLEU"。§6.4 CIFAR-10 上 LayerNorm 反而比 Baseline 测试误差高 1.53%（过拟合），RMSNorm 优于 Baseline 0.013%。
- **vs BatchNorm [12]**：BatchNorm 跨样本估计统计量，对变长序列（RNN）不友好；RMSNorm/LayerNorm 都从同层内估计，样本独立。CIFAR-10 上 BatchNorm 仍最优（8.25%），RMSNorm 8.83%。Figure 5（p.8）M3 解读亦指出 BatchNorm-LSTM 早期下降快但 LayerNorm/RMSNorm 达到更低 final error。
- **vs WeightNorm [22]**：WeightNorm 重参数化权重向量、解耦长度与方向；RMSNorm 归一化激活。WeightNorm 收敛更慢、Test14/17=21.7/23.5 低于 (p)RMSNorm（§A.1, Figure 7 p.13）。M3 对 Figure 7 的解读确认 WeightNorm "converges noticeably slower and to a lower final BLEU"。作者明确 L2-Norm（与 RMS 仅差 √n）不适用于层归一化（§4）。
- **vs L2-Norm**：Table 2 中 L2-Norm 仅 20.7/22.0，反而逊于 Baseline——Figure 2（p.6）M3 解读 L2-Norm "slowest startup, lowest final score"，印证"按 √n 缩放球面"是必要的。
- **vs 无归一化初始化方案 [36]**（Fixup 类）：[36] 仅适用于残差网络且需改全部初始化层、不易迁移到 RNN；RMSNorm 是 LayerNorm 的 drop-in 替换，普适。
- **Tensor slicing 实现**：pRMSNorm 理论更快，但 TF/PyTorch/Theano 的切片操作实现不优，有时反而略慢于 RMSNorm（§6.1）。

## 跨论文关系（→ MOC 谱系）
- **谱系定位**：归一化家族（BatchNorm → LayerNorm → **RMSNorm**）。RMSNorm 是"去均值版 LayerNorm"，把归一化的成功从 re-centering+re-scaling 缩减到 re-scaling 一项，是现代 LLM 栈的默认归一化原语。
- **[[root-family-of-normalization]]**：RMSNorm 属于"按层内统计量、样本独立"的归一化分支（与 BatchNorm 跨样本分支并列）；pRMSNorm 进一步把统计量估计从全集缩到子集（受 GroupNorm [34] 启发）。
- **[[hyper-connections]]**：残差拓扑族。RMSNorm 是现代 stack（含 hyper-connection / 残差连接变体）内部使用的归一化原语——现代 LLM 的"层间流"由残差拓扑承运，层内激活稳定由 RMSNorm 承运，二者正交可叠加（§7 明示与低精度、kernel fusion 正交）。
- **[[muon-is-scalable-for-llm-training]]**（Muon Appendix D）：Muon 指出 RMSNorm 的 gain γ **必须施加 weight decay**，否则输出 RMS 会 spike——这是与 RMSNorm 直接耦合的稳定性约束。本文 §4.2 已揭示 ∂L/∂g 正比于归一化后输入、g 量级被隐式稳定（Eq. 8），但未讨论 weight decay 对 g 的长期发散控制；Muon 的工作补上了这一缺口。
- **现代 LLM 采纳**：LLaMA、DeepSeek、Qwen 等现代 decoder LLM 普遍采用 RMSNorm 而非 LayerNorm，验证了本文"re-centering 非必要"的核心假设在大规模下成立。本文（2019, NeurIPS）是这一工程共识的理论与实证起点。
- **Transformer 适配**：§6.1 Table 4 是早期证明 RMSNorm 可替换 Transformer 中 LayerNorm（baseline 无归一化直接训练失败）的实验之一，相对 LayerNorm 提速 6.9~9.3%。

## 局限与边界
- **不不变于 re-centering**（Table 1，Eq. 7 vs Eq. 6 的对称性只对 scaling 成立）：对权重/输入的平移噪声无保护。§6.1 Figure 4（p.7）的"中心=0.2"实验显示 RMSNorm 仍比 LayerNorm 鲁棒，但二者均逊于正常初始化——re-centering 在极端初始化下并非全无价值，只是"非根本"。
- **pRMSNorm 的精度-效率权衡**：小 p（小 m）下梯度易爆炸（§5）；CIFAR-10 上 pRMSNorm 测试误差比 RMSNorm 高 1.54%（Table 10）；切片实现不优时反而更慢（§6.1）。但 Figure 3（p.7）M3 解读显示在 RNNSearch 上 p 对 BLEU 几乎不敏感——精度风险是任务/架构相关的。
- **CIFAR-10 上 LayerNorm 反效果**：Table 10 中 LayerNorm 测试误差 10.49% 劣于 Baseline 8.96%——作者承认"层归一化在图像处理上不如 BatchNorm/WeightNorm"（§6.4），RMSNorm 同样继承这一边界，仅相对 LayerNorm 改善了泛化。
- **效率增益依赖实现**：7~64% 的提速区间随框架/硬件/架构/其他组件相对成本而变（§7）；Transformer 上仅 7~9% 因序列化归一化操作少，RNN 上最显著。
- **理论解释留白**：作者自陈（§7）"未来想对 RMSNorm 成功背后的原因做更多分析"——本文给了不变性（Eq. 6–7）+ 梯度（Eq. 8–10）的形式化分析，但未给出"为何 re-scaling 足够而 re-centering 不必要"的更深层机制证明（仅在 §6.1 Table 5 给经验佐证）。
- **未讨论 γ 的长期发散**：§4.2 分析 ∂L/∂g 的短期稳定性（Eq. 8），但未涉及 weight decay 对 γ 的长期约束——这一缺口由后续 [[muon-is-scalable-for-llm-training]] Appendix D 补上。
- **评估时代局限**：实验模型规模小（RNNSearch、Transformer-base），未涉及十亿/百亿参数级；后续 LLM 的大规模采纳才是真正验证，但已超出本文范围。
