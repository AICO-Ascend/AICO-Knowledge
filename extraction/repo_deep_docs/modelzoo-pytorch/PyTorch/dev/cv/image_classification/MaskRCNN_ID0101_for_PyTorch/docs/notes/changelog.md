# Backward Compatibility and Change Log

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/notes/changelog.md

# 深度解读：MaskRCNN_ID0101_for_PyTorch / docs/notes/changelog.md

---

## 【定位】

本文档是 Detectron2（本文为 Mask R-CNN 模型仓中携带的衍生说明）面向用户披露**向后兼容性策略、Config 版本变更记录与历史静默回退（silent regression）清单**的变更说明文件，目的是帮助使用方判断升级风险、定位已修复/未修复的潜在错误来源。

---

## 【技术要点】

1. **API 稳定性分级**：分为「文档化 stable API（入口含在 `detectron2.readthedocs.io/modules/index.html`）」与「internal API（其余 function/class/attribute）」两级；前者受保护（破坏前会先发 deprecation warning 并写入 release logs），后者更易变更，但对 `detectron2/projects` 下被复用的内部 API 仍可能按 stable 策略对待。
2. **破坏性变更追踪方式**：在 release logs 中搜索关键字 `"incompatible changes"` 即可定位全部不兼容改动（链接：`https://github.com/facebookresearch/detectron2/releases`）。
3. **Config 版本号自开源以来未再变化**（"Detectron2's config version has not been changed since open source"），开源用户无需关心。
4. **Config v1 变更**：将 `RPN_HEAD.NAME` 重命名为 `RPN.HEAD_NAME`。
5. **Config v2 变更**：在发布前一次性批量重命名了一批 configurations。
6. **静默回退（incorrect results without warning）清单**：列出 4 段特定日期窗口内的已知错误，按时间倒序追溯至 2019-11-09。

---

## 【关键机制与数据】

- **工作原理**：本文档实质是一份"风险告知书"，通过把 API 拆成 stable / internal 两层，并强制要求破坏性变更走 release logs 公示，让第三方代码可以"以库方式升级"而非"fork 升级"——**原文明确指出**："using it as a library will still be less disruptive than forking, because the frequency and scope of API changes will be much smaller than code changes."
- **静默回退的数据流影响**：列表中的每一项都是会**悄无声息地产生错误结果**的回归（原文："since they may silently produce incorrect results and will be hard to debug"），所以特别列出供事后排查/对账。
- **关键日期与触发条件（性能/正确性数据，按原文逐字保留）**：
  - **04/01/2020 – 05/11/2020**：`TRAIN_ON_PRED_BOXES = True` 时精度异常（"Bad accuracy if `TRAIN_ON_PRED_BOXES` is set to True."）。
  - **03/30/2020 – 04/01/2020**：ResNet 构建不正确（"ResNets are not correctly built."）。
  - **12/19/2019 – 12/26/2019**：使用 aspect ratio grouping 会导致精度下降（"Using aspect ratio grouping causes a drop in accuracy."）。
  - **– 11/9/2019**（起始日期不明确，原文写为 `"- 11/9/2019"`）：测试时增强（TTA）未对最后一个类别做预测（"Test time augmentation does not predict the last category."）。
- **新版本发布渠道**：原文指向 GitHub Releases（`https://github.com/facebookresearch/detectron2/releases`），所有更新（含上述不兼容变更）的唯一权威入口即此链接。

---

## 【表格解读】

**原文无表格**。原文既无 markdown 表格，也无隐含的二维表结构。涉及条目（Config 版本变更、静默回退）均以单列 bullet list 形式给出，未涉及多列对比或参数矩阵，因此按要求标注为"原文无表格"。

---

## 【公式解读】

**原文无公式**。全文未出现任何 LaTeX、伪代码或数学表达式，仅含配置项名称字符串（如 `RPN_HEAD.NAME`、`RPN.HEAD_NAME`、`TRAIN_ON_PRED_BOXES`）与日期区间。

---

## 【关联】

- **上游/配套文档**：
  - **Release logs**：`https://github.com/facebookresearch/detectron2/releases` —— 一切不兼容变更、stable API 弃用记录的权威落地点；查找方式为搜索 `"incompatible changes"`。
  - **API documentation**：`https://detectron2.readthedocs.io/modules/index.html` —— stable API 边界定义处，所有未在此列出的成员均归为 internal API。
- **同级模块**：
  - **`detectron2/projects`** 目录：内部 API 跨项目复用层；文档明示对其中已被外部项目依赖的内部符号，仍可能按 stable 策略处理（"we may use them for convenience among projects under `detectron2/projects`"），并有望在迭代成熟后"promoted to stable"。
- **与本文同仓的位置关系**：本文位于 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/notes/changelog.md`，说明该 Mask R-CNN 实现直接复用或对接 Detectron2 的 API/Config 体系；上游 Detectron2 任何 v1/v2 之后的新改动都会沿这条链路影响本仓。
- **内部链接**：本文未提供仓库内相对路径链接，故"与文中提到的其他特性/模块/上下游的关系"全部通过上述三条外部 GitHub/release/readthedocs 链接表达。

---

## 【使用方法】

**启用方式/配置项/命令**：

- 若需**追踪破坏性变更**：在 release logs 页面以 `"incompatible changes"` 为关键字检索（原文："search for 'incompatible changes' in release logs"）。
- 若需**识别 Config 是否需要迁移**：仅 v1（`RPN_HEAD.NAME → RPN.HEAD_NAME`）与 v2（一批重命名）两个迁移点；自开源起 config 版本号未再变化（原文："Detectron2's config version has not been changed since open source. There is no need for an open source user to worry about this."）。
- 若需**排查已知静默错误**：按训练/推理时间戳对照 4 段窗口（2020-04-01~05-11、2020-03-30~04-01、2019-12-19~12-26、~2019-11-09）确认是否落入了已知回退区间，并对相关开关做修正（如关闭 `TRAIN_ON_PRED_BOXES`、关闭 aspect ratio grouping、检查 TTA 最后类别输出、升级到修复 ResNet 构建的 commit 之后版本）。

原文未涉及具体的安装命令、环境变量或 demo 启动方式，故本节其余内容不另行扩展。
