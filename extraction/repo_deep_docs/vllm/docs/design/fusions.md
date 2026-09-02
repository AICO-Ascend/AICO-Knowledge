# Fusion torch.compile passes

> 仓 `vllm` · 路径 `docs/design/fusions.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/fusions.md

# vllm/docs/design/fusions.md 深度解读

## 【定位】
本文档系统阐述 vLLM 通过 `torch.compile` Inductor 自定义 Pass 在编译期对模型算子/通信做的 kernel fusion 能力清单与开关配置,把"优化"从模型定义中剥离,使上层模型代码不破坏 layer abstraction,同时给出每种 fusion 的默认值、性能区间、平台/精度支持矩阵及命令行/Python 启用方式,作为 vLLM 编译栈与性能调优的速查手册。

## 【技术要点】

1. **Fusion 控制入口统一**:所有 fusion 均通过 `PassConfig`(嵌套在 `CompilationConfig` 下)的字段控制,并随 `optimization_level`(O1/O2)自动启用,与模型代码解耦。
2. **AllReduce + RMSNorm fusion**(`fuse_allreduce_rms`):将 AllReduce 与 RMSNorm(以及可选 residual_add、quant)融合;默认在 O2 的 Hopper/Blackwell + TP>1 场景生效,E2E 提速 5-20%,非 Fullgraph,`num_tokens` 低时收益更明显。
3. **Attention + Quantization fusion**(`fuse_attn_quant`):把 Attention 输出直接生成 FP8/NVFP4 量化张量,支持普通 Attention 与 MLA Attention 两条入口;默认关闭,E2E 提速 3-7%,需 Fullgraph,`num_tokens` Always 适用,且对 attention backend 有依赖(并非所有后端都支持融合量化输出)。
4. **RoPE + KV-Cache Update**(`fuse_rope_kvcache`):Rotary embedding 与 KV cache write 融合;O2 时仅在 ROCm/AITER 上启用,E2E 提速 2-4%,非 Fullgraph,低 `num_tokens` 段生效。
5. **QK Norm + RoPE**(`enable_qk_norm_rope_fusion`):Q/K 的 RMSNorm 与 rotary embedding 串联融合;默认关闭,E2E 提速 2-3%,非 Fullgraph,低 `num_tokens` 段受益。
6. **Sequence Parallelism + AsyncTP GEMM-Collective 重叠**(`enable_sp` / `fuse_gemm_comms`):`enable_sp` 把 AllReduce 改写成 ReduceScatter + AllGather;`fuse_gemm_comms` 让 GEMM 与 reduce-scatter/all-gather 互相 overlap;`enable_sp` 是 AsyncTP 的前置依赖;两者均需 Fullgraph 且仅在 `num_tokens` 较大时获益,`fuse_gemm_comms` 单独看 E2E 提速 7-10%。
7. **激活/归一量化融合族**:`fuse_norm_quant`(RMSNorm + residual add → FP8/FP4 量化)、`fuse_act_quant`(SiLU+Mul → FP8/FP4 量化),都在 O1 条件性默认开启,E2E 提速 1-4%,Always `num_tokens`;ROCm 上另有 `fuse_act_padding`(Residual add + RMSNorm → padding)与 `fuse_mla_dual_rms_norm`(Paired Q+KV RMSNorm ± FP8 quant → 单 kernel)。

## 【关键机制与数据】

- **作用原理**:fusions 通过自定义 `torch.compile` Inductor Pass 注入,把跨算子的"写后读"中间张量停留在 kernel 内部,从而(原文:) 减少内存往返并把多条算子合成一次 launch;`PassConfig` 字段在 `optimization_level` 选定后自动开/关对应融合。能让 fusion 生效的两种情形是(原文:) "Inductor partition" 或 `splitting_ops=[]`,对应表格中的 "Fullgraph" 列。
- **数据流形态**:以 `fuse_allreduce_rms` 为例,链路是 `All-reduce → RMSNorm (+residual_add) (→ quant)`;以 `fuse_attn_quant` 为例,链路是 `Attention output → FP8/NVFP4 quant`;以 AsyncTP 系列为例,链路是 `GEMM → reduce-scatter / all-gather → GEMM`。
- **性能区间(原文给出的所有数字均为"E2E Speedup"指示值,依赖模型/批量/硬件)**:
  - `fuse_allreduce_rms`:5-20%(低 `num_tokens`)
  - `fuse_attn_quant`:3-7%(Always)
  - `fuse_attn_quant` (MLA):TBD(Always)
  - `fuse_rope_kvcache`:2-4%(低 `num_tokens`)
  - `enable_qk_norm_rope_fusion`:2-3%(低 `num_tokens`)
  - `fuse_gemm_comms`:7-10%(高 `num_tokens`)
  - `fuse_norm_quant`:1-4%(Always)
  - `fuse_act_quant`:1-4%(Always)
  - `fuse_act_padding`:TBD(Always)
  - `fuse_mla_dual_rms_norm`:1-2%(Always)
- **原文特别提示**:这些提速区间"严重依赖具体模型、batch size 和硬件",手工调优务必用同一用例对 fusion 开/关做实测。
- **`.num_tokens` 列**:表示 fusion 在 token 量低/高/全段都激活 —— Low 表示小 batch 段更明显,High 表示大 batch 段更明显,Always 表示不挑 batch。

## 【表格解读】

### 表 1:Quick Reference

| Fusion | `PassConfig` flag | Fused operations | Default at | E2E Speedup | Fullgraph | `num_tokens` |
| --- | --- | --- | --- | --- | --- | --- |
| [AllReduce + RMSNorm](#allreduce--rmsnorm-fuse_allreduce_rms) | `fuse_allreduce_rms` | All-reduce → RMSNorm (+residual_add) (→ quant) | O2 (Hopper/Blackwell + TP > 1) | 5-20% | No | Low |
| [Attention + Quant](#attention--quantization-fuse_attn_quant) | `fuse_attn_quant` | Attention output → FP8/NVFP4 quant | Off by default | 3-7% | Yes | Always |
| [MLA Attention + Quant](#attention--quantization-fuse_attn_quant) | `fuse_attn_quant` | MLA Attention output → FP8/NVFP4 quant | Off by default | TBD | Yes | Always |
| [RoPE + KV-Cache Update](#rope--kv-cache-update-fuse_rope_kvcache) | `fuse_rope_kvcache` | Rotary embedding → KV cache write | O2 (ROCm/AITER only) | 2-4% | No | Low |
| [QK Norm + RoPE](#qk-norm--rope-enable_qk_norm_rope_fusion) | `enable_qk_norm_rope_fusion` | Q/K RMSNorm → rotary embedding | Off by default | 2-3% | No | Low |
| [Sequence Parallelism](#sequence-parallelism-enable_sp) | `enable_sp` | AllReduce → ReduceScatter + AllGather | Off by default | Prereq for AsyncTP | Yes | High |
| [AsyncTP GEMM + collective](#asynctp-gemm--collective-overlap-fuse_gemm_comms) | `fuse_gemm_comms` | GEMM → reduce-scatter / all-gather → GEMM | Off by default | 7-10% | Yes | High |
| [RMSNorm + Quant](#rmsnorm--quantization-fuse_norm_quant) | `fuse_norm_quant` | RMSNorm (+residual add) → FP8/FP4 quant | O1 (conditional) | 1-4% | No | Always |
| [SiLU+Mul + Quant](#silumul--quantization-fuse_act_quant) | `fuse_act_quant` | SiLU+Mul activation → FP8/FP4 quant | O1 (conditional) | 1-4% | No | Always |
| [RMSNorm + Padding](#rmsnorm--padding-fuse_act_padding) | `fuse_act_padding` | Residual add + RMSNorm → padding | O1 (ROCm/AITER only) | TBD | No | Always |
| [MLA Dual RMSNorm](#mla-dual-rmsnorm-fuse_mla_dual_rms_norm) | `fuse_mla_dual_rms_norm` | Paired Q + KV RMSNorm (+ FP8 quant) → 1 kernel | O1 (ROCm/AITER only) | 1-2% | No | Always |

**逐行解读**:
- 第 1 行:`fuse_allreduce_rms` 在"集合通信+归一"边界节省一次 kernel launch 与中间张量往返;仅当 Hopper/Blackwell 且 TP>1 时 O2 自动启用;提速随 token 量减小而放大,典型区间 5-20%。
- 第 2-3 行:同一条 flag `fuse_attn_quant` 同时覆盖普通 Attention 与 MLA Attention,因为两者都把"Attention 输出"作为 quant 的输入边界;需 Fullgraph 才能在编译期看到完整融合模式;MLA 收益待测(TBD);支持列表详见 Support Matrix 的星号说明。
- 第 4 行:`fuse_rope_kvcache` 节省一次 RoPE 写回 + KV cache 写入的两段往返;仅 ROCm/AITER 路径默认随 O2 打开;非 Fullgraph,在小 `num_tokens` 时相对收益更突出(2-4%)。
- 第 5 行:`enable_qk_norm_rope_fusion` 让 Q/K RMSNorm 与 rotary 合成一核;默认关闭,需手工开启;同样偏小 batch 段。
- 第 6 行:`enable_sp` 实质上是"通信拆分"的编译期改写,把一次 AllReduce 拆成 RS+AG,为后续 GEMM-collectives overlap 铺路;它本身不直接给一个 E2E speedup,而是 AsyncTP 的前置条件(`Prereq for AsyncTP`),需 Fullgraph 且仅在 `num_tokens` 较大时划得来。
- 第 7 行:`fuse_gemm_comms` 是 7-10% 区间的核心受益者;它依赖第 6 行的 `enable_sp`(也是 AsyncTP 链路);同样需 Fullgraph 且偏向高 `num_tokens`。
- 第 8-9 行:`fuse_norm_quant` 与 `fuse_act_quant` 在 O1 上条件性默认开,二者都覆盖了"归一/激活 → 量化"最常见的写后读场景,因此 `num_tokens` Always 适用,稳态收益 1-4%。
- 第 10 行:`fuse_act_padding` 是 ROCm/AITER 专属,把 residual add + RMSNorm 与后面算子需要的 padding 合成;收益尚未定(TBD)。
- 第 11 行:`fuse_mla_dual_rms_norm` 把"Q 路径 RMSNorm"与"KV 路径 RMSNorm"合并成单 kernel(必要时再串 FP8 quant),仅 ROCm/AITER,Always `num_tokens`,1-2%。

### 表 2:Support Matrix

| Fusion | SM100 (Blackwell) | SM90 (Hopper) | SM89 (Ada) | SM80 (Ampere) | ROCm |
| --- | --- | --- | --- | --- | --- |
| `fuse_allreduce_rms` | FP16/BF16, FP8 static, NVFP4 | FP16/BF16, FP8 static | — | — | — |
| `fuse_attn_quant`\* | FP8 static\*, NVFP4\* | FP8 static\* | FP8 static\* | — | FP8 static\* |
| `fuse_attn_quant` (MLA)\* | FP8 static\*, FP8 per-group\*, NVFP4\* | FP8 static\*, FP8 per-group\* | FP8 static\*, FP8 per-group\* | — | FP8 static\* (untested) |
| `fuse_rope_kvcache` | — | — | — | — | FP16/BF16 |
| `enable_qk_norm_rope_fusion` | FP16/BF16 | FP16/BF16 | FP16/BF16† | FP16/BF16† | — |
| `enable_sp` | FP16/BF16, FP8 static† | FP16/BF16, FP8 static | FP16/BF16† | FP16/BF16† | — |
| `fuse_gemm_comms` | FP16/BF16, FP8 static† | FP16/BF16, FP8 static | FP16/BF16† | FP16/BF16† | — |
| `fuse_norm_quant` | FP8 static, FP8 per-token, FP8 per-group | FP8 static, FP8 per-token, FP8 per-group | FP8 static, FP8 per-token, FP8 per-group | — | FP8 static, FP8 per-token, FP8 per-group |
| `fuse_act_quant` | FP8 static, NVFP4 | FP8 static, FP8 per-group (128/64) | FP8 static, FP8 per-group (128/64) | — | FP8 per-group |
| `fuse_act_padding` | — | — | — | — | FP16/BF16 |
| `fuse_mla_dual_rms_norm` | — | — | — | — | BF16 |

**逐行解读**:
- 第 1 行 `fuse_allreduce_rms`:NVL/NVFP4 仅 Blackwell 才有;Hopper 只到 FP8 static;Ada/Ampere/ROCm 一律不支持。
- 第 2 行 `fuse_attn_quant`:星号代表对 attention backend 有依赖(并非所有后端都支持融合量化输出),详见下文小节;Ada 上可用 FP8 static,Ampere/ROCm 都不支持;NVFP4 仅 Blackwell。
- 第 3 行 `fuse_attn_quant` (MLA):MLA 版本在 Blackwell 上额外支持 FP8 per-group、NVFP4;Hopper/Ada 上支持 FP8 static 与 per-group;Ampere 不支持;ROCm 上"FP8 static\* (untested)" 表示实现存在但尚未完成验证。
- 第 4 行 `fuse_rope_kvcache`:全 Nvidia 平台都不列支持(`—`),仅 ROCm 上 FP16/BF16 可用 —— 与上表"O2 时仅 ROCm/AITER 默认启用"互相印证。
- 第 5-8 行(`enable_qk_norm_rope_fusion` / `enable_sp` / `fuse_gemm_comms`):这三个都是分两类标记—— `†` 表示该组合存在但当前(原文:) "仅 SM90 会自动配置",其他架构需显式设置 `PassConfig.sp_min_token_num`,并且(原文:) "SM100 还需额外设置 `VLLM_DISABLED_KERNELS=FlashInferFP8ScaledMMLinearKernel`" 才能跑通。
- 第 9 行 `fuse_norm_quant`:是覆盖最广的一档,Nvidia SM100/90/89 上 FP8(static/per-token/per-group)全开,ROCm 同步全开,只有 Ampere(`—`)不支持。
- 第 10 行 `fuse_act_quant`:Hopper/Ada 明确支持 FP8 per-group (128/64) 两种分组大小;Blackwell 额外上 NVFP4;ROCm 仅 FP8 per-group;Ampere 不支持。
- 第 11 行 `fuse_act_padding` 与第 12 行 `fuse_mla_dual_rms_norm`:都只列在 ROCm 列,与"ROCm/AITER only" 的自动启用条件一致。

## 【公式解读】

原文无公式(整篇文档没有 LaTeX、公式或伪代码公式;所谓"fused operations" 是用箭头串起来的算子名叙述,而不是数学式),故记为:**原文无公式**。

## 【关联】

- 上游/机制基础:本文的 fusions 全部以 `torch.compile` Inductor 自定义 Pass 为载体,因此相关详细机制需查阅 [torch_compile.md](torch_compile.md)。
- 启用等级:fusions 的默认开/关由 `optimization_level` 决定(O1 条件性默认 / O2 在特定硬件+TP 条件下默认 / 多数 "Off by default"),详见 [optimization_levels.md](optimization_levels.md)(文中链接两次)。
- 算子后端依赖:`fuse_attn_quant` 的实际可用性取决于当前选用的 attention backend,与 [attention_backends.md](attention_backends.md) 直接相关,文档要求读者去 attention backend 小节查"per-backend details"。
- 跟踪进展:文档给出 `fuse_attn_quant` 等仍在演进 fusion 的追踪 issue `vllm-project/vllm#36066`。
- 上下游关系链:`PassConfig`(Pass/编译期优化)→ `CompilationConfig`(`optimization_level` 与 backend 选择)→ 模型运行(via `LLM(...)`)与命令行(`vllm serve` / `vllm bench latency`)→ 算子后端(attention backend 等)。

## 【使用方法】

**Python 启用**:把 `PassConfig` 实例嵌入 `CompilationConfig.pass_config` 传给 `LLM(...)`,字段名一一对应每条 fusion;`optimization_level` 选 2 即采用 O2 默认(配合特定硬件/TP 条件自动开启部分 fusion)。原文示例:

```python
from vllm import LLM
from vllm.config import CompilationConfig, PassConfig

llm = LLM(
    model="...",
    optimization_level=2, # Default optimization level
    compilation_config=CompilationConfig(
        pass_config=PassConfig(
            fuse_norm_quant=True,
            fuse_act_quant=True,
            fuse_allreduce_rms=False,  # disable a specific fusion
        )
    ),
)
```

**命令行启用**:所有 `vllm ...` 子命令(`vllm serve`、`vllm bench latency` 等)统一通过 `-O2` 选优化等级 + `-cc.pass_config.<flag>=True|False` 单点开关 fusion。原文示例:

```bash
# Enable O2 defaults, but turn off allreduce fusion
vllm serve meta-llama/Llama-3.1-8B-Instruct -O2 -cc.pass_config.fuse_allreduce_rms=False

# 等价于更冗长写法:
vllm serve meta-llama/Llama-3.1-8B-Instruct -O2 --compilation-config '{"pass_config": {"fuse_allreduce_rms": false}}'

# 在 vllm bench 等其他子命令中同样可用:
vllm bench latency --model=meta-llama/Llama-3.1-8B-Instruct -O2 -cc.pass_config.fuse_allreduce_rms=False
```

**特殊环境变量**(原文 ‡ 标注):在非 SM90 架构启用 `enable_sp` / `fuse_gemm_comms` 时需要显式设 `PassConfig.sp_min_token_num`;SM100 启用时还需设置 `VLLM_DISABLED_KERNELS=FlashInferFP8ScaledMMLinearKernel`。
