# GLM example：title generation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_12_GLM_EXAMPLE_TITLE_GENERATION.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_12_GLM_EXAMPLE_TITLE_GENERATION.md

# 一体化深度解读：FlagAI GLM 标题生成 Tutorial

---

## 【定位】

本文档是 FlagAI（Flagopen AI）模型库中**基于 GLM-large-ch（中文 GLM-Large）模型进行文本摘要式「标题生成」任务的端到端实践指南**，完整覆盖了从数据装载、自定义 Dataset/Collate、模型加载、Trainer 微调，到推理阶段随机采样与 Beam Search 两种解码方式的最小可运行样例，目的是让用户在 `FlagAI/examples/glm_title_generation` 目录下"照搬即可跑通"一段中文长文→短标题的 seq2seq 微调与生成流程。

---

## 【技术要点】

1. **任务定义与数据形态**：输入一段中文长文（`src`），输出对应的短标题（`tgt`），属于典型的 seq2seq 条件生成；样例数据存放于 `/examples/glm_title_generation/data/`，由 `read_file()` 分别从 `src_dir` 和 `tgt_dir` 读取并以 `.strip('\n').lower()` 规范化后返回。

2. **自定义 Dataset 与三段式批处理 Collate**：通过 `GLMTitleGenerationDataset.__getitem__` 调用 `tokenizer.encode_plus(source_text, target_text=target_text)` 把 (src, tgt) 编码为 `input_ids / target_ids / position_ids / attention_mask / loss_mask` 五元组；`GLMTitleGenerationCollateFN` 以批次内最大长度为基准对四项进行 padding——其中 `pad_position_ids` 需同时处理两段 position（block 0 续号、block 1 用 `[1]*pad_len` 填充），`pad_loss_mask` 用 `0` 填充以屏蔽 padding 位的 loss。

3. **AutoLoader 一键加载中文 GLM-Large**：使用 `AutoLoader("title-generation", model_name="GLM-large-ch", model_dir="./state_dict/glm/")`，目录需包含 `config.json / pytorch_model.bin / vocab.txt`；任务名 `seq2seq` 与模型名 `GLM-large-ch` 共同决定权重来源（本地或远端 hub）。

4. **Trainer 训练超参**：原文 Trainer 实例化时给出的关键参数为 `batch_size=1`、`gradient_accumulation_steps=1`、`lr=2e-4`、`weight_decay=1e-3`、`epochs=10`、`log_interval=10`、`eval_interval=10000`、`num_checkpoints=1`、`save_interval=1`，设备通过 `torch.cuda.is_available()` 自动选择 cuda/cpu。

5. **两种推理解码方式**：
   - **随机采样** `predict_generate_randomsample`：`out_max_length=66, top_k=10, top_p=0.1, repetition_penalty=4.0, temperature=1.2`——同时使用 top-k 与 top-p 截断，并用较强的 repetition_penalty（4.0）抑制重复；
   - **Beam Search** `predict_generate_beamsearch`：`out_max_length=66, beam_size=10`——保留 10 条候选束。

6. **端到端命令行入口**：训练 `cd FlagAI/examples/glm_title_generation && python ./train.py`；推理需在 `generate.py` 中修改 `model_dir`（模型配置路径）与 `model_save_path`（已训练权重路径）后 `python ./generate.py`。

---

## 【关键机制与数据】

**工作原理与数据流（按执行顺序）：**

1. **原文：样例输入**——三段中文长文分别关于"可穿戴产品设计原则"、"iPhone 触屏手机 8 年发展"、"雅虎剥离阿里巴巴 15% 股权"。
2. **原文：样例输出标题**——
   - `可 穿 戴 产 品 设 计 原 则 十 大 原 则`
   - `乔 布 斯 宣 布 iphone 8 年 后 将 成 为 个 人 电 脑`
   - `雅 虎 拟 剥 离 阿 里 巴 巴 15 ％ 股 权`
   
   （输出以"空格分字"形式呈现，是中文按 token/字符粒度的可视化结果。）
3. **数据流管线**：磁盘文本文件 → `read_file()` 读为 `src/tgt` 字符串列表 → `GLMTitleGenerationDataset` 单条 `encode_plus` → DataLoader 按 `my_collate_fn` 批次 padding → `torch.LongTensor` 批张量 → Trainer 喂入模型。
4. **训练对象**：`GLM-large-ch`（中文 GLM Large 变体）；框架为 `env_type="pytorch"` 的 FlagAI 自研 Trainer，对外暴露 batch_size、梯度累积、学习率、权重衰减、epoch、日志/评估间隔、checkpoint 数量与保存间隔等旋钮。
5. **性能/基准数据**：原文未给出 loss 曲线、训练时长、显存占用、推理 QPS、BLEU/ROUGE 等任何量化指标，**仅以三条样例定性展示效果**。

> 注：原文出现的关键数字仅有 `epochs=10, lr=2e-4, weight_decay=1e-3, batch_size=1, log_interval=10, eval_interval=10000, num_checkpoints=1` 与推理侧 `out_max_length=66, top_k=10, top_p=0.1, repetition_penalty=4.0, temperature=1.2, beam_size=10`，除此之外无更多数值化性能/规模数据。

---

## 【表格解读】

**原文无表格。** 全文未出现任何 markdown 表格、参数对照表或性能对比表，所有信息以代码块 + 散文段落形式给出。需"参数清单"时，参见上方【技术要点】第 4、5 条整理。

---

## 【公式解读】

**原文无公式。** 文档不涉及 LaTeX 公式、伪代码公式或数学表达式；其"算法核心"以 `encode_plus` 调用 + 三种 `pad_*` 函数的 Python 代码段呈现，而非公式化表达。

---

## 【关联】

- **上游能力依赖**：本文档依赖 FlagAI 框架的三大基础设施——
  1. `flagai.auto_model.auto_loader.AutoLoader`：通过 `task_name + model_name` 自动定位/下载权重与 vocab；
  2. `flagai.trainer.Trainer`：统一封装 env_type、device、保存/评估策略的 PyTorch 训练循环；
  3. FlagAI 内置 `tokenizer.encode_plus(source, target)`：提供 GLM 特有的 `input_ids / target_ids / position_ids（两段 block）/ attention_mask / loss_mask` 五元组封装（这是 GLM 自回归填空式预训练范式在 SFT 上的直接体现）。
- **任务面定位**：示例 `task_name` 写为 `"title-generation"`，但代码注释中又写 *"'seq2seq' is the task_name"*，说明标题生成在 FlagAI 任务体系中属于 `seq2seq`（条件生成）大类，是后续 chat、summarization、translation 等任务的同型模板。
- **同目录姊妹示例**：`FlagAI/examples/glm_title_generation/` 是 examples 目录下一个具体子项目，文档未给出内链，但可合理推断与同级 `glm_*` 示例（其他 GLM 下游任务）共享同一套 AutoLoader/Trainer 范式。
- **图片资源**：原文以 `./img/bert_title_generation_model.png` 作为模型结构示意图（注意路径名虽含 `bert`，实际训练的是 GLM，疑为历史命名遗留），无内部超链接。
- **内部链接**：原文未提供任何超链接（包括文末给出的"内部链接: (无)"也明示这一点），因此跨文档引用关系无法在此展开。

---

## 【使用方法】

**1. 准备与启动训练**（原文"Model Train"小节）：
```commandline
cd FlagAI/examples/glm_title_generation
python ./train.py
```
- 训练数据放置在 `/examples/glm_title_generation/data/`，需自行保证 `src_dir` 与 `tgt_dir` 指向的文件可被 `read_file()` 逐行读取。

**2. 关键配置项**（原文"Trainer 实例化"代码块直接给出，可按需覆盖）：
- `env_type="pytorch"`（也支持其它 env，原文未展开）
- `experiment_name="glm-title-generation"`
- `batch_size=1`，`gradient_accumulation_steps=1`
- `lr=2e-4`，`weight_decay=1e-3`
- `epochs=10`，`log_interval=10`，`eval_interval=10000`
- `load_dir=None`（不加载已有 checkpoint，从头微调）
- `save_dir="checkpoints"`，`save_interval=1`，`num_checkpoints=1`（只保留最近 1 个 ckpt）
- `pytorch_device=device`（cuda 优先，回退 cpu）

**3. 模型与分词器配置**（原文"Load model and tokenizer"代码块）：
```python
model_dir = "./state_dict/glm/"   # 需含 config.json / pytorch_model.bin / vocab.txt
AutoLoader("title-generation", model_name="GLM-large-ch", model_dir=model_dir)
model = auto_loader.get_model()
tokenizer = auto_loader.get_tokenizer()
```

**4. 推理**（原文"Generation"小节）：
- 推理前**必须**在 `generate.py` 中修改 `model_dir`（模型配置路径）与 `model_save_path`（训练得到的权重路径）。
- 运行命令：`cd FlagAI/examples/glm_title_generation && python ./generate.py`
- 解码策略二选一：
  - **随机采样**：`predictor.predict_generate_randomsample(text, out_max_length=66, top_k=10, top_p=0.1, repetition_penalty=4.0, temperature=1.2)`
  - **Beam Search**：`predictor.predict_generate_beamsearch(text, out_max_length=66, beam_size=10)`

> **原文未涉及**的内容：推理显存/速度、checkpoint 命名规范、`evaluate` 回调实现细节、多卡分布式 (DDP) 配置、与其他 GLM 任务的迁移差异、效果评测指标——若需这些信息需自行参考 FlagAI 仓库的其他文档或源码。
