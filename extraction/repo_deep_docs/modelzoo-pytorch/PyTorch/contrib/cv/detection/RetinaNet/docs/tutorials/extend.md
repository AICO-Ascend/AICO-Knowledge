# Extend Detectron2's Defaults

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/extend.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/extend.md

# 深度解读：Extend Detectron2's Defaults

## 【定位】
本文档旨在回答一个研究工程的核心张力问题：**如何在保留底层灵活性的同时，提供高层抽象让标准用法足够简单**。它系统性地介绍了 Detectron2 中用以扩展默认行为（defaults）的三类接口形态，并指明"何时该走标准路径、何时该自行拼装"的判断准则。

---

## 【技术要点】

1. **两类核心抽象（原文标号 1、2）**：Detectron2 同时提供
   - 接受 `cfg` 参数的"标准默认"接口（thin-but-friendly），用户只需加载 config 并传递；
   - 接受显式参数（explicit arguments）的"积木式"接口，要求用户具备领域知识，可自由组合。

2. **第三类实验性接口（原文标号 3）**：使用 `@configurable` 装饰器的类，可同时接受 `cfg` 或显式参数调用，但其显式参数接口被明确标记为 *experimental*、**可能变动**。

3. **范式选择策略**：仅需标准行为 → `getting_started.md` 即可；需要扩展则按数据/加载器/模型/训练四个维度参考后续教程。

4. **Mask R-CNN 显式构造示例**：以 *非 config* 方式手工实例化 `GeneralizedRCNN`，覆盖 Backbone（FPN+ResNet）、RPN（Proposal Generator）、StandardROIHeads（Box + Mask）三大组件，并显式指定像素归一化与通道格式。

5. **关键数字（保留自原文示例代码）**：
   - ResNet stage 配置：`[3, 4, 6, 3]` blocks，strides `[1, 2, 2, 2]`，通道对 `[64,256,512,1024] → [256,512,1024,2048]`；
   - RPN FPN 层级 `["p2","p3","p4","p5","p6"]`，每层 `num_anchors=3`；
   - Anchor 尺寸 `[[32],[64],[128],[256],[512]]`，宽高比 `[0.5, 1.0, 2.0]`，strides `[4,8,16,32,64]`；
   - RPN 训练：`batch_size_per_image=256`、`positive_fraction=0.5`、`pre_nms_topk=(2000,1000)`、`post_nms_topk=(1000,1000)`、`nms_thresh=0.7`；
   - ROI 训练：`num_classes=80`、`batch_size_per_image=512`、`positive_fraction=0.25`、`proposal_matcher` IoU 阈值 `[0.5]`；
   - 像素归一化：`pixel_mean=[103.530, 116.280, 123.675]`、`pixel_std=[1.0, 1.0, 1.0]`、`input_format="BGR"`。

6. **设计哲学**：研究意味着"以新方式做事"，因此 thin abstraction 与 high-level abstraction 并存；两者共同服务于"既能开箱即用，又能拆解重组"的目标。

---

## 【关键机制与数据】

原文给出的不是性能数据，而是**架构/接口工作原理**层面的描述：

- **工作原理（原文）**：当 detectron2 的"标准默认"不足以满足需求时，用户可以复用"显式参数接口"自行组合出新的 pipeline——Mask R-CNN 示例即为证明，展示了不依赖 config 文件、从零拼装完整模型的方式。
- **数据流（原文）**：示例代码构造顺序为 *Backbone (FPN) → ProposalGenerator (RPN) → ROIHeads (Box + Mask) → pixel_mean/std & input_format*，呈现了从特征提取 → 候选框生成 → 区域精化（分类/回归 + 分割）的典型级联。
- **性能数据**：原文**未涉及**任何 benchmark/速度/精度数字。

---

## 【表格解读】
原文无表格（仅含一段 `<details>` 折叠的 Python 代码块）。

---

## 【公式解读】
原文无 LaTeX/伪代码形式的数学公式。示例代码中的参数序列（如 `[3, 4, 6, 3]`、`(2000, 1000)`、`(10, 10, 5, 5)`）均为**配置项的字面量**，而非公式。其语义需结合模块源码理解，例如：
- `(pre_nms_topk, post_nms_topk) = (2000, 1000)`：训练态 NMS 前/后保留的 top-k 候选框数；
- `(10, 10, 5, 5)`：box2box_transform 权重，对应 (dx, dy, dw, dh) 的 σ 缩放因子；
- `[0.5, 1.0, 2.0]`：anchor 的宽高比；
- `[0.3, 0.7]`：RPN 训练时 anchor 与 GT 的 IoU 阈值（neg/pos 边界）。

---

## 【关联】

文档通过文末清单给出了完整的上下游教程矩阵，体现了 detectron2 扩展体系的**四面延伸**：

| 扩展维度 | 对应教程（原文链接） | 解决什么问题 |
|---|---|---|
| 数据集 | `./datasets.md` | 自定义数据集接入 |
| 数据加载 | `./data_loading.md` | 自定义 DataLoader |
| 模型使用 | `./models.md` | 改写/覆盖已有模型行为 |
| 模型编写 | `./write-models.md` | 从零写新模型 |
| 训练流程 | `./training.md` | Hook 或自写训练循环 |
| 标准入门 | `./getting_started.md` | 仅用默认行为即可走通 |
| 装饰器 API | `../../modules/config.html#detectron2.config.configurable` | 实验性 `@configurable` 双形态调用 |

文中 Mask R-CNN 示例本身即是 `models.md` / `write-models.md` 的具象化样本——把 `GeneralizedRCNN` 拆为 Backbone / ProposalGenerator / ROIHeads 三层积木。

---

## 【使用方法】

原文**未涉及**任何具体启用命令、CLI flag 或环境变量。文档只给出**方法论层面的指引**：

- **若只需标准行为** → 阅读 [`getting_started.md`](./getting_started.md)；
- **若需替换默认** → 按"数据集 → 加载器 → 模型 → 训练"四步参考对应教程：
  - 自定义数据集：[`./datasets.md`](./datasets.md)
  - 自定义 DataLoader：[`./data_loading.md`](./data_loading.md)
  - 改写/扩展模型：[`./models.md`](./models.md) + [`./write-models.md`](./write-models.md)
  - 自定义训练循环：[`./training.md`](./training.md)
- **若使用 `@configurable`** → 参考 [`detectron2.config.configurable`](../../modules/config.html#detectron2.config.configurable) 模块文档，并注意显式参数接口为 **experimental**，存在变动风险。

> 实际"启用方式"（如 config 字段命名、注册器机制、构建函数调用模式）需要进入上述各子教程进一步查阅，原文未在此处展开。
