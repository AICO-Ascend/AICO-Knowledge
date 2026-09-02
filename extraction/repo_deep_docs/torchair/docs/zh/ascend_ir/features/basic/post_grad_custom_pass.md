# 自定义FX图Pass功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/post_grad_custom_pass.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/post_grad_custom_pass.md

# 一体化深度解读: 自定义FX图Pass功能

---

## 【定位】

本文档解决的是 TorchAir 编译流程中"用户如何介入并修改 AOT 编译后的 PyTorch FX 图"的问题, 提供了一套基于 `torchair.CompilerConfig` 的自定义 Pass 注册机制, 使开发者能在内置 Pass 之前或之后插入自己的 FX 图变换逻辑, 从而实现图内多流并行、算子时序重排等定制化优化。

---

## 【技术要点】

1. **强约束的 Pass 函数签名**: 自定义 Pass 必须遵循 `def _(gm, example_inputs, config: torchair.CompilerConfig) -> None` 的签名; `gm` 是 AOT 编译后的 `GraphModule` 对象 (其 `gm.graph` 即为 FX 图), `example_inputs` 是 `FakeTensor` 类型输入 (通常无需使用), `config` 是 `CompilerConfig` 对象 (用于感知完整编译选项)。

2. **原地修改 + 无返回值约定**: Pass 必须原地修改 `gm` 对象, 任何返回值都会被忽略; 无法处理的情况应抛出异常, 不抛出异常时则必须保证修改后 FX 图的执行结果与修改前完全一致。

3. **两个注册阶段 (内置 Pass 前后)**: 通过 `config.post_grad_custom_pre_pass` 可让自定义 Pass 在 TorchAir 内置 FX 图优化 Pass **执行前**生效; 通过 `config.post_grad_custom_post_pass` 可让自定义 Pass 在内置 Pass **执行后**生效; 两者均接受自定义 Pass 函数作为入参。

4. **图节点操控通过 FX Graph API 完成**: 修改图时使用 `fx_graph.inserting_before(node)` / `fx_graph.inserting_after(node)` 上下文管理器配合 `fx_graph.call_function(...)` 来插入新节点; 通过 `node.op == "call_function"` 与 `node.target == torch.ops.aten.<op>.default` 匹配目标算子。

5. **多流/时序控制四元组**: 在 `air` 命名空间下提供四个算子用于流与时序操控——`torch.ops.air.scope_enter.default` (进入新流)、`torch.ops.air.scope_exit.default` (退出新流)、`torch.ops.air.record.default` (记录事件)、`torch.ops.air.wait.default` (等待事件); `wait` 节点通过 `args=([record_node],)` 引用上游 `record` 节点。

6. **辅助验证手段**: 通过 `torchair.logger.setLevel(logging.DEBUG)` 打开 Debug 日志查看插入节点; 通过 `config.debug.graph_dump.type = "pbtxt"` 与 `config.debug.graph_dump.path = "./graph_dump"` 在 max-autotune 模式下 dump 图; 通过 `config.ge_config.optimization_switch = "AutomaticUbFusion:off"` 关闭算子融合以便在 Profiling 中清晰观测分流与时序; 通过 `torch_npu.profiler` 输出 `./prof` 目录的 profiling 文件。

---

## 【关键机制与数据】

**工作原理 (以"图内多流并行计算"示例):**

原文以一个包含 `mm`、`abs`、`add`、`sub` 四个算子的 `Model` 为输入网络, 目标是将 `mm` 与 `abs` 放到名为 `stream_1` 的新流上执行, 并让 `sub` 在 `abs` 之后执行。其机制分两步:

- **流绑定 (Stream Binding)**: Pass 在 `torch.ops.aten.mm.default` 节点前插入 `torch.ops.air.scope_enter.default` (参数 `(["_user_stream_label"], ["stream_1"])`), 在 `torch.ops.aten.abs.default` 节点后插入 `torch.ops.air.scope_exit.default`, 由此 `[scope_enter, scope_exit]` 区间内的算子将在 `stream_1` 上执行。
- **跨流时序 (Cross-Stream Ordering)**: Pass 在 `torch.ops.aten.abs.default` 节点后插入一个 `torch.ops.air.record.default` 节点 (保存为 `record_node`), 在 `torch.ops.aten.sub.Tensor` 节点前插入 `torch.ops.air.wait.default`, 其 `args=([record_node],)` 引用上游 `record` 节点, 由此 `sub` 必须等待 `record` 之前的所有节点执行完才能开始。

原文为示例性质, **未提供性能数据 (如加速比、吞吐提升、延迟数据等)**, 故本节不杜撰数字。

**数据流概览 (基于原文示例):**

```
x ──┬──► mm ──► abs ──► add ──► (return add)
    └──► sub ◄── wait ◄── record (由 abs 后插入)
                          ▲
stream_1: scope_enter ──► [mm, abs] ──► scope_exit
```

(注: 上述为对原文节点插入位置的逻辑重建, 原文未给出此图, 仅作为辅助理解。)

---

## 【表格解读】

原文包含一个参数表 (表 1), 逐字还原如下:

| 参数名 | 说明 |
| -- | -- |
| `post_grad_custom_pre_pass` | TorchAir 本身内置了部分 FX 图优化 Pass, 该配置控制自定义 Pass 在内置 Pass **执行前**生效。传入自定义 Pass 函数。 |
| `post_grad_custom_post_pass` | TorchAir 本身内置了部分 FX 图优化 Pass, 该配置控制自定义 Pass 在内置 Pass **执行后**生效。传入自定义 Pass 函数。 |

**逐行解读:**

- **`post_grad_custom_pre_pass`**: 控制"前置"自定义 Pass 的插槽。其语义是当用户希望自己的图变换先于 TorchAir 内置 Pass 生效时使用; 典型场景是希望在图还未被内置优化动过之前先做结构调整 (例如插入流控制节点), 避免被后续融合 Pass "吃掉"。入参为一个符合 `def _(gm, example_inputs, config)` 签名的 Python 函数。
- **`post_grad_custom_post_pass`**: 控制"后置"自定义 Pass 的插槽。其语义是在 TorchAir 内置优化已经跑完之后再做修改; 典型场景是基于已被优化后的图做最终调整 (例如对已经融合的子图做算子替换或注释注入)。入参同样是符合签名的 Python 函数。
- 两参数互不冲突, 可单独或同时使用; 原文示例中默认仅启用 `post_grad_custom_pre_pass`, 而 `post_grad_custom_post_pass` 以注释形式给出作为可选方案。

---

## 【公式解读】

原文给出的 Pass 函数签名如下, 逐字保留:

```python
def _(gm, example_inputs, config: torchair.CompilerConfig) -> None
```

**符号含义:**

- **`_`**: 函数名占位符, 原文以下划线命名示意, 实际可取任意合法 Python 标识符 (如示例中的 `_custom_pre_pass`)。表示"这是被注册到 TorchAir 的回调函数"。
- **`gm`** (`GraphModule` 类型): AOT (Ahead-of-Time) 编译阶段生成的 `GraphModule` 对象, 内含完整的 FX 图; 通过 `gm.graph` 即可获得 `fx.Graph` 实例进行节点遍历与修改。
- **`example_inputs`** (FakeTensor 列表类型): 与 `gm` 配套的 `FakeTensor` 类型输入, 用于在符号化层面追踪形状与 dtype; 原文明确指出"通常不需要使用"。
- **`config`** (`torchair.CompilerConfig` 类型): TorchAir 编译后端创建的 `CompilerConfig` 对象, 暴露完整编译选项 (如 `debug`、`ge_config` 等), 让自定义 Pass 能根据编译模式 (如是否 max-autotune) 决定自身行为。
- **`-> None`**: 返回类型注解, 强调 Pass 不应有返回值——返回值会被 TorchAir 忽略。

此外, 示例中插图所用的四类节点调用形式 (伪代码, 原文形式):

```python
fx_graph.call_function(torch.ops.air.scope_enter.default,
                       args=(["_user_stream_label"], ["stream_1"]))
fx_graph.call_function(torch.ops.air.record.default, args=())
fx_graph.call_function(torch.ops.air.scope_exit.default, args=())
fx_graph.call_function(torch.ops.air.wait.default, args=([record_node],))
```

**符号含义:**

- `torch.ops.air.scope_enter.default` 的两个参数依次为**流标签列表** (`["_user_stream_label"]`) 和**流名列表** (`["stream_1"]`), 表明该流用于用户自定义的并行调度; `scope_exit.default` 无参数, 与最近的 `scope_enter` 配对。
- `record.default` 无参数, 在节点序列中充当"事件锚点"。
- `wait.default` 的参数是一个单元素列表, 内容为要等待的上游 `record_node` 引用, 表达"先于 `sub` 节点执行的前置依赖"。

---

## 【关联】

本特性处于 TorchAir 编译流水线的 FX 图优化阶段, 与以下模块/特性存在上下游或配套关系:

- **上游 (配置入口)**: [`CompilerConfig`](../../api/torchair/compiler_config.md) — 自定义 Pass 通过其 `post_grad_custom_pre_pass` / `post_grad_custom_post_pass` 两个属性注册; 同时其 `debug.graph_dump` 与 `ge_config.optimization_switch` 子配置在本示例中被联动使用。
- **Debug 日志通道**: [TorchAir Python 层日志打印](python_log_print.md) — 验证 Pass 是否生效的首要手段, 通过 `torchair.logger.setLevel(logging.DEBUG)` 开启后可在日志中观察插入的新节点及其位置。
- **图结构落盘**: [算子 data dump 功能](../advanced/data_dump.md) — 通过 `config.debug.graph_dump` dump 出的图 (`.pbtxt`) 可用于静态查看算子时序是否符合预期。
- **Profiling 观测**: [性能分析案例](../../../appendix/cases/performance_cases.md#性能分析案例) — 通过 `torch_npu.profiler` 输出的 profiling 文件动态验证算子的分流 (不同 stream 上的并发执行) 与时序控制 (跨流 wait/record 的依赖关系) 是否如预期。
- **运行时算子**: 本文依赖 `torch.ops.air.scope_enter` / `scope_exit` / `record` / `wait` 四个 AIR 自定义算子完成流绑定与事件同步, 这类算子是 TorchAir 在 NPU 上实现多流并行的底层原语。

---

## 【使用方法】

**完整启用流程 (基于原文示例代码):**

1. **导入与日志开启**:
   ```python
   import torch, torch_npu, torchair, logging
   from torchair import logger
   logger.setLevel(logging.DEBUG)
   ```

2. **定义网络** (`Model` 类, 包含 `mm → abs → add`、`sub(x, mm)` 等算子)。

3. **编写自定义 Pass**, 函数签名严格遵循 `def _(gm, example_inputs, config: torchair.CompilerConfig)`, 内部通过遍历 `gm.graph.nodes`, 在目标 `call_function` 节点前后用 `inserting_before` / `inserting_after` 上下文调用 `fx_graph.call_function(...)` 插入 `air` 算子。

4. **创建并配置 `CompilerConfig`**:
   ```python
   config = torchair.CompilerConfig()
   config.post_grad_custom_pre_pass = _custom_pre_pass
   # 可选: config.post_grad_custom_post_pass = _custom_pre_pass
   # 可选: config.debug.graph_dump.type = "pbtxt"
   # 可选: config.debug.graph_dump.path = "./graph_dump"
   # 可选: config.ge_config.optimization_switch = "AutomaticUbFusion:off"
   ```

5. **编译与执行**:
   ```python
   npu_backend = torchair.get_npu_backend(compiler_config=config)
   model = Model().npu()
   opt_model = torch.compile(model, backend=npu_backend)
   x = torch.randn([3, 3]).npu()
   opt_model(x)
   ```

6. **Profiling (可选, 用于验证分流与时序)**:
   ```python
   experimental_config = torch_npu.profiler._ExperimentalConfig(
       profiler_level=torch_npu.profiler.ProfilerLevel.Level2)
   with torch_npu.profiler.profile(
       activities=[torch_npu.profiler.ProfilerActivity.NPU,
                   torch_npu.profiler.ProfilerActivity.CPU],
       with_stack=True, record_shapes=False, profile_memory=False,
       schedule=torch_npu.profiler.schedule(wait=0, warmup=0, active=1, repeat=1, skip_first=0),
       experimental_config=experimental_config,
       on_trace_ready=torch_npu.profiler.tensorboard_trace_handler("./prof")) as prof:
       opt_model(x)
       prof.step()
   ```

**关键配置项汇总 (均来自原文):**

| 配置项 | 作用 | 取值/默认值 |
| -- | -- | -- |
| `config.post_grad_custom_pre_pass` | 注册前置自定义 Pass | 自定义 Pass 函数 |
| `config.post_grad_custom_post_pass` | 注册后置自定义 Pass (可选) | 自定义 Pass 函数 |
| `config.debug.graph_dump.type` | 设置 dump 图的类型 (可选, 用于验证) | `"pbtxt"` |
| `config.debug.graph_dump.path` | 设置 dump 图的输出目录 (可选) | `"./graph_dump"` |
| `config.ge_config.optimization_switch` | 关闭算子融合, 便于在 Profiling 中清晰观测分流 (可选) | `"AutomaticUbFusion:off"` |
| `torchair.logger` 日志级别 | 验证插入节点及位置 (Debug 模式可见新节点) | `logging.DEBUG` |
