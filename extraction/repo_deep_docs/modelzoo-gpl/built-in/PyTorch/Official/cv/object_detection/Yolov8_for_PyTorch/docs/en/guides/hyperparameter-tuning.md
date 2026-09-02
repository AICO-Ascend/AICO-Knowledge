# Ultralytics YOLO [Hyperparameter Tuning](https://www.ultralytics.com/glossary/hyperparameter-tuning) Guide

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/hyperparameter-tuning.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/hyperparameter-tuning.md

# 一体化深度解读:Ultralytics YOLO 超参数调优指南

## 【定位】

这篇文档系统阐述 Ultralytics YOLO 中**基于遗传算法(突变)的超参数自动调优机制**,解决如何在训练前/训练过程中自动搜索 `lr0`/`batch`/`epochs`/`mosaic` 等高阶结构性参数的最优组合,以提升模型在精度、召回、mAP 等指标上的表现。

---

## 【技术要点】

1. **调优对象(可调超参数)**:涵盖**学习率** `lr0`(决定每次迭代向 loss 最小值的步长)、**batch size** `batch`(单次前向传播同时处理的图像数)、**epochs**(完整前向+反向遍历整个训练集的次数)、以及**架构细节**(通道数、层数、激活函数类型等)。完整增强超参数列表通过 `../usage/cfg.md#augmentation-settings` 提供。

2. **遗传算法机制**:Ultralytics YOLO 用**突变(Mutation)** 而非**交叉(Crossover)** 来生成新的超参数候选 —— 通过对现有超参数施加"小幅、随机"的扰动进行**局部搜索**。原文明确指出:"Crossover is a popular genetic algorithm technique, [but] it is not currently used in Ultralytics YOLO"。

3. **核心入口方法**:Python API 中通过 `model.tune(...)` 调用底层 `Tuner` 类。原文示例关键调用参数为:
   - `data="coco8.yaml"`
   - `epochs=30`
   - `iterations=300`
   - `optimizer="AdamW"`
   - `plots=False, save=False, val=False`(原文解释:"skipping plotting, checkpointing and validation other than on final epoch for faster Tuning")

4. **调优流程(闭环迭代)**:识别评估指标(AP50、F1-score 等) → 设置计算预算 → 初始化超参数 → 用 `_mutate` 方法突变 → 用突变后的超参数训练 → 用 AP50/F1-score 等评估 → 记录 metrics+hyperparameters → 重复,直至达到**预设迭代次数**或**性能指标达标**。

5. **输出物结构**(位于 `runs/detect/tune/` 下):
   - `best_hyperparameters.yaml` — 最佳超参数
   - `best_fitness.png` — fitness vs iteration 曲线
   - `tune_results.csv` — 每轮迭代的逐项记录
   - `tune_scatter_plots.png` — 超参数 vs 指标散点图
   - `weights/last.pt`、`weights/best.pt` — 最后/最佳权重

6. **调优禁用规则**:初始化为 0 的超参数**不会**被调优,原文示例中 `degrees=0.0`、`shear=0.0`、`perspective=0.0`、`flipud=0.0`、`mixup=0.0`、`copy_paste=0.0` 即属此类。

---

## 【关键机制与数据】

### 调优引擎:遗传突变(Mutation-only GA)

工作原理:在每轮迭代中,从已有的超参数集合出发,通过 `_mutate` 方法施加随机扰动生成新的候选超参数组合,然后用该组合训练模型并以 fitness(通常为 AP50 或综合指标)评价,保留优者进入下一代。**不使用交叉**,因此是一种纯粹的"局部随机搜索 + 选择"机制,而非传统遗传算法的"重组"。

### Fitness 评估指标(原文):

- 评价指标可选 **AP50**、**F1-score**,或自定义指标。
- `best_fitness.png` 是 fitness 对迭代次数的曲线,用于可视化遗传算法随时间的进展。

### 原文给出的真实最佳一次运行结果(YAML 注释中):

```
558/900 iterations complete ✅ (45536.81s)
Best fitness=0.64297 observed at iteration 498
Best fitness metrics:
  metrics/precision(B):    0.87247
  metrics/recall(B):       0.71387
  metrics/mAP50(B):        0.79106
  metrics/mAP50-95(B):     0.62651
  val/box_loss:            2.79884
  val/cls_loss:            2.72386
  val/dfl_loss:            0.68503
  fitness:                 0.64297
Best fitness model: /usr/src/ultralytics/runs/detect/train498
```

数据流(基于 YAML/CSV 输出可还原):

- **输入**:`yolo11n.pt` 预训练权重 + `coco8.yaml` 数据集配置 + 迭代次数 `iterations=300`、每轮 `epochs=30` + `AdamW` 优化器。
- **逐轮**:对 22 个超参数(`lr0, lrf, momentum, weight_decay, warmup_epochs, warmup_momentum, box, cls, dfl, hsv_h, hsv_s, hsv_v, degrees, translate, scale, shear, perspective, flipud, fliplr, mosaic, mixup, copy_paste`)进行扰动 → 训练 30 epoch → 记录 fitness 与各指标 → 写入 `tune_results.csv`。
- **输出**:在 900 次迭代中,第 498 次达到 fitness 峰值 0.64297,最佳超参数被持久化到 `best_hyperparameters.yaml`,最佳模型权重保存为 `weights/best.pt`。

### `best_hyperparameters.yaml` 中的最优超参数(原文逐字):

| 类别 | 超参数 | 最优值 |
|---|---|---|
| 优化器 | lr0 | 0.00269 |
| 优化器 | lrf | 0.00288 |
| 优化器 | momentum | 0.73375 |
| 优化器 | weight_decay | 0.00015 |
| 优化器 | warmup_epochs | 1.22935 |
| 优化器 | warmup_momentum | 0.1525 |
| 损失权重 | box | 18.27875 |
| 损失权重 | cls | 1.32899 |
| 损失权重 | dfl | 0.56016 |
| 增强 | hsv_h | 0.01148 |
| 增强 | hsv_s | 0.53554 |
| 增强 | hsv_v | 0.13636 |
| 增强 | degrees | 0.0 *(未调)* |
| 增强 | translate | 0.12431 |
| 增强 | scale | 0.07643 |
| 增强 | shear | 0.0 *(未调)* |
| 增强 | perspective | 0.0 *(未调)* |
| 增强 | flipud | 0.0 *(未调)* |
| 增强 | fliplr | 0.08631 |
| 增强 | mosaic | 0.42551 |
| 增强 | mixup | 0.0 *(未调)* |
| 增强 | copy_paste | 0.0 *(未调)* |

### `tune_results.csv` 原文示例(逐字)显示的迭代演进规律:

- 第 1 行 fitness=0.05021,第 2 行 0.07217,第 3 行 0.06584 —— 数值在小范围震荡,反映突变 + 选择的搜索性质。
- `lr0` 从 0.01 微扰到 0.01003;`momentum` 从 0.937 → 0.93897 → 0.91009;`warmup_epochs` 从 3.0 → 2.79757 → 3.42176 —— 证实了"小幅随机扰动"的突变机制。

---

## 【表格解读】

**原文无表格**(整篇文档未出现任何 markdown 表格;相关结构化信息以代码块/YAML/CSV/目录树形式呈现,已在【关键机制与数据】一节中用我整理的 markdown 表格逐行还原)。

---

## 【公式解读】

**原文无公式**(文档未给出任何 LaTeX 数学公式或伪代码公式;fitness 评估仅以"AP50, F1-score, or custom metrics"等文字描述)。

---

## 【关联】

文末/文内给出的内部链接揭示了与本指南紧密耦合的上下游模块:

1. **`../usage/cfg.md#augmentation-settings`** — **增强超参数的总目录**。本指南明确指向它作为"YOLO11 使用的全部增强超参数的完整列表"的权威参考,意味着 `hsv_h/s/v`、`degrees`、`translate`、`scale`、`shear`、`perspective`、`flipud/fliplr`、`mosaic`、`mixup`、`copy_paste` 等键的合法取值范围需查阅该页。
2. **`../yolov5/tutorials/hyperparameter_evolution.md`** — **YOLOv5 时代的超参数进化教程**。本指南是其在 YOLO11 上的继承与简化版本(去掉了 crossover),沿用了同一套 mutation-only 思路。
3. **`../integrations/ray-tune.md`** — **Ray Tune 集成**。可与本指南互补:Ray Tune 提供更强大的分布式/早停/调度器策略,适合大规模搜索,而本指南内置的遗传突变则是轻量、开箱即用的默认方案。
4. **`../usage/cfg.md#augmentation-settings`** — 重复引用,强调增强配置项的统一来源。
5. **`../yolov5/tutorials/hyperparameter_evolution.md`** — 重复引用,强调算法血统。
6. **`../guides/yolo-performance-metrics.md`** — **YOLO 性能指标指南**。调优时使用的 `AP50`、`mAP50-95`、`precision`、`recall`、`fitness` 等指标的定义与计算方式在此定义,与本指南的"Evaluate Model"步骤直接对应。
7. **`../hub/cloud-training.md`** — **Ultralytics HUB 云端训练**。当本地计算资源不足以承担"computationally intensive"的调优时,可通过 HUB 在云端运行 `model.tune()`,获得相同输出物结构。

---

## 【使用方法】

### Python API(原文唯一给出的启用方式):

```python
from ultralytics import YOLO

# 初始化 YOLO 模型
model = YOLO("yolo11n.pt")

# 在 COCO8 上对 YOLO11n 进行 30 epochs、300 次迭代的超参数调优
model.tune(
    data="coco8.yaml",
    epochs=30,
    iterations=300,
    optimizer="AdamW",
    plots=False,
    save=False,
    val=False,
)
```

### 关键参数含义(原文):

| 参数 | 原文作用说明 |
|---|---|
| `data` | 指定数据集配置(YAML),示例中为 `coco8.yaml` |
| `epochs` | 每次调优迭代中训练的总 epoch 数,示例为 30 |
| `iterations` | 调优总迭代次数,示例为 300 |
| `optimizer` | 优化器,示例为 `AdamW` |
| `plots=False` | 跳过绘图,加快调优 |
| `save=False` | 不保存 checkpoint,加快调优 |
| `val=False` | 仅在最后一轮做验证,加快调优 |

### 流程操作步骤(原文):

1. **识别指标**(AP50、F1-score 等)
2. **设定预算**(计算资源)
3. **初始化超参数**(默认或基于先验)
4. **突变**(调用 `_mutate`)
5. **训练 + 评估**
6. **记录** 结果到 `tune_results.csv` 等
7. **重复** 直至达到迭代上限或 fitness 达标

### 调优后使用方法(原文):

用 `best_hyperparameters.yaml` 中的值初始化未来训练(原文:"You can use this file to initialize future trainings with these optimized settings"),并使用 `runs/detect/tune/weights/best.pt` 作为最佳权重起点。
