# FPDT (fully pipelined distributed transformer) (Ulysses + offload)

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/fpdt.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/fpdt.md

# FPDT (fully pipelined distributed transformer) 文档深度解读

---

## 【定位】

本篇文档描述了 FPDT（Fully Pipelined Distributed Transformer）特性——一种在原生 Ulysses 序列并行基础上叠加细粒度 chunk 切分、计算/通信并行调度以及 CPU-NPU offload 的增强方案，用于解决多模态/长序列训练与推理中传统 Transformer 出现的流水线阻塞、通信延迟、计算空泡和显存不足等瓶颈问题。

---

## 【技术要点】

1. **两级切分机制**：在原生 Ulysses 按 sequence 维度切分的基础上，再将切分后的 sequence 进一步拆解为多个 chunks，形成"Ulysses 切分 → FPDT chunk 切分"的两级粒度。
2. **计算-通信掩盖（overlap）**：通过计算流与通信流的并行调度，使模块内（intra-module）实现并发，规避原生 Ulysses 中"同步依赖强、通信与计算无法有效重叠"的阻塞。
3. **CPU-NPU load/offload**：在 NPU 显存紧张时支持将数据 offload 到 CPU 侧，缓解显存压力，是 FPDT 应对 OOM 的关键手段。
4. **三项使能开关**：FPDT 主开关（--FPDT）、chunk 数量（--FPDT-chunk-number）、offload 子开关（--FPDT-with-offload），三者均通过 `pretrain_model.json` 中的 `predictor` 字段配置。
5. **依赖约束**：必须满足 `CP > 1`（同时开启 FPDT 与 FPDT_chunk_number 才算真正使能），并且 `per_gpu_seq_len` 必须能被 `FPDT_chunk_number` 整除（保证均匀切分）。
6. **典型触发场景**：视频分辨率/帧数设置得很大，单卡计算过程会触发 OOM，此时开启 FPDT 是必要手段。

---

## 【关键机制与数据】

**工作原理（两级流水线）**

- 原文："在原生 Ulysses 切分 sequence 逻辑的基础上再将切分后的 sequence 拆解成多个 chunks，结合计算流与通信流并行调度，实现模块内并发，有效提升资源利用率。"
- 第一级：原生 Ulysses 按 sequence 维度做粗粒度切分（典型用于 Context Parallelism）。
- 第二级：FPDT 在每个 Ulysses 切分片内部再做 chunk 维度的细粒度切分，使每个 chunk 更小、计算单元更轻。
- 在模块内，chunk 维度的计算与 All-to-All 等集合通信被调度到不同流（stream），从而实现"通信与计算掩盖"，压缩空泡（bubble）。
- 在显存维度：当 NPU 侧 HBM 不够时，可通过 `FPDT_with_offload` 把中间张量卸载到 CPU 内存，按需重新加载，突破单卡显存上限。

**数据流概览**

```
Sequence 输入
   │
   ▼
[原生 Ulysses 切分]  —— CP 维度（卡间）
   │
   ▼
[FPDT chunk 切分]    —— chunk 维度（卡内 / 流水级）
   │
   ├── 计算流 ──→ chunk 级 forward/backward
   │
   └── 通信流 ──→ All-to-All（被计算掩盖）
   │
   ▼
[FPDT_with_offload 可选]  —— CPU 内存 ↔ NPU HBM 换入换出
   │
   ▼
输出
```

**性能/效果数据**

- 原文："根据模型不同、参数量不同，效果各有差异，可以针对 FPDT_chunk_number、FPDT_with_offload 指标进行调优，均有收益。"
- 原文未提供具体的加速比、显存节省百分比或吞吐量数字，仅给出"调优这两个指标均有收益"的定性结论；具体数值需用户根据自身模型实测。

---

## 【表格解读】

**原文无表格。**

原文在「使用方法」一节给出了一段 JSON 配置示例，但这是**配置代码块**，不是参数表或性能对比表，因此按要求判定为"原文无表格"。该 JSON 的关键字段值可在【使用方法】一节查看。

---

## 【公式解读】

**原文无公式。**

文档中仅含一个隐含的整除约束："需要确保 per_gpu_seq_len 可以被 FPDT_chunk_number 整除"。如果按伪代码形式表达即为：

```
assert per_gpu_seq_len % FPDT_chunk_number == 0
```

含义：每个 NPU 上的序列长度 `per_gpu_seq_len` 必须能被 chunk 数量 `FPDT_chunk_number` 整除，否则 chunk 切分不均匀会导致流水线尾部出现尾块（tail chunk）等待，破坏并发掩盖效果。该式为自然语言描述，原文未给出符号化的数学公式。

---

## 【关联】

文档显式或隐式涉及以下上下游/关联特性：

- **Ulysses 序列并行**：FPDT 的切分根基，原文明确写到"在原生 Ulysses 切分 sequence 逻辑的基础上"；FPDT 是对 Ulysses 的细粒度补丁。
- **CP / Context Parallelism**：`CP > 1` 是 FPDT 的使能前提，CP 是 FPDT 发挥作用的载体。
- **DeepSpeed FPDT 实现**：原文「鸣谢」给出参考实现 `deepspeed/sequence/fpdt_layer.py`，意味着 mindspeed-mm 的 FPDT 借鉴/对接了 DeepSpeed 中的同名模块。
- **多模态视频训练**：触发场景为"视频分辨率/帧数设置的很大时，单卡 OOM"，因此 FPDT 与多模态视频生成/理解 pipeline 直接耦合，配置入口位于 `predictor` 字段而非通用训练字段。
- **CPU-NPU 异构内存体系**：`FPDT_with_offload` 涉及 host memory 与 device memory 之间的数据换入换出，属于 PyTorch / Megatron-LM 风格的 activation offload 扩展。

> 说明：原文末尾「鸣谢」只给出了两个外部链接（DeepSpeed 教程和代码），**未提供仓库内部的交叉链接**（与本次提示 "内部链接: (无)" 一致）。因此本节关系梳理均基于正文语义抽取，无内部锚点可指。

---

## 【使用方法】

**典型场景（原文）**：

> "视频分辨率/帧数设置的很大时，训练过程中，单卡进行计算过程会报 OOM，需要开启 FPDT。"

**使能步骤（原文）**：

1. 编辑启动脚本中的 `pretrain_model.json`，定位到 `predictor` 配置块。
2. 配置以下三个布尔/整型字段（原文示例值）：

```json
{
  "predictor": {
    "FPDT": true,
    "FPDT_chunk_number": 4,
    "FPDT_with_offload": true
  }
}
```

| 字段 | 类型 | 含义 | 原文中给出的示例值 |
|---|---|---|---|
| `FPDT` | bool | FPDT（Ulysses Offload）主开关 | `true` |
| `FPDT_chunk_number` | int | chunk 数量，越大粒度越细，但需满足整除约束 | `4` |
| `FPDT_with_offload` | bool | 是否启用 CPU-NPU 间的 load/offload | `true` |

3. 对应命令行参数形式（原文给出）：

| 命令行参数 | 对应 JSON 字段 |
|---|---|
| `--FPDT` | `FPDT` |
| `--FPDT-chunk-number` | `FPDT_chunk_number` |
| `--FPDT-with-offload` | `FPDT_with_offload` |

**触发条件与约束（原文）**：

- 必须 `CP > 1`；同时开启 `FPDT` 与 `FPDT_chunk_number` 才算真正使能 FPDT。
- 必须保证 `per_gpu_seq_len % FPDT_chunk_number == 0`（即每个 GPU 上的序列长度可被 chunk 数整除）。

**调优建议（原文）**：

> "可以针对 FPDT_chunk_number、FPDT_with_offload 指标进行调优，均有收益。"——具体最优值需要根据模型结构与参数量自行试验，**原文未给出推荐数值表**。
