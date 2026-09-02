# swap-attention

> 仓 `mindspeed` · 路径 `docs/zh/features/swap_attention.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/swap_attention.md

# swap-attention 文档一体化深度解读

## 【定位】

这篇文档描述了 mindspeed（昇腾大模型加速库）中 **swap-attention 功能**：通过将激活值卸载到 CPU 内存并在反向传播时从 CPU 内存预取（prefetch）激活值到设备内存，从而 **替代或部分替代全重计算（recomputation）**，在显存占用与训练计算开销之间取得更优的折中。

---

## 【技术要点】

1. **核心思路**：利用 **设备内存（NPU HBM）+ CPU 内存（DDR）** 二级存储激活值；前向计算时把当前层激活值落到 CPU，反向计算时再 H2D（Host-to-Device）预取到 NPU，以 H2D 高带宽"以网补存、以网强算"，提升 MFU。
2. **与重计算的互补关系**：完整重计算（recomputation）用计算换显存；swap-attention 用 CPU 内存换显存、同时用带宽换计算，可单独使用，也可与 `--recompute-num-layers [int]` 联合使用，让"前 N 层全连接层重计算 + 所有 attention 层 swap"成为新的混合策略。
3. **前提条件**：必须开启 **flash attention 融合算子**，swap-attention 才能生效。
4. **可配置 module 范围**：通过 `--swap-modules` 控制哪些 module 的激活值参与 swap，默认值为 `"input_norm,self_attention,post_attention_norm"`；mcore 场景下默认仅预取 `self_attention` module。
5. **覆盖层数约束**：`--recompute-num-layers [int]` 的 `[int]` 指的是 **每一个 pipeline stage 的层数**，其取值需满足 `[int] ≤ num-layers / pipeline-model-parallel-size`。
6. **已知限制**：`--swap-attention` **暂不兼容 LoRA 微调**；跨 NUMA 内存访问可能引起性能波动，可通过 `export CPU_AFFINITY_CONF=1,lazy_bind:0` 做进程绑核缓解。

---

## 【关键机制与数据】

### 工作原理（原文）

1. **存储分工**：激活值不全部驻留在 NPU HBM，而是按层生命周期卸载到 CPU 内存（DDR）。
2. **预取流水线**：在梯度反向传播的同时，从 CPU 内存 **预取（prefetch）** 下一段所需的激活值到 NPU HBM，使得反向计算与 H2D 数据搬运 **重叠执行**，避免重计算带来的额外算力开销。
3. **三条工作模式**（按使用场景区分）：
   - **模式 A：仅 swap-attention（`--swap-attention`）**
     对每一层 attention 层的激活值进行 swap（CPU↔HBM 卸载/预取），不启用任何重计算 → 在"几乎不损耗性能"的前提下节省显存，支持更大模型配置。
   - **模式 B：swap-attention + 部分重计算（`--swap-attention` + `--recompute-num-layers [int]`）**
     对每一层 attention 层的激活值做预取，同时对 **前 [int] 层（每个 pp stage 内）全连接层** 进行重计算 → 替换"全重计算"，获得性能收益。
4. **依赖算子**：依赖 flash attention 融合算子才能运行；`--swap-modules` 决定参与 swap 的具体 module 集合（默认三个 norm + self_attention）。

### 数据流（基于原文表述整合）

- 前向：每层 attention 所需激活 → 落 CPU 内存。
- 反向：梯度反传到该层 → 同时 H2D 预取该层激活到 NPU → 进入 attention 反向计算。
- 与重计算耦合时：前 [int] 层全连接层不预取/不卸载，改为在前向时丢弃激活、反向时重算；其余层走 swap 路径。

### 性能数据

- 原文未给出任何具体数字（如加速比、显存节省量、MFU 提升幅度等）。文档仅以定性方式给出结论：
  - 原文："该方案相比完全重计算具有性能收益；相比不重计算具有内存收益。"
  - 原文：模式 A"几乎不损耗性能"（定性表述，非量化）。

---

## 【表格解读】

**原文无表格**。文中所有配置项以行内列表形式给出，未使用表格结构。逐字罗列如下：

| # | 参数 | 类型 | 默认值 | 作用 |
|---|------|------|--------|------|
| 1 | `--swap-attention` | flag | 关闭 | 开启 swap-attention 功能；前提为已开启 flash attention 融合算子 |
| 2 | `--recompute-num-layers [int]` | int | 未给默认值 | 与 `--swap-attention` 联合使用，对每个 pp stage 的前 [int] 层全连接层进行重计算 |
| 3 | `--swap-modules` | string | `"input_norm,self_attention,post_attention_norm"` | 自行配置参与 swap 的 module；mcore 场景下默认仅预取 `self_attention` |

---

## 【公式解读】

**原文无公式**。文中未出现 LaTeX 或伪代码形式的数学表达式。

---

## 【关联】

文档未提供内部链接（"内部链接: (无)"）。但从内容可推断的关联模块/特性如下：

- **flash attention 融合算子**：swap-attention 的硬性前提，必须先开启。
- **重计算（recomputation）机制**：本文的核心对比对象，swap-attention 被定位为对"全重计算"的替代方案；二者通过 `--recompute-num-layers [int]` 形成混合策略。
- **mcore（Megatron-Core）模型实现**：在 mcore 场景下，`--swap-modules` 的默认行为从三个 module 缩减为仅 `self_attention`，说明该特性针对 mcore 模型路径有专门默认。
- **pipeline-model-parallel-size（PP）**：作为 `--recompute-num-layers [int]` 取值上限的约束来源（`[int] ≤ num-layers / pipeline-model-parallel-size`），与并行切分策略紧耦合。
- **NUMA / CPU 绑核（`CPU_AFFINITY_CONF`）**：CPU 内存访问侧的运维依赖，因为激活值放在 CPU DDR 上，跨 NUMA 会引发性能波动。
- **LoRA 微调**：被显式标注为 **不兼容**，下游使用方需绕开此组合。

---

## 【使用方法】

启用方式（原文涉及）：

1. **仅开启 swap-attention（节省显存，性能几乎无损）**
   ```
   --swap-attention
   ```
   需先开启 flash attention 融合算子。可选追加 `--swap-modules <string>` 自定义参与 swap 的 module；mcore 下默认仅预取 `self_attention`。

2. **swap-attention + 部分重计算（替代全重计算，谋求性能收益）**
   ```
   --swap-attention
   --recompute-num-layers [int]
   ```
   - 行为：对每层 attention 做激活 swap，同时对每个 pp stage 内前 [int] 层全连接层做重计算。
   - 约束：`[int] ≤ num-layers / pipeline-model-parallel-size`。

3. **可选参数 `--swap-modules`**
   - 类型：string
   - 默认值：`"input_norm,self_attention,post_attention_norm"`
   - 作用：按模型自行裁剪参与 swap 的 module 集合。

4. **性能波动时的运维手段（原文 NOTE）**
   - 若观察到性能波动，疑似跨 NUMA 内存访问导致，可通过进程绑核缓解：
     ```
     export CPU_AFFINITY_CONF=1,lazy_bind:0
     ```

5. **不兼容组合（原文 NOTE）**
   - `--swap-attention` **暂不兼容 LoRA 微调**，应避免同时启用。

## 图文联合解读

- `swap_attention.png`: 1) 图分Forward/Backward两条时间轴，展示L0-L3每层Attention/MLP执行流水：Forward在Attention后通过"swap att"将激活值异步卸载至CPU（图注"wait&resize 0"），Backward在Attention前通过"prefetch att"从CPU预取回设备并wait同步。

2) 论证：swap与prefetch恰好对齐Attention模块边界，证明数据搬运可被计算掩盖，实现H2D带宽换显存。

3) 印证文档"以网补存、以网强算"的论点，说明`--swap-attention`通过预取重叠避免重计算，从而兼得性能与内存收益。
- `swap_attention1.png`: **图文联合解读：**

1) **图示内容**：展示4个Transformer层（横向并列），每层包含"attn"（青色填充）和"MLP"（灰色）两个模块；底部标注`--swap-attention`，表示仅开启预取功能的场景。所有attn模块被高亮，强调attention激活值被选定为预取对象。

2) **技术结论**：开启`--swap-attention`后，每一层的attention激活值均参与CPU↔Device的预取流水线，MLP模块未被纳入，从而实现"以网补存"的内存节省，且不触发重计算。

3) **与文档论点的关系**：对应文档"仅开启预取功能"场景，论证该方案可"在几乎不损耗性能的情况下节省内存"，为支持更大模型配置提供依据。
- `swap_attention2.png`: **图文解读**：

图示展示了4个Transformer层块中`attn`和`MLP`模块的执行状态差异：第1、2层MLP为绿色（重计算），对应`--recompute-num-layers 2`；attn和后续层MLP呈现蓝色（活跃）与灰色（灰色表示预取/CPU交换中）的交替状态，直观体现"以网补存"——利用CPU内存驻存attention激活值并在反向时通过H2D高带宽异步预取，与前2层MLP重计算叠加，在节省显存的同时减少额外计算开销，论证了"相比全重计算有性能收益、相比无重计算有显存收益"的结论。
