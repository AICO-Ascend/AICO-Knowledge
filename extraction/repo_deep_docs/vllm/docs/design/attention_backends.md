# Attention Backend Feature Support

> 仓 `vllm` · 路径 `docs/design/attention_backends.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/attention_backends.md

# 一体化深度解读: vLLM Attention Backend Feature Support

## 【定位】
本文档解决「如何为 vLLM 选择 Attention 后端(attention backend),以及各后端在何种硬件/模型/特性配置下可用」的问题,提供自动选择的手动/自动机制、CUDA 平台下后端优先级,并通过自动生成的特性矩阵展示各后端的能力边界。

---

## 【技术要点】

1. **两种 CLI 后端指定方式(互斥)**:
   - 简单方式:`--attention-backend FLASH_ATTN`
   - 结构化方式:`--attention-config.backend` 或 `-ac.backend`,支持点号、JSON 等多种写法(如 `--attention-config '{"backend": "FLASH_ATTN"}'`)。原文明确二者"mutually exclusive"。

2. **Python API 两种等价写法**:通过 `AttentionConfig(backend=AttentionBackendEnum.FLASH_ATTN)` 传给 `LLM`,或直接用 `attention_backend="FLASH_ATTN"` 字符串参数;示例模型为 `Qwen/Qwen3-0.6B`。

3. **后端选择的双模式**:手动模式下,配置不兼容时抛出 `ValueError` 并给出具体原因(如 `compute capability not supported`);自动模式下,按优先级顺序遍历(1 = 最高),首个兼容后端即被选中,全部不兼容则列出所有失败原因。

4. **优先级表覆盖三类 Attention 形态**:Standard Attention(MHA/MQA/GQA)、MLA Attention(DeepSeek-style)、MLA V4 Sparse(DeepSeek V4 稀疏),标准与 MLA 的优先级表由 `gen:priority-standard` / `gen:priority-mla` 占位符在文档构建时自动生成。

5. **平台分支**:ROCm 与 CPU 平台有独立选择逻辑,本文仅详述 CUDA;另外 MLA 在 FP8 KV cache 下**总是优先** `FLASHINFER_MLA_SPARSE`,BF16 KV cache 下,query-head 数量 ≤ 16 时优先 `FLASHINFER_MLA_SPARSE`,否则优先 `FLASHMLA_SPARSE`。

6. **FlashAttention 4(FA4)在 Blackwell 的硬约束**:`head_size=256` 时使用专用 FA4 kernel,要求 KV cache block size = 128;若 `--block-size` 固定且非 128 倍数则 FlashAttention 直接出局(显式指定时变 error);不支持 logit soft cap、attention sinks、mm_prefix/R-SWA masking、DCP、windowed encoder attention,触发时透明回退到 FA2。

---

## 【关键机制与数据】

**后端验证流程(原文)**:`AttentionBackend.validate_configuration()` 检查项涵盖 model dtype、head size、compute capability 等。配置与所选后端不兼容时,`Selected backend FLASHMLA is not valid for this configuration. Reason: ['compute capability not supported']`。

**MLA 预填自动选择顺序(原文)**:
- 默认:先试 FlashAttention。
- Blackwell(SM100)兜底序:TRT-LLM Ragged → FlashInfer → TokenSpeed MLA。
- 当 `(qk_nope_head_dim=192, qk_rope_head_dim=64, v_head_dim=256)` 时,TRT-LLM Ragged 在 FlashAttention 之前尝试。
- 其他 GPU:仅考虑 FlashAttention。

**DeepSeek V4 稀疏 MLA 流水线(原文)**:compressor + SWA + indexer,256-token 块,head 512;NVIDIA 上 SM12x 默认 `FLASHINFER_MLA_SPARSE_DSV4`,其他支持架构默认 `FLASHMLA_SPARSE_DSV4`。

**MiniMax M3 Lightning Indexer(原文)**:block-sparse GQA 后端;indexer 对 KV 块打分,选取 top-k(加上固定 init/local 块),attention 只在这些块上计算;index keys 单独存放于 side cache。该后端**不参与**自动优先级列表,由模型直连。

**FlashInfer Native vs XQA/trtllm-gen(原文)**:`†` 注释说明 Native 为常规 FlashInfer 路径,XQA 是 SM90 decode 路径(经 FlashInfer 的 TRTLLM decode API 暴露),trtllm-gen 用于 SM100 且支持 sinks;可通过 `--attention-config.use_trtllm_attention=0` 关闭 XQA/trtllm-gen。

**FlashAttention 版本(原文)**:通过 `--attention-config.flash_attn_version=2/3/4` 指定;SM100+(Blackwell) 默认 FA4,SM90(Hopper) 默认 FA3,其他默认 FA2。

---

## 【表格解读】

**重要说明**:原文除「Legend 表」外,其余所有特性矩阵与优先级表均使用 mkdocs 占位符(`--8<-- "gen:priority-standard"`, `--8<-- "gen:table-standard"`, `--8<-- "gen:table-minimax"`, `--8<-- "gen:table-mla-prefill"`, `--8<-- "gen:table-mla-decode"`, `--8<-- "gen:table-mla-v4-decode"`)标记,**实际表格内容由 `docs/mkdocs/gen_files/generate_attention_backends.py` 在文档构建时**基于 `AttentionBackend.validate_configuration()` 的检查结果**自动生成**。因此文档原文中并不存在渲染完毕的完整表格,只有列定义。

下方逐字还原原文中**唯一完整呈现**的 Legend 表:

| Column | Description |
| ------ | ----------- |
| **Dtypes** | Supported model data types (fp16, bf16, fp32) |
| **KV Dtypes** | Supported KV cache data types (`auto`, `fp8`, `fp8_e4m3`, etc.) |
| **Block Sizes** | Supported KV cache block sizes (%N means multiples of N) |
| **Head Sizes** | Supported attention head sizes |
| **Sink** | Attention sink support (for StreamingLLM) |
| **Non-Causal** | Non-causal (bidirectional) attention support for decoder models |
| **Sparse** | Sparse attention support (MLA only) |
| **MM Prefix** | Multimodal prefix full attention support |
| **DCP** | Decode Context Parallelism support (`--decode-context-parallel-size`) |
| **Attention Types** | Supported attention patterns (Decoder, Encoder, Enc-Dec) |
| **Compute Cap.** | Required CUDA compute capability (N/A for non-CUDA backends) |

逐行解读:
- **Dtypes / KV Dtypes**:模型权重与 KV cache 数据类型;KV cache 用 `fp8_e4m3` 这类具体量化格式,模型侧只列浮点三件套(fp16/bf16/fp32)。
- **Block Sizes**:`%N` 表示「N 的倍数」,而不是任意整数;用于约束 PagedAttention 的页大小。
- **Head Sizes**:attention head 维度,常见如 64、128、256;head_size=256 在 FA4 上有专属路径(见技术要点 6)。
- **Sink**:StreamingLLM 风格的 attention sink;trtllm-gen 在 SM100 上支持,FA4 在 head_size=256 时不支持。
- **Non-Causal**:解码器模型支持双向注意力,多用于 prefix/prompt 部分。
- **Sparse**:仅对 MLA 有意义(对应 MLA 稀疏变体)。
- **MM Prefix**:多模态 prefix 需要 full attention(而非因果掩码)。
- **DCP**:与 `--decode-context-parallel-size` 命令对应,表示是否参与 decode 阶段的上下文并行。
- **Attention Types**:区分 Decoder(自回归)、Encoder(双向,如 BERT)、Encoder-Decoder(如 T5)。
- **Compute Cap.**:CUDA Compute Capability(如 8.0/8.9/9.0/10.0/12.0);非 CUDA 后端显示 N/A。

**符号约定(原文)**:`✅` = Supported,`❌` = Not supported。

---

## 【公式解读】

原文无公式。文档未出现任何 LaTeX 公式或伪代码表达式;所提及的"决策逻辑"(如优先级排序、版本默认、稀疏选择)均以自然语言加 `‡` / `*` 脚注形式呈现。

---

## 【关联】

文档与以下模块/特性存在显式关联(基于文中提及):

- **`AttentionBackend.validate_configuration()`**:所有特性矩阵的数据来源,位于后端注册表;同时也是手动选择触发的不兼容错误来源。
- **`AttentionConfig`**(`vllm.config`):Python API 的入口对象,与 `LLM` 类的 `attention_config` 参数绑定,等价于 CLI 的 `--attention-config`。
- **`AttentionBackendEnum`**(`vllm.v1.attention.backends.registry`):枚举所有可用后端名的中心注册点;CLI 上 `--attention-backend FLASH_ATTN` 中的字符串即来自此枚举。
- **`-ac.mla_prefill_backend`**:MLA 预填专用配置路径,与 `-ac.backend` 形成 split(MLA 预填 vs MLA/Standard decode 共用 `-ac.backend`)。
- **`-ac.backend`** 在 MLA decode 中复用为标准后端选择路径;而 DeepSeek V4 sparse MLA 的 decode 则单独走 `--attention-backend=`(`FLASHMLA_SPARSE_DSV4` / `FLASHINFER_MLA_SPARSE_DSV4`),命名空间分离。
- **`--attention-config.flash_attn_version`**:与 `--attention-config.use_trtllm_attention` 共同构成对 FlashAttention 与 FlashInfer 内部分支的细粒度控制。
- **`--block-size`**:与 FlashAttention 的 block size 约束联动(FA4 head_size=256 要求 128)。
- **`--decode-context-parallel-size`**:DCP 列所对应的运行时参数。
- **StreamingLLM / attention sinks**:`Sink` 列对应能力。
- **多模态 prefix / mm_prefix / R-SWA masking**:`MM Prefix` 列对应能力。
- **`docs/mkdocs/gen_files/generate_attention_backends.py`**:文档构建期负责把 `AttentionBackend` 注册表渲染成 markdown 表格的脚本;**注:文末未提供其他内部链接(原文标注"内部链接: (无)")**,以上关联均来自文档正文中的代码/参数引用。

---

## 【使用方法】

**CLI 选择后端(原文)**:
```bash
# 简单方式
vllm serve <model> --attention-backend FLASH_ATTN

# 结构化方式(点号)
vllm serve <model> --attention-config.backend FLASH_ATTN
vllm serve <model> -ac.backend FLASH_ATTN

# 结构化方式(JSON)
vllm serve <model> --attention-config '{"backend": "FLASH_ATTN"}'
vllm serve <model> -ac '{"backend": "FLASH_ATTN"}'
```

**Python API(原文)**:
```python
from vllm import LLM
from vllm.config import AttentionConfig
from vllm.v1.attention.backends.registry import AttentionBackendEnum

llm = LLM(
    model="Qwen/Qwen3-0.6B",
    attention_config=AttentionConfig(backend=AttentionBackendEnum.FLASH_ATTN),
)
# 或等价:
llm = LLM(model="Qwen/Qwen3-0.6B", attention_backend="FLASH_ATTN")
```

**MLA 预填(原文)**:`-ac.mla_prefill_backend=<BACKEND>`,例如 `-ac.mla_prefill_backend=FLASH_ATTN`;不指定则运行时按硬件自动选。

**MLA decode(原文)**:复用 `-ac.backend=<BACKEND>`,例如 `-ac.backend=FLASHMLA`。

**DeepSeek V4 sparse MLA decode(原文)**:`--attention-backend=<BACKEND>`,例如 `--attention-backend=FLASHMLA_SPARSE_DSV4` / `FLASHINFER_MLA_SPARSE_DSV4`。

**FlashAttention 版本(原文)**:`--attention-config.flash_attn_version=2|3|4`。

**关闭 XQA / trtllm-gen(原文)**:`--attention-config.use_trtllm_attention=0`。

**未自动选后端时**:不传任何后端参数,vLLM 按优先级表自动挑首个兼容后端;ROCm/CPU 的选择逻辑需查阅对应平台文档(原文未在本页展开)。
