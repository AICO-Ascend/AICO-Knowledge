# Qwen3-235B-A22B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-235B-A22B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-235B-A22B.md

# Qwen3-235B-A22B 文档深度解读

## 【定位】

本文档是 vLLM-Ascend 在华为 Ascend NPU 平台上部署 Qwen3 系列最大 MoE 模型 Qwen3-235B-A22B（235B 总参/22B 激活）的端到端验证与运维指南,覆盖**模型支持特性、环境准备、模型量化、多节点通信校验、Docker/源码安装、单节点在线部署及多节点 PD 分离部署**的全流程,首次支持版本为 v0.8.4rc2,基于 v0.21.0 验证,适用于 Atlas 800I A2/A3 全系列产品。

---

## 【技术要点】

1. **模型规格与版本门槛**:Qwen3-235B-A22B 具备 235B 总参数、22B 每 token 激活参数的 MoE 架构;首次支持版本为 **v0.8.4rc2**,文档验证基于 **vLLM-Ascend v0.21.0**,**v0.21.0 及以上版本均可稳定运行**。

2. **硬件拓扑与卡数配置**:
   - **BF16 版本**可部署于:1× Atlas 800I A3 (64GB×16)、1× Atlas 800I A2 (64GB×8)、2× Atlas 800I A2 (32GB×8);
   - **W8A8 量化版本**硬件需求与 BF16 一致,均为推荐卡数,实际可按需调整;
   - **A3 系列采用 dual-die 设计**:8 个 NPU × 双 die = 16 颗芯片,对应 `/dev/davinci[0-15]`;共享机器可按需映射部分芯片(如 `/dev/davinci[0-7]` 对应 NPU 0–3)。

3. **W8A8 量化流程**:基于 `msmodelslim` 工具,执行 `quant_qwen_moe_w8a8.py` 脚本,使用 `qwen3-moe_anti_prompt_50.json` (anti 数据集) 和 `qwen3-moe_calib_prompt_50.json` (校准数据集) 各 50 条 prompt,并附加 `--rot` 标志启用旋转量化。

4. **在线服务部署关键参数**(Atlas 800I A2/A3 单节点 8 卡示例):
   - `--tensor-parallel-size 8`、`--data-parallel-size 1`、`--enable-expert-parallel`
   - `--quantization ascend`、`--max-num-seqs 32`、`--max-model-len 131072`
   - `--max-num-batched-tokens 8096`、`--gpu-memory-utilization 0.95`
   - `--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`
   - `--hf-overrides` 中开启 **YaRN RoPE**: `rope_theta=1000000`、`factor=4`、`original_max_position_embeddings=32768`

5. **Ascend 专用环境变量**:`HCCL_BUFFSIZE=512`、`ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`。

6. **Docker 镜像与设备映射**:使用 `quay.io/ascend/vllm-ascend` 全合一镜像(A3 系列使用 `-a3` 后缀),需挂载 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 及驱动工具目录,默认工作目录 `/workspace`,vLLM 与 vLLM-Ascend 以 site-packages 包形式安装。

---

## 【关键机制与数据】

- **YaRN RoPE 扩展机制**:原文通过 `--hf-overrides '{"rope_parameters": {"rope_type":"yarn","rope_theta":1000000,"factor":4,"original_max_position_embeddings":32768}}'` 将上下文从 32 768 扩展至 131 072(`max-model-len`),其中 `factor=4` 即扩展比例;旋转基础频率 `rope_theta=1000000` 为 YaRN 默认配置。

- **PD 分离(原文 5.2 节标题明示)**:多节点部署通过将 Prefill(预填充)与 Decode(解码)阶段拆分到不同节点,降低单节点资源耦合;原文在第 5.2 节仅给出节标题,**该节正文内容在所提供原文片段中已被截断**,因此具体命令/数据流/性能数据未在原文中给出。

- **量化收益**:原文未提供 W8A8 与 BF16 的吞吐/精度对比数字,仅说明硬件需求相同,量化收益数据**原文未涉及**。

- **服务启动判定**(原文):出现 `(APIServer pid=…) INFO: Started server process / Application startup complete.` 三行日志即视为服务启动成功。

- **专家并行**:`--enable-expert-parallel` 是 MoE 模型在 vLLM-Ascend 上的关键并行策略,与张量并行协同;原文未给出具体的 EP×TP 笛卡尔组合性能数据。

---

## 【表格解读】

**原文表 1 — BF16 版本硬件与下载**

| Model | Hardware Requirement | Download |
|-------|---------------------|----------|
| Qwen3-235B-A22B (BF16) | 1 Atlas 800I A3 (64GB × 16), 1 Atlas 800I A2 (64GB × 8), 2 Atlas 800I A2 (32GB × 8) | [Download](https://www.modelscope.cn/models/Qwen/Qwen3-235B-A22B) |

**逐行解读**:
- *第 1 行*:BF16 精度模型,可在一台满配 A3 (16 张 64GB NPU)、一台满配 A2 (8 张 64GB NPU) 或两台 32GB×8 的 A2 上运行;权重从 ModelScope 官方仓库下载,适用于显存/算力充裕、追求精度的场景。

**原文表 2 — 量化版本(W8A8 预转换)硬件与下载**

| Model | Quantization | Hardware Requirement | Download |
|-------|-------------|---------------------|----------|
| Qwen3-235B-A22B-W8A8 | W8A8 | 1 Atlas 800I A3 (64GB × 16), 1 Atlas 800I A2 (64GB × 8), 2 Atlas 800I A2 (32GB × 8) | [Download](https://modelers.cn/models/Modelers_Park/Qwen3-235B-A22B-w8a8) |

**逐行解读**:
- *第 1 行*:W8A8(权重 8-bit、激活 8-bit)预量化版本,模型仓库为 modelers.cn 而非 ModelScope;硬件需求表与 BF16 相同,意味着量化版本在小批量/低吞吐场景并不会放宽卡数,但能带来显存与带宽的相对节省(具体节省幅度**原文未给出**)。

---

## 【公式解读】

**原文无公式**(无 LaTeX 数学式或伪代码公式块)。

唯一接近公式表达的是 `vllm serve` 命令中的 `--hf-overrides` JSON 配置与 `rope_parameters`,其作为**结构化配置参数**而非数学公式给出(已在【技术要点】第 4 条解读)。

---

## 【关联】

本文档处于 vllm-ascend 文档体系的**模型部署教程层**,与以下模块/文档存在上下游引用关系(基于文末内部链接):

| 内部链接 | 角色 | 与本文档关系 |
|---|---|---|
| `../../user_guide/support_matrix/supported_models.md` | 模型支持矩阵 | 回答 Qwen3-235B-A22B 的整体支持状态(功能/精度/算子) |
| `../../user_guide/feature_guide/index.md` | 功能配置指南 | 解释各特性(专家并行、量化、PD 分离等)的开关与配置方式 |
| `../../getting_started/installation.md#installation-multi-node-interconnect` | 多节点互联安装 | 5.2 节多节点 PD 部署的前置环境校验入口 |
| `../../getting_started/installation.md` | 总安装指南 | 4.2 节源码安装的详细步骤入口 |
| `../../user_guide/configuration/env_vars.md` | Ascend 环境变量手册 | `HCCL_BUFFSIZE`、`ASCEND_RT_VISIBLE_DEVICES`、`PYTORCH_NPU_ALLOC_CONF` 的完整语义说明 |
| `../features/pd_disaggregation_mooncake_multi_node.md` | Mooncake 多节点 PD 分离特性文档 | 与本文 5.2 节多节点 PD 分离直接对应,提供 Mooncake 引擎实现细节 |
| `../../developer_guide/evaluation/using_ais_bench.md` (及 `#execute-performance-evaluation`) | 精度与性能评测 | 文档原文中提到 "accuracy and performance evaluation",对应 ais_bench 评测工具入口 |
| `../../developer_guide/performance_and_debug/optimization_and_tuning.md` | 性能调优 | `cudagraph_mode=FULL_DECODE_ONLY`、YaRN RoPE 等参数背后的调优思路 |

**关联定位**:本文档是 **"特性 → 具体模型部署落地"** 的桥梁层——上层特性文档定义能力,本文给出在 Qwen3-235B-A22B 上的具体参数组合与命令模板。

---

## 【使用方法】

**① 模型权重获取**

- BF16:从 [ModelScope Qwen3-235B-A22B](https://www.modelscope.cn/models/Qwen/Qwen3-235B-A22B) 下载。
- W8A8 预转换:从 [modelers.cn Modelers_Park/Qwen3-235B-A22B-w8a8](https://modelers.cn/models/Modelers_Park/Qwen3-235B-A22B-w8a8) 下载。
- 多节点场景:建议存放到所有节点共享可访问的目录。

**② 模型量化(可选,自量化路径)**

```shell
git clone https://gitcode.com/Ascend/msmodelslim.git
cd msmodelslim && bash install.sh

cd example/Qwen3-MOE
python3 quant_qwen_moe_w8a8.py \
    --model_path /path/to/your/Qwen3-235B-A22B \
    --save_path /path/to/your/Qwen3-235B-A22B-W8A8-rot \
    --anti_dataset ../common/qwen3-moe_anti_prompt_50.json \
    --calib_dataset ../common/qwen3-moe_calib_prompt_50.json \
    --trust_remote_code True \
    --rot
```

**③ 多节点通信校验**:多节点 PD 部署前按 [installation-multi-node-interconnect](../../getting_started/installation.md#installation-multi-node-interconnect) 流程验证。

**④ Docker 镜像安装**

- A3 系列:`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`,映射 `/dev/davinci[0-15]`(16 颗芯片)。
- A2 系列:`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`,映射 `/dev/davinci[0-7]`(8 颗芯片)。
- 通用挂载:`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 及驱动工具目录。
- 验证:`docker ps | grep vllm-ascend-env`(状态 Up)、`pip show vllm-ascend`(显示版本)。

**⑤ 源码安装(替代 Docker)**:按 [Installation Guide](../../getting_started/installation.md) 操作,验证命令同为 `pip show vllm-ascend`;多节点需在**每个节点**重复执行。

**⑥ 单节点在线服务启动(Atlas 800I A2/A3)**

```shell
export HCCL_BUFFSIZE=512
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True

vllm serve your_model_path \
    --host <host_ip> \
    --port <port> \
    --tensor-parallel-size 8 \
    --data-parallel-size 1 \
    --seed 1024 \
    --quantization ascend \
    --served-model-name qwen3 \
    --max-num-seqs 32 \
    --max-model-len 131072 \
    --max-num-batched-tokens 8096 \
    --enable-expert-parallel \
    --trust-remote-code \
    --gpu-memory-utilization 0.95 \
    --hf-overrides '{"rope_parameters": {"rope_type":"yarn","rope_theta":1000000,"factor":4,"original_max_position_embeddings":32768}}' \
    --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'
```

**⑦ 多节点 PD 分离部署**:原文 5.2 节仅给出章节标题 "Multi-Node PD Separation Deployment",**具体部署命令、节点角色分配、跨节点 HCCL 配置等使用细节在所提供原文片段中已被截断,未涉及**;需结合 `../features/pd_disaggregation_mooncake_multi_node.md` 与 `../../user_guide/configuration/env_vars.md` 获取完整步骤。
