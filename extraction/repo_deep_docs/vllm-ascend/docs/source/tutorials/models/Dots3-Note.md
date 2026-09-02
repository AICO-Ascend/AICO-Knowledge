# Dots3 Note

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Dots3-Note.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Dots3-Note.md

# Dots3 Note 文档深度解读

## 【定位】

本文档是 vLLM-Ascend 上部署与使用 Dots3 Note（基于 Dots3 Note MoE + MLA 架构、带音频/视觉多模态编码器的大型语言模型）的实操型 Guide，覆盖硬件环境校验、软件栈版本、官方镜像拉取、容器启动、多模态形态（text-only / image / audio）选择与后续功能验证的端到端流程，验证基线为 vLLM-Ascend v0.22.1rc1（搭配 vLLM 0.22.1）。原文在第 4.3 节"Environment Variables"处被截断，本解读仅就原文已呈现的内容作答。

---

## 【技术要点】

1. **模型架构与多模态**：Dots3 Note = Dots3 Note MoE + MLA 架构；额外具备 audio + vision 编码器。文本/图像/音频三种形态可同时启用，但同一进程内不可动态切换，必须重启服务（§1）。
2. **三种 Form 与启动参数**：
   - text-only → `--language-model-only`
   - image（文本+图像，每请求 ≤ 7 张）→ `--limit-mm-per-prompt '{"image":7,"video":0,"audio":0}'`
   - audio（文本+音频）→ `--limit-mm-per-prompt '{"image":0,"video":0,"audio":1}'`
3. **MTP 推测解码**：✅ 支持 text-only 与 audio；image 形态下被禁用（Model Runner V1 限制），采用 MTP3 + draft eager 方案（§2）。
4. **FusedMC2 MoE 算子融合**：✅ 支持，通过 `--additional-config` 启用融合后的 `dispatch_ffn_combine` / `mega_moe` 算子（§2）。
5. **Prefix Caching**：✅ 支持，通过 `--enable-prefix-caching` 复用相似 prompt 的 KV（§2）。
6. **硬件与并行拓扑**：单节点 Atlas 800I A3（板型号 `IT22HMDA_4_S`），8 卡 × 双 die = 16 chips，对应 `/dev/davinci[0-15]`，单芯片 64 GB 显存；原文强调 TP16 配置不可直接套用到不同设备拓扑上（§3.1）。
7. **软件栈版本**：npu-smi 26.0.rc1 / firmware 9.0.0.0.205 / CANN 9.0.0 / torch-npu 2.10.0；推荐 all-in-one 镜像 `quay.io/ascend/vllm-ascend:dots3-note-prev-a3-openeuler`（§3.2 / §4.1 / §4.2）。
8. **容器挂载要求**：Atlas A3 需映射全部 16 个 `/dev/davinci*`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并挂载 `/usr/local/dcmi`、hccn_tool、npu-smi、driver lib64、version.info、ascend_install.info 与模型权重目录（§4.2）。

---

## 【关键机制与数据】

- **形态（Form）选型机制**：三种形态分别对应不同的多模态限制与典型基准（text-only → 长上下文/文本推理；image → MMMU 等视觉任务；audio → MMAR 等音频任务）。原文明确：选定 Form 后，后续启动与功能验证命令必须保持同一 Form（§1）。
- **MTP 推测解码限制**：在 image 形态下，MTP 因 Model Runner V1 限制被关闭；该限制与硬件无关，是上层 runner 实现差异（§2，原文表格说明列）。
- **FusedMC2**：把 MoE 的 dispatch / FFN / combine 链路做算子融合（`dispatch_ffn_combine` / `mega_moe`），通过 `--additional-config` 注入，属于推理路径上的算子层优化（§2）。
- **Prefix Caching**：通过 `--enable-prefix-caching` 复用前缀 KV，针对相似 prompt 降低重计算成本（§2）。
- **数据流与启动变量**：
  - 宿主机：`HOST_MODEL_PATH=/path/to/dots3_note`（宿主机侧权重路径）
  - 容器内：`MODEL_PATH=/models/dots3_note`，`SERVED_NAME=dots3_note`（§3.3 / §4.2）
  - 验证命令：`npu-smi info` 应识别 8 卡 16 chip；`python -c "import vllm, vllm_ascend, torch_npu; print(vllm.__version__)"` 与 `pip show vllm vllm-ascend torch-npu` 用于校验组件版本（§4.2）。
- **性能数据**：原文未给出吞吐量、时延、显存占用等量化性能数字，仅说明"v0.22.1rc1 及之后版本可稳定运行"（§1），因此不臆造任何 benchmark 数字。
- **关联性能评估入口**：原文将性能执行链路指向 AIS Bench 评测文档（见【关联】）。

---

## 【表格解读】

### 表格 1：Form 与多模态配置（§1，原文逐字还原）

| Form | Input | Typical scenario | Modal configuration |
|---|---|---|---|
| text-only | Text | Long-context dialogue, text reasoning | `--language-model-only` |
| image | Text + images (≤ 7 per request) | MMMU and other vision tasks | `--limit-mm-per-prompt '{"image":7,"video":0,"audio":0}'` |
| audio | Text + audio | MMAR and other audio tasks | `--limit-mm-per-prompt '{"image":0,"video":0,"audio":1}'` |

**逐行解读**：
- text-only 行：仅文本输入，典型场景为长上下文对话与文本推理；通过 `--language-model-only` 关闭多模态编码器，降低显存与算子开销。
- image 行：每请求最多 7 张图像（与 `--limit-mm-per-prompt` 中 `image:7` 严格对应，且 `video:0` / `audio:0` 显式关掉其余模态），对应 MMMU 等多模态理解基准。
- audio 行：单请求 1 条音频，关闭图像与视频通路，对应 MMAR 等音频理解任务。
- 横向共同规则：同一进程不可动态切 Form；选定后所有启动与验证命令须保持一致。

### 表格 2：Supported Features（§2，原文逐字还原）

| Feature | Support | Description |
|---|---|---|
| Model architecture | Dots3 Note MoE + MLA | MoE mixture of experts + multi-head latent attention |
| Multimodal | audio + vision | Audio / vision encoders, enabled per form (see §5.1) |
| MTP speculative decoding | ✅ (text-only / audio) | MTP3 + draft eager; disabled for image (Model Runner V1 limitation) |
| FusedMC2 | ✅ | Fused `dispatch_ffn_combine` / `mega_moe` operators for MoE (`--additional-config`) |
| Prefix caching | ✅ | `--enable-prefix-caching`, reuses KV for similar prompts |

**逐行解读**：
- Model architecture 行：架构名称为 "Dots3 Note MoE + MLA"，即专家混合 + 多头潜在注意力，是文档标题模型的核心结构标识。
- Multimodal 行：仅列出 audio + vision；文本由主模型自身承担，故未单列；具体启用形态参见 §5.1。
- MTP speculative decoding 行：覆盖 text-only 与 audio 两种形态；image 形态因 Model Runner V1 实现限制关闭；draft 端使用 eager 模式（MTP3）。
- FusedMC2 行：通过 `--additional-config` 启用融合 MoE 算子；融合对象是 dispatch + FFN + combine 链路。
- Prefix caching 行：通过 `--enable-prefix-caching` 开关启用，机制为相似 prompt 复用 KV。

### 表格 3：Hardware Specification（§3.1，原文逐字还原）

| Item | Specification |
|---|---|
| Server | Single-node Atlas A3 inference series (Atlas 800I A3, board model `IT22HMDA_4_S`) |
| NPU | Atlas A3 products (8 cards, each dual-die (2 chips)), 16 chips in total, corresponding to `/dev/davinci[0-15]` |
| Memory | 64 GB device memory per chip |
| Chip software version | SOC_VERSION = `ascend910_9391` (A3 series) |
| Host form | Single-node deployment (not multi-node) |

**逐行解读**：
- Server 行：单节点 Atlas 800I A3，板型号固定为 `IT22HMDA_4_S`。
- NPU 行：8 张卡、每张双 die，因此 OS 层共 16 个 davinci 设备节点（`/dev/davinci0..15`），是 TP16 拓扑的物理基础。
- Memory 行：单芯片 64 GB 显存；16 颗芯片共 1024 GB 设备显存（此总量系由原文 16 × 64 GB 直接推出，非原文新数据）。
- Chip software version 行：SOC_VERSION `ascend910_9391`，是 A3 系列的片上软件标识。
- Host form 行：明确单节点部署，非多节点；用于约束后续并行参数。

### 表格 4：Software Environment（§3.2，原文逐字还原）

| Item | Version |
|---|---|
| NPU driver (npu-smi) | 26.0.rc1 |
| Firmware | 9.0.0.0.205 |
| CANN | 9.0.0 |
| torch-npu | 2.10.0 |

**逐行解读**：
- NPU driver：26.0.rc1；通过 `npu-smi info` 与 `/usr/local/Ascend/driver/version.info` 校验。
- Firmware：9.0.0.0.205；与驱动配套。
- CANN：9.0.0；容器内路径 `/usr/local/Ascend/cann-9.0.0`。
- torch-npu：2.10.0；需与 torch 版本匹配，原文未列具体 torch 版本号。

### 表格 5：Components（§4.1，原文逐字还原）

| Component | Version | Description |
|---|---|---|
| vLLM | 0.22.1 | Inference serving framework, provides OpenAI-compatible service (`vllm serve`) |
| vLLM-Ascend (vllm-ascend) | 0.22.1rc1 | Community-maintained Ascend NPU hardware plugin that connects the NPU to vLLM through the vLLM hardware pluggable interface, aligned with the vLLM version |
| torch-npu | 2.10.0 | PyTorch NPU operator library, paired with the torch version |
| CANN | 9.0.0 | Ascend software stack (development kit + operator packages), in-container path `/usr/local/Ascend/cann-9.0.0` |

**逐行解读**：
- vLLM 行：0.22.1，承担 OpenAI 兼容的推理服务入口（`vllm serve`）。
- vLLM-Ascend 行：0.22.1rc1，作为 vLLM 硬件可插拔接口的 Ascend NPU 适配插件，与 vLLM 版本对齐。
- torch-npu 行：2.10.0，PyTorch 与 NPU 算子之间的桥接库。
- CANN 行：9.0.0，Ascend 算子与开发工具栈容器内落地路径。

### 表格 6：Image 矩阵（§4.2，原文逐字还原）

| Image | Hardware | OS |
|---|---|---|
| `quay.io/ascend/vllm-ascend:dots3-note-prev` | Atlas A2 | Ubuntu |
| `quay.io/ascend/vllm-ascend:dots3-note-prev-openeuler` | Atlas A2 | openEuler |
| `quay.io/ascend/vllm-ascend:dots3-note-prev-a3` | Atlas A3 | Ubuntu |
| `quay.io/ascend/vllm-ascend:dots3-note-prev-a3-openeuler` | Atlas A3 | openEuler |

**逐行解读**：
- 文档推荐使用第四行 `dots3-note-prev-a3-openeuler`，与 §3.1 的 Atlas A3 硬件 + 16 chips 拓扑对齐。
- 若硬件为 Atlas A2 或 OS 为 Ubuntu，应切换到对应 tag；其余 tag 的设备映射（davinci 数量、驱动挂载路径）需相应调整，原文未给出 A2 的具体设备数。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **下游：性能评估执行链**。原文（§1）"功能验证"语义引出性能基准执行路径，文档通过内置链接 `../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation` 指向 AIS Bench 评测指南；Dots3 Note 的吞吐/时延评估通过 AIS Bench 完成，与本指南的部署产物（vLLM-Ascend 服务）形成"部署 → 评估"的串联。
- **上游：vLLM 硬件可插拔接口**。vLLM-Ascend 通过 vLLM 的 hardware pluggable interface 接入，§4.1 将 vLLM 与 vLLM-Ascend 描述为"框架 + 插件"关系，vLLM 版本（0.22.1）与 vLLM-Ascend 版本（0.22.1rc1）必须对齐（§1 / §4.1）。
- **横向：多模态开关依赖项**。§2 "Multimodal" 行将多模态启用形式回链到 §5.1（即"per form"启用细节），但本文档在 §5.1 之前已被截断，因此 §5.1 内容本解读无法覆盖。
- **依赖：CANN / torch-npu / 驱动 / 固件**。§3.2 与 §4.1 形成软件栈依赖清单；宿主机通过 `/usr/local/Ascend/driver/...` 路径把驱动与固件挂载进容器，§4.2 的 `docker run` 命令落实了这一依赖。

---

## 【使用方法】

**镜像与拉取**（宿主侧执行，§4.2）：
```bash
export IMAGE=quay.io/ascend/vllm-ascend:dots3-note-prev-a3-openeuler
docker pull "$IMAGE"
export HOST_MODEL_PATH=/path/to/dots3_note
test -d "$HOST_MODEL_PATH"
```

**容器启动**（宿主侧执行，§4.2）：使用 `docker run -it --rm --name vllm-ascend --shm-size=1g --net=host` 加 16 个 `--device /dev/davinci{0..15}`，外加 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，挂载 `/usr/local/dcmi`、`hccn_tool`、`npu-smi`、`driver/lib64/`、`version.info`、`ascend_install.info`、`/root/.cache` 与 `$HOST_MODEL_PATH` 到 `/models/dots3_note:ro`，最后以 `"$IMAGE" bash` 进入。

**进入容器后变量与最小检查**（§4.2）：
```bash
export MODEL_PATH=/models/dots3_note
export SERVED_NAME=dots3_note
npu-smi info
python -c "import vllm, vllm_ascend, torch_npu; print(vllm.__version__)"
pip show vllm vllm-ascend torch-npu
test -d "$MODEL_PATH"
```

**形态（Form）启用参数**（§1，需与第 5 章 `vllm serve` 命令组合使用，原文未给出完整 `vllm serve` 启动命令行）：
- text-only：加 `--language-model-only`
- image：加 `--limit-mm-per-prompt '{"image":7,"video":0,"audio":0}'`
- audio：加 `--limit-mm-per-prompt '{"image":0,"video":0,"audio":1}'`

**特性开关**（§2）：`--enable-prefix-caching` 启用前缀 KV 复用；`--additional-config` 启用 FusedMC2 融合 MoE 算子；MTP 推测解码在 text-only / audio 下自动启用，image 形态下不可用。

**§4.3 Environment Variables**：原文以"Set the following environment variables in"一句截断，**原文未涉及**具体环境变量清单与命令；本节以下内容（如 `vllm serve` 的完整启动命令、客户端请求样例、性能评测复现命令）均未在原文给出，需参考文档后续章节或 `../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`。
