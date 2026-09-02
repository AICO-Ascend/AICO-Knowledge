# Hy3-preview

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Hy3-preview.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Hy3-preview.md

# Hy3-preview 文档深度解读

## 【定位】

这篇文档记录了 **Tencent Hy Team 的 Hy3-preview MoE 模型在 Atlas A3 16-NPU 节点上经 vLLM Ascend 验证的部署/服务路径**,提供从模型权重来源、容器准备、单节点 `vllm serve` 启动、功能冒烟测试到精度/性能评估的完整端到端操作手册。

---

## 【技术要点】

1. **模型规模**: 总参 295B / 激活 21B / MTP 层参 3.8B,首个基于 Tencent 重建基础设施训练的模型,定位为提升复杂推理、指令跟随、上下文学习、编码、Agent 任务。
2. **验证硬件**: 单 Atlas A3 节点,16 NPUs,每 NPU 64 GB HBM;实际权重运行每 NPU 约消耗 **58 GB** 进程内存。
3. **默认验证路径**: `TP16 + EP + MTP + ACLGraph`,由 `HCCL_OP_EXPANSION_MODE=AIV` 环境变量配合。
4. **启动关键参数**:
   - `--tensor-parallel-size 16`
   - `--speculative-config.method mtp` + `--speculative-config.num_speculative_tokens 1`
   - `--enable-expert-parallel` + `--enable-ep-weight-filter` (推荐启用,过滤不属于本 EP rank 的专家权重以降低磁盘/主机内存压力)
   - `--tool-call-parser hy_v3` + `--reasoning-parser hy_v3` + `--enable-auto-tool-choice`
   - `--max-model-len 32768`、`--max-num-seqs 8`
   - `--served-model-name hy3-preview`
5. **精度参考(原文)**:
   - GSM8K(gen): **93.07**
   - C-Eval(gen): **87.64**
   - 硬件:1 Atlas A3 (64GB × 16)
6. **轻量在线 Benchmark 设定**:`vllm bench serve` + `--backend openai-chat`、随机 prompt、`--random-input-len {1024,4096,16384}`、`--random-output-len 128`、`--num-prompts 4`、`--max-concurrency 1`、`--temperature 0`、4 requests per input length。

---

## 【关键机制与数据】

### 工作原理与数据流(原文表述)

- **MTP 推测解码**:`--speculative-config.method mtp` 启用 MTP 层作为推测草稿(配合 3.8B MTP 参数),`num_speculative_tokens 1` 表示每步额外投机 1 个 token。
- **专家并行 + 权重过滤**:`--enable-expert-parallel` 启用 EP;`--enable-ep-weight-filter` 在加载阶段跳过不属于本 EP rank 的专家权重,**降低 MoE 大 checkpoint 的磁盘读取与主机内存占用**。
- **HCCL AIV 扩展**:启动前导出 `HCCL_OP_EXPANSION_MODE=AIV`,启用 HCCL 的 All-in-One Vector 通信扩展,适配 16 路张量并行下的集合通信。
- **ACLGraph**:`ACLGraph` 路径作为默认加速选项,与 MTP 共同参与推理图捕获。
- **Hy3 接口声明**:Tool calling 与 reasoning 均为 Hy3 README 中声明的服务接口,因此默认绑定 `hy_v3` parser。

### 性能数据(原文,仅供功能性能参考,非调优吞吐上限)

| Random input length | Success / total | Mean TTFT (ms) | Mean TPOT (ms) | Output throughput (tok/s) | Total token throughput (tok/s) |
| --- | --- | ---: | ---: | ---: | ---: |
| 1,024 | 4 / 4 | 484.64 | 30.10 | 29.71 | 270.90 |
| 4,096 | 4 / 4 | 1379.41 | 30.24 | 24.52 | 811.99 |
| 16,384 | 4 / 4 | 2604.58 | 30.43 | 19.79 | 2554.55 |

> 原文标注:这些数字来自真实权重的冒烟 benchmark,1 Atlas A3 16-NPU 节点,TP16 + EP + MTP + ACLGraph,**是功能性性能证据,非调优吞吐上限**。

---

## 【表格解读】

### 表 1:精度评估结果(AISBench,原文逐字还原)

| dataset | version | metric | mode | vllm-api-general-chat | note |
| ----- | ----- | ----- | ----- | ----- | ----- |
| GSM8K | - | accuracy | gen | 93.07 | 1 Atlas A3 (64GB × 16) |
| C-Eval | - | accuracy | gen | 87.64 | 1 Atlas A3 (64GB × 16) |

**逐行解读**:
- **GSM8K 行**:小学数学应用题基准;`version` 列空(`-`)表示使用默认 split;`metric=accuracy`、`mode=gen`(生成式);在该硬件配置下通过 vllm-api-general-chat 通道取得 **93.07%** 准确率。
- **C-Eval 行**:中文综合考试基准;同样为 `accuracy` / `gen`;`vllm-api-general-chat` 通道得分 **87.64%**。
- **note 列**:两行均标注运行平台为 **1 Atlas A3 (64GB × 16)**,与本文验证硬件一致;原文声明该结果"仅供参考"。

### 表 2:轻量在线 Benchmark 性能(原文逐字还原)

| Random input length | Success / total | Mean TTFT (ms) | Mean TPOT (ms) | Output throughput (tok/s) | Total token throughput (tok/s) |
| --- | --- | ---: | ---: | ---: | ---: |
| 1,024 | 4 / 4 | 484.64 | 30.10 | 29.71 | 270.90 |
| 4,096 | 4 / 4 | 1379.41 | 30.24 | 24.52 | 811.99 |
| 16,384 | 4 / 4 | 2604.58 | 30.43 | 19.79 | 2554.65 |

**逐行解读**:
- **1,024 行(短输入)**:4/4 请求全部成功;**Mean TTFT 484.64 ms**(首次 token 时间),**Mean TPOT 30.10 ms/token**(每输出 token 耗时);**Output throughput 29.71 tok/s**、**Total token throughput 270.90 tok/s**——短输入下 TTFT 占主导,总吞吐由 prompt 编码与首 token 决定。
- **4,096 行(中输入)**:4/4 成功;TTFT 升至 **1379.41 ms**(约为短输入的 2.85×,因 prompt 预填充线性增长);TPOT 几乎不变 **30.24 ms/token**;**Output throughput 24.52 tok/s**、**Total token throughput 811.99 tok/s**——批量解码阶段稳定,吞吐随输出规模上升。
- **16,384 行(长输入)**:4/4 成功;TTFT **2604.58 ms**(约为短输入的 5.37×);TPOT 微增至 **30.43 ms/token**;**Output throughput 19.79 tok/s**、**Total token throughput 2554.65 tok/s**——长 prompt 下 TTFT 主导,但总吞吐因输出规模更大反而显著上升。
- **横向规律(原文给出)**:TTFT 随输入长度单调上升,TPOT 在三个长度上几乎稳定(30.10→30.24→30.43 ms),Total token throughput 随 prompt 长度增加而增加(由 prompt token 解码进入总吞吐统计所致),Output throughput 略降。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档通过文末的内部链接与以下模块/指南形成依赖关系:

1. **[Supported Features List](../../user_guide/support_matrix/supported_models.md)** — "Supported Features" 节指向此页,用于查询 Hy3-preview 在 vLLM Ascend 上的支持矩阵(特性兼容性)。
2. **[Feature Guide](../../user_guide/feature_guide/index.md)** — 同节指引,用于查询本文所启用的特性(EP、MTP、ACLGraph、tool-call/reasoning parser、auto-tool-choice 等)的具体配置方法。
3. **[Installation](../../getting_started/installation.md)** — "Environment Preparation > Installation" 节对"非 docker,从源码安装 `vllm-ascend`"的用户指向上述安装指南。
4. **[Using AISBench](../../developer_guide/evaluation/using_ais_bench.md)** — "Accuracy Evaluation > Using AISBench" 与 "Performance > Using AISBench" 两节均指向该指南,作为精度/性能评估的执行入口。
5. **[Using AISBench for performance evaluation](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation)** — "Performance > Using AISBench" 节具体指向该指南的 *execute-performance-evaluation* 锚点,用于执行 AISBench 性能测试。

关联链路总结:**Hy3-preview 部署指南 → 支持矩阵 → 特性配置 → 安装方法 → 评估执行**。

---

## 【使用方法】

### 1. 选择并拉取镜像
原文:`export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`(Atlas A3 选 `-a3` 后缀)。

### 2. 启动容器(原文)
需透传 16 个 `/dev/davinci*` 设备、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,挂载 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/...`、`/etc/ascend_install.info` 与模型目录(`/models`);使用 `--net=host`、`--shm-size=1g`。

### 3. 准备权重
原文:Hugging Face / ModelScope / GitCode 任选其一,下载或挂载至共享路径,示例 `/models/Hy3-preview`。

### 4. 启动 vLLM 服务(原文逐字保留)
```bash
cd /workspace
export MODEL_PATH=/models/Hy3-preview

HCCL_OP_EXPANSION_MODE=AIV \
vllm serve ${MODEL_PATH} \
  --served-model-name hy3-preview \
  --tensor-parallel-size 16 \
  --speculative-config.method mtp \
  --speculative-config.num_speculative_tokens 1 \
  --enable-expert-parallel \
  --enable-ep-weight-filter \
  --tool-call-parser hy_v3 \
  --reasoning-parser hy_v3 \
  --enable-auto-tool-choice \
  --max-model-len 32768 \
  --max-num-seqs 8 \
  --host 0.0.0.0 \
  --port 8000
```

### 5. 功能验证(原文)
- 健康检查:`curl -sf http://127.0.0.1:8000/v1/models`
- 文本冒烟:`curl -sS http://127.0.0.1:8000/v1/chat/completions` 携带 `chat_template_kwargs: {"reasoning_effort": "no_think"}` 等 JSON 体;预期返回 `"content": "Hi"`、`finish_reason=stop`。

### 6. 精度与性能评估
- 精度:执行 AISBench(参考 `using_ais_bench.md`),得出 GSM8K / C-Eval 结果。
- 性能(原文逐字保留 `vllm bench serve` 调用):
```bash
vllm bench serve \
  --backend openai-chat \
  --base-url http://127.0.0.1:8000 \
  --endpoint /v1/chat/completions \
  --model /models/Hy3-preview \
  --served-model-name hy3-preview \
  --dataset-name random \
  --random-input-len 1024 \
  --random-output-len 128 \
  --num-prompts 4 \
  --request-rate inf \
  --max-concurrency 1 \
  --temperature 0 \
  --top-p 1
```
- 或执行 vLLM Benchmark、vLLM Benchmark Suite(参考 https://docs.vllm.ai/en/latest/benchmarking/)。

### 7. 已知限制(原文涉及)
- 模型配置支持 **262,144 tokens**,本指南**仅验证 32,768 token** 服务;更大上下文需另行容量验证。
- 正式 AISBench 精度结果待定,需在实际 benchmark 运行后补全。
