# T5 title generation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_19_T5_EXAMPLE_TITLE_GENERATION.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_19_T5_EXAMPLE_TITLE_GENERATION.md

# T5 title generation 一体化深度解读

## 【定位】

本文档面向中文 T5 (T5-base-ch) 微调场景,提供**端到端的「标题生成 (title generation)」任务示例**:从数据加载、模型/分词器加载、训练配置(含多卡 DeepSpeed),到推理生成,给出最小可复现的完整流程,帮助使用者在 FlagAI 框架下快速跑通 seq2seq 形式的中文摘要/标题生成任务。

---

## 【技术要点】

1. **任务范式**:典型的 seq2seq 输入→输出映射 —— 给定一段正文文本,生成对应的标题。文档以 `Background` 段直接点明 "Title-generation task aims to generate title for the given input text"。

2. **模型选择**:通过 FlagAI 的统一加载入口 `AutoLoader("seq2seq", "T5-base-ch", model_dir="./state_dict/")` 装载中文 T5-base,使用同一加载器同时获得 `model` 与 `tokenizer`。

3. **数据组织**:以 `read_file()` 函数从文本文件读入并构造 `src`(正文)与 `tgt`(标题)两列表,所有文本在读入时做 `.lower()`(原文中保留小写处理步骤),后续按 **80/20** 切分训练/验证集,且训练集再截取**前 2000 条**用于示例运行。

4. **训练超参数**:通过 `Trainer(env_type="deepspeed", ...)` 配置,**batch_size=1, gradient_accumulation_steps=1, lr=2e-4, weight_decay=1e-3, epochs=10, log_interval=10, eval_interval=10000, save_interval=1, num_checkpoints=1, num_gpus=2, num_nodes=1, master_ip='127.0.0.1', master_port=17750**,训练入口命令为 `python ./train.py`。

5. **序列长度约束**:训练/验证数据集通过 `T5Seq2seqDataset` 封装,**max_src_length=300, max_tgt_length=200**,Tokenizer 由前一步 `loader.get_tokenizer()` 注入。

6. **推理生成**:通过 `python ./generate.py` 运行生成脚本,其中需手动将已训练模型路径设为类似 `"./checkpoints/1001/mp_rank_00_model_states.pt"`(原文注明 "1001 is example, you need modify the number"),即可直观看到生成结果而非验证集 loss。

---

## 【关键机制与数据】

**工作原理(基于原文描述):**

- **数据流**:`src_dir / tgt_dir` 两个文本文件 → `read_file()` 逐行读取并去 `\n` + 转小写,产出 `src`/`tgt` 列表 → 按 `train_size = int(data_len * 0.8)` 切分 → `T5Seq2seqDataset` 用 tokenizer 把中文文本编码为 ≤300 / ≤200 长度的序列 → 送入 seq2seq 模型 → DeepSpeed 多卡并行训练 → 周期性 checkpoint 落入 `checkpoints/` → `generate.py` 加载保存的 `mp_rank_00_model_states.pt` 推理输出标题。

**示例数据(原文展示的 3 条输入-输出对,保留原文字符级间隔):**

- 输入1(可穿戴产品设计原则):"本文总结了十个可穿戴产品的设计原则而这些原则同样也是笔者认为是这个行业最吸引人的地方1为人们解决重复性问题2从人开始而不是从机器开始3要引起注意但不要刻意4提升用户能力而不是取代人"
  - 输出标题:"可 穿 戴 产 品 设 计 原 则 十 大 原 则"
- 输入2(乔布斯 iPhone 演讲):"2007年乔布斯向人们展示iPhone并宣称它将会改变世界还有人认为他在夸大其词然而在8年后以iPhone为代表的触屏智能手机已经席卷全球各个角落未来智能手机将会成为真正的个人电脑为人类发展做出更大的贡献"
  - 输出标题:"乔 布 斯 宣 布 iphone 8 年 后 将 成 为 个 人 电 脑"
- 输入3(雅虎剥离阿里股权):"雅虎发布2014年第四季度财报并推出了免税方式剥离其持有的阿里巴巴集团15％股权的计划打算将这一价值约400亿美元的宝贵投资分配给股东截止发稿前雅虎股价上涨了大约7％至5145美元"
  - 输出标题:"雅 虎 拟 剥 离 阿 里 巴 巴 15 ％ 股 权"

> 原文未提供训练集/验证集 loss、生成质量指标(BLEU/ROUGE)或推理耗时等定量性能数据,仅有上述 3 条定性结果展示。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文是 FlagAI 仓库内 **「T5 序列到序列 (seq2seq) 微调」** 主题下的标题生成示例文档,涉及的关键依赖与上下文关系如下(均严格基于原文):

- **FlagAI 模型加载层**:`flagai.auto_model.auto_loader.AutoLoader` —— 文档使用其 `"seq2seq"` 任务类型与 `"T5-base-ch"` 模型名,体现 AutoLoader 对任务类型 + 模型名的统一抽象。
- **FlagAI 训练层**:`flagai.trainer.Trainer` —— 提供 DeepSpeed 分布式训练入口,文档显式列出 `env_type="deepspeed"`、hostfile、deepspeed.json 等典型分布式参数,提示这是更大分布式训练框架的一个用法片段。
- **FlagAI 数据层**:`T5Seq2seqDataset` —— 文档未给出该类的内部实现,只调用其 `src / tgt / tokenizer / max_src_length / max_tgt_length` 五个参数,显示它是 seq2seq 微调的统一数据集封装。
- **样例数据位置**:文档指出"The sample data is in `/examples/bert_title_generation/data/`"——值得注意,虽然本文档用 T5,但**样例数据目录沿用 bert_title_generation 命名**,这暗示仓库中存在一套与 T5 共享的标题生成语料资源。
- **Checkpoint 命名约定**:生成阶段使用的 `./checkpoints/1001/mp_rank_00_model_states.pt` 中的 `1001` 与 `mp_rank_00_` 命名,符合 DeepSpeed/Megatron-LM 风格的多卡并行模型分片命名习惯,与上文 `Trainer` 中 `num_gpus=2` 一致。
- **内部链接**:原文无内部链接。

---

## 【使用方法】

**启用方式与运行命令(原文给出的实操步骤):**

1. **准备数据**:将正文与标题分别放入两个文件,参考 `/examples/bert_title_generation/data/` 下的样例;在 `train.py` 中实现 `read_file()` 返回 `src`、`tgt` 列表(读入时 `strip('\n').lower()`)。

2. **加载模型与分词器**:
   ```python
   from flagai.auto_model.auto_loader import AutoLoader
   loader = AutoLoader("seq2seq", "T5-base-ch", model_dir="./state_dict/")
   model = loader.get_model()
   tokenizer = loader.get_tokenizer()
   ```

3. **配置 Trainer 并启动训练**:
   ```python
   from flagai.trainer import Trainer
   trainer = Trainer(
       env_type="deepspeed",
       experiment_name="t5_seq2seq",
       batch_size=1,
       gradient_accumulation_steps=1,
       lr=2e-4,
       weight_decay=1e-3,
       epochs=10,
       log_interval=10,
       eval_interval=10000,
       load_dir=None,
       save_dir="checkpoints",
       save_interval=1,
       num_checkpoints=1,
       master_ip='127.0.0.1',
       master_port=17750,
       num_nodes=1,
       num_gpus=2,
       hostfile='./hostfile',
       deepspeed_config='./deepspeed.json',
       training_script=__file__,
   )
   ```
   命令行执行:`python ./train.py`(原文: "The configuration support multi-gpus training.")。

4. **构造数据集并训练**(原文给出参数):
   - 划分:`train_size = int(data_len * 0.8)`
   - 训练集仅取前 2000 条:`train_src = sents_src[:train_size][:2000]`、`train_tgt = sents_tgt[:train_size][:2000]`
   - 验证集:`val_src = sents_src[train_size:]`、`val_tgt = sents_tgt[train_size:]`
   - `T5Seq2seqDataset(..., max_src_length=300, max_tgt_length=200)`
   - 调用 `trainer.train(model, train_dataset=..., valid_dataset=...)`

5. **推理生成**:
   - 修改 `generate.py` 中 `model_save_path = "./checkpoints/1001/mp_rank_00_model_states.pt"`(将 `1001` 替换为实际 checkpoint 编号,原文明确指出 "1001 is example, you need modify the number")。
   - 执行:`python ./generate.py`
   - 输出即生成的标题(以空格分隔的中文字符,与原文示例一致)。

> 注:原文未涉及具体的环境安装(conda/pip)命令、DeepSpeed 启动细节、评估指标或推理超参(如 beam size、temperature)等配置项,以上信息不在原文中。
