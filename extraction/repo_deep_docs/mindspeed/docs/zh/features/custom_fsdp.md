# Megatron 全分片数据并行（Fully Sharded Data Parallel, FSDP）

> 仓 `mindspeed` · 路径 `docs/zh/features/custom_fsdp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/custom_fsdp.md

# Megatron 全分片数据并行 (FSDP) — 文档深度解读

## 【定位】
这篇文档说明了 Megatron 中 FSDP（全分片数据并行）能力的目标与用法：在 ZeRO-1 仅切分优化器状态的基础上，进一步在 DP 域内切分模型权重与梯度，从而降低大模型训练时的静态显存占用。

## 【技术要点】
1. **切分范围的扩展**：在 ZeRO-1 仅切分「优化器状态」的基础上，把「模型权重」与「梯度」也纳入 DP 域内分片，目标是降低静态显存的主要占用部分。
2. **前向通信-释放流程**：每块权重前向传播前，先在 DP 域内做 All Gather；前向结束后立即释放 Gather 得到的完整权重，仅保留分片。
3. **反向通信流程**：反向传播前再次 All Gather 取出完整权重；反向后通过 Reduce Scatter 对所有 DP rank 的梯度求和，并只保留当前 DP rank 对应的分片。
4. **触发条件**：DP > 1，且模型权重在显存中占比较大、需进一步节省显存的场景。
5. **显存与性能的权衡**：启用后静态显存下降，但每次前向/反向都额外引入通信，整体性能会下降。
6. **组合限制**：MindSpeed 仅适配该特性的基础功能，文档明确不建议与仓内其他特性组合使用。

## 【关键机制与数据】
- **背景动机（原文）**：「随着大模型权重增加，需要进一步提高显存利用效率。之前的 ZeRO-1 操作只对优化器的状态在 DP 域内进行切分，但是对模型权重和梯度并未做切分。这使得模型权重和梯度占用静态显存的主要部分。」
- **核心数据流（原文）**：
  - 前向：`All Gather（分片→完整）` → 前向计算 → 释放完整权重，仅保留分片
  - 反向：`All Gather（分片→完整）` → 反向计算 → `Reduce Scatter（梯度求和 + 只保留本 rank 分片）`
- **性能代价（原文）**：「模型和权重被进一步切分，显存下降。但是因为每次前向反向都新增了通信，性能会下降。」

> 原文未给出任何具体的显存下降数值、通信量数值或性能基准百分比，本文不臆造。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。

## 【关联】
- **与 ZeRO-1 的关系**：FSDP 是对 ZeRO-1（仅切分优化器状态）的扩展，新增了对「模型权重」与「梯度」的 DP 域切分。文档明确以 ZeRO-1 作为对比基准。
- **与分布式优化器的协同**：启用 FSDP 的配置中要求开启 `--use-distributed-optimizer`，且要求关闭 `--gradient-accumulation-fusion`（通过 `--no-gradient-accumulation-fusion`），表明该特性与 MindSpeed 的分布式优化器和梯度累积融合存在耦合约束。
- **CUDA 设备连接约束**：要求执行 `unset CUDA_DEVICE_MAX_CONNECTIONS`，即关闭 CUDA 设备最大并发连接数设置，避免与 FSDP 的通信模式冲突。
- **组合限制（原文）**：「MindSpeed 适配该特性的基本功能，不建议与仓内其他特性组合」，即与其他 MindSpeed 特性（如并行策略、重计算、混合精度等）的叠加未在本文档保证兼容性。
- **测试脚本**：文末给出内部链接 `../../../tests_extend/system_tests/feature_tests/custom_fsdp.sh`，作为启用该特性的参考脚本入口。

## 【使用方法】
1. **启动配置（原文）**：
   ```bash
   --use-custom-fsdp
   --data-parallel-sharding-strategy optim_grads_params
   --no-gradient-accumulation-fusion
   --use-distributed-optimizer
   ```
2. **环境变量（原文）**：
   ```bash
   unset CUDA_DEVICE_MAX_CONNECTIONS
   ```
3. **参考脚本**：详细启用方式见内部链接 `../../../tests_extend/system_tests/feature_tests/custom_fsdp.sh`。
