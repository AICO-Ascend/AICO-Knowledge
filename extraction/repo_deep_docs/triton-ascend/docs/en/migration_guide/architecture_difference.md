# Development Differences Between Ascend and GPUs

> 仓 `triton-ascend` · 路径 `docs/en/migration_guide/architecture_difference.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-ascend/docs/en/migration_guide/architecture_difference.md

# 深度解读：Development Differences Between Ascend and GPUs

## 【定位】

本文档系统阐述在 Triton 编程框架下，从 GPU 迁移到 Ascend NPU 进行算子开发时必须理解的三类核心架构差异——**多核并行策略、单核数据传输策略（含 tiling）、Ascend NPU IR 编译优化**——并以 GELU 算子为贯穿示例，展示从标准 Torch 写法到带 tiling 的高性能 Triton 写法的演进路径，目标读者是从 GPU 上 Triton 开发迁移到 Ascend 平台的开发者。

---

## 【技术要点】

1. **多核并行本质差异**：GPU 的 grid 是"逻辑任务维度"（解耦于物理核），Ascend 的 grid 是"物理核组映射"（绑定 AI Core 拓扑）。GPU 没有 grid 维度的硬限制；Ascend 要求 `grid size ≤ AI Core 总数`，二维布局需与拓扑匹配。

2. **核数硬上限 ≤ 65,535**：Ascend 上 Triton 的 launch 网格第一维 `ncore`（核数）当前版本必须 ≤ 65,535；示例 `triton_gelu[n, 1, 1](...)` 的第一个参数即使用核数。

3. **执行模型差异**：GPU 一个 grid thread 对应一次 kernel 执行；Ascend 每个物理核只执行一个 block，但可对该 block 进行**重复调度**（vector 核与 cube 核属于多物理核，核数随硬件代际变化）。

4. **三级 Tiling 参数体系**：跨核 tiling 用 `ncore`，核间 tiling 用 `xblock`（block 大小），核内细粒度 tiling 用 `xblock_sub`；通过对三级粒度的组合适配 on-chip memory。

5. **On-chip memory 上限 192 KB**：Atlas 800T/I A2 每个计算周期的数据量不得超过 192 KB，否则会引发 memory overflow——这是 tiling 设计的硬约束。

6. **Ascend IR 编译选项**：`multibuffer`（默认 true，启用并行流水数据传输）、`unit_flag`、`limit_auto_multi_buffer_only_for_local_buffer`、`limit_auto_multi_buffer_of_local_buffer`、`set_workspace_multibuffer`、`enable_hivm_auto_cv_balance`，均为 autotune 阶段通过 `triton.Config` 字典传入。

---

## 【关键机制与数据】

**工作原理——Ascend 路径下的"调度—Tiling—编译"三级优化链：**

1. **多核调度层**：开发者通过 launch 网格的 `ncore` 参数显式指定参与运算的物理核数，框架把这 `ncore` 个 grid 直接绑定到对应 AI Core；不同于 GPU 通过 `program_id` 解码到线程，Ascend 的 `tl.program_id(0)` 直接对应物理核号——`xoffset = tl.program_id(0) * XBLOCK` 这一行即是"用核号 × 块大小"计算该核负责的数据起点。

2. **数据 Tiling 层**：跨核维度用 `ncore × XBLOCK` 切分总数据；到单核内再以 `XBLOCK_SUB` 为步长循环 `range(0, XBLOCK, XBLOCK_SUB)` 完成细粒度切片——mask `xmask = x_index < xnumel` 保证越界安全。示例参数 `ncore=32, xblock=32768, xblock_sub=8192`，可读出"32 个核 × 32 K 元素/核 = 1 M 元素总量，每核再分 4 轮 8 K 子块处理"。

3. **On-chip memory 守护**：`tl.load` 将子块从 global memory 装载到 on-chip memory 缓存（在 Atlas 800T/I A2 上总额 192 KB），`tl.store` 回写——`xblock_sub` 大小实际上限受制于 192 KB，因此 8 K 元素 × 单元素字节数需 ≤ 192 KB。

4. **IR 编译优化层**：当 tiling 选定后，`multibuffer=True` 等选项通过 `triton.Config` 注入，告诉编译器把数据传输组织成并行流水（pipeline），从而隐藏访存延迟。

**性能/约束数据（原文摘录）：**
- 原文章节"Full Utilization of Cores"明确：「the number of cores in the current version must be less than or equal to 65,535」。
- 原文：「Atlas 800T/I A2 has an on-chip memory capacity of 192 KB」。
- 原文示例：`ncore = 32; xblock = 32768; xblock_sub = 8192`。

---

## 【表格解读】

### 表 1：Core comparison（GPU vs Ascend，多核并行本质对比）

| Dimension | GPU (NVIDIA) | Ascend |
|---|---|---|
| Essence of grids | Logical task dimension (decoupled from physical cores) | Physical core group mapping (bound to the AI core topology) |
| Limit on the number of cores/dimensions | No hard limit on the grid dimensions/sizes | Grid size ≤ Total number of AI cores; topology matching required by 2D |

**逐行解读：**

- **第一行（Essence of grids）**：点出两种架构的"网格观"差异——GPU 把 grid 当作纯逻辑任务容器，与 SM/CUDA core 物理排布无对应关系，由硬件调度器决定哪个 block 落到哪个 SM；Ascend 则直接把 grid 的某个维度映射到一个具体的 AI Core 拓扑位置（如 2D 拓扑的行/列），开发者写 `tl.program_id(0)` 实际上拿到的是**物理核号**，因此 grid 必须按 AI Core 物理拓扑分布。

- **第二行（Limit）**：横向对比出 Ascend 的两个硬约束——总量约束 `grid ≤ AI Core 数` 与二维拓扑约束（当使用 `2D grid` 时必须与芯片 `2D 拓扑` 对齐）；GPU 侧则没有任何硬上限，靠硬件自动调度扩展。

### 表 2：Ascend NPU IR 编译选项

> 注：原文此表在 `enable_hivm_auto_cv_balance` 行末被截断，原文无"Enabled or Not"列的明确取值；以下逐字保留原文内容。

| Option | Capability | Enabled or Not |
|---|---|---|
| multibuffer | Data transfer through parallel pipelines. | Default: **true**. Options: **true** and **false**. It is configurable during autotune. |
| unit_flag | Optimization item for cube-out. | Default: None. Options: **true** and **false**. It is configurable during autotune. |
| limit_auto_multi_buffer_only_for_local_buffer | Optimization item for CV operators and cube-out. | Default: None. Options: **true** and **false**. It is configurable during autotune. |
| limit_auto_multi_buffer_of_local_buffer | Scope of enabling double buffer for cube operators. | Default: None. Value range: ["no-limit","no-l0c"]. It is configurable during autotune. |
| set_workspace_multibuffer | It takes effect only when **limit_auto_multi_buffer_only_for_local_buffer** is set to **false**. | Default: None. Example: [2,4]. It is configurable during autotune. |
| enable_hivm_auto_cv_balance | **set_workspace_multibuffer** takes effect only when **limit_auto_multi_buffer_only_for_local_buffer** is set to **false**. | Default: None. |

**逐行解读：**

- **multibuffer（多缓冲/流水线传输）**：唯一默认启用的选项（Default: true），开启后数据传输可走并行 pipeline，从而在 `tl.load` 计算与下一次数据传输重叠执行，是隐藏访存延迟的核心开关。
- **unit_flag**：面向 cube 算子输出（cube-out）的优化项，二值开关。
- **limit_auto_multi_buffer_only_for_local_buffer**：控制 multibuffer 是否仅作用于 local buffer 的开关，覆盖 CV 类算子和 cube-out 算子——它是一道"前置闸门"：后面两个选项 `set_workspace_multibuffer` 和 `enable_hivm_auto_cv_balance` 的生效都依赖此开关为 false。
- **limit_auto_multi_buffer_of_local_buffer**：把 cube 算子的双缓冲作用域收紧，值域 `["no-limit","no-l0c"]`——前者不限制，后者排除 L0c 缓存区。
- **set_workspace_multibuffer**：当上述"前置闸门"关闭时，进一步给出 workspace 的多缓冲倍率（例 `[2,4]` 含义未在原文展开，可理解为 2～4 份 buffer）。
- **enable_hivm_auto_cv_balance**：与 `set_workspace_multibuffer` 同条件下生效，与 Hivm（Host Interface Vector Module）的 CV 通路负载均衡相关，原文末尾"Default: None."的"Enabled or Not"列内容在原文中被截断。

---

## 【公式解读】

**原文 GELU 算子公式（Torch 版，伪代码形式）：**

$$
\text{res} = x_0 \times 0.5 \times \left(1.0 + \text{torch.erf}\!\left(\dfrac{x_0}{\text{torch.sqrt}(\text{torch.tensor}(2.0))}\right)\right)
$$

**Triton 版本（核内语义等价，调用 `tl.*` 算子）：**

$$
\text{ret} = x \times 0.5 \times \left(1.0 + \text{tl.erf}\!\left(\dfrac{x}{\text{tl.sqrt}(2.0)}\right)\right)
$$

**符号说明：**

- $x_0$ / $x$：输入张量（`in_ptr0`），Torch 版是宿主张量，Triton 版是装载到 on-chip memory 的子块元素。
- `0.5`：GELU 公式的线性项系数，与 erf 项求和后构成近似正态分布累计函数的取值缩放。
- `1.0`：常数偏置，与 erf 项加和后等价于把 erf 落在 (0,1) 范围的输出整体抬高。
- `torch.erf(...)` / `tl.erf(...)`：误差函数。GELU 使用 erf 形式 $\Phi(x) = 0.5 \times (1 + \text{erf}(x/\sqrt{2}))$ 来逼近标准正态 CDF，从而得到 GELU 近似 $0.5 x (1 + \text{erf}(x/\sqrt{2}))$。
- `torch.sqrt(torch.tensor(2.0))` / `tl.sqrt(2.0)`：$\sqrt{2}$，GELU 近似公式的分母常数。
- `res` / `ret`：返回值，写回 `out_ptr0` 张量。
- 约束作用：此公式在 `triton_easy_kernel` 中作用于一次性加载的整张输入；在 `triton_better_kernel` 中将 $x$ 替换为带 mask 的 $x_{index}$，即 $ret_{index} = x_{index} \times 0.5 \times \left(1.0 + \text{tl.erf}(x_{index}/\sqrt{2})\right)$，仅对 `xmask = x_index < xnumel` 命中的元素计算。

---

## 【关联】

**文末内部链接（原文给出）：**

- `../examples/06_autotune_example.md`：原文 "Compilation Optimization → Ascend NPU IR Optimization" 一节在介绍编译选项用法时，明示"For details, see [Autotune Example](../examples/06_autotune_example.md)"。本文档只是给出在 autotune 阶段通过 `triton.Config({'XS': 1 * 128, 'multibuffer': True})` 这类字典传入选项的**语法形式**，完整的 autotune 流程与调优样例（约束空间、runner、benchmark loop）由该示例文档承担。

**与文中其他模块/特性的关联（基于原文上下文还原）：**

- 与"**Multi-Core Task Parallelism Strategy**"的关系：GELU 示例的 `triton_better_kernel[ncore, 1, 1](...)` 一行同时承担"多核并行策略"（通过 `ncore=32` 显式指定 32 个核）和"单核数据传输策略"（通过 `xblock=32768` 划块）两节的桥梁。
- 与"**Autotune**"的关联：`ncore / xblock / xblock_sub` 的取值即 autotune 的搜索空间，与 `multibuffer=True` 等 IR 开关并列传入 `triton.Config`，原文示例 `triton.Config({'XS': 1 * 128, 'multibuffer': True})` 中 `XS` 是 tiling 类参数的另一种命名约定。
- 与代码内符号的关联：`x0`（输入张量）、`out1`（输出张量）、`x0.numel()`（元素总数，用于 mask 边界 `xnumel`）贯穿示例——它们是 `triton_better_kernel` 接口形参 `in_ptr0 / out_ptr0 / xnumel` 的调用现场。

---

## 【使用方法】

**1. 启用（硬件前提）：**
- 硬件：Ascend NPU（示例对应 Atlas 800T/I A2，on-chip memory 192 KB）。
- 软件：`triton-ascend`（已迁移至 https://github.com/triton-lang/triton-ascend）。

**2. 启动多核——launch 第一参数：**
```python
triton_gelu[n, 1, 1](...)  # n ≤ 65,535，且 n ≤ 当前设备 AI Core 总数
```

**3. 三级 Tiling 参数：**
| 参数 | 含义 | 示例取值 |
|---|---|---|
| `ncore` | 使用核数（跨核 tiling） | 32 |
| `xblock` | 核间数据块大小（inter-core tiling） | 32768 |
| `xblock_sub` | 核内细粒度大小（intra-core tiling） | 8192 |

总数据量参考：`ncore × xblock` 即单轮覆盖元素数（如 32 × 32768 = 1,048,576）。每轮单核数据体积须 ≤ on-chip memory 上限（Atlas 800T/I A2 为 192 KB）。

**4. 启用 IR 优化（autotune 配置阶段）：**
```python
def get_autotune_config():
    return [
        triton.Config({'XS': 1 * 128, 'multibuffer': True}),
    ]
```
- `multibuffer=True` 是默认行为（Default: true）。
- `unit_flag`、`limit_auto_multi_buffer_only_for_local_buffer`、`limit_auto_multi_buffer_of_local_buffer`、`set_workspace_multibuffer`、`enable_hivm_auto_cv_balance` 等开关同样以字典形式传入；`set_workspace_multibuffer` 取值形态示例 `[2,4]`，`limit_auto_multi_buffer_of_local_buffer` 取值形态示例 `"no-limit"` / `"no-l0c"`。详见原文链接的 autotune 示例文档。

**5. 注意事项（原文警戒）：**
- 原文章节"Precautions"明确：`triton_easy_kernel` 一次性把整张 `NUMEL` 装入 on-chip memory，**仅适用于小规模张量或入门演示**，大规模数据必须使用 `triton_better_kernel` 的 tiling 写法以免溢出 on-chip 192 KB 容量。
