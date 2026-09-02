# T5 标题生成

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_19_T5_EXAMPLE_TITLE_GENERATION.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_19_T5_EXAMPLE_TITLE_GENERATION.md

# T5 标题生成 文档深度解读

---

## 【定位】

本文档是 FlagAI 框架下 T5 模型进行**中文文本摘要/标题生成**任务的端到端使用教程，描述从数据加载、模型载入、训练到生成标题的完整流水线，旨在帮助用户基于一段长文本抽取对应的短标题。

---

## 【技术要点】

1. **任务类型**：Seq2Seq（序列到序列）生成式任务，输入文本，输出对应标题。
2. **模型指定**：通过 `AutoLoader` 以 `task_name="seq2seq"`、`model_name="T5-base-ch"` 加载，并从本地 `./state_dict/` 目录读取权重。
3. **数据准备**：通过自定义 `read_file()` 把语料拆成 `src`（正文）与 `tgt`（标题）两列；训练/验证按 **80% / 20%** 划分，并对训练集截取前 **2000** 条。
4. **数据集封装**：使用 `T5Seq2seqDataset`，`max_src_length=300`，`max_tgt_length=200`。
5. **训练配置**：使用 FlagAI `Trainer`，关键超参包括 `batch_size=1`、`gradient_accumulation_steps=1`、`lr=2e-4`、`weight_decay=1e-3`、`epochs=10`、`log_interval=10`、`eval_interval=10000`、`num_gpus=2`，基于 **DeepSpeed**（`env_type="deepspeed"`）启动多卡训练，端口 `17750`。
6. **生成推理**：训练完成后，修改 `model_save_path`（示例 `./checkpoints/1001/mp_rank_00_model_states.pt`，其中 `1001` 为占位编号）后运行 `python ./generate.py` 即可获得生成结果。

---

## 【关键机制与数据】

- **工作原理**：基于 T5（Text-to-Text Transfer Transformer）的 encoder-decoder 架构，将整段正文视作"待翻译源序列"，将标题视作"目标序列"，从而把标题抽取建模为文本到文本的条件生成问题。
- **数据流**：用户文本 → `read_file()` 切分为 `src`/`tgt` → 按 0.8 比例划分 train/val → 在训练集中截取前 2000 条 → `T5Seq2seqDataset` 做 token 化与长度截断（src≤300, tgt≤200）→ `Trainer` 驱动模型在 DeepSpeed 多卡环境上训练 → 保存 checkpoint → `generate.py` 加载 checkpoint 解码得到标题。
- **示例原文（Inputs/Outputs 原文有 3 组）**：
  - 输入："本文总结了十个可穿戴产品的设计原则……" → 输出："可 穿 戴 产 品 设 计 原 则 十 大 原 则"
  - 输入："2007年乔布斯向人们展示iPhone并宣称它将会改变世界……" → 输出："乔 布 斯 宣 布 iphone 8 年 后 将 成 为 个 人 电 脑"
  - 输入："雅虎发布2014年第四季度财报并推出了免税方式剥离其持有的阿里巴巴集团15％股权的计划……" → 输出："雅 虎 拟 剥 离 阿 里 巴 巴 15 ％ 股 权"
- **小写归一化**：在 `read_file()` 中，对每行调用 `.lower()`，即将样本整体转为小写后送入模型。
- **性能数据**：原文未提供训练耗时/吞吐/指标（loss、accuracy、Rouge 等）数据。

---

## 【表格解读】

**原文无表格**（文档以代码块、命令和示意文字呈现，未出现任何 markdown 表格或参数对照表）。

---

## 【公式解读】

**原文无公式**（文档仅涉及 Python API 调用与命令行，未出现 LaTeX 或伪代码形式的数学公式）。

---

## 【关联】

- **上游框架**：FlagAI（`flagai.auto_model.auto_loader.AutoLoader`、`flagai.trainer.Trainer`、`T5Seq2seqDataset`），属于 FlagAI 统一模型加载与训练入口的一部分。
- **模型组件**：T5-base-ch（中文 T5 base 版），seq2seq 任务族下的成员之一；与同目录下其他任务共享同一 `AutoLoader` 范式。
- **底层依赖**：DeepSpeed（`env_type="deepspeed"`，`deepspeed_config='./deepspeed.json'`），用于多机多卡分布式训练。
- **同模块示例**：原文中提到样本数据存放在 `/examples/bert_title_generation/data/`，说明 FlagAI 仓库在 examples 目录下另有 BERT 标题生成示例，本教程与之共享同一份数据组织约定（src/tgt 文本对）。
- **关联产物**：`./checkpoints/` 目录下保存的 `mp_rank_00_model_states.pt`（DeepSpeed 风格的 model states 文件），是 `generate.py` 的输入。
- 文档文末标注 **内部链接: (无)**，说明本文未显式给出相对仓库内的跳转链接。

---

## 【使用方法】

### 启用方式
1. **准备数据**：将样本文件置于 `examples/bert_title_generation/data/`，按 `src` / `tgt` 两份文本格式组织。
2. **在 train.py 中实现 `read_file()`**，返回 `src` 列表与 `tgt` 列表（已 `.lower()`）。

### 关键配置项
| 配置项 | 取值（原文） | 含义 |
|---|---|---|
| task_name | `"seq2seq"` | 任务类型 |
| model_name | `"T5-base-ch"` | 中文 T5 base 模型 |
| model_dir | `"./state_dict/"` | 预训练权重路径 |
| env_type | `"deepspeed"` | 训练后端 |
| batch_size | `1` | 单卡 batch |
| gradient_accumulation_steps | `1` | 梯度累积步数 |
| lr | `2e-4` | 学习率 |
| weight_decay | `1e-3` | 权重衰减 |
| epochs | `10` | 训练轮数 |
| log_interval | `10` | 日志间隔 |
| eval_interval | `10000` | 验证间隔 |
| num_gpus | `2` | GPU 数量 |
| master_port | `17750` | DeepSpeed master 端口 |
| num_nodes | `1` | 节点数 |
| max_src_length | `300` | 输入最大长度 |
| max_tgt_length | `200` | 输出最大长度 |
| train/val 划分比例 | `0.8` | 80% 训练 / 20% 验证 |
| 训练集截取条数 | `2000` | 训练子集大小 |

### 命令
- **训练**：`python ./train.py`（支持多卡，已在 Trainer 内通过 DeepSpeed 配置）。
- **生成**：
  1. 在 `generate.py` 中将 `model_save_path` 改为实际 checkpoint 路径，例如 `./checkpoints/<iter>/mp_rank_00_model_states.pt`。
  2. 运行：`python ./generate.py`，即可查看生成标题。

> 备注：原文中 `model_save_path` 的 `1001` 仅为示例编号，需替换为实际保存的 iteration/目录编号，原文已明确提示 "you need modify the number"。
