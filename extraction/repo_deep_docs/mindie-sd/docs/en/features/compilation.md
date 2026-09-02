# Compilation Features

> 仓 `mindie-sd` · 路径 `docs/en/features/compilation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/compilation.md

# 编译特性 (Compilation Features) 深度解读

## 【定位】
本文档描述 mindie-sd 在昇腾 (Ascend) NPU 上基于 PyTorch `torch.compile` 提供的自定义后端 `MindieSDBackend()`，它把"算子融合 (Pattern Fusion)"与"静态图捕获 (ACLGraph Acceleration)"两类编译期加速能力统一封装，解决 Stable Diffusion 类多模态模型在昇腾上的 kernel 启动开销与动态调度开销问题。

## 【技术要点】
1. **统一入口**：两类能力共用同一入口——将 `MindieSDBackend()` 作为 `backend` 参数传给 `torch.compile`，可作用于整个 transformer、单个 `nn.Module` 类 (装饰器) 或单个 `forward` 函数。
2. **Pattern Fusion 自动匹配**：编译期通过 Pattern Matcher 自动把常见算子组合替换为昇腾亲和的融合算子；可通过 `CompilationConfig.fusion_patterns` 单独开关 `enable_rms_norm / enable_rope / enable_adalayernorm / enable_fast_gelu / enable_mul_add` 五项，**默认全部为 `True`**。
3. **ACLGraph 静态图捕获**：在 Pattern Fusion 之上进一步用 `torch.npu.NPUGraph` 把优化后的图捕获为静态执行图，回放 (replay) 时跳过动态调度。
4. **两个 ACLGraph 模式互斥**：`aclgraph_only` (跳过 Pattern Fusion) 与 `aclgraph_with_compile` (先融合再捕获) 二选一，同时开启时 `aclgraph_with_compile` 优先级更高。
5. **首次开销与重捕获约束**：首次执行有编译开销，**默认最多 8 次尝试**；运行时输入 shape 必须与捕获时一致，否则触发 re-capture；不支持动态 shape / 动态控制流 / 条件分支，不提供 `graph.update` 接口。
6. **变长输入的外部 padding 方案**：典型应用为音频场景——先以 `max_len` 触发 capture，再对每个 chunk 做 `F.pad` 到 `max_len`，输出切片取前 `actual_len` 还原真实长度。

## 【关键机制与数据】
- **两条能力叠加关系**（原文）：Pattern Fusion 通过 Pattern Matcher 在编译期把"常见算子组合"替换为昇腾融合算子，目的是"reducing kernel launch overhead"；ACLGraph 在此基础上将图捕获为静态执行图，目的是"skipping dynamic graph scheduling during replay"。
- **首次开销**（原文）：编译开销仅出现在初次执行，默认最多 8 次尝试；正常情况下后续运行不发生重编译。benchmark 时需要**排除 warm-up 阶段**。
- **配置时序**（原文）：`CompilationConfig` 必须在调用 `torch.compile()` **之前**完成配置，因为 `torch.compile(..., backend=MindieSDBackend())` 调用时会读取 `CompilationConfig` 中的开关。
- **效果验证手段**（原文）：在 `MINDIE_LOG_LEVEL=debug` 下观察 debug 日志中的 `PatternMatchPass replace` 计数，确认 RMSNorm、RoPE 等融合算子被实际替换，再做运行时长测量。
- **DBCache 内存约束**（原文）：与 Cache-DiT DBCache 组合使用时必须设置 `PYTORCH_NPU_ALLOC_CONF='expandable_segments:True'`，否则可能内存溢出。

## 【表格解读】

### 表 1：Pattern Fusion 开关 (`fusion_patterns`)

| Option | Default | Description |
|--------|--------|------|
| `fusion_patterns.enable_rms_norm` | `True` | RMSNorm fusion |
| `fusion_patterns.enable_rope` | `True` | RoPE fusion |
| `fusion_patterns.enable_adalayernorm` | `True` | AdaLayerNorm fusion |
| `fusion_patterns.enable_fast_gelu` | `True` | fastGELU fusion |
| `fusion_patterns.enable_mul_add` | `True` | Mul+Add fusion |

**逐行解读**：
- **`enable_rms_norm`**：控制 RMSNorm (Root Mean Square Layer Normalization) 算子融合是否启用，默认开；DiT 类模型中广泛使用。
- **`enable_rope`**：控制 RoPE (Rotary Position Embedding) 算子融合是否启用，默认开；位置编码计算开销较大，融合收益明显。
- **`enable_adalayernorm`**：控制 AdaLayerNorm (Adaptive LayerNorm) 融合是否启用，默认开；SD/FLUX 类 DiT 模型中常用条件归一化。
- **`enable_fast_gelu`**：控制 fastGELU 融合是否启用，默认开；用查表/近似替换标准 GELU。
- **`enable_mul_add`**：控制 Mul+Add (乘加融合，FMA) 融合是否启用，默认开；典型如 `silu(x) * y` 类残差分支。

### 表 2：ACLGraph 配置项

| Option | Default | Description |
|--------|--------|------|
| `aclgraph_only` | `False` | ACLGraph only, skip Pattern Fusion |
| `aclgraph_with_compile` | `False` | Pattern Fusion first, then capture as ACLGraph |
| `enable_freezing` | `True` | Whether to perform constant folding before compilation |
| `safe_output_mode` | `True` | Whether to clone output during ACLGraph replay |
| `graph_log_url` | `None` | Graph transform log URL for debugging |

**逐行解读**：
- **`aclgraph_only`**：仅做 ACLGraph 静态图捕获，跳过 Pattern Fusion；默认关。用于只想消除动态调度开销、不做算子融合的场景。
- **`aclgraph_with_compile`**：先做 Pattern Fusion 再捕获成 ACLGraph（推荐路径）；默认关。与 `aclgraph_only` 互斥，**同时开启时本项优先**。
- **`enable_freezing`**：是否在编译前执行常量折叠 (constant folding)；默认开，能在编译期消除常数计算。
- **`safe_output_mode`**：是否在 ACLGraph replay 时对输出做 `clone`；默认开，避免后续算子意外修改静态图内的输出 buffer。
- **`graph_log_url`**：图变换日志的输出 URL（用于调试）；默认 `None`，不输出。

## 【公式解读】
原文无公式。

## 【关联】
- **`core_layers.md#fused-operators`**：Pattern Fusion 中五大融合算子（RMSNorm / RoPE / AdaLayerNorm / fastGELU / Mul+Add）的 API 细节定义在 `core_layers.md` 的"fused operators"小节，本文档仅列出开关用法与含义，详细调用方式需要跳转阅读。
- **`mindiesd/compilation/mindie_sd_backend.py`**：本文档在 troubleshooting 一节指向该源文件，指出后端内置了一个 logging 模块，开启后可以观察到 pattern 激活前后的图变化；与 `torch.compile` 的"缩小 scope"配合可定位 pattern 失败原因。
- **`examples/cache-dit/FLUX.1-dev.md`**：本文档把该示例作为"参考示例 (Reference Examples)"——一个完整的 FLUX.1-dev 单卡端到端流程，把 `MindieSDBackend()` 编译优化与 Cache-DiT 的 DBCache 串起来，覆盖基线/优化对比、`pip install cache-dit` 与 `PYTORCH_NPU_ALLOC_CONF` 前置依赖、`PatternMatchPass replace` 日志验证、dual-stream / single-stream transformer block 的可运行脚本等。

## 【使用方法】

### 启用 Pattern Fusion (Basic Usage)
```python
from mindiesd.compilation import MindieSDBackend
import torch

# 方式一：编译整个 transformer
pipe = FluxPipeline.from_pretrained(...)
transformer = torch.compile(pipe.transformer, backend=MindieSDBackend())
setattr(pipe, "transformer", transformer)

# 方式二：装饰整个 Module
@torch.compile(backend=MindieSDBackend())
class FluxSingleTransformerBlock(nn.Module):
    ...

# 方式三：装饰单个 forward
class FluxSingleTransformerBlock(nn.Module):
    @torch.compile(backend=MindieSDBackend())
    def forward(...):
        ...
```

### 关闭/开启单个融合模式
```python
from mindiesd.compilation import CompilationConfig

CompilationConfig.fusion_patterns.enable_rms_norm = False      # 关闭 RMSNorm 融合
CompilationConfig.fusion_patterns.enable_rope = False          # 关闭 RoPE 融合
CompilationConfig.fusion_patterns.enable_adalayernorm = False  # 关闭 adaLN 融合
CompilationConfig.fusion_patterns.enable_fast_gelu = False     # 关闭 fastGelu 融合
CompilationConfig.fusion_patterns.enable_mul_add = False       # 关闭 Mul+Add 融合
```

### 启用 ACLGraph (在 Pattern Fusion 之上)
```python
from mindiesd.compilation import CompilationConfig

# 必须在 torch.compile() 调用之前配置
CompilationConfig.aclgraph_with_compile = True
# 后续 torch.compile(..., backend=MindieSDBackend()) 自动生效
```

### 变长输入 (音频场景)
```python
max_len = 512

model = torch.compile(transformer, backend=MindieSDBackend())
_ = model(torch.randn(max_len, dim, device="npu"))  # 触发 capture

for audio_chunk in chunks:
    actual_len = audio_chunk.shape[0]
    padded = torch.nn.functional.pad(audio_chunk, (0, 0, 0, max_len - actual_len))
    output = model(padded)[:actual_len]
```

### 与 Cache-DiT 组合的前置依赖 (FLUX.1-dev)
- 安装：`pip install cache-dit`
- 环境变量：`PYTORCH_NPU_ALLOC_CONF='expandable_segments:True'`（DBCache 必需，否则可能内存溢出）
- 验证：设置 `MINDIE_LOG_LEVEL=debug`，在日志中观察 `PatternMatchPass replace` 计数确认 RMSNorm / RoPE 等已被替换，再测量 runtime
