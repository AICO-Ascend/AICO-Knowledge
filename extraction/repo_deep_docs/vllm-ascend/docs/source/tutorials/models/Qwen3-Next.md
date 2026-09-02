# Qwen3-Next

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-Next.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Next.md

# Qwen3-Next 文档深度解读

## 【定位】
本文档是 vllm-ascend 项目中针对 **Qwen3-Next 稀疏 MoE 模型** 的一份端到端落地指南,聚焦"模型能力简介 → 支持特性查询 → 环境准备 → 部署 → 功能验证 → 精度/性能评估 → 调优建议"的核心验证步骤,目的是让使用者在 Atlas 800 A2/A3 等昇腾节点上完整跑通 Qwen3-Next-80B-A3B-Instruct 的推理服务与基准评测。

---

## 【技术要点】
1. **模型架构属性**: Qwen3-Next 是高稀疏度 MoE 模型,在 Qwen3 MoE 基础上引入了 **hybrid attention mechanism**(混合注意力)和 **multi-token prediction mechanism**(多 token 预测),用于提升长上下文与大体量参数下的训练/推理效率。
2. **首次支持版本**: 在 `vllm-ascend:v0.10.2rc1` 中首次支持,并可在 **v0.16.0 及之后** 版本稳定运行。
3. **后端实现**: 当前使用 **Triton Ascend** 作为底层算子实现,处于 **实验(experimental)阶段**,后续版本可能在稳定性、准确性与性能上出现变更。
4. **硬件与权重**: `Qwen3-Next-80B-A3B-Instruct` 需要 **8 卡**(单 Atlas 800 A3 64GB×16 节点 或 单 Atlas 800 A2 64GB×8 节点);权重托管在 ModelScope。
5. **启动关键参数**: `--tensor-parallel-size 4`、`--max-model-len 32768`、`--gpu-memory-utilization 0.8`、`--max-num-batched-tokens 4096`、`--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`。
6. **TP 限制**: 当前 **不支持 TP ≥ 16**(模型 16 个 query head 仅 2 个 KV head,TP≥16 时 GQA 退化为 MHA,且 FIA 算子在 head_dim=256 的 MHA 场景下失效)。

---

## 【关键机制与数据】

### 工作原理 / 数据流
- **架构机制**: 稀疏 MoE + hybrid attention + multi-token prediction 三者协同,在长上下文、大总参数规模下兼顾训练与推理效率(原文未给出具体路由策略或 attention 配比)。
- **推理后端**: 走 Triton Ascend 算子链 → vLLM 推理引擎 → OpenAI 兼容 `/v1/chat/completions` 接口。
- **Cudagraph 模式**: 启动参数启用 `cudagraph_mode="FULL_DECODE_ONLY"`,只对 Decode 阶段做 CUDA Graph 捕获,降低 Kernel Launch 开销。

### 性能数据(原文)
| 维度 | 原文数值 |
|---|---|
| 硬件 | A3-752T, **2 node** |
| 部署 | TP4 + Full Decode Only |
| 输入/输出 | **2k / 2k** |
| 并发(Concurrency) | **32** |
| 吞吐 | **580 tps** |
| TPOT | **54 ms** |

### 精度数据(原文)
- 测试条件: `Qwen3-Next-80B-A3B-Instruct` 在 `vllm-ascend:0.13.0rc1`,使用 AISBench 通用聊天评测
- **gsm8k / accuracy / gen 模式 = 95.53**

---

## 【表格解读】

### 表格 1: 精度评测结果(原文 Section 7)

| dataset | version | metric | mode | vllm-api-general-chat |
| --- | --- | --- | --- | --- |
| gsm8k | - | accuracy | gen | 95.53 |

**逐行解读**:
- `dataset = gsm8k`:GSM8K 是小学数学应用题基准,考察模型多步推理与算术能力。
- `version = -`:原文未填写具体数据集版本号。
- `metric = accuracy`:以"最终数值答案是否正确"作为评测指标。
- `mode = gen`:采用生成式(generation)而非判别式打分。
- `vllm-api-general-chat = 95.53`:在 vLLM 通用聊天 API 路径下,Qwen3-Next-80B-A3B-Instruct 取得 **95.53%** 的准确率(仅供参照,版本为 0.13.0rc1)。

### 表格 2: 场景概览(Table 1,原文 Section 9.1,**原文此处被截断**)

| Scenario | Deployment Mode | *Total NPUs | Weight Version | Key Considerations |
| --- | --- | --- | --- | --- |
| High Throughput<br>(16k context) | Single-Node Mixed | 2 | *(原文截断)* | *(原文截断)* |

**逐行解读**:
- 仅能确认存在"High Throughput (16k context)"这一场景条目,部署模式为 **Single-Node Mixed**;`Total NPUs = 2`;其后的 `Weight Version` 与 `Key Considerations` 列在提供的原文末尾被截断,**不可臆造**。

---

## 【公式解读】
**原文无公式**。原文仅涉及命令行参数与少量数值指标,未给出任何 LaTeX 或伪代码形式的数学表达式。

---

## 【关联】
依据文末内部链接可定位以下关联模块:

- **特性矩阵/支持列表**:
  - `supported_models.md`:给出 Qwen3-Next 支持的能力矩阵。
  - `feature_matrix.md`:项目级特性 → 模型兼容性矩阵。
- **特性配置指南**:
  - `feature_guide/index.md`:具体 feature 的启用配置方法。
- **安装入口**(在 Section 4 多次引用):
  - `installation.md`:总安装说明。
  - `installation.md#installation-prebuilt-image`:预构建镜像使用小节。
- **评测工具链**(Section 7、Section 8):
  - `using_ais_bench.md`:AISBench 精度评测。
  - `using_ais_bench.md#execute-performance-evaluation`:AISBench 性能评测子节。
- **性能调优上下文**(Section 9 引出):
  - `optimization_and_tuning.md`:性能与调试维度的调优手册,与本文 9.1 推荐配置/9.2 调优方法直接关联。
- **FAQ 兜底**:
  - `faqs.md`:面向常见问题的索引,作为本文未覆盖细节的兜底入口。

整体上,本文处于 vllm-ascend 文档体系的"**模型实战教程**"层,向上承接 `getting_started/installation` 的环境准备,向下衔接 `developer_guide/evaluation` 的精度/性能评测,并与 `developer_guide/performance_and_debug/optimization_and_tuning` 的调优方法形成闭环。

---

## 【使用方法】

### 启用方式
1. **Docker 镜像方式**(Section 4.1):拉取 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3` 镜像,以 A3 系列示例命令运行,挂载 `/dev/davinci0..15`、`davinci_manager`、`devmm_svm`、`hisi_hdc` 等昇腾设备与 `/usr/local/dcmi`、`/usr/local/Ascend/driver/...` 驱动目录,暴露 `8000:8000`。
2. **源码方式**(Section 4.2):先后从 `github.com/vllm-project/vllm` 与 `github.com/vllm-project/vllm-ascend` 克隆,以 `pip install -e .` 安装。
3. 安装后通过 `pip show vllm vllm-ascend` 校验版本信息出现。

### 部署命令(原文 Section 5.1)
```bash
vllm serve Qwen/Qwen3-Next-80B-A3B-Instruct \
  --served-model-name qwen3_next \
  --tensor-parallel-size 4 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.8 \
  --max-num-batched-tokens 4096 \
  --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'
```
成功标志:日志出现 `Started server process [...]` → `Application startup complete.`

### 功能验证(原文 Section 6)
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" -d '{
    "model": "qwen3_next",
    "messages": [{"role": "user", "content": "Who are you?"}],
    "temperature": 0.6, "top_p": 0.95, "top_k": 20,
    "max_completion_tokens": 32
  }'
```
期望返回 HTTP 200 且 JSON 中 `choices` 字段非空。

### 评测命令(原文 Section 8,vLLM Benchmark - serve)
```bash
export VLLM_USE_MODELSCOPE=True
vllm bench serve \
  --model Qwen/Qwen3-Next-80B-A3B-Instruct \
  --dataset-name random \
  --random-input 200 \
  --num-prompts 200 \
  --request-rate 1 \
  --save-result --result-dir ./
```

### 调优约束(原文 Section 9.1)
- **不要使用 TP ≥ 16**(原因:GQA 退化 + head_dim=256 下 FIA 算子失效)。
- 实际调优请结合最大输入/输出长度、prefix cache 命中率、精度要求、部署机比等条件,并参考 `optimization_and_tuning.md` 中的调优方法(本文 Section 9.2 的具体内容**原文未提供,不可臆造**)。
