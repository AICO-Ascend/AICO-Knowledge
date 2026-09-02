# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/config.md

# RetinaNet_for_PyTorch → Configs Tutorial 深度解读

## 【定位】
本文是 MMDetection 风格检测框架（RetinaNet_for_PyTorch 基于此生态）的**配置系统教程**，系统讲解配置文件的查看方式、运行时覆盖、模块化继承、命名约定、`train_cfg/test_cfg` 弃用迁移，以及以 Mask R-CNN(R50-FPN) 为范例的完整字段含义速查。

---

## 【技术要点】

1. **配置查看命令**：执行 `python tools/misc/print_config.py /PATH/TO/CONFIG` 即可在终端打印完整配置。

2. **运行时配置覆盖（`--cfg-options`）**：通过 `tools/train.py` 或 `tools/test.py` 提交任务时支持三类就地修改：
   - 字典链键更新，例如 `--cfg-options model.backbone.norm_eval=False` 将主干中所有 BN 切回 `train` 模式；
   - 列表内字典更新，例如 `--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam` 替换管线第 0 个算子；
   - 列表/元组整体替换，例如 `--cfg-options workflow="[(train,1),(val,1)]"`，要求**必须用引号且值内部不允许任何空白字符**。

3. **四类`_base_`原子组件**：位于 `config/_base_` 下，分别为 `dataset`、`model`、`schedule`、`default_runtime`；Faster R-CNN、Mask R-CNN、Cascade R-CNN、RPN、SSD 等方法均由这四类各取一个组合而成，称为 *primitive*。

4. **三层继承约束**：同一目录建议只保留一个 *primitive*，其余配置均继承自它，最大继承深度为 **3**；若基于现有方法修改，可通过 `_base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` 显式继承。

5. **配置文件命名模板**：
   ```
   {model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
   ```
   `{xxx}` 为必需段，`[yyy]` 为可选段。

6. **标准化训练计划（schedule）**：默认 `8x2`（8 卡 × 每卡 batch=2）；`1x`=12 epochs、`2x`=24 epochs、`20e`=20 epochs（被 cascade 类模型采用）；学习率 decay 规则详见下一节表格。

7. **弃用的 `train_cfg/test_cfg`**：原本与 `model=dict(type=...)` 并列在顶层，现已被迁移到 `model` 内部成为嵌套字段，统一配置位置。

8. **主干 norm 切换约定**：默认 `bn`，可选 `gn`/`syncbn`；`gn-head`/`gn-neck` 表示仅 head/neck 用 GN，`gn-all` 表示全模型（backbone+neck+head）均替换。

---

## 【关键机制与数据】

**数据流（覆盖路径）**：用户 CLI 参数 → `tools/train.py` 或 `tools/test.py` 解析 `--cfg-options` → 按"key 链式访问"或"列表下标"语义定位字段 → 在合并/继承解析后**就地覆盖** config dict → 最终在 mmcv 配置系统中序列化用于模型构建。

**继承链路（深度上限=3）**：
```
_base_/dataset
_base_/model
_base_/schedule
_base_/default_runtime   ←→   xxx_rcnn/*_coco.py (primitive)
                                 ↑
                          _inherits_ (max depth = 3)
                                 ↑
                            具体实验配置
```

**配置原子构成的 4 类**（原文："There are 4 basic component types under `config/_base_`, dataset, model, schedule, default_runtime"），典型组合出 Faster/Mask/Cascade R-CNN、RPN、SSD。

**学习率衰减规则**（原文所给）：
- `1x` (12 epochs)：在第 8、11 epoch 处 ×0.1
- `2x` (24 epochs)：在第 16、22 epoch 处 ×0.1
- `20e` (20 epochs)：在第 16、19 epoch 处 ×0.1

**BN 训练/评估切换语义**：`norm_eval=False` → BN 切到 `train` 模式（统计量会更新）；`norm_eval=True` → BN 保持 `eval` 模式（统计量冻结）。原文原文例子：`--cfg-options model.backbone.norm_eval=False`。

**`workflow` 字段语义**：形如 `[(train,1),(val,1)]`，元组第二个整数表示**周期数**（epochs or iters），控制 train/val 交替节奏。

---

## 【表格解读】

原文无完整 markdown 表格，但有两处结构化信息——「schedule 衰减规则」与「配置模板各字段」——可被显式表格化还原。原文中无表格标注 "原文无表格" 不准确，故补如下两表，**逐字保留**原文术语与数字。

### 表 1：训练计划 schedule 与学习率衰减位置（按原文 1:1 还原）

| Schedule | 总 epochs | 衰减点（epoch × 0.1） |
|----------|-----------|--------------------------|
| `1x` | 12 | 8 / 11 |
| `2x` | 24 | 16 / 22 |
| `20e` | 20 | 16 / 19 |

**逐行解读**：
- `1x` 行：`1x` 是 12 epochs 训练的速记，初始 LR 在 8、11 epoch 各衰减 10 倍，适用于默认周期实验。
- `2x` 行：`2x` 即 `1x` 的两倍 24 epochs，衰减点同步拉到 16、22 epoch。
- `20e` 行：`20e` 标注的 "e" 指 epochs，被 **cascade** 模型采用，20 epochs 下在 16 与 19 epoch 处衰减。

### 表 2：配置名模板字段表（按原文字段说明 1:1 还原）

| 段位 | 是否必需 | 可选取值示例 | 备注 |
|------|----------|--------------|------|
| `{model}` | ✅ | `faster_rcnn`、`mask_rcnn` 等 | 模型类别 |
| `[model setting]` | ❌ | `without_semantic`（用于 `htc`）、`moment`（用于 `reppoints`） | 某些模型的特殊配置 |
| `{backbone}` | ✅ | `r50`（ResNet-50）、`x101`（ResNeXt-101） | 主干类型 |
| `{neck}` | ✅ | `fpn`、`pafpn`、`nasfpn`、`c4` | 颈部结构 |
| `[norm_setting]` | ❌ | `bn`（默认）、`gn`、`syncbn`、`gn-head`、`gn-neck`、`gn-all` | 归一化层位置与类型 |
| `[misc]` | ❌ | `dconv`、`gcb`、`attention`、`albu`、`mstrain` | 杂项插件 |
| `[gpu x batch_per_gpu]` | ❌ | `8x2`（默认） | GPU 数 × 每 GPU batch |
| `{schedule}` | ✅ | `1x`、`2x`、`20e` | 训练计划（见表 1） |
| `{dataset}` | ✅ | `coco`、`cityscapes`、`voc_0712`、`wider_face` | 数据集 |

**逐行解读**：模板 `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}` 中，所有大括号 `{}` 必须出现（如 `faster_rcnn_r50_fpn_1x_coco`），而方括号 `[]` 内容缺省时省略（如 `mask_rcnn_r50_fpn_8x2_1x_coco` 未指定 `[misc]`、`[norm_setting]` 即隐含默认 BN）；`[norm_setting]` 还可三态化地限定 GN 作用范围——仅 head、仅 neck 或全模型。

---

## 【公式解读】

原文无标准数学公式，但含一个**配置命名模板**（伪代码模板形式）：

```
{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
```

**符号含义与作用**：
- `{model}`：检测器类型，如 `faster_rcnn`、`mask_rcnn`，决定模型主体结构。
- `[model setting]`：模型专属开关（可缺省），如 `without_semantic` 关闭 HTC 的语义分支、`moment` 启用 RepPoints 的矩预测。
- `{backbone}`：主干网络代号，如 `r50`、`x101`。
- `{neck}`：neck 模块代号，如 `fpn`、`pafpn`、`nasfpn`、`c4`。
- `[norm setting]`：归一化规则（可缺省，缺省即为 `bn`），可选 `gn`、`syncbn`、`gn-head`、`gn-neck`、`gn-all`。
- `[misc]`：杂项插件（可缺省），如 `dconv`（可变形卷积）、`gcb`（全局上下文块）、`attention`、`albu`（albumentations 增强）、`mstrain`（多尺度训练）。
- `[gpu x batch_per_gpu]`：硬件资源规格（可缺省），如 `8x2`。
- `{schedule}`：训练计划，必需，见表 1。
- `{dataset}`：数据集名称，必需。

此外，原文 `workflow` 字段的语法形如元组列表（可视为程序级公式）：

```
workflow = [(train, k), (val, k), ...]
```
其中第二项 `k`（整数）为该阶段持续的 epoch（或 iter）周期数。

---

## 【关联】

- 与 **mmcv** 强绑定：原文指向 [mmcv config 文档](https://mmcv.readthedocs.io/en/latest/utils.html#config) 作为底层配置机制说明；`print_config.py` 与 `Config` 解析、合并、继承逻辑均由 mmcv 提供。
- 与 **`tools/train.py` / `tools/test.py`** 关联：CLI 入口通过 `--cfg-options` 调用本文所述三类覆盖语义。
- 与 **`config/_base_` 四类组件**关联：`dataset`、`model`、`schedule`、`default_runtime` 是所有 *primitive* 配置的拼装件，本文所有继承关系围绕这四者展开。
- 与 **MMDetection 模型库**关联：范例 Mask R-CNN 引用大量 mmdet 模块源码链接，包括 `mmdet/models/backbones/resnet.py`（主干）、`mmdet/models/necks/fpn.py`（neck）、`mmdet/models/dense_heads/rpn_head.py`（RPN 头）、`mmdet/core/anchor/anchor_generator.py`（anchor 生成器）、`mmdet/core/bbox/coder/delta_xywh_bbox_coder.py`（box 编解码器）等。
- 与 **预训练权重源 `torchvision://resnet50`** 关联：范例中通过该 URL 加载主干预训练。
- **内部链接**：原文标注 (无)，故无可用内部文档跳转；外部链接为 mmcv 官方文档。

---

## 【使用方法】

1. **查看完整配置**（原文命令）：
   ```bash
   python tools/misc/print_config.py /PATH/TO/CONFIG
   ```

2. **运行时覆盖配置**（提交训练/测试任务时附 `--cfg-options`）：
   ```bash
   python tools/train.py /PATH/TO/CONFIG --cfg-options model.backbone.norm_eval=False
   python tools/train.py /PATH/TO/CONFIG --cfg-options data.train.pipeline.0.type=LoadImageFromWebcam
   python tools/train.py /PATH/TO/CONFIG --cfg-options workflow="[(train,1),(val,1)]"
   ```

3. **新增配置约定**：
   - 完全新方法时在 `configs/` 下建立 `xxx_rcnn` 文件夹；
   - 在已有方法上修改时，先 `_base_ = ../<method>/<primitive>.py`，再覆写需变字段；
   - 同目录仅保留一个 *primitive*，最大继承深度 = 3。

4. **命名规范**：遵循 `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}`，例如 `mask_rcnn_r50_fpn_gn-all_8x2_1x_coco.py`。

5. **`train_cfg/test_cfg` 迁移**：将原本顶层并列的 `train_cfg=dict(...)`、`test_cfg=dict(...)` 内嵌至 `model=dict(type=..., train_cfg=dict(...), test_cfg=dict(...))` 之中，避免弃用警告。

6. **schedule 选用**：`1x` 跑 12 epochs，`2x` 跑 24 epochs，cascade 系列使用 `20e`（20 epochs），各自遵循表 1 中的 LR 衰减节点。
