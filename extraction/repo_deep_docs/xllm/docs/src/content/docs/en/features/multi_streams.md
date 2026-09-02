# multi_streams

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/multi_streams.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/multi_streams.md

# 一体化深度解读:xLLM Multi-stream Parallel

---

## 【定位】

这篇文档描述 xLLM 在**分布式大模型推理**场景下,针对 prefill 阶段通过**双流并行(multi-stream parallelism)** 将同一 batch 拆分为 micro-batch,以「计算流」与「通信流」重叠执行,从而**掩盖跨设备通信开销**、提升 TTFT 与吞吐的能力。

---

## 【技术要点】

1. **问题根源**:大模型(尤其是 MoE, 如 Deepseek)分布式推理中,通信开销显著;若计算与通信在同一 stream 上串行执行,设备在等待通信完成时空闲,造成算力浪费。
2. **核心机制**:在模型层将输入 batch **拆分为 2 个 micro-batch**,分配到不同 stream 上——一个 stream 执行第一个 micro-batch 的计算,另一个 stream 同时执行第二个 micro-batch 的通信,实现计算-通信 overlap。
3. **启用开关**:xLLM 提供 gflags 参数 `enable_multi_stream_parallel`,**默认 `false`**;在服务启动脚本中设为 `true` 即可开启,示例命令 `--enable_multi_stream_parallel=true`。
4. **收益数据**:开启 prefill 双流并行后,可**掩盖 75% 以上的通信开销**;在 DeepSeek-R1 模型生成 1 token 的场景下,实现 **TTFT 降低 7%**、**吞吐提升 7%**。
5. **作用范围限制**:**仅支持 prefill 阶段**,对长输入请求收益更明显;**仅支持 DeepSeek 与 Qwen3 dense(非 MoE)模型**。
6. **隐含前提**:依赖底层设备的 stream 并发能力(文中未明示硬件类型,如 CUDA stream 等)。

---

## 【关键机制与数据】

### 工作原理(原文还原)

1. **触发条件**:进入 prefill 阶段、batch 内含分布式通信需求(典型为 MoE expert all-to-all 或 attention 聚合)。
2. **拆分动作**:**「the input batch is split into 2 micro-batches」**——原文明确数字为 2。
3. **并发编排**:
   - Stream A → 计算 micro-batch 1;
   - Stream B → 通信(micro-batch 1 计算结果聚合 / micro-batch 2 的预备通信);
   - 下一轮切换:Stream A 计算 micro-batch 2、Stream B 执行相关通信。
4. **收益来源**:计算 kernel 与通信 kernel 在不同 stream 上**时间维度的重叠**,使原本因通信而空闲的计算资源恢复占用。

### 性能数据(原文逐字保留)

| 指标 | 数值 | 适用条件 |
|---|---|---|
| 通信开销掩盖率 | **>75%** | prefill 双流并行开启 |
| TTFT 降低 | **7%** | DeepSeek-R1,生成 1 token |
| 吞吐提升 | **7%** | DeepSeek-R1,生成 1 token |

> 注:文中未给出绝对延迟(ms)、QPS、batch size、序列长度等基准参数,亦未提供 Qwen3 dense 下的实测数据,以上解读仅基于原文。

---

## 【表格解读】

**原文无表格。** 文档采用「要点列表 + 一张架构示意图(`figures/multi_streams_architecture.jpg`)」承载信息,未使用 markdown/HTML 表格。

---

## 【公式解读】

**原文无公式。** 文档未给出任何数学表达式或伪代码公式;「通信开销掩盖率」「TTFT/吞吐 7%」均以定性文字与百分比呈现,未展开为可推导公式。

---

## 【关联】

原文未提供内部链接(`内部链接: (无)`)。可由文本内容推断的上下文关联如下:

- **上游/触发方**:**分布式推理框架**——文档开篇即指出「distributed inference scenarios for large-scale models」,并以 **Deepseek(MoE)** 为典型场景,说明该特性服务于 xLLM 的多设备/多卡推理路径。
- **下游/受益方**:
  - **DeepSeek-R1 模型**——性能数据明确在该模型上取得 7%/7% 收益。
  - **Qwen3 dense(非 MoE)模型**——在 Notice 中被列入支持范围,但未给出独立性能数据。
- **作用阶段限定**:与 xLLM 推理生命周期的 **prefill 阶段** 绑定;**decode 阶段未涉及**,文档明确「currently only supports the prefill phase」。
- **互补机制**:本质是「计算-通信 overlap」思路,与业界常见的 CUDA stream / NCCL 双流模式同源,但被封装在 `enable_multi_stream_parallel` 这一统一开关下。

---

## 【使用方法】

1. **启动参数**:
   ```shell
   --enable_multi_stream_parallel=true
   ```
2. **默认值**:`false`(即默认关闭,需手动开启)。
3. **配置位置**:**xLLM 的服务启动脚本**(原文表述「set it to true in xLLM's service startup script」)。
4. **支持模型**:**DeepSeek、Qwen3 dense(非 MoE)**;其他模型未在文档中列出,是否生效需以官方发布为准。
5. **生效阶段**:**仅 prefill 阶段**;输入请求越长,收益越大(原文未给阈值/上限)。

## 图文联合解读

- `multi_streams_architecture.jpg`: 1) 图中双流并行：stream 0 交替执行 batch 0/1 的 Attn 与 MoE 计算，stream 1 同步执行另一 batch 的 Dispatch/Combine 通信；虚线框标注"full utilization"，箭头表示两流间批次交接。

2) 计算与通信在两个 micro-batch 上交错执行，设备计算资源无需空等通信，实现满载利用。

3) 图示直观佐证"双流并行隐藏通信延迟"的论点，为文档给出的"掩蔽 75%+ 通信开销、DeepSeek-R1 推理 7% 加速"提供机制层面的可视化解释。
