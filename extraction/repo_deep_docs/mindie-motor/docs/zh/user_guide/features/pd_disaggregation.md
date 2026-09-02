# PD分离说明

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/pd_disaggregation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/pd_disaggregation.md

# 「PD 分离」feature 文档深度解读

## 【定位】
本文档面向使用昇腾自研推理集群管理框架（mindie-motor）的用户，定义并解释 **PD 分离（Prefill & Decode 分离）** 这一部署架构——将 LLM 推理的 Prefill 与 Decode 两阶段拆分到不同实例运行，以提高 NPU 利用率与吞吐。

---

## 【技术要点】

1. **PD 分离的核心定义**：把 LLM 推理的 **Prefill（预填充）** 与 **Decode（解码）** 两个阶段拆分到**不同实例**上运行；适用于"对时延和吞吐要求较高"的场景。
2. **Prefill 阶段特性**：对输入 prompt 执行**一次完整前向传播**，生成初始 Hidden States；属性为**计算密集型**；**每个新输入序列都需执行一次 Prefill**。
3. **Decode 阶段特性**：基于 Prefill 结果**逐步生成后续 token**，每步仅计算最新 token 的激活与 attention，单步计算量较小，但需**反复执行直至生成结束**；属性为**访存密集型**（以 **KV Cache 等内存访问**为主）。
4. **多机 PD 分离部署方案**：采用 Kubernetes（K8s）架构，通过 K8s Service 为 Coordinator 暴露推理入口，使用多个 Deployment 分别部署三类角色。
5. **角色拓扑**：**Controller（单 Pod）**——负责集群与实例管理；**Coordinator（单 Pod）**——接收用户请求并调度至 P/D 实例；**Server**——**P 实例与 D 实例各若干 Pod**，由 P 实例与 D 实例协同完成一次完整推理。
6. **业务收益**：原文列出三条优势——资源利用更优（计算/带宽资源分别匹配 Prefill/Decode 特性）、吞吐能力提升（Prefill 处理新请求与 Decode 处理已有请求并行）、时延更可控（减少排队与等待，尤其在高并发下）。

---

## 【关键机制与数据】

- **工作原理（数据流）**（原文:）：用户请求经 K8s Service 入口到达 **Coordinator（单 Pod）** → Coordinator **调度至 P 实例**执行 Prefill（前向传播生成 Hidden States）→ P 实例与 **D 实例协同**完成一次完整推理 → D 实例基于 Prefill 结果**逐步生成 token**，每步仅处理最新 token 的激活与 attention，**反复执行直至生成结束**，过程中以 **KV Cache** 为主要访存对象。
- **节点/Pod 拓扑（原文:）**：
  - Controller：**单 Pod**
  - Coordinator：**单 Pod**
  - Server：**P 实例若干 Pod + D 实例若干 Pod**
  - 入口：K8s Service 暴露 Coordinator
- **性能/收益数据（原文）**：原文未给出量化数字（如具体吞吐提升百分比、时延降低毫秒数等），仅给出**定性表述**："在相同时延下提升整体吞吐"、"提高 NPU 利用率，减轻 Prefill 与 Decode 分时复用带来的相互干扰"、"尤其在高并发场景下有助于降低时延"。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未提供任何内部链接（文末标注"内部链接: (无)"），因此本节仅依据正文文本梳理**文档内部提及的关联组件**，不臆测外部模块：

- **Controller**：负责**集群与实例管理**，是 PD 分离部署中的控制平面角色（单 Pod）。
- **Coordinator**：负责**接收用户请求并调度至 P/D 实例**，是 PD 分离部署中的入口与调度角色（单 Pod，通过 K8s Service 暴露）。
- **Server（P 实例）**：执行 **Prefill 阶段**（计算密集型）。
- **Server（D 实例）**：执行 **Decode 阶段**（访存密集型，依赖 KV Cache）。
- **KV Cache**：Decode 阶段**反复执行**过程中所依赖的内存数据结构（原文表述为"KV Cache 等内存访问"）。
- **K8s Service**：为 Coordinator 暴露推理入口的网络组件。

> 说明：上述均为**原文内文相互引用**，不属于文末给出的内部链接；文末给出的内部链接清单为空，故无法补充更多跨特性/跨模块的指引。

---

## 【使用方法】

原文未涉及。

> 原文仅对 PD 分离的**概念、阶段含义、部署拓扑（Controller/Coordinator/Server 三类 K8s 资源）与优势**作说明性描述，未提供具体的**启用开关、配置文件项、命令行/参数、API 调用或 Helm/Operator 安装步骤**。如需启用方式，需参考 mindie-motor 仓库中的部署/运维相关文档（本文档未给出相应链接）。
