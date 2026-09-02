# 教程 2: 自定义数据集

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/customize_datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/customize_datasets.md

# 一体化深度解读：customize_datasets.md

## 【定位】
本篇是 MMSegmentation 在 BiseNetV1_for_PyTorch 仓内的「教程 2：自定义数据集」，系统化阐述在不修改框架源码的前提下，如何将自有数据接入语义分割训练流水线，覆盖「重新组织数据」与「混合数据」两条定制路径。

---

## 【技术要点】

1. **目录约定（重新组织数据路径）**：要求在 `data/my_dataset/` 下建立 `img_dir/{train,val}` 与 `ann_dir/{train,val}`，文件名以 `{img_suffix}` 与 `{seg_map_suffix}` 结尾；**同前缀**的图像与标注自动配对为训练样本。

2. **split 过滤机制**：提供 `split` 参数（文本文件，每行列出样本前缀）后，仅加载前缀出现在该列表中的样本；`split` 文件可与 `ann_dir` 列表组合使用，形成「ann_dir 列表 ↔ split 列表」一一对应关系。

3. **标注像素值硬约束（原文）**：标注必须为与图像同形状 `(H, W)` 的整型图，像素取值范围 `[0, num_classes - 1]`；亦可使用 **Pillow `'P'` 模式**构造带调色板的彩色标注。

4. **RepeatDataset 包装（重复）**：通过 `type='RepeatDataset'` + `times=N` 包装器将原始数据集重复 N 轮，常用于配平不同数据源的样本比例。

5. **两种拼接方式**：
   - **同构拼接**：把 `ann_dir` 写成列表（如 `['anno_dir_1', 'anno_dir_2']`），把 `split` 写成列表（`['split_1.txt', 'split_2.txt']`），二者位置一一对应；也可将二者同时列表化。
   - **异构拼接**：在顶层 `data` 字典的 `train` 字段传入由多个不同数据集配置组成的列表（`train=[dataset_A_train, dataset_B_train]`），同时仍可为每个数据集分别套 `RepeatDataset`。

6. **MultiImageMixDataset 包装（多图混合）**：在 `train_pipeline` 前置多图增强算子（如 `RandomMosaic`，`prob=1`），再以 `MultiImageMixDataset` 作为数据集 wrapper，使 Mosaic / MixUp 这类需跨样本采样的增强成为可能；wrapper 内层 dataset 仍保留轻量 pipeline（`LoadImageFromFile` + `LoadAnnotations`），重负载增强全部交给外层 `train_pipeline`。

---

## 【关键机制与数据】

- **配对与过滤工作流**（原文）：
  - 数据加载单元以「同前缀文件名」为单位配对 `img_dir` 与 `ann_dir`；
  - 若提供 `split`，仅前缀命中列表项的样本被加载；
  - 示例 `split` 内容：`xxx`、`zzz`，则最终参与训练的图像路径为 `data/my_dataset/img_dir/train/xxx{img_suffix}` 与 `.../zzz{img_suffix}`，标注路径同理。

- **RepeatDataset 行为**（原文）：将原始 dataset 配置作为 `dataset` 子字段嵌入，`times=N` 控制重复轮次，原 pipeline 不变。

- **多图混合的执行顺序**（原文代码）：
  1. `RandomMosaic`（`prob=1`）— 多样本拼接；
  2. `Resize`（`img_scale=(1024, 512)`，`keep_ratio=True`）— 几何规整；
  3. `RandomFlip`（`prob=0.5`）— 随机翻转；
  4. `Normalize`（`img_norm_cfg`）— 像素归一化；
  5. `DefaultFormatBundle` — 张量化打包；
  6. `Collect`（`keys=['img', 'gt_semantic_seg']`）— 字段筛选；
  
  而 wrapper 内部 dataset 仅持有 `LoadImageFromFile` + `LoadAnnotations`，实现「读盘 → 出 wrapper → 在 wrapper pipeline 中完成多图增强」的解耦。

- **批处理维度配置**（原文）：`data = dict(imgs_per_gpu=2, workers_per_gpu=2, ...)`，单卡 2 图、2 worker。

- **类别与调色板**（原文）：`MultiImageMixDataset` 示例传入 `classes`、`palette` 与 `reduce_zero_label=False`，用于将索引标注可视化为调色板图。

- **性能/精度数据**：原文未提供任何 benchmark、IoU、时延或显存数字。

---

## 【表格解读】

**原文无表格**。所有信息均以「目录树伪代码」与「Python 配置片段」形式呈现，未出现参数表或性能对比表。

---

## 【公式解读】

**原文无公式**。文中唯一一处数学化表达为标注像素值取值范围 `[0, num_classes - 1]`，它是一个区间约束而非推导公式，且未以 LaTeX 形式给出，故按要求统一归入「无公式」。

---

## 【关联】

- **上下游框架**：本文隶属于 **MMSegmentation** 教程体系（"教程 2"），所有 dataset 配置均消费 `train_pipeline` / `test_pipeline` 与顶层 `data` 字典，需与同仓其他教程（数据预处理、模型配置、训练脚本）协同阅读。

- **跨工具依赖**：
  - 标注生成链路 → **Pillow `'P'` 模式**（调色板索引图）；
  - 多图增强算子 → `RandomMosaic`、并可推广到 **MixUp** 等需要跨样本混合的增强族。

- **数据包装器族谱**：
  - `RepeatDataset`（样本级重复）— 常作为更上游的「数量平衡」工具；
  - `MultiImageMixDataset`（跨样本混合）— 必须与 Mosaic 类算子配合，下游仍可继续叠加 `Resize` / `Normalize` 等单图增强。

- **Pipeline 模块协同**：内层 dataset 的 `LoadImageFromFile` + `LoadAnnotations` 与外层 `train_pipeline` 的 `DefaultFormatBundle` + `Collect` 共同完成「原始文件 → 增强 → 张量化打包 → 字段筛选」全链路。

- **内部链接**：本文档**未提供任何内部链接**（原文与提问方均标注「无」）。

---

## 【使用方法】

### 路径一：重新组织数据
1. 建立 `data/<my_dataset>/img_dir/{train,val}` 与 `data/<my_dataset>/ann_dir/{train,val}`；
2. 文件名采用 `{前缀}{img_suffix}` / `{前缀}{seg_map_suffix}` 命名约定；
3. （可选）在 dataset 配置中传入 `split='path/to/split.txt'`，文本每行一个前缀；
4. 标注以 `(H, W)` 整型图保存，像素 ∈ `[0, num_classes - 1]`，或用 Pillow `'P'` 模式保存彩色调色板图。

### 路径二：重复数据集
```python
dataset_A_train = dict(
    type='RepeatDataset',
    times=N,
    dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline)
)
```

### 路径三：拼接数据集
- **同构拼接**：
  ```python
  dict(type='Dataset_A',
       img_dir='img_dir',
       ann_dir=['anno_dir_1', 'anno_dir_2'],      # 或 split=['split_1.txt','split_2.txt']
       split=['split_1.txt', 'split_2.txt'],       # 与 ann_dir 一一对应
       pipeline=train_pipeline)
  ```
- **异构拼接**：
  ```python
  data = dict(
      imgs_per_gpu=2, workers_per_gpu=2,
      train=[dataset_A_train, dataset_B_train],
      val=dataset_A_val, test=dataset_A_test)
  ```

### 路径四：多图混合（以 Mosaic 为例）
```python
train_pipeline = [
    dict(type='RandomMosaic', prob=1),
    dict(type='Resize', img_scale=(1024, 512), keep_ratio=True),
    dict(type='RandomFlip', prob=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg']),
]

train_dataset = dict(
    type='MultiImageMixDataset',
    dataset=dict(
        classes=classes, palette=palette,
        type=dataset_type, reduce_zero_label=False,
        img_dir=data_root + "images/train",
        ann_dir=data_root + "annotations/train",
        pipeline=[dict(type='LoadImageFromFile'),
                  dict(type='LoadAnnotations')]),
    pipeline=train_pipeline)
```

> 原文未提供「一键启用命令」或脚本启动行，所有定制动作均通过配置文件中的 dict 字段完成。
