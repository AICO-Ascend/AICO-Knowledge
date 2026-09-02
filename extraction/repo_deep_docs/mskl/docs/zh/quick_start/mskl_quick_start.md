# msKL 算子 Kernel 轻量化调用快速入门

> 仓 `mskl` · 路径 `docs/zh/quick_start/mskl_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mskl/docs/zh/quick_start/mskl_quick_start.md

# msKL 算子 Kernel 轻量化调用快速入门 — 一体化深度解读

## 【定位】

这篇文档解决"如何在 Python 脚本中**不依赖 ACLNN 框架**直接调用已编译好的自定义算子 Kernel（.o）与 Tiling 动态库（.so）"的问题，定位为面向初学者的 msKL 工具快速上手指南，以简易加法算子 AddCustom 为载体演示 Kernel 轻量化调用、验证链路与执行结果比对。

---

## 【技术要点】

1. **强制环境前提**：仅支持标准化 CANN 容器环境，依赖 `$ASCEND_HOME_PATH`、`$ATB_HOME_PATH` 环境变量，并通过 `[ -f /.dockerenv ]` 检测容器标识；自检脚本必须全部输出 `[PASS]` 才能继续。
2. **示例代码仓路径**：脚本默认工作路径为 `~/ot_demo/workspace/src/AddCustom`，并需存在 `~/ot_demo/msot/example/quick_start`（自检脚本要求）。
3. **核心接口 msKL.tiling_func**：传入 `op_type`、`inputs`、`outputs`、`lib_path`，返回带 `blockdim`（核函数启动数量）、`workspace`（工作空间内存）、`tiling_data`（序列化结构体）的 Tiling 输出。
4. **核心接口 msKL.get_kernel_from_binary**：通过 `.o` 文件路径直接加载 Kernel，输入/输出可直接使用 `numpy.array`，执行完即可读取输出做精度比对。
5. **示例算子规格**：张量形状 `(8, 4096)`、数据类型 `np.float16`、`NPU_ID=0`、输入通过 `np.random.randint(1, 5, TENSOR_SHAPE)` 随机生成；典型路径涉及 CANN 版本 `cann-8.5.0` 与 `ascend910b` 平台。
6. **工具启动方式**：通过工具命令启动脚本：`mskl python3 mskl_demo.py`；直接运行使用 `python3 mskl_demo.py`；若执行失败或卡住，可修改 `NPU_ID` 切换为其他可用 NPU 卡。

---

## 【关键机制与数据】

**调用流程（数据流，依据原文代码 main 函数）**：

1. **张量准备**：构造 `a`、`b`（随机整数 1–5，转 `np.float16`）、`c`（全零 `(8, 4096)` 张量），并预计算 `golden = (a + b).astype(TENSOR_DTYPE)` 作为比对基准。
2. **Tiling 调用**：`mskl.tiling_func(op_type="AddCustom", inputs=[a, b], outputs=[c], lib_path=TILING_LIB_PATH)` 返回 `tiling_output`，从中取出 `tiling_output.workspace` 与 `tiling_output.tiling_data`。
3. **Kernel 执行**：`add_custom(a, b, c, workspace, tiling_data)` 内部先 `mskl.get_kernel_from_binary(KERNEL_BINARY_PATH)` 获取 kernel 对象，再以 `device_id=NPU_ID` 调用。
4. **结果验证**：`np.array_equal(c, golden)`，输出 `compare success.` 或 `compare failed.`。

**原文执行日志示例**：

```text
[INFO ] Load tiling library /usr/local/Ascend/cann-8.5.0/opp/vendors/customize/op_impl/ai_core/tbe/op_tiling/lib/linux/aarch64/libcust_opmaster_rt2.0.so
[INFO ] Set kernel_type as vec, you can change this value by input [kernel_type] in [mskl.get_kernel_from_binary] manually.
compare success.
```

**原文：性能/规模数字**：
- 张量规模 `(8, 4096)` = **32,768** 元素（来自原文代码常量）。
- 输入随机数范围 **1–5**（来自原文 `np.random.randint(1, 5, ...)`）。
- 安装耗时 **约 3 分钟**（原文："外网可达环境下预计耗时：约 3 分钟"）。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

（文档给出的仅为 Python 代码与执行命令，未出现任何 LaTeX 或伪代码形式的数学公式。）

---

## 【关联】

文档虽未提供内部链接，但通过外链/引用描述了清晰的上下游依赖关系：

- **上游前置**：以《算子开发工具链快速入门》（`op_tool_quick_start.md`）及其 §2.3 节"开发构建算子工程 msopgen"为前提，依赖其产出的算子工程目录（`~/ot_demo/workspace/src/AddCustom`）以及编译产物 `.o` 与 `.so`。
- **环境前置**：依赖《昇腾 AI 算子开发工具链学习环境安装指南》（`installation_guide.md`）以完成 CANN 容器环境部署。
- **下游集成**：msKL 工具可与其他算子工具链通过 `mskl python3 mskl_demo.py` 命令无缝集成，无需接入完整 ACLNN 框架即可完成 Kernel 调用与验证。
- **平台关联**：示例路径显式指向 `ascend910b` 平台与 CANN `8.5.0` 版本，表明该工具链与 Ascend AI Core 系列硬件及对应 OPP 自定义算子包目录结构（`opp/vendors/customize/op_impl/ai_core/tbe/{kernel,op_tiling}`）耦合。

---

## 【使用方法】

**1. 环境准备（强制前置）**：
- 按 `installation_guide.md` 完成 CANN 容器安装（原文："约 3 分钟"）。
- 执行自检脚本，必须全部 `[PASS]`：
  - 检查 `/.dockerenv`、`$ASCEND_HOME_PATH`、`$ATB_HOME_PATH`。
  - 检查 `~/ot_demo/msot/example/quick_start` 存在。
- 配置环境变量：`source ${CANN安装路径}/set_env.sh`，设置 `$ASCEND_HOME_PATH`（原文明确要求）。

**2. 算子工程准备**：
- 按 `op_tool_quick_start.md` §2.3 操作完成算子工程生成与编译，产物落在 `~/ot_demo/workspace/src/AddCustom`。

**3. 创建/适配调用脚本**：
- 编辑 `~/ot_demo/workspace/src/AddCustom/mskl_demo.py`，定义：
  - `KERNEL_BINARY_PATH`：编译产物的 `.o` 路径。
  - `TILING_LIB_PATH`：Tiling `.so` 路径。
  - `TENSOR_SHAPE = (8, 4096)`、`TENSOR_DTYPE = np.float16`、`NPU_ID = 0`。
- 查询 `.o` 路径命令：`find $ASCEND_HOME_PATH -name *AddCustom*o`。
- 查询 `.so` 路径命令：`find $ASCEND_HOME_PATH -path */customize/* -name liboptiling.so`。

**4. 执行调用（必须在算子已部署到 CANN 之后）**：
- 直接执行：`python3 mskl_demo.py`。
- 通过 msKL 工具启动：`mskl python3 mskl_demo.py`。
- 期望日志包含 `Load tiling library ...` 与 `Set kernel_type as vec ...`，最终输出 `compare success.`。

**5. 排错建议（原文）**：
- 若执行失败或卡住，"可能是默认的0卡异常，可以尝试修改`mskl_demo.py`中的`NPU_ID`改用其他可用卡"。
- 可通过 `mskl.get_kernel_from_binary` 的 `kernel_type` 参数手动指定（例如从默认 `vec` 改为其他类型），以适配不同 Kernel 实现。

**6. 配置项（原文涉及）**：
| 配置/参数 | 取值/作用 | 出现位置 |
|---|---|---|
| `NPU_ID` | 默认 `0`，可改为其他可用 NPU 卡 | 脚本顶部常量 |
| `kernel_type` | 由 `get_kernel_from_binary` 接收，可手动覆盖默认 `vec` | 执行日志提示 |
| `$ASCEND_HOME_PATH` | 指向 CANN 安装路径，需 `source set_env.sh` 后生效 | 自检与 `find` 命令 |
