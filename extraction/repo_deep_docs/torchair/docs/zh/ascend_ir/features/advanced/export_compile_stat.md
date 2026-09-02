# 图编译统计信息导出功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/export_compile_stat.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/export_compile_stat.md

# 图编译统计信息导出功能 — 一体化深度解读

## 【定位】
这篇文档描述 TorchAir 中"图编译统计信息导出"能力：在 GE 图模式的在线/离线图编译过程中，将图融合与 UB 融合结果以 `fusion_result.json` 形式落盘，使程序即使异常中断也能保留编译结果，便于用户回溯问题定位与分析。

---

## 【技术要点】

1. **适用范围**：原文明确"本功能仅适用于 GE 图模式场景"。
2. **配置入口**：通过 `torchair.get_npu_backend` 的 `compiler_config`，对 `ge_config.export_compile_stat` 赋值开启；`compiler_config` 实例由 `torchair.CompilerConfig()` 构造。
3. **配置项类型**：`export_compile_stat` 为**字符串型**字段（注意是 `str` 而非 `int`，示例中赋值为 `"2"`）。
4. **三个取值层级**：
   - `"0"`：关闭，不生成统计信息。
   - `"1"`：仅在程序运行正常退出时生成统计信息。
   - `"2"`（默认值）：图编译完成时生成统计信息——这是与 `"1"` 的关键差异，因此即使图编译执行中断也仍能落盘。
5. **导出内容**（原文标注"当前"）：仅覆盖**图融合**与 **UB（Unified Buffer）融合**两类信息，对应外部标准《CANN图融合和UB融合规则参考》。
6. **产物文件**：默认在**当前执行路径**（即当前工作目录）下生成 `fusion_result.json`；即使图编译执行中断，依然会有文件保存。

---

## 【关键机制与数据】

**工作原理（基于原文）**：在 GE 图模式编译流水线中，原本只将"图融合"与"UB 融合"结果以内存对象形式存在；本特性在 `export_compile_stat` 触发条件满足时（即对应生命周期的关键节点：图编译完成 / 程序正常退出），将该结果序列化为 `fusion_result.json` 落盘到当前工作目录。

- **触发时点对比**（原文描述）：
  - 取值 `"1"` 对应"程序运行正常退出"——属于进程级别收尾触发。
  - 取值 `"2"` 对应"图编译完成"——属于编译阶段级别触发，独立于进程退出状态，因此崩溃路径也能保留可用结果，原文："开启本功能后，如果图编译执行中断，依然会有文件保存"。
- **数值/性能数据**：原文未给出时间开销、文件体积或吞吐对比等量化指标。
- **边界条件**：原文特别强调"程序异常退出时也能生成编译结果"，这是该功能的核心收益；但同时也限定为 GE 图模式，非 GE 图模式不在覆盖范围。

---

## 【表格解读】

**表 1 参数说明**（原文逐字还原）：

| 参数名 | 说明 |
| -- | -- |
| export_compile_stat | 图编译过程中是否生成统计信息（当前包括图融合/UB融合结果信息），字符串类型。<br>0：关闭，不生成统计信息。<br>1：程序运行正常退出时生成统计信息。<br>2（默认值）：图编译完成时生成统计信息。 |

逐行解读：

- **参数名 `export_compile_stat`**：作为 `ge_config` 下的子字段，是 GE 后端在编译期检查并决定是否落盘 `fusion_result.json` 的总开关。
- **类型约束**："字符串类型"——意味着即使语义上是枚举值也必须以 `str` 形式赋值（代码示例用 `"2"` 而非 `2`），这是配置正确生效的前提。
- **导出范围**："当前包括图融合/UB融合结果信息"中"当前"二字暗示文档成稿时该导出能力只覆盖这两类融合信息，未来若扩展到其他统计维度，理论上无需更改参数名。
- **`0`：关闭**：用于不需要统计、或对落盘开销/磁盘占用敏感的场景；该取值同时也是净化环境、避免污染工作目录的常用选项。
- **`1`：正常退出时生成**：仅依赖进程级退出回调，因此典型用例是脚本化批量推理后做融合回顾；缺点是崩溃/被 kill 等异常路径不落盘。
- **`2`（默认值）：图编译完成时生成**：在 GE 图编译阶段就触发一次落地，因此即使后续程序异常退出，文件仍存在——这是该功能"方便用户问题定位和分析"的实用价值所在，也是推荐的默认行为。

---

## 【公式解读】

原文无公式。

---

## 【关联】

1. **与算子融合规则体系的关联**：本文所导出的图融合、UB 融合结果，规则细节引用了《CANN图融合和UB融合规则参考》——这是 `fusion_result.json` 中字段语义的对标参考。
2. **与编译后端/配置 API 的关联**：本特性挂载在 `torchair.get_npu_backend` 的 `compiler_config`（即 `CompilerConfig`）体系下，属于 GE 后端配置子集；详见内部链接 `../../api/torchair/get_npu_backend.md`。
3. **与产物说明文档的关联**：`fusion_result.json` 的字段结构与样例引用了《融合开关文件-产物说明》章节，详见内部链接 `fusion_switch_file.md#产物说明`。
4. **与 GE 图模式的关系**：本特性"仅适用于 GE 图模式场景"，因此使用前需确认上层调用确实走的是 GE 图编译路径，而非 ACL/单算子等其他执行形态。

---

## 【使用方法】

**启用命令（原文代码示例，仅供参考，不支持直接拷贝运行）**：

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 图编译统计信息导出功能开关
config.ge_config.export_compile_stat = "2"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

**配置项与触发方式（基于原文）**：

| 场景 | 赋值 | 效果 |
| -- | -- | -- |
| 关闭导出 | `config.ge_config.export_compile_stat = "0"` | 不生成 `fusion_result.json` |
| 仅正常退出时导出 | `config.ge_config.export_compile_stat = "1"` | 程序正常退出时生成统计信息 |
| 默认（推荐用法） | `config.ge_config.export_compile_stat = "2"` | 图编译完成时即生成，异常中断也能保留 |

**产物路径**：开启后，默认在"当前执行路径"（即运行脚本时所在的当前工作目录）下生成 `fusion_result.json`；详细内容参见 `fusion_switch_file.md#产物说明`。
