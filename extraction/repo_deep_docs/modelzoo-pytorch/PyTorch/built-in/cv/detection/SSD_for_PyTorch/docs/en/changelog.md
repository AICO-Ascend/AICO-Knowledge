# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/changelog.md

# 文档深度解读：MMDetection v2.24.0 / v2.25.0 Changelog

---

## 【定位】

这篇文档是 MMDetection 目标检测框架在 v2.24.0（2022/4/26）和 v2.25.0（2022/5/31）两个版本周期内的**变更日志**，记录了框架在模型支持（新算法接入）、不兼容变更（配置文件语义重定义）、新特性（增强工具/数据增强）、Bug 修复、性能优化和文档完善等维度的演进轨迹，为用户升级版本与使用新能力提供权威参考。

---

## 【技术要点】

1. **新模型与算法支持**：v2.25.0 接入 ConvNeXt（#7281）、DDOD（#7279）、SOLOv2（#7441），并新增 Mask2Former 用于**实例分割**（#7571、#8032）。
2. **Mask2Former 配置文件语义重命名（破坏性变更，#7571）**：v2.25.0 之前 `mask2former_xxx_coco.py` 代表**全景分割**；v2.25.0 之后改为代表**实例分割**，新增 `mask2former_xxx_coco-panoptic.py` 专门承载全景分割配置。
3. **专用 WandbLogger Hook（#7459）**：通过 `MMDetWandbHook` 将训练指标、checkpoint 与元数据推送到 W&B，可通过 `cfg.log_config.hooks` 配置，参数包括 `project`、`interval`、`log_checkpoint`、`log_checkpoint_metadata`、`num_eval_images`。
4. **AvoidOOM / AvoidCUDAOOM 抗显存溢出机制（#7434、#8091）**：三段式降级策略——首先调用 `torch.cuda.empty_cache()` 重试；失败后转为 FP16 重试；仍失败则将输入从 GPU 拷贝到 CPU 继续计算。提供 `retry_if_cuda_oom` 函数包装与装饰器两种调用形式。
5. **Simple Copy-Paste 数据增强（#7501）**：基于论文 arXiv:2012.07177，为实例分割引入 Copy-Paste 增强，示例配置位于 `configs/simple_copy_paste/mask_rcnn_r50_fpn_syncbn-all_rpn-2conv_ssj_scp_32x2_270k_coco.py`。
6. **训练超参自动化**：支持 Class Aware Sampler（`num_sample_class=1`，#7436）、按 GPU 数与每 GPU 样本数自动缩放学习率（`auto_scale_lr = dict(enable=True, base_batch_size=N)`，#7482）、Dataloader 参数精细化（#7668）、`MemoryProfilerHook` 显存剖析（`interval=50`，#7560）、Mosaic 增加概率参数（#7371）、Resize 指定插值模式（#7585）。

---

## 【关键机制与数据】

### 工作原理

**① WandbLogger Hook 注册流程**（原文）：
通过 `cfg.log_config.hooks` 列表注入 `MMDetWandbHook`，由 MMDet 的日志 hook 调度机制在训练 step 中按 `interval` 周期触发上报。

**② AvoidCUDAOOM 三级降级**（原文）：
1. 调用 `torch.cuda.empty_cache()` 释放缓存后重试；
2. 仍失败则将输入 dtype 转换为 FP16 重试；
3. 仍失败则把输入从 GPU 迁移到 CPU 继续计算。

**③ Auto-scaling LR 公式**（原文伪代码）：
```
auto_scale_lr = dict(enable=True, base_batch_size=N)
```
其中 `N = samples_per_gpu × gpu_number`（当前 config 推导学习率所用的全局 batch size），默认 `enable=False` 以保持向后兼容；可通过命令行加 `--auto-scale-lr` 临时开启。

**④ Dataloader 配置拆分**（原文对比）：
v2.23.0 中 `samples_per_gpu`、`workers_per_gpu` 写在顶层 `data` 字典，仅作用于训练集；v2.24.0 拆分为 `train_dataloader / val_dataloader / test_dataloader`，可独立设置推理阶段的 batch size 与 worker 数。

### 性能与效率数据

**原文：`analyze_result.py` 提速**（#7891）：
> "The evaluation time is speedup by **10 ~ 15 times** and only tasks **10 ~ 15 minutes** now."

即结果分析脚本的评估时间提速 **10–15 倍**，从数小时级别缩短至 **10–15 分钟**。

**原文：Class Aware Sampler 配置示例**（#7436）：
```
data=dict(train_dataloader=dict(class_aware_sampler=dict(num_sample_class=1))))
```

**原文：MemoryProfilerHook 配置示例**（#7560）：
```
custom_hooks = [dict(type='MemoryProfilerHook', interval=50)]
```

---

## 【表格解读】

### 表格 1：Mask2Former 配置文件语义重命名（破坏性变更）

| before v2.25.0 | after v2.25.0 |
|---|---|
| `mask2former_xxx_coco.py` represents config files for **panoptic segmentation**. | `mask2former_xxx_coco.py` represents config files for **instance segmentation**. <br> `mask2former_xxx_coco-panoptic.py` represents config files for **panoptic segmentation**. |

**逐行解读**：
- v2.25.0 之前，文件名 `mask2former_xxx_coco.py` 隐含语义为**全景分割（panoptic segmentation）**任务。
- v2.25.0 之后，文件名主体 `mask2former_xxx_coco.py` 的语义变更为**实例分割（instance segmentation）**，是破坏性变更。
- 全景分割配置被分离到带 `-panoptic` 后缀的独立文件 `mask2former_xxx_coco-panoptic.py` 中。
- 升级影响：用户必须检查自己的训练脚本与 config 路径，避免加载错任务的权重或评估指标。

---

### 表格 2：Dataloader 配置风格 v2.23.0 vs v2.24.0

| v2.23.0 | v2.24.0 |
|---|---|
| ```python\ndata = dict(\n    samples_per_gpu=64, workers_per_gpu=4,\n    train=dict(type='xxx', ...),\n    val=dict(type='xxx', samples_per_gpu=4, ...),\n    test=dict(type='xxx', ...),\n)\n``` | ```python\n# A recommended config that is clear\ndata = dict(\n    train=dict(type='xxx', ...),\n    val=dict(type='xxx', ...),\n    test=dict(type='xxx', ...),\n    # Use different batch size during inference.\n    train_dataloader=dict(samples_per_gpu=64, workers_per_gpu=4),\n    val_dataloader=dict(samples_per_gpu=8, workers_per_gpu=2),\n    test_dataloader=dict(samples_per_gpu=8, workers_per_gpu=2),\n)\n\n# Old style still works but allows to set more arguments about data loaders\ndata = dict(\n    samples_per_gpu=64,  # only works for train_dataloader\n    workers_per_gpu=4,  # only works for train_dataloader\n    train=dict(type='xxx', ...),\n    val=dict(type='xxx', ...),\n    test=dict(type='xxx', ...),\n    # Use different batch size during inference.\n    val_dataloader=dict(samples_per_gpu=8, workers_per_gpu=2),\n    test_dataloader=dict(samples_per_gpu=8, workers_per_gpu=2),\n)\n``` |

**逐行解读**：
- **左栏（v2.23.0 旧式）**：`samples_per_gpu` 与 `workers_per_gpu` 写在 `data` 顶层，仅对训练生效；验证/测试只能通过各自字典内联覆盖（如 `val=dict(..., samples_per_gpu=4, ...)`），语义不直观且能力受限。
- **右栏（v2.24.0 新式推荐）**：将采样参数抽离到独立的 `train_dataloader / val_dataloader / test_dataloader` 键，可针对每个阶段独立设置 batch size 与 worker 数量，结构更清晰。
- **右栏下半部分（兼容写法）**：保留旧式顶层 `samples_per_gpu/workers_per_gpu` 写法以兼容旧 config，但官方明确其**仅作用于 `train_dataloader`**，验证/测试仍需在各自的 `*_dataloader` 字典内单独声明。
- **变更影响**：用户升级时无需立即改写 config（兼容兜底），但新写法是官方推荐路径，可避免隐式默认行为带来的 batch size 错误。

---

## 【公式解读】

**原文无公式**。

注：原文中出现的仅为 Python 配置字典（伪配置 DSL），并非数学公式或算法伪代码；其中 `auto_scale_lr = dict(enable=True, base_batch_size=N)` 与 `N = samples_per_gpu × gpu_number` 的语义已在【关键机制与数据】节解读。

---

## 【关联】

本 Changelog 是 MMDetection 框架演进的入口，与以下内部特性/模块形成上下游依赖：

- **ConvNeXt** → 链接至 `configs/convnext`：新骨干网络支持，可用于多种检测/分割 head 替换 ResNet/Swin。
- **DDOD** → 链接至 `configs/ddod`：新颖检测器（arXiv:2107.02963），依赖通用检测流水线。
- **SOLOv2** → 链接至 `configs/solov2`：单阶段实例分割算法（arXiv:2003.10152），与 Mask2Former 实例分割能力互补。
- **Mask2Former** → 链接至 `configs/mask2former`：统一分割框架，本次新增实例分割支持，并重命名配置文件（v2.25.0 之后 `xxx_coco.py` 改为实例分割，全景分割用 `xxx_coco-panoptic.py`）。
- **Mask2Former 实例分割预训练模型** → 链接至 `configs/mask2former`（原文末尾处截断）：v2.24.0 末尾提到"Release pre-trained models of Mask2Former"，与新增能力配套发布。
- **Simple Copy-Paste** → 链接至 `configs/simple_copy_paste/mask_rcnn_r50_fpn_syncbn-all_rpn-2conv_ssj_scp_32x2_270k_coco.py`：以 Mask R-CNN 为载体的 Copy-Paste 数据增强示例配置，作为数据增强层接入训练流程。
- **`MMDetWandbHook`** → 链接 `docs/en/tutorials/useful_hooks.md`（#7810 文档完善项）以及官方 Colab 教程：实验可视化模块，与日志系统耦合。
- **AvoidOOM** → 链接 `docs/en/get_started.md` 安装与使用指南（#7897 重写）：作为运行时容错机制，与训练入口脚本对接。
- **`auto_scale_lr`** → 隐式关联所有 config（用户需自行校验 `base_batch_size`）：与分布式训练调度器关联。
- **Class Aware Sampler** → 链接 OpenImages 数据集配置（外部 GitHub 链接）：长尾/类别不平衡场景的数据采样器，与 `train_dataloader` 紧耦合。
- **`MemoryProfilerHook`** → 链接 `useful_hooks.md`：显存监控与调试工具。

---

## 【使用方法】

> 以下均为原文明确给出的启用方式。

### 1. 启用 WandbLogger

```python
cfg.log_config.hooks = [
  dict(type='MMDetWandbHook',
       init_kwargs={'project': 'MMDetection-tutorial'},
       interval=10,
       log_checkpoint=True,
       log_checkpoint_metadata=True,
       num_eval_images=10)]
```
原文附带示例 Colab 教程：`https://colab.research.google.com/drive/1RCSXHZwDZvakFh3eo9RuNrJbCGqD0dru?usp=sharing#scrollTo=WTEdPDRaBz2C`。

### 2. 启用 AvoidCUDAOOM（两种姿势）

**函数包装式**：
```python
from mmdet.utils import AvoidCUDAOOM
output = AvoidCUDAOOM.retry_if_cuda_oom(some_function)(input1, input2)
```

**装饰器式**：
```python
from mmdet.utils import AvoidCUDAOOM

@AvoidCUDAOOM.retry_if_cuda_oom
def function(*args, **kwargs):
    ...
    return xxx
```

### 3. 启用 Class Aware Sampler

```python
data=dict(train_dataloader=dict(class_aware_sampler=dict(num_sample_class=1))))
```

### 4. 启用 Auto-scaling LR

在 config 中写入：
```python
auto_scale_lr = dict(enable=True, base_batch_size=N)
```
或在命令行追加 `--auto-scale-lr`；需自行核对 `base_batch_size = samples_per_gpu × gpu_number` 的正确性，默认 `enable=False`。

### 5. 启用 Memory Profiler Hook

```python
custom_hooks = [
    dict(type='MemoryProfilerHook', interval=50)
]
```

### 6. 升级到 v2.25.0 后切换 Mask2Former 任务

- 实例分割：使用 `mask2former_xxx_coco.py`
- 全景分割：使用 `mask2former_xxx_coco-panoptic.py`

### 7. Simple Copy-Paste 数据增强

参考示例配置：`configs/simple_copy_paste/mask_rcnn_r50_fpn_syncbn-all_rpn-2conv_ssj_scp_32x2_270k_coco.py`（#7501）。

> **关于 YOLOX、加速 Video 推理、`DilatedEncoder.block_dilations`、`DyHead + Swin-Large` 骨干预训练模型等项**：原文仅说明已修复/已支持/已发布，未给出具体启用代码，故不在此罗列。
