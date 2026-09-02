# AMD Quark

> 仓 `vllm` · 路径 `docs/features/quantization/quark.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/quark.md

# AMD Quark 集成文档深度解读

## 【定位】

这篇文档描述 vLLM 如何集成 AMD Quark 量化工具链,提供在 AMD GPU 上运行大语言模型量化推理的端到端工作流(从环境安装、校准数据准备、量化配置、模型导出到 vLLM 加载与 `lm_eval` 评估),重点演示 FP8 per-tensor + AutoSmoothQuant 算法 + KV-cache FP8 量化的完整范例。

---

## 【技术要点】

1. **工具链定位**:Quark 是 AMD 提供的灵活量化工具包,支持 weight / activation / kv-cache 三类张量量化,以及 AWQ、GPTQ、Rotation、SmoothQuant 等前沿算法,产出可在 AMD GPU 上 vLLM 中高性能运行的量化模型。
2. **安装依赖**:三条 pip 命令:`pip install amd-quark`(主量化工具);`pip install vllm "lm-eval[api]>=0.4.12"`(推理与评估);此外依赖 Transformers 加载模型、PyTorch Dataloader 加载校准数据。
3. **五步量化流程**:Load Model → Prepare Calibration Dataloader → Set Quantization Config → Quantize & Export → Evaluation in vLLM。
4. **量化配置关键参数**(原文 Llama-2-70b-chat-hf 范例):
   - `MAX_SEQ_LEN = 512`
   - `BATCH_SIZE = 1`、`NUM_CALIBRATION_DATA = 512`
   - 校准数据集:`mit-han-lab/pile-val-backup` 的 `validation` split
   - 量化 spec:`FP8E4M3PerTensorSpec`,`observer_method="min_max"`,`is_dynamic=False`(静态量化)
   - 算法:`AutoSmoothQuant`,配置文件路径为 `examples/torch/language_modeling/llm_ptq/models/llama/autosmoothquant_config.json`
   - KV-cache 量化目标层名模式:`["*k_proj", "*v_proj"]`
   - 排除层:`["lm_head"]`
5. **导出格式**:必须使用 HuggingFace `safetensors` 格式,导出目录命名遵循 `Llama-2-70b-chat-hf-w-fp8-a-fp8-kvcache-fp8-pertensor-autosmoothquant` 这样的语义化规则(权重-FP8、激活-FP8、KV-cache-FP8、per-tensor、AutoSmoothQuant)。
6. **vLLM 加载与评估**:`LLM(..., kv_cache_dtype="fp8", quantization="quark")` 直接读取量化模型;亦可用 `lm_eval --model vllm --model_args ... --tasks gsm8k` 评估准确率。

---

## 【关键机制与数据】

**工作原理与数据流**(根据原文 5 步流程梳理):

- **Step 1**:用 `transformers.AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto", dtype="auto")` 以 `meta-llama/Llama-2-70b-chat-hf` 为例加载模型,tokenizer 的 `pad_token` 复用 `eos_token`。
- **Step 2**:从 pile-val-backup 取前 512 条文本,用 tokenizer 做 `padding/truncation/max_length=512` 处理,送入 `torch.utils.data.DataLoader(batch_size=1, drop_last=True)`,作为校准数据。
- **Step 3**:构造分层量化配置——全局对 input/weight 施加 FP8 per-tensor 静态 spec,对 `*k_proj` 与 `*v_proj` 层额外叠加 KV-cache 输出量化 spec;再叠加 AutoSmoothQuant 算法配置(从 JSON 文件载入),排除 `lm_head` 层。
- **Step 4**:`ModelQuantizer.quantize_model(model, calib_dataloader)` 执行量化 → `quantizer.freeze(model)` 冻结量化参数 → `ModelExporter.export_safetensors_model(...)` 以 HuggingFace safetensors 格式写出,导出时通过 `JsonExporterConfig` 并设置 `kv_cache_group = ["*k_proj", "*v_proj"]` 保留 KV-cache 量化元信息。
- **Step 5**:vLLM 通过 `quantization="quark"` 后端解析量化模型,`kv_cache_dtype="fp8"` 显式启用 KV-cache FP8 存储;推理通过 `SamplingParams(temperature=0.8, top_p=0.95)` 控制采样;`lm_eval` 用同一 `pretrained=`、`kv_cache_dtype='fp8'`、`quantization='quark'` 参数串在 gsm8k 上评估。

**性能/精度数据**:原文未提供具体的加速比、吞吐量、显存节省或精度下降数字,仅以定性表述提到"有效降低内存与带宽占用、加速计算并提升吞吐量,且精度损失极小"(mininal accuracy loss)。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档正文未显式列出其他内部 `.md` 链接;根据任务上下文提示的内部链接信息,本文档关联到 `online.md`(共两处,推测对应文档站点的"在线推理"或"在线部署"等通用说明页),可视为 vLLM 主文档体系中量化相关特性的上游/平行条目。此外,文档通过外链强依赖以下上游生态:
- **Quark 官方文档**(`quark.docs.amd.com/latest`):涵盖安装、config 描述、calibration 数据集、HuggingFace 导出、Python API 示例、`quantize_quark.py` 脚本说明。
- **Transformers**(`huggingface.co/docs/transformers`):模型与 tokenizer 加载。
- **PyTorch Dataloader**(`pytorch.org/tutorials/.../data_tutorial.html`):校准数据加载。
- **`datasets.load_dataset`**(HuggingFace):pile-val-backup 数据来源。
- **`lm-evaluation-harness`**:`lm_eval --model vllm` 评估入口。
- **vLLM `LLM` entrypoint**:以 `quantization="quark"` 作为量化后端标识接入,与 vLLM 自身量化框架的其它后端(如 GPTQ、AWQ、bitsandbytes 等)并列。

从 Quark 的量化算法角度,本文档示例的 AutoSmoothQuant 与上文提到的 AWQ、GPTQ、Rotation、SmoothQuant 属于同一算法家族中的不同实现选择,文中通过 `examples/torch/language_modeling/llm_ptq/models/<model>/<algo>_config.json` 这一相对路径约定统一引用,可视为与 vLLM 量化 backend 的算法可插拔契约。

---

## 【使用方法】

**安装**:
```bash
pip install amd-quark
pip install vllm "lm-eval[api]>=0.4.12"
```

**Python API 五步流程(以 Llama-2-70b-chat-hf + FP8 per-tensor + AutoSmoothQuant 为例)**:

- **Step 1 加载模型**:`AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto", dtype="auto")`;tokenizer 复用 `eos_token` 作 `pad_token`。
- **Step 2 准备校准数据**:`BATCH_SIZE=1`、`NUM_CALIBRATION_DATA=512`、源数据 `mit-han-lab/pile-val-backup` validation split、`max_length=512`、`drop_last=True`。
- **Step 3 量化配置**:`FP8E4M3PerTensorSpec(observer_method="min_max", is_dynamic=False).to_quantization_spec()` → `QuantizationConfig(input_tensors=..., weight=...)` 全局;KV-cache 层(`["*k_proj", "*v_proj"]`)叠加 `output_tensors=KV_CACHE_SPEC`;算法从 `autosmoothquant_config.json` 载入;`exclude=["lm_head"]`。
- **Step 4 量化与导出**:`ModelQuantizer(quant_config).quantize_model(model, calib_dataloader)` → `.freeze(model)` → `ModelExporter(config=ExporterConfig(json_export_config=JsonExporterConfig(...).kv_cache_group=["*k_proj","*v_proj"]), export_dir=...)` → `exporter.export_safetensors_model(freezed_model, quant_config=quant_config, tokenizer=tokenizer)`(在 `torch.no_grad()` 下)。
- **Step 5 vLLM 推理与评估**:
```python
llm = LLM(
    model="Llama-2-70b-chat-hf-w-fp8-a-fp8-kvcache-fp8-pertensor-autosmoothquant",
    kv_cache_dtype="fp8",
    quantization="quark",
)
outputs = llm.generate(prompts, SamplingParams(temperature=0.8, top_p=0.95))
```

**`lm_eval` 评估命令**:
```bash
lm_eval --model vllm \
  --model_args pretrained=Llama-2-70b-chat-hf-w-fp8-a-fp8-kvcache-fp8-pertensor-autosmoothquant,kv_cache_dtype='fp8',quantization='quark' \
  --tasks gsm8k
```

**Quark 一键脚本(`quantize_quark.py`,原文末尾示例被截断,可见部分)**:
```bash
python3 quantize_quark.py --model_dir meta-llama/Llama-2-70b-chat-hf \
                          --output_dir /path/to/output \
                          --quant_scheme w_fp8_a_fp8 \
                          --kv_cache_dtype fp8 \
                          --quant_algo autosmoothquant \
                          --num_c
```
> 注:原文此行末尾出现 `--num_c` 后即被截断(原文:"--num_c"),其后是否包含 `--num_calibration_data` 等参数原文未给出,不可臆造。

**关键配置项汇总**(原文给出):
| 维度 | 取值/参数 |
|---|---|
| 量化算法 | AutoSmoothQuant(配置文件 `autosmoothquant_config.json`) |
| 量化精度 | FP8(E4M3) |
| 量化粒度 | per-tensor |
| 量化模式 | 静态(`is_dynamic=False`,`observer_method="min_max"`) |
| 量化目标张量 | weight / activation / kv-cache output |
| KV-cache 目标层模式 | `*k_proj`、`*v_proj` |
| 排除层 | `lm_head` |
| 模型导出格式 | HuggingFace `safetensors` |
| vLLM 量化后端标识 | `quantization="quark"` |
| vLLM KV-cache dtype | `kv_cache_dtype="fp8"` |
| 采样参数 | `temperature=0.8`、`top_p=0.95` |
