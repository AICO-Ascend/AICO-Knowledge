# Web UI 前端架构演进与体验优化设计

> 仓 `msmodeling` · 路径 `docs/design/web_ui_frontend_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/web_ui_frontend_design.md

# 设计文档深度解读：Web UI 前端架构演进与体验优化设计

---

## 【定位】

本文档是一份面向 `web_ui/` 当前 Gradio Blocks 前端实现的**演进型设计 RFC**：在保持 CLI 主链路不变的前提下，识别现状问题并给出一条低风险、可分阶段落地的前端架构与体验优化路径，目标是把 Web UI 从"参数堆叠页面"演进为"面向实验分析、任务治理和专项分析的工作台"。

---

## 【技术要点】

1. **现网前端形态**：基于 Gradio Blocks 构建，位于 `http://127.0.0.1:2345/`，启动命令为 `python -m web_ui.web_ui_start --host 127.0.0.1 --port 2345`；包含 `Simulator` 与 `Optimizer` 两大入口，覆盖 `LLM Models` / `VL Models` / `Video Models` 三类仿真工作流。

2. **Text Generate 表单规模**：已接近 **70 个字段**，覆盖基础模型与设备参数、并行参数、量化参数、MoE 参数、模块级高级并行覆盖、性能模型与调试参数——已进入"专业配置台"阶段。

3. **核心数据契约**：`schemas.py` 定义的 `ExperimentTask`（任务描述）与 `ExperimentResult`（结果描述），决定前端如何把表单值组织成任务、如何统一渲染/缓存/导出结果；`ExperimentResult.source` 取值 `"run"`（真实执行）或 `"cache"`（缓存复用）。

4. **缓存与持久化路径**：`result_store.py` 基于 SQLite 存储，路径 `.msmodeling_ui/results.sqlite3`；原始日志持久化路径 `.msmodeling_ui/logs/`；缓存键基于"稳定参数哈希"生成；缓存是主链路的一部分（执行前参与任务去重与结果复用）。

5. **六层架构分层**：页面层（`app.py` / `components.py` / `styles.py`）、交互编排层（`callbacks.py`）、任务构造与执行层（`command_builder.py` / `runner.py`）、解析与持久化层（`parsers.py` / `result_store.py`）、数据与工具层（`schemas.py` / `utils.py`）、结果可视化层（`charts.py`）；产品结构演进方向为"全局层 / 工作流入口层 / 高频场景层 / 配置层 / 结果层"五层结构。

6. **安全边界强制项**：服务可驱动 `cli/inference` 下的命令入口，因此**仅本地通信、命令白名单、参数白名单必须由后端强制执行**，前端按钮禁用/文案提示不构成真实安全边界。

---

## 【关键机制与数据】

**核心数据流（文本仿真场景，原文 §4.3）**：

```
用户填写表单 → Preview/Run → callbacks.py 收集与校验参数
  → command_builder.py 生成 ExperimentTask 列表
  → result_store.py 尝试缓存命中
  → runner.py 并发执行未命中任务
  → parsers.py 解析日志并生成 ExperimentResult
  → result_store.py 持久化结果与日志
  → callbacks.py 组织 summary / charts / tables / filters
  → 页面刷新展示
```

**关键机制要点（原文 §4.4 / §5）**：

- 缓存非附属功能而是主链路一环：执行前即参与任务去重与结果复用。
- 进度组件当前仅展示 `completed / total`、百分比、状态、最新任务；总时间"沿用上一次任务时间"导致 ETA 不可信（原文 §6.1.7）。
- "并发治理"当前偏"单批次任务组并发"，尚未支持"多会话并行工作台"（原文 §6.1.8）。
- `Parallel Jobs` 与实际 worker 关系不清晰，缺全局并发池配置入口（原文 §6.2.1）。

**已通过原型验证、但不应立即进入开发的能力（原文 §4.5.3）**：过重 Hero 区摘要、过细的开发/联调显示项、多批次并行会话管理、配置资产管理（保存/加载/回填）完整能力、所有任务按钮的完整后端闭环。

**性能数据**：原文未提供性能基准数字（如吞吐、延迟、E2E 时间等），仅描述机制形态。

---

## 【表格解读】

**修订记录表（原文 §0）**：

| 日期 | 修订版本 | 修改描述 | 作者 |
| -- | -- | -- | -- |
| 2026-06-03 | v1 | 现网 `http://127.0.0.1:2345/` 与当前 HTML 原型，补充"现网能力 vs 原型能力"的差距分析 | 彭志品 |

**逐行解读**：
- **第 1 行**：本设计文档的首次（v1）发布时间为 2026-06-03，由彭志品起草；其核心工作是基于现网部署地址 `http://127.0.0.1:2345/` 与当前 HTML 原型，补充两者能力的差距分析——这是文档立题的起点，决定了后续章节必然出现"现网/原型"二元对照视角（如 §4.5 反复使用此框架）。

---

## 【公式解读】

原文无公式（无 LaTeX、无伪代码公式形式）。

文档中存在两处结构化代码块，均为**层级结构示意**而非数学/逻辑公式：

1. **六层架构文字图（§4.1）**：以 `页面层 / 交互编排层 / 任务构造与执行层 / 解析与持久化层 / 数据与工具层 / 结果可视化层` 表示文件归属关系，无运算语义。
2. **核心数据流伪代码（§4.3）**：以 `->` 串联的流水线步骤，表示数据从前端表单到页面刷新的传递路径，不是公式。
3. **产品五层结构（§8.1）**："全局层 / 工作流入口层 / 高频场景层 / 配置层 / 结果层"为目标态分层方案，原文在"基础参数 / 专项参数（MoE / Video / Advan…"处被截断，不完整。

故严格按"公式"标准判定：**原文无公式**。

---

## 【关联】

文档显式或隐式关联的模块/特性如下（均来自原文表述，未做外推）：

- **上游/核心执行链路**：`cli/inference`（被安全边界段落明确点名，要求其三个入口受后端白名单约束）。
- **CLI 主链路**：文档多处声明"不改变 CLI、解析器和执行链路"——即 Web UI 是 CLI 之上的薄编排层。
- **同仓设计文档体系**：本文件位于 `docs/design/`，标题为"Web UI 前端架构演进与体验优化设计"，按惯例与同目录其他 `docs/design/*.md`（如本仓还涉及 modeling 评估与服务化场景）属于同一设计基线。
- **专项分析能力（页面需显式产品化）**：`Video DiT Cache`、`PD Split Analysis`（§3.1）、`DiT Cache Analysis`、`PD Disaggregated` 专项结果解释（§4.5.2）。
- **被引用的现有文件清单**：`web_ui/app.py`、`web_ui/components.py`、`web_ui/styles.py`、`web_ui/callbacks.py`、`command_builder.py`、`runner.py`、`parsers.py`、`result_store.py`、`schemas.py`、`utils.py`、`charts.py`。
- **核心数据结构**：`ExperimentTask`、`ExperimentResult`（在 §4.3、§4.4 反复出现，是前后端契约）。
- **持久化路径**：`.msmodeling_ui/results.sqlite3`、`.msmodeling_ui/logs/`。
- **运行入口**：`python -m web_ui.web_ui_start --host 127.0.0.1 --port 2345`（§4.2）。
- **内部链接**：原文文末标注"（无）"。

---

## 【使用方法】

- **启动命令（原文 §4.2）**：`python -m web_ui.web_ui_start --host 127.0.0.1 --port 2345`
- **访问地址（原文 §0 / §4.2）**：`http://127.0.0.1:2345/`
- **配置文件/参数**：原文未给出 yaml/json 配置项或环境变量列表，仅声明缓存路径 `~/.msmodeling_ui/results.sqlite3` 与日志路径 `~/.msmodeling_ui/logs/`。
- **页面工作流选择**：进入后可选 `Simulator` 或 `Optimizer`，再在 Simulator 内选 `LLM` / `VL` / `Video`。
- **进阶启用项**：原文 §3.2 明确"不要求立即将 Gradio 替换为 React/Vue"、"不在本文档中重构 CLI 核心算法、性能模型或日志协议"——即**是否启用分阶段重构、何时分阶段重构，原文未给出启用开关**，仅作为设计演进路径提出。
- **未涉及项**：原文未给出具体的开关/特性 Flag/命令行参数清单（除启动命令外），也未给出 CI/CD 灰度启用方式。
