# TileLang-Ascend AI Core Exception Dump Technical White Paper

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/ascend_aicore_exception_dump_en.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/ascend_aicore_exception_dump_en.md

# TileLang-Ascend AI Core Exception Dump 深度解读

---

## 【定位】

这篇文档描述了 TileLang-Ascend 中一项**自动捕获 AI Core 硬件异常时算子输入张量数据**的能力,通过 CANN 的异常回调机制实现异常现场的"事后取证",解决传统调试方法只能拿到硬件错误码、无法还原异常时刻输入张量实际数据的问题。

---

## 【技术要点】

1. **回调式自动捕获**:TileLang 在编译期向 CANN runtime 注册异常回调函数(`aclrtSetExceptionInfoCallback`),AI Core 异常发生时 CANN 自动异步触发,无需人工干预。
2. **MAGIC 标记定位 ParamSizeInfo**:编译期在 kernel 参数尾部追加 `ParamSizeInfo` 结构,首部为 8 字节 MAGIC 值 `0x474e414c454c4954`(即 ASCII "TILELANG"),回调以 8 字节步长在参数 buffer 中搜索该标记,实现回调代码与 kernel 参数布局完全解耦。
3. **Tensor 元信息结构**:ParamSizeInfo 包含 kernel 名称(作为 dump 文件前缀)、各 tensor 的字节大小、设备地址、ACL 数据类型码。
4. **依赖 CANN API**:需 `aclrtSetExceptionInfoCallback`、`aclrtGetArgsFromExceptionInfo`、`acldumpSaveExceptionInfo` 三个 API,要求 **CANN >= 9.3.0**。
5. **编译期配置开关**:`TL_ASCEND_EXCEPTION_DUMP` 通过 TVM `PassContext` 机制传播(Python `pass_configs` → `PassContext.config` → Codegen 读取),**默认关闭**;关闭时不生成任何相关代码,产物 ABI 与未启用时完全一致。
6. **双后端覆盖**:同时支持 `ascendc`(AscendC)与 `pto`(PTO)两种 codegen 后端。
7. **端到端工具链**:提供 `parse_exception_dump()` Python 接口,封装 dump 文件发现、调用 CANN `msaicerr.py`、读取 `.bin` 文件为 `np.ndarray` 的完整流程。
8. **环境变量强制要求**:`ASCEND_DUMP_PATH` 与 `ASCEND_DUMP_SCENE` 必须在 `import torch` / ACL 初始化**之前**设置,否则 CANN 不读取。
9. **默认关闭的三个原因**:① 依赖的 CANN API 在旧版本中可能不可用;② 启用会向 kernel 签名追加额外参数,改变 ABI;③ 异常回调注册会改变 CANN runtime 行为。

---

## 【关键机制与数据】

### 工作流程(原文 ASCII 图)
```
kernel execution ──→ AI Core hardware exception
                     │
                     ▼
   CANN invokes registered exception callback
                     │
   ┌─────────────────┴─────────────────┐
   │                                   │
Extract kernel args buffer    Callback searches for
from exception info           MAGIC marker on Host
(device memory)               to locate ParamSizeInfo
   │                                   │
   └───────────┬───────────────────────┘
               ▼
Build acldumpTensorInfo array
(tensor addresses, sizes, data types)
               │
               ▼
acldumpSaveExceptionInfo(kernel_name, ...)
               │
               ▼
<ASCEND_DUMP_PATH>/extra-info/data-dump/<devId>/
  <kernel_name>.custom.<timestamp>
               │
               ▼ Post-mortem parsing
msaicerr.py parses → per-tensor .bin files
               │
               ▼
read_msaicerr_bin() → np.ndarray
```

### 核心机制说明

- **异常回调机制**:回调由 CANN 在异常时自动触发,使用 `aclrtGetArgsFromExceptionInfo` 从异常信息中提取 kernel 参数 buffer(驻留于设备内存),拷贝到 host 后再解析。原文:"The callback uses CANN APIs to extract the kernel's argument buffer (in device memory) from the exception info, copies it to the host, and then parses it."
- **MAGIC 搜索与解耦**:回调并不预先知道 tensor 在参数 buffer 中的位置,因此以 8 字节为步长扫描 MAGIC 值;命中后即可从 ParamSizeInfo 读取全部 tensor 描述符。原文:"This approach fully decouples the callback code from the kernel's specific parameter layout."
- **Dump 文件路径**:`<ASCEND_DUMP_PATH>/extra-info/data-dump/<devId>/<kernel_name>.custom.<timestamp>`,每个 kernel 的文件以 kernel 名称前缀,避免多 kernel 干扰。
- **配置传播链路**:`pass_configs` → `PassContext.config` → Codegen 读取 → 条件生成 C++ 代码;关闭时不生成任何相关代码,产物与未启用时完全一致。

### 关键 MAGIC 常量(原文)
- **MAGIC 值**:`0x474e414c454c4954`,即 ASCII 字符串 "TILELANG",长度为 8 字节。

### 性能/数据维度信息
- 原文未提供性能数据(吞吐量、延迟、存储开销等),**无相关数字**。

---

## 【表格解读】

### 表 1:Use Cases(原文 §1)

| Scenario | Description |
|----------|-------------|
| Kernel debugging | Recover input tensors after a hardware exception for local issue reproduction |
| CI automated testing | Trigger exceptions in test cases and verify dump data matches expected inputs |
| Production troubleshooting | Deploy with the feature enabled; dumps are auto-saved on exception without reproduction |

**解读**:三类典型场景——(1) 本地调试时通过还原异常时的输入张量进行问题复现;(2) CI 自动化测试中主动触发异常并校验 dump 数据是否匹配预期输入(隐含回归测试意图);(3) 生产环境部署时开启功能,异常时自动落盘 dump 文件而无需重新复现。这覆盖了从开发、测试到生产的全生命周期。

---

### 表 2:CANN APIs(原文 §3.1)

| API | Purpose |
|-----|---------|
| `aclrtSetExceptionInfoCallback` | Register exception callback |
| `aclrtGetArgsFromExceptionInfo` | Extract kernel args from exception info |
| `acldumpSaveExceptionInfo` | Save tensor data to dump file |

**解读**:三个 CANN API 形成完整的"注册-提取-保存"链路——`aclrtSetExceptionInfoCallback` 负责注册回调(编译期调用),`aclrtGetArgsFromExceptionInfo` 在异常发生时从异常信息中抽取 kernel 参数 buffer,`acldumpSaveExceptionInfo` 将 tensor 数据写入 dump 文件。它们分别来自 `acl/acl_rt.h` 与 `acl/acl_dump.h`,是 CANN >= 9.3.0 的强制依赖。

---

### 表 3:Environment Variables(原文 §3.2)

| Variable | Required | Description |
|----------|----------|-------------|
| `ASCEND_DUMP_PATH` | Yes | Root path for dump files |
| `ASCEND_DUMP_SCENE` | Yes | Set to `aic_err_brief_dump` to enable exception dump |
| `ASCEND_HOME_PATH` | At parse time | Locates CANN's `msaicerr.py` tool |

**解读**:`ASCEND_DUMP_PATH` 是 dump 文件根目录(必填),`ASCEND_DUMP_SCENE` 设为 `aic_err_brief_dump` 才会触发异常 dump(必填),`ASCEND_HOME_PATH` 仅在解析阶段用于定位 `msaicerr.py`(非运行期必需)。**关键约束**:前两者必须早于 `import torch` / ACL 初始化设置,否则 CANN 不会读取这两个变量——这与 CANN 的初始化时机耦合。

---

### 表 4:Return Value of `parse_exception_dump()`(原文 §4.4)

| Field | Type | Description |
|-------|------|-------------|
| `data` | `np.ndarray` | Tensor data (1-D; reshape as needed) |
| `type` | `str` | `"input"` / `"output"` / `"workspace"` |
| `index` | `int` | Tensor index within its type group |
| `dtype` | `str` | Data type string, e.g. `"float16"` |
| `file` | `str` | Path to the `.bin` file |

**解读**:函数返回 `list[dict]`,每个 dict 描述一个 tensor:`data` 是 1 维 ndarray(原文明确提示"reshape as needed"),`type` 用三值字符串区分 input/output/workspace,`index` 是同类分组内的编号,`dtype` 为可读字符串,`file` 是该 tensor 对应的 `.bin` 文件路径(便于溯源)。**注意**:返回的 ndarray 是 1 维,使用者需要根据业务自行 reshape——这是一个明确的接口契约,可能给不熟悉此约定的使用者带来困惑。

---

## 【公式解读】

**原文无公式**。

(注:文中出现的 MAGIC 常量 `0x474e414c49454c54`/`TILELANG` 是数据常量而非数学公式;dump 路径模板 `<ASCEND_DUMP_PATH>/extra-info/data-dump/<devId>/<kernel_name>.custom.<timestamp>` 是路径模板而非公式,故本节判定为"原文无公式"。)

---

## 【关联】

### 上下游模块关系(基于文末/文中提及)

- **CANN runtime**:本特性完全建立在 CANN 异常回调 API(`aclrtSetExceptionInfoCallback` 等)之上,CANN 版本必须 >= 9.3.0。
- **TVM `PassContext`**:通过 TVM 的标准 `PassContext` 机制传播配置 `TL_ASCEND_EXCEPTION_DUMP`,说明该特性深度集成在 TVM 编译流水线中。
- **Codegen 后端**:同时覆盖 `ascendc`(AscendC)与 `pto`(PTO)两种 codegen 后端,与 TileLang-Ascend 的双后端架构紧密耦合。
- **CANN 工具链**:依赖 CANN 自带的 `msaicerr.py` 工具(位于 `$ASCEND_HOME_PATH/tools/msaicerr/`)进行 dump 文件解析。
- **Python 工具模块**:提供 `tilelang.tools.ascend_exception_dump_bin` 模块中的 `parse_exception_dump()` 函数,封装端到端解析流程。
- **`tilelang.PassConfigKey.TL_ASCEND_EXCEPTION_DUMP`**:作为 TVM `PassConfigKey` 枚举的一员被 `tilelang.jit` 装饰器与 `tilelang.compile` 消费,属于 TileLang 编译配置体系。

> 注:原文未提供内部链接列表,以上关联关系均基于文档中文字描述推断。

---

## 【使用方法】

### 启用方式

**Step 1 — 开启编译配置**(必须在编译时启用,默认关闭):

```python
import tilelang

@tilelang.jit(
    out_idx=[2],
    pass_configs={
        tilelang.PassConfigKey.TL_ASCEND_EXCEPTION_DUMP: True,
    },
)
def my_kernel(M, N, dtype="float16"):
    ...
```

也可在 `tilelang.compile` 中以相同方式传 `pass_configs`。

**Step 2 — 设置环境变量**(必须在 `import torch` 之前):

```python
import os
os.environ["ASCEND_DUMP_PATH"] = "/tmp/exc_dump"
os.environ["ASCEND_DUMP_SCENE"] = "aic_err_brief_dump"

import torch
import tilelang
```

> **关键点**:`ASCEND_DUMP_SCENE` 不设置则即使发生异常也不会写 dump;`ASCEND_DUMP_PATH` 不设置则默认当前工作目录。

**Step 3 — 捕获异常并解析 dump**:

```python
from tilelang.tools.ascend_exception_dump_bin import parse_exception_dump

try:
    result = kernel(a, b)
except Exception as e:
    print(f"AI Core exception: {e}")
    tensors = parse_exception_dump(
        dump_path="/tmp/exc_dump",
        kernel_name="main_kernel",
    )
    for t in tensors:
        data = t["data"]  # np.ndarray (1-D)
        print(f"  {t['type']}[{t['index']}] dtype={t['dtype']}, "
              f"shape={data.shape}, min={data.min():.4f}, max={data.max():.4f}")
```

### 手动解析(原文 §4.5,文档在末尾处被截断)

原文 §4.5 给出了手动调用 CANN `msaicerr.py` 的命令模板,但具体命令正文在 `python $ASCEND_HOME_PATH/tools/msaicerr/msaicerr.py \` 之后被截断(`原文:` 仅展示了 `python $ASCEND_HOME_PATH/tools/msaicerr/msaicerr.py -d /` 一行的开头,具体参数未完整呈现)。**原文未完整给出**手动解析命令的全部内容。

### 配置项汇总

| 类别 | 名称 | 取值/说明 |
|------|------|----------|
| 编译配置 | `TL_ASCEND_EXCEPTION_DUMP` | 布尔值,`True` 启用 / `False`(默认)关闭 |
| 环境变量 | `ASCEND_DUMP_PATH` | dump 文件根目录(必填) |
| 环境变量 | `ASCEND_DUMP_SCENE` | 取值 `aic_err_brief_dump`(必填) |
| 环境变量 | `ASCEND_HOME_PATH` | 定位 CANN `msaicerr.py`(解析时使用) |
| CANN 版本 | 最低 9.3.0 | 提供三个必需 API |
