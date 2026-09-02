# 特性与调优配置

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/feature_menu.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/feature_menu.md

# 一体化深度解读：TorchNPU Inductor 特性菜单文档

---

## 【定位】

本文档是 TorchNPU（昇腾 PyTorch 适配插件）中 `torch_npu/_inductor` 模块的**特性与调优配置总索引页**，以菜单形式聚合了 Catlass、动态 shape、FXGraph 图优化、离散访存、自动 Tiling、分核/限核、CostModel 等九大特性域及其下属环境变量/调优开关的文档链接，为开发者提供一份"Inductor 后端在昇腾硬件上可调参数与功能开关"的导航地图。

---

## 【技术要点】

1. **目录层级为"特性域 → 子文档"两级**：一级菜单包括「环境变量列表」「Catlass」「动态shape」「FXGraph图优化」「离散访存」「自动Tiling优化」「分核/限核」「CostModel」「其他环境变量」共九大特性域，每个特性域下挂载"快速入门"或具体环境变量条目。

2. **Catlass 域包含 6 个子条目**：快速入门、`CATLASS_EPILOGUE_FUSION`、`TORCHINDUCTOR_CATLASS_ENABLED_OPS`、`TORCHINDUCTOR_MAX_AUTOTUNE`、`TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS`、`TORCHINDUCTOR_NPU_CATLASS_DIR`、`TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING`，是菜单中子条目最多的特性域。

3. **自动 Tiling 优化域聚焦并行/调度**：包含 `FASTAUTOTUNE`、`INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE`、`TORCHINDUCTOR_COMPILE_THREADS`、`TORCHNPU_PRECOMPILE_THREADS` 四个开关，分别对应快速 autotune、激进 autotune、编译线程数、预编译线程数。

4. **CostModel 域是性能预测组件**：含快速入门、`INDUCTOR_ASCEND_ENABLE_COSTMODEL`（开关）、`INDUCTOR_ASCEND_COSTMODEL_RATIO`（比率参数）。

5. **其他环境变量域聚合非分类开关**：包括 `ENABLE_INPLACE_BUFFERS`、`INDUCTOR_ASCEND_CHECK_ACCURACY`、`INDUCTOR_ASCEND_DUMP_FX_GRAPH`、`INDUCTOR_ASCEND_LOG_LEVEL`、`TORCHINDUCTOR_NDDMA` 共 5 项，涵盖 buffer 复用、精度校验、FX 图导出、日志级别、NDDMA 访存等杂项。

6. **FXGraph 图优化域含可关闭 pass 列表**：除快速入门外，暴露 `SHUT_DOWN_FX_PASS_LIST`，允许用户按需屏蔽特定 FX 优化 pass。

---

## 【关键机制与数据】

本文档为**纯索引/导航型文档**，不含任何性能数据、benchmark 结果或定量参数。其机制完全体现在目录组织上：

- **作用机制**：作为特性文档的根入口，递归索引 `torch_npu/_inductor/docs/feature/` 子树中所有 markdown 文档；用户从此页跳转进入具体特性文档查阅环境变量语义、默认值、适用场景。
- **数据流**：无（不涉及运行时数据流）。
- **性能数据**：原文未涉及。
- **量化参数**：原文未涉及任何具体数值、阈值或默认配置。

---

## 【表格解读】

原文无表格。

（原文是一份纯 markdown 嵌套无序列表形式的菜单文档，所有信息以列表条目和相对路径链接形式呈现。）

---

## 【公式解读】

原文无公式。

（文档仅由标题、列表项和相对路径链接构成，未包含任何 LaTeX 公式或伪代码表达式。）

---

## 【关联】

基于文末内部链接信息，本文档作为索引枢纽，与以下特性/模块存在层级引用关系：

| 上级特性域 | 下属子文档链接 | 关联主题 |
|---|---|---|
| 通用 | `./environment_variables_summary.md` | 全量环境变量汇总 |
| Catlass | `./catlass/catlass.md` | Catlass 主文档入口 |
| Catlass | `./catlass/overview.md` | Catlass 快速入门 |
| Catlass | `./catlass/CATLASS_EPILOGUE_FUSION.md` | Epilogue 融合开关 |
| Catlass | `./catlass/TORCHINDUCTOR_CATLASS_ENABLED_OPS.md` | 启用 Catlass 的算子集 |
| Catlass | `./catlass/TORCHINDUCTOR_MAX_AUTOTUNE.md` | 最大 autotune 主开关 |
| Catlass | `./catlass/TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS.md` | autotune GEMM 后端选择 |
| Catlass | `./catlass/TORCHINDUCTOR_NPU_CATLASS_DIR.md` | Catlass 库目录指定 |
| Catlass | `./catlass/TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING.md` | 用 profiling 做 do_bench |
| 动态 shape | `./dynamicshape/dynamicshape.md`、`./dynamicshape/shapehandling.md` | 动态 shape 处理 |
| FXGraph 图优化 | `./graph_optimization/SHUT_DOWN_FX_PASS_LIST.md` | FX pass 关闭列表 |
| 离散访存 | `./non_contiguous_accesses/INDUCTOR_INDIRECT_MEMORY_MODE.md` | 间接访存模式 |
| 自动 Tiling | `./tiling/FASTAUTOTUNE.md`、`INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE.md`、`TORCHINDUCTOR_COMPILE_THREADS.md`、`TORCHNPU_PRECOMPILE_THREADS.md` | 自动 tiling 与并行编译 |
| 分核/限核 | `./limit_core/limit_core.md` | 核心数限制 |
| CostModel | `./costmodel/INDUCTOR_ASCEND_ENABLE_COSTMODEL.md`、`INDUCTOR_ASCEND_COSTMODEL_RATIO.md` | 性能 cost 模型开关与比率 |
| 其他 | `./other/ENABLE_INPLACE_BUFFERS.md`、`INDUCTOR_ASCEND_CHECK_ACCURACY.md`、`INDUCTOR_ASCEND_DUMP_FX_GRAPH.md`、`INDUCTOR_ASCEND_LOG_LEVEL.md`、`TORCHINDUCTOR_NDDMA.md` | buffer 复用、精度校验、图导出、日志、NDDMA |

从组织结构可推断上下游关系：**Inductor 后端**是这些特性的统一承载层；**Catlass**、**CostModel**、**自动 Tiling** 都属于编译期优化策略；**动态 shape**、**离散访存** 属于输入/内存特征适配；**FXGraph 图优化**、**分核/限核** 属于图级与硬件资源调度；**其他环境变量** 则是横切式辅助开关（如精度、buffer、日志、dump）。

---

## 【使用方法】

本文档为导航页，**原文未涉及任何启用命令、配置项或 API 调用方式**。其"使用方式"即为：从此菜单点击进入对应特性文档，再依据各子文档中具体的环境变量（如 `TORCHINDUCTOR_MAX_AUTOTUNE`、`INDUCTOR_ASCEND_ENABLE_COSTMODEL`、`TORCHINDUCTOR_COMPILE_THREADS` 等）按需设置。

各环境变量的实际取值、默认值、生效范围均不在本文档内，需跳转至对应子文档查阅。
