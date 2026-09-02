# tips_for_best_training_results

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/tips_for_best_training_results.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/tips_for_best_training_results.md

# YOLOv5 最佳训练结果技巧 深度解读

## 【定位】

这篇文档解决的是"如何用 YOLOv5 训练得到最佳 mAP 与最好结果"的问题——它是一份系统性最佳实践指南，覆盖数据集准备、模型选择、训练超参三大维度，目标是让用户在不动默认设置或尽量少改动的前提下，获得可复现的高质量 YOLOv5 训练结果。

## 【技术要点】

1. **数据规模基线**：每类 ≥ 1500 张图像、≥ 10000 个标注实例；背景图（无目标图像）建议占数据集 0%–10%（原文给出参考：COCO 有 1000 张背景图，约占总数据的 1%）。
2. **数据多样性与标注一致性**：图像要覆盖部署环境（不同时段/季节/天气/光照/角度/来源）；全部类别全部图像都要标注，不允许部分标注（Partial labelling 将失败）；标签框必须紧贴目标、无空隙、无遗漏。
3. **背景图像机制**：背景图用于降低 False Positives (FP)，不需要任何 label；可通过 `train_batch*.jpg` 在训练启动时可视化校验标签正确性。
4. **模型族选择**：YOLOv5x / YOLOv5x6 通常结果最好但参数量大、需要更多 CUDA 显存、推理更慢；移动端推荐 YOLOv5s/m，云端推荐 YOLOv5l/x。
5. **两种训练起点**：小到中等数据集（VOC、VisDrone、GlobalWheat）推荐从预训练权重开始——`python train.py --data custom.yaml --weights yolov5s.pt`；大数据集（COCO、Objects365、OIv6）推荐从架构配置文件从头训练——`python train.py --data custom.yaml --weights '' --cfg yolov5s.yaml`。
6. **训练超参三要素**：先以默认 300 epochs 跑出 baseline；图像尺寸默认 `--img 640`，含大量小目标时可升到 `--img 1280`，推理时需与训练使用同一 `--img`；`--batch-size` 用硬件能承受的最大值（小 batch 会得到较差的 batchnorm 统计量）；超参默认值在 `hyp.scratch-low.yaml`，先跑默认再考虑改动——**增强类超参增大会减弱/推迟过拟合**、延长可训练时长并提升最终 mAP，`hyp['obj']` 这类损失分量增益的减小则有助于减轻对应分量的过拟合。

## 【关键机制与数据】

> 以下均与原文一致，未做引申。

原文强调的核心因果链：在**数据集足够大且标注良好**的前提下，大多数时候无需改动模型或训练设置就能得到不错的结果；如果结果不理想，再按本文档步骤迭代改进；**用户最应该先做的第一件事是用全部默认设置训练**，目的是建立性能基线并定位可改进环节。

原文给出的可观察信号（用于向社区求助前应提供的最大信息量）：train losses、val losses、P、R、mAP 曲线、PR curve、confusion matrix、training mosaics、test results、labels.png 等统计图，全部位于 `project/name` 目录（通常在 `yolov5/runs/train/exp`）。

原文关于 epochs 与过拟合的因果机制：300 epochs 出现过拟合迹象 → 减少 epochs；300 epochs 后仍无过拟合 → 延长到 600、1200 等更多 epochs。

原文关于 image size 的机制：COCO 在原生 `--img 640` 训练，由于小目标多也可受益于 `--img 1280`；若自定义数据集中小目标多，应在原分辨率或更高分辨率训练；**最佳推理结果在训练时所用的同一 `--img` 下获得**。

原文关于 batch size 的机制：batch 越小，batchnorm 统计量越差，应避免。

原文关于 augmentation 超参与过拟合的机制：增大 augmentation 超参 → 减弱并推迟过拟合 → 允许更长训练 → 更高最终 mAP；减小损失分量增益类超参（如 `hyp['obj']`）→ 帮助缓解对应损失分量的过拟合。

原文关于 COCO 背景图的机制（背景图用来降低 FP）：COCO 有 1000 张背景图作参考，占总量约 1%。

## 【表格解读】

**原文无表格**。文档中以四列代码块形式给出 train 命令的"可替换槽位"，不是表格：

```shell
python train.py --data custom.yaml --weights yolov5s.pt
                                             yolov5m.pt
                                             yolov5l.pt
                                             yolov5x.pt
                                             custom_pretrained.pt
```

这五行的语义是：`--weights` 参数是一个可替换槽位，分别可用官方预训练权重 `yolov5s.pt / yolov5m.pt / yolov5l.pt / yolov5x.pt` 或用户自定义的 `custom_pretrained.pt`；其余参数 `--data custom.yaml` 不变。

```bash
python train.py --data custom.yaml --weights '' --cfg yolov5s.yaml
                                                      yolov5m.yaml
                                                      yolov5l.yaml
                                                      yolov5x.yaml
```

这四行的语义是：当用户从零开始训练时，`--weights` 必须显式置空串 `''`，并通过 `--cfg` 指定模型架构 YAML（`yolov5s/m/l/x.yaml` 之一），而不是直接加载预训练权重——结构与权重都被显式重置。

## 【公式解读】

**原文无公式**。

## 【关联】

文档与本仓内其他模块的关联主要通过文末与文中给出的两条锚链接：

- **`./train_custom_data.md#local-logging`**：在「Dataset → Label verification」一节被引用，作为 `train_batch*.jpg` 马赛克可视化示例页的内链锚点（`#local-logging`），用于让用户在训练开始阶段就肉眼确认标签是否正确包围目标、无错标漏标。这一步是上游前置条件：标签对齐了，本指南后续的"训练结果才有意义"才有讨论的根基。
- **`./hyperparameter_evolution.md`**：在「Training Settings → Hyperparameters」一节被显式指向，作为**自动超参优化**配套教程——本文档对超参的态度是"先用 `hyp.scratch-low.yaml` 默认值跑，再考虑手动修改"；而该链接指向的演进教程提供的是自动化方法，作为本文档超参段落的下游/扩展路径。

此外在外部关联上，本文 doc 与外部 README 的「Pretrained Checkpoints」对照表（云端/移动端模型族选型）、`train.py` 的 argparser（epochs / batch-size / img 等全量参数定义）、`data/hyps/hyp.scratch-low.yaml`（默认超参定义）三个文件/页面有直接引用关系。

## 【使用方法】

原文显式给出的启用方式与配置项（含命令原文）：

- **从预训练权重启动（小/中数据集）**：

  ```shell
  python train.py --data custom.yaml --weights yolov5s.pt
  ```

  其中 `--weights` 可替换为 `yolov5m.pt / yolov5l.pt / yolov5x.pt / custom_pretrained.pt`，权重会自动从最新 YOLOv5 release 下载。

- **从架构配置从头启动（大数据集）**：

  ```bash
  python train.py --data custom.yaml --weights '' --cfg yolov5s.yaml
  ```

  其中 `--cfg` 可替换为 `yolov5m.yaml / yolov5l.yaml / yolov5x.yaml`；`--weights` 必须显式置空串以避免下载预训练权重。

- **训练超参调节三键**：
  - `--epochs`：从 300 起步，按过拟合与否酌增到 600 / 1200 或酌减。
  - `--img`：COCO 默认 `640`；含大量小目标可升 `1280`；推理须使用与训练相同的 `--img`。
  - `--batch-size`：取硬件可承受的最大值。
- **默认超参来源**：`data/hyps/hyp.scratch-low.yaml`，建议先不改超参跑通 baseline。
- **训练日志与可视化输出位置**：`project/name` 目录（默认 `yolov5/runs/train/exp`），含 `train_batch*.jpg`、`labels.png`、loss/PR/confusion matrix 等。
- **背景图像比例**：背景图占数据集 0%–10%（参考 COCO 的 1%），无 label，仅用于降低 FP。
