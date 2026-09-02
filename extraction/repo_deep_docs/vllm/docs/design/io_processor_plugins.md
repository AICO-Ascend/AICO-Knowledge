# IO Processor Plugins

> 仓 `vllm` · 路径 `docs/design/io_processor_plugins.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/io_processor_plugins.md

# IO Processor Plugins 设计文档深度解读

## 【定位】

本文档描述 vLLm 的 **IO Processor 插件机制**：一种允许用户为 pooling 模型自定义输入/输出预处理与后处理的扩展能力，从而支持诸如"输入图像、输出图像"等多模态生成场景，并提供完整的插件接口规范、加载方式与优先级规则。

---

## 【技术要点】

- **适用模型范围**：插件机制当前**仅支持 pooling 模型**，触发方式包括 `LLM` / `AsyncLLM` 的 `encode` 方法，以及在线服务模式下的 `/pooling` endpoint。
- **数据契约**：prompt 类型和最终 request 输出类型均由插件自定义；**vLLm 不对输入/输出数据做任何验证**，正确性完全由插件负责。
- **核心接口**：`IOProcessor`（位于 `vllm.plugins.io_processors.interface`），提供以下关键方法：
  - `parse_data(data)` — 校验用户数据并转换为 `pre_process*` 所期望的输入；
  - `merge_sampling_params(params)` / `merge_pooling_params(params)` — 合并默认 `SamplingParams` / `PoolingParams`（`merge_pooling_params` 默认 task 为 `"plugin"`）；
  - `pre_process(prompt, request_id, **kwargs)` / `pre_process_async(...)` — 由校验后的输入生成一个或多个 vLLM `PromptType`；
  - `post_process(model_output, request_id, **kwargs)` / `post_process_async(...)` — 由 `PoolingRequestOutput` 序列生成自定义输出。
- **异步输出顺序处理**：`post_process_async` 内部使用 `sorted([(i, item) async for i, item in model_output], key=lambda output: output[0])` 显式按 id 排序后再调用 `post_process`，原文注释明确指出 **"We cannot guarantee outputs are returned in the same order they were fed to vLLM."**
- **加载方式**：插件在引擎启动时加载，两种途径：
  1. 通过 `EngineArgs.io_processor_plugin`（离线 `LLM` / `AsyncLLM` 传入，或在线模式下命令行 `--io-processor-plugin`）；
  2. 通过模型 HF 配置 `config.json` 中的 `io_processor_plugin` 字段。
- **优先级规则**：通过 `EngineArgs` 设置的插件名**覆盖** HF 模型 config.json 中的设置。

---

## 【关键机制与数据】

**工作原理与数据流**（基于原文）：

1. **用户输入 → 校验**：`parse_data(data: object) -> IOProcessorInput`，将任意用户数据转换为插件自有输入类型。
2. **参数合并**：可选地通过 `merge_sampling_params` / `merge_pooling_params` 把用户传入参数与默认参数合并。
3. **预处理 → 模型提示**：`pre_process*` 把校验后的 `IOProcessorInput` 转为一个或多个 `PromptType`（或 `Sequence[PromptType]`），送入模型的 `encode` 方法执行常规推理。
4. **推理输出**：`encode` 返回 `Sequence[PoolingRequestOutput]`。
5. **后处理 → 插件输出**：`post_process*` 把 `PoolingRequestOutput` 序列转换成插件自定义的 `IOProcessorOutput`，对异步流则先按 id 排序再聚合。

**多模态用例**：原文示例场景为"用户向 vLLM 输入一张图像，输出一张图像"，具体实现参考 IBM `terratorch` 仓库中基于 `PrithviGeospatialMAE` 的 segmentation 插件，可生成 geotiff 图像。

**异步排序细节（原文）**：`post_process_async` 使用 async generator `(int, PoolingRequestOutput)` 元组，先 `sorted(... key=lambda output: output[0])` 排序，再 `[output[1] for output in sorted_output]` 收集后传入 `post_process`。

---

## 【表格解读】

**原文无表格。** 文档未包含任何 markdown / 文本表格，接口细节以 Python 类定义与签名方式给出。

---

## 【公式解读】

**原文无公式。** 文档不包含 LaTeX 或伪代码形式的公式；所有计算逻辑均以方法签名与代码片段呈现。

---

## 【关联】

- **与 Pooling 模型的耦合**：IO Processor 插件仅服务于 pooling 模型，依赖 `PoolingParams`、`PoolingRequestOutput`、`PromptType` 等 pooling 路径下的核心数据结构。
- **调用入口**：
  - 离线模式：`LLM.encode` / `AsyncLLM.encode`；
  - 在线服务模式：`/pooling` endpoint。
- **插件接口定义**：抽象类 `IOProcessor` 定义于 `vllm.plugins.io_processors.interface` 模块，构造时接受 `VllmConfig` 与 `BaseRenderer`（renderer 仅在 `__init__` 中可见，未在方法列表中使用）。
- **依赖的 vLLm 数据结构**：`SamplingParams`、`PoolingParams`（默认 `task="plugin"`）、`PromptType`、`PoolingRequestOutput`、`VllmConfig`。
- **示例代码（文末内部链接）**：
  - 在线推理示例：[`examples/pooling/plugin/prithvi_geospatial_mae_online.py`](../../examples/pooling/plugin/prithvi_geospatial_mae_online.py)
  - 离线推理示例：[`examples/pooling/plugin/prithvi_geospatial_mae_io_processor.py`](../../examples/pooling/plugin/prithvi_geospatial_mae_io_processor.py)
- **外部参考实现**：IBM 的 [`terratorch`](https://github.com/IBM/terratorch/tree/main/terratorch/vllm/plugins/segmentation) 中提供了基于 `PrithviGeospatialMAE` 的可生成 geotiff 图像的实际插件示例。

---

## 【使用方法】

**加载/启用方式（原文给出）**：

1. **通过 `EngineArgs`**：
   - 离线模式：`AsyncLLM` 初始化时设置 `EngineArgs.io_processor_plugin`；
   - 离线模式：`LLM` 初始化时传入 `io_processor_plugin` 参数；
   - 在线模式：命令行参数 `--io-processor-plugin`。
2. **通过模型 HF 配置**：在模型的 `config.json` 中添加 `io_processor_plugin` 字段。
3. **优先级**：`EngineArgs` 中的设置覆盖 HF config.json 中的同名设置（"setting the plugin name via `EngineArgs` will override any plugin name specified in the model HF config"）。

**插件实现要点**：需继承 `IOProcessor` 抽象类并实现 `pre_process` 与 `post_process`（`pre_process_async` 与 `post_process_async` 可选实现），同步版本会自动作为异步版本的默认实现；异步 `post_process_async` 会自动按 id 排序后调用同步 `post_process`，插件作者无需自行处理乱序问题。
