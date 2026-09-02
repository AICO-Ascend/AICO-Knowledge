# msPTI 快速入门

> 仓 `mspti` · 路径 `docs/zh/quick_start/mspti_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mspti/docs/zh/quick_start/mspti_quick_start.md

# msPTI 快速入门 — 一体化深度解读

## 【定位】

本文档是 msPTI（MindStudio Profiling Tools Interface）在昇腾 NPU 上的"零门槛"快速体验指南，目标是引导用户按 **安装工具 → 配置环境 → 运行样例** 的三步流程，验证 msPTI 已随 CANN 一同安装并可正常工作，为后续基于 msPTI 构建面向推理/训练场景的 NPU 性能分析工具打基础。

---

## 【技术要点】

1. **msPTI 的产品定位**：是华为昇腾 MindStudio 提供的「性能剖析 API 集合」，用于构建 NPU 应用级性能分析工具，覆盖 **推理和训练** 两种场景。
2. **集成与分发方式**：msPTI **已集成于 CANN 软件包中**（需安装 `Toolkit + ops` 包），因此单独升级或安装最新版本时才需走独立安装流程（参见《msPTI 工具安装指南》）。
3. **多语言支持**：提供 C/C++ API 与 Python API 两套接口，其中 Python API 要求 **Python 3.10+** 环境。
4. **可选依赖**：Python Monitor 样例额外依赖 **PyTorch + torch_npu** 框架。
5. **互斥约束**：msPTI **不可与其他性能数据采集工具同时使用**，否则会导致采集的数据丢失（明确写入"约束说明"章节）。
6. **样例入口固定路径**：基础 Activity API 样例固定位于 `${install_path}/tools/mspti/samples/mspti_activity/`，通过 `bash sample_run.sh` 一键运行。

---

## 【关键机制与数据】

**工作原理（基于原文推断的事实）：**
- msPTI 通过采集多类 Profiling 事件来刻画 NPU 上的运行时行为，样例输出中可见的事件类别包括：
  - **RUNTIME_API**：例如 `DevMalloc`、`MemCopySync`，每条记录携带 `start` 与 `end` 时间戳（精度为纳秒级，例如 `1775186328012443375`）。
  - **MEMORY**：记录 `operationType: ALLOCATION`、`memoryKind: MEMORY_DEVICE` 等内存分配信息。
  - **MEMCPY**：记录 `copyKind: HTOD`、传输字节数（如 `bytes: 32`）。
- 样例运行还会触发 **UserBufferRequest / UserBufferComplete** 流程，请求与释放用户态 buffer，从样例输出来看，buffer 中填入了 8 组 double 类型结果（如 `result[0] is: 1.200000` ~ `result[7] is: 10.600000`），表明采样过程可对自定义回调数据进行回传。

**性能数据：** 原文未给出 msPTI 自身的性能开销、采样率或吞吐量等量化指标，仅给出样例运行成功后的输出片段，故此处不展开。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **安装链路** → `../install_guide/mspti_install_guide.md`（《msPTI 工具安装指南》）：当用户需要单独升级或安装最新版本 msPTI 时，本文将其作为下游详细文档引用。
- **CANN 套件** → msPTI 以子模块形式集成在 CANN 中，其目录布局遵循 `${install_path}/tools/mspti/...` 规范，依赖 CANN 的 `set_env.sh` 完成环境变量配置，因此 msPTI 与 CANN 的 Toolkit、ops 包构成强依赖关系。
- **PyTorch / torch_npu**（可选）→ 仅为 Python Monitor 样例的前置依赖，对 C/C++ Activity API 样例无强制要求。
- **昇腾产品形态**（外部链接）→ 硬件环境章节指向《昇腾产品形态说明》用于确认服务器支持的 NPU 型号，是 msPTI 运行的前置硬件依据。
- **互斥关系** → msPTI 与"其他性能数据采集工具"存在互斥使用约束，这影响其与 Ascend 生态中其他 Profiler/Profiler-like 工具（例如系统级 profiler、第三方 trace 工具）共存时的方案选择。

---

## 【使用方法】

**1. 安装验证（已安装 CANN 时）：**
```bash
pip show mspti
```
若输出版本信息且无报错即表示安装成功。

**2. 配置 CANN 环境变量：**
```bash
source ${install_path}/set_env.sh
```
其中 `${install_path}` 示例为 `/usr/local/Ascend/cann`。

**3. 运行基础 Activity API 样例：**
```bash
cd ${install_path}/tools/mspti/samples/mspti_activity
bash sample_run.sh
```
运行成功后，终端会按事件类型依次打印 `UserBufferRequest` / `UserBufferComplete`、`RUNTIME_API`、`MEMORY`、`MEMCPY` 等 Profiling 记录。

**4. 单独升级 / 安装 msPTI：** 参见《msPTI 工具安装指南》（`../install_guide/mspti_install_guide.md`）。
