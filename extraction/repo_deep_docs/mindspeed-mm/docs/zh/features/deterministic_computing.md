# 确定性计算

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/deterministic_computing.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/deterministic_computing.md

# 一体化深度解读：确定性计算（Deterministic Computing）

---

## 【定位】

这篇文档解决的是 MindSpeed MM 框架下分布式多模态训练中**训练结果不可复现**的问题——即在相同超参下，由于随机初始化、数据打乱、Dropout、归约通信与矩阵乘法调度等随机性因素导致 LOSS 曲线无法完全对齐的场景，为重复实验验证、调参优化、问题复现与调试提供确定性的计算能力保障。

---

## 【技术要点】

1. **原生 FSDP2（native FSDP2）启用方式**：在模型 YAML 配置文件的 `training` 段设置 `use_deter_comp: true`。
2. **MCORE / 基于 Megatron 的 FSDP2 启用方式**：在训练脚本的命令行参数中添加 `--use-deter-comp`。
3. **替代方案一：原生 NPU 确定性开关**：脚本中追加 `--npu-deterministic` 参数，能力来自底层 MindSpeed。
4. **替代方案二：msprobe 工具链**：通过 MindStudio Training Tools 中的 msprobe 包启用确定性计算（基于 `seed_all`）。
5. **多卡/多机环境变量 `HCCL_DETERMINISTIC=true`**：开启归约类通信算子的确定性计算与保序功能。
6. **环境变量 `CLOSE_MATMUL_K_SHIFT=1`**：关闭矩阵乘法（matmul）错峰计算，保证 matmul 计算顺序一致。

---

## 【关键机制与数据】

**触发确定性的随机源（原文）：**
> 随机初始化、数据打乱、dropout 等

文档指出这些是导致相同超参下训练结果不一致的根因，且明确说明"即使使用相同的超参数，每次训练的结果也可能存在差异，导致 LOSS 曲线无法完全重合"——这是启用确定性计算的目标信号。

**适用场景（原文明确列举）：**
- 重复实验验证
- 调参优化过程
- 问题复现和调试

**性能权衡说明（原文）：**
> 启用确定性计算会对训练性能产生一定影响。
> 在生产环境中，可以根据实际需求权衡确定性和性能。

文档未给出具体的性能损耗百分比、加速比等量化指标，仅做定性说明，因此**性能数据按"原文未涉及"处理**。

**数据流层面的机制（综合原文可推导）：**
- 路径 A（`use_deter_comp: true` / `--use-deter-comp`）→ 框架内确定性开关；
- 路径 B（`--npu-deterministic`）→ 借助 MindSpeed 的 NPU 算子确定性能力；
- 路径 C（msprobe）→ 通过 `seed_all` 一类机制统一固定 Python/PyTorch/Numpy 等随机种子；
- 配套开关 `HCCL_DETERMINISTIC=true` 作用于**集合通信层**（all-reduce 等归约算子）；
- `CLOSE_MATMUL_K_SHIFT=1` 作用于**计算层**（matmul 算子调度策略）。
  上述三层共同保证端到端可复现。

---

## 【表格解读】

**原文无表格。** 文档中只有命令/参数行（YAML 字段、CLI flag、环境变量），未给出参数对照表或性能对比表。

---

## 【公式解读】

**原文无公式。** 文档未涉及任何数学公式或伪代码。

---

## 【关联】

按用户给出的"内部链接：(无)"，本文档在 mindspeed-mm 仓内没有锚点式交叉引用，但存在若干**外部链接**，下游读者据此跳转：

1. **[MindSpeed 确定性计算文档](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/npu_deterministic.md)**——`--npu-deterministic` 参数的详细说明所在，定位为 mindspeed-mm 的**上游基础能力**（MindSpeed → MindSpeed MM）。
2. **[msprobe 文档 seed_all 章节](https://gitcode.com/Ascend/msprobe/blob/master/docs/zh/user_guide/dump/pytorch_data_dump_instruct.md#seed_all)**——MindStudio Training Tools 工具链中的 msprobe 包，作为**替代方案**提供基于 seed 的确定性能力。
3. **[HCCL_DETERMINISTIC 说明（CANN 社区版 82RC1）](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/maintenref/envvar/envref_07_0099.html)**——昇腾 CANN/HCCL 集合通信库的官方环境变量文档，为本文档多卡/多机场景的环境变量提供权威说明，是**底层依赖**。

**模块间关系（综合原文）：**
- mindspeed-mm 提供两种**内置入口**（YAML `use_deter_comp` 与 CLI `--use-deter-comp`），覆盖两种训练后端（native FSDP2 与 megatron-FSDP2 / MCORE）。
- 当内置入口不适用或需更细粒度控制时，可下沉至 **MindSpeed（上游）** 的 `--npu-deterministic`，或平行使用 **msprobe（昇腾工具链）** 的 `seed_all`。
- 多卡/多机场景必须额外打开 **CANN HCCL 层** 的 `HCCL_DETERMINISTIC` 与 `CLOSE_MATMUL_K_SHIFT`，否则框架级开关在跨节点集合通信与 matmul 调度处仍可能引入随机性。

---

## 【使用方法】

**方式一：原生 FSDP2（YAML）**——在模型 YAML 配置文件的 `training` 段设置：

```yaml
training:
  use_deter_comp: true
```

**方式二：MCORE / Megatron-FSDP2（CLI）**——在训练脚本中添加：

```bash
--use-deter-comp
```

**方式三：替代方案 `--npu-deterministic`（CLI）**——在脚本中添加：

```bash
--npu-deterministic
```

（适用场景与差异详见上文"关联"节中的 MindSpeed 文档链接。）

**方式四：替代方案 msprobe 工具链**——通过 MindStudio Training Tools 中的 msprobe 包调用 `seed_all` 启用（详见 msprobe 文档）。

**必需的环境变量（多卡/多机与 matmul 场景）：**

```bash
# 1) 多卡/多机：开启归约类通信算子的确定性 + 保序
export HCCL_DETERMINISTIC=true

# 2) 关闭 matmul 错峰计算，保证 matmul 计算顺序一致
export CLOSE_MATMUL_K_SHIFT=1
```

**注意事项（原文）：**
- 启用确定性计算**会对训练性能产生一定影响**（具体损耗原文未给出量化数据）。
- 生产环境中需在确定性与性能之间**按实际需求权衡**。
