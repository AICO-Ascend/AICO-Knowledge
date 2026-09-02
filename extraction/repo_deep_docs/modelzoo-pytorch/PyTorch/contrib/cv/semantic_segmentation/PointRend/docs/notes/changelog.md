# Change Log and Backward Compatibility

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/notes/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/notes/changelog.md

# PointRend changelog 文档深度解读

## 【定位】

本文件是 PointRend 项目(基于 detectron2 框架实现)对外发布的**变更日志与向后兼容性说明**,核心目的是:告知用户该项目作为研究型代码库的**API 稳定性策略、配置版本演进历史,以及在历史上曾经出现过但未被显式告警的"静默回归"(silent regression)问题清单**,以便下游使用者在升级/复现实验时能够快速定位潜在风险与已修复缺陷。

## 【技术要点】

1. **API 稳定性分级**(原文核心机制)
   - **稳定(stable)API**:列入官方 [API 文档](https://detectron2.readthedocs.io/modules/index.html) 的"函数/类名、参数、文档化的类属性",被认定为稳定,变更前会通过 *deprecation warning* 给出"合理过渡期",并在 release log 中记录。
   - **内部(internal)API**:未列入官方文档的函数/类/属性,被认定为内部接口,允许频繁变更。
   - **准稳定(semi-stable)API**:在 `detectron2/projects` 目录下被项目间复用的内部接口,可能被提升为稳定 API 并享受同等待遇。
   - **实验性(experimental)项目**:`detectron2/projects` 下或以 `detectron2.projects` 导入的所有项目,均视为研究性质,API 可随时变更。

2. **默认行为类接口的特殊约定**
   - 类名/函数名中含 "default" 字样,或文档明确说明会产出"default behavior" 的接口,其行为可能在新增特性时发生变化。

3. **配置版本演进**(原文给出两个版本节点)
   - **v1**:将 `RPN_HEAD.NAME` 重命名为 `RPN.HEAD_NAME`。
   - **v2**:在发布前一次性批量重命名大量配置项。
   - **现状声明**:自开源以来,detectron2 的 config version **未再发生变化**,开源用户无需担心。

4. **"静默回归"问题清单**(4 条带具体日期范围的缺陷记录)
   - 04/01/2020 – 05/11/2020: 当 `TRAIN_ON_PRED_BOXES=True` 时精度异常。
   - 03/30/2020 – 04/01/2020: ResNet 构建存在错误。
   - 12/19/2019 – 12/26/2019: 使用 aspect ratio grouping 导致精度下降。
   - – 11/9/2019: Test-time augmentation 无法预测最后一类。

5. **变更追踪指引**:用户可于 [release logs](https://github.com/facebookresearch/detectron2/releases) 中搜索关键字 **"incompatible changes"** 来检索不兼容变更。

6. **"升级 vs Fork"的官方立场**:即便存在破坏性变更,作为库依赖使用 detectron2 仍比 fork 该仓库更"低侵入",因为 API 变更的频率与范围远小于代码层级的变更。

## 【关键机制与数据】

### 工作原理 / 数据流

- 文档并不描述任何模型训练或推理的数据流,而是描述了**项目元信息**层面的治理机制:
  - **API 治理流水线**:外部文档(readthedocs)→ 文档化的部分被锁定为 stable;未文档化部分归为 internal;projects/ 内部被跨项目复用的接口享受"准稳定"待遇。
  - **变更传播路径**:`deprecation warning`(代码层) → `release logs`(GitHub)(版本说明层) → 本 changelog(项目层)。

### 性能 / 回归数据(原文)

- **静默回归时间窗**(均以"起止日期 + 缺陷描述"的形式记录):
  - **04/01/2020 – 05/11/2020**:`TRAIN_ON_PRED_BOXES=True` 时出现"bad accuracy",即正确率非预期下降,具体下降幅度**原文未量化**。
  - **03/30/2020 – 04/01/2020**:ResNet 构建错误("not correctly built"),具体错误内容与影响范围**原文未列出**。
  - **12/19/2019 – 12/26/2019**:aspect ratio grouping 触发精度下降("drop in accuracy"),具体幅度**原文未列出**。
  - **– 11/9/2019**(原文起始日期未完整写出):test-time augmentation **漏预测最后一个类别**("does not predict the last category")。

> 注意:以上 4 条记录仅提供**时间窗与症状描述**,未给出具体性能数字、触发条件复现脚本或影响模型清单。

## 【表格解读】

**原文无表格。**

(整篇 changelog 全部以项目符号列表 + 日期范围呈现,未使用任何 markdown / HTML 表格结构。)

## 【公式解读】

**原文无公式。**

(文档中未出现任何数学公式、LaTeX 表达式或伪代码块。)

## 【关联】

由于文末提供的**内部链接列表为"(无)"**,即原文未显式给出任何站内的上下游交叉引用,因此本节仅基于文档内文出现的**外部链接与命名实体**梳理关联关系:

- **上游框架:detectron2**
  - PointRend 项目文档明确指向 [detectron2 releases](https://github.com/facebookresearch/detectron2/releases) 作为正式变更说明的唯一权威源。
  - 本文档的"配置版本变更"("Config Version Change Log")、"静默回归"等章节,均描述的是 **detectron2 主仓**的历史问题,而非 PointRend 自身独立的事件。

- **API 文档体系:[detectron2 readthedocs](https://detectron2.readthedocs.io/modules/index.html)**
  - 文档将"是否被该 API 文档收录"作为判断接口是否属于 *stable API* 的硬性标准,即 **API 文档 ⇨ 稳定性契约** 的单向关系。

- **项目目录结构:`detectron2/projects/`**
  - 与"stable / internal / experimental"三类 API 的划分存在直接关联——`projects/` 下的所有内容被一律归为实验性,且该目录内的接口如果被多个项目复用,可被"升级"为 stable。

- **`TRAIN_ON_PRED_BOXES` 等配置项**
  - 出现在"静默回归"清单中,暗示其与训练流程(可能涉及 RPN / proposal 训练回路)直接耦合,但 PointRend 中是否复用了该路径,本文档未做关联说明。

- **RPN 相关配置(`RPN_HEAD.NAME` / `RPN.HEAD_NAME`)**
  - 出现在"Config Version Change Log"的 v1 中,说明 detectron2 在历史上曾对**区域建议网络(RPN)模块的配置命名**做过一次重命名,PointRend 作为上层语义分割模块,继承自该配置体系。

## 【使用方法】

本 changelog **不涉及启用方式、配置项或命令**,其内容定位为"元信息说明",因此:

- **启用方式**:原文未涉及。
- **配置项**:仅以"兼容性提示"形式提及了两个**历史重命名**点 —— `RPN_HEAD.NAME → RPN.HEAD_NAME`(v1)以及 v2 批量重命名,**并未给出当前可用的配置项或推荐配置**。
- **命令**:原文未涉及任何 CLI / 训练 / 推理命令。

如需获取本项目实际的使用方法(模型调用、权重加载、推理脚本等),需参考 PointRend 项目内的其它文档(README、`getting_started.md`、`models/README.md` 等),**本 changelog 文件本身不提供**。
