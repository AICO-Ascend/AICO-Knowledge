# 教程 1: 学习配置文件

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/config.md

# 一体化深度解读：BEVDet/mmdet3d 配置文件教程

---

## 【定位】

本文档系统介绍 mmdet3d 框架（含 BEVDet）配置文件的**结构、命名规范、继承机制及编写规范**，解决"如何组织/继承/检查/命名配置文件"这一基础工程问题，使研究者能够基于已有方法快速派生新实验配置。

---

## 【技术要点】

1. **四大基本组件**：在 `config/_base_/` 下分四类——`dataset`（数据集）、`model`（模型）、`schedule`（训练策略）、`default runtime`（运行默认设置）；每类选一个组件组合即可构建 SECOND、PointPillars、PartA2、VoteNet 等方法。
2. **原始配置（primitive）与继承深度限制**：同一文件夹下推荐**仅一个**原始配置，其他配置均继承之，**最大继承深度为 3**。
3. **配置文件检查命令**：`python tools/misc/print_config.py /PATH/TO/CONFIG`；可通过附加 `--options xxx.yyy=zzz` 临时覆盖字段查看更新结果。
4. **配置文件命名模板（强制 + 可选字段）**：
   `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}`，其中 `{xxx}` 必填、`[yyy]` 可选。
5. **训练 schedule 的固定约定**：`1x`=12 轮，`2x`=24 轮，`20e`=20 轮（用于级联模型）；`1x`/`2x` 在第 8/16 与 11/22 轮将初始学习率衰减 10 倍，`20e` 在第 16、19 轮衰减 10 倍；默认 batch 设定为 `4x8`。
6. **弃用顶层 `train_cfg` / `test_cfg`**：遵循 MMDetection 规范，必须迁移至 `model` 字典内的 `train_cfg=dict(...)`、`test_cfg=dict(...)` 子字段。
7. **归一化（norm setting）约定**：默认 `bn`；可选 `gn`、`sbn`，位置变体 `gn-head`/`gn-neck`/`gn-all` 分别表示仅作用于头部、颈部或全模型。

---

## 【关键机制与数据】

- **配置继承工作流**（原文）：在已有方法基础上派生新实验时，先在新建配置顶部写 `_base_ = ../pointpillars/hv_pointpillars_fpn_sbn-all_4x8_2x_nus-3d.py`，再覆写必要字段；若属于**与现有方法均不共享结构**的全新方法，则在 `configs/` 下新建 `xxx_rcnn/` 文件夹。
- **检查与覆写**（原文）：`print_config.py` 可解析最终配置；`--options` 形如 `xxx.yyy=zzz` 的点号路径语法用于在运行时层级覆盖任意字段。
- **数据流**（原文）：原始配置 → 被继承配置 → 最终生效配置；最终通过 print_config 校验。
- **VoteNet 配置内嵌的超参数数据**（原文，原文给出但**示例在文档中途中断**，仅可见至 `dict(type='IndoorFl...`）：
  - `backbone.in_channels=4`、`num_points=(2048, 1024, 512, 256)`、`radius=(0.2, 0.4, 0.8, 1.2)`、`num_samples=(64, 32, 16, 16)`、`sa_channels` 与 `fp_channels` 四/两组元组。
  - `bbox_head.num_classes=18`，`PartialBinBasedBBoxCoder` 的 `num_sizes=18`、`num_dir_bins=1`、`with_rot=False`，以及 18 类 `mean_sizes` 列表（原文逐项给出，未篡改）。
  - 投票模块 `vote_per_seed=1`、`gt_per_seed=3`、`conv_channels=(256, 256)`；聚合 SA 模块 `num_point=256`、`radius=0.3`、`num_sample=16`、`mlp_channels=[256, 128, 128, 128]`。
  - 训练超参：`pos_distance_thr=0.3`、`neg_distance_thr=0.6`、`sample_mod='vote'`；测试超参：`sample_mod='seed'`、`nms_thr=0.25`、`score_thr=0.8`、`per_class_proposal=False`。
  - 数据：`dataset_type='ScanNetDataset'`、`data_root='./data/scannet/'`、`class_names` 18 项；`valid_cat_ids=(3,4,5,6,7,8,9,10,11,12,14,16,24,28,33,34,36,39)`、`max_cat_id=40`、`num_points=40000`。

> 注：原文 VoteNet 示例**在 `'IndoorFl` 处被截断**，后续流程未给出，本文不做臆造。

---

## 【表格解读】

### 表 1：配置文件命名字段说明（**逐字还原**自原文命名模板 + 字段列表）

| 字段（模板标记） | 必/选 | 含义 / 取值 | 原文示例 |
|---|---|---|---|
| `{model}` | 必填 | 模型种类 | `hv_pointpillars`、`VoteNet` |
| `[model setting]` | 可选 | 某些模型的特殊设定 | （原文未给出具体示例） |
| `{backbone}` | 必填 | 主干网络种类 | `regnet-400mf`、`regnet-1.6gf` |
| `{neck}` | 必填 | 模型颈部的种类 | `fpn`、`secfpn` |
| `[norm_setting]` | 可选 | 归一化设置，默认 `bn` | `gn`、`sbn`、`gn-head`、`gn-neck`、`gn-all` |
| `[misc]` | 可选 | 各种设置/插件 | `strong-aug` |
| `[batch_per_gpu x gpu]` | 可选 | 每 GPU 样本数 × GPU 数 | 默认 `4x8` |
| `{schedule}` | 必填 | 训练方案 | `1x`（12 轮）、`2x`（24 轮）、`20e`（20 轮，级联模型用） |
| `{dataset}` | 必填 | 数据集 | `nus-3d`、`kitti-3d`、`lyft-3d`、`scannet-3d`、`sunrgbd-3d`、`kitti-3d-3class`、`kitti-3d-car` |

**逐行解读**：
- 模板的 `[]` 与 `{}` 之别是命名规范的"硬契约"，建议贡献者严格遵循以维持一致性。
- `norm_setting` 的位置变体（`-head`/`-neck`/`-all`）控制 BN 在网络中的扩散范围，针对小 batch 显存受限场景有实际工程意义。
- `schedule` 字段暗含学习率衰减节奏（见【技术要点】第 5 条），命名本身即是 schedule 配置的索引。
- `dataset` 字段的 `-3class`、`-car` 后缀说明**同一数据集的多设定支持**，通过类目数量在文件名层面消歧。

### 表 2：schedule 与学习率衰减轮次对照（**逐字还原**自原文）

| schedule | 总轮次 | 学习率衰减 1（×0.1） | 学习率衰减 2（×0.1） | 适用场景 |
|---|---|---|---|---|
| `1x` | 12 | 第 8 轮 | 第 11 轮 | 通用 |
| `2x` | 24 | 第 16 轮 | 第 22 轮 | 通用 |
| `20e` | 20 | 第 16 轮 | 第 19 轮 | 级联模型 |

**解读**：`e` 后缀用于级联检测器（cascade），其轮次安排与 `1x`/`2x` 不同（衰减更靠后）；`1x`/`2x` 的衰减恰好落在"剩余 1/3 起点"和"末尾前 1 轮"，符合典型 2 段式衰减实践。

---

## 【公式解读】

**原文无数学公式。**

文档中存在一个**配置命名的伪代码模板**（原文逐字保留）：

```
{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
```

其中：
- `{xxx}` —— 必填字段（model、backbone、neck、schedule、dataset）；
- `[yyy]` —— 可选字段（model setting、norm setting、misc、batch x gpu）；
- 字段间以**下划线 `_`** 分隔。

该"公式"等价于"正则表达式的命名规约"，保证 cfg 文件名可被一致解析、对照与索引。

---

## 【关联】

- **与 MMCV 的关系**：原文明确"更多细节请参考 MMCV 文档"（https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html ），表明本框架的配置系统是 MMCV Config 体系的**领域特化**实现。
- **与 MMDetection 的关系**：原文"遵循 MMDetection 的做法"弃用顶层 `train_cfg`/`test_cfg`，说明该工程实践源自 2D 检测生态，向 3D 迁移。
- **与上游模型库的关系**：构建示例列举了 SECOND、PointPillars、PartA2、VoteNet 四个方法，说明配置文件机制需能同时容纳**体素类方法（SECOND、PointPillars、PartA2）**与**点集方法（VoteNet）**——这恰好对应文档给出的 VoteNet 完整示例（PointNet2SASSG + VoteHead）。
- **与数据集生态的关联**：命名模板中枚举 `nus-3d`/`kitti-3d`/`lyft-3d`/`scannet-3d`/`sunrgbd-3d`，分别对应**室外多类别**（nuScenes）、**室外车类**（KITTI）、**室外大规模**（Lyft）、**室内场景**（ScanNet）、**室内 RGB-D**（SUN-RGBD）五大数据域，体现配置的跨域复用能力。
- **下游检查工具**：`tools/misc/print_config.py` 作为配套工具实现"配置→最终字典"的物化，与 `_base_` 继承机制形成闭环。

---

## 【使用方法】

**1. 检查最终配置**（原文命令）：
```
python tools/misc/print_config.py /PATH/TO/CONFIG
```
可输出经继承/字段覆写解析后的**完整配置字典**，便于排查继承链中的字段覆盖是否符合预期。

**2. 临时覆盖字段查看**（原文）：
```
python tools/misc/print_config.py /PATH/TO/CONFIG --options xxx.yyy=zzz
```
点号路径语法支持层级覆写，可视化"如果改了这个字段会变成什么样"，无需修改磁盘文件。

**3. 派生新配置**（原文流程）：
- **基于现有方法**：新建 cfg，顶部写 `_base_ = ../<method>/<primitive_cfg>.py`，再覆写需修改字段。
- **全新结构方法**：在 `configs/` 下创建 `xxx_rcnn/` 文件夹，独立组织 `_base_` 四组件。
- **继承深度**：任意 cfg 的 `_base_` 链不超过 **3 层**（含自身）。

**4. train_cfg / test_cfg 迁移**（原文）：
- 弃用形式（顶层）：
  ```python
  model = dict(type=..., ...)
  train_cfg = dict(...)
  test_cfg = dict(...)
  ```
- 推荐形式（嵌入 model）：
  ```python
  model = dict(
      type=...,
      ...,
      train_cfg=dict(...),
      test_cfg=dict(...),
  )
  ```

**5. 命名规范遵守**（原文）：新贡献的配置须严格遵循 `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}` 模板，确保 `configs/` 目录的可索引性。

**原文未涉及**：CI 校验配置合法性的脚本、环境变量驱动的配置注入、动态配置生成等更高级用法——本文档仅覆盖"阅读与编写"层面。
