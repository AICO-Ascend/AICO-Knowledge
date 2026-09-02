# EAGLE Draft Models

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/eagle.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/eagle.md

# EAGLE Draft Models 文档深度解读

## 【定位】
这篇文档描述如何在 vLLM 中配置基于 EAGLE (Extrapolation Algorithm for Greater Language-model Efficiency) 的 draft 模型来执行 speculative decoding,分别给出 EAGLE 与 EAGLE3 两种 drafter 的最小可运行示例与预训练模型获取来源。

## 【技术要点】
1. **Speculative decoding 框架**:通过 EAGLE 草稿模型生成候选 token,主模型(原文示例为 `meta-llama/Meta-Llama-3-8B-Instruct`)并行验证,提升推理吞吐。
2. **EAGLE (v1) drafter**:使用 `yuhuili/EAGLE-LLaMA3-Instruct-8B` 作为 draft model;主模型 `tensor_parallel_size=4`,draft 模型 `draft_tensor_parallel_size=1`(草稿模型并行度可独立于主模型)。
3. **EAGLE3 drafter**:使用 `RedHatAI/Llama-3.1-8B-Instruct-speculator.eagle3` 作为 draft model;主模型 `tensor_parallel_size=2`,draft 模型 `draft_tensor_parallel_size=2`,且 `method` 字段需显式设置为 `"eagle3"` 以区分版本。
4. **关键投机参数**:`num_speculative_tokens=2`,即每步生成 2 个候选 token 由主模型并行校验。
5. **采样参数**:示例使用 `SamplingParams(temperature=0.8, top_p=0.95)`。
6. **兼容性约束**:`vllm<0.7.0` 需要用外部 gist 脚本转换 speculative model,并通过本地路径 `path/to/modified/eagle/model` 注入 `speculative_config["model"]`。

## 【关键机制与数据】
原文未涉及工作原理细节、性能数据(如 acceptance rate、加速比、吞吐量数字)或内部数据流图。原文仅以提示语形式说明:"a more detailed example for offline mode, including how to extract request level acceptance rate, can be found in [examples/features/speculative_decoding/spec_decode_offline.py](../../../examples/features/speculative_decoding/spec_decode_offline.py)",即将"如何提取请求级 acceptance rate"这一执行链路细节委托给了 `spec_decode_offline.py` 示例。文档本身不展示数据流,也不引用论文中关于 EAGLE 的 extrapolation 公式,仅给出配置入口。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。

## 【关联】
- **下游示例模块**:`../../../examples/features/speculative_decoding/spec_decode_offline.py`(位于 `examples/features/speculative_decoding/` 路径下),用于离线模式中更细粒度的 speculative decoding 用法,包括如何抽取 request 级别的 acceptance rate;本文档视其为补充说明与延伸阅读入口。
- **外部资源**:
  - EAGLE 论文 [arXiv:2401.15077](https://arxiv.org/pdf/2401.15077),作为方法出处。
  - Hugging Face 集合 [RedHatAI/speculator-models](https://huggingface.co/collections/RedHatAI/speculator-models) 与 [yuhuili/models(搜索关键字 eagle)](https://huggingface.co/yuhuili/models?search=eagle),提供预训练 draft 模型分发渠道(涵盖 EAGLE 与 EAGLE3 两类)。
- **版本兼容分支**:对 `vllm<0.7.0` 用户,文档指向外部 gist 脚本 [abhigoyal1997/1e7a4109](https://gist.github.com/abhigoyal1997/1e7a4109ccb7704fbc67f625e86b2d6d) 进行模型转换,说明本特性在 vLLM 主线与旧版之间存在 draft 模型格式上的兼容性差异。

## 【使用方法】
原文以两段可直接复制运行的 Python 代码呈现启用方式,核心配置项均通过 `LLM(...)` 的 `speculative_config` 字典传入:

- **EAGLE (v1) drafter 启用方式**:
  ```python
  llm = LLM(
      model="meta-llama/Meta-Llama-3-8B-Instruct",
      tensor_parallel_size=4,
      speculative_config={
          "model": "yuhuili/EAGLE-LLaMA3-Instruct-8B",
          "draft_tensor_parallel_size": 1,
          "num_speculative_tokens": 2,
          "method": "eagle",
      },
  )
  ```
- **EAGLE3 drafter 启用方式**:
  ```python
  llm = LLM(
      model="meta-llama/Meta-Llama-3-8B-Instruct",
      tensor_parallel_size=2,
      speculative_config={
          "model": "RedHatAI/Llama-3.1-8B-Instruct-speculator.eagle3",
          "draft_tensor_parallel_size": 2,
          "num_speculative_tokens": 2,
          "method": "eagle3",
      },
  )
  ```
- **可配置字段(原文显式给出)**:`speculative_config["model"]`、`speculative_config["draft_tensor_parallel_size"]`、`speculative_config["num_speculative_tokens"]`、`speculative_config["method"]`(取值为 `"eagle"` 或 `"eagle3"`)。
- **采样侧**:`SamplingParams(temperature=0.8, top_p=0.95)`。
- **生成调用**:`outputs = llm.generate(prompts, sampling_params)`,随后通过 `output.outputs[0].text` 取得生成文本。
- **旧版兼容说明**:`vllm<0.7.0` 需先以外部 gist 脚本转换 draft 模型,再以本地路径形式填入 `speculative_config["model"]`。
