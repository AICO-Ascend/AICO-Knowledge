# CPU Offload

> 仓 `mindie-sd` · 路径 `docs/en/features/cpu_offload.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/cpu_offload.md

# 一体化深度解读: mindie-sd 异步 CPU Offload 特性文档

## 【定位】

这篇文档解决了 **昇腾 NPU 上 DiT (Diffusion Transformer) 模型因显存超限而无法单机推理的问题**, 通过**异步 Offload 机制**将部分 block 权重卸载至 CPU 内存, 在层间计算与权重搬运之间构建并行流水线, 将同步卸载模式下的 GPU 等待时间掩藏, 从而显著提升大模型推理时 NPU 的利用率。

---

## 【技术要点】

1. **问题背景 — 同步 Offload 的瓶颈**: DiT 推理要求所有 block 权重常驻 NPU 显存; 当模型超过单卡容量时, 同步模式下 GPU (此处代指 NPU) 算完一层即停下, 等待下一层权重从 CPU 搬运至 NPU, 大部分时间 GPU 处于空闲状态, 利用率极低。
2. **核心方案 — 异步 Offload (Asynchronous Offload)**: 通过**异步流水线设计**让计算与权重加载并行化 — 当 NPU 计算第 N 层时, 后台已开始搬运第 N+1 层权重; 第 N 层算完时, 第 N+1 层权重已就绪, **用计算时间掩盖搬运时间**。
3. **独立拷贝流 (Independent copy streams)**: 将 `h2d_stream` (Host to Device) 与 `d2h_stream` (Device to Host) 与 compute stream **分离**, 实现拷贝与计算并行执行。
4. **Forward pre-hook**: 在每个 block 执行前, **异步预加载**后续 block 的权重到 NPU。
5. **Forward hook**: 在每个 block 执行后, 将**已使用过的权重从 NPU 卸载**回 CPU 释放显存。
6. **保留 block 数量控制**: 通过 `min_reserved_blocks_count` 参数 (默认 `2`) 控制常驻 NPU 的 block 数量, 其余 block 在 CPU/NPU 之间动态换入换出。

---

## 【关键机制与数据】

### 工作原理 (异步流水线)

原文未提供量化性能数据 (如加速比、节省显存百分比), 但描述了完整的**四要素**协同机制:

| 机制组件 | 角色 | 时序行为 |
|---|---|---|
| `compute_stream` | 计算主轴 | 依次执行 layer N 的算子 |
| `h2d_stream` (Host→Device) | 上行搬运 | 在 layer N 计算期间**后台传输** layer N+1 权重至 NPU |
| `d2h_stream` (Device→Host) | 下行搬运 | layer N 计算完成后, **后行卸载**已用完的权重回 CPU, 释放显存 |
| `min_reserved_blocks_count` | 容量边界 | 控制 NPU 上常驻 block 数 (`默认=2`), 余下 block 进入换入/换出池 |

### 数据流示意 (基于原文描述还原)

```
时间轴 →
[layer 1 计算] | [layer 2 计算] | [layer 3 计算] | ...
     ↑                ↑                ↑
  d2h: layer 1 权重卸载  d2h: layer 2 权重卸载  d2h: layer 3 权重卸载
     (后台)             (后台)             (后台)

  h2d: layer 2 权重预加载  h2d: layer 3 权重预加载  h2d: layer 4 权重预加载
     (后台)             (后台)             (后台)
```

原文两个配图 (`figures/offload_process_image.png` 与 `figures/async_offload_image.png`) 分别对应**同步流程**与**异步流程**的对比, 文档未在正文给出图片的具体技术指标。

### 性能数据

**原文未给出量化性能指标** (如吞吐提升倍数、GPU idle ratio 等)。文档仅以定性描述 "**significantly reducing GPU idle time**" 阐述收益。

---

## 【表格解读】

### 原文参数表 (逐字还原)

| Parameter | Type | Required | Default | Description |
| ------ | ------ | ------ | -------- | ------ |
| `model` | `torch.nn.Module` | Yes | - | Target model to enable offloading |
| `blocks` | `ModuleList` | Yes | - | Sequentially ordered block list in the model |
| `min_reserved_blocks_count` | `int` | No | `2` | Number of blocks always kept on NPU |

### 逐行解读

- **`model` (`torch.nn.Module`, 必填, 无默认)**: 待启用 offload 的目标模型实例。`enable_offload` 会通过注册 forward pre-hook 与 forward hook 的方式**就地修改**该模型 (函数返回 `None`, 不返回新对象), 因此调用前需先实例化 DiT 模型。
- **`blocks` (`ModuleList`, 必填, 无默认)**: 模型内**按执行顺序排列**的 block 列表 (即 DiT 的 `model.blocks`)。注意此处限定类型为 `ModuleList`, 说明 offload 框架假设 blocks 在推理时按**线性顺序**逐个执行, 这与 DiT 同构 stacked-block 的拓扑相吻合; 若模型内 block 调用顺序非顺序 (如分支), 流水线预取可能错位。
- **`min_reserved_blocks_count` (`int`, 选填, 默认 `2`)**: 始终保留在 NPU 上的 block 数量。`2` 为官方推荐默认 — 留出 1 个当前正在计算的 block + 1 个已被 h2d_stream 预加载即将被消费的下一 block, 即可覆盖典型的"生产者—消费者"流水线, 同时为其他算子 (如 attention 中的 KV cache、layernorm 临时张量) 预留显存空间; 调大该值会减少换入换出次数 (降低搬运开销), 但会占用更多 NPU 显存。

---

## 【公式解读】

**原文无公式** (无 LaTeX 表达式、无伪代码算法公式)。文档以**自然语言 + API 签名**形式描述机制, 唯一接近伪代码的是 `enable_offload(model, blocks, min_reserved_blocks_count=2)` 这一函数签名, 已在上节表格中体现。

---

## 【关联】

文档内部仅显式关联 **一个**其他特性模块:

- **[DyEPLB.md](DyEPLB.md)** (原文 Notes 段落):
  - **关系类型**: **协同使用时的潜在冲突**。文档明确指出: *"When used together with [DyEPLB.md](DyEPLB.md), bandwidth contention may occur. Adjust execution timing as needed to avoid mutual blocking."*
  - **冲突根源**: DyEPLB (Dynamic Expert Parallel Load Balancer, 动态专家并行负载均衡) 在 MoE 场景下会主动**在 NPU 之间迁移专家权重**, 这同样需要占用 NPU↔NPU / NPU↔Host 的高速互联带宽。当 CPU Offload 的 h2d_stream/d2h_stream 与 DyEPLB 的权重迁移流**同时跑**时, 二者会**争抢总线带宽**, 导致双方有效带宽下降、流水线被互相阻塞。
  - **缓解措施**: 文档建议用户 "**Adjust execution timing**" — 即通过调度使两条数据通路在时间上错峰 (例如在 DyEPLB 平衡窗口内暂停 offload 预取, 或反之), 但**未提供具体的调度 API 或参数**, 需用户根据实际拓扑自行调优。

文档未涉及与其他子模块 (如 vLLM Omni 集成、Diffusers+CacheDit 集成、lightx2v) 的具体耦合关系, 故不展开臆测。

---

## 【使用方法】

### 1. 启用方式

通过 `mindiesd.offload.enable_offload` 一行 API 启用, **无需额外编译或环境变量**。

### 2. 完整代码模板 (原文 Usage Example)

```python
from mindiesd.offload import enable_offload

# Create model
model = DiTModel(...)

# Enable offload, keep 2 blocks on NPU
enable_offload(model, model.blocks, min_reserved_blocks_count=2)

# Move model to NPU
model.to("npu")

# Normal inference; framework automatically manages async weight swapping
with torch.no_grad():
    output = model(x)
```

### 3. 关键使用细节

- **调用顺序固定**: 必须先 `enable_offload(...)` 再 `model.to("npu")`。若先迁至 NPU 再注册 hook, 已驻留在 NPU 上的权重会在第一次 forward hook 触发时被错误卸载, 引发数据竞争。
- **blocks 必须按执行顺序传入**: API 假设 `blocks` 是顺序容器, 流水线预取依赖"第 i 个 block 接下来会执行第 i+1 个 block"这一前提。
- **推理时禁用梯度**: 文档示例使用 `torch.no_grad()`, offload 仅服务于前向推理, 暂未涉及训练场景。
- **与 DyEPLB 联用时**: 需自行调度执行时序以避免带宽争抢 (原文未给出具体调度 API, 仅给出原则性建议)。
- **配置项**: 仅 `min_reserved_blocks_count` 一个可调参数 (默认 `2`), 其余机制 (流的创建、hook 注册) 全部封装在 API 内部, 用户无需手动配置。

## 图文联合解读

- `offload_process_image.png`: **图解分析：**

1) **画面内容**：顶部为Layer0–3四层序列，下方斜向级联的四个任务块，每块含"loading"（粉色）与"computing"（绿色，"d"标识）两段；每个loading严格对齐对应层，块与块串行排列、无重叠。

2) **论证结论**：同步卸载模式下，loading与computing必须串行执行，层间存在明显空闲等待（图中块间阶梯间隔），GPU利用率低。

3) **与文档关系**：此图即文中"synchronous offload"流程示意，与下文async_offload_image形成对比，铺垫"异步流水线用并行掩盖传输时延、降低GPU空闲"的核心论点。
- `async_offload_image.png`: **1) 图中内容：** 顶层水平排列Layer0–Layer3四层（紫/青色方块）；下方以阶梯式错位排布"computing"（紫色）与"loading"（蓝/绿色）块，每层计算块紧邻下一层的加载块，呈流水线重叠布局。

**2) 技术结论：** 直观展示异步Offload通过并行流水线，使GPU在计算Layer N时，后台已并行搬运Layer N+1权重，计算与传输时间相互掩盖，大幅消除GPU空闲。

**3) 与文档关系：** 图证"独立copy流 + 前向pre-hook"机制带来的重叠收益，支撑"Asynchronous Offload显著降低GPU idle、提升利用率"的核心论点。
