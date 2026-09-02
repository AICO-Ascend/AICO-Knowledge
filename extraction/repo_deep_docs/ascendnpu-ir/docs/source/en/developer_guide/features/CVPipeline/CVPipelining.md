# Cube–Vector software pipelining

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/CVPipeline/CVPipelining.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/CVPipeline/CVPipelining.md

# 深度解读：Cube–Vector Software Pipelining（CV 流水线）

---

## 【定位】

这篇文档描述 HIVM 中的 **CV 流水线（CV-Pipelining）Pass** 所提供的能力：针对 Mix 类型算子内核中 Cube（矩阵乘）与 Vector（向量）指令交替且相互依赖的循环（如 FlashAttention），通过将两类指令拆分为独立 work item 并行执行，提升硬件利用率（ILP）与整体性能。

---

## 【技术要点】

1. **作用对象**：Mix 算子内核中 Cube 与 Vector 指令交叉依赖的 `scf.for` 循环（典型场景如 FlashAttention），核心目标是把串行的 Cube → Vector → Cube → Vector 链改写为多指令并行。
2. **核心算法六步**：
   1. 寻找合适的 `scf.for` 循环；
   2. 将 Cube 与 Vector 拆分为独立的 work item；
   3. 重新建立数据依赖关系；
   4. 对需要 multi-buffering 的 tensor 进行扩容（沿时间维扩展为多 buffer）；
   5. 对外层循环进行 unroll（按 `pipeline_depth` 展开）；
   6. 将每个 work item 放入各自独立的子循环中执行。
3. **多缓冲（Multi-Buffering）机制**：被拆分后的 Cube/Vector 结果通过 `tensor.insert_slice` 写入 `tensor<3x16x16xf32>`（原 `tensor<16x16xf32>`）形式的扩展 buffer，并在消费端用 `extract_slice` 取出，从而支持流水线并行访问而无读写冲突。
4. **循环步长变换**：原 `scf.for 0 to N step S` 改写后变为 `scf.for 0 to N step 3*S`，其中 3 对应一个完整 Cube→Vector→Cube（或 Vector→Cube→Vector）流水段的时间步数（即 pipeline 阶段数）。
5. **可配置参数**：`set-workspace-multibuffer`，默认值为 **2**，表示软件流水线阶段数与 multi-buffer 数量。
6. **重要副作用提示**：使用 multi-buffering 会**增加 UB（Unified Buffer）使用量**，需要根据具体 workload 调整流水线阶段数以平衡性能与内存占用。

---

## 【关键机制与数据】

### 工作原理

- **依赖识别与拆分**：Pass 扫描循环体内的指令，识别 Cube 与 Vector 的产生-消费关系。例如原文示例中 `Cube() → Vector → Cube → Vector` 的串行链，被拆成四个 work item：`{cube_loop}`、`{vector_loop}`、`{cube_loop}`、`{vector_loop}`。
- **数据流（Before → After）**：
  - **Before**：单层 `scf.for` 步长 `S`，所有指令在同一迭代内顺序执行。
  - **After**：外层循环步长变为 `3*S`，每个 work item 内部使用一个独立的 `scf.for 0 to 3` 子循环分别产出对应阶段的计算结果。
- **Buffer 扩展规则**（原文）："When no other Work Item needs the result, no buffer expansion needed"——当某个 work item 的结果不再被后续 work item 消费时，无需进行 buffer 扩容。例如示例中最后一个 `%v1` 的返回类型仍是 `tensor<16x16xf32>`，而非 `tensor<3x16x16xf32>`。
- **跨迭代依赖约束**（原文）：若 `v0` 与 `v1` 因中间存在 Cube 而无法归入同一 work item，且 `arg0` 在 `v1` 中定义却被 `v0` 使用，则**不会**应用 CV-Pipelining；反之，若 Cube 不使用 `v0`，则 `v0` 与 `v1` 可放入同一 work item，CV-Pipelining 生效。

### 性能数据

> 原文未提供具体性能数字（如加速比、吞吐提升等基准测试数据）。仅定性描述："improves hardware utilization (ILP) and performance"。

---

## 【表格解读】

| Option | Default Value | Description |
|------|--------|------|
| `set-workspace-multibuffer` | 2 | Number of software pipeline stages and multi-buffering count |

**逐行解读**：

- **`set-workspace-multibuffer`（选项名）**：控制 CV 流水线阶段数的编译选项，同时也是 multi-buffer 的份数。原文示例代码中外层循环步长扩展系数为 `3`，与默认 2 并不严格一致——文档示例展示的是概念性拆分示意，实际编译期会以该参数值决定 buffer 扩展维度与 unroll 因子。
- **Default Value = 2**：默认使用 2 级流水线 / 2 份 buffer。这是经验保守值，可在 UB 容量允许范围内调高以进一步提升 ILP，调低以节省 UB 占用。
- **Description**：明确该参数同时承担"流水线阶段数"与"multi-buffer 数量"两个语义，二者在该 Pass 中是统一控制量。

---

## 【公式解读】

> 原文无公式。文档仅以 MLIR 代码示例描述循环变换前后的 IR 结构，未给出任何数学表达式或伪代码公式。

---

## 【关联】

文档开头明确提示读者在阅读本文之前应先阅读 **[CV Optimization](../CV/CVOptimization.md)**，作为 CV 相关术语的前置知识。具体关联点如下：

- **上游/前置文档**：`../CV/CVOptimization.md` — 提供 CV 术语基础（如什么是 Mix kernel、Cube/Vector 指令分类等），是理解本文 CV 流水线优化对象的前提。
- **同类特性**：本文属于 HIVM 中面向 CV 类算子（Mix 算子）的编译优化 Pass，与文档标题点明的"CV software pipelining"作用域直接对应。
- **硬件载体**：Ascend Core 中的 Cube 单元与 Vector 单元是本文优化目标的物理载体，二者支持异步并行是 CV-Pipelining 得以生效的硬件前提。

---

## 【使用方法】

启用方式通过编译选项 `set-workspace-multibuffer` 控制：

- **选项**：`set-workspace-multibuffer`
- **默认值**：**2**
- **作用**：设置软件流水线阶段数与 multi-buffer 数量。
- **调优建议**（原文）："tune the number of pipeline stages for your workload"——由于多缓冲会增加 UB 占用，需要根据实际工作负载的内存预算调整该参数值，在 UB 容量与并行度之间取得平衡。

> 原文未涉及具体的命令行调用格式、CMake 选项声明方式或 API 调用代码示例，仅给出选项名称、默认值与语义描述。
