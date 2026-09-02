# YOLOv5 🚀 by Ultralytics, AGPL-3.0 license

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/hyperparameter_evolution.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/hyperparameter_evolution.md

# YOLOv5 超参数进化 (Hyperparameter Evolution) 深度解读

---

## 【定位】

本文档系统描述了 YOLOv5 中**基于遗传算法 (Genetic Algorithm) 的超参数自动优化机制**——通过定义一组超参数初值、设计适应度函数、迭代执行"变异"生成新个体，从而自动搜索出比人工设定更优的训练超参数组合，并产出可复用的 `hyp_evolved.yaml`。

---

## 【技术要点】

1. **超参数规模**: YOLOv5 共有约 **30 个超参数**，定义于 `/data/hyps` 目录下的 `*.yaml` 文件中，默认值针对从零训练 COCO 优化。
2. **进化算子**: 主要为**交叉 (crossover) 与变异 (mutation)**；本文档的实现**仅使用变异**，变异概率 **80%**，方差 **0.04**，子代由历代最优父代组合产生。
3. **默认迭代代数**: 基线场景 (base scenario) 默认跑 **300 代**，可通过 `--evolve 1000` 修改；建议最少 300 代以获得最佳结果。
4. **适应度 (Fitness) 函数**: 加权组合 `mAP@0.5` (权重 10%) + `mAP@0.5:0.95` (权重 90%)，Precision `P` 与 Recall `R` 权重为 0。
5. **基线场景示例**: 使用预训练权重 `yolov5s.pt` 在 `coco128.yaml` 上 finetune **10 个 epochs**；通过追加 `--evolve` 启动进化。
6. **多卡调度**: 通过 `for i in 0..7` 循环 + `nohup` 后台启动 + 30 秒错峰延迟 (`sleep $(expr 30 \* $i)`) 实现 8 卡并行进化。
7. **输出物**: 每代结果记录到 `runs/evolve/exp/evolve.csv`，每代最优子代保存为 `runs/evolve/hyp_evolved.yaml`，最终由 `utils.plots.plot_evolve()` 绘制 `evolve.png`。
8. **可视化解读**: 每超参数一个子图，x 轴为超参数值，y 轴为 fitness；黄色高密度区表示高频采样区；垂直分布表示该参数被禁用 (在 `train.py` 的 `meta` 字典中设置)。

---

## 【关键机制与数据】

### 工作流程 (4 步闭环)
1. **Initialize (初始化)**: 加载 `/data/hyps/*.yaml` 中的初值 (建议使用针对 COCO 从零训练优化的默认值)。
2. **Define Fitness (定义适应度)**: 自定义加权适应度函数，默认聚焦 `mAP@0.5:0.95`。
3. **Evolve (进化)**: 在基线场景上反复训练，每代生成变异子代并依据 fitness 筛选。
4. **Visualize (可视化)**: 用 `evolve.csv` 绘制参数-fitness 散点图，分析各超参数敏感度。

### 性能数据 (原文示例一次完整进化的产出)
> **原文示例结果** (Best generation=287 / Last generation=300):
>
> | 指标 | 值 |
> |------|-----|
> | metrics/precision | 0.54634 |
> | metrics/recall | 0.55625 |
> | metrics/mAP_0.5 | 0.58201 |
> | metrics/mAP_0.5:0.95 | 0.33665 |
> | val/box_loss | 0.056451 |
> | val/obj_loss | 0.042892 |
> | val/cls_loss | 0.013441 |

**原文:** 与默认初始值相比，`lrf` 由 0.01 → **0.2** (变化 20 倍)，其他超参数在示例中保持不变。

### 计算开销 (原文)
> "evolution is generally expensive and time-consuming, as the base scenario is trained hundreds of times, possibly requiring hundreds or thousands of GPU hours." — 即每代都需要完整训练一次基线场景，300 代意味着 **数百到上千 GPU·小时**。

### 传统方法对比 (原文依据)
> 传统网格搜索 (Grid Search) 在三类场景下变得不可行 (intractable):
> 1. 高维搜索空间 (high dimensional search space)
> 2. 维度间相关性未知 (unknown correlations among the dimensions)
> 3. 评估每个点的适应度代价昂贵 (expensive nature of evaluating the fitness at each point)

这是遗传算法 (GA) 在此场景下成为合适候选的原因。

---

## 【表格解读】

### 表 1: 默认超参数清单 (源自 `/data/hyps/*.yaml`，原文逐字还原)

| 参数名 | 默认值 | 含义 (原文注释) |
|--------|--------|-----------------|
| lr0 | 0.01 | initial learning rate (SGD=1E-2, Adam=1E-3) |
| lrf | 0.01 | final OneCycleLR learning rate (lr0 * lrf) |
| momentum | 0.937 | SGD momentum/Adam beta1 |
| weight_decay | 0.0005 | optimizer weight decay 5e-4 |
| warmup_epochs | 3.0 | warmup epochs (fractions ok) |
| warmup_momentum | 0.8 | warmup initial momentum |
| warmup_bias_lr | 0.1 | warmup initial bias lr |
| box | 0.05 | box loss gain |
| cls | 0.5 | cls loss gain |
| cls_pw | 1.0 | cls BCELoss positive_weight |
| obj | 1.0 | obj loss gain (scale with pixels) |
| obj_pw | 1.0 | obj BCELoss positive_weight |
| iou_t | 0.20 | IoU training threshold |
| anchor_t | 4.0 | anchor-multiple threshold |
| fl_gamma | 0.0 | focal loss gamma (efficientDet default gamma=1.5) |
| hsv_h | 0.015 | image HSV-Hue augmentation (fraction) |
| hsv_s | 0.7 | image HSV-Saturation augmentation (fraction) |
| hsv_v | 0.4 | image HSV-Value augmentation (fraction) |
| degrees | 0.0 | image rotation (+/- deg) |
| translate | 0.1 | image translation (+/- fraction) |
| scale | 0.5 | image scale (+/- gain) |
| shear | 0.0 | image shear (+/- deg) |
| perspective | 0.0 | image perspective (+/- fraction), range 0-0.001 |
| flipud | 0.0 | image flip up-down (probability) |
| fliplr | 0.5 | image flip left-right (probability) |
| mosaic | 1.0 | image mosaic (probability) |
| mixup | 0.0 | image mixup (probability) |
| copy_paste | 0.0 | segment copy-paste (probability) |

**逐行解读 (按功能分组):**

- **优化器组 (lr0, lrf, momentum, weight_decay)**: 控制梯度下降核心动力学；`lrf=0.01` 表示 OneCycleLR 的最终学习率为初始值的 1%，`momentum=0.937` 是 SGD 推荐值。
- **学习率热身组 (warmup_*)**: 训练前 3 个 epoch 逐步将 momentum 从 0.8 升到 0.937、bias lr 从 0.1 升到 lr0，避免初期梯度震荡。
- **损失权重组 (box, cls, cls_pw, obj, obj_pw, fl_gamma)**: 三类损失加权；`box=0.05` 较小因为 box 本身数值大；`fl_gamma=0.0` 即不启用 Focal Loss。
- **IoU/Anchor 组 (iou_t, anchor_t)**: 正负样本划分阈值与 anchor 多重阈值。
- **颜色增强组 (hsv_h, hsv_s, hsv_v)**: HSV 空间数据增强，最大饱和度 0.7、亮度 0.4。
- **几何增强组 (degrees, translate, scale, shear, perspective, flipud, fliplr)**: 旋转/平移/缩放/错切/透视/翻转；默认仅启用水平翻转 (0.5)。
- **复合增强组 (mosaic, mixup, copy_paste)**: Mosaic 概率 1.0 (默认开启)，mixup 与 copy_paste 默认关闭。

### 表 2: 进化前后对比 (来自原文示例)

| 超参数 | 默认初值 | 进化后值 | 变化倍数 |
|--------|----------|----------|----------|
| lrf | 0.01 | 0.2 | 20× |
| 其余 27 项 | — | 与初值相同 | 1× |

> **原文:** 文档给出的实例中，仅 `lrf` 发生明显变化，其他保持不变——意味着遗传算法可能只"动"了真正影响收敛的若干维度。

### 表 3: 适应度权重矩阵 (原文)

| 指标 | Precision (P) | Recall (R) | mAP@0.5 | mAP@0.5:0.95 |
|------|:-------------:|:----------:|:-------:|:------------:|
| 权重 w | 0.0 | 0.0 | 0.1 | 0.9 |

> **解读:** `mAP@0.5:0.95` (COCO 主指标) 占 90% 权重主导，`mAP@0.5` 占 10% 辅助，P/R 被排除 (适应度聚焦定位质量)。

---

## 【公式解读】

### 公式 1: 适应度函数 (Python 伪代码)

```python
def fitness(x):
    """Return model fitness as the sum of weighted metrics [P, R, mAP@0.5, mAP@0.5:0.95]."""
    w = [0.0, 0.0, 0.1, 0.9]   # weights for [P, R, mAP@0.5, mAP@0.5:0.95]
    return (x[:, :4] * w).sum(1)
```

**符号含义:**
- `x`: 形状为 `(N, ≥4)` 的指标矩阵，每行对应一个候选超参数个体，每列依次为 `[P, R, mAP@0.5, mAP@0.5:0.95]`。
- `x[:, :4]`: 取前 4 列 (P/R/mAP@0.5/mAP@0.5:0.95)。
- `w = [0.0, 0.0, 0.1, 0.9]`: 各指标权重向量。
- `x[:, :4] * w`: 广播逐元素相乘，关闭 P 与 R (权重 0)。
- `.sum(1)`: 沿 axis=1 求和，得到每个个体的标量 fitness。

**作用:** 将 4 项检测指标压缩为单标量值，遗传算法对该值做最大化 (maximize)。

### 公式 2: 学习率调度 (OneCycleLR)

$$ \text{lr}(t) = \text{lr0} \times \text{lrf} $$

**符号含义:**
- `lr0`: 初始学习率 (默认 `0.01`)。
- `lrf`: 最终学习率**倍率因子** (默认 `0.01` → 最终 lr = 0.0001；进化后 `0.2` → 最终 lr = 0.002)。
- `t`: OneCycleLR 调度器内部步进。

**作用:** 在训练末段将学习率衰减到初始值的 `lrf` 倍；进化示例中 `lrf` 从 0.01 飙到 0.2，表明遗传算法发现该场景下应保留更高的末期学习率。

---

## 【关联】

### 与本文档同源 (上下游/平行模块)

- **`utils/metrics.py`**: 默认 fitness 函数 `fitness()` 的实际定义位置 (本文档中仅以伪代码呈现，推荐使用源码默认版本)。
- **`utils/plots.plot_evolve()`**: 进化结束后将 `evolve.csv` 绘制为 `evolve.png` 的工具函数。
- **`train.py` 中的 `meta` 字典**: 控制哪些参数被"禁用" (固定不变、不参与变异)，用于防止关键参数漂移。
- **`/data/hyps/*.yaml`**: 30 个超参数的初始定义文件所在目录。
- **`runs/evolve/exp/`**: 进化实验输出根目录 (含 `evolve.csv` 与每代最优 `hyp_evolved.yaml`)。

### 与仓库其他文档 (云端/环境部署)

通过文末 `Supported Environments` 章节衔接:

| 文档路径 | 作用 |
|---------|------|
| `../environments/google_cloud_quickstart_tutorial.md` | 在 GCP 上快速启动 YOLOv5 (可作为进化任务的运行环境) |
| `../environments/aws_quickstart_tutorial.md` | 在 AWS 上快速启动 YOLOv5 (可作为进化任务的运行环境) |
| `../environments/azureml_quickstart_tutorial.md` | 在 Azure ML 上快速启动 YOLOv5 (适合大规模多 GPU 进化) |
| `../environments/docker_image_quickstart_tutorial.md` | 通过 Docker 镜像快速启动 YOLOv5 (含 CUDA/CUDNN 预装环境，便于复现) |

> **逻辑关系:** 由于进化过程需要"数百到上千 GPU·小时"，上述云端/容器环境文档为大规模并行进化 (例如 8 卡或更多) 提供了基础设施参考。

---

## 【使用方法】

### 命令 (原文提供)

| 场景 | 命令 |
|------|------|
| 基线训练 (未进化) | `python train.py --epochs 10 --data coco128.yaml --weights yolov5s.pt --cache` |
| 单卡启动进化 | `python train.py --epochs 10 --data coco128.yaml --weights yolov5s.pt --cache --evolve` |
| 多卡启动进化 (推荐) | 见下方 8 卡 `for` 循环 + `nohup` + `sleep $(expr 30 \* $i)` 错峰脚本 |
| 多卡 `while` 循环 (原文标注: 不推荐) | 见原文 `while true; do nohup python train.py...` 片段 |
| 自定义代数 | `python train.py --evolve 1000` |

### 多卡进化启动脚本 (原文)

```bash
for i in 0 1 2 3 4 5 6 7; do
  sleep $(expr 30 \* $i) &&  # 30-second delay (optional)
  echo 'Starting GPU '$i'...' &&
  nohup python train.py --epochs 10 --data coco128.yaml --weights yolov5s.pt --cache --device $i --evolve > evolve_gpu_$i.log &
done
```

### 前置环境 (原文 "Before You Start")

```bash
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt  # 需 Python>=3.8.0、PyTorch>=1.8
```

### 产物与可视化 (原文)

```python
from utils.plots import plot_evolve
plot_evolve('runs/evolve/exp/evolve.csv')  # 生成 evolve.png
```

### 关键配置项

- **`--evolve <N>`**: 设置进化代数 (默认 300)。
- **`train.py` 中 `meta` 字典**: 列出"禁用/不参与变异"的超参数名 (即 `fliplr=0.5` 这种固定值)，防止被 GA 改写。
- **`/data/hyps/*.yaml`**: 可替换/编辑初始超参数文件以注入先验知识。

> **原文未涉及:** 自定义变异算子 (crossover)、早停 (early stopping) 阈值、单代内多 trial 平均等机制；本文档聚焦于 mutation-only 流程。
