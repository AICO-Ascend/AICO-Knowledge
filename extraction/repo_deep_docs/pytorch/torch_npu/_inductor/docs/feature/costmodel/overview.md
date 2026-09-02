# CostModel特性介绍

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/costmodel/overview.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/costmodel/overview.md

# CostModel 特性深度解读

## 【定位】
本文档描述 Inductor-Ascend 在 Triton 后端 precompile 阶段新增的 **CostModel 预筛选能力**——通过 Triton-Ascend CostModel 后端对大量候选 config 做静态性能预测,按预测耗时排序后只保留较优子集进入后续编译与 profiling,从而压低首编译开销;它不改变算子语义,也不决定最终运行 kernel,仅作为「候选瘦身 + 兜底保护」环节。

---

## 【技术要点】

1. **生效条件三元组**:`INDUCTOR_ASCEND_ENABLE_COSTMODEL=1` **且** 候选 config 数量 **大于 1** **且** `INDUCTOR_ASCEND_COSTMODEL_RATIO ∈ (0, 1)`,三者同时满足才执行 CostModel 预筛选;否则跳过,使用原始 config 集合。
2. **核心接口**:Triton-Ascend 提供单 item 接口 `costmodel_bench`,返回 `(config, 预测耗时)` 二元组,Inductor 侧逐 config 调用并汇总。
3. **筛选比例参数**:`INDUCTOR_ASCEND_COSTMODEL_RATIO`(示例值 `0.25`)用于在按预测耗时升序排序后,**保留靠前的部分** config 替换原集合进入 precompile。
4. **Config 组成**:候选 config 包含 block 大小、stage 数量、warp 数量等影响代码生成与运行性能的参数。
5. **Arg Bindings 输入**:传入 TTIR 中标量参数实际值(如 `arg3=98432, pid_x=0`);当 TTIR 出现 `tt.get_num_programs x` 时,自动补充 `num_programs_x`,用于解析动态 shape 与运行时参数表达式。
6. **三层保护机制**:①过滤预测耗时为 ∞ 的 config;②筛选后集合全部编译失败时,启用被筛掉的 **兜底 config** 再做 precompile;③基于 TTIR 内容与 CostModel 参数的 **缓存**,避免重复预测。

---

## 【关键机制与数据】

**工作原理(6 步流水线,原文:「原理」节):**

1. **TTIR 逐 config 生成**:对当前 kernel 的每个候选 config 单独生成对应 TTIR。
2. **Arg Bindings 解析**:从运行时输入和 grid 信息中抽取 CostModel 所需的标量参数绑定值。
3. **静态仿真预测**:逐 config 调用 Triton-Ascend 提供的 `costmodel_bench` 单 item 接口,获得 `(config, 预测耗时)`,由 Triton-Ascend 运行时完成仿真。
4. **过滤与排序**:剔除预测耗时为 ∞ 的 config,剩余按预测耗时 **从小到大** 排序。
5. **比例截断**:按 `INDUCTOR_ASCEND_COSTMODEL_RATIO` 保留排序靠前的 config,替换原始 config 集合送入 precompile。
6. **兜底记录**:未被选中的 config 记录为兜底集;若筛选后集合未产生有效编译结果,使用兜底集再次执行 precompile。

**关键数据/语义声明(原文逐条):**

- 原文:面向 **A5+** 平台、**PyTorch-v2.9.0**、**Inductor-Ascend** Triton 后端的 **precompile 阶段** 提供预筛选。
- 原文:CostModel 预测结果是 **静态估计值,不等价于真实 profiling 耗时**,最终性能选择仍以实际编译与 profiling 为准。
- 原文:CostModel **不改变算子计算语义,不直接决定最终运行时使用的 kernel**;最终可用 config 仍会经过 precompile 校验,autotune 流程继续基于实际编译与 profiling 结果完成选择。
- 原文:Arg Bindings 无法解析的标量参数会导致该 config 预测失败,该 config 视为 **无有效预测结果**。
- 原文:CostModel 缓存命中条件包含 **TTIR 内容** 和 **传入 CostModel 的参数**,kernel 或 config 变化后会生成新缓存项。

---

## 【表格解读】
**原文无表格**。原文未提供任何参数表、性能对比表或配置矩阵。

---

## 【公式解读】
**原文无公式**。原文未给出 LaTeX 或伪代码形式的数学表达式;所涉及的关键参数(如 `INDUCTOR_ASCEND_COSTMODEL_RATIO`、`costmodel_bench` 返回的预测耗时)以文字+示例值(`0.25`、`arg3=98432`、`pid_x=0`、`num_programs_x`)形式给出。

---

## 【关联】

依据原文明确提及的上下游与依赖,可梳理如下关系链:

- **上游触发**:`torch.compile(backend="inductor")` 编译入口 → Inductor-Ascend Triton 后端 → 进入 precompile 阶段 → 触发 CostModel 预筛选(原文:「正常`torch.compile`即可进入 CostModel 链路」)。
- **下游流程**:CostModel 筛选出的 config 集合 → precompile → autotune(基于实际编译与 profiling 结果完成最终选择)→ 最终运行 kernel(原文:「后续 autotune 流程会继续基于实际编译和 profiling 结果完成选择」)。
- **横向依赖**:
  - **Triton-Ascend CostModel 后端**:提供 `costmodel_bench` 接口与 Arg Bindings 解析、静态仿真能力;若后端不可用或调用异常,**跳过 CostModel 预筛选,继续使用原始 config 集合**(原文:「使用约束」第 2 条)。
  - **Triton-Ascend 运行时**:执行 CostModel 预测过程(原文:「CostModel 预测过程由 Triton-Ascend 运行时完成」)。
  - **Triton kernel 编译中间表示 TTIR**:CostModel 的输入基础,既是单 config 静态仿真的对象,也是缓存命中键的一部分(原文:「TTIR」概念节与「使用约束」第 5 条)。
- **可配合特性**:**autotune**——CostModel 是 precompile 阶段的「前置瘦身」,autotune 仍是最终选型负责者(原文:「最终可用 config 仍会经过 precompile 校验,后续 autotune 流程会继续基于实际编译和 profiling 结果完成选择」)。

> 原文文末标注「内部链接: (无)」,故未发现可跳转的内部锚点或同级文档链接。

---

## 【使用方法】

**1. 启用开关(原文「使用方法」节):**

```shell
export INDUCTOR_ASCEND_ENABLE_COSTMODEL=1
```

**2. 调整预筛选比例(原文示例值):**

```shell
export INDUCTOR_ASCEND_COSTMODEL_RATIO=0.25
```

**3. 触发链路(原文「使用方法」节示例代码):**

```python
import torch
import torch_npu


@torch.compile(backend="inductor")
def fn(x, y):
    return x + y


out = fn(torch.randn(1024, device="npu"), torch.randn(1024, device="npu"))
```

正常调用 `torch.compile` 装饰的函数即可进入 CostModel 链路,无需额外编程接口。

**4. 启用前置条件(原文「使用约束」节汇总):**

| 条件 | 要求 |
|---|---|
| `INDUCTOR_ASCEND_ENABLE_COSTMODEL` | `=1` |
| 候选 config 数量 | `> 1` |
| `INDUCTOR_ASCEND_COSTMODEL_RATIO` | 位于 `(0, 1)` 开区间 |
| Triton-Ascend CostModel 后端 | 必须可用,否则跳过 CostModel |

**5. 原文未涉及内容:**
- 未提供关闭/回滚命令(除将 `INDUCTOR_ASCEND_ENABLE_COSTMODEL` 置非 `1` 外)。
- 未提供缓存清理/失效的命令或 API。
- 未提供日志级别或可观测性开关。
- 未提供 per-op/per-kernel 的细粒度启用粒度(仅全局环境变量)。
