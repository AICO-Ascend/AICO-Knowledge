# How to debug the vLLM-torch.compile integration

> 仓 `vllm` · 路径 `docs/design/debug_vllm_compile.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/debug_vllm_compile.md

# docs/design/debug_vllm_compile.md 深度解读

---

## 【定位】

这篇文档是 vLLM-torch.compile 集成出现问题时的**调试指南**，系统性地说明如何用 `tlparse` 获取编译日志、如何通过层级化开关（flag）逐级关闭 vLLM-torch.compile 流水线的各个子系统、如何识别与处理 TorchDynamo 图断裂、动态形状约束违规与 guard 问题，从而定位故障子系统并最小化对性能的影响。

---

## 【技术要点】

1. **分层关闭策略（六级开关）**：vLLM 暴露了从最粗粒度到最细粒度的 6 个开关，可在不停 CUDAGraphs/Inductor/vLLM IR 的前提下，分别关闭 vLLM-torch.compile 集成的不同部件（详见下方表格）。
2. **vLLM-compile ≠ torch.compile**：vLLM-compile 是基于 PyTorch Compile 内部 API 自定义的编译器，并非 torch.compile 本身；可通过 `-cc.mode=1`（`CompilationMode.STOCK_TORCH_COMPILE`）切回原生 torch.compile。
3. **四级编译流水线**：(1) TorchDynamo 全图捕获（动态 batch size / token 数）→(2) 可选的图切分/特化，并用 TorchInductor（含 vLLM 自定义 pass 与 vLLM IR lowering）编译 →(3) 产物写入 vLLM compile cache 复用 →(4) 应用 CUDAGraphs 降低 CPU 开销。任何一步出错都需要独立定位。
4. **tlparse + TORCH_TRACE 收集日志**：通过环境变量 `TORCH_TRACE=<dir>` 在 trace 过程中为每个 rank 生成一份日志文件，再用 `tlparse <rank_0_log_file>` 生成 HTML（默认输出到 `./tl_out/index.html`）；查看 `compilation_metrics` 可获取 batch size 的 symbolic constraints。
5. **动态形状假设**：vLLM 假设 torch.compile 添加的所有 guard 都是可安全丢弃的，不会把编译图约束到特定输入形状；若违反将引发运行时错误或 `ConstraintViolationErrors`；可通过 `-cc.dynamic_shapes_config.type=unbacked` 或 `=backed_size_oblivious` 切换到更严格的动态形状模式来排查。
6. **TorchDynamo 全图要求**：vLLM 要求模型 forward 必须能通过 fullgraph 模式被捕获；对动态 batch size 的分支（如 `if data.size[0] % 128 == 0`）属于不可捕获，需改写或封装为 custom op（TorchDynamo 不会 trace 进 custom op）。

---

## 【关键机制与数据】

**原文：** vLLM-torch.compile 流水线由四个步骤组成，**任一步都可能出错**：
1. TorchDynamo 对模型做**全图捕获**，图的动态维度是 batch size（即 token 数）。
2. vLLM 可选地**切分和/或特化**该图，然后用 TorchInductor 把每个图编译成编译产物；该步可能使用 vLLM 自定义 Inductor pass 进一步优化图，包括 vLLM IR lowering 以消除 dispatch 开销。
3. 编译产物被保存到 **vLLM compile cache**，以便将来加载。
4. vLLM 应用 **CUDAGraphs** 来降低 CPU 开销。

**原文：** vLLM 默认编译**一个图**为一个产物，并用该产物覆盖所有 batch size；若代码不能用 Dynamic Shapes 捕获，可能出现「silent incorrectness、loud errors 或 CUDA illegal memory access」三类症状。

**原文：** IR torch wrap 默认仅在 `mode=VLLM_COMPILE` 且 `backend="inductor"`（默认）时启用；可通过 `ir_enable_torch_wrap=False` 关闭。

**原文：** TLDR 明确指出：使用 `tlparse` 收集 torch.compile 日志，**务必将日志附在 bug 报告/支持请求中**。

---

## 【表格解读】

**逐字还原原表**：

| Online Flag                    | Offline Flag                                                                   | Result                                               |
|--------------------------------|--------------------------------------------------------------------------------|------------------------------------------------------|
| --enforce-eager                | enforce_eager=True                                                             | Turn off torch.compile and CUDAGraphs                |
| -cc.mode=0                     | compilation_config=CompilationConfig(mode=CompilationMode.NONE)                | Turn off torch.compile only                          |
| -cc.mode=1                     | compilation_config=CompilationConfig(mode=CompilationMode.STOCK_TORCH_COMPILE) | Turn off vLLM-compile modifications to torch.compile |
| -cc.cudagraph_mode=NONE        | compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE)        | Turn off CUDAGraphs only                             |
| -cc.backend=eager              | compilation_config=CompilationConfig(backend='eager')                          | Turn off TorchInductor                               |
| -cc.ir_enable_torch_wrap=False | compilation_config=CompilationConfig(ir_enable_torch_wrap=False)               | Turn off vLLM IR wrapping                            |

**逐行解读**：

| 行 | 含义 |
|---|---|
| 1 (`--enforce-eager` / `enforce_eager=True`) | **最粗粒度**：同时关闭 torch.compile 与 CUDAGraphs，进入纯 eager 模式；性能损失最大但可靠性最高，适合快速判断问题是否出在整条集成链路上。 |
| 2 (`-cc.mode=0` / `CompilationMode.NONE`) | **保留 CUDAGraphs，但关闭 torch.compile**：用于隔离 torch.compile 自身的图捕获、编译、guard 等问题。 |
| 3 (`-cc.mode=1` / `CompilationMode.STOCK_TORCH_COMPILE`) | **关闭 vLLM-compile 对 torch.compile 的修改**：仍用 torch.compile，但跑原生版本（无 vLLM 自定义 Inductor pass / IR lowering 等）；用于判断问题是否由 vLLM 自定义编译逻辑引入。 |
| 4 (`-cc.cudagraph_mode=NONE` / `CUDAGraphMode.NONE`) | **关闭 CUDAGraphs，保留 torch.compile**：用于隔离 CUDAGraphs 阶段（replay、设备捕获、动态 shape 等）的问题。 |
| 5 (`-cc.backend=eager` / `backend='eager'`) | **关闭 TorchInductor**：torch.compile 仍会运行（如 Dynamo 捕获、guard 等），但不再用 Inductor 生成 fused kernel，便于排查 Inductor codegen 层面的问题。 |
| 6 (`-cc.ir_enable_torch_wrap=False` / `ir_enable_torch_wrap=False`) | **关闭 vLLM IR 的 torch wrap**：vLLM IR 默认会在 `mode=VLLM_COMPILE + backend="inductor"` 下做 functionalization/custom fusions/lowering；关闭后可观察 eager 调度行为，便于排查 vLLM IR 自身问题。 |

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **vLLM-torch.compile 集成设计**：文档开头在「Things can go wrong in each of the four steps」一段明确引用 `./torch_compile.md` 作为更详细的设计文档；该文档与本调试指南是同一主题的「设计 ↔ 排错」配对。
- **vLLM IR 设计**：与本调试指南中 `-cc.ir_enable_torch_wrap=False`、vLLM IR lowering、`functionalization / custom fusions / lowering` 直接相关；详见 `./vllm_ir.md`。
- **Dynamic Shapes 与 vLLM Guard Dropping**：本指南的「Debugging constraint violations and dynamic shapes guards issues」一节与 `torch_compile.md#dynamic-shapes-and-vllm-guard-dropping` 直接对应——该内部链接指向 vLLM 默认假设「所有 torch.compile 添加的 guard 都可安全丢弃」的设计动机与机制，本指南负责该假设被违反时的诊断与更严格模式切换。
- **torch.compile 前端（TorchDynamo）**：依赖 PyTorch Dynamo 的 fullgraph 捕获能力；图断裂需向 pytorch/pytorch 上游提交 issue，文中明确引导用户跳到 PyTorch Dynamo 指南。
- **vLLM compile cache**：四级流水线的第 3 步保存编译产物，调试时若切换 mode/backend 需注意缓存复用可能导致旧产物被加载——文档未明示此交互，但属于流水线耦合点。

---

## 【使用方法】

**1. 安装 tlparse：**
```sh
pip install tlparse
```

**2. 收集 torch.compile 日志（offline）：**
```sh
TORCH_TRACE=~/trace_dir python my_script.py
tlparse ~/trace_dir/<rank_0_log_file>
```

**3. 收集 torch.compile 日志（serving）：**
```sh
TORCH_TRACE=~/trace_dir vllm serve
# ctrl-c out of the server
tlparse ~/trace_dir/<rank_0_log_file>
```
HTML 默认输出至 `./tl_out/index.html`。

**4. 完全关闭 vLLM-torch.compile（含 CUDAGraphs）：**
```sh
vllm serve --enforce-eager
```
```py
LLM(model, enforce_eager=True)
```

**5. 仅关闭 torch.compile：**
```sh
vllm serve -cc.mode=0
```
```py
from vllm.config.compilation import CompilationConfig, CompilationMode
LLM(model, compilation_config=CompilationConfig(mode=CompilationMode.NONE))
```

**6. 切回原生 torch.compile（关闭 vLLM-compile 修改）：**
```sh
vllm serve -cc.mode=1
```
```py
LLM(model, compilation_config=CompilationConfig(mode=CompilationMode.STOCK_TORCH_COMPILE))
```

**7. 仅关闭 CUDAGraphs：**
```sh
vllm serve -cc.cudagraph_mode=NONE
```
```py
from vllm.config.compilation import CompilationConfig, CUDAGraphMode
LLM(model, compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE))
```

**8. 仅关闭 TorchInductor：**
```sh
vllm serve -cc.backend=eager
```
```py
LLM(model, compilation_config=CompilationConfig(backend='eager'))
```

**9. 关闭 vLLM IR wrapping（捕获 eager dispatch 行为）：**
```sh
vllm serve -cc.ir_enable_torch_wrap=False
```
```py
from vllm.config.compilation import CompilationConfig
LLM(model, compilation_config=CompilationConfig(ir_enable_torch_wrap=False))
```

**10. 切换更严格的动态形状模式以排查 guard 问题：**
```sh
vllm serve meta-llama/Llama-3.2-1B -cc.dynamic_shapes_config.type=unbacked
vllm serve meta-llama/Llama-3.2-1B -cc.dynamic_shapes_config.type=backed_size_oblivious
```

**注意事项**：
- 排查动态形状 guard 问题时，重点在 `tlparse` 输出中查看 `compilation_metrics` 的 symbolic constraints；若有任何约束限制了 batch size，则图未真正做到 full dynamic capture。
- 对于无法被 Dynamo 捕获的 token-related 分支，要么改写代码，要么把分支逻辑封装为 custom operator（TorchDynamo 不会 trace 进 custom op）。
- **文档在「Debugging constraint violations and dynamic shapes guards issues」末尾的 offline unbacked 模式代码示例被截断**（原文止于 `DynamicShapesConfig,`），需参照 vLLM 仓库 `vllm/config/compilation.py` 中 `DynamicShapesConfig` 的实际字段补全。

## 图文联合解读

- `design_diagram.png`: **图文联合解读：**

**图示内容：** 四阶段流水线。① graph capture：捕获完整计算图（foo→attention→bar）。② graph splitting：按可缓存性拆分子图——绿色（foo、bar）可缓存，粉色（attention）不可缓存。③ Inductor compile + custom passes：仅对可缓存子图做 backend 编译，产出 artifact_0/artifact_1。④ CUDAGraphs wrapper：将 artifact 嵌入带 `cuda_graphs()` 上下文的 run()。

**技术结论：** vLLM-torch.compile 集成由多个**正交可关**的环节串联而成：捕获→切分→编译→CUDAGraph 录制，每一环出错都可能独立引起回归。

**与文档关系：** 图中每个阶段正对应文档表格中的一组开关：`-cc.mode=0` 关闭 ②③，`-cc.backend=eager` 关闭 ③，`-cc.cudagraph_mode=NONE` 关闭 ④，`--enforce-eager` 关闭 ③④。图形直观印证了"逐层禁用以定位故障"的调试方法论。
- `tlparse_inductor.png`: **1) 图中内容**
左面板为Chrome Trace"Chromium Events"视图,列出PT2编译产生的0–13号构建产物(trace event),其中第10项`inductor_output_code_cxt577…`被红框高亮;红色箭头指向右面板,即展开该文件后的Triton JIT内核源码——含`@triton_heuristics.pointwise`装饰器、签名(含`in_ptr0/1/2`、`DeviceProperties` cuda)及`fused_cat`对应的triton.jit函数实现。

**2) 技术结论**
torch.compile的Inductor后端会为vLLM算子自动生成Triton GPU内核(如fused cat);通过Perfetto可视化界面,可一键从跟踪事件定位到生成的代码产物,实现"白盒"调试。

**3) 与文档关系**
印证TL;DR"用tlparse获取torch.compile日志"的核心论点,展示具体调试入口与产物样例,为开发者定位vLLM-torch.compile集成问题提供可操作指引。
- `dynamic_shapes.png`: **图文联合解读：**

**1) 图中内容：** 左侧展示一段条件分支代码（`if x.shape[0] % 128 == 0: foo() else: bar()`），右侧标注"Graph is only valid for x.shape[0] % 128 == 0"。中间红框是 tlparse 提取的栈追溯（`triton_quantize_nvfp4` 调用），下方是自动生成的 Guards 列表（Expr 表达式），其中 `Eq(Mod(s72, 128), 0)` 被红框高亮，右下方 tlparse 时间线中 `compilation_metrics_311.html` 同样被高亮。红箭头串联：编译指标 HTML → Guards 表达式 → 源码栈。

**2) 论证结论：** torch.compile 会基于张量形状（如 s72 % 128 == 0）自动插入运行时 Guards；tlparse 工具链能将这些 Guards 反向追溯到具体调用函数 `triton_quantize_nvfp4`，实现"指标→表达式→源码"的端到端调试。

**3) 与文档关系：** 直接支撑文档核心观点——使用 tlparse 抓取 torch.compile 日志并附在 bug 报告中，可定位由 vLLM 自定义算子触发的图重编译/缓存命中问题。
- `tlparse_inductor.png`: **1) 图中内容**
左面板为Chrome Trace"Chromium Events"视图,列出PT2编译产生的0–13号构建产物(trace event),其中第10项`inductor_output_code_cxt577…`被红框高亮;红色箭头指向右面板,即展开该文件后的Triton JIT内核源码——含`@triton_heuristics.pointwise`装饰器、签名(含`in_ptr0/1/2`、`DeviceProperties` cuda)及`fused_cat`对应的triton.jit函数实现。

**2) 技术结论**
torch.compile的Inductor后端会为vLLM算子自动生成Triton GPU内核(如fused cat);通过Perfetto可视化界面,可一键从跟踪事件定位到生成的代码产物,实现"白盒"调试。

**3) 与文档关系**
印证TL;DR"用tlparse获取torch.compile日志"的核心论点,展示具体调试入口与产物样例,为开发者定位vLLM-torch.compile集成问题提供可操作指引。
