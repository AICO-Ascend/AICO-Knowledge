# YOLOv5 with Comet

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/comet_logging_integration.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/comet_logging_integration.md

# YOLOv5 + Comet 集成 Guide 深度解读

## 【定位】
这篇文档是 YOLOv5 与 Comet ML 实验追踪平台的对接指南,系统化地描述如何把 YOLOv5 训练过程中的**指标、超参数、可视化、预测样本、模型检查点与数据集资产**自动上报到 Comet,从而实现训练流程的可追踪、可复现与团队协作。

---

## 【技术要点】

1. **安装与凭据配置**:通过 `pip install comet_ml` 安装;凭据可走两条路——环境变量 (`COMET_API_KEY`、`COMET_PROJECT_NAME`,后者默认 `yolov5`) 或在工作目录创建 `.comet.config` 文件 (`[comet]` 段下设 `api_key` 与 `project_name`)。
2. **一行训练即接入**:`python train.py --img 640 --batch 16 --epochs 5 --data coco128.yaml --weights yolov5s.pt` 即触发自动上报,无需改动训练脚本源码。
3. **自动上报三件套**:Metrics(训练/验证的 Box/Object/Classification Loss,验证的 mAP_0.5、mAP_0.5:0.95、Precision、Recall)、Parameters(模型超参 + 命令行参数)、Visualizations(验证集混淆矩阵、所有类别的 PR 曲线与 F1 曲线、类别标签 Correlogram)。
4. **环境变量细粒度控制**:原文列出 8 个 `COMET_*` 变量,各自带默认值——`COMET_MODE=online`、`COMET_MODEL_NAME=yolov5`、`COMET_LOG_CONFUSION_MATRIX=true`、`COMET_MAX_IMAGE_UPLOADS=100`、`COMET_LOG_PER_CLASS_METRICS=false`、`COMET_DEFAULT_CHECKPOINT_FILENAME=last.pt`、`COMET_LOG_BATCH_LEVEL_METRICS=false`、`COMET_LOG_PREDICTIONS=true`。
5. **检查点与预测样本上报**:Checkpoint 上报默认关闭,需通过 `train.py --save-period N` 启用(N 即保存周期);预测样本默认开启,可通过 `train.py --bbox_interval N` 控制"每 N 个 batch 上报一次",并使用 Comet 的 Object Detection Custom Panel 可视化。
6. **数据集资产化**:通过 `train.py --upload_dataset` 把数据上传到 Comet Artifacts,版本化且自动写入 `yaml` 元数据;消费侧把 `yaml` 的 `path` 字段写成 `comet://<workspace>/<artifact>:<version or alias>` 即可直接拉取。

---

## 【关键机制与数据】

- **数据流(原文)**:YOLOv5 训练脚本 → 内部已封装的 Comet 回调 → `comet_ml` SDK → Comet 后端 (online mode) / 本地离线缓存 (offline mode)。用户在 Comet UI 中查看图表、混淆矩阵、PR/F1、预测图像、Artifact 版本与实验血缘。
- **预测采样频率(原文)**:`bbox_interval` 对应 "every Nth batch of data per epoch";示例 `--bbox_interval 2` 表示每个 epoch 内每 2 个 batch 上报一次预测。文档明确提示 **YOLOv5 验证 dataloader 的默认 batch size 为 32**,因此设置 logging 频率时需要据此对齐。
- **图像上限(原文)**:默认最多上传 100 张验证图像;通过 `COMET_MAX_IMAGE_UPLOADS=200` 等数值可上调/下调。
- **Checkpoint(原文)**:`--save-period 1` 表示每 1 个 epoch 把 checkpoint 上报 Comet,默认行为是**不上报 checkpoint**。
- **类级别指标(原文)**:`COMET_LOG_PER_CLASS_METRICS=true` 时,会在训练结束时按类别记录 mAP、Precision、Recall、f1,默认关闭。
- **Batch 级指标(原文)**:`COMET_LOG_BATCH_LEVEL_METRICS=true` 时记录每个 batch 的训练指标,默认关闭。
- **指标内容(原文)**:Box Loss、Object Loss、Classification Loss 在 train 与 validation 上;mAP_0.5、mAP_0.5:0.95、Precision、Recall 仅在 validation 上。
- **可视化内容(原文)**:验证集预测的 Confusion Matrix、所有类别的 PR 与 F1 曲线、Class Labels 的 Correlogram。
- **Artifact 寻址格式(原文)**:`comet://<workspace name>/<artifact name>:<artifact version or alias>`,直接写到数据集 `yaml` 的 `path` 字段。

> 原文未给出具体数值型性能数据(如 mAP 数值、吞吐量、显存占用等),也未涉及 Comet 后端存储规模/速率指标。

---

## 【表格解读】

原文无表格(整篇文档以代码块、列表、命令行片段为主,未呈现参数表/性能对比表/配置矩阵)。

---

## 【公式解读】

原文无公式(文档聚焦工具集成与配置,未涉及任何损失函数、IoU、NMS 等数学表达式)。

---

## 【关联】

- **`train_custom_data.md`(文末/正文内部链接)**:在「Uploading a Dataset to Comet Artifacts」一节中明确指出,要被上传的数据集必须按 `train_custom_data.md` 所描述的方式组织,且 `yaml` 必须与 `coco128.yaml` 同构。这意味着 Comet 集成以 YOLOv5 既定的数据集目录约定为前置契约,二者形成"数据结构 → 资产化"的上下游关系。
- **上游依赖**:`comet_ml` Python SDK(`pip install comet_ml`)、Comet 账户与 API Key、YOLOv5 `train.py` 入口脚本。
- **下游消费**:Comet UI 的 Experiment 视图、Custom Panels(Object Detection 可视化 Panel)、Artifacts Tab、实验血缘图。
- **运行时协作**:与 YOLOv5 既有的命令行参数体系(`--img`、`--batch`、`--epochs`、`--data`、`--weights`、`--save-period`、`--bbox_interval`、`--upload_dataset`)深度耦合,Comet 仅以"附加观测层"的形式存在,不改动训练循环本身。

---

## 【使用方法】

**1) 安装**
```shell
pip install comet_ml
```

**2) 配置凭据(二选一)**
- 环境变量:
  ```shell
  export COMET_API_KEY=<Your Comet API Key>
  export COMET_PROJECT_NAME=<Your Comet Project Name>  # 默认 yolov5
  ```
- `.comet.config` 文件:
  ```
  [comet]
  api_key=<Your Comet API Key>
  project_name=<Your Comet Project Name>  # 默认 yolov5
  ```

**3) 启动训练(自动上报)**
```shell
python train.py --img 640 --batch 16 --epochs 5 --data coco128.yaml --weights yolov5s.pt
```

**4) 启用 Checkpoint 上报**
```shell
python train.py --img 640 --batch 16 --epochs 5 --data coco128.yaml --weights yolov5s.pt --save-period 1
```

**5) 控制预测上报频率(每 epoch 每 N 个 batch 上报一次)**
```shell
python train.py --img 640 --batch 16 --epochs 5 --data coco128.yaml --weights yolov5s.pt --bbox_interval 2
```

**6) 上调/下调预测图像数 + 调整频率**
```shell
env COMET_MAX_IMAGE_UPLOADS=200 python train.py --img 640 --batch 16 --epochs 5 --data coco128.yaml --weights yolov5s.pt --bbox_interval 1
```

**7) 开启类级别指标**
```shell
env COMET_LOG_PER_CLASS_METRICS=true python train.py --img 640 --batch 16 --epochs 5 --data coco128.yaml --weights yolov5s.pt
```

**8) 把数据集上传到 Comet Artifacts**
```shell
python train.py --img 640 --batch 16 --epochs 5 --data coco128.yaml --weights yolov5s.pt --upload_dataset
```

**9) 用已存的 Artifact 作为训练数据源**
```yaml
# artifact.yaml
path: "comet://<workspace name>/<artifact name>:<artifact version or alias>"
```
```shell
python train.py --img 640 --batch 16 --epochs 5 --data artifact.yaml --weights yolov5s.pt
```

**10) 8 个 Comet 环境变量速查(原文)**
| 变量 | 作用 | 默认 |
|---|---|---|
| `COMET_MODE` | online / offline | `online` |
| `COMET_MODEL_NAME` | 保存模型名 | `yolov5` |
| `COMET_LOG_CONFUSION_MATRIX` | 是否记录混淆矩阵 | `true` |
| `COMET_MAX_IMAGE_UPLOADS` | 最多上传图像数 | `100` |
| `COMET_LOG_PER_CLASS_METRICS` | 是否记录每类指标 | `false` |
| `COMET_DEFAULT_CHECKPOINT_FILENAME` | 续训 checkpoint 名 | `last.pt` |
| `COMET_LOG_BATCH_LEVEL_METRICS` | 是否记录 batch 级指标 | `false` |
| `COMET_LOG_PREDICTIONS` | 是否记录预测样本 | `true` |

## 图文联合解读

- `notebook_logo.png`: **图文联合解读：**

**1) 图中内容**：Comet ML品牌Logo——左侧为红橙色弧形火焰状（形似彗星轨迹），下方带黄色火星拖尾，右侧为灰色小写"comet"字样。

**2) 技术论证**：此为品牌标识图，非技术架构或数据流图，不承载具体技术结论，仅建立视觉识别。

**3) 与文档关系**：作为文档头部品牌Banner，配合正文"Comet构建帮助数据科学家加速ML/DL模型的工具"段落，强化品牌认知，呼应"YOLOv5 with Comet"主题，引领读者进入配置说明。

（约148字）
