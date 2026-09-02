# Backward Compatibility and Change Log

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/notes/changelog.md

# 深度解读:Cascade_RCNN / docs/notes/changelog.md

## 【定位】
本文件是 Detectron2 项目的**向后兼容策略与变更日志说明文档**,面向下游使用者,阐明三类信息:(1) 何时 API 会被改动、改动如何过渡;(2) Config 系统版本演进情况;(3) 历史版本中潜藏的、不报错但会产出错误结果的「静默回归」(silent regression)及其影响时间区间。整体目的是让用户理解:使用该库依赖的风险边界与已知缺陷。

---

## 【技术要点】

1. **API 稳定性分级制度**:Detectron2 将 API 分为两类——(a) 在 [API documentation](https://detectron2.readthedocs.io/modules/index.html) 中列出的函数/类名、参数、文档化的类属性被视为 *stable*,除非文档另行说明; (b) 其他函数/类/属性视为 *internal*,更可能发生变化,但部分会被提升为 stable 待遇。
2. **弃用过渡机制**:Stable API 在必须变更前会触发 `deprecation warning` 给用户留出"合理过渡期",相关记录会写入 [release logs](https://github.com/facebookresearch/detectron2/releases)。可搜索关键字 `incompatible changes` 来定位。
3. **Config 版本变更日志**:共两个版本——v1:`RPN_HEAD.NAME` 重命名为 `RPN.HEAD_NAME`;v2:发布前一批配置项重命名。文档明确说明开源以来 config 版本未再变更,开源用户无需关心。
4. **第三方依赖的相对稳定性定位**:即使存在 break,与 fork 相比,作为库引用 detectron2 的"API 变更频率与范围"显著小于"代码变更",因此更不具破坏性。
5. **静默回归警报清单**:用日期区间标定 4 段已知会"悄悄产出错误结果"的回归窗口,供历史结果核查。
6. **静默回归复现条件**(均为定性条件,无量化阈值):
   - `TRAIN_ON_PRED_BOXES = True` 时精度异常;
   - ResNets 构建不正确;
   - 使用 aspect ratio grouping 时精度下降;
   - Test time augmentation 漏预测最后一类。

---

## 【关键机制与数据】

**工作原理 / 流程(文档所述)**

- 兼容性管理流程:Detectron2 维护 release logs → 在 API 必须改动时先在文档中标注 → 触发 `deprecation warning` → 用户搜索 `incompatible changes` 字符串即可检索所有破坏性变更。
- 静默回归通告机制:不通过报错暴露,而是事先以"日期区间 + 影响范围"形式列出,让用户在审视历史产出时有据可查。

**原文中以"日期区间"形式给出的隐式性能数据(原文):**

| 区间起 | 区间止 | 现象 |
|---|---|---|
| 2019-11-09 之前 | — | TTA(test time augmentation)不预测最后一类 |
| 2019-12-19 | 2019-12-26 | 使用 aspect ratio grouping 导致精度下降 |
| 2020-03-30 | 2020-04-01 | ResNets 未被正确构建 |
| 2020-04-01 | 2020-05-11 | 当 `TRAIN_ON_PRED_BOXES=True` 时精度异常 |

(以上日期与现象均为原文逐字提取,未做推断。)

---

## 【表格解读】

原文无表格。文中以"列表 + 短句"形式承载信息(API 策略要点、Config 版本变更条目、静默回归按日期分条),没有显式的 markdown 表格结构,因此不做表格还原。

---

## 【公式解读】

原文无公式。文档性质为政策说明与变更历史,未涉及任何数学表达式、伪代码或参数化公式。

---

## 【关联】

- **上游 release logs**:`https://github.com/facebookresearch/detectron2/releases`——所有 `incompatible changes` 与新版本发布说明的真正源头,本文仅给出入口指针。
- **API 文档**:`https://detectron2.readthedocs.io/modules/index.html`——判定 API 属于 *stable* 还是 *internal* 的依据面;若某 API 未列于该文档,则按 internal 处理。
- **`detectron2/projects` 路径**:在"内部 API 待遇"那一段被特别点名——由于该项目内部会出于便利而在多个子项目间复用某些未文档化 API,Detectron2 承诺对此类 API 也按 stable 策略处理,并在时机成熟时将其提升为 stable。
- **Config 系统**:本文只触及 `RPN_HEAD.NAME → RPN.HEAD_NAME` 等配置改名这一表面层,未深入机制;真正的 config 加载/合并逻辑需结合 detectron2 主仓 config 模块源码。
- **Cascade_RCNN 子目录关联**:虽然本文位于 modelzoo-pytorch 的 `Cascade_RCNN/docs/notes/` 下,但其内容明显是 detectron2 通用文档的副本/嵌入(指向上述 `facebookresearch/detectron2` 与 `detectron2.readthedocs.io`),即 Cascade_RCNN 训练流程依赖此兼容性契约。

> 注:用户提供的"内部链接"清单为"(无)",故本节外部关联全部来自文档正文中的链接,未引入文档未出现的关联。

---

## 【使用方法】

原文未涉及具体启用方式、配置项或命令行。

本文是一份**政策与变更说明**,而非操作指南。要实际应用其提示,需要:

1. 查阅 [release logs](https://github.com/facebookresearch/detectron2/releases) 检索字符串 `incompatible changes`;
2. 在排查"为什么历史训练结果与现版本对不上"时,按"静默回归"四段日期区间反查 commit;
3. 在修改涉及 `TRAIN_ON_PRED_BOXES`、ResNet 构建、aspect ratio grouping、test time augmentation 的代码时,留意其落入原文标出的回归窗口则结果可能不可信。
