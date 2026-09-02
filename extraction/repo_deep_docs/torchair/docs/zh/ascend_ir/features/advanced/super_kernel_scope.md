# 图内标定SuperKernel范围

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/super_kernel_scope.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/super_kernel_scope.md

# 图内标定SuperKernel范围 — 一体化深度解读

## 【定位】

本文档解决"如何在 GE 图模式下，以用户主动标定（with 上下文）的方式圈定 SuperKernel 融合范围，并对该范围施加细粒度编译选项，从而优化算子调度开销、提升昇腾 NPU 推理性能"的问题。

---

## 【技术要点】

1. **能力定位**：SuperKernel 是基于已编译二进制代码的多 Kernel 融合技术（区别于源码融合），将子图中多个 Kernel 入口以子函数调用方式合并为单个超级 Kernel，配合图依赖关系插入同步，以减少调度等待与算子头开销。

2. **使用前提**：仅适用于 **GE 图模式 + 静态图** 场景；支持的产品范围为 **Atlas A5/A3/A2 训练与推理系列**。

3. **融合策略**：按网络中算子顺序依次识别能否融合，**遇到不可融合算子即生成第一段 SuperKernel 并自动跳过该算子，开始第二段 SuperKernel 融合**。当前支持 SuperKernel 融合的通信类算子包括 **AllReduce、ReduceScatter、AllGather、AlltoAll**。

4. **核心 API**：`torchair.scope.super_kernel(scope: str, options: str = '')`；`scope` 字符串相同的 with 块视为同一融合范围，传入 `None` 表示该范围不进行 SuperKernel 融合。

5. **编译选项格式**：`<option1>=<value1>:<option2>=<value2>:…`，多个选项用 **英文冒号** 分隔，可自定义组合（覆盖默认）。

6. **核数控制约束**：`debug-aic-num` 与 `debug-aiv-num` 的比例仅支持 **1:0、0:1、1:1、1:2** 四种；其数值不可超过当前硬件最大核数，亦不可超过 SuperKernel 原本应启动的核数；若范围内算子使用 `limit_core_num`，则同时受其上限约束。

7. **DCache 一致性三选项族**：`dcci-before-kernel-start` / `dcci-after-kernel-end` / `dcci-disable-on-kernel` 均通过指定 `op_type` 列表（示例 `dcci-before-kernel-start=GroupedMatmul,MoeGatingTopK`）来抑制算子内部自动插入缓存刷新指令，改由 SuperKernel 调度前/后/完全不再插入 `DataCacheCleanAndInvalid`；对 **Tiling 下沉的算子或通信类算子不生效**。

---

## 【关键机制与数据】

- **实现原理（原文二步走）**：
  1. 通过 SuperKernel 融合策略识别可被融合的子图；
  2. 将子图内算子按融合规则合并为一个大 Kernel，在新 Kernel 内生成一段子 Kernel 调用代码，将子图上所有 Kernel 入口函数完成一次调用，并基于图的依赖完成同步插入。

- **收益来源（原文）**：与单算子下发相比，SuperKernel 可优化任务调度的等待时间和调度开销，并利用 task 间隙资源进一步优化算子头开销；多流融合（`stream-fusion=1`）的收益来自**减少各流上算子的调度开销**，而非增加并行度，融合前后跨流并行能力不变；Cube 算子与 Vector 算子多流并行融合通常可获得较好收益。

- **同步机制**：SuperKernel 启动核数 = 范围内子算子的最大启动核数（原文示例：算子 a 启动核数 4、算子 b 启动核数 2 → SK 启动核数 4）；当子算子使用 `SyncAll` 全核同步指令时，可启用 `feed-sync-all=1`，系统会在子算子其余核中插入 `SyncAll`，保证同步次数匹配，防止卡住超时。

- **性能数据采集**：启动核数通过 Profiling 采集的 `kernel_details.csv` 中 **"Block Dim"** 字段获取（参考文档内「性能分析案例」章节）。

- **示例中的数据规模**：`token_num = 864`，`expert_num = 2048`，`top_k = 1024`，模型对比 `ModelOrigin`（不融合）与 `ModelSuperKernel`（用 `super_kernel("sp1", "")` 圈定 `npu_moe_gating_top_k_softmax` + `npu_dynamic_quant` 融合为 SuperKernel），通过 `np.array_equal` 验证精度一致后输出 "Precision ====== Success!!!"。

---

## 【表格解读】

原文 **表 1 编译选项说明** 还原如下：

| 选项参数 | 说明 |
|---|---|
| feed-sync-all | 当子算子启动核数小于 SuperKernel 启动核数且使用了 SyncAll 全核同步指令，若出现算子执行卡住或超时，可尝试配置本选项解决此问题。<br>**0**：关闭本功能（默认值），若子算子使用 SyncAll 全核同步指令，用户需自行保证子算子与 SuperKernel 启动核数相同。<br>**1**：开启本功能，系统自动识别 SuperKernel 内算子是否调用 SyncAll 全核同步指令，同时判断子算子启动核数是否小于 SuperKernel 启动核数。若小于 SuperKernel 启动核数，会在 SuperKernel 内子算子的其余核中插入 SyncAll 指令，保证与子算子内调用 SyncAll 次数匹配，防止卡住超时。<br>SuperKernel 启动核数为子算子的最大启动核数。假设 SuperKernel 包括算子 a（启动核数为 4）和算子 b（启动核数为 2），此时 SuperKernel 启动核数为 4。<br>启动核数可通过 Profiling 采集的性能数据获取，即"kernel_details.csv"文件中"Block Dim"字段，采集操作请参考性能分析案例。<br>**子算子启动核数**：非 SuperKernel 场景下开启 Profiling，"Block Dim"字段表示每个算子的启动核数。<br>**SuperKernel 启动核数**：SuperKernel 场景下开启 Profiling，"Block Dim"字段表示 SuperKernel 的启动核数。 |
| stream-fusion | 控制 SuperKernel 内是否启用多流融合，从而提升算子运行效率，选项取值如下：<br>**0（默认值）**：关闭多流融合。当标定范围内存在算子分布在多条流上的场景时，将触发编译报错，无法完成融合。<br>**1**：启用多流融合，表示 SuperKernel 融合范围的算子可分布在多条流上。<br>多流融合的收益来自减少各流上算子的调度开销，而非增加并行度，融合前后跨流并行能力不变。SuperKernel 内部因同步约束可能引入串行化，实际收益取决于算子排布，通常 Cube 算子和 Vector 算子多流并行融合可以获得较好收益。 |
| strict-scope-check | 本选项用于检查 SuperKernel 融合的范围是否符合预期。对于断开的 SuperKernel、不支持融合的算子可通过本功能查询：<br>**bypass**：打印 C++ 侧 Warning 级别日志，忽略该范围的 SuperKernel 生成。<br>**abort**：打印 C++ 侧 Error 级别日志，对该范围的 SuperKernel 直接报错退出。<br>Warning 或 Error 级别日志信息可在 plog 文件（文件名为 plog-`*pid_**.log`）中查看，搜索关键字"super_kernel_scope"即可。<br>本功能暂不支持检查 SuperKernel 融合范围内的集合通信算子，如 AllGather、AlltoAll 等。 |
| dcci-before-kernel-start | 通过本选项指定的算子，其内部调用 GlobalTensor 的 GetValue/SetValue 时不会自动插入缓存刷新指令，**而在 SuperKernel 调用该算子前**会插入 DataCacheCleanAndInvalid 指令，刷新整个 DCache（数据缓存），保证该算子内的数据缓存不受前序算子的影响。<br>配置格式形如：`dcci-before-kernel-start=<op1_type>,<op2_type>`<br>本选项在保证算子本身 cache 一致性的前提下可提升模型性能，原理可参考《CANN Ascend C 算子开发》中"编程指南>附录>算子入图（GE图）开发>SuperKernel开发"章节。<br>若本选项指定的算子为支持 Tiling 下沉的算子或通信类算子，功能将不生效。<br>DataCacheCleanAndInvalid 接口介绍参见《CANN Ascend C API》中"基础API>缓存处理>DataCacheCleanAndInvalid"章节。<br>本选项指定的算子 op_type 可通过 Profiling 查看，例如：`dcci-before-kernel-start=GroupedMatmul,MoeGatingTopK`。 |
| dcci-after-kernel-end | 通过本选项指定的算子，其内部调用 GlobalTensor 的 GetValue/SetValue 时不会自动插入缓存刷新指令，**而在 SuperKernel 调用该算子后**，会插入 DataCacheCleanAndInvalid 指令，刷新整个 DCache（数据缓存），保证该算子内的数据缓存不会影响后续的算子。<br>配置格式形如：`dcci-after-kernel-end=<op1_type>,<op2_type>`。<br>其他要求与 dcci-before-kernel-start 一样。 |
| dcci-disable-on-kernel | 通过本选项指定的算子，其内部调用 GlobalTensor 的 GetValue/SetValue 时不会自动插入缓存刷新指令，**而在 SuperKernel 调用该算子前后**，不会插入任何 DataCacheCleanAndInvalid 指令。<br>配置格式形如：`dcci-disable-on-kernel=<op1_type>,<op2_type>`。<br>其他要求与 dcci-before-kernel-start 一样。 |
| debug-aic-num | 本选项用于指定 Scope 内 SuperKernel 最终启动的 aic 核数（Cube Core），要求正整数，配置格式形如：`debug-aic-num=10`。<br>本选项通常与 debug-aiv-num 一同使用，对应不同的 kernel type，组合效果如下：<br>`debug-aic-num=12`，SK 按照 MIX_AIC_1_0 启动 12 核。<br>`debug-aic-num=12:debug-aiv-num=0`，SK 按照 MIX_AIC_1_0 启动 12 核。<br>`debug-aiv-num=12`，SK 按照 MIX_AIV_1_0 启动 12 核。<br>`debug-aiv-num=12:debug-aic-num=0`，SK 按照 MIX_AIV_1_0 启动 12 核。<br>`debug-aic-num=12:debug-aiv-num=12`，SK 按照 MIX_AIC_1_1 启动 12 核。<br>`debug-aic-num=12:debug-aiv-num=24`，SK 按照 MIX_AIC_1_2 启动 12 核。<br>`debug-aic-num` 与 `debug-aiv-num` 的比例仅支持 1:0、0:1、1:1、1:2。<br>`debug-aic-num` 与 `debug-aiv-num` 的数值不可超过当前硬件最大核数，若 SuperKernel Scope 内算子使用 `limit_core_num` 控制核数，则不可超过其设置的最大核数。<br>`debug-aic-num` 与 `debug-aiv-num` 的数值不可超过 SuperKernel 原本应启动的核数。 |
| debug-aiv-num | 本选项用于指定 Scope 内 SuperKernel 最终启动的 aiv 核数（Vector Core），要求正整数，配置格式形如：`debug-aiv-num=10`。其他要求与 debug-aic-num 一样。 |

### 逐行解读

- **feed-sync-all**：解决"SK 内子算子使用了 `SyncAll` 全核同步指令，但子算子启动核数小于 SK 启动核数"导致的卡住/超时问题。开启（=1）后系统自动在 SK 内子算子的其余核上补 `SyncAll`，让同步指令次数与子算子内部一致。默认关闭（=0），用户需自行保证核数对齐。启动核数通过 Profiling 的 `Block Dim` 字段采集。

- **stream-fusion**：控制多流融合是否启用。默认关闭且**强制单流**（多流场景会编译报错）；开启后 SK 范围算子可跨流分布。注意收益来源是**减少调度开销**而非提升并行度，Cube/Vector 算子多流并行融合通常收益较好，SK 内部同步约束可能引入额外串行化。

- **strict-scope-check**：用于调试融合范围是否正确。`bypass` 仅 Warning 并跳过该范围 SK 生成；`abort` 则 Error 级直接报错退出。日志位于 plog 文件（`plog-*pid_**.log`），关键字 `super_kernel_scope`。**当前不支持检查集合通信算子（AllGather、AlltoAll 等）**。

- **dcci-before-kernel-start**：将指定 `op_type` 算子的内部缓存刷新（DCache）从算子内部移到 **SK 调用该算子之前**，避免前序算子遗留脏数据。配置格式 `<op1_type>,<op2_type>`。对 Tiling 下沉算子、通信类算子不生效；`op_type` 可通过 Profiling 查看。

- **dcci-after-kernel-end**：与上一项对称，缓存刷新放在 **SK 调用该算子之后**，防止本算子脏缓存污染下游。其他要求与 `dcci-before-kernel-start` 相同。

- **dcci-disable-on-kernel**：对指定 `op_type` 算子，**SK 调用前后都不再插入** `DataCacheCleanAndInvalid`，完全禁用该 SK 节点周围的自动 DCache 刷新。其他要求同上。

- **debug-aic-num / debug-aiv-num**：分别控制 **Cube Core** 与 **Vector Core** 的最终启动核数（正整数）。组合 kernel type 矩阵共 6 种典型组合（MIX_AIC_1_0、MIX_AIV_1_0、MIX_AIC_1_1、MIX_AIC_1_2 等）；aic:aiv 比例仅支持 4 种（1:0、0:1、1:1、1:2）；同时受 **硬件最大核数 + 算子用 `limit_core_num` 设置的上限 + SK 原本应启动核数** 三重封顶。

---

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的公式定义）。仅给出伪代码式的 API 签名：

```python
with torchair.scope.super_kernel(scope: str, options: str = ''):
```

- **scope**：`str`，标识 SuperKernel 范围名；同名 = 同一范围；传 `None` 表示该范围不融合。
- **options**：`str`，编译选项串，格式 `"<option1>=<value1>:<option2>=<value2>:..."`，英文冒号分隔。

---

## 【关联】

- **下游/调试调优**：确认融合结果、定位执行异常、分析性能无收益/劣化时，参考 **SuperKernel 调试调优方法 → `../../../appendix/cases/superkernel_cases.md#ge图模式`**。
- **核数控制协同**：`debug-aic-num` / `debug-aiv-num` 必须不超过 SK 范围内算子使用 `limit_core_num` 设置的最大核数，详见 **`../../api/scope/limit_core_num.md`**。
- **API 主入口**：本文档使用的 `torchair.scope.super_kernel(scope, options)` 接口详见 **`../../api/scope/super_kernel.md`**。
- **性能数据采集**：核数（Block Dim）的 Profiling 采集方法详见 **`../../../appendix/cases/performance_cases.md#性能分析案例`**。
- **底层原理依赖**：DCache 同步（dcci-* 选项族）的底层机制可参考 CANN 官方文档《Ascend C 算子开发》中"编程指南>附录>算子入图（GE图）开发>SuperKernel开发"章节，以及《CANN Ascend C API》中"基础API>缓存处理>DataCacheCleanAndInvalid"（外部链接，本文未给出 URL 的相对路径）。
- **支持的算子族**：通信类 AllReduce、ReduceScatter、AllGather、AlltoAll 已支持 SuperKernel 融合（其它通信算子未列）；集合通信算子在 `strict-scope-check` 下暂不检查。

---

## 【使用方法】

**步骤（原文）**：
1. 用户自行分析模型脚本中可被融合的算子。
2. 标定 SuperKernel 范围：使用 `with torchair.scope.super_kernel(scope: str, options: str = ''):` 包裹需要融合的算子；`scope` 相同代表同一范围，传 `None` 表示不融合；`options` 默认采用表 1 所有默认值，也支持 `"<option>=<value>"` 自定义组合、英文冒号分隔。

**可配置编译选项（参数项及取值，原文已逐项给出）**：
- `feed-sync-all`：0（默认）/ 1
- `stream-fusion`：0（默认）/ 1
- `strict-scope-check`：bypass / abort
- `dcci-before-kernel-start=<op1_type>,<op2_type>,…`
- `dcci-after-kernel-end=<op1_type>,<op2_type>,…`
- `dcci-disable-on-kernel=<op1_type>,<op2_type>,…`
- `debug-aic-num=<正整数>`：建议与 `debug-aiv-num` 联用；比例限 1:0 / 0:1 / 1:1 / 1:2
- `debug-aiv-num=<正整数>`：要求与 `debug-aic-num` 对称

**示例代码（原文）**：用 `torchair.get_npu_backend(compiler_config=config)` 编译，分别运行 `ModelOrigin`（无 SK）与 `ModelSuperKernel`（用 `with torchair.scope.super_kernel("sp1", "")` 包裹 `npu_moe_gating_top_k_softmax` + `npu_dynamic_quant`），用 `np.array_equal` 校验两组输出一致后打印 "Precision ====== Success!!!"。
