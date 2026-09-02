# INDUCTOR_ASCEND_CHECK_ACCURACY

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/other/INDUCTOR_ASCEND_CHECK_ACCURACY.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/other/INDUCTOR_ASCEND_CHECK_ACCURACY.md

# INDUCTOR_ASCEND_CHECK_ACCURACY 深度解读

## 【定位】
这是一篇描述 TorchNPU（昇腾 PyTorch 适配插件）中 Inductor 后端**精度对比调试开关**的环境变量文档，通过 `INDUCTOR_ASCEND_CHECK_ACCURACY` 控制是否启用 triton 后端单算子用例 dump 与精度对比工具。

---

## 【技术要点】

1. **核心能力**：开启 triton 后端精度对比工具，自动 dump 单算子用例，便于比对算子层的实际输出精度。
2. **级联触发**：当本变量启用时，会**自动启用** `INDUCTOR_ASCEND_DUMP_FX_GRAPH` 功能——二者存在隐式联动关系。
3. **取值语义**：默认值为空（关闭），启用值采用宽松布尔语义——`1`、`true`、`yes` 等都能开启。
4. **性能副作用**：启用后会**影响编译效率**，因此定位为**仅限调试与精度验证场景**使用的工具开关。
5. **支持的型号范围**：仅在 **Atlas A5 系列产品** 上支持。
6. **启用方式**：通过 shell 环境变量 `export` 注入，无须修改代码或配置文件。

---

## 【关键机制与数据】

- **工作机制**（原文）：文档仅描述了“开启 triton 后端精度对比工具，dump 单算子用例”这一高层行为，**未给出**底层数据流、采样流程、对比基线（如 vs eager 模式 vs CPU 参考实现）、误差阈值等具体细节。
- **级联机制**（原文）：`INDUCTOR_ASCEND_CHECK_ACCURACY` 启用 → 自动联动开启 `INDUCTOR_ASCEND_DUMP_FX_GRAPH`，原文未说明反向是否成立（即 dump fx graph 开启是否会反向触发本开关）。
- **性能数据**：原文**未提供**任何编译耗时、运行时开销、内存占用等量化数据，仅以“会影响编译效率”做定性描述。
- **配置示例**（原文）：
  ```bash
  export INDUCTOR_ASCEND_CHECK_ACCURACY=1
  ```

---

## 【表格解读】

下表为**逐字还原**原文中“功能描述”下的取值说明表：

| 值 | 说明 |
|---|---|
| 未设置或空 | 关闭精度对比工具（默认值） |
| 1、true、yes等 | 开启精度对比工具 |

**逐行解读**：

- **第 1 行 – “未设置或空”**：表示环境变量未定义或其值为空字符串，对应**默认关闭**状态，精度对比工具不生效，triton 后端走正常的编译/执行路径，不进行单算子 dump 与精度比对。
- **第 2 行 – “1、true、yes等”**：列出三类典型“真值”字符串作为启用标志（`1`、`true`、`yes`），并以“等”字提示存在其他等价真值（如 `True`、`YES`、`on` 等宽松解析）。原文未严格列出全部可识别字符串，仅给出一组示例。

---

## 【公式解读】

**原文无公式**。本文档为环境变量开关的功能说明文档，不涉及任何数学公式、性能模型或阈值判定式。

---

## 【关联】

- **`INDUCTOR_ASCEND_DUMP_FX_GRAPH`**（强关联，正向级联）：
  - 文档明确指出——当 `INDUCTOR_ASCEND_CHECK_ACCURACY` 启用时，**会自动启用** `INDUCTOR_ASCEND_DUMP_FX_GRAPH`。
  - 含义：本开关并非独立功能，而是 dump fx graph 能力之上的“精度对比”增强层；dump 出 fx graph 后才能在其上跑精度比对流程。
  - 原文未提及反向关系，也未提供 `INDUCTOR_ASCEND_DUMP_FX_GRAPH` 文档的内部链接。
- **triton 后端**（隐含依赖）：本工具作用于 triton 后端路径，与非 triton 后端（如纯 AscendC / 图算子路径）的精度调试机制是否存在，文档未涉及。
- **编译流程**（影响范围）：原文提示“会影响编译效率”，表明本开关会改变 Inductor 编译期的图处理与 dump 流程，但具体改动点未在本文档中展开。
- **支持的硬件平台**：仅 **Atlas A5 系列产品**，意味着在 Atlas 训练/推理系列产品（如 Atlas 800I A2、Atlas 900 A3 SuperPoD 等非 A5 型号）上本文档所述开关的支持情况未在原文覆盖。

> 备注：原文**未提供任何文末内部链接**，因此以上关联信息均依据文档正文中出现的特性名/模块名推断。

---

## 【使用方法】

**启用命令**（原文）：
```bash
export INDUCTOR_ASCEND_CHECK_ACCURACY=1
```

**关闭方式**（原文未涉及具体 unset 写法，但根据“未设置或空 = 关闭”的语义）：
- 不设置该环境变量；或
- `unset INDUCTOR_ASCEND_CHECK_ACCURACY`；或
- 将其值置为空字符串。

**使用约束**（原文）：
- 开启精度对比工具**会影响编译效率**，建议仅在**调试和精度验证**时使用，**不推荐**在生产训练/推理流程中长期保持开启。
- 启用本变量时**会自动启用** `INDUCTOR_ASCEND_DUMP_FX_GRAPH`——若不希望 fx graph 被同时 dump，需谨慎评估。

**适用硬件**（原文）：仅 **Atlas A5 系列产品**。

**其他配置项**（如阈值、最大 dump 数量、对比基线等）：**原文未涉及**。
