# 负载均衡

> 仓 `drivingsdk` · 路径 `docs/zh/features/dataload_balance.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/drivingsdk/docs/zh/features/dataload_balance.md

# 文档深度解读：drivingsdk 负载均衡（dataload_balance）

---

## 【定位】

本文档系统描述 drivingsdk 中针对自动驾驶**分布式训练样本计算量差异显著**而设计的**负载均衡特性**，通过排序-分桶-随机化三步机制让各训练节点负载趋于一致，从而压缩通信等待开销、提升端到端训练性能。

---

## 【技术要点】

1. **问题根源**：自动驾驶场景中的点云、雷达、相机等多模态数据在不同道路场景下规模差异巨大；模型如 `QCNet`（按 `Agents` 数量）、`Deformable DETR`、`CenterPoint3D`（按 `voxel` 张量尺寸）的单样本计算量随场景剧烈波动，分布式默认按样本均匀分配会引发各节点负载不均与频繁通信等待。
2. **三步解决方案**：① **排序（sorting）**——按引发不均衡的主要瓶颈元素对样本排序；② **分桶（bucketing）**——按排序结果分桶，使相邻样本计算量相近；③ **分桶随机化与节点分发（bucket_arange）**——对桶随机化后再分发，兼顾训练随机性与节点间负载均衡。
3. **三组件协作架构**：入口包括 `DynamicDataset`（抽象类，提供 `sorting()` / `bucketing()`）、`DynamicSampler`（提供 `bucket_arange()`）、`DynamicTransforms`（动态预处理），分布在数据流中形成完整流水线。
4. **两套可继承实现**：分桶侧提供 `UniformBucketingDynamicDataset`（按 `num_bucket` 均匀分布，配 `DynamicDistributedSampler`）与 `CapacityBucketingDynamicDataset`（按 `bucket_capacity` 定容分桶，配 `ReplicasDistributedSampler`）；Sampler 子类在桶随机化基础上再叠加节点级切分与再随机化。
5. **CenterPoint3D 实例化路径**：通过 `get_voxel_number_from_mean_vfe(data_path, filename, sweeps, max_sweeps)` 获取点云 `voxel` 尺寸并写入序列化文件 → 让 `NuScenesDataset` 同时继承 `PointCloudDynamicDataset` → 以 `bucket_capacity=8` 完成分桶 → 将 `torch.utils.data.distributed.DistributedSampler` 替换为 `ReplicasDistributedSampler`。
6. **量化收益**：原文标注基于 CenterPoint3D 训练场景，相比未启用负载均衡的同配置训练，性能提升**约 18%**；同时强调该数值依赖具体数据分布与模型。

---

## 【关键机制与数据】

- **核心机制链**（原文整理）：
  - **排序**：`DynamicDataset.sorting()` 根据瓶颈元素对样本排序 → 输出"有序样本"。
  - **分桶**：`DynamicDataset.bucketing()` 按排序结果切分样本桶 → 输出"样本桶集合"。
  - **随机化**：`DynamicSampler.bucket_arange()` 处理桶级 + 桶内两级随机化 → 输出"随机化后的桶"。
  - **分发**：`DynamicSampler` 子类按节点数完成样本分配 → 输出"各节点的样本集"。
  - **预处理**：`DynamicTransforms` 在训练循环中做动态变换（如基于瓶颈元素的计算）→ 输出"可训练样本"。
- **两套配套关系**（避免混用，原文用 NOTE 强调）：
  - `UniformBucketingDynamicDataset` ↔ `DynamicDistributedSampler`：仅做桶随机化与桶内随机化，不做节点间切分。
  - `CapacityBucketingDynamicDataset` ↔ `ReplicasDistributedSampler`：在两轮随机化之上**再按节点数均匀切分并随机化**，适合桶大小可控的容量分桶场景。
- **训练-推理分支逻辑**（原文 CenterPoint3D 示例）：`if training` 时调用 `self.sorting()` 与 `self.bucketing(bucket_capacity=8)`；`else` 则置 `self.buckets = None`，避免在推理阶段引入额外逻辑。
- **性能数据**（原文）："基于负载均衡特性的训练性能较未使用负载均衡特性的同配置训练**提升约 18%**"，**以 CenterPoint3D 训练场景为基准**，建议以自身场景实测为准。
- **零侵入切入点**：通过 `mx_driving.dataset.utils.get_voxel_number_from_mean_vfe` 即可获取 `voxel` 张量尺寸，"用户无需对模型做过多侵入式修改"（原文表述）。

---

## 【表格解读】

### 表 1：`DynamicDataset` 抽象方法

> 原文逐字还原

| 抽象方法 | 作用 |
|----------|------|
| `sorting()` | 根据模型中造成负载不均衡瓶颈的主要元素，对数据集样本进行排序 |
| `bucketing()` | 根据`sorting()`结果，对数据集样本进行分桶 |

**逐行解读**：
- `sorting()`：是负载均衡特性的**第一步抽象**，要求用户根据具体模型的瓶颈元素（如 `voxel` 张量尺寸、`Agents` 数量）实现排序逻辑；不规定排序键，由模型特性决定。
- `bucketing()`：紧接 `sorting()`，输入是已排序样本，需根据所选子类决定如何分桶；本表强调两者的**输入-输出耦合关系**。

---

### 表 2：`DynamicDataset` 子类与配套 Sampler

> 原文逐字还原

| 子类 | 关键参数 | 分桶方式 | 配套Sampler |
|------|----------|----------|--------------|
| `UniformBucketingDynamicDataset` | `num_bucket`（分桶总量） | 样本按`sorting()`结果均匀分布到所有桶内 | `DynamicDistributedSampler` |
| `CapacityBucketingDynamicDataset` | `bucket_capacity`（桶容量） | 每桶分配`bucket_capacity`个样本 | `ReplicasDistributedSampler` |

**逐行解读**：
- `UniformBucketingDynamicDataset`：以"分桶总数"`num_bucket` 为参数，把按瓶颈元素排序后的样本**等量铺**到所有桶；适合数据规模确定、希望各桶大小均衡的场景；配套 `DynamicDistributedSampler`（不做节点切分）。
- `CapacityBucketingDynamicDataset`：以"单桶样本数"`bucket_capacity` 为参数，按桶**定容**装填——桶数量随数据规模自适应，是 CenterPoint3D 示例中使用的方案；配套 `ReplicasDistributedSampler`（附带节点级再切分）。

---

### 表 3：`DynamicSampler` 子类与适用场景

> 原文逐字还原

| 子类 | 随机化流程 | 适用场景 |
|------|-----------|----------|
| `DynamicDistributedSampler` | 1. 对样本桶进行随机化；<br>2. 在桶内对桶内数据随机化 | `UniformBucketingDynamicDataset`的分桶结果 |
| `ReplicasDistributedSampler` | 1. 对样本桶进行随机化；<br>2. 在桶内对桶内数据随机化；<br>3. 按节点数将桶内数据均匀分布到各节点并再次随机化 | `CapacityBucketingDynamicDataset`的分桶结果 |

**逐行解读**：
- `DynamicDistributedSampler`：两级随机化（桶级 + 桶内），**不**对桶内样本做节点间再切分；用于"均匀分桶"场景，分发由底层分布式机制承担。
- `ReplicasDistributedSampler`：在两级随机化之上**新增第 3 步**，按节点数均匀切分桶内数据并再次随机化，对应"容量分桶"场景；正是因为这一步的差异，使它能保证跨节点负载均衡。

---

### 表 4：组件协作流程

> 原文逐字还原

| 环节 | 组件 | 输出 |
|------|------|------|
| 排序 | `DynamicDataset.sorting()` | 有序样本 |
| 分桶 | `DynamicDataset.bucketing()` | 样本桶集合 |
| 随机化 | `DynamicSampler.bucket_arange()` | 随机化后的桶 |
| 分发 | `DynamicSampler`（子类实现） | 各节点的样本集 |
| 预处理 | `DynamicTransforms` | 可训练样本 |

**逐行解读**：
- 排序阶段由 `DynamicDataset` 的 `sorting()` 完成，输出有序样本（按瓶颈元素大小排列）。
- 分桶阶段紧接其上输出"样本桶集合"，结构上进入 Sampler 处理范围。
- 随机化由 `bucket_arange()` 抽象方法承载，输出可直接分发的桶。
- 分发阶段"子类实现"明确把节点级切分职责下放到 `ReplicasDistributedSampler`，输出"各节点的样本集"。
- 预处理阶段在训练循环内对样本做瓶颈元素相关变换，最终输出"可训练样本"进入下游训练。

---

### 表 5：相关源码路径

> 原文逐字还原

| 组件 | 源码位置 |
|------|----------|
| `DynamicDataset`及子类 | `mx_driving/dataset/` |
| `DynamicSampler`及子类 | `mx_driving/dataset/` |
| `DynamicTransforms` | `mx_driving/dataset/utils/dynamic_transform.py` |
| CenterPoint3D示例 | `model_examples/CenterPoint/` |

**逐行解读**：
- `DynamicDataset` 与 `DynamicSampler` 两大类及子类**共用** `mx_driving/dataset/` 这一目录，提示开发者修改时仅需聚焦于该路径。
- `DynamicTransforms` 单独落到 `mx_driving/dataset/utils/dynamic_transform.py`，是 CenterPoint3D 示例中 `get_voxel_number_from_mean_vfe` 等关键函数的所在地。
- CenterPoint3D 示例仓库位于 `model_examples/CenterPoint/`，与本文档结尾"完成上述修改后，模型即可正常训练"指向的训练入口互相对应。

---

## 【公式解读】

**原文无公式**。

（虽未出现显式数学公式，但原文隐含的等价表述为：每节点负载 ≈ 每个分到的桶内"瓶颈元素量的近似相等的小集合"，这是排序→定容分桶→节点均匀切分三层操作共同逼近的目标。）

---

## 【关联】

- **上游关联（数据准备）**：依赖按 `model_examples/CenterPoint/README.md` 中"准备数据集"一节生成的序列化文件；序列化阶段需通过 `mx_driving.dataset.utils.get_voxel_number_from_mean_vfe(data_path, filename, sweeps, max_sweeps)` 写入 `info["voxel_num"]` 字段，作为后续排序依据。
- **下游关联（训练执行）**：完成示例代码改造后，训练入口回到 `model_examples/CenterPoint/README.md`（用户提供的内部链接：`../../../model_examples/CenterPoint/README.md`），由该 README 继续承载训练脚本、配置与启动命令。
- **横向类比模型**：原文背景还提及 `QCNet`（按 `Agents` 数量负载不均）与 `Deformable DETR`，提示同一套 `DynamicDataset` / `DynamicSampler` 抽象也可迁移到**任意"瓶颈元素驱动训练负载不均"的模型**，只需在各自 `sorting()` 中替换瓶颈度量。
- **组件内耦合**：跨章节锚链在原文多处呈现——例如"为何选用 CenterPoint3D"→"上节"、"实现分桶随机化"→"组件二：DynamicSampler"、"效果验证"→"组件一 / 组件二"，揭示了文档将**机制说明 ↔ 示例实现 ↔ 效果验证**串成一条闭环叙述。

---

## 【使用方法】

以下要点均严格基于原文"使用方法示例"与"效果验证与注意事项"两节：

1. **确认瓶颈元素**：对 CenterPoint3D，原文明确为"点云转换获得的 `voxel` 张量尺寸"。
2. **生成带瓶颈元素的序列化文件**：在数据准备代码中加入
    ```python
    from mx_driving.dataset.utils import get_voxel_number_from_mean_vfe
    voxel_num = get_voxel_number_from_mean_vfe(data_path, ref_sd_rec['filename'], sweeps, max_sweeps)
    info["voxel_num"] = voxel_num
    ```
3. **数据集类改造**：修改 `pcdet/datasets/nuscenes/nuscenes_dataset.py`，让 `NuScenesDataset` 同时继承 `PointCloudDynamicDataset`；训练阶段调用 `self.sorting()` 与 `self.bucketing(bucket_capacity=8)`；非训练阶段置 `self.buckets = None`。
4. **Sampler 替换**：将 `pcdet/datasets/__init__.py` 中原 `torch.utils.data.distributed.DistributedSampler(dataset)` 替换为
    ```python
    from mx_driving.dataset import ReplicasDistributedSampler
    sampler = ReplicasDistributedSampler(dataset)
    ```
    （因为示例中使用了**容量分桶** `bucket_capacity=8`，所以**必须**配套使用 `ReplicasDistributedSampler`。）
5. **配套关系约束**（原文强调）："分桶方式与 Sampler 需按组件一与组件二的配套关系选用，**混用可能导致负载均衡失效或数据分布异常**"。
6. **精度影响（原文声明）**：负载均衡"改变的是样本采样顺序与分配方式，**不改变数据内容与模型结构**"；出现收敛异常时建议先核对 Sampler 与分桶参数的配套关系。
7. **详细训练步骤**：原文指向 [CenterPoint3D模型](../../../model_examples/CenterPoint/README.md)，即 `../../model_examples/CenterPoint/README.md`，由该 README 提供启动训练命令等其余细节——**原文未在本文件内列出具体启动命令**。
