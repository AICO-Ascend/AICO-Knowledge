# Tutorial 7: Backends Support

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/backends_support.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/backends_support.md

# 一体化深度解读: Tutorial 7 — Backends Support

---

## 【定位】

本教程属于 BEVDet_for_PyTorch (基于 mmdetection3d 体系) 的训练基础设施层文档,**解决在 BEVDet/3D 检测框架中接入非本地存储后端 (Ceph, 通过 `petrel` 客户端) 进行数据、模型权重、检查点和训练日志的读写问题**,从而使得训练流程无须依赖本地磁盘拷贝,可以直接从分布式对象存储拉取 nuScenes/KITTI 等大规模 3D 感知数据。

---

## 【技术要点】

1. **统一抽象层 — `file_client_args`**: 框架将文件 I/O 抽象为 file_client,所有需要读文件的模块都通过同一个 `file_client_args` 字典配置,只需改一处即可切换 Disk / Ceph (petrel) / LMDB 等后端,无需改业务逻辑。
2. **`path_mapping` 本地→远程路径映射**: `backend='petrel'` 时,需要通过 `path_mapping` 字典将本地相对路径 (如 `./data/nuscenes/`、`data/nuscenes/`) 映射为 Ceph 上的 `s3://` URI (`s3://openmmlab/datasets/detection3d/nuscenes/`),代码示例中显式给出了**两个等价映射** (带 `./` 与不带 `./`) 防止相对路径差异导致检索失败。
3. **`db_sampler` 双侧 file_client 注入**: db_sampler 同时承担"加载训练点云"和"加载 dbinfo pkl"两个职责,因此在示例中既给 `points_loader` 注入 `file_client_args`,也给 db_sampler 自身注入 `file_client_args`,保证从 Ceph 加载 GT 数据库信息 (kitti_dbinfos_train.pkl) 时也能命中同一后端。
4. **三处信息文件注入点**: 训练管线中需要在三类位置同时配置 `file_client_args`:`train_pipeline` 的 `LoadPointsFromFile` 和 `LoadAnnotations3D`、`test_pipeline` 的 `LoadPointsFromFile`,以及 `data` dict 的 `train/val/test` 三项,实现**训练/验证/测试**全链路 Ceph 化。
5. **检查点三类 URI 注入**:
   - **预训练权重**: 通过 `init_cfg=dict(type='Pretrained', checkpoint='s3://...')` 加载 backbone (示例: `regnetx_1.6gf`)。
   - **恢复训练**: `load_from = 's3://...'` 指向完整 checkpoint 路径 (`hv_pointpillars_secfpn_6x8_160e_kitti-3d-car_...pth`)。
   - **保存检查点**: `checkpoint_config = dict(interval=1, max_keep_ckpts=2, out_dir='s3://...')` 周期写盘并保留最近 2 个。
6. **`keep_local` 日志本地化策略**: `TextLoggerHook` 提供 `keep_local` 参数,默认保留本地日志 (`keep_local` 缺省即 True);设为 `False` 后会在备份到 Ceph 后**清理本地副本**,节省磁盘。
7. **EvalHook 与 DistEvalHook 的 best-ckpt 直写 Ceph**: `evaluation = dict(interval=1, save_best='bbox', out_dir='s3://...')` 让评估钩子在每个 eval 周期按 `bbox` 指标挑选最优权重并直写 Ceph,省去人工同步步骤。

---

## 【关键机制与数据】

- **后端选型机制 (原文)**: "We support different file client backends: Disk, Ceph and LMDB, etc." — 即文件 I/O 是一个可插拔后端,磁盘为默认,`petrel` 是 Ceph/S3 兼容协议下的客户端实现,LMDB 用于嵌入式键值高速缓存。
- **数据流 (原文,基于代码示例推导)**:
  - **训练数据流**: `train_pipeline` → `LoadPointsFromFile` (Ceph 拉 .bin 点云) → `LoadAnnotations3D` (Ceph 拉标注) → `ObjectSample` 通过 `db_sampler` 从 Ceph 拉 `kitti_dbinfos_train.pkl` 与对应 GT 点云 → 增广 → Collect。
  - **验证/测试数据流**: `test_pipeline` → `LoadPointsFromFile` (Ceph) → `MultiScaleFlipAug3D` 包裹 (含 `GlobalRotScaleTrans` / `RandomFlip3D` / `PointsRangeFilter`) → Collect。
- **训练时点云滤波参数 (原文)**: `point_cloud_range` 配合 `PointsRangeFilter` 与 `ObjectRangeFilter` 限定范围;`ObjectNoise` 的 `num_try=100`、`translation_std=[0.25, 0.25, 0.25]`、`rot_range=[-0.15707963267, 0.15707963267]` (≈ ±π/20);`GlobalRotScaleTrans` 的 `rot_range=[-0.78539816, 0.78539816]` (≈ ±π/4)、`scale_ratio_range=[0.95, 1.05]`;`RandomFlip3D` 的 `flip_ratio_bev_horizontal=0.5`。
- **MultiScaleFlipAug3D 参数 (原文)**: `img_scale=(1333, 800)`、`pts_scale_ratio=1`、`flip=False`。
- **RepeatDataset (原文)**: 训练配置 `type='RepeatDataset', times=2`,即一轮 epoch 内部对数据集重复 2 次采样。
- **工作流 (原文)**: `workflow = [('train', 1)]`,即 1 个 train 单元 + 1 个 val 单元交替 (由 mmcv 约定)。
- **检查点管理数值 (原文)**: `interval=1` (每 1 个 epoch 存一次)、`max_keep_ckpts=2` (最多保留 2 个本地/Ceph 副本)。
- **日志周期 (原文)**: `interval=50`,即每 50 个 iter 记录一次日志。
- **预训练样例 (原文)**: backbone 选 `regnetx_1.6gf`,路径 `s3://openmmlab/checkpoints/mmdetection3d/regnetx_1.6gf`。
- **示例 checkpoint 路径 (原文)**: `s3://openmmlab/checkpoints/mmdetection3d/v0.1.0_models/pointpillars/hv_pointpillars_secfpn_6x8_160e_kitti-3d-car/hv_pointpillars_secfpn_6x8_160e_kitti-3d-car_20200620_230614-77663cd6.pth` — 命名约定蕴含 `pointpillars`、6×8 batch、`160e` (160 epochs)、KITTI-3D-car 任务、时间戳与 hash 后缀 `77663cd6`。

---

## 【表格解读】

**原文无表格。**

(全部信息均以 Python 配置字典 + 注释形式给出,未出现 markdown 表格。)

---

## 【公式解读】

**原文无公式。**

(原文所有数值参数均以列表/字面量形式直接出现在配置 dict 中,例如 `translation_std=[0.25, 0.25, 0.25]`,未给出独立的数学公式或伪代码表达。)

---

## 【关联】

原文未提供任何内部链接 (`(无)`),但从内容上下文可推断以下关联关系 (基于原文配置出现的类名/模块名,非臆造新机制):

- **与数据层上游**: `LoadPointsFromFile` / `LoadAnnotations3D` / `db_sampler` (含 `LoadPointsFromFile` 子模块) — 这三者共享同一份 `file_client_args`,因此只要一处配置 Ceph 即可打通整个 nuScenes / KITTI 数据读取路径;`data_root` 仍是本地路径占位,但通过 `path_mapping` 将其解释为 Ceph URI。
- **与模型层**: `pts_backbone` 中 `init_cfg.checkpoint` 走 Ceph,意味着 backbone 预训练权重可独立于数据集放在 Ceph 上,与数据后端解耦。
- **与训练生命周期**: `load_from` (恢复) → `workflow` (train/val 调度) → `checkpoint_config` (周期保存) → `evaluation.save_best` (最优权重) → `log_config.hooks` (日志),构成训练→评估→落盘→日志的完整 Ceph 闭环。
- **与日志子系统**: `TextLoggerHook` 的 `out_dir` 决定 Ceph 日志路径,`keep_local` 决定是否双写本地;`interval=50` 与 mmcv 默认日志系统对齐。

---

## 【使用方法】

### 1. 数据与标注从 Ceph 加载

将原文给出的 `file_client_args` (含 `backend='petrel'` 与双键 `path_mapping`) 注入到三处:

- `train_pipeline` 中的 `LoadPointsFromFile` 与 `LoadAnnotations3D`;
- `db_sampler` 自身 + 其内部 `points_loader` 子字典;
- `data['train']`、`data['val']`、`data['test']` 三个数据集 dict。

用户须将 `path_mapping` 中 `s3://openmmlab/datasets/detection3d/nuscenes/` 与 `s3://openmmlab/checkpoints/...` 替换为**自己的 Ceph/S3 数据路径**。

### 2. 预训练 backbone 从 Ceph 加载

```python
init_cfg=dict(type='Pretrained', checkpoint='s3://<your-bucket>/<model-name>')
```

原文示例 backbone 为 `regnetx_1.6gf`。

### 3. 断点续训从 Ceph 加载

```python
load_from = 's3://<your-bucket>/path/to/checkpoint.pth'
resume_from = None   # 原文写法
workflow = [('train', 1)]
```

### 4. 检查点保存到 Ceph

```python
checkpoint_config = dict(interval=1, max_keep_ckpts=2, out_dir='s3://<your-bucket>/<ckpt-dir>')
```

每 1 个 epoch 保存一次,仅保留最近 2 个。

### 5. EvalHook 写最优权重到 Ceph

```python
evaluation = dict(interval=1, save_best='bbox', out_dir='s3://<your-bucket>/<best-ckpt-dir>')
```

按 `bbox` (3D 检测框) 指标挑选最优。

### 6. 训练日志备份到 Ceph

```python
log_config = dict(
    interval=50,
    hooks=[dict(type='TextLoggerHook', out_dir='s3://<your-bucket>/<log-dir>')])

# 备份后删除本地副本:
log_config = dict(
    interval=50,
    hooks=[dict(type='TextLoggerHook', out_dir='s3://<your-bucket>/<log-dir>', keep_local=False)])
```

**启用后端切换的总体步骤 (按原文推导)**:
1. 确认运行环境已安装 `petrel` 客户端 (mmcv 生态默认随 `mmcv-full` 提供);
2. 将所有相关 dict 中的 `file_client_args.backend` 设为 `'petrel'`,并按原文格式填好 `path_mapping`;
3. 把代码示例中所有 `s3://openmmlab/...` 占位 URI 替换为自有 bucket;
4. 保持磁盘 (Disk) 与 Ceph 路径的语义一致 (即 `path_mapping` 必须覆盖训练代码中可能出现的全部本地路径形态,包括 `./xxx/` 与 `xxx/` 两种写法);
5. 启动训练,框架将自动通过 `petrel` 在 Ceph 上读写数据/权重/日志,无需额外 CLI 参数。
