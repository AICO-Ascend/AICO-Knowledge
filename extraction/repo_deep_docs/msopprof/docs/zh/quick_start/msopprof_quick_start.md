# msOpProf 算子性能调优工具快速入门

> 仓 `msopprof` · 路径 `docs/zh/quick_start/msopprof_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopprof/docs/zh/quick_start/msopprof_quick_start.md

# msOpProf 算子性能调优工具快速入门 — 深度解读

---

## 【定位】
本文档是 msOpProf 算子性能调优工具的入门指南，演示如何采集并分析运行在昇腾 AI 处理器上的算子关键性能指标（耗时、带宽、Cache 行为、内存访问等），帮助开发者快速定位软、硬件性能瓶颈，基于一个简易加法算子为例展开全流程实操。

---

## 【技术要点】

1. **强制前置环境**：仅支持标准化 CANN 容器环境，不兼容裸机、虚拟机或其他非标准容器；外网可达情况下安装约需 3 分钟，自检脚本须全部输出 `[PASS]` 才能继续。
2. **调试编译选项**：在 `op_kernel/CMakeLists.txt` 首行插入 `add_ops_compile_options(ALL OPTIONS -g)` 或 `npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g)`，开启调试信息以支持后续性能采集。
3. **两种采集模式**：
   - 上板：`msopprof --output=./msopprof_output_npu ./execute_add_op`，捕获真实硬件耗时、Pipe 使用、内存带宽、Cache 行为；
   - 仿真：`msopprof simulator --soc-version=Ascendxxxyy --output=./msopprof_output_sim ./execute_add_op`，擅长指令流追踪与代码热点定位，但硬件相关行为模拟精度有限。
4. **输出产物**：在 `--output` 目录下生成 `.csv` 与 `.bin` 两类文件；`.csv` 用于表格化指标查看（如 `MemoryUB.csv`），`.bin` 用于 MindStudio Insight 图形化分析。
5. **SOC 版本获取**：`--soc-version` 参数值通过 `python3 -c "import acl; print(acl.get_soc_name())"` 命令获取，`xxxyy` 为用户实际使用的具体芯片类型代号。
6. **可视化工具**：通过 MindStudio Insight 导入 `visualize_data.bin` 文件，可在 Details 页面查看计算内存热力图、Cache 热力图、算子代码热点图等图形化视图。

---

## 【关键机制与数据】

**工作原理**：
- msOpProf 通过插入 `-g` 调试编译选项，使算子 Kernel 携带可供剖析的调试符号/插桩点，从而在运行期由运行时工具（`msopprof` 命令）拉取硬件计数器与 Pipe 状态信息，落地为 `.csv`（结构化指标）和 `.bin`（可视化所需的原始事件流）两类产物。
- 上板与仿真两条采集路径互补：上板路径依赖真实 NPU 卡的硬件 PMU/Pipe 事件，因此对内存延迟与带宽瓶颈的刻画高保真；仿真路径基于指令模拟器，事件流完整稳定，适合做代码热点定位与指令流追踪。

**数据流**（按文中顺序）：
`修改 CMakeLists.txt（加 -g）→ bash ./build.sh 编译 → bash $MY_OP_PKG 安装 → 切换到 caller/build 目录 → 执行 msopprof 命令 → 在 ./msopprof_output_xxx 下生成 .csv / .bin → csv 直接查看 / bin 用 MindStudio Insight 打开 → 恢复 CMakeLists.txt.bak`。

**性能数据（原文示例）**：
- 原文:`MemoryUB.csv` 中加法算子任务被均分为 **8 个 block**，全部调度至 **Vector Core** 执行（即 `sub_block_id` 均为 `vector0`）。
- 原文:Block 0 的 `aiv_ub_read_bw_vector` 为 **1.023164 GB/s**，Block 1 为 **0.769523 GB/s**，原文指出"如果差异过大，可能提示有优化空间"。
- 原文:各 block 的 `aiv_time(us)` 介于 **7.456666 ~ 10.001111** 之间，`aiv_total_cycles` 介于 **13422 ~ 18002** 之间。
- 原文:读写带宽大致呈 **1:0.5** 比例（例如 Block 0 读 1.023164 / 写 0.511582 GB/s），与加法算子的"读两端 + 写一端"的数据访问特征一致。

---

## 【表格解读】

**原文表格还原**（逐字）：

| block_id | sub_block_id | aiv_time(us) | aiv_total_cycles | aiv_ub_read_bw_vector(GB/s) | aiv_ub_write_bw_vector(GB/s) |
|:--------:|:------------:|:------------:|:----------------:|:---------------------------:|:----------------------------:|
| 0 | vector0 | 7.456666 | 13422 | 1.023164 | 0.511582 |
| 1 | vector0 | 9.914444 | 17846 | 0.769523 | 0.384762 |
| 2 | vector0 | 10.001111 | 18002 | 0.762855 | 0.381427 |
| 3 | vector0 | 9.684444 | 17432 | 0.787799 | 0.393899 |
| 4 | vector0 | 9.747222 | 17545 | 0.782725 | 0.391363 |
| 5 | vector0 | 9.062222 | 16312 | 0.84189 | 0.420945 |
| 6 | vector0 | 9.293889 | 16729 | 0.820904 | 0.410452 |
| 7 | vector0 | 8.658889 | 15586 | 0.881105 | 0.440553 |

**逐行解读**：
- `block_id`：任务被均分为 8 个 block（编号 0–7），代表算子在不同 Vector 计算单元上的并行分片。
- `sub_block_id`：全部为 `vector0`，说明 8 个 block 均被调度到 Vector Core（向量计算单元），未走 Cube 等其他子块，加法算子属典型 Vector 任务。
- `aiv_time(us)`：各 block 的 AI Vector 耗时（微秒），范围 7.46–10.00，Block 0 最快、Block 2 最慢，最高与最低相差约 2.54 µs。
- `aiv_total_cycles`：对应的总周期数（13422–18002），与 `aiv_time(us)` 单调一致，可用于跨频率平台归一化对比。
- `aiv_ub_read_bw_vector(GB/s)`：Vector 单元读取 Unified Buffer（UB）的实测带宽，范围 0.76–1.02 GB/s，Block 0 显著领先（约为 Block 1 的 1.33 倍）。
- `aiv_ub_write_bw_vector(GB/s)`：Vector 单元写入 UB 的实测带宽，范围 0.38–0.51 GB/s，每行约为对应读带宽的一半左右，与加法算子"读 a、读 b、写 c"的访存模式吻合。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

依据原文的链接与上下文，本文与其他模块的关系如下：

1. **前置依赖链**：
   - 《昇腾 AI 算子开发工具链学习环境安装指南》(`installation_guide.md`)：提供 CANN 容器环境，是 msOpProf 采集得以运行的基础。
   - 《算子开发工具链快速入门》(`op_tool_quick_start.md`) 的 2.3 节（`msopgen`）：产出 `AddCustom` 算子工程（`~/ot_demo/workspace/src/AddCustom`）与 caller 可执行文件（`~/ot_demo/workspace/src/caller/build/execute_add_op`），是本文的操作对象。
2. **下游可视化**：与 MindStudio Insight 工具协同——`.csv` 直接打开读指标，`.bin` 通过 MindStudio Insight 的 Import Data → Details 页面渲染为热力图与代码热点图；详细图表含义参考 `mindstudio_insight/user_guide/basic_operations.md`。
3. **目录结构参考（文末内部链接）**：`../user_guide/msopprof_simulator_user_guide.md#目录结构参考`：解释 msopprof 在 `--output` 目录下产出的 `.csv` / `.bin` 文件组织方式，是仿真器采集结果的官方目录约定，与本指南第 2.3.3 节"查看性能数据结果"直接对应。

---

## 【使用方法】

**启用方式（按原文步骤复述）**：

1. **环境准备**（强制前置）：
   - 按 `installation_guide.md` 完成 CANN 容器安装；
   - 在终端执行 §2.1.2 自检脚本，确认两条均输出 `[PASS]`（容器环境变量 `$ASCEND_HOME_PATH`、`$ATB_HOME_PATH` 须非空，且 `~/ot_demo/msot/example/quick_start` 目录须存在）。

2. **算子工程准备**（前提）：
   - 按 `op_tool_quick_start.md` 2.3 节完成 `AddCustom` 算子工程的构建，确保 `~/ot_demo/workspace/src/AddCustom` 与 `~/ot_demo/workspace/src/caller/build/execute_add_op` 可用。

3. **开启调试编译选项**（配置项）：
   ```shell
   cd ~/ot_demo/workspace/src/AddCustom
   cp -f op_kernel/CMakeLists.txt op_kernel/CMakeLists.txt.bak
   printf '%s\n' "if(COMMAND add_ops_compile_options)" \
     "  add_ops_compile_options(ALL OPTIONS -g)" \
     "elseif(COMMAND npu_op_kernel_options)" \
     "  npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g)" \
     "endif()" | cat - op_kernel/CMakeLists.txt > tmp && mv -f tmp op_kernel/CMakeLists.txt
   ```

4. **重新编译部署**：
   ```shell
   bash ./build.sh
   MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
   ```

5. **上板性能采集**（命令）：
   ```shell
   cd ~/ot_demo/workspace/src/caller/build
   msopprof --output=./msopprof_output_npu ./execute_add_op
   ```

6. **仿真器性能采集**（命令；`xxxyy` 通过 `python3 -c "import acl; print(acl.get_soc_name())"` 替换）：
   ```shell
   msopprof simulator --soc-version=Ascendxxxyy --output=./msopprof_output_sim ./execute_add_op
   ```

7. **查看结果**：
   - 直接打开 `./msopprof_output_xxx/MemoryUB.csv` 等 `.csv` 文件比对各 block 的耗时与 UB 读写带宽；
   - 在 MindStudio Insight 中点左上角 `Import Data` 导入 `visualize_data.bin`，进入 `Details` 页面查看热力图与代码热点。

8. **收尾恢复**（原文命令）：
   ```shell
   cd ~/ot_demo/workspace/src/AddCustom
   cp -f op_kernel/CMakeLists.txt.bak op_kernel/CMakeLists.txt
   ```

> 注：原文未涉及更多配置项（如采样率、过滤规则、白名单算子等高级参数）的设置方法，相关说明需参阅 `../user_guide/msopprof_simulator_user_guide.md#目录结构参考` 及 MindStudio Insight 官方文档。
