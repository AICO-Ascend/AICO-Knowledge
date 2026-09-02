# Shared Memory

> 仓 `mindie-sd` · 路径 `docs/en/features/share_memory.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/share_memory.md

# 深度解读:docs/en/features/share_memory.md

---

## 【定位】
这篇文档描述了 mindie-sd 中"跨进程共享 NPU 权重内存"的能力,通过让同一 NPU 设备上的多个模型实例共用同一份权重物理内存,降低多实例部署场景下的显存占用。

---

## 【技术要点】

1. **核心问题定位**:多实例(multi-instance)场景中,同一 NPU 设备上的多个模型持有相同的权重,导致显存冗余;共享内存可削减这部分冗余占用。
2. **理论依据**:只要不同张量基于**同一 NPU 物理地址 + 同一 offset** 构造,即可同时访问同一段物理内存,即权重可被多进程"重复指向"而非"重复存储"。
3. **设计架构**:引入**进程间共享内存管理器(inter-process shared memory manager)**,统一由该管理器分配内存,各进程复用管理器分配的同一物理地址。
4. **跨进程通信机制**:主实例(Process 0)通过 **ZMQ** 将 NPU 物理地址 `data_ptr` 广播给从实例(Process 1+);从实例据此构造张量,实现"零拷贝权重共享"。
5. **共享粒度与生命周期**:`init_share_memory` 需先于 `share_memory` 调用;从实例调用 `share_memory` 时**不再 `to("npu")` 加载权重**(示例代码明确注释 "No weight loading"),改为通过共享句柄(handle)重建张量。
6. **关键 API 入参约束**:必须显式传入 `instance_world_size`(实例总数)与 `instance_id`(当前实例 ID,`0` 表示主实例);`master_addr` 默认 `"127.0.0.1"`、`base_port` 默认 `5555`,用于建立 ZMQ 通信。

---

## 【关键机制与数据】

> 以下所有内容均严格源自原文,凡数值/参数/流程均原样标注。

- **原文**:不同张量只要用"相同的物理地址 + 相同的 offset"构造,即可同时访问同一段物理内存区域——这是文档给出的唯一理论依据,未给出额外的地址映射算法说明。
- **原文**:进程间共享 NPU Allocator 由主实例(Process 0)调用,完成"计算所需内存大小 offset → 分配 → 返回 `data_ptr` → 通过 IPC 把 `data_ptr` 同步给从实例(Process 1)→ 触发 CPU→NPU 的内存拷贝"的完整链路。
- **原文**:从实例拿到 `data_ptr` 后,**不重新分配物理显存**,而是与主实例基于同一 `data_ptr` 与 offset 共同构造张量,因此多个进程的 `torch.Tensor` 视图指向同一段 NPU 显存。
- **原文**:跨进程通信采用 ZMQ,主控地址默认 `"127.0.0.1"`,基准端口默认 `5555`;`init_share_memory` 接收 `instance_world_size` 与 `instance_id`,按此建立组规模与身份。
- **原文**:文档**未提供**任何性能数据(吞吐、显存节省比例、时延等)、Benchmark、量化指标或显存占用的对比数字——本文不臆造。
- **原文**:文档未给出支持的具体模型规模(dtype/参数量)、`share_memory` 调用顺序对权重的额外约束、共享内存对齐要求、ZMQ 消息格式等细节。

---

## 【表格解读】

### 表 1:`init_share_memory` 参数表(原文逐字还原)

| Parameter | Type | Required | Default | Description |
| ------ | ------ | ------ | -------- | ------ |
| `instance_world_size` | `int` | Yes | - | Total number of instances |
| `instance_id` | `int` | Yes | - | Current instance ID (0 is the primary instance) |
| `master_addr` | `str` | No | `"127.0.0.1"` | ZMQ communication master address |
| `base_port` | `int` | No | `5555` | ZMQ base port |

**逐行解读**:
- `instance_world_size`:必填整型,代表本次共享会话涉及的实例总数,用于管理器确认参与方数量。
- `instance_id`:必填整型,标识当前进程在实例组中的身份;`0` 为主实例,负责加载权重并广播 `data_ptr`;`≥1` 的实例为从实例。
- `master_addr`:非必填字符串,默认 `"127.0.0.1"`,作为 ZMQ 通信的主地址;本地多实例场景可直接使用默认值。
- `base_port`:非必填整型,默认 `5555`,ZMQ 通信的基准端口,实例组内可在此基础上派生具体端口。

### 表 2:`share_memory` 参数表(原文逐字还原)

| Parameter | Type | Required | Default | Description |
| ------ | ------ | ------ | -------- | ------ |
| `module` | `torch.nn.Module` | Yes | - | Model instance to be moved |
| `device` | `str` / `torch.device` | No | `None` | Target device, e.g. `"npu:0"` |
| `dtype` | `torch.dtype` | No | `None` | Target data type |

**逐行解读**:
- `module`:必填的 `torch.nn.Module`,即需要迁入共享 NPU 内存的模型实例。
- `device`:非必填,可为 `str` 或 `torch.device`,用于指定目标设备(如 `"npu:0"`);未填时由 `None` 默认占位。
- `dtype`:非必填的 `torch.dtype`,指定目标数据类型,用于构造与主实例一致的视图(具体语义以 mindiesd 运行时实现为准,原文未展开)。

---

## 【公式解读】

**原文无公式**。文档未给出任何 LaTeX 数学式或伪代码形式的关系式;地址共享机制以流程步骤(Implementation Flow 五步)与 API 调用示例的形式呈现,而非以公式呈现。

---

## 【关联】

原文末尾未提供任何内部链接信息(用户已明示 "内部链接: (无)")。从文档自身可提炼出的关联如下(均基于原文表述,**不臆造**):

- **与多实例部署的关联**:文档 Core Problem 指出"多实例场景下同一 NPU 上多份权重冗余",因此本特性服务于多实例部署,**适用前提是"同 NPU、跨进程、共享同一份权重"**。
- **与 ZMQ 通信层的关系**:`init_share_memory` 的 `master_addr`/`base_port` 参数表明该机制依赖 ZMQ 进行 `data_ptr` 广播,与文档 Implementation Flow 第 3 步"via inter-process communication"对应。
- **与 `torch.Tensor` 构造的关系**:Implementation Flow 第 5 步与 Usage Example 中"Build tensors via shared handles"的描述表明,本特性需要底层张量构造支持"以 `data_ptr` + offset 重建张量"的语义;但文档未进一步指明该构造是借由 PyTorch 原生能力还是 mindiesd 自定义算子实现。
- **与 mindiesd 其他特性**:用户给出"无内部链接",**原文未显式引用** vLLM Omni、Diffusers+CacheDit、lightx2v 等框架,故本文不做关联臆断。

---

## 【使用方法】

以下命令/代码片段均**严格取自原文 Usage Example**。

### 1. 导入接口

```python
from mindiesd.share_memory import init_share_memory, share_memory
```

### 2. 主实例(Primary instance,instance_id=0):加载权重并共享

```python
from mindiesd.share_memory import init_share_memory, share_memory

init_share_memory(instance_world_size=2, instance_id=0)
model = ModelClass().to("npu")
model = share_memory(model, device="npu:0")
```

要点(原文):先 `init_share_memory` 建立组;再 `ModelClass().to("npu")` 由主实例加载权重到 NPU;最后 `share_memory` 将模型迁入共享 NPU 内存。

### 3. 从实例(Secondary instance,instance_id=1):接收共享内存

```python
from mindiesd.share_memory import init_share_memory, share_memory

init_share_memory(instance_world_size=2, instance_id=1)
model = ModelClass()  # No weight loading
model = share_memory(model, device="npu:0")  # Build tensors via shared handles
```

要点(原文):从实例**不加载权重**(`No weight loading`),直接构造模型对象;`share_memory` 通过共享句柄(handle)重建张量,从而与主实例指向同一段 NPU 物理地址。

### 4. 启用前必备条件(原文已具备的约束)

- 必须先调用 `init_share_memory`,后调用 `share_memory`(原文示例顺序即此);
- 主实例与从实例的 `instance_world_size` 必须保持一致(原文示例均为 `2`);
- 主实例与从实例需能通过 `master_addr`/`base_port` 互通 ZMQ,以便广播 `data_ptr`。
- 原文未涉及集群调度、多 NPU 跨卡共享、共享内存回收/释放时机的配置项,故**不展开**。

## 图文联合解读

- `memory_share_image_1.png`: **图解：**

1) **图示内容**：上半部展示两个实例（instance 0/1）在NPU Device上各存一份完整的tensor1–4权重副本；下半部（红色虚线下方）经共享内存优化后，两实例的Model（QLinear/KLinear/VLinear/OLinear）通过箭头共同映射到Device上同一组tensor1–4。

2) **技术结论**：多实例同卡部署时权重存在冗余存储；通过共享tensor存储空间可显著减少NPU显存占用。

3) **与文档关系**：直接对应"Core Problem"论点——可视化"多模型共享同一NPU设备相同权重"以及"共享内存可降低内存消耗"的核心思想，为后续Theoretical Basis（同物理地址+offset构造tensor）和Implementation Flow提供动机铺垫。
- `memory_share_image_2.png`: **图文解读：**

图中展示了跨进程NPU共享内存的实现流程：NPU Allocator分配物理地址data_ptr，Process 0通过CPU→NPU复制数据后，经Gloo通信将地址传给Process 1，两进程以相同data_ptr+offset构建Tensor（图中QLinear/KLinear/VLinear/OLinear的虚线箭头指向同一物理块）。论证了"同一物理地址+偏移量可被多进程访问"的理论成立，实现了权重共享，节省显存。
