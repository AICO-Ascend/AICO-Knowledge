# Megatron 自定义流水线布局

> 仓 `mindspeed` · 路径 `docs/zh/features/pipeline-model-parallel-layout.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/pipeline-model-parallel-layout.md

# Megatron 自定义流水线布局 — 一体化深度解读

---

## 【定位】

本文档描述 MindSpeed 通过 `--pipeline-model-parallel-layout` 参数解决 Megatron 默认均匀切分 PP/VPP stage 时遇到的负载不均衡问题，使 embedding、decoder、MTP、loss 等不同层可显式按计算负载分配到各流水 stage 上。

---

## 【技术要点】

1. **核心能力**：以单字符串参数 `--pipeline-model-parallel-layout` 显式指定每个 PP/VPP stage 持有的层类型与数量，覆盖默认按 decoder 层数均匀切分的方式。
2. **层字符约定**：使用 `E`（embedding 层）、`t`（transformer decoder 层）、`m`（MTP 层）、`L`（loss 层）四个字符描述 layout。
3. **字符串语法**：`|` 划分 stage；`,` 仅为可读性分隔，解析时被忽略；`x*N` 表示单字符重复（如 `t*3` ≡ `ttt`）；`(pattern)*N` 表示段重复（如 `(tt|)*2` ≡ `tt|tt|`）；连续 `||` 表示空 stage（与 `--moe-fb-overlap` 同时开启时不支持空 decoder chunk）。
4. **VPP 自动推导**：layout 中 stage 数量除以 `--pipeline-model-parallel-size` 自动得到 VPP size；纯 PP 场景下 stage 数应等于 PP size。
5. **典型数值校验**：原文示例 decoder 层总数满足 `2 + 2 + 3 + 1 = 8`（与 `--num-layers 8` 一致），MTP 层数 1（与 `--mtp-num-layers 1` 一致），embedding 与 loss 各出现一次。
6. **MoE 协同**：与 `--moe-fb-overlap` 共同启用时使用 layout-aware VPP 调度，按 forward/backward chunk 实际 layer graph 数执行 overlap，层数不等时先配对再处理剩余层；仍受 `--moe-fb-overlap` 原有约束（`alltoall` dispatcher、`--moe-grouped-gemm`、`--expert-tensor-parallel-size=1`、`--expert-model-parallel-size > 1`）。

---

## 【关键机制与数据】

**工作原理**（原文）：

- Layout 字符串从前向计算顺序展开：先列出 VPP rank 0 上所有 PP stage，再列出 VPP rank 1，以此类推。
- VPP size 通过 `layout stage 数 ÷ PP size` 自动推导。
- 与 `--moe-fb-overlap` 同时使用时，前反向 overlap 按当前 forward chunk 与 backward chunk 的实际 layer graph 数量执行；当两侧层数不一致时，先对可配对的层执行 overlap，再处理剩余层。
- MoE 跨 microbatch 前反向通信掩盖（`--moe-fb-overlap`）在受限场景下可与自定义 layout 配合使用。

**性能数据**：原文未涉及具体吞吐、空泡率或 profiling 数值。

---

## 【表格解读】

### 表格 1：层类型字符含义表（逐字还原）

| 字符 | 含义 |
| --- | --- |
| `E` | embedding 层 |
| `t` | transformer decoder 层 |
| `m` | MTP 层 |
| `L` | loss 层 |

**逐行解读**：

- **`E` → embedding 层**：表示流水 stage 持有 embedding 计算，原文指出在含 embedding/loss 的模型中均匀切分会使首尾 stage 承担额外计算，layout 允许显式将其放到指定 stage。
- **`t` → transformer decoder 层**：表示标准 transformer 解码器层，是常规 dense 模型默认均匀切分的主体；layout 中 `t` 的总数受 `--num-layers` 约束。
- **`m` → MTP 层**：表示 Multi-Token Prediction 层，原文强调使用 MTP 时必须放在 decoder 层之后（约束 4：decoder 层必须放在 MTP 层之前），且 `m` 的数量必须与 `--mtp-num-layers` 一致。
- **`L` → loss 层**：表示 loss 计算，layout 中必须且只能出现一次（约束 2），可与 `E` 共同出现在首尾 stage。

### 表格 2：PP/VPP stage 分布示例（逐字还原，layout `Ett|tt|ttt|tmL`，PP=2，VPP=2）

| PP rank | VPP rank 0 | VPP rank 1 |
| --- | --- | --- |
| 0 | `Ett` | `ttt` |
| 1 | `tt` | `tmL` |

**逐行解读**：

- **PP rank 0 / VPP rank 0 = `Ett`**：第 0 个流水 rank 在第一个 VPP chunk 同时持有 embedding 和 2 个 decoder 层，承担前向计算起点与额外 embedding 开销。
- **PP rank 0 / VPP rank 1 = `ttt`**：同一 PP rank 的第二个 VPP chunk 持有 3 个 decoder 层，与 rank 0 的 VPP rank 0 形成非均匀 chunk（2 层 vs 3 层），演示"同一 PP rank 上不同 VPP chunk 持有不同数量 decoder 层"的能力。
- **PP rank 1 / VPP rank 0 = `tt`**：第 1 个流水 rank 的第一个 chunk 仅持有 2 个 decoder 层，无额外结构层。
- **PP rank 1 / VPP rank 1 = `tmL`**：第 1 个流水 rank 的第二个 chunk 持有 1 个 decoder 层、1 个 MTP 层和 loss 层，承担 MTP 与 loss 计算——这正是原文所述"开启 MTP 或将 embedding、loss 计算纳入流水 stage 时，首尾 stage 可能承担额外计算"的典型布局。

---

## 【公式解读】

**原文无公式**（`x*N`、`(pattern)*N` 等属于 layout 字符串的语法约定，而非数学公式；`2 + 2 + 3 + 1 = 8` 为层数校验的算术关系，已在【技术要点】中说明）。

---

## 【关联】

本特性与以下 MindSpeed/Megatron 机制存在耦合或互斥关系：

- **互补/协同**：
  - `--moe-fb-overlap`：MoE 跨 microbatch 前反向通信掩盖，原文明确支持二者联合启用并提供 layout-aware VPP 调度。
  - MoE 配置族：`--expert-model-parallel-size`、`--expert-tensor-parallel-size`、`--num-experts`、`--moe-grouped-gemm`、`--moe-token-dispatcher-type alltoall`（典型 MoE 组合的组成部分）。
  - `--mtp-num-layers`：layout 中 `m` 字符数量必须与该参数一致。

- **互斥/不可同时使用**（原文约束 6–10）：
  - `--num-layers-per-virtual-pipeline-stage`：仅依靠该参数无法表达每个 stage 的层类型与具体层数，是本文要替代的能力。
  - `--num-virtual-stages-per-pipeline-rank`：VPP 由 layout 自动推导，二者冲突。
  - `--pipeline-num-transformer-layers`、`--noop-layers`、`--schedules-method dualpipev`：当前调度或层数配置与自定义 layout 不兼容。
  - `--recompute-in-bubble`、`--recompute-in-advance`：当前不支持与自定义 layout 同时启用。
  - `--optimize-send-recv-comm`：仅在 layout 推导出 VPP 时不可同时使用，纯 PP 场景未限制。
  - `--noop-layers + --pipeline-model-parallel-layout + --moe-fb-overlap`：三者组合暂不支持。

- **替代关系**：本特性被视为对 `--num-layers-per-virtual-pipeline-stage` 的能力扩展——后者仅支持均匀切分，前者支持显式层类型与非均匀 chunk 切分。

- **上游背景**：基于 Megatron 的 PP（Pipeline Parallelism）与 VPP（Virtual Pipeline Parallelism），本文档定位为 Megatron 默认均匀切分方案的 MindSpeed 增强层。

---

## 【使用方法】

### 启用方式

在启动脚本中添加 `--pipeline-model-parallel-layout` 参数即可启用该特性。

### 配置示例 1：PP=2 + VPP 自动推导（decoder=8，MTP=1）

```shell
--pipeline-model-parallel-size 2
--pipeline-model-parallel-layout Ett|tt|ttt|tmL
--num-layers 8
--mtp-num-layers 1
```

stage 总数 4，`4 / PP=2` 自动推导 `VPP=2`；decoder 层总数 `2+2+3+1=8`，MTP 层数 1，embedding 与 loss 各出现一次。

### 配置示例 2：纯 PP（PP=2，无 VPP）

```shell
--pipeline-model-parallel-size 2
--pipeline-model-parallel-layout Etttt|ttttL
--num-layers 8
```

layout 的 stage 数量等于 `--pipeline-model-parallel-size`。

### 配置示例 3：与 `--moe-fb-overlap` 联合启用（典型 MoE）

```shell
--pipeline-model-parallel-size 2
--pipeline-model-parallel-layout Ett|tt|ttt|tmL
--num-layers 8
--mtp-num-layers 1
--expert-model-parallel-size 2
--expert-tensor-parallel-size 1
--num-experts 8
--moe-grouped-gemm
--moe-token-dispatcher-type alltoall
--moe-fb-overlap
```

需同时满足 `--moe-fb-overlap` 原有约束：`alltoall` dispatcher、开启 `--moe-grouped-gemm`、`--expert-tensor-parallel-size=1` 且 `--expert-model-parallel-size > 1`。

### 核心约束（10 条）

1. layout 中 stage 数量必须能被 `--pipeline-model-parallel-size` 整除。
2. layout 中必须且只能包含一个 `E`（embedding）和一个 `L`（loss）。
3. layout 中 decoder 层（`t`）数量必须与 `--num-layers` 一致。
4. 若使用 MTP，`m` 数量必须与 `--mtp-num-layers` 一致，且 `t` 必须放在 `m` 之前。
5. 当前暂不支持 encoder 层。
6. 不能与 `--num-layers-per-virtual-pipeline-stage`、`--num-virtual-stages-per-pipeline-rank` 同时配置。
7. 不能与 `--pipeline-num-transformer-layers`、`--noop-layers`、`--schedules-method dualpipev` 同时使用。
8. 不支持与 `--recompute-in-bubble` 或 `--recompute-in-advance` 同时使用。
9. 当 layout 推导出 VPP 时，不支持与 `--optimize-send-recv-comm` 同时使用。
10. 与 `--moe-fb-overlap` 同时使用时，不支持空 decoder chunk，也不支持 `--noop-layers + --pipeline-model-parallel-layout + --moe-fb-overlap` 三者组合。
