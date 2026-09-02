# msAgent快速入门

> 仓 `agent-skills` · 路径 `official/MindStudio/docs/zh/getting_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/MindStudio/docs/zh/getting_started/quick_start.md

# msAgent快速入门 一体化深度解读

---

## 【定位】

本文档是 msAgent 的**快速入门指南**，解决"在昇腾 NPU + CANN 环境已就绪后，如何一步步完成 LLM 后端对接配置、选择特定 Agent 能力模块并进入交互式会话"的最小可用流程问题，让用户在最短路径上启动并使用 msAgent 的各种 AI 辅助研发功能。

---

## 【技术要点】

1. **运行环境前置条件**：必须先安装昇腾 NPU 驱动与配套版本的 CANN 软件（包含 Toolkit 与 ops 包），并配置相关环境变量；之后才能安装 msAgent 本身。CANN 的安装通过外部链接《CANN 快速安装》获取。

2. **双层 LLM 配置机制**：LLM 接入由两类参数协同完成——环境变量提供鉴权凭证（如 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY`），`msagent config` 命令提供三个运行时参数：
   - `--llm-provider`：协议类型（`openai` / `anthropic` / `google`）
   - `--llm-base-url`：模型服务商地址
   - `--llm-model`：模型名称（需从模型服务商网站的"模型广场"获取）

3. **多协议 LLM 兼容**：msAgent 同时支持 4 种 LLM 服务接入形态——OpenAI 兼容接口（云端）、OpenAI 兼容接口（本地 `http://127.0.0.1:8000/v1`）、Anthropic 兼容服务、Google / Gemini 服务；本地 OpenAI 兼容服务示例使用 `OPENAI_API_KEY="dummy"` 作为占位符。

4. **配置校验机制**：通过 `msagent config --show` 回显先前步骤 2 设置的参数值，验证配置是否写入成功。

5. **Agent 能力模块化启动**：msAgent 通过 `--agent <Name>` 参数在同一交互式入口下切换 6 种能力——默认模式、`Profiler`（性能调优）、`Accuracy`（精度调试）、`Quantizer`（模型量化）、`Operator`（算子调优）、`Minos`（文档辅助），不指定则进入默认会话。

6. **典型示例参数（原文中明确给出的）**：OpenAI 兼容示例使用 `https://api.deepseek.com/v1` + `deepseek-v4-flash`；Anthropic 示例使用 `claude-sonnet-4-20250514`；Google 示例使用 `gemini-2.5-pro`。

---

## 【关键机制与数据】

本文档属于"上手操作型"文档，**未描述** msAgent 内部的 Agent 调度、Prompt 编排、模型推理调用、性能指标等机制；也未给出任何性能数据（如 token 数、时延、吞吐量等）。

可从原文中提取的"数据"仅为**示例配置参数**（即原文给出的真实可参考值）：

- 原文（OpenAI 兼容远程示例）：`--llm-base-url "https://api.deepseek.com/v1"` , `--llm-model "deepseek-v4-flash"`
- 原文（OpenAI 兼容本地示例）：`--llm-base-url "http://127.0.0.1:8000/v1"`，密钥使用 `"dummy"` 占位
- 原文（Anthropic 示例）：`--llm-provider anthropic`，模型名 `claude-sonnet-4-20250514`
- 原文（Google/Gemini 示例）：`--llm-provider google`，模型名 `gemini-2.5-pro`
- 原文：Agent 模块共 **6 个**（默认 + Profiler、Accuracy、Quantizer、Operator、Minos）

整体工作流（从原文可还原）为：① 装 CANN → ② 装 msAgent → ③ 写环境变量 API Key → ④ `msagent config` 写入 provider/url/model → ⑤ `msagent config --show` 校验 → ⑥ `msagent [--agent <Name>]` 启动会话。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档是 msAgent 的入口级文档，明确向上下游与其他文档存在如下关联（基于原文内部链接梳理）：

| 关联方向 | 文档 | 关系性质 |
|---|---|---|
| 上游（前置依赖） | 《[msAgent安装指南](./install_guide.md)》 | msAgent 本体的安装步骤，本文 §1 第 2 步指向 |
| 上游（外部） | 《[CANN 快速安装](https://www.hiascend.com/cann/download)》 | NPU 驱动 + CANN 软件包安装，本文 §1 第 1 步指向 |
| 下游（功能模块，按本文 §3 启动命令锚定） | `../agent_guide/Profiler.md` | `--agent Profiler` 进入性能调优交互式会话 |
| 下游（功能模块） | `../agent_guide/Accuracy.md` | `--agent Accuracy` 进入精度调试交互式会话 |
| 下游（功能模块） | `../agent_guide/Quantizer.md` | `--agent Quantizer` 进入模型量化交互式会话 |
| 下游（功能模块） | `../agent_guide/Operator.md` | `--agent Operator` 进入算子调优交互式会话 |
| 下游（功能模块） | `../agent_guide/Minos.md` | `--agent Minos` 进入文档辅助交互式会话 |
| 下游（命令大全） | `../user_guide/usemap.md` | 《msAgent使用指南》，本文 §3 末尾"更多命令"指向 |

可以看出本文是**用户旅程的中心枢纽文档**：上游承接安装与环境准备（`install_guide.md` + CANN 外部链接），下游以 5 条平行分支派发到具体的 Agent 能力专精文档，再以 1 条汇总性命令手册（`usemap.md`）收口。

---

## 【使用方法】

下表**逐字还原**原文中给出的全部启用方式/配置项/命令（按使用顺序排列）：

### §1 环境准备
```bash
# 1) 安装昇腾 NPU 驱动 + 配套 CANN（Toolkit + ops 包），配置环境变量
#    详见外部链接 https://www.hiascend.com/cann/download

# 2) 安装 msAgent 本体
#    详见 ./install_guide.md
```

### §2 配置 LLM

| 步骤 | 命令 / 环境变量 | 说明 |
|---|---|---|
| 2-a 准备 API Key | 用户自行在模型服务商网站创建 | 原文："需要用户自行登录模型服务商网站进行创建" |
| 2-b 设置环境变量 | `export OPENAI_API_KEY="your-key"` | OpenAI 兼容接口鉴权 |
| 2-b 设置环境变量 | `export ANTHROPIC_API_KEY="your-key"` | Anthropic 兼容服务鉴权 |
| 2-b 设置环境变量 | `export GOOGLE_API_KEY="your-key"` | Google / Gemini 服务鉴权 |
| 2-b OpenAI 兼容远程 | `msagent config --llm-provider openai --llm-base-url "https://api.deepseek.com/v1" --llm-model "deepseek-v4-flash"` | 原文示例 |
| 2-b OpenAI 兼容本地 | `msagent config --llm-provider openai --llm-base-url "http://127.0.0.1:8000/v1" --llm-model "your-model"` | 原文示例，密钥用 `"dummy"` |
| 2-b Anthropic 兼容 | `msagent config --llm-provider anthropic --llm-base-url "https://example.com/anthropic" --llm-model "claude-sonnet-4-20250514"` | 原文示例 |
| 2-b Google/Gemini | `msagent config --llm-provider google --llm-base-url "https://example.com/google" --llm-model "gemini-2.5-pro"` | 原文示例 |
| 2-c 校验配置 | `msagent config --show` | 显示先前配置即视为成功 |

### §3 启动会话

| 启动场景 | 命令 | 进入的会话类型 |
|---|---|---|
| 默认会话 | `msagent` | 默认交互式会话 |
| 性能调优 | `msagent --agent Profiler` | [Profiler 性能调优](../agent_guide/Profiler.md) 会话 |
| 精度调试 | `msagent --agent Accuracy` | [Accuracy 精度调试](../agent_guide/Accuracy.md) 会话 |
| 模型量化 | `msagent --agent Quantizer` | [Quantizer 模型量化](../agent_guide/Quantizer.md) 会话 |
| 算子调优 | `msagent --agent Operator` | [Operator 算子调优](../agent_guide/Operator.md) 会话 |
| 文档辅助 | `msagent --agent Minos` | [Minos 文档辅助](../agent_guide/Minos.md) 会话 |
| 更多命令 | （参见 ../user_guide/usemap.md） | 命令全集 |
