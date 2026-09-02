# 计算与通信并行功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/cc_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/cc_parallel.md

【定位】
本文档描述 TorchAir 中"计算与通信并行"（CC Parallel）能力的开启方式与使用约束：在分布式大模型推理场景下，对 AllReduce 通信算子及其上下文可连续切分的算子进行切分，使通信与计算在昇腾 NPU 上并行执行，从而加速分布式推理。

【技术要点】
1. 适用对象：网络中的 AllReduce 通信算子，以及其上下文中"可以连续切分"的算子。
2. 使用范围：仅适用于 GE 图模式场景，非图模式或非 AllReduce 通信算子不在切分范围内。
3. 切分粒度：仅对 AllReduce 通信算子进行切分，其他类型的通信算子不在本功能处理范围。
4. 目标效果：通信与计算并行运行，以加速分布式推理。
5. 启用方式：通过 `torchair.get_npu_backend` 中的 `compiler_config` 进行配置。
6. 关键开关：使用 `config.experimental_config.cc_parallel_enable` 控制，默认 `False`，置为 `True` 即开启并行模式。

【关键机制与数据】
- 原文：通过对网络中 AllReduce 通信算子以及上下文中可以连续切分的算子切分，从而启用通信和计算并行运行。
- 原文：本功能仅适用于 GE 图模式场景。
- 原文：只有网络中存在通信算子才能切分，切分时，仅对 AllReduce 通信算子进行切分。
- 原文未涉及具体的切分算法、切分阈值、收益量化数据、加速比、性能数字等内容；本文档仅声明机制与开关，未提供量化数据。

【表格解读】

| 参数名 | 说明 |
|--|--|
| cc_parallel_enable | 图执行时是否开启计算与通信并行。False（默认值）：不开启并行模式。True：开启并行模式。 |

逐行解读：
- 参数名 `cc_parallel_enable`：位于 `config.experimental_config` 命名空间下，是一个布尔开关，控制"计算与通信并行"功能是否在图执行阶段启用。
- 说明字段给出了开关的两个取值语义：`False` 为默认值，表示不开启并行模式；`True` 表示开启并行模式。是否影响图执行阶段由 NPU 后端根据该配置决定，文档未给出底层切换逻辑细节。
- 原表中仅此一个参数项，无其他相关参数同时披露。

【公式解读】
原文无公式。

【关联】
- 与 `torchair.get_npu_backend`（内部链接 `../../api/torchair/get_npu_backend.md`）直接相关：本功能的配置入口 `config.experimental_config.cc_parallel_enable` 是 `get_npu_backend` 在获取 NPU 后端时传入的 `CompilerConfig` 的子字段，需通过该接口完成编译后端的构建与图编译，再配合 `torch.compile(model, backend=npu_backend)` 触发生效。
- 与 GE 图模式上下游强绑定：本功能的使用约束明确"仅适用于 GE 图模式场景"，因此依赖于 TorchAir 中 GE 图编译链路；非图模式（例如 eager 模式）或非 AllReduce 通信算子不进入本功能的处理路径。
- 与大模型分布式推理场景绑定：文档将本功能定位在"大模型切分部署"场景中，作用对象为分布式通信集合（AllReduce），因此其上游为模型切分/并行策略，下游为昇腾 NPU 上计算与通信的并行执行。

【使用方法】
原文给出的示例代码（仅供参考，不支持直接拷贝运行）：

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 计算与通信并行开关
config.experimental_config.cc_parallel_enable = True
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

配置项说明：
- `config.experimental_config.cc_parallel_enable`：布尔型，`True` 表示开启计算与通信并行，`False`（默认值）表示不开启。
- 其余启用方式、原生命令、环境变量等，原文未涉及。
