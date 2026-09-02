# INDUCTOR_INDIRECT_MEMORY_MODE

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/non_contiguous_accesses/INDUCTOR_INDIRECT_MEMORY_MODE.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/non_contiguous_accesses/INDUCTOR_INDIRECT_MEMORY_MODE.md

# INDUCTOR_INDIRECT_MEMORY_MODE 文档深度解读

## 【定位】

这篇文档描述了 TorchNPU（昇腾 PyTorch 适配插件）中 **Inductor 对离散访存（non-contiguous access）类算子进行融合的能力开关与融合方式选择**的配置项，主要面向 Atlas A5 训练系列产品。

---

## 【技术要点】

1. **环境变量控制开关**：通过 `INDUCTOR_INDIRECT_MEMORY_MODE` 环境变量控制是否开启离散访存的 Inductor 融合以及选择何种融合方式，默认值为 `"simd_simt_mix"`。
2. **三选一融合模式**：`mode` 可选值为两种 —— `fallback`（不进行 Inductor 融合）或 `simd_simt_mix`（使用 load/store DSL 进行 Inductor 融合），**官方推荐 `simd_simt_mix`**。
3. **三种子 Kernel 类型**：`simd_simt_mix` 模式下生成的 kernel 内部支持 simd 模板方案、纯 simt 方案、simd+simt 模板三种不同类型算子，并由 Autotune 自动选择调优出最优 tiling。
4. **元数据标识机制**：在 `simd_simt_mix` 模式下生成的 triton 算子，会在 `inductor_meta` 中通过字段 `{'npu_kernel_type': 'simd_simt_mix'}` 标识其为模板方案 simt 算子。
5. **硬件平台约束**：A2、A3 系列**不支持**离散访存类算子的 Inductor 融合，**仅在 A5 上支持**该特性。
6. **DSL 兼容性**：`simd_simt_mix` 模式使用的 load/store DSL 与 PyTorch 社区保持一致。

---

## 【关键机制与数据】

### 工作原理

- **fallback 模式**：对离散访存类算子**不进行** Inductor 融合，算子按常规路径执行（原文："对于离散访存类的算子不进行Inductor融合"）。
- **simd_simt_mix 模式（默认 & 推荐）**：
  1. 针对离散访存类算子采用与社区一致的 **load、store DSL** 描述；
  2. 单个融合 kernel 同时承载三类实现 —— **simd 模板方案、纯 simt 方案、simd+simt 模板**；
  3. **Autotune** 在运行期根据硬件/输入特征选择其中最优 tiling；
  4. 生成的 Triton 算子在 `inductor_meta` 中写入 `npu_kernel_type: simd_simt_mix` 字段，用于后续阶段识别其为模板方案 simt 算子。

> **原文**：未提供具体的性能数据、benchmark 数字或量化指标；本文档仅描述能力开关与机制，不含性能数值。

---

## 【表格解读】

**原文无表格**

---

## 【公式解读】

**原文无公式**

---

## 【关联】

本文档作为离散访存 Inductor 融合特性的配置文档，与以下机制/模块存在上下游关系（基于原文信息推断）：

- **Inductor 编译栈**：本特性是 Inductor 后端针对离散访存算子的融合增强，依赖 `inductor_meta` 字典传递算子类型标识（`npu_kernel_type` 字段），供 Inductor 编译流水线的下游阶段识别。
- **Triton 算子生成层**：融合产物为 Triton 算子，因此与 TorchNPU 的 Triton 算子生成/调度流程直接耦合。
- **Autotune 调优子系统**：`simd_simt_mix` 模式下三种 tiling 方案的优选由 Autotune 完成，依赖平台侧的 Autotune 能力。
- **硬件平台矩阵**：A2、A3（不支持）与 A5（支持）形成对照，表明该特性与昇腾具体 IP 架构强绑定。
- **社区一致性**：load/store DSL "与社区一致"，说明本特性在 DSL 层面对齐上游 PyTorch Inductor，便于生态兼容。

> 注：本文档**未提供内部链接**，上述关联基于文档自身内容及上下文特征推断。

---

## 【使用方法】

**启用方式**（原文有明确命令）：

```bash
# 推荐用法：开启 simd_simt_mix 模式（同时也是默认值）
export INDUCTOR_INDIRECT_MEMORY_MODE=simd_simt_mix

# 关闭 Inductor 融合（回退路径）
export INDUCTOR_INDIRECT_MEMORY_MODE=fallback
```

**关键配置项**：

| 配置项 | 可选值 | 默认值 | 推荐值 | 适用型号 |
|---|---|---|---|---|
| `INDUCTOR_INDIRECT_MEMORY_MODE` | `fallback` / `simd_simt_mix` | `simd_simt_mix` | `simd_simt_mix` | 仅 Atlas A5 训练系列产品 |

**使用约束**（原文）：
- 仅 A5 支持离散访存类算子的 Inductor 融合；
- A2、A3 上即使设置该环境变量也不会触发离散访存融合（仅相当于 `fallback` 行为）。
