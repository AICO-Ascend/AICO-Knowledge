# 以存代算

> 仓 `mindie-sd` · 路径 `docs/zh/features/cache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/cache.md

# MindIE SD 缓存加速特性深度解读

## 【定位】

本文档系统阐述了 MindIE SD 在扩散模型推理场景下「以存代算」的缓存加速能力，针对扩散模型多时间步迭代中相邻步 latent 相似导致的大量冗余计算问题，提供 DiTCache（block 粒度缓存）、AttentionCache（Attention 层粒度缓存）、时间步优化三类可独立或组合使用的加速手段。

---

## 【技术要点】

- **三大缓存策略并存、可独立或组合**：DiTCache（block 粒度，最通用、推荐首选）、AttentionCache（Attention 层粒度，更细粒度）、时间步优化（调整/跳过迭代步数，作为补充）。
- **统一的配置抽象 CacheConfig**：必选字段为 `method`（`"dit_block_cache"` 或 `"attention_cache"`）、`blocks_count`（每步 block 数）、`steps_count`（总迭代步数）；可选字段 `step_start`（默认 `0`）、`step_interval`（默认 `1`，强制重新计算间隔）、`step_end`（默认 `10000`）、`block_start`（默认 `0`）、`block_end`（默认 `10000`）。
- **统一的执行代理 CacheAgent**：通过 `apply(function, *args, **kwargs)` 包装 block 或 attention 模块的原始调用；`apply` 第一个入参为 `callable`（要执行的 block 或 attn 模块），后续参数与原代码一致。
- **DiTCache 优化方法（搜索 + MSE 选最优）**：先按加速比算出最少需 cache 的 block 数，再从 block1 开始遍历找最小三组 (block_start, block_end) 组合，最后遍历全部组合用 MSE 最小者作为最优配置；命中缓存时将 DiTBlock 序列的前向变成张量读取。
- **AttentionCache 优化方法（空间换时间）**：按加速比 ratio 计算需跳过的最小 attention 次数，结合 `start_step` 与 `min_skip_attention` 推出 `min_interval` 与 `step_end`，遍历所有组合找 MSE 最小配置；直接复用 stepN 的 Attention 结果到 stepM。
- **时间步优化两种方式**：① 修改 timestep 数值（如 50→20）；② Adastep 自适应动态跳步（当前仅 CogVideoX 使用，已被 DiTCache / AttnCache 替代）。
- **AttentionCache 显存代价**：开启会增加显存消耗，单卡易出现 `RuntimeError: NPU out of memory`，官方推荐八卡推理。

---

## 【关键机制与数据】

- **冗余来源（原文）**：扩散模型推理会循环迭代多个时间步，每步所有 block 都参与计算；相邻步之间 latent 相似 → 中间结果几乎相同 → 计算冗余 → 推理慢。
- **DiTCache 原理（原文）**：基于相邻迭代采样步骤间、或相邻 block 间的激活相似性，复用模型局部特征，跳过指定的 DiTBlock。
- **DiTCache 核心优化点（原文）**：缓存命中时，直接复用 stepN 中特定 block 区间的计算结果到 stepM，从而将整个 DiTBlock 序列的正向传播计算变成一次简单的张量读取操作。
- **DiTCache 优化流程（原文 4 步）**：
  1. 根据加速比计算最小需要 cache 的 block 数。
  2. 在每个 step 中，由于 block0 需要计算，所以从 block1 开始遍历，通过计算找到最小的三组 block start 和 block end。
  3. 遍历上一步骤中得到的所有可能的组合，计算模型 cache 前和 cache 后的 MSE，找到 MSE 损失最小的配置作为最优解。
  4. 将上述步骤得到的参数配置在模型中，并在执行推理时开启 cache 完成加速。
- **AttentionCache 原理（原文）**：基于相邻时间步特性相似性，与 DiTCache 不同——AttentionCache 通过复用 block 里的 Attention 计算结果，跳过部分 Attention 层。
- **AttentionCache 核心优化点（原文）**：利用以空间换时间的原理，直接复用 stepN 的 block 的 Attention 层计算缓存结果到 stepM。
- **AttentionCache 优化流程（原文 3 步）**：
  1. 根据加速比 ratio，计算最小需要跳过的 attention 次数。
  2. 根据开始 step 和 min_skip_attention 计算出 min_interval 与 step_end，并遍历所有可能的结果，计算模型 cache 前和 cache 后的 MSE，找到 MSE 损失最小的配置作为最优解。
  3. 将上述步骤中得到的参数配置在模型中，并在执行推理时开启 cache 完成加速。
- **时间步优化原理（原文）**：通过减少、调整或跳过扩散模型去噪过程中的某些步骤，在尽量不损失精度的前提下，减少 DitModule 数量，避免冗余计算。
- **Adastep（原文）**：自适应的、动态的时间步跳过算法；推理时实时评估 latent 当前状态，动态决定跳过 step 间差异较小的若干步；当前仅在 CogVideoX 中使用，其他模型没有使用，被 DiTCache、AttnCache 替代。
- **性能数字**：原文未给出具体的加速比、MSE 阈值、显存占用等数值数据。

---

## 【表格解读】

### 表 1：CacheConfig 参数表（逐字还原）

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `method` | `str` | 是 | - | 缓存方法，`"attention_cache"` 或 `"dit_block_cache"` |
| `blocks_count` | `int` | 是 | - | 每步的 block 数 |
| `steps_count` | `int` | 是 | - | 总迭代步数 |
| `step_start` | `int` | 否 | `0` | 开始缓存步数 |
| `step_interval` | `int` | 否 | `1` | 缓存间隔步数 |
| `step_end` | `int` | 否 | `10000` | 结束缓存步数 |
| `block_start` | `int` | 否 | `0` | 开始缓存 block 索引 |
| `block_end` | `int` | 否 | `10000` | 结束缓存 block 索引 |

**解读**：三个必选参数构成缓存策略的最小描述——`method` 决定缓存粒度（Attention 层 vs DiT block），`blocks_count` 描述模型结构信息（与 AttentionCache 中 `transformer.transformer_blocks` 数量对应），`steps_count` 决定总步长上限。可选参数提供了缓存生效的窗口（`step_start` / `step_end`）、强制刷新的间隔（`step_interval`，默认 1 即每步都可能复用）以及 block 维度的裁剪范围（`block_start` / `block_end`）。默认 `step_end=10000` 与 `block_end=10000` 表明未显式配置时，缓存范围默认覆盖到索引上限，实际使用时应按 `steps_count - 1` 收敛。

### 表 2：CacheAgent 构造参数表（逐字还原）

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `config` | `CacheConfig` | 是 | - | 缓存配置对象 |

**解读**：CacheAgent 是配置驱动型的执行代理，自身仅持有一个 `CacheConfig` 引用，所有行为由配置决定，体现「配置与执行分离」的设计。

### 表 3：CacheAgent.apply 方法签名（逐字还原）

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `function` | `callable` | 是 | 要执行的函数（block 或 attn 模块） |
| `*args` | - | 否 | 函数位置参数 |
| `**kwargs` | - | 否 | 函数关键字参数 |

**解读**：`apply` 是一种「装饰性调用」接口——它既能在 DiTCache 中以 block 为粒度包裹 `self.transformer_blocks` 中的每个 DiTBlock，也能在 AttentionCache 中以 attn 模块为粒度包裹 block 内部的 `self.attn`，因此通过统一的 `callable + args/kwargs` 协议屏蔽底层差异。

---

## 【公式解读】

原文无公式（无 LaTeX 数学式，也无伪代码形式的算式表达）。

---

## 【关联】

- **示例代码**：文末显式给出内部链接 `examples/cache/cache.py`（路径为 `../../../examples/cache/cache.py`），是本文档中 DiTCache 与 AttentionCache 两条路径的统一示例载体，文档标注「具体示例详情请参见 examples 下的 cache 目录」。
- **模块间协同**：CacheConfig 与 CacheAgent 在 DiTCache 路径下作用于 `pipeline.transformer`（取 `transformer.single_blocks` 长度作为 `blocks_count`）；在 AttentionCache 路径下作用于 `transformer.transformer_blocks` 内部的 attention 子模块——两者通过同一对接口服务不同的模型结构层。
- **替代关系**：Adastep 时间步跳过算法已被 DiTCache / AttnCache 替代，仅在 CogVideoX 中作为遗留路径保留。

---

## 【使用方法】

### 公共前置步骤
1. 导入接口：
   ```python
   from mindiesd import CacheConfig, CacheAgent
   ```

### 启用 DiTCache
2. 初始化 `CacheConfig`，`method="dit_block_cache"`：
   ```python
   config = CacheConfig(
       method="dit_block_cache",
       blocks_count=len(transformer.single_blocks),
       steps_count=args.infer_steps,
       step_start=args.cache_start_steps,
       step_interval=args.cache_interval,
       step_end=args.infer_steps-1,
       block_start=args.single_block_start,
       block_end=args.single_block_end
   )
   ```
3. 在 Transformer 的 `init` 方法中初始化缓存变量：`self.cache = None`
4. 初始化并挂载 CacheAgent：
   ```python
   cache_agent = CacheAgent(config)
   pipeline.transformer.cache = CacheAgent(config)
   ```
5. 在 Transformer 的 `forward` 中遍历 block 并通过 `apply` 调用：
   ```python
   for index_block, block in enumerate(self.transformer_blocks):
       hidden_states, encoder_hidden_states = self.cache.apply(
           block,
           hidden_states=hidden_states,
           encoder_hidden_states=encoder_hidden_states,
           encoder_hidden_states_mask=encoder_hidden_states_mask,
           temb=temb,
           image_rotary_emb=image_rotary_emb,
           joint_attention_kwargs=attention_kwargs,
           txt_pad_len=txt_pad_len
       )
   ```

### 启用 AttentionCache
2. 初始化 `CacheConfig`，`method="attention_cache"`，`block_start`/`block_end` 可用默认：
   ```python
   config = CacheConfig(
       method="attention_cache",
       blocks_count=len(transformer.transformer_blocks),
       steps_count=args.infer_steps,
       step_start=args.start_step,
       step_interval=args.attentioncache_interval,
       step_end=args.end_step
   )
   ```
3. 在 Transformer 的 block 模块 `init` 中初始化：`self.cache = None`
4. 初始化 CacheAgent 并对 block 列表中每个 block 挂载：
   ```python
   cache_agent = CacheAgent(config)
   for block in transformer.transformer_blocks:
       block.cache = cache_agent
   ```
5. 在 block 模块的 `forward` 中对 attention 子模块使用 `apply`：
   ```python
   attn_output = self.cache.apply(
       self.attn,
       hidden_states=img_modulated,
       encoder_hidden_states=txt_modulated,
       encoder_hidden_states_mask=encoder_hidden_states_mask,
       image_rotary_emb=image_rotary_emb,
       **joint_attention_kwargs,
   )
   ```

### 启用时间步优化
- 方式一：修改 timestep 数值（例如从 50 减到 20）。
- 方式二：Adastep 自适应跳步（当前仅 CogVideoX 可用，已被 DiTCache / AttnCache 替代）。

### 注意事项（原文 FAQ）
- Qwen-Image-Edit-2509 开启 AttentionCache 报 `RuntimeError: NPU out of memory` 时，推荐使用八卡推理。

## 图文联合解读

- `dit_cache_image_1.png`: 图示DiT推理的二维计算网格：横轴为采样步0~T，纵轴为Block 0~B，每格执行一个Block（右侧放大显示其内部STA→⊕→CA→⊕→MLP残差结构）。

论证：相邻步latent相似引发网格内大量冗余计算，故可沿步维度在块粒度（DiTCache）或Attention粒度（AttentionCache）缓存复用。

与文档呼应：直观呈现CacheConfig中`steps_count`/`blocks_count`/`step_start`/`block_start`参数的网格作用域，支撑"块级优先、Attention级备选"的策略选择。
- `dit_cache_image_2.png`: **图文联合解读：**

**图示内容**：顶部为采样步时间轴（0, 0.1n, 0.2n … n）；step1 表示每步中仅中间连续 block 作为 `min_block` 需重算；step2 以 Case0/1/2 三列展示不同步间 block 复用命中着色（绿/粉/蓝）；step3 展示 `step_start` 与 `block_start` 二维筛选关系，最少重算量 = `min_block` ≈ `all_block/4`。

**技术论证**：在"步"与"块"两个维度同时裁剪计算范围——仅未命中缓存的 block 才重算，其余直接复用历史结果，从而削减相邻步间 latent 相似造成的冗余。

**文档关系**：对应 `CacheConfig` 中 `step_start/step_end`、`block_start/block_end`、`blocks_count` 参数，直观可视化 DiTCache "以存代算"的复用机制与推荐策略。
- `attention_cache_image_1.png`: **图文联合解读**

图示左侧网格按 `step_interval` 间隔缓存 block：蓝色虚线块为完整计算序列，橙色块复用前步缓存结果；右侧对比单 block 内部结构，缓存命中时跳过 STA 模块，仅以残差 δ 直连，仅计算 CA 与 MLP。论证了相邻采样步 latent 相似性可在 block 粒度消除大量冗余计算，正对应文档中 **DiTCache** 的 block 级复用策略。
- `attention_cache_image_2.png`: **图文联合解读：**

图示展示了采样步长轴（0→n）中以 0.15n–0.35n 为缓存起点的区间。step1 根据 ratio 计算 min_skip_attention；step2 将 step_start 区间映射至 all_step=n-2，再经 min_interval 抵达 step_end=end，多条并行箭头表示间隔缓存窗口。

技术结论：以 ratio 动态驱动步级缓存策略，实现按时间步粒度的冗余跳过计算。

与文档关系：直观可视化 CacheConfig 中 `step_start`、`step_end`、`step_interval` 协同控制"时间步优化"缓存范围的机制，佐证缓存参数可精细调控推理步数。
