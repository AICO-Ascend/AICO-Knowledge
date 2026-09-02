# DeepSeek-OCR-2

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/DeepSeekOCR2.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/DeepSeekOCR2.md

# DeepSeek-OCR-2 文档深度解读

## 【定位】

本文档解决的是如何在 vllm-ascend 平台上部署、验证与评测 `DeepSeek-OCR-2` 多模态 OCR 模型的问题,系统性地给出了从环境准备、容器化安装、单节点在线部署、功能验证、精度评测到性能调优的完整操作指南。

---

## 【技术要点】

1. **版本基线**: `DeepSeek-OCR-2` 模型首次在 `vllm-ascend:v0.16.0` 中获得支持,且在该版本及之后可稳定运行。
2. **硬件形态**: 推荐在 **1 Atlas 800 A2**(单节点)上完成部署,多节点部署官方建议"不推荐",Prefill-Decode 解分离"不需要"。
3. **模型权重**: 来自 [HuggingFace deepseek-ai/DeepSeek-OCR-2](https://huggingface.co/deepseek-ai/DeepSeek-OCR-2),推荐存放到多节点共享目录 `/root/.cache/`。
4. **容器镜像**: `m.daocloud.io/quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`,区分 A2 系列(8 卡 davinci0–7)与 A3 系列(16 卡 davinci0–15)的设备映射。
5. **关键环境变量**:`VLLM_USE_V1=1`、`TOKENIZERS_PARALLELISM=false`、`PYTORCH_NPU_ALLOC_CONF="expandable_segments:True"`、`TASK_QUEUE_ENABLE=1`。
6. **启动参数**: `--tensor-parallel-size 1`、`--port 1055`、`--max_model_len 8192`、`--no-enable-prefix-caching`、`--gpu-memory-utilization 0.8`、`--mm-processor-cache-gb 0`;`additional-config` 含 `weight_nz_mode=0`、`enable_cpu_binding=true`、`multistream_overlap_shared_expert=true`、`fuse_qknorm_rope=false`。

---

## 【关键机制与数据】

### 工作机制

- **kv_cache 容量计算(原文)**: `--gpu-memory-utilization` * HBM size − peak GPU memory usage。在 profile run(warm-up)阶段 vLLM 会以 `--max-num-batched-tokens` 输入记录峰值显存,然后据此倒推可用 kv_cache。该值越高,可用 kv_cache 越多,但过高会在实际推理中因 EP 负载不均等原因触发 OOM,默认值为 `0.9`。
- **prefix caching 控制(原文)**: 通过 `--no-enable-prefix-caching` 关闭,若需启用则移除该参数。
- **多模态输入路径(原文)**: `--allowed-local-media-path /` 允许任意本地媒体路径作为输入;`--mm-processor-cache-gb 0` 设置多模态处理器缓存大小为 0 GB。

### 性能与精度数据(原文)

- **精度(Accuracy)**: 在 `1 Atlas 800 A2` 上,`textvqa` 准确率 `50.28`(`vllm-api-general-chat` 模式,`gen`);`omnidocbench` 准确率 `66.86`。
- **性能(Performance)**: 硬件 A2-313T,1 节点;输入/输出 `1080P/256`;**TTFT = 2s**,**TPOT = 200ms**,单卡平均 `864 TPS`(Token Per Second)。
- **调优场景**:多模态 1080P 场景采用 `Single-Node Mixed` 部署,`*Total NPUs = 16(A3)`,权重版本 `deepseekocr2`,采用 `dp1 tp1` 以承载高分辨率视觉输入。

---

## 【表格解读】

### 表格 1:Accuracy 评测结果(原文第 7 节)

| dataset | version | metric | mode | vllm-api-general-chat | note |
|---------|---------|--------|------|------------------------|------|
| textvqa | - | accuracy | gen | 50.28 | 1 Atlas 800 A2 |
| omnidocbench | - | accuracy | gen | 66.86 | 1 Atlas 800 A2 |

**逐行解读**:
- 第 1 行 `textvqa`:该数据集是面向自然图像中文本问答任务的经典 VQA benchmark;在 `vllm-api-general-chat` 通用对话 API 路径下、`gen`(生成式)模式下取得 `50.28` 准确率,运行载体为单台 Atlas 800 A2(原文"1 Atlas 800 A2")。`version` 留空,说明未标注具体数据集切分版本。
- 第 2 行 `omnidocbench`:该数据集聚焦文档理解/OCR 综合评测,在相同的 `vllm-api-general-chat` 与 `gen` 模式下取得 `66.86` 准确率,同样在单 Atlas 800 A2 上得到。两行共同表明 DeepSeek-OCR-2 在文本问答与文档理解两类任务上均能以端到端生成 API 的形式完成精度回归。

### 表格 2:Scenario Overview(原文第 9.1 节,Table 1)

| Scenario | Deployment Mode | *Total NPUs | Weight Version | Key Considerations |
|----------|-----------------|-------------|----------------|--------------------|
| Multimodal<br>(1080P) | Single-Node Mixed | 16 (A3) | deepseekocr2 | dp1 tp1 for high-resolution visual inputs |

**逐行解读**:
- 唯一一行对应 1080P 多模态推理场景:部署模式 `Single-Node Mixed`,`*Total NPUs = 16(A3)`,注释说明 "1 node = 1 Atlas 800 A3 server (64GB × 16 NPUs)";权重版本采用 `deepseekocr2`;关键考量是 `dp1 tp1`,即数据并行 1、tensor 并行 1 的并行拓扑,以适配高分辨率视觉输入带来的显存与计算压力。
- 注意该表格描述的是 A3 调优建议,与第 7、8 节中 A2 实际跑分使用的硬件不同;它属于"调优参考矩阵"而非实测结果。

---

## 【公式解读】

原文第 5.1 节给出的 kv_cache 计算表达式:

```
available kv_cache size = `--gpu-memory-utilization` * HBM size − peak GPU memory usage
```

**符号说明**:
- `--gpu-memory-utilization`:vLLM 用于实际推理的 HBM 占用比例(本文档取 `0.8`,默认 `0.9`),取值范围 `[0, 1]`。
- `HBM size`:设备 HBM 物理总容量。
- `peak GPU memory usage`:在 profile run(warm-up)阶段以 `--max-num-batched-tokens` 输入做一次推理所记录的峰值显存占用,反映模型权重、激活等"不可回收"的内存峰值。
- `available kv_cache size`:最终可分配给 KV Cache 的显存预算,直接决定可服务的并发/批处理上限。

**作用**:此公式揭示了 OOM 风险来源——profile run 的峰值可能与真实推理不同(如 EP 负载不均),因此 `--gpu-memory-utilization` 过高会压缩剩余空间,触发 OOM。

---

## 【关联】

- **支持矩阵**:通过 [Supported Features List](../../user_guide/support_matrix/supported_models.md) 与 [Feature Matrix](../../user_guide/feature_matrix.md) 查阅 DeepSeek-OCR-2 的能力矩阵;本文档第 2 节直接链接到 `supported_models.md`。
- **特性配置**:通过 [Feature Guide](../../user_guide/feature_guide/index.md) 获取每个特性的配置方法,本文档第 2 节也指向同一文档。
- **多节点安装**:第 3.2 节指引到 [verify multi-node communication environment](../../getting_started/installation.md#installation-multi-node-interconnect),尽管第 5.2 节指出"单节点部署推荐",但仍保留了多节点联通校验入口。
- **预构建镜像**:第 4.1 节通过 [using docker](../../getting_started/installation.md#installation-prebuilt-image) 引入 A2/A3 系列容器启动命令。
- **精度/性能评测**:第 7、8 节统一回链到 [Using AISBench](../../developer_guide/evaluation/using_ais_bench.md) 与 [execute-performance-evaluation](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation)。
- **性能调优**:第 9.2.1 节指向 [Public Performance Tuning Documentation](../../developer_guide/performance_and_debug/optimization_and_tuning.md),作为通用调优参考。
- **FAQ**:文档目录中链接到 [FAQs](../../faqs.md),用于排查常见问题(本文档未直接引用,但属于站点的兜底入口)。

---

## 【使用方法】

### 1. 下载权重(原文 3.1)
- 从 [deepseek-ai/DeepSeek-OCR-2](https://huggingface.co/deepseek-ai/DeepSeek-OCR-2) 下载至 `/root/.cache/`。

### 2. 启动容器(原文 4.1)
- A2 系列:8 卡 davinci 设备挂载,镜像 `m.daocloud.io/quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`,挂载 `/root/.cache`。
- A3 系列:16 卡 davinci 设备挂载,其余一致;多节点部署时需在每个节点重复执行。

### 3. 在线推理服务(原文 5.1)
- 设置环境变量:`VLLM_USE_V1=1`、`TOKENIZERS_PARALLELISM=false`、`PYTORCH_NPU_ALLOC_CONF="expandable_segments:True"`、`TASK_QUEUE_ENABLE=1`。
- `vllm serve /root/.cache/DeepSeek-OCR-2 --served-model-name deepseekocr2 --trust-remote-code --tensor-parallel-size 1 --port 1055 --max_model_len 8192 --no-enable-prefix-caching --gpu-memory-utilization 0.8 --allowed-local-media-path / --additional-config '{...}' --mm-processor-cache-gb 0`。

### 4. 功能验证(原文 6)
- 服务成功启动日志:`INFO: Started server process [...]` / `Application startup complete.`。
- 调用示例:`curl http://<node0_ip>:<port>/v1/completions -d '{"model":"deepseekocr2","prompt":"The future of AI is","max_completion_tokens":50,"temperature":0}'`。

### 5. 精度评测(原文 7)
- 走 AISBench 流程,参考 `using_ais_bench.md`;参考结果见上文【表格解读】表格 1。

### 6. 性能评测(原文 8)
- 走 AISBench 性能流程;输入/输出 `1080P/256`,硬件 A2-313T 1 节点,得到 `TTFT=2s, TPOT=200ms, 864 TPS/card`。

### 7. 调优(原文 9)
- 参照 [optimization_and_tuning.md](../../developer_guide/performance_and_debug/optimization_and_tuning.md);1080P 多模态场景推荐 `dp1 tp1`、16 NPUs (A3)、`Single-Node Mixed`。
