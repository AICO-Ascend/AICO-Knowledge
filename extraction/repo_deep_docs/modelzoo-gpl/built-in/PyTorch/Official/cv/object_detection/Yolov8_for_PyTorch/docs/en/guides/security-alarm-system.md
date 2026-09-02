# Security Alarm System Project Using Ultralytics YOLO11

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/security-alarm-system.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/security-alarm-system.md

# 深度解读:Security Alarm System Project Using Ultralytics YOLO11

---

## 【定位】

本文档解决"将 Ultralytics YOLO11 实时目标检测能力接入安防报警场景"的问题,描述了一种基于摄像头视频流的轻量级报警系统能力:检测到画面中存在目标时,通过 Gmail SMTP 发送一次性邮件告警。

---

## 【技术要点】

1. **模型与推理**:使用 `YOLO("yolo11n.pt")`(YOLO11 nano 版本)进行推理;运行设备通过 `torch.cuda.is_available()` 自动选择 `"cuda"` 或 `"cpu"`。
2. **视频采集**:使用 OpenCV `cv2.VideoCapture(capture_index)`,帧尺寸固定为 **640×480**(`cv2.CAP_PROP_FRAME_WIDTH/HEIGHT`)。
3. **邮件通道**:SMTP 服务器 `smtp.gmail.com: 587`,通过 `server.starttls()` 启用 TLS,使用 Gmail **App Password(16 位)** 进行认证(非普通账户密码)。
4. **告警去重逻辑**:`__call__` 主循环通过 `self.email_sent` 标志位实现"仅在 `class_ids` 非空且尚未发送过时触发一次邮件;目标消失后重置标志位",从而实现单次告警而非连续告警。
5. **可视化与 FPS**:`display_fps` 通过 `fps = 1 / round(end_time - start_time, 2)` 计算帧率,并以白底黑字覆盖在图像左上角;`plot_bboxes` 使用 `Annotator` 在每个检测框上绘制类别名标签。
6. **退出与资源回收**:主循环 `cv2.waitKey(5) & 0xFF == 27` 以 5ms 延时轮询,**ESC(键码 27)** 退出;退出后调用 `cap.release()`、`cv2.destroyAllWindows()` 与 `server.quit()` 释放摄像头、窗口与 SMTP 连接。
7. **存储需求(FAQ 原文)**:标准本地部署需约 **5GB** 可用磁盘空间(用于存放 YOLO11 模型及依赖)。

---

## 【关键机制与数据】

**工作原理(端到端数据流)**:

1. **参数配置阶段**:用户在代码顶部填写 `password`、`from_email`、`to_email` 三个字符串变量。
2. **SMTP 连接建立**:以 `smtp.gmail.com:587` 创建 `smtplib.SMTP` 实例 → `starttls()` → `login(from_email, password)` 完成认证。
3. **检测主循环**:
   - `cap.read()` 读取一帧 → 记 `start_time`
   - `self.model(im0)` 推理 → `results`
   - `plot_bboxes` 提取 `results[0].boxes.xyxy.cpu()` 与 `results[0].boxes.cls.cpu().tolist()`,遍历并通过 `Annotator.box_label` 标注
   - 若 `len(class_ids) > 0` 且 `not self.email_sent` → 调用 `send_email(to_email, from_email, len(class_ids))` 并置 `email_sent = True`
   - 若 `class_ids` 为空 → 置 `email_sent = False`(允许下次重新触发)
   - `display_fps` 叠加 FPS → `cv2.imshow("YOLO11 Detection", im0)` 显示
4. **退出分支**:ESC → 释放资源 + `server.quit()` 关闭 SMTP。

**性能/配置数据(原文)**:

| 数据项 | 原文数值 |
|---|---|
| 视频帧宽 | 640 |
| 视频帧高 | 480 |
| SMTP 端口 | 587 |
| SMTP 主机 | smtp.gmail.com |
| App Password 长度 | 16 位 |
| 退出键 | ESC(键码 27) |
| `waitKey` 延时 | 5 ms |
| 磁盘空间需求(FAQ) | ~5 GB |

**邮件正文模板(原文)**:`message_body = f"ALERT - {object_detected} objects has been detected!!"`(注意原文 "has" 系单复数误用,未做修正),主题 `"Security Alert"`。

---

## 【表格解读】

**原文无表格。**

(原文仅含 3 张图片:封面图、嵌入 YouTube 演示视频 `<iframe>`、邮件接收样本截图,无 markdown 表格。)

---

## 【公式解读】

原文中的"公式"均为 Python 表达式,而非数学公式,逐字保留如下:

**1. FPS 计算式**

```python
fps = 1 / round(self.end_time - self.start_time, 2)
```

- `self.end_time`:`time()` 取得的本帧循环结束时间戳。
- `self.start_time`:`time()` 取得的本帧循环开始时间戳(上一轮 `display_fps` 或 `__call__` 入口处赋值)。
- `round(..., 2)`:将两帧时间差保留两位小数(原文保留)。
- `1 / ...`:取倒数得到帧率(单位:帧/秒)。
- 随后 `text = f"FPS: {int(fps)}"` 取整显示。

**2. 邮件正文模板**

```python
message_body = f"ALERT - {object_detected} objects has been detected!!"
```

- `object_detected`:函数 `send_email` 的入参,默认值为 `1`,调用时实际传入 `len(class_ids)`(当前帧检测到的目标数量)。
- 该字符串经 `MIMEText(message_body, "plain")` 封装后通过 `message.as_string()` 发送。

**3. 边界框坐标解包**

```python
boxes = results[0].boxes.xyxy.cpu()
clss  = results[0].boxes.cls.cpu().tolist()
names = results[0].names
```

- `xyxy`:左上、右下两点坐标的张量,`.cpu()` 移至 CPU 内存(便于遍历)。
- `cls`:类别索引张量,`.tolist()` 转为 Python 列表;`names[int(cls)]` 查表得到类别名称字符串。

---

## 【关联】

文档明确提到的内部/外部链接及其与本文档的关系:

1. **`../hub/pro.md`(Ultralytics HUB Pro Plan)**:
   - 在 FAQ "What are the storage requirements for running Ultralytics YOLO11?" 中被引用,作为"扩展存储、增强特性"的延伸阅读入口。
   - 关联点:本地约 5GB 磁盘空间是基线;若需要更大规模数据集管理、协作与云端训练,可迁移到 HUB Pro Plan。

2. **`../guides/hyperparameter-tuning.md`**:
   - 由分析员在文档元信息/链接清单中提供,正文(在所提供片段)中未直接出现文本引用。
   - 关联点(推断):本文档默认使用 `yolo11n.pt` 的出厂参数;若用户希望进一步降低误报("false positives")或适配特定监控场景,可借助超参数调优指南(如 `lr0`、`conf`、`iou`、`mosaic` 等)对模型/训练流程做精调,再回灌到本报警系统。

3. **外部集成入口(FAQ 中提及)**:
   - `<https://docs.ultralytics.com/integrations/>`:用于将 YOLO11 接入既有安防基础设施(如 VMS、NVR、告警网关)。
   - `<https://myaccount.google.com/apppasswords>`:Gmail App Password 生成入口,前置依赖。

4. **与其他模块的隐含关系**:
   - `ultralytics.utils.plotting.Annotator` / `colors`:属于 Ultralytics 工具库,与训练/推理主流程(`YOLO.predict`)配套使用,共同支撑"检测 → 标注 → 报警"的闭环。
   - 文档路径(`Yolov8_for_PyTorch/docs/en/guides/`)显示本文档位于 Ultralytics 官方文档生态的"guides"层级,与 `hub/`(产品页)、`guides/`(方法论)同级。

---

## 【使用方法】

**启用步骤(原文)**:

1. **生成 Gmail App Password**:访问 `<https://myaccount.google.com/apppasswords>`,应用名可填 "security project",获取 **16 位**密码。
2. **填写邮件参数**:在脚本顶部赋值 `password = ""`、`from_email = ""`(须与生成密码的邮箱一致)、`to_email = ""`。
3. **建立 SMTP 连接**:运行 `server = smtplib.SMTP("smtp.gmail.com: 587")` → `server.starttls()` → `server.login(from_email, password)`。
4. **启动检测**:执行
   ```python
   detector = ObjectDetection(capture_index=0)
   detector()
   ```
   `capture_index=0` 对应系统默认摄像头(如需 USB 摄像头或多摄像头,可改为对应索引)。
5. **运行行为**:检测到任意目标 → 发送一封主题为 "Security Alert" 的邮件(正文含目标数量)→ 画面内持续存在目标时**不再重复发送**;目标从画面消失后,下一次重新出现将再次触发。
6. **退出**:在显示窗口按 **ESC**(键码 27)即可退出,资源被自动释放。

**配置项(原文)**:

| 配置项 | 位置 | 含义/默认值 |
|---|---|---|
| `password` | 顶部变量 | Gmail App Password(16 位) |
| `from_email` | 顶部变量 | 发件邮箱(需与 App Password 对应账户一致) |
| `to_email` | 顶部变量 | 收件邮箱 |
| `capture_index` | `ObjectDetection(...)` 入参 | 摄像头索引(默认 `0`) |
| `self.model = YOLO("yolo11n.pt")` | `__init__` | 模型权重文件路径(可换 `yolo11s/m/l/x.pt`) |
| `self.device` | `__init__` | `"cuda"` 若 GPU 可用,否则 `"cpu"` |
| `cv2.CAP_PROP_FRAME_WIDTH` | `__call__` | 640 |
| `cv2.CAP_PROP_FRAME_HEIGHT` | `__call__` | 480 |
| `cv2.waitKey(5)` | `__call__` | 5 ms 显示延时 |
| `send_email(..., object_detected=1)` | 函数签名 | 邮件正文中的目标数量,默认 1 |

**未涉及项**:文档未给出 YOLO11 模型的 `conf`、`iou`、`imgsz` 等推理超参的显式设置(均采用库默认),也未涉及模型训练/数据集准备流程——若需降低误报,需另行参考 `../guides/hyperparameter-tuning.md` 与 Ultralytics 训练文档。
