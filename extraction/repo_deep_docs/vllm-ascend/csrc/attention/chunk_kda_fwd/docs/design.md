# ChunkKdaFwd 设计

> 仓 `vllm-ascend` · 路径 `csrc/attention/chunk_kda_fwd/docs/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/csrc/attention/chunk_kda_fwd/docs/design.md

# ChunkKdaFwd 设计文档深度解读

## 【定位】

本文档定义 `ChunkKdaFwd`（Chunk-based KDA 前向算子）的端到端设计：对外对齐 fla-org `chunk_kda_fwd` 顶层接口与 12 项返回契约，不新增公开算子原型，在 A2/A3/A5 三代硬件上统一数学定义的同时复用既有 `ChunkKdaFwd` 入口并保留 A5 regbase 双发射特化，同时让 FwdH 阶段可服务 KDA 与 GDN 两条通路。

---

## 【技术要点】

1. **接口对齐与原型收敛**：顶层对齐非 CP（Context Parallel）`fla-org chunk_kda_fwd`；不新增公开算子原型，A5 快路径复用既有 `ChunkKdaFwd` 原型与外层 kernel 入口；阶段选择仅依赖私有 `stage` 属性，不增加公开字段。
2. **架构统一与特化并存**：A2/A3/A5 共用同一数学定义；A5 单独保留 regbase 双发射；arch35 路径在 FwdH 上复用 `ChunkGatedDeltaRuleFwdH` 的数学实现。
3. **L2 分阶段调度**：调度流水线为 `raw g → ChunkKdaFwd[gate cumsum → Prepare/Post-WU → FwdH → Finalize] → attn_out`；A5 BF16 + chunk=64 + K=V=128 dense 对齐场景走单次物理 L0，A5 其他多 chunk 场景拆为四段 launch，其余场景维持单 launch。
4. **布局与状态约定**：内部递推统一 `[..., K, V]`；`state_v_first=true` 时在 L2 层进入 FwdH 前转置 `initial_state`；`hCompute` 保持 head-major，`hOut` 在导出边界转为 sequence-major。
5. **Tiling key 模板化**：两个 key 同属一个 L0 的编译期场景变体——`key=1` 为非 chunk=64 / K=V=128 的通用族，`key=2` 为 chunk=64、K=V=128 的族（含 dense / tail / varlen）；两个 key 在 A2/A3/A5 均生成，host `SetTilingKey` 仅判 chunk/K/V，不判 SoC。
6. **重计算 / 可选输出策略**：`final_state/gk/w/u/qg/kg/v_new/h` 以 `OPTIONAL_OUTPUT` 互不耦合，非空指针即导出；四段 launch 路径将阶段间依赖物化为 executor 内部张量；Python 层对齐 fla-org 提交 `0f0f0c97af39343855b43bbbaddcedfda5cb9d77`，规则化 `Aqk/Akk` 始终返回，`gk/hOut/final_state` 按开关决定导出。

---

## 【关键机制与数据】

### 工作原理与数据流（原文逐节梳理）

**L2 调度层**（原文："raw g → ChunkKdaFwd[...] → attn_out"）
- `aclnnChunkKdaFwd` 负责公开 layout 的连续化与必要视图转换。
- A5 BF16 + chunk=64 + K=V=128 dense 对齐快路径：单次物理 `ChunkKdaFwd` L0。
- A5 其他多 chunk 场景：同一私有 L0 按 **Gate/Prepare → Post-WU → FwdH → Finalize** 四阶段顺序提交，阶段间用物理 launch 边界重置事件状态。
- A2/A3 与单 chunk 场景：单次物理 L0。

**阶段职责链**（四阶段产物一览）

| 阶段 | 关键读取 | 关键产物 | 关键性质 |
|---|---|---|---|
| `KdaGateCumsum` | raw/已激活 gate | `gk`（FP32 chunk-local log2 累计） | 公式 `gk = cumsum(gate)/ln(2)`；同步提供 GDN2 独立 L2 接口，输入/输出固定 BNSD/NTD |
| `Prepare` | `q/k/v/gk/beta` + 变长元数据 | `Aqk, Akk, qg, qg_scaled, w_seed, u_seed` | 矩阵与三角求逆用 FP32 累积，公开中间量写回时转 q dtype |
| `Post-WU` | `k/gk/w_seed/Akk/u_seed` | `w, u, kg, v_new_seed` | `Akk` head 循环按 `H_v` 执行；GQA 映射只在读 q/k head 时换算 |
| `FwdH` | `kg/w/u/gk` + 可选 `initial_state` | `v_new, h_next` | arch35 复用 `ChunkGatedDeltaRuleFwdH`；其他场景在 `ChunkKdaFwd` 内嵌共享 FwdH；key-wise `gk` 固定 `exp2` |
| `Finalize` | `qg_scaled/Aqk/v_new/h` | `attn_out` | 按 BSND/TND 直接写出；反向所需中间量保持 BNSD/NTD |

**FwdH 状态递推核心公式**（原文逐字保留）
```
v_new = u - w @ h_prev
h_next = exp2(gk_last) * h_prev + kg^T @ v_new
```
- `exp2`（非 `exp`）确保与 log2 累计后的 gate 在数值上对齐。
- key-wise 路径固定使用 `exp2`，与 chunk-wise 路径统一。

**Finalize 公式**（原文逐字保留）
```
attn_out = qg_scaled @ h + Aqk @ v_new
```

**状态布局**
- 内部递推统一 `[..., K, V]`；`state_v_first=true` 在进入 FwdH 前由 L2 转置 `initial_state`。
- `hCompute`：head-major，给 Finalize 消费用。
- 公开 `hOut`：sequence-major，末两维顺序按 `state_v_first` 决定。
- `final_state`：按序列排列，与 FLA 顶层输出一致。

**重计算策略与 Python 对齐**
- Python/legacy 包装层对齐 fla-org 提交 `0f0f0c97af39343855b43bbbaddcedfda5cb9d77`：
  - `Aqk/Akk`：**始终返回**。
  - `disable_recompute=false` → **不**保留 `w/u/qg/kg/v_new`。
  - `disable_recompute=true` 或 `return_intermediate_states=true` → 保留公开 `hOut`。
  - `use_gate_in_kernel=false` 或 `disable_recompute=true` → 保留 `gk`。
  - `final_state` 仅在 `output_final_state=true` 时创建公开输出。
- 单 launch 路径：隐藏输出走固定 ABI 占位 + kernel workspace 承接中间结果。
- 四段 launch 路径：阶段间依赖 `gk/w/u/qg/kg/v_new/h/final_state` 及私有 `qg_scaled/u_seed` 物化为 executor 内部张量，**不**依赖前一 launch 的 kernel workspace。
- 第 12 项 `initial_state` 由 Python 层原对象透传（与 FLA 低层 12 返回值接口对齐）。

**模板化与 tiling key 选择规则**
- 唯一外层入口 `op_kernel/chunk_kda_fwd.cpp`，唯一私有 L0 类型；Prepare / Post-WU / Finalize 内部实现头与统一 kernel 入口同属 `chunk_kda_fwd/op_kernel/`，无独立 L0 原型或 `.cpp` 入口。
- A5 实现位于 `op_kernel/arch35/*.h`；host 侧 A5 模板选择位于 `op_host/arch35/*.h`。
- A5 四段路径只是用不同私有 `stage` 属性连续调用同一入口。
- `key=2` dense 对齐场景：单 launch + arch35 FwdH；融合 score 写回在跳过共享 PostWU 时，额外物化以块尾 gate 为参考的最终 `kg`，供 FwdH 与可选公开输出共用。
- A5 多 chunk 的 tail / varlen 以及 `key=1` 泛化场景：四段 launch。
- tiling key 与私有 `stage` **不**改变公开算子原型、输出契约或数学定义。

**性能设计原则**（原文逐条）
- Prepare 的右矩阵驻留 L1，避免 K/K^T 重复搬运与重复转置。
- AIC 使用 L1/L0 双缓冲组织 MTE2、MTE1、Cube、Fixpipe。
- AIV 使用输入 staging ping-pong，使下一 tile 的 MTE2 与当前 tile 的 VEC 重叠。
- A5 VEC 路径使用 regbase 双发射；数值主计算仍保持 FP32。
- inter-sub-chunk 合并使用独立 workspace 区域，避免阻塞主 tile 流水。
- 性能结论只使用 `msopprof`；目标回归 case 定义在 `tests/op_cases/chunk_kda_fwd.json`。

**验证矩阵**（原文逐条）
- 平台：A2 / A3 / A5。
- dtype：FP16 / BF16。
- layout：BSND / BNSD / TND / NTD。
- gate：raw / 已激活，safe true / false。
- Shape：K=128，V=128/256，chunk=64/128，dense / varlen / tail / GQA。
- 属性：final state、重计算策略、`state_v_first`。

---

## 【表格解读】

**原文无表格**（文档未包含任何 markdown / 文本表格，所有参数与配置项以正文叙述形式给出）。

为便于读者对照，将文档中关键分类枚举整理如下（**为便于阅读的二次归纳，原文以列表/叙述呈现，并非原文表格**）：

| 类别 | 原文枚举项 | 说明 |
|---|---|---|
| 平台 | A2、A3、A5 | 同一数学定义，A5 保留 regbase 特化 |
| dtype | FP16、BF16 | |
| layout | BSND、BNSD、TND、NTD | 输入/输出 layout 解耦 |
| gate | raw、已激活；safe true/false | KdaGateCumsum 同时服务 raw 与已激活 |
| Shape 维度 | K=128；V=128/256；chunk=64/128 | |
| 序列形式 | dense、varlen、tail、GQA | |
| 属性开关 | final state、重计算策略、`state_v_first` | |
| tiling key | key=1、key=2 | key=1=通用，key=2=chunk=64+K=V=128；均为同一 L0 编译期变体 |

---

## 【公式解读】

文档共出现四组公式，逐字保留如下：

**① Gate cumsum（KdaGateCumsum 阶段）**
```
gk = cumsum(gate) / ln(2)
```
- `gate`：输入的 raw 或已激活门控值，原始语义来自上游张量。
- `cumsum(gate)`：在 chunk 内对 gate 做累积求和；输出被约束为 chunk-local。
- `ln(2)`：将自然对数域的累计除以 `ln(2)`，转为以 2 为底的指数域；这是为了后续使用 `exp2` 而非 `exp` 时的数值一致性。
- `gk`：FP32 chunk-local log2 累计值，作为后续 FwdH 与 Finalize 的 gate 输入。

**② FwdH 状态递推（FwdH 阶段）**
```
v_new = u - w @ h_prev
h_next = exp2(gk_last) * h_prev + kg^T @ v_new
```
- `u`：Post-WU 产出的中间量（chunk 局部值变换）。
- `w`：Post-WU 产出的中间量。
- `h_prev`：上一 chunk 末态（或 `initial_state`），形状 `[..., K, V]`，由 `[..., K, V]` 内部约定保证。
- `v_new`：本 chunk 写入值增量。
- `gk_last`：本 chunk 末尾的 gate 累计（log2 域），scalar 形式乘到 `h_prev` 上做递推衰减/保持。
- `exp2(gk_last)`：以 2 为底的指数，与 `gk` 的 log2 累计一致；确保乘性 gate 与加性 gate 数学等价。
- `kg`：Post-WU 产出的中间量，作为 `v_new` 的写入权重。
- `kg^T @ v_new`：将 `v_new` 沿 V 维聚合后写回 `h_next`，完成 state 写入。
- `h_next`：本 chunk 末态，传给下一 chunk 或作为 `final_state` 导出。

**③ Finalize（Finalize 阶段）**
```
attn_out = qg_scaled @ h + Aqk @ v_new
```
- `qg_scaled`：Prepare 产出的 q 经 gate 缩放后的量。
- `h`：Finalize 阶段读取的 `h`，对应 `hCompute`（head-major）形态。
- `Aqk`：Prepare 产出的中间量，构成 v 维聚合权重。
- `v_new`：FwdH 阶段产出的本 chunk 写入增量。
- `qg_scaled @ h`：通过状态读出 attn 主体部分。
- `Aqk @ v_new`：用 `Aqk` 对 `v_new` 做线性组合，补足 v 维信息。
- `attn_out`：按 BSND/TND 直接写出的最终注意力输出。

**④ L2 调度流水线伪代码**
```text
raw g -> ChunkKdaFwd[
    gate cumsum -> Prepare/Post-WU -> FwdH -> Finalize
] -> attn_out
```
- 描述从 `raw g` 到 `attn_out` 的端到端流水线，括号内为 `ChunkKdaFwd` 内部分阶段顺序。

---

## 【关联】

文末未提供内部链接（"内部链接: (无)"），但文档在叙述中显式关联了以下模块 / 文件 / 上游依赖：

- **fla-org `chunk_kda_fwd`**：顶层接口对齐对象；具体 Python/legacy 包装层对齐提交 `0f0f0c97af39343855b43bbbaddcedfda5cb9d77`。
- **`ChunkGatedDeltaRuleFwdH`**：arch35 路径在 FwdH 阶段复用的同名数学实现，提供与既有 GDN 路径的代码复用关系。
- **GDN2**：通过 `KdaGateCumsum` 的独立 L2 接口被 GDN2 调用，使同一 cumsum 算子服务 KDA 与 GDN。
- **既有 `ChunkKdaFwd` 算子原型与外层 kernel 入口**：A5 快路径复用对象，本设计不引入新原型。
- **代码组织**：
  - 外层入口：`op_kernel/chunk_kda_fwd.cpp`
  - Prepare / Post-WU / Finalize 内部实现头：`chunk_kda_fwd/op_kernel/`
  - A5 实现：`op_kernel/arch35/*.h`
  - A5 host 模板选择：`op_host/arch35/*.h`
- **`aclnnChunkKdaFwd`**：负责公开 layout 的连续化与视图转换，是算子的公开 aclnn 入口。
- **测试 / 性能**：
  - 性能剖析工具：`msopprof`（唯一被允许出具性能结论的工具）。
  - 回归 case：`tests/op_cases/chunk_kda_fwd.json`。

---

## 【使用方法】

文档**未**直接以"命令行 / API 用法"形式给出启用步骤，但给出了与 Python/legacy 包装层对齐的开关语义，可作为启用与配置依据（原文有则写）：

- **`output_final_state=true`**：创建并返回 `final_state` 公开输出；否则 `final_state` 不导出。
- **`return_intermediate_states=true`**：与 `disable_recompute=true` 任一为真时，保留公开 `hOut`。
- **`disable_recompute`**
  - `false`：不保留 `w/u/qg/kg/v_new`（隐藏输出不导出）。
  - `true`：保留 `w/u/qg/kg/v_new`，并保留 `gk`、保留公开 `hOut`。
- **`use_gate_in_kernel=false`**：保留 `gk` 公开输出（即便 `disable_recompute=false`）。
- **`state_v_first=true`**：L2 在进入 FwdH 前转置 `initial_state`；公开 `hOut` 末两维顺序随之调整。
- **gate 输入形式**：支持 raw gate 与已激活 gate 两种，`safe` 开关支持 `true/false`；`KdaGateCumsum` 同时提供独立 L2 接口供 GDN2 调用（输入/输出固定 BNSD/NTD）。
- **shape / 平台覆盖**：A2 / A3 / A5；FP16 / BF16；K=128，V=128 或 256；chunk=64 或 128；支持 dense / varlen / tail / GQA。
- **tiling key 选择**：由 host `SetTilingKey` 根据 chunk、K、V 自动判定 `key=1`（通用）或 `key=2`（chunk=64 + K=V=128），不感知 SoC。
- **stage 触发**：`stage` 为私有属性，由 L2 内部按场景自动决定单 launch 或四段 launch（A5 四段路径仅用不同 `stage` 属性连续调用同一入口），不暴露给用户。

> 注：原文未涉及具体的 Python 调用示例、`aclnn` 调用模板或 `torch.ops` 装载命令，故仅整理上述语义层开关；如需进一步用法，请参考 fla-org `chunk_kda_fwd` 在 `vllm-ascend` 仓库中的 Python/legacy 包装层实现。
