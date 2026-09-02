# 版本说明

> 仓 `indexsdk` · 路径 `docs/zh/release_notes_index.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/indexsdk/docs/zh/release_notes_index.md

# Index SDK 26.1.0 版本说明深度解读

## 【定位】

本文档是华为昇腾平台 Index SDK 26.1.0 版本的发行说明（Release Notes），主要解决两个问题：一是明确该版本与 CANN、Ascend HDK 等上下游组件的版本配套与兼容性矩阵；二是告知用户在 26.1.0 版本中新增了哪些面向 A2/A3 平台的检索能力以及相关业务接口的变更情况，为升级决策和特性使用提供权威依据。

## 【技术要点】

1. **TS FlatIP 与 Int8Cos 算子扩展到 A2/A3 平台**：原文给出的具体规格——A2 底库 6000 万、A3 底库 1.25 亿、维度 256、batch 范围 1–256、topk=200。
2. **IVF-RabitQ 索引扩展到 A2/A3 平台**：原文给出的具体规格——底库 1000 万、维度 128、topk=300、数据精度 FP32。
3. **配套产品矩阵**：Index SDK 26.1.0 与 CANN 9.1.0、Ascend HDK 26.1.0 形成当前 Release 配套关系，同时向前兼容 CANN 8.5.0 / 9.0.0 与 Ascend HDK 25.5.0 / 26.0.RC1。
4. **IVF-RabitQ 业务接口扩展**：新增 `train`、`remove_ids`、`copyFrom`、`copyTo`、`update` 共 5 个接口，覆盖索引训练、元素删除、跨实例复制（双向）以及数据更新等生命周期动作。
5. **关键特性与遗留问题**：本版本无关键特性变更，无遗留问题，无已解决问题，升级过程及升级后对现行系统均无影响。

## 【关键机制与数据】

原文未给出算法实现细节或数据流说明，仅以"特性描述"形式给出可量化的运行规格，原文摘录如下：

- TS FlatIP / Int8Cos：A2 底库 6 千万，A3 底库 1.25 亿，256 维度，batch1–256，topk200。
- IVF-RabitQ：底库 1000 万，128 维度，topk300，数据精度 FP32。
- 接口新增：IVF-RabitQ 新增 train、remove_ids、copyFrom、copyTo、update。
- 版本兼容标记："Y" 表示可配套，"/" 表示不可配套。
- 病毒扫描：通过；漏洞修补列表：无。

## 【表格解读】

### 表格 1：产品版本信息

| 字段 | 取值 |
|---|---|
| 产品名称 | Index SDK |
| 产品版本 | 26.1.0 |
| 版本类型 | Release 版本 |

**解读**：定义本次发布主体的官方身份，是后续配套表与特性表的前提字段。

### 表 1：Index SDK 软件版本配套表

| Index SDK | CANN 版本 | Ascend HDK 版本 |
|---|---|---|
| 26.1.0 | 9.1.0 | 26.1.0 |

**解读**：仅展示本版本（26.1.0）一行，是官方推荐的"黄金组合"配套关系：CANN 9.1.0 + Ascend HDK 26.1.0。

### 表 2：Index SDK 与 CANN 版本兼容

| Index SDK \ CANN | 8.5.0 | 9.0.0 | 9.1.0 |
|---|---|---|---|
| 7.3.0   | Y | / | / |
| 26.0.0  | Y | Y | / |
| 26.1.0  | Y | Y | Y |

**解读**：本版本（26.1.0）是 CANN 三个版本（8.5.0、9.0.0、9.1.0）下唯一全部可配套的 Index SDK 版本；同时也意味着 CANN 9.1.0 是必须配套的"下限"——若要使用 26.1.0 的新特性，至少需要 CANN 9.1.0。

### 表 3：Index SDK 与 Ascend HDK 版本兼容

| Index SDK \ Ascend HDK | 25.5.0 | 26.0.RC1 | 26.1.0 |
|---|---|---|---|
| 7.3.0   | Y | / | / |
| 26.0.0  | Y | Y | / |
| 26.1.0  | Y | Y | Y |

**解读**：与表 2 结论对称——本版本（26.1.0）是 Ascend HDK 三个版本下唯一全部可配套的 Index SDK 版本；而 HDK 26.1.0 是与 Index SDK 26.1.0 对齐的官方推荐搭配。

### 表 4：新增特性

| 特性名称 | 特性描述 | 配套产品型号 |
|---|---|---|
| TS FlatIP 与 Int8Cos 支持 A2/A3 平台 | TS FlatIP, Int8Cos 支持 A2 A3：A2 底库 6 千万，A3 底库 1.25 亿，256 维度，batch1-256，topk200。 | Atlas 800I A3 超节点服务器<br>Atlas 800I A2 推理服务器 |
| IVF-RabitQ 索引支持 A2/A3 平台 | A2, A3 支持 IVF-RabitQ：底库 1000 万，128 维度，topk300，数据精度 FP32。 | Atlas 800I A3 超节点服务器<br>Atlas 800I A2 推理服务器 |

**解读**：两条新增特性均同时面向 A2（Atlas 800I A2 推理服务器）与 A3（Atlas 800I A3 超节点服务器）两类硬件平台。第一条以"TS FlatIP + Int8Cos"为代表的检索算子在 256 维、topk200 场景下覆盖了 batch 1–256 的吞吐弹性；第二条 IVF-RabitQ 是量化类索引，FP32 输入、128 维、topk300、最大底库 1000 万。

### 表 5：业务接口变更（Index SDK）

| 接口对象 | 变更类型 | 新增接口 |
|---|---|---|
| IVF-RabitQ | 新增 | `train`、`remove_ids`、`copyFrom`、`copyTo`、`update` |

**解读**：仅 IVF-RabitQ 受影响，5 个新接口覆盖：训练（`train`）、按 ID 删除（`remove_ids`）、双向复制（`copyFrom` / `copyTo`）、增量更新（`update`），使 IVF-RabitQ 具备完整的"训练—构建—查询—维护"生命周期操作能力。

### 表 6：26.1.0 版本配套文档

| 文档名称 | 内容简介 | 更新说明 |
|---|---|---|
| 《Index SDK 26.1.0 用户指南》 | 主要包括 Index SDK 的使用流程、算法介绍、算子生成说明、API 接口说明以及其他常用的操作。 | 详见《Index SDK 26.1.0 用户指南》 |

**解读**：用户指南是 26.1.0 唯一配套主文档，覆盖使用流程、算法、算子生成、API 接口说明等核心内容，与本 Release Notes 形成"特性 + 用法"的互补关系。

## 【公式解读】

原文无公式。

## 【关联】

- **下游配套**：与 CANN（8.5.0 / 9.0.0 / 9.1.0）和 Ascend HDK（25.5.0 / 26.0.RC1 / 26.1.0）存在强版本配套关系；本版本（26.1.0）是当前可同时兼容上述全部配套组合的唯一 Index SDK 版本。
- **硬件平台**：A2（Atlas 800I A2 推理服务器）与 A3（Atlas 800I A3 超节点服务器）共同承载本次两大新特性（TS FlatIP/Int8Cos、IVF-RabitQ）。
- **索引算法模块**：IVF-RabitQ 作为本次受影响最大的索引类型，新增 5 个生命周期接口（`train`、`remove_ids`、`copyFrom`、`copyTo`、`update`）。
- **配套文档**：通过文末链接指向 [《Index SDK 26.1.0 用户指南》](01_introduction.md#软件架构) 的"软件架构"章节，用于进一步了解使用流程、算法介绍、算子生成与 API 接口。

## 【使用方法】

原文未涉及具体的启用命令、配置项或调用示例，仅提供版本配套矩阵与新特性列表；如需获取 API 使用细节（如 IVF-RabitQ 新增的 `train`、`remove_ids`、`copyFrom`、`copyTo`、`update` 接口的调用方式），需参考配套的《Index SDK 26.1.0 用户指南》（链接：`01_introduction.md#软件架构`）。
