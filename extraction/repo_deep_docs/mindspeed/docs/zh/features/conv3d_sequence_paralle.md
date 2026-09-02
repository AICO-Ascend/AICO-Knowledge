# conv3d 序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/conv3d_sequence_paralle.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/conv3d_sequence_paralle.md

# conv3d 序列并行 — 一体化深度解读

## 【定位】
本文档描述 mindspeed 昇腾大模型加速库中 **Conv3DSequenceParallel** 模块的能力：通过对三维卷积（conv3d）输入特征图沿卷积核 **depth 维度进行切分** 并分发到不同进程组并行执行，从而将原本顺序的三维卷积操作并行化，以提升多模态/视觉类大模型中三维卷积的吞吐效率。

---

## 【技术要点】

1. **切分维度**：沿卷积核的 **depth 维度** 对输入特征图进行切分（非 batch、非 channel、非 spatial），分发到不同的进程组并行执行 conv3d。这是该模块并行化的核心切入点。
2. **前向数据流**：输入特征图 → 按 depth 切分（split） → 分布式进程组并行 conv3d → 结果 **gather** → 输出给下游模块。
3. **反向数据流**：下游梯度到来 → 按 depth 维度 **split** → 分发到并行三维卷积模块做反向传播 → 各路梯度 **gather** → 输出给上游模块。即正反两段互为对偶的 split / gather 流程。
4. **接口类名与并行大小参数**：通过 `Conv3DSequenceParallel(..., sp_size)` 显式声明序列并行规模，参数 `sp_size` 默认值为 **1**（即默认不开启并行）。
5. **通信进程组**：通过 `pg` 参数（必选，`torch.distributed.ProcessGroup`）指定通信域，将并行卷积与分布式集合通信绑定。
6. **支持范围限制**：模块**不支持 padding 模式**，凡原本带 padding 的 conv3d 不能用该模块替换；其余参数语义（kernel_size、stride、dilation、bias、dtype）与标准 conv3d 保持一致（默认值：kernel_size=(1,1,1)，stride=(1,1,1)，dilation=1，bias=True，dtype=torch.bfloat16）。
7. **可选参数异步通信**：通过 `param_async`（默认 **False**）开关参数异步通信，用于进一步掩盖通信开销。

---

## 【关键机制与数据】

- **工作机制（原文）**："构造 Conv3DSequenceParallel 类，将输入特征图按照卷积核的 depth 维度进行切分后进行并行卷积。"——即以 depth 维切分为并行化锚点，绕过 conv3d 各区块之间"无真正先后约束"的串行结构。
- **前向（原文）**："将输入特征图按照卷积核的 depth 维度进行切分，分发到不同的进程组中进行 conv3d 三维卷积操作，将卷积结果进行 gather 操作后输出到下游模块。"
- **反向（原文）**："Conv3DSequenceParallel 类会将下游反向得到的梯度进行 split 操作，将梯度的 depth 维度进行切分，分发到并行的三维卷积模块上进行反向传播，再将并行的三维卷积模块的反向梯度进行 gather 操作后输出到上游模块。"
- **数据流图（原文）**：文档引用了一张示意图 `figures/conv3d_sequence_parallel.png`，标注为 "conv3d 序列并行前向与反向数据流示意图"，直观展示上述 split → 并行 conv3d → gather 的拓扑。
- **使用影响（原文）**："将逐卷积区域的卷积操作分发到进程组中进行并行化执行，提高三维卷积效率。"——即把区域级的卷积从串行改为并行执行以提升效率。
- **性能数据**：原文未给出具体的加速比、吞吐量、时延等数字，仅定性地指出"提高三维卷积效率"。

---

## 【表格解读】

**原文无表格。** 文档的参数说明以"列表+逐项描述"形式给出，未以表格呈现参数对照或性能对比。

---

## 【公式解读】

**原文无公式。** 文档未给出 LaTeX/伪代码公式，机制描述以自然语言 + 接口列表 + 数据流图为主。

---

## 【关联】

原文内部链接信息标注为 **(无)**，文中也未显式引用其他特性/模块的链接。可从文档本身推断的隐含关联包括：

- **依赖**：深度依赖 PyTorch 分布式原语 `torch.distributed.ProcessGroup`（`pg` 参数）与集合通信（`split` / `gather`），因此需运行在已初始化分布式进程组的训练环境中。
- **作用对象**：上游为多模态/视觉类大模型中**非 padding 模式**的 conv3d 模块，下游为这些模型后续的算子/层（梯度继续向上游反向传播）。
- **与 Megatron 类张量/序列并行的关系**：`sp_size`、`pg` 的命名风格与 mindspeed 中其他 sequence-parallel 类特性保持一致，可视为该库在 conv3d 这一具体算子上的序列并行扩展。
- **与 Conv3dSequenceParallel 自身前/反过程的关联**：前向的 gather 输出对应反向的 split 输入；反向的 gather 输出对应前向的 split 输入，二者构成对偶算子对。

---

## 【使用方法】

**启用方式（原文）**："将原有的 conv3d 模块替换为 `Conv3DSequenceParallel` 并指定相关参数，以实现并行加速。"

**接口签名（原文逐字保留）**：
`Conv3DSequenceParallel(pg, in_channels, out_channels, kernel_size, stride, dilation, bias, param_async, dtype, sp_size)`

**参数清单（原文逐字保留）**：

| 参数 | 必选/可选 | 类型 | 默认值 | 含义 |
|---|---|---|---|---|
| `pg` | 必选 | `torch.distributed.ProcessGroup` | — | 通信进程组 |
| `in_channels` | 必选 | `int` | — | 输入通道数 |
| `out_channels` | 必选 | `int` | — | 输出通道数 |
| `kernel_size` | 可选 | `tuple(int,int,int)` | `(1, 1, 1)` | 卷积核大小 |
| `stride` | 可选 | `tuple(int,int,int)` | `(1, 1, 1)` | 各个维度卷积步长大小 |
| `dilation` | 可选 | `int` 或 `tuple(int,int,int)` | `1` | 扩张率 |
| `bias` | 可选 | `bool` | `True` | 是否开启偏置 |
| `param_async` | 可选 | `bool` | `False` | 是否开启参数异步通信 |
| `dtype` | 可选 | `torch.dtype` | `torch.bfloat16` | 卷积层的数据类型 |
| `sp_size` | 可选 | `int` | `1` | 序列并行大小 |

**典型使用流程（按原文归纳）**：
1. 确认原模型使用的是**非 padding 模式**的 conv3d（否则不可替换，见"注意事项"）。
2. 构造或获取 `torch.distributed.ProcessGroup` 实例作为 `pg`。
3. 以与原 conv3d 一致的 `in_channels`、`out_channels`、`kernel_size`、`stride`、`dilation`、`bias` 初始化 `Conv3DSequenceParallel`。
4. 按需设定 `sp_size > 1` 开启序列并行、`param_async=True` 开启参数异步通信、`dtype` 与原模块保持一致。
5. 在模型前向/反向中用该模块替换原 conv3d，即获得按 depth 维切分并行化的三维卷积。

**注意事项（原文）**："`Conv3DSequenceParallel` 模块并不支持 padding 模式，因此使用了 padding 的 conv3d 模块不能使用 `Conv3DSequenceParallel` 模块替换。"

## 图文联合解读

- `conv3d_sequence_parallel.png`: **图文联合解读：**

1）图示内容：上下两行分别描绘前向（Conv3DSequenceParallel前向过程）与反向（Conv3DSequenceParallel反向过程）数据流。前向路径为：初始化→_split（depth维度切分）→多组并行的conv3d原生前向→_gather→输出；反向路径为对称反转：_split→多组并行conv3d原生反向→_gather→all_reduce→输出。模块标注涵盖_ConvSplitForwardGatherBackward、_ConvGatherForwardSplitBackward、allreduce_function与conv3d。

2）技术结论：通过沿depth维切分后多进程组并行执行conv3d，结合gather/all_reduce完成数据重组，可对各独立卷积区块实现并行化以加速三维卷积。

3）与文档关系：图示精准对应文档"前向过程"与"反向过程"两段论述，将抽象的"切分—并行卷积—汇聚"流程具象化为可执行的算子链路。
