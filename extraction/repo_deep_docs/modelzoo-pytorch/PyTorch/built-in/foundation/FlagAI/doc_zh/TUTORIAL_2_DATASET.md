# 数据集处理流程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_2_DATASET.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_2_DATASET.md

# 一体化深度解读：FlagAI 数据集处理流程

---

## 【定位】
本文档系统性地阐述 FlagAI 项目中 NLP 数据预处理的完整流程，以 `CommitmentBank` 为示例拆解了**分类任务微调（提示学习）、预训练、生成任务微调**三类典型场景下如何将原始散乱文件数据重组为模型可直接消费的统一结构样本。

---

## 【技术要点】

1. **三大数据预处理场景**：原文明确划分三种情形——分类任务微调（含普通微调与提示学习两种形态）、预训练、生成任务微调；其中提示学习需额外构建完形填空模板，更适合低资源/小样本场景。

2. **核心处理流水线（4 步法）**：以分类微调为例，流程为 ① 初步读取并处理数据集（含自动加载 + 统一结构）→ ② 将数据整理成模型输入（构建完形填空模板 + 分词构造样本）→ ③ 创建加载器；预训练与生成任务遵循类似骨架。

3. **关键类与函数**：
   - `Tokenizer.from_pretrained("GLM-large-en")`：构造分词器（教程示例选用 GLM-large-en）。
   - `SuperGlueDataset(task_name, data_dir, dataset_type, tokenizer)`：自动加载并统一数据集结构的主函数。
   - `ConstructSuperglueStrategy(cl_args, tokenizer, task_name)`：构造 `collate_fn`。
   - `torch.utils.data.DataLoader`：配合 `batch_size=1, shuffle=False, num_workers=1, drop_last=False, pin_memory=False, collate_fn=collate_fn`（原文示例参数）。

4. **`SuperGlueDataset` 四参数**（原文明确给出）：
   - `task_name`：数据集简称（见加载数据集表格）。
   - `data_dir`：数据集自动下载目录，默认 `./dataset`（代码示例中使用 `./datasets/`）。
   - `dataset_type`：`train` / `dev` / `test` 之一。
   - `tokenizer`：已构建完成的分词器。

5. **`CollateArguments()`**：用于"得到默认参数"，再与 tokenizer、task_name 共同传入 `ConstructSuperglueStrategy` 构造 collate 函数。

6. **支持的数据集范围（表格中 23 项）**：覆盖 SuperGLUE（cb、copa、multirc、rte、wic、wsc、boolq、record）、CLUE（afqmc、tnews）、GLUE（ax-b、ax-g、cola、sst2、mrpc、qqp、mnli、mnli-mm、qnli）以及 xstance、xstance-de、xstance-fr、race、agnews；语言涵盖英文、中文、德文、法文。

---

## 【关键机制与数据】

**工作原理（原文表述提炼）：**
- 构建数据集的本质是 NLP 数据预处理——把"原始散乱文件数据"重组成"统一结构数据"，以便语言模型直接使用。
- 流程图（`img/dataset_pipeline.png`，宽度 600px，原文提及）展示了以 `CommitmentBank` 为例的整体管道。
- 分类微调存在两种形态：① 普通微调；② 提示学习（prompt-based，需额外构建完形填空模板）。原文以**提示学习**为例展开讲解。
- 分类数据预处理的两阶段：
  - **1.2 初步读取并处理数据集**——`SuperGlueDataset` 负责自动加载并统一所有数据集的结构。
  - **1.3 将数据整理成模型的输入**——先构建完形填空模板（1.3a），再分词并构造输入样例（1.3b）。
- 预训练与生成任务：原文目录中提及对应章节标题（`2.1 预训练任务数据格式样例`、`2.2 预训练的任务处理实例代码`、`3.1 生成任务应用代码`、`3.1 生成任务支持数据集`、`3.2 生成任务里将数据整理成模型的输入`），但**提供的正文内容到此为止已截断**，未展开具体机制。

**性能/数据指标**：原文未提供任何性能数字、基准分数或训练吞吐量数据。

---

## 【表格解读】

> **原文表格标题语境**：FlagAI 目前支持的分类数据集清单，按"数据集名称 / 数据集简称 / 语言 / 所属评测基准 / 支持提示学习 / 可自动下载 / 已测试通过"七列组织。

| 数据集名称 | 数据集简称 | 语言 | 所属评测基准 | 支持提示学习 | 可自动下载 | 已测试通过 |
|---|---|---|---|---|---|---|
| CommitmentBank | cb | 英文 | SuperGLUE | ✅ | ✅ | ✅ |
| Choice of Plausible Alternatives | copa | 英文 | SuperGLUE | ✅ | ✅ | ✅ |
| Multi-Sentence Reading Comprehension | multirc | 英文 | SuperGLUE | ✅ | ✅ | ✅ |
| Recognizing Textual Entailment | rte | 英文 | SuperGLUE | ✅ | ✅ | ✅ |
| Words in Context | wic | 英文 | SuperGLUE | ✅ | ✅ | ✅ |
| The Winograd Schema Challenge | wsc | 英文 | SuperGLUE | ✅ | ✅ | ✅ |
| Broadcoverage Diagnostics | boolq | 英文 | SuperGLUE | ✅ | ✅ | ✅ |
| Reading Comprehension with Commonsense Reasoning | record | 英文 | SuperGLUE | ✅ | ✅ | ✅ |
| Ant Financial Question Matching Corpus | afqmc | 中文 | CLUE | ✅ | ✅ | ✅ |
| Short Text Classificaiton for News | tnews | 中文 | CLUE | ✅ | ✅ | ✅ |
| Broadcoverage Diagnostics | ax-b | 英文 | SuperGLUE | ✅ | ✅ | ❌ |
| Winogender Schema Diagnostics | ax-g | 英文 | SuperGLUE | ✅ | ✅ | ❌ |
| The Corpus of Linguistic Acceptability | cola | 英文 | GLUE | ✅ | ✅ | ❌ |
| The Stanford Sentiment Treebank | sst2 | 英文 | GLUE | ✅ | ✅ | ❌ |
| Microsoft Research Paraphrase Corpus | mrpc | 英文 | GLUE | ✅ | ✅ | ❌ |
| Quora Question Pairs | qqp | 英文 | GLUE | ✅ | ✅ | ❌ |
| MultiNLI Matched | mnli | 英文 | GLUE | ✅ | ✅ | ❌ |
| MultiNLI Mismatched | mnli-mm | 英文 | GLUE | ❌ | ✅ | ❌ |
| Question NLI | qnli | 英文 | GLUE | ✅ | ✅ | ❌ |
| X-Stance | xstance | 英文 | （空） | ✅ | ❌ | ❌ |
| X-Stance (German) | xstance-de | 德文 | （空） | ✅ | ❌ | ❌ |
| X-Stance (French) | xstance-fr | 法文 | （空） | ✅ | ❌ | ❌ |
| RACE | race | 英文 | （空） | ✅ | ❌ | ❌ |
| AG News | agnews | 英文 | （空） | ✅ | ❌ | ❌ |

**逐行解读**：
- **前 8 行 SuperGLUE 子集（cb/copa/multirc/rte/wic/wsc/boolq/record）**：全部英文，全部支持提示学习，全部可自动下载且**全部测试通过**——构成 FlagAI 分类任务的"第一梯队"就绪能力。
- **CLUE 中文数据集（afqmc、tnews）**：与 SuperGLUE 第一梯队同等级别——支持提示学习、可自动下载、测试通过，是中文分类的代表。
- **GLUE/SuperGLUE 诊断与扩展集（ax-b、ax-g、cola、sst2、mrpc、qqp、mnli、qnli）**：除 `mnli-mm` 外均"支持提示学习 + 可自动下载"，但**已测试通过全部为 ❌**，提示用户使用前需自行验证。
- **`mnli-mm` 是表中唯一"支持提示学习 = ❌"且"可自动下载 = ✅"的条目**：与 `mnli` 形成 Matched/Mismatched 配对，但提示学习能力存在差异。
- **多语种与扩展数据集（xstance/xstance-de/xstance-fr/race/agnews）**：覆盖英文、德文、法文；所属评测基准栏为空，**可自动下载全部为 ❌**，意味着用户需自行准备数据；同样均未测试通过。
- **整体趋势**：可自动下载性 ≠ 测试通过度；测试通过的 10 个数据集全部集中在 SuperGLUE 与 CLUE 的主流任务上，提示文档示例 `task_name='cb'` 与 `task_name='rte'` 的选择正好落在"已验证可运行"的子集内。

---

## 【公式解读】

**原文无公式**（全文未出现任何 LaTeX 数学公式或伪代码形式的数学表达式）。

---

## 【关联】

依据原文目录与文末内部链接信息，可梳理如下关联关系：

- **与 `The Stanford Question Answering Dataset` 的关联**：原文中作为内部链接出现两次。文档当前未在正文中具体展开 SQuAD 的使用方式，但内部链接的出现表明 FlagAI 项目中存在对该数据集的相关说明（可能位于其他章节或 `DATASET_EXAMPLE.md`）。
- **与 `DATASET_EXAMPLE.md` 的关联**：作为本文之外的"数据集示例"参考文档，是本教程的补充/姐妹篇（推断用于展示具体样例）。
- **与 `GLM.md` 的关联**：作为内部链接出现两次。`Tokenizer.from_pretrained("GLM-large-en")` 直接依赖 GLM 模型分词器；预训练章节（在目录中预告）与 GLM 模型的预训练数据格式紧密相关——本文档的上游是分词器/模型层（GLM），下游是 `DataLoader` 与训练流程。
- **章节内部上下游关系**：
  - `1.1 应用代码` 是入口，调用 `1.2 SuperGlueDataset` → `1.3 ConstructSuperglueStrategy` → `1.4 DataLoader`。
  - `1.3` 拆分为 `1.3a 构建完形填空模板` 与 `1.3b 分词并构造输入样例`，二者构成"模板 + 样本"的输入构造链。
  - 文档目录预告了**平行结构**：`第 2 章 预训练`（含 `2.1 数据格式样例`、`2.2 实例代码`）与**第 3 章 生成任务微调**（含 `3.1 应用代码`、`3.1 支持数据集`、`3.2a 构建填空模板`、`3.2b 分词构造样本`），与第 1 章分类微调呈三路并列，但本文档正文仅给出第 1 章详细展开。

---

## 【使用方法】

依据原文给出的可直接复用的代码骨架：

```python
import torch
from flagai.data.tokenizer import Tokenizer 
from flagai.data.dataset import SuperGlueDataset
from flagai.test_utils import CollateArguments
from flagai.data.dataset import ConstructSuperglueStrategy

# 1) 得到默认 collate 参数
cl_args = CollateArguments()

# 2) 创建分词器（示例为英文 GLM-large-en）
tokenizer = Tokenizer.from_pretrained("GLM-large-en")

# 3) 加载并统一数据集结构
dataset = SuperGlueDataset(task_name='cb',
                           data_dir='./datasets/',
                           dataset_type='train',
                           tokenizer=tokenizer)

# 4) 构造 collate function（注意此处示例 task_name 与上面不同，原文如此）
collate_fn = ConstructSuperglueStrategy(cl_args, tokenizer, task_name="rte")

# 5) 创建 DataLoader（原文参数）
loader = torch.utils.data.DataLoader(dataset,
                                    batch_size=1,
                                    shuffle=False,
                                    num_workers=1,
                                    drop_last=False,
                                    pin_memory=False,
                                    collate_fn=collate_fn)
```

**关键配置项**（原文已显式列出）：
- `task_name`：从文末表格的"数据集简称"列中选择（如 `cb`、`rte`、`afqmc`、`tnews` 等）。
- `data_dir`：数据集下载/读取根目录，默认 `./dataset`。
- `dataset_type`：`train` / `dev` / `test`。
- `tokenizer`：由 `Tokenizer.from_pretrained(...)` 构造，模型选择依任务而定（教程示例为 `GLM-large-en`）。
- DataLoader 参数：`batch_size=1, shuffle=False, num_workers=1, drop_last=False, pin_memory=False`。

**预训练与生成任务**：原文目录中已列出章节标题（`2.1/2.2`、`3.1/3.2`），但**提供的正文内容截断于分类数据集表格之后**，因此具体的预训练/生成任务启用方式、配置项与命令——**原文未涉及**。
