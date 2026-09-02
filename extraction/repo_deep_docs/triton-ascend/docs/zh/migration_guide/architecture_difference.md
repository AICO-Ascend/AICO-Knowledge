# 昇腾与GPU的开发差异

> 仓 `triton-ascend` · 路径 `docs/zh/migration_guide/architecture_difference.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-ascend/docs/zh/migration_guide/architecture_difference.md

# 昇腾与GPU开发差异文档深度解读

## 【定位】

这篇文档是 **triton-ascend 迁移指南中的架构差异总览**，从多核并行策略、单核数据搬运（分块 Tiling）策略、AscendNPU IR 编译优化能力三个层面，对比了 Triton 在昇腾 NPU 与 NVIDIA GPU 上开发范式的核心差异，帮助开发者把 GPU 上"逻辑 grid + 自动硬件映射"的心智模型迁移到 NPU 的"物理核强绑定 + 显式分块调优"模型上。

---

## 【技术要点】

1. **grid 本质不同**：GPU 的 grid 是与物理核解耦的逻辑任务维度（无硬限制，可三维 `grid=[n,m,l]` 乘积展开）；昇腾 grid 是绑定 AI Core 拓扑的物理核映射，`grid 大小 ≤ AI Core 总数`，2D 需匹配硬件拓扑。
2. **执行单元不同**：GPU 一个 grid 线程对应一次 kernel 执行的最小单元；NPU 上 Vector 核与 Cube 核分属多物理核，每个核执行一个 Block，但**支持对该 Block 重复调度执行**。
3. **核数调优上限**：通过 launch 形参 `triton_gelu[n, 1, 1](...)` 显式控制使用的核数，**当前版本核数需 ≤ 65535**。
4. **三层切分参数**：以 GELU 为例有 `ncore`（跨核切分）、`xblock`（核间数据块大小）、`xblock_sub`（核内细粒度划分）；GELU 高效样例取 `ncore=32, xblock=32768, xblock_sub=8192`。
5. **片上内存约束**：Atlas 800T/I A2 的片上内存容量为 **192KB**，每轮计算的数据量不得超过此上限，否则触发内存溢出。
6. **AscendNPU IR 编译选项**：9 个 `triton.Config` 可配项（如 `multibuffer`、`unit_flag`、`tile_mix_vector_loop`、`auto_blockify_size` 等），覆盖流水并行、Cube 搬出优化、CV 混合算子切片与 `TRITON_ALL_BLOCKS_PARALLEL` 扩展维度等场景。

---

## 【关键机制与数据】

- **多核并行机制（原文）**："NPU在Triton多核并行中是物理核强绑定模式，与GPU逻辑维度并行+硬件自动物理映射的模式形成核心差异"。在 GPU 上，一次 launch 提交的 grid 总量 (`n×m×l`) 只决定逻辑并行度，由硬件调度器映射到 SM；在 NPU 上，grid 的第一维大小直接对应要启用的 AI Core 数量，开发者必须显式规划。
- **单核 Block 重调度（原文）**："每个核仅执行一次Block,且支持对该Block重复调度执行"。这意味着 NPU 的"循环"既可以由开发者用 `tl.range`/Python `for` 写在 kernel 里（核内循环），也可以由运行时把同一 Block 重复发到同一核上（核间重复）。
- **数据搬运机制（原文）**：通过 `tl.load()` 把全局内存中的 tile 搬到片上，`tl.store()` 把结果写回全局；GELU 高效版本用 `xmask = x_index < xnumel` 做边界保护，确保 tile 切分不越界。
- **192KB 上限（原文）**："Atlas 800T/I A2产品的片上内存容量为192KB"，所以 `XBLOCK_SUB=8192`（以 fp32 计 ≈32KB）这种粒度选择是受此约束直接推导出来的设计取舍。
- **65535 核数上限（原文）**："当前版本核数需小于等于65535"，这是 launch 第一维参数的硬性上限，决定了单次 launch 能并行覆盖的最大数据规模上界。
- **CV 算子定义（原文）**："CV算子表示该算子运算过程中既使用了AI Core又使用了Vector Core"，这一概念决定了 `tile_mix_vector_loop`、`tile_mix_cube_loop` 等多个 IR 选项的适用对象。

---

## 【表格解读】

### 表 1：GPU vs 昇腾 grid 本质与限制对比（原文逐字还原）

| 维度 | GPU（NVIDIA） | 昇腾（Ascend） |
|---|---|---|
| grid 本质 | 逻辑任务维度（和物理核解耦） | 物理核组映射（绑定 AI Core 拓扑） |
| 核数 / 维度限制 | grid 维度 / 大小无硬限制 | grid 大小≤AI Core 总数，2D 需匹配拓扑 |

- 第 1 行 `grid 本质`：揭示两者根本差异——GPU 把 grid 当作"逻辑任务量"，由运行时调度到 SM；昇腾则把 grid 直接视作"要占用的物理核"，必须与 AI Core 拓扑对齐。
- 第 2 行 `核数/维度限制`：GPU 端没有硬上限，理论上三维 grid 的乘积可以非常大；昇腾端第一维大小不能超过 AI Core 总数，并且使用 2D grid 时必须按硬件拓扑做匹配（例如 Cube 核与 Vector 核的排布），否则可能编译失败或性能退化。

### 表 2：AscendNPU IR 编译选项清单（原文逐字还原）

| 选项 | 能力 | 是否开启 |
|---|---|---|
| multibuffer | 开启流水并行数据搬运 | 默认 true；true, false。autotune 中可配置 |
| unit_flag | cube 搬出的一个优化项 | 默认 None；true, false。autotune 中可配置 |
| limit_auto_multi_buffer_only_for_local_buffer | CV 算子一个优化项，cube 搬出的一个优化项 | 默认 None；true, false。autotune 中可配置 |
| limit_auto_multi_buffer_of_local_buffer | cube 算子开启 double buffer 具体的 scope | 默认 None；["no-limit", "no-l0c"]，autotune 中可配置 |
| set_workspace_multibuffer | 只有在 limit_auto_multi_buffer_only_for_local_buffer=false 场景下生效 | 默认 None；如 [2,4]，autotune 中可配置 |
| enable_hivm_auto_cv_balance | set_workspace_multibuffer 只有在 limit_auto_multi_buffer_only_for_local_buffer=false 场景下生效 | 默认 None；true, false。autotune 中可配置 |
| tile_mix_vector_loop | CV 算子的一个优化项，当前 vector 可以切几份 | 默认 None；如 [2,4,8]，autotune 中可配置 |
| tile_mix_cube_loop | CV 算子一个优化项，当前 cube 可以切几份 | 默认 None；如 [2,4,8]，autotune 中可配置 |
| auto_blockify_size | TRITON_ALL_BLOCKS_PARALLEL 优化项，用于指定扩展的左起第一个维度的大小 | 默认 1；如 [2,4,8]，autotune 中可配置 |

逐行解读：

- **multibuffer**：唯一默认开启（true）的项，启用后计算与数据搬运可以流水并行，是 NPU 上掩盖 DDR 延迟的关键开关。
- **unit_flag**：Cube 核数据搬出阶段的一个开关，用来打开特定的搬出优化路径。
- **limit_auto_multi_buffer_only_for_local_buffer**：控制 multi-buffer 自动展开是否仅作用于 Local Buffer（即 L1/UB 等片上 buffer），常用于 CV 混合算子，避免对 GM/L2 等大容量存储做无谓的 double buffer。
- **limit_auto_multi_buffer_of_local_buffer**：限定 cube 算子 double buffer 的具体 scope，可选 `no-limit`（全放开）或 `no-l0c`（排除 L0C 这类高带宽小容量 buffer）。
- **set_workspace_multibuffer**：在 `limit_auto_multi_buffer_only_for_local_buffer=false` 场景下生效，配置 workspace buffer 的多 buffer 数量（如 `[2,4]`），决定 pipeline 深度。
- **enable_hivm_auto_cv_balance**：同样依赖 `limit_auto_multi_buffer_only_for_local_buffer=false` 前提，让 Hivm（异构指令虚拟机）模块自动平衡 Cube 与 Vector 之间的负载。
- **tile_mix_vector_loop**：把 vector 计算再切成多片，常用于 vector 计算耗时占比高、需要更细粒度流水的情形，候选 `[2,4,8]`。
- **tile_mix_cube_loop**：与上一项对偶，把 cube 计算切成多片，候选同样是 `[2,4,8]`，由 autotune 选最优切分。
- **auto_blockify_size**：与 `TRITON_ALL_BLOCKS_PARALLEL` 联合使用，控制被扩展的最左侧维度大小（如 `[2,4,8]`），决定 block 化的并行展开粒度，默认 1 表示不展开。

---

## 【公式解读】

**原文无公式**。文档中的 GELU 计算表达式均以 Python/Triton 代码形式给出（如 `x * 0.5 * (1.0 + tl.erf(x / tl.sqrt(2.0)))`），未使用 LaTeX 或伪代码形式的数学公式。

若需指出代码中隐含的数学式，可视为：

$$y = x \cdot \tfrac{1}{2} \cdot \left(1 + \mathrm{erf}\!\left(\tfrac{x}{\sqrt{2}}\right)\right)$$

其中 $x$ 是输入张量元素，$\mathrm{erf}$ 是高斯误差函数，$y$ 是 GELU 激活的输出。但该式并非原文以公式形式呈现，仅作为代码语义补充。

---

## 【关联】

- **autotune 示例（`../examples/06_autotune_example.md`）**：文档中 "编译优化能力 → AscendNPU IR 优化" 一节明确把 `multibuffer=True` 的 `triton.Config({'XS': 1 * 128, 'multibuffer': True})` 用作示例，并指引读者查阅 autotune 示例页面；后者承担"如何把这些 IR 选项放进 autotune 候选配置并自动选择最优"的实操职责，是本篇文档的直接下游。
- **triton.Config / autotune 机制**：表 2 中所有 IR 选项均通过 `triton.Config` 在 autotune 阶段注入，因此本文与 `triton.autotune` 的候选配置机制紧密耦合。
- **Triton 编程基本接口**：本文示例依赖 `tl.load`、`tl.store`、`tl.arange`、`tl.program_id`、`tl.constexpr` 等基础 API，与 triton-ascend 文档体系中"Kernel 编程入门"层级的 API 文档形成上下游依赖。
- **Atlas 800T/I A2 硬件规格**：192KB 片上内存这一数字来自具体硬件平台，与硬件规格说明文档相关；AI Core 总数、Vector/Cube 核拓扑决定 `ncore` 与 2D grid 的实际取值上限。
- **GELU 算子示例**：本文用 GELU 作为载体，从 `standard_unary`（Torch）→ `triton_easy_kernel`（无分块）→ `triton_better_kernel`（带 Tiling）逐步演进，体现"从 GPU 直觉写法到 NPU 高效写法"的迁移路径，与迁移指南其他算子示例同构。

---

## 【使用方法】

- **控制使用核数**：通过 launch 元组第一维传入 `triton_gelu[n, 1, 1](...)`，其中 `n` 为启用的核数，**需 ≤ 65535**。
- **配置切分参数**：在调用 `triton_better_kernel` 时传入 `ncore`、`xblock`、`xblock_sub` 三个参数；文档样例取 `ncore=32, xblock=32768, xblock_sub=8192`，并受 Atlas 800T/I A2 的 **192KB 片上内存**约束。
- **启用 IR 优化选项**：在 autotune 配置阶段（即 `triton.Config` 字典中）传入键值，例如：

  ```python
  def get_autotune_config():
      return [
          triton.Config({'XS': 1 * 128, 'multibuffer': True}),
      ]
  ```

  其它可用键包括 `unit_flag`、`limit_auto_multi_buffer_only_for_local_buffer`、`limit_auto_multi_buffer_of_local_buffer`（取值如 `["no-limit", "no-l0c"]`）、`set_workspace_multibuffer`（如 `[2,4]`）、`enable_hivm_auto_cv_balance`、`tile_mix_vector_loop`、`tile_mix_cube_loop`、`auto_blockify_size`（如 `[2,4,8]`）。完整选项与默认值见表 2。
- **参考代码位置（原文注）**："优化编译选项在 `ascend/backend/compiler.py` 代码中"，如需查阅默认实现可定位到该文件。
