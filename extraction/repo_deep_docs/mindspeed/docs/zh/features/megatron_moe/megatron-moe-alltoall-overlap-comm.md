# Megatron MoE alltoall dispatcher分支通信隐藏优化

> 仓 `mindspeed` · 路径 `docs/zh/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md

# Megatron MoE alltoall dispatcher 分支通信隐藏优化 — 一体化深度解读

## 【定位】
本文档介绍 mindspeed 中针对 Megatron MoE 训练场景，通过 **异步通信与子图切分** 实现 Expert Parallel (EP) 通信与计算的互相掩盖（overlap），从而提升 MoE 模型端到端训练性能的优化特性，并说明该特性在 `alltoall` 与 `alltoall_seq` 两种 dispatcher 分支下各自的启用方式。

---

## 【技术要点】

1. **问题域**：MoE 训练中存在大量 EP（Expert Parallel）通信未被隐藏，端到端耗时占比大。
2. **核心思路**：让通信与计算交替进行（通算并行），以减少空闲等待。
3. **前向实现**：在前向过程中使用**异步通信**，尽可能与计算互相掩盖。
4. **反向实现**：对整个计算流程做**子图切分**，使反向过程中也能实现通算并行。
5. **双分支支持**：同时支持 `alltoall` 与 `alltoall_seq` 两种 dispatcher，针对两者做了**针对性优化**（即两组不同的开关组合）。
6. **共享专家兼容**：在 `alltoall` 分支上兼容 Megatron 原生的 `moe-shared-expert-overlap` 方案，并以更细粒度的掩盖获得进一步性能提升。
7. **性能收益**：相较基准 dispatcher 提升 **10%+**；在开启 `--moe-shared-expert-overlap` 后仍可再提升 **4%+**；但会**导致显存占用增加**，建议搭配 ZeroMemory 使用。

---

## 【关键机制与数据】

### 工作原理（原文）

- **前向**：使用**异步通信**与计算交替进行，互相掩盖。
- **反向**：对整个计算流程进行**子图切分**，在反向阶段也实现通算并行。
- **alltoall 分支兼容**：在与 `--moe-shared-expert-overlap` 共存时，通过**更细粒度**的掩盖实现较原生方案的性能进一步提升。

### 数据/性能（原文）

| 场景 | 性能提升（原文） |
|---|---|
| 基准 dispatcher（megatron-moe dropless 分支） | 性能可提升 **10%+** |
| 同时开启 `--moe-shared-expert-overlap` | 仍可提高 **4% 以上** |
| 显存代价 | 启动该特性会导致**显存占用增加**（原文描述为正常现象） |

### 适用场景（原文）
- 适用对象：`megatron-moe`、**dropless 方案分支**。
- 适用动机：**需要提高训练性能**的场景。

---

## 【表格解读】

**原文无表格**。

（文档以分条目（列表 / 命令）形式罗列开关与说明，未出现参数表或性能对比表。）

---

## 【公式解读】

**原文无公式**。

（文档以自然语言描述机制与开关，未给出任何数学公式或伪代码算式。）

---

## 【关联】

### 1. 内部链接 — ZeroMemory（`megatron-moe-zero-memory.md`）
文档文末明确提供链接：

> ZeroMemory介绍及设置可参考 [ZeroMemory文档](megatron-moe-zero-memory.md)。

**关系**：本特性启用后会**增加显存占用**，ZeroMemory 是用来**回收/调整显存**的搭配方案，二者构成"性能优化 + 显存回收"的组合关系。原文将 ZeroMemory 作为显存增大的应对手段给出。

### 2. 与 `moe-shared-expert-overlap` 的关系
- 在 `alltoall` 分支上**兼容** Megatron 原生的 `moe-shared-expert-overlap` 方案；
- 通过更细粒度的掩盖，使性能**较原生方案进一步提升 4%+**（性能基线为"已开启 `--moe-shared-expert-overlap` 的原生方案"）。

### 3. 与 dispatcher 类型的分支关系
- **互斥分支**：`alltoall` 分支与 `alltoall_seq` 分支为二选一关系，对应不同的 `--moe-token-dispatcher-type`。
- **互斥开关**：`--moe-tp-extend-ep` 仅在 `alltoall_seq` 分支可用，`alltoall` 分支不支持；原文给出明确切换建议：「如使用该特性，请切换为 `alltoall_seq`」。

### 4. 与 `moe-grouped-gemm` 的关系
两个分支均要求同时开启 `--moe-grouped-gemm`，且**目前仅支持 Grouped MLP**，体现本特性对计算后端的强依赖。

### 5. 与 `moe-permutation-async-comm` 的关系
仅在 `alltoall_seq` 分支需额外开启 `--moe-permutation-async-comm`，可视为该分支的前置依赖开关。

---

## 【使用方法】

### 总开关
```
--moe-alltoall-overlap-comm
```

### 分支 A：`alltoall_seq` 分支
需同时开启以下开关：
- `--moe-permutation-async-comm`
- `--moe-token-dispatcher-type alltoall_seq`
- `--moe-grouped-gemm`（目前仅支持 **Grouped MLP**）

当 **tp > 1** 时，**还需同时开启**：
- `--moe-tp-extend-ep`

### 分支 B：`alltoall` 分支
需同时开启：
- `--moe-token-dispatcher-type alltoall`
- `--moe-grouped-gemm`（目前仅支持 **Grouped MLP**）
- **不支持开启** `--moe-tp-extend-ep`；如需使用该特性，请切换为 `alltoall_seq` 分支。

### 显存管理建议
启用本特性后显存占用会增加（原文标注为正常现象），可搭配 **ZeroMemory** 特性调整显存使用状况；ZeroMemory 的具体介绍与设置见文档文末链接 [`megatron-moe-zero-memory.md`](megatron-moe-zero-memory.md)。
