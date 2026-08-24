# 📊 图表素材索引（figures_index）


> 按主题分类的图表清单，含 caption + 页码 + 本地图片路径，便于技术报告快速插入与引用。

> 标 ⭐ 的图已用 MiniMax 多模态深度解读（技术解读见对应论文 MD 的 Figure [!tip]）。

共 685 张图，来自 68 篇论文；其中 ⭐658 张已深度解读。

## ⭐ 精选架构图（MiniMax 深度解读，可直接插入技术报告）

### IndexCache: Accelerating Sparse Attention via Cross-Layer In — Fig.1 (p.1)
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图为条形对比图，横轴列出5个基准（HLE、HLE w/ tools、SciCode、AIME25、IFBench），蓝/灰双柱对照 GLM-5 与 GLM-5+IndexCache：得分几乎持平（30.4/30.4、50.4/50.3、45.0/47.0、95.9/95.9、71.0/70.0），SciCode 略升，验证"性能无损"。

原文借此论证：IndexCache 跨层复用 indexer，省去 50% 索引计算，端到端仍可获约 1.2× 加速，是支撑"稀疏注意力高效化"主张的关键实验锚点，位于论文开篇以快速建立方法的可信度与价值印象。
*caption: Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50% of indexer computations while maintaining comparable performance acr… ｜ 论文 [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] ｜ arxiv 见 MD 元信息*

### IndexCache: Accelerating Sparse Attention via Cross-Layer In — Fig.2 (p.3)
![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]]
> [!tip] 【MiniMax 解读】IndexCache 架构图(Fig.2)：对比 (a) 标准 DSA（每层跑 lightning indexer）与 (b) IndexCache（加条件分支：F 层算并缓存索引到临时 buffer T_cache，S 层直接复用 T_cache 跳过 indexer）。T_cache 仅存当前索引张量、每 F 层覆写、无额外显存。利用 token 选择跨层冗余消除稳定层 indexer 计算。架构核心图。
*caption: Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning indexer at every layer. (b) IndexCache adds a single conditional branc… ｜ 论文 [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] ｜ arxiv 见 MD 元信息*

### IndexCache: Accelerating Sparse Attention via Cross-Layer In — Fig.3 (p.8)
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图3以30B模型为对象，柱状图对比DSA基线与IndexCache在两种索引粒度（1/2 indexer、1/4 indexer）下的相对加速比。(a) Prefill阶段加速随上下文长度递增：10K时1/2与1/4索引器分别为121%/127%，200K时提升至142%/**182%**；(b) Decode阶段同样呈正相关，10K为115%/124%，60K达119%/更高值。原文借此论证：IndexCache通过跨层索引复用，在更长上下文与更稀疏的索引器配置下收益放大，证明其方法在prefill/decode全流程均稳定超越DSA基线，是论文"稀疏注意力高效加速"主张的核心定量证据。
*caption: Relative speedup of IndexCache over the DSA baseline across three inference settings on the 30B model. DSA baseline is normalized to 100%.… ｜ 论文 [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] ｜ arxiv 见 MD 元信息*

### IndexCache: Accelerating Sparse Attention via Cross-Layer In — Fig.4 (p.16)
![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) 该图为30B DSA模型46层两两之间的top-k索引重叠率热力图（0–1.0）。对角线为1.0（黄色，自重叠），层间总体呈青绿色（约0.4–0.6）；红色方框按贪心搜索的1/4 IndexCache模式将约每4层划为一组，框内对角邻域明显更亮（≈0.7–1.0），表明相邻层共享索引比例显著更高。

2) 论文借此论证：跨层存在显著的索引冗余，且冗余随层距增大而衰减；1/4分块共享模式恰对应高重叠区，从而验证IndexCache"跨层复用top-k索引"的设计可行性。

3) 该图为方法链路的经验基石——先证冗余、再设计缓存复用策略，最终支撑稀疏注意力加速与质量保持之间的平衡。
*caption: Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.… ｜ 论文 [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.1 (p.2)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心结构与数据**：图示LLM输入"What will happen if Medusa meets a llama?"后，在Transformer末层Last Hidden上并行挂接3个Medusa Head，分别预测第2–4位token的Top-k（Head1: *is / ' / the*；Head2: *difficult / is / '*；Head3: *not / difficult / a*），与LM Head的Top-k（*It / I / As*）交叉组合成候选，经tree-attention并行验证，接受最长公共前缀"It is difficult"，实现单步多token输出。

**原文关键结论**：多解码头+候选验证机制将逐token自回归解码压缩为一步多token预测，配合tree-based attention实现并行校验，从而显著加速推理。

**论文作用**：作为方法总览图（Section 2开篇），贯通多头预测（2.1.1）→候选组装（2.1.2）→验证接受（2.3.1）的完整加速链路，是后续各模块的视觉导引。
*caption: MEDUSA introduces multiple heads on top of the last hidden states of the LLM, enabling the prediction of several sub- sequent tokens in parallel (Sect… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.2 (p.3)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示Medusa的树形注意力（Tree Attention）机制：左侧为候选树——根节点（Root）下挂Head1的两个token "It/I"，每个再分支出Head2的"is/./the"三选项，构成2×3共6条候选路径；右侧为对应的**Tree Mask矩阵**（8列Key对应候选序列，行对应Query），每行仅在与自身及祖先token对应的位置打勾（如查询"the"可关注"It/is/./the"），形成稀疏的因果掩码。

原文据此论证：凭借MEDUSA多头输出天然的分层预测结构，自顶向下构建候选树，可使单次前向传播**并行验证多条续写**；该稀疏掩码是Medusa推测解码管线中实现批量验证的关键组件，相较Miao等自底向上合并草稿候选的方法，更契合多头预测的分叉特性，从而在保证准确性的同时显著加速推理。
*caption: Remarkably, similar ideas have also been explored in independent works like Miao et al. (2023); Spector & Re (2023), where they follow a bottom-up app… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.3 (p.7)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig03.png]]
> [!tip] 【图文联合解读】图(a)对比Vicuna-7B/13B吞吐：基线约46/35 tok/s，MEDUSA-1加速2.18×/2.33×，MEDUSA-2均达2.83×；图(b)显示MEDUSA-2在MT-Bench 8类任务加速比介于2.58×(人文/推理)至3.62×(抽取)，编码类3.29×居中靠前。论文以此论证：多解码头并行预测可跨模型规模稳定实现>2×加速，且加速比随token可预测性提升（结构化任务>开放生成）。该图是实验链路核心证据，定量支撑"以轻量附加头显著加速LLM推理"这一中心结论。
*caption: Left: Speed comparison of baseline, MEDUSA-1 and MEDUSA-2 on Vicuna-7B/13B. MEDUSA-1 achieves more than 2× wall-time speedup compared to the baseline … ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.4 (p.8)
![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p08.png]]
> [!tip] **Main Figure Description (Figure 4):**

Figure 4 is a two-panel scatter plot evaluating tree-attention configurations for Medusa's speculative decoding.
- **Panel (a)** — Acceleration Rate (y-axis, 1.0–3.5) vs. Number of Candidate Tokens (x-axis, 0–250). Blue dots represent randomly sampled dense trees; red stars mark optimized sparse trees; a baseline "w/o Medusa" point sits at acc. rate = 1.
- **Panel (b)** — Decoding speed in tokens/s (y-axis, 60–120) vs. same candidate-token count, using identical color coding.
- **Flow:** candidate-token count → tradeoff between acceptance rate (quality) and throughput (latency).

**Key takeaway:** Sparse trees (red stars) sustain ~3.2–3.5× acceleration across token counts, while dense trees cluster lower (~2.5–3.0×). Although the acceptance rate stays stable, throughput drops sharply beyond ~150 tokens because per-step compute grows, creating a clear accuracy-vs-latency trade-off.

**Caption (verbatim):**
*Figure 4.* Effectiveness of numbers of candidate tokens for decoding introduced by trees (default number of candidate token for decoding is 1 when using KV cache). Left: The acceleration rate for randomly sampled dense tree settings (blue dots) and optimized sparse tree settings (red stars). Right: The speed (tokens/s) for both settings. The trend lines indicate that while the acceleration rate remains relatively stable for sparse trees, there is a notable decrease in speed as the candidate tokens increases.
*caption: Effectiveness of numbers of candidate tokens for decoding introduced by trees (default number of candidate token for decoding is 1 when using KV cache… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.5 (p.5)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读**

该图横轴为后验阈值（0–0.25），双纵轴分别对应**接受率（蓝，3.0–3.5）**与**生成质量分（橙，7.0–7.6）**；两条曲线沿阈值变化呈现此消彼长的趋势——蓝色接受率从约3.5单调下降并稳定在3.25–3.3，橙色质量分数在7.1–7.6间剧烈震荡，左侧另标注Greedy（★，蓝）与Rejection Sampling（●，橙）作为基准参考。

论文借此论证：**典型接受（Typical Acceptance）阈值是速度–质量的调控旋钮**——较低阈值带来更高吞吐但质量波动剧烈，过高则牺牲加速收益，因此需选取中间折中区段以同时兼顾推理加速与生成质量。

该图处于实验链路的**质量保障验证环节**，与正文"训练策略与头部数量选择"配合，证明MEDUSA在通过多解码头获得加速的同时，质量不显著劣于RS/Greedy基线，为方法有效性提供关键实证支撑。
*caption: 5… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.6 (p.15)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读（≤220字）：**

图6为MEDUSA-2在Vicuna-7B上的稀疏候选树：根节点"Once"沿4层展开共64个候选token节点，每节点为对应MEDUSA head（标签1–4）的top-k预测，数字标示预测来自哪一head。红色高亮路径"Once → itself → a → time → ."展示了一步前向即被4个头**全部正确预测**的4个未来token，直观证明多头并行解码能精准命中真实续写序列。

该图作为论文核心机制的视觉证据，将Medusa-1"tree attention + accept longest prefix"的复杂度以具体稀疏树呈现，论证Medusa-2通过放宽prefix约束、引入正确性归一化训练目标，能在保持单步多token验证的同时提升候选召回率，为后文基准加速比与消融实验提供机理支撑。
*caption: Visualization of a sparse tree setting for MEDUSA-2 Vicuna-7B. The tree has 64 nodes representing candidate tokens and a depth of 4 which indicates 4 … ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.7 (p.15)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig07.png]]
> [!tip] 【图文联合解读】**图7联合解读**

1) **核心对象与数据**：三幅子图分别对应 Vicuna-7B/13B/33B 三个目标模型，横轴为草稿 token 数 γ(1–15)，纵轴为生成速度(tokens/s)。每图对比 4 个草稿模型（Llama-68M/160M/1B、Vicuna-1B），灰色虚线标注基线速度：7B≈46 t/s、13B≈35 t/s、33B≈17.5 t/s。

2) **关键结论**：所有目标模型上推测解码均能超越基线，且存在最优 γ≈2–4。7B 上 Llama-68M 峰值约 67 t/s（≈1.46×）；13B 峰值约 54 t/s（≈1.54×）；33B 上 Vicuna-1B 峰值约 28 t/s（≈1.6×）。γ 过大后速度回落，表明过多样本因接受率下降而失效。

3) **论文作用**：作为 Appendix E 补充证据，与 Table 7（A100 roofline 分析）共同支撑 Medusa 框架的工程合理性——在硬件算力受限的 attention 计算瓶颈下，Medusa 通过并行多头预测+树状验证提升有效吞吐，验证其在 7B–33B 全规模上的实用加速效果。
*caption: Inference speed of various models using speculative decoding on MT-Bench. Baseline model speeds are presented by grey dotted lines for comparison. γ d… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.8 (p.16)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig08.png]]
> [!tip] 【图文联合解读】**Figure 8 图文联合解读**

**1）核心对象与数据**：该图以柱状图对比四个模型（Vicuna-7B、Zephyr-7B、Vicuna-13B、Vicuna-33B）在"无 Medusa"与"Medusa-2"下的吞吐（Tokens/s）。具体数值为：Vicuna-7B 由约 46 提升至约 130（**2.83×**）；Zephyr-7B 由约 42 提升至约 108（**2.66×**）；Vicuna-13B 由约 35 提升至约 98（**2.83×**）；Vicuna-33B 由约 18 提升至约 42（**2.35×**）。

**2）关键结论**：Medusa-2 在所有尺寸与家族上均带来显著加速（2.35×–2.83×），证明多解码头方案具备跨模型的通用性。但自蒸馏训练的 Zephyr-7B、Vicuna-13B/33B 加速比相对偏弱，论文据此指出"质量保留与提速"之间存在权衡——自蒸馏使分布更窄、可被预测的 token 减少，从而削弱了投机增益。

**3）在论文中的作用**：作为跨模型规模的端到端速度基准，该图支撑了"Medusa 不局限于单一基座"的可推广性结论，与猜想解码理论及训练数据/温度的分析共同构成完整实验链路中的**部署适用性证据**。
*caption: Speedup of various models with MEDUSA-2. MEDUSA-2 shows significant speed improvement over all the models, while models trained with self-distillation… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.9 (p.18)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig09.png]]
> [!tip] 【图文联合解读】**图9（Llama-7B Roofline 图）联合解读**

图9在双对数坐标上呈现六类算子的实测位置：横轴为计算强度（1–10k FLOP/Byte），纵轴为性能（10G–300T+ FLOP/s）；蓝色虚线为HBM带宽天花板（1935 GB/s），红色虚线为算力天花板（312 TFLOP/s），绿色虚线标示二者的ridge point。具体看：线性层（qkv mlp、up/gate/down，无论init/ar）密集聚集在右侧算力受限区，触及~200T FLOP/s；qk/pv注意力算子散布在左侧带宽受限斜线，qk/pv ar（解码阶段）性能最低（仅~10G–1T FLOP/s）；图中标注显示增大batch或seq_len可使qk/pv init沿带宽线向右上方攀升。

**关键结论**：LLM推理中线性层算力利用率高，而注意力（尤其解码阶段）是内存带宽瓶颈；增大batch/seq_len可显著提升注意力算力利用率。

**在论文中的作用**：为Medusa多解码头并行推测解码策略提供理论动机——通过多token一次前向，将原本处于带宽受限、算力利用率极低的qk/pv ar推向算力受限区，从而释放GPU峰值算力，构成全文加速机制的硬件层面依据。
*caption: The figure shows the relationship between FLOP/s and Operational Intensity for all benchmarked datapoints of Llama-7B operators on A100-80GB-PCIe. The… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.10 (p.18)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig10.png]]
> [!tip] 【图文联合解读】**图10解读（Llama-13B / A100-80GB-PCIe）**

图10为Roofline分析：横轴算术强度(1–10k FLOP/Byte)、纵轴实测性能(10G–>100T FLOP/s)，叠加1,935 GB/s带宽线(蓝虚)与312 TFLOP/s算力线(红虚)，绿线标记~160 FLOP/Byte的拐点。六类算子中，`up/gate/down init`与`qkv mlp init`贴近算力上限(>100T)；`up/gate/down ar`沿带宽斜线分布(1–10T)；`qk/pv ar`强度仅~1、性能<2T FLOP/s，呈典型memory-bound。

**论证结论**：prefill已逼近算力天花板，而decode阶段几乎全部受HBM带宽限制，权重加载为瓶颈。该图直接支撑Medusa核心动机——通过多解码头并行预测多token，将多次decode访存合并以提升算术强度，突破单token生成的带宽瓶颈，为论文加速框架提供硬件层定量依据。
*caption: Llama-13B operators on A100-80GB-PCIe. 18… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.11 (p.19)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig11.png]]
> [!tip] 【图文联合解读】**图11核心**：Llama-33B在A100-80GB-PCIe上的Roofline图，横轴算术强度1→10k FLOP/Byte，纵轴性能10G→100T FLOP/s；红虚线为312 TFLOP/s计算上限，蓝虚线为1935 GB/s带宽斜线（交叉点ridge）。六类算子（qkv/mlp、up·gate·down、qk·pv）分init（prefill）与ar（decode）两阶段。ar阶段点几乎全集中在强度~1、低于ridge的带宽受限区（10G–1T FLOP/s），远未触及计算上限。

**论证结论**：LLM推理（尤其自回归decode）为memory-bound而非compute-bound，硬件算力大量闲置。

**论文作用**：为Medusa多head并行猜测与验证提供硬件动机——将decode批量化、提升算术强度，向compute-bound区域迁移，从而释放被浪费的算力、加速推理。
*caption: Llama-33B operators on A100-80GB-PCIe. 1 10 100 1k 10k… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.12 (p.19)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig12.png]]
> [!tip] 【图文联合解读】图12为Llama-7B在A40上的Roofline模型：横轴运算强度1→10k (FLOP/Byte)，纵轴性能10G→100T (FLOP/s)；蓝虚线为带宽上限696 GB/s，红虚线为算力上限149.7 TFLOP/s，绿竖线标示转折点（≈200）。图中标注六类算子（qkv、mlp、up/gate/down、qk/pv）在init与ar两阶段的位置：qk/pv的ar阶段落在强度≈1、性能仅10G–1T的强内存受限区，远低于带宽线；qkv/mlp矩阵运算则位于强度≈100、性能10T+的算力受限区。结合图11，本图量化说明ar解码阶段注意力算子严重受内存带宽制约，论证了Medusa多解码头方案通过单次前向预测多token、提升算术强度以突破该瓶颈的必要性。
*caption: Llama-7B operators on A40. 19… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.13 (p.20)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig13.png]]
> [!tip] 【图文联合解读】图13为Llama-13B在A40上的算子roofline图。横轴运算强度1–1000，纵轴性能10G–100T；红色虚线~150TF为A40算力峰值，蓝色虚线为带宽屋顶。数据分三簇：低强度(~1)棕色×约50G–700G，属显存受限；中强度橙色×约0.7–3T，处于过渡区；高强度(~100–200)紫色×达10–30T，逼近算力上限。

原文论证：(1)基座LLM推理为memory-bound，受限于带宽屋顶；(2)Medusa新增多个解码头，将负载推向高强度区、靠近计算峰值，从而利用原本闲置的算力。

在论文中的作用：为"Medusa把负载由访存瓶颈推向算力饱和区"提供算子级roofline建模支撑，解释其多预测头并行解码的加速机理。
*caption: Llama-13B operators on A40. 1 10 100 1k 10k… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.14 (p.20)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig14.png]]
> [!tip] 【图文联合解读】图14为Llama-33B在A40上的Roofline模型：横轴为运算强度，纵轴为FLOP/s（对数刻度）。红色虚线标A40峰值算力约100T FLOP/s，蓝色斜线表示内存带宽天花板。橙色×簇集中于强度≈1、性能50G–1T FLOP/s（LayerNorm、attention等访存受限算子）；紫色×簇位于强度≈50–80、性能10–30T FLOP/s（GEMM等计算受限算子）。论文借此论证：访存受限算子远未触及算力峰值，是LLM推理瓶颈；Medusa多头并行预测可聚合访存受限运算、提升等效运算强度并向计算受限区迁移，为其加速框架提供硬件层动因。
*caption: Llama-33B operators on A40. 20… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.15 (p.21)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig15.png]]
> [!tip] 【图文联合解读】**核心对象与结构**：Llama-7B 在 A6000 上的算子级 roofline 图。X 轴为算子强度 FLOP/Byte（1→10k，对数），Y 轴为性能 FLOP/s（10G→100T，对数）；红线 181 TFLOP/s 为算力天花板，蓝线 768 GB/s 为带宽上界，绿线约 270 处为岭点；×标记涵盖 qkv、mlp up/gate/down、qk/pv 等算子在 init（prefill）与 ar（decode）两种工作点。

**关键结论**：qk/pv 等注意力算子在两种阶段均落在左坡 ~1 FLOP/Byte、低性能 30G–700G 区，呈带宽受限；mlp up/gate/down 集中于高强度 50–300 FLOP/Byte 处逼近峰值；decode 阶段算子强度普遍低于岭点，整体深陷 memory-bound 区域。

**论文作用**：以 roofline 量化论证 autoregressive decode 受带宽而非算力制约，多头并行验证不会加剧计算压力，为 Medusa 多解码头加速方案提供算子级理论与实验支撑。
*caption: Llama-7B operators on A6000. 1 10 100 1k 10k… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.16 (p.21)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig16.png]]
> [!tip] 【图文联合解读】该图是Llama-13B在A6000上的Roofline图：横轴运算强度1–10k FLOP/Byte、纵轴性能10G–100T FLOP/s（均对数），蓝虚线为768 GB/s带宽天花板，红虚线为181 TFLOP/s算力上限。算子（qkv、mlp、up/gate/down、qk/pv）以×标于init（prefill）和ar（decode）两工况。ar解码算子集中于~1 FLOP/Byte、性能仅40–700G FLOP/s，受带宽严重制约；init预填充算子沿斜线攀升至5–40T FLOP/s，已逼近算力上限。关键结论：自回归解码为内存瓶颈，单token串行访存浪费算力——这正是Medusa多头并行解码的实证动机：一次预测多token以摊薄权重加载开销、提升带宽利用率，构成论文"多解码头加速框架"的核心论证依据。
*caption: Llama-13B operators on A6000. 21… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.17 (p.22)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig17.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图17以 Roofline 模型刻画 Llama-33B 在 A6000 上的算子表现。横轴为运算强度（FLOP/Byte），纵轴为算力（FLOP/s），并叠加 768 GB/s 带宽线（蓝虚）与 181 TFLOP/s 计算峰线（红虚），Ridge Point 约在 235 FLOP/Byte 处（绿虚线）。六类算子分两区：① 位于 Ridge 右侧的 **up/gate/down**（MLP 线性层，无论 init 还是 ar）落在 ~180 TFLOP/s 的计算天花板，呈 compute-bound；② 位于 Ridge 左侧的 **qkv/mlp** 与 **qk/pv** 注意力相关算子呈 memory-bound，且 ar（自回归）变体远低于 init 版本，仅约 0.1–10 TFLOP/s。

论文借此论证：自回归解码阶段注意力/QKV 是访存瓶颈，GPU 算力被严重闲置。该图直接支撑 Medusa 的核心动机——通过多解码头并行预测多个 token，把访存受限的 AR 路径转化为可利用空闲算力的批量计算，从而实现推理加速。
*caption: Llama-33B operators on A6000. 22… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.18 (p.23)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig18.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图18是Llama 33B在A100 80GB PCIe、batch=16条件下attention矩阵乘的roofline图（双对数坐标）。图中绘出两条硬件上界：1935 GB/s带宽线（蓝虚）与312 TFLOP/s计算线（红虚），交点（绿虚线）约在160–200 FLOP/Byte处。

关键数据点：
- **自回归qk/pv**（灰点，约0.7–1 FLOP/Byte）：性能仅~0.5–1.5 TFLOP/s，远低于双屋顶线，呈严重memory-bound；
- **Medusa候选数16→112**（黄→深紫）：运算强度由~10升至~50 FLOP/Byte，性能从~10 TFLOP/s攀升至~80–90 TFLOP/s，逼近计算屋顶。

**结论与作用**：该图量化论证了Medusa的核心加速机制——通过多候选头并行解码，将attention的算术强度从深度访存区推高至计算受限区，显著提升单步硬件利用率，是论文"多解码头框架可系统性突破自回归瓶颈"这一核心论点的roofline级实验支撑。
*caption: FLOP/s vs. Operational Intensity of attention matrix multiplication with batch size 16. 23… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.19 (p.24)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig19.png]]
> [!tip] 【图文联合解读】**图19解读：**

1）图为 Llama 33B 在序列长度 1024 下，注意力矩阵乘法（QK/PV 投影）的 Roofline 模型：横轴为算术强度（1–30+），纵轴为实测 FLOP/s（10G–100T+）。红色虚线为硬件峰值算力约 300T FLOP/s，蓝色虚线为显存带宽上限。灰色点（强度≈1）处于带宽受限区，仅达 100G–1T FLOP/s；橙色点（强度≈10）约 5–50T；紫色点（强度≈20–30）约 30–80T，整体均远低于算力峰值线。

2）该图论证：注意力层属 memory-bound，其瓶颈在于权重加载而非算力，因此通过多 token 投机解码可摊销访存开销、获得加速——为 Medusa 的核心动机提供硬件层面依据。

3）与 Fig.20（线性层分析）共同支撑论文"M 型推理应以减少访存为目标"的主张，奠定多解码头方法论的硬件合理性。
*caption: FLOP/s vs. Operational Intensity of attention matrix multiplication with sequence length 1024. 1 10 100 1k 10k… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.20 (p.24)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig20.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) 该图为 Llama 33B 在 A100 上 up/gate/down 线性层的 roofline 图。横轴 Operational Intensity 约 0.7–30+，纵轴 FLOP/s 从 10G 跨越至 100T 以上；灰色低候选数点紧贴蓝色带宽边界斜线（~1T→10T），橙色与紫色高候选数点在强度 ~20–30 处抬升至 ~20T–100T，向红色虚线代表的算力天花板（约 200T+）逼近。

2) 原文以此论证：随 Medusa 接受候选数从 16 增至 112，每字节权重/KV 上执行的 FLOP 增多，kernel 由带宽受限区向右上方迁移；高候选时 MLP 线性层几近饱和 A100 Tensor Core（312 TFLOP/s 上限），说明额外投机验证是"免费算力"，可被线性层摊销利用。

3) 与 Fig. 19（qk/pv 注意力仍处于带宽限以下）互补，从硬件 roofline 层面定量解释 Medusa 推理加速的来源——验证开销在 MLP 层被计算能力吸收，构成论文核心实验证据链。
*caption: FLOP/s vs. Operational Intensity of Linear layers. 24… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.21 (p.26)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig21.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示 Llama-7B（batch=1，seq=1024，A100）下，候选 token 数 1→112 的三项指标：蓝色星"模拟接受率"由 1.0 单调升至 ~3.3；绿色星"模拟加速比"在候选数 ≈64 处达 ~2.95 饱和后略降至 ~2.85；堆叠柱为归一化验证时延（qk/pv ar、qkv linear ar、up/gate/down ar 三层），总时延由 1.0 增至 ~1.15，瓶颈在 FFN 投影层。

论文据此论证：**候选 token 增多持续抬高接受率，但验证开销同步上涨，使加速比在 ≈64 处饱和**，证明 Medusa 头数存在最优工作点，并非"越多越好"。在论文方法链路中，该图作为效率–精度权衡的量化证据，为头数选择与稀疏化策略提供实证支撑。
*caption: Simulated acceleration rate, speedup, and normalized latency ablation using different numbers of candidate tokens under the setting of batch size 1 an… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.22 (p.27)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig22.png]]
> [!tip] 【图文联合解读】**图22图文联合解读**

1. **核心数据**：横轴为候选token数（1–112），纵轴为模拟加速比（0–3.0×），固定序列长度1024、Llama-7B，绘制7条批大小曲线（bs=1/2/4/8/16/32/64）。bs=1在候选64时峰值约2.93×，bs=2约2.60×（@64），bs=4约2.25×（@32），bs=8约1.82×（@16–32），bs=16约1.41×（@16），bs=32、64则随候选数增加加速比从1.0单调降至~0.15。

2. **关键结论**：加速比随批大小增大而显著衰减；最优候选token数与批大小呈反向关系（bs越小越能容纳多候选）。当bs≥32时，过多候选token反而损害性能，验证猜测开销/验证成本在批大时主导。

3. **论文作用**：作为模拟分析（图22-23对偶扫描：固定seq扫bs / 固定bs扫seq），在端到端实验前预测Medusa头数选择与工作负载匹配策略，指导实际部署中权衡头数与批大小。
*caption: Simulated speedup with sequence length 1024 for Llama-7B. 1 16 32 48 64 80 96 112… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.23 (p.27)
![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig23.png]]
> [!tip] 【图文联合解读】**图23 联合解读：**

**1. 核心对象与数据：** 图展示 Llama-7B 在 batch size=4 固定下，Medusa 模拟加速比随候选 token 数（1–112）的变化曲线，共 7 条对应序列长度 128–8192。短序列收益最高：seq_len=128/256/512 在 32 候选时峰值达 2.40–2.45×；中长序列（1024–2048）峰值约 2.00–2.23×；seq_len=4096 峰值降至 ~1.78×；seq_len=8192 仅约 1.36×。所有曲线在 80+ 候选后均回落。

**2. 关键结论：** (a) 存在最优候选数 ≈32，过多会因 verify 开销抵消收益；(b) 加速比随序列长度增加单调下降，印证 Medusa 在低算术强度（小 batch/长序列）场景下增益受限。

**3. 论文作用：** 与 Fig 22（固定 seq_len=1024 扫 batch size）正交互补，系统刻画加速比在 batch×sequence 二维空间中的分布，为方法适用边界提供量化依据。
*caption: Simulated speedup with batch size 4 for Llama-7B. 27… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.1 (p.1)
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig01.png]]
> [!tip] 【图文联合解读】图含上下两幅折线图，以LLaMA-3.1-8B-Instruct为target、在MT-bench上对比EAGLE-2（红）与EAGLE-3（蓝），x轴为1/2/4/8×ShareGPT。上图Speedup：EAGLE-3由~3.7单调升至~4.4，EAGLE-2在~3.2处趋于饱和；下图Accept length：EAGLE-3由~5.2升至~6.1，EAGLE-2始终贴近~4.1。图用以论证：EAGLE-3的新架构打破了前作随数据增大迅速饱和的瓶颈，首次呈现持续上升的scaling law。作为开篇Figure，它奠定全文核心动机——更多训练数据带来更大加速收益，为后续架构设计、训练策略与实验验证提供支撑。
*caption: Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target model, with the x-axis representing the data scale relative to ShareGP… ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.2 (p.2)
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig02.png]]
> [!tip] 【图文联合解读】图2展示7种方法在4个目标模型上的推理加速比（temperature=0）：Vicuna-13B（MT-bench）上EAGLE-3达5.6×，超过EAGLE-2（4.1×）、Medusa（2.1×）与投机采样（1.9×）；LLaMA-3.1-8B、LLaMA-3.3-70B、DeepSeek-R1-LLaMA-8B（GSM8K）上EAGLE-3分别达4.4×、4.1×、5.0×，均为各模型最优。该图作为性能总览，证明EAGLE-3在对话与推理任务、8B–70B不同规模上一致领先已有方法；配合Table 2消融（去特征约束+多级特征融合），共同支撑其两项关键改进的有效性，构成论文方法验证链路的收口证据。
*caption: Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1… ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.3 (p.3)
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig03.png]]
> [!tip] 【图文联合解读】**图3 联合解读**

1) **核心结构**：图分三层对比。上层EAGLE：训练Step1用真实特征f_t预测f̂_{t+1}、t̂_{t+2}（含l_fea、l_token双损失），测试Step2串行自回归f̂→t̂；中层EAGLE+l_fea去除版：改输出无约束向量â，仅l_token，但测试时t̂_{t+3}≉ t_{t+3}（红错号）暴露训练-测试失配；底层EAGLE-3（training-time test）：训练时把Step1预测的â_{t+1}回灌为Step2输入（红虚线箭头"Training-time test"），使训练/测试一致，Step2输出t̂_{t+3}≈t_{t+3}。

2) **关键结论**：原文指出EAGLE训练用真特征、测试用预测特征，存在分布偏移；将Step1纳入训练循环后，模型学会在自身预测误差下仍保持稳定，使增加训练数据的收益更显著，验证了training-time test的必要性。

3) **论文作用**：作为EAGLE-3方法论核心图，奠定"训练模拟推理时自回归"原则，衔接后续消融与scaling实验，为EAGLE-3在更大数据/模型下的加速增益提供机制依据。
*caption: Illustration of training-time test (the bottom part) and its comparison with other draft methods (the upper and middle parts). f denotes the feature, … ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.4 (p.2)
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图4横轴为相对ShareGPT的训练数据规模（1/2/4/8倍），纵轴为接受率0-α，对比EAGLE、EAGLE-3及去掉特征预测的EAGLE三条曲线。EAGLE从约0.755升至0.784即饱和；EAGLE-3起点最低（≈0.722）但斜率最陡，于4倍处反超原EAGLE并达≈0.801；无特征预测版本始终居前（8倍≈0.812）。

该图印证原文关键结论：原EAGLE对数据扩展几乎无感，而采用"training-time test"将Step 1融入训练后，数据扩展收益被显著放大，使EAGLE-3在大数据规模下超越基线。此图作为支撑"训练-测试一致性"核心设计的可扩展性证据，串联起方法动机与后续加速比的实验链。
*caption: We can address this issue by incorporating Step 1 into the training process (the bottom of Figure 3). Using this method, the benefits of increasing tr… ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.5 (p.4)
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读**

1) **核心结构**：左为冻结的Target Model，经Embedding、两层Decoder Layer后输出低/中/高层特征 $l_{how}, m_{how}, l_{can}, m_{can}$（高层 $h$ 未在图中绘出）；右为Draft Model的三步流水线——① FC Layer融合目标特征 $g$ 与上下文embedding $e$；② Decoder Layer自回归展开序列；③ 仅LM Head扩展为多分支候选树（"can"/"I"/"do"）。

2) **关键论证**：EAGLE-3通过**训练时测试**让Draft Model直接消费Target Model的**多层特征（l/m/h）**而非仅末层hidden state，并以三层架构（FC→Decoder→LM Head）实现"特征融合→序列自回归→树状并行候选"解耦，使草稿生成既保留目标模型语义信息、又获得高吞吐候选。

3) **论文作用**：该图是EAGLE-3方法论的核心可视化，明确其相对EAGLE/EAGLE-2的**架构增量**（三层管线+多层级特征输入+训练时测试策略），为后续消融与加速比实验提供机制依据，是理解后续图6、图7 tree attention与训练流程的基础。
*caption: Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. l, m, and h represent the low, middle, and high-level feat… ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.6 (p.5)
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图示展示训练时测试的三个注意力因果mask：①原生训练步（3×3，token 为 How/can/I）为全下三角，每 query 关注全部前置 key；②两个模拟步（依次 3×6、3×9）随 draft token（蓝/黄色，与原句"How can I are we do…"等灰色训练 token 区分）注入，mask 由稠密退化为严格对角——仅 query=key 处标✓，其余置零。

它论证：仅当 key 源自原始训练数据才需全下三角矩阵乘；模拟 draft 阶段用向量点积按位计算即可，避免对角化稀疏矩阵的算力浪费。该稀疏化改造与 HASS 类似，共同支撑 EAGLE-3 在训练—测试一致性模拟下训练 draft 模型，从而在推理时实现低开销的多 token 预测加速。
*caption: All attention masks are diagonal, except when the original training data is used as the key. Using matrix multiplication in this case would result in … ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.7 (p.8)
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig07.png]]
> [!tip] 【图文联合解读】**图7联合解读：**

1）**核心对象与数据**：横轴为0-α至7-α（即在已接受前序token条件下，输入含n个估计特征后的接受率），纵轴为接受率。EAGLE（红）从0-α的≈0.71急剧衰减：1-α≈0.64、3-α≈0.57、6-α降至≈0.51，整体跌幅约20%；而EAGLE-3（蓝）始终稳定在0.78–0.81区间，几乎无衰减，6-α处反达峰值≈0.81。

2）**论证的关键结论**：随估计特征数n增加，传统EAGLE因仅依赖last-token特征而出现严重的接受率雪崩；EAGLE-3通过训练时即采用test-time多特征输入，使其在自投机多步生成中保持高且平稳的接受率，二者差距随n增大而显著扩大。

3）**作用**：为EAGLE-3"训练-测试一致性"设计提供了直接定量证据，是论证其推理加速效果优于EAGLE的核心实验之一。
*caption: Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-… ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.1 (p.1)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图1展示MT-bench贪心解码下，6个模型（Vicuna 7B/13B/33B、LLaMA2-Chat 7B/13B/70B）相对Vanilla（1.00x基线）的推理加速比。EAGLE以2.78x–3.07x全面领先且稳定在~3倍；Medusa约1.92–1.97x、Lookahead约1.45–1.64x；传统Speculative sampling因无合适draft model，7B/13B均标N/A，仅33B（1.27x）、70B（1.88x）可用且显著低于EAGLE；DistillSpec仅适用于LLaMA2-Chat 70B（2.13x）。

该图作为开篇核心motivation，量化揭示现有无损加速方法在中小模型上"无draft可用"或加速有限的瓶颈，直接支撑后文提出基于"重思feature uncertainty"的EAGLE方案——无需微调backbone即可在所有规模模型上取得一致且最高的加速比。
*caption: Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for greedy (temperature=0) settings. Speedup ratio of Medusa and Lookahead a… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.2 (p.2)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig02.png]]
> [!tip] 【图文联合解读】**图2解读（MT-bench，T=1）**

图2对比EAGLE、Speculative sampling、DistillSpec、Vanilla在Vicuna 7B/13B/33B与LLaMA2-Chat 7B/13B/70B共6个模型上的加速比。**EAGLE全模型稳定取得2.13x–2.68x加速**（7B最低2.13x，13B最高2.68x）；Speculative sampling仅在33B（1.03x）与70B（2.06x）有效，其余N/A；DistillSpec仅70B达1.84x，其余1.00x；Vanilla恒为1.00x基线。

原文借此论证：Lookahead仅支持贪心、Medusa非贪心不保无损，故排除比较；EAGLE基于特征不确定性的建模天然适配采样，在T=1下全模型均获显著无损加速，远超token级投机与蒸馏方法。

该图与表2（接受长度τ、接受率α）共同支撑论文核心论点——**重新思考特征不确定性是推进投机采样的关键**。
*caption: Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medu… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.3 (p.2)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig03.png]]
> [!tip] 【图文联合解读】**图3联合解读**

1) **核心结构**：以 token "I" 及其特征 $f_{\text{I}}$ 为根节点（$p_{\text{I}}$：am=0.6, always=0.4），经 sampling 分叉为两条支链——左支 "always"→$f_{\text{always}}$（$p_{\text{begin}}$=0.8, $p_{\text{look}}$=0.2），右支 "am"→$f_{\text{am}}$（$p_{\text{excited}}$=0.3, $p_{\text{ready}}$=0.7），量化展示同一前缀下的双分支概率分布。

2) **关键结论**：仅凭 $f_{\text{I}}$ 无法唯一确定下一特征；下一特征取决于 sampling 结果，由此引出"特征不确定性"概念，挑战 EAGLE 假设特征可确定下一 token 的前提。

3) **论文作用**：作为动机图，揭示自回归特征预测受随机采样影响，为 EAGLE 必须重新思考特征不确定性、改进投机采样策略提供直观论据。
*caption: Uncertainty in feature sequences. The next fea- ture following fI is contingent on the sampling outcome and cannot be determined solely based on fI, w… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.4 (p.3)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig04.png]]
> [!tip] 【图文联合解读】图示MT-bench上Vicuna 7B三种draft模型7轮Epoch的Speedup（左）与Acc（右）曲线：feature&shifted-token最优，Speedup从≈1.95升至≈2.75、Acc从≈0.62升至≈0.78；feature次之（≈1.85/0.65）；token最差且几乎停滞（≈1.5/0.30）。

技术结论：纯token或纯特征作draft输入时接受率受限，而"特征序列+超前1拍token序列"双输入消除了采样下f_{t+1}的不确定性，使接受率与加速比同时大幅提升。

论文作用：在ablation层面定量验证EAGLE核心架构（f_t+t_{t+1}双输入）的设计必要性，支撑Vicuna/LLaMA2-70B上2.68×加速比的关键实验结论。
*caption: Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at tempera- ture=0, tested on MT-bench with Vicuna 7B a… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.5 (p.4)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig05.png]]
> [!tip] 【图文联合解读】**图5图文联合解读：**

图示四种推测解码生成 t₄、t₅ 的流程：①**Speculative Sampling** 调用小型 LLM 串行推理；②**Lookahead** 仅以单 token 做 2-Gram/Jacobi 匹配；③**Medusa** 多 Head 共享同一 f₂ 输入，draft 间无信息传递；④**EAGLE** 联合多 token embedding（t₂,t₃）与前序 feature（f₁,f₂），先自回归预测 f₃ 再得 t₄，下轮预测 f₃ 又作输入。

对比揭示前三者局限：仅依赖 token（Lookahead/Spec.Sampling），或忽略 draft 间 feature 不确定性累积（Medusa 所有 head 共用同一 f）。EAGLE 通过"embedding + feature 自回归"兼顾 token 确定性与 feature 上下文性，直观论证其核心动机——**重新思考 feature 不确定性**，为后文 EAGLE 方法展开与实验对比奠定框架。
*caption: A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5. t (represented by blue blocks) denotes tokens, and f (orange blocks) … ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.6 (p.4)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig06.png]]
> [!tip] 【图文联合解读】图6为EAGLE推测解码流水线。上部计算流：左侧Target LLM将"how can"经Embedding、Transformer Layers、LM Head得首token"can/I"；右侧Draft Model以"One Auto-regression Head"为核心，特征f（橙块）与嵌入e（绿块）联合输入，经Forward 1-3多层预测候选（红框：make/help、a/our等），蓝色雪花模块为冻结的目标LLM参数。下部展示对应生成树：Query"How can"采样得"I"，由FeatExtrapolator逐层外推为多层候选分支。

该图论证：草稿模型以"特征+嵌入"联合输入替代纯嵌入预测，可捕获更深层上下文；冻结目标LLM保证一致性；树状多token采样提升验证吞吐。作为方法总览，为核心论点"特征不确定性需重新思考"提供机制框架，支撑后续实验链路。
*caption: Pipeline of EAGLE. The upper section illustrates the computational process, while the lower section displays the corresponding generation results for … ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.7 (p.7)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig07.png]]
> [!tip] 【图文联合解读】**图7联合解读：**

该图量化MT-bench（temp=0）下6个模型的加速比：EAGLE含tree attention为2.78x–3.07x，不含为2.27x–2.66x，Vanilla统一为1.00x。模型覆盖Vicuna 7B/13B/33B与LLaMA2-Chat 7B/13B/70B。

**技术结论：** tree attention在所有模型上稳定带来约0.4–0.5x的额外加速，是EAGLE不可或缺的工程组件；即便剥离该模块，EAGLE仍保持2倍以上加速。

**论文作用：** 作为消融实验，一方证明EAGLE核心的特征不确定性预测机制独立有效（无需tree attention亦显著超越Vanilla），另一方面量化tree attention对端到端加速的边际贡献，为"EAGLE+tree attention"完整方案提供实证支撑。
*caption: Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.8 (p.8)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读（≤220字）：**

图8以Vicuna-7B/MT-bench为基准，在2×4网格（行：T=0/1；列：Speedup/τ/0-α/1-α）中对比四种draft输入。量化显示：feature&shifted-token（蓝线）在所有指标全面最优——T=0时加速比≈2.7×、τ≈3.7、0-α≈0.78、1-α≈0.68；T=1时加速比≈2.0×、τ≈3.0；纯token（绿）始终最差，纯feature（红）次之，且其0-α/1-α明显低于双输入方案。

**论证结论**：draft模型必须同时利用目标LLM的下一层feature与偏移后的token，二者缺一不可；token偏移是显著提升接受率τ与walltime加速的关键。

**链路作用**：直接验证EAGLE核心架构选择——"feature + shifted-token"输入是其投机采样相对纯token基线实现显著加速（约2.7×）的根因，构成论文方法主张的关键实验证据。
*caption: Performance of draft models with varying inputs. The target LLM is Vicuna 7B, and the test dataset is MT-bench.… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.9 (p.12)
![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig09.png]]
> [!tip] 【图文联合解读】图示 EAGLE 草稿的两类计算拓扑：左图启用树注意力，以 1 个“query”为根，连同 22 个候选共 23 个节点（最长 5 步），可同时处理多条分支路径；右图无树注意力，仅为“query＋5 个 token”的 6 节点单链。论文指出，最优树形依赖上下文；批量增大、冗余计算浪费减少时，较小的树可能更优。该图位于“草稿生成—主模型验证”链路，揭示并行收益与注意力开销的权衡。
*caption: However, the optimal tree structure is likely context-dependent. For instance, as batch size increases and redundant computational resources decrease,… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### EAGLE-2: Faster Inference of Language Models with Dynamic Dr — Fig.1 (p.1)
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig01.png]]
> [!tip] 【图文联合解读】图1为temperature=1下四种LLM（Vicuna 7B/13B、LLaMA2-Chat 7B/13B）三种lossless加速方法的推理加速比柱状图。数据：Vicuna 7B为3.05x(EAGLE-2)/2.13x(EAGLE)/1.50x(投机采样)；Vicuna 13B为3.80x/2.32x/1.62x；LLaMA2-Chat 7B为3.19x/2.22x（投机采样N/A）；LLaMA2-Chat 13B为3.92x/2.68x（N/A）。原文借该图论证两点：①EAGLE-2的动态草稿树机制在全部模型上稳定超越EAGLE与投机采样；②在保证输出分布不变前提下仍取得3-4倍显著加速。该图作为论文首图，对全文方法部分起总览性铺垫作用，为Table 1的细粒度对比与动态草稿树算法阐述建立直观性能基准。
*caption: Speedup ratios of different methods at tempera- ture=1. For speculative sampling, the Vicuna series uses… ｜ 论文 [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] ｜ arxiv 见 MD 元信息*

### EAGLE-2: Faster Inference of Language Models with Dynamic Dr — Fig.2 (p.2)
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图2对比了EAGLE-2与四种基线方法（EAGLE、Medusa、Lookahead、Speculative sampling）在7个模型（Vicuna 7B/13B、LLaMA2-Chat 7B/13B/70B、LLaMA3-Instruct 8B/70B）上的推理加速比（temperature=0）。量化显示：EAGLE-2在Vicuna 13B达**4.26×**峰值，所有模型稳定在**3.29×–4.26×**，系统性地领先EAGLE（2.72×–3.07×）、Lookahead（1.43×–1.61×）与Medusa/Spec Sampling。原文借此论证动态草稿树带来的稳定且显著的加速收益，构成论文核心实验证据，支撑"EAGLE-2为当前最快推测解码方法"的结论，并衔接Table 1的扩展对比。
*caption: Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna- 68M as the draft model. LLaMA2-Chat 7B,… ｜ 论文 [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] ｜ arxiv 见 MD 元信息*

### EAGLE-2: Faster Inference of Language Models with Dynamic Dr — Fig.3 (p.3)
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig03.png]]
> [!tip] 【图文联合解读】草稿阶段(a)：标准方法对token(t2,t3→t4→t5)链式自回归；EAGLE额外引入上一层特征f1,f2，自回归预测f3,f4后映射为token。验证阶段(b)：标准方法链式校验t4→t5，单分支接受；EAGLE改用树结构(t4分支为t5、t6)，由原LLM一次性并行验证，可同时接受多token。论文以此图论证核心方法学结论：①特征级自回归降低草稿难度，②动态草稿树扩展一次验证的接受基数，构成EAGLE-2"特征预测+树形验证"双层加速推理框架的可视化基础，后续实验均围绕二者带来的端到端加速展开验证。
*caption: Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s tree-structured draft is shown only in the verification stage, while th… ｜ 论文 [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] ｜ arxiv 见 MD 元信息*

### EAGLE-2: Faster Inference of Language Models with Dynamic Dr — Fig.4 (p.3)
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图4下半部对比了EAGLE与EAGLE-2的草稿树结构。EAGLE对"10+2"生成两分支"="和"+"，再对"10+2="静态地生成两分支"1"和"3"；EAGLE-2同样生成"="、"+"两分支，但识别到"1"高置信后，动态沿"="延伸出链式节点"1→2"。原文以此论证：**EAGLE-2依据置信度自适应调整草稿树形状**，将算力集中在高概率路径上，避免在低概率候选（如"3"）上浪费验证开销。该图作为方法论示例，引出后文提出的动态草稿树（dynamic draft tree）机制，是EAGLE-2相较EAGLE实现进一步加速加速比的核心创新证据。
*caption: Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. When the query is “10+2=”, the next token is very likely to be correct… ｜ 论文 [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] ｜ arxiv 见 MD 元信息*

### EAGLE-2: Faster Inference of Language Models with Dynamic Dr — Fig.5 (p.3)
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据：** 图(a)为二元draft树结构（Query→P1/P2→P3–P6，共6个叶子位置）；图(b)为散点图，纵轴Accept Rate(0–1)，横轴Position(1–6)，每点对应一次query。量化趋势：P1接受率密集集中在~1.0（全图最高），P2次之（约0.4–0.9），P3分散于0.2–0.5，P4、P6普遍跌至0.0–0.2（最低），P5相对偏高（0.2–0.9）。

**2) 关键结论：** draft token接受率具有显著的**位置依赖性**——左上（浅层、靠左分支）token接受率高，深层（尤其P6）接受率低。说明并非所有draft位置同等有价值。

**3) 在论文中的作用：** 该图是EAGLE-2从静态树转向**动态draft树**的核心动机证据：既然接受率随位置差异巨大，等宽静态扩展浪费算力；动态树据此对高接受率分支多扩展、低接受率分支少扩展，从而提升speculative decoding的整体加速比。
*caption: Overall, the acceptance rate of draft tokens is position-dependent, with the highest acceptance rate at position P1 and the lowest at position P6. Dra… ｜ 论文 [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] ｜ arxiv 见 MD 元信息*

### EAGLE-2: Faster Inference of Language Models with Dynamic Dr — Fig.6 (p.4)
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig06.png]]
> [!tip] 【图文联合解读】**图6图文联合解读**

**1）核心对象与数据**：横轴为draft模型输出的置信度（0–1，分10个区间），纵轴为目标LLM Vicuna 7B在同一置信度区间内的实际接受率。蓝色柱体沿红色虚线 y=x 近似单调递增——置信度≈1.0区间接受率约0.98，最低区间（≈0.0–0.05）接近0.00。

**2）关键技术结论**：置信度与接受率高度正相关、几近线性；中段（0.4–0.6）柱体略超对角线，说明draft模型的置信度略偏保守但具有强校准性，可作为token排序与节点筛选的可靠信号。

**3）在论文中的作用**：为§4.1（动态扩展draft tree）与§4.2（draft token重排）提供经验支撑——按置信度从最新一层中挑选"最有希望"的节点送入下一轮扩展的做法是合理且有保障的。
*caption: Average acceptance rates for different confidence score intervals of the draft model. The red dashed line connects (0,0) and (1,1) to aid in visual as… ｜ 论文 [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] ｜ arxiv 见 MD 元信息*

### EAGLE-2: Faster Inference of Language Models with Dynamic Dr — Fig.7 (p.5)
![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig07.png]]
> [!tip] 【图文联合解读】**【对象与结构】** 动态草稿树：根"It(1.0)"分叉为is/has双层；橙色top-2节点(a=0.48, to=0.14)作扩展输入，生成绿色子节点good/nice/be/do；Rerank后保留top-8蓝色节点(It,is,has,a,the,to,good,be)，扁平为1D序列后按树结构构建仅可见祖先节点的注意力掩码。

**【技术结论】** 局部扩展(top-2选节点)与全局重排(top-8选草稿)解耦，使草稿树依据上下文动态自适应生成多条高置信候选，而非依赖预设静态结构。

**【论文作用】** 直观看]<]minimax[>[展示EAGLE-2相对EAGLE"动态草稿树"的核心创新，支撑其以更少草稿模型调用换取更高接受率与推理加速比的实验结论。
*caption: Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the block… ｜ 论文 [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] ｜ arxiv 见 MD 元信息*

### BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI — Fig.1 (p.2)
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig01.png]]
> [!tip] 【图文联合解读】**图1核心内容**：以三行对照呈现三种语言生成范式——自回归（arbitrary-length、✓KV caching、✗Not Parallelizable）、全扩散（fixed-length、✗No KV caching、✓Parallelizable）、块扩散（arbitrary-length、✓KV caching、✓Parallelizable），并用"continue to reduce the deficit"等生成示例直观展示块内并行去噪过程。

**论证的技术结论**：块扩散融合两类模型优势，兼具变长生成、KV缓存与块内并行采样，同时克服自回归不可并行、纯扩散不可缓存的固有缺陷。

**论文整体作用**：作为方法总览图，在引言/方法章节开篇建立"块内扩散+块间自回归"的混合范式概念框架，为后续训练损失推导、噪声调度设计与推理效率实验提供直觉锚点。
*caption: Block diffusion sequentially generates blocks of tokens by performing diffusion within each block and conditioning on previous blocks. By combining st… ｜ 论文 [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] ｜ arxiv 见 MD 元信息*

### BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI — Fig.2 (p.6)
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图示LM1B（16B token训练）单token训练NLL曲线，横轴约150k–250k步，包含：红色曲线（块扩散/扩散，方差最大、存在明显尖峰）、橙色AR曲线（最平滑低方差）、绿色AR随机batch曲线（方差居中）等多条线对比。

论文借此论证关键结论：平均50%掩码的离散扩散NELBO训练方差，与随机batch的AR相当，意味着每batch有效token近似翻倍（≈2×），扩散目标并无显著梯度劣势。

该图为块扩散作为AR与扩散LM之间插值框架的可行性提供经验背书，回应"扩散训练方差大、不易优化"的潜在质疑，是后续block size与调度实验的方法论前提。
*caption: Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of… ｜ 论文 [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] ｜ arxiv 见 MD 元信息*

### BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI — Fig.3 (p.21)
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig03.png]]
> [!tip] 【图文联合解读】**Figure 3 图文联合解读**

**1）核心对象与结构：** 图示一个专门化的注意力掩码（Specialized Attention Mask），按L=3个块（如x¹、x²、x³）排列，图中可见三色分区——**Block Diagonal (M_BD)**（块对角，每个块内独立）、**Offset Block Causal (M_OBC)**（偏移块因果，跨块时仅关注先前块）、**Block Causal (M_BC)**（块内因果，同块内token依次关注前者）。结合上下文规则：块内采用因果掩码更新x^b；块间跨注意力条件化于x^<b。

**2）关键技术结论：** 该掩码为块扩散模型构造了一种"块级稀疏因果+跨块条件化"的混合注意力模式：块内保持自回归因果性，块间以偏移因果避免信息泄露，同时通过M_BD实现并行去噪。原文Figure 4进一步证明，将其改写为FlexAttention兼容的稀疏掩码后，在L=1024、B=16、A5000上相比PyTorch原生实现可获**约5倍加速**与显著内存节省。

**3）在论文中的作用：** 该图是块扩散方法的核心算法图示，奠定了"块级半自回归"训练/采样范式，并为后续高效推理实现提供视觉依据，连接理论框架与系统优化。
*caption: x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3… ｜ 论文 [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] ｜ arxiv 见 MD 元信息*

### BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI — Fig.4 (p.22)
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图4展示了将图3的掩码策略改写为FlexAttention兼容的稀疏掩码函数（约30行PyTorch代码）。核心结构是合成三种掩码：①块内自注意（block_causal）、②跨块条件上下文（block_causal_BC）、③偏移块因果（M_OBC），通过`q//block_size`取整、`xt_flag`/`x0_flag`标识（0/1）控制q/kv关系，以按位XOR与AND逐元素组合，得到稀疏的`M_OBC`偏移因果掩码。

该代码论证了：基于PyTorch≥2.5的FlexAttention/JIT定制算子，在A5000、L=1024、B=16条件下，**显存显著降低且加速≈5倍**，相较朴素的`scaled_dot_product_attention`优势明显。

在论文链路中，此图属于工程实现层，为Block Diffusion模型的关键创新——半自回归+扩散混合的块稀疏注意力——提供高效GPU实现支撑，是模型可扩展训练/推理的底层保障。
*caption: We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customize… ｜ 论文 [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] ｜ arxiv 见 MD 元信息*

### BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI — Fig.5 (p.23)
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图5以代码片段展示核心实现：顶部调用 `torch.compile(fullgraph=True, mode="max-autotune-no-cudagraphs")` 进行全图编译加速；下方定义 `single_pass_block_diff_attn(q, k, v, block_mask)` 函数，内部通过 `flex_attention(q, k, v, block_mask=block_mask)` 完成一次前向注意力计算。

该图论证的关键技术结论：块扩散语言模型利用 PyTorch FlexAttention 接口，将自定义的块级因果掩码（block_mask）直接传入底层注意力内核，无需重写 CUDA/Triton 内核即可在通用硬件上高效实现"块内双向、块间因果"的混合注意力模式。

在全论文中的作用：它是连接理论掩码设计（Section）与高效训练推理的工程桥梁——通过 `flex_attention` 把块式注意力模式硬件化，使大语言规模下的块扩散训练成为可能，是模型可扩展性的核心实现支撑。
*caption: Attention computation using FlexAttention with our proposed custom mask.… ｜ 论文 [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] ｜ arxiv 见 MD 元信息*

### BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI — Fig.6 (p.26)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]]
> [!tip] ## Description

This figure is **not an architecture diagram** but rather a **qualitative sample** illustrating the output of MDLM (Sahoo et al., 2024a), a masked diffusion language model. There is no architecture, component, or data-flow schematic — the "figure" is simply a rendered block of generated text wrapped between `<lendoftext>` sentinel tokens.

**Reading the output:** The generated passage (~1024 tokens, produced over 5K diffusion steps) is a topical mishmash blending multiple domains — art criticism (Paolo Capacotti, Giuliano/Angiolo/Leonetto Romei/Fiastri family), a museum crime anecdote (Franco Belzina's life, the broken candle, statue restoration), WWII history (Canadian/Italian POWs, statues removed from Cooper–Paris), and music industry references (record labels, festivals). **Key takeaway:** despite MDLM achieving competitive perplexity, the 1024-token sample exhibits topic drift, entity hallucination, and incoherent transitions — a common failure mode where diffusion-style generation lacks the autoregressive consistency that maintains long-range coherence in causal LMs.

## Caption (verbatim)

> **Figure 6:** Sample from MDLM (Sahoo et al., 2024a) of length *L* = 1024 and *T* = 5K diffusion steps. The generative perplexity of this sample under GPT2-Large is 69.26 and its entropy is 5.6.
*caption: Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion steps.… ｜ 论文 [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] ｜ arxiv 见 MD 元信息*

### BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI — Fig.7 (p.27)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]]
> [!tip] **Figure description:** This figure is not an architecture diagram but a *sample generation* from BD3-LM, a block-wise discrete diffusion language model. It displays a single block of continuous narrative text (≈2,031 tokens) bounded by `<lendoftext>` end-of-document markers. The content is a coherent, multi-paragraph story about a girl traveling to Mexico, her mother being detained at a Bangkok airport on the way home, and broader commentary on Calais refugees — demonstrating that the model produces long, fluent, topic-consistent passages.

**Key technical takeaway:** Despite being trained with a context length of only L = 1,024, BD3-LM generates sequences of length L = 2,031 (nearly 2× the training window) using only T = 5K diffusion steps with block size L' = 16, yielding coherent text with GPT2-Large generative perplexity 24.3 and entropy 5.5 — showing block diffusion can extrapolate beyond training context.

**Caption (verbatim):**
> Figure 7: Sample from BD3-LM for block size L' = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3, and its entropy is 5.5.
*caption: Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative … ｜ 论文 [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] ｜ arxiv 见 MD 元信息*

### BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI — Fig.8 (p.28)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]]
> [!tip] **Description**

This is not a traditional architecture diagram — it is a qualitative-output figure. The figure consists of a single boxed block of generated English text flanked by `<lendofftext>` sentinel tokens. The text is one long, unsegmented passage (~2,000 tokens) produced by an autoregressive language model; it drifts incoherently across multiple unrelated topics (an NFL game recap, a personal dispute over a tree in "Charlotte Gardens," architectural commentary on a building, and assorted trivia), with frequent name/topic confusions, fabricated quotes, and hallucinated entities. There are no labeled components, arrows, or data-flow stages — the "architecture" is implicit (AR transformer with context length 1024 producing a 2003-token sample, benchmarked against GPT2-Large, achieving perplexity 10.6 and entropy 5.5).

**Key takeaway:** The sample illustrates that even a long-context AR model (L=1024) trained to generate beyond its context (L=2003) still produces locally fluent but globally incoherent, topic-drifting text — demonstrating that long-context AR pretraining alone does not guarantee coherent long-form generation.

**Caption (verbatim):**
Figure 8: Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5.
*caption: Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this samp… ｜ 论文 [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] ｜ arxiv 见 MD 元信息*

### DFlash: Block Diffusion for Flash Speculative Decoding — Fig.1 (p.2)
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图1以分组柱状图形式展示DFlash、EAGLE-3相对自回归基线（均归一为1.00）在Qwen3-8B+Transformers后端、7个基准上的加速比：GSM8K（5.15 vs 2.23）、Math500（6.08 vs 2.05）、AIME25（5.62 vs 2.05）、HumanEval（5.14 vs 2.17）、MBPP（4.65 vs 1.93）、LiveCodeBench（5.51 vs 1.81）、MT-Bench（2.75 vs 1.90）。DFlash在所有任务上均显著领先，平均超EAGLE-3约2.5倍以上，最高比值出现在LiveCodeBench（约3.0×），最低也在MT-Bench（约1.45×）。原文借此直接论证"块扩散式投机解码"在精度无损前提下，可大幅超越主流自回归投机方法（EAGLE-3），作为开篇核心实验，奠定全文方法优势与实用价值。
*caption: Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the… ｜ 论文 [[dflash-block-diffusion-for-flash-speculative-decoding]] ｜ arxiv 见 MD 元信息*

### DFlash: Block Diffusion for Flash Speculative Decoding — Fig.2 (p.4)
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图2展示DFlash推理流程的三个阶段：(1) 左侧目标模型编码上下文（含`-./&01`等前缀token），提取**隐藏上下文特征**（顶部阴影方块）并向中间虚线框注入；(2) 中间虚线框为草稿模型，融合目标特征后以**块扩散**方式并行生成约**278个token候选**（如"45%5/0$*5…"），左下虚线框示意已确认/待确认/待生成三类token状态；(3) 右侧目标模型一次性并行验证候选块，部分token被拒绝（"!!!"），其余被接受并继续生成下一块。

**论证结论**：目标模型的隐藏特征可直接作为草稿模型各层的条件输入，无需从头预测；块级扩散+并行验证使每步解码一次前向即可生成数百token。

**论文作用**：作为方法核心示意图，配合Table 2的**speedup/acceptance**数据，直观证明DFlash相较传统自回归推测解码的加速机理与收益来源。
*caption: DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s… ｜ 论文 [[dflash-block-diffusion-for-flash-speculative-decoding]] ｜ arxiv 见 MD 元信息*

### DFlash: Block Diffusion for Flash Speculative Decoding — Fig.3 (p.3)
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1）核心对象与数据：** 分组柱状图，横轴为 draft token 数（4/8/16），纵轴为生成延迟（ms）。EAGLE-3（1层）随 token 数线性增长：约 6.5→12→26 ms；而 DFlash 三种配置几乎平坦——DFlash(1) 始终 ≈2 ms，DFlash(3) 约 3.5–4 ms，DFlash(5) 约 5–6 ms。在 16 token 处，EAGLE-3 比最快 DFlash(1) 慢约 13 倍。

**2）关键结论：** DFlash 因采用 Block Diffusion 并行生成全部 draft token，延迟与草稿长度几乎解耦；而 EAGLE-3 因自回归逐 token 生成，成本随长度线性放大。这验证了 DFlash 作为 draft model 在效率上对自回归方案的数量级优势。

**3）在论文中的作用：** 该图是论文核心卖点之一的实验支撑——证明 DFlash 不仅在生成质量/接受率上可竞争，更以"恒定低延迟"显著降低 speculative decoding 的单步开销，为其在在线推理/树形解码场景中的实用性提供量化证据。
*caption: Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.… ｜ 论文 [[dflash-block-diffusion-for-flash-speculative-decoding]] ｜ arxiv 见 MD 元信息*

### DFlash: Block Diffusion for Flash Speculative Decoding — Fig.4 (p.5)
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig04.png]]
> [!tip] 【图文联合解读】**图4 联合解读**

图分两栏。左栏"From Target Model"为6列（p1–p4, r1, r2）因果三角掩码，目标模型对prompt与干净response自回归编码，输出蓝色上下文特征；右栏"Mask Blocks"为12列×12行的块注意力矩阵，按r1/m/m/m、r2/m/m/m、r3/m/m/m划分为3块，每块4行中仅允许同块clean token（橙）及前块mask token（绿）相互可见，白色为不可见token。

**核心结论**：draft模型以左侧蓝色目标特征为cross-attention条件，在每个clean response token之后并行预测3个mask token，从而形成"块扩散"式训练目标；条件注入被严格限定在clean token位置，避免未来信息泄露。

**论文作用**：该图即DFlash核心训练范式的示意图，是后文Table 4中Qwen3-27B取得较长接受长度与加速比的方法论基础。
*caption: DFlash training attention. The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens… ｜ 论文 [[dflash-block-diffusion-for-flash-speculative-decoding]] ｜ arxiv 见 MD 元信息*

### DFlash: Block Diffusion for Flash Speculative Decoding — Fig.5 (p.13)
![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig05.png]]
> [!tip] 【图文联合解读】**图5图文联合解读：**

图示Math500数据集上Acceptance Length随训练epoch（1–9）的演化，对比有/无loss decay两条曲线。蓝色（有loss decay）epoch 1即达~4.4，epoch 2快速跃升至~5.4；橙色（无）epoch 1仅~4.2，需至epoch 4方追至~6.0。两者在epoch 6–7同步收敛至峰值~6.45（蓝色略高），epoch 9趋于一致~6.35。

原文据此论证：**loss decay策略使dFlash训练"收敛更快、效果更好"**——尤其在前3个epoch显著拉开差距。在论文整体链路中，该消融实验作为附录A.5.2随机掩码采样方案的支撑，验证了损失衰减对投机解码头快速稳定收敛、高接受率（最终~6.35）的必要性，是模型实现高效推测的关键训练技巧之一。
*caption: The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING OF MASKED BLOCKS… ｜ 论文 [[dflash-block-diffusion-for-flash-speculative-decoding]] ｜ arxiv 见 MD 元信息*

### DSpark: Confidence-Scheduled Speculative Decoding with Semi- — Fig.1 (p.4)
![[assets/crops/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-fig01.png]]
> [!tip] 【图文联合解读】**图示 DSpark 三轮解码循环**：
① 目标模型由 prompt A/B/C 自回归生成锚点 D；
② D 进入起草模块——并行主干对 E–H 一次输出 logits，序贯头顺次解码得到置信度 c₁–c₄，硬件感知调度器按置信保留 E/F/G、丢弃低置信的 H；
③ 目标模型并行验证 D–G，接受 E/F（✓），否决 G（✗）并改写为 G* 作为下一轮锚点。

**原文论证**：自回归起草 T_draft∝γ、纯并行起草则牺牲 τ；DSpark 以"并行主干＋序贯头"折中，并以**置信调度**取代定长验证，避免在 c₄ 这类低置信 token 上浪费 T_verify，整体压缩 L = (T_draft + T_verify)/τ。

**论文作用**：作为方法总览图，具象化 Equation 1 的三项延迟权衡，并为 Table 1 中"DSpark 平均接受长度反超 Eagle3"的反直觉结论提供机制支撑。
*caption: Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= (𝑇draft + 𝑇verify)/𝜏. Autoregressive drafters achieve high 𝜏but pay 𝑇d… ｜ 论文 [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] ｜ arxiv 见 MD 元信息*

### JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin — Fig.1 (p.2)
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig01.png]]
> [!tip] 【图文联合解读】**图1解读：**

该图以分组柱状图形式对比三种推测解码方法（DFlash蓝、DDTree橙、JetSpec绿）在四个基准上的端到端加速比。HumanEval：DFlash≈?.4×、DDTree 6.31×、JetSpec **7.12×**；MBPP：3.96/6.09/**6.73×**；LCB：4.70/6.75/**7.67×**；MT-Bench：2.72/4.26/**4.58×**。

原文借此论证两点结论：①树形草稿（DDTree、JetSpec）显著优于块并行草稿（DFlash），证明因果性-效率瓶颈可突破；②JetSpec在所有基准上均取得最高加速，尤其在HumanEval和LCB上较DDTree额外提升约0.6–0.9×。

该图作为开篇主结果图，确立了JetSpec并行树形草稿的SOTA地位，为后续方法详解和消融实验提供总体性能基线。
*caption: End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs across math, coding, and chat benchmarks. DFlash denotes the original b… ｜ 论文 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] ｜ arxiv 见 MD 元信息*

### JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin — Fig.2 (p.3)
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig02.png]]
> [!tip] 【图文联合解读】图(a)横轴为对数刻度γ∈[2,256]，纵轴为加速比，在c=0.05条件下绘制6条曲线对应α=0.70~0.95。数据呈典型"先升后降"形态：α=0.95在γ=16处达~6.5×峰值，α=0.90峰值~4.6×(γ=16)，α=0.85峰值~3.7×(γ=8)，α=0.70仅在γ=2处~2.2×；γ>32后所有曲线骤降至<1.5×，在γ=256收敛至~0.5–1×。

论证结论：即便c已压至0.05，传统推测解码仍存在"加速比天花板"——单纯增大γ收益递减甚至恶化；必须**同时**降低每token起草成本c并提高接受率α才能突破。Table 12给出不同L、N下实测c值，为本图参数标定提供依据。

论文作用：作为Eq.(2)理论预测的可视化锚点，定量揭示传统推测解码γ扩展失效的瓶颈，为JetSpec以**并行树形起草**大幅降低c、从而突破天花板的核心动机提供关键支撑。
*caption: Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Compa… ｜ 论文 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] ｜ arxiv 见 MD 元信息*

### JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin — Fig.3 (p.4)
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig03.png]]
> [!tip] 【图文联合解读】**【核心对象】** 图示JetSpec三阶段流水线：①抽取冻结目标模型 $M_p$ 多层（Layer M…N）中间隐藏态，经Feature Fusion压缩为单条Fused Feature；②以"return"为anchor、γ个[init]为草稿槽，输入m层因果并行Draft Head $M_q$，单次前向产出7节点候选树（return为根，a(s=-0.51)/+(s=-2.48)/B(s=-4.05)/sum(s=-1.39)/b(s=-2.91)等分支）并配tree-causal注意力掩码矩阵；④BFS排序后回灌 $M_p$ 做tree-SD验证。

**【技术结论】** 草稿成本c被压至轻量head级，接受率α借中间层融合特征保持高位，破解c/α权衡，使加速比随γ单调上升。

**【链路作用】** 作为方法总览图，串联"特征抽取→并行树生成→tree验证"完整推理链，为后续实验论证加速上限提供架构依据。
*caption: JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate h… ｜ 论文 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] ｜ arxiv 见 MD 元信息*

### JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin — Fig.4 (p.15)
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图4对比因果头与扩散头从相同前缀"We"出发的草稿树质量。

**核心对象与数据：** 因果头rank-1分支"are told that"忠实（gap=−0.34），验证器接受6 token；扩散头rank-1分支"given told that"不连贯（gap=+42.50，目标联合概率≈e⁻⁶³），仅接受4 token；但扩散头rank-3分支（gap=−3.69）反而忠实。

**关键技术结论：** 扩散头采用分支无关的逐位预测器q_sur，将"given"(depth 1)与"told"(depth 2)独立组合——两者局部合理但全局不相邻，导致rank-1分支虽高概率却全局荒谬。即：树质量而非单一token概率才是speculative decoding扩展的真正瓶颈。

**论文作用：** 揭示并行树草稿在扩散头下的典型失败模式，论证JetSpec需要专门解决"局部合理、全局不连贯"的草稿质量问题，支撑其方法设计的必要性。
*caption: Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft from the same prefix (last token “We”). The causal head’s rank-1 bran… ｜ 论文 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] ｜ arxiv 见 MD 元信息*

### JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin — Fig.5 (p.18)
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig05.png]]
> [!tip] 【图文联合解读】图示注意力掩码矩阵，行=3 blocks × 6 query positions（anchor + 5），列=verified prefix（x₀–x₃）+ sampled blocks。**所有 query 对 verified prefix 全 ✓（黄色）**；仅 block 1 内部呈**左上三角因果掩码**——attend anchor a₁ 及更早位；block 2、3 对 block 1 列**全深紫遮蔽**，实现块间隔离。

该掩码直接支撑 JetSpec 的**并行树形 draft 训练机制**：使多个采样块在同一前向中并行计算的同时，仍保留块内自回归约束与块间独立性，避免长串行展开；从而把 draft 规模从线性扩展转为批量扩展，论证其打破 speculative decoding 缩放上限的核心技术结论。
*caption: Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor pl… ｜ 论文 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] ｜ arxiv 见 MD 元信息*

### JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin — Fig.6 (p.19)
![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图中展示 JetSpec 的**训练块采样结构**：每个 block 含 1 个 anchor（隐于上下文、无 loss）与多个 future token（带 loss），具体可见三行共 9 个标注 "loss" 的橙色块，索引形如 b_{i,j}（i=block 行号 1–3，j=块内位置 3–5），对应"predicted token position with loss"。

原文借此论证关键结论：通过 block-wise 采样把 anchor 留作上下文、仅对 future 位置施加 loss，使因果 draft head 能在**冻结目标模型**条件下，以目标模型特征为条件学习多 token 联合预测，从而支撑其并行树状 draft 的可扩展性，缓解传统 speculative decoding 的 scaling ceiling。

在整体链路中，此图属于**训练策略说明**模块，与 §3.3 的 draft head 设计衔接，为后续实验（墙钟加速比）提供方法论基础。
*caption: Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss… ｜ 论文 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.1 (p.1)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图含四个子图（256/1024/4k/16k GPU），散点横轴为GPT-3迭代时间(s)、纵轴为网络成本($)，颜色编码NIC端口数/GPU(1–8)，每图标注Best Performance、Cost-effective(ZCube)、Budget-friendly(BCube)三点，并对比HPN、Rail-only、3-layer Rail、Optimized FT等基线。

**关键结论：** 四种规模下ZCube均稳定落在帕累托前沿中段——相对BCube迭代时间显著缩短，相对HPN/Optimized FT网络成本大幅下降，论证其是兼顾性能与成本的最优折中拓扑。

**论文作用：** 该图为ATOP自动化搜索的核心产出，证明搜索可跨规模一致定位ZCube式优解，为后续ZCube拓扑推广与大规模训练实验提供实证支撑。
*caption: ATOP search results on different GPU scales, each point representing a topology. For each scale, we label the three notable points in each plot: Best … ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.2 (p.3)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图2展示rank 0在interleaved 1F1B调度下GPT-3训练的时间线（TP通信省略），含4条并行轨道：Comp呈"6个连续F → B-F-B-F → 约9个连续B"的交错模式；DP Comm中4次AG对齐前段F、5次RS对齐尾部B；PP Send/Recv以细粒度蓝/红短竖线密集散布于整个时间轴。

**论证结论**：在3D并行（TP+DP+PP）下，即使TP通信被吸收到节点内网络，PP与DP通信仍以高频、细粒度方式贯穿训练全程，形成持续且并发的集合通信流量——传统"少量大消息"优化范式难以将其聚合吸收。

**论文作用**：该图为后文ZCube拓扑设计提供关键流量驱动力——揭示经典Fat-Tree对并发、细粒度、多模式流量效率不足，从而论证需要面向LLM训练特征定制网络拓扑，并以ATOP自动化流水线辅助决策。
*caption: GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excluding TP communication as it typically occurs on the intra-server netw… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.3 (p.4)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**(a)** 256-GPU全互联流量下每100Gbps承载最大流数对比，BCube/ZCube/Best-perf三种配置分别为约2.5/1.2/0.4，BCube最高但Rail-only存在"Can't Comm"异常；(b) 4k-GPU GPT-3单ToR故障退化率：ZCube仅2.8%（成本54%），低于HPN 9.0%、BCube 15.0%、ROFT 46.9%、Rail-only 46.2%，甚至优于成本318%的Best-perf（8.3%）。

**技术结论：** ATOP自动生成的ZCube以约一半成本实现比ROFT/HPN更优的故障鲁棒性，且all-to-all带宽无通信异常，证明自动化设计能突破人工直觉局限。

**论文作用：** 作为核心定量证据，串联"自动管线→新拓扑产出→成本/带宽/容错综合优越性"三段论证，支撑ZCube作为大规模模型训练高性价比拓扑的主结论。
*caption: (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs topology. (b) The performance degradation of GPT-3 training after a Sin… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.4 (p.5)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图刻画ATOP流水线的三大功能模块及闭环数据流：①**Topology Modeling**（拓扑建模）接受"Topology Constraints"与"Optimization Objectives"输入，生成"Search Space"；②**Topology Optimizer**与**Topology Evaluator**构成"Optimization Loop"，前者输出"New Topologies"，后者回传"Topologists' Performance"形成反馈迭代；③最终输出"Optimal Topology"。原文以此论证ATOP具备**自动化探索非对称/非传统拓扑**的能力，突破人工设计的局限，为后文ZCube（中层交换机需额外端口的非对称结构）等创新拓扑的自动生成奠定方法论基础，是论文由"经验驱动"迈向"搜索驱动"网络架构设计的核心技术骨架。
*caption: Overview of ATOP allows the system to explore novel topology designs automatically, not limited to variants or combinations of existing ones. It can p… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.5 (p.6)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig05.png]]
> [!tip] 【图文联合解读】图5展示ATOP构建层间与层内连接的3步流程。上半部（层间）：8个GPU搭配N₂=4、N₃=2两层交换机，经块划分H¹₁₂=4、H²₁₂=2、H³₂₃=1（其中H¹₁₃=H²₁₃=0）、块间连接E₁₂=1、E₂₃=2形成层次拓扑；下半部（层内）：在S¹₁=4×S¹₂=2二维网格上按P¹₁=3、P¹₂=1向上连线，再由A、C参数确定各维连接模式。它论证ATOP仅以少量离散超参即可参数化复杂拓扑，未指定值默认0实现稀疏搜索，是理解其搜索空间结构与后续Z-Cube等自动化优化实验的方法基础。
*caption: Examples of constructing inter-layer and intra-layer connections in ATOP. Unmentioned hyperparameters = 0.… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.6 (p.9)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1）核心对象与数据：** 图6展示4k GPU拓扑搜索中两种散点图——(a) Pareto最优集与(b) 全部候选集。横轴为GPT-3-175B迭代时间(2.5–5.0 s)，纵轴为网络成本(0–1.2×10⁸美元)，颜色按每GPU NIC端口数(1–8)分级。图中标注五个关键拓扑：Best Performance、Cost-effective (ZCube)、Budget-friendly (BCube)、HPN、Rail-only、3-layer Rail-Optimized FT。

**2）关键结论：** ZCube位于Pareto前沿左下端，成本约1500万美元、迭代时间约2.75 s，显著优于HPN/Rail-only/3-layer FT（同性能下成本更低、同成本下速度更快），同时靠近BCube但训练速度更优，验证其"高性价比"特性。

**3）论文作用：** 通过对比(a)稀疏Pareto前沿与(b)海量候选，量化展示ATOP搜索管线的剪枝效率与多目标权衡能力，为ZCube设计选择提供实验依据，支撑全文"自动化优化产出实用低成本拓扑"的核心主张。
*caption: During the 4k GPUs search process: (a) The Pareto- optimal topologies generated by ATOP; (b) All the topologies generated by ATOP.… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.7 (p.9)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig07.png]]
> [!tip] 【图文联合解读】图7含两幅散点图：(a)调整4k-GPU DCN、(b)1k→4k扩展。横轴GPT-3-175B迭代时间2–7s，纵轴网络成本1–5×10⁷美元，色编码NIC端口数(1绿/2橙)。ATOP搜索的拓扑散点与BCube/Rail-only/HPN/3-layer Rail-Optimized FT/极优解/极省解基线共绘，ZCube落于帕累托拐点，性能-成本双优。该图证明ATOP在4k-GPU规模及扩展场景下能自动发现优于经典拓扑的ZCube方案，是验证ZCube核心优势与ATOP搜索能力的关键实验证据。
*caption: (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The search results when expanding a DCN from 1k GPUs to 4k GPUs. be unfair t… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.8 (p.10)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig08.png]]
> [!tip] 【图文联合解读】**图8联合解读（≤220字）**

图(a)展示ZCube(n,k+1)的递归构造：由n个ZCube(n,k)子立方与n^k台新增顶层交换机堆叠而成，每GPU配k+1端口NIC（Level 0~k）。图(b)给出ZCube(2,3)实例：3层级、8台GPU（编号000~111）、8台交换机，验证小规模拓扑正确性。图(c)展示ZCube(84,3)-partial：84个Pod，每Pod 84台GPU，Level 1与Level 2各7056（=84²）台交换机，仅显示代表性连线，验证万卡级可扩展性。论文借此论证ZCube支持多端口NIC灵活部署、可线性扩展至大规模集群，是ATOP自动化拓扑流水线输出高性价比低成本网络的核心结构证据，区别于传统Fat-Tree/Dragonfly等高成本方案。
*caption: (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An example of ZCube(2, 3). (c) An example of ZCube(84,3)-partial. ZCube(𝑛,𝑘+ … ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.9 (p.11)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig09.png]]
> [!tip] 【图文联合解读】**图9解读：**

图9展示1024/4096/16384 GPU三种规模下，GPT-3 175B与MoE-GPT在ZCube、HPN、Rail-only、ROFT、BCube、Dragonfly六种拓扑上的迭代时延（柱状）与建网成本（底部标注）。16384 GPU时ZCube(128,2)为4.95s/6.06s、成本$57.28M，HPN为5.10s/$84.03M，Dragonfly虽最省($45.35M)但时延飙至10.34s/13.79s，规模越大差距越显著。结论：ZCube时延全面最优且成本具强竞争力，验证ATOP自动化管线产出高性价比拓扑。该图将"时延—成本"二维Pareto前沿具象化，是支撑ZCube作为大模型训练推荐拓扑的核心实验证据。
*caption: The training iteration time for GPT-3 175B and MoE-GPT models and the corresponding network costs on various topologies, under different numbers of GP… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.10 (p.11)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1. **核心对象与数据**：图为16384 GPU训练GPT-3 175B单次迭代中PP流完成时间（FCT, μs, 对数刻度2⁷~2¹¹）的CDF，4条曲线对比ZCube(128,2)、HPN、Rail-only、ROFT。ZCube在~2⁷ μs处陡升至≈0.93，几乎全部流在2⁸.⁵ μs前完成；HPN/Rail-only次之，约2⁸~2⁹ μs达1.0；ROFT最差，曲线在CDF≈0.5处出现长平台，部分流延迟至~2¹⁰ μs才完成，长尾显著。

2. **关键结论**：在PP同步密集流量下，ZCube将流完成时间压缩到远低于传统HPN/Rail-only，并彻底消除长尾，证明其对PP关键路径的低延迟保障。

3. **论文作用**：作为Pipeline Parallelism维度的关键实验，与DP/NP维度的对比图共同构成"三类并行流量×多拓扑"的性能证据链，支撑"ZCube在大模型训练中全面优于现有拓扑"的核心论点。
*caption: CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 GPUs. GPU clusters, the failure probability of a single switch is 0.03%… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.11 (p.12)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig11.png]]
> [!tip] 【图文联合解读】**图11解读：**

该图展示(a) ROFT实测拓扑：4台Spine交换机与4台Leaf交换机组成全连接Clos结构，下连4台服务器（每机含4张GPU与4个NIC），上行链路400Gbps，每台Leaf全互联至全部Spine，构成典型胖树全互联模式。

**关键论证：** 通过ROFT与ZCube并列对比，原文用以说明传统全互联Clos开销巨大（链路数随端口数平方增长），而ZCube以更高成本效益的精简拓扑实现等价训练通信模式，验证"高成本效益大模型训练网络"的核心结论。

**链路作用：** 作为全文方法论的实测落地证据，承接自动化拓扑优化流水线（ATOP）的设计输出，为ZCube在真实测试床上的可行性与性能优势提供可视化与定量支撑。
*caption: The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G 4G 16G… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.12 (p.12)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图12以双柱状图对比ROFT与ZCube(4,2)在真实部署中的集合通信性能。横轴消息尺寸1M–16B/16G共8档，纵轴为BusBw：上子图All-reduce在64M处达≈130 GB/s，256M后稳定于≈190 GB/s；下子图All-to-all在64M后稳定于≈55–60 GB/s。两图所有尺寸下两种拓扑的柱高近乎重合，差异落在误差棒内。

原文据此论证关键结论：尽管ZCube仅采用48条200G链路（ROFT为32条400G），硬件成本降低25%，All-reduce与All-to-all吞吐量却与ROFT完全持平；同时因网络直径更短，进一步带来最高7%的LLM训练加速。

该图在论文链路上扮演"真实硬件落地验证"角色，将拓扑优化的纸面设计优势转化为可复现的实测带宽证据，为"以低成本达成等效集合通信性能"的核心主张提供最终支撑，衔接理论分析与端到端训练成本论证。
*caption: Collective communication performance on real- world deployment. ZCube and ROFT achieve the same all-reduce and all-to-all perfor- mance, while ZCube r… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.13 (p.15)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 13）：**

**1) 核心对象与数据：** 散点图展示 Case 3 搜索结果中 1k↔4k GPU 拓扑扩展的 Pareto 关系。横轴为 GPT-3-175B 迭代时间（2.0–7.0 s，越低越好），纵轴为修改链路数（0–4×10⁴，成本指标），颜色编码 NIC Ports/GPU（1 或 2）。标注的关键拓扑包括：Best Performance（红星，约 2.5 s / 1.8×10⁴）、HPN（~3.0 s / 1.4×10⁴）、3-layer Rail-Optimized FT、Rail-only、BCube，蓝色曲线为搜索得到的 Pareto 前沿。

**2) 关键结论：** 图中红色箭头将搜索空间划分为"Cost-effective (ZCube)"区域（左上，性能接近最优且修改链路可控）与"Budget-friendly"区域（右下，迭代时间略增但成本最低）。ZCube 落在高性价比象限——以显著少于 Best-Performance 方案的链路改动获得接近最优的训练时延，证明其在性能-成本权衡上全面优于 HPN、BCube、Rail-only 等人工基线。

**3) 在论文链路中的作用：** 作为 Case 3（千卡↔四千卡扩展场景）的成本维度证据，该图与其它性能/成本图共同支撑论文核心主张——ZCube 是"highly cost-effective"的自动拓扑优化结果，将搜索空间可视化以直观证明自动化管线能找到优于人工设计的 Pareto 最优解。
*caption: In the search results of Case 3, the comparison between the number of modified links (another cost metric) and training performance.… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.14 (p.15)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示了 ATOP 对 16k GPU 多租户数据中心网络的搜索结果：横轴为平均迭代时间（~2.4–4.5 s），纵轴为网络成本（0–3.5×10⁸ 美元），散点按单 GPU NIC 端口数（1–8）着色，并勾勒出蓝色 Pareto 前沿。

图中将 ZCube（红箭头标注）定位于"代价敏感区间"：其平均迭代时间约 2.6 s，成本约 7.5×10⁷ 美元，性能接近 HPN、Rail-only 及 3-layer Rail-Optimized FT 等基线；相比顶部"Best Performance"方案（≈2.45 s、2.5×10⁸ 美元）成本下降约 3×，仅延迟小幅增加，而 BCube 则处于"预算友好"区但迭代时间更慢。

该图作为 Use Case 4 的核心证据，证明 ATOP 能在 Pareto 前沿上自动发现兼顾性能与成本的多租户拓扑——尤其凸显 ZCube 在性能—成本权衡上对 HPN/Rail-only/FT 等传统方案的替代优势，支撑论文"高性价比大规模训练网络"的总体结论。
*caption: The search results of ATOP when building a new data center for multi-tenancy.… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.15 (p.15)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig15.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示ATOP在**4k GPU异构DCN、严格搜索空间**下的Pareto搜索：横轴为GPT-3-175B迭代时间（约6.8–10.5 s），纵轴为网络成本（约$9M–$20M），散点按每GPU NIC端口数着色（绿色代表1端口），并绘有左下凸的Pareto前沿曲线。图中标注三个关键方案：**Best Performance**（~6.9s, $15M）、**Cost-effective**（~7.2s, $10M），以及对比基线**3-layer Rail-Optimized FT**（~7.5s, $16.5M）。

**技术结论**：即便在严格搜索空间约束下，ATOP仍能同时优化性能与成本——其Cost-effective方案较Rail-Optimized FT基线仅微增迭代时间，却显著降低成本；Best Performance方案亦全面优于FT基线，验证了搜索质量。

**作用**：在"新建异构数据中心"场景下证明ATOP的通用性与有效性，是论文"自动化拓扑搜索→推荐拓扑"完整实验链路的关键支撑。
*caption: The search results of ATOP when building a new heterogeneous data center with strict search space con- straints.… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.16 (p.16)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**(1) 核心数据：** 图(a)显示Pareto最优拓扑数随生成总量从0增至约4500–5400后趋于饱和；图(b) Jaccard距离由约0.55–0.6骤降至接近0；图(c) HyperVolume由0快速攀升至≈0.97–1.0，三者在约20000个拓扑后均稳定。四种规模（256/1024/4096/16384 GPU）曲线高度一致。

**(2) 关键结论：** ATOP在生成约2万拓扑后即可收敛——Pareto集大小饱和、代际间Jaccard距离归零、目标空间覆盖度趋近完备，表明算法收敛快、结果稳定，且结论在跨数量级搜索规模下保持一致。

**(3) 论文作用：** 该图为ATOP搜索效率与可扩展性提供经验证据，为后续在小规模搜索中发现的ZCube拓扑迁移至大规模集群（最高16384 GPU）的合理性提供收敛性背书，衔接ATOP与ZCube方法链。
*caption: During the ATOP optimization process: (a) The relationship between the number of Pareto-optimal topologies and the total number of topologies generate… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.17 (p.17)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig17.png]]
> [!tip] 【图文联合解读】图(a)为两层无阻塞 Rail‑Fat‑Tree：R个Pod、M个Spine；每Pod有M台Server、每台K个GPU（Leaf亦为K），N=RMK。跨Pod的N路流经ECMP，橙色流会争用同一出口。(b)为BCube(1)：有n个L1/L0交换机，每Server有n个GPU/NIC；约n²量级流量需经NIC转发，特定All‑to‑All并非全二分带宽。论文借此说明ECMP碰撞与NIC瓶颈会导致降速，并引出自动寻优及ZCube低成本高带宽方案。
*caption: Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-blocking 2-layer Rail-Optimized… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.18 (p.17)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig18.png]]
> [!tip] 【图文联合解读】**图18图文联合解读**

该图在4096 GPU规模下，对比9种拓扑（ROFT、BCube(64,2)/（16,3）、ZCube(64,2)/（16,3）及其partial、HPN、Dragonfly、Rail-only）在链路口故障率0–15%下group all-to-all的平均JCT及标准差带。数据显示：Dragonfly对故障极敏感，JCT由约0.9s飙升至1.7s；Rail-only与ROFT劣化至约1.2s；而ZCube(16,3)-partial、ZCube(64,2)、ZCube(16,3)与HPN始终维持在0.6s左右，曲线平缓且方差带窄。

原文借此论证：ZCube族（尤其是partial变体）在链路失效场景下具备最优鲁棒性与低延迟，验证其作为大规模训练高性价比拓扑的可行性。该图是论文实验链路的**容错性评估环节**，与性能、成本图共同支撑ZCube优于Dragonfly/BCube/HPN的核心结论。
*caption: The average JCT for group all-to-all communica- tion under different topologies with link failures on 4096 GPUs, with shading representing the standar… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.19 (p.18)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig19.png]]
> [!tip] 【图文联合解读】**图19联合解读：**

**核心对象与数据：** 左图为ROFT、右图为ZCube在Allreduce操作下的实测（TestBed，蓝实线）与仿真（Simulation，橙虚线）BusBw对比。横轴为消息规模（1M–16G），纵轴为BusBw（GB/s）。两图趋势高度一致：小消息（1M）约5 GB/s；16M处约40 GB/s；64M时TestBed约135、Simulation约115 GB/s出现可见差距；256M后均饱和于~195 GB/s。

**关键技术结论：** 仿真曲线在饱和段与实测几乎重合，仅在中段（64M–256M）小幅低估，说明带packet spraying的数据包级仿真能较准确预测ROFT与ZCube两种拓扑的真实网络带宽性能，验证了仿真方法的可信度。

**论文作用：** 该图是仿真→实测闭环验证的关键证据，支撑论文以仿真驱动拓扑优化搜索的设计，证明所提出的自动化拓扑优化流水线（ATop→ZCube）所选拓扑在真实部署中具有可预期的高性能。
*caption: Comparison between packet-level network simulation (with packet spraying for load balancing) and the real-world testbed in §6.2. I… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.20 (p.19)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig20.png]]
> [!tip] 【图文联合解读】**图20联合解读：**

图20含两幅FCT CDF图。左图"All-to-all"（0.8–2.0ms）：NS-3（蓝）与Flow-level simulator（橙）曲线形态高度吻合，仅NS-3略偏左（完成稍快）；右图"GPT-3-22B训练"（0–0.03s）：Astra-sim+NS-3与Astra-sim+Flow-level simulator曲线在≈0.001s处急升并几乎重合，整体分布一致。

**技术结论：** 包级NS-3与流级仿真器在合成All-to-all流量及Astra-sim驱动的真实大模型训练流量下，FCT分布均高度吻合，验证了流级仿真对包级仿真的高保真度。

**论文作用：** 作为Astra-sim驱动的拓扑优化流水线中仿真器的可信度校验，使作者能以低开销流级仿真替代高开销NS-3，从而支持对大规模模型训练网络拓扑进行高效、自动化的搜索与评估。
*caption: Comparison of the CDF of flow completion times between NS-3 and flow-level simulators.… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.21 (p.20)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig21.png]]
> [!tip] 【图文联合解读】**图21图文联合解读**

图21展示基于51.2 Tbps交换机的**ROFT拓扑**，承载16384 GPU集群。三层结构：**Core层**128台（128×400G端口）下连4个Super-Pod；每Super-Pod含**64个Spine**（64×400G上/下行），覆盖8个Pod；每Pod含**8个Leaf**（64×400G）接64台服务器，每台配8 NIC（512服务器/Super-Pod，集群共2048台）。该图论证ROFT通过"三层Fat-Tree+rail对齐"实现每NIC绑定固定rail，使全部16384卡获得等价带宽并避免oversubscription，在论文中作为ATOP自动化优化管线的核心cost-effective方案，与Figure22 rail-only、Figure23 HPN对比，最终推出Figure24 ZCube更优解。
*caption: ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.22 (p.20)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig22.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 22 – Rail-only 拓扑）：**

1）**核心对象与结构**：16384 GPU 集群采用 Rail-only 拓扑，每条 Rail 独立成 2 层 CLOS。共 8 条 Rail 互连，单条 Rail 含 16 个 L2 SW（128×400G）下连 32 个 Pod 的 L1 SW，每个 L1 SW 服务 64 台服务器（Pod 内共 2048 台/rail，集群合计 16 384 GPU）。L2↔L1 用 4×400G 全连接，每台服务器 8 个 NIC 分别绑定到 Rail 1–8。

2）**关键技术结论**：Rail 内部为独立 2 层 CLOS，L2 SW 与 32 个 Pod 的 L1 SW 全相连，提供 rail 内 full-bisection 带宽以承载张量并行的密集通信；同时规避 3 层 Fat-Tree 的规模与成本开销。

3）**论文作用**：作为 ROFT、HPN、ZCube 等候选方案之外的 baseline 参考，用以凸显 ZCube 在 cost-effective 与大规模训练带宽利用率上的优势。
*caption: Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with … ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.23 (p.20)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig23.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 23 – HPN 拓扑）：**

1）**核心对象**：基于51.2 Tbps交换机的16384 GPU集群HPN双端口设计。128台Spine（128×400G）经全互联下连16个Pod，每Pod含16台Leaf（64×400G上行+128×200G下行），每Leaf下挂128台双端口服务器（2×200G NIC，共2048台×8 GPU=16384 GPU）。

2）**关键技术结论**：通过双端口折叠设计，将两个Fat-Tree Pod合并为一个，服务器仅需2块NIC（而非ROFT的8块），在保留三级CLOS带宽的同时显著降低交换机与网卡规模，提升成本效益。

3）**论文作用**：作为HPN候选方案，与Figure 21/22的ROFT及Rail-only方案并列，共同构成自动化拓扑优化流水线（ATOP）的输入设计空间，供ZCube与对比基线在规模、成本与性能维度进行量化评估。
*caption: HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### From ATOP to ZCube: Automated Topology Optimization Pipeline — Fig.24 (p.20)
![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig24.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示 ZCube(128,2) 拓扑结构：顶层 128 台 L2 交换机（每台 128×200G + 128×200G 双端口，总 51.2 Tbps），通过紫色/橙色**跨 Pod 对角链路**下连 128 台 L1 交换机；每台 L1 直连 16 台服务器（2×200G，8 NIC），共 2048 台 ×8 NIC=16384 GPU。

原文借此论证：ZCube 利用 L2↔L1 对角跳线替代传统 Fat-Tree 的中间层交换，使跨 Pod 通信跳数更少、层级更扁平，在 51.2 Tbps 交换容量下达成显著优于 ROFT/HPN 的成本-效益折中。

在论文中，该图作为自动化拓扑优化流水线输出的代表性候选方案，与 Fig21–23 的 ROFT、Rail-only、HPN 横向对比，共同支撑大规模模型训练网络"拓扑—成本—性能"联合评估的实验链路。
*caption: ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880… ｜ 论文 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.1 (p.1)
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig01.png]]
> [!tip] 【图文联合解读】## Figure 1 图文联合解读

**1) 核心对象与数据：**
该图为多面板条形图，对比 Kimi K2.5（蓝色 K 标）与 Claude Opus 4.5、Gemini 3 Pro 及另两款模型在四大类基准上的得分：
- **Coding – SWE-bench Verified**：K2.5 = 76.8，其余为 80.0 / 80.9 / 76.2
- **Coding – SWE-bench Multilingual**：K2.5 = 73.0（最高），余为 72.0 / 77.5 / 65.0
- **Video – VideoMMBU**：K2.5 = 86.6（领先），余为 85.9 / 84.4 / 87.6
- **Video – LongVideoBench**：K2.5 = 79.8（大幅领先），余为 76.5 / 67.2 / 77.7
另有 SearchQA（76.1 vs 63.2）与视频类基准（87.7 vs 88.5）的局部对比。

**2) 关键论证结论：**
K2.5 在 **多语言代码修复**与**长/多模态视频理解**任务上取得 SOTA，在 SWE-bench Verified 上接近最优，证明其在视觉-智能体（coding + video）双线均具竞争力。

**3) 在论文中的作用：**
作为首页总览图，定量支撑论文核心卖点——"visual-agentic intelligence"，为后续 Table 1 的联合训练策略消融提供基线锚点。
*caption: Kimi K2.5 main results. 1… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.2 (p.4)
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig02.png]]
> [!tip] 【图文联合解读】**图2联合解读：**

**① 核心数据**：图含两条RL训练曲线。左图MMMU Pro（粉）起点≈0.71–0.72，随RL FLOPs攀升并逼近≈0.76虚线参考；右图（绿）起点≈0.69，最终稳定在≈0.78左右，基线虚线位于≈0.70。两条曲线均呈持续上升趋势并伴随明显振荡收敛。

**② 关键结论**：作者以"minimal zero-vision SFT"为起点，仅靠加大视觉RL算力即在两个基准上获得显著且单调的增益（MMMU Pro +4–5pp，右图 +8–9pp），证明无需预先大量视觉微调，长程RL即可"涌现"出鲁棒的视觉能力。

**③ 方法链路作用**：此图为全文核心证据——支撑"文本能力先于视觉激活、视觉能力由RL后激活获得"的设计哲学，与Table 2的跨模态迁移结果呼应，共同论证MoE+RL的后训练范式无需显式视觉SFT即可获得多模态智能。
*caption: Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.3 (p.5)
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示 Agent Swarm 系统架构。**核心对象**：左侧为可训练 Orchestrator，配备 create_subagent、assign_task、search、browser 等工具；右侧为动态生成的约 6 类冻结子智能体（AI / Physics / Life Sciences / Anthropology Researcher、Fact Checker、Web Developer），每个内置搜索与浏览工具。**结构与数据**：Orchestrator 先执行"create subagents"并收到 success 回执，再分两批"Assign Tasks"——首批拆为 100 个子任务（4×AI Researcher + 1×Physics + 4×Life Sciences + 1×Anthropology），次批 25 个（2×Fact Checker + 1×File Downloader + ... + Web Developer），各子智能体并行完成后逐一回传 task N result，最终聚合为 Final Results。**论证结论**：可训练 Orchestrator 通过"动态创建专用子智能体 + 任务并行分解 + 结果汇聚"实现复杂任务的分布式高效执行。**论文作用**：该图是 Kimi K2.5 方法链路的架构骨架，定义了"一个训练中枢 + 多个冻结专家"的协同范式，为后续能力扩展与实验评测提供框架基础。
*caption: An agent swarm has a trainable orchestrator that dynamically creates specialized frozen subagents and decomposes complex tasks into parallelizable sub… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.4 (p.6)
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig04.png]]
> [!tip] 【图文联合解读】**图4 图文联合解读**

图含左右两子图，横轴均为 RL flops。左图（Training Accuracy vs Steps）以散点+红色平滑曲线呈现训练准确率，由初始约 36% 平滑上升至末段约 64%；右图（Average Parallelism vs Steps）显示平均并行度：初期约 8.5、中段长期平稳徘徊于 7.5–9、后期加速攀升至约 14。

该图以双指标共演化论证两点核心结论：① 并行 Agent 强化学习训练过程平稳收敛、无发散崩溃，证明 r_finish 等奖励机制驱动的训练可行性；② 准确率与并行度同向增长，说明模型不仅"答对任务"，还主动学习提升任务分解的并行深度，回应了正文中"避免无意义切分过多子智能体"的设计目标——分解是有效而非冗余的。

在论文方法链中，该图承担 RL 后训练阶段"策略正确性 + 并行分解合理性"的双重实证支撑，为后续 agentic 能力评测提供训练可信度背书。
*caption: In our parallel-agent reinforcement learning environment, the training accuracy increases smoothly as train- ing progresses. At the same time, the lev… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.5 (p.10)
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **图表内容**：左雷达图为"Performance (%)"，覆盖 AIME2025、GPQADIAMOND、HMMT25_Feb/Nov、MMLUPro、LiveCodeBenchV6 及 Overall 共 7 个基准；Toggle 前（灰虚线）vs 后（蓝实线）显示 5 项提升（如 LiveCodeBenchV6 +2.2%、AIME2025 +1.1%）、2 项下降（GPQADIAMOND −1.0%、MMLUPro −2.0%），Overall +0.3%。右雷达图为"Token Usage"，7 项全部减少（绿标 0 增加），幅度 −745 至 −8127 tokens，Overall 节省 4791。

2) **关键结论**：token-efficient RL 在 7 个基准上**全部**显著降低 token 消耗，同时整体性能仅微涨 0.3%，证明"省 token 不损精度"。

3) **论文作用**：作为方法有效性的核心证据，支撑 Kimi K2 Thinking "降本保效"的核心卖点，为后续推理效率与多模态训练优化提供量化锚点。
*caption: Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL. compromise alleviates memory pressure, it does not … ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.6 (p.14)
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig06.png]]
> [!tip] 【图文联合解读】**注意**：所提供图片实为一张性能对比表格，与caption所述"词云"不符，以下按图像实际内容解读。

该表横向比较K2.5 Agent Swarm、Kimi K2.5、Claude Opus 4.5、GPT-5.2、GPT-5.2 Pro在三项基准上的得分：BrowseComp为78.4/60.6/37.0/65.8/77.9；WideSearch为79.0/72.7/76.2/—/—；In-house Swarm Bench为58.3/41.6/45.8/—/—。

论证结论：Agent Swarm相对Kimi K2.5基座在BrowseComp提升17.8分、In-house Swarm Bench提升16.7分，且在BrowseComp以78.4超越GPT-5.2 Pro（77.9），证明Orchestrator动态调度多异构子代理的架构有效。

整体作用：作为论文方法链路的终点证据，量化呈现"Orchestrator+子代理群"框架相比单模型基座与同级前沿模型的综合优势。
*caption: The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.7 (p.14)
![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig07.png]]
> [!tip] 【图文联合解读】**图7实质为一张多基准成绩对比表**（caption仅提BrowseComp，但实际涵盖三项）：列依次为K2.5 Agent Swarm、K2.5 单代理基线（即Discard-all）、Claude Opus 4.5、GPT-5.2、GPT-5.2 Pro；行依次为 BrowseComp（78.4 / 60.6 / 37.0 / 65.8 / 77.9）、WideSearch（79.0 / 72.7 / 76.2 / — / —）、In-house Swarm Bench（58.3 / 41.6 / 45.8 / — / —）。

**技术结论**：Agent Swarm在三项基准上均大幅超越Discard-all基线——BrowseComp +17.8、WideSearch +6.3、Swarm +16.7，并在BrowseComp上反超GPT-5.2 Pro（77.9）、远超Claude Opus 4.5（37.0），印证"Orchestrator主动上下文分片优于被动压缩"。

**在论文中的作用**：作为核心实验证据，验证多代理编排方法相较单代理上下文管理的有效性，并完成K2.5与顶级闭源模型的横向定位。
*caption: Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context management in BrowseComp. (60.6%) and surpassing even GPT-5.2 Pro (77.… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.8 (p.15)
![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]]
> [!tip] # Figure Description

**Note:** The figure graphic itself is not rendered on this page — only the caption and surrounding text are visible. The following description is inferred from the caption and page context.

**Architecture/Components/Data Flow (inferred from caption):**
- **X-axis:** Target Item-F1 (information coverage/quality metric), ranging from 30% → 70%
- **Y-axis:** Execution time (latency)
- **Two curves compared:**
  - Agent Swarm (multi-agent parallel orchestration)
  - Single-agent baseline (sequential execution)
- **Benchmark:** WideSearch — a wide-scope search/retrieval task

**Key Technical Takeaway (≤120 words):**
The figure demonstrates that Kimi K2.5's Agent Swarm delivers a **3×–4.5× latency reduction** over single-agent baselines on the WideSearch benchmark, with the speedup *widening* as task complexity (target Item-F1) increases from 30% to 70%. This means parallel sub-agent orchestration scales favorably with task difficulty — the harder and broader the search, the more Agent Swarm outperforms sequential execution. The result validates the system's design choice of concurrent execution of heterogeneous sub-tasks with selective context persistence, enabling lower inference latency without sacrificing answer completeness on complex agentic workloads.

---

# Caption Verbatim Transcription

> **Figure 8:** Agent Swarm achieves 3 –4.5 faster execution time compared to single-agent baselines as target Item-F1 increases from 30% to 70% in WideSearch testing.
*caption: Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent baselines as target Item-F1 increases from 30% to 70% in WideSearch testin… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.9 (p.21)
![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]]
> [!tip] # Figure 9 Description

**Architecture/Components/Data Flow:**
The figure displays learning curves (loss/accuracy vs. training steps) plotted on a Cartesian grid for three vision-to-text token ratio configurations—**10:90, 20:80, and 50:50**—under a *fixed* overall vision-text token budget. The x-axis represents training progression (steps/tokens consumed), while the y-axis tracks task performance, with separate curves likely shown for vision tasks, language tasks, and joint bi-modal benchmarks. Three colored lines distinguish the ratios, enabling visual comparison of convergence speed, asymptotic performance, and training stability across ratios.

**Key Technical Takeaway (≤120 words):**
Early fusion combined with **lower vision ratios (e.g., 10:90 or 20:80)** yields superior convergence and bi-modal competence compared to the 50:50 configuration. Higher vision ratios cause a "dip-and-recover" pattern, where text capability degrades mid-training before recovering, indicating a modality domain shift. Co-optimizing vision and language from the outset enables smoother gradient landscapes and prevents representation collapse, reinforcing that native multimodal pre-training with moderate vision weight achieves more robust cross-modal alignment under fixed token budgets.

---

**Caption (verbatim):**
> Figure 9: Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under **fixed** vision-text token budget across vision and language tasks. Early fusion with lower vision ratios tend to yield better results.
*caption: Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixed vision-text token budget across vision and language tasks. Early fus… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.10 (p.23)
![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]]
> [!tip] # Figure 10: Overview of Agentic RL Framework

**Architecture/Components & Data Flow:**

The figure depicts a modular agentic RL training framework organized around a central **Rollout Manager** that orchestrates up to ~100,000 concurrent agent tasks as independent asynchronous coroutines. Each task acquires an environment instance from a managed pool (equipped with sandbox and specialized tools) and recursively triggers sub-task rollouts, enabling multi-agent paradigms and partial rollouts.

The framework is built from composable, pluggable modules wrapping the core agent loop:
- **Tool/Sandbox module** — heterogeneous tool execution with sandboxing
- **Reward module** — multi-faceted reward signal composition
- **Prompt diversification module** — prompt variation
- **Instruction-following module** — instruction adherence enhancement

Inference engine outputs flow back through a **train-inference co-design** layer that records log-probabilities for mismatch correction, with a proxy service bridging black-box LLM-API environments into the custom protocol.

**Key Technical Takeaway:**
The core innovation is treating every agent task as an independent async coroutine with a **dedicated Rollout Manager**, enabling 100,000-way concurrency, recursive sub-task rollouts, and partial rollout control — making complex multi-agent training tractable while keeping sandboxing, reward composition, and prompt diversification as orthogonal, pluggable modules.

---

**Caption (verbatim):**

> Figure 10: Overview of our agentic RL framework.
*caption: Overview of our agentic RL framework. environments with minimal overhead. Our design prioritizes compositional modularity by integrating a suite of pl… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.11 (p.28)
![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]]
> [!tip] **Description of the figure area:**

The figure content itself is not rendered/visible in this image — the main body of the page appears as blank white space, suggesting the qualitative example (likely screenshots/frames of a gameplay playthrough) failed to load or is missing. No architecture, components, or data flow diagrams are visible to describe.

**Key takeaway from caption:** Kimi K2.5 uses parallel visual agents to analyze long-form, high-resolution video (32 videos at 1080p) — demonstrating multi-hour video understanding via parallelization rather than sequential frame processing.

**Caption (verbatim):**

> Figure 11: Qualitative example of Kimi K2.5 analyzing a complete playthrough of [overlapping/unreadable characters] 24 hours of continuous gameplay across 32 videos at 1080p using parallel visual agents. See generated webpage and source videos (all rights reserved by source authors).

*Note: There is visible text-overlap/garbling near "playthrough of " in the original PDF rendering (e.g., characters resembling "𝒢𝒰𝒱𝓏𝓊") where an inline object/image collides with the caption text, making one word illegible.*
*caption: Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth: Wukong (24 hours of continuous gameplay across 32 videos at 1080p) us… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2.5: VISUAL AGENTIC INTELLIGENCE — Fig.12 (p.29)
![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]]
> [!tip] # Figure Description

**Note:** The figure body on this page appears blank/unrendered — only the caption is visible at the bottom. The page is otherwise empty white space.

**What should be present (based on caption):**
- **Type:** Qualitative examples (presumably a multi-panel figure)
- **Subject:** Kimi K2.5 performing visual reasoning tasks
- **Mechanism:** "via tool use" — implying the model invokes external tools (e.g., code execution, image manipulation, object detection, geometric calculators) rather than answering purely from internal perception
- **Implied data flow:** Visual input → model perception → tool selection → tool execution → result integration → reasoning output

**Key technical takeaway (≤120 words):**
Kimi K2.5 augments its native visual perception with **external tool calls** to solve visual reasoning tasks. Rather than relying solely on a vision encoder's internal representation, the model decomposes problems, invokes specialized tools (code, analysis modules, etc.), and integrates the results into its chain of thought. This agentic vision approach extends the model's capabilities beyond what fixed-resolution visual tokens alone can support, enabling more accurate, verifiable, and compositional visual reasoning.

---

**Caption (verbatim):**
> Figure 12: Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use.
*caption: Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 29… ｜ 论文 [[kimi-k2-5-visual-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.1 (p.9)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 图示内容：** 展示MoE层前向传播的Route与Dispatch两阶段数据流。`Input Tokens [B×S, H]` 进入绿色**TopKRouter**：先经`Gating Linear`，再由`Softmax/Sigmoid`打分，最后`Top-k Selection + Load Balancing`输出`routing map`与`probs`；随后蓝色**Token Dispatcher**执行`Permute`（按专家分组tokens）→`All-to-All`（跨GPU发送）→`Postprocess`（预处理），将tokens分发至右侧`Shared`通路及各Expert。

**2) 关键结论：** 原文以此论证MoE的核心机制是**token级稀疏激活**与**跨GPU All-to-All通信**的耦合，路由决策与分发传输构成性能与扩展性的关键瓶颈。

**3) 论文作用：** 作为方法总览图，为后续章节深入讨论路由策略、通信优化、Expert并行计算等具体技术提供整体框架铺垫。
*caption: Data flow through an MoE layer: Route, Dispatch, Compute, and Combine stages.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.2 (p.10)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示Megatron-Core中MoE TopKRouter架构：左为分数函数（softmax归一化得[BxS, E]维分数），中为Top-K选择，输出两个并行产物——逐token概率[BxS, E]（加权组合专家输出）与路由映射[BxS, E]（dispatcher布尔掩码）；下方为两类负载均衡机制：无辅助损失的Expert Bias与全局batch级的Global_aux_loss。原文借此论证Router同时兼容aux-loss与aux-loss-free双路径，可灵活切换细粒度路由与均衡策略；该图是后续细粒度MoE并行调度、分组GEMM与token-dropless训练等扩展组件的路由计算基础。
*caption: Router architecture: linear projection, score function, top-𝑘selection, and load balancing. combine_postprocess (backward).… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.3 (p.13)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig03.png]]
> [!tip] 【图文联合解读】**图3图文解读**

图以双对数坐标对比约30个LLM的"总参数量（1B–1000B）"与"每token前向FLOPs"，●为Dense、▲为MoE，并标注≈2N参考线。Dense模型（LLaMA-3.1-405B、Nemotron-4 340B、Falcon-180B、OPT-175B/BLOOM-176B等）严格落在2N带内；MoE模型（Mixtral-8x22B、DeepSeek-V3、Hunyuan-Large、Qwen3-MoE-235B、Kimi-K2、Grok-1、Ling-1T等）总参数可达数百至千亿级，但FLOPs仅数十至百亿B，远低于2N线。论文借此论证MoE以稀疏激活实现"高参数、低算力"的扩展优势，从而引出Megatron-Core针对专家/张量/流水线并行的可扩展MoE训练方案。
*caption: Dense Model vs MoE Model parameter/compute scaling.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.4 (p.15)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig04.png]]
> [!tip] 【图文联合解读】图示 **EP=4、8 Experts、2 Experts/GPU**（GPU0 持 E0/E1，GPU1 持 E2/E3）的 MoE 数据流：token 序列 [T0][T1][T2]… 经路由后，由 **All-to-All dispatch** 分发到各 GPU 对应专家计算，再经 **All-to-All combine** 回收结果。原文借此论证：EP 将专家切分到多 GPU 以摊薄单设备显存与算力，关键代价是 all-to-all 通信。该图是论文方法学的起点，为后续 EP 通信优化与大规模扩展性实验提供架构基础。
*caption: Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communication dispatches tokens to their assigned experts and combines results… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.5 (p.17)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig05.png]]
> [!tip] 【图文联合解读】## 图文联合解读

**1) 核心对象与结构：**
左侧（传统方案）上为 TP2-DP2：序列被切成 Seq1/Seq2 两段，每段 2 个 Rank（Rank1–3）各持 1/2 Attn；下为 ETP2-EP2：4 个 Experts 被拆成两组分发到不同 Rank。右侧（Parallel Folding）上为 TP2-CP2：4 个 Rank 同处 Seq1，靠 Context Parallel 切分序列；下为 ETP2-EP1：所有 Experts（1/2 E1–E4）完整堆叠在每个 Rank 上（EP=1，专家本地化）。

**2) 关键技术结论：**
绿色虚线箭头显示二者可等价映射，证明可将原本耦合的 DP×EP 解耦为 CP×EP1——在保持等效序列并行度的同时，消除 EP 带来的跨设备 Expert 通信开销。

**3) 论文链路中的作用：**
该图作为 MoE Parallel Folding 方案的形式化定义与可行性证据，为后续显存/通信收益及大规模训练实验奠定理论基础，是该方法从"概念"走向"实现验证"的桥梁。
*caption: Parallelism mappings: traditional constraints vs. MoE Parallel Folding decoupling.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.6 (p.18)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图6展示了 Parallel Folding 中 **Attention 层在单一 TP 组内**的并行配置：8 张 GPU（GPU0–GPU7）构成一个 TP=8 的张量并行组，组内通过 TP AllReduce（8 路通信）完成 attention 集合通信，A2A Scope 限定为这 8 GPU。

**论证结论**：传统方案中 attention（TP/CP）与 MoE（EP）必须共享同一并行映射，导致通信域膨胀；而 folded 布局将二者解耦——attention 在小组内保持高 TP/CP，MoE 在同小组内独立使用 ETP=1、高 EP，all-to-all 与 attention 集合通信都局限在 NVLink 互连的小 GPU 组内，从而降低跨域通信开销。

**论文作用**：作为核心方法的可视化证据，支撑 Parallel Folding 在 MoE 训练中实现 attention–MoE 解耦并行、提升可扩展性的设计主张。
*caption: Parallel Folding: decoupled attention and MoE parallelism mappings.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.7 (p.22)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig07.png]]
> [!tip] 【图文联合解读】**图7 联合解读：**

Figure 7 并列对比 Baseline（左）与 Memory-Efficient Permutation（右）两条 MoE 专家块前向通路，以蓝/粉色块区分临时中间张量与反向保存张量。Baseline 依次为 Router→Permute→A2A+LocalPermute→FC1→SwiGLU→FC2→Unpermute+A2A→Unpermute，粉色保存张量密集，且需缓存 probs 至最后 Unpermute 阶段。

优化版将 Permute 提前到 Router 之前，probs 与 routing map 由已置换 token 产出；并将 A2A 拆为"A2A+LocalPermute"与"A2A+Permute"双路径，用 Fused WeightedSwiGLU 内部吸收 probs（图中标注 [B×TopK×S, H] 张量就地释放），省去多处反向缓存。

**技术结论**：重排计算顺序与算子融合可显著削减 MoE 激活显存。**论文作用**：属 Megatron-Core MoE 显存优化链路的关键一环，为后续更大规模稀疏专家扩展奠定基础。
*caption: Memory-Efficient Permutation.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.8 (p.23)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图8展示了DeepSeek-V3架构中的**选择性重计算（Selective Recomputation）策略**。图例标注了七类操作的内存管理方式：紫色core_attn（fused_attn无需重算）、粉色moe_act、绿色layernorm、蓝色mlp_up_proj、黄色dispatch均采用**output-discarding**（丢弃输出，反向时重算）；红色虚线框标记moe模块，橙色虚线框标记shared_experts。右下块图可见shared_experts内部FC1→Swiglu→FC2三段结构，灰色阴影区域表示各模块的重计算范围。备注指出dense mlp模块的mlp_recompute未在图中绘出。

**技术结论：** 论文据此论证——重算应优先施加于"显存密集但计算廉价"的算子（layernorm、dispatch、mlp_up_proj等），从而以极小计算开销换取显著的激活显存节省，是MoE大规模训练的关键显存优化手段之一。

**论文作用：** 该图与Figure 7（通信计算重叠）共同构成第3章的两大训练加速支柱，支撑后文吞吐量与显存占用实验的优化依据。
*caption: Selective Recomputation.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.9 (p.24)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图9展示前向传播中细粒度激活卸载的两流时间线。Compute Stream依次执行Forward FC1与FC2（深绿块），D2H Stream负责Offload to CPU（深灰块）。关键在于：FC1的激活无需等FC2完成即可启动卸载，箭头指示其起始时刻，浅绿"Overlap"区表明D2H传输与FC2计算在时间上完全并行。

论文借此论证：通过流级重叠，可将激活offload开销隐藏于后续计算之下，避免串行等待的墙钟代价，从而在保留大规模MoE训练所需显存卸载能力的同时，最小化对训练吞吐的影响。该机制是Megatron-Core细粒度activation offloading调度方案的核心组成部分，与并行/流水策略协同实现大规模MoE模型的可扩展训练。
*caption: Fine-grained activation offloading: stream overlap for forward and backward passes.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.10 (p.26)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig10.png]]
> [!tip] 【图文联合解读】图示MoE层细粒度内存策略：左路Attention（mlp_norm→QKV→Core Attn→Attn Proj→mlp_norm），右路MoE（Dispatch→FC1→MoE Act→FC2→Combine），绿色活跃、灰色中间态，Shared Experts分支并行汇入。共8处配置：mlp_norm/attn_proj/expert_fc1/moe_act采用offload，layernorm/moe_act采用recompute，core_attn/mla_up_proj可OR切换，FC2输出可Discard。

技术结论：原文论证精度感知优化与CPU offloading互补，按模块粒度独立配置，使显存占用与重算开销可按需权衡。

整体作用：作为Megatron-Core的细粒度内存优化接口，与粗粒度选择性recompute构成完整栈，为大规模MoE训练提供关键显存节流能力，是系统级可扩展方案的核心配置层。
*caption: Fine-grained offloading and recomputation: complementary memory optimization strategies. optimization target. Megatron-Core provides two techniques: p… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.11 (p.28)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig11.png]]
> [!tip] 【图文联合解读】图(a)展示FSDP2策略下3个Linear模块在Device Rank 0/1上的分布：Linear 1采用Shard_Param按模块分片集体缓冲（蓝色，每Rank各持一份对应条目），Linear 2、3为均匀分片（绿/红色），再以DTensor形式映射至各Rank对应位置。原文借此论证FSDP2"逐参数均匀分片"使通信缓冲与shard不对齐、引入额外开销；该图为对比铺垫(b) Megatron-FSDP"按模块扁平化、非均匀分片并对齐通信缓冲"的核心论点服务，是论文分布式训练设计章节中支撑其sharding strategy优越性的关键原理示意。
*caption: Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b) Megatron-FSDP flattens per-module and shards non-uniformly, aligning… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.12 (p.28)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示对比FSDP梯度处理两种方案：上方为torch.empty的CUDACachingAllocator每次通信重新分配；下方Persistent双缓冲设计——两个预分配buffer在FSDP collectives间循环复用，经Reduce Scatter产出Gradient shard。

原文借此论证：**消除每次collective的分配开销，并使NCCL User Buffer Registration成为可能**。该设计在论文中支撑Table 12关于不同并行策略（degree 𝑑）对内存与通信影响的对比实验，是MoE大规模训练通信栈优化的核心环节，对降低显存峰值、提升集合通信效率至关重要。
*caption: Persistent double-buffer design: two pre-allocated buffers are cycled across FSDP collectives, eliminating allocation overhead and enabling NCCL User … ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.13 (p.30)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示 4 块 GPU（GPU0–3），每卡承载 1 个专家，整体并行处理 8 个 token（a1–a8，每卡 2 个）。数据流为：Attention Layer 输出 → 本地 Router 决策 → token 被染色标记目标专家（如 a2 标绿、a1 标蓝）→ 经 EP group 的 **Dispatch（All-to-All 集合通信）** 将 token 跨卡路由至对应专家所在 GPU。

2) **关键技术结论**：Expert Parallelism 的核心通信代价来自 Dispatch 阶段的 **All-to-All**：Router 在本地完成路由决策后，token 必须在 EP group 内重新分发，使每卡只处理分到本地专家的子集——这是 EP 区别于 TP/PP 的标志性通信模式。

3) **论文中的作用**：作为 §4.2.1 "Communication Anatomy" 的开篇图，奠定后续讨论 Combine、GEMM 切分、All-to-All 优化（如双向/TMA 加速）等问题的基础，是 Megatron-Core MoE 通信栈设计的参照原型。
*caption: Expert parallelism across 4 GPUs with 4 experts.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.14 (p.31)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig14.png]]
> [!tip] 【图文联合解读】图示HybridEP调度内核两路数据流：①节点间（绿框）从其他节点同rank获取RDMA Token/Prob/Scaling factor；②本地（粉框）从注意力层与路由器取Token/Prob/Scaling factor。前者由RDMA warp组跨节点交换后送入"Global Memory→SM warp group"，与本地输入共同经FIFO转发至目标expert。论证核心：HybridEP将跨节点RDMA与节点内dispatch解耦——先由RDMA warp组完成同rank交换，再由SM warp组在节点内FIFO推送，避免SM直接处理RDMA数据。该设计是MoE专家并行通信栈中dispatch阶段token高效路由的关键实现。
*caption: The dispatch kernel design of HybridEP.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.15 (p.31)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig15.png]]
> [!tip] 【图文联合解读】1) **对象与结构**：图中是 HybridEP 的两条并行 combine 路径，每条处理 Token、Prob 两类数据：本地 Global Memory→SM/intra-node warp group，或其他节点同 rank 的 RDMA Token/Prob→SM/inter-node warp group；随后均经 SMEM Cyclic FIFO。  
2) **技术结论**：节点内与 RDMA 通信分工处理，并用共享内存循环队列衔接，减少 CPU 调度、拷贝和同步开销。  
3) **作用**：作为 MoE 通信到专家计算的 kernel 实现图，支撑 HybridEP 的低开销 token 组合及性能扩展性实验。
*caption: The combine kernel design of HybridEP.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.16 (p.32)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 16）**

该图展示双微批次（u-Batch Even / Odd）在 MoE 流水线中的三段时序，每行均包含 FWD→BWD→FWD；三段顶部标注"Merged"，下方虚线框分别标记 ubatch 0（归属 Even 行）与 ubatch 1（归属 Odd 行）。

**关键结论**：1F1B 流水使 ubatch 1 的 FWD 与 ubatch 0 的 BWD 并发；"Merged"段表明连续的 FWD-FWD 阶段可与 MoE 专家路由的 all-to-all 通信重叠执行，从而隐藏通信开销。

**论文作用**：作为 Megatron-Core MoE 扩展方法的核心调度图，支撑其"计算-通信全重叠"的高吞吐训练策略。
*caption: Merged FWD-FWD Timeline with all-to-all Overlapping.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.17 (p.33)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig17.png]]
> [!tip] 【图文联合解读】**图17图文联合解读：**

**1) 核心对象与结构**：图示为按奇偶分流的微批次双轨时间轴（u-Batch-Even / u-Batch-Odd），横向分为三段："Not Merged"段仅含 ubatch0 的 FWD；"Merged-1"段将 ubatch0 的 BWD 与 ubatch1 的 FWD 并排放置；"Merged-2"段将 ubatch1 的 BWD 与 ubatch2 的 FWD 并行呈现，颜色块以绿(FWD)/灰(BWD)区分。

**2) 论证的技术结论**：原文借此说明，在 MoE 训练中，相邻微批次的前向计算与上一微批次的反向计算可"合并"(merged)重叠执行，而非严格串行；该调度使 all-to-all（专家并行 dispatch/combine）通信得以嵌入计算空隙，从而隐藏通信开销。

**3) 在论文整体中的作用**：作为"All-to-All Overlapping"优化策略的可视化佐证，支撑 Megatron-Core MoE 流水线实现通信-计算重叠、提升大规模专家并行训练吞吐量的核心方法论结论。
*caption: Merged FWD-BWD Timeline with all-to-all Overlapping.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.18 (p.34)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig18.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图18展示三种EP all-to-all通信与计算的执行时间线对比：

1）**Baseline（无重叠）**：F/Attention→F/Dispatch(A2A)→F/MLP→F/Combine(A2A)→B/Combine→B/MLP→B/Dispatch→B/Attention严格串行，A2A通信占迭代时间30–40%。

2）**1F1B Overlap Baseline**：分Compute Stream与Communication Stream两轨，将F/ATTN-F/MLP与B/COMBINE-B/DISPATCH错位并行，但仍存在尾部暴露A2A。

3）**1F1B Overlap with W/D Split**：进一步把MLP拆为D/MLP与W/MLP两段，与A2A更细粒度交错；暴露A2A通信压缩至<5%，overlap ratio达93%，较中间方案获得明显Speed Up。

**结论**：论文用此图论证W/D Split是EP通信隐藏的最优方案，将通信瓶颈从30–40%降至5%以下。

**作用**：位于EP通信优化章节，作为支撑Megatron-Core MoE大规模训练效率的关键可视化证据，为后续性能数字提供机理说明。
*caption: EP all-to-all communication overlap strategies: baseline vs. 1F1B with W/D split.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.19 (p.35)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig19.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图19展示了**交错式PP时间线**（PP=4，VPP=3，Grad accumulation=8）在**warmup阶段**对all-to-all通信的隐藏策略。图例用橙/蓝/粉三色区分FWD的三条虚拟管道及对应BWD，每格数字标记微批次序号（1–8）。红色框出warmup结束时多执行的一个额外微batch，其fprop紧接主时间线起点的microbatch（标注"Execute one extra micro-batch"），而bprop则与下方相邻微batch的fprop/bprop重叠（多箭头所示）。

关键结论：**通过在warmup阶段注入额外微batch**，使后续微batch的前向/反向与MoE all-to-all通信在时间轴上**计算-通信交叠**，从而隐藏通信开销。

在论文中，该图支撑Megatron-Core交错流水线中"**通信隐藏于计算**"的核心优化链路，是MoE大规模训练高效率的关键实证。
*caption: Interleaved PP Timeline with all-to-all Overlapping.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.20 (p.37)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig20.png]]
> [!tip] 【图文联合解读】**结构**：permute fusion 流水线分 Forward/Backward 两路。Forward：tokens、probs → Preprocess Kernel（生成 row ID map）→ Permute Kernel → permuted tokens/probs → Linear FC1 → Act Function（融合 probs）→ output。Backward：gradient → Act Function(反) → Linear FC1(反) → permuted grad → Unpermute Kernel（复用 row ID map）→ tokens grad、probs grad。黄色虚线框标注 row ID map 在前后向间共享。

**结论**：offset map 一次生成、前后向双向复用，避免反复构建路由索引；permute 与 FC1/激活融合，消除"多小 kernel 启动 + GPU 额外开销"。

**作用**：MoE 专家并行中高效 token 路由/调度的核心机制，是大规模 MoE 可扩展训练的关键支撑。
*caption: The pipeline for permute fusion in the training process. • Preprocessing: Permutation is fundamentally a data transfer process that requires tokens to… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.21 (p.38)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig21.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图21展示MoE路由器的融合流程：输入经Gating Linear产生Logits后，分两路径并行演示——上路采用Topk/Group Topk搭配Sigmoid/Softmax，下路用Topk搭配Sigmoid/Softmax，两路径分别汇聚为单一"Fused kernel"。

**关键论证：** 路由器中的Top-k专家选择与激活函数可被融合为单个kernel，省去多次中间张量写回与launch开销，相比传统分步执行显著降低访存与调度代价。

**在论文中的位置：** 该图隶属Megatron-Core的MoE性能优化模块（与Figure 19/20的grouped GEMM等并列），是支撑其端到端可扩展训练链路中路由器层级算子融合优化的关键可视化说明。
*caption: The workflow of the router fusion. • Computation of MoE auxiliary loss: Building on step 2, the auxiliary loss computation is fused into a single kern… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.22 (p.39)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig22.png]]
> [!tip] 【图文联合解读】**图22 联合解读**

**核心对象与结构**：上下两幅子图均含 CPU/GPU 双时间线。上图（传统执行）CPU 侧交替出现 *Python & Framework* 与 *Launch K1* 等多次调用块，GPU 侧 K1、K2 之间形成 "CPU Overhead" 气泡；下图（CUDA Graph 执行）CPU 侧仅一个 *Graph Launch (Single API call)* 长块，GPU 侧 K1、K2 紧密背靠背，底部绿色箭头标注 "NO GPU BUBBLE"。

**关键技术结论**：原文借此论证——逐核启动路径下 CPU 调度开销足以让 GPU 产生空闲等待，而单次 API 提交整张计算图可彻底消除该空泡。

**论文中作用**：MoE 训练含大量细粒度专家计算与 all-to-all 通信核，传统调度极易使 GPU 空转。本图为 Megatron-Core 集成 CUDA Graph 提供执行模型层面的动机支撑。
*caption: Traditional execution (top) versus CUDA Graph execution (bottom).… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.23 (p.39)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig23.png]]
> [!tip] 【图文联合解读】**图23解读：**

图示一次训练迭代（3层、2微批次）的调度序列：前向块F₁₁–F₁₃、损失块L、反向块B₁₁–B₁₃依次排列。**紫色虚框（Layer-wise CUDA Graphs）**逐层独立封装每个F/B；**橙色虚框（Full CUDA Graphs）**将整段前向（或整段迭代）打包为单一图。

**技术结论：** MoE模型中各层专家路由使每层处理的token数动态变化，Full CUDA Graph要求全段shape一致，因此**无法捕获**；Layer-wise方案将每层作为独立子图capture，既复用kernel消除launch开销，又容忍层内shape浮动。

**方法链作用：** 是论文针对MoE特殊结构对CUDA Graph机制的关键改造，构成Megatron-Core可扩展MoE训练性能优化的核心组件之一。
*caption: Full versus layer-wise CUDA Graphs in one training iteration (three layers, two microbatches).… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.24 (p.40)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig24.png]]
> [!tip] 【图文联合解读】**图24联合解读**

1) **结构与数据流**：图24将单个MoE Transformer层按"静态/动态形状"划分为三个CUDA Graph scope与三段图外区。紫色"attn"框内含 LayerNorm→Attention QKV→Core Attention→Attention Projection→Bias·Dropout·Add 共5个静态算子；绿色"moe_router"框含 Gating→Top-K Routing，并旁路接入Shared Expert；蓝色"moe_preprocess"框含Permutation与AG A2A-v in/out splits。图外（红色"Dynamic Shapes"括号）为 Global A2A-v exchange tokens、Local Permutation、Routed Experts GEMM、Local Unpermutation、Global A2A-v recover tokens、Unpermutation。

2) **关键技术结论**：CUDA Graph只捕获形状固定的组件（attention、router/shared expert、preprocess），将每迭代变化的per-expert token数对应的Routed Experts GEMM及dispatch/combine通信排除在图外。

3) **链路作用**：在dropless MoE训练中通过per-layer partial graph capture，在最大化kernel launch优化（静态路径）与容忍动态token分布之间取得平衡，是MoE与CUDA Graph协同的性能基础设施。
*caption: Partial CUDA Graphs capture static components (attention, shared experts, router, preprocessing) while leaving dynamic expert computation outside the … ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.25 (p.41)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig25.png]]
> [!tip] 【图文联合解读】**图25联合解读**

**1）核心对象与结构**
该图为NSight Systems profiler时间线，对比Transformer层前向传播两版本在+104~109ms（无CUDA Graph，上）与+97.5~103ms（部分CUDA Graph，下）区间的执行序列。按MoE流程划分为**preprocess、dispatch、routed experts（含GroupedGEMM_parallel/nvls）、combine**四个阶段。上图各kernel块之间存在明显**空白间隙**（CPU launch overhead）；下图左侧绿色"CUDA Graph"区块连续紧凑，可见`cudaMemcpyAsync`等异步调用将多步操作封装，kernel间隙被消除，而dispatch/combine等动态部分仍保留外部调度。

**2）关键技术结论**
Megatron-Core对静态可复现的计算段（attn、expert GEMM等）实施CUDA Graph捕获，可基本消除CPU发射开销与launch latency；对依赖token路由、动态专家分配的dispatch/combine则保留非图路径，从而兼顾**执行效率与动态灵活性**。

**3）在论文中的作用**
作为NSight实测证据，支撑文中核心论点——Partial CUDA Graphs是Megatron-Core MoE训练实现高吞吐的关键优化之一，与并行张量/专家、TokenDrop等优化协同，使大规模MoE训练可扩展。
*caption: Transformer layer forward pass: without (upper) and with (lower) partial CUDA Graphs. CPU overhead is largely eliminated for static components.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.26 (p.42)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig26.png]]
> [!tip] 【图文联合解读】图中以 \(L\) 层、\(M\) 个微批比较执行顺序：启用 PP 时连续运行 \(F_{mb0},F_{mb1},\ldots\)，再统一反向；禁用 PP 时按 \(F_{mb0}\!→\!B_{mb0}\!→\!F_{mb1}\!→\!B_{mb1}\) 执行。CUDA Graph 保存的反向上下文会被后续前向覆盖，故 PP 下不能跨微批共享，总计需 \(L·M·2\) 个图；无 PP 仅需 \(L·2\) 个。图中解释了两者冲突，为图数量估算及 MoE 训练优化设计提供依据。
*caption: Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatches. With PP (top): Execution is interleaved—multiple forward passes r… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.27 (p.45)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig27.png]]
> [!tip] 【图文联合解读】**图27（Backward）图文联合解读：**

**1) 核心结构：** 图示ECHO反向计算流，自底向上为：Combine backward → FC2 双轨（dgrad 主路径 + wgrad 并行）→ MoE act backward → FC1 双轨（dgrad + wgrad）→ Dispatch Backward。两条黄色模块贯穿全程——左侧 "Expert Dispatch" 将 home expert 权重分发至 dgrad 计算路径；右侧 "Expert Gradient Dispatch" 从 wgrad 路径汇聚梯度回传 home expert。两条横向 dashed 线划分出 FC2、MoE act、FC1、dispatch 四个阶段。

**2) 关键结论：** 反向与前向结构对称——dgrad 在被克隆的 hot expert 上算、wgrad 归约回 home expert，从而在不改 MoE 算法的前提下，保持专家并行并复用热专家权重，避免跨 rank 重复存储。

**3) 论文作用：** 与前向图配对构成完整 ECHO 调度示意图，是论证"调度即扩展性"的核心证据，支撑 ECHO 在不修改路由/并行框架条件下实现 MoE 高效训练的结论。
*caption: ECHO workflow for forward and backward passes. The planner generates routing and hot expert maps. Expert Dispatch clones hot expert weights to spare s… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.28 (p.46)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig28.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象与结构：** 图分三列对比三种执行模式的显存布局。每列含多层（行）×多专家（Exp 0/1/2）的方块堆叠，绿色为实际占用 token（编号 0–5），白色为空闲区，虚线框表示预分配但未用容量。Eager 列贴合实际、无浪费；Static Shape 列每层独立预留最坏容量，白色碎片显著；Paged Stashing 列各层共享一个超尺寸 tmp 缓冲区，配合 Stashing buffer 将分散 token 紧凑填入。

**关键结论：** Paged Stashing 以"共享最坏尺寸 tmp + 分页暂存"机制，在保留静态分配优势的同时，把碎片率逼近 Eager 水平，兼顾稳定性与显存利用率。

**论文作用：** 为 MoE 训练中 Expert Parallel 显存瓶颈提供解决方案的可视化依据，支撑 Paged Stashing 作为 Megatron Core 中 MoE 通信–计算重叠优化的核心设计。
*caption: Memory layout comparison across three execution modes. Left: Eager mode allocates memory dynamically based on actual usage. Middle: Baseline static sh… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.29 (p.46)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig29.png]]
> [!tip] 【图文联合解读】**联合解读：**

1) **图示对象**：横向时间线对比两条 CUDA Stream——绿色 Compute Stream（依次执行 Forward Layer N、N+1），深灰 Stash Stream（执行 Layer N 激活从 tmp buffer 拷至 stash buffer）；两者在时间轴上以箭头衔接，浅绿"Overlap"区表明 Layer N 的 stash 拷贝与 Layer N+1 的前向计算完全并行执行。

2) **关键结论**：前向 stash 通信可与下一层计算 kernel 完全重叠，专用 Pack Stream 使 tmp→paged stash 的拷贝延迟被计算掩盖，不引入额外气泡。

3) **链路作用**：作为 MoE 训练显存-计算重叠优化的核心证据，证明 paged stashing 通过流并行实现了激活备份零开销，是支撑大规模 MoE 流水线高吞吐的关键环节。
*caption: Paged Stashing stream overlap. Forward pass: After Layer N computes, its activations are stashed (copied from tmp buffer to paged stashing buffer) on … ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.30 (p.50)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig30.png]]
> [!tip] 【图文联合解读】**图示内容（量化）**：展示三种FP8量化方案的缩放因子粒度。Per-Tensor为整张量1个scale（最粗，单色大方块）；Blockwise为128×128块1个scale（中等，2×2示意）；MXFP8为1×32元素1个scale（最细，6×6共36个小色块）。底部双向箭头标注粒度光谱：左侧"Coarse / Fewer Scales"，右侧"Fine / More Scales"。

**技术结论**：FP8训练配置由"数据格式（E4M3/Hybrid）+ 缩放粒度"联合定义；粒度越细→scale越多→数值精度越高，但scale元数据存储与计算开销也越大，三者构成精度–效率的权衡谱系。

**方法作用**：位于第5.3节首图，承接前文"三堵墙"分析，作为Reduced-Precision Recipes的形式化铺垫，为后续NVFP4讨论建立粒度对比基准。
*caption: FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8. A reduced-precision training recipe consists of: • Data format. There are two type… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.31 (p.52)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig31.png]]
> [!tip] 【图文联合解读】## 图文联合解读

**核心对象与结构**：图31由四个子图(a-d)组成，分别展示线性层在不同平台、不同FP8方案下的前向(Forward)、反向(Backward)、优化器(Optimizer)计算流程。Hopper平台(a/c)需要"Cast and Transpose"以适配行/列量化布局；Blackwell(b)仅需"Cast to FP8"无需转置；(c)引入Blockwise(1D行/列+2D块)；(d)在Blackwell上使用MXFP8原生"Quantize"操作，所有张量(输入、权重、梯度)均为Rowwise/Colwise MXFP8。

**关键技术结论**：MXFP8(d)相较Per-tensor(a/b)和Blockwise(c)，量化粒度更细(finer-grained)，因此精度更精确；且Blackwell Tensor Core原生支持MXFP8，性能更佳，故成为Blackwell默认FP8方案。

**论文链路作用**：该图属于精度/量化章节，为MoE大模型训练选择低精度数值方案提供决策依据，与并行策略、通信优化共同构成Megatron-Core可扩展训练栈的核心组件。
*caption: The computation of a linear layer with various FP8 recipes. Note the differences in quantization granularity and tensor layout requirements across pla… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.32 (p.53)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig32.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示展示 **FP8 主权重按块缩放（blockwise scaling）量化在数据并行（DP）下的边界处理**：

1) **核心对象与结构**：左图表示权重矩阵被划分为多个量化块（红框即一块），该块在 2D 布局下可能被切分到不同 DP rank；中图（DP rank 0）演示"块不完整"情形——仅用当前 rank 持有的子块数据计算 local abs-max；右图（DP rank 1）演示"块完全不在本 rank"情形——将该块 abs-max 置 0。

2) **关键结论**：在 DP 切分下，量化块的 abs-max 必须在各 rank 本地按 2D 布局感知地独立计算，空块置 0 不参与缩放，从而保证跨 rank 量化后统计量一致、避免溢出。

3) **论文作用**：该图是 FP8 量化章节中"分布式正确性"的支撑图，衔接块级缩放方案与 Megatron-Core 的并行栈，使 FP8 主权重量化可与 TP/DP/EP 并行兼容，服务于 MoE 大规模训练中的显存与吞吐优化。
*caption: FP8 primary weight quantization scheme for blockwise scaling.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.33 (p.54)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig33.png]]
> [!tip] 【图文联合解读】**图示内容**：三个权重矩阵(Weight 0/1/2)按 DP rank 边界 flatten 拼接到一条全局权重 buffer；每个 rank 持有其对应分片的 FP32 master weights，经三步完成量化——① Step 1 取本地 abs-max；② Step 2 通过 all-reduce 在 rank 间汇总得 global abs-max；③ Step 3 据此将 master 权重量化（partial cast）为 FP8 model weights。

**技术结论**：方案采用 **delayed scaling**（沿用上一 step 的 global abs-max，避免当前步等待同步）与 **per-tensor current scaling**（整条 flattened buffer 共享单一张量级缩放因子），在保证量化精度的同时把同步开销降到最低。

**论文作用**：支撑 Megatron-Core 中分布式优化器的 FP8 量化流水线，使 all-reduce 通信与 FP8 cast 流水并行，是 MoE 大模型可扩展 FP8 训练栈中实现权重低精度存储/通信的关键一环。
*caption: FP8 primary weight quantization scheme for delayed scaling and per-tensor current scaling.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.34 (p.57)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig34.png]]
> [!tip] 【图文联合解读】图(b)展示4K→256K序列长度下SDPA与MoE占总FLOPs占比的此消彼长：SDPA（红）由4K约13%单调升至256K约90%；MoE（蓝）由4K的59.4%降至256K的约6%。两曲线在约16K附近交叉，4K时MoE主导（59.4%），64K时SDPA主导（69.7%）。

原图用以论证：SDPA复杂度为Θ(s²)、MoE及其他操作仅Θ(s)，故长序列训练时注意力成为算力瓶颈。论文据此强调须重点优化SDPA（如FlashAttention内核），才能使MoE模型在长序列场景下保持可扩展性。
*caption: SDPA exhibits 𝑂(𝑠2) complexity, while MoE and the remaining attention operations exhibit 𝑂(𝑠) complexity. Therefore, SDPA dominates the computation at… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.35 (p.59)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig35.png]]
> [!tip] 【图文联合解读】该图以表格形式对比TP与两种CP（Context Parallel）在Core Attention中的通信与计算模式：CP(P2P)线性层权重复制，K/V切片直接送入SDPA并伴点对点通信；CP(A2A)权重同样复制，但K/V先经All-to-All重分布再输入SDPA；TP权重被切分并行、无额外集合通信步骤。

关键结论：CP方案下线性层权重在各rank上重复存储，attention输入仍需通过P2P或A2A通信才能正确分片到各rank；而TP通过将权重本身切分，使各rank天然持有对应分片，通信模式更简洁高效。

该图为论文论证长序列训练中CP与TP的通信开销权衡提供直观对比，是方法选型与性能分析的核心参考依据。
*caption: Communication and computation patterns of TP and two types of CP.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.36 (p.61)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig36.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**
图(a)"Unpacked sequences"展示5条变长序列（橙、蓝、米、绿、紫），按各自长度独立放置，未做拼接。最长序列（如蓝色）决定批处理行高，其余序列（尤其米色）右侧留有大量空白/padding，仅为对齐最长序列。

**2) 关键技术结论**
"未打包"模式下，短序列被强制padding到与最长序列等长，造成**显著的计算浪费**——GPU算力消耗在无意义的padding token上，**吞吐效率下降**。这在MoE训练中尤其严重，因为不同样本激活的专家数与序列长度相关，padding会污染token路由与负载统计。

**3) 在论文中的作用**
该图作为**动机图**，引出后文提出的"Packed sequences"方案：通过将多条样本拼接填满固定context长度，消除padding冗余，从而**提升MoE训练吞吐与专家路由统计的准确性**，是该方法整体效率优化的关键铺垫。
*caption: Unpacked vs. Packed sequences.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.37 (p.61)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig37.png]]
> [!tip] 【图文联合解读】图中用4×4与4×2网格表示打包序列的因果注意力有效计算：左图7个单元集中为6+1，右图呈4+3分布，体现等长切分不等于计算均衡。原文据此指出变长样本会导致Context Parallel通信组负载不均；Dynamic-CP按序列长度动态选择切分和通信组，无需迁移参数或优化器状态，仅增加很小框架开销。该图是Dynamic-CP的动机性论证，并非性能实验。
*caption: Compute imbalance in causal attention over packed sequences. are partitioned and which CP communication group is used by attention operators, without … ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.38 (p.61)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig38.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a)展示三条不等长序列（橙长/蓝中/绿短）打包输入。(b)标准CP2方案：每个微批次将整条打包序列在GPU-0与GPU-1上重复切分并行，双卡各持有完全相同的橙+蓝+绿序列，存在显著冗余。(c)动态CP方案：微批次0的橙色长序列仍用CP2双卡拆分；微批次1则按长度自适应——蓝序列归GPU-0、绿序列归GPU-1，各自改为CP1单卡执行，CP组数随序列长度动态切换。该机制有效消除短序列的跨GPU通信与重复计算开销，是Megatron-Core处理变长packed sequences以提升MoE训练吞吐的关键并行优化。
*caption: Dynamic Context Parallelism for Packed Sequences.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.39 (p.64)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig39.png]]
> [!tip] 【图文联合解读】图分两栏对比Megatron-Core MoE的两种负载均衡策略：(a)辅助损失法沿 Logits→Score Function→Top-k Selection→Dispatch 路径，先按分数函数计算专家接收概率 P_i=(1/T)Σ probs(x,i)，再统计路由频次 f_i=(1/(T·topk))Σ routing_map(t,i)，以 L_aux=α·E·Σ(f_i·P_i) 做梯度反向传播的"可微软均衡"；(b)Sinkhorn 路线沿 Logits→exp→Row/Col Norm 迭代收敛→Top-k→Dispatch，以矩阵归一化分配实现"非可微硬均衡"（图中示例矩阵元素为 -4,-3,-2,-1）。两者为框架提供互补的专家路由机制选择，是支撑大规模MoE可扩展训练栈的关键模块之一。
*caption: Load balancing strategies in Megatron-Core MoE.… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.40 (p.65)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig40.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图40展示Megatron-Core MoE的**共享专家架构**流程。核心结构：输入token流（T1–T7）经门控选Top-K→**Token Dispatch**（All-to-All通信，橙色框）→Norm→**Routed Experts Compute**（橙色框）→Norm→**Token Combine**（橙色框）→Add叠加共享专家输出→输出token。

**关键技术结论**：共享专家处理**全部token**，路由专家仅处理Top-K被分配的token；当启用overlap时，共享专家计算与Token Dispatch/Combine的All-to-All通信**并行执行**，从而隐藏通信延迟。

**论文作用**：该图是Megatron-Core实现**计算–通信重叠（overlap）**优化的核心证据，支撑其作为Nemotron-3 Super/Ultra模型采用的MoE架构基础，证明双分支设计可在不增加关键路径时延的前提下扩展专家容量。
*caption: Shared expert architecture in Megatron-Core MoE. The shared expert processes all tokens while routed experts process only their assigned tokens. When … ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.41 (p.66)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig41.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示DeepSeek-V3在16 PP×2 VPP共32虚拟阶段上的灵活流水线布局：PP Rank 0首段承载Embedding+3个Dense Decoder（计算量≈2个MoE Decoder当量）；PP Rank 1–13为标准阶段，每rank均布2个MoE Decoder；末端PP Rank 14放置MTP（多token预测）层，PP Rank 15放置轻量Loss层，绿色箭头标示数据流向。

**技术结论：** 打破传统均匀层分配，支持异构层（轻量Embed/Loss/Dense vs 重型MoE/MTP）按计算与内存特性差异化编排至pipeline首尾，避免出现瓶颈rank。

**论文作用：** 与Table 10配套，证明Megatron-Core具备非均匀pipeline placement能力，是训练超大规模MoE模型（如DeepSeek-V3）的关键系统级支撑。
*caption: Flexible Pipeline Parallel Placement. 66… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Scalable Training of Mixture-of-Experts Models with Megatron — Fig.42 (p.67)
![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig42.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 42）：**

图示E2G2T2细粒度MoE结构：输入经**Grouped Router→topK/Softmax**，从**4个专家**中选通**top-2**（红箭头激活，灰X门控），每个专家含W1(**h×2h**)与W2(**2h×h**)，即中间维为密集MLP的一半，求和后输出。

**关键技术结论：** 将密集MLP中间维切分为两半(4h→2h)并复制成2组专家，同时复制路由器权重使Top2**必然各选中一个不同分片**，训练起始MoE输出与原密集模型严格一致。

**作用：** 这是"granular upcycling"的核心机制，实现从密集检查点**无损初始化**细粒度MoE，是论文扩大专家数量同时保持训练稳定性的关键链路。
*caption: An example of granular upcycling a dense layer into E2G2T2 fine-grained MoE. E2G2T2 denotes 4 experts, top 2, with half intermediate size. (1) We shar… ｜ 论文 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] ｜ arxiv 见 MD 元信息*

### Qwen3-VL Technical Report — Fig.1 (p.3)
![[assets/crops/qwen3-vl-technical-report-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示Qwen3-VL整体架构：Vision Encoder接收**原生分辨率**输入——图1（1248×9376→**11427 tokens**）、图2（256×32→**8 tokens**，超小图）、图3（1440×800→**1125 tokens**）及视频流（含0.0/4.0/8秒帧，736×448），输出**变长视觉令牌**；DeepStack将多层视觉令牌同时注入LLM Block 1~N，Interleaved MRoPE编码位置、文本时间戳定位视频帧，最终由Dense/MoE Decoder统一自回归解码图文视频令牌。

该图佐证三大技术结论：①视觉令牌数与分辨率成正比、变长映射；②DeepStack多层注入保留细节；③统一解码器兼容文本/图像/视频。它是论文方法部分的**总览蓝图**，为后续章节的预训练、实验设计提供框架基础。
*caption: The Qwen3-VL framework integrates a vision encoder and a language model decoder to process multimodal inputs, including text, images, and video. The v… ｜ 论文 [[qwen3-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### Qwen3-VL Technical Report — Fig.2 (p.17)
![[assets/crops/qwen3-vl-technical-report-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与数据**：柱状图按升序展示模型在自建多语言OCR测试集上的准确率（%）。可见语言包括罗马尼亚语、斯瓦希里语、俄语、印地语、希伯来语、波兰语、Catanzarro、意大利语、德语、越南语、乌克兰语、乌兹别克语、西班牙语、法语、葡萄牙语、日语等；准确率范围约71%–84%，其中拉丁/日耳曼语族（葡、法、西、日）达到83–84%的最高档，东欧与南亚语种处于71–74%最低档。

2) **关键结论**：39种支持语言中有32种准确率超70%，证明Qwen3-VL具备"实用级"多语种OCR能力，而非仅覆盖主流语言。

3) **链路作用**：作为能力广度证据，补强论文"OCR相关VQA达到SOTA"的核心论点，体现模型在文档理解与多语言场景下的泛化优势。
*caption: Multilingual OCR performance of our model on a self-built test set. The model achieves over 70% accuracy on 32 out of 39 supported languages, demonstr… ｜ 论文 [[qwen3-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### Qwen3-VL Technical Report — Fig.3 (p.25)
![[assets/crops/qwen3-vl-technical-report-fig03.png]]
> [!tip] 【图文联合解读】图3为Qwen3-VL-235B-A22B-Instruct的视频"大海捞针"(NIAH)检索热力图：横轴为视频时长，左板为训练内上下文(0–30min/≤256K token)，右板为外推上下文(40–120min/最高1024K token)，纵轴为针帧插入深度(0–100%)，共约70个单元格按Accuracy Score(0–1，红→黄→绿)着色。实测中各深度×时长组合的格子几乎全部呈深绿(≈1.0)，无明显红/黄区，表明无论针帧置于首尾或中段、视频长达2小时/1024K token，模型均能稳定定位并正确作答。该图作为核心长上下文评测证据，支撑Qwen3-VL"原生小时级长视频理解"的关键卖点，并实证其从256K到1024K的上下文外推能力无明显退化。
*caption: Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across varying video durations and needle positions. Each cell shows accuracy… ｜ 论文 [[qwen3-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### DeepStack: Deeply Stacking Visual Tokens is Surprisingly Sim — Fig.1 (p.1)
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 1）**

该图分两部分：左为架构示意，将视觉token分4组（标注1–4）通过残差连接沿Transformer由浅至深（层l_a…l_d）分层注入，而非一次性串入序列；右为七维雷达图，对比7个基准（VQAv2 78.5/80.9/87.6、GQA 62.0/64.4、TextVQA 58.2/61.9、DocVQA 28.1/46.0、InfoVQA 25.8/31.6、SEED 58.6/62.9、POPE 85.9/87.6），四曲线分别为Sequence-576ctx、Sequence-2880ctx、DeepStack-V与DeepStack-L（均2880token/576ctx）。

原文借此论证：仅靠"分层堆叠+残差注入"，在不增上下文长度前提下，DeepStack-L即可全面碾压同ctx的串接基线，并逼近5×ctx的串接模型。

论文作用：以一张图同时完成"动机（高分辨率需更多token）→方法（分层注入）→收益（4× token且不增ctx）"的全链路论证，作为后续Vicuna-7B/CLIP ViT-L实验的可视化总纲。
*caption: Left: Conventional large multimodal models (LMMs) string all visual tokens into a sequence for high- and low-resolution images. Middle: Our DeepStack … ｜ 论文 [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] ｜ arxiv 见 MD 元信息*

### DeepStack: Deeply Stacking Visual Tokens is Surprisingly Sim — Fig.2 (p.4)
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图示 **DeepStack-V**（视觉编码器侧架构）：高分辨率图像被切分为多块网格（如编号 1–5 的彩色区域），低分辨率版本对应 1 块；经 Patch Embed 与首层 ViT Block 处理后，串接多层 ViT Block，每层间分别注入 4 个来自不同图像区域/分辨率的视觉 token 组（图中红/橙/绿/紫标号的 1-1-1-1、2-2-2-2、5-5-5-5），最终经 Connector 接入 LLM 与文本 token 融合。

**技术结论**：DeepStack 将视觉 token 分散堆叠至 ViT 多个中间层（而非仅输入层），借助高分辨率邻域块在不同深度强化细粒度视觉表征。

**方法作用**：作为论文核心架构图，证明"多层视觉 token 注入"在视觉编码器和 LLM 两侧均通用，是后续消融与基准实验的方法基石。
*caption: Architecture of DeepStack. The main innovation lies in the DeepStack strategy that infuses visual tokens into different layers. Left: DeepStack for LL… ｜ 论文 [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] ｜ arxiv 见 MD 元信息*

### DeepStack: Deeply Stacking Visual Tokens is Surprisingly Sim — Fig.3 (p.8)
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig03.png]]
> [!tip] 【图文联合解读】**图3核心内容**：左图(b)展示插入全局token后，高分辨率token堆叠间隔*s*∈{3,4,5}对性能的影响——平均得分稳定在49.7–49.9，几乎无变化；右图(c)展示堆叠层数N∈{0,2,4,6,9}的影响——0层约49.5，4层达到峰值约50.7，9层回落至约49.5。

**关键结论**：间隔*s*鲁棒（间隔1–2即可覆盖所有层），无需精细调参；层数需折中，过少无法充分融合、过多反而引入干扰，4层为最优。

**论文作用**：为DeepStack"深层堆叠"策略提供超参依据，证明该设计轻量且对堆叠密度不敏感，仅需选好堆叠次数即可稳定获益，是方法实用性的关键验证。
*caption: Analysis on using LLM layers to process visual tokens. (a) We insert the visual tokens into different starting layers and initialize the correspondenc… ｜ 论文 [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] ｜ arxiv 见 MD 元信息*

### DeepStack: Deeply Stacking Visual Tokens is Surprisingly Sim — Fig.4 (p.10)
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig04.png]]
> [!tip] 【图文联合解读】**图像无法有效辨认**——所展示的图片内容为循环图表（VOQA/POP/GAQA 等标注）与 DeepStack Figure 4（视觉问答对比示例）无关，疑似加载错误，故仅依据原文进行解读：

1) **核心对象与结构**：图分两栏对比 LLaVA-1.5 与 DeepStack，两者均使用 576 视觉 token 的同等上下文长度；上方样本在图像中以**红圈**标注问题对应区域，下方样本展示细粒度图像描述任务。

2) **关键技术结论**：在 token 数严格公平的前提下，DeepStack 通过多层叠加（stacking）策略，在需要**高分辨率与细粒度视觉理解**的 VQA（上方示例）以及**细节图像描述**（下方示例）上显著优于 LLaVA-1.5，验证视觉表征的层级堆叠优于单层扩张。

3) **整体链路作用**：作为定性可视化（qualitative visualization），与论文中量化的 LLaVA-Bench、MMBench、MM-Vet、TextVQA、POPE、MMMU 等基准结果相互印证，支撑"深度堆叠视觉 token 而非简单增加 token 数"这一核心方法论主张。
*caption: Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison.… ｜ 论文 [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] ｜ arxiv 见 MD 元信息*

### DeepStack: Deeply Stacking Visual Tokens is Surprisingly Sim — Fig.5 (p.9)
![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig05.png]]
> [!tip] 【图文联合解读】图5展示DeepStack对4×4视觉token的三种采样分组方案：2D Spatial（行内交替"1,2,1,2 / 3,4,3,4"，行列均交替）、1D Sequential（按行同色，"1,1,1,1 → 4,4,4,4"纵向排列）、2D Grid（2×2块同色，"1,1,2,2 / 3,3,4,4"分块均匀）。相同编号token在同一层被堆叠送入LMM。论文借此论证分组策略的多样性与鲁棒性——2D Spatial细粒度空间交替、1D Sequential保持序列连续性、2D Grid强化局部块一致性，三者均支撑多层视觉token整合。作为消融可视化，它验证了"深度堆叠视觉token"对采样方式不敏感的核心结论，是证明DeepStack通用性的关键图示。
*caption: Visualization of three sam- pling methods for DeepStack.… ｜ 论文 [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] ｜ arxiv 见 MD 元信息*

### 昇腾 950 NPU 架构白皮书 — Fig.301 (p.12)
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig301.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图实为正文段落而非架构示意图，仅依据文字与上下文解读。所述昇腾950为多Die合封Chiplet：含2个AI Die、2个IO Die，950PR配8个、950DT配4个HBM片上内存模组，通过D2D Clink与Memory Interface互联，构成UMA整体。结合原文论证：①Chiplet封装实现内存统一访问与扩展性；②Cube Core数量32/28/36、Vector Core 64/56/72，算力梯度按精度逐级递减，MXFP4下Cube算力最高达1946 TFLOPS；③支撑LLM算子加速（FlashAttention单核提升1.5~2倍）与CCU通信-计算融合，软硬协同支撑Super Node从384卡扩展至8K卡，是大模型训练推理全流程加速的硬件基石。
*caption: 昇腾950 芯片架构示意图… ｜ 论文 [[ascend-950-npu-architecture-whitepaper]] ｜ arxiv 见 MD 元信息*

### 昇腾 950 NPU 架构白皮书 — Fig.403 (p.18)
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig403.png]]
> [!tip] 【图文联合解读】**注意：图与所给caption存在冲突**——题目称图为"数值精度示意"，但实际图像标题为「图4-2 Cube Core 处理架构示意图」。以下按图像真实内容解读：

**1) 核心对象与结构**：图像展示Cube Core的脉动式PE阵列微架构。上半部示意k个输入流（x₀…x_{k-1} 与 y₀…y_{k-1}）沿正交方向注入一排PE单元；下半部展开为 4×4 PEs 网格，所有PE输出汇聚至 Σ 累加单元，完成矩阵乘累加（MAC）运算。

**2) 关键技术结论**：Cube Core 通过二维 PE 阵列实现大规模乘加并行，是 Ascend 950 张量算力的硬件载体；Σ 树形归约支持高吞吐、低延迟的矩阵乘法，是后续混合精度、稀疏加速等功能扩展的物理基础。

**3) 论文整体作用**：作为第四章计算引擎微架构的图示锚点，为后续章节（算力峰值推算、精度支持、数据流优化等）提供结构化依据。
*caption: Cube Core 支持的数值精度示意… ｜ 论文 [[ascend-950-npu-architecture-whitepaper]] ｜ arxiv 见 MD 元信息*

### 昇腾 950 NPU 架构白皮书 — Fig.406 (p.22)
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig406.png]]
> [!tip] 【图文联合解读】**说明**：所提供内容仅为论文正文文字段落，未呈现实际的 Cube-Vector 融合架构示意图，故仅依据 4.1.4 节文本进行解读。

---

**图文联合解读**：

1) **核心对象与结构**：图示应展示 AI Core 内 Cube 核（含 L1 Buffer）与 Vector 核（含 Unified Buffer）通过一条**直连 CV 数据传输通道**相连，绕过 L2 层进行核内数据交换，体现 SIMD 为主、SIMT 为辅的新异构融合编程架构。

2) **关键技术结论**：Cube L1 Buffer 与 Vector Unified Buffer 间的直连通道免去了 L2 中转，显著**提高核内数据复用率**，减少 L2 层数据搬移开销，从而提升 CV 融合算子的执行效率。

3) **论文整体作用**：作为硬件级证据，支撑新架构在端到端吞吐、时延与开发效率三者之间取得更优平衡这一核心论点，是"CV 融合"特性论证的关键图示。
*caption: AI Core Cube-Vector 融合示意图… ｜ 论文 [[ascend-950-npu-architecture-whitepaper]] ｜ arxiv 见 MD 元信息*

### 昇腾 950 NPU 架构白皮书 — Fig.409 (p.25)
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig409.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象与结构：** 该图展示昇腾 950（950PR/950DT）的内存三级层次——底层为高速片上 DRAM（缓存全局数据，两型号配置不同），中层为 L2 Cache（服务 AIC/AIV 的 AI 计算，与片上内存双向搬运），上层为 L3 Cache（服务 AI CPU 通用计算），三级间以高带宽低延迟链路连通。

**关键技术结论：** 原文以此论证，分层存储将 AI 加速器与 CPU 的数据访问局部化——L2 以"片上 DRAM↔AIC/AIV"双向通路承担高吞吐 AI 数据流，L3 服务 CPU 通用任务，分工明确，整体提升 Memory 子系统效率。

**论文作用：** 该图作为硬件架构总览的关键图示，与执行单元、数据流等章节联动，为读者建立"存储-计算"协同的整体认知框架，是论文方法论证的视觉锚点。
*caption: 昇腾950 内存层次示意图… ｜ 论文 [[ascend-950-npu-architecture-whitepaper]] ｜ arxiv 见 MD 元信息*

### 昇腾 950 NPU 架构白皮书 — Fig.411 (p.27)
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig411.png]]
> [!tip] 【图文联合解读】**图文联合解读**：

需说明：图片实际为**图4-10 "Non-allocate (L2 hint) 典型应用场景示意图"**，而非所提示的 Figure 4-11 STARS2.0 架构图。以下按图实内容解读：

1. **核心对象与结构**：图中两个并行任务 Task0、Task1。其中 Task0 输出的 **data A** 沿 `non-allocate` 属性路径直接写入 Global Memory（绕过 L2 Cache）；而 Task0 与 Task1 共用的 **data B** 则经由 L2 Cache 中转复用，体现"绕过 vs. 复用"的差异化分配。

2. **论证的技术结论**：佐证正文所述——异腾 950 针对 SDMA 提供 L2 Cache 驻留策略（CMO），涵盖 Prefetch、Writeback、Flush 三类操作，程序员可通过配置参数控制 CMO 触发时机与作用域，从而按需决定数据是否驻留 L2。

3. **链路作用**：该图位于 4.4 节"软硬协同高效调度：STARS2.0"之前，承担**承上启下**作用——以存储层级访存优化收束，随后转入 STARS2.0 硬件调度器在任务/资源/数据流层面的协同调度论述。
*caption: STARS2.0 架构示意图… ｜ 论文 [[ascend-950-npu-architecture-whitepaper]] ｜ arxiv 见 MD 元信息*

### 昇腾 950 NPU 架构白皮书 — Fig.417 (p.36)
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig417.png]]
> [!tip] 【图文联合解读】图像无法辨认，仅依据原文解读。

**图文联合解读：**

1. **核心对象**：图 417 的标题为"昇腾 950 的一种超节点示意图"，按 caption 应展示昇腾 950NPU 超节点（Super-Node）的拓扑结构，包括多颗 NPU 芯片经高带宽互连（如 HCCS/UB 或自研总线）组成的紧耦合域，可能涉及片间/机框级互联、共享内存或拓扑编排示意。但实际图片仅显示章节标题"4.7 超节点能力 / 4.7.1 异腾超节点"，并无具体拓扑图。

2. **关键技术结论**：原文将其置于 4.7 节，作为昇腾 950 区别于单芯片能力的关键论据——通过超节点互联扩展算力规模与通信带宽，支撑大模型训练/推理中的跨芯片并行与协同。

3. **论文作用**：承接前文单芯片微架构、Cache/HBM、计算单元等设计，论证昇腾 950 由"单 NPU"扩展到"超节点"的系统级扩展能力，是性能规模化叙事的关键支撑图。
*caption: 昇腾950 的一种超节点示意图… ｜ 论文 [[ascend-950-npu-architecture-whitepaper]] ｜ arxiv 见 MD 元信息*

### 昇腾 950 NPU 架构白皮书 — Fig.418 (p.36)
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig418.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示呈现昇腾950超节点的三层交换拓扑：底层多颗Ascend 950芯片以曲线互联呈Full Mesh；中层各集群内Switch汇聚芯片间通信；顶层Switch跨集群互联，构成Clos/混合组网。原文据此论证：基于UB（Unified Bus）互连协议配合UB Switch，可组建K级别规模的超节点，芯片间通过UB实现高效通信，并支持Full Mesh、Clos、灵活混合等多种拓扑。该图位于4.7.2节"超节点与超大内存池组网"开篇，确立横向扩展架构框架，为后续引入CPU超大内存池共享与池化组网方案铺垫技术前提。
*caption: 昇腾950 访问CPU 超大内存池示意图… ｜ 论文 [[ascend-950-npu-architecture-whitepaper]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.1 (p.1)
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig01.png]]
> [!tip] 【图文联合解读】图(b)为IFBench/Qwen3 8B上的学习曲线对比：蓝线(GEPA)在前几百次rollout即陡升至近满分并保持高平台；绿线(MIPROv2)上升模式类似但终值略低；橙线(GRPO)增长极缓，24k rollouts后仍处低位徘徊。测试集星标(左上蓝星≈满分，右下橙星≈零分)直观显示泛化鸿沟。

原文借此论证两点关键技术结论：(1)基于反射的提示进化样本效率显著优于基于大规模采样的RL路线(GRPO)；(2)在提示优化领域亦超越SOTA的MIPROv2。

在论文中，该图作为开篇首张核心实验证据，确立GEPA"少样本、高性能"的范式优势，为后续跨任务(HotpotQA、Sudoku等)与跨模型族的泛化性论证奠定基础。
*caption: A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As mo… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.2 (p.3)
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示GEPA为多跳QA系统"二跳文档检索"任务所生成的优化提示词（GPT-4.1 Mini），由初始种子提示演化而来。优化后的提示词具有高度结构化特征，包含Task、Input Understanding、Purpose and Context、Key Observations and Lessons、How to Build the Query、Practical Strategy、Output共7大段落，并嵌入了具体策略（如"识别summary_1中提到的更广泛实体"）与正反例（Madeira群岛人口、歌曲→专辑），引导LLM生成补充性检索查询。

原文以此论证：**GEPA通过反思式提示进化，能产出结构化、含策略与示例的专家级提示，远胜简短种子提示**。该图作为定性证据，与附录L对各任务GEPA vs MIPROv2提示词的全面对比相呼应，共同支撑论文核心论点——**基于LLM反思的提示进化可超越强化学习方法**。在实验链路中，它处于"提示优化→任务执行→性能评估"环节的前端，用以直观展示GEPA所生成提示的复杂度与策略丰富度，为后续HotpotQA等基准上的量化结果提供可解释性背书。
*caption: This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, alo… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.3 (p.5)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]]
> [!tip] ## Figure Description (Architecture/Data Flow + Key Takeaway)

**Architecture/Components:** Figure 3 depicts GEPA's iterative optimization loop. Each iteration, GEPA proposes a new candidate via one of two strategies — *Reflective Prompt Mutation* or *System Aware Merge*. The candidate is first evaluated on a **minibatch**; if it improves, it advances to a **larger validation set** (D_pareto). Instead of greedily picking the single best mutator, GEPA uses **Pareto-based candidate sampling** — filtering and sampling from the per-task best list to preserve diversity. Surviving candidates are added to pool **P** with ancestry records. After the budget exhausts, the candidate with the best aggregate performance on D_pareto is returned.

**Key Takeaway:** GEPA replaces greedy single-best selection with **Pareto-frontier sampling**, trading short-term exploitation for diversity, which yields a local-optimum escape and superior sample efficiency/generalization. (≈95 words)

---

## Verbatim Caption Transcription

> Figure 3: GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section 3) or System Aware Merge (Appendix D.1)), first evaluating them on a minibatch, and if improved, evaluating on a larger dataset. Instead of selecting the best performing candidate to mutate always, which can lead to a local-optimum, GEPA introduces Pareto-based candidate sampling (Section 3.1), which filters and samples from the list of best candidates per task, ensuring sufficient diversity. Overall, these design decisions allow GEPA to be highly sample-efficient while demonstrating strong generalization.
*caption: GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.4 (p.4)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]]
> [!tip] I'm unable to fulfill this request as stated because **no figure is visible in the image provided**. This page (page 4 of an ICLR 2026 paper) contains only running text. The two figures referenced in the text — "Figure 3" (described as an overview of GEPA) and "Figure 4" (described as the full GEPA algorithm) — are mentioned but not rendered in this particular image. Additionally, no caption text is present on this page that I can transcribe verbatim.

What the page *does* contain, textually, is:

- **Formalization of a compound AI system** as ℳ = (M; C; X; Y), where:
  - M = {M₁; …; M_{|M|}} — language modules (LLM subcomponents, each with prompts P_i and underlying weights X_i)
  - C — control-flow logic orchestrating module invocation
  - X, Y — global input/output schemas
- **Two optimization formulations**:
  - Eq. (1): joint prompt + weight optimization, max_h,θ E_{(x,m)~T} [μ(x; h; θ; m)]
  - Eq. (2): budget-constrained variant, subject to ≤ B rollouts
- **Introduction of GEPA** (Section 3), motivated by three principles: genetic prompt evolution, natural-language reflective feedback, and Pareto-based candidate selection.

If you can share the actual figure page, I'd be glad to describe its architecture, data flow, key takeaway, and transcribe its caption.
*caption: GEPA receives the following inputs: A system  instan- tiated with simple prompts to be optimized, training dataset D train (consisting of task instan… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.5 (p.7)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]]
> [!tip] # Figure Description

**Note:** The provided image contains only text content from the paper (paragraph text, a figure caption, and section 3.1). No actual figure graphic is visible in this page extract — only the caption text appears. Below I describe what the caption communicates about Figure 5's intended content.

## Intended Figure 5 (based on caption)

**Architecture / Components:** The figure shows an annotated subtree extracted from Figure 25d, depicting GEPA's reflective prompt-mutation optimization trajectory on the PUPA (privacy-preserving delegation) task. Nodes represent prompt candidates; each node carries an annotation describing the prompt change at that step.

**Data Flow:** Progression flows from the base prompt (candidate 0) → best-performing prompt (candidate 11), visualized via red arrows indicating iterative refinements. Each refinement node is annotated with its targeted nuance, accumulated through successive rounds of optimization.

## Key Technical Takeaway

GEPA's iterative reflection accumulates **targeted, task-specific prompt refinements** (rather than generic rewrites), and these cumulative nuances compound to produce substantial performance gains — each step adds localized improvements informed by prior rollouts and feedback.

## Caption (Verbatim Transcription)

> **Figure 5:** GEPA's reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure visualizes the optimization trajectory taken by GEPA, presenting an annotated subtree from Figure 25d (for the privacy-preserving delegation task PUPA) to demonstrate the iterative enhancements made to the prompts. The progression from the base prompt (candidate 0) to the best performing prompt (candidate 11) is highlighted with red arrows, and key prompt changes at each step are annotated beside the corresponding nodes. Full-length instructions for these iterations are provided in Appendix K.1. Each prompt refinement in this trajectory adds targeted nuances informed by ongoing optimization, illustrating how GEPA's process accumulates lessons to continually boost task performance.
*caption: GEPA’s reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure v… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.6 (p.10)
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig06.png]]
> [!tip] 【图文联合解读】图6展示了在Qwen3 8B上四种候选选择策略于HotpotQA、IFBench、Hover、PUPA四个基准的聚合得分：Baseline 48.84、SelectBestCandidate 54.89（+6.05）、BeamSearch 53.95（+5.11）、GEPA 61.28（+12.44）。论文据此论证：贪心式"每轮选最优"一次迭代即陷入局部最优，改善幅度有限（Hover仅45.33、IFBench反降至30.44），说明早熟收敛；而Pareto采样（GEPA）各项均最优（Hover 52.33、PUPA 91.85），同等预算下提升幅度约为前两者的两倍。该消融实验支撑了GEPA算法设计的核心决策——以Pareto候选选择替代贪心/束搜索，强化其相对传统RL搜索与朴素提示优化的优势。
*caption: Comparing the impact of different candidate selection strategies. (Left) As can be seen, selecting the best-performing candidate in every iteration le… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.7 (p.13)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
> [!tip] # Observation About the Image

The image provided contains **only text** — specifically, two figure captions (Figure 7 and Figure 8) on page 13 of an ICLR 2026 paper. **The figures themselves are not rendered in this image**, so I cannot visually describe their architecture, components, or data flow from a chart/graph that isn't shown.

Below is a faithful transcription of the two captions visible on the page:

---

**Figure 7:** GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequential refinements with environment feedback, achieves an aggregate score of only 4.25%. When enhanced with retrieval-augmented generation (RAG) and MIPRO, the sequential refinement agent improves to scores of 16.33% and 19.03%, respectively. Notably, the final prompt produced by GEPA enables the same agent to reach a utilization score of 26.85%, all without requiring any runtime RAG.

**Figure 8:** GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast_p vs. rollouts plot for p=[0;5; 1], where the speedup is calculated over Pytorch-eager. fast_p is a metric described in (Ouyang et al., 2025) that measures the fraction of tasks for which the method generated a kernel executing faster than p times the baseline. As can be seen, GEPA with GPT-4o is able to generate cuda kernels executing faster than Pytorch-eager for over 20% of the 35 representative tasks.

---

If you can share the rendered figure (chart/graph), I'd be glad to describe its architecture, components, data flow, and key technical takeaway.
*caption: GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.9 (p.24)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]]
> [!tip] **Description of the main figure (Figure 9):**

The figure shows two pseudocode algorithms for **System-Aware Merge**:

- **Algorithm 3 — DESIRABLE(a; i; j; P)**: Iterates over each module m ∈ {1..jMj}, comparing ancestor and descendant prompts. Returns True only if either parent's module prompt matches the other (i.e., no constraint-affecting module changes), otherwise False.

- **Algorithm 4 — MERGE(P; A; S; r)**: A genetic crossover operator that (1) samples two distinct parents via a seeded stochastic sampler `r`, (2) skips direct-ancestry pairs, repeated merges, and children not improving parent's score, (3) calls DESIRABLE as a filter, (4) constructs offspring by copying parent P[a] and per-module selecting the prompt inherited from whichever parent contributes a unique module, defaulting otherwise.

**Key technical takeaway:** Merge uses ancestry-aware filtering plus a desirability check to ensure only constraint-preserving crossovers between promising, non-trivial parents survive — combining evolutionary search with structural constraint safety.

**Caption (verbatim):**
> Figure 9: Details of System Aware Merge. r represents a seeded stochastic sampler.
*caption: Details of System Aware Merge. r represents a seeded stochastic sampler.… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.10 (p.28)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
> [!tip] **Description:**

The page contains two figures from an ICLR 2026 paper:

- **Figure 10** (top): A two-panel bar/result chart showing final test-set performance across aggregate and individual benchmarks for two models: (a) `gpt-41-mini` and (b) `qwen3-8b`. Each subplot likely compares multiple training methods (e.g., GRPO, LoRA, GEPA) along the x-axis with performance scores on the y-axis.

- **Figure 11** (bottom): A learning-curve comparison plot on the 2-hop HoVer task, contrasting GEPA vs. GRPO under full-parameter fine-tuning across training steps, mirroring earlier LoRA comparisons (Figures 1, 12–15).

**Key takeaway:** GEPA's advantage over GRPO is consistent across training regimes — it maintains a comparable relative performance gap whether GRPO uses parameter-efficient (LoRA) or full-parameter fine-tuning, suggesting the gains stem from the algorithm itself rather than the optimization substrate.

**Caption (verbatim):**

(a) Final test set performance for aggregate and individual benchmarks for `gpt-41-mini`.

(b) Final test set performance for aggregate and individual benchmarks for `qwen3-8b`.

Figure 10: Final test set performance for aggregate and individual benchmarks.

Figure 11: This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetuning on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against GRPO with LoRA (in figures 1, 12, 13, 14, 15), showing that GEPA achieves a comparable performance gap relative to both full-parameter and parameter-efficient versions of GRPO.
*caption: Final test set performance for aggregate and individual benchmarks.… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.12 (p.29)
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图为Figure 12子图(c)，展示Qwen3 8B在HotpotQA上使用GRPO优化器时，4条不同配置曲线在0–250次rollout内的得分演化：蓝色曲线约50步内骤升至最高平台（约顶部），绿色虚线平稳居中，橙色阶梯式缓升至中低位，灰线始终贴底；星标分别标示各配置峰值，蓝星最高、灰星最低。

论文借此与同图(a)(b)的MIPRO基线并列，揭示RL类优化器在不同模型上样本效率与终值差异显著（GRPO在Qwen3 8B上收敛较慢、终值偏低），从而在整体实验链路中为GEPA的高样本效率与强泛化结论提供量化对照基准。
*caption: Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO 0 50 10 150 20 250… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.13 (p.29)
![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图13(c)展示了在IFBench基准上，Qwen3 8B模型采用GRPO方法时，"训练rollout次数（x轴）"与"得分（y轴）"的演化关系。可识别三条曲线：绿色线在前期迅速爬升至约0.85并保持平稳高位；橙色线缓慢上升，最终稳定在约0.55–0.60的较低水平；蓝色线几乎平直维持在接近0.95的高位（可能代表已优化提示或更强基线），星号标记各方法最优得分点。

论文借此图论证的关键结论是：在IFBench这一指令遵循类任务上，RL类方法（GRPO，橙色）优化效率低、得分上限受限；而反思式提示进化方法（绿色，GEPA）仅需少量rollout即可达到显著更高的分数，验证了"prompt evolution can outperform RL"的核心主张。

在论文整体实验链路中，该图属于RL基线对比环节，与MIPRO、HotpotQA等结果共同支撑作者关于"轻量级反思式提示优化在大模型上比强化学习更高效"的实验证据。
*caption: IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.14 (p.29)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
> [!tip] # Main Figure Description

The visible plots show **learning curves** for prompt/RL optimization experiments across four benchmarks. Each figure contains 3 subplots comparing:

- **(a) GPT-4.1 Mini - MIPRO** (off-prompt optimization baseline)
- **(b) Qwen3 8B - MIPRO** (off-prompt optimization on smaller open model)
- **(c) Qwen3 8B - GRPO** (on-policy reinforcement learning)

**Axes/components:** x-axis = rollout step (training iteration), y-axis = benchmark score. Multiple colored lines per panel appear to represent independent training seeds/runs, with star markers indicating final/best scores per seed.

**Data flow:** Each panel tracks how the optimizer's score on the target benchmark evolves over training rollouts. Only panel (c) for HotpotQA (Fig. 12) and IFBench (Fig. 13) renders visibly here; the others appear blank.

**Key technical takeaway:** GRPO (RL fine-tuning) on Qwen3 8B achieves competitive or superior benchmark scores with substantially fewer rollouts than MIPRO prompt-search variants, suggesting sample-efficient on-policy optimization can match or beat expensive prompt search — and crucially, transfers across diverse reasoning tasks (multi-hop QA, instruction following, claim verification, reasoning puzzles).

# Caption Transcriptions (verbatim)

**Figure 12:** Hotpot QA Bench: rollout vs. score for different models/settings.

**Figure 13:** IFBench: rollout vs. score for different models/settings.

**Figure 14:** HoverBench: rollout vs. score for different models/settings.

**Figure 15:** PUPA: rollout vs. score for different models/settings.
*caption: HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.16 (p.30)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
> [!tip] **Figure description (inferred from captions):**

**Figure 16** — A grouped bar/box plot showing the *generalization gap* (final test-set score minus best validation score) for several prompt-optimization methods, broken down by optimizer. It contrasts prior work (Wan et al., 2024), where exemplar-based optimizers generalized best, against the new finding that instructions from *reflective prompt evolution* also generalize strongly.

**Figure 17** — Two side-by-side scatter plots, (a) GPT-4.1 Mini and (b) Qwen3 8B, plotting *final aggregate benchmark score* (y-axis) against *aggregate prompt token count* (x-axis) for each optimizer (GEPA vs. MIPROv2, etc.). Each point is one optimized system.

**Key technical takeaway:** GEPA yields prompts that are **<33 % the size of MIPROv2's** while achieving **higher accuracy**, and its tokens are spent on *instructions* rather than few-shot exemplars—demonstrating that reflective, instruction-style optimization is more token-efficient and generalizes better on modern instruction-following LLMs.

---

**Caption (verbatim, Figure 16):**
> Figure 16: Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between final test set performance and the best achieved validation performance) for different optimizers. While Wan et al. (2024) previously observed that exemplars tend to generalize better, our results suggest that instructions generated by reflective prompt evolution can achieve stronger generalization as well as improved overall performance. We hypothesize this difference may be due to the improving capabilities of the underlying LLMs, as more recent models are both better at adhering to instructions and capable of reflecting on their outputs.

**Caption (verbatim, Figure 17):**
> Figure 17: These plots visualize the final aggregate scores against the aggregate prompt size (across all benchmarks) of the final optimized system for each optimizer. It can be seen that GEPA consistently produces prompts that are around less than 33% of the size of MIPROv2's prompts, while getting higher performance. Most of GEPA's prompt tokens are used for providing instructions, whereas most of MIPROv2's prompt tokens pertain to few-shot examples.
*caption: Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.18 (p.31)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
> [!tip] **Description of Figure 18:**

The figure presents a comparative analysis of token counts for optimized programs across multiple benchmarks, split into two panels. Panel (a) shows results for the GPT-4.1 Mini model, while panel (b) shows the same comparison for the Qwen3 8B model. The subplots compare different prompt optimization methods (visible in Figure 19's legend): Abl:SelectBestCandidate, SelectBestCandidate+Merge, GEPA-Best Config, and GEPA+Merge. Token counts are plotted on the y-axis against various benchmark tasks on the x-axis.

**Key Technical Takeaway:** GEPA+Merge generally achieves comparable or lower token counts than the ablation baselines while maintaining prompt quality, demonstrating that the merge step contributes meaningful efficiency gains during prompt optimization across both proprietary (GPT-4.1 Mini) and open-source (Qwen3 8B) language models.

**Caption (verbatim):**
"(a) Comparing the token counts of the optimized programs across benchmarks for GPT-4.1 Mini.
(b) Comparing the token counts of the optimized programs across benchmarks for Qwen3 8B.
Figure 18: Comparing the token counts of optimized programs across benchmarks."
*caption: Comparing the token counts of optimized programs across benchmarks. (a) Abl:SelectBestCandidate (b) SelectBestCandidate +… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.20 (p.32)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
> [!tip] # Description

The page (from an ICLR 2026 Oral paper, p. 32) contains three comparison figures whose rendered plot bodies are **missing** — only the sub-panel labels and captions are visible, suggesting a PDF/image extraction failure where the underlying charts did not render.

**Inferred structure** (from subcaptions): Each figure compares four ablation conditions across two benchmarks/two models, laid out as a 1×4 grid of panels (a–d). The variables compared are prompt-optimization methods: an ablation baseline (**SelectBestCandidate**), its **+Merge** variant, **GEPA**, and **GEPA+Merge – Best Config**. The vertical axes (not shown) likely track a metric such as optimized-prompt score vs. optimization budget/iterations, judging from the experimental naming.

**Key takeaway:** The ablation isolates *Merge* as the contributing factor, with **GEPA+Merge** reported as the **Best Config** in Figures 20 & 21, while Figure 22 splits it into separate (c) GEPA and (d) GEPA+Merge panels for finer comparison.

---

# Verbatim Caption Transcription

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate + Merge    (c) GEPA    (d) GEPA+Merge - Best Config
>
> **Figure 20: HotpotQA Qwen3 8B**

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate + Merge    (c) GEPA    (d) GEPA+Merge - Best Config
>
> **Figure 21: IFBench GPT-4.1 Mini**

> (a) Abl: SelectBestCandidate    (b) SelectBestCandidate+Merge    (c) GEPA - Best Config    (d) GEPA+Merge
>
> **Figure 22: IFBench Qwen3 8B**

Header: *"Accepted at ICLR 2026 (Oral)."* · Page number: **32**
*caption: HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.23 (p.33)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
> [!tip] **Description (≤120 words):**

The page shows three comparative ablation figures (Figures 23–25) from a paper accepted at ICLR 2026 (Oral), each evaluating prompt/optimization configurations across two benchmarks (HoVer, PUPA) and two models (GPT-4.1 Mini, Qwen3 8B). Although the plotted curves/data are not rendered in this image (only subplot labels appear), the consistent 2×2 ablation matrix compares: (a) Ablation: SelectBestCandidate as baseline, (b) SelectBestCandidate + Merge, (c) GEPA (with "Best Config" variant in Fig. 24), and (d) GEPA + Merge (with "Best Config" variant in Fig. 23 and Fig. 25). The shared structure suggests an ablation study isolating the contribution of selection vs. merging in GEPA-style reflective prompt optimization.

**Key takeaway:** The figures ablate whether *merging* candidate prompts adds value on top of GEPA's reflective selection mechanism across model sizes.

**Caption transcription:**

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA
>
> (d) GEPA+Merge - Best Config
>
> Figure 23: HoVer GPT-4.1 Mini

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA - Best Config
>
> (d) GEPA+Merge
>
> Figure 24: HoVer Qwen3 8B

> (a) Abl:SelectBestCandidate
>
> (b) SelectBestCandidate + Merge
>
> (c) GEPA
>
> (d) GEPA+Merge - Best Config
>
> Figure 25: PUPA GPT-4.1 Mini
*caption: HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.26 (p.34)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]]
> [!tip] **Main Figure Description:**

The page references **Figure 26: PUPA Qwen3 8B**, which compares four prompt-optimization strategies for a privacy-preserving LLM request task on the Qwen3 8B model. The four conditions labeled are: (a) Ablation of SelectBestCandidate, (b) SelectBestCandidate + Merge, (c) GEPA – Best Config, and (d) GEPA + Merge. Below the caption, Section K.1 ("Prompts at Intermediate Stages for PUPA") showcases two evolved prompts from a search tree — Node 0 (score 82.26), a terse two-line instruction, and Node 2 (score 90.99), a richly structured prompt with explicit Task Description plus enumerated "Key Points and Domain-Specific Details" covering Privacy Preservation and Query Reformulation. The progression illustrates how GEPA's evolutionary search elaborates lightweight seeds into detailed, rubric-aligned instructions.

**Key Technical Takeaway:** GEPA's reflective prompt evolution converts minimal seed prompts into detailed, multi-section rubrics — increasing PUPA's Qwen3-8B score from ~82 to ~91 — demonstrating that structured, principle-rich prompts substantially outperform terse ones for privacy-preserving query rewriting.

**Caption (verbatim):**
"Figure 26: PUPA Qwen3 8B"
*caption: PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.27 (p.12)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]]
> [!tip] # Figure Description

There is **no figure visible on this page**. Page 12 contains only textual content from two sections:

- **Section 5.1** ("GEPA for Inference-Time Search (Contd.)") — discusses preliminary findings using GEPA as an inference-time search technique for code-generation tasks (NPU kernels and CUDA kernels). It references two figures that appear elsewhere in the paper:
  - **Figure 27** — "the detailed prompt for NPUEval" (mentioned but not shown here)
  - **Figure 8** — depicts GEPA boosting GPT-4o's close-to-0% fast₁ score above 20% with increasing search budget (mentioned but not shown here)

- **Section 5.2** ("GEPA for Adversarial Prompt Search (Contd.)") — describes instantiating GEPA for adversarial prompt search by inverting the reward signal, evaluated on AIME-2025.

# Caption Transcription

**No figure caption is present on this page.** The two figures referenced (Figure 8 and Figure 27) appear on different pages of the paper and are not displayed here.
*caption: We also note that generation stochasticity (temperature based sampling) is eliminated by operating under a cache; this ensures that ob- served improve… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.1 (p.1)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**核心结构**：图(a)展示Orca的两级PP调度——4个请求A/B/C/D以完整prefill块(A_p, B_p, C_p, D_p)串行执行，decode小条(A_d1, B_d1…)稀疏插入，GPU1出现两段明显Bubble；图(b)展示SARATHI——prefill被切分为A_p1/A_p2、B_p1-B_p3、C_p1/C_p2、D_p1/D_p2等小块，与decode token密集交错，GPU1与GPU2均无空泡。

2）**关键结论**：原文借此论证三点——(i)完整prefill长度不一导致pipeline bubble；(ii)decode单token开销比prefill高一个数量级却独占调度；(iii)SARATHI通过"chunked prefill + decode-maximal batching"将decode"搭车"piggyback到prefill chunk上，消除bubble并摊薄decode成本。

3）**论文作用**：作为开篇Figure 1，承担problem statement与solution teaser双重职能，为后文chunk size分析、stall-free调度及decode-maximal batching策略提供视觉锚点。
*caption: Example two-stage pipeline parallel schedule. (a)… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.2 (p.3)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig02.png]]
> [!tip] 【图文联合解读】**(a) Decoder Block**：两层子模块堆叠，每层均为「LayerNorm → 子模块 → Add残差」结构；下层为Attention，上层为FFN。

**(b) Attention**：输入经 `W_{Q,K,V}`（`H→3H`）线性投影拆分为 Q/K/V，送入 Self-Attention，结果 Concat 后再经 `W_O`（`3H→H`）与 Dropout 还原到 H 维。

**(c) FFN**：经 `W（H→H2）→GeLU→W（H2→H）` 双层线性变换加 Dropout，维度先扩后缩。

**作用**：该图量化了decoder每token的算子构成，为文中对比 prefill 与 decode 每token耗时（Table 2）提供结构依据——即 prefill 是 compute-bound（`H→3H` 大矩阵乘），decode 是 memory-bound。这正是 Sarathi 提出 "chunked prefill piggyback decodes" 的前提：通过切分长 prompt 为与 decode token 尺寸匹配的 chunk，把 compute-heavy 的 prefill 塞进 decode batch 的空闲槽，从而提升 GPU 利用率。
*caption: High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.3 (p.4)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示左为 Prefill（batch 1–18，per-token 时间稳定在 ≈0.23–0.25 ms）、右为 Decode（batch=1 时 ≈46 ms，batch=18 时 ≈3 ms）的堆叠柱图，按 preproj / attn / postproj / ffn_ln1 / ffn_ln2 / others 分解。Prefill 在 batch=1 即饱和 GPU，耗时近乎恒定；Decode 受内存带宽限制，其中 attention 几乎不随 batch 摊薄，而线性算子可摊薄——batch=1 时 decode ≈200× prefill。

该图揭示 **prefill 与 decode 的算力–带宽不对称**，是论文核心动机：证明将 decode 请求"挂靠"到饱和算力的 chunked prefill 上、填补 decode 未利用 GPU 算力的必要性，即 Sarathi 合并调度方案的设计前提。
*caption: Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even a… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.4 (p.4)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**(a)** LLaMA-13B/A6000 上 Prefill（1K 序列）在 batch=1 时即达 ~180 tokens/ms，吞吐随 batch 几乎饱和，曲线平坦；而 Decode 在 batch<32 时吞吐极低（<20 tokens/ms），仅在大 batch（≥256）且短序列（64）下才升至 ~100 tokens/ms。

**(b)** Prefill 算术强度随 batch 增长（≈800→2750），呈计算密集型；Decode 算术强度长期 <10，batch=256 时才跃升至 ~125–240，呈典型访存密集型。

**论证结论：** Prefill 与 Decode 的算术强度存在数量级差异（计算 vs 访存瓶颈不同），这是两者无法在同 batch 中高效并发的根因。论文由此提出将 Prefill 分块"挂载"（piggyback）在 Decode batch 上，将短 Prompt 切碎以拉高 Decode 的 batch size 从而提升其算术强度，实现二者吞吐同时增益——这是 Sarathi 调度策略的核心动机。
*caption: Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU. operations. Figure 4b shows th… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.5 (p.5)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**① 图示内容：** 2路PP跨GPU1/GPU2处理4个请求(A,B,C,D)的时间线。GPU1先依次完成Aₚ/Bₚ/Cₚ/Dₚ四个prefill块，随后出现PB₁、PB₂、PB₃三段虚线"气泡"，再处理Aᵈ1Bᵈ1、Cᵈ1Dᵈ1、Aᵈ2Bᵈ2等decode批次；GPU2延迟一个iteration启动，同样跑完prefill后衔接decode，未见明显空闲。

**② 论证结论：** 由于同一batch内prefill与decode耗时差异显著（非均匀执行时间），标准iteration级PP调度会在GPU上产生pipeline气泡，造成算力浪费。

**③ 论文作用：** 作为动机图，引出Sarathi的核心方案——将prefill切分为chunk与decode混合批处理，用decode"piggyback"填充气泡，提升吞吐。
*caption: Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to … ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.6 (p.6)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig06.png]]
> [!tip] 【图文联合解读】## Figure 6 深度解读

**1) 核心对象与结构**
该图为第三个 chunk prefill 迭代的注意力掩码矩阵。横轴为 12 个 key token（k0–k11），按 chunk_size=4 分为三组；纵轴为 4 个 query（q8–q11）。绿色区（k0–k7）全为 1，表示对历史 chunk 的注意力可复用预计算的 K/V；橙色区（k8–k11）呈下三角掩码——q8 仅关注 k0–k8，q9 关注 k0–k9，q10 至 k0–k10，q11 全关注，体现新 chunk 内部的标准因果掩码。

**2) 原文论证的关键技术结论**
证明 chunked prefill 中，**旧 chunk 的 query（q8）只需与本 chunk 及之前 key 计算注意力**，无需重算；**新 chunk 的 query（q9–q11）仅需对当前及之前 token 做因果掩码**。即不同位置 query 所需注意力范围不同，为"非对称计算"和 piggybacking decode 提供了形式化依据。

**3) 在论文方法链路中的作用**
该图是 SARATHI 混合批处理（prefill + decode 同 batch）可行性的**核心可视化证据**：它解释为何可将 decode 的 query 拼接到 prefill chunk 后，无需重算全部注意力，从而支撑论文关于吞吐提升与流水线效率的核心论点。
*caption: Example of how attention mask is set across dif- ferent chunk prefill iterations in SARATHI (q and k represent “query" and “key" tokens, respectively)… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.7 (p.7)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 7）**

**1）核心对象与结构**：图将 LLaMA-13B 在 A6000 上单次 transformer 迭代拆为 preproj、postproj、ffn、total compute 四条曲线，横轴为序列长度 0–1024，纵轴为耗时（ms）。preproj 缓慢从约 10ms 升至约 60ms；postproj 最小，全程 ≤20ms；ffn 主导耗时，从约 30ms 阶梯式跃升至约 150ms；total compute 从约 45ms 增至约 270ms。**关键特征**是 ffn 与 total compute 呈明显"楼梯状"跳变，突变点集中在 128、256、512、640、768、896 等处——这正是 GPU 矩阵乘 tile 尺寸边界，即 tile quantization 效应的可视化证据。

**2）原文论证结论**：prefill 计算量并非随长度连续线性增长，而是按 tile 大小离散跳变；非 tile 对齐的请求会浪费碎片化算力。这是 Sarathi 采用"chunked-prefill、将 chunk 设为 tile 边界倍数"策略的硬件层动因。

**3）在论文链路中的作用**：与前文 decode-maximal batching 对比呼应，作为 Sarathi-Serve 调度设计的实验支撑——证明以 tile 对齐 chunk 切分预填充，可显著降低单步延迟、消除碎片开销。
*caption: The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU. maximal batching with that of the baseline scheme that com-… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.8 (p.9)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig08.png]]
> [!tip] 【图文联合解读】**Figure 8 图文联合解读**

**1) 核心对象与数据**：横轴为 Batch Size（2–18），纵轴为 Decode-only 阶段加速比（0–10×），三组序列长度：1K（橙色）、2K（灰斜纹）、3K（绿网格）。1K 序列覆盖全部 batch；2K 止于 batch=8（最高≈5.8×，batch=2）；3K 仅至 batch=6（最高≈4.4×，batch=2）。随 batch 增大加速比单调下降：1K 由 ~9.8× 降至 ~2.7×；序列越长，可承载的 batch 越小，加速比也越低。

**2) 关键结论**：即便排除 piggyback prefill 的收益，仅 decode 阶段 SARATHI 仍带来显著加速（最高近 10×），证明 chunked prefill 通过提高 GPU 利用率与改善 kernel 调度，正面惠及纯 decode 路径，而非仅来自混合 prefill 的分摊。

**3) 在论文中的作用**：作为单独剥离 decode 的 ablation，排除"加速源于把 prefill 摊到 decode 上"的混淆，从机制层面夯实 SARATHI 在混合负载下整体吞吐提升的根基。
*caption: Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.9 (p.10)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示 LLaMa 13B 在 A6000 上、三种序列长度（1K/2K/3K，对应批大小 18/10/6）下，三档 chunk size（128/256/512）的归一化吞吐随 Prefill/Decode（P:D）比的变化曲线。

**核心数据：** 各曲线均在低 P:D 处达到峰值后单调下降；1K 时 chunk=256 峰值最高（≈1.27，P:D≈15），3K 时 chunk=512 峰值最高（≈1.20，P:D≈60），chunk=128 在所有场景下均最差（峰值≈1.13）。

**论证结论：** 存在最优 P:D 比，且最优 chunk size 随序列长度增大而增大（短序列宜小 chunk，长序列宜大 chunk），Sarathi 相对纯 decode 基线最高可获 ~27% 吞吐增益。

**论文作用：** 为 Sarathi 在实际部署中根据序列长度自适应选择 chunk size 与调度 P:D 比提供量化依据，支撑"分块 prefill 搭车 decode"通用性论点。
*caption: Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequence lengths, P:D ratios, and chunk sizes. 2 4 6 8 10 12 14 16 18… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.10 (p.10)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图10以2×3堆叠柱阵展示LLaMa-13B在A6000上的算子级耗时分解，蓝色（SARATHI）柱普遍低于橙色（baseline），且差距随batch增大而扩大。例如seq_len=1K、chunk=256时，bs=18下baseline≈8.6s而SARATHI≈6.8s，节约约20%；seq_len=3K、bs=6下由≈8.4s降至≈6.8s。各分量中ffn占比最大、attn次之，preproj/postproj较小，且SARATHI主要压缩ffn与attn段，pre/postproj几近持平。chunk=512整体比256更优（如bs=18、1K时由6.8s再降至≈5.2s）。

**论证结论：** chunked-prefill与decode piggybacking通过提升kernel利用率，使ffn（GEMM-heavy）受益最显著，且随batch放大收益递增；减小chunk size会部分抵消优势。

**论文链路作用：** 与端到端加速比互补，作为微观算子级归因证据，支撑"SARATHI消除prefill/decode失衡、提升GPU利用率"的核心主张。
*caption: Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk si… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.11 (p.11)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig11.png]]
> [!tip] 【图文联合解读】图(b)展示在序列长度1K、batch size=18下，SARATHI三种chunk尺寸（128/256/512）与Orca best-case随Prefill/Decode比（0–100%）变化的归一化吞吐曲线。SARATHI在低P:D区间（5–30%）出现峰值：chunk=256在P:D≈15%达1.26×，chunk=512在≈30%达1.23×，chunk=128在≈5%达1.14×；Orca best-case最高仅约1.10×。该图与子图(a)共同论证：SARATHI的chunked prefill合并策略在多种负载下均稳定优于Orca迭代级调度，是验证"Splitwise+chunked"设计优于纯迭代调度的关键消融证据。
*caption: Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. configuration of sequence length and chunk size, we show the effect of vary… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.12 (p.12)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 12b）**

**核心对象与数据**：图(b)展示GPT-3在DGX A100上仿真部署下，三种调度策略处理0–10000请求时的端到端完成时间。在10000请求时，SARATHI（蓝色虚线）约1900s，TP+PP（橙色实线）约3700s，TP(8 replicas)（绿色点划线）约2900s，三者近似线性增长但斜率差异显著。

**关键技术结论**：通过将decode与chunked prefill混合调度消除pipeline bubble，SARATHI相较TP+PP将请求完成时间降低近50%，相较TP(8 replicas)亦快约35%，验证了混合流水策略的端到端优越性。

**论文整体作用**：与图(a)的pipeline bubble分析呼应，从微观（气泡占比）到宏观（用户可见延迟）共同构成SARATHI有效性的完整证据链。
*caption: Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation. the effect of varia… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.13 (p.13)
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据**：Figure 13 包含三组柱状图，实验对象为 LLaMa-13B on A6000，序列长度取 1K/2K/3K，每组 8 根柱对应 chunk size 64–512。(a) 纯 self-attention 加速比：随 chunk 增大由 ~0.27（64@1K）升至 ~0.88–0.90（256–512@3K）；(b) chunked-prefill vs. full prefill 端到端加速比：1K 时 64 仅 ~0.2、512 达 ~0.95，长序列在 256 后基本饱和；(c) 整 batch 端到端加速比（chunked-prefill + decode-maximal）：各 chunk 下均 >1，1K 时峰值 ~1.28（256/512），3K 仍 ~1.22。

**2) 关键结论**：单独 chunked-prefill（b）在小 chunk 下甚至慢于全序列 prefill；但一旦与 decode 批处理联合调度（c），系统整体获得 20%+ 加速，验证了"decode piggyback"才是收益主因，而非单纯切分。

**3) 在论文中的作用**：作为消融实验，剥离自注意力开销与整批吞吐量两个层面，量化证明 Sarathi "chunked-prefills × decode co-batching" 的设计必要性——为方法核心的 piggyback 调度策略提供实证支撑。
*caption: Ablation study: Effect of varying the chunk size on different components of the system for LLaMa 13B on A6000 GPU. measure the time to compute the pre… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.1 (p.1)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig01.png]]
> [!tip] 【图文联合解读】图1a为0~350s生成token数曲线：Sarathi-Serve平滑升至约30K tokens，vLLM呈阶梯状，在200~220s出现明显"Generation stall"（插图标注）。图1b为P99 token间隔柱状图，在QPS=0.55/0.7/1.0下vLLM从约0.5s飙升至约1.4s（负载越高恶化越剧），Sarathi-Serve稳定在约0.3~0.35s。该图作为开篇动机图，定量揭示vLLM在高并发下存在秒级生成停顿与尾部延迟膨胀两大缺陷，为Sarathi-Serve以chunked-prefill+stall-free调度兼顾吞吐上限与消除停顿的核心论点提供直接实证依据，并奠定后文调度设计与实验评估的必要性。
*caption: Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation trace. 1a highlights one of the many generation stalls lasting over seve… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.2 (p.2)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig02.png]]
> [!tip] 【图文联合解读】**图2解读：**

**1) 结构与数据**：二维定性定位图，纵轴为Throughput（越高越好），横轴为TBT Latency（越右越差）。四个系统坐标分别为：FasterTransformer（红圆，左下——decode优先，吞吐与TBT均低）、Orca（紫圆，中部偏右——prefill优先）、vLLM（蓝圆，右上——prefill优先，吞吐高但TBT尾延迟高）；三者由灰色虚线串联，标注"迭代级批处理→Paged Attention"，构成既有方法的帕累托前沿。Sarathi-Serve（绿色星标）独立位于左上象限——高吞吐、低TBT延迟，旁注"Stall-free batching"。

**2) 关键结论**：现有系统受调度策略制约，prefill优先换高吞吐却牺牲TBT，decode优先反之，沿虚线呈此消彼长；Sarathi-Serve通过无停顿批处理跳出该曲线，**同时实现高吞吐与低TBT**，打破throughput–TBT权衡。

**3) 论文作用**：图位于第2页，作为问题动机图，先建立tradeoff认知、再预告方法定位，为后续chunked prefill、stall-free调度等机制设计与实验评估提供论证锚点。
*caption: Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes … ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.3 (p.5)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig03.png]]
> [!tip] 【图文联合解读】**图3联合解读：**

该图含左右两子图（Mistral-7B / 单卡A100，prompt长度1024）：
- **Prefill**：批大小 1/2/4/8，吞吐约 4.5k→5.4k→5.2k→4.8k tokens/s，BS≥2 即饱和甚至略降；
- **Decode**：批大小 1/8/16/32/64，吞吐约 10→110→220→420→810 tokens/s，随批大小近似线性增长。两图纵轴相差近一个数量级。

**论证结论**：prefill 计算密集，单请求即吃满算力，batching 边际收益小；decode 访存密集，受制于单 token 访存开销，batching 能近乎线性放大吞吐。

**论文作用**：揭示两阶段算力–访存特性失衡这一根因，为 Sarathi-Serve 提出"分块 prefill + decode 共批（stall-free batching）"以提升整体吞吐、压低时延提供直接动机。
*caption: Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for b… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.4 (p.5)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig04.png]]
> [!tip] 【图文联合解读】**图4解读：**

**1）核心数据：** 左图为Mistral-7B在A100上的Prefill耗时（序列长度128→2k），从约33ms单调上升至约143ms，其中linear层（青色斜纹）始终占主体（2k时约120ms），attention与others占比小。右图为Decode耗时（batch size 1→64），全程几乎持平于18–23ms，linear仍为主，attention可忽略。

**2）关键结论：** Prefill与Decode均以linear层为瓶颈；因decode算术强度低，**1个decode token的linear开销≈128个prefill token**，且增加batch几乎不放大延迟，说明decode是访存受限。

**3）在论文中的作用：** 该图是Sarathi-Serve提出"chunked prefill+decode共批"（splitwise）的核心动机——证明把prefill小块塞进decode batch可被现有GPU带宽"免费"吸收，从而打破throughput–latency权衡，同时解释了为何大batch下throughput仍受限。
*caption: Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in b… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.5 (p.6)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig05.png]]
> [!tip] 【图文联合解读】【对象】LLaMA2-70B 线性运算在 4×A100 上的算术强度（FLOPs/bytes）随 token 数变化曲线：Decode（~30 token, ~50）位于红色 Memory Bound（Low MFU）区，Prefill（~1000 token, ~800）位于绿色 Compute Bound（Low MBU）区，Sarathi-Serve 平衡点（~600 token, ~500）恰落在两虚线交点——鞍点。

【结论】Decode 算术强度低，访存受限→MFU 低；Prefill 计算密集→MBU 低；二者单独执行均欠佳。Sarathi-Serve 将 prefill chunk 与 decode 混合，把工作点钉在鞍点附近，从而同时提升 MBU 与 MFU。

【作用】为论文核心调度策略（chunked prefill + 混合批）提供硬件层量化动机，是吞吐–时延权衡取舍设计的理论锚点。
*caption: Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different number of token running on four A100s. Decode batches have low arithmetic… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.6 (p.6)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图6展示LLaMA2-70B在A100上线性层执行时间随batch token数（128–4096，对数轴）的变化，对比TP-2（蓝）与TP-4（橙）两条曲线，呈阶梯状增长。具体数据：128 token时TP-2约60 ms、TP-4约30 ms；2048 token时升至约450 ms / 300 ms；4096 token时TP-2约1000 ms、TP-4约520 ms。在128–512区间两曲线均近水平平坦，TP-4始终低于TP-2。

原文借此论证：小batch时执行时间受HBM权重读取带宽主导而非算力，故线性层在小token区间呈"停滞"；越过拐点后计算主导，时间随token近似线性增长，TP-4因权重切片更小更优。

该图为Sarathi-Serve的核心论据之一：揭示线性层存在内存带宽受限的"空闲区间"，从而支撑其"chunked prefill + decode共batch"策略——利用停滞区填入prefill片段以提高吞吐，而不会显著增加延迟，从而同时优化throughput–latency权衡。
*caption: Linear layer execution time as function of number of tokens in a batch for LLaMA2-70B on A100(s) with different tensor parallel degrees. When the numb… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.7 (p.6)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig07.png]]
> [!tip] 【图文联合解读】图7沿时间轴横向对比四种调度的迭代块序列：vLLM在A_d、B_d之后串入C_p、D_p两个全prefill，导致A、B的decode发生stall（标注"TBT with prefill interference"）；Orca以C_p/D_p/A_d/B_d混合批处理，但因长prompt执行时长仍高，无法消除A、B的stall；FasterTransformer则反复多轮A_d/B_d直至A、B退出才调度C_p、D_p，虽无decode stall但新请求prefill却停滞；Sarathi-Serve将C、D的prefill各切分为p1、p2两chunk，在A_d、B_d的decode间隙交叉插入，实现全程"No stalls"。

该图是论文核心可视化论据，定量证明仅靠"混合批"或"优先级极端倾斜"都无法双赢——唯有**chunked prefill与decode交错**才能兼顾吞吐与延迟，直接引出Sarathi-Serve"分块+交错调度"的核心方法论，并为后续Figure 8的stall-free时间线与正文throughput–latency tradeoff论证提供基础。
*caption: A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent diffe… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.8 (p.7)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig08.png]]
> [!tip] 【图文联合解读】**图8 联合解读**

图8对比两套2路PP调度（GPU0+GPU1×4请求A-D）时间线：
① **Orca（上行）**：两GPU错位执行，标出两类灰色气泡——prefill长度差异（A_p/B_p vs C_p/D_p耗时不同）及prefill/decode相互干扰（解码等待下一个prefill完成），出现明显空档；
② **Sarathi-Serve（下行）**：将每请求切分为A_p1/A_p2/A_d1/A_d2等定长块，两GPU锁步执行，标注"Minimal Bubbles"，气泡几乎不可见。

原文借此论证：变长prefill与prefill-decode共存是Orca流水线气泡的两大根源，而uniform-compute批次（分块prefill）能基本消除之。该图是Sarathi-Serve核心设计——**chunked-prefill+uniform batch**——的关键动机图，为后续吞吐-时延权衡实验奠定理论依据。
*caption: A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batc… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.9 (p.8)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图9以2×3柱状图，对比三种批处理策略在Mistral-7B（单A100，预算256）与LLaMA2-70B（4×A100，预算512）上的batch time，扫描上下文{1024, 2048, 4096}与batch size{1, 32, 64}。数据表明：Decode+Full Prefill开销随上下文急剧放大（如70B在ctx=4096、batch=1时达28.3×），而Decode+Chunked Prefill开销稳定可控（多数情形≤3.7×，且随batch增大而衰减）。

该图论证关键结论：Orca式完整prefill混合会严重阻塞decodes、破坏SLO；而分块prefill将代价封顶于token预算内。论文以此实验支撑Sarathi-Serve的核心设计——chunked prefill是实现throughput–latency可控权衡的必要性前提，而非可选优化。
*caption: The incremental cost of coalescing prefills with decode batches. We consider two batching schemes – (i) Decode +… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.10 (p.11)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图10以双子图形式展示两种数据集下（(a) openchat_sharegpt4；(b) arxiv_summarization），Orca、vLLM、Sarathi-Serve 三种调度器在 Mistral-7B 与 Yi-34B 上的最大吞吐（QPS），分 SLO-S（严格）和 SLO-R（宽松）两档。关键定量结果：Mistral-7B 在 openchat 上 Sarathi 达 ~2.05/2.25 QPS（标注 2.78×/2.15×）；Yi-34B 在 SLO-S 下获 **4.00×**（最强增益）；arxiv 跨模型亦保持 1.69×–1.97× 的稳定领先。

**论证结论**：Sarathi-Serve 在满足 SLO 的前提下，吞吐量在所有 (模型×数据集×SLO) 组合上均高于 Orca 与 vLLM，且大模型/长输入场景优势更显著，证明 chunked-prefill 与 decode 协同调度对吞吐–延迟权衡的"驯服"是普适的。

**论文作用**：与 Fig.7–9 共同构成 §6 评估核心，从端到端时延、首 token 延迟到最大承接容量逐级收敛，最终锁定"显著扩容 + 不破 SLO"的方法优势。
*caption: Capacity (in queries per second) of Mistral-7B and… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.11 (p.11)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig11.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图11含(a)(b)两子图，对比 Orca、vLLM、Sarathi-Serve 三种调度器在 LLaMA2-70B 与 Falcon-180B（均采用流水线并行 PP）下的最大容量（Max Capacity），分别在严格 SLO-S 与宽松 SLO-R 下评估。(a) openchat_sharegpt4 上 Sarathi 相对 vLLM 提升 **5.54–6.31×**；(b) arxiv_summarization 上严格 SLO 下为 **4.20–4.69×**，宽松 SLO 下为 **2.75–3.00×**。

**关键结论**：Sarathi-Serve 在满足时延 SLO 的同时显著提高吞吐，且严格 SLO 下优势更突出，验证其 chunked-prefill + decode-fusion 调度对流水线并行大模型同样有效。该实验将论证从单 GPU 张量并行场景扩展到多节点 PP 场景，补强了全文的方法—实验论证链。
*caption: Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with different schedulers under strict (SLO-S) and relaxed (SLO-R) latency… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.12 (p.12)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图含两子图：上图为 Mistral-7B（P99 TBT SLO 范围 0.1–0.5s），下图为 Yi-34B（0.2–1.0s），纵轴均为最大吞吐量（Max Capacity）。对比 vLLM 三档 batch（32/64/128）与 Sarathi-Serve 两档 token budget（SS-512、SS-2048）。

**关键数据**：Mistral-7B 上 SS 稳定在 2.0–2.3 之间，vLLM 仅 0.78–1.57；Yi-34B 上 SS 维持 1.14–1.28，vLLM 不及 0.8。SS-2048 在严格 SLO 下起点较低（Mistral 0.5、Yi-34B 0.2），随 SLO 放宽迅速反超 vLLM 并趋平。

**论证结论**：在任意延迟约束下，Sarathi-Serve 均显著优于 vLLM，模型越大优势越明显，验证了分块预填充 + token budget 对吞吐–延迟权衡的优化效果，是论文核心实验支撑。
*caption: Latency – Throughput tradeoff in vLLM and… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.13 (p.12)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig13.png]]
> [!tip] 【图文联合解读】**图13联合解读**

图13以Falcon-180B为对象，对比跨节点并行策略。(a)P50 TBT条形图：batch 8→128时，纯跨节点TP8从~0.19s升至~0.36s，而TP4:PP2（节点内TP+跨节点PP）稳定在0.08–0.15s，batch=128时差距达2.4×。(b)容量图：SLO-S下Sarathi-Serve TP4:PP2达~0.6，是vLLM TP8（~0.13）与vLLM TP4:PP2（~0.15）的~4.6×与4×；SLO-R下亦达~0.75。

该图论证两点：①跨节点TP因通信开销大导致TBT膨胀、扩展性差，应以PP替代；②在混合并行配置下，Sarathi-Serve的chunked-prefill与融合调度显著放大吞吐。它在论文中作为核心方法（延迟-吞吐权衡调度）面向跨节点超大模型场景的关键实验支撑，验证"避免跨节点TP + 采用Sarathi调度"是同时满足SLO与高吞吐的必要组合。
*caption: TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP withi… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.14 (p.13)
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig14.png]]
> [!tip] 【图文联合解读】**图示内容**：Yi-34B(TP-2)上chunked-prefills相对no-chunking的prefill开销归一化柱状图。横轴为prompt长度2K/4K/8K，三色柱对应chunk=512/1024/2048。读数：chunk=2048时开销≈1.00、1.00、0.97（几无额外成本）；chunk=1024约1.18–1.23；chunk=512约1.28–1.35，随prefill长度变化趋于稳定。

**技术结论**：chunked-prefills并非零代价，chunk越小overload越高（小至512时引入20%–35%额外计算），而chunk≥2048基本消除开销。

**论文作用**：量化分块预填充的计算代价，为Sarathi-Serve选用2048 chunk粒度（兼顾decode共批与prefill开销）的设计决策提供实验依据，支撑"分块几乎不损prefill效率"的核心论点。
*caption: Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using ch… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### DeepSeek-V4: Towards Highly Efficient Million-Token Context  — Fig.1 (p.14)
![[assets/crops/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图左为分组柱状图，横轴并列7项基准，每组三柱（蓝条纹=DeepSeek-V4-Pro-Max，深灰/浅灰柱为对比模型），蓝柱在多数指标上达到或超过对应灰柱；图右上下两块楔形面积图分别刻画推理FLOPs与KV cache随序列长度增长的斜率，V4系列曲线显著低于V3.2基准线。

该图论证核心结论：V4-Pro-Max以**更低推理算力与KV占用**实现基准性能对标或反超同类模型，呼应2.4节Muon优化器对训练效率的改进。

在论文链路中，它起到总览性"性能–效率"双重证据作用，支撑"百万token高效上下文智能"主旨，为后文长horizon任务与测试时扩展的可行性提供定量依据。
*caption: 2.4. Muon Optimizer… ｜ 论文 [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] ｜ arxiv 见 MD 元信息*

### DeepSeek-V4: Towards Highly Efficient Million-Token Context  — Fig.5 (p.15)
![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]]
> [!tip] 【MiniMax 解读】DeepSeek-V4 细粒度 EP(Fig.5)：MoE 层拆 Dispatch/Linear-1/Linear-2/Combine 四段。Comet 仅粗粒度重叠 Dispatch↔L1、L2↔Combine；本方案把 expert 再切 wave，一波 dispatch 完即开算、下一波并行 dispatch→稳态下「当前波计算+下一波 token 传输+上一波结果回送」三路并发=连续计算-通信流水。因单层通信<计算，融合成单流水 kernel 藏住互连延迟→低带宽互连也不掉吞吐。架构核心图，与 MoE/EP 相关。
*caption: This forms a fine-grained pipeline among experts, keeping both computation and communication continuous throughout the wave. The wave-based scheduling… ｜ 论文 [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.1 (p.1)
![[assets/crops/kimi-vl-technical-report-fig01.png]]
> [!tip] 【图文联合解读】图1为MathVision基准上的对比散点图（坐标轴标签与图例不可读）。可观察：深蓝星标位于左上最高位（推测Kimi-VL-Thinking-2506）、浅蓝星标次之（推测其轻量变体）；右上绿X标（推测QVQ-72B/Max-Preview）接近顶格；紫、灰虚线分别连接多枚圆点并随序列递增上行（推测Gemma-3与Qwen2.5-VL系列规模档位）；蓝、红圆点位于底部。该图论证关键结论：仅以2.8B激活参数的MoE轻量LLM，即在多模态数学推理上达到乃至逼近数十B级长思考VLM的水平，凸显稀疏激活架构的高效性。作为论文开篇"性能名片"，它先于Table 1的训练流程概览，构成"方法链路→实验结果"的入口性证据，强化"小参数、强推理"的整体叙事。
*caption: Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, including short-thinking VLMs (e.g. Gemma-3 series, Qwen2.5-VL series) and lon… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.2 (p.2)
![[assets/crops/kimi-vl-technical-report-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图2以八组柱状图横向对比Kimi-VL-A3B与Qwen2.5-VL-7B、DeepSeek-VL2、GPT-4o、GPT-4o-mini、Llama-3.2-11B-Instruct、Gemma-3-12B-IT在五大类共八项基准上的得分。具体表现：通用（MMMU 57、MMBench 83.1）、OCR（InfoVQA 83.2）、多图（BLINK 57.3）、长视频（LongVideoBench 64.5、Video-MME 67.8）、长文档（MMLongBench-Doc 35.1）、代理（ScreenSpot-Pro 34.5、OSWorld 8.2）上，Kimi-VL-A3B均处于领先或并列第一位置，尤其在长文档（MMLongBench-Doc领先GPT-4o约21分）和代理任务（OSWorld领先GPT-4o约3分）上优势显著。

**核心论证**：仅激活约3B参数的Kimi-VL-A3B以小模型之身全面超越或追平7B–12B开源模型，并在多数任务上反超参数量远大于自身的GPT-4o，验证了"高效MoE视觉语言架构"在保持推理成本优势的同时实现跨任务泛化的关键技术结论。

**论文作用**：该图是实验章节的"总览门面"，先于Table 3给出全局性能印象，用以支撑后续详细表格与消融研究，是论文展示方法竞争力与实用价值的核心证据。
*caption: Highlights of Kimi-VL performance for a wide range of benchmarks like, general benchmarks (MMMU, MMBench), OCR (InfoVQA), multi-image (BLINK), long vi… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.3 (p.3)
![[assets/crops/kimi-vl-technical-report-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图示 Kimi-VL 三模块架构：**MoonViT**（原生分辨率视觉编码器）→ **MLP Projector** → **MoE Language Decoder**（堆叠 N 层，每层含 Attention + MoE FFN，Router 将 token 分派至 Non-shared Experts 与 Shared Experts）。

MoonViT 直接处理多尺度异构输入，规避 resize 失真：小图 50×20px、长视频 480×270px 多帧、细粒度图 1113×672px（1008px 内含 ROI）、OCR 条带 58px 高、UI 截图 800×1731px。

**论证要点**：原生分辨率编码保留细节以适配异构视觉任务；MoE 兼顾容量与推理效率。**论文作用**：作为开篇架构总图，奠定后续多基准（OCR InfoVQA、Agent OSWorld/屏幕截图、长视频 LongVideoBench 等）泛化性能的方法学根基。
*caption: The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT that allows native- resolution images, an MLP projector, and a Mixture… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.4 (p.4)
![[assets/crops/kimi-vl-technical-report-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示 Kimi-VL 三阶段预训练流水线：(1) 文本预训练 5.2T tokens（纯文本）；(2) ViT 训练 2.0T→0.1T tokens，采用 CoCa-loss + 微型语言解码器对齐 LLM；(3) 联合预训练 1.4T tokens，多模态数据渐进式升至 40%，并以"resumes LR scheduler"衔接文本阶段。

论文借此论证两点关键结论：①预训练总计消耗 4.4T tokens（不含纯文本阶段）；②所有更新语言模型的阶段均为联合训练，以防止灾难性遗忘、保留文本能力。

该图为方法总纲，奠定后续 SFT/RLHF 的基础——先打牢文本与视觉编码器各自基础，再以渐进比例融合多模态，是 Kimi-VL 在不牺牲语言能力前提下获得视觉理解能力的关键架构设计。
*caption: The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-only pre-training of its language model. To preserve text abilities, all … ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.5 (p.6)
![[assets/crops/kimi-vl-technical-report-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心结构：** 图示 Kimi-VL 后训练三阶段流水线。阶段一为**联合监督微调（SFT）**，在文本+多模态数据上依次进行 **1 Epoch@32K + 1 Epoch@128K**，上下文每阶段扩展 4 倍；阶段二为**长思维链 SFT（Long-CoT SFT）**，覆盖 Planning、Evaluation 等推理数据；阶段三为 **RL**（强化学习）以增强长思考能力。

**2) 关键技术结论：** 通过"短上下文联合训练 → 上下文长度逐级倍增 → 长 CoT 微调 → RL 强化"的递进式设计，以约 80 万样本量实现长上下文与长链思考能力的协同激活。

**3) 在论文中的作用：** 位于预训练之后、推理评测之前，是 Kimi-VL 区别于普通 VLM 的核心增强链路，承担将基础模型升级为具备长思考能力的 Thinking 变体的关键职能。
*caption: The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages of joint SFT in 32K and 128K context, and further long-CoT SFT and RL s… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.6 (p.8)
![[assets/crops/kimi-vl-technical-report-fig06.png]]
> [!tip] 【图文联合解读】**图6图文联合解读**

图6展示Kimi-VL-Thinking对爱因斯坦手稿图像的逐步推理过程（部分文字片段呈现）。模型沿多条线索链式分析：①**视觉感知**——手写潦草但连贯，源自单一作者；②**数学内容**——含g(引力)、M(质量)、T(时间)等变量、偏导求和与张量记法，符合场论风格；③**语言线索**——出现德语"Gleichung"(方程)、"Gln"，指向德语母语者；④**知识匹配**——公式与广义相对论场方程吻合，最终判定作者为Albert Einstein。该图作为定性案例，定证Thinking模式具备**多模态链式推理**与**跨域(历史人物+科学理论)联合推断**能力，是论文论证"思考型VLM"区别于普通VLM的核心可视化证据之一。
*caption: Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to perform historical and scientific inference by analyzing handwritten … ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.7 (p.12)
![[assets/crops/kimi-vl-technical-report-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图为多子图问答演示，至少包含两个完整案例：①城市场景匹配——模型比对四张子图（含圆顶/天文台建筑），通过密度、布局、圆顶结构特征判定第4张与第1张同地；②地标识别——基于可伸缩屋顶与CN塔背景，定位为多伦多Rogers Centre体育场；③游戏场景识别——依据霓虹灯、全息屏、赛博朋克美学判断为《赛博朋克2077》Night City中的酒吧/俱乐部。每个案例以"图像+Response"配对呈现。

**2) 关键技术结论：** 论证Kimi-VL具备三类视觉推理能力——空间/结构匹配（layout grounding）、文化地标识别（cultural landmark grounding）、风格化场景理解（stylistic cue grounding），即视觉内容可被锚定于空间、语境与文化知识。

**3) 在论文中的作用：** 作为定性案例（qualitative showcase），与论文核心主张"激活视觉推理"互文，支撑其在M3原生训练阶段联合注入的OCR、图像描述、视觉定位与世界知识等多模态能力，无需CoT即可完成复杂跨模态推断。
*caption: Kimi-VL exhibits strong visual reasoning capabilities by grounding visual content in spatial, contextual, and cultural knowledge. It accurately identi… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.8 (p.13)
![[assets/crops/kimi-vl-technical-report-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 该图展示一道圆形几何题的求解示例。题目给定⊙O中AB为直径、D、C在圆上、∠D=62°，求∠ACO（选项A.26°/B.28°/C.30°/D.32°）。模型分三步作答：①由直径得∠ACB=90°；②圆心角∠AOC=2×62°=124°；③等腰△AOC中2x+124°=180°，解得x=28°，选B。

**2) 关键结论：** 证明Kimi-VL能将视觉几何信息转化为符号链，综合调用圆周角定理、直径性质、等腰三角形等多条定理，完成多步精准推理。

**3) 论文作用：** 作为定性案例，与MathVision等定量基准互补，展示模型在视觉-符号跨模态数学推理上的实际能力，强化其技术报告的方法学说服力。
*caption: Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric inference by solving a circle geometry problem step by step. The model… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.9 (p.14)
![[assets/crops/kimi-vl-technical-report-fig09.png]]
> [!tip] 【图文联合解读】**图像部分内容编码异常，仅能识别三栏布局与分隔结构，需结合原文解读。**

图9以三栏并列结构展示Kimi-VL的OCR能力：①左栏为结构化金融表格（含"Total Current Assets""Property, Plant"等多行条目，括号内数值列），被解析为markdown表格；②中栏为复杂数学公式（含分式、求和、上下标 `∑h^N O^N`、`Q^x ≤ N` 等符号），下方标注"Rendered formula"，体现LaTeX转换；③右栏为手写中文段落，转录为带语境的文字。

原文借此论证：模型在**结构化表格→markdown、符号公式→LaTeX、手写文本→转录**三类异构模态上均具备鲁棒的多模态文本抽取与解释能力。

在论文链路中，该图作为Figure 9位于实验可视化部分（p.14），与表格/榜单（定量）互补，以定性案例支撑前文OCR、ChartQA、DocVQA等基准结论，强化"Kimi-VL在真实异构文档场景中具备工程级可用性"的叙事。
*caption: Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across varied content types, including structured financial tables, complex ma… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.10 (p.15)
![[assets/crops/kimi-vl-technical-report-fig10.png]]
> [!tip] 【图文联合解读】**图像无法辨认，仅依据原文解读。**

图片渲染为乱码字符，仅可辨识出 Step 1–12 共 12 个步骤标签，原图应为 Chrome 浏览器中开启"Do Not Track"的截图序列（含思考、动作、API 调用三栏），实际内容未能呈现。

按 caption 与正文论述：

1) **核心对象**：Kimi-VL 在 GUI 智能体场景下的多步骤推理案例——12 步内依次完成 Chrome 隐私设置导航、菜单定位、开关切换等操作，每步均含 Thought / Action / API Call 三段结构；

2) **关键结论**：证明模型具备逐帧视觉解读 + UI 元素识别 + 顺序动作执行的链式推理与工具调用能力，可胜任复杂 GUI 任务；

3) **论文作用**：作为定性 case study，定向支撑"Kimi-VL 视觉–语言–动作闭环"的能力论述，是其与同类模型在 GUI agent 维度对比的直观佐证。
*caption: Kimi-VL is capable of following multi-step reasoning processes to complete complex GUI tasks. In this example, it successfully enables the “Do Not Tra… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.11 (p.16)
![[assets/crops/kimi-vl-technical-report-fig11.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图11展示Kimi-VL长视频场景分割能力：左侧输入为一段约3分37秒的短片（密集帧采样网格），右侧模型输出12个场景切片（时间跨度00:00:00–00:03:37），每个均给出精确起止时间戳与细粒度描述，涵盖人物动作（如转经轮老者、滑雪跳跃）、镜头运动（特写/航拍/水下）、情绪氛围（神秘、敬畏）及贯穿主题（精神性、冒险、人与自然）。

**论证结论：** 模型具备分钟级长时序视频理解、精准时间定位与连贯叙事生成能力，能在多场景切换中保持语义一致性，并自动提炼主题线索。

**整体作用：** 作为定性示例，与其他视频能力图共同支撑Kimi-VL在长视频任务上的实用性与细粒度描述质量，强化论文"长上下文多模态理解"的核心主张。
*caption: Video scene splitting. Kimi-VL processes a long-form video by segmenting it into coherent scenes and providing detailed start/end timestamps along wit… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.12 (p.17)
![[assets/crops/kimi-vl-technical-report-fig12.png]]
> [!tip] 【图文联合解读】该图展示Kimi-VL对一段约36分钟（00:00–35:55）教学视频的10帧采样理解任务。指令要求在"授人以鱼/渔"谚语基础上找出作者的"进一步要求"。模型通过逐帧追踪幻灯片文本语义演进：从"give a man a fish"→"teach a man to fish"→"teach him the taste of fish and make him hungry"，精准定位第三层递进，并在响应中给出完整阐释（强调激励与持续学习的重要性）。

此例用以定性论证模型对**长视频帧序列的概念演化抽取与跨时序推理**能力。在论文评测链路中，它作为"长时序+概念理解"的典型案例，与定量基准互补，支撑 Kimi-VL 在视频理解维度的能力声明，体现其从稀疏关键帧中聚合高层语义的技术优势。
*caption: Catching and understanding key details from an hour-long video course. Kimi-VL demonstrates its ability to comprehend and interpret instructional vide… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### KIMI-VL TECHNICAL REPORT — Fig.13 (p.16)
![[assets/crops/kimi-vl-technical-report-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与数据**：图13展示Kimi-VL-Thinking在MMMU基准上，推理时最大思考token长度（1k/2k/4k/8k/16k）对测试准确率的影响。数据点为49.2%→52.4%→56.2%→60.1%→61.7%，呈单调递增；图中左侧另可见MathVista在8k时71.3%等数据点，共涉及三个benchmark。

2) **关键结论**：原文论证"在三个16k上限的benchmark上，增加推理时的最大思考token长度均能持续提升测试准确率"，即test-time scaling law在视觉推理模型上同样成立，思考预算越大收益越高，但16k→8k的边际增益（+1.6pp）小于4k→8k（+3.9pp），呈饱和趋势。

3) **论文作用**：该图作为"思考长度即性能杠杆"的实证支撑，强化了Kimi-VL-Thinking的核心卖点——通过扩展推理时的思考预算实现性能提升，与文本版Kimi k1.5的test-time compute scaling主张一脉相承，奠定视觉MLLM的scaling新范式。
*caption: Specifically, increasing the max thinking token length at inference time consistently improves test-time accuracy across all three 16… ｜ 论文 [[kimi-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### DeepSeekMath: Pushing the Limits of Mathematical Reasoning i — Fig.1 (p.1)
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 1）：**

该图以时间为横轴，展示开源模型在MATH竞赛级基准Top1准确率的变化：LLaMA1-65B约10.6%（2023初）→WizardMath约21%（2023末），并用三条水平参考线标示闭源前沿——GPT-4早期版约42%、GPT-4 API约50%、Gemini-Ultra约54%。虚线趋势显示开源进步明显但仍落后闭源达2–3倍差距。

作为论文**开篇动机图**，此图直观论证"开源模型在数学推理上仍未逼近前沿"这一核心问题，为后续提出DeepSeekMath填补这一能力缺口、突破开源数学推理上限的立题与实验链路提供必要的前提铺垫。
*caption: Top1 accuracy of open-source models on the competition-level MATH benchmark… ｜ 论文 [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] ｜ arxiv 见 MD 元信息*

### DeepSeekMath: Pushing the Limits of Mathematical Reasoning i — Fig.2 (p.5)
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig02.png]]
> [!tip] 【图文联合解读】**图1解读：**

图示DeepSeekMath从Common Crawl采集数学网页的迭代流水线：①以种子数学语料训练fastText分类器；②从全网召回数学网页构建Math Corpus；③挖掘高密度数学域名；④新域名回灌至第②步形成闭环迭代。

**图2原文论点：**
通过"种子→分类器→域名发现"自举闭环，无需昂贵人工标注即可自动化、规模化地从无标注网页扩展高质量数学数据，验证数据规模与质量可兼得。

**图3链路作用：**
该流程产出120B token数学预训练语料，是DeepSeekMath-Base 7B训练的数据基石，并与下游GRPO强化学习协同，最终奠定模型数学推理的领先性能。
*caption: An iterative pipeline that collects mathematical web pages from Common Crawl.… ｜ 论文 [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] ｜ arxiv 见 MD 元信息*

### DeepSeekMath: Pushing the Limits of Mathematical Reasoning i — Fig.3 (p.7)
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig03.png]]
> [!tip] 【图文联合解读】**图3 联合解读**

**核心对象与结构**：四个子图横向对比DeepSeek-LLM 1.3B在四种语料（MathPile蓝、OpenWebMath橙、Proof-Pile-2绿、DeepSeekMath Corpus红）上、训练0–150B tokens期间，在GSM8K、MATH、CMATH、BBH四项基准的准确率曲线。

**关键数据**：
- GSM8K：DeepSeekMath Corpus攀升至约22–23%，其余仅12–14%，MathPile几乎停滞于2%。
- MATH：DeepSeekMath Corpus达~13–14%，OpenWebMath/Proof-Pile-2约10%，MathPile保持~3%。
- CMATH：DeepSeekMath Corpus达~44–45%，OpenWebMath/Proof-Pile-2仅~18%，MathPile趋近于0。
- BBH：差距收窄，DeepSeekMath Corpus约34%，最低约25%。

**论证结论**：DeepSeekMath Corpus在数学推理任务上显著优于现有开源数学语料库，且随训练量持续提升，验证其数据质量与构建方法的有效性。

**在论文中的作用**：该实验链路中"语料对比"环节的关键可视化证据，为后续基于该语料训练DeepSeekMath 7B并取得SOTA提供数据层面的合法性支撑。
*caption: Benchmark curves of DeepSeek-LLM 1.3B trained on different mathematical corpora.… ｜ 论文 [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] ｜ arxiv 见 MD 元信息*

### DeepSeekMath: Pushing the Limits of Mathematical Reasoning i — Fig.4 (p.13)
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig04.png]]
> [!tip] 【图文联合解读】图分上下两部分对比PPO与GRPO流程。PPO由策略模型对问题q采样单输出o，经Reference（KL）、Reward（r）、Value（v）三模型后用GAE计算优势A；GRPO对同一q采样G个输出{o₁…o_G}，仅用Reference与Reward，通过Group Computation由组内奖励{r₁…r_G}直接生成{A₁…A_G}，彻底取消Value模型。颜色上黄色为训练模型、蓝色为冻结模型。该图论证GRPO以组分数统计量替代Value基线，可显著节省显存与算力，构成论文RLHF训练阶段的方法基础。
*caption: Demonstration of PPO and our GRPO. GRPO foregoes the value model, instead… ｜ 论文 [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] ｜ arxiv 见 MD 元信息*

### DeepSeekMath: Pushing the Limits of Mathematical Reasoning i — Fig.5 (p.19)
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图为 DeepSeekMath-Instruct 1.3B 模型在 GSM8K 基准上、采用不同方法继续训练 0–9000 步的准确率曲线对比。可见至少四条曲线：

- **蓝色方法**表现最佳，从约 56.5% 上升至 ~65–66%；
- **橙色方法**次之，最终达 ~64%；
- **Online RFT（绿色）**波动较大，由 ~56.5% 提升至 ~62–63%；
- **RFT（紫色）**几乎停滞，长期徘徊在 59–60%。

**关键结论**：原文据此论证——在 SFT 模型基础上，单纯的离线 RFT 已接近性能天花板（甚至饱和），而引入在线探索/采样的方法（如 Online RFT 及更强变体）能持续突破上限，验证了"在线强化"对数学推理进一步提升的必要性。

**论文链路作用**：该图作为消融/方法对比证据，支撑论文主张的 GRPO 等在线策略优于 RFT 的核心论点，衔接其整体方法（监督 → RFT → Online RFT/GRPO）的演进叙事。
*caption: Performance of the DeepSeekMath-Instruct 1.3B model, which was further trained… ｜ 论文 [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] ｜ arxiv 见 MD 元信息*

### DeepSeekMath: Pushing the Limits of Mathematical Reasoning i — Fig.6 (p.20)
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示 DeepSeekMath-Instruct 7B 在 GSM8K 与 MATH 上三轮迭代 RL 的训练曲线（步数 0–5300）。GSM8K 准确率从 Iteration-0 起点 ~83% 提升至 ~86%，Iteration-1 起步 ~87%、峰值 ~88%，Iteration-2 起步 ~87%、峰值 ~89%；MATH 从 ~46.8% 经 ~49% 升至 ~50.5%，三轮峰值均逼近 52%。

核心结论：**每轮迭代起点显著高于上一轮末值，证明 RL 切实带来能力提升；但迭代间增益边际递减**（GSM8K 仅 +1–1.5pp，MATH 仅 +1.5–2pp）。

方法链作用：该图为"为何需要 GRPO+迭代 SFT 融合"提供经验依据——纯迭代 RL 收益趋缓、且训练步数逐轮增加（3000→5000+），论文据此提出用新 SFT 数据重置 RL 起点，突破 RL 自身天花板。
*caption: Performance of iterative reinforcement learning with DeepSeekMath-Instruct 7B on… ｜ 论文 [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] ｜ arxiv 见 MD 元信息*

### DeepSeekMath: Pushing the Limits of Mathematical Reasoning i — Fig.7 (p.21)
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示 GSM8K 上 Maj@K 与 Pass@K 随候选数 K（1→64，温度 0.7）的变化：Maj@K-Instruct（紫，81.5%→89.6%）与 Maj@K-RL（橙，88%→91%）在 K≥8 后趋于平台；Pass@K-Instruct（蓝，88.2%→97.4%）与 Pass@K-RL（绿，81.5%→99.2%）随 K 陡升。原文据此论证：**RL 显著提升 Maj@K**（橙高于紫约 1.4 个百分点），但对 Pass@K 无明显增益，说明 RL 改善的是多数投票的可靠性，而非单条解的正确率或解空间覆盖。该图是论文揭示"RL 主要强化自一致投票稳定性"这一核心增益模式的关键证据。
*caption: The Maj@K and Pass@K of SFT and RL DeepSeekMath 7B on GSM8K and MATH… ｜ 论文 [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] ｜ arxiv 见 MD 元信息*

### High-Dimensional Continuous Control Using Generalized Advant — Fig.1 (p.8)
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig01.png]]
> [!tip] 【图文联合解读】该图上部展示3D仿生机器人：球形躯干+4条腿肢（每肢2自由度，共8维连续动作空间），置于棋盘格地面/蓝天的MuJoCo仿真环境；下部以5帧序列呈现习得步态，证明策略可驱动多肢协调移动。

原文在6.2.1 ARCHITECTURE节以该图建立具身仿真基准，论证GAE能处理躯干姿态与肢体关节耦合的高维连续控制，相对TD(λ)在多步信用分配上具优势。

该图位于方法/实验链路起点，为后续TRPO+GAE训练提供高维任务载体，支撑策略学习的定量对比。
*caption: 6.2.1 ARCHITECTURE… ｜ 论文 [[high-dimensional-continuous-control-using-generalized-advantage-estimation]] ｜ arxiv 见 MD 元信息*

### High-Dimensional Continuous Control Using Generalized Advant — Fig.2 (p.10)
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig02.png]]
> [!tip] 【图文联合解读】左图：cart-pole在γ=0.99下10种λ设置（0/0.36/0.68/…/1.0及No VF）的cost-迭代曲线，λ∈[0.92,0.98]约30次迭代降至≈-10，No VF与λ=0仅≈-2。右图：5×7的γ-λ网格热图，20次迭代后白色（高reward）集中于γ、λ均取中间值处。论证：GAE通过λ实现偏差-方差权衡，中间值在收敛速度与最终性能上最优。该图为GAE超参选择提供经验依据，并支撑后续三维双足/四足运动等复杂任务的方法推广。
*caption: Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement … ｜ 论文 [[high-dimensional-continuous-control-using-generalized-advantage-estimation]] ｜ arxiv 见 MD 元信息*

### High-Dimensional Continuous Control Using Generalized Advant — Fig.3 (p.10)
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig03.png]]
> [!tip] 【图文联合解读】**图3图文联合解读**

**1) 核心对象与数据：** 左图为3D双足机器人9次平均的学习曲线，横轴为策略迭代次数0–500，纵轴代价由0降至约−2.5，涵盖10组(γ, λ)配置；其中红色曲线(γ=0.995, λ=0.98)最低降至≈−2.2。右图为3D四足机器人5次平均曲线，横轴0–1000，代价0至−12，三条γ=0.995曲线对比：λ=0.96(黄)≈−11.5最优，λ=1(橙)≈−10.5次之，无value函数(绿)≈−8.5最差。

**2) 关键结论：** 在双足上(γ, λ)敏感、最优组合落在偏倚-方差折中区；四足上明确显示GAE引入value函数(λ<1)显著优于无baseline与λ=1的vanilla策略梯度。

**3) 在论文中的作用：** 在高维连续运动控制任务上实证GAE的有效性与超参鲁棒性区间，支撑其作为TRPO优势估计核心组件的实证依据。
*caption: Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algo- rithm. Right: learning curves for 3D quadrupedal locomotion, a… ｜ 论文 [[high-dimensional-continuous-control-using-generalized-advantage-estimation]] ｜ arxiv 见 MD 元信息*

### High-Dimensional Continuous Control Using Generalized Advant — Fig.4 (p.11)
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig04.png]]
> [!tip] 【图文联合解读】**图4（c）可见内容解读**（图中仅含站立片段，(a)(b)学习曲线未呈现，故结合原文caption综合解读）：

**1) 核心对象与结构**
图4(c)以编号1–6的6个连续姿态，呈现3D模拟人形体由仰卧（1）→侧卧（2）→蜷缩撑地（3）→双手触地推起（4）→近直立并抬臂平衡（5）→完全站立举手（6）的运动序列；每帧姿态由MuJoCo渲染的多刚体棒人组成，对应二维状态特征。

**2) 论证的关键技术结论**
该序列与(a)四足行走、(b)3D站立学习曲线互相印证，证明GAE在高维连续控制任务（含63维髋膝踝力矩+17维刚体姿态）中可稳定收敛，并习得具备"翻身—撑起—平衡—直立"语义结构的有意义行为，而非局部最优。

**3) 在论文链路中的作用**
作为GAE从低维基准推广至类人/多足高维运动控制的核心实验证据，支撑第7节"Discussion"中关于GAE可扩展至复杂3D locomotion与manipulation类任务的结论。
*caption: (a) Learning curve from quadrupedal walking, (b) learning curve for 3D standing up, (c) clips from 3D standing up. 7 DISCUSSION… ｜ 论文 [[high-dimensional-continuous-control-using-generalized-advantage-estimation]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.1 (p.1)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig01.png]]
> [!tip] 【图文联合解读】图1为首页主结果条形图，对比 Kimi-K2-Instruct 与 DeepSeek-V3-0324、Qwen3-235B-A22B、GPT-4.1、Claude 4 Opus/Sonnet、Gemini 2.5 Flash（非思考模式）在四类基准的得分（%）：
- SWE-bench Verified：65.8 vs Opus 72.5、GPT-4.1 54.6
- SWE-bench Multilingual：47.3 vs Sonnet 51.0、GPT-4.1 31.5
- Agentic & Competitive Coding：66.1 vs Opus 67.6、DeepSeek 48.8
- AceBench(en)工具使用：76.5 vs GPT-4.1 80.1、Opus 75.6

原文借此论证：Kimi-K2 在 SWE 与智能体编码达开源 SOTA、逼近闭源旗舰，工具使用接近 GPT-4.1。作为摘要级证据，支撑"开源领先、可比肩闭源旗舰"这一中心性能主张。
*caption: Kimi K2 main results.2 1https://huggingface.co/moonshotai/Kimi-K2-Instruct 2All models evaluated above are non-thinking models. For SWE-bench Multilin… ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.2 (p.4)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig02.png]]
> [!tip] 【图文联合解读】**图2解读：**

**核心数据**：左图（Vanilla + Muon）显示注意力 logits 在约16k步内单调上升至1200+且无收敛迹象；右图（Kimi K2 + MuonClip, τ=100）在约220k步训练中，logits 迅速触及封顶值100，持续约30%训练步后衰减至稳定的30–40区间。

**关键结论**：对比证明 Muon 优化器单独使用会引发注意力 logits 爆炸（>1000），导致数值不稳定甚至训练发散；而 QK-Clip 通过按头裁剪 W_q 权重，将 logits 硬性限制在 τ=100 以内，使其在训练前期触发后自然回落，验证了 QK-Clip 对注意力 logit 增长的有效调控。

**方法链路作用**：作为论文核心创新 MuonClip 的直接经验证据，衔接"问题暴露（logits爆炸）→ 机制设计（QK-Clip）→ 规模化可行性证明（K2全量训练）"，为后续百万亿token级训练稳定性背书。
*caption: Left: During a mid-scale training run, attention logits rapidly exceed 1000, which could lead to potential numerical instabilities and even training d… ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.3 (p.5)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig03.png]]
> [!tip] 【图文联合解读】**图3 图文联合解读**

图3展示Kimi K2逐步训练loss曲线（未经平滑/抽样）：横轴约0–15.5T tokens，纵轴loss从≈2.0单调下降至≈1.35；密集蓝色震荡带约1.35–1.65，全程**未见异常尖峰或发散**。

①**核心对象**：K2预训练全过程的step级loss轨迹，跨度约15.5万亿token。
②**关键论证**：作者借此证明，相比K1.5新引入的合成数据/重述策略与训练栈协同良好，预训练在超大规模下保持单调收敛且无中断尖峰，间接佐证数据管线与基础设施的稳健性。
③**链路作用**：作为"预训练无异常"的实证前提，为后续MuonClip优化器设计、后训练SFT/RL及智能体能力评测奠定可信基线。
*caption: Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we om… ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.4 (p.5)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象与结构**：Figure 4 展示自动回归式分块改写（auto-regressive chunk-wise rephrasing）流水线。输入长文本经切分后，顶部蓝色高亮框保留滑动上下文窗口，每块文本经紫色"rephrase-prompt"改写，生成绿色"partial output"（SDUWLDO RXWSXW），三块按自回归顺序（DXWR UHJUHVVLYH）依次处理，最终拼接为完整改写段落。

**关键技术结论**：通过分块+上下文保留机制，突破单次改写长度上限，确保长文本改写时块间语义连贯；结合 fidelity verification 做语义对齐检验，作为训练前的质量把关。

**论文链路作用**：该流水线是 Kimi-K2 训练数据构造（特别是 Long Context 改写语料）的核心预处理环节，为后续 MuonClip 优化与多任务训练提供高质量、改写后的长上下文监督信号。
*caption: • Fidelity verification: To ensure consistency between original and rewritten content, we perform fidelity checks that compare the semantic alignment … ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.5 (p.7)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与数据**：左图为 Validation Loss vs Training FLOPs（对数轴），含绿、紫、蓝、橙多条 MoE 训练曲线，每条对应"激活专家=8、共享专家=1、总专家数不同"的稀疏度配置，曲线呈典型 lr schedule 的"陡降–回升"末端形态；右图为 Loss vs Training Tokens，4 条虚线对应 1.2/2.2/4.5/9.0×10²⁰ FLOPs 四档算力，比较"层数=头数"方形模型与"头数翻倍"圆形对照。

2) **关键技术结论**：固定激活专家数下，增大总专家数（即提高稀疏度）能持续压低验证损失，呈现稳定的稀疏度 scaling law——同等算力时模型越稀疏越优。

3) **论文链路作用**：为 Kimi K2 选用高稀疏 MoE 架构（众多专家、少量激活）提供 scaling 实证支撑，奠定"以稀疏换性能"的设计前提，并与右图共同验证最优训练资源分配策略。
*caption: Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared … ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.6 (p.7)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig06.png]]
> [!tip] 【图文联合解读】**左图**：横轴为Training FLOPs（10²⁰–10²¹，对数刻度），纵轴为Validation Loss（≈1.3–1.8）。展示蓝、紫、绿、橙四组不同规模模型的loss下降轨迹——实线为含cosine学习率重启的原始训练loss（可见周期性尖峰回弹），虚线为对应的拟合下降趋势。

**右图**：横轴为Training Tokens（≈10¹¹），按1.2 / 2.2 / 4.5 / 9.0 ×10²⁰ FLOPs四档绘出U形loss曲线。方块标记代表"头数=层数"基线，圆点标记为"头数翻倍"对照组——在同一计算量档位下，圆点曲线稳定低于方块，降幅约0.5%–1.2%（最优loss由≈1.75降至≈1.38）。

**技术结论**：在Kimi K2的规模区间内，适度增加注意力头数（而非单纯加深层数）可稳定带来validation loss收益，且对所有四个计算档位一致生效。

**论文作用**：属于架构消融scaling实验，为Kimi K2选择"层数较浅、头数较多"的配置提供实证依据，支撑后续Muon优化器与MLA等结构设计决策。
*caption: Scaling curves for models with number of atten- tion heads equals to number of layers and their counter- parts with doubled attention heads. Doubling … ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.7 (p.8)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图7上半部用横向时序条展示两个PP阶段内的算子重叠：计算侧（MLP/Attn/WGrad）与通信侧（EP-D 蓝、EP-C 黄、PP 绿）及卸载侧（Onload/Load 黄）嵌套并行。下半部呈典型流水线阶梯（微批次1–8错列），绿色边框标注的"8"块凸显PP通信气泡被EP dispatch/combine及其他算子"填满"，空闲时间大幅压缩。

论文借此论证核心结论：在不同PP阶段（warm-up、稳态、cool-down）中，计算、集合通信（EP收发、PP点对点）与CPU offload可被深度流水重叠，从而隐藏通信与I/O开销，是Kimi K2实现高MFU万卡训练的关键调度基础。
*caption: Computation, communication and offloading overlapped in different PP phases.… ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.8 (p.10)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig08.png]]
> [!tip] 【图文联合解读】**(a) 核心结构**：图分两部分。**(a) 工具规格合成**——MCP 真实工具与由 Domains→Applications 衍生的合成工具共同汇入 Tool Repository，进而生成 Agents 与带 rubric 的 Tasks；**(b) 轨迹生成与过滤**——Task 驱动 User Agent 与 Agent 交互，Agent 通过 observation/call 调用 Tool Simulator 产出 trajectories，再由 Judge Agent 依据 Rubrics 筛选为 Filtered Data。

**论证结论**：真实+合成双源工具库配合"多智能体—rubric 过滤"管道，可规模化产出高质量工具调用训练轨迹。

**整体作用**：作为 Kimi K2 agentic 能力 SFT 训练的数据合成基石，为下游 tool-use 评测与对齐提供可验证的监督数据。
*caption: Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (… ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.9 (p.10)
![[assets/crops/kimi-k2-open-agentic-intelligence-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a)为真实MCP工具的t-SNE二维投影，数百点按源类别着色(黄/绿/紫/蓝/橙/红等)，可见同色点呈局部弱聚类(如右侧黄色簇、左上绿色簇)，整体仍混合；图(b)区域在图中未渲染出散点，仅保留标题文字。

作者借此论证：真实工具自然聚类反映来源多样性，合成工具按预定义域系统铺开以补足盲区，二者融合使训练所用工具空间在功能维度上既多样又完备。

该图位于工具库构建环节，是面向后续SFT训练的数据分布证据——证明真实+合成双源策略能为工具调用训练提供均衡且覆盖充分的工具集合，而非偏倚于单一来源。
*caption: t-SNE visualizations of tool embeddings. (a) Real-world MCP tools exhibit natural clustering based on their original source categories. (b) Synthetic … ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.10 (p.14)
![[assets/kimi-k2-open-agentic-intelligence-p14.png]]
> [!tip] **Architecture / Components / Data Flow**

Figure 10 illustrates a three-tier parameter-update pipeline:

1. **Training Engine (top layer)** – holds model weights in DRAM; each worker contributes its local parameter shard.
2. **Distributed Checkpoint Engine (middle layer)** – co-located workers that pull a local parameter copy from the training engine and then broadcast the *full* parameter set across all checkpoint workers, regardless of inference-side sharding.
3. **Inference Engine (bottom layer)** – uses a different sharding scheme, pulling only the parameter shard it needs from the checkpoint engine.

For the 1T Kimi K2 model, updates are streamed parameter-by-parameter in a pipelined fashion to minimize memory footprint.

**Key Technical Takeaway**

By broadcasting the full parameter set cluster-wide rather than using a network-file-system re-shard, the design fully decouples the training and inference engines, simplifies maintenance, and completes a full K2 parameter update in **<30 seconds** — negligible versus a single RL iteration.

**Caption (verbatim)**

> Figure 10: Parameter update utilizing a checkpoint engine
*caption: Parameter update utilizing a checkpoint engine… ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.11 (p.29)
![[assets/kimi-k2-open-agentic-intelligence-p29.png]]
> [!tip] **Main Figure Description**

The figure content itself is not visibly rendered on this page — only its caption ("Figure 11: Chinese in-house benchmark evaluation.") appears above the surrounding paragraph, with the actual chart area blank. Based on the in-text reference, Figure 11 presents a model comparison chart evaluating Kimi-K2-Instruct against baseline LLMs (ChatGPT-4o-latest, Claude Sonnet 4, DeepSeek-V3-0324) on Chinese in-house held-out benchmarks, likely displayed as win-rate / loss-rate / tie-rate bars or radar-style comparisons per model pair.

**Key Technical Takeaway (≤120 words):**
Kimi-K2-Instruct demonstrates strong, balanced Chinese-language open-ended capability, posting high win-rates of ~65.4% vs ChatGPT-4o-latest, ~64.6% vs Claude Sonnet 4, and ~59.6% vs DeepSeek-V3-0324 on access-restricted in-house benchmarks. Critically, its loss-rate stays uniformly low (~17%) across all comparisons, indicating it rarely loses outright and rarely ties — it consistently wins or comes close. This combination of high win-rate and uniformly low loss-rate (verified on a held-out, contamination-controlled set) provides robust evidence that the Chinese performance is genuine generalization, not benchmark overfitting.

**Caption (verbatim):**
"Figure 11: Chinese in-house benchmark evaluation."
*caption: Chinese in-house benchmark evaluation. rate, i.e. 98.9. On FaithJudge’s RAG tasks the hallucination rate is 7.4 %, likewise present as 92.6 for table … ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.12 (p.30)
![[assets/kimi-k2-open-agentic-intelligence-p30.png]]
> [!tip] **Figure Description & Technical Takeaway**

The referenced figure (Figure 12) compares training loss curves between two small-scale MoE models — one using vanilla Muon and the other using MuonClip with an aggressive threshold (τ = 30). The architecture under test is a 0.5B-activated / 3B-total-parameter MoE (presumably the Kimi K2 / MuonScaffold stack), where QK-Clip caps the per-head maximum attention logit S_max at 100. The plot shows two nearly-overlapping loss trajectories over training steps.

**Key takeaway:** Even an aggressive QK-Clip threshold (τ = 30) produces no visible degradation in training loss, confirming that bounding attention logits via MuonClip is a safe intervention — it constrains logit explosion without harming convergence dynamics.

**Verbatim Caption:**

> Figure 12: Applying QK-Clip to Muon in a small-scale setting with an aggressive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logits.
*caption: Applying QK-Clip to Muon in a small-scale setting with an aggresive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and… ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### KIMI K2: OPEN AGENTIC INTELLIGENCE — Fig.13 (p.32)
![[assets/kimi-k2-open-agentic-intelligence-p32.png]]
> [!tip] ## Main Figure Description

The figure presents **Figure 13: pipeline for RL weight update** in three variants (a, b, c), depicting how trained weights from RL engines are resharded into inference engines across GPUs.

**Architecture/Components:**
- Each GPU holds three equal-size device buffers: one **H2D buffer** (Host-to-Device loading of offloaded parameters) and two **IPC buffers** (GPU-to-GPU broadcast, shared with inference engines via memory mapping).
- **Subplot (a)** – Theoretical 3-stage pipeline: (1) async H2D copy of weight shard → (2) copy shard to IPC buffer + broadcast to all devices → (3) inference engines reload from second IPC buffer. All three stages overlap in a pipeline.
- **Subplot (b)** – PCIe-bounded 3-stage: stages collapse into sequential execution because concurrent H2D + broadcast saturate the shared PCIe fabric on H800 clusters.
- **Subplot (c)** – Fixed 2-stage pipeline adopted in practice: (1) synchronous, all-device H2D transfer → (2) broadcast and reload happen in parallel.

**Data flow:** Host memory (offloaded params) → H2D buffer → IPC buffer A → broadcast over NVLink/PCIe → IPC buffer B → inference engine reload.

**Key Technical Takeaway:** Overlapping H2D, Broadcast, and Reload operations yields high bandwidth for resharding weights from train to inference engines; at large scale the parameter set fits the H2D buffer in a single transfer, making the simpler 2-stage pipeline PCIe-friendly.

## Caption (verbatim)

**Figure 13:** pipeline for RL weight update
*caption: pipeline for RL weight update… ｜ 论文 [[kimi-k2-open-agentic-intelligence]] ｜ arxiv 见 MD 元信息*

### Search-R1: Training LLMs to Reason and Leverage Search Engin — Fig.1 (p.4)
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读**

**核心对象与结构：** Figure 1 横向并列展示 Search-R1 的两种 RL 训练范式。上半部分为 **PPO**：策略 LLM（Trained Model，黄色）在 rollout 阶段多轮调用 Search Engine（蓝色）；训练时由 Value 函数 v 与即时奖励 r 经 **GAE** 计算 Advantage A，并以 Frozen Reference Model（绿色）做 KL 锚定。下半部分为 **GRPO**：移除 Critic，对同一 query 采样 G 条 rollout（r₁…r_G），经 **Group Computation** 生成逐样本归一化的优势 A₁…A_G。两者共用同一带 search engine 的多轮 rollout 通路。

**关键论证结论：** Search-R1 验证了"LLM+搜索引擎"可在 PPO（有 critic）与 GRPO（无 critic）两种主流 RL 算法下统一训练，证明 search engine 接入与具体 RL 框架解耦，方法具有算法无关的通用性。

**论文整体作用：** 作为 Method 部分的总览图，统摄后续 PPO/GRPO 消融与主实验的实验链路，是读者理解 Search-R1 训练闭环的入口。
*caption: Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).… ｜ 论文 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Search-R1: Training LLMs to Reason and Leverage Search Engin — Fig.2 (p.9)
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig02.png]]
> [!tip] 【图文联合解读】1) 四子图横轴均为训练步Step。(a) 0-500步：PPO(蓝)缓升至~0.40；GRPO(橙)约200步即达~0.40，随后骤降归零。(b) 0-200步：Base由~0.05缓升至~0.35，Instruct由~0.25速升至~0.40，终值相近。(c) 响应长度(950-1100)呈"降-升-稳"三段轨迹，与奖励(~0.5)同向。(d) 有效搜索次数由~1.4升至~1.85，与奖励协同上升。

2) 论证：GRPO收敛快但存崩溃风险；PPO稳而慢；指令微调仅加速收敛、不抬上限；模型自发学得更频繁调用搜索，长度与奖励耦合演化。

3) 作用：为Search-R1的算法选型(GRPO)、基座选择(Instruct)及奖励塑造(长度+搜索激励)提供关键实证支撑。
*caption: (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable op… ｜ 论文 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Search-R1: Training LLMs to Reason and Leverage Search Engin — Fig.3 (p.17)
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(b)为Qwen-2.5-7b-base在约200步RL训练中的Train Reward曲线，对比"w. mask"（蓝）与"w.o. mask"（橙）。两者起点均约0.10–0.15；带掩码曲线约150步升至~0.45并稳定；不带掩码曲线整体滞后，且在近终点处出现剧烈塌陷（骤降至~0.10），训练不稳定。

**技术结论：** 检索到的外部token应被屏蔽、不参与损失计算；掩码策略可加速收敛并避免不相关检索内容干扰策略更新。

**方法作用：** 该实验验证了Search-R1训练链路中"retrieved-token-loss-masking"这一关键设计选择的必要性，为RL+检索的整体流程提供消融支撑。
*caption: Retrieved Token Loss Masking Study instruction-tuned models exhibit faster convergence and benefit from higher initial perfor- mance relative to their… ｜ 论文 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Search-R1: Training LLMs to Reason and Leverage Search Engin — Fig.4 (p.17)
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig04.png]]
> [!tip] 【图文联合解读】**核心对象与结构**：图(b)展示Qwen2.5-7b-base/instruct在PPO RL训练下的Train Reward曲线（Step 0–200，奖励区间0.15–0.50）。Base（蓝）初始奖励约0.18，约50步后开始抬升；Instruct（橙）初始约0.38，全程高位震荡；两者最终均收敛于~0.45。

**关键技术结论**：用以论证SEARCH-R1对底座模型鲁棒——指令微调版收敛更快、起点更优，但最终性能与基础版几乎一致，说明该RL训练范式不依赖特定的模型初始化。

**论文整体作用**：作为支撑性消融实验，与Table 4（检索token loss masking消融）并列，证明SEARCH-R1的关键设计选择在多种设置下均有效，强化方法可推广性的论证。
*caption: Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final … ｜ 论文 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Search-R1: Training LLMs to Reason and Leverage Search Engin — Fig.5 (p.18)
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图5展示了Search-R1在Qwen2.5-7b-base（500步，奖励0.1→0.55）与Qwen2.5-7b-it（约300步，奖励0.3→0.5）上PPO与GRPO的训练曲线对比。GRPO（橙）初期爬升更陡，约150步即接近收敛；PPO（蓝）爬升较缓但全程平稳；在7b-it图中GRPO约200步处出现明显下跌，印证其"后段不稳定"。

论文借此论证Search-R1框架对底层RL算法不敏感，PPO与GRPO最终奖励可比、均可作为可行基座，从而支撑其方法链路的算法兼容性结论，强化"RL+检索"范式的普适性主张。
*caption: Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability a… ｜ 论文 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Search-R1: Training LLMs to Reason and Leverage Search Engin — Fig.6 (p.19)
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig06.png]]
> [!tip] 【图文联合解读】该图展示SEARCH-R1在Qwen2.5-7b-base+PPO下，检索topk=1/3/5三条训练奖励曲线（step 0–500，纵轴0.1–0.55）：均从~0.1起步，~step 200前快速攀升，之后在0.45–0.55区间震荡收敛；topk=5于step 320附近出现明显下探，三者在收敛阶段高度交织。

原文借此论证：检索深度变化下训练动力学高度一致，证明SEARCH-R1对topk超参不敏感、训练稳定。

该图属消融实验，与Figure 5（不同LLM/RL组合）互补，为"检索增强RL训练具备鲁棒性"这一核心结论提供量化支撑。
*caption: The training dynamics of SEARCH-R1 with a different number of retrieved pas- sages. (LLM: Qwen2.5-7b-base, RL: PPO)… ｜ 论文 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Search-R1: Training LLMs to Reason and Leverage Search Engin — Fig.7 (p.19)
![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图7展示SEARCH-R1采用GRPO算法、基于Qwen2.5-7b-base模型时，不同组大小（group size=1/3/5）在约500步训练过程中奖励（reward）的动态变化曲线。横轴为训练步数（Step），纵轴为奖励值，绿色×标记（size=1）曲线明显位于上方，在0.4–0.6区间剧烈波动；蓝线（size=5）与橙线（size=3）则贴近底部、几乎重叠且波动微弱。

原文借此说明：组大小并非PPO收敛的主导因素——size=1反而获得最高奖励，而size=3与size=5训练信号极弱（提示GRPO在该设定下需更大群体方差才能形成有效优势），从而佐证检索深度（top-k）并非性能瓶颈这一关键结论。在全文实验链路中，该图与表7互为补充，共同构成"对超参不敏感、方法鲁棒"的论证支撑，强化了SEARCH-R1框架无需精细调参即可稳定训练的核心卖点。
*caption: We observe that a larger group size generally leads to faster convergence but may also increase the risk of collapse due to the inherent instability o… ｜ 论文 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.1 (p.1)
![[assets/crops/hyper-connections-fig01.png]]
> [!tip] 【图文联合解读】该图含4个子图，在500B tokens规模上对比基线 OLMoE-1B-7B（红）与加入超连接的 OLMoE-1B-7B-DHC×4（蓝）：(1) 训练损失（0.99 EMA平滑）DHC×4全程低于基线，终点差距0.027；(2) C4-en验证损失差距0.028，并标注 "×1.8" 收敛加速；(3) HellaSwag准确率 DHC×4 约71% 对比基线约69.5%；(4) ARC-Challenge DHC×4 约46% 对比基线约40%。

原文据此论证：DHC（Dynamic Hyper-Connections）显著提升训练收敛效率，并在500B tokens长程训练与下游基准上持续保持优势。作为Introduction开篇核心实验证据，为后续消融实验与机制分析提供量化锚点，奠定论文"超连接作为残差结构替代方案有效"的总体立论。
*caption: The performance of the baseline model OLMoE-1B-7B and the model with hyper- connections, OLMoE-1B-7B-DHC×4. (1) and (2) show the training loss (0.99 E… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.2 (p.2)
![[assets/crops/hyper-connections-fig02.png]]
> [!tip] 【图文联合解读】**图2（n=2）解读**

**结构呈现**：图示对比四种连接方案——(a) 残差连接（基线，单层输出加回h）；(b) HC全量版：h拆为h₁、h₂两个隐向量，以7个标量（α₀,₀、α₀,₁、α₁,₀、α₁,₁、α₂,₁、α₂,₂ 实现层↔隐向量深度路由，β₁、β₂ 控制隐向量至输出的残差缩放，并附带h₁↔h₂横向链路）实现纵深加权与宽度交换；(c) 仅保留α的垂直深度连接；(d) 仅保留β的横向宽度连接。

**技术结论**：HC把单一残差通路拓展为"深度整合+宽度交互"双通路；(c)(d)作为消融对照，证明纵、横向通路缺一不可。

**论文作用**：作为HC整体架构定义图与消融范式，为后续嵌入Transformer（图17）及各类视觉/语言实验提供结构基线。
*caption: Hyper-connections (HC) with an expansion rate of n = 2. (a) Residual connections. (b) Hyper-connections: β1, β2, α0,0, α0,1, α1,0, α1,1, α2,1, and α2,… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.3 (p.2)
![[assets/crops/hyper-connections-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**图表内容**：横轴为层索引 i（0~32），纵轴为相邻层输入的余弦相似度 cos(h₀ⁱ, h₀ⁱ⁺¹)。红线（Pre-Norm）从第 1 层约 0.2 迅速攀升至 0.85–0.95 区间，并在整个网络深度上保持稳定的高值；蓝线（Hyper-Connection）同样从低位上升，但中位数仅在 0.60–0.85 之间大幅振荡，且第 5–95 分位带更宽（约 0.35–0.90）。

2）**关键论证**：Pre-Norm 模型中相邻层输入高度相似（≈0.9），表明存在明显的表征坍缩/秩坍缩问题，深层难以获得新信息；而 Hyper-Connection 将相似度显著拉低并放大层间差异，证明其有效缓解了该瓶颈。

3）**论文作用**：作为方法动机图，Figure 3 在引入 Hyper-Connection 前定量揭示 Pre-Norm 的固有缺陷，为后续提出残差宽度扩展（多流残差映射）以恢复层间表征多样性提供实验依据，奠定整篇方法的立论基础。
*caption: Cosine similarity be- tween the input of the current and the previous layers for the OLMo-1B models (Groeneveld et al., 2024). The curve represents th… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.4 (p.5)
![[assets/crops/hyper-connections-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a)展示n=2的**顺序排列**超连接结构：单个输入经展开生成2条并行隐藏流（蓝色与橙色块），依次通过layer 1与layer 2；每层前通过"⊕"汇聚各流，层内由可学习矩阵H^l控制流间混合与残差路径。

**论证结论**：该图直观说明超连接（HC）通过可学习矩阵将传统单残差扩展为多流并行结构，并在顺序堆叠中保持每层的多流聚合能力，证明HC可作为ResNet残差连接的**直接泛化**框架。

**整体作用**：图4(a)(b)共同奠定HC的拓扑自由度——既支持常规顺序堆叠，也支持并行多分支，为后续实验（ResNet、ViT、LLM等任务）验证"多流残差优于单流"提供结构基础，是方法论层的核心可视化支撑。
*caption: Sequential and parallel arrangements of hyper-connections with n = 2.… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.5 (p.6)
![[assets/crops/hyper-connections-fig05.png]]
> [!tip] 【图文联合解读】**图5解读**

该图展示OLMo-1B基线与DHC在扩展率x1/x2/x4/x8下、100–500B tokens的训练损失曲线（共2子图，各5条曲线）。

**数据观察**：左图（含tanh）在500B处，DHCx1≈2.47最高，基线≈2.43居中，DHCx4/x8≈2.38最低；右图（去tanh）整体上移但曲线排序一致，DHCx4/x8 W/O tanh仍最优。

**关键结论**：①扩展率越大损失越低，DHC x≥2稳定优于基线，证明超连接结构有效；②tanh的引入进一步压低损失，验证其设计必要性。

**论文作用**：作为方法验证的核心实验，从消融角度同时支撑了"扩展率"与"tanh"两项关键设计选择。
*caption: Comparison of training loss curves for different expansion rate. The left subfigure includes models with dynamic hyper-connections (DHC) at various ex… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.6 (p.8)
![[assets/crops/hyper-connections-fig06.png]]
> [!tip] 【图文联合解读】图以100–500B训练token的OLMo‑7B（红）与DHC×4（蓝）作1×4对照：0.99 EMA训练损失约由2.45降至2.18，C4‑en由2.74降至2.47，DHC全程略低。HellaSwag最终约70%对69%，SciQ约92%对90%，蓝线更优，阴影表示波动范围。结果证明DHC×4在7B规模兼具优化与泛化优势；该图将消融及静态评测延伸至完整训练曲线，支撑动态超连接可扩展且有效的核心结论。
*caption: (1) and (2) Training loss (0.99 EMA smoothed) and C4-en validation loss for OLMo-7B and OLMo-7B-DHC×4 models. (3) and (4) Accuracy curves on hellaswag… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.7 (p.9)
![[assets/crops/hyper-connections-fig07.png]]
> [!tip] 【图文联合解读】核心：32×32下三角热力图，对比超连接与Post/Pre-Norm层间权重（色阶−1至+1），奇数层（注意力层）用绿色刻度标记。超连接矩阵呈稀疏非均匀分布，第10–11行附近出现一处标注为"PTB"（预训练偏置）的异常亮斑；Post-Norm表现为对角方向的平滑衰减；Pre-Norm则接近均匀强连接（近似恒等）。

结论：超连接学到了比固定残差更丰富、可学习的跨层路由结构，并保留了来自预训练的偏置特征，突破了Post/Pre-Norm的刚性模式。

作用：作为4.5节可视化分析的核心证据，解释表1中DHC×4在MMLU Var（39.7 vs 38.5）和HellaSwag（70.2 vs 69.5）上优于基线的性能来源。
*caption: Visualization of connection matrices for hyper-connections and various related baseline methods. The attention layers, which have odd ids, are marked … ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.8 (p.14)
![[assets/crops/hyper-connections-fig08.png]]
> [!tip] 【图文联合解读】图左为标准残差Transformer（h⁰→Attention⁺→FFN⁺→…→h^L单流跳连）；右为宽度n=2的Hyper-Connections：h⁰经Repeat得双流h⁰₁、h⁰₂，每层以α^l_{i,k}分配权重（2×3矩阵）将前层多流混合输入Attention/FFN，β^l_j门控缩放输出后再分裂为h^l₁、h^l₂。结论：超连接以可学习权重替代固定残差，将残差函数族从标量加法扩展为多流加权聚合，缓解层间信息瓶颈。作用：为论文核心架构创新提供与残差基线的直观对照，支撑后续消融与扩展性实验。
*caption: Comparison between transformers with hyper-connections and that with residual connec- tions. 14… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.9 (p.17)
![[assets/crops/hyper-connections-fig09.png]]
> [!tip] 【图文联合解读】图9由28张子图组成，对比 OLMoE-1B-7B（红）与 OLMoE-1B-7B-DHC×4（蓝）在约100B–500B tokens 训练区间的表现。上12张为训练loss及12个验证集（C4、Dolma六子集 books/cc/pes2o/reddit/stack/wiki、Ice、M2D2-s2orc、Pile、WikiText-103）的loss曲线，蓝色全程稳定低于红色约0.02–0.05；下16张为MMLU四类及平均、HellaSwag、SciQ、ARC-Challenge/Easy、PIQA、WinoGrande、OpenBookQA、BoolQ、COPA、CommonsenseQA、SocialIQA 的下游准确率，蓝色多数高于红色且差距随训练持续或扩大。

论证：DHC×4 在保持 MoE 稀疏激活宽度不变的前提下，同时降低预训练loss并提升下游任务准确率，支撑核心主张——可学习残差连接（DHC）作为静态跳连的可扩展替代优于基线，是论文方法有效性的关键横向验证证据。
*caption: Loss curves in V3 validation sets and accuracy curves on downstream tasks for OLMoE-1B7B and OLMoE-1B7B-DHC×4 models. 17… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.10 (p.18)
![[assets/crops/hyper-connections-fig10.png]]
> [!tip] 【图文联合解读】图含15子图：9个V3验证集loss曲线（c4 en、dolma六子集books/cc/pes2o/reddit/stack/wiki、ice、m2d2-s2orc、pile、wikitext103）与6个下游任务准确率（HellaSwag、SciQ、COPA、OpenbookQA、PIQA、WinoGrande、ARC-Easy），对比OLMo-7B基线与OLMo-7B-DHC×4在100B–500B token训练区间表现。

蓝色DHC×4在所有loss子图均稳定低于红色基线（如HellaSwag最终约70% vs 68%、SciQ约92% vs 90%、COPA约83% vs 80%），6个准确率均高于基线。论证DHC宽度扩展（×4）在7B规模上同时改善预训练loss与下游能力，是论文支撑"超连接可扩展优于残差基线"结论的核心实验链路。
*caption: Loss curves in V3 validation set and accuracy curves on downstream tasks for OLMo-7B and OLMo-7B-DHC×4 models. 18… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.11 (p.20)
![[assets/crops/hyper-connections-fig11.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 图示对象与数据：** 图中展示 ViT/16-Large（红线）与 ViT/16-Large-DHC×2（蓝线）在约 60000–95000 步区间的训练 loss 曲线，EMA(0.999) 平滑；纵轴为 loss，横轴为训练步数。蓝线全程位于红线之下，差距随步数推进而逐渐收敛。

**2) 论证的技术结论：** DHC×2 在多 epoch 训练中持续降低训练 loss，证明超连接带来的额外容量确有优化收益；但随同一数据集被反复遍历，HC 的增益递减，暗示存在对训练集的过拟合/记忆效应，容量扩展收益边际递减。

**3) 在论文链路中的作用：** 作为支撑实验，量化验证 HC 的容量增益随训练饱和的边界条件，为后续关于泛化、可扩展性与训练效率的讨论提供实证依据，也解释了在有限 epoch 设置下 DHC 优势更显著的现象。
*caption: Training loss curves of ViT/16-Large and ViT/16-Large-DHC×2, smoothed using an… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.12 (p.21)
![[assets/crops/hyper-connections-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读（图12）**

图12展示ViT-Base/16-DHC×2末层DHC模块权重在两幅不同输入图上的分布直方图：左侧绿色为"capitulum"，右侧橙色为"779:school bus"，共7个参数（β₁≈1.10–1.20、β₂≈1.10–1.20、α₁,₀≈−0.65–−0.35、α₁,₁≈1.1–1.3、α₁,₂≈0.1–0.3、α₂,₀≈2.0–2.4、α₂,₁≈−0.2–0.2）。

关键发现：同一网络面对不同样本时权重分布差异极大——"school bus"在β₁≈1.20、α₁,₁≈0.9、α₁,₂≈−0.1、α₂,₁≈−0.2等极值处高度集中（频次≈50），而"capitulum"分布相对分散。这是论文**"超连接具有输入自适应动态路由"**这一核心命题的直观证据，用以佐证其用可学习动态连接替代静态残差路径的方法论动机。
*caption: Distribution of weights of last DHC in ViT-Base/16-DHC×2 model. F MORE VISUALIZATION AND ANALYSIS… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.13 (p.22)
![[assets/crops/hyper-connections-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象：** 图中两组（a DHC / b SHC）各展示5个33×33上三角展开连接矩阵 **C⁽⁰⁾~C⁽⁴⁾**（隐状态 h_i^j 中 j=0…32），色阶[−1, 1]，奇数层（注意力层）顶部标绿刻度。

**2) 关键结论：** 两模型学到的连接模式高度一致——主对角线呈深红（≈+1，自连接最强），向上呈近似指数衰减的正连接；C⁽⁰⁾扩散最广，注意力层位置出现竖向蓝条（负抑制）。这说明习得的连接结构以"位置/层依赖"为主，而非输入相关，从而支持 SHC 可作为 DHC 的简化替代。

**3) 链路作用：** 为"去除动态门控、保留静态超连接亦不损性能"提供可视化依据，支撑论文方法简化与推理加速的核心论点。
*caption: Visualization of unfolded connection matrix.… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.14 (p.23)
![[assets/crops/hyper-connections-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象**：三幅33×33展开式连接矩阵热力图（值域[-1,1]，红正蓝负），分别对应 OLMo-1B-DHC×1/×2/×4。

**结构对比**：
- (a) ×1：连接高度集中在主对角带，中段约第18列被标注"wasted"，呈现明显的稀疏带状结构，代表性容量未被充分利用；
- (b) ×2：连接沿对角扩展，副对角与跨行条目增多，带状结构弱化；
- (c) ×4：连接近乎弥散至全矩阵，出现显著蓝色（负值）条目，呈现正负交错的多路径路由。

**技术结论**：随宽度从1→4，连接从"窄带冗余"演化为"近全连接"；×1存在显著浪费，而更宽连接可承载更丰富、含正负权重的多路径信息流。

**论文作用**：作为经验证据，支撑"加宽超连接可释放表征容量"的核心论点，与其它实验共同构成 DHC 设计的消融/可解释性链路。
*caption: Comparison of unfolded connection matrices for OLMo-1B-DHC×1, OLMo-1B-DHC×2 and OLMo-1B-DHC×4 model.… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.15 (p.31)
![[assets/crops/hyper-connections-fig15.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象与数据：** 图L展示1B参数规模下5条训练Loss曲线（EMA平滑，衰减率0.99），横轴为token数（0–500B），纵轴Loss范围2.4–2.9。曲线包括基线OLMo-1B（红）、ResiDual（蓝）、Altup×2（绿）、本文DHC×2（紫）、DHC×2 W/O tanh（橙）。起点均约2.88–2.89，训练至500B时收敛到不同终值：Altup最高约2.42，紫/橙两条DHC最低约2.38–2.39，基线与ResiDual居中约2.40；红色基线在约100B、250B处出现明显Loss尖峰。

**关键技术结论：** 在1B规模下，本文DHC×2（含/不含tanh）训练Loss始终低于基线OLMo与ResiDual，全程优于Altup；tanh激活对DHC性能影响极小，验证了所提方法相对相关工作的稳定优势。

**论文链路作用：** 作为附录L的扩展实验，1B规模与正文更小规模的实验形成多尺度互证，强化"DHC在大模型预训练中同样有效且优于ResiDual、Altup"的核心主张，支撑正文方法对比的结论。
*caption: Training loss curves of related works, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99. 31… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.16 (p.32)
![[assets/crops/hyper-connections-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读**

1) **核心对象与数据**：图中呈现 5 条训练 loss 曲线，横轴为训练 token 量（0–1000B），纵轴 loss 范围约 2.35–2.60，曲线经 EMA（decay=0.99）平滑。对比对象为基线 OLMo-1B（红）与四个 DHC（带 tanh）变体：x1（蓝）、x2（绿）、x4（紫）、x8（橙）。两条红色竖线标记约 250B 与 350B 处 loss 尖峰事件。训练终止时 loss 由高到低约为：DHCx1≈2.36 > 基线≈2.35 > DHCx2/x4≈2.34 > DHCx8≈2.33（最低）。

2) **关键结论**：DHC 扩展比（×N）越大，训练 loss 越低，证明超连接中**残差流宽度扩展**对模型拟合能力有正向增益；但 x1 因通道数不足略逊于基线，验证了**最小扩展阈值**的存在。该图与 Fig.17（无 tanh）配对，论证 tanh 门控对收敛稳定性的必要性。

3) **实验链路作用**：此图属于超连接消融实验（与 Table 6、Fig.13–15 呼应），为论文核心主张——DHC 通过隐式增加模型深度/宽度且不增显式参数即提升性能——提供了长程训练（1000B tokens 量级）的可复现 loss 证据，构成从组件有效性到端到端训练有效性的关键证据链。
*caption: Training loss curves of DHC with tanh over 500 billion tokens, smoothed using… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.17 (p.32)
![[assets/crops/hyper-connections-fig17.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 图示内容**：5条EMA(衰减率0.99)平滑的训练loss曲线，横轴0–1000B tokens，纵轴约2.30–2.60；对比OLMo-1B基线（红）与DHC×1/×2/×4/×8无tanh版本（蓝/绿/紫/橙）。紫色DHC×4末值最低≈2.33，橙×8、绿×2次之，红色基线在1000B处≈2.35；蓝色×1全程高于基线表现最差。

**2) 关键技术结论**：去掉tanh约束后，DHC×2/×4/×8仍稳定低于基线且随expansion rate提升loss进一步降低，证明tanh并非DHC发挥作用的必要前提；但×1反劣于基线，表明需足够宽度扩展方能取得增益。

**3) 论文作用**：属DHC消融实验关键证据，验证无tanh简化设计仍保持有效性，为方法选型与训练效率提供支撑。
*caption: Training loss curves of DHC without tanh over 500 billion tokens, smoothed using… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.18 (p.33)
![[assets/crops/hyper-connections-fig18.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示OLMo-1B四种架构在10B–500B tokens上的训练损失曲线（EMA衰减0.99平滑），含四组：红线基线OLMo-1B、蓝线OLMo-1B-PTB、绿线DHC×4去tanh、紫线DHC×4。500B tokens处收敛损失依次约为2.41、2.43、2.39、2.38——DHC×4最低，PTB反高于基线，tanh带来小幅额外增益。

**论证结论：**
1. 所提Dynamic Hyper-Connections（DHC）在训练收敛性上显著优于串行基线与并行Transformer块（PTB）；
2. PTB虽加速并行却损失更差，证明DHC兼顾效率与质量；
3. tanh门控组件不可或缺，去除即性能回退。

**论文链路作用：** 该图是核心消融/对比证据，回应"并行化是否更优"的潜在质疑，支撑Hyper-Connections作为优于串行、PTB两类baseline的架构选择，为后续下游任务表现提供训练动力学依据。
*caption: Training loss curves comparied with parallel transformer blocks (PTB), smoothed using… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### BERTopic: Neural topic modeling with a class-based TF-IDF pr — Fig.1 (p.7)
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-fig01.png]]
> [!tip] 【图文联合解读】1) 两子图对比9个主题模型在Trump数据集上的墙钟耗时（秒），横轴为词汇量≈2500–18000（由文档数1000→43000调控）。左图含CTM-MPNET（紫），随词量陡升至~1500s，其余8模型均<100s；右图剔除CTM后y轴缩至0–100s：NMF（棕）最快~33s，LDA~45s，Top2Vec-MPNET（灰）与BERTopic-MPNET（绿）最高达~95–100s。

2) 论证BERTopic（非MPNET变体）效率可比LDA/NMF，并显著优于CTM等神经主题模型；CTM极端耗时会掩盖其他模型差异。

3) 为BERTopic的类TF-IDF流程提供可扩展性证据，支撑其"质量+效率"双重卖点，奠定后文主题质量比较的可行性前提。
*caption: Computation time (wall time) in seconds of each topic model on the Trump dataset. Increasing sizes of vocabularies were regulated through selection of… ｜ 论文 [[bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure]] ｜ arxiv 见 MD 元信息*

### Dual-Head Reasoning Distillation: Improving Classifier Accur — Fig.1 (p.2)
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig01.png]]
> [!tip] 【图文联合解读】**【图示内容】** 图以两张雷达图分别展示 Llama-3.2-3B+BoolQ 与 Qwen-3-4B+BoolQ 两个主干在 SuperGLUE 八项任务（CB/COPA/MultiRC/RTE/WiC/WSC/BoolQ/Avg）上 Teacher（CoT Zero-shot，紫点线）、Baseline（pooled classifier，蓝虚线）与 DHRD（红实线）的得分。DHRD 几乎完全包络 Baseline，在 CB（≈89 vs 78）、COPA（≈79 vs 75）、RTE（≈92 vs 91）等低资源推理任务上提升最显著，Avg 也略优，整体逼近 Teacher 曲线。

**【技术结论】** 原文据此论证：DHRD 仅在训练阶段引入 CoT 推理，跨主干稳健提升分类头精度；增益源于"输入–理由–标签"三元组对齐，而非通用 LM 正则化。

**【整体作用】** 作为开篇概览图，定量支撑"训练时推理可替代测试时推理"的核心主张，为后续 Table 1 与消融实验铺垫。
*caption: SuperGLUE per-task scores for four backbones. DHRD (train-time reasoning) consistently beats the pooled-classifier baseline and rivals teacher model G… ｜ 论文 [[dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning]] ｜ arxiv 见 MD 元信息*

### Dual-Head Reasoning Distillation: Improving Classifier Accur — Fig.2 (p.3)
![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示共享解码器上的双头架构：①**分类头**对蓝色输入token（L_cls个，D维嵌入ℝ^(L_cls×D)）池化输出K类logits；②**推理头**通过LM Head对全序列（蓝色分类token+橙色教师推理token，共L_cls+L_rat个，ℝ^((L_cls+L_rat)×D)）施加因果LM损失。原文据此论证：推理头仅在训练时借助教师思维链做辅助蒸馏，推理阶段完全弃用，使分类器零开销吸收推理知识。该图是论文DHRD方法的**核心架构图**，支撑"训练时推理、推理时仅分类"的整体链路设计，是其相对传统CoT蒸馏的关键创新点。
*caption: Dual-head fine-tuning on a shared decoder. The classification head pools hidden states over the input span (blue) to produce K class logits. The train… ｜ 论文 [[dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning]] ｜ arxiv 见 MD 元信息*

### Dynamic Large Concept Models: Latent Reasoning in an Adaptiv — Fig.1 (p.4)
![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a)展示DLCM总览结构：输入token经编码器（蓝色圆角模块）后，通过Q查询机制映射至4个概念槽C₁–C₄（内含a、ba、bn等字符符号），再经后续"MH"模块继续处理。图(b)展示边界检测与池化：token序列(s、B、b、a、o、b、bn)按阈值K动态切分边界，池化为C₁–C₄四个概念。

原文借此论证：DLCM以"概念"（concept）替代传统token作为推理粒度，通过边界检测自适应分块、Q查询检索形成潜变量序列，实现语义空间中的动态推理。该图作为全文方法基石，为Table 1预训练数据统计与下游对比实验提供架构锚点。
*caption: 3.1… ｜ 论文 [[dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space]] ｜ arxiv 见 MD 元信息*

### Dynamic Large Concept Models: Latent Reasoning in an Adaptiv — Fig.9 (p.7)
![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p07.png]]
> [!tip] # Description

**Note:** This page contains no rendered figure—it is a text-heavy section (Sections 3.6, 4, 4.1–4.3) that *references* "Figure 2" (attention mask illustration) and "Figure 9" (speedup plot, not shown). The figure-equivalent content here is the conceptual data flow described in text:

## Architecture / Components / Data Flow (as described)

1. **Inputs:** Tokens t₁…t_L (queries) and concept features c₁…c_M (keys/values), with variable-length mapping where each concept c_j spans a segment of tokens.
2. **Problem:** Ragged attention mask—direct Flex Attention is inefficient due to dynamic mask generation and irregular memory access.
3. **Solution — Concept Replication:** Replicate each concept feature c_j to fill its segment length, producing K̃ = repeat(c, segment_lengths) and Ṽ = repeat(c, segment_lengths). This aligns KV length with query length L.
4. **Compute:** Run FlashAttention's **VarLen** kernel (causal-style self-attention) on the replicated KV, since K/V are locally constant within each segment.
5. **Training loss:** L = L_CE + L_a (cross-entropy + load-balancing, Eq. 15), with RMSNorm on Q and K (Eq. 16).

## Key Technical Takeaway
Concept replication converts irregular concept-token cross-attention into a uniform-length VarLen self-attention problem, yielding **1.26×–1.73× speedup** over Flex Attention by trading a small memory cost for highly optimized CUDA kernels.

## Caption (verbatim from the page)

No figure caption is present on this page. The page's opening line reads:

> "**3.6 Training Objective** — The total loss combines next-token prediction with adaptive compression:
> 
> L = L_CE + L_a       (15)
> 
> where L_CE is cross-entropy on output tokens and L_a is the load-balancing loss."

The only in-line figure references are: *"Figure 2"* (ragged-boundary attention mask) and *"Figure 9"* (plotted speedup T_FA = T_8 ).
*caption: 4.3… ｜ 论文 [[dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.1 (p.3)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig01.png]]
> [!tip] 【图文联合解读】该图展示3种RLHF算法（PPO/Safe-RLHF/ReMax）的三阶段数据流：①Generation（Actor Gen，ReMax含2个）；②Preparation（Ref/RM/Critic/Cost模型的Forward）；③Training（Actor Training，PPO与Safe-RLHF另有Critic Training，Safe-RLHF还引入L_ptx损失与Actor Fwd）。各算法模型组合与拓扑各异——PPO需4模型，Safe-RLHF额外引入Cost模型，ReMax仅3模型且无critic。

**论证结论**：HybridFlow以统一的Stage抽象即可灵活承载不同模型数量与执行顺序，验证其作为通用RLHF框架的表达力与可扩展性。

**论文作用**：作为方法论开篇的"能力示例"，证明单一系统可统一支持多样RLHF流程，为后续灵活的Actor/Colocation调度与高效分布式实现奠定设计动机。
*caption: Dataflow graph of 3 RLHF algorithms [19, 43, 55].… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.2 (p.3)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(b)展示HybridFlow混合编程模型：顶层单控制器协调Actor、Critic、Reward、Reference四类模型；每个模型内部采用多控制器实现（图中以`gen(prompts)`、`comp_values(res)`、`comp_reward(res)`三段伪代码为例，共享`all_gather_weights()`同步与`model()`调用），灰色节点表示当前未激活。

原文借此论证两个关键技术结论：**灵活**——解耦数据与计算依赖、无缝集成任意LLM系统；**高效**——阶段转换零冗余（避免权重重复广播）、支持不同模型放置策略。

在论文整体链路中，该图是"混合控制器"设计的核心证据，与(a)纯多控制器范式形成对照，支撑后续吞吐量、显存占用与分布式扩展性实验的设计假设，是方法论章节的奠基性技术图。
*caption: Programming model used in RLHF systems. (a)… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.3 (p.4)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图左侧展示数据流图𝒟，包含Gen、Ref、RM、Value及Actor/Critic Training六个节点；中间为Placement方案，将四类模型分别映射至3台机器的6块GPU：Actor→机器A(GPU0-1)、Critic→机器B(GPU2-3)、Ref与RM共置→机器C(GPU4-5)；右侧Execution Pattern展示时序：Gen与Value分别在A、B上并行执行，Ref与RM在C上串行执行。

该图论证的核心结论是：HybridFlow通过解耦**模型放置**与**计算调度**，使各模型可独立并行于不同设备（如Gen与Value跨机并发），同时允许无依赖的子模型（如Ref、RM）共置以节省显存和资源，从而在3机6卡上灵活组织RLHF多阶段流水线。

此图在论文中起承上启下作用：它是3D并行的具体实例，用以说明所提抽象如何将RLHF复杂依赖关系转化为高效可执行的分布式调度方案，支撑后续吞吐量与可扩展性的实验论证。
*caption: Dataflow execution given a model placement plan.… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.4 (p.6)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图自顶向下分5层：①用户输入层（RLHF数据流图、模型/设备配置）；②ParallelWorker层，包含Transfer Protocol、3D-HybridEngine、训练/生成双引擎；③Auto Mapping层（模型放置+设备分配）；④Resource Pool层；⑤底层Physical Devices。

原文借此论证：通过层次化API将RLHF数据流描述与底层分布式执行解耦——上层用数据流图灵活表达算法逻辑，Auto Mapping自动完成模型-设备映射，3D-HybridEngine在统一显存下交错训练与生成，从而避免传统RLHF框架在显存/控制流层面的低效。

该图是整篇论文方法总纲，统领§4-§6各模块定位，并在实验部分支撑其端到端吞吐与显存利用率优势。
*caption: Architecture of HybridFlow. 3D-HybridEngine and Auto-Mapping algorithm. The hybrid programming model includes a set of hierarchical APIs to enable fle… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.5 (p.6)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a)展示`ActorWorker`继承`3DParallelWorker`，通过`ResourcePool(n_gpus_per_machine × n_machines)`分配GPU，按DP/TP/PP三维配置初始化模型；图(b)展示单控制器调度Actor(p,t,d=1,2,3，3个DP组)与Critic(p,t,d=2,1,2，2个DP组)间的5步异步数据reshard（①调用 ②返回future ③收集 ④分发 ⑤传输）。该图论证：分层API支持异构并行配置模型间的灵活数据重分片，是HybridFlow单控制器多Worker范式实现RLHF灵活训练的核心机制。
*caption: An illustration of hierarchical APIs. (a) Model with 3D parallel configuration, resource allocation, and 3DParallelWorker initialization. (b) Asynchro… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.6 (p.7)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图6展示一份**单一Python控制脚本**，按"生成响应→准备经验→更新actor/critic"三阶段编排，涵盖PPO/ReMax/Safe-RLHF三种RLHF算法；其中**蓝色虚框**标注ReMax特有行（`do_sample=False`、蓝叉标记`critic.compute_values`在ReMax中可省），**红色虚框**标注Safe-RLHF特有行（`cost.compute_cost`与`pretrain_loss`）。

原文借此论证**HybridFlow在不改算法代码的前提下，仅增删若干行即可切换不同RLHF算法**，体现其编程模型的灵活性。该图作为方法部分的关键示例，与第3节"单控制器抽象+分布式执行解耦"的设计形成呼应，为后文性能与易用性实验提供代码级证据。
*caption: Implementation of PPO [55], ReMax [43], and Safe- RLHF [19]. Users can adapt to different RLHF algorithms by simply adding or deleting a few lines of … ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.7 (p.8)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig07.png]]
> [!tip] 【图文联合解读】**图7解读：3D-HybridEngine工作流**

**核心结构**：展示单次RLHF迭代中4块GPU的完整流程，分为5步：①All Gather模型权重→②加载P1-P4提示词→③生成R1-R4响应并跨TP组AllGather→④将权重重新分片切回训练模式→⑤训练。训练采用1-2-2（p-t-d）并行，生成采用1-1-2-2（pg-tg-dg-d）并行，含2个Micro-DP组、TP组（红虚线）。

**技术结论**：通过权重resharding与并行组重配置，实现同一套4 GPU在生成（低显存、需长序列）与训练（高吞吐）两种模式间零冗余切换，避免传统方案中生成与训练资源割裂的问题。

**论文作用**：作为HybridEngine的核心证据图，支撑"灵活3D并行+零冗余权重转换"这一关键设计，证明RLHF训练在有限GPU资源下仍可高效完成生成—训练循环。
*caption: 3D-HybridEngine workflow in one RLHF iteration. 4 GPUs are used for actor training and generation. 1-2-2 (𝑝-𝑡-𝑑) parallel groups are used in training … ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.8 (p.8)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图8展示RLHF中actor训练→生成阶段的**模型权重重分片**机制，硬件为2机×4卡（G1–G8）。训练时单机内4卡构成TP组、跨机为DP组，每卡持有模型权重分片（橙）与冗余训练权重（灰）。

**(a) HybridFlow-V**：沿用相同TP/DP分组，生成阶段需在TP组内All-Gather完整权重再丢弃未用分片，冗余通信开销大。

**(b) HybridFlow**：采用**Micro-DP组**重新分组，缩小All-Gather范围，每份权重仅在更少卡间共享（如G1+G3互传），显著降低跨阶段通信与显存冗余。

**论证结论**：由于RLHF三阶段（训练/生成/推理）所需并行模式各异，权重分布必然重分配；通过差异化分组设计，HybridFlow可大幅压缩resharding成本。

**论文作用**：该图是3DHybridEngine**自动并行映射与权重重分片**优化的核心可视化证据，直接支撑其对RLHF端到端效率的提升主张。
*caption: Model weights resharding. 2 machines each with 4 GPUs are used for actor training and generation. model parameters updated in iteration 𝑖(step 1○in Fi… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.9 (p.11)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图9以四个子图(a–d)对比7B/13B/34B/70B模型在8–128 GPU上的PPO吞吐量(tokens/s)，四种系统（NeMo-Aligner、DS-Chat、OpenRLHF、HybridFlow）同列对照。绿色HybridFlow条形在各规模下均最高：7B/128 GPU达约3.7×10⁴ tok/s，70B/128 GPU达约0.8×10⁴ tok/s；加速比随模型增大而扩大（7B: 1.68–8.63×，70B: 5.17–17.98×，34B峰值达20.57×）。

论文借此定量论证：HybridFlow通过灵活组合3D混合并行与RLHF阶段解耦编排，在端到端训练吞吐上系统性优于现有框架。该图是全文"高效RLHF"主张的核心实验支撑，证明其架构优势随模型与集群规模同步放大。
*caption: PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines. 8 16 32 64 128 # of GPUs 0 1 2 3… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.10 (p.11)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
> [!tip] ## Main Figure Description

**Architecture/Components**: The figure consists of three rows of grouped bar charts (Figures 9, 10, 11), each containing four subfigures corresponding to Llama model sizes: 7B, 13B, 34B, and 70B. Each subfigure plots **throughput (tokens/s)** on the y-axis against the **number of GPUs** (8/16/32/64/128, varying by model size) on the x-axis. Four systems are compared via colored bars: NeMo-Aligner (blue), DS-Chat (orange), OpenRLHF (red), and HybridFlow (green).

**Data Flow**: The rows correspond to three RLHF algorithms — PPO (top), ReMax (middle), and Safe-RLHF (bottom) — illustrating end-to-end RLHF training throughput scaling.

**Key Technical Takeaway**: HybridFlow consistently and substantially outperforms all baselines across every model size and algorithm, achieving **1.5×–19.8× speedups**, with the largest gains at 70B scale where competing systems fail to scale efficiently.

## Verbatim Captions

**Figure 9.** PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines.

**Figure 10.** ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines

**Figure 11.** Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines
*caption: ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines 8 16 32 64 128 # of GPUs 0 1 2 3… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.12 (p.12)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig12.png]]
> [!tip] 【图文联合解读】## 图文联合解读

**1) 核心对象与数据**：图(a)为13B模型下四种放置策略（Colocate蓝、Split橙、Standalone红、HybridFlow绿）在16/24/32/64/96/128 GPU下的吞吐量（tokens/s，单位1e4）。小规模时Colocate≈HybridFlow≈0.7–1.0e4，Standalone仅0.4–0.7e4；128 GPU时四者收敛至约2.6e4。

**2) 关键技术结论**：HybridFlow在不同GPU规模下吞吐均≥Standalone，尤其在16–64 GPU区间显著领先（最大提升约30–40%），且在小规模时与Colocate持平；说明其灵活映射并不以吞吐为代价，突破了"非Colocate则慢"的固有代价。

**3) 在论文中的作用**：作为可扩展性实验的核心证据，证明HybridFlow的placement解耦设计兼具灵活性与高效性，为"统一多策略RLHF训练"主张提供关键性能背书。
*caption: Throughput of HybridFlow under different placements 32 64 96 128 # of GPUs… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.13 (p.12)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象与数据**：图13展示13B actor/ref + 70B critic/reward配置下，Colocate、Split、Standalone、HybridFlow四种放置策略在32/64/96/128块GPU上的吞吐量（tokens/s，量级1e4）。32 GPU时HybridFlow约5500，与Colocate持平但远高于Split(~2000)与Standalone(~2500)；64 GPU时HybridFlow升至约8500，居首；96–128 GPU时四种策略差距收窄至约9000–12000，HybridFlow仍领先约10%。

**关键结论**：异构模型规模下，固定放置策略（Colocate/Split/Standalone）顾此失彼，HybridFlow的灵活放置在中小规模GPU集群上提升最显著（最高近2×），验证其自适应布局优势。

**论文作用**：作为placement消融实验，与图12（67B actor场景）共同支撑方法章节关于"flexible 3D hybrid engine"可扩展性的主张。
*caption: Placement comparison under 13B actor and reference policy & 70B critic and reward model.… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.14 (p.13)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读（图14）：**

图14以双子图形式，在7B(T_g=2)与13B(T_g=4)两种配置下，对比四种框架在不同GPU规模下的"actor训练↔生成"模式切换耗时。

- **7B子图**：OpenRLHF从8卡约4s线性增至128卡约11s；DS-Chat约3-5s；HybridFlow-V约3-4s；HybridFlow始终稳定在2.5-3.5s（最低）。
- **13B子图**：差距进一步放大——OpenRLHF从10s升至17s，DS-Chat从5s升至12s，而HybridFlow几乎保持在3-4s，几乎不随GPU数增长。

**论证结论**：HybridFlow通过将训练与生成统一在同一调度器内（而非控制器分离式架构），将切换开销压到最低且具备良好扩展性。这正是其端到端RLHF训练吞吐量优于同类框架的关键工程支撑。
*caption: Transition time between actor training and generation.… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.15 (p.13)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig15.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示了 **7B 与 13B actor 模型在 16 GPU 上**于四种生成并行配置（T_g/D_g = 8/1、4/2、2/4、1/8）下的时间分解，包含 **generation time（蓝色）** 与 **transition time（橙色）** 两部分。量化来看：7B 生成时间随 T_g 减小从约 85s 降至 30s 左右；13B 则在 T_g=8/D_g=1 与 T_g=1/D_g=8 时均出现约 220s 的高值，呈现非单调 U 形。transition time 占比相对较小（7B 约 3–5s，13B 约 5–10s），但不可忽略。

原文借此论证：HybridFlow 通过解耦训练/生成资源并采用统一调度，将 actor 模型的 **reshard 过渡时间平均减少 55.2%（11.7s）**，凸显其在 RLHF 流水线中显著降低模式切换开销的关键优势。该图在实验链路中服务于"RLHF 训练—生成频繁交替场景下的端到端效率"这一核心主张，为 HybridFlow 的灵活并行设计提供了直接量化支撑。
*caption: Time breakdown on different generation parallel sizes of the actor model on 16 GPUs. various model scales, which is the time to reshard model weights … ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### HybridFlow: A Flexible and Efficient RLHF Framework — Fig.16 (p.13)
![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以对数纵轴柱状图展示8组（模型规模, GPU数）配置下的设备映射算法耗时：(7B,8)≈10s、(7B,16)≈30s、(13B,24)≈65s、(13B,32)≈110s、(34B,48)≈220s、(34B,64)≈370s、(70B,96)≈800s、(70B,128)≈1400s。

原文借此论证：当模型与GPU同步放大时，Auto Device Mapping的求解时间呈近似指数增长，但在最大规模70B/128 GPU下仍控制在约25分钟以内，处于工程可接受范围，证明该算法在千亿级RLHF训练中具备可扩展性，避免了映射本身成为系统瓶颈，从而支撑HybridFlow整体"灵活高效"的实验结论。
*caption: Runtime of device mapping algorithm. The model size and # of GPUs are simultaneously scaled.… ｜ 论文 [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.1 (p.1)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig01.png]]
> [!tip] 【图文联合解读】图示ALE三件套（ROCK沙盒+iFlow智能体+ROLL训练）通过ROME实现"任务→动作→执行→反馈→学习"闭环。Terminal-Bench 2.0上ROME(30B-A3B)24.72分、SWE-bench Verified 57.40分，均超同体量Qwen3(13.48/46.33)；训练曲线准确率由41.60%升至89.83%（相对增益+113.16%）。此为开篇门面图，确立"ROME闭环RL训练范式"核心叙事，证明30B-A3B经iFlow闭环训练即可逼近480B大模型水平(26.97/65.20)。
*caption: Overview of the Agentic Learning Ecosystem (ALE) and ROME Performance. 1[cs.AI] 12 Mar 2026… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.2 (p.4)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig02.png]]
> [!tip] 【图文联合解读】图(b)展示Agentic RL训练流水线两阶段闭环：Rollout阶段由Agentic LLM向环境输出Action（Tokens），回收Observation（State）；积累的Trajectory Data送入Training阶段完成Weight Update，再经Weight Synchronization回传LLM，形成自循环。图(a)展示ALE生态（含RK Sandbox、CLI、Agent Framework、LLM、Proxy Service、Response Queue、Execution Engine等模块），为流水线提供可执行环境与工程支撑。原文据此论证：智能体RL的核心挑战已从单纯的数据规模与质量，转向训练基础设施、可执行环境与评估协议的协同设计——ALE即作为该一体化技术栈，催化社区协作。
*caption: The overview of agentic RL ecosystem (a) and its training pipeline (b). technical stack, ALE is also a call to reframe the community’s priorities. In … ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.3 (p.5)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig03.png]]
> [!tip] 【图文联合解读】图3展示ROLL核心架构。

**(a)细粒度Rollout与异步训练**：上侧Rollout系统含Queue Scheduler→LLM Proxy→Environment三段流水线，下侧Training System以容量4条轨迹的Sample Buffer解耦Train Worker；Async Control Logic经Suspend/Update/Resume调度Rollout、KV Cache Recompute与Train step。LLM Engine时序显示4块GPU并行跑traj1–8，GPU D嵌入"Training i"，余卡于Vacant窗口待命，验证轨迹级流水线重叠。

**(b)Train-Rollout多路复用**：在同Async工作流上叠加shrink/expand机制——训练突发期GPU D让位运行Training i，原负责的traj5经Vacant触发KV Cache重算；高峰期再扩展恢复，证实动态GPU池可弹性伸缩。

论文借此论证：轨迹级异步流水线+弹性GPU复用是ROLL支撑大规模agentic RL高吞吐训练的系统基石，为后文实验规模扩展提供架构基础。
*caption: ROLL Architecture. (a) ROLL pipelines LLM generation, environment interaction, and reward phases at trajectory-level granularity. Training is also dec… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.4 (p.6)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示ROCK系统架构：右侧聚焦两大核心技能——Skill 4"海量调度"（含10,000+并发Sandbox，节点标注Running/Succeed/Failed/Pending四态，由Docker鲸鱼统一编排）与Skill 5"鲁棒容错隔离"（展示鲸鱼容器RUNNING/CRASHED状态自动恢复）；左侧揭示Worker–Sandbox–Env Hub执行栈，并通过Agent Bridging模块实现Model Server与RL Frame间经GEM传递Action/Observation的闭环交互。

**技术论断：** 该图直观论证ROCK具备万级并发沙箱编排与节点级故障自愈两大能力，是智能体强化学习训练得以规模化落地的工程基石。

**论文作用：** 作为Figure 4居于系统设计章节，为后续Table 4（大模型工具调用基准）等实验提供基础设施可行性背书，贯穿"craft on rock and roll"的核心叙事。
*caption: ROCK System Architecture.… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.5 (p.8)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig05.png]]
> [!tip] 【图文联合解读】图示iFlow CLI四大模块：用户界面（CLI Client/IDE Plugins/Web/SDK 4项）、Main Agent（含Compress/Reminder/Detection/Env. Mgmt 4种运行时扩展）、Tool Suits（File/MCP/System/Task/Network/Other 6类）、Context Management（Compression/Retrieval/Enhancement/Isolation/Persistent Memory 5项），通过Tool Call与Context Interaction双向联动，并叠加Hooks、Skill-Based Workflows、多级记忆三项增强能力。原文以此论证iFlow CLI可独立编排完整历史上下文，由代理统一转发至ROLL推理worker（训练）或外部API（部署），实现原生模式与ROLL的清晰解耦，简化训练-部署全链路。
*caption: The overview of iFlow CLI architecture and execution. these requests already contain the complete historical context, fully orchestrated by the iFlow … ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.6 (p.10)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读**

**1) 核心对象与结构**：图分左右两区。左侧 *Code Centric Data*——从 High-Quality Repo&PR 爬取 Repo/Issue/Test/Code Patch/Discussion，加工为 Localization、Repair、Unit Test Generation、Multi-turn Interaction、Code Reasoning 五类任务感知数据。右侧 *Agentic Data* 四个子模块：①Programming-Centric（Explore→Build→Review→Behavior 四 Agent 协作，产出 Instance 与 Trajectory）；②General Tool Use（Dialogue&API、Web 交互）；③Safety（Risk Knowledge→Inject Attack→Tiered Validation→Red Team）；④Data Filtering（Heuristic Filter→LLM-based Judge→Execution Simulator→Expert Inspection 四级流水线）。

**2) 关键技术结论**：训练数据由代码基本数据与 agentic 数据双轨合成，多 Agent 协作 + 四级过滤保障数据质量与安全，是 ROME 性能优异的底层支撑。

**3) 论文作用**：该图为 ROME 提供完整数据蓝图，支撑 Table 5/6 中 ROME 在多数基准上可比肩/超越更强开源 agentic 模型的实验结论，构成"数据→训练→评测"链路的关键上游环节。
*caption: Overview of data sources and composition pipelines for training agentic models, spanning code centric basic data and agentic data. 3… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.7 (p.16)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 7：ROME 训练管线）**

图示 ROME 三阶段训练架构：**Stage 1 连续预训练**共 800B tokens——500B 语料（代码+推理/工具调用数据）→300B 轨迹（文件系统、网页购物等）建立"原子能力→智能体求解器"，统一用 Next-Token Prediction 目标；**Stage 2 SFT** 按 70%智能体 / 15%推理 / 15%通用指令数据配比，经启发式过滤（冗余工具调用、过度思考、假阳性）+ LLM-as-Judge 排序，再以 Error/Context Masking 对失败/无关 token 零损失，完成"自适应数据回访"；**Stage 3** 基于 Chunked MDP（sᵢ,aᵢ,rτᵢ 序列）的 IPA 策略优化，融合 TOPR-TIS off-policy 增强、token 级重要性采样与动态轨迹过滤。原文借此论证"先预训练打基础→SFT 注入安全演示→RL 强化安全决策"的链式后训练路径，是全文方法论的骨架图。
*caption: Overview of ROME’s Training Pipeline. incidents. Finally, we generated corresponding golden trajectories devoid of general-security issues for subsequ… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.8 (p.20)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

IPA流水线核心：专家轨迹T*切分为t个chunk（c*₁…c*ₜ），每chunk含状态sᵢ及token序列（τᵢ、τₜ₁ᵢ…τₜₕᵢ、τ⁺ᵢ、τ⁻ᵢ）。经重采样生成两条rollout T⁽¹⁾、T⁽²⁾：早期chunk（绿框）走模仿学习，后续chunk（蓝框）走策略优化，分别输出折扣chunk级回报R(T⁽¹⁾)、R(T⁽²⁾)（γ折扣）。两关键机制：①chunk级重要性采样 ρ_cᵢ=(∏ π_θ^megatron/π_θold^megatron)^(1/|cₜ|) 修正策略偏移；②推理–训练失配掩码 m_cᵢ，当 SGLang 与 megatron 几何似然比 >H 即屏蔽该chunk。

**论证结论：**支撑§3.2.4.4样本效率——通过chunk级重采样+IS+掩码复用专家片段，避免冷启动探索。

**链路作用：**IPA是RL微调阶段的核心算法，与SFT互补，构成两阶段训练pipeline。
*caption: Overview of the Proposed Interaction-Perceptive Agentic Policy Optimization (IPA) training pipeline. sample efficiency(§3.2.4.4). An overview of our f… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.9 (p.22)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示横向三行对比同一智能体轨迹上三种重要性采样粒度。顶行（token级）将众多τ_token打包入chunk c₂…cₜ，两处"Interaction"箭头落入chunk内部，与chunk边界错位；中行（chunk级，橙色高亮并标✓）每条Interaction箭头恰好落在chunk边界上，τ_{2h}/r₂ 与 s_t/τ_{t1} 等位置严格对齐；底行（sentence级）一个粗粒度句子横跨多条Interaction，混叠多个交互事件。结构上量化呈现了"chunk数↔token数↔interaction次数"的三种对应关系。

原文据此论证：**chunk级粒度与环境中agentic交互的天然边界完全对齐**，既避免token级的子chunk内切分失配，又避免sentence级的跨交互混叠，因而是重要性采样的最优选择。

在论文方法链路中，该图为后续"采样策略—交互步对齐—策略梯度更新"模块提供粒度选择的实证依据，是连接环境交互建模与训练目标设计的关键前提。
*caption: Comparison of importance sampling strategies across token-level, chunk-level, and sentence- level granularities, where chunk-level aligns with the nat… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.10 (p.23)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig10.png]]
> [!tip] 【图文联合解读】图10以三联子图对比Chunk-Level Optimization与baseline。左图（对数纵轴10⁻²–10²）显示Chunk梯度范数稳定于~10⁻²，baseline在步骤35附近异常飙至~10²并剧烈震荡；中图训练成功率由51%升至峰值70%（稳定于65–68%），baseline仅~60–63%；右图测试成功率由48%升至峰值57.5%，baseline仅~52%。论文据此论证：分块级优化凭借稳定梯度与有效信用分配，在训练测试两端均显著优于baseline并具备泛化性，为整体"流式智能体"优化框架的稳健性与有效性提供关键实验支撑。
*caption: Comparison of Chunk-Level Optimization and baseline on a mini-set of the training data. Left:… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.11 (p.24)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig11.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：**
左图为"Sampling From Beginning"示意。一条轨迹被切分为多个 chunk（s₁→c₁→r₁→⋯→s*ₜ→c*ₜ→r*ₜ→⋯→s*ₗ），星号 s* 标识"关键岔路口"（Crucial Fork）状态。在每个 chunk 上并行展开 III 次 rollout（标注 ⁽ⁱ⁾、⁽ⁱⁱ⁾、⁽ⁱⁱⁱ⁾），结果全部以 ❌ 失败告终（"All Failures"、"Uninformative Rollouts"），右端仅露出"Expert-Like"轨迹示意，暗示需回溯到 s*ₗ 关键节点才可获得专家级轨迹。

**2) 关键技术结论：**
原文论证：从头开始的 rollout 难以抵达关键岔路口 s*ₗ，导致大量无效探索，严重限制策略学习效率；而 Sequential Rollback 从关键 chunk 初始化，可大幅降低探索负担，使模型沿关键节点逐步回溯，实现 chunk 级课程学习。

**3) 在论文中的作用：**
该图作为动机图，揭示了传统"从初始状态采样"在长程困难任务中的低效性，为后文提出的 Chunk-Level Initialized Resampling（Sequential Rollback）提供必要性依据，是 AgentFlow 训练管线中关键的数据采样加速机制之一。
*caption: Illustration of the Chunk-Level Initialized Resampling Strategy (Sequential Rollback). Left: In challenging tasks, sampling high-quality trajectories … ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.12 (p.25)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图含三子图，对比Seq-Rollback（绿）与Baseline（灰）约175步训练。左图"训练时平均成功率"：绿线在10%–100%剧烈波动、均值约60–80%，两橙色圈标记骤降点（≈20%和≈40%）；灰线恒为0%。中图"Expert Chunks数量"：绿线由~45递减至~20，标注"Rollback"箭头；灰线恒为0%。

原文用此论证：顺序回退机制能产出大量有价值正样本，而朴素采样基线完全失败；成功率骤降恰反映模型跨关键chunk回退重试的机制行为。作为论文核心贡献Sequential Rollback在难训练任务上的关键经验证据，支撑回退策略的必要性、有效性与可解释性。
*caption: Performance of Sequential Rollback and baseline (naive sampling) on a challenging training task. Left: Average success rate during training, which ref… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.13 (p.26)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图13对比"块级初始化重采样"（Parallelized Initialization, 橙线）与无该机制（灰线）下的IPA训练表现。可见右侧测试时成功率曲线：训练100步时橙线达约90%，灰线仅约52%，差距近40个百分点；左侧训练任务平均成功率在早期阶段橙线也明显领先。原文借此论证两点关键技术结论：(1) 块级重采样在训练初期即提供更多样化的奖励信号；(2) 使模型能以课程式方式攻克最难任务（Middle面板最低成功率亦显著提升）。在论文整体链路中，该图作为消融证据支撑"Parallelized Initialization"是IPA方法中提升rollout价值与最终泛化性能的关键组件。
*caption: Comparison of IPA with & without Chunk-Level Initialized Resampling (Parallelized Initial- ization) on a mini-set of the training data. Left: Average … ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.14 (p.27)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读（≤220字）**

该图为Figure 14的部分视图，展示Terminal Bench Pro的基准特征与跨基准对比。

**(a) 环形图**：呈现Terminal Bench Pro在8个任务类别（Scientific Computing、Debugging、Games、System Administration、Security、Machine Learning、Data Processing、Software Engineering）上的分布，各扇区面积接近，表明**类目分布均衡**（每类约12.5%）。

**(c) 热力图**：三列对比Terminal Bench 1.0/2.0/Pro Public在Security、SE、System Admin、Debugging四类上的pass@1标准差。Pro Public在所有四类均最低（如SE: 0.02 vs 1.0的0.09；Debugging: 0.04 vs 2.0的0.18），验证其**评估方差更低、更稳定可靠**。

**论证结论**：通过"均衡覆盖 + 低方差"双重证据，支撑Terminal Bench Pro作为**更严谨基准**的主张——避免类别偏斜与结果波动，使模型能力评估更具区分力。

**链路作用**：作为§3.3.2小节核心可视化，为后文实验（如评测新模型时统一在该基准上的可比性）提供方法论基础。
*caption: Benchmark characterization and cross-benchmark comparison of Terminal Bench Pro against other benchmarks.… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.15 (p.28)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig15.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 15 · 激活参数量 vs 准确率）：**

图示为各模型在 agentic 基准上的平均准确率（纵轴 10–40%）与激活参数量（横轴 0–40B+）的散点对比。核心发现：**iFlow-ROME（30B-A3B）在仅 ~3B 激活参数下达约 30% 准确率**，逼近 GLM-4.6（~28B 激活、~36%）、Kimi-K2-0905（~30B、~32%）等大模型，并显著优于同激活量级的 GPT-OSS-120B（~25%）与 Qwen3-Coder 30B-A3B（~21%）；右上方为参数未知的闭源模型（Claude-Haiku-4.5、GPT-5 Mini 等）。图中斜向"Performance-Parameter Trade-off"箭头印证：在极低激活成本下，iFlow-ROME 凭借路由机制实现了极具竞争力的 agent 性能，凸显 MoE 架构的效率优势，为论文"小激活、大能力"的核心主张提供量化支撑。
*caption: Performance-parameter trade-offs in agentic tasks. Scores represent averages on general agentic and code agent benchmarks. Models with known parameter… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.16 (p.34)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig16.png]]
> [!tip] 【图文联合解读】**图16解读**

**1) 核心对象与数据**：5×5 配对胜率热力图（去除平局），基于 100 个真实任务、30 位专家盲评多数投票，行模型相对列模型的胜率（绿高红低）。ROME 对 Qwen3-Coder 30B 与 Devstral Small 2 取得 **100%** 全胜；对 Qwen3-Coder Plus 与 GLM-4.6 达 **58.8%**；GLM-4.6 对 Plus 仅 44.4%；30B 对 Small 2 为 61.1%。ROME 在各列向上颜色均最绿。

**2) 关键论证结论**：ROME 不仅碾压开源小模型（30B、Small 2），对当前最强商用编码模型（Plus、GLM-4.6）仍保持多数头对头胜率，证明其在真实复杂任务上的全面领先。

**3) 论文整体作用**：作为主实验人评证据，与自动化榜单互补，支撑"RFlow/ROME 优于 SOTA 商用与开源 agent"这一核心论点，是论文方法有效性的关键验证环节。
*caption: Pairwise win-rate matrix (%) on the 100-task real-world benchmark under 30-expert blinded majority voting. Each cell reports the percentage of tasks w… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.17 (p.36)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig17.png]]
> [!tip] 【图文联合解读】**图17图文联合解读：**

该图呈5×3网格，对比5个AI系统生成"睡眠管理系统"App的截图，各3张：

- **ROME (a-c)**：粉紫渐变欢迎页（含环形进度）、深色数据分析页（指标卡 7h30m/82%/23:15/12 + 折线/柱状图）、带头像设置页，UI最完整美观。
- **Qwen3-Coder-Plus (d-f)**：周报、睡眠记录（进度条）、数据分析柱状图，结构简单。
- **GLM-4.6 (g-i)**：折线+环形图仪表盘，但三张截图几乎雷同，多样性差。
- **Qwen3-coder-30B (j-l)**：饼图+数据表（100%/22:45/82%/62%），信息密度低。
- **Devstral-Small-2 (m-o)**：任务清单、记录页（42h30m/7h15m/85%/12）、图表页，导航不连贯。

**原文论证结论**：ROME 能产出多页面、含导航与丰富可视化、视觉风格统一的完整Web应用；基线模型普遍存在页面单调、组件缺失或生成重复等问题。

**作用**：作为Case study 1的定性证据，与定量评测互补，共同支撑ROME在端到端全栈Web生成上的优越性。
*caption: Case study 1 screenshot examples: Sleep Management System Generation. 36… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.18 (p.37)
![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig18.png]]
> [!tip] 【图文联合解读】图18以5×2网格对比ROME、Qwen3-Coder-Plus、GLM-4.6、Qwen3-coder-30B、Devstral-Small-2五款代理在"太阳系建模"任务第2、3次截图：ROME呈现完整恒星＋多颗行星分布在同心轨道环上，UI控件齐全；Qwen3-Plus行星排成水平直线，几何失真；GLM-4.6背景转为蓝色渐变且太阳退化为黄色矩形，未完成渲染；Qwen3-30B行星稀少；Devstral-Small-2两屏几乎全黑，仅留椭圆描边。图中用以论证ROME在多轮迭代式可视化生成中，物体完备性、布局合理性与稳定性显著优于开源基线模型，支撑论文"agentic crafting"框架能显著提升大模型创意编码与复杂动态场景构建能力这一核心结论。
*caption: Case study 2 screenshot examples: Solar System Modeling. 37… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.1 (p.1)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读（中文）**

**1）核心对象与结构/数据：**
图分三栏。左栏为Avg@4准确率柱状图，在GAIA/xBench-DeepSearch/Frames三基准上，Before RL（43.7/28.7/58.9）→ASearcher-v1（52.8/42.1/70.9）→ASearcher-v2（58.7/51.1/74.5），v2相对RL前分别提升+15.0/+22.4/+15.6。中栏显示训练步0–450中每轨迹工具调用次数，阶段2（>200步）后MAX约从5增至100+，AVG从~2升至20+。右栏（log刻度）显示生成tokens从~10⁴升至~10⁵。

**2）原文论证的关键技术结论：**
异步RL带来显著增益，验证训练有效性；随训练推进，模型自发学习更长程的搜索行为（工具调用与生成长度均上升），证明大尺度异步RL可"解锁"十回合以上的长时搜索能力。

**3）在论文中的作用：**
开篇Figure 1统领全文，主图三栏共同支撑"异步RL既提精度、又增长horizon"的两大核心论点，为后续方法与消融提供动机与可视化依据。
*caption: (Left) Asynchronous RL brings substantial improvements: Through RL training, our agent, ASearcher-Web-QwQ, obtains +15.0, +22.4, and +15.6 improvement… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.2 (p.3)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图2对比Search-R1与ASearcher两种智能体架构。左侧Search-R1仅配备搜索工具，单轮最大≤10 turns，仅返回Top-K条目；右侧ASearcher集成搜索+浏览双工具，最大支持≤128 turns长程交互，且能将约100K长度的网页内容摘要压缩至约100长度。图例区分可训练组件（LLM Gen、Tool Calling）、外部工具与外部信息四类。

原文借此论证关键结论：ASearcher以单一LLM即可同时完成推理与长网页总结，无需依赖外部LLM，突破Search-R1的10轮瓶颈。

作用：作为方法核心框架图，为后续大规模异步RL训练及Table 2本地知识库实验提供架构基础。
*caption: Comparison between ASearcher and Search-R1. (Left) Search-R1 is only equipped with search tools and lacks web browsing capability. (Right) ASearcher u… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.3 (p.4)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图3以GAIA复杂问答"Mice"为题，对比三列方法推理轨迹：Search-R1-32B 3次搜索即给出错误"Pigs"且无验证；Search-o1(QwQ)经多轮检索定位文献，但漏关键信息并误判为"Goats"；ASearcher-Web-QwQ通过四阶段——聚焦搜索定位Hafnia alvei→识别Wikipedia及相关2021临床文献→跨文档关联Olga Tapia小鼠研究→基于二次检索的*Grounded Verification*——得出正确答案"Mice"。

该案例支撑论文核心结论：端到端异步RL赋予智能体**长程分解、不确定性感知与自我验证**能力，使其在超过10轮的复杂任务上优于无验证搜索式RL及已有Search-o1基线，是正文论证ASearcher长视野搜索优势的**关键定性证据**。
*caption: A case study on a complex query from GAIA. Search-R1-32B is unable to break down the complex question and has severe hallucinations. Search-o1 (QwQ) c… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.4 (p.7)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图4展示数据合成Agent的三阶段闭环管线：①**左：种子输入**——以QA对（Q："Daniel Charbonell 2014签约旧金山巨人合同几年？" A：四年）及支撑事实为起点；②**中：双动作迭代修改**——**Injection**通过搜索引擎+浏览器抽取外事实（如"古巴外野手，曾效力San Jose Giants"）注入问题增加线索；**Fuzz**模糊关键信息（如将"2014"改为"early 2010s"）提高不确定性；③**右：质量验证三步**——基本可解性与清晰度检查、多答案生成测难度（仅"四年"✓）、答案唯一性校验；通过后回流更新QA与事实库。

**论文作用**：此管线为大规模异步RL训练提供高质量、可解、唯一、具长程推理难度的事实型QA数据，是Agentic Search模型在GAIA/xBench等基准（表4）取得SOTA的数据基础。
*caption: Data Synthesis Agent. Starting from a seed QA, the data synthesis agent iteratively modifies the question through two actions, Injection and Fuzz. Thr… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.5 (p.7)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心数据**：左图支撑事实数主要分布在7–9之间（占比~0.18–0.19），呈长程检索特征；中图fuzz动作集中在5–6次（峰~0.33），injection动作更分散、向10–11次偏移，整体动作链跨度大；右图QwQ-32B无工具直接答题准确率呈双峰分布，约60%集中于0附近，约15%接近1。

2) **关键结论**：合成问题普遍依赖多条事实链与多轮检索动作，远超单跳查询；模型无工具时绝大多数无法作答，双峰说明问题要么完全无法直接推理、要么模型"碰巧"记住，真正考验搜索与多轮整合能力。

3) **论文作用**：作为数据合成管线的统计验证，为后续ASearcher的大规模异步RL训练提供难度合理、长度足够的长程搜索任务基线。
*caption: Statistics from our data synthesis process. (Left) The distribution of the number of supporting facts. (Middle) The distribution of the number of fuzz… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.6 (p.9)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1. **核心对象与数据**：左图显示ASearcher-Web-QwQ测试时平均工具调用数（5→12）与平均准确率（≈52%→55%）呈单调上升关系；中图显示训练过程中每条轨迹的工具调用数：MAX从约5增长至峰值60–70，AVG稳定在3–7，MIN接近0–1；右图log尺度下生成tokens同步增长（MAX由≈5×10⁴升至≈2×10⁵，AVG由10⁴升至≈2×10⁴）。

2. **关键技术结论**：测试时强制更多回合显著提升准确率，验证了长程搜索的scaling有效性；训练中模型自发涌现出远超常规的长轨迹行为，突破了"ten-turn"限制。

3. **论文中的作用**：以训练动力学（工具调用与token长度自然增长）+ 测试时scaling实证共同支撑"大规模异步RL可解锁长程agentic搜索"这一核心论点，衔接方法设计与下游性能收益。
*caption: (Left) Test scaling of ASearcher-Web-QwQ. Data points are obtained by enforcing different minimum turns.The accuracy is averaged over GAIA, xBench-Dee… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.7 (p.10)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示横向对比两种RL训练流水线。**One-Step-Off RL**：轨迹1–12并行生成，但批次须等待最长轨迹（如横跨多步的Traj 7）才能启动Train Step N，期间已完成的Traj 8–12被迫"Idle Time"；训练步内mini-batch顺序为(1,2,3,4)→(6,5,8,7)，存在乱序与浪费。**Fully Async RL**：轨迹持续异步产出，训练步N/N+1/N+2以更短周期无缝触发，分别消费(1,2,3,4)、(5,6,8,9)、(10,7,11,13)，GPU近满载。该图论证：完全解耦训练与轨迹生成可消除长尾阻塞、显著加速训练，是论文支撑大规模长周期智能体搜索RL训练的核心基础设施依据。
*caption: One-Step-off RL v.s. Fully Asynchronous RL. In batch generation systems, a batch should wait for the longest trajectory, leading to significant GPU id… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.8 (p.14)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以双柱状图（左 Avg@4、右 Pass@4）在 GAIA、xBench-DeepSearch、Frames 三大基准上对比 QwQ-32B 基座 RL 训练前后的表现。**具体数据**：Avg@4 三基准分别由 43.7/28.7/58.9 提升至 58.7/51.1/74.5（ASearcher-v2）；Pass@4 由 62.1/51.0/77.1 提升至 74.7/75.0/85.5，且 v1→v2 仍持续单调上升。

**关键论证**：原文借此佐证所提出的异步大规模 RL 训练流程，使 agent 习得复杂检索、关键信息抽取与冲突信息消解能力——尤其 xBench-DeepSearch 增幅最显著（Avg@4 +22.4、Pass@4 +24.0），说明 RL 对长程深度搜索类任务增益最大。

**论文作用**：作为核心主结果图，量化证明方法在多基准上对开源基座 QwQ-32B 的稳定提升，支撑整体异步 RL 训练范式有效性的实验结论。
*caption: Comparison of the performance of QwQ-32B agent before and after RL Training. training pipeline trains the agent to learn complex search strategies to … ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.9 (p.15)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig09.png]]
> [!tip] 【图文联合解读】图9展示ASearcher-Local-7B在约300个训练步内三项均值指标的变化曲线：(a) **生成Tokens**从~1000于~50步骤降至~150低谷，后回升至~900；(b) **搜索次数**由~1于~80步后稳步攀升至~5.5；(c) **URL直访**由~0.4于~50步内归零并长期维持近0。

**技术结论**：训练初期模型快速抑制冗余URL直访并精简生成；随后轨迹逐步延长、检索轮次自然增加，验证"长程多轮检索行为由RL自主涌现"而非依赖设计。

**论文作用**：作为ASearcher异步RL方法在长视野agentic搜索中有效性的一手演化证据，支撑全文关于模型自学深度检索、突破十轮瓶颈的核心论点。
*caption: Training Dynamics of ASearcher-Local-7B.… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.10 (p.15)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig10.png]]
> [!tip] 【图文联合解读】**Figure 10 联合解读**

Figure 10 展示 ASearcher-Local-14B 在约 220 训练步内三个行为指标演变：
- (a) 单轨迹生成 token：由 ~400 降至 ~200（step 25），step 60 跃至峰值 ~720，后续于 500–650 震荡；
- (b) 单轨迹搜索次数：由 ~1.5 在 step 35 后跃升，峰值 ~5.8（step 60），稳定于 4–5；
- (c) 单轨迹 URL 访问：长期近 0，step 130 后跃升至 ~1.8–2.0 并维持。

三图共同证明：随异步 RL 推进，模型自发涌现更长推理链、更频繁的多轮搜索与网页访问，验证方法有效激励长程智能体搜索行为。该图在论文中作为训练动态的关键实证，支撑"异步大规模 RL 可解锁超十轮搜索"的核心论点。
*caption: Training Dynamics of ASearcher-Local-14B. 15… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with — Fig.11 (p.16)
![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig11.png]]
> [!tip] 【图文联合解读】**图11联合解读**

**核心数据**：左图展示训练step 0–400内6个反思关键词（search/alternatively/wait/check/confirm/however）的每轨迹词频，"search"峰值约8k+、"alternatively"约7k；右图展示5个外部信息显式引用词（doc/mention/source/earlier/previous）频次，"doc"峰值约2.5k、"previous"约1.5k。两组曲线在step ≈250后均出现陡升拐点并持续上行。

**关键结论**：随着RL训练推进，智能体自发地、显著地增加了反思性措辞与显式回溯外部文档的频率，证明"自我校验＋信息溯源"这一核心agentic行为模式是奖励驱动的涌现结果，而非依赖prompt工程或SFT的先验注入。

**整体作用**：作为行为层面（behavioral）的诊断证据，支撑论文主张——大规模异步RL能自然解锁长视野智能体搜索能力，反思-引用循环是性能增益的关键机制。
*caption: Left: Word count of reflective keywords during training time. Right: Word count of keywords indicating explicit reference of external information. sop… ｜ 论文 [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ｜ arxiv 见 MD 元信息*

### AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys — Fig.1 (p.4)
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以时间轴横向对比两种RL系统的执行流：左侧同步系统将24次生成任务（蓝条1-24，分布于4张GPU）依次排布，待全部生成完毕后才执行3轮训练块（橙块"1-8/9-16/17-24"）与权重加载（黄条），导致GPU在训练与加载阶段完全闲置；右侧一步重叠方案则把训练固定在单张GPU上进行，其余3张GPU持续滚动生成，使推理设备空置时间显著减少。

原文借此论证：**同步流水线存在严重的推理—训练串行空泡，是端到端吞吐的关键瓶颈**；即便仅做一步重叠也能回收大量空闲算力，从而为AReaL所提出的"全异步、生成与训练深度交叠"的整体架构提供量化动机，是其方法设计的核心起点，并在后续Table 1中转化为对AIME24/LiveCodeBench上端到端效率提升的实验依据。
*caption: Execution timeline of a synchronous (left) and a one-step overlap (right) RL system showing underutilized inference devices. … Rollout Controller Rewa… ｜ 论文 [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] ｜ arxiv 见 MD 元信息*

### AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys — Fig.2 (p.4)
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示AREAL异步架构核心组成：①**生成端**（左虚线框）含多个Interruptible Rollout Worker（GPU节点，以"…"示意可扩展），受Rollout Controller（CPU）调度，由Reward Service（CPU）打分；②**训练端**（右虚线框）含多个Trainer Worker（GPU节点），通过Parameter Service做参数Save/Load（紫色箭头）；③数据通路为Rollout Controller → Aggregate Batch → Replay Buffer → Send Full Batch，左→右流动（蓝箭头Trajectory、绿箭头Prompt）；④红箭头Interrupt Signal支持生成途中刷新权重。

原文论证结论：解耦generation与training，避免同步RLHF的吞吐瓶颈；"可中断rollout"机制使轨迹可基于近实时策略生成，保证数据新鲜度。

论文整体作用：该架构是AREAL方法落地的系统工程核心，支撑其在大规模语言推理任务上实现高吞吐、近实时策略更新的RL训练链路。
*caption: The AREAL architecture featuring asynchronous generation and training components.… ｜ 论文 [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] ｜ arxiv 见 MD 元信息*

### AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys — Fig.3 (p.4)
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以时间轴展示AREAL的异步生成-训练流水线：GPU1/GPU2并行执行生成任务（蓝色，编号1–9及字母a–g），GPU3负责训练（橙色，Batch1=1–4、Batch2=5–8、Batch3=9–c），三批之间通过黄色Load Weight加载新参数（θ₀→θ₁→θ₂），竖虚线标出"下一批次训练就绪时刻"。

图中蓝叉标记θ₁/θ₂到达时被中断的旧请求，中断后必须以新权重重做绿色KV Cache Recompute才能复用。该图论证了AREAL的核心机制：**用"可中断生成+重计算"换取参数新鲜度**——避免stale data的同时，量化了异步带来的KV重算开销，是支撑文中"训练不被生成阻塞、生成不因训练而等待"的关键设计图示。
*caption: Illustration of generation management in AREAL. Vertical lines show the ready time for the next step training. Blue crosses show the interrupted reque… ｜ 论文 [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] ｜ arxiv 见 MD 元信息*

### AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys — Fig.4 (p.8)
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig04.png]]
> [!tip] 【图文联合解读】**图4联合解读：**

图4以2×2子图展示强扩展性实验，对比AREAL（蓝实线）与verl（橙虚线）在GPU数从128增至512时的吞吐量，纵轴约18k–37k tokens/秒，覆盖7B/32B模型与16k/32k上下文四种组合。AREAL扩展接近理想线性线，32B模型下吞吐由约18k提升至35k；verl斜率显著偏低，且在32B+32k上下文时直接OOM导致数据缺失。

该图用以论证AREAL异步RL框架的扩展性优势：在更大模型、更长上下文场景下仍保持近线性加速比，而同步基线verl已触及显存瓶颈，从而为论文"大规模异步RL可行且高效"的核心结论提供关键实证支撑。
*caption: The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so th… ｜ 论文 [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] ｜ arxiv 见 MD 元信息*

### AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys — Fig.5 (p.9)
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读（图5，p.9）**

**1）核心对象与数据：** 三面板消融实验，基于1.5B模型在数学推理任务上的训练。(a)(b)分别为naive PPO与解耦目标（式5）下MaxStaleness∈{0,1,2,4,8,16,∞}的奖励曲线；(c)为有效吞吐量条形图，定量数据为128.7→269.3→356.6→356.6→371.7→382.4→396.8 k tokens/s，随staleness单调递增。

**2）关键结论：** 仅增大staleness会劣化naive PPO（曲线发散、奖励下降）；而解耦目标使所有staleness曲线紧贴η=0 oracle，性能几乎无损。二者结合即"适度staleness+解耦目标"可获得>2×训练加速且保持最终评估性能——证实两个算法选择缺一不可。

**3）论文链路作用：** 该图为AREAL异步RL框架的核心算法决策提供实证：它把"解耦PPO目标"与"staleness容忍度"确立为系统级最优配置，支撑后文大规模实验的高吞吐-高性能主张，是方法论可行性的关键消融证据。
*caption: Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essentia… ｜ 论文 [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] ｜ arxiv 见 MD 元信息*

### AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys — Fig.6 (p.10)
![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig06.png]]
> [!tip] 【图文联合解读】图6(b)展示中断式生成消融：1.5B模型吞吐量231k vs 207k tokens/s，7B为130k vs 111k，可中断机制带来约12%–17%提升。结合未渲染的图6(a)：动态批处理在1B/7B/32B较常规批处理分别达427.4/454.7/387.7 vs 404.4/303.1/283.0 TFLOPs/GPU，平均~30%吞吐增益。两图共同量化验证AREAL的两项系统优化——动态微批次分配与可中断生成——均显著提升吞吐，在论文方法链中为异步RL框架的工程可行性提供关键实验支撑。
*caption: Ablation studies on system optimizations. experimental setup, we configured 32 micro-batches for the standard setting and established a token budget o… ｜ 论文 [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] ｜ arxiv 见 MD 元信息*

### DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via  — Fig.2 (p.6)
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-fig02.png]]
> [!tip] 【图文联合解读】图2展示DeepSeek-R1的四路汇聚管线（带6类图例：模型/提示-响应/算法/提示/奖励/后处理）：

(a) V3 Base → RL（Accuracy & Format奖励）→ **R1 Zero** → Sampling+Filter（准确性）+人工Refine → Cold Start Long CoT 数据；

(b) V3 Base → SFT（冷启动长CoT）→ **Dev-1** → RL（规则奖励 & 语言一致性）→ **Dev-2**；

(c) V3 Sampling → 推理+非推理数据集；

(d) V3 Base → SFT融合数据 → **Dev-3** → RL（规则奖励 & 偏好奖励）→ **R1**。

原文借此论证"冷启动长CoT → 双轮SFT+RL迭代"是兼顾推理能力激发与人类对齐的核心范式，作为整篇方法学总览图，为后续蒸馏与基准对比提供路线支撑。
*caption: In the initial stage, we collect thousands of cold-start data that exhibits a conversational, human-aligned thinking process. RL training is then appl… ｜ 论文 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via  — Fig.3 (p.14)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]]
> [!tip] No figure is visible in the provided image. The image contains only page 14 of an academic paper, consisting of body text discussing Supervised Fine-Tuning (SFT), Reinforcement Learning (RL), and a section titled "A.3. A Comparison of GRPO and PPO." 

While the text references "Figure 3" for a comparison between GRPO and PPO algorithms, the actual figure/diagram is not present in this image — only a textual reference and the start of equations ("For each question ?, GRPO samples a group of outputs {o₁, o₂, ..., o_G} from the old policy") are shown.

If you intended to share Figure 3, please upload the image containing the actual diagram (architecture/components/data flow visualization). I'd be happy to describe it and transcribe the caption once provided.
*caption: For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g from the old policy 14… ｜ 论文 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via  — Fig.6 (p.35)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]]
> [!tip] **Note:** The main visual on this page is **Table 6** (no architecture/data-flow figure is present). Description and caption below.

**Description (Table 6):**
The table maps six DeepSeek-R1 distilled student models to their base backbones and initial learning rates. Components include: (1) *Distilled Model* — six sizes spanning 1.5B–70B parameters across Qwen and Llama families; (2) *Base Model* — pre-trained sources (Qwen2.5-Math-1.5B/7B, Qwen2.5-14B/32B, Llama-3.1-8B, Llama-3.3-70B-Instruct); (3) *Initial Learning Rate* — values ranging from 1×10⁻⁴ (smallest) down to 2×10⁻⁵ (largest).

**Key takeaway:** Initial LR scales inversely with model size (1×10⁻⁴ for 1.5B → 2×10⁻⁵ for 70B), and the two smallest Qwen variants intentionally use math-specialized base models (Qwen2.5-Math) to bootstrap reasoning capability before distillation.

**Caption (verbatim):**
Table 6 | DeepSeek-R1 Distilled Models, their corresponding Base Models, and Initial Learning Rates.
*caption: B.6. Ablation Study of Language Consistency Reward… ｜ 论文 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via  — Fig.7 (p.37)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]]
> [!tip] ## Figure Description

The actual Figure 7 plot is not visually rendered in this page excerpt — only its caption appears. Based on the caption and surrounding discussion, the figure depicts the **Language Consistency (LC) Reward ablation during reinforcement learning**, comparing two RL training conditions on language-mixing behavior.

**Components/data flow implied by the figure:**
- **X-axis:** training steps (RL progress)
- **Y-axis:** language consistency metric
- **Curves:** a baseline RL run *without* LC reward vs. an RL run *with* LC reward applied
- **Side panels (per text):** benchmark performance on math (maintained) and coding (slight degradation)

**Key technical takeaway:**
Without the LC reward signal, the model progressively drifts into language mixing as RL progresses; introducing LC reward preserves stable monolingual output throughout training, trading only marginal coding-benchmark performance for substantially better alignment with human-preferred readability.

## Caption (verbatim)

**Figure 7** jThe experiment results of Language Consistency (LC) Reward during reinforcement learning.
*caption: As can be seen, without the LC reward, language consistency gradually deteriorates as train- ing steps increase. However, when the LC reward is applie… ｜ 论文 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via  — Fig.13 (p.48)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]]
> [!tip] ## Main Figure Description

**Architecture/Components:**
Table 9 is a structured comparison matrix evaluating AI models across six safety benchmarks. The columns include the SST, BBQ, ART, XSTest, DNA*, and HarmBench* metrics, alongside an Average Score column. The rows compare frontier models: Claude-3.7-Sonnet, o1, GPT-4o, Qwen2.5 Instruct (72B), DeepSeek-V3, plus two DeepSeek-R1 variants (hide cot and standard R1).

**Data Flow/Logic:** Scores flow horizontally from individual benchmark evaluations to an aggregated Average Score column. The asterisked benchmarks (DNA, HarmBench) are reproduced by the authors, while other results derive from independent HELM evaluations. Values in parentheses represent pure-model performance without the risk control system described in D.3.1.

**Key Technical Takeaway:** DeepSeek-R1 achieves an average safety score of 95.0 (with risk control), comparable to or exceeding Claude-3.7-Sonnet (94.6) and GPT-4o (92.2). However, without the risk control system, its HarmBench score drops dramatically from 89.3 to 35.0—revealing that the model's raw safety behavior relies heavily on post-hoc filtering rather than intrinsic alignment. (117 words)

## Caption Verbatim Transcription

"Table 9 |Comparison of DeepSeek-R1 and other frontier models on safety benchmarks. A higher score indicates better safety performance. Benchmarks marked with * are the results reproduced by us, while other numerical results are obtained from the independent HELM evaluations. The numbers in parentheses represent the results of the pure model without considering the risk control system (introduced in D.3.1)."
*caption: We have categorized potential content safety challenges faced by language models into 4 major categories and 28 subcategories.… ｜ 论文 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via  — Fig.14 (p.53)
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]]
> [!tip] # Observation: No Figure Present

The provided image contains **only text content** (page 53 of a research paper, likely the DeepSeek technical report). No figure, chart, diagram, or visualization is visible in the image. The text merely *references* "Figure 14" for multilingual safety scores across 50 languages, but the figure itself is not shown.

# Available Text Content

Since no figure is present, I can only transcribe the visible caption-adjacent text. There is no caption to transcribe verbatim because no figure is rendered.

## Section Headers Visible:
- **D.3.4. Multilingual Safety Performance**
- **D.3.5. Robustness against Jailbreaking**

## Key Technical Content (from the text, in lieu of a figure):

**Test Set Construction:**
- Original bilingual safety testset translated into **50 commonly used languages**
- Full translation for high-frequency languages; sampling translation for low-frequency ones
- Final corpus: **9,330 questions**
- Quality ensured via combined **LLM translation + human-assisted calibration**

**Scoring Scheme (LLM-as-a-judge):**
| Response Type | Points |
|---|---|
| Safe | 5 |
| Unsafe | 0 |
| Rejection | 4 |

**Headline Results Across 50 Languages:**
| Model | With Risk Control | Without Risk Control |
|---|---|---|
| DeepSeek-V3 | **86.5%** | 75.3% |
| DeepSeek-R1 | **85.9%** | 74.2% |
| Claude-3.7-Sonnet | 88.3% | — |
| GPT-4o (2024-05-13) | — | 75.2% |

**Key Takeaway:** With the risk control system enabled, DeepSeek-V3/R1's multilingual safety approaches Claude-3.7-Sonnet (SOTA), while DeepSeek-R1 exhibits **zero high-risk languages** — indicating no obvious language-specific vulnerabilities.
*caption: For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and without the risk control system (introduced in D.3.1). Additionally, w… ｜ 论文 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Conditional Memory via Scalable Lookup: A New Axis of Sparsi — Fig.2 (p.6)
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**(a) 训练阶段**：图中展示两块 GPU 设备并行计算，底层 Input IDs 经 Vocab Embedding 与 Transformer Block 后分流入两卡，每卡按 Engram → Attention → MoE 顺序堆叠并带残差⊕；两卡 Engram 表之间通过 All2All 通信交换活跃行。

**(b) 推理阶段**：单设备上 Vocab Embedding → Transformer Block → 含 Engram 层（紫色）→ Transformer Block → 含 Engram 层，主机端 Engram 表存于"Memory Hierarchy"，通过 Host Communication 按需加载到 On Device Computation。

**论证结论**：训练通过表分片+All2All 实现容量随加速卡线性扩展；推理通过主机卸载释放设备显存，结合数据复用发挥条件记忆效用。

**论文作用**：该图为 Engram 方法提供系统级可行性证明，是后续 Table 2（Engram-27B 仅 82% FLOPs 即匹配基线 LongPPL）等效率实验的工程基础。
*caption: During training, to accommodate large-scale embedding tables, we employ standard model parallelism by sharding the tables across available GPUs. An Al… ｜ 论文 [[conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models]] ｜ arxiv 见 MD 元信息*

### Conditional Memory via Scalable Lookup: A New Axis of Sparsi — Fig.5 (p.16)
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig05.png]]
> [!tip] 【图文联合解读】图5展示Engram架构消融：深蓝曲线描绘3B MoE下Engram单模块插入层深（Layer 8–12）对验证损失的影响，呈先微升后回落趋势，结合原文揭示Layer 2早注最优。右栏5个×号标记消融变体：去多分支融合、去token压缩、去门控、加4-gram、去短卷积，分别落于橙虚线（基线）与绿虚线（完整Engram）之间梯度位置。原文借此论证三大核心组件——分支专属融合、上下文感知门控、tokenizer压缩——任一缺失即引最大回归。该图为论文"条件记忆需多组件协同"方法论的关键证据，串联架构设计→消融验证→相对3B MoE全面优越的实验闭环。
*caption: We find that three components yield the most significant gains: (i) branch- specific fusion within the multi-branch backbone, (ii) context-aware gatin… ｜ 论文 [[conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models]] ｜ arxiv 见 MD 元信息*

### Conditional Memory via Scalable Lookup: A New Axis of Sparsi — Fig.7 (p.18)
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig07.png]]
> [!tip] 【图文联合解读】## Figure 7 联合解读

**核心对象与结构**：图以热力图形式展示 Engram 门控机制在多语言文本上的激活分布。颜色越深红表示门控标量 αₜ 越接近 1，每行对应一个 token 序列，N=3 后缀 n-gram 完成后触发。可观察到五行示例：(1) 英文 "…norse Brucephal us." 中 "Bruce" 与 "phalus" 显著激活；(2) "Way." 中 "Way" 激活；(3) "…iana, Princess of Wales." 中 "Princess of Wales" 连续高亮；(4) 中文 "印刷术。" 中 "术" 单独激活；(5) 中文 "…医圣',…《伤寒杂病论》" 中 "医圣"、"《伤寒杂病论》" 等命名实体高亮。

**关键论证结论**：门控机制并非均匀响应，而是呈现高度选择性——仅在**静态、可枚举的局部模式**完成时强烈激活，涵盖英语多 token 命名实体（如 Princess of Wales）与公式化短语；该选择性在中文场景同样成立（"医圣"、《伤寒杂病论》），证实跨语言泛化。

**链路作用**：此图构成 Engram "条件记忆"假设的定性证据，表明查找表能精准捕捉模式补全信号而非全段均匀检索，是后续量化稀疏性增益与推理加速实验的机理基础。
*caption: The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static pa… ｜ 论文 [[conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models]] ｜ arxiv 见 MD 元信息*

### HC: Manifold-Constrained Hyper-Connections — Fig.1 (p.1)
![[assets/crops/hc-manifold-constrained-hyper-connections-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图对比三种残差连接结构：(a) 标准残差——单条恒等旁路，x_l 经 Layer F 后与 x_l 简单相加得 x_{l+1}；(b) Hyper-Connections (HC)——引入三个可学习映射（橙色 H_l^pre、H_l^post、H_l^res），将单流扩展为多流并通过 Pre/Post/Res Mapping 混合；(c) mHC——在 HC 基础上对三个映射分别施加流形投影算子 P_M（绿色框），即 P_M^pre(H_l^pre)、P_M^post(H_l^post)、P_M^res(H_l^res)。

原文借此论证关键技术结论：HC 的 Res Mapping 矩阵若不加约束，其行和可能偏离 1、破坏残差流的尺度稳定性，导致训练振荡；mHC 将映射投影到（如双随机矩阵）流形上，从而稳定残差信号幅度。

在论文中的作用：作为开篇 Figure 1，它奠定全文方法框架，使后续 Table 1 的消融实验与正文中关于"流形约束带来收敛稳定性与性能增益"的论证得以直观对照。
*caption: Illustrations of Residual Connection Paradigms. This figure compares the structural… ｜ 论文 [[hc-manifold-constrained-hyper-connections]] ｜ arxiv 见 MD 元信息*

### HC: Manifold-Constrained Hyper-Connections — Fig.2 (p.7)
![[assets/crops/hc-manifold-constrained-hyper-connections-fig02.png]]
> [!tip] 【图文联合解读】图(a)显示HC相对mHC的绝对损失差在5k步内从~0.012骤降至近0，但15k步后又反弹至~0.005；图(b)显示HC梯度范数在0.10–0.18间剧烈震荡，而mHC从0.25单调降至~0.05。原文据此论证HC存在训练不稳定（梯度范数不收敛、损失差回升），从而引出对残差流施加流形约束的mHC，作为全文核心方法改进的动机与实验起点。
*caption: Training Instability of Hyper-Connections (HC). This figure illustrates (a) the absolute… ｜ 论文 [[hc-manifold-constrained-hyper-connections]] ｜ arxiv 见 MD 元信息*

### HC: Manifold-Constrained Hyper-Connections — Fig.3 (p.7)
![[assets/crops/hc-manifold-constrained-hyper-connections-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a)展示单层映射 𝓗^res 的逐层前向信号增益（灰）与反向梯度增益（蓝）：在 60 层内二者大多围绕 1 波动（数量级 ≈10⁰），仅在边界 *l*≈0、*l*≈60 处出现尖峰（前向 ≈30，反向 ≈15）。图(b)展示累积乘积 ∏𝓗^res 的复合映射：前向信号末端骤升至 ≈500（10^2.7），反向梯度在中间层累积放大至 ≈3000（10^3.5），整体呈 2–3 个数量级的指数级爆炸。

原文借此论证 **HC 的传播不稳定性**：单层增益看似平稳，但跨深层逐层相乘后信号/梯度会发生数量级级别的发散。该图是论文提出"流形约束（manifold-constrained）"方案以稳定 HC 残差传播的核心动机图，直接驱动后续实验设计与消融验证。
*caption: Propagation Instability of Hyper-Connections (HC). This figure illustrates the… ｜ 论文 [[hc-manifold-constrained-hyper-connections]] ｜ arxiv 见 MD 元信息*

### HC: Manifold-Constrained Hyper-Connections — Fig.4 (p.12)
![[assets/crops/hc-manifold-constrained-hyper-connections-fig04.png]]
> [!tip] 【图文联合解读】**图4 图文联合解读：**

**1) 核心对象与结构：** 图示三流并行时间轴——Normal Compute Stream（含 MLP(B/W/F)、ATTN(B/W/F) 及 Whole Stage Recompute(B)）、Communication Stream（含 DISPATCH(F/B)、COMBINE(F/B)、PP Send/Recv(F/B)）、High Priority Compute Stream（仅承载 ℱₚₒₛₜ,ᵣₑₛᴹ）。小操作 ℱᵖʳᵉᴹ、ℱᵖᵒˢₜ,ᵣₑₛᴬ 等以斜纹小矩形穿插于各流衔接处，体现 Dense 交互开销被嵌入 DualPipe 调度。

**2) 关键结论：** mHC 引入的预聚合/残差聚合额外开销（m 路分发-合并）可与 PP 通信及主流计算完全重叠；高优先级流使小算子不被 stall，证明 mHC 在不牺牲通信-计算重叠效率前提下可扩展至多头架构。

**3) 论文作用：** 该图落在文末 Efficiency/Systems 章节，是支撑"mHC 实际可部署"的核心工程证据，承接前文算法推导，为实践落地与训练成本对比提供调度层依据。
*caption: Communication-Computation Overlapping for mHC. We extend the DualPipe… ｜ 论文 [[hc-manifold-constrained-hyper-connections]] ｜ arxiv 见 MD 元信息*

### HC: Manifold-Constrained Hyper-Connections — Fig.5 (p.12)
![[assets/crops/hc-manifold-constrained-hyper-connections-fig05.png]]
> [!tip] 【图文联合解读】图5在27B模型、5万步内比较Baseline、HC与mHC。左图以Baseline损失差为0；mHC由约−0.06回升至−0.021，HC回升更快、约至−0.015。右图mHC梯度范数由约0.13缓降至0.04，明显低于在0.09–0.18间剧烈波动并多次触及0.20的HC，且后期趋近Baseline。说明流形约束可抑制梯度爆炸、提升训练稳定性，同时维持更低损失；该图是mHC稳定性设计与后续性能实验之间的关键验证。
*caption: Training Stability of Manifold-Constrained Hyper-Connections (mHC). This figure… ｜ 论文 [[hc-manifold-constrained-hyper-connections]] ｜ arxiv 见 MD 元信息*

### HC: Manifold-Constrained Hyper-Connections — Fig.6 (p.13)
![[assets/crops/hc-manifold-constrained-hyper-connections-fig06.png]]
> [!tip] 【图文联合解读】**图6(b) Token Scaling Curve 解读**

**对象与数据**：图(b)为双面板折线图，横轴为FLOPs（≈1–5×10²¹）。左面板"Absolute Loss Gap"以Baseline归零为参考，mHC曲线从约-0.024单调上升至-0.015；右面板"Relative Loss Ratio"中Baseline锁定100%，mHC由98.8%升至99.15%，两者均表明mHC在各token预算下Loss始终更低。

**技术结论**：mHC的增益在数据规模维度上**持续存在但略有收敛**，说明Baseline仅能通过更多token部分追赶，无法反超，验证了mHC改进的稳健性。

**论文作用**：与(a) Compute Scaling Curve互为补充，从**参数量（3B→27B）**与**数据量**两轴联合证明mHC在全规模上可扩展，是支撑其"适用于生产级预训练"主张的核心缩放性证据。
*caption: Scaling properties of mHC compared to the Baseline. (a) Compute Scaling Curve.… ｜ 论文 [[hc-manifold-constrained-hyper-connections]] ｜ arxiv 见 MD 元信息*

### HC: Manifold-Constrained Hyper-Connections — Fig.7 (p.14)
![[assets/crops/hc-manifold-constrained-hyper-connections-fig07.png]]
> [!tip] 【图文联合解读】**(1) 核心对象与数据**
(a) 单层映射（0–60层）：前向信号增益 $\mathcal{P}_{M^{res}}(\mathcal{H}_l^{res})$ 严格为 1.0（灰线平直）；反向梯度增益 ≈1.03–1.05（蓝线），全程近乎水平。
(b) 复合映射：前向乘积 $\prod_{i=1}^{l}\mathcal{P}_{M^{res}}(\mathcal{H}_i^{res})$ 仍恒为 1.0；反向梯度乘积自 ≈1.1 上升，在第 20–25 层达峰值 ≈1.65，再缓降至 ≈1.0。

**(2) 技术结论**
流形约束保证前向信号幅度逐层精确归一，无衰减也无爆炸；但反向梯度经多层累积可放大约 65%，存在明显爆炸隐患——证明 mHC 对前向与反向路径并非对称稳定。

**(3) 在论文中的作用**
以可量化的传播曲线诊断 mHC 的稳定性边界，揭示反向链路缺乏对偶约束，从而为后续讨论残差式梯度修正、双向流形约束或初始化策略提供实证依据。
*caption: Propagation Stability of Manifold-Constrained Hyper-Connections (mHC). This… ｜ 论文 [[hc-manifold-constrained-hyper-connections]] ｜ arxiv 见 MD 元信息*

### HC: Manifold-Constrained Hyper-Connections — Fig.8 (p.14)
![[assets/crops/hc-manifold-constrained-hyper-connections-fig08.png]]
> [!tip] 【图文联合解读】**图8图文联合解读**

图8对比HC（上行）与mHC（下行）在27B模型中的单层映射$\mathcal{H}^{res}$与复合映射$\prod$。**HC**的$\mathcal{H}_{60}^{res}$内部元素达±6.77，复合映射$\prod_{i=1}^{60}\mathcal{H}_{61-i}^{res}$元素飙至±142与±509，传播严重失稳；而**mHC**各层值稳定于[0,1]区间，行列和均≈1.0。原文据此论证流形约束显著提升信号/梯度传播稳定性，是验证mHC缓解深层网络表征爆炸/坍塌核心动机的关键可视化实证。
*caption: Visualizations of Learnable Mappings. This figure displays representative single-… ｜ 论文 [[hc-manifold-constrained-hyper-connections]] ｜ arxiv 见 MD 元信息*

### Linear Optimal Topic Transport for Document Similarity — Fig.1 (p.7)
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-fig01.png]]
> [!tip] 【图文联合解读】**图1 解读**

**1) 核心对象与数据**：该柱状图比较了10种文档表示/距离方法（nBOW、SIF、Cosine、RWMD、HOfTT、HOTT、WMD-T20、LOTT、LOTT-5、LOTT-10）在6个数据集上的k-NN分类平均测试误差（%）。其中LOTT系本文提出的三种变体（含不同rank或embed层选择）。

**2) 关键结论**：在ohsumed上LOTT表现偏弱（52%），但加锚点增强的LOTT-5/10降至48/46，差距收窄；而在其余5个数据集上，LOTT/LOTT-5/10均处于最低误差区间，例如bbcsport LOTT-10=7%（仅略低于WMD-T20的6%），classic LOTT-10=5%为该数据集最优，amazon/reuters LOTT-10=11/9%与WMD-T20持平或更优。整体说明LOTT系列在跨数据集下与WMD-T20、RWMD这一类SOTA基线具有可比或更优的k-NN表现，验证其在标准距离度量路线下的有效性。

**3) 在论文中的作用**：该图为方法实验链路的**主结果展示**，为后续段落所引"影响CLASSIC均值误差"等更细致的分析提供全景对比，支撑本文关于"线性最优主题传输可作为文档相似度替代度量"的核心论断。
*caption: k-NN classification performance across datasets affects mean test error in the CLASSIC dataset. 531… ｜ 论文 [[linear-optimal-topic-transport-for-document-similarity]] ｜ arxiv 见 MD 元信息*

### Linear Optimal Topic Transport for Document Similarity — Fig.2 (p.8)
![[assets/crops/linear-optimal-topic-transport-for-document-similarity-fig02.png]]
> [!tip] 【图文联合解读】该图以 2×2 网格对比 LOTT、SBERT、HOTT、nBoW 四种方法在 CLASSIC 数据集（4 类、CACM/MED/CRAN/CISI）上的 t-SNE 二维投影。直观可见：LOTT 与 HOTT 形成颜色分明、类内紧凑的簇群；SBERT 各类有重叠；nBoW 散点几乎混为一体。原文借此论证 LOTT 嵌入具备良好的语义结构，类内一致性与类间分离度均优，为文档相似度度量提供可解释的表征依据，支撑其在主实验中的优越性。
*caption: t-SNE on CLASSIC… ｜ 论文 [[linear-optimal-topic-transport-for-document-similarity]] ｜ arxiv 见 MD 元信息*

### Root Mean Square Layer Normalization — Fig.1 (p.1)
![[assets/crops/root-mean-square-layer-normalization-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(b)横轴为训练时间(0–160分钟)，纵轴为Loss(4–10)，展示GRU-RNNSearch前10k步的两条曲线：蓝色Baseline最终约6.0，橙色LayerNorm约4.5；在约35分钟同一训练步处，Baseline=7.0，LayerNorm=5.9，损失差1.1。

原文借此论证：LayerNorm带来的加速收敛主要来自**缩放不变性**而非均值中心化（re-centering invariance），因为均值归一化并不降低隐藏状态或梯度方差。作者据此提出RMSNorm仅保留缩放项即可达到相近甚至更优效果。

该图作为论文动机起点，连接Table 1的不变性分析，推动RMSNorm作为更轻量替代方案的提出与后续实验验证。
*caption: One major feature of LayerNorm that is widely regarded as contributions to the stabilization is its re-centering invariance property: the summed input… ｜ 论文 [[root-mean-square-layer-normalization]] ｜ arxiv 见 MD 元信息*

### Root Mean Square Layer Normalization — Fig.2 (p.6)
![[assets/crops/root-mean-square-layer-normalization-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：Figure 2 为 RNNSearch 模型在 newstest2013 上的验证集 SacreBLEU 收敛曲线，横轴为训练步数（×30k，0–50），纵轴为 Valid BLEU（0–25），共五条曲线。L2-Norm（红）起步最低、收敛最慢，最终约 22；Baseline（蓝）起步约 15，收敛缓慢；LayerNorm（橙）、RMSNorm（绿）、pRMSNorm（紫）均在 ~5 步内快速攀升至 23–24 平台。

2）**关键结论**：RMSNorm/pRMSNorm 在保持与 LayerNorm 相当收敛速度的同时，达到最高的终端 BLEU，验证其在 NMT 任务中作为轻量归一化方案的有效性。

3）**论文作用**：作为支撑实验，与 Table 1 等 WMT 测试集结果互证，强化"RMSNorm = 可去均值重中心化的 LayerNorm"这一核心论点。
*caption: SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented accord- ing to Nematus [25] in Tensorﬂow.… ｜ 论文 [[root-mean-square-layer-normalization]] ｜ arxiv 见 MD 元信息*

### Root Mean Square Layer Normalization — Fig.3 (p.7)
![[assets/crops/root-mean-square-layer-normalization-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 3）：**

**1) 核心对象与数据：** 单线折线图，x 轴为 pRMSNorm 的标量超参数 p（%），在约 10%–100% 区间以 10% 步长扫参；y 轴为 RNNSearch（TF 版 Nematus）在 newstest2013 验证集上的 SacreBLEU，刻度 22–25。

**2) 关键结论：** 蓝色曲线整体近似水平，全 p 区间 BLEU 集中在 23.9–24.1 之间，最大波幅约 0.5 分，仅在 p≈90% 处出现一次浅凹（≈23.6），其余波动 ≤0.1 分。这直接说明 pRMSNorm 对 p 取值**极不敏感**，基本"免调参"。

**3) 在论文中的作用：** 作为超参数鲁棒性消融，与正文中 RMSNorm 与 LayerNorm 的精度/速度对比互为补充，支撑核心主张——pRMSNorm 是一种**即插即用、性能无损、对超参宽容**的轻量化归一化替代方案。
*caption: SacreBLEU score on new- stest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorﬂow-version Ne- matus, and change p by a step size of 10%.… ｜ 论文 [[root-mean-square-layer-normalization]] ｜ arxiv 见 MD 元信息*

### Root Mean Square Layer Normalization — Fig.4 (p.7)
![[assets/crops/root-mean-square-layer-normalization-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象与数据：** 图示newstest2013验证集上SacreBLEU随训练步数（0–30×30k）的变化曲线。对比两条曲线——LayerNorm（蓝）从约1缓慢爬升至约4，几乎持平；RMSNorm（橙）从约4稳步上升至约16，全程领先且差距持续扩大。

**关键论证结论：** 当初始化中心为0.2（非零偏移）时，RMSNorm显著优于LayerNorm。这是因为RMSNorm去掉了LayerNorm中的re-centering（均值中心化）步骤，不强制将输入拉回零均值，因此对初始化偏移具有更强的鲁棒性，避免了训练塌陷。

**在论文中的作用：** 该图作为"初始化敏感性"实验的关键证据，与Figure 2/3共同支撑论文核心主张——RMSNorm在保留re-scaling的同时简化re-centering，不仅计算更高效，还在非标准初始化下保持稳定性能，是LayerNorm的可行替代方案。
*caption: SacreBLEU score curve of Layer-… ｜ 论文 [[root-mean-square-layer-normalization]] ｜ arxiv 见 MD 元信息*

### Root Mean Square Layer Normalization — Fig.5 (p.8)
![[assets/crops/root-mean-square-layer-normalization-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图5展示了Attentive Reader模型上六种归一化方法的验证错误率收敛曲线（约300k训练步）：Baseline（蓝）收敛缓慢，300k步后错误率仍约0.48；BatchNorm-LSTM（绿）较慢；LayerNorm（红）、BatchNorm-Everywhere（橙）、RMSNorm（紫）、pRMSNorm（棕）在约50k步即收敛至≈0.5。结合表6，各方法每0.1k步耗时为：LayerNorm 392s、RMSNorm 333s（节省15.1%）、pRMSNorm 330s（节省15.8%）。

论文以此论证关键结论：**RMSNorm与LayerNorm收敛性能相当，但计算开销显著降低**——通过省略均值中心化、重计算缩放不变性，简化了归一化计算。该实验在整体方法链中起核心验证作用：证明RMSNorm在保持训练稳定性的同时，实现了效率与精度的最佳平衡，为后续在Transformer、机器翻译等大规模任务中的推广提供了实证依据。
*caption: Error rate on validation set for the attentive reader model.… ｜ 论文 [[root-mean-square-layer-normalization]] ｜ arxiv 见 MD 元信息*

### Root Mean Square Layer Normalization — Fig.6 (p.8)
![[assets/crops/root-mean-square-layer-normalization-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

Figure 6 以三幅子图（R@1、R@5、R@10）展示 Order-Embedding 模型在 COCO 跨模态检索任务中验证集 Recall@K 随训练步数（×0.3k，0–250）的演化。蓝色 Baseline 曲线在三项指标上均明显落后（R@1≈39 vs. 归一化组≈41；R@10≈87 vs. ≈89），收敛更慢且终值更低；RMSNorm（绿）与 pRMSNorm（红）自训练早期即领先 LayerNorm（橙），三者最终趋于相近，但 RMSNorm/pRMSNorm 峰值与稳定性略优。

原文借此论证：**在 OE 跨模态场景下，RMSNorm 收敛速度与最终性能均不逊于 LayerNorm，且远胜无归一化基线**，呼应 Figure 5 的"精度可比"与 Table 6 的"RMSNorm 比 LayerNorm 快约 15%"。

在论文整体实验链路中，该图与 §6.3 的 Image-Caption Retrieval 共同构成"质量—效率"双重证据链：既证明 RMSNorm 在跨模态检索中提供与 LayerNorm 同等收敛质量，又凸显其计算效率优势，从而支撑全文核心主张——RMSNorm 是 LayerNorm 的有效替代。
*caption: Recall@K values on validation set for the order-embedding models. worse than RMSNorm. Although in Figure 5 the performance of RMSNorm and LayerNorm is… ｜ 论文 [[root-mean-square-layer-normalization]] ｜ arxiv 见 MD 元信息*

### Root Mean Square Layer Normalization — Fig.7 (p.13)
![[assets/crops/root-mean-square-layer-normalization-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图7对比RNNSearch在newstest2013上50×30k步内的SacreBLEU收敛曲线：Baseline（蓝）起点最低（~5 BLEU）且缓慢爬升至~22；LayerNorm（橙）起步即达~17，快速收敛至~23；RMSNorm（绿）、pRMSNorm（红）、WeightNorm（紫）均从~10–12起步，最终收敛于~22–23，性能与LayerNorm基本持平。

该图用于论证：**RMSNorm及其参数化版本pRMSNorm能达到与LayerNorm相当的翻译质量**，而无需计算均值与再平移，从而以更低的计算开销获得相近效果。这为论文核心主张——RMSNorm可作为LayerNorm的简洁替代——提供了在NMT任务上的直接实验支撑，是方法验证链路中的关键证据之一。
*caption: SacreBLEU score curve over train- ing steps on newstest2013 (devset) for the RNNSearch. Models are trained with Nema- tus in Theano.… ｜ 论文 [[root-mean-square-layer-normalization]] ｜ arxiv 见 MD 元信息*

### GQA: Training Generalized Multi-Query Transformer Models fro — Fig.1 (p.1)
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图1展示了从多头注意力（MHA）到多查询注意力（MQA）的参数转换流程。左侧为H个独立的Key投影矩阵（K₁…K_H），每个维度为d_model×d_h；经中间"Mean Pool"操作后，合并为右侧单一的Key投影K_MQ（仍保持d_model×d_h）。

**论证结论**：通过将所有头的K/V投影矩阵逐元素取均值，可将H份独立的K/V头压缩为1份共享参数，且输出维度不变。该操作无额外训练即可完成，实现了从MHA到MQA的参数无缝降维。

**论文作用**：作为全文核心方法"训练式转换"的可视化基础，说明了GQA作为一种通用化形态——只需调整共享头数，即可平滑插值于MHA与MQA之间，是后续初始化策略与实验分析的理论前提。
*caption: Overview of conversion from multi-head to multi-query attention. Key and value projection matri- ces from all heads are mean pooled into a single head… ｜ 论文 [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] ｜ arxiv 见 MD 元信息*

### GQA: Training Generalized Multi-Query Transformer Models fro — Fig.2 (p.2)
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig02.png]]
> [!tip] 【图文联合解读】图示三种注意力机制的Q/K/V头配置对比：左Multi-head（H=8）每查询头独立配独立K/V头（8个K、8个V）；右Multi-query仅1个K、1个V头被8个查询共享；中间加粗的Grouped-query将8个查询头分为4组，每2查询共享1个K/V头（共4个K/V）。原文借此论证：GQA是MHA与MQA之间的插值方案，在保留多头表征能力的同时显著降低K/V显存与解码计算开销。该图为论文核心方法奠定结构基础——将预训练MHA checkpoint只需少量额外步（比例α）即可转换/微调为GQA模型，从而兼顾质量与推理效率。
*caption: Overview of grouped-query method. Multi-head attention has H query, key, and value heads. Multi-query attention shares single key and value heads acro… ｜ 论文 [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] ｜ arxiv 见 MD 元信息*

### GQA: Training Generalized Multi-Query Transformer Models fro — Fig.3 (p.3)
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig03.png]]
> [!tip] 【图文联合解读】**图3图文联合解读：**

图3散点图展示四模型的速度-性能权衡：MHA-Large(≈0.4ms, 46.0)、MQA-XXL(≈0.3ms, 46.6)、GQA-XXL(≈0.3ms, 47.2)、MHA-XXL(≈1.5ms, 47.3)。GQA-XXL以MQA级推理速度取得接近MHA-XXL的质量，且比后者快约5倍，构成Pareto最优折中。

原文借此论证：经5%继续训练的MQA在速度-质量权衡上优于MHA-Large，GQA则同时逼近MHA-XXL的性能并保留显著的速度增益。该图是论文实验链路的核心可视化证据，验证"uptraining"方法将MHA检查点高效转化为GQA的可行性——在不牺牲质量的前提下大幅提升推理效率，支撑GQA作为实用注意力替代方案的核心论点。
*caption: Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality and faster speed than MHA-Large, and GQA achieves even better performanc… ｜ 论文 [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] ｜ arxiv 见 MD 元信息*

### GQA: Training Generalized Multi-Query Transformer Models fro — Fig.4 (p.4)
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示T5-Large以α=0.05上训练至MQA时，三种checkpoint转换方法的性能对比：Mean池化约55.6、First取首头约55.5、Random随机初始化约55.2。

**技术结论**：Mean池化最优，Random最差但绝对差距仅约0.4，说明仅需5%上训练，从MHA checkpoint转换即可获得接近最优的MQA性能，验证转换策略而非从零训练的有效性。

**论文作用**：为论文核心主张——MHA checkpoint可通过轻量键值头转换快速得到高性能MQA/GQA——提供方法选型依据，支撑后续uptraining实验链路设计与维度消融的合理性。
*caption: Performance comparison of different check- point conversion methods for T5-Large uptrained to MQA with proportion α = 0.05. ‘Mean’ mean-pools key and … ｜ 论文 [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] ｜ arxiv 见 MD 元信息*

### GQA: Training Generalized Multi-Query Transformer Models fro — Fig.5 (p.4)
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig05.png]]
> [!tip] 【图文联合解读】## 图文联合解读

**核心数据**：横轴为 uptraining 比例 α（0/5%/10%），纵轴为模型性能。MHA 基线（粉色虚线）恒定约 57.5；GQA-8（蓝方块）从 α=0 时约 56.7 升至 α=10% 时约 57.4；MQA（橙三角）从约 54.0 急升至 5% 时的约 57.0，随后趋于平缓。

**关键结论**：α=0 时 MQA 落后 MHA 约 3.5 分，而 GQA-8 仅落后约 0.8 分，说明 GQA 在"无重训练"状态下就能很好地逼近 MHA 质量；仅需 5% uptraining，两者即获大幅提升且收益递减，证明极小额外成本即可恢复性能。

**论文作用**：作为 uptraining 有效性的实证核心，支撑"用 GQA 替代 MHA 是推理效率与质量最优折中"的核心主张，使论文方案具备实际部署可行性。
*caption: Performance as a function of uptraining pro- portion for T5 XXL models with MQA and GQA-8.… ｜ 论文 [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] ｜ arxiv 见 MD 元信息*

### GQA: Training Generalized Multi-Query Transformer Models fro — Fig.6 (p.4)
![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig06.png]]
> [!tip] 【图文联合解读】**图6图文联合解读：**

图6展示GQA-XXL在输入2048、输出512条件下，单样本推理时间（秒）随分组数1–64的变化，对照MHA（≈2.5s）、MQA（≈0.5s）两条基线。GQA在1–8组时与MQA几乎重合（≈0.5s），16组0.6s，32组0.8s，64组陡升至≈2.5s，逼近MHA。

结论：分组≤8几乎无推理开销，≥32则效率优势消失，证实8组是兼顾表达力与速度的最佳折中。该图为论文核心方法——"由MHA检查点转换少量分组GQA"——提供推理成本实证，验证转换后模型在保留多头能力的同时获得近似MQA的推理速度。
*caption: Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups add… ｜ 论文 [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] ｜ arxiv 见 MD 元信息*

### Qwen2.5-VL Technical Report — Fig.1 (p.3)
![[assets/crops/qwen2-5-vl-technical-report-fig01.png]]
> [!tip] 【图文联合解读】图示Qwen2.5-VL架构：Vision Encoder支持原生分辨率与动态FPS采样（0.5/1/2FPS），视频宽644、时长8s，经Conv3D(2×14×14)窗口划分与Conv2D 2×时序合并后映射成644/1288/2576可变长token；ViT块由Window Attention×M+Full Attention×1构成，配RMSNorm与SwiGLU FFN；3D MRoPE沿时间轴对齐绝对时间ID(0–15s)，最终输入Qwen2.5 LM Decoder。原文借此论证三大核心：原生分辨率保细节、动态采样提效率、绝对时间编码增强时序/时刻定位，作为全篇方法总纲，为后续视频理解与时间定位实验提供架构基线。
*caption: The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a language model decoder to process multimodal inputs, including images … ｜ 论文 [[qwen2-5-vl-technical-report]] ｜ arxiv 见 MD 元信息*

### DeepSeek-V3 Technical Report — Fig.5 (p.12)
![[assets/crops/deepseek-v3-technical-report-fig05.png]]
> [!tip] 【图文联合解读】# Figure 5 深度解读

**核心对象与结构**：图示展示 **8 个 PP（流水线并行）rank × 20 个 micro-batch** 的 DualPipe 双向调度时序。绿色方格代表正向（forward）计算，橙色代表通信（communication），蓝色代表反向（backward）计算，白色为空闲/bubble 时间。每个 PP rank 从两端同时接收 micro-batch，编号 2–9 的 micro-batch 对称分布于流水线两半，由黑色边框标注"通信-计算重叠"单元。

**论证的关键技术结论**：双向流水线使大部分通信（橙色）可被计算（绿色/蓝色）完全覆盖，显著压缩了传统单向流水线的 bubble 区；只要保持计算-通信比恒定，模型进一步扩展时仍可实现跨节点的 **细粒度专家并行（fine-grained EP）**，获得近零通信开销。

**在论文中的作用**：Figure 5 是 DeepSeek-V3 训练基础设施一节（p.12）的核心示意图，为 DualPipe 算法与跨节点 EP 协同设计提供可视化证据，支撑"大规模 MoE 训练近乎零开销"这一基础设施层面的关键声明。
*caption: It employs a bidirectional pipeline scheduling, which feeds micro-batches from both ends of the pipeline simultaneously and a significant portion of c… ｜ 论文 [[deepseek-v3-technical-report]] ｜ arxiv 见 MD 元信息*

### DeepSeek-V3 Technical Report — Fig.6 (p.15)
![[assets/crops/deepseek-v3-technical-report-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图中所见聚焦 Wgrad（权重梯度）通路：FP8 输入先经 ⊗ 矩阵乘、再在 **FP32** 下 Σ 累加，产出 Weight Gradient (FP32)；该梯度与 Master Weight（由 Optimizer States 以"**To BF16 / To FP32**" 回写更新）共同进入优化器；同时 Input、Output Gradient 均标注"**To FP8**"用于 Dgrad 计算。原文借该图论证：尽管 Linear 的 Fprop / Dgrad / Wgrad 三类 GEMM 均以 FP8 加速以降低算力与显存，但权重梯度在 **FP32** 累加、主权重以 BF16/FP32 高精度维护，从而保证 FP8 训练下的数值稳定性。

该图是 DeepSeek-V3 **混合精度 FP8 训练框架** 的核心架构图，承接前文 tile-wise / block-wise 量化策略，为后续消融实验与训练成本下降提供方法学依据。
*caption: Firstly, in order to accelerate model training, the majority of core computation kernels, i.e., GEMM operations, are implemented in FP8 precision. The… ｜ 论文 [[deepseek-v3-technical-report]] ｜ arxiv 见 MD 元信息*

### DeepSeek-V3 Technical Report — Fig.10 (p.48)
![[assets/crops/deepseek-v3-technical-report-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读**

该图展示 230B DeepSeek-V2 模型上 BF16 与 FP8 两种精度训练的 loss 曲线对比：横轴为已处理 token 数（0–~900B），纵轴为 loss（1.7–2.5），两条曲线全程几乎完全重合；右上角内嵌放大子图给出相对差 (FP8−BF16)/BF16 随训练步数的变化，振荡区间约在 ±0.5% 内。

原文借此论证：所提出的 FP8 混合精度框架（细粒度量化、累加精度保持等）可在不引入额外 spike 的前提下，逼近 BF16 基线的收敛行为，从而支撑"全程 FP8 训练无损"的核心结论。

在论文整体链路中，该图位于方法章节末尾，作为对底层训练基础设施（low-precision training framework）正确性的关键实证依据，为后续 V3 全栈 FP8 大规模预训练（14.8T tokens）的可行性提供直接经验支撑。
*caption: 48… ｜ 论文 [[deepseek-v3-technical-report]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.1 (p.1)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图1为二维散点图，横轴为8K上下文下的理论解码成本（0.05–0.10 USD），纵轴为激活参数量（0–50B）。Step-3以红星标于约(0.056 USD, 38B)，处于同激活参数规模下解码成本最低的位置；DSv3约(0.069, 37B)、Kimi K2约(0.066, 32B)均在其右上方，灰色阴影区域为GQA模型的Pareto前沿。原文借此论证：解码阶段因MFU低、推理模型thinking长，导致每token成本居高，Step-3通过系统协同设计打破了"高激活参数⇔高成本"的传统权衡，实现"大而省"。该图作为全文动机图，将"高激活参数×低解码成本"确立为Step-3的核心设计目标，为后续架构与推理系统共设计奠定论证基础。
*caption: The Pareto frontier of recent models regarding acti- vated parameters and decoding costs. The darker area is GQA models’ Pareto frontier. Note: Step-3… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.2 (p.6)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图2以双柱状图对比Step-3、DSv3、Qwen3 MoE、Qwen3 32B在H800、H20、A800、910B、AFD五种部署方案下的**每百万token理论解码成本**，分别对应8K（左）与32K（右）上下文。8K下Step-3成本约0.055–0.080，32K下AFD方案降至约0.13，**均显著低于Qwen3 32B（8K约0.083–0.197，32K约0.28–0.73）和DSv3**；AFD部署通过为Attention与FFN分别选用最优硬件，使各模型成本降至最低。

该图直接支撑论文核心论点——Step-3虽**激活参数最多（38B）**，但凭借模型-系统协同设计（AFD等），解码成本反而最低，验证了"大而经济"的设计主张，是论文方法链路中**实验验证**的关键证据。
*caption: With all the results shown, we make the following observations:… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.3 (p.6)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig03.png]]
> [!tip] 【图文联合解读】**图3 图文联合解读**

1. **核心对象与数据**：左图对比三种混合线性注意力模型在8K/32K/128K上下文下的KV cache大小（GB），Step-3从~0.3 GB线性增长至~4.1 GB，而Llama 4 M与MM M1在128K时分别达~7.2 GB与~6.0 GB。右图为H800上单token解码理论成本（USD），Step-3在128K时仅~0.70 USD，约为Llama 4 M（~1.13）的62%、MM M1（~1.02）的69%。

2. **关键结论**：Step-3凭借更激进的线性注意力层比例与更小的KV预算，在长上下文场景下KV占用与解码成本均显著低于MiniMax M1和Llama 4 Maverick，与Table 3（32K下每token算访开销）相互印证。

4. **论文作用**：作为"大而便宜"核心论点（affordable）的关键成本证据，量化支撑模型–系统协同设计在解码侧的经济性收益。
*caption: Second, the time spent on each layer will be largely unbal- anced – when running with long context, the full GQA layers consume much more time than th… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.4 (p.8)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig04.png]]
> [!tip] 【图文联合解读】**图4解读**

**① 核心对象与数据**：横轴为910B加速器上的三种场景，纵轴为单token成本（USD）。Pangu MoE（红色斜线）三场景依次为0.114 / 0.395 / 0.076 USD；Step-3（青色实心）依次为0.078 / 0.168 / 0.213 USD。

**② 关键结论**：两条曲线趋势完全相反——Step-3在解码场景全面更便宜（8K省约32%，32K省约57%），但训练反而贵约2.8倍；序列越长，Step-3的解码成本优势越显著。说明Step-3把成本预算从训练侧前移到解码侧。

**③ 论文作用**：以Pangu MoE为对照基线，定量验证Step-3"模型-系统协同设计"的核心理念——牺牲训练经济性以换取大规模MoE在长上下文解码时的可负担性，从而支撑全文"large yet affordable"的论证主线。
*caption: Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.5 (p.8)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig05.png]]
> [!tip] 【图文联合解读】**图5联合解读**

图示三种注意力设计在8K→32K解码下的算术强度轨迹，并叠绘H800/910B/A800/H20四类硬件roofline：
- **DSv3-MLA**：强度≈512（~1.1 GB / 590 GFLOPs），沿H800 ridge，**计算主导**；
- **Qwen3-GQA**：强度≈32（~3.1 GB / 100 GFLOPs），贴近H20，**访存主导**；
- **Step-3-MFA**（红星）：强度≈128（~1.0 GB / 130 GFLOPs），**精准落在910B(≈175)与A800(≈156) roofline的ridge交汇点**。

论文以此量化论证"硬件-算法协同"的核心结论：MFA相较DSv3 MLA**计算量降至约1/4**，相较Qwen3 GQA**访存量降至约1/3**，且在910B/昇腾等国产硬件上同样命中sweet spot。该图是Step-3"低成本大模型"系统级设计主张的**关键定量证据**，支撑全文硬件无关可部署的论证。
*caption: The compute and memory access of different atten- tion designs during decoding, including DSv3’s MLA, Qwen3… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.6 (p.11)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 6）**

**1) 图示结构（量化）**：左路Attention模块（Norm→Attn→Norm+残差）本地计算；中路由Norm→Router→Expert Combine本地完成，右路由TP gather/EP scatter→Expert Compute→TP scatter/EP gather置于远端专家池。隐藏状态以fp8经中间虚线跨域传输，回传bf16；Router下发expert distribution，Expert Combine回传TopK score。

**2) 关键技术结论**：FFN模块可依硬件与模型结构，自适应选择TP-only、EP-only或TP+EP混合并行部署，体现模块解耦的灵活性。

**3) 论文作用**：作为Step-3模型-系统协同设计中AFD（Attention/FFN Disaggregation）架构的核心示意图，奠定"注意力本地低延迟+专家远端弹性扩展"的设计思想，是后续讨论专家均衡、稳定性及整体成本-性能权衡的方法基础。
*caption: Module disaggregation in AFD architecture. FFN can be deployed in TP-only, EP-only, or a hybrid TP+EP way, depending on hardware and model architectur… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.7 (p.12)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**
左侧展示通信拓扑：8卡FFN实例与8卡Attention实例通过**Direct RDMA**实现1对1直连（GPU数量相等、无中间路由）。右侧为时间轴上的多阶段流水线：Layer0/Layer1各承载3个批次（D1–D3与D1'–D3'），FFN（顶行）与Attention（底行）交替执行；两者间存在两条非对称传输——FFN→Attention 采用 **bf16**（黄块1/2/3、1'/2'/3'），Attention→FFN 采用 **fp8**（棕色块）。

**2) 关键论证结论**
图文共同证明AFD架构通过：(a) 解耦Attention/FFN并直连以消除PCIe/NCCL瓶颈；(b) **非对称精度传输**（前向高保真、反向压缩）平衡精度与带宽；(c) 批次×层级二维流水，使通信与计算深度重叠，掩盖访存延迟。

**3) 在论文中的作用**
该图是AFD系统设计的核心机制图，作为前文MoE解码算力–带宽失衡问题与后续系统级硬件协同（cost-effective decoding）论证之间的桥梁，奠定"模型–系统协同"立论基础。
*caption: Communication topology and the multi-stages pipeline of the AFD architecture.… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.8 (p.13)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig08.png]]
> [!tip] 【图文联合解读】**图联合解读：**

**核心对象与结构：** 图示StepMesh为AFD设计的双实例流水线。左侧Attention实例含CPU三线程（NetRecv Thread经RDMA PollCQ收张量、Main Thread执行Wait→Launch Attention→PushPull、NetSend Thread做Kernel Sync与RDMA PostSend）与GPU（Attention Kernel将Activation Tensors转为Token Tensors）；右侧FFN实例结构对称（GPU跑FFN Kernel反向产出Activation Tensors），两实例经底部RDMA NIC交叉互连。

**关键结论：** 通过Recv/Send/Main三线程并行，Main Thread Wait与Launch Kernel期间网络收发被Kernel Sync完全隐藏，实现通信-计算全重叠；Token与Activation张量在Attention↔FFN间直接RDMA交换，无中心调度。

**论文作用：** 该图为AFD（Attention-FFN解耦）提供系统级实现证据，支撑论文"大模型廉价协同解码"的整体论点——异构低成本节点按Attention/FFN分工组网即可承担超大模型推理。
*caption: StepMesh communication workflow tailored for AFD.… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.9 (p.13)
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig09.png]]
> [!tip] 【图文联合解读】## Figure 9 图文联合解读

**1) 核心结构（三层架构）：**
- **顶层 API 层**：左侧 AFTensorWorker API 封装 `Wait`、`PushPull`（供 attention 实例）；右侧 AFTensorServer API 封装 `GetBatch`、`Respond`（供 FFN 实例）。
- **中间核心层**：StepMesh Core，含 NetSend/NetRecv 线程，负责跨设备张量传输调度。
- **底层后端层**：分两条路径——Network API（RDMATransport → RDMA NIC）与 Accelerator API（CPUBackend / GPUBackend / xPUBackend → CPU / GPU / xPU 设备）。

**2) 关键结论：**
该图论证 StepMesh 将张量通信逻辑与底层硬件解耦，通过 Attention-FFN 解耦后两套对偶 API（PushPull 与 GetBatch/Respond）实现异构多加速器（CPU/GPU/xPU）间的 RDMA 高效协同。

**3) 论文链路作用：**
作为"模型–系统协同设计"中的**系统栈组件**，StepMesh 与 MFA 注意力、MoE 路由等算法级创新配套，支撑论文"大规模但低成本解码"的核心主张。
*caption: StepMesh framework for multiple accelerators. AF-… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.1 (p.2)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图示SGLang三层架构：**前端**(SGLang Client，含Sec.2语言原语extend/gen/fork) → **Interpreter**(黄色调度器) → **后端Runtime**(蓝色，集成Sec.3 RadixAttention、Sec.4 压缩FSM、Sec.5 API推测执行)。

该图论证的核心结论：以**嵌入式DSL前端+流式Interpreter+优化Runtime**的分层设计，将原语依赖解析、KV缓存复用、状态机压缩统一抽象；Interpreter记录数据依赖使独立原语并行批执行，前缀自动命中RadixAttention。

作为论文方法链路总纲图(Fig.1)，它在Sec.1结尾铺垫后三章技术细节(§2原语→§3缓存→§4 FSM→§5推测)，并支撑§6实验：在HumanEval/MTBench等基准上较vLLM/Guidance/LMQL实现最高6.4×加速。
*caption: System architecture: An interpreter executes language primitives with optimized runtime.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.2 (p.3)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig02.png]]
> [!tip] 【图文联合解读】# Figure 2 图文联合解读

**1) 核心对象与结构**

该图为代码注释图，展示 SGLang 中多维作文评判器（multi-dimensional essay judge）的完整实现，调用 `gen`、`select`、`fork` 等原语（红色高亮），由右侧黄色箭头逐行标注功能：
- **入口**：`run` 函数——运行 SGLang 程序，支持 chat 模板与多模态输入；
- **分支（branch）**：`fork()` 并行触发多个 `gen` 调用，按"dimension"逐项评判；
- **求解（solve）**：单维度调用采用 **KV Cache Reuse**（Sec. 3）复用前文 prompt；用 `select` 从候选选项中选最高概率答案；
- **合并（merge）**：汇总各维度 JSON 结果，并采用 **快速约束解码**（Sec. 4，正则 `[ABCD][+-]?\s`）与 **API 投机执行**（Sec. 5）输出最终字母等级与摘要。

**2) 关键论证结论**

图示证明：仅用 7 个原语即可将论文 [40] 的 branch-solve-merge 提示范式实现为高效程序，且 SGLang 的三类运行时优化（KV cache 复用、约束解码、投机执行）可无缝嵌入。

**3) 在论文链路中的作用**

该图作为"方法示例"，承上（Sec. 2 编程模型）启下（Sec. 3–5 各项优化），直观体现 SGLang 用高层原语 + 自动优化替代手工工程，是后续性能基准（Figure 3）与消融实验的应用载体。
*caption: The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLan… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.3 (p.5)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示9个时间点RadixAttention基数树的演化：根节点出发，两类聊天分支共享系统提示"You are a helpful assistant."公共前缀；少样本链（Question1–Answer1…Question3）与自一致性多采样（"This is…/Let us…/We can…/To solve…"）依次挂载为子分支。节点c、j等在(5)(8)(9)经LRU驱逐（橙色×标记）。

**技术结论：** 基数树实现自动前缀共享KV缓存，无需手动提示管理；LRU策略保证热点prompt常驻、冷分支及时淘汰。

**论文作用：** 作为SGLang运行时核心机制的可视化证据，为后续提示复用吞吐量与延迟基准实验提供机制基础。
*caption: Examples of RadixAttention operations with an LRU eviction policy, illustrated across nine time points. The figure demonstrates the dynamic evolution … ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.4 (p.6)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig04.png]]
> [!tip] 【图文联合解读】**图(a)**：Normal FSM为regex `{"summary":_`构建**12状态(0-11)**线性结构，每个状态对应单个字符`{ " s u m m a r y " : _`；**(c)**：解码过程显示FSM校验与LLM前向频繁交替——每token（`{"`、`summary`、`":`、`_`）均触发**独立LLM调用**，调度粒度过细。

**关键结论**：原文借助Normal FSM对照Compressed FSM论证——后者通过合并具有相同未来转移的等价状态节点，把逐字符校验压缩为多 token批量匹配，从而**单次LLM解码可同时校验多字符**，显著降低调度与前向开销。

**作用**：作为第3节"压缩FSM等价性"(Theorem 3.1)的可视化证据，与算法1的cache-aware调度共同构成"问题刻画→压缩优化→延迟基准"方法链路中的核心论据，支撑sglang高效结构化生成的性能优势。
*caption: The decoding process of normal and compressed FSMs (the underscore _ means a space). requests by matched prefix length and prioritize requests with lo… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.5 (p.7)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) 图为 Llama-7B 上 6 个结构化生成任务（LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat 短/长、DSPy RAG）的归一化吞吐条形对比。橙色条（SGLang）在全部任务上柱高均显著领先蓝色（Guidance）与绿色（LMQL）基线；LLM Judge 与 DSPy RAG 上领先幅度最大（近 4–5 倍），Multi-Turn Chat(long) 上三者差距最小。

2) 原文以此论证：含两次 `gen` 的 pattern 中，朴素做法需对同一 `context` 重复支付输入 token 费用；而 SGLang 借助推测执行复用首次调用的 prefix 并继续生成，从而在跨任务场景下稳定获得高吞吐增益。

3) 该图是论文核心实验证据，将运行时优化（推测执行、前缀共享/RadixAttention）与真实结构化 LM 程序效率挂钩，支撑"DSL 前端 + 高效执行后端"整套方法的有效性结论。
*caption: Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n").… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.6 (p.8)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：横轴为 6 个 Llama-7B 工作负载（LM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat 短/长、DSPy Pipeline RAG），纵轴为归一化延迟。橙色（SGLang）、蓝色（Guidance）、灰色（LMQL）、绿色（另一基线）四组柱状对比，前两项三项齐全，后四项 Guidance/LMQL 因不支持批处理与并行而被剔除。

2）**关键结论**：在 LM Judge 与 HellaSwag 上，LMQL 延迟达 SGLang 的约 2.5–3 倍；Multi-Turn Chat（短/长）与 DSPy Pipeline 上，绿色基线延迟也明显高于 SGLang。SGLang 在全部 6 项基准中延迟最低。

3）**论文作用**：该图作为性能收尾证据，配合 Figure 7（Mixtral-8x7B）证明 SGLang 的 RadixAttention 与前端优化在分类、Agent、CoT、结构化输出、多轮对话、RAG 等典型结构化 LLM 程序场景下均具备跨负载、跨模型规模的稳定加速优势。
*caption: Normalized latency on Llama-7B models. Lower is better. MMLU… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.7 (p.8)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig07.png]]
> [!tip] 【图文联合解读】该图展示 Mixtral-8x7B 启用张量并行后，SGLang 在 5 类基准（MMLU、ReAct Agents、Generative Agents、Tree of Thought、Skeleton of Thought）上的归一化吞吐：SGLang 均归一为 1.0；对手在 MMLU≈0.12、ReAct Agents≈0.10 落后最显著，Tree of Thought≈0.25 差距明显，Generative Agents 与 Skeleton of Thought≈0.72 差距最小。

原文借此论证：SGLang 的前端优化与运行时协同在 MoE + 张量并行场景下仍稳定胜出，优势在含控制流、多轮交互的 Agent 与 CoT 负载上尤为突出。

作用：补充 Figure 6（Llama-7B），证明吞吐优势可跨模型规模与并行策略复现，强化方法在大模型场景下的通用性结论。
*caption: Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better. result from KV cache reuse, the exploitation of parallelism wi… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.8 (p.9)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图8(c)为RadixAttention消融实验的柱状图，横轴为四个基准负载（LLM Judge、Tree of Thought、MMLU、Multi-Turn Chat短对话），纵轴为归一化性能（0–1），对比七种配置：无缓存、无树结构、FCFS调度、随机调度、无前端并行、无前端提示、全优化（Full Optimization，橙色）。

**关键结论**：全优化方案在四个负载上均接近1.0归一化值，显著优于任一单一组件关闭情形；其中"无缓存"在LLM Judge与MMLU上退化最严重（约0.15–0.40），"无前端并行/提示"在Tree of Thought上影响明显（约0.35），证实radix缓存、树状调度、前端并行与提示各自独立贡献性能。

**论文作用**：该消融图支撑SGLang核心设计——RadixAttention缓存+前端DSL优化是端到端加速的必要组成部分，缺一不可，为整体性能优势提供分项归因证据。
*caption: (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.9 (p.14)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig09.png]]
> [!tip] 【图文联合解读】**图9图文联合解读**

该图以四种典型 LLM 编程模式展示 KV cache 共享结构：(a) Few-shot——三个 Prompt 共享相同的 "Few-shot examples" 前缀；(b) Self-consistency——同一 Question 派生出三条独立 Answer；(c) Multi-turn chat——Chat History 随轮次累积延长，每轮仅追加新的 Q/A；(d) Tree-of-thought——沿分支路径共享逐层 Search History。蓝/绿/黄三色分别标注可共享 prompt、非共享输入、非共享输出。

论文借此论证：在结构化 LM 程序中**存在大量相同前缀**（few-shot 示例、对话历史、搜索路径），KV cache 复用空间显著。该图为 SGLang 核心机制 **RadixAttention（前缀共享调度）** 提供具体应用场景的动机支撑，是连接"LM 程序结构特性"与"系统级缓存优化"的关键概念桥梁。
*caption: KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable m… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.10 (p.17)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图上部分给出一个 JSON 结构化正则（含 `name:[\w\d\s]+`、`age:[0-9]+`、`house` 为 Gryffindor/Slytherin/Ravenclaw/Hufflepuff 四选一枚举）；下部分"Decoding Status"列出对"填 Harry Potter 信息"提示符的候选下一 token：仅小写 "age" ✓ 被接受，而 "Age" 因大小写不符被 ✗、"hou" 因当前路径无法延伸到合法 token 被 ✗；箭头 "Decode + FSM" 指向右侧 "Constrained Decoding" 输出。

**技术结论：** 原文借此论证——regex 经自动编译为 FSM 后，在每一步解码通过对 logit 施加掩码屏蔽与模式不符的 token，使生成结果严格匹配 JSON 字段名、字符集与枚举约束，无需后处理重解析。

**链路作用：** 该图位于"regex→FSM→约束解码"方法链路可视化末端，为后续 JSON/HTML/SQL 等结构化输出基准的正确性与吞吐实验提供直观原理支撑，强调 FSM 路径相对逐 token 语法校验的效率优势。
*caption: Example of how regex is converted into FSM and how FSM guides the decoding process.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.11 (p.18)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]]
> [!tip] **SGLang论文 Figure 11 深度解读**

**1) 图类型**
**架构/流程对比图**（不是结果图）。属于"机制示意"类别：用 token 级别的展开图，对比两种 FSM-guided 解码方式在结构化生成中的执行路径差异。**

**2) 核心内容**

**组件构成**
- **左上图（Jump-Forward Decode With Compressed FSM）**：上半部为 Prefill（绿色块：`Please fill in the following information about Harry Potter.`），其后跟一连串橙色块（Jump-Forward 一次性跳过的 token 序列）和少量蓝色 Decode token。
- **左下图（Normal Decode With FSM）**：相同 Prefill 后，逐 token 展开的"密集蓝块"序列，每个结构化 token 都被独立解码。
- **右栏（Generated JSONs）**：两种方式最终输出的等价 JSON 内容：
  ```
  {
    "name": "Harry",
    "age": 15,
    "house": "Gryffindor"
  }
  ```

**关键 Token 流对比**
| 元素 | Compressed FSM（Jump-Forward） | Normal FSM |
|---|---|---|
| `{` `"name":"` `Harry` `"age":` `15` `"house":` `"Gryffindor"` `}` | 橙色块一次性 jump | 逐 token 蓝色解码 |
| 关键"内容 token" | 蓝色（`Har/ry/_Pot/ter/1/G/ryffindor`） | 全部蓝色 |
| 前向传播次数 | **显著减少** | 逐 token |

**图例（Legend）**
- 🟩 **Prefill**（绿色）：一次性前缀编码
- 🟦 **Decode**（蓝色）：常规自回归解码
- 🟧 **Jump-Forward**（橙色）：由 FSM 确定性"快进"跳过的 token

**3) 一个关键技术要点**

**Jump-Forward 解码的本质**：当 Compressed FSM 通过 regex/grammar 推断出某些 token 序列是**确定性必须出现**的（如空白 `_____`、引号 `"`、冒号 `:`、逗号 `,`、花括号 `{}`），无需 LLM 参与采样——直接在一次 forward pass 内将这些 token 整体"注入"到输出流，并只对真正的"自由 token"（如 `Harry`、`15`、`Gryffindor`）调用模型。**

**带来的收益**：**
- **减少 N 次 forward → 减少 N-1 次 decode step**，显著降低结构化输出（如 JSON、函数调用、regex-guided 文本）的端到端延迟；
- **不改变输出语义**：右侧 Generated JSONs 完全一致；
- **配合 B.2 节的 retokenization**：压缩 FSM 在跳进前会调用原 tokenizer 重对齐，避免"字符串↔token"边界错位（如 `summary` 不能被切成 `summa`+`ry`）。

这一机制是 SGLang 在结构化生成（JSON mode / regex / EBNF）场景下实现高吞吐的核心优化路径。

**4) Caption 逐字转录**

> **Figure 11**: Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfigure explains the origins of various result components.

**中文翻译**：**
> 图 11：使用 Compressed FSM 解码与使用普通 FSM 解码的对比：左侧子图描绘每次前向传播中的解码过程，右侧子图解释各输出结果的来源构成。
*caption: Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfi… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.12 (p.19)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图为 Llama-2-70B + TP 配置下 SGLang（橙色，归一化为 1.0）与另一基线系统（绿色，图例被裁切）于 5 种典型 LLM 程序上的吞吐对比。绿色条读数大致为：MMLU≈0.12、ReAct Agents≈0.10、Generative Agents≈0.60、Tree of Thought≈0.30、Skeleton-of-Thought≈0.80，呈现"简单 prompt 差距悬殊、复杂多调用场景差距收窄"的梯度。

原文借此论证：在张量并行的大模型上，SGLang 的 RadixAttention 与 API 级批调度对含多轮/分支调用的结构化生成（Agents、ToT、SoT）带来 1.2×–10× 的吞吐加速，证实其前端语言模型程序与后端 KV 缓存协同设计的端到端效率优势，构成实验链路中"真实工作负载可扩展性"的关键证据。
*caption: Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better. MMLU… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.13 (p.19)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig13.png]]
> [!tip] 【图文联合解读】**图13联合解读**

图13以并列条形图对比"SGLang"（橙）与"Optimal cache hit rate"（浅蓝）在6个基准上的命中率——LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat (short/long)、DSPy RAG Pipeline。除Multi-Turn Chat两类外，SGLang柱高均接近甚至贴合Optimal柱；Multi-Turn Chat (short) 与 (long) 出现明显落差。论文借此论证：SGLang的缓存复用已接近理论最优，但多轮对话场景仍有提升空间，由此引出附录D.1中"重写计算图与更多静态规划"这一未来优化方向。
*caption: Achieved cache hit rate and optimal cache hit rate on various benchmarks. opportunities for more compilation optimizations, as we can rewrite the grap… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.14 (p.20)
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig14.png]]
> [!tip] 【图文联合解读】## Figure 14(b) 图文联合解读

**1) 核心结构与数据：**
图中展示一个计算图，按列分为三条 Stream（对应三次函数调用）。Stream 1 主链含 18 个节点（ConstantText×10、Argument×1、Gen×3、Variable×2）；Stream 2 与 Stream 3 各含 4 个节点。跨流边将 Stream 1 中 Gen("tip_1") 的输出分别送入 Stream 2、3 的 Variable("tip_1") 节点；Gen("tip_2") 输出则同时被 Stream 2 的 Variable("paragraph") 引用，呈现典型的 fan-out 数据依赖。

**2) 关键技术结论：**
通过把 SGLang DSL 程序编译成显式数据流图，可揭示 Stream 1 内 Gen("tip_1") 与 Gen("tip_2") 之间、乃至三条 Stream 之间的并行机会——LM 生成调用可被调度器批量/乱序执行，而非受源代码顺序约束。

**3) 在论文中的作用：**
该图作为 runtime scheduler 的**动机示例**，论证 SGLang 将命令式 LLM 程序提升为数据流图后，能够自动发现并利用生成调用间的并行性，从而支撑论文核心主张——结构化语言模型程序的高效执行。
*caption: An SGLang program and its corresponding dataflow graph.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.1 (p.1)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig01.png]]
> [!tip] 【图文联合解读】**核心对象与结构**：图1对比两种LMM服务执行时间线。上半"Aggregated"（DP=4）E与LLM共享同GPU，4行流水线依次为E¹→LLM¹、E²→LLM²、E³→LLM³、E⁴→LLM⁴（挤占E⁵使其延迟）→LLM⁵；下半"Disaggregated"（P=3, E=1）E与LLM分置不同GPU，Encoder行集中处理E¹–E⁵，LLM三行并行执行LLM¹–LLM⁵。

**论证结论**：聚合架构下encoder与prefill共用GPU产生资源争用，如LLM⁴阻塞E⁵；解耦后两者独立调度，消除时序干扰。

**论文作用**：开篇动机图，揭示传统聚合部署的流水线瓶颈，为后文EPD解耦方案提供必要性依据。
*caption: Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to i… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.2 (p.2)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig02.png]]
> [!tip] 【图文联合解读】**图2联合解读**

1）**核心数据**：该柱状图对比了 MiniCPM-V 2.6 模型在 **Disaggregated（蓝色）** 与 **Aggregated（绿色）** 两种部署下的最大批处理大小（Max Batch Size），横轴为每请求图像数（1/3/5/15/20/30/40）。数据显示：1图时，解耦配置批大小约48 vs 聚合仅约6；3图时约17 vs 约2；5图时约8 vs 约1；15图及以上，聚合模式全部 OOM（显存不足），而解耦模式仍可支持 15图≈4、20图≈3、30–40图≈1 的批处理。

2）**论证结论**：将 LLM 从 GPU 卸载后，编码器独占显存，使批容量获得数倍乃至近一个数量级的提升，并解锁了更高分辨率/更多图像的请求输入，直观证明了**解耦架构的显存效率收益**。

3）**论文作用**：该图位于方法介绍后的实验验证环节，作为 EPD-Disaggregation 提出的**首个量化动机证据**，为后续吞吐/延迟实验提供容量前提说明。
*caption: Impact of disaggregation on supported batch size and number of images per request for the MiniCPM- V 2.6 model. Removing the LLM from the GPU signifi-… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.3 (p.3)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig03.png]]
> [!tip] 【图文联合解读】**图3图文联合解读：**

该图展示EPD分离推理流水线架构：三类GPU（E黄、P橙、D绿）各自配备独立的队列与处理阶段——Encoding Queue→Encoding Stage→EP Bridge Queue、P同构、D同构。数据经"EP Migration"由E传P，再经"PD Migration"由P传D，输入ip/im经三阶段生成输出o。

**论证结论：** 将多模态推理拆解为编码、预填充、解码三个异构阶段，因各阶段显存/算力特征差异显著（对应Table 3中E与P最大批处理规模相差数倍），独立部署可避免资源争用。

**论文作用：** 作为EPD方法的核心架构定义图，确立阶段划分与跨阶段迁移机制，为后续资源调度、批处理优化等实验奠定基础。
*caption: The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migration—handle the trans- fer of data from encoding to prefill and from pre… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.4 (p.4)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig04.png]]
> [!tip] 【图文联合解读】图示EPD分离推理架构：多模态请求经Scheduler(Load Balancer)分配至Encoding、Prefill、Decoding三类专精实例，分别承载Encoder Weights+MM Cache、LLM Weights+MM/KV Cache及纯解码任务。阶段间以5槽EP Bridge Queue经Async Transfer(§3.2.1)异步交接；阶段内用TP/PP并行，跨阶段用IRP(§3.2.2)通信。

它论证将异构负载解耦到独立实例可弹性扩缩、消除长尾阻塞，是论文EPD方法的核心系统蓝图，后续全部实验均基于此架构展开。
*caption: System architecture of the proposed EPD Disaggregated Inference. the data associated with the request. In the decoding stage, workers load the LLM wei… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.5 (p.6)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig05.png]]
> [!tip] 【图文联合解读】**图5联合解读**

图示为3×2网格：上/下两行分别为每请求2/4张图像，列依次为MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B；纵轴SLO达成率(%)，横轴请求速率，三曲线对比EPD、DistServe、vLLM。**2图/请求时**，EPD峰值吞吐（虚线标示）约2.7/0.4/0.2 req/s且全程维持~100% SLO，而DistServe仅20–55%、vLLM常<10%（InternVL2两模型）；**4图/请求时**，EPD仍领先，峰值吞吐降至~1.5/0.1 req/s，基线几乎贴近0。

该图用于端到端SLO实验，量化证明EPD解耦在多模型、多图像规模下均稳定优于基线，是支撑"EPD Disaggregation"部署有效性结论的核心数据。
*caption: SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V … ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.6 (p.7)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图6含三幅箱线图，横轴为每请求图像数，纵轴为TTFT（秒），蓝色EPD与绿色DistServe对比：(a) MiniCPMv-2.6在2–16图范围内，16图时EPD≈3s、DistServe≈8.5s；(b) InternVL2-8B在2–8图范围，8图时EPD≈3.8s、DistServe≈5.5s；(c) InternVL2-26B在2–5图范围，5图时EPD≈5.2s、DistServe≈9.2s。

数据论证关键结论：随每请求图像数增加，TTFT单调增长，但**EPD增速远低于DistServe，差距随图像数扩大而显著放大**（如InternVL2-26B 5图时差距近2倍），证明EPD解耦对多图密集请求的延迟控制优势明显。

该图作为方法验证核心证据，在实验链中支撑"EPD解耦可有效降低多模态首token延迟"这一主张。
*caption: Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b)… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.7 (p.7)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig07.png]]
> [!tip] 【图文联合解读】图7展示MiniCPM-V 2.6在NextQA数据集上的SLO达成率(%)与请求速率(req/s)关系。三条曲线对比：EPD(蓝)在约1.2 req/s前稳定保持近100%达成率后骤降，垂直虚线标示其最大承载点；DistServe(绿)从约57%持续衰减；vLLM(红)仅约35%且迅速归零。该图论证EPD通过编码器-预填充-解码器分离设计显著提升多模态模型的在线服务SLO性能，是论文核心端到端实验的关键证据，与Table 7(音频基准)共同支撑"分离式架构优于DP/3P1D等方案"的方法结论。
*caption: SLO attainment (↑) versus request rate on the… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.8 (p.7)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读**

1) **核心数据**：横轴为请求速率(0.5–3.0 req/s)，纵轴为SLO达成率(%)。EPD(蓝)在0.5–1.5 req/s区间维持近100%，至约1.85 req/s(蓝色虚线)仍达90%阈值，2.0 req/s降为~70%，3.0 req/s仅~10%；DistServe(绿)与vLLM(红)在0.5 req/s仅约70%，随负载上升持续衰减，3.0 req/s时降至5–10%。

2) **关键结论**：EPD在全部请求速率下均显著优于vLLM和DistServe，其维持90% SLO的最大可承载请求率约为后两者的近4倍，验证了编码-预填充-解码分离架构在多模态视频推理场景下的优越性。

3) **论文作用**：作为EPD方法的核心实验证据之一，与Figure 7、Table 8共同支撑"分离式架构显著提升大模型多模态服务效率"的整体论证。
*caption: As seen, EPD consistently outperforms vLLM and Dist-… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.9 (p.9)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig09.png]]
> [!tip] 【图文联合解读】图9对比三种方案在InternVL2-8B模型、NPU上的SLO达成率（请求率0.007–0.035 req/s）：EPD由~95%单调降至~25%，仅在≤0.008 req/s内仍高于90%阈值线（红虚线）；DistServe与vLLM全程贴近0%，完全未达标。原文据此论证：EPD是唯一满足严格TTFT SLO的方案，基线即使在低负载下也整体失败。该图作为关键定量证据，支撑论文"Encode–Prefill–Decode解耦"核心架构的主张。
*caption: As shown, EPD is the only configuration that achieves the SLO requirements, while the other baselines fail to meet the SLOs entirely, even at low requ… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.10 (p.13)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图含三子图，均以EPD（橙实线）对比DistServe基线7P（绿虚线，约97 req/s）。**左图**：吞吐量随编/预填工人数配比变化——1E6P仅~45、5E2P峰值~155、6E1P降至~85 req/s，表明编/预填资源均衡（5:2）至关重要。**中图**：每请求图像数1→5时EPD由~155降至~50 req/s，但全程持续领先DistServe。**右图**：批大小32–64时EPD达~175 req/s峰值，对批大小不敏感。**作用**：作为敏感性/消融实验，定量论证EPD解耦在资源配置、图像规模、批大小三维度上均稳定优于DistServe，支撑全文"EPD解耦可大幅提升LMM服务吞吐"的核心主张。
*caption: Left: Impact of varying the number of encoding workers in the EPD method. The notation xEyP denotes a configuration with x encoder and y prefill worke… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.11 (p.13)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig11.png]]
> [!tip] 【图文联合解读】图示为2×3子图网格：纵轴SLO达成率(0–100%)、横轴请求速率(req/s)；上下行分别对应每请求6/8张图像，(a)(b)(c)列对应MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B；蓝/绿/红曲线分别代表EPD、DistServe、vLLM。

数据观察：(a) MiniCPM-V 2.6中EPD在≤1.0 req/s保持100% SLO，6/8图对应最大可持续速率≈1.4/1.9 req/s；DistServe峰值仅~45%，vLLM全程<20%。(b)(c) EPD仅在≈0.1 req/s时近100%，随负载上升急剧下滑；两基线全程≈0%。

论证结论：图像数由6增至8时EPD承载速率不降反升(1.4→1.9)，印证"随图像数增加仍保持稳健"；三模型EPD均大幅领先基线，且在InternVL2-26B等大模型上差距更悬殊。

整体作用：作为EPD解耦方案端到端主实验，以"负载×SLO"量化其在多模态大模型在线服务中跨模型与图像规模的实用性与鲁棒性。
*caption: SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V … ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Efficiently Serving Large Multimodal Models Using EPD Disagg — Fig.12 (p.16)
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图12以堆叠柱状图展示InternVL2-8B模型在每请求图像数(#I/R)由1增至8时，encode（绿）与prefill（蓝）阶段的延迟占比，分(a)GPU与(b)NPU两组。GPU上encode占比由约65%(#I/R=1)降至约25%(#I/R=8)，prefill升至约75%；NPU上encode由约72%降至约39%，prefill升至约61%。

原文借此论证：随图像量增加，encode与prefill占比发生明显翻转，且NPU的encode占比始终比GPU高约10–20%，两类阶段呈现显著不同的资源与时延特征——encode并行度高、可独立批处理，prefill则计算密集。该差异为论文核心贡献**EPD解耦**（Encode/Prefill/Decode分离部署）提供了直接实验依据，支撑将二者分配到不同硬件单元以提升多模态推理的整体吞吐与SLO达标率。
*caption: Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) s… ｜ 论文 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.1 (p.2)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig01.png]]
> [!tip] 【图文联合解读】图示Mooncake架构：左侧KVCache-centric Conductor含三调度器（Cache-aware Prefill Scheduler、KVCache Balance Scheduler、Load-balance Decoding Scheduler）；纵向分三层资源池——Prefill Pool（GPU/VRAM+本地分块预fill+分页KVCache）、KVCache Pool（CPU/DRAM/SSD分布式KVCache）、Decoding Pool（GPU/VRAM+分页KVCache），节点间以RDMA传输KVCache、Prefill节点间用PP/SP通信。右侧明示两阶段优化目标：Prefill max Cache Reuse受TTFT SLO、最低MFU、KVCache<DRAM约束；Decoding max Throughput受TBT SLO、KVCache<VRAM约束。

技术结论：解耦prefill/decoding并将KVCache显式提升为一等公民资源，通过分布式RDMA池化跨节点复用cache，从而兼顾延迟SLO与吞吐。

作用：全文方法总览图，奠定后续调度器设计与Table 1缓存命中率实验的分析框架。
*caption: Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these th… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.2 (p.4)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig02.png]]
> [!tip] 【图文联合解读】## 图2（右半·解码阶段）联合解读

**核心数据**：横轴为 Batch Size 1–16（序列长度固定 8k）。绿色柱（归一化吞吐量）从约 0.07 近似线性增长至 1.0；红色折线（解码延迟）几乎平稳，仅在 Batch 15–16 处轻微上扬至 1.0。

**论证结论**：解码阶段吞吐随 batch 近似线性放大，而延迟几乎不增长——这是「**解码高 batch 友好**」的关键实测证据。结合左半图 prefill 阶段计算量随序列长度超线性增长的事实，作者论证 prefill 与 decode 具有截然不同的扩缩特性。

**论文作用**：作为 Mooncake 提出 **prefill/decode 分离架构（disaggregation）** 的核心动机支撑——将计算密集、低延迟敏感的 prefill 与可大批并行、可吞吐优先的 decode 解耦部署，由 KVCache-centric 调度器协同，才能同时兼顾吞吐与 SLO。
*caption: Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the co… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.3 (p.5)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig03.png]]
> [!tip] 【图文联合解读】**图3联合解读（≤220字）**

① **核心对象与结构**：展示CPU内存中的KVCache池，含9个Token块(a–i)。每个块采用**链式哈希**：A=Hash(a)、B=Hash(A+b)、…、F=Hash(E+f)，哈希值由自身内容与前缀哈希共同决定。三色分类：黄色=前缀缓存块、粉色=增量缓存块、灰色=未分配块。

② **关键技术结论**：示例中a–e五个前缀块全部Match✓复用，f处Mismatch✗触发失配；增量块F–I(粉色)被新计算并写入新位置。证明链式哈希+块粒度可实现**精确前缀去重**，避免整请求重复计算前缀KVCache。

③ **论文整体作用**：该池是Mooncake解耦架构的存储底层，通过Prefill Instance→Messenger→Decoding Instance间的Load/Store/Transfer/Write/Read五路径实现跨实例KVCache流转，为后续Prefix Caching复用与Early Rejection（表3所示过载场景拒请求）提供基础设施支撑。
*caption: The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.4 (p.6)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig04.png]]
> [!tip] 【图文联合解读】图分两栏：左为Prefill实例，含CPU/GPU双层，按Prefix与Incremental KVCache分块；右为Decoding实例，含Full KVCache。流程含s1前缀复用、s2增量prefill、s3跨实例KVCache传输、s4解码四个步骤。Prefill侧(∗)逐层Load/Store与计算并行，隐藏传输开销；Decoding侧(†)异步加载与GPU解码重叠，避免GPU空泡。该图论证Mooncake分离架构"计算与传输并发"的核心优化设计，是KVCache中心化方法论的关键图示。
*caption: Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in pa… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.5 (p.6)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig05.png]]
> [!tip] 【图文联合解读】图5展示请求trace的输入（蓝）与输出（绿）长度分布，频率为log刻度。**输入高度右偏**：峰值集中于0–5k tokens（~10⁴），但长尾延伸至120k+，跨度达4个数量级；**输出近似双峰**：主峰在300–500 tokens（~10³），次峰近2000，最大约2100。

**关键论证**：实际负载中输入长度极端异构——长输入使prefill阶段产生巨大KV cache却仅生成少量token，与decode阶段轻量增量KV形成严重的内存–计算失衡；而输出相对短且有界，prefill/decode资源需求极不对称。

**论文作用**：此图为后续"以KVCache为中心的prefill–decode解耦架构"提供数据驱动的动机支撑，是Mooncake分离式设计合理性的关键实证基础，也为调度策略与cache复用讨论奠定前提。
*caption: Input and output length distributions in the request trace. 4… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.6 (p.7)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 6）**

1) **图示数据**：横轴 Block Hit Count（对数刻度 1–10⁴），纵轴 CDF。约 55% 的块命中次数=1，约 77% ≤2 次，约 95% ≤10 次；命中≥10² 的块占比可忽略，最大值延伸至 ~10⁴ 但概率极小。整体呈极度长尾分布。

2) **关键结论**：少量"热门"块承担绝大多数重用请求，证实 LLM 请求间 KV cache 复用潜力大、冗余重计算成本高，从而为"以 KV cache 为中心"的设计提供量化依据。

3) **论文作用**：支撑 Mooncake 的核心动机——将 prefill 计算与 KV cache 存储解耦、池化共享，使小部分热块可被多次复用，显著降低 prefix 重算开销。
*caption: CDF (Cumulative Distribution… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.7 (p.9)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig07.png]]
> [!tip] 【图文联合解读】**图7联合解读**

图7对比两种KVCache存储策略（Serialized序列化 vs Layer-wise分层）在不同请求长度（8K–128K）下的存储延迟。量化数据：Serialized延迟近似线性增长（8K约0.11s→128K约0.86s）；Layer-wise全程稳定在约0.10s，128K时仅为Serialized的~1/8.6。

**关键结论**：原文借此论证"分层并发存储KVCache"可消除长序列下存储开销的线性放大，是Mooncake采用Transformer层间流水线调度、并把prefill计算与KVCache写入重叠的核心实验依据，支撑其长上下文场景下的高吞吐设计。
*caption: Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.8 (p.11)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图为箱线图，纵轴为TTFT（秒），含一条约30秒的SLO虚线。横轴对比四种调度策略：

1. **核心数据**：KVCache-centric中位数约7–8s，分布极紧凑，远低于SLO；cache-aware中位数约18s，仅少量离群点；load-balancing均值89.41s、箱体伸至~105s，须线达~220s；random均值92.92s、箱体最高~150s、须线逼近285s。

2. **关键结论**：论文提出的KVCache-centric调度策略TTFT最低且稳定，证明以KVCache为中心的调度远优于负载均衡与随机策略，能稳定满足SLO；而load-balancing和random因忽略cache局部性，导致大量长尾延迟。

3. **链路作用**：作为消融/对比实验，量化验证核心调度设计（KVCache-centric）的有效性，支撑论文"以KVCache为中心"这一核心架构主张。
*caption: The prefill scheduling experiment in the Mooncake cluster.… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.9 (p.13)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) 图示20分钟窗口内 prefill（绿线）与 decoding（黄线）实例的负载率随时间变化曲线，y 轴负载范围约 10%–95%。两条曲线呈明显**反相位**：prefill 飙升时 decoding 多处低位，反之亦然，且 prefill 振幅显著更大，深谷多次逼近底部。

2) 原文借此论证：在未启用基于预测的 early rejection 机制之前，解耦架构下 prefill 与 decoding 节点负载严重不均衡、波动剧烈，暴露出传统调度难以稳定 SLO 的缺陷，从而为引入**预测式早拒**以均衡负载提供动机。

3) 该图作为**对比基线**，与后续启用 early rejection 后的负载曲线（图10/11）形成对照，串联起"暴露问题 → 提出方案 → 实验验证"的完整论证链，是 Mooncake 调度策略章节的关键支撑。
*caption: The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.10 (p.14)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**核心对象与数据**：图分上下两行4个Stage，沿时间轴展示实例**解码负载（上，橙）与预填充负载（下，蓝）**的动态变化。Stage1解码≈0.15（低）/预填充≈0.95（高，新请求密）→Accept；Stage2解码≈0.8（高）/预填充≈0.15（低）→Reject；Stage3再次解码≈0.15/预填充≈0.8→Accept；Stage4解码≈0.6/预填充≈0.3→Reject。曲线连接呈现"高-低"振荡。

2）**关键结论**：早期拒绝依据预测的解码负载阈值（≈0.6，橙色虚线）切换Accept/Reject，避免预填充过载溢出，同时印证原文"资源稀缺、需精确预测时，请求级预测尤为困难"——单纯看当前预填充会误判（Stage2本应Reject时预填充低），必须预测解码端未来负载。

3）**方法链作用**：该图为Mooncake**过载预测与早期拒绝策略**提供可视化依据，是调度器在Prefill/Decode解耦架构中保护KVCache节点不被预填冲击的关键决策环节。
*caption: Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions ar… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.11 (p.16)
![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig11.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图呈现2×2网格中的L-Eval列（ArXiv列未显示）：横轴为请求速率（0.25–2.0 req/s），纵轴为归一化P90 TTFT（上）与P90 TBT（下），虚线1.0为SLO阈值；蓝、红、橙三曲线分别对应Mooncake与两种vLLM基线。TTFT图中，Mooncake在1.5 req/s前维持在0.1–0.3，至~2.0才破线；基线分别在1.25与1.5处即触线。TBT图中，Mooncake与红色基线先后在~1.0与~0.75 req/s突破SLO，而橙色基线始终平坦于~0.2–0.3。

原文借此论证：解耦架构在端到端长文本场景中显著提升SLO吞吐上限，TTFT增益尤为突出；该图为论文整体方法链路的"系统级压测"收尾，呼应§3.2调度与KV缓存传输设计，并以真实基准数据支撑"以KV Cache为中心"的可行性结论。
*caption: End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets instances. In real-world clusters, the demand for prefill a… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.12 (p.16)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
> [!tip] **Description (≤120 words):**

Figure 11 presents a 2×2 grid of end-to-end performance benchmarks comparing Mooncake against vLLM variants on two long-context datasets (ArXiv Summarization, L-Eval). The top row plots normalized P90 TTFT (Time To First Token) versus request rate, while the bottom row plots normalized P90 TBT (Time Between Tokens). Three series are compared: Mooncake-[3P+1D] (blue) plus two baseline configurations (red, orange). Across all four panels, Mooncake's disaggregated architecture sustains lower latency values at substantially higher request rates before saturating the SLO thresholds (dashed lines at 1.0). The bottom-row TBT curves particularly show Mooncake flattening near ~0.5 while baselines climb toward violation.

**Key takeaway:** Mooncake's prefill–decode disaggregation decouples TTFT from TBT bottlenecks, enabling 2–3× higher sustainable request rates under identical SLOs.

**Verbatim caption:**

Figure 11: End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets
*caption: End-to-end experiments of Mooncake and vLLM on simulated data.… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.13 (p.17)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]]
> [!tip] # Figure 13 Description

**Note:** The figure itself (CDF plots) is not visible in the rendered page — only its caption appears. The description below is reconstructed from the caption and accompanying text in §8.1.3.

## Architecture / Components / Data Flow

Figure 13 is a **two-panel CDF plot** comparing request-level latency distributions between two serving stacks on identical real-world traces:

- **Mooncake-[10P+10D]** — 10 prefill instances + 10 decoding instances (disaggregated prefill/decode).
- **vLLM-[20M]** — 20 monolithic instances.
- **Left panel:** TTFT (Time To First Token) CDF, with an SLO threshold at **30 s**.
- **Right panel:** per-token TBT (Time Between Tokens) CDF, capped at **0.1 s/token**.
- **Data flow:** replayed production request traces → dispatched to either Mooncake's prefill→decode pipeline or vLLM's integrated engine → per-request TTFT and TBT samples → empirical CDF curves.

## Key Technical Takeaway

TTFT compliance is near-identical (~100%) for both systems, but **TBT SLO adherence diverges sharply**: Mooncake satisfies it for ~100% of requests vs. **only 57% for vLLM**, allowing Mooncake to serve ~75% more requests under the same SLOs.

## Caption (verbatim)

> Figure 13: Request TTFT and TBT distributions of Mooncake and vLLM under real workloads
*caption: Request TTFT and TBT distributions of Mooncake and vLLM under real workloads… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.1 (p.2)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示 **ZeRO-2 数据并行的计算流水**：两个 Model Replica（GPU）分别输入 Data 0 / Data 1，各自执行 **Forward → Backward → Reduce-Scatter → Update Params → All-Gather**。两副本在 Reduce-Scatter 阶段通过 *"sync grads"* 同步分片梯度，在 All-Gather 阶段通过 *"gather params"* 拉取完整参数。

**论证的关键结论**：相比传统 All-Reduce，ZeRO-2 将**梯度与优化器状态按数据并行维度切分存储**，消除每卡冗余，显著降低单卡显存占用，使超大模型可在数据并行规模上线性扩展。

**在论文中的作用**：该图给出 MegaScale 的**基础并行范式**，作为后续万卡级扩展框架（通信优化、流水线编排、故障定位与心跳检测等）的算子级前提，支撑"超过 10,000 GPU 训练 LLM"的可行性论证。
*caption: Data parallel training with ZeRO2. dependencies that contribute to stability issues. We develop a robust training framework to automate fault localiza… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.2 (p.3)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig02.png]]
> [!tip] 【图文联合解读】该图展示Interleaved 1F1B流水线调度：3个stage（0/1/2）在时间轴排列，粉色为前向、蓝色为反向（编号0–5代表micro-batch），灰色为warmup/cooldown区段；红色虚线将时间轴划分为warmup（重复出现0,1,2,0,1,2,3）、稳态1F1B（4,0,5,1,3,2,4,0,5,1,3,2…）、cooldown三阶段。warmup阶段同一组micro-batch号重复出现，说明每个stage承担多个模型chunk并交错执行前向，从而用更少气泡填满流水线。原文据此论证：交错调度与ZeRO状态分片结合可显著压缩气泡率，是支撑千卡–万卡规模强扩展（对应Table 2中3072→12288 GPU仍保持高吞吐）的关键调度策略。
*caption: Interleaved 1F1B pipeline. update the model. Instead of duplicating model states (like the optimizer states, gradients, and parameters), Zero Redun- d… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.3 (p.4)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图分三子图：(a) 标准PTB含SP区LayerNorm+All-Gather/Reduce-Scatter与TP区QKV ColParaLinear→Self Attention→RowParaLinear；(b) 将AG融合进ColParaLinear、RS融合进RowParaLinear，消除独立通信节点；(c) 双CUDA流S0(GEMM)与S1(comm)并行，使A×W与all-gather Copy交错、B×W与reduce-scatter交错执行。

**技术结论**：算子级融合＋流级重叠，使TP的集合通信与GEMM计算时间线重合，隐藏通信时延。

**整体作用**：作为Megascale万卡训练系统栈的算子层关键改造，为后续大规模扩展实验提供PTB结构级通信优化基础。
*caption: Overlapping communication in tensor parallelism (TP) and sequence parallelism (SP) with parallel transformer block (PTB). with a large receptive field… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.4 (p.4)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 图示核心对象与结构**
该图对比流水线并行相邻两阶段（stage i、stage i+1）的两个阶段时序：左侧 Warm-up 阶段，每阶段呈现 R→FWD→S 的串行序列；右侧 Steady 阶段，FWD（绿）与 BWD（紫）计算块沿独立 stream（虚线）与顶部的 R、底部的 S 通信块并行排布，标注 "Communication Overlap"。

**2) 原文论证的关键结论**
稳态下前向与反向计算均与相邻 Send/Receive 通信相互独立，因此通信可分流并行、覆盖计算，从而隐藏集合通信延迟；冷启动（cool-down）阶段则为该重叠技术的逆向复用。

**3) 在论文整体方法中的作用**
此图为 MegaScale 在 10000+ GPU 规模下流水线并行的核心系统优化之一，通过通信-计算解耦降低通信占比、提升 GPU 利用率，是实现高吞吐大规模训练的关键设计。
*caption: The cool-down phase can be viewed as the inverse of the warm-up phase, allowing for the inverse application of the same technique. As for the steady p… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.5 (p.6)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图5呈现Megascale万卡训练的容错工作流，采用**Driver-Executor双层架构**。Driver侧含User API、Checker、Log Analysisor、Evicted Pods/Blocked IPs四个模块；Executor侧含Executor 0~N并行节点。关键交互包括：User API提交作业并生成驱逐Pod/封禁IP列表；Checker对Executor执行stop & check并回收结果；Log Analysisor通过心跳（heartbeat）触发Checker；Driver经Kubernetes管理资源。

原文借此论证：在>10,000 GPU规模下，网络链路抖动（flapping）、Pod驱逐等故障不可避免，需通过心跳监测+主动检测+IP封禁的闭环机制实现快速恢复，确保长稳训练不中断。

该图在论文中起到承上启下作用：上承底层网络/通信栈的可靠性设计，下启具体故障应对策略（链路恢复、节点替换），是证明"万卡可持续训练"系统可信度的核心架构图。
*caption: Robust training workflow. interval and help recover the transmission more quickly when the link flapping period is short. 4… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.6 (p.8)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图6横轴为训练步数（0–30000），纵轴为MFU（0–0.6）。多色折线代表同一训练任务的多次独立执行，MFU整体落在0.35–0.45区间，但波动显著：红色线段（约7000–17000步）MFU仅0.35–0.38，低于蓝/橙/粉/紫/绿等其余执行（约0.40–0.43），同一任务不同run间MFU差异可达5–10%。

论文借此论证：**大规模训练中性能不一致是常态而非异常**——即便软硬件配置相同，跨次执行的MFU仍存在系统性偏差，单次观测无法代表真实训练效率，必须建立可重复、可量化的可靠性度量。

该图在论文链路中作为**现象驱动的开篇实证**，支撑后文提出的全栈诊断工具与故障恢复机制（如HDFS带宽缓解），说明仅靠扩大GPU规模并不能保证稳定高效训练，必须配套工程化可靠性保障。
*caption: Inconsistent MFU observed in large-scale training. Differ- ent colors denote distinct executions of the same training job. mitigates the bandwidth con… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.7 (p.8)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：该图为48个rank（rank 0–47，分布在host 0–11共12台主机，每机4卡）的计算阶段（前向+反向）延迟热力图。色阶由2.0s（浅粉）到2.5s（深红），并标注三类通信依赖：TP Comm（绿色）、DP Comm（紫色）、PP Comm（橙色箭头）。rank 20（host 5）被选中高亮，可展开3D视图观察跨并行维度的依赖关系。多数rank稳定在~2.0s，但rank 32（host 8）显著偏红，存在掉队。

2) **关键结论**：热力图直观暴露了大规模训练中的延迟分布不均——个别rank（如32）成为straggler；同时揭示了TP/DP/PP三种并行维度间的通信耦合关系，便于诊断瓶颈来源。

3) **论文作用**：作为性能剖析与可视化工具，支撑MegaScale诊断流水线中"识别长尾、定位通信热点"的核心能力，是其全栈优化体系（算法/网络/调度）发现问题→定位根因的关键一环。
*caption: We gather latency data of the computation phase (forward and backward) across devices and average the latency across steps. The aggregated data is vis… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.8 (p.9)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象与结构**：该图呈现 Megascale 调试框架的流水线并行轨迹视图。横向为统一时间轴，纵向为同一 pipeline group 内的 4 个 stage（rank[0]、rank[4]、rank[8]、rank[12]，共 16 个 stage 中的子集）。事件块按类型着色：绿色为 forward（f...），橙色为 backward（bac...），灰色为前/反向大块（forwar.../bac...），短箭头显示跨 rank 的数据依赖（选中事件后高亮）。

**论证结论**：图中清晰呈现 1F1B 调度模式——各 stage 交错启动形成流水气泡，forward 波从 rank[0] 向右传播、backward 波回传，可视化工具将这种跨 stage 时序与显式依赖关系一并暴露，便于在大规模训练中定位流水线停顿与通信瓶颈。

**论文作用**：支撑文中 Nezha 大规模分布式调试系统章节，作为"能在万卡规模下对复杂流水线 schedule 做细粒度可视化"的实证。
*caption: The trace shows events collected in a pipeline group on a unified timeline. Dependencies become visible when an event is selected.… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.9 (p.10)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig09.png]]
> [!tip] 【图文联合解读】**图9解读：**

**1) 图示数据：** 该柱状图展示530B模型在弱扩展设置下（batch size随GPU数同比放大）的MFU对比，横轴为GPU规模（2240/4480/11200），纵轴为MFU(%)。MegaScale在三种规模下MFU分别为54.30%、54.10%、54.30%，几乎水平；Megatron-LM则为49.20%、48.80%、48.20%，两者存在约5–6个百分点的稳定差距，且两条序列随规模扩大均无明显下降。

**2) 关键结论：** 论文以此证明MegaScale相对Megatron-LM具有**规模无关的持续效率增益**——其全栈优化（通信overlap、并行策略、可靠性机制等）在大规模下仍稳定保持约54% MFU，弱扩展性良好。

**3) 论文作用：** 该图是论文"万卡级高效训练"主张的核心量化证据之一，与强扩展、收敛性、故障恢复等实验共同构成对MegaScale系统级性能的完整论证链。
*caption: Weak-scaling training performance of Megatron-LM and… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.10 (p.11)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig10.png]]
> [!tip] 【图文联合解读】**图10解读：ADAM与LAMB优化器训练损失对比**

**1) 核心对象与数据**
图(b)展示两条训练loss曲线：蓝色为1×batch_size下的ADAM，橙色为4×batch_size下的LAMB。横轴为已消费tokens（B，0–270B+），纵轴为loss（2–8）。ADAM起点约4.5，LAMB起点近8且在~90B处出现尖峰；两条曲线在~150B tokens后基本重合，最终loss稳定在≈2.2。

**2) 关键技术结论**
证明在batch_size扩大4倍的情况下，LAMB优化器能达到与ADAM（1×batch_size）几乎一致的收敛loss，说明大batch训练不会损失模型质量，验证了LAMB优化器在大batch场景下的有效性。

**3) 在论文中的作用**
此图属于微基准实验（microbenchmark），为整篇论文万卡级训练提供优化器选型依据：在大规模集群中必须使用大batch以摊销通信开销，而本实验证明LAMB可在保持loss不退化的前提下支撑4×batch扩展，是后续端到端万卡训练可扩展性论证的关键支撑。
*caption: The training loss curves in microbenchmark experiments.… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.11 (p.11)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig11.png]]
> [!tip] 【图文联合解读】**图11联合解读：**

图示万卡规模（10 000+ GPU）训练千亿参数、多token模型的归一化loss曲线：X轴为已消费token比例(0–1)，Y轴为loss。曲线初始≈0.85骤降至~0.2，再缓降至≈0.15；多色段对应100+次故障重启，loss衔接平滑无明显跳变。

**关键结论**：MegaScale的故障检测与恢复机制可在万卡、跨周长周期训练中保持收敛稳定性，多次重启不影响loss趋势。

**论文作用**：作为production-scale端到端验证，证明系统在真实超大规模长周期训练中的鲁棒性与可落地性，是整套方法从单点优化走向规模化可靠训练的最终佐证。
*caption: The normalized training loss curve of a real production run on more than 10,000 GPUs for several weeks. This run trains a model with hundreds of billi… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.12 (p.12)
![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图12横轴为训练步数（0–30000），纵轴为MFU（0–0.6）。橙色线对应前约1万步，蓝色线对应1万–3万步，两条同配置试验曲线MFU均稳定在约0.48–0.50，仅偶现向下尖刺（落后节点瞬时拖累）。橙色段尖刺稍频，蓝色段更平直，说明排查straggler与问题代码段后MFU趋于平稳。

原文借此图论证：万卡级规模下，经诊断与代码优化，训练利用率可长期保持稳定，支撑"有效训练时间率>90%"的可靠性声明；在论文链路中，它是衔接"问题诊断→针对性优化→长期稳定性验证"实验闭环的关键实证证据。
*caption: The MFU becomes stable after addressing the stragglers and problematic code segments. Different colors represent different training trials with the sa… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### ZeRO: Memory Optimizations Toward Training Trillion Paramete — Fig.1 (p.3)
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图1以 Ψ=7.5B、K=12、N_d=64 为具体参数，量化对比 Baseline 与 ZeRO-DP 三阶段（P_os、P_os+g、P_os+g+p）的**每卡显存**：参数（蓝）、梯度（橙）、优化器状态（绿）三色块由满载依次被切分，单卡占用从 Baseline 的 (2+2+K)Ψ=**120GB** 降至 31.4GB → 16.6GB → **1.9GB**，约 **60×** 压缩。

**关键结论**：依次分片优化器状态、梯度、参数可逐级消除数据并行冗余，且通信开销可控。

**作用**：作为全文方法论的开篇动机图，为后续 P_os / P_g / P_p 的形式化定义及万亿参数训练可行性论证奠定量化基础。
*caption: Comparing the per-device memory consumption of model states, with three stages of… ｜ 论文 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] ｜ arxiv 见 MD 元信息*

### ZeRO: Memory Optimizations Toward Training Trillion Paramete — Fig.2 (p.4)
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图2以双轴柱状/散点复合图，对比1.5B–170B共9档模型规模下ZeRO（绿点）与基线MP（橙/红三角）的单GPU吞吐量（实线为10/15 Pflops参考线，灰柱为加速比）。数据上：ZeRO吞吐量稳定在30–38 Tflops，1.5/8B时基线仅23–26 Tflops、加速比≈1×；100B时ZeRO达~38 Tflops、基线骤降至~3.5 Tflops、加速比峰值~10×；170B仍保持~10×加速。

**技术结论**：验证ZeRO通过消除MP冗余存储，使MP始终限于单节点即可训练百亿–千亿级模型；相比>40B必须跨节点MP的基线，吞吐量与可扩展性均显著领先。

**论文作用**：作为Stage-1实验的核心证据，量化支撑"在标准数据并行集群上高效训练万亿参数模型"这一核心主张。
*caption: ZeRO training throughput and speedup w.r.t SOTA baseline for varying model sizes.… ｜ 论文 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] ｜ arxiv 见 MD 元信息*

### ZeRO: Memory Optimizations Toward Training Trillion Paramete — Fig.3 (p.5)
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig03.png]]
> [!tip] 【图文联合解读】**图3图文联合解读：**

1) **核心对象与数据**：横轴为GPU数（64→400），左轴为总性能Tflops（对数），右轴为单卡Tflops。灰柱=单卡吞吐，绿线=实测总性能，蓝线=理想线性参考。64卡时实测与线性线重合（约1500 Tflops，单卡~6 Tflops）；随规模扩展，实测曲线（绿）全程高于理想线性线（蓝），且灰柱同步增长（6→36 Tflops/GPU）；400卡时实测约15000 Tflops（15 PFlops），单卡~38 Tflops/GPU。

2) **关键结论**：ZeRO-100B在60B模型上呈现超线性扩展，单卡吞吐亦随规模提升，证实分片化显存优化缓解了内存-计算比瓶颈，训练速度较SOTA提升超10×。

3) **论文作用**：作为方法核心实证，衔接"显存瓶颈分析→ZeRO分片策略→超大规模可行性论证"链路，为后续ZeRO-100B乃至万亿参数训练提供性能保证。
*caption: Superlinear scalability and per GPU training throughput of a 60B parameter model using ZeRO-100B. 38 TFlops per GPU, and aggregate performance over 15… ｜ 论文 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] ｜ arxiv 见 MD 元信息*

### ZeRO: Memory Optimizations Toward Training Trillion Paramete — Fig.4 (p.16)
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig04.png]]
> [!tip] 【图文联合解读】**图4散点图联合解读：**

左图为散点图，横轴为模型规模(1–13B参数)，纵轴为单卡吞吐量(0–50 Tflops)。绿色圆点(ZeRO-DP)从1.5B约40 Tflops上升，6–8B时达峰约47 Tflops，超过35 Tflops虚线(对应集群聚合4.5 Pflops)；橙色三角(Baseline-DP)在同等规模仅约18 Tflops，较ZeRO低约55%。右图(Figure 5)补充Model-ZeRO-17B验证困惑度全程低于Megatron-LM-8.3B。

**技术结论：** ZeRO-DP仅靠分片数据并行即可将单卡吞吐提升约2倍，并在10B级仍维持近峰值，验证其可扩展性。**论文作用：** 该图作为吞吐可行性证据，支撑后续Figure 5中17B模型训练实验及向万亿参数扩展的论证链。
*caption: Max model throughput with ZeRO-DP.… ｜ 论文 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] ｜ arxiv 见 MD 元信息*

### ZeRO: Memory Optimizations Toward Training Trillion Paramete — Fig.5 (p.16)
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图5横轴为迭代步数（0–300K），纵轴为验证困惑度（8–14），对比两条曲线：橙色Megatron-LM-8.3B与绿色Model-ZeRO-17B。两者起点均接近14，但绿色ZeRO-17B曲线全程位于橙色之下，迭代至30万步时，ZeRO-17B收敛至约8.8，而Megatron-LM-8.3B稳定在约9.3附近。

原文据此论证：ZeRO使可训练参数规模从8.3B跃升至17B（Turing-NLG），同时困惑度反而更低，证明内存优化未以模型质量为代价。该图作为论文方法验证阶段的核心实验证据，与表8（不同ZeRO配置下的显存分配）相互呼应，共同支撑"ZeRO赋能SOTA大规模模型训练"的整体技术叙事。
*caption: SOTA Turing-NLG enabled by ZeRO.… ｜ 论文 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] ｜ arxiv 见 MD 元信息*

### ZeRO: Memory Optimizations Toward Training Trillion Paramete — Fig.6 (p.16)
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读**

**1）核心对象与数据**：图分两子图。左图在固定 batch size=16 下，测试 ZeRO Config 1–5 可训练的最大模型规模：Config 1≈40B、2≈60B、3≈50B、4≈140B、5≈150B；右图展示对应缓存占用（GB），Config 1–3 仅含 40B 模型（约 24–30 GB），Config 4–5 同时给出 40B（≈20 GB）与 100B（≈27–30 GB）模型的内存开销。

**2）关键技术结论**：Config 3→4 之间出现数量级跃升（50B→140B），而缓存占用几乎不增反降，证明突破 GPU 显存瓶颈的关键在于 Config 3/4 引入的 ZeRO-Infinity 思想——将优化器状态等卸载至 CPU/NVMe 内存，使超大规模模型训练成为可能，且单卡内存代价受控。

**3）论文链路作用**：该图作为 ZeRO 三阶段（Pos/G/Pa）→ Infinity 演进路线的量化证据，回答了"为何需要 Stage 3 之后的优化"，支撑后文对万亿参数训练的可行性论证。
*caption: Max model size .… ｜ 论文 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] ｜ arxiv 见 MD 元信息*

### ZeRO: Memory Optimizations Toward Training Trillion Paramete — Fig.7 (p.16)
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig07.png]]
> [!tip] 【图文联合解读】图含三子图，量化展示ZeRO五种配置：①固定batch=16时最大模型规模由Config 1–3的40–60B跃升至Config 4–5的140–150B；②40B/100B模型各配置下缓存占用稳定在20–30GB；③170B模型在Config 1–4下无法训练（×标记），仅Config 5达约20Tflops，60B模型单卡吞吐由约12升至约31Tflops。

原文结论：ZeRO-3+（Config 4/5）在缓存相近的前提下将可训练模型规模提升约3倍，并首次实现纯数据并行下的170B级训练，验证零冗余存储可突破显存瓶颈。

论文作用：作为核心定量证据，支撑ZeRO将数据并行扩展至万亿参数规模的方法链路。
*caption: Max cache allo- cated.… ｜ 论文 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] ｜ arxiv 见 MD 元信息*

### ZeRO: Memory Optimizations Toward Training Trillion Paramete — Fig.8 (p.16)
![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig08.png]]
> [!tip] 【图文联合解读】图以ZeRO配置1–5为横轴：左图显示40B/100B模型缓存由约30/29 GB降至20/26 GB；右图显示60B模型在配置4达约35 Tflops，170B仅配置5可运行，约21 Tflops。说明深层配置可兼顾内存与吞吐，使超大模型训练可行；据此估算1T BERT-Large训练约需140天，为ZeRO方案选择和万亿参数扩展提供量化依据。
*caption: Throughput per GPU. a Bert-Large model for a data sample. Even if we assume the same sequence length and the total number of samples required to train… ｜ 论文 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.1 (p.1)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与数据**：半对数散点图，横轴为2018–2021年份，纵轴为参数量（10⁻²至10³亿，对数轴）。六个标注点：ELMo (94M, 2018)→BERT-L (340M)→GPT-2 (1.5B)→Megatron-LM (8.3B)→Turing-NLG (17.2B)→GPT-3 (175B, 2020)，红色虚线拟合呈指数增长。

2) **论证结论**：约2年内参数量增长近3个数量级，训练所需FLOPs随之指数飙升，单卡/单节点已无法承载。

3) **论文作用**：作为开篇动机图，引出Megatron-LM的核心贡献——张量并行+流水并行，在GPU集群上高效训练千亿级模型，与图中趋势形成"问题—方案"呼应。
*caption: Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models with time. The number of floating-point op- erations to train these mode… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.2 (p.3)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：图示展示了 Transformer 层在 PTD 并行下的二维切分。绿色实线框"Pipeline MP partition #1"代表一个流水阶段，内部串联多个结构相同的 Transformer 层（每层含 Self-Attention 与 MLP 子模块）；蓝色虚线框"Tensor MP partition #1/#2"将同一层内 Q/K/V 矩阵乘法与 MLP 切分到 2 个 GPU 上，层间仅在边界处通过 all-reduce 通信。

2）**关键技术结论**：该图直观论证了 Megatron 的核心方案——张量并行（层内）与流水线并行（层间）正交组合，使单层权重与激活显存被 N_t 个 GPU 平摊，同时流水阶段又可跨 N_p 个 GPU 扩展层数，从而在保持高利用率的前提下支撑超大规模模型（论文 Table 2 即在此架构上将 GPT 模型扩至 530B 参数）。

3）**论文作用**：此图是全文方法学的"总览图"，后文 Table 2 等实验均以此 PTD 并行布局为基线，证明其相对 ZeRO-3 的吞吐与可扩展性优势。
*caption: Combination of tensor and pipeline model parallelism (MP) used in this work for transformer-based models.… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.3 (p.3)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图示GPipe在4个Device上的流水线调度，1个batch切分为8个microbatch（编号1–8）。蓝色方块为前向pass，绿色为反向pass（时长为前向的2倍），灰色区域为pipeline bubble。Device 1率先启动前向，各设备依次错开1个microbatch时间，全部前向完成后才依次启动反向，呈现典型"先全部F、再全部B"的同步模式。

**2) 关键结论：** 纯流水线并行存在显著气泡（warm-up与cool-down阶段设备空闲），其占比与microbatch数N和设备数M相关（效率≈N/(N+M−1)），是GPipe方案的核心效率瓶颈。

**3) 论文作用：** 作为Megatron-LM提出PTD-P（张量+流水线+数据三维并行）方法的动机基线，论证单维流水线并行不足以高效训练超大模型，需结合张量并行进一步压缩气泡、提升GPU集群利用率。
*caption: GPipe pipeline schedule with forward passes (blue) for all microbatches (represented by numbers) followed by backward passes (green). The gray area re… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.4 (p.3)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig04.png]]
> [!tip] 【图文联合解读】图中展示4个设备（Device 1–4）上两种1F1B流水线调度对比：上图默认调度按顺序处理微批次1–7，灰色气泡（warm-up阶段）约占前半时段；下图交错调度将每设备再分配1个模型分片（深绿为第1分片、浅绿为第2分片），微批次扩展至1–8，灰色气泡明显缩小，flush更早完成。原文借此论证：交错式1F1B通过把多个Transformer分片分配到同一GPU，让前向/反向计算在时序上更紧密交叠，可在几乎不增加显存开销的前提下显著压缩气泡、提升端到端吞吐。该图是Megatron-LM提出的Interleaved 1F1B核心优化的示意，作为流水线并行的关键贡献，直接支撑后续千卡级GPU集群训练LLM的大规模实验验证。
*caption: Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleav… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.5 (p.5)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心结构**：图分(a) MLP和(b) Self-Attention两个子图，展示Transformer块沿2个GPU的张量切分方式。MLP中`f`将`X`拆为`[Y₁B₁, Y₂B₂]`并行计算，`g`做all-reduce恢复`Z`；Self-Attention中`Q/K/V`沿注意力头维度切分为`[Q₁,Q₂]/[K₁,K₂]/[V₁,V₂]`，各GPU独立完成`Softmax→Dropout`后由`g`合并输出。

2) **关键结论**：`f`与`g`为共轭算子——前向`f`恒等、`g`通信，反向时角色互换，证明层内张量并行只需一次all-reduce即可同步，无需逐层参数传递。

3) **论文作用**：与流水线并行（层间）正交，构成Megatron-LM"层内张量并行+层间流水线并行"双维度并行的可视化基础，用于推导通信量代价模型并降低pipeline bubble占比。

(约218字)
*caption: Blocks of transformer model partitioned with tensor model parallelism (figures borrowed from Megatron [40]). 𝑓and 𝑔 are conjugate. 𝑓is the identity op… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.6 (p.5)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig06.png]]
> [!tip] 【图文联合解读】图以对数刻度数据并行规模d（1→64）为横轴、气泡占比（0–1.0）为纵轴，呈现n=32/128、b′=B/b∈{32,128,512}四组曲线。关键数据：①n=32,b′=32时，d=1处气泡≈0.97、d=32降至0；②n=128,b′=512全程仅约0.12–0.25；③n=128,b′=128即便d=64气泡仍≈0.50。结论：b′（每阶段microbatch数）是气泡主导因素——b′越大气泡越低；固定b′时n↑（即流水线深度↑）气泡随之上升。论文借此量化"流水线空泡与并行配置的关系"，为数据并行度与微批规模的选择提供实验依据，支撑整体并行策略与调度优化的论证。
*caption: Fraction of time spent idling due to pipeline flush (pipeline bubble size) versus data-parallel size (𝑑), for different numbers of GPUs (𝑛) and ratio … ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.7 (p.6)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig07.png]]
> [!tip] 【图文联合解读】**图7联合解读：**

1) **核心数据**：1B参数GPT模型（128头/h=4096/4层）的单卡吞吐量随microbatch变化曲线。尺寸1→16时，每GPU吞吐量由约68 TFLOP/s单调升至约91 TFLOP/s，但增益递减明显（1→2增约9，8→16仅增约2），呈对数饱和趋势。

2) **关键结论**：增大microbatch可摊薄kernel launch等固定开销、提升GPU利用率；存在明显"甜点区"（约8–16），过小则算力浪费，过大收益饱和。

3) **作用定位**：作为单卡baseline，验证microbatch对计算效率的影响，为后续张量并行与流水线并行的batch配置提供经验依据，是模型并行前确认最优工作负载的关键前置实验。
*caption: Per-GPU throughput versus microbatch size for a GPT model with a billion parameters (128 attention heads, hidden size of 4096, 4 transformer layers).… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.8 (p.6)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig08.png]]
> [!tip] 【图文联合解读】**Figure 8 图文联合解读**

1) **核心内容**：展示同一GPT模型在总batch size=128（蓝圆）与512（橙菱）下，归一化吞吐随microbatch size *b*∈{1,2,4,8,16} 的曲线。蓝线在 *b*=2–4 达峰≈1.10，*b*=16 骤降至≈0.75；橙线在 *b*=4 达峰≈1.22，*b*=16 仍保持≈1.11，整体更平稳且始终高于蓝线。

2) **关键技术结论**：microbatch 存在最优值——*b* 太小则 GPU kernel 效率低（*t_f*/*t_b* 大），*b* 太大则流水线 bubble 成本（*p*−1 项）激增；更大的总 batch（如512）能更稳定地承受较大 microbatch。

3) **论文中的作用**：与 Fig.7（*t_f*/*t_b* 标度）配套，将"单步时间"与"流水线 bubble"两类代价合成吞吐公式，量化 microbatch 调优权衡，是 Megatron-LM 分布式训练配置准则的核心实验支撑。
*caption: Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·  𝑡𝑓(𝑏) + 𝑡𝑏(𝑏)) with respect to the mi- crobatch size 𝑏for the same … ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.9 (p.7)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig09.png]]
> [!tip] 【图文联合解读】**图9解读：**

**1）核心对象与结构：** 图以4块GPU（编号1–4）分属两个节点的流水线阶段（浅蓝块GPUs 1、2为阶段一，深蓝块GPUs 3、4为阶段二）为对象。(a) 中节点内NVLink用于层间通信，跨节点InfiniBand需传输完整红色张量块；(b) 中发送端按头维度将张量切分为若干小块（浅红色）经InfiniBand分发，接收端通过all-gather重新拼合为完整张量（深红色）。

**2）关键技术结论：** scatter/gather优化把InfiniBand链路传输的张量从完整粒度降为分片粒度，等效降低了跨节点带宽占用，同时保持计算结果等价。

**3）在论文中的作用：** 该图是Megatron-LM张量并行–流水线并行跨节点通信优化的核心论据，支撑其在大规模GPU集群上保持高扩展效率的整体方法链。
*caption: Scatter/gather communication optimization. Light blue blocks are layers in the first pipeline stage, and dark blue blocks are layers in the second pip… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.10 (p.8)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示四组配置下每GPU吞吐量（TFLOP/s）随GPU数（768→1920+）的变化。橙色PTD-P两条曲线稳定在140–170 TFLOP/s区间，几乎不随规模衰减；蓝色ZeRO-3则从约145急剧下滑至45–50，175B模型降幅最显著（仅剩约1/3）。论文借此论证：纯数据并行方案（ZeRO-3）在GPU增多后通信开销主导，性能严重退化；而PTD-P结合张量、流水线与数据并行的混合策略保持近线性高效扩展，支撑了Megatron-LM方法体系的核心结论——大规模模型训练必须采用混合并行而非单纯数据并行，以获得可扩展的吞吐。
*caption: Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B GPT-3 model is shown with dotted lines, and the 530B model is shown wi… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.11 (p.9)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig11.png]]
> [!tip] 【图文联合解读】**图11 联合解读**

1) **核心数据**：横轴为流水线并行度 P∈{1,2,4,8}，纵轴为单 GPU 吞吐量(TFLOPS/s)。batch=8(蓝)由 P=1 的 ~165 降至 P=8 的 ~88，跌幅近 47%；batch=128(橙)则从 ~178 仅缓降至 ~163(约 8%)，基本水平。

2) **关键结论**：弱扩展(模型随 P 增大)下，pipeline bubble 开销在小 batch 时无法被摊薄，导致每 GPU 吞吐显著下降；而 batch 足够大时，bubble 被掩盖，pipeline parallel 接近线性扩展。

3) **在论文中的作用**：该图支撑"pipeline parallelism 需配合足够大的 micro-batch 才能高效"的核心论点，与文中 1F1B 调度分析互为印证，是论证大规模训练组合策略(tensor+pipeline+data)可行性的关键实验证据。
*caption: Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.12 (p.9)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图横轴为 batch size（12–60），纵轴为每 GPU 实现的 teraFLOP/s，蓝色圆点为非交错（non-interleaved）调度，橙色菱形为交错（interleaved）调度，对比 175B 参数 GPT 模型在 96 GPU 上的吞吐。可读关键数据：BS=12 时非交错约 82、交替约 119（差距最大 ~37 TFLOP/s）；BS=24 时约 109 vs 134；BS=36 时约 122 vs 141；BS=48 时约 130 vs 143；BS=60 时约 135 vs 146，随 batch 增大差距收窄并趋于饱和。

**技术结论：** 交错调度在各 batch 下均显著优于非交错，且在小 batch 时收益更突出，证明通过将模型层切分为更细的子阶段（虚拟阶段）并交替执行，能有效缓解流水线气泡。

**论文作用：** 该图为本文核心创新——Interleaved 1F1B 流水线并行调度——提供了 175B 大规模模型上的端到端性能证据，是支撑该调度方案有效性的关键实验图。
*caption: Throughput per GPU of interleaved and non-interleaved schedules for a GPT model (175 billion parameters) on 96 GPUs. and a microbatch size of 1. As we… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.13 (p.9)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图13展示64块A100训练162.2B参数GPT模型时，五种(流水线并行度, 张量并行度)=(2,32)/(4,16)/(8,8)/(16,4)/(32,2)配置下的单GPU吞吐量(TFLOPS/s)。两条曲线分别对应batch=32(蓝)与128(橙)：batch=128全程高于batch=32，前者在(8,8)处峰值约165 TFLOPS/s，后者峰约142；在高流水线配置(16,4)与(32,2)处大小batch落差最大(差~50–60 TFLOPS/s)，而小batch在(8,8)两侧迅速衰减。

**论证结论**：两种并行的配比显著影响吞吐，二者不可极端化；大batch可有效掩盖流水线空泡(bubble)，使高流水线配置仍保持高性能。

**论文作用**：作为Figure 12(纯张量并行)的对照，本图直接验证了Megatron-LM"流水线并行+张量并行"联合方案的核心主张——通过合理拆分即可高效训练百亿级以上模型，构成其方法学闭环的关键实验证据。
*caption: Throughput per GPU of various parallel configurations that combine pipeline and tensor model parallelism using a GPT model with 162.2 billion paramete… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.14 (p.10)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示5.9B参数GPT在64块A100上不同(流水线并行度,数据并行度)配置的单GPU吞吐量：批大小=32时，从(2,32)的约62 TFLOP/s单调降至(32,2)的约42 TFLOP/s；批大小=512时，从约148降至约90 TFLOP/s。两条曲线随流水线深度增加均呈下降趋势，原文借此论证：**在该模型规模与GPU数量下，数据并行效率高于管道并行**，pure-data-parallel配置最划算，而增大pipeline会因气泡(bubble)开销显著降低每GPU吞吐。该图为论文并行策略选择（Figure 13/14共同构成扩展性实验）提供了量化依据，是支撑"Megatron在并行配置空间仍具高效率"这一整体结论的关键数据点。
*caption: Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, … ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.15 (p.10)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig15.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据**
该图横轴为五种(TP, DP)组合：(2,32)、(4,16)、(8,8)、(16,4)、(32,2)，纵轴为单 GPU 吞吐量 (tFLOP/s，0–200)。三条曲线对应 BS=32(蓝)、128(橙)、512(绿)。起点：BS=512 约 128、BS=128 约 103、BS=32 约 58；随TP增大均持续下滑，至 (32,2) 时三者收敛至约 22–25 tFLOP/s。

**2) 关键技术结论**
原文用以论证：随 TP 规模由 2 增至 32，三批大小曲线均从 ~125 骤降至 ~25 tFLOP/s，根源是 all-to-all 通信开销主导——一味放大张量并行反成性能瓶颈。

**3) 在论文链路中的作用**
作为"组合并行配置敏感性"实验的关键证据，支撑"TP 不应盲目放大、需与 DP 协同配置"的并行策略准则，与 Figure 14/16 共同构成 Megatron-LM 并行规模选择的方法学依据。
*caption: Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, th… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.16 (p.10)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图16展示在 **(t,p)=(8,8)** 并行、**64卡 A100** 训练 **91B 参数 GPT** 时，单卡吞吐（纵轴 teraFLOP/s，0–200）随 microbatch（横轴 1/2/4/8，对数刻度）的变化，含 batch=128 与 batch=512 两条曲线。**橙色（512）**：约 163→172→160→155，全程近乎平坦，峰值 ≈172 TF/s；**蓝色（128）**：约 155→158→140→120，microbatch ≥4 后明显下滑。

**关键结论**：batch=512 时对 microbatch 大小极不敏感（强鲁棒），逼近算力峰值；batch=128 较大 microbatch 会因整批 microbatch 数少、流水线气泡占比相对增大而损失吞吐。

**在论文中的作用**：作为扩展性实验的一环，量化验证"张量并行 + 流水线并行"组合在千亿参数规模、用较小 microbatch 仍可保近峰效率，为 Megatron-LM 在大规模训练上的方法论高效性提供直接实证支撑。
*caption: Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different microbatch sizes on a GPT model with 91 billion parameters, for two dif… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.17 (p.11)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig17.png]]
> [!tip] 【图文联合解读】**图17联合解读**

该图刻画145B参数GPT模型在128块A100上的吞吐量（sequences/秒）随batch size（1–256，对数刻度）的变化，对比启用与停用activation recomputation（蓝圆 vs 橙菱）。橙色"W/o act. recomp"曲线仅至batch=8即达约4 seq/s，因显存耗尽（OOM）终止；蓝色曲线则持续爬升至batch=256时约7.8 seq/s。值得注意的是在batch≤8区间，无recomp略高（~4 vs ~3），恰好暴露了重计算的算力开销。

原文据此论证：以算力换显存的重计算可将可用batch从8扩展到256，使吞吐量近似翻倍，是百亿级模型训练的必备技术。

其作用在论文整体方法链中，呼应"张量并行+流水并行+混合精度+重计算"的可扩展训练体系，为大规模模型训练落地提供关键memory-saving抓手。
*caption: Throughput (in sequences per second) with and without activation recomputation for a GPT model with 145 billion param- eters using 128 A100 GPUs ((𝑡, … ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Efficient Large-Scale Language Model Training on GPU Cluster — Fig.18 (p.11)
![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig18.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）图表为折线对比图，横轴为批大小（12/24/36/48/60），纵轴为每GPU达成算力（50–150 teraFLOP/s），含两条曲线：未优化（蓝圈）在各批大小下达约107/120/127/130/131 TFLOPS，散射-收集优化（橙菱）达约119/134/142/144/147 TFLOPS。

2）原文借此论证：在96张A100上训练175B参数GPT-3并采用交错调度时，散射-收集通信优化在所有批大小下均稳定优于未优化基线，批大小60时差距约16 TFLOPS（147 vs 131），验证了该优化对张量并行流水线通信瓶颈的缓解效果。

3）该图属于消融/优化效果验证实验，为Megatron-LM在大规模集群上实现高效训练的工程方案提供量化支撑，是证明所提通信优化必要性与有效性的关键实证。
*caption: Throughput per GPU with and without the scatter/gather optimization for a GPT model with 175 billion parameters using 96 A100 GPUs and the interleaved… ｜ 论文 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] ｜ arxiv 见 MD 元信息*

### Megatron-LM: Training Multi-Billion Parameter Language Model — Fig.1 (p.2)
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图1为对数-对数坐标下 PetaFLOPs/s 随 GPU 数的变化：蓝色模型并行（1–8 卡，≈0.04→0.23 PFLOPs/s）；绿色模型+数据并行（64–512 卡，≈2.5→16 PFLOPs/s），两段曲线均紧贴灰色"线性"虚线参考。结论：纯模型并行与"模型+数据"混合并行均实现近似线性的弱扩展效率，512 卡达到 ~16 PFLOPs/s。作用：在论文主体提出 transformer 层内 MLP/Attention 切分优化之前，先以实测 FLOPS 证明并行框架具备近线性可扩展性，为后续大模型训练方案奠定可行性基础。
*caption: Model (blue) and model+data (green) parallel FLOPS as a function of number of GPUs. Model parallel (blue): up to 8-way model parallel weak scaling wit… ｜ 论文 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] ｜ arxiv 见 MD 元信息*

### Megatron-LM: Training Multi-Billion Parameter Language Model — Fig.2 (p.3)
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig02.png]]
> [!tip] 【图文联合解读】该图展示Transformer单层数据流：输入嵌入→Layer Norm→Attention子层（Self-Attention+Dropout+残差Add）→Layer Norm→MLP子层（H→4H经GeLU激活后4H→H，含Dropout与残差Add），整个块重复x L次后接输出层。紫色块为全连接层，MLP含4倍维度扩展。原文以此论证Transformer结构高度规整且MLP参数占比巨大，为后续按注意力头和MLP维度进行张量切分的模型并行方案提供结构基础，是实现千亿参数高效训练的关键依据。
*caption: Transformer Architecture. Purple blocks correspond to fully connected layers. Each blue block represents a single trans- former layer that is replicat… ｜ 论文 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] ｜ arxiv 见 MD 元信息*

### Megatron-LM: Training Multi-Billion Parameter Language Model — Fig.3 (p.4)
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图示 Transformer 块的两个子模块——(a) MLP 和 (b) Self-Attention——沿纵向切分至 2 个 GPU。MLP 中 X 经 f 算子分为 A₁、A₂ 两路并行计算后由 g 合并；Self-Attention 中 X 经 f 分为两组注意力头（Q₁/Q₂、K₁/K₂、V₁/V₂），并行 Softmax+Dropout 后拼接输出。

**2) 关键技术结论：** f 与 g 是**共轭算子**——f 在前向为恒等、反向为 all-reduce；g 在前向为 all-reduce、反向为恒等。即一次通信在前向与反向间复用，避免冗余同步，仅在子模块边界处通信即可完成跨 GPU 计算。

**3) 在论文中的作用：** 该图是 Megatron-LM 模型并行的基本构建块，论证了 MLP 列切分与 Attention 头切分均无需额外参数同步即可正确反向传播，为后续训练 83 亿/175 亿参数模型提供了核心并行原语与通信正确性保证。
*caption: Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an identity operator in the forward pass and all reduce in the backward pass… ｜ 论文 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] ｜ arxiv 见 MD 元信息*

### Megatron-LM: Training Multi-Billion Parameter Language Model — Fig.4 (p.5)
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示单个模型并行 Transformer 层。流水线为 X → LayerNorm → Self-Attention(Q/K/V Linear + 输出 Linear) → Dropout → 残差⊕ → LayerNorm → MLP(Linear → GeLU → Linear) → Dropout → 残差⊕ → Y。其中 Self-Attention 与 MLP 两块以虚框标注为"Model Parallel"（各占一份权重分片），LayerNorm/Dropout/⊕在每卡本地复制。**每层共 4 次 all-reduce**：两块各在 fwd+bwd 中各 1 次（每个 Model Parallel 块对应 "2 All-Reduces"）。

2) **原文论证的关键结论**：在列并行 GEMM Y_i = X A_i 下，每块前向需 1 次 all-reduce 聚合 Y；反向梯度 ∂X 需另 1 次 all-reduce。故单层前向+反向共 4 次集合通信，**与层数线性、与数据并行组解耦**，通信量可控。

3) **整体方法链作用**：这是 Megatron 张量并行的"通信账本"基础——证明仅靠列并行+行并行（无参数服务器、无额外同步）即可扩展到数十亿参数，为后续 PTD-P（与流水并行/Pipeline 组合）及在 8/16 卡 DGX 上训练 GPT-3 8.3B/22.4B 提供通信开销量化的理论依据。
*caption: Communication operations in a transformer layer. There are 4 total communication operations in the forward and backward pass of a single model paralle… ｜ 论文 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] ｜ arxiv 见 MD 元信息*

### Megatron-LM: Training Multi-Billion Parameter Language Model — Fig.5 (p.6)
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig05.png]]
> [!tip] 【图文联合解读】**图5图文联合解读：**

图5展示两类并行的弱扩展效率：模型并行（1→8 GPU）由100%降至77%；模型+数据并行（64→512 GPU）由96%缓降至74%。原文借此论证：扩展至512卡时效率仍保持74%以上，证明模型并行及与数据并行结合可有效训练超大模型，突破单卡显存限制并保持高利用率，为论文核心实验提供关键支撑。
*caption: Model and model + data parallel weak scaling efﬁciency as a function of the number of GPUs. done by scaling the batch-size, however, this approach doe… ｜ 论文 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] ｜ arxiv 见 MD 元信息*

### Megatron-LM: Training Multi-Billion Parameter Language Model — Fig.6 (p.7)
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig06.png]]
> [!tip] 【图文联合解读】**图示核心：** 横轴为训练迭代次数（0–300k），纵轴为验证集 LM 困惑度（8–24）。三条曲线分别对应 355M（蓝，收敛于 ~15）、2.5B（红，~11）、8.3B（黄，~9）三个 GPT-2 模型，均训练 300k 迭代。

**关键结论：** 在相同迭代预算下，模型规模越大，下降越陡、收敛越快、终值困惑度越低，明确证实了参数规模与收敛性能的扩展效应（scaling effect）。

**论文作用：** 该图直接服务于核心论点——即所提出的模型并行方案可成功训练出数十亿参数 Transformer 并获得更优下游能力。它以收敛曲线为关键实证，回击了对超大模型训练可行性的质疑，支撑后文 8.3B 模型质量评估的合理性。
*caption: Validation set perplexity. All language models are trained for 300k iterations. Larger language models converge notice- ably faster and converge to lo… ｜ 论文 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] ｜ arxiv 见 MD 元信息*

### Megatron-LM: Training Multi-Billion Parameter Language Model — Fig.7 (p.8)
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig07.png]]
> [!tip] 【图文联合解读】图左半对比Transformer块：(a)原始结构为LN→Self-Attn+残差→LN→MLP+残差；(b)将LN置于残差之后、调整其位置。右半为训练loss曲线（0–500k次迭代，纵轴0–8）：752M模型采用(a)时在约230k iter处loss骤升至~7（训练发散），336M用(a)与752M用(b)均稳定下降至~1.0–1.3。

**核心结论**：原始架构在752M规模出现训练不稳定/发散，而调整LN放置位置的(b)架构可实现稳定收敛并取得更低loss。

**论文作用**：为模型并行扩展至数十亿参数所必需的Transformer架构改造（LN-残差顺序调整）提供了直接实验验证，是支撑后续GPT类大规模模型训练的稳定性基础。
*caption: Training loss for BERT model using the original architec- ture (a) and the rearranged architecture (b). Left ﬁgure shows the training loss for 336M an… ｜ 论文 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] ｜ arxiv 见 MD 元信息*

### Megatron-LM: Training Multi-Billion Parameter Language Model — Fig.8 (p.12)
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig08.png]]
> [!tip] 【图文联合解读】图示512块GPU的两级组织：纵向64个**model parallel group**，每组8卡（GPU-1~8…505~512），承担Transformer层张量切分；横向8个**data parallel group**跨各模型组按对应位置GPU互连（如各组第k卡聚合），构成64路数据并行维度。

**论证结论**：8路模型并行与64路数据并行可正交组合，既缓解单卡显存瓶颈，又通过batch维扩展吞吐。

**论文作用**：作为方法部分混合并行（hybrid parallelism）方案的拓扑实例，与Figure 7互补，支撑"在512卡集群上高效训练多百亿参数模型"这一核心可扩展性论断。
*caption: Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel and 64-way data parallel. C. Text Samples… ｜ 论文 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.1 (p.2)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读**

**1) 图示内容**：该图呈现论文的整体结构框架，展示了4个并列的技术维度章节及子节：§4并行策略（4.1混合并行、4.2自动并行、4.3异构并行，各1子节）、§5计算优化（5.1算子优化、5.2混合精度训练）、§7集合通信（7.1集合通信、7.2通信调度、7.3网内聚合）、§8容错（8.1故障分析、8.2异常检测、8.3检查点恢复、8.4无检查点恢复，共4子节最多）。

**2) 论证结论**：原文用此图论证分布式大模型训练效率可沿"并行—计算—通信—容错"四层栈式分解，每层含具体子技术（如并行3类、通信3类、容错4类）。

**3) 论文作用**：作为综述的导航图，为读者提供分类索引，明确各优化技术在整个训练流水线中的层级定位与覆盖范围。
*caption: Overall structure of this survey.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.2 (p.3)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图2将典型Transformer层拆为两大块：左侧Attention块含Norm、融合投影Linear(Wqkv)、Q/K/V三路送入MHA/GQA、再经Linear(Wo)输出，最后残差相加⊕；右侧FFN块为SwiGLU结构——Norm后Linear(W1)经SiLU与Linear(W3)逐元素相乘⊙，再由Linear(W2)映射回原维度并残差相连。全层共6个权重矩阵、2次Norm、2处残差。

论文借此论证：Transformer层是分布式训练（TP/PP/DP）的基本切分与调度单元，Attention（GEMM+集合通信）与FFN（纯GEMM）的计算/通信特性差异决定了不同的并行与重计算策略。该图为后续混合精度、激活检查点、序列并行等优化讨论提供了统一的计算图参考。
*caption: A typical Transformer layer contains an Attention… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.3 (p.4)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig03.png]]
> [!tip] 【图文联合解读】**图3图文联合解读**

图示将分布式LLM训练基础设施划分为左右两平面：左侧**数据面**自上而下依次为Backend Network（承载训练流量）→4个Compute Node→Frontend Network（管理与存储流量）→Training Dataset Storage与Checkpoint Storage；右侧**控制面**包含Scheduling System，以及Fault Tolerance子系统（细分Anomaly Detection与Failure Recover）。

**论证结论**：分布式LLM高效训练不仅依赖算力横向扩展，更需前后端网络解耦（分离训练流量与管控/存储流量）、存储分层（数据集与检查点独立），并通过调度与容错子系统协同保障大规模训练的稳定性与可恢复性。

**论文作用**：作为综述的总览架构图，统摄后续对并行计算、网络拓扑、存储优化、调度策略与容错机制等章节的系统化论述，构成全篇方法学的整体框架。
*caption: Infrastructure overview for distributed LLM training.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.4 (p.5)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图中将分布式LLM训练的基础设施优化研究分为两大类别（可视为按优化主题的分类表）：

**第一类（资源调度与分配类，12项）**：Tiresias、THEMIS、ElasticFlow、Gavel、Gandiva_fair、FGD、Lucid、Pollux、Sia、Crius、Hydro、Acme，主要聚焦GPU/作业调度与公平性。

**第二类（系统效率与弹性类，7项）**：Cassini、HIRE、SiloD、Synergy、EnvPipe、Zeus、Perseus，侧重流水线、弹性伸缩、能效与容错。

**原文论证结论**：作者通过该分类表系统梳理了"基础设施优化"这一维度的代表性工作，凸显调度、弹性、效率三大研究主线，为后续讨论并行策略与算法优化奠定对比基线。

**论文作用**：作为综述的方法学骨架之一，与算法层优化形成"算法×基础设施"双维度分类图谱，帮助读者快速定位研究坐标。
*caption: Studies on infrastructure optimizations for distributed LLM training.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.5 (p.6)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig05.png]]
> [!tip] 【图文联合解读】图5展示五种芯片间互连拓扑：(a)树形——1个Root Complex经PCIe Switch分层挂接16片芯片；(b)Cube-Mesh——8节点构成3D立方体邻接；(c)交换全连接——2个NVSwitch各自将上下两组芯片全连；(d)P2P全连接——8节点两两直连，呈完全图；(e)2D-Torus——4×4网格，含红色行向与蓝色列向环绕边。

论文据此论证：各拓扑在带宽、延迟、可扩展性与成本间存在显著权衡——树形廉价但根节点处易成瓶颈；Cube-Mesh结构平衡；NVSwitch全连（如NVLink）提供高带宽；P2P延迟最低但N²连线难以扩展；2D-Torus（如TPU Pod）利于大规模部署但AllReduce需特殊映射。

作用：作为后续讨论3D并行（TP/PP/DP）通信模式与节点内拓扑选型匹配的硬件基础铺垫。
*caption: Five chip-to-chip topologies: tree topology, cube-mesh topology, switch-based fully-connected topology, P2P-based… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.6 (p.7)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig06.png]]
> [!tip] 【图文联合解读】图6展示大规模GPU集群四种典型网络拓扑（2 Pod 并列，每Pod含2 Spine + 2 Leaf + 每Leaf下挂8 GPU节点）：(a) Clos——Core(2)-Spine(4)-Leaf(4)三级直连，叶仅连本Pod；(b) Dragonfly+——省去Core层，两Pod Spine间以弧形长线直接跨Pod互连；(c) Rail-Optimized——保留Core-Spine层，但每Leaf横向扇出至对Pod GPU（底部大量交叉连线），带宽局部优化；(d) Rail-Only——仅本Pod内Leaf-GPU链路，无跨Pod底层通路。原文借此论证：拓扑决定All-Reduce等集合通信的对分带宽与最短路径，直接影响DP/TP/PP并行切分及计算-通信重叠效率。该图为后续章节搭建"硬件拓扑→并行策略→训练效率"的物理前提，是连接基础设施与算法优化的枢纽图示。
*caption: Four typical network topologies in large-scale GPU clusters: Clos topology, Dragonfly+ topology, rail-optimization… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.7 (p.10)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig07.png]]
> [!tip] 【图文联合解读】**图7联合解读：**

**核心对象与结构**：图7将分布式LLM训练的并行方案研究分为两类列表呈现——上框列举12项并行方案研究（HetPipe [221]、AccPar [222]、Whale [223]、AMP [224]、Pathways [225]、HPH [226]、SDPipe [227]、HAP [228]、PipePar [229]、Yuan et al. [230]、SWARM [231]、FusionAI [232]），涵盖异构流水线、自动并行等系统级方案；下框列举6项RLHF训练系统（DeepSpeed-Chat [233]、HuggingFace TRL [234]、OpenRLHF [235]、Adaptive Placement and Parallelism [236]、ReaLHF [237]、PUZZLE [238]），聚焦强化学习微调场景。

**技术结论**：通过分类列举，揭示分布式LLM训练并行技术已从单一流水线/数据并行拓展到异构资源调度、自动并行搜索及RLHF专用框架等多元路径，技术生态丰富且针对不同训练阶段（预训练、对齐）有专门优化。

**论文作用**：作为综述章节的分类总览图，为后续深入讨论各类并行策略提供文献索引框架，便于读者快速定位相关工作。
*caption: Studies on parallelism schemes for distributed LLM training.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.8 (p.12)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 8）：**

该图以一个16层LLM为例，展示三层并行嵌套结构：外层为2个Data Parallel副本（Rank 0/1），通过AllReduce同步梯度；内层包含4个Pipeline Stage（0/1/2/4，跳号编排），分别承载Layers 0-3、4-7、8-11、12-15，Stage间以Send/Recv传递激活值；每个Stage内部进一步切分为4个Tensor Parallel分片（TP-0至TP-3）。原图还嵌入Sequence Parallel层。

原文借此论证：**DP解决数据扩展、PP分摊层间计算与内存、TP分摊单层显存**，三者正交可叠加，是支撑千亿级LLM在分布式集群上训练的核心组合范式。在全文方法链中，该图为"并行策略分类与组合"章节的实例化说明，为后续ZeRO、激活重计算等内存优化技术的讨论奠定拓扑基础。
*caption: An example of 3D-parallelism with data parallelism, tensor parallelism, and pipeline parallelism.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.9 (p.14)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig09.png]]
> [!tip] 【图文联合解读】图示N设备专家并行架构：每个设备独占一个Expert（图示Expert-1与Expert-N），Embedding/Attention/Add&Norm层跨设备复制；Token经Gating路由后，由All-to-All Dispatch分发至各设备Expert，再经All-to-All回传汇合，经Add&Norm生成输出Token。

论证结论：Expert分片部署配合两次All-to-All通信实现跨设备协作，可在显存受限下扩展MoE参数容量并保持负载均衡，是大规模MoE分布式训练的核心并行策略。

论文作用：与数据并行、张量并行、流水线并行并列，作为综述中支撑"参数与稀疏容量扩展"章节的关键配图。
*caption: Expert parallelism. The dotted line highlights the… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.10 (p.17)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig10.png]]
> [!tip] 【图文联合解读】**核心对象与结构**：该图为 RLHF 四模型协作数据流图。包含 2 个可训练模型（Actor Model、Critic Model，红色）与 2 个冻结模型（Reference Model、Reward Model，蓝色），并标注三步流程：① Actor 由 query 集 x₁…xₙ 生成 response y₁…yₙ；② Critic/Reference/Reward 推理产出 value、score、KL 估计；③ 训练信号回传 Actor 与 Critic。

**关键结论**：RLHF 需协同 4 个异构模型并交替执行"推理—评分—训练"，其中 2 个冻结、2 个可训练，证明 RLHF 对分布式显存、通信与调度均提出高于普通 SFT 的资源需求。

**论文作用**：作为 RLHF 训练范式章节的结构锚点，为后文分布式优化策略（模型并行、显存管理等）提供动机与需求基线。
*caption: An example of RLHF. Inference process: 1 The… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.11 (p.19)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig11.png]]
> [!tip] 【图文联合解读】**核心对象**：分类树状结构，列出分布式LLM训练中4类计算优化研究及约22项代表性工作：
① **编译优化**（左侧标签 "…tions"）：Kernel级（Halide[267]、TVM[252]、Roller[268]、Triton[269]、ALCOP[270]）；Graph级（Chimera[271]、Welder[272]、Slapo[203]、TorchDynamo&TorchInductor[273]、JIT-Q[274]）。
② **混合精度**（标签 "…int"）：FP16 [275]、Campgo[276]、BF16 [277]、THC[278]。
③ **亚字节精度**（标签 "…oint"）：Wang et al.[279]、Sun et al.[280]、FP8-LM[281]、Rouhani[282]。
④ **量化**（标签 "…nt"）：INT8-Jetfire[283]、INT4-Xi[284]、1-Bit-BitNet[285]/b1.58[286]。

**关键论证**：计算优化从**编译器层级**（kernel、graph）到**数值精度层级**（mixed precision、sub-byte、quantization）逐级压降算力与显存，是分布式训练效率提升的关键技术支柱。

**论文作用**：作为综述对"计算优化"子领域的系统分类索引，与通信优化、并行策略、内存优化等并列，构成完整分布式LLM训练优化全景图。
*caption: Studies on computation optimizations for distributed LLM training.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.12 (p.21)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig12.png]]
> [!tip] 【图文联合解读】图12展示分布式LLM训练内存优化研究的分类树（局部）。顶部框为"卸载（Offloading）"，细分为静态卸载（L2L、ZeRO-Offload、Elixir、Yuan et al.，共4项）与动态卸载（TSPLIT、PatrickStar、Mobius、Harmony、TMOF、STRONGHOLD，共6项）；下方框列举另一类共6项工作（ZeRO-Infinity、Angel-PTM、Smart-Infinity、Fuyou、MoESys等），对应异构存储扩展显存方案。原文据此论证：内存优化研究沿"卸载"与"异构显存扩展"两条路径展开，均通过CPU/NVMe分担GPU显存压力。该图为论文方法综述章节的子分类支撑，系统梳理分布式训练栈，缓解大模型训练的内存瓶颈。
*caption: Studies on memory optimizations for distributed LLM training.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.13 (p.25)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 13）：**

该图为128×128 GPU对通信热力图，量化展示InternLM-2 102B单次迭代在TP=8/PP=4/DP=4/ZeRO-1=4配置下的通信量（256MB–12GB）。

**结构特征**：
- 对角线有16个8×8深紫方块（16组TP群组），单次AllReduce峰值达12GB，为最重通信；
- 蓝色点状散点对应DP/ZeRO群组内通信，强度次之；
- 黄色对角线代表PP点对点通信，仅256MB量级，最轻。

**关键结论**：通信强度呈 TP > DP/ZeRO > PP 的明确层次，验证了"按通信强度优先级排布拓扑"的设计原则——需将高带宽TP通信约束在NVLink域内。

**论文作用**：作为实验证据支撑第7章集体通信优化讨论，证明分层并行中不同维度通信开销差异巨大，是拓扑感知调度与集合通信算法选择的核心依据。
*caption: Communication traffic heatmap for InternLM-2… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.14 (p.26)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图14以三层分层结构（左标签被截断，依内容可还原为**Scheduling/ Aggregation/ Delegation**）梳理分布式LLM训练的通信优化研究：

- **上层（调度）**：分四子类——流水线阶段分解（Breadth-First[159]、Fold3D[351]、TriRace[352]）、通信分解（SYNDICATE[354]等4项）、计算分解（CoCoNet[357]等4项）、乱序反向传播[361]，共12篇。
- **中层（聚合）**：SwitchML[362]、FPISA[363]等6种可编程交换机方案。
- **下层（委派）**：仅NVIDIA Mellanox SHARP v1/v2/v3[368]一项，指向硬件卸载。

**论证结论**：通信优化呈"软→硬"分层谱系，从算法调度到网络设备卸载，互补共存。

**论文作用**：作为综述通信优化章节的方法学分类地图，为读者快速定位各层代表工作与选型权衡提供索引。
*caption: Studies on communication optimizations for distributed LLM training.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Training of Large Language Models on Distributed I — Fig.15 (p.29)
![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig15.png]]
> [!tip] 【图文联合解读】**图文联合解读（图15）**

该图以分类树形式系统梳理分布式LLM训练容错技术，左侧为四类主干（Checkpointing、Recomputing、Parcae/Oobleck类、Elasticity），右侧罗列代表性工作，共19项：Checkpointing下细分**同步**（DeepSpeed、Varuna、JIT-/Flash-/Universal Checkpointing，5项）、**Snapshot-Stall**（Check-N-Run、TorchSnapshot，2项）、**异步**（DeepFreeze、CheckFreq、LightCheck、DataStates-LLM、FastPersist，5项）；其余三行各列2–3项。

原文借此论证：容错设计存在**同步开销、快照粒度与弹性恢复**间的权衡——主流方案由同步快照逐步演进到异步检查点与弹性冗余。图中各子类的划分与文献编号直接支撑全文"训练效率优化"谱系中的**可靠性分支**，与并行、通信、内存优化并列，是综述方法分类的重要组成部分。
*caption: Studies on fault tolerance techniques for distributed LLM training.… ｜ 论文 [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.1 (p.1)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig01.png]]
> [!tip] 【图文联合解读】左图量化展示 A100 40GB 显存分配：参数 26GB(65%) 常驻，KV Cache >30% 按请求动态分配，激活仅小片。右图双曲线对比：现有系统(橙)batch≈8 即显存触顶 39GB、吞吐仅 ~0.3k tok/s；vLLM(蓝)线性缓增、batch=40 仍可服务，吞吐稳 ~0.9k tok/s。作用：开篇动机图，揭示传统 KV 连续分配引致内部碎片严重、batch 受限，锚定 PagedAttention 分页方案——碎片降至 sub-block 量级、吞吐提升 2–4×，为全文方法与实验铺垫论证基础。
*caption: Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.2 (p.2)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig02.png]]
> [!tip] 【图文联合解读】该图以堆叠柱状图对比四个系统的KV缓存利用率构成：Orca(Max)仅20.4%用于token states，57.3%被内部碎片吞噬；Orca(Pow2)、Orca(Oracle)虽改善分配，但仍因外部碎片（41.6%、36.6%）与过度预留（17.9%、25.2%）浪费大半；vLLM则将有效token states占比提升至96.3%，几乎消除各类碎片。数据直观证明：现有LLM服务系统因KV cache采用连续预分配策略，浪费了60–80%的宝贵显存。该量化基线为论文核心——PagedAttention以非连续分页机制消除KV cache碎片——提供了不可或缺的问题动机与对照基准。
*caption: Average percentage of memory wastes in different LLM serving systems during the experiment in §6.2. percentage of memory is used for other data, inclu… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.3 (p.4)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以一条水平连续内存条展示两段请求的KV cache分配：请求A占用7个prompt token槽("Four…fathers")+1个已生成token槽，并预留2个reserved槽，但其后留有**2038个从未使用的内部碎片**；请求B仅用3个prompt token槽+1个reserved槽，留有**507个内部碎片**；两段间的灰色间隙标注为**外部碎片(External fragmentation)**。

原文借此论证：现有系统因按最大序列长度**连续预分配**，同时产生reserved、internal fragmentation、external fragmentation三类浪费，使显存无法容纳更多并发请求。该图作为**动机图**，直接引出PagedAttention的核心思想——将KV cache拆为固定大小非连续"页"，借助块表映射消除碎片，从而在方法链路中奠定"页式显存管理"必要性的视觉证据基础。
*caption: KV cache memory management in existing systems. Three types of memory wastes – reserved, internal fragmentation, and external fragmentation – exist th… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.4 (p.5)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig04.png]]
> [!tip] 【图文联合解读】**图4联合解读（vLLM系统架构）**

1) **核心对象与结构**：图示含三类组件——中央**Scheduler**（调度器）通过有向边连接**KV Cache Manager**（内含两张Block tables网格）与N个并行**Worker**（每个Worker含Cache Engine+Model Shard+GPU）；KV Cache Manager下接**CPU/GPU Block Allocator**两个分配器。

2) **关键技术结论**：Scheduler集中管控请求调度；KV Cache Manager以Block Table为元数据，将GPU显存按"页"粒度（类OS虚拟内存）分配；CPU Block Allocator支持阻塞序列的溢出管理，证明PagedAttention可消除KV Cache碎片。

3) **论文整体作用**：此图是vLLM的系统总览，对应后续§4 PagedAttention算法的硬件落地——Scheduler+Block Manager实现"以页为单位的注意力计算"，是连接内存管理理论与实际GPU serving系统的桥梁，支撑了§5实验中高吞吐量的结果。
*caption: vLLM system overview.… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.5 (p.5)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示：左侧查询向量"forth"与右侧3个非连续KV块（块大小B=4）通过箭头建立注意力计算关系。Block1存"years/ago/our/fathers"，Block2存"brought/forth"（未填满），Block0存"Four/score/and/seven"；逻辑序列为0→1→2，但物理上分散、不相邻。

论证结论：原文给出分块注意力公式A_ij=exp(qᵢᵀK_j/√d)/Σ，证明softmax注意力可按固定大小块独立计算，KV向量无需在显存中连续存储，从而彻底解耦逻辑序列顺序与物理内存布局。

论文作用：作为PagedAttention算法的标志性图示，为后续block table虚实块映射机制、显存分页管理及高吞吐LLM serving的系统实现奠定直观基础。
*caption: Illustration of the PagedAttention algorithm, where the attention key and values vectors are stored as non-contiguous blocks in the memory. block size… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.6 (p.6)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig06.png]]
> [!tip] 【图文联合解读】**1) 核心结构（具体/量化）**：图示 Request A 的 KV 分页映射。4 个逻辑 KV 块（Block 0–3，每块容量 4 token）通过 Block Table 指向 GPU DRAM 上的物理块 **7、1、3**（序号非连续），表项含 "Physical block number" 与 "# filled"；新生成的 *fathers*、*brought* 使逻辑块 1 由 3→4、逻辑块 2 由 0→1，以黄色高亮。

**2) 论证的技术结论**：①逻辑–物理块解耦，物理块可非连续分配，消除外部碎片；②块内按 token 增量填充，`# filled` 追踪部分占用，避免预分配造成的内部浪费，并支持流式解码时原位追加。

**3) 在论文链路中的作用**：本图是 PagedAttention 的机制示意——把 OS 虚拟内存分页思想移植到 LLM 的 KV cache 管理，是后续显存高效利用、近零浪费以及请求间物理块共享等实验结论的方法论基础。
*caption: Block table translation in vLLM. divides it into physical KV blocks (this is also done on CPU RAM for swapping; see §4.5). The KV block manager also m… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.7 (p.6)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig07.png]]
> [!tip] 【图文联合解读】**图7 图文联合解读**

图示两并发请求（A："Four score and seven…"；B："It was the best of…"）的逻辑KV块经各自块表映射至共享的9块物理KV池（每块4 token）。物理分配**非连续且跨请求交错**：A 的逻辑块 0→物理 7、块 1→物理 1、块 2→物理 3；B 的逻辑块 1→物理 2；橙色高亮为 A 生成阶段新增 token，绿色为 B 的块。

**核心结论**：PagedAttention 通过逻辑–物理块映射的"类虚拟内存"机制，消除连续分配导致的内存碎片与浪费，支持多请求并发下的块级独立调度与跨请求内存共享（如公共前缀可共用物理块）。

**论文作用**：该图是 PagedAttention 核心机制最直观的设计级证据，为后续吞吐量、显存利用率等系统级实验提供方法基础，论证 vLLM 服务框架的可行性。
*caption: Storing the KV cache of two requests at the same time in vLLM. requests and the latest tokens for generation phase requests) as one sequence and feeds… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.8 (p.7)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig08.png]]
> [!tip] 【图文联合解读】该图展示两样本 A1、A2 并行采样的内存视图：二者 Logical Block 0（prompt "Four score and seven"）通过块表映射到同一 Physical Block 7，**Ref count=2**；当 A2 写"mothers"触发 Copy-on-write，原共享块被复制出新 Block 3（"fathers"），Ref count 由 2→1，两样本写入互不影响。原文借此论证：PagedAttention 的块级内存管理可在 prompt 共享 KV cache 的同时，仅在输出分歧处按块复制，兼顾显存节约与样本独立性，是 vLLM 高吞吐、低显存的关键设计支撑。
*caption: Parallel sampling example. generates a single sequence. In the remainder of this paper, we assume the more general case in which a request gener- ates… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.9 (p.7)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig09.png]]
> [!tip] 【图文联合解读】**图9 — Beam Search下的Paged KV缓存布局**

图示4条beam候选在block级KV缓存上的分配：**Block 0、Block 1**为全部beam共享的前缀块；候选0/1在**Block 3**处分叉，候选2/3在**Block 2**处分叉；带"×"标记的**Block 5、Block 2、Block 4、Block 8**代表其所属beam在后续步被剪枝，对应物理块随即被回收，复用为**Block 9–12**。

**原文论证的关键结论**：相较传统连续分配因beam间前缀重复和动态剪枝造成的严重碎片与显存浪费，paged block机制可同时实现①跨beam前缀KV共享与②被剪枝beam内存的即时释放，从而显著提升beam search场景下的显存利用率与批吞吐。

**在论文中的作用**：该图是PagedAttention针对beam decoding提出的内存管理方案的直观示例，与shared-prefix（Figure 7）、parallel sampling（Figure 8）共同构成"复杂采样场景"图示组，支撑全文核心论点——vLLM在多样化解码策略下均能逼近最优显存效率。
*caption: Beam search example. sample space. The algorithm relies on the beam width pa- rameter 𝑘, which determines the number of top candidates retained at eve… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.10 (p.8)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig10.png]]
> [!tip] 【图文联合解读】**Figure 10 图文联合解读**

**1) 核心对象与结构**
图中展示两个并行翻译请求（Sequence A 与 B）的三段式结构：
- **Shared prefix**（黄色共享段，~50 token）：两序列完全相同，含指令"Translate English to French:"及三个示例对（sea otter→loutre de mer / peppermint→menthe poivrée / plush giraffe→girafe en peluche）。
- **Task input**（绿色私有段）：A 为 `"cheese" =>`，B 为 `I love you =>`。
- **Task output**（蓝色私有段）：A 输出 `fromage`，B 输出 `Je t'aime`。

**2) 原文论证的技术结论**
两请求的 prefix 完全一致，意味着 LLM serving 中该部分会产生重复的 prefill 计算与 KV cache 存储；这正是 PagedAttention 引入 **block-level KV cache sharing** 的现实驱动力——共享前缀的物理页只需分配一次，多请求复用，节省显存并避免冗余计算。

**3) 在论文整体中的作用**
作为 vLLM 共享前缀优化（如 Copy-on-Write、块表复用）的典型用例图，证明 few-shot prompting 与 system prompt 场景下 prefix 共享具有普遍性，为后续性能收益（显存节省、吞吐提升）提供具体应用背景。
*caption: Shared prompt example for machine translation.… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.11 (p.9)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig11.png]]
> [!tip] 【图文联合解读】## 图文联合解读

**1. 核心对象与数据**
图(a) ShareGPT：输入长度均值 161.31 tokens，输出均值 337.99 tokens，分布跨度大，输出长尾延伸至 ~2000 tokens；图(b) Alpaca：输入均值仅 19.31，输出均值 58.45，两者均高度集中在 0–100 tokens 区间，密度峰值约 7–8×10⁻²。两个数据集的输入/输出长度均呈现**高度异构、长尾分布**特征，且输出长度方差显著大于输入。

**2. 关键论证结论**
请求长度（尤其是输出）不可预测且差异巨大，传统基于"最长预估长度预分配连续 KV cache"的方案会造成严重内部碎片与内存浪费；这正是 PagedAttention 提出**按页非连续分配、动态拼接**的动机——以分页机制应对任意长度的生成请求。

**3. 在论文链路中的作用**
位于评估章节开头，作为实验场景的真实数据画像：ShareGPT 代表长对话、长输出压力场景，Alpaca 代表短指令场景。两者互补地验证了 vLLM/PagedAttention 在**不同负载特征**下均能维持高吞吐，证明分页 KV 缓存机制具有通用性与鲁棒性。
*caption: Input and output length distributions of the (a)… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.12 (p.10)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读**

该图以归一化延迟（s/token）对请求率（req/s）作图，对比 FasterTransformer、Orca(Max/Pow2/Oracle) 与 vLLM 在 OPT-13B/66B/175B 三种规模、ShareGPT 与 Alpaca 两个数据集共 6 种配置下的吞吐上限。数据上 vLLM 在 ShareGPT 上 OPT-13B/66B/175B 分别可承载约 1.9/1.0/2.4 req/s，远超 Orca-Oracle（约 1.0/0.45/1.6），更远超 FasterTransformer；Alpaca 上 vLLM 同样领先（OPT-175B ≈21 vs Orca-Oracle≈16 req/s）。

原文借此论证：PagedAttention 通过分页式 KV cache 消除了碎片，使单序列生成场景下 vLLM 相比 Orca 基线吞吐显著提升（长序列 ShareGPT 增益更大）。

该图属于端到端服务实验的核心证据链，与 Figure 11 的批处理吞吐共同支撑"vLLM 在所有模型规模与负载下均最优"的方法结论。
*caption: Single sequence generation with OPT models on the ShareGPT and Alpaca dataset… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.13 (p.10)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig13.png]]
> [!tip] 【图文联合解读】图13展示OPT-13B在ShareGPT(2 reqs/s)与Alpaca(30 reqs/s)两种负载下的平均批处理请求数对比。ShareGPT子图：vLLM=30.42，Orca(Oracle/Pow2/Max)依次为13.62/9.81/7.00，vLLM约为Orca最优的2.2倍；Alpaca子图：vLLM=132.44，Orca依次为72.75/43.24/7.00，约为Oracle的1.8倍。该图论证PagedAttention通过消除KV cache碎片化与显存浪费，使系统可同时承载更多并发请求，有效批大小显著超越传统连续批处理方案。在论文实验链路中，它与吞吐量、延迟指标互补，直接量化vLLM"更高吞吐"的核心优势，为方法有效性提供关键实证。
*caption: Average number of batched requests when serv- ing OPT-13B for the ShareGPT (2 reqs/s) and Alpaca (30 reqs/s) traces.… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.14 (p.11)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图14展示OPT-13B在Alpaca数据集上四种负载（并行生成size=2/4、束搜索width=2/4）下，vLLM（蓝/绿线）与Orca-Max、Orca-Power（红叉/橙三角）的归一化延迟（s/token）随请求速率（req/s）变化曲线。图中显示vLLM蓝色曲线在请求速率达到约15-18 req/s时延迟才开始急剧上升，而Orca-Max仅在约2 req/s、Orca-Power在约8 req/s即饱和。

**关键结论：** 在并行采样与束搜索等需要共享前缀或管理多个序列的工作负载下，vLLM凭借PagedAttention的分页KV缓存管理，将吞吐量较Orca-Max提升约7-8倍，较Orca-Power提升约2倍。

**论文作用：** 该图扩展了Figure 13的实验维度，证明PagedAttention不仅在普通自回归生成中有效，在更复杂的解码策略（并行生成、束搜索）中同样显著降低内存碎片、提升服务吞吐，巩固了vLLM方法的核心技术优势。
*caption: Parallel generation and beam search with OPT-13B on the Alpaca dataset.… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.15 (p.11)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig15.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a)(b)分别量化OPT-13B服务Alpaca负载时，并行采样（输出序列数2/4/6）与束搜索（束宽2/4/6）下KV块共享带来的显存节省。并行采样节省由6.09%升至9.79%；束搜索节省则达37.56%→53.13%→55.16%，幅度与绝对值均显著更高。论文借此实证块共享对公共前缀密集的解码场景（尤以束搜索为甚）收益突出，支撑PagedAttention通过共享KV块提升显存利用率这一核心机制的有效性，是其系统级显存高效性实验论证链中的关键一环。
*caption: Average amount of memory saving from sharing KV blocks, when serving OPT-13B for the Alpaca trace.… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.16 (p.12)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图中两子图对比了翻译场景下共享前缀请求时，vLLM与Orca(Oracle)的归一化延迟(s/token)随请求速率(req/s)的变化。(a) 1-shot前缀（80 tokens）：Oracle约在30 req/s处急剧上升至~0.4，而vLLM在~48 req/s才升至~0.52；(b) 5-shot前缀（341 tokens）：Oracle仅在~10 req/s即爆发至~0.4，vLLM仍维持至~45 req/s后才升至~0.62。

**关键技术结论：** 前缀越长，Oracle基线因无法高效共享KV cache而越早饱和（30→10 req/s）；vLLM凭借PagedAttention的物理块共享机制，将饱和点保持在45–48 req/s，证明其在共享前缀场景下显著优于不可达的Oracle上限。

**论文链路作用：** 此图为端到端Serving性能验证，与Figure 13–15（吞吐、调度策略）形成完整实验链，并通过"前缀共享"压力测试，凸显vLLM内存管理在真实多请求并发场景中的核心优势。
*caption: Translation workload where the input prompts share a common prefix. The prefix includes (a) 1 example with 80 tokens or (b) 5 examples with 341 tokens… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.17 (p.12)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig17.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图17展示在聊天机器人负载下四种调度策略的归一化延迟（×token）随请求率（req/s，0–0.9）变化曲线。三种Orca变体（Max/Pow2/Oracle）在请求率达到约0.5–0.6 req/s时延迟即急剧飙升至1.0，而vLLM在约0.8 req/s仍保持低延迟（≈0.2），直至0.85 req/s才升至≈0.4。

原文借此论证：在细粒度、输入输出长度不固定的真实聊天负载下，vLLM（PagedAttention）相较Orca基线可将有效服务吞吐提升约**40–60%**。该图作为论文实验链路中端到端"真实负载验证"的关键一环，与合成长迹（Figure 15–16）共同支撑"分页式KV缓存在实际部署中显著优于连续分配"的核心结论。
*caption: Performance on chatbot workload.… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.18 (p.12)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
> [!tip] **Main Figure Description (Figure 18 — Ablation Experiments):**

The figure contains two subplots:

- **(a) Kernel latency (μs) vs. context length (64→256):** Compares four lines — vLLM (bs=8/32) and FasterTransformer (bs=8/32). vLLM shows 20–26% higher per-kernel latency than FT, but still wins end-to-end.
- **(b) Normalized latency (s/token) vs. block size (1→256):** Two traces (ShareGPT, Alpaca). Both form a U-shape; best region around block size 16–32. Alpaca degrades sharply beyond 32 because short sequences suffer fragmentation, while ShareGPT tolerates larger blocks.

**Data flow narrative:** tokens → PagedAttention block table → GPU KV-cache reads → attention kernel → output latency.

**Key takeaway:** PagedAttention adds ~20–26% kernel overhead over FasterTransformer, yet vLLM still outperforms it end-to-end, and a block size of 16 is the sweet spot — large enough to saturate GPU parallelism, small enough to keep internal fragmentation low.

**Caption (verbatim):** "Figure 18. Ablation experiments."
*caption: Ablation experiments. handle the long prompts, as PagedAttention resolves the problem of memory fragmentation and reservation. 7… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.19 (p.13)
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig19.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**(a) 微基准**：随 block size 从 1→256，Swap in、Swap out 及 Swap in+out 的耗时由 ~135/80/57 ms 急剧下降至 ~40/17/17 ms；而 Recompute 几乎与块大小无关，维持在 ~33–40 ms。二者约在 **block=16** 处发生交叉——块越大，swap 越划算。

**(b) 端到端（OPT-13B + ShareGPT）**：归一化延迟在 block=16–64 时达到最低（约 0.1 s/token）；过小（1–4）受 swap 开销主导，过大（256）则因块粒度粗、内部碎片与 KV 块复用率下降，两端均回升至 0.7–1.1 s/token。

**论文作用**：该图为 PagedAttention 选取 block size=16 提供了量化依据——必须足够大以让 swap 优于 recompute，又不能过大以避免浪费，并通过端到端实验闭环验证了这一权衡在真实负载下并非仅是微基准层面成立。
*caption: (a) Overhead of recomputation and swapping for different block sizes. (b) Performance when serving OPT-13B with the ShareGPT traces at the same reques… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.1 (p.1)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示用三色图例区分可共享KV缓存（蓝）、不可共享prompt（绿）、不可共享generation（黄），对比Sequence-based与四种Tree-based解码：(1)Self-consistency——单prompt分支为G₁/G₂；(2)Few-shot prompting——示例P₁/P₂及其生成可共享；(3)Tree-of-thoughts——通过Search History在分支间共享上下文；(4)推测解码——草稿模型产出token树t₀→t₁,t₂,t₃→t₄，验证后保留t₀/t₂/t₄并跨Step history复用。Sequence-based各序列完全独立、无共享；而Tree-based蕴含丰富可共享结构，但传统实现难以高效利用。结合Table 1（ToT生成38,315 vs CoT仅525 token的开销差异），作者论证Tree-based存在严重计算冗余，从而引出DeFT借助FlashAttention对树状结构做高效分块注意力与KV缓存复用的核心贡献。
*caption: Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., … ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.2 (p.5)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig02.png]]
> [!tip] 【图文联合解读】图示DEFT两阶段中的**Phase 1（QKV准备）**：HBM内Input Metadata含Query、共享前缀KV_0、分支KV_1/KV_2及Tree Topo，Q_a/Q_b各映射对应分支KV。经**KV-Guided Grouping**（跨分支复用KV_0）与**Flattened Tree KV Splitting**（按树拓扑切成均衡组G_i），IO感知装入各SM_i。

原文论证：消除共享前缀冗余KV读取 + SM负载均衡，为Phase 2共享内存（19TB/s）跑部分注意力 + 树感知全局归约供均衡输入。

在论文中：作为投机解码链路的**前端预处理核心**，直接决定HBM带宽（2TB/s）利用率与SM并行度，是"内存高效、硬件友好树结构注意力"方法的基础环节。
*caption: Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.3 (p.6)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig03.png]]
> [!tip] 【图文联合解读】图3展示QKV准备阶段分区策略对比：

**(a)** 两级级联解码树含查询Qa/Qb与节点KV0-KV2；Vanilla Tree Attention无分区并行度低；Q-Guided Grouping仅2组（Flash-Attention采用，G0:Qa+KV0+KV1, G1:Qb+KV0+KV2）；KV-Guided（本文）按KV对应查询分组提升并行度。

**(b)** Flash-Decoding/Radix对Q-Guided再做KV切分得G00-G11四组，但仍无KV IO感知；本文DeFT-Node按节点分3组（G0:Qa+Qb+KV0, G1:Qa+KV1, G2:Qb+KV2），DeFT-Node-Chunk再切节点KV得G00/G01/G1/G2四组。

**(c)** DeFT-Flatten通过深度优先展平→均匀块切→64位位因果掩码(KV-BCM，按KV块归属节点标记)，实现G0/G1/G2负载均衡。红色框标各组HBM-SharedMemory间IO量。

**论证**：逻辑分区不增QKV数据搬移成本，KV-Guided以IO感知实现高并行，奠基Attention阶段高效加载。

**论文作用**：作为DeFT核心图示，确立从Q导向到KV导向分区的演进路线，支撑Flash Tree Attention整体框架。
*caption: Comparison of QKV partitioning strategies during the QKV Preparation Phase between DEFT-… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.4 (p.9)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig04.png]]
> [!tip] 【图文联合解读】**图4解读**

图4展示在Medusa 32查询token树的推测解码场景下，6种注意力方法的延迟分解（Attention/KV Management/Other三类，纵轴秒）。关键量化数据：非分页的Tree-Attention-Medusa（U）总延迟最高约275s，其中KV管理占比高达53.46%；而DeFT系列（带分页机制）总延迟仅55–90s区间，以DeFT-Flatten最低。

**论证结论**：非分页方案的KV管理是主要延迟瓶颈，而分页KV管理能显著压低总延迟。

**论文作用**：该图是实验链路中验证DEFT核心设计——Flash Tree Attention + 分页KV——相对Tree-Attention-Medusa实现显著加速的关键证据，支撑"分页管理是树结构LLM推理高效性必要条件"这一论点。
*caption: Latency breakdown for specula- tive decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged m… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.5 (p.15)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig05.png]]
> [!tip] 【图文联合解读】**1) 核心对象与结构**
图示一棵解码树：根节点 S0=Prompt"Machine Learning"，分叉为 S1="System is difficult" 与 S2="has changed the"，当前迭代 iter=3。底部输入元数据含 Query、KV Cache (S0,S1,S2)、Tree Topo，经"extract and pack"送入 HBM→Shared Mem。上部按 KV 前缀划分为 3 个 QKV Group（Group 0/1/2），每组 Query（"difficult/the"、"the"、"the"）按共享 KV 配对执行 Attention。

**2) 关键技术结论**
论证 DeFT 的核心机制：Query 按 KV 前缀分组复用，使共享 KV 路径只需一次访存即可被多条查询路径共同使用，从而消除树形推理中的冗余计算与内存访问；并说明 DeFT-Node 与 DeFT-Flatten 仅 QKV 划分策略不同。

**3) 在论文中的作用**
作为系统总览与算法核心图，将"解码树→元数据→QKV 分组→Flash-Tree Attention Kernel"流水线具象化，为后续核函数设计与吞吐加速实验提供机制基础。
*caption: Illustration of DEFT. (Left) System overview. (Right) The data flow of DEFT-Node (DEFT-Flatten is similar except for QKV partitioning) using a decodin… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.6 (p.16)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p16.png]]
> [!tip] **Figure 6 Description (architecture/components/data flow + key takeaway)**

The figure illustrates tree-based decoding in two parts. **(a)** shows two query topologies paired with their KV caches: a *Sequence KV* (s₀) feeding a flat **Query Token Tree** of up to 64 tokens (t₁→t₂, t₃, t₄, t₅), versus a *Tree KV* (s₀ branching into s₁, s₂) paired with parallel queries (t₁, t₂), enabling shared-prefix reuse. **(b)** shows the **Bit Mask** mechanism: each query token tᵢ carries a 64-bit mask M[tᵢ] encoding causal connectivity (pᵢ bits: 1=no mask, 0=masked) between the token tree and tᵢ.

**Key takeaway:** Causal correctness in parallel tree decoding is preserved by a per-token 64-bit bit mask, which is far more storage-efficient than materializing full causal masks while still supporting speculative/multi-step reasoning workloads.

**Caption (verbatim):**
Figure 6: Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.
*caption: Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.7 (p.17)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig07.png]]
> [!tip] 【图文联合解读】**图7联合解读：**

图7对比两类树状解码的KV缓存复用。左为多步推理：提示P经两步TreeAttention生成G₁、G₂，再树搜索扩展为4叶节点(G₁.₁/G₁.₂/G₂.₁/G₂.₂)；右为投机解码：草稿模型产出5节点token树T_t(t₀→t₁/t₂,t₃→t₄)，验证后保留V_t={t₀,t₂,t₄}进入下一步G₃。蓝色框（共享历史KV）与黄色框（生成KV）的统一配色，论证DeFT的Flash Tree Attention KV缓存共享机制对**多步推理**与**投机解码**两类树状推理场景均通用，体现其作为统一加速方案的普适性，为论文核心实验对比提供方法论支撑。
*caption: Analysis for two case studies of tree-based decoding. (Left) Multi-step reasoning. (Right) Speculative decoding. Blue boxes mean shareable past KV cac… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.8 (p.19)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示 Medusa 树形注意力逐算子流程：左侧给出 KV0/KV1/KV2 三节点树拓扑及稠密因果掩码 DCM，Q/K 经 GEMM 分块（m×k、k×n）后写入 HBM；右侧 SM 通过多次 Load/Write 从 HBM 反复读取 S、S′、Ms、P 等中间结果，依次完成 S=QK⊤、S/Sc、S+DCM、Softmax、O=PV 全链路，每步都伴随一次全局内存往返。原文据此论证：未采用 Kernel Fusion 与 Tiling，导致 QK⊤、DCM、Softmax 等中间量产生显著冗余 IO。该图在论文中充当低效基线，反衬 DEFT 所提 Flash Tree Attention 融合分块策略的必要性。
*caption: Operations of Tree Attention-Medusa (Cai et al., 2024). No Kernel Fusion or Tiling strategy is applied, which introduces significant IO of partial res… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.9 (p.19)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig09.png]]
> [!tip] 【图文联合解读】**图9深度解读**

图示DEFT-Node两阶段kernel：3组QKV（G0=Q1·KV0、G1=Q1·KV1、G2=Q2·KV2）构成KV0→{KV1,KV2}的树拓扑（Tree Topo）。Stage1各组在SM上并行FlashAttn得PA_i与LSE_i写回HBM；Stage2从HBM加载PA₀:₂+LSE₀:₂至SM₃，依TreeTopo做DeFT_reduction归约为全局Attention。

**论证结论**：相比中间量（QK⊤、Softmax、P）频繁往返HBM的未融合kernel，该设计融合组内计算并以tree-aware LSE归约避免中间结果全局物化，显著降低IO并充分利用共享内存。

**论文作用**：作为DeFT树结构解码核心机制的可视化基础，衔接KV-Guided Grouping与FlashAttention分块思想，支撑高效树结构LLM推理的整体论证链。
*caption: Overview of two stages in DEFT Attention Kernel (DEFT-Node for example, and DEFT-Flatten is similar). Stage 1–calculate partial attentions. Based on t… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.10 (p.20)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 10b · Stage 2）：**

1) **核心对象与结构**：图示 Stage 1 输出的 4 组偏量——`Q1/KV0→(lse0,lse1,PA0,PA1)`、`Q1/KV1→(lse2,PA2)`、`Q1/KV2→(lse3,PA3)`、`Q2/KV0→偏量`。中部"Remap LSEᵢ and PAᵢ for each Query"将其按查询重组为 **Lse/PA Map for Q1**（lse0,lse2,PA0,PA2）和 **for Q2**（lse1,lse3,PA1,PA3），再由右侧 *Global reduction kernel* 用 LogSumExp 合并为最终 **Attention of Q1,Q2**。

2) **论证结论**：偏量可按 Query 归并复用，证明树形解码中"共享 KV"路径只需按 Q 分组做一次全局归约，即可数值稳定地得到与全量 FlashAttention 等价的结果，从而把多 QKV 组并行计算与单次 Reduce 衔接。

3) **方法链路作用**：补全 Figure 10(a) 两阶段内核的 Stage 2 实现细节，支撑"分 QKV 组并行 + 按 Query 归约"的核心架构，是论文证明 DEFT-Node/Flatten 在树状投机解码中正确且高效的关键图示。
*caption: Detailed attention operations of DEFT kernel (DEFT-Node for example, and DEFT-Flatten is similar). Based on the same decoding tree in Figure 3.… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.11 (p.21)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig11.png]]
> [!tip] 【图文联合解读】图11对比三种Tree Attention的QKV分块策略：左侧Medusa按GEMM将KV切为m×k与k×n的tile块，产生全量partial结果M；右侧SpecInfer采用Q-Guided Grouping，把查询分为G₀（Q_a）与G₁（Q_b）两组，分别共享同一组KV₀/₁/₂，并通过Q-BCM位掩码"110""101"标注各查询实际访问的KV子集。原文论证：当叶节点数ln足够大时，partial结果的IO开销可与KV cache相当，从而说明朴素的逐tile GEMM切分存在冗余访存问题，为论文提出的Q-BCM分块与Flash Tree Attention优化提供必要性依据，是方法链路中IO分析与分块策略设计的支撑图。
*caption: When the number of leaf nodes/queries ln is sufficiently large, the IO cost of partial results might become comparable to that of the KV cache. For in… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.12 (p.23)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图12展示两阶段构建解码树模板的流程。左绿框"Reconstruct thought trees"：Prompt节点按宽度w在d层深度上扩展为思维树，节点标为thought_i_j；✓标记保留节点，红色✗标记剪枝节点，虚线省略其余深度/宽度分支。右橙框"Tree templates for decoding"：每个保留节点封装5项元数据——start/end iteration（100/103）、thought size（3）、parent id（thought_i-1,k）、children id（None），并映射到具体文本"System is difficult"。据此生成两张结构化表：**Branch records**（迭代100，从(i-1,k)生成(i,j)）与**Prune records**（迭代103，剪掉(i,j)）。

**技术结论**：作者论证树模板可由真实推理轨迹离线重建，并通过5项元数据完整表征节点的生成时机、长度、父子关系，从而无遗漏地为解码阶段提供可调度的分支与剪枝信息。

**方法链路作用**：该模板是DeFT解码的离线预处理产物，为FlashTreeAttention提供"何时生成何分支、何时剪除何节点"的调度依据，是实现高效树结构推理的关键前置步骤。
*caption: The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.13 (p.25)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**核心对象与数据**：图示排序任务下，DEFT-Node 与 DEFT-Flatten 两种切分策略在迭代步 2000–3700 区间的对比。左轴 Speedup Ratio（蓝实线）前期稳定在 320–380 倍，后期（≈3000 后）剧烈震荡；右轴 Tree Node Len std（红虚线）在 220–300 之间周期性起伏。

2）**关键结论**：DEFT-Node 相对 DEFT-Flatten 获得高达约 350 倍的加速比，证明节点级切分显著优于展平切分，尤其在节点长度方差较小、树结构深度（d=10）× 宽度（w=10）规整的排序任务上，Node 策略能充分利用 Flash Tree Attention 的并行前缀，避免 Flatten 带来的冗余计算。

3）**在论文中的作用**：作为消融/对比实验，支撑 DEFT-Node 作为默认切分策略的设计选择，强化"树状推理的高效解码依赖于与树结构对齐的注意力切分"这一核心论点。
*caption: Comparison of split strategies DEFT-Node and DEFT-Flatten in sorting task. Speedup ratio refers to the ratio between the per iteration latency of DEFT… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.14 (p.26)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
> [!tip] **Architecture/Components/Data Flow:**
Figure 14 is a 2×2 grid of line plots showing per-iteration latency (Time, ms) over 400 decoding steps for few-shot prompting tasks. Each subplot varies the tree width (10, 20, 30, 50). Five curves are compared per subplot: DeFT-Flatten-e2e, Radix-e2e, DeFT-Flatten-Attn, Radix-Attn, and Medusa-Attn. The "e2e" curves measure end-to-end decoding latency, while "Attn" curves isolate attention overhead, allowing joint visualization of system-level vs. kernel-level performance as tree topology changes.

**Key Technical Takeaway:**
DeFT-Flatten's relative advantage over Radix Attention grows monotonically with tree width (1.24× at w=20, 1.33× at w=50) because wider trees increase KV-cache prefix reuse across parallel speculative-decoding branches, while attention overhead in competing schemes (e.g., Medusa) scales linearly with tree width via DCM growth.

**Caption (verbatim):**
"Figure 14: Per iteration latency for few-shot prompting tasks with different tree width. *e2e* means decoding latency(optimal end-to-end latency), while *Attn* means only the attention overhead."
*caption: Per iteration latency for few-shot prompting tasks with different tree width. e2e means decoding latency(optimal end-to-end latency), while Attn means… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.15 (p.26)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig15.png]]
> [!tip] 【图文联合解读】该图展示Prompt Length=1000时，不同token树规模（t=32/64/128/256）下单层Attention延迟随KV Chunk Size（128–1024）的变化曲线（实线为DeFT-Flatten，虚线为对照）。量化数据：t=32橙色线约90μs，t=256黄色线约270μs，延迟随t递增；多数曲线在chunk=256–512处取极小值，至1024时明显回升。原文据此论证chunk选择是Query IO冗余（越小越冗余）与SM线程块调度（越大越易空闲）的权衡；该ablation为DEFT系统确定最优KV chunk尺寸提供依据，支撑Flash Tree Attention整体推理效率的实验链路。
*caption: The chunk size selection is a trade-off between IO redundancy and threadblock scheduling: a larger chunk size means less redundancy of Query IO but ma… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.16 (p.27)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示在投机解码场景下（生成长度1000、token树大小=64），三种DEFT变体（DeFT-Node、DeFT-Node-Chunk，图中推测最高红线为DeFT-Flatten）的每输出token时间（TPOT）随prompt长度（2500–20000 tokens）变化的趋势。三条曲线均单调上升，但DeFT-Flatten增速最快（20000时TPOT最高），DeFT-Node居中，DeFT-Node-Chunk最低且增速最平缓，长prompt下优势显著拉开。原文借此论证：**chunk级KV切分策略（DeFT-Node-Chunk）在长上下文投机解码中延迟最低**，验证了Table 6关于切分粒度对注意力延迟影响的结论。该图作为方法验证的关键实验，支撑了论文整体方法链中"分块注意力优化"这一核心技术贡献，证明其在真实长prompt场景下具备实用加速价值。
*caption: Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.17 (p.27)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig17.png]]
> [!tip] 【图文联合解读】该图展示生成长度=1000、Token Tree Size=64时，4种注意力实现的解码延迟随Prompt长度（约2000→20000 tokens）的变化。短prompt下四条曲线几乎重合（差异≈0），但随prompt延长，粉色基线斜率最陡，DeFT-Node次之，DeFT-Node-Chunk与橄榄色chunk基线增长最缓，至20000 tokens时差距已拉开数倍。论文借此论证：在推测解码的长上下文场景中，节点级KV复用叠加chunk分块的双重优化使DeFT-Node-Chunk具备最优可扩展性，是其作为论文核心高效变体的关键实验支撑。
*caption: Decoding latency of DEFT with different prompt lengths in speculative decoding.… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.18 (p.28)
![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig18.png]]
> [!tip] 【图文联合解读】图18在生成长度1000、Token Tree Size=64的推测解码设定下，对比不同注意力实现随Prompt长度（0–20000 tokens）变化的延迟曲线：红色线（朴素树注意力）斜率最陡，长prompt下延迟最高；DeFT-Node（青蓝）次之；DeFT-Node-Chunk（紫）增长最缓且接近最优基线。

核心结论：随prompt增长，朴素树注意力开销急剧膨胀，而DeFT-Node-Chunk通过分块策略显著压缩长prompt下的注意力延迟，验证了chunk机制在大上下文推测解码中的可扩展性。

该图在论文实验链路中起"长上下文效率验证"作用，作为DEFT方法论在长prompt场景下优于朴素树注意力的关键定量证据，支撑整体Tree-Structured speculative decoding的高效性论证。
*caption: Attention latency of DEFT with different prompt lengths in speculative decoding.… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.1 (p.3)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig01.png]]
> [!tip] 【图文联合解读】图示Transformer按算子瓶颈三色分类：黄色compute-bound（W_Q/K/V/O、Up、Down、Gate 共7类权重共享算子，大batch摊销权重加载）；绿色memory-bound（prefill/decode attention，每请求独享KV cache，小batch避压）；蓝色network-bound（AllGather/AllReduce通信同步）。原文据此论证NanoFlow核心：异构batch+device-stream级算子融合，跨CUDA stream注入micro-batch将串行依赖转并行，实现1.91×吞吐、达理论峰68.5%。此图奠定全文方法论基石——先分类、再调度融合，后续流水设计与实验评估均依托此分类展开。
*caption: Transformer architecture. The operations in the yellow boxes have large batch sizes and share model weight parameters across requests; hence, they are… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.2 (p.5)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig02.png]]
> [!tip] 【图文联合解读】## 图文联合解读

**1. 核心对象与结构**
该热力图以 6 个 LLM（行：LLaMA-3 8B、Mistral 8x7B、LLaMA-2/3 70B、Qwen2 72B、LLaMA-3 405B）×13 种 GPU + Compute Bound 参考列（V100→Ada6000 PCIe）共 78 格，单元格数值为"网络通信时间/计算时间"比值（范围 0.119–2.609）。色编码：黄色(<1)表示计算受限，蓝色(>1)表示通信受限。

**2. 关键结论**
数据显示两条清晰趋势：①**模型越大越偏黄**（如 LLaMA-3 405B 在多数 GPU 上仅 0.119–0.812，呈深黄），说明大模型被 GEMM 主导；②**GPU 越快越偏蓝**（如 LLaMA-3 8B 在 H100/B100/B200/Gaudi 上达 1.008–1.529，Ada6000 上高达 2.609），意味着当算力足够强时，allreduce 等集合通信反成瓶颈。

**3. 在论文方法链中的作用**
该图为 NanoFlow 提出**nano-batch + 通信-计算重叠**提供动机：传统大 batch 在通信受限场景下吞吐不再随 batch 线性增长（因被 allreduce 阻塞），故需将大 batch 拆成 nano-batch 并流水化通信与计算，以榨干通信受限区间的吞吐。
*caption: Comparison of network time and compute time. The closer to yellow, the more compute-bound the workload is, whereas the closer to blue indicates the wo… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.3 (p.5)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig03.png]]
> [!tip] 【图文联合解读】热力图以5种LLM部署配置（行为LLaMA-3 8B×1、Mistral 8×7B×8、LLaMA-2/3 70B×8、Qwen2 72B×8）×6类负载（列为LMSYS-Chat/Splitwise/ShareGPT及512-512、1024-512、512-1024）为轴，单元值为计算时间与访存时间之比。绝大多数单元格呈黄色（计算受限，0.07–0.68），仅单卡LLaMA-3 8B在512-1024长输出负载下升至1.09、进入浅绿访存受限区；多GPU的大模型比值最低（0.07–0.32），纯计算受限。

图证：LLM推理在模型、部署与负载维度上瓶颈位置显著分散——同一时刻系统内同时存在计算、访存、网络三类受限算子。NanoFlow据此提出按算子类型（GEMM/GEMV/AllReduce）分别流水编排的调度方案，以同时缓解三类瓶颈、提升整体吞吐。
*caption: Comparison of compute time and memory time.… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.4 (p.8)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以时间轴展示现有LLM推理系统单层执行流水线，依次包含：KQV投影（黄/计算）、DecAttn（绿/访存）、PF Prefill（黄）、Attn.AG（蓝/网络）、O投影、O.AG、UGD大块计算（黄，主导项）、UGD.AR全归约（蓝）；首尾虚线框表示邻层KQV。

**关键结论：** 在KQV-DecAttn、PF-AG、AG-UGD、UGD-AR四段交界均出现"WASTED"空隙，因短小的访存/网络操作（DecAttn、AG/AR）与超长UGD计算（占主导）无法流水填充，导致计算核心在等访存/通信时空转，吞吐受限。

**论文作用：** 此图作为动机图，定量揭示"算力被访存/网络气泡浪费"的结构性瓶颈，直接引出NanoFlow将多层小操作聚合以消除WASTED、提升throughput的核心方案。
*caption: Execution pipeline of existing systems. The green, yellow, and blue operations correspond to memory-, compute-, and network-bound operations. Operatio… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.5 (p.8)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig05.png]]
> [!tip] 【图文联合解读】图5展示不同GEMM-GEMV实现配对下的归一化性能P：最优GEMM（蓝线）由左侧~1.0单调降至~0.45，最优GEMV（橙线）由近0升至~1.0，二者呈明显此消彼长；非最优GEMV（灰虚线）在0.1–0.9间剧烈波动。红色参考线标出P≈0.8与P≈0.3两个临界点。

论证两点关键结论：(1) GEMM与GEMV性能存在显著权衡，错配将使GEMV性能跌至非最优路径的~0.1；(2) 不同实现组合形成"数百万种配置"，穷举profile不可行。

作用上，此图作为NanoFlow的motivation，支撑其设计高效性能模型与搜索策略，在不遍历全空间的前提下为硬件选择最优GEMM-GEMV重叠组合，是LLM推理跨核重叠调度的基础实验依据。
*caption: Interference characteristics between GEMM and GEMV kernels. The points on the x-axis correspond unique GEMM-GEMV implementation pairs. The y-axis deno… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.6 (p.11)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig06.png]]
> [!tip] 【图文联合解读】图6展示NanoFlow为LLaMA-2 70B单层自动生成的执行流水线：沿"Layer"时间轴，将KQV计算、Prefill（PF1）、Q/O投影、Up·Gate·Down（UGD1/UGD2 R=0.9）、DecAttn1–4（R=0.4）及AG·AR（R=0.1–0.2）等算子分置计算/内存/网络三条轨道并行排布；实色与格纹背景分别对应batch 0–768与768–2048。原文借此论证NanoFlow通过Prefill Attention、AG→AR Transform等机制，使计算密集（UGD R=0.9）与访存/网络密集（KQV、AR R=0.1–0.4）算子互补重叠，提升整体资源利用率，从而提高服务吞吐。该图是把NanoFlow自动调度能力与端到端吞吐实验相连的核心可视化证据。
*caption: Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 76… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.7 (p.11)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读（≤220字）：**

该图以LLaMA-2-70B、8 GPU、TP=8为固定配置，在Splitwise、LMSYS-Chat、ShareGPT三组真实负载下对比每GPU吞吐量（tokens/s）。四个柱形（由低到高约251→1259、293→1247、335→1272）显示NanoFlow（橙色）达到1259/1247/1272 tokens/s，约为理论最优线1857（红色虚线）的67%，相对最优基线提升约1.5–2倍，并全面优于其余三种方法。该图是§6.4消融实验的收口，以端到端量化证据证明NanoFlow所提协同优化在所有真实负载上均稳定逼近最优，构成论文"近最优LLM服务"核心论点的关键支撑。
*caption: Offline throughput comparison. NanoFlow outper- forms all baselines for all the workload settings. TP stands for the number of GPUs used with tensor p… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.8 (p.13)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图含三面板延迟-请求率曲线（Splitwise/LMSYS-Chat-1M/ShareGPT），对比 vLLM、DeepSpeed-FastGen、TensorRT-LLM 与 NanoFlow 在 200 ms/token SLO 阈值（红色虚线）下随 req/s 变化的归一化延迟。各基线分别在 Splitwise 约 6.6–8.2、LMSYS ≈17.1、ShareGPT ≈10.5 req/s 处越过红线陡升，而 NanoFlow（红色）推迟至 15–32 req/s 才显著上升。原文借此论证 NanoFlow 在严苛 SLO 下能维持更高请求吞吐；该图作为方法有效性的端到端压测证据，与正文的 micro-benchmark 组件分析互为印证，构成"组件→系统→SLO 吞吐"完整实验链路的最后一环。
*caption: Latency comparison. The x-axis shows the number of incoming requests per second and the y-axis shows the normalized latency. NanoFlow handles higher r… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.9 (p.13)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig09.png]]
> [!tip] 【图文联合解读】图9为NanoFlow消融实验，纵轴为单GPU Token吞吐量(tokens/s)，横轴在四种I/O配置(512/0、512/512、1024/512、512/1024)下对比四种方案。量化数据：NanoFlow依次为1446/1323/1291/1277 tokens/s，全面优于Non-overlap基线(1273/1106/1092/1048)与Nanobatch-only(1171/982/958/952)；关键发现是Nanobatch-only反而低于Non-overlap，说明单独纳米批划分会引入额外开销。

技术结论：仅做nano-batching并不能提升性能，必须与overlapping结合才能发挥优势；offload版(1402/1290/1259/1244)略有下降但仍优于两基线。

论文作用：以消融证据支撑NanoFlow两大核心技术——nano-batching与overlap缺一不可，是验证方法有效性的关键依据。
*caption: Ablation study results for NanoFlow. Nano-batching and overlapping improves NanoFlow’s performance.… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.10 (p.13)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig10.png]]
> [!tip] 【图文联合解读】该图以Compute/Memory/Network三层堆叠时序（0–3000μs）对比单层推理资源占用。(a)非重叠基线串行：Compute在1300–2700μs维持~88%峰值，Memory在300–700μs达80%，Network仅短暂脉冲达58–75%，三类资源时间上近乎互斥。(b)NanoFlow三类资源交错并发，Compute呈多段阶梯（25%–88%），Memory与Network同步起伏，整体Compute利用率均值达68.5%。论文借此论证NanoFlow通过算子级细粒度融合实现跨资源并发是其相对非重叠流水线提升吞吐的关键机制证据，也提示内核干扰下仍存优化空间。
*caption: While the non-overlapping baseline sequentially executes operations, which mostly uses only one resource at a given time, the NanoFlow instance can co… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.11 (p.13)
![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig11.png]]
> [!tip] 【图文联合解读】**图示对象与数据**：柱状图对比 vLLM（蓝）与 NanoFlow（橙）在 5 个模型上的归一化单卡吞吐（%），红虚线标示 100% 最优基准，柱内数字为绝对 tokens/s/GPU。具体：Llama-3-70B 32.0%(593)→70.6%(1306)；Qwen2-72B 30.8%(554)→67.4%(1213)；Deepseek-67B 27.4%(532)→59.1%(1147)；Mixtral-8x7B 9.7%(997)→50.4%(5188)；Llama-3-8B 31.9%(5187)→78.5%(12756)。

**关键结论**：NanoFlow 在全部模型上均显著优于 vLLM，最高达最优吞吐的 78.5%（Llama-3-8B），相对 vLLM 提升约 2.2–5.2 倍。

**论文作用**：作为通用性验证，证明 NanoFlow 在 dense 与 MoE、不同参数规模模型上均稳定逼近最优，支撑"跨架构实现近最优服务吞吐"的核心主张。
*caption: We find that… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### Gated Delta Networks: Improving Mamba2 with Delta Rule — Fig.1 (p.7)
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读**

1) 图分三块：左为Gated DeltaNet-H1架构（N×重复，每块含Gated DeltaNet+MLP→SWA+MLP共2子层）；中为H2混合架构（Mamba2+MLP→Gated DeltaNet+MLP→SWA+MLP共3子层）；右为Block设计，展示四条并行路径——q/k（Linear+Conv+SiLU+L2 norm）、v（Linear+Conv+SiLU）、α/β（Linear+SiLU）汇入Gated Delta Rule→Norm→Linear输出。

2) 论证结论：delta-rule线性注意力配合乘性门控α、β可显著增强联想召回；H1/H2通过交错DeltaNet、Mamba2(SSM)、SWA，实现选择性长程记忆+结构化递归+局部上下文三者的优势融合。

3) 在论文中地位：作为架构总图定义模型骨架，为后续WikiText ppl 16.42、zero-shot ppl 55.32及H2最优ppl 15.91等核心实验结果提供结构支撑。
*caption: Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.… ｜ 论文 [[gated-delta-networks-improving-mamba2-with-delta-rule]] ｜ arxiv 见 MD 元信息*

### Gated Delta Networks: Improving Mamba2 with Delta Rule — Fig.2 (p.8)
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig02.png]]
> [!tip] 【图文联合解读】**图2图文联合解读**

该图以3×2网格展示6个长文本基准(GovReport、Qasper等)上、序列长度从4k扩展至20k时的性能曲线，纵轴为各任务指标。图例含四条线：Mamba1(橙)、DeltaNet(蓝)、GatedDeltaNet及另一变体(绿/棕)。

**关键观察**：在所有基准上，**Mamba1退化最严重**——如GovReport从~9.1降至~6.0，Qasper从~20降至~13；**DeltaNet(蓝)居中**，16k后也明显下滑；而**GatedDeltaNet系列(绿/棕)**曲线始终位于最下方簇，在20k处仍保持稳定。

**论证作用**：该实验用以证明——**门控(gating)与Delta规则的组合显著改善了Mamba2/DeltaNet基线的长度外推能力**，是验证"Gated DeltaNet"核心设计(在Delta规则上引入遗忘门)有效性的关键证据，呼应论文标题"improving Mamba2 with delta rule"的主旨。
*caption: Length extrapolation on six long benchmarks.… ｜ 论文 [[gated-delta-networks-improving-mamba2-with-delta-rule]] ｜ arxiv 见 MD 元信息*

### Gated Delta Networks: Improving Mamba2 with Delta Rule — Fig.3 (p.9)
![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig03.png]]
> [!tip] 【图文联合解读】图3为折线图，横轴为序列长度×批大小组合（2K×16→16K×2），纵轴为训练吞吐（K tokens/s，~25–60）。展示8个1.3B模型在单卡H100上的表现：Transformer++（蓝线）随序列增长由~55急降至~27 K/s；而DeltaNet、Mamba1/2、Gated DeltaNet、Samba等线性注意力/Gated RNN基线保持平稳（~38–50 K/s）。

原文借此论证两点：(1) 独立混合器中Samba优于Mamba；(2) 所提Gated DeltaNet-H1与-H2吞吐超越Samba，证明Delta Rule+门控机制兼具高质量与高效率。

该图作用：与下游语言建模/下游任务质量指标形成互补，从算力成本维度佐证所提架构"质量–效率"双重优势，闭环论证其工程实用性。
*caption: Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outper… ｜ 论文 [[gated-delta-networks-improving-mamba2-with-delta-rule]] ｜ arxiv 见 MD 元信息*

### Parallel Scan on Ascend AI Accelerators — Fig.3 (p.3)
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig03.png]]
> [!tip] 【图文联合解读】**1) 图示对象与结构**：展示Ascend 910B单AI Core架构：含1个AI Cube Unit（Cube核心+L0A/L0B/L0C、BT/FP、L1 Buffer+FixPipe+Scalar）与2个AI Vector Unit（各含Vector核+Vector Scratchpad+Scalar），三者均经左侧Global Memory互联。

**2) 关键技术结论**：Cube与Vector各持独立scratchpad，跨单元无本地直连通路，仅能经全局内存/L2交换数据；非对称划分迫使parallel scan采用block-tiled、解耦look-back的通信最小化设计，而非GEMM中心方案。

**3) 论文方法链作用**：为解耦scan方法提供硬件依据——AIV跑element-wise/局部scan，AIC做跨块前缀累积，MTE编排块级tile传输，从而在Ascend上高效实现线性注意力/SSM scan。
*caption: 1 shows the Ascend architecture where the… ｜ 论文 [[parallel-scan-on-ascend-ai-accelerators]] ｜ arxiv 见 MD 元信息*

### Parallel Scan on Ascend AI Accelerators — Fig.4 (p.4)
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig04.png]]
> [!tip] 【图文联合解读】**图4核心内容：**

图示 ScanU 单 tile（x_l → y_l）的片上数据通路。左下为 Global Memory，含输入张量 x（含 tile x_l）、上方的 U_s（通常为上一轮的累加结果），以及输出 y（含 y_l）。右上 Cube unit：从 GM 读 x_l 至 L0A（矩阵缓冲），与 L0B 中 1/0 选择矩阵（实现下三角扫描矩阵）做矩阵乘，结果落入 L1C；随后 L1C 数据经 DMA 进入右下 Vector unit 的 UB，并在 UB 内通过一串 "+" 链式累加（向量级 prefix-sum），最终写回 y_l。

**论证结论：** ScanU 把"扫描"拆解为 Cube 端的大规模矩阵乘（构造 partial sum）+ Vector 端的链式累加（完成 prefix-sum），即"超立方算子 + 向量归约"混合实现，避开显式多步同步扫描。

**在论文中的作用：** 作为 Algorithm 4.1 的微观数据流证据，支撑其"用 Cube unit 完成并行扫描主体、用 Vector unit 完成剩余归约"的核心设计；与性能模型及实验部分呼应，论证该混合策略在 Ascend 上的吞吐与访存优势。
*caption: 1: Data path from an input tile xℓto an output tile yℓof the ScanU (Algorithm 4.1).… ｜ 论文 [[parallel-scan-on-ascend-ai-accelerators]] ｜ arxiv 见 MD 元信息*

### Parallel Scan on Ascend AI Accelerators — Fig.5 (p.7)
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以有向依赖图形式，自顶向下展示了"Parallel Scan"作为根节点，向下派生出 **Weighted Sampling** 与 **Split** 两条主线；Split 又分出 **Radixsort** 与 **Compress**；Radixsort 进一步支撑 **Top-K Sampling**，Weighted Sampling 衍生 **Top-P Sampling**（含虚线连接）。各应用间以实/虚箭头标注直接调用与衍生依赖。

原文借此论证关键结论：**多种主流算法（采样、基数排序、压缩、Top-K/Top-P）均可被归约为 parallel scan 原语**，因此在 Ascend 加速器上高效实现 parallel scan 即能同时加速整条应用链路。

在论文整体定位上，该图属于**动机图（motivating figure）**，位于方法章节前部，为后续面向 Ascend 的并行扫描算子设计与性能实验提供应用场景清单，论证研究工作的覆盖面与实用价值。
*caption: 1: A diagram of well-known parallel scan applica- tions considered here along with their dependencies.… ｜ 论文 [[parallel-scan-on-ascend-ai-accelerators]] ｜ arxiv 见 MD 元信息*

### Parallel Scan on Ascend AI Accelerators — Fig.6 (p.8)
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig06.png]]
> [!tip] 【图文联合解读】图示910B4上fp16 MCSCAN带宽随输入长度(0~1×10⁸)的变化：memcpy峰值~560 GB/s，s=128/64/32分别饱和约300/200/100 GB/s，PyTorch cumsum近0。段长越大带宽越高，s=128达memcpy约53%，验证其相对ScanU 15.2×加速。作为Algorithm 4.3的实测支撑，定量呈现段长对硬件利用率的影响，佐证分段扫描方案在910B4上的高效性。
*caption: 1:… ｜ 论文 [[parallel-scan-on-ascend-ai-accelerators]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.1 (p.1)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig01.png]]
> [!tip] 【图文联合解读】图1为多面板水平柱状对比图，Kimi K3以蓝色高亮、Fable 5/Opus 4.8/GPT-5、5.6 Sol/GLM-5.2为基线，覆盖12项Coding与通用/视觉Agent基准。在可见面板中，Kimi K3于FrontierSWE(81.2)、SWE-Marathon(42.0)、AutomationBench(30.8)三项夺魁，对GLM-5.2最大领先近17分；仅ZeroBench w/tool(41.0)略逊于Fable 5(46.0)。该图置于首页，作为全文方法-实验链路的开篇主结果，集中论证Kimi K3在编码与Agent推理上达到开源前沿水平，为后续章节提供核心实证锚点。
*caption: Kimi K3 main results. 1https://huggingface.co/moonshotai/Kimi-K3[cs.CL] 7 Aug 2026… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.2 (p.3)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig02.png]]
> [!tip] 【图文联合解读】图示Kimi K3整体架构：输入经MoonViT-V2+MLP视觉通路→Embedding→堆叠Block，每Block由"3层KDA+1层Gated MLA"组成，每注意力层配Stable LatentMoE FFN，α/w门控贯穿残差。左上图展开LatentMoE：2个Shared Expert与N个Routed Expert由Router聚合；左下图展开KDA：q/k经Conv（q附L2归一化）、v直入，α/β由Linear生成，以Norm与⊗门控融合输出。该图论证"token/channel/layer三维度混合"的核心设计，是Table 2性能对比所依赖的结构基线蓝图。
*caption: The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.3 (p.5)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig03.png]]
> [!tip] 【图文联合解读】**图(b)核心对象**：两个4×4分块矩阵对比KDA分块计算。Kimi Linear：主对角线4个橙色"Position-pair Diagonal"块需显式位置对计算，下三角6格用蓝色Tensor Core；Kimi K3：经log-decay下界化后，全部10个因果块（主对角+下三角）统一为蓝色Tensor Core稠密矩阵乘，白色上三角保留因果掩码。

**论证的技术结论**：log-decay下界化（sigmoid钳至g_min=-5）使对角块不再需要特殊计算路径，所有因果块均可纳入Tensor Core加速，硬件利用率显著提升，复杂度从"对角线特殊+其余稠密"简化为"统一稠密GEMM"。

**论文整体作用**：这是K3相对Kimi Linear的核心工程优化之一，支撑其在大规模长序列训练/推理中的硬件效率，是"前沿智能"得以在KDA架构上落地实现的关键链路。
*caption: Lower-bounded decay and its effect on chunkwise KDA computation. (a) Kimi Linear uses an unbounded negative-Softplus mapping, whereas Kimi K3 bounds t… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.4 (p.7)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig04.png]]
> [!tip] 【图文联合解读】**核心对象**：左表给出 GLU、SwiGLU、SiTU-GLU 三者的 Gate/Up 分支公式（σ、x·σ(x)、β₁tanh(x/β₁)·σ(x) 等）；右图绘制其在 x∈[−10, 100] 上的标量响应曲线，插图放大原点附近。

**关键结论**：SiTU-GLU（红，β₁=4, β₂=25）在原点处紧贴 SwiGLU（绿），保留其类 SwiGLU 的训练动力学；但大 x 时收敛于 |f(x)|≤β₁β₂=100 的有界渐近线，而 SwiGLU 与 GLU 均无界增长。

**论文作用**：以可视化直观论证 SiTU-GLU 同时具备"近原点近似 SwiGLU"与"输出有界"两性质，为后续训练稳定性与消融实验提供几何直觉与设计依据。
*caption: Gate and up branches of GLU, SwiGLU, and SiTU-GLU, together with their scalar responses, where σ denotes the sigmoid function. Both branches receive t… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.5 (p.8)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图展示Quantile Balancing路由机制的核心步骤：m=8 token、n=4 routed experts、k=1选一。(a) 标准Top-k产生负载(4,3,1,0)严重倾斜；(b) 图中灰色横杠为各margin $s_{i,j}+b_j-\alpha_i$，红色虚线为新偏置阈值$\widehat{b}_j^{(t+1)}$，置于第(q+1)大margin处，使每列恰q=2个margin越过；(c) 经此重新路由后，t1–t8被均匀分给E1–E4，每专家恰收2 token。

**论证结论：** Quantile Balancing通过对每专家偏置的"分位数截断"，将不均衡Top-k路由强制转化为均匀分配，从根本上抑制过热/饿死专家。

**论文作用：** 作为Kimi K3稀疏MoE路由层关键算法可视化证据，支撑其大规模专家并行训练中负载均衡与训练稳定性的方法论主张。
*caption: Illustration of Quantile Balancing with m = 8 tokens, n = 4 routed experts, and k = 1 selected expert per token. (a)… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.6 (p.9)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图呈现预训练消融阶段视觉塔梯度范数随训练步（7k–22k+）的完整轨迹，对比MoonViT-3D（蓝，SigLIP初始化）与MoonViT-V2（红，从零训练）。MoonViT-3D多次出现0.5–0.75的高尖峰，尤其集中在14k–15k步处；而MoonViT-V2梯度主体低于0.2，尖峰稀少且小，仅在22k附近出现约0.4的脉冲。

此图论证的核心结论：**从零训练的MoonViT-V2优化更稳定、梯度更可控**，显著优于基于SigLIP初始化的MoonViT-3D方案。

在论文整体方法链路中，它为"弃用外部预训练初始化、改用从零训练视觉编码器"的架构决策提供了直接的训练稳定性实证，是MoonViT-V2最终取代MoonViT-3D成为默认视觉塔的关键支撑证据之一。
*caption: Vision-tower gradient norms in our pre-training ablations. Compared with the SigLIP-initialized MoonViT-3D, the from-scratch MoonViT-V2 maintains lowe… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.7 (p.11)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示为对数–对数坐标系下的两条拟合 scaling-law 曲线（虚线），横轴为训练 FLOPs（10²¹ 刻度可见），纵轴为评估损失。蓝色虚线为 Kimi K2，红色虚线为 Kimi K3，每条曲线上标有星号表示实测数据点。两曲线整体平行下移，K3 在相同 FLOPs 下损失更低，或达到相同损失所需计算量约为 K2 的 1/2.5。

2) **关键结论**：以 2.5× 的横向位移定量证明 K3 在 scaling efficiency 上相较 K2 取得显著增益，即每单位算力可获得更优模型质量，验证了 K3 架构/训练方案的有效性。

3) **论文作用**：该图位于实验论证环节，作为支撑 K3 跨入 "open frontier intelligence" 主张的核心定量证据之一，将抽象的"更强"转化为可测量的计算效率提升，为 K3 资源分配决策与代际跃迁论断提供经验依据。
*caption: Fitted scaling-law curves for Kimi K2 and Kimi K3. Kimi K3 achieves 2.5× gain in scaling efficiency over Kimi K2.… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.8 (p.13)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读（图8）：**

图8为2×2四宫格双轴折线图，覆盖Web Development、Agentic Search、Agentic Chart Understanding、Agentic Visual Puzzles四项评测。横轴为RL FLOPs，蓝实线（左轴）为得分(%)，红虚线（右轴）为平均助手步数。量化趋势：Web Development得分由~10%升至~80%、步数~5→10；Agentic Chart Understanding得分~30%→70%、步数~3→6；Agentic Visual Puzzles得分~40%→80%；Agentic Search得分~10%→60%；四任务步数整体均随FLOPs同步增长。

原文据此论证**"RL FLOPs扩展→工具调用步长与综合能力协同提升"**这一核心scaling结论。该图与Figure 7互补，构成论文"算力驱动Agentic能力与推理深度共增长"主线论断的关键实证，支撑Kimi K3以RL为后训练主要杠杆的方法学定位。
*caption: Scores and the average assistant steps across a variety of public and in-house evaluations during RL. By scaling RL FLOPs, tool-call steps scale up co… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.9 (p.15)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

左侧分层知识图谱：1中心节点辐射7+领域（CS/AI、Coding、Math、Physics、Chemistry、Biomedicine、Humanities等），各领域再分叉约30+细粒度概念节点，呈多层辐射状。右侧三阶段流水线：①联合采样相关节点形成关键词集（如RoPE、GPU kernel）；②据此从互联网抓取公开素材（论文/博客/代码库）；③按实例选择任务类型（Coding/Knowledge/Vision等）合成任务。

原文论证：知识图谱的层级语义结构保证任务在广域学科覆盖与细粒度概念两个尺度上兼具多样性与可控性；关键词→素材→任务链路将开放网络数据自动转化为结构化训练任务，实现规模化数据合成。

论文作用：作为任务合成框架总览图，揭示训练数据如何由知识先验+公开语料自动生成，奠定大规模、多样化、可扩展训练集构建的方法基础。
*caption: Overview of knowledge-graph-guided task synthesis. The hierarchically organized knowledge graph represents concepts at multiple levels, ranging from b… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.10 (p.17)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig10.png]]
> [!tip] 【图文联合解读】1) 图中4条阶梯曲线比较黑盒“相机维修管理系统”的复现进度：工具调用从50%推进至100%，完成度由验证器评估；终值约为红/橙90、紫82、蓝81、绿52。  
2) 曲线表明，代理借助 oracle 查询可逐层还原隐藏的3D维修系统及Web应用，但过程是阶段性的，代理能力决定完成效率与上限。  
3) 该实验构成“黑盒探测—工具执行—系统复现—验证评测”链路，证明方法可处理开放式长程应用复制。
*caption: Completion curves on Camera Repair Management System, a black-box system replication task in which the agent reconstructs a hidden 3D-camera repair sy… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.11 (p.19)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig11.png]]
> [!tip] 【图文联合解读】图11为PP0/PP1/PP2三阶段时间轴甘特图，含6个微批次（蓝前向/红反向），5条轨道并行跑DataLoader+ViT计算、EP gather param、NCCL与激活Onload/Offload。放大框拆解单阶段：Attn–SE1–MLP–SE2（穿插EP-C/EP-D）–WGrad，前后夹Offload块。

结论：MoE专家通信、跨卡NCCL与激活换页被精确流水线化，并与PP前反向深度重叠，从而掩盖Expert All-to-All与reduce-scatter开销。

作用：作为Kimi K3训练栈（ZeRO-Offload+EP重叠调度）的关键证据，支撑其超大规模MoE高效训练，使计算/通信/换页同步推进而不形成气泡。
*caption: Computation, communication and offloading overlapped in different PP phases.… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.12 (p.23)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**① 核心对象与结构：** 1个6144-token物理块被切分为12个512-token的prefix-hash子块，其中前5块为蓝色（已缓存的MLA块，对应B=2560/512=5），后7块为浅灰色（空块）；下方12个标记对应每个hash边界的KDA checkpoint状态（○=无checkpoint，●=已持久化，橙色●=在B=2560处命中）。

**② 关键结论：** KDA checkpoint稀疏分布且通常与对话轮次边界对齐；新请求到达B=2560时，以copy-on-write方式复用前5个MLA hash块与该处KDA checkpoint，对区间[0, B)实现零重算（zero-recompute）即可直接续写prefill。

**③ 在论文中的作用：** 展示"细粒度prefix caching + 状态checkpoint"的协同机制，是Kimi K3长上下文推理高效prefill恢复与KV复用方案的核心可视化证据。
*caption: Fine-grained prefix caching within a physical cache block. A 6144-token physical block contains twelve 512-token hash blocks, with cached MLA blocks s… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.13 (p.32)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig13.png]]
> [!tip] 【图文联合解读】**图13联合解读**

图13含四个子图，对比Kimi K3（★）与GPT-5.6 Sol、Claude Fable 5/Opus 4.8/Sonnet 5/Mythos 5在代码、检索、智能体任务上得分/ELO与单任务成本关系。关键数据：(a) K3约$4达72.5%，成本不到Fable 5（$10.5/77.5%）一半；(b) K3(max)仅~$1即达~91.5%，以约1/27成本超越Opus 4.8 10M token(~88%)；(c)(d) K3 ELO略低于Fable 5（1680/1550 vs 1748/1580），但成本仅其1/3~1/2。该图作为"显著更低成本达前沿智能"主张的核心实证，支撑K3在性能–成本帕累托前沿上优于闭源同级的结论。
*caption: Score vs. per-task inference cost on Kimi Code Bench 2.0, BrowseComp, GDPval-AA v2, and AA-Briefcase. Kimi K3 is marked with a star.… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.14 (p.33)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**：该图为AttnRes算子GPU kernel优化的纵向case study，横轴为优化耗时（小时，约15–20h区间），纵轴为相对加速比。四条阶梯状轨迹分别对应四个模型的迭代优化过程，×号标记为单次尝试散点，水平虚线表示各自达到的最高性能平台：Kimi K3（红）**+59.7%**、Claude Fable 5（蓝）**+57.1%**、GPT-5.5（绿）**+30.8%**、GPT-5.6 Sol（深红）**+17.3%**。

**2) 关键技术结论**：Kimi K3在约17h即触及性能天花板，最终加速比领先第二名约2.6个百分点、领先GPT系列25–42个百分点；其轨迹爬升更快、平台更早稳定，说明该模型在编译反馈—profiling—改写循环中具备更高效的多轮迭代搜索与"通过"判定能力，而GPT-5.6 Sol虽耗时相近却仅获+17.3%，凸显Kimi K3在底层算子优化任务上显著优于同期前沿闭源模型。

**3) 在论文链路中的作用**：作为Figure 14 case study，它与上游基准评测互补，从"过程性"维度具象化K3的智能边界——不再仅给出最终分数，而是展示模型在长时程、需工具反馈的复杂系统工程任务中的探索效率与上限突破能力，支撑"开放前沿智能"（open frontier intelligence）这一核心论断。
*caption: Case study: GPU kernel optimization on AttnRes. 7… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.15 (p.34)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig15.png]]
> [!tip] 【图文联合解读】图15为MiniTriton自研GPU编译器的四项实证：(a)L20 fp32 CUDA-core roofline中matmul 4096³达2048³量级GFLOP/s，逼近cuBLAS 8192³实测峰38.1 TFLOP/s；(b)tf32/bf16张量核roofline，minitriton(红)与cuBLAS曲线几近重合，bf16峰值115.8 TFLOP/s；(c)字符级GPT 100步训练损失曲线与torch eager完全重合；(d)单卡vs DDP×2(L20 NCCL)120步交叉熵差max仅0.0033，final 2.4876/2.4870。论证结论：编译器在多算子多精度下达工业级roofline上限，且端到端收敛与分布式扩展均数值正确。该case study在论文中作为系统层证据，证明前沿智能体具备完整GPU编译器研发能力，而非仅应用层代码生成。
*caption: Case study: GPU compiler development with MiniTriton. (a) CUDA-core and (b) tensor-core rooflines of MiniTriton kernels on an NVIDIA L20 (sm_89) again… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.16 (p.46)
![[assets/crops/kimi-k3-open-frontier-intelligence-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 16，Kimi K3 Chat Template）：**

1) **结构对象**：图分三栏。(a) 上下文布局按"全局选项（tool-declare、thinking-effort）→ 输入消息（system/user/tool/assistant，mid-session 虚线注入 dynamic tool-declare）→ 单次选项（tool-choice、response-format）"三段式排列，前缀为 `[open]think[sep]` / `[open]response[sep]`；(b) assistant 消息体含 think、response、tools 三条独立通道，以 `[end_of_msg]` 收尾；(c) tools 通道按 `call tool="python|search" index=N` 形式承载参数化调用（如 `{"timeout":150}`）。

2) **关键论证**：全局选项前置 + 单次选项后置，保证 per-request 配置不破坏历史 KV cache；mid-session 工具以 input option 形式动态注入；三通道解耦使 thinking、回复、工具调用可独立采样与缓存复用。

3) **论文作用**：该模板是 K3 推理时 thinking-effort、tool-use 与 KV cache 高效复用的结构基础，支撑后续长上下文与 agent 评测链路。
*caption: Structure of the Kimi K3 chat template. (a) Context layout: global option messages precede the input messages, while one-shot option messages follow t… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Prefill-as-a-Service: KVCache of Next-Generation Models Coul — Fig.1 (p.2)
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig01.png]]
> [!tip] 【图文联合解读】**图1解读**

图1对比PD分离LLM两种部署范式：左侧PrfaaS（Prefill-as-a-Service）专用集群配本地KV Store与Prefill节点，右侧本地PD集群含Standard/Decode节点及本地KV Store，二者经中间"跨数据中心KVCache传输层"（松耦合KV Transfer）连接，层内对比"Dense—Network Bound"（✗，因带宽受限被否）与"Hybrid—Prefill Bound"（✓，以Prefill为瓶颈而被选）两条路径，并由底部"基于以太网的跨集群KV Store"统一封装。

**论证结论**：Hybrid松耦合方案可克服跨数据中心带宽瓶颈，使KVCache可在集群间高效流转，从而实现PrfaaS多集群分离推理。

**全文作用**：作为方法论总图，引出后续对Hybrid传输、KV布局与跨集群调度的具体设计与实验。
*caption: Comparison of two deployment paradigms for PD-disaggregated LLM serving.… ｜ 论文 [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] ｜ arxiv 见 MD 元信息*

### Prefill-as-a-Service: KVCache of Next-Generation Models Coul — Fig.2 (p.4)
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1）核心数据：** 图以 MiniMax-M2.5 在 8×H200 实例上的实测呈现双轴关系——蓝柱为 KV 吞吐量(Gbps)、红线为 Prefill 延迟(s)，横轴为 prompt 长度(1K–128K)。吞吐量从 1K 的 ~5 Gbps 单调升至 64K 峰值 ~61 Gbps，128K 回落至 ~48 Gbps；延迟在 ≤32K 区间保持 <1.2 s，64K 升至 ~2.2 s，128K 陡增至 ~5.5 s。

**2）关键结论：** 长上下文 prefill 产生高达数十 Gbps 级别的 KV 流量，且在 128K 出现明显 **compute-bound 拐点**——吞吐量不升反降、延迟指数级攀升，证明长 prompt 的 prefill 是高算力开销单元，将其剥离至专用实例具备现实必要性。

**3）论文作用：** 为 "prefill-as-a-service / KV cache 跨数据中心传输" 的核心动机提供单实例 KV 带宽量化证据，论证解耦 prefill 与 decode 的工程价值。
*caption: KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.… ｜ 论文 [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] ｜ arxiv 见 MD 元信息*

### Prefill-as-a-Service: KVCache of Next-Generation Models Coul — Fig.3 (p.6)
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig03.png]]
> [!tip] 【图文联合解读】该图展示PrfaaS-PD部署拓扑：核心为Local PD Cluster（含Prefill与Decode两类节点，由Intra-Cluster RDMA Network高带宽互联，配套Hybrid Prefix Cache Pool），短请求(l≤t)本地直接处理；Global KVCache Manager经Inter-Cluster Ethernet跨集群统一调度。原文借此论证：PrfaaS-PD通过Prefill/Decode分离、RDMA+Ethernet分层网络与混合前缀缓存池，可支撑跨数据中心的KVCache传输。该图为后文跨机房KV吞吐实验（表3，8×H200，SGLang v0.5.9）提供系统部署前提与方法框架。
*caption: Deployment topology of the PrfaaS-PD architecture.… ｜ 论文 [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] ｜ arxiv 见 MD 元信息*

### Prefill-as-a-Service: KVCache of Next-Generation Models Coul — Fig.4 (p.7)
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig04.png]]
> [!tip] 【图文联合解读】图4展示统一Hybrid Cache Pool：第3组Full Attention含8个块级KVCache单元；池中可见12块，其中5个粉色跨集群Transfer-Cache块、7个灰色空闲块。论文说明，线性状态与全注意力KVCache虽分组建管，却共享分块资源；前缀缓存仅集群内且按块对齐，传输缓存可跨集群任意长度并在使用后释放。该结构连接各PD集群的prefill/decode链路，为跨数据中心KV传输、资源隔离及统一池调度提供架构基础，并非结果指标图。
*caption: Hybrid prefix cache pool. Linear states and full-attention KVCache are managed by separate groups backed by a unified block pool. Blocks are categoriz… ｜ 论文 [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] ｜ arxiv 见 MD 元信息*

### Prefill-as-a-Service: KVCache of Next-Generation Models Coul — Fig.5 (p.11)
![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig05.png]]
> [!tip] 【图文联合解读】**图(a)** 展示本地 PD 集群内 prefill/decode 实例分配（固定 Np+Nd=8）的吞吐量网格扫描：下 x 轴 Np∈[1,7]、上 x 轴 Nd∈[7,1]，纵轴 Λ_max(req/s)。红线 Prefill bound 在 Np=1→3 单调上升至 3.24，绿线 Decode bound 在 Np=4→7 单调下降至 ~0.8，二者在最优点 ★Np=3、Nd=5 交汇。附表量化 1K/8K/32K/128K 序列对应 KVCache 为 190.8/308.9/701.3/2316.3 MiB。

**关键结论**：总实例数受限时，prefill 与 decode 实例存在唯一最优配比——prefill 过多受 prefill 吞吐上界制约，decode 过多受 decode 上界制约，形成"V 形"包络。

**论文作用**：与图(b)固定 Np=3、Nd=5 扫描传输时间 t 配合，构成两变量优化的两阶段网格搜索，为跨数据中心 KVCache 共享方案的实例/带宽联合部署决策提供量化依据。
*caption: Illustration of the grid search process for the two optimization variables. (a) fixes t at the optimum and searches over the prefill/decode instance s… ｜ 论文 [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] ｜ arxiv 见 MD 元信息*

### LongSpec: Long-Context Lossless Speculative Decoding with Ef — Fig.1 (p.1)
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig01.png]]
> [!tip] 【图文联合解读】**1) 核心对象与数据**
对数刻度柱状图（y 轴 2k→10M），对比 7 个前沿 LLM 的上下文窗口：DeepSeek-V3、Qwen3-235B-A22B 约 128k；Claude 3.7 Sonnet 约 200k；Grok 3、GPT-4.1、Gemini 2.5 Pro 约 1M；Llama 4 Scout 约 10M（最高）。红色虚线标 2k，为 EAGLE 训练上下文长度。

**2) 关键结论**
现代 LLM 实际上下文窗口为 EAGLE 训练长度的 **64×~5000×**，EAGLE 根本无法覆盖真实长上下文场景，直接迁移将失效。

**3) 论文作用**
作为核心动机图，揭示 SOTA 推测解码方法在长上下文下的根本局限，为 LongSpec（长上下文无损推测解码）的研究必要性提供直观量化依据。
*caption: The SoTA SD method, EAGLE, has a training context length of 2048, which is significantly shorter than the context lengths of modern LLMs. 2023), and t… ｜ 论文 [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] ｜ arxiv 见 MD 元信息*

### LongSpec: Long-Context Lossless Speculative Decoding with Ef — Fig.2 (p.4)
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a)展示内存高效草稿模型：对输入"deep"用定长3-token窗口（gaunt/with/deep）做局部自注意力，再通过交叉注意力读取Target LLM的历史KV缓存，最终经LM Head预测"wrinkles"，实现以小内存消费长上下文。图(b)对比Vanilla索引（大间隔如0,1,2,803）与Anchor-Offset索引（锚点0-3+偏移段如10204-11221、30004-30055），证明后者能将短文本训练的位置分布拉近长文本训练，显著缩小能力Gap。图(c)将Flash Attention（全✓的prefix快路径）与Mask Attention（按speculative tree掩码的灵活路径）合并为Hybrid Attention。三组件分别解决草稿建模内存、训练分布对齐、树形验证效率问题，共同支撑LongSpec在长上下文下的无损推测解码。
*caption: Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and the Hybrid Tree Attention. (a) We use a sliding window self-attention… ｜ 论文 [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] ｜ arxiv 见 MD 元信息*

### LongSpec: Long-Context Lossless Speculative Decoding with Ef — Fig.3 (p.7)
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig03.png]]
> [!tip] 【图文联合解读】图3以5子图×5数据集（G/Q/M/L/R）柱状对比LongSpec（深蓝）与MagicDec（浅蓝）在T=1下的解码速度（tokens/s），覆盖Vicuna-7B/13B、LongChat-7B/13B与LLaMA-3.1-8B。LongSpec在所有25组组合中均显著领先：7B/8B模型实现约2.4–2.5×加速（如LongChat-7B在LCC：51→124 tokens/s，Vicuna-7B在LCC：50→119），13B模型约2×加速（如LongChat-13B在LCC：37→93）。该图证明其高效草稿生成与验证机制在跨模型、跨长文任务下稳定有效，是论文实验链路中支撑"长上下文无损加速"结论的核心证据。
*caption: Decoding speed (tokens/s) across different models and settings. All results are computed at T = 1. The letters G, Q, M, L, and R on the horizontal axi… ｜ 论文 [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] ｜ arxiv 见 MD 元信息*

### LongSpec: Long-Context Lossless Speculative Decoding with Ef — Fig.4 (p.8)
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图中展示长上下文训练过程中两条Loss曲线（横轴Steps 0–1200）：红色为启用了Anchor-Offset Indices的预训练模型，初始Loss约4.2并快速收敛至~3.5；蓝色为未启用版本，初始Loss高达~6.3，需经约1200步才降至同等水平。红色箭头标注"3.93×"，定量说明无Anchor-Offset需多花近4倍训练步数才能追上。

该图作为训练阶段的实证依据，证明Anchor-Offset位置编码策略在长上下文建模中具备显著更优的起点Loss与收敛效率，为后续投机解码中Draft模型对超长位置信息的准确预测提供了关键的模型质量前提，从而支撑Table 4中更高的平均接受长度τ与解码加速结论。
*caption: Training loss curves on long-context data.… ｜ 论文 [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] ｜ arxiv 见 MD 元信息*

### LongSpec: Long-Context Lossless Speculative Decoding with Ef — Fig.5 (p.8)
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig05.png]]
> [!tip] 【图文联合解读】**核心对象与量化数据**

Figure 5 以水平堆叠条形图分解单次投机解码循环的延迟，对比 **EAGLE（~78 ms）** 与 **Hybrid Tree Attention（~40 ms）**，分四段：draft model forward、target model attention、target model FFN、verification。EAGLE 中 target attention 约 50 ms（占绝对主体）；Hybrid 将其压缩至 ~12 ms（约 4× 加速），draft、FFN、verification 三段基本不变，总耗时近乎减半。

**关键技术结论**

该图量化佐证 caption 论述：Hybrid Tree Attention 的收益**集中体现在目标模型注意力层**，直接缓解长上下文验证阶段的注意力计算瓶颈，验证了作者"目标模型 attention 层显著降低"的论断。

**在论文整体链路中的作用**

作为 LongSpec 核心效率实证证据，支撑其"长上下文无损 + 高效"的设计主张；与吞吐、接受率等实验数据相互呼应，证明优化并非以牺牲无损性为代价。
*caption: Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latenc… ｜ 论文 [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] ｜ arxiv 见 MD 元信息*

### LongSpec: Long-Context Lossless Speculative Decoding with Ef — Fig.6 (p.9)
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig06.png]]
> [!tip] 【图文联合解读】图6展示Vanilla、MagicDec、LongSpec在批大小1–8下的吞吐量。LongSpec全面领先——批大小8时达约560，是Vanilla(~290)与MagicDec(~312)的近2倍；而MagicDec与Vanilla曲线几乎重合，差距<10%。原文据此论证：在长输出推理场景中，前缀较短使MagicDec的草稿模型退化为目标模型而失效；LongSpec通过高效草稿与验证机制突破了这一瓶颈，是支撑"无损推测解码可应用于长上下文/长输出"这一核心结论的关键实验证据。
*caption: Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such long-output scenarios because the initial inference stage of the long … ｜ 论文 [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] ｜ arxiv 见 MD 元信息*

### SpecExtend: A Drop-in Enhancement for Speculative Decoding o — Fig.1 (p.1)
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig01.png]]
> [!tip] 【图文联合解读】图1展示Llama-3.1-8B-Instruct+EAGLE-3在1K–128K输入长度下的双轴数据：绿色折线为吞吐量(tokens/s)，堆叠柱为显存占用(蓝Model Weights+橙KV Cache)。量化可见：吞吐量从1K的~150骤降至4K的~45 tokens/s；而KV Cache在≤32K时仍<2 GiB，直至128K才增至~16 GiB与权重持平。

**技术结论**：性能崩塌远早于显存瓶颈出现，说明长序列下推测解码减速的主因并非KV Cache显存/带宽，而源自其他机制(如草稿模型匹配率下降、注意力计算开销等)。

**论文作用**：以"反直觉"现象作为核心动机，引出SpecExtend——针对非显存瓶颈的长序列性能退化，提出对推测解码的即插即用增强方案。
*caption: Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct and EAGLE-3 across varying input lengths. Performance significantly de… ｜ 论文 [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] ｜ arxiv 见 MD 元信息*

### SpecExtend: A Drop-in Enhancement for Speculative Decoding o — Fig.2 (p.2)
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig02.png]]
> [!tip] 【图文联合解读】该图展示SpecExtend整体流程：长输入序列切分为8个Chunk，经Flash Attention Prefill并行输入Target与Draft模型；Target通过Hybrid Tree Attention验证Draft生成的候选Token，其Attention Scores经"Cross-model Retrieval"反向回传，从8个Chunk中筛选出{1,3,7,8}保留至Draft Model KV Cache，实现draft与target的KV对齐。

论文以此论证三项drop-in加速技术——Prefill阶段FlashAttention、Verify阶段Hybrid Tree Attention、基于注意力分数的Chunk选择性缓存——在无需额外训练下兼顾draft速度与准确性，为Table 2中相对自回归生成取得显著Speedup提供了核心方法学支撑。
*caption: Overview of SpecExtend. FlashAttention accelerates the prefill phases of both target and draft models, and Hybrid Tree Attention accelerates the verif… ｜ 论文 [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] ｜ arxiv 见 MD 元信息*

### SpecExtend: A Drop-in Enhancement for Speculative Decoding o — Fig.3 (p.4)
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig03.png]]
> [!tip] 【图文联合解读】左图：Hard/Easy token接受率（%），CMR≈61.5/75，均高于StreamingLLM的60/70.5；右图：1st/2nd/3rd/Resampled四位置的自然散度D_LK，CMR前三位置约0.25–0.33、Resampled约0.74，均低于StreamingLLM的0.37–0.39与0.84。

论文据此论证两点核心结论：(1)CMR在难易token上drafting均更准确，接受率提升；(2)CMR使draft分布与target模型在所有位置均更对齐，分布差异更小。

该图在论文中的作用：作为SpecExtend核心模块CMR的微观有效性证据，与第4节端到端加速比互补，从"分布层"和"接受率层"共同支撑CMR作为长序列推测解码"即插即用"增强模块的核心论点。
*caption: Left figure shows acceptance rates for hard and easy tokens, where CMR enables more accurate drafting in both cases compared to StreamingLLM.… ｜ 论文 [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] ｜ arxiv 见 MD 元信息*

### SpecExtend: A Drop-in Enhancement for Speculative Decoding o — Fig.4 (p.5)
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig04.png]]
> [!tip] 【图文联合解读】**图(a) 平均接受长度（Vicuna-7B/68M，1K→16K 输入）**
- Standard（绿）：从 ~3.75 骤降至 ~1.7
- StreamingLLM（橙）：从 ~3.7 降至 ~2.55
- SpecExtend（蓝）：始终最高，从 ~3.8 仅降至 ~2.95

**图(b) 16K-token 端到端时延堆叠（Target/Draft Prefill + Verification + Drafting）**
- Standard 总计约 17 s，Verification（绿）占主导 ~12 s、Drafting（粉）~3 s
- With SpecExtend 总时延骤降至 ~5.5 s，验证与起草段均显著压缩

**论证结论与作用**：原文以(a)说明长序列下传统 KV cache 失效致接受长度崩塌、加速失效；以(b)量化SpecExtend 作为 drop-in 模块带来的约 3 倍时延收益。该图在论文实验链路中承担"质量不丢、墙钟显著降低"的双重证据，是支撑 SpecExtend 在长上下文投机解码有效性的核心可视化。
*caption: (a) Average accepted length of Vicuna-7B/68M across different draft model cache settings. (b) End-to-end latency breakdown of speculative decoding on … ｜ 论文 [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] ｜ arxiv 见 MD 元信息*

### SpecExtend: A Drop-in Enhancement for Speculative Decoding o — Fig.5 (p.6)
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读**

1) 该图为四面板分组柱状图（图片可见右侧"LC-7B/LC-68M"与"LC-7B/EAGLE"两面板），横轴为GovReport上1K–16K输入长度，纵轴加速比0–3.5，深浅蓝柱对比标准投机解码与SpecExtend。关键数据：LC-68M在8K由1.12升至2.30、16K由1.51升至2.84；EAGLE在16K由1.81升至3.21。

2) 原文论证：标准投机解码随序列增长加速比显著衰减（16K仅1.51/1.81），而SpecExtend始终保持>1.8并呈上升趋势，长序列增益最明显，证实其对长输入的稳健加速能力。

3) 该图是论文核心实验证据，验证SpecExtend作为即插即用模块在不同draft模型（LC-68M、EAGLE）与各长度下均稳定提升加速比，支撑其长序列泛化性与工程实用价值。
*caption: Speedup comparison of standard speculative decoding and SpecExtend across varying input lengths on… ｜ 论文 [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] ｜ arxiv 见 MD 元信息*

### SpecExtend: A Drop-in Enhancement for Speculative Decoding o — Fig.6 (p.7)
![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig06.png]]
> [!tip] 【图文联合解读】**图6联合解读：**

图6对比Naive AR、EAGLE-3、EAGLE-3+SpecExtend三种方法在DeepSeek-R1-Distill-Llama-8B/AIME-24长推理任务上的解码速度（左，Tok/s）与平均接受长度（右）。具体数据：Naive AR为31.42/1.00，EAGLE-3为30.34/1.89，EAGLE-3+SpecExtend跃升至117.21/5.95。

**关键结论：** 单独EAGLE-3在长推理场景下速度甚至略低于自回归基线（30.34 vs 31.42），表明草稿模型在长序列后段出现退化；叠加SpecExtend后速度提升约3.7倍，接受长度提升约3.1倍。

**作用：** 该图是验证SpecExtend作为即插即用模块在长思维链推理场景下有效性的核心定量证据，支撑论文"无需重训练即可恢复并放大EAGLE-3加速收益"的核心主张。
*caption: Decoding speed (left) and average ac- cepted length (right) of the DeepSeek-R1-Distill-Llama- 8B/EAGLE-3 setup on the long reasoning task with the AIM… ｜ 论文 [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.1 (p.3)
![[assets/crops/a-survey-of-large-language-models-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图1以arXiv月度标题/摘要精确匹配统计：**(a)**"language model"自2018年6月起累计从约200篇（GPT-1锚点）增至2023年初近10000篇（GPT-4）；**(b)**"large language model"自2019年10月近乎零（T5锚点）飙至约1780篇（GPT-4），两曲线均呈指数式爆发。作者借此论证：从早期语言建模到GPT-4等复杂任务求解是科学思维的重要飞跃，LLM兴起标志着AI研究范式转折。该图作为引言动机，为后文Table 1对十亿级LLM的系统梳理与技术演进讨论奠定量化基础。
*caption: As discussed before, language model is not a new tech- nical concept specially for LLMs, but has evolved with the advance of artificial intelligence o… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.3 (p.99)
![[assets/crops/a-survey-of-large-language-models-fig03.png]]
> [!tip] 【图文联合解读】图3以时间轴（2019–2026）呈现约70+款代表性LLM。2019年仅T5单点；2022–2024集中爆发（GPT-3/4、LLaMA2、Qwen、Claude 3.5、DeepSeek等）；2025年单年即含DeepSeek-R1、GPT-o3、Claude 4.5、LLaDA、M2等30+款；黄色高亮标记公开权重模型。

**技术结论**：LLM研发呈指数级扩张，开源生态与商业闭源双轨并行，中美欧多元主体激烈竞争，迭代周期压缩至月级。

**论文作用**：作为综述"全景基线图"，为后续预训练、对齐微调、应用等章节建立模型谱系与时序坐标，辅助读者跨章节交叉定位与引用。
*caption: – Section 4: add LLM-based data filtering and selec- tion methods in Section 4.1.2; update Section 4.2.1, “Emergent Architectures” to include more dis… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.4 (p.7)
![[assets/crops/a-survey-of-large-language-models-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1）核心对象与结构：** 图中以时间轴串联GPT-1(2018.06)→GPT-2(2019.02)→GPT-3(2020.05)→Codex(2021.07)→GPT-3.5(2022.03)→GPT-4(2023.03)，并下挂两条虚线支链：一条经 code-davinci-002 → text-davinci-002（+instruction）→ text-davinci-003（+RLHF）→ gpt-3.5-turbo（+chat）；另一条延伸至GPT-4 Turbo与GPT-4 Turbo with vision(2023.09)。ChatGPT横跨GPT-3.5与GPT-4。

**2）关键论证结论：** GPT系列沿"decoder-only生成式预训练→规模化→上下文学习→代码专门化→指令微调→RLHF对齐→对话/多模态"路径演进，体现decoder-only架构与人类对齐技术是LLM能力跃迁的两大核心驱动力。

**3）论文中的作用：** 为综述提供GPT系发展时间锚点，作为代表性LLM案例支撑后续方法分类与能力分析。
*caption: The basic principle underlying GPT models is to compress the world knowledge into the decoder-only… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.5 (p.12)
![[assets/crops/a-survey-of-large-language-models-fig05.png]]
> [!tip] 【图文联合解读】**【图文联合解读·图5 LLaMA进化图】**

**1) 核心对象与结构：** 以LLaMA为根节点的有向进化图，共30+变体，按4类边演化——①红虚线"继续预训练"派生Chinese-LLaMA、BiLLa、Panda等中文化版本；②绿/蓝实线"模型/数据继承"对应指令微调，衍生Alpaca、Vicuna、BELLE、Ziya、Chinese-Alpaca等；③任务/领域适配支线（含图标分类：数学Goat、医疗ChatMed、法律Lawyer LLaMA、TaoLi等）+RLHF线（PKU-Beaver）；④虚线框内为多模态扩展（LLaVA、MiniGPT-4、OpenFlamingo、VisionLLM）。

**2) 关键论证：** 原图集中论证——开源LLaMA通过"继续预训练+指令微调+任务适配+多模态扩展"四条路径，在数月内引爆社区生态，验证了开源模型相对闭源在迭代速度与跨域扩散上的显著优势。

**3) 论文作用：** 作为开源生态爆炸式发展的具象证据，支撑全文核心论点"开源驱动LLM快速迭代与领域/模态扩散"，并串联方法论章节对指令微调、RLHF、领域适配、多模态技术的讨论。
*caption: Public API of LLMs. Instead of directly using the model copies, APIs provide a more convenient way for common users to use LLMs, without the need of r… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.7 (p.18)
![[assets/crops/a-survey-of-large-language-models-fig07.png]]
> [!tip] 【图文联合解读】图7展示LLM预训练前的**6阶段数据预处理流水线**：①原始语料（网页/书籍/代码等）→②过滤筛选（语言/度量/统计/关键词四类启发式规则）→③去重（句级、文档级、集合级）→④隐私脱敏（检测并移除PII）→⑤分词（SentencePiece、Byte-level BPE等）→⑥得到可直接喂入训练的token序列。

**原文论证**：高质量语料是预训练基础；过滤阶段采用分类器式与启发式两种互补策略，可显著降噪提质。

**论文作用**：作为数据准备章节的方法总览图，将文本采集到模型训练的全链路可视化，奠定后续分词、模型架构与训练策略论述的事实基础。
*caption: Filtering and Selection. To remove low-quality data from the collected corpus, existing work generally adopts two ap- proaches, namely classifier-base… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.8 (p.20)
![[assets/crops/a-survey-of-large-language-models-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示4类数据源（Source 1–4）依次在Stage 1、Stage 2、…、Stage n–1、Stage n共n个预训练阶段中的占比柱状变化：Stage 1以Source 1为主，Stage 2趋向四源均衡，Stage n–1偏向Source 3，Stage n又以Source 4最重。曲线箭头标注"Data Mixture"指向任一阶段内的源配比，大括号"Data Curriculum"则横跨所有阶段。

原文借此论证两点关键结论：① 数据混合在**全局**层面设定源分布；② 数据课程在**局部**允许各阶段按比例动态调整，以契合不同能力的培养需求。该图是论文第4章数据准备部分的核心可视化，串联起数据源选择→混合策略→课程调度的完整预训练数据管线，为下游训练实验章节提供调度框架支撑。
*caption: Data Mixture. Since each kind of data source is closely related to the development of certain capacities for LLMs (referring to the discussions in Sec… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.9 (p.22)
![[assets/crops/a-survey-of-large-language-models-fig09.png]]
> [!tip] 【图文联合解读】图以"A Survey of Large Language Models"（前3 token为prefix、后3为target）为示例，用三个6×6矩阵对比三种架构的注意力模式，颜色编码：前缀互注意（蓝）、前缀→目标（绿）、目标互注意（黄）、掩码（灰）。具体差异：
- **Causal Decoder**：prefix单向（左下蓝三角）、target因果（右下黄下三角）、prefix→target绿，无target→prefix；
- **Prefix Decoder**：prefix全蓝、target全黄（双向），仅target→prefix掩码；
- **Encoder-Decoder**：编码器3×3全蓝（双向），解码器行对编码器列绿（cross-attention），target自身因果。

论文借此论证三类主流架构的本质差异在于注意方向性与prefix/target是否解耦，奠定GPT系、LLaMA系、T5系LLM分类的架构谱系基础，是方法论总览部分的关键可视化锚点。
*caption: Encoder-decoder Architecture. The vanilla Transformer model is built on the encoder-decoder architecture [22], which consists of two stacks of Transfo… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.13 (p.43)
![[assets/crops/a-survey-of-large-language-models-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图13展示了四种参数高效微调（PEFT）方法的结构对比：

**(a) Adapter Tuning**：在每个Transformer层的MHA与FFN之后各插入一个瓶颈结构的Adapter模块（绿色），仅训练新增的小模块参数。

**(b) Prefix Tuning**：在每一层输入前拼接可训练前缀向量（红色），冻结原模型参数。

**(c) Prompt Tuning**：仅在输入层最前端添加可学习Prompt（黄色），不侵入各层结构，最轻量。

**(d) LoRA**：在权重矩阵旁并行低秩分解矩阵（W_up、W_down，橙色），推理时可合并。

**论证结论**：四种方法的核心思想一致——冻结预训练LLM绝大部分参数，仅微调极少量新增参数（Adapter、前缀、Prompt或低秩矩阵），即可适配下游任务。

**论文作用**：作为第43页"Parameter-Efficient Fine-Tuning"小节的核心图示，与Table 4的定量对比呼应，为后续章节讨论指令微调与RLHF的成本权衡提供方法论支撑，是LLM高效适配技术的总览入口。
*caption: Adapter Tuning. Adapter tuning incorporates small neural network modules (called adapter) into the Transformer mod- els [406]. To implement the adapte… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.16 (p.54)
![[assets/crops/a-survey-of-large-language-models-fig16.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 16）：**

图示 **Planning Framework** 含三大核心组件——**Task Planner (LLM)**、**Plan Executor**、**Environment**，并附 Memory、Tool 两个辅助模块。流程为：Task→LLM 生成 Plan→Executor 输出 Action 作用于 Environment→Environment 经 Feedback 回传 Planner 触发 plan refine→最终输出 Result。底部按 **Internal(LLM 自身)** 与 **External(Human / World / Others)** 对组件分类。

原文据此论证：LLM 可作为 task planner，生成自然语言动作序列或可执行程序形式的多步整体方案，闭环反馈支持计划的迭代修正与泛化。

作用上，该图作为论文**规划范式的总纲（统一形式化框架）**，为后文具体方法（zero-shot / few-shot / CoT 规划、ReAct 等）提供一致的组件划分与交互参照。
*caption: In this paradigm, there are typically three components: task planner, plan executor, and environment36. Specifically, task planner, which is played by… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### A Survey of Large Language Models — Fig.17 (p.59)
![[assets/crops/a-survey-of-large-language-models-fig17.png]]
> [!tip] 【图文联合解读】**图文联合解读（图17）：**

该图以两组人机对话并排对比两类幻觉：**(a)内在幻觉**——输入"Bob之妻Amy、之女Cindy，谁是Cindy对Amy的关系？"，模型却答"Cindy是Amy的**daughter-in-law**（儿媳）"（红字标注），与输入直接矛盾，应为孙女关系；**(b)外在幻觉**——被问及"RLHF含义"时，模型将其臆造为"Rights, Limitations, Harms, and Freedoms"（红字），却正确解释了LLM，无中生有。

**论证结论：** 幻觉不仅在GPT-4等顶尖LLM中普遍发生，且模型自身难以识别文本中的幻觉内容。

**章节作用：** 作为第59页"幻觉挑战"小节的关键实证样例，与LVLM幻觉引用[604]共同支撑作者对可信度风险的定性论述，引导后续缓解策略章节。
*caption: Hallucination widely occurs in existing LLMs, even the most superior LLMs such as GPT-4 [46]. Furthermore, existing work shows that LLMs encounter dif… ｜ 论文 [[a-survey-of-large-language-models]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.1 (p.2)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示展示了自回归生成的两个连续步骤（Step 1、Step 2），序列由"The"、"apple"、"tas"等青色 token 框组成，曲线箭头表示当前新 token 对所有历史 token 的注意力依赖；右下方粉色框标注"KV Cache"，用于存储历史 token 的 K、V 矩阵。

**核心结论：** 图示直观论证 KV cache 的必要性——若无缓存，每步都需从头重算所有历史 token 的 K、V，时间复杂度为 O(n²)；借助缓存复用，仅需计算新增 token，使单步注意力降为 O(n)。

**论文作用：** 作为 Figure 1 置于引言，奠定全文优化动机，后续章节围绕"如何更高效地压缩/共享该缓存"展开，属于全文技术链路的问题定义与起点。
*caption: Autoregressive generation, at each step the new token (orange) attends to all prior tokens (cyan). Without caching, keys and values for every past tok… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.2 (p.3)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读**

1) **核心对象与结构**：图示单层 Transformer 内 KV cache 的数据流。输入 token $x_t$（橙色）经三个投影 $W_Q, W_K, W_V$ 分流：$Q_t$（黄色，左侧）无需缓存；$K_t, V_t$（teal 蓝绿）依次 append 到各自的 cache $K_c=[K_1,\ldots,K_t]$、$V_c=[V_1,\ldots,V_t]$（teal 框标注缓存区）。底部给出注意力的完整计算式 $\mathrm{softmax}(Q_tK_c^\top/\sqrt{d_k})V_c$。右侧橙色标注明确指出缓存体量为 $t\times d_v$，每头每层线性增长。

2) **关键技术结论**：teal 色块直观看清"被缓存的对象"就是 K、V 两路；其大小随已解码 token 数 $t$ 以 $O(T)$ 增长，逐 token 累积、不可压缩释放。这正是后文所有 KV cache 优化策略（量化、淘汰、共享、压缩、分页等）共同针对的内存瓶颈来源。

3) **论文链路作用**：作为全文"问题定义"奠基图——在介绍任何优化方法之前，先建立 KV cache 的结构、大小与访存模式，为后续 5 大类优化技术的分类与实验对比提供统一的参照基线。
*caption: Data-flow of the KV cache within a single transformer layer. Input token xt fans into three projections; Kt and Vt are appended to their respective ca… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.3 (p.3)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig03.png]]
> [!tip] 【图文联合解读】图以32K–128K上下文为横轴、FP16 KV缓存显存为纵轴，展示LLaMA‑2 7B、13B、70B三条线性增长曲线；128K时缓存分别约64、80、40GB。虚线表示A100 80GB容量，点线表示FP16参数显存（约14、26GB）。KV缓存随序列长度持续膨胀：7B仅缓存就占64GB，计入14GB参数后几乎耗尽单卡显存，成为推理瓶颈。该图为后文缓存压缩、量化及调度卸载实验提供容量基线与必要性依据。
*caption: KV cache memory as a function of context length for three LLaMA-2 model variants under fp16 precision.… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.4 (p.4)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以 4×4 因果自注意力矩阵呈现"The apple tastes sweet."的注意力分布，采用 Viridis 配色（深紫=低、黄=高），灰色表示被掩码的未来 token；右下"Query=sweet"行可读出对"apple"约 0.65（对应 caption 中 65%）、"tastes"约 0.20、"sweet"自注意约 0.10，行和归一为 1。

论文借此论证：**KV 条目重要性高度不均**——个别 token（如 sweet→apple）承载绝大部分注意力，其余条目贡献微弱。这正是 H₂O、SnapKV 等基于注意力分数驱动的 KV 淘汰策略的核心前提，为后文量化、淘汰与预算分配等优化章节提供直觉依据与动机锚点。
*caption: Causal self-attention weight matrix for “The apple tastes sweet.” visualised with the Viridis colormap (dark purple = low, yellow = high). Gray cells … ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.5 (p.5)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig05.png]]
> [!tip] 【图文联合解读】图以"KV Cache Optimization"为根节点，向下展开五条并列分支：①Cache Eviction（H₂O、SnapKV、NACL、Ada-KV）；②Cache Compression（KIVI、PALU、MiniCache、KVQuant）；③Hybrid Memory（PagedAttention、InfiniGen、LayerKV）；④New Attention Mechanism（Linear、Log-Linear、KIMI Linear）；⑤Combination Methods（FlexGen、ShadowKV、TailorKV）。原文借此论证：KV 缓存优化是从丢弃、压缩、存储分配、注意力改造到组合方案的多维系统化路径，而非单一手段。该分类法为后续各章节的方法对比、性能基准测试与综述分析提供了统一归类框架，是整篇 survey 的方法学骨架。
*caption: Taxonomy of KV cache optimization techniques surveyed in this paper, organized into five major categories.… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.6 (p.6)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig06.png]]
> [!tip] 【图文联合解读】图6以4个10×10因果注意力图比较动态、步幅、局部静态稀疏及带H2O的策略；H2O额外标出高注意力列，左下图以0.2、0.1、0.1、0.6（累加1.4、1.5、0.5、0.6）说明按累计注意力保留KV。右下示意约0–100%内存压缩、50–80%准确率的权衡：固定策略约60%后明显降精度，H2O到约90%仍接近80%。该图以“近期+高重要性远距token”的淘汰机制连接缓存结构与评测，作为框架概览和概念性权衡说明，并非完整实验表。
*caption: Upper plots illustrate symbolic plots of an attention map deploying different KV cache policies in LLM generation. Lower right: contrasts their accura… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.7 (p.7)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig07.png]]
> [!tip] 【图文联合解读】**图7图文联合解读：**

**1）核心对象与结构：** 图示SnapKV的三阶段压缩流程。输入序列KV按"层"维度展开，含白色Prefix与绿色Obs.window（观察窗）；中间通过Attention Weight Calc.（以观察窗为query）与Voting机制，在每层每个注意力头投票筛选出橙色重要特征；底部经Clustering聚类后拼接Obs.window，产出Compressed KVs。右侧以Q4财报问答为例，验证压缩后仍可定位"R&D expenses"等关键事实。

**2）关键技术结论：** Prefix中注意力权重具有高度集中性与可聚类性，仅保留每头重要特征簇即可近似全量KV，论证了"少而精"的KV即可支撑高质量生成。

**3）论文作用：** 作为SnapKV核心方法示意图，与全量KV基线对比，证明长上下文KV cache可大幅压缩而生成质量几乎无损，为高效推理链路提供方法支撑。
*caption: The graph shows the simplified workflow of SnapKV, where the orange area represents the cluster of features per head selected by SnapKV. These feature… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.8 (p.9)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）图示对象为KV cache矩阵X∈R^(l_prompt×d)：蓝色大矩形为完整缓存，红色虚框沿d维度（通道/列方向）取出一列，标注 s_X, z_X∈R^d，表明缩放因子与零点按"通道"逐列计算——即**per-channel quantization**沿token维度聚合统计量。

2）结合正文"K中某些维度幅度极大"的观察，该图论证：Key cache存在显著通道级异常值，故需**逐通道量化**以保留敏感维度精度；而Value无此模式，KIVI改用per-token量化，二者结合构成KIVI的核心设计。

3）该图为KIVI方法的关键可视化依据，支撑其"Key per-channel + Value per-token"非对称量化策略，为后续实验链路中实现4-bit近无损压缩提供理论直觉与方案锚点。
*caption: Definition of per-token and per-channel quantization. X ∈Rlprompt×d is the key/value cache, where lprompt is the number of tokens and d is the number … ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.9 (p.9)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示 Palu 的低秩 KV-cache 压缩流——原始线性投影权重 W 被分解为下投影矩阵（左侧输入 X 块）与上投影矩阵 **B**（底部红块）；蓝色"Original KV"框中为完整输出 **Y**，红色文字"**Cache H instead of Y**"标示被替换的缓存对象。虚线箭头表示下投影到低维隐表示 **H**，实线箭头表示由 B 重建回 Y。

2) **关键结论**：推理时不再缓存完整 K/V 张量 Y，而只缓存经低秩压缩后的 H；Y 可通过 Y ≈ B·H 低成本重建，从而以 rank 比例缩减 KV-cache 显存，同时保持输出近似等价。

3) **论文作用**：作为 Palu 章节的方法示意图，为"低秩投影压缩 KV-cache"这一核心论点提供直观机制说明，支撑后续实验在长上下文、多 batch 推理场景下显存与吞吐收益的论证。
*caption: Palu’s low-rank projection method for KV-cache reduction. A weight matrix W of linear projection is decomposed into two low-rank matrices. Input X is … ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.10 (p.11)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示vLLM分布式推理架构：1个**Scheduler**（绿色）调度N个**Worker**（Worker 0…N−1），每Worker含一个**Cache Engine**与一个**Model Shard**（各占一块GPU）；**KV Cache Manager**持有两张**Block tables**（图中以粉色列高亮，类比OS页表），下接**CPU Block Allocator**与**GPU Block Allocator**两级分配器，跨设备管理KV块。

原文据此论证三条关键技术结论：①KV缓存采用**块级（page-like）**粒度管理以消除碎片；②模型按Shard在多Worker间并行，调度与缓存解耦；③CPU↔GPU两级分配器支撑KV块在主存与显存间的灵活映射，是后续swap/offload/prefix-sharing等优化的前提。

该图位于论文第11页，作为后续PagedAttention、内存交换、跨设备卸载等KV优化策略讨论的**系统基线参照框架**，统一读者对vLLM组件边界的认知。
*caption: vLLM system overview [22]. 11… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.11 (p.12)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig11.png]]
> [!tip] 【图文联合解读】**核心对象与结构：** 图示InfiniGen预取模块三阶段操作流——Offline（Skewing离线分析token重要性）、Prefill（Partial Weight Idx Generation生成选中token索引）、Decoding（逐层推理）。GPU/CPU双时间轴并行：GPU执行Layer(i-1)的KV Sel.→Attention→FFN时，CPU同步Prefetching；Layer i改用Light Attention接收CPU回传的Selected Keys/Values。

**关键技术结论：** 离线Skewing识别重要token，Prefill阶段仅生成部分权重索引；Decoding利用层间计算间隙在CPU预取目标K/V，使数据传输与GPU计算重叠，隐藏访存延迟。

**论文作用：** 作为"预测式预取"代表方案，与LayerKV的层间切分策略形成对比，论证KV-cache优化机制多样化（重要token预测+CPU-GPU预取重叠），支撑长序列LLM推理降开销讨论。
*caption: Operation flow of the prefetching module of InfiniGen. [23]. A layer-wise KV cache management strategy is proposed in LayerKV [24]. The core concept i… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.12 (p.15)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示上方"标准线性注意力"为**单层顺序链**：每步接收Q、K、V——顶部为3维查询向量、底部为3×3键值矩阵，经单节点处理后水平传递历史状态，复杂度O(N)；下方"对数线性注意力"采用**双层分层结构**：底层K、V先经多个分桶节点并行聚集，再通过⊕加法运算合并至上层节点，形成对数级深度的递推架构。

该对比论证关键结论：标准线性注意力复杂度低但只能拟合全局线性关系、表达力受限；分层对数线性结构以近线性代价换来更强的近似能力。在论文中，此图位于**注意力机制综述**背景章节（[30]引文），用于引出"局部线性注意力"等改进思路，为后续KV-Cache压缩、稀疏化等核心方案奠定理论与结构基础。
*caption: Standard linear attention (top) vs. loglinear attention (bottom). The input consists of query, key, and value vectors [30]. at nearby keys and average… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.13 (p.17)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig13.png]]
> [!tip] 【图文联合解读】图13展示ShadowKV的GPU–CPU混合架构，分两阶段：

① **Pre-filling**：GPU对Pre-RoPE Key Cache并行三条路径——SVD生成Low-rank Key Cache、RoPE&Reduce生成Landmarks、Find Outliers标记Outliers，三者均Cached于GPU；Value Cache则Offload至CPU。

② **Decoding**：Landmarks经KV Sel.判别Cache Hit/Miss，Missed Chunk IDs下发CPU做Value Cache Fetching；Low-rank Key Cache经Reconstruction+RoPE，与Outliers共同汇入Sparse Attention。

**论文作用**：该图直观论证了"低秩Key+Landmarks+Outliers驻GPU、Value卸CPU"的存储分工，以及"Landmarks引导稀疏注意力"的访存机制，是ShadowKV将KV总占用压缩至单层约2.3GB、支撑百万级长上下文推理的核心设计，构成论文KV压缩方法链的关键一环。
*caption: During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaining a low-rank key cache, landmarks, and outliers on the GPU. During de… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### KV Cache Optimization Strategies for Scalable and Efficient  — Fig.14 (p.17)
![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示TailorKV系统全景，分三大模块：①**离线识别**——依据注意力分数与估计稀疏度，将各层划分为Quantization Friendly或Sparsity Friendly两类；②**Prompt Encoding**——量化友好路径对Keys做Per-Channel量化、Values做Per-Token量化，结果存入Quantized KV Cache Buffer；③**Token Generation**——量化层执行混合精度矩阵乘；稀疏层则通过Critical Key Buffer（writing/reading）检索Top-K Tokens，结合Critical Current Query完成全精度矩阵乘。CPU端KV Cache Memory Pool配合Offload(1)、Prefetch(2/5)、Fetch(4)实现GPU-CPU协同；右侧Layer 0→N示意按层异构调度。

**作用**：作为方法总图，支撑"按层特性差异化压缩"的核心结论，是TailorKV端到端推理流水线的可视化总纲。
*caption: System overview of TailorKV. Offline identification categorizes the layers into quantization-friendly and sparsity-friendly. For quantization-friendly… ｜ 论文 [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] ｜ arxiv 见 MD 元信息*

### Kimi Linear: An Expressive, Efficient Attention Architecture — Fig.1 (p.1)
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig01.png]]
> [!tip] 【图文联合解读】```thinking
The image is Figure 1(b) from the Kimi Linear paper, showing TPOT (Time Per Output Token, ms) vs Decoding Length (4K to 1M tokens). Three curves: MLA (teal dashed, steep growth), GDN-H (orange, low growth), Kimi Linear (purple, low growth, overlapping with GDN-H). At 1M tokens: Kimi Linear ≈1.84ms vs MLA ≈11.48ms (6.3× speedup). Red arrows mark 4.8×/5.7×/6.3× speedups at 256K/512K/1M.

Need ≤220 Chinese chars covering: 1) quantified data/structure, 2) key technical conclusion from caption/text, 3) role in paper's overall argument chain.
```

**图文联合解读：**

图(b)展示TPOT(ms)随解码长度(4K→1M)的变化曲线：MLA(青色虚线)急剧攀升，1M时达约11.48ms；Kimi Linear(紫色)与GDN-H(橙色)近乎重合且低增长，1M时Kimi仅1.84ms。红色箭头标注256K/512K/1M处相对MLA的加速比依次为4.8×/5.7×/6.3×。

**原文论证结论：** Kimi Linear在长序列解码中维持低TPOT，与GDN-H持平并显著优于MLA，支持更大batch，从而实现端到端推理加速。

**论文作用：** 与(a)图"性能-加速比Pareto前沿"互补，构成"质量不减、速度更优"的双重证据链，是验证Kimi Linear架构实用价值(尤其长上下文场景)的核心实验支撑。
*caption: (a) Performance vs. acceleration. With strict fair comparisons with 1.4T training tokens, on MMLU-Pro (4k context length, red stars), Kimi Linear lead… ｜ 论文 [[kimi-linear-an-expressive-efficient-attention-architecture]] ｜ arxiv 见 MD 元信息*

### Kimi Linear: An Expressive, Efficient Attention Architecture — Fig.2 (p.5)
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig02.png]]
> [!tip] 【图文联合解读】图2展示了batch=1、16头条件下，KDA（ours）与DPLR两种注意力内核在输入长度2K–64K（对数刻度）下的执行时间（ms）对比。KDA（紫色实线）从2K约2ms平稳增长至64K约30ms；DPLR（青色虚线）在64K时陡升至约58ms，曲线明显更陡。两者差距随序列长度扩大而显著拉大。

原文借此论证：KDA内核相对DPLR在长序列上具有更优的推理效率与更好的复杂度表现，是论文"expressive yet efficient"核心主张的关键效率证据，支撑Kimi Linear在长上下文场景下的实际部署可行性。
*caption: Execution time of kernels for vary- ing input lengths, with a uniform batch size of 1 and 16 heads.… ｜ 论文 [[kimi-linear-an-expressive-efficient-attention-architecture]] ｜ arxiv 见 MD 元信息*

### Kimi Linear: An Expressive, Efficient Attention Architecture — Fig.3 (p.5)
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图3展示Kimi Linear架构：每个块由token-mixing层（Norm+注意力）后接MoE通道混合层（Norm+MoE）组成，**采用"N个KDA层间插1个MLA层"的混合模式（图中标注N×与1×，N=3）**。右上展开MoE细节：含Ns个Shared Expert与Nr个Routed Expert（Router门控按概率分布选择）；右下展开KDA：两条路径分别经Linear+Conv与σ门控融合后送入Kimi Delta Attention。

**技术结论**：主体使用线性复杂度KDA保留细粒度信息，**周期性MLA层维持全局注意力锚点**；MoE的共享+路由专家设计兼顾通用知识与专项能力。

**论文作用**：作为方法总览图，与Table 3呼应——为"Kimi Linear同时超越纯MLA基线与GDN-H混合基线"的短上下文评估结果提供结构性依据，奠定"线性注意力+周期全注意力"的设计范式。
*caption: Neural Parameterization… ｜ 论文 [[kimi-linear-an-expressive-efficient-attention-architecture]] ｜ arxiv 见 MD 元信息*

### Kimi Linear: An Expressive, Efficient Attention Architecture — Fig.4 (p.7)
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图4为2×3网格：上行绘制256–2048序列长度下的峰值准确率，下行绘制1K token下20K步训练收敛曲线，对比KDA/GDN/Mamba2在Palindrome、MQAR、Stack三任务表现。数据上，KDA与GDN在短序列均近100%，但KDA约5K步即收敛，GDN需15–20K步；Mamba2于Palindrome（≥512）、Stack（≥1024）即降至0%，完全失效。论文借此论证KDA兼具**快速收敛**与**长序列表达力**，是唯一在三项任务同时有效的方案，为下游真实语言基准评测提供合成任务层面的理论支撑。
*caption: Results on synthetic tasks: palindrome, multi query associative recall, and the state tracking.… ｜ 论文 [[kimi-linear-an-expressive-efficient-attention-architecture]] ｜ arxiv 见 MD 元信息*

### Kimi Linear: An Expressive, Efficient Attention Architecture — Fig.5 (p.9)
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图中以双对数坐标对比 MLA（蓝，虚线，2.3092·C⁻⁰·⁰⁵³⁶）与 Kimi Linear（红，虚线，2.2879·C⁻⁰·⁰⁵²⁷）在不同算力 C（FLOP/s-days，约 10¹ 量级）下的损失曲线。两曲线斜率相近（衰减指数仅差 0.0009），表明两者随算力提升的收益节奏一致；但 Kimi Linear 曲线整体下移，等损失下算力节省约 **1.16×**。论文借此论证 Kimi Linear 在保持与 MLA 几乎相同 scaling 行为的同时，实现了显著的"常数级"效率优势，从而支撑其作为新注意力架构在长上下文场景中可扩展且更优的结论，是实验链路中验证方法有效性的关键定量证据。
*caption: The fitted scaling law curves for MLA and Kimi Linear. balanced positional bias across layers, which improves robustness and extrapolation at long ran… ｜ 论文 [[kimi-linear-an-expressive-efficient-attention-architecture]] ｜ arxiv 见 MD 元信息*

### Kimi Linear: An Expressive, Efficient Attention Architecture — Fig.6 (p.12)
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig06.png]]
> [!tip] 【图文联合解读】**图6核心对象与量化数据**

图6展示双面板折线图，追踪RL训练约20–110步过程中Kimi Linear@1.4T（紫实线）与MLA@1.4T（青虚线）在**(b) MATH 500 Test** 与 **(c) AIME 2025** 两个数学基准上的准确率。可读出关键数值：MATH 500上Kimi Linear收敛至约87–88%，MLA约78–80%，全程领先约6–8个百分点；AIME 2025上Kimi Linear达约22–23%，MLA约19%，领先约3–4个百分点。

**原文论证的关键结论**

Kimi Linear的KDA+MLA混合架构在整个RL阶段始终显著优于纯全注意力基线，证明高效注意力不会损害数学推理能力。

**在论文链路中的作用**

前文已论证训练效率与长上下文优势，此图补全"RL后训练推理能力不退化"的关键实证闭环，为"线性注意力可替代全注意力"这一核心主张提供下游任务维度的支撑。
*caption: The training and test accuracy curves for Kimi Linear@1.4T and MLA@1.4T during Math RL training. Kimi Linear consistently outperforms the full attenti… ｜ 论文 [[kimi-linear-an-expressive-efficient-attention-architecture]] ｜ arxiv 见 MD 元信息*

### Kimi Linear: An Expressive, Efficient Attention Architecture — Fig.7 (p.13)
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(b)为batch=1时TPOT随解码长度（4K→1M，对数刻度）变化曲线：MLA虚线随长度近似线性攀升至~18ms（1M处）；Kimi Linear（紫实线）与GDN-H（橙）几乎重合，1M处仅~8ms；图中标注在512K处提速1.8×、1M处提速2.2×。

**关键结论：** 长序列解码场景下，Kimi Linear较全注意力MLA取得1.8–2.2倍加速，且与GDN-H性能曲线几乎不可区分，说明其用线性注意力取代部分MLA层后，仍保持了类GDN的高效推理特性。

**论文作用：** 与图(a)预填充时延互为补充，从"预填充+解码"两端共同证明Kimi Linear相对MLA的全链路效率优势，是论证该架构具备实际部署价值的关键效率证据。
*caption: (a) The prefilling time of MLA (full attention), hybrid GDN-H and our Kimi Linear. (b) The time per output token (TPOT) for MLA, GDN-H and Kimi Linear… ｜ 论文 [[kimi-linear-an-expressive-efficient-attention-architecture]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.1 (p.1)
![[assets/crops/muon-is-scalable-for-llm-training-fig01.png]]
> [!tip] 【图文联合解读】图(b)可见：MMLU分数对训练FLOPs（2e22~1e24+，对数横轴）的Pareto前沿散点图。红星Moonlight-2.4B-1.2T与Moonlight-2.4B-5.7T精确落于蓝色虚线"MMLU Performance Frontier"上；约15个橙点对比模型（Qwen-2.5-14B/7B/3B、Gemma-2-9B、OLMo-2-13B/7B、Llama-3.1-8B、DCLM-7B、StableLM-2-12B、DeepSeek-V3-Small-2.4B等）多分布于前沿下方。

技术结论：结合(a)面板Muon相对AdamW拟合线整体更低、水平箭头标注"0.519× FLOPs"，论文主张Muon在计算最优训练下效率约2倍提升，使Moonlight以更低算力突破MMLU Pareto前沿。

论文作用：作为开篇总览图，将"优化器可扩展性"(a)与"下游能力评估"(b)双线耦合，是全文核心结论（Muon可大规模替代AdamW）的视觉锚点，为后续缩放实验与模型发布提供关键数据支撑。

（注：图像仅显示(b)面板，(a)面板依原文论述补充。）
*caption: Scaling up with Muon. (a) Scaling law experiments comparing Muon and Adam. Muon is ∼2× more computational efficient than Adam with compute optimal tra… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.2 (p.4)
![[assets/crops/muon-is-scalable-for-llm-training-fig02.png]]
> [!tip] 【图文联合解读】图含双面板。下方展示约35k–65k迭代中AdamW（绿）、无WD Muon（红）、加WD Muon（蓝）的验证损失曲线，两Muon变体均显著低于AdamW，且加WD Muon末段最低。上方差曲线（无WD−加WD）标注两关键节点：24k迭代处无WD领先0.023，66k迭代处被反超，加WD领先0.017。结论：随训练推进，权重衰减对Muon的正则化收益逐步累积并反超，使其最终收敛损失最低。论文作用：以消融形式证实WD是Muon可扩展训练配方不可或缺的一环，为完整方法链路提供关键支撑。
*caption: Validation loss curves for AdamW (green), Muon without weight decay (red), and Muon with weight decay (blue).… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.3 (p.7)
![[assets/crops/muon-is-scalable-for-llm-training-fig03.png]]
> [!tip] 【图文联合解读】**1) 图示内容**：横轴为训练算力 OP/s-days（log scale，约 10⁰–10¹），纵轴为 LM loss（log scale）。图中含两类曲线：实线为多组不同模型规模下 Muon（蓝）/AdamW（红）的实际训练轨迹（噪声明显）；虚线为两者的拟合标度律曲线。

**2) 关键结论**：在整个算力范围内 Muon 蓝色虚线始终位于 AdamW 红色虚线下方，且两条虚线斜率近似平行。拟合式为 $L_\text{Muon}\approx 2.506\cdot C^{-0.052}$，$L_\text{AdamW}\approx 2.608\cdot C^{-0.054}$——等算力下 Muon 绝对 loss 低约 0.1，且标度指数（0.052 vs 0.054）相近，说明其优势可随规模持续保持而非趋同。

**3) 论文作用**：作为整篇 scaling 实验的定量收束，验证 Muon 具备与 AdamW 同阶的标度行为但更优常数项，为 compute-optimal 配置与"Muon 可扩展"的核心主张提供直接证据。
*caption: Fitted scaling law curves for Muon and AdamW optimizers.… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.4 (p.10)
![[assets/crops/muon-is-scalable-for-llm-training-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：图为1×6子图网格（图中可见SharedExperts、Router、Dense三个，其余AttnQO、AttnKV、Experts被截），每图横轴为训练迭代次数（0–约30K+），纵轴为权重矩阵的SVD熵值；每图叠加AdamW（红）与Muon（蓝）两条曲线。具体数值：SharedExperts中AdamW从~0.94降至~0.90，Muon从~0.95降至~0.925；Router中AdamW约0.68→0.78，Muon高达0.91–0.96；Dense中AdamW稳定在~0.955，Muon约0.97–0.985。

2）**关键结论**：Muon在所有六类权重矩阵上的SVD熵均**一致高于**AdamW，说明Muon更新后奇异值分布更均匀、矩阵秩更满，有效抑制了AdamW训练中出现的"谱塌缩/方向退化"现象。这从频谱/几何角度揭示了Muon优越性来源——Newton-Schulz正交化保留了多方向学习能力。

3）**论文链路作用**：该图属于Muon论文的"机制分析"模块，紧接loss/benchmark等结果之后，为Muon可扩展性提供**理论级**解释，与正交化动量、谱范数控制等讨论呼应，构成"现象→机制→方法"的闭环论证。
*caption: SVD entropy of weight matrices across different training iterations. We categorize the weight matrices into 6 different groups: 1) AttnQO denotes the … ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.5 (p.15)
![[assets/crops/muon-is-scalable-for-llm-training-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图通过左右两面板呈现5个算力档（1.0e+20 → 8.9e+20 FLOPs）的优化景观：左面板为学习率（~0.0010–0.0014）与损失的关系，右面板为批量大小（200–900）与损失的关系。关键结构特征：(1) 算力每增一档，最终损失单调下降约0.02–0.05；(2) 最优批量随FLOPs上移，从~250扩至~850，呈明显的batch-size scaling；(3) 各档曲线在最优值附近均较平坦，表明最优超参对算力预算稳健。

论文用此图论证：**Muon优化器下的最优LR与batch size均遵循可预测的scaling law**，不同FLOPs档间曲线形状一致，验证了训练开销从1e20到8.9e20 FLOPs的可扩展性。
*caption: Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.6 (p.15)
![[assets/crops/muon-is-scalable-for-llm-training-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图6展示了计算**门控缩放因子（gate scaling factor）**的Python实现片段。代码对应一个函数（签名含`int, topk: int, iter_times: int`参数），注释涉及MoE（混合专家）、experts数量、top-k选择及迭代次数。可辨识的关键逻辑含`l1]`与`*0.5`操作，推测基于Newton-Schulz迭代的谱范数估计，对门控矩阵的更新按 √(fan_in) 或与topk、专家数相关的比例进行缩放，以保持更新谱范与Adam尺度一致。

**论证作用**：论文借此说明Muon优化器在推广至MoE架构时，需针对门控矩阵（非线性选择机制）定制缩放规则，确保与对hidden weights采用Newton-Schritz正交化更新时保持动力学一致，从而支撑"Muon可规模化"的核心结论。

**论文链路**：图6是方法论的可复现性补充，与Table 6（优化器在预训练/SFT阶段互换实验）形成"算法实现→跨阶段验证"的闭环，证明Muon不仅适用于dense LLM，在MoE结构与不同训练阶段同样有效。
*caption: D… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.7 (p.17)
![[assets/crops/muon-is-scalable-for-llm-training-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**(1) 核心对象与数据**  
图(b) Gradient Norm 横轴为训练迭代（0–37000次），纵轴梯度范数 0–1.0。红色 Moonlight-A 出现多次尖峰：约 12000 步达 ~0.95、16000 步达 ~1.0、还有 5000、8000、18000、24000 步等多处小尖峰；蓝色 Moonlight 则从起始 ~0.3 平滑衰减并稳定在 ~0.05 附近，无明显尖峰。图(d) Large Attention Logits Ratio (Layer 1) 纵轴 0–0.00014，蓝色 Moonlight 在 ~18000–25000 步出现剧烈尖峰（峰值 ~1.4e-4，集中在 21000–23000 步），而红色 Moonlight-A 全程贴近 0。

**(2) 关键技术结论**  
作者用此图对比两变体训练稳定性：Moonlight-A 梯度更易爆炸（高幅频繁尖峰），而 Moonlight 虽梯度平稳，却在第一层注意力 logits 上出现集中式大幅异常；两种不稳定形态不同但都揭示训练中的数值风险。

**(3) 在论文链路中的作用**  
该图为 Muon 优化器扩展至 LLM 训练时的训练动力学诊断证据，用于支撑后续归因分析与改进方案（如 rms 平衡项），位于 ablation/分析章节，承接主结果表、过渡至稳健性讨论。
*caption: Training dynamics comparison between Moonlight and Moonlight-A… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.8 (p.9)
![[assets/crops/muon-is-scalable-for-llm-training-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图8以双对数坐标（Training FLOPs）展示各模型GSM8k得分，两个红色星标为Moonlight系列：2.4B-1.2T在约2e22 FLOPs下达46分，2.4B-5.7T在约9e22 FLOPs下达77分，均精准落于蓝色"性能前沿"虚线上。对比Qwen-2.5-7B/14B、Llama-3.1-8B、Gemma-2-9B等模型，它们需3-10倍FLOPs才能追平Moonlight-5.7T。

**技术结论**：Muon优化器使Moonlight以显著更低的训练算力即可达到GSM8k性能前沿，验证Muon在大模型训练中具备强可扩展性与算力效率。

**论文作用**：作为收尾性证据，将Muon从算法层面的收敛改进，落地为终端任务（数学推理）的算力-性能最优，强化"Muon可规模化"的核心主张。
*caption: 6.… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.9 (p.18)
![[assets/crops/muon-is-scalable-for-llm-training-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读（≤220字）：**

1) **结构与数据**：该图为7×27=189子图的网格矩阵，行对应7类注意力层权重矩阵（WC压缩K/V共享潜空间、WKC/WKR带/不带RoPE的K投影、WO输出投影、WQC/WQR带/不带RoPE的Q投影、WV值上投影），列对应L1–L27共27层。每子图含两条奇异值谱曲线——红为AdamW、蓝为Muon；红框标记Muon奇异值熵低于AdamW的层。

2) **关键结论**：Muon在大多数注意力矩阵上产出更陡峭、更集中（低熵）的奇异值谱——尤其WQC、WQR行几乎全层红框，WO行多数红框，WV行也有较多——表明Muon隐式正则化于低秩解，对查询/输出投影尤为明显。

3) **论文作用**：从谱结构视角解释Muon优于AdamW的内在机理，作为机制分析的核心证据嵌入论文"现象→原因→性能"的完整论证链。
*caption: Distribution of singular values for each weight matrix in the attention layers. We use WC to denote the weight matrices at each layer that compress th… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Muon is Scalable for LLM Training — Fig.10 (p.19)
![[assets/crops/muon-is-scalable-for-llm-training-fig10.png]]
> [!tip] 【图文联合解读】**1) 核心对象与结构**
图为 16×26 的网格热力可视化：行 = 4 个专家(E0–E3)各 × {WO, WI, WV} + 共享专家 SE 的三投影 + 路由器 RW，共 16 行；列 = L2–L27 共 26 层。每格两条排序奇异值衰减曲线，红=AdamW、蓝=Muon；红框标注 Muon 奇异值熵更低的格（图中约数十处，集中在 E0WO、E1WO、SEWO 等少数投影的浅层与末层）。

**2) 关键结论**
Muon 经 Newton–Schulz 正交化后，其训练得到的 FFN 权重矩阵奇异值谱整体更陡峭、低秩特征更显著，与 AdamW 产生系统性差异，且在不同专家/投影/层上差异并不均匀。

**3) 在论文中的作用**
作为机理证据，从权重内部谱结构层面解释 Muon 相对 AdamW 的损失/性能优势，与论文"Muon 可规模化训练 LLM"的核心主张形成实验-机理闭环。
*caption: Distribution of singular values for each weight matrix in the feed-forward network (FFN) layers. We use WI, WV and WO to denote the weight matrices in… ｜ 论文 [[muon-is-scalable-for-llm-training]] ｜ arxiv 见 MD 元信息*

### Attention Residuals — Fig.1 (p.1)
![[assets/crops/attention-residuals-fig01.png]]
> [!tip] 【图文联合解读】图示三种残差架构：(a)标准残差对Attention+MoE层均匀⊕累加；(b)Full AttnRes每层引入Q/K/V矩阵与α权重，选择性聚合全部前层L个输出；(c)Block AttnRes将层分组为N块，将每token内存由O(Ld)降至O(Nd)。该图论证：标准残差"一刀切"聚合存在局限，注意力残差以学到的α权重实现层间选择性信息路由，Block变体以分组粒度换取内存效率；为后续Table 1各方案内存访问成本对比与附录两阶段推理调度建立方法基础框架。
*caption: Overview of Attention Residuals. (a) Standard Residuals: standard residual connections with uniform additive accumulation. (b) Full AttnRes: each laye… ｜ 论文 [[attention-residuals]] ｜ arxiv 见 MD 元信息*

### Attention Residuals — Fig.3 (p.6)
![[assets/crops/attention-residuals-fig03.png]]
> [!tip] 【图文联合解读】**图3深度解读（≤220字）**

**核心对象与结构**：图示4物理Rank×2虚拟Stage的流水线通信布局。每Rank缓存已收块（`[b₀]`、`[b₀,b₁]`），阶段切换仅传增量块（`+[b₁,b₂]`、`+[b₂,b₃]`），斜纹框标记AttnRes块终点缓存位。

**论证的关键结论**：AttnRes通过缓存机制将跨阶段通信量从"全量历史重传"压缩为"增量块传输"，Rank 0→Rank 3每个Stage仅传递1–2个新增块，而非所有累积块，显著降低推理时流水线并行的通信开销。

**论文整体链路作用**：该图是AttnRes系统效率层面的核心可视化证据，与Table 3（AttnRes vs baseline性能对比）相互印证，共同支撑"块级残差缓存+增量通信=高效流水线推理"的方法论闭环，为后文分布式部署分析提供通信模型基础。
*caption: Cache-based pipeline communication example with 4 physical ranks and 2 virtual stages per rank, where hatched boxes denote end of AttnRes blocks. Numb… ｜ 论文 [[attention-residuals]] ｜ arxiv 见 MD 元信息*

### Attention Residuals — Fig.4 (p.9)
![[assets/crops/attention-residuals-fig04.png]]
> [!tip] 【图文联合解读】该图以双对数尺度展示三种模型的缩放定律拟合曲线：Baseline（蓝, 1.891×C⁻⁰·⁰⁵⁷）、Full AttnRes（红, 1.865×C⁻⁰·⁰⁵⁷）、Block AttnRes（橙, 1.870×C⁻⁰·⁰⁵⁸），x轴PFLOP/s-days 0.5–5+，y轴Loss≈1.7–1.95。两条AttnRes曲线全程低于Baseline，且衰减指数几乎一致（-0.057 vs -0.058），说明增益贯穿全尺度。图标注Loss≈1.8处Block AttnRes相对Baseline节省1.25×算力（同算力下Block达1.692 vs Baseline 1.714）。

作为方法核心主实验，该图定量证明AttnRes在任意规模均稳定有效，且Block变体以更低开销逼近Full收益，与表4消融共同支撑"残差路径改造普遍有效"这一论文核心结论。
*caption: Scaling law curves for Attention Residuals. Both Full and Block AttnRes consistently outperform the baseline across all scales. Block AttnRes closely … ｜ 论文 [[attention-residuals]] ｜ arxiv 见 MD 元信息*

### Attention Residuals — Fig.5 (p.10)
![[assets/crops/attention-residuals-fig05.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**(a) 验证损失**：Baseline（蓝）与 Block AttnRes（红）起始均约 1.47，训练全程走势一致，但 Block AttnRes 在 ~80k 步后加速下降，最终约 1.15，低于 Baseline 的 ~1.18，验证其优化更充分。

**(b) 块输出幅度**（0–27 层）：Baseline 在前 20 层维持在 ~1，但第 20 层后陡升至 ~12，呈末端激活爆炸；Block AttnRes 全程平稳在 0–2 区间，证明其有效抑制了深层信号膨胀。

**(c) 梯度幅度**（×10⁻⁵）：Baseline 梯度在第 0 层达 ~2.5 后单调衰减至近 0，呈现典型的梯度消失；Block AttnRes 全程维持在 0.1–0.7，分布显著更均衡。

**论证作用**：该图从"损失更低、激活更稳、梯度更匀"三方面，为 Block AttnRes 改善信号传播的理论主张提供直接经验证据；与 Table 5 中多种残差机制的横向梳理互补，构成论文方法验证链中的关键实证支撑。
*caption: Training dynamics of Baseline and Block AttnRes. (a) Validation loss during training. (b) Each transformer block’s output magnitude at the end of trai… ｜ 论文 [[attention-residuals]] ｜ arxiv 见 MD 元信息*

### Attention Residuals — Fig.6 (p.11)
![[assets/crops/attention-residuals-fig06.png]]
> [!tip] 【图文联合解读】**Figure 6 图文联合解读**

**核心对象与数据**：横轴为块大小 S∈{32,16,8,4,2}，纵轴为16层模型验证损失。红色实线 Block AttnRes 在五个 S 下的取值依次为 1.757、1.753、1.748、1.746、1.746；两条参考线：Baseline（灰虚线，1.766）与 Full AttnRes（红虚线，S=1，1.737）。

**技术结论**：块越小损失越低，S=32→4 单调下降共 0.011；在 S=4 处已收敛至 1.746，与 S=2 完全持平，说明进一步细化块无收益。Block AttnRes 即使在 S=32（1.757）也优于 Baseline（1.766），但始终未追平 Full AttnRes，最优差距约 0.009。

**论文作用**：作为 Table 4 消融的延伸，量化"块大小"这一实用超参的效率–性能权衡——S=4 即可获得 Full AttnRes 近 95% 的增益（1.746 vs 1.737），为部署中的块粗化选择提供实证依据。
*caption: Effect of block size on validation loss (16-layer model). • Language understanding and reasoning: MMLU [13], MMLU-Pro Hard [55], GPQA-Diamond [41], BB… ｜ 论文 [[attention-residuals]] ｜ arxiv 见 MD 元信息*

### Attention Residuals — Fig.7 (p.12)
![[assets/crops/attention-residuals-fig07.png]]
> [!tip] 【图文联合解读】**图7 联合解读**

图7呈现固定算力（≈6.5×10¹⁹ FLOPs、≈2.3×10⁸活跃参数）下，5×5的(d_model/L_b, H/L_b)架构网格验证损失热力图，分Baseline(a)与Attention Residuals(b)两组。Baseline最优在(60, 0.3)处，损失1.847；Attention Residuals最优在(45, 0.3)处，损失1.802，全网格均更优（最高值1.954→更低）。

论证结论：(1) 算力固定时，注意力残差相对Baseline普遍带来约0.03–0.05的损失下降；(2) 最优共同落于H/L_b=0.3，但AR所需d_model/L_b更小（45<60），说明残差机制提升了参数利用率；(3) 该图在论文中作为架构无关性证据，与主实验互补，支撑"残差设计独立带来增益"的核心论点，并为后续缩放实验的超参选择提供依据。
*caption: Architecture sweep under fixed compute (≈6.5 × 1019 FLOPs, ≈2.3 × 108 active parameters). Each cell reports validation loss for a (dmodel/Lb, H/Lb) co… ｜ 论文 [[attention-residuals]] ｜ arxiv 见 MD 元信息*

### Attention Residuals — Fig.8 (p.13)
![[assets/crops/attention-residuals-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图8为16层16头模型的逐层注意力权重热力图。上排（Full AttnRes）源空间为32×16、含斜纹屏蔽区，每层权重几乎全集中于最近邻的±1–2行，对角支配明显；下排（Block AttnRes）源压缩为8块索引，呈现清晰的块对角块状结构（块内权重≈0.8–0.9），仅末层向下一块轻微溢出。

作者借此论证：两种 Attention Residuals 均保持强对角/块对角主导，说明**局部路径仍是主通道**，远距离权重稀疏可控且无广泛弥散，从而验证"块级近似即可逼近全连接残差"的假设。

该图为论文方法链中的**经验证据支撑**：从微观权重分布角度解释为何 Block AttnRes 在几乎不损失建模能力的前提下，可大幅压缩通信开销，连接理论分析与后续实验结论。
*caption: Depth-wise attention weight distributions for a 16-head model with full (top) and block (bottom) Attention Residuals, averaged over tokens. The model … ｜ 论文 [[attention-residuals]] ｜ arxiv 见 MD 元信息*

### Attention Residuals — Fig.9 (p.15)
![[assets/crops/attention-residuals-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象**：L=4 的四种残差变体的深度混合矩阵 M。Highway 用标量门（γ、g），(m)HC 用 β⊤Aα 形式的矩阵-向量乘积；Full AttnRes 显示 φ(wₗ, kᵢ) 未归一化打分，按来源节点用蓝/橙/紫/绿背景分组；Block AttnRes(S=2) 将 4 层分两个源块，块内用 φ(w, k₁+k₂) 聚合。

2) **关键结论**：统一视角下，M 的每行表示层 l 对早期各层输出的混合权重；标准残差对应全 1 等权混合，Highway/(m)HC 引入标量或低秩门控，而 AttnRes 用基于当前 token 查询 (w) 与历史键 (k) 的 φ 分数实现**输入依赖、源感知**的深度路由，且 Block 版本在保证表达力的同时显著降低复杂度。

3) **论文作用**：作为方法论桥梁，将 AttnRes 纳入"深度混合矩阵"统一框架，与 Highway、mHC 对照，直观论证其作为**通用残差推广**的合理性与计算效率优势，为后续实验提供理论支撑。
*caption: Depth mixing matrices M for four residual variants (L=4; Block AttnRes uses block size S=2). Highway is shown with scalar gates for clarity. AttnRes p… ｜ 论文 [[attention-residuals]] ｜ arxiv 见 MD 元信息*

### Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperP — Fig.2 (p.23)
![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p23.png]]
> [!tip] I don't see a figure on this page—it consists entirely of body text (page 23 of a technical paper on FlowServe, covering DistFlow KV-transfer scheduling, heterogeneous prefill/decode deployment on Ascend NPUs, and the introduction to §5.2 "Disaggregated MoE-Attention").

The page does **reference** two figures, but they are not present on this page:
- **Figure 2** — referenced in the "Heterogeneous Prefill-Decode Deployment" paragraph for the cross-NPU KV-cache transfer path (Ascend 910B prefill ↔ Ascend 910C decode over RoCE/VPC via DistFlow).
- **Figures 18 and 19** — referenced at the very bottom of the page as illustrations of three new techniques for disaggregated MoE-Attention.

Because no figure or caption is actually rendered on the supplied image, I cannot describe its architecture/components/data flow or transcribe its caption verbatim. If you can share the page(s) containing Figure 2 or Figures 18/19, I'll provide the description and verbatim caption as requested.
*caption: FlowServe selects the appropriate DistFlow [10] backend based on the network fabric. For MLA models like DeepSeek and Kimi K2, both interconnects sati… ｜ 论文 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] ｜ arxiv 见 MD 元信息*

### Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperP — Fig.4 (p.8)
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示两NPU经XCCL分布式传输协议交互：每端含AIV核、DMA引擎、片上Unified Buffer（Ping-Pong双区）；外存分App Data（KV$）、Metadata（eventID/chunkID/TailPtr）、Managed Data（Ring含head/tail）。8步红箭头串联MTE2读→MTE3写→元数据轮询全流程。

论证：①MTE2/MTE3内存语义实现zero-copy传输；②Ping-Pong双区使步骤1/2并行，隐藏片间延迟；③元数据轮询替代CPU中断，降低kernel launch开销；④同时支持DMA引擎双路径。

作用：作为CloudMatrix384跨NPU集合通信（PD分离推理中KV cache transfer）的硬件原生机制，支撑高吞吐低延迟MoE推理服务。
*caption: Step 1: The sender’s serving engine invokes XCCL’s send, passing the source buffer in the app data area (e.g., KV cache), an eventID (e.g., number of … ｜ 论文 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] ｜ arxiv 见 MD 元信息*

### Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperP — Fig.8 (p.12)
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig08.png]]
> [!tip] 【图文联合解读】图8展示A2E与E2A两种MoE通信原语。结构：上方Attention NPU组（含NPU/DMA/AIV/Mem(data)），下方Expert组（Mem含meta+data），红色箭头标注5步流程。A2E以最左侧Expert为trampoline：①Attention下发meta，②AIV处理，③拉取data回Attention，④⑤跨Expert级联更新meta与data；E2A反向：Expert先横向汇聚，再经Attention端AIV回流meta与data。

论证关键：采用两阶段路由，以trampoline NPU解耦meta与data传输，避免Attention↔Expert直连开销；结合URMA绕过主机CPU直连DMA，降低MTE与DMA延迟权衡。

作用：是CloudMatrix384 MoE推理中dispatch/combine的核心通信原语，支撑大规模专家并行的可扩展调度。
*caption: Trade-off between MTE and DMA. To improve communication efficiency, we employ NPU-Direct Unified Remote Memory Access (URMA), a technique on Ascend NP… ｜ 论文 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] ｜ arxiv 见 MD 元信息*

### Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperP — Fig.10 (p.12)
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**核心对象与结构：** 该图展示 DeepSeek 单个 MoE 层在多 Die（Die 0–3 及 N–1/N）上的并行执行时间线，每 Die 依次执行 MLAPrologue（红）→ MLA（黄）→ All2All（绿）→ O → Gating 序列。关键视觉差异：(1) Die 0/1 的 MLA 块宽度明显大于 Die 2/3，量化呈现 MLA 延迟的 die 间差异；(2) 各 Die 的 All2All 被红色虚线垂直对齐，标示同步点；(3) Die 2/3 在 Gating 之后出现蓝色空白段，代表空闲等待。

**论证的技术结论：** 配合三种 Key Technique——① DP-LB 调度将不同 Die 的 MLA 延迟拉齐，避免 All2All 同步时的短板效应；② MLAPrologue 与 MLA 采用 TP=1 配合 All2All，避免 KV cache 重复；③ Proactive GC 回收 Gating 后空闲 Die 的 CPU 资源，消除 stragglers。

**论文作用：** 该图作为 FlowServe 推理架构中分布式 MoE 调度章节的标志性图示，直观串联"延迟变异—同步阻塞—资源闲置"三大痛点与其解决方案，是论文分布式执行优化的核心证据。
*caption: This redesign centers on three key components: • First, we introduce the Data Parallel (DP) group abstraction, inspired by SGLang [24].… ｜ 论文 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] ｜ arxiv 见 MD 元信息*

### Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperP — Fig.12 (p.16)
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig12.png]]
> [!tip] 【图文联合解读】图示FlowServe EPLB四阶段闭环：①两NPU Die内MLA→Gating→Collect采集Expert Stats；②EPLB算法基于token计数（如表中Expert 1承载Token3的510 tokens/step）决策冗余专家布局；③Expert Reconfig更新Logical-Physical Expert Map；④LB→Dispatch按新映射执行，支持DeepSeek模型最高288路专家并行。原文以"token数代理负载"统一表征通信与计算开销，论证可同时优化MoE-Dispatch均衡与计算均衡，构成论文MoE推理服务的核心调度链路。
*caption: Step 1: Collecting Expert Load Distribution. First, we collect data on expert loads across NPUs. We define expert load as the total number of tokens r… ｜ 论文 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] ｜ arxiv 见 MD 元信息*

### Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperP — Fig.17 (p.22)
![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig17.png]]
> [!tip] 【图文联合解读】**核心对象与结构：** 图示 M prefill × N decode 异构部署（示意各 3 组），含 Job Executor 全局调度器、Prefill/Decode 两侧 TE 集群，每 TE 为二级结构：TE Shell → DP（Master + 多 Executor）→ Generator + RTC-DistFlow，共 9 步箭头（1–9 及 8a/8b）刻画"JE 路由 → Prefill Shell → DP 内调度 → 跨 TE KV 直传 → Decode Shell → 重新生成"的端到端请求流。

**论证结论：** 证明解耦方案全互联可落地——RTC-DistFlow 实现低开销跨 TE KV cache 迁移，JE 统一弹性调度 M prefill/N decode 实例，达成资源解耦与负载均衡。

**论文作用：** 作为 CloudMatrix384 解耦推理架构的蓝图，衔接底层硬件拓扑与上层调度策略，为后续吞吐/延迟实验提供方法基线。
*caption: 1. A request first arrives at a randomly selected Job Executor (JE), which assigns it to a prefill… ｜ 论文 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.1 (p.2)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig01.png]]
> [!tip] 【图文联合解读】图中将“块1+块2+块3”的KV生成分为4种：①全量重算3块，最慢但质量高；②仅复用块1前缀缓存，重算块2–3；③全量复用3块KV、忽略跨块注意力，速度快但质量低；④CacheBlend全量复用，仅选择性重算少量KV，速度提升明显且质量良好。该图用于引出速度—质量权衡，并作为后续实验基线。
*caption: Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend’s selective KV recompute. full KV recompute (Figure 1(a)). Despite many o… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.2 (p.4)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig02.png]]
> [!tip] 【图文联合解读】图2双子图：Musique(a)与2WikiMQA(b)，横轴为输入相关chunks数(1–45/1–35)，纵轴F1-Score。对比Full KV recompute含跨块注意力(蓝实线)与Full KV reuse无跨块注意力(橙虚线)：Musique上蓝线从0.19升至0.32峰值(25块)后微降，橙线在5块处达0.23后持续下滑至0.16；2WikiMQA蓝峰0.31(30块)，趋势一致。

论文借此论证：检索chunks越多质量越高，但若无跨块注意力，单纯KV复用质量反随chunks数增加而下降。图内直接标注"跨块注意力增益"，是CacheBlend提出"选择性KV重算+跨块融合"方案的核心动机，为后续方法设计及效率/质量权衡实验提供立论基础。
*caption: Generation quality improves as more text chunks are retrieved. and fetch top-k relevant chunks from the database, based on the least L2 distance betwe… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.3 (p.4)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(c)展示"Full KV reuse"方案：两块预存的KV缓存（Chunk1、Chunk2）直接拼接Query送入LLM，不做任何重计算。输出示例显示，面对FIFA世界杯类查询，模型仅给出"梅西、C罗知名"等表面信息（红色❌），未能融合两chunk内容得出正确答案。

**原文结论**：完整复用KV虽省时，但忽略了chunk间的cross-attention，导致跨块信息无法交互，产生事实性错误。

**论文作用**：此图与图(b)"Full KV recompute"形成对比——前者慢而正确、后者快而错——共同揭示RAG场景中KV复用的核心矛盾（效率 vs 准确性），从而为CacheBlend提出"选择性KV重计算以恢复跨块注意力"的方法提供直接动机与问题定义。
*caption: An illustrative example of an LLM input with two text chunks prepended to a query. Full KV recompute (b), with- out reusing KV cache, is slow but give… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.4 (p.5)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig04.png]]
> [!tip] 【图文联合解读】**图4联合解读**

**核心对象**：图(a)上排左为26×26注意力矩阵，黄框（行15–25、列0–15）内有数个明显亮点，右侧17×45前向注意力呈清晰对角分布；图(b)同位置黄框完全空白，右侧前向注意力在列17附近出现异常纵向亮带，对角结构紊乱。

**技术结论**：完整KV重用因跳过文本块间cross-attention，导致前向注意力偏移、生成错误；完整KV重算注意力正确但开销大。两者前向注意力的差异即源于cross-attention的有无。

**论文作用**：以可视化对比证明"单纯复用缓存必丢精度"，从而为CacheBlend的核心思路——选择性重算部分层的KV以恢复chunk间cross-attention，同时保留缓存加速——提供直接动机与理论支撑。
*caption: Contrasting the attention matrices of (a) full KV recompute and (b) full KV reuse. The yellow boxes highlight the cross-attention. The right-hand side… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.5 (p.6)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig05.png]]
> [!tip] 【图文联合解读】图中为第 \(i\) 层的选择性重算：输入经 \(Q_i\) 与按 token 存储的 \(K_i\) 相乘生成注意力矩阵，再乘 \(V_i\)，得到第 \(i+1\) 层输入；图中明确标出仅重算 2 个 token 的 KV，而非整层 token。它说明 CacheBlend 在保留注意力知识融合效果的同时，以少量重算降低计算量和时延。该图是 RAG 缓存复用机制的结构示意，连接其性能与精度实验，并非结果数据图。
*caption: Illustrated contrast between (a) full KV recompute and (b) selective KV recompute on one layer. 0 10 20 30 40 50… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.6 (p.6)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig06.png]]
> [!tip] 【图文联合解读】**图6联合解读：**

**结构数据：** 三模型（Mistral-7B点线、Yi-34B虚线、Llama-70B实线）的前向注意力偏差随逐层KV重计算比例（0–50%）的衰减曲线。起始偏差约0.55–0.60，前5%内骤降至~0.20，随后缓慢收敛于0.10–0.15，三模型走势一致，Mistral-7B全程略低。

**技术结论：** 该图支撑CacheBlend核心论点——按HKVD分数仅重算少量token的KV即可大幅削减注意力偏差，且最陡降发生于最高KV偏差token处，验证"选择性部分重算"策略的合理性：以极小重算开销逼近全量重算精度。

**链路作用：** 它是论文"重算预算–精度权衡"实验的关键定量证据，为后续"仅重算~10% KV即可保持生成质量"的全栈优化结论提供底层理论支撑。
*caption: Attention deviation reduces as we recompute the KV of more tokens on each layer. Importantly, the biggest drop in attention deviation results from rec… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.7 (p.7)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图7以CDF形式刻画Mistral-7B（4/5/6层）、Yi-34B（10/11/12层）、Llama-70B（4/5/6层）相邻层间KV偏差的分布。三组曲线高度重合，绝大部分token的KV偏差集中在0–20以内（约90%分位数），三条曲线几乎完全重叠，说明跨相邻层的KV值变化极小、分布近似一致。

该图用以论证：**LLM各层KV缓存对最终输出贡献稳定，仅靠缓存拼接近似已足够**，无需逐token重算全部层。这正是CacheBlend"选择性少层重算+缓存融合"策略的实验依据——既然偏差小，少量层（如每16层中只重算1层）即可修正拼接误差，从而在RAG长上下文场景下实现KV缓存复用与加速推理，构成论文方法链路的关键支撑图。
*caption: Distribution of KV deviation of different tokens on one layer. 5 vs. 6 12 vs. 13 21 vs. 22 31 vs. 32… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.8 (p.7)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig08.png]]
> [!tip] 【图文联合解读】## 图文联合解读

**1) 核心对象与数据：** 该图展示三个模型（Mistral-7B、Yi-34B、Llama-70B）中，相邻层间每个 token 的 KV 偏差的 Spearman 秩相关系数。横轴为不同层对（如 5 vs. 6、12 vs. 13、31 vs. 32 等），纵轴 0–1.0。三组柱形均接近 1.0（≈0.97–1.00），且跨浅层、中层、深层层对均保持极高相关性。

**2) 关键论证结论：** 原文据此指出，HKVD（高 KV 偏差）token 在不同层并非独立，其分布在相邻层间高度一致；因此只需识别少数 token 即可在全层做选择性重算，避免逐层独立选取带来的额外开销。

**3) 在方法中的作用：** 该图为 CacheBlend 的"选择性 KV 重计算 + 缓存融合"策略提供统计依据——HKVD 的层间相关性正是该策略得以在保证生成质量前提下大幅降低重算量的核心前提。
*caption: Rank correlation of the KV deviation per token be- tween two consecutive layers. expensive and defeats the purpose of selective KV recom- pute. Instea… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.9 (p.7)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig09.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图9展示CacheBlend逐层HKVD（高KV偏差）token的级联筛选机制。结构上：每层对"Updated KV"与"Precomputed KV"做KV偏差计算（柱状图），筛出HKVD tokens。Layer 1全量重算以建立初始HKVD集合，Layer 2仅在前层HKVD子集内重算3个token并再次筛选，后续层继续级联。浅色格代表Re-used，深色代表Re-computed。

原文借此论证：层间级联选择使重算规模逐层收敛至极少数token，被复用缓存的偏差仍受控，从而兼顾精度与速度。该机制是CacheBlend在RAG长上下文场景下"高比例缓存复用+极少增量重算"这一核心加速方案的关键环节，使预填充计算量显著降低而生成质量几乎无损。
*caption: CacheBlend selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.10 (p.8)
![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]
> [!tip] ## Figure 10 Description

**Figure 10** illustrates two design choices in CacheBlend's loading controller, presented as two panels:

**Panel (a) – Recompute ratio:** Line plot of Prefill delay (TTFT, y-axis) vs. Re-compute ratio %, x-axis 0–50). A dashed line ("w/o pipelining") rises steeply from ~1 to ~3.5s; a solid line ("w. pipelining") stays nearly flat, rising only slightly from ~1 to ~2s. An annotation marks 26.8% as the optimal ratio for a 1 GB/s SSD where no extra delay is introduced.

**Panel (b) – Storage device choice:** Bar chart comparing Prefill delay across GPU, CPU RAM, SSD (32 Gbps), and SSD (4 Gbps), with hatched bars for w/o pipelining and solid bars for w. pipelining. The annotation identifies the cheapest device (CPU RAM) that introduces no extra delay under a 15% recompute ratio.

## Key Technical Takeaway (≤120 words)

CacheBlend exploits **pipelining of KV loading and selective recomputation** so that, as long as the recompute delay T_recompute remains ≤ the KV-loading delay T_load, the recomputation is "hidden" and TTFT is not penalized. This lets the controller decouple quality from latency: (1) pick the smallest recompute ratio r* whose quality drop is negligible (empirically ~15%), then (2) select the cheapest storage device whose T_load ≥ T_recompute. Result: KV caches can be stored on slower, cheaper media (e.g., CPU RAM or 32 Gbps SSD instead of GPU HBM) without increasing TTFT, cutting cost while preserving inference quality.

## Caption (verbatim)

**Figure 10.** *(a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay.*
*caption: (a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increas… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.11 (p.9)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig11.png]]
> [!tip] 【图文联合解读】**1) 图示核心对象与结构**
展示CacheBlend处理单条RAG请求的完整6步流程：用户提问"Can we use drones in agriculture?"→①Loading Controller(★)→②抓取4个文本块(Drone Chunk#1/#2、Agri Chunk#1/#2)→③写入三层KV Cache Store(CPU/SSD/慢盘)→④读出KV Cache #1-4并触发KV Cache Fusor(★)→⑤产出Fused KV Cache→⑥返回回复"Drones can…"并回写Potential New KV Cache。

**2) 原文论证的关键技术结论**
验证CacheBlend两大核心组件——**Loading Controller**负责调度检索文本与缓存I/O，**KV Cache Fusor**对各块复用缓存做选择性重算融合，得到全局一致的Fused KV Cache，从而避免全量重计算并保证语义正确性；同时预计算新缓存回写，为后续请求复用。

**3) 在论文方法链路中的作用**
作为系统级架构总览图，承上(缓存复用动机)启下(选择性重算、融合策略及端到端性能实验)，为读者建立"控制器+融合器+分层存储"的整体设计心智模型。
*caption: CacheBlend system (green stared) in light of LLM context augmented generation for a single request. CacheBlend uses text provided by the retriever, in… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.12 (p.10)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig12.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以4×3散点矩阵展示**TTFT（横轴）vs生成质量（纵轴，F1/RougeL）**权衡：四行为2WikiMQA、MusiQue、SAMSum、MultiNews四个RAG数据集，三列为Mistral-7B、Yi-34B、Llama-70B三种模型，对比CacheBlend、全KV复用、前缀缓存、全KV重算四种策略。

**关键结论**：CacheBlend（红方块）在所有12组实验中均显著左移于全KV重算（如Llama-70B的2WikiMQA上TTFT由~3s降至~1s），TTFT加速达2.2–3.3×；同时其质量点几乎与全KV重算重合，验证"质量损失可忽略"。全KV复用虽最快但质量严重塌陷（点远低于红线），前缀缓存则仍偏慢。

**论文作用**：作为主实验结果，直观证明CacheBlend在Pareto前沿上兼顾速度与质量，是RAG多文档缓存融合方案的有效性核心证据。
*caption: CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligible quality drop across four datasets and three models.… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.13 (p.10)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig13.png]]
> [!tip] 【图文联合解读】图13在四个数据集（2WikiMQA、Musique用F1-Score；SAMSum、MultiNews用RougeL）上以TTFT(s)为横轴、质量为纵轴散点对比CacheBlend（红方块）、MapReduce（绿星）、MapRerank（紫十字），箭头指向左上代表"更优"。前三个数据集上CacheBlend得分约0.32–0.37，均高于MapReduce且TTFT减半（约0.7–0.8s vs 1.7–3.1s）；MultiNews上CacheBlend略低（0.16 vs 0.20）但仍更快。MapRerank虽TTFT最低，质量却明显劣化。该图论证"缓存融合能在保持生成质量的同时大幅降低首token延迟"，是论文核心实验结论之一，证明CacheBlend在RAG长上下文场景下兼顾速度与质量，是方法链路中最终落地收益的关键支撑图。
*caption: Generation quality of CacheBlend with Yi-34B vs MapReduce and MapRerank. 7… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.14 (p.11)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig14.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**：Figure 14 为 2×3 网格，横轴为每秒平均请求速率（吞吐量），纵轴为 TTFT（首 token 延迟，秒）；列分别为 Mistral-7B、Yi-34B、Llama-70B 三种模型，行分别为 2WikiMQA 与 Musique 扩展数据集。比较 CacheBlend（红方块）、Full KV 重算（蓝三角）、Prefix Caching RAM（浅蓝圆点）与 RAM+SSD（绿菱形）四种策略。

**2) 关键结论**：在两数据集与三模型下，CacheBlend 曲线始终位于右下——例如 Llama-70B 上请求率达 ~0.85/s 时 TTFT 约 7s，而 Full KV recompute 仅 ~0.2/s 即超 8s；Mistral-7B 上 CacheBlend 可承载 ~4 req/s 时 TTFT 仍 <2s，基线在 1 req/s 前已劣化。即"相似质量下更低 TTFT、更高吞吐"。

**3) 论文链路作用**：作为端到端服务性能图，是方法有效性的总验证——把"KV cache 融合"的微观机制（Fig 5–9）落到 RAG 服务宏观指标（延迟-吞吐曲线），支撑 §6 性能评估核心结论。
*caption: CacheBlend achieves lower TTFT with higher throughput in RAG scenarios compared with baselines of similar quality. 3 6 9 12 (a) Number of chunks… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.15 (p.11)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig15.png]]
> [!tip] 【图文联合解读】图1×3折线图量化对比CacheFuse与Full KV重算的TTFT：(a)块数3→12，前者由~0.05s缓升至~0.25s，后者从~0.25s飙升至~1.2s；(b)块长300→900，前者稳定于0.15–0.3s，后者达~1.45s；(c)批大小2→10，前者0.2→1.6s，后者从~0.7s急升至~7.8s。原文借此论证CacheFuse在RAG不同配置下TTFT均显著低于基线，且差距随规模扩大。在论文中作为Figure 14的补充消融，验证方法对块数、长度、批大小等关键超参的鲁棒性，强化"缓存融合可显著降低首token时延"的核心结论。
*caption: CacheBlend outperforms baseline with varying chunk numbers, chunk lengths, and batch sizes. • SAMSum [25]: This dataset comprises multiple pairs of di… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.16 (p.8)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig16.png]]
> [!tip] 【图文联合解读】**图16解读：**

**1) 核心对象与数据：** 图16在Yi-34B模型上对比四种方法于2WikiMQA、Musique、SAMSum、MultiNews四个数据集的生成质量（F1或RougeL）随重算比（Re-compute Ratio）的变化。CacheBlend（红线方块）集中在5%–18%重算区间，质量约0.30–0.38 F1 / ~0.18 RougeL，几乎贴合Full KV recompute（蓝三角，~100%重算）；Full KV reuse（橙×，0%重算）质量骤降至0.15–0.18；Prefix Caching（蓝圆）同样需近100%重算。

**2) 关键结论：** 5%–18%的选择性重算即可逼近全量KV重算的质量，最小必要重算量即构成系统延迟下界。

**3) 在论文中的作用：** 在整体实验链路中提供"质量等价性"关键证据，支撑CacheBlend以极小重算开销替代Prefix Caching全量重算、从而实现RAG推理加速的核心论点。
*caption: This means that even if the storage device is a fast device (ex. CPU RAM), the delay will be lower-bounded by the minimal recomputation to guarantee q… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CacheBlend: Fast Large Language Model Serving for RAG with C — Fig.17 (p.12)
![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig17.png]]
> [!tip] 【图文联合解读】**Figure 17 图文联合解读**

该图以两个散点图（CPU RAM、Slower Disk 4Gbps）对比四种方法，横轴为 TTFT（首 token 延迟，秒），纵轴为 F1-Score：CacheBlend（红方）、Full KV Reuse（橙×）、Prefix Caching（蓝圆）、Full Recomp（蓝三角）。

**关键数据**：RAM 下 CacheBlend TTFT≈0.6s、F1≈0.32；Prefix Caching 与 Full Recomp TTFT 2.0–2.4s、F1≈0.32；Full KV Reuse TTFT 0.2s 但 F1 仅 0.15。慢盘场景下 CacheBlend TTFT≈1.3s、F1≈0.32，仍低于 Prefix Caching/Full Recomp 的 2.0s。

**技术结论**：CacheBlend 在与重计算相当的 F1 下，TTFT 显著降低，构成 Pareto 最优，验证即便 KV 缓存存于较慢存储，仍能兼顾速度与生成质量。

**论文作用**：此图为实验链路中存储介质敏感性实验，支撑"KV 复用+部分重算"机制在不同硬件条件下的鲁棒性结论。
*caption: CacheBlend’s outperforms baselines when using RAM and slower disks… ｜ 论文 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.1 (p.3)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

该图以三栏流水线形式展示数据采集全流程：

1. **第一栏（蓝色）**：从 torch/transformers 库中爬取种子算子，产出 matmul、relu、conv2d 三类基础算子，构建"计算原语库"。

2. **第二栏（绿色）**：以 LLM 为"组合器"，将 conv2d、relu、matmul 等单一算子自动合成融合任务（fused op：conv2d → relu → matmul）。

3. **第三栏（白色）**：基于四项 rubric 过滤——可执行（Executable ✓）、确定性（Non-random ✓）、合理负载（Reasonable Workload ✓）、非平凡（Non-trivial ✓），并约束数据类型一致（如 fp16）。

**论证结论**：原文借此说明其训练数据并非随机拼凑，而是通过"原始算子→LLM 合成→rubric 筛选"的链式质控，保证题目可编译、可复现且具训练价值。

**在论文中的作用**：作为整体方法链路的"数据底座"，直接服务于后续 Agentic RL 的 CUDA kernel 生成与高效评测，是论文区别于现有工作（如 KernelBench）的关键数据工程创新。
*caption: Overview of the three-stage data collection pipeline. We first crawl seed operators from PyTorch… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.2 (p.4)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图2展示CUDA Agent的闭环工作流：(1) 输入侧含 `SKILL.md` 系统提示（PyTorch+CUDA专家角色）与 `Workdir`（kernels/、model.py、binding.cpp、utils/含verify与profile脚本）；(2) 中间CUDA Agent生成 `kernel.cu`、`kernel_binding.cpp`、`model_new.py`；(3) GPU Pool执行并反馈四类指标——Correctness、Generated Time 1.26ms、Torch Eager Time 2.30ms、Compile Time 1.80ms。该图定义了训练/评估闭环，将生成→编译→正确性验证→性能基准串成单步RL轨迹。Table 2消融实验据此验证"agent loop"为关键组件，移除后性能显著下降，印证其作为方法链基础设施的必要性。
*caption: Overview of the agent loop.… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.3 (p.5)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示Agentic RL阶段的核心架构：Actor Model（绿）与Critic Model（蓝）均由RL预热后采样的轨迹分别初始化；Critic Model额外经Value Training训练，二者通过PPO算法连接并最终生成CUDA Agent。原文以此论证：(1)采用"单轮RL预热→轨迹采样→初始化actor-critic"的两阶段训练策略，保证agentic RL的稳定冷启动；(2)以PPO为框架的actor-critic结构是大规模CUDA内核生成agentic RL的关键设计。该图是论文整体方法链路的核心枢纽，串联起轨迹生成、奖励调度与最终高性能CUDA智能体训练的全流程。
*caption: Overview of training pipeline. Following a single-turn RL warm-up stage, the sampled trajectories are… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.4 (p.10)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(a) Training Reward与(b) Actor Entropy对比PPO w/ RFT（橙）与w/o RFT（绿）在约30步训练中的表现。定量看：含RFT时奖励稳步升至1.9–2.0，熵平稳于~0.07；去除RFT时奖励在步16达峰~1.75后骤降至0，熵由~0.07飙升至~0.13后训练崩溃。该图论证RFT是防止策略弥散、维持训练稳定的关键模块——无RFT时策略变得弥散且结构不良。它与Figure 5（Value Pretrain消融）共同构成稳定性消融实验，验证CUDA Agent PPO训练框架中两项必要设计，支撑整体RL管线可靠性的论证。
*caption: Ablation: RFT. Removing RFT causes training reward to collapse. The concurrent increase in actor entropy… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.5 (p.10)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig05.png]]
> [!tip] 【图文联合解读】图5双子图横轴均为训练步数（0–30）。(a) 价值函数解释方差EV：PPO w/ Value Pretrain（橙）全程平稳≈0；w/o（绿）剧烈波动，最低≈-8，约10步即崩溃终止。(b) 响应长度截断比：带预训练者恒为0；不带者约10步内飙升至0.25后训练中断。

技术结论：Value Pretraining使critic学到有意义的价值函数（高EV），为策略提供稳定梯度信号；缺失时价值估计失效，探索失控，交互轨迹过长触发截断，训练发散。

论文作用：在CUDA Agent的PPO-RL训练链路中，与Fig.4（RFT消融）互补，共同论证"价值预训练"与"拒绝采样微调"是大规模RL稳定收敛的必要前提。
*caption: Ablation: Value Pretraining. Without Value Pretraining, the critic fails to learn a meaningful value… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.6 (p.13)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图(b)展示训练数据中的"组合型Torch算子类"`Model`：在`forward`中依次执行`Softmax(dim=1)`→`ConvTranspose2d`(3→16通道，k=3，s=2，p=1)→可学习`bias`相加；输入张量形状为`[512, 3, 32, 32]`。它表明训练算子并非单原子操作，而是由softmax+转置卷积+偏置融合而成的复合算子类，由此扩展了可优化算子空间的组合深度与多样性，为agent生成长程、融合式CUDA kernel提供更贴近真实工作负载的训练目标，支撑大规模RL对复杂算子的端到端优化能力验证。
*caption: Examples of operator classes in our training data.… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.7 (p.13)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig07.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1) **核心对象**：直方图展示训练样本与全部评估样本间的最大AST相似度分布。横轴范围0–0.45，纵轴占比0%–12%；峰值约12%出现在相似度≈0.30处，整体集中于0.15–0.45区间，极低相似度(<0.10)样本几乎为零；右上角虚线"t"标记约0.42的阈值位置。

2) **关键结论**：训练集与评估集存在中等程度的代码结构重叠，既非高度雷同（避免数据泄露/记忆式刷分），也非完全无关（保证任务可迁移），由此佐证评估结果的有效性与公平性。

3) **链路作用**：作为前置数据审计环节，用于在RL训练前排除与评测题高度相似的训练样本，防止策略过拟合到已知解，确保后续KernelBench等基准上的性能提升来自真正的泛化能力。
*caption: Distribution of the maximum AST similarity between each training sample and all evaluation samples.… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.8 (p.22)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig08.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图8展示的是 PyTorch 风格的参考算子代码（Case D.2）。核心对象为 `Model` 类，其 `forward(self, A, B)` 执行 `torch.diag(A) @ B`：将 1D 向量 A（N=4096）构造为对角矩阵，与 2D 矩阵 B（4096×4096）做矩阵乘，得到 (N, M) 结果。`get_inputs()` 用 `torch.rand` 生成 A、B 作为测试输入，`get_init_inputs()` 为空。

该代码作为**真值参考算子（reference operator）**，用于在 CUDA 内核生成流水线中：(1) 让 agent 生成的 CUDA kernel 与 `torch.diag(A)@B` 逐元素对比以验证正确性；(2) 提供真实计算语义供 RL 奖励/性能基准对照。它在论文方法链路中扮演 ground-truth 角色，确保 agent 在 KernelBench 类基准上学习"对角矩阵×稠密矩阵"这一特定算子的最优 CUDA 实现。
*caption: Reference operator for diagonal matmul (Case D.2).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.9 (p.23)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig09.png]]
> [!tip] 【图文联合解读】图9为Case D.2对角矩阵乘的CUDA实现。Kernel采用1D grid-stride循环，每个线程由`row=idx/4096`得行号后执行`output[idx]=A[row]*B[idx]`，覆盖4096×4096=16M元素；launcher启动1024 blocks×128 threads。

关键论证：代码未物化稠密对角矩阵，而是将A作为1D向量(N=4096)按行复用索引，直接产出完整N×M输出——证明RL agent能识别对角稀疏结构并做针对性优化，而非套用通用matmul模板。

论文作用：作为定性案例之一，与其他case共同支撑"agent生成的kernel具备问题感知优化"的核心论点，区别于通用PyTorch基线，验证agentic RL在大规模kernel生成中的实际价值。
*caption: Diagonal matmul kernel implementation (Case D.2).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.10 (p.23)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig10.png]]
> [!tip] 【图文联合解读】**图文联合解读（Figure 10，Case D.2）：**

1）图中展示 `ModelNew` 的 Python 封装：继承 `nn.Module`，仅含 `__init__` 与 `forward(A, B)`，`A` 为 1D 向量 `shape (N,)`，`B` 为 2D 张量 `(N, M)`，逻辑即 `C[i,j] = A[i] * B[i,j]`；前向直接转发至 `cuda_extension.diagonal_multiply_forward(A, B)`，返回 `(N, M)` 结果，自身不含任何计算或对角矩阵构造。

2）原文借此论证"结构化算子"无需物化稠密对角阵：CUDA 端以 **1024 blocks × 128 threads** 启动，线程在 `output` 上做 grid-stride 循环，由 `row = idx / 4096` 反推行号，复用 `A[row]` 一次性广播至该行全部 M 列，仅一次访存完成行级标量–向量乘。

3）在论文链路中，它是 CUDA-Agent 生成的"自定义算子 wrapper + 高性能 kernel"协同范式的代表样例，用以证明 agent 能将高层 PyTorch 算子等价改写为稀疏/结构化语义的高效 GPU 实现，是端到端编译–执行评估 (Case D.2) 的关键验证。
*caption: Custom operator for diagonal matmul (Case D.2).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.11 (p.25)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig11.png]]
> [!tip] 【图文联合解读】图11展示Case D.3的PyTorch参考算子（共31行代码）：输入x形状(batch_size,input_size)=(1024,8192)，可学习权重矩阵(hidden_size,input_size)=(8192,8192)；forward依次执行torch.matmul转置乘法（GEMM）→x/2（Divide）→torch.sum(dim=1,keepdim=True)（Sum）→×scaling_factor=1.5（Scaling），输出(batch_size,1)=(1024,1)。

该图作为正确性基准真值，用以论证CUDA-Agent能将包含**GEMM矩阵乘、elementwise除、reduction求和、标量缩放**四类异构算子复合的PyTorch模型，自动转译为结果正确且高性能的自定义CUDA kernel。它构成附录D案例集中的关键实证，体现agentic RL方法对多类算子融合调度的综合能力，是论文"参考算子→生成CUDA内核→正确性+性能评测"实验链路中标准答案的角色。
*caption: Reference operator for matrix multiplication, division, summation, and scaling (Case D.3).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.12 (p.26)
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p26.png]]
> [!tip] **Architecture / Components / Data Flow**

The figure shows a two-stage fused CUDA implementation (`fused_sum_dot_launcher`) for an input_size × hidden_size matrix operation (8192 × 8192):

1. **Stage 1 — `sum_weight_kernel`**: 1 thread per input column; loops over the hidden dimension, accumulating column sums of the `weight` matrix into `sum_weight[8192]`. Launched with ⌈8192/128⌉ blocks × 128 threads.
2. **Stage 2 — `dot_product_kernel`**: 1024 blocks × 128 threads, each thread performs a **float4-vectorized** dot product of `x` against `sum_weight` (4 multiply-adds per load), writes to shared memory, then performs a **log₂(128) tree reduction** in `smem`. Thread 0 emits `output[block] = smem[0] · (scaling_factor / 2.0f)`.

**Key Technical Takeaway** — The fusion reduces the O(8192²) matrix–vector work to O(8192·1024) by pre-summing the weight columns on-GPU; combined with `float4` coalesced loads and in-block shared-memory reduction, this minimizes global-memory traffic and eliminates an intermediate host-visible reduction step.

**Caption (verbatim):**
Figure 12: Fused sum-then-dot-product kernel implementation (Case D.3).
*caption: Fused sum-then-dot-product kernel implementation (Case D.3).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.13 (p.27)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig13.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图13展示`ModelNew`自定义算子类（22行代码），将原本独立的**矩阵乘法、除法、求和与缩放**四类操作融合，通过单次`cuda_extension.fused_sum_dot`调用替代多条PyTorch逐op链。`__init__`声明weight参数与scaling_factor，`forward`仅返回融合输出，体现**算子融合 + 自定义CUDA扩展**的端到端可集成形态。

论文借此论证：在D.3案例中，Agent能够生成超越torch原生接口的**fused custom operator**，将多类element-wise/reduction操作合一，直接通过PyTorch `nn.Module`对外暴露，验证了agentic RL在生成可编译、可调用的高性能CUDA算子方面的泛化能力，为"算子级优化取代逐op调度"提供落地证据。
*caption: Custom operator for matrix multiplication, division, summation, and scaling (Case D.3).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.14 (p.28)
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p28.png]]
> [!tip] **Description:**

The figure presents a PyTorch implementation of a ResNet BasicBlock reference operator. The `Model` class (with `expansion=1`) is initialized with `in_channels`, `out_channels`, and `stride=1`. Its architecture comprises two sequential 3×3 convolutions (`conv1`, `conv2`) each followed by BatchNorm2d (`bn1`, `bn2`), with a ReLU activation after the first BN. A `downsample` Sequential (1×1 conv + BN) adjusts dimensions when stride ≠ 1. **Data flow:** input → conv1→bn1→ReLU → conv2→bn2 → add identity shortcut (downsampled if needed) → ReLU → output. Test code uses `in_channels=3, out_channels=64, stride=1, batch_size=10` on 224×224 tensors.

**Key takeaway:** The skip connection enables gradient flow by adding the (optionally downsampled) input to the convolved output before the final ReLU — the defining feature of residual learning.

**Caption (verbatim):**

Figure 14 Reference operator for Resnet BasicBlock (Case D.4).
*caption: Reference operator for Resnet BasicBlock (Case D.4).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.17 (p.30)
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig17.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图示为 Case D.4 的 CUDA 融合 add-ReLU 内核源码（共 33 行）。核心结构：`block_size=256`，`grid_size` 上限 4096，采用**网格步进循环（grid-stride loop）**；主体通过 `reinterpret_cast<float4*>` 做 **向量化 4 元素批量访存**，每元素执行 `fmax(v1+v2, 0.0f)`，尾部用标量循环补齐非 4 对齐元素。

论文用它论证的关键结论：经过 RL 训练的 agent 能自主产出**融合访存（向量化 float4）+ 激活融合**的高质量优化内核，体现"显存带宽受限算子 → 单次访存完成 add+ReLU"的优化能力，是验证 agent 在 end-to-end 编译、SIMD 化与尾部处理等工程细节上达到人类专家水平的关键案例。
*caption: Fused add-relu kernel implementation (Case D.4).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA — Fig.18 (p.31)
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p31.png]]
> [!tip] ## Description

**Architecture / Components**
The figure shows a `ModelNew` (PyTorch `nn.Module`) implementing a fused ResNet BasicBlock for inference:
- Two 3×3 conv layers (`conv1`, `conv2`) plus an optional 1×1 `downsample` conv
- Three matching BatchNorm2d modules (`bn1`, `bn2`, `downsample[1]`)
- A custom CUDA extension providing `conv_forwardd` (conv + optional ReLU) and `fused_add_relu_forward` (add + ReLU)

**Data flow (`forward`)**
1. Enable TF32 for matmul/conv
2. Save `identity = x` (skip branch)
3. Fold `bn1` into `conv1` weights/bias → call custom conv (stride, padding, dilation, ReLU=True)
4. Fold `bn2` into `conv2` → call custom conv (ReLU=False)
5. If downsample ≠ None, fold its BN and apply to `identity`
6. `fused_add_relu_forward(out, identity)`
7. Disable TF32; return `out`

**Key technical takeaway (≤120 words):**
The block performs inference-time **BN-folding**, absorbing each BatchNorm's γ/β/mean/var into the preceding Conv's weight and bias (`γ·W/√(var+ε)`, `β − μ·γ/√(var+ε)`). This lets the entire residual block — conv, BN, skip-add, and ReLU — collapse into just **two custom CUDA calls** (`conv_forwardd`, `fused_add_relu_forward`) per branch. The result is a single fused kernel that eliminates intermediate tensor materialization, cuts kernel-launch overhead, and keeps TF32 precision scoped only to the convolutions themselves. (~90 words)

**Caption (verbatim):**
Figure 18. Custom operator for Resnet BasicBlock (Case D.4).
*caption: Custom operator for Resnet BasicBlock (Case D.4).… ｜ 论文 [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ｜ arxiv 见 MD 元信息*

### Single-Rollout Asynchronous Optimization for Agentic Reinfor — Fig.1 (p.1)
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig01.png]]
> [!tip] 【图文联合解读】**图1联合解读**

该图为柱状图，对比SAO（深蓝）、GRPO（浅蓝）与基线（白）在多基准上的得分。可读取的量化结果：MMT Nov 2025上SAO达**88.3**，较GRPO（76.0）提升**12.3**分；IMO Answer Bench上SAO为**55.8**，超出基线53.3；SWE-Bench Verified上SAO得**29.8**，较GRPO（27.0）和基线（23.0）分别提升**2.8**与**6.8**分。

原文借此论证核心结论——SAO在四个推理基准与一个编码基准（共五项）上**全面稳定超越**GRPO与Qwen3-30B-A3B SFT基线，是支撑"单次rollout异步优化策略优于传统同步GRPO"主张的**首要经验证据**。

该图作为论文首页Figure 1，奠定整篇实验链路的基调——先以宏观性能对比建立方法有效性，再逐项剖析机制（异步、效率、单rollout假设），形成"结果先行、机理跟进"的论证结构。
*caption: The performance of SAO on reasoning and coding benchmarks. The four reasoning benchmarks are evaluated in a reasoning-with-Python-tool setting, where … ｜ 论文 [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Single-Rollout Asynchronous Optimization for Agentic Reinfor — Fig.2 (p.3)
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：图分两行对比。上行（SAO）：编号 7、9（及 8）三条轨迹**逐条独立**送入 Training 模块，参数 π_θ 与 π_rollout 通过反向箭头同步迭代；下行（GRPO）：编号 3→2→1 的轨迹必须**积攒为一组**后整体送入 Training。右侧附两幅相同的 Trust Region 图，以横轴 A、纵轴 π_θ / π_rollout 给出上下界 1+ε_h 与 1-ε_l 围成的灰色安全区域，表明两方法均受同一信任域约束。

2）**关键技术结论**：SAO 单轨迹一完成即可训练（"ready for training"），无需等齐整组，从而消除 GRPO 中因等待最慢样本造成的 GPU 气泡；同步保证新旧策略比仍在 1±ε 信任域内。

3）**论文链路作用**：该图是方法概述的总锚点，承上启下——直观展示 SAO 把同步组训练拆解为异步流水线，启下各节中"Rollout–Train 交叠""资源利用率/吞吐提升""信任域约束保持"等分析与实验的对比基准。
*caption: Overview of SAO with single rollout design. The numbers denote the generation order of trajectories. For SAO, each trajectory becomes available for tr… ｜ 论文 [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Single-Rollout Asynchronous Optimization for Agentic Reinfor — Fig.3 (p.6)
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图3以Qwen3-30B-A3B为基模型，在AIME 2025与Beyond（AIME之外）两个数学基准上，对SAO、GRPO(w/ DIS)与Vanilla GRPO三条曲线进行了约1000步训练的准确率对比。**量化结果**显示：在AIME 2025上，SAO最终达到约95%，GRPO(w/ DIS)约92%；在Beyond基准上，SAO约70%，GRPO(w/ DIS)约65–67%；Vanilla GRPO在约150步后骤降至约73%并迅速崩溃退出。

**技术结论**：图中SAO曲线在两个基准的训练全程几乎全程位于GRPO(w/ DIS)之上，直观支撑原文"SAO almost consistently outperforms the optimized GRPO"的核心论断；同时Vanilla GRPO的早崩反衬出DIS稳定化与单rollout异步策略的必要性。

**作用定位**：作为论文的主对比实验图，它在方法/实验链路中扮演关键验证角色——将提出的SAO与经改进的强基线GRPO并列训练，是证明"单rollout+异步优化"在智能体RL中相对主流GRPO具有稳定性与性能双重优势的核心证据。
*caption: Performance comparison between SAO and GRPO (w/ DIS) during training. It can be observed that SAO almost consistently outperforms the optimized GRPO d… ｜ 论文 [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Single-Rollout Asynchronous Optimization for Agentic Reinfor — Fig.4 (p.7)
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig04.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图4(b)(c)分别展示SAO训练动力学的两项关键诊断。**(b)** 为 Critic Gradient Norm 曲线，上方"SAO w/o Frozen attention"（全参数优化）在~500步后梯度飙升至约10且持续增长；下方 SAO（冻结注意力）稳定保持在4–5，证明冻结注意力对价值网络训练的正则化必要性。**(c)** 为 Token-level Clip Ratio，紫色 SAO 曲线在~500步附近出现峰值约0.006，蓝色 vanilla VAPO（无DIS）全程趋近于0，说明 DIS 机制允许更积极的策略更新并触发裁剪。两图共同支撑论文核心论断：异步单次rollout需配合**冻结注意力价值训练**与**DIS解耦裁剪**两项设计，二者协同保证异步架构下 critic 稳定与 policy 高效探索，是 SAO 优于串行VAPO的实验证据基础。
*caption: Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for SAO and a single-critic-update baseline. (b) Critic gradient norm duri… ｜ 论文 [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Single-Rollout Asynchronous Optimization for Agentic Reinfor — Fig.5 (p.9)
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig05.png]]
> [!tip] 【图文联合解读】图示训练步数(0–430)与奖励(0–0.75)曲线，对比SAO(深蓝)与Running Mean基线(浅蓝)在单rollout在线学习下的表现。两处灰色阴影区(步150–170、290–310)代表风格奖励切换：SAO峰值约0.70–0.75，切换后迅速回升；Running Mean则适应滞后明显，稳态性能偏低(约0.45–0.60)。

该图论证在非平稳偏好下，SAO相比运行均值优势估计具备更快适应速度与更高稳态奖励，凸显其对偏好漂移的鲁棒性。

在实验链路中，此图作为消融对比，验证SAO相对传统优势估计的必要性，为单rollout异步优化方法的核心论点提供关键实证。
*caption: Online learning simulation under changing writing-style preferences. 5… ｜ 论文 [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### Single-Rollout Asynchronous Optimization for Agentic Reinfor — Fig.6 (p.13)
![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig06.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

图中横轴为训练步数（部分截断），纵轴为Reward（范围约0.42–0.54），对比三条曲线：SAO（token-level，浅蓝）、Step-level(Average)（紫）、Step-level(Last-Token)（深蓝）。训练起点三者均约0.44–0.45，中段曲线交织；最终SAO升至约0.47，明显高于Step-level(Average)的~0.44与Step-level(Last-Token)的~0.45。

原文借此论证：**在单次rollout异步优化框架下，采用token级优势估计（即SAO）比step级聚合（Average/Last-Token）能获得更高的训练奖励**，验证token级细粒度信用分配在agentic RL中的有效性。

在论文整体链路中，该图属于消融/对比实验环节，为前文方法部分提出的token级SAO算法提供直接经验证据，说明其设计选择（非step级粗粒度回报聚合）在奖励优化上具有可观测优势，支撑后续任务性能（pass@k）的整体提升结论。
*caption: Training reward for token-level SAO training and step-level variants, where token-level shows better training rewards.… ｜ 论文 [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### rLLM: Relational Table Learning with LLMs — Fig.1 (p.1)
![[assets/crops/rllm-relational-table-learning-with-llms-fig01.png]]
> [!tip] 【图文联合解读】**图文联合解读：**

左图为2010–2025年全球数据量堆叠柱状图（单位ZB），总量从约30ZB增至约100ZB，其中Video/Image占比最大，Text仅约20ZB。右图为LLM分词成本堆叠面积图（单位trillion dollar），到2025年升至约5000，但Text逆袭成为最大成本项。图中标注指出："语言数据虽量小但token成本高"、"多模态数据虽量大但成本相对低"。

论文借此引出关键结论：**结构化表格数据**虽规模有限，却长期被LLM高昂的token开销与语义理解需求所忽视，因而亟需专门的关系表学习方法（即rLLM）。该图作为开篇动机证据，与Table 1（数据集汇总）衔接，为后续方法设计与基准实验提供问题驱动的论证支撑。
*caption: Trends in global data volume and in LLM token costs by data type… ｜ 论文 [[rllm-relational-table-learning-with-llms]] ｜ arxiv 见 MD 元信息*

### rLLM: Relational Table Learning with LLMs — Fig.2 (p.2)
![[assets/crops/rllm-relational-table-learning-with-llms-fig02.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图示rLLM自下而上的三层架构：①底层**Data Engine**含Data Loader、Graph Builder、Table Marker三个组件；②中层**Modules**整合三类——GNNs（GraphConv、GraphTransform）、LLMs（Prediction、Enhancement）、TNNs（TableConv、TableTransform）；③顶层**Models**提供Combine、Align、Co-Train三种范式。

原文借此论证其"以最小架构复杂度高效捕获表间依赖"的核心设计理念——通过数据→模块→模型的分层解耦，将异构模型（GNN/LLM/TNN）统一在统一接口下。

该图是全文方法总纲，为后续模块化实现与Table 2的RelBench等基准分类精度对比实验提供整体框架支撑。
*caption: The architecture of rLLM analyzed using GNNs. This design efficiently captures inter-table dependencies with minimal architectural complexity.… ｜ 论文 [[rllm-relational-table-learning-with-llms]] ｜ arxiv 见 MD 元信息*

### rLLM: Relational Table Learning with LLMs — Fig.3 (p.2)
![[assets/crops/rllm-relational-table-learning-with-llms-fig03.png]]
> [!tip] 【图文联合解读】**图文联合解读**

图示rLLM基础数据结构：底层"ABC (Python)"和"Dataset (Pytorch)"通过继承箭头指向统一的"Dataset"基类；后者派生"Cora、IMDB、Titanic..."等具体数据集，并通过花括号（containment）包含右上方虚线框内的"GraphData"与"TableData"两个抽象父类，二者再分别由"BaseGraph"和"BaseTable"继承实现。

原文以此论证：rLLM数据层以单一Dataset类统一封装图数据与表数据（含外键关系），同时满足关系表数据的存储与处理需求。该图是论文方法链路的底层基石——为后续表学习、图神经网络与外键建模提供了可继承、可扩展的标准化数据接口。
*caption: Base data structure in rLLM. Arrows indicate inher- itance relationships and parentheses indicate containment relationships. data, respectively. Overa… ｜ 论文 [[rllm-relational-table-learning-with-llms]] ｜ arxiv 见 MD 元信息*

### rLLM: Relational Table Learning with LLMs — Fig.4 (p.3)
![[assets/crops/rllm-relational-table-learning-with-llms-fig04.png]]
> [!tip] 【图文联合解读】图示BRIDGE双路架构：左侧关系表（Table I/II含PK，Table III含PK+FK）经Table Encoder升维为表格嵌入；非表格特征（图结构等）旁路直连Graph Encoder（GNN），二者融合后输出。

**技术结论**：TableConv将异构列特征映射至高维空间，以弥补列数少、样本信息不足的缺陷；非表格特征旁路设计则避免图结构信息在表格编码中损失。

**论文作用**：作为BRIDGE总框图，串联"关系表→表格嵌入→图嵌入→预测"全链路，为后续TableConv与GNN融合的实验提供架构基础。
*caption: The architecture of BRIDGE columns, which can vary greatly in nature. Due to the diverse types of features and the often limited information provided … ｜ 论文 [[rllm-relational-table-learning-with-llms]] ｜ arxiv 见 MD 元信息*

## 按主题分类

### architecture (45)

- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig01.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.1 (p.1): ATOP search results on different GPU scales, each point representing a topology.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig02.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.2 (p.3): GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig03.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.3 (p.4): (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs t…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig04.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.4 (p.5): Overview of ATOP allows the system to explore novel topology designs automatical…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig05.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.5 (p.6): Examples of constructing inter-layer and intra-layer connections in ATOP. Unment…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig06.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.6 (p.9): During the 4k GPUs search process: (a) The Pareto- optimal topologies generated …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig07.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.7 (p.9): (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The se…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig08.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.8 (p.10): (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An exam…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.9 (p.11): The training iteration time for GPT-3 175B and MoE-GPT models and the correspond…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig10.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.10 (p.11): CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.11 (p.12): The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.12 (p.12): Collective communication performance on real- world deployment. ZCube and ROFT a…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig13.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.13 (p.15): In the search results of Case 3, the comparison between the number of modified l…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig14.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.14 (p.15): The search results of ATOP when building a new data center for multi-tenancy.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.15 (p.15): The search results of ATOP when building a new heterogeneous data center with st…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig16.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.16 (p.16): During the ATOP optimization process: (a) The relationship between the number of…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.17 (p.17): Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-bl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig18.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.18 (p.17): The average JCT for group all-to-all communica- tion under different topologies …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig19.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.19 (p.18): Comparison between packet-level network simulation (with packet spraying for loa…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.20 (p.19): Comparison of the CDF of flow completion times between NS-3 and flow-level simul…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig21.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.21 (p.20): ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig22.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.22 (p.20): Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rai…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig23.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.23 (p.20): HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig24.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.24 (p.20): ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig01.png]] — **Efficient Large-Scale Language Model Training on G** Fig.1 (p.1): Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models wi…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig02.png]] — **Efficient Large-Scale Language Model Training on G** Fig.2 (p.3): Combination of tensor and pipeline model parallelism (MP) used in this work for …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.3 (p.3): GPipe pipeline schedule with forward passes (blue) for all microbatches (represe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig04.png]] — **Efficient Large-Scale Language Model Training on G** Fig.4 (p.3): Default and interleaved 1F1B pipeline schedules. The top figure shows the defaul…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.5 (p.5): Blocks of transformer model partitioned with tensor model parallelism (figures b…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.6 (p.5): Fraction of time spent idling due to pipeline flush (pipeline bubble size) versu…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig07.png]] — **Efficient Large-Scale Language Model Training on G** Fig.7 (p.6): Per-GPU throughput versus microbatch size for a GPT model with a billion paramet…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig08.png]] — **Efficient Large-Scale Language Model Training on G** Fig.8 (p.6): Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.9 (p.7): Scatter/gather communication optimization. Light blue blocks are layers in the f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.10 (p.8): Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.11 (p.9): Throughput per GPU of pipeline parallelism using two different batch sizes in a …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig12.png]] — **Efficient Large-Scale Language Model Training on G** Fig.12 (p.9): Throughput per GPU of interleaved and non-interleaved schedules for a GPT model …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig13.png]] — **Efficient Large-Scale Language Model Training on G** Fig.13 (p.9): Throughput per GPU of various parallel configurations that combine pipeline and …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig14.png]] — **Efficient Large-Scale Language Model Training on G** Fig.14 (p.10): Throughput per GPU of various parallel configurations that combine data and pipe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig15.png]] — **Efficient Large-Scale Language Model Training on G** Fig.15 (p.10): Throughput per GPU of various parallel configurations that combine data and tens…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig16.png]] — **Efficient Large-Scale Language Model Training on G** Fig.16 (p.10): Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different m…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig17.png]] — **Efficient Large-Scale Language Model Training on G** Fig.17 (p.11): Throughput (in sequences per second) with and without activation recomputation f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig18.png]] — **Efficient Large-Scale Language Model Training on G** Fig.18 (p.11): Throughput per GPU with and without the scatter/gather optimization for a GPT mo…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig01.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.1 (p.7): Visualization of the (hybrid) architecture and block design of Gated DeltaNet mo…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`
- ⭐ ![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig02.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.2 (p.8): Length extrapolation on six long benchmarks.…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`
- ⭐ ![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig03.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.3 (p.9): Training throughput comparison of 1.3B models on a single H100 GPU. standalone m…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`

### disaggregated-serving (66)

- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig01.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.1 (p.1): Example two-stage pipeline parallel schedule. (a)…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig02.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.2 (p.3): High-level architecture of a decoder block. sequence length of each request (i.e…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig03.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.3 (p.4): Per-token prefill and decode time with different batch sizes (sequence length = …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig04.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.4 (p.4): Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig05.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.5 (p.5): Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] acros…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig06.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.6 (p.6): Example of how attention mask is set across dif- ferent chunk prefill iterations…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig07.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.7 (p.7): The effect of tile quantization on the runtime of one iteration of LLaMA-13B on …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig08.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.8 (p.9): Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 25…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig09.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.9 (p.10): Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequ…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig10.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.10 (p.10): Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig11.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.11 (p.11): Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. confi…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig12.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.12 (p.12): Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig13.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.13 (p.13): Ablation study: Effect of varying the chunk size on different components of the …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig01.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.1 (p.1): Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation tr…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig02.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.2 (p.2): Current LLM serving systems involve a tradeoff be- tween throughput and latency …  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig03.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.3 (p.5): Throughput of the prefill and decode phases with different batch sizes for Mistr…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig04.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.4 (p.5): Prefill and decode time with different input sizes for Mistral-7B running on sin…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig05.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.5 (p.6): Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different num…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig06.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.6 (p.6): Linear layer execution time as function of number of tokens in a batch for LLaMA…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig07.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.7 (p.6): A generation stall occurs when one or more prefills are scheduled in between con…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig08.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.8 (p.7): A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig09.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.9 (p.8): The incremental cost of coalescing prefills with decode batches. We consider two…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig10.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.10 (p.11): Capacity (in queries per second) of Mistral-7B and…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig11.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.11 (p.11): Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig12.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.12 (p.12): Latency – Throughput tradeoff in vLLM and…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig13.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.13 (p.12): TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross nod…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig14.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.14 (p.13): Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig01.png]] — **SGLang: Efficient Execution of Structured Language** Fig.1 (p.2): System architecture: An interpreter executes language primitives with optimized …  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig02.png]] — **SGLang: Efficient Execution of Structured Language** Fig.2 (p.3): The implementation of a multi-dimensional essay judge in SGLang utilizes the bra…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig03.png]] — **SGLang: Efficient Execution of Structured Language** Fig.3 (p.5): Examples of RadixAttention operations with an LRU eviction policy, illustrated a…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig04.png]] — **SGLang: Efficient Execution of Structured Language** Fig.4 (p.6): The decoding process of normal and compressed FSMs (the underscore _ means a spa…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig05.png]] — **SGLang: Efficient Execution of Structured Language** Fig.5 (p.7): Normalized throughput on Llama-7B models. Higher is better. pattern: s += contex…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig06.png]] — **SGLang: Efficient Execution of Structured Language** Fig.6 (p.8): Normalized latency on Llama-7B models. Lower is better. MMLU…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig07.png]] — **SGLang: Efficient Execution of Structured Language** Fig.7 (p.8): Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is …  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig08.png]] — **SGLang: Efficient Execution of Structured Language** Fig.8 (p.9): (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig09.png]] — **SGLang: Efficient Execution of Structured Language** Fig.9 (p.14): KV cache sharing examples. Blue boxes represent shareable prompt parts, green bo…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig10.png]] — **SGLang: Efficient Execution of Structured Language** Fig.10 (p.17): Example of how regex is converted into FSM and how FSM guides the decoding proce…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]] — **SGLang: Efficient Execution of Structured Language** Fig.11 (p.18): Comparison of decoding using Compressed FSM versus normal FSM: The left subfigur…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig12.png]] — **SGLang: Efficient Execution of Structured Language** Fig.12 (p.19): Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is b…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig13.png]] — **SGLang: Efficient Execution of Structured Language** Fig.13 (p.19): Achieved cache hit rate and optimal cache hit rate on various benchmarks. opport…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig14.png]] — **SGLang: Efficient Execution of Structured Language** Fig.14 (p.20): An SGLang program and its corresponding dataflow graph.…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig01.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.1 (p.1): Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggre…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig02.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.2 (p.2): Impact of disaggregation on supported batch size and number of images per reques…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig03.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.3 (p.3): The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migrati…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig04.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.4 (p.4): System architecture of the proposed EPD Disaggregated Inference. the data associ…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig05.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.5 (p.6): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig06.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.6 (p.7): Distribution of TTFT (Y-axis) across varying numbers of images per request (X-ax…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.7 (p.7): SLO attainment (↑) versus request rate on the…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig08.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.8 (p.7): As seen, EPD consistently outperforms vLLM and Dist-…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig09.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.9 (p.9): As shown, EPD is the only configuration that achieves the SLO requirements, whil…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig10.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.10 (p.13): Left: Impact of varying the number of encoding workers in the EPD method. The no…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig11.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.11 (p.13): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig12.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.12 (p.16): Breakdown of latency for encode and prefill stages using the InternVL2-8B model …  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig01.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.1 (p.2): Mooncake Architecture. remote location will prolong the TTFT, and a large batch …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig02.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.2 (p.4): Normalized throughput and latency of prefill and decoding stages with different …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig03.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.3 (p.5): The KVCache pool in CPU memory. Each block is attached with a hash value determi…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig04.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.4 (p.6): Workflow of inference instances. ( ) For prefill instances, the load and store …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig05.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.5 (p.6): Input and output length distributions in the request trace. 4…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.6 (p.7): CDF (Cumulative Distribution…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig07.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.7 (p.9): Latency of storing KVCache of different request lengths (Layer-wise latency refe…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig08.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.8 (p.11): The prefill scheduling experiment in the Mooncake cluster.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig09.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.9 (p.13): The load of prefill and decoding instances over 20 minutes, before using the pre…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig10.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.10 (p.14): Instance load when applying Early Rejection and Early Rejection Based on Predict…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig11.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.11 (p.16): End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eva…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.12 (p.16): End-to-end experiments of Mooncake and vLLM on simulated data.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.13 (p.17): Request TTFT and TBT distributions of Mooncake and vLLM under real workloads…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`

### kv-cache (53)

- ⭐ ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig01.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.1 (p.1): Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.2 (p.3): Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning …  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig03.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.3 (p.8): Relative speedup of IndexCache over the DSA baseline across three inference sett…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig04.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.4 (p.16): Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig01.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.1 (p.2): Mooncake Architecture. remote location will prolong the TTFT, and a large batch …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig02.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.2 (p.4): Normalized throughput and latency of prefill and decoding stages with different …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig03.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.3 (p.5): The KVCache pool in CPU memory. Each block is attached with a hash value determi…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig04.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.4 (p.6): Workflow of inference instances. ( ) For prefill instances, the load and store …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig05.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.5 (p.6): Input and output length distributions in the request trace. 4…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.6 (p.7): CDF (Cumulative Distribution…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig07.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.7 (p.9): Latency of storing KVCache of different request lengths (Layer-wise latency refe…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig08.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.8 (p.11): The prefill scheduling experiment in the Mooncake cluster.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig09.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.9 (p.13): The load of prefill and decoding instances over 20 minutes, before using the pre…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig10.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.10 (p.14): Instance load when applying Early Rejection and Early Rejection Based on Predict…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig11.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.11 (p.16): End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eva…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.12 (p.16): End-to-end experiments of Mooncake and vLLM on simulated data.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.13 (p.17): Request TTFT and TBT distributions of Mooncake and vLLM under real workloads…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig01.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.1 (p.2): Comparison of two deployment paradigms for PD-disaggregated LLM serving.…  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ⭐ ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig02.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.2 (p.4): KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.…  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ⭐ ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig03.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.3 (p.6): Deployment topology of the PrfaaS-PD architecture.…  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ⭐ ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig04.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.4 (p.7): Hybrid prefix cache pool. Linear states and full-attention KVCache are managed b…  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ⭐ ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig05.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.5 (p.11): Illustration of the grid search process for the two optimization variables. (a) …  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig01.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.1 (p.2): Autoregressive generation, at each step the new token (orange) attends to all pr…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig02.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.2 (p.3): Data-flow of the KV cache within a single transformer layer. Input token xt fans…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig03.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.3 (p.3): KV cache memory as a function of context length for three LLaMA-2 model variants…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig04.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.4 (p.4): Causal self-attention weight matrix for “The apple tastes sweet.” visualised wit…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig05.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.5 (p.5): Taxonomy of KV cache optimization techniques surveyed in this paper, organized i…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig06.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.6 (p.6): Upper plots illustrate symbolic plots of an attention map deploying different KV…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig07.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.7 (p.7): The graph shows the simplified workflow of SnapKV, where the orange area represe…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig08.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.8 (p.9): Definition of per-token and per-channel quantization. X ∈Rlprompt×d is the key/v…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig09.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.9 (p.9): Palu’s low-rank projection method for KV-cache reduction. A weight matrix W of l…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig10.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.10 (p.11): vLLM system overview [22]. 11…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig11.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.11 (p.12): Operation flow of the prefetching module of InfiniGen. [23]. A layer-wise KV cac…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig12.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.12 (p.15): Standard linear attention (top) vs. loglinear attention (bottom). The input cons…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig13.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.13 (p.17): During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaini…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig14.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.14 (p.17): System overview of TailorKV. Offline identification categorizes the layers into …  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig01.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.1 (p.2): Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend’s s…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig02.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.2 (p.4): Generation quality improves as more text chunks are retrieved. and fetch top-k r…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig03.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.3 (p.4): An illustrative example of an LLM input with two text chunks prepended to a quer…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig04.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.4 (p.5): Contrasting the attention matrices of (a) full KV recompute and (b) full KV reus…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig05.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.5 (p.6): Illustrated contrast between (a) full KV recompute and (b) selective KV recomput…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig06.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.6 (p.6): Attention deviation reduces as we recompute the KV of more tokens on each layer.…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig07.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.7 (p.7): Distribution of KV deviation of different tokens on one layer. 5 vs. 6 12 vs. 13…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig08.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.8 (p.7): Rank correlation of the KV deviation per token be- tween two consecutive layers.…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig09.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.9 (p.7): CacheBlend selects the HKVD (high KV deviation) tokens of one layer by computing…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.10 (p.8): (a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smart…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig11.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.11 (p.9): CacheBlend system (green stared) in light of LLM context augmented generation fo…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig12.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.12 (p.10): CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligibl…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig13.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.13 (p.10): Generation quality of CacheBlend with Yi-34B vs MapReduce and MapRerank. 7…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig14.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.14 (p.11): CacheBlend achieves lower TTFT with higher throughput in RAG scenarios compared …  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig15.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.15 (p.11): CacheBlend outperforms baseline with varying chunk numbers, chunk lengths, and b…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig16.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.16 (p.8): This means that even if the storage device is a fast device (ex. CPU RAM), the d…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ⭐ ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig17.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.17 (p.12): CacheBlend’s outperforms baselines when using RAM and slower disks…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`

### long-context (8)

- ⭐ ![[assets/crops/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-fig01.png]] — **DeepSeek-V4: Towards Highly Efficient Million-Toke** Fig.1 (p.14): 2.4. Muon Optimizer…  `[[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]`
- ⭐ ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]] — **DeepSeek-V4: Towards Highly Efficient Million-Toke** Fig.5 (p.15): This forms a fine-grained pipeline among experts, keeping both computation and c…  `[[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig01.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.1 (p.1): The SoTA SD method, EAGLE, has a training context length of 2048, which is signi…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig02.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.2 (p.4): Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig03.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.3 (p.7): Decoding speed (tokens/s) across different models and settings. All results are …  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig04.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.4 (p.8): Training loss curves on long-context data.…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig05.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.5 (p.8): Latency breakdown for a single speculative decoding loop comparing the EAGLE imp…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig06.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.6 (p.9): Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such …  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`

### moe (42)

- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig01.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.1 (p.9): Data flow through an MoE layer: Route, Dispatch, Compute, and Combine stages.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig02.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.2 (p.10): Router architecture: linear projection, score function, top-𝑘selection, and load…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig03.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.3 (p.13): Dense Model vs MoE Model parameter/compute scaling.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig04.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.4 (p.15): Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communic…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig05.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.5 (p.17): Parallelism mappings: traditional constraints vs. MoE Parallel Folding decouplin…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig06.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.6 (p.18): Parallel Folding: decoupled attention and MoE parallelism mappings.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig07.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.7 (p.22): Memory-Efficient Permutation.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig08.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.8 (p.23): Selective Recomputation.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig09.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.9 (p.24): Fine-grained activation offloading: stream overlap for forward and backward pass…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig10.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.10 (p.26): Fine-grained offloading and recomputation: complementary memory optimization str…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig11.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.11 (p.28): Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig12.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.12 (p.28): Persistent double-buffer design: two pre-allocated buffers are cycled across FSD…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig13.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.13 (p.30): Expert parallelism across 4 GPUs with 4 experts.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig14.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.14 (p.31): The dispatch kernel design of HybridEP.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig15.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.15 (p.31): The combine kernel design of HybridEP.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig16.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.16 (p.32): Merged FWD-FWD Timeline with all-to-all Overlapping.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig17.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.17 (p.33): Merged FWD-BWD Timeline with all-to-all Overlapping.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig18.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.18 (p.34): EP all-to-all communication overlap strategies: baseline vs. 1F1B with W/D split…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig19.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.19 (p.35): Interleaved PP Timeline with all-to-all Overlapping.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig20.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.20 (p.37): The pipeline for permute fusion in the training process. • Preprocessing: Permut…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig21.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.21 (p.38): The workflow of the router fusion. • Computation of MoE auxiliary loss: Building…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig22.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.22 (p.39): Traditional execution (top) versus CUDA Graph execution (bottom).…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig23.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.23 (p.39): Full versus layer-wise CUDA Graphs in one training iteration (three layers, two …  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig24.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.24 (p.40): Partial CUDA Graphs capture static components (attention, shared experts, router…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig25.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.25 (p.41): Transformer layer forward pass: without (upper) and with (lower) partial CUDA Gr…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig26.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.26 (p.42): Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatc…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig27.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.27 (p.45): ECHO workflow for forward and backward passes. The planner generates routing and…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig28.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.28 (p.46): Memory layout comparison across three execution modes. Left: Eager mode allocate…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig29.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.29 (p.46): Paged Stashing stream overlap. Forward pass: After Layer N computes, its activat…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig30.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.30 (p.50): FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8. A reduced-pr…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig31.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.31 (p.52): The computation of a linear layer with various FP8 recipes. Note the differences…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig32.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.32 (p.53): FP8 primary weight quantization scheme for blockwise scaling.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig33.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.33 (p.54): FP8 primary weight quantization scheme for delayed scaling and per-tensor curren…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig34.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.34 (p.57): SDPA exhibits 𝑂(𝑠2) complexity, while MoE and the remaining attention operations…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig35.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.35 (p.59): Communication and computation patterns of TP and two types of CP.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig36.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.36 (p.61): Unpacked vs. Packed sequences.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig37.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.37 (p.61): Compute imbalance in causal attention over packed sequences. are partitioned and…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig38.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.38 (p.61): Dynamic Context Parallelism for Packed Sequences.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig39.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.39 (p.64): Load balancing strategies in Megatron-Core MoE.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig40.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.40 (p.65): Shared expert architecture in Megatron-Core MoE. The shared expert processes all…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig41.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.41 (p.66): Flexible Pipeline Parallel Placement. 66…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig42.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.42 (p.67): An example of granular upcycling a dense layer into E2G2T2 fine-grained MoE. E2G…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`

### multimodal (46)

- ⭐ ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig01.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.1 (p.1): Kimi K2.5 main results. 1…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig02.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.2 (p.4): Vision RL training curves on vision benchmarks starting from minimal zero-vision…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig03.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.3 (p.5): An agent swarm has a trainable orchestrator that dynamically creates specialized…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig04.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.4 (p.6): In our parallel-agent reinforcement learning environment, the training accuracy …  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig05.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.5 (p.10): Comparison of model performance and token usage for Kimi K2 Thinking following t…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig06.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.6 (p.14): The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instan…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig07.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.7 (p.14): Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context …  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.8 (p.15): Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent base…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.9 (p.21): Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixe…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.10 (p.23): Overview of our agentic RL framework. environments with minimal overhead. Our de…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.11 (p.28): Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth:…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.12 (p.29): Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 2…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ⭐ ![[assets/crops/qwen3-vl-technical-report-fig01.png]] — **Qwen3-VL Technical Report** Fig.1 (p.3): The Qwen3-VL framework integrates a vision encoder and a language model decoder …  `[[qwen3-vl-technical-report]]`
- ⭐ ![[assets/crops/qwen3-vl-technical-report-fig02.png]] — **Qwen3-VL Technical Report** Fig.2 (p.17): Multilingual OCR performance of our model on a self-built test set. The model ac…  `[[qwen3-vl-technical-report]]`
- ⭐ ![[assets/crops/qwen3-vl-technical-report-fig03.png]] — **Qwen3-VL Technical Report** Fig.3 (p.25): Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across …  `[[qwen3-vl-technical-report]]`
- ⭐ ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig01.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.1 (p.1): Left: Conventional large multimodal models (LMMs) string all visual tokens into …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ⭐ ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig02.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.2 (p.4): Architecture of DeepStack. The main innovation lies in the DeepStack strategy th…  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ⭐ ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig03.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.3 (p.8): Analysis on using LLM layers to process visual tokens. (a) We insert the visual …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ⭐ ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig04.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.4 (p.10): Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ⭐ ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig05.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.5 (p.9): Visualization of three sam- pling methods for DeepStack.…  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig01.png]] — **KIMI-VL TECHNICAL REPORT** Fig.1 (p.1): Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, includin…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig02.png]] — **KIMI-VL TECHNICAL REPORT** Fig.2 (p.2): Highlights of Kimi-VL performance for a wide range of benchmarks like, general b…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig03.png]] — **KIMI-VL TECHNICAL REPORT** Fig.3 (p.3): The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT …  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig04.png]] — **KIMI-VL TECHNICAL REPORT** Fig.4 (p.4): The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-onl…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig05.png]] — **KIMI-VL TECHNICAL REPORT** Fig.5 (p.6): The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages o…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig06.png]] — **KIMI-VL TECHNICAL REPORT** Fig.6 (p.8): Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig07.png]] — **KIMI-VL TECHNICAL REPORT** Fig.7 (p.12): Kimi-VL exhibits strong visual reasoning capabilities by grounding visual conten…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig08.png]] — **KIMI-VL TECHNICAL REPORT** Fig.8 (p.13): Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric …  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig09.png]] — **KIMI-VL TECHNICAL REPORT** Fig.9 (p.14): Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across v…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig10.png]] — **KIMI-VL TECHNICAL REPORT** Fig.10 (p.15): Kimi-VL is capable of following multi-step reasoning processes to complete compl…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig11.png]] — **KIMI-VL TECHNICAL REPORT** Fig.11 (p.16): Video scene splitting. Kimi-VL processes a long-form video by segmenting it into…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig12.png]] — **KIMI-VL TECHNICAL REPORT** Fig.12 (p.17): Catching and understanding key details from an hour-long video course. Kimi-VL d…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/kimi-vl-technical-report-fig13.png]] — **KIMI-VL TECHNICAL REPORT** Fig.13 (p.16): Specifically, increasing the max thinking token length at inference time consist…  `[[kimi-vl-technical-report]]`
- ⭐ ![[assets/crops/qwen2-5-vl-technical-report-fig01.png]] — **Qwen2.5-VL Technical Report** Fig.1 (p.3): The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a …  `[[qwen2-5-vl-technical-report]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig01.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.1 (p.1): Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggre…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig02.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.2 (p.2): Impact of disaggregation on supported batch size and number of images per reques…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig03.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.3 (p.3): The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migrati…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig04.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.4 (p.4): System architecture of the proposed EPD Disaggregated Inference. the data associ…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig05.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.5 (p.6): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig06.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.6 (p.7): Distribution of TTFT (Y-axis) across varying numbers of images per request (X-ax…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.7 (p.7): SLO attainment (↑) versus request rate on the…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig08.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.8 (p.7): As seen, EPD consistently outperforms vLLM and Dist-…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig09.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.9 (p.9): As shown, EPD is the only configuration that achieves the SLO requirements, whil…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig10.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.10 (p.13): Left: Impact of varying the number of encoding workers in the EPD method. The no…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig11.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.11 (p.13): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig12.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.12 (p.16): Breakdown of latency for encode and prefill stages using the InternVL2-8B model …  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`

### rl (68)

- ⭐ ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig01.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.1 (p.1): A comparison of learning behavior of the GEPA prompt optimizer against a state-o…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig02.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.2 (p.3): This figure shows an example prompt generated by GEPA for the second-hop documen…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.3 (p.5): GEPA proposes a new candidate in every iteration by improving existing candidate…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.4 (p.4): GEPA receives the following inputs: A system  instan- tiated with simple prompt…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.5 (p.7): GEPA’s reflective prompt mutation systematically incorporates task-specific nuan…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig06.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.6 (p.10): Comparing the impact of different candidate selection strategies. (Left) As can …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.7 (p.13): GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector ut…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.8 (p.13): GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.9 (p.24): Details of System Aware Merge. r represents a seeded stochastic sampler.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.10 (p.28): Final test set performance for aggregate and individual benchmarks.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.11 (p.28): This figure compares the learning behaviour of GEPA against GRPO with full-param…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig12.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.12 (p.29): Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.13 (p.29): IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIP…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.14 (p.29): HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.15 (p.29): PUPA: rollout vs. score for different models/settings. 29…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.16 (p.30): Generalization gaps for different optimization methods. Following Wan et al. (20…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.17 (p.30): These plots visualize the final aggregate scores against the aggregate prompt si…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.18 (p.31): Comparing the token counts of optimized programs across benchmarks. (a) Abl:Sele…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.19 (p.31): HotpotQA GPT-4.1 Mini 31…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.20 (p.32): HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.21 (p.32): IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.22 (p.32): IFBench Qwen3 8B 32…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.23 (p.33): HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.24 (p.33): HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.25 (p.33): PUPA GPT-4.1 Mini 33…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.26 (p.34): PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.27 (p.12): We also note that generation stochasticity (temperature based sampling) is elimi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig01.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.1 (p.4): Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig02.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.2 (p.9): (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability af…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig03.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.3 (p.17): Retrieved Token Loss Masking Study instruction-tuned models exhibit faster conve…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig04.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.4 (p.17): Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges fa…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig05.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.5 (p.18): Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across fo…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig06.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.6 (p.19): The training dynamics of SEARCH-R1 with a different number of retrieved pas- sag…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig07.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.7 (p.19): We observe that a larger group size generally leads to faster convergence but ma…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig01.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.1 (p.3): Dataflow graph of 3 RLHF algorithms [19, 43, 55].…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig02.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.2 (p.3): Programming model used in RLHF systems. (a)…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig03.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.3 (p.4): Dataflow execution given a model placement plan.…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig04.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.4 (p.6): Architecture of HybridFlow. 3D-HybridEngine and Auto-Mapping algorithm. The hybr…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig05.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.5 (p.6): An illustration of hierarchical APIs. (a) Model with 3D parallel configuration, …  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig06.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.6 (p.7): Implementation of PPO [55], ReMax [43], and Safe- RLHF [19]. Users can adapt to …  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig07.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.7 (p.8): 3D-HybridEngine workflow in one RLHF iteration. 4 GPUs are used for actor traini…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig08.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.8 (p.8): Model weights resharding. 2 machines each with 4 GPUs are used for actor trainin…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig09.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.9 (p.11): PPO throughput. Numbers in parentheses are HybridFlow speedups compared with bas…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.10 (p.11): ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with b…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.11 (p.11): Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compare…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig12.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.12 (p.12): Throughput of HybridFlow under different placements 32 64 96 128 # of GPUs…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig13.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.13 (p.12): Placement comparison under 13B actor and reference policy & 70B critic and rewar…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig14.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.14 (p.13): Transition time between actor training and generation.…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig15.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.15 (p.13): Time breakdown on different generation parallel sizes of the actor model on 16 G…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig16.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.16 (p.13): Runtime of device mapping algorithm. The model size and # of GPUs are simultaneo…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ⭐ ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig01.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.1 (p.4): Execution timeline of a synchronous (left) and a one-step overlap (right) RL sys…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ⭐ ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig02.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.2 (p.4): The AREAL architecture featuring asynchronous generation and training components…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ⭐ ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig03.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.3 (p.4): Illustration of generation management in AREAL. Vertical lines show the ready ti…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ⭐ ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig04.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.4 (p.8): The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consi…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ⭐ ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig05.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.5 (p.9): Ablation studies of the decoupled PPO objective and staleness control with a 1.5…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ⭐ ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig06.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.6 (p.10): Ablation studies on system optimizations. experimental setup, we configured 32 m…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ⭐ ![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-fig02.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.2 (p.6): In the initial stage, we collect thousands of cold-start data that exhibits a co…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ⭐ ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.3 (p.14): For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g fro…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ⭐ ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.6 (p.35): B.6. Ablation Study of Language Consistency Reward…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ⭐ ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.7 (p.37): As can be seen, without the LC reward, language consistency gradually deteriorat…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ⭐ ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.13 (p.48): We have categorized potential content safety challenges faced by language models…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ⭐ ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.14 (p.53): For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and …  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ⭐ ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig01.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.1 (p.1): The performance of SAO on reasoning and coding benchmarks. The four reasoning be…  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ⭐ ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig02.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.2 (p.3): Overview of SAO with single rollout design. The numbers denote the generation or…  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ⭐ ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig03.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.3 (p.6): Performance comparison between SAO and GRPO (w/ DIS) during training. It can be …  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ⭐ ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig04.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.4 (p.7): Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for …  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ⭐ ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig05.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.5 (p.9): Online learning simulation under changing writing-style preferences. 5…  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ⭐ ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig06.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.6 (p.13): Training reward for token-level SAO training and step-level variants, where toke…  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`

### sparse-attention (4)

- ⭐ ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig01.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.1 (p.1): Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.2 (p.3): Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning …  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig03.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.3 (p.8): Relative speedup of IndexCache over the DSA baseline across three inference sett…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig04.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.4 (p.16): Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`

### speculative (78)

- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig01.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.1 (p.2): MEDUSA introduces multiple heads on top of the last hidden states of the LLM, en…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig02.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.2 (p.3): Remarkably, similar ideas have also been explored in independent works like Miao…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig03.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.3 (p.7): Left: Speed comparison of baseline, MEDUSA-1 and MEDUSA-2 on Vicuna-7B/13B. MEDU…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p08.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.4 (p.8): Effectiveness of numbers of candidate tokens for decoding introduced by trees (d…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig05.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.5 (p.5): 5…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig06.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.6 (p.15): Visualization of a sparse tree setting for MEDUSA-2 Vicuna-7B. The tree has 64 n…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig07.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.7 (p.15): Inference speed of various models using speculative decoding on MT-Bench. Baseli…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig08.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.8 (p.16): Speedup of various models with MEDUSA-2. MEDUSA-2 shows significant speed improv…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig09.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.9 (p.18): The figure shows the relationship between FLOP/s and Operational Intensity for a…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig10.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.10 (p.18): Llama-13B operators on A100-80GB-PCIe. 18…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig11.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.11 (p.19): Llama-33B operators on A100-80GB-PCIe. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig12.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.12 (p.19): Llama-7B operators on A40. 19…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig13.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.13 (p.20): Llama-13B operators on A40. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig14.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.14 (p.20): Llama-33B operators on A40. 20…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig15.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.15 (p.21): Llama-7B operators on A6000. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig16.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.16 (p.21): Llama-13B operators on A6000. 21…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig17.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.17 (p.22): Llama-33B operators on A6000. 22…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig18.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.18 (p.23): FLOP/s vs. Operational Intensity of attention matrix multiplication with batch s…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig19.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.19 (p.24): FLOP/s vs. Operational Intensity of attention matrix multiplication with sequenc…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig20.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.20 (p.24): FLOP/s vs. Operational Intensity of Linear layers. 24…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig21.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.21 (p.26): Simulated acceleration rate, speedup, and normalized latency ablation using diff…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig22.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.22 (p.27): Simulated speedup with sequence length 1024 for Llama-7B. 1 16 32 48 64 80 96 11…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig23.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.23 (p.27): Simulated speedup with batch size 4 for Llama-7B. 27…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig01.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.1 (p.1): Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target …  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For the standard speculati…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig03.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.3 (p.3): Illustration of training-time test (the bottom part) and its comparison with oth…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig04.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.4 (p.2): We can address this issue by incorporating Step 1 into the training process (the…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig05.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.5 (p.4): Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the d…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig06.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.6 (p.5): All attention masks are diagonal, except when the original training data is used…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig07.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.7 (p.8): Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LL…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig01.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.1 (p.1): Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for gr…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig02.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.2 (p.2): Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig03.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.3 (p.2): Uncertainty in feature sequences. The next fea- ture following fI is contingent …  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig04.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.4 (p.3): Accuracy and speedup ratio of draft models based on tokens, features and feature…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig05.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.5 (p.4): A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5.…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig06.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.6 (p.4): Pipeline of EAGLE. The upper section illustrates the computational process, whil…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig07.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.7 (p.7): Speedup ratios of EAGLE with and without the use of tree attention. The evaluati…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig08.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.8 (p.8): Performance of draft models with varying inputs. The target LLM is Vicuna 7B, an…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig09.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.9 (p.12): However, the optimal tree structure is likely context-dependent. For instance, a…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig01.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.1 (p.1): Speedup ratios of different methods at tempera- ture=1. For speculative sampling…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ⭐ ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig02.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For speculative sampling, …  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ⭐ ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig03.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.3 (p.3): Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s t…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ⭐ ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig04.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.4 (p.3): Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. …  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ⭐ ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig05.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.5 (p.3): Overall, the acceptance rate of draft tokens is position-dependent, with the hig…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ⭐ ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig06.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.6 (p.4): Average acceptance rates for different confidence score intervals of the draft m…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ⭐ ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig07.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.7 (p.5): Illustration of EAGLE-2. The numbers beside the edges represent the confidence s…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ⭐ ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig01.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.1 (p.2): Block diffusion sequentially generates blocks of tokens by performing diffusion …  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ⭐ ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig02.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.2 (p.6): Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on …  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ⭐ ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig03.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.3 (p.21): x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ⭐ ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig04.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.4 (p.22): We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible spar…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ⭐ ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig05.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.5 (p.23): Attention computation using FlexAttention with our proposed custom mask.…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ⭐ ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.6 (p.26): Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion s…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ⭐ ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.7 (p.27): Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffus…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ⭐ ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.8 (p.28): Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ⭐ ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig01.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.1 (p.2): Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qw…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ⭐ ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig02.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.2 (p.4): DFlash Inference Design. Hidden context features extracted from the target model…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ⭐ ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig03.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.3 (p.3): Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ⭐ ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig04.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.4 (p.5): DFlash training attention. The target model provides context features (blue) tha…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ⭐ ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig05.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.5 (p.13): The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ⭐ ![[assets/crops/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-fig01.png]] — **DSpark: Confidence-Scheduled Speculative Decoding ** Fig.1 (p.4): Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= …  `[[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]`
- ⭐ ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig01.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.1 (p.2): End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs a…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ⭐ ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig02.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.2 (p.3): Expected speculative decoding speedup scales as a function of draft length γ, un…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ⭐ ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig03.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.3 (p.4): JetSpec design overview. JetSpec extracts fused hidden features from the frozen …  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ⭐ ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig04.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.4 (p.15): Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ⭐ ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig05.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.5 (p.18): Figure 5: Causal attention mask used for training with multiple sampled blocks. …  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ⭐ ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig06.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.6 (p.19): Each sampled block includes an anchor position and multiple future token positio…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig01.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.1 (p.1): The SoTA SD method, EAGLE, has a training context length of 2048, which is signi…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig02.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.2 (p.4): Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig03.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.3 (p.7): Decoding speed (tokens/s) across different models and settings. All results are …  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig04.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.4 (p.8): Training loss curves on long-context data.…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig05.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.5 (p.8): Latency breakdown for a single speculative decoding loop comparing the EAGLE imp…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig06.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.6 (p.9): Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such …  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig01.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.1 (p.1): Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct …  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ⭐ ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig02.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.2 (p.2): Overview of SpecExtend. FlashAttention accelerates the prefill phases of both ta…  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ⭐ ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig03.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.3 (p.4): Left figure shows acceptance rates for hard and easy tokens, where CMR enables m…  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ⭐ ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig04.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.4 (p.5): (a) Average accepted length of Vicuna-7B/68M across different draft model cache …  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ⭐ ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig05.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.5 (p.6): Speedup comparison of standard speculative decoding and SpecExtend across varyin…  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ⭐ ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig06.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.6 (p.7): Decoding speed (left) and average ac- cepted length (right) of the DeepSeek-R1-D…  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`

### training (157)

- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig01.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.1 (p.1): Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target …  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For the standard speculati…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig03.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.3 (p.3): Illustration of training-time test (the bottom part) and its comparison with oth…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig04.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.4 (p.2): We can address this issue by incorporating Step 1 into the training process (the…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig05.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.5 (p.4): Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the d…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig06.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.6 (p.5): All attention masks are diagonal, except when the original training data is used…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig07.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.7 (p.8): Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LL…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig01.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.1 (p.1): ATOP search results on different GPU scales, each point representing a topology.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig02.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.2 (p.3): GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig03.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.3 (p.4): (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs t…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig04.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.4 (p.5): Overview of ATOP allows the system to explore novel topology designs automatical…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig05.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.5 (p.6): Examples of constructing inter-layer and intra-layer connections in ATOP. Unment…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig06.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.6 (p.9): During the 4k GPUs search process: (a) The Pareto- optimal topologies generated …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig07.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.7 (p.9): (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The se…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig08.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.8 (p.10): (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An exam…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.9 (p.11): The training iteration time for GPT-3 175B and MoE-GPT models and the correspond…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig10.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.10 (p.11): CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.11 (p.12): The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.12 (p.12): Collective communication performance on real- world deployment. ZCube and ROFT a…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig13.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.13 (p.15): In the search results of Case 3, the comparison between the number of modified l…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig14.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.14 (p.15): The search results of ATOP when building a new data center for multi-tenancy.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.15 (p.15): The search results of ATOP when building a new heterogeneous data center with st…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig16.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.16 (p.16): During the ATOP optimization process: (a) The relationship between the number of…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.17 (p.17): Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-bl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig18.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.18 (p.17): The average JCT for group all-to-all communica- tion under different topologies …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig19.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.19 (p.18): Comparison between packet-level network simulation (with packet spraying for loa…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.20 (p.19): Comparison of the CDF of flow completion times between NS-3 and flow-level simul…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig21.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.21 (p.20): ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig22.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.22 (p.20): Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rai…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig23.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.23 (p.20): HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig24.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.24 (p.20): ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig01.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.1 (p.9): Data flow through an MoE layer: Route, Dispatch, Compute, and Combine stages.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig02.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.2 (p.10): Router architecture: linear projection, score function, top-𝑘selection, and load…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig03.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.3 (p.13): Dense Model vs MoE Model parameter/compute scaling.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig04.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.4 (p.15): Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communic…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig05.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.5 (p.17): Parallelism mappings: traditional constraints vs. MoE Parallel Folding decouplin…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig06.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.6 (p.18): Parallel Folding: decoupled attention and MoE parallelism mappings.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig07.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.7 (p.22): Memory-Efficient Permutation.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig08.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.8 (p.23): Selective Recomputation.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig09.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.9 (p.24): Fine-grained activation offloading: stream overlap for forward and backward pass…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig10.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.10 (p.26): Fine-grained offloading and recomputation: complementary memory optimization str…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig11.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.11 (p.28): Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig12.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.12 (p.28): Persistent double-buffer design: two pre-allocated buffers are cycled across FSD…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig13.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.13 (p.30): Expert parallelism across 4 GPUs with 4 experts.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig14.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.14 (p.31): The dispatch kernel design of HybridEP.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig15.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.15 (p.31): The combine kernel design of HybridEP.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig16.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.16 (p.32): Merged FWD-FWD Timeline with all-to-all Overlapping.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig17.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.17 (p.33): Merged FWD-BWD Timeline with all-to-all Overlapping.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig18.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.18 (p.34): EP all-to-all communication overlap strategies: baseline vs. 1F1B with W/D split…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig19.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.19 (p.35): Interleaved PP Timeline with all-to-all Overlapping.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig20.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.20 (p.37): The pipeline for permute fusion in the training process. • Preprocessing: Permut…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig21.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.21 (p.38): The workflow of the router fusion. • Computation of MoE auxiliary loss: Building…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig22.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.22 (p.39): Traditional execution (top) versus CUDA Graph execution (bottom).…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig23.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.23 (p.39): Full versus layer-wise CUDA Graphs in one training iteration (three layers, two …  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig24.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.24 (p.40): Partial CUDA Graphs capture static components (attention, shared experts, router…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig25.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.25 (p.41): Transformer layer forward pass: without (upper) and with (lower) partial CUDA Gr…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig26.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.26 (p.42): Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatc…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig27.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.27 (p.45): ECHO workflow for forward and backward passes. The planner generates routing and…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig28.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.28 (p.46): Memory layout comparison across three execution modes. Left: Eager mode allocate…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig29.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.29 (p.46): Paged Stashing stream overlap. Forward pass: After Layer N computes, its activat…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig30.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.30 (p.50): FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8. A reduced-pr…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig31.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.31 (p.52): The computation of a linear layer with various FP8 recipes. Note the differences…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig32.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.32 (p.53): FP8 primary weight quantization scheme for blockwise scaling.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig33.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.33 (p.54): FP8 primary weight quantization scheme for delayed scaling and per-tensor curren…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig34.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.34 (p.57): SDPA exhibits 𝑂(𝑠2) complexity, while MoE and the remaining attention operations…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig35.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.35 (p.59): Communication and computation patterns of TP and two types of CP.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig36.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.36 (p.61): Unpacked vs. Packed sequences.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig37.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.37 (p.61): Compute imbalance in causal attention over packed sequences. are partitioned and…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig38.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.38 (p.61): Dynamic Context Parallelism for Packed Sequences.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig39.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.39 (p.64): Load balancing strategies in Megatron-Core MoE.…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig40.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.40 (p.65): Shared expert architecture in Megatron-Core MoE. The shared expert processes all…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig41.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.41 (p.66): Flexible Pipeline Parallel Placement. 66…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig42.png]] — **Scalable Training of Mixture-of-Experts Models wit** Fig.42 (p.67): An example of granular upcycling a dense layer into E2G2T2 fine-grained MoE. E2G…  `[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig01.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.1 (p.4): Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig02.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.2 (p.9): (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability af…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig03.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.3 (p.17): Retrieved Token Loss Masking Study instruction-tuned models exhibit faster conve…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig04.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.4 (p.17): Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges fa…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig05.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.5 (p.18): Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across fo…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig06.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.6 (p.19): The training dynamics of SEARCH-R1 with a different number of retrieved pas- sag…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig07.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.7 (p.19): We observe that a larger group size generally leads to faster convergence but ma…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ⭐ ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig01.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.1 (p.1): Overview of conversion from multi-head to multi-query attention. Key and value p…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ⭐ ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig02.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.2 (p.2): Overview of grouped-query method. Multi-head attention has H query, key, and val…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ⭐ ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig03.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.3 (p.3): Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality an…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ⭐ ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig04.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.4 (p.4): Performance comparison of different check- point conversion methods for T5-Large…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ⭐ ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig05.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.5 (p.4): Performance as a function of uptraining pro- portion for T5 XXL models with MQA …  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ⭐ ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig06.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.6 (p.4): Time per sample for GQA-XXL as a function of the number of GQA groups with input…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig01.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.1 (p.2): Data parallel training with ZeRO2. dependencies that contribute to stability iss…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig02.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.2 (p.3): Interleaved 1F1B pipeline. update the model. Instead of duplicating model states…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig03.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.3 (p.4): Overlapping communication in tensor parallelism (TP) and sequence parallelism (S…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig04.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.4 (p.4): The cool-down phase can be viewed as the inverse of the warm-up phase, allowing …  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig05.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.5 (p.6): Robust training workflow. interval and help recover the transmission more quickl…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig06.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.6 (p.8): Inconsistent MFU observed in large-scale training. Differ- ent colors denote dis…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig07.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.7 (p.8): We gather latency data of the computation phase (forward and backward) across de…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig08.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.8 (p.9): The trace shows events collected in a pipeline group on a unified timeline. Depe…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig09.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.9 (p.10): Weak-scaling training performance of Megatron-LM and…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig10.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.10 (p.11): The training loss curves in microbenchmark experiments.…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig11.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.11 (p.11): The normalized training loss curve of a real production run on more than 10,000 …  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig12.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.12 (p.12): The MFU becomes stable after addressing the stragglers and problematic code segm…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig01.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.1 (p.3): Comparing the per-device memory consumption of model states, with three stages o…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ⭐ ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig02.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.2 (p.4): ZeRO training throughput and speedup w.r.t SOTA baseline for varying model sizes…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ⭐ ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig03.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.3 (p.5): Superlinear scalability and per GPU training throughput of a 60B parameter model…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ⭐ ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig04.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.4 (p.16): Max model throughput with ZeRO-DP.…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ⭐ ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig05.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.5 (p.16): SOTA Turing-NLG enabled by ZeRO.…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ⭐ ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig06.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.6 (p.16): Max model size .…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ⭐ ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig07.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.7 (p.16): Max cache allo- cated.…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ⭐ ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig08.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.8 (p.16): Throughput per GPU. a Bert-Large model for a data sample. Even if we assume the …  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig01.png]] — **Efficient Large-Scale Language Model Training on G** Fig.1 (p.1): Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models wi…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig02.png]] — **Efficient Large-Scale Language Model Training on G** Fig.2 (p.3): Combination of tensor and pipeline model parallelism (MP) used in this work for …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.3 (p.3): GPipe pipeline schedule with forward passes (blue) for all microbatches (represe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig04.png]] — **Efficient Large-Scale Language Model Training on G** Fig.4 (p.3): Default and interleaved 1F1B pipeline schedules. The top figure shows the defaul…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.5 (p.5): Blocks of transformer model partitioned with tensor model parallelism (figures b…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.6 (p.5): Fraction of time spent idling due to pipeline flush (pipeline bubble size) versu…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig07.png]] — **Efficient Large-Scale Language Model Training on G** Fig.7 (p.6): Per-GPU throughput versus microbatch size for a GPT model with a billion paramet…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig08.png]] — **Efficient Large-Scale Language Model Training on G** Fig.8 (p.6): Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.9 (p.7): Scatter/gather communication optimization. Light blue blocks are layers in the f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.10 (p.8): Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.11 (p.9): Throughput per GPU of pipeline parallelism using two different batch sizes in a …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig12.png]] — **Efficient Large-Scale Language Model Training on G** Fig.12 (p.9): Throughput per GPU of interleaved and non-interleaved schedules for a GPT model …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig13.png]] — **Efficient Large-Scale Language Model Training on G** Fig.13 (p.9): Throughput per GPU of various parallel configurations that combine pipeline and …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig14.png]] — **Efficient Large-Scale Language Model Training on G** Fig.14 (p.10): Throughput per GPU of various parallel configurations that combine data and pipe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig15.png]] — **Efficient Large-Scale Language Model Training on G** Fig.15 (p.10): Throughput per GPU of various parallel configurations that combine data and tens…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig16.png]] — **Efficient Large-Scale Language Model Training on G** Fig.16 (p.10): Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different m…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig17.png]] — **Efficient Large-Scale Language Model Training on G** Fig.17 (p.11): Throughput (in sequences per second) with and without activation recomputation f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig18.png]] — **Efficient Large-Scale Language Model Training on G** Fig.18 (p.11): Throughput per GPU with and without the scatter/gather optimization for a GPT mo…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig01.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.1 (p.2): Model (blue) and model+data (green) parallel FLOPS as a function of number of GP…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ⭐ ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig02.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.2 (p.3): Transformer Architecture. Purple blocks correspond to fully connected layers. Ea…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ⭐ ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig03.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.3 (p.4): Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an ide…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ⭐ ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig04.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.4 (p.5): Communication operations in a transformer layer. There are 4 total communication…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ⭐ ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig05.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.5 (p.6): Model and model + data parallel weak scaling efﬁciency as a function of the numb…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ⭐ ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig06.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.6 (p.7): Validation set perplexity. All language models are trained for 300k iterations. …  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ⭐ ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig07.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.7 (p.8): Training loss for BERT model using the original architec- ture (a) and the rearr…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ⭐ ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig08.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.8 (p.12): Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig01.png]] — **Efficient Training of Large Language Models on Dis** Fig.1 (p.2): Overall structure of this survey.…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig02.png]] — **Efficient Training of Large Language Models on Dis** Fig.2 (p.3): A typical Transformer layer contains an Attention…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig03.png]] — **Efficient Training of Large Language Models on Dis** Fig.3 (p.4): Infrastructure overview for distributed LLM training.…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig04.png]] — **Efficient Training of Large Language Models on Dis** Fig.4 (p.5): Studies on infrastructure optimizations for distributed LLM training.…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig05.png]] — **Efficient Training of Large Language Models on Dis** Fig.5 (p.6): Five chip-to-chip topologies: tree topology, cube-mesh topology, switch-based fu…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig06.png]] — **Efficient Training of Large Language Models on Dis** Fig.6 (p.7): Four typical network topologies in large-scale GPU clusters: Clos topology, Drag…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig07.png]] — **Efficient Training of Large Language Models on Dis** Fig.7 (p.10): Studies on parallelism schemes for distributed LLM training.…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig08.png]] — **Efficient Training of Large Language Models on Dis** Fig.8 (p.12): An example of 3D-parallelism with data parallelism, tensor parallelism, and pipe…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig09.png]] — **Efficient Training of Large Language Models on Dis** Fig.9 (p.14): Expert parallelism. The dotted line highlights the…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig10.png]] — **Efficient Training of Large Language Models on Dis** Fig.10 (p.17): An example of RLHF. Inference process: 1 The…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig11.png]] — **Efficient Training of Large Language Models on Dis** Fig.11 (p.19): Studies on computation optimizations for distributed LLM training.…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig12.png]] — **Efficient Training of Large Language Models on Dis** Fig.12 (p.21): Studies on memory optimizations for distributed LLM training.…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig13.png]] — **Efficient Training of Large Language Models on Dis** Fig.13 (p.25): Communication traffic heatmap for InternLM-2…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig14.png]] — **Efficient Training of Large Language Models on Dis** Fig.14 (p.26): Studies on communication optimizations for distributed LLM training.…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig15.png]] — **Efficient Training of Large Language Models on Dis** Fig.15 (p.29): Studies on fault tolerance techniques for distributed LLM training.…  `[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig01.png]] — **Muon is Scalable for LLM Training** Fig.1 (p.1): Scaling up with Muon. (a) Scaling law experiments comparing Muon and Adam. Muon …  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig02.png]] — **Muon is Scalable for LLM Training** Fig.2 (p.4): Validation loss curves for AdamW (green), Muon without weight decay (red), and M…  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig03.png]] — **Muon is Scalable for LLM Training** Fig.3 (p.7): Fitted scaling law curves for Muon and AdamW optimizers.…  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig04.png]] — **Muon is Scalable for LLM Training** Fig.4 (p.10): SVD entropy of weight matrices across different training iterations. We categori…  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig05.png]] — **Muon is Scalable for LLM Training** Fig.5 (p.15): Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets…  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig06.png]] — **Muon is Scalable for LLM Training** Fig.6 (p.15): D…  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig07.png]] — **Muon is Scalable for LLM Training** Fig.7 (p.17): Training dynamics comparison between Moonlight and Moonlight-A…  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig08.png]] — **Muon is Scalable for LLM Training** Fig.8 (p.9): 6.…  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig09.png]] — **Muon is Scalable for LLM Training** Fig.9 (p.18): Distribution of singular values for each weight matrix in the attention layers. …  `[[muon-is-scalable-for-llm-training]]`
- ⭐ ![[assets/crops/muon-is-scalable-for-llm-training-fig10.png]] — **Muon is Scalable for LLM Training** Fig.10 (p.19): Distribution of singular values for each weight matrix in the feed-forward netwo…  `[[muon-is-scalable-for-llm-training]]`

## 按论文

### #1 IndexCache: Accelerating Sparse Attention via Cross-Layer In

- ⭐ Fig.1 (p.1) ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig01.png]]
  - Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50% of indexer computations while maintaining comparable performance across both long-context and reasoning tasks, deliver
- ⭐ Fig.2 (p.3) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]]
  - Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning indexer at every layer. (b) IndexCache adds a single conditional branch (red lines): F layers compute and cache fresh in
- ⭐ Fig.3 (p.8) ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig03.png]]
  - Relative speedup of IndexCache over the DSA baseline across three inference settings on the 30B model. DSA baseline is normalized to 100%.
- ⭐ Fig.4 (p.16) ![[assets/crops/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig04.png]]
  - Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.

### #2 MEDUSA: Simple LLM Inference Acceleration Framework with Mul

- ⭐ Fig.1 (p.2) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig01.png]]
  - MEDUSA introduces multiple heads on top of the last hidden states of the LLM, enabling the prediction of several sub- sequent tokens in parallel (Section 2.1.1). During inference, each head generates 
- ⭐ Fig.2 (p.3) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig02.png]]
  - Remarkably, similar ideas have also been explored in independent works like Miao et al. (2023); Spector & Re (2023), where they follow a bottom-up approach and construct the tree by merging mul- tiple
- ⭐ Fig.3 (p.7) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig03.png]]
  - Left: Speed comparison of baseline, MEDUSA-1 and MEDUSA-2 on Vicuna-7B/13B. MEDUSA-1 achieves more than 2× wall-time speedup compared to the baseline implementation while MEDUSA-2 further improves the
- ⭐ Fig.4 (p.8) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p08.png]]
  - Effectiveness of numbers of candidate tokens for decoding introduced by trees (default number of candidate token for decoding is 1 when using KV cache). Left: The acceleration rate for randomly sample
- ⭐ Fig.5 (p.5) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig05.png]]
  - 5
- ⭐ Fig.6 (p.15) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig06.png]]
  - Visualization of a sparse tree setting for MEDUSA-2 Vicuna-7B. The tree has 64 nodes representing candidate tokens and a depth of 4 which indicates 4 MEDUSA heads involved in calculation. Each node in
- ⭐ Fig.7 (p.15) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig07.png]]
  - Inference speed of various models using speculative decoding on MT-Bench. Baseline model speeds are presented by grey dotted lines for comparison. γ denotes the draft token number. E. Additional Resul
- ⭐ Fig.8 (p.16) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig08.png]]
  - Speedup of various models with MEDUSA-2. MEDUSA-2 shows significant speed improvement over all the models, while models trained with self-distillation (Zephyr-7B, Vicuna-13/33B) have weaker speedup du
- ⭐ Fig.9 (p.18) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig09.png]]
  - The figure shows the relationship between FLOP/s and Operational Intensity for all benchmarked datapoints of Llama-7B operators on A100-80GB-PCIe. The dashed lines represent the HBM bandwidth limit (1
- ⭐ Fig.10 (p.18) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig10.png]]
  - Llama-13B operators on A100-80GB-PCIe. 18
- ⭐ Fig.11 (p.19) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig11.png]]
  - Llama-33B operators on A100-80GB-PCIe. 1 10 100 1k 10k
- ⭐ Fig.12 (p.19) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig12.png]]
  - Llama-7B operators on A40. 19
- ⭐ Fig.13 (p.20) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig13.png]]
  - Llama-13B operators on A40. 1 10 100 1k 10k
- ⭐ Fig.14 (p.20) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig14.png]]
  - Llama-33B operators on A40. 20
- ⭐ Fig.15 (p.21) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig15.png]]
  - Llama-7B operators on A6000. 1 10 100 1k 10k
- ⭐ Fig.16 (p.21) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig16.png]]
  - Llama-13B operators on A6000. 21
- ⭐ Fig.17 (p.22) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig17.png]]
  - Llama-33B operators on A6000. 22
- ⭐ Fig.18 (p.23) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig18.png]]
  - FLOP/s vs. Operational Intensity of attention matrix multiplication with batch size 16. 23
- ⭐ Fig.19 (p.24) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig19.png]]
  - FLOP/s vs. Operational Intensity of attention matrix multiplication with sequence length 1024. 1 10 100 1k 10k
- ⭐ Fig.20 (p.24) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig20.png]]
  - FLOP/s vs. Operational Intensity of Linear layers. 24
- ⭐ Fig.21 (p.26) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig21.png]]
  - Simulated acceleration rate, speedup, and normalized latency ablation using different numbers of candidate tokens under the setting of batch size 1 and sequence length 1024 for Llama-7B on an A100 80G
- ⭐ Fig.22 (p.27) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig22.png]]
  - Simulated speedup with sequence length 1024 for Llama-7B. 1 16 32 48 64 80 96 112
- ⭐ Fig.23 (p.27) ![[assets/crops/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig23.png]]
  - Simulated speedup with batch size 4 for Llama-7B. 27

### #3 EAGLE-3: Scaling up Inference Acceleration of Large Language

- ⭐ Fig.1 (p.1) ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig01.png]]
  - Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target model, with the x-axis representing the data scale relative to ShareGPT.
- ⭐ Fig.2 (p.2) ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig02.png]]
  - Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1, we present comparisons with additional methods, 
- ⭐ Fig.3 (p.3) ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig03.png]]
  - Illustration of training-time test (the bottom part) and its comparison with other draft methods (the upper and middle parts). f denotes the feature, t denotes the token, and a represents the unconstr
- ⭐ Fig.4 (p.2) ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig04.png]]
  - We can address this issue by incorporating Step 1 into the training process (the bottom of Figure 3). Using this method, the benefits of increasing training data become more pronounced. We name this t
- ⭐ Fig.5 (p.4) ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig05.png]]
  - Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. l, m, and h represent the low, middle, and high-level features of the target model, respectively. e denotes 
- ⭐ Fig.6 (p.5) ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig06.png]]
  - All attention masks are diagonal, except when the original training data is used as the key. Using matrix multiplication in this case would result in significant computational waste, so we can use vec
- ⭐ Fig.7 (p.8) ![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig07.png]]
  - Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-

### #4 EAGLE: Speculative Sampling Requires Rethinking Feature Unce

- ⭐ Fig.1 (p.1) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig01.png]]
  - Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for greedy (temperature=0) settings. Speedup ratio of Medusa and Lookahead are copied from their original technical reports. W
- ⭐ Fig.2 (p.2) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig02.png]]
  - Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medusa does not guarantee lossless performance. Theref
- ⭐ Fig.3 (p.2) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig03.png]]
  - Uncertainty in feature sequences. The next fea- ture following fI is contingent on the sampling outcome and cannot be determined solely based on fI, where both “always” and “am” are possible to follow
- ⭐ Fig.4 (p.3) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig04.png]]
  - Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at tempera- ture=0, tested on MT-bench with Vicuna 7B as the original LLM. Feature&shifted-token refers t
- ⭐ Fig.5 (p.4) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig05.png]]
  - A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5. t (represented by blue blocks) denotes tokens, and f (orange blocks) signifies the features, with subscripts indicating
- ⭐ Fig.6 (p.4) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig06.png]]
  - Pipeline of EAGLE. The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, green blocks repr
- ⭐ Fig.7 (p.7) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig07.png]]
  - Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.
- ⭐ Fig.8 (p.8) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig08.png]]
  - Performance of draft models with varying inputs. The target LLM is Vicuna 7B, and the test dataset is MT-bench.
- ⭐ Fig.9 (p.12) ![[assets/crops/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-fig09.png]]
  - However, the optimal tree structure is likely context-dependent. For instance, as batch size increases and redundant computational resources decrease, a smaller tree might be preferable. Tuning the dr

### #5 EAGLE-2: Faster Inference of Language Models with Dynamic Dr

- ⭐ Fig.1 (p.1) ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig01.png]]
  - Speedup ratios of different methods at tempera- ture=1. For speculative sampling, the Vicuna series uses
- ⭐ Fig.2 (p.2) ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig02.png]]
  - Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna- 68M as the draft model. LLaMA2-Chat 7B, 13B, and LLaMA3-Instruct 8B lack suitable draft m
- ⭐ Fig.3 (p.3) ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig03.png]]
  - Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-
- ⭐ Fig.4 (p.3) ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig04.png]]
  - Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. When the query is “10+2=”, the next token is very likely to be correctly pre- dicted as “1”. However, with a static draf
- ⭐ Fig.5 (p.3) ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig05.png]]
  - Overall, the acceptance rate of draft tokens is position-dependent, with the highest acceptance rate at position P1 and the lowest at position P6. Draft tokens in the upper left side of the draft tree
- ⭐ Fig.6 (p.4) ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig06.png]]
  - Average acceptance rates for different confidence score intervals of the draft model. The red dashed line connects (0,0) and (1,1) to aid in visual assessment. The original LLM is Vicuna 7B. aspects: 
- ⭐ Fig.7 (p.5) ![[assets/crops/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-fig07.png]]
  - Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the blocks represent the value of the nodes. During the exp

### #6 BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI

- ⭐ Fig.1 (p.2) ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig01.png]]
  - Block diffusion sequentially generates blocks of tokens by performing diffusion within each block and conditioning on previous blocks. By combining strength from autoregressive and diffusion models, b
- ⭐ Fig.2 (p.6) ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig02.png]]
  - Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has 
- ⭐ Fig.3 (p.21) ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig03.png]]
  - x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3
- ⭐ Fig.4 (p.22) ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig04.png]]
  - We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customized JIT attention operation that uses significantly 
- ⭐ Fig.5 (p.23) ![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig05.png]]
  - Attention computation using FlexAttention with our proposed custom mask.
- ⭐ Fig.6 (p.26) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]]
  - Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion steps.
- ⭐ Fig.7 (p.27) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]]
  - Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3
- ⭐ Fig.8 (p.28) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]]
  - Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5

### #7 DFlash: Block Diffusion for Flash Speculative Decoding

- ⭐ Fig.1 (p.2) ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig01.png]]
  - Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the
- ⭐ Fig.2 (p.4) ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig02.png]]
  - DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s
- ⭐ Fig.3 (p.3) ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig03.png]]
  - Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.
- ⭐ Fig.4 (p.5) ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig04.png]]
  - DFlash training attention. The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens p and clean response tokens r.
- ⭐ Fig.5 (p.13) ![[assets/crops/dflash-block-diffusion-for-flash-speculative-decoding-fig05.png]]
  - The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING OF MASKED BLOCKS

### #8 DSpark: Confidence-Scheduled Speculative Decoding with Semi-

- ⭐ Fig.1 (p.4) ![[assets/crops/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-fig01.png]]
  - Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= (𝑇draft + 𝑇verify)/𝜏. Autoregressive drafters achieve high 𝜏but pay 𝑇draft ∝𝛾; parallel drafters collapse 𝑇draft to a si

### #9 JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin

- ⭐ Fig.1 (p.2) ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig01.png]]
  - End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs across math, coding, and chat benchmarks. DFlash denotes the original block-parallel drafting method, DDTree is tree-base
- ⭐ Fig.2 (p.3) ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig02.png]]
  - Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Comparing the two panels shows that reducing c substant
- ⭐ Fig.3 (p.4) ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig03.png]]
  - JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.
- ⭐ Fig.4 (p.15) ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig04.png]]
  - Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft from the same prefix (last token “We”). The causal head’s rank-1 branch (“ are told that”) is faithful: target joint Σ 
- ⭐ Fig.5 (p.18) ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig05.png]]
  - Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor plus earlier positions within its own block, but can
- ⭐ Fig.6 (p.19) ![[assets/crops/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-fig06.png]]
  - Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss, while loss is applied only to future token posit

### #10 From ATOP to ZCube: Automated Topology Optimization Pipeline

- ⭐ Fig.1 (p.1) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig01.png]]
  - ATOP search results on different GPU scales, each point representing a topology. For each scale, we label the three notable points in each plot: Best performance, Most
- ⭐ Fig.2 (p.3) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig02.png]]
  - GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excluding TP communication as it typically occurs on the intra-server network. • Expert parallelism (EP), used in mixture-of
- ⭐ Fig.3 (p.4) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig03.png]]
  - (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs topology. (b) The performance degradation of GPT-3 training after a Single ToR Fault in a 4k-GPUs topology. ZCube and Bes
- ⭐ Fig.4 (p.5) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig04.png]]
  - Overview of ATOP allows the system to explore novel topology designs automatically, not limited to variants or combinations of existing ones. It can produce high-performance asymmetric topologies, suc
- ⭐ Fig.5 (p.6) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig05.png]]
  - Examples of constructing inter-layer and intra-layer connections in ATOP. Unmentioned hyperparameters = 0.
- ⭐ Fig.6 (p.9) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig06.png]]
  - During the 4k GPUs search process: (a) The Pareto- optimal topologies generated by ATOP; (b) All the topologies generated by ATOP.
- ⭐ Fig.7 (p.9) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig07.png]]
  - (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The search results when expanding a DCN from 1k GPUs to 4k GPUs. be unfair to other topologies. However, in Case 3, even expan
- ⭐ Fig.8 (p.10) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig08.png]]
  - (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An example of ZCube(2, 3). (c) An example of ZCube(84,3)-partial. ZCube(𝑛,𝑘+ 1) is equipped with (𝑘+ 1) NIC ports numbered from
- ⭐ Fig.9 (p.11) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig09.png]]
  - The training iteration time for GPT-3 175B and MoE-GPT models and the corresponding network costs on various topologies, under different numbers of GPUs.
- ⭐ Fig.10 (p.11) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig10.png]]
  - CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 GPUs. GPU clusters, the failure probability of a single switch is 0.03%.
- ⭐ Fig.11 (p.12) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig11.png]]
  - The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G 4G 16G
- ⭐ Fig.12 (p.12) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig12.png]]
  - Collective communication performance on real- world deployment. ZCube and ROFT achieve the same all-reduce and all-to-all perfor- mance, while ZCube reduces hardware cost by 25% by using only 48×200G 
- ⭐ Fig.13 (p.15) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig13.png]]
  - In the search results of Case 3, the comparison between the number of modified links (another cost metric) and training performance.
- ⭐ Fig.14 (p.15) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig14.png]]
  - The search results of ATOP when building a new data center for multi-tenancy.
- ⭐ Fig.15 (p.15) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig15.png]]
  - The search results of ATOP when building a new heterogeneous data center with strict search space con- straints.
- ⭐ Fig.16 (p.16) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig16.png]]
  - During the ATOP optimization process: (a) The relationship between the number of Pareto-optimal topologies and the total number of topologies generated by ATOP; (b) The Jaccard distance between the Pa
- ⭐ Fig.17 (p.17) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig17.png]]
  - Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-blocking 2-layer Rail-Optimized
- ⭐ Fig.18 (p.17) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig18.png]]
  - The average JCT for group all-to-all communica- tion under different topologies with link failures on 4096 GPUs, with shading representing the standard deviation of the JCT.
- ⭐ Fig.19 (p.18) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig19.png]]
  - Comparison between packet-level network simulation (with packet spraying for load balancing) and the real-world testbed in §6.2. I
- ⭐ Fig.20 (p.19) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig20.png]]
  - Comparison of the CDF of flow completion times between NS-3 and flow-level simulators.
- ⭐ Fig.21 (p.20) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig21.png]]
  - ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.
- ⭐ Fig.22 (p.20) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig22.png]]
  - Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with [51] and [57].
- ⭐ Fig.23 (p.20) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig23.png]]
  - HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.
- ⭐ Fig.24 (p.20) ![[assets/crops/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-fig24.png]]
  - ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880

### #11 KIMI K2.5: VISUAL AGENTIC INTELLIGENCE

- ⭐ Fig.1 (p.1) ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig01.png]]
  - Kimi K2.5 main results. 1
- ⭐ Fig.2 (p.4) ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig02.png]]
  - Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve, demonstrating that zero-vision activation paired
- ⭐ Fig.3 (p.5) ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig03.png]]
  - An agent swarm has a trainable orchestrator that dynamically creates specialized frozen subagents and decomposes complex tasks into parallelizable subtasks for efficient distributed execution.
- ⭐ Fig.4 (p.6) ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig04.png]]
  - In our parallel-agent reinforcement learning environment, the training accuracy increases smoothly as train- ing progresses. At the same time, the level of parallelism during training also gradually i
- ⭐ Fig.5 (p.10) ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig05.png]]
  - Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL. compromise alleviates memory pressure, it does not fundamentally resolve the load imbalance caused by
- ⭐ Fig.6 (p.14) ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig06.png]]
  - The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the
- ⭐ Fig.7 (p.14) ![[assets/crops/kimi-k2-5-visual-agentic-intelligence-fig07.png]]
  - Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context management in BrowseComp. (60.6%) and surpassing even GPT-5.2 Pro (77.9%). Similarly, WideSearch sees a 6.3% improvement
- ⭐ Fig.8 (p.15) ![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]]
  - Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent baselines as target Item-F1 increases from 30% to 70% in WideSearch testing. rather than context truncation, allowing the sy
- ⭐ Fig.9 (p.21) ![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]]
  - Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixed vision-text token budget across vision and language tasks. Early fusion with lower vision ratios tend to yield better 
- ⭐ Fig.10 (p.23) ![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]]
  - Overview of our agentic RL framework. environments with minimal overhead. Our design prioritizes compositional modularity by integrating a suite of plug- gable components, such as a Tolset module for 
- ⭐ Fig.11 (p.28) ![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]]
  - Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth: Wukong (24 hours of continuous gameplay across 32 videos at 1080p) using parallel visual agents. See generated webpage 
- ⭐ Fig.12 (p.29) ![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]]
  - Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 29

### #12 Scalable Training of Mixture-of-Experts Models with Megatron

- ⭐ Fig.1 (p.9) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig01.png]]
  - Data flow through an MoE layer: Route, Dispatch, Compute, and Combine stages.
- ⭐ Fig.2 (p.10) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig02.png]]
  - Router architecture: linear projection, score function, top-𝑘selection, and load balancing. combine_postprocess (backward).
- ⭐ Fig.3 (p.13) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig03.png]]
  - Dense Model vs MoE Model parameter/compute scaling.
- ⭐ Fig.4 (p.15) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig04.png]]
  - Expert Parallelism (EP) distributes experts across GPUs. The all-to-all communication dispatches tokens to their assigned experts and combines results.
- ⭐ Fig.5 (p.17) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig05.png]]
  - Parallelism mappings: traditional constraints vs. MoE Parallel Folding decoupling.
- ⭐ Fig.6 (p.18) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig06.png]]
  - Parallel Folding: decoupled attention and MoE parallelism mappings.
- ⭐ Fig.7 (p.22) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig07.png]]
  - Memory-Efficient Permutation.
- ⭐ Fig.8 (p.23) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig08.png]]
  - Selective Recomputation.
- ⭐ Fig.9 (p.24) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig09.png]]
  - Fine-grained activation offloading: stream overlap for forward and backward passes.
- ⭐ Fig.10 (p.26) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig10.png]]
  - Fine-grained offloading and recomputation: complementary memory optimization strategies. optimization target. Megatron-Core provides two techniques: precision-aware optimization that reduces storage r
- ⭐ Fig.11 (p.28) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig11.png]]
  - Comparison of sharding strategies: (a) FSDP2 shards each parameter uniformly; (b) Megatron-FSDP flattens per-module and shards non-uniformly, aligning with communication buffers.
- ⭐ Fig.12 (p.28) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig12.png]]
  - Persistent double-buffer design: two pre-allocated buffers are cycled across FSDP collectives, eliminating allocation overhead and enabling NCCL User Buffer Registration.
- ⭐ Fig.13 (p.30) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig13.png]]
  - Expert parallelism across 4 GPUs with 4 experts.
- ⭐ Fig.14 (p.31) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig14.png]]
  - The dispatch kernel design of HybridEP.
- ⭐ Fig.15 (p.31) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig15.png]]
  - The combine kernel design of HybridEP.
- ⭐ Fig.16 (p.32) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig16.png]]
  - Merged FWD-FWD Timeline with all-to-all Overlapping.
- ⭐ Fig.17 (p.33) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig17.png]]
  - Merged FWD-BWD Timeline with all-to-all Overlapping.
- ⭐ Fig.18 (p.34) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig18.png]]
  - EP all-to-all communication overlap strategies: baseline vs. 1F1B with W/D split.
- ⭐ Fig.19 (p.35) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig19.png]]
  - Interleaved PP Timeline with all-to-all Overlapping.
- ⭐ Fig.20 (p.37) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig20.png]]
  - The pipeline for permute fusion in the training process. • Preprocessing: Permutation is fundamentally a data transfer process that requires tokens to be stored consecutively in the buffer correspondi
- ⭐ Fig.21 (p.38) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig21.png]]
  - The workflow of the router fusion. • Computation of MoE auxiliary loss: Building on step 2, the auxiliary loss computation is fused into a single kernel.
- ⭐ Fig.22 (p.39) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig22.png]]
  - Traditional execution (top) versus CUDA Graph execution (bottom).
- ⭐ Fig.23 (p.39) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig23.png]]
  - Full versus layer-wise CUDA Graphs in one training iteration (three layers, two microbatches).
- ⭐ Fig.24 (p.40) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig24.png]]
  - Partial CUDA Graphs capture static components (attention, shared experts, router, preprocessing) while leaving dynamic expert computation outside the graph.
- ⭐ Fig.25 (p.41) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig25.png]]
  - Transformer layer forward pass: without (upper) and with (lower) partial CUDA Graphs. CPU overhead is largely eliminated for static components.
- ⭐ Fig.26 (p.42) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig26.png]]
  - Why Pipeline Parallelism prevents CUDA Graphs from being shared across microbatches. With PP (top): Execution is interleaved—multiple forward passes run before any backward pass. If microbatches share
- ⭐ Fig.27 (p.45) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig27.png]]
  - ECHO workflow for forward and backward passes. The planner generates routing and hot expert maps. Expert Dispatch clones hot expert weights to spare slots; Expert Gradient Dispatch reduces gradients b
- ⭐ Fig.28 (p.46) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig28.png]]
  - Memory layout comparison across three execution modes. Left: Eager mode allocates memory dynamically based on actual usage. Middle: Baseline static shape requires worst-case sized buffers for each lay
- ⭐ Fig.29 (p.46) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig29.png]]
  - Paged Stashing stream overlap. Forward pass: After Layer N computes, its activations are stashed (copied from tmp buffer to paged stashing buffer) on a dedicated Pack stream while Layer N+1 computes o
- ⭐ Fig.30 (p.50) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig30.png]]
  - FP8 training recipes: Per-Tensor Scaling, Blockwise FP8, and MXFP8. A reduced-precision training recipe consists of: • Data format. There are two types of FP8 format: E4M3 and E5M2 [71, 74]. Usually t
- ⭐ Fig.31 (p.52) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig31.png]]
  - The computation of a linear layer with various FP8 recipes. Note the differences in quantization granularity and tensor layout requirements across platforms. precise due to the finer-grained scaling g
- ⭐ Fig.32 (p.53) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig32.png]]
  - FP8 primary weight quantization scheme for blockwise scaling.
- ⭐ Fig.33 (p.54) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig33.png]]
  - FP8 primary weight quantization scheme for delayed scaling and per-tensor current scaling.
- ⭐ Fig.34 (p.57) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig34.png]]
  - SDPA exhibits 𝑂(𝑠2) complexity, while MoE and the remaining attention operations exhibit 𝑂(𝑠) complexity. Therefore, SDPA dominates the computation at longer sequence lengths.
- ⭐ Fig.35 (p.59) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig35.png]]
  - Communication and computation patterns of TP and two types of CP.
- ⭐ Fig.36 (p.61) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig36.png]]
  - Unpacked vs. Packed sequences.
- ⭐ Fig.37 (p.61) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig37.png]]
  - Compute imbalance in causal attention over packed sequences. are partitioned and which CP communication group is used by attention operators, without requiring any parameter redistribution or optimize
- ⭐ Fig.38 (p.61) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig38.png]]
  - Dynamic Context Parallelism for Packed Sequences.
- ⭐ Fig.39 (p.64) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig39.png]]
  - Load balancing strategies in Megatron-Core MoE.
- ⭐ Fig.40 (p.65) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig40.png]]
  - Shared expert architecture in Megatron-Core MoE. The shared expert processes all tokens while routed experts process only their assigned tokens. When overlap is enabled, shared expert computation runs
- ⭐ Fig.41 (p.66) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig41.png]]
  - Flexible Pipeline Parallel Placement. 66
- ⭐ Fig.42 (p.67) ![[assets/crops/scalable-training-of-mixture-of-experts-models-with-megatron-core-fig42.png]]
  - An example of granular upcycling a dense layer into E2G2T2 fine-grained MoE. E2G2T2 denotes 4 experts, top 2, with half intermediate size. (1) We shard MLP weights in the intermediate dimension (4ℎ→2ℎ

### #13 Qwen3-VL Technical Report

- ⭐ Fig.1 (p.3) ![[assets/crops/qwen3-vl-technical-report-fig01.png]]
  - The Qwen3-VL framework integrates a vision encoder and a language model decoder to process multimodal inputs, including text, images, and video. The vision encoder is specifically designed to handle d
- ⭐ Fig.2 (p.17) ![[assets/crops/qwen3-vl-technical-report-fig02.png]]
  - Multilingual OCR performance of our model on a self-built test set. The model achieves over 70% accuracy on 32 out of 39 supported languages, demonstrating strong and usable multilingual capabilities.
- ⭐ Fig.3 (p.25) ![[assets/crops/qwen3-vl-technical-report-fig03.png]]
  - Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across varying video durations and needle positions. Each cell shows accuracy (%) for locating and answering questions about th

### #14 DeepStack: Deeply Stacking Visual Tokens is Surprisingly Sim

- ⭐ Fig.1 (p.1) ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig01.png]]
  - Left: Conventional large multimodal models (LMMs) string all visual tokens into a sequence for high- and low-resolution images. Middle: Our DeepStack LMMs stack the tokens into a grid and infuse them 
- ⭐ Fig.2 (p.4) ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig02.png]]
  - Architecture of DeepStack. The main innovation lies in the DeepStack strategy that infuses visual tokens into different layers. Left: DeepStack for LLMs. Given an input image, we feed the tokens extra
- ⭐ Fig.3 (p.8) ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig03.png]]
  - Analysis on using LLM layers to process visual tokens. (a) We insert the visual tokens into different starting layers and initialize the correspondence input embeddings as zero; (b) We fix the first l
- ⭐ Fig.4 (p.10) ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig04.png]]
  - Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison.
- ⭐ Fig.5 (p.9) ![[assets/crops/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-fig05.png]]
  - Visualization of three sam- pling methods for DeepStack.

### #15 昇腾 950 NPU 架构白皮书

- ⭐ Fig.301 (p.12) ![[assets/crops/ascend-950-npu-architecture-whitepaper-fig301.png]]
  - 昇腾950 芯片架构示意图
- Fig.401 (p.17) ![[assets/ascend-950-npu-architecture-whitepaper-p17.png]]
  - AI Core 架构及各层级SRAM 示意图
- Fig.402 (p.18) ![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]
  - Cube Core 处理架构示意图
- ⭐ Fig.403 (p.18) ![[assets/crops/ascend-950-npu-architecture-whitepaper-fig403.png]]
  - Cube Core 支持的数值精度示意
- Fig.404 (p.19) ![[assets/ascend-950-npu-architecture-whitepaper-p19.png]]
  - HiF8 数值精度
- Fig.405 (p.21) ![[assets/ascend-950-npu-architecture-whitepaper-p21.png]]
  - Vector Core 架构示意图
- ⭐ Fig.406 (p.22) ![[assets/crops/ascend-950-npu-architecture-whitepaper-fig406.png]]
  - AI Core Cube-Vector 融合示意图
- Fig.407 (p.23) ![[assets/ascend-950-npu-architecture-whitepaper-p23.png]]
  - NDDMA 指令
- Fig.408 (p.24) ![[assets/ascend-950-npu-architecture-whitepaper-p24.png]]
  - 昇腾950 新同步机制代码示例
- ⭐ Fig.409 (p.25) ![[assets/crops/ascend-950-npu-architecture-whitepaper-fig409.png]]
  - 昇腾950 内存层次示意图
- Fig.410 (p.27) ![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]
  - Non-allocate（L2 hint）典型应用场景示意图
- ⭐ Fig.411 (p.27) ![[assets/crops/ascend-950-npu-architecture-whitepaper-fig411.png]]
  - STARS2.0 架构示意图
- Fig.412 (p.31) ![[assets/ascend-950-npu-architecture-whitepaper-p31.png]]
  - URMA 异步访存通信的过程示意图
- Fig.413 (p.32) ![[assets/ascend-950-npu-architecture-whitepaper-p32.png]]
  - UB Memory 同步访存语义地址通信过程示意图
- Fig.414 (p.33) ![[assets/ascend-950-npu-architecture-whitepaper-p33.png]]
  - CCU 架构示意图
- Fig.415 (p.34) ![[assets/ascend-950-npu-architecture-whitepaper-p34.png]]
  - UB On Chip Switch 转发示意图
- Fig.416 (p.35) ![[assets/ascend-950-npu-architecture-whitepaper-p35.png]]
  - PCIe 5.0 架构示意图
- ⭐ Fig.417 (p.36) ![[assets/crops/ascend-950-npu-architecture-whitepaper-fig417.png]]
  - 昇腾950 的一种超节点示意图
- ⭐ Fig.418 (p.36) ![[assets/crops/ascend-950-npu-architecture-whitepaper-fig418.png]]
  - 昇腾950 访问CPU 超大内存池示意图
- Fig.419 (p.37) ![[assets/ascend-950-npu-architecture-whitepaper-p37.png]]
  - 昇腾950 直接访问超大存储资源池示意图
- Fig.420 (p.38) ![[assets/ascend-950-npu-architecture-whitepaper-p38.png]]
  - 昇腾超节点基于UB Switch 转换为以太网与以太世界互通示意图
- Fig.421 (p.39) ![[assets/ascend-950-npu-architecture-whitepaper-p39.png]]
  - 昇腾芯片支持以太网与以太世界互通示意图

### #16 GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM

- ⭐ Fig.1 (p.1) ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig01.png]]
  - A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As more rollouts are sampled, the prompt optimizers can
- ⭐ Fig.2 (p.3) ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig02.png]]
  - This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, along with the seed prompt it started with. Appendix 
- ⭐ Fig.3 (p.5) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]]
  - GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section 3) or System Aware Merge (Appendix D.1)), first e
- ⭐ Fig.4 (p.4) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]]
  - GEPA receives the following inputs: A system  instan- tiated with simple prompts to be optimized, training dataset D train (consisting of task instances (x; m) as described in Section 2), the standar
- ⭐ Fig.5 (p.7) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]]
  - GEPA’s reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure visualizes the optimization trajectory taken by GEP
- ⭐ Fig.6 (p.10) ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig06.png]]
  - Comparing the impact of different candidate selection strategies. (Left) As can be seen, selecting the best-performing candidate in every iteration led to a local-optima after one iteration, leading t
- ⭐ Fig.7 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequ
- ⭐ Fig.8 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast p vs. rollouts plot for p=[0:5; 1], where the speedup is calculated over Pytorch-eager. fast p is a m
- ⭐ Fig.9 (p.24) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]]
  - Details of System Aware Merge. r represents a seeded stochastic sampler.
- ⭐ Fig.10 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - Final test set performance for aggregate and individual benchmarks.
- ⭐ Fig.11 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetun- ing on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against G
- ⭐ Fig.12 (p.29) ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig12.png]]
  - Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO 0 50 10 150 20 250
- ⭐ Fig.13 (p.29) ![[assets/crops/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-fig13.png]]
  - IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- ⭐ Fig.14 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- ⭐ Fig.15 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - PUPA: rollout vs. score for different models/settings. 29
- ⭐ Fig.16 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between final test set performance and the best achieved 
- ⭐ Fig.17 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - These plots visualize the final aggregate scores against the aggregate prompt size (across all benchmarks) of the final optimized system for each optimizer. It can be seen that GEPA consistently pro- 
- ⭐ Fig.18 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - Comparing the token counts of optimized programs across benchmarks. (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- ⭐ Fig.19 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - HotpotQA GPT-4.1 Mini 31
- ⭐ Fig.20 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- ⭐ Fig.21 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)
- ⭐ Fig.22 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench Qwen3 8B 32
- ⭐ Fig.23 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- ⭐ Fig.24 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- ⭐ Fig.25 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - PUPA GPT-4.1 Mini 33
- ⭐ Fig.26 (p.34) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]]
  - PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA
- ⭐ Fig.27 (p.12) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]]
  - We also note that generation stochasticity (temperature based sampling) is eliminated by operating under a cache; this ensures that ob- served improvements tie closely to inference scaling through pro

### #17 SARATHI: Efficient LLM Inference by Piggybacking Decodes wit

- ⭐ Fig.1 (p.1) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig01.png]]
  - Example two-stage pipeline parallel schedule. (a)
- ⭐ Fig.2 (p.3) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig02.png]]
  - High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’s embedding size (e.g., 5120 for LLaMA-13B).
- ⭐ Fig.3 (p.4) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig03.png]]
  - Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even at batch size of 1 and results in almost constant p
- ⭐ Fig.4 (p.4) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig04.png]]
  - Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU. operations. Figure 4b shows the arithmetic intensity of each operation separatel
- ⭐ Fig.5 (p.5) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig05.png]]
  - Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times. set of layers; 
- ⭐ Fig.6 (p.6) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig06.png]]
  - Example of how attention mask is set across dif- ferent chunk prefill iterations in SARATHI (q and k represent “query" and “key" tokens, respectively). The attention mask for v (“values") is set simil
- ⭐ Fig.7 (p.7) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig07.png]]
  - The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU. maximal batching with that of the baseline scheme that com- putes prefill and decode iterations separately. W
- ⭐ Fig.8 (p.9) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig08.png]]
  - Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).
- ⭐ Fig.9 (p.10) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig09.png]]
  - Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequence lengths, P:D ratios, and chunk sizes. 2 4 6 8 10 12 14 16 18
- ⭐ Fig.10 (p.10) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig10.png]]
  - Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk sizes of 256 (top half) and 512 (bottom half). Orang
- ⭐ Fig.11 (p.11) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig11.png]]
  - Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. configuration of sequence length and chunk size, we show the effect of varying batch sizes. Further, for each run, we also sh
- ⭐ Fig.12 (p.12) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig12.png]]
  - Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation. the effect of variable sequence lengths on request latencies.
- ⭐ Fig.13 (p.13) ![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig13.png]]
  - Ablation study: Effect of varying the chunk size on different components of the system for LLaMa 13B on A6000 GPU. measure the time to compute the prefill phase for various se- quence lengths using th

### #18 Taming Throughput-Latency Tradeoff in LLM Inference with Sar

- ⭐ Fig.1 (p.1) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig01.png]]
  - Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation trace. 1a highlights one of the many generation stalls lasting over several seconds in vLLM [53]. 1b shows the impact of i
- ⭐ Fig.2 (p.2) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig02.png]]
  - Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens
- ⭐ Fig.3 (p.5) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig03.png]]
  - Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that diff
- ⭐ Fig.4 (p.5) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig04.png]]
  - Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arit
- ⭐ Fig.5 (p.6) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig05.png]]
  - Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different number of token running on four A100s. Decode batches have low arithmetic intensity i.e., they are bottlenecked by memory f
- ⭐ Fig.6 (p.6) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig06.png]]
  - Linear layer execution time as function of number of tokens in a batch for LLaMA2-70B on A100(s) with different tensor parallel degrees. When the number of tokens is small, execution time is dictated 
- ⭐ Fig.7 (p.6) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig07.png]]
  - A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Sub- script d represents a decode i
- ⭐ Fig.8 (p.7) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig08.png]]
  - A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times.
- ⭐ Fig.9 (p.8) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig09.png]]
  - The incremental cost of coalescing prefills with decode batches. We consider two batching schemes – (i) Decode +
- ⭐ Fig.10 (p.11) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig10.png]]
  - Capacity (in queries per second) of Mistral-7B and
- ⭐ Fig.11 (p.11) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig11.png]]
  - Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with different schedulers under strict (SLO-S) and relaxed (SLO-R) latency SLOs.
- ⭐ Fig.12 (p.12) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig12.png]]
  - Latency – Throughput tradeoff in vLLM and
- ⭐ Fig.13 (p.12) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig13.png]]
  - TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP within node and PP across nodes. (b) Capacity under str
- ⭐ Fig.14 (p.13) ![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig14.png]]
  - Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using chunk lengths of 512, 1024 and 2048.

### #20 DeepSeek-V4: Towards Highly Efficient Million-Token Context 

- ⭐ Fig.1 (p.14) ![[assets/crops/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-fig01.png]]
  - 2.4. Muon Optimizer
- ⭐ Fig.5 (p.15) ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]]
  - This forms a fine-grained pipeline among experts, keeping both computation and communication continuous throughout the wave. The wave-based scheduling speeds up the 15

### #21 KIMI-VL TECHNICAL REPORT

- ⭐ Fig.1 (p.1) ![[assets/crops/kimi-vl-technical-report-fig01.png]]
  - Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, including short-thinking VLMs (e.g. Gemma-3 series, Qwen2.5-VL series) and long-thinking VLMs (QVQ-72B/Max-Preview), on MathVisi
- ⭐ Fig.2 (p.2) ![[assets/crops/kimi-vl-technical-report-fig02.png]]
  - Highlights of Kimi-VL performance for a wide range of benchmarks like, general benchmarks (MMMU, MMBench), OCR (InfoVQA), multi-image (BLINK), long video (LongVideoBench, Video-MME), long document (MM
- ⭐ Fig.3 (p.3) ![[assets/crops/kimi-vl-technical-report-fig03.png]]
  - The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT that allows native- resolution images, an MLP projector, and a Mixture-of-Experts (MoE) language decoder. 1) Kimi-VL is 
- ⭐ Fig.4 (p.4) ![[assets/crops/kimi-vl-technical-report-fig04.png]]
  - The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-only pre-training of its language model. To preserve text abilities, all stages that update the language model are joint tr
- ⭐ Fig.5 (p.6) ![[assets/crops/kimi-vl-technical-report-fig05.png]]
  - The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages of joint SFT in 32K and 128K context, and further long-CoT SFT and RL stages to activate and enhance long thinking abilit
- ⭐ Fig.6 (p.8) ![[assets/crops/kimi-vl-technical-report-fig06.png]]
  - Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to perform historical and scientific inference by analyzing handwritten manuscripts step by step. In this example, our mod
- ⭐ Fig.7 (p.12) ![[assets/crops/kimi-vl-technical-report-fig07.png]]
  - Kimi-VL exhibits strong visual reasoning capabilities by grounding visual content in spatial, contextual, and cultural knowledge. It accurately identifies matching urban locations based on structural 
- ⭐ Fig.8 (p.13) ![[assets/crops/kimi-vl-technical-report-fig08.png]]
  - Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric inference by solving a circle geometry problem step by step. The model analyzes given conditions, applies geometric theo
- ⭐ Fig.9 (p.14) ![[assets/crops/kimi-vl-technical-report-fig09.png]]
  - Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across varied content types, including structured financial tables, complex mathematical formulas, and handwritten Chinese text.
- ⭐ Fig.10 (p.15) ![[assets/crops/kimi-vl-technical-report-fig10.png]]
  - Kimi-VL is capable of following multi-step reasoning processes to complete complex GUI tasks. In this example, it successfully enables the “Do Not Track” feature in the Chrome browser to enhance onlin
- ⭐ Fig.11 (p.16) ![[assets/crops/kimi-vl-technical-report-fig11.png]]
  - Video scene splitting. Kimi-VL processes a long-form video by segmenting it into coherent scenes and providing detailed start/end timestamps along with fine-grained natural language descriptions for e
- ⭐ Fig.12 (p.17) ![[assets/crops/kimi-vl-technical-report-fig12.png]]
  - Catching and understanding key details from an hour-long video course. Kimi-VL demonstrates its ability to comprehend and interpret instructional video content by analyzing frame sequences and extract
- ⭐ Fig.13 (p.16) ![[assets/crops/kimi-vl-technical-report-fig13.png]]
  - Specifically, increasing the max thinking token length at inference time consistently improves test-time accuracy across all three 16

### #22 DeepSeekMath: Pushing the Limits of Mathematical Reasoning i

- ⭐ Fig.1 (p.1) ![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig01.png]]
  - Top1 accuracy of open-source models on the competition-level MATH benchmark
- ⭐ Fig.2 (p.5) ![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig02.png]]
  - An iterative pipeline that collects mathematical web pages from Common Crawl.
- ⭐ Fig.3 (p.7) ![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig03.png]]
  - Benchmark curves of DeepSeek-LLM 1.3B trained on different mathematical corpora.
- ⭐ Fig.4 (p.13) ![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig04.png]]
  - Demonstration of PPO and our GRPO. GRPO foregoes the value model, instead
- ⭐ Fig.5 (p.19) ![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig05.png]]
  - Performance of the DeepSeekMath-Instruct 1.3B model, which was further trained
- ⭐ Fig.6 (p.20) ![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig06.png]]
  - Performance of iterative reinforcement learning with DeepSeekMath-Instruct 7B on
- ⭐ Fig.7 (p.21) ![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig07.png]]
  - The Maj@K and Pass@K of SFT and RL DeepSeekMath 7B on GSM8K and MATH

### #23 High-Dimensional Continuous Control Using Generalized Advant

- ⭐ Fig.1 (p.8) ![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig01.png]]
  - 6.2.1 ARCHITECTURE
- ⭐ Fig.2 (p.10) ![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig02.png]]
  - Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement is obtain by intermediate values of λ in the range
- ⭐ Fig.3 (p.10) ![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig03.png]]
  - Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algo- rithm. Right: learning curves for 3D quadrupedal locomotion, averaged across ﬁve runs.
- ⭐ Fig.4 (p.11) ![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig04.png]]
  - (a) Learning curve from quadrupedal walking, (b) learning curve for 3D standing up, (c) clips from 3D standing up. 7 DISCUSSION

### #24 KIMI K2: OPEN AGENTIC INTELLIGENCE

- ⭐ Fig.1 (p.1) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig01.png]]
  - Kimi K2 main results.2 1https://huggingface.co/moonshotai/Kimi-K2-Instruct 2All models evaluated above are non-thinking models. For SWE-bench Multilingual, we evaluated only Claude 4 Sonnet because th
- ⭐ Fig.2 (p.4) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig02.png]]
  - Left: During a mid-scale training run, attention logits rapidly exceed 1000, which could lead to potential numerical instabilities and even training divergence. Right: Maximum logits for Kimi K2 with 
- ⭐ Fig.3 (p.5) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig03.png]]
  - Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we omit the very beginning of training for clarity. A k
- ⭐ Fig.4 (p.5) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig04.png]]
  - • Fidelity verification: To ensure consistency between original and rewritten content, we perform fidelity checks that compare the semantic alignment of each rephrased passage with its source. This se
- ⭐ Fig.5 (p.7) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig05.png]]
  - Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared experts to 1, and varied the total number of exper
- ⭐ Fig.6 (p.7) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig06.png]]
  - Scaling curves for models with number of atten- tion heads equals to number of layers and their counter- parts with doubled attention heads. Doubling the number of attention heads leads to a reduction
- ⭐ Fig.7 (p.8) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig07.png]]
  - Computation, communication and offloading overlapped in different PP phases.
- ⭐ Fig.8 (p.10) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig08.png]]
  - Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (b) Multi-agent pipeline to generate and filter tra
- ⭐ Fig.9 (p.10) ![[assets/crops/kimi-k2-open-agentic-intelligence-fig09.png]]
  - t-SNE visualizations of tool embeddings. (a) Real-world MCP tools exhibit natural clustering based on their original source categories. (b) Synthetic tools are organized into pre-defined domain catego
- ⭐ Fig.10 (p.14) ![[assets/kimi-k2-open-agentic-intelligence-p14.png]]
  - Parameter update utilizing a checkpoint engine
- ⭐ Fig.11 (p.29) ![[assets/kimi-k2-open-agentic-intelligence-p29.png]]
  - Chinese in-house benchmark evaluation. rate, i.e. 98.9. On FaithJudge’s RAG tasks the hallucination rate is 7.4 %, likewise present as 92.6 for table consistency.
- ⭐ Fig.12 (p.30) ![[assets/kimi-k2-open-agentic-intelligence-p30.png]]
  - Applying QK-Clip to Muon in a small-scale setting with an aggresive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logit
- ⭐ Fig.13 (p.32) ![[assets/kimi-k2-open-agentic-intelligence-p32.png]]
  - pipeline for RL weight update

### #25 Search-R1: Training LLMs to Reason and Leverage Search Engin

- ⭐ Fig.1 (p.4) ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig01.png]]
  - Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).
- ⭐ Fig.2 (p.9) ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig02.png]]
  - (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Bas
- ⭐ Fig.3 (p.17) ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig03.png]]
  - Retrieved Token Loss Masking Study instruction-tuned models exhibit faster convergence and benefit from higher initial perfor- mance relative to their base counterparts. Despite this early advantage, 
- ⭐ Fig.4 (p.17) ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig04.png]]
  - Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final performance of both models is very similar. F
- ⭐ Fig.5 (p.18) ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig05.png]]
  - Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO pr
- ⭐ Fig.6 (p.19) ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig06.png]]
  - The training dynamics of SEARCH-R1 with a different number of retrieved pas- sages. (LLM: Qwen2.5-7b-base, RL: PPO)
- ⭐ Fig.7 (p.19) ![[assets/crops/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-fig07.png]]
  - We observe that a larger group size generally leads to faster convergence but may also increase the risk of collapse due to the inherent instability of reinforcement learning.

### #26 HYPER-CONNECTIONS

- ⭐ Fig.1 (p.1) ![[assets/crops/hyper-connections-fig01.png]]
  - The performance of the baseline model OLMoE-1B-7B and the model with hyper- connections, OLMoE-1B-7B-DHC×4. (1) and (2) show the training loss (0.99 EMA smoothed) and the C4-en validation loss, respec
- ⭐ Fig.2 (p.2) ![[assets/crops/hyper-connections-fig02.png]]
  - Hyper-connections (HC) with an expansion rate of n = 2. (a) Residual connections. (b) Hyper-connections: β1, β2, α0,0, α0,1, α1,0, α1,1, α2,1, and α2,2 are learnable scalars or scalars predicted by th
- ⭐ Fig.3 (p.2) ![[assets/crops/hyper-connections-fig03.png]]
  - Cosine similarity be- tween the input of the current and the previous layers for the OLMo-1B models (Groeneveld et al., 2024). The curve represents the median of similarity, while the shaded area indi
- ⭐ Fig.4 (p.5) ![[assets/crops/hyper-connections-fig04.png]]
  - Sequential and parallel arrangements of hyper-connections with n = 2.
- ⭐ Fig.5 (p.6) ![[assets/crops/hyper-connections-fig05.png]]
  - Comparison of training loss curves for different expansion rate. The left subfigure includes models with dynamic hyper-connections (DHC) at various expansion rates, while the right subfigure shows the
- ⭐ Fig.6 (p.8) ![[assets/crops/hyper-connections-fig06.png]]
  - (1) and (2) Training loss (0.99 EMA smoothed) and C4-en validation loss for OLMo-7B and OLMo-7B-DHC×4 models. (3) and (4) Accuracy curves on hellaswag and sciq, demonstrating the superior performance 
- ⭐ Fig.7 (p.9) ![[assets/crops/hyper-connections-fig07.png]]
  - Visualization of connection matrices for hyper-connections and various related baseline methods. The attention layers, which have odd ids, are marked with green tick marks.
- ⭐ Fig.8 (p.14) ![[assets/crops/hyper-connections-fig08.png]]
  - Comparison between transformers with hyper-connections and that with residual connec- tions. 14
- ⭐ Fig.9 (p.17) ![[assets/crops/hyper-connections-fig09.png]]
  - Loss curves in V3 validation sets and accuracy curves on downstream tasks for OLMoE-1B7B and OLMoE-1B7B-DHC×4 models. 17
- ⭐ Fig.10 (p.18) ![[assets/crops/hyper-connections-fig10.png]]
  - Loss curves in V3 validation set and accuracy curves on downstream tasks for OLMo-7B and OLMo-7B-DHC×4 models. 18
- ⭐ Fig.11 (p.20) ![[assets/crops/hyper-connections-fig11.png]]
  - Training loss curves of ViT/16-Large and ViT/16-Large-DHC×2, smoothed using an
- ⭐ Fig.12 (p.21) ![[assets/crops/hyper-connections-fig12.png]]
  - Distribution of weights of last DHC in ViT-Base/16-DHC×2 model. F MORE VISUALIZATION AND ANALYSIS
- ⭐ Fig.13 (p.22) ![[assets/crops/hyper-connections-fig13.png]]
  - Visualization of unfolded connection matrix.
- ⭐ Fig.14 (p.23) ![[assets/crops/hyper-connections-fig14.png]]
  - Comparison of unfolded connection matrices for OLMo-1B-DHC×1, OLMo-1B-DHC×2 and OLMo-1B-DHC×4 model.
- ⭐ Fig.15 (p.31) ![[assets/crops/hyper-connections-fig15.png]]
  - Training loss curves of related works, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99. 31
- ⭐ Fig.16 (p.32) ![[assets/crops/hyper-connections-fig16.png]]
  - Training loss curves of DHC with tanh over 500 billion tokens, smoothed using
- ⭐ Fig.17 (p.32) ![[assets/crops/hyper-connections-fig17.png]]
  - Training loss curves of DHC without tanh over 500 billion tokens, smoothed using
- ⭐ Fig.18 (p.33) ![[assets/crops/hyper-connections-fig18.png]]
  - Training loss curves comparied with parallel transformer blocks (PTB), smoothed using

### #27 BERTopic: Neural topic modeling with a class-based TF-IDF pr

- ⭐ Fig.1 (p.7) ![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-fig01.png]]
  - Computation time (wall time) in seconds of each topic model on the Trump dataset. Increasing sizes of vocabularies were regulated through selection of documents ranging from 1000 documents until 43000

### #28 Dual-Head Reasoning Distillation: Improving Classifier Accur

- ⭐ Fig.1 (p.2) ![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig01.png]]
  - SuperGLUE per-task scores for four backbones. DHRD (train-time reasoning) consistently beats the pooled-classifier baseline and rivals teacher model Gemini 2.5 Flash, with the largest gains on CB/COPA
- ⭐ Fig.2 (p.3) ![[assets/crops/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-fig02.png]]
  - Dual-head fine-tuning on a shared decoder. The classification head pools hidden states over the input span (blue) to produce K class logits. The train-only reasoning head applies a causal LM loss over

### #29 Dynamic Large Concept Models: Latent Reasoning in an Adaptiv

- ⭐ Fig.1 (p.4) ![[assets/crops/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-fig01.png]]
  - 3.1
- ⭐ Fig.9 (p.7) ![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p07.png]]
  - 4.3

### #30 HybridFlow: A Flexible and Efficient RLHF Framework

- ⭐ Fig.1 (p.3) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig01.png]]
  - Dataflow graph of 3 RLHF algorithms [19, 43, 55].
- ⭐ Fig.2 (p.3) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig02.png]]
  - Programming model used in RLHF systems. (a)
- ⭐ Fig.3 (p.4) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig03.png]]
  - Dataflow execution given a model placement plan.
- ⭐ Fig.4 (p.6) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig04.png]]
  - Architecture of HybridFlow. 3D-HybridEngine and Auto-Mapping algorithm. The hybrid programming model includes a set of hierarchical APIs to enable flexible expression of the RLHF dataflow and effi- ci
- ⭐ Fig.5 (p.6) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig05.png]]
  - An illustration of hierarchical APIs. (a) Model with 3D parallel configuration, resource allocation, and 3DParallelWorker initialization. (b) Asynchronous data re- sharding between two models with col
- ⭐ Fig.6 (p.7) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig06.png]]
  - Implementation of PPO [55], ReMax [43], and Safe- RLHF [19]. Users can adapt to different RLHF algorithms by simply adding or deleting a few lines of code. our programming model, HybridFlow is flexibl
- ⭐ Fig.7 (p.8) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig07.png]]
  - 3D-HybridEngine workflow in one RLHF iteration. 4 GPUs are used for actor training and generation. 1-2-2 (𝑝-𝑡-𝑑) parallel groups are used in training and 1-1-2-2 (𝑝𝑔- 𝑡𝑔-𝑑𝑔-𝑑) parallel groups are used
- ⭐ Fig.8 (p.8) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig08.png]]
  - Model weights resharding. 2 machines each with 4 GPUs are used for actor training and generation. model parameters updated in iteration 𝑖(step 1○in Figure 7), for generation within each micro DP group
- ⭐ Fig.9 (p.11) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig09.png]]
  - PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines. 8 16 32 64 128 # of GPUs 0 1 2 3
- ⭐ Fig.10 (p.11) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
  - ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines 8 16 32 64 128 # of GPUs 0 1 2 3
- ⭐ Fig.11 (p.11) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
  - Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines reward models. Each model is a Llama [73] model with sizes ranging from 7B to 70B. Safe-RLHF has an
- ⭐ Fig.12 (p.12) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig12.png]]
  - Throughput of HybridFlow under different placements 32 64 96 128 # of GPUs
- ⭐ Fig.13 (p.12) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig13.png]]
  - Placement comparison under 13B actor and reference policy & 70B critic and reward model.
- ⭐ Fig.14 (p.13) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig14.png]]
  - Transition time between actor training and generation.
- ⭐ Fig.15 (p.13) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig15.png]]
  - Time breakdown on different generation parallel sizes of the actor model on 16 GPUs. various model scales, which is the time to reshard model weights from training to generation, under the same settin
- ⭐ Fig.16 (p.13) ![[assets/crops/hybridflow-a-flexible-and-efficient-rlhf-framework-fig16.png]]
  - Runtime of device mapping algorithm. The model size and # of GPUs are simultaneously scaled.

### #31 Let It Flow: Agentic Crafting on Rock and Roll

- ⭐ Fig.1 (p.1) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig01.png]]
  - Overview of the Agentic Learning Ecosystem (ALE) and ROME Performance. 1[cs.AI] 12 Mar 2026
- ⭐ Fig.2 (p.4) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig02.png]]
  - The overview of agentic RL ecosystem (a) and its training pipeline (b). technical stack, ALE is also a call to reframe the community’s priorities. In complex agentic settings, the central challenge is
- ⭐ Fig.3 (p.5) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig03.png]]
  - ROLL Architecture. (a) ROLL pipelines LLM generation, environment interaction, and reward phases at trajectory-level granularity. Training is also decoupled via a sample buffer using an asyn- chronous
- ⭐ Fig.4 (p.6) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig04.png]]
  - ROCK System Architecture.
- ⭐ Fig.5 (p.8) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig05.png]]
  - The overview of iFlow CLI architecture and execution. these requests already contain the complete historical context, fully orchestrated by the iFlow CLI. The proxy then forwards these requests to the
- ⭐ Fig.6 (p.10) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig06.png]]
  - Overview of data sources and composition pipelines for training agentic models, spanning code centric basic data and agentic data. 3
- ⭐ Fig.7 (p.16) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig07.png]]
  - Overview of ROME’s Training Pipeline. incidents. Finally, we generated corresponding golden trajectories devoid of general-security issues for subsequent post-training (e.g., SFT and RL). Our overarch
- ⭐ Fig.8 (p.20) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig08.png]]
  - Overview of the Proposed Interaction-Perceptive Agentic Policy Optimization (IPA) training pipeline. sample efficiency(§3.2.4.4). An overview of our framework, including its key components and data fl
- ⭐ Fig.9 (p.22) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig09.png]]
  - Comparison of importance sampling strategies across token-level, chunk-level, and sentence- level granularities, where chunk-level aligns with the natural granularity of interactions.
- ⭐ Fig.10 (p.23) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig10.png]]
  - Comparison of Chunk-Level Optimization and baseline on a mini-set of the training data. Left:
- ⭐ Fig.11 (p.24) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig11.png]]
  - Illustration of the Chunk-Level Initialized Resampling Strategy (Sequential Rollback). Left: In challenging tasks, sampling high-quality trajectories from the beginning is difficult, severely limiting
- ⭐ Fig.12 (p.25) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig12.png]]
  - Performance of Sequential Rollback and baseline (naive sampling) on a challenging training task. Left: Average success rate during training, which reflects the percentage of positive signals in traini
- ⭐ Fig.13 (p.26) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig13.png]]
  - Comparison of IPA with & without Chunk-Level Initialized Resampling (Parallelized Initial- ization) on a mini-set of the training data. Left: Average success rate on training tasks. The gap between cu
- ⭐ Fig.14 (p.27) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig14.png]]
  - Benchmark characterization and cross-benchmark comparison of Terminal Bench Pro against other benchmarks.
- ⭐ Fig.15 (p.28) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig15.png]]
  - Performance-parameter trade-offs in agentic tasks. Scores represent averages on general agentic and code agent benchmarks. Models with known parameters are shown as circles, while proprietary models w
- ⭐ Fig.16 (p.34) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig16.png]]
  - Pairwise win-rate matrix (%) on the 100-task real-world benchmark under 30-expert blinded majority voting. Each cell reports the percentage of tasks where the row model is judged better than the col- 
- ⭐ Fig.17 (p.36) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig17.png]]
  - Case study 1 screenshot examples: Sleep Management System Generation. 36
- ⭐ Fig.18 (p.37) ![[assets/crops/let-it-flow-agentic-crafting-on-rock-and-roll-fig18.png]]
  - Case study 2 screenshot examples: Solar System Modeling. 37

### #32 Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with

- ⭐ Fig.1 (p.1) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig01.png]]
  - (Left) Asynchronous RL brings substantial improvements: Through RL training, our agent, ASearcher-Web-QwQ, obtains +15.0, +22.4, and +15.6 improvements on GAIA, xBench, and
- ⭐ Fig.2 (p.3) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig02.png]]
  - Comparison between ASearcher and Search-R1. (Left) Search-R1 is only equipped with search tools and lacks web browsing capability. (Right) ASearcher utilizes a simple agent design with two basic tools
- ⭐ Fig.3 (p.4) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig03.png]]
  - A case study on a complex query from GAIA. Search-R1-32B is unable to break down the complex question and has severe hallucinations. Search-o1 (QwQ) can identify the corrects articles through extensiv
- ⭐ Fig.4 (p.7) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig04.png]]
  - Data Synthesis Agent. Starting from a seed QA, the data synthesis agent iteratively modifies the question through two actions, Injection and Fuzz. Through injection, the agent enriches the question by
- ⭐ Fig.5 (p.7) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig05.png]]
  - Statistics from our data synthesis process. (Left) The distribution of the number of supporting facts. (Middle) The distribution of the number of fuzz actions and injection actions. (Right) The accura
- ⭐ Fig.6 (p.9) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig06.png]]
  - (Left) Test scaling of ASearcher-Web-QwQ. Data points are obtained by enforcing different minimum turns.The accuracy is averaged over GAIA, xBench-DeepSearch, and Frames. (Middle)
- ⭐ Fig.7 (p.10) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig07.png]]
  - One-Step-off RL v.s. Fully Asynchronous RL. In batch generation systems, a batch should wait for the longest trajectory, leading to significant GPU idle time. In contrast, fully asynchronous RL achiev
- ⭐ Fig.8 (p.14) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig08.png]]
  - Comparison of the performance of QwQ-32B agent before and after RL Training. training pipeline trains the agent to learn complex search strategies to perform precise searches, extract key information,
- ⭐ Fig.9 (p.15) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig09.png]]
  - Training Dynamics of ASearcher-Local-7B.
- ⭐ Fig.10 (p.15) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig10.png]]
  - Training Dynamics of ASearcher-Local-14B. 15
- ⭐ Fig.11 (p.16) ![[assets/crops/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-fig11.png]]
  - Left: Word count of reflective keywords during training time. Right: Word count of keywords indicating explicit reference of external information. sophisticated prompt-based agents powered by Large Re
- Fig.12 (p.20) ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p20.png]]
  - A case study on a complex query from GAIA. Search-R1-32B is unable to break down the complex question and has severe hallucinations. Search-o1 (QwQ) can identify the corrects articles through extensiv

### #33 AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys

- ⭐ Fig.1 (p.4) ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig01.png]]
  - Execution timeline of a synchronous (left) and a one-step overlap (right) RL system showing underutilized inference devices. … Rollout Controller Reward Service
- ⭐ Fig.2 (p.4) ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig02.png]]
  - The AREAL architecture featuring asynchronous generation and training components.
- ⭐ Fig.3 (p.4) ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig03.png]]
  - Illustration of generation management in AREAL. Vertical lines show the ready time for the next step training. Blue crosses show the interrupted requests when new parameters arrive. 4
- ⭐ Fig.4 (p.8) ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig04.png]]
  - The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so the data points are missing. 8
- ⭐ Fig.5 (p.9) ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig05.png]]
  - Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupl
- ⭐ Fig.6 (p.10) ![[assets/crops/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-fig06.png]]
  - Ablation studies on system optimizations. experimental setup, we configured 32 micro-batches for the standard setting and established a token budget of 32,768 per micro-batch for the dynamic batching 

### #34 DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via 

- ⭐ Fig.2 (p.6) ![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-fig02.png]]
  - In the initial stage, we collect thousands of cold-start data that exhibits a conversational, human-aligned thinking process. RL training is then applied to improve the model perfor- mance with the co
- ⭐ Fig.3 (p.14) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]]
  - For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g from the old policy 14
- ⭐ Fig.6 (p.35) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]]
  - B.6. Ablation Study of Language Consistency Reward
- ⭐ Fig.7 (p.37) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]]
  - As can be seen, without the LC reward, language consistency gradually deteriorates as train- ing steps increase. However, when the LC reward is applied, stable language consistency is maintained throu
- ⭐ Fig.13 (p.48) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]]
  - We have categorized potential content safety challenges faced by language models into 4 major categories and 28 subcategories.
- ⭐ Fig.14 (p.53) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]]
  - For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and without the risk control system (introduced in D.3.1). Additionally, we tested the multilingual safety performance of Cl

### #35 Conditional Memory via Scalable Lookup: A New Axis of Sparsi

- ⭐ Fig.2 (p.6) ![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig02.png]]
  - During training, to accommodate large-scale embedding tables, we employ standard model parallelism by sharding the tables across available GPUs. An All-to-All communication primitive is used to gather
- ⭐ Fig.5 (p.16) ![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig05.png]]
  - We find that three components yield the most significant gains: (i) branch- specific fusion within the multi-branch backbone, (ii) context-aware gating, and (iii) tokenizer compression. Removing any o
- ⭐ Fig.7 (p.18) ![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig07.png]]
  - The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static patterns. In English, we observe strong activations 

### #36 HC: Manifold-Constrained Hyper-Connections

- ⭐ Fig.1 (p.1) ![[assets/crops/hc-manifold-constrained-hyper-connections-fig01.png]]
  - Illustrations of Residual Connection Paradigms. This figure compares the structural
- ⭐ Fig.2 (p.7) ![[assets/crops/hc-manifold-constrained-hyper-connections-fig02.png]]
  - Training Instability of Hyper-Connections (HC). This figure illustrates (a) the absolute
- ⭐ Fig.3 (p.7) ![[assets/crops/hc-manifold-constrained-hyper-connections-fig03.png]]
  - Propagation Instability of Hyper-Connections (HC). This figure illustrates the
- ⭐ Fig.4 (p.12) ![[assets/crops/hc-manifold-constrained-hyper-connections-fig04.png]]
  - Communication-Computation Overlapping for mHC. We extend the DualPipe
- ⭐ Fig.5 (p.12) ![[assets/crops/hc-manifold-constrained-hyper-connections-fig05.png]]
  - Training Stability of Manifold-Constrained Hyper-Connections (mHC). This figure
- ⭐ Fig.6 (p.13) ![[assets/crops/hc-manifold-constrained-hyper-connections-fig06.png]]
  - Scaling properties of mHC compared to the Baseline. (a) Compute Scaling Curve.
- ⭐ Fig.7 (p.14) ![[assets/crops/hc-manifold-constrained-hyper-connections-fig07.png]]
  - Propagation Stability of Manifold-Constrained Hyper-Connections (mHC). This
- ⭐ Fig.8 (p.14) ![[assets/crops/hc-manifold-constrained-hyper-connections-fig08.png]]
  - Visualizations of Learnable Mappings. This figure displays representative single-

### #37 Linear Optimal Topic Transport for Document Similarity

- ⭐ Fig.1 (p.7) ![[assets/crops/linear-optimal-topic-transport-for-document-similarity-fig01.png]]
  - k-NN classification performance across datasets affects mean test error in the CLASSIC dataset. 531
- ⭐ Fig.2 (p.8) ![[assets/crops/linear-optimal-topic-transport-for-document-similarity-fig02.png]]
  - t-SNE on CLASSIC

### #38 Root Mean Square Layer Normalization

- ⭐ Fig.1 (p.1) ![[assets/crops/root-mean-square-layer-normalization-fig01.png]]
  - One major feature of LayerNorm that is widely regarded as contributions to the stabilization is its re-centering invariance property: the summed inputs after LayerNorm remain intact when the inputs or
- ⭐ Fig.2 (p.6) ![[assets/crops/root-mean-square-layer-normalization-fig02.png]]
  - SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented accord- ing to Nematus [25] in Tensorﬂow.
- ⭐ Fig.3 (p.7) ![[assets/crops/root-mean-square-layer-normalization-fig03.png]]
  - SacreBLEU score on new- stest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorﬂow-version Ne- matus, and change p by a step size of 10%.
- ⭐ Fig.4 (p.7) ![[assets/crops/root-mean-square-layer-normalization-fig04.png]]
  - SacreBLEU score curve of Layer-
- ⭐ Fig.5 (p.8) ![[assets/crops/root-mean-square-layer-normalization-fig05.png]]
  - Error rate on validation set for the attentive reader model.
- ⭐ Fig.6 (p.8) ![[assets/crops/root-mean-square-layer-normalization-fig06.png]]
  - Recall@K values on validation set for the order-embedding models. worse than RMSNorm. Although in Figure 5 the performance of RMSNorm and LayerNorm is comparable, RMSNorm is around 15% faster than Lay
- ⭐ Fig.7 (p.13) ![[assets/crops/root-mean-square-layer-normalization-fig07.png]]
  - SacreBLEU score curve over train- ing steps on newstest2013 (devset) for the RNNSearch. Models are trained with Nema- tus in Theano.

### #39 GQA: Training Generalized Multi-Query Transformer Models fro

- ⭐ Fig.1 (p.1) ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig01.png]]
  - Overview of conversion from multi-head to multi-query attention. Key and value projection matri- ces from all heads are mean pooled into a single head.
- ⭐ Fig.2 (p.2) ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig02.png]]
  - Overview of grouped-query method. Multi-head attention has H query, key, and value heads. Multi-query attention shares single key and value heads across all query heads. Grouped-query attention instea
- ⭐ Fig.3 (p.3) ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig03.png]]
  - Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality and faster speed than MHA-Large, and GQA achieves even better performance with similar speed gains and comparable quality 
- ⭐ Fig.4 (p.4) ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig04.png]]
  - Performance comparison of different check- point conversion methods for T5-Large uptrained to MQA with proportion α = 0.05. ‘Mean’ mean-pools key and value heads, ‘First’ selects the first head and ‘R
- ⭐ Fig.5 (p.4) ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig05.png]]
  - Performance as a function of uptraining pro- portion for T5 XXL models with MQA and GQA-8.
- ⭐ Fig.6 (p.4) ![[assets/crops/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-fig06.png]]
  - Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost 

### #40 Qwen2.5-VL Technical Report

- ⭐ Fig.1 (p.3) ![[assets/crops/qwen2-5-vl-technical-report-fig01.png]]
  - The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a language model decoder to process multimodal inputs, including images and videos. The vision encoder is designed to hand

### #41 DeepSeek-V3 Technical Report

- ⭐ Fig.5 (p.12) ![[assets/crops/deepseek-v3-technical-report-fig05.png]]
  - It employs a bidirectional pipeline scheduling, which feeds micro-batches from both ends of the pipeline simultaneously and a significant portion of communications can be fully overlapped. This overla
- ⭐ Fig.6 (p.15) ![[assets/crops/deepseek-v3-technical-report-fig06.png]]
  - Firstly, in order to accelerate model training, the majority of core computation kernels, i.e., GEMM operations, are implemented in FP8 precision. These GEMM operations accept FP8 tensors as inputs an
- ⭐ Fig.10 (p.48) ![[assets/crops/deepseek-v3-technical-report-fig10.png]]
  - 48

### #42 Step-3 is Large yet Affordable: Model-system Co-design for C

- ⭐ Fig.1 (p.1) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig01.png]]
  - The Pareto frontier of recent models regarding acti- vated parameters and decoding costs. The darker area is GQA models’ Pareto frontier. Note: Step-3 also has the highest attention effective rank [7]
- ⭐ Fig.2 (p.6) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig02.png]]
  - With all the results shown, we make the following observations:
- ⭐ Fig.3 (p.6) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig03.png]]
  - Second, the time spent on each layer will be largely unbal- anced – when running with long context, the full GQA layers consume much more time than the linear attention layers. This may not be a probl
- ⭐ Fig.4 (p.8) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig04.png]]
  - Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.
- ⭐ Fig.5 (p.8) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig05.png]]
  - The compute and memory access of different atten- tion designs during decoding, including DSv3’s MLA, Qwen3
- ⭐ Fig.6 (p.11) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig06.png]]
  - Module disaggregation in AFD architecture. FFN can be deployed in TP-only, EP-only, or a hybrid TP+EP way, depending on hardware and model architecture. start to be concerned about other issues like e
- ⭐ Fig.7 (p.12) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig07.png]]
  - Communication topology and the multi-stages pipeline of the AFD architecture.
- ⭐ Fig.8 (p.13) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig08.png]]
  - StepMesh communication workflow tailored for AFD.
- ⭐ Fig.9 (p.13) ![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig09.png]]
  - StepMesh framework for multiple accelerators. AF-

### #43 SGLang: Efficient Execution of Structured Language Model Pro

- ⭐ Fig.1 (p.2) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig01.png]]
  - System architecture: An interpreter executes language primitives with optimized runtime.
- ⭐ Fig.2 (p.3) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig02.png]]
  - The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLang are shown in red. 2
- ⭐ Fig.3 (p.5) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig03.png]]
  - Examples of RadixAttention operations with an LRU eviction policy, illustrated across nine time points. The figure demonstrates the dynamic evolution of the radix tree in response to various requests.
- ⭐ Fig.4 (p.6) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig04.png]]
  - The decoding process of normal and compressed FSMs (the underscore _ means a space). requests by matched prefix length and prioritize requests with longer matched prefixes instead of using a first-com
- ⭐ Fig.5 (p.7) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig05.png]]
  - Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n"). Naively, the two gen primitives correspond to two
- ⭐ Fig.6 (p.8) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig06.png]]
  - Normalized latency on Llama-7B models. Lower is better. MMLU
- ⭐ Fig.7 (p.8) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig07.png]]
  - Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better. result from KV cache reuse, the exploitation of parallelism within a single program, and faster constrained deco
- ⭐ Fig.8 (p.9) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig08.png]]
  - (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.
- ⭐ Fig.9 (p.14) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig09.png]]
  - KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable model outputs. Shareable elements include few-shot 
- ⭐ Fig.10 (p.17) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig10.png]]
  - Example of how regex is converted into FSM and how FSM guides the decoding process.
- ⭐ Fig.11 (p.18) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]]
  - Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfigure explains the origins of various result compon
- ⭐ Fig.12 (p.19) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig12.png]]
  - Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better. MMLU
- ⭐ Fig.13 (p.19) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig13.png]]
  - Achieved cache hit rate and optimal cache hit rate on various benchmarks. opportunities for more compilation optimizations, as we can rewrite the graph and perform more static planning. D.1
- ⭐ Fig.14 (p.20) ![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig14.png]]
  - An SGLang program and its corresponding dataflow graph.

### #44 Efficiently Serving Large Multimodal Models Using EPD Disagg

- ⭐ Fig.1 (p.1) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig01.png]]
  - Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference be- tween encode and prefill stages (e
- ⭐ Fig.2 (p.2) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig02.png]]
  - Impact of disaggregation on supported batch size and number of images per request for the MiniCPM- V 2.6 model. Removing the LLM from the GPU signifi- cantly increases capacity, enabling larger batche
- ⭐ Fig.3 (p.3) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig03.png]]
  - The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migration—handle the trans- fer of data from encoding to prefill and from prefill to de- code, respectively. We denote the inpu
- ⭐ Fig.4 (p.4) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig04.png]]
  - System architecture of the proposed EPD Disaggregated Inference. the data associated with the request. In the decoding stage, workers load the LLM weights for decoding tasks and use the KV cache.
- ⭐ Fig.5 (p.6) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig05.png]]
  - SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively
- ⭐ Fig.6 (p.7) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig06.png]]
  - Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b)
- ⭐ Fig.7 (p.7) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig07.png]]
  - SLO attainment (↑) versus request rate on the
- ⭐ Fig.8 (p.7) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig08.png]]
  - As seen, EPD consistently outperforms vLLM and Dist-
- ⭐ Fig.9 (p.9) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig09.png]]
  - As shown, EPD is the only configuration that achieves the SLO requirements, while the other baselines fail to meet the SLOs entirely, even at low request rates.
- ⭐ Fig.10 (p.13) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig10.png]]
  - Left: Impact of varying the number of encoding workers in the EPD method. The notation xEyP denotes a configuration with x encoder and y prefill workers. The DistServe method uses a fixed 7P configura
- ⭐ Fig.11 (p.13) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig11.png]]
  - SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively
- ⭐ Fig.12 (p.16) ![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig12.png]]
  - Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light gr

### #45 Mooncake: A KVCache-centric Disaggregated Architecture for L

- ⭐ Fig.1 (p.2) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig01.png]]
  - Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these throughput-oriented optimizations may lead to violat
- ⭐ Fig.2 (p.4) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig02.png]]
  - Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the computational complexity of attention networks scale
- ⭐ Fig.3 (p.5) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig03.png]]
  - The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.
- ⭐ Fig.4 (p.6) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig04.png]]
  - Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in parallel with the prefill computation to mitigate tr
- ⭐ Fig.5 (p.6) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig05.png]]
  - Input and output length distributions in the request trace. 4
- ⭐ Fig.6 (p.7) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig06.png]]
  - CDF (Cumulative Distribution
- ⭐ Fig.7 (p.9) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig07.png]]
  - Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).
- ⭐ Fig.8 (p.11) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig08.png]]
  - The prefill scheduling experiment in the Mooncake cluster.
- ⭐ Fig.9 (p.13) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig09.png]]
  - The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.
- ⭐ Fig.10 (p.14) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig10.png]]
  - Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions are necessary, making request-level predictions part
- ⭐ Fig.11 (p.16) ![[assets/crops/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-fig11.png]]
  - End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets instances. In real-world clusters, the demand for prefill and decoding instances generally remains stable ove
- ⭐ Fig.12 (p.16) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
  - End-to-end experiments of Mooncake and vLLM on simulated data.
- ⭐ Fig.13 (p.17) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]]
  - Request TTFT and TBT distributions of Mooncake and vLLM under real workloads

### #46 MegaScale: Scaling Large Language Model Training to More Tha

- ⭐ Fig.1 (p.2) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig01.png]]
  - Data parallel training with ZeRO2. dependencies that contribute to stability issues. We develop a robust training framework to automate fault localization and recovery. We design heartbeat messages en
- ⭐ Fig.2 (p.3) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig02.png]]
  - Interleaved 1F1B pipeline. update the model. Instead of duplicating model states (like the optimizer states, gradients, and parameters), Zero Redun- dancy Optimizer (ZeRO) [11] shards these states acr
- ⭐ Fig.3 (p.4) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig03.png]]
  - Overlapping communication in tensor parallelism (TP) and sequence parallelism (SP) with parallel transformer block (PTB). with a large receptive field created by stacking layers of such windowed atten
- ⭐ Fig.4 (p.4) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig04.png]]
  - The cool-down phase can be viewed as the inverse of the warm-up phase, allowing for the inverse application of the same technique. As for the steady phase, both the forward and backward computation ar
- ⭐ Fig.5 (p.6) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig05.png]]
  - Robust training workflow. interval and help recover the transmission more quickly when the link flapping period is short. 4
- ⭐ Fig.6 (p.8) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig06.png]]
  - Inconsistent MFU observed in large-scale training. Differ- ent colors denote distinct executions of the same training job. mitigates the bandwidth constraints of HDFS, leading to a substantial reducti
- ⭐ Fig.7 (p.8) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig07.png]]
  - We gather latency data of the computation phase (forward and backward) across devices and average the latency across steps. The aggregated data is visualized host 0 0 1 2 3 host 3 12 13 14 15 host 6 2
- ⭐ Fig.8 (p.9) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig08.png]]
  - The trace shows events collected in a pipeline group on a unified timeline. Dependencies become visible when an event is selected.
- ⭐ Fig.9 (p.10) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig09.png]]
  - Weak-scaling training performance of Megatron-LM and
- ⭐ Fig.10 (p.11) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig10.png]]
  - The training loss curves in microbenchmark experiments.
- ⭐ Fig.11 (p.11) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig11.png]]
  - The normalized training loss curve of a real production run on more than 10,000 GPUs for several weeks. This run trains a model with hundreds of billions of parameters on multi-trillion tokens. Differ
- ⭐ Fig.12 (p.12) ![[assets/crops/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-fig12.png]]
  - The MFU becomes stable after addressing the stragglers and problematic code segments. Different colors represent different training trials with the same setup. executing diagnostic tests is less than 

### #47 ZeRO: Memory Optimizations Toward Training Trillion Paramete

- ⭐ Fig.1 (p.3) ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig01.png]]
  - Comparing the per-device memory consumption of model states, with three stages of
- ⭐ Fig.2 (p.4) ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig02.png]]
  - ZeRO training throughput and speedup w.r.t SOTA baseline for varying model sizes.
- ⭐ Fig.3 (p.5) ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig03.png]]
  - Superlinear scalability and per GPU training throughput of a 60B parameter model using ZeRO-100B. 38 TFlops per GPU, and aggregate performance over 15 Petaﬂops. This is more than 10x improvement in tr
- ⭐ Fig.4 (p.16) ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig04.png]]
  - Max model throughput with ZeRO-DP.
- ⭐ Fig.5 (p.16) ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig05.png]]
  - SOTA Turing-NLG enabled by ZeRO.
- ⭐ Fig.6 (p.16) ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig06.png]]
  - Max model size .
- ⭐ Fig.7 (p.16) ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig07.png]]
  - Max cache allo- cated.
- ⭐ Fig.8 (p.16) ![[assets/crops/zero-memory-optimizations-toward-training-trillion-parameter-models-fig08.png]]
  - Throughput per GPU. a Bert-Large model for a data sample. Even if we assume the same sequence length and the total number of samples required to train the model, training a 1T model would take 140 day

### #48 Efficient Large-Scale Language Model Training on GPU Cluster

- ⭐ Fig.1 (p.1) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig01.png]]
  - Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models with time. The number of floating-point op- erations to train these models is increasing at an exponential rate.
- ⭐ Fig.2 (p.3) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig02.png]]
  - Combination of tensor and pipeline model parallelism (MP) used in this work for transformer-based models.
- ⭐ Fig.3 (p.3) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig03.png]]
  - GPipe pipeline schedule with forward passes (blue) for all microbatches (represented by numbers) followed by backward passes (green). The gray area represents the pipeline bubble. For simplicity, we a
- ⭐ Fig.4 (p.3) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig04.png]]
  - Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleaved 1F1B schedule, where each device is assigned mu
- ⭐ Fig.5 (p.5) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig05.png]]
  - Blocks of transformer model partitioned with tensor model parallelism (figures borrowed from Megatron [40]). 𝑓and 𝑔 are conjugate. 𝑓is the identity operator in the forward pass and all- reduce in the 
- ⭐ Fig.6 (p.5) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig06.png]]
  - Fraction of time spent idling due to pipeline flush (pipeline bubble size) versus data-parallel size (𝑑), for different numbers of GPUs (𝑛) and ratio of batch size to microbatch size (𝑏′ = 𝐵/𝑏).
- ⭐ Fig.7 (p.6) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig07.png]]
  - Per-GPU throughput versus microbatch size for a GPT model with a billion parameters (128 attention heads, hidden size of 4096, 4 transformer layers).
- ⭐ Fig.8 (p.6) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig08.png]]
  - Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·  𝑡𝑓(𝑏) + 𝑡𝑏(𝑏)) with respect to the mi- crobatch size 𝑏for the same GPT model from Figure 7.
- ⭐ Fig.9 (p.7) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig09.png]]
  - Scatter/gather communication optimization. Light blue blocks are layers in the first pipeline stage, and dark blue blocks are layers in the second pipeline stage. Without the scatter/gather optimizati
- ⭐ Fig.10 (p.8) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig10.png]]
  - Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B GPT-3 model is shown with dotted lines, and the 530B model is shown with solid lines). Global batch sizes are fixed and 
- ⭐ Fig.11 (p.9) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig11.png]]
  - Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-parallel size). 12 24 36 48 60
- ⭐ Fig.12 (p.9) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig12.png]]
  - Throughput per GPU of interleaved and non-interleaved schedules for a GPT model (175 billion parameters) on 96 GPUs. and a microbatch size of 1. As we increase the number of pipeline stages, we also i
- ⭐ Fig.13 (p.9) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig13.png]]
  - Throughput per GPU of various parallel configurations that combine pipeline and tensor model parallelism using a GPT model with 162.2 billion parameters and 64 A100 GPUs.
- ⭐ Fig.14 (p.10) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig14.png]]
  - Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, mi- crobatch size of 
- ⭐ Fig.15 (p.10) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig15.png]]
  - Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, a
- ⭐ Fig.16 (p.10) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig16.png]]
  - Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different microbatch sizes on a GPT model with 91 billion parameters, for two different batch sizes using 64 A100 GPUs. importance 
- ⭐ Fig.17 (p.11) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig17.png]]
  - Throughput (in sequences per second) with and without activation recomputation for a GPT model with 145 billion param- eters using 128 A100 GPUs ((𝑡, 𝑝) = (8, 16)). 12 24 36 48 60
- ⭐ Fig.18 (p.11) ![[assets/crops/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig18.png]]
  - Throughput per GPU with and without the scatter/gather optimization for a GPT model with 175 billion parameters using 96 A100 GPUs and the interleaved schedule.

### #49 Megatron-LM: Training Multi-Billion Parameter Language Model

- ⭐ Fig.1 (p.2) ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig01.png]]
  - Model (blue) and model+data (green) parallel FLOPS as a function of number of GPUs. Model parallel (blue): up to 8-way model parallel weak scaling with approximately 1 billion parameters per GPU (e.g.
- ⭐ Fig.2 (p.3) ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig02.png]]
  - Transformer Architecture. Purple blocks correspond to fully connected layers. Each blue block represents a single trans- former layer that is replicated N times. and compute efﬁciency. The original tr
- ⭐ Fig.3 (p.4) ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig03.png]]
  - Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an identity operator in the forward pass and all reduce in the backward pass while g is an all reduce in the forward pass and 
- ⭐ Fig.4 (p.5) ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig04.png]]
  - Communication operations in a transformer layer. There are 4 total communication operations in the forward and backward pass of a single model parallel transformer layer. contains a portion of the emb
- ⭐ Fig.5 (p.6) ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig05.png]]
  - Model and model + data parallel weak scaling efﬁciency as a function of the number of GPUs. done by scaling the batch-size, however, this approach does not address training large models that do not ﬁt
- ⭐ Fig.6 (p.7) ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig06.png]]
  - Validation set perplexity. All language models are trained for 300k iterations. Larger language models converge notice- ably faster and converge to lower validation perplexities than their smaller cou
- ⭐ Fig.7 (p.8) ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig07.png]]
  - Training loss for BERT model using the original architec- ture (a) and the rearranged architecture (b). Left ﬁgure shows the training loss for 336M and 752M BERT model. While the original architecture
- ⭐ Fig.8 (p.12) ![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig08.png]]
  - Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel and 64-way data parallel. C. Text Samples

### #51 Efficient Training of Large Language Models on Distributed I

- ⭐ Fig.1 (p.2) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig01.png]]
  - Overall structure of this survey.
- ⭐ Fig.2 (p.3) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig02.png]]
  - A typical Transformer layer contains an Attention
- ⭐ Fig.3 (p.4) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig03.png]]
  - Infrastructure overview for distributed LLM training.
- ⭐ Fig.4 (p.5) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig04.png]]
  - Studies on infrastructure optimizations for distributed LLM training.
- ⭐ Fig.5 (p.6) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig05.png]]
  - Five chip-to-chip topologies: tree topology, cube-mesh topology, switch-based fully-connected topology, P2P-based
- ⭐ Fig.6 (p.7) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig06.png]]
  - Four typical network topologies in large-scale GPU clusters: Clos topology, Dragonfly+ topology, rail-optimization
- ⭐ Fig.7 (p.10) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig07.png]]
  - Studies on parallelism schemes for distributed LLM training.
- ⭐ Fig.8 (p.12) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig08.png]]
  - An example of 3D-parallelism with data parallelism, tensor parallelism, and pipeline parallelism.
- ⭐ Fig.9 (p.14) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig09.png]]
  - Expert parallelism. The dotted line highlights the
- ⭐ Fig.10 (p.17) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig10.png]]
  - An example of RLHF. Inference process: 1 The
- ⭐ Fig.11 (p.19) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig11.png]]
  - Studies on computation optimizations for distributed LLM training.
- ⭐ Fig.12 (p.21) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig12.png]]
  - Studies on memory optimizations for distributed LLM training.
- ⭐ Fig.13 (p.25) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig13.png]]
  - Communication traffic heatmap for InternLM-2
- ⭐ Fig.14 (p.26) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig14.png]]
  - Studies on communication optimizations for distributed LLM training.
- ⭐ Fig.15 (p.29) ![[assets/crops/efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey-fig15.png]]
  - Studies on fault tolerance techniques for distributed LLM training.

### #52 Efficient Memory Management for Large Language Model Serving

- ⭐ Fig.1 (p.1) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig01.png]]
  - Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory for the KV cache (red) is (de)allocated per servi
- ⭐ Fig.2 (p.2) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig02.png]]
  - Average percentage of memory wastes in different LLM serving systems during the experiment in §6.2. percentage of memory is used for other data, including ac- tivations – the ephemeral tensors created
- ⭐ Fig.3 (p.4) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig03.png]]
  - KV cache memory management in existing systems. Three types of memory wastes – reserved, internal fragmentation, and external fragmentation – exist that prevent other requests from fitting into the me
- ⭐ Fig.4 (p.5) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig04.png]]
  - vLLM system overview.
- ⭐ Fig.5 (p.5) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig05.png]]
  - Illustration of the PagedAttention algorithm, where the attention key and values vectors are stored as non-contiguous blocks in the memory. block size (𝐵). Denote the key block 𝐾𝑗= (𝑘(𝑗−1)𝐵+1, . . . ,
- ⭐ Fig.6 (p.6) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig06.png]]
  - Block table translation in vLLM. divides it into physical KV blocks (this is also done on CPU RAM for swapping; see §4.5). The KV block manager also maintains block tables—the mapping between logical 
- ⭐ Fig.7 (p.6) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig07.png]]
  - Storing the KV cache of two requests at the same time in vLLM. requests and the latest tokens for generation phase requests) as one sequence and feeds it into the LLM. During LLM’s computation, vLLM u
- ⭐ Fig.8 (p.7) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig08.png]]
  - Parallel sampling example. generates a single sequence. In the remainder of this paper, we assume the more general case in which a request gener- ates multiple sequences. In parallel sampling, one req
- ⭐ Fig.9 (p.7) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig09.png]]
  - Beam search example. sample space. The algorithm relies on the beam width pa- rameter 𝑘, which determines the number of top candidates retained at every step. During decoding, beam search ex- pands ea
- ⭐ Fig.10 (p.8) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig10.png]]
  - Shared prompt example for machine translation.
- ⭐ Fig.11 (p.9) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig11.png]]
  - Input and output length distributions of the (a)
- ⭐ Fig.12 (p.10) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig12.png]]
  - Single sequence generation with OPT models on the ShareGPT and Alpaca dataset
- ⭐ Fig.13 (p.10) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig13.png]]
  - Average number of batched requests when serv- ing OPT-13B for the ShareGPT (2 reqs/s) and Alpaca (30 reqs/s) traces.
- ⭐ Fig.14 (p.11) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig14.png]]
  - Parallel generation and beam search with OPT-13B on the Alpaca dataset.
- ⭐ Fig.15 (p.11) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig15.png]]
  - Average amount of memory saving from sharing KV blocks, when serving OPT-13B for the Alpaca trace.
- ⭐ Fig.16 (p.12) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig16.png]]
  - Translation workload where the input prompts share a common prefix. The prefix includes (a) 1 example with 80 tokens or (b) 5 examples with 341 tokens.
- ⭐ Fig.17 (p.12) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig17.png]]
  - Performance on chatbot workload.
- ⭐ Fig.18 (p.12) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
  - Ablation experiments. handle the long prompts, as PagedAttention resolves the problem of memory fragmentation and reservation. 7
- ⭐ Fig.19 (p.13) ![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig19.png]]
  - (a) Overhead of recomputation and swapping for different block sizes. (b) Performance when serving OPT-13B with the ShareGPT traces at the same request rate.

### #53 DeFT: Decoding with Flash Tree-attention for Efficient Tree-

- ⭐ Fig.1 (p.1) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig01.png]]
  - Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., 2022; Liu et al., 2023) or selection, as shown in 
- ⭐ Fig.2 (p.5) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig02.png]]
  - Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV
- ⭐ Fig.3 (p.6) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig03.png]]
  - Comparison of QKV partitioning strategies during the QKV Preparation Phase between DEFT-
- ⭐ Fig.4 (p.9) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig04.png]]
  - Latency breakdown for specula- tive decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.
- ⭐ Fig.5 (p.15) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig05.png]]
  - Illustration of DEFT. (Left) System overview. (Right) The data flow of DEFT-Node (DEFT-Flatten is similar except for QKV partitioning) using a decoding tree example.
- ⭐ Fig.6 (p.16) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p16.png]]
  - Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.
- ⭐ Fig.7 (p.17) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig07.png]]
  - Analysis for two case studies of tree-based decoding. (Left) Multi-step reasoning. (Right) Speculative decoding. Blue boxes mean shareable past KV cache in storage and memory access during the tree at
- ⭐ Fig.8 (p.19) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig08.png]]
  - Operations of Tree Attention-Medusa (Cai et al., 2024). No Kernel Fusion or Tiling strategy is applied, which introduces significant IO of partial results like QK⊤, DCM, and Softmax between GPU global
- ⭐ Fig.9 (p.19) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig09.png]]
  - Overview of two stages in DEFT Attention Kernel (DEFT-Node for example, and DEFT-Flatten is similar). Stage 1–calculate partial attentions. Based on the QKV grouping results after KV-Guided Grouping
- ⭐ Fig.10 (p.20) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig10.png]]
  - Detailed attention operations of DEFT kernel (DEFT-Node for example, and DEFT-Flatten is similar). Based on the same decoding tree in Figure 3.
- ⭐ Fig.11 (p.21) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig11.png]]
  - When the number of leaf nodes/queries ln is sufficiently large, the IO cost of partial results might become comparable to that of the KV cache. For instance, in the Llama models (Touvron et al., 2023a
- ⭐ Fig.12 (p.23) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig12.png]]
  - The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)
- ⭐ Fig.13 (p.25) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig13.png]]
  - Comparison of split strategies DEFT-Node and DEFT-Flatten in sorting task. Speedup ratio refers to the ratio between the per iteration latency of DEFT-Node and DEFT-Flatten. Tree Node Len std represen
- ⭐ Fig.14 (p.26) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
  - Per iteration latency for few-shot prompting tasks with different tree width. e2e means decoding latency(optimal end-to-end latency), while Attn means only the attention overhead.
- ⭐ Fig.15 (p.26) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig15.png]]
  - The chunk size selection is a trade-off between IO redundancy and threadblock scheduling: a larger chunk size means less redundancy of Query IO but may cause potential idle SMs of GPUs due to fewer th
- ⭐ Fig.16 (p.27) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig16.png]]
  - Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000
- ⭐ Fig.17 (p.27) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig17.png]]
  - Decoding latency of DEFT with different prompt lengths in speculative decoding.
- ⭐ Fig.18 (p.28) ![[assets/crops/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-fig18.png]]
  - Attention latency of DEFT with different prompt lengths in speculative decoding.

### #54 NanoFlow: Towards Optimal Large Language Model Serving Throu

- ⭐ Fig.1 (p.3) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig01.png]]
  - Transformer architecture. The operations in the yellow boxes have large batch sizes and share model weight parameters across requests; hence, they are compute-bound. Operations in green boxes require 
- ⭐ Fig.2 (p.5) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig02.png]]
  - Comparison of network time and compute time. The closer to yellow, the more compute-bound the workload is, whereas the closer to blue indicates the workload is more network-bound. LMSYS-Chat Splitwise
- ⭐ Fig.3 (p.5) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig03.png]]
  - Comparison of compute time and memory time.
- ⭐ Fig.4 (p.8) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig04.png]]
  - Execution pipeline of existing systems. The green, yellow, and blue operations correspond to memory-, compute-, and network-bound operations. Operations in the previous and next layer are denoted by d
- ⭐ Fig.5 (p.8) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig05.png]]
  - Interference characteristics between GEMM and GEMV kernels. The points on the x-axis correspond unique GEMM-GEMV implementation pairs. The y-axis denotes the GEMM and GEMV kernels’ normalized performa
- ⭐ Fig.6 (p.11) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig06.png]]
  - Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 768-2048, respectively. R stands for resource utiliz
- ⭐ Fig.7 (p.11) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig07.png]]
  - Offline throughput comparison. NanoFlow outper- forms all baselines for all the workload settings. TP stands for the number of GPUs used with tensor parallelism. • How do the various techniques propos
- ⭐ Fig.8 (p.13) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig08.png]]
  - Latency comparison. The x-axis shows the number of incoming requests per second and the y-axis shows the normalized latency. NanoFlow handles higher request within 200ms SLO constraints.
- ⭐ Fig.9 (p.13) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig09.png]]
  - Ablation study results for NanoFlow. Nano-batching and overlapping improves NanoFlow’s performance.
- ⭐ Fig.10 (p.13) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig10.png]]
  - While the non-overlapping baseline sequentially executes operations, which mostly uses only one resource at a given time, the NanoFlow instance can concurrently utilize multiple resources and achieves
- ⭐ Fig.11 (p.13) ![[assets/crops/nanoflow-towards-optimal-large-language-model-serving-throughput-fig11.png]]
  - We find that

### #55 Gated Delta Networks: Improving Mamba2 with Delta Rule

- ⭐ Fig.1 (p.7) ![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig01.png]]
  - Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.
- ⭐ Fig.2 (p.8) ![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig02.png]]
  - Length extrapolation on six long benchmarks.
- ⭐ Fig.3 (p.9) ![[assets/crops/gated-delta-networks-improving-mamba2-with-delta-rule-fig03.png]]
  - Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outperform

### #56 Parallel Scan on Ascend AI Accelerators

- ⭐ Fig.3 (p.3) ![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig03.png]]
  - 1 shows the Ascend architecture where the
- ⭐ Fig.4 (p.4) ![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig04.png]]
  - 1: Data path from an input tile xℓto an output tile yℓof the ScanU (Algorithm 4.1).
- ⭐ Fig.5 (p.7) ![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig05.png]]
  - 1: A diagram of well-known parallel scan applica- tions considered here along with their dependencies.
- ⭐ Fig.6 (p.8) ![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig06.png]]
  - 1:

### #57 Kimi K3: Open Frontier Intelligence

- ⭐ Fig.1 (p.1) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig01.png]]
  - Kimi K3 main results. 1https://huggingface.co/moonshotai/Kimi-K3[cs.CL] 7 Aug 2026
- ⭐ Fig.2 (p.3) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig02.png]]
  - The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.
- ⭐ Fig.3 (p.5) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig03.png]]
  - Lower-bounded decay and its effect on chunkwise KDA computation. (a) Kimi Linear uses an unbounded negative-Softplus mapping, whereas Kimi K3 bounds the log-decay with a scaled sigmoid; the curves sho
- ⭐ Fig.4 (p.7) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig04.png]]
  - Gate and up branches of GLU, SwiGLU, and SiTU-GLU, together with their scalar responses, where σ denotes the sigmoid function. Both branches receive the scalar input x, and all curves share the domain
- ⭐ Fig.5 (p.8) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig05.png]]
  - Illustration of Quantile Balancing with m = 8 tokens, n = 4 routed experts, and k = 1 selected expert per token. (a)
- ⭐ Fig.6 (p.9) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig06.png]]
  - Vision-tower gradient norms in our pre-training ablations. Compared with the SigLIP-initialized MoonViT-3D, the from-scratch MoonViT-V2 maintains lower gradient norms with fewer spikes, indicating mor
- ⭐ Fig.7 (p.11) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig07.png]]
  - Fitted scaling-law curves for Kimi K2 and Kimi K3. Kimi K3 achieves 2.5× gain in scaling efficiency over Kimi K2.
- ⭐ Fig.8 (p.13) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig08.png]]
  - Scores and the average assistant steps across a variety of public and in-house evaluations during RL. By scaling RL FLOPs, tool-call steps scale up consistently, accompanied by a comprehensive improve
- ⭐ Fig.9 (p.15) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig09.png]]
  - Overview of knowledge-graph-guided task synthesis. The hierarchically organized knowledge graph represents concepts at multiple levels, ranging from broad domains to fine-grained concepts. Related nod
- ⭐ Fig.10 (p.17) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig10.png]]
  - Completion curves on Camera Repair Management System, a black-box system replication task in which the agent reconstructs a hidden 3D-camera repair system as a web application through oracle queries. 
- ⭐ Fig.11 (p.19) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig11.png]]
  - Computation, communication and offloading overlapped in different PP phases.
- ⭐ Fig.12 (p.23) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig12.png]]
  - Fine-grained prefix caching within a physical cache block. A 6144-token physical block contains twelve 512-token hash blocks, with cached MLA blocks shown in blue and empty blocks in light gray. The m
- ⭐ Fig.13 (p.32) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig13.png]]
  - Score vs. per-task inference cost on Kimi Code Bench 2.0, BrowseComp, GDPval-AA v2, and AA-Briefcase. Kimi K3 is marked with a star.
- ⭐ Fig.14 (p.33) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig14.png]]
  - Case study: GPU kernel optimization on AttnRes. 7
- ⭐ Fig.15 (p.34) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig15.png]]
  - Case study: GPU compiler development with MiniTriton. (a) CUDA-core and (b) tensor-core rooflines of MiniTriton kernels on an NVIDIA L20 (sm_89) against torch eager, torch.compile, Triton, and cuBLAS 
- ⭐ Fig.16 (p.46) ![[assets/crops/kimi-k3-open-frontier-intelligence-fig16.png]]
  - Structure of the Kimi K3 chat template. (a) Context layout: global option messages precede the input messages, while one-shot option messages follow them, so that per-request options leave the history

### #58 Prefill-as-a-Service: KVCache of Next-Generation Models Coul

- ⭐ Fig.1 (p.2) ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig01.png]]
  - Comparison of two deployment paradigms for PD-disaggregated LLM serving.
- ⭐ Fig.2 (p.4) ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig02.png]]
  - KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.
- ⭐ Fig.3 (p.6) ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig03.png]]
  - Deployment topology of the PrfaaS-PD architecture.
- ⭐ Fig.4 (p.7) ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig04.png]]
  - Hybrid prefix cache pool. Linear states and full-attention KVCache are managed by separate groups backed by a unified block pool. Blocks are categorized as prefix-cache (intra-cluster only, block-alig
- ⭐ Fig.5 (p.11) ![[assets/crops/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-fig05.png]]
  - Illustration of the grid search process for the two optimization variables. (a) fixes t at the optimum and searches over the prefill/decode instance split within the local PD cluster. (b) fixes

### #59 LongSpec: Long-Context Lossless Speculative Decoding with Ef

- ⭐ Fig.1 (p.1) ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig01.png]]
  - The SoTA SD method, EAGLE, has a training context length of 2048, which is significantly shorter than the context lengths of modern LLMs. 2023), and their ability to handle extensive con- texts is bec
- ⭐ Fig.2 (p.4) ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig02.png]]
  - Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and the Hybrid Tree Attention. (a) We use a sliding window self-attention layer to capture the local context information an
- ⭐ Fig.3 (p.7) ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig03.png]]
  - Decoding speed (tokens/s) across different models and settings. All results are computed at T = 1. The letters G, Q, M, L, and R on the horizontal axis represent the datasets GovReport, QMSum, Multi-N
- ⭐ Fig.4 (p.8) ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig04.png]]
  - Training loss curves on long-context data.
- ⭐ Fig.5 (p.8) ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig05.png]]
  - Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latency reduction is observed in the target model’s at- 
- ⭐ Fig.6 (p.9) ![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig06.png]]
  - Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such long-output scenarios because the initial inference stage of the long reasoning task is not the same as the traditional 

### #60 SpecExtend: A Drop-in Enhancement for Speculative Decoding o

- ⭐ Fig.1 (p.1) ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig01.png]]
  - Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct and EAGLE-3 across varying input lengths. Performance significantly declines well before the shift of memory bottleneck.
- ⭐ Fig.2 (p.2) ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig02.png]]
  - Overview of SpecExtend. FlashAttention accelerates the prefill phases of both target and draft models, and Hybrid Tree Attention accelerates the verification phase. We use the target model’s attention
- ⭐ Fig.3 (p.4) ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig03.png]]
  - Left figure shows acceptance rates for hard and easy tokens, where CMR enables more accurate drafting in both cases compared to StreamingLLM.
- ⭐ Fig.4 (p.5) ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig04.png]]
  - (a) Average accepted length of Vicuna-7B/68M across different draft model cache settings. (b) End-to-end latency breakdown of speculative decoding on 16K-token inputs. retrieved context to identify an
- ⭐ Fig.5 (p.6) ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig05.png]]
  - Speedup comparison of standard speculative decoding and SpecExtend across varying input lengths on
- ⭐ Fig.6 (p.7) ![[assets/crops/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-fig06.png]]
  - Decoding speed (left) and average ac- cepted length (right) of the DeepSeek-R1-Distill-Llama- 8B/EAGLE-3 setup on the long reasoning task with the AIME-24 benchmark.

### #61 A Survey of Large Language Models

- ⭐ Fig.1 (p.3) ![[assets/crops/a-survey-of-large-language-models-fig01.png]]
  - As discussed before, language model is not a new tech- nical concept specially for LLMs, but has evolved with the advance of artificial intelligence over the decades. Early lan- guage models mainly ai
- ⭐ Fig.3 (p.99) ![[assets/crops/a-survey-of-large-language-models-fig03.png]]
  - – Section 4: add LLM-based data filtering and selec- tion methods in Section 4.1.2; update Section 4.2.1, “Emergent Architectures” to include more discus- sions about SSM-based architectures; add Tabl
- ⭐ Fig.4 (p.7) ![[assets/crops/a-survey-of-large-language-models-fig04.png]]
  - The basic principle underlying GPT models is to compress the world knowledge into the decoder-only
- ⭐ Fig.5 (p.12) ![[assets/crops/a-survey-of-large-language-models-fig05.png]]
  - Public API of LLMs. Instead of directly using the model copies, APIs provide a more convenient way for common users to use LLMs, without the need of running the model locally. As a representative inte
- ⭐ Fig.7 (p.18) ![[assets/crops/a-survey-of-large-language-models-fig07.png]]
  - Filtering and Selection. To remove low-quality data from the collected corpus, existing work generally adopts two ap- proaches, namely classifier-based and heuristic-based. The former approach trains 
- ⭐ Fig.8 (p.20) ![[assets/crops/a-survey-of-large-language-models-fig08.png]]
  - Data Mixture. Since each kind of data source is closely related to the development of certain capacities for LLMs (referring to the discussions in Section 4.1), it is important to set a suitable distr
- ⭐ Fig.9 (p.22) ![[assets/crops/a-survey-of-large-language-models-fig09.png]]
  - Encoder-decoder Architecture. The vanilla Transformer model is built on the encoder-decoder architecture [22], which consists of two stacks of Transformer blocks as the encoder and decoder, respective
- ⭐ Fig.13 (p.43) ![[assets/crops/a-survey-of-large-language-models-fig13.png]]
  - Adapter Tuning. Adapter tuning incorporates small neural network modules (called adapter) into the Transformer mod- els [406]. To implement the adapter module, a bottleneck architecture has been propo
- ⭐ Fig.16 (p.54) ![[assets/crops/a-survey-of-large-language-models-fig16.png]]
  - In this paradigm, there are typically three components: task planner, plan executor, and environment36. Specifically, task planner, which is played by LLMs, aims to generate the whole plan to solve a 
- ⭐ Fig.17 (p.59) ![[assets/crops/a-survey-of-large-language-models-fig17.png]]
  - Hallucination widely occurs in existing LLMs, even the most superior LLMs such as GPT-4 [46]. Furthermore, existing work shows that LLMs encounter difficulties in recognizing the hallucinated con- ten

### #62 KV Cache Optimization Strategies for Scalable and Efficient 

- ⭐ Fig.1 (p.2) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig01.png]]
  - Autoregressive generation, at each step the new token (orange) attends to all prior tokens (cyan). Without caching, keys and values for every past token would be recomputed from scratch at each step. 
- ⭐ Fig.2 (p.3) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig02.png]]
  - Data-flow of the KV cache within a single transformer layer. Input token xt fans into three projections; Kt and Vt are appended to their respective caches (teal); Qt attends over the full caches to pr
- ⭐ Fig.3 (p.3) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig03.png]]
  - KV cache memory as a function of context length for three LLaMA-2 model variants under fp16 precision.
- ⭐ Fig.4 (p.4) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig04.png]]
  - Causal self-attention weight matrix for “The apple tastes sweet.” visualised with the Viridis colormap (dark purple = low, yellow = high). Gray cells are causally masked future tokens. Each row sums t
- ⭐ Fig.5 (p.5) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig05.png]]
  - Taxonomy of KV cache optimization techniques surveyed in this paper, organized into five major categories.
- ⭐ Fig.6 (p.6) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig06.png]]
  - Upper plots illustrate symbolic plots of an attention map deploying different KV cache policies in LLM generation. Lower right: contrasts their accuracy-memory trade-off. Left: the overview of H2O fra
- ⭐ Fig.7 (p.7) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig07.png]]
  - The graph shows the simplified workflow of SnapKV, where the orange area represents the cluster of features per head selected by SnapKV. These features are then used to form new Key-Value pairs concat
- ⭐ Fig.8 (p.9) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig08.png]]
  - Definition of per-token and per-channel quantization. X ∈Rlprompt×d is the key/value cache, where lprompt is the number of tokens and d is the number of channels. zX is the zero-point, and sX is the s
- ⭐ Fig.9 (p.9) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig09.png]]
  - Palu’s low-rank projection method for KV-cache reduction. A weight matrix W of linear projection is decomposed into two low-rank matrices. Input X is down-projected to a latent representation H, which
- ⭐ Fig.10 (p.11) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig10.png]]
  - vLLM system overview [22]. 11
- ⭐ Fig.11 (p.12) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig11.png]]
  - Operation flow of the prefetching module of InfiniGen. [23]. A layer-wise KV cache management strategy is proposed in LayerKV [24]. The core concept is to split KV cache by layers, keeping only a subs
- ⭐ Fig.12 (p.15) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig12.png]]
  - Standard linear attention (top) vs. loglinear attention (bottom). The input consists of query, key, and value vectors [30]. at nearby keys and averages their value; while Linear Attention is alike glo
- ⭐ Fig.13 (p.17) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig13.png]]
  - During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaining a low-rank key cache, landmarks, and outliers on the GPU. During decoding, it employs landmarks for sparse attention.
- ⭐ Fig.14 (p.17) ![[assets/crops/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-fig14.png]]
  - System overview of TailorKV. Offline identification categorizes the layers into quantization-friendly and sparsity-friendly. For quantization-friendly layers, we employ aggressive static quantization.

### #63 Kimi Linear: An Expressive, Efficient Attention Architecture

- ⭐ Fig.1 (p.1) ![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig01.png]]
  - (a) Performance vs. acceleration. With strict fair comparisons with 1.4T training tokens, on MMLU-Pro (4k context length, red stars), Kimi Linear leads performance (51.0) at similar speed. On RULER (1
- ⭐ Fig.2 (p.5) ![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig02.png]]
  - Execution time of kernels for vary- ing input lengths, with a uniform batch size of 1 and 16 heads.
- ⭐ Fig.3 (p.5) ![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig03.png]]
  - Neural Parameterization
- ⭐ Fig.4 (p.7) ![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig04.png]]
  - Results on synthetic tasks: palindrome, multi query associative recall, and the state tracking.
- ⭐ Fig.5 (p.9) ![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig05.png]]
  - The fitted scaling law curves for MLA and Kimi Linear. balanced positional bias across layers, which improves robustness and extrapolation at long ranges, leading to stronger long-context performance.
- ⭐ Fig.6 (p.12) ![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig06.png]]
  - The training and test accuracy curves for Kimi Linear@1.4T and MLA@1.4T during Math RL training. Kimi Linear consistently outperforms the full attention baseline by a sizable margin during the whole R
- ⭐ Fig.7 (p.13) ![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig07.png]]
  - (a) The prefilling time of MLA (full attention), hybrid GDN-H and our Kimi Linear. (b) The time per output token (TPOT) for MLA, GDN-H and Kimi Linear during decoding. (We use batch size = 1 here for 

### #64 Muon is Scalable for LLM Training

- ⭐ Fig.1 (p.1) ![[assets/crops/muon-is-scalable-for-llm-training-fig01.png]]
  - Scaling up with Muon. (a) Scaling law experiments comparing Muon and Adam. Muon is ∼2× more computational efficient than Adam with compute optimal training. (b) The MMLU performance of our Moonlight m
- ⭐ Fig.2 (p.4) ![[assets/crops/muon-is-scalable-for-llm-training-fig02.png]]
  - Validation loss curves for AdamW (green), Muon without weight decay (red), and Muon with weight decay (blue).
- ⭐ Fig.3 (p.7) ![[assets/crops/muon-is-scalable-for-llm-training-fig03.png]]
  - Fitted scaling law curves for Muon and AdamW optimizers.
- ⭐ Fig.4 (p.10) ![[assets/crops/muon-is-scalable-for-llm-training-fig04.png]]
  - SVD entropy of weight matrices across different training iterations. We categorize the weight matrices into 6 different groups: 1) AttnQO denotes the weight matrices related to the query and output pr
- ⭐ Fig.5 (p.15) ![[assets/crops/muon-is-scalable-for-llm-training-fig05.png]]
  - Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets
- ⭐ Fig.6 (p.15) ![[assets/crops/muon-is-scalable-for-llm-training-fig06.png]]
  - D
- ⭐ Fig.7 (p.17) ![[assets/crops/muon-is-scalable-for-llm-training-fig07.png]]
  - Training dynamics comparison between Moonlight and Moonlight-A
- ⭐ Fig.8 (p.9) ![[assets/crops/muon-is-scalable-for-llm-training-fig08.png]]
  - 6.
- ⭐ Fig.9 (p.18) ![[assets/crops/muon-is-scalable-for-llm-training-fig09.png]]
  - Distribution of singular values for each weight matrix in the attention layers. We use WC to denote the weight matrices at each layer that compress the hidden states to the shared latent spaces for ke
- ⭐ Fig.10 (p.19) ![[assets/crops/muon-is-scalable-for-llm-training-fig10.png]]
  - Distribution of singular values for each weight matrix in the feed-forward network (FFN) layers. We use WI, WV and WO to denote the weight matrices involved in the FFN layer with SwiGLU activation fun

### #65 Attention Residuals

- ⭐ Fig.1 (p.1) ![[assets/crops/attention-residuals-fig01.png]]
  - Overview of Attention Residuals. (a) Standard Residuals: standard residual connections with uniform additive accumulation. (b) Full AttnRes: each layer selectively aggregates all previous layer output
- Fig.2 (p.5) ![[assets/attention-residuals-p05.png]]
  - PyTorch-style pseudo code for Block Attention Residuals. block_attn_res computes softmax attention over block representations using a learned pseudo-query wl; forward is a single-layer pass that maint
- ⭐ Fig.3 (p.6) ![[assets/crops/attention-residuals-fig03.png]]
  - Cache-based pipeline communication example with 4 physical ranks and 2 virtual stages per rank, where hatched boxes denote end of AttnRes blocks. Numbers indicate micro-batch indices. Each rank caches
- ⭐ Fig.4 (p.9) ![[assets/crops/attention-residuals-fig04.png]]
  - Scaling law curves for Attention Residuals. Both Full and Block AttnRes consistently outperform the baseline across all scales. Block AttnRes closely tracks Full AttnRes, recovering most of the gain a
- ⭐ Fig.5 (p.10) ![[assets/crops/attention-residuals-fig05.png]]
  - Training dynamics of Baseline and Block AttnRes. (a) Validation loss during training. (b) Each transformer block’s output magnitude at the end of training. (c) Each transformer block’s gradient magnit
- ⭐ Fig.6 (p.11) ![[assets/crops/attention-residuals-fig06.png]]
  - Effect of block size on validation loss (16-layer model). • Language understanding and reasoning: MMLU [13], MMLU-Pro Hard [55], GPQA-Diamond [41], BBH [48], ARC-Challenge [6], HellaSwag [65], and Tri
- ⭐ Fig.7 (p.12) ![[assets/crops/attention-residuals-fig07.png]]
  - Architecture sweep under fixed compute (≈6.5 × 1019 FLOPs, ≈2.3 × 108 active parameters). Each cell reports validation loss for a (dmodel/Lb, H/Lb) configuration, where Lb = L/2 is the number of Trans
- ⭐ Fig.8 (p.13) ![[assets/crops/attention-residuals-fig08.png]]
  - Depth-wise attention weight distributions for a 16-head model with full (top) and block (bottom) Attention Residuals, averaged over tokens. The model has 16 attention and 16 MLP layers. Each row shows
- ⭐ Fig.9 (p.15) ![[assets/crops/attention-residuals-fig09.png]]
  - Depth mixing matrices M for four residual variants (L=4; Block AttnRes uses block size S=2). Highway is shown with scalar gates for clarity. AttnRes panels show unnormalized ϕ scores; background color

### #66 Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperP

- ⭐ Fig.2 (p.23) ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p23.png]]
  - FlowServe selects the appropriate DistFlow [10] backend based on the network fabric. For MLA models like DeepSeek and Kimi K2, both interconnects satisfy TTFT and TPOT SLAs.
- ⭐ Fig.4 (p.8) ![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig04.png]]
  - Step 1: The sender’s serving engine invokes XCCL’s send, passing the source buffer in the app data area (e.g., KV cache), an eventID (e.g., number of sends), the receiver NPU’s ID, and the number of A
- ⭐ Fig.8 (p.12) ![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig08.png]]
  - Trade-off between MTE and DMA. To improve communication efficiency, we employ NPU-Direct Unified Remote Memory Access (URMA), a technique on Ascend NPUs similar to IBGDA on GPUs [15]. NPU-Direct URMA 
- ⭐ Fig.10 (p.12) ![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig10.png]]
  - This redesign centers on three key components: • First, we introduce the Data Parallel (DP) group abstraction, inspired by SGLang [24].
- ⭐ Fig.12 (p.16) ![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig12.png]]
  - Step 1: Collecting Expert Load Distribution. First, we collect data on expert loads across NPUs. We define expert load as the total number of tokens routed to each expert within a given time interval.
- ⭐ Fig.17 (p.22) ![[assets/crops/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-fig17.png]]
  - 1. A request first arrives at a randomly selected Job Executor (JE), which assigns it to a prefill

### #67 CacheBlend: Fast Large Language Model Serving for RAG with C

- ⭐ Fig.1 (p.2) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig01.png]]
  - Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend’s selective KV recompute. full KV recompute (Figure 1(a)). Despite many optimizations, the delay and computation of prefill
- ⭐ Fig.2 (p.4) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig02.png]]
  - Generation quality improves as more text chunks are retrieved. and fetch top-k relevant chunks from the database, based on the least L2 distance between the embeddings of the query and the chunk respe
- ⭐ Fig.3 (p.4) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig03.png]]
  - An illustrative example of an LLM input with two text chunks prepended to a query. Full KV recompute (b), with- out reusing KV cache, is slow but gives the correct answer. Full KV reuse (c), however, 
- ⭐ Fig.4 (p.5) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig04.png]]
  - Contrasting the attention matrices of (a) full KV recompute and (b) full KV reuse. The yellow boxes highlight the cross-attention. The right-hand side plots show the resulting forward attention matric
- ⭐ Fig.5 (p.6) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig05.png]]
  - Illustrated contrast between (a) full KV recompute and (b) selective KV recompute on one layer. 0 10 20 30 40 50
- ⭐ Fig.6 (p.6) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig06.png]]
  - Attention deviation reduces as we recompute the KV of more tokens on each layer. Importantly, the biggest drop in attention deviation results from recomputing the KV of the tokens with the highest KV 
- ⭐ Fig.7 (p.7) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig07.png]]
  - Distribution of KV deviation of different tokens on one layer. 5 vs. 6 12 vs. 13 21 vs. 22 31 vs. 32
- ⭐ Fig.8 (p.7) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig08.png]]
  - Rank correlation of the KV deviation per token be- tween two consecutive layers. expensive and defeats the purpose of selective KV recom- pute. Instead, we observe that the HKVD tokens on different la
- ⭐ Fig.9 (p.7) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig09.png]]
  - CacheBlend selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer and selecting the tokens among them with high KV 
- ⭐ Fig.10 (p.8) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]
  - (a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay. recompute of one layer, the KV-loading 
- ⭐ Fig.11 (p.9) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig11.png]]
  - CacheBlend system (green stared) in light of LLM context augmented generation for a single request. CacheBlend uses text provided by the retriever, interacts with the storage device(s), and provides K
- ⭐ Fig.12 (p.10) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig12.png]]
  - CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligible quality drop across four datasets and three models.
- ⭐ Fig.13 (p.10) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig13.png]]
  - Generation quality of CacheBlend with Yi-34B vs MapReduce and MapRerank. 7
- ⭐ Fig.14 (p.11) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig14.png]]
  - CacheBlend achieves lower TTFT with higher throughput in RAG scenarios compared with baselines of similar quality. 3 6 9 12 (a) Number of chunks
- ⭐ Fig.15 (p.11) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig15.png]]
  - CacheBlend outperforms baseline with varying chunk numbers, chunk lengths, and batch sizes. • SAMSum [25]: This dataset comprises multiple pairs of dialogues and summaries, and requires the LLM to out
- ⭐ Fig.16 (p.8) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig16.png]]
  - This means that even if the storage device is a fast device (ex. CPU RAM), the delay will be lower-bounded by the minimal recomputation to guarantee quality.
- ⭐ Fig.17 (p.12) ![[assets/crops/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-fig17.png]]
  - CacheBlend’s outperforms baselines when using RAM and slower disks

### #68 CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA

- ⭐ Fig.1 (p.3) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig01.png]]
  - Overview of the three-stage data collection pipeline. We first crawl seed operators from PyTorch
- ⭐ Fig.2 (p.4) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig02.png]]
  - Overview of the agent loop.
- ⭐ Fig.3 (p.5) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig03.png]]
  - Overview of training pipeline. Following a single-turn RL warm-up stage, the sampled trajectories are
- ⭐ Fig.4 (p.10) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig04.png]]
  - Ablation: RFT. Removing RFT causes training reward to collapse. The concurrent increase in actor entropy
- ⭐ Fig.5 (p.10) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig05.png]]
  - Ablation: Value Pretraining. Without Value Pretraining, the critic fails to learn a meaningful value
- ⭐ Fig.6 (p.13) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig06.png]]
  - Examples of operator classes in our training data.
- ⭐ Fig.7 (p.13) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig07.png]]
  - Distribution of the maximum AST similarity between each training sample and all evaluation samples.
- ⭐ Fig.8 (p.22) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig08.png]]
  - Reference operator for diagonal matmul (Case D.2).
- ⭐ Fig.9 (p.23) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig09.png]]
  - Diagonal matmul kernel implementation (Case D.2).
- ⭐ Fig.10 (p.23) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig10.png]]
  - Custom operator for diagonal matmul (Case D.2).
- ⭐ Fig.11 (p.25) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig11.png]]
  - Reference operator for matrix multiplication, division, summation, and scaling (Case D.3).
- ⭐ Fig.12 (p.26) ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p26.png]]
  - Fused sum-then-dot-product kernel implementation (Case D.3).
- ⭐ Fig.13 (p.27) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig13.png]]
  - Custom operator for matrix multiplication, division, summation, and scaling (Case D.3).
- ⭐ Fig.14 (p.28) ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p28.png]]
  - Reference operator for Resnet BasicBlock (Case D.4).
- ⭐ Fig.17 (p.30) ![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig17.png]]
  - Fused add-relu kernel implementation (Case D.4).
- ⭐ Fig.18 (p.31) ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p31.png]]
  - Custom operator for Resnet BasicBlock (Case D.4).

### #69 Single-Rollout Asynchronous Optimization for Agentic Reinfor

- ⭐ Fig.1 (p.1) ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig01.png]]
  - The performance of SAO on reasoning and coding benchmarks. The four reasoning benchmarks are evaluated in a reasoning-with-Python-tool setting, where the baseline is the Qwen3- 30B-A3B SFT model; SWE-
- ⭐ Fig.2 (p.3) ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig02.png]]
  - Overview of SAO with single rollout design. The numbers denote the generation order of trajectories. For SAO, each trajectory becomes available for training immediately upon completion.
- ⭐ Fig.3 (p.6) ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig03.png]]
  - Performance comparison between SAO and GRPO (w/ DIS) during training. It can be observed that SAO almost consistently outperforms the optimized GRPO during the training process on different benchmarks
- ⭐ Fig.4 (p.7) ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig04.png]]
  - Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for SAO and a single-critic-update baseline. (b) Critic gradient norm during value training under full-parameter optimizatio
- ⭐ Fig.5 (p.9) ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig05.png]]
  - Online learning simulation under changing writing-style preferences. 5
- ⭐ Fig.6 (p.13) ![[assets/crops/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-fig06.png]]
  - Training reward for token-level SAO training and step-level variants, where token-level shows better training rewards.

### #70 rLLM: Relational Table Learning with LLMs

- ⭐ Fig.1 (p.1) ![[assets/crops/rllm-relational-table-learning-with-llms-fig01.png]]
  - Trends in global data volume and in LLM token costs by data type
- ⭐ Fig.2 (p.2) ![[assets/crops/rllm-relational-table-learning-with-llms-fig02.png]]
  - The architecture of rLLM analyzed using GNNs. This design efficiently captures inter-table dependencies with minimal architectural complexity.
- ⭐ Fig.3 (p.2) ![[assets/crops/rllm-relational-table-learning-with-llms-fig03.png]]
  - Base data structure in rLLM. Arrows indicate inher- itance relationships and parentheses indicate containment relationships. data, respectively. Overall, this design meets the familiar storage and pro
- ⭐ Fig.4 (p.3) ![[assets/crops/rllm-relational-table-learning-with-llms-fig04.png]]
  - The architecture of BRIDGE columns, which can vary greatly in nature. Due to the diverse types of features and the often limited information provided by tables with fewer columns, it is crucial to map
