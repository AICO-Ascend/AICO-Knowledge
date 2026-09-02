# ClearML Integration

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/clearml_logging_integration.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/clearml_logging_integration.md

# ClearML Integration 文档深度解读

## 【定位】

这篇文档解决"如何将 ClearML（一款开源 ML 工具箱）与 YOLOv5 训练流程集成，从而获得实验追踪、数据版本管理、超参优化和远程执行能力"的问题，是 YOLOv5 调用 ClearML 能力的官方集成指南。

## 【技术要点】

1. **ClearML 五大核心能力**：(1) 实验管理器追踪每次 YOLOv5 训练；(2) 集成数据版本工具对训练数据进行版本化；(3) 通过 ClearML Agent 远程训练与监控；(4) 通过 ClearML 超参优化获得最佳 mAP；(5) 通过 ClearML Serving 将训练好的 YOLOv5 模型快速转为 API。

2. **环境安装与接入**：通过 `pip install clearml` 安装 Python 包后，使用 `clearml-init` 命令将 SDK 接入服务（Hosted Service 或自建 Server 均可）。

3. **YOLOv5 训练追踪自动启用**：安装 `clearml>=1.2.0` 后，与 YOLOv5 训练脚本（`train.py`）自动集成，无需额外代码改动；默认 `project_name=YOLOv5`、`task_name=Training`，可通过 `--project` / `--name` 参数覆盖；注意 ClearML 使用 `/` 作为子项目分隔符。

4. **追踪内容范围**：源代码 + 未提交改动、安装包列表、(超)参数、模型检查点（`--save-period n` 控制每 n 个 epoch 保存一次）、控制台输出、标量（mAP_0.5、mAP_0.5:0.95、precision、recall、losses、learning rates）、机器/运行时间等基本信息、label correlogram 和 confusion matrix 等图表、每 epoch 带边界框的图像、每 epoch 的 mosaic 图、每 epoch 的验证图。

5. **数据集版本管理协议**：YOLOv5 仓库支持传入数据集版本 ID，自动按需拉取；YAML 文件需拷贝至数据集根目录；YAML 必备字段为 `path`、`train`、`test`、`val`、`nc`、`names`；上传命令支持短命令 `clearml-data sync --project YOLOv5 --name coco128 --folder .` 或长命令链 `clearml-data create` → `clearml-data add --files .` → `clearml-data close`（后者可选 `--parent <parent_dataset_id>` 实现增量复用）。

6. **超参优化与远程执行机制**：ClearML 利用已记录的代码、包与环境信息，使实验完全可复现；HPO 通过克隆模板任务并修改超参实现；提供预设脚本 `utils/loggers/clearml/hpo.py`，可用 Optuna（`pip install optuna`）或 RandomSearch；通过在脚本中将 `task.execute_locally()` 改为 `task.execute()` 即可让 ClearML Agent 从队列中远程拉取执行。

## 【关键机制与数据】

- **数据流（追踪方向）**：`train.py` → ClearML SDK（`clearml>=1.2.0`） → ClearML Server/Hosted Service → Web UI 展示。原文："Every training run from now on, will be captured and stored by the ClearML experiment manager."

- **数据集接入数据流**：本地 `coco128/` 文件夹 → `clearml-data sync`（或 create/add/close 三段式） → ClearML 数据集版本（带 ID） → `python train.py --data clearml://<your_dataset_id>` 引用。原文："this repository supports supplying a dataset version ID, and it will make sure to get the data if it's not there yet. Next to that, this workflow also saves the used dataset ID as part of the task parameters."

- **可复现性机制**：每次实验记录的 metadata 包括源代码 + 未提交改动 + 已安装包 + 环境详情，使实验可在另一台机器完整重建。原文："Using the code information, installed packages and environment details, the experiment itself is now **completely reproducible**."

- **HPO 原理**：克隆已有实验（template task），修改超参后自动重跑，本质为 ClearML 实验的可复现 + 参数改写能力的组合。原文："ClearML allows you to clone an experiment and even change its parameters... this is basically what HPO does."

- **远程执行原理**：每个被记录的实验包含足够元信息（installed packages、uncommitted changes 等），ClearML Agent 监听队列、克隆并重建环境后执行任务。原文："every experiment tracked by the experiment manager contains enough information to reproduce it on a different machine (installed packages, uncommitted changes etc.). So a ClearML agent does just that: it listens to a queue for incoming tasks and when it finds one, it recreates the environment and runs it."

- **默认目录结构**（原文）：
  ```
  ..
  |_ yolov5
  |_ datasets
      |_ coco128
          |_ images
          |_ labels
          |_ LICENSE
          |_ README.txt
  ```
  拷贝 YAML 至数据集根后：
  ```
  ..
  |_ yolov5
  |_ datasets
      |_ coco128
          |_ images
          |_ labels
          |_ coco128.yaml  # <---- HERE!
          |_ LICENSE
          |_ README.txt
  ```

- **性能/数字指标**：原文未给出具体训练时长、加速比、显存占用等量化数据；仅出现训练超参示例值：`--img 640 --batch 16 --epochs 3`、`--weights yolov5s.pt`，HPO 需先 `pip install optuna`。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **与 YOLOv5 训练脚本的关联**：依赖 `train.py` 与 `--project`、`--name`、`--save-period`、`--cache`、`--img`、`--batch`、`--epochs`、`--data`、`--weights` 等参数；YAML 数据集配置（`coco8.yaml`、`coco128.yaml`）是其上游输入。
- **与 HPO 子模块的关联**：`utils/loggers/clearml/hpo.py` 是 YOLOv5 仓库内置脚本，需填入 template task 的 ID 后运行；与第三方优化器 Optuna 配套使用（可选）。
- **与远程执行子系统的关联**：通过 `task.execute()` 将 HPO 任务下发至 ClearML Agent 队列，构成 HPO → Remote Execution 的串联调用链。
- **与 ClearML 服务端组件的关系**：Hosted Service（`clear.ml`）或自建 Server 是所有能力（实验管理、数据版本、HPO、Agent、Serving）共同的后端基础。
- **与产物可视化的关联**：依托 Ultralytics 文档仓库中的截图资源（`clearml-scalars-dashboard.avif`、`clearml-dataset-interface.avif`、`hpo-clearml-experiment.avif`）辅助说明。
- **关联链接信息**：原文未提供内部链接（已标注「无」）。

## 【使用方法】

**1) 服务端准备（任选其一）：**
- 注册 [ClearML Hosted Service](https://clear.ml/) 免费账号；
- 或自建 Server（[部署文档](https://clear.ml/docs/latest/docs/deploying_clearml/clearml_server)）。

**2) 安装与凭证配置：**
```bash
pip install clearml
clearml-init
```
凭证获取路径：Settings → Workspace → Create new credentials。

**3) 训练并自动追踪：**
```bash
pip install clearml>=1.2.0
python train.py --img 640 --batch 16 --epochs 3 --data coco8.yaml --weights yolov5s.pt --cache
```
自定义项目与任务名：
```bash
python train.py --project my_project --name my_training --img 640 --batch 16 --epochs 3 --data coco8.yaml --weights yolov5s.pt --cache
```

**4) 数据集版本化：**
- 将 YAML 文件拷贝至数据集根目录，确保含 `path`、`train`、`test`、`val`、`nc`、`names` 键；
- 上传（短命令）：
```bash
cd coco128
clearml-data sync --project YOLOv5 --name coco128 --folder .
```
- 上传（等价长命令链，可选 `--parent <parent_dataset_id>` 复用父版本）：
```bash
clearml-data create --name coco128 --project YOLOv5
clearml-data add --files .
clearml-data close
```
- 用 ClearML 数据集训练：
```bash
python train.py --img 640 --batch 16 --epochs 3 --data clearml://<your_dataset_id> --weights yolov5s.pt --cache
```

**5) 超参优化：**
```bash
pip install optuna
python utils/loggers/clearml/hpo.py
```
需先在 `utils/loggers/clearml/hpo.py` 中填入 template task 的 ID；将 `task.execute_locally()` 改为 `task.execute()` 可切换为远程队列执行。

**6) 远程执行（高级）：**
- 部署并启动 ClearML Agent（参考 [YouTube 视频](https://youtu.be/MX3BrXnaULs) 与 [Agent 文档](https://clear.ml/docs/latest/docs/clearml_agent)）；
- 将训练/HPO 任务以 `task.execute()` 提交至队列，Agent 会自动拉取、重建环境并运行。
