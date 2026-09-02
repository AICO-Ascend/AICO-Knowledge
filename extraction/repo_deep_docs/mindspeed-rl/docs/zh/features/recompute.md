# Megatron 重计算

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/recompute.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/recompute.md

# Megatron 重计算 — 一体化深度解读

---

## 【定位】

这篇文档描述了 Megatron 框架中**重计算（Recomputation）**这一显存优化特性，针对大模型训练中前向激活值随深度线性增长、挤占硬件内存的痛点，通过在反向传播时按需重新计算激活来缩短激活生命周期、降低显存占用，并给出了选择性重计算与完全重计算两条路径的参数化启用方式。

---

## 【技术要点】

1. **核心思路**：前向传播与损失计算阶段即时释放不再需要的激活值显存，反向传播时按需重新计算，缩短激活生命周期，降低对硬件内存的压力。
2. **选择性重计算（推荐）**：仅对 Transformer 架构内的 `core_attention` 组件执行激活重计算——保留重计算成本高但显存占用小的激活，仅释放并重算"显存占用大、重算成本低"的激活。
3. **完全重计算**：除输入数据外，所有激活值在需要时重新计算，适用于显存极度受限场景。
4. **两种重计算方案（`recompute_method`）**：
   - `uniform`：将 Transformer 层**均匀分组**（每组大小为 `recompute_num_layers`），按组存储输入与激活。
   - `block`：仅对前 `recompute_num_layers` 个 Transformer 层做重计算，剩余层不做重计算。
5. **参数优先级冲突**：当同时配置 `recompute_activations` 与 `recompute_granularity full` 时，**生效的是选择性重计算**（而非完全重计算）。
6. **与流水并行的耦合**：当脚本同时配置 `recompute_method block`、`recompute_granularity full`、`num_layers_per_virtual_pipeline_stage N` 时，可用 `recompute_num_layers N` 控制每个 vpp stage 的重计算层数；参数 `enable_recompute_layers_per_pp_rank` 可改写该语义，使其**无视 vpp、按每个 pp stage 配置重计算层数**。
7. **legacy 分支限制**：在 legacy 分支下，开启 `use_flash_attn` 将**无法使用**选择性重计算。

---

## 【关键机制与数据】

- **工作原理（原文）**：前向传播与损失函数计算阶段，即时释放不再需要的激活值内存空间；反向传播时按需重新计算激活值。"激活值保存数量随模型深度线性增长"——这是触发重计算的根本动因。
- **数据流（原文）**：
  - **传统路径**：前向 → 全部激活缓存在显存 → 反向读取 → 计算梯度。
  - **重计算路径**：前向 → 释放可重算激活 → 反向需要时**重算** → 计算梯度。
- **策略分支（原文）**：
  - 选择性重计算 → 锁定 `core_attention` 范围，保留"小显存/高重算成本"激活、重算"大显存/低重算成本"激活。
  - 完全重计算 → 除输入外全量重算，**最大限度减少对内存的依赖**。
- **性能代价（原文）**：重计算会带来**额外的计算成本，降低性能**；因此需在"内存占用"与"计算吞吐"之间综合权衡。
- **虚拟流水并行（vpp）耦合（原文）**：与 `num_layers_per_virtual_pipeline_stage N`、`recompute_num_layers N` 联动时可按 vpp stage 粒度细控；`enable_recompute_layers_per_pp_rank` 提供"无视 vpp、按 pp stage 配置"的语义开关。

> 说明：原文未给出具体的数值性能数据（如显存节省百分比、吞吐损失比例），此处严格不补全。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

本文是 Megatron 训练栈内独立的显存优化特性文档，与以下特性/模块存在耦合关系（均为原文正文提及的关联项）：

| 关联项 | 关系性质 | 说明 |
|---|---|---|
| **`core_attention`** | 作用对象 | 选择性重计算**只针对**该组件执行激活重计算 |
| **Transformer 层** | 分组单元 | `uniform`/`block` 两种方案都以 Transformer 层为基本计数单位 |
| **流水并行（pp / virtual pipeline, vpp）** | 作用域配置 | `num_layers_per_virtual_pipeline_stage` + `recompute_num_layers` + `enable_recompute_layers_per_pp_rank` 三者联动决定重计算层在 pp/vpp 维度的分配语义 |
| **Flash Attention（`use_flash_attn`）** | 互斥约束 | legacy 分支下开启 `use_flash_attn` 将**无法使用**选择性重计算 |
| **legacy 分支** | 代码分支 | 选择性重计算的可用性受其约束 |

文末内部链接信息标注为「(无)」。

---

## 【使用方法】

**配置项 / 命令（原文逐字保留）：**

| 配置项 | 取值 / 命令 | 含义 |
|---|---|---|
| `recompute_activations` | 标志位（注释：开启选择性重计算） | 开启**选择性**重计算 |
| `recompute_granularity` | `full`（注释：开启完全重计算） | 开启**完全**重计算 |
| `recompute_method` | `uniform` \| `block`（任选其一） | 重计算方案选择 |
| `recompute_num_layers` | 整数 N | `uniform` 下为每组层数；`block` 下为前缀重计算层数；在与 `num_layers_per_virtual_pipeline_stage N` 联用时也表示每个 vpp stage 的重计算层数 |
| `num_layers_per_virtual_pipeline_stage` | 整数 N | 虚拟流水并行下每 stage 的层数 |
| `enable_recompute_layers_per_pp_rank` | 标志位 | 改写 `recompute_num_layers N` 的语义：**无视 vpp、按 pp stage 配置**重计算层数 |
| `use_flash_attn` | 标志位 | legacy 分支下，开启此标志**禁用**选择性重计算 |

**生效优先级（原文）：**
- 同时配置 `recompute_activations` 与 `recompute_granularity full` → **生效的是选择性重计算**。
- 同时配置 `recompute_method block` + `recompute_granularity full` + `num_layers_per_virtual_pipeline_stage N` → `recompute_num_layers N` 控制每个 vpp stage 的重计算层数；可通过 `enable_recompute_layers_per_pp_rank` 切换语义为"按 pp stage"。

**使用影响（原文）：**
- 降低对内存的需求。
- 带来额外计算成本、降低性能 → 需综合考虑内存占用与吞吐进行配置权衡。
