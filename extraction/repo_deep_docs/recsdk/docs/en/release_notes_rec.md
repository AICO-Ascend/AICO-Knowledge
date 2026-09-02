# Version Mapping

> 仓 `recsdk` · 路径 `docs/en/release_notes_rec.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/release_notes_rec.md

# recsdk · Release Notes 26.0.0 深度解读

---

## 【定位】

本文档是华为昇腾 MindX 推荐 SDK（Rec SDK）**26.0.0 版本（Release 版本）的官方 changelog/release notes**，集中说明该版本对应的 MindSDK/Ascend HDK/CANN 配套关系、新增特性（特别是面向 Atlas 350 PCIe 卡的适配、生成式推荐算子、多级缓存策略等）、接口与关键特性变更情况，以及升级后的兼容性影响与文档入口。

---

## 【技术要点】

1. **产品与版本基线**：Rec SDK 26.0.0 隶属 MindSDK，类型为 Release 版本；与之相关的 Ascend HDK 版本——Atlas 350 配套 **1.0.RC1**、其它产品配套 **26.0.RC1**；CANN 配套 **9.0.0**。
2. **版本兼容性矩阵**：原 MindSDK 26.0.0 可升级至 **MindSDK 7.3.0 / 7.3.0.x**；CANN 兼容 **8.3.RC1+、8.5.0+、9.0.0+ 及 patch**；Ascend HDK 兼容 **25.5.0+、25.1.RC1+、26.0.RC1+ 及 patch**。
3. **Torch（torch_rec_v1）多级缓存升级**：新增"增量保存/加载"与"差分卡加载"能力；缓存准入/淘汰策略新增 **`showclick`**；同时支持推荐模型在"算力切分设备（computing power-partitioned devices）"上的推理。
4. **稀疏表基础能力（tf_rec_v2 / torch_rec_v2）**：首次覆盖稀疏表全生命周期——建表、查表、保存、加载、特征准入、特征淘汰；目前仅在 **Atlas 350 PCIe card** 上支持。
5. **面向生成式推荐的融合算子**：完成 `in_linear_silu`、`reverse_sequence` 并**适配 Atlas 350**；完成 `norm_multiply_dropout`、`concat_2d_jagged` 但**暂未适配 Atlas 350**；HSTU 算子 backward 性能优化，前向/反向新增 **int32** 类型支持。
6. **算子重构与生态模块适配**：表查反向算子、HSTU 前向/反向算子被重构；`fbgemm-npu`、HKV 同步适配 Atlas 350。
7. **变更与影响摘要**：接口变更、关键特性变更、已解决问题、已知问题、升级中影响、升级后影响、漏洞修复——**均标注为 None（无）**。
8. **升级后必须动作**：Rec SDK Torch（torch_rec_v1）升级后需**重新编译 `torchrec_npu` 及自定义算子相关包**。

---

## 【关键机制与数据】

- **多级缓存保存/加载机制（原文：torch_rec_v1）**：
  - 支持 *Incremental saving and loading*（增量保存/加载）。
  - 支持 *Differential card loading*（差分卡加载）。
- **多级缓存准入/淘汰策略（原文：torch_rec_v1）**：
  - 引入 `showclick` admission and eviction policy。
- **稀疏表基础函数集合（原文：tf_rec_v2 / torch_rec_v2）**：
  - 包含 table creation、table lookup、saving、loading、feature admission、feature eviction。
- **生成式推荐融合算子（原文：Rec SDK operators）**：
  - 已完成且适配 Atlas 350：`in_linear_silu`、`reverse_sequence`。
  - 已完成但未适配 Atlas 350：`norm_multiply_dropout`、`concat_2d_jagged`。
  - HSTU 算子：backward 性能优化；前向/反向新增 int32 支持；并被重构（refactored）。
- **算力切分设备推理（原文：torch_rec_v1）**：*Recommendation models now support inference on computing power-partitioned devices*。
- **病毒扫描结果（原文：Virus Scan Results）**：*Virus scan passed*。
- **升级后编译动作（原文：Version Compatibility）**：*After the upgrade, recompile `torchrec_npu` and the packages related to custom operators*。

> 注：本文档为 changelog，未给出量化性能数据（如时延/吞吐/QPS 等），上述为"原文有的功能性描述"，未出现具体性能数字。

---

## 【表格解读】

### 表 1：Product Version Information（产品版本信息）

| Product | Version | Version Type |
| --- | --- | --- |
| MindSDK | 26.0.0 | Release version |

**逐行解读**：标识本次 changelog 描述的对象为 MindSDK 下的 Rec SDK 26.0.0，发布形态为 Release（非 RC/beta），适用于生产环境。

### 表 2：Related Product Version Mapping（相关产品版本映射）

| Product | Version |
| --- | --- |
| Ascend HDK | Atlas 350: 1.0.RC1；Other products: 26.0.RC1 |
| CANN | 9.0.0 |

**逐行解读**：列出 Rec SDK 26.0.0 的运行时依赖栈——CANL/CANN 9.0.0；Ascend HDK 在 Atlas 350 上单独走 1.0.RC1 分支，其余产品沿用 26.0.RC1 分支，体现了 Atlas 350 作为新硬件平台的版本独立节奏。

### 表 3：Software version compatibility（Table 1 软件版本兼容性）

| MindSDK Version | MindSDK Version to Upgrade To | CANN Version Compatibility | Ascend HDK Version Compatibility |
| --- | --- | --- | --- |
| Rec SDK 26.0.0 | MindSDK 7.3.0 and 7.3.0.x | CANN 8.3.RC1 and patch versions；CANN 8.5.0 and patch versions；CANN 9.0.0 and patch versions | Ascend HDK 25.5.0 and patch versions；Ascend HDK 25.1.RC1 and patch versions；Ascend HDK 26.0.RC1 and patch versions |

**逐行解读**：
- 当原部署的 MindSDK 是 Rec SDK 26.0.0 时，升级目标为 7.3.0 / 7.3.0.x 序列。
- CANN 侧允许多版本共存（8.3.RC1 / 8.5.0 / 9.0.0 及其 patch），意味着 26.0.0 的 Rec SDK 在 CANN 升级路径上具备较好的前向/后向兼容性。
- Ascend HDK 同样支持 25.5.0 / 25.1.RC1 / 26.0.RC1 三个分支，提供了从旧 HDK 平滑过渡到 26.0.RC1 的弹性空间。
- NOTE 说明：兼容性意味着软件升级时相关软件无需同步升级或打补丁，现有功能仍受支持。

### 表 4：New Features（新特性）

| Feature | Description | Compatible Product Models |
| --- | --- | --- |
| Rec SDK TensorFlow (tf_rec_v1) | Adapted for the Atlas 350 PCIe card. | Atlas 800T A2 training server；Atlas 200T A2 Box16 heterogeneous subrack；Atlas 800T A3 SuperPoD server；Atlas 350 PCIe card |
| Rec SDK Torch (torch_rec_v1) | Multi-level cache saving and loading: Incremental saving and loading and differential card loading are supported.<br>Multi-level cache admission and eviction: The `showclick` admission and eviction policy is supported.<br>Recommendation models now support inference on computing power-partitioned devices.<br>Adapted for the Atlas 350 PCIe card. | 同上（Atlas 800T A2 / 200T A2 Box16 / 800T A3 SuperPoD / Atlas 350 PCIe） |
| Rec SDK TensorFlow (tf_rec_v2) | The basic sparse table functions are implemented, including table creation, table lookup, saving, loading, feature admission, and feature eviction. | Atlas 350 PCIe card |
| Rec SDK Torch (torch_rec_v2) | 同上 | Atlas 350 PCIe card |
| Rec SDK operators | Fused operators for generative recommendation models, including `in_linear_silu` and `reverse_sequence`, are completed and adapted for the Atlas 350 PCIe card.<br>Fused operators for generative recommendation models, including `norm_multiply_dropout` and `concat_2d_jagged`, are completed but not adapted for the Atlas 350 PCIe card.<br>Enhanced HSTU operators: The performance of the backward operator is optimized. The forward and backward operators now support the int32 type.<br>Refactored operators: The table lookup backward operator and the HSTU forward and backward operators are refactored. | 同 tf_rec_v1（Atlas 800T A2 / 200T A2 Box16 / 800T A3 SuperPoD / Atlas 350 PCIe） |
| fbgemm-npu | Adapted for the Atlas 350 PCIe card. | 同 tf_rec_v1 |
| HKV | Adapted for the Atlas 350 PCIe card. | Atlas 350 PCIe card |

**逐行解读**：
- **tf_rec_v1 / torch_rec_v1**：本次最大主线——全面适配 Atlas 350 PCIe card，且 torch 路径额外获得多级缓存的存/取/淘汰能力增强与算力切分设备推理支持。
- **tf_rec_v2 / torch_rec_v2**：第二代 SDK 引入稀疏表基础函数集，是 v2 路线首次具备端到端 sparse table 能力，但当前仅覆盖 Atlas 350。
- **Rec SDK operators**：分两条线——（a）生成式推荐融合算子，Atlas 350 已落地部分（`in_linear_silu`、`reverse_sequence`），另有已完成但尚未在 Atlas 350 适配的（`norm_multiply_dropout`、`concat_2d_jagged`）；（b）HSTU 算子性能/类型扩展（int32）与算子重构。
- **fbgemm-npu / HKV**：作为底层依赖模块同步打通 Atlas 350 适配。

### 表 5：26.0.0 Documentation（文档入口）

| Document | Description | Update Description |
| --- | --- | --- |
| Rec SDK 26.0.0 User Guide（链接到 ../../README.md） | 介绍 Rec SDK 的安装部署、功能、模型适配与 API 参考 | 详见 *Rec SDK 26.0.0 User Guide* |

**逐行解读**：本文档指向仓库根目录的 README.md 作为用户指南主入口，覆盖安装、部署、模型适配与 API 参考。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 Atlas 350 PCIe card 的强耦合**：本次 changelog 的几乎所有特性主线（tf_rec_v1、torch_rec_v1、tf_rec_v2、torch_rec_v2、operators、fbgemm-npu、HKV）都伴随"Adapted for the Atlas 350 PCIe card"，可视为本次发布的**核心适配对象**。Ascend HDK 也为 Atlas 350 单独拉出 **1.0.RC1** 分支，与其余产品的 26.0.RC1 区分，说明 Atlas 350 在 SDK 节奏上是独立轨道。
- **算力切分设备推理（computing power-partitioned devices）**：与多级缓存、稀疏表基础函数一同被列入 torch_rec_v1，提示该能力与**大模型/推荐系统的分布式部署、显存/算力切片**密切相关，但本 changelog 未披露具体设备划分模型。
- **HSTU / 融合算子**：HSTU 是生成式推荐/序列推荐的关键算子，本次同时优化 backward、扩展 int32、并重构前向/反向，与生成式推荐融合算子（`in_linear_silu`、`reverse_sequence`、`norm_multiply_dropout`、`concat_2d_jagged`）共同组成"生成式推荐算子矩阵"。
- **依赖栈**：CANN 9.0.0 + Ascend HDK 26.0.RC1（或 25.5.0/25.1.RC1）+ MindSDK 7.3.0/7.3.0.x ↔ Rec SDK 26.0.0，构成完整的运行时依赖关系。
- **下游文档入口**：文末唯一的内部链接 [Rec SDK 26.0.0 User Guide](../../README.md) 指向仓库根 README，作为该 changelog 对应的详细使用文档（安装、部署、模型适配、API 参考）。

---

## 【使用方法】

- **升级操作**：Rec SDK Torch（torch_rec_v1）用户升级后必须重新编译 `torchrec_npu` 及自定义算子相关包（原文明确给出）。
- **配套版本选择**：CANN 可选用 8.3.RC1 / 8.5.0 / 9.0.0（含 patch）任一；Ascend HDK 可选用 25.5.0 / 25.1.RC1 / 26.0.RC1（含 patch）；如目标硬件是 Atlas 350，则 Ascend HDK 必须使用 **1.0.RC1** 分支。
- **新特性启用**：
  - torch_rec_v1 的多级缓存可使用增量保存/加载、差分卡加载，以及 `showclick` 准入/淘汰策略；
  - 推荐模型可部署到算力切分设备上推理；
  - tf_rec_v2 / torch_rec_v2 可调用稀疏表建表、查表、保存、加载、特征准入/淘汰（仅 Atlas 350）；
  - 生成式推荐融合算子 `in_linear_silu`、`reverse_sequence` 在 Atlas 350 上可用；`norm_multiply_dropout`、`concat_2d_jagged` 已完成但**未适配 Atlas 350**，需关注后续版本；
  - HSTU 算子可在 forward/backward 使用 int32 类型。
- **使用前检查**：Virus scan 通过；Usage Precautions、Interface Changes、Key Feature Changes、Resolved Issues、Known Issues、Upgrade Impact（升级中/升级后）、Vulnerability Patch List 各项均为 None，无额外限制。
- **配套用户指南**：详见 [Rec SDK 26.0.0 User Guide](../../README.md)。

> 原文未提供具体的 CLI 命令、环境变量、配置文件路径或 API 调用样例——以上"启用方式"均为 changelog 中可直接读取到的版本/编译动作/算子名称层面信息，未做任何臆造。
