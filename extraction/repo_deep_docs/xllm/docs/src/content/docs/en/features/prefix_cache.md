# prefix_cache

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/prefix_cache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/prefix_cache.md

# xLLM Prefix Cache Optimization 文档深度解读

## 【定位】

本文档系统描述 xLLM 推理引擎中**前缀缓存（Prefix Cache）优化**能力,涵盖其哈希匹配机制、调度器集成、Cache-Aware DP 路由策略以及端到端性能收益,解决在多轮对话/长上下文场景下 KV cache 复用率低、prefill 计算冗余大的问题。

---

## 【技术要点】

1. **哈希匹配机制**: 基于 `murmur_hash` 实现前缀缓存,采用 **LRU 淘汰策略**,以提升匹配效率与命中率。
2. **多调度器兼容**: 已对 `continuous_scheduler`、`chunked_scheduler`、`zero_evict_scheduler` 三类调度器完成优化,缓存**在 prefill 操作完成后立即更新**,保证匹配时效性。
3. **分块匹配优化**: 针对 `chunked_scheduler` 支持**多阶段分块 prefill 匹配**,降低计算开销并尽量减少 KV cache 占用。
4. **Cache-Aware DP 路由**: 当 `dp_size > 1`(数据并行)时,请求被路由到持有**最长前缀缓存命中**的 DP rank,以提升跨 rank 的 KV cache 复用。
5. **双阈值路由门控**:
   - `prefix_cache_aware_dp_match_threshold` (默认 `0.5`): 前缀 block 命中率下限,低于该值则回退到 free-block 均衡路由。
   - `prefix_cache_aware_dp_imbalance_threshold` (默认 `0.1`): 跨 rank KV 利用率差距上限,超出则关闭 affinity 路由,选择负载最低的 rank。
6. **性能收益**: 在 Qwen3-8B 模型、TPOT 约束 50ms 条件下,启用后 **E2E 延迟下降 10%**。

---

## 【关键机制与数据】

### 工作原理

- **匹配流程**: 输入 prompt 经 `murmur_hash` 计算得到前缀 token 块的哈希键,在缓存表中按 LRU 顺序查找匹配项,命中部分跳过 prefill,仅对未命中尾部执行 prefill。
- **缓存更新时机**: prefill 完成后**立即**写入缓存,保证后续请求可即时复用,提高匹配及时性。
- **多阶段分块匹配 (chunked_scheduler)**: 在分块 prefill 过程中执行多阶段前缀匹配,从而在调度早期即削减冗余计算与显存占用。
- **DP 路由决策**: 路由时同时评估前缀命中长度与跨 rank KV 利用率差距,优先送往高亲和度 rank,但在负载严重不均时自动降级为负载均衡策略。

### 性能数据(原文)

| 测试条件 | 指标 | 结果 |
|----------|------|------|
| Qwen3-8B | TPOT 约束 | 50ms |
| 启用 prefix cache 后 | E2E 延迟 | **下降 10%** |

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

原文以行内伪公式形式给出跨 rank KV 利用率差距的计算式(保留原式):

$$
\text{cross-rank KV utilization gap} = \frac{\max(\text{used}) - \min(\text{used})}{\text{total\_blocks}}
$$

**符号含义**:
- `max_used`: 各 DP rank 中当前已使用的 KV block 数(最大值)。
- `min_used`: 各 DP rank 中当前已使用的 KV block 数(最小值)。
- `total_blocks`: 系统中 KV block 的总容量。
- 整体含义: 衡量数据并行下 rank 间 KV 利用的相对不均衡程度。

**作用**: 当该比值超过阈值 `prefix_cache_aware_dp_imbalance_threshold` (默认 `0.1`) 时,系统判定负载倾斜过严重,**关闭** cache-affinity 路由,转而选择负载最低的 rank,以避免单一 rank 被打爆。

(文档中另含一阈值 `prefix_cache_aware_dp_match_threshold = 0.5`,表示前缀 block 命中率的下限,低于则回退 free-block 均衡策略——该阈值以参数形式给出,无对应数学公式。)

---

## 【关联】

- **下游/特性关联**: 文末显式引用 [Disaggregated PD](/en/features/disagg_pd/) 特性页,提示在 PD 分离架构中 prefix cache **仅在特定 scheduler 角色下支持**,需查阅 disagg_pd 文档获取支持的具体配置。
- **调度器依赖**: prefix cache 功能依赖三类调度器实现 —— `continuous_scheduler`、`chunked_scheduler`、`zero_evict_scheduler`,其优化策略因调度器而异(尤其 chunked_scheduler 拥有独立的多阶段匹配逻辑)。
- **数据并行耦合**: Cache-Aware DP 路由是 prefix cache 与 DP(数据并行)拓扑的交叉点,涉及 `dp_size` 参数与跨 rank KV 利用率统计。
- **生命周期钩子**: 缓存更新紧耦合于 prefill 阶段完成事件,属推理主流程的关键节点。

---

## 【使用方法】

启用 prefix cache 的相关 gflags 参数如下(原文给出):

```bash
# 基础启用
--enable_prefix_cache=true

# 启用 Cache-Aware DP 路由(需 dp_size > 1)
--enable_prefix_cache=true --enable_prefix_cache_aware_dp_routing=true

# 阈值调优(可选,使用默认值即可)
--prefix_cache_aware_dp_match_threshold=0.5        # 默认 0.5
--prefix_cache_aware_dp_imbalance_threshold=0.1    # 默认 0.1
```

注: 上述参数均为 **gflags** 形式,在 xLLM 启动命令行中传入即可生效;DP 路由相关阈值仅在 `enable_prefix_cache_aware_dp_routing=true` 时起作用。对于 disaggregated PD 模式下的具体配置组合,原文指引至 [Disaggregated PD](/en/features/disagg_pd/) 查阅。
