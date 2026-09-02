# Profiler

> 仓 `mstt` · 路径 `profiler/tinker/CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mstt/profiler/tinker/CHANGELOG.md

# Profiler / Optimizer CHANGELOG 深度解读

## 【定位】

本篇文档是 mstt 代码仓中 **profiler/tinker 路径下的 changelog**，用于按版本号追溯其内部两大子模块——**Profiler（性能剖析器）** 与 **Optimizer（优化器/内存仿真器）**——的能力演进与 bug 修复记录，目的是让使用者了解每个版本相对前一版本新增、改动或废弃了哪些与训练&大模型端到端调试调优相关的功能。

---

## 【技术要点】

按两个子模块分别提炼：

### Profiler 子模块

1. **子图前向代码动态提取（1.3.3）**：在子图（sub-graph）级别自动抽取前向计算代码，替代硬编码的 profile 区间。
2. **profile 范围按脚本动态生成（1.3.1b）**：不再依赖人工标注范围，而是基于用户脚本自动生成 profile 区间；同期校正子图 wrap 逻辑并实现 `attention_mask` 的自动化生成。
3. **block adapter 重构（1.3.0 / 1.2.2A）**：通过 `block adapter` 抽象层分别重构 mcore block（1.3.0）和 legacy block（1.2.2A, 4block），并将训练框架的 `import` 统一封装在 adapter 中，以降低对外部训练框架的耦合。
4. **张量信息自动提取（1.2.2）**：profile 阶段自动提取张量（tensor）的元信息，避免手工记录。
5. **计时机制升级（1.2.2）**：将 host 侧 `time.time()` 替换为 `torch.cuda.Event` 的 `elapsed_time()`，并"去除所有 `synchronize` 操作"；同时在计时前增加 `barrier` 以同步各设备，并在 `barrier` 之后再多跑一轮预热、把 `event.start()` 放在预热完成之后。
6. **ModelLink 适配（1.2.0 / 1.3.0）**：分别适配 ModelLink 1.0.RC2（对应原命名方式 ModelLink-1.1）与 1.0.RC3（对应袁明明方式 ModelLink-1.2）。

### Optimizer 子模块

7. **入口改造与并行策略去重（1.3.0）**：重构入口逻辑，并修复并行策略重复的问题。
8. **`dist_opt` 切分调整（1.2.0）**：将分布式优化器状态切分调整为**2 阶优化器状态**与**全精度权重参数**两部分。
9. **内存仿真逻辑完善（1.2.0）**：调整 `reserved` 内存仿真逻辑；新增 `attention_mask` 内存占用仿真；调整 `recompute` 内存仿真，**开启时保留 `input` 内存占用**。

---

## 【关键机制与数据】

### Profiler 1.2.2 的时间测量流水线（原文核心数据流）

| 阶段 | 动作 | 原文表述 |
|---|---|---|
| ① 设备同步 | 各 device 同步就绪 | "在时间测量前新增 `barrier` 同步各设备" |
| ② 预热 | barrier 之后再多跑一轮预热 | "在 `barrier` 之后再多跑一轮预热" |
| ③ 启动事件 | event.start() 置于预热之后 | "并将 `event.start()` 放在预热后" |
| ④ 测量 | 用 CUDA event 计时 | "将 `host` 侧 `time.time()` 时间测量方式修改为 `torch.cuda.Event` 的 `elapsed_time` 测量方式" |
| ⑤ 清理 | 不再阻塞同步 | "去除所有 `synchronize` 操作" |

**工作原理（原文）：** 通过 `barrier` + "额外一轮预热 + `event.start()` 延后到预热后" 的组合，把 GPU 上首次 kernel 启动（jit/cuDNN benchmark 等）造成的尾延迟从正式计时区间中剥离；改用 `torch.cuda.Event` 异步计时后，去掉 host 侧 `synchronize` 可避免 CPU/GPU 串行等待带来的统计偏差。

### Profiler 1.3.1b 的"动态化"链路（原文）

> "根据脚本动态生成 profile 范围 → 校正子图 wrap 逻辑 → 自动化生成 `attention_mask`"

含义：用户脚本本身成为 profile 范围的事实来源（不再依赖手工注解）；子图 wrap 层负责把范围正确包裹到模型子图上；`attention_mask` 不再由用户手写，而是 wrap 阶段自动派生。

### Optimizer 1.2.0 的内存仿真改进（原文）

- **`dist_opt` 切分内容**：从原文表述看，切分由"2 阶优化器状态"与"全精度权重参数"两部分构成（隐含前提：低精度权重/梯度不进入该切分范围）。
- **`attention_mask` 内存占用仿真**：新增条目，意味着 Optimizer 现在会把 `attention_mask` 的显存占用纳入仿真预算。
- **`recompute` 内存仿真**：原文"开启时保留 `input` 内存占用"，指 recompute 激活重计算开启时，输入张量的显存占用需被保留（因为重计算需要以 input 为锚点重放前向）。

> 注：以上数据/机制均直接来源于原文条目，原文未给出绝对数值（如具体 MB、ms、版本号以外的具体数字），故不再补充。

---

## 【表格解读】

**原文无表格。**

（文档为 changelog 列表式叙述，未出现参数表/性能对比/配置项表格。）

---

## 【公式解读】

**原文无公式。**

（文档未出现 LaTeX、伪代码或可识别为数学表达式的公式。Profiler 1.2.2 中提到的 `elapsed_time` 是 API 名而非公式；`barrier`、`event.start()` 是命令名。）

---

## 【关联】

基于原文条目，可梳理出的模块依赖与上下游关系：

1. **ModelLink（外部依赖 / 适配对象）**
   - Profiler 1.2.0 适配 **ModelLink 1.0.RC2**（对应原命名方式 ModelLink-1.1）。
   - Profiler 1.3.0 适配 **ModelLink 1.0.RC3**（对应袁明明方式 ModelLink-1.2）。
   → Profiler 的能力边界受 ModelLink 版本约束，是典型的"上游训练框架适配"链路。

2. **Block Adapter（内部抽象层）**
   - Profiler 1.2.2A：`使用 adapter 封装对训练框架的 import` + `使用 block adapter 重构 legacy block (4block)`。
   - Profiler 1.3.0：`使用 block adapter 重构 mcore block`。
   → Adapter 同时承担两件事：① 把训练框架的 import 隔离在 adapter 内（屏蔽外部 API 变动），② 统一 legacy / mcore 两套 block 的 profile 接入方式。

3. **子图 wrap 逻辑 ↔ attention_mask**
   - Profiler 1.3.1b：`校正子图 wrap 逻辑，自动化生成 attention_mask`。
   → 子图 wrap 是 attention_mask 自动生成的执行点，二者绑定演进。

4. **Optimizer ↔ Profiler（共享语义）**
   - Optimizer 1.2.0 中 `attention_mask` 内存占用仿真 与 Profiler 1.3.1b 的 `attention_mask` 自动化生成 形成上下游呼应：Profiler 负责"运行时是否生成 / 如何生成"，Optimizer 负责"事前仿真时应分配多少显存预算"。

5. **recompute / dist_opt / reserved 三条内存仿真线（Optimizer 1.2.0）**
   - 三者在同一版本集中调整，表明 Optimizer 的内存仿真模型是一次整体重构（reserved 基础盘 + dist_opt 分布式切分 + recompute 激活重算 + attention_mask 注意力掩码），覆盖分布式训练下的全部主要显存来源。

6. **Profiler 1.3.3 ↔ 1.3.1b**
   - 1.3.1b 实现"profile 范围动态生成 + 子图 wrap"，1.3.3 在此基础上加入"子图前向代码动态提取"，是从"范围自动化"到"代码本身自动化"的递进。

---

## 【使用方法】

**原文未涉及。**

changelog 仅描述"做了什么改动"，并未给出：
- 启用 profile 的具体命令行 / 配置项；
- Optimizer 内存仿真器的调用接口；
- block adapter 的注册 / 接入方式；
- ModelLink 1.0.RC2 / RC3 的版本号约束条件。

如需这些信息，应查阅 mstt 仓内 profiler/tinker 的 README 或使用文档（非本 changelog 内容）。
