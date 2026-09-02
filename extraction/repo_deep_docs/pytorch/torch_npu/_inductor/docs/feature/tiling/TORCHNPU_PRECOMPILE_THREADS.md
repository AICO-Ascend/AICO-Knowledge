# TORCHNPU_PRECOMPILE_THREADS

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/tiling/TORCHNPU_PRECOMPILE_THREADS.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/tiling/TORCHNPU_PRECOMPILE_THREADS.md

# TORCHNPU_PRECOMPILE_THREADS 文档深度解读

## 【定位】

这篇文档描述了 TorchNPU（昇腾 PyTorch 适配插件）中预编译（precompile）阶段的多线程并发控制能力——通过环境变量 `TORCHNPU_PRECOMPILE_THREADS` 控制并行编译线程数，从而影响模型编译阶段的吞吐与资源占用。

---

## 【技术要点】

1. **功能本质**：控制预编译阶段使用的并发编译线程数量，是面向 NPU 编译流水线的并行度旋钮。
2. **默认值机制**：默认线程数取 `max_precompiled_thread_num = os.cpu_count() // 2`，即宿主机 CPU 逻辑核数的一半。
3. **并发触发条件**：当设置值 **大于 1** 时启用并发编译（"大于1时，使用并发编译"）；等于 1 或更小时则退化为串行编译行为。
4. **配置方式**：通过 Linux shell 环境变量注入，例如 `export TORCHNPU_PRECOMPILE_THREADS=32`。
5. **使用约束**：原文标注 "无"，即未声明任何额外约束（如最小/最大值上限、与其他变量互斥关系等）。
6. **支持硬件范围**：Atlas A2、A3、A5 系列产品。

---

## 【关键机制与数据】

- **工作原理**：在模型首次进入 NPU 编译流程时，预编译阶段会依据 `TORCHNPU_PRECOMPILE_THREADS` 派生出多个工作线程并行执行编译子任务，目标是缩短首次编译延迟（warm-up cost）。
- **默认取值逻辑**：`os.cpu_count()` 反映宿主机可用 CPU 逻辑核数；`// 2`（整除 2）作为保守折中，避免编译线程与推理/数据预处理线程抢占 CPU 资源。
- **示例数据**（原文）：`TORCHNPU_PRECOMPILE_THREADS=32`，用于在多核服务器上将编译并行度显式拉到 32。
- **并发与串行的切换阈值**：以 "1" 作为分水岭，大于 1 即进入并发路径。

> 注：原文未给出任何性能基准数据（如加速比、显存占用等），仅描述机制本身。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无数学公式**。

不过原文出现一段类代码的赋值表达式：

```text
max_precompiled_thread_num = os.cpu_count() // 2
```

**符号含义**：

| 符号 | 含义 | 作用 |
|---|---|---|
| `max_precompiled_thread_num` | 默认预编译线程数（上界默认值） | 决定未设置环境变量时的并行度 |
| `os.cpu_count()` | Python 标准库函数，返回宿主机 CPU 逻辑核数 | 反映可用并发硬件规模 |
| `// 2` | Python 整除运算符 | 取核数的一半作为保守默认值，平衡编译速度与 CPU 资源占用 |

---

## 【关联】

**原文无内部链接**。

从文档上下文（路径 `torch_npu/_inductor/docs/feature/tiling/`）可推断该特性属于 Inductor 编译子模块下的 tiling 相关特性族，但**原文未给出与其他特性的交叉引用**。

---

## 【使用方法】

**启用方式（原文给出）：**

```shell
export TORCHNPU_PRECOMPILE_THREADS=32
```

将变量值替换为期望的线程数后，TorchNPU 的预编译阶段将按此并发度执行。

**注意事项（原文给出）：**
- 使用约束：无额外约束，原文未声明取值范围、与其他编译变量的互斥关系或推荐上限；
- 适用型号：Atlas A2 / A3 / A5 系列产品。
