# Tutorial 2: Adding New Dataset

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/pose_estimation/Hourglass_for_PyTorch/mmpose-master/docs/tutorials/new_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/pose_estimation/Hourglass_for_PyTorch/mmpose-master/docs/tutorials/new_dataset.md

【定位】
本教程（Tutorial 2: Adding New Dataset）解决「如何将自己的数据集接入 mmpose 进行训练/验证/测试」的问题，描述了在 mmpose 中复用框架现成数据管线（最简路径：转成 COCO 标注格式）的标准做法与配套 config 改造方式。

【技术要点】
1. **数据组织最简路径**：将自定义数据集的标注文件转换为 COCO 格式 JSON，而非重写数据加载类。
2. **COCO JSON 三大必需键**：`images`（图像元信息）、`annotations`（实例标注）、`categories`（类别定义）。
3. **`images` 字段必备键**：`file_name`（图像文件名）、`height`、`width`、`id`（图像唯一编号）。
4. **`annotations` 字段必备键**：`segmentation`（多边形分割坐标）、`keypoints`（扁平 [x,y,v] 序列）、`num_keypoints`（已标注关键点数量，示例为 10）、`area`（目标区域面积，示例 3894.5826）、`iscrowd`（是否密集场景，示例 0）、`image_id`、`bbox`（[x,y,w,h]，示例 [402.34, 205.02, 65.26, 88.45]）、`category_id`、`id`（标注唯一编号，示例 215218）。
5. **`keypoints` 编码方式**：每点 3 个值 (x, y, visibility flag)，visibility 取 0（未标注）/1（已标注但不可见）/2（已标注且可见）；示例数据共 17 个关键点 × 3 = 51 个数值，对应 COCO person 关键点定义。
6. **`categories` 字段必备键**：`id`（类别 ID，示例 1）、`name`（类别名，示例 'person'）。
7. **Config 改造点**：在 `configs/my_custom_config.py` 中设置 `dataset_type = 'MyCustomDataset'`、`classes = ('a','b','c','d','e')`，并在 `data` dict 下分别为 `train`/`val`/`test` 指定 `type`、`ann_file`（标注 JSON 路径）、`img_prefix`（图像目录前缀），以及 `samples_per_gpu=2`、`workers_per_gpu=2`。

【关键机制与数据】
- **工作原理**：原文采用「最小改动」策略——只要把数据预处理成 COCO 标准 JSON，就能直接复用 mmpose 已有的数据加载、评估与可视化管线，无需编写新的 Dataset 类。
- **数据流**：
  1. 用户准备原始图像 + 原始标注；
  2. 通过预处理脚本将标注序列化为 COCO 格式 JSON（含 `images`/`annotations`/`categories` 三个顶层键）；
  3. 修改 `configs/my_custom_config.py`，把 `dataset_type`、`classes` 与各 split 的 `ann_file`/`img_prefix` 指向自己的路径；
  4. 框架按 COCO 解析器读取 JSON，映射关键点 → 模型训练目标。
- **性能数据**：原文未提供任何基准/吞吐量/精度数字。

【表格解读】
原文无表格（仅提供 JSON 标注结构示例与 config 代码片段，非表格形式，故此处不进行表格逐字还原）。

【公式解读】
原文无公式。

【关联】
文末内部链接:（无）。从内容外推，本教程属于 mmpose「数据集接入」系列教程的第 2 篇，与同类教程通常的上下游关系为：
- **上游（数据准备）**：用户需先完成关键点标注（可借助 labelme、COCO-Annotator 等工具），再按本教程转 COCO 格式；
- **下游（模型训练/评估）**：完成 config 修改即可复用 mmpose 已实现的 COCO 风格数据加载与关键点 AP 评估逻辑，无需额外适配；
- **并行替代方案**：原文虽未在本节展开，但系列教程通常另设「实现自定义 Dataset 类」的分支教程作为本节「转 COCO 格式」的替代路径。

【使用方法】
按原文所述启用流程如下：
1. 将自定义标注转为 COCO 格式 JSON，确保包含 `images` / `annotations` / `categories` 三个顶层键及上文列出的全部子键；
2. 编辑 `configs/my_custom_config.py`：
   ```python
   dataset_type = 'MyCustomDataset'
   classes = ('a', 'b', 'c', 'd', 'e')
   data = dict(
       samples_per_gpu=2,
       workers_per_gpu=2,
       train=dict(type=dataset_type,
                  ann_file='path/to/your/train/json',
                  img_prefix='path/to/your/train/img',
                  ...),
       val=dict(type=dataset_type,
                ann_file='path/to/your/val/json',
                img_prefix='path/to/your/val/img',
                ...),
       test=dict(type=dataset_type,
                 ann_file='path/to/your/test/json',
                 img_prefix='path/to/your/test/img',
                 ...))
   ```
   将 `ann_file` 替换为实际 JSON 标注路径，将 `img_prefix` 替换为实际图像目录前缀，`classes` 替换为自有类别元组；
3. 使用该 config 启动训练/测试即可（具体启动命令原文未涉及，需结合 mmpose 训练脚本文档）。
