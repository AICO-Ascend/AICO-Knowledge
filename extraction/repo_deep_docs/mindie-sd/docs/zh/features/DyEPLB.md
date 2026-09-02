# 动态专家负载均衡

> 仓 `mindie-sd` · 路径 `docs/zh/features/DyEPLB.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/DyEPLB.md

# 深度解读：动态专家负载均衡 (DyEPLB)

## 【定位】

本文档解决 DiT-MoE 视觉生成模型在专家并行（EP）推理中，因视觉数据空间局部性与扩散去噪时序动态性所共同导致的"专家负载时空双重不均"问题，提供一套**非侵入、可异步、可配置三种模式**的动态专家负载均衡（DyEPLB）方案与配套 API。

---

## 【技术要点】

1. **问题域与架构前提**：方案针对 DiT（Diffusion Transformer）+ MoE（Mixture of Experts）架构。与 LLM 不同，视觉数据的强空间局部性会诱发特定专家过载，且扩散模型去噪过程中专家激活分布存在显著时序动态变化——传统静态负载均衡因无法应对"时空双重异构性"而失效，因此必须采用动态负载均衡。

2. **核心机制**：通过**负载信息动态调整 Rank 上的专家权重**来达到专家负载均衡，从而实现模型推理加速。负载采集与调度被外置到独立线程和进程，以最小化对主推理流程的阻塞。

3. **三种 EP 模式**（通过 `mode` 参数选择）：
   - **A2A（标准 all-to-all）**：通信均衡，为通用场景**推荐方案**。
   - **AG（all-gather）**：需额外做"变换矩阵 × expert scores"的 matmul，适合需全局同步的场景。
   - **EX（可控模式）**：通过 `max_move` 限制单次专家布局改变规模，适合与 offload 共存时降低峰值显存。

4. **与 CPU 卸载互斥**：方案涉及 H2D（Host-to-Device）数据传输，与 [CPU 卸载](cpu_offload.md) 同时使用可能存在**带宽争抢**，需自行调整执行时机。

5. **接入点**：负载采集与权重替换发生在 MoE 前向的 `npu_moe_init_routing` **之后**、`npu_grouped_matmul_finalize_routing` **之前**——这是昇腾 NPU 亲和的算子级 hook 点。

6. **进程拓扑**：EPLB 算法本身以独立进程（`mindiesd.eplb.eplb_scheduler`）方式拉起，主进程通过 `construct_expert_info_transfer_pool` 与之通信（基于 `ip` / `port` / `auth_key`），构成"主推理进程 + EPLB 调度进程"的双进程结构。

---

## 【关键机制与数据】

**工作原理（数据流）**：

```
┌─────────────────┐  收集 expanded_indices   ┌──────────────────┐
│ MoE 前向(主进程) │ ───────────────────────► │ ExpertLoadCollector│
│   npu_moe_init_ │                          └────────┬─────────┘
│   routing       │                                   │ 异步传输
│                 │  ┌────────────────────────────┐   ▼
│                 │  │ DynamicDispatcher          │  ┌──────────────────────┐
│                 │◄─┤ .check_consistency()       │  │ EPLB Scheduler 进程  │
│                 │  │ .update_flag → update_weight│  │ (mindiesd.eplb.eplb_ │
│ npu_grouped_    │  └────────────────────────────┘  │  scheduler)          │
│ matmul_finalize │                                  └──────────────────────┘
└─────────────────┘
```

1. **主进程**：`model.moe_module.block` 上挂载 `ExpertLoadCollector` 与 `DynamicDispatcher`。
2. 每步 forward 中，`npu_moe_init_routing` 输出 `expanded_indices` → 由 `expert_load_collector.collect_expert_load()` 采集 → 通过 worker 线程池（`construct_expert_info_transfer_pool` 建立）异步送往 EPLB 调度进程。
3. **EPLB 调度进程**根据全局负载计算新的专家布局，回传"是否需要更新"信号。
4. 主进程 `dispatcher.check_consistency()` 读取该信号；若 `update_flag=True`，则调用 `update_module_weight_and_map()` 替换 `weight1` / `weight2` 与本地专家映射，然后继续 `npu_grouped_matmul_finalize_routing`。
5. **AG 模式特例**：在算子之间还需用 `dispatcher.get_expert_trans_tensor()` 取出变换矩阵，与 `scores` 做 `torch.matmul` 得到 `trans_scores`，用于后续聚合。

**异步处理边界**（原文）：
> "为了最小程度地减少对主推理的影响，将算法和专家权重的拼接使用额外的线程和进程来处理。"

**负载均衡节流**：通过 `ExpertLoadCollector(lb_interval)` 控制每隔多少步触发一次平衡（默认 1，即每步都采集；实际触发更新仍由 `dispatcher.update_flag` 决定）。

**性能数据**：原文未提供具体加速比、吞吐或显存数字，因此本节不臆造任何性能指标。

---

## 【表格解读】

### 表 1：EPLB 调度进程启动参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `world_size` | 必填 | EP 数 |
| `expert_num` | 必填 | 全局专家数量 |
| `block_num` | 必填 | MoE 层数 |
| `max_move` | — | EX 模式下最大移动专家数量 |
| `redundant` | — | 冗余专家数 |
| `mode` | 必填 | A2A / AG / EX |
| `auth_key` | `secret_key` | 默认读取环境变量 `EPLB_AUTH_KEY` |

**逐行解读**：
- `world_size` / `expert_num` / `block_num`：三者必填，对应 EP 并行度、专家容量与 MoE 层数，构成算法搜索空间的基本维度。
- `max_move`：**仅 EX 模式有效**，限定单次重排可移动的专家上限，是 EX 模式"可控性"的直接体现——限制幅度的同时也限制了峰值带宽/H2D 开销，因此 EX 模式被推荐用于"与 offload 共存"的场景。
- `redundant`：冗余专家数量，用于在部分专家过载时通过冗余备份承接（具体策略原文未给出，属 EPLB 算法内部行为）。
- `mode`：唯一模式选择开关，原文强调三种模式通信特征不同：A2A 通信均衡、AG 需 matmul、EX 可控。
- `auth_key`：进程间通信鉴权，缺省值 `secret_key` 等价于"未配置"，生产环境应显式设置 `EPLB_AUTH_KEY` 环境变量。

### 表 2：`ExpertLoadCollector` 参数

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `expert_num` | `int` | 是 | - | 全局专家数 |
| `lb_interval` | `int` | 否 | `1` | EPLB 间隔步数 |

**逐行解读**：
- `expert_num`：必须与 EPLB 调度进程保持一致，否则跨进程张量语义错位。
- `lb_interval`：采集/调度的时间粒度，默认 `1` 表示每步都上报；当负载变化平缓时可调大以减少跨进程通信开销。

### 表 3：`DynamicDispatcher` 参数

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `expert_num` | `int` | 是 | - | 全局专家数 |
| `weight1` | `Tensor` | 是 | - | UP 权重 |
| `weight2` | `Tensor` | 是 | - | DOWN 权重 |
| `rank_in_group` | `int` | 是 | - | EP 通信组组内编号 |
| `ep_size` | `int` | 是 | - | EP 数 |

**逐行解读**：
- `weight1` / `weight2`：MoE 专家的 UP/DOWN 投影权重，是 `update_module_weight_and_map()` 替换的目标张量；这里只暴露两个权重，说明当前版本**仅针对典型两层 FFN 形式的 MoE**。
- `rank_in_group` 与 `ep_size`：构造 Rank 视角下的本地专家映射所需，决定 `local_expert_indices_map` 等输出维度；二者必须与启动命令的 `world_size` 对齐。

### 表 4：`construct_expert_info_transfer_pool` 参数

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `module` | `Module` | 是 | - | 初始化后的 model |
| `rank_in_group` | `int` | 是 | - | EP 通信组组内编号 |
| `device` | `int` | 是 | - | rank 对应的 device 编号 |
| `ip` | `str` | 是 | - | 与服务端 ip 一致 |
| `port` | `int` | 是 | - | 与服务端 port 一致 |
| `auth_key` | `str` | 否 | `secret_key` | 默认读取环境变量 `EPLB_AUTH_KEY` |

**逐行解读**：
- 这是把 `model` 与 `EPLB Scheduler` 进程对接的"通道工厂"——`ip` / `port` 必须与 `python -m mindiesd.eplb.eplb_scheduler --host ... --port ...` 一致；`auth_key` 缺省读取 `EPLB_AUTH_KEY` 环境变量，与表 1 同源。
- `device` 与 `rank_in_group` 共同标识主进程侧需要把"哪个 Rank 上的哪个 NPU 设备"接入异步传输池。

---

## 【公式解读】

原文无公式。

（注：文中 `trans_scores = torch.matmul(scores, expert_trans_tensor)` 为代码片段而非数学公式，故不纳入"公式"一节；其语义已在【关键机制与数据】AG 模式特例中描述——变换矩阵用于把局部 scores 映射到重排后的专家布局上。）

---

## 【关联】

- **与 [CPU 卸载](cpu_offload.md) 的关系**：原文"技术特点"与"推荐方案"中**两次**显式提及该互斥关系。DyEPLB 的权重替换需要 H2D 传输，CPU 卸载的 offload→reload 同样走 H2D 通道，二者并发时存在**PCIe/NPU H2D 带宽争抢**。因此：
  - 同时启用时需自行调整执行时机（如错峰触发 EPLB 更新）；
  - 推荐在此场景下使用 **EX 模式**，因其 `max_move` 限制了单次传输数据量，可降低峰值带宽压力。
- **与上游 EP 通信的耦合**：DyEPLB 不替代 EP 通信原语（A2A / AG），而是**叠加在 EP 之上的负载重均衡层**——三种 `mode` 与底层 EP 通信模式一一对应（A2A / AG / EX），属于"通信层 + 调度层"的分层设计。
- **与 MoE 算子的耦合**：依赖昇腾亲和算子 `torch_npu.npu_moe_init_routing`（产出 `expanded_indices` 作为负载信号）与 `torch_npu.npu_grouped_matmul_finalize_routing`（消费重排后的权重），属 MindIE-SD 昇腾亲和工具链的一部分。

---

## 【使用方法】

**Step 1 — 启动 EPLB 调度进程**（独立进程）：

```shell
python -m mindiesd.eplb.eplb_scheduler \
    --world_size 2 \
    --host localhost \
    --port 50001 \
    --mode A2A
```

> 必填参数：`world_size`、`expert_num`、`block_num`、`mode`；可选：`max_move`（EX）、`redundant`、`auth_key`。

**Step 2 — 主进程注入采集器与调度器**：

```python
from mindiesd.eplb.dispatcher import DynamicDispatcher
from mindiesd.eplb.collector import ExpertLoadCollector
from mindiesd.eplb.task_manager import construct_expert_info_transfer_pool

model.init()

model.moe_module.block.expert_load_collector = ExpertLoadCollector(expert_num, lb_interval)
model.moe_module.block.dispatcher = DynamicDispatcher(
    expert_num, weight1, weight2, rank_in_group, ep_size)

if eplb_enabled:
    construct_expert_info_transfer_pool(
        module=model, rank_in_group=rank_in_group, device=device,
        ip=host, port=port, auth_key=auth_key)

model.forward()
```

**Step 3 — AG 模式额外步骤**：在 dispatcher 标记更新后做变换矩阵乘法：

```python
if EP_AG and self.dispatcher.update_flag:
    expert_trans_tensor = self.dispatcher.get_expert_trans_tensor()
    trans_scores = torch.matmul(scores, expert_trans_tensor)
```

**Step 4 — 在 MoE 前向关键算子之间接入**：

```python
expanded_tokens, expanded_row_idx, expanded_indices = torch_npu.npu_moe_init_routing(
    tokens, row_idx, indices, tokens.shape[0])

self.expert_load_collector.collect_expert_load(expanded_indices)
self.dispatcher.check_consistency()

if self.dispatcher.update_flag:
    weight1, weight2, local_expert_num, device_indices_map, \
        local_expert_indices_map, local_expert_list = \
        self.dispatcher.update_module_weight_and_map()
    self.weight1 = weight1
    self.weight2 = weight2
    self.local_expert_num = local_expert_num

tokens = torch_npu.npu_grouped_matmul_finalize_routing()
```

**模式选型速查**（原文推荐）：
| 场景 | 推荐模式 |
|------|----------|
| 通用场景 | A2A |
| 需全局同步 | AG |
| 与 CPU 卸载共存 / 抑制峰值显存 | EX |

## 图文联合解读

- `dyeplb_image_1.png`: 图左示 DiT Block 结构（Visual Tokens→Self/Cross-Attention→MoE），右按 Device/Host 分层描绘 MoE 流程：设备侧 Load Collector 采集负载→Host 端 Fast Planning Algorithm 规划→异步回传 Weight Update，三模块标为 Selective。论证"无侵入+异步流水线"设计——采集、规划、拼接在附加线程/进程并行处理，不阻塞推理主流程，与文档"最小化主流程影响""全局同步点可灵活选择"论点相互印证。
