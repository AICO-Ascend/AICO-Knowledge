# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/config.md

# 一体化深度解读:Tutorial 1: Learn about Configs

---

## 【定位】

本教程文档系统性地介绍了 MMDetection3D(包括 BEVDet)配置系统的模块化与继承式设计理念,涵盖配置文件结构、命名规范、废弃字段迁移以及典型模型(VoteNet)的完整配置示例,目的是让用户能够规范地编写、复用、派生配置以支持多种 3D 检测实验。

---

## 【技术要点】

1. **配置系统设计哲学**:采用"模块化 + 继承式"架构,所有配置由 `config/_base_` 下的 4 类基础组件组合而成——`dataset`、`model`、`schedule`、`default_runtime`,典型可由各一份基础组件构成的方法包括 SECOND、PointPillars、PartA2、VoteNet 等。

2. **继承层级约束**:同一文件夹下推荐仅有 **一个 _primitive_ (原始)配置**,其余配置从该 primitive 继承,因此最大继承深度被限制为 **3 层**(This is because the maximum of inheritance level is 3)。

3. **配置命名规范(必选+可选字段)**:
   `{model}_[model setting]_{backbone}_[neck]_[norm setting]_[misc]_[batch_per_gpu x gpu]_{schedule}_{dataset}`
   `{xxx}` 为必选,`[yyy]` 为可选。例如 `_base_ = ../pointpillars/hv_pointpillars_fpn_sbn-all_4x8_2x_nus-3d.py`。

4. **训练计划(schedule)与学习率衰减规则**:
   - `1x` = 12 epochs,`2x` = 24 epochs,`20e` = 20 epochs(cascade 模型专用)。
   - `1x`/`2x` 时初始学习率在 **第 8/16 epoch 与第 11/22 epoch** 处衰减 10 倍;
   - `20e` 时初始学习率在 **第 16 epoch 与第 19 epoch** 处衰减 10 倍。

5. **归一化设置选项**:`bn` 为默认(Batch Normalization),可选 `gn` (Group Normalization)、`sbn` (Synchronized Batch Normalization);粒度标识如 `gn-head`/`gn-neck` 表示仅在 head/neck 使用 GN,`gn-all` 则在 backbone+neck+head 全程使用。

6. **train_cfg / test_cfg 字段迁移**:遵循 MMDetection 的规范,配置文件顶层的 `train_cfg=...` 与 `test_cfg=...` 已**废弃**,需内联到 `model` 字典内部的 `train_cfg=dict(...)` 与 `test_cfg=dict(...)`。

7. **配置检视与覆盖命令**:
   - 打印完整配置:`python tools/misc/print_config.py /PATH/TO/CONFIG`
   - 临时覆盖字段:`--options xxx.yyy=zzz`

---

## 【关键机制与数据】

### 工作原理与数据流

**配置加载与继承流程(原文叙述)**:用户编写的配置文件通过 `_base_` 字段引用父配置,加载器会递归地合并父配置字典并被当前文件覆写。该机制允许开发者只需在 `_base_` 上"派生 + 修改必要字段"即可构造新实验(原文:user may first inherit the basic PointPillars structure by specifying `_base_ = ../pointpillars/hv_pointpillars_fpn_sbn-all_4x8_2x_nus-3d.py`, then modify the necessary fields)。

**新方法落地路径(原文)**:若所构建方法与任何已有方法结构都不共享,推荐在 `configs` 下创建形如 `xxx_rcnn` 的文件夹。

**VoteNet 配置文件示例中的关键超参与数据(原文逐字段)**:

| 子模块 | 字段 | 值(原文) |
|---|---|---|
| detector type | `type` | `'VoteNet'` |
| backbone type | `type` | `'PointNet2SASSG'` |
| backbone in_channels | `in_channels` | `4`(点云输入通道) |
| backbone num_points | `num_points` | `(2048, 1024, 512, 256)`(每个 SA 模块采样点数) |
| backbone radius | `radius` | `(0.2, 0.4, 0.8, 1.2)`(各 SA 层搜索半径) |
| backbone num_samples | `num_samples` | `(64, 32, 16, 16)` |
| backbone sa_channels | `sa_channels` | `((64,64,128),(128,128,256),(128,128,256),(128,128,256))` |
| backbone fp_channels | `fp_channels` | `((256,256),(256,256))` |
| backbone norm_cfg | `norm_cfg` | `dict(type='BN2d')` |
| SA module 池化方式 | `pool_mod` | `'max'`(可选 `'max'` 或 `'avg'`) |
| SA 是否使用 xyz | `use_xyz` | `True` |
| SA 是否归一化 xyz | `normalize_xyz` | `True` |
| head type | `type` | `'VoteHead'` |
| head num_classes | `num_classes` | `18`(分类数) |
| bbox_coder type | `type` | `'PartialBinBasedBBoxCoder'` |
| bbox_coder num_sizes | `num_sizes` | `18`(尺寸聚类数) |
| bbox_coder num_dir_bins | `num_dir_bins` | `1` |
| bbox_coder with_rot | `with_rot` | `False` |
| mean_sizes | (18 行,3 维) | 每类平均尺寸,与 class_names 顺序一致(原文给出 18 个具体三维数值) |
| vote_module in_channels | `in_channels` | `256` |
| vote_module vote_per_seed | `vote_per_seed` | `1`(每个种子生成 1 个 vote) |
| vote_module gt_per_seed | `gt_per_seed` | `3` |
| vote_module conv_channels | `conv_channels` | `(256, 256)` |
| vote_module conv_cfg | `conv_cfg` | `dict(type='Conv1d')` |
| vote_module norm_cfg | `norm_cfg` | `dict(type='BN1d')` |
| vote_module norm_feats | `norm_feats` | `True` |
| vote_loss type | `type` | `'ChamferDistance'` |
| vote_loss mode | `mode` | `'l1'` |
| vote_loss reduction | `reduction` | `'none'` |
| vote_loss loss_dst_weight | `loss_dst_weight` | `10.0` |
| vote_aggregation type | `type` | `'PointSAModule'` |
| vote_aggregation num_point | `num_point` | `256` |
| vote_aggregation radius | `radius` | `0.3` |
| vote_aggregation num_sample | `num_sample` | `16` |
| vote_aggregation mlp_channels | `mlp_channels` | `[256, 128, 128, 128]` |
| feat_channels | `feat_channels` | `(128, 128)` |
| objectness_loss type | `type` | `'CrossEntropyLoss'` |
| objectness_loss class_weight | `class_weight` | `[0.2, 0.8]` |
| objectness_loss reduction | `reduction` | `'sum'` |
| objectness_loss loss_weight | `loss_weight` | `5.0` |
| center_loss type | `type` | `'ChamferDistance'` |
| center_loss mode | `mode` | `'l2'` |

> 原文示例在 `center_loss=` 行被截断,后续字段(原文未给出)不再赘述。

---

## 【表格解读】

**原文无表格**。

原文以 Python 配置字典(代码块)的形式给出示例,未呈现任何 markdown/HTML 表格。我已在"关键机制与数据"一节以表格形式**逐字**还原 VoteNet 示例的配置字段、值与对应注释,便于按字段查阅。

---

## 【公式解读】

**原文无公式**。

原文未出现 LaTeX 或伪代码公式。可被视作"公式/规则"的是命名模板字符串(见下),其更像一种格式化语法而非数学公式:

```
{model}_[model setting]_{backbone}_[neck]_[norm setting]_[misc]_[batch_per_gpu x gpu]_{schedule}_{dataset}
```

符号含义说明:
- `{model}`:模型族名,必选,如 `hv_pointpillars`、`VoteNet`。
- `[model setting]`:模型特定设置,可选。
- `{backbone}`:骨干网络,必选,如 `regnet-400mf`、`regnet-1.6gf`。
- `[neck]`:颈部结构,可选,如 `fpn`、`secfpn`。
- `[norm_setting]`:归一化配置,可选,默认 `bn`,可取 `gn`、`sbn`,粒度后缀如 `gn-head`/`gn-neck`/`gn-all`。
- `[misc]`:杂项/插件,可选,如 `strong-aug`。
- `[batch_per_gpu x gpu]`:每 GPU 批大小 × GPU 数,可选,默认 `4x8`。
- `{schedule}`:训练计划,必选,`1x`(=12 epochs)、`2x`(=24 epochs)、`20e`(=20 epochs)。
- `{dataset}`:数据集,必选,如 `nus-3d`、`kitti-3d`、`lyft-3d`、`scannet-3d`、`sunrgbd-3d`,多设置时带类数后缀,如 `kitti-3d-3class`、`kitti-3d-car`。

---

## 【关联】

由于原文未提供文末内部链接(用户已标注"内部链接: (无)"),可识别的关联主要来自文档自身的引用与代码字段:

1. **与 mmcv 的关系**:配置加载、字段合并、`_base_` 解析等底层机制由 mmcv 提供,原文明确"Please refer to mmcv (https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html) for detailed documentation",因此本指南是 mmcv Config 文档在 3D 检测场景下的上层封装说明。

2. **与 MMDetection 的关系**:`train_cfg` / `test_cfg` 字段内联到 `model` 的迁移方式直接沿用 MMDetection 的做法(原文:Following MMDetection, the `train_cfg` and `test_cfg` are deprecated in config file)。

3. **与下游模块注册表的关联**:配置中的 `type='VoteNet'`、`type='PointNet2SASSG'`、`type='VoteHead'`、`type='PartialBinBasedBBoxCoder'`、`type='PointSAModule'`、`type='ChamferDistance'`、`type='CrossEntropyLoss'`、`type='BN1d'`、`type='BN2d'`、`type='Conv1d'` 等字符串均指向 `mmdet3d.models.detectors`、`mmdet3d.models.backbones`、`mmdet3d.models.dense_heads`、`mmdet3d.core.bbox.coders`、`mmdet3d.models.model_utils` 中的具体类——配置系统的字段名直接对应 mmdet3d 的模块注册路径。

4. **与方法间复用的关联**:文档建议"贡献者从已有方法继承"以保证一致性(原文:we recommend contributors to inherit from exiting methods),这意味着同一 `_base_` 链(例如 `hv_pointpillars_*`)下的所有变体共享模型骨架,仅在数据增强、head、schedule 等局部字段上做差异化。

---

## 【使用方法】

### 配置检视与运行时覆盖(原文给出)
- 打印完整配置:
  ```
  python tools/misc/print_config.py /PATH/TO/CONFIG
  ```
- 临时覆盖字段查看更新后的配置:
  ```
  --options xxx.yyy=zzz
  ```

### 创建新配置的推荐流程(原文给出)
1. **基于现有方法派生**:在目标方法的 `_base_` 配置上写 `_base_ = ../<method>/<primitive>.py`,然后仅覆写需要修改的字段(原文示例:`_base_ = ../pointpillars/hv_pointpillars_fpn_sbn-all_4x8_2x_nus-3d.py`)。
2. **全新方法**:在 `configs/` 下创建 `xxx_rcnn` 文件夹并自上而下构建 primitive。
3. **单一 primitive 约束**:同一目录下保持 **只有 1 个 primitive**,其余配置均继承之,继承深度 **不超过 3 层**。

### 配置命名规范(原文给出)
按 `{model}_[model setting]_{backbone}_[neck]_[norm setting]_[misc]_[batch_per_gpu x gpu]_{schedule}_{dataset}` 命名,`{xxx}` 必选、`[yyy]` 可选。

### 训练计划数值(原文给出)
- `1x` → 12 epochs,`2x` → 24 epochs,`20e` → 20 epochs。
- `1x`/`2x` 学习率衰减点:**第 8/16 与第 11/22 epoch**(×0.1)。
- `20e` 学习率衰减点:**第 16 与第 19 epoch**(×0.1)。

### train_cfg/test_cfg 迁移(原文给出)
将顶层
```python
# deprecated
model = dict(type=..., ...)
train_cfg=dict(...)
test_cfg=dict(...)
```
迁移为
```python
# recommended
model = dict(
    type=..., ...,
    train_cfg=dict(...),
    test_cfg=dict(...),
)
```

### 典型模型可由 4 个 _base_ 直接组合而成(原文列出)
- `SECOND`、`PointPillars`、`PartA2`、`VoteNet` 等,各取 `dataset` + `model` + `schedule` + `default_runtime` 一份即可拼装。

> 原文未涉及具体训练启动命令(如 `tools/train.py` 的调用形式)、数据集准备步骤、配置文件校验 CLI、debug/dry-run 选项等,这些内容应在其他 tutorial 中另行查阅。
