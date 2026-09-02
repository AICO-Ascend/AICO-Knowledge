# 数据负载均衡(数据分桶重排序)

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/bucket_reordering.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/bucket_reordering.md

# mindspeed-mm「数据负载均衡(数据分桶重排序)」特性深度解读

---

## 【定位】

本文档针对多模态大模型训练中**因图/视频 token 数量差异大导致 micro-batch 内 padding 浪费严重、DP rank 间负载不均、训练吞吐受限于最慢 rank**的问题，给出数据分桶 (`data_bucketing_img`) 与数据重排序 (`data_reordering_img`) 两类负载均衡方案的选型依据、配置方法及最佳实践。

---

## 【技术要点】

1. **两类负载均衡策略**：性能优先的 `data_bucketing_img`（默认）与精度优先的 `data_reordering_img`；两者通过 `priority_mode` 字段切换，本质是「按 token 数分桶」与「在分桶基础上再做均匀重排」的关系。
2. **触发入口**：在 `dataloader_param` 下将 `sampler_type` 设为 `BucketBatchSampler` 才会启用分桶逻辑；该 sampler 是承载 `priority_mode` 的运行容器。
3. **Qwen2VL 标配模板**：`examples/qwen2vl/data_2b.json` 中的 `dataloader_param` 给出可直接复制的 JSON 配置块，组合参数为 `BucketBatchSampler` + `data_reordering_img` + `drop_last=true` + `data_sharding=true` + `shuffle=true`。
4. **分布式耦合点**：`data_sharding=true` 用于分布式训练数据分片；`drop_last` 用于丢弃尾批不完整 batch；二者与 `BucketBatchSampler` 共同决定 DP rank 实际看到的样本分布。
5. **场景化取舍规则**：原文给出"性能优先/精度敏感/长视频/混合分辨率"四种场景的最佳实践，且明确 `data_reordering_img` 比 `data_bucketing_img` 存在**少量额外计算开销**。
6. **作用域与限制**：当前已支持 Qwen2VL，其他模型的支持正在扩展；启用后**原始数据顺序被改变但不影响收敛性**（原文表述）。

---

## 【关键机制与数据】

**问题根源（原文:）**
> "在多模态模型训练中，不同样本的图片/视频 token 数量差异较大"
> 直接后果：①同一 micro-batch 内样本长度差异大，padding 浪费严重；②不同 DP rank 之间计算负载不均衡，出现快慢卡等待；③训练吞吐量受限于最慢的 DP rank。

**连锁效应（原文:）**
- **梯度聚合通信效率低下**：先完成的 rank 需等待最慢 rank，AllReduce 阶段存在大量空闲等待，通信-计算重叠率低。
- **显存利用率低**：需对齐 micro-batch 内最长样本，短样本产生大量 padding token，占显存但不产生有效梯度。
- **训练步间耗时波动大**：不同 batch 样本长度分布不一致，导致各步耗时差异大、整体吞吐不稳定。

**机制闭环（原文:）**
> "数据分桶重排序通过对数据进行智能分组和排序，使同一 batch 内的样本长度更加接近，同时使不同 DP rank 之间的计算量更加均衡，从而提升训练效率。"

**两方案逻辑分层（原文:）**
- `data_bucketing_img`：按图片 token 数分桶 → 同桶样本组成 batch → 减少 padding。
- `data_reordering_img`：在分桶基础上再做数据重排序 → 让训练数据的**分布**更均匀，避免因数据顺序导致的训练偏差。

**性能相关数据（原文:）**：原文未给出量化指标（如 padding 减少比例、吞吐提升幅度、耗时下降百分比等），仅以定性方式描述"大幅减少 padding 浪费"、"少量额外计算开销"等效果。

**DP 维度的差异（原文:）**
> "在 DP=1 的单卡场景下，分桶主要减少 padding；在 DP>1 时，还能改善负载均衡。"
> 即：分桶的两类收益（减 padding + 均衡负载）随并行度扩大而叠加。

---

## 【表格解读】

### 表格 1：方案对比表（原文逐字还原）

| 方案 | priority_mode 配置 | 优先级 | 特点 |
|------|-------------------|--------|------|
| 数据分桶 | `data_bucketing_img`（默认） | 性能 | 减少 padding，提升训练吞吐量 |
| 数据重排 | `data_reordering_img` | 精度 | 在分桶基础上保证数据分布均匀性 |

**逐行解读：**
- **数据分桶行**：默认走 `data_bucketing_img`，定位为性能优先；其特点是直接削减 padding、提升吞吐——对应解决"显存利用率低"与"吞吐受限于最慢 rank"。
- **数据重排行**：通过 `data_reordering_img` 触发，定位为精度优先；它在分桶之上再做一次分布均匀性约束，回应"步间耗时波动大"与"训练偏差"问题；代价是额外计算开销（原文已警示）。

### 表格 2：配置参数说明表（原文逐字还原）

| 参数 | 说明 | 取值 |
|------|------|------|
| `sampler_type` | 采样器类型，启用分桶需设置为 `BucketBatchSampler` | `BucketBatchSampler` |
| `priority_mode` | 负载均衡策略 | `data_bucketing_img`（默认，性能优先）/ `data_reordering_img`（精度优先） |
| `drop_last` | 是否丢弃最后一个不完整的 batch | `true` / `false` |
| `data_sharding` | 是否对数据进行分片（分布式训练时建议开启） | `true` / `false` |
| `shuffle` | 是否在每个 epoch 开始时打乱数据顺序 | `true` / `false` |

**逐行解读：**
- **`sampler_type`**：是启用整套机制的"开关"，未设置成 `BucketBatchSampler` 则分桶逻辑根本不生效。
- **`priority_mode`**：决定走分桶还是分桶+重排路径，与表格 1 一一对应。
- **`drop_last`**：控制是否丢弃尾批；为追求 rank 间均衡，建议保持 `true`（与 Qwen2VL 示例一致）。
- **`data_sharding`**：分布式训练建议开启，原文明确"建议开启"，并与 `BucketBatchSampler` 配合实现跨 rank 样本均衡分发。
- **`shuffle`**：epoch 级打乱，避免长期训练时同一批样本反复出现，与 `data_reordering_img` 的"分布均匀"诉求方向一致。

---

## 【公式解读】

**原文无公式。**

（注：原文未给出 token 数分桶阈值、分桶 size、重排调度策略等任何形式化表达式或伪代码。）

---

## 【关联】

> **内部链接标注：原文未提供任何内部链接（用户标注为「无」），故此处仅梳理原文文字层面提及的横向关系。**

- **与 Qwen2VL 模型的耦合**：文档明确"当前已支持 Qwen2VL 模型，其他模型的支持正在扩展中"，并以 `examples/qwen2vl/data_2b.json` 为唯一配置范例，说明该特性目前在 Qwen2VL 路径下落地最完整。
- **与 dataloader_param 的耦合**：特性需通过 `dataloader_param` 下的 `sampler_type` + `priority_mode` 联合启用，属于 dataloader 层而非模型层或并行策略层。
- **与 DP 并行策略的协同**：原文强调在 `DP>1` 时除减少 padding 外还能改善负载均衡，因此与分布式训练框架的 DP 维度强相关；`data_sharding=true` 是该协同在 dataloader 侧的对应配置。
- **与训练范式的关联**："长视频训练"与"混合分辨率数据"被点名为高收益场景，提示该特性对**多模态生成 / 多模态理解**两条主线下的高变长样本任务尤为重要。
- **与上下游**：原文未提及与具体算子、加速库、通信库（如 AllReduce 实现）的对接细节，亦未引用任何其他特性文档。

---

## 【使用方法】

### 1. 启用条件（原文有）
- 必须将 `dataloader_param.sampler_type` 设为 `BucketBatchSampler`；
- 再通过 `dataloader_param.priority_mode` 在 `data_bucketing_img`（默认）与 `data_reordering_img` 之间二选一。

### 2. Qwen2VL 配置示例（原文逐字还原）

在 `examples/qwen2vl/data_2b.json` 中，修改 `dataloader_param`：

```json
"dataloader_param": {
    "dataloader_mode": "sampler",
    "drop_last": true,
    "sampler_type": "BucketBatchSampler",
    "priority_mode": "data_reordering_img",
    "collate_param": {
        "model_name": "qwen2vl",
        "ignore_pad_token_for_loss": true
    },
    "pin_memory": true,
    "data_sharding": true,
    "shuffle": true
}
```

> 该示例采用了**精度优先**模式（`data_reordering_img`）；若切换为性能优先，将 `priority_mode` 改为 `data_bucketing_img` 即可。

### 3. 选型决策（原文"最佳实践"逐条还原）
1. 性能优先 → 使用默认 `data_bucketing_img`；
2. 精度敏感 → 使用 `data_reordering_img`；
3. 长视频训练 → 分桶效果尤为显著；
4. 混合分辨率数据 → 强烈建议启用分桶。

### 4. 注意事项（原文逐条还原）
- 仅 Qwen2VL 已支持，其他模型支持扩展中；
- 启用后数据原始顺序会被改变，但不影响训练收敛性；
- `data_reordering_img` 比 `data_bucketing_img` 有少量额外计算开销；
- `DP=1` 时收益主要为减少 padding；`DP>1` 时收益叠加为减 padding + 负载均衡。

### 5. 未涉及内容
- 原文未涉及具体命令行调用方式、环境变量、CLI flag；
- 原文未提供 `BucketBatchSampler` 的实现位置、桶数 / 桶大小等内部参数；
- 原文未提供性能基准数据、复现脚本或评测配置。
