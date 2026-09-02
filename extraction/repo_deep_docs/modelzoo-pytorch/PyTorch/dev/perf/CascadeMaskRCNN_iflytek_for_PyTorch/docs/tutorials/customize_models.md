# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/customize_models.md

# 文档深度解读：CascadeMaskRCNN_iflytek_for_PyTorch — Tutorial 4: Customize Models

---

## 【定位】

这篇文档面向基于 MMDetection 框架进行二次开发的研究员/工程师，**系统性地指导用户如何在不（或尽量少）改动上游源码的前提下，通过注册机制和配置系统，以"新增组件"的方式定制检测模型的 5 类组成要素（backbone / neck / head / roi extractor / loss）**。

> 注：本文为模型定制指南（tutorial），非性能/算法介绍文档；全文以"开发流程"为主线，**未涉及任何性能数据或对比基准**。

---

## 【技术要点】

1. **模型组件的 5 类划分**（原文第一段明确列出）：
   - `backbone`：FCN 特征抽取网络（如 ResNet、MobileNet）
   - `neck`：连接 backbone 与 head 的中间结构（如 FPN、PAFPN）
   - `head`：任务相关预测头（如 bbox prediction、mask prediction）
   - `roi_extractor`：从 feature map 抽取 RoI 特征（如 RoI Align）
   - `loss`：head 内部用于计算损失的模块（如 FocalLoss、L1Loss、GHMLoss）

2. **组件注册机制**：每一类组件均通过对应 decorator 注册：
   - backbone → `@BACKBONES.register_module()`
   - neck → `@NECKS.register_module()`
   - head → `@HEADS.register_module()`（同时用于 bbox head、roi head、mask head 等）
   - loss → `@LOSSES.register_module()`（结合 `@weighted_loss` 实现逐元素加权）

3. **两种导入策略**（"侵入式" vs "非侵入式"）：
   - 侵入式：往 `mmdet/models/<子包>/__init__.py` 增加 `from .xxx import YYY`
   - 非侵入式：在 config 中添加：
     ```python
     custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'],
                           allow_failed_imports=False)
     ```

4. **配置继承（`_base_`）**：自 MMDetection 2.0 起，配置支持继承，**新增 head 的 config 仅需写"差异部分"**。Double Head R-CNN 示例即通过 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 复用 Faster R-CNN FPN 配置。

5. **bbox head 的"三分支/双分支"设计**：Double Head R-CNN 在 `_bbox_forward` 中对 `cls` 与 `reg` 分别使用不同 `roi_scale_factor`（配置中给出 `reg_roi_scale_factor=1.3`）抽取 RoI 特征，再送入 `bbox_head(x_cls, x_reg)`，实现分类与回归的特征解耦。

6. **`@weighted_loss` decorator**（在 loss 章节）：使 loss 支持"按元素加权"，原文给出的 MyLoss 模板代码即使用该 decorator。

---

## 【关键机制与数据】

### 工作原理：组件注册-导入-配置三步流程

文档展示的所有新组件（MobileNet / PAFPN / DoubleConvFCBBoxHead / DoubleHeadRoIHead / MyLoss）都遵循同一三步范式：

**Step 1 — 定义组件**：在 `mmdet/models/<子包>/xxx.py` 中以 `nn.Module` 子类形式实现，并用对应 decorator 注册。

**Step 2 — 导入模块**：二选一
- 改 `__init__.py`（侵入式）
- config 中声明 `custom_imports`（非侵入式）

**Step 3 — 在 config 中实例化**：通过 `type='类名'` 字符串名查 registry 找到类，再用 kwargs 传参。

### 数据流：Double Head R-CNN 的 RoI 前向（原文 `_bbox_forward` 伪代码）

```text
rois
  ├─> bbox_roi_extractor(x[:num_inputs], rois)            # 分类分支
  │     └─> bbox_cls_feats
  └─> bbox_roi_extractor(x[:num_inputs], rois,
                         roi_scale_factor=reg_roi_scale_factor)  # 回归分支（放大 1.3x）
        └─> bbox_reg_feats

bbox_cls_feats, bbox_reg_feats
  ├─ 若 with_shared_head: shared_head(...) 各自过一遍
  └─> bbox_head(bbox_cls_feats, bbox_reg_feats)  ->  (cls_score, bbox_pred)
```

输出打包为 `dict(cls_score, bbox_pred, bbox_feats)` 返回。

### PAFPN 示例参数（原文 config 片段）

| 字段 | 值 |
|---|---|
| `in_channels` | `[256, 512, 1024, 2048]` |
| `out_channels` | `256` |
| `num_outs` | `5` |

### Double Head R-CNN 配置中的关键参数（原文）

| 字段 | 值 | 含义（按原文位置推断） |
|---|---|---|
| `reg_roi_scale_factor` | `1.3` | 回归分支 RoI 放大倍数 |
| `num_convs` | `4` | 分类分支共享 conv 层数 |
| `num_fcs` | `2` | 回归分支共享 fc 层数 |
| `in_channels` | `256` | head 输入通道 |
| `conv_out_channels` | `1024` | conv 输出通道 |
| `fc_out_channels` | `1024` | fc 输出通道 |
| `roi_feat_size` | `7` | RoI 特征空间尺寸（7×7） |
| `num_classes` | `80` | COCO 类别数 |
| `bbox_coder.type` | `DeltaXYWHBBoxCoder` | 边框编/解码方式 |
| `target_means` | `[0., 0., 0., 0.]` | 编码均值 |
| `target_stds` | `[0.1, 0.1, 0.2, 0.2]` | 编码方差（xy 与 wh 区分） |
| `reg_class_agnostic` | `False` | 类别相关回归 |
| `loss_cls` | `CrossEntropyLoss`, `loss_weight=2.0` | 分类损失 |
| `loss_bbox` | `SmoothL1Loss`, `beta=1.0`, `loss_weight=2.0` | 回归损失 |

> 原文未提供训练/精度/速度等性能数据，本节不补充。

---

## 【表格解读】

**原文无表格。**

原文主要以代码块 + 项目符号列表形式呈现内容，未出现任何 markdown 表格或 HTML 表格结构。性能/参数对照信息均嵌在 config 代码片段内（已在上节"关键参数"中以表格化形式整理展示）。

---

## 【公式解读】

**原文无公式。**

全文未出现 LaTeX 公式或伪代码公式块。涉及的"数学/计算"语义（如 bbox coder 的 `DeltaXYWHBBoxCoder`、`SmoothL1Loss(beta=1.0)`）仅以**配置字段名/类名**方式引用，未给出表达式形式。

唯一可视为"伪代码公式"的元素是 Double Head 论文摘要式 ASCII 图（已在【技术要点】第 5 条转写为文字），原文为：

```
                  /-> shared convs ->  /-> cls
                                      \-> reg
roi features
                  \-> shared fc    ->  /-> cls
                                      \-> reg
```

这仅是网络拓扑示意，**不属于数值公式**。

---

## 【关联】

### 与文中其他特性的耦合点

1. **与"配置继承（`_base_`）"的耦合**：自定义 head 必须依赖 `_base_` 提供 backbone/neck/数据流等基础设施；Double Head R-CNN 即基于 `faster_rcnn_r50_fpn_1x_coco.py` 进行最小化覆盖。

2. **与"Registry / Builder"的耦合**：所有 5 类组件均通过统一 builder（`BACKBONES / NECKS / HEADS / LOSSES`）发现——这是文档全篇能成立的**基础设施前提**（虽未在本文展开定义）。

3. **与"RoI Head ↔ BBox Head"的耦合**：Double Head R-CNN 涉及 **两层继承**：
   - `DoubleConvFCBBoxHead(BBoxHead)` — 仅覆盖 forward 拓扑
   - `DoubleHeadRoIHead(StandardRoIHead)` — 仅覆盖 `_bbox_forward`
   - 其余 `init_*` / `forward_train` / `simple_test` 等仍来自父类 `StandardRoIHead`（原文 `_bbox_forward` 注释："inherits other logics from the `StandardRoIHead`"）

4. **与 `roi_extractor.num_inputs` 的耦合**：`x[:self.bbox_roi_extractor.num_inputs]` 这种切片写法说明 bbox 头只取 backbone 输出 feature map 的前 N 个层级，**剩余层级由 mask head 使用**——这是 FPN 多尺度输出在两阶段头之间的常规分工（原文未展开，但代码已暗示）。

5. **与"MMDetection 2.0 配置系统"的耦合**：原文显式提及 "Since MMDetection 2.0, the config system supports to inherit configs"，表明该 tutorial 假设读者使用 ≥2.0 版本。

### 与上下文的串联（基于目录语义推断）

该文档属于 tutorials 系列（"Tutorial 4"），按命名约定，上下游可能涉及：
- Tutorial 1–3：config、数据流、模型构建基础
- Tutorial 5+：自定义数据集、损失、训练策略

> **原文内未提供任何内部链接**（"内部链接: (无)"已确认），故具体 tutorial 之间的引用关系不在本文档信息范围内。

---

## 【使用方法】

### 启用方式总览（按 5 类组件分述，原文给出）

#### A. 新增 backbone
1. 在 `mmdet/models/backbones/<name>.py` 实现类并 `@BACKBONES.register_module()`
2. 二选一导入：
   - 改 `mmdet/models/backbones/__init__.py` 加 `from .<name> import <Class>`
   - 或 config 加 `custom_imports = dict(imports=['mmdet.models.backbones.<name>'], allow_failed_imports=False)`
3. config 中：
   ```python
   model = dict(..., backbone=dict(type='<Class>', arg1=xxx, arg2=xxx), ...)
   ```

#### B. 新增 neck
1. `mmdet/models/necks/<name>.py` 实现并 `@NECKS.register_module()`
2. 同上二选一导入（注意原文 neck 示例的 `custom_imports` 路径写法有误：`'mmdet.models.necks.pafpn.py'` 多了一个 `.py`，应视为原文笔误，**未由用户额外修改**）
3. config 中：
   ```python
   neck=dict(type='PAFPN', in_channels=[256,512,1024,2048], out_channels=256, num_outs=5)
   ```

#### C. 新增 head（最复杂）
需 **三处** 协同：
1. 新 bbox head（`mmdet/models/roi_heads/bbox_heads/double_bbox_head.py`）：继承 `BBoxHead`，实现 `__init__` + `forward(x_cls, x_reg)`
2. 新 RoI head（`mmdet/models/roi_heads/double_roi_head.py`）：继承 `StandardRoIHead`，**只重写** `_bbox_forward`；其余函数继承
3. 导入到 `mmdet/models/bbox_heads/__init__.py` 与 `mmdet/models/roi_heads/__init__.py`，**或** 在 config 中写：
   ```python
   custom_imports=dict(imports=['mmdet.models.roi_heads.double_roi_head',
                                'mmdet.models.bbox_heads.double_bbox_head'])
   ```
4. config 形如：
   ```python
   _base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'
   model = dict(roi_head=dict(
       type='DoubleHeadRoIHead',
       reg_roi_scale_factor=1.3,
       bbox_head=dict(_delete_=True,
                      type='DoubleConvFCBBoxHead',
                      num_convs=4, num_fcs=2, ...)))
   ```
   > `_delete_=True` 用以删除 `_base_` 中的同名 `bbox_head`，避免冲突（原文显式给出该字段）。

#### D. 新增 loss
> **原文此节被截断**（MyLoss 示例代码在 `loss = torch.abs(pre` 处结束，未给出后续）。已知信息：
- 在 `mmdet/models/losses/my_loss.py` 实现
- 用 `@weighted_loss` 修饰函数
- 用 `@LOSSES.register_module()` 注册类
- 模板代码片段：
  ```python
  @weighted_loss
  def my_loss(pred, target):
      assert pred.size() == target.size() and target.numel() > 0
      loss = torch.abs(pre...  # 原文截断
  ```
- 具体的 `__all__` 注册写法、`build_loss` 调用示例、config 中引用方式 **均不在原文信息范围内**（属于文档残缺部分，未补全）。

#### E. 新增 roi extractor
> **原文未涉及 roi extractor 的定制流程**，仅在组件分类处点名"e.g., RoI Align"。

### 关键命令/语法速查

| 操作 | 原文措辞 |
|---|---|
| 注册 backbone | `@BACKBONES.register_module()` |
| 注册 neck | `@NECKS.register_module()` |
| 注册 head | `@HEADS.register_module()` |
| 注册 loss | `@LOSSES.register_module()` + `@weighted_loss` |
| 非侵入式导入 | `custom_imports = dict(imports=[...], allow_failed_imports=False)` |
| 删除 base 中的同名子配置 | `dict(_delete_=True, type='NewClass', ...)` |
| 继承父配置 | `_base_ = '../path/to/parent_config.py'` |

---

## 附：原文残缺说明

文档在 **"Add new loss"** 一节的代码示例处被截断（`loss = torch.abs(pre` 戛然而止），因此关于：
- `my_loss.py` 完整代码
- 损失函数在 head 中如何被引用（`loss_cls=dict(type='MyLoss', ...)` 的具体形态）
- `@weighted_loss` 的内部实现机制

这些信息 **不在原文信息范围内**，本解读未做任何补全或臆造。
