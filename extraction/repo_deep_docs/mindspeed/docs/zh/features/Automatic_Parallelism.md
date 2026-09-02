# Automatic Parallelism

> 仓 `mindspeed` · 路径 `docs/zh/features/Automatic_Parallelism.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/Automatic_Parallelism.md

# Automatic Parallelism 文档深度解读

## 【定位】

本文档描述了 mindspeed 面向大模型分布式训练场景提供的"多维并行配置自动寻优"能力：用户仅给定模型结构与集群规模，系统即可在限定时间内自动推荐一组较优的 PP/TP/DP/SP/CP/UP/mbs 并行组合，免去专家手工调参。

---

## 【技术要点】

1. **三段式自动寻优算法**：由"内存自适应感知的搜索空间构建 → 基于算子不确定性估计的高保序性 Cost Model → 基于概率匹配的高效搜索算法"三部分串联构成（原文"解决方案"段）。
2. **内存灰盒模型剪枝**：用内存灰盒模型预先排除 OOM 的并行配置，缩小搜索空间（原文第一条 bullet）。
3. **算子不确定性 Cost Model**：以低保真数据（单算子调用）作为先验，结合算子整网性能数据建立算子执行耗时的不确定性模型，再叠加通信耗时合成端到端性能的概率分布（原文第二条 bullet）。
4. **Thompson Sampling 搜索**：基于概率匹配/Thompson Sampling 探索并行策略，"以高概率探索高价值并行配置"，并"灵活支持探索早停"（原文第三条 bullet）。
5. **搜索预算硬约束**：算法最长搜索时间为 **8 小时**，支持灵活提前退出，无需人工干预（原文"使用方法"注）。
6. **启动方式约束**：必须使用 **python 作为脚本启动器**，在所有节点上拉起脚本，并配置 `--auto-parallel` 等多维自动并行参数（原文"使用方法"首段）。

---

## 【关键机制与数据】

- **搜索空间爆炸数据**（原文："挑战"段）：Llama-65B 在 4×8 集群规模下，仅考虑 PP、TP、DP、SP、VPP、mbs 六个维度，**配置组合共有 812 种**，手工调优时间成本过高。
- **手工调优代价**（原文）：人工调优预计数天~数周，实验成本高；且相似模型的最优并行配置并不相同。
- **已支持/即将支持的并行维度**（原文"并行配置的支持情况"）：
  - 已支持（✅）：PP、TP、DP、CP、DeepSpeed-Ulysses Parallel (UP)、Megatron-SP、mbs。
  - 即将支持（❌）：MOE、VPP、自适应重计算。
- **数据流/工作原理**（综合原文三条 bullet）：
  1. 输入：模型结构 + 集群配置 → 用内存灰盒模型剔除 OOM 配置，缩减候选集；
  2. 对候选集内每种并行策略，Cost Model 输出端到端耗时的概率分布（先验来自单算子调用，融合整网算子实测数据 + 通信耗时）；
  3. Thompson Sampling 按概率匹配方式迭代选点，"以高概率探索高价值并行配置"，可在达到时间/收益阈值时早停并推荐最优。
- **性能数据**：原文未给出具体加速比/吞吐数字，"使用效果"段仅为图片占位（图 auto_parallel_2.png），无可量化指标。

---

## 【表格解读】

原文包含一张"多维自动并行相关参数"表，逐字还原如下：

| 参数名            | 参数含义                                       |
| ----------------- | ---------------------------------------------- |
| --auto-parallel   | 多维自动并行特性总开关                          |
| --nnodes          | 集群中节点的个数                                |
| --nproc_per_node  | 每个节点中计算设备的个数                        |
| --master-addr     | 集群中主节点的 IP 地址                          |
| --master-port     | 用于通信的端口号，各节点需要配置相同的端口号     |
| --node-rank       | 集群中节点的 rank，主节点为 0，其他节点为 1,2,…… |

逐行解读：

- **--auto-parallel**：特性总开关，只有显式传入才会进入多维自动并行流程。
- **--nnodes / --nproc_per_node / --master-addr / --master-port / --node-rank**：标准的 PyTorch 分布式启动参数，分别描述集群总节点数、每节点设备数、主节点 IP、共享端口、当前节点 rank，用于拉起跨节点分布式搜索进程；与 Llama-7B 示例脚本中 `SEARCH_ARGS` 块一一对应。
- 注：表中"参数含义"原文未给出取值范围/默认值，相关限制需由调用方按集群实际环境填写。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文末标注"内部链接: (无)"，原文未提供任何内部交叉链接。但从正文内容可识别以下特性/模块的耦合关系：

- **上游被并行化的并行维度**：PP、TP、DP、SP、CP、Ulysses Parallel (UP)、VPP、EP——这些是大模型并行训练的基础算子集合，自动并行算法对其中已支持的 7 个维度（PP/TP/DP/CP/UP/SP/mbs）进行组合搜索。
- **下游对接的模型/框架**：示例脚本调用 `pretrain_gpt.py` 并传入 `--tensor-model-parallel-size`、`--pipeline-model-parallel-size`、`--sequence-parallel`、`--use-flash-attn`、`--use-fused-rmsnorm`、`--swiglu` 等参数，指向 Megatron-LM 系的 GPT 预训练入口及其 Llama2 风格配置（rope / RMSNorm / untie-embeddings / SwiGLU）。
- **已实现框架适配**：DeepSpeed-Ulysses Parallel (UP) 与 Megatron-SP 已被纳入搜索维度，说明 mindspeed 在该特性层面对二者均已打通。
- **未覆盖模块（即将支持）**：MOE（对应 EP）、VPP（虚拟流水线）、自适应重计算——表明这些特性与自动并行尚未解耦，后续可能纳入搜索维度。
- **依赖/环境**：示例脚本需 `source /usr/local/Ascend/ascend-toolkit/set_env.sh` 并设置 `NPU_ASD_ENABLE=0`，`--distributed-backend nccl`，说明其运行于昇腾 NPU + NCCL 通信后端之上。

---

## 【使用方法】

**启动前置条件（原文"使用方法"首段）**：

- 使用 **python 作为脚本启动器**，在**所有节点**上拉起脚本。
- 配置多维自动并行相关参数（见上表）。

**关键参数（来自表格与示例脚本）**：

```
--auto-parallel          # 必选，多维自动并行特性总开关
--nnodes <N>             # 集群节点数
--nproc-per-node <N>     # 每节点设备数
--master-addr <IP>       # 主节点 IP
--master-port <PORT>     # 通信端口（所有节点一致）
--node-rank <RANK>       # 当前节点 rank，主节点为 0
```

**运行约束（原文）**：算法最长搜索时间为 **8 小时**，支持灵活提前退出，无需人工干预。

**Llama-7B 配置示例（原文脚本片段）**：在标准 Megatron-LM 风格 GPT_ARGS（TP=1、PP=8、num-layers 32、hidden-size 4096、ffn-hidden-size 11008、32 heads、seq-length 2048、micro-batch-size 4、global-batch-size 256、fp16、cosine LR、RMSNorm、RoPE、SwiGLU、flash-attn 等）基础上，将 `SEARCH_ARGS` 块以 `$SEARCH_ARGS` 形式追加到 `python pretrain_gpt.py` 启动命令中，并以 `--distributed-backend nccl` 收尾，日志重定向到 `logs/search_llama_7b.txt`。

## 图文联合解读

- `auto_parallel_1.png`: **1）图示内容**：四级流水线结构——①输入（模型结构、集群信息）→②构建搜索空间（内存灰盒建模、并行配置剪枝）→③高保序性Cost Model（Shape推导、算子耗时及不确定性预测、端到端不确定性耗时建模）→④不确定性搜索（概率匹配算法、在线Profiling），后者向Cost Model回传数据形成闭环。

**2）技术结论**：系统通过"剪枝缩小空间→概率建模预测耗时→Thompson Sampling高效搜索→实测反馈迭代"四步闭环，自动化产出较优并行配置。

**3）文档呼应**：图示完整对应文档三条解决方案，印证了"以内存灰盒降维、以不确定性模型+概率匹配搜索"替代手工调优的核心论点。
- `auto_parallel_2.png`: **1) 图内容**：表格列出8个模型（7B~65B，NPU 8/16/32）的自动并行搜索结果，含搜索空间（224~835）、性能比、探索次数（1~5）、耗时（15~68min），并对比专家与自动的(pp,tp,dp,cp,up,mbs)配置。

**2) 技术结论**：自动并行在8个模型上均≥专家调优性能（4个↑1.02~1.10，4个=1.0），且仅需少量探索即可收敛，证明算法高效有效。

**3) 与论点关系**：直接验证"自动并行可替代数日~数周手工调优"的论点，体现成本与性能优势。
