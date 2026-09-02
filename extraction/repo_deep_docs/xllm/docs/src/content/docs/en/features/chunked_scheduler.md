# chunked_scheduler

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/chunked_scheduler.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/chunked_scheduler.md

# 一体化深度解读：ChunkedPrefill Scheduler

## 【定位】
这篇文档描述 xLLM 的 **chunked prefill（分块预填充）调度策略**——一种通过将长 prompt 拆分成小块进行批量处理，从而在大语言模型推理场景中降低峰值显存占用、提升设备利用率、并与 decode 阶段请求更顺畅混合调度的能力。

---

## 【技术要点】

1. **核心思想——"拆分长 prompt 为小块进行 batch 处理"**：chunked prefill 不再一次性处理整条 prompt，而是将长 prompt 切成较小的 chunk 进入批处理流水线（原文："splitting long prompts into smaller chunks for batch processing, rather than processing the entire prompt at once"）。
2. **三大收益**（原文逐字）：① "effectively reduce peak GPU memory usage" ② "improve device utilization" ③ "better schedule and mix processing with requests from the decode stage"。
3. **实现位置与状态**：该策略 "has been implemented in xLLM"（已完成落地，非规划/草案）。
4. **配置通道**：通过 **gflags** 参数对功能开关进行控制（"exposed through gflags parameters to control the feature's on/off state"）。
5. **功能开关**：`--enable_chunked_prefill=true`（强制启用）。
6. **chunk 大小配置**：`--max_tokens_per_chunk_for_prefill=20480`（可选；若不显式设置，**默认值等于 `max_tokens_per_batch`**）。

---

## 【关键机制与数据】

**工作原理（原文提炼）**：
- 输入侧：原本一次性送入的完整 prompt，被切分为若干个 token 级 chunk；
- 调度侧：这些 chunk 以"小批次"形式进入推理管线，与 decode 阶段的请求在同一调度器中混合调度（"mix processing with requests from the decode stage"）；
- 资源侧：每次进入 GPU 的 token 总量被约束在 `max_tokens_per_chunk_for_prefill` 之内，从而抑制单次 prefill 造成的显存尖峰，并释放出空隙给 decode 请求并发推进；
- chunk 大小缺省值回退：未设置时默认为 `max_tokens_per_batch`（即沿用整批 token 上限作为 chunk 上限）。

**性能数据（原文逐字）**：
> 原文："After enabling chunked prefill, on the Qwen3-8B model with a TPOT constraint of 50ms, the TTFT latency **decreased by 46%**."
- 测试模型：**Qwen3-8B**
- TPOT（per-output-token latency）约束：**50ms**
- 指标：**TTFT（Time To First Token）**
- 改善幅度：**↓ 46%**（启用 chunked prefill 后的 TTFT 较启用前下降 46%）

---

## 【表格解读】

**原文无表格。**

文档全文为叙述 + 一段 bash 命令示例 + 一句性能结论，未包含任何对比表、参数表或配置矩阵。

---

## 【公式解读】

**原文无公式。**

文档未给出 LaTeX 表达式、伪代码公式或任何形式化的数学定义（如 chunk 切分公式、TTFT/TPOT 定义公式等）。

---

## 【关联】

**原文无内部链接，亦未显式点名任何上下游模块。**

文档仅在功能介绍中提及与 **decode 阶段（decode stage）请求的混合调度**这一隐式关联——即 chunked prefill 的调度对象与 decode 请求共用同一调度器，但未给出指向具体模块/文件的内部链接。文末"内部链接"字段亦标注为"（无）"，因此本节无可展开的交叉引用内容。

---

## 【使用方法】

启用方式（**原文命令逐字保留**）：

```bash
--enable_chunked_prefill=true
--max_tokens_per_chunk_for_prefill=20480 # optional
```

- 必选项：`--enable_chunked_prefill=true` —— 打开 chunked prefill 调度策略。
- 可选项：`--max_tokens_per_chunk_for_prefill=20480` —— 设置每个 prefill chunk 的 token 上限；注释 `# optional` 表明此参数非必填。
- **缺省行为**：若未显式设置 chunk 大小，"its default value is equal to `max_tokens_per_batch`"（即默认回退到每批 token 上限的值）。

原文未涉及诸如 API 调用方式、环境变量、yaml/JSON 配置模板或与其他 flags 的协同约束等内容。
