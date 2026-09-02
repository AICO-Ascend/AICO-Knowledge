# 教程 10: 权重初始化

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/init_cfg.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/init_cfg.md

# 一体化深度解读：MMDetection 权重初始化（init_cfg）教程

## 【定位】

本教程系统说明 MMDetection 中基于 `init_cfg` 的模型权重初始化机制——定义 `init_cfg` 的数据结构、`layer`/`override` 键的语义、配置层级覆盖关系、子模块优先级规则，以及代码层、容器层、配置文件层三种声明路径，使开发者能为自定义模型组件获得可控、可复现、可继承的初始化策略。

---

## 【技术要点】

1. **两步初始化流程**：① 在 `model_cfg` 中为模型或其组件定义 `init_cfg`（**子组件的 `init_cfg` 优先级更高，会覆盖父模块**）；② 构建模型后显式调用 `model.init_weights()`，参数按配置文件写法被初始化。

2. **高层 API 调用链（原文流程图式描述）**：
   `model_cfg(init_cfg) → build_from_cfg → model → init_weight() → initialize(self, self.init_cfg) → children's init_weight()`
   —— `init_weights()` 最终会递归到子模块自身的 `init_weight()`。

3. **`init_cfg` 数据类型与三键结构**：类型为 `dict` 或 `list[dict]`，包含三组键：
   - `type` (str)：对应 `INTIALIZERS` 中初始化器名称 + 初始化器参数；
   - `layer` (str 或 list[str])：Pytorch / MMCV 中可学习参数层的类名（如 `'Conv2d'`、`'DeformConv2d'`），**注意不支持 `MultiheadAttention`**（因其不是 weights/bias 属性层）；
   - `override` (dict 或 list[dict])：对**非 `BaseModule` 派生类**但又需要与 `layer` 同方式初始化的子模块进行差异化配置，含 `type`（初始化器+参数）与 `name`（子模块名）。

4. **`layer` 键的两种粒度**：
   - 整模块统一：`init_cfg = dict(type='Constant', layer=['Conv1d','Conv2d','Linear'], val=1)`；
   - 分层差异化：`init_cfg = [dict(type='Constant', layer='Conv1d', val=1), dict(type='Constant', layer='Conv2d', val=2), dict(type='Constant', layer='Linear', val=3)]` → `nn.Conv1d`→val=1, `nn.Conv2d`→val=2, `nn.Linear`→val=3。

5. **`override` 键的三种语义**：
   - 覆盖特定子模块：`override=dict(type='Constant', name='reg', val=3, bias=4)` 覆盖 `init_cfg` 主体的 `val=1, bias=2`；
   - `layer=None` 时仅初始化 `override.name` 所指子模块，`type` 与其他参数可省略；
   - 同时未定义 `layer` 与 `override` → **不初始化任何东西**。
   
6. **两类无效用法（原文示例）**：
   - `override` 缺 `name` 键 → 无效；
   - `override` 有 `name` 但无 `type` 键 → 无效（即便给了 `val`、`bias`）。

7. **预训练模型加载**：`init_cfg = dict(type='Pretrained', checkpoint='torchvision://resnet50')`，通过 `Pretrained` 类型 + checkpoint URI 加载。

---

## 【关键机制与数据】

**工作原理（原文）**：

- 初始化入口在 `BaseModule.__init__` 中接受 `init_cfg`，存储为 `self.init_cfg`；调用 `model.init_weights()` 时，`initialize(self, self.init_cfg)` 会按配置分别对模型自身层（按 `layer` 匹配 Pytorch/MMCV 类名）与 `override` 显式命名的子模块执行对应初始化器，最后**递归触发** `children's init_weight()`，因此子模块自身的 `init_cfg` 自然具有更高优先级。
- `layer` 匹配依据：层必须是带有 `weights` 和 `bias` 属性的类，因此 `MultiheadAttention` 类不在支持范围。
- `override` 设计动机：针对**不继承自 `BaseModule`**、但初始化方式又与 `layer` 列表中类相同的子模块，若其为 `BaseModule` 派生类则无需 `override`（可直接由子模块自身 `init_cfg` 控制）。
- `layer=None` + `override` 模式：等价于"只初始化 `override.name` 所指子模块，且继承父 `init_cfg` 的 `type` 与参数"，因为注释 "self.feat and self.cls 将被 Pytorch 初始化" 表明其它层完全不被改写。

**性能数据**：原文无任何性能/数值基准。

---

## 【表格解读】

原文无表格（仅有 `init_cfg` 字段的列表式描述与代码示例，未出现 markdown 表格）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游依赖 — MMCV 初始化器注册表 `INTIALIZERS`**：`init_cfg['type']` 必须是其中已注册的初始化器名称，初始化器参数透传给对应 MMCV 初始化函数；教程末尾给出 [MMCV 权重初始化文档](https://mmcv.readthedocs.io/en/latest/cnn.html#weight-initialization) 与 MMCV [PR #780](https://github.com/open-mmlab/mmcv/pull/780) 作为权威细节来源。
- **上游依赖 — `mmcv.runner.BaseModule`**：自定义模型必须继承 `BaseModule`（或 `mmdet.models` 中的模型基类），并通过 `super().__init__(init_cfg)` 把 `init_cfg` 注入 `self.init_cfg`，这是后续 `model.init_weights()` 能识别配置的前提。
- **容器组件 — `mmcv.Sequential` / `mmcv.ModuleList`**：可在构造时通过 `init_cfg=XXX` 让容器统一初始化内部子层，使容器自身成为可被 `init_weights()` 识别的初始化单元。
- **配置体系 — `model_cfg`**：模型可通过 `model = dict(type='FooModel', arg1=XXX, arg2=XXX, init_cfg=XXX)` 在配置文件中声明初始化策略，被 `build_from_cfg` 在建模阶段一并消费。
- **YOLOX 仓内关系 — 同仓教程目录**：本文件位于 `docs/zh_cn/tutorials/`，与该目录下其他教程（如数据集、配置、推理等）共享 `model_cfg → build → init_weights → train` 的统一生命周期，**为后续训练/迁移学习教程提供初始权重来源**（尤其是 `Pretrained` + `torchvision://...` checkpoint 用法）。

---

## 【使用方法】

**启用方式（三种声明路径，原文示例）**：

1. **代码中直接初始化**（在 `__init__` 写入字面量 `init_cfg=XXX`）：
   ```python
   from mmcv.runner import BaseModule
   class FooModel(BaseModule):
       def __init__(self, arg1, arg2, init_cfg=XXX):
           super(FooModel, self).__init__(init_cfg)
           ...
   ```

2. **在 `mmcv.Sequential` / `mmcv.ModuleList` 中初始化**：
   ```python
   from mmcv.runner import BaseModule, ModuleList
   class FooModel(BaseModule):
       def __init__(self, arg1, arg2, init_cfg=None):
           super(FooModel, self).__init__(init_cfg)
           ...
           self.conv1 = ModuleList(init_cfg=XXX)
   ```

3. **在配置文件中初始化**：
   ```python
   model = dict(
       ...,
       model=dict(type='FooModel',
                  arg1=XXX, arg2=XXX,
                  init_cfg=XXX),
       ...)
   ```

**配置项（按原文 `init_cfg` 键说明）**：

| 键 | 类型 | 作用 |
|---|---|---|
| `type` | str | `INTIALIZERS` 中已注册的初始化器名 + 参数 |
| `layer` | str 或 list[str] | Pytorch/MMCV 中可学习参数层类名（需含 `weights`/`bias`），如 `'Conv1d'`、`'Conv2d'`、`'Linear'`、`'DeformConv2d'` |
| `override` | dict 或 list[dict] | 对非 `BaseModule` 派生子模块做差异化初始化；含 `type`（初始化器+参数）与 `name`（子模块名） |

**典型命令/取值（原文示例数值）**：

- 统一初始化：`dict(type='Constant', layer=['Conv1d','Conv2d','Linear'], val=1)`
- 分层差异化：`[dict(type='Constant', layer='Conv1d', val=1), dict(type='Constant', layer='Conv2d', val=2), dict(type='Constant', layer='Linear', val=3)]`
- `override` 覆盖：`dict(type='Constant', layer=['Conv1d','Conv2d'], val=1, bias=2, override=dict(type='Constant', name='reg', val=3, bias=4))`
- `layer=None` + `override`：`dict(type='Constant', val=1, bias=2, override=dict(name='reg'))`
- 预训练：`dict(type='Pretrained', checkpoint='torchvision://resnet50')`

**触发命令**（原文）：在完成第 1 步声明 `init_cfg` 后，必须**显式调用 `model.init_weights()`** 才执行实际参数写入。
