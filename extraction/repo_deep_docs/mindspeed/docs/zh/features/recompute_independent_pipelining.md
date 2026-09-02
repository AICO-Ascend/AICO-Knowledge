# 重计算流水线独立调度

> 仓 `mindspeed` · 路径 `docs/zh/features/recompute_independent_pipelining.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/recompute_independent_pipelining.md

# 重计算流水线独立调度 — 深度解读

---

## 【定位】

这篇文档描述 mindspeed 中将 **重计算（recomputation）从反向计算的依赖中解耦**，使其成为调度器主动管理的独立调度单元，从而在虚拟流水线并行（VPP）场景下同时优化 **显存峰值** 与 **训练性能** 的能力。

---

## 【技术要点】

1. **核心痛点（背景）**：传统流水线调度中，重计算由反向计算触发并与之绑定，必须等待下一个 stage 的梯度返回才能开始，但重计算本身并不需要该梯度 → 产生额外 bubble、性能下降。
2. **解耦机制（方案）**：修改调度器，把重计算提升为 **独立调度单元**（scheduler-driven），并基于 PyTorch 的 `saved_tensors_hooks` 实现新的重计算方法，使其可在反向计算之前的合适时机被主动触发或直接去除。
3. **场景一（未开启重计算）`--recompute-in-bubble`**：在虚拟流水线调度中利用 bubble 主动插入重计算，"以极小性能代价换取显存峰值降低"，需保留激活值的前向块数量减少到 **PP × VPP**（PP=流水线并行数，VPP=虚拟流水线并行数）。
4. **场景二（已开启重计算）`--recompute-in-advance`**：解除重计算与"后一个 stage 的反向计算"之间的依赖，从而提前重计算；同时 **去除模型最后一层的重计算**，实现性能提升。
5. **使用前提互斥**：`--recompute-in-bubble` 要求 `recompute_num_layers = None 或 0`（即未开启重计算）；`--recompute-in-advance` 要求 `recompute_num_layers ≠ None 且 ≠ 0`（即必须已开启重计算），且 **两个开关不可同时开启**。
6. **大量特性不兼容**（详见【使用方法】）：`--recompute-in-bubble` 与 `--recompute-in-advance` 各自与多种重计算变体（uniform / block / selective / adaptive）、通信重叠优化（`no-align-grad-reduce`、`no-overlap-p2p-communication`）、`swap-attention` 以及 MoE 场景下的两项重计算特性存在冲突。

---

## 【关键机制与数据】

**工作原理（数据流）：**

- 原机制：反向计算 → 触发重计算 → 重计算依赖下一 stage 的梯度回流，形成 **串行依赖链**，产生空闲 bubble。
- 新机制：调度器主动调度重计算单元 → 重计算不再等待反向梯度 → 可在 bubble 时间窗内被自由 **插入或剔除**。
- 底层实现依托 PyTorch 的 **`saved_tensors_hooks`**，在反向计算前合适的时机主动触发或去除部分重计算。

**关键性能/内存数据（原文唯一量化点）：**

> 原文：「将需要保留激活值的前向计算块的个数减少到 **PP × VPP**」

即：在 `--recompute-in-bubble` 模式下，原本需要在前向阶段常驻激活值的块数被压缩到与 **PP × VPP** 同量级，bubble 内的空闲时间被转化为"算力"用以重算历史激活值，从而降低峰值显存。

**两个调度对比图（图 1、图 2）**：原文仅给出 PNG 占位说明，分别对应"未开启重计算调度图"与"开启重计算调度图"，原文未给出图内时序细节数字。

---

## 【表格解读】

**原文无表格。**

（文档中仅有的两个图示为 PNG 时序图，未以表格形式给出参数或性能数据。）

---

## 【公式解读】

**原文无公式。**

（原文仅给出符号化文本 "PP × VPP"，未以数学公式形式呈现。）

---

## 【关联】

原文无内部链接。根据内容可识别出以下逻辑依赖关系：

- **上游/前置**：
  - 虚拟流水线并行（VPP）：两个开关 `--recompute-in-bubble` 与 `--recompute-in-advance` 均 **必须** 先开启 VPP。
  - 重计算功能本身：`--recompute-in-advance` 需要先开启重计算；`--recompute-in-bubble` 则不能开启。
- **平行/互斥特性**（原文 NOTE 中提及，本文需忠实列出冲突对象）：
  - 重计算变体：完全重计算 uniform、完全重计算 block、选择重计算、自适应选择重计算。
  - 通信/调度优化：`no-align-grad-reduce`、`no-overlap-p2p-communication`。
  - 显存优化：`swap-attention`。
  - MoE 相关：`--moe-adaptive-recompute-activation`、`--moe-layer-recompute`（仅与 `--recompute-in-bubble` 冲突）。
- **实现基础**：PyTorch 的 `saved_tensors_hooks` 是该新重计算方法的底层机制。

---

## 【使用方法】

**配置项（原文逐字保留）：**

- 开启 **利用 bubble 进行重计算** 功能：
  ```
  --recompute-in-bubble
  ```
  约束：
  - 必须开启虚拟流水线并行特性；
  - 使用前 **不能** 开启重计算；
  - `recompute_num_layers` 参数需为 `None` 或 `0`。

- 开启 **提前重计算 + 去除不必要重计算** 功能：
  ```
  --recompute-in-advance
  ```
  约束：
  - 必须开启虚拟流水线并行特性；
  - 使用前 **需要** 开启重计算；
  - 不支持 `recompute_method = uniform`；
  - `recompute_num_layers` 不能为 `None` 或 `0`；
  - 与 `--recompute-in-bubble` **不可同时开启**。

**不兼容项速查（原文 NOTE 直引）：**

- `--recompute-in-bubble` 暂不兼容：完全重计算 uniform、完全重计算 block、选择重计算、自适应选择重计算、`swap-attention`、`no-align-grad-reduce`、`no-overlap-p2p-communication`；MoE 场景下另不兼容 `--moe-adaptive-recompute-activation`、`--moe-layer-recompute`。
- `--recompute-in-advance` 暂不兼容：完全重计算 uniform、选择重计算、自适应选择重计算、`no-align-grad-reduce`、`no-overlap-p2p-communication`。
