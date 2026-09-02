# Megatron 分布式权重

> 仓 `mindspeed` · 路径 `docs/zh/features/dist_ckpt.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/dist_ckpt.md

# Megatron 分布式权重 —— 一体化深度解读

## 【定位】

这篇文档描述了 mindspeed 中"完全分片权重"方案（即 `--ckpt-format torch_dist`）的能力，用于在大模型训练中以**零通信开销（相对分布式优化器）+ 零数据冗余（相对传统 `torch` 格式）**的方式完成权重与优化器状态的保存与加载。

---

## 【技术要点】

1. **问题根源（`--ckpt-format torch`）**：每张卡持有完整的优化器状态，保存时全部写入磁盘，存在数据冗余。
2. **已有折中（分布式优化器）**：通过分片持有优化器状态降低运行内存与磁盘占用，但**保存阶段引入 All-Gather、加载阶段引入 Scatter**，带来额外通信开销。
3. **完全分片方案（`torch_dist`）**：模型参数与优化器状态均做**完全分片**，每张卡仅保存/加载各自的分片数据，**消去了保存阶段的 All-Gather 与加载阶段的 Scatter**。
4. **并行维度覆盖**：支持 **TP、PP、CP、EP、VPP** 五种并行配置，以及 Megatron 原生特性启用场景；**暂未适配 MindSpeed 特性启用场景**。
5. **CP 限制**：在 CP 场景下，`--ckpt-format torch_dist` 目前仅支持 `--context-parallel-algo` 为 `megatron_cp_algo`。
6. **格式自识别**：通过 `--auto-detect-ckpt-format` 可选参数，使加载端自动判断待加载权重属于 `torch_dist` 还是 `torch` 格式。

---

## 【关键机制与数据】

**对比维度（原文叙述的相对关系，非具体数值）：**

| 对比对象 | 数据冗余 | 保存阶段通信 | 加载阶段通信 | 磁盘占用 |
|---|---|---|---|---|
| `torch`（传统） | 有（每卡全量优化器状态） | 无 All-Gather | 无 Scatter | 大 |
| 分布式优化器 | 无（分片持有） | **有 All-Gather** | **有 Scatter** | 小 |
| `torch_dist`（本文方案） | 无（完全分片） | **无 All-Gather** | **无 Scatter** | 小 |

- **工作原理（原文）**：在保存阶段，每张卡仅将自己持有的模型参数与优化器状态分片写入磁盘；在加载阶段，每张卡仅从磁盘读取属于自己的分片并装入本地，无需做集合通信重组。
- **性能数据**：原文**未给出**具体的内存、磁盘、通信量、加速比等量化数字，仅以定性方式描述"节省磁盘空间""省去通信操作"。
- **数据流概述（依据原文推导）**：`torch_dist` 模式下，rank × 维度（TP/PP/CP/EP/VPP）共同决定分片粒度 → 每张卡只持久化自己拥有的那一片 → 加载时按相同 `--ckpt-format` 与（可选）`--auto-detect-ckpt-format` 读回本地分片。

---

## 【表格解读】

**原文无表格。**（文末 NOTE 区以三条项目符号呈现限制说明，未形成结构化表格；其内容已在【使用方法】的 NOTE 块中逐字保留并解读。）

---

## 【公式解读】

**原文无公式。**（文档为方案说明型，未涉及任何数学表达式或 LaTeX/伪代码形式的公式。）

---

## 【关联】

- **上游对比方案**：与 `--ckpt-format torch`（传统全量权重）以及 Megatron 的"分布式优化器（distrib optimizer）"构成三种权重保存/加载策略的对比三角，本文方案定位为两者的折中改进。
- **依赖的并行特性**：TP、PP、CP、EP、VPP 五种并行配置，是该特性得以"完全分片"生效的基础维度；其中 CP 还受 `--context-parallel-algo megatron_cp_algo` 约束。
- **互斥范围（原文）**：**暂未适配 MindSpeed 特性启用场景**，即在 MindSpeed 自有特性叠加使用时，`torch_dist` 不保证兼容。
- **加载端格式自识别**：通过 `--auto-detect-ckpt-format` 与 `--ckpt-format` 配合，实现在同一脚本中混载 `torch` 与 `torch_dist` 历史权重的兼容能力（属于加载侧的桥接特性）。
- **Megatron 原生特性**：文档明确支持 Megatron 原生特性的启用场景，意味着该方案与 Megatron 生态的标准 ckpt 流程对齐，而非 mindspeed 私有改造。
- **内部链接**：本文档**未提供**任何内部链接（文末"内部链接: (无)"），因此无法从文档内部追溯到具体上下游模块路径。

---

## 【使用方法】

**启用分布式权重保存**：
```
--ckpt-format torch_dist
--save 权重保存路径
```

**启用加载端自动格式检测（可选）**：
```
--ckpt-format torch_dist
--load 权重加载路径
--auto-detect-ckpt-format
```

**约束与注意（原文 NOTE 原文摘录要点）**：
- 加载 `torch_dist` 格式权重时，**必须**指定与之相同的 `--ckpt-format torch_dist`。
- `--ckpt-format torch_dist` **暂未适配 MindSpeed 特性启用场景**。
- 在 CP 场景下，`--ckpt-format torch_dist` 目前**仅支持** `--context-parallel-algo` 为 `megatron_cp_algo`。

**未涉及的内容（原文）**：原文未给出具体的性能数字、未提供配置项的完整枚举表，也未涉及具体的安装/编译/环境变量启用方式。
