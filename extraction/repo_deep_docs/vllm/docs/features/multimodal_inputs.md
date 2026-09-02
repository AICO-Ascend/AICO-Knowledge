# Multimodal Inputs

> 仓 `vllm` · 路径 `docs/features/multimodal_inputs.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/multimodal_inputs.md

# 深度解读：vLLM Multimodal Inputs 文档

---

## 【定位】

这篇文档面向**多模态模型的使用者**，系统性地讲解了如何在 vLLM 中以**离线推理（Offline Inference）**方式向多模态模型（视觉语言模型、音频语言模型等）传递图像、RGBA 图像、多图、视频帧等多模态输入，以及对应的提示词构造、数据字典格式、批量推理与特殊模型（Moondream3）的提示词配方，同时给出了**安全防护**建议（防 SSRF）。

---

## 【技术要点】

1. **多模态数据载体**：通过 `vllm.inputs.PromptType` 协议传递离线推理请求，核心字段为 `prompt`（遵循 HuggingFace 模型仓库文档规定的文本格式）与 `multi_modal_data`（遵循 `vllm.inputs.MultiModalDataDict` schema 的字典）。图像通过 `"image"` 键传入，支持单张 PIL.Image 对象或列表形式的多张图像。

2. **安全策略（SSRF 防护）**：
   - 启动参数 `--allowed-media-domains`，可接受域名字符串列表（例：`upload.wikimedia.org github.com www.bogotobogo.com`），限制 vLLM 可访问的远程媒体来源。
   - 环境变量 `VLLM_MEDIA_URL_ALLOW_REDIRECTS=0`，禁止 HTTP 重定向以绕过域名限制。
   - 特别提示：在容器化环境中 vLLM Pod 可能拥有内网不受限访问能力，因此该限制尤为重要。

3. **单图与批量推理**：`llm.generate()` 可同时接受单条 `{prompt, multi_modal_data}` 字典（单条推理）或字典列表（批量推理），LLM 类统一处理。

4. **多图推理（同一 prompt 嵌入多张图像）**：以 `microsoft/Phi-3.5-vision-instruct` 为例，需设置 `trust_remote_code=True`、`max_model_len=4096`、`limit_mm_per_prompt={"image": 2}`（最大接受图像数），并在 prompt 中使用 `<|image_1|>` / `<|image_2|>` 占位符，`multi_modal_data["image"]` 传 list。

5. **LLM.chat 多种图像格式**：支持 `image_url`（URL）、`image_pil`（PIL 对象）、`image_embeds`（torch 预计算张量）三种 type；`image_url` 也支持 `data:image/jpeg;base64,{base64_image}` 内联编码格式（用于视频帧的 base64 编码）。

6. **视频帧转图像输入**：以 `Qwen/Qwen2-VL-2B-Instruct` 为例，通过 `limit_mm_per_prompt={"image": 4}` 限制每 prompt 最大帧数（原文标注可调整），将视频帧逐帧以 `image_url` 类型拼接进 message content。

7. **RGBA 透明背景定制**：通过 `LLM` 构造参数 `media_io_kwargs={"image": {"rgba_background_color": [R, G, B]}}` 控制 RGBA→RGB 转换时的填充色；接受 list 或 tuple，每通道取值范围 0–255；默认 `(255, 255, 255)` 白色背景；仅对带透明通道的 RGBA 图像生效，RGB 图像不受影响。

8. **Moondream3 任务专属 prompt 配方**：`Moondream3ForCausalLM` 支持 `query`（图像问答）与 `caption`（图像描述）两种任务；通过特殊 token `<|endoftext|>`、`<image>`、`<|md_reserved_0|>`、`<|md_reserved_1|>`、`<|md_reserved_2|>` 拼装；`caption` 任务支持 `length` 参数（默认 `"normal"`）；使用 `tokenizer="moondream/starmie-v1"`、`max_model_len=2048`、`limit_mm_per_prompt={"image": 1}`。

---

## 【关键机制与数据】

**工作原理与数据流：**

- **离线推理链路（原文）**：用户构造 `PromptType`（含 `prompt` 文本 + `multi_modal_data` 字典）→ 调用 `llm.generate()` 或 `llm.chat()` → vLLM 依据 `multi_modal_data` 中各 modality 键（`image` / `audio` 等）查找对应处理管线 → 输出 `RequestOutput`，从中取 `o.outputs[0].text` 作为生成文本。

- **prompt 格式来源（原文）**：`prompt` 字段格式需"Refer to the HuggingFace repo for the correct format to use"，意味着模板由模型自身决定，vLLM 不强制统一格式。
  - LLaVA-1.5：`USER: <image>\nWhat is the content of this image?\nASSISTANT:`
  - Phi-3.5-vision：`<|user|>\n<|image_1|>\n<|image_2|>\nWhat is the content of each image?<|end|>\n<|assistant|>\n`
  - Moondream3 query：`<|endoftext|><image><|md_reserved_0|>query<|md_reserved_1|>{question}<|md_reserved_2|>`
  - Moondream3 caption：`<|endoftext|><image><|md_reserved_0|>describe<|md_reserved_1|>{length}<|md_reserved_2|>`

- **图像输入多源支持（原文）**：`LLM.chat` 的 message content 支持 `image_url`（远程 URL 或 base64 data URI）、`image_pil`（PIL Image 对象）、`image_embeds`（`torch.load` 预计算嵌入张量）三种并存形式。

- **RGBA 转换机制（原文）**：vLLM 将 RGBA 图像转 RGB，透明像素被 `rgba_background_color` 指定颜色替换；未设置时回退到白色 `(255, 255, 255)`，纯 RGB 图像不受该参数影响。

- **关键配置数值（原文）**：
  - Phi-3.5-vision：`max_model_len=4096`，`limit_mm_per_prompt={"image": 2}`
  - Qwen2-VL-2B-Instruct：`limit_mm_per_prompt={"image": 4}`（每视频最大帧数 4，原文注释"可调整"）
  - Moondream3：`max_model_len=2048`，`limit_mm_per_prompt={"image": 1}`，`SamplingParams(max_tokens=64, temperature=0)`

**性能数据**：原文**未提供**性能基准（如吞吐量、延迟、显存占用等）相关数字；亦无对比测试数据。

---

## 【表格解读】

**原文无表格。** 文档结构以代码示例 + 说明性 note/tip 段落为主，未出现参数对照表、性能对比表或配置项矩阵。所有数值（如 `max_model_len=4096`、`limit_mm_per_prompt={"image": 2}` 等）均散落于代码片段与文字描述中。

---

## 【公式解读】

**原文无公式。** 文档不涉及数学公式、伪代码算法或 LaTeX 表达式。所有行为均通过 Python 代码示例（`LLM` 类调用、`SamplingParams` 配置、字典 schema 等）描述。

---

## 【关联】

根据文末内部链接，该文档与以下模块/特性紧密耦合：

| 链接目标 | 关联性质 |
|---|---|
| `../models/supported_models.md#list-of-multimodal-language-models` | 上游依赖：明确**哪些模型被 vLLM 支持为多模态语言模型**，决定本文档 API 的适用范围 |
| `../models/generative_models.md#llmchat` | API 依赖：`LLM.chat` 方法的详细定义与签名，本文通过 `LLM.chat` 演示图像多源输入 |
| `../../examples/generate/multimodal/vision_language_offline.py` | 单图离线推理完整示例（与文档中 LLaVA 单图片段对应） |
| `../../examples/generate/multimodal/vision_language_multi_image_offline.py` | 多图离线推理完整示例（与 Phi-3.5-vision 多图片段对应） |
| `../../examples/generate/multimodal/audio_language_offline.py` | 音频多模态输入的离线推理示例（与本文"图像"并列的音频 modality） |
| `../../examples/generate/multimodal/openai_chat_completion_client_for_multimodal.py` | 通过 OpenAI 兼容客户端调用多模态能力（在线服务路径） |
| `../../vllm/transformers_utils/chat_templates/registry.py` | Chat 模板注册表：管理 `LLM.chat` 中不同模型的多模态消息渲染模板 |
| `../../examples/pooling/embed/template/vlm2vec_phi3v.jinja` | 嵌入（pooling）场景下的 VLM→向量模板，扩展多模态的 pooling 用法 |
| `../../examples` | vLLM 示例总入口，覆盖更多模型与 modality 组合 |

**延伸关系**：
- 文档开头指向 GitHub Issue #4194（多模态支持 RFC），说明该能力处于**持续迭代状态**。
- 文档提示"open an issue on GitHub"用于反馈，是与社区贡献流程的接口。
- 安全建议部分与 vLLM 服务端/部署模块（`--allowed-media-domains`、`VLLM_MEDIA_URL_ALLOW_REDIRECTS` 环境变量）紧密关联，涉及网络层与 media loader 子系统。

---

## 【使用方法】

### 1. 服务端/部署层安全配置

| 项 | 形式 | 示例 / 取值 |
|---|---|---|
| `--allowed-media-domains` | vLLM 启动命令行参数 | `--allowed-media-domains upload.wikimedia.org github.com www.bogotobogo.com`（空格分隔的域名列表） |
| `VLLM_MEDIA_URL_ALLOW_REDIRECTS` | 环境变量 | 设置 `=0` 禁止 HTTP 重定向绕过域名限制 |

### 2. 离线推理基础 API

```python
from vllm import LLM
llm = LLM(model="...")                # 加载多模态模型
outputs = llm.generate({              # 单条
    "prompt": "...",
    "multi_modal_data": {"image": image},
})
# 或传入 list → 批量
outputs = llm.generate([{...}, {...}])
generated_text = outputs[0].outputs[0].text
```

### 3. 多图推理（以 Phi-3.5-vision 为例）

```python
llm = LLM(
    model="microsoft/Phi-3.5-vision-instruct",
    trust_remote_code=True,
    max_model_len=4096,
    limit_mm_per_prompt={"image": 2},
)
outputs = llm.generate({
    "prompt": "<|user|>\n<|image_1|>\n<|image_2|>\n...<|end|>\n<|assistant|>\n",
    "multi_modal_data": {"image": [image1, image2]},
})
```

### 4. `LLM.chat` 多源图像输入

支持的 `content` type：
- `"image_url"`：传 `{"url": <url 或 base64 data URI>}`（URL 示例 `https://picsum.photos/id/32/512/512`，base64 示例 `data:image/jpeg;base64,{base64_image}`）
- `"image_pil"`：传 PIL Image 对象（例：`ImageAsset('cherry_blossom').pil_image`）
- `"image_embeds"`：传 `torch.load(...)` 加载的预计算嵌入
- `"text"`：传 `{"text": "..."}` 文本段落

### 5. 视频帧推理（以 Qwen2-VL 为例）

```python
llm = LLM("Qwen/Qwen2-VL-2B-Instruct", limit_mm_per_prompt={"image": 4})
# 视频帧逐帧 base64 编码后追加为 image_url 条目
message["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
outputs = llm.chat([message])
```

### 6. RGBA 背景色定制

```python
# 默认白色（无需设置）
llm = LLM(model="llava-hf/llava-1.5-7b-hf")

# 自定义黑色
llm = LLM(
    model="llava-hf/llava-1.5-7b-hf",
    media_io_kwargs={"image": {"rgba_background_color": [0, 0, 0]}},
)

# 自定义蓝色
llm = LLM(
    model="llava-hf/llava-1.5-7b-hf",
    media_io_kwargs={"image": {"rgba_background_color": [0, 0, 255]}},
)
```

参数约束（原文）：
- 类型：`list` 或 `tuple`，长度 3（如 `[R, G, B]`）
- 范围：每通道 `0–255`
- 默认值：`(255, 255, 255)`（白色，向后兼容）
- 作用范围：仅影响带透明通道的 RGBA 图像；纯 RGB 图像不受影响

### 7. Moondream3 任务 prompt 配方

```python
llm = LLM(
    model="moondream/moondream3-preview",
    tokenizer="moondream/starmie-v1",
    trust_remote_code=True,
    max_model_len=2048,
    limit_mm_per_prompt={"image": 1},
)
# query 任务：使用 <|md_reserved_0|>query<|md_reserved_1|>{question}<|md_reserved_2|>
# caption 任务：使用 <|md_reserved_0|>describe<|md_reserved_1|>{length}<|md_reserved_2|>
# 推理时配合 SamplingParams(max_tokens=64, temperature=0)
```

> **注意**：原文在 `caption_out = llm.generate` 处被截断，caption 任务的完整 `llm.generate(...)` 调用示例与返回值未在已提供片段中给出，使用时需参照 Moondream3 模型官方仓库或 vLLM 完整版文档。
