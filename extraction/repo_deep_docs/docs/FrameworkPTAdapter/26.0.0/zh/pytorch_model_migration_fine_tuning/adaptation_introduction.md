# 适配简介

> 仓 `docs` · 路径 `FrameworkPTAdapter/26.0.0/zh/pytorch_model_migration_fine_tuning/adaptation_introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/docs/FrameworkPTAdapter/26.0.0/zh/pytorch_model_migration_fine_tuning/adaptation_introduction.md

# 适配简介 — 一体化深度解读

## 【定位】

这篇文档定位为 **昇腾 NPU 上 PyTorch 混合精度（Mixed Precision）训练适配的入门总览**，解决"用户将 PyTorch 训练脚本迁移到 NPU 后，如何正确启用并配置 AMP（自动混合精度）以匹配 float32 训练精度"的问题，明确推荐使用 PyTorch 原生 AMP 模块而非第三方 APEX，并交代约束、接口与四种典型场景的接入方法。

---

## 【技术要点】

1. **混合精度定义**：训练时同时使用 **float32（单精度）** 与 **float16（半精度）** 两种数据类型，使用相同超参数即可达到与纯 float32 训练"几乎相同的精度"。
2. **两种实现路径**：① PyTorch 框架内置 **AMP** 功能模块；② 第三方 **APEX** 混合精度模块。官方推荐路径为前者。
3. **硬件约束差异**：
   - **Atlas 训练系列产品**：迁移完成后、训练开始前**必须**开启混合精度（架构特性要求）。
   - **Atlas A2 / Atlas A3 训练系列产品**：可自行选择是否开启。
4. **接口核心**：AMP 适配围绕两个接口 —— `amp.autocast()` 与 `amp.GradScaler()`，前者负责前向计算精度切换，后者负责损失缩放。
5. **NPU 支持的 4 种 AMP 场景**：典型场景、梯度累加场景、多模型/多损失/多优化器场景、DDP 单 NPU 单进程场景。
6. **NPU 增强参数**：原生 `amp.GradScaler` 默认采用动态 Loss Scale；NPU 上额外新增 `dynamic` 参数，`dynamic=False` 时支持**静态 Loss Scale**，并可通过 `init_scale` 设置取值（示例 `init_scale = 2.**10`）。

---

## 【关键机制与数据】

- **工作机制（原文）**：混合精度训练通过在同一训练过程中混合 float32 与 float16 数据类型，使用相同超参数，达到与 float32 几乎相同的精度。
- **接口分工（原文）**：混合精度 AMP 适配主要包括 `amp.autocast()`（自动精度转换）与 `amp.GradScaler()`（损失缩放）两个接口。
- **Loss Scale 策略（原文）**：原生 PyTorch 默认使用**动态 Loss Scale**，Loss Scale 取值会根据训练情况动态调整；NPU 上适配的 `amp.GradScaler` 增加了 `dynamic` 参数，`dynamic=False` 时使用**固定值 Loss Scale**，并由 `init_scale` 参数设定取值。
- **性能声明（原文）**：混合精度开启**可能**提升性能，但不针对所有模型生效；若性能未提升需进一步性能调优修改。
- **精度风险（原文）**：开启混合精度后，由于数值表示范围与最小间隔发生变化，可能导致极少部分网络出现精度掉点甚至无法收敛，可参考 `mixed_prec_debug.md` 解决。
- **顺序约束（原文）**：混合精度适配操作应在**脚本迁移完成后、训练开始之前**进行。
- **示例数值（原文）**：`init_scale = 2.**10`，即固定 Loss Scale 初始系数取值为 2 的 10 次方 = 1024。

---

## 【表格解读】

**表 1 参数说明**（原文逐字还原）：

| 参数名称 | 参数说明 | 参数取值 |
|---|---|---|
| `dynamic` | AMP 是否使用动态 Loss Scale。 | True（默认）：使用动态 Loss Scale。<br>False：使用静态 Loss Scale。 |
| `init_scale` | 在使用静态 Loss Scale 时的初始 scale 系数。 | 仅在 `dynamic=False` 时可用，用户根据实际情况设置。 |

**逐行解读**：
- **`dynamic` 行**：该参数控制 Loss Scale 是否随训练动态调整。默认 `True`，即沿用 PyTorch 原生行为，按训练情况动态调整 Loss Scale 取值；设为 `False` 后切换为静态 Loss Scale 模式，需要配合 `init_scale` 给出固定系数。
- **`init_scale` 行**：仅在 `dynamic=False`（静态 Loss Scale 模式）下生效，由用户根据网络梯度幅值实际情况自行设置；典型示例取 `2.**10`（即 1024），用于在静态模式下补偿 float16 梯度下溢问题。

---

## 【公式解读】

原文无公式。文档中出现的仅为一段 Python 代码示例（非数学公式）：

```python
scaler = amp.GradScaler(init_scale = 2.**10, dynamic = False)
```

该代码表示以 **静态 Loss Scale = 2¹⁰ = 1024** 初始化 NPU 适配版本的 `amp.GradScaler` 对象，等价于在 NPU 上关闭动态 Loss Scale 调整、固定使用 1024 作为缩放系数。

---

## 【关联】

依据文末内部链接信息，本文档与同仓库内以下文档构成上下游/并列关系：

- **[mixed_prec_intro.md — 混合精度原理与计算过程介绍](mixed_prec_intro.md)**：本文档是"适配简介"（How），该链接指向"原理与计算过程"（Why/How it works）。读者按本文完成接口适配后，可跳转阅读其底层机制。
- **[mixed_prec_debug.md — 混合精度问题调测](mixed_prec_debug.md)**：本文"使用约束"中明确指出，开启混合精度后可能出现精度掉点甚至无法收敛，并直接给出该链接作为解决方案入口，属"问题排查"下游文档。

此外，本文对外引用了 PyTorch 官方文档（`amp.autocast` / `amp.GradScaler` / 4 种典型场景），以及第三方 [Ascend/apex](https://gitcode.com/Ascend/apex) 仓库作为非推荐路径备选。

---

## 【使用方法】

**启用方式**（原文）：

1. 在脚本迁移完成、训练开始**之前**，按需启用混合精度适配。
2. **硬件判定**：
   - Atlas 训练系列产品：**必须**开启混合精度。
   - Atlas A2 / Atlas A3 训练系列产品：可选开启。
3. **首选 PyTorch 原生 AMP 模块**（`amp.autocast` + `amp.GradScaler`），按官方四种场景（典型 / 梯度累加 / 多模型损失优化器 / DDP 单 NPU 单进程）接入。
4. **若使用静态 Loss Scale**，按如下命令配置（原文示例，逐字保留）：

   ```python
   scaler = amp.GradScaler(init_scale = 2.**10, dynamic = False)
   ```

   - `dynamic=False`：关闭动态 Loss Scale，启用静态模式。
   - `init_scale=2.**10`：设置静态 Loss Scale 系数为 1024，用户可按实际情况调整。
5. **若性能未提升**：需进一步做性能调优修改（原文未给出具体命令）。
6. **若出现精度掉点/不收敛**：参考 [`mixed_prec_debug.md`](mixed_prec_debug.md) 进行调测。
7. **若选用第三方 APEX 模块**：参考外部仓库 [Ascend/apex](https://gitcode.com/Ascend/apex)（非推荐路径）。
