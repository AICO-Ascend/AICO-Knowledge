# DeepSeek V4细粒度重计算

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/deepseek4_fine_grained_recompute.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/deepseek4_fine_grained_recompute.md

## 【定位】

这篇文档描述 DeepSeek V4 在 Mcore 训练场景中通过细粒度重计算减少反向传播所需激活值保存量、降低 NPU 显存占用的能力，并给出 CSA、MHC 两类重计算的独立或组合启用方式。

## 【技术要点】

1. **总体机制**：在训练且开启梯度计算的反向传播阶段，重新计算 CSA 和 MHC 中的部分中间结果，减少需要保存的激活值，从而降低 NPU 显存占用。
2. **CSA 重计算**：通过 `--recompute-csa-attention` 开启，覆盖受支持的 Q 投影、Indexer、Sparse Attention 和输出投影等计算。
3. **CSA 与归一化重计算的配合**：`--recompute-csa-attention` 与 `--recompute-norm` 组合使用时，会重计算目标层的 Q 归一化。
4. **MHC 重计算**：通过 `--mhc-recompute` 开启融合 NPU MHC pre/post 细粒度重计算；该选项仅对融合 NPU MHC 生效，因此必须同时配置 `--enable-mhc` 和 `--use-fused-mhc`。
5. **组合关系**：CSA 重计算与 MHC 重计算相互独立，没有参数依赖关系，可以单独或同时开启；同时开启时会协调中间激活值的释放时机。
6. **适用边界与代价**：
   - 仅用于 DeepSeek V4 的 Mcore 训练场景；
   - 默认关闭；
   - 仅在训练且开启梯度计算时生效；
   - MTP 层当前不启用该重计算；
   - 会增加一定计算开销，实际收益取决于模型规模、序列长度和并行配置。

## 【关键机制与数据】

该特性工作在训练的反向传播阶段：原本需要在反向计算中使用、因而需要提前保存的部分激活，改为在需要时重新计算。由此减少训练过程中的激活值保存量，进一步降低 NPU 显存占用。

- **原文:** 特性通过“在反向传播时重新计算CSA和MHC中的部分中间结果”，减少训练过程中保存的激活值。
- **原文:** CSA 重计算覆盖受支持的 Q 投影、Indexer、Sparse Attention、输出投影等计算，并与 `--recompute-norm` 配合时覆盖目标层的 Q 归一化。
- **原文:** MHC 重计算作用于融合 NPU MHC pre/post，并要求先启用 `--enable-mhc` 和 `--use-fused-mhc`。
- **原文:** 两种重计算相互独立；单独或同时开启均可，同时开启时“会协调中间激活值的释放时机”。
- **原文:** 该能力“会增加一定的重计算开销”，以额外计算换取显存节省。
- **原文:** 原文未提供显存节省量、吞吐变化、训练耗时或加速比等量化性能数据；仅说明实际收益与模型规模、序列长度和并行配置有关。
- **原文:** 原文未给出重计算层数比例、触发阈值、模块版本号或其他固定数值。

## 【表格解读】

### 原文表格逐字还原

| 重要参数 | 参数说明 |
|----------|----------|
| `--recompute-csa-attention` | 开启DeepSeek V4 CSA细粒度重计算。覆盖受支持的Q投影、Indexer、Sparse Attention以及输出投影等计算；与`--recompute-norm`组合时重计算目标层的Q归一化。 |
| `--mhc-recompute` | 开启融合NPU MHC pre/post细粒度重计算。需要同时配置`--enable-mhc`和`--use-fused-mhc`。 |

### 逐行解读

| 原文参数 | 解读 |
|---|---|
| `--recompute-csa-attention` | 开启 DeepSeek V4 的 CSA 细粒度重计算。它不是只重计算单一算子，而是覆盖文档列出的受支持计算范围，包括 Q 投影、Indexer、Sparse Attention 和输出投影。与 `--recompute-norm` 配合时，还会对目标层的 Q 归一化执行重计算。 |
| `--mhc-recompute` | 开启融合 NPU MHC pre/post 细粒度重计算。该参数不是独立可用的通用开关，文档明确要求同时配置 `--enable-mhc` 和 `--use-fused-mhc`，说明 MHC 重计算只适用于融合 NPU MHC 实现。 |

## 【公式解读】

原文无公式。

## 【关联】

原文未提供文末内部链接，以下关系均来自正文中的模块、参数及适用条件：

1. **CSA 重计算与归一化重计算**  
   `--recompute-csa-attention` 可与 `--recompute-norm` 组合，扩展到目标层 Q 归一化的重计算。

2. **MHC 重计算与融合 MHC 配置**  
   `--mhc-recompute` 依赖 `--enable-mhc` 和 `--use-fused-mhc` 共同确定融合 NPU MHC 运行环境；但它与 `--recompute-csa-attention` 之间没有参数依赖关系。

3. **CSA 与 MHC 两种重计算路径**  
   两者是相互独立的特性入口：既可分别开启，也可同时开启；同时启用时会统一协调中间激活值的释放时机。

4. **重计算与反向传播**  
   特性直接服务于训练和梯度计算阶段，用于在反向传播时恢复部分中间结果，从而减少前置激活保存。

5. **与模型及运行配置的关系**  
   是否适合开启取决于模型规模、序列长度、并行配置以及当前 NPU 显存情况。文档没有给出统一的自动选择规则，因此需要根据这些条件决定单独或组合启用。

6. **与 MTP 层的关系**  
   MTP 层当前不启用该重计算，因此该特性不覆盖 MTP 层。

## 【使用方法】

### 仅开启 CSA 细粒度重计算

```shell
--recompute-csa-attention
```

如需同时重计算目标层的 Q 归一化，还需组合：

```shell
--recompute-csa-attention \
--recompute-norm
```

### 仅开启 MHC 细粒度重计算

```shell
--enable-mhc \
--use-fused-mhc \
--mhc-recompute
```

### 同时开启两种细粒度重计算

```shell
--recompute-csa-attention \
--enable-mhc \
--use-fused-mhc \
--mhc-recompute
```

补充约束：

- 当前特性仅用于 DeepSeek V4 的 Mcore 训练场景，默认关闭。
- 必须在训练且开启梯度计算时使用。
- MTP 层当前不启用该重计算。
- 开启后会增加额外的重计算开销，应结合模型规模、序列长度、并行配置和 NPU 显存情况选择启用。
