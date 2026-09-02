# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs/changelog.md

# 一体化深度解读:modelzoo-pytorch R(2+1)D 路径下的 changelog.md

## 【定位】

该文档是 **mmaction2 项目(OpenMMLab 视频理解工具箱)** 的累积性变更日志(changelog),按版本(Master / 0.16.0 / 0.15.0 / 0.14.0 / 0.13.0)组织,逐条记录每个发行版中的 **新特性(New Features)**、**改进(Improvements)**、**Bug 与文档修正(Bug and Typo Fixes)** 与 **模型库(ModelZoo)** 增删,供开发者追踪功能演进、迁移升级与引用对应 PR。

> ⚠️ 说明:虽然文档物理路径位于 `PyTorch/contrib/cv/video/R(2+1)D/docs/changelog.md`,但内容描述的是 **整个 mmaction2 仓库**(原文中所有 PR 链接均指向 `github.com/open-mmlab/mmaction2/pull/...`),并非 R(2+1)D 单个模型的变更。

---

## 【技术要点】

1. **多模型架构支持矩阵扩展**:覆盖 TSN / TSM / Timesformer / PoseC3D / ACRN / TRN / LFB / CSN 等识别模型,并将 Swin Transformer、Swin/Swin-3D 等 timm 主干与 TSN 结合作为示例。
2. **外部生态深度集成**:打通 PyTorchVideo(Transforms、RandAugment、AugMix)、pytorch-image-models/timm、MMCls、TorchVision、MMCV(Registry、EvalHook)、MIM。
3. **数据 I/O 与解码能力增强**:新增 PIMS Decoder、流式文件名 number counting、检测无效视频工具、`--cfg-options` 透传给 demo、json 输出到 video demo。
4. **训练范式升级**:支持 Mixup/Cutmix for recognizers、Focal Loss(随 ACRN)、`metric_options` 评估项、`self.with_neck` 属性;并把 `lr` 配置项重命名为 `scheduler`。
5. **部署与导出链路**:为 `pytorch2onnx.py` 增加 softmax 选项,支持 ONNX/TensorRT 引擎测试,修复 `num_classes <= 4` 时导出 bug。
6. **数据集与标注体系扩张**:新增 Jester、Diving48 数据集支持;改写 HMDB51 注释生成;为 Kinetics400 提供 val 集下载链接与替代下载方式;推出 Something-Something-V2 256 高度 checkpoint。

---

## 【关键机制与数据】

原文未给出数值化的性能/精度对比表,只通过条目式记录功能开关。结合原文可归纳的工作机制如下:

- **版本时间锚点(原文)**:`0.16.0 (01/07/2021)` / `0.15.0 (31/05/2021)` / `0.14.0 (30/04/2021)` / `0.13.0 (31/03/2021)`,Master 区段为撰写时尚未发行的下一版。
- **数据流层面的动作**(原文):
  - 用 PIMS Decoder 替代/补充默认视频解码路径(`#946`)。
  - 为 flow-wise filename template 加入 number counting(`#922`),即按序号而非固定占位符匹配光流帧。
  - `video demo` 输出 json(`#906`),把推理结果结构化输出,便于后续脚本消费。
- **训练调度层面**(原文):
  - `lr` 配置项更名为 `scheduler`(`#916`)—影响所有现有 config,需在升级时同步迁移。
  - `Refactor Sampler`(`#790`)、`Refactor spatio-temporal augmentation`(`#782`)、`Refactor Metafiles`(`#956 #979 #966`)等重构条目,改变数据采样、时序增广与模型元信息文件的内部接口。
- **CI / 工程化层面**(原文):`Use MMCV Model Registry`(`#843`)、`Polish code style with Pylint`(`#908`)、`Audit the usage of shutil.rmtree`(`#943`)等。

---

## 【表格解读】

**原文无表格**。原文档采用 Markdown 标题 + Markdown 项目符号列表的层级结构(版本号 → Highlights/New Features/Improvements/Bug and Typo Fixes/ModelZoo → 形如 `- 条目 ([#PR](URL))` 的条目),未出现任何参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式**。本文档属于发行说明性质,未涉及数学表达式、损失函数定义或伪代码。

---

## 【关联】

虽然文档位于 R(2+1)D 子路径下,但内容描述的是 mmaction2 总体,且与以下特性/模块存在上下游关系(均出自原文 PR 编号):

- **下游消费方**
  - PyTorchVideo 生态:Transforms(`#1008`)、RandAugment + AugMix 训练的 TSM-R50 sthv1 checkpoint。
  - timm 主干:`#880` 把 timm 主干接入 TSN,并配套发布 TSN+Swin 的 ModelZoo 条目。
  - MMCls / TorchVision 主干:`#679` / `#720` 分别把 MMCls 与 TorchVision 主干接入 TSN(`#553` 引入 LFB)。
- **上游依赖**
  - MMCV:`Use MMCV Model Registry`(`#843`)、`Use EvalHook in MMCV with backward compatibility`(`#793`)、`Fix mmcv install in CI`(`#977`)。
  - MIM:`Support MIM`(`#870`)。
- **平级交互模块**
  - PoseC3D(`#786 #890`) ↔ Jester dataset(`#864`):pose-based 数据集训练/评测通路。
  - ACRN + Focal Loss(`#891`) ↔ `metric_options` for evaluation(`#873`):损失函数与评估接口同版升级。
  - TRN(`#755`) ↔ Diving48(`#835`):新模型与新数据集同期落地。
  - Timesformer(`#839`)与 `TSN with Swin Transformer`(`#880`)在 0.16.0 同步出现在 Highlights 与 ModelZoo。
- **发布物钩子**
  - ModelZoo 段落每次版本都发布新 checkpoint(CSN、UCF101、HMDB51、sthv1、Swin-TSN、Timesformer、PoseC3D、ACRN 等),与 New Features 段落一一对应,可作为「特性 → 预训练权重」的索引。
- **链接拓扑**
  - PR 链接均指向 `https://github.com/open-mmlab/mmaction2/pull/<N>`;文末无内部锚点链接(用户提示:「内部链接: (无)」)。

---

## 【使用方法】

**原文未涉及**。该文档是变更日志,不含启用方式、配置项或命令行教程。若需启用其中提及的特性,需要回到 mmaction2 仓库对应 PR 的代码或对应模型目录下的 `README.md` / config 文件查阅,本 changelog 仅作为索引。例如:

- 想使用 timm 主干:`#880` 的 config 路径(原文未给出,需自行查 PR)。
- 想使用 PIMS Decoder:需在数据预处理 pipeline 中替换 decoder(原文未给出具体字段名)。
- 想做 ONNX 导出:可使用 `tools/pytorch2onnx.py`,并加上 `--softmax` 选项(`#781`)。
- 想跑 TSM-R50 sthv1 RandAugment/AugMix checkpoint:在 ModelZoo 中查找由 PR `#1008` 引入的权重(原文未给出 URL)。
