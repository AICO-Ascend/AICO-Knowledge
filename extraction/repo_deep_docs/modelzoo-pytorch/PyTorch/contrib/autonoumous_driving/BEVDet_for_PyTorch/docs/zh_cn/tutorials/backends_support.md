# 教程 7: 后端支持

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/backends_support.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/backends_support.md

# 一体化深度解读:BEVDet 后端支持 (Backend Support) 教程

---

## 【定位】

本教程阐述 BEVDet (PyTorch 版本) 在 MMDetection3D 框架下如何配置 **多文件客户端后端** —— 特别是通过 `petrel` 后端把训练/推理的**数据、标注、预训练模型、检查点、最优权重、训练日志**全部接入 Ceph (S3 兼容) 存储,使原本依赖本地磁盘的流水线可以无缝运行在分布式对象存储之上。

---

## 【技术要点】

1. **统一后端选择**:通过 `file_client_args = dict(backend='petrel', path_mapping=...)` 把后端切到 petrel (Ceph/S3 客户端),并用 `path_mapping` 做本地路径到 `s3://openmmlab/...` 的前缀映射。
2. **数据/标注读取**:`path_mapping` 同时映射两条规则,分别覆盖 `'./data/nuscenes/'` 与 `'data/nuscenes/'` 两种相对写法,把数据目录、`.pkl` (如 `kitti_dbinfos_train.pkl`)、`.json` 标注都指向 Ceph。
3. **全链路注入 `file_client_args`**:`db_sampler` 内部 `points_loader`、`LoadPointsFromFile`、`LoadAnnotations3D`、`train/val/test` 顶层 `dataset` 都要显式传入同一份 `file_client_args`,否则部分子模块会回落到本地默认后端。
4. **预训练与权重热加载**:`init_cfg.checkpoint` 直接写成 `s3://...`;`load_from = 's3://...hv_pointpillars_secfpn_6x8_160e_kitti-3d-car_20200620_230614-77663cd6.pth'`,无需预先下载到本地。
5. **Ceph 端检查点保存**:`checkpoint_config = dict(interval=1, max_keep_ckpts=2, out_dir='s3://openmmlab/mmdetection3d')`,即每个 epoch (`interval=1`) 写一次,本地最多保留 2 份,主目录在 Ceph。
6. **最优权重与日志**:`evaluation = dict(interval=1, save_best='bbox', out_dir='s3://openmmlab/mmdetection3d')` 在验证时把 `bbox` 指标最优权重写到 Ceph;`log_config` 的 `TextLoggerHook` 用 `out_dir='s3://openmmlab/mmdetection3d'`,并可通过 `keep_local=False` 在备份后删除本地日志。

---

## 【关键机制与数据】

**工作原理 / 数据流**(原文综合):

- 文件客户端采用**单例 + 注册表**模式:在配置最外层实例化一次 `file_client_args`,随后在 `LoadPointsFromFile`、`LoadAnnotations3D`、`db_sampler.points_loader`、`dataset` 等多处复用,实现"同一份参数驱动所有 I/O 行为"。
- `path_mapping` 的语义是**前缀替换**:`'./data/nuscenes/' → 's3://openmmlab/datasets/detection3d/nuscenes/'` 与 `'data/nuscenes/' → s3://openmmlab/datasets/detection3d/nuscenes/'` 同时存在,是为兼容代码库中两套相对路径写法。
- 数据流(以训练为例):`train_pipeline` 中 `LoadPointsFromFile` 通过 `file_client_args` 去 Ceph 取点云 → `LoadAnnotations3D` 取 3D 框与标签 → `ObjectSample` 借助 `db_sampler.file_client_args` 从 Ceph 取 `kitti_dbinfos_train.pkl` 做 GT 库采样 → 后续增广 / 收集走本地内存。
- 权重 / 日志流:`model.init_cfg.checkpoint` / `load_from` 直接指向 Ceph 上的 `.pth`;`runner` 每 `interval=1` 个 epoch 触发 `checkpoint_config` 把权重序列化写入 Ceph;`EvalHook` 每 `interval=1` 次评估比对 `bbox` 指标,把最优单独再写一份;`TextLoggerHook` 每 `interval=50` 个迭代写日志。

**关键配置数字(原文出现)**:
- `rate=1.0`(db 采样倍率,原文 `db_sampler` 中);
- `sample_groups=dict(Car=15)`(Car 类每次采样 15 个样本,原文);
- `translation_std=[0.25, 0.25, 0.25]`(ObjectNoise 平移噪声,原文);
- `rot_range=[-0.15707963267, 0.15707963267]`(≈ ±π/20,ObjectNoise 旋转,原文);
- `flip_ratio_bev_horizontal=0.5`(RandomFlip3D 翻转概率,原文);
- `rot_range=[-0.78539816, 0.78539816]`(≈ ±π/4,GlobalRotScaleTrans 旋转,原文);
- `scale_ratio_range=[0.95, 1.05]`(缩放范围,原文);
- `pts_scale_ratio=1`、`img_scale=(1333, 800)`(测试多尺度增强,原文);
- `interval=1`、`max_keep_ckpts=2`(checkpoint_config);
- `interval=50`(log_config 写盘频率);
- `times=2`(`RepeatDataset` 重复 2 轮)。

> 说明:上述数字仅是文档中**配置示例**给出的值,并非性能指标;原文未提供任何训练/推理吞吐或精度数据。

---

## 【表格解读】

**原文无表格。**(整篇教程由 6 个 Python 配置代码片段组成,不含任何 markdown / HTML 表格。)

---

## 【公式解读】

**原文无公式。**(文档全部为 Python 字典式配置,未出现任何数学公式或伪代码。)

---

## 【关联】

- **与 MMDetection3D 生态的关系**:本文给出的 `LoadPointsFromFile`、`LoadAnnotations3D`、`ObjectSample`、`GlobalRotScaleTrans`、`PointsRangeFilter`、`ObjectRangeFilter`、`DefaultFormatBundle3D`、`Collect3D`、`MultiScaleFlipAug3D`、`RepeatDataset`、`EvalHook`、`TextLoggerHook` 等组件,均来自 MMDetection3D/MMCV 体系;BEVDet 在此基础上**仅做文件后端的替换**即可获得 Ceph 支持,说明后端切换对算法逻辑透明。
- **与 BEVDet 模型的耦合点**:
  - `pts_backbone` 在示例中被 `_delete_=True` 后重建为 `NoStemRegNet`(arch=`regnetx_1.6gf`),并通过 `init_cfg.checkpoint` 从 Ceph 加载 RegNet 预训练权重 —— 这是 BEVDet 论文中"以 ImageNet 预训练 RegNet 作为图像骨干 / 点云分支参数初始化"的可复现路径。
  - 检查点保存位置 (`out_dir='s3://openmmlab/mmdetection3d'`) 与 `load_from` 的 Ceph 路径呼应,意味着模型迭代(从预训练 → 微调 → 续训)全程可在 Ceph 闭环,不需要任何本地落盘。
- **与流水线上下文的依赖**:`train_pipeline` 的数据加载依赖 `point_cloud_range`、`class_names`、`data_root` 等外部变量;本教程默认这些变量在调用该配置片段的 Python 入口已被定义,文档本身未给出其定义。
- **文档所在仓库位置**:文件位于 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/backends_support.md`,是 BEVDet_for_PyTorch tutorials 目录中的一篇;文末标注"内部链接:(无)",即该页未再交叉指向其他 tutorial。

---

## 【使用方法】

### 1) 启用 Ceph 作为文件后端

```python
file_client_args = dict(
    backend='petrel',
    path_mapping=dict({
        './data/nuscenes/': 's3://openmmlab/datasets/detection3d/nuscenes/',
        'data/nuscenes/' : 's3://openmmlab/datasets/detection3d/nuscenes/',
    }))
```
> 把占位 `s3://openmmlab/datasets/detection3d/nuscenes/` 替换为用户自己的 Ceph 桶路径。

### 2) 在 db_sampler 与 train/val/test pipeline 中注入

- `db_sampler.points_loader.file_client_args = file_client_args`
- `db_sampler.file_client_args = file_client_args`
- `train_pipeline` 中每个 `LoadPointsFromFile` / `LoadAnnotations3D` 都要加 `file_client_args=file_client_args`
- `test_pipeline` 中 `LoadPointsFromFile` 同理
- `data.train.dataset` / `data.val` / `data.test` 三处 `file_client_args=file_client_args`

### 3) 从 Ceph 加载预训练 / 续训权重

```python
# 预训练骨干
init_cfg=dict(type='Pretrained', checkpoint='s3://openmmlab/checkpoints/mmdetection3d/regnetx_1.6gf')

# 完整检查点续训
load_from = 's3://openmmlab/checkpoints/mmdetection3d/v0.1.0_models/pointpillars/hv_pointpillars_secfpn_6x8_160e_kitti-3d-car/hv_pointpillars_secfpn_6x8_160e_kitti-3d-car_20200620_230614-77663cd6.pth'
resume_from = None
workflow = [('train', 1)]
```

### 4) 把检查点 / 最优权重 / 日志写到 Ceph

```python
checkpoint_config = dict(interval=1, max_keep_ckpts=2, out_dir='s3://openmmlab/mmdetection3d')
evaluation       = dict(interval=1, save_best='bbox', out_dir='s3://openmmlab/mmdetection3d')
log_config       = dict(interval=50, hooks=[dict(type='TextLoggerHook', out_dir='s3://openmmlab/mmdetection3d', keep_local=False)])
```
其中 `save_best='bbox'` 表示按 `bbox` 指标选最优;`keep_local=False` 表示备份到 Ceph 后删除本地日志副本(若需保留本地副本则置 `True` 或省略)。

> **原文未涉及**的内容包括:如何在不安装 petrel 库的纯磁盘环境下回退、`backend` 字段除 `'petrel'` 外的可选值 (如 `'ceph'`、`'memcached'`、`'lmdb'` 在引言中提及但正文未给出示例) 的具体配置、以及权限 / 凭证配置方式。
