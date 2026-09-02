# zero_evict_scheduler

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/zero_evict_scheduler.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/zero_evict_scheduler.md

## 【定位】

这篇文档介绍 xLLM 的 **Zero Evict Scheduler（零驱逐调度策略）**：通过模拟调度判断新增请求是否会驱逐其他请求，尽量降低请求驱逐率、避免对被驱逐请求重新执行 Prefill，从而改善端到端约束下的 TPOT 延迟。

## 【技术要点】

1. **核心目标是降低请求驱逐率**  
   Zero Evict 并非要求绝对不发生驱逐，而是通过调度检测，尽量减少请求被提前移出的情况。

2. **使用模拟轮次验证可调度性**  
   调度算法会执行模拟调度，检查待调度请求加入后是否会导致其他请求被驱逐，即验证该请求能否在不驱逐现有请求的条件下完成调度。

3. **避免被驱逐请求的重复 Prefill**  
   请求一旦被驱逐，再次服务时可能需要重新进行 Prefill 计算。降低驱逐率可以减少这部分额外计算。

4. **主要收益是改善 TPOT**  
   TPOT 即 **Time Per Output Token（每个输出 Token 的时间）**。原文给出的结果是：启用 Zero Evict 后，在 E2E 延迟约束下，TPOT 延迟降低。

5. **通过 gflags 控制**  
   启用策略和设置单序列最大解码 Token 数分别使用：
   ```text
   --use_zero_evict=true
   --max_decode_token_per_sequence=256
   ```
   其中 `256` 表示每个序列允许的最大解码 Token 数；原文未将其描述为并发数或序列数量。

6. **原文性能结果**  
   在 **Qwen3-8B** 模型和 **E2E latency constraint** 测试条件下，TPOT latency **降低 27%**。

## 【关键机制与数据】

**原文：** 调度算法采用 simulation rounds，判断一个请求是否能够在不驱逐其他请求的情况下被调度。

其工作逻辑可按原文整理为：

1. 调度器面对待处理请求时，不立即按普通方式直接占用资源。
2. 通过模拟轮次评估加入该请求对现有请求集合的影响。
3. 判定该请求加入后是否会造成其他请求被驱逐。
4. 只有不会导致其他请求被驱逐的调度结果，才符合 Zero Evict 策略的目标。
5. 通过减少请求驱逐，避免被驱逐请求再次进入服务流程时重新执行 Prefill。
6. 最终收益体现在 TPOT 延迟下降。

**原文：** 在 Qwen3-8B 模型上，启用 Zero Evict 并设置 E2E 延迟约束后，TPOT latency 相比原状态 **decreased by 27%**。

这里的“降低 27%”是原文所述的相对性能变化，原文没有提供：

- 绝对 TPOT 数值；
- 原始 TPOT 与启用后 TPOT；
- 吞吐量、首 Token 延迟或 Prefill 时长数据；
- 测试硬件、批大小、输入输出长度和并发规模；
- simulation rounds 的轮次数量与具体判定细节。

因此，该结果只能说明原文测试条件下 TPOT 相对下降 27%，不能进一步换算为其他性能指标。

## 【表格解读】

原文无表格。

文档中的参数与性能数据均以正文、项目符号和命令形式出现，没有提供参数对照表、配置矩阵或性能对比表。

## 【公式解读】

原文无公式。

文档未给出驱逐率、TPOT、资源容量或模拟判定逻辑的数学表达式。

相关指标只在正文中以文字描述：

- **Eviction rate**：请求被驱逐的比例，Zero Evict 策略试图将其最小化。
- **TPOT**：Time Per Output Token，即每个输出 Token 的生成时间。
- **E2E latency constraint**：端到端延迟约束；原文没有给出其具体阈值。
- **27%**：原文报告的 TPOT latency 相对降幅，而不是 27 个时间单位或 27 个百分点。

## 【关联】

1. **与请求调度的关系**  
   Zero Evict 是 xLLM 请求调度策略的一部分。它不是独立的推理计算模块，而是在调度请求时评估是否会对其他请求造成驱逐。

2. **与 Prefill 的关系**  
   文档给出的直接收益链是：

   `降低请求驱逐率`  
   → `减少被驱逐请求的 Prefill 重复计算`  
   → `改善 TPOT`。

3. **与 gflags 配置系统的关系**  
   该能力通过 xLLM 的 gflags 参数暴露：
   - `--use_zero_evict` 控制策略开关；
   - `--max_decode_token_per_sequence` 控制单序列最大解码 Token 数。

4. **与推理阶段的关系**  
   文档明确关联了 Prefill 和 Decode：
   - 被驱逐请求可能需要重新进行 Prefill；
   - `--max_decode_token_per_sequence=256` 直接涉及单序列的 Decode Token 上限。

5. **与 E2E 延迟约束的关系**  
   性能结果是在 E2E 延迟约束下测得，说明该策略在满足端到端延迟目标时改善了 TPOT；但原文没有说明调度器如何与约束联动。

6. **上下游模块与链接**  
   文末没有提供内部链接，原文也未点名更多上游队列、缓存、KV Cache 管理器、请求队列或硬件后端等模块。因此，只能确认该策略位于 xLLM 的调度层，并通过 gflags 对外开放，不能进一步确定它与这些未提及组件的直接接口关系。

## 【使用方法】

启用 Zero Evict 策略，并设置每个序列的最大解码 Token 数：

```bash
--use_zero_evict=true
--max_decode_token_per_sequence=256
```

参数含义：

| 参数 | 原文含义 |
|---|---|
| `--use_zero_evict=true` | 启用 zero evict scheduling strategy |
| `--max_decode_token_per_sequence=256` | 将每个序列的最大 decode tokens 设置为 256 |

原文未涉及：

- 是否需要重启 xLLM；
- 配置文件中的完整写法；
- 其他调度策略参数；
- 动态修改 gflags 的方式；
- 策略的默认值；
- E2E 延迟约束的具体配置命令；
- 指标采集或回归测试命令。
