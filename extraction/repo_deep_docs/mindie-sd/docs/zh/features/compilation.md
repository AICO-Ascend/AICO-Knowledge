# 编译特性

> 仓 `mindie-sd` · 路径 `docs/zh/features/compilation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/compilation.md

# 编译特性文档深度解读

## 【定位】

这篇文档系统介绍了 MindIE SD 基于 PyTorch `torch.compile` 框架提供的自定义后端 `MindieSDBackend()`，以及它在昇腾 NPU 上提供的两套互补编译加速能力（Pattern 融合 + ACLGraph 加速），重点解决扩散模型/多模态模型在昇腾芯片上的算子融合开销与 kernel 调度开销问题。

---

## 【技术要点】

1. **双能力互补架构**：`MindieSDBackend()` 同时承载 Pattern 融合（Pattern Matcher 将常见算子组合替换为昇腾融合算子）与 ACLGraph 加速（通过 `torch.npu.NPUGraph` 捕获静态执行图、replay 时跳过动态调度）两套机制，通过统一的 `CompilationConfig` 集中控制。

2. **三种使用入口**：可对 `transformer` 整体调用 `torch.compile(..., backend=MindieSDBackend())`、可对单个 `nn.Module` 用装饰器、可对 `forward` 函数用装饰器，三种方式效果等价。

3. **五种融合 Pattern 开关**：`CompilationConfig.fusion_patterns` 提供 `enable_rms_norm`、`enable_rope`、`enable_adalayernorm`、`enable_fast_gelu`、`enable_mul_add` 五个布尔开关，全部默认 `True`，可单独关闭某个 Pattern。

4. **ACLGraph 两模式互斥**：`aclgraph_only`（仅 ACLGraph，跳过 Pattern 融合）与 `aclgraph_with_compile`（先 Pattern 融合再捕获为 ACLGraph）二者互斥；同时开启时 `aclgraph_with_compile` 优先级更高。

5. **编译一次性成本与回退**：使能后首次运行最多进行 8 次编译尝试，后续运行一般不再重编；benchmark 测试需将预热阶段耗时去除以避免偏差。

6. **变长输入适配策略**：语音等场景的动态序列长度通过外部 padding 到固定 `max_len`、capture 后用 `[:actual_len]` 切片取回实际输出，以满足 ACLGraph 对静态 shape 的要求。

---

## 【关键机制与数据】

- **工作原理（Pattern 融合路径）**：`MindieSDBackend` 内置多组算子融合 Pattern，编译阶段由 Pattern Matcher 扫描计算图，命中后自动替换为昇腾优化算子；每个 Pattern 独立可控，详细 API 见 `core_layers.md#融合算子`。
- **工作原理（ACLGraph 路径）**：在 Pattern 融合优化后的图基础上，使用 `torch.npu.NPUGraph` 将计算图捕获为静态执行计划；replay 阶段跳过动态图调度，直接执行预编译的 kernel 序列。
- **配置时机约束**（原文：`CompilationConfig` 需在 `torch.compile()` 调用前完成配置）：若在 `torch.compile()` 之后再修改 `CompilationConfig`，不会作用于已编译图。
- **首次耗时与重捕规则**（原文：首次触发图捕获存在一次性耗时开销；运行时输入 shape 须与捕获时一致，变更会触发重新捕获）：表明 ACLGraph 模式对输入 shape 敏感，shape 变更将付出重新捕获代价。
- **动态能力边界**（原文：不支持动态 shape、动态 control flow 或 conditional branching）：ACLGraph 静态图本质不支持这三类动态行为，超出此范围需切回非编译模式。
- **环境依赖**（原文：仅昇腾 NPU 环境支持）：后端强依赖 `torch.npu` 能力栈，非 NPU 环境无法运行。
- **参考示例验证手段**（原文）：通过 `MINDIE_LOG_LEVEL=debug` 观察 `PatternMatchPass replace` 匹配数量，确认 RMSNorm、RoPE 等融合算子已被替换后再统计耗时，确保优化真正生效。

---

## 【表格解读】

### 表格一：Pattern 融合配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `fusion_patterns.enable_rms_norm` | `True` | RMSNorm 融合 |
| `fusion_patterns.enable_rope` | `True` | RoPE 融合 |
| `fusion_patterns.enable_adalayernorm` | `True` | AdaLayerNorm 融合 |
| `fusion_patterns.enable_fast_gelu` | `True` | fastGELU 融合 |
| `fusion_patterns.enable_mul_add` | `True` | Mul+Add 融合 |

**逐行解读**：
- `enable_rms_norm` (默认 `True`)：控制 RMSNorm（均方根归一化）算子融合；常用于 LLM/DiT 中的归一化层。
- `enable_rope` (默认 `True`)：控制 Rotary Position Embedding（旋转位置编码）融合；常见于注意力 Q/K 的位置编码。
- `enable_adalayernorm` (默认 `True`)：控制 Adaptive LayerNorm（自适应层归一化）融合；常用于 DiT 中带条件输入的归一化变体。
- `enable_fast_gelu` (默认 `True`)：控制 fastGELU 近似激活函数融合；用于替代标准 GELU 的快速实现。
- `enable_mul_add` (默认 `True`)：控制 Mul+Add（乘加融合）Pattern；典型于 AdaLN 中的 `scale*x + shift` 类操作。
- 全部默认 `True` 的设计表明，融合 Pattern 是后端的"开箱即用"加速能力；用户仅在排查具体算子兼容性问题或对比 baseline 时才需要将单项置 `False`。

### 表格二：ACLGraph 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `aclgraph_only` | `False` | 仅 ACLGraph，跳过 Pattern 融合 |
| `aclgraph_with_compile` | `False` | 先 Pattern 融合，再捕获为 ACLGraph |
| `enable_freezing` | `True` | 编译前是否执行常量折叠 |
| `safe_output_mode` | `True` | ACLGraph replay 时是否 clone 输出 |
| `graph_log_url` | `None` | 调试用 graph transform 日志 URL |

**逐行解读**：
- `aclgraph_only` (默认 `False`)：纯 ACLGraph 模式；跳过 Pattern 融合步骤，适合需要保留未融合基线以做对照、或融合 Pattern 与捕获不兼容的场景。
- `aclgraph_with_compile` (默认 `False`)：融合 + 捕获双开模式；这是生产部署最常用的最高加速档；与 `aclgraph_only` 互斥，优先级更高。
- `enable_freezing` (默认 `True`)：编译前对常量进行折叠（constant folding）；可减少捕获图中的常量节点，提升捕获与 replay 效率。
- `safe_output_mode` (默认 `True`)：replay 时对输出做 clone；防止多帧复用同一 buffer 造成数据被覆盖，建议生产环境保持开启。
- `graph_log_url` (默认 `None`)：调试钩子；用于在指定 URL/路径输出 graph transform 日志，配合 `mindie_sd_backend.py` 中的日志模块定位 Pattern 失效原因。
- 默认值整体偏保守（两个核心开关均为 `False`），说明用户必须显式启用 ACLGraph 相关选项才能获得该层加速。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与核心算子层的关系**：本文档的 `CompilationConfig.fusion_patterns` 中列举的五类 Pattern（RMSNorm、RoPE、AdaLayerNorm、fastGELU、Mul+Add）都对应 `core_layers.md#融合算子` 章节中描述的昇腾融合算子实现；本文档只说明开关位置，具体算子的 API/性能数据见 `core_layers.md`。

- **与后端实现的关系**：所有 Pattern 匹配与 graph transform 的实际逻辑位于 [`mindiesd/compilation/mindie_sd_backend.py`](../../../mindiesd/compilation/mindie_sd_backend.py)；该文件同时定义了日志模块，开启后能观察到 Pattern 使能前后的图变化情况，是问题定位的关键入口。

- **与端到端示例的关系**：文档末尾给出 [FLUX.1-dev 模型推理优化指南](../../../examples/cache-dit/FLUX.1-dev.md) 作为完整落地参考，演示了 `MindieSDBackend()` 与 Cache-DiT DBCache 在单卡 FLUX.1-dev 上的组合使用方法，包括优化前后对比、依赖安装、效果验证和可运行脚本。

- **与上游 PyTorch 的关系**：当本文档内置的定位手段不够用时，建议参考 [PyTorch `torch.compile` 官方文档](https://docs.pytorch.org/docs/main/generated/torch.compile.html)；本文档明确不提供 `graph.update` 接口（该接口主要用于 LLM 场景动态注入 attention metadata，与 SD 场景无关）。

---

## 【使用方法】

### 启用入口（三种等价方式）

```python
# 方式一：对 transformer 整体 compile
pipe = FluxPipeline.from_pretrained(...)
transformer = torch.compile(pipe.transformer, backend=MindieSDBackend())
setattr(pipe, "transformer", transformer)

# 方式二：对 Module 使用装饰器
@torch.compile(backend=MindieSDBackend())
class FluxSingleTransformerBlock(nn.Module):

# 方式三：对 forward 函数使用装饰器
class FluxSingleTransformerBlock(nn.Module):
    @torch.compile(backend=MindieSDBackend())
    def forward(...):
```

### 控制 Pattern 融合开关

```python
from mindiesd.compilation import CompilationConfig

CompilationConfig.fusion_patterns.enable_rms_norm = False
CompilationConfig.fusion_patterns.enable_rope = False
CompilationConfig.fusion_patterns.enable_adalayernorm = False
CompilationConfig.fusion_patterns.enable_fast_gelu = False
CompilationConfig.fusion_patterns.enable_mul_add = False
```

### 启用 ACLGraph 加速

```python
from mindiesd.compilation import CompilationConfig

CompilationConfig.aclgraph_with_compile = True
# 之后调用 torch.compile(..., backend=MindieSDBackend()) 即自动启用
```

### 变长输入适配

```python
max_len = 512
model = torch.compile(transformer, backend=MindieSDBackend())
_ = model(torch.randn(max_len, dim, device="npu"))  # 触发捕获

for audio_chunk in chunks:
    actual_len = audio_chunk.shape[0]
    padded = torch.nn.functional.pad(audio_chunk, (0, 0, 0, max_len - actual_len))
    output = model(padded)[:actual_len]
```

### 配置时机与问题定位

- `CompilationConfig` 必须在 `torch.compile()` **之前**完成配置；
- 通过 `MINDIE_LOG_LEVEL=debug` 开启日志模块（定义于 `mindie_sd_backend.py`），可观察 Pattern 匹配数量与图变化；
- 通过控制 `torch.compile` 的作用范围（整体 vs 单 Module vs 单 forward）缩小问题定位范围；
- benchmark 需去除首次预热（含最多 8 次编译尝试）耗时。
