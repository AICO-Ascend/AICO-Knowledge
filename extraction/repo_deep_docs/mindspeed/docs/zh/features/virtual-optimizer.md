# virtual-optimizer

> 仓 `mindspeed` · 路径 `docs/zh/features/virtual-optimizer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/virtual-optimizer.md

# mindspeed — `virtual-optimizer` 特性文档深度解读

---

## 【定位】

本文档描述 mindspeed 在昇腾 NPU 上**借助昇腾驱动的虚拟内存原生能力，将优化器（Adam 家族）的一二阶动量（`exp_avg` / `exp_avg_sq`）实际内存在 Host 侧、地址映射在 device 侧**的低侵入（"一行代码"）显存节省方案，用以缓解大集群训练中 Pipeline Parallelism（PP）靠前 stage 的显存压力。

---

## 【技术要点】

1. **核心 API 替换**：将优化器状态构造由 `torch.zeros_like(p, memory_format=torch.preserve_format)` 替换为 `torch_npu.empty_with_swapped_memory(p.size(), device=p.device)`，即可把 `exp_avg`、`exp_avg_sq` 张量落到 Host 虚拟内存。
2. **触发动机**：大 PP 时前几个 stage 显存压力大；增大梯度累积（gradient accumulation）后，"优化器一二阶动量被 swap"这一段开销占比可忽略，因此可以放心地把动量搬到 Host 侧。
3. **触发方式（命令行）**：
   - `--virtual-optimizer all`：对所有 PP stage 全部 Swap 一二阶动量。
   - `--virtual-optimizer <浮点GB>`：每个 PP stage Swap 同样大小的显存，例如 `--virtual-optimizer 2.0` ≈ 每 stage 2 GB。
   - `--virtual-optimizer <g1 g2 g3 g4 ...>`：每个 PP stage Swap 不同大小的显存，例如 `--virtual-optimizer 6 5 4 3`。
4. **驱动限制与配套工具**：申请为虚拟内存的张量**不能被设备端直接访问**，故不能直接 `print` / `save`。文档给出两个 wrapper：
   - `swap_tensor_copy_wrapper`：包装 `Tensor.copy_`，区分 dst/src 是否 swap、是否同设备，再做 `fill_(1).mul_(src)` 规避随路计算。
   - `swap_tensor_func_wrapper`：包装 `cpu` / `npu` / `clone` / `detach`，先把 swap tensor 拷到普通张量，再走原函数；detach 还会给结果挂上 `swap_tensor=True` 标记。
5. **推荐 CPU 绑核配置**：`export CPU_AFFINITY_CONF=1,lazy_bind:0`——粗粒度绑核到 NPU 对应的 NUMA CPU 核心，避免跨 NUMA 内存访问并降低调度开销（针对虚拟内存走 Host 路径后 CPU 介入更频繁的场景）。
6. **适配范围**：与现有分布式优化器逻辑（含 `overlap-grad-reduce` / `overlap-param-gather` 等通信并行）"解耦"——不侵入分布式优化器代码本体，因此不需要重做多流同步。

---

## 【关键机制与数据】

### 工作原理（原文叙述，原文标注）

- **原文**："借助昇腾驱动的虚拟内存原生能力，可以实现申请一个实际内存在 Host 侧，但内存地址可被映射在 device 上的张量，并且该张量可参与绝大多数 NPU 算子计算（除涉及随路计算的算子）"——即 swap 后的动量张量在 device 侧仍持有地址，可直接被大多数 NPU 算子读写，无需显式 D2H / H2D 搬运。
- **原文**："申请的 Host 虚拟内存无法实现随路计算（没有硬件随路计算单元）"——这是该方案**唯一的能力边界**：涉及随路计算（attached computation）的算子无法使用该路径，需经 wrapper 拷贝回普通 device 张量。

### 性能来源（原文给出的"为什么更快"的两条理由）

- **原文**："虚拟内存能够节省两次 UB 与 HBM 的搬运时长，直接从硬件执行访问。"——对比传统 Swap 路径中先把数据从 HBM 拷到 UB、再从 UB 经 DMA 落 Host、再回拷的两段搬运，虚拟内存方案省掉了中间步骤。
- **原文**："基于虚拟内存的搬运可以利用算子本身的流水机制（MTE2/MTE3/Vector），与计算产生指令级的并行掩盖，避免引入额外的流同步性能与内存的开销（如 Swap 引入的多流）。"——即硬件/驱动在算子内部自然完成跨域访存，复用算子既有流水线，不需要额外 stream 同步。

### 性能数据

- **原文未提供任何量化指标**（无时间、无吞吐数字、无显存节省数字）。原文对优势/劣势的描述均为定性结论。

---

## 【表格解读】

**原文无表格**。

文档中唯一的"对比"元素是一张示意图 `figures/virtual-optimizer.png`，正文以"下图为图示对比说明"引出，作者以文字给出了虚拟内存方案相对于纯 Swap 方案的优势/劣势对比，但未给出表格形式的逐项参数。

---

## 【公式解读】

**原文无公式**。

文档中只有一段 Python 代码片段（替换 `torch.zeros_like` 为 `torch_npu.empty_with_swapped_memory`）和两个 wrapper 函数定义，不含任何数学公式或伪代码形式算法表达式。

---

## 【关联】

原文为该特性标注的内部链接 **（无）**，但从文档描述本身可梳理出以下上下游关系（基于原文叙述，不臆造）：

| 关系方向 | 模块/概念 | 原文依据 |
|---|---|---|
| 上下游（动机侧） | Pipeline Parallelism（PP） | "PP 的增大会对前几个 stage 造成较大的显存压力" |
| 上下游（动机侧） | Gradient Accumulation（梯度累积） | "增大梯度累积的情况下，优化器部分的一二阶动量显存 swap 的开销可忽略不计" |
| 上下游（替代/解耦） | 分布式优化器 + `overlap-grad-reduce` / `overlap-param-gather` | "当前分布式优化器逻辑复杂，并且与各种通信并行相互耦合"——本文方案不再侵入该耦合逻辑 |
| 上下游（硬件依赖） | 昇腾驱动虚拟内存能力、随路计算单元（attached computation unit） | "借助昇腾驱动的虚拟内存原生能力"；"没有硬件随路计算单元" |
| 上下游（运行时） | NPU 与 CPU 的 NUMA 拓扑 | 推荐配置 `CPU_AFFINITY_CONF=1,lazy_bind:0`——绑定到 NPU 对应 NUMA CPU 核心 |
| 上下游（功能依赖） | 优化器状态保存/加载（checkpoint） | "当前优化器部分的保存与加载已经适配"——保存/加载路径已通过 wrapper 处理 swap tensor |

---

## 【使用方法】

### 命令行启用（原文给出）

```bash
# 1) 全量 Swap：所有 PP stage 的全部一二阶动量均走虚拟内存
--virtual-optimizer all

# 2) 等量 Swap：每个 PP stage 申请相同大小的 Host 虚拟内存
#    下例为每个 stage 申请约 2.0 GB
--virtual-optimizer 2.0

# 3) 异量 Swap：每个 PP stage 独立指定 GB 数（按顺序对应 stage）
#    下例四阶段 PP 分别 Swap 6 / 5 / 4 / 3 GB
--virtual-optimizer 6 5 4 3
```

### 推荐环境变量（原文给出）

```bash
export CPU_AFFINITY_CONF=1,lazy_bind:0
```

——粗粒度绑核到 NPU 对应的 NUMA CPU 核心，减少跨 NUMA 内存访问与调度开销。

### 受驱动限制的访问方式（原文给出）

swap tensor **不可直接 `print` / `save`**，需通过以下 wrapper 间接访问；当前优化器部分的保存与加载已默认走该路径：

```python
def swap_tensor_copy_wrapper(func):
    def wrapped(*args, **kwargs):
        dst, src = args[0], args[1]
        dst_swap, src_swap = is_swap_tensor(dst), is_swap_tensor(src)
        if dst_swap or src_swap:
            if dst.device == src.device:
                dst.fill_(1).mul_(src)
            elif dst_swap:
                src_npu = src.to(dst.device)
                dst.fill_(1).mul_(src_npu)
            elif src_swap:
                src_npu = torch.ones_like(src).mul(src)
                dst.copy_(src_npu)
            else:
                raise TypeError
        else:
            func(*args, **kwargs)  # copy_
    return wrapped


def swap_tensor_func_wrapper(org_func, func_type):
    def wrapped(*args, **kwargs):
        if is_swap_tensor(args[0]):
            if func_type == "detach":
                detach = org_func(*args, **kwargs)
                setattr(detach, "swap_tensor", True)
                setattr(detach.data, "swap_tensor", True)
                return detach
            src = torch.empty_like(args[0])
            src.copy_(args[0])
            if func_type == "cpu":
                return src.cpu()
            elif func_type == "npu" or func_type == "clone":
                return src
            else:
                raise ValueError(f"func_type {func_type} not supported")
        else:
            return org_func(*args, **kwargs)
    return wrapped


# 标记一个张量为 swap tensor
p = torch.randn(100).npu()
exp_avg_swap = torch_npu.empty_with_swapped_memory(p.size(), device=p.device)
setattr(exp_avg_swap, "swap_tensor", True)

# 触发：打印 swap tensor（通过 wrapper 把数据拷到普通张量再 .cpu()）
torch.Tensor.copy_ = swap_tensor_copy_wrapper(torch.Tensor.copy_)
torch.Tensor.cpu   = swap_tensor_func_wrapper(torch.Tensor.cpu, "cpu")
exp_avg_cpu = exp_avg_swap.cpu()
print(f"exp_avg_cpu: {exp_avg_cpu}")
```

### 不适用场景（原文标注）

- 涉及 **随路计算（attached computation）** 的算子无法直接消费 swap tensor（驱动/HW 限制）；需要先经 wrapper 拷成普通 device 张量再运算（这会丧失虚拟内存方案的"免搬运"收益）。

## 图文联合解读

- `virtual-optimizer.png`: **图示解读：**

1) **画面内容**：上半部分对比传统Swap（Host→H2D→UB→HBM→Adam→HBM→UB→D2H→Host，7步搬运）与虚拟内存（Host→UB/Adam→Host，仅2步）；下半部分展示Adam算子产生的ExpAvg/ExpAvgSq以虚线框"虚拟显存"驻留device侧，物理ExpAvg在host侧通过"映射"关联。

2) **技术结论**：虚拟内存让Adam算子直接访问host物理内存，省去多次UB↔HBM往返；映射机制使device地址可参与计算。

3) **与文档关系**：图示印证"虚拟内存节省两次UB与HBM搬运""无需额外多流"的论点，并直观呈现`empty_with_swapped_memory`实现"一行代码替换"的工作机理。
