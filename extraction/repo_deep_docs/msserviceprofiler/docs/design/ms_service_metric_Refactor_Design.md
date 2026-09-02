# ms-service-metric 可扩展指标架构重构设计文档

> 仓 `msserviceprofiler` · 路径 `docs/design/ms_service_metric_Refactor_Design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/docs/design/ms_service_metric_Refactor_Design.md

```markdown
【定位】
本文档描述 `ms-service-metric` 指标采集架构的完整重构方案，将 Core 与框架业务（vLLM-Ascend）解耦，通过 Python Entry Point 接入 Provider 插件、支持多 YAML 加载与配置目录拆分，并以 Overlay/Exclusive 两种所有权模式实现渐进迁移，最终让最终用户在不修改任何包的情况下按目录拆分 YAML 并加载外部 Handler。

---

【技术要点】

1. **三层扩展架构**：Core（Hook/配置合并/Provider 发现/事务式重载） + Framework Provider（vLLM-Ascend 自维护 YAML 与 Handler） + User Config（单文件或单目录 YAML，由现有环境变量加载）。
2. **Provider Entry Point 发现**：Core 使用 `importlib.metadata.entry_points()` 发现 `ms_service_metric.providers` 组；vLLM-Ascend 在 `setup.py` 中以 `"vllm-ascend = vllm_ascend.observability.ms_metrics:get_metric_provider"` 形式注册，并在工厂函数内部惰性导入 `ms_service_metric.provider_api`，避免对 Core 形成硬依赖。
3. **两种所有权模式**：默认 `ownership_mode="overlay"`（Provider 实际声明的 symbol 整体替换，Core/Adapter 兜底其余 symbol）；迁移完成后可显式设为 `"exclusive"`，先按 `owned_symbol_prefixes` 过滤 Core 兜底再加载 Provider。
4. **Provider 描述符与默认值**：Core 定义 frozen dataclass `MetricProvider`，默认 `priority=100`、默认 `ownership_mode="overlay"`，字段含 `config_paths` / `framework_package` / `owned_symbol_prefixes` / `handler_module_prefixes`。
5. **多 YAML 与打包**：Provider 目录下 `provider.py` 对 `config/*.yaml` 排序后生成 `config_paths`，并在 `setup.py` 用 `package_data={"vllm_ascend.observability.ms_metrics": ["config/*.yaml"]}` 将 YAML 打入 Wheel。
6. **配置加载顺序与去重**：Core 默认 → Adapter 兜底 → Active Provider → 框架级用户配置（如 `MS_SERVICE_METRIC_VLLM_CONFIG`）→ 全局用户配置 `MS_SERVICE_METRIC_CONFIG_PATH`，最后做默认值填充与语义去重；去重基于 Handler 引用、有效名称、版本范围、Metric 名称/类型/表达式/桶/labels 的内部指纹，**不要求 YAML 增加 `id` 字段**。
7. **事务式重载与冲突策略**：配置和 Handler 重载失败时恢复上一次已提交状态；同名 Provider 全部跳过；存在 Exclusive 且 owned prefix 相互包含时冲突双方均跳过；Provider 按 `(priority, name)` 稳定排序。
8. **不新增环境变量**：用户扩展仍使用现有 `MS_SERVICE_METRIC_CONFIG_PATH`（支持单文件或单目录）。

> 注：原文在 3.8 节末尾（"Metric 类型、名称、labels、buckets "后）被截断，本次解读仅覆盖可见部分。

---

【关键机制与数据】

**1. 总体架构数据流**（对应 3.1 mermaid 图）：

```
Adapter/Core fallback YAML ─┐
Python Entry Point (vLLM-Ascend) ──► ProviderRegistry ──► SymbolConfig
Single YAML / YAML Directory ────────────────────────────┘
                                │
                                ▼
                         Semantic Dedup
                                ▼
                          MetricHandler
                                ▼
                       SymbolHandlerManager
                                ▼
                         MetricsManager ──► vLLM /metrics
```

`base_metrics.yaml` 与 `eplb_metrics.yaml` 通过 Python Entry Point `H` 汇入 `ProviderRegistry B`；`Framework Handlers K` 直接连入 `MetricHandler E`；最终所有指标经 `MetricsManager G` 暴露到 vLLM `/metrics` 端点。

**2. 配置加载流水线**（对应 3.7 mermaid 图）：

```
Core Default ──► Adapter Fallback ──►{Provider Active?}
                                       ├─ No  ──► Keep Fallback
                                       ├─ Overlay ──► Replace Contributed Symbols
                                       └─ Exclusive ──► Filter Owned Prefixes and Load Provider
                                  ──► Framework User Config
                                  ──► Global User Config
                                  ──► Fill Defaults & Semantic Dedup
```

**3. Provider 生命周期与版本 Gap**：Core 已合入重构但 vLLM-Ascend 未合入 Provider 时，Core 找不到 `ms_service_metric.providers` Entry Point，**继续加载原 Adapter YAML 与通用 Handler**，指标保持可用（原文：2.1 节 "Core 单独升级"）。Provider PR 失败、YAML 无效或 Handler 导入失败时 Provider 整体跳过、保留 Core 兜底（原文：2.2 节 "Provider 渐进迁移"）。

**4. 语义指纹组成**（原文 3.7 节）：Handler 引用或默认 Handler；显式有效名称；版本范围和 lock patch；Metric 名称、类型、表达式、桶和 labels。原文明确：**省略默认值与显式写出相同默认值会得到相同指纹**；同一 Handler 但 metrics 或 labels 不同会得到不同指纹并允许同时生效。

**5. Provider 校验范围**（原文 3.8 节，可见部分）：描述符字段类型、非空值和 ownership mode；YAML 路径必须为普通文件，文件不能为空；symbol 格式和 owned prefix 归属；Handler 必须来自稳定 Core 门面或 `handler_module_prefixes`。

**6. 性能/量化数据**：原文未提供任何具体性能数据、QPS 数字或延迟指标。

---

【表格解读】

**表 3.3-1：`MetricProvider` 字段含义**（原文逐字还原）：

| 字段 | 含义 |
|---|---|
| `name` | Provider 唯一名称，用于排序、日志和冲突识别 |
| `config_paths` | Provider 提供的一个或多个 YAML 绝对路径 |
| `priority` | Provider 加载顺序，数值越小越先处理 |
| `framework_package` | 需要版本过滤时用于读取框架安装版本 |
| `owned_symbol_prefixes` | Provider 声明可维护的 symbol 模块前缀 |
| `handler_module_prefixes` | Provider 自有 Handler 的允许导入前缀 |
| `ownership_mode` | `overlay` 渐进迁移或 `exclusive` 完整接管 |

逐行解读：

- **`name`**：作为 Provider 唯一标识，在同名歧义时**全部跳过**（3.6.3 Provider 冲突）；并参与 `(priority, name)` 二元组排序。
- **`config_paths`**：接收 `provider.py` 对 `config/*.yaml` 排序后的绝对路径列表（3.5 节），同目录新增 YAML 不需修改 Provider 工厂。
- **`priority`**：默认 `100`，数值越小越先处理，与 `name` 共同决定 Provider 激活顺序。
- **`framework_package`**：可选，仅在需要版本过滤时使用，Core 据此读取框架安装版本。
- **`owned_symbol_prefixes`**：Exclusive 模式下 Core 据此**过滤**属于 Provider 的兜底 symbol（3.6.2）；两个 Exclusive Provider 拥有的前缀相互包含时冲突双方都跳过（3.6.3）。
- **`handler_module_prefixes`**：白名单作用——限制 Provider 外部 Handler 仅可来自这些前缀（3.7 设计目标："支持 Provider 外部 Handler，同时限制其可导入模块范围"）。
- **`ownership_mode`**：取 `overlay` 或 `exclusive`；原文设计目标写明 Overlay 是迁移期默认，Exclusive 是迁移完成后的显式接管状态。

原文除上述表格外，未出现其他参数表/性能对比表/配置项表格；3.1、3.7 的 mermaid 图为流程图而非表格，已在【关键机制与数据】节描述。

---

【公式解读】

原文无数学公式或伪代码公式。

> 备注：原文 3.3 节包含 `MetricProvider` 的 frozen dataclass 定义与 3.4 节的 `entry_points={...}` / `package_data={...}` Python 代码片段，但这两段均属于数据/接口结构定义而非"公式"，已分别在【表格解读】与【使用方法】节中展开。

---

【关联】

1. **vLLM-Ascend**（上游框架 Provider）：维护 `vllm_ascend/observability/ms_metrics/` 下的 `provider.py`、`handlers.py` 与 `config/*.yaml`，通过 Entry Point 接入 Core。相关 PR：`vLLM-Ascend PR #13783`。
2. **msserviceprofiler 仓**（Core 主体）：本次重构主要落地仓；相关 PR：`msserviceprofiler PR !433`。
3. **Python 打包与发现机制**：依赖 `importlib.metadata.entry_points()`（Provider 发现）与 `package_data`（YAML 进 Wheel）；Provider 工厂内部惰性导入 `ms_service_metric.provider_api` 以保证未安装 Core 时 vLLM-Ascend 推理功能不受影响。
4. **Core 稳定门面与 API**：`ms_service_metric.provider_handlers`（暴露稳定 Handler）与 `ms_service_metric.provider_api`（提供"窄化的指标写入接口"）；Provider Handler 必须通过这些门面访问能力，**不得引用 `ms_service_metric.adapters.*` 等 Core 内部路径**（3.2.3 Handler 归属原则）。
5. **通用运行时元数据**：Core 负责 DP、PD role、phase 等通用上下文；这些不进入 Provider，从而避免 Provider 重复实现通用能力。
6. **指标上报链路**：`MetricsManager` → vLLM `/metrics`，沿用既有 Prometheus 暴露方式（设计目标："现有单 YAML、内置 Adapter、模块式 Handler 和 Prometheus 暴露方式保持兼容"）。
7. **未来扩展点**：SGLang 适配**不在本次范围内**（1.4 非目标），但原文明确"后续可复用同一 Provider 架构接入"。
8. **Prometheus / Grafana**：1.4 节明确**不修改**其部署与持久化机制，Metrics 仍作为"持续观测和第一层问题定位"使用，不会被扩展为算子级 Profiling。

---

【使用方法】

1. **Provider Entry Point 注册**（原文 3.4）：

   ```python
   entry_points={
       "ms_service_metric.providers": [
           "vllm-ascend = "
           "vllm_ascend.observability.ms_metrics:get_metric_provider",
       ],
   }
   ```

2. **Provider 工厂函数（vLLM-Ascend 侧，原文 3.4）**：`get_metric_provider()` 内部**惰性导入** `ms_service_metric.provider_api`，避免硬依赖 Core。

3. **YAML 打入 Wheel（原文 3.5）**：

   ```python
   package_data={
       "vllm_ascend.observability.ms_metrics": ["config/*.yaml"],
   }
   ```

4. **vLLM-Ascend Provider 目录结构**（原文 3.5）：

   ```text
   vllm_ascend/observability/ms_metrics/
   ├── __init__.py
   ├── provider.py
   ├── handlers.py
   └── config/
       ├── base_metrics.yaml
       └── eplb_metrics.yaml
   ```

   `provider.py` 负责对 `config/*.yaml` 排序后生成 `config_paths`，新 YAML 无需改 Provider 工厂。

5. **用户配置加载**（原文 1.3 / 2.5）：通过现有环境变量 `MS_SERVICE_METRIC_CONFIG_PATH` 指向**单文件**或**单目录多 YAML**；框架级用户配置使用 `MS_SERVICE_METRIC_VLLM_CONFIG`（3.7 加载顺序第 4 步）；原文明确**不增加新的环境变量**。

6. **外部 Handler 加载**（原文 1.3 / 2.5）：用户可在配置根目录放置以 `module:function` 语法引用的独立 Handler 文件，**无需修改或安装 Python 包**。

7. **运行控制**：metric `on/off/restart` 控制由 Core 负责（3.2.1），重载采用事务式——失败时回退到上一次已提交配置（2.6 / 3.8）。

8. **正式验证手段**（原文 3.5）：仅源码目录中存在 YAML 不足以证明发布可用；需构建或安装 Wheel，从 `importlib.metadata` 发现 Entry Point，并确认 `provider.config_paths` 中每条路径均存在。
```
