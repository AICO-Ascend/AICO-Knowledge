# Tutorial 3: Custom Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/3_data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/3_data_pipeline.md

【定位】
本文档是 MMPose（基于 PyTorch 的姿态估计工具库）的教程 3，主题为"自定义数据流水线"，解决姿态估计任务中如何**设计、配置与扩展数据预处理流水线（Data Pipeline）**的问题。具体能力包括：阐明 pipeline 的总体设计哲学（Dataset / DataLoader 解耦、`DataContainer` 处理变长数据）、给出 Simple Baseline (ResNet50) 的 train/val pipeline 完整示例及每个操作对 dict 字段的增删改、以及提供向 MMPose 注册自定义 Transform 的标准三步流程。

【技术要点】
- **总体架构**：使用 `Dataset` + `DataLoader`（多 worker）做数据加载；`Dataset` 返回 dict，其 key 对应模型 `forward` 方法的参数名。
- **变长数据**：姿态估计中图像尺寸、gt bbox 尺寸不固定，因此引入 MMCV 中的 `DataContainer` 类型来收集和分发不同尺寸的数据。
- **解耦设计**：数据集（dataset）定义如何处理标注（annotations），数据流水线（pipeline）定义准备数据 dict 的全部步骤，二者解耦。
- **Pipeline 形态**：由若干操作（operations）顺序串接而成，**每个操作以 dict 为输入并以 dict 输出**，传给下一个 transform。
- **四大类操作**：数据加载（data loading）、预处理（pre-processing）、格式化（formatting）、标签生成（label generating）。
- **Simple Baseline (ResNet50) 训练流水线关键参数**：随机翻转概率 `flip_prob=0.5`；半身变换 `num_joints_half_body=8, prob_half_body=0.3`；随机缩放旋转 `rot_factor=40, scale_factor=0.5`；标签生成高斯热图 sigma `sigma=2`；归一化均值 `mean=[0.485, 0.456, 0.406]`，标准差 `std=[0.229, 0.224, 0.225]`（即 ImageNet 统计量）。
- **自定义扩展三步走**：
  1. 在任意文件中用 `@PIPELINES.register_module()` 装饰器注册新 Transform（输入 dict、返回 dict）。
  2. `from .my_pipeline import MyTransform` 导入。
  3. 在 config 文件的 `train_pipeline` 列表中按位置插入 `dict(type='MyTransform')`。
- **Collect 阶段**：`keys` 指定保留并移入 `img` 的字段；`meta_keys` 指定保留并打包到 `img_meta` 的字段；其余字段被移除。

【关键机制与数据】
- **工作原理**：pipeline 是一个有序的字典变换链（pipeline consists of a sequence of operations. Each operation takes a dict as input and also output a dict for the next transform）。原始样本经 `LoadImageFromFile` → 几何增强（翻转/半身/缩放旋转/仿射）→ 张量化与归一化 → 标签生成（热图）→ `Collect` 整理为模型所需的标准 dict。
- **数据流（字段流向）**（原文逐条）：
  - `LoadImageFromFile`：**add** `img, img_file`
  - `TopDownRandomFlip`：**update** `img, joints_3d, joints_3d_visible, center`
  - `TopDownHalfBodyTransform`：**update** `center, scale`
  - `TopDownGetRandomScaleRotation`：**update** `scale, rotation`
  - `TopDownAffine`：**update** `img, joints_3d, joints_3d_visible`
  - `NormalizeTensor`：**update** `img`
  - `ToTensor`：**update** `img`
  - `TopDownGenerateTarget`：**add** `target, target_weight`
  - `Collect`：**add** `img_meta`（键由 `meta_keys` 指定）；**remove** 除 `keys` 指定外的所有键
- **性能数据**：原文未提供任何训练/推理性能数据。

【表格解读】
原文无表格。但原文以**字典列表**形式列出了 Simple Baseline (ResNet50) 的完整 `train_pipeline` 与 `val_pipeline`，并按"Data loading / Pre-processing / Generating labels / Formatting"四个分组给出每一步对字段的影响（add / update / remove）。下面按原文逐字还原这两段配置（作为关键信息表呈现）：

**train_pipeline（原文逐字）**：
| # | type | 关键参数 |
|---|------|----------|
| 1 | LoadImageFromFile | — |
| 2 | TopDownRandomFlip | flip_prob=0.5 |
| 3 | TopDownHalfBodyTransform | num_joints_half_body=8, prob_half_body=0.3 |
| 4 | TopDownGetRandomScaleRotation | rot_factor=40, scale_factor=0.5 |
| 5 | TopDownAffine | — |
| 6 | ToTensor | — |
| 7 | NormalizeTensor | mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225] |
| 8 | TopDownGenerateTarget | sigma=2 |
| 9 | Collect | keys=['img','target','target_weight'], meta_keys=['image_file','joints_3d','joints_3d_visible','center','scale','rotation','bbox_score','flip_pairs'] |

**val_pipeline（原文逐字）**：
| # | type | 关键参数 |
|---|------|----------|
| 1 | LoadImageFromFile | — |
| 2 | TopDownAffine | — |
| 3 | ToTensor | — |
| 4 | NormalizeTensor | mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225] |
| 5 | Collect | keys=['img'], meta_keys=['image_file','center','scale','rotation','bbox_score','flip_pairs'] |

**逐行解读**：
- 训练流程顺序：先加载图像 → 几何数据增强（随机翻转/半身裁剪中心/随机缩放旋转/仿射变换）→ 张量化 → 归一化（ImageNet 统计量）→ 生成高斯热图标签 → Collect 收口为模型输入。
- 验证流程不包含随机增强（无翻转、无半身、无随机缩放旋转、无热图标签生成），仅保留确定性的 `TopDownAffine` + `NormalizeTensor`，确保推理可复现。
- 训练时 `Collect` 同时保留 `img` 与 `target/target_weight`（监督信号），验证时仅保留 `img`，验证阶段不需要热图真值。
- 训练与验证的 `meta_keys` 略有差异：训练多出 `'joints_3d','joints_3d_visible','flip_pairs'`，因为这些字段在数据增强时被更新，需随 `img_meta` 传递；验证无需这些增强相关字段。
- 归一化参数沿用 ImageNet 的 RGB 均值/标准差，是迁移学习常用做法。
- `flip_prob=0.5`、`rot_factor=40`、`scale_factor=0.5`、`sigma=2` 为 Simple Baseline 训练姿态估计时的典型超参。

【公式解读】
原文无公式。

【关联】
- 与 **MMCV**：通过 `MMCV` 的 `DataContainer`（用于变长数据收集与分发）以及 `mmcv.parallel.data_container` 模块耦合。
- 与 **MMCV 数据注册机制**：自定义 Transform 通过 `@PIPELINES.register_module()` 装饰器（来自 `mmpose.datasets.PIPELINES`）注册，依赖 MMCV 的注册器体系。
- 与 **MMPose 数据集层**：本文区分 "dataset" 与 "pipeline"，dataset 负责处理标注，pipeline 负责数据准备，二者解耦；自定义 Transform 在 config 中与 dataset 配置组合使用。
- 与 **模型 forward 接口**：约定 `Dataset` 返回的 dict key 与模型 `forward` 方法的参数名一致，因此 `Collect` 阶段输出的 `img` / `img_meta` / `target` / `target_weight` 字段直接对接 Simple Baseline (ResNet50) 这类 top-down 模型的输入。
- 与 **训练/验证流程**：本文给出同名 `train_pipeline` / `val_pipeline` 字段，提示它们是 config 中独立的两段列表，分别由 dataset 的 `train_pipeline` / `val_pipeline` 字段引用。
- 与 **Simple Baseline (ResNet50)**：本教程以该模型为例展示完整 pipeline，因此与同目录其他模型文档（如 HRNet config）共享同一套顶层数据流，仅具体增强参数可能不同。
- 内部链接：原文未提供任何仓库内相对链接，仅给出一个外部链接指向 MMCV 源码（见文末）。

【使用方法】
原文未提供独立的"启用命令"。配置方式即在 MMPose config 文件中以字典列表形式定义 `train_pipeline` 与 `val_pipeline`，例如：

```python
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='TopDownRandomFlip', flip_prob=0.5),
    dict(type='TopDownHalfBodyTransform', num_joints_half_body=8, prob_half_body=0.3),
    dict(type='TopDownGetRandomScaleRotation', rot_factor=40, scale_factor=0.5),
    dict(type='TopDownAffine'),
    dict(type='ToTensor'),
    dict(type='NormalizeTensor',
         mean=[0.485, 0.456, 0.406],
         std=[0.229, 0.224, 0.225]),
    dict(type='TopDownGenerateTarget', sigma=2),
    dict(type='Collect',
         keys=['img', 'target', 'target_weight'],
         meta_keys=['image_file','joints_3d','joints_3d_visible','center','scale',
                    'rotation','bbox_score','flip_pairs']),
]

val_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='TopDownAffine'),
    dict(type='ToTensor'),
    dict(type='NormalizeTensor',
         mean=[0.485, 0.456, 0.406],
         std=[0.229, 0.224, 0.225]),
    dict(type='Collect',
         keys=['img'],
         meta_keys=['image_file','center','scale','rotation','bbox_score','flip_pairs']),
]
```

自定义 Transform 的注册与挂载流程：

```python
# my_pipeline.py
from mmpose.datasets import PIPELINES

@PIPELINES.register_module()
class MyTransform:
    def __call__(self, results):
        results['dummy'] = True
        return results
```

```python
# 导入
from .my_pipeline import MyTransform
```

```python
# 在 config 的 train_pipeline 列表中按位置插入
dict(type='MyTransform'),
```

运行/启用方式（原文未涉及启动命令）；命令行启动需结合同仓库其他文档（如 config 启动方式）。
