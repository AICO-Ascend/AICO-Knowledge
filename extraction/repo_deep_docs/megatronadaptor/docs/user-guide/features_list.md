# Megatron-LM 支持特性列表

> 仓 `megatronadaptor` · 路径 `docs/user-guide/features_list.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/megatronadaptor/docs/user-guide/features_list.md

# Megatron-LM 支持特性列表 — 一体化深度解读

---

## 【定位】

这篇文档是 Megatron-LM（昇腾适配版）训练脚本所有命令行参数的**配置目录手册**，按功能分类（激活函数 / 注意力机制 / 位置编码 / 归一化 / 混合精度 / 并行策略）逐条罗列支持的 `--参数名`、`描述`、`约束`（互斥、依赖、默认值），为用户在 `pretrain_xxx.py` 入口脚本上配置训练任务提供参数速查与约束说明。文档末尾章节被截断（停在 6.4 上下文并行的标题，表格内无内容）。

---

## 【技术要点】

1. **六类核心特性域**：激活函数、注意力机制、位置编码、归一化、混合精度（FP16/BF16/FP8）、并行策略（TP/PP/SP/CP），均以命令行 `--flag` 形式暴露，每条均含"依赖/互斥"约束说明。
2. **激活函数互斥族**：`--swiglu` / `--squared-relu` / `--quick-geglu` 三者两两互斥；融合内核类 `--use-te-activation-func` 仅支持 `gelu/silu/relu`；另含 MoE 场景专用 `--use-fused-weighted-squared-relu`。
3. **MLA vs GQA 互斥**：Multi-Latent Attention（`--multi-latent-attention`）与 Group Query Attention（`--group-query-attention`）互斥，前者通过低秩压缩 KV（`q-lora-rank`、`kv-lora-rank`）降显存，后者通过共享 KV 头降显存。
4. **位置编码多实现**：支持 `learned_absolute` / `rope` / `yarn` / `mrope` / `relative` / `none` 六类；RoPE 提供缩放（`--use-rope-scaling`、`--rope-scaling-factor` 默认 8.0）、外推（`rotary-seq-len-interpolation-factor`）、YaRN（`mscale`、`mscale-all-dim`）等长序列支持。
5. **混合精度双路线**：BF16/FP16 直接互斥；FP8 由 Transformer Engine 提供，需 `--fp8-format {e4m3, hybrid}` 与 `--fp8-recipe {tensorwise, delayed, mxfp8, blockwise}` 联合配置，并支持首尾层 BF16 隔离（`--first-last-layers-bf16`）。
6. **多层互斥与分阶段通信重叠**：TP 通信重叠（`--tp-comm-overlap`）下含 6 个细粒度 `disable-*` 子开关；PP 部分 P2P 通信重叠中"warmup-flush"与"普通 overlap"互斥；`--pipeline-model-parallel-layout` 与 `decoder-first/last-pipeline-num-layers` 互斥。

---

## 【关键机制与数据】

以下均出自原文（仅摘录有数字 / 明确机制的部分）：

- 原文：默认位置编码类型 `--position-embedding-type` 默认 `learned_absolute`；RoPE 频率基数 `--rotary-base` 默认 `10000`；归一化 `--norm-epsilon` 默认 `1e-5`。
- 原文：T5 风格相对注意力桶数 `--relative-attention-num-buckets` 默认 `32`，最大距离 `--relative-attention-max-distance` 默认 `128`。
- 原文：MLA 中 `--q-lora-rank` 默认 `None`（MLA 配置默认 `512`），`--kv-lora-rank` 默认 `32`（MLA 配置默认 `512`），`--qk-head-dim` 默认 `128`，`--qk-pos-emb-head-dim` 默认 `64`，`--v-head-dim` 默认 `128`。
- 原文：RoPE 缩放因子 `--rope-scaling-factor` 默认 `8.0`；MLA 配置中 `--rotary-scaling-factor` 默认 `40`（普通默认 `1.0`）；YaRN `--mscale` 默认 `1.0`，`--mscale-all-dim` 默认 `0.0`。
- 原文：动态损失缩放 `--initial-loss-scale` 默认 `2^32`，窗口 `--loss-scale-window` 默认 `1000`，最小值 `--min-loss-scale` 默认 `1.0`，滞后 `--hysteresis` 默认 `2`。
- 原文：FP8 余量 `--fp8-margin` 默认 `0`，更新频率 `--fp8-interval` 默认 `1`，amax 历史窗口 `--fp8-amax-history-len` 默认 `1`；FP8 amax 计算策略二选一 `most_recent` / `max`。
- 原文：并行度 `--tensor-model-parallel-size` 与 `--pipeline-model-parallel-size` 默认均为 `1`；VPP microbatch 组 `--microbatch-group-size-per-virtual-pipeline-stage` 默认 `1`；`--rotary-percent` 默认 `1.0`（全维度应用）。

---

## 【表格解读】

### 表 1 — 激活函数（原文逐字还原）

| 参数名 | 描述 | 约束 |
|--------|------|------|
| `--swiglu` | 使用 SwiGLU 激活函数 | 与 `--squared-relu`、`--quick-geglu` 互斥 |
| `--squared-relu` | 使用 Squared ReLU 激活函数 | 与 `--swiglu` 互斥 |
| `--openai-gelu` | 使用 OpenAI 近似 GELU 激活函数 | 遗留参数，无互斥校验 |
| `--quick-geglu` | 使用快速 GeGLU 激活函数 | 与 `--swiglu` 互斥 |
| `--use-te-activation-func` | 使用 Transformer Engine 实现的激活函数 | 布尔开关；与 bias_activation_fusion 互斥；仅支持 gelu/silu/relu |
| `--use-fused-weighted-squared-relu` | 启用融合的加权 Squared ReLU 内核 | 布尔开关；用于 MoE 场景的融合加权 Squared ReLU 内核 |
| `--no-bias-gelu-fusion` | 禁用 bias-GELU 融合内核 | 布尔开关；当 add_bias_linear=False 时自动禁用 |
| `--no-bias-swiglu-fusion` | 禁用 bias-SwiGLU 融合内核 | 布尔开关；只对 `--swiglu` 生效 |

**逐行解读**：第 1–4 行是用户可选的激活函数族，`swiglu/squared-relu/quick-geglu` 三者互相排斥（同时只能启一个），而 `openai-gelu` 是历史遗留位，默认即可用。第 5 行是 Transformer Engine 后端入口，受 `bias_activation_fusion` 互斥约束，且只覆盖三种激活；第 6 行专门为 MoE 引入；最后两行是 bias+激活融合内核关闭开关，控制性能/精度取舍。

### 表 2 — 注意力机制（原文逐字还原）

| 参数名 | 描述 | 约束 |
|--------|------|------|
| `--use-flash-attn` | 启用 Flash Attention 加速注意力计算 | 布尔开关 |
| `--flash-decode` | 启用 Flash 解码模式 | 布尔开关；不能与 `--no-rope-freq` 同时使用 |
| `--group-query-attention` | 启用 Group Query Attention (GQA)，多个 Q 头共享 KV 头 | 布尔开关；需配合 `--num-query-groups` 设置组数；与 `--multi-latent-attention` 互斥 |
| `--multi-latent-attention` | 启用 Multi-Latent Attention (MLA)，通过低秩压缩 KV 降低显存 | 布尔开关；需配合 `--q-lora-rank`、`--kv-lora-rank`、`--qk-head-dim`、`--v-head-dim` 使用；与 `--group-query-attention` 互斥 |
| `--q-lora-rank` | MLA 中 Q 矩阵的低秩压缩维度 | int，默认 None（MLA 配置中默认 512）；依赖 `--multi-latent-attention` |
| `--kv-lora-rank` | MLA 中 KV 矩阵的低秩压缩维度 | int，默认 32（MLA 配置中默认 512）；依赖 `--multi-latent-attention` |
| `--qk-head-dim` | MLA 中每个头的 QK 维度 | int，默认 128；依赖 `--multi-latent-attention` |
| `--qk-pos-emb-head-dim` | MLA 中位置编码部分的头维度 | int，默认 64；依赖 `--multi-latent-attention` |
| `--v-head-dim` | MLA 中每个头的 V 维度 | int，默认 128；依赖 `--multi-latent-attention` |
| `--qk-layernorm` | 对 Q、K 向量分别做 LayerNorm 归一化 | 布尔开关 |
| `--qk-l2-norm` | 对 Q、K 向量做 L2 归一化 | 布尔开关（Llama4 风格） |
| `--relative-attention-num-buckets` | 设置 T5 风格相对注意力偏置的桶数 | int，默认 32；仅 `--position-embedding-type relative` 时有效 |
| `--relative-attention-max-distance` | 设置相对注意力偏置的最大距离 | int，默认 128；依赖 `--position-embedding-type relative` |
| `--apply-query-key-layer-scaling` | 将注意力分数除以 √head_dim 进行缩放 | 布尔开关；启用时自动设置 `--attention-softmax-in-fp32` |
| `--attention-backend` | 指定注意力计算的后端实现 | 可选值：`auto`、`flash`、`fused`、`unfused`、`local`；默认 `auto` |
| `--attention-output-gate` | 在注意力输出上应用门控机制 | 布尔开关 |
| `--window-size` | 设置滑动窗口注意力的窗口大小 | tuple(int,int)，默认 None（全局注意力）；-1 表示无限窗口 |
| `--window-attn-skip-freq` | 窗口注意力的跳过频率，每隔 N 层使用一次全局注意力 | int；依赖 `--window-size` |
| `--disable-bias-linear` | 禁用所有线性层的偏置 | 布尔开关（将 add_bias_linear 设为 False） |
| `--add-qkv-bias` | 仅为 QKV 投影层添加偏置 | 布尔开关，默认 False；当 add_bias_linear=True 时自动设为 True |

**逐行解读**：前 4 行是注意力架构选择（普通 / Flash / Flash Decode / GQA / MLA），其中 GQA 与 MLA 互斥；中间 5 行是 MLA 的低秩参数（Q、KV 维度+头维度+位置编码维度）；`qk-layernorm` / `qk-l2-norm` 是 QK 端归一化两种流派；`relative-attention-*` 用于 T5 风格相对偏置；`apply-query-key-layer-scaling` 启用后会自动把 softmax 提升到 FP32；`attention-backend` 五选一便于在不同平台切内核；`window-size`/`window-attn-skip-freq` 是 LongLLaMA 类滑动窗口组合；最后两行控制全局是否禁用 bias。

### 表 3 — 位置编码（原文逐字还原）

| 参数名 | 描述 | 约束 |
|--------|------|------|
| `--position-embedding-type` | 位置编码类型 | 可选值：`learned_absolute`、`rope`、`yarn`、`mrope`、`relative`、`none`；默认 `learned_absolute` |
| `--use-rotary-position-embeddings` | 启用旋转位置编码 (RoPE) | 布尔开关（已废弃）；设置后强制 position_embedding_type='rope' |
| `--rope-type` | RoPE 的具体实现类型 | 可选值：`rope`、`yarn`；默认 None（MLA 默认 `yarn`，普通注意力默认 `rope`） |
| `--rotary-base` | RoPE 频率基数 θ | int，默认 10000 |
| `--rotary-percent` | 对每个头的前 N% 维度应用旋转编码 | float，默认 1.0（全部维度） |
| `--rotary-seq-len-interpolation-factor` | RoPE 序列长度插值因子，用于外推更长序列 | float，默认 None |
| `--use-rope-scaling` | 启用 RoPE 缩放（线性外推） | 布尔开关；需配合 `--rope-scaling-factor` |
| `--rope-scaling-factor` | RoPE 线性缩放因子 | float，默认 8.0；依赖 `--use-rope-scaling` |
| `--no-rope-freq` | 指定跳过 RoPE 的层频率（每 N 层不加 RoPE） | int 或 list，默认 None；不能与 `--flash-decode` 同时使用；int 时须整除 num_layers |
| `--rotary-interleaved` | 使用交错方式应用旋转维度（而非前后对半分） | 布尔开关；不能与 `--multi-latent-attention` 同时使用 |
| `--no-rope-fusion` | 禁用 RoPE 的融合内核优化 | 布尔开关 |
| `--rotary-scaling-factor` | 旋转缩放因子 | float，默认 1.0（MLA 配置中默认 40） |
| `--mscale` | YaRN 中的 mscale 参数，控制注意力温度 | float，默认 1.0 |
| `--mscale-all-dim` | YaRN 中对所有维度应用 mscale | float，默认 0.0 |
| `--mrope-section` | 指定多维 RoPE (M-RoPE) 的维度分段方式 | list of int；`--position-embedding-type mrope` 时必填 |
| `--max-position-embeddings` | 模型支持的最大位置编码长度 | int，默认 None；须 >= seq_length |

**逐行解读**：第一行是"总开关"，六选一决定位置编码家族；`use-rotary-position-embeddings` 标注已废弃但保留向后兼容（旧脚本里写着不会报错）；`rotary-base=10000` 与 `rotary-percent=1.0` 描述 RoPE 频率与维度覆盖范围；`use-rope-scaling + rope-scaling-factor` 用于线性外推，`rotary-seq-len-interpolation-factor` 用于序列长插值；`mscale/mscale-all-dim` 是 YaRN 温度控制；`mrope-section` 是 M-RoPE 必填项；`--no-rope-freq`（每隔 N 层不加 RoPE）与 `--flash-decode` 互斥，`--rotary-interleaved` 与 MLA 互斥；`max-position-embeddings` 是序列长度上限校验点。

### 表 4 — 归一化（原文逐字还原）

| 参数名 | 描述 | 约束 |
|--------|------|------|
| `--normalization` | 归一化层类型 | 可选值：`RMSNorm`、`LayerNorm`；默认 `LayerNorm` |
| `--norm-epsilon` | 归一化计算中的 epsilon，防止除零 | float，默认 1e-5 |
| `--apply-residual-connection-post-layernorm` | 残差连接接在 LayerNorm 之后（而非之前） | 布尔开关 |
| `--no-persist-layer-norm` | 禁用持久化 LayerNorm | 布尔开关 |
| `--apply-wd-to-qk-layernorm` | 对 QK LayerNorm 的参数也应用权重衰减 | 布尔开关 |
| `--fused-residual-rmsnorm` | 使用融合的 RMSNorm + 残差连接内核 | 布尔开关；依赖 `--normalization RMSNorm` |

**逐行解读**：`normalization` 二选一决定归一化家族；`norm-epsilon=1e-5` 是数值稳定的下限常量；后 4 行都是性能 / 训练风格的微调开关：残差位序、是否使用持久化内核、QK-LN 是否走权重衰减、RMSNorm 与残差融合。

### 表 5 — 混合精度训练（原文逐字还原）

| 参数名 | 描述 | 约束 |
|--------|------|------|
| `--bf16` | 使用 BF16 混合精度训练 | 布尔开关；与 `--fp16` 互斥 |
| `--fp16` | 使用 FP16 混合精度训练 | 布尔开关；与 `--bf16` 互斥 |
| `--fp32-residual-connection` | 残差连接使用 FP32 精度（提高数值稳定性） | 布尔开关 |
| `--fp8-format` | FP8 低精量化格式 | 可选值：`e4m3`、`hybrid`；依赖 TE 库 |
| `--fp8-recipe` | FP8 量化策略 | 可选值：`tensorwise`、`delayed`、`mxfp8`、`blockwise`；依赖 `--fp8-format` |
| `--fp8-margin` | FP8 amax 计算时的余量值 | int，默认 0 |
| `--fp8-interval` | FP8 缩放因子更新频率（每 N 步更新一次） | int，默认 1 |
| `--fp8-amax-history-len` | FP8 amax 历史窗口长度 | int，默认 1 |
| `--fp8-amax-compute-algo` | FP8 amax 计算策略 | 可选值：`most_recent`、`max` |
| `--no-fp8-wgrad` | 禁用 FP8 权重梯度计算 | 布尔开关 |
| `--fp8-param-gather` | 在参数 AllGather 阶段使用 FP8 通信 | 布尔开关；依赖 `--fp8-format` |
| `--fp8-quantizer-factory` | 自定义 FP8 量化器的 Python 实现路径 | str；用于 `custom` 量化策略 |
| `--reuse-grad-buf-for-mxfp8-param-ag` | MXFP8 参数收集时复用梯度缓冲区以节省显存 | 布尔开关；依赖 `--fp8-recipe mxfp8` |
| `--keep-fp8-transpose-cache` | 保留 FP8 转置缓存 | 布尔开关 |
| `--te-precision-config-file` | Transformer Engine 精度配置文件路径 | str (YAML/JSON) |
| `--first-last-layers-bf16` | 首尾层使用 BF16（其余层可用 FP8） | 布尔开关 |
| `--num-layers-at-start-in-bf16` | 起始使用 BF16 的层数 | int；依赖 `--first-last-layers-bf16` |
| `--num-layers-at-end-in-bf16` | 末尾使用 BF16 的层数 | int；依赖 `--first-last-layers-bf16` |
| `--grad-reduce-in-bf16` | 梯度 AllReduce 使用 BF16 通信 | 布尔开关 |
| `--disable-bf16-reduced-precision-matmul` | 禁用 BF16 低精度矩阵乘法累加 | 布尔开关 |
| `--attention-softmax-in-fp32` | 注意力 softmax 使用 FP32 计算 | 布尔开关；启用 `--apply-query-key-layer-scaling` 时自动开启 |
| `--fp16-lm-cross-entropy` | 语言模型交叉熵使用 FP16 计算 | 布尔开关；依赖 `--fp16` |
| `--loss-scale` | 固定损失缩放值（不使用动态缩放） | float，默认 None（使用动态缩放） |
| `--initial-loss-scale` | 动态损失缩放的初始值 | float，默认 2^32 |
| `--loss-scale-window` | 损失缩放窗口大小（连续 N 步无溢出则翻倍） | int，默认 1000 |
| `--min-loss-scale` | 最小损失缩放值 | float，默认 1.0 |
| `--hysteresis` | 损失缩放滞后参数（允许连续 N 次溢出再缩小） | int，默认 2 |
| `--accumulate-allreduce-grads-in-fp32` | 梯度 AllReduce 累积使用 FP32 | 布尔开关 |

**逐行解读**：最顶层 `bf16/fp16` 互斥；`fp32-residual-connection` 可单独提升残差精度；中段是 FP8 完整配置（`format × recipe` 二维选择 + amax 历史窗口与计算策略）；`first-last-layers-bf16 + num-layers-at-start/end-in-bf16` 是首尾层精度隔离，避免 FP8 影响关键层；`grad-reduce-in-bf16` / `accumulate-allreduce-grads-in-fp32` 控制集合通信精度；`attention-softmax-in-fp32` 与 QK 缩放自动联动；最末 5 行是 FP16 损失缩放族（固定/动态/窗口/最小值/滞后）。

### 表 6 — 张量并行 / 流水线并行 / 序列并行（原文逐字还原）

#### 6.1 张量并行

| 参数名 | 描述 | 约束 |
|--------|------|------|
| `--tensor-model-parallel-size` | 张量并行度，将模型权重按列/行切分到多个 GPU | int，默认 1 |
| `--tp-comm-overlap` | 启用 TP 通信与计算重叠（AllGather/ReduceScatter） | 布尔开关，默认 False；开启后以下 disable 参数才生效 |
| `--tp-comm-overlap-cfg` | 指定 TP 通信重叠配置 YAML 文件路径 | str (YAML)；依赖 `--tp-comm-overlap` |
| `--disable-tp-comm-bulk-wgrad` | 禁用 TP 通信批量 wgrad 重叠 | 布尔开关；依赖 `--tp-comm-overlap` |
| `--disable-tp-comm-bulk-dgrad` | 禁用 TP 通信批量 dgrad 重叠 | 布尔开关；依赖 `--tp-comm-overlap` |
| `--disable-tp-comm-overlap-ag` | 禁用 TP 通信 AllGather 重叠 | 布尔开关；依赖 `--tp-comm-overlap` |
| `--disable-tp-comm-overlap-rs` | 禁用 TP 通信 ReduceScatter 重叠 | 布尔开关；依赖 `--tp-comm-overlap` |
| `--disable-tp-comm-split-ag` | 禁用 TP 通信 Split AllGather | 布尔开关；依赖 `--tp-comm-overlap` |
| `--disable-tp-comm-split-rs` | 禁用 TP 通信 Split ReduceScatter | 布尔开关；依赖 `--tp-comm-overlap` |
| `--no-clone-scatter-output-in-embedding` | 禁用 Embedding 中 scatter 输出的 clone | 布尔开关 |

#### 6.2 流水线并行

| 参数名 | 描述 | 约束 |
|--------|------|------|
| `--pipeline-model-parallel-size` | 流水线并行度，将模型按层切分到多个 stage | int，默认 1 |
| `--pipeline-model-parallel-layout` | 自定义流水线并行布局（每 stage 的层分配） | str；与 `--decoder-first/last-pipeline-num-layers` 互斥 |
| `--num-layers-per-virtual-pipeline-stage` | 每个虚拟流水线阶段的层数（启用 VPP） | int；需能被总层数整除 |
| `--num-virtual-stages-per-pipeline-rank` | 每个流水线 rank 的虚拟阶段数 | int；与 `--num-layers-per-virtual-pipeline-stage` 二选一 |
| `--decoder-first-pipeline-num-layers` | 解码器第一个流水线阶段的层数 | int；与 `--pipeline-model-parallel-layout` 互斥 |
| `--decoder-last-pipeline-num-layers` | 解码器最后一个流水线阶段的层数 | int；与 `--pipeline-model-parallel-layout` 互斥 |
| `--account-for-embedding-in-pipeline-split` | 在流水线切分时将 Embedding 层参与层数计算 | 布尔开关 |
| `--account-for-loss-in-pipeline-split` | 在流水线切分时将 Loss 层参与层数计算 | 布尔开关 |
| `--microbatch-group-size-per-virtual-pipeline-stage` | VPP 中每个虚拟 stage 连续执行的 micro-batch 数量 | int，默认 1；依赖 VPP 开启 |
| `--pipeline-model-parallel-comm-backend` | 流水线并行通信后端 | 可选值：`nccl`、`ucc` |
| `--overlap-p2p-communication-warmup-flush` | 重叠 P2P 通信预热刷新阶段 | 布尔开关 |
| `--no-overlap-p2p-communication` | 禁用 P2P 通信重叠 | 布尔开关；与 `--overlap-p2p-communication-warmup-flush` 互斥 |

#### 6.3 序列并行

| 参数名 | 描述 | 约束 |
|--------|------|------|
| `--sequence-parallel` | 启用序列并行，将 LayerNorm/Dropout 按序列维度切分 | 布尔开关；依赖 `--tensor-model-parallel-size > 1` |

#### 6.4 上下文并行（原文表格被截断，仅有标题与表头，无内容行）

> **说明**：原文 6.4 节只给出小标题，表格内一行数据都没有（文档此处截止）。

**逐行解读 — 6.1 TP**：基础并行度 `--tensor-model-parallel-size` 默认 1；`--tp-comm-overlap` 是通信计算重叠总开关，开启后才有 6 个细粒度 `disable-*` 子开关（覆盖 bulk wgrad/dgrad、AllGather、ReduceScatter、Split AG/RS）；`--no-clone-scatter-output-in-embedding` 控制 Embedding 路径上的 clone 行为（性能取舍）。

**逐行解读 — 6.2 PP**：基础并行度 `--pipeline-model-parallel-size` 默认 1；VPP 由 `--num-layers-per-virtual-pipeline-stage` 或 `--num-virtual-stages-per-pipeline-rank` 二选一启用（互斥）；`layout` 与 `decoder-first/last` 互斥；`microbatch-group-size-per-virtual-pipeline-stage` 控制 VPP 内 micro-batch 连续执行数；通信后端 NCCL/UCC 二选一；末尾 3 行是 P2P 通信重叠组的互斥对。

**逐行解读 — 6.3 SP**：序列并行唯一开关 `--sequence-parallel`，**依赖 TP>1** 才能启用，本质是把 SP 作为 TP 的一种扩展维度，复用其切分网格。

---

## 【公式解读】

原文无公式。

说明：本文档是纯配置目录，未给出任何 LaTeX 数学式或伪代码表达式。文档中诸如"除以 √head_dim"等描述仅以文字形式存在，未以公式呈现。

---

## 【关联】

文档本身**未提供内部锚链接**（题目给定"内部链接: (无)"），但通过"约束"列描述了多条跨章节的依赖关系，可梳理为以下隐性关联：

- **注意力 ↔ 位置编码**：`--no-rope-freq` 与 `--flash-decode` 互斥（注意力 vs 位置编码）；`--rotary-interleaved` 与 `--multi-latent-attention` 互斥（位置编码 vs MLA）；`--relative-attention-num-buckets/max-distance` 仅在 `position-embedding-type=relative` 时生效。
- **注意力 ↔ 归一化**：QK 端的 `--qk-layernorm` / `--qk-l2-norm` / `--apply-wd-to-qk-layernorm` 三处分别落在"注意力"与"归一化"两章，构成端到端 QK 归一化路径。
- **激活函数 ↔ 注意力**：`--use-te-activation-func` 与 `bias_activation_fusion` 互斥；同时 `--no-bias-gelu-fusion` 在 `add_bias_linear=False` 时自动禁用，体现激活与线性 bias 配置的联动。
- **混合精度 ↔ 注意力 / 训练**：`--apply-query-key-layer-scaling` 自动开启 `--attention-softmax-in-fp32`；`--disable-bias-linear` 会自动调整 `--add-qkv-bias`；`--fp8-recipe=mxfp8` 触发 `--reuse-grad-buf-for-mxfp8-param-ag`。
- **并行策略 ↔ 混合精度**：`--grad-reduce-in-bf16` / `--accumulate-allreduce-grads-in-fp32` / `--fp8-param-gather` 等通信精度开关直接影响集合通信与并行切分。
- **并行策略内部**：TP（6.1）的通信重叠与 PP（6.2）的 P2P 重叠属于不同通信阶段；SP（6.3）依赖于 TP>1；CP（6.4）原文档截断未给参数。
- **与外部库的依赖**：所有 FP8 相关参数、`--te-precision-config-file`、`--use-te-activation-func` 均依赖 Transformer Engine（TE）库；`--pipeline-model-parallel-comm-backend` 二选一 NCCL 或 UCC。
- **上游/下游模块关联**：`--first-last-layers-bf16` + 头尾 `--num-layers-at-start/end-in-bf16` 与并行策略中的"层切分"耦合，因为这些 BF16 隔离层的存在会影响流水线阶段的层数计算。

---

## 【使用方法】

原文本身即是使用方法参考（每行一条 `--flag`），核心启用模式如下：

- **激活函数选择**：在 `pretrain_gpt.py` / `pretrain_bert.py` 等入口脚本里以 `--swiglu` / `--s
