# ♨️ AscendInfra · 昇腾全栈知识专区

> AICO-Knowledge 双入口之二（配套入口：[📚 知识书架 SHELF.md](SHELF.md)）。
> 以开发者视角自下而上展开昇腾技术栈：芯片架构与数据通路 → AscendC 概念与 API 族 →
> 算子全景 → CANN/HCCL 系统软件 → 训推框架 → 模型算法的昇腾落地映射 → Agent/RL。
> 全部内容链回本库深读资产——论文机制、仓内设计文档、官方手册逐字还原，处处有出处。
>
> 数据基础：69 篇论文深读 · 134 仓归档（1,719 篇文档七节深读）· 6 页官方手册深读。

**目录**：[一、硬件](#一硬件可视化三代-ai-core-与数据通路) · [二、核心概念](#二知识可视化ascendc-核心概念) · [三、API 族](#三ascendc-api-族全景) · [四、算子全景](#四算子全景按模型结构域) · [五、算子仓](#五算子仓地图) · [六、系统软件](#六系统软件cann--hccl--图编译) · [七、训推框架](#七训练与推理框架) · [八、模型落地映射](#八模型算法的昇腾落地映射) · [九、Agent/RL](#九昇腾-agentic--rl) · [十、精度/性能方法论](#十精度与性能方法论) · [十一、知识对照](#十一知识对照表) · [十二、仓全景](#十二昇腾仓全景) · [十三、缺口](#十三共同缺口待补)

---

## 一、硬件可视化：三代 AI Core 与数据通路

理解昇腾的一切优化从这张图开始：**计算**（Cube/Vector/Scalar）、**存储**（GM→L2→L1→L0→UB 层次）、**搬运**（MTE DMA 引擎）三类资源的分工，决定了算子设计的全部约束。

```
                        ┌────────────────────────── AI Core ──────────────────────────┐
                        │                                                             │
   GM（HBM/DDR）        │   ┌──────┐   MTE2   ┌────┐  ┌─────┐                         │
   （片外主存）          │   │  L1  │ ───────► │L0A/│  │     │                         │
      │                 │   │512KB │ ───────► │L0B │─►│CUBE │ 16×16×16 矩阵乘/拍       │
      │  MTE2（搬入）    │   └──────┘          │64KB│  │     │                         │
      ▼                 │                      └────┘  └──┬──┘                         │
   ┌──────┐             │   ┌──────┐                     │ L0C 128KB                   │
   │  L2  │ ──────────► │   │  UB  │ ◄── FixPipe ────────┘ （结果回写/随路量化）        │
   │ 缓存 │   MTE2      │   │192KB │                                               │
   └──────┘             │   └──┬───┘   MTE1（L1→UB）                                  │
      ▲                 │      │      ┌───────┐    MTE3（搬出）                        │
      └──────────────── │      └────► │ VEC   │ ───────────► GM                        │
                        │  Scalar ×2  │向量单元│                                       │
                        └─────────────┴───────┴───────────────────────────────────────┘
```

三条流水解耦（MTE 搬运 / Cube 矩阵 / Vector 向量）是 double buffer、通信掩盖等一切性能手段的硬件依据。

**存储层次与三代规格**（数值出处：[910B/A2/A3 抽象硬件架构深读](../extraction/repo_deep_docs/agent-skills/community/Op/ascendc-operator-design/references/hardware-architecture.md) · [昇腾 950 架构白皮书深读](../extraction/deep/ascend-950-npu-architecture-whitepaper.md)）：

| 存储级 | 910B（A2） | 950（第三代达芬奇） | 角色 |
|---|---|---|---|
| L1 | 512 KB | 更大（面向新数据流） | Cube 输入暂存 |
| L0A / L0B | 各 64 KB | 配套新 Cube | 矩阵左右手操作数 |
| L0C | 128 KB | 配套新 Cube | 矩阵结果累加 |
| UB | 192 KB | 2×256 KB（双缓冲友好） | Vector 工作区 |
| Cube | 16×16×16 FP16/拍 | 同量级 + 原生低精度 | 矩阵乘主力 |

### 昇腾 950（第三代达芬奇）

| 维度 | 规格 |
|---|---|
| 产品形态 | 950PR（推荐+Prefill）128 GB · 1.6 TB/s ｜ 950DT（训练+Decode）144 GB · 4 TB/s |
| 封装 | 2 AI-Die + 2 IO-Die chiplet |
| 互联 | 灵衢 Unified Bus 2.0 |
| 原生精度谱 | FP32 → FP8（E4M3/E5M2/HiF8）→ FP4 |
| 编程模型 | SIMD 为主 + SIMT 为辅 |

→ [白皮书深读（本库独家 · 华为官方白皮书，arXiv 无索引）](../extraction/deep/ascend-950-npu-architecture-whitepaper.md)

### CloudMatrix384 超节点

| 维度 | 数值 |
|---|---|
| 通信范式 | XCCL 内存语义（非 verbs） |
| P2P 小消息延迟 | < 1 MB → < 20 μs |
| 搬运并行 | MTE2/MTE3 ping-pong 藏延迟 |
| 实测规模 | global batch 46,080 · A2E 172 μs |
| 可扩展性 | ~300K NPU pair |

→ [论文深读（独家）](../extraction/deep/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod.md) · [arXiv 原文](https://arxiv.org/abs/2508.02520)

### Atlas 产品支持矩阵

A2 系列（800T A2 / 900 A2 PoD…）· A3 系列（800T A3 / 900 A3 SuperPoD…）· 推理系列（300I DUO / 200I Pro）· 950DT——逐字还原自官方容器镜像支持表。
→ [支持矩阵深读](../extraction/web_deep_docs/vllm-ascend-quickstart.md) · [原始网页](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/latest/quick_start.html)

---

## 二、知识可视化：AscendC 核心概念

| 概念 | 一句话 |
|---|---|
| **TPipe** | 统一管理 Device 端内存的调度器，核函数内所有缓冲申请的总入口 |
| **TQue / TBuf** | TQue 以队列管理内存（配 EnQue/DeQue 做流水同步）；TBuf 管理临时变量缓冲。二选一是性能 FAQ 高频点 |
| **GlobalTensor / LocalTensor** | GM（外部存储）与 Local Memory（核内存储）的张量抽象——所有数据搬运的两端 |
| **double buffer** | 搬运与计算并行：UB 切两半，MTE 搬下一块的同时 Vector 算当前块。硬件依据 = 三流解耦（见上方架构图） |
| **tiling 切分** | 数据分核策略：把大任务切成核内可容纳的块，消除拖尾、对齐 512B 访问 |
| **内存格式** | ND / NZ / NCHW / NHWC / NC1HWC0——Cube 友好的是 NZ 分形，TransDataTo5HD 做格式转换 |
| **同步原语** | SetFlag / WaitFlag / PipeBarrier——对应硬件的同步信号流；Cube↔Vector 跨核同步是精度 FAQ 之首 |
| **TP / PP / DP** | 模型并行三轴：张量并行 / 流水并行 / 数据并行 |
| **集合通信** | HCCL（片间）/ LCCL（片上）集合通信库 |

---

## 三、AscendC API 族全景

| API 族 | 代表接口 | 功能 |
|---|---|---|
| 数据搬运 | DataCopy · DataCopyPad · Copy | GM↔L0/L1↔UB 各通路搬运；DataCopyPad 支持非对齐搬运与填充 |
| 收集/分散/填充 | Gather · Gatherb · Scatter · Duplicate · Brcb · CreateVecIndex | 按偏移地址收集/分散元素；变量广播填充；创建向量索引 |
| 转置/格式 | Transpose · TransDataTo5HD | 16×16 二维块转置；NCHW↔NHWC、NC1HWC0 分形转换 |
| 单目运算 | Exp · Ln · Abs · Reciprocal · Sqrt · Rsqrt · Not · VectorPadding | 按元素一元函数（Reciprocal 精度不满足要求的场景注意） |
| 双目运算 | Add · Sub · Mul · Div · Max · Min · And · Or · MulAddDst · FusedMulAdd | 按元素二元运算，单迭代处理 PAR 个元素 |
| 标量双目 | Adds · Muls · Maxs · Mins | 矢量与标量逐元素运算 |
| 比较 | Compare · CompareScalar | 逐元素比较（LT/GT/GE/EQ/NE/LE），结果写比特位 |
| 选择 | Select · GatherMask | 按掩码比特从两源操作数选取元素 |
| 排序组合 | Sort32 · RpSort16 · ProposalConcat · ProposalExtract · MrgSort | Sort32 一次迭代排 32 个数（score+index 结构 8B） |
| 精度转换 | Cast 族 | dtype 间转换（fp16/fp32/bf16/int8…） |

---

## 四、算子全景（按模型结构域）

| 结构域 | 内容 | 深读资产 |
|---|---|---|
| **Attention** | MLA 矩阵吸收 · 稀疏注意力打分 · KDA chunkwise 线性注意力——论文机制与仓内算子设计文档互证 | [ChunkKdaFwd 设计](../extraction/repo_deep_docs/vllm-ascend/csrc/attention/chunk_kda_fwd/docs/design.md) · [SparseAttentionScore 设计](../extraction/repo_deep_docs/vllm-ascend/csrc/attention/sparse_attention_score/docs/sparse_attention_score_design.md) · [KDA 论文深读](../extraction/deep/kimi-linear-an-expressive-efficient-attention-architecture.md) |
| **MoE** | dispatch/combine 通信算子 + 专家负载均衡（EPLB） | [Megatron-Core MoE 深读](../extraction/deep/scalable-training-of-mixture-of-experts-models-with-megatron-core.md) · [EPLB 深读](../extraction/repo_deep_docs/mindspeed-rl/docs/zh/features/EPLB.md) |
| **Matmul / Cube** | Cube 单元模板库 + 矩阵分形格式（NZ）与 L0 双输入缓冲的匹配 | [CATLASS 教程深读](../extraction/repo_deep_docs/catlass/docs/tutorials.md) · [catlass 仓](https://gitcode.com/xLLM-AI/catlass) |
| **量化** | Attention 量化 · Anti-Outlier 离群值抑制 · 模型压缩工具链 | [Attention 量化深读](../extraction/repo_deep_docs/mindie-llm/docs/zh/user_guide/feature/attention_quantization.md) · [Anti-Outlier 深读](../extraction/repo_deep_docs/mindie-llm/docs/zh/user_guide/feature/anti_outlier.md) · [msModelSlim 量化设计](../extraction/repo_deep_docs/msmodelslim/docs/zh/contributing/design/典型模型量化支持特性设计说明书.md) |
| **序列扫描** | 并行 scan 是线性注意力/状态空间模型的底层算子 | [Parallel Scan on Ascend 深读（独家）](../extraction/deep/parallel-scan-on-ascend-ai-accelerators.md) |
| **多模态** | ViT 编码与多模态融合的算子需求 | [MindSpeed-MM 仓](https://gitcode.com/Ascend/MindSpeed-MM)（训练）· [MindIE-SD 仓](https://gitcode.com/Ascend/MindIE-SD)（推理） |

---

## 五、算子仓地图

| 仓 | 版本 | 定位 |
|---|---|---|
| [triton-ascend](https://gitcode.com/Ascend/triton-ascend) | v3.2.1 | Triton 的昇腾后端（已迁 triton-lang 主线）——GPU 算子迁移昇腾的最低门槛 → [昇腾与 GPU 开发差异深读](../extraction/repo_deep_docs/triton-ascend/docs/zh/migration_guide/architecture_difference.md) |
| [catlass](https://gitcode.com/xLLM-AI/catlass) | v1.1.0 | CATLASS = CANN 版 CUTLASS，Cube 算子模板库 |
| [ascend-transformer-boost](https://gitcode.com/xLLM-AI/ascend-transformer-boost) | v9.0.0 | ATB 加速库（Transformer 融合算子） |
| [op-plugin](https://gitcode.com/Ascend/op-plugin) | v5.0.rc3 | torch_npu 算子插件 |
| [xllm_ops](https://gitcode.com/xLLM-AI/xllm_ops) · [torch_npu_ops](https://gitcode.com/xLLM-AI/torch_npu_ops) · [triton-ascend-kernels](https://gitcode.com/Ascend/triton-ascend-kernels) | — | 高性能算子库群 |

---

## 六、系统软件：CANN / HCCL / 图编译

CANN 是昇腾的 CUDA：驱动与运行时之上，图编译（GE/torchair）、算子库、HCCL 集合通信构成软件栈主体。三份官方手册已逐字入库——其中**商用版与社区版环境变量清单的一致性对照是本库独家结论**。

```
 应用框架（PyTorch / torch_npu）
   ↓
 图编译（GE · torchair）
   ↓
 算子库（AscendC / AOL / ATB）
   ↓
 运行时 + 驱动
   ↓
 HCCL 集合通信（跨芯片）
```

### 环境变量速查（高频精选）

| 变量 | 说明 |
|---|---|
| HCCL_BUFFSIZE | 集合通信缓存区 ≥1，默认 200 MB |
| HCCL_RDMA_RETRY_CNT | RDMA 重传次数 ∈ [1,7]，默认 7 |
| HCCL_IF_BASE_PORT | Host 网卡起始端口 → 连占 32 端口 |
| ASCEND_REMAIN_CACHE_SIZE_RATIO | 算子编译缓存保留比，默认 50% |
| HF32 开关 | 仅 Conv / Matmul 类算子生效 |
| PYTORCH_NPU_ALLOC_CONF | torch_npu 侧显存分配器配置 |

→ [CANN 全量手册（132 表行逐字）](../extraction/web_deep_docs/ascend-cann-commercial-envvars.md) · [PyTorch NPU 22 变量](../extraction/web_deep_docs/ascend-pytorch-envvars.md)

### 版本对照（本库独家 · 机械 diff 实证）

CANN 环境变量索引页：**商用版 900 与社区版 910beta1 逐行 diff 仅 4 行站内锚点 ID 差异**，变量名/分组/简介逐字相同——环境变量知识可跨版复用。后续版本发布重抓即得增量 diff。
→ [商用版深读](../extraction/web_deep_docs/ascend-cann-commercial-envvars.md) · [社区版深读](../extraction/web_deep_docs/ascend-cann-community-envvars.md) · [版本对照记录](../extraction/web_moc.md)

### HCCL 集合通信

通信域创建（基于 root 节点信息）官方指南已入库：建链流程、ranktable 与端口占用规则、可靠性重传（SDMA/RDMA CQE 错误触发算子重执行，以通信域为粒度）。
→ [HCCL 通信域指南深读](../extraction/web_deep_docs/ascend-cann-hccl-guide.md) · [hccl_transfer 仓](https://gitcode.com/xLLM-AI/hccl_transfer)

### 图编译（torchair / GE）

计算与通信并行、动态 shape 分档、算子级确定性计算、编译缓存——图编译层特性文档七节深读在册。
→ [计算与通信并行](../extraction/repo_deep_docs/torchair/docs/zh/ascend_ir/features/advanced/cc_parallel.md) · [确定性计算](../extraction/repo_deep_docs/torchair/docs/zh/ascend_ir/features/advanced/deterministic.md) · [torchair 仓](https://gitcode.com/Ascend/torchair)

---

## 七、训练与推理框架

训练看 MindSpeed 家族（对位 Megatron），推理开源看 vllm-ascend、商用看 MindIE——全部仓带版本血缘，特性文档七节深读在册。

### MindSpeed 训练家族（v26.1.0_core_r0.12.1）

- **fb-overlap**：MoE 前反向 AllToAll 通信掩盖 → [特性深读 + 3 图图文联合解读](../extraction/repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md)
- 版本命名规则：`<产品版>_core_r<Megatron-Core 兼容版>`（26.1.0 配套 MCore 0.12.1）
- 家族：mindspeed / mindspeed-llm / mindspeed-mm / mindspeed-rl / mindspeed-ops / mindspeed-bridge / megatronadaptor / transformerenginenpu

→ [mindspeed 仓卡片（分析层）](../extraction/deep/repo-mindspeed.md) · [代码仓](https://gitcode.com/Ascend/MindSpeed)

### vllm-ascend（v0.25.1rc1）

- vLLM 的昇腾官方后端；仓内藏算子级设计文档（ChunkKdaFwd / SparseAttentionScore）
- 特性教程深读：[PD 分离（Mooncake 多机）](../extraction/repo_deep_docs/vllm-ascend/docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md) · [动态 chunked 流水并行](../extraction/repo_deep_docs/vllm-ascend/docs/source/tutorials/features/dynamic_chunked_pipeline_parallel.md)

→ [仓卡片（分析层）](../extraction/deep/repo-vllm-ascend.md) · [中文快速上手深读](../extraction/web_deep_docs/vllm-ascend-quickstart.md)

### MindIE 商用推理栈（3.1.0）

- mindie-llm（引擎）· mindie-turbo（加速）· mindie-motor（集群编排）· mindie-sd（多模态）
- 特性深读：[架构设计](../extraction/repo_deep_docs/mindie-llm/docs/zh/developer_guide/architecture_design/architecture_overview.md) · [异步调度](../extraction/repo_deep_docs/mindie-llm/docs/zh/user_guide/feature/asynchronous_scheduling.md) · [Attention 量化](../extraction/repo_deep_docs/mindie-llm/docs/zh/user_guide/feature/attention_quantization.md) · [Motor 架构](../extraction/repo_deep_docs/mindie-motor/docs/zh/architecture.md) · [SD 动态专家负载均衡](../extraction/repo_deep_docs/mindie-sd/docs/en/features/DyEPLB.md)

→ [MindIE-LLM 仓](https://gitcode.com/Ascend/MindIE-LLM)

### xLLM（v0.10.1）

- 京东开源推理框架；GLM-5.3-Flash day-0 适配时间线已记入仓卡片（版本血缘实例）
- 特性深读：[PD 分离设计](../extraction/repo_deep_docs/xllm/docs/src/content/docs/en/features/disagg_pd.md) · [chunked 调度](../extraction/repo_deep_docs/xllm/docs/src/content/docs/en/features/chunked_scheduler.md)

→ [仓卡片（分析层）](../extraction/deep/repo-xllm.md) · [对照：vLLM serve 312 参数手册](../extraction/web_deep_docs/vllm-cli-serve.md)

---

## 八、模型算法的昇腾落地映射

每个算法在这里回答一个问题：**落到昇腾需要哪些算子、哪个框架已支持**。论文机制深读在主书架，本页给落地映射。

| 算法 | 论文深读 | 昇腾算子需求 | 落地证据 |
|---|---|---|---|
| KDA（Kimi 线性注意力） | [Kimi Linear](../extraction/deep/kimi-linear-an-expressive-efficient-attention-architecture.md) · [GDN](../extraction/deep/gated-delta-networks-improving-mamba2-with-delta-rule.md) | chunkwise 线性注意力 + 并行 scan | [ChunkKdaFwd 设计文档](../extraction/repo_deep_docs/vllm-ascend/csrc/attention/chunk_kda_fwd/docs/design.md) · [并行 scan 论文](../extraction/deep/parallel-scan-on-ascend-ai-accelerators.md) |
| DSA（DeepSeek 稀疏注意力） | [DeepSeek V4](../extraction/deep/deepseek-v4-towards-highly-efficient-million-token-context-intelligence.md) | 稀疏 gather / index 算子 | [SparseAttentionScore 设计](../extraction/repo_deep_docs/vllm-ascend/csrc/attention/sparse_attention_score/docs/sparse_attention_score_design.md) |
| MLA（低秩注意力） | [DeepSeek V3](../extraction/deep/deepseek-v3-technical-report.md)（[架构裁剪图](../extraction/assets/crops/deepseek-v3-technical-report-fig02-mla.png)） | 矩阵吸收 + 大 Cube 吞吐 | MindSpeed / vllm-ascend 均支持（标杆适配模型） |
| MoE | [Megatron-Core MoE](../extraction/deep/scalable-training-of-mixture-of-experts-models-with-megatron-core.md) | dispatch/combine 通信算子 + EPLB | [fb-overlap](../extraction/repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md) · [EPLB](../extraction/repo_deep_docs/mindspeed-rl/docs/zh/features/EPLB.md) |
| FP8 训练 | [DeepSeek V3 §FP8](../extraction/deep/deepseek-v3-technical-report.md) | 原生 FP8（E4M3/E5M2/HiF8） | 910C 不原生支持（需 PTQ 补偿）→ 950 原生支持（见硬件节） |
| 投机解码（EAGLE 族） | [主书架投机解码条目](SHELF.md) | 草案树注意力 + 采样算子 | vllm-ascend 实验性支持 EAGLE3 |

---

## 九、昇腾 Agentic / RL

Agent 系统的昇腾落地当前以 RL 训练栈为主；Agentic 算子生成是 GPU 侧前沿、昇腾侧方法论可平移的方向。

- **MindSpeed-RL（v2.3.0）**：昇腾强化学习加速库——EPLB、推理图模式、激活重计算、chunked prefill、长序列并行等特性深读在册。→ [EPLB 深读](../extraction/repo_deep_docs/mindspeed-rl/docs/zh/features/EPLB.md) · [长序列并行](../extraction/repo_deep_docs/mindspeed-rl/docs/zh/features/context_parallel.md) · [MindSpeed-RL 仓](https://gitcode.com/Ascend/MindSpeed-RL)
- **RL 训推耦合（论文层）**：AREAL 异步 rollout · HybridFlow 训推解耦 · DeepSeek-R1 GRPO——方法论对昇腾 RL 栈直接有参考价值。→ [主书架 Agentic RL 分区](SHELF.md)
- **Agentic 算子生成（前沿）**：CUDA-Agent（Agentic RL 生成 CUDA kernel）的方法论可平移到 AscendC 算子生成——昇腾侧尚无对应系统，是机会窗口。→ [CUDA-Agent 深读](../extraction/deep/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.md)

---

## 十、精度与性能方法论

昇腾算子开发的两套社区方法论（整理自昇腾官方教程与算子开发实践），与本库深读资产互补。

### 12 步搞定算子精度问题

1. **开日志重跑**——打开昇腾日志获取详细信息
2. **搜索案例库**——检索问题案例库
3. **检查标杆和过程**——检查标杆函数或测试过程，排除低级错误
4. **定性问题类型**——确认是功能问题还是偶发的时序/同步/竞争问题
5. **用例特征分析**——同类问题归类 + 正反比较找准特征
6. **增加必要的校验**——入参和 tiling 加严格校验，避免问题流入后端
7. **最小代价稳定复现**——找到稳定复现的最低成本测试用例
8. **错误数据特征分析**——分析错误数据分布，结合分核和计算逻辑找代码段
9. **对比找差异**——对比不同版本/不同用例
10. **调试 & 借助工具**——调试或工具检测辅助定位
11. **积极求助 & 风险上报**——把问题描述清楚后对外求助
12. **整理问题过程和刷新案例**——记录关键信息与推敲过程并分享

### 12 步搞定算子性能优化

1. **先度量后优化**——基于 profiling 或仿真流水，避免经验主义
2. **最大化利用 UB**——优先大块内存的搬运和计算，降低迭代次数
3. **开启 double buffer**——大数据量优先实现 db，保证搬运与计算并行
4. **定界/聚焦耗时大头**——profiling 定位耗时单元，有针对性屏蔽代码找关键路径
5. **优先大块 + 对齐计算/搬运**——减少碎片与非对齐操作，GM 访问尽量 512B 对齐
6. **高效的 tiling 切分**——合理切分大块计算与核数选择，消除拖尾
7. **简化计算公式/逻辑**——等效变换/近似计算减少计算量
8. **合理的流水排布**——计算/搬运流水排布消除浪费
9. **消除冗余逻辑**——冗余计算步骤、内存占用、多余同步指令
10. **固化标准计算块**——固化基础计算单元、常量化计算参数
11. **缓存高效利用**——用好 L2/L1/UB 各级缓存与 cacheline/对齐特性
12. **该收手时就收手**——建立科学的性能理论评估机制，知道何时停止优化

**优化小技巧**：谨慎使用 Alloc/Free/EnQue/DeQue（延迟申请、用完立即释放）· TPipe 外置（创建外置到核函数，引用传递）· FixPipe 随路量化（Cube 核随路量化）· 空间换时间。

### FCodeQ（算子开发高频问答）

| 问题 | 要点 |
|---|---|
| Cube 和 Vector 间如何同步？ | 跨核同步用 `ffts_cross_core_sync`（Cube 侧，PIPE 按需选用：MTE3 拷出完成触发 / MTE2 拷入完成触发）+ `wait_flag_dev`（Vector 侧等待 flag） |
| 如何将 TQue 改成 TBuf？ | TBuf 管理临时变量缓冲，无 EnQue/DeQue 同步语义，适合非流水化临时空间 |
| 310P 如何实现 DataCopyPad 逻辑？ | 310P 无 DataCopyPad 接口，需手工补对齐搬运 + 填充逻辑 |
| 如何实现高性能转置？ | Transpose（16×16 块）/ TransDataTo5HD（NCHW↔NC1HWC0），配合 NZ 分形格式 |

---

## 十一、知识对照表

同一概念的图形化呈现、机制深读、仓内实现锚点三方互证。

| 概念 | 本页位置 | 本库深读 / 手册 | 仓实现锚点 |
|---|---|---|---|
| double buffer（搬运/计算并行） | 一、架构图 · 三流解耦 | [fb-overlap 特性深读](../extraction/repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md) | [MindSpeed 原始文档](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md) |
| 通信掩盖流水 | 一、数据通路 | [DeepSeek-V3 DualPipe 深读](../extraction/deep/deepseek-v3-technical-report.md) | [MindSpeed fb-overlap 实现](https://gitcode.com/Ascend/MindSpeed) |
| 线性注意力算子（KDA/GDN） | 八、落地映射表 | [Kimi Linear 深读](../extraction/deep/kimi-linear-an-expressive-efficient-attention-architecture.md) | [ChunkKdaFwd 原始设计](https://gitcode.com/gh_mirrors/vl/vllm-ascend/blob/main/csrc/attention/chunk_kda_fwd/docs/design.md) |
| tiling 切分 | 二、概念表 | [CANN 手册（编译/执行条目）](../extraction/web_deep_docs/ascend-cann-commercial-envvars.md) | [catlass 仓](https://gitcode.com/xLLM-AI/catlass) |
| 集合通信 HCCL | 六、软件栈分层 | [HCCL 通信域指南](../extraction/web_deep_docs/ascend-cann-hccl-guide.md) | [hccl_transfer 仓](https://gitcode.com/xLLM-AI/hccl_transfer) |
| Cube/Vector 双单元 | 一、AI Core 架构图 | [抽象硬件架构深读](../extraction/repo_deep_docs/agent-skills/community/Op/ascendc-operator-design/references/hardware-architecture.md) | [catlass（Cube 模板）](https://gitcode.com/xLLM-AI/catlass) |
| 超节点组网 | 一、CloudMatrix 卡片 | [CloudMatrix384 深读](../extraction/deep/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod.md) | [HCCL 超节点环境变量](../extraction/web_deep_docs/ascend-cann-commercial-envvars.md) |

---

## 十二、昇腾仓全景

134 仓按技术族分组；每仓有机械层卡片（版本/tag/结构），重点仓有分析层卡片与数十到数百篇文档深读。完整可检索清单见 [repo_deep_index.json](../extraction/repo_deep_index.json)。

| 族 | 成员 |
|---|---|
| MindSpeed 训练家族（10） | mindspeed · mindspeed-llm · mindspeed-mm · mindspeed-rl · mindspeed-ops · mindspeed-bridge · mindspeed-agent · mindspeed-core-ms · megatronadaptor · transformerenginenpu |
| MindIE 推理家族（5） | mindie-llm · mindie-turbo · mindie-motor · mindie-motor-cpp · mindie-sd |
| 推理引擎与后端（9） | vllm · vllm-ascend · xllm · xllm_ops · xllm_atb_layers · text-embeddings-inference · mindinferenceservice … |
| 算子与编译（21） | triton-ascend · catlass · torchair · op-plugin · apex · tilelang-ascend · ascend-transformer-boost · tvm … |
| 通信与存储（8） | hccl_transfer · memfabric_hybrid · memcache · parakv · mooncake · tensorpipe · transferqueue · brpc |
| 集群管理与部署（9） | mind-cluster · mindcluster-deploy · ascend-deployer · ray-ascend · slime-ascend · fsdpturbo … |
| 调优与工具链 msIT/msTT 族（24） | msit · mstt · msprof · msdebug · msprobe · msmodelslim · msserviceprofiler … |
| 模型套件与行业 SDK（27） | modelzoo 族 · recsdk · visionsdk · ragsdk · multimodalsdk · agent-skills · docs … |
| 三方依赖镜像（21） | cutlass · faiss · flashinfer · sentencepiece · composable_kernel … |

---

## 十三、共同缺口（待补）

- ~~达芬奇架构手册~~（已关闭：agent-skills 仓抽象硬件架构深读覆盖，见硬件节出处）
- ~~HCCL 使用指南~~（已关闭：通信域创建指南页已入库深读，见系统软件节）
- MindIE vs vllm-ascend 选型对照（官方无此页，需自建或找第三方权威分析）
- HCCL vs NCCL 接口语义对照（待权威来源）
- CANN 软件栈分层官方总览（当前分层图为本页自绘，待官方图对照）

---

> AscendInfra · AICO-Knowledge 知识库双入口之二 · 配套入口 [📚 知识书架 SHELF.md](SHELF.md) ·
> 本页所有数值均可在所链深读资产中溯源 · 页面手工维护（`bookshelf/ascend_infra.md`；交互式 HTML 旧版备份为 `ascend_infra.html`）
