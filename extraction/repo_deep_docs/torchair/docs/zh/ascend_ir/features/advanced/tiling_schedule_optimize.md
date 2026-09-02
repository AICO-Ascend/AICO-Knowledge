# Tiling调度优化功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/tiling_schedule_optimize.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/tiling_schedule_optimize.md

# 一体化深度解读：Tiling调度优化功能

## 【定位】

这篇文档描述在 TorchAir 静态图（GE 图模式）场景下，通过「Tiling 下沉」将原本依赖运行时输入值才能计算的 Tiling 参数下沉到 Device 侧 AI CPU 上执行的调度优化能力，目的是消除 Tiling 计算阶段的 Host-Device 交互开销，提升整图下沉的执行效率。

---

## 【技术要点】

1. **整图下沉的延伸问题**：静态图通过整图一次性下发消除了算子粒度的 Host-Device 交互，但部分算子的 Tiling 参数依赖运行时具体输入值（「Tiling 值依赖」），这部分计算仍需要 Host 介入，破坏了下沉的连续性。
2. **Tiling 下沉机制**：将 Tiling 计算本身下沉到 Device 侧 AI CPU 上执行，使整个推理流程（包含动态 Tiling 计算 + 算子计算）完全在 Device 侧完成。
3. **Tiling 的语义**：原文定义为「描述 NPU 上算子输入/输出数据切分、分块计算、多核并行等逻辑，以满足片上存储限制和计算 pipeline 的需求」，属于片上存储与计算流水线的调度描述。
4. **适用范围限定**：仅适用于 GE 图模式 + 静态 Shape 模型；当前仅融合算子（矢量计算与矩阵计算融合）支持，例如 FusedInferAttentionScore、IncreFlashAttention。
5. **CANN 版本强耦合**：基于支持 Tiling 下沉特性的新版本 CANN 编译生成的算子，与不支持该特性的旧版 CANN 运行时不兼容。
6. **启用入口**：通过 `torchair.get_npu_backend` 的 `compiler_config` 路径进行配置，参数为 `config.experimental_config.tiling_schedule_optimize`，取值 `True`/`False`，默认 `False`。

---

## 【关键机制与数据】

**整体机制链路（原文整合）**：

- **阶段一：整图下沉**。完整计算图一次性下发至 Device，后续算子执行由 Device 自主完成，无需 Host 参与，减少 Host-Device 交互开销，提升执行效率。
- **阶段二：Tiling 动态计算的卡点**。部分算子的 Tiling 计算依赖运行时输入的具体数值（原话：「Tiling 值依赖」），需在执行时动态计算 Tiling 参数，这部分若留在 Host 上完成，会重新引入 Host-Device 交互。
- **阶段三：Tiling 下沉解决卡点**。将 Tiling 计算下沉到 Device 侧 AI CPU 执行，使「动态 Tiling 计算 + 算子执行」全程在 Device 侧闭环。

**关键性能层面的描述**（原文）：
- 「减少 Host-Device 交互开销，提升执行效率」——这是原文明确给出的优化目标表述，但**未给出具体的加速比、时延数据或性能数字**。

**数据流特征**（原文整合）：
- 计算图整图下发 → Device 侧执行；
- 存在 Tiling 值依赖的算子：Tiling 在 Device 侧 AI CPU 上动态生成 → 同一 Device 上继续执行算子计算（矢量 + 矩阵融合），全程不离开 Device。

---

## 【表格解读】

**表 1（参数说明，原文逐字还原）**：

| 参数名 | 说明 |
| -- | -- |
| tiling_schedule_optimize | 是否开启Tiling计算调度优化。False（默认值）：不开启。True：开启。 |

**逐行解读**：

- **参数名 `tiling_schedule_optimize`**：命名上同时覆盖「Tiling」与「schedule 优化」两层含义，与文档标题「Tiling调度优化」一致。
- **说明的语义层次**：
  - 第一层是功能开关语义：开启/不开启 Tiling 计算的调度优化；
  - 第二层是默认值语义：默认 `False`，即框架**默认不开启此优化**，需要用户显式开启，这一保守默认值侧面印证了下方「使用约束」中提到的适用范围与版本兼容性限制；
  - 第三层是选项语义：仅 `True`/`False` 二值，无中间灰度状态，对应「开关型」配置。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与整图下沉机制的关系**：本文描述的 Tiling 下沉是整图下沉场景中的「子问题求解器」。整图下沉解决了常规算子的 Host-Device 交互，Tiling 下沉解决了其中 Tiling 值依赖算子的 Host-Device 交互；二者结合，构成「全 Device 侧闭环」的执行路径。

- **与 GE 图模式的关系**：使用约束第一条明确「本功能仅适用于 GE 图模式场景」，说明 Tiling 下沉是 GE 图执行器的能力，而非 Dynamo / inductor 等其他图执行器的能力。

- **与融合算子集合的关系**：当前能力仅覆盖「矢量计算 + 矩阵计算融合」的融合算子，并以 FusedInferAttentionScore、IncreFlashAttention 为例，这两类均为注意力计算相关融合算子，提示其典型使用场景为大模型/Transformer 类推理。

- **与 CANN 工具链的耦合关系**：能力依赖「支持 Tiling 下沉特性」的新版本 CANN 进行算子编译；运行时不兼容旧版 CANN。这是一条跨组件版本门，文档将其列为使用约束之一。

- **与 Ascend samples 仓的关系**：文档明确「端到端算子 Tiling 下沉过程」不在本文档范围，需跳转到 Ascend samples 仓的 `AddCustomTilingSink` 样例（含 README.md）获取；这是文档间职责的边界划分。

- **内部链接 `../../api/torchair/get_npu_backend.md`**：该链接指向 `torchair.get_npu_backend` 的 API 文档，是本文档配置示例中实际调用的接口；本文档中的 `CompilerConfig`、`experimental_config.tiling_schedule_optimize` 等 Python 路径中各级对象的字段含义，需结合该 API 文档进行完整查阅。

---

## 【使用方法】

**配置示例**（原文给出，仅供参考，不支持直接拷贝运行）：

```python
import torch_npu
import torchair
config = torchair.CompilerConfig()
# Tiling调度优化配置
config.experimental_config.tiling_schedule_optimize = True
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

**配置要点**：

1. 通过 `torchair.CompilerConfig()` 构造配置对象；
2. 在 `experimental_config` 命名空间下设置 `tiling_schedule_optimize = True`（显式开启；不设置或设为 `False` 则不开启）；
3. 将配置传入 `torchair.get_npu_backend(compiler_config=config)`，获得携带该优化能力的 NPU 后端；
4. 用 `torch.compile(model, backend=npu_backend)` 触发编译与执行。

**端到端样例**：访问 Ascend samples 仓下的 `operator/ascendc/2_features/17_tiling_sink/AddCustomTilingSink` 样例（含 README.md）——`https://gitee.com/ascend/samples/tree/master/operator/ascendc/2_features/17_tiling_sink/AddCustomTilingSink`，获取完整的自定义算子 Tiling 下沉端到端过程。

**前置环境要求（原文「使用约束」节）**：

- 必须运行在 GE 图模式；
- 模型必须为静态 Shape；
- 当前仅融合算子（矢量 + 矩阵融合）受支持；
- 依赖支持 Tiling 下沉特性的新版 CANN 编译产出，且需在新版 CANN 运行时执行。
