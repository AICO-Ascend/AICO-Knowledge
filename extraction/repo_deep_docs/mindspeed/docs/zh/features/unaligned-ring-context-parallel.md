# 非对齐Ring长序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/unaligned-ring-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/unaligned-ring-context-parallel.md

# 非对齐 Ring 长序列并行 — 一体化深度解读

## 【定位】

本文档描述了 mindspeed 中"非对齐 Ring 长序列并行"特性，旨在解决传统 Ring Attention/Context Parallel 要求序列长度必须被 CP size 整除的硬约束，使序列并行能够兼容动态、不规则、不可整除的输入序列（如多模态、流式数据、个性化推荐等场景）。

---

## 【技术要点】

1. **核心约束突破**：传统 Ring 序列并行要求 `sequence length % CP size == 0`；本特性解除该约束，允许每个 rank 持有非均匀的子序列长度。
2. **形状协商协议 (shape negotiation protocol)**：通信前先在 rank 之间交换"有效长度 (effective length)"信息，避免错位传输。
3. **变化隔离函数 `get_unaligned_cp_shapes`**：在分块计算与通信之前调用，根据当前 `block_id` 与目标 `next_block_id` 取出当前 rank 与目标 rank 的子序列长度。
4. **API 入口**：通过 `ringattn_context_parallel` 接口新增的 `shapes` 参数传入切分信息；`shapes` 为通用索引结构，支持 list / tuple / dict（如 `[100, 100, 20]`、`(100, 100, 20)`、`{0: 100, 1: 100, 2: 20}`）。
5. **返回值结构**：函数返回长度为 2 的列表 `[shapes[block_id], shapes[next_block_id]]`，对应"当前 rank 长度"与"目标 rank 长度"。
6. **运行范围限制**：当前仅支持 `--attention-mask-type=general` 的场景。

---

## 【关键机制与数据】

**工作原理（原文描述还原）：**

1. 启动阶段：调用方先准备每个 rank 的非均匀切分长度集合 `shapes`，作为本次非对齐 Ring 计算的协商基础。
2. 协商阶段（原文："通信前先交换有效长度信息"）：在进入 Ring Attention 的分块计算与通信流程前，参与 CP 通信的 rank 之间交换各自持有的有效子序列长度。
3. 隔离变化（原文："通过 `get_unaligned_cp_shapes` 隔离变化"）：用 `get_unaligned_cp_shapes(shapes, block_id, next_block_id)` 取出本轮计算所需的两个关键尺寸——`shapes[block_id]`（当前 rank 的子序列长度）与 `shapes[next_block_id]`（目标/下一 block 对应的子序列长度）。
4. 计算与通信阶段：基于上述两个长度完成本 block 的 Attention 计算以及与 `next_block_id` 的 KV 传输/交换，在分块计算和通信时传递非均匀的序列，从而实现"非均匀切分的 RingAttention 计算"。
5. 终止阶段：各 rank 完成本轮 block 计算后继续按 Ring 拓扑流转下一 block，直到所有 block 处理完毕。

**数据流（从原文提取的接口形态）：**

```
调用方准备 shapes
      │
      ▼
ringattn_context_parallel(q, k, v, head_num, cp_para, softmax_scale,
                          attn_mask, dropout_p, shapes=shapes)
      │
      ▼ (内部按需调用)
get_unaligned_cp_shapes(shapes, block_id, next_block_id)
      │
      ▼
返回 [shapes[block_id], shapes[next_block_id]]
      │
      ▼
用于分块计算 & 跨 rank 通信时的非均匀 KV 交换
```

**性能数据**：原文未涉及具体性能数字、加速比或基准测试结果。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。原文仅以 Python 代码形式给出了 `get_unaligned_cp_shapes` 的实现：

```python
def get_unaligned_cp_shapes(shapes, block_id, next_block_id):
    if shapes is None:
        return None
    unaligned_cp_shapes = [shapes[block_id], shapes[next_block_id]]
    return unaligned_cp_shapes
```

符号说明：

- `shapes`：调用方传入的索引式数据结构（list/tuple/dict），保存每个 block（rank）对应的子序列长度。
- `block_id`：当前正在处理的分块标识，索引当前 rank 的有效长度。
- `next_block_id`：Ring 拓扑中下一通信目标对应的分块标识，索引目标 rank 的有效长度。
- 返回值 `unaligned_cp_shapes`：`[当前 rank 长度, 目标 rank 长度]`，供后续分块计算与通信使用；若 `shapes is None` 则直接透传 `None`，表示走传统对齐路径。

---

## 【关联】

- **上游/基座特性**：本文是 mindspeed 中"长序列并行 (Context Parallel, CP) / RingAttention"的扩展特性，建立在传统 Ring CP 能力之上。
- **核心接口 `ringattn_context_parallel`**：本特性的接入点，新增 `shapes` 参数。
- **辅助函数 `get_unaligned_cp_shapes`**：本特性的关键内部工具，被 `ringattn_context_parallel` 在分块调度时调用。
- **运行环境约束**：依赖 attention 计算的 mask 模式为 `--attention-mask-type=general`。
- **典型应用场景**：多模态学习（图像/视频/文本序列长度差异大）、实时流式数据分析（到达时间不确定导致序列长度不固定）、个性化推荐（用户行为序列长度各异）。
- **内部链接**：原文未提供任何内部链接。

---

## 【使用方法】

**启用方式（原文有）：**

1. 在调用 `ringattn_context_parallel` 接口时，通过新增的 `shapes` 参数传入各 rank 的非均匀切分长度。示例代码：

```python
output = ringattn_context_parallel(
    q, k, v,
    head_num,
    cp_para,
    softmax_scale,
    attn_mask,
    dropout_p,
    shapes=shapes
)
```

2. `shapes` 参数的合法形式（任选其一）：

   - 列表：`[100, 100, 20]`
   - 元组：`(100, 100, 20)`
   - 字典：`{0: 100, 1: 100, 2: 20}`

   只要支持 `[]` 索引访问即可。

3. 运行环境需满足：原文中明确指出的唯一硬性约束——**仅支持 `--attention-mask-type` 为 `general` 的场景**。

**配置项/命令行参数**：原文未涉及独立的环境变量或新增命令行开关；其启用依赖于上述 `shapes` 参数的传入以及 `--attention-mask-type=general` 的注意力掩码配置。
