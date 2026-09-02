# Dynamic Speculative Decoding

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/dynamic_speculative_decoding.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/dynamic_speculative_decoding.md

# 深度解读: Dynamic Speculative Decoding

## 【定位】

本文档描述 vLLM 中"动态投机解码 (Dynamic Speculative Decoding, DSD)"能力——根据运行时并发度 (batch size, BS) 动态调整每序列的草稿 token 数 K,从而在并发负载变化时仍维持投机解码对 TPOT 的正向收益。

---

## 【技术要点】

1. **核心矛盾**: 投机解码 (SD) 在解码阶段需对每条序列验证 K 个 token,使"有效 BS"放大为 `BS*K`;一旦 `BS*K` 越过临界 BS,验证开销将反噬解码速度 (TPOT)。DSD 通过按 BS 自适应调整 K 来规避此问题。
2. **配置入口**: 在任何 SD 方法的 `--speculative-config` 中追加 `num_speculative_tokens_per_batch_size` 字段,其为"列表的列表",每条 entry 形如 `[start_bs, end_bs, optimal_K]`,表示当并发度落入 `[start_bs, end_bs]` 时使用 `optimal_K` 个草稿 token。
3. **退化兜底**: 当 K=0 表示完全禁用草稿 (no draft tokens produced),即在该 BS 区间直接回退到普通自回归解码。
4. **默认/兜底字段**: 同时仍保留 `num_speculative_tokens` 作为静态默认 K,DP 模式下自动回退到此静态值。
5. **在线切换时机**: K 的调整发生在每次调度的运行时,根据当前并发度所在区间选择对应的 optimal_K,无需重启服务。
6. **环境变量约束**: 文中给出的在线示例需显式设置 `VLLM_USE_V2_MODEL_RUNNER=0` (即关闭 Model Runner V2),说明该示例是面向 MRv1 路径展示的;但 Limitations 同时指出 Full Cudagraph 仅 MRv2 支持。

---

## 【关键机制与数据】

- **工作原理 (原文)**: "SD methods need to verify K tokens for each sequence during decoding. As BS increases, the effective BS becomes BS*K which increases the compute requirement during verification. When this BS*K goes beyond a critical BS then SD negatively impacts the decode speed (TPOT). DSD helps by tuning the K to an optimal value such that we continue to reap the benefits from SD."
- **数据流 (原文示例)**: Eagle Drafter 配置为三段映射 `[1,64,3] / [65,128,1] / [129,512,0]`,意即并发度 ≤64 用 K=3、65–128 用 K=1、129–512 用 K=0;Eagle3 Drafter 配置为五段映射 `[1,16,5] / [17,32,4] / [33,64,3] / [65,128,1] / [129,512,0]`,体现"并发越低,允许的草稿越多"的渐缩策略。
- **典型 RL rollout 场景 (原文)**: 训练初期高并发,末期因少量长尾请求拉低有效并发,DSD 在末尾自动上调 K 以保持吞吐。
- **性能数据**: 原文未提供任何量化 benchmark 数字 (无 TPOT 改善比例、无延迟数字、无吞吐对比)。仅以 K=0/1/3/4/5 等离散取值作为定性建议。

---

## 【表格解读】

原文未提供正式 markdown 表格,但其核心配置 `num_speculative_tokens_per_batch_size` 实质是一个"BS 区间 → K"映射表,以下基于原文逐字还原并解读:

**Eagle Drafter (Llama-3.1-8B-Instruct)**

| start_bs | end_bs | optimal_K | 含义 (原文逐字) |
|----------|--------|-----------|------------------|
| 1 | 64 | 3 | "K=3 will be used when the concurrency is in range [1, 64]" |
| 65 | 128 | 1 | "K=1 will be used when the concurrency is in range [65, 128]" |
| 129 | 512 | 0 | "K=0 will be used when the concurrency is in range [129, 512], i.e., no draft tokens will be produced." |

逐行解读:
- 第一行: 低并发区间 (1–64) 启用完整草稿深度 K=3,投机收益最大且验证开销可承受。
- 第二行: 中并发区间 (65–128) 草稿深度降至 K=1,验证开销减半,平衡收益与开销。
- 第三行: 高并发区间 (129–512) 关闭草稿 (K=0),直接退化为普通自回归,验证放大效应被彻底消除。

**Eagle3 Drafter (Llama-3.1-8B-Instruct)**

| start_bs | end_bs | optimal_K |
|----------|--------|-----------|
| 1 | 16 | 5 |
| 17 | 32 | 4 |
| 33 | 64 | 3 |
| 65 | 128 | 1 |
| 129 | 512 | 0 |

逐行解读:
- 第一行: 极低并发 (1–16) 允许最大草稿深度 K=5,Eagle3 多 token 草稿的接受率优势得以发挥。
- 第二行: 并发 17–32 时 K=4,渐进缩量。
- 第三行: 并发 33–64 时 K=3,与 Eagle 配置对齐。
- 第四行: 并发 65–128 时 K=1,验证压力已显著。
- 第五行: 并发 ≥129 时 K=0,完全关闭草稿。
- 整体规律: BS↑ → K↓,且 K 的下降梯度在低 BS 段较缓 (3→4→5),在高 BS 段陡降 (1→0)。

---

## 【公式解读】

原文无 LaTeX 公式,仅出现两处概念性表达,逐字保留并解释:

**概念 1: 有效批量放大**
```
effective BS = BS * K
```
- `BS`: 实际并发序列数 (concurrency / batch size)。
- `K`: 每个序列每步需验证的草稿 token 数。
- `effective BS`: 单步验证阶段实际处理的 token 总数,即 SD 对计算压力的放大倍数。

**概念 2: 反转条件 (原文表述式)**
> "When this BS*K goes beyond a critical BS then SD negatively impacts the decode speed (TPOT)."

- `critical BS`: 未在原文中给出具体数值,为一个隐含的、与硬件/模型相关的阈值。
- `TPOT`: Time Per Output Token,每生成一个 token 的延迟。
- 含义: 当 `BS * K > critical BS` 时,验证阶段的额外计算开始抵消草稿命中带来的加速,SD 由收益转为拖累。

**配置 schema (伪代码式)**
```
num_speculative_tokens_per_batch_size := [[start_bs, end_bs, optimal_K], ...]
```
- `start_bs`, `end_bs`: 区间闭区间端点 (原文示例未说明开闭性,示例区间连续衔接,推断为左闭右闭或端点归属前段)。
- `optimal_K`: 该并发区间下推荐的草稿 token 数,可为 0 (即禁用 SD)。

---

## 【关联】

- **Eagle / Eagle-3 / DFlash**: 文中明确指出 DSD 当前已测试通过的 SD 方法集合,其他方法"may or may not work out of the box",故特性与这三类草稿模型强耦合。
- **Model Runner V1 vs V2 (MRv1 / MRv2)**: DSD 与运行时的 cuda graph 能力绑定——MRv2 支持 Full Cudagraph,MRv1 仅支持 piece-wise cuda graph;同时原文在线示例刻意使用 `VLLM_USE_V2_MODEL_RUNNER=0`,意味着示例走 MRv1 路径但仅能获得 piece-wise cuda graph 加速。
- **`num_speculative_tokens` (静态字段)**: 在 DP 启用时被作为兜底回退值,二者构成"动态优先 / 静态兜底"的关系。
- **Data Parallelism (`--data-parallel-size > 1`)**: 与 DSD 互斥。原文解释机制: "Each DP rank schedules independently, so ranks can pick different K values, causing DP collective divergence and deadlocks."——即各 DP rank 独立调度会选出不同 K,导致集合通信 (collective) 维度发散并死锁,故启用 DP 时 vLLM 自动禁用 DSD 字段。
- **Speculative Decoding 总体框架**: DSD 是投机解码特性族下的子能力,作用于解码阶段的 K 选择,不改变草稿模型/验证算法本身。

---

## 【使用方法】

**启用方式 (原文)**

1. 在 `vllm serve` 命令中通过 `--speculative-config '<JSON>'` 注入 DSD 配置。
2. JSON 内必填字段:
   - `method`: 草稿方法 (示例: `eagle`, `eagle3`)。
   - `model`: 草稿模型路径 (示例: `yuhuili/EAGLE-LLaMA3.1-Instruct-8B`)。
   - `num_speculative_tokens`: 静态默认 K (示例: `3`)。
   - `num_speculative_tokens_per_batch_size`: 动态映射列表,格式 `[[start_bs, end_bs, optimal_K], ...]`。

**原文给出的两条可直接复制的在线示例**:

- **Eagle Drafter**:
```bash
VLLM_USE_V2_MODEL_RUNNER=0 vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --speculative-config '{
    "method": "eagle",
    "model": "yuhuili/EAGLE-LLaMA3.1-Instruct-8B",
    "num_speculative_tokens": 3,
    "num_speculative_tokens_per_batch_size": [
      [1, 64, 3],
      [65, 128, 1],
      [129, 512, 0]
    ]
  }'
```

- **Eagle3 Drafter**:
```bash
VLLM_USE_V2_MODEL_RUNNER=0 vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --speculative-config '{
    "method": "eagle3",
    "model": "yuhuili/EAGLE3-LLaMA3.1-Instruct-8B",
    "num_speculative_tokens": 3,
    "num_speculative_tokens_per_batch_size": [
      [1, 16, 5],
      [17, 32, 4],
      [33, 64, 3],
      [65, 128, 1],
      [129, 512, 0]
    ]
  }'
```

**使用约束 (原文 Limitations)**:
- 仅 Eagle / Eagle-3 / DFlash 经过测试。
- Full Cudagraph 仅 MRv2 支持;MRv1 仅支持 piece-wise cuda graph。
- 不兼容 `--data-parallel-size > 1`;启用 DP 时 vLLM 自动回退到静态 `num_speculative_tokens`。
