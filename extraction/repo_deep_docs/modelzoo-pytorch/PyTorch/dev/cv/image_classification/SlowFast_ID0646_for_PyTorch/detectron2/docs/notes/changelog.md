# Change Log and Backward Compatibility

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/notes/changelog.md

# 深度解读:detectron2 Change Log and Backward Compatibility

---

## 【定位】

这篇文档是 detectron2 项目的变更与向后兼容性说明,告知使用者如何理解项目 API/配置的稳定性边界、配置版本历史,以及历史上若干"静默回归"(silent regression,无报错但结果不正确)的发生区间,以便用户在升级/复现实验时识别潜在风险。

---

## 【技术要点】

- **Release 日志入口**:官方变更记录在 GitHub release logs(`https://github.com/facebookresearch/detectron2/releases`),`incompatible changes` 是检索不兼容变更的关键词。
- **API 稳定性分层**(核心机制):
  - **Stable API**:出现在 [API 文档](https://detectron2.readthedocs.io/modules/index.html) 中的函数/类名、参数、文档化的类属性,默认稳定;若必须破坏,会先以 deprecation warning 过渡合理周期,再正式 break,并写入 release logs。
  - **Internal API**:未在 API 文档中暴露的成员,**更容易变更**;但若 `detectron2/projects` 内部已广泛使用,可能被"提升"为按 Stable 策略对待。
  - **Experimental**:通过 `detectron2/projects` 导入或位于 `detectron2/projects/` 目录下的项目,全部视为实验性。
  - **Default 行为**:类/函数名含 `default`,或文档明确为 "default behavior" 的,可能因新增特性而改变行为。
- **Config 版本历史**(自开源以来未发生变更,使用者无需担心):
  - **v1**:`RPN_HEAD.NAME` → 重命名为 `RPN.HEAD_NAME`。
  - **v2**:发布前对大量配置项做了一批批量重命名。
- **静默回归列表**(原文按日期倒序排列,均为"无报错但产出错误结果"的缺陷):
  - `04/01/2020 - 05/11/2020`:`TRAIN_ON_PRED_BOXES=True` 时精度异常。
  - `03/30/2020 - 04/01/2020`:ResNet 构建不正确。
  - `12/19/2019 - 12/26/2019`:使用 aspect ratio grouping 导致精度下降。
  - `截至 11/9/2019`:Test time augmentation 不预测最后一个类别。
- **总体建议**:第三方项目以"库依赖"方式跟进 detectron2 更新,通常比 fork 跟进更稳妥——API 变更的频率与范围远小于代码层变更。

---

## 【关键机制与数据】

### 向后兼容的工作原理

detectron2 出于"研究性质"的定位,**不保证 100% 向后兼容**,但通过分层治理减少对使用者的冲击:

1. **分级保护**:Stable > Internal(experimental,但可能因 projects 内部互通而被提升)> Projects(全部 experimental)。
2. **Deprecation 缓冲期**:Stable API 真正 break 前会有警告过渡。
3. **集中通告**:变更集中记录在 GitHub release logs,搜索 `incompatible changes` 即可获取。

### 数据流 / 性能数据

原文未给出性能数字、benchmark 曲线或量化指标;此节不臆造数据。

---

## 【表格解读】

**原文无表格**。

(配置版本与静默回归均以列表/条目形式给出,未以表格呈现。)

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

- **Release Logs**:具体的版本变更/incompatible changes 需跳转 [GitHub releases](https://github.com/facebookresearch/detectron2/releases)。
- **API 文档**:Stable API 的判定边界来源于 [detectron2 API documentation](https://detectron2.readthedocs.io/modules/index.html),其中"是否文档化"是分类依据。
- **`detectron2/projects`**:既是 API 分层的"特殊提级"对象(部分 internal API 因其内互通被按 Stable 策略对待),也是全部 experimental 的来源——所有经 `detectron2.projects` 导入或位于该目录的项目都被视为研究性项目。
- **Config 版本(v1/v2)**:与上文 `RPN_HEAD.NAME → RPN.HEAD_NAME` 这类命名重构对应,属于历史配置兼容性问题。
- **Silent Regressions**:涉及的具体机制分别跨越 `TRAIN_ON_PRED_BOXES` 训练开关、ResNet 骨干构建、aspect ratio grouping 采样策略、TTA(test time augmentation)预测流程——这些都是 detectron2 训练/推理链路中的关键环节,与上文 API/Config 稳定性治理共同构成项目的"信任"框架。

(注:本文档未提供内部链接;文末"内部链接"字段标记为 "(无)"。)

---

## 【使用方法】

**原文未涉及**具体的启用命令、配置项开关或 API 调用示例。

本文档是一份说明性 changelog,仅描述"什么样的变更会在何时出现"以及"使用者在升级时应如何应对",未给出操作步骤。实际使用/升级方式需结合:
- Release logs 中的具体 incompatible changes 条目,
- API 文档中的 Stable API 列表,
- 涉及上述静默回归区间的 commit/版本核对(以规避潜在精度异常)。
