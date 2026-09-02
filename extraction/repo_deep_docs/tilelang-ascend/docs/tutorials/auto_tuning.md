# Reserved parameters for optimization

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/auto_tuning.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/auto_tuning.md

# tilelang-ascend · Auto-Tuning 文档深度解读

---

## 【定位】

这篇文档是 tilelang-ascend 项目中关于 **Tile Language 程序自动调优(Auto-Tuning)** 的入门指南,系统性地描述了如何通过预留优化参数、生成候选配置、并行编译与基准测试来自动寻找 GEMM 等算子的最优性能配置,并引入了 Carver 框架作为候选配置的自动生成器。

---

## 【技术要点】

1. **三步调优流程**:文档将 Auto-Tuning 抽象为三个核心步骤——①使用预留参数实现 kernel ②生成候选配置(手动枚举 / 组合遍历 / Carver 自动生成)③使用 `AutoTuner` 并行编译并 benchmark。
2. **预留参数设计**:kernel 函数签名上预留 6 个调优参数——`block_M`、`block_N`、`block_K`、`num_stages`、`thread_num`、`enable_rasteration`,运行时由外部配置注入,实现"一份代码多份实例化"。
3. **候选配置生成两路径**:①手动写死若干字典(原文给出两个示例配置);②用 `itertools.product` 对每个参数空间做笛卡尔积组合遍历,例如 `block_M∈[64,128,256]`、`block_N∈[64,128,256]`、`block_K∈[32,64]`、`num_stages∈[0,1,2,3]`、`thread_num∈[128,256]`、`enable_rasterization∈[True,False]`。
4. **AutoTuner 编译与基准**:通过 `AutoTuner.from_kernel(kernel=..., configs=...).set_compile_args(...)` 配置 JIT 编译选项(`out_idx=[-1]`、`supply_type=tl.TensorSupplyType.Integer`、`ref_prog=ref_program`、`skip_check=False`、`target="auto"`),以 `warmup=3, rep=20` 的方式运行并产出可立即调用的 `result.kernel(a, b)`。
5. **Carver 自动配置生成**:Carver 是面向 GPU/CPU/加速器的 tiling 策略生成与排序框架,提供 `MatmulTemplate` 等预置模板;通过 `with_arch(CUDA("cuda"))` 绑定架构后,以 `recommend_hints(topk=10)` 一次性返回 top-k 推荐配置。
6. **Carver hint 字段映射**:`MatmulTemplate` 输出的 hint 需映射到 tilelang 配置——`hint.rstep[0]` → `block_K`、`hint.pipeline_stage` → `num_stages`、`hint.rasterization_plan is not NoRasterization` → `enable_rasteration`、`thread_num = block_rows * block_cols * 32`(其中 32 为 warp 大小)。

---

## 【关键机制与数据】

**工作原理与数据流**(基于原文):

- **流程图谱**(原文):`kernel(预留参数) → 候选配置列表 configs → AutoTuner.from_kernel → set_compile_args → run(warmup=3, rep=20) → result.kernel(a, b)`
- **数据流**(原文):候选配置作为 dict 列表注入 AutoTuner,AutoTuner 负责把每份配置代入 kernel 签名进行实例化、编译、并以参考程序 `ref_program` 做正确性校验(若 `skip_check=False`),最终保留最优配置。
- **关键数字**(原文):
  - 手动示例 1:`block_M=128, block_N=128, block_K=128, num_stages=3, thread_num=128, enable_rasteration=True`
  - 手动示例 2:`block_M=32, block_N=32, block_K=32, num_stages=0, thread_num=32, enable_rasteration=False`
  - 组合遍历的搜索空间:`3 × 3 × 2 × 4 × 2 × 2 = 288` 个组合(基于原文中列出的每个列表长度)
  - Carver 推荐数:`topk=10`
  - 基准测试参数:`warmup=3, rep=20`
  - Carver 中 warp 大小常数:`32`(出现在 `block_rows * block_cols * 32`)
- **关键类型/类**(原文):`AutoTuner.from_kernel`、`tl.TensorSupplyType.Integer`、`CUDA("cuda")`、`MatmulTemplate`、`recommend_hints`、`NoRasterization`、`itertools.product`。
- **性能数据**:原文未给出具体的性能数字或加速比。

---

## 【表格解读】

**原文无表格。** 文档中所有结构化信息(参数名、候选值、配置示例)均以 Python 代码块(dict 字面量与列表字面量)形式呈现,而非 markdown 表格。

---

## 【公式解读】

**原文无公式。** 文档中未出现 LaTeX 形式或伪代码形式的数学公式。

唯一涉及的算术表达式出现在 Carver 部分:
- `thread_num = block_rows * block_cols * 32`
  - `block_rows`、`block_cols`:由 Carver hint 推导出的二维 tile 行列数(原文未给出具体值,仅给出乘积形式)
  - `32`:NVIDIA CUDA 架构中一个 warp 的线程数(原文未显式说明,但作为常数直接出现)
  - 作用:将 tile 的二维网格大小乘以 warp 大小,得到每 kernel 实例需要的总线程数。

文档中的"组合搜索空间"也未以数学式形式表达,仅通过 `itertools.product(...)` 的列表参数隐式表达。

---

## 【关联】

文档中显式提及的外部关联(无内部链接):

- **`examples/gemm/example_gemm.py`**:文档明示该教程是简化版,完整实现见此文件,代表 GEMM auto-tuning 的参考样例代码。
- **Carver 框架**:被定位为"轻量级 tiling 配置生成与排序框架",支持 GPU/CPU/加速器后端,覆盖矩阵乘法、elementwise、reduction-oriented 等常见算子。文档通过 `#using-carver-to-auto-generate-candidate-configurations` 的锚链接将 Step 2 的"手动枚举"与"Carver 自动生成"两个子路径关联起来。
- **`ref_program`(参考程序)**:作为正确性比对基准传入 `set_compile_args`,依赖用户自己提供(原文未展开定义)。
- **`AutoTuner` 与 `result.kernel`**:作为调优入口与产物出口,文档指出 `result.kernel(a, b)` 可直接被用户复用,即调优产物即最终可调用的优化 kernel。

---

## 【使用方法】

基于原文可提取的启用方式与配置项:

1. **kernel 实现阶段**:在 `def kernel(...)` 签名中预留 `block_M, block_N, block_K, num_stages, thread_num, enable_rasteration` 共 6 个参数(全部可设为 `None` 默认),并在内部以 `@T.prim_func` 装饰的 `main` 中使用这些参数。
2. **候选配置生成**:
   - 手动方式:直接写 `configs = [{"block_M": ..., ...}, ...]` 的 dict 列表。
   - 组合遍历方式:用 `itertools.product(block_M, block_N, block_K, num_stages, thread_num, enable_rasterization)` 一次性生成笛卡尔积,再封装为 dict 列表。
   - Carver 方式:`MatmulTemplate(M, N, K, in_dtype, out_dtype, accum_dtype).with_arch(CUDA("cuda")).recommend_hints(topk=10)`,然后遍历 `roller_hints` 把 `hint.rstep[0]`、`hint.pipeline_stage`、`hint.rasterization_plan`、`block_rows * block_cols * 32` 分别映射到 6 个预留参数。
3. **AutoTuner 调用**:
   ```python
   autotuner = AutoTuner.from_kernel(
       kernel=kernel,
       configs=get_configs(M, N, K, with_roller),  # 原文 with_roller 含义未展开
   ).set_compile_args(
       out_idx=[-1],
       supply_type=tl.TensorSupplyType.Integer,
       ref_prog=ref_program,
       skip_check=False,
       target="auto",
   )
   result = autotuner.run(warmup=3, rep=20)
   out_c = result.kernel(a, b)
   ```
4. **关键配置项含义**(原文给出名称,含义需结合代码上下文推断):
   - `out_idx=[-1]`:指定输出在参数列表中的索引。
   - `supply_type=tl.TensorSupplyType.Integer`:benchmark 时的张量供给类型。
   - `ref_prog=ref_program`:正确性参考实现。
   - `skip_check=False`:不跳过正确性校验。
   - `target="auto"`:目标后端自动选择。
   - `warmup=3, rep=20`:预热 3 次,重复测量 20 次。
5. **未涉及的配置项**(原文未涉及):CLI 启动方式、环境变量、配置文件路径、Carver 内部打分函数细节、`with_roller` 参数的具体语义等,均未在文档中说明。
