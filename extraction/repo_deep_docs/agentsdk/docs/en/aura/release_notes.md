# Version Mapping

> 仓 `agentsdk` · 路径 `docs/en/aura/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agentsdk/docs/en/aura/release_notes.md

# Agent SDK 26.0.0 (Beta) Release Notes 深度解读

## 【定位】
本篇文档是 Agent SDK 26.0.0 Beta 版的发行说明（changelog），描述该版本的产品版本映射、与 Ascend HDK / CANN 的版本兼容矩阵、本次新增能力范围，以及升级影响和配套用户指南入口，本质上是面向集成与运维侧的"版本变更与兼容性清单"。

## 【技术要点】
1. **产品定位**：发布主体为 **Agent SDK 26.0.0**，版本类型为 **Beta 版本**；该版本作为 **MindSDK** 家族成员与 Ascend HDK **26.0.RC1**、CANN **9.0.0** 及各自补丁版本保持兼容。
2. **配套硬件收敛**：本版本所有新增特性（5 项）均显式声明仅兼容 **Atlas 800T A2 training server**，未涉及其他硬件形态。
3. **LLM 训练侧新能力**：新增对 **Qwen2.5 7B** 模型在 **WebSearcher Agent** 场景下的微调支持。
4. **强化学习训练栈扩展**：新增基于 **GAIA2** 数据集的 **GRPO** 训练支持；并引入 **verl** 训练后端引擎作为可选 backend。
5. **Agent 框架集成**：与 **LangGraph**（agent development frontend framework）完成集成，作为前端框架对接入口。
6. **训练效率机制**：新增 **context trajectory compression management**（上下文轨迹压缩管理）以及 **step-level RL training algorithms**（步进级强化学习训练算法）两项能力。

## 【关键机制与数据】
- **原文**：版本兼容声明为 "Agent SDK: This version has no compatibility issues."，即与既有组件无冲突。
- **原文**：软件版本兼容性的 NOTE 解释 —— "Software version compatibility means that when you upgrade the product software version, related software does not need to be upgraded or patched, and existing features remain supported."，即升级 Agent SDK 后，CANN / Ascend HDK 的关联产品无需强制升级或补丁，已有特性继续可用。
- **原文**：所有变更类别（Interface Changes / Key Feature Changes / Resolved Issues / Known Issues / Usage Precautions / Upgrade Impact / Vulnerability Patch List）均标记为 **None**，意味着本版本在接口、关键特性回归、缺陷修复、已知问题、升级冲击与漏洞补丁维度没有需要公告的事项，整体变更集中在"新增能力"。
- **原文**：Virus Scan Results = "Virus scan passed."。

## 【表格解读】

### 表 1：Product Version Information（原文 HTML 表格转写）

| Product      | Version | Version Type |
|--------------|---------|--------------|
| Agent SDK    | 26.0.0  | Beta version |

逐行解读：
- **Product = Agent SDK**：发布对象为 Agent SDK 组件，属于 MindSDK 体系下的 Agent 训练/部署 SDK。
- **Version = 26.0.0**：本次发布的具体语义化版本号为大版本 26 的首个版本。
- **Version Type = Beta version**：明确标注为 Beta 版，提示稳定性尚未达 GA，需评估生产可用性边界。

### 表 2：Related Product Version Mapping

| Product      | Version   |
|--------------|-----------|
| Ascend HDK   | 26.0.RC1  |
| CANN         | 9.0.0     |

逐行解读：
- **Ascend HDK 26.0.RC1**：底层驱动/固件侧需匹配的 RC1 版本，对应本次 Agent SDK 26.0.0。
- **CANN 9.0.0**：计算架构（CANN）侧需匹配的 9.0.0 主版本；下游的"软件版本兼容性表"进一步允许该版本及其 patch。

### 表 3：Software version compatibility（**Table 1**）

| MindSDK Version   | MindSDK Version to Upgrade | CANN Version Compatibility                                       | Ascend HDK Version Compatibility                                  |
|-------------------|----------------------------|------------------------------------------------------------------|-------------------------------------------------------------------|
| Agent SDK 26.0.0  | N/A                        | CANN 9.0.0 and its patch versions                                | Ascend HDK 26.0.RC1 and its patch versions                        |

逐行解读：
- **MindSDK Version = Agent SDK 26.0.0**：被升级的本体版本。
- **MindSDK Version to Upgrade = N/A**：不存在"先升到中间版本再升 26.0.0"的中间路径，可直接部署该版本。
- **CANN Version Compatibility = CANN 9.0.0 and its patch versions**：CANN 9.0.0 主线及其补丁版均兼容，无需强制升级。
- **Ascend HDK Version Compatibility = Ascend HDK 26.0.RC1 and its patch versions**：Ascend HDK 26.0.RC1 主线及补丁版均兼容。

### 表 4：New Features

| Feature     | Description                                                                          | Compatible Product Models       |
|-------------|--------------------------------------------------------------------------------------|---------------------------------|
| Agent SDK   | Supports fine-tuning the Qwen2.5 7B model for the WebSearcher Agent scenario.        | Atlas 800T A2 training server   |
| Agent SDK   | Supports GRPO training on the GAIA2 dataset.                                         | Atlas 800T A2 training server   |
| Agent SDK   | Integrates with the LangGraph agent development frontend framework.                 | Atlas 800T A2 training server   |
| Agent SDK   | Supports the `verl` training backend engine.                                        | Atlas 800T A2 training server   |
| Agent SDK   | Supports context trajectory compression management and step-level RL training algorithms. | Atlas 800T A2 training server |

逐行解读：
- **Qwen2.5 7B + WebSearcher Agent 微调**：将 7B 规模的 Qwen2.5 模型针对"网页检索 Agent"这一具体业务场景进行微调，属于垂直化能力落地。
- **GAIA2 + GRPO 训练**：使用 GAIA2 这一基准/数据集，叠加 GRPO（Group Relative Policy Optimization）这一强化学习算法进行训练，是典型的 RL 训练通路扩展。
- **LangGraph 前端框架集成**：与 LangGraph（agent development frontend framework）完成集成，意味着 Agent SDK 可作为 LangGraph 后端/底层训练能力提供者。
- **`verl` 训练后端引擎**：显式标注为 backend engine 的 verl 引擎被纳入支持，是新增的 RL/Agent 训练执行后端。
- **context trajectory compression + step-level RL**：在更长上下文的轨迹（trajectory）维度引入压缩管理，并把 RL 训练粒度推进到 step-level，目的是在长程 Agent 任务中兼顾显存/上下文效率与训练粒度。
- **统一硬件列**：所有 5 项新特性都收敛在 Atlas 800T A2 training server，硬件支持面本次未扩展。

### 表 5：26.0.0 Documentation

| Document                                                | Description                                                                                                          | Update Notes                                                                          |
|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| [Agent SDK 26.0.0 User Guide](../../../aura/README.md)  | Describes the introduction, installation and deployment, quick start, API reference, and other common operations of Agent SDK. | For details about the changes, see [Agent SDK 26.0.0 User Guide](../../../aura/README.md). |

逐行解读：
- **Document**：唯一指向 `../../../aura/README.md` 的用户指南。
- **Description**：该指南覆盖 introduction、installation and deployment、quick start、API reference 等通用操作内容。
- **Update Notes**：变更详情请直接查看同一份 26.0.0 User Guide，即本 changelog 与 README 之间为"概览 ↔ 详尽"的对应关系。

## 【公式解读】
原文无公式。

## 【关联】
- **与底层依赖栈的耦合**：本次变更的可用性以 CANN 9.0.0（含补丁）与 Ascend HDK 26.0.RC1（含补丁）为前置条件，二者通过"Software version compatibility"形成强绑定关系；其中 CANN 9.0.0 也作为顶层"Related Product Version Mapping"出现，说明这是横跨多个 MindSDK 组件的统一基线。
- **与生态前端框架的耦合**：新增的 LangGraph 集成把 Agent SDK 与上层 agent 开发框架（LangGraph）打通，使 SDK 的训练/推理能力可被外部 agent 应用直接编排。
- **与训练后端的耦合**：`verl` 引擎与 GRPO + step-level RL 训练算法、context trajectory compression 共同构成"RL/Agent 训练栈"，互相依赖：GRPO 与 step-level RL 需要 verl 之类的后端来执行，而 trajectory compression 则为长上下文 RL 提供可行性。
- **与数据集/模型的耦合**：Qwen2.5 7B 与 GAIA2 数据集分别定义了"被微调的基座模型"与"RL 训练的评测/训练数据"，二者共同决定本版本的能力边界。
- **文档关联**：原文中"26.0.0 Documentation"小节明确将变更细节指向 `../../../aura/README.md`（用户指南），即 changelog 与用户指南互为入口；本次提供的两条内部链接（`../../../aura/README.md`、`../../../aura/README.md`）均指向同一份 README，无其他模块交叉链接。

## 【使用方法】
原文未涉及具体的启用命令、配置项或参数。文档仅在"Usage Precautions"中声明 **None**，未给出 CLI 指令、配置文件 key、环境变量或 SDK 初始化方式；具体的安装、部署、API 调用与启动步骤需参考指向的 [Agent SDK 26.0.0 User Guide](../../../aura/README.md)。
