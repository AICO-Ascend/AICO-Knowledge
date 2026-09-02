# 推理大EP（Expert Parallel）

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/expert_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/expert_parallel.md

# 一体化深度解读：推理大EP（Expert Parallel）

---

## 【定位】
这篇文档描述了 mindspeed-rl 中面向 MoE 混合专家模型推理场景的**专家并行（Expert Parallel, EP）能力**，说明如何通过将不同专家分散部署到多卡来突破单卡显存瓶颈并提升 MoE 推理吞吐。

---

## 【技术要点】

1. **两种 EP 并行模式并存**
   - `ep_level: 1`：基于 **AllGather** 通信实现的专家并行；
   - `ep_level: 2`：基于 **AllToAll 与通算融合** 实现的专家并行。

2. **适用前提**：多个专家分布在不同设备上，每个 token 仅激活其路由所指的**局部专家**，从而天然适配并行切分。

3. **核心价值（量化指标）**
   - MoE 推理吞吐可提升 **1.5–4 倍**；
   - 通过将专家分布到更多设备，**缓解单卡显存压力**，避免单卡无法容纳全部专家参数的情况。

4. **三层协同配置**（并非单一开关，而是 general / runtime / actor 三处必须同步）：
   - `general_config` 中开启开关并指定 EP 并行度 `n`；
   - `runtime_env.yaml` 中将 `VLLM_DP_SIZE` 设为同一 `n`；
   - `actor_config` 中将 `expert_model_parallel_size` 设为同一 `n`。

5. **配置强约束**：三处参数 `infer_expert_parallel_size` / `VLLM_DP_SIZE` / `expert_model_parallel_size` **必须取同一个值 `n`**，以保持配置一致。

---

## 【关键机制与数据】

**工作原理（原文）**：
- MoE 模型将"专家"维度从模型参数中拆出，作为一种独立的并行轴；
- 专家并行把不同专家分别放到不同设备上，token 经过路由后只访问其激活的局部专家，**避免每个设备都复制全量专家参数**；
- 通信层提供两种实现路径：`ep_level: 1` 用 AllGather 收集专家信息，`ep_level: 2` 用 AllToAll 做 token–专家重排，并叠加通算融合以降低开销；
- 通过把 EP 并行度设为 `n`，相当于把全量专家集合扩展到 `n` 张设备上共同承载。

**性能数据（原文）**：
- MoE 推理吞吐提升 **1.5–4 倍**（原文表述为"1.5–4 倍"，未给出具体模型/硬件/批量下的细分数字）；
- 显存收益为定性描述：缓解单卡显存压力（原文未给出显存节省的具体百分比或 GB 数）。

---

## 【表格解读】

**原文无表格**。原文仅以代码片段形式给出了三段 YAML 配置示例，未提供任何参数对照表、性能对比表或配置项矩阵，故此节不展开。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 或伪代码形式的公式，未给出如「并行度 × 单卡专家数 = 总专家数」之类的显式表达。

---

## 【关联】

原文**未提供文末内部链接**（"内部链接: (无)"），且正文中也未显式交叉引用其他特性/模块。因此可关联的内容仅能基于原文上下文推断：

- 与 **MoE 混合专家模型**强绑定：本文讨论的所有收益（吞吐 1.5–4 倍、显存扩展）均建立在 MoE 路由 + 局部专家激活这一前提之上；
- 与 **actor 推理侧配置**（`actor_config.expert_model_parallel_size`）以及 **vLLM 运行时**（`VLLM_DP_SIZE`）耦合：文档明确要求三者保持同一 `n`，说明 EP 的开启并非单一组件行为，而是与推理引擎、Actor 框架协同生效；
- `ep_level: 1`（AllGather）与 `ep_level: 2`（AllToAll + 通算融合）构成同主题下的两种实现变体，是 EP 能力内部的分支选项而非独立特性；
- 由于原文未给出链接，无法进一步关联到诸如张量并行、流水并行等其他并行维度的具体描述。

---

## 【使用方法】

**1. 开启专家并行（`general_config`）**
```yaml
enable_expert_parallel: true
infer_expert_parallel_size: n  # n 为 EP 并行度
```

**2. 同步运行环境（`runtime_env.yaml`）**
- 将 `VLLM_DP_SIZE` 设为与 `infer_expert_parallel_size` **相同的 `n`**，以保持配置一致。

**3. 配置模型并行参数（`actor_config`）**
```yaml
expert_model_parallel_size: n  # 与上述 n 保持一致
```

**约束总结**（原文）：
- 三处 `n` 必须一致；
- `enable_expert_parallel` 须为 `true` 才生效；
- 模式选择（`ep_level: 1` / `ep_level: 2`，对应 AllGather 或 AllToAll+通算融合）以及任何与之配套的 batch、top-k、专家数量等参数，**原文未涉及**，需结合仓库其他文档或源码确认。
