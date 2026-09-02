# MindStudio Ops Profiler Quick Start

> 仓 `msopprof` · 路径 `docs/en/quick_start/msopprof_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopprof/docs/en/quick_start/msopprof_quick_start.md

# msopprof 快速入门指南 · 一体化深度解读

---

## 【定位】

这篇文档解决的是 **基于 Ascend AI Processor 的算子性能瓶颈定位问题**：通过 msOpProf 工具采集算子在 NPU 上运行时产生的时序、带宽、流水等关键性能指标，并以 CSV/Bin 形式输出，再借助 MindStudio Insight 可视化，从而帮助开发者从"算子开发完成 → 性能是否达标"这一闭环中快速识别软件与硬件层面的优化空间。

---

## 【技术要点】

1. **前置依赖校验（Python）**：通过单行命令 `python3 -c "import ...; assert version.parse(numpy.__version__) <= version.parse('1.26.4')"` 一次性校验 `numpy / sympy / scipy / attrs / psutil / decorator` 的可用性，并对 `numpy` 做了**严格的上限版本约束（≤ 1.26.4）**，避免高版本 numpy 的 API 变化导致工具链异常。
2. **内核侧编译选项注入**：在 `op_kernel/CMakeLists.txt` 的第 1 行通过 `sed -i "1i\\add_ops_compile_options(ALL OPTIONS -g)"` 插入 `-g` 调试信息，是为了保留符号信息，使后续 profiler 能将性能数据回溯到源码热点。
3. **两条互补的采集通道**：
   - **板载硬件通路**：`msprof op --output=./msprof_output_npu ./execute_add_op`，在真实 NPU 上抓取"算子执行时间、流水占用、内存带宽、缓存行为"等难以在仿真器上高保真复现的真实硬件特征。
   - **模拟器通路**：`msprof op simulator --soc-version=Ascendxxxyy --output=./msprof_output_sim ./execute_add_op`，在不具备 NPU 硬件时使用仿真器完成"指令流追踪 + 代码热点定位"等更完整稳定的分析（需先通过外部链接获取 SoC 版本）。
4. **结果产物分层**：
   - `.csv`（如 `MemoryUB.csv`）：结构化数值数据，便于人工对照或外部脚本处理；
   - `.bin`（如 `visualize_data.bin`）：专供 MindStudio Insight 渲染热力图、缓存视图、算子代码热点图。
5. **可视化关闭回环**：通过 MindStudio Insight 的 **Import Data → Details** 入口完成 `.bin` 导入与多视图浏览；分析完成后，使用 `.orig.bak` 备份恢复原始 `CMakeLists.txt`，避免 `-g` 在生产构建中长期生效。
6. **"先用起来再读原理"的引导式流程**：文档刻意将 `2.3.3`（生成结果 → 看 CSV）、`2.3.4`（导入 Insight）排在原理段落之后，目的是让初学者先获得直观体验再回头理解 SoC/板载与仿真器差异（`2.3.2 NOTE`）。

---

## 【关键机制与数据】

**工作原理（原文整合还原）**：

- **触发面**：在算子代码不改、构建产物保留 `-g` 符号的前提下，对已经编译部署完成的 `AddCustom` 算子可执行文件 `./execute_add_op` 启动 `msprof`；
- **采集面**：根据是否拥有真实 NPU，选择 `msprof op`（板载）或 `msprof op simulator`（需 `--soc-version`）两种采集模式；
- **数据流**：`msprof` 输出的目录结构包含`.csv`（每类硬件指标一张）与`visualize_data.bin`（聚合后的可视化包），前者面向"表格分析"，后者面向"图形浏览"；
- **视图面**：`.bin` 被 MindStudio Insight 打开后，可呈现 **计算内存热力图 / 缓存热力图 / 算子代码热点图** 等多种视图；
- **收敛面**：分析完成、定位优化点后，恢复原有的 `CMakeLists.txt`（去除 `-g`），结束调试态。

**性能数据示例（原文：`MemoryUB.csv` 摘录与解读）**：任务被均分为 8 个块，全部调度到 Vector Core 执行。Block 0 的 read 带宽约 **1.02 GB/s**、write 带宽约 **0.51 GB/s**，而 Block 1 的 read 带宽仅约 **0.77 GB/s**、write 带宽约 **0.38 GB/s**——文档明确指出"差异过大则可能存在优化空间"，即通过块间带宽均衡度来判断是否存在数据布局、内存访问模式或任务切分上的非均衡。

---

## 【表格解读】

原文给出唯一一张数据表（MermoryUB.csv 字段示意），**逐字还原**如下：

| block_id | sub_block_id | aiv_time(us) | aiv_total_cycles | aiv_ub_read_bw_vector(GB/s) | aiv_ub_write_bw_vector(GB/s) |
|:--------:|:------------:|:------------:|:----------------:|:---------------------------:|:----------------------------:|
| 0 | vector0 | 7.456666 | 13422 | 1.023164 | 0.511582 |
| 1 | vector0 | 9.914444 | 17846 | 0.769523 | 0.384762 |
| 2 | vector0 | 10.001111 | 18002 | 0.762855 | 0.381427 |
| 3 | vector0 | 9.684444 | 17432 | 0.787799 | 0.393899 |
| 4 | vector0 | 0.782725 | 17545 | 0.782725 | 0.391363 |
| 5 | vector0 | 9.062222 | 16312 | 0.841890 | 0.420945 |
| 6 | vector0 | 9.293889 | 16729 | 0.820904 | 0.410452 |
| 7 | vector0 | 8.658889 | 15586 | 0.881105 | 0.440553 |

> 说明：上文按"原文 markdown 表结构"逐字保留列头与数值；注意原文 Block 4 行的第一列与第五列原文同时填为 `0.782725`（推为排版/示例拼接错误，正文解读仍按"`~0.78 GB/s` 量级"理解）。

**逐行解读**：

- **block_id = 0**：`aiv_time` 仅 7.46 us（最低），`aiv_total_cycles = 13422`（最低），read 带宽高达 **1.02 GB/s**——是 8 个块中执行最快、带宽最充裕的"短板"，说明该 block 访存模式最为对路。
- **block_id = 1**：相比 Block 0 时间延长约 33%（9.91 us vs 7.46 us）、cycles 升至 17846、read 带宽降至 **0.77 GB/s**——是文档明确点名的"非均衡示例"，提示开发者关注该 block 的访存模式或负载分配。
- **block_id = 2**：`aiv_time` 达到全表最大（10.001 us），是优化收口的关键候选块。
- **block_id = 3, 4, 5, 6, 7**：耗时落在 8.66–9.74 us 之间，带宽落在 0.78–0.88 GB/s 区间，整体呈"中间偏高、Block 0 / Block 7 偏快"的两端分布——可作为衡量"块间负载均衡"是否达标的对照基线。

**方法论**：通过该表可以同时观察"**时间维度（aiv_time / aiv_total_cycles）**"与"**带宽维度（UB read/write）**"两条线索；两者差异方向一致时（例如时间长的块带宽也低），可快速怀疑存在访存瓶颈或任务切分不均。

---

## 【公式解读】

**原文无公式**（文档以命令、表格与文字描述为主，未给出任何数学公式或 LaTeX 表达式）。

---

## 【关联】

- **上游前置文档**：本文档假设用户已先后完成两篇引导文档——
  1. *Ascend Operator Development Toolchain Quick Start*（完成 2.1 与 2.3 节的算子项目准备，提供 `~/ot_demo/workspace/src/AddCustom`、`execute_add_op` 等依赖）；
  2. *Ascend AI Operator Development Toolchain Learning Environment Installation Guide*（完成环境安装与 `workspace` 配置，作为 `msprof` 命令运行的前置）。
- **配套采集参数文档**：在使用模拟器通路前，需借助 *Chip SoC Type Acquisition Method* 获取 `--soc-version` 参数取值。
- **可视化下游**：`.bin` 数据的图形化浏览依赖两个 MindStudio Insight 文档：
  1. *MindStudio Insight 工具安装指南*（用于安装独立应用）；
  2. *MindStudio Insight 工具基础操作文档*（"Import Data → Details"流程、各类图表含义的官方释义）。
- **同仓库内关系**：本节归属于"quick_start"快速入门路径，强调"先体验、再原理"，与 `msot`（算子开发工具链）通过 OpTool + msOpProf 形成 "**开发 → 性能调优**"的串联闭环。

---

## 【使用方法】

- **启动环境校验**：`python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"`
- **开启调试编译**：进入 `~/ot_demo/workspace/src/AddCustom`，备份原 `op_kernel/CMakeLists.txt`，并在首行插入 `add_ops_compile_options(ALL OPTIONS -g)`
- **重编译并部署**：`bash ./build.sh`，随后定位本次产物 `custom_opp_*.run`，执行 `bash $MY_OP_PKG`
- **采集（板载 NPU）**：`cd ~/ot_demo/workspace/src/caller/build && msprof op --output=./msprof_output_npu ./execute_add_op`
- **采集（仿真器，需查询 SoC）**：`msprof op simulator --soc-version=Ascendxxxyy --output=./msprof_output_sim ./execute_add_op`
- **结果查看**：直接在 `--output` 目录查看 `.csv`；将 `visualize_data.bin` 通过 MindStudio Insight 的 **Import Data → Details** 入口导入浏览
- **还原环境**：使用 `.orig.bak` 覆盖被改动的 `op_kernel/CMakeLists.txt`，关闭调试信息

> 原文未涉及：自定义采集时间窗、采样率参数、回归式对比、性能阈值自动告警等更细粒度的开关（需进入 msOpProf 详细文档查阅）。
