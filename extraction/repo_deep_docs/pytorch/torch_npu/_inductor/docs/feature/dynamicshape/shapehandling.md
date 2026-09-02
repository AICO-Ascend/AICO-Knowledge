# shapeHandling 特性介绍

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/dynamicshape/shapehandling.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/dynamicshape/shapehandling.md

# shapeHandling 特性深度解读

## 【定位】

ShapeHandling 是 PyTorch Ascend 扩展（针对华为 Ascend 加速卡的 PyTorch 适配层，即 torch_npu）中的 **Inductor 编译优化特性**，通过把动态形状输入按"档位（gear）"归一化映射，**减少编译次数**，并在结合 aclgraph（NPUGraph）时**减少图捕获次数**，从而提升模型推理效率。

---

## 【技术要点】

1. **形状分档（bucketing）**：对输入张量的 `batchsize` 和 `sequence length` 维度进行分档处理，把相近的输入形状归并到同一个档位，档位内共享同一份编译产物。
2. **自动 padding 与 splitting**：当输入形状超过 `max_size` 时自动**分割**；当输入形状不在任何档位时自动 **padding 到最近的上一个档位**。
3. **维度类型限制**：仅支持两种维度类型 `BATCHSIZE` 和 `SEQLEN`，`shape_handling_configs` 最多配置两个维度类型；`BATCHSIZE` 下所有受影响张量必须共享相同的批次维度，`SEQLEN` 可为不同张量指定不同序列维度。
4. **档位生成策略（policy）**：内置 `TIMES`（按 `min_size`/`max_size` 生成 2 的整数幂档位）和 `CUSTOM`（通过 `gears` 显式指定）两种；非空 `gears` 优先于 `min_size/max_size/policy`；原文明确："当前 `min/max` 路径仅支持 `TIMES`"。
5. **与 PyTorch Dynamo 集成**：通过 `torch.compile(..., options=shape_options)` 注入编译选项，与 Inductor/Dynamo 流水线协同。
6. **与 aclgraph 协同**：在 `backend='npugraphs'` 下，shape_handling 在捕获 aclgraph 之前先把输入处理为同档位形状，相同档位共享同一份 aclgraph；原文明确 aclgraph 后端建议 `dynamic=False`，因为 aclgraph 本身不支持动态形状。
7. **可扩展的处理钩子**：通过 `shape_handling_dict` 提供 `trans_pre_fn` / `trans_post_fn` / `re_pre_fn` / `re_post_fn` 四个自定义回调，覆盖 transform 前后、recover 前后的转换逻辑。

---

## 【关键机制与数据】

- **核心工作流**（原文描述）：shape_handling 在捕获/编译之前，对输入按 `shape_handling_configs` 中的维度与档位规则做 **transform → 同档位同形状 → 复用编译/aclgraph → recover**。`BATCHSIZE` 维度影响所有张量且共享，`SEQLEN` 可针对每个 Tensor 单独指定维度下标。
- **降编译次数实测数据**（原文）：以 `test_shapes = [(3, 20), (4, 20), (5, 20), (6, 20)]` 的 4 个不同形状输入为例
  - 不开启：编译次数 = **4**
  - 开启（`min_size=1, max_size=1024, policy=TIMES`）：编译次数 = **2**（按 2 的整数幂档位归并）
- **aclgraph 降捕获次数实测数据**（原文）：相同 4 个输入下
  - `aclgraph` 单独使用：捕获次数 = **4**
  - `aclgraph + shape_handling`：捕获次数 = **2**
- **性能特征对比**（原文）：aclgraph 单独使用下"首次执行较慢（每次都要捕获）、后续执行快（复跑）"；aclgraph + shape_handling 下"首次较慢（仅首次捕获）、后续执行快（复跑）"。
- **维度下标规则**：原文明确"BATCHSIZE：`dimensions` 列表中只有第一个元素会被使用"；"SEQLEN：如果提供了单个维度值，会自动应用到所有受影响的张量"。
- **indices 字段**：控制档位应用到哪些输入 Tensor；空列表 `[]` 表示运行时自动推导可处理 Tensor。
- **底层类**：`NPUShapeHandling(configs=..., transform_pre_fn=..., transform_post_fn=...)`（原文示例出现）。

---

## 【表格解读】

### 表 1：`torch.compile(..., options=...)` 新增字段

| 字段 | 类型 | 是否必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `enable_shape_handling` | `bool` | 开启时必填 | `False` | 是否开启 shape handling。 |
| `shape_handling_configs` | `list[dict]` | 开启时必填 | `None` | shape 规则列表。最多支持两个维度类型（`BATCHSIZE`、`SEQLEN`）。 |
| `shape_handling_dict` | `dict` | 否 | `None` | 自定义预处理/后处理函数集合。 |

**逐行解读**：第一行 `enable_shape_handling` 是总开关，必须显式置 `True` 才会启用分档逻辑。第二行 `shape_handling_configs` 是规则主体，类型为字典列表，每个元素描述一个维度（batchsize 或 seqlen）的分档规则，全局上限两个；缺省 `None` 表示未配置。第三行 `shape_handling_dict` 是可选的高级扩展点，用于注入自定义回调覆盖默认 transform/recover 流程；缺省时走默认实现。

### 表 2：`shape_handling_configs` 内部字段

| 字段 | 类型 | 是否必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `type` | `str` | 是 | 无 | 维度类型：`BATCHSIZE` 或 `SEQLEN`。 |
| `dimensions` | `int` 或 `list[int]` | 否 | `BATCHSIZE->[0]`，`SEQLEN`按规则推导 | 目标维度下标。`SEQLEN` 支持按 Tensor 分别指定。 |
| `indices` | `list[int]` | 否 | `[]` | 应用到哪些输入 Tensor。空列表表示运行时自动推导可处理 Tensor。 |
| `value` | `int`/`float` | 否 | `0.0` | pad 填充值。 |
| `gears` | `list[int]` | 否 | `[]` | 明确指定档位。非空时优先于 `min_size/max_size/policy`。 |
| `min_size` | `int` | 否 | `1` | 自动生成 gear 的最小值。 |
| `max_size` | `int` | 否 | `1024` | 自动生成 gear 的最大值。 |
| `policy` | `str` | 否 | `TIMES` | gear 生成策略。当前 `min/max` 路径仅支持 `TIMES`。 |

**逐行解读**：`type` 是唯一必填项，指定维度语义。`dimensions` 描述作用维度下标，`BATCHSIZE` 默认作用于第 0 维，`SEQLEN` 既可全局指定也可按 Tensor 分别指定；二者优先级由原文规则"对于 BATCHSIZE 类型，dimensions 列表中只有第一个元素会被使用"约束。`indices` 控制"哪些输入张量参与此规则"，空列表即自动推导。`value` 用于 padding 时填什么值，默认 `0.0`。`gears` 是显式档位列表，非空时强制覆盖自动生成；空时回退到 `min_size/max_size/policy`。`min_size`/`max_size` 约束自动档位生成的边界，默认 `1` 与 `1024`。`policy` 决定档位生成方式，默认 `TIMES`（2 的整数幂），并且原文明确当前 `min/max` 路径只支持 `TIMES`。

### 表 3：`shape_handling_dict` 内部字段

| 字段 | 推荐签名 | 说明 |
|---|---|---|
| `trans_pre_fn` | `(*args, **kwargs) -> list[torch.Tensor]` | transform 前，将调用输入转换成 Tensor 列表。 |
| `trans_post_fn` | `(list[list[torch.Tensor]]) -> tuple[list[tuple], list[dict]]` | transform 后，将分组 Tensor 还原为"多组 args/kwargs"。 |
| `re_pre_fn` | `(list[Any]) -> list[list[torch.Tensor]]` | recover 前，将多组结果转回 Tensor 组。 |
| `re_post_fn` | `(list[torch.Tensor]) -> Any` | recover 后，恢复成最终返回结构。 |

**逐行解读**：`trans_pre_fn` 是 transform 阶段最前端的归一化钩子，把任意 `*args, **kwargs` 收拢成 Tensor 列表；`trans_post_fn` 是 transform 阶段末端钩子，把按档位分组后的多组 Tensor 还原为"多组 args/kwargs"，用于驱动下游多次调用；`re_pre_fn` 与 `re_post_fn` 是 recover 阶段对称的两个钩子，把下游按档位返回的多个结果恢复成与原始调用结构一致的单一返回值。四个钩子首尾相接，构成 transform→recover 的完整可定制管线。

### 表 4：不同编译模式对比

| 编译模式 | 编译次数（4个不同形状输入，共享两个档位） | 特点 |
|---------|---------------------------|------|
| 静态形状 (dynamic=False) | 4 | 每个形状都需要编译 |
| 静态形状 + shape_handling | 2 | 相同档位共享编译结果 |
| aclgraph 单独使用 | 4 | 每个形状都需要重新捕获 aclgraph |
| aclgraph + shape_handling | 2 | 相同档位共享 aclgraph |

**逐行解读**：第一行 baseline 显示 4 个不同形状在普通静态编译下产生 4 份编译产物。第二行开启 shape_handling 后，由于 (3,20)(4,20)(5,20)(6,20) 落在两个 2 的整数幂档位上，编译次数直接折半到 2。第三行等价于把 backend 换成 npugraphs，每种形状都要重新捕获 aclgraph，依然是 4 次。第四行 backend 保持 npugraphs 同时开启 shape_handling，捕获次数同步折半为 2；该行也是整篇文档主推的组合方式。

### 表 5：aclgraph 性能对比

| 配置 | 捕获次数（4个不同形状输入） | 首次执行时间 | 后续执行时间 | 适用场景 |
|------|---------------------------|-------------|-------------|----------|
| aclgraph 单独使用 | 4 | 较慢（每次都要捕获） | 快（复跑） | 输入形状固定的场景 |
| aclgraph + shape_handling | 2 | 较慢（仅首次捕获） | 快（复跑） | 输入形状在一定范围内变化的场景 |

**逐行解读**：第一行 aclgraph 单独使用时，4 个形状对应 4 次捕获开销，因此首次执行累计较慢；后续每档形状的复跑走 aclgraph 缓存所以快，但只对单档生效。第二行加 shape_handling 后捕获次数降到 2，意味着只有"前 2 个新档位首次进入"时慢，之后所有同档输入都直接复跑；本质上把"慢"集中到档位首次捕获上，从而把适用场景从"形状完全固定"扩展到"形状在一定范围内变化"。

---

## 【公式解读】

**原文无公式**。档位生成只通过配置项 `policy=TIMES`（2 的整数幂）、`min_size`、`max_size`、`gears` 表达，没有给出显式的数学表达式。

---

## 【关联】

- **torch.compile / Inductor / Dynamo 流水线**：shape_handling 以 `options` 字典形式注入 `torch.compile`，与 PyTorch Dynamo + Inductor 编译链路紧耦合，原文"与 PyTorch Dynamo 集成，提供编译优化"明确这一关系。
- **aclgraph（NPUGraph）**：通过 `backend='npugraphs'` 显式启用，是 shape_handling 最重要的协同模块；文档大半篇幅用于阐述二者结合如何扩展 aclgraph 的适用场景。
- **`NPUShapeHandling` 类**：在"自定义预处理和后处理函数"小节以 `NPUShapeHandling(configs=..., transform_pre_fn=..., transform_post_fn=...)` 形式被实例化，是该特性的底层封装类，承接 `shape_handling_configs` 与 `shape_handling_dict` 中的钩子。
- **本仓其他文档**：原文未给出内部链接，无法推断其他模块的引用关系。

---

## 【使用方法】

**启用总开关**：在 `torch.compile(..., options=shape_options)` 中将 `enable_shape_handling` 设为 `True`，并提供 `shape_handling_configs`。

**最小配置示例**（原文"如何使用 → 基本使用方法"）：

```python
shape_options = {
    "enable_shape_handling": True,
    "shape_handling_configs": [
        {"type": "BATCHSIZE", "dimensions": 0, "value": 0.0,
         "min_size": 1, "max_size": 1024, "policy": "TIMES"},
        {"type": "SEQLEN", "dimensions": [1], "value": 0.0,
         "min_size": 1, "max_size": 1024, "policy": "TIMES"}
    ]
}

compiled_fn = torch.compile(
    model_fn, backend='inductor', dynamic=False, options=shape_options
)
```

**与 aclgraph 联用**（原文示例）：把 `backend` 换成 `'npugraphs'`，并建议保留 `dynamic=False`；shape_handling 会在捕获 aclgraph 之前完成输入归一化，相同档位共享同一份 aclgraph。

**自定义档位**：把 `policy` 设为 `CUSTOM` 并通过 `gears=[...]` 显式枚举档位；非空 `gears` 会优先于 `min_size/max_size/policy`。

**自定义钩子**：通过 `shape_handling_dict` 字段提供 `trans_pre_fn` / `trans_post_fn` / `re_pre_fn` / `re_post_fn`，或在底层通过 `NPUShapeHandling(configs=..., transform_pre_fn=..., transform_post_fn=...)` 传入，覆盖默认的 transform / recover 流程。

**运行环境依赖**：所有示例依赖 `import torch` 与 `import torch_npu`，且输入张量需放置在 `device="npu"` 上；原文示例未涉及更多 CLI 入口或环境变量。
