# 训练阶段评估验证功能

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/validation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/validation.md

# 一体化深度解读：训练阶段评估验证功能

## 【定位】

这篇文档解决在长时间大规模分布式训练中"仅凭训练集 loss 无法及时发现过拟合"的问题，描述 MindSpeed-MM 在训练流程中周期性执行验证集 loss 评估的能力，并同时给出 FSDP2（新增）与 MCORE/Megatron（原有）两条后端链路的配置与使用方法。

## 【技术要点】

1. **双后端并行支持**：FSDP2 是本次新增验证能力（使用 `val_dataset_param`、`val_interval` 等新字段），MCORE（Megatron）沿用原有 `--eval-interval`、`--eval-iters` 以及数据集内的 `val_dataset` 字段，两套入口并存于同一篇文档。
2. **验证触发机制**：训练达到指定间隔后，框架自动暂停训练分支，将模型切换至 `eval()` 状态，遍历验证集计算 loss，验证结束后恢复训练状态继续训练——即"训练—暂停—eval—恢复"的串行切模流程。
3. **FSDP2 YAML 锚点复用**：`val_dataset_param` 通过 YAML 锚点 `&TRAIN_DATASET_PARAM` / `<<: *TRAIN_DATASET_PARAM` 复用 `dataset_param`，仅覆盖 `dataset` 与 `cache_dir` 两个差异字段，避免重复配置。
4. **间隔开关语义**：`val_interval` 默认值为 `0`，表示关闭验证；只有大于 `0` 时才开启验证；开启后若未配置验证集，训练启动阶段直接报错——将"开关状态"与"数据集就绪"做强制耦合。
5. **dataloader 隔离**：验证 dataloader 关闭 shuffle、并使用独立 seed，**确保不影响训练 dataloader 的采样顺序**，避免验证流程污染训练随机性。
6. **能力边界**：当前仅支持 loss 验证，要求模型 forward 返回 loss 且验证集 batch 格式与训练集一致；**不支持生成式评测和任务指标评估**。

## 【关键机制与数据】

**整体工作流（训练—验证—训练三阶段切换）：**
- 训练流程持续推进 → 计数器到达 `val_interval`（FSDP2 单位 step / MCORE 单位 iteration）→ 框架暂停训练分支 → `model.eval()` 切换状态 → 遍历验证集计算 loss → 训练状态恢复 → 继续训练。该流程在原文以"暂停训练分支，将模型切换到 `eval()` 状态"+"验证结束后恢复训练状态继续训练"两句话明确描述。

**FSDP2 dataloader 隔离设计（原文）：** "验证 dataloader 会关闭 shuffle，并使用独立 seed，避免影响训练 dataloader 的采样顺序。"——这是与一般训练脚本直接共用 dataloader 的关键差异点，是防止验证采样污染训练随机状态的核心保障。

**MCORE 字段映射（原文）：** 验证集在数据配置 `basic_parameters` 中通过 `val_dataset` 显式配置，并可由 `val_max_samples` 限制样本数；该字段命名空间与训练 `dataset` 同级而非独立 `val_dataset_param` 块。

**性能/数据数字（原文仅出现的）：**
- FSDP2 示例：`val_interval: 1000`、`val_micro_batch_size: 1`、训练 `micro_batch_size: 4`。
- MCORE 示例：`--eval-interval 1000`、`--eval-iters 10`。
- 验证开销相关原文未给出具体性能/耗时数据。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **FSDP2 ↔ MCORE 两条后端链路并列**：文档将"新增能力"与"已有能力"在同一篇说明中并列，配置入口完全不同——FSDP2 用 YAML 字段（`val_dataset_param`、`val_interval`、`val_micro_batch_size`），MCORE 用命令行参数（`--eval-interval`、`--eval-iters`）加数据 JSON 内 `val_dataset`/`val_max_samples`，使用者需根据所选后端走对应配置路径。
- **FSDP2 模型支持 ↔ Qwen3.5 实现**：FSDP2 当前"部分模型可参考 Qwen3.5 的实现方式"（指向 `examples/qwen3_5/qwen3_5_35B_config.yaml`），其余模型支持情况以具体实现为准——即该能力的模型覆盖是渐进式的，Qwen3.5 是当前可参考的实现范例。
- **MCORE 模型支持 ↔ Qwen2.5VL 实现**：MCORE 侧 validation 能力依赖具体模型训练链路实现，"部分模型可参考 Qwen2.5VL 的实现方式"，同样以具体实现为准——表明两条后端的"模型可用清单"是分别维护、各自以一个代表模型为参考的。
- **与训练主流程的耦合点**：验证依赖"模型 forward 返回 loss"以及"验证集 batch 格式与训练集一致"——这意味着该特性并非独立模块，而是嵌入训练主循环并对数据集 collator 与模型前向签名有耦合要求。
- **功能边界 ↔ 生成式评测**：文档明确"不支持生成式评测和任务指标评估"，将本特性定位为**训练过程 loss 监控**而非完整 evaluation 套件，潜在后续能力（生成式、指标类）属于本文之外的范畴。

## 【使用方法】

**FSDP2（native FSDP2）路径**——在模型 YAML 配置文件中：

```yaml
data:
  dataset_param: &TRAIN_DATASET_PARAM
    dataset_type: huggingface
    basic_parameters: &TRAIN_BASIC_PARAMETERS
      dataset_dir: ./data
      dataset: ./data/train.json
      cache_dir: ./cache_dir/train

  val_dataset_param:
    <<: *TRAIN_DATASET_PARAM
    basic_parameters:
      <<: *TRAIN_BASIC_PARAMETERS
      dataset: ./data/val.json
      cache_dir: ./cache_dir/val

training:
  micro_batch_size: 4
  val_interval: 1000
  val_micro_batch_size: 1
```

字段说明（原文逐字）：
- `data.val_dataset_param`：验证集配置，结构与 `data.dataset_param` 一致，可通过 YAML 锚点复用训练集配置，仅覆盖验证集路径、缓存路径等差异字段。
- `training.val_interval`：验证间隔，单位为 step。默认 `0`，表示关闭验证；大于 `0` 时开启验证。
- `training.val_micro_batch_size`：验证阶段的 micro batch size。未设置时默认复用 `training.micro_batch_size`。

约束：验证开启后，如果未配置验证集，训练启动阶段会报错。可参考 `examples/qwen3_5/qwen3_5_35B_config.yaml`；其他模型支持情况以具体实现为准。

**MCORE（Megatron）路径**——shell 脚本 `OUTPUT_ARGS`：

```shell
OUTPUT_ARGS="
    ...
    --eval-interval 1000 \
    --eval-iters 10 \
    ...
"
```

- `--eval-interval`：验证间隔，单位为 iteration。
- `--eval-iters`：每次验证执行的迭代次数。

数据集 JSON：

```json
{
  "dataset_param": {
    "basic_parameters": {
      "dataset": "./data/train.json",
      "val_dataset": "./data/val.json",
      "val_max_samples": null
    }
  }
}
```

- `val_dataset`：显式指定验证集路径。
- `val_max_samples`：限制验证集样本数，常用于调试。

模型支持参考 Qwen2.5VL 的实现方式，其他模型支持情况以具体实现为准。

**通用约束（原文）：** 当前功能仅支持训练过程中的 loss 验证，要求模型 forward 返回 loss，且验证集 batch 格式与训练集一致；当前不支持生成式评测和任务指标评估。
