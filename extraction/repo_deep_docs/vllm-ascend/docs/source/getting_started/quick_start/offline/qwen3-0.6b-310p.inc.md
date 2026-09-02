# qwen3-0.6b-310p.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/offline/qwen3-0.6b-310p.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/offline/qwen3-0.6b-310p.inc.md

【定位】
这篇文档描述在 Atlas 300I DUO 和 Atlas 200I Pro 硬件路径上离线运行 Qwen3-0.6B 模型的标准示例及针对 Ascend NPU 的运行时约束,作为该硬件路径下的快速入门模板。

【技术要点】
- 硬件验证范围: Qwen3-0.6B 示例已在 Atlas 300I DUO 和 Atlas 200I Pro 上验证通过。
- 精度要求: 强制使用 `float16`。
- 计算图模式: 须使用 `FULL_DECODE_ONLY`,并限制 graph capture 大小,捕获尺寸列表为 `[1, 2, 4, 8]`。
- 不支持项: `enable_npugraph_ex` 在该硬件路径上不支持,需通过 `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex":false}}'` 显式关闭。
- 并发上限: `max_num_seqs=8`,与 `cudagraph_capture_sizes` 的最大值一致。
- 推理参数: `temperature=0.0`, `max_tokens=32`,即采用贪心解码生成最多 32 个 token。
- 离线入口: `python3 example.py` 直接调用 `LLM.generate()`,并通过断言验证输出长度与非空。

【关键机制与数据】
- 工作原理: 文档展示 vLLM 通过 platform plugin 机制自动检测 Ascend 平台。原文日志: `Platform plugin ascend is activated`,由 `vllm_ascend:register` 注入。
- 数据流: 两个 prompt `["Hello, my name is", "The future of AI is"]` 进入 `LLM.generate`,使用 `LLM` 实例内部配置的编译与额外 Ascend 配置;`SamplingParams` 控制采样与生成长度。
- 性能/捕获尺寸(原文): `cudagraph_capture_sizes=[1, 2, 4, 8]` 表示 NPUGraph 仅捕获批大小为 1、2、4、8 的 decode 阶段,其他尺寸走非 graph 路径。`max_num_seqs=8` 与该列表上限对齐。
- 生成结果(原文示例输出):
  - Prompt `'Hello, my name is'` → Generated text `' Lucy and I am an 8 year old who loves to draw and write stories'`
  - Prompt `'The future of AI is'` → Generated text `' a topic that is being discussed in various contexts. In the business world, AI'`
- 退出过程(原文标注): `Shutdown initiated (timeout=0)` → `Shutdown complete` → `Engine core proc EngineCore died unexpectedly, shutting down client.`,文档明确说明这些消息不影响推理结果。

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】
- 内部链接: 原文未提供内部链接(无 `.md` 引用或锚点)。
- 模块关联(基于原文命名): 文档涉及的配置项 `ascend_compilation_config` 与 `enable_npugraph_ex` 属于 vllm-ascend 编译配置层;`cudagraph_mode` / `cudagraph_capture_sizes` 属于 vLLM 上层 `compilation_config`,通过 Ascend plugin 转化为 NPUGraph 后端;`vllm.platform_plugins` 体系负责 ascend plugin 的注册与激活。

【使用方法】
- 启动容器后,在容器终端创建 `example.py`,复制原文 Python 代码。
- 通过命令行运行: `python3 example.py`。
- 关键配置项(原文):
  - `LLM(model="Qwen/Qwen3-0.6B", dtype="float16", max_num_seqs=8)`
  - `compilation_config={"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes": [1, 2, 4, 8]}`
  - `additional_config={"ascend_compilation_config": {"enable_npugraph_ex": False}}`
  - `SamplingParams(temperature=0.0, max_tokens=32)`
- 等效的额外命令行方式(原文): `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex":false}}'`,用于禁用 `enable_npugraph_ex`。
- 预期日志(原文): `Available plugins for group vllm.platform_plugins` → `- ascend -> vllm_ascend:register` → `Platform plugin ascend is activated`。
