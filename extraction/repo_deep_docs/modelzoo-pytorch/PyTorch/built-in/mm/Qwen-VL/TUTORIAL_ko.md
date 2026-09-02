# Qwen-VL-Chat Tutorial

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/mm/Qwen-VL/TUTORIAL_ko.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/mm/Qwen-VL/TUTORIAL_ko.md

【定位】
这篇教程式指南文档解决"如何快速上手使用 Qwen-VL-Chat 多模态大模型"的问题,通过对模型初始化、接口调用与多种典型任务(视觉问答、密集文本理解、图表数学推理、多图中文推理、Grounding 框选、带框的图像描述)的示例化演示,展示该模型在 Hugging Face Transformers 接口下的能力边界与调用范式。

【技术要点】
1. **模型加载**:使用 `transformers` 库的 `AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)` 与 `AutoModelForCausalLM.from_pretrained(..., device_map="cuda", trust_remote_code=True).eval()` 加载分词器与模型,并通过 `GenerationConfig.from_pretrained(...)` 配置生成参数;`device_map="cuda"` 表明默认将模型部署在 GPU 上。原文:"```tokenizer``` 是 인터리브된 멀티모달 입력(interleaved multimodal inputs)을 전처리하는 데 사용되며, ```model```은 Qwen-VL-Chat 모델입니다."
2. **多模态输入构造**:`tokenizer.from_list_format([{'image': ...}, {'text': ...}, ...])` 用于把一张或多张图片与文本交错组装为单次查询;支持单图/多图,例如教程中的双图对照 (`Chongqing.jpeg` + `Beijing.jpeg`)。
3. **对话式调用**:通过 `response, history = model.chat(tokenizer, query=query, history=None|history)` 进行单轮/多轮对话,首次提问 `history=None`,后续追问传入先前 `history` 以维持多轮上下文。
4. **随机种子控制可复现性**:在初始代码中注释掉了 `torch.manual_seed(1234)`,在多图对照段落使用 `torch.manual_seed(5678)`,在 Grounding 段落使用 `torch.manual_seed(1234)`;原文特别强调:"`torch.manual_seed(5678)`를 사용하여 무작위 시드를 설정하지 않으면 매번 출력이 달라집니다. 랜덤 시드를 설정하더라도 하드웨어 및 소프트웨어 환경의 차이로 인해 얻은 결과가 이 튜토리얼과 다를 수 있습니다".
5. **Grounding 输出格式**:模型以 XML 风格标签同时输出文本与坐标,原文样例:`<ref>上海环球金融中心</ref><box>(667,437),(760,874)</box>和<ref>东方明珠</ref><box>(506,75),(582,946)</box>`;每个 `<box>` 提供左上/右下两个像素坐标。
6. **可视化与带框描述**:`tokenizer.draw_bbox_on_latest_picture(response, history)` 将最近一次对话中的 `<ref>`/`<box>` 标签渲染到图像上并保存(如 `Shanghai_Output.jpg`、`apple.jpg`);另外在 Grounded Captioning 中,只需在 prompt 中加入 `Generate the caption in English with grounding:` 即可一次性获得带框英文描述。

【关键机制与数据】
- **数据流(单轮)**:`assets/.../*.jpeg` 图片路径 → `tokenizer.from_list_format` 列表化封装 → `model.chat(tokenizer, query, history=None)` → 返回 `(response, history)`;文本回复直接打印。
- **数据流(多轮)**:首次问完后将返回的 `history` 回传给下一次 `model.chat(...)`,实现对话记忆。原文示例:第一问识别出电影 "Rebecca" → 第二问"谁导演了这部电影?" → 答出 "Alfred Hitchcock"。
- **数学推理示例数据**:菜单中 Salmon Burger 单价 $10、Meat Lover's Pizza 单价 $12,2 个 Salmon Burger = $20、3 个 Meat Lover's Pizza = $36,合计 $56(原文:"Therefore, the total cost would be $56.");此处使用了 "Think carefully step by by step" 类 CoT 提示,原文指出:"```단계별로 신중하게 생각하세요```는 복잡한 작업을 단계별로 모델에 안내하는 일반적인 프롬프트입니다. 따라서 완료해야 할 복잡한 작업이 있는 경우에는 이 프롬프트를 사용하여 모델의 정확도를 향상시켜 보세요."
- **Grounding 坐标数据**(原文):
  - 上海环球金融中心:`<box>(667,437),(760,874)</box>`
  - 东方明珠:`<box>(506,75),(582,946)</box>`
- **多语言能力**:同一模型可处理英文与中文 prompt,例如中文 prompt "上面两张图片分别是哪两个城市？请对它们进行对比。"、"图里有啥"、"请给我框出图中上海环球金融中心和东方明珠"、"帮我写个这座城市的旅游计划" 均直接由同一 `model.chat` 接口处理。
- **关于性能的提示**:原文没有提供推理速度、显存占用、token/s、精度等量化性能指标,只在"Grounding Capability"和"Multi-Figure Reasoning"两节明确指出"主观性问题输出结果多样、随机性较大"以及"不同硬件/软件环境可能造成差异",未给出具体性能数字。

【表格解读】
原文无表格。

【公式解读】
原文无公式。唯一接近"形式化表达"的 Grounding 输出结构可以视作一种伪代码标记约定(原文示例):
```
<ref>对象名</ref><box>(x1,y1),(x2,y2)</box>
```
其中 `<ref>...</ref>` 包裹模型识别的实体名称(自然语言文字),`<box>(x1,y1),(x2,y2)</box>` 提供该实体在图像中的左上角像素坐标 `(x1,y1)` 与右下角像素坐标 `(x2,y2)`;一个响应可包含多组 `<ref>...<box>...` 配对,以覆盖多个目标对象(原文同时给出 上海环球金融中心 与 东方明珠 两组框)。

【关联】
文档内未提供内部链接,文末关联信息显示"内部链接: (无)"。从内容上看,本教程属于 modelzoo-pytorch 仓 `PyTorch/built-in/mm/Qwen-VL` 目录下的**面向用户的使用样例层**,其上游是 Qwen-VL-Chat 本身(由 Hugging Face 仓库 `Qwen/Qwen-VL-Chat` 通过 `trust_remote_code=True` 远程加载),其下游/可拓展的相关能力在教程中依次铺垫:
- 视觉问答 → 密集文本理解 → 图表数学推理(隐含 chain-of-thought 提示技巧)
- 单图 → 多图中文推理(扩展到跨语言输入)
- 自由对话 → Grounding 输出(扩展到空间定位)
- 纯文本 → Grounded Captioning(将 captioning 与 grounding 融合,产出带框的英文描述)

【使用方法】
原文已给出完整可运行的 Python 调用流程,核心启用与配置命令/参数如下:
1. **安装/依赖**:原文未给出 `pip install` 命令,仅依赖 `torch` 与 `transformers`(`from transformers import AutoModelForCausalLM, AutoTokenizer`, `from transformers.generation import GenerationConfig`)。
2. **模型与分词器加载**(原文代码):
   ```python
   tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
   model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-VL-Chat", device_map="cuda", trust_remote_code=True).eval()
   model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
   ```
3. **查询构造**:`tokenizer.from_list_format([{'image': '<图片路径>'}, {'text': '<文本>'}, ...])`,可叠加多张图片或多段文本。
4. **推理调用**:`response, history = model.chat(tokenizer, query=query, history=None)`(首轮)/ `history=history`(后续轮)。
5. **Grounding 可视化**:`image = tokenizer.draw_bbox_on_latest_picture(response, history); image.save('Shanghai_Output.jpg')`。
6. **可复现性**:`torch.manual_seed(1234)`(Grounding 段)、`torch.manual_seed(5678)`(多图中文段);首段代码中以注释形式保留了 `torch.manual_seed(1234)` 作为可选项。
8. **CoT 提示模板**:对复杂推理任务在 prompt 末尾追加 "Think carefully step by step" / "단계별로 신중하게 생각하세요" 类逐步思考指令以提高准确率。

> 说明:原文 "Grounded Captioning" 节在给出"如何获取不带 `<box>` 标注的纯文本 caption"的 `import re; clean_respo...` 代码片段处被截断,后续清洗正则与完成代码原文未提供,因此本节"去除 box 标注的具体正则与代码"在原文中不完整。
