# NPU_DEVICE_LIMIT

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/limit_core/limit_core.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/limit_core/limit_core.md

# NPU_DEVICE_LIMIT 文档深度解读

---

## 【定位】

本文档描述了 `NPU_DEVICE_LIMIT` 这一环境变量特性：通过对 NPU 卡的 Cube Core 与 Vector Core 计算核进行划分/限核，使一个计算图内的算子仅能使用受限范围内的计算核，从而在同一张 NPU 卡上支持多个实例（多个算子）并发推理，专门服务于小 shape 模型场景下算子打不满计算核导致的算力浪费问题。

---

## 【技术要点】

1. **核心机制**：通过环境变量 `NPU_DEVICE_LIMIT` 限制当前进程/计算图可使用的 Cube Core 与 Vector Core 数量，格式为字符串 `'Cube数,Vector数'`（如 `'14,28'` 或 `'7,14'`）。
2. **作用范围**：限制作用于单个计算图中所涉及的所有算子类型，涵盖 **AclNN 算子、triton 手写算子、triton 自动融合算子、catlass 算子** 四类。
3. **核心配比约束**：在 **A2/A3/A5 代际** 的 NPU 上，Cube 与 Vector 的物理配比为 **1:2**，因此设置 `NPU_DEVICE_LIMIT` 时建议保持 Cube:Vector = 1:2 的比例（如 `'14,28'`、`'7,14'`）。
4. **默认行为**：若不设置该环境变量，则默认使用 NPU 上**全部**的 Cube Core 与 Vector Core 核。
5. **应用场景**：针对算子 shape 较小、无法打满 cube core 与 vector core 的小 shape 模型场景，通过分核/限核实现多个算子在同一张 NPU 卡上并发执行。
6. **当前支持型号**：**Atlas A5 系列产品**（文档明确标注的型号）。

---

## 【关键机制与数据】

**工作原理**（原文）：
- 用户通过 `export NPU_DEVICE_LIMIT='14,28'` 设定可用 Cube Core 数 = 14、Vector Core 数 = 28；
- 运行时框架将按该配额向当前计算图暴露计算资源，使其所包含的各类算子（aclNN、triton 手写、triton 自动融合、catlass）最多使用这 14 个 Cube Core 与 28 个 Vector Core；
- 剩余的物理核对其他实例/进程可见，从而支持**多实例并发推理**。

**数据流**（原文）：
- 输入：环境变量字符串 → 解析为 (cube_limit, vector_limit) 二元组；
- 输出：受控的计算图 → 使用受限计算核完成算子调度；
- 剩余核资源 → 供同一 NPU 卡上的其他实例并发使用。

**性能数据**：原文未提供量化性能数据，仅以定性方式描述"避免小 shape 模型算力浪费"的目标。

---

## 【表格解读】

原文表格逐字还原：

| 值 | 说明 |
|---|---|
| 例'7,14'或者'14,28' | Cube和Vector的核数限制 |

**逐行解读**：
- **第一行（值列）**：给出两种示例数值 `'7,14'` 与 `'14,28'`。其中第一个数字为 Cube Core 限制数，第二个为 Vector Core 限制数。
- **第一行（说明列）**：明确说明该值的语义为"Cube 和 Vector 的核数限制"，即整张表的语义在于描述该环境变量的合法取值范围示例。
- **数值含义**：`'7,14'` 对应 Cube:Vector = 1:2 的比例，`'14,28'` 同样保持 1:2 比例，与 A2/A3/A5 代际 1:2 物理配比的约束一致。
- **隐含规则**：表格仅给出"例子"而非"可选值全集"，意味着实际可设值需用户根据 NPU 型号实际核数与 1:2 比例自行推导。

---

## 【公式解读】

原文无公式。

（虽存在 Cube:Vector = 1:2 的隐含比例关系，但原文并未以数学公式形式给出，故不做公式化表达。）

---

## 【关联】

原文未提供任何内部链接（文档标注"内部链接: (无)"），但从内容可归纳以下关联模块/特性：

- **下游算子类型**：`NPU_DEVICE_LIMIT` 的限制范围覆盖以下四类算子：
  - **AclNN 算子**（昇腾标准算子库）
  - **triton 手写算子**（用户/开发者通过 Triton 语言手写的算子）
  - **triton 自动融合算子**（Inductor 等模块自动生成的 Triton 融合算子）
  - **catlass 算子**（昇腾类 CUDA 模板库算子）
- **硬件代际关联**：与 **A2/A3/A5 代际** NPU 的物理核配比（Cube:Vector = 1:2）强相关，该配比决定了合法限核值的推荐比例。
- **典型应用场景**：小 shape 模型多实例并发推理，与"小 shape 模型"优化主题相关，但文档未给出进一步跳转链接。

---

## 【使用方法】

**启用方式（原文有）**：

```bash
export NPU_DEVICE_LIMIT='14,28'
```

**配置项（原文有）**：

| 配置项 | 取值说明 |
|---|---|
| `NPU_DEVICE_LIMIT` | 字符串格式 `'Cube核数,Vector核数'`，例如 `'7,14'` 或 `'14,28'`；Cube 与 Vector 数量比例建议为 **1:2**（A2/A3/A5 代际约束）；不设置则默认使用全部 Cube 与 Vector 核 |

**使用约束（原文有）**：
- 仅推荐在 **A2/A3/A5 代际** NPU 上设置，且 Cube:Vector 比例需保持 **1:2**。
- 若不设置，默认占用 NPU 全部计算核。

**支持型号（原文有）**：
- Atlas A5 系列产品

**命令/示例（原文有）**：

```bash
export NPU_DEVICE_LIMIT='14,28'    # 划分 14 个 Cube Core 与 28 个 Vector Core 作为可用资源
```
