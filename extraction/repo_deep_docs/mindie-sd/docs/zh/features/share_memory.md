# 显存共享

> 仓 `mindie-sd` · 路径 `docs/zh/features/share_memory.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/share_memory.md

# 显存共享（share_memory）深度解读

## 【定位】

这篇文档描述了 mindie-sd 在**同一 NPU 设备上多实例共享模型权重显存**的能力，通过进程间共享的 NPU Allocator 与 ZMQ 通信，使多份同构模型实例复用同一片物理显存，从而降低多实例部署的显存消耗。

---

## 【技术要点】

- **核心问题**：多实例场景下，同一 NPU 设备上多个模型使用相同权重造成显存浪费，原文图示（`figures/memory_share_image_1.png`）展示多份相同权重的并存。
- **理论支撑**：利用**相同的 NPU 物理地址 + 偏移（offset）** 构建不同 Tensor，从而多个 Tensor 同时访问同一片物理内存。
- **设计思路**：使用**进程间共享的内存管理器**统一管理内存，不同进程通过该管理器分配到的同一物理地址实现共享。
- **关键参数与默认值**（来自接口）：
  - `instance_world_size`：总实例数（必选 `int`，无默认值）。
  - `instance_id`：当前实例 ID，**0 为主实例**（必选 `int`）。
  - `master_addr`：ZMQ 通信主地址，默认 `"127.0.0.1"`。
  - `base_port`：ZMQ 基础端口，默认 `5555`。
- **核心 API**：`init_share_memory(...)` 初始化进程间共享内存管理器；`share_memory(module, device, dtype)` 将模型迁移到共享 NPU 显存。
- **跨进程通信机制**：主实例通过 **ZMQ** 将权重所在的 NPU 物理地址广播给从实例；从实例通过该物理地址 + offset 构建 Tensor，避免重复加载权重。

---

## 【关键机制与数据】

**工作原理（原文实现流程 5 步，对应图 `figures/memory_share_image_2.png`）：**

1. **进程 0** 统计所需内存大小 offset，通过**进程间共享的 NPU Allocator** 申请内存。
2. NPU Allocator 将申请到的**物理内存地址 `data_ptr`** 返回给进程 0。
3. 进程 0 将 `data_ptr` 通过**进程间通信（ZMQ）** 传给进程 1。
4. 进程 0 触发**内存拷贝**，将 CPU 内存拷贝到实际 NPU 物理地址上。
5. 进程 0 与进程 1 通过 `data_ptr` + `offset` 各自构建 Tensor。

**数据流特征（原文）：**

- 共享的核心要素是 **`data_ptr`（NPU 物理地址）+ `offset`（偏移）** 两者的组合，而非权重本身的复制。
- 主实例（`instance_id=0`）负责加载权重并发起物理内存分配；**从实例不加载权重**，仅通过共享句柄构建 Tensor。
- 跨进程传递通道明确为 **ZMQ**（由 `master_addr` + `base_port` 寻址）。

**性能/数据指标**：原文未提供具体的显存节省数字、吞吐提升或延迟对比数据。

---

## 【表格解读】

### 表 1：`init_share_memory` 参数表（原文逐字还原）

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `instance_world_size` | `int` | 是 | - | 总实例数 |
| `instance_id` | `int` | 是 | - | 当前实例 ID（0 为主实例） |
| `master_addr` | `str` | 否 | `"127.0.0.1"` | ZMQ 通信主地址 |
| `base_port` | `int` | 否 | `5555` | ZMQ 基础端口 |

**逐行解读：**

- **`instance_world_size`（必选）**：声明本次多实例共享的**总进程数**，用于协调器确定共享规模。调用方必须显式传入，文档未给默认值。
- **`instance_id`（必选）**：当前进程在多实例集合中的编号；**编号 0 为主实例**，承担加载权重与共享 `data_ptr` 的职责，其他编号为从实例。
- **`master_addr`（默认 `"127.0.0.1"`）**：ZMQ 主通信地址，本地多实例下取默认即可；多机或跨容器部署时需要覆盖。
- **`base_port`（默认 `5555`）**：ZMQ 基础端口，用于建立进程间通信通道，与 `master_addr` 共同定位协调端点。

### 表 2：`share_memory` 参数表（原文逐字还原）

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `module` | `torch.nn.Module` | 是 | - | 待迁移的模型实例 |
| `device` | `str` / `torch.device` | 否 | `None` | 目标设备，如 `"npu:0"` |
| `dtype` | `torch.dtype` | 否 | `None` | 目标数据类型 |

**逐行解读：**

- **`module`（必选）**：要迁移到共享显存上的 PyTorch 模型实例。**主实例传入已加载权重的模型**；**从实例传入未加载权重的模型**，二者通过共享句柄映射到同一物理内存。
- **`device`（默认 `None`）**：目标设备，可传字符串（如 `"npu:0"`）或 `torch.device` 对象；为 `None` 时由内部推断。
- **`dtype`（默认 `None`）**：目标数据类型；为 `None` 时按模型现有 dtype 处理（原文未给出 dtype 自动转换规则）。

---

## 【公式解读】

**原文无公式**。文档通过文字与流程图描述机制，未给出任何 LaTeX/伪代码形式的公式。

---

## 【关联】

- **进程间通信依赖 ZMQ**：由 `init_share_memory` 的 `master_addr`（默认 `"127.0.0.1"`）与 `base_port`（默认 `5555`）共同确定通信端点，用于广播 NPU 物理地址 `data_ptr`。
- **NPU Allocator 抽象**：文档未给出该分配器的具体实现链接，但流程中明确依赖"**进程间共享的 NPU Allocator**"作为内存的统一申请通道。
- **主/从实例角色分工**：以 `instance_id=0` 为主实例（加载权重 + 触发 CPU→NPU 拷贝），其余为从实例（仅通过 `data_ptr` + `offset` 构建 Tensor）。
- **内部链接**：原文未提供任何内部链接（本任务也注明"内部链接: (无)"），故文档之间明确的交叉引用关系原文未涉及。

---

## 【使用方法】

**Python 调用入口**（原文）：

```python
from mindiesd.share_memory import init_share_memory, share_memory
```

**主实例（加载权重并共享）**（原文示例）：

```python
from mindiesd.share_memory import init_share_memory, share_memory

init_share_memory(instance_world_size=2, instance_id=0)
model = ModelClass().to("npu")
model = share_memory(model, device="npu:0")
```

**从实例（接收共享内存）**（原文示例）：

```python
from mindiesd.share_memory import init_share_memory, share_memory

init_share_memory(instance_world_size=2, instance_id=1)
model = ModelClass()  # 不加载权重
model = share_memory(model, device="npu:0")  # 通过共享句柄构建 Tensor
```

**关键使用要点（原文）：**

- 主实例需先调用 `init_share_memory(instance_world_size=N, instance_id=0)`，再加载权重到 NPU，再调用 `share_memory(model, device="npu:0")`。
- 从实例同样需先调用 `init_share_memory`，**但不要加载权重**（注释"不加载权重"为原文明确说明），随后通过 `share_memory` 以共享句柄构建 Tensor。
- `instance_world_size` 必须与实际启动的实例数量一致；多机或非常用端口时需覆盖 `master_addr` / `base_port`。
- 环境变量、CLI 启动命令、配置文件路径等额外启用方式**原文未涉及**。

## 图文联合解读

- `memory_share_image_1.png`: **图文联合解读：**

**1) 图中内容：** 上半部分为"共享前"——instance 0 与 instance 1 各持有一段独立的 Device 显存（[0,n]、[0,m]），其中 tensor1-4 完整重复存放两份，颜色映射对应各自 Model 的 QLinear/KLinear/VLinear/OLinear 四层；下半部分为"共享后"——Device 仅存一份 tensor1-4，两实例的四层通过同色虚线箭头共同指向这同一片物理内存。

**2) 技术结论：** 同一 NPU 上多实例加载相同权重时，权重无需各存一份，通过共享底层 tensor 即可让多个 Model 复用同一片显存，从而消除冗余。

**3) 与文档关系：** 直接图示化文档"核心问题"——多实例重复权重导致显存浪费，呼应"利用相同 NPU 物理地址构建不同 Tensor"的设计思路。
- `memory_share_image_2.png`: **图解读：**

1) **画面内容**：上行为NPU显存布局，标注 `Tensor = data_ptr + offset`，由 NPU Allocator 分配，tensor1-4 以 0、n 偏移依次排布；下两行为 process 0（持有完整 CPU tensors 与 Q/K/V/O Linear）和 process 1（仅持有 Linear），通过 Gloo 跨进程通信；①②③④⑤ 五步对应实现流程。

2) **技术结论**：同一物理地址 data_ptr 配合不同 offset 即可让多进程共享同一片 NPU 显存，避免重复加载模型权重。

3) **与文档关系**：直观印证"理论支撑"中"相同物理地址+偏移构建不同 Tensor"的观点，并图解"实现流程"五步：申请→返回地址→IPC 传递→CPU→NPU 拷贝→双方构建 Tensor，支撑多实例下降低显存消耗的核心论点。
