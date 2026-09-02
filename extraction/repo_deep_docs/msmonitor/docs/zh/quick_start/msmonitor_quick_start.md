# msMonitor工具快速入门

> 仓 `msmonitor` · 路径 `docs/zh/quick_start/msmonitor_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmonitor/docs/zh/quick_start/msmonitor_quick_start.md

# msMonitor 工具快速入门 — 一体化深度解读

---

## 【定位】

本文档是 msMonitor（MindStudio-Monitor）一站式在线监控工具的**快速入门指南**，核心解决"如何在最短路径上对集群训练任务进行性能监测与瓶颈定位"的问题：通过"先用 npu-monitor 抓关键算子耗时 → 出现劣化再用 nputrace 做详细数据采集"的两段式工作流，给出一条端到端、可复现的最小操作链路。

---

## 【技术要点】

1. **两段式工作流（核心使用范式）**
   - **第一段**：使用 `npu-monitor` 功能获取关键算子耗时。
   - **第二段**：监测到关键算子耗时劣化后，使用 `nputrace` 采集详细性能数据做分析。

2. **前置依赖（原文要求）**：必须先完成 msMonitor 工具安装，参见《msMonitor 工具安装指南》。

3. **dynolog daemon 启动**（步骤 1）
   - 基础命令：`dynolog --certs-dir NO_CERTS --enable-ipc-monitor`
   - 可选参数：传入 `--metric_log_dir <路径>` 用于指定 TensorBoard 文件落盘路径。
   - 默认日志路径：`/var/log/dynolog.log`
   - 安全约束：`--certs-dir NO_CERTS` 仅用于测试环境，生产环境建议使用证书验证。

4. **msMonitor 环境变量配置**（步骤 2）：`export MSMONITOR_USE_DAEMON=1`

5. **msPTI 使能**（步骤 3）：通过 `LD_PRELOAD` 预加载 `libmspti.so`
   - 默认路径示例：`/usr/local/Ascend/cann/lib64/libmspti.so`
   - 通用形式：`<CANN Toolkit安装路径>/cann/lib64/libmspti.so`

6. **npu-monitor 触发**（步骤 5）—— 使用 `dyno` 命令行
   - 开启：`dyno --certs-dir NO_CERTS npu-monitor --npu-monitor-start --report-interval-s 30 --mspti-activity-kind Kernel`
   - 关闭：`dyno --certs-dir NO_CERTS npu-monitor --npu-monitor-stop`
   - 关键参数：`--report-interval-s 30`（上报周期 30s）、`--mspti-activity-kind Kernel`（上报数据类型为 Kernel）

7. **nputrace 触发**（步骤 6）—— 使用 `dyno` 命令行
   - 命令：`dyno --certs-dir NO_CERTS nputrace --start-step 10 --iterations 2 --activities CPU,NPU --analyse --data-simplification false --log-file /tmp/profile_data`
   - 关键参数语义：
     - `--start-step 10`：从第 10 个 step 开始采集
     - `--iterations 2`：采集 2 个 step
     - `--activities CPU,NPU`：采集框架、CANN 和 device 数据
     - `--analyse`：采集完后自动解析
     - `--data-simplification false`：解析完成不做数据精简
     - `--log-file /tmp/profile_data`：落盘路径
   - **强约束**：触发 nputrace 前必须先关闭 npu-monitor 功能。

8. **PyTorch 训练脚本示例**（步骤 4）—— `SimpleModel` 全连接网络
   - 网络结构：`Linear(64,128) → ReLU → Linear(128,64) → ReLU → Linear(64,10)`
   - 超参：`batch_size=32, num_steps=100, input_size=64, num_classes=10`
   - 优化器：`torch.optim.SGD`，学习率 `lr=0.01`
   - 损失函数：`nn.CrossEntropyLoss()`
   - 设备：`npu:0`（自动回退到 `cpu`）
   - **关键无侵入特性**：使用 PyTorch 原生优化器（`torch.optim.SGD`、`torch.optim.Adam`）时，msMonitor 可自动识别训练迭代边界，无需额外修改代码。

---

## 【关键机制与数据】

**数据流 / 工作原理（基于原文重建的因果链路）：**

1. **链路启动层**
   - `dynolog daemon`（IPC 监控使能）启动后作为后台常驻进程，承担"接收来自训练进程的运行时数据上报、并将数据落盘（默认 `/var/log/dynolog.log`，可选 TensorBoard 路径 `--metric_log_dir`）"的职责。
   - `MSMONITOR_USE_DAEMON=1` 环境变量使训练进程侧的 msMonitor 组件对接 daemon 通道。

2. **运行时插桩层**
   - 通过 `LD_PRELOAD` 预加载 CANN Toolkit 自带的 `libmspti.so`，在不改 PyTorch 用户代码的前提下对算子级调用进行插桩（这是 npu-monitor / nputrace 能够拿到 Kernel 级数据的前提）。
   - 原文："使用 PyTorch 原生优化器……msMonitor 可自动识别训练迭代边界，无需额外修改代码"——说明 msPTI + 原生优化器组合能自动捕获 step 边界，从而支持 `--start-step` / `--iterations` 这种 step 粒度的精确切片。

3. **第一阶段（轻量监测）**：npu-monitor
   - `dyno npu-monitor --npu-monitor-start` 触发后，daemon 以 `report-interval-s 30`（30 秒）为周期，将 `mspti-activity-kind Kernel` 类型的算子耗时数据周期性上报。
   - 此阶段仅做关键算子耗时的周期性概览，开销较小，适合长时间挂在训练任务上。

4. **第二阶段（详细分析）**：nputrace
   - 当第一阶段发现耗时劣化，使用 `dyno nputrace` 触发**离散步级**的详细 trace 采集。
   - 采集维度 `--activities CPU,NPU` 同时覆盖**框架侧（CPU/Python 侧调用栈）、CANN 层（算子下发/调度）、device 侧（NPU 硬件执行）**三层数据。
   - `--analyse` 使采集完成后自动解析 trace，省去手工调用解析工具的步骤；`--data-simplification false` 保留原始完整数据（不做精简），便于事后做精细归因。
   - **互斥约束（原文）**：必须先关闭 npu-monitor 才能触发 nputrace——说明二者共享同一套 msPTI 资源/上报通道，不能并发。

5. **性能数据**：原文未给出具体的算子耗时数字、带宽数字、加速比数字等性能基准——本文档仅为操作指南，不含量化性能数据。

---

## 【表格解读】

**原文无表格**。本文档所有信息都以"操作步骤 + 命令示例 + 注释"的形式给出，未出现参数表、性能对比表、配置项表等结构化表格。

---

## 【公式解读】

**原文无公式**。本文档为入门操作指南，未涉及任何数学公式、性能模型公式或伪代码公式。

---

## 【关联】

本文档作为快速入门，是 msMonitor 体系中的一个"枢纽型"文档，向外连接到以下四个功能/特性文档：

| 关联文档 | 关联方向 | 关联语义（原文出处） |
|---|---|---|
| `../install_guide/msmonitor_install_guide.md` | 前置依赖（上游） | 步骤"前置条件"明确："完成msMonitor工具安装，具体请参见《msMonitor工具安装指南》"——本文档的所有操作均以工具已正确安装为前提。 |
| `../user_guide/dynolog_instruct.md` | 横向配套 | 步骤 1 的 Note 注释引用："详情请参见 dynolog_instruct"——dynolog daemon 是 msMonitor 的 IPC 后台，本文只给启动命令，安全/证书/生产部署细节在该文档中。 |
| `../user_guide/npumonitor_instruct.md` | 横向配套 | 步骤 5 末尾引用："npu-monitor 功能详细介绍和采集结果说明请参见 npumonitor_instruct"——本文只演示开启/关闭命令与关键参数，详细数据字段、采集结果解读在该文档中。 |
| `../user_guide/nputrace_instruct.md` | 横向配套 | 步骤 6 末尾引用："nputrace 功能详细介绍和采集结果说明请参见 nputrace_instruct"——本文只给出一次最小可运行的 trace 采集命令，完整的 trace 解析、视图使用、性能分析方法在该文档中。 |

**整体关系图（基于原文表述）**：
- 上下游链路：安装指南 → （本文档快速入门） → 三个用户指南（dynolog / npu-monitor / nputrace 详解）。
- 功能耦合关系：dynolog daemon 是公共底座（步骤 1 + 步骤 2），npu-monitor 与 nputrace 是其上层的两个互斥业务入口（步骤 5 ↔ 步骤 6）。

---

## 【使用方法】

> 以下仅汇总**原文中明确出现**的启用方式 / 配置项 / 命令。

### A. 前置条件（原文步骤）
- 完成 msMonitor 工具安装（参见 msmonitor_install_guide.md）。

### B. dynolog daemon 启动（步骤 1）
```bash
# 基础模式（仅用于测试环境）
dynolog --certs-dir NO_CERTS --enable-ipc-monitor

# 启用 TensorBoard 落盘
dynolog --certs-dir NO_CERTS --enable-ipc-monitor --metric_log_dir /tmp/metric_log_dir
```
- daemon 默认日志：`/var/log/dynolog.log`
- 生产环境：必须使用证书验证，不可继续用 `NO_CERTS`。

### C. 环境变量（步骤 2 + 步骤 3）
```bash
export MSMONITOR_USE_DAEMON=1
export LD_PRELOAD=/usr/local/Ascend/cann/lib64/libmspti.so
```

### D. 训练任务启动（步骤 4）
```bash
python train.py
```
- 可使用原文提供的完整 PyTorch 脚本（SimpleModel 全连接网络，无需外部数据集）。
- 使用 `torch.optim.SGD` / `torch.optim.Adam` 等原生优化器时无需额外修改代码。

### E. npu-monitor 启用 / 停用（步骤 5）
```bash
# 开启：上报周期 30s，仅采集 Kernel 类型
dyno --certs-dir NO_CERTS npu-monitor --npu-monitor-start --report-interval-s 30 --mspti-activity-kind Kernel

# 关闭
dyno --certs-dir NO_CERTS npu-monitor --npu-monitor-stop
```

### F. nputrace 触发（步骤 6）
```bash
dyno --certs-dir NO_CERTS nputrace \
  --start-step 10 \
  --iterations 2 \
  --activities CPU,NPU \
  --analyse \
  --data-simplification false \
  --log-file /tmp/profile_data
```
- **强制约束**：触发 nputrace 前必须先执行 `npu-monitor --npu-monitor-stop`。
