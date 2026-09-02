# Qwen3.8-27B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3.8-27B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3.8-27B.md

# Qwen3.8-27B 文档深度解读

## 【定位】

这篇文档是 **Qwen3.8-27B 模型在 vLLM-Ascend（Ascend NPU）上的端到端部署与验证指南**，目标读者是需要将这一 27B 参数稠密视觉-语言模型跑在华为昇腾硬件上的工程师，覆盖硬件选型、镜像安装、多节点通信、权重下载、功能验证与精度/性能评测等关键步骤；该模型首个被支持的版本即 **vLLM-Ascend 0.23.0**。

---

## 【技术要点】

1. **混合注意力骨架（Hybrid Attention Backbone）**：64 层中仅 16 层跑带门控的完整注意力（`full_attention_interval: 4`），其余 48 层使用线性注意力（Gated DeltaNet），具备恒定大小的循环状态（constant recurrent state）。
2. **原生多模态与原生长上下文**：架构为 `Qwen3_5ForConditionalGeneration`（`config.json` 含 `vision_config`），支持图像与视频；原生上下文窗口 262,144 tokens，可扩展至 1,000,000 tokens。
3. **内置 MTP 投机解码头**：模型自带 Multi-Token Prediction draft head，可与投机解码链路配合。
4. **可调推理深度与思考链保留**：Thinking mode 默认开启，可按请求关闭；`reasoning_effort` 支持 `xhigh` / `medium` / `low`；历史消息中的推理过程通过 `preserve_thinking` 保留。
5. **四类权重与硬件匹配**：BF16 原生权重、W8A8 量化、W8A8-MXFP8 量化、W8A8-310P 量化；分别适配 Ascend950DT/PR、Atlas 800 A3、Atlas 800 A2、Atlas 300I DUO 等节点。
6. **多镜像入口与依赖处理**：Ascend950DT/PR 使用 `quay.io/ascend/vllm-ascend:qwen3.8-a5`；A3 使用 `qwen3.8-a3`；A2 使用 `v0.23.0`；Atlas 300I DUO 使用 `v0.23.0-310p`。Atlas 300I DUO 上源码安装时需 `pip uninstall -y triton-ascend triton` 以规避依赖冲突。

---

## 【关键机制与数据】

### 工作原理 / 数据流（原文）

- **注意力分布机制**：64 层 Transformer 中每 4 层出现一次完整注意力层，剩余层用 Gated DeltaNet 线性注意力替代。这意味着在长序列推理时，48 个线性注意力层仅维护固定大小的 recurrent state，显存与计算随序列长度近似线性而非二次方增长。
- **视觉通道**：架构名 `Qwen3_5ForConditionalGeneration` 表明文本与视觉共用一个条件生成框架；视觉配置以 `vision_config` 形式挂在 `config.json` 中，图像/视频 token 与文本 token 一同进入主干。
- **MTP 通路**：模型原生附带 MTP draft head，意味着部署时可使用 vLLM 的 speculative decoding 流程把 MTP 当作 drafter，而无需额外训练一个 draft 模型。
- **思考模式与推理上下文**：`thinking_mode` 默认开启；请求级关闭；`reasoning_effort` 决定推理链展开深度；`preserve_thinking` 用于在多轮对话里把先前回合的思考链内容保留下来供后续回合使用。

### 性能 / 容量数据（原文）

- BF16 权重部署要求：≥768 GB（96 GB × 8）或 ≥1024 GB（128 GB × 8）或 ≥1024 GB（64 GB × 16）或 ≥512 GB（64 GB × 8）显存的节点规模。
- 原生上下文：262,144 tokens，最大可外推/扩展至 1,000,000 tokens。
- 注意力层配比：16/64 ≈ 25% 的层是 full attention，其余 75% 是 linear attention。
- 版本基线：vLLM-Ascend **0.23.0** 是该模型首个被支持的版本。

> 原文未给出具体的吞吐量（tokens/s）、TTFT、Prefill/Decode 时延或端到端 benchmark 数字（该部分出现在被截断的第 5 节 "Online Serv…" 之后）。

---

## 【表格解读】

原文 §3.1 是以列表形式给出的"模型权重与硬件需求"清单，本质上是一张参数-硬件对照表。下面以 markdown 表格逐字还原：

| 权重名称 | 类型 | 所需节点硬件 | 模型权重下载链接 |
|---|---|---|---|
| Qwen3.8-27B | BF16 version | 1 × Ascend950DT series (96GB × 8) 节点；或 1 × Ascend950PR series (128GB × 8) 节点；或 1 × Atlas 800 A3 (64GB × 16) 节点；或 1 × Atlas 800 A2 (64GB × 8) 节点 | https://www.modelscope.cn/models/Qwen/Qwen3.8-27B |
| Qwen3.8-27B-w8a8 | Quantized version | 1 × Ascend950PR series (128GB × 8) 节点；或 1 × Atlas 800 A3 (64GB × 16) 节点；或 1 × Atlas 800 A2 (64GB × 8) 节点 | https://www.modelscope.cn/models/Eco-Tech/Qwen3.8-27B-w8a8 |
| Qwen3.8-27B-w8a8-mxfp8 | Quantized version | 1 × Ascend950DT series (96GB × 8) 节点；或 1 × Ascend950PR series (128GB × 8) 节点 | https://www.modelscope.cn/models/Eco-Tech/Qwen3.8-27B-w8a8-mxfp8 |
| Qwen3.8-27B-w8a8-310p | Quantized version | 1 × Atlas 300I DUO | https://www.modelscope.cn/models/Eco-Tech/Qwen3.8-27B-w8a8-310p |

**逐行解读**：

- **第 1 行（BF16）**：BF16 是未量化版本，权重体积最大，因此可选节点最多，覆盖 950DT/950PR/A3/A2 全部四种平台，门槛最低的是 Atlas 800 A2（64 GB × 8 = 512 GB）。权重由 Qwen 官方提供。
- **第 2 行（W8A8）**：W8A8（权重 8bit、激活 8bit）量化版本相比 BF16 把权重大致压到 1/2，BF16 可跑的 A3/A2 仍可运行；但 BF16 可跑的 950DT 在量化版中被剔除（因为 96 GB × 8 的显存规模此时对 W8A8 不再是必需门槛），意味着该量化权重在 950DT 上不列入推荐。量化版本由 Eco-Tech 提供。
- **第 3 行（W8A8-MXFP8）**：MXFP8（Microscaling FP8）量化版本，仅支持 950DT/950PR 这两种更新的昇腾系列，硬件门槛比第 2 行更窄。
- **第 4 行（W8A8-310P）**：专门为 Atlas 300I DUO（310P 处理器）编译的量化版本，是这张表中唯一针对单卡推理盒（不是节点级 8/16 卡）的权重，因此部署形态与其他三行不同。

附带的部署建议（原文）：模型权重建议下载到多节点共享目录，例如 `/root/.cache/`。

---

## 【公式解读】

原文无公式（既无 LaTeX 数学式，也无伪代码算法块）。

文档第 1 节中以伪参数形式提到的 `full_attention_interval: 4`、`reasoning_effort`（`xhigh`/`medium`/`low`）、`preserve_thinking` 等都是**配置键/枚举值**，不是数学公式。

---

## 【关联】

文档通过相对路径引用了仓库内多项指南/支持矩阵，依赖关系如下：

- **支持特性矩阵与功能指南**：
  - `../../user_guide/support_matrix/supported_features.md`：被 §2 "Supported Features" 直接引用，作为该模型支持能力的事实依据。
  - `../../user_guide/feature_guide/index.md`：被 §2 引用，用于查询具体功能的配置细节。
  - `../../user_guide/support_matrix/feature_matrix.md`：出现在文末内部链接列表中，应是另一个层面的功能矩阵汇总。
- **安装链路**：
  - `../../getting_started/installation.md#installation-multi-node-interconnect`：被 §3.2 引用，是"多节点通信验证"的依据。
  - `../../getting_started/installation.md#installation-prebuilt-image`：被 §4.1 引用，是 docker 镜像拉取与运行的总入口。
  - `../../getting_started/installation.md#installation-existing-cann-install`：被 §4.2 引用，是"源码安装"的依据。
- **评测与调优**：
  - `../../developer_guide/evaluation/using_ais_bench.md`：文末内部链接列表中，应承担"精度 / 性能评测"的角色（文档第 5 节之后预计会引用，但原文此处被截断）。
  - `../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`：上面这页中的"执行性能评测"小节锚点。
  - `../../developer_guide/performance_and_debug/optimization_and_tuning.md`：承担"性能调优"章节。
- **FAQ**：
  - `../../faqs.md`：作为最后兜底，解决用户常见疑问。

整体上，这篇文档是 **Qwen3.8-27B 部署生命周期** 的"主索引页"：本身只展开硬件/镜像/安装细节，其他环节（feature matrix、evaluation、tuning、FAQs）通过链接外联到 developer_guide 与 user_guide。

---

## 【使用方法】

### 启用方式

1. **选权重版本**：按 §3.1 表格匹配硬件，挑出对应模型 ID（如 BF16 → `Qwen/Qwen3.8-27B`）。
2. **下载权重**：原文推荐 `modelscope.cn` 链接，并把权重放到共享目录 `/root/.cache/`。
3. **（可选）验证多节点通信**：参考 `installation.md#installation-multi-node-interconnect`。

### 镜像启动命令（原文逐字保留关键变量）

```bash
# Ascend950DT/PR
export IMAGE=quay.io/ascend/vllm-ascend:qwen3.8-a5
export NAME=vllm-ascend
docker run --rm --name $NAME --net=host --shm-size=1g \
    --device /dev/davinci0 … --device /dev/davinci7 \
    --device /dev/davinci_manager --device /dev/hisi_hdc \
    --device /dev/ummu --device /dev/uburma \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /etc/hccl_rootinfo.json:/etc/hccl_rootinfo.json \
    -v /etc/hixlep/:/etc/hixlep/ \
    -v /root/.cache:/root/.cache \
    -v /usr/local/sbin:/usr/local/sbin \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
    -v /usr/lib64:/usr/lib64 \
    -it $IMAGE bash
```

```bash
# A3 series（注意 IMAGE 不同，设备数扩展到 16 个 davinci）
export IMAGE=quay.io/ascend/vllm-ascend:qwen3.8-a3
# /dev/davinci0 … /dev/davinci15 + /dev/devmm_svm（其它参数略）
```

```bash
# A2 series
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0
```

```bash
# Atlas 300I DUO
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-310p
```

### 容器内验证

```shell
python -c "import vllm, vllm_ascend; print('vllm and vllm_ascend are ready')"
```

### 源码安装（替代 docker）

参考 `installation.md#installation-existing-cann-install`；每个节点安装相同版本的 vLLM 与 vLLM-Ascend。

!!! note "Atlas 300I DUO 上的额外步骤"
    ```bash
    pip uninstall -y triton-ascend triton
    ```

### 关键配置项（推理期）

- `full_attention_interval: 4` —— 控制每 4 层出现一次 full attention（其余层为 linear attention/Gated DeltaNet）。
- `thinking_mode` —— 默认 on，可按请求关闭。
- `reasoning_effort ∈ {xhigh, medium, low}` —— 调节推理链展开深度。
- `preserve_thinking` —— 多轮对话时是否保留历史回合的思考链文本。

### 原文未涉及

- **Online serving 启动命令**（`vllm serve …` 的具体参数）：原文在 §5 "Online Serv…" 处被截断，没有给出 `vllm serve` 命令模板。
- **功能验证（Functional Verification）样例请求**：被截断，未列出。
- **精度与性能评测的具体步骤与指标**：原文虽在文末内部链接指向 `using_ais_bench.md` 与 `optimization_and_tuning.md`，但本页面正文未给出可复现的评测命令与吞吐/时延数字。
- **FAQ 内容**：原文只给出 `../../faqs.md` 的链接，未在本页面列出问答。
- **vLLM-Ascend 0.23.0 与更早/更晚版本之间的差异**：未涉及。
