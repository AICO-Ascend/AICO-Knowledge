# Compute by Caching

> 仓 `mindie-sd` · 路径 `docs/en/features/cache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/cache.md

# docs/en/features/cache.md 一体化深度解读

## 【定位】

本文档描述 MindIE SD 套件中面向扩散模型推理的**缓存加速（Caching Acceleration）能力**——通过复用相邻 timestep/block/attention 层之间的高相似中间结果，跳过冗余计算，从而降低 DiT 类扩散模型多步迭代的推理开销，并提供了三种可独立或组合使用的策略（DiTCache、AttentionCache、Timestep Optimization）及其统一编程接口 `CacheConfig`/`CacheAgent`。

---

## 【技术要点】

1. **三类缓存策略层级递进**：文档列出三种方法——`DiTCache`（block 粒度缓存，泛化性最强）、`AttentionCache`（attention 层粒度，粒度更细）、`Timestep Optimization`（在 timestep 维度减步）。推荐组合为 "DiTCache First → AttentionCache Alternative → Timestep Optimization Supplement"。
2. **统一配置类 `CacheConfig`**：通过 `method` 字段取值 `"dit_block_cache"` 或 `"attention_cache"` 区分策略，其余参数覆盖 block/step 维度：`blocks_count`、`steps_count`（必填），`step_start/step_interval/step_end`、`block_start/block_end`（可选，默认分别 0/1/10000、0/10000）。
3. **统一执行类 `CacheAgent`**：构造时注入 `CacheConfig`，调用时通过 `apply(function, *args, **kwargs)` 把 block/attention 模块包裹起来，缓存命中时退化为张量读取。
4. **DiTCache 核心机制**：在 cache 命中时把"stepN 中某一段 block 的计算结果"直接复用到 stepM，使得该 block 序列的前向传播退化为 tensor read；通过搜索脚本在速度比（speedup ratio）约束下求最小跳过 block 数，再遍历 block start/end 组合取 MSE 最小者为最优解。
5. **AttentionCache 核心机制**：与 DiTCache 不同——它跳过的是 block **内部的 attention 层**，用空间换时间复用相邻 timestep 的 attention 结果；通过 `start step` + `min_skip_attention` 派生 `min_interval` 与 `step_end`，遍历后取 MSE 最小的配置。
6. **典型调用范式**：在 Transformer `__init__` 中将 `self.cache = None` 预留，在初始化阶段 `pipeline.transformer.cache = CacheAgent(config)` 注入，并在 forward 循环里 `self.cache.apply(block, hidden_states=…, …)` 替代原始 block 调用。

---

## 【关键机制与数据】

- **工作原理（DiTCache）**：基于"相邻迭代步/相邻 block 之间的激活相似性"，复用局部模型特征并跳过指定的 DiTBlock。原文未给出具体的速度比、block 数或 MSE 阈值等数值。
- **工作原理（AttentionCache）**：基于"相邻 timestep 之间的特征相似性"，复用 block 内 attention 层结果，跳过部分 attention 层。
- **优化流程（DiTCache）**：原文给出 4 步：
  1. 基于 speedup ratio 计算需要缓存的最少 block 数；
  2. 在每一步中，由于 block0 必须计算，从 block1 起遍历，找出三组最小的 block start/end 组合；
  3. 遍历上一步得到的全部组合，计算 caching 前后 MSE，选取 MSE 最小者为最优解；
  4. 将参数配入模型并在推理阶段启用 cache。
- **优化流程（AttentionCache）**：原文给出 3 步：
  1. 基于 speedup ratio 计算最少跳过的 attention 操作数；
  2. 基于 start step 与 min_skip_attention 计算 `min_interval` 与 `step_end`，遍历所有可能结果计算 caching 前后 MSE，取最小者为最优；
  3. 将参数配入模型并启用 cache。
- **数据流**：CacheAgent 拦截 `apply` 调用，按 `CacheConfig` 的范围/区间判定是否命中缓存；命中则返回缓存张量，未命中则执行 `function` 并按规则写入缓存。
- **性能数据**：原文未给出具体加速比、时延、显存占用或 MSE 数值。

---

## 【表格解读】

### 表 1：`CacheConfig` 参数表（原文逐字还原）

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `method` | `str` | Yes | - | Caching method, `"attention_cache"` or `"dit_block_cache"` |
| `blocks_count` | `int` | Yes | - | Number of blocks per step |
| `steps_count` | `int` | Yes | - | Total number of iteration steps |
| `step_start` | `int` | No | `0` | Step index to start caching |
| `step_interval` | `int` | No | `1` | Caching interval in steps |
| `step_end` | `int` | No | `10000` | Step index to end caching |
| `block_start` | `int` | No | `0` | Block index to start caching |
| `block_end` | `int` | No | `10000` | Block index to end caching |

**逐行解读**：
- `method`：必填枚举，限定为 `"attention_cache"` 或 `"dit_block_cache"` 两个字符串，决定走 DiTCache 还是 AttentionCache 路径。
- `blocks_count`：必填整型，描述每一步的 block 总数，是缓存命中判定与搜索脚本遍历 block 区间时所依赖的"上界"。
- `steps_count`：必填整型，扩散过程总迭代步数 T，提供 step 维度的范围。
- `step_start`（默认 `0`）：缓存开始生效的 timestep 下标，可推迟启用以保留前几步的完整计算。
- `step_interval`（默认 `1`）：强制重新计算的间隔步数，间隔点处不命中缓存，保证误差不无限累积。
- `step_end`（默认 `10000`）：缓存结束 timestep，配合 `step_start` 形成 [step_start, step_end] 的有效缓存窗口。
- `block_start`（默认 `0`）/`block_end`（默认 `10000`）：在每一步内控制从哪个 block 到哪个 block 之间允许/禁止命中缓存，配合 `blocks_count` 形成细粒度 block 区间。

### 表 2：`CacheAgent` 构造参数表（原文逐字还原）

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `config` | `CacheConfig` | Yes | - | Cache configuration object |

**逐行解读**：
- `config`：必填，类型为上一节的 `CacheConfig` 对象，CacheAgent 通过构造时持有该配置完成策略选择与命中判定。

### 表 3：`CacheAgent.apply` 方法参数表（原文逐字还原）

| Parameter | Type | Required | Description |
|------|------|------|------|
| `function` | `callable` | Yes | The function to execute (block or attention module) |
| `*args` | - | No | Positional arguments for the function |
| `**kwargs` | - | No | Keyword arguments for the function |

**逐行解读**：
- `function`：必填可调用对象，对 DiTCache 传入一个 DiTBlock，对 AttentionCache 传入一个 attention 子模块，决定被缓存替换的目标粒度。
- `*args`/`**kwargs`：可选，分别转发原模块的位置参数与关键字参数（如 `hidden_states`、`encoder_hidden_states`、`temb`、`image_rotary_emb` 等），保持与原始 forward 调用签名一致。

---

## 【公式解读】

原文无公式（LaTeX 或伪代码形式均未出现）。

---

## 【关联】

- **示例入口**：文末内部链接 `../../../examples/cache/cache.py` 指向 examples 下的 cache 目录，是 DiTCache/AttentionCache 的端到端可运行样例（含搜索脚本产出最优配置并接入 pipeline 的流程）。
- **上游调用方**：文档示例代码中出现 `pipeline.transformer.single_blocks`、`self.transformer_blocks`、`encoder_hidden_states`、`temb`、`image_rotary_emb`、`joint_attention_kwargs`、`txt_pad_len` 等字段，说明缓存能力依赖标准 DiT-style Transformer 的 forward 签名；使用方需在自家 pipeline 的 Transformer 模块中暴露上述接口字段。
- **同级特性**：与仓库总览提到的 `Diffusers + CacheDit` 框架并列——本文档描述的是 MindIE SD 内置的 CacheAgent 机制，是 CacheDit 等上层加速框架的底层能力来源之一。
- **与 timestep 优化策略的关系**：本文档列举的 "Timestep Optimization" 作为第三种可与 DiTCache/AttentionCache 叠加使用的策略，但本文件（截至截断处）尚未给出其独立章节与参数说明，应在仓库其他文档/示例中查阅。
- **设备依赖**：文档属昇腾亲和加速能力（仓库定位为"昇腾亲和的多模态加速系列套件"），与同套件中的 vLLM Omni、lightx2v 等模块并列，共同构成多框架加速矩阵。

---

## 【使用方法】

**启用方式**（原文给出的最小流程）：

1. **导入接口**
   ```python
   from mindiesd import CacheConfig, CacheAgent
   ```

2. **在模型初始化方法中构造 `CacheConfig`**（DiTCache 示例）：
   ```python
   config = CacheConfig(
       method="dit_block_cache",
       blocks_count=len(transformer.single_blocks),   # 启用缓存的 block 总数
       steps_count=args.infer_steps,                  # 总推理迭代步数
       step_start=args.cache_start_steps,             # 缓存起始 step
       step_interval=args.cache_interval,             # 强制重算的间隔步
       step_end=args.infer_steps-1,                   # 缓存终止 step
       block_start=args.single_block_start,           # 单步内缓存起始 block
       block_end=args.single_block_end                # 单步内缓存终止 block
   )
   ```
   - `method` 取 `"attention_cache"` 时即切换到 AttentionCache 路径，参数语义保持一致。

3. **在 Transformer 中预留 cache 变量**
   ```python
   self.cache = None
   ```

4. **注入 CacheAgent**
   ```python
   cache_agent = CacheAgent(config)
   pipeline.transformer.cache = CacheAgent(config)
   ```

5. **在 forward 中通过 `apply` 包裹 block**
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
           txt_pad_len=txt_pad_len,
       )
   ```

**配置项与命令**：见上文表 1（`CacheConfig` 全部参数）；**最优配置（speedup ratio、最小跳过 block/attention 数、MSE 最优解）的搜索流程** 原文给出步骤但未给出具体数值/命令行脚本，需结合文末链接 [cache.py](../../../examples/cache/cache.py) 中的搜索脚本实际执行产出。`AttentionCache` 的完整步骤化调用代码片段在原文截断处之后未给出，需查阅示例文件。

## 图文联合解读

- `dit_cache_image_1.png`: **图文联合解读：**

**1) 图示内容：** 左侧为二维计算网格——横轴是采样步 `t`(0→T)，纵轴是块索引 `s`(0→e)，每格为一个 Block；右侧通过红色引线放大展示单个 Block 的内部结构：`x → STA →(+ )→ CA →(+)→ MLP`，均为残差连接。

**2) 技术结论：** 图示论证了扩散模型推理计算呈"步 × 块"二维可分解结构，跨步与跨块两个方向均存在大量重复算子，且 Block 内部注意力/MLP 子层可被独立复用。

**3) 与文档对应：** 横轴冗余 → 支撑 **Timestep Optimization**（跳步）；纵轴冗余 → 支撑 **DiTCache**（块级缓存，首选通用策略）；Block 内 STA/CA 分层 → 支撑 **AttentionCache**（更细粒度）。网格结构直观印证文档"三种粒度可独立或组合使用"的论断。
- `dit_cache_image_2.png`: **图文联合解读**

1) **图中内容**：顶部箭头展示扩散采样的时间步序列（0 → 0.1n → 0.2n → n）。Step1 中红色括号标注"min_block"，标记每次推理必计算的最小块数；Step2 展示三种 Case（0/1/2），不同颜色的块表示在不同时刻被重新计算，其余灰色块则复用缓存结果；Step3 给出索引公式，从 step start（0、0.1n、0.2n）经 block start 映射到 block number（min_block ~ min_block+all_block//4），明确缓存重算范围。

2) **技术结论**：DiTCache 在时序维度上，仅对首末若干块重算，中间块复用前步结果，通过 min_block 机制在通用性与加速比间取得平衡。

3) **与文档对应**：图示正是文档"DiTCache First：块粒度缓存、通用性最强"这一推荐的实现依据，量化了块粒度缓存的重算边界。
- `attention_cache_image_1.png`: **图解读：**

1) **结构/数据流**：左侧为step×block二维网格，橙色块表示完整计算步（step_start及每隔step_interval），蓝色虚线块表示复用缓存的中间结果；右侧展示单个Block内部STA→CA→MLP流水线，对比说明STA输出δ被缓存时，CA与MLP仍按残差方式正常计算。

2) **技术结论**：相邻timestep间latent相似，可通过跳过Block级或Attention级子模块（STA）复用δ缓存，省去冗余计算。

3) **与文档关系**：直观印证"DiTCache First"块级缓存策略——按步间隔复用Block输出；若进一步缓存STA结果，则对应AttentionCache更细粒度方案。
- `attention_cache_image_2.png`: **图文联合解读：**

1）**图示内容**：顶部时间轴标注采样步骤，重点高亮0.15n至0.35n区间（粉红块）；下方为配置流程图，分两步：step1由"ratio"推导"min_skip_attention"；step2由"step_start"（含0.15n、0.35n锚点）经"all_step"和"min_interval"映射至"step_end"，重复三次。

2）**技术结论**：图示论证了Timestep Optimization策略的执行逻辑——在指定时间步区间内，按min_interval间隔跳过部分步骤，并依据ratio动态设置最小跳过注意力比例，从而削减冗余计算。

3）**与文档关系**：该图正是文档中"Timestep Optimization：缩减或跳过部分时间步"论点的参数化示意图，揭示其与DiTCache/AttentionCache正交互补、可叠加使用的实现机制。
