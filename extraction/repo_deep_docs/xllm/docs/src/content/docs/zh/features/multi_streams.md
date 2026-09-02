# multi_streams

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/multi_streams.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/multi_streams.md

# 「多流并行」feature 文档深度解读

---

## 【定位】

本文档介绍 xLLM 在模型图层引入的多流并行（multi-stream parallel）能力：通过将单个 batch 切分为两个 micro batch，让计算与通信分别在不同 stream 上并发执行，从而在分布式大模型推理（尤其是大规模 MoE）的 prefill 阶段掩盖通信开销、降低 TTFT 并提升吞吐。

---

## 【技术要点】

1. **问题域**：大规模 MoE（如 DeepSeek 类）分布式推理中，跨设备结果聚合产生显著通信开销；若计算与通信共用同一 stream，device 计算资源会在等待通信完成时空转。
2. **核心做法**：在模型图层支持多流并行，将输入 batch 拆分为 **2 个 micro batch**——一个流负责其中一个 micro batch 的计算，另一个流负责另一个 micro batch 的通信，二者并行执行以"掩盖"通信开销。
3. **启用开关**：提供 gflags 参数 **`enable_multi_stream_parallel`**，默认 **false**；开启时在服务启动脚本中设为 `--enable_multi_stream_parallel=true`。
4. **作用阶段**：原文以 **caution** 形式注明——双流并行目前 **仅支持 prefill 阶段**。
5. **适用模型**：目前仅支持 **DeepSeek** 与 **Qwen3 dense（非 MoE）** 模型。
6. **收益规律**：请求输入越长，收益越大（原文"请求输入越长，收益越大"）。

---

## 【关键机制与数据】

### 工作原理（基于原文叙述）

- **背景驱动**（原文）：大模型分布式推理需要在设备间聚合计算结果；以 DeepSeek 类大规模 MoE 为例，分布式规模大、通信开销大；若计算与通信共用同一 stream，device 计算资源会"一直等待通信完成才能开始后面的计算"。
- **并行化策略**（原文）：xLLM 在"模型图层"引入多流并行，把输入 batch 拆成 2 个 micro batch，"一个流执行一个 micro batch 的计算操作，另一个流执行另一个 micro batch 的通信操作，计算和通信同时执行，从而掩盖通信开销"。
- **架构图引用**：原文嵌入 `figures/multi_streams_architecture.jpg` 作为「异步调度」示意图，用以直观展示双流的执行时序。

### 性能数据（原文给出的唯一量化结论）

- **可掩盖的通信开销**（原文）：prefill 双流并行开启后，**基本可掩盖 75 以上的通信开销**（按原文措辞保留，结合上下文应理解为 "75% 以上"）。
- **DeepSeek-R1 模型、只输出 1 个 token 场景下**（原文）：
  - **TTFT 下降 7%**
  - **吞吐提升 7%**

> 说明：原文 performance 部分仅给出上述两个百分比指标，并未提供绝对时延（如 ms）、吞吐（tokens/s）或不同 batch/输入长度下的对比曲线；故解读中不引入额外数字。

---

## 【表格解读】

**原文无表格**。

本节附注：原文以 caution 提示框形式罗列了三项限定条件（非表格结构），为保留信息完整性转写如下：

| 限定条件（原文 caution） | 内容 |
|---|---|
| 支持阶段 | 仅 prefill 阶段 |
| 收益与输入长度的关系 | 请求输入越长，收益越大 |
| 支持的模型范围 | 仅支持 DeepSeek、Qwen3 dense（非 MoE）模型 |

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档未提供内部链接（"内部链接: (无)"）。基于原文语义可识别的关联项如下，均来自文档自身表述：

- **作用对象**：DeepSeek、Qwen3 dense（非 MoE）模型——与文档列出的"适用模型范围"一致。
- **优化目标**：分布式推理通信开销——呼应「背景」中提到的 Deepseek 类大规模 MoE 分布式场景。
- **执行阶段**：prefill（与 decode 阶段的对应行为原文未涉及）。
- **运行配置**：与 gflags 启动参数 `enable_multi_stream_parallel` 绑定，作用于 xLLM 服务启动脚本（具体脚本路径/启动入口原文未给出）。

---

## 【使用方法】

- **启用方式**：在 xLLM 服务启动脚本中，将 gflags 参数 `enable_multi_stream_parallel` 设为 `true`。
- **示例命令**（原文给出）：
  ```shell
  --enable_multi_stream_parallel=true
  ```
- **默认值**：原文标注为 **false**（即默认关闭）。
- **生效范围与限制**（原文 caution）：
  - 仅 prefill 阶段生效；
  - 仅支持 DeepSeek、Qwen3 dense（非 MoE）模型；
  - 输入越长收益越大。
- **其他配置项/命令行开关**：原文未涉及更多 gflags、环境变量或配置文件路径。

## 图文联合解读

- `multi_streams_architecture.jpg`: **图示解读：**

1) **结构**：两条并行流，纵向时间对齐。stream 0 串行执行 Attn/MoE 计算，stream 1 串行执行 Dispatch/Combine 通信；紫/橙块分别代表 batch 0 与 batch 1。对角箭头表示 stream 0 的 MoE 计算依赖 stream 1 前置的 Dispatch 通信结果。

2) **技术结论**：计算与通信被分配到不同流，且按 batch 错开——stream 0 算 batch 1 时，stream 1 同时做 batch 0 的通信，形成"full utilization"重叠区，使设备始终有活可干。

3) **与文档关系**：直接论证"拆 batch 为两个 micro batch、双流分别跑计算和通信以掩盖通信开销"的设计，对应性能收益（TTFT↓7%、吞吐↑7%）。
