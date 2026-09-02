# Model Architecture Report Template

> 仓 `model-agent` · 路径 `skills/verification/ascend-profiling-anomaly/references/architecture_report_template.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/verification/ascend-profiling-anomaly/references/architecture_report_template.md

# Model Architecture Report Template 深度解读

## 【定位】

这篇文档是昇腾模型 Agent 中**针对大模型 Profiling 数据反向还原网络架构的 Markdown 报告模板**,规定了在执行异常发现（anomaly discovery）时,如何输出一份独立的"模型架构报告",用纯 profiling 证据链回答"这个模型是什么、各层结构如何、怎么执行的"这一问题,与异常报告（"什么看起来不自然"）形成互补。

---

## 【技术要点】

1. **报告与异常报告解耦**:架构报告是独立的 `model_architecture_report_<profiling_dir_name>.md` 文件,与 anomaly report 平行产出,前者回答"what is this model and how does it execute",后者回答"what looks unnatural"。

2. **FusedInferAttentionScore (FIA) 作为主结构标记**:以 FIA 调用次数为主结构探针——prefill FIA 时长 **>10ms**、decode FIA 时长 **<1ms**——通过次数除法推算每 pass 层数与总 pass 数,通过时间戳间隙识别 prefill→decode 阶段切换点。

3. **十节强制结构**:必须按顺序包含 ①Configuration Context ②Model Architecture Determination ③Forward Pass Boundaries ④Layer Classification ⑤Cross-Verification Table ⑥Per-Layer Sub-Structure ⑦Decode Phase Analysis ⑧Communication Pipeline Structure ⑨Layer-to-Layer Variation ⑩Model Architecture Summary。

4. **三层分类法**:基于内核序列中有无 DispatchFFNCombine / GroupedMatmul / MoeGatingTopK / alltoallv 出现,把模型分为 Dense 层（0–N）、MoE+DFC 层（N+1–M）、MoE+GMM 最后一层三类。

5. **证据链式交叉验证**:Section 4.5 的 Cross-Verification Table 给出按 pass 统计的关键 op 计数（如 FIA(prefill)=93、DispatchFFNCombine=89、GroupedMatmul=4、MoeGatingTopK=91、split_qkv_rmsnorm_rope=N、ReshapeAndCache=N+1),用来反推层归属与 MoE 边界。

6. **多 stream 重叠量化**:Section 4.8 要求解释 **kernel_sum >> wall_ms** 的成因（多流并行),通过 ASCII 管道图刻画 stream 之间的 overlap 关系,定位通信可被计算隐藏的部分。

---

## 【关键机制与数据】

### 工作原理(纯 profiling 反推)

- **从目录名 + profiling 元数据提取配置**:文档要求从 `<profiling_dir_name>` 解析出 `DP{X} × TP{Y} [with EP]`,prefill 序列长度、decode 序列长度、batch size,捕获跨度（capture span）的 `{duration}s / {kernel_count} kernels / {stream_count} streams`,以及 `{pass_count}` 个 forward pass 中包含 `{prefill_FIA_count}` 个 prefill FIA + `{decode_FIA_count}` 个 decode FIA。

- **结构证据链推导流程**(Section 4.2 原文):①Count total FIA invocations → ②Separate prefill FIA(duration>10ms) from decode FIA(duration<1ms) → ③Divide to determine layers per pass and passes per capture → ④Identify phase transition points by timestamp gaps → ⑤Present as evidence table。

- **过渡层 / 最后一层的复合结构**:Section 4.6 原文明确指出"transition/last layer"通常合并 ①Last transformer layer computation ②Output head (logit projection) ③Sampling logic (ArgMax, rejection sampling for speculative decode) ④Next-iteration input preparation (embedding, position encoding, KV cache setup) ⑤Any AICPU ops that should be flagged。

- **Decode 与 Prefill 的成本画像切换**:Section 4.7 原文举例"FIA drops dramatically (e.g., 28ms → 0.2ms)",代价主导项从 attention 切换为 EP 模型下的 all-to-all 通信,本质从 latency-bound 转为 bandwidth-bound。

- **跨 pass 变化监测**:Section 4.3 原文要求"Note any cross-pass variation (e.g., FIA duration increasing across passes due to KV cache growth)"。

- **同类型层内的方差**:Section 4.9 原文举例"DFC ranging from 5.4ms to 14.8ms across MoE layers"。

> 注:除上述 FIA 阈值（10ms / 1ms）、FIA 下降示例（28ms → 0.2ms）、DFC 方差示例（5.4ms–14.8ms）、过渡层占时示例（87ms）等之外,文档未给出具体模型或基准性能数据,其余数字均属于模板占位符 `{...}` 或表格示例行。

---

## 【表格解读】

### 表 1:Section 4.4 Layer Classification(原文逐字还原)

| Layer Type | Layers | Count | Characteristics |
|---|---|---|---|
| Dense | 0–N | K | No MoE routing; attention → projection → norm → FFN (direct MatMul) |
| MoE+DFC | N+1–M | J | Full MoE layers with DispatchFFNCombine for fused expert routing+compute |
| MoE+GMM | M+1 (last) | 1 | MoE with GroupedMatmul instead of DFC; includes output head, sampling, decode prep |

**逐行解读**:
- **Dense 行**:占据连续层号区间 `[0, N]`,共 `K` 层。特征是"无 MoE 路由",即数据流遵循 `attention → projection → norm → FFN (direct MatMul)`,FFN 通过普通 MatMulV3 实现而非专家路由。
- **MoE+DFC 行**:占据 `[N+1, M]` 区间,共 `J` 层。识别标志是存在 `DispatchFFNCombine`,它把"路由 + 专家计算"融合为单个内核,因此只需一次内核调用就完成原本需要 gather/MatMul/scatter 三步的工作。
- **MoE+GMM 行**:仅最后一层（即 `M+1`,Count=1),用 `GroupedMatmul` 取代 `DispatchFFNCombine`,并额外承担 `output head`（logit 投影）、`sampling`、`decode prep` 三件套——这是单层特例,需特别标注。

---

### 表 2:Section 4.5 Cross-Verification Table(原文逐字还原)

| Op | Per Pass Count | Interpretation |
|---|---|---|
| FIA (prefill) | 93 | 1 per layer |
| DispatchFFNCombine | 89 | Layers 3–91 only (MoE layers) |
| GroupedMatmul | 4 | 2 in transition layer + 2 in decode |
| MoeGatingTopK | 91 | 89 prefill MoE + 2 decode |
| split_qkv_rmsnorm_rope | N | Present in layers with next-layer prep |
| ReshapeAndCache | N+1 | KV cache updates |

**逐行解读**:
- **FIA(prefill)=93**:表明该模型有 93 层(prefill 阶段每层恰好一次 attention 内核),即从总 FIA 数减去 decode FIA 数得到。
- **DispatchFFNCombine=89**:MoE+DFC 层共 89 层,对应 Section 4.4 表的 `Layers 3–91`,故前 3 层(0–2)被反推为 Dense 层,最后一层(92)走 GMM 路径而非 DFC。
- **GroupedMatmul=4**:`2 in transition layer + 2 in decode`,说明 transition 层用到 2 次 GMM,decode 阶段也用到 2 次——这是 EP 模型中常见的门控 + 专家权重矩阵分别走的 GMM 路径。
- **MoeGatingTopK=91**:`89 prefill MoE + 2 decode`,等于 MoE 层数 + decode 阶段的 2 次路由计算,与 DFC 计数 89 完全自洽。
- **split_qkv_rmsnorm_rope=N**:仅出现在需要为下一层做准备的层,通常除最后一层外每层 1 次,因此总量=N(总层数减一)。
- **ReshapeAndCache=N+1**:KV cache 更新比层数多 1 次,因为最后一层之后还会写一次 cache(对应下一 decode 步的 K0/V0),形成 N+1 的尾数差。

---

### 表 3:Section 4.9 Layer-to-Layer Variation(原文逐字还原)

| Metric | Dense (0–2) | MoE+DFC (3–91) | Transition (92) | Decode |
|---|---|---|---|---|
| Wall time | X ms | Y ms (avg) | Z ms | W ms |
| FIA share | A% | B% | C% | D% |
| DFC cost | 0 | V ms | 0 | 0 |
| Post-FIA compute | ... | ... | ... | ... |
| Kernels per layer | ... | ... | ... | ... |

**逐行解读**:
- **Wall time 行**:四类层各自的端到端墙钟时长,X/Y/Z/W 都是占位,文档要求"Y"取 MoE+DFC 类的平均值(因为同类型层内存在方差)。
- **FIA share 行**:FIA 在该类层中所占时间比例(Attention 占总墙钟的份额)。Decode 阶段该比例会显著下降(原 Section 4.7 提及 28ms → 0.2ms 的剧烈下降)。
- **DFC cost 行**:Dense 和 Transition 层为 0(无路由融合),MoE+DFC 行为 V ms(典型方差 5.4–14.8ms,如原 Section 4.9 注释)。
- **Post-FIA compute 行**:FIA 之后的 RMSNorm/Quant/AllGather 等收尾计算。
- **Kernels per layer 行**:每类层一个完整 forward 涉及的 kernel 个数,用于识别复杂度跳变点(例如过渡层通常 kernel 数明显多于普通 MoE 层,因为它叠加了 sampling + decode prep)。

---

### 表 4:Section 4.7 Decode Dominant Costs(模板要求但原文无完整示例)

> 原文:"Provide a **dominant costs table** with Component | Duration (ms) | Share"。表格列定义明确,但具体行内容未给出。

**逐行解读**:Section 4.7 要求 decode 层给出一张 Component × Duration × Share 表,行内容由实际 profiling 填入,通常包含:Decode FIA、all-to-all 通信(EP 模型)、GroupedMatmul、Sample、KV cache 更新等。原文中仅承诺"Highlight the key contrast: FIA drops dramatically (e.g., 28ms → 0.2ms)",数值示例来自 28ms → 0.2ms 这一过渡点。

---

## 【公式解读】

原文无 LaTeX 公式,亦无伪代码形式数学公式。文档中的所有"计算"都是流程性文字(参见 Section 4.2 的 5 步推导步骤),未给出代数表达式。判定:**原文无公式**。

---

## 【关联】

文档中**未提供任何内部链接或交叉引用**——文末 Internal Links 字段标注"(无)"。Section 9 / Section 10 章节中以"对比 prefill / decode"措辞提及两个阶段,但都限定在本文件内部表格之间,未跨文件引用其他模块。

如需映射到外部模块,从命名与上下文可推测(非原文断言,仅作下游使用提示):
- 与 `anomaly report` 平行产出(原文明确"separate from the anomaly report");
- 输入数据来源是 profiling 目录中的 kernel trace + 目录名 metadata(`<profiling_dir_name>`);
- 依赖的内核原语名(`DispatchFFNCombine` / `GroupedMatmul` / `MoeGatingTopK` / `FusedInferAttentionScore` / `split_qkv_rmsnorm_rope` / `ReshapeAndCache`)暗示该报告对接昇腾 CANN profiling 输出。

---

## 【使用方法】

### 启用方式

1. 在执行 `ascend-profiling-anomaly` 流程、产出异常发现结果的同时,**额外生成一份独立的 Markdown 架构报告**。
2. 文件名严格遵循:
   ```
   model_architecture_report_<profiling_dir_name>.md
   ```
   示例:`model_architecture_report_0313_dp2_tp8_ep_100k_1k_bs10.md`
3. 放置位置:`profiling directory` 或 `working output directory`。

### 强制配置项 / 模板项(原文 Section 3 枚举)

报告必须按顺序包含十节:
1. Configuration Context
2. Model Architecture Determination
3. Forward Pass Boundaries
4. Layer Classification
5. Cross-Verification Table
6. Per-Layer Sub-Structure
7. Decode Phase Analysis
8. Communication Pipeline Structure
9. Layer-to-Layer Variation
10. Model Architecture Summary

### 分类阈值 / 参数(原文给出的硬编码)

- prefill FIA 判定阈值:**duration > 10ms**
- decode FIA 判定阈值:**duration < 1ms**
- 文件名占位变量:`<profiling_dir_name>`(原 profiling 目录名,例如 `0313_dp2_tp8_ep_100k_1k_bs10`)
- 维度占位:`DP{X} × TP{Y} [with EP]`、`{prefill_len}`、`{decode_len}`、`{N}`(batch size)、`{duration}`(秒)、`{kernel_count}`、`{stream_count}`、`{model_type}`、`{layer_count}`、`{pass_count}`、`{prefill_FIA_count}`、`{decode_FIA_count}`

### 调用 / 运行命令

**原文未涉及任何 CLI 命令、可执行脚本或 API 调用方式**——文档定位为报告模板与产出规范,不描述如何触发生成。判定:配置项与产出规则已列出,执行命令层面**原文未涉及**。
