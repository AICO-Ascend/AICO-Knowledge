# Quick Start

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/docs/en/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/docs/en/quick_start.md

# 一体化深度解读: BERT PyTorch (NPU 适配) Quick Start 文档

---

## 【定位】

本篇文档面向使用 NPU (Ascend Atlas 900 A2 PoDc) 平台的 PyTorch 用户, 提供 **BERT-base 模型在 SQuADv1.1 数据集上完成训练 (含精度与性能两条路径) 的一站式 Quick Start 指引**, 覆盖环境准备、字典下载、预训练权重获取、单/八卡训练启动命令以及训练结果性能表, 并附常见问题 (首次训练预处理耗时长) 说明。

---

## 【技术要点】

- **模型规模 (原文):** BERT-base 由 **12 层**、**768 维隐向量**、**12 个 self-attention head**、总计 **110M 参数** 构成; 整体框架由多层 Transformer encoder 堆叠而成。
- **每层 encoder 结构 (原文):** 由 *multi-head-attention* 子层与 *feed-forward* 子层组成; 每个 attention 机制负责"基于目标词与句中所有词的相关性, 对目标词重新编码"。
- **Attention 三步计算 (原文):** ①计算词与词之间的相关性 → ②对相关性得分做归一化 → ③以相关性得分为权重对所有词编码做加权求和, 得到目标词编码。
- **训练支持规模 (原文):** 同时支持 **单节点单设备 (1p)** 与 **单节点八设备 (8p)** 两种拓扑, 每种拓扑都提供 `full` (精度) 与 `performance` (性能) 两个脚本。
- **依赖与加速库 (原文):** 通过 `pip install -r requirements.txt` 安装依赖; 另外按 **Ascend Apex Installation Guide** 单独安装 Apex 加速库。
- **数据集与目录结构 (原文):** 使用 **SQuADv1.1**; 需放置在源码根目录下名为 `v1.1/` 的目录中, 内部含 `train-v1.1.json` / `dev-v1.1.json` / `evaluate-v1.1.py`。
- **字典文件 (原文):** 在 `v1.1/data/uncased_L-24_H-1024_A-16/` 下放置 `bert-base-uncased-vocab.txt` (目录名对应 Large 配置 24 层/1024 隐层/16 head, 但此处用于 base 训练的 vocab)。
- **预训练权重 (原文):** 名为 `bert_base.pt`; 训练命令中 `--ckpt_path` 只需指定所在目录, 无需带文件名。
- **关键性能数字 (原文 Table 2, 2025-05-10 更新):** Bert-Base 8p 在 Atlas 900 A2 PoDc 上 **FP16 达 3118 FPS** (对比 Competitor 2463); Bert-Large 8p 同平台达 **1084 FPS** (对比 870.4)。

---

## 【关键机制与数据】

### 工作原理 (BERT-base attention 三步)
原文以"目标词与全句所有词的相关性"为核心, 将 attention 机制抽象为: 
1. **相关性计算** — 对目标词与句子内所有词两两打分;
2. **归一化** — 对得到的原始分数做归一化 (原文仅描述为"normalizing the relevance scores", 未给出 softmax 等具体公式);
3. **加权求和** — 用归一化后的相关性作为权重, 对所有词编码做加权求和, 输出目标词的新编码。

此机制在每一层、每一个 head 中并行执行, 多个 head 的输出经拼接/投影后送入 feed-forward 子层, 再逐层堆叠形成 BERT-base 的整体编码能力。

### 数据流 (训练链路)
1. 在源码根目录创建 `v1.1/` 并放置 SQuADv1.1 原始文件与评估脚本;
2. 在 `v1.1/data/uncased_L-24_H-1024_A-16/` 放置 `bert-base-uncased-vocab.txt` 字典;
3. 通过 NVIDIA DeepLearningExamples 链接获取 `bert_base.pt` 预训练权重, 并放置于 `--ckpt_path` 指定的目录;
4. 调用 `train_base_full_1p.sh` / `train_base_performance_1p.sh` / `train_base_full_8p.sh` / `train_base_performance_8p.sh` 之一启动训练;
5. 训练结束后, 权重文件保存于 *当前目录*, 同时输出模型训练精度与性能信息。

### 性能数据 (原文 Table 2, FP16, 8 卡)
| 配置 | FPS |
|---|---|
| Bert-Base 8p — Competitor | 2463 |
| Bert-Base 8p — Atlas 900 A2 PoDc | 3118 |
| Bert-Large 8p — Competitor | 870.4 |
| Bert-Large 8p — Atlas 900 A2 PoDc | 1084 |

**Atlas 900 A2 PoDc 相对 Competitor 的吞吐提升 (据原文数字算得):**
- Bert-Base 8p: 3118 ÷ 2463 ≈ **1.266×** (原文未给出此比值, 此处仅为根据原文两个数字相除得出);
- Bert-Large 8p: 1084 ÷ 870.4 ≈ **1.246×** (同上, 原文未直接声明)。

### 缓存机制 (FAQ, 原文)
首次训练第一步执行 SQuAD 预处理, **典型耗时约十分钟**; 完成后会在数据集同目录生成缓存文件, 后续训练运行速度将显著提升。

---

## 【表格解读】

### 原文唯一表格 — "Table 2 Training results"

原文表格**逐字还原**:

| Name | Precision Type | FPS |
| :------ |:-------:|:------:|
| Bert-Base 8p-Competitor | FP16 | 2463 |
| Bert-Base 8p-Atlas 900 A2 PoDc | FP16 | 3118 |
| Bert-Large 8p-Competitor | FP16 | 870.4 |
| Bert-Large 8p-Atlas 900 A2 PoDc | FP16 | 1084 |

**逐行解读 (仅基于原文呈现信息):**

1. **Bert-Base 8p — Competitor | FP16 | 2463 FPS**
   第三方对照平台在 8 卡 BERT-base 上的吞吐基线, 作为 NPU 平台的对照基准。

2. **Bert-Base 8p — Atlas 900 A2 PoDc | FP16 | 3118 FPS**
   本仓库 (NPU 适配) 在 Atlas 900 A2 PoDc 上 8 卡 BERT-base 的吞吐; 较 Competitor 高出 655 FPS (原文未直接给出差值, 此处为简单相减)。

3. **Bert-Large 8p — Competitor | FP16 | 870.4 FPS**
   第三方对照平台在 8 卡 BERT-Large 上的吞吐基线 (BERT-Large 参数量远高于 base, 故 FPS 显著下降)。

4. **Bert-Large 8p — Atlas 900 A2 PoDc | FP16 | 1084 FPS**
   本仓库在 Atlas 900 A2 PoDc 上 8 卡 BERT-Large 的吞吐; 较 Competitor 高出 213.6 FPS (同上为简单相减, 原文未声明)。

> 注: 表中所有数字仅以 FPS 一种指标展示, **未涉及 precision/recall/F1 等 SQuAD 精度指标**, 也未注明 batch size、sequence length、warmup/step 数等训练超参; 原文标注数据更新日期为 **2025-05-10**。

---

## 【公式解读】

原文无公式 (无 LaTeX 表达式, 也无伪代码形式的数学式)。  
唯一与"数值计算"相关的描述是 attention 三步流程的散文式说明:

> *"…calculating the relevance between words, normalizing the relevance scores, and performing a weighted sum of all word encodings using the relevance scores to obtain the encoding of the target word."*

**符号含义与作用** (此处为对原文自然语言描述的形式化对应, **并非原文给出的公式**, 仅作解读参考):

| 原文步骤 | 形式化对应 (解读参考, 非原文) | 作用 |
|---|---|---|
| calculating the relevance between words | 对词向量 $q$ 与 $k_i$ 做相似度, 如 $\text{score}_i = q \cdot k_i$ | 衡量目标词与第 $i$ 个词的关联强度 |
| normalizing the relevance scores | $\alpha_i = \text{softmax}(\text{score}_i)$ | 将原始分数归一化为权重 |
| weighted sum using relevance scores | $\text{output} = \sum_i \alpha_i \cdot v_i$ | 用归一化权重对所有 value 加权求和, 得到目标词新编码 |

> **重要提示:** 上述表格的三个形式化对应**并非原文所有**, 原文只以自然语言三步骤描述 attention, 未给出具体算子 (如是否采用 softmax、是否带缩放因子 $\sqrt{d_k}$ 等)。实际实现细节需以 NVIDIA DeepLearningExamples 参考实现为准。

---

## 【关联】

文档内部关联信息 (来自文末链接):

- **[Installation Guide](install_guide.md)** — 唯一一处显式内部链接, 出现在"Preparing the Environment"小节, 用于指导读者如何准备训练环境 (与本 Quick Start 形成"先装环境、再跑训练"的串联关系)。

文档外部关联 (来自原文):

- **NVIDIA DeepLearningExamples** (https://github.com/NVIDIA/DeepLearningExamples/tree/master/PyTorch/LanguageModeling/BERT) — 本仓库的上游参考实现, 同时也是**预训练权重**与 **SQuADv1.1 数据集**的获取来源, 文档明确将本仓库描述为"an implementation adapted for NPU"。
- **Ascend Apex Installation Guide** (https://gitcode.com/Ascend/apex/blob/master/docs/en/installing_apex.md) — 安装 Apex 加速库所依赖的官方指南, 与 `pip install -r requirements.txt` 共同构成依赖安装链路。
- **SQuADv1.1** 数据集 — 本文档训练唯一涉及的下游任务数据来源。
- **预训练模型 `bert_base.pt`** — 既是训练起点 (--ckpt_path), 也是 FAQ 中"缓存预处理"链路的上游输入。

---

## 【使用方法】

### 启用方式 (原文提供)

1. **环境准备**
   - 参见 [Installation Guide](install_guide.md);
   - 根目录执行 `pip install -r requirements.txt`;
   - 按 Ascend Apex 安装指南安装 Apex。

2. **数据集准备 (SQuADv1.1)**
   ```bash
   mkdir v1.1 && cd v1.1
   ```
   目录结构需含 `train-v1.1.json` / `dev-v1.1.json` / `evaluate-v1.1.py`。

3. **字典下载**
   ```bash
   mkdir -p data/uncased_L-24_H-1024_A-16 && cd data/uncased_L-24_H-1024_A-16
   ```
   将 `bert-base-uncased-vocab.txt` 放入该目录。

4. **预训练模型获取** — 从 NVIDIA DeepLearningExamples 链接下载, 验证文件为 `bert_base.pt`。

### 配置项 / 命令 (原文给出)

| 启动模式 | 命令 (原文) | 说明 |
|---|---|---|
| 单卡精度 | `bash test/train_base_full_1p.sh --data_path=/xxx/v1.1 --ckpt_path=real_path` | BERT-base 单设备精度训练 |
| 单卡性能 | `bash test/train_base_performance_1p.sh --data_path=/xxx/v1.1 --ckpt_path=real_path` | BERT-base 单设备性能训练 |
| 八卡精度 | `bash test/train_base_full_8p.sh --data_path=/xxx/v1.1 --ckpt_path=real_path` | BERT-base 八设备精度训练 |
| 八卡性能 | `bash test/train_base_performance_8p.sh --data_path=/xxx/v1.1 --ckpt_path=real_path` | BERT-base 八设备性能训练 |

**关键参数 (原文):**

- `--data_path`: 数据集路径, **必须指向数据集的 `v1.1` 目录**。
- `--ckpt_path`: 预训练模型存储路径, **只需提供文件所在目录, 无需包含文件名**。

### 输出位置 (原文)

训练完成后, **权重文件保存于当前目录**, 同时在终端输出模型训练精度与性能信息。首次运行会在数据集同目录生成 SQuAD 预处理缓存, 后续训练显著加速 (典型首次预处理耗时约 **十分钟**)。
