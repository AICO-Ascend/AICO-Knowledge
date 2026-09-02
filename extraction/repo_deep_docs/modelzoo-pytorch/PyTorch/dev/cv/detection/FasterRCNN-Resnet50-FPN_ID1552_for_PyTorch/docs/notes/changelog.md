# Backward Compatibility and Change Log

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/notes/changelog.md

# 一体化深度解读:FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch / docs/notes/changelog.md

## 【定位】

这篇文档是 Detectron2(被 FasterRCNN-Resnet50-FPN 模型仓库作为上游依赖)的**兼容性政策与变更日志说明文件**,解决的是"研究型视觉库在快速迭代时如何管理 API 稳定性、配置版本演进,以及如何向用户警示历史上沉默而危险的回归缺陷"这三个问题。

---

## 【技术要点】

1. **API 稳定性分层**:Detectron2 将 API 分为两类——(a) **稳定 API**:列入 [API documentation](https://detectron2.readthedocs.io/modules/index.html) 的函数/类名、参数、文档化类属性,变更前会先发出 deprecation warning 并写入 release logs;(b) **内部 API**:未文档化、更可能变动,但位于 `detectron2/projects` 下的可能按稳定 API 待遇处理并视情况晋升。
2. **兼容破坏的官方检索入口**:用户可通过在 [release logs](https://github.com/facebookresearch/detectron2/releases) 中搜索 "incompatible changes" 来定位破坏性变更。
3. **以"作为库使用"优于"Fork"的核心理由**:原文断言"the frequency and scope of API changes will be much smaller than code changes",即 API 变更频度与范围远小于代码变更。
4. **Config 版本演进(原文):**
   - **v1**:`RPN_HEAD.NAME` → `RPN.HEAD_NAME`(命名空间重命名)
   - **v2**:发布前对**大量**配置项进行了重命名("A batch of rename of many configurations")
   - 自开源以来 config 版本号**未再变动**,开源用户无需关注此问题。
5. **Silent Regression 清单(原文逐条保留关键日期与配置项):**
   - `04/01/2020 - 05/11/2020`:当 `TRAIN_ON_PRED_BOXES=True` 时出现**精度错误**。
   - `03/30/2020 - 04/01/2020`:**ResNets 构建不正确**(silent regression)。
   - `12/19/2019 - 12/26/2019`:**使用 aspect ratio grouping 导致精度下降**(silent regression)。
   - `- 11/9/2019`:**测试时增强(Test time augmentation)未预测最后一类**——即类索引末尾被遗漏的预测缺失 bug。

---

## 【关键机制与数据】

**工作原理(原文):**
- Detectron2 维护一个**外部链接型发布日志**(github releases),所有破坏性改动均记录于此,本文档本身仅作兼容性政策的索引与元说明。
- 兼容性政策通过**双层 API 分级**实现——文档化为稳定承诺、未文档化为可调整预留,这是研究型代码库常见的"软稳定性"策略。
- 对于"沉默回归"(silent regression),文档以**日期区间 + 现象描述**的形式告知用户:在特定历史时段使用特定配置或特性时,结果会**静默错误**(silently produce incorrect results)且难以调试。

**数据流(原文):**
- 用户配置 → 经由 `RPN.HEAD_NAME`(v1 之后)等键名解析 → RPN 训练/推理。原文未给出数值性能数据,仅定性描述"破坏性变更频度小于代码变更"。

**性能数据:原文未提供任何量化性能指标**(无 mAP、无 latency、无 throughput),仅提供日期区间和配置键名。

---

## 【表格解读】

**原文无表格。**

原文以纯文本列表形式罗列了 silent regression 的四条记录,未使用 markdown 表格结构,因此无表格可还原。

---

## 【公式解读】

**原文无公式。**

本文档为政策/日志说明,不含任何数学公式或伪代码表达式。

---

## 【关联】

本文档作为 Detectron2 的**元说明层**,与以下特性/模块存在上下游关联(均来自原文内引用):

- **Detectron2 官方发布日志** → https://github.com/facebookresearch/detectron2/releases
  - 关系:所有不兼容变更的**权威来源**,本文档指引用户去此处检索 "incompatible changes"。
- **Detectron2 API 文档** → https://detectron2.readthedocs.io/modules/index.html
  - 关系:**稳定 API 的界定范围**,任何在此文档中列出的函数/类名/参数/文档化属性均受 deprecation warning 机制保护。
- **`detectron2/projects` 子项目**
  - 关系:内部 API 的"准稳定"缓冲区——虽为内部 API,但因跨项目复用,可能被官方"晋升"为稳定 API。
- **`RPN.HEAD_NAME` 配置键**(v1 重命名产物)
  - 关系:FasterRCNN-Resnet50-FPN 等检测模型在配置中读取 RPN 头部名称,本文档解释了为何现使用 `RPN.HEAD_NAME` 而非历史 `RPN_HEAD.NAME`。
- **关键受影响的训练/推理开关**(silent regression 涉及):
  - `TRAIN_ON_PRED_BOXES`(训练开关)→ 关联 FasterRCNN 训练流程
  - **ResNet 主干构建** → 关联 FasterRCNN-Resnet50-FPN 模型的主干网络初始化路径
  - **Aspect ratio grouping** → 关联数据加载器中的 batch 采样策略
  - **Test time augmentation(TTA)** → 关联推理时的多尺度/多翻转增强流程

本文档自身**无文末内部链接**(原文与用户提示均确认无内链)。

---

## 【使用方法】

**启用方式 / 配置项 / 命令(原文有则写):**

- **查看兼容性破坏变更**:在 https://github.com/facebookresearch/detectron2/releases 页面搜索关键字 `"incompatible changes"`。
- **查阅稳定 API 列表**:访问 https://detectron2.readthedocs.io/modules/index.html,函数/类/参数若列于此则视为受 deprecation warning 保障的稳定 API。
- **RPN 配置键**:历史上需将 `RPN_HEAD.NAME` 改写为 `RPN.HEAD_NAME`(config v1 的迁移项;自开源以来无新版本迁移)。
- **避开 silent regression**:
  - 若在 `04/01/2020 - 05/11/2020` 时段使用过 `TRAIN_ON_PRED_BOXES=True`,需回查/重训以避免精度静默错误。
  - 若在 `03/30/2020 - 04/01/2020` 时段使用过 ResNet 主干,需复核模型权重。
  - 若在 `12/19/2019 - 12/26/2019` 时段使用过 aspect ratio grouping,需复核精度。
  - 若在 `11/9/2019` 之前使用过 test time augmentation,需补查最后类别是否被遗漏预测。

**原文未涉及**:具体的命令行启动方式、超参数调优、性能基准复现命令等,均**未在本文档中出现**。
