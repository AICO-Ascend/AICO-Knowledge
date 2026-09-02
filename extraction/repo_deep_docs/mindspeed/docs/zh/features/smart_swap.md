# SmartSwap

> 仓 `mindspeed` · 路径 `docs/zh/features/smart_swap.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/smart_swap.md

# SmartSwap 文档深度解读

## 【定位】

这篇文档描述的是 mindspeed 中一项名为 **SmartSwap** 的自适应 Swap 内存优化特性，用于解决大模型训练中的 OOM 问题：在不需要用户手写异步换入换出逻辑（区别于传统 Swap 方案）且不引入额外计算开销（区别于重计算方案）的前提下，通过自动迭代生成最优 Swap 策略，使训练在可用最大显存内继续运行。

---

## 【技术要点】

1. **三阶段自适应迭代框架**：SmartSwap 通过「数据采样 → 策略生成 → 策略执行」的闭环循环迭代，依次经历三个阶段：
   - **WarmUp 阶段**：仅执行数据采样，采集 Tensor 生命周期信息；此时 OOM 会被底层内存异常覆盖机制拦截，使模型继续运行。
   - **SearchPolicy 阶段**：同时执行数据采样与策略执行；策略生成包含「候选内存过滤 → 内存策略生成 → 内存模拟排布」三个子步骤。
   - **Stable 阶段**：仅执行策略执行；通过多流异步执行内存 Swap，掩盖对计算流的耗时影响。

2. **三种使用场景**：
   - OOM 场景：拦截 OOM 报错并自动生成 Swap 策略；
   - 非 OOM 场景：根据配置文件中指定的「减少显存值」自动生成 Swap 策略，使训练在指定显存内运行；
   - 重计算替代场景：减少模型代码中的重计算生效范围。

3. **核心配置参数**（`swap_policy_config.py`）：
   - `self.policy_v2 = True` —— v2 开关，简化用户使用；
   - `self.policy_pref = SwapPolicyPref.BETTER_PERFORMANCE` —— 策略偏好：`BETTER_PERFORMANCE` 仅选择 activation；`BETTER_MEMORY_SAVING` 选择 activation 与 optimizer 两部分；
   - `self.swap_bucket_size = -1` —— 控制 swap 每层 tensor 大小（单位 Bytes），默认 `-1`，小于零视为全选；
   - `self.num_attn_layers_per_stage = 1` —— SwapStage 划分粒度，默认 `1` 表示每个 SwapStage 包含一个 attention layer。

4. **静态序列约束**：原文明确 SmartSwap 适配静态序列场景，**暂未适配动态场景（如 MOE 类场景）**。

5. **Host 内存占用**：Swap 将占用 Host 内存，例如单机 8 卡若每卡换出 `30GB` 到 Host，则单机至少需要 Host 内存 `8*30=240GB`。

6. **自定义算子接入方式**：通过 `NPUSwapManager` 的 `BeginHook / TensorHook / PostHook / EndHook` 系列调用嵌入算子前后位置，并修改算子编译代码中的 `include_paths`（添加 `ops/csrc/pluggable_allocator/smart_swap`）与 `extra_ldflags`（链接 `smart_swap` 库），同时设置 `LD_LIBRARY_PATH` 环境变量。

---

## 【关键机制与数据】

**工作原理（自适应策略迭代生成）**

整个特性以「有限次数验证下的最优策略选择」为核心思想，运行流程如原文配图 `smart_swap_flowchart.png` 所示，按时间维度依次走过三个阶段：

| 阶段 | 数据采样 | 策略生成 | 策略执行 | 关键副作用 |
|------|----------|----------|----------|------------|
| WarmUp | ✅ | ❌ | ❌ | OOM 异常被覆盖，使模型继续运行 |
| SearchPolicy | ✅ | ✅（候选过滤→策略生成→模拟排布） | ✅ | 在候选策略中迭代筛选 |
| Stable | ❌ | ❌ | ✅（多流异步执行） | Swap 耗时被计算流掩盖 |

**数据流**

- WarmUp 阶段采集的 Tensor 生命周期信息成为 SearchPolicy 阶段「候选内存过滤」的输入；
- SearchPolicy 阶段生成的策略在执行时通过多流（与计算流并行）异步换入换出，使显存占用在保证计算不中断的前提下压缩到目标值；
- 策略执行的反馈用于在下次迭代中更新策略，形成闭环。

**性能数据（原文标注）**

| 场景 | 配置变更 | 性能收益 |
|------|----------|----------|
| llama2（8p，pp1，seqlen 8k，layer 32） | tp8 → tp1 | **25%** |
| llama2（8p，pp1，seqlen 16k，layer 40） | 关闭全重计算 | **28%** |

> 原文备注：以上数字均为原文给出的实测收益示例，未提供更多基准场景数据。

---

## 【表格解读】

**原文无表格**（文档正文部分未呈现 markdown 表格，仅以代码块与列表形式罗列参数；上述「三阶段对比表」与「性能数据表」均为本解读根据原文信息整理，便于阅读，原文无此结构）。

---

## 【公式解读】

**原文无公式**（文档未包含 LaTeX 或伪代码形式的公式；唯一隐含的计算为注意事项中的 Host 内存估算 `8*30=240GB`，该数字出现在说明性语句中，非公式形式）。

---

## 【关联】

文档涉及的多项内部资源与上下游关系如下（基于原文路径/类名信息）：

- **配置入口**：`mindspeed/core/memory/smart_swap/swap_policy_config.py` —— 全部参数（`policy_v2` / `policy_pref` / `swap_bucket_size` / `num_attn_layers_per_stage`）均定义于该文件。
- **底层头文件**：`NPUSwapManager.h`（位于自定义算子可 include 的路径中），提供 `BeginHook` / `TensorHook` / `PostHook` / `EndHook` 接口，是自定义算子接入 Swap 生命周期的关键。
- **自定义算子示例**：
  - C++ 实现：`mindspeed/ops/csrc/cann/gmm.cpp`（npusmm 算子示例）；
  - 编译入口：`mindspeed/op_builder/gmm_builder.py`（`GMMOpBuilderPublic`），其中 `include_paths` 增加 `ops/csrc/pluggable_allocator/smart_swap`，`extra_ldflags` 增加 `-L ${TORCH_EXTENSIONS_DIR}/smart_swap/ -lsmart_swap`。
- **运行时环境**：训练脚本（如 `pretrain_xxx.sh`）需设置 `TORCH_EXTENSIONS_DIR` 与 `LD_LIBRARY_PATH`，指向已编译好的 smart_swap 扩展库。
- **与已有方案的对比关系**：
  - 与 **重计算** 互为替代关系（场景 3 明确指出）；
  - 与 **传统 Swap** 的关系是「自动化升级」，原文将传统 Swap 描述为「需要用户自己编写和控制异步换入换出时机和内存管理」，SmartSwap 用自适应迭代取代了这一人工成本。
- **流程图**：`docs/zh/features/figures/smart_swap_flowchart.png`（随文档附带，描绘 WarmUp→SearchPolicy→Stable 三阶段流转）。

---

## 【使用方法】

1. **命令行使能**：在训练脚本中添加参数 `--smart-swap`。
2. **配置文件调优（可选）**：编辑 `mindspeed/core/memory/smart_swap/swap_policy_config.py`，原文给出 v2 版本示例配置：

```python
self.policy_v2 = True  # True是开启，False是关闭
self.policy_pref = SwapPolicyPref.BETTER_PERFORMANCE  # BETTER_PERFORMANCE是选择activation，BETTER_MEMORY_SAVING是选择activation和optimizer两个部分
self.swap_bucket_size = -1  # 控制swap每层tensor的大小，单位Bytes。默认-1，小于零即视为全选。
self.num_attn_layers_per_stage = 1  # 指定SwapStage划分粒度。默认1，即每个SwapStage包含一个attention layer。
```

3. **自定义算子接入（仅在用户使用了自定义 cpp 算子时需要）**：
   - 在算子 cpp 代码中 `#include "NPUSwapManager.h"`，并在算子调用前后插入 `BeginHook` / `TensorHook` / `PostHook` / `EndHook` 调用；
   - 在算子编译 builder 的 `include_paths` 中追加 `'ops/csrc/pluggable_allocator/smart_swap'`，并在 `extra_ldflags` 中追加 `-L${TORCH_EXTENSIONS_DIR}/smart_swap/ -lsmart_swap`；
   - 在训练脚本中预先 `export TORCH_EXTENSIONS_DIR=/home/xxx/exts/`，并将 `${TORCH_EXTENSIONS_DIR}/smart_swap/` 注入 `LD_LIBRARY_PATH`。

> 原文未提供更多如多卡启动命令、调度器集成方式等内容。

## 图文联合解读

- `smart_swap_flowchart.png`: 图示AutoPolicy三阶段循环（Warm Up→Search Policy→Stable），及Search阶段Profiling→候选过滤→策略生成→模拟→满足的迭代闭环；右侧SwapExecute展示CPU、NPU计算流、NPU Swap流三流并行执行T2的D2H/H2D异步换入换出，以wait event同步掩盖计算耗时。论证"自适应迭代生成最优Swap策略"与"多流异步隐藏Swap延迟"两大核心结论，与文档中策略生成三阶段、SearchPolicy迭代及Policy Execute多流异步机制一一对应。
