# Chunked Prefill

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/chunked_prefill.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/chunked_prefill.md

# Chunked Prefill 文档深度解读

## 【定位】

这篇文档描述 Chunked Prefill（Splitfuse）特性——通过将长 prompt 拆分为小块并与 decode 请求混合组批，解决推理服务中 prefill 与 decode 计算负载不均导致的延迟波动与 prefill 阶段 OOM 问题。

---

## 【技术要点】

1. **长 prompt 分块调度**：长 prompt 被分解成更小的 chunk，在多个 forward step（多次迭代）中调度，**只有最后一块 chunk 的 forward 完成后才开始该请求的 token 生成**，前序 chunk 仅做 prefill 计算不产出 token。
2. **混合组批（prefill + decode 填充）**：构建 batch 时，一个 prefill chunk 占一席，其余槽位用 decode 请求填充，**降低纯 decode 组 batch 的成本**。
3. **每步计算量均衡**：将短 prompt request 组合以精确填充 step 空隙，使**每个 step 的计算量基本相等**，进而使所有请求的平均延迟更稳定。
4. **参数约束（vLLM 脚本）**：`max-num-batched-tokens ≥ max-model-len`，且需 **大于 256 并能被 256 整除**；建议值 **4096、8192 或更大**。
5. **启用开关**：脚本中添加 `enable_chunked_prefill: True`。
6. **互斥与兼容性约束**：不能与 **Prefix Cache（APC）**、**KV Cache 量化** 特性同时使用；**Qwen 系列模型**支持此特性。

---

## 【关键机制与数据】

**工作原理（原文叙述整合）：**

- **调度阶段**：长 prompt → 拆分为 chunk → 分多个 forward step 调度 → 最后一块 chunk 完成 forward → 进入生成阶段。
- **组批阶段**：每个 step 的 batch 由「1 个 prefill chunk + 多个 decode 槽位」构成，目的是填充 step 空隙、平衡计算量。
- **效果链路（原文）：**「平衡 prefill 和 decode 的计算利用率 → 降低请求 P90_ttft（time to first token）、P90_tpot（time per output token）时延 → 在短输入、短输出且高并发的场景优势明显 → 可用于解决 prefill 阶段单 batch 过大导致的 OOM」。

**性能数据：** 原文未给出具体吞吐量数字、加速比、benchmark 结果等量化性能数据，仅描述**定性优势**（提升效率 / 增强一致性 / 降低时延减小 OOM）以及**两个延迟指标名称** `P90_ttft`、`P90_tpot`。

---

## 【表格解读】

**原文无表格。** 文档未包含参数表、性能对比表或配置项表，仅以散文形式列出 `max-model-len`、`max-num-batched-tokens` 两个参数及其约束关系。

---

## 【公式解读】

**原文无公式。** 文档未给出任何数学公式或伪代码形式，仅以自然语言描述分块调度与混合组批机制。

---

## 【关联】

文档内部无 `内部链接` 字段（标注为「无」），但文中通过功能约束与开关交互隐含了以下模块/特性关联：

| 关联对象 | 关系性质 | 原文表述 |
|---|---|---|
| **Prefix Cache (APC)** | 互斥 | "该特性不能和 … Prefix Cache(APC) … 同时使用" |
| **KV Cache 量化** | 互斥 | "不能和 … KV Cache 量化特性同时使用" |
| **vLLM v1 scheduler** | 默认行为 | "vLLM v1 scheduler 默认开启" Chunked Prefill |
| **ascend_scheduler_config** | 反向默认 | "开启 ascend_scheduler_config 后，默认关闭" Chunked Prefill |
| **Qwen 系列模型** | 兼容性范围 | "Qwen 系列模型支持此特性" |
| **vLLM 推理脚本** | 部署载体 | 使用方法章节的 `max-model-len` / `max-num-batched-tokens` / `enable_chunked_prefill` 均作用于 vLLM 脚本 |

总体定位：Chunked Prefill 是 vLLM 推理侧（部署/服务阶段）的调度优化特性，向上服务于推理服务 SLA（稳定 P90_ttft / P90_tpot），向下与 KV Cache / Prefix Cache 等缓存特性存在排他约束。

---

## 【使用方法】

**启用方式（原文）：**

1. **配置参数**（vLLM 脚本）：
   - `max-model-len`：单个请求的最大处理长度。
   - `max-num-batched-tokens`：单个推理批次中所有请求的最大 tokens 数。
   - 约束条件：**`max-num-batched-tokens ≥ max-model-len`**；且 `max-num-batched-tokens` **大于 256 并能被 256 整除**。
   - 建议取值：**4096、8192 或更大**。

2. **开启开关**（脚本中添加配置）：
   ```yaml
   enable_chunked_prefill: True
   ```

3. **默认值差异**：
   - 在 **vLLM v1 scheduler** 下：Chunked Prefill **默认开启**。
   - 开启 **`ascend_scheduler_config`** 后：Chunked Prefill **默认关闭**。

**注意事项（原文）：**
- 不能与 **Prefix Cache（APC）**、**KV Cache 量化** 同时使用。
- 仅 **Qwen 系列模型**支持此特性。
