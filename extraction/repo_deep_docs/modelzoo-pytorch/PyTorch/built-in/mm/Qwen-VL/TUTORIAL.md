# Qwen-VL-Chat Tutorial

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/mm/Qwen-VL/TUTORIAL.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/mm/Qwen-VL/TUTORIAL.md

# Qwen-VL-Chat Tutorial 深度解读

## 【定位】
本教程文档面向已安装好 Qwen-VL-Chat 多模态大模型的使用者，通过五个递进的代码示例（海报问答→多轮对话→密集文字理解→数学推理→多图对比→目标检测框定位）演示该模型在视觉问答、文本理解、图表数学推理、多图推理以及视觉定位（Grounding）五大场景下的端到端调用流程。

## 【技术要点】

1. **模型初始化三件套**：通过 `transformers` 的 `AutoTokenizer.from_pretrained` 加载分词器，`AutoModelForCausalLM.from_pretrained`（`device_map="cuda"`、`trust_remote_code=True`）加载模型并 `.eval()` 进入推理模式，最后以 `GenerationConfig.from_pretrained` 装载生成配置；模型 ID 统一为 `"Qwen/Qwen-VL-Chat"`。

2. **多模态输入封装接口**：`tokenizer.from_list_format` 接受一个 list of dict，每个 dict 通过 `{'image': path}` 或 `{'text': str}` 表达图文交错输入，tokenizer 内部负责把图像与文本拼接、预处理并 tokenize 成模型可消费的 query。

3. **多轮对话状态管理**：每个 `model.chat` 调用返回 `(response, history)`，首轮使用 `history=None`，后续轮次将上一轮的 `history` 传入实现上下文延续；query 的图像只在需要时被重复送入。

4. **推理随机性控制**：通过 `torch.manual_seed(1234)` 或 `torch.manual_seed(5678)` 设置随机种子以复现教程中的输出；原文明确说明即使设了种子，软硬件环境差异仍可能导致结果不同。

5. **思维链提示技巧**：在数学推理样例中使用 `Think carefully step by step.` 引导模型分步推理，被作者标注为提升复杂任务准确率的"common prompt"。

6. **视觉定位（Grounding）输出格式**：调用定位能力时，模型以 `<ref>对象名</ref><box>(x1,y1),(x2,y2)</box>` 这样的 XML 风格标记输出文本与包围框坐标，文档原文样例截断于 `<ref>` 处。

## 【关键机制与数据】

**模型架构与编码流程（原文）**：原文说明 `tokenizer` 处理交错多模态输入，`model` 即 Qwen-VL-Chat 本体；初始化代码注释给出可选随机种子 `torch.manual_seed(1234)` 作为示例值。

**多轮问答流转（原文）**：
- 第一轮（针对 `assets/mm_tutorial/Rebecca_(1939_poster).jpeg`）：`history=None` → 输出 `"The name of the movie in the poster is "Rebecca.""`，与海报原片名一致。
- 第二轮（文本提问导演）：`history=history` → 输出 `"The movie "Rebecca" was directed by Alfred Hitchcock."`，将首轮识别出的电影名作为上下文事实回引。

**密集文字识别（原文）**：
- 输入 `assets/mm_tutorial/Hospital.jpg`，提问"哪一层是耳鼻喉科？"→ 输出 `"The Department of Otorhinolaryngology is located on the 4th floor."`
- 追问"哪一层是外科？"→ 输出 `"The Department of Surgery is located on the 3rd floor."`，证明模型在多轮间持续依赖图像中的版面信息作答。

**数学推理分步输出（原文）**：对 `Menu.jpeg` 提问 "two Salmon Burger and three Meat Lover's Pizza 的总价"，模型输出原文摘要：
- 2 × Salmon Burgers @ \$10 = \$20
- 3 × Meat Lover's Pizzas @ \$12 = \$36
- 合计 \$56
（以上单价与总价均直接来自文档样例输出。）

**多图对比与中文能力（原文）**：对 `Chongqing.jpeg`、`Beijing.jpeg` 两张图组合输入，中文 prompt 设为 `上面两张图片分别是哪两个城市？请对它们进行对比。`；示例输出提及"重庆的城市天际线…现代都市的繁华与喧嚣"以及"北京的天际线…中国首都的现代化和国际化"。原文警示此任务主观性强，未固定种子时每次输出不同。

**Grounding 输出（原文）**：针对 `Shanghai.jpg`，先用短中文 prompt `图里有啥` 得到建筑物描述，再用 `请给我框出图中上海环球金融中心和东方明珠` 触发定位，输出 XML 片段 `<ref>上海环球金融中心</ref><box>(667,437),(760,874)</box>和<ref>`（原文在此处截断）。

## 【表格解读】
**原文无表格**。全文仅含图片资源（`assets/mm_tutorial/Rebecca_(1939_poster).jpeg`、`Hospital.jpeg`、`Menu.jpeg`、`Chongqing.jpeg`、`Beijing.jpeg`、`Shanghai.jpg` 及其 `_Small` 缩略图）和代码块，未出现参数表、性能对比或配置项表格。

## 【公式解读】
**原文无公式**。教程示例仅出现金额累加 `$20 + $36 = $56` 这种文档样例输出中的算术自然语言，而非 LaTeX 或伪代码形式的可独立引用的公式。

## 【关联】
原文未给出内部链接或与其他模块的显式引用，文中上下游关系主要体现在代码调用层面：

- **与 tokenizer 模块的耦合**：`model.chat` 必须同时接收 `tokenizer` 对象与 `query`（`from_list_format` 的产物），两者同源依赖 `trust_remote_code=True` 的自定义代码。
- **与 history 状态对象的关系**：5 个示例中前 4 个的多轮示例都依赖 `history=history` 闭环累积，只在每节首轮使用 `history=None` 重置；Grounding 示例把"先描述"作为一轮、把"再框出"作为带历史的第二轮，形成 `history` 跨能力的桥接。
- **与示例数据资产（`assets/mm_tutorial/`）的关系**：5 个能力演示各绑定一张/两张图像，文末并无列出图片版权或下载命令，需依赖仓库 `assets/` 目录约定俗成使用。

## 【使用方法】

**启用方式**（原文给出的最小运行命令）：

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen-VL-Chat",
    device_map="cuda",
    trust_remote_code=True,
).eval()
model.generation_config = GenerationConfig.from_pretrained(
    "Qwen/Qwen-VL-Chat",
    trust_remote_code=True,
)
```

**关键调用模式**（原文模板）：

| 场景 | 关键参数 | 原文示例取值 |
|---|---|---|
| 单轮首次提问 | `history` | `None` |
| 多轮追问 | `history` | 上一轮返回的 `history` |
| 可复现性 | `torch.manual_seed` | 多图对比示例取 `5678`，其余示例取 `1234` |
| 复杂任务提示 | 追加 "Think carefully step by step." | 数学推理示例原文样例 |
| 触发定位 | prompt 含"框出 / 标出"等指令 | `请给我框出图中上海环球金融中心和东方明珠` |

**输出后处理**：Grounding 章节原文提示模型会以 `<ref>…</ref><box>(x1,y1),(x2,y2)</box>` 形式返回，可直接用于在原图上绘制矩形框（教程到此截断，未给出绘图代码；原文未涉及 bbox 坐标到 PIL/CV2 绘制的桥接脚本）。
