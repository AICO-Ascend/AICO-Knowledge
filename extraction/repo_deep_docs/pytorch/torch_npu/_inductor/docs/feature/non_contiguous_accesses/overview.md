# 离散访存特性介绍

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/non_contiguous_accesses/overview.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/non_contiguous_accesses/overview.md

# 离散访存特性 — 一体化深度解读

---

## 【定位】

这篇文档面向 PyTorch 昇腾适配插件（TorchNPU）的 Inductor 后端，**系统介绍了在推荐类大 Embedding 模型场景下的"离散访存（Non-contiguous / Indirect Memory Access）"特性**：梳理了哪些 PyTorch 算子属于离散访存算子、阐述其在 A2/A3 上只能 fallback 到 eager 而在 A5 上可通过 SIMT 加速的工作原理，并给出了 Inductor 在 A5 上控制该特性的两种运行模式（`simd_simt_mix` 与 `fallback`）。

---

## 【技术要点】

1. **离散访存算子的归类**：按"GM → UB 为离散"与"UB → GM 为离散"两类划分，前者包含 `aten.embedding`、`aten.index`、`aten.gather`、`aten.index_select`，后者包含 `aten.index_put`、`aten.scatter`。
2. **典型生成模式**：以 `aten.embedding` 为例，Inductor 先生成一次 load 把索引从 GM（`in_ptr0`）搬到 UB（`tmp0`），再用 `tmp0` 作为下标从 embedding 表（`in_ptr1`）中搬运长度为 `128` 的向量组成新的 UB tensor（`tmp1`），从而产生间接访存 IR。
3. **硬件能力差异**：原文明确"由于 A2/A3 上仅支持 SIMD 访存，对于离散访存场景仅能通过标量搬运，因此上述的离散访存算子将会 fallback 到 eager 模式运行"；而 A5 加入了 SIMT 访存能力，能够加速间接访存的搬运。
4. **触发条件**：若 Inductor 中生成了间接访存 IR，则 Inductor 把该 Kernel 标记为"需要使用间接访存相关算子"，并由环境变量切换不同 Codegen / Autotune 行为。
5. **`simd_simt_mix` 模式下的三种底层方案**：SIMT 方案（整 kernel 用 SIMT）、SIMT 模板方案（间接访存 load/store 走 CCE 模板算子经 SIMT 实现、其余代码走 SIMD）、SIMD 甜点方案（整 kernel 走 SIMD，离散访存部分在 ta 层做 SIMD 优化，并通过 Inductor Autotune 自动选最优）。
6. **`fallback` 模式**：关闭离散访存，离散访存类算子整体 fallback 处理（不进入 Inductor 融合）。

---

## 【关键机制与数据】

**工作原理（原文："由于A2/A3上仅支持simd访存，对于离散访存场景仅能通过标量搬运，因此上述的离散访存算子将会fallback到eager模式运行。而在A5硬件中加入了simt访存能力，对于间接访存的场景使用simt能够加速离散数据的搬运，本特性将会支持上述的离散访存算子在A5硬件上的inductor融合。"）**

- 数据流：GM（`in_ptr0` 索引表）→ UB（`tmp0`）用作行号 → GM（`in_ptr1` embedding 表，按 `128 × tmp0` 跨度取一行）→ UB（`tmp1`）。
- 关键常数 `128`（原文）：在示例代码中表示每行向量的长度（即 `x1 + 128*tmp0` 中的步长）。
- `Y0BLOCK_SUB` 取值假设（原文）：注释中"假设Y0BLOCK_SUB为4"。
- 模式选择（原文："对于间接访存相关的算子，由于存在多种不同的Codegen以及Autotune逻辑，使用环境变量进行控制"）：通过环境变量在 `simd_simt_mix` 与 `fallback` 之间切换；`simd_simt_mix` 内部还会通过 Inductor Autotune 进行自动选优。

> 原文未给出具体 ms / speedup 等性能数字，亦未给出具体的"行/列数 × Embedding 规模"等量化数据；性能数据**原文未涉及**。

---

## 【表格解读】

**原文表格 1 — 离散访存算子分类：**

| 算子类别 | pytorch算子 |
| --- | --- |
| load类(GM到UB为离散访存) | aten.embedding、aten.index、aten.gather、aten.index_select |
| store类(UB到GM为离散访存) | aten.index_put、aten.scatter |

逐行解读：

1. **load 类（GM → UB 方向为离散访存）**：当数据从全局内存（GM）读入统一缓冲区（UB）时，由于访问的地址不是连续的整段偏移，因此属于离散访存。原文列出 4 个典型 PyTorch 算子，其中 `aten.embedding` 是推荐模型 lookup 的代表，`aten.index`、`aten.gather`、`aten.index_select` 都是沿某个维度按索引取元素/切片的算子。
2. **store 类（UB → GM 方向为离散访存）**：当 Inductor 融合后需要把局部写回到 GM 时，若目标地址不连续，则构成离散存储。原文列出 `aten.index_put`、`aten.scatter` 两个算子；这两类在 Autotune 时也享受 SIMD 甜点方案在 ta 层的优化。

---

## 【公式解读】

原文以近似 Triton 的伪代码展示了间接访存的生成模式，逐字保留并附符号含义：

```python
y0 = tl.arange(0, Y0BLOCK_SUB)        # y0 为连续访存，假设 Y0BLOCK_SUB 为 4
# in_ptr0 = [1, 0, 4, 5]
tmp0 = tl.load(in_ptr0 + (y0), y0_mask, other=0.0)
# tmp0 = [1, 0, 8, 10]                （原文给出的实例值）
# in_ptr1 = [[row0], [row1], ..., [row10]]
tmp1 = tl.load(in_ptr1 + (x1 + 128*tmp0), y0_mask & x1_mask)
# tmp1 = [[row1], [row0], [row8], [row10]]
# tmp1 即为间接访存
```

符号逐项说明（以原文出现的符号为准）：

| 符号 | 含义 | 作用 |
| --- | --- | --- |
| `Y0BLOCK_SUB` | y 维块大小 | 原文注释"假设为 4"，决定 `tl.arange` 生成的连续下标个数 |
| `y0` | `tl.arange(0, Y0BLOCK_SUB)` 产生的连续整数序列 | 表示本次 kernel 在 y 维上的连续访问下标，本身是连续访存 |
| `in_ptr0` | GM 上的索引张量（例如 `[1, 0, 4, 5]`） | 存储要 lookup 的行号 |
| `tmp0` | 第一次 `tl.load` 从 `in_ptr0` 读出的索引 UB tensor（实例值 `[1, 0, 8, 10]`） | 作为"行号"参与下一阶段间接访存 |
| `y0_mask` | y 维边界 mask | 过滤越界访问 |
| `other=0.0` | mask 失效位的填充值 | Triton load 接口的兜底参数 |
| `in_ptr1` | GM 上的大 Embedding 表，按 128 个元素组成一行（`[row0]…[row10]`） | 待离散访问的目标张量 |
| `128` | 一行的元素个数（原文步长常量） | 与 `tmp0` 相乘得到行内起始偏移 |
| `x1` | x 维偏移（在 `128` 个元素内的位置） | 与 `128*tmp0` 合成最终地址 |
| `tmp1` | 第二次 `tl.load` 从 `in_ptr1` 中按"行号 = `tmp0`"取出的向量（实例值 `[[row1],[row0],[row8],[row10]]`） | 即所谓"间接访存"的结果，写在 UB 上 |
| `y0_mask & x1_mask` | y 与 x 两个维度的有效位按位与 | 同时屏蔽两个维度的越界 |

原文的核心机制可概括为：**第一阶段把"行号"从 GM 搬到 UB，第二阶段用 UB 上的行号去 GM 中"指哪儿打哪儿"地取整行向量**；由于第二阶段的地址由运行时数据 `tmp0` 决定，无法静态化为连续偏移，因此属于间接访存。

---

## 【关联】

- 上游背景：文档将本特性的必要性挂接到"**推荐模型的 Embedding 参数规模极其庞大**"上，强调其与 `aten.embedding`、`aten.gather` 这类 lookup 算子在推理与训练中的频繁调用绑定。
- 硬件分层：明文将 A2/A3（A 系列 SIMD-only）与 A5（新增 SIMT）划分到两条不同的代码路径：A2/A3 → eager fallback；A5 → Inductor 融合 + SIMT。
- 编译器协同：在 `simd_simt_mix` 模式下涉及到底层编译器的 3 种 Codegen（SIMT、SIMT 模板、SIMD 甜点）以及 **Inductor Autotune** 的自动选择机制，由"环境变量"在模式间切换。
- 图形资产：原文末引用了一张架构图（`./arch.drawio.svg`），用于直观展示 SIMT / SIMT 模板 / SIMD 甜点 / fallback 之间的关系，但文本中未展开。
- **内部链接：原文无内部链接（文末链接列表为"无"）**；唯一外部资源是同目录下的 `arch.drawio.svg`。

---

## 【使用方法】

- **模式开关**（原文："使用环境变量进行控制"）：通过环境变量在以下两种模式间切换
  - `simd_simt_mix` 模式：在该模式内，底层编译器层面存在 3 种方案（SIMT 整 kernel / SIMT 模板混合 / SIMD 甜点 + Autotune），由 Inductor Autotune 在编译期自动选择单测性能最优的算子作为整网运行算子。
  - `fallback` 模式：关闭离散访存，离散访存类的算子直接 fallback 处理（不进入 Inductor 融合）。
- **触发条件**：当 Inductor 生成的 IR 中含有间接访存表达式时，Inductor 会自动把对应 Kernel 标记为"使用间接访存相关算子"，随后按当前环境变量进入对应路径。

> 原文未给出具体的环境变量名（如 `TORCHINDUCTOR_*` 之类的字面量）、也未给出 `cmake` / CLI 启动命令，故具体变量名及命令**原文未涉及**，需要在仓库源码或环境变量注释中另行查阅。
