# Use Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/models.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/models.md

# 深度解读：detectron2「Use Models」文档

---

## 【定位】

本文是 detectron2 官方教程中关于**模型使用**的核心指南，描述如何**构建（build）模型结构、加载/保存权重、以训练或推理模式调用模型、读写标准化的输入/输出字典格式**，以及如何在不修改源码的前提下**部分执行模型以获取中间张量**——本质上是一篇"模型层的接口契约与执行范式"参考手册。

---

## 【技术要点】

1. **模型构建函数**：使用 `detectron2.modeling.build_model(cfg)`（以及 `build_backbone`、`build_backbone`、`build_roi_heads`），返回 `torch.nn.Module`，**仅构造结构、参数随机初始化**。
2. **权重加载/保存**：通过 `DetectionCheckpointer` 完成，调用 `.load(file_path_or_url)`（通常传 `cfg.MODEL.WEIGHTS`）；保存用 `DetectionCheckpointer(model, save_dir="output").save("model_999")`，生成 `output/model_999.pth`。同时识别 PyTorch `.pth` 与 model zoo 的 `.pkl` 格式；也可用 `torch.{load,save}` 或 `pickle.{dump,load}` 直接操纵文件。
3. **调用约定**：统一为 `outputs = model(inputs)`，`inputs` 类型为 `list[dict]`；每个 dict 对应一张图像。
4. **训练模式硬约束**：所有内置模型**必须**在 `EventStorage` 上下文内调用，训练统计量会写入该 storage。
5. **推理模式两种入口**：① 推荐 `DefaultPredictor` 封装器（自动加载模型、预处理、单图操作）；② 手动 `model.eval()` + `torch.no_grad()` 后直接前向。
6. **部分执行模型的 3 条路径**：① 改写/继承子模型并新增返回值；② 调用 `model.backbone / model.proposal_generator / model.roi_heads._forward_box / model.roi_heads.mask_pooler` 等子模块手动拼接前向；③ 注册 PyTorch **forward hooks** 捕获中间张量。三种方式均需阅读原 `forward` 源码以理解内部数据流。

---

## 【关键机制与数据】

### 1. 数据流：从数据集到模型

```
DatasetMapper(原始数据) → dict(单图标注) 
   → DataLoader 批处理 → list[dict]（即 model inputs）
   → model(inputs) → list[dict]（推理）或 dict[str→ScalarTensor]（训练）
```

原文明确："The output of the default `DatasetMapper` is a dict that follows the above format. After the data loader performs batching, it becomes `list[dict]` which the builtin models support."

### 2. 模型输入字典字段（原文逐条）

| 字段 | 类型 | 关键约束 |
|---|---|---|
| `"image"` | `Tensor`，形状 `(C, H, W)` | 通道语义由 `cfg.INPUT.FORMAT` 决定；归一化在模型内部按 `cfg.MODEL.PIXEL_{MEAN,STD}` 完成 |
| `"height"` / `"width"` | 标量 | **期望**输出分辨率，可≠ 输入 image 的尺寸（如 resize 后希望回到原分辨率） |
| `"instances"` | `Instances` 对象（仅训练） | 含 `gt_boxes` (`Boxes`)、`gt_classes`（long Tensor，范围 `[0, num_categories)`）、`gt_masks`（`PolygonMasks` 或 `BitMasks`）、`gt_keypoints`（`Keypoints`） |
| `"proposals"` | `Instances` 对象（仅 Fast R-CNN 风格） | 含 `proposal_boxes`（`Boxes`）、`objectness_logits`（P 维 Tensor）；提供时模型按该分辨率输出（原文："This is more efficient and accurate"） |
| `"sem_seg"` | `Tensor[int]`，形状 `(H, W)` | 语义分割训练真值，像素值 = 类别标签（从 0 开始） |

### 3. 模型输出字典字段（原文逐条）

- **训练模式**：返回 `dict[str → ScalarTensor]`，即**所有损失项的字典**。
- **推理模式**：返回 `list[dict]`，每张图一个 dict，按任务分支可能含：
  - `"instances"` → `Instances`：`pred_boxes` (`Boxes`)、`scores`（N 维 Tensor）、`pred_classes`（N 维 long Tensor，`[0, num_categories)`）、`pred_masks`（Tensor `(N, H, W)`）、`pred_keypoints`（Tensor `(N, num_keypoint, 3)`，最后一维为 `(x, y, score)`，score>0）。
  - `"sem_seg"`：Tensor `(num_categories, H, W)`，语义分割预测。
  - `"proposals"` → `Instances`：`proposal_boxes`（`Boxes`）、`objectness_logits`（N 维 torch 向量）。
  - `"panoptic_seg"`：**二元组** `(Tensor, list[dict])`——Tensor 形状 `(H, W)`，元素为 segment id；`list[dict]` 每项含 `id`、`isthing`（bool，thing/stuff 二选一）、`category_id`（`isthing==True` 时为 thing 类 id，否则为 stuff 类 id）。

### 4. 部分执行模型示例（原文逐字）

```python
images = ImageList.from_tensors(...)  # 预处理后的输入 tensor
model = build_model(cfg)
features = model.backbone(images.tensor)                          # 1. 骨干网络
proposals, _ = model.proposal_generator(images, features)         # 2. RPN 生成 proposals
instances = model.roi_heads._forward_box(features, proposals)      # 3. box 头前向
mask_features = [features[f] for f in model.roi_heads.in_features]# 4. 收集 mask 头输入特征
mask_features = model.roi_heads.mask_pooler(mask_features,
                       [x.pred_boxes for x in instances])         # 5. RoI Align 池化
```

该流程在 mask 头之前取出 `mask_features`，是典型的"绕开 `forward()`、手动拼接子模块"的用法。

---

## 【表格解读】

**原文无表格**。

（注：上文"关键机制与数据"中的输入/输出字段对照表是我为便于呈现而从原文中提取的层级列表信息重新组织而成，**并非原文表格**；原文以"项目符号列表"形式呈现。）

---

## 【公式解读】

**原文无公式**。文档以接口规范与代码示例为主，不含数学公式或伪代码推导。

---

## 【关联】

本文位于模型层接口的中心位置，与其上下游模块通过文末内部链接紧密关联：

1. **检查点模块** → [DetectionCheckpointer](../modules/checkpoint.html#detectron2.checkpoint.DetectionCheckpointer)：负责 `.load/.save` 的实现细节，与本文"Load/Save a Checkpoint"小节直接对应。
2. **推理封装器** → [DefaultPredictor](../modules/engine.html#detectron2.engine.defaults.DefaultPredictor)：在"Use a Model → Inference"小节中被推荐作为简单推理入口。
3. **数据结构层（训练输入与推理输出共用）**：
   - [Instances](../modules/structures.html#detectron2.structures.Instances)：输入 `gt_*` 与输出 `pred_*` 的容器，贯穿训练/推理。
   - [Boxes](../modules/structures.html#detectron2.structures.Boxes)：输入 `gt_boxes/proposal_boxes` 与输出 `pred_boxes/proposal_boxes` 的统一表示。
   - [PolygonMasks](../modules/structures.html#detectron2.structures.PolygonMasks) 与 [BitMasks](../modules/structures.html#detectron2.structures.BitMasks)：输入 `gt_masks` 的两种可选表示。
   - [Keypoints](../modules/structures.html#detectron2.structures.Keypoints)：输入 `gt_keypoints` 的表示；输出端则降级为 `Tensor (N, num_keypoint, 3)`。
4. **数据预处理** → [DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper)：本文"How it connects to data loader"小节明确说明，`DatasetMapper` 的输出即是符合本文"Model Input Format"规范的 dict，经 DataLoader 批处理后变为 `list[dict]` 喂入模型。
5. **横向教程**：[write-models.md](./write-models.md)：在"Partially execute a model → 选项 1"中引用，是"如何自定义/改写子模型"的官方指引，与本文形成"使用 vs. 改写"的对偶。

---

## 【使用方法】

以下为原文中**显式给出**的命令/配置项（代码片段逐字保留）：

**① 构建模型**：
```python
from detectron2.modeling import build_model
model = build_model(cfg)  # returns a torch.nn.Module
```

**② 加载权重**（通常路径取自 `cfg.MODEL.WEIGHTS`）：
```python
from detectron2.checkpoint import DetectionCheckpointer
DetectionCheckpointer(model).load(file_path_or_url)
```

**③ 保存权重**：
```python
checkpointer = DetectionCheckpointer(model, save_dir="output")
checkpointer.save("model_999")  # save to output/model_999.pth
```

**④ 训练调用**（必须在 `EventStorage` 内）：
```python
from detectron2.utils.events import EventStorage
with EventStorage() as storage:
  losses = model(inputs)
```

**⑤ 简单推理**（推荐）：`DefaultPredictor`，详细用法见其 API doc。

**⑥ 手动推理**：
```python
model.eval()
with torch.no_grad():
  outputs = model(inputs)
```

**⑦ 部分执行模型**（mask 特征提取示例见上文"关键机制与数据"第 4 点）。

**关键配置项（原文出现的 cfg 字段）**：
- `cfg.MODEL.WEIGHTS` —— 权重文件路径
- `cfg.INPUT.FORMAT` —— 图像通道语义
- `cfg.MODEL.PIXEL_{MEAN,STD}` —— 模型内部归一化参数

（原文未提供具体的命令行启动脚本，所有用法均以 Python API 形式给出。）
