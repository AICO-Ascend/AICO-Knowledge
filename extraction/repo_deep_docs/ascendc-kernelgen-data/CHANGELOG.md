# CHANGELOG

> 仓 `ascendc-kernelgen-data` · 路径 `CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendc-kernelgen-data/CHANGELOG.md

# NPU-KernelBench 1.0.0 Changelog 深度解读

---

## 【定位】

这篇文档定义了 **NPU-KernelBench 1.0.0** 首个正式版本的发布内容,描述了一个面向 Ascend NPU 的核函数 (kernel) 评测与基准测试框架,涵盖多语言支持、并行执行、断点续跑、反作弊检测以及配套算子数据集的整套能力。

---

## 【技术要点】

1. **六大模块化框架**: `cli` / `data` / `builder` / `evaluator` / `runner` / `report`,构成完整的评测流水线 (pipeline)。
2. **三语言核函数评测能力**: 支持 **PyTorch/torch_npu**、**Ascend C/CANN**、**Triton** 三种核函数语言的评测。
3. **双 CLI 命令**: `eval` (单算子评测) 与 `run-dataset` (批量数据集评测)。
4. **双 Runner 模式**: `persistent` (长驻 worker,默认) 与 `isolated` (进程隔离,完整 NPU 隔离)。
5. **断点续跑与并行**: 支持 `--resume` 断点续跑 (中断后从上次进度恢复),支持**多 NPU 并行执行**评测任务。
6. **work_dir 自包含可复现**: 评测完成后 `work_dir` 目录自包含,可独立复现 (通过 `cd work_dir && python eval.py`)。
7. **反作弊机制**: AST 静态扫描 + 内核签名一致性检查 + 输出缓存 / monkey-patching / 时钟异常等 reward hacking 检测。
8. **配套数据集**: `kernel_generator` 数据集,共 **85 个算子** (level1: 33, level2: 30, level3: 10, level4: 12),并提供 **11 个测试样例**(gelu, identity, matmul, vector_add_ascendc, gemm_bias_catlass, pixel_scale_clip_ascendc 等,含 CMake 构建变体)。

---

## 【关键机制与数据】

### 工作原理与数据流

根据原文描述,NPU-KernelBench 1.0.0 的工作流程可还原为以下层次:

1. **CLI 入口层**: 用户通过 `eval` 或 `run-dataset` 命令触发评测,CLI 模块解析参数并分发任务。
2. **数据层 (data)**: 加载 `kernel_generator` 数据集 (85 个算子,按 level1-level4 分级) 与 11 个测试样例。
3. **构建层 (builder)**: 根据算子需求,构建对应语言的核函数 (PyTorch/torch_npu、Ascend C/CANN、Triton),含 CMake 构建变体。
4. **执行层 (runner)**: 
   - `persistent` 模式下,worker 长驻进程,持续接收评测任务 (默认模式);
   - `isolated` 模式下,每个任务以独立进程运行,实现完整 NPU 隔离。
   - 支持多 NPU 并行执行。
5. **评测层 (evaluator)**: 运行核函数并采集结果,配合反作弊模块进行 AST 静态扫描、内核签名一致性检查,以及检测输出缓存、monkey-patching、时钟异常等 reward hacking 行为。
6. **报告层 (report)**: 生成评测结果,输出至 `work_dir`。该目录自包含,支持 `cd work_dir && python eval.py` 独立复现。
7. **断点续跑机制**: 通过 `--resume` 参数,中断后可从上次进度恢复,避免重复执行已完成任务。

### 关键数据 (原文)

- **算子总数**: 85 个
  - level1: 33 个
  - level2: 30 个
  - level3: 10 个
  - level4: 12 个
- **测试样例数**: 11 个 (含 gelu, identity, matmul, vector_add_ascendc, gemm_bias_catlass, pixel_scale_clip_ascendc 等,含 CMake 构建变体)
- **支持语言**: 3 种 (PyTorch/torch_npu, Ascend C/CANN, Triton)
- **Runner 模式**: 2 种 (persistent, isolated)

---

## 【表格解读】

**原文无表格**

---

## 【公式解读】

**原文无公式**

---

## 【关联】

根据原文内容,NPU-KernelBench 1.0.0 与以下特性/模块存在内部关联:

1. **AscendC 算子代码生成训练数据集**: NPU-KernelBench 作为评测框架,与 `ascendc-kernelgen-data` 仓库的训练数据集形成上下游关系 — 训练数据集提供算子样本,NPU-KernelBench 提供对这些生成核函数的评测能力,二者共同支撑"算子代码自动生成模型的训练与评估"这一总体目标。

2. **六模块内部依赖关系**:
   - `cli` → 调用 `runner` 启动任务
   - `data` → 为 `builder` 提供算子定义
   - `builder` → 为 `evaluator` 构建可执行核函数
   - `evaluator` → 调用 `runner` 执行核函数
   - `report` → 汇总 `evaluator` 输出生成报告

3. **反作弊模块与 evaluator 的关系**: 反作弊检测 (AST 扫描、签名检查、reward hacking 检测) 是 `evaluator` 的内嵌子能力,服务于"训练算子代码生成模型时防止 reward hacking"这一核心需求。

4. **work_dir 复现机制与报告模块**: `work_dir` 自包含特性由 `report` 模块保证,实现"一次评测,处处复现"的可重现研究 (reproducible research) 目标。

> 注: 原文未提供内部链接 (文末标注"内部链接: (无)"),以上关联均基于原文文本内容的语义推断。

---

## 【使用方法】

根据原文,可提取以下使用方式:

1. **CLI 单算子评测**:
   ```
   eval
   ```

2. **CLI 批量数据集评测**:
   ```
   run-dataset
   ```

3. **断点续跑**:
   ```
   --resume
   ```

4. **Runner 模式选择** (两种):
   - `persistent` (长驻 worker,默认)
   - `isolated` (进程隔离,完整 NPU 隔离)

5. **独立复现**:
   ```
   cd work_dir && python eval.py
   ```

6. **多 NPU 并行**: 原文仅提及"支持多 NPU 并行执行评测任务",未给出具体配置命令。**原文未涉及**具体的多 NPU 并行启用参数。

7. **数据集使用**: 加载 `kernel_generator` 数据集 (85 个算子,level1-level4 分级) 与 11 个测试样例 (gelu, identity, matmul, vector_add_ascendc, gemm_bias_catlass, pixel_scale_clip_ascendc 等)。

> 注: 原文未提供配置文件路径、环境变量设置、构建命令 (除 `python eval.py` 外) 等更详细的使用说明。
