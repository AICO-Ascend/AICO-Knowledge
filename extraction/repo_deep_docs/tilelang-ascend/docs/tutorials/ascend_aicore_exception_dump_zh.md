# TileLang-Ascend AI Core Exception Dump 技术白皮书

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/ascend_aicore_exception_dump_zh.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/ascend_aicore_exception_dump_zh.md

# TileLang-Ascend AI Core Exception Dump 文档一体化深度解读

---

## 【定位】

这篇文档描述并指导使用 TileLang-Ascend 在昇腾 NPU 上提供的 **AI Core 硬件异常现场自动 dump** 调试能力：当 kernel 因非法内存访问、MTE 错误、Cube/Vector 计算溢出等触发硬件异常时，自动捕获并保存 kernel 的输入张量数据，使开发者能够在事后恢复异常现场进行复现分析。

---

## 【技术要点】

1. **CANN 异常回调触发机制**：TileLang 在编译时将异常回调函数注册到 CANN 运行时；AI Core 异常发生时，CANN 异步调用该回调，并传入异常信息——整个过程无需手动介入。

2. **MAGIC 标记 + ParamSizeInfo 解耦设计**：编译时在 kernel 参数末尾附加 `ParamSizeInfo` 结构体，包含 8 字节 MAGIC 值 `0x474e414c454c4954`（ASCII "TILELANG"）、kernel name 和 tensor 元信息（字节数、设备地址、ACL 数据类型编码）；回调在 args buffer 中按 8 字节步长搜索 MAGIC 定位 ParamSizeInfo，从而与 kernel 具体参数布局解耦。

3. **`TL_ASCEND_EXCEPTION_DUMP` 编译配置开关**：默认 `False`，通过 TVM 标准 `PassContext` 机制（Python `pass_configs` → `PassContext.config` → Codegen 读取）传递；关闭时不生成任何相关代码，编译产物与未启用该特性时完全一致；开启后 kernel 签名会附加额外参数，改变编译产物 ABI。

4. **依赖 CANN >= 9.3.0 三个 API**：`aclrtSetExceptionInfoCallback`（注册回调）、`aclrtGetArgsFromExceptionInfo`（获取 kernel args）、`acldumpSaveExceptionInfo`（保存 tensor 数据）。

5. **双后端与 Kernel 级隔离**：同时覆盖 AscendC (`ascendc`) 与 PTO (`pto`) 两个 codegen 后端；dump 文件以 kernel name 为前缀，支持多 kernel 场景下的文件隔离。

6. **端到端 Python 解析封装**：`parse_exception_dump(dump_path, kernel_name, output_dir, wait_seconds)` 一站式完成查找 dump 文件 → 调用 CANN `msaicerr.py` → 读取 numpy 数组；`read_msaicerr_bin(file_path, dtype, shape, header_size)` 读取单个 `.bin` 文件为 `np.ndarray`。

---

## 【关键机制与数据】

### 工作流程

`原文:` kernel 执行 → AI Core 硬件异常 → CANN 调用已注册的异常回调 → 两路并行处理：
- 从异常信息中获取 kernel args buffer（device 内存）
- 回调函数在 Host 侧按 8 字节步长搜索 MAGIC 标记，定位 `ParamSizeInfo`

→ 构建 `acldumpTensorInfo` 数组（tensor 地址、大小、数据类型） → 调用 `acldumpSaveExceptionInfo(kernel_name, ...)` → 写入 `<ASCEND_DUMP_PATH>/extra-info/data-dump/<devId>/<kernel_name>.custom.<timestamp>` → 事后由 `msaicerr.py` 解析为 per-tensor `.bin` 文件 → `read_msaicerr_bin()` 输出 `np.ndarray`。

### 关键数值与路径

| 项 | 原文中数值/模式 |
|---|---|
| MAGIC 值 | `0x474e414c454c4954`（ASCII "TILELANG"），8 字节步长搜索 |
| Dump 文件路径模板 | `<ASCEND_DUMP_PATH>/extra-info/data-dump/<devId>/<kernel_name>.custom.<timestamp>` |
| 解析后 .bin 文件命名 | `<kernel_name>.custom.<timestamp>.<tensor_type>.<tensor_index>.<dtype>.bin` |
| CANN 最低版本 | 9.3.0 |
| 必需环境变量 | `ASCEND_DUMP_PATH`、`ASCEND_DUMP_SCENE`（值设为 `aic_err_brief_dump`） |
| 默认配置状态 | `TL_ASCEND_EXCEPTION_DUMP` 默认 `False` |

### 性能/开销数据

`原文:` 文档未提供任何定量性能数据（如 dump 时间开销、文件大小、回调延迟等），仅定性描述其"零侵入开关"特性。

---

## 【表格解读】

### 表格 1：适用场景（原文第 1 节）

| 场景 | 说明 |
|------|------|
| Kernel 调试 | 硬件异常后恢复输入张量，用于本地复现问题 |
| CI 自动化测试 | 测试用例中触发异常并验证 dump 数据与预期输入一致 |
| 生产环境排障 | 开启配置后部署，异常发生时自动落盘，无需复现 |

**解读**：原文明示了该特性的三类使用场景：开发阶段的本地复现、CI 流水线中验证异常时的 dump 数据正确性、生产环境的事后排障。三类场景对"自动落盘、零侵入"的要求逐级提高，但都依赖同一套 dump 文件机制。

---

### 表格 2：CANN API 依赖（原文第 3.1 节）

| API | 作用 |
|-----|------|
| `aclrtSetExceptionInfoCallback` | 注册异常回调 |
| `aclrtGetArgsFromExceptionInfo` | 从异常信息获取 kernel args |
| `acldumpSaveExceptionInfo` | 保存 tensor 数据到 dump 文件 |

**解读**：该表列出特性依赖的三个 CANN API。前两者属于异常回调生命周期（注册回调 + 从回调上下文中取 args），最后一个属于 dump 持久化阶段。CANN < 9.3.0 因不提供这些 API 而无法启用该特性，这也是文档严格标注"**CANN >= 9.3.0**"的原因。

---

### 表格 3：环境变量（原文第 3.2 节）

| 环境变量 | 必需 | 说明 |
|----------|------|------|
| `ASCEND_DUMP_PATH` | 是 | dump 文件根路径 |
| `ASCEND_DUMP_SCENE` | 是 | 设为 `aic_err_brief_dump` 启用异常 dump |
| `ASCEND_HOME_PATH` | 解析时 | 定位 CANN 的 `msaicerr.py` 工具 |

**解读**：前两者为运行期必需，必须在 `import torch` / ACL 初始化**之前**设置，否则 CANN 不会读到；`ASCEND_DUMP_SCENE` 作为功能开关（值为 `aic_err_brief_dump`），缺省则即使配置 `TL_ASCEND_EXCEPTION_DUMP=True` 也不会落盘；`ASCEND_DUMP_PATH` 缺省时 CANN 默认写当前工作目录（见原文 4.2 节末段补充说明）；`ASCEND_HOME_PATH` 仅在事后解析阶段用于定位 `msaicerr.py`。

---

### 表格 4：`parse_exception_dump()` 返回值字段（原文第 4.4 节）

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | `np.ndarray` | tensor 数据（1-D，需按实际 shape reshape） |
| `type` | `str` | `"input"` / `"output"` / `"workspace"` |
| `index` | `int` | 同类型 tensor 的序号 |
| `dtype` | `str` | 数据类型字符串，如 `"float16"` |
| `file` | `str` | `.bin` 文件路径 |

**解读**：返回值是 `list[dict]`，每个 dict 描述一个 tensor。`data` 为 1-D 数组（未携带 shape 信息），消费者需根据原始 kernel 调用语义手动 `reshape`；`type` 区分 input/output/workspace 三类，便于排查是哪个角色的 tensor 触发了异常；`index` 为同类型 tensor 的序号（如多个 input 时为 0、1、2…）；`file` 字段保留原始 `.bin` 路径，方便追溯。

---

### 表格 5：Python 配置键（原文第 6 节）

| API | 说明 |
|-----|------|
| `tilelang.PassConfigKey.TL_ASCEND_EXCEPTION_DUMP` | 配置键，值为 `"tl.ascend_exception_dump"`，默认 `False` |

**解读**：这是唯一用于开启该特性的 Python 配置项。值在源码层映射为字符串键 `"tl.ascend_exception_dump"`，沿 TVM `PassContext.config` 通道下沉到 codegen，控制是否条件化生成异常回调相关 C++ 代码。

---

### 表格 6：Python 工具函数（原文第 6 节）

| 函数 | 说明 |
|------|------|
| `parse_exception_dump(dump_path, kernel_name, output_dir, wait_seconds)` | 一站式解析：查找 dump 文件 → msaicerr 解析 → 读取 numpy 数组 |
| `read_msaicerr_bin(file_path, dtype, shape, header_size)` | 读取单个 `.bin` 文件为 numpy 数组 |

**解读**：两条工具函数构成解析层。"一站式"封装适合异常处理中快速恢复现场；`read_msaicerr_bin` 适合单文件粒度的精细分析（如已知具体路径想自定义 dtype/shape/header_size 时）。原文未列出 `output_dir`、`wait_seconds`、`header_size` 的具体默认值，需在源码中确认。

---

### 表格 7：CANN 环境变量（原文第 6 节）

| 环境变量 | 值 | 说明 |
|----------|-----|------|
| `ASCEND_DUMP_PATH` | 路径 | dump 文件根路径 |
| `ASCEND_DUMP_SCENE` | `aic_err_brief_dump` | 启用 AI Core 异常 dump |
| `ASCEND_HOME_PATH` | CANN 安装路径 | 定位 msaicerr.py 工具 |

**解读**：与表格 3 内容相同，作为速查参考再列一次，强调运行期（dump 生成）与解析期（msaicerr 定位）对环境变量的不同依赖。

---

## 【公式解读】

`原文无公式`。

文档中出现的关键标识符和路径模式（如下），不属于数学公式但属形式化定义：

1. **MAGIC 标识符**（原文 2.3 节）：`MAGIC = 0x474e414c454c4954`
   - 符号含义：8 字节常量，ASCII 编码后即 `"TILELANG"`。
   - 作用：在 kernel args buffer 中作为唯一哨兵，回调按 8 字节步长搜索该值以定位 `ParamSizeInfo` 结构体起点。

2. **Dump 文件路径模板**（原文 2.4 节）：`<ASCEND_DUMP_PATH>/extra-info/data-dump/<devId>/<kernel_name>.custom.<timestamp>`
   - 符号含义：`<ASCEND_DUMP_PATH>` 由 env 注入；`<devId>` 为昇腾设备 ID；`<kernel_name>` 由 `ParamSizeInfo` 中保存；`<timestamp>` 由 CANN 在 dump 时生成。
   - 作用：固定由 CANN 拼装，多 kernel 场景下以 kernel name 隔离互不覆盖。

3. **`.bin` 文件命名模板**（原文第 5 节）：`<kernel_name>.custom.<timestamp>.<tensor_type>.<tensor_index>.<dtype>.bin`
   - 符号含义：`tensor_type ∈ {input, output, workspace}`；`tensor_index` 为同类序号；`dtype` 为数据类型字符串。
   - 作用：经 msaicerr 解析后的 per-tensor 文件命名约定，与上表 4 的 `file`、`type`、`index`、`dtype` 字段一一对应。
   - 原文示例：`main_kernel.custom.20260731191027177.input.0.float16.bin` —— 表明 timestamp 在示例中可达 17 位（表示毫秒级时间）。

---

## 【关联】

原文未提供任何站内超链接或交叉引用（`内部链接: (无)`），仅在文本中提及以下关联项：

- **CANN 运行时**：异常回调注册与 dump 文件持久化均依赖 CANN 的 `acl/acl_rt.h`、`acl/acl_dump.h` 头与 API，特性属于 CANN 之上的一层封装。
- **TVM PassContext**：配置项 `TL_ASCEND_EXCEPTION_DUMP` 沿 TVM 标准的 `pass_configs → PassContext.config → Codegen` 链路传递，受 TVM 编译时配置机制约束。
- **双 codegen 后端**：同时服务 `ascendc`（AscendC）与 `pto`（PTO）两种昇腾代码生成路径，覆盖了 TileLang-Ascend 当前的 codegen 选项。
- **完整示例文件**：`examples/exception_dump_test/example_exception_dump.py` —— 文档将完整可运行代码指向该文件，而非内嵌长代码段。
- **CANN 工具 `msaicerr.py`**（位于 `$ASCEND_HOME_PATH/tools/msaicerr/msaicerr.py`）：与 TileLang 的 `parse_exception_dump()` / `read_msaicerr_bin()` 形成上下层关系——后者调用前者完成 dump 拆解，前者作为底层解析器由 CANN 提供。

---

## 【使用方法】

### 启用条件（原文涉及）

1. **CANN 版本**：>= **9.3.0**（必需，提供三个 ACL API）。
2. **环境变量**（需在 `import torch` / ACL 初始化之前设置）：
   - `ASCEND_DUMP_PATH`：dump 文件根路径（不设则默认当前工作目录）。
   - `ASCEND_DUMP_SCENE`：设为 `aic_err_brief_dump`，否则即使开启配置也不会落盘。
   - `ASCEND_HOME_PATH`：解析期用于定位 `msaicerr.py`。
3. **编译配置**：通过 `tilelang.jit` 或 `tilelang.compile` 的 `pass_configs` 传入 `tilelang.PassConfigKey.TL_ASCEND_EXCEPTION_DUMP: True`，默认 `False`。

### 启用步骤（原文涉及）

```python
# 步骤 1：先于 import torch 设置环境变量
import os
os.environ["ASCEND_DUMP_PATH"] = "/tmp/exc_dump"
os.environ["ASCEND_DUMP_SCENE"] = "aic_err_brief_dump"

import torch
import tilelang

# 步骤 2：通过 pass_configs 启用特性
@tilelang.jit(
    out_idx=[2],
    pass_configs={
        tilelang.PassConfigKey.TL_ASCEND_EXCEPTION_DUMP: True,
    },
)
def my_kernel(M, N, dtype="float16"):
    ...
```

### 解析 dump（原文涉及）

- **一站式 API**：在异常处理块中调用 `from tilelang.tools.ascend_exception_dump_bin import parse_exception_dump; tensors = parse_exception_dump(dump_path="/tmp/exc_dump", kernel_name="main_kernel")`，返回 `list[dict]`，每 dict 含 `data`(np.ndarray)、`type`、`index`、`dtype`、`file` 字段。
- **手动分步**：
  1. `python $ASCEND_HOME_PATH/tools/msaicerr/msaicerr.py -d <dump_file> -out /tmp/parsed` 解析为 per-tensor `.bin`。
  2. `from tilelang.tools.ascend_exception_dump_bin import read_msaicerr_bin; data = read_msaicerr_bin(<bin_path>, dtype=np.float16, shape=(128, 128))` 读为 numpy。

### 完整示例位置（原文涉及）

`examples/exception_dump_test/example_exception_dump.py`。
