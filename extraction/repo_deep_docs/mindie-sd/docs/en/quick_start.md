# Wan2.1-T2V-14B 8-card inference

> 仓 `mindie-sd` · 路径 `docs/en/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/quick_start.md

# mindie-sd 快速开始文档深度解读

---

## 【定位】

本文档是 MindIE SD（昇腾亲和的多模态加速系列套件）的**入门级 Quick Start 指南**，以 **Wan2.1** 文本/图像到视频模型为例，从权重获取、脚本执行、到加速特性效果展示，完整演示了 MindIE SD 在 Atlas 800I A2 推理服务器上完成一次端到端 T2V 推理的全部前置与执行步骤，并量化呈现了 Cache / TP / CFG / Ulysses / FA Sparse 等加速特性在单卡与多卡配置下的加速收益。

---

## 【技术要点】

1. **代码与权重分离架构**：通过 `git clone https://modelers.cn/MindIE/Wan2.1.git` 获取推理脚本（含依赖 `requirements.txt`），但模型权重文件 **不包含** 在仓库中，需单独从 HuggingFace（或 modelscope）下载 Wan2.1-T2V-14B、Wan2.1-I2V-14B-480P、Wan2.1-I2V-14B-720P 三类权重。
2. **权重目录结构**：标准布局为 `Wan2.1-T2V-14B/{config.json, model_index.json, models/{dit, vae, text_encoder}, ...}`，即 DiT 主干、VAE 解码、文本编码器分别落在 `models/` 下的子目录。
3. **执行方式**：将 `MindIE-SD/examples/wan/infer_t2v.sh` 拷贝到仓库根目录，通过 `export model_base="/path/to/Wan2.1-T2V-14B"` 设置权重路径后执行 `bash infer_t2v.sh` 启动 **8 卡** T2V 推理。
4. **五大加速特性同时启用**：Cache（AttentionCache）、TP（Tensor Parallel）、FA Sparse（RainFusion）、CFG（CFG Parallel）、Ulysses（Ulysses Parallel），测试硬件为 **Atlas 800I A2 推理服务器（1\*64G）**，固定输出分辨率 **H\*W 832\*480**，`sample_steps=50`。
5. **单卡基线与 Cache 加速梯度**：基线 **860.2s**；Cache Speedup 1.6 → 631.7s（1.36x）；Cache Speedup 2.0 → 541.8s（1.59x）；Cache Speedup 2.4 → **516.9s（1.66x，最佳）**。
6. **多卡并行策略选择**：在 2/4/8 卡配置下，分别评估 VAE、TP、CFG、Ulysses 单一并行策略以及 **CFG + TP / CFG + Ulysses 混合并行**，8 卡 `CFG=2 + Ulysses=4 + VAE` 取得全表最佳 **76.4s（7.34x）**。

---

## 【关键机制与数据】

### 工作原理 / 数据流

MindIE SD 的推理数据流按照"获取脚本 → 获取权重 → 设置 `model_base` → 执行 `infer_t2v.sh`"的顺序串接。脚本入口读入 `model_base` 指向的本地权重目录，按 `models/{dit, vae, text_encoder}` 拆分子模块加载；运行时依据所选加速特性叠加 Cache 缓存复用、TP/Ulysses 张量/序列切分、CFG 并行双分支以及 RainFusion FA Sparse 优化，最终生成 832\*480 视频。

### 性能数据（原文标注的实测值）

**原文（单卡 Cache 加速）**：基线 860.2s → + Cache Speedup 1.6：631.7s（1.36x）→ + Cache Speedup 2.0：541.8s（1.59x）→ + Cache Speedup 2.4：516.9s（1.66x，最佳）。

**原文（双卡单一并行）**：VAE 548.8s（1.02x）→ TP 502.8s（1.12x）→ CFG 332.6s（1.69x）→ Ulysses 327.6s（**1.71x，最佳**）。

**原文（4 卡组合并行）**：TP=4+VAE 204.0s（2.754x）→ CFG=2+TP=2+VAE 175.8s（3.19x）→ Ulysses=4+VAE 151.1s（3.71x）→ CFG=2+Ulysses=2+VAE 147.9s（**3.79x，最佳**）。

**原文（8 卡组合并行）**：TP=8+VAE 141.5s（3.96x）→ CFG=2+TP=4+VAE 102.9s（5.45x）→ Ulysses=8+VAE 78.1s（7.18x）→ CFG=2+Ulysses=4+VAE 76.4s（**7.34x，全表最佳**）。

---

## 【表格解读】

### 表 1：模型权重下载清单（原文逐字还原）

| Model | Description | Weight Download |
| ------ | ------ | ---------- |
| Wan2.1-T2V-14B | Text-to-Video | [HuggingFace](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B) |
| Wan2.1-I2V-14B-480P | Image-to-Video (480P) | [HuggingFace](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P) |
| Wan2.1-I2V-14B-720P | Image-to-Video (720P) | [HuggingFace](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-720P) |

**解读**：列出 Wan2.1 系列在 MindIE SD 中已验证的三种模型权重，三者均来自 HuggingFace 上的 `Wan-AI` 组织仓库。T2V-14B 面向文本生成视频，I2V-14B 提供 480P 与 720P 两种图像生成视频分辨率；本表是用户从外部获取权重的官方入口指引，文中另补充 modelscope 为可选下载源。

### 表 2：单卡 Cache 加速结果（原文逐字还原）

| Baseline | + Cache Speedup 1.6 | + Cache Speedup 2.0 | + Cache Speedup 2.4 |
| :---: | :---: | :---: | :---: |
| 860.2s | 631.7s 1.36x | 541.8s 1.59x | 516.9s ***1.66x** |
| ![](figures/single_card_base_fa.gif) | ![](figures/single_card_fa_attentioncache_speedup_1_6.gif) | ![](figures/single_card_fa_attentioncache_speedup_2_0.gif) | ![](figures/single_card_fa_attentioncache_speedup_2_4.gif) |

**解读**：以 832\*480 分辨率、`sample_steps=50`、单卡（1\*64G）下的 50 步 E2E 时间为度量。基线 860.2s 对应未启用 AttentionCache 的情况；随着 Cache Speedup 档位从 1.6 提升至 2.4，耗时从 631.7s 单调下降到 516.9s，加速比从 1.36x 提升到 1.66x（粗体加 `*` 标注为最佳），表明 AttentionCache 通过复用跨步注意力结果可显著压缩 T2V 推理时间。

### 表 3：双卡单并行策略结果（原文逐字还原）

| Model | Cards | Parallel Strategy | Video Output Resolution | Operator Optimization | Cache Optimization | FA Sparse | 50-Step E2E Time(s) | Speedup |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Wan2.1 | 2 | VAE | 832*480 | Yes | Yes | Yes | 548.8 | 1.02x |
| Wan2.1 | 2 | TP | 832*480 | Yes | Yes | Yes | 502.8 | 1.12x |
| Wan2.1 | 2 | CFG | 832*480 | Yes | Yes | Yes | 332.6 | 1.69x |
| Wan2.1 | 2 | Ulysses | 832*480 | Yes | Yes | Yes | 327.6 | ***1.71x** |

**解读**：所有四组实验均同时开启 Operator Optimization、Cache Optimization、FA Sparse，仅在并行策略列上变化。VAE 并行收益最低（548.8s，1.02x），TP 略优（502.8s，1.12x），CFG 与 Ulysses 显著拉开差距（332.6s / 327.6s），Ulysses 取得最佳 1.71x（加 `*`），表明在双卡规模下序列维度切分比张量切分更能放大可并行度。

### 表 4：多卡组合并行策略结果（原文逐字还原）

| Model | Cards | Parallel Strategy | Video Output Resolution | Operator Optimization | Cache Optimization | FA Sparse | 50-Step E2E Time(s) | Speedup |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Wan2.1 | 4 | TP=4, VAE | 832*480 | Yes | Yes | Yes | 204.0 | 2.754x |
| Wan2.1 | 4 | CFG=2, TP=2, VAE | 832*480 | Yes | Yes | Yes | 175.8 | 3.19x |
| Wan2.1 | 4 | Ulysses=4, VAE | 832*480 | Yes | Yes | Yes | 151.1 | 3.71x |
| Wan2.1 | 4 | CFG=2, Ulysses=2, VAE | 832*480 | Yes | Yes | Yes | 147.9 | ***3.79x** |
| Wan2.1 | 8 | TP=8, VAE | 832*480 | Yes | Yes | Yes | 141.5 | 3.96x |
| Wan2.1 | 8 | CFG=2, TP=4, VAE | 832*480 | Yes | Yes | Yes | 102.9 | 5.45x |
| Wan2.1 | 8 | Ulysses=8, VAE | 832*480 | Yes | Yes | Yes | 78.1 | 7.18x |
| Wan2.1 | 8 | CFG=2, Ulysses=4, VAE | 832*480 | Yes | Yes | Yes | 76.4 | ***7.34x** |

**解读**：4 卡与 8 卡规模下，组合并行（CFG 与 Ulysses/TP 同时启用）相对单一并行均带来额外收益。4 卡从纯 TP=4（204.0s，2.754x）演进到 CFG=2+Ulysses=2+VAE（147.9s，**3.79x，最佳**）；8 卡从纯 TP=8（141.5s，3.96x）演进到 CFG=2+Ulysses=4+VAE（76.4s，**7.34x，全表最佳**）。整体趋势：① 相同卡数下 Ulysses 路线 > TP 路线；② CFG 与序列/张量并行正交叠加可再获得 ~25%~30% 收益；③ 卡数从 4 升至 8 时最优策略耗时由 147.9s 进一步压缩到 76.4s（约 1.93x），与卡数翻倍接近线性。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **[Installation Guide](./installation.md)**：本文档开头声明，在开始推理前必须先按此文档完成环境搭建与 MindIE SD 安装，是 Quick Start 的**前置依赖**。
- **[Model/Framework Support Matrix (features/supported_matrix.md)](./features/supported_matrix.md)**：当用户需使用 FLUX.1-dev、HunyuanVideo 等**其他模型**的权重时，需查阅该矩阵获取对应下载链接。
- **[Parameter Configuration (../../examples/wan/parameter_config.md)](../../examples/wan/parameter_config.md)**：对 `infer_t2v.sh` 与 `model_base` 等参数提供**详细释义**，本文档对其仅做引用，不展开。
- **[AttentionCache (./features/cache.md#attentioncache)](./features/cache.md#attentioncache)**：单卡 Cache 加速结果章节对应的底层特性实现文档。
- **[Tensor Parallel (./features/parallelism.md)](./features/parallelism.md)**：双卡与多卡表中 TP 行的实现来源。
- **[CFG Parallel (./features/parallelism.md)](./features/parallelism.md)**：CFG 行及"CFG=N"组合并行项的实现来源；文档中两次引用 `./features/parallelism.md`。
- **[RainFusion / FA Sparse (./features/sparse.md)](./features/sparse.md)**：所有性能表中 "FA Sparse" 列的底层特性实现。
- **[Ulysses Sequence Parallel (./features/parallelism.md#ulysses-sequence-parallel)](./features/parallelism.md#ulysses-sequence-parallel)**：Ulysses 行与"Ulysses=N"组合并行项的锚点链接，锚到 parallelism 文档的序列并行小节。

文档在末尾通过 `*` 标注最佳结果，形成 Cache / TP / CFG / Ulysses / FA Sparse 五大特性间的横向对比，并将最简执行路径前置、性能收益后置，构成了"先用起来 → 再看能跑多快"的递进叙事。

---

## 【使用方法】

### 1. 获取推理脚本
```bash
git clone https://modelers.cn/MindIE/Wan2.1.git && cd Wan2.1
pip install -r requirements.txt
```

### 2. 获取模型权重（以 Wan2.1-T2V-14B 为例）
从 HuggingFace（[Wan-AI/Wan2.1-T2V-14B](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B)）或 modelscope 下载，权重需落地为：
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

### 3. 执行推理（8 卡示例）
```bash
cp MindIE-SD/examples/wan/infer_t2v.sh ./
export model_base="/path/to/Wan2.1-T2V-14B"
bash infer_t2v.sh
```

### 关键配置项
- **`model_base`**：环境变量，指向本地权重目录的根路径，是脚本读取权重的唯一入口；详细参数（如 `sample_steps` 等）见 `examples/wan/parameter_config.md`。
- **`sample_steps`**：固定为 **50**（性能数据均在此设定下测得）。
- **输出分辨率**：性能表中固定为 **H\*W = 832\*480**。

### 启用加速特性
本 Quick Start 文档未给出具体的特性开关命令或配置文件字段，性能表中各特性（Cache / TP / CFG / Ulysses / FA Sparse）**同时启用**，其启用方式的原文链接为 `./features/cache.md#attentioncache`、`./features/parallelism.md`、`./features/sparse.md`、`./features/parallelism.md#ulysses-sequence-parallel`，配置命令细节需到各特性文档中查阅，原文未涉及。

## 图文联合解读

- `single_card_base_fa.gif`: # 图文关联分析

## 1) 图片内容
图示为两只猫戴着红色拳击手套在聚光灯舞台上对峙的写实照片，并非技术架构图，无任何结构、数据流或标注信息。

## 2) 技术结论
该图片**无法论证任何技术结论**，不涉及模型并行、显存分配或推理流水线等8卡部署相关概念。

## 3) 与文档论点关系
该图与"Wan2.1-T2V-14B 8-card 推理"主题**完全无关**，疑为占位符错误或误传。文档论及权重目录结构（dit/vae/text_en）、多模型支持及环境配置，应配以分布式推理拓扑图或权重组织示意图方能有效辅助说明。建议替换为正确的架构配图。
- `single_card_fa_attentioncache_speedup_1_6.gif`: **图文不符提示**：

1) **图中所画**：该图实为一张AI生成的猫咪拳击对战艺术照——两只戴拳套的猫在聚光灯下对峙，并非任何技术结构图、数据流图或架构示意图。

2) **技术论证**：无。图中未呈现8卡推理的拓扑结构、模型并行策略、张量切分方式、显存分配或流水线调度等任何技术要素，无法论证任何结论。

3) **与文档关系**：文档主题为Wan2.1-T2V-14B模型在MindIE SD上的8卡部署推理流程，需要展示例如：8卡GPU分组、DiT/VAE/Text Encoder模块映射、TP/PP并行策略、数据并行通信等架构图。当前配图与文档论点**完全无关**，建议替换为对应的推理部署架构示意图。
- `single_card_fa_attentioncache_speedup_2_0.gif`: **图文不匹配警告** ⚠️

1. **图里画了什么**：图片显示两只猫戴着红色拳击手套在灯光舞台上对峙——是AI生成的写实风格图像，并非技术示意图。

2. **论证了什么技术结论**：无法论证任何技术结论，因为该图片与"Wan2.1-T2V-14B 8-card 推理"主题毫无关联。

3. **与文档论点的关系**：文档讨论的是分布式推理（8卡）、模型权重目录结构（dit/vae/text_en）、MindIE SD安装等工程内容；而插图为拳击小猫，明显属于**配图错放**——可能是文档自动化生成时误填占位图，或误将T2V文生视频模型的样例输出当作架构图插入。

**建议**：替换为真正的8卡并行推理拓扑图（如DiT+VAE+TextEncoder跨卡切分、数据并行/张量并行的NCCL通信示意图），才能匹配文档论点。
- `single_card_fa_attentioncache_speedup_2_4.gif`: **图文联合解读**

1) **画面内容**：静态图像呈现两只戴红色拳击手套的猫咪，在聚光灯下的擂台两侧对峙，姿态对称、动作张力强，光影富有戏剧性。

2) **技术结论**：作为 Wan2.1-T2V-14B 的生成样例，论证该模型具备高质量文生视频能力——可刻画多主体交互、复杂肢体动作、动态光影及电影级构图。

3) **与文档关系**：文档章节聚焦"Wan2.1-T2V-14B 8-card 推理"快速上手流程，配图并非展示分布式并行架构（无8卡拓扑/数据流标注），而是作为**生成效果示例**，直观证明在 MindIE SD 部署下该 14B 模型可产出符合提示语且视觉表现优异的视频帧，支撑"快速启动即可获得高质量生成"的论点。
