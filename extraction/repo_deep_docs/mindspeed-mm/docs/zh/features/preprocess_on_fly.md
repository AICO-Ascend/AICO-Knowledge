# Preprocess On Fly

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/preprocess_on_fly.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/preprocess_on_fly.md

# Preprocess On Fly 文档深度解读

## 【定位】
本文档针对多模态训练场景中非流式数据加载默认方案（`dataset.map` 全量预处理 + Arrow 落盘）带来的**启动慢、磁盘占用高**两大瓶颈，给出 **Preprocess On Fly 在线预处理策略**的能力描述、机制原理与启用方式，并明确其仅在非流式 + HuggingFace 数据集场景下生效。

---

## 【技术要点】

1. **默认方案的两个具体瓶颈**
   - 启动慢：大规模数据集全量预处理耗时高，期间可能因处理过久导致**超时报错退出**
   - 磁盘占用高：多模态数据（图像、视频）单条样本预处理后全量落盘占用大量磁盘空间

2. **在线预处理的两个核心机制**
   - **按需执行**：将 `preprocess_func` 通过 `set_transform` 挂载为 dataset 的 transform，**在训练过程中每次读取 batch 时才触发预处理，不落盘**
   - **并行预取**：配合 DataLoader 的 `num_workers` 多进程预取机制，**掩盖预处理耗时**

3. **生效范围严格限定**
   - 仅在**非流式数据加载场景**（`streaming: false`）下
   - 仅针对 **huggingface 数据集类型**生效
   - 由 `preprocess_on_fly` 参数控制
   - 当前在 **Kimi-K2.5 及 Qwen3.5 系列模型**中**已默认开启**

4. **关键路径替换关系**
   - 开启 `preprocess_on_fly` → 走 **`set_transform`** 路径
   - **不调用 `dataset.map`**
   - `preprocessing_batch_size` 和 `preprocessing_num_workers` **不生效**

5. **并发参数行为约束**
   - `num_workers=0` 时预处理在**主进程同步执行，会阻塞训练**
   - 需设置 `num_workers>0`（示例中为 `8`）以实现多进程预取掩盖耗时

---

## 【关键机制与数据】

### 工作原理（原文核心描述整合）

- **默认路径（非开启 Preprocess On Fly 时）**：启动阶段通过 `dataset.map` 对**全量数据集**执行预处理 → 结果**落盘到 Arrow 缓存** → 训练时读取 Arrow。
- **Preprocess On Fly 路径（开启后）**：通过 `set_transform` 把 `preprocess_func` **挂载**为 dataset 的 transform → **训练过程中每次读取 batch 时才触发**预处理 → **不落盘** → 配合 DataLoader 多进程预取 (`num_workers`) 并行执行预处理与训练消费。

### 性能/收益（原文定性表述，无具体数字）

- 原文描述的收益为定性表达：
  - 缓解"启动慢"——避免启动阶段全量预处理导致的**超时报错退出**
  - 缓解"磁盘占用高"——多模态样本**不落盘**
  - 训练时延——通过 `num_workers` 多进程**掩盖预处理耗时**（原文未给具体吞吐/加速比数字）

### 性能数据
> 原文未给出具体的加速比、吞吐量、磁盘节省量等量化性能数据。

---

## 【表格解读】

**原文无表格。**

原文仅含一段 YAML 配置代码示例（非参数表、非性能对比表、非配置项矩阵），因此不存在可逐字还原的结构化表格。

---

## 【公式解读】

**原文无公式。**

原文未出现任何 LaTeX 公式或伪代码形式的算式；其机制描述以文字 + YAML 配置块形式呈现。

---

## 【关联】

原文**未提供文末内部链接**，因此无法从该文档内显式抽取上下游链接。但基于文档原文可梳理以下**功能性关联**：

- **与数据加载模式的关系**：`preprocess_on_fly` 是 `streaming: false`（非流式）场景下的替代/补充机制；若切换到 `streaming: true`，该参数不生效。
- **与 HuggingFace 数据集类型的耦合**：该特性**仅**对 huggingface 数据集类型生效，与其他数据集类型不互通。
- **与默认 `dataset.map` 预处理路径的互斥**：开启后直接走 `set_transform`，**跳过** `dataset.map`、`preprocessing_batch_size`、`preprocessing_num_workers` 这条全量预处理链路——三者在开启状态下"不生效"。
- **与模型默认配置的关联**：在 **Kimi-K2.5 与 Qwen3.5 系列**模型中已被默认开启，暗示该特性是这两条模型训练流水线的**默认配置项**。
- **与 DataLoader 多进程的依赖**：依赖 `num_workers>0` 才能发挥"掩盖预处理耗时"的效果；若 `num_workers=0`，会退化为阻塞执行。

---

## 【使用方法】

### 启用方式（原文 YAML 示例逐字还原）

```yaml
basic_parameters:
  streaming: false  # 需关闭流式加载
  preprocess_on_fly: true

dataloader_param:
  num_workers: 8  # 通过多进程预取掩盖预处理耗时
```

### 参数详解（原文逐条）

- **`streaming`**：流式加载开关，`preprocess_on_fly` 仅在 `streaming: false` 时生效，该参数**默认关闭**。
- **`preprocess_on_fly`**：是否在训练时进行预处理，**默认 `false`**。开启后走 `set_transform` 路径，不调用 `dataset.map`，`preprocessing_batch_size` 和 `preprocessing_num_workers` **不生效**。
- **`num_workers`**：DataLoader 的 worker 进程数，通过多进程预取掩盖预处理耗时。`num_workers=0` 时预处理在主进程同步执行，**会阻塞训练**。

### 启用前提（原文约束汇总）
1. 数据加载场景必须是**非流式**（`streaming: false`）；
2. 数据集类型必须是 **huggingface** 数据集；
3. 若希望获得"掩盖耗时"的收益，需设置 `num_workers > 0`。
