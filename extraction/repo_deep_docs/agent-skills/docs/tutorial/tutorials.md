# Skills 使用教程

> 仓 `agent-skills` · 路径 `docs/tutorial/tutorials.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/docs/tutorial/tutorials.md

# 昇腾 agent-skills 仓库 docs/tutorial/tutorials.md 深度解读

---

## 【定位】

本篇文档是 **Ascend Agent Skills 教程索引页**，用于集中收录并分类展示昇腾社区为开发者提供的 7 篇使用教程（涵盖算子开发、模型迁移、框架特性适配等方向），本身不承载具体技术细节，定位为「目录/导航文档」，帮助开发者快速定位所需的学习资源。

---

## 【技术要点】

由于原文为教程索引表，技术要点从目录所列教程主题归纳：

1. **Triton Vector 算子开发**：教程标题为「1小时完成Triton Vector算子开发」，使用 Triton 语言完成 Ascend Vector 算子开发。
2. **CATLASS 融合算子开发**：教程标题为「1小时完成CATLASS融合算子开发」，使用 CATLASS（CAscade Template ATLASS）完成融合算子开发。
3. **Ascend C Vector 算子开发**：教程标题为「1小时内完成Ascend C Vector算子开发」，使用 Ascend C 编程语言完成 Vector 算子开发。
4. **BEVFormer 模型迁移训练**：教程标题为「30分钟完成BEVFormer自驾模型迁移与训练实战」，针对自动驾驶 BEV（Bird's Eye View）感知模型的迁移与训练。
5. **MindSpeed-MM FSDP2 自动迁移**：教程标题为「轻松完成MindSpeed-MM FSDP2自动迁移」，涉及 FSDP2（Fully Sharded Data Parallel v2）分布式训练策略的自动迁移。
6. **Megatron → MindSpeed 特性迁移**：教程标题为「高效实现Megatron到MindSpeed的特性迁移」，将 Megatron 框架的特性迁移到昇腾自研的 MindSpeed 框架。
7. **Mamba3 / SSM 模型适配**：教程标题为「MindSpeed LLM结合Agent-Skills适配Mamba3模型，解锁SSM模型新潜能」，将 Agent-Skills 与 MindSpeed LLM 结合以适配 Mamba3（SSM / State Space Model 架构）模型。

> 备注：上述"1小时""30分钟"为原文标题所标注的时间量级，原文未给出更细粒度的具体数字（如代码行数、参数列表、性能数据），文档中亦不展开技术机制。

---

## 【关键机制与数据】

**原文未涉及**任何具体的工作原理、数据流、性能数据、命令行参数或配置项。

本篇文档仅提供一个外链表格，每一行只包含「序号 / 教程名称 / 教程链接」三列信息，链接均指向 `mp.weixin.qq.com` 公众号文章（外部链接），未在本文档内嵌任何教程正文。因此，**无法从原文提取内部技术机制或性能数据**。

---

## 【表格解读】

**原文表格逐字还原**：

| 序号 | 教程名称 | 教程链接 |
| --- | --- | --- |
| 1 | 1小时完成Triton Vector算子开发 | [查看教程](https://mp.weixin.qq.com/s/8gJHcL85bvY6rH2EvOjrWQ) |
| 2 | 1小时完成CATLASS融合算子开发 | [查看教程](https://mp.weixin.qq.com/s/G-jvGCFo4mHcFqE4tbxC0A) |
| 3 | 1小时内完成Ascend C Vector算子开发 | [查看教程](https://mp.weixin.qq.com/s/j7PvG5Xyog4wAbOe7Vgttg) |
| 4 | 30分钟完成BEVFormer自驾模型迁移与训练实战 | [查看教程](https://mp.weixin.qq.com/s/S2PY6VYYszMmMlk8nth0bg) |
| 5 | 轻松完成MindSpeed-MM FSDP2自动迁移 | [查看教程](https://mp.weixin.qq.com/s/LwGbM2E_p6trpKVaLmq2sA) |
| 6 | 高效实现Megatron到MindSpeed的特性迁移 | [查看教程](https://mp.weixin.qq.com/s/2qmG9tqosiJsGxmaYMr4VQ) |
| 7 | MindSpeed LLM结合Agent-Skills适配Mamba3模型，解锁SSM模型新潜能 | [查看教程](https://mp.weixin.qq.com/s/4fmGfkTA6cZbK3gX29-OWw) |

**逐行解读**：

| 行 | 主题域 | 解读 |
| --- | --- | --- |
| 1 | **算子开发 — Triton** | 教程聚焦 Triton 语言开发 Ascend Vector 算子路径，标题强调"1小时"完成学习曲线。 |
| 2 | **算子开发 — CATLASS** | CATLASS 是昇腾面向融合算子（Fused Kernel）的模板库，教程强调用 CATLASS 完成融合算子，1 小时入门。 |
| 3 | **算子开发 — Ascend C** | Ascend C 是昇腾官方算子开发 DSL，教程以 Vector 算子为入口，1 小时内可掌握基本开发流程。 |
| 4 | **模型迁移 — BEV（自驾）** | BEVFormer 是经典自动驾驶 BEV 感知模型，教程覆盖"迁移 + 训练"完整实战（30 分钟量级）。 |
| 5 | **分布式训练迁移 — FSDP2** | MindSpeed-MM 是昇腾大模型多模态训练框架，本教程聚焦 FSDP2 分布式并行策略的"自动"迁移。 |
| 6 | **框架迁移 — Megatron→MindSpeed** | 将 NVIDIA Megatron-LM 框架的特性迁移到昇腾 MindSpeed，体现跨框架特性复用的"高效"路径。 |
| 7 | **大模型架构适配 — Mamba3/SSM** | 唯一一篇直接点名"Agent-Skills"作用的教程：把 Agent-Skills 作为工具，与 MindSpeed LLM 协同，解锁 SSM 类（Mamba3）模型的适配能力。 |

> **结构观察**：7 篇中，算子开发 3 篇（第 1/2/3）、模型/框架迁移 3 篇（第 4/5/6）、Agent-Skills 实战 1 篇（第 7），与目录标题"Skills 使用教程"相呼应——只有第 7 篇直接体现 Agent-Skills 在 LLM 训练链路中的角色，其余更偏昇腾生态的通用教程合集。

---

## 【公式解读】

**原文无公式**。本篇文档为目录索引，不包含任何 LaTeX 公式或伪代码形式的技术表达式。

---

## 【关联】

原文未提供任何内部链接（"内部链接: (无)"），且本文档是 `docs/tutorial/tutorials.md` 这一独立索引页，与同仓其他 Markdown 之间没有显式的交叉引用。从**教程主题间的技术关系**可归纳如下（属于上下文推断，非原文显式陈述）：

- **第 1、2、3 篇** 共同覆盖"昇腾算子开发生态"：Triton（高级 DSL）、CATLASS（融合算子模板库）、Ascend C（底层原生 DSL）三条互补路径，互为替代/分层方案。
- **第 5、6、7 篇** 共同覆盖"训练框架迁移/适配"：MindSpeed-MM（FSDP2 分布式）、MindSpeed LLM（从 Megatron 移植特性）、MindSpeed LLM（适配 Mamba3 SSM），均围绕昇腾自研的 **MindSpeed** 训练框架展开。
- **第 7 篇** 是唯一一篇明确出现 **Agent-Skills** 字样的教程，定位为 Agent-Skills 在 LLM 训练链路上的实战样例，可视为 Agent-Skills 与 MindSpeed 框架协同的"标杆案例"。

---

## 【使用方法】

**原文未涉及**任何启用方式、配置项、命令或 API 调用说明。

本文档的"使用方法"即为：**打开本文档 → 在表格中找到所需方向的教程链接 → 点击链接跳转至对应微信公众号文章进行学习**。所有教程链接的发布平台为 `mp.weixin.qq.com`，需要通过微信生态访问。文档未提供离线版本、镜像、PDF 等替代访问方式，也未标注教程的兼容性、版本要求或前置依赖。
