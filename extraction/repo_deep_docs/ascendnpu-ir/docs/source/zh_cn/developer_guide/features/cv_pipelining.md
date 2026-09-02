# Cube与Vector软件流水优化

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/cv_pipelining.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/cv_pipelining.md

# Cube与Vector软件流水优化 —— 一体化深度解读

## 【定位】
本文档描述HIVM中 **CV Pipelining Pass** 的能力：针对MIX算子中Cube与Vector指令存在相互依赖的循环（如FlashAttention等场景），通过将两类指令拆分为独立的Work Item并进行软件流水，使其在昇腾硬件上异步并行执行，从而提高指令级并行度（ILP）和硬件利用率。

---

## 【技术要点】
1. **优化对象**：MIX算子中含多个Cube与Vector指令**相互依赖**的循环（如FlashAttention）。
2. **硬件前提**：昇腾核心包含Cube核心（矩阵乘）和Vector核心（其他向量运算），二者**无依赖时可并行异步运行**。
3. **核心机制**：寻找适当的`for`循环 → 将Cube与Vector指令**分离为独立Work Item** → 建立Work Item间的数据依赖 → 将需扩展成multi-buffer的`tensor`扩展 → **原循环unroll** → 将每个Work Item放入**单独循环**中。
4. **Multi-Buffering副作用**：会导致部分UB（Unified Buffer）空间占用更多，需根据实际场景调整软流水阶段数以取得最佳性能。
5. **编译选项**：
   - `set-workspace-multibuffer`：默认值 **2**（软件流水阶段数 = Multi-Buffering数量）
   - `--enable-lazy-loading`：默认值 **false**（允许将Load op克隆到多个Work Item以减少中间buffer扩展）
6. **算子侧提示**：可通过`extension.compile_hint(t, "cv_pipeline_lazy_load", True)`为指定tensor开启Lazy Load。

---

## 【关键机制与数据】

**工作原理（数据流与变换）**：

**变换前**（原文MLIR伪代码）：
- 单层`scf.for`循环，迭代步长为`S`。
- 每个迭代顺序执行：`Cube()` → `Vector(%c)` → `Cube(%v)` → `Vector(%c1)`，四次调用均为`tensor<16x16xf32>`。

**变换后**（原文MLIR伪代码）：
- 外层`scf.for`步长由`S`变为`3*S`（原文：`scf.for 0 to N step 3*S`）。
- 内部**4个独立的`scf.for`**（步长均为3），分别对应一个Work Item（cube_loop / vector_loop交替出现）：
  - `%c`：`cube_loop`，产出`tensor<3x16x16xf32>`（multi-buffer展开）。
  - `%v`：`vector_loop`，从`%c`中`extract_slice`，产出`tensor<3x16x16xf32>`。
  - `%c1`：`cube_loop`，从`%v`中`extract_slice`，产出`tensor<3x16x16xf32>`。
  - `%v1`：`vector_loop`，**保持`tensor<16x16xf32>`**，原文注释："When no other Work Item needs the result, no buffer expansion needed"。

**性能/代价数据**（原文）：
- 原文未给出具体性能数字。
- 代价：UB空间占用更多（因Multi-Buffering），需权衡调整阶段数。
- 收益：通过Cube/Vector并行获得更高**ILP**（指令级并行度）。

---

## 【表格解读】

**编译选项表（原文逐字还原）**：

| 选项 | 默认值 | 含义 |
|------|--------|------|
| `set-workspace-multibuffer` | 2 | 软件流水的阶段数，同时也是Multi-Buffering的数量 |
| `--enable-lazy-loading` | false | 开启CV Pipelining中的Lazy Load功能，允许将Load op克隆到多个Work Item中，以减少中间buffer扩展 |

**逐行解读**：
- **`set-workspace-multibuffer`（默认值2）**：直接控制软件流水阶段数。该值同时即为Multi-Buffering的buffer数量，例如默认2即每个被扩展的tensor会被复制为2份，以避免流水读写冲突。**调大**：提升并行度，但增加UB占用；**调小**：节省UB，但流水线深度降低、并行度下降。
- **`--enable-lazy-loading`（默认值false）**：开启后允许将Load op（数据加载操作）克隆到多个Work Item中。目的是**复用加载结果，减少因中间buffer扩展带来的内存膨胀**。在某些场景下可降低multi-buffer带来的UB压力。

---

## 【公式解读】

**原文无数学公式**（无LaTeX表达式的数学推导）。

但文档提供了**MLIR变换伪代码**作为形式化机制描述，其关键"结构"可理解为：

$$
\text{变换前: } \forall i \in [0, N) \text{ step } S,\quad C_i \to V_i \to C_i' \to V_i' \quad (\text{串行})
$$

$$
\text{变换后: } \exists K \in \{3,\ldots\},\ \forall j \in [0, K) \text{ 独立循环},\ \text{步长 } 3S
$$

其中关键符号含义（来自原文MLIR）：
- `scf.for 0 to N step 3*S`：外层循环，步长变为`3*S`，反映unroll后阶段数×原步长。
- `tensor<3x16x16xf32>`：3即multi-buffer展开份数，16×16即单份tensor的原始形状。
- `extract_slice` / `tensor.insert_slice`：在独立Work Item间按版本号（如0/1/2）读写对应缓冲区。
- `{cube_loop}` / `{vector_loop>`：Work Item的类型标记，决定该循环承载的是Cube还是Vector指令。
- `-> tensor<16x16xf32>`（最后`%v1`处）：表示无下游依赖时**不进行buffer扩展**。
- 迭代边界`0 to 3`：与multi-buffer份数一致，每个阶段填充对应槽位。

---

## 【关联】

**前置依赖（文首引用）**：
- **./cv_optimization.md**（CV Optimization）：文档首句明确建议读者在阅读本文之前先阅读CV Optimization，以了解CV编译相关术语。这是本文的唯一内部链接，构成**强前置关系**——CV Pipelining Pass作用于CV类kernel之上，CV Optimization文档中的术语（如kernel分类、Cube/Vector算子语义、编译流程等）是理解本文的基础。

**功能互补**：
- 本文Pass属于HIVM（HIVM是AscendNPU-IR中面向昇腾亲和算子编译的模块）针对CV类kernel的**性能优化**手段，与CV Optimization属于"基础编译 → 性能调优"层级关系。
- Multi-Buffering机制与通用AI编译中**double buffering / triple buffering**概念同源，但本文将Multi-Buffering阶段数暴露为`set-workspace-multibuffer`编译选项，供用户按场景微调。
- Lazy Load特性（`--enable-lazy-loading` / `cv_pipeline_lazy_load`）是CV Pipelining的**辅助开关**，用于缓解buffer扩展带来的内存压力。

---

## 【使用方法】

**1. 全局编译选项（影响所有受Pass处理的算子）**：
- 设置软流水阶段数：`set-workspace-multibuffer`（默认2），值越大并行度越高、UB占用越多。
- 开启Lazy Load：`--enable-lazy-loading`（默认false），将Load op克隆到多个Work Item以减少中间buffer扩展。

**2. 算子级细粒度控制（仅对指定tensor生效）**：
- 通过算子侧的编译提示接口：
  ```python
  extension.compile_hint(t, "cv_pipeline_lazy_load", True)
  ```
  为特定tensor `t`开启Lazy Load功能，作用粒度比`--enable-lazy-loading`更细。

**3. 使用约束（决定能否开启Pipeline）**：
- 支持Pipeline的循环中，仅 `scf.for` 与 `scf.if` op 可包含region/block；这些算子的region内部**仅允许存在cube或vector指令**。
- **迭代间的数据依赖必须能够拆分到各自独立的Work Item中**。原文给出两种典型场景判断：
  - **无法开启CV-Pipelining**：若`v0`与`v1`无法被提取至同一Work Item（因为中间有Cube依赖），同时参数`arg0`由`v1`定义却被`v0`使用——形成跨Work Item的回路依赖。
  - **CV-Pipelining可正常生效**：若Cube未使用`v0`，则`v0`可下沉至`v1`所在的Work Item，此时依赖可拆分、流水线可建立。
- 原文示例MLIR（用于对照理解）：
  ```mlir
  scf.for iter_args(%arg0 = %init) {
      %v0 = Vector(%arg0)
      %c = Cube(%v0)
      %v1 = Vector(%c)
      yield %v1
  }
  ```
