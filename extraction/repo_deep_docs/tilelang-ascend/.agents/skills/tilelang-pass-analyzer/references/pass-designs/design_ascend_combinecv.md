# 1. 背景与目标

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-pass-analyzer/references/pass-designs/design_ascend_combinecv.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-pass-analyzer/references/pass-designs/design_ascend_combinecv.md

# 一体化深度解读: `design_ascend_combinecv.md`

## 【定位】

本文档是 TileLang-Ascend 项目中 `CombineCV` Pass 的设计说明书,目标是**让前端开发者不再显式书写 `with scope("C")/with scope("V")` 来区分 Cube/Vector 核心,而由后端 Pass 自动从 TIR (Tensor IR) 中识别、分离 Cube 与 Vector 类型的计算,并自动生成跨核心 (Cube↔Vector) 的同步代码**,以降低昇腾算子开发门槛并保证数据依赖正确性。

---

## 【技术要点】

1. **硬件异构双核分离**:Ascend NPU 包含 **Cube 核心** (对应 AI Core,负责 GEMM/矩阵乘) 与 **Vector 核心** (对应 AI Vector,负责逐元素/广播/激活)。Pass 需将同一份 TIR 拆成两条执行路径。

2. **API 名称驱动的分类映射**:`callnodeMapPos_` 字典按 intrinsic 名字硬编码归属:
   - Cube 端:`copy_gm_to_l1`, `gemm_v0`, `copy_l1_to_l0a`, `copy_l1_to_l0b`, `copy_l0c_to_gm`, 以及 buffer scope `wmma.matrix_a/b/accumulator`、`shared.l1`。
   - Vector 端:`copy_gm_to_ub`, `copy_ub_to_gm`, `copy_ub_to_ub`, 以及 buffer scope `shared.ub`。

3. **同步管道与读写方向**:`GM_COPY_CFG_INFOS` 字典规定每条 GM 拷贝的管道类型与方向——`copy_gm_to_l1 → MTE2(读)`, `copy_l0c_to_gm → FIX(写)`, `copy_gm_to_ub → MTE2(读)`, `copy_ub_to_gm → MTE3(写)`。三种管道:`MTE2`(搬运入)、`MTE3`(搬出)、`FIX`(L0C 输出)。

4. **同步点匹配与 sync_flag_id 分配**:对同一 `workspace_name`,cube 写 ↔ vec 读、cube 读 ↔ vec 写配成一对,使用统一的 `sync_flag_id`(文档示例中三个 workspace 各自分配 `sync_flag_id = 0/1/2`)。SetFlag 由写者发起,WaitFlag 由读者等待。

5. **跨核心同步插入策略 (`AutoInsertCrossCoreSync`)**:经 `CrossCoreSyncCollector` 收集 → 按 workspace 分组 → 配对 → `FindTargetLoopDepth` 选最优挂载循环层 → `CrossCoreSyncInserter` 实际插入 SetFlag/WaitFlag;支持 `cross_interval > 1` 的跨度同步以减少同步频率。

6. **Pass 开关配置**:测试代码中体现的配置项为 `"tl.ascend_auto_cv_combine"` (Bool),默认 `false`,需通过 `ConfigContext::Create()->AddConfig(...)` 显式开启;同时该 Pass 还串联一个可选的同步插入流程。

7. **输出结构标记**:最终 `PrimFunc` 的根 block 用 `AttrStmt(resource_scope=0)` 包裹 cube 路径,`AttrStmt(resource_scope=1)` 包裹 vec 路径,合并为 `SeqStmt{cube_body, vec_body}`。

---

## 【关键机制与数据】

### 工作原理(原文给出的三层流水线视角)

文档以"cube 完成 GEMM → 通知 → vec 读 GM 入 UB → vec 算 → 写回 GM → 通知 → cube 下一轮"的典型流水线示例,阐明双核交互协议:
- Cube 侧:`copy_gm_to_l1 (MTE2)` → `GEMM computation` → `copy_l0c_to_gm (FIX)` → `SetFlag(sync_id)`。
- Vector 侧:收到 `WaitFlag(sync_id)` → `copy_gm_to_ub (MTE2)` → `Vector computation` → `copy_ub_to_gm (MTE3)` → `SetFlag(sync_id+1)`。
- Cube 下一轮:`WaitFlag(sync_id+1)` 阻塞至 vec 完成写回。

### 数据流(`CrossCoreSyncCollector` 视角)

对每个 workspace 同时记录四元组 `{scope, order, is_write, pipe}` 以及父循环链 `parent_for_nodes` 与可选 `stage_loop`,再经配对器合并为 sync pair,输出每个 pair 一个 `sync_flag_id`。

### 性能/开销表述

文档"技术目标·性能指标"仅给出定性目标:
- "**跨核心同步开销最小化,仅在必要时插入同步**"
- "**同步点选择最优化,减少等待时间**"

> **原文**:除上述定性描述外,**未给出任何具体数字、加速比、吞吐、延迟、benchmark 数值**。

### 同步位置算法(`FindTargetLoopDepth`)

文档以伪代码/自然语言描述:
- 双指针遍历 cube 与 vec 的 `parent_for_nodes` 循环链;
- 累计乘积作为循环次数;
- 取两边次数相等时的**最大深度**作为挂载点;
- 跳过迭代次数为 `1` 的循环与非 const 的共享循环。

文档未给出该算法的具体数学公式,仅给出语义级描述(见下方"公式解读"节说明)。

---

## 【表格解读】

### 表 1:`CrossCoreSyncPoint` 字段说明表(原文逐字还原)

| 字段 | 类型 | 说明 |
|------|------|------|
| scope | int | 核心类型:0=cube, 1=vector |
| order | int | 在该核心内的执行顺序 |
| sync_flag_id | int | 同步标志 ID,匹配的 cube/vec 对使用相同 ID |
| is_write | bool | true=写操作(需要 SetFlag), false=读操作(需要 WaitFlag) |
| workspace_name | string | workspace 缓冲区标识,用于匹配同步对 |
| pipe | string | 管道类型,影响 SetFlag 的具体行为 |
| target_for_node | optional<ForNode*> | 同步语句应挂载的循环层 |
| parent_for_nodes | vector<ForNode*> | IR 节点所在的所有父循环 |
| cross_interval | int | 跨度间隔,用于减少同步频率 |

**逐行解读:**
- `scope ∈ {0,1}` 是同步点的"阵营"标签,0 表示该 sync point 属于 cube 侧,1 表示属于 vec 侧;该值在最终包装时与 `AttrStmt(resource_scope=...)` 一一对应。
- `order` 是同一侧内的相对顺序号,文档同步点匹配示例展示了 cube 端 `[write_order_0, read_order_1, write_order_2]`、vec 端 `[read_order_0, write_order_1, read_order_2]`,并据此两两配对。
- `sync_flag_id` 是 cube↔vec 配对后共享的全局编号,文档示例三个 workspace 分别为 `0/1/2`;匹配规则为 "cube write → vec read" 与 "cube read ← vec write"。
- `is_write` 决定插入 `SetFlag` (写者发出) 还是 `WaitFlag` (读者等待)。
- `workspace_name` 是配对的唯一键:同一 workspace 的两侧读写点才会配成一对。
- `pipe` 在三处取值 `MTE2/MTE3/FIX`,与 `GM_COPY_CFG_INFOS` 表一致,影响 SetFlag/WaitFlag 与对应硬件管道的绑定方式。
- `target_for_node` 与 `parent_for_nodes` 联合支撑 `FindTargetLoopDepth`,用于确定同步语句到底插入哪一层循环。
- `cross_interval` 支持"跨多次迭代才同步一次"的优化:文档示例 `cross_interval = 1` 表示每轮同步;`> 1` 时按循环变量条件判断是否真同步。

---

### 表 2:`callnodeMapPos_` — Stmt 与 CV 分类映射关系表(原文逐字还原)

| Intrinsic / Buffer Scope 名 | 归类 |
|------------------------------|------|
| `copy_gm_to_l1` | cube |
| `gemm_v0` | cube |
| `copy_l1_to_l0a` | cube |
| `copy_l1_to_l0b` | cube |
| `copy_l0c_to_gm` | cube |
| `copy_gm_to_ub` | vec |
| `copy_ub_to_gm` | vec |
| `copy_ub_to_ub` | vec |
| `wmma.matrix_a` | cube |
| `wmma.matrix_b` | cube |
| `wmma.accumulator` | cube |
| `shared.l1` | cube |
| `shared.ub` | vec |

**逐行解读:**
- Cube 侧的 GM→L1、L1→L0A/L0B、L0C→GM 形成完整 "矩阵计算数据流":外部 GM 数据流入 L1 共享缓冲,再分片到 L0A/L0B 寄存器,矩阵乘结果累加到 L0C 后由 FIX 管道写回 GM。
- `gemm_v0` 是矩阵乘 intrinsic,直接归 cube。
- Vector 侧的 `copy_*_ub_*` 全围绕 Unified Buffer (UB) 工作:`copy_gm_to_ub` 是向量化算子最常见的输入路径,`copy_ub_to_gm` 是输出路径,`copy_ub_to_ub` 是 UB 内部重排/广播。
- `wmma.matrix_a/b/accumulator` 与 `shared.l1` 作为 buffer scope 关键字归 cube,与 `shared.ub` 对立——这一对正是文档 "Location Map 构建" 步骤中 `Var → Scope` 映射的来源。
- 该字典是 `CubeEmitter/VecEmitter` 判定一条语句归属的最重要依据之一(与 buffer scope 检查并列)。

---

### 表 3:`GM_COPY_CFG_INFOS` — Stmt 与 Pipeline 的读写映射关系表(原文逐字还原)

| Intrinsic | is_write (read/write) | pipe |
|-----------|------------------------|------|
| `copy_gm_to_l1` | false (读) | `MTE2` |
| `copy_l0c_to_gm` | true (写) | `FIX` |
| `copy_gm_to_ub` | false (读) | `MTE2` |
| `copy_ub_to_gm` | true (写) | `MTE3` |

**逐行解读:**
- 这张表刻画了四条跨 GM 边界搬运的方向性与硬件管道归属,是 `CrossCoreSyncCollector` 构造 `is_write` 与 `pipe` 字段的数据源。
- 两条"读 GM"操作(`copy_gm_to_l1`、`copy_gm_to_ub`)共用 `MTE2` 管道,但分属 cube / vec 两套通路——这是同步匹配时双方能"对上话"的前提:同一 workspace 在 cube 端由 MTE2 读入、在 vec 端由 MTE2 读入,语义对称。
- `copy_l0c_to_gm` 走 `FIX` 管道,是 cube 端独有的"写"动作,通常是同步触发的源头(cube 写 → vec 读)。
- `copy_ub_to_gm` 走 `MTE3` 管道,是 vec 端独有的"写"动作,通常是同步的另一源头(vec 写 → cube 下一轮读)。

---

## 【公式解读】

> **原文无 LaTeX 数学公式**。文档仅以伪代码与自然语言描述算法逻辑。

可保留的算法伪代码(摘自原文,逐字保留原意):

```
FindTargetLoopDepth(cube.parent_for_nodes, vec.parent_for_nodes):
    双指针遍历 cube 与 vec 的循环链
    计算累计循环次数(乘积)
    找到次数相等时的最大深度作为挂载点
    跳过迭代次数为 1 的循环和非 const 的共享循环
```

**符号解释:**
- `cube.parent_for_nodes` / `vec.parent_for_nodes`:分别为 cube 侧与 vec 侧同步点所处的所有外层 `ForNode` 列表(从外到内)。
- "累计循环次数":文档未给出具体记号,语义上可理解为对应该侧从最外层到当前层的迭代次数乘积。
- "最大深度":即最终选定的 `target_for_node` 在循环嵌套中的层级序号。
- "迭代次数为 1 的循环" 与 "非 const 的共享循环":被算法显式跳过——前者无意义,后者无法静态判断同步条件。

同步点匹配伪代码(原文):

```
for each workspace:
    cube ops: [write_order_0, read_order_1, write_order_2]
    vec  ops: [read_order_0,  write_order_1, read_order_2]
    pair: cube[write] ↔ vec[read]
          cube[read]  ↔ vec[write]
    assign: pair_0.sync_flag_id = 0
            pair_1.sync_flag_id = 1
            pair_2.sync_flag_id = 2
```

**符号解释:** `write_order_*` / `read_order_*` 是 `CrossCoreSyncPoint.order` 在 cube/vec 两端的取值;`sync_flag_id` 为全局唯一标志,SetFlag 与 WaitFlag 用同一 ID 才能配对成功。

---

## 【关联】

文档通过系统架构图、流水示例与数据结构,展示了 `CombineCV` Pass 与上下游的清晰关系:

1. **上游 — TIR (PrimFunc)**:`CombineCV` 的输入是 TIR 层的 `PrimFunc`,Pass 在 IR 层工作,需对所有 `EvaluateNode`(对应 intrinsic 调用)与 buffer 定义做后序遍历。
2. **下游 — 输出 PrimFunc**:最终输出仍是 `PrimFunc`,但根 block 结构变为 `SeqStmt{ cube_body, vec_body }`,且每个分支包裹在 `AttrStmt(resource_scope=0/1)` 中——`resource_scope` 是 Ascend 后端识别双核的标记,本 Pass 是其上游生产方。
3. **与 `Location Map` 的耦合**:Pass 第一步即构建 `Var → Scope` 映射,该映射同时被 `CubeEmitter`/`VecEmitter` 用作"buffer scope 检查"的依据——即"是否保留某条语句"的次要判据。
4. **与 `CVCombineEmitter` 的耦合**:`CubeEmitter(is_aiv=F)` 与 `VecEmitter(is_aiv=T)` 是同一份 IR 的双发射器,二者必须保证覆盖原始 IR 的全部语义,否则会出现计算丢失;这一约束是文档要求"前端不显示规定 scope 也能正确分核"的根本保证。
5. **与 `AutoInsertCrossCoreSync` 的可选串联**:`CrossCoreSyncCollector → 匹配分配 → CrossCoreSyncInserter` 是独立子流程;文档将其标注为"可选",与"双路径生成"解耦——意味着可以仅生成双路径、不插入同步(由后续硬件调度或手工 SetFlag/WaitFlag 处理)。
6. **与前端 scope 语法**:文档明确说明本需求开发后,"前端不显示规定 scope,后端自动识别并分离",因此与 `with scope("C") / with scope("V")` 是替代关系而非并行关系。
7. **测试链路**:验证章节给出 `PassContext::Create()` + `ConfigContext::Create()->AddConfig(...)` 的使用范式,说明本 Pass 接入 TileLang 标准的 Pass 管理与配置中心。

---

## 【使用方法】

### 启用方式(原文 UT 测试代码)

```cpp
TEST(CombineCV, ConfigOptions) {
    // 默认:关闭
    PassContext ctx = PassContext::Create();
    EXPECT_FALSE(ctx->GetConfig<Bool>(
        "tl.ascend_auto_cv_combine", Bool(false)).value());

    // 开启
    ctx = PassContext::Create(
        ConfigContext::Create()
        ->AddConfig("tl.ascend_auto_cv_combine", Bool(true))
    );
    EXPECT_TRUE(ctx->GetConfig<Bool>(
        "tl.ascend_auto_cv_combine", Bool(false)).value());

    // 开启 + 跨核心同步配置(原文片段在此被截断)
    ctx = PassContext::Create(
        ConfigContext::Create()
        ->AddConfig("tl.ascend_auto_cv_combine", Bool(true))
        ->AddConfig(...)
    );
}
```

### 配置项(原文明确给出)

| 配置项 | 类型 | 默认值 | 作用 |
|--------|------|--------|------|
| `tl.ascend_auto_cv_combine` | Bool | `false` | 是否启用 CombineCV Pass(自动分核) |

> **原文未涉及**的第二项配置(从 `->AddConf` 被截断处可推测还存在一个"跨核心同步开关"配置,具体名字与默认值未在原文中给出)。文档也**未提供 CLI 命令、Python API、环境变量等其他启用方式**。

### 输出侧使用注意

最终 IR 需通过 `AttrStmt(resource_scope=0)` (cube) 与 `AttrStmt(resource_scope=1)` (vec) 标识分核;具体 `resource_scope` 数值 `0/1` 在文档中显式出现,Ascend 后续算子编译阶段需识别这两个取值。

### 文档截断说明

原文在"测试跨核心同步配置"代码片段的 `->AddConf` 处被截断(可见末尾 `->AddConf`),因此与跨核心同步插入对应的第二个配置项的具体名称、类型与默认值**原文未涉及**;其余章节(背景、架构、详细设计、测试配置首段)信息完整。
