# Tutorial 4: Customize Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_models.md

# NasFPN · Tutorial 4: Customize Models — 深度解读

> 路径: `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_models.md`
> 注: 原文在 "Add new loss" 章节末尾被截断 (以 `from ` 结尾, 后续 `MyLoss` 完整示例与 "Add new roi extractor" 等章节缺失), 以下解读仅基于原文可读内容, 不臆补缺失段落。

---

## 【定位】

这篇文档是 MMDetection 框架下 **"如何扩展/自定义检测模型组件"** 的官方教程, 系统说明如何向既有模型中**新增 backbone、neck、head、roi extractor、loss 五类组件**, 并以 *MobileNet*、*PAFPN*、*Double Head R-CNN* 为完整样例, 给出从「写类文件 → 注册装饰器 → 导入模块 → 写入 config」的端到端范式。

---

## 【技术要点】

1. **5 类组件划分** (原文开篇定义)
   - **backbone**: FCN 类特征提取网络 (例: ResNet, MobileNet)
   - **neck**: backbone 与 head 之间的连接部件 (例: FPN, PAFPN)
   - **head**: 任务相关输出 (例: bbox prediction, mask prediction)
   - **roi extractor**: 从特征图提取 RoI 特征 (例: RoI Align)
   - **loss**: head 内部用于计算损失的组件 (例: FocalLoss, L1Loss, GHMLoss)

2. **注册装饰器机制** (Registry Pattern)
   - 通过 `@BACKBONES.register_module()` / `@NECKS.register_module()` / `@HEADS.register_module()` 将新类登记到全局注册表; 类必须实现 `__init__` / `forward` / `init_weights`。

4. **两种导入方式**
   - 方式 A: 手动 `from .mobilenet import MobileNet` 加入对应目录的 `__init__.py`
   - 方式 B: 在 config 中加 `custom_imports = dict(imports=['mmdet.models.backbones.mobilenet'], allow_failed_imports=False)`, **无需修改源码**

5. **BBox Head 双分支约定**
   - 新建 `DoubleConvFCBBoxHead(BBoxHead)` 时, `forward(self, x_cls, x_reg)` 显式接收**分类特征**与**回归特征**两个输入 (对应 Double Head R-CNN 双分支设计)。

6. **RoI Head 重写最小化**
   - `DoubleHeadRoIHead(StandardRoIHead)` 仅重写 `_bbox_forward` (即分类/回归使用**不同 roi_scale_factor**), 其余方法 (assign/sampler/init_weights/simple_test 等) 直接继承, 体现 **"继承基类 + 局部覆写"** 的扩展原则。

7. **Config 继承体系 (自 MMDetection 2.0 起)**
   - 通过 `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` 复用基础模型, 仅覆写差异部分, 并可用 `_delete_=True` 删除被继承配置中的某字段。

---

## 【关键机制与数据】

### 工作流 (原文隐含)
`backbone (提多尺度特征图)` → `neck (跨层融合)` → `head + roi_extractor (在特征上做任务预测)` → `loss (与 GT 计算损失)`

### Double Head R-CNN 的具体超参数 (原文)
- 继承基线: `../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`
- `reg_roi_scale_factor = 1.3` (回归分支 RoI 缩放因子)
- `DoubleConvFCBBoxHead`:
  - `num_convs=4`, `num_fcs=2`
  - `conv_out_channels=1024`, `fc_out_channels=1024`
  - `in_channels=256`, `roi_feat_size=7`
  - `num_classes=80`
- BBox coder: `DeltaXYWHBBoxCoder`, `target_means=[0., 0., 0., 0.]`, `target_stds=[0.1, 0.1, 0.2, 0.2]`
- `reg_class_agnostic=False` (回归按类区分)
- 分类损失: `CrossEntropyLoss (use_sigmoid=False, loss_weight=2.0)`
- 回归损失: `SmoothL1Loss (beta=1.0, loss_weight=2.0)`

### PAFPN neck 样例参数 (原文)
- 输入通道列表: `[256, 512, 1024, 2048]` (即 ResNet-50 四阶段输出)
- `out_channels=256`, `num_outs=5`, `start_level=0`, `end_level=-1`, `add_extra_convs=False`

### MobileNet backbone 骨架 (原文)
仅给出占位签名 `__init__(self, arg1, arg2)`, **未提供任何具体数值**; 文档本身亦未声明性能数据。

> 注: 原文**未给出任何性能指标 (mAP / FPS / 参数量)**, 故本节无 benchmark 数据。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**
(虽然 BBox coder 与 SmoothL1Loss 隐含 Δx/Δy/Δw/Δh 编码及 smooth L1 公式, 但文档**并未显式写出任何数学式**, 此处严格依据原文。)

---

## 【关联】

| 关联对象 | 关系 | 备注 |
|---|---|---|
| `BaseRoIHead` | `StandardRoIHead` 的父类, 提供 RoI 头骨架 | 原文未给出其全部方法签名 |
| `StandardRoIHead` | `DoubleHeadRoIHead` 的直接父类, 提供 `init_assigner_sampler / init_bbox_head / init_mask_head / init_weights / forward_dummy / forward_train / simple_test` 等 | Double Head 仅覆写 `_bbox_forward` |
| `BBoxHead` | `DoubleConvFCBBoxHead` 的父类, 提供 bbox 头基类 | |
| `_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'` | Double Head R-CNN 继承自 Faster R-CNN R50-FPN 1x COCO 配置 | MMDetection 2.0+ 支持 config 继承 |
| `mmdet.models.builder` | 提供 `HEADS` / `build_head` / `build_roi_extractor` 注册表与工厂函数 | |
| 外部参考 | Double Head R-CNN 论文 `https://arxiv.org/abs/1904.06493` | 原文引用 |
| 注册表与 Builder | 装饰器 `@BACKBONES / @NECKS / @HEADS.register_module()` 通过 builder 工厂按 `type` 字符串构建对象 | 与 modelzoo-pytorch 中 NasFPN 的检测 pipeline 一脉相承 |

---

## 【使用方法】

> 全部步骤均严格来自原文。

### 通用三步流程
1. **定义组件类**: 在 `mmdet/models/{backbones|necks|roi_heads/...|losses}/xxx.py` 新建文件,使用对应注册装饰器。
2. **导入模块**: 二选一
   - 在对应目录 `__init__.py` 加 `from .xxx import Xxx`
   - 或在 config 中加
     ```python
     custom_imports = dict(
         imports=['mmdet.models.backbones.mobilenet'],
         allow_failed_imports=False)
     ```
3. **写入 config** (以 backbone 为例):
   ```python
   model = dict(
       ...,
       backbone=dict(type='MobileNet', arg1=xxx, arg2=xxx),
       ...)
   ```

### 各组件配置样例 (原文)

**新 Neck (PAFPN) 在 config 中:**
```python
neck=dict(
    type='PAFPN',
    in_channels=[256, 512, 1024, 2048],
    out_channels=256,
    num_outs=5)
```

**新 Head (Double Head R-CNN) 完整 config:**
```python
_base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'
model = dict(
    roi_head=dict(
        type='DoubleHeadRoIHead',
        reg_roi_scale_factor=1.3,
        bbox_head=dict(
            _delete_=True,
            type='DoubleConvFCBBoxHead',
            num_convs=4,
            num_fcs=2,
            in_channels=256,
            conv_out_channels=1024,
            fc_out_channels=1024,
            roi_feat_size=7,
            num_classes=80,
            bbox_coder=dict(
                type='DeltaXYWHBBoxCoder',
                target_means=[0., 0., 0., 0.],
                target_stds=[0.1, 0.1, 0.2, 0.2]),
            reg_class_agnostic=False,
            loss_cls=dict(
                type='CrossEntropyLoss', use_sigmoid=False, loss_weight=2.0),
            loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=2.0))))
```

**新 Loss 的注册范式 (原文片段, 已被截断):**
```python
import torch
import torch.nn as nn

from
# (原文此处被截断, @weighted_loss 装饰器与 MyLoss 类完整实现未给出)
```

> **原文未涉及**: 训练命令 / 启动脚本 / 评测流程 / 性能基准数据 / 推理命令 / checkpoint 路径; 这些信息在当前文档中**均不存在**, 实际使用需结合 MMDetection 仓库的 `tools/train.py` / `configs/` 等其它文档。
