# Backward Compatibility and Change Log

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/notes/changelog.md

# 一体化深度解读

## 【定位】
这篇文档是 detectron2（作为该 Faster RCNN 模型仓的上游依赖）的**向后兼容性与变更日志说明**，用于告知用户如何追踪版本变更、明确哪些 API 被视为稳定、内部 API 的处理策略、配置文件版本演进历史，以及若干会"静默产生错误结果"的隐藏回归问题及其影响时间范围。

---

## 【技术要点】

1. **版本日志来源指向**：文档将"新版本更新"指向外部链接 `https://github.com/facebookresearch/detectron2/releases`，而非在文档内维护历史记录。
2. **API 稳定性分层策略**：
   - **稳定 API**：列入 [API 文档](https://detectron2.readthedocs.io/modules/index.html) 的"函数/类名、参数、文档化的类属性"，除非文档另行声明，否则视为稳定；破坏前会有 **deprecation warning** 的过渡期，并写入 release logs。
   - **内部 API**：其他函数/类/属性更可能变动，但若已被 `detectron2/projects` 下项目实际使用，可能被提升为稳定 API 同样处理。
4. **兼容破坏的追踪方式**：通过在 [release logs](https://github.com/facebookresearch/detectron2/releases) 中搜索关键字 **"incompatible changes"** 来定位破坏性变更。
5. **Config 版本演进**：自开源以来 config 版本号**未再变更**，用户无需关注；目前仅记录了 **v1、v2** 两次重命名：
   - v1：`RPN_HEAD.NAME` → `RPN.HEAD_NAME`
   - v2：发布前的一批重命名（无具体条目）
6. **静默回归清单**：以日期区间形式列出 4 条会"静默产生错误结果"的回归（详见下表）。

---

## 【关键机制与数据】

- **机制：API 稳定性分层** — 文档通过"文档化 vs 内部"将 API 划分为两层，对外文档化的 API 走 deprecation warning → release logs 的安全迁移路径；内部 API 走更快迭代路径，但有"被其他项目实际使用"这一升级触发条件。
- **机制：Config 版本静默** — 原文明确"Detectron2's config version has not been changed since open source"，意味着**v2 之后无新增 config 版本**，下游用户不需要写版本迁移代码。
- **机制：静默回归的发现/披露** — 通过日期区间而非版本号标识，意在告诉使用者"如果你在这段时间内跑过训练/推理，结果可能错误，且不会报错"，需自行重跑或比对。

> 注：原文未给出性能数字、训练指标、显存/吞吐等数据，仅有行为层面的定性描述。

---

## 【表格解读】

### 表格 1：Config 版本变更历史（基于原文逐字还原）

| 版本 | 变更内容 |
|------|----------|
| v1   | Rename `RPN_HEAD.NAME` to `RPN.HEAD_NAME`. |
| v2   | A batch of rename of many configurations before release. |

**逐行解读：**
- **v1**：仅一项配置重命名 — 把"区域建议网络（RPN）头部"的名称配置从 `RPN_HEAD.NAME` 改写为 `RPN.HEAD_NAME`，路径合并到 `RPN` 命名空间下，使 RPN 相关配置统一收敛。
- **v2**：发布前一次性进行了**大量配置项的重命名**（"a batch of rename of many configurations"），原文**未列具体条目**，用户需到 release logs 自查；这是为开源发布做的统一清理。

### 表格 2：静默回归清单（基于原文逐字还原）

| 时间区间 | 静默回归现象 |
|----------|--------------|
| 04/01/2020 - 05/11/2020 | Bad accuracy if `TRAIN_ON_PRED_BOXES` is set to True. |
| 03/30/2020 - 04/01/2020 | ResNets are not correctly built. |
| 12/19/2019 - 12/26/2019 | Using aspect ratio grouping causes a drop in accuracy. |
| - 11/9/2019 | Test time augmentation does not predict the last category. |

**逐行解读：**
- **04/01/2020 – 05/11/2020**：当配置 `TRAIN_ON_PRED_BOXES=True`（即用预测框进行下一轮训练，是迭代式检测/自训练范式的开关）时，会出现**精度下降**且无报错。对在该窗口内复现自训练类工作（如本仓 Faster RCNN 的迭代训练流程）的用户影响显著。
- **03/30/2020 – 04/01/2020**：**ResNet 骨干网构建错误**，窗口仅 2 天，但波及所有以 ResNet 为骨干的目标检测模型；本仓 Faster RCNN 即依赖此类骨干，理论上需要核对自己在该窗口的 commit hash。
- **12/19/2019 – 12/26/2019**：使用 **aspect ratio grouping**（按长宽比分组采样）会导致**精度下降**。该采样策略常用于目标检测以稳定 batch 内目标尺寸分布。
- **- 11/9/2019**（原文如此，开头日期缺失）：**测试时增强（TTA）漏预测最后一个类别**，即推理时类别数 = `C` 时只会输出 `C-1` 个类别结果，属于类别索引越界类 bug。

> 解读补充：原文以"日期区间 + 现象"形式披露，意味着这些 bug **在版本号层面无明显提示**，必须用日期作为隐式版本键来排查。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档虽未给出内部链接，但依据内容可识别出如下上下游/模块关系：

- **与 [API 文档](https://detectron2.readthedocs.io/modules/index.html) 的关系**：API 文档是"稳定 API 集合"的**唯一权威清单**，稳定性策略以"是否在 API 文档中"作为判定边界。
- **与 [release logs](https://github.com/facebookresearch/detectron2/releases) 的关系**：release logs 是"破坏性变更的检索源"，关键字 **"incompatible changes"** 是统一检索入口；deprecation warning 与破坏性变更的最终落点都在此处。
- **与 `detectron2/projects` 下项目的关系**：作为内部 API"被提升为稳定"的触发条件来源，projects 子目录下的实际使用情况会影响 API 稳定性分层。
- **与本仓 Faster RCNN 的关系**：本模型作为 detectron2 体系下的目标检测实现，其骨干（ResNet 系）、配置（RPN/HEAD_NAME、aspect ratio grouping、TRAIN_ON_PRED_BOXES）、测试时增强等能力均与本日志中提及的回归点**直接重叠**，因此用户应据此核对自己所用版本的 commit 日期。

---

## 【使用方法】

- **启用方式**：本文档为**说明性 changelog**，无启用开关或编译/运行命令。
- **配置项相关原文**：仅 `TRAIN_ON_PRED_BOXES=True`（04/01/2020 – 05/11/2020 区间会引发静默精度下降）被点名；其余配置 (`RPN.HEAD_NAME`、aspect ratio grouping、TTA) 为受回归影响的触发条件，**原文未提供推荐值或启用命令**。
- **检索破坏性变更的命令/方法**：在 [release logs](https://github.com/facebookresearch/detectron2/releases) 内搜索关键字 **"incompatible changes"**。
