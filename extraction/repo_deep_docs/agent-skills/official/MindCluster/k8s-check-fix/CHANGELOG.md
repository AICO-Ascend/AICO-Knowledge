# 更新日志

> 仓 `agent-skills` · 路径 `official/MindCluster/k8s-check-fix/CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/MindCluster/k8s-check-fix/CHANGELOG.md

# `k8s-check-fix` CHANGELOG v1.0.0 深度解读

## 【定位】
本文档是 `k8s-check-fix` 技能（Agent Skills 仓库首个发布版本，发布日期 2026-03-25）的更新日志，描述该技能为 AI Agent 提供的 **Kubernetes 集群诊断与安全修复能力**——以六个诊断子命令为核心、以严格白名单和用户确认为安全门禁、以结构化 JSON 为输出约定的一套可远程、可多集群、可渐进披露的运维辅助技能。

---

## 【技术要点】

1. **六个诊断子命令**：`sweep`（全集群健康检查，涵盖节点/问题 Pod/告警事件/组件状态）、`pod`（Pod 深入排查：描述/日志/上一次日志/事件/镜像版本差异）、`deploy`（Deployment 分析：滚动状态/历史版本/ReplicaSet/事件）、`resources`（资源压力：节点使用率/Top Pod/缺少限制的 Pod）、`events`（近期事件汇总与 Top 原因）、`fix`（安全修复，需 `--confirm`，白名单仅六类 kubectl 命令）。
2. **写操作白名单（仅六类）**：`rollout undo`、`rollout restart`、`scale`、`delete pod`、`cordon`、`uncordon`；`kubectl exec` 被完全禁用。
3. **默认只读 + 用户确认门禁**：所有诊断命令只读；写操作必须完整展示命令并等待用户明确同意；可通过配置开启 **会话级只读模式**进一步禁止所有写操作。
4. **远程执行与多集群**：通过 SSH 在跳板机运行 `kubectl`，参数为 `--remote-host`、`--remote-key`、`--remote-user`；使用 `--context` 切换集群上下文。
5. **环境预检**：启动前检查 `kubectl`、`jq` 与集群连通性（含远程 SSH 链路）；自动识别 RBAC 权限不足并给出友好提示。
6. **防注入与无凭证泄露**：所有参数通过 `jq --arg` 传递且变量加双引号；输出中不含 kubeconfig 路径、token、Secret 内容。
7. **渐进式披露结构**：`guides/faults/` 收录六类故障恢复指南（etcd 集群故障、API Server 证书过期、kube-scheduler 故障、Worker 节点宕机、kubelet 证书过期、CNI 插件故障）；另有 `pod_checks.md`、`node_checks.md`、`deployment_checks.md`、`network_checks.md`、`security_notes.md`；`gotchas.md` 记录常见诊断陷阱；输出模板覆盖通用诊断报告、Pod 详细检查、Deployment 分析、修复计划确认及输出风格指南。
8. **配置与持久化**：`config.json` 持久化用户偏好（默认上下文、命名空间、只读模式）。
9. **模块化脚本架构**：主入口 `scripts/k8s-check-fix.sh`（参数解析与路由）；共享库 `scripts/lib/`（公共函数/k8s 封装/远程执行/预检）；子命令实现 `scripts/subcommands/`（六个子命令各一）。
10. **依赖**：`kubectl`（本地或远程）、`jq`（本地）、SSH 客户端（仅远程执行模式）。
11. **文档矩阵**：`SKILL.md`（AI 助手使用指南）、`README.md`（用户概览）、`SECURITY.md`（安全策略/威胁模型/RBAC 建议）、`CHANGELOG.md`（本文件）。

---

## 【关键机制与数据】

- **诊断-修复两段式工作原理**：诊断侧由 `sweep / pod / deploy / resources / events` 五个只读子命令采集 JSON 数据，AI 据此定位问题；修复侧仅 `fix` 一个子命令承担写操作，且严格受白名单约束——形成"只读分析 → 计划展示 → 用户确认 → 执行"的闭环。
- **数据流**：所有命令输出统一为结构化 JSON，便于 AI 直接解析；参数经 `jq --arg` 注入避免 shell 注入；远程模式经 SSH 通道将 `kubectl` 调用转发至跳板机执行。
- **安全机制**：白名单（六类 kubectl 子命令）+ 黑名单（`kubectl exec`）+ 会话级只读模式（配置项）+ 输出脱敏（去除 kubeconfig 路径/token/Secret 内容）构成四层防线。
- **预检数据点**：启动期校验对象包括 `kubectl` 可用性、`jq` 可用性、集群连通性（含远程 SSH）；遇 RBAC 权限不足即以友好提示阻断而非裸报错。
- **原文无性能数据**：本 changelog 未给出吞吐量、延迟、扫描耗时等性能指标。

---

## 【表格解读】

**原文无表格。**

> 说明：原文中"六个诊断子命令""白名单六类 kubectl 命令""guides/faults/ 六个恢复指南""脚本架构三层目录"等均以列表/分项形式陈述，未以表格呈现，故按要求标注"原文无表格"，不做臆造。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **本技能作为 Agent Skills 仓库首个发布版本（v1.0.0）**：changelog 明确标注"首次发布"，意味着该技能是该仓库的基线能力，后续版本将在此基础上迭代。
- **子技能 / 子命令间的协作关系**：六个子命令在同一入口脚本 `scripts/k8s-check-fix.sh` 下路由；共享库 `scripts/lib/` 为所有子命令提供公共函数、k8s 封装、远程执行、预检能力，体现"主入口 + 共享库 + 子命令实现"的三层依赖关系。
- **文档-脚本-模板的三角支撑**：
  - `SKILL.md` 指引 AI 助手如何调用本技能；
  - `README.md` 提供用户侧概览；
  - `SECURITY.md` 描述威胁模型与 RBAC 建议，约束技能调用边界；
  - `gotchas.md` 与各 `guides/*.md`（`faults/` 六篇 + `pod_checks.md` / `node_checks.md` / `deployment_checks.md` / `network_checks.md` / `security_notes.md`）构成 AI 模型的知识增量与行为准则来源；
  - 输出模板（通用诊断报告、Pod 详细检查、Deployment 分析、修复计划确认、输出风格指南）则保证各子命令产物风格一致、便于 AI 解析。
- **上下游关系**：上游——`kubectl` / `jq` / SSH 客户端；下游——AI Agent 通过解析 JSON 输出并结合 guides / gotchas / security_notes 决定后续动作；远程模式下，技能 → SSH → 跳板机 → kubectl → Kubernetes API Server 形成调用链。
- **内部链接**：原文未提供内部链接（标注"内部链接: (无)"）。

---

## 【使用方法】

以下启用方式、配置项与命令均直接来自原文：

1. **调用入口**：通过主脚本 `scripts/k8s-check-fix.sh` 启动，按参数解析路由到对应子命令。
2. **六个子命令用法**：
   - `sweep` – 全集群健康检查；
   - `pod` – Pod 深入排查；
   - `deploy` – Deployment 分析；
   - `resources` – 资源压力检测；
   - `events` – 近期事件汇总；
   - `fix` – 安全修复（**必须**带 `--confirm`）。
3. **远程执行参数**：`--remote-host`、`--remote-key`、`--remote-user`（用于 SSH 跳板机运行 `kubectl`）。
4. **多集群切换**：`--context` 指定集群上下文。
5. **配置持久化**：通过 `config.json` 设置默认上下文、命名空间、只读模式（即可启用**会话级只读模式**禁止所有写操作）。
6. **修复安全约束**：写操作仅允许六类 kubectl 命令（`rollout undo`、`rollout restart`、`scale`、`delete pod`、`cordon`、`uncordon`）；`kubectl exec` 完全禁用；执行前必须完整展示命令并等待用户明确同意。
7. **环境前置条件**：`kubectl`（本地或远程）、`jq`（本地）、SSH 客户端（仅远程模式）；启动时自动预检其可用性与集群连通性。
8. **文档入口**：`SKILL.md`（AI 助手使用指南）、`README.md`（用户概览）、`SECURITY.md`（安全策略与威胁模型）、`gotchas.md`（常见诊断陷阱）、`guides/faults/`（六类故障恢复指南）以及 `guides/{pod_checks,node_checks,deployment_checks,network_checks,security_notes}.md`。

> **原文未涉及**的具体参数值（如超时阈值、JSON schema 字段定义、配置文件默认字段名、guides 各篇的具体步骤）均未在本文档给出，需查阅仓库中相应文件方可获取。
