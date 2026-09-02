# Megatron MoE alltoall dispatcher分支内存优化

> 仓 `mindspeed` · 路径 `docs/zh/features/megatron_moe/megatron-moe-zero-memory.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-zero-memory.md

# Megatron MoE alltoall dispatcher 分支内存优化 · 一体化解读

## 【定位】

本文档描述 Megatron MoE 在 `alltoall` / `alltoall_seq` dispatcher 分支下, 针对 MoE 动态内存大且开启 overlap 后进一步膨胀的"内存墙"问题, 提供基于"细粒度重计算 + 重通信 + 针对性 swap" 的零内存优化能力 (`--moe-zero-memory`)。

## 【技术要点】

1. **问题驱动**: MoE 动态内存本已偏大, 启用 overlap 策略后动态内存继续抬升, 内存墙问题突出; 此时普通整段重计算粒度过粗, 会带来显著性能回退。
2. **三手段合一**: 在 `alltoall` / `alltoall_seq` dispatcher 分支下, 通过"重通信 + 细粒度重计算 + 针对性 swap"组合进行内存节省, 并用计算掩盖重通信与 swap, 把重计算与未掩盖的通信隐藏起来。
3. **两级粒度**:
   - `level0` —— 在专家计算部分做重计算, 性能损失较小;
   - `level1` —— 更大粒度的重计算, 相对 `level0` 性能损失更高, 但内存收益更大。
4. **内存收益量级 (原文给出的相对值)**:
   - `level0` 节省的内存 ≈ MLP 重计算可节省内存的 **70%+**;
   - `level1` 节省的内存 ≈ MLP 重计算可节省内存的 **90%+**;
   - 两级方案的速度均优于直接做 MLP 重计算。
5. **`alltoall` 分支专属优化**: 在 `alltoall` 分支中, 将 `probs` 的重计算前移, 进一步放大内存节约效果。
6. **共享专家范围**: 上述"MLP"涵盖**共享专家部分** (不仅仅是路由专家)。

## 【关键机制与数据】

1. **工作原理**:
   - 该方案不是单一手段, 而是把"重通信、细粒度重计算、针对性 swap"三类手段串联在 `alltoall` / `alltoall_seq` dispatcher 分支中。
   - 关键思路是用**计算掩盖重通信和 swap**, 同时把**重计算与未掩盖的通信进行隐藏**, 从而在节省内存的同时尽量不损失吞吐。
   - `level0` 把重计算落在专家计算内部, 粒度更细; `level1` 在此基础上把重计算范围扩大, 以牺牲更多性能为代价换取更高内存节省。

2. **数据流侧的两个关键点 (原文)**:
   - 在 `alltoall` 分支中, 显式做了 **`probs` 重计算的前移**, 让 probs 相关中间态更早被回收 / 重建, 提升内存峰值削减效果。
   - "MLP" 的重计算口径**包含共享专家部分**, 因此优化对象覆盖到共享专家 MLP。

3. **性能 / 内存数据 (原文)**:
   - 原文: 内存收益相对值为 `level0` ≥ MLP 重计算的 **70%+**; `level1` ≥ MLP 重计算的 **90%+**; 速度"相比重计算 MLP 性能更优"。
   - 原文未给出绝对显存数值、绝对吞吐数值或具体 benchmark 数字, 也未给出与 `--moe-alltoall-overlap-comm` 单独 vs `--moe-fb-overlap` 组合下的对比数据, 故不杜撰。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **依赖的 overlap 特性**: 必须与 `--moe-alltoall-overlap-comm` 或 `--moe-fb-overlap` 同时开启才能使用 `--moe-zero-memory`。
  - `--moe-fb-overlap` 路径下的具体注意事项 (尤其是 `level1` 与 `--moe-zero-memory-num-layers` 的兼容性) 见文末内部链接:
    - [Megatron MoE 跨 microbatch 间 A2A 通信掩盖](megatron-moe-fb-overlap.md)
- **dispatcher 维度**: 仅在 `alltoall` 与 `alltoall_seq` dispatcher 上启用; 其中 `probs` 重计算前移是 `alltoall` 分支特有的内存优化点。
- **覆盖范围**: 优化对象包含**路由专家 MLP** 与**共享专家 MLP**; 不局限于其中之一。
- **替代关系**: 该特性是相对于"普通重计算 MLP" 的更优替代 —— 内存节省相当或更高 (`level1` 接近 MLP 重计算收益的 90%+), 且速度更优。

## 【使用方法】

1. **启用开关**:
   - `--moe-zero-memory level0` 或 `--moe-zero-memory level1`

2. **必须同时开启的依赖项**:
   - `--moe-alltoall-overlap-comm` 或 `--moe-fb-overlap` (二选一)。

3. **层数配置**:
   - `--moe-zero-memory level0`: 原文: "因为性能损失较小, 不支持配置层数, 功能为所有层使能"。
   - `--moe-zero-memory level1`: 默认为所有层使能; 也可配置 `--moe-zero-memory-num-layers x`, 其中 `x ≥ 0` 且 `x ≤ num_layers // pp`。

4. **适用场景约束 (原文)**:
   - ① 当前支持 `alltoall`、`alltoall_seq` dispatcher 模式, 适用于 megatron-moe 需要重计算的通用场景;
   - ② 在 `--moe-fb-overlap` 状态下**支持 `level0`**;
   - ③ 在 `--moe-fb-overlap` 状态下**不支持** `--moe-zero-memory-num-layers` 配置 (即层数参数在 `--moe-fb-overlap` 路径下不可用)。

5. **与 `megatron-moe-fb-overlap.md` 的衔接**: 在 `--moe-fb-overlap` 下使用本特性的具体注意事项, 请参照文末链接 [Megatron MoE 跨 microbatch 间 A2A 通信掩盖](megatron-moe-fb-overlap.md)。
