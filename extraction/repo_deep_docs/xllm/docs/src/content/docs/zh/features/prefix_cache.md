# prefix_cache

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/prefix_cache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/prefix_cache.md

# 「Prefix Cache 优化」文档深度解读

## 【定位】
本文档描述 xLLM 的 **Prefix Cache（前缀缓存）优化能力** —— 通过基于 mermer_hash 的匹配机制、LRU 淘汰策略以及多种调度器协同，在 prefill 后即时更新缓存并提升命中率，从而降低推理时延与 KV cache 占用。

## 【技术要点】
1. **匹配机制**：prefix_cache 基于 **mermer_hash**（minhash/近似 hash）实现前缀匹配，相比精确匹配提供更极致的匹配效率。
2. **淘汰策略**：采用 **LRU**（Least Recently Used）淘汰策略，维持缓存空间可控。
3. **多调度器兼容**：同时支持 **continuous_scheduler、chunked_scheduler、zero_evict_scheduler** 三种调度器。
4. **即时更新**：在 prefill 完成后即更新 prefix_cache，提升匹配时效性。
5. **多阶段 chunked_prefill 匹配**：针对 chunked_scheduler，支持多阶段 chunked_prefill 匹配，目的为减少计算量并尽可能减少 kv_cache 占用。
6. **Cache 感知 DP 路由**：当 `dp_size > 1` 时，请求可被路由到持有最长 prefix cache 命中的 DP rank，提高跨 rank 的 KV cache 复用率。
7. **gflag 暴露**：prefix_cache 通过 gflag 参数控制开关，无需修改代码即可启用。

## 【关键机制与数据】

### 工作原理
- **匹配流程**：prefix_cache 基于 mermer_hash 计算前缀指纹 → 在缓存中查找最长匹配前缀 → 命中后复用其 KV cache，跳过对应 token 的 prefill 计算。
- **缓存更新时机**：在 prefill 阶段完成后立即更新 prefix_cache，而非延迟到请求结束，从而尽早使新计算结果可被后续请求命中。
- **chunked_scheduler 优化**：通过多阶段 chunked_prefill 匹配，将一个长 prefill 拆分为多个 chunk 分阶段匹配，使得早完成的 chunk 可以立即更新缓存并被复用。
- **zero_evict 协同**：与 zero_evict_scheduler 协同开启可避免预分配策略对缓存的过早驱逐。
- **DP 路由机制**：在数据并行场景下，根据各 rank 已有 prefix block 的命中比例与 KV 利用率均衡度，动态决定请求路由目标。

### 性能数据
- **原文：** 在 Qwen3-8B 模型上，限制 TPOT=50ms，开启 prefix_cache 后 **E2E 时延下降 10%**。
- **原文：** 默认参数：
  - `prefix_cache_aware_dp_match_threshold` 默认值 **0.5**
  - `prefix_cache_aware_dp_imbalance_threshold` 默认值 **0.1**

## 【表格解读】
**原文无表格**。文档中的配置参数以列表/代码块形式呈现，未包含表格结构，故不做逐字还原。

## 【公式解读】
**原文无公式**。文档中涉及阈值判断的概念性描述（如"低于该阈值时回退到空闲 block 均衡"），但未给出任何 LaTeX 公式或伪代码表达式，故不做公式还原。

## 【关联】
本文档与 **PD 分离（Prefill-Decode Disaggregation）** 特性存在直接关联：
- 文档末尾以 `:::note` 提示：**PD 分离下的 prefix cache 支持范围与调度器角色相关**，需参见 [PD 分离](/zh/features/disagg_pd/) 中的支持配置说明。
- 这表明 prefix cache 在 PD 分离架构下的行为可能受调度器（prefill scheduler / decode scheduler）角色差异影响，存在兼容性边界，读者需结合 PD 分离文档共同理解完整能力范围。

## 【使用方法】

### 基础启用
通过 gflag 参数开启 prefix_cache：
```
--enable_prefix_cache=true
```
若需使用 zero_evict 策略并设置 `max_decode_token_per_sequence`，同样通过此 flag 控制。

### Cache 感知 DP 路由启用
当数据并行规模 `dp_size > 1` 时，可启用 cache 感知路由：
```
--enable_prefix_cache=true --enable_prefix_cache_aware_dp_routing=true
```

### 关键配置项说明
- **`prefix_cache_aware_dp_match_threshold`**（默认 `0.5`）：选择 cache 亲和 rank 所需的最低 prefix block 命中比例，低于该阈值时回退到空闲 block 均衡策略。
- **`prefix_cache_aware_dp_imbalance_threshold`**（默认 `0.1`）：跨 rank KV 利用率差异上限，计算方式为 `(max_used - min_used) / total_blocks`；超过此值时路由到负载最低的 rank。

### PD 分离场景
**原文未涉及**具体开启命令；仅提示需参考 [PD 分离](/zh/features/disagg_pd/) 文档中的支持配置说明来确定 prefix cache 在 PD 角色下的启用方式。
