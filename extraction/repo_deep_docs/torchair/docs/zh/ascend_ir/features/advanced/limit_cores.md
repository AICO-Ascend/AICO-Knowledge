# AI Core和Vector Core限核功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/limit_cores.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/limit_cores.md

# 一体化深度解读：AI Core和Vector Core限核功能

## 【定位】

本文档描述 TorchAir 在昇腾 NPU 上、GE 图模式下，如何通过**算子级**和**全局（session）级**两种粒度限制 AI Core / Vector Core 使用数量，解决**多流场景中所有核被单一流独占、导致算子并行度下降**的问题，从而提升算子并行执行的收益。

---

## 【技术要点】

1. **问题背景**：多流场景下可能出现所有 Core 被一个流占用，导致算子执行并行度降低，限核是为了把核分给不同流以保证并行收益。
2. **两种限核方法**：
   - **算子级核数**（operator-level）：通过 `torchair.scope.limit_core_num(op_aicore_num, op_vectorcore_num)` 的 `with` 语句块指定块内算子使用的最大核数。
   - **全局核数**（session-level）：通过 `torchair.get_npu_backend` 中的 `compiler_config`（即 `config.ge_config.aicore_num`）指定。
3. **优先级关系**：**算子级核数配置的优先级高于全局核数配置**。
4. **取值范围**：
   - `op_aicore_num`：取值范围 `[1, max_aicore]`。
   - `op_vectorcore_num`：取值范围 `[1, max_vectorcore]`；当 AI 处理器上**仅存在 AI Core 不存在 Vector Core** 时，仅支持取值为 **0**。
   - 全局 `${aicore_num}` / `${vectorcore_num}`：整数类型，取值范围分别为 `[1, max_aicore]` / `[1, max_vectorcore]`。
5. **格式约定**：全局核数必须使用 `|` 分隔，形如 `{aicore_num}|${vectorcore_num}`（字符串类型）。
6. **使用约束**：
   - 本功能**仅适用于 GE 图模式场景**。
   - 配置的核数**不能超过 AI 处理器本身允许的最大核数**；若超出，**默认采用最大核数作为实际运行核数**。
   - 运行过程中**实际使用的核数可能少于配置的最大核数**。

---

## 【关键机制与数据】

- **核数查询方式**：用户可通过 `CANN软件安装目录/<arch>-linux/data/platform_config/<soc_version>.ini` 查看 AI 处理器的核心规格，原文示例展示某 SoC：
  - `ai_core_cnt = 24`
  - `cube_core_cnt = 24`
  - `vector_core_cnt = 48`
- **限核生效判定**：通过 `Change ge.aicoreNum from xx` 和 `Change ge.vectorcoreNum from xx` 日志判断。若配置超过最大核数，则被截断为最大核数。原文示例配置 `aicore_num="24|100"`，日志显示实际生效为 **`aicore_num=20`、`vectorcore_num=40`**（即平台上限）。
- **核数生效链路**（从日志可追踪）：
  - `CreateSession` → 写入 GE option `ge.aicoreNum / ge.vectorcoreNum`；
  - `parseAicoreNumOption` 解析 origin 值；
  - `UpdateCoreCountWithOption` 将值写入 `ThreadLocalContext`；
  - 与 platform 默认值（如 `platform 20`、`platform 40`）对比；
  - 若超过则 `Change ge.aicoreNum from platform 20 to rts 20`（保留上限）；
  - TEFUSION 侧 `InitConfigItemsFromOptions` 读取最终生效值 `[20]`。
- **算子级核数验证方式**：通过图 dump（`config.debug.graph_dump.type="txt"` 或 `"pbtxt"`），在算子的 `attr` 属性中以 `_op_aicore_num` 和 `_op_vectorcore_num` 为 key 查看生效的核数。

---

## 【表格解读】

**原文无独立"参数表"标题，仅列出**：

**表 1  参数说明**

| 参数名 | 说明 |
| -- | -- |
| aicore_num | 指定全局 AI Core 和 Vector Core 数，字符串类型。 |

**逐行解读**：
- `aicore_num`：唯一在表 1 中明确列出的全局配置项，类型为字符串。其完整格式在表后说明文字中补充为 `{aicore_num}|${vectorcore_num}`，通过 `|` 分隔 AI Core 数与 Vector Core 数，两者均为整数，且各自有独立的取值上限（`max_aicore` / `max_vectorcore`）。

文档其他参数（`op_aicore_num`、`op_vectorcore_num`、`_op_aicore_num`、`_op_vectorcore_num`、`ge.aicoreNum`、`ge.vectorcoreNum` 等）以正文段落或代码注释形式给出，未单独成表。

---

## 【公式解读】

原文无标准数学公式，但存在一个**配置格式约定**，可视为伪代码公式：

```
aicore_num = "{aicore_num}|${vectorcore_num}"
```

- **`|`**：必填分隔符，分隔 AI Core 数与 Vector Core 数。
- **`${aicore_num}`**：整数，表示全局 AI Core 数，取值范围 `[1, max_aicore]`。
- **`${vectorcore_num}`**：整数，表示全局 Vector Core 数，取值范围 `[1, max_vectorcore]`。
- **整体字符串**：作为 `config.ge_config.aicore_num` 的赋值（原文示例：`config.ge_config.aicore_num = "24|100"` 与 `"24|48"`）。

算子级使用方式为 Python 上下文表达式（伪代码形式）：

```
with torchair.scope.limit_core_num(op_aicore_num: int, op_vectorcore_num: int):
    # 块内算子按入参指定核数
```

- **`op_aicore_num: int`**：该算子运行时的最大 AI Core 数，取值 `[1, max_aicore]`。
- **`op_vectorcore_num: int`**：该算子运行时的最大 Vector Core 数，取值 `[1, max_vectorcore]`；仅 AI Core 无 Vector Core 场景下可取 `0`。

---

## 【关联】

根据文末内部链接，可串联出本文档在 TorchAir 文档体系中的上下游：

- **AI Core/Cube Core/Vector Core 基础概念**：[`../../../appendix/appendix/aicore.md`](../../../appendix/appendix/aicore.md) — 提供 AI Core / Cube Core / Vector Core 的硬件背景知识，是理解"为什么要限核"的物理基础。
- **Eager 与图模式控核差异**：[`../../../appendix/appendix/core_limit.md`](../../../appendix/appendix/core_limit.md) — 区分 Eager 模式与图模式下控核方式的差异，本文聚焦 GE 图模式。
- **算子级限核 API**：[`../../api/scope/limit_core_num.md`](../../api/sorch/limit_core_num.md) — 即 `torchair.scope.limit_core_num` 的 API 参考，定义 `with` 语句块的具体语义与参数。
- **图结构 dump 功能**：[`../basic/graph_dump.md`](../basic/graph_dump.md) — 用于校验算子级 `_op_aicore_num` / `_op_vectorcore_num` attr 是否生效。
- **NPU 后端与 CompilerConfig**：[`../../api/torchair/get_npu_backend.md`](../../api/torchair/get_npu_backend.md) — 全局核数配置 `config.ge_config.aicore_num` 通过该接口注入编译后端。

整体来看：本文档位于 TorchAir `advanced` 特性层，向上承接底层硬件概念（aicore.md / core_limit.md），向下消费两类 API（`scope.limit_core_num` 与 `get_npu_backend`），并依赖图 dump 工具做结果验证。

---

## 【使用方法】

**原文给出完整三步流程与示例代码，关键配置项与命令如下**：

1. **分析模型脚本**：用户自行分析需要指定核数的算子。
2. **（可选）算子级核数配置**：

   ```python
   with torchair.scope.limit_core_num(op_aicore_num: int, op_vectorcore_num: int):
   ```

   - 通过图 dump（`config.debug.graph_dump.type = "txt"` 或 `"pbtxt"`）在算子 `attr` 中以 `_op_aicore_num` / `_op_vectorcore_num` key 验证。
3. **（可选）全局核数配置**：

   ```python
   import torch_npu, torchair
   config = torchair.CompilerConfig()
   config.ge_config.aicore_num = "24|100"   # 格式 "{aicore_num}|${vectorcore_num}"
   npu_backend = torchair.get_npu_backend(compiler_config=config)
   opt_model = torch.compile(model, backend=npu_backend)
   ```

   - 验证方式：开启 Python 侧日志（`logger.setLevel(logging.DEBUG)`），在 `plog` 中查看 `ge.aicoreNum` / `ge.vectorcoreNum` 的实际生效值。

**原文给出的完整使用示例**（节选关键片段）：

```python
class Model(torch.nn.Module):
    def forward(self, in1, in2, in3, in4):
        with torchair.scope.limit_core_num(4, 5):           # 算子级：AI Core=4, Vector Core=5
            mm_result  = torch.mm(in3, in4)
            add_result = torch.add(in1, in2)
        mm1_result = torch.mm(in3, in4)                      # 块外使用全局配置
        return add_result, mm_result, mm1_result

config = CompilerConfig()
config.debug.graph_dump.type = "pbtxt"
config.ge_config.aicore_num = "24|48"                       # 全局：AI Core=24, Vector Core=48
npu_backend = torchair.get_npu_backend(compiler_config=config)
model = torch.compile(model, backend=npu_backend, dynamic=False, fullgraph=True)
```

**注意事项（原文约束摘要）**：
- 仅 GE 图模式场景适用。
- 核数不得超过 AI 处理器硬件上限；超过则被截断为最大核数。
- `op_vectorcore_num` 在"仅有 AI Core 无 Vector Core"硬件上仅支持 `0`。
- 算子级优先级高于全局级。
