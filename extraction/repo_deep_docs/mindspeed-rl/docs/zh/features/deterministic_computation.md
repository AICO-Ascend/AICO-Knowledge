# 确定性计算

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/deterministic_computation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/deterministic_computation.md

# 确定性计算 Feature 文档深度解读

## 【定位】

本文档描述 mindspeed-rl 强化学习加速库中「确定性计算」特性的启用方法与配置流程,解决「重复训练 reward 分数可能不一致、无法复现训练过程和定位问题」的工程痛点,在给定相同输入时保证输出完全可复现。

---

## 【技术要点】

文档将确定性计算拆解为**三层配置**,由数据入口到算子执行再到推理引擎,缺一不可:

1. **数据输入一致性 (3 项子配置)**
   - `no_shuffle: true` / `full_shuffle_instruction_dataset: false` —— 关 shuffle,保证数据读取顺序不变;
   - `no_shuffle: false` + `seed: 1234` —— 开 shuffle 但通过固定种子保证每次运行顺序一致;
   - `guarantee_order: true` (在 `rl_config` 中) —— 使能 TD (TransferDock)/TQ (TransferQueue) 数据通道保序;
   - DAPO 场景额外配置 `filter_groups_enable: false` —— 关闭动态采样以保证每轮迭代输入一致。

2. **算子 API 层确定性 (2 项开关)**
   - 在 `megatron_training` 参数中加入 `npu_deterministic: true`;
   - DPO 算法场景需在 DPO 启动脚本中额外设置环境变量 `export HCCL_DETERMINISTIC=True`。

3. **vLLM 推理层确定性 (1 项可选参数)**
   - 在 `sampling_config` 参数中加入 `seed: 1234`,仅在需要验证「断点续训」的确定性时设置,从头训练两次时无需设置。

原文明确警告:**训练前需删除数据集目录下后缀为 `.npy` 的缓存文件**,否则数据一致性可能失效。

---

## 【关键机制与数据】

### 工作原理链路

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  数据输入一致 │ →  │  数据通道保序  │ →  │  算子确定性   │ →  │  vLLM 确定性  │
│  (shuffle控制)│    │ (guarantee_  │    │ (npu_determ. │    │   (seed)     │
│ no_shuffle / │    │   order)     │    │  / HCCL_DET.)│    │   (可选)     │
│   seed 1234  │    │   TD/TQ      │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### 数据流关键说明 (原文)

- **shuffle 控制 (原文):** MindSpeed RL 提供 `no_shuffle` (默认 False,每个 epoch 进行 shuffle,可用 seed 控制 shuffle 随机性) 和 `full_shuffle_instruction_dataset` (默认 False,处理完所有 epoch 后是否对完整数据再 shuffle) 两个参数控制数据集输入。
- **数据通道保序 (原文):** DataStrategy 支持 TD (TransferDock) 与 TQ (TransferQueue) 两种数据通道;数据取出默认是乱序的,vLLM 推理等对输入顺序敏感,两次训练需保持一致顺序才能有相同输出;开启 `guarantee_order: true` 后将按实际数据顺序进行存取。
- **DAPO 场景 (原文):** DAPO 场景下使能确定性计算,应配置动态采样参数为 `false`,才能保证每轮迭代的数据输入是一致的 (`filter_groups_enable: false`)。
- **算子 API (原文):** `npu_deterministic: true` 使能算子 API 确定性计算;DPO 算法场景下还需在 DPO 启动脚本中加入环境变量开关 `export HCCL_DETERMINISTIC=True`。
- **vLLM 种子 (原文):** vLLM 中的种子参数用于控制各种随机数生成器的随机状态;如果是从头开始训练两次,仅开启前文的确定性计算方法即可;如需验证断点续训的确定性计算,需要设置该参数。

### 性能/效果数据

原文仅提供一张示意图 `image.png` (位于 `../../../docs/zh/figures/deterministic_computation/image.png`),用于直观展示「开启确定性计算后重复训练的 reward 分数完全一致」。**原文未提供具体的性能开销数字、reward 数值对比表或加速比数据**。

---

## 【表格解读】

**原文无表格**。

(文档以 YAML 代码块和文字说明组织内容,未出现任何 markdown 表格结构。)

---

## 【公式解读】

**原文无公式**。

(文档为工程配置指南,未涉及任何 LaTeX 数学公式或伪代码算法描述。)

---

## 【关联】

本文档在内部通过以下链路与其他模块/脚本耦合:

| 关联对象 | 路径 | 触发场景 | 关联性质 |
|---|---|---|---|
| DPO 训练启动脚本 | `../../../examples/dpo/dpo_trainer_qwen3_30b_a3b.sh` | 仅 DPO 算法场景 | 需在该脚本中追加环境变量 `export HCCL_DETERMINISTIC=True`,与 `npu_deterministic: true` 配合使用 |
| 示意图资源 | `../../../docs/zh/figures/deterministic_computation/image.png` | 文档展示 | 用于可视化 reward 分数一致性对比 |
| Megatron 训练配置 (yaml) | `megatron_training` 参数段 | 所有场景 | 容纳 `no_shuffle` / `full_shuffle_instruction_dataset` / `seed` / `npu_deterministic` 等参数 |
| RL 运行时配置 | `rl_config` 参数段 | 数据通道保序 | 容纳 `guarantee_order: true` |
| 采样配置 | `sampling_config` 参数段 | 断点续训验证场景 | 容纳 `seed: 1234` |

DPO 启动脚本链接是本文档中**唯一指向 examples 目录的内部链接**,与「DPO 算法特殊处理」这一支线配置形成对应——其他算法 (除 DAPO 特别提及外) 默认走通用配置流程。

---

## 【使用方法】

原文按「数据输入 → 算子确定性 → vLLM 确定性」三层给出完整配置,关键命令/配置项如下:

### Layer 1: 数据输入一致

**1.1 关闭 shuffle (保证数据完全有序)**

```yaml
# 训练前先删除数据集目录下后缀为 .npy 的缓存文件
no_shuffle: true
full_shuffle_instruction_dataset: false
```

**1.1' 开启 shuffle 但固定随机性**

```yaml
no_shuffle: false
seed: 1234  # 如果有就不用再加
full_shuffle_instruction_dataset: false
```

**1.2 使能数据通道保序 (TD/TQ)**

```yaml
# rl_config 参数段
guarantee_order: true
```

**1.3 DAPO 场景 (关闭动态采样)**

```yaml
filter_groups_enable: false
```

### Layer 2: 算子 API 确定性

**2.1 通用开关**

```yaml
# megatron_training 参数段
npu_deterministic: true
```

**2.1' DPO 算法额外开关 (命令)**

```bash
# 在 DPO 启动脚本 ../../../examples/dpo/dpo_trainer_qwen3_30b_a3b.sh 中追加
export HCCL_DETERMINISTIC=True
```

**2.2 vLLM 确定性 (可选,仅断点续训验证时使用)**

```yaml
# sampling_config 参数段
seed: 1234
```
