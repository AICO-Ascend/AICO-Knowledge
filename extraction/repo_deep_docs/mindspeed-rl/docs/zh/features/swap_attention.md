# swap-attention

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/swap_attention.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/swap_attention.md

# swap-attention 文档深度解读

## 【定位】
这篇文档描述 swap-attention 功能——在反向传播时从 CPU 内存动态预取 attention 层激活值，利用 H2D（Host-to-Device）高带宽传输缓解大模型训练中的"内存 vs 重计算"权衡瓶颈，从而提升 MFU、节省显存并支持更大模型配置。

## 【技术要点】
1. **核心机制**：在梯度反向传播过程中，从 CPU 内存预取 attention 层激活值（节省原本需要重计算的 forward 激活），借 H2D 高带宽补足 host→device 的数据搬运。
2. **两种使用场景**：(a) 开启 `swap_attention` + `recompute_num_layers:[int]`，用 attention 预取 + 前 N 层 FFN 重计算替代"全重计算"；(b) 仅开启 `swap_attention`，在不重计算前提下节省显存，几乎不损性能。
3. **预设预取模块**：`swap_modules` 默认值为 `"input_norm,self_attention,post_attention_norm"`；在 mcore 场景下默认仅预取 self_attention module，可按模型自行配置。
4. **重计算层数控制**：`recompute_num_layers`（int，默认 None 即不开启重计算）控制每层中前若干层全连接层走重计算路径。
5. **强制前置依赖**：必须开启 flash attention 融合算子 `use_flash_attn = True`。
6. **性能调优手段**：跨 NUMA 内存访问可能引起性能波动，可通过 `export CPU_AFFINITY_CONF=1,lazy_bind:0` 做进程绑核缓解。

## 【关键机制与数据】
**工作原理（原文整合）：** 文档描述了一个与传统重计算对立的方案——传统方案在反向传播时"重新算"前向激活以省显存，但代价是额外的 compute 和 latency；swap-attention 改为"在反向传播的同时，把事先保留在 CPU 内存中的 attention 层激活值异步预取回 device"，从而绕开重计算的 compute 开销，并把数据传输交给 H2D 高带宽链路承担。

**两种模式下的数据流差异（原文）：**
- **场景 a（开启重计算优化性能）**："对每一层的 attention 层的激活值进行预取，同时，对前 [int] 层的全连接层进行重计算。" → 用 attention 层的 H2D 预取 + FFN 前 N 层重计算，组合替代全重计算。
- **场景 b（仅预取）**："对每一层的 attention 层的激活值进行预取，提高计算效率。" → 不引入任何重计算，纯靠预取节省显存。

**性能收益定性描述（原文）：**
- "充分利用 H2D 高带宽的数据传输优势" → 传输链路是性能基础。
- "有效缓解内存瓶颈，提升 MFU，加速大模型训练" → 收益指标明确指向 **MFU** 与训练吞吐。
- 场景 b 收益表述为"几乎不损耗性能的情况下，节省内存，以支持更大的模型的配置"。

## 【表格解读】
原文无表格。文档仅以"参数 + 默认值 + 含义"的散文形式列出 `swap_modules` 与 `recompute_num_layers`，未提供参数对照表或性能对比表，故此处不做表格还原。

## 【公式解读】
原文无公式。文档未给出任何数学公式或伪代码形式的表达，所有机制以文字描述配合 `figures/swap_attention{0,1,2}.png` 示意呈现。

## 【关联】
文档自身未提供内部链接（"内部链接: (无)"），但从内容中可梳理出以下模块/特性关联：
- **前置依赖**：`use_flash_attn = True`（flash attention 融合算子）—— swap-attention 必须在 flash attention 开启时使用。
- **互补/替代关系**：与传统的"全重计算（recompute）"策略互为替代——场景 a 即是用 swap-attention + 局部重计算替代全重计算。
- **并行维度耦合**：`recompute_num_layers` 的取值被绑定到 pipeline model parallel 维度，原文明确"`[int]` 的取值应该小于等于 `num_layers / pipeline_model_parallel_size`"，即按 pp stage 切分生效。
- **硬件亲和性**：与 NUMA 拓扑耦合，原文给出 `CPU_AFFINITY_CONF=1,lazy_bind:0` 的绑核缓解方案，说明 H2D 预取对 CPU 侧的内存局部性敏感。
- **不兼容特性**：与 LoRA 微调不兼容，原文明确"`swap_attention` 暂不兼容 LoRA 微调"。
- **mcore 适配**：`swap_modules` 在 mcore 场景下默认行为与通用场景不同（默认仅预取 self_attention module），说明其与 Megatron-Core 风格的模块划分存在耦合。

## 【使用方法】
**启用步骤（原文）：**
1. （前提）开启 flash attention 融合算子：`use_flash_attn = True`。
2. 开启 swap_attention 功能：`swap_attention: True`。

**可选参数（原文逐字）：**
| 参数名 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `swap_modules` | string | `"input_norm,self_attention,post_attention_norm"` | 可根据模型自行配置 module；mcore 场景下默认仅预取 self_attention module |
| `recompute_num_layers` | int | `None`（即不开启重计算） | 可根据场景需要自行配置重计算的层数；开启时与 `swap_attention` 配合用于"优化重计算性能"场景 |

**注意事项（原文逐字）：**
1. `recompute_num_layers [int]` 中的 `[int]` 层数指的是**每一个 pp stage 的层数**；取值应 `<= num_layers / pipeline_model_parallel_size`。
2. 若出现性能波动，可能是跨 NUMA 内存访问引起，可尝试通过进程绑核缓解 `export CPU_AFFINITY_CONF=1,lazy_bind:0`。
3. `swap_attention` 暂不兼容 LoRA 微调。

## 图文联合解读

- `swap_attention0.png`: **图示内容**：上半为前向（Forward），L0-L3 各层 Attention 模块后触发 `swap att`（存激活到CPU），MLP 后 `wait&resize 0`；下半为反向（Backward），先 `prefetch att`（H2D 取回），MLP 处 `wait`（重计算）。

**技术结论**：Attention 激活在反向时从CPU异步预取，MLP 采用重计算，二者并行掩盖传输与重算开销。

**与文档关系**：印证"swap_attention + recompute_num_layers"替换全重计算的机制——用H2D高带宽换内存，用预取与重算交叠提升MFU。
- `swap_attention1.png`: **图文联合解读：**

**图示**：四组Transformer层块，每块含attn与MLP。全部attn为蓝色（启用预取）；前2层MLP为绿色（激活保留），后2层MLP灰化（重计算）。配置：`swap_attention:true`，`recompute_num_layers:2`。

**技术结论**：采用"attention全预取 + MLP选择性重计算"的混合策略：H2D高带宽从CPU预取attn激活以节省显存与重算开销，仅对指定层MLP进行重计算，避免全量重算带来的计算冗余。

**与文档关系**：对应使用场景(a)，即以`swap_attention`+`recompute_num_layers`的组合替代全重计算方案，提升MFU并缓解显存瓶颈。
- `swap_attention2.png`: **图文解读：**

图示展示了4个连续的transformer层，每层含`attn`（青蓝色填充）与`MLP`（白色描边）两个模块，配文`swap_attention: true`。

**技术结论：** 仅对attention层的激活值进行CPU-GPU动态预取，MLP层不受影响，无需重计算。

**与文档关系：** 对应使用场景b——"仅开启预取，节省内存"，强调在不损耗性能的前提下，以H2D高带宽传输替代attention重计算，缓解显存瓶颈。
