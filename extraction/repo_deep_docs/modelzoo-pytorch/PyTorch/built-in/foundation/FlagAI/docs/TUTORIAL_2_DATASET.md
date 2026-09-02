# Data set processing flow

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_2_DATASET.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_2_DATASET.md

# 深度解读: FlagAI 数据集处理流程文档

---

## 【定位】

本文档系统阐述了 FlagAI 中**数据集构建(数据预处理)流程**,目标是**将分散、异构的原始文件数据重组为语言模型可直接使用的统一结构化数据**,并以 CommitmentBank 为示例,完整展示了"分类任务微调(prompt-tuning)"场景下从原始文件到 DataLoader 的端到端构建链路。

---

## 【技术要点】

1. **三类数据预处理范式**:文档明确指出 FlagAI 项目当前支持三大类预处理 —— **分类任务微调(含 fine-tuning 与 prompt-tuning 两种形态)、预训练(pretraining)、生成任务微调**。其中 prompt-tuning 因需要额外 cloze template,更适配**有限数据场景**。
2. **分类任务数据集统一封装类**:核心入口函数为 `SuperGlueDataset`,位于 `flagai.data.dataset` 模块,负责"自动加载 + 结构统一化"两步走。
3. **Collate 构造策略**:通过 `ConstructSuperglueStrategy(cl_args, tokenizer, task_name="rte")` 在 `flagai.data.dataset` 中构建 collate_fn,再交由 `torch.utils.data.DataLoader` 消费。
4. **关键参数体系**:`SuperGlueDataset` 含四个主参 —— `task_name`(数据集标识符)、`data_dir`(默认 `./dataset`,数据自动下载至此)、`dataset_type`(取值 `train/dev/test`)、`tokenizer`(在 Tutorial1 中构造,示例为 `"GLM-large-en"`)。
5. **DataLoader 配置默认值**:示例代码给出 `batch_size=1, shuffle=False, num_workers=1, drop_last=False, pin_memory=False` 的标准启动配置。
6. **支持数据集一览**:FlagAI 当前在分类任务下挂载了 **22 个数据集**,覆盖 **SuperGLUE、GLUE、CLUE** 三大 benchmark,语言涵盖英文、中文、德文、法文;其中**完全测试通过的为 9 个**(boolq/cb/copa/muiltirc/rte/wic/wsc/afqmc/tnews),其余 13 个仅支持自动下载但**未完全测试**(`❌`),xstance 三个变体甚至**不支持自动下载**。

---

## 【关键机制与数据】

**数据流(原文):** 原始分散文件 → `SuperGlueDataset` 自动加载 → 结构统一化 → `ConstructSuperglueStrategy` 生成 collate_fn → `torch.utils.data.DataLoader` 产出可训练 batch。整条链路图见原文 `img/dataset_pipeline.png`,文档以 **CommitmentBank 为示例任务**贯穿。

**性能/数据指标:** 原文未给出吞吐量、序列长度、batch 大小建议、显存占用等性能数据;**仅声明** `batch_size=1` 为示例取值,`data_dir` 默认值为 `./dataset`。

**自动下载机制:** 原文:"Data will be automatically downloaded to `data_dir` directory, which is `./dataset` by default.",即只要给定 `task_name` 与 `data_dir`,数据集自动下载并预处理,无需人工干预。

---

## 【表格解读】

> 注:原文表格在 RACE(race)行被截断,以下逐字还原完整表格(含被截断的最后一行):

| dataset name | Identifier | Language | Benchmark | Auto-Download | Fully tested |
|---|---|---|---|---|---|
| Broadcoverage Diagnostics | boolq | English | SuperGLUE | ✅ | ✅ |
| CommitmentBank | cb | English | SuperGLUE | ✅ | ✅ |
| Choice of Plausible Alternatives | copa | English | SuperGLUE | ✅ | ✅ |
| Multi-Sentence Reading Comprehension | muiltirc | English | SuperGLUE | ✅ | ✅ |
| Words in Context | wic | English | SuperGLUE | ✅ | ✅ |
| The Winograd Schema Challenge | wsc | English | SuperGLUE | ✅ | ✅ |
| Recognizing Textual Entailment | rte | English | SuperGLUE | ✅ | ✅ |
| Ant Financial Question Matching Corpus | afqmc | Chinese | CLUE | ✅ | ✅ |
| Short Text Classificaiton for News | tnews | Chinese | CLUE | ✅ | ✅ |
| Broadcoverage Diagnostics | ax-b | English | SuperGLUE | ✅ | ❌ |
| Winogender Schema Diagnostics | ax-g | English | SuperGLUE | ✅ | ❌ |
| The Corpus of Linguistic Acceptibility | cola | English | GLUE | ✅ | ❌ |
| The Stanford Sentiment Treebank | sst2 | English | GLUE | ✅ | ❌ |
| Microsoft Research Paraphrase Corpus | mrpc | English | GLUE | ✅ | ❌ |
| Quora Question Pairs | qqp | English | GLUE | ✅ | ❌ |
| MultiNLI Matched | mnli | English | GLUE | ✅ | ❌ |
| MultiNLI Mismatched | mnli-mm | English | GLUE | ✅ | ❌ |
| Question NLI | qnli | English | GLUE | ✅ | ❌ |
| X-Stance | xstance | English | (空) | ❌ | ❌ |
| X-Stance (German) | xstance-de | German | (空) | ❌ | ❌ |
| X-Stance (French) | xstance-fr | French | (空) | ❌ | ❌ |
| RACE | race | (原文截断) | (原文截断) | (原文截断) | (原文截断) |

**逐行解读:**

- **boolq / cb / copa / multirc / wic / wsc / rte**:均属 **SuperGLUE** benchmark 的英文任务,自动下载 + 完全测试通过,代表 FlagAI 一线稳定性保障。
- **afqmc / tnews**:**中文 CLUE benchmark** 数据集,自动下载 + 完全测试通过,补齐中文能力。
- **ax-b / ax-g**:SuperGLUE 的**诊断(diagnostics)**子集,用于偏见/性别公平性分析,仅支持下载但**未完全测试**。
- **cola / sst2 / mrpc / qqp / mnli / mnli-mm / qnli**:**GLUE** 经典英文任务,均自动下载支持,但**完全测试字段为 ❌** —— 提示这些任务的可运行性需用户自行验证。
- **xstance / xstance-de / xstance-fr**:**多语言立场检测**(英语/德语/法语),**三项能力均缺失**(❌ ❌),Benchmark 列亦为空,属边缘支持。
- **race**:原文行在 `race` 后被截断,Language/Benchmark/Auto-Download/Fully tested 字段信息不完整,无法补全。

**整体表格信号:** 表格将数据集划分为**三档质量等级** —— 完全可用(9 个)、仅可下载(12 个)、未完整下载(3 个),用户应据此选择风险可控的数据集。

---

## 【公式解读】

**原文无公式。** 本文档为应用/工程导向的指南,未包含任何数学公式或伪代码算法描述。

---

## 【关联】

文档与以下特性/上下游存在显式关联(基于文末内部链接与正文交叉引用):

- **`The Stanford Question Answering Dataset`(SQuAD)**:作为内部链接出现,属"问答"类数据集,推断对应**生成任务微调**预处理路径,与本节展示的分类任务路径形成对照。
- **`DATASET_EXAMPLE.md`**:数据加载的**示例代码补集**,本文档给出接口签名与典型调用,`DATASET_EXAMPLE.md` 提供完整可运行样例。
- **`GLM.md`**:示例代码中 `Tokenizer.from_pretrained("GLM-large-en")` 即指向 GLM 模型说明;**tokenizer 与模型必须配套**,因此本数据预处理流程强依赖于 GLM 模型文档。
- **`The Stanford Question Answering Dataset`(二次出现)**:与首次链接重复,印证该数据集在 FlagAI 中是**预训练/问答任务的关键示例**。

---

## 【使用方法】

**最小可运行示例(原文已给出):**

```python
import torch
from flagai.data.tokenizer import Tokenizer
from flagai.data.dataset import SuperGlueDataset, ConstructSuperglueStrategy
from flagai.test_utils import CollateArguments

cl_args = CollateArguments()                                  # 1. 取默认 collate 参数
tokenizer = Tokenizer.from_pretrained("GLM-large-en")         # 2. 构造 tokenizer(依赖 GLM.md)
dataset = SuperGlueDataset(                                   # 3. 加载数据集
    task_name='cb', data_dir='./datasets/', dataset_type='train', tokenizer=tokenizer)
collate_fn = ConstructSuperglueStrategy(cl_args, tokenizer, task_name="rte")  # 4. collate 策略
loader = torch.utils.data.DataLoader(                         # 5. 装配 DataLoader
    dataset, batch_size=1, shuffle=False, num_workers=1,
    drop_last=False, pin_memory=False, collate_fn=collate_fn)
```

**配置项说明(原文):**

| 配置项 | 取值/默认值 | 说明 |
|---|---|---|
| `task_name` | 详见表格 Identifier 列(如 `cb`/`rte`/`boolq` 等) | 数据集标识,决定自动下载哪个数据集 |
| `data_dir` | `./dataset`(默认) | 数据集自动下载目录 |
| `dataset_type` | `train` / `dev` / `test` | 选择预处理的是训练/验证/测试集 |
| `tokenizer` | 来自 `Tokenizer.from_pretrained(...)` | 需与下游模型匹配(示例:`GLM-large-en`) |
| `batch_size` | `1`(示例) | DataLoader 批大小 |
| `shuffle` | `False`(示例) | 是否打乱 |
| `num_workers` | `1`(示例) | 数据加载子进程数 |
| `drop_last` | `False`(示例) | 是否丢弃末尾不足 batch |
| `pin_memory` | `False`(示例) | 是否锁页内存(常用于 GPU 加速) |

**启用条件:** 需安装 `flagai` 包并已下载 `GLM-large-en` 等对应 tokenizer;运行前确保 `data_dir` 路径可写;首次运行需联网,系统会自动下载所选 `task_name` 对应的原始数据。**原文未涉及**关于分布式/多卡/DeepSpeed 启动方式、batch 大小调优建议、序列长度 padding 策略等高级配置说明。
