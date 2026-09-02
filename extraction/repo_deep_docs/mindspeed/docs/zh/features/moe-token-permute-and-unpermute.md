# MoE Token Permute and Unpermute 融合优化

> 仓 `mindspeed` · 路径 `docs/zh/features/moe-token-permute-and-unpermute.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/moe-token-permute-and-unpermute.md

# MoE Token Permute and Unpermute 融合优化 — 一体化深度解读

---

## 【定位】

本文档针对 MoE（Mixture of Experts）架构中 **MoEAlltoAllTokenDispatcher 调度器在 Token 重排（Permute）与结果重组（Unpermute）两步产生的密集数据移动性能瓶颈**，描述了 MindSpeed 将这两个操作分别融合为单一算子的优化方案、启用方式、推荐配套配置、兼容性限制及系统环境要求。

---

## 【技术要点】

1. **优化对象**：MoE 流程中的两个特定步骤——**Token 数据重排（Permute）**与**专家处理后结果重组（Unpermute）**；前者按专家分组 token，后者将分散结果还原到原始 token 顺序。
2. **优化手段**：MindSpeed 将 "MoE Token Permute" 与 "Unpermute" **分别融合成单个算子（fused operator）**，以减少 Kernel 启动次数与中间张量读写。
3. **启用开关**：提供两个等价命令行参数，**推荐使用** `--moe-permute-fusion`，也可用 `--use-fused-moe-token-permute-and-unpermute`。
4. **配套配置（避免性能劣化）**：
   - `--moe-token-dispatcher-type alltoall` → 必须设置 `--expert-tensor-parallel-size 1`；
   - `--moe-token-dispatcher-type alltoall_seq` → 必须开启 `--moe-tp-extend-ep`。
5. **调度器类型约束**：**仅支持** `alltoall` 与 `alltoall_seq` 两种；`allgather` **暂不支持**。
6. **专家容量参数兼容性**：启用 `--moe-expert-capacity-factor` 时，**必须同时开启** `--moe-pad-expert-input-to-capacity`；仅单独开启前者而不开启后者时，与融合算子**不兼容**。
7. **运行时基线要求**：环境需为 **CANN 8.3.RC1 / TorchNPU 7.2.RC1 及之后所有迭代版本**。

---

## 【关键机制与数据】

**MoE 调度器四步流水线（原文）：**
1. **Token 路由**：通过专家门控（gating mechanism）为每个 token 选择最合适的专家。
2. **数据重排（Permute）**：按所选专家对 token 分组，以便各专家并行处理——这是**性能瓶颈之一**，涉及大量数据移动，分布式训练中尤甚。
3. **专家处理**：每个专家并行处理属于它的 token。
4. **结果重组（Unpermute）**：将来自不同专家的结果还原回**原始 token 顺序**——同样因密集数据移动成为**性能瓶颈之一**。

**融合策略（原文）：**
- 解决思路为 "将 MoE Token Permute 和 Unpermute 操作**分别融合成一个算子**"，对应两个独立的融合 Kernel（一个处理 Permute，一个处理 Unpermute），并非把 Permute 和 Unpermute 合到一个 Kernel 里。
- 收益定性描述（原文）："**不仅能够有效节省内存资源，还能提升模型训练性能**"。
- 文档**未给出**任何量化数字（加速比、吞吐提升百分比、显存节省量、benchmark 场景等），故不臆造。

**依赖的更高层模块（原文）：** 调度器名为 `MoEAlltoAllTokenDispatcher`；三种调度器类型为 `alltoall`、`alltoall_seq`、`allgather`。

---

## 【表格解读】

**原文无表格**。

文档中没有出现任何 markdown 表格、参数对比表或性能对比表。所有信息以"命令/开关 + 短描述"和编号要点形式给出。

---

## 【公式解读】

**原文无公式**。

文档未给出任何数学公式、伪代码或 LaTeX 表达式。Permute/Unpermute 的语义仅以自然语言（"按选择的专家进行分组""将处理后的结果重新组合回原始的 token 顺序"）描述。

---

## 【关联】

- **核心上游模块**：`MoEAlltoAllTokenDispatcher`（MoE Token 调度器）——本文档的优化正是嵌入在其 Permute/Unpermute 子步骤中。
- **联动配置开关**（文档内已交叉引用）：
  - `--moe-token-dispatcher-type`：决定走哪条调度路径（`alltoall` / `alltoall_seq` / `allgather`，最后一种不支持）。
  - `--moe-expert-capacity-factor` 与 `--moe-pad-expert-input-to-capacity`：成对使用才能与融合算子兼容。
  - `--expert-tensor-parallel-size`：在 `alltoall` 模式下必须设为 `1`。
  - `--moe-tp-extend-ep`：在 `alltoall_seq` 模式下必须开启。
- **运行环境**：CANN（昇腾 CANN 算子库）与 TorchNPU 的**版本标识**是该融合算子可用的基线条件。
- **等价开关关系**：`--moe-permute-fusion` ⇔ `--use-fused-moe-token-permute-and-unpermute`（文档显式声明两者等价，并推荐前者）。
- 文档**未提供**文末内部链接，所涉及到的其他模块/特性需要通过上文开关名在仓库内交叉检索。

---

## 【使用方法】

**1. 启动脚本启用（二选一，等价，推荐前者）：**

```
--moe-permute-fusion
```
或
```
--use-fused-moe-token-permute-and-unpermute
```

**2. 推荐配套配置（避免性能劣化）：**

| 调度器类型 | 必须配套的开关 |
|---|---|
| `--moe-token-dispatcher-type alltoall` | `--expert-tensor-parallel-size 1` |
| `--moe-token-dispatcher-type alltoall_seq` | 开启 `--moe-tp-extend-ep` |

**3. 兼容性约束（原文）：**
- 调度器类型仅限 `alltoall` 与 `alltoall_seq`；`alltoall_seq` 与 `allgather` 中的 `allgather` **不支持**。
- 若启用 `--moe-expert-capacity-factor`，必须同时启用 `--moe-pad-expert-input-to-capacity`。
- 系统环境需为 **CANN 8.3.RC1 / TorchNPU 7.2.RC1 及之后迭代版本**。

> 文档未涉及 YAML/JSON 配置文件示例、API 调用方式或多卡启动模板，以上即为原文给出的全部启用信息。
