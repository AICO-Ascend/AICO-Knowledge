# MindStudio Operator Tools 版本说明

> 仓 `msot` · 路径 `docs/zh/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/zh/release_notes/release_notes.md

# MindStudio Operator Tools (msOT) 版本说明 深度解读

---

## 【定位】

本文档是「MindStudio Operator Tools (msOT)」26.0.0(内测) 与 8.3.0(正式) 两个版本的官方 release notes,系统披露了 msDebug / msKL / msKPP / msOpGen / msOpProf / msSanitizer 等昇腾算子开发工具链的版本配套、特性变更与 Bugfix,用于帮助开发者评估版本升级影响与新特性可用性。

---

## 【技术要点】

1. **版本配套矩阵**:msOT 26.0.0 需搭配 CANN 9.0.0+ 与 Python 3.11+;msOT 8.3.0 需搭配 CANN 8.2.RC1+ 与 Python 3.11+;且 26.0.0 已「适配毕昇编译器编译选项变更」与「多种新增芯片规格型号 + CANN 芯片标识变更」。
2. **msDebug 新增能力**:支持不设置 kernel object 路径上板调试;读内存时跳过元素个数;shared_memory 算子调试;asc 编译算子的 coredump 与上板调试;host 侧结构体变量打印;coredump 解析支持非 inline 编译调用栈回溯。
3. **msOpProf 性能调优新增**:支持 shmem / asc 算子库;通过 AscendC API 打点生成「通算融合框架」流水图;Scalar 性能数据精细化分析;SIMT VF 指令 Stall、寄存器利用率、发射效率、负载均衡分析;并输出计算内存热力图与代码热点图。
4. **msSanitizer 检测能力扩展**:新增 LocalTensor(单/双目计算、搬运 API)越界检测;SIMT 与 Main-Scalar 流水间内存踩踏;SIMTR VF 内线程间竞争;冗余 SET_FLAG 检测;插桩指令扩到 SET_FLAG / WAIT_FLAG / SET_FLAGI / WAIT_FLAGI / HSET / HWAIT / GET_BUF / RLS_BUF;新增 `--demangle` CLI 选项与实时寄存器状态采集;mstx 接口通过 `sanitizer_report.h` 头文件开放。
5. **msKL / msKPP / msOpGen 首次发布(8.3.0)**:msKL 暴露 `tiling_func` / `get_kernel_from_binary` 与 autotune 系列接口;msKPP 支持算子特性建模、计算搬运规格分析、极限性能分析、tiling 初步设计;msOpGen 支持算子原型工程生成、仿真 dump 转仿真流水图、编译部署。
6. **构建与发布层变更**:root 用户安装目录最小权限改为 700;安装包命名统一整改(`mindstudio-opprof_linux.run` 等);支持 Unix Makefiles 构建;解决 GCC 7 / 11.x / 12.x 编译失败;新增 `libform.so.5` 交付件;依赖仓下载速度提升 10 倍;msSanitizer UT 默认启用 debug 模式,新增 `sanitizer_report.h` 头文件。

---

## 【关键机制与数据】

### msSanitizer 工作原理
- **原文**:检测范围分为四大类——内存检测(Global Memory / Local Memory 越界、未对齐)、竞争检测(并发内存访问引发的数据竞争)、未初始化检测、同步检测(Ascend C 算子中未配对的 SetFlag/WaitFlag 指令)。
- **原文**:26.0.0 在流水间竞争插桩中新增 `SET_FLAG / WAIT_FLAG / SET_FLAGI / WAIT_FLAGI / HSET / HWAIT / GET_BUF / RLS_BUF` 八类核内/核间同步指令的解析,以「增强竞争检测能力」。
- **原文**:mstx 接口新增针对「核间 barrier 与 set_flag/wait_flag 语义」的上报通道;内存池上报「去除 region 与 heap 的绑定限制,支持 region 直接注册」。

### msOpProf 工作原理
- **原文**:通算融合算子性能采集机制为「通过 AscendC API 进行性能打点,采集代码在算子 block 上的实际耗时情况」。
- **原文**:计算内存热力图、Cache 热力图、Roofline 瓶颈分析图、算子代码热点图、Pipe 流水图均以「资源维度展示 + 关联调用栈」方式定位瓶颈。
- **原文**:性能数据从多指标维度(基础信息、计算负载、内存负载、SIMT VF Stall、寄存器利用率、发射效率)落盘为「性能数据文件」。
- **原文**:构建产物下载速度「10 倍提升」;仿真流水图泳道排序与指令颜色划分进行了优化。

### msDebug 工作原理
- **原文**:上板调试提供「断点展示、变量打印、寄存器打印、内存打印、代码行级别单步调试、核信息展示与切换、调用栈展示」全链路能力。
- **原文**:coredump 解析支持「调用栈展示、寄存器展示、变量展示」。
- **原文**:26.0.0 在 root 安装场景将「文件夹的最小权限要求修改为 700」。

### msKPP / msKL 工作原理
- **原文**:msKPP 基于自身接口「模拟出算子耗时」,输出搬运流水统计、指令信息统计、指令流水图、指令占比饼图,并「快速筛选出几种较优的 tiling 策略」。
- **原文**:msKL 通过 `tiling_func` 和 `get_kernel_from_binary` 接口「调用 msOpGen 工程中的 tiling 函数以及用户自定义的 Kernel 函数」;autotune 系列接口支持「对模板库算子进行代码替换、编译、运行以及性能对比」。

---

## 【表格解读】

### 表格 1:产品版本信息(原文逐字还原)

| 产品名称 | 产品版本 | 版本类型 |
|----------|----------|----------|
| msOT | 26.0.0 | 内测版本 |
| msOT | 8.3.0 | 正式版本 |

**逐行解读**:
- 第 1 行 `msOT / 26.0.0 / 内测版本`:本文档并列发布的两个版本之一,处于内测阶段,通常面向早期适配与兼容性验证,需结合 CANN 9.0.0+ 使用。
- 第 2 行 `msOT / 8.3.0 / 正式版本`:正式发布版本,基于 CANN 8.2.RC1+,对应工具链(8.3.0)的稳定交付,适合生产环境使用。

### 表格 2:相关产品版本配套说明(原文逐字还原)

| msOT版本 | CANN版本 | Python版本 |
|----------|----------|------------|
| 26.0.0 | 推荐9.0.0及以上 | 推荐 Python 3.11及以上 |
| 8.3.0 | 8.2.RC1及以上 | 推荐 Python 3.11及以上 |

**逐行解读**:
- 第 1 行 `26.0.0 / CANN 9.0.0+ / Python 3.11+`:内测版本对底层 CANN 算子栈提出更高要求(CANN 9.0.0),与「适配毕昇编译器编译选项变更」「适配多种新增芯片规格型号」相互印证,表明 26.0.0 是面向新一代硬件 + 新版 CANN 的内测基线。
- 第 2 行 `8.3.0 / CANN 8.2.RC1+ / Python 3.11+`:正式版本覆盖当前主流 CANN 8.2.RC1 系列用户,Python 版本要求与 26.0.0 保持一致,保证脚本工具链兼容。
- 两行的共同项:均要求 Python 3.11+,说明 msOT 工具链脚本层已统一切换到较新 Python 解释器,迁移到旧版 Python 的用户需关注兼容性。

---

## 【公式解读】

原文无公式。

---

## 【关联】

1. **msOpGen ↔ msKL**:原文「msKL 提供 `tiling_func` 和 `get_kernel_from_binary` 接口,支持调用 msOpGen 工程中的 tiling 函数以及用户自定义的 Kernel 函数」——说明 msOpGen 生成的算子工程是 msKL 调测的输入载体,二者构成「算子生成 → 算子调测/调优」上下游链路。
2. **msOpProf ↔ AscendC API**:「支持自定义通算融合框架的性能分析能力,可通过 AscendC API 打点生成通算流水图」——msOpProf 与 AscendC 算子编程框架直接耦合,打点 API 是其性能采样的入口。
3. **msSanitizer ↔ mstx / sanitizer_report.h**:「kernel 侧 mstx 接口通过 sanitizer_report.h 头文件进行开放,用户可自定义接入」——sanitizer_report.h 是 mstx 接口对外开放的唯一通道,用户的自定义检测上报必须经由此头文件。
4. **msOT ↔ CANN / 毕昇编译器**:26.0.0 的「适配毕昇编译器编译选项变更」「兼容 CANN 芯片标识变更」表明 msOT 工具链与底层 CANN 发行包、毕昇编译器强耦合,版本配套矩阵(表格 2)是依赖关系的硬约束。
5. **msDebug / msOpProf / msSanitizer ↔ msOpGen 算子工程**:三者在 8.3.0 中均为「首次发布」,且 msDebug 支持「asc 编译的算子的 coredump 调试与上板调试」、msOpProf 支持「shmem 算子库、asc 算子库的性能调优」——三个工具共同围绕 msOpGen 生成的工程进行调试、性能分析、正确性验证,形成「生成 → 调优 → 调试 → 正确性验证」完整闭环。

---

## 【使用方法】

原文未涉及具体启用命令、配置项或调用示例(本文档定位为 release notes,仅披露变更清单;具体的 install/run 命令请参见仓库内各子工具的安装指南与用户手册,例如 msOpProf 的 `msopprof_install_guide.md` 在 26.0.0 中被重命名)。
