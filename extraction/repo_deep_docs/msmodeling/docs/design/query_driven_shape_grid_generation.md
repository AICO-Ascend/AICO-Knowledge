# 查询驱动的 Shape 网格生成设计

> 仓 `msmodeling` · 路径 `docs/design/query_driven_shape_grid_generation.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/query_driven_shape_grid_generation.md

# 查询驱动的 Shape 网格生成设计 — 一体化深度解读

---

## 【定位】

这篇文档描述 `tools/perf_data_collection/generate_shape_grid.py` 工具如何以 TensorCast/ServingCast 在 throughput optimizer 中的**实际 CANN Kernel 查询路径**为首要输入，混合通用理论兜底，生成只含**可 replay Shape** 的性能数据库网格——目的是回答"该模型在 throughput optimizer 中到底会查询哪些 Kernel Shape"这一纯理论笛卡尔积无法可靠回答的问题。

---

## 【技术要点】

1. **五类公开输入**：仅 `--database-path`（必选）、`--rows`（默认 `1000`，单轮新增上限而非总行数）、`--target-models`（HF 模型 ID，必选）、`--ops`（可选 replay-supported Kernel 集合）、`--seed`（默认 `0`，Coverage 候选稳定排序种子）。设备、vLLM/PyTorch/CANN 版本从 `op_mapping.yaml` 读取，不重复公开。
2. **三层优先级**：exact demand → 同 Kernel/dtype/format/runtime regime 单轴插值与边界 → 两个真实动态轴组合 → 三个及以上确定性组合；动态轴只从同一 schema 下多个 exact demand 的实际变化推断，联动组（按固定比例共变的维度）作为整体处理。
3. **算子优先级**：传入 `--ops` 时优先级最高，命中走查询网格、未命中走通用 Theory Generator，未传入时算子集 = 模型实际查询 ∩ 有 CSV ∩ 有 replay 入口的 Kernel；通用配置明确标 `skip` 才跳过理论兜底；无 replay 入口或无 CSV 在写数据库前报错。
4. **Workload Policy**：HF 架构 + 设备拓扑自适应构造扫描；optimizer `batch 1～512`、TP/EP/MoE-DP/decode-only DCP 分轴扫描；TP×EP 仅保留 `min×max`、`max×min`、`max×max`、`mid×mid` 四点；除主 baseline 外其余 workload 仅跑 batch 下界与采样上界两个查询，上界满足 `batch × input_length ≤ max_context_length`。
5. **调度与收敛**：每 workload 独立子进程，并发上限 8（按 CPU/内存自动下调），每个 optimizer 保持单 job；trace 与 optimizer 进程树连续 **30 秒无活动**即判定该 workload 查询收敛、回收子进程；checkpoint 缓存键 = workload policy + 模型 + 数据库内容 + 查询/投影源码摘要。
6. **投影与 replay 边界**：projector 处理 MatMul `(K,N)→(N,K)`、ND/FRACTAL_NZ block、RoPE/SwiGlu/ReshapeAndCache 换序、MoE token permute/unpermute、3D→2D flatten、FIA/SparseFlashAttention/LightningIndexer runtime metadata 等；不支持的 demand 直接拒绝并计数，不写猜测行；通信 Kernel 捕获查询但不写入 compute CSV。

---

## 【关键机制与数据】

### 数据流（原文 ASCII 图，逐段解读）

```
HuggingFace ModelArchitecture
        ↓
内部 workload policy（设备数、长度、batch、并行与编译组合）
        ↓
多次 throughput_optimizer
        ↓
ProfilingDataSource 捕获 HIT/MISS 的实际 Kernel 查询
        ↓
版本化 CANNBackendProjector
        ↓
查询命中：精确锚点 + CoveragePlanner 插值/边界候选
查询未命中的显式 --ops：通用 Theory Generator
        ↓
仅写入存在 op_replay/*_run.py 的 Kernel CSV
        ↓
start_microbench / op_replay 实测回填
```

解读：入口是 HF 架构元数据；内部 policy 不暴露给用户，只决定要扫哪些（设备数、长度、batch、TP/EP/MoE-DP/DCP/MTP、编译融合、量化）组合；多次 optimizer 子进程独立跑出查询，DataSource 同时记录 HIT 与 MISS；projector 按目标数据库 CSV schema 做 TensorCast→replay Shape 投影；查询与理论候选走同一 CSV 签名去重 + `--rows` 预算；最终落库前提是有 `op_replay/*_run.py`；写库行耗时字段为 0，由 `start_microbench` / `op_replay` 实测回填。

### 查询捕获范围

- 普通 compute、elementwise、attention、MoE、MTP projection；
- composite 的 compute / attention / cache 子 Kernel；
- 独立通信和 composite 通信查询；
- 数据库 **HIT 与 MISS**（MISS 也必须记录，允许 analytic fallback 不中断后续模型执行）。
- 每个 optimizer 子进程写独立 **JSONL 分片**，主进程按稳定查询签名全局去重；签名不含模型名和 workload 名，避免同 Kernel 查询因来源不同重复占网格；来源仅留 trace 诊断；trace schema 与 projector 软件栈身份显式版本化。
- primary/alternate Kernel 共存时，trace 保留版本化 backend candidate 集合，只对目标数据库中**存在且有 op replay** 的 Kernel 写行。
- cache pool 容量等已由查询规则声明为性能无关的轴：使用 replay-minimal 或现有 schema 容量；序列长度、有效 block 数、runtime metadata 仍来自真实执行。

### 与实测查询语义一致性（与 PR705 解耦）

- 复用 PR705 验证过的通用查询语义，但代码独立落本分支，不依赖 PR705、不引入其模型数据或模型特判。
- composite 的 exact 与 interpolation 共用同一份 TP/phase/SP runtime mapping；SP 只投影 Prefill，Decode 保留原 token。
- **TP=1 是合法恒等分片**；非整除 token 按 `ceil(tokens / TP)` 生成最忙 rank 的物理 Shape。
- cache update 物理池容量**非性能轴**；Scatter 查询仅按 cache tail、update tail、dtype/format 分 regime。
- `compute_scale` 保留 FP16/BF16 物理差异、标量 scale 输出、NCL/ND format 以及 per-token / per-tensor / per-channel / per-block regime——这些在 CSV 命中**前**就写入 query trace。
- 单请求 Sparse Attention Prefill 使用一维 token 轴，避免两个相同自由度被表示成共线二维插值；共享 token 轴的多输入算子通过 mapping 声明联动输入。

### Workload 收敛与并行

- TP/EP/MoE-DP/DCP/MTP 候选完成合法性过滤后展开成单一并行配置的独立 workload。
- 调度器并发上限 **8**，按 CPU 核数与可用内存自动下调；每 optimizer 单 job。
- 进度输出包含：候选组合数、单 workload 耗时、完成原因、已完成数量、ETA。
- 收敛判定：`trace` 已覆盖该 workload 的 TP/EP 候选，且 trace 与整个 optimizer 进程树连续 **30 秒**无活动 → 跳过 optimizer 结果汇总/缓存等待阶段的无效耗时。
- checkpoint 缓存键含 workload policy 版本、目标模型、数据库内容、查询/投影关键源码摘要；DB/模型/查询语义任一变化即失效；中断后再次执行同一命令复用已完成 workload，失败/不完整 workload 重跑；缓存不写性能数据库、不改变 CSV 来源语义。

### compile/SP/DFC 与极端组合抑制

- 不执行 `max context × max EP × max MTP` 三轴极端角点。
- 工具在一个**中间长度锚点**查询 EP/MTP 完整边界交互；在短、长长度锚点只跑基础编译配置；CoveragePlanner 再将长度轴与离散交互轴组合加密。
- 默认量化之外：W8A8 动态量化 + **BF16 基线** + **代表性的 INT8 KV-cache** 查询。

### CoveragePlanner 优先级（数值化）

| 级别 | 内容 |
|---:|---|
| 1 | 实际查询的 exact demand |
| 2 | 同一 Kernel、dtype/format、runtime regime 内的单轴插值及上下边界 |
| 3 | 两个真实动态轴的组合 |
| 4 | 三个及以上动态轴的确定性组合 |

- 联动组示例：MatMul 的 M 轴 + 输出 M 轴；FRACTAL_NZ 权重块与逻辑 N/K 的比例。
- 隐藏维度 / 头维度 / runtime regime 若查询中未变化则**不被任意扰动**。
- Attention、Sparse Attention、LightningIndexer 含 list-valued runtime metadata：不脱离执行上下文做笛卡尔扩展；显式 `--ops` 触发理论兜底时必须由**该算子专用 generator**同步生成 Shape 与 runtime metadata。

### 物理 Shape 投影要点（原文逐项）

- MatMul 权重 `(K,N) → (N,K)`；
- ND 与 FRACTAL_NZ block Shape；
- grouped weight 的 expert 前缀；
- RoPE 输入换序与布局转换；
- SwiGlu 双输入合并；
- ReshapeAndCache 的合并 cache 拆分；
- MoE token permute/unpermute：token flatten、index dtype、辅助输出；
- grouped-list 激活拼接与专家权重前缀；
- compile/SP 下 RmsNorm、AddRmsNorm、DynamicQuant、DFC 的物理槽位；
- 3D token/batch 到 2D kernel Shape 的 flatten；
- FIA、SparseFlashAttention、LightningIndexer 的 runtime metadata 与可 replay 物理槽位。

投影规则由数据库软件栈身份版本化；不匹配现有 CSV schema 的 demand → 拒绝 + 计数，不写猜测行。

### 性能/回填边界

- Shape 生成工具只产出待实测网格；**写入行的耗时字段为 0**。
- 完整验收闭环（原文列出五步）：
  1. 目标 A3/对应硬件上执行 microbench 回填；
  2. 检查生成行 replay 成功率与无效行；
  3. 用独立 holdout workload 检查数据库 coverage；
  4. 检查插值误差；
  5. 对 optimizer best row 执行 text_generate B2B。
- 原文明确警告："仅靠 Shape 数量'足够密'不能证明 CANN latency 可精确插值"，Kernel 选择/tiling/融合可能存在非连续边界。

---

## 【表格解读】

### 表 1：五类公开输入参数（逐字还原）

| 参数 | 必选 | 含义 |
|---|---:|---|
| `--database-path` | 是 | 目标性能数据库目录，同时提供设备和软件栈映射 |
| `--rows` | 否 | 每个 CSV 本次最多新增的有效唯一行数，默认 1000 |
| `--target-models` | 是 | 一个或多个 HuggingFace 模型 ID |
| `--ops` | 否 | 最终需要生成的 replay-supported Kernel；未指定时使用模型查询结果 |
| `--seed` | 否 | Coverage 候选的稳定排序种子，默认 0 |

**逐行解读**：

- `--database-path`（必选）：既是性能库所在目录，也承担设备拓扑与软件栈版本映射职责，因此设备、vLLM/PyTorch/CANN 版本信息**不再重复**作为公开参数，统一从此目录的 `op_mapping.yaml` 读取。
- `--rows`（默认 `1000`，可选）：注意语义是**"本轮每个 CSV 至多新增 1000 行"**，不是"最终总行数 1000"。已有行、重复候选、非法候选都不占预算，工具继续追加后续候选，从而实现多次运行的**增量式**扩库。
- `--target-models`（必选）：接受一个或多个 HuggingFace 模型 ID；模型架构元数据驱动内部 workload policy 与扫描组合。
- `--ops`（可选）：最终生成目标集合的覆盖；不传时算子集由"模型查询 ∩ 有 CSV ∩ 有 replay 入口"决定。传入时优先级最高——查询命中走查询网格，未命中走通用理论兜底，且不做模型适用性拦截。
- `--seed`（默认 `0`，可选）：仅影响 CoveragePlanner 候选的**稳定排序**，保证同一配置多次执行时排序可重现，不影响最终 CSV 签名去重结果。

### 表 2：CoveragePlanner 优先级（见"关键机制与数据"节末，已在那里逐行解读；此处不重复）

> 原文除上述参数表与 CoveragePlanner 优先级表外，无其他独立表格。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 数学式或伪代码数学公式；唯一具有公式语义的是：

- **TP 非整除 token 物理 Shape 推导规则（伪代码式描述）**：`ceil(tokens / TP)` 生成最忙 rank 的物理 Shape——符号含义为：分子 `tokens` 是真实请求序列长度，分母 `TP` 是张量并行度，`ceil` 为向上取整函数，作用是确定 Tensor Parallel 中**最忙 rank**（即被多分到一个 token 的 rank）所承载的物理 Shape，从而保证该 rank 不被低估。
- **Batch 上界约束**：`batch × input_length ≤ max_context_length`——符号含义：`batch` 为采样上界、`input_length` 为输入序列长度、`max_context_length` 为模型最大上下文窗口，整体作为 HF 架构自适应的 batch 上界选取条件，且最低保留 `batch=1`，越接近最大 context 采样 batch 越小。
- **TP×EP corner/midpoint 集合**：`{min×max, max×min, max×max, mid×mid}`——四个交叉扫描点，符号含义：`min`/`mid`/`max` 分别取自合法单轴扫描的最小/中位/最大代表点。

其余均为自然语言描述，未给出封闭公式。

---

## 【关联】

文档涉及的关键上下游模块/特性及其相互关系：

- **TensorCast / ServingCast**：实际查询路径的来源——`ProfilingDataSource` 在完成 TensorCast→数据库查询形状投影后记录需求，因此本工具的输入依赖这两条 casting 链路产生的真实查询，而非纯模型结构推导。
- **throughput_optimizer**：工具被驱动调用的核心组件；多次执行其子进程以捕获不同并行/编译/量化组合下的 Kernel 查询；本工具只消费其 query trace，不消费最终最优解；PP 因只改变层在 stage 间归属、不改变单层 Kernel Shape，当前 optimizer 不为不同 PP 数重复生成同一层 Shape。
- **CANNBackendProjector**：版本化的 TensorCast→replay Shape 投影器，与 `op_mapping.yaml` 中声明的软件栈身份绑定；规则随软件栈身份版本化演进。
- **`op_replay/*_run.py`**：replay 支持列表的运行时发现点；最终落库行必须存在对应 replay 脚本，否则在写数据库前报错；通信 Kernel 当前无统一 replay 入口，故只捕获查询、不写 compute CSV。
- **`start_microbench` / op_replay 回填**：本工具写库的耗时字段恒为 0，性能数据由回填环节填入，构成本工具→实测回填→验收五步闭环。
- **`op_mapping.yaml`**：设备/软件栈映射的单一来源；设备、vLLM/PyTorch/CANN 版本从该文件读取，使公开参数保持精简。
- **PR705**：被引用为"已验证的通用查询语义"基线，但本实现代码独立、不依赖其代码或模型数据，避免历史模型特判污染通用契约。
- **CoveragePlanner**：覆盖扩展引擎，输出按上述四级优先级排列；处理联动组（按固定比例共变的维度）与 list-valued runtime metadata 的非笛卡尔扩展。
- **Checkpoint 缓存**（系统临时目录）：与性能数据库隔离；其失效条件串联了 workload policy、目标模型、数据库内容、查询/投影源码摘要四类信息。
- **PP（Pipeline Parallel）特殊说明**：文档明确指出涉及跨 stage 通信或特殊 pipeline kernel 时，应"先在仿真查询层显式建模，再由相同捕获机制自然进入网格"，提示仿真查询层是 PP 类 Shape 的未来入口。
- **关联配置项**：`skip`（通用 generator 明确跳过）、`compute_scale` 四种 regime、FRACTAL_NZ / ND / NCL format 标记。

---

## 【使用方法】

### 启用命令（原文 PowerShell 示例，逐字保留）

```powershell
python tools/perf_data_collection/generate_shape_grid.py `
  --database-path <性能数据库目录> `
  --target-models <HuggingFace模型ID> `
  --rows 1000 `
  --seed 0
```

### 完整参数清单（对应"用户接口"小节，逐字还原）

| 参数 | 必选 | 默认 | 含义 |
|---|:---:|:---:|---|
| `--database-path` | 是 | — | 目标性能数据库目录，同时提供设备和软件栈映射 |
| `--rows` | 否 | `1000` | 每个 CSV 本次最多新增的有效唯一行数 |
| `--target-models` | 是 | — | 一个或多个 HuggingFace 模型 ID |
| `--ops` | 否 | 模型查询结果 | 最终需要生成的 replay-supported Kernel |
| `--seed` | 否 | `0` | Coverage 候选的稳定排序种子 |

### 关键使用语义（原文强调点）

- `--rows 1000` 表示"每个目标 CSV 本轮**最多新增** 1000 行"，不是"最终总行数为 1000"；已有行、重复候选和非法候选都不占预算。
- 重复执行同一命令会复用 checkpoint cache 中已完成的 workload，无需新增公开参数；DB/模型/查询语义变化自动失效；失败或不完整 workload 自动重跑。
- 设备、vLLM/PyTorch/CANN 版本不作为公开参数，统一从 `--database-path` 下 `op_mapping.yaml` 读取。
- 验收不在本工具内：写库后需走"microbench 回填 → replay 成功率检查 → holdout coverage 检查 → 插值误差检查 → text_generate B2B"五步闭环。
