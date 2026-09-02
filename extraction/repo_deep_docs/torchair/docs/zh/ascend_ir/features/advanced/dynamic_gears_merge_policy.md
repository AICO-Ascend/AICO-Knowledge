# 动态shape图分档执行功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/dynamic_gears_merge_policy.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/dynamic_gears_merge_policy.md

# 动态shape图分档执行功能 — 一体化深度解读

## 【定位】

这篇文档描述 TorchAir 中"动态 shape 图分档执行"能力：在用户网络仅少量维度（如 Batch）变化且变化范围有限可枚举的场景下，将一张动态图按指定档位（gears）切分为多个静态子图，从而兼顾"形状灵活性"与"近静态图的执行性能"，解决纯动态图性能差、纯静态图又无法适应多 shape 的矛盾。

---

## 【技术要点】

1. **核心思想 — 档位化静态子图**：在 `torch.compile(dynamic=True)` 基础上，通过 `set_dim_gears` 把若干可枚举的 shape 数值固化为多个档位；每个档位在执行时被实例化为一张静态子图，可一次性整图下发到 NPU Device，性能优于不分档的纯动态图。
2. **三种图模式对比**（以 Add 算子、shape ∈ {(2,2), (4,2)} 为例）：
   - `dynamic=False`（静态图）：仅支持编译时 shape (2,2)/(2,2)，输入 (4,2) 会触发重新编译。
   - `dynamic=True`（纯动态图）：支持 (-1,-1)，覆盖任意相等 shape，但算子任务不能一次下发，性能最差。
   - **分档动态图**：支持 (-1,2)，并把第 0 维按 [2, 4] 分档，得到 2 个静态子图，性能优于纯动态图。
3. **关键约束**：
   - 仅适用 **GE 图模式**（不支持同时启用 `Dynamo导图功能` 与 `RefData类型转换功能`）。
   - 仅适用 **整图优化**（`torch.compile(..., fullgraph=True)`）。
   - `set_dim_gears` 必须与 `dynamic=True` 搭配使用；scalar 符号化由 Dynamo 在 `dynamic=True` 下自动完成。
   - 参与分档的 Tensor **不能传入私有格式**（如 FRACTAL_NZ、NC1HWC0）。
   - **总档位数 ≤ 100**；档位值不能为 0 或 1（FX graph 中 dim 符号化范围为 [2, ∞)，0/1 不会命中动态 FX graph，需重新成图）。
4. **两种组合模式**（`inference_config.dynamic_gears_merge_policy`）：
   - `zip`（默认）：按位置一一对应。
   - `product`：按笛卡尔积组合，可生成更多档位。
5. **API 与配置项**：`torchair.inference.set_dim_gears(tensor, dim_gears={dim:[…]})` + `torchair.CompilerConfig().inference_config.dynamic_gears_merge_policy` + `torchair.get_npu_backend(compiler_config=config)` + `torch.compile(model, backend=npu_backend)`。
6. **首次执行即生效**：首次执行时设置档位即可保证首次编译就捕获档位，后续执行无需再设置，避免重复设置引入性能损耗。

---

## 【关键机制与数据】

- **档位实例化机制**（原文）：当 `set_dim_gears` 指定某维度的分档值列表（如 `{0:[2, 4]}`）后，TorchAir 会将该维度标记为"可分档动态"，并按所选 `dynamic_gears_merge_policy`（zip 或 product）展开为若干具体 shape；每一种具体 shape 都会被编译为一张"可独立整图下发"的静态子图（即 GE 中的 `concrete graph`）。
- **执行时命中机制**（原文）：同一档位内的输入直接复用已编译子图，**不再触发重新编译**；只有当实际 shape 落在已设档位集合之外时，才会触发重编译。
- **档位展开数据流**（原文示例）：input1 与 input2 均设 `{0:[2,4]}` 时，
  - zip 模式 → 2 种组合：(2,2)/(2,2) 与 (4,2)/(4,2)；
  - product 模式 → 4 种组合：(2,2)/(2,2)、(2,2)/(4,2)、(4,2)/(2,2)、(4,2)/(4,2)，其中 (2,2)/(4,2) 与 (4,2)/(2,2) 在 Add 算子上因"两输入 shape 必须相同"而**不符合业务规则**。
- **GE 后端实际下发参数**（原文日志）：
  - `ge.inputShape = arg1_1:-1,2; arg2_1:-1,2`：动态维标注，第二维固定为 2。
  - `ge.dynamicDims = 2,2; 4,4`：枚举出的具体档位值。
  - `ge.dynamicNodeType = 1`、`ge.jit_compile = 2`、`ge.deterministic = 0`、`ge.exec.atomicCleanPolicy = 1` 等：GE 编译选项组合，体现"动态分档 + 静态子图下发"的混合执行模式。
- **整图优化前提**（原文）：文档示例代码使用 `torch.compile(model, fullgraph=True, backend=npu_backend)`，明确要求 **fullgraph=True** 才能保证整图被分档编译。
- **关于性能差原文未给出具体数字**，仅定性描述"动态图比分档后的动态图性能差"。

---

## 【表格解读】

**原文表格 — 表 1 参数说明（逐字还原）：**

| 参数名 | 说明 |
|---|---|
| `dynamic_gears_merge_policy` | 指定动态分档组合模式。若采用 zip 模式配置档位繁琐时，可使用 product 模式配置。zip（默认值）：按位置一一对应。product：排列组合，可以根据笛卡尔积组合成更多的档位。 |

**逐行解读：**
- **第一行（也是唯一一行）**：`dynamic_gears_merge_policy` 是 `CompilerConfig.inference_config` 下的开关项，**默认值 `zip`**。
  - 选择 `zip` 时，多个 Tensor（或同一 Tensor 多维）的档位列表按下标对齐，**组合数等于最短列表长度**，配置直观但展开受限于"按位"对齐关系。
  - 选择 `product` 时，对每个 Tensor/维度的档位集合做**笛卡尔积**，组合数是各集合大小的乘积；**配置简单**（每个维度只需列出有限几个候选值），但可能产生业务不期望的非法组合（如 Add 算子两输入 shape 不一致的情况），需业务侧保证语义正确。

---

## 【公式解读】

**原文无显式 LaTeX 公式**。但文档隐含两个"伪公式"式关系，可用 LaTeX 还原（仅基于原文信息，不引入新数字）：

1. **档位总数约束**（原文："生成的总档位数量不超过 100"）：

$$
N_{\text{total}} \le 100
$$

- $N_{\text{total}}$：经过 `dynamic_gears_merge_policy` 展开后所有 Tensor 档位组合的总数。

2. **档位值合法范围**（原文："档位值不能包含 0 或 1，因为动态 FX graph 中 dim 值符号化的最大表示范围是 [2, ∞)"）：

$$
\forall v \in \text{gears}, \quad v \in [2, +\infty)
$$

- $v$：某一维度的档位取值。

3. **zip 与 product 展开规模**（基于原文 4 个数字示例：input1/input2 各 `{0:[2,4]}`，input3 为 `{0:[2,3,4], 1:[10,20]}`）：

- zip 模式（按位对齐）：$\displaystyle N_{\text{zip}} = \min\!\bigl(\lvert L_{1}\rvert, \lvert L_{2}\rvert, \dots\bigr)$
- product 模式（笛卡尔积）：$\displaystyle N_{\text{product}} = \prod_i \lvert L_{i}\rvert$

其中 $\lvert L_i\rvert$ 为第 $i$ 个 Tensor/维度档位列表的长度。以原文示例：

- input1 与 input2 各 $\{0:[2,4]\}$：zip → $\min(2,2)=2$；product → $2 \times 2 = 4$。
- input3 设 $\{0:[2,3,4], 1:[10,20]\}$：product → $3 \times 2 = 6$，对应原文列出的 6 个档位 $(2,10),(3,10),(4,10),(2,20),(3,20),(4,20)$；若同样 6 个档位用 zip 模式，则需显式写 $\{0:[2,3,4,2,3,4], 1:[10,10,10,20,20,20]\}$，与原文示例一致。

---

## 【关联】

- **与 [`compile_cache.md`](compile_cache.md) 的关系**：文档在"动态shape图分档执行"段落中明确指出，**`torch.compile` 或模型编译缓存功能编译出的图** 都能用于分档场景；意味着分档编译产物同样可被缓存复用，减少命中已设档位输入时的重编译开销。
- **与 [`dynamo_export.md`](dynamo_export.md) 的关系**：在"使用约束"中明确 **互斥**，本功能"暂不支持同时配置 Dynamo 导图功能"。
- **与 [`ref_data.md`](ref_data.md) 的关系**：同样在"使用约束"中明确 **互斥**，"暂不支持同时配置 RefData 类型转换功能"。
- **与 [`set_dim_gears`](../../api/inference/set_dim_gears.md) 的关系**：本文档的核心 API 调用接口，档位由该接口注入；文档"使用方法"步骤 1 完整展示了 `torchair.inference.set_dim_gears(input, dim_gears={dim:[…]})` 的用法。
- **与 [`get_npu_backend`](../../api/torchair/get_npu_backend.md) 的关系**：通过 `CompilerConfig().inference_config.dynamic_gears_merge_policy` 设置组合模式后，由 `torchair.get_npu_backend(compiler_config=config)` 生成 backend 并交给 `torch.compile`，是组合模式生效的承载通道。
- **与 [`cplus_log_print.md`](../basic/cplus_log_print.md) 的关系**：文档"后续操作"段落展示了开启 C++ 层日志后，实际打印的 GE 编译参数（`ge.inputShape`、`ge.dynamicDims` 等），用户可据此核对档位是否与预期一致。
- **上下游模块**：上游是 PyTorch 动态图编译（`torch.compile(dynamic=True)` → Dynamo 符号化），下游是 GE 后端的具体子图（`concrete graph`）下发执行；本能力处于二者之间的"档位化编译/实例化"环节。

---

## 【使用方法】

**原文提供完整步骤，关键要点摘录：**

1. **设置档位**（首次执行前调用一次即可）：

   ```python
   import torch, torch_npu, torchair
   input1 = torch.ones(2, 2).npu()
   input2 = torch.ones(2, 2).npu()
   torchair.inference.set_dim_gears(input1, dim_gears={0:[2, 4]})
   torchair.inference.set_dim_gears(input2, dim_gears={0:[2, 4]})
   ```

   注意事项（原文）：支持同 Tensor 单/多维档位；shape 不在档位内会报错；同一 Tensor 不可两次设置不同档位；总档位 ≤ 100；档位值不含 0/1；仅首次需要设置档位。

2. **（可选）选择组合模式**：

   ```python
   import torch_npu, torchair
   config = torchair.CompilerConfig()
   config.inference_config.dynamic_gears_merge_policy = "zip"   # 或 "product"
   npu_backend = torchair.get_npu_backend(compiler_config=config)
   opt_model = torch.compile(model, backend=npu_backend)
   ```

3. **整图编译 + 执行**（原文示例）：

   ```python
   model = torch.compile(model, fullgraph=True, backend=npu_backend)
   ```

   首次以 (2,2)/(2,2) 执行触发分档编译；再以 (4,2)/(4,2) 执行命中档位，不重新编译。

4. **日志验证**：开启 `TorchAir C++ 层日志打印`（参见 `cplus_log_print.md`），核对 `ge.inputShape` 与 `ge.dynamicDims` 是否与预期档位一致。

> 关于 `dynamic_gears_merge_policy` 之外的其余 `inference_config` 子项、`CompilerConfig` 其余字段的完整列表，原文未涉及。

## 图文联合解读

- `add.png`: 图：两张量shape均为(2,2)，分别由input1、input2流入Add，结果写入output。结论：以(2,2)编译的Add图仅适配该输入规格，是对比静态图、动态图及分档图执行方式的基准。
