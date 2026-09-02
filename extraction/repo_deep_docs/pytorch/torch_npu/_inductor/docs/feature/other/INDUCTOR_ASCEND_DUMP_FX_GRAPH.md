# INDUCTOR_ASCEND_DUMP_FX_GRAPH

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/other/INDUCTOR_ASCEND_DUMP_FX_GRAPH.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/other/INDUCTOR_ASCEND_DUMP_FX_GRAPH.md

# INDUCTOR_ASCEND_DUMP_FX_GRAPH 文档深度解读

## 【定位】

这篇文档描述了 TorchNPU（昇腾 PyTorch 适配插件）中 Inductor 子模块的一个 FX Graph dump 调试开关能力，用于在单算子用例场景下生成 FX Graph 供调试与问题排查使用。

---

## 【技术要点】

- **核心用途**：dump 功能专用于单算子（single-op）用例的调试和问题排查。
- **环境变量名**：`INDUCTOR_ASCEND_DUMP_FX_GRAPH`，默认值为空（未设置即关闭）。
- **取值规则**：
  - 未设置或空 → 关闭 fx graph dump（默认值）；
  - `1`、`true`、`yes` 等真值字符串 → 开启 fx graph dump。
- **自动启用机制**：当 `INDUCTOR_ASCEND_CHECK_ACCURACY` 或 `AOTI_ASCEND_DEBUG_KERNEL` 启用时，本功能会被自动开启。
- **副作用提示**：开启后会生成额外的文件，占用磁盘空间，因此建议仅在调试和问题排查场景下使用。
- **适用硬件**：支持型号为 Atlas A5 系列产品（原文使用 `<term>Atlas A5 系列产品</term>` 标签）。

---

## 【关键机制与数据】

- **工作机制（原文）**：通过环境变量控制 FX Graph 的 dump 行为；该变量既可由用户手动设置开启，也可由 `INDUCTOR_ASCEND_CHECK_ACCURACY` 或 `AOTI_ASCEND_DEBUG_KERNEL` 触发自动开启。
- **默认值（原文）**：空（未设置），即默认关闭 fx graph dump。
- **触发链路（原文）**：上游开关（精度检查 / AOTI 调试内核启用）→ 自动启用 `INDUCTOR_ASCEND_DUMP_FX_GRAPH` → 生成额外的 dump 文件。
- **性能/吞吐数据**：原文未提供任何性能数据、文件大小、运行时间等量化指标。

---

## 【表格解读】

原文包含一个关于 `INDUCTOR_ASCEND_DUMP_FX_GRAPH` 取值含义的配置表，逐字还原如下：

| 值 | 说明 |
|---|---|
| 未设置或空 | 关闭fx graph dump（默认值） |
| 1、true、yes等 | 开启fx graph dump |

**逐行解读：**

- **第一行「未设置或空」**：表示当用户没有 export 该变量、或者 export 但未赋任何值时，FX Graph dump 功能处于关闭状态，这也是该功能的默认行为。该行的关键含义在于强调"零侵入"——不配置就不会产生任何 dump 文件，也就不会有磁盘占用。
- **第二行「1、true、yes 等」**：原文用"等"字暗示这是一个非穷举的真值集合，除明确列出的 `1`、`true`、`yes` 外，还可能包含其他等价真值字符串（如 `on`、`True`、`YES` 等），体现该开关采用布尔式字符串解析，与典型环境变量语义一致。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游关联**（自动触发本功能的开关）：
  - `INDUCTOR_ASCEND_CHECK_ACCURACY` — 启用时自动开启 FX Graph dump；
  - `AOTI_ASCEND_DEBUG_KERNEL` — 启用时同样自动开启 FX Graph dump。
- **下游关联**（本功能的产出/影响）：
  - 会生成额外的 dump 文件，占用磁盘空间（原文未指明文件路径、命名规则或输出目录）。
- **使用场景关联**：与"单算子用例调试"场景绑定，主要服务于精度比对与 AOTI 内核调试这两类问题排查流程。
- **内部链接**：原文无内部链接信息。

---

## 【使用方法】

- **启用方式（原文）**：通过环境变量开启：
  ```bash
  export INDUCTOR_ASCEND_DUMP_FX_GRAPH=1
  ```
  或使用 `true` / `yes` 等等价真值字符串。
- **关闭方式（原文）**：将变量设为空或不设置，保持默认关闭状态。
- **隐式启用（原文）**：无需手动 export，只要 `INDUCTOR_ASCEND_CHECK_ACCURACY` 或 `AOTI_ASCEND_DEBUG_KERNEL` 启用即可自动开启。
- **硬件前提（原文）**：仅在 Atlas A5 系列产品上支持。
- **其他配置项 / 命令 / 参数**：原文未涉及（未给出 dump 文件路径、文件命名、保留策略、清理命令等）。
