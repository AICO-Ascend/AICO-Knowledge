# TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS （同社区）

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/catlass/TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/catlass/TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS.md

# 一体化深度解读：TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS

## 【定位】

这篇文档说明 TorchInductor 在 max-autotune 模式下可挑选的 GEMM（通用矩阵乘）后端候选列表的环境变量配置方式，并指出该变量在 Ascend for PyTorch 社区中与上游 PyTorch 社区同名为 `TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS`，从而让昇腾用户在不改代码的前提下，通过追加 `"CATLASS"` 字符串来把 Catlass 后端纳入 autotune 候选。

## 【技术要点】

1. **变量名与社区对齐**：环境变量名为 `TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS`，文档明确标注"同社区"，即与 PyTorch 上游同名变量语义一致，确保用户从社区迁移到昇腾插件时无需重新学习。
2. **取值形式**：变量值是一组以逗号分隔的后端名字符串（如 `"ATEN,TRITON,CPP"` 或 `"CATLASS,ATEN"`），TorchInductor 在 max-autotune 阶段会按列表顺序或全量遍历这些候选后端做性能择优。
3. **默认配置**：默认值为 `TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS="ATEN,TRITON,CPP"`，文档强调"此默认值为社区的默认配置"，即昇腾侧未额外注入任何昇腾专有后端。
4. **启用 Catlass 的方式**：要在 max autotune 中尝试 Catlass 后端，只需把字符串 `"CATLASS"` 加入到该环境变量的值列表中（其它项保持不变），Catlass 就会作为一个新的可试后端。
5. **支持的硬件范围**：仅在 **Atlas A5 系列产品**上提供（原文未给出其它具体型号枚举）。
6. **使用约束**：原文明示"无"，即不附加额外的算子形状、dtype、layout 等前置限制。

## 【关键机制与数据】

- **原文：** 该环境变量"确认 max autotune 可尝试的后端有哪些"，属于 max-autotune 调优流程中的**候选后端白名单**。TorchInductor 在 max-autotune 模式下，会针对同一 GEMM 形状生成多个不同后端（ATEN / TRITON / CPP / CATLASS）的实现并实测耗时，再选择最快者编译到最终生成的代码中。
- **原文：** 变量值以**逗号分隔的字符串列表**形式给出（如 `"ATEN,TRITON,CPP"`、`"CATLASS,ATEN"`），本质上是给 TorchInductor 的后端候选枚举提供了一份用户可控的过滤集合。
- **原文：** 默认配置为 `"ATEN,TRITON,CPP"`，**不包含 CATLASS**——意味着在不显式配置时，昇腾侧与社区行为完全一致，不会自动启用 Catlass。
- **原文：** 加入 `"CATLASS"` 的方式不是覆盖式替换，而是**追加到列表中**（示例为 `"CATLASS,ATEN"`），用户可与现有社区后端共存。
- **性能数据**：原文未给出任何 benchmark 数字、加速比或与其它后端的耗时对比。
- **数据流**：原文未描述具体的数据流路径或调用栈。

## 【表格解读】

**原文无表格。**

## 【公式解读】

**原文无公式。**

## 【关联】

- **与上游 PyTorch 社区的关系**：该变量与社区 max-autotune 中"选择 GEMM 后端"的环境变量同语义、同名（同社区），因此其取值语义、默认行为均与社区一致，可视作上游变量在昇腾侧的直接延伸。
- **与 Catlass 后端的关系**：Catlass 是昇腾自研的高性能矩阵运算库，本特性通过把 `"CATLASS"` 加入候选列表，使 Catlass 成为 max-autotune 中可被自动挑选的 GEMM 实现之一，构成本仓库 `_inductor/docs/feature/catlass/` 路径下的 Catlass 特性入口之一。
- **与 TorchInductor max-autotune 的关系**：变量作用于 TorchInductor 的 max-autotune 调优阶段，作用于 `_inductor` 命名空间下的代码，与 `torch_npu/_inductor` 这一 Inductor 适配模块直接相关。
- **硬件绑定**：通过"支持的型号"段将本特性锚定到 **Atlas A5 系列产品**，即与昇腾具体芯片代际绑定。
- 原文文末括号内给出"(无)"内部链接信息，本文未识别到可链向其它特性的内链。

## 【使用方法】

1. **查看/确认当前默认值**（原文默认）：
   ```shell
   echo $TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS
   # 未设置时，行为等价于 "ATEN,TRITON,CPP"
   ```

2. **启用 Catlass 后端并与 ATEN 共存**（原文配置示例）：
   ```shell
   export TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS="CATLASS,ATEN"
   ```

3. **完全替换为 Catlass 单一候选**（基于原文语义推断的等价用法，原文未直接给出该组合，仅给出"加入"形式的示例）：
   ```shell
   export TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS="CATLASS"
   ```

4. **恢复社区默认行为**：
   ```shell
   export TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS="ATEN,TRITON,CPP"
   ```

5. **典型调用场景**：在脚本或容器入口中 export 该变量后，运行 PyTorch 程序时开启 `torch.compile(..., mode="max-autotune")`（原文未明写此命令，但变量名/语义暗示了 max-autotune 模式为前提），TorchInductor 即会在该模式中按列表枚举候选后端并自动挑选最优实现。

> 说明：原文未提供 Python 层 API 入口、动态修改方式或 `torch._inductor.config` 同名配置项；以上使用方法严格基于原文中"环境变量 + max autotune"的描述给出。
