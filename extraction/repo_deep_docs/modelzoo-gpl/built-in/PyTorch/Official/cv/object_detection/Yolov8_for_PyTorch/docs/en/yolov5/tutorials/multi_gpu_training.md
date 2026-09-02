# On master machine 0

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/multi_gpu_training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/multi_gpu_training.md

# YOLOv5 多 GPU 训练文档深度解读

## 【定位】
这篇文档系统说明如何在单台或多台机器上,使用**多 GPU**训练 YOLOv5 模型,涵盖了从单卡 → `DataParallel` → `DistributedDataParallel` 三种模式的命令、注意事项以及在 AWS P4d + 8×A100 上的实测 DDP 性能基准。

## 【技术要点】

1. **环境前置条件**:Python ≥ 3.8.0、PyTorch ≥ 1.8(推荐 ≥ 1.9,因 `torch.distributed.run` 在 PyTorch ≥ 1.9 中替代了 `torch.distributed.launch`);多卡训练**强烈推荐 Docker Image**。
2. **三种训练模式**:
   - **Single GPU**:`python train.py --batch 64 --data coco.yaml --weights yolov5s.pt --device 0`
   - **Multi-GPU DataParallel**(`--device 0,1`)——文档明确标注 ⚠️ **不推荐**,因为"slow and barely speeds up training compared to using just 1 GPU"。
   - **Multi-GPU DistributedDataParallel(DDP)**——文档标注 ✅ **推荐**:`python -m torch.distributed.run --nproc_per_node 2 train.py --batch 64 --data coco.yaml --weights yolov5s.pt --device 0,1`
3. **Batch 切分规则**:`--batch` 是**总 batch-size**,会被均分到每个 GPU;例如 batch=64、2 卡 → 每卡 32;并且 `--batch` **必须是 GPU 数量的整数倍**。
4. **GPU 编号与设备选择**:默认使用 `0...(N-1)`;可通过 `--device 2,3` 指定特定卡(注意 DDP 示例此时通常配合 `--cfg yolov5s.yaml --weights ''` 从头训练)。
5. **DDP 进阶选项**:
   - **SyncBatchNorm**(`--sync-bn`):仅多卡 DDP 可用;会显著降低训练速度,**仅在每卡 batch ≤ 8 时推荐**使用,以提升精度。
   - **多机训练**:需指定 `--nnodes N --node_rank R --master_addr "192.168.1.1" --master_port 1234`,要求所有机器的代码与数据集一致且可互通;**所有 N 台机器都连上后训练才会开始**,仅 master 机器输出日志。
6. **隐含资源差异**:GPU 0 占用内存**稍多于**其他 GPU,因为它维护 EMA 并负责 checkpointing。

## 【关键机制与数据】

- **DDP 启动机制**:`torch.distributed.run`(原 `torch.distributed.launch`)在每节点启动 N 个进程协同工作,通过 `--master_addr` / `--master_port` 建立节点间通信,以 NCCL/GLOO 等后端同步梯度。
- **Batch 切分数据流**(原文):"`--batch` is the total batch-size. It will be divided evenly to each GPU. In the example above, it is 64/2=32 per GPU." 即 DDP 在数据加载侧已把数据切片并行喂给各卡。
- **Error 处理**:`RuntimeError: Address already in use` 时通过 `--master_port 1234` 切换端口即可解决。
- **实测性能数据**(原文:AWS EC2 P4d,8×A100 SXM4-40GB,YOLOv5l,1 个 COCO epoch,见下表)。

## 【表格解读】

**原文表格(逐字还原)**:

| GPUs<br>A100 | batch-size | CUDA_mem<br><sup>device0 (G) | COCO<br><sup>train | COCO<br><sup>val |
| ------------ | ---------- | ---------------------------- | ------------------ | ---------------- |
| 1x           | 16         | 26GB                         | 20:39              | 0:55             |
| 2x           | 32         | 26GB                         | 11:43              | 0:57             |
| 4x           | 64         | 26GB                         | 5:57               | 0:55             |
| 8x           | 128        | 26GB                         | 3:09               | 0:57             |

**逐行解读**:
- **1× A100(b=16)**: 单卡基线,训练 1 epoch 耗时 20 分 39 秒,验证 0:55;显存占用 26 GB(device0)。
- **2× A100(b=32)**: batch 翻倍均分,训练时间下降到 11:43(相对 1 卡**约 ~1.76× 加速**);验证几乎不变 0:57。
- **4× A100(b=64)**: 训练 5:57(相对 1 卡**约 ~3.47× 加速**);验证 0:55。
- **8× A100(b=128)**: 训练仅 3:09(相对 1 卡**约 ~6.56× 加速**);验证 0:57。
- **整体规律**:CUDA_mem(device0)始终保持 **26GB**,说明显存占用主要与模型/单卡 batch 相关,而与 GPU 总数弱相关;训练耗时随 GPU 数量近似线性下降但**逐渐呈现亚线性扩展**(8 卡未达理论 8× 加速),验证步骤耗时基本不变(因 val 不并行或并行开销与数据 IO 主导)。

## 【公式解读】

原文无 LaTeX 公式或严格数学公式。文中**唯一**的算术表达式为 `64/2=32 per GPU`(出现在 Multi-GPU DDP Mode 段落),这是一条**内联算术说明**,含义为:**总 batch-size ÷ GPU 数量 = 每卡实际 batch-size**;其作用是提示用户传入 `--batch` 时需按"总批大小"理解,而非"每卡批大小"。除了这一内联算式外,文档不包含其他公式。

## 【关联】

- **`../environments/docker_image_quickstart_tutorial.md`**:文档 ProTip 明确建议"**Docker Image** is recommended for all Multi-GPU trainings",并提供 Docker 镜像链接;`Profiling code` 段也使用 `sudo docker run -it --ipc=host --gpus all ...` 拉起容器作为性能测试前置环境。
- **`../environments/aws_quickstart_tutorial.md`**:Results 章节的 DDP profiling 直接在"**AWS EC2 P4d instance**"上完成,因此该教程是文档所引用硬件环境的部署/上手指南。
- **其他环境教程(未在文档正文中显式提及,但在内部链接列表中存在)**:`../environments/google_cloud_quickstart_tutorial.md`、`../environments/azureml_quickstart_tutorial.md` —— 在 FAQ 中"Have you tried in other environments listed in the 'Environments' section below?"间接指向了这些云环境,可作为多机/多卡部署时的备选平台。
- **上下游关系**:
  - 上游(模型/数据):本教程使用 `models/yolov5s.yaml`、`yolov5s.pt`、`data/coco.yaml` 等标准入口,前置依赖 `requirements.txt`、YOLOv5 最新 release。
  - 横向(PyTorch 分布式 API):依赖 PyTorch 原生的 `torch.nn.DataParallel`、`torch.nn.parallel.DistributedDataParallel`、`torch.nn.SyncBatchNorm` 以及启动器 `torch.distributed.run`。
  - 下游(本教程延伸):FAQ 中的 Checklist 引导用户回到 README/Docker/Cloud 教程排查问题。

## 【使用方法】

**启用方式(原文逐字保留命令)**:

1. **单卡训练**(基准):
   ```bash
   python train.py --batch 64 --data coco.yaml --weights yolov5s.pt --device 0
   ```

2. **多卡 DataParallel(⚠️ 不推荐)**:
   ```bash
   python train.py --batch 64 --data coco.yaml --weights yolov5s.pt --device 0,1
   ```

3. **多卡 DDP(✅ 推荐)**:
   ```bash
   python -m torch.distributed.run --nproc_per_node 2 train.py --batch 64 --data coco.yaml --weights yolov5s.pt --device 0,1
   ```

4. **指定特定 GPU(例如只用 2、3 号卡)**:
   ```bash
   python -m torch.distributed.run --nproc_per_node 2 train.py --batch 64 --data coco.yaml --cfg yolov5s.yaml --weights '' --device 2,3
   ```

5. **启用 SyncBatchNorm**(仅在每卡 batch ≤ 8 时考虑):
   ```bash
   python -m torch.distributed.run --nproc_per_node 2 train.py --batch 64 --data coco.yaml --cfg yolov5s.yaml --weights '' --sync-bn
   ```

6. **多机 DDP — master 机(R=0)**:
   ```bash
   python -m torch.distributed.run --nproc_per_node G --nnodes N --node_rank 0 --master_addr "192.168.1.1" --master_port 1234 train.py --batch 64 --data coco.yaml --cfg yolov5s.yaml --weights ''
   ```

7. **多机 DDP — 其它机器(R=1...N-1)**:
   ```bash
   python -m torch.distributed.run --nproc_per_node G --nnodes N --node_rank R --master_addr "192.168.1.1" --master_port 1234 train.py --batch 64 --data coco.yaml --cfg yolov5s.yaml --weights ''
   ```

8. **端口冲突时切换端口**:
   ```bash
   python -m torch.distributed.run --master_port 1234 --nproc_per_node 2 ...
   ```

**关键配置项一览(原文出现)**:
- `--nproc_per_node G`:每节点 GPU 数。
- `--batch`:总 batch-size,必须是 GPU 数的整数倍。
- `--device <ids>`:使用的 GPU 列表(支持 `0,1` 或 `2,3` 等任意子集)。
- `--sync-bn`:开启跨卡同步 BatchNorm。
- `--cfg yolov5s.yaml` + `--weights ''`:从零开始训练的搭配(在指定特定卡示例中出现)。
- `--nnodes N --node_rank R --master_addr --master_port`:多机训练所需的拓扑与通信参数。
- `--master_port`:解决 `Address already in use` 错误时改用其他端口。
- **平台要求**:Linux(推荐),Windows 未测试;Python ≥ 3.8.0;PyTorch ≥ 1.8(分布式启动器相关项 ≥ 1.9)。
