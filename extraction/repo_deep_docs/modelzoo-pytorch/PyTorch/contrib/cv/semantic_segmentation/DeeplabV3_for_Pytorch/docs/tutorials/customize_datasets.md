# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/customize_datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/customize_datasets.md

# 一体化深度解读:Tutorial 2: Customize Datasets

## 【定位】
这篇文档解决"MMSegmentation 在用户没有现成支持格式时,如何把自己的数据集接入 DeeplabV3_for_Pytorch 训练/验证流程,以及如何把多个数据集混用 (repeat/concat)"的问题,描述的是框架层面的数据集接入与组合能力。

## 【技术要点】
1. **目录结构约定**:数据需组织为 `data/my_dataset/{img_dir, ann_dir}/{train, val}`,训练样本通过同后缀 (img_suffix / seg_map_suffix) 的图片-标注文件配对。
2. **split txt 文件过滤**:`split` 参数可指向一个 txt,只加载以该 txt 中行为前缀的文件;支持按 prefix 过滤 train/val 集。
3. **标注图像规范**:标注必须是 `(H, W)` 形状的图像,像素取值范围 `[0, num_classes - 1]`,推荐使用 Pillow 的 `'P'` 调色板模式 (palette mode) 制作彩色标注图。
4. **数据集重复 (Repeat)**:用 `RepeatDataset` 包装器对原数据集重复 `N` 次,放在外层配置中。
5. **同类数据集拼接 (Concat, 同类型)**:`ann_dir` 与 `split` 均可接受列表形式 (`[anno_dir_1, anno_dir_2]` / `[split_1.txt, split_2.txt]`),且两者可同时使用并按位置一一对应。
6. **异类数据集拼接 (Concat, 不同类型)**:在顶层 `data` 字典的 `train` 字段下放入一个由多个 dataset config 组成的 list,`val`/`test` 仍可为单一配置。

## 【关键机制与数据】
**数据加载机制**:
- 配对机制:同一前缀 `{xxx, yyy, zzz}` 下的 `img_dir/...` 与 `ann_dir/...` 自动配对为训练样本,因此图片后缀与标注后缀必须保持一致,否则配对失败。
- 过滤机制:`split` 充当白名单,通过 prefix 匹配决定进入管道的文件子集;若不给 `split`,则 `img_dir/ann_dir` 中所有文件都会被加载 (原文: "If `split` argument is given, only part of the files in img_dir/ann_dir will be loaded.")。
- 标注取值约束:像素值 ∈ `[0, num_classes - 1]`,这是后续 loss / 评估模块能正确识别类别索引的前提。

**数据流 (pipeline 视角)**:
- 自定义数据集配置 → `pipeline=train_pipeline` (训练) 或 `test_pipeline` (验证/测试) → 进入 MMSegmentation 通用 dataloader。
- 当使用 `RepeatDataset` 时,数据在 epoch 内被连续采样 `times=N` 次,因此每个 epoch 看到的样本量被放大 N 倍。
- 当使用列表式 `train = [dataset_A_train, dataset_B_train]` 时,MMSegmentation 会把多个数据集顺序拼接成一个大的训练池,采样时不区分来源。

**性能/数据相关数字**:原文未给出训练吞吐量、显存占用、加速比等定量性能数据;唯一显式数字是标注像素取值范围 `[0, num_classes - 1]` 与重复次数 `N`/`M`(用户自定义)。

## 【表格解读】
**原文无表格**。本文档以代码块 (目录结构、Python config) 形式呈现示例,未使用 markdown 表格组织参数或性能对比。

## 【公式解读】
**原文无公式**。本文档未出现 LaTeX 或伪代码形式的数学公式。

## 【关联】
- 上游关联:文档反复引用 `pipeline=train_pipeline` / `pipeline=test_pipeline`,说明自定义数据集配置必须与 MMSegmentation 的 **数据预处理 pipeline** 系统对接;`pipeline` 字段是数据流配置的衔接点。
- 同库教程关联:文档标题为 "Tutorial 2",暗示其前序为 "Tutorial 1"(通常为基础入门,原文未给出内部链接),后续可能涉及自定义模型、自定义训练策略等(原文未明确列出)。
- 同章节其他特性关联:文档涉及 `Dataset_A` / `Dataset_B` 的命名占位符,提示 MMSegmentation 内置了多种数据集类型,这些类型既可单独使用也可被 `RepeatDataset` 包装或互相拼接。
- 工具关联:推荐使用 Pillow 的 `P` (palette) 模式生成标注图,与文档外部链接 `https://pillow.readthedocs.io/en/stable/handbook/concepts.html#palette` 对应,这是外部依赖指引 (原文中以 [pillow] 形式给出,不属于仓内链接)。

## 【使用方法】
**启用方式 (基于原文)**:
1. **目录式自定义 (最简方式)**:
   - 按 `data/my_dataset/{img_dir, ann_dir}/{train, val}` 组织数据。
   - 若只想加载子集,在 `ann_dir/train` (或 `img_dir/train`) 下放置 `split.txt`,逐行列出所需文件前缀 (如 `xxx`、`zzz`)。
   - 在 dataset config 中指定 `img_dir`、`ann_dir`、`split`(可选)以及 `pipeline`。

2. **数据集重复**:
   ```python
   dataset_A_train = dict(
       type='RepeatDataset',
       times=N,
       dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline)
   )
   ```

3. **同类拼接** (任选其一):
   - 拼接 `ann_dir`: `ann_dir=['anno_dir_1', 'anno_dir_2']`
   - 拼接 `split`: `split=['split_1.txt', 'split_2.txt']`
   - 同时拼接两者并按位置一一对应。

4. **异类拼接**:
   在顶层 `data` 字典里:
   ```python
   data = dict(
       imgs_per_gpu=2,
       workers_per_gpu=2,
       train=[dataset_A_train, dataset_B_train],
       val=dataset_A_val,
       test=dataset_A_test
   )
   ```

5. **混合配置 (Repeat + Concat)**:原文末尾给出完整范式,先对 `Dataset_A` 重复 `N` 次、对 `Dataset_B` 重复 `M` 次,再放入 `data['train']` 列表中进行拼接,`val`/`test` 仍走各自 pipeline。

**配置项速览 (原文出现)**:
| 字段 | 含义 |
|---|---|
| `type` | 数据集类型,如 `'RepeatDataset'`、`'Dataset_A'` |
| `times` | `RepeatDataset` 的重复次数 |
| `dataset` | `RepeatDataset` 内层被包装的数据集 config |
| `img_dir` | 图像目录,可为字符串或列表 (拼接时) |
| `ann_dir` | 标注目录,可为字符串或列表 |
| `split` | 过滤用的 split txt,可为字符串或列表 |
| `pipeline` | 训练/测试数据预处理 pipeline |
| `imgs_per_gpu` | 每张 GPU 的 batch size (示例值 2) |
| `workers_per_gpu` | 每张 GPU 的 dataloader worker 数 (示例值 2) |

**注**:原文未涉及具体命令行 (如 `python train.py ...` 的启动方式),也未给出 `num_classes`、`img_suffix`、`seg_map_suffix` 的具体取值示例,这些需结合具体业务自行设定。
