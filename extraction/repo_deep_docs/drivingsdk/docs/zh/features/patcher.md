# 一键Patcher（快速上手）

> 仓 `drivingsdk` · 路径 `docs/zh/features/patcher.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/drivingsdk/docs/zh/features/patcher.md

# 一键 Patcher（快速上手）深度解读

---

## 【定位】

本文档是华为昇腾 Driving SDK 中「一键 Patcher」特性的快速上手指南，旨在解决**开源自动驾驶模型从 CUDA 生态迁移到昇腾 NPU 平台时的零侵入适配问题**——通过 Monkey Patch 运行时替换机制，让用户在不动一行原始模型代码的前提下完成 CUDA → NPU 的迁移。

---

## 【技术要点】

1. **零侵入迁移框架**：基于 Monkey Patch 机制，在程序运行时动态替换模块、类、函数或方法的属性，实现"不修改原始代码的一个字符"的 CUDA → NPU 迁移。

2. **三级抽象模型**：`AtomicPatch`（单点替换）→ `Patch`（组合多相关 AtomicPatch）→ `Patcher`（管理器），外加预配置的 `default_patcher` 实例开箱即用。

3. **三类导入控制 API**：
   - `skip_import("<cuda_module>")`：跳过昇腾环境不存在的模块
   - `replace_import("<old>", "<new>")`：整模块替换导出
   - `inject_import("<src>", "<name>", "<target>")`：补回父模块缺失的导出

4. **辅助工具能力**：内置 `with_profiling()`（性能采集）、`with_precision_debugger()`（精度采集）、`brake_at(<step>)`（训练早停）、`allow_internal_format()`（允许 NPU 内部格式）。

5. **依赖声明装饰器**：`@with_imports("module")` 在补丁函数中声明所依赖的外部模块，确保 patcher 正确处理导入顺序。

6. **物理文件隔离**：推荐将迁移代码集中在 `migrate_to_ascend/` 目录下，与原始代码物理解耦，便于上游升级维护。

---

## 【关键机制与数据】

**工作原理（原文）**：一键 Patcher 的核心是 Monkey Patch 运行时替换——在 `apply()` 时，patcher 遍历注册的 `AtomicPatch`，将每个 target 路径（如 `"mmcv.ops.msda.forward"`）的属性动态指向 replacement（NPU 版本）。模型原始代码中对 `mmcv.ops.msda.forward()` 的调用，在 `apply()` 之后实际执行的是 NPU 实现，代码文本零变化。

**执行时机约束（原文）**：`apply()` 必须在所有其他 `import` 之前调用。原因是 Patcher 通过替换模块属性实现补丁——如果目标模块已被导入且其属性已被其他模块引用，补丁将无法生效。

**环境链（原文）**：文档通过 `patcher_env.png` 图示了 Patcher 的运行环境，通过 `patcher_behind_apply.png` 图示了 `apply()` 背后的内部过程。

**预定义补丁的覆盖范围（原文数据）**：框架内置预定义补丁共覆盖 6 个第三方库——mmcv（8 个补丁）、mmengine（1 个）、mmdet（4 个）、mmdet3d（2 个）、numpy（1 个）、torch（2 个），另有 `torch_scatter`（1 个）、`transformers`（1 个，`>=4.51.0`）、`diffusers`（1 个，`==0.35.1`）需要手动添加。在 21 个内置补丁中，✅ 默认启用 14 个，❌ 需手动添加 7 个。

---

## 【表格解读】

### 表 1：快速上手与功能详解文档的关系

| 文档 | 定位 | 适用场景 |
|------|------|--------------|
| 本文档（快速上手） | 功能性使用：是什么、为什么、怎么最快跑通 | 首次使用、需要快速接入模型 |
| [一键Patcher（功能详解）](./patcher_features.md) | 各特性的底层逻辑、实现原理与接口的具体说明（参数、示例、注意事项） | 需要深入配置某个功能、排查不生效原因 |

**逐行解读**：
- 第一行定义了本文档的边界——只做功能性快速接入，覆盖背景、最小示例、核心概念。
- 第二行指向 `patcher_features.md` 作为深度参考，用于接口参数、底层实现原理的查阅。
- 两文档形成"快速上手 → 功能详解"的二级文档结构。

---

### 表 2：直接修改模型源代码的传统做法的问题

| 问题 | 说明 |
|------|------|
| 代码管理混乱 | 原始代码与适配代码混杂，难以维护 |
| 升级困难 | 上游更新后需要重新适配 |
| 三方库改动成本高 | 修改mmcv等库的自定义算子后需要重新编译 |

**逐行解读**：
- "代码管理混乱"：CUDA 适配代码散落各处，与原始代码混在一起，导致 git diff 噪音大、阅读困难。
- "升级困难"：上游开源模型一旦更新，所有手工修改的适配点需重新对齐，工作量线性叠加。
- "三方库改动成本高"：mmcv 等库含自定义 CUDA 算子，修改后需重新编译整套库，环境管理负担重。
- 该表是 Patcher 特性提出的**反例基线**，用以对比后文"解决方案"表的零侵入优势。

---

### 表 3：一键 Patcher 解决的五大问题

| 问题 | 解决方式 |
|------|----------|
| 迁移工作量大、门槛高 | 封装常见适配为预定义补丁，一行代码即可应用 |
| 修改三方库源码需重新编译 | 运行时替换，无需修改和编译mmcv等库的源代码 |
| 适配代码与原始代码耦合 | 补丁独立于模型代码，源代码与迁移代码完全解耦 |
| 迁移经验难以复用 | 将已验证的适配方案沉淀为预定义补丁，新模型可直接复用 |
| 缺少昇腾环境的实用功能 | 内置性能采集（Profiling）、训练早停（Brake）等工具 |

**逐行解读**：
- 第 1 行：降低使用门槛，预定义补丁通过 `default_patcher.apply()` 一行代码激活。
- 第 2 行：运行时替换规避了"重编译 mmcv"这个最重的环节。
- 第 3 行：补丁代码物理隔离（推荐 `migrate_to_ascend/` 目录），实现解耦。
- 第 4 行：经验沉淀机制——同类问题（如 mmcv 的 `MultiScaleDeformableAttention`）一次写好，多模型复用。
- 第 5 行：在零侵入替换之外，额外提供 `with_profiling()`、`brake_at()` 等 NPU 平台专用工具。

---

### 表 4：三类导入控制 API 的选用场景

| 场景 | 推荐API | 典型例子 |
|------|---------|----------|
| 模块在昇腾环境根本不存在，但后续路径并不会真正执行它 | `skip_import()` | `flash_attn`、`torch_scatter`只在顶部被import，真实执行路径会被NPU patch接管 |
| 问题就发生在模块import边界，需要把整个模块入口换掉 | `replace_import()` | DiffusionDrive把`projects.mmdet3d_plugin.ops.deformable_aggregation`的导出切到NPU实现 |
| 类/函数定义在子模块里，但父模块没有正确导出，导致`from pkg import Name`失败 | `inject_import()` | DiffusionDrive把`V1SparseDrive`、`V1SparseDriveHead`等类补回`projects.mmdet3d_plugin.models` |

**逐行解读**：
- 第 1 行（`skip_import`）：针对**"模块不存在但代码不会真正跑到"**的场景，例如 `flash_attn` 仅在 import 阶段被引用，运行时由 NPU patch 接管。轻量级处理。
- 第 2 行（`replace_import`）：针对**"整个模块导出需要重定向"**的场景，例如把 `projects.mmdet3d_plugin.ops.deformable_aggregation` 的 `DeformableAggregationFunction` 替换为 NPU 实现。中粒度处理。
- 第 3 行（`inject_import`）：针对**"父模块导出缺失"**的场景，例如 `V1SparseDrive` 类定义在子模块但父模块未导出，导致 `from ... import` 失败。补丁级注入修复。

---

### 表 5：核心概念 AtomicPatch / Patch / Patcher

| 概念 | 说明 |
|------|------|
| **AtomicPatch** | 最小补丁单元，执行单个target → replacement替换 |
| **Patch** | 组合补丁，将多个相关的AtomicPatch组织在一起（如一个算子的forward + backward） |
| **Patcher** | 补丁管理器，收集、组织和应用所有补丁，并提供导入控制等辅助功能 |
| **default_patcher** | 预配置的Patcher实例，已包含常用预定义补丁，开箱即用 |

**逐行解读**：
- `AtomicPatch` 是最小粒度的"点替换"，target 是属性路径字符串，replacement 是新的可调用对象。
- `Patch` 把一对相关的原子操作打包（例如一个算子的 forward + backward、init + call），形成逻辑完整的适配单元。
- `Patcher` 是顶层容器，负责调度和提供导入控制、Profiling、Brake 等辅助能力。
- `default_patcher` 是 `Patcher` 的预配置实例，等价于"已注入所有 ✅ 默认补丁"的 Patcher。

---

### 表 6：预定义补丁列表（核心配置表）

| 模块 | 补丁名称 | 说明 | default_patcher |
|------|----------|------|:---------------:|
| **mmcv** | MultiScaleDeformableAttention | 多尺度可变形注意力 | ✅ |
|  | DeformConv | 可变形卷积 | ✅ |
|  | ModulatedDeformConv | 调制可变形卷积 | ✅ |
|  | SparseConv3D | 3D稀疏卷积 | ✅ |
|  | Stream | CUDA流管理 | ✅ |
|  | DDP | 分布式数据并行 | ✅ |
|  | Voxelization | 体素化 | ❌ |
|  | OptimizerHooks | 优化器钩子（mmcv 1.x） | ❌ |
| **mmengine** | OptimizerWrapper | 优化器包装器 | ❌ |
| **mmdet** | PseudoSampler | 伪采样器 | ❌ |
|  | ResNetAddRelu | ResNet加ReLU融合 | ✅ |
|  | ResNetMaxPool | ResNet最大池化 | ✅ |
|  | ResNetFP16 | ResNet FP16支持 | ❌ |
| **mmdet3d** | NuScenesDataset | NuScenes数据集 | ✅ |
|  | NuScenesMetric | NuScenes评估指标 | ✅ |
| **numpy** | NumpyCompat | NumPy兼容性修复 | ✅ |
| **torch** | TensorIndex | 张量索引优化 | ✅ |
|  | BatchMatmul | 批量矩阵乘法 | ✅ |
| **torch_scatter** | TorchScatter | scatter操作NPU实现 | ❌ |
| **transformers** | TransformersNPU | transformers NPU组合补丁（>=4.51.0） | ❌ |
| **diffusers** | DiffusersNPU | diffusers NPU组合补丁（==0.35.1） | ❌ |

**逐行解读**：
- mmcv 模块是补丁最密集的部分（共 8 个），覆盖注意力、可变形卷积、稀疏卷积、流管理、分布式，体素化（Voxelization）和 OptimizerHooks 因场景特异性需手动添加。
- mmengine 仅 1 个补丁（OptimizerWrapper），需手动添加。
- mmdet 中基础 Backbone 优化（AddRelu、MaxPool）默认启用；FP16 和 PseudoSampler 需按需手动添加。
- mmdet3d 的 NuScenes 数据集与评估指标默认启用，对自动驾驶场景做了内置适配。
- numpy 的 `NumpyCompat` 是早期兼容性补丁，恢复 `np.bool` / `np.float` / `np.int` 等已移除别名，避免第三方库 import 时崩溃。
- torch 层的 TensorIndex 和 BatchMatmul 属于基础算子优化，默认启用。
- `TorchScatter`、`TransformersNPU`（版本约束 `>=4.51.0`）、`DiffusersNPU`（版本约束 `==0.35.1`）均需手动 `patcher.add()`。

---

## 【公式解读】

**原文无公式**。

（文档中的 `compute_gaussian_weights` 示例仅含普通 Python 算术表达式，不构成数学公式；执行语义 "target → replacement" 也以表格/代码形式呈现，未以公式表达。）

---

## 【关联】

本文档与以下内容存在引用/上下游关系：

- **[./patcher_features.md](./patcher_features.md)**（功能详解）：本文档在多处声明"完整参数与实现原理参见功能详解"，是本文档的**深度参考文档**。具体子章节链接：
  - `./patcher_features.md#补丁机制`：解释 `precheck`、`runtime_check`、`with_imports`、`target_wrapper` 等进阶能力，以及为何 `apply()` 必须在 import 之前。
  - `./patcher_features.md#导入控制`：解释 `skip_import` / `replace_import` / `inject_import` 三个 API 的完整用法、行为说明与实现原理。
  - `./patcher_features.md#补丁单元`：解释 `AtomicPatch` / `Patch` 各参数的完整接口说明。
- **[../../../model_examples/DiffusionDrive/README.md](../../../model_examples/DiffusionDrive/README.md)**（DiffusionDrive 示例）：文档中给出的 `replace_import` 真实例子（`projects.mmdet3d_plugin.ops.deformable_aggregation` → `DeformableAggregationFunction`）和 `inject_import` 例子（`V1SparseDrive`、`V1SparseDriveHead`）均来自该模型，是 Patcher 三个导入控制 API 的典型使用案例。
- **[../../../model_examples/PanoOcc/README.md](../../../model_examples/PanoOcc/README.md)**（PanoOcc 示例）：作为 SDK 的模型示例之一，与 DiffusionDrive 并列展示 Patcher 的实际落地。

**文档定位关系**：本文档（快速上手）是 Patcher 特性的**入口层**，`patcher_features.md`（功能详解）是**机制层**，两个 `model_examples/.../README.md` 是**实践案例层**，三层形成"快速入门 → 原理深入 → 模型参考"的完整知识链路。

---

## 【使用方法】

### 最小接入（原文）

在 `train.py` 的**最顶部**（所有其他 import 之前）添加：

```python
from mx_driving.patcher import default_patcher
default_patcher.apply()

from tools.train import main
main()
```

### 常用功能速览（原文命令清单）

```python
from mx_driving.patcher import default_patcher, AtomicPatch

default_patcher.skip_import("<cuda_module>")                     # 跳过CUDA模块
default_patcher.replace_import("<old_module>", "<new_module>")   # 整模块替换
default_patcher.inject_import("<src>", "<name>", "<target>")     # 注入导入
default_patcher.add(AtomicPatch("<target>", replacement))        # 添加补丁
default_patcher.with_profiling("<output_dir>")                   # 性能采集
default_patcher.with_precision_debugger(dump_path="<dump_dir>")  # 精度采集
default_patcher.brake_at(<step>)                                 # 训练早停
default_patcher.allow_internal_format()                          # 允许NPU内部格式
default_patcher.apply()                                          # 应用所有
```

### 在 default_patcher 上扩展自定义补丁（原文）

```python
from mx_driving.patcher import default_patcher, Patch, AtomicPatch
from mx_driving.patcher.patch import with_imports

class MyCustomPatch(Patch):
    """自定义补丁描述"""

    @classmethod
    def patches(cls, options=None):
        return [
            AtomicPatch(
                "target_module.target_function",
                cls._replacement,
            ),
        ]

    @staticmethod
    @with_imports("module")  # 声明函数依赖的外部模块
    def _replacement(...):
        """替换函数实现"""
        ...

default_patcher.add(MyCustomPatch)
default_patcher.apply()
```

### 文件组织约定（原文）

推荐目录结构：

```
my_model/                          ← 源代码（不做任何修改）
├── configs/
├── projects/
├── tools/
│   ├── train.py
│   └── test.py

├── migrate_to_ascend/             ← 迁移代码（独立目录）
│   ├── patch.py                   # 补丁定义和patcher配置
│   ├── train.py                   # 昇腾训练入口（顶部加patcher代码）
│   ├── test.py                    # 昇腾测试入口
│   ├── train_8p.sh                # 8卡分布式训练脚本
│   └── requirements.txt
```

### 关键注意事项（原文）

- `Patch.name` 为可选项，未显式定义时默认使用类名。
- `disable()` 既支持字符串名，也支持直接传 `Patch` 类或补丁实例。
- 若需替换 `default_patcher` 中已启用的冲突补丁，推荐先 `disable()` 默认补丁，再 `add()` 新补丁。
- 进阶参数 `precheck`、`runtime_check`、`with_imports`、`target_wrapper` 的完整用法需参考 `./patcher_features.md#补丁机制`。
