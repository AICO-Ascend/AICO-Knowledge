# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/models.md

# 一体化深度解读:detectron2 `Use Models` 教程

---

## 【定位】

这篇文档系统解答 detectron2 中"如何构建、加载/保存权重、调用、解读输入输出、以及如何部分执行以获取中间张量"等一整套模型使用问题,是把 `build_model` 返回的 `torch.nn.Module` 对象在训练/推理两条主线上落到代码层面的官方指引。

---

## 【技术要点】

1. **模型构建三件套**: 通过 `detectron2.modeling` 中的 `build_model`、`build_backbone`、`build_roi_heads` 等工厂函数按 `cfg` 组装模型;`build_model` **只搭结构并填入随机参数**,不会自动加载预训练权重。

2. **权重加载/保存由 `DetectionCheckpointer` 承担**: 既识别 PyTorch `.pth`,也识别 model zoo 的 `.pkl`;`load(file_path_or_url)` 路径通常来自 `cfg.MODEL.WEIGHTS`;`save("model_999")` 写入 `save_dir/output/model_999.pth`。底层完全可被 `torch.{load,save}` / `pickle.{dump,load}` 替代。

3. **统一的调用签名 `outputs = model(inputs)`**,`inputs` 是 `list[dict]`,每个 dict 对应一张图像;训练态必须包在 `EventStorage` 上下文里以记录训练统计;推理态可用 `model.eval()` + `torch.no_grad()`,也可直接用封装好的 `DefaultPredictor`。

4. **标准输入 dict 的键集**: `image`(C,H,W Tensor,通道含义由 `cfg.INPUT.FORMAT` 决定,图像归一化在模型内用 `cfg.MODEL.PIXEL_{MEAN,STD}` 完成)、`height`/`width`(期望输出分辨率,与 `image` 字段解耦)、`instances`(训练用 GT,含 `gt_boxes`/`gt_classes`/`gt_masks`/`gt_keypoints`)、`proposals`(Fast R-CNN 风格模型用,含 `proposal_boxes`/`objectness_logits`,若提供则模型按此分辨率输出,更省算)、`sem_seg`(H,W 的 `int` Tensor,语义分割 GT)。

5. **标准输出格式**: 训练态返回 `dict[str->ScalarTensor]` 的损失集合;推理态返回 `list[dict]`,含 `instances`(`pred_boxes`/`scores`/`pred_classes`/`pred_masks`(N,H,W)/`pred_keypoints`(N,num_keypoint,3,每行 `(x,y,score)`,score>0))、`sem_seg`(num_categories,H,W)、`proposals`、`panoptic_seg`(`(Tensor, list[dict])`,Tensor 形状 (H,W) 为像素级 segment id,dict 含 `id`/`isthing`/`category_id`)。

6. **三种获取中间张量的方式**: ①按 `write-models.md` 重写子模型;②直接拆解 `model.backbone / model.proposal_generator / model.roi_heads` 等子模块做部分执行;③用 PyTorch forward hooks。三者都需先阅读现有 `forward` 代码。

---

## 【关键机制与数据】

### 数据流闭环
原文: `DatasetMapper` 的输出本就是符合上述格式的 dict;经 DataLoader 批量化后变成 `list[dict]`,刚好喂入所有 builtin 模型。即 *mapper → DataLoader → model* 三者通过同一套 dict/list[dict] 契约无缝衔接。

### 训练态 vs 推理态的契约差异
原文: 训练态必须在 `EventStorage()` 上下文里调用,统计指标才会被记录;推理态不会写入 storage。两者对输入 dict 的必选键也不同——训练需要 GT 字段,推理只需 `image`(可选 `height`/`width`)。

### 输入 image 与输出分辨率解耦
原文: 输入的 `image` 字段已是预处理后的尺寸(例如 resize 后),但用户可通过 `height`/`width` 指定让模型输出**原始分辨率**的结果;同样,若 `proposals` 被显式提供,模型输出也会按 proposals 的分辨率走,而不是按输入 `image` 的分辨率——原文标注此做法"更高效也更精确"。

### 通道/归一化参数注入位置
原文: `cfg.INPUT.FORMAT` 决定 `image` 通道含义,`cfg.MODEL.PIXEL_{MEAN,STD}` 决定的归一化**在模型内部**执行,而非在 mapper 里。

### 部分执行示例(原文逐字摘录的代码路径)
原文: `features = model.backbone(images.tensor)` → `proposals, _ = model.proposal_generator(images, features)` → `instances = model.roi_heads._forward_box(features, proposals)` → `mask_features = [features[f] for f in model.roi_heads.in_features]` → `mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])`。该片段用以**在 mask head 之前取出 mask features**,说明模型内部的 backbone / proposal_generator / roi_heads 子模块都被设计成可独立调用的对象。

### 性能/数值相关声明
原文未给出任何基准测试数值、参数量或速度数据。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

按文末内部链接梳理本篇与 detectron2 其他模块的依赖拓扑:

- **权重 IO 链路**: 本篇 `DetectionCheckpointer` → [`../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer`](file://../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer),承载 `cfg.MODEL.WEIGHTS` 的实际加载与 `.pth`/`.pkl` 互操作。
- **推理便捷入口**: 文档直接指向 [`../modules/engine.html#detectron2.engine.defaults.DefaultPredictor`](file://../modules/engine.html#detectron2.engine.defaults.DefaultPredictor),作为"不想手写预处理+单图推理"时的封装层;它内部会完成模型加载、预处理并对单张图运行前向。
- **数据结构(实例/框)**: 输入 `instances`、`proposals`,以及输出 `instances`、`proposals`、`panoptic_seg` 中描述的 segment 列表,均依赖 [`../modules/structures.html#detectron2.structures.Instances`](file://../modules/structures.html#detectron2.structures.Instances);框字段(`gt_boxes`/`pred_boxes`/`proposal_boxes`)统一由 [`../modules/structures.html#detectron2.structures.Boxes`](file://../modules/structures.html#detectron2.structures.Boxes) 表达,在本篇中 **Instances 与 Boxes 各被链接两次**(输入侧与输出侧),恰好反映它们在 train/inference 双向契约中都出现。
- **结构化标注**: `gt_masks` 指向 [`../modules/structures.html#detectron2.structures.PolygonMasks`](file://../modules/structures.html#detectron2.structures.PolygonMasks) 与 [`../modules/structures.html#detectron2.structures.BitMasks`](file://../modules/structures.html#detectron2.structures.BitMasks) 两种可选表示;`gt_keypoints` / `pred_keypoints` 关联 [`../modules/structures.html#detectron2.structures.Keypoints`](file://../modules/structures.html#detectron2.structures.Keypoints)。
- **数据侧对接**: [`../modules/data.html#detectron2.data.DatasetMapper`](file://../modules/data.html#detectron2.data.DatasetMapper) 的输出已被声明为符合本篇"Model Input Format"的 dict,经 DataLoader 批量化即得 `list[dict]` 喂入模型——这是上游数据流到本篇模型契约的唯一标准接口。
- **模型定制链路**: 文档显式建议读者参考另一篇 `write-models.md` 来"重写子模型以获取中间张量",表明本文档与自定义模型编写教程构成 *使用 → 改造* 的串联关系。

---

## 【使用方法】

### 构建模型
```python
from detectron2.modeling import build_model
model = build_model(cfg)  # 仅结构 + 随机参数
```

### 加载权重(常见做法)
```python
from detectron2.checkpoint import DetectionCheckpointer
DetectionCheckpointer(model).load(file_path_or_url)  # 通常来自 cfg.MODEL.WEIGHTS
```

### 保存权重
```python
checkpointer = DetectionCheckpointer(model, save_dir="output")
checkpointer.save("model_999")  # 写入 output/model_999.pth
```

### 训练调用(必须在 EventStorage 内)
```python
from detectron2.utils.events import EventStorage
with EventStorage() as storage:
    losses = model(inputs)
```

### 推理调用(两种方式)
- 直接前向:
```python
model.eval()
with torch.no_grad():
    outputs = model(inputs)
```
- 或使用封装: `DefaultPredictor`(参见其 API 文档)

### 输入 dict 的关键配置项
| 配置键 | 含义 |
|---|---|
| `cfg.INPUT.FORMAT` | 决定 `image` 通道含义 |
| `cfg.MODEL.PIXEL_{MEAN,STD}` | 在模型内做图像归一化 |
| `cfg.MODEL.WEIGHTS` | `DetectionCheckpointer.load` 默认目标 |

### 部分执行获取中间张量(以 mask_features 为例)
```python
images = ImageList.from_tensors(...)  # 预处理好的输入
model = build_model(cfg)
features = model.backbone(images.tensor)
proposals, _ = model.proposal_generator(images, features)
instances = model.roi_heads._forward_box(features, proposals)
mask_features = [features[f] for f in model.roi_heads.in_features]
mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])
```

### 其他获取中间张量的途径
- 按 `write-models.md` 重写子模型;
- 用 PyTorch forward hooks 获取模块输入/输出(链接指向 PyTorch 官方教程 *Former Torchies' nn Module Tutorial* 的 hooks 小节)。

原文未涉及具体的命令行/Shell 启动方式,模型使用均在 Python API 层完成。
