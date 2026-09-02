# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/extend.md

# PointRend extend.md 深度解读

## 【定位】
本文档描述 Detectron2 在"研究灵活性"与"工程易用性"之间取得平衡的两类抽象接口（cfg 配置驱动 vs 显式参数组件），并示范如何通过 `@configurable` 装饰器在三种粒度（纯配置 / 配置+覆盖 / 全显式参数）下构建同一 Mask R-CNN 模型，从而为研究人员提供"突破默认抽象、灵活替换组件"的能力。

---

## 【技术要点】

1. **三类接口的层次化设计**
   - **Type 1 — cfg 驱动接口**：函数/类接收由 yaml 文件生成的 `cfg` 参数，实现"标准默认"路径，用户只需加载专家写好的 yaml 并透传，无需关心各字段含义。
   - **Type 2 — 显式参数接口**：每个函数/类是独立小积木，需要使用者自行理解每个参数后组装，可灵活拼装。
   - **Type 3 — `@configurable` 装饰器接口**：同时支持 `cfg` 模式、显式参数模式或二者混合；其显式参数接口当前标记为 **experimental**。

2. **`build_model(cfg)` 标准入口**
   加载正确 yaml 配置后，一行 `model = build_model(cfg)` 即可构造 Mask R-CNN。

3. **配置+覆盖的混合模式**
   ```python
   model = GeneralizedRCNN(
       cfg,
       roi_heads=StandardROIHeads(cfg, batch_size_per_image=666),
       pixel_std=[57.0, 57.0, 57.0])
   ```
   关键覆盖值：`batch_size_per_image=666`、`pixel_std=[57.0, 57.0, 57.0]`。

4. **全显式参数 Mask R-CNN 完整构造路径**（原文大型代码块），关键参数：
   - **Backbone**：ResNet-50（`BasicStem(3, 64, norm="FrozenBN")`，冻结前 2 个 stage，`out_features=["res2","res3","res4","res5"]`）。
   - **FPN**：256 通道，顶层 `LastLevelMaxPool()`。
   - **RPN**：`in_features=["p2","p3","p4","p5","p6"]`，`in_channels=256`，`num_anchors=3`；
     - 锚框：`sizes=[[32],[64],[128],[256],[512]]`，`aspect_ratios=[0.5, 1.0, 2.0]`，`strides=[4,8,16,32,64]`，`offset=0.0`；
     - 匹配：`Matcher([0.3, 0.7], [0, -1, 1], allow_low_quality_matches=True)`；
     - 回归：`Box2BoxTransform([1.0, 1.0, 1.0, 1.0])`；
     - 采样：`batch_size_per_image=256`，`positive_fraction=0.5`；
     - NMS：`pre_nms_topk=(2000, 1000)`，`post_nms_topk=(1000, 1000)`，`nms_thresh=0.7`。
   - **ROI Heads（80 类）**：`batch_size_per_image=512`，`positive_fraction=0.25`；
     - Proposal 匹配：`Matcher([0.5], [0, 1], allow_low_quality_matches=False)`；
     - Box 分支：`box_in_features=["p2","p3","p4","p5"]`，`ROIPooler(7, (1/4, 1/8, 1/16, 1/32), 0, "ROIAlignV2")`；
     - Box 头：`FastRCNNConvFCHead`，`fc_dims=[1024, 1024]`；
     - Box 预测：`test_score_thresh=0.05`，`Box2BoxTransform((10, 10, 5, 5))`；
     - Mask 分支：`mask_in_features=["p2","p3","p4","p5"]`，`ROIPooler(14, ..., "ROIAlignV2")`；
     - Mask 头：`MaskRCNNConvUpsampleHead`，`conv_dims=[256, 256, 256, 256, 256]`。
   - **数据归一化**：`pixel_mean=[103.530, 116.280, 123.675]`，`pixel_std=[1.0, 1.0, 1.0]`，`input_format="BGR"`。

5. **可替换性原则**（"break existing abstractions and replace them with new ones"）——所有上述组件均可被替换，而非被视作不可触碰的黑盒。

6. **配套教程导航**（文档末尾）
   - 标准场景 → [getting_started.md](./getting_started.md)
   - 自定义数据集 → [datasets.md](./datasets.md)
   - 自定义 DataLoader → [data_loading.md](./data_loading.md)
   - 使用/覆写模型 → [models.md](./models.md)、[write-models.md](./write-models.md)
   - 自定义训练循环（hooks/自定义 loop）→ [training.md](./training.md)

---

## 【关键机制与数据】

工作原理（基于原文描述）：

- **抽象双层结构**："薄抽象"允许研究者拆解/替换一切组件；"高抽象"（cfg-only 路径）让用户在不感知细节的前提下复现标准行为。
- **三种调用粒度的等价性**：同一个 `GeneralizedRCNN` 既能由 `build_model(cfg)` 构造，也能通过混合参数或全显式参数构造，证明 cfg 字段与显式参数之间存在一一映射。
- **FrozenBN 的使用**：在显式构造路径中，backbone 显式声明 `norm="FrozenBN"`，并调用 `.freeze(2)` 冻结前 2 个 stage。
- **ROI 池化双分支**：box 分支与 mask 分支各自使用独立的 `ROIPooler`，仅输出尺寸（7 vs 14）不同，采样率均为 0，池化类型均为 `"ROIAlignV2"`。

性能数据：原文未涉及任何训练/推理性能数字、benchmark 或精度指标。

---

## 【表格解读】

**原文无表格**（全文仅包含 markdown 文本与代码块，未出现任何结构化表格）。

---

## 【公式解读】

**原文无公式**（未出现 LaTeX 数学表达式或伪代码公式；唯一可视为公式化的内容是 yaml 字段映射到显式参数值的"声明式"代码片段，但不属于公式范畴）。

---

## 【关联】

文档在末尾明确链接到以下内部教程，构成"扩展 Detectron2"的完整知识图谱：

| 链接 | 角色 |
|---|---|
| [configs.md](configs.md) | Yacs Configs 教程 —— 解释 cfg-only 抽象的来源 |
| [lazyconfigs.md](lazyconfigs.md) | LazyConfig 系统 —— 基于"显式参数组件"风格 |
| [`../modules/config.html#detectron2.config.configurable`](../modules/config.html#detectron2.config.configurable) | `@configurable` 装饰器 API 参考（Type 3 接口的实现机制） |
| [getting_started.md](./getting_started.md) | 标准场景入门（仅需默认行为时使用） |
| [datasets.md](./datasets.md) | 自定义数据集扩展 |
| [data_loading.md](./data_loading.md) | 自定义 DataLoader 扩展 |
| [models.md](./models.md) | 使用/覆写标准模型行为 |
| [write-models.md](./write-models.md) | 从零编写新模型 |

上下游关系：本文档位于 `PointRend/docs/tutorials/` 之下，承接 [getting_started.md]（标准用法），向下分发到 [datasets.md / data_loading.md / models.md / write-models.md / training.md]（六大扩展方向），并通过 [@configurable] 装饰器把"cfg 抽象"与"显式参数抽象"统一在同一函数签名下。

---

## 【使用方法】

- **标准用法**：加载 yaml 配置 → `model = build_model(cfg)`（详见 [getting_started.md](./getting_started.md)）。
- **混合模式**：将 `cfg` 作为首个参数传入，并在后续命名参数中覆盖特定子组件或顶层超参（如 `roi_heads`、`pixel_std`）。
- **全显式模式**：直接用组件类（`FPN`、`RPN`、`StandardROIHeads`、`ROIPooler`、`FastRCNNOutputLayers`、`MaskRCNNConvUpsampleHead` 等）手动组装模型，所有数值与原文代码块一致。
- **扩展入口**：根据需求类型跳转到末尾列出的对应教程（数据集 / DataLoader / 模型 / 写新模型 / 训练循环）。
- **@configurable 装饰器**：参考 `../modules/config.html#detectron2.config.configurable` API 文档；原文明确标注"显式参数接口当前为 experimental"。

> 注：原文未提供 CLI 命令、环境变量或具体安装步骤；启用方式完全由用户自行在 Python 代码层面按上述三种粒度调用。
