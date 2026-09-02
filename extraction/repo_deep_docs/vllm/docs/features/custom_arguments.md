# Custom Arguments

> 仓 `vllm` · 路径 `docs/features/custom_arguments.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/custom_arguments.md

# vLLM Custom Arguments 文档深度解读

## 【定位】

这篇文档解决的是 **如何在不修改 vLLM 源码、不重新编译的前提下, 向 vLLM 推理请求传入 `SamplingParams` 和标准 REST API 规范之外的任意自定义参数** —— 主要服务于自定义 logits processor 等需要往请求链路里注入额外参数的扩展场景。

## 【技术要点】

- **零侵入式扩展通道**: 自定义参数以 `dict` 形式传入, 添加或删除均**无需重新编译 vLLM** (原文: "Adding or removing a vLLM custom argument does not require recompiling vLLM, since the custom arguments are passed in as a dictionary.")。
- **离线入口 `SamplingParams.extra_args`**: 通过 `SamplingParams(extra_args={"your_custom_arg_name": 67})` 把 dict 注入, 任何能访问 `SamplingParams` 的代码都能读取。
- **在线入口 `vllm_xargs`**: 同时支持 **OpenAI 兼容 REST API** 与 **Anthropic 兼容 `/v1/messages` 端点**, 通过 JSON body 中的 `vllm_xargs` 字段传入。
- **OpenAI SDK 兼容**: SDK 用户通过 `client.completions.create(..., extra_body={"vllm_xargs": {...}})` 透传, 无需直接拼 HTTP 请求体。
- **离/在线统一**: 文档明确 `vllm_xargs` 在底层被赋值给 `SamplingParams.extra_args`, 因此**离线和在线两条路径共用同一套下游消费代码**。
- **配套校验要求**: 自定义 logits processor 必须实现 `validate_params`, 否则非法参数会导致**未定义行为** (原文: "invalid custom arguments can cause unexpected behaviour")。

## 【关键机制与数据】

**工作原理 (三段式流转)**:

1. **入口注入**: 用户在请求构造阶段 (离线 `SamplingParams` 构造 / 在线 JSON body / SDK `extra_body`) 把 dict 形态的自定义参数塞进去。
2. **桥接归一**: 在线入口的 `vllm_xargs` 被服务端**映射到 `SamplingParams.extra_args`**, 完成"在线字段 → 离线字段"的翻译。
3. **下游消费**: 任何拿到 `SamplingParams` 的代码 (尤其是自定义 logits processor) 通过 `extra_args` 字典读取所需参数, 并由 `validate_params` 做合法性校验。

**数据流 (原文)**:
> "`vllm_xargs` is assigned to `SamplingParams.extra_args` under the hood, so code which uses `SamplingParams.extra_args` is compatible with both offline and online scenarios."

**性能数据**: 原文**未给出**任何吞吐量、延迟或内存相关的性能数字。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

文档**本身只显式引用了一个内部链接**, 但围绕该特性存在一条清晰的上下游依赖链:

| 关联对象 | 关系 | 说明 |
|---|---|---|
| `./custom_logitsprocs.md` (Custom Logits Processors) | **直接下游 / 主要用例** | 文档开头即指出 custom arguments 的典型动机是"在不修改 vLLM 源码的前提下使用自定义 logits processor"; 反向地, custom_logitsprocs 文档必然依赖本文的 `extra_args` / `vllm_xargs` 通道把参数投递到 processor 中。 |
| `SamplingParams` | **核心数据结构** | 既是离线入口字段 (`extra_args`) 的宿主, 也是在线 `vllm_xargs` 的最终落地字段。 |
| `LLM` (离线推理引擎) | **离线下游** | 接收带 `extra_args` 的 `SamplingParams`, 把参数暴露给 logits processor 等扩展点。 |
| vLLM REST API Server (端口 8000) | **在线入口** | 通过 `vllm_xargs` 字段透传自定义参数, 同时支持 OpenAI 兼容端点 (`/v1/completions`) 和 Anthropic 兼容端点 (`/v1/messages`)。 |
| OpenAI Python SDK | **在线旁路封装** | 通过 `extra_body={"vllm_xargs": {...}}` 实现客户端侧的参数注入, 底层仍走同一 REST 通道。 |

## 【使用方法】

**离线 (Offline) — Python SDK**:

```python
SamplingParams(extra_args={"your_custom_arg_name": 67})
```

**在线 (Online) — OpenAI 兼容 REST API**:

```bash
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        ...
        "vllm_xargs": {"your_custom_arg": 67}
    }'
```

**在线 (Online) — OpenAI Python SDK**:

```python
batch = await client.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    ...,
    extra_body={
        "vllm_xargs": {
            "your_custom_arg": 67
        }
    }
)
```

**前置约束 (原文 note)**: 若自定义参数要喂给自定义 logits processor, 该 processor **必须实现 `validate_params`**, 否则传入的非法参数可能引发未预期行为。

**未涉及**: 文档**未给出** `validate_params` 的签名、必传/可选字段、错误传播方式等细节, 也未给出最大 dict 大小、并发限制、序列化限制等运行时约束 —— 这些都需要回到 `./custom_logitsprocs.md` 或 `SamplingParams` 源码中查阅。
