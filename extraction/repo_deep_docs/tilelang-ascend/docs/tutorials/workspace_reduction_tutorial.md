# TileLang-Ascend Workspace Reduction Tutorial

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/workspace_reduction_tutorial.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/workspace_reduction_tutorial.md

# TileLang-Ascend Workspace Reduction Tutorial 深度解读

---

## 【定位】

这篇文档解决的是 **Ascend 架构下 Cube 核与 Vector 核无法直接交换数据** 所带来的编程复杂性问题——通过编译器自动化的 "Workspace Reduction" 机制,让用户用单条 `T.copy` 语句即可完成跨核数据搬运,由编译器自动完成 workspace 分配、两段式 GM 拷贝插入与多核偏移管理。

---

## 【技术要点】

文档围绕 Workspace Reduction 给出以下核心机制:

1. **跨核通信背景**: Ascend 架构中 Cube 与 Vector 核心之间无法直接交换数据,传统方案必须经过 Global Memory (GM) 中转,涉及显式 workspace 缓冲区声明、生命周期管理与 offset 计算,增加前端脚本编写难度。

2. **自动 workspace 分配 (Automate workspace allocation)**: 编译器为跨核数据传输自动创建 GM workspace 缓冲区,用户无需手动声明。

3. **两段式 copy 转换 (Transform copy statements)**: 将直连的 `copy_l0c_to_ub` 与 `copy_ub_to_l1` 转换为基于 GM 的两段式拷贝 (L0C → GM → UB 与 UB → GM → L1)。

4. **多核支持 (Support multi-core scenarios)**: 每个 AI Core 通过 `cid` 偏移获得独立的 workspace 区域。

5. **Vector 核切分处理 (Handle vector core splitting)**: 当 `threads=2` 时,workspace 存储完整数据,UB 端按 `vid` 进行切分。

6. **编程模型简化 (Simplify programming model)**: 用户只写单条 `T.copy` 语句,由编译器统一负责 workspace 管理,无需显式两段式脚本。

> **启用方式**: Workspace Reduction 在编译流水线中 **自动启用**,不需要任何手动配置 ("Workspace Reduction is **automatically enabled** in the compilation pipeline. No manual configuration required.")。

---

## 【关键机制与数据】

### 工作原理

原文描述的传统流程 (无 Workspace Reduction 时) 是显式三步:

1. Cube 将结果写入 Global Memory (GM);
2. Vector 从 GM 读回数据;
3. 两个核心之间可能存在同步开销 ("Potential synchronization overhead between cores")。

Workspace Reduction 的介入点是在用户的源代码层——它对下面这种 **直接跨核拷贝语句** 进行变换:

```python
T.copy(acc_s_l0c, acc_s_ub)  # ← Workspace Reduction triggered
```

注释 "# ← Workspace Reduction triggered" 明确指出:只要出现 L0C → UB 的直连 copy 语句,Workspace Reduction 即被触发,由编译器将其改写为 L0C → GM (workspace) → UB 的两段式流程。

### 数据流 (以 FlashAttention 为例)

文档在 §2.2 给出了完整的数据流链路,可逐句对应 Cube/Vector 角色:

- `T.gemm_v0(q_l1, k_l1, acc_s_l0c, transpose_B=True, init=True)` → **Cube 端**, 计算 Attention score 写入 L0C (`acc_s_l0c`);
- `T.copy(acc_s_l0c, acc_s_ub)` → 触发 Workspace Reduction 的 L0C → UB 搬运;
- `T.tile.exp` / `T.reduce_max` / `T.tile.sub` 等 → **Vector 端**, 在 UB 上完成 Softmax 计算。

整段 kernel 在 `threads=2, is_npu=True` 的并行维度下运行,`cid` 用于多核 workspace 区域切分,`vid` 用于 vector 核内的 UB 数据切分。

### 性能/数据相关数字

**原文未给出任何定量性能数据 (无吞吐、无 latency、无加速比)**。文档仅在限制条件处提供若干静态参数,详见下一节"使用方法"中的数字约束。

---

## 【表格解读】

**原文无表格。**

整篇文档未包含任何参数表、性能对比表或配置项表。所有信息均以文字描述与代码片段形式给出。

---

## 【公式解读】

**原文无公式。**

文档中未出现任何 LaTeX 公式或伪代码形式的数学表达式;数据流均通过 Python 代码片段 (`@T.prim_func` kernel 示例) 描述。

---

## 【关联】

文档与以下特性/模块/示例存在明确上下游关系:

1. **FlashAttention 示例 (核心关联)**:
   - 文档正文 §2.2 显式链接到 `../../examples/developer_mode/flash_attn_bshd_developer.py`,作为 Workspace Reduction 在真实算子 (FlashAttention) 中应用的 "Practical Example"。
   - §2.1 的 "Basic Example (Expert Mode)" 同样描述了相同的 `T.copy(acc_s_l0c, acc_s_ub)` 模式,可视为该完整示例的最小化抽象。

2. **Vid Reduction (强依赖)**:
   - §3.1 明确指出 Workspace Reduction 需要与 Vid Reduction 协同工作 ("Requires coordination with Vid Reduction"),约束条件为 `threads` 参数必须设置为 **1 或 2**。
   - 这意味着 Workspace Reduction 不是独立特性,而是 Ascend 编译流水线中与 Vid Reduction 配套的子模块。

3. **Sparse Flash Attention (SFA) 算子 (应用边界)**:
   - §3.2 "Skip UB scenario" 提到 Workspace Reduction 目前仅在 SFA 算子的 **indices array transfer** 场景中得到支持,这是其当前唯一被验证过的 "skip UB" 用例。

4. **Ascend Cube / Vector 异构核心架构 (上游背景)**:
   - 文档 §1 的 Design Goals 起源于 Cube 与 Vector 核无法直接交换数据的硬件事实,Workspace Reduction 是针对该硬件约束的编译层解决方案。

5. **未来作用域拷贝插入 (Scoped copy-back insertion)**:
   - §3.3 提出的未来增强方向——"region-based copy insertion strategy"——暗示现有方案仍存在跨核同步冗余开销,与 Workspace Reduction 形成演进关系。

---

## 【使用方法】

### 启用方式

- **自动启用**: Workspace Reduction 无需用户手动配置,在编译流水线中自动生效 ("Workspace Reduction is **automatically enabled** in the compilation pipeline. No manual configuration required.")。

### 用户代码层用法

用户只需在 `T.Kernel` 块中正常书写直连 copy 语句,例如:

```python
with T.Kernel(..., threads=2, is_npu=True) as (cid):
    T.gemm_v0(q_l1, k_l1, acc_s_l0c, ...)
    T.copy(acc_s_l0c, acc_s_ub)   # 自动触发 Workspace Reduction
    T.tile.exp(acc_s_ub, acc_s_ub)
```

### 关键配置/约束参数 (原文明确给出)

| 参数 | 取值要求 | 出处 |
|---|---|---|
| `threads` | 必须为 `1` 或 `2` | §3.1 "Current Constraints" |
| Workspace shape | 必须为 2D `[M, N]` (当前);未来扩展到更高维 | §3.2 "Known Limitations" |
| Shape 性质 | 必须为编译期静态常量,不支持动态 shape | §3.1 / §3.2 |
| `is_npu` | `True` (从示例代码可观察到,Ascend 专用路径) | §2.1 / §2.2 代码 |
| 多核机制 | 通过 `cid` 偏移分配独立 workspace 区域 | §1 |
| 向量切分 | `threads=2` 时,workspace 存完整数据,UB 端按 `vid` 切分 | §1 |

### 命令/编译选项

**原文未涉及任何 CLI 命令、编译 flag 或环境变量**。文档强调该特性在编译流水线中自动启用,未给出开关式配置项。

### 当前已知限制 (影响使用方法)

- 静态 shape 是硬性要求,动态 shape 尚未支持;
- workspace 维度仅支持 2D;
- Skip UB 场景目前只覆盖 SFA 算子的 indices array transfer。

### 未来增强 (原文提及,尚未实现)

- **Scoped copy-back insertion**: 在 region 边界、所有数据消费者之前插入 Stage 2 copy 语句,以减少 copy 与 compute 操作的交错,降低跨核同步冗余开销 (§3.3)。

---

> **参考链接**: 完整可运行示例见 [`flash_attn_bshd_developer.py`](../../examples/developer_mode/flash_attn_bshd_developer.py)。
