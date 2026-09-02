# 版本说明

> 仓 `release-management` · 路径 `MindStudio/26.1.0/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/release-management/MindStudio/26.1.0/release_notes.md

# MindStudio 26.1.0 Release Notes 深度解读

## 【定位】
本篇文档是 MindStudio 26.1.0 分支的版本说明(changelog),对外明确该版本相对上一代的配套栈版本号(CANN 9.1.0 / TorchNPU 26.1.0 / Ascend HDK 26.1.0)、跨版本兼容性矩阵,以及对内逐条罗列训练工具链、推理工具链、算子开发工具链(msKPP / msOpGen / msDebug / msSanitizer / msOpProf / msKL / msTX / msProf)的新增/变更特性,用于支撑版本发布管控与下游使用方适配决策。

---

## 【技术要点】

1. **三段式工具链升级定位**(原文第 1 节):围绕「训练开发工具 / 推理开发工具 / 算子开发工具」三大方向,分别针对大模型训练多核调度失衡、强化学习训推不一致、HostBound 瓶颈、推理量化调优、昇腾 950 算子调试等痛点,给出能力升级矩阵。
2. **配套版本同步升级**:当前 26.1.x 分支默认配套 CANN 9.1.0、TorchNPU 26.1.0、Ascend HDK 26.1.0(三者版本号完全对齐为 26.1.0/9.1.0)。
3. **向下兼容的版本矩阵**:MindStudio 26.1.x 仍兼容 CANN 8.5.0 / 9.0.0、TorchNPU 2.3.0 / 26.0.0、Ascend HDK 25.5.x / 26.0.RC1 / 25.7.RC1 等历史版本,呈"老 MindStudio 对新组件不兼容、老组件对新 MindStudio 兼容"的不对称矩阵。
4. **检测类工具的命令行参数体系**:msSanitizer 通过多个独立开关参数控制检测项——`--check-dcci=yes`(DCCI 缺失)、`--check-cross-npu-races=yes`(卡间竞争)、`--check-level`(读写权限)、`--padding`(GM 安全区大小)、`--log-level`(日志),形成可组合的检测策略。
5. **统一构建与 CI 适配**:msKPP、msOpGen、msDebug、msSanitizer、msOpProf、msKL、msTX 七个工具均完成「统一构建入口脚本 + 新型统一构建镜像 + CMake 4.x 适配」的同步升级;CI 构建流程支持基于 Tag 指定发布包版本号。
6. **不兼容变更提示**:msOpGen 将 whl 包安装方式由传统的 `pip install` 改为 `entry_points` 方式,以解决 `pip uninstall` 残留文件问题;同时 `msopst.ini` 配置文件位置由旧路径调整到标准配置目录,依赖旧路径的自定义脚本需同步适配。

---

## 【关键机制与数据】

- **DCCI 缺失检测机制**(原文,msSanitizer 章节):通过命令行参数 `--check-dcci=yes` 启用,自动识别算子中遗漏的 `dcci` 指令;开启 DCCI 检测时**自动关闭指令过滤与竞争检测功能**以消除干扰。
- **跨 NPU 卡间竞争检测机制**(原文,msSanitizer 章节):通过 `--check-cross-npu-races=yes` 启用,感知共享内存场景下的数据竞争,支持 `msTX` 软同步语义(`barrier` / `signal`),覆盖卡间通信中的数据竞争分析。
- **SIMT 架构检测补齐**(原文,msSanitizer 章节):未初始化检测通过指令重放增强精度;支持多个 `simt_vf` 函数竞争分析、`simt` 与 `main_scalar` 间 UB 竞争识别、`sync_threads` 未配对检测;新增 `simt_call` / `simt_start` / `simt_end` 桩函数并提供调用栈。
- **GM Buffer 安全区机制**(原文,msSanitizer 章节):在 Global Memory buffer 尾部增加安全保护区,识别越过 buffer 边界的写入行为,覆盖 Tiling 下沉 AICPU 等典型越界写场景;通过 `--padding` 参数控制安全区大小。
- **msDebug 断点自动识别**(原文,msDebug 章节):MI 接口新增断点位置是否处于 SIMT 区域的判断信息,调试器据此自动区分软断点 / 硬断点,支持 `simd_vf` 场景的断点设置并按断点位置自动判断应下发软断点还是硬断点。
- **msOpProf 指令级流水图**(原文,msOpProf 章节):在昇腾 950PR/DT 芯片上采集并生成指令级流水图(Pipeline Timeline),可视化各指令在不同流水阶段的执行时序;SIMT 算子支持 warp 维度流水图,并新增 Top Stall Reason 自动归因分析。
- **内存热力图多方向带宽采集**(原文,msOpProf 章节):通过动态插桩细化指令级搬运通路,补充 `UB→GM`、`Dcache→GM`、`UB→L1`、`L1→UB` 等多方向内存带宽数据。
- **msTX 与 msSanitizer 联动**(原文,msTX 章节):msTX 新增内存属性指定 API,显式标记某段内存区域的读写属性(只读/只写/读写),辅助 msSanitizer 精确区分合法访问与异常访问、降低误报;另新增 `TORCH_NPU_REPORT_MEM_ACCESS` 宏,配合 Ascend PyTorch Profiler 的 `mstx=True` 采集模式实现精细内存行为分析。
- **msOpGen 安装方式重构**(原文,msOpGen 章节):将 whl 包安装方式由 `pip install` 改为 `entry_points`,解决 `pip uninstall` 卸载后残留文件问题;同时去除安装过程中的软链接校验、文件属主校验及路径长度限制。
- **昇腾 950PR/DT 上板调试能力**(原文,msDebug 章节):支持软硬断点设置与恢复、内存/变量/寄存器展示、单步调试(step over / step in)、中断运行、多核切换、线程切换;支持 coredump 解析(调用栈回溯、错误寄存器展示、线程切换),并自动获取 core 文件中的 kernel object 以辅助符号解析。

---

## 【表格解读】

### 表 1:版本配套说明(原文第 2 节)

| MindStudio分支 | CANN版本 | TorchNPU版本 | Ascend HDK |
| ---- | ---- | ---- | ---- |
| 26.1.x | 9.1.0 | 26.1.0 | 26.1.0 |

**解读**:本表给出 26.1.x 分支的官方默认配套栈:底层 CANN 9.1.0、上层 TorchNPU 26.1.0、驱动/固件层 Ascend HDK 26.1.0。三层版本号语义上完全对齐(均为 26.1.0 主版本或对应 9.1.0),表示该分支是 MindStudio、框架、芯片驱动三层同步迭代的版本节点。

---

### 表 2:CANN 兼容性矩阵(原文第 3 节)

| MindStudio | CANN 8.5.0 | CANN 9.0.0 | CANN 9.1.0 |
| ---- | ---- | ---- | ---- |
| 8.3.x | Y | / | / |
| 26.0.x | Y | Y | / |
| 26.1.x | Y | Y | Y |

**解读**:矩阵揭示一条规律——**MindStudio 始终向下兼容旧 CANN,但新 CANN 不向下兼容旧 MindStudio**。8.3.x 仅能用 CANN 8.5.0;26.0.x 兼容 8.5.0 与 9.0.0;26.1.x 三档 CANN 全部兼容。意味着升级 MindStudio 不会强制升级 CANN,但若希望使用 CANN 9.1.0,必须使用 26.1.x。

---

### 表 3:TorchNPU 兼容性矩阵(原文第 3 节)

| MindStudio | TorchNPU 2.3.0 | TorchNPU 26.0.0 | TorchNPU 26.1.0 |
| ---- | ---- | ---- | ---- |
| 8.3.x | Y | / | / |
| 26.0.x | Y | Y | / |
| 26.1.x | Y | Y | Y |

**解读**:与 CANN 矩阵结构完全一致——TorchNPU 2.3.0 是 8.3.x/26.0.x/26.1.x 三档 MindStudio 都能用的「最老」版本;TorchNPU 26.1.0 仅 26.1.x 支持。TorchNPU 版本号体系从 2.x 跳到 26.x,与 MindStudio 主版本号对齐,暗示二者同节奏发版。

---

### 表 4:Ascend HDK 兼容性矩阵(原文第 3 节)

| MindStudio | Ascend HDK 25.5.x | Ascend HDK 26.0.RC1 / 25.7.RC1 | Ascend HDK 26.1.0 |
| ---- | ---- | ---- | ---- |
| 8.3.x | Y | / | / |
| 26.0.x | Y | Y | / |
| 26.1.x | Y | Y | Y |

**解读**:HDK 矩阵同样延续「老 MindStudio 只认老 HDK」的规律;26.0.RC1 与 25.7.RC1 合并为一档,说明二者承担相同能力;HDK 26.1.0 仍只有 26.1.x 支持,体现驱动与工具链强绑定的特性。

---

### 表 5:新增特性总表(原文第 4 节,逐行还原并解读)

由于表内共 44 条特性记录(原文中 msProf 记录在文末被截断),下表按工具分组保留原文描述并给出逐行解读:

| 工具 | 特性名称 | 原文特性描述 | 解读 |
| ---- | ---- | ---- | ---- |
| msKPP | compile.json 文件生成 | 支持在编译阶段生成 compile.json 编译信息文件,记录编译选项与依赖信息,便于与性能分析及 CI 工具链集成。 | 把编译期元数据固化为结构化文件,打通「编译—性能分析—CI」三段流水线。 |
| msKPP | 统一构建方案适配 | 统一构建入口脚本,适配新型统一构建镜像,UT 同步适配新构建环境,提升构建稳定性与 CI 兼容性。 | 收敛构建入口到统一脚本,降低镜像/UT 环境差异导致的失败率。 |
| msKPP | clang-tidy 代码检查 | 新增 clang-tidy 配置文件与 pre-commit clang-tidy hook,支持代码提交前的静态分析检查与 clean code 规范校验。 | 把静态检查前移到 commit 阶段,降低 CI 反馈延迟。 |
| msKPP | 单元测试补充 | 新增 msKPP 核心模块的单元测试用例,提升代码测试覆盖率与回归保障。 | 补齐核心模块回归网。 |
| msKPP | CI 版本号构建适配 | CI 构建流程支持基于 Tag 指定发布包版本号,确保出包版本与实际代码版本一致。 | 让 Tag → 包版本号可追溯,避免「代码与包对不上」问题。 |
| msOpGen | pip 安装方式优化(不兼容变更) | 将 whl 包安装方式从传统的 `pip install` 改为 `entry_points` 方式,解决 `pip uninstall` 卸载后残留文件的问题;`msopst.ini` 配置文件位置由旧路径调整到标准配置目录。 | **破坏性变更**:用户脚本若硬编码了 `msopst.ini` 路径需同步迁移。 |
| msOpGen | 统一构建方案适配 | 统一构建入口脚本,`build.py` 升级为正式方案,支持稳定 checkout 子模块到指定版本;适配新型统一构建镜像。 | `build.py` 从临时方案转正,锁定子模块版本,提升首次构建成功率。 |
| msOpGen | 安全校验放宽 | 去除安装过程中的软链接校验、文件属主校验及路径长度限制。 | 适配受限/容器化部署环境,降低安装门槛。 |
| msOpGen | 快速入门优化 | 适配 CANN 9.0.0 中编译接口的变更,更新快速入门中的编译命令与示例。 | 文档与示例跟上 CANN 接口演进,避免新用户踩坑。 |
| msOpGen | MindStudio LOGO 与 pre-commit | 命令行工具新增 MindStudio 启动 LOGO 与版本信息展示;新增 pre-commit 配置文件。 | 提升品牌辨识度,加入 pre-commit 流程。 |
| msOpGen | CI 构建版本号适配 | 适配 CI 基于 Tag 或分支指定发布包版本号流程。 | 与 msKPP 一致的 Tag→包号策略。 |
| msDebug | 昇腾 950PR/DT 芯片上板调试 | 全面支持昇腾 950PR/DT 芯片 AscendC 算子上板调试,包括软硬断点、内存/变量/寄存器展示、单步、中断、多核切换、线程切换;支持 `simd_vf` 场景断点并自动判断软/硬断点。 | 昇腾 950 算子调试的完整闭环能力首次落地。 |
| msDebug | 昇腾 950PR/DT 芯片支持 coredump 解析 | 支持 coredump 文件解析:调用栈回溯、错误寄存器展示、线程切换;自动获取 core 中的 kernel object 辅助符号解析。 | 离线现场分析能力,提升疑难问题排查效率。 |
| msDebug | Host 侧读取 GM 内存 | 断点停在 Host 侧时,可直接读 Device 端 GM 内容,无需切换 Device 侧。 | Host/Device 混合调试场景下提升排障效率。 |
| msDebug | 线程信息展示增强 | 新增线程信息详细展示与线程切换,支持 core 文件线程展示;MI stopped 事件额外输出当前 core 的 `thread-dim` 信息。 | 调试上下文可视化更完整。 |
| msDebug | 寄存器展示优化 | 按 `aic/aiv/simt/simd` 分类型展示寄存器,统一打印顺序;新增 S/R 通用寄存器读取;合并 core 解析与上板寄存器读取;补充下一代芯片 error 寄存器。 | 多架构统一寄存器视图,降低跨架构调试心智负担。 |
| msDebug | 断点类型自动识别 | MI 接口新增断点位置是否处于 SIMT 区域的判断信息,自动区分软/硬断点。 | 减少断点类型误设导致的调试中断。 |
| msDebug | 易用性与构建优化 | 统一构建脚本、适配 CMake 4.x、移除 CMake 上限、适配 `asc` 新注册 Function、支持 `aclrt` 算子不强依赖 runtime。 | 构建环境与运行时依赖同时放宽。 |
| msSanitizer | DCCI 缺失检测 | 通过 `--check-dcci=yes` 启用,识别遗漏的 `dcci` 指令;开启时自动关闭指令过滤与竞争检测。 | 缓存一致性预检;开关互斥避免误报。 |
| msSanitizer | 卡间竞争检测 | 通过 `--check-cross-npu-races=yes` 启用,感知共享内存数据竞争,支持 `msTX` 软同步(`barrier`/`signal`)。 | 跨卡竞争分析从 0 到 1。 |
| msSanitizer | SIMT 架构检测增强 | 未初始化检测支持 SIMT 并通过指令重放增强;支持多 `simt_vf` 函数竞争分析、`simt` 与 `main_scalar` 间 UB 竞争识别、`sync_threads` 未配对检测;新增 `simt_call/simt_start/simt_end` 桩。 | SIMT 架构检测能力补齐至接近 SIMD 覆盖度。 |
| msSanitizer | 读写权限控制 | SIMD 越界检测与 SIMT 检测新增 `--check-level` 参数,可指定仅读 / 仅写 / 读写双向。 | 检测粒度可调,降低误报。 |
| msSanitizer | GM Buffer 安全区越界写检测 | 在 GM buffer 尾部增加安全保护区,识别越界写,覆盖 Tiling 下沉 AICPU 场景;通过 `--padding` 控制大小。 | 「加哨兵」式的越界防护。 |
| msSanitizer | 同步检测增强 | 新增算子卡死检测;补充 `get_buf/rls_buf` 流水间与核间竞争检测。 | 检测覆盖从「数据正确性」扩展到「流程不死锁」。 |
| msSanitizer | 运行时 Ctrl-c 中断 | 算子运行时支持 Ctrl-c 信号中断优雅退出。 | 检测耗时长时可手动中止。 |
| msSanitizer | 易用性与构建优化 | 默认关闭工具日志(`--log-level` 可开启);help 优化;统一构建脚本;适配 CMake 4.x;LOGO 与版本信息。 | 默认低噪声,按需调高。 |
| msOpProf | 昇腾 950PR/DT 指令级流水图 | 在昇腾 950PR/DT 上采集并生成指令级流水图(Pipeline Timeline),可视化各指令在不同流水阶段时序。 | 流水线气泡与瓶颈定位。 |
| msOpProf | SIMT Warp 粒度流水图与 Stall 分析 | 新增 SIMT 算子 warp 维度流水图;新增 Top Stall Reason 自动归因。 | SIMT 性能瓶颈可量化、可归因。 |
| msOpProf | 内存热力图指标增强 | 通过动态插桩细化指令级搬运通路,补充 `UB→GM`、`Dcache→GM`、`UB→L1`、`L1→UB` 等多方向内存带宽数据。 | 内存子系统瓶颈分析维度更全。 |
| msOpProf | 仿真流水图 Scalar 头开销展示 | 仿真流水图新增 Scalar 指令头开销(译码/发射等)展示,A2/A3 均支持。 | 把 Scalar 与计算耗时分离,定位 Scalar 侧瓶颈。 |
| msOpProf | 动态插桩细化与 SIMT 指令桩 | 新增 SIMT 类指令动态桩,细化搬运通路数据采集粒度。 | 流水图与热力图数据来源更精准。 |
| msOpProf | AscendC API 打点支持 | 部分款型支持基于 AscendC API 的自定义打点,流水图对应展示。 | 用户可在代码中标记关键段做分段分析。 |
| msOpProf | 自定义打点流水图易用性优化 | 优化展示体验,warp 流水图增加使用线程数量展示。 | 并行度可观测。 |
| msOpProf | 易用性与构建优化 | 统一构建脚本、适配 CMake 4.x;help 优化;LOGO;新增 clang-tidy 配置。 | 与其他工具对齐构建与代码规范。 |
| msKL | 统一构建方案适配 | 统一构建入口脚本,适配新型统一构建镜像。 | 构建链路收敛。 |
| msKL | pre-commit 代码检查 | 新增 pre-commit 配置,支持代码提交前自动风格检查与格式校验。 | 代码规范前置。 |
| msKL | CI 版本号构建适配 | CI 支持基于 Tag 或分支指定发布包版本号。 | Tag→包号可追溯。 |
| msKL | 单元测试补充 | 新增 `test_driver.py` 与 `test_config.py` 单元测试用例。 | 核心模块回归网。 |
| msTX | 内存属性指定接口 | 新增内存属性指定 API,可显式标记某段内存区域读写属性(只读/只写/读写),辅助 msSanitizer 区分合法/异常访问。 | 用户语义直接喂给工具,降低误报。 |
| msTX | Torch NPU 内存访问上报宏 | 新增 `TORCH_NPU_REPORT_MEM_ACCESS` 宏,配合 Ascend PyTorch Profiler 的 `mstx=True` 采集模式做精细内存分析。 | 框架侧埋点 + Profiler 采集的联动。 |
| msTX | compile.json 文件生成 | 编译阶段生成 `compile.json` 编译信息文件。 | 与 msKPP 一致的编译元数据沉淀策略。 |
| msTX | 统一构建方案适配 | 统一构建脚本、适配新镜像、UT 同步适配。 | 构建链路收敛。 |
| msTX | clang-tidy 代码检查 | 新增 clang-tidy 配置与 pre-commit hook。 | 静态检查前置。 |
| msTX | CI 版本号构建适配 | CI 支持基于 Tag 指定发布包版本号。 | Tag→包号可追溯。 |
| msProf | 昇腾 950PR/DT 芯片支持 DPU 调度与硬件采样解析 | 新增 DPU task track 与 hccl track 数据的 C 化解析能力,支持 DPU 算子下发执行(**原文在「DPU 算子下发执行」处被截断,本节剩余内容无法从原文获取**)。 | 仅就可见原文:解析能力从脚本/脚本化升级为 C 化,降低开销;后续特性缺失。 |

> ⚠️ **原文截断提示**:新增特性表末尾的 `msProf` 章节在「支持 DPU 算子下发执行」处被截断,本文档无法对该行后续内容及其他潜在遗漏特性进行解读,已在表中如实标注。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **msTX ↔ msSanitizer 联动**:msTX 新增的内存属性指定 API 与 `TORCH_NPU_REPORT_MEM_ACCESS` 宏,均显式声明为「辅助 msSanitizer 精确区分合法访问与异常访问」「配合 Ascend PyTorch Profiler 的 `mstx=True` 采集模式」——即上层语义信息向下游检测/分析工具回灌,形成「声明(msTX)→ 检测(msSanitizer)/采集(Profiler)」的串联。
- **msOpProf 与 AscendC 算子代码**:自定义打点要求用户在算子代码中通过 AscendC API 插桩标记关键代码段,意味着 msOpProf 与 AscendC 算子源是紧耦合关系;同样,`compile.json` 生成也是 msKPP 与 msTX 共同特性,反映编译元数据被多个工具共用。
- **msOpGen ↔ msDebug ↔ msSanitizer ↔ msOpProf**:四者均面向算子开发全流程(msOpGen 产生算子工程 → msDebug 调试 → msSanitizer 静态/动态检测 → msOpProf 性能分析),构成算子开发的四阶段流水线;msOpGen 中的 `msopst.ini` 配置变更会反向影响其他工具链对算子工程的解析路径。
- **MindStudio ↔ CANN ↔ TorchNPU ↔ Ascend HDK**:由版本兼容性矩阵可见,26.1.x 必须依托 CANN 9.1.0(及向下兼容的 8.5.0/9.0.0)、TorchNPU 26.1.0(及向下兼容的 2.3.0/26.0.0)、Ascend HDK 26.1.0(及向下兼容的 25.5.x/26.0.RC1/25.7.RC1)运行,任一层版本不匹配都会触发 `/` 即不兼容。
- **msDebug ↔ 昇腾 950PR/DT 芯片**:msDebug 的多条新增特性(上板调试、coredump 解析、寄存器展示优化、断点类型自动识别、Host 读 GM)均明确指向昇腾 950PR/DT 这一新架构芯片;msOpProf 的指令级流水图、SIMT Warp 流水图等同样以昇腾 950PR/DT 为首期落地目标,二者共同支撑昇腾 950 算子的「调试—分析」闭环。
- **msSanitizer 内部开关互斥**:DCCI 缺失检测开启时**自动关闭指令过滤与竞争检测**,意味着同一算子运行中三类检测不能同时叠加,存在排他约束关系。
- **统一构建 ↔ CMake 4.x ↔ CI**:msKPP / msOpGen / msDebug / msSanitizer / msOpProf / msKL / msTX 均完成「统一构建入口脚本 + 新型统一构建镜像 + 适配 CMake 4.x」三件套升级,且 CI 支持 Tag→包号追溯,形成统一的工程脚手架。

---

## 【使用方法】

原文未提供独立的「启用步骤/安装命令」章节,但散落在特性描述中的可执行项如下,均按原文摘录:

- **DCCI 缺失检测启用**(原文,msSanitizer):`--check-dcci=yes`(开启时自动关闭指令过滤与竞争检测)。
- **卡间竞争检测启用**(原文,msSanitizer):`--check-cross-npu-races=yes`(感知共享内存数据竞争,支持 `msTX` 软同步语义 `barrier`/`signal`)。
- **读写权限控制**(原文,msSanitizer):`--check-level` 参数指定仅检测读 / 仅写 / 读写双方向。
- **GM Buffer 安全区大小控制**(原文,msSanitizer):`--padding` 参数控制安全区大小。
- **日志级别控制**(原文,msSanitizer):默认关闭工具日志以提升检测性能,可通过 `--log-level` 按需开启。
- **运行时中断**(原文,msSanitizer):算子运行时可通过 `Ctrl-c` 信号优雅中断退出。
- **msOpGen 包安装方式变更**(原文,msOpGen 不兼容变更):whl 包安装由传统 `pip install` 改为 `entry_points` 方式;`msopst.ini` 配置文件位置由旧路径调整到标准配置目录——**依赖旧路径的自定义脚本需要同步适配**。
- **msOpGen 构建入口**(原文,msOpGen):`build.py` 升级为正式方案,支持稳定 checkout 子模块到指定版本。
- **pre-commit 静态检查**(原文,msKPP / msKL / msTX / msOpProf 等多处):新增 clang-tidy 配置文件与 pre-commit clang-tidy hook,支持代码提交前的自动风格检查与格式校验。
- **compile.json 生成**(原文,msKPP / msTX):编译阶段生成 `compile.json` 编译信息文件,记录编译选项与依赖信息。
- **CI 出包版本号指定**(原文,msKPP / msOpGen / msKL / msTX):CI 构建流程支持基于 Tag 或分支指定发布包版本号,确保出包版本与实际代码版本一致。
- **msTX 内存属性 API**(原文,msTX):用户可在算子代码中通过接口显式标记某段内存区域的读写属性(只读/只写/读写)。
- **Torch NPU 内存访问上报**(原文,msTX):新增 `TORCH_NPU_REPORT_MEM_ACCESS` 宏,配合 Ascend PyTorch Profiler 的 `mstx=True` 采集模式使用。
- **配套版本组合**(原文第 2 节):MindStudio 26.1.x ↔ CANN 9.1.0 ↔ TorchNPU 26.1.0 ↔ Ascend HDK 26.1.0 为默认推荐配套;若使用 CANN 8.5.0/9.0.0、TorchNPU 2.3.0/26.0.0、HDK 25.5.x/26.0.RC1/25.7.RC1 也可向下兼容运行。

> ⚠️ **原文截断提示**:本文档 `msProf` 条目在「支持 DPU 算子下发执行」处被截断,该工具的完整新增特性与对应启用方式在原文中未提供完整信息。
