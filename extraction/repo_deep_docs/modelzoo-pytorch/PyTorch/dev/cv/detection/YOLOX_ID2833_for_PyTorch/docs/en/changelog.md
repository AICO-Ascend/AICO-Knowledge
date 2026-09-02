# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/changelog.md

# MMDetection Changelog 深度解读 (v2.24.0 ~ v2.25.3)

## 【定位】

本文档是 MMDetection 官方维护的 **Changelog (变更日志)**,按版本时间倒序记录了 v2.25.3 (2022-10-25)、v2.25.2 (2022-09-15)、v2.25.1 (2022-07-29)、v2.25.0 (2022-05-31)、v2.24.0 (2022-04-26) 共 5 个版本的 Bug Fixes、Improvements、Documents、New Features、Highlights、Backward Incompatible Changes 以及 Contributors 名单,是用户升级迁移、查阅 API 行为变更、追溯贡献者的权威依据。

---

## 【技术要点】

1. **新增骨干/检测器支持**:`ConvNeXt` (论文 2201.03545)、`DDOD` (论文 2107.02963)、`SOLOv2` (论文 2003.10152)、`Mask2Former` (论文 2112.01527, 实例分割分支) 共四大模型首次并入或扩展。
2. **Mask2Former 配置文件命名重构 (破坏性)**:v2.25.0 起,原 `mask2former_xxx_coco.py` 含义由「全景分割」**改为**「实例分割」,并新增 `mask2former_xxx_coco-panoptic.py` 专门承载全景分割任务。
3. **OOM 自愈机制 (`AvoidOOM` / `AvoidCUDAOOM`)**:三级重试策略——先 `torch.cuda.empty_cache()` → 再 FP16 转换 → 最后 GPU→CPU 数据搬运,使 OOM 后代码仍能继续运行;提供函数包装与装饰器两种用法。
4. **专用 `WandbLoggerHook` (MMDetWandbHook)**:支持 `project`、`interval`、`log_checkpoint`、`log_checkpoint_metadata`、`num_eval_images` 等字段,并提供 Colab 教程。
5. **ClassAwareSampler**:在 `train_dataloader` 下新增 `class_aware_sampler` 字段,`num_sample_class=1` 等,用于在 OpenImages 等长尾数据集上提升表现。
6. **`auto_scale_lr` 自动学习率缩放**:依据 `samples_per_gpu × gpu number` 与 `base_batch_size=N` 自动线性调整 LR,可通过 `--auto-scale-lr` 命令行开关启用,默认 `enable=False`。
7. **analyze_result.py 加速**:官方声明「评估时间提速 10~15 倍」「单次任务仅需 10~15 分钟」(PR #7891)。
8. **Simple Copy-Paste 数据增强**:支持将源图实例粘贴到目标图,典型配置 `configs/simple_copy_paste/mask_rcnn_r50_fpn_syncbn-all_rpn-2conv_ssj_scp_32x2_270k_coco.py`。
9. **跨平台 / 兼容性**:修复 Pytorch 1.10 不兼容、单 GPU 分布式训练 CUDA device 指定错误、macOS 上图像 shape 获取错误、`mdformat` 兼容 Python 3.6 等。
10. **配置文件 `${key}` 占位替换**:支持用 `cfg.key` 的值替换配置文本中的 `${key}`,便于按需替换字段 (PR #7492)。
11. **DyHead × Swin-Large 发布**:PR #7733 放出带 Swin-Large 主干的 DyHead 配置。

---

## 【关键机制与数据】

| 机制 / 改动 | 工作原理与数据 (原文摘录) |
|---|---|
| `AvoidCUDAOOM` 自愈流程 | 原文:「It will first retry after calling `torch.cuda.empty_cache()`. If it still fails, it will then retry by converting the type of inputs to FP16 format. If it still fails, it will try to copy inputs from GPUs to CPUs to continue computing.」三级兜底,优先显存回收→精度降级→设备降级。 |
| `MMDetWandbHook` 配置示例 | 原文:`cfg.log_config.hooks = [dict(type='MMDetWandbHook', init_kwargs={'project': 'MMDetection-tutorial'}, interval=10, log_checkpoint=True, log_checkpoint_metadata=True, num_eval_images=10)]` |
| `ClassAwareSampler` 启用 | 原文:`data=dict(train_dataloader=dict(class_aware_sampler=dict(num_sample_class=1))))`,示例参考 OpenImages 配置。 |
| `auto_scale_lr` 启用 | 原文:`auto_scale_lr = dict(enable=True, base_batch_size=N)`,`N = samples_per_gpu × gpu_number`,可通过 `--auto-scale-lr` 命令行开关。 |
| `analyze_result.py` 性能提升 | 原文:「The evaluation time is speedup by 10 ~ 15 times and only tasks 10 ~ 15 minutes now.」(PR #7891) |
| `WandbLoggerHook` 与 v2.25.3 离线兼容 | 原文:「Skip remote sync when wandb is offline」(PR #8755) |
| YOLOX 跨设备训练 | 原文:「Enable YOLOX training on different devices」(PR #7912) |
| `DilatedEncoder.block_dilations` 可设 | 原文:「Support to set `block_dilations` in `DilatedEncoder`」(PR #7812) |
| Video Inference 数据加载加速 | 原文:「Speedup the Video Inference by Accelerating data-loading Stage」(PR #7832) |
| `gpu_collect` 可从配置读取 | 原文:「Support reading `gpu_collect` from `cfg.evaluation.gpu_collect`」(PR #7672) |
| ONNX 简化器版本要求 | 原文:「Upgrade onnxsim to at least 0.4.0」(PR #8383) |
| Mask2Former 配置拆分语义变更 | 原文表格(见下节) |

---

## 【表格解读】

### 唯一完整可还原的表格:Mask2Former 配置语义对照表 (v2.25.0)

原文逐字还原:

| before v2.25.0 | after v2.25.0 |
|---|---|
| `mask2former_xxx_coco.py` represents config files for **panoptic segmentation**. | `mask2former_xxx_coco.py` represents config files for **instance segmentation**. <br> `mask2former_xxx_coco-panoptic.py` represents config files for **panoptic segmentation**. |

**逐行解读**:
- **「before v2.25.0」列**:在 v2.24.x 及更早版本,所有 `mask2former_xxx_coco.py` 一律承担「全景分割 (panoptic segmentation)」任务。
- **「after v2.25.0」列上条**:v2.25.0 起,无后缀的 `mask2former_xxx_coco.py` **语义被重定义为「实例分割 (instance segmentation)」**,这一变更属于 Backwards Incompatible Changes (PR #7571)。
- **「after v2.25.0」列下条**:同时新增 `mask2former_xxx_coco-panoptic.py` 专门用于全景分割,旧的全景分割配置必须改用 `-panoptic` 后缀,否则会跑成实例分割任务。

> 注:原文还给出了另一处「v2.23.0 vs v2.24.0」 dataloader 参数对照表,但由于文档末尾被截断 (`val=dict(typ` 后内容缺失),无法逐字还原完整表格,故此处不补全。

---

## 【公式解读】

**原文无公式。**

(虽然变更日志涉及 Gaussian radius 等数学概念,但原文只以「Fix mistakes in gaussian radius formula (PR #8607)」一笔带过,未给出任何 LaTeX/伪代码公式表达式,因此按要求如实标注「无」。)

---

## 【关联】

| 关联项 | 关系性质 | 在本文档出现位置 |
|---|---|---|
| `configs/convnext` | 新增模型配置目录 | v2.25.0 Highlights / New Features |
| `configs/ddod` | 新增模型配置目录 | v2.25.0 Highlights / New Features |
| `configs/solov2` | 新增模型配置目录 | v2.25.0 Highlights / New Features |
| `configs/mask2former` | 重命名/重定义语义的配置目录 (出现 4 次) | v2.25.0 Highlights、Backwards incompatible changes |
| `docs/en/get_started.md` | 安装指南被重写 | v2.25.0 Improvements (PR #7897) |
| `docs/en/tutorials/useful_hooks.md` | 新增 Hook 教程 | v2.25.0 Improvements (PR #7810) |
| `configs/simple_copy_paste/mask_rcnn_r50_fpn_syncbn-all_rpn-2conv_ssj_scp_32x2_270k_coco.py` | Simple Copy-Paste 实例分割参考配置 | v2.24.0 New Features (PR #7501) |
| `docs/en/get_started.md`、`useful_hooks.md` | 与 `MMDetWandbHook`、`AvoidCUDAOOM` 等改进同批发布 | v2.25.0 |

**关系网总结**:v2.25.0 是本文档的核心枢纽版本——它一次性引入 ConvNeXt/DDOD/SOLOv2/Mask2Former 四模型、引入 Wandb Hook 与 OOM 自愈两大基础设施;v2.25.1、v2.25.2、v2.25.3 三个 patch 版本则围绕这些新能力做 Bug Fix(单 GPU 分布式、PyTorch 1.10 兼容、Wandb 离线模式等),而 v2.24.0 则提供了 Simple Copy-Paste、ClassAwareSampler、auto_scale_lr 等被 v2.25.0 复用的前置能力。

---

## 【使用方法】

> 原文未集中给出统一的「启用方式」清单,以下仅整理**直接出现于原文的代码/命令片段**。

### 1. 启用 `MMDetWandbHook` (原文, v2.25.0)
```python
cfg.log_config.hooks = [
    dict(type='MMDetWandbHook',
         init_kwargs={'project': 'MMDetection-tutorial'},
         interval=10,
         log_checkpoint=True,
         log_checkpoint_metadata=True,
         num_eval_images=10)]
```
配套 Colab 教程见原文链接 `https://colab.research.google.com/drive/1RCSXHZwDZvakFh3eo9RuNrJbCGqD0dru?usp=sharing#scrollTo=WTEdPDRaBz2C`。

### 2. 使用 `AvoidCUDAOOM` —— 函数包装 (原文, v2.25.0)
```python
from mmdet.utils import AvoidCUDAOOM
output = AvoidCUDAOOM.retry_if_cuda_oom(some_function)(input1, input2)
```

### 3. 使用 `AvoidCUDAOOM` —— 装饰器 (原文, v2.25.0)
```python
from mmdet.utils import AvoidCUDAOOM

@AvoidCUDAOOM.retry_if_cuda_oom
def function(*args, **kwargs):
    ...
    return xxx
```

### 4. 启用 `ClassAwareSampler` (原文, v2.24.0)
```python
data=dict(train_dataloader=dict(class_aware_sampler=dict(num_sample_class=1))))
```
参考:OpenImages Faster R-CNN 配置。

### 5. 启用 `auto_scale_lr` (原文, v2.24.0)
在 config 中写入:
```python
auto_scale_lr = dict(enable=True, base_batch_size=N)
```
其中 `N = samples_per_gpu × gpu_number`;或通过命令行加 `--auto-scale-lr` 开关。默认 `enable=False`。

### 6. Mask2Former 任务切换 (原文, v2.25.0)
- 实例分割:使用 `configs/mask2former/mask2former_xxx_coco.py`
- 全景分割:使用 `configs/mask2former/mask2former_xxx_coco-panoptic.py`

### 7. onnxsim 升级 (原文, v2.25.2)
需将 onnxsim 升级至 **至少 0.4.0**(PR #8383)。

> 其它如 ConvNeXt/DDOD/SOLOv2/Mask2Former/Simple Copy-Paste 的训练/推理命令,原文**未涉及**具体 CLI,需参照各自 `configs/...` 目录下的 README。
