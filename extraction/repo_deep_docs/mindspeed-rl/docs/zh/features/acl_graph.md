# 推理图模式

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/acl_graph.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/acl_graph.md

# mindspeed-rl · 推理图模式 文档深度解读

---

## 【定位】

这篇文档解决的是**在昇腾设备上为大模型推理启用/关闭图模式（TorchAir / torch.compile 后端）并与 vLLM 的 eager 模式开关协同配置**的问题，核心目标是通过合理的 `torchair_graph` 与 `enforce_eager` 参数搭配，配合 `TASK_QUEUE_ENABLE` 环境变量，提升推理性能。

---

## 【技术要点】

1. **TorchAir 定位**：TorchAir（Torch Ascend Intermediate Representation）是昇腾为 Ascend Extension for PyTorch（torch_npu）提供的**图模式能力扩展库**，其作用是为 PyTorch 网络在昇腾设备上提供**推理**场景下的图模式执行能力。原文强调其用途限定为"推理"，并非训练。

2. **编译后端与对接机制**：TorchAir 基于 `torch.compile` 提供昇腾设备的**图模式编译后端**，对接 PyTorch 的 **Dynamo 特性**，将 PyTorch 的 **FX（Functionalization）计算图**转换为昇腾 **Ascend IR（Intermediate Representation）计算图**，并通过 **GE（Graph Engine）** 启动计算图编译和执行能力。

3. **vLLM `enforce_eager` 语义**：`enforce_eager=True` 是 vLLM 推理框架中的执行模式开关，用于强制模型以 **eager execution**（逐条立即执行）方式运行，不进行图构建或延迟求值；这是相对于默认的图优化执行路径的"反优化"路径。

4. **`torchair_graph` 参数**：用于在 **DeepSeek V3** 模型上使能 torchair 图模式（即开启昇腾图编译路径）。

5. **`enforce_eager` 参数**：使能 PyTorch eager 模式；当显存有余量时，**建议将该参数设置为 false**，以启动图模式，提高推理性能。

6. **环境变量与开关互斥约束**：
   - 当 `enforce_eager: false` 时，`TASK_QUEUE_ENABLE` 需设置为 **1**；
   - 当 `enforce_eager: true` 时，`TASK_QUEUE_ENABLE` 需设置为 **2**；
   - **DeepSeek V3 开启 `torchair_graph` 时，必须关闭 `enforce_eager`**（即不能同时为 true）。

---

## 【关键机制与数据】

**数据流 / 工作原理（原文描述链路）：**

```
PyTorch 网络
   │
   ▼
torch.compile 后端 (TorchAir 提供)
   │
   ▼ (对接 PyTorch Dynamo 特性)
PyTorch FX (Functionalization) 计算图
   │
   ▼ (转换)
昇腾 Ascend IR 计算图
   │
   ▼ (驱动)
GE (Graph Engine)  ──→ 计算图编译 + 执行
```

**关键执行模式对照（原文语义）：**

- **图模式（默认/enforce_eager=false）**：PyTorch 操作经过 FX → Ascend IR → GE 的完整编译与图优化路径，性能更高。
- **eager 模式（enforce_eager=true）**：PyTorch 操作**逐条立即执行**，无图构建、无延迟求值，便于调试但性能较低。

**性能数据**：原文未给出具体的吞吐量、时延、加速比等数值，**仅给出方向性建议**——"显存有余量时建议 `enforce_eager: false`，以启动图模式，提高推理性能"。文档未提供量化性能对比。

---

## 【表格解读】

**原文无表格。**

文档中仅以 YAML 代码块形式给出配置示例：

```yaml
general_config:
    enforce_eager: true
    torchair_graph: false
```

这不是表格，而是配置代码块，因此按原文如实记录为"原文无表格"。

---

## 【公式解读】

**原文无公式。**

全文未出现 LaTeX 公式、伪代码公式或任何数学表达式。所有内容均为概念性描述与 YAML 配置示例。

---

## 【关联】

**与文中提及的上游/相关模块的关系：**

| 关系对象 | 在本文档中的角色 | 文档中描述的内容 |
|---|---|---|
| **Ascend Extension for PyTorch (torch_npu)** | TorchAir 的运行载体 | TorchAir 是其提供的图模式能力扩展库 |
| **torch.compile** | TorchAir 的实现基础 | TorchAir 基于其提供昇腾设备的图模式编译后端 |
| **PyTorch Dynamo** | 图捕获前端 | TorchAir 对接其进行图捕获 |
| **PyTorch FX (Functionalization)** | 中间表示层 | 被转换为 Ascend IR 的源计算图 |
| **昇腾 Ascend IR (Intermediate Representation)** | 目标中间表示 | FX 计算图被转换为 Ascend IR |
| **GE (Graph Engine)** | 计算图编译与执行引擎 | 负责启动 Ascend IR 的编译与执行 |
| **vLLM (Very Large Language Model)** | 推理框架宿主 | 提供 `enforce_eager` 这一执行模式开关 |
| **DeepSeek V3** | 目标应用模型 | 文档明确指出该参数是为 DeepSeek V3 使能 torchair 图模式 |

**与 `TASK_QUEUE_ENABLE` 环境变量的约束关系**：该环境变量虽未在本文档中展开解释其内部机制，但通过"注释"形式与 `enforce_eager` 形成强绑定——两者必须按规则协同设置。

> 文档内部链接：**(无)**。全文未提供其他文档的相对路径或锚点链接，仅包含两个 PyTorch 官方文档外链（Dynamo、FX），不属于 mindspeed-rl 内部关联。

---

## 【使用方法】

### 配置示例（原文 YAML 代码块，原样还原）：

```yaml
general_config:
    enforce_eager: true
    torchair_graph: false
```

### 配置项说明（原文整理）：

| 配置项 | 取值 | 含义 | 原文建议 |
|---|---|---|---|
| `general_config.enforce_eager` | `true` / `false` | 是否使能 PyTorch eager 模式 | 显存有余量时建议设为 `false`，以启动图模式、提高推理性能 |
| `general_config.torchair_graph` | `true` / `false` | 是否对 DeepSeek V3 使能 torchair 图模式 | 与 `enforce_eager` 互斥使用（见下） |

### 配套环境变量（原文注释）：

| `enforce_eager` 取值 | `TASK_QUEUE_ENABLE` 取值 |
|---|---|
| `false`（图模式） | **1** |
| `true`（eager 模式） | **2** |

### 使用约束（原文注意事项，原文逐条保留）：

> **注意：**
> 1. `enforce_eager: false` 时，`TASK_QUEUE_ENABLE` 需设置为 **1**，否则设置为 **2**。
> 2. DeepSeek V3 开启 `torchair_graph` 时，需要**关闭 `enforce_eager`**（即 `enforce_eager` 不能同时为 true）。

### 启用 / 关闭方式总结：

- **启用图模式（性能优先路径）**：`enforce_eager: false` + `TASK_QUEUE_ENABLE=1`，并按模型需要决定是否设置 `torchair_graph: true`。
- **强制 eager 模式（调试 / 显存紧张 / 兼容性优先路径）**：`enforce_eager: true` + `TASK_QUEUE_ENABLE=2`，此时 `torchair_graph` 必须为 `false`（在 DeepSeek V3 上与 `enforce_eager` 互斥）。
- **DeepSeek V3 启用 torchair 图模式**：在 `enforce_eager: false` 的前提下设置 `torchair_graph: true`，并配套 `TASK_QUEUE_ENABLE=1`。
