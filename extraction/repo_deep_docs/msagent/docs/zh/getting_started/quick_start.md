# msAgent快速入门

> 仓 `msagent` · 路径 `docs/zh/getting_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msagent/docs/zh/getting_started/quick_start.md

# msAgent 快速入门文档深度解读

## 【定位】

这篇文档是 msAgent（MindStudio 智能体）的零门槛上手指南，目标是把"环境准备 → LLM 配置 → 启动会话 → 交互技巧"四个环节串成最小可用闭环，让首次使用者能在数分钟内完成模型配置、选择 Agent 功能、进入交互式会话并掌握核心 slash 命令。

---

## 【技术要点】

- **一键安装脚本**：通过 `curl ... install.sh`（Linux/macOS/WSL）与 `irm ... install.ps1`（Windows PowerShell 5.1+）两条命令完成 msAgent 自身安装，源指向 `raw.gitcode.com/Ascend/msagent/raw/master/scripts/`。
- **LLM 配置三件套**：通过环境变量（`*_API_KEY`，具体为 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY`）持有凭据，然后由 `msagent config` 命令的 `--llm-provider`、`--llm-base-url`、`--llm-model` 三个参数锁定协议类型、服务商地址、模型名称；最后用 `msagent config --show` 校验是否生效。
- **四种 LLM 协议接入场景**：OpenAI 兼容接口、本地 OpenAI 兼容服务（无需密钥时可填任意非空字符串，例如 `dummy`）、Anthropic 兼容服务、Google / Gemini 服务；模型示例包括 `deepseek-v4-flash`、`claude-sonnet-4-20250514`、`gemini-2.5-pro`。
- **六类内置 Agent 入口**：通过 `msagent --agent <Name>` 在启动时切换，分别对应 Profiler（性能调优）、Accuracy（精度调试）、Quantizer（模型量化）、Modeling（仿真建模与自动寻优）、Operator（算子调优）、Minos（文档辅助）；不指定则进入默认会话。
- **Skill 双层调用模型**：内置 Skill 通过 `/skills` 交互式列表浏览加载，亦可 `/skills <skill-name>` 或 `/skills <skill-name> <prompt>` 直接调用（示例：`/skills ascend-computation-analysis 帮我根据性能数据分析有无计算类的瓶颈`）；自定义 Skill 通过 `/add-skill <path-to-skill>` 从本地路径即时安装。
- **六大 slash 命令**：会话线程 `/threads`、技能加载 `/skills`、自定义技能 `/add-skill`、全屏工具输出 `/tool-output`（同 `Ctrl+O`）、长期记忆 `/remember` 与 `/showmemory`，共同构成交互界面。

---

## 【关键机制与数据】

- **会话线程持久化**：原文：「会话历史会自动保存为独立线程，可随时浏览并恢复到之前的会话继续工作。」`/threads` 命令以"按时间倒序展示预览摘要"的方式列出所有线程（原文：「打开会话线程列表，按时间倒序展示预览摘要」）。
- **Skill 的语义**：原文：「Skill 是面向特定场景的专项能力模块（如性能分析、模型量化等）。」它通过 `/skills` 打开交互式列表，上下键浏览、回车加载。
- **自定义 Skill 即装即用**：原文：「除了内置 Skill，用户也可通过 `/add-skill` 从本地路径安装自定义 Skill」，支持指定 Skill 目录或 `SKILL.md` 文件，路径形态如 `/add-skill /path/to/my-skill`，「安装后立即生效」。
- **全屏工具输出查看器行为**：原文：「当 Agent 执行工具调用产生的输出较长时（如日志、配置文件、代码块等），输入 `/tool-output` 可在全屏查看器中浏览完整内容，避免输出截断影响阅读。」快捷键为 `Ctrl+O`，支持多输出左右切换、上下键/`PageUp`/`PageDown` 滚动、`Enter`/`Ctrl+O`/鼠标点击展开折叠、`Esc` 关闭。
- **长期记忆的物理落盘**：原文：「记忆会写入 `~/.msagent/state/projects/<project-id>/memory.md`，后续会话会自动读取。」`/remember <content>` 为追加语义，示例为 `/remember 用户希望默认使用中文回答`。
- **多轮上下文保护机制**：原文：「上下文窗口有限，进行多轮复杂任务时，建议在关键节点触发结论记录，避免早期分析结果被后续交互挤出窗口。」提供了一段示范 Prompt 让 Agent 在 Skill 完成一轮分析后输出 Markdown 报告，并指出「当后续触发上下文压缩时，可直接重新读取该报告作为上下文基础」。
- **敏感信息策略**：原文：「不要保存 API Key、密码、令牌等敏感信息。」——这是 `/remember` 的使用边界。
- **本地 LLM 服务的占位密钥**：原文：「如本地模型服务无密钥，可填入任意非空字符串」，示例值为 `dummy`。

> 注：性能数据、吞吐、时延等指标在原文中均未出现，本文不做臆造。

---

## 【表格解读】

### 表格 1：常见模型服务商

> 原文：

| 模型服务商   | 官网链接                               |
|---------|------------------------------------|
| DeepSeek | [https://platform.deepseek.com/](https://platform.deepseek.com/) |
| 百炼 | [https://help.aliyun.com/zh/model-studio/get-api-key](https://help.aliyun.com/zh/model-studio/get-api-key) |

**逐行解读**：

- **DeepSeek** 行：指引用户前往其开放平台门户 `platform.deepseek.com` 创建 API Key，是后续以 OpenAI 兼容协议接入 `https://api.deepseek.com` 的前置动作。
- **百炼** 行：指向阿里云百炼模型工作室帮助文档中"获取 API Key"的具体页面，配合示例 `https://api.deepseek.com` 等价于 OpenAI 兼容接口的接入路径。

### 表格 2：LLM 配置场景

> 原文：

| 配置场景 | 示例 |
| --- | --- |
| OpenAI 兼容接口 | `export OPENAI_API_KEY="your-key"`<br>`msagent config --llm-provider openai --llm-base-url "https://api.deepseek.com" --llm-model "deepseek-v4-flash" # 以DeepSeek为例` |
| 本地 OpenAI 兼容服务 | `export OPENAI_API_KEY="dummy"  # 如本地模型服务无密钥，可填入任意非空字符串`<br>`msagent config --llm-provider openai --llm-base-url "http://127.0.0.1:8000/v1" --llm-model "your-model"` |
| Anthropic 兼容服务 | `export ANTHROPIC_API_KEY="your-key"`<br>`msagent config --llm-provider anthropic --llm-base-url "https://example.com/anthropic" --llm-model "claude-sonnet-4-20250514"` |
| Google / Gemini 服务 | `export GOOGLE_API_KEY="your-key"`<br>`msagent config --llm-provider google --llm-base-url "https://example.com/google" --llm-model "gemini-2.5-pro"` |

**逐行解读**：

- **OpenAI 兼容接口行**：覆盖了"环境变量 + msagent config 两步走"的范式：先用 `OPENAI_API_KEY` 注入密钥，再用 `--llm-provider openai` 声明协议，以 `--llm-base-url` 指定厂商网关（示例 `https://api.deepseek.com`），以 `--llm-model "deepseek-v4-flash"` 锁定具体模型。"以 DeepSeek 为例"表明该行为通用 OpenAI 兼容厂商的代表示例。
- **本地 OpenAI 兼容服务行**：演示了无鉴权场景的兜底做法——`OPENAI_API_KEY="dummy"` 是占位字符串，`--llm-base-url "http://127.0.0.1:8000/v1"` 指向本地常驻模型服务，`--llm-model "your-model"` 由用户替换为本地服务实际暴露的模型名。
- **Anthropic 兼容服务行**：环境变量切换为 `ANTHROPIC_API_KEY`，`--llm-provider anthropic` 触发 Anthropic 协议分支，`--llm-model "claude-sonnet-4-20250514"` 是 Anthropic Claude Sonnet 4 的具体版本号（时间戳形式命名 `20250514`）。
- **Google / Gemini 服务行**：环境变量为 `GOOGLE_API_KEY`，`--llm-provider google` 对应 Gemini 协议分支，模型示例 `gemini-2.5-pro` 表明对应 Gemini 2.5 Pro 系列；`--llm-base-url` 中的 `https://example.com/google` 是文档占位符。

### 表格 3：Agent 启动命令

> 原文：

| Agent | 说明 | 启动命令 |
| --- | --- | --- |
| [Profiler](../agent_guide/Profiler.md) | 性能调优 | `msagent --agent Profiler` |
| [Accuracy](../agent_guide/Accuracy.md) | 精度调试 | `msagent --agent Accuracy` |
| [Quantizer](../agent_guide/Quantizer.md) | 模型量化 | `msagent --agent Quantizer` |
| [Modeling](../agent_guide/Modeling.md) | 仿真建模与自动寻优 | `msagent --agent Modeling` |
| [Operator](../agent_guide/Operator.md) | 算子调优 | `msagent --agent Operator` |
| [Minos](../agent_guide/Minos.md) | 文档辅助 | `msagent --agent Minos` |

**逐行解读**：

- **Profiler 行**：定位"性能调优"，是 msAgent 在 MindStudio 体系中负责性能分析的主入口，对应链接 `../agent_guide/Profiler.md`。
- **Accuracy 行**：定位"精度调试"，负责数值精度相关问题的诊断与修复，对应 `../agent_guide/Accuracy.md`。
- **Quantizer 行**：定位"模型量化"，负责模型权重量化与压缩流程，对应 `../agent_guide/Quantizer.md`。
- **Modeling 行**：定位"仿真建模与自动寻优"，是更广义的"系统建模 + 调参寻优"能力的封装，对应 `../agent_guide/Modeling.md`。
- **Operator 行**：定位"算子调优"，聚焦单个算子（Kernel）级别的优化策略，对应 `../agent_guide/Operator.md`。
- **Minos 行**：定位"文档辅助"，承担知识问答、文档辅助检索等非性能/精度类任务，对应 `../agent_guide/Minos.md`。
- **整体观察**：六个 Agent 形成"性能/精度/量化/建模/算子/文档"的完整能力矩阵，每个 Agent 都是独立的工作流而非简单模式开关。

### 表格 4：`/threads` 命令

> 原文：

| 命令 | 说明 |
| --- | --- |
| `/threads` | 打开会话线程列表，按时间倒序展示预览摘要。 |

**逐行解读**：唯一一行展示了"会话历史持久化"功能的访问入口；"按时间倒序展示预览摘要"意味着该视图不直接恢复线程，而要先选目标线程再决定恢复——这是典型的"先浏览再载入"交互范式。

### 表格 5：`/skills` 命令集

> 原文：

| 命令 | 说明 |
|---|---|
| `/skills` | 打开交互式 Skill 列表，上下键浏览、回车加载。 |
| `/skills <skill-name>` | 直接指定 Skill 名称加载，如 `/skills ascend-computation-analysis`。 |
| `/skills <skill-name> <prompt>` | 加载 Skill 并传入任务执行，如 `/skills ascend-computation-analysis 帮我根据性能数据分析有无计算类的瓶颈`。 |

**逐行解读**：

- 第1 行 `/skills`：等价于"图形化选 Skill"模式，列出所有 Skill 以供浏览。
- 第2 行 `/skills <skill-name>`：跳过浏览直接加载指定的 `ascend-computation-analysis` Skill，示例表明 Skill 命名采用"领域-能力-动作"风格。
- 第3 行 `/skills <skill-name> <prompt>`：在加载 Skill 的同时直接传入任务 prompt，示例 prompt「帮我根据性能数据分析有无计算类的瓶颈」是一个面向性能分析 Skill 的典型提问。

### 表格 6：`/add-skill` 命令

> 原文：

| 命令 | 说明 |
|---|---|
| `/add-skill <path-to-skill>` | 从本地路径安装 Skill 目录，如 `/add-skill /path/to/my-skill`。 |

**逐行解读**：唯一一行明确"路径"是必填参数，形态既支持 Skill 目录也支持 `SKILL.md` 单文件（原文：「支持指定 Skill 目录或 `SKILL.md` 文件」），典型路径形如 `/path/to/my-skill`。

### 表格 7：`/tool-output` 查看器操作

> 原文：

| 操作 | 说明 |
| --- | --- |
| `/tool-output` 或 `Ctrl+O` | 打开全屏工具输出查看器。 |
| 左右方向键 | 切换多个工具输出。 |
| 上下方向键、`PageUp`/`PageDown` | 滚动内容。 |
| `Enter` / `Ctrl+O` / 鼠标点击 | 展开或折叠完整输出。 |
| `Esc` | 关闭查看器。 |

**逐行解读**：

- 第1 行：触发器有两种——slash 命令 `/tool-output` 与快捷键 `Ctrl+O`，入口路径一致。
- 第2 行：左右方向键用于"多输出切换"，说明 Agent 可能并发执行多个工具调用，需要在结果之间跳转。
- 第3 行：上下键配合 `PageUp`/`PageDown` 提供粗/细两种滚动粒度，适合长日志阅读。
- 第4 行：`Enter`/`Ctrl+O`/鼠标点击统一复用为"展开折叠"动作，与第 1 行的"打开查看器"形成"双模语义"——同一快捷键在不同模式下含义不同。
- 第5 行：`Esc` 是标准的"关闭"语义，与多数全屏查看器一致。

### 表格 8：`/remember` 命令集

> 原文：

| 命令 | 说明 |
| --- | --- |
| `/remember <content>` | 追加一条长期记忆，如 `/remember 用户希望默认使用中文回答`。 |
| `/showmemory` | 查看当前项目已保存的长期记忆。 |

**逐行解读**：

- 第1 行 `/remember <content>`：`content` 是必填项；语义为"追加"（不是覆盖），示例「用户希望默认使用中文回答」展示了典型的"用户偏好"类记忆。
- 第2 行 `/showmemory`：只读命令，用于回看当前项目的全部长期记忆；语义对象是"当前项目"（对应 `~/.msagent/state/projects/<project-id>/memory.md` 这一项目级文件）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档内部链接形成的"能力地图"如下：

- **安装前置**：[`./install_guide.md`](./install_guide.md) —— 文档第 1 节末尾明确指引"更多安装方式，具体请参见《msAgent 安装指南》"，与本文档第 1 节的"一键安装"形成"快速路径 + 完整路径"的互补关系。
- **六大 Agent 详细文档**：第 3 节的 Agent 启动命令表通过超链接指向上层目录 `../agent_guide/` 下的六份独立指南：
  - [`Profiler.md`](../agent_guide/Profiler.md) —— 性能调优 Agent 的使用说明；
  - [`Accuracy.md`](../agent_guide/Accuracy.md) —— 精度调试 Agent 的使用说明；
  - [`Quantizer.md`](../agent_guide/Quantizer.md) —— 模型量化 Agent 的使用说明；
  - [`Modeling.md`](../agent_guide/Modeling.md) —— 仿真建模与自动寻优 Agent 的使用说明；
  - [`Operator.md`](../agent_guide/Operator.md) —— 算子调优 Agent 的使用说明；
  - [`Minos.md`](../agent_guide/Minos.md) —— 文档辅助 Agent 的使用说明。
- **使用手册总入口**：[`../user_guide/usemap.md`](../user_guide/usemap.md) —— 在第 3 节末尾（"更多命令请参见《msAgent 使用指南》"）与第 4 节末尾（"更完整的命令和快捷键说明请参见《msAgent 使用指南》"）被引用两次，承担"完整 slash 命令/快捷键手册"的入口角色。

**整体关联视图**：本文档（quick_start.md）是入口级 onboarding；上层六大 Agent 文档是"按垂直能力展开"的能力手册；user_guide/usemap.md 是"按横向命令/快捷键展开"的工具手册；install_guide.md 是部署前置。三者与 quick_start.md 形成"先安装 → 再快速启动 → 按需深入 Agent 能力或查阅命令手册"的导航闭环。

---

## 【使用方法】

> 以下命令均按原文逐字保留。

**1. 安装**

```shell
# Linux / macOS / WSL
curl -LsSf https://raw.gitcode.com/Ascend/msagent/raw/master/scripts/install.sh | bash

# Windows（PowerShell 5.1+）
irm https://raw.gitcode.com/Ascend/msagent/raw/master/scripts/install.ps1 | iex
```

**2. 配置 LLM**

```bash
# OpenAI 兼容接口
export OPENAI_API_KEY="your-key"
msagent config --llm-provider openai --llm-base-url "https://api.deepseek.com" --llm-model "deepseek-v4-flash"

# 本地 OpenAI 兼容服务
export OPENAI_API_KEY="dummy"
msagent config --llm-provider openai --llm-base-url "http://127.0.0.1:8000/v1" --llm-model "your-model"

# Anthropic 兼容服务
export ANTHROPIC_API_KEY="your-key"
msagent config --llm-provider anthropic --llm-base-url "https://example.com/anthropic" --llm-model "claude-sonnet-4-20250514"

# Google / Gemini 服务
export GOOGLE_API_KEY="your-key"
msagent config --llm-provider google --llm-base-url "https://example.com/google" --llm-model "gemini-2.5-pro"

# 查看当前配置
msagent config --show
```

**3. 启动会话**

```bash
msagent                                    # 默认交互式会话
msagent --agent Profiler                   # 性能调优
msagent --agent Accuracy                   # 精度调试
msagent --agent Quantizer                  # 模型量化
msagent --agent Modeling                   # 仿真建模与自动寻优
msagent --agent Operator                   # 算子调优
msagent --agent Minos                      # 文档辅助
```

**4. 会话内 slash 命令**

```bash
/threads                                   # 打开会话线程列表（按时间倒序）

/skills                                    # 打开交互式 Skill 列表（上下键浏览、回车加载）
/skills <skill-name>                       # 直接加载 Skill，如 /skills ascend-computation-analysis
/skills <skill-name> <prompt>              # 加载 Skill 并传入任务，如 /skills ascend-computation-analysis 帮我根据性能数据分析有无计算类的瓶颈

/add-skill <path-to-skill>                 # 从本地路径安装 Skill（支持目录或 SKILL.md 文件），如 /add-skill /path/to/my-skill

/tool-output                               # 打开全屏工具输出查看器（等效 Ctrl+O）
Ctrl+O                                     # 打开/展开折叠 全屏查看器
左右方向键                                    # 切换多个工具输出
上下方向键 / PageUp / PageDown             # 滚动内容
Enter                                      # 展开或折叠完整输出
Esc                                        # 关闭查看器

/remember <content>                        # 追加一条长期记忆，如 /remember 用户希望默认使用中文回答
/showmemory                                # 查看当前项目已保存的长期记忆
```

**5. 推荐的多轮 Prompt 模板（原文提供的示例）**

> 请根据上述分析结果，输出一份完整的 Markdown 分析报告，包含问题摘要、根因分析、关键数据和优化建议。

> 注意：原文明确提示"不要保存 API Key、密码、令牌等敏感信息"，且本地 OpenAI 兼容服务场景下"如本地模型服务无密钥，可填入任意非空字符串"。

## 图文联合解读

- `threads.png`: **图文联合解读：**

1) **图像内容**：终端界面显示 `Profiler > /threads` 命令视图，提示用户"Select a thread to restore. Use Up/Down and press Enter."（选择要恢复的线程，使用上下键和回车键）。列表中有一条高亮会话记录：`[57 minutes ago] 今天天气怎么样`。

2) **技术结论**：证明 msAgent 内置 Profiler 工具具备**会话持久化与历史回溯能力**，用户可通过 `/threads` 子命令浏览过往对话，并基于时间戳快速定位与恢复。

3) **与文档关系**：快速入门主要讲环境准备与 LLM 配置，本图作为完成配置后的**最小可用交互成果展示**，印证"进入 msAgent 最小可用的交互流程"这一核心论点——配置成功后用户即可发起对话（询问天气），并通过 Profiler 随时管理会话历史，体现产品的完整闭环能力。
- `skills_browser.png`: **图文联合解读：**

1) **画面内容**：终端界面 `Profiler > /skills`，提示「Enter: select skill | Tab: expand/collapse」，下列出 7 个可选用技能（skill）：`ascend-communication-analysis`、`ascend-computation-analysis`、`ascend-schedule-analysis`、`ascend_pytorch_profiler_db_explorer`、`cluster-fast-slow-rank-detector`、`github-raw-fetch`、`mindstudio_profiler_data_check`，每项附有触发场景的简短说明。

2) **技术结论**：msAgent 采用「技能（skill）模块化」架构，按 Ascend NPU profiling 数据的不同维度（通信/计算/调度/集群诊断/数据校验/外部拉取）封装为独立可调用单元，支持运行时动态选用。

3) **与文档关系**：对应引言中「选择 Agent 功能」的步骤——通过 `/skills` 交互入口让用户在进入最小可用交互流程前，按 profiling 场景按需挂载对应技能，体现"按需装配、即选即用"的设计。
- `add_skill.png`: **图文联合解读：**

1) **图示内容**：终端截图，展示三行——①输入命令 `/add-skill "/home/ylb/test-skill/"`；②系统返回 ✅ 提示，已将技能安装至 `/home/ylb/msagent/.msagent/skills/test-skill` 并为 `Profiler` agent 启用；③空命令提示行，下方附带斜杠指令提示（询问Profiler、@ 引用文件、/ 使用命令）。

2) **技术结论**：演示 msAgent 的"技能（Skill）动态加载"机制——通过斜杠命令即可挂载外部 skill 目录，并即时对指定 agent 启用，存储于 `.msagent/skills/` 目录下。

3) **与文档关系**：佐证文档"快速入门"的"最小可用交互流程"，证明配置 LLM 后用户可在 REPL 中以 `/` 命令扩展 agent 能力，无需重启即可热加载。
- `tool_output.png`: **图示解读（≤150字）：**

图示终端界面展示msAgent内置MCP工具**msprof-mcp_execute_sql**的第40次调用记录，结构包含三段：①顶部导航提示（左右切换/上下滚动/折叠）；②Args区显示`db_path`指向Ascend PyTorch Profiler数据库及SQL语句（JOIN PYTORCH_API与STRING_IDS，按API聚合耗时TOP25）；③Output区返回JSON结果（row_count=0、columns=["api_name","total_us"]）。

**论证结论**：msAgent可通过MCP协议对昇腾性能剖析数据库执行SQL查询，验证了Agent的工具调用与数据检索能力。

**与文档关系**：印证"配置LLM → 启动 → 进入最小可用交互流程"路径，证明安装后即可用自然语言驱动性能分析场景。
