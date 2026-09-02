# Qwen3-ASR-1.7B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-ASR-1.7B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-ASR-1.7B.md

# Qwen3-ASR-1.7B 部署指南 — 一体化深度解读

---

## 【定位】

本文档是 **vllm-ascend** 镜像仓中对 Qwen3-ASR-1.7B 模型在 Ascend NPU 上落地的端到端使用指南,围绕"在 Atlas A2 / Atlas 300I DUO 上把 1.7B 参数的语音识别模型拉起来、做功能性验证、做精度/性能评测、做调优"这条主线展开。

---

## 【技术要点】

1. **模型定位与版本耦合**
   - Qwen3-ASR-1.7B 是 Qwen 团队推出的 **1.7B 参数**自动语音识别(ASR)模型。
   - 覆盖能力:**中文/英文语音、中文方言、多语种语音、歌声转写**;并提供**长音频 (long-audio) 与流式 (streaming)** 推理能力。
   - 引入版本:**upstream vLLM v0.19.0**;镜像标签需与 vLLM 版本严格对齐,并对照 support matrix 确认 release 状态。

2. **硬件与精度最低门槛**
   - BF16 权重可在以下两种 NPU 上以单卡部署:
     - **1× Ascend 910B 64 GB**
     - **1× Ascend Atlas 300I DUO 48 GB**
   - 权重来源:**ModelScope** 上的 `Qwen/Qwen3-ASR-1.7B`。
   - 多机部署建议把权重放到**共享目录**(如 `/root/.cache/`)。

3. **两条安装路径:Docker 与源码**
   - Docker:根据硬件选择 Atlas A2 (默认 tag) 或 Atlas 300I DUO (带 `-310p` 后缀 tag);Atlas A2 使用 `--shm-size=1g`,Atlas 300I DUO 需 `--shm-size=10g`。
   - 源码安装:遵循 Installation Guide,并对 **Atlas 300I DUO** 必须先卸载 `triton-ascend triton`(`pip uninstall -y triton-ascend triton`)。

4. **单节点 Online 部署:平台差异化的关键参数**
   - 公共基线:`--tensor-parallel-size 1`、`--max-model-len 4096`、`--gpu-memory-utilization 0.9`、`--port 8000`、`--served-model-name qwen3-asr`。
   - **Atlas 300I DUO 专属**:追加 `--dtype float16`,并通过 `--additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false, "enable_npu_graph_ex": false}}'` + `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes": [1, 4]}'` 控制编译行为。
   - **Atlas A2** 版本额外加 `--enforce-eager`,禁用 graph 执行,用于 300I DUO 的 A2 2UP 兼容性场景。

5. **Chat Completions API 验证路径**
   - 走 `/v1/chat/completions`,`messages[0].content[0]` 采用 `audio_url` 类型,把音频 URL 作为 `audio_url.url` 传入。
   - 启动成功的判定条件:**日志出现 `Application startup complete`**;调用成功判定:**HTTP 200** 且 `choices` 字段包含转写文本。

6. **评测体系**
   - 精度:**WER (Word Error Rate, 词级)** 与 **CER (Character Error Rate, 字级)**。
   - 性能:记录至少 **音频时长、请求并发、端到端延迟、实时率 (real-time factor)、吞吐** 五个维度,确保覆盖**音频预处理、请求构造、API 通信、推理、响应解析**全链路。

7. **调优三档定位(低延迟/高吞吐/长音频)**
   - 文档明确指出这些是"起点而非全局最优",需按音频时长、并发、延迟、NPU 内存**实测调整**;并显式禁止把**纯文本合成请求**当作 ASR 流量的代理做性能测试。

---

## 【关键机制与数据】

- **Causal attention mask 的二次方内存增长**(原文):Atlas 300I DUO 上自动探测到的"较大上下文长度"会构造 full causal attention mask,其内存消耗随 `max_model_len` **二次方增长**;这是 FAQ 中 OOM 的根因,并解释了为什么该平台必须**显式保守设置** `--max-model-len 4096`。
- **cudagraph capture 范围**(原文):`cudagraph_capture_sizes: [1, 4]` 表示图捕获仅覆盖 batch size 1 与 4,搭配 `FULL_DECODE_ONLY` 模式,降低 Atlas 300I DUO 编译/内存压力。
- **fuse_norm_quant 关闭**(原文):`"fuse_norm_quant": false` 显式关闭 norm-quant 融合算子,推测与 fp16 + 310P 编译器兼容性相关(原文未给出技术细节,仅给出开关)。
- **enable_npu_graph_ex 关闭**(原文):`"enable_npu_graph_ex": false` 禁用 NPU 扩展 graph 执行,与 `--enforce-eager` 思路一致,但通过 ascend 编译配置层面控制。
- **shm-size 差异**(原文):Atlas A2 为 `1g`,Atlas 300I DUO 为 `10g`——推断与 310P 的共享内存通信压力有关(原文未给具体原因)。
- **gpu-memory-utilization 0.9**(原文):预留 10% 显存供其他进程;当 NPU 共享时建议**进一步下调**。

---

## 【表格解读】

> 原文中只有"Performance Tuning"一张关键表格,逐字还原如下:

| Scenario | Recommended Starting Point | Key Considerations |
| --- | --- | --- |
| Low latency | `--tensor-parallel-size 1`, `--max-model-len 4096` | Use short audio inputs and avoid sharing the NPU with other workloads. |
| High throughput | Increase request concurrency after establishing the latency baseline | Monitor NPU memory and end-to-end latency; do not use synthetic text-only requests as a proxy for ASR traffic. |
| Long audio | Increase `--max-model-len` only as required | On Atlas 300I DUO, keep the value conservative because attention-mask memory grows with the configured maximum length. |

**逐行解读:**

- **Low latency (低延迟)**:以 **TP=1** 与 **`max-model-len=4096`** 为起点,理由是把并行度关到最小、把上下文窗口限定到合理值以降低 attention 计算量;同时约束输入为**短音频**,并**避免 NPU 被其他工作负载共享**——这与 FAQ 中"OOM 与共享/上下文"两条风险线索呼应。
- **High throughput (高吞吐)**:不指定具体并发数,而是先**建立延迟基线**,再在此基础上**抬高并发**;并要求**同步监控 NPU 内存与端到端延迟**。表格特别强调**不能用文本-only 合成请求当 ASR 代理**——这是 ASR 性能测试的方法论陷阱(音频预处理与解码端开销差异大)。
- **Long audio (长音频)**:仅在确有必要时**放大 `--max-model-len`**,且在 Atlas 300I DUO 上保持**保守值**——理由是 attention-mask 内存与该值正相关,在 310P 48 GB 平台上放大会快速逼近 OOM 红线,与 FAQ 中"自动探测大上下文 → 二次方 attention mask → OOM"形成闭环。

---

## 【公式解读】

**原文无公式**(原文无数学公式、无伪代码形式表达式)。文档中出现的与"指标"相关的术语:

- **WER (Word Error Rate)**:词级识别错误率,英文场景常用(原文未给出计算式)。
- **CER (Character Error Rate)**:字级识别错误率,中文/多语种场景常用(原文未给出计算式)。
- **Real-Time Factor (RTF)**:性能评估指标之一(原文未给出计算式)。

如需量化定义,需参考通用 ASR 文献;**原文未提供具体数学表达**。

---

## 【关联】

- **Supported Models Matrix**([../../user_guide/support_matrix/supported_models.md](../../user_guide/support_matrix/supported_models.md)):用于确认 Qwen3-ASR-1.7B 在当前 release 的**支持状态**;本文档反复提醒要回查该表。
- **Feature Guide**([../../user_guide/feature_guide/index.md](../../user_guide/feature_guide/index.md)):承载"功能特性"章节的详细配置入口;Qwen3-ASR-1.7B 的**流式 (streaming) 与长音频**等特性的具体开关大概率在此。
- **Installation Guide**([../../getting_started/installation.md](../../getting_started/installation.md)):源码安装路径的官方文档,本文"4.2 Source Code Installation"直接转发到该指南。
- **Public FAQs**([../../faqs.md](../../faqs.md)):两处被引用——一是 5 节末尾的"启动失败时查 FAQs";二是文档第 10 节 FAQ 自身的兜底指向,说明 Atlas 300I DUO OOM 等问题在公共 FAQ 中可能已有更系统解答。
- **Performance Tuning Documentation**([../../developer_guide/performance_and_debug/optimization_and_tuning.md](../../developer_guide/performance_and_debug/optimization_and_tuning.md)):第 9 节末尾转发,作为通用调优的"上游"参考,本文档三档起点是该文档之上的**模型/硬件特化补丁**。

**关系图谱(摘要)**:

```
Qwen3-ASR-1.7B 指南
  ├─► Support Matrix   (确认模型是否被当前 release 支持)
  ├─► Feature Guide    (流式/长音频等特性的开关)
  ├─► Installation     (源码安装详细步骤)
  ├─► Performance Tuning  (通用调优方法论,本文档在其上叠加 ASR 特化)
  └─► FAQs             (启动失败 & 环境/参数常见问题)
```

---

## 【使用方法】

**1. 拉取 Docker 镜像并启动容器**(原文命令):

- Atlas A2:`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`,挂载 `/root/.cache`,`--shm-size=1g`。
- Atlas 300I DUO:`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p`,`--shm-size=10g`。
- 验证:`docker ps --filter name=vllm-ascend` 与 `pip show vllm vllm-ascend`,容器应 `Up`,两个包版本应可读。

**2. 源码安装**:遵循 `../../getting_started/installation.md`;若用于 Atlas 300I DUO,先执行 `pip uninstall -y triton-ascend triton`,再 `pip show vllm-ascend` 验证。

**3. 启动在线服务**(原文命令):

- Atlas A2:`vllm serve your_model_path --served-model-name qwen3-asr --tensor-parallel-size 1 --max-model-len 4096 --gpu-memory-utilization 0.9 --enforce-eager --port 8000`。
- Atlas 300I DUO:在 Atlas A2 命令基础上,改用 `--dtype float16`、追加 `--additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false, "enable_npu_graph_ex": false}}'` 与 `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes": [1, 4]}'`,**不要加 `--enforce-eager`**。
- 启动成功标志:日志 `Application startup complete`;启动失败 → 公共 FAQs。

**4. Chat Completions 调用**(原文命令):

- 端点:`POST http://localhost:8000/v1/chat/completions`,`Content-Type: application/json`。
- Body 中 `model=qwen3-asr`,`messages[0].content` 用 `type=audio_url`,`audio_url.url` 指向音频文件 URL。
- 期望:HTTP 200 + `choices` 字段含转写文本。

**5. 配置项语义速查**(原文汇总):

| 启动参数 / 配置键 | 作用 | 适用平台 |
| --- | --- | --- |
| `--tensor-parallel-size 1` | 单 NPU 部署;扩并需先确认拓扑 | 通用 |
| `--max-model-len 4096` | 限制最大序列长度;Atlas 300I DUO 必须显式保守设置 | 通用,310P 强制 |
| `--gpu-memory-utilization 0.9` | vLLM executor 可用显存占比;NPU 共享时下调 | 通用 |
| `--enforce-eager` | 禁用 graph 执行 | Atlas A2 / 300I DUO 的 A2 2UP 兼容场景 |
| `--dtype float16` | 数据类型 | 仅 Atlas 300I DUO |
| `fuse_norm_quant: false` | 关闭 norm-quant 算子融合 | 仅 Atlas 300I DUO |
| `enable_npu_graph_ex: false` | 禁用 NPU 扩展图执行 | 仅 Atlas 300I DUO |
| `cudagraph_mode: FULL_DECODE_ONLY` | cudagraph 仅捕获 decode 阶段 | 仅 Atlas 300I DUO |
| `cudagraph_capture_sizes: [1, 4]` | cudagraph 捕获的 batch size 集合 | 仅 Atlas 300I DUO |
| `--port 8000` | 服务端口 | 通用 |
| `--served-model-name qwen3-asr` | 对外暴露的模型名 | 通用 |

> 注:表中"适用平台"列依据**原文明示**的配置位置/使用上下文归纳,未在原文中给出"适用平台"显式字段。
