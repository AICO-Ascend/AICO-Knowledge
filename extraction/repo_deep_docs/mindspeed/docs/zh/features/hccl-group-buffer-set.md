# Hccl Group Buffer Set

> 仓 `mindspeed` · 路径 `docs/zh/features/hccl-group-buffer-set.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/hccl-group-buffer-set.md

# Hccl Group Buffer Set 特性文档深度解读

## 【定位】
本文档针对 MindSpeed 通信域 Buffer 只能通过 `HCCL_BUFFSIZE` 环境变量统一设置（默认 200MB）、无法按通信域差异化配置的痛点，提供自动与手动两种方式精细化设置各通信域缓冲区大小，从而在显存不足场景下实现显存节约与性能无损的平衡。

---

## 【技术要点】

1. **统一设置的局限性**：当前 MindSpeed 通信域 Buffer 只能通过环境变量 `HCCL_BUFFSIZE` 统一设置，默认值为 **200MB**，但不同通信域所需 Buffer 大小不能一概而论。

2. **双方案配置体系**：
   - **自动配置（推荐）**：`--hccl-group-buffer-adaptive`，MindSpeed 根据网络参数自适应通信域缓冲区大小。
   - **手动配置**：`--hccl-group-buffer`，以 `组名:大小MB` 格式让用户按需设置。

3. **MoE 负载不均衡系数**：`--hccl-ep-group-buffer-adaptive-factor`，仅用于 ep 相关通信组；系数 **=1** 代表负载均衡情况下的 buffer 大小，系数 **=n** 代表当前 buffer 是负载均衡情况的 **n 倍**，配置过大会导致 **OOM**。

4. **自动配置支持的通信组（14 个）**：`cp`、`mp`、`mp_exp`、`tp`、`pp`、`tp_cp`、`tp_exp`、`exp`、`pp_new_stream`、`cp2`、`cp_ulysses`、`cp_ring`、`cp_ring_intra`、`cp_ring_intra_overlap`。

5. **手动配置支持的通信组（23 个，比自动多 9 个）**：`dp`、`dp_cp`、`cp`、`mp`、`mp_exp`、`tp`、`pp`、`embd`、`tp_dp_cp`、`tp_dp`、`tp_cp`、`tp_exp`、`exp`、`dp_modulo_exp`、`pp_new_stream`、`cp2`、`cp_ulysses`、`cp_ring`、`cp_ring_intra`、`cp_ring_intra_overlap`、`nd1_dim1`、`ag_x_sd_rcv_overlap`、`nd1_dim2`、`ag_y_sd_rcv_overlap`、`nd2_dim1`、`nd2_dim2`。
   > 注：原文列表内含 26 个名称，请以原文为准。

6. **版本依赖**：本特性依赖 **TorchNPU:FrameworkPTAdapter 7.0.RC1.B020**（含该版本）之后的版本。

---

## 【关键机制与数据】

### 工作原理

- **自动配置路径**：MindSpeed 依据网络参数（如张量并行 tp、上下文并行 cp、流水线并行 pp 等维度信息）自适应计算各通信域所需 Buffer 大小；对于 ep 相关通信组（`exp`、`tp_exp`、`tp`），引入用户自定义的负载不均衡系数作为放大因子。
- **手动配置路径**：用户按 `组名:大小MB;组名:大小MB;...` 格式传入，MindSpeed 按指定值分配各通信域 Buffer。
- **使用效果（原文描述）**：
  - **LLaMA 系列模型**：开启自适应方案，性能不下降的同时可以节约显存。
  - **MoE 相关模型**：开启自适应方案并设置合适的负载不均衡系数，性能不下降的同时可以节约显存。

### 性能/显存数据

原文未给出具体的显存节约数值、性能百分比等量化指标。

---

## 【表格解读】

**原文无表格。**

文中仅以列表形式罗列了自动配置与手动配置各自支持的通信组名称，未以表格形式呈现。

---

## 【公式解读】

**原文无公式（LaTeX 或伪代码形式）。**

原文未给出任何数学公式，但有一处关键的数量关系描述（用文字表达）：

> "设置 `--hccl-ep-group-buffer-adaptive-factor` 大小为 **1**，代表的是负载均衡情况下需要开启的 buffer 大小；设置为 **n**，代表当前缓冲区大小是负载均衡情况下的 **n 倍**。"

可用文字等价为：

$$
\text{EP\_Buffer\_Size} = n \times \text{Buffer\_Size\_at\_Load\_Balanced}
$$

其中：
- $n$：用户指定的 `--hccl-ep-group-buffer-adaptive-factor` 系数，$n \ge 1$。
- $\text{Buffer\_Size\_at\_Load\_Balanced}$：负载均衡情况下 ep 相关通信组所需的 buffer 大小。
- 原文警告：$n$ 配置过大会导致 **OOM**。

---

## 【关联】

### 与其他特性/模块的关系

- **依赖基础组件**：本特性构建在昇腾 **HCCL**（集合通信库）之上，替代/补充了原有的 `HCCL_BUFFSIZE` 环境变量设置方式。
- **并行策略模块**：自动配置覆盖的张量并行（tp）、上下文并行（cp）、流水线并行（pp）通信域与 MindSpeed 的并行策略实现深度耦合。
- **MoE 专家并行（ep）**：与 MoE 模型的负载均衡密切相关，`--hccl-ep-group-buffer-adaptive-factor` 系数是面向 MoE 场景专门设计的调参接口。
- **依赖版本**：依赖 TorchNPU 的 `FrameworkPTAdapter 7.0.RC1.B020` 及以上版本，说明该特性与昇腾 PyTorch 适配框架版本绑定。
- **手册引用**：背景部分引用了《CANN 环境变量参考》的 `[HCCL_BUFFSIZE]` 章节，说明本文是 CANN 通信层 Buffer 配置在 MindSpeed 中的上层封装。

### 内部链接

原文文末给出的内部链接为 **(无)**，无内部交叉引用。

---

## 【使用方法】

### 启用条件

- 依赖 **TorchNPU:FrameworkPTAdapter 7.0.RC1.B020** 及以上版本。

### 自动配置（推荐）

| 参数 | 说明 |
|------|------|
| `--hccl-group-buffer-adaptive` | 开启自适应通信域缓冲区设置，自动配置 tp、cp、pp 相关通信组大小 |
| `--hccl-ep-group-buffer-adaptive-factor` | 用于 ep 相关通信组（`exp`、`tp_exp`、`tp`），指定负载不均衡系数；`1` = 负载均衡情况，`n` = 负载均衡情况的 n 倍，过大会 OOM |

### 手动配置

| 参数 | 说明 |
|------|------|
| `--hccl-group-buffer` | 指定通信组及大小，格式 `组名:大小MB;组名:大小MB;...`，单位 MB |

**手动配置示例（原文）**：`dp:200;tp:300;exp:400`，即 dp 通信域 200MB、tp 通信域 300MB、exp 通信域 400MB。

### 配置项枚举（通信组支持列表）

- **自动配置支持**：cp、mp、mp_exp、tp、pp、tp_cp、tp_exp、exp、pp_new_stream、cp2、cp_ulysses、cp_ring、cp_ring_intra、cp_ring_intra_overlap（共 14 个）。
- **手动配置额外支持**：dp、dp_cp、embd、tp_dp_cp、tp_dp、dp_modulo_exp、nd1_dim1、ag_x_sd_rcv_overlap、nd1_dim2、ag_y_sd_rcv_overlap、nd2_dim1、nd2_dim2 等。

### 适用场景

原文描述：显存不足、需要降低显存占用的场景可以开启该特性。
