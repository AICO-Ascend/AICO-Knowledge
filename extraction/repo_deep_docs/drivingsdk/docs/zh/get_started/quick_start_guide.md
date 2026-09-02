# 快速入门

> 仓 `drivingsdk` · 路径 `docs/zh/get_started/quick_start_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/drivingsdk/docs/zh/get_started/quick_start_guide.md

# Driving SDK 快速入门 深度解读

## 【定位】

这篇文档是 Driving SDK（华为昇腾-自动驾驶加速库）的快速入门指南，通过两个端到端示例（scatter_max 算子调用和 BEVFusion 模型训练），引导开发者快速体验并验证 Driving SDK 两大核心能力——**高性能算子库**与**优选模型库**。

---

## 【技术要点】

1. **两大核心能力定位**：Driving SDK 提供高性能算子库（NPU 优化算子，可替代 PyTorch 原生算子）和优选模型库（BEVFusion、BEVFormer、Sparse4D 等典型自动驾驶模型的 NPU 迁移方案）。
2. **scatter_max 算子功能**：根据索引将多个源张量中对应位置的最大值聚合到目标张量，同时返回每个最大值来自哪个源张量（argmax）。
3. **scatter_max 张量规格**：输入 `updates` 为 float32 类型 (3,8) 矩阵，`indices` 为 int32 类型 (3,) 向量 ` [0, 2, 0]`，`out` 初始化为 `(3, 8)` 的全零张量；输出为 `out`（最大值聚合结果）+ `argmax`（来源索引，int32 类型）。
4. **BEVFusion 环境一键安装**：通过 `bash install_BEVFusion.sh` 脚本自动完成 `mmcv` 和 `mmdetection3d` 的源码编译安装。
5. **数据集要求**：使用 nuScenes 数据集，需构建包含 `maps`、`samples`、`sweeps`、`v1.0-test`、`v1.0-trainval` 的 `nuscenes` 目录，并通过 `tools/create_data.py` 预处理生成 `nuscenes_gt_database` 与 `nuscenes_infos_{train,val,test}.pkl`。
6. **训练参数默认值**：训练脚本 `train_full_8p_base_fp32.sh` 默认值——`--batch-size=4`、`--num-npu=8`、`--epochs=6`。
7. **训练日志与验证产物**：日志默认输出到 `test/output/0/train_0.log`；训练完成后自动验证并输出 mAP/mATE/mASE/mAOE/mAVE/mAAE/NDS 等指标。
8. **依赖预训练权重**：需要两份外部权重文件——`swint-nuimages-pretrained.pth`（Swin 骨干网络 nuImages 预训练）和 `bevfusion_lidar_voxel0075_second_secfpn_8xb4-cyclic-20e_nus-3d-2628f933.pth`（lidar-only 检测器）。

---

## 【关键机制与数据】

### 算子工作机制（scatter_max）

- **输入说明（原文）**：`updates` 是一个 (3, 8) 的 float32 张量，承载 3 个源张量；`indices = [0, 2, 0]` 表示 3 个源张量分别要聚合到 `out` 的第 0 行、第 2 行、第 0 行。
- **聚合规则（原文）**：第 0 行与第 0 行逐位置取 max → 输出 `out[0]`；第 2 行单独存在 → 输出 `out[2]`；`out[1]` 没有 indices 指向，因此保持初始的全零（聚合后仍为 0）。
- **argmax 含义（原文）**：返回每个输出位置的最大值来自哪个源行；当 `out` 中全零位置无任何聚合来源时，argmax 退化为初始化填充值 3（即"out 的初始 z 行索引 3"——实际 `argmax[1]` 全为 3，对应 `out` 初始化的全零行；`argmax[2]` 全为 1，对应唯一一个写入了 `out[2]` 的源行）。

### 数据流（算子层）

```
updates (3×8, float32) ─┐
indices (3, int32)    ─┼─→ scatter_max(updates, indices, out) ─→ out (3×8, 聚合最大值)
out    (3×8, zeros)    ─┘                                   ─→ argmax (3×8, int32, 来源索引)
```

### 数据流（模型层）

```
BEVFusion 代码根目录
    ↓ bash install_BEVFusion.sh（自动编译 mmcv + mmdetection3d）
依赖环境
    ↓ 下载 nuScenes 数据集 + tools/create_data.py 预处理
训练数据（nuscenes_gt_database + nuscenes_infos_*.pkl）
    ↓ 下载 Swin / lidar-only 权重至 pretrained/
预训练权重
    ↓ bash test/train_full_8p_base_fp32.sh
训练日志（test/output/0/train_0.log）→ 自动验证 → 评估指标
```

### 训练日志样本数据（原文给出）

```
Epoch(train) [1][1/3862]  lr: 6.6667e-05  eta: 36 days, 9:13:56  time: 135.6712
  data_time: 4.1619  memory: 18113  grad_norm: nan  loss: 18.0867
  loss_heatmap: 6.6903  layer_-1_loss_cls: 0.5519  layer_-1_loss_bbox: 10.8446  matched_ious: 0.0018
```

训练日志显示当前为 FP32 训练第 1 个 epoch 的第 1/3862 iter。

### 验证评估指标（原文给出，训练完成后自动验证输出）

| 指标 | 数值 |
|---|---|
| mAP | 0.6805 |
| mATE | 0.2762 |
| mASE | 0.2518 |
| mAOE | 0.3478 |
| mAVE | 0.2928 |
| mAAE | 0.1951 |
| NDS | 0.7039 |
| Eval time | 158.1s |

---

## 【表格解读】

**原文表1（参数说明）逐字还原**：

| 参数名 | 说明 |
| ---- | ---- |
| `--batch-size` | 每卡batchsize，默认值为4。 |
| `--num-npu` | 每节点NPU卡数，默认值为8。 |
| `--epochs` | 训练轮数，默认值为6。 |

**逐行解读**：

- `--batch-size`：每张 NPU 卡上的 batch size，默认值为 4。原文示例命令中显式传入 `--batch-size=4` 与默认值一致；该参数决定了单卡一次前向/反向传播处理的样本数。
- `--num-npu`：每个节点上使用的 NPU 卡数，默认值为 8。原文示例命令中显式传入 `--num-npu=8` 与默认值一致；该参数决定了分布式训练的并行规模（8 卡数据并行）。
- `--epochs`：训练的总轮数，默认值为 6。原文在脚本注释中已明确指出"FP32精度训练（默认6个 epochs）"，与该默认值一致。

---

## 【公式解读】

原文无公式。

---

## 【关联】

Driving SDK 快速入门在文档生态中位于入口位置，向下串联到以下多个子模块：

- **[Driving SDK 软件安装](../installation/installation.md)**（前置依赖）：文档开头即提示读者先完成环境搭建，详细安装说明在该文档中。本快速入门的所有示例（算子调用、模型训练）都假设环境已安装完毕。
- **[API 清单](../api/README.md)**（算子库入口）：scatter_max 所属的高性能算子库的完整算子索引页，"详细说明请参阅"指向此处，是算子查询的统一入口。
- **[scatter_max 算子说明](../api/context/scatter_max.md)**（算子细节）：scatter_max 的独立技术文档，提供完整 API 签名、参数说明与适用场景；快速入门只演示最小可用代码片段，深度使用需跳转此处。
- **[BEVFusion 模型说明](../../../model_examples/BEVFusion/README.md)**（模型细节）：优选模型库中 BEVFusion 的独立技术文档；快速入门展示了从环境安装到训练启动的完整链路，但模型结构、配置细节、推理导出等内容均在 `../../../model_examples/BEVFusion/README.md` 中。
- **[模型清单](../models/support_list.md)**（模型库索引）：列出优选模型库中所有模型（BEVFusion、BEVFormer、Sparse4D 等）的清单与详细使用指导；快速入门是 BEVFusion 的具体示例，但 BEVFormer、Sparse4D 等其他模型可在此清单中找到入口。

整体链路：`installation.md`（安装）→ `quick_start_guide.md`（快速上手示例）→ `api/README.md` + `models/support_list.md`（能力索引）→ `scatter_max.md` / `BEVFusion/README.md`（具体 API/模型深度文档）。

---

## 【使用方法】

### scatter_max 算子调用（原文给出）

```python
import torch, torch_npu
from mx_driving import scatter_max

updates = torch.tensor([[2, 0, 1, 3, 1, 0, 0, 4],
                        [0, 2, 1, 3, 0, 3, 4, 2],
                        [1, 2, 3, 4, 4, 3, 2, 1]], dtype=torch.float32).npu()
indices = torch.tensor([0, 2, 0], dtype=torch.int32).npu()
out = updates.new_zeros((3, 8))
out, argmax = scatter_max(updates, indices, out)
print(out)
print(argmax)
```

### BEVFusion 训练完整流程（原文给出）

```shell
# 1. 进入模型代码根目录
cd DrivingSDK/model_examples/BEVFusion

# 2. 一键安装依赖（自动编译 mmcv 与 mmdetection3d 源码）
bash install_BEVFusion.sh

# 3. 进入自动创建的 mmdetection3d 目录，下载/软链接 nuScenes 数据集
cd mmdetection3d

# 4. 数据预处理（生成 GT database 与 infos pickle）
python tools/create_data.py nuscenes --root-path ./data/nuscenes --out-dir ./data/nuscenes --extra-tag nuscenes

# 5. 创建 pretrained 目录并放置两个权重文件
mkdir pretrained
cd pretrained
# (手动下载 swint-nuimages-pretrained.pth 与 bevfusion_lidar_voxel0075_second_secfpn_8xb4-cyclic-20e_nus-3d-2628f933.pth)

# 6. 返回 BEVFusion 模型根目录
cd ../..

# 7. 启动 FP32 精度训练（默认 6 个 epochs）
bash test/train_full_8p_base_fp32.sh --batch-size=4 --num-npu=8
```

### 关键配置项（原文给出）

- **算子库导入路径**：`from mx_driving import scatter_max`（Driving SDK Python 包名为 `mx_driving`）。
- **张量 device 要求**：必须调用 `.npu()` 将张量搬至 NPU 设备；返回结果默认在 `device='npu:0'`。
- **训练脚本路径**：`test/train_full_8p_base_fp32.sh`，接受三种参数形式——默认值、关键字参数、位置参数。
- **训练日志路径**：`test/output/0/train_0.log`。
- **预训练权重目录**：`mmdetection3d/pretrained/` 下需放置两个 `.pth` 文件。
