# Prompt Embedding Inputs

> 仓 `vllm` · 路径 `docs/features/prompt_embeds.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/prompt_embeds.md

# vLLM Prompt Embedding Inputs 文档深度解读

## 【定位】

这篇文档描述了 vLLM 如何接收**预计算的 prompt 嵌入向量（prompt embeddings）作为模型输入**——即跳过「文本→token ids→嵌入向量」链路中的前两步，让调用方直接把张量送入模型，从而支持 token 词表之外的嵌入、自定义嵌入空间的输入，以及嵌入与文本的混合提示。

## 【技术要点】

1. **核心数据结构**：在离线推理中使用 `vllm.inputs.EmbedsPrompt` 协议，关键字段为 `prompt_embeds`，是一个形状为 `(sequence_length, hidden_size)` 的 `torch.Tensor`，其中 `sequence_length` 是嵌入对应的 token 数量，`hidden_size` 是模型的隐藏层维度。
2. **离线路径**：可直接传入来自 Hugging Face Transformers 模型的 prompt embeddings 到 `prompt_embeds` 字段（参考 `prompt_embed_offline.py`）。
3. **在线路径启用开关**：通过 OpenAI 兼容服务启用，对应命令为 `vllm serve ... --enable-prompt-embeds`；同时支持 Completions API 与 Chat Completions API。
4. **Completions API 传输方式**：在 JSON 请求体中使用 `prompt_embeds` 键，载荷为 **base64 编码的 torch tensor**；当与 `prompt` 混合输入时，embedds 总是排在前部；**服务端不应用 chat template**，调用方需自行对完整模板化后的 token 序列做嵌入。
5. **Chat Completions API 传输方式**：将 `prompt_embeds` 作为 `content` 中的一个 content part（类型 `"type": "prompt_embeds"`，数据 `"data": "<base64_encoded_tensor>"`），可与 `"type": "text"` 文本 part 交错；多个 `prompt_embeds` part 可出现在任意消息、任意位置；服务端在 chat template 渲染阶段先将其扩展为占位 token，再把预计算嵌入在对应位置拼接到模型输入中。
6. **Chat Completions 关键约束**：每个 `prompt_embeds` part 应**只编码纯内容**（不再包含已模板化的整段对话），由服务端像处理普通文本 `content` 字符串一样将 chat template 包裹在外；否则会导致模板被双重应用。
7. **安全约束**：原文明确警告「vLLM engine may crash if incorrect shape of embeddings is passed」，并指出 `--enable-prompt-embeds` 仅应面向受信用户开启。

## 【关键机制与数据】

**工作原理（按调用路径拆解）**

- **文本到嵌入的传统链路（原文描述）**：对于典型的 decoder-only 模型（如 `meta-llama/Llama-3.1-8B-Instruct`），token id → prompt embedding 这一步通过查找**学习到的 embedding matrix**完成；但模型**不限于只能处理与自身 token 词表对应的嵌入**——这就是支持外部 prompt embeddings 的根本动机。
- **离线输入流**：调用方准备 `prompt_embeds` 张量 → 通过 `vllm.inputs.EmbedsPrompt` 协议送入 vLLM 引擎 → 引擎直接将该张量送入模型，跳过 tokenizer 与 embedding lookup。
- **在线输入流（Completions API）**：
  - 调用方先在客户端将 torch tensor **base64 编码**，作为 JSON 字段 `prompt_embeds` 发送。
  - 服务端解码后直接用于模型输入；如果同时提供 `prompt`，embedds 排在前部。
  - **服务端不做 chat template 渲染**，因此若模型依赖 chat template，调用方必须自行：① 应用 chat template → ② 对得到的所有 token id 做嵌入 → ③ 将整段嵌入提交（即系统提示、角色标记、generation prompt 等都应已「烤」入嵌入）。
- **在线输入流（Chat Completions API）**：
  - 客户端将每个 `prompt_embeds` part 以 base64 形式放入 content 列表。
  - 服务端在 chat template 渲染阶段把每个 `prompt_embeds` part **展开为正确数量的占位 token**，再在对应 token 位置上**将预计算嵌入 splice 进模型输入**。
  - 与 Completions 不同：这里 **embedding 内容应为"纯内容"**，模板由服务端在请求时刻像处理普通 `content` 字符串一样动态包裹——避免双重模板化。

**性能/数值相关数据**：原文未给出基准性能数据或显存/吞吐数字，仅定义了张量形状 `(sequence_length, hidden_size)` 与 `(num_tokens, hidden_size)`。

## 【表格解读】

**原文无表格**。

## 【公式解读】

**原文无 LaTeX 公式**，但有两处关键的张量形状定义，逐字保留并解读如下：

1. 离线（`vllm.inputs.EmbedsPrompt`）字段定义：

   $$\texttt{prompt\_embeds} \in \mathbb{R}^{(\texttt{sequence\_length},\ \texttt{hidden\_size})}$$

   符号含义：
   - `sequence_length`：嵌入序列长度，即对应的 token 数量。
   - `hidden_size`：模型隐藏层维度（embedding size），需与目标模型的 `hidden_size` 一致。
   - 类型：`torch.Tensor`。

2. 在线 Chat Completions 每个 content part 的 data 字段：

   $$\texttt{data} \;\text{为 base64 编码的}\ \texttt{torch.Tensor},\ \text{形状}\ (\texttt{num\_tokens},\ \texttt{hidden\_size})$$

   符号含义：
   - `num_tokens`：该 part 嵌入对应的 token 数量。
   - `hidden_size`：同上，需匹配模型。
   - `data`：经过 base64 序列化后的字节串，便于通过 JSON 传输。

## 【关联】

- **上游示例 / 调用方代码**：
  - 离线用例：[`examples/features/prompt_embed/prompt_embed_offline.py`](../../examples/features/prompt_embed/prompt_embed_offline.py) —— 展示如何将 Hugging Face Transformers 模型的输出送入 `vllm.inputs.EmbedsPrompt` 的 `prompt_embeds` 字段。
  - 在线用例（OpenAI Client）：[`examples/features/prompt_embed/prompt_embed_inference_with_openai_client.py`](../../examples/features/prompt_embed/prompt_embed_inference_with_openai_client.py) —— 展示使用 OpenAI 兼容客户端（启动经 `--enable-prompt-embeds` 的 `vllm serve`）提交 base64 tensor 的完整流程。
- **协议 / 类型**：[`vllm.inputs.EmbedsPrompt`][]（文档内链接）——离线推理的输入 schema 容器。
- **服务端 HTTP 接口**：
  - [Completions API](https://platform.openai.com/docs/api-reference/completions) —— `prompt_embeds` 作为顶层 JSON 键。
  - [Chat Completions API](https://platform.openai.com/docs/api-reference/chat) —— `prompt_embeds` 作为消息 `content` 数组中的 content part。
- **上下文关联**：文档与「多模态输入」相关——`Offline Inference` 章节首句「To input multi-modal data, follow this schema in `vllm.inputs.EmbedsPrompt`」表明 prompt embeddings 是 vLLM 多模态输入承载机制的一部分（嵌入既可来自文本，也可来自其他模态编码器）；同时也与 chat template 子系统紧耦合，因为 Chat Completions API 路径下服务端需要把 `prompt_embeds` part 翻译为占位 token 后再 splice。

## 【使用方法】

**离线推理启用方式（原文有）**

- 使用 `vllm.inputs.EmbedsPrompt` 类型构造输入，关键字段为 `prompt_embeds: torch.Tensor`，形状 `(sequence_length, hidden_size)`。
- 可直接传入来自 Hugging Face Transformers 模型的输出，参考 [`prompt_embed_offline.py`](../../examples/features/prompt_embed/prompt_embed_offline.py)。

**在线服务启用方式（原文给出完整命令）**

启动 OpenAI 兼容 server 时加上 `--enable-prompt-embeds`：

```bash
vllm serve meta-llama/Llama-3.2-1B-Instruct --runner generate \
  --max-model-len 4096 --enable-prompt-embeds
```

- `--enable-prompt-embeds`：开启 prompt embeddings 接收（Completions API 与 Chat Completions API 同时启用）。
- `--max-model-len 4096`：设置最大模型长度（原文示例参数）。
- `--runner generate`：选择 generate runner（原文示例参数）。
- 模型使用 `meta-llama/Llama-3.2-1B-Instruct`（原文示例模型）。

**请求构造（原文有）**

- Completions API：在 JSON body 中放 `"prompt_embeds": "<base64_encoded_tensor>"`，可与 `"prompt"` 同请求共存（embedds 排在前）。
- Chat Completions API：在消息的 `content` 数组中插入 `{"type": "prompt_embeds", "data": "<base64_encoded_tensor>"}`，可与 `{"type": "text", "text": "..."}` 任意交错、任意数量；tensor 形状应为 `(num_tokens, hidden_size)`。

**客户端示例**

- OpenAI Python 客户端调用见 [`prompt_embed_inference_with_openai_client.py`](../../examples/features/prompt_embed/prompt_embed_inference_with_openai_client.py)。

**注意事项（原文明确给出）**

- Completions API：调用方必须自行完成 chat template + 嵌入；服务端不应用模板。
- Chat Completions API：`prompt_embeds` part 只承载纯内容，模板由服务端动态包裹；不要把已模板化的整段对话编码进去。
- 安全：`--enable-prompt-embeds` 仅对受信用户开启；错误的嵌入形状可能导致 vLLM engine 崩溃。
