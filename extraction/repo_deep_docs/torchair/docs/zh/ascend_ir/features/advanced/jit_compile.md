# 算子在线编译选项

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/jit_compile.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/jit_compile.md

# 算子在线编译选项 · 一体化深度解读

## 【定位】

这篇文档描述了在 TorchAir GE 图模式下,**算子编译方式的可控选项**,即让用户在模型编译阶段自行决定是走"在线编译算子"路径,还是"复用系统中已编译好的算子二进制"路径,以适配静态 shape 与动态 shape 网络的不同诉求。

## 【技术要点】

1. **适用场景收紧**: 本功能**仅适用于 GE 图模式**场景(`原文: 本功能仅适用于GE图模式场景`),其余场景不生效。
2. **配置入口收敛**: 通过 `torchair.get_npu_backend` 的 `compiler_config` 入口配置,具体字段位于 `config.experimental_config.jit_compile`(`原文: 该功能通过torchair.get_npu_backend中compiler_config配置`)。
3. **当前唯一合法值**: `jit_compile` 参数当前**仅支持 `"auto"`**,虽然定位是"可选项",但实际可用值被收窄到一个自动模式(`原文: 当前仅支持"auto",系统自行判断编译方式`)。
4. **默认值即自动态**: `jit_compile` 默认值为 `"auto"`,即开箱即用即由系统自行决策编译策略(`原文: 默认值为"auto"`)。
5. **静态 shape 策略**: 对静态 shape 网络,选择**在线编译算子**(`原文: 针对静态shape网络,选择在线编译算子`)。
6. **动态 shape 策略**: 对动态 shape 网络,**优先查找**系统中已编译好的算子二进制,若查找不到再**回退到在线编译**(`原文: 针对动态shape网络,优先查找系统中已编译好的算子二进制,如果查找不到对应的二进制,再在线编译算子`)。

## 【关键机制与数据】

**工作原理(原文):** 该选项并不暴露细粒度控制,而是把决策权交给系统(`"auto"`)。系统基于 shape 特征分流:

- **静态 shape 分支**:shape 是固定的,系统**直接在线编译**,不需要也不去查表外的历史二进制,因为同一 shape 的算子都可基于本次编译直接生成。
- **动态 shape 分支**:shape 会变,此时**优先复用**已有算子二进制(已编译好的算子更稳定、更省编译耗时),若缓存或系统中查无对应二进制,**才退回到在线编译**,作为兜底。

整体是一条"**看 shape → 决策路径 (auto)**"的隐式分流,而非显式开关。该文档未给出任何性能数据(如编译耗时、显存占用等),原文无性能类数字。

## 【表格解读】

**表 1 · 参数说明(原文逐字还原)**

| 参数名 | 说明 |
|--|--|
| jit_compile | 算子编译方式，默认值为"auto"。当前仅支持"auto"，系统自行判断编译方式。<br>针对静态shape网络，选择在线编译算子。<br>针对动态shape网络，优先查找系统中已编译好的算子二进制，如果查找不到对应的二进制，再在线编译算子。 |

**逐行解读:**
- **参数名 `jit_compile`**:这是该特性的唯一开关字段,挂在 `CompilerConfig.experimental_config` 下,属于"实验性"命名空间的配置。
- **`算子编译方式,默认值为"auto"`**:指明默认值,使用时即便不显式赋值,系统也会按 auto 策略行为;若用户没有特殊诉求,无须改写。
- **`当前仅支持"auto",系统自行判断编译方式`**:强调该字段暂时**没有别的可选枚举值**,不能手动强制"仅在线"或"仅复用二进制",所有判断都交给系统。
- **`针对静态shape网络,选择在线编译算子`**:静态 shape 下不走"查二进制"分支,保证编译产物与本次 shape 完全匹配,避免 shape 漂移带来的兼容性问题。
- **`针对动态shape网络,优先查找系统中已编译好的算子二进制,如果查找不到对应的二进制,再在线编译算子`**:动态 shape 下走"先查复用、后在线兜底",体现了对**编译耗时/稳定性**与**算子覆盖率**之间的权衡。
- 行内 `<br>` 仅作换行语义,语义上仍属同一项 `jit_compile` 参数的同一段描述。

## 【公式解读】

原文无公式。

## 【关联】

- 上下游/同级关系:**通过 `torchair.get_npu_backend` 接入**,因此该特性必须与 `CompilerConfig` 的构造、`npu_backend` 与 `torch.compile` 的衔接机制配合使用(`原文示例`:`config = torchair.CompilerConfig()` → `npu_backend = torchair.get_npu_backend(compiler_config=config)` → `torch.compile(model, backend=npu_backend)`)。
- 内部链接指向上游 API 文档 [`../../api/torchair/get_npu_backend.md`](../../api/torchair/get_npu_backend.md),该链接是**配置入口的承载模块**,即所有形如 `jit_compile` 这样的 `experimental_config` 子字段的注册位置都在 `get_npu_backend` 的 `CompilerConfig` 体系中。
- 适用域强绑定:**GE 图模式**,因此该特性不与其它非 GE 模式(如可能存在的 eager 路径)互通。

## 【使用方法】

启用/配置方式均源自原文示例与表 1 字段,完整路径如下:

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 算子在线编译选项配置
config.experimental_config.jit_compile = "auto"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

要点(原文有则写):
- 赋值字段:`config.experimental_config.jit_compile`。
- 当前唯一可用值:`"auto"`(默认即此值,显式写出或省略效果一致)。
- 关键命令/对象:`torchair.CompilerConfig`、`torchair.get_npu_backend(compiler_config=...)`、`torch.compile(model, backend=npu_backend)`。
- **运行约束**:本特性仅在 **GE 图模式** 下生效,其它模式下即便设值也不会按文档所述语义工作。
- 原文明确说明示例代码**仅供参考、不支持直接拷贝运行**,实际接入需结合自身模型与 `torch.compile` 流程调整。
