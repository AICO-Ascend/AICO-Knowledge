# FSDP2

> 仓 `mindspeed` · 路径 `docs/zh/features/fsdp2.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/fsdp2.md

# FSDP2 文档深度解读

---

## 【定位】

本文档针对 PyTorch 原生 FSDP（Fully Sharded Data Parallel）使用 FlatParameter 带来的"桶内单参数差异化操作困难、状态字典实现复杂且需额外通信"两大痛点，介绍 mindspeed 中集成的 FSDP2（基于沿 0 维分片的 DTensor 表示）替代方案，并给出完整的配置项、性能收益与使用边界说明。

---

## 【技术要点】

1. **核心改造：移除 FlatParameter，改用沿 0 维分片的 DTensor**
   原文明确指出"FSDP2 移除了 FlatParameter，采用沿 0 维分片的 DTensor 表示分片参数"，由此获得对单参数直接操作（冻结、精度转换）、免通信的分片状态字典、简化的初始化流程三项收益。

2. **环境变量约束**：`CUDA_DEVICE_MAX_CONNECTIONS=2`，原文注释"设置不能为 1"。

3. **互斥配置（必须关闭）**：开启 FSDP2 时需关闭分布式优化器及其相关配置，并关闭 Megatron 风格重计算三项参数 `--recompute-granularity`、`--recompute-method`、`--recompute-num-layers`。

4. **权重保存格式限制**：`--ckpt-format` 仅支持 `torch_dist` 或 `torch_dcp`；且 `--untie-embeddings-and-output-weights` 必须开启。

5. **重计算代价量化（原文给出）**：
   - 全层重计算：节省显存约 **30~40%**，吞吐下降约 **15~25%**；
   - 部分重计算：节省显存约 **15~25%**，吞吐下降约 **5~10%**。

6. **典型性能数据（原文给出）**：针对 Llama-7B，FSDP2 相对 FSDP1 **峰值内存降低 7%**，MFU 更高，且损失曲线一致。

---

## 【关键机制与数据】

### 1. 工作原理

- **参数分片**：FSDP2 不再把一组参数 flatten 成一个 FlatParameter 通信桶，而是把每个参数独立沿第 0 维切分成分片张量，由 DTensor 表示。这使得每个参数都可被单独寻址、单独冻结、单独转精度。
- **状态字典**：由于参数本身就是分片状态，免去了 FSDP1 中"先 gather 成 FlatParameter、再拆分回各参数"造成的额外通信，逻辑也大幅简化（原文描述 FSDP1 的状态字典逻辑"长达数千行代码且需要额外通信"）。
- **重计算**：在 FSDP2 模式下通过 `fsdp2_config.yaml` 的 `recompute_modules` 触发，底层基于 PyTorch 原生 `apply_activation_checkpointing` + `checkpoint_wrapper`，在前向时不保存中间激活，反向时重算。
- **通信开销来源（原文解释）**：若同时配置 `reshard_after_forward=True`，反向时还需重新获取分片参数，可能引入额外通信；这是重计算导致吞吐下降的原因之一。

### 2. 性能数据（仅写原文有的）

- **模型/基准**：Llama-7B
- **内存收益**：FSDP2 相对 FSDP1 峰值内存降低 **7%**
- **吞吐（MFU）**：FSDP2 高于 FSDP1（原文未给出具体百分比）
- **收敛**：损失曲线与 FSDP1 相同

### 3. 重计算使用边界（原文给出推荐/不推荐条件）

- **推荐开启**：训练过程中出现 OOM；激活显存占用超过总显存 50%；需要更大 batch size 或更长序列长度。
- **不推荐开启**：计算是瓶颈（NPU 利用率接近 100%）；通信是瓶颈（网络带宽已饱和）；模型较小或 batch size 较小且显存充足。

### 4. 数据流概览（基于原文配置项推断）

`sub_modules_to_wrap`（指定包装模块）→ 按 `sharding_size` 把参数沿 0 维切到多个 NPU → 前向计算时按需 all-gather（或保持分片由 `reshard_after_forward` 决定）→ 反向时 reduce-scatter 梯度（精度为 `reduce_dtype`，默认 fp32）→ 参数以 `param_dtype`（默认 bf16）存储 → 可选卸载到 CPU（`offload_to_cpu=True`，可配合 `pin_memory=True`）。

---

## 【表格解读】

**原文无表格**。原文以 YAML 代码块形式给出 `fsdp2_config.yaml` 的全部配置项（见下文【使用方法】），并未以 markdown 表格形式呈现参数表/性能对比/配置项。

---

## 【公式解读】

**原文无公式**。全文未出现任何 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

原文未提供内部链接（题目已注明"内部链接: (无)"），但从内容可识别出以下与其他模块/特性的耦合关系：

1. **分布式优化器**：开启 FSDP2 时必须关闭——两者在优化器状态/梯度分片职责上冲突。
2. **Megatron 风格重计算**：由 `--recompute-granularity` / `--recompute-method` / `--recompute-num-layers` 控制，与 FSDP2 的 `recompute_modules` **互斥**，二者只能选其一。
3. **`MegatronModule` 基类**：使用 `ckpt-format=torch_dist` 时，模型需继承 `MegatronModule` 或自定义实现 `sharded_state_dict()`；使用 `torch_dcp` 时需实现 `state_dict_for_save_checkpoint()`，且返回值需与 `model.state_dict()` 一致。
4. **`mindspeed_mm` 模型库**：示例中 `sub_modules_to_wrap`、`ignored_modules`、`recompute_modules` 的取值均通过 `mindspeed_mm.models.*` 的绝对路径引入（如 `mindspeed_mm.models.predictor.dits.sat_dit.VideoDiTBlock`、`mindspeed_mm.models.ae.base.AEModel`），说明 FSDP2 与 mindspeed 多模态模型库深度耦合。
5. **FSDP1（PyTorch 原生 FSDP）**：FSDP2 是其替代方案，原文给出 Llama-7B 上的对比基线。
6. **PyTorch 原生能力**：底层重计算依赖 `torch.nn.activation` 体系的 `apply_activation_checkpointing` + `checkpoint_wrapper`。

---

## 【使用方法】

### 命令行参数（原文给出）

```bash
export CUDA_DEVICE_MAX_CONNECTIONS=2 # 设置不能为 1
--use-torch-fsdp2 \
--fsdp2-config-path ./fsdp2_config.yaml \
--ckpt-format torch_dist \
--untie-embeddings-and-output-weights \
# 注意不能打开分布式优化器
```

### `fsdp2_config.yaml` 配置项（原文逐字保留）

```yaml
sharding_size: int # 分片组大小，表示每个参数分片组的NPU数量
sub_modules_to_wrap: Optional[Iterable[torch.nn.Module]] = None # 需要进行FSDP包装的模块类列表，需通过绝对路径引入：例如：mindspeed_mm.models.predictor.dits.sat_dit.VideoDiTBlock
reshard_after_forward: Union[bool, int] = True # 前向计算后立即重新分片参数
param_dtype: bf16 # 参数存储精度
reduce_dtype: fp32 # 梯度通信精度
cast_forward_inputs: bool = True # 自动转换前向输入到计算精度
ignored_modules: Optional[Iterable[torch.nn.Module]] = None # 排除FSDP管理的模块类列表, 需要通过绝对路径引入：例如：mindspeed_mm.models.ae.base.AEModel
offload_to_cpu: bool = False # 将权重，梯度以及优化器状态卸载到cpu
pin_memory: bool = True  # 只有当offload_to_cpu为True时才会生效
num_to_forward_prefetch: int  # 指定前向计算预取（forward prefetch）的层数，默认值为0
recompute_modules: Optional[Iterable[torch.nn.Module]] = None # 需要进行重计算的模块类列表，需通过绝对路径引入：例如：mindspeed_mm.models.predictor.dits.sat_dit.VideoDiTBlock
```

### 注意事项（原文逐条保留）

1. 开启 fsdp2 训练时，需关闭分布式优化器及其相关配置。
2. 开启 fsdp2 训练时，`ckpt-format` 仅支持 `torch_dist` 或 `torch_dcp`：
   - `torch_dist`：模型需继承 `MegatronModule` 或自定义实现 `sharded_state_dict()`；同时需保证模型中所有权重的 0 维 size 均 ≥ `sharding_size`。
   - `torch_dcp`：模型需继承 `MegatronModule` 或自定义实现 `state_dict_for_save_checkpoint()`，且其返回的权重字典需与 `model.state_dict()` 的返回值一致。
3. 开启 fsdp2 训练时，需关闭 Megatron 重计算相关配置：`--recompute-granularity`、`--recompute-method`、`--recompute-num-layers`。
