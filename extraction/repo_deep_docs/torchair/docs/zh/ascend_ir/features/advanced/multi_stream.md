# 多流表达功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/multi_stream.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/multi_stream.md

# 多流表达功能 (Multi-Stream Expression Feature) 深度解读

---

## 【定位】

本篇文档描述了 TorchAir 中**多流表达（Multi-Stream Expression）能力**，用于在大模型推理场景下，将原本串行的算子通过用户指定 stream 分发到不同流上并行执行并形成 overlap，从而降低整体计算耗时；其定位特别聚焦于 **Ascend IR 图内资源并发（max-autotune 模式）**，尤其针对 Cube 计算资源未完全利用的场景。

---

## 【技术要点】

1. **并行类型双分支**：文档明确划分两类并行——"**计算与计算并行**"（基于数据依赖分析出可并行分支，指定 stream 并行）和"**计算与通信并行**"（针对无数据依赖的通信操作提前占用通信资源）。
2. **Cube 资源饱和度判定**：文档给出开启判据——**若 Cube 计算资源已完全使用，不建议开启本功能**，否则会引入额外调度导致原计算性能劣化。
3. **场景适用性边界**：仅适用于 **GE 图模式**；纯 Vector 场景计算耗时"一般在可接受范围"，含 Cube 场景下开启本功能效益更优。
4. **静态 Shape 三重约束**：① 与 `enable_single_stream`（单流执行功能）冲突、不支持同时开启；② **不推荐在 SuperKernel 内设置算子多 stream 并行**（应改用 `super_kernel_scope.md` 中的 stream-fusion 编译选项）；③ 默认多流优先级高于动态 shape 多流。
5. **动态 Shape 开关**：默认单流模式，需通过 CANN 环境变量 `ENABLE_DYNAMIC_SHAPE_MULTI_STREAM=1` 开启多流，且一旦开启，"**优先级低于**"本静态 shape 多流功能。
6. **流间调度核心三件套**：`npu_scope.npu_stream_switch`（声明流切换 + 自动添加 `_enable_inner_parallel` 属性）+ `npu_scope.npu_wait_tensor`（跨流时序同步）+ 默认 stream 兜底；其中 `_enable_inner_parallel` 属性的约束与配套 CANN 版本大于 9.0.0 时才生效。

---

## 【关键机制与数据】

**工作原理 / 数据流（原文机制梳理）**：

- **分发入口**：用户在 Python 脚本中通过 `with torchair.scope.npu_stream_switch(stream_tag, stream_priority, enable_inner_parallel):` 语句块，将块内的算子切换到 `stream_tag` 流上；语句块外的算子仍走默认 stream。
- **属性自动注入**：进入 with 块后，系统"**自动添加 `_enable_inner_parallel` 属性**"，且属性值与 `enable_inner_parallel` 参数值一致（默认 `True`），从而由 GE 接管该流内的并发分流策略。
- **流标签语义**：相同的 `stream_tag` 代表相同的流，由用户自行控制；不同 `stream_tag` 即可对应不同 stream，从而形成多流并行。
- **跨流同步机制**：通过 `npu_scope.npu_wait_tensor` 指定"**算子 a 等待算子 b 执行完后执行**"，建立显式的跨流数据依赖同步关系（即文档配图中"虚线控制边"的来源）。
- **优先级语义**：`stream_priority` 表示 Runtime 并发时优先给高优先级流分配核资源，文档注明"**当前版本使用默认值 0 即可**"，即暂未要求用户区分优先级。

**性能相关数据**：原文未提供具体加速比、算子数阈值、并行度上限等量化性能数据，仅给出定性结论（"降低整体计算耗时"、"含 Cube 场景效益更优"）。**原文无量化性能数字**。

---

## 【表格解读】

**原文无表格**。

（注：原文中 `npu_stream_switch` 的三个参数以列表项形式呈现，并非 markdown 表格结构，故此处不强行造表。）

---

## 【公式解读】

**原文无公式**。

（注：文档为特性说明类内容，未涉及 LaTeX 数学公式或伪代码形式的算式表达。）

---

## 【关联】

利用文末内部链接信息，本特性在 TorchAir 体系内的上下游关系如下：

| 关联对象 | 链接 | 关系性质 |
|---------|------|---------|
| 单流执行功能 | `single_stream.md` | **互斥关系**：静态 Shape 场景下，本功能与 `enable_single_stream` 冲突，不支持同时开启 |
| 图内标定 SuperKernel 范围 | `super_kernel_scope.md` | **替代/补充关系**：若在 SuperKernel 内需要多流融合，应改用该特性中的 **stream-fusion 编译选项**，而非本功能的原始 `npu_stream_switch` 写法 |
| `npu_stream_switch` API | `../../api/scope/npu_stream_switch.md` | **本特性的核心 API**：`with` 语句块的真正落地点，决定算子归属 stream |
| `npu_wait_tensor` API | `../../api/scope/npu_wait_tensor.md` | **配套时序控制 API**：在多流方案中用于建立跨流依赖、同步执行时序 |

此外，原文还外链至 **CANN GE 图引擎 API** 中"属性名列表"章节（`https://hiascend.com/document/redirect/CannCommunityAscendGraphApi`），用于说明 `_enable_inner_parallel` 属性的约束，且该属性需配套 **CANN 版本大于 9.0.0** 时才生效——这构成了本特性对底层 CANN 版本的硬约束。

---

## 【使用方法】

**1. 前置分析**：用户自行分析模型中可进行并行计算的算子（基于数据依赖图）。

**2. 开启多流表达（核心 API）**：

```python
with torchair.scope.npu_stream_switch(stream_tag: str, stream_priority: int = 0, enable_inner_parallel: bool = True):
    # 块内算子切换至 stream_tag 流
```

参数说明（原文逐字）：
- `stream_tag`：需要切换到的流的标签，相同的标签代表相同的流，由用户控制。
- `stream_priority`：切换到 `stream_tag` 流的优先级，Runtime 运行时并发时优先给高优先级流分配核资源，**当前版本使用默认值 0 即可**。
- `enable_inner_parallel`：是否启用 `stream_tag` 流内的算子按照 GE 原有的并发策略分流，**默认开启**。

**3. （可选）控制并行时序**：

通过 `npu.scope.npu_wait_tensor` 接口实现时序控制，指定算子 a 等待算子 b 执行完后执行。

**4. 动态 Shape 场景额外配置**：

```bash
export ENABLE_DYNAMIC_SHAPE_MULTI_STREAM=1
```

**5. 完整使用示例（原文代码摘要）**：

```python
class Model(torch.nn.Module):
    def forward(self, in1, in2, in3, in4):
        add_result = torch.add(in1, in2)                    # 默认 stream
        with tng.scope.npu_stream_switch('1'):              # 流 "1"
            tng.scope.npu_wait_tensor(in4, add_result)      # 等 add_result
            mm_result = torch.mm(in3, in4)
        mm1 = torch.mm(in3, in4)                            # 默认 stream
        with tng.scope.npu_stream_switch('2'):              # 流 "2"
            tng.scope.npu_wait_tensor(in4, mm_result)       # 等 mm_result
            add2 = torch.add(in3, in4)
        return add_result, mm_result, mm1, add2
```

配置项要点：示例中通过 `CompilerConfig()` + `config.debug.graph_dump.type = "pbtxt"` 输出 pbtxt 文件以可视化多流拓扑（对应原文档"图 1 pbtxt 文件样例 / 多流示意图"）。

## 图文联合解读

- `ge_multi_stream.png`: # 图文联合解读

## 1) 图中内容
该图为计算图结构，包含：4个Data输入节点、2个Add节点、2个MatMul节点、2个Identity节点（白色框，标识多流切换点）以及1个NetOutput输出节点。数据流呈左右两条并行分支：左侧MatMul接收Data并经Identity流入下方Add；右侧MatMul由上方Add经Identity驱动；两路结果汇聚至NetOutput。

## 2) 技术结论
图中通过**Identity节点**标记多流切换边界，证明：将无数据依赖的MatMul分派到不同stream并行执行，可使两条计算分支形成overlap，提升执行效率。

## 3) 与文档论点关系
直观对应文档"使用方法"中`npu_stream_switch`的作用机制——以with语句块包裹的算子被打上stream_tag切换流标签，并通过`_enable_inner_parallel`属性驱动GE图引擎将可并行算子调度至不同stream，实现计算与计算并行，契合文档"Cube未占满时开启多流降低耗时"的核心论点。
