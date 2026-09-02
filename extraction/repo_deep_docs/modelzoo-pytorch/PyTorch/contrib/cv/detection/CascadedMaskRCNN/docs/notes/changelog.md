# Backward Compatibility and Change Log

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/notes/changelog.md

# CascadedMaskRCNN/docs/notes/changelog.md 深度解读

## 【定位】
这篇文档是 detectron2 框架的**向后兼容性与变更日志说明**,向用户告知 API 的稳定性边界、配置版本演进历史,以及历史上若干"静默回归"(silent regression)的具体时间段,帮助第三方使用者判断升级风险并定位潜在的不正确结果来源。

---

## 【技术要点】

1. **API 稳定性分级策略**:文档列出两类 API 的处理方式——文档化 API(函数/类名、参数、文档化类属性)被视作 stable;其余为 internal,更容易变更。但 `detectron2/projects` 下出于项目间便利性而使用的 API,也可能被视作 stable。
2. **弃用过渡机制**:stable API 若必须破坏,会先**触发 deprecation warning**(持续一段合理时间)再真正破坏,并记录在 release logs 中。
3. **配置文件版本演进**:历史上共两个版本——**v1**:`RPN_HEAD.NAME` → `RPN.HEAD_NAME`;**v2**:发布前一批重命名操作。原文注明"自开源以来 config version 未再变更",开源用户无需关注。
4. **第三方升级建议**:即便有破坏,使用 detectron2 作为库比直接 fork 破坏更小,因为"API 变更的频率和范围会远小于代码变更"。查看方式:在 release logs 中搜索 "incompatible changes"。
5. **静默回归时间线**(共 4 段,原文):均会**静默产出不正确结果且难以调试**:
   - 04/01/2020 – 05/11/2020:`TRAIN_ON_PRED_BOXES=True` 时准确率异常
   - 03/30/2020 – 04/01/2020:ResNets 构建不正确
   - 12/19/2019 – 12/26/2019:使用 aspect ratio grouping 导致准确率下降
   - 截至 11/9/2019:测试时增强(test time augmentation)未预测最后一个类别
6. **官方更新入口**:所有新更新以 [https://github.com/facebookresearch/detectron2/releases](https://github.com/facebookresearch/detectron2/releases) 为准。

---

## 【关键机制与数据】

**工作原理(兼容性保障机制)**:
- 原文将 API 划分为"stable"与"internal"两层,前者以文档化为锚定,后者以"使用便利性"为锚定。
- 破坏流程采用"先 deprecate → 持续警告 → 最终破坏 → release logs 记录"的标准三段式,使外部用户有缓冲期。
- config 版本演进采用"v1 单条改名 → v2 批量改名"的模式,之后冻结,体现"研究型库"的演进特点(原文:"Due to the research nature of what the library does, there might be backward incompatible changes")。

**数据流与时间维度**:
- 静默回归区段跨越约 6 个月(2019-11 至 2020-05),每一段都精确到天,意味着这些 bug 是在生产环境中隐式运行而无错误信号。
- 回归影响范围涉及训练(`TRAIN_ON_PRED_BOXES`)、骨干网络构建(ResNets)、数据采样策略(aspect ratio grouping)、推理后处理(test time augmentation),覆盖训练—推理全链路。

**性能数据**:
- 原文未提供数值化的性能指标(无 mAP、无 loss 数字);仅以"Bad accuracy"、"drop in accuracy"、"incorrectly built"等定性描述呈现回归影响。

---

## 【表格解读】

原文无表格。

> 补充说明:虽然"Config Version Change Log"与"Silent Regression in Historical Versions"两节在视觉上呈列表式排布,但原文使用的是 markdown 列表(无表头、无列对齐),不构成结构化表格。其信息可视为:
> 
> | 节 | 内容形态 | 关键字段 |
> |---|---|---|
> | Config Version Change Log | 无序列表 | 版本号、改动描述 |
> | Silent Regression | 无序列表 | 起止日期、缺陷描述 |

---

## 【公式解读】

原文无公式。

---

## 【关联】

该 changelog 处于检测模块的文档目录,与以下外部资源形成上下游关系(原文链接):

- **Release logs(主更新来源)**:`https://github.com/facebookresearch/detectron2/releases`——所有 incompatible changes、新特性发布均记录于此,本文档明确建议用户在此处搜索 "incompatible changes" 以查看破坏性变更。
- **API documentation(稳定性锚点)**:`https://detectron2.readthedocs.io/modules/index.html`——stable API 的判定依据是"是否被该文档列出",包括函数/类名、参数、文档化的类属性。
- **`detectron2/projects` 子项目**:作为 internal API 可能被升格为 stable 的"灰度缓冲带",因其内部项目间复用需求,作者承诺对此类 API 也"采用相同的稳定策略"。

需注意:本文档标题虽位于 `CascadedMaskRCNN/docs/notes/`,但内容讨论的是**整个 detectron2 框架**的兼容性,而非 CascadedMaskRCNN 单个模型;所以该 changelog 对所有 detectron2-based 模型(含 Mask R-CNN、Cascaded Mask R-CNN 等)均适用。

---

## 【使用方法】

原文未涉及具体的启用命令、配置项或脚本调用方式。仅给出**查阅方式**与**升级建议**:

1. **查看破坏性变更**:在 [release logs](https://github.com/facebookresearch/detectron2/releases) 中检索关键字 **"incompatible changes"**。
2. **定位静默回归**:若怀疑训练/推理结果异常,可对照"Silent Regression in Historical Versions"列表,确认所用版本是否落在受影响时间段内(04/01/2020–05/11/2020、03/30/2020–04/01/2020、12/19/2019–12/26/2019、–11/9/2019)。
3. **配置版本兼容**:开源用户无需处理 config version,因原文明确"Detectron2's config version has not been changed since open source"。
4. **升级策略选择**:文档明确推荐"作为库使用"而非"fork",以借助上述稳定化机制降低破坏风险。
