# Web UI 重构设计文档（Vue 3 + FastAPI）

> 仓 `msmodeling` · 路径 `docs/design/web_ui_refactor_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/web_ui_refactor_design.md

# Web UI 重构设计文档深度解读

## 【定位】

本文档定义 `web_ui/` 从 Gradio Blocks 单体架构迁移到 Vue 3 + FastAPI + SQLite 前后端分离架构的重构设计基线，作为后续演进的架构参考。

---

## 【技术要点】

1. **前端框架**：Vue 3（`<script setup>` 组合式 API）+ Element Plus（企业级组件 + 暗色主题）+ ECharts 5 / vue-echarts（散点图/柱状图/主题感知）+ Pinia + reactive composables（无 boilerplate 轻量状态管理）+ Vite 6（ESM 原生 + 快速 HMR）。

2. **后端栈**：FastAPI（异步 + 自动 OpenAPI + Pydantic 校验）+ SQLite（WAL mode，零配置本地单机）+ Alembic（版本化 schema 管理）+ pytest + pytest-cov（**100% 后端覆盖率**目标）。

3. **核心交互范式**：表单配置驱动（`config/forms/*.ts` 作为 source of truth，不硬编码 UI）+ 动态 SchemaForm 渲染 + 跨字段校验依赖图 + 多值字段自动 cartesian product 展开为多用例。

4. **任务生命周期**：`useJobRunner.ts` 实现提交→轮询→结果全链路；后端 Job Manager + Runner 通过 subprocess + 进程池执行 `cli/inference/*` 下的 CLI 命令；任务运行时锁定模块标签页切换（Toast 提示）。

5. **结果组件架构**：`useResultComponent.ts` 实现模块→结果组件路由；结果组件按 mode 感知渲染（如 ThroughputOptimizer 区分 AggregatedView/DisaggregatedView/PDRatioView/OptimizerCurves）；ResultPane 状态机：idle/running/succeeded/failed。

6. **插件系统**：`plugins/contract.py` 定义 MsmdPlugin 数据契约；通过 `entry_points` 机制自动发现插件；插件可贡献菜单项/app-bar 按钮/全局浮窗，并触发 Alembic 自动迁移路径发现。

---

## 【关键机制与数据】

### 数据流（原文：第 2.1 节系统分层）

浏览器（Vue 3 SPA：Pages + Components + Composables）通过 **HTTP (axios)** 调用 FastAPI 后端的 API Router → Services → Runners 三层；Runners 通过 **subprocess** 调用 CLI 层（`cli/inference/text_generate` / `video_generate` / `throughput_optimizer`）。

### 任务生命周期（原文：第 2.4 节 Console 页）

- **表单配置驱动**：字段从 `config/forms/*.ts` 动态生成，分组折叠（通用/请求/并行/量化/MoE/高级并行/调试），控件支持 text/number/select/multi-select/switch。
- **多值展开**：逗号分隔列表自动展开为多用例（原文示例：`device=A,B` → 2 个 case）。
- **结果面板状态机**：idle（空占位）/ running（旋转图标 + 状态）/ succeeded（结果组件）/ failed（错误告警）。
- **提交反馈**：提交成功 → Toast 通知（原文在"Task submitted successfully"处被截断）。
- **运行时锁**：任务运行中阻止切换模块标签页（Toast 提示）。

### 关键架构决策（原文：第 1.1 节重构动机）

| 维度 | Gradio 旧版 | Vue 3 + FastAPI 新版 |
|---|---|---|
| 文件组织 | `app.py` + `callbacks.py` 集中所有逻辑 | 前后端分离，职责拆分到独立模块 |
| 参数传递 | 回调依赖长参数列表 | TypeScript 接口 + Pydantic schema |
| 状态管理 | `gr.State` 散落各处 | Vue 3 reactive + Pinia store |
| 结果展示 | 通用表格 | 模块化结果组件 + mode 感知渲染 |
| 任务治理 | 缺少任务中心 | Job 生命周期 + 历史 + 轮询 |
| 安全边界 | 前后端职责模糊 | 后端强约束 + 前端纯展示 |

### 测试指标（原文：第 1.2 节技术选型）

原文明确目标：**100% 后端覆盖率**（pytest + pytest-cov）。

---

## 【表格解读】

### 表 1：修订记录（原文第 1 节首表）

| 日期 | 修订版本 | 修改描述 | 作者 |
|---|---|---|---|
| 2026-07-28 | v1 | 从 Gradio 迁移到 Vue 3 + FastAPI 架构的重构设计文档 | zwt |

**逐行解读**：本文档为 v1 初始版本，2026-07-28 发布，由 zwt 撰写，记录从 Gradio 向 Vue 3 + FastAPI 架构迁移的设计基线，无后续修订记录。

### 表 2：重构动机对比（原文第 1.1 节）

| 问题 | Gradio 现状 | 重构后 |
|---|---|---|
| **文件膨胀** | `app.py` + `callbacks.py` 集中所有逻辑 | 前后端分离，职责拆分到独立模块 |
| **位置参数传递** | 回调依赖长参数列表 | 类型安全的 TypeScript 接口 + Pydantic schema |
| **状态管理分散** | `gr.State` 散落各处 | Vue 3 reactive + Pinia store |
| **结果展示** | 通用表格，专项语义弱 | 模块化结果组件，mode 感知渲染 |
| **任务治理** | 缺少任务中心 | Job 生命周期管理 + 历史 + 轮询 |
| **安全边界** | 前后端职责模糊 | 后端 FastAPI 强约束 + 前端纯展示 |

**逐行解读**：
- **文件膨胀**：旧版仅 2 个文件承担全部前后端逻辑，新版按 API Router/Services/Runners 等职责拆分。
- **参数传递**：Gradio 的位置参数容易因顺序错乱引发 bug，TypeScript 接口 + Pydantic 提供编译期与运行期双重类型保护。
- **状态管理**：`gr.State` 在回调间隐式传递，Vue 3 reactive + Pinia store 提供显式响应式状态。
- **结果展示**：通用表格无法表达 ThroughputOptimizer 等场景的 mode 语义（Aggregated/Disaggregated/PD Ratio/Optimizer Curves），新版支持模块化路由。
- **任务治理**：旧版无历史追溯，新版通过 Job 生命周期 + 历史 + 轮询实现完整任务中心。
- **安全边界**：Gradio 模式下前后端耦合导致权限边界模糊，FastAPI 后端可做强约束，前端仅做展示。

### 表 3：技术选型（原文第 1.2 节）

| 层 | 技术 | 理由 |
|---|---|---|
| 前端框架 | Vue 3 (`<script setup>`) | 组合式 API，轻量，生态成熟 |
| UI 库 | Element Plus | 企业级组件，暗色主题支持 |
| 图表 | ECharts 5 + vue-echarts | 散点图 / 柱状图 / 主题感知 |
| 状态管理 | Pinia + reactive composables | 轻量，无 boilerplate |
| 构建 | Vite 6 | 快速 HMR，ESM 原生 |
| 后端框架 | FastAPI | 异步、自动 OpenAPI、Pydantic 校验 |
| 数据库 | SQLite (WAL mode) | 零配置，本地单机 |
| 迁移 | Alembic | 版本化 schema 管理 |
| 测试 | pytest + pytest-cov | 100% 后端覆盖率 |

**逐行解读**：
- **Vue 3**：`<script setup>` 语法糖降低组合式 API 使用门槛。
- **Element Plus**：与 Vue 3 配套的企业级组件库，原生支持暗色主题切换。
- **ECharts 5**：通过 `ChartWrapper.vue` 封装实现主题感知（light/dark 切换时图表同步）。
- **Pinia**：替代 Vuex，去除 mutation 等 boilerplate。
- **Vite 6**：HMR 提升开发体验，ESM 原生适合现代浏览器。
- **FastAPI**：Pydantic 模型即请求/响应 schema，自动生成 OpenAPI 文档。
- **SQLite WAL**：Write-Ahead Logging 模式提升并发读写性能，适合本地单机部署。
- **Alembic**：与 SQLModel ORM 配套，支持版本化迁移与插件自动发现。
- **pytest-cov**：覆盖率目标 100%，作为后端质量门槛。

### 表 4：全局层（App Shell）能力（原文第 2.4 节）

| 能力 | 说明 |
|---|---|
| 顶部导航栏 | 品牌标识 + 主页/文档/历史 导航按钮 |
| 语言切换 | 中文 / English 实时切换（内联双语，非 vue-i18n） |
| 主题切换 | 亮色 / 暗色 实时切换（CSS 变量 + ECharts 主题同步） |
| 插件导航 | 插件贡献的菜单项 / app-bar 按钮 / 全局浮窗（动态发现） |
| 任务运行时锁 | 任务运行中阻止切换模块标签页（Toast 提示） |

**逐行解读**：
- **顶部导航**：基础品牌展示 + 三大主入口路由（主页/文档/历史）。
- **语言切换**：实现方式为内联双语资源对象（key → `{zh, en}`），而非引入 vue-i18n 库，减少依赖体积。
- **主题切换**：通过 `styles/theme.css` 的 CSS 变量驱动，配合 `useChartTheme.ts` 让 ECharts 同步切换主题。
- **插件导航**：基于 `plugins/loader.py` 的 entry_points 发现机制，插件可贡献 UI 元素。
- **运行时锁**：防止任务中途切换模块导致上下文丢失，通过 Toast 反馈用户。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文末内部链接 `../zh/install_guide/msmodeling_install_guide.md`：

- **上下游关联**：
  - 本文档是 Web UI 重构的架构基线，**安装指南**（`zh/install_guide/msmodeling_install_guide.md`）依赖本文档定义的目录结构（`web_ui/frontend/`、`web_ui/backend/`）来描述安装与启动流程。
  - 文档提到被替代的旧设计 `web_ui_frontend_design.md`（Gradio 版本），本文档是其后续演进。
  - 通过 CLI 层 `cli/inference/text_generate`、`cli/inference/video_generate`、`cli/inference/throughput_optimizer` 与底层建模寻优引擎对接。
  - 插件系统（`plugins/`）通过 entry_points 机制扩展新模块，新插件的 schema 注册由 `schema_registry.py` 管理。
  - 通过 Alembic 迁移（`migrations/versions/0001_initial_schema.py`）管理数据库 schema 演进。

---

## 【使用方法】

原文未涉及具体的启用命令或配置项说明（原文在"提交成功 → Toast 通知 `Task submitted successfully"处被截断，后续启用/配置/命令章节未呈现）。读者应参考关联的安装指南文档 `../zh/install_guide/msmodeling_install_guide.md` 获取部署与启动细节。
