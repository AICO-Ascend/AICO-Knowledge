# TORCHINDUCTOR_COMPILE_THREADS(同社区)

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/tiling/TORCHINDUCTOR_COMPILE_THREADS.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/tiling/TORCHINDUCTOR_COMPILE_THREADS.md

# `TORCHINDUCTOR_COMPILE_THREADS` 一体化深度解读

---

## 【定位】

本文档描述 TorchNPU（昇腾 PyTorch 适配插件）中 **Inductor 并发编译进程数**的环境变量配置项 `TORCHINDUCTOR_COMPILE_THREADS`，明确其默认值、行为条件及所支持的昇腾硬件型号，解决"如何在 NPU 后端控制 TorchInductor 并行编译粒度"的问题。

---

## 【技术要点】

1. **核心作用**：控制 TorchInductor **并发编译 kernel 的进程数量**（原文："并发编译的进程数量"）。
2. **默认值**：`32`（原文："默认值为32"），与 PyTorch **社区逻辑保持一致**（原文："与社区逻辑保持一致"）。
3. **触发多进程的阈值条件**：当该值 **大于 1** 时启用 **多进程编译**；等于或小于 1 时退化为单进程路径（原文："大于1时，使用多进程编译"）。
4. **配置方式**：通过 shell 环境变量设置（原文示例：`export TORCHINDUCTOR_COMPILE_THREADS=32`）。
5. **使用约束**：原文明确标注"无"，即**无使用约束**。
6. **支持型号**：覆盖昇腾三档主力产品线——Atlas A2 系列、Atlas A3 系列、Atlas A5 系列。

---

## 【关键机制与数据】

**工作原理**（原文信息整理）：

- 该变量属于 TorchInductor 的**编译期并行度参数**，影响的是"编译阶段"的进程并发度，而非算子执行阶段的线程数。
- 当 `TORCHINDUCTOR_COMPILE_THREADS > 1` 时，Inductor 调度多个子进程并行完成 kernel 编译（codegen → 编译后端），其目的为**降低首次编译 latency**。
- 该机制在 TorchNPU 中**与社区默认行为对齐**（默认 `32`），即 NPU 后端没有自定义改写这一默认值，保持与 upstream PyTorch Inductor 一致。

**原文数据点**：

- 默认进程数：`32`（原文："默认值为32"）。
- 多进程触发条件：`> 1`（原文："大于1时，使用多进程编译"）。

> 注：原文未提供性能对比数据、编译耗时加速比、内存占用等具体指标，故此处不臆造。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

1. **与 PyTorch 上游社区的关联**：文档标题明确标注"**(同社区)**"，说明该参数在 TorchNPU 中的语义、默认值与上游 PyTorch Inductor **完全对齐**，未做昇腾侧定制化改写，属于"沿用社区约定"的兼容性配置。
2. **所属模块层级**：路径 `torch_npu/_inductor/docs/feature/tiling/` 表明：
   - 归属于 **`torch_npu._inductor`** 子包，即 TorchNPU 对 Inductor 后端的适配层；
   - 处于 **`docs/feature/tiling/`** 文档目录下，与 tiling（分块）相关特性文档并列，但本参数本身控制的是**编译并行度**而非分块策略。
3. **与编译流程的上下游关系**：
   - **上游**：Inductor 的 FX graph 捕获与 lowering；
   - **本参数作用点**：Inductor codegen 后调用 **编译后端**（如 Triton/AscendC 编译器）进行 kernel 编译的**并行调度环节**；
   - **下游**：生成的 kernel 二进制被缓存并交付运行时执行。
4. **支持硬件关联**：所列 **Atlas A2 / A3 / A5 系列产品**均为昇腾训练+推理一体的高性能 NPU SoC，覆盖当前昇腾主力硬件代际，说明该参数在三档产品上的 Inductor 编译路径均已开启。
5. **内部链接**：原文文末提供的内部链接信息为 **"(无)"**，即本文档未主动链接到仓内其他特性文档；与 tiling 目录下其他文档仅存在目录级别的并列关系。

---

## 【使用方法】

**启用方式**（原文示例，逐字保留）：

```shell
export TORCHINDUCTOR_COMPILE_THREADS=32
```

**配置说明**：

- 通过 `export` 设置为所需正整数即可生效（设置后启动的 Python 进程继承该环境变量）。
- 取值含义：
  - `> 1`：启用多进程编译；
  - `= 1`：退化为单进程编译路径；
  - 默认值：`32`（不设置时即取此值）。
- **使用约束**：原文标注"无"。
- **生效硬件**：Atlas A2 / A3 / A5 系列产品（原文列表）。

> 原文未涉及代码层 API 调用方式、Python `os.environ` 设置示例、动态调整接口等内容，此处不补充。
