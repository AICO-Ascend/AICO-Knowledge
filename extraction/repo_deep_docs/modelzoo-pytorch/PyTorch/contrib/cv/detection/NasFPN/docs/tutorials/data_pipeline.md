# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/data_pipeline.md

# 一体化深度解读：Tutorial 3: Customize Data Pipelines

## 【定位】
本教程系统阐述 mmdet（基于 MMCV）面向目标检测任务的数据准备流水线（data pipeline）设计原理、内置算子行为约定以及自定义扩展方法，帮助用户在不改框架源码的前提下灵活组合/新增数据增强与格式化步骤。

---

## 【技术要点】

1. **数据加载范式**：沿用 PyTorch 的 `Dataset` + `DataLoader` 多 worker 取数约定，单个样本以 **dict** 形式返回，且字段名与模型 `forward` 的入参一一对应。
2. **`DataContainer` 类型**：因检测任务中图像、bbox 等尺寸不一，MMCV 引入 `DataContainer` 专门承载"张量尺寸不一致但需打包到 batch"的字段；详见 `mmcv/parallel/data_container.py`。
3. **流水线与数据集解耦**：数据集 (`Dataset`) 负责标注处理（如何解析），流水线 (`pipeline`) 负责样本组装（如何变换），每个算子都是"dict → dict"的纯函数式映射；蓝色为算子、绿色为新增 key、橙色为更新 key。
4. **四类算子分类**：data loading / pre-processing / formatting / test-time augmentation。Faster R-CNN 经典 pipeline 包含 8 个步骤，`img_scale=(1333, 800)`、`keep_ratio=True`、`flip_ratio=0.5`、`size_divisor=32`、`to_rgb=True`，并复用 `img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)`。
5. **字段生命周期约定**：每个内置算子明确声明其对 dict 的 `add / update / remove` 字段（例如 `LoadImageFromFile` add `img/img_shape/ori_shape`；`Collect` 在 add `img_meta` 的同时 remove 其余未在 `keys` 中指定的 key）。
6. **三步自定义流程**：① 在任意文件（示例 `my_pipeline.py`）中用 `@PIPELINES.register_module()` 注册类；② 导入该类；③ 在 config 的 `train_pipeline` 列表里以 `dict(type='MyTransform')` 插入。

---

## 【关键机制与数据】

**工作原理（数据流视角）**
- 原始样本（图像路径 + 标注）经过流水线各算子顺序处理，每步接收上游的 `results` dict，输出新的 `results` dict，下游算子继续消费。
- 蓝色块 = 算子节点、绿色键 = 该算子新增字段、橙色键 = 该算子更新已有字段；该图示由原文 `![pipeline figure](../../resources/data_pipeline.png)` 提供（原文未给具体数值，是结构示意）。
- `DataContainer` 在 batch collation 阶段被 `collate` 函数识别，对不同形状的张量做"按维度 0 堆叠或保持为 list"，从而适配 `DataLoader` 输出。
- `Collect` 是流水线的最后一道闸门：它一方面按 `meta_keys` 组装 `img_meta`，另一方面把 `keys` 之外的字段统统 `remove`，从而控制最终送入模型 forward 的字段集。
- 推理侧通过 `MultiScaleFlipAug` 包装子变换列表 `transforms`，内部对图像做多尺度/翻转后再次走 `Resize → RandomFlip → Normalize → Pad → ImageToTensor → Collect`，避免在 train_pipeline 之外重复声明。

**性能数据**
- 原文：未给出任何吞吐量、加速比或精度数字，仅描述 pipeline 结构与字段约定。

---

## 【表格解读】

原文无标准 markdown 表格。但原文以"列表 + 子项"的结构给出了**算子字段操作矩阵**，这是本教程最核心的可对照结构。下面用 markdown 表格逐字还原其内容，并按节解读。

### 表 1：Data loading 类算子的字段影响

| 算子 (type) | add (新增字段) |
|---|---|
| LoadImageFromFile | img, img_shape, ori_shape |
| LoadAnnotations | gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg, bbox_fields, mask_fields |
| LoadProposals | proposals |

**解读**：三步把磁盘上的图像路径、检测标注和外部候选框（proposals，如 RPN 阶段或外部 detector 给出）读入 dict。注意 `LoadAnnotations` 同时新增了 `bbox_fields` / `mask_fields` 这类"字段名字段"，供后续 `Resize` / `RandomFlip` / `Pad` 通过通配符 `*bbox_fields`、`*mask_fields` 自动级联更新所有相关标注。

### 表 2：Pre-processing 类算子的字段影响

| 算子 (type) | add | update |
|---|---|---|
| Resize | scale, scale_idx, pad_shape, scale_factor, keep_ratio | img, img_shape, *bbox_fields, *mask_fields, *seg_fields |
| RandomFlip | flip | img, *bbox_fields, *mask_fields, *seg_fields |
| Pad | pad_fixed_size, pad_size_divisor | img, pad_shape, *mask_fields, *seg_fields |
| RandomCrop | — | img, pad_shape, gt_bboxes, gt_labels, gt_masks, *bbox_fields |
| Normalize | img_norm_cfg | img |
| SegRescale | — | gt_semantic_seg |
| PhotoMetricDistortion | — | img |
| Expand | — | img, gt_bboxes |
| MinIoURandomCrop | — | img, gt_bboxes, gt_labels |
| Corrupt | — | img |

**解读**：
- `Resize` 既会按 `img_scale=(1333, 800), keep_ratio=True` 调整 `img` 与 `img_shape`，又通过 `*bbox_fields` 通配同步缩放所有 bbox，避免标签–图像尺寸脱节。
- `RandomFlip` / `Pad` / `RandomCrop` 共享 `*bbox_fields`、`*mask_fields`、`*seg_fields` 通配语义，是 bbox 与 mask 几何一致性保证的关键。
- `Pad` 的 `size_divisor`（如 32）与 `Resize` 的 `img_scale` 共同决定是否能被 backbone 下采样整除，是 mmdet 默认约定的硬件对齐点。
- `Normalize` 会把整个 `img_norm_cfg`（含 mean/std/to_rgb）回填到 dict，便于复算与可视化。
- `PhotoMetricDistortion`（亮度/对比度/饱和度/色相扰动）、`Corrupt`（噪声、模糊、雾等腐蚀）属于图像增强族，不触碰标签。

### 表 3：Formatting 类算子的字段影响

| 算子 (type) | add | update / 行为 |
|---|---|---|
| ToTensor | — | update: specified by `keys` |
| ImageToTensor | — | update: specified by `keys` |
| Transpose | — | update: specified by `keys` |
| ToDataContainer | — | update: specified by `fields` |
| DefaultFormatBundle | — | update: img, proposals, gt_bboxes, gt_bboxes_ignore, gt_labels, gt_masks, gt_semantic_seg |
| Collect | img_meta (meta_keys 指定) | remove: all other keys except those in `keys` |

**解读**：
- 前四个算子都是"通用转换"，具体处理的字段由调用时的 `keys` / `fields` 参数决定——同一算子可复用到不同字段。
- `DefaultFormatBundle` 是检测任务的"打包快捷方式"，一次性把所有常用检测字段转成 Tensor/DataContainer，省去逐字段配置。
- `Collect` 是流水线的统一收口：除了显式声明的 `keys` 字段以及按 `meta_keys` 聚合的 `img_meta` 之外，**移除非保留字段**，确保 dict 进入模型前是"最瘦"的——这是流水线对模型 forward 接口契约的最终执行点。

### 表 4：Test-time augmentation

| 算子 (type) | 用途 |
|---|---|
| MultiScaleFlipAug | 多尺度 + 翻转 TTA 包装器，内部把 `transforms` 列表对图像作用后送入 `ImageToTensor` 与 `Collect` |

**解读**：原文仅列名（"Test time augmentation" 节），未细化字段操作。其作用是把 `transforms` 这一子 pipeline 作用在每个尺度/翻转组合上，并自动完成 tensor 化和字段收集。原文 `test_pipeline` 的 `flip=False` 表示该具体配置不使用翻转 TTA。

---

## 【公式解读】

原文无公式（无 LaTeX、无伪代码形式的数学表达式）。如需"以式子形式"概括流水线，可写为：

$$
\mathrm{results}_0 \xrightarrow{f_1} \mathrm{results}_1 \xrightarrow{f_2} \mathrm{results}_2 \xrightarrow{\dots} \xrightarrow{f_n} \mathrm{results}_n
$$

其中每个 $f_i$ 为算子 `i`（dict→dict 的纯函数），$\mathrm{results}_0$ 为 `Dataset.__getitem__` 起始 dict，$\mathrm{results}_n$ 经 `Collect` 收口后送入模型 `forward`。但请注意：**此式为对原文结构的概念性概括，并非原文中给出的公式。**

---

## 【关联】

- **`DataContainer` 上游（数据承载层）**：见 `mmcv/parallel/data_container.py`（原文已给出链接），由 `collate` 函数消费。Detection pipeline 中的 `gt_bboxes`、`gt_masks`、`gt_semantic_seg` 一般都包装成 `DataContainer` 以容忍 batch 内不同图像大小。
- **`Dataset` 与 `PIPELINES` 注册表**：`@PIPELINES.register_module()` 装饰的类由 mmdet datasets 负责按 `type` 字符串解析到具体类，因此 `my_pipeline.py` 一旦被导入即可在 config 中通过 `dict(type='MyTransform')` 调用。
- **与 Faster R-CNN 配置的耦合**：`train_pipeline` 末端的 `Collect(keys=['img','gt_bboxes','gt_labels'])` 必须覆盖模型 forward 的全部入参，否则会触发 KeyError——`img_meta` 同时携带 `img_shape / pad_shape / scale_factor / ori_shape` 等，是模型 `forward_dummy` 与真实的 `forward` 共享相同字段契约的关键。
- **TTA 与训练解耦**：`MultiScaleFlipAug` 把推理增强作为单算子封装，从而让 `test_pipeline` 可独立于 `train_pipeline` 配置；`ImageToTensor` 作为其下游节点，确保 TTA 输出仍是 Tensor+Collect 的标准形态。
- **图像增强族 → 模型端**：所有 `update: img` 的算子（`Resize/RandomFlip/Pad/Normalize/PhotoMetricDistortion/Expand/MinIoURandomCrop/Corrupt`）联合作用于 `img`，而 bbox/seg/mask 由 `*bbox_fields / *mask_fields / *seg_fields` 同步更新——这种"图-标同步"语义是 mmdet 与 mmsegmentation 共享流水线约定的体现。
- **README/教程同系列**：本教程为 modelzoo 中的 Tutorial 3（前两篇为环境与配置相关，原文未给出链接，按"内部链接：(无)"提示处理），与同仓其它 detection tutorial（如 configs 说明、NasFPN 专项）共享同一套 pipeline 约定。

---

## 【使用方法】

**启用/扩展流程（原文 3 步 + 必要上下文）：**

1. **新建文件（如 `my_pipeline.py`），注册自定义算子**：
   ```python
   from mmdet.datasets import PIPELINES

   @PIPELINES.register_module()
   class MyTransform:
       def __call__(self, results):
           results['dummy'] = True
           return results
   ```
   算子必须满足：输入一个 dict，返回一个 dict；可选地定义 `__init__` 接收超参。

2. **在 config 或训练脚本中导入该文件**：
   ```python
   from .my_pipeline import MyTransform
   ```
   导入会触发 `@PIPELINES.register_module()` 的副作用，把类登记到全局 registry。

3. **在 config 的 `train_pipeline` 中以字符串方式引用**：
   ```python
   img_norm_cfg = dict(
       mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
   train_pipeline = [
       dict(type='LoadImageFromFile'),
       dict(type='LoadAnnotations', with_bbox=True),
       dict(type='Resize', img_scale=(1333, 800), keep_ratio=True),
       dict(type='RandomFlip', flip_ratio=0.5),
       dict(type='Normalize', **img_norm_cfg),
       dict(type='Pad', size_divisor=32),
       dict(type='MyTransform'),          # ← 自定义算子
       dict(type='DefaultFormatBundle'),
       dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
   ]
   ```

**关键配置项摘录（原文逐字保留）：**
- `img_norm_cfg.mean = [123.675, 116.28, 103.53]`
- `img_norm_cfg.std = [58.395, 57.12, 57.375]`
- `img_norm_cfg.to_rgb = True`
- `Resize.img_scale = (1333, 800)`，`keep_ratio = True`
- `RandomFlip.flip_ratio = 0.5`
- `Pad.size_divisor = 32`
- `Collect.keys` 必须包含模型 forward 所需全部字段（默认 Faster R-CNN：`['img','gt_bboxes','gt_labels']`）
- 推理 `MultiScaleFlipAug.img_scale = (1333, 800)`，`flip = False`，内部 `transforms` 链为 `Resize → RandomFlip → Normalize → Pad → ImageToTensor → Collect`

**原文未涉及**：命令行启动方式、超参搜索/调优建议、与具体 backbone 的字段约定差异等，原文均未给出，按"原文未涉及"处理。
