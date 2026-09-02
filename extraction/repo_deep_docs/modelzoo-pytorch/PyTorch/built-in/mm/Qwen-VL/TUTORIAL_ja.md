# Qwen-VL-Chat チュートリアル

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/mm/Qwen-VL/TUTORIAL_ja.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/mm/Qwen-VL/TUTORIAL_ja.md

# Qwen-VL-Chat チュートリアル 深度解读

---

## 【定位】

这篇文档是 **Qwen-VL-Chat 多模态大语言模型的入门级实战教程**，通过五个递进的示例（多轮视觉问答、文本理解、图表数学推理、多视角中文推理、目标定位 Grounding）演示该模型如何以 `tokenizer.from_list_format` + `model.chat` 的统一接口完成"图像 + 文本 → 文本/坐标"的端到端推理。

---

## 【技术要点】

1. **模型与分词器加载**：使用 HuggingFace `transformers` 的 `AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)` 和 `AutoModelForCausalLM.from_pretrained("Qwen/Qwen-VL-Chat", device_map="cuda", trust_remote_code=True).eval()`，并通过 `GenerationConfig.from_pretrained(...)` 注入生成配置；`trust_remote_code=True` 是加载 Qwen 自定义模型类所必需的。

2. **交织多模态输入构造**：`tokenizer.from_list_format([{'image': '...'}, {'text': '...'}, ...])` 是核心 API，负责把图像路径和文本片段拼装为模型可接受的对话输入；同一列表可放置多个 `'image'` 字典以支持多图输入。

3. **多轮对话状态管理**：`model.chat(tokenizer, query=query, history=history)` 每次返回 `(response, history)`；首次调用 `history=None`，后续调用须把上一步返回的 `history` 回传，模型即基于上下文作答。

4. **随机种子与可复现性**：原文用 `torch.manual_seed(1234)` 与 `torch.manual_seed(5678)` 两个具体种子分别锁定定位示例和多视角推理示例；并显式说明即便固定种子，软硬件差异仍可能导致输出与教程不一致。

5. **Grounding 输出的标记语言格式**：模型以 `<ref>名称</ref><box>(x1,y1),(x2,y2)</box>` 的 XML-like 结构返回目标坐标，例如 `<ref>上海环球金融中心</ref><box>(667,437),(760,874)</box>`。

6. **边界框可视化**：通过 `tokenizer.draw_bbox_on_latest_picture(response, history)` 直接在最近一张输入图上绘制模型返回的 box，输出为 PIL Image 对象，可用 `.save('Shanghai_Output.jpg')` 保存。

---

## 【关键机制与数据】

- **工作原理**：原文描述为"`tokenizer` 用于交织多模态输入的前处理，`model` 即 Qwen-VL-Chat 模型本体"；推理以 `.eval()` 模式运行，配合 `model.generation_config` 控制生成。
- **数据流**：图像路径 → `from_list_format` → 列表化 query → `model.chat` → `(response, history)`；下一轮用 `history` 续接 → 输出文本或坐标。
- **随机种子（原文指定）**：`1234`（Grounding 示例、最终旅游计划示例）、`5678`（重庆/北京对比示例）。
- **具体坐标样本（原文示例输出）**：上海环球金融中心 `(667,437),(760,874)`；东方明珠 `(506,75),(582,946)`。
- **菜单价格样本（原文推理输出）**：Salmon Burger $10/个、Meat Lover's Pizza $12/个，合计 $56（2×10 + 3×12）。
- **性能数据**：原文未给出 FPS、显存占用、参数量等量化性能指标，仅定性提示"主观问题回答具有较高随机性"。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。可视为公式的"伪代码表示"仅有坐标格式：

```
<ref>{目标名称}</ref><box>(x1, y1), (x2, y2)</box>
```

- `<ref>...</ref>`：语义标签，标识所框选对象的名称。
- `<box>(x1, y1), (x2, y2)</box>`：矩形包围框的两个对角顶点坐标 `(x1,y1)`、`(x2,y2)`。
- 整套标记由模型在一次生成中直接产出，无需后处理解析。

---

## 【关联】

原文未提供内部链接（`(无)`）。从内容可识别的逻辑依赖如下：

- `tokenizer.from_list_format` 与 `tokenizer.draw_bbox_on_latest_picture` 同属 `AutoTokenizer` 对象；后者依赖前者缓存的"最近一张图片"上下文，因此必须紧跟返回 box 的 `model.chat` 调用之后使用。
- `model.generation_config` 通过 `GenerationConfig.from_pretrained` 与权重一同下发，与 `torch.manual_seed` 共同决定生成结果的可复现性。
- 各示例在资源层面均依赖同一仓库下的资产目录 `assets/mm_tutorial/`（海报、医院招牌、菜单、城市照片、上海照片等）。

---

## 【使用方法】

**1. 环境与初始化（原文代码）**

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

# torch.manual_seed(1234)  # 需要可复现性时打开

tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen-VL-Chat", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen-VL-Chat", device_map="cuda",
    trust_remote_code=True).eval()
model.generation_config = GenerationConfig.from_pretrained(
    "Qwen/Qwen-VL-Chat", trust_remote_code=True)
```

**2. 推理调用范式（原文统一接口）**

```python
query = tokenizer.from_list_format([
    {'image': 'assets/mm_tutorial/xxx.jpeg'},   # 可省略或多张
    {'text':  'your question here'},             # 可省略（纯图/纯文场景）
])
response, history = model.chat(tokenizer, query=query, history=None)  # 首轮
# response, history = model.chat(tokenizer, query=query, history=history)  # 后续轮
print(response)
```

**3. Grounding 可视化（原文示例）**

```python
# 模型返回 <ref>...</ref><box>(x1,y1),(x2,y2)</box> 后：
image = tokenizer.draw_bbox_on_latest_picture(response, history)
image.save('Shanghai_Output.jpg')
```

**4. 资源与提示**
- 图像路径均相对于仓库 `assets/mm_tutorial/` 目录（如 `Rebecca_(1939_poster).jpeg`、`Hospital.jpg`、`Menu.jpeg`、`Chongqing.jpeg`、`Beijing.jpeg`、`Shanghai.jpg`）。
- 复现主观类输出（城市对比、旅游计划）建议显式调用 `torch.manual_seed(...)`；硬件/软件环境差异仍可能导致结果偏移。
- `device_map="cuda"` 表明原文默认 GPU 推理环境（CPU 配置项原文未涉及）。
