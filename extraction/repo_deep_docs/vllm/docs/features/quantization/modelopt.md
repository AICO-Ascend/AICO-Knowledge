# NVIDIA Model Optimizer

> 仓 `vllm` · 路径 `docs/features/quantization/modelopt.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/modelopt.md

【定位】本文档解决 vLLM 如何接入、加载并部署 NVIDIA Model Optimizer (ModelOpt) 产出的量化 checkpoint (覆盖 LLM/VLM/扩散模型的 PTQ 与 QAT 场景) 的问题,系统说明 vLLM 识别的 checkpoint 格式、量化工作流、Kernel 自动选择/回退策略以及线上服务与本地测试的具体方式。

【技术要点】

- **checkpoint 检测机制**: vLLM 通过 `hf_quant_config.json` 中的 `quantization.quant_algo` 字段识别 ModelOpt 量化格式,支持的算法包括 `FP8`、`FP8_PER_CHANNEL_PER_TOKEN`、`FP8_PB_WO`/`fp8_pb_wo`、`NVFP4`、`W4A16_NVFP4`、`MXFP8`。
- **NVFP4/W4A16_NVFP4 加载参数**: 这两类 checkpoint 在 vLLM 中均通过 `quantization="modelopt_fp4"` 加载;`FP8_PB_WO` 典型为 128×128 block-scaled FP8 weight-only;`FP8` 默认为 per-tensor weight scale,可选静态 activation scale;`FP8_PER_CHANNEL_PER_TOKEN` 为 per-channel weight scale + 动态 per-token activation 量化。
- **MXFP8 加载参数**: 通过 `quantization="modelopt_mxfp8"` 加载;在 SM100 系列 GPU 上若 activations 为 BF16,需用 `--linear-backend flashinfer_trtllm` 选用 FlashInfer 的 TensorRT-LLM GEMM 后端。
- **NVFP4 Kernel 自动选择与回退**: 加载时 vLLM 按平台可用后端自动选择 GEMM kernel,候选为 `cutlass`、`flashinfer_cutlass`、`flashinfer_cutedsl`、`flashinfer_trtllm`、`flashinfer_cudnn`、`marlin`;若平台无原生 FP4 GEMM kernel,自动回退到 weight-only (W4A16) 由 Marlin 执行并打 warning,可能降低计算密集型吞吐;可用 `--linear-backend` 显式覆盖自动选择 (取代已废弃的 `VLLM_NVFP4_GEMM_BACKEND`);`W4A16_NVFP4` 的 `auto` 当前固定选 Marlin;BF16 activation 模型可显式 `--linear-backend flashinfer_cutedsl`。
- **PTQ 量化流程**: 调用 `modelopt.torch.quantization` (`mtq`) 的 `FP8_DEFAULT_CFG` 等 config,定义 `forward_loop(model)` 在 calib_set 上做 calibration,经 `mtq.quantize(model, config, forward_loop)` 就地替换量化模块;在 `torch.inference_mode()` 下用 `modelopt.torch.export.export_hf_checkpoint` 导出为可被 vLLM 加载的 HF 风格目录。
- **部署与服务**: Python 侧用 `vllm.LLM(model=..., quantization="modelopt", trust_remote_code=True)` 加载 (如 `nvidia/Llama-3.1-8B-Instruct-FP8`);HTTP 侧用 `vllm serve <path_to_exported_checkpoint> --quantization modelopt --host 0.0.0.0 --port 8000` 启动 OpenAI 兼容服务。
- **本地测试门控**: vLLM 的 ModelOpt 单元测试默认在 CI 中跳过,通过环境变量 `VLLM_TEST_MODELOPT_FP8_PC_PT_MODEL_PATH` 与 `VLLM_TEST_MODELOPT_FP8_PB_WO_MODEL_PATH` 指定本地 checkpoint 路径后,可用 `pytest -q tests/quantization/test_modelopt.py` 运行。

【关键机制与数据】

- 原文: checkpoint 识别路径为 `hf_quant_config.json`,关键字段是 `quantization.quant_algo`;`FP8_PB_WO` 在文中明确 "(typically 128×128 blocks)"。
- 原文: NVFP4 在加载时由 vLLM 在 CUTLASS、FlashInfer、Marlin 等后端之间自动挑选 GEMM kernel;无原生 FP4 GEMM 时回退 weight-only (W4A16) 经 Marlin 执行并产生 throughput 损失警告。
- 原文: NVFP4/W4A16_NVFP4 与 MXFP8 在 vLLM 侧分别使用统一加载字符串 `"modelopt_fp4"` 与 `"modelopt_mxfp8"`。
- 原文: PTQ 工作流数据流为 `HF 模型 → mtq.quantize (FP8_DEFAULT_CFG + forward_loop + calib_set) → export_hf_checkpoint (torch.inference_mode) → HF 风格量化目录 → vLLM LLM(quantization="modelopt") 加载 → vllm serve --quantization modelopt`。
- 原文: `W4A16_NVFP4` 的 `auto` 当前固定返回 Marlin;`--linear-backend` 取代已废弃的环境变量 `VLLM_NVFP4_GEMM_BACKEND`。
- 原文: 文档未提供具体吞吐数字、延迟数字或模型规模参数,因此本节不引述未在原文中出现的性能数据。

【表格解读】原文无表格。

【公式解读】原文无公式。

【关联】

- 与上游 **NVIDIA/Model-Optimizer** 仓库耦合:本文档列出依赖 (`pip install nvidia-modelopt`),并引用其 PTQ 示例脚本路径 `examples/llm_ptq`;所有 vLLM 侧的 `quantization="modelopt*"` 字符串都依赖 ModelOpt 产出的 `hf_quant_config.json` 与 `export_hf_checkpoint` 导出产物,因此 ModelOpt 是 vLLM 这条量化路径的上游生态。
- 与 vLLM **Kernel 选择 / 线性后端**子系统耦合:文档将 NVFP4 的 GEMM kernel 选择逻辑指向 `KernelConfig` (在 [Engine Arguments](../../configuration/engine_args.md) 页面),并通过 `vllm serve --help=KernelConfig` 暴露 `--linear-backend` 取值 (含 `cutlass`/`flashinfer_*`/`marlin`);MXFP8+BF16 在 SM100 上亦受同一参数控制。
- 与 vLLM **OpenAI 兼容 Server** 耦合:文档给出的 `vllm serve ... --quantization modelopt --host 0.0.0.0 --port 8000` 复用 vLLM 通用 HTTP 服务入口,提示量化方式仅作为 `quantization` 参数注入,服务接口与未量化模型一致。
- 与 vLLM **量化测试**体系耦合:文档末尾的环境变量 (`VLLM_TEST_MODELOPT_FP8_PC_PT_MODEL_PATH`、`VLLM_TEST_MODELOPT_FP8_PB_WO_MODEL_PATH`) 与 `tests/quantization/test_modelopt.py` 表明 ModelOpt 路径有独立测试门控,需本地 checkpoint 才执行。
- 与 vLLM 中 **QAT** 路径的关联:导语提及 QAT 能力,但正文未给出独立 QAT 章节或命令,属于"声明支持但未在本特性文档展开"的关系。

【使用方法】

- 安装依赖: `pip install nvidia-modelopt`。
- Python 加载 (示例 `nvidia/Llama-3.1-8B-Instruct-FP8`): `LLM(model=model_id, quantization="modelopt", trust_remote_code=True)`。
- NVFP4 / W4A16_NVFP4 加载: `quantization="modelopt_fp4"`。
- MXFP8 加载: `quantization="modelopt_mxfp8"`。
- 启动 OpenAI 兼容服务: `vllm serve <path_to_exported_checkpoint> --quantization modelopt --host 0.0.0.0 --port 8000`。
- 覆盖 NVFP4 GEMM 后端 (取代已废弃的 `VLLM_NVFP4_GEMM_BACKEND`): `--linear-backend {cutlass|flashinfer_cutlass|flashinfer_cutedsl|flashinfer_trtllm|flashinfer_cudnn|marlin}`;MXFP8+BF16 on SM100 显式选用 `--linear-backend flashinfer_trtllm`;BF16 activation 显式选 FlashInfer CuTe-DSL 用 `--linear-backend flashinfer_cutedsl`;`W4A16_NVFP4` 的 `auto` 当前选 Marlin。
- PTQ 量化 (Python): 使用 `modelopt.torch.quantization as mtq` 的 `FP8_DEFAULT_CFG` 等 config,定义 `forward_loop(model)`,调用 `mtq.quantize(model, config, forward_loop)`;在 `torch.inference_mode()` 下用 `modelopt.torch.export.export_hf_checkpoint(model, export_dir)` 导出。
- 本地测试: 设置 `VLLM_TEST_MODELOPT_FP8_PC_PT_MODEL_PATH` 与 `VLLM_TEST_MODELOPT_FP8_PB_WO_MODEL_PATH` 指向本地 checkpoint,执行 `pytest -q tests/quantization/test_modelopt.py`;CI 默认跳过。
