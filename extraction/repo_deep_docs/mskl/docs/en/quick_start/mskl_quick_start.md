# msKL Lightweight Kernel Call Quick Start

> 仓 `mskl` · 路径 `docs/en/quick_start/mskl_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mskl/docs/en/quick_start/mskl_quick_start.md

# msKL Quick Start 文档深度解读

## 【定位】

本文档解决"如何在 Python 脚本中跳过 ACLNN 框架, 以轻量级方式完成 Ascend 自定义算子的 Tiling 调用 + Kernel 二进制加载 + 执行验证"的问题, 帮助入门用户在前置教程(简单 AddCustom 加法算子)基础上快速体验 msKL 工具提升算子开发效率的能力。

---

## 【技术要点】

1. **msKL 三大核心接口机制**:
   - `mskl.tiling_func`: 通过指定 `.so` Tiling 动态库与 `op_type` 精确调用目标 Tiling 函数, 接受 `inputs`/`outputs`/`lib_path` 等参数, 在不依赖 ACLNN 框架的前提下构造 `TilingContext`, 返回 `blockdim` (核函数启动数量)、`workspace` (workspace 内存) 与序列化 `tiling_data`。
   - `mskl.get_kernel_from_binary`: 通过指定 `.o` 内核二进制文件与函数签名, 直接加载并调用 Kernel, 输入/输出以 `numpy.array` 形式传入, 调用后可立即读取输出 tensor 内容做精度比对。
   - **与工具链无缝集成**: 通过 `mskl python3 mskl_demo.py` 命令即可直接启动 mskl Python 脚本。

2. **Python 依赖包强约束** (原文): `numpy`、`sympy`、`scipy`、`attrs`、`psutil`、`decorator`, 且 `numpy.__version__ <= 1.26.4`; 校验命令输出 `All is OK` 即通过。

3. **运行时路径关键变量** (原文示例):
   - `KERNEL_BINARY_PATH` 指向 `/usr/local/Ascend/cann-8.5.0/.../AddCustom_ab1b6750d7f510985325b603cb06dc8b.o` (CANN 8.5.0)
   - `TILING_LIB_PATH` 指向 `/usr/local/Ascend/cann-8.5.0/.../op_tiling/liboptiling.so`
   - 实际路径以 `find $ASCEND_HOME_PATH -name *AddCustom*o` 与 `find $ASCEND_HOME_PATH -path */customize/* -name liboptiling.so` 命令获取。

4. **示例算子张量规格** (原文): `TENSOR_SHAPE = (8, 4096)`、`TENSOR_DTYPE = np.float16`、`NPU_ID = 0`; 输入数据通过 `np.random.randint(1, 5, ...)` 生成, golden 值由 `(a + b).astype(TENSOR_DTYPE)` 计算。

5. **执行三步流程** (原文示例脚本): ① `mskl.tiling_func(...)` 获取 tiling 策略与 workspace → ② `add_custom(a, b, c, workspace, tiling_data)` 执行 Kernel → ③ `np.array_equal(c, golden)` 校验结果, 输出 `compare success.` 或 `compare failed.`

---

## 【关键机制与数据】

msKL 的工作流遵循"上游 Tiling + 下游 Kernel"两阶段轻量调用模型:

1. **环境前置约束**: 原文明示"必须重做"Operator Tool Development Environment Setup Guide 中的步骤, 以保证"所有依赖组件、环境变量等"完整一致; Tiling 库加载时打印 `[INFO ] Load tiling library .../libcust_opmaster_rt2.0.so` (原文日志), 表明 msKL 会按需加载 CANN 提供的 Tiling 运行时库。

2. **Tiling 阶段**: 通过 `mskl.tiling_func(op_type="AddCustom", inputs=[a, b], outputs=[c], lib_path=TILING_LIB_PATH)` 拉起目标算子的 Tiling 动态库, 在库内部完成对输入/输出 shape、dtype 的解析, 输出三件套 (`tiling_output.workspace`、`tiling_output.tiling_data`、内部隐含的 `blockdim`) 供后续 Kernel 调用使用, 也可用于"tiling 逻辑验证" (原文)。

3. **Kernel 阶段**: `add_custom()` 函数调用 `mskl.get_kernel_from_binary(KERNEL_BINARY_PATH)` 加载 `.o` 文件获得 kernel 句柄, 随后以 `(a, b, c, workspace, tiling_data, device_id=NPU_ID)` 触发执行; 原文日志 `[INFO ] Set kernel_type as vec, you can change this value by input [kernel_type] in [mskl.get_kernel_from_binary] manually.` 表明该接口会自动设置默认 kernel 类型 (`vec`), 用户可通过 `kernel_type` 参数手动覆盖。

4. **正确性数据流**: 输入 `a`, `b` 为随机整数 (1~5) 生成的 float16, `c` 初始化为 `np.zeros`, `golden = (a + b).astype(TENSOR_DTYPE)`; Kernel 执行后通过 `np.array_equal` 严格比对, 原文样例输出 `compare success.`

5. **失败处置** (原文): 若执行失败或挂起, 默认 NPU 0 可能异常, 建议修改 `mskl_demo.py` 中的 `NPU_ID` 切换至其他可用 NPU。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

1. **[前置依赖] Ascend Operator Development Toolchain Quick Start**: 文档明确"假设读者已完成该工具链完整流程", 且要求完成其中 Section 2.1 与 Section 2.3 (原文 Section 2.2), 作为 msKL 演示的算子工程 (`AddCustom`) 与编译产物 (`.o`、`.so`) 来源。
2. **[环境配套] Operator Tool Development Environment Setup Guide**: 用于环境安装与工作区配置, 同时也是 Python 依赖包 (Section 2.1.1) 出错时的修复依据。
3. **[算子部署前置] CANN 部署**: Section 2.3.3 的 `> [!CAUTION]` 提示"调用前请确保算子已成功部署至 CANN, 否则会报错", 表明 msKL 是消费 CANN 已部署产物的轻量调用层, 与 CANN `opp` 目录下 `op_impl/ai_core/tbe/` 的 vendor 自定义算子目录结构直接耦合。
4. **[互补工具链] ACLNN 框架**: 原文 Section 2.3 开篇即说明 msKL 通过 `tiling_func` 与 `get_kernel_from_binary` "enabling lightweight Tiling invocation without relying on the ACLNN framework", 定位于 ACLNN 之外的旁路调用通道。

---

## 【使用方法】

1. **环境自检命令** (原文 Section 2.1.1):
   ```shell
   python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"
   ```

2. **进入算子工程目录并创建脚本** (原文 Section 2.3.1):
   ```shell
   cd ~/ot_demo/workspace/src/AddCustom
   vi mskl_demo.py
   ```

3. **定位编译产物真实路径** (原文 Section 2.3.2):
   ```shell
   find $ASCEND_HOME_PATH -name *AddCustom*o
   find $ASCEND_HOME_PATH -path */customize/* -name liboptiling.so
   ```
   将所得绝对路径分别回填到 `mskl_demo.py` 的 `KERNEL_BINARY_PATH` 与 `TILING_LIB_PATH`。

4. **脚本执行** (原文 Section 2.3.3):
   - 直接执行: `python3 mskl_demo.py`
   - 通过 mskl 工具启动 (原文 Section 2.3 介绍): `mskl python3 mskl_demo.py`
   - 成功标志日志: `compare success.`

5. **配置项** (原文示例脚本):
   - `TENSOR_SHAPE`、`TENSOR_DTYPE`: 调整输入张量形状与 dtype。
   - `NPU_ID`: 失败/挂起时切换 NPU 设备号。
   - `kernel_type` 参数 (原文日志提示): 在 `mskl.get_kernel_from_binary` 中可手动指定以覆盖默认 `vec` 类型。
