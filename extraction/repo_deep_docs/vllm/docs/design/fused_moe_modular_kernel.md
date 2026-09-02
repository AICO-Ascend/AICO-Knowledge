# Fused MoE Modular Kernel

> 仓 `vllm` · 路径 `docs/design/fused_moe_modular_kernel.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/fused_moe_modular_kernel.md

# 一体化深度解读:Fused MoE Modular Kernel

## 【定位】

本文档介绍 vLLM 中 **FusedMoEModularKernel**(模块化内核)框架的设计与实现,它把一个完整 Fused MoE 前向中数量繁多、可替换的操作拆成三类抽象组件(Prepare/Experts/TopKWeightAndReduce),通过 **All2All Dispatch 的输入激活格式**区分 Contiguous(Non-Batched)和 Batched 两种变体,从而把"全连接 dispatch × 多种 expert kernel × 多种 reduce 策略"组合爆炸变成可管理、可独立测试的几条主干,并通过抽象基类为未来实现提供统一骨架。

---

## 【技术要点】

1. **两种输入激活格式(由 All2All Dispatch 决定)**
   - **Contiguous / Standard / Non-Batched**:激活张量形状 `(M, K)`,附带 `TopK Ids` 与 `TopK weights`,形状均为 `(M, num_topk)`;代表实现 `DeepEPHTPrepareAndFinalize`(对应 DeepEP High-Throughput All2All)。
   - **Batched**:激活张量形状 `(num_experts, max_tokens, K)`,**并非所有条目都有效**;附带 `expert_num_tokens` 张量(`size = num_experts`),其中 `expert_num_tokens[i]` 表示订阅第 i 个 expert 的有效 token 数;代表实现 `DeepEPLLPrepareAndFinalize`(对应 DeepEP Low-Latency All2All)。

2. **三类抽象组件**
   - `TopKWeightAndReduce` —— 在 Unpermute 之后、All2All Combine 之前做 TopK 权重应用与归约(也可下沉到 Experts 中)。
   - `FusedMoEPrepareAndFinalizeModular` —— 暴露 `prepare` / `prepare_no_receive` / `finalize`,负责输入量化 + All2All Dispatch + All2All Combine。
   - `FusedMoEExpertsModular` —— 暴露 `apply` / `workspace_shapes` / `finalize_weight_and_reduce_impl`,负责 MoE 核心计算。

3. **`FusedMoEPrepareAndFinalizeModular` 的三大接口**
   - `prepare`:输入激活量化 + All2All Dispatch。
   - `prepare_no_receive`:与 `prepare` 类似但**不阻塞等待其他 worker**;返回 "receiver" 回调,由调用方稍后触发以等待跨 worker 结果;**并非所有实现都支持**,若可用可与共享 expert 等工作**交叉执行**(interleaving)。
   - `finalize`:触发 All2All Combine,**可选择**在此完成 TopK 权重应用与归约(由传入的 `TopKWeightAndReduce` 对象决定)。

4. **`FusedMoEExpertsModular::apply()` 的操作序列**
   `Permute → Matmul(W1) → Act + Mul → Quantization → Matmul(W2) → Unpermute → (可选)TopK 权重应用 + 归约`。

5. **`workspace_shapes()` 必须返回的内容**
   **2 个 workspace 形状** + **workspace 数据类型** + **fused MoE 输出形状**,供 `FusedMoEModularKernel::forward()` 一次性分配 workspace 张量与输出张量,避免多次中间内存分配。

6. **TopK 权重应用/归约位置由返回的 `TopKWeightAndReduce` 对象决定**
   - 在 `FusedMoEExpertsModular` 内完成 → `finalize_weight_and_reduce_impl()` 返回 `TopKWeightAndReduceNoOp`。
   - 交给 `FusedMoEPrepareAndFinalizeModular::finalize()` 完成 → 返回 `TopKWeightAndReduceContiguous` / `TopKWeightAndReduceNaiveBatched` / `TopKWeightAndReduceDelegate` 之一。
   - `FusedMoEModularKernel` 在两者之间充当"桥梁",决定权重归约实际发生位置。

---

## 【关键机制与数据】

- **Batched 与 Non-Batched 的核心差异**(原文):操作层面上的主要区别只在 `Permute / Unpermute`,其他操作保持一致。
- **Batched 变体中"非法条目"语义**(原文):`num_experts × max_tokens × K` 张量**并非所有条目都有效**,必须配合 `expert_num_tokens` 才能定位有效 token。
- **workspace 张量复用机制**(原文):连续多个算子复用同一组预分配 workspace,避免中间 tensor 反复分配,由 `FusedMoEModularKernel::forward()` 统一分配并传入 `apply()`。
- **延迟接收 / 交错执行机制**(原文):`prepare_no_receive` 通过返回 receiver 回调,**允许把 All2All 的等待与本地计算(例如 shared expert)** 在时间上交错,减少气泡。
- **Decoupling 价值**(原文):Modular Kernel 把 All2All Dispatch & Combine 实现与 fused MoE 实现**解耦**,允许二者**独立开发与测试**。
- **典型耗时点下沉案例**(原文):在 `FusedMoEExpertsModular::apply()` 内做 TopK 权重应用与归约可获得性能收益,典型 PR 见 `https://github.com/vllm-project/vllm/pull/20228`。
- **典型后端绑定**(原文):
  - `DeepEPHTPrepareAndFinalize` ← DeepEP **High-Throughput** All2All kernels
  - `DeepEPLLPrepareAndFinalize` ← DeepEP **Low-Latency** All2All kernels

---

## 【表格解读】

**原文无表格**(原文中没有出现任何 markdown 表格或键值对照表;仅有两张配图链接 `figures/fused_moe_non_batched.png`、`figures/fused_moe_batched.png`、`figures/prepare_and_finalize_blocks.png`、`figures/fused_experts_blocks.png`,以及若干示意图,但都不属于表格)。

---

## 【公式解读】

原文给出 `FusedMoEModularKernel` 的 Python 伪代码 sketch,逐字保留如下:

```py
class FusedMoEModularKernel:
    def __init__(self,
                 prepare_finalize: FusedMoEPrepareAndFinalizeModular,
                 fused_experts: FusedMoEExpertsModular):

        self.prepare_finalize = prepare_finalize
        self.fused_experts = fused_experts

    def forward(self, DP_A):

        Aq, A_scale, _, _, _ = self.prepare_finalize.prepare(DP_A, ...)

        workspace13_shape, workspace2_shape, _, _ = self.fused_experts.workspace_shapes(...)

        # allocate workspaces
        workspace_13 = torch.empty(workspace13_shape, ...)
        workspace_2 = torch.empty(workspace2_shape, ...)

        # execute fused_experts
        fe_out = self.fused_experts.apply(Aq, A_scale, workspace13, workspace2, ...)

        # war_impl is an object of type TopKWeightAndReduceNoOp if the fused_experts implementations
        # performs the TopK Weight Application and Reduction.
        war_impl = self.fused_experts.finalize_weight_and_reduce_impl()

        output = self.prepare_finalize.finalize(fe_out, war_impl,...)

        return output
```

**符号逐项解释:**

| 符号 | 含义 / 作用 |
|---|---|
| `prepare_finalize` | `FusedMoEPrepareAndFinalizeModular` 实例,持有 `prepare`/`prepare_no_receive`/`finalize` 三接口 |
| `fused_experts` | `FusedMoEExpertsModular` 实例,持有 `apply`/`workspace_shapes`/`finalize_weight_and_reduce_impl` |
| `DP_A` | 进入 MoE 前的输入激活(Data-Parallel 维度的 activation) |
| `Aq` | `prepare()` 输出之一:**已量化**的激活(Quantization 在此完成) |
| `A_scale` | `prepare()` 输出之一:**量化 scale** |
| `_, _, _, _` | `prepare()` 还会产出 `TopK ids`、`TopK weights`、以及 All2All 通信相关的元数据/handle,这里被解构丢弃 |
| `workspace13_shape`、`workspace2_shape` | 由 `workspace_shapes()` 返回的 **2 个 workspace 形状**(分别覆盖 W1 前后两段中间结果,与 W2 阶段) |
| `_ , _` | `workspace_shapes()` 还会返回 **workspace 数据类型** 与 **fused MoE 输出形状** |
| `workspace_13`、`workspace_2` | 由 `torch.empty` 按上述形状一次性预分配的中间缓冲区 |
| `fe_out` | `apply()` 输出,即经过 `Permute → W1 matmul → Act+Mul → Quant → W2 matmul → Unpermute →(可选)TopK Weight+Reduce` 后的结果 |
| `war_impl` | `TopKWeightAndReduce` 对象;若 `fused_experts` 已自行完成权重归约则为 `TopKWeightAndReduceNoOp`,否则为 `TopKWeightAndReduceContiguous` / `NaiveBatched` / `Delegate` 之一 |
| `output` | `prepare_finalize.finalize(fe_out, war_impl, ...)` 的最终输出(All2All Combine 后的结果) |

**整体数据流(伪代码语义):**
1. `prepare` 把本地 `DP_A` 做量化 + All2All Dispatch,得到 `Aq` / `A_scale` / TopK 信息 / 通信 handle。
2. `workspace_shapes` 询问 Experts 实现需要多大中间缓冲区。
3. `forward` 一次性分配 `workspace_13`、`workspace_2`。
4. `apply` 在 workspace 上执行完整的 Permute/W1/Act+Mul/Quant/W2/Unpermute/(可能)reduce 流程,产出 `fe_out`。
5. `finalize_weight_and_reduce_impl` 声明本步是否已做完 TopK 归约,以决定 `finalize` 是否需要补做。
6. `finalize` 触发 All2All Combine,必要时调用 `war_impl` 完成 TopK 归约,产出 `output`。

---

## 【关联】

- **核心实现文件**
  - [`modular_kernel.py`](../../vllm/model_executor/layers/fused_moe/modular_kernel.py) — `FusedMoEModularKernel` 主类定义,以及三类抽象组件的协调逻辑。
  - [`topk_weight_and_reduce.py`](../../vllm/model_executor/layers/fused_moe/topk_weight_and_reduce.py) — `TopKWeightAndReduceNoOp` / `TopKWeightAndReduceContiguous` / `TopKWeightAndReduceNaiveBatched` / `TopKWeightAndReduceDelegate` 等具体实现。
  - [`all2all.py`](../../vllm/distributed/device_communicators/all2all.py) — `FusedMoEPrepareAndFinalizeModular` 类型所依赖的 All2All Dispatch / Combine 通信层。

- **特性与背景文档**(同仓 design 目录)
  - [`moe_kernel_features.md#fused-moe-modular-all2all-backends`](./moe_kernel_features.md#fused-moe-modular-all2all-backends) — Modular 框架所支持的 All2All 后端清单(DeepEP HT/LL 等)。
  - [`moe_kernel_features.md#fused-experts-kernels`](./moe_kernel_features.md#fused-experts-kernels) — `FusedMoEExpertsModular` 的可选 expert kernel 实现。

- **测试与工具**
  - [`test_modular_kernel_combinations.py`](../../tests/kernels/moe/test_modular_kernel_combinations.py) — 对多种 `prepare_finalize × fused_experts` 组合做正确性测试。
  - [`mk_objects.py`](../../tests/kernels/moe/modular_kernel_tools/mk_objects.py) — 在测试中构造 Modular Kernel 对象的工厂。
  - [`common.py`](../../tests/kernels/moe/modular_kernel_tools/common.py) — 测试公共工具。
  - [`profile_modular_kernel.py`](../../tests/kernels/moe/modular_kernel_tools/profile_modular_kernel.py) — 对 Modular Kernel 组合进行性能 profiling。

- **上游**
  - All2All Dispatch / Combine 内核(如 DeepEP High-Throughput / Low-Latency kernels),被 `FusedMoEPrepareAndFinalizeModular` 类型(如 `DeepEPHTPrepareAndFinalize`、`DeepEPLLPrepareAndFinalize`)封装。

- **典型性能优化 PR**
  - 在 `FusedMoEExpertsModular::apply()` 内做 TopK 权重应用与归约的示例:[vllm-project/vllm#20228](https://github.com/vllm-project/vllm/pull/20228)。

---

## 【使用方法】

- **新增 `FusedMoEPrepareAndFinalizeModular` 类型(原文涉及,文档在 Step 1 中途中断)**
  - 通常一个 `FusedMoEPrepareAndFinalizeModular` 类型由一种 **All2All Dispatch & Combine 内核** 承载;如 `DeepEPHTPrepareAndFinalize` 由 DeepEP High-Throughput 承载,`DeepEPLLPrepareAndFinalize` 由 DeepEP Low-Latency 承载。
  - **Step 1:Add an All2All manager**(原文此句后被截断:"The `FusedMoEPrepareAndFinalizeModular` implementations typically fetch a kernel-implementation 'handle' from the All2" —— 后续步骤在原文提供的文本中未给出)。

- **新增 `FusedMoEExpertsModular` 实现的关键约束**(原文)
  - 必须实现 `apply()` / `workspace_shapes()` / `finalize_weight_and_reduce_impl()`。
  - `workspace_shapes()` 必须返回 **2 个 workspace 形状 + workspace 数据类型 + fused MoE 输出形状**,供 `FusedMoEModularKernel::forward()` 预分配内存。
  - 若在 `apply()` 内自行完成 TopK 权重应用与归约,则 `finalize_weight_and_reduce_impl()` 返回 `TopKWeightAndReduceNoOp`;否则返回 `TopKWeightAndReduceContiguous` / `TopKWeightAndReduceNaiveBatched` / `TopKWeightAndReduceDelegate` 之一,交给 `finalize()` 执行。

- **启用 Modular Kernel 的运行时路径**(原文)
  - 通过 `FusedMoEModularKernel(prepare_finalize, fused_experts)` 组合一个具体后端;在 `forward(DP_A)` 中: `prepare → workspace 分配 → apply → finalize_weight_and_reduce_impl → finalize`,无需额外开关代码。

- **未涉及**
  - 具体的命令行 flag、环境变量、配置文件 key 在本文档提供的内容中**未给出**;`How-To` 中 Step 1 之后的步骤、以及"如何新增 `FusedMoEExpertsModular` / `TopKWeightAndReduce`"的详细步骤在原文截断处之后,原文未涉及。

## 图文联合解读

- `fused_moe_non_batched.png`: **图文解读：**

1）图示Fused MoE非批处理流程：DP_A→量化→All2All Dispatch分发→Permute按专家分组复制→两次GroupedGemm(W1/W2)，夹带激活+乘法与二次量化→Unpermute还原→TopK加权→Reduce→All2All Combine汇聚。

2）论证关键结论：非批处理需经permute将同专家token聚合成GroupedGemm输入格式，量化位置影响尺度张量形状。

3）与文档呼应：直观展示Contiguous变体中(M,K)连续输入如何经专家分组变换为GroupedGemm格式，支撑"输入格式决定后续算子链"的核心论点。
- `fused_moe_batched.png`: 1) 图示Batched/Masked变体的全流程数据流：`DP_A(M_dp,K)` → `Quantization` → `All2All Dispatch`分发至各EP rank → 输出按expert聚合、填充至`max_tokens`的张量`(num_local_experts, max_tokens, K)` → `BatchedGemm(K,N)` → `Act+Mul`降至`N//2` → 二次量化 → `BatchedGemm(N//2,K)` → `All2All Combine`（含TopK加权与归约）→ 还原`DP_out(M_dp,K)`。颜色区分：紫色=输入/输出、绿色=通信（Dispatch/Combine）、蓝色=计算核（Gemm/量化）。

2) 论证：Batched格式受All2All按expert聚合所限，须以`max_tokens`对齐填充并使用`BatchedGemm`；模块化内核因此需将"通通信+量化+批量GEMM"三阶段串联，方能完成MoE前向。

3) 与文档论点呼应——印证"输入激活布局完全取决于All2All Dispatch，且Batched变体需配合专用Combine完成TopK归约"。
- `prepare_and_finalize_blocks.png`: **图文联合解读：**

图示展示了 Fused MoE **Non-Batched/Contiguous** 变体的端到端流水线，分为三大模块化块：**Prepare**（量化→All2All Dispatch 跨 EP 通信）、**Maybe Finalize**（TopK 权重应用→Reduce）、**Finalize**（All2All Combine），中间由白框代表核心融合算子（Permute+MM1+Act_Mul+Quant+MM2+UnPermute）。

它论证了 FusedMoEModularKernel 通过**模块化分块**将通信、计算、归约解耦，使 Prepare/Combine/Finalize 可插拔（如 DeepEPHT vs DeepEPLL）。结合文档，此图印证了"输入格式决定变体，但整体框架统一"的论点，为不同 All2All Dispatch 提供了可替换的接口抽象。
- `fused_experts_blocks.png`: ## 图文联合解读

**1) 图中内容：** 展示FusedMoE Non-Batched（非批处理/连续）变体的完整流水线。数据流向：DP_A → Quantization → All2All Dispatch → **FusedMoEPermuteExpertsUnpermute块**（Permute→GroupedGemm W1→Act+Mul→Quant→GroupedGemm W2→Unpermute）→ **Maybe块**（TopK权重应用+Reduce）→ All2All Combine → DP_out。关键标注包括各阶段张量形状（M, K）、"Other EP Ranks"通信接口。

**2) 技术结论：** 连续变体的核心特征是输入保持(M, K)连续格式；计算通过Permute转为GroupedGemm可处理的分组格式，Unpermute再还原；Reduce块为可选模块（Maybe），体现模块化设计。

**3) 与文档关系：** 直接对应文档"Contiguous variant"的描述（shape (M, K)、示例DeepEPHTPrepareAndFinalize），将抽象"多步操作"具象化为可复用的PermuteExpertsUnpermute核心块+可选Reduce块的两层模块化结构。
