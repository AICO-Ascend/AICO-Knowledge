# Qwen-VL-Chat使用教程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/mm/Qwen-VL/TUTORIAL_zh.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/mm/Qwen-VL/TUTORIAL_zh.md

# Qwen-VL-Chat 使用教程 —— 一体化深度解读

---

## 【定位】

本教程面向开发者,演示如何基于 Hugging Face Transformers 加载并调用 **Qwen-VL-Chat** 多模态大模型,以最小可运行代码示例展示其在**视觉问答、密集文字理解、图表数学推理、多图对比与中文输入、Grounding(指定区域框选)**等能力下的典型用法。

---

## 【技术要点】

1. **模型加载三件套**:使用 `transformers` 库的 `AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)`、`AutoModelForCausalLM.from_pretrained(..., device_map="cuda", trust_remote_code=True).eval()` 与 `GenerationConfig.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)` 分别获得分词器、模型与生成配置,并将生成配置挂载到 `model.generation_config`。
2. **图文混排输入接口**:`tokenizer.from_list_format([{'image': '<图片路径>'}, {'text': '<问题>'}, ...])` 接受 Python 列表,每项可标记为 `image` 或 `text`,按出现顺序组成多模态 query,多图输入时在列表中并列多个 `{'image': ...}` 即可。
3. **多轮对话机制**:`model.chat(tokenizer, query=query, history=...)` 返回 `(response, history)` 二元组;首轮传 `history=None`,后续轮次回传上一轮的 `history`,以维持多轮上下文。
4. **Grounding 输出协议**:模型以**标记语言**形式输出目标位置,形如 `<ref>目标名</ref><box>(x1,y1),(x2,y2)</box>`,两个坐标分别为矩形框的左上角与右下角像素坐标;调用 `tokenizer.draw_bbox_on_latest_picture(response, history)` 即可在最新一张图上绘制可视化结果并保存为 JPG。
5. **可复现性控制**:文档示例在两处显式设定随机种子 —— 多图中文示例用 `torch.manual_seed(5678)`,Grounding 示例用 `torch.manual_seed(1234)`;原文明示:不设种子时回答会有随机性,即使设了种子也可能因软硬件差异而得到不同结果。
6. **复杂任务引导提示词**:示例中显式使用了 `Think carefully step by step.`(中文文档对应同一段) 作为"分步推理"提示,以提升图表/数学推理的稳定性。

---

## 【关键机制与数据】

- **工作原理(原文)**:文档对工作流的描述 —— "`tokenizer` 用于对图文混排输入进行分词和预处理,而 `model` 则是 Qwen-VL-Chat 模型本身。" 即分词器负责把图像(以路径形式传入)与文本组装为模型可消费的 query,模型负责推理并产出回复与更新后的对话历史。
- **数据流(原文)**:图像文件路径 → `tokenizer.from_list_format` 列表 → `query` → `model.chat(tokenizer, query, history)` → 文本回复 / 带 `<ref><box>` 的标记语言回复 → 必要时 `tokenizer.draw_bbox_on_latest_picture` → 保存可视化 JPG。
- **示例输出中的可量化数据(原文)**:
  - Grounding(上海图):`上海环球金融中心` → `<box>(667,437),(760,874)</box>`;`东方明珠` → `<box>(506,75),(582,946)</box>`。
  - 菜单数学推理:Salmon Burger 单价 `$10` × 2 = `$20`;Meat Lover's Pizza 单价 `$12` × 3 = `$36`;合计 `$56`。
  - 医院指示牌问答:Department of Otorhinolaryngology 在 `4th floor`,Department of Surgery 在 `3rd floor`。
- **示例使用的资产路径(原文)**:`assets/mm_tutorial/Rebecca_(1939_poster).jpeg`、`assets/mm_tutorial/Hospital.jpg`(文档正文使用 `.jpeg` 与 `.jpg` 两种后缀,以下同)、`assets/mm_tutorial/Menu.jpeg`、`assets/mm_tutorial/Chongqing.jpeg`、`assets/mm_tutorial/Beijing.jpeg`、`assets/mm_tutorial/Shanghai.jpg`。
- **可复现性提示(原文)**:"请注意,城市间的比较/旅游计划是一个具有相当主观性的问题,因此模型产生的回复可能具有相当高的随机性。若不使用 `torch.manual_seed(5678/1234)` 设置随机数种子,每次的输出结果会不一样。"

> 说明:原文未给出 latency、throughput、显存占用、batch size、max length 等量化性能数据,以上为**示例输出中的明确数值**,非性能基准。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

> 备注:菜单示例在回复中给出了一组乘法与加法(2 × $10 + 3 × $12 = $56),但原文并未将其形式化为 LaTeX 或伪代码公式,仅以自然语言步骤列出,故按原文不视为"公式"。

---

## 【关联】

- **与 Hugging Face Transformers 生态的依赖**:全程使用 `transformers` 的 `AutoModelForCausalLM`、`AutoTokenizer`、`GenerationConfig`,并通过 `trust_remote_code=True` 加载 Qwen 自定义模型代码,表明 Qwen-VL-Chat 在 modelzoo 内的运行入口是 HF Transformers 而非 Megatron-LM / 内部 trainer。
- **与"Grounding"能力上下游的衔接**:Grounding 章节与前序"多轮视觉问答"共享同一 `history`,即先常规提问识别图中物体(得到对话历史),再用自然语言指令触发 `<ref><box>` 标记语言输出,再由 `tokenizer.draw_bbox_on_latest_picture` 完成可视化,从而把"语言指令 → 坐标 → 图像标注"三段串成一条链路。
- **与多模态资产目录的耦合**:教程示例统一依赖 `assets/mm_tutorial/` 目录下的若干图片,代码中以相对路径直接传入 `from_list_format`,意味着文档默认工作目录即为仓库根目录。
- **多语言与多图扩展点**:同一 `from_list_format` 接口在"中文 + 双图"示例中扩展为列表内并列两个 `{'image': ...}` + 一个 `{'text': ...}`,说明单图与多图使用同一 API、不需要切换调用入口。
- **随机性相关的全链路一致性**:文档两处提示(多图中文、Grounding)都要求 `torch.manual_seed`,且都强调"软硬件环境差异仍会导致结果不同",这是后续做对比/复现实验时必须关注的耦合点。

---

## 【使用方法】

以下命令与配置均**逐字取自原文**:

1. **环境与随机性(可选)**
   ```python
   torch.manual_seed(1234)   # 或 5678,依示例而定
   ```

2. **初始化分词器、模型、生成配置**
   ```python
   from transformers import AutoModelForCausalLM, AutoTokenizer
   from transformers.generation import GenerationConfig

   tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
   model = AutoModelForCausalLM.from_pretrained(
       "Qwen/Qwen-VL-Chat", device_map="cuda", trust_remote_code=True
   ).eval()
   model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
   ```

3. **构造图文混排 query**
   ```python
   query = tokenizer.from_list_format([
       {'image': 'assets/mm_tutorial/<图片文件名>'},
       {'text': '<问题文本>'},
   ])
   ```

4. **首轮提问**
   ```python
   response, history = model.chat(tokenizer, query=query, history=None)
   print(response)
   ```

5. **后续多轮提问**
   ```python
   query = tokenizer.from_list_format([{'text': '<后续问题>'}])
   response, history = model.chat(tokenizer, query=query, history=history)
   print(response)
   ```

6. **Grounding 结果可视化**
   ```python
   image = tokenizer.draw_bbox_on_latest_picture(response, history)
   image.save('Shanghai_Output.jpg')   # 原文示例文件名
   ```

7. **复杂任务引导**(原文)
   - 在 prompt 中追加 `Think carefully step by step.`,可引导模型分步处理图表数学类任务。
