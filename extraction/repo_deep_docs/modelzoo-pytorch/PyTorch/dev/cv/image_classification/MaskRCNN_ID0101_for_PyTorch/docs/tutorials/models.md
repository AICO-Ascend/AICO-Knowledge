# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/models.md

# 一体化深度解读:detectron2 "Use Models" 指南

## 【定位】

这篇文档是 detectron2 模型使用层的总入口文档,系统说明如何**构建模型、加载/保存检查点、调用模型进行训练或推理**,以及**内置模型标准化的输入/输出字典格式**,并提供**部分执行模型获取中间张量**的三种可选方案——解决 detectron2 用户面对 `nn.Module` 时"如何拿到结构、如何喂数据、如何读结果、如何掏中间层"这一整套使用链路上的所有基础问题。

---

## 【技术要点】

1. **模型构建三件套**:通过 `detectron2.modeling` 下的工厂方法 `build_model(cfg)`、`build_backbone`、`build_roi_heads` 构建模型/子模型,返回标准的 `torch.nn.Module`;`build_model` 仅搭建结构并填充**随机参数**,不含预训练权重。
2. **检查点加载/保存**:`detectron2.checkpoint.DetectionCheckpointer(model)` 同时支持 PyTorch 的 `.pth` 与 model zoo 的 `.pkl` 两种格式;加载方式为 `checkpointer.load(file_path_or_url)`(通常传 `cfg.MODEL.WEIGHTS`),保存方式为 `checkpointer.save("model_999")` 写到 `save_dir` 指定的目录。
3. **统一调用接口**:`outputs = model(inputs)`,其中 `inputs` 必须是 `list[dict]`,每个 dict 对应一张图像;训练态还需外套 `EventStorage()` 上下文,推理态可配合 `model.eval()` + `torch.no_grad()`。
4. **零代码推理封装**:`detectron2.engine.defaults.DefaultPredictor` 是模型包装器,内置**模型加载、预处理、单图推理**默认行为,适合简单推理场景(注意其按单图操作而非 batch)。
5. **训练/推理输出契约**:训练时输出 `dict[str->ScalarTensor]` 的损失字典;推理时输出 `list[dict]`,每张图一个字典,字段依任务而定(`instances` / `sem_seg` / `proposals` / `panoptic_seg`)。
6. **部分执行模型取中间张量**:三条路径——(a) 按 `write-models.md` 重写子模块/头部使其返回所需张量;(b) 自定义 forward,直接调用 `model.backbone` / `model.proposal_generator` / `model.roi_heads._forward_box` / `model.roi_heads.mask_pooler` 等子模块;(c) 利用 PyTorch **forward hooks** 抓取特定模块的输入/输出,可与 (b) 组合使用。

---

## 【关键机制与数据】

**原文:** 数据流上,默认 `DatasetMapper` 产出的单样本字典格式与文档所述"Model Input Format"完全一致;经过 DataLoader 的 batching 后变成 `list[dict]`,正好喂给内置模型。即**数据格式契约贯穿 Mapper → DataLoader → Model 三段**。

**原文:** 输入图像张量形状为 `(C, H, W)`,通道语义由 `cfg.INPUT.FORMAT` 决定;图像归一化在模型内部使用 `cfg.MODEL.PIXEL_{MEAN,STD}` 完成(而非在外部预处理)。

**原文:** 类别标签取值范围统一为 `[0, num_categories)`;目标检测关键点预测张量形状为 `(N, num_keypoint, 3)`,最后一维为 `(x, y, score)`,且**得分必须 > 0**(原文:"Scores are larger than 0")。

**原文:** 语义分割输出形状为 `(num_categories, H, W)`;全景分割输出为二元组 `(Tensor, list[dict])`,Tensor 形状 `(H, W)`、元素值为 segment id,列表中每个 dict 含 `id` / `isthing` / `category_id` 三字段,`isthing==True` 时 `category_id` 表示 thing 类 id,否则为 stuff 类 id。

**原文:** `"height"`、`"width"` 是**期望输出**分辨率,不一定等于 `"image"` 字段的实际尺寸——例如 `image` 是 resize 后的,而用户希望 boxes/masks 回填到**原始分辨率**;同理 `"proposals"` 若由调用方提供,模型输出将按 proposal 所在分辨率给出(原文称此"more efficient and accurate")。

**原文:** 部分执行示例代码中,通过 `model.roi_heads.in_features` 取到 ROI 头所需的特征层名列表,再用 `model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])` 在 mask head 之前拿到 `mask_features`——表明 ROI 头的特征选择由 `in_features` 列表控制,pooler 接受 boxes 列表作为 RoIAlign 的采样依据。

---

## 【表格解读】

原文无表格(全文以嵌套无序列表/代码块描述输入输出契约,无任何 markdown 表格)。

---

## 【公式解读】

原文无 LaTeX 数学公式。

文档中唯一与"算法/流程等价"相关的伪代码片段是**部分执行模型示例**(逐字保留):

```python
images = ImageList.from_tensors(...)  # preprocessed input tensor
model = build_model(cfg)
features = model.backbone(images.tensor)
proposals, _ = model.proposal_generator(images, features)
instances = model.roi_heads._forward_box(features, proposals)
mask_features = [features[f] for f in model.roi_heads.in_features]
mask_features = model.roi_heads.mask_pooler(mask_features, [x.pred_boxes for x in instances])
```

符号/对象含义:

| 符号 | 含义/作用 |
|---|---|
| `images` | `ImageList` 对象,封装 batch 后的图像张量及尺寸信息(由 `ImageList.from_tensors(...)` 从预处理张量构造) |
| `images.tensor` | batch 张量,直接喂给 backbone |
| `features` | dict,key 是 FPN 层名(如 `"p2"`/`"p3"`/`"p4"`/`"p5"`),value 是对应特征图 |
| `model.backbone(images.tensor)` | 调用 backbone 子模块,得到多尺度特征 `features` |
| `model.proposal_generator(images, features)` | RPN/候选框生成器,返回 `(proposals, losses)`,此处用 `_` 丢弃训练损失 |
| `proposals` | `Instances` 类型的候选区域 |
| `model.roi_heads._forward_box(features, proposals)` | 直接调用 box head 私有方法,得到带 `pred_boxes`/`scores`/`pred_classes` 的 `instances` |
| `model.roi_heads.in_features` | ROI 头要求输入的特征层名字列表 |
| `[features[f] for f in model.roi_heads.in_features]` | 按 ROI 头要求的层名挑选对应特征图 |
| `[x.pred_boxes for x in instances]` | 每张图一张 instance,各自取出 box 用于 ROIAlign 采样 |
| `model.roi_heads.mask_pooler(...)` | mask head 的 RoIAlign 池化层,产出 mask head 的输入特征 `mask_features`(尚未进入 mask 卷积) |

整段代码的目的就是**在 mask head 真正计算之前截获 `mask_features`**,从而获得可用于可视化、辅助损失或自定义下游任务的中间表示。

---

## 【关联】

文档与其他模块/教程构成如下依赖网(基于文末内部链接):

| 关联对象 | 关系 |
|---|---|
| `detectron2.checkpoint.DetectionCheckpointer` | 负责加载/保存 `.pth`、`.pkl` 模型文件,本指南是其上层使用示例 |
| `detectron2.engine.defaults.DefaultPredictor` | 模型的高级推理封装,内置预处理与单图推理,与"裸调 `model.eval()`+`no_grad()`"路径并列 |
| `detectron2.structures.Instances` | 输入端:训练时承载 `gt_boxes`/`gt_classes`/`gt_masks`/`gt_keypoints`;输出端:承载 `pred_boxes`/`scores`/`pred_classes`/`pred_masks`/`pred_keypoints`;Fast R-CNN 风格模型还承载 `proposals` |
| `detectron2.structures.Boxes` | `Instances` 内 `gt_boxes`/`proposal_boxes`/`pred_boxes` 的容器,存 N 个或 P 个 box |
| `detectron2.structures.PolygonMasks` / `BitMasks` | `Instances.gt_masks` 的两种存储实现,文档明确两者均被接受 |
| `detectron2.structures.Keypoints` | `Instances.gt_keypoints` 的容器,存 N 个关键点集合 |
| `detectron2.data.DatasetMapper` | **上游数据契约的源头**:其输出单样本 dict 严格遵循本文档"Model Input Format";DataLoader 把它 batch 成 `list[dict]` 后直接喂给模型——即文档默认的"输入契约"由 Mapper 保证 |
| `./write-models.md`(教程) | 用于"重写子模块以返回额外张量"选项 1,扩展自定义模型能力 |
| PyTorch 官方 `former_torchies/nnft_tutorial.html`(forward hooks) | 选项 3 的外部依赖,提供在不修改源码的情况下抓取中间张量的能力 |

**逻辑流总结**:`DatasetMapper`(数据)→ `DataLoader`(`list[dict]` 批量化)→ 内置模型(`build_model`)→ 检查点加载(`DetectionCheckpointer`)→ 训练(`EventStorage`)/推理(`DefaultPredictor` 或裸 forward)→ 输出(`Instances`/`sem_seg`/`panoptic_seg` 等结构化预测)。

---

## 【使用方法】

**启用与构建**
- 导入:`from detectron2.modeling import build_model`
- 构建:`model = build_model(cfg)`,返回 `torch.nn.Module`。
- 子模型构建:同模块下还有 `build_backbone`、`build_roi_heads`(原文未给出具体调用示例)。

**加载/保存检查点**
- 导入:`from detectron2.checkpoint import DetectionCheckpointer`
- 加载(常见用法):`DetectionCheckpointer(model).load(file_path_or_url)`,文件路径常取自 `cfg.MODEL.WEIGHTS`。
- 保存(需先指定 `save_dir`):
  ```python
  checkpointer = DetectionCheckpointer(model, save_dir="output")
  checkpointer.save("model_999")  # 实际写到 output/model_999.pth
  ```
- 支持格式:PyTorch `.pth`、detectron2 model zoo 的 `.pkl`。
- 完全手动:`torch.{load,save}` 处理 `.pth`;`pickle.{dump,load}` 处理 `.pkl`。

**训练调用**
- 必须在 `EventStorage` 上下文内:
  ```python
  from detectron2.utils.events import EventStorage
  with EventStorage() as storage:
      losses = model(inputs)
  ```
- 返回值:`dict[str->ScalarTensor]` 的损失字典。

**推理调用**
- 简单路径:`DefaultPredictor`(详见其 API 文档)。
- 直接路径:
  ```python
  model.eval()
  with torch.no_grad():
      outputs = model(inputs)
  ```
- 注意 `DefaultPredictor` 默认为**单图**而非 batch;裸 forward 路径则保留 batch 能力。

**输入字典标准字段(完整清单)**

| 字段 | 类型 | 用途/备注 |
|---|---|---|
| `"image"` | `Tensor` (C, H, W) | 必填;通道含义由 `cfg.INPUT.FORMAT` 定义;归一化在模型内部用 `cfg.MODEL.PIXEL_{MEAN,STD}` 完成 |
| `"height"` / `"width"` | int | **期望**输出分辨率,可与 `"image"` 实际尺寸不同 |
| `"instances"` | `Instances`(训练用) | 含 `gt_boxes`/`gt_classes`/`gt_masks`/`gt_keypoints` |
| `"proposals"` | `Instances`(Fast R-CNN 风格) | 含 `proposal_boxes`/`objectness_logits`;提供后模型按此分辨率输出 |
| `"sem_seg"` | `Tensor[int]` (H, W) | 语义分割 GT;类别 id 从 0 起 |

**输出字典标准字段**

| 字段 | 类型 | 说明 |
|---|---|---|
| `"instances"` | `Instances` | `pred_boxes`/`scores`/`pred_classes`/`pred_masks`(N,H,W)/`pred_keypoints`(N,num_keypoint,3,(x,y,score>0)) |
| `"sem_seg"` | `Tensor` (num_categories, H, W) | 语义分割预测 |
| `"proposals"` | `Instances` | `proposal_boxes`/`objectness_logits` |
| `"panoptic_seg"` | `(Tensor(H,W), list[dict])` | Tensor 元素为 segment id;list 中每 dict 含 `id`/`isthing`/`category_id`(`isthing==True` 表示 thing 类,否则 stuff 类) |

**部分执行模型(原文"原文:" 给出三种方案,见上节公式解读与关联)**
1. 重写子模块/头部(参见 `./write-models.md`)。
2. 自定义 forward,直接调用 `model.backbone`、`model.proposal_generator`、`model.roi_heads._forward_box`、`model.roi_heads.mask_pooler` 等(完整代码见上文公式解读)。
3. 注册 PyTorch **forward hooks**(教程链接见原文)。

**原文未涉及的内容**:文档未提供具体的命令行启动方式、未给出端到端训练脚本示例、未涉及分布式训练、AMP/混合精度、梯度累积等训练侧的工程化配置——这些均需查阅 detectron2 其它文档/教程。
