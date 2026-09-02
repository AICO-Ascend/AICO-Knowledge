# YOLO11 🚀 on AzureML

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/azureml-quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/azureml-quickstart.md

# 一体化深度解读：YOLO11 🚀 on AzureML

## 【定位】

这篇文档是 Ultralytics YOLO11 在 Microsoft Azure Machine Learning (AzureML) 云平台上的 **快速上手指南 (quickstart)**，向数据科学家和开发者说明如何在 AzureML 工作区中创建算力实例、搭建 Conda 环境、安装 ultralytics/onnx 依赖，并通过**终端 (CLI)** 或 **Notebook (Python SDK)** 两种方式完成 YOLO11 的预测与训练任务，从而把本地/单机工作流迁移到云端以获得弹性算力和 MLOps 能力。

---

## 【技术要点】

1. **AzureML 工作区前置条件**：必须先在 Azure 中拥有一个 AzureML workspace，作为管理所有 AzureML 资源（算力、数据、模型、实验）的中心化入口（参见微软官方文档 `concept-workspace`）。
2. **创建算力实例 (Compute Instance)**：在 AzureML workspace 中通过 `Compute > Compute instances > New` 选择资源规格新建计算实例，作为后续运行命令的载体。
3. **Conda 虚拟环境 (`yolo11env`)**：在算力实例的终端中通过 `conda create --name yolo11env -y` → `conda activate yolo11env` → `conda install pip -y` 三步创建并激活环境；Notebook 场景还需额外安装 `ipykernel` 并注册 `python -m ipykernel install --user --name yolo11env --display-name "yolo11env"`。
4. **依赖安装固定版本**：进入 `ultralytics` 目录后依次 `pip install -r requirements.txt` → `pip install ultralytics` → `pip install onnx>=1.12.0`，其中 ONNX 版本被显式锁定在 **1.12.0 及以上**。
5. **CLI 训练参数组合**：示例命令 `yolo train data=coco8.yaml model=yolo11n.pt epochs=10 lr0=0.01`——使用 `coco8.yaml` 数据集、`yolo11n.pt` 预训练权重、训练 **10 epochs**、初始学习率 **0.01**。
6. **CLI 预测示例**：命令 `yolo predict model=yolo11n.pt source='https://ultralytics.com/images/bus.jpg'`，使用 Ultralytics 官方示例图片 `bus.jpg` 作为远程数据源进行推理。
7. **Python SDK 工作流（Notebook 中）**：四步操作链——`YOLO("yolo11n.pt")` 加载模型 → `model.train(data="coco8.yaml", epochs=3)` 训练（注意 Notebook 示例的 epochs=3 与 CLI 示例的 epochs=10 不同） → `model.val()` 在验证集评估 → `model("...")` 推理 → `model.export(format="onnx")` 导出 ONNX。
8. **Notebook 中 `%%bash` cell 必须 `source activate yolo11env`**：以确保 Jupyter 的每个 bash 子进程都进入同一个 Conda 环境，避免依赖错位。

---

## 【关键机制与数据】

**AzureML 对 YOLO 用户的核心价值链（原文逐条表述）**：

- 易于管理用于训练的大型**数据集和算力资源**；
- 利用 AzureML 内置工具进行**数据预处理、特征选择、模型训练**；
- 通过 MLOps 能力更高效地**协作**，包括但不限于对**模型和数据的监控 (monitoring)、审计 (auditing)、版本管理 (versioning)**。

**工作流数据流（按"工作区→算力→环境→依赖→任务"链路）**：

1. 入口：AzureML workspace（中心化资源管理）；
2. 算力：Compute instance（云端 VM）；
3. 入口方式二选一：Terminal（CLI）或 Notebook（IPython kernel）；
4. 环境隔离：conda env `yolo11env`；
5. 依赖：`requirements.txt` + `ultralytics` + `onnx>=1.12.0`；
6. 任务调用：CLI（`yolo predict/train`）或 Python（`ultralytics.YOLO`）；
7. 产物：训练好的 `.pt` 权重、验证 `metrics`、预测结果、可导出的 ONNX 模型。

**原文出现的具体数字/标识（全部为原文直接给出的）**：
- 环境名：`yolo11env`
- CLI 训练：`epochs=10`，`lr0=0.01`，`data=coco8.yaml`，`model=yolo11n.pt`
- Notebook 训练：`epochs=3`（注意此处与终端不同）
- ONNX 版本约束：`>=1.12.0`
- 远程图片：`https://ultralytics.com/images/bus.jpg`

---

## 【表格解读】

**原文无表格**。整篇文档仅以标题、段落、图片和代码块形式组织内容，未包含任何参数表、性能对比表或配置矩阵。

---

## 【公式解读】

**原文无公式**。文档不涉及任何 LaTeX 表达式、数学公式或伪代码算法。

---

## 【关联】

文档中明示的**内部链接**（位于 quickstart 指南中）将本文与 Ultralytics 通用快速上手文档建立了以下耦合关系：

| 内部链接锚点 | 在本文中出现的位置 | 作用 |
|---|---|---|
| `../quickstart.md#use-ultralytics-with-cli` | "Quickstart from Terminal" 末尾（命令 `yolo train ...` 之后） | 引导读者查阅 Ultralytics CLI 通用用法 |
| `../quickstart.md#use-ultralytics-with-cli` | "Quickstart from a Notebook" 的预测示例后 | Notebook 中运行 CLI 预测时跳转到 CLI 详细文档 |
| `../quickstart.md#use-ultralytics-with-python` | "Quickstart from a Notebook" 的 Python 训练示例旁 | 引导读者查阅 Ultralytics Python SDK 通用用法 |
| `../quickstart.md#use-ultralytics-with-cli` | FAQ "How do I run YOLO11 on AzureML..." 末尾 | 再次指向 CLI 详细用法作为补充参考 |
| `../quickstart.md#use-ultralytics-with-cli` | 同上 FAQ 中提到 "more details" 的引用 | 复用同一锚点提供延伸阅读 |

**下游关联模块**：依赖 `ultralytics` 包（提供 `YOLO` 类、`yolo` CLI、`.pt` 权重如 `yolo11n.pt`）以及 ONNX（导出格式 `format="onnx"`），并向上衔接 AzureML 官方文档中的 `Data Asset`、`Job`、`Model Register` 等高级 MLOps 能力（即文末"Explore More with AzureML"小节中的 5 条外部链接）。

---

## 【使用方法】

> 以下命令均**逐字摘自原文**，未做任何改写或补充。

### ① 创建并激活 Conda 环境（Terminal 路径）
```bash
conda create --name yolo11env -y
conda activate yolo11env
conda install pip -y
```

### ② 安装依赖（Terminal 路径）
```bash
cd ultralytics
pip install -r requirements.txt
pip install ultralytics
pip install onnx>=1.12.0
```

### ③ CLI 推理
```bash
yolo predict model=yolo11n.pt source='https://ultralytics.com/images/bus.jpg'
```

### ④ CLI 训练
```bash
yolo train data=coco8.yaml model=yolo11n.pt epochs=10 lr0=0.01
```

### ⑤ Notebook 路径：创建 IPython kernel
```bash
conda create --name yolo11env -y
conda activate yolo11env
conda install pip -y
conda install ipykernel -y
python -m ipykernel install --user --name yolo11env --display-name "yolo11env"
```

### ⑥ Notebook 路径：在 `%%bash` cell 中安装依赖
```bash
%%bash
source activate yolo11env
cd ultralytics
pip install -r requirements.txt
pip install ultralytics
pip install onnx>=1.12.0
```

### ⑦ Notebook 路径：在 `%%bash` cell 中运行 CLI 推理
```bash
%%bash
source activate yolo11env
yolo predict model=yolo11n.pt source='https://ultralytics.com/images/bus.jpg'
```

### ⑧ Notebook 路径：Python SDK 端到端任务（train → val → predict → export）
```python
from ultralytics

# Load a model
model = YOLO("yolo11n.pt")  # load an official YOLO11n model

# Use the model
model.train(data="coco8.yaml", epochs=3)  # train the model
metrics = model.val()  # evaluate model performance on the validation set
results = model("https://ultralytics.com/images/bus.jpg")  # predict on an image
path = model.export(format="onnx")  # export the model to ONNX format
```

### ⑨ 关键配置项汇总（原文出现的字段名）
- `model`：权重路径，示例值 `yolo11n.pt`；
- `source`：推理输入（URL/文件/视频均可，示例为远程 jpg URL）；
- `data`：数据集 yaml，示例值 `coco8.yaml`；
- `epochs`：训练轮数，原文同时给出 `10`（CLI）和 `3`（Python）两个不同示例值；
- `lr0`：初始学习率，示例值 `0.01`；
- `format`：导出格式，示例值 `"onnx"`。

> 提醒：原文未涉及 GPU 选择、batch size、image size、AzureML 配额/VM SKU、`az ml` CLI、AzureML Python SDK 的 `MLClient/Job/Environment` 等具体配置——这些属于文末"Explore More"小节所链接的外部高级文档范畴，本文未展开。
