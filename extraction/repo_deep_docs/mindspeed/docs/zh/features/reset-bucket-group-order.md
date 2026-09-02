# bucket重排算法

> 仓 `mindspeed` · 路径 `docs/zh/features/reset-bucket-group-order.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/reset-bucket-group-order.md

# 「bucket 重排算法」feature 文档深度解读

## 【定位】

这篇文档描述了 mindspeed 中为解决「开启 `overlap-param-gather` 后计算与通信仍存在串行」问题而设计的 **bucket 重排算法** —— 通过记录并固化首次迭代的 bucket_group 触发顺序，使后续迭代的预取通信能与当前计算有效重叠，提升数据并行训练的资源利用率与吞吐。

---

## 【技术要点】

- **触发场景**：模型定义顺序与执行顺序不一致（典型如重定义 transformer 组件、使用多模态大模型时），导致参数分桶（bucket）通信与计算存在大量串行。
- **核心思路**：针对参数分桶引入「重排策略」——记录第一次迭代的 bucket_group 触发顺序，作为后续迭代通信预取的固定调度依据。
- **启用开关**：新增命令行参数 `--reset-bucket-group-order`，需配合 `--use-distributed-optimizer`、`--overlap-grad-reduce`、`--overlap-param-gather` 三个参数同时开启才能生效。
- **生效逻辑**：首次迭代仅记录顺序，不做调度优化；自第二次迭代开始，除第一个 bucket 触发无法与计算重叠外，后续每一次「预取下一个桶的通信」都能与「当前的计算」流水重叠。
- **收益量化（原文）**：在盘古模型上吞吐提升 0.85%；在手动打乱模型定义顺序的 Llama 2 上吞吐提升约 1%。
- **适用范围**：采用数据并行策略的训练场景；尤其在模型定义顺序混乱、桶通信本身无序时增益最明显。

---

## 【关键机制与数据】

**工作原理（两阶段）**

- **第一阶段 —— 顺序记录**：
  - 在第一次迭代过程中，按真实触发顺序记录 bucket-group 出现的次序。
  - 第一次前向（forward）结束时，bucket 的顺序被完整记录下来。

- **第二阶段 —— 流水掩盖**：
  - 第二次迭代开始时，依据记录的固定顺序调度预取（prefetch）。
  - 第一个 bucket 的触发由于没有「前序桶的预取通信可重叠」，仍与计算串行。
  - 此后每一次桶的预取通信，都能与当前正在执行的计算重叠，从而实现 communication–computation 的流水掩盖（pipeline masking）。

**对比基线（原文）**：Megatron 0.12.1 的方案已能解决精度问题，但不可避免地仍会出现「计算和通信串行」的问题；本特性在此基础上进一步掩盖串行，提升资源利用率。

**性能数据（原文）**：
- 盘古（开启 reset-bucket-group-order）：吞吐提升 **0.85%**。
- Llama 2（手动调乱模型定义顺序后开启）：吞吐提升 **约 1%**。
- 增益前提：必须同时开启 `use-distributed-optimizer` + `overlap-grad-reduce` + `overlap-param-gather`。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未提供内部链接。但从文中涉及的术语与机制可推断其上下游关系：

- **上游机制（依赖开启）**：
  - `use-distributed-optimizer`：分布式优化器，是参数分桶与异步通信的基础。
  - `overlap-grad-reduce`：梯度归约（reduce）与计算的重叠，是参数 gather 重叠的前置流水环节。
  - `overlap-param-gather`：参数 gather（参数广播/收集）与前向计算的重叠，是本特性要进一步掩盖的目标环节。
- **本特性解决的问题对象**：Megatron 0.12.1 中 `overlap-param-gather` 在模型定义顺序混乱场景下残余的「计算–通信串行」窗口。
- **典型应用模型**：盘古（Pangu）系列大模型、Llama 2（在打乱模型定义顺序的对照场景下验证增益）。

---

## 【使用方法】

**启用方式**：在训练启动命令中追加以下参数即可开启 bucket 重排算法：

```
--reset-bucket-group-order
```

**必须同时开启的参数（缺一不可）**：

- `--use-distributed-optimizer`
- `--overlap-grad-reduce`
- `--overlap-param-gather`

**适用训练场景**：数据并行（DP）训练；尤其推荐在模型定义顺序与执行顺序差异较大（如重定义 transformer 组件、多模态大模型）的场景下使用。
