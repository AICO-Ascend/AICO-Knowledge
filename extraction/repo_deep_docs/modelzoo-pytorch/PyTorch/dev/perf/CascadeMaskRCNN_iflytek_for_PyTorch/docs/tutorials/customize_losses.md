# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/customize_losses.md

# 一体化深度解读:Tutorial 6 — Customize Losses

---

## 【定位】

本文是 MMDetection 框架面向用户(尤其是算法研究员/工程师)的一份**实战型教程文档**,旨在解决一个具体问题:**当框架内置的损失函数默认配置无法适配新数据集或新模型时,用户该如何系统化地"自定义损失"(Customize Losses)**。文档以 Focal Loss 为完整示范案例,先抽象出损失计算的统一四步流水线,再将所有可定制的维度归并为两类操作 — **"Tweaking"(微调现有超参/归约方式/标量权重)** 与 **"Weighting"(逐元素加权)** — 并指出每一类操作在配置文件中对应的修改位置。简言之,本文描述的能力是:**在不改动框架源码的前提下,通过对 config 文件与 head 模块中 `get_targets` 方法行为的理解,完成对检测损失从超参、归约、标量权重到逐元素权重的全链路定制**。

---

## 【技术要点】

1. **损失计算的统一四步流水线(Computation Pipeline)**:从 `(pred, target, weights)` 输入到最终标量 loss,固定经过四步 — ① 通过 loss kernel 函数得到 **element-wise / sample-wise** 损失;② 用 **weight tensor 按元素加权**;③ 将损失 tensor **归约(Reduce)为标量**;④ 用 **标量再次加权**。后文所有"修改哪一步"的讨论都建立在这套抽象之上。

2. **两类定制范式:Tweaking vs. Weighting**:
   - **Tweaking** 对应步骤 ①③④ — 主要通过**配置文件(config)即可完成**,不需要写代码;
   - **Weighting** 对应步骤 ② — 逐元素权重与具体 head 强耦合,**无法仅靠 config 完成**,需要在对应 head 的 `get_targets` 方法中产出 `label_weights` / `bbox_weights` 等张量。

3. **Tweaking 的三大可改维度(以 Focal Loss 为例)**:
   - **步骤 ① 超参**:Focal Loss 构造器中显式列出 `use_sigmoid=True, gamma=2.0, alpha=0.25, reduction='mean', loss_weight=1.0`,其中 **`gamma=1.5, alpha=0.5`** 是文档给出的"替换示范值";
   - **步骤 ③ 归约方式**:将 `reduction` 由默认 `'mean'` 改为 `'sum'`;
   - **步骤 ④ 标量损失权重**:在多任务(multi-task)场景下控制分类损失与回归损失的相对比重,文档示范将 `loss_weight` 由 `1.0` 改为 `0.5`。

4. **Focal Loss 构造器与 config 的"一一对应"关系**:文档明确指出"`The following code sniper are the construction method and config of FL respectively, they are actually one to one correspondence.`" — 即 Python `__init__` 形参与 config dict 的 key 一一对应,这一约束是 config-only 定制成立的前提。

5. **Weighting(逐元素加权)的本质**:用与损失 tensor **形状相同的 weight tensor** 逐元素相乘,使损失中不同条目获得不同缩放;与 Tweaking 的"标量权重"在粒度上有本质区别。

6. **两类 Weighting 的具体载体**:`label_weights`(用于分类损失)、`bbox_weights`(用于 bbox 回归损失),均**在对应 head 的 `get_targets` 方法内产出**;文档以 `ATSSHead` 为示例 — 它**继承自 `AnchorHead` 但覆写了 `get_targets` 方法**,从而产出与父类不同的 `label_weights` 与 `bbox_weights`,这是 weighting 修改在代码层面的具体落点。

---

## 【关键机制与数据】

### 1. 损失计算的工作原理(原文拆解)

原文明确给出的四步:

1. Get **element-wise** or sample-wise loss by the loss kernel function.
2. Weighting the loss with a weight tensor **element-wisely**.
3. Reduce the loss tensor to a **scalar**.
4. Weighting the loss with a **scalar**.

→ **逐元素粒度从细到粗的链条**:kernel 输出(逐元素 / 逐样本)→ 逐元素 weight tensor 加权(仍为逐元素)→ reduce 归约为 scalar → scalar 二次加权。**步骤 ② 与 ③ 之间的粒度跳跃是理解"两类定制"分野的关键**。

### 2. Tweaking 三步骤的可视化数据流

原文用 FL 的 `__init__` 与对应 config 的并列展示,明确各 key 的**默认值与示范替换值**:

| 维度 | 步骤归属 | config key | 原文默认值 | 原文示范替换值 |
|---|---|---|---|---|
| 是否使用 sigmoid | 步骤 ① | `use_sigmoid` | `True` | 未改 |
| gamma | 步骤 ① | `gamma` | `2.0` | `1.5` |
| alpha | 步骤 ① | `alpha` | `0.25` | `0.5` |
| 归约方式 | 步骤 ③ | `reduction` | `'mean'` | `'sum'` |
| 标量损失权重 | 步骤 ④ | `loss_weight` | `1.0` | `0.5`(针对 `loss_cls` 的示范场景) |

(注:此表为基于原文 Python 代码块逐字提取并按步骤归位,非原文已有表格的复刻 — 见下节"表格解读"。)

### 3. ATSSHead.get_targets 的方法签名(原文逐字摘录)

```python
class ATSSHead(AnchorHead):
    ...
    def get_targets(self,
                    anchor_list,
                    valid_flag_list,
                    gt_bboxes_list,
                    img_metas,
                    gt_bboxes_ignore_list=None,
                    gt_labels_list=None,
                    label_channels=1,
                    unmap_outputs=True):
```

→ 原文用这一签名来**具体指明 weighting 定制应修改的方法位置**,签名与 `AnchorHead.get_targets` 同构但行为不同(被覆写)。

### 4. 性能数据

**原文未涉及任何性能/精度/时延数字**,亦无 benchmark 表格。本文聚焦"如何改",不涉及"改完效果如何"。

---

## 【表格解读】

**原文无表格。**

(说明:原文中所有结构化信息都以 **Python 代码块**形式给出,而非 markdown 表格。文档共出现 5 个代码块:1 个 FL 构造器、4 个对应 config 的 dict。)

为便于读者对照理解,以下将原文 5 段代码块**逐字还原**为 markdown 表格(此表非原文表格,系作者为解读而做的代码-表格化整理,**所有字段值均一字不改取自原文**):

### 表 A:原文 FL 构造器与 4 段 config 的逐字对照

| 出处 | 原文逐字摘录 |
|---|---|
| FL 构造器 | ```python @LOSSES.register_module() class FocalLoss(nn.Module):     def __init__(self,                  use_sigmoid=True,                  gamma=2.0,                  alpha=0.25,                  reduction='mean',                  loss_weight=1.0): ``` |
| config:默认/基础 | ```python loss_cls=dict(     type='FocalLoss',     use_sigmoid=True,     gamma=2.0,     alpha=0.25,     loss_weight=1.0) ``` |
| config:改超参(步骤 ①) | ```python loss_cls=dict(     type='FocalLoss',     use_sigmoid=True,     gamma=1.5,     alpha=0.5,     loss_weight=1.0) ``` |
| config:改归约(步骤 ③) | ```python loss_cls=dict(     type='FocalLoss',     use_sigmoid=True,     gamma=2.0,     alpha=0.25,     loss_weight=1.0,     reduction='sum') ``` |
| config:改标量权重(步骤 ④) | ```python loss_cls=dict(     type='FocalLoss',     use_sigmoid=True,     gamma=2.0,     alpha=0.25,     loss_weight=0.5) ``` |

**逐行解读**:
- **第 1 行(FL 构造器)**:这是所有后续 config dict 的"母版",5 个形参顺序为 `use_sigmoid → gamma → alpha → reduction → loss_weight`,与下文的 config key 严格一一对应;`reduction='mean'` 与 `loss_weight=1.0` 都是默认值,**强调"大多数情况下用户不必重写它们"**。
- **第 2 行(基础 config)**:与构造器签名一一对应,**复现了默认行为** — `gamma=2.0, alpha=0.25, reduction 走默认 mean, loss_weight=1.0`。
- **第 3 行(改超参)**:仅 `gamma` 与 `alpha` 被替换(`2.0→1.5`, `0.25→0.5`),其它字段保持默认;这是**步骤 ① 的唯一改动面**。
- **第 4 行(改归约)**:在默认 config 基础上**追加** `reduction='sum'` — 注意原文未替换而是新增,因为 `'mean'` 是构造器默认值,在 dict 中显式写出即为覆盖;这一步属于**步骤 ③**。
- **第 5 行(改标量权重)**:把 `loss_weight` 从 `1.0` 改为 `0.5`,其它不变 — 这一改动针对的是**多任务场景下分类损失 vs. 回归损失的相对比重**,是**步骤 ④** 的典型用例。

### 表 B:逐元素权重相关的关键代码摘录(原文 ATSSHead.get_targets 签名)

| 出处 | 原文逐字摘录 |
|---|---|
| ATSSHead 继承与覆写声明 | ```python class ATSSHead(AnchorHead):     ...     def get_targets(self,                     anchor_list,                     valid_flag_list,                     gt_bboxes_list,                     img_metas,                     gt_bboxes_ignore_list=None,                     gt_labels_list=None,                     label_channels=1,                     unmap_outputs=True): ``` |

**逐行解读**:
- **`class ATSSHead(AnchorHead)`** — 关键事实:**ATSSHead 并非全新实现,而是在 AnchorHead 基础上覆写 `get_targets`**。这是 weighting 定制在代码层面的"切入口" — 想改 weighting,**不必从零写 head**,只需仿照 ATSSHead 的模式**覆写父类方法、产出不同的 `label_weights` / `bbox_weights`**。
- **方法签名中的 8 个形参**:与 AnchorHead 完全同构;后续 5 个带默认值的参数(`gt_bboxes_ignore_list=None, gt_labels_list=None, label_channels=1, unmap_outputs=True`)表明该方法在"忽略区域 / 类别通道 / 是否 unmap"上都有可调旋钮。

---

## 【公式解读】

**原文无公式。**

(说明:文档通篇未出现任何 LaTeX 数学公式或伪代码形式的公式块 — 既无损失函数的数学定义(如 FL 的 -α(1-p)^γ log p 形式未在文中出现),也无归约/加权的算式表达。整个"流水线"完全用自然语言步骤编号 + Python 代码块描述。这是本文的一个特点:工程导向,抽象层级停留在"config key → 数值"这一层级,而非数学推导层级。)

---

## 【关联】

根据文末标注,本文档**无内部链接(无)**。但原文在正文流中显式提到了两个**外部 GitHub 链接**(指向 MMDetection 官方仓库的源码),它们构成了本文与 MMDetection 框架其它模块的关联锚点:

### 1. 与 `mmdet/models/losses/focal_loss.py` 的关联(对应"Tweaking"示例)

原文第一句明确说 "Here we take [Focal Loss (FL)](https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/losses/focal_loss.py) as an example." — 这意味着:
- **本文是 `focal_loss.py` 的"用户侧文档"**:文档中展示的 `FocalLoss` 类、`@LOSSES.register_module()` 装饰器、构造器签名,都直接对应 `focal_loss.py` 中的源码实现;
- **"config 中每多写一个 key,源码构造器就多接一个形参"**:这种一一对应是 MMDetection 注册器机制(`LOSSES.register_module`)的产物,本文档的整套 config-only 定制范式**完全依赖**这一注册机制才能成立 — 也就是说,本文档隐式假设读者了解 `Registry` 与 `build_from_cfg` 的工作原理。

### 2. 与 `mmdet/models/dense_heads/atss_head.py` 与 `anchor_head.py` 的关联(对应"Weighting"示例)

原文称 "Here we take [ATSSHead](https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/dense_heads/atss_head.py#L530) as an example, which inherit [AnchorHead](https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/dense_heads/anchor_head.py) but overwrite its `get_targets` method which yields different `label_weights` and `bbox_weights`." — 这意味着:
- **本文是 ATSS 论文思想(Adaptive Training Sample Selection)在工程上的"二次注解"**:ATSS 与其父类 AnchorHead 的关键差异不在 loss 本身,而在 `get_targets` 产出的 weighting 张量 — 这是 weighting 范式最经典的工业范例;
- **文档的潜在阅读顺序**:读者应在掌握 `AnchorHead.get_targets` 之后再看 `ATSSHead.get_targets`,才能体会"覆写 get_targets 即覆写 weighting"这一设计模式;本文档相当于这一模式的**入门导览**。

### 3. 与 MMDetection 其它 Tutorial 的隐式上下游

虽然文末链接列表为空,但从命名"Tutorial 6"可推断其位于一个教程系列中(通常 Tutorial 1-5 覆盖 install / inference / dataset / model / 等);**本文属于"模型/损失定制"专题,与前序教程中的 config 用法、head 工作机制存在强依赖**。文档本身不显式给出这些依赖链,需要读者自行串联。

---

## 【使用方法】

### 1. 启用方式

原文未提供"安装/启用"层面的命令(如 `pip install`、注册新 loss 等),因为本文面向**已安装好 MMDetection 的用户**,讨论的是**怎么改 config**,而非**怎么把框架跑起来**。

### 2. 配置项(Config 项)汇总

将原文所有可改的 config key 及其作用整理如下(全部来自 FL 示例,**仅适用于分类损失 `loss_cls`;`loss_bbox` 的字段名/取值可能不同,原文未示范**):

| config key | 所属步骤 | 数据类型(按原文) | 默认值(原文) | 作用(按原文) |
|---|---|---|---|---|
| `type` | — | str | `'FocalLoss'` | 损失类名,经 `LOSSES` 注册器解析 |
| `use_sigmoid` | 步骤 ① | bool | `True` | 是否在 loss kernel 前对预测做 sigmoid |
| `gamma` | 步骤 ① | float | `2.0` | FL 聚焦参数 |
| `alpha` | 步骤 ① | float | `0.25` | FL 类别平衡因子 |
| `reduction` | 步骤 ③ | str | `'mean'` | 归约方式(`'mean'`/`'sum'` 等) |
| `loss_weight` | 步骤 ④ | float | `1.0` | 多任务下控制该损失相对权重 |

### 3. 修改逐元素权重的步骤(步骤 ②,无法仅靠 config)

按原文指路:
1. 定位到目标 head 的 `get_targets` 方法(例如 `ATSSHead` 在 `mmdet/models/dense_heads/atss_head.py:530`);
2. 在该方法返回前修改或覆写 `label_weights` / `bbox_weights` 张量的构造逻辑;
3. 若是从零实现,采用 `ATSSHead → AnchorHead` 的继承覆写模式:继承父类 head,只重写 `get_targets` 即可,**保留其它机制不变**。

### 4. 命令/命令行

**原文未涉及任何命令行调用**(如 `python tools/train.py ...`、`--cfg-options` 等)。本文档完全聚焦于"config 文件里写什么",不涉及训练脚本层面的用法。如需命令行覆盖 config,需自行参考其它教程(原文未给出)。

### 5. 注意事项(由原文直接推得,非臆造)

- **"Tweaking" 与 "Weighting" 的边界**:能改 config 的就改 config(步骤 ①③④);改不了再动 head 代码(步骤 ②);
- **构造器与 config 一一对应**:新增 config key 必须同步修改构造器签名,否则 `build_from_cfg` 会因多余 key 或缺失 key 报错(此为注册器机制推论,非原文直述);
- **多任务权重的语境性**:`loss_weight` 在不同模型/不同数据上"highly context related"(原文表述),需结合具体任务调优,本文不给出推荐数字。
