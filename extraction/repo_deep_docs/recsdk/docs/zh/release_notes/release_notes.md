# 版本说明

> 仓 `recsdk` · 路径 `docs/zh/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/zh/release_notes/release_notes.md

# Rec SDK 26.1.0 版本说明文档深度解读

## 【定位】
本文档是华为昇腾 MindX **Rec SDK 26.1.0** 的发布说明（Release Notes），系统阐述了该版本相比前一版（26.0.0）的新增特性、配套软件版本矩阵、与上下游组件的兼容性、业务接口/关键特性变更以及升级影响，为版本升级决策和适配部署提供依据。

---

## 【技术要点】

1. **新硬件适配**：全子产品线（tf_rec_v1、torch_rec_v1）首次支持 **Atlas 350 标卡**；tf_rec_v2 与 torch_rec_v2 适配机型收敛为 Atlas 350 标卡。
2. **动态表淘汰策略（torch_rec_v2）**：新增四种淘汰策略——**TIMESTAMP**（按时间戳）、**STEP**（按步数）、**CUSTOMIZED**（用户自定义）、**LFU**（最不经常使用），用于动态表内存管理。
3. **稀疏表缓存模式（torch_rec_v2）**：新增 **HBM+DDR** 双级缓存模式，区别于既有 HBM 单一介质缓存。
4. **持久化与训练能力（torch_rec_v2）**：新增 **增量保存功能**，新增对 **EmbeddingBagCollection** 场景的支持，优化器支持范围扩展为 **SGD、ADAM、AdaGrad、RowWiseAdaGrad**。
5. **生成式推荐模型融合算子补齐**：新增 **split_2d_jagged、concat_2d_jagged、norm_multiply_dropout** 三个融合算子，并适配 Atlas 350 标卡；同时对 **hstu_v2** 算子在 Atlas 350 上进行性能优化。
6. **软件栈配套**：兼容 **CANN 9.1.0 / Ascend HDK 26.1.0 / TorchNPU 26.1.0**；并向下兼容 CANN 9.0.0 + Ascend HDK 26.0.RC1 + TorchNPU 26.0.0（见 26.0.0 行的"Y"标记）。

---

## 【关键机制与数据】

- **动态表淘汰策略的工作机理**（原文："新增动态表淘汰策略（TIMESTAMP/STEP/CUSTOMIZED/LFU）"）：文档未给出具体算法伪代码或阈值参数，但通过命名可知是四种不同触发维度的淘汰器——TIMESTAMP 基于时间老化、STEP 基于训练步数老化、CUSTOMIZED 由用户传入回调决定、LFU 基于访问频次计数。原文没有给出"在何种容量阈值触发""淘汰比例"等具体数字。
- **HBM+DDR 缓存模式**（原文："HBM+DDR 缓存模式"）：原文仅给出模式名称，未描述 L1/L2 数据分层规则、回写策略、容量配比、命中率指标，因此无可量化性能数据。
- **torch_rec_v1/v2 升级约束**（原文："在升级版本后，需要重新编译 torchrec_npu 和自定义算子相关包"）：表明 Rec SDK Torch 系列与 TorchNPU 的二进制耦合，重打包是必经步骤。
- **业务接口变更、关键特性变更、已解决问题、遗留问题、升级影响**：原文均标注"无"。
- **病毒扫描结果**：原文标注"通过"。
- 文档未提供性能对比数值（如 QPS、Recall、显存占用、训练吞吐等基准）。

---

## 【表格解读】

### 表格 A：产品版本信息（来自"产品版本信息"小节）

| 产品名称 | 产品版本 | 版本类型 | 维护周期 |
|---|---|---|---|
| Rec SDK | 26.1.0 | Release 版本 | 参考维护策略（../../../README.md#torch_rec_v1-框架维护策略） |

**解读**：定义本次发布包的身份标识。维护周期被外链到根目录 README 中的"框架维护策略"锚点，说明维护承诺不在本文档展开。

---

### 表格 B：表 1 — Rec SDK 软件版本配套表

| Rec SDK | CANN 版本 | Ascend HDK 版本 | TorchNPU 版本 |
|---|---|---|---|
| 26.1.0 | 9.1.0 | 26.1.0 | 26.1.0 |

**解读**：本次发布的"官方推荐配套组合"，四个组件版本号完全同步对齐到 26.1.0 周期（仅 CANN 例外，为 9.1.0）。

---

### 表格 C：表 2 — Rec SDK 与 CANN 版本兼容

| Rec SDK \ CANN 版本 | 8.5.0 | 9.0.0 | 9.1.0 |
|---|---|---|---|
| 7.3.0 | Y | / | / |
| 26.0.0 | / | Y | Y |
| 26.1.0 | / | / | Y |

**解读**：
- 沿对角线方向"Y"逐版右移，体现 CANN 大版本不向后兼容的设计：Rec SDK 7.3.0 仅适配 CANN 8.5.0；26.0.0 兼容 CANN 9.0.0 与 9.1.0；**26.1.0 仅兼容 CANN 9.1.0**，与 CANN 8.5.0 / 9.0.0 均不可配套（"/"）。
- 即从 26.0.0 升级到 26.1.0，若原系统运行在 CANN 9.0.0，则需要联动升级 CANN 至 9.1.0。

---

### 表格 D：表 3 — Rec SDK 与 Ascend HDK 版本兼容

| Rec SDK \ Ascend HDK 版本 | 25.5.0 | 26.0.RC1 | 26.1.0 |
|---|---|---|---|
| 7.3.0 | Y | / | / |
| 26.0.0 | / | Y | Y |
| 26.1.0 | / | / | Y |

**解读**：
- 与 CANN 兼容表结构高度对称；**26.1.0 仅与 Ascend HDK 26.1.0 可配套**，不再支持 25.5.0 与 26.0.RC1。
- 26.0.0 同时适配 RC1 与正式版（26.1.0），说明 Rec SDK 26.0.0 在过渡期已为 HDK 26.1.0 留出兼容性窗口，但 26.1.0 起窗口关闭。

---

### 表格 E：表 4 — Rec SDK 与 TorchNPU 版本兼容

| Rec SDK \ TorchNPU 版本 | 7.3.0 | 26.0.0 | 26.1.0 |
|---|---|---|---|
| 7.3.0 | Y | / | / |
| 26.0.0 | / | Y | Y |
| 26.1.0 | / | / | Y |

**解读**：
- TorchNPU 兼容矩阵与 HDK 矩阵呈"完全平移"关系，验证了三者在 Rec SDK 中是协同发布的耦合栈。
- **Rec SDK 26.1.0 必须搭配 TorchNPU 26.1.0**；同时结合 NOTE 中"需要重新编译 torchrec_npu 和自定义算子相关包"的提示，意味着任何残留的 torchrec_npu 二进制在升级后都不可用。

---

### 表格 F：新增特性表

| 特性名称 | 特性描述 | 配套产品型号 |
|---|---|---|
| Rec SDK TensorFlow(tf_rec_v1) | 适配 Atlas 350 标卡 | Atlas 800T A2 训练服务器；Atlas 200T A2 Box16 异构子框；Atlas 800T A3 超节点服务器；Atlas 350 标卡 |
| Rec SDK Torch(torch_rec_v1) | 适配 Atlas 350 标卡 | Atlas 800T A2 训练服务器；Atlas 200T A2 Box16 异构子框；Atlas 800T A3 超节点服务器；Atlas 350 标卡 |
| Rec SDK TensorFlow(tf_rec_v2) | 适配 Atlas 350 标卡 | Atlas 350 标卡 |
| Rec SDK Torch(torch_rec_v2) | 支持动态表淘汰策略：TIMESTAMP、STEP、CUSTOMIZED、LFU；支持稀疏表缓存模式：HBM+DDR；支持增量保存功能；支持 EmbeddingBagCollection 场景；支持 SGD、ADAM、AdaGrad、RowWiseAdaGrad 优化器 | Atlas 350 标卡 |
| Rec SDK 算子 | 生成式推荐模型融合算子补齐，并适配 Atlas 350 标卡：split_2d_jagged、concat_2d_jagged、norm_multiply_dropout；Atlas 350 标卡算子性能优化：hstu_v2 | Atlas 800T A2 训练服务器；Atlas 200T A2 Box16 异构子框；Atlas 800T A3 超节点服务器；Atlas 350 标卡 |

**解读**：
- v1 系列（tf_rec_v1 / torch_rec_v1）的本次变更**仅是机型扩展**（新增 Atlas 350 标卡），保持原有功能集。
- **所有重磅新特性集中在 torch_rec_v2 子产品**：动态淘汰、缓存模式、增量保存、场景拓展、优化器补齐。
- **tf_rec_v2 在本版本的功能集较窄**，仅完成 Atlas 350 适配，未引入上述新机制——这暗示 Rec SDK 的下一代表达重心已从 TF 后端迁移到 Torch 后端。
- **算子条目横跨 v1 与 v2**，因为算子层（hstu_v2、split_2d_jagged 等）是底层公共组件，既服务于 tf_rec_v1/torch_rec_v1（多机型），也支撑未来模型在 Atlas 350 上的运行。

---

### 表格 G：26.1.0 版本配套文档

| 文档名称 | 内容简介 | 更新说明 |
|---|---|---|
| 《Rec SDK 26.1.0 用户指南》（../../../README.md） | 主要包括 Rec SDK 的简介、软件安装部署、功能特性、模型适配和相关的 API 接口参考。 | 变更详见《Rec SDK 26.1.0 用户指南》。 |

**解读**：本文档本身不承载使用细节，所有安装、部署、API 调用方式均通过根目录 README 给出（链接回 `../../../README.md`）。

---

## 【公式解读】

**原文无公式**。

文档中仅出现版本号矩阵与特性名称列表，未涉及任何数学公式、伪代码或算法表达式。

---

## 【关联】

- **子产品/模块层级关系**：本文档同时覆盖 **4 个子产品**——`tf_rec_v1`、`torch_rec_v1`、`tf_rec_v2`、`torch_rec_v2`，以及一个横切关注点 **Rec SDK 算子**。其中 v1 是稳定维护线（仅做机型适配），v2 是特性演进线（承担本次全部新特性引入）。
- **下游硬件依赖**：所有子产品均依赖华为 Atlas 系列——**Atlas 800T A2 训练服务器、Atlas 200T A2 Box16 异构子框、Atlas 800T A3 超节点服务器、Atlas 350 标卡**；其中 Atlas 350 标卡为本版本新增目标。
- **上游软件栈依赖**：必须同时配套 **CANN 9.1.0 + Ascend HDK 26.1.0 + TorchNPU 26.1.0**（torch_rec 路线还需重编 torchrec_npu）。
- **算子层耦合**：新增的 **split_2d_jagged / concat_2d_jagged / norm_multiply_dropout** 与性能优化的 **hstu_v2** 属于生成式推荐模型（Generative Recommendation）的融合算子栈，承接 26.0.0 已开启的 HSTU 类工作。
- **持久化与训练框架耦合**：torch_rec_v2 新增的"增量保存功能"与"EmbeddingBagCollection 场景支持"分别对接 PyTorch 训练流程的 checkpoint 与 DLRMS 典型 Embedding 拓扑。
- **外部文档锚点**：
  - `../../../README.md`：维护策略、用户指南（安装部署、功能特性、模型适配、API 参考）；
  - `../resources/RecSDK漏洞修补列表.xlsx`：本版本对应的安全 CVE 修补明细（文档外链，正文未列出条目）。

---

## 【使用方法】

**原文未涉及**。

本文档为 changelog 性质，未包含安装命令、配置项、启用开关或代码调用示例。所有"如何使用 Rec SDK"的实操信息被外引到 **《Rec SDK 26.1.0 用户指南》**（`../../../README.md`）的"软件安装部署、功能特性、模型适配和相关的 API 接口参考"章节中。
