# CustomOp

> 仓 `vllm` · 路径 `docs/design/custom_op.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/custom_op.md

# vLLM CustomOp 设计文档深度解读

## 【定位】

这篇文档描述 vLLM 中 `CustomOp` 抽象类的设计机制——它既是按 `current_platform` 把 `forward()` 自动分派到对应后端实现的运行时分发器，也是 vLLM 与 OOT (Out-Of-Tree) 插件注册自定义算子的统一注册框架。

---

## 【技术要点】

1. **双字典注册中心**: `CustomOp` 在 class 层维护两个字典，分别索引 vLLM 内置算子和 OOT 插件算子，每个条目以"注册名→类"形式存放。

2. **两种注册装饰器**:
   - `@CustomOp.register("op_name")` —— 注册 vLLM 内置算子到 `op_registry` 字典。
   - `@CustomOp.register_oot("op_name")` —— 注册 OOT 算子（细节在 `plugin_system.md` 中展开）。

3. **七路平台分发路由**（按 `current_platform` 分派；ROCm 若无 `forward_hip()` 则回退到 `forward_cuda()`；所有平台最终兜底到 `forward_native()`）：
   - CPU → `forward_cpu()`
   - CUDA → `forward_cuda()`
   - ROCm → `forward_hip()`（缺失回退到 `forward_cuda()`）
   - XPU → `forward_xpu()`
   - TPU → `forward_tpu()`
   - OOT → `forward_oot()`（仅在 OOT 平台调用）
   - Default → `forward_native()`

4. **启用/禁用决策由 `compilation_config.custom_ops` 驱动**: 仅当 `CustomOp` 注册名出现在该列表中才启用自定义实现；否则调用 `forward_native()`。`all`/`none` 两个关键字互斥，前者全启用、后者全禁用；`+op_name` 表示强制启用、`-op_name` 表示强制禁用。

5. **默认启用策略自动追加**: 当 `compilation_config.backend == "inductor"` 且 `compilation_config.mode != CompilationMode.NONE` 时自动追加 `none`；否则自动追加 `all`。含义：在 `torch.compile` 模式下，让 Inductor 为禁用项生成（融合的）Triton kernel。

6. **对象级强制启用**: 多模态场景下 vLLM 已硬启用 `MMEncoderAttention`、`ApplyRotaryEmb` 等以保留设备特定深度优化 kernel；也可通过 `CustomOp.__init__(enforce_enable=True)` 在对象级强制启用自身。原文注明：`enforce_enable` 机制将在后续给多模态拆分独立 `compilation_config` 后移除。

---

## 【关键机制与数据】

**注册—分发—决策三段式工作流**（原文）:

1. **注册阶段**: 通过 `@CustomOp.register("op_name")` 把类加入 `op_registry`；通过 `@CustomOp.register_oot("op_name")` 注册 OOT 实现。

2. **调用阶段**（原文）:
   > "When a `CustomOp` is called (i.e., call its `forward()` method), if it is enabled (i.e., with `--compilation_config.custom_ops '["+op_name"]'`), it will automatically dispatch the forward method to the appropriate backend according to `current_platform`. Otherwise (i.e., it is disabled), it will only call the `forward_native()` method to use PyTorch-native implementation of this forward method."

3. **默认行为拼接规则**（原文）:
   > "By default, if `compilation_config.backend == "inductor"` and `compilation_config.mode != CompilationMode.NONE`, a `none` will be appended into `compilation_config.custom_ops`, otherwise a `all` will be appended."

**数据流（推断自原文文字）**: 用户/CLI → `compilation_config.custom_ops` 字符串列表 → CustomOp `__init__` 时解析为"启用集合" → `forward()` 被调用时查表决定分派到哪个 `forward_xxx()`，或回落到 `forward_native()`。

**性能相关数字**: 原文未给出量化性能数据（如吞吐、延迟、kernel 加速比等）。唯一与"性能动机"相关的描述是"为多模态 ViT 部分保留设备特定深度优化 kernel"，没有具体数字。

**继承重写警告**（原文）:
> "Note that the dispatching logic might not be absolute because of class inheritance. Derived class might override the behavior."

---

## 【表格解读】

原文无表格。原文通过列表形式给出了"平台→分派方法"的对照规则，以及"配置关键字→语义"的对照，但都没有采用表格形式呈现。

---

## 【公式解读】

原文无公式。文档中既无 LaTeX 公式，也无伪代码形式的状态方程/代价函数——CustomOp 的所有逻辑均通过装饰器签名、字符串列表配置和条件分支表达。

---

## 【关联】

- **`./plugin_system.md`**: 这是文末给出的唯一内部链接。`CustomOp` 的 OOT 注册路径（`@CustomOp.register_oot("op_name")` → `forward_oot()`）依赖于插件系统加载 OOT 实现，文档明确说明 OOT 注册机制将在 plugin_system.md 中详细介绍。
- **`compilation_config` 体系**: CustomOp 的启用/禁用决策完全寄生于 `CompilationConfig` 中的 `custom_ops` 字段、`backend` 字段和 `mode`（`CompilationMode` 枚举）字段；与之相关的还有 `torch.compile` / `inductor` 后端的融合 Triton kernel 生成路径。
- **`torch.compile` / Inductor**: 当默认 backend 是 inductor 且 mode 非 `NONE` 时，CustomOp 会被刻意禁用以便让 Inductor 接管融合。
- **多模态 ViT 路径**: `MMEncoderAttention`、`ApplyRotaryEmb`、`MMEncoderAttn`、`qwen2_decoder`、`rel_pos_attention` 等多模态算子被点名，说明 CustomOp 与多模态编码器子图存在紧耦合；文档预留了"未来给多模态单独一个 `compilation_config`"的演进方向。

---

## 【使用方法】

**CLI 命令**（原文给出，可直接用于启动 server）:

```bash
# 全启用
--compilation_config.custom_ops '["all"]'

# 全禁用
--compilation_config.custom_ops '["none"]'

# 除 op1 外全部启用（- 前缀 = 禁用）
--compilation_config.custom_ops '["all,-op1"]'

# 仅启用 op1 和 op2（+ 前缀 = 启用，基于 none 之上叠加）
--compilation_config.custom_ops '["none,+op1,+op2"]'
```

**实现新 CustomOp 的步骤**（原文 tutorial 段落）:
1. 实现一个新类，继承自 `CustomOp` 基类。
2. 在类上添加 `@CustomOp.register("op_name")` 装饰器以注册到 `CustomOp` 系统。
3. 根据需要实现不同的 `forward_xxx()` 方法（如 `forward_native`、`forward_cuda`、`forward_cpu` 等）。

**示例骨架**（原文给出，以 `MMEncoderAttention` 为例）:
- `__init__` 接收 `num_heads`、`head_size`、`scale`、`num_kv_heads`、`prefix`、`multimodal_config` 等参数。
- `forward_native(...)` 调用 TORCH_SDPA 实现。
- `forward_cuda(...)` 调用 FA 或 TORCH_SDPA 实现。
- `forward_cpu(...)`（原文片段在 `cu_seqlens: torch.Tensor | None = No` 处被截断，但足以看出签名形态）。

**强制启用参数**（原文）: 在 `CustomOp.__init__()` 中传入 `enforce_enable=True`，可在对象级强制启用该 op，绕过全局 `custom_ops` 配置。

**当前已注册的 CustomOp 类别**（原文清单）:
- Attention: `multi_head_latent_attention`
- Activation: `silu_and_mul`、`mul_and_silu`、`gelu_new`、`gelu_fast`、`quick_gelu`、`gelu_and_mul`、`gelu_and_mul_sparse`、`relu2`、`xielu`、`swigluoai_and_mul`、`fatrelu_and_mul`
- MM-Conv: `conv2d`、`conv3d`
- Embedding: `vocab_parallel_embedding`、`parallel_lm_head`
- Linear: `row_parallel_linear`、`column_parallel_linear`、`replicated_linear`
- Logits Processor: `logits_processor`
- Mamba: `mamba_mixer`、`mamba_mixer2`、`mixer2_gated_rms_norm`、`short_conv`
- MoE: `fused_moe`、`modular_fused_moe`、`unquantized_fused_moe`、`transformers_fused_moe`、`grouped_topk`
- Norm: `rms_norm`、`rms_norm_gated`、`gemma_rms_norm`
- Quantization: `quant_fp8`
- Rope: `rotary_embedding`、`dual_chunk_rotary_embedding`、`apply_rotary_emb`
- Encoder: `qwen2_decoder`、`mm_encoder_attn`、`rel_pos_attention`

> 注：上文 `原文无表格` / `原文无公式` 处明确说明文档未包含该形式内容；任何"性能加速比"、"kernel 耗时"等数字均未在原文中出现，本文不作臆造。
