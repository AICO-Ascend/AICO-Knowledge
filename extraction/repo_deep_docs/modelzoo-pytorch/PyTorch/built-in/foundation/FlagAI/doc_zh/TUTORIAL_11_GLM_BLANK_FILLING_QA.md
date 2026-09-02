# GLM 空白填充

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_11_GLM_BLANK_FILLING_QA.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_11_GLM_BLANK_FILLING_QA.md

# GLM 空白填充 文档深度解读

## 【定位】
本篇文档介绍 GLM 模型"空白填充 (Blank Filling)"的核心能力 —— 通过自回归填充方式天然处理可变长度的缺失文本，并将情感分类、问答等下游任务统一重新定义为空白填充任务进行微调；并给出了基于 FlagAI `GLM-large-ch` 模型分别使用 `[MASK]`、`[sMASK]`、`[gMASK]` 三种遮挡粒度进行推理预测的代码示例。

---

## 【技术要点】

1. **训练范式：自编码 + 自回归结合** —— 训练时随机从输入文本中**删除连续的 token**，然后以自回归方式训练模型重建被删除部分。
2. **下游任务统一为"空白填充"** —— 任何任务（包括情感分类）都会被改写为"带空白的句子 → 填什么"，例如情感分类重写为 `"它真的____"`，由填入"好/坏"判定极性。
3. **三种遮挡粒度（对应三种预测格式）**：
   - `[MASK]` —— Token 级遮挡，仅遮挡句子中**随机 token**，掩码部分最少，生成内容也有限。
   - `[sMASK]` —— 句子级遮挡，要求遮挡区间必须是**完整句子**；**总长度 15%** 的区间被抽样覆盖；目标是 seq2seq 任务，预测结果比 `[MASK]` 更长。
   - `[gMASK]` —— 文档级遮挡；对单个较长跨度采样，长度从**原始长度的 50%–100% 均匀分布**采样；目标是生成长文本。
4. **特殊控制符 `<|startofpiece|>`** —— 在示例文本中作为"原上下文"与"待生成/填空内容"之间的分隔标记。
5. **默认演示模型 `GLM-large-ch`** —— 更大规模版本为 **`GLM-10b-ch`**（百亿参数），文档以外部链接指向 BAAI 模型详情页。
6. **统一推理入口** —— 三类遮挡的代码示例均调用 `Predictor(model, tokenizer).predict_generate_randomsample(text)`，仅输入 `text` 中的遮挡符号不同。

---

## 【关键机制与数据】

- **预训练数据流（原文）**：从输入文本中"随机删除连续的 token" → 模型以"自回归"方式"重建这些被删除的部分"。
- **微调数据流（原文）**：原始下游任务 → 改写为"原文 + 空白占位"的形式 → 模型预测填空内容，输出用作下游任务的结果。
- **`[MASK]` 数据流（原文）**：随机 token 被遮挡 → 生成内容长度最短、粒度最细；例：`[CLS]北京故宫是中国[MASK]非物质文化遗产。<|startofpiece|>现存最大的古代宫殿建筑, 也是`。
- **`[sMASK]` 数据流（原文）**：完整句子被遮挡，覆盖率 **15%**；预测为完整句子或段落，长于 `[MASK]`；例：`[CLS]人工智能是一个以计算机科学为基础,由计算机、数学、哲学等多学科交叉融合的交叉学科,[sMASK],具有非常巨大的前景。<|startofpiece|>它涉及的信息量……模拟人类意识。`
- **`[gMASK]` 数据流（原文）**：对单一长跨度采样，长度服从 **原始长度的 50%–100% 均匀分布**；目标为长文本生成；例：`[CLS]问题:啤酒伤胃吗?回答:[gMASK]<|startofpiece|>谢邀。 我是啤酒爱好者……使体内温度升高,`。
- **情感分类重写示例（原文）**：原始任务 → `"它真的____"` → 模型预测填入 `"好"` 或 `"坏"` → 判定积极/消极。
- **与 BERT 的关系（原文）**：`[MASK]` 场景下 GLM 可以进行被遮挡 token 的预测，文档原话 "与 BERT 类似，GLM 可以进行被遮挡 token 的预测"。

---

## 【表格解读】
**原文无表格。**

（文档仅以一段文字 + 三段"原文: 示例"以及三段 Python 代码呈现，未出现任何结构化表格。）

---

## 【公式解读】
**原文无公式。**

（文档未包含任何数学公式或伪代码形式的表达式。）

---

## 【关联】

- **与 BERT 的关系**：文档明确指出"与 BERT 类似，GLM 可以进行被遮挡 token 的预测" —— `[MASK]` 用法与 BERT 的掩码语言建模（MLM）在形式上相通，但 GLM 是**自回归**重建而非 BERT 的非自回归分类。
- **三种遮挡粒度的层级关系**：`[MASK]` < `[sMASK]` < `[gMASK]`，从 token 级 → 句子级 → 文档级，**生成的文本长度依次递增**，覆盖的预测任务难度也递增（短词补全 → seq2seq → 长文生成）。
- **模型版本关联**：本文使用 `GLM-large-ch` 进行演示，并指向外部 BAAI 模型详情页（链接：`https://model.baai.ac.cn/model-detail/100001`）以获取百亿参数版本 `GLM-10b-ch`。
- **FlagAI 内部组件依赖**：示例代码所调用的 `Predictor`、`GLMModel`、`Tokenizer/GLMLargeChTokenizer` 均位于 flagai 内部模块（`flagai.model.glm_model`、`flagai.data.tokenizer`、`flagai.model.predictor.predictor`），属于模型加载 + 分词 + 推理的统一封装。
- **图像资源**：开篇配图位于相对路径 `./img/glm_blank_filling.png`，与本文主题对应。

---

## 【使用方法】

> 原文提供了三段可直接运行的 Python 代码（`gMASK` 文档级生成 / `MASK` token 级补全 / `sMASK` 句子级补全），均遵循相同流程：

1. **导入依赖**
   ```python
   import torch
   from flagai.model.glm_model import GLMModel
   from flagai.data.tokenizer import Tokenizer            # sMASK 示例使用 GLMLargeChTokenizer
   from flagai.model.predictor.predictor import Predictor
   ```

2. **指定模型**
   - `model_name = 'GLM-large-ch'`（中文大模型）。
   - 更大规模可选：`GLM-10b-ch`（外部链接引导）。

3. **加载分词器**
   ```python
   tokenizer = Tokenizer.from_pretrained(model_name)      # 仅下载/加载分词器配置
   tokenizer = Tokenizer.from_pretrained(model_name, only_download_config=False)  # 真正下载模型权重
   ```
   （`gMASK` 示例中先调用 `from_pretrained(model_name)` 后又重复一次 `from_pretrained(..., only_download_config=False)`，疑似原文笔误；`MASK` 示例直接传入 `only_download_config=False`。）

4. **加载模型**
   ```python
   model = GLMModel.from_pretrain(model_name=model_name,
                                  download_path="./state_dict/")     # gMASK 示例显式指定
   # 或：
   model = GLMModel.from_pretrain(model_name=model_name, only_download_config=False)  # MASK/sMASK 示例
   ```

5. **移至 GPU 并封装**
   ```python
   model.cuda(torch.cuda.current_device())
   predictor = Predictor(model, tokenizer)
   ```

6. **构造待填空文本并推理**
   - 文档级：`text = '问题：啤酒伤胃吗？回答：[gMASK]'`
   - Token 级：`text = '北京故宫是中国[MASK]非物质文化遗产。'`
   - 句子级：`text = '人工智能是一个以计算机科学为基础，由计算机、数学、哲学等多学科交叉融合的交叉学科，[sMASK]，具有非常巨大的前景。'`

7. **调用统一推理方法**
   ```python
   output = predictor.predict_generate_randomsample(text)
   print(text, '\n', output)
   ```

**配置项速查**（原文出现过的参数）：
| 参数 / 命令 | 含义 | 出现位置 |
| --- | --- | --- |
| `model_name` | 模型标识，如 `'GLM-large-ch'` | 三段示例均出现 |
| `download_path` | 模型权重下载/存放目录，示例值 `"./state_dict/"` | `gMASK` 示例 |
| `only_download_config=False` | 不仅下载配置，还下载完整权重 | `MASK`、`sMASK` 示例 |
| `model.cuda(torch.cuda.current_device())` | 将模型搬至当前 CUDA 设备 | 三段示例 |
| `predict_generate_randomsample(text)` | 自回归随机采样式生成 / 填空接口 | 三段示例 |
| `[MASK]` / `[sMASK]` / `[gMASK]` | 三种遮挡占位符，分别对应 token/句子/文档级 | 三段示例 |
| `<|startofpiece|>` | 输入与生成内容的分隔标记 | `text` 字符串内 |
