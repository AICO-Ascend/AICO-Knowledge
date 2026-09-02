# Backward Compatibility and Change Log

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/notes/changelog.md

# 一体化深度解读:Faster_Mask_RCNN_for_PyTorch/docs/notes/changelog.md

---

## 【定位】

本篇文档描述 Detectron2 库的**向后兼容性与变更日志(Beta Test Log)**策略与历史记录,目的是告知用户在 Detectron2 演进过程中如何识别/应对 API 变更、配置文件版本变更以及历史上"静默回归(silent regression)"可能导致的隐性精度问题,从而降低升级/调试成本。

---

## 【技术要点】

1. **发布追踪来源**:版本变更记录集中托管于 `https://github.com/facebookresearch/detectron2/releases`,用户应据此查看新更新。

2. **稳定 API vs 内部 API 的分层契约**:
   - **稳定 API**:API 文档(https://detectron2.readthedocs.io/modules/index.html)中列出的函数/类名、参数、文档化的类属性。除非文档另注,否则被视为 stable。修改前会先经过合理的**弃用警告期**,并在 release log 中说明。
   - **内部 API**:未列入文档的函数/类/属性,变更可能性更高。但对 `detectron2/projects` 下项目间为方便起见可能共用的内部 API,可被"提升"按 stable API 策略对待。

3. **第三方升级建议**:即使存在破坏性变更,作为库使用比 fork 更不易受干扰,因为 API 变更频率与范围小于代码变更。识别方式:在 release log 中搜索 "incompatible changes"。

4. **配置文件版本变更**:
   - **v1**:`RPN_HEAD.NAME` 重命名为 `RPN.HEAD_NAME`。
   - **v2**:正式发布前对大量配置项进行批量重命名。
   - **现状**:Detectron2 自开源以来 config 版本未再变更,开源用户无需关心。

5. **静默回归(可能引发不正确结果且难以调试)清单**(均为原文逐字条目):
   - **2020-04-01 至 2020-05-11**:`TRAIN_ON_PRED_BOXES=True` 时精度错误(Bad accuracy)。
   - **2020-03-30 至 2020-04-01**:ResNet 构建不正确(ResNets are not correctly built)。
   - **2019-12-19 至 2019-12-26**:使用 aspect ratio grouping 导致精度下降。
   - **至 2019-11-09**:测试时增强(test time augmentation)未预测最后一类别(does not predict the last category)。

6. **变更哲学**:Detectron2 是研究性质(research nature)项目,可能有向后不兼容变更;但通过弃用警告期与文档化来减少对用户的打断。

---

## 【关键机制与数据】

**工作原理/兼容性机制(原文表述)**:
- 原文:"APIs listed in API documentation ... are considered stable unless otherwise noted in the documentation. They are less likely to be broken, but if needed, will trigger a deprecation warning for a reasonable period before getting broken, and will be documented in release logs."
  → 机制:稳定 API 变更前先进入"弃用警告 → 文档化记录于 release log → 实际破坏"三阶段流程。
- 原文:"Others functions/classes/attributes are considered internal, and are more likely to change."
  → 机制:内部 API 不保证稳定性,但与 `detectron2/projects` 路径下的耦合项可能被"提升"为 stable 待遇。
- 原文:"the frequency and scope of API changes will be much smaller than code changes."
  → 含义:库使用者受 API 变更的影响小于代码整体变更。

**配置版本机制(原文表述)**:
- 原文:"Detectron2's config version has not been changed since open source."
  → 数据点:自开源起,config 版本号未发生新版本变更;仅有 v1、v2 两次历史重命名。
- v1 机制:把 `RPN_HEAD.NAME` 单项重命名为 `RPN.HEAD_NAME`(将命名空间从"head"维度归入 RPN 主体下)。
- v2 机制:在正式发布前对"一批(many)"配置项执行批量重命名。

**静默回归数据点(原文表述)**:
| 时间窗口 | 触发条件/现象 |
|---|---|
| 2020-04-01 → 2020-05-11 | `TRAIN_ON_PRED_BOXES=True` → Bad accuracy |
| 2020-03-30 → 2020-04-01 | ResNets 错误构建 |
| 2019-12-19 → 2019-12-26 | aspect ratio grouping → 精度下降 |
| 至 2019-11-09 | Test time augmentation 未预测最后类别 |

---

## 【表格解读】

原文无表格。

(可逐字呈现的"表格"原文并未以 Markdown 表格形式存在;仅"静默回归"一节以项目符号列表形式枚举了 4 个时间窗口与对应问题,见上文【关键机制与数据】。)

---

## 【公式解读】

原文无公式。

---

## 【关联】

本篇为 Detectron2 生态的"治理类"文档,与其他说明性/操作类文档存在如下隐含关联(基于原文措辞推断,均为原文直接提及或指向):

- **API 文档**:原文链接 `https://detectron2.readthedocs.io/modules/index.html` —— 本篇定义了 stable API 的判定边界,即"API 文档中列出者 = stable",因此本篇是该 API 文档的"契约附则"。
- **Release Logs**:原文链接 `https://github.com/facebookresearch/detectron2/releases` —— 本篇明确指引用户在该处查找"incompatible changes"关键字以定位破坏性变更,Release Logs 是本篇的"变更事实源"。
- **`detectron2/projects` 子目录**:原文提及库内某些 API 因项目间方便被共用而"按 stable 策略对待",暗示 `detectron2/projects` 是 stable 边界被扩展的实际受益对象。
- **配置系统(Config System)**:本篇的 v1/v2 配置变更条目与 Detectron2 配置加载/重命名工具(如 `config.dump_versions` 类机制,虽原文未直接提及其工具名)存在治理上的上下游关系——配置重命名的"消费方"是配置加载层。
- **Faster_Mask_RCNN_for_PyTorch 模型仓自身**:本篇被收录在 Faster_Mask_RCNN_for_PyTorch 的 docs/notes/ 路径下,作为该模型仓的兼容性与变更说明;但 Faster_Mask_RCNN 训练侧若使用 `TRAIN_ON_PRED_BOXES=True`、aspect ratio grouping、test time augmentation,需特别注意上述静默回归时间窗口内的版本风险。

> 原文内部链接信息标注为"(无)",本节"关联"仅基于原文内嵌的外部链接与措辞建立。

---

## 【使用方法】

原文未涉及具体启用方式、配置项命令或操作步骤。

可从原文直接获得的使用方式仅为以下**查阅/检索方式**(而非代码配置):

1. 查看新版本更新:访问 `https://github.com/facebookresearch/detectron2/releases`。
2. 判断 API 是否稳定:查阅 `https://detectron2.readthedocs.io/modules/index.html` 中是否列出了相应函数/类/属性;若列出且文档未另注"unstable",则视为 stable。
3. 定位破坏性变更:在 release logs 中搜索关键字 `incompatible changes`。
4. 排查静默精度问题:若用户在 2019-11-09 ~ 2020-05-11 区间内的 Detectron2 版本上遇到精度异常,应参照原文列出的 4 条 silent regression 时间窗口,确认是否命中了已知问题并升级到修复版本。
5. 配置文件兼容性:若使用极早期版本的 Detectron2 配置,可能涉及 `RPN_HEAD.NAME → RPN.HEAD_NAME` 等 v1/v2 重命名迁移;自开源后无进一步 config 版本变更,无需担心新版本破坏配置兼容性。

> 注:以上均严格来自原文措辞;原文未提供具体的配置开关、训练命令、推理命令或启用 flag,故不补充原文以外的操作步骤。
