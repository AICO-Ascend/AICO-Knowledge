# 共享专家混置

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/mix_shared_routing.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/mix_shared_routing.md

# 「共享专家混置」深度解读

## 【定位】

本文档系统描述了昇腾 MindIE LLM 推理引擎中 MoE（混合专家）架构下**共享专家（Shared Expert）的三种部署与计算策略**（外置、内置、混置），重点说明"共享专家混置"作为一种将共享专家纳入路由专家负载均衡计算的优化手段，与 Atlas 800I A2/A3 服务器、DeepSeek V3/R1 模型以及专家负载均衡（EPLB）之间的搭配关系及配置方式。

---

## 【技术要点】

1. **三种共享专家部署策略的并行定义**：文档以并列方式给出"外置 / 内置 / 混置"三种模式，每种模式都从**部署位置**（独立 NPU 卡 / 同一 NPU 卡 / 混部）和**负载均衡对象**（仅路由专家 / 路由+共享专家）两个维度进行区分。
2. **三种计算流程的对比**：
   - 外置：`dispatch → 同时计算共享专家和路由专家 → combine`（共享专家与路由专家并行计算）
   - 内置：`共享专家 matmul → dispatch → 路由专家 → combine → 共享专家结果 + 路由专家结果`（共享专家先于路由专家串行启动）
   - 混置：`dispatch → 同时计算共享专家和路由专家 → combine`（**与外置流程形态相同**，但负载均衡计算方式不同）
3. **模型与硬件支持范围**：仅 DeepSeek V3/R1；硬件涉及 Atlas 800I A3 超节点服务器与 Atlas 800I A2 推理服务器两类。
4. **性能叠加条件**：文档明确指出"搭配负载均衡使用，则性能更优"，适用于共享专家外置（144 卡场景）和共享专家混置两种配置方式。
5. **关键配置参数**：`ep_level`、`eplb.level`、`eplb.expert_map_file`、`num_dangling_shared_experts`、`mix_shared_routing`。
6. **144 卡场景专属约束**：仅 Atlas 800I A3 超节点服务器的 144 卡场景支持"单独设置共享专家外置"，且其他场景下共享专家外置不被支持。

---

## 【关键机制与数据】

**工作原理（计算流对比）**

文档将三种模式的计算流建模为 dispatch（分发）与 combine（合并）两个 MoE 通信原语之间的不同组合：

- **外置/混置模式**：dispatch 之后，共享专家与路由专家**同时**被计算，再统一 combine。这意味着共享专家的输入也来自 dispatch 阶段对 token 的分发结果。
- **内置模式**：共享专家先单独完成 matmul（不依赖 dispatch），dispatch 之后再算路由专家，最后 combine 阶段才把"共享专家结果 + 路由专家结果"汇总。**原文无具体数字说明各阶段耗时占比**。

**负载均衡机制的差异（原文要点提炼）**

- 外置：共享专家固定在前几张 NPU 上，**计算负载均衡时只考虑路由专家**。
- 内置：共享专家与路由/冗余专家共卡部署，**计算负载均衡时只考虑路由专家**。
- 混置：**把共享专家作为路由专家来计算负载均衡**——即在负载均衡算法中共享专家获得了与路由专家同等的"被均衡"待遇。

**性能数据**：原文未给出任何 benchmark 数字、吞吐量、时延或加速比，仅以定性表述"性能更优"描述。

---

## 【表格解读】

**原文无表格**。

文档中所有结构化信息均通过 JSON 代码块（参数配置示例）和 Markdown 项目符号呈现，没有以 `<table>` 形式呈现的对比表。以下为对原文三个 JSON 配置块的逐字还原与解读：

**配置块 ①：搭配专家负载均衡（推荐）**

| 参数路径 | 取值 | 解读 |
|---|---|---|
| `models.deepseekv2.ep_level` | `2` | 专家并行等级设为 2（启用 EP=2） |
| `models.deepseekv2.eplb.level` | `1` | 专家负载均衡开关设为 1（开启 EPLB） |
| `models.deepseekv2.eplb.expert_map_file` | `"xxxx.json"` | 指向预先生成的专家部署表（需由 `./expert_parallelism_load_balancer.md#冗余专家部署表生成` 流程产出，路径占位为 `xxxx.json`） |

**配置块 ②：Atlas 800I A3 超节点 144 卡，单独外置共享专家**

| 参数路径 | 取值 | 解读 |
|---|---|---|
| `models.deepseekv2.ep_level` | `2` | 专家并行等级设为 2 |
| `models.deepseekv2.num_dangling_shared_experts` | `32` | 外置（dangling）的共享专家数量为 32 |

**配置块 ③：单独设置共享专家混置**

| 参数路径 | 取值 | 解读 |
|---|---|---|
| `models.deepseekv2.mix_shared_routing` | `true` | 启用"共享专家混置"模式 |

---

## 【公式解读】

**原文无公式**。

文档中没有以 LaTeX 或伪代码形式给出的数学公式。三种模式的计算流程以自然语言 + 箭头（`→`）伪代码方式表达，可视为一种非形式化的算子序列描述：

```
外置/混置：dispatch → 同时计算共享专家和路由专家 → combine
内置：    共享专家 matmul → dispatch → 路由专家 → combine → 共享专家结果 + 路由专家结果
```

符号含义（非原文，仅就其字面逻辑进行解读）：
- `dispatch`：MoE 路由阶段，将 token 分配到目标专家。
- `combine`：MoE 聚合阶段，将专家输出合并回 token。
- `matmul`：标准矩阵乘法，对应共享专家的前向计算。
- `同时计算`：并行执行，无数据依赖。

---

## 【关联】

- **上游依赖 / 配套特性**：文中推荐配置需要先生成"冗余专家部署表"，对应链接 `./expert_parallelism_load_balancer.md#冗余专家部署表生成`——即 **专家负载均衡（EPLB）** 模块。文档明确把"搭配 EPLB"作为推荐使用样例，说明共享专家混置并非独立优化，而是 EPLB 体系下的一个子策略。
- **服务化配置入口**：执行推理前需配置 `config.json`，对应链接 `../user_manual/service_parameter_configuration.md`——即服务化参数配置文档。该文档是本文档中所有 JSON 示例（`models.deepseekv2.*`）的"承载文件"。
- **启动链路**：服务启动章节指向《MindIE Motor 开发指南》"快速入门 \> 启动服务"，说明本文档在 MindIE Motor 服务化调用链路之下运行，并非独立的 CLI/SDK 接口。
- **横向对比**：与同路径下的其他 MoE 优化特性（如 EPLB）属于同一 feature 目录层级，存在配置项 `eplb` 与 `mix_shared_routing` / `num_dangling_shared_experts` 的并列关系，但**文档未给出与 expert parallel / tensor parallel 等并行维度的耦合说明**。

---

## 【使用方法】

**启用方式分三类场景**（原文示例已逐字给出，整理如下）：

### 场景 A：搭配专家负载均衡（推荐）

1. 先按 [冗余专家部署表生成](./expert_parallelism_load_balancer.md#冗余专家部署表生成) 生成专家部署表。
2. 在 `config.json` 中写入：
   ```json
   "models": {
     "deepseekv2": {
       "ep_level": 2,
       "eplb": {
         "level": 1,
         "expert_map_file": "xxxx.json"
       }
     }
   }
   ```
   含义：`ep_level=2` 开启 EP，`eplb.level=1` 开启 EPLB，`expert_map_file` 指向已生成的部署表。

### 场景 B：Atlas 800I A3 超节点 144 卡，单独外置共享专家（不搭配 EPLB）

```json
"models": {
  "deepseekv2": {
    "ep_level": 2,
    "num_dangling_shared_experts": 32
  }
}
```
含义：`num_dangling_shared_experts=32` 表示有 32 个共享专家被独立外置到前几张 NPU 卡。

### 场景 C：单独启用共享专家混置

```json
"models": {
  "deepseekv2": {
    "mix_shared_routing": true
  }
}
```
含义：`mix_shared_routing=true` 表示启用混置模式，负载均衡算法将共享专家视为路由专家进行调度。

### 执行推理步骤（原文已列）

1. 配置服务化参数，详见 [配置参数说明（服务化）](../user_manual/service_parameter_configuration.md)，参数值参见上文三个场景的 JSON 示例。
2. 启动服务，详见《MindIE Motor 开发指南》"快速入门 \> 启动服务"章节（原文指向 https://gitcode.com/Ascend/MindIE-Motor/blob/dev/docs/zh/user_guide/quick_start.md）。

### 约束清单（启用前必读，原文已列）

- 模型：**仅支持 DeepSeek V3/R1**。
- 硬件：
  - 共享专家外置 → **仅** Atlas 800I A3 超节点服务器；且**仅 144 卡场景**支持"单独设置共享专家外置"。
  - 共享专家混置 → 同时支持 Atlas 800I A2 推理服务器 与 Atlas 800I A3 超节点服务器。
- 性能叠加条件：共享专家外置（144 卡）或共享专家混置 → **搭配负载均衡使用时性能更优**。
