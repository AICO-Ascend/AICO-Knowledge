# 图模式编译节点遍历选项

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/topology_sorting_strategy.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/topology_sorting_strategy.md

# 文档深度解读：图模式编译节点遍历选项（`topology_sorting_strategy`）

---

## 【定位】

这篇文档描述了在 TorchAir 昇腾 NPU 图模式推理场景下，用户如何通过 `topology_sorting_strategy` 配置项选择不同的图遍历顺序（DFS / BFS / RDFS / StableRDFS），从而影响算子编译时的静态图内存占用与执行顺序一致性，重点解决"通信算子在多卡间执行顺序不一致导致死锁或精度问题"的工程痛点。

---

## 【技术要点】

1. **配置项归属**：通过 `torchair.get_npu_backend` 接口中的 `compiler_config` 进行配置，具体路径为 `config.experimental_config.topology_sorting_strategy`，属于 `experimental_config` 命名空间下的实验性配置。
2. **四种遍历策略**：
   - **DFS（默认值）**：Depth First Search，深度优先遍历。
   - **BFS**：Breadth First Search，广度优先遍历。
   - **RDFS**：Reverse DFS，反向深度优先遍历。
   - **StableRDFS**：稳定拓扑序策略——对图中已有算子保持原计算顺序，对新增算子使用 RDFS 遍历。
3. **使用约束**：本功能**仅适用于 GE 图模式场景**，非 GE 图模式不支持此选项。
4. **策略选择的风险提示**：若同一通信域内的通信算子之间**未通过控制边显式约束依赖**，选择非稳定排序算法（DFS / BFS / RDFS）**可能导致多卡间执行顺序不一致**，进而引发**通信死锁或精度问题**。
5. **StableRDFS 的局限性**：原文明确指出"StableRDFS 旨在最大程度上保留原图的时序"，但**在图融合或图优化导致拓扑结构变更时，其稳定性仍可能失效**。
6. **推荐做法**：推荐通过**显式控制边**保障执行顺序的**绝对一致性**；StableRDFS 仅作为**无法修改图结构时的辅助补偿方案**。

---

## 【关键机制与数据】

原文未提供量化性能数据或具体内存占用数字，本节仅描述其工作原理层面的机制：

- **作用时机**：发生在"推理场景下进行算子编译时"，作用于图编译阶段，决定编译器对计算图的遍历顺序。
- **影响维度**：原文定性表述为"对静态图内存使用有不同的影响"，但**未给出具体数值或对比数据**；同时影响通信算子在多卡上的执行顺序。
- **数据流**：用户构造 `CompilerConfig` → 通过 `experimental_config.topology_sorting_strategy` 设置策略字符串 → 调用 `get_npu_backend(compiler_config=config)` 包装后端 → 经 `torch.compile(model, backend=npu_backend)` 应用于模型编译过程。
- **底层依据**：原文将"执行顺序"与"通信算子拓扑"关联，暗示遍历策略影响的是算子调度顺序而非算子实现本身。

> 原文标注：所有上述表述均来自原文"功能简介"、"参数说明"表格及其备注段落，**未提供 benchmark 数据**。

---

## 【表格解读】

### 表格逐字还原

**表 1　参数说明**

| 参数名 | 说明 |
| -- | -- |
| topology_sorting_strategy | 图执行时可以设置不同的图遍历顺序。<br>DFS（默认值）：Depth First Search，深度优先遍历策略。<br>BFS：Breadth First Search，广度优先遍历策略。<br>RDFS：Reverse DFS，反向深度优先遍历策略。<br>StableRDFS：稳定拓扑序策略，针对图里已有的算子，不会改变其计算顺序；针对图里新增的算子，使用RDFS遍历策略。<br>若同一通信域内的通信算子间未通过控制边显式约束依赖，选择非稳定排序算法（如 DFS、BFS、RDFS）可能导致多卡间执行顺序不一致，从而引发通信死锁或精度问题。虽然StableRDFS旨在最大程度上保留原图的时序，但在图融合或图优化导致拓扑结构变更时，其稳定性仍可能失效。因此，推荐通过显式控制边来保障执行顺序的绝对一致性，而 StableRDFS仅作为在无法修改图结构时的辅助补偿方案。 |

### 逐行解读

| 行 | 解读 |
|---|---|
| **参数名 `topology_sorting_strategy`** | 配置项的字段名，挂在 `config.experimental_config` 之下，类型为字符串枚举。 |
| **"图执行时可以设置不同的图遍历顺序。"** | 该参数的本质功能：通过指定遍历算法控制编译后图的执行调度顺序。 |
| **DFS（默认值）** | 默认策略，采用深度优先遍历；隐含含义：在多数场景下无需特殊配置即可使用。 |
| **BFS** | 备选策略之一，采用广度优先遍历，与 DFS 形成"深度 vs 广度"的两条基本路径。 |
| **RDFS** | 备选策略之一，采用反向深度优先遍历，等价于在逆向上做 DFS。 |
| **StableRDFS** | 复合策略：核心思想是"已存在算子保持稳定，新增算子用 RDFS"；是一种**保守**的遍历选择。 |
| **"若同一通信域内的通信算子间未通过控制边显式约束依赖……"** | 风险条件 1：通信算子之间缺乏显式依赖；风险后果 1：多卡间执行顺序不一致；最终后果：通信死锁或精度问题。 |
| **"虽然 StableRDFS 旨在最大程度上保留原图的时序……"** | StableRDFS 的**边界条件**：图融合或图优化改变拓扑后，稳定性可能失效——即它不提供绝对保证。 |
| **"因此，推荐通过显式控制边来保障执行顺序的绝对一致性……"** | 官方推荐方案优先级：**显式控制边 > StableRDFS**；StableRDFS 仅作为**辅助补偿**。 |

---

## 【公式解读】

**原文无公式。**

文档涉及的是配置项与策略枚举，没有出现任何 LaTeX 公式或伪代码算法表示。

---

## 【关联】

根据文末提供的内部链接，本特性与以下模块/接口存在直接依赖关系：

- **`torchair.get_npu_backend`**（[../../api/torchair/get_npu_backend.md](../../api/torchair/get_npu_backend.md)）
  - 关系：**配置注入点**。`topology_sorting_strategy` 必须通过 `get_npu_backend(compiler_config=...)` 的 `compiler_config` 参数传入才能生效，因此本特性是 `get_npu_backend` 的下游消费者。
  - 路径分析：相对路径 `../../api/torchair/get_npu_backend.md` 表明该链接指向 TorchAir API 层的核心入口文档。

- **上游依赖**：
  - **`CompilerConfig`**（构造配置对象的类）：是 `topology_sorting_strategy` 的载体容器。
  - **`experimental_config`**（命名空间）：是配置项的访问路径前缀，暗示该特性处于**实验阶段**。
  - **`torch.compile`**（PyTorch 动态图→静态图编译入口）：最终通过 `backend=npu_backend` 接入。

- **隐含关联（原文未直接链接，但涉及）**：
  - **GE 图模式**（Graph Engine）：文档约束"本功能仅适用于 GE 图模式场景"，表明其依赖昇腾 GE 引擎的图编译流水线。
  - **算子融合 / 图优化 Pass**：StableRDFS 在图融合导致拓扑变更时会失效，间接关联图优化模块。
  - **控制边（Control Edge）**：作为推荐方案的依赖关系建立机制，与通信算子（如 AllReduce、AllGather 等集合通信算子）相关。

---

## 【使用方法】

### 启用方式（原文代码示例逐字保留）

```python
import torch_npu
import torchair
config = torchair.CompilerConfig()
# 图模式编译的遍历策略配置
config.experimental_config.topology_sorting_strategy = "DFS"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

### 配置项列表

| 配置项 | 取值 | 说明 |
|---|---|---|
| `config.experimental_config.topology_sorting_strategy` | `"DFS"`（默认） | 深度优先遍历 |
| 同上 | `"BFS"` | 广度优先遍历 |
| 同上 | `"RDFS"` | 反向深度优先遍历 |
| 同上 | `"StableRDFS"` | 稳定拓扑序策略 |

### 启用前提（约束条件）

- **场景约束**：仅适用于 **GE 图模式场景**，非 GE 图模式不支持。
- **声明性提示**：原文标注"示例仅供参考不支持直接拷贝运行"，意味着该代码示例不可直接执行，需结合用户实际模型与上下文使用。

### 选型建议（原文依据）

1. **默认场景**：保持 `"DFS"` 不变。
2. **多卡通信涉及执行顺序问题**：优先**通过显式控制边**约束通信算子依赖；若无法修改图结构，可将策略切换为 `"StableRDFS"` 作为**辅助补偿**。
3. **避免做法**：在通信算子缺乏显式依赖时，不要随意使用 `"DFS"` / `"BFS"` / `"RDFS"` 等非稳定排序算法。

> 原文未涉及：性能 benchmark 数据、内存占用量化对比、各策略在不同模型规模下的适配建议——以上信息在原文中均**未提供**。
