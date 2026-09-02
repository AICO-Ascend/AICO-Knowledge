# 快速开始

> 仓 `mindie-sd` · 路径 `docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/quick_start.md

# 一体化深度解读：MindIE SD 快速开始（Wan2.1 文生视频）

## 【定位】
本文档以 Wan2.1 文生视频模型为例，给出 MindIE SD 套件的端到端**上手流程**：从克隆推理脚本、获取模型权重，到在 Atlas 800I A2 服务器上跑通单卡/多卡推理，并以实测数据展示 AttentionCache、TP、CFG、Ulysses 等加速特性在 50 步 E2E 推理下的加速效果。它是一篇**面向首次使用者的"安装—跑通—看效果"三步式指南**。

---

## 【技术要点】

1. **推理脚本获取**：从魔乐社区（modelers.cn）克隆 `MindIE/Wan2.1` 仓库并 `pip install -r requirements.txt` 安装依赖，**注意此仓库只含脚本、不含权重**。
2. **模型权重**：Wan2.1 三个变体均从 HuggingFace 获取——`Wan2.1-T2V-14B`（文生视频）、`Wan2.1-I2V-14B-480P`（图生视频 480P）、`Wan2.1-I2V-14B-720P`（图生视频 720P），也可从 modelscope 拉取；权重目录固定包含 `config.json`、`model_index.json` 以及 `models/{dit,vae,text_encoder}/`。
3. **运行入口命令**：把权重路径写到 `model_base` 环境变量，然后复制并执行 `MindIE-SD/examples/wan/infer_t2v.sh`；命令示例给出 **Wan2.1-T2V-14B 8 卡推理**这一具体规格。
4. **加速特性集合（同一台 Atlas 800I A2 1*64G 上对比）**：Cache（AttentionCache）、TP（Tensor Parallel）、FA 稀疏（RainFusion）、CFG 并行、Ulysses 并行。基准测试参数锁定为视频分辨率 `H*W=832*480`、`sample_steps=50`。
5. **单卡 Cache 加速比**：基线 860.2s → 加速比 1.36x/1.59x/**1.66x**（最优，516.9s），呈现三档 Cache 配置可调。
6. **双卡单策略**：VAE 1.02x → TP 1.12x → CFG 1.69x → **Ulysses 1.71x（最优，327.6s）**。
7. **多卡组合**：4 卡最优为 `CFG=2, Ulysses=2, VAE` → 147.9s / **3.79x**；8 卡最优为 `CFG=2, Ulysses=4, VAE` → 76.4s / **7.34x**。

---

## 【关键机制与数据】

**工作原理（按文档叙述）**：

- 文档将推理流程抽象为「脚本 → 权重 → 环境变量 → 启动脚本」四步，不展开内部模型/算子实现细节（细节被外链到各 feature 文档）。
- 加速特性是**正交可叠加**的：在所有双卡/多卡测试里，算子优化、cache 算法优化、FA 稀疏三列均为 √，因此加速比差异主要由"并行策略"决定。
- 多卡组合体现两个自由度：**并行维度数量**（4 卡 vs 8 卡）与**并行策略混合**（如 `CFG=2, Ulysses=2` 表示把 2 个 seed 并行交给 Ulysses 序列并行再做 2 路 CFG 并行）。

**关键实测数据（原文）**：

- 单卡基线：**860.2s**；最优 Cache 档：**516.9s / 1.66x**（50 步 E2E，832×480）。
- 双卡最优：Ulysses，**327.6s / 1.71x**。
- 4 卡最优：CFG=2, Ulysses=2, VAE，**147.9s / 3.79x**。
- 8 卡最优：CFG=2, Ulysses=4, VAE，**76.4s / 7.34x**。

**加速比单调性观察（基于原文表）**：
- 4 卡组：TP=4 (2.754x) < CFG=2+TP=2 (3.19x) < Ulysses=4 (3.71x) < CFG=2+Ulysses=2 (3.79x)。
- 8 卡组：TP=8 (3.96x) < CFG=2+TP=4 (5.45x) < Ulysses=8 (7.18x) < CFG=2+Ulysses=4 (7.34x)。
- **结论**：在相同卡数下，Ulysses > TP；CFG 与 Ulysses 组合 > Ulysses 单独使用 > TP 与 CFG 组合。

---

## 【表格解读】

### 表 1：Wan2.1 支持的模型与权重下载

| 模型 | 说明 | 权重下载 |
|------|------|----------|
| Wan2.1-T2V-14B | 文生视频 | [HuggingFace](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B) |
| Wan2.1-I2V-14B-480P | 图生视频（480P） | [HuggingFace](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P) |
| Wan2.1-I2V-14B-720P | 图生视频（720P） | [HuggingFace](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-720P) |

**逐行解读**：
- 第 1 行：本文示例所用的文生视频主力模型，14B 参数量。
- 第 2 行：480P 图生视频变体，分辨率较低，适合资源受限或快速验证。
- 第 3 行：720P 图生视频变体，分辨率更高但显存/算力需求更大。
- 共同点：三个变体均**只提供 HuggingFace 链接**，modelscope 仅在文末 NOTE 中提及作为备选。

### 表 2：Wan2.1-T2V-14B 权重目录结构

```text
Wan2.1-T2V-14B/
├── config.json
├── model_index.json
├── models/
│   ├── dit/
│   ├── vae/
│   └── text_encoder/
└── ...
```

**解读**：diffusers 风格的三组件目录——`dit`（主扩散 Transformer）、`vae`（视频编解码）、`text_encoder`（文本编码器），顶层由 `model_index.json` 索引。这是能否被 MindIE SD 正确加载的前置条件。

### 表 3：单卡 Cache 加速效果

| Baseline | + Cache 加速比1.6 | + Cache 加速比2.0 | + Cache 加速比2.4 |
|:---:|:---:|:---:|:---:|
| 860.2s | 631.7s 1.36x | 541.8s 1.59x | 516.9s ***1.66x** |
| ![](figures/single_card_base_fa.gif) | ![](figures/single_card_fa_attentioncache_speedup_1_6.gif) | ![](figures/single_card_fa_attentioncache_speedup_2_0.gif) | ![](figures/single_card_fa_attentioncache_speedup_2_4.gif) |

**逐行解读**：
- 基线 860.2s（无任何加速）；随 Cache 加速比从 1.6 → 2.0 → 2.4 提高，耗时**单调下降**：631.7s → 541.8s → 516.9s，对应加速比 1.36x → 1.59x → **1.66x**（标 * 为最优档）。
- 下方 4 个 .gif 链接对应视频生成的可视化对比结果。

### 表 4：双卡单个并行策略效果

| 模型 | 卡数 | 并行策略 | 视频输出分辨率 | 算子优化 | cache 算法优化 | FA 稀疏 | 50 步 E2E 耗时(s) | 加速比 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Wan2.1 | 2 | VAE | 832*480 | √ | √ | √ | 548.8 | 1.02x |
| Wan2.1 | 2 | TP | 832*480 | √ | √ | √ | 502.8 | 1.12x |
| Wan2.1 | 2 | CFG | 832*480 | √ | √ | √ | 332.6 | 1.69x |
| Wan2.1 | 2 | Ulysses | 832*480 | √ | √ | √ | 327.6 | ***1.71x** |

**逐行解读**：
- 第 1 行 VAE（双卡 VAE 解码并行）：548.8s，1.02x——仅靠 VAE 并行几乎没有收益，因为主要瓶颈在 DiT 推理。
- 第 2 行 TP（Tensor Parallel 张量并行）：502.8s，1.12x——对 14B 模型有适度收益。
- 第 3 行 CFG：332.6s，1.69x——CFG 并行显著削减一半 DiT 前向次数，效果接近 Ulysses。
- 第 4 行 **Ulysses**：327.6s，**1.71x（最优）**，略胜 CFG。

### 表 5：多卡并行策略组合效果

| 模型 | 卡数 | 并行策略 | 视频输出分辨率 | 算子优化 | cache 算法优化 | FA 稀疏 | 50 步 E2E 耗时(s) | 加速比 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Wan2.1 | 4 | TP=4, VAE | 832*480 | √ | √ | √ | 204.0 | 2.754x |
| Wan2.1 | 4 | CFG=2, TP=2, VAE | 832*480 | √ | √ | √ | 175.8 | 3.19x |
| Wan2.1 | 4 | Ulysses=4, VAE | 832*480 | √ | √ | √ | 151.1 | 3.71x |
| Wan2.1 | 4 | CFG=2, Ulysses=2, VAE | 832*480 | √ | √ | √ | 147.9 | ***3.79x** |
| Wan2.1 | 8 | TP=8, VAE | 832*480 | √ | √ | √ | 141.5 | 3.96x |
| Wan2.1 | 8 | CFG=2, TP=4, VAE | 832*480 | √ | √ | √ | 102.9 | 5.45x |
| Wan2.1 | 8 | Ulysses=8, VAE | 832*480 | √ | √ | √ | 78.1 | 7.18x |
| Wan2.1 | 8 | CFG=2, Ulysses=4, VAE | 832*480 | √ | √ | √ | 76.4 | ***7.34x** |

**逐行解读**：
- **4 卡组**：4 种策略中 `CFG=2, Ulysses=2` 最优 3.79x；与最差 TP=4 相比节约 56.1s（节省 27.5%）。
- **8 卡组**：4 种策略中 `CFG=2, Ulysses=4` 最优 7.34x；与最差 TP=8 相比节约 65.1s（节省 46.0%）。
- 跨组观察：8 卡最优（7.34x）相比单卡基线 860.2s，耗时下降到 76.4s，**约 11.3× 加速**（与表中 7.34x 不同，因为 7.34x 是相对各自最优配置计算的——这里实际相对单卡加速比 = 860.2/76.4 ≈ 11.26x；原文未直接给此数字，故仅作分析陈述）。
- **通用结论**：在所有组合里 Ulysses + CFG 都优于 TP + CFG，验证了序列并行对长视频 DiT 的适配优势。

---

## 【公式解读】

**原文无公式**。文中所有数值结果都以表格形式直接给出（耗时 s、加速比 x），未出现 LaTeX 表达式或伪代码公式。

---

## 【关联】

- **[安装指导](./installation.md)**：文档开头要求"开始推理前，请先按安装指导完成环境准备和 MindIE SD 安装"——是本文的前置依赖。
- **[Modelers - MindIE/Wan2.1](https://modelers.cn/models/MindIE/Wan2.1)**：提供 Wan2.1 推理脚本与模型索引，是脚本与权重的官方仓库。
- **[参数配置](../../examples/wan/parameter_config.md)**：`infer_t2v.sh` 中 `model_base` 等参数的详细说明外链到此文档。
- **[AttentionCache](./features/cache.md#attentioncache)**：单卡 Cache 加速特性的具体机制在 cache.md 中说明，本文只引用其名称与加速比档位（1.6/2.0/2.4）。
- **[Tensor Parallel（TP）](./features/parallelism.md)**：双卡/多卡表中"TP"对应的特性文档。
- **[CFG 并行](./features/parallelism.md)**：同一份 parallelism.md 中也覆盖了 CFG 并行机制。
- **[Ulysses 序列并行](./features/parallelism.md#ulysses-sequence-parallel)**：本文多卡表中最优加速来源，锚点跳转至 parallelism.md 的 ulysses-sequence-parallel 小节。
- **[FA 稀疏 / RainFusion](./features/sparse.md)**：所有表中均默认启用的"FA 稀疏"特性，对应文档在 sparse.md。
- **[模型/框架支持情况（features/supported_matrix.md）](./features/supported_matrix.md)**：用于查询 FLUX.1-dev、HunyuanVideo 等其他模型的权重获取链接与适配情况，是本文 NOTE 中引导用户继续扩展的接口。

整体看，本文档是 MindIE SD 的**导航门面**：每一个加速名词都精确外链到对应 feature 文档，使读者能顺藤摸瓜深入到各 feature 的内部实现。

---

## 【使用方法】

**1. 环境前置**（原文引用，未展开细节）：
- 按 [安装指导](./installation.md) 完成 MindIE SD 安装。

**2. 克隆并安装脚本**：
```bash
git clone https://modelers.cn/MindIE/Wan2.1.git && cd Wan2.1
pip install -r requirements.txt
```

**3. 下载权重（三种变体之一）**：
- `Wan2.1-T2V-14B`（文生视频，本文示例）
- `Wan2.1-I2V-14B-480P`（图生视频 480P）
- `Wan2.1-I2V-14B-720P`（图生视频 720P）
- 也可从 modelscope 获取（原文 NOTE 提示）。
- 必须保证目录结构为 `Wan2.1-T2V-14B/{config.json, model_index.json, models/{dit,vae,text_encoder}/}`。

**4. 启动 8 卡推理（Wan2.1-T2V-14B）**：
```bash
cp MindIE-SD/examples/wan/infer_t2v.sh ./
export model_base="/path/to/Wan2.1-T2V-14B"
bash infer_t2v.sh
```

**5. 加速特性启用方式**：原文未列出各特性的具体配置项（如 AttentionCache 的 `cache_ratio`、Ulysses 的 `sequence_parallel_size` 等参数名称与取值），仅给出**它们的效果数据**。具体如何开启 AttentionCache、TP、CFG、Ulysses、FA 稀疏（RainFusion）需查阅上文关联的各 feature 文档：
- Cache 档位 → `features/cache.md#attentioncache`
- TP/CFG/Ulysses 规模（=2/=4/=8）→ `features/parallelism.md`
- FA 稀疏（RainFusion）→ `features/sparse.md`
- 推理脚本详细参数 → `examples/wan/parameter_config.md`

**6. 加速特性推荐组合（基于原文实测）**：
- 单卡：直接启用 **AttentionCache（加速比 2.4 档）**，可达 1.66x。
- 双卡：**Ulysses 并行**，1.71x 最优。
- 4 卡：**CFG=2 + Ulysses=2 + VAE**，3.79x 最优。
- 8 卡：**CFG=2 + Ulysses=4 + VAE**，7.34x 最优。

## 图文联合解读

- `single_card_base_fa.gif`: 图展示暖色舞台灯光下，两只拟人化猫戴红色拳套搏斗，突出主体、动作与光影。图中未呈现模型结构或数据流；它作为 Wan2.1 文生视频的输出样例，辅助说明 MindIE SD 的推理能力，不能直接证明加速效果。
- `single_card_fa_attentioncache_speedup_1_6.gif`: 两只猫戴着红色拳套，在聚光灯下对垒，象征多卡、多路或不同优化方案的性能竞争。图示强化“加速效果”章节，但其本身不提供技术数据，具体结论仍以配套测试结果为准。
- `single_card_fa_attentioncache_speedup_2_0.gif`: 图中不是技术结构图，而是两只猫戴红色拳套在聚光灯下对拳，类似拳击擂台画面。它作为视频生成示例，展示文本可转化为具有动作与场景感的视频帧；但没有数据流或性能标注，不能证明 Cache、多卡等加速效果，仅与“文生视频/加速效果展示”主题呼应。
- `single_card_fa_attentioncache_speedup_2_4.gif`: ① 图中两只猫在暖色聚光灯下面对面站立，挥动红色拳套，形似拳击对决；没有技术结构、数据流或参数标注。  
② 画面以“对战”隐喻性能比较，可能对应单卡/多卡及不同加速特性的对照，但本身不提供实测结论。  
③ 该图呼应文档的“加速效果展示”主题，实际依据仍应来自后续数据与配置说明。
