# Model

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/pytorch_hub_model_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/pytorch_hub_model_loading.md

【定位】这篇文档讲解如何通过 PyTorch Hub (`torch.hub.load`) 一行代码加载 Ultralytics YOLOv5 预训练模型并执行推理/训练/截图/多 GPU 等任务,聚焦 "加载即用 + 可定制" 的模型装载与调用范式。

【技术要点】
1. **环境依赖**: Python >= 3.8.0、PyTorch >= 1.8,通过 `pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt` 安装;不需克隆仓库,模型与数据集会在 `torch.hub.load` 调用时按需自动下载。
2. **核心装载 API**: `torch.hub.load("ultralytics/yolov5", "yolov5s")` 一行加载 YOLOv5 家族的最小最快模型 `yolov5s`,直接得到可调用对象 `model`。
3. **推理返回结构**: `results` 对象支持 `.print()`、`.save()`、`.show()`、`.xyxy` (tensor)、`.pandas().xyxy[0]` (DataFrame),输出坐标列固定为 `xmin / ymin / xmax / ymax / confidence / class / name`。
4. **推理超参 (Inference Settings)**: `model.conf=0.25`(NMS 置信阈值)、`iou=0.45`(NMS IoU 阈值)、`agnostic=False`(类无关 NMS)、`multi_label=False`(单框多标签)、`classes=None`(按类别过滤)、`max_det=1000`(单图最大检测数)、`amp=False`(自动混合精度);推理时可指定 `size=320` 之类的自定义输入尺寸。
5. **设备与定制**: 支持 `model.cpu()` / `model.cuda()` / `model.to(device)` 后置迁移,也可在装载时用 `device="cpu"` 直接落到指定设备;输入图像会在推理前自动迁移到模型所在设备;支持 `_verbose=False` 静默加载、`channels=4` 改输入通道数、`classes=10` 改输出类别数、`force_reload=True` 丢弃缓存重新下载。
6. **高级用法**: `autoshape=False` 用于训练模式,`pretrained=False` 用于从零随机初始化;`ImageGrab.grab()` 可做桌面截屏推理;多 GPU 用 `threading.Thread` + `device=0/1` 并行;`results.crop(save=True)` 导出裁剪检测框,`results.ims` + `results.render()` + `base64.b64encode` 可输出 Base64 编码结果图供 API 服务使用。

【关键机制与数据】
原文: 装载阶段通过 `torch.hub.load("ultralytics/yolov5", "yolov5s")` 从 PyTorch Hub 拉取最新 YOLOv5 release 的预训练权重与数据集,无需克隆仓库。
原文: `model` 内部封装 `AutoShape()` 前向方法,负责自动将输入 (PIL / OpenCV BGR / numpy / URL / 截图) 转成张量并放到正确设备,故调用方可以 `model(im)` 或 `model([im1, im2], size=640)` 直接推理。
原文: `results.pandas().xyxy[0]` 在 zidane.jpg 上的输出列与数值原文示例为:
```
     xmin    ymin    xmax   ymax  confidence  class    name
0  749.50   43.50  1148.0  704.5    0.874023      0  person
1  433.50  433.50   517.5  714.5    0.687988     27     tie
2  114.75  195.75  1095.0  708.0    0.624512      0  person
3  986.00  304.00  1028.0  420.0    0.286865     27     tie
```
原文: 简单示例对单张 `zidane.jpg` URL 推理;详细示例通过 `torch.hub.download_url_to_file` 下载两张图片(`zidane.jpg`, `bus.jpg`),`im1` 为 PIL 图,`im2` 为 `cv2.imread(...)[..., ::-1]` (BGR→RGB),以 `model([im1, im2], size=640)` 做批推理;结果默认保存到 `runs/hub`。
原文: 改 `channels=4` 时,除第一层输入层外其余均沿用预训练权重,输入层以随机权重保留;改 `classes=10` 时同理,输出层被替换并以随机权重保留。
原文: 多 GPU 示例同时加载 `model0`(device=0) 与 `model1`(device=1),通过 `threading.Thread(daemon=True)` 并行对不同图像执行 `results.save()`。
原文: Base64 输出链路为 `results.ims` → `results.render()` 在原图上绘制框与标签 → `Image.fromarray` → JPEG 编码 `BytesIO` → `base64.b64encode` 输出 utf-8 字符串,适用于 Flask REST API。

【表格解读】原文无表格。

【公式解读】原文无公式。

【关联】
- `./train_custom_data.md`:文档中明确指出 "Alternatively see our YOLOv5 Train Custom Data Tutorial" 用于模型训练,与本篇 `autoshape=False` + `pretrained=False` 的训练装载路径互补,负责下游自定义数据训练流程。
- `./model_export.md`:虽未在原文中出现但属于同目录教程,通常承担把 Hub 加载的模型导出为 ONNX / TFLite / CoreML 等格式的职责,衔接 "装载 → 部署"。
- `../environments/google_cloud_quickstart_tutorial.md`、`../environments/aws_quickstart_tutorial.md`、`../environments/azureml_quickstart_tutorial.md`、`../environments/docker_image_quickstart_tutorial.md`:为 YOLOv5 提供 GCP / AWS / Azure ML / Docker 镜像等运行环境,与本文 "Hub 一行装载 + 设备/多 GPU 推理" 配合,构成云端或容器化推理的前置环境章节。
- 文中另一隐含外部依赖是 YOLOv5 主仓库 `models/common.py` 的 `AutoShape()` forward 方法,负责统一封装推理前处理与后处理。

【使用方法】
1. **安装依赖**:
   ```bash
   pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt
   ```
   要求 Python>=3.8.0、PyTorch>=1.8。
2. **最小加载并推理**:
   ```python
   import torch
   model = torch.hub.load("ultralytics/yolov5", "yolov5s")
   results = model("https://ultralytics.com/images/zidane.jpg")
   results.pandas().xyxy[0]
   ```
3. **批推理 + 结果保存**: `model([im1, im2], size=640)` 后可调 `results.print()` / `results.save()` (默认输出到 `runs/hub`) / `results.show()` / `results.xyxy[0]` / `results.pandas().xyxy[0]`。
4. **推理超参**:
   ```python
   model.conf = 0.25   # NMS confidence threshold
   iou = 0.45          # NMS IoU threshold
   agnostic = False    # NMS class-agnostic
   multi_label = False # NMS multiple labels per box
   classes = None      # e.g. = [0, 15, 16] 过滤 COCO persons/cats/dogs
   max_det = 1000      # 每张图最大检测数
   amp = False         # 自动混合精度推理
   results = model(im, size=320)
   ```
5. **设备选择**:
   ```python
   model.cpu(); model.cuda(); model.to(device)
   # 或装载时直接指定
   model = torch.hub.load("ultralytics/yolov5", "yolov5s", device="cpu")
   ```
6. **静默加载**: `torch.hub.load("ultralytics/yolov5", "yolov5s", _verbose=False)`。
7. **改变输入通道/类别数**:
   ```python
   torch.hub.load("ultralytics/yolov5", "yolov5s", channels=4)   # 输入通道=4
   torch.hub.load("ultralytics/yolov5", "yolov5s", classes=10)   # 输出类别=10
   ```
8. **强制重新下载**: `torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=True)`。
9. **截图推理**: `im = ImageGrab.grab(); results = model(im)`。
10. **多 GPU 并行推理**:
    ```python
    model0 = torch.hub.load("ultralytics/yolov5", "yolov5s", device=0)
    model1 = torch.hub.load("ultralytics/yolov5", "yolov5s", device=1)
    threading.Thread(target=run, args=[model0, "https://ultralytics.com/images/zidane.jpg"], daemon=True).start()
    threading.Thread(target=run, args=[model1, "https://ultralytics.com/images/bus.jpg"], daemon=True).start()
    ```
11. **训练模式**:
    ```python
    model = torch.hub.load("ultralytics/yolov5", "yolov5s", autoshape=False)                  # 加载预训练
    model = torch.hub.load("ultralytics/yolov5", "yolov5s", autoshape=False, pretrained=False)  # 从零随机初始化
    ```
12. **导出裁剪检测 / Base64 结果**:
    ```python
    results.crop(save=True)                 # 裁剪并保存
    results.ims; results.render()           # 在原图上绘制框
    im_base64 = Image.fromarray(results.ims[i])
    im_base64.save(buffered, format="JPEG")
    print(base64.b64encode(buffered.getvalue()).decode("utf-8"))
    ```
13. **Pandas 结果**: `results.pandas().xyxy[0]` 直接得到列 `xmin / ymin / xmax / ymax / confidence / class / name` 的 DataFrame。
