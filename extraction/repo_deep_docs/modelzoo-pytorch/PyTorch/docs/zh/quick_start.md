# 快速入门

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/docs/zh/quick_start.md

# 一体化深度解读：BERT-base 快速入门文档

## 【定位】
本文档是「modelzoo-pytorch」代码仓中 BERT-base 模型在 NPU 上的**快速入门指南**，覆盖从环境准备、数据集/词典/预训练权重获取、单/8卡训练启动，到最终性能展示与常见问题答疑的完整流程，使开发者能够以最少步骤在 Ascend 平台上复现并对比 BERT-base 的精度与吞吐性能。

---

## 【技术要点】

1. **模型规模（原文明确给出）**：BERT-base 为 **12 层 encoder、768 维隐藏层、12 个自注意头（self-attention head）、约 110M 参数**的多层 Transformer-Encoder 堆叠结构；每一层由 **multi-head-attention + feed-forward** 组成，每个 attention 的计算包含三个步骤：① 计算词间相关度 ② 对相关度归一化 ③ 用相关度与所有词编码加权求和得到目标词新编码。
2. **代码仓定位（原文）**：本实现基于 **NVIDIA DeepLearningExamples 仓库**中 BERT 的 PyTorch 参考实现，commit_id 锁定为 **499fb1c5ad0431fee71766f0e5b99d523fd98a3b**，并由本仓适配 NPU。
3. **任务/数据集**：以 **SQuAD v1.1** 为训练数据集（用户自行获取），目录结构包含 `train-v1.1.json`、`dev-v1.1.json`、`evaluate-v1.1.py`；词典使用 **bert-base-uncased-vocab.txt**，存放在 `v1.1/data/uncased_L-24_H-1024_A-16/` 下。
4. **并行度规格**：模型支持 **单机单卡（1p）** 与 **单机 8 卡（8p）** 训练，每种并行度都区分「精度（full）」脚本与「性能（performance）」脚本，共 **4 个 shell 启动脚本**：
   - `test/train_base_full_1p.sh`
   - `test/train_base_performance_1p.sh`
   - `test/train_base_full_8p.sh`
   - `test/train_base_performance_8p.sh`
5. **核心启动参数**：`--data_path` 指向数据集的 **v1.1 目录**；`--ckpt_path` 仅需传入**预训练权重所在目录**，不包含文件名。
6. **依赖组件**：需通过 `pip install -r requirements.txt` 安装基础依赖，并按 **Ascend Apex 安装指导**额外安装 Apex 优化库。

---

## 【关键机制与数据】

- **工作原理（原文）**：BERT 是双向 Transformer-Encoder；每层由 **multi-head-attention + feed-forward** 构成；attention 流程三步走 —— **计算词间相关度 → 相关度归一化 → 与所有词编码加权求和**，以此对每个目标词重新编码。
- **首次训练慢的原因（FAQ 原文）**：第一个 step 会先对 SQuAD 做**预处理**，通常耗时约 **十分钟**；预处理完成后会在**数据集相同目录**生成**缓存文件**，下次训练直接复用，速度显著提升。
- **性能对比数据（原文表 2，更新于 2025年5月10日，精度类型均为 FP16）**：
  - Bert-Base 8p：**竞品 2463 FPS** vs **Atlas 900 A2 PoDc 3118 FPS**
  - Bert-Large 8p：**竞品 870.4 FPS** vs **Atlas 900 A2 PoDc 1084 FPS**
  - （原文未给出加速比换算公式，由读者自行计算可得：Base 提升约 1.27×、Large 提升约 1.25×，此处仅为推算说明、非原文数字）

---

## 【表格解读】

> 原文表 2 — 训练结果展示表

| NAME | 精度类型 | FPS |
| :------ | :-------: | :------: |
| Bert-Base 8p-竞品 | FP16 | 2463 |
| Bert-Base 8p-Atlas 900 A2 PoDc | FP16 | 3118 |
| Bert-Large 8p-竞品 | FP16 | 870.4 |
| Bert-Large 8p-Atlas 900 A2 PoDc | FP16 | 1084 |

**逐行解读**：

- **第 1 行**：`Bert-Base 8p-竞品`，FP16 精度下吞吐为 **2463 FPS**，作为 BERT-Base 8 卡训练的对照基线（"竞品"通常指 GPU 厂商参考实现）。
- **第 2 行**：`Bert-Base 8p-Atlas 900 A2 PoDc`，FP16 下吞吐 **3118 FPS**，即本文档重点验证的 NPU 硬件（Atlas 900 A2 PoDc）实测结果，相对竞品同精度更高。
- **第 3 行**：`Bert-Large 8p-竞品`，FP16 下 **870.4 FPS**，代表 BERT-Large 8 卡训练的对照基线；Large 模型相比 Base 参数量更大，因此绝对吞吐显著降低（不足 Base 的 1/2）。
- **第 4 行**：`Bert-Large 8p-Atlas 900 A2 PoDc`，FP16 下 **1084 FPS**，Atlas 900 A2 PoDc 上 BERT-Large 8 卡实测值，相较竞品同样更优。

> **注**：原文中仅给出此一张表格（表 2），未提供其他参数表/配置表/对比表。

---

## 【公式解读】

**原文无公式**。

文档中未出现 LaTeX 公式或伪代码形式的数学表达式；attention 的计算步骤以**自然语言三步骤**描述，未给出具体的 Q/K/V、Softmax、加权求和等数学形式。

---

## 【关联】

- **install_guide.md**（文末/正文中提到的唯一内部链接）：被引用于「准备训练环境」章节，为本指南提供**环境安装的前置指引**（包括 Python、PyTorch、NPU 驱动、toolkit 等），是启用本文档训练流程的**上游依赖文档**。
- **Ascend Apex 安装指导**（外部链接，`gitcode.com/Ascend/apex/.../installing_apex.md`）：作为本仓 BERT 实现的**外部依赖组件**，Apex 提供混合精度与优化器加速能力，与 FP16 训练脚本（`performance` 脚本）密切相关。
- **NVIDIA DeepLearningExamples 仓库**（外部参考链接）：作为**上游算法实现来源**，commit_id `499fb1c5ad0431fee71766f0e5b99d523fd98a3b` 锁定了与本仓 NPU 适配版本对齐的算法基线，是模型结构与训练超参的参考基准。
- **SQuAD 评测脚本 `evaluate-v1.1.py`**：由用户在数据集准备阶段自行下载，属于**下游评估组件**；与表 2 中的「精度（full）」脚本配套，用于产出模型精度指标。
- **「精度（full）」 vs 「性能（performance）」脚本**：本仓 BERT 实现的**两条平行工作流**——前者侧重训练精度（对应表 2 中的"精度类型 FP16"行所测出的实际精度），后者侧重吞吐（对应表 2 中的 FPS 列），二者共享同一数据集与预训练权重入口。

---

## 【使用方法】

### 1. 环境与依赖安装
```bash
# 在源码包根目录安装 Python 依赖
pip install -r requirements.txt
# 按 Ascend Apex 安装指导安装 Apex（原文为外部链接，本处不展开）
```
> 详细硬件/驱动/CANN 环境请参考 [install_guide.md](install_guide.md)。

### 2. 准备数据集（SQuAD v1.1）
```bash
mkdir v1.1
cd v1.1
# 用户自行获取 train-v1.1.json、dev-v1.1.json、evaluate-v1.1.py 放入 v1.1 目录

# 建立词典目录
mkdir -p data/uncased_L-24_H-1024_A-16
cd data/uncased_L-24_H-1024_A-16
# 用户自行下载 bert-base-uncased-vocab.txt 放入此目录
```

### 3. 获取预训练模型
用户自行获取后，确认目录中存在 `bert_base.pt`（原文仅给出文件名结构，未指定具体下载命令）。

### 4. 启动训练
```bash
# 进入源码包根目录
cd /${模型文件夹名称}

# 单机单卡
bash test/train_base_full_1p.sh --data_path=/xxx/v1.1 --ckpt_path=real_path        # 精度
bash test/train_base_performance_1p.sh --data_path=/xxx/v1.1 --ckpt_path=real_path  # 性能

# 单机 8 卡
bash test/train_base_full_8p.sh --data_path=/xxx/v1.1 --ckpt_path=real_path        # 精度
bash test/train_base_performance_8p.sh --data_path=/xxx/v1.1 --ckpt_path=real_path  # 性能
```

### 5. 参数说明（原文）
- **`--data_path`**：数据集路径，需写到 `v1.1` 目录（例如 `/xxx/v1.1`）。
- **`--ckpt_path`**：预训练模型**所在目录路径**，**无需包含预训练权重文件名**。
- **输出位置**：训练完成后，权重文件保存在**当前路径**（启动脚本时所在的工作目录）；同时输出**模型训练精度与性能信息**。

### 6. 常见问题（FAQ）
- **首次训练首个 step 极慢**：因 SQuAD 预处理耗时（**约十分钟**），预处理完成后会在**数据集相同目录**生成缓存文件，后续训练复用缓存，**启动速度显著加快**。

> **原文未涉及**：未给出具体的 batch size、learning rate、epoch 数、max_seq_length 等超参配置；未给出 `evaluate-v1.1.py` 的调用方式；未给出 ckpt 加载与评估的完整精度复现命令；未提供 Docker 容器化启动方式。这些内容如需了解，应进一步参考 `install_guide.md` 或源码包内 README。
