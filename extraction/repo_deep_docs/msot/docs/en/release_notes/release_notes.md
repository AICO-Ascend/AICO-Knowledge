# MindStudio Operator Tools Release Notes

> 仓 `msot` · 路径 `docs/en/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/en/release_notes/release_notes.md

# MindStudio Operator Tools 26.0.0 Release Notes 深度解读

---

## 【定位】

本文档是 Huawei CANN 算子工具链 **MindStudio Operator Tools (msOT) 26.0.0**（Internal Beta）的发版说明,系统性地描述了 msDebug、msOpProf、msSanitizer、msOpGen 四大子工具在算子调试、性能调优、内存正确性检测、算子工程生成方向上 **新增能力、构建发布变更、Bug 修复** 三大类变更,并标注其与 BiSheng 编译器、CANN 多代芯片、AscendC 算子开发框架的兼容关系。

---

## 【技术要点】

1. **版本兼容性矩阵收敛**: msOT 26.0.0 适配 CANN ≥ 9.0.0(推荐) 与 Python ≥ 3.11(推荐);旧线 8.3.0 兼容 CANN ≥ 8.2.RC1。两版均建议 Python 3.11+。
2. **msDebug 新增 6 类能力**: 无需设置 kernel object 路径的板级调试、读内存跳过元素计数显示、shared_memory 算子调试、asc 编译算子的 coredump + 板级调试、host 传入 kernel struct 变量的变量日志、coredump 解析中的非内联编译调用栈回溯。
3. **msOpProf 新增 5 项性能分析能力**: shmem/asc 算子库性能调优、custom compute-fusion 框架通过 AscendC API 插桩生成计算流水线图、Scalar 性能数据细化分析（含计算访存热图-访存负载分析扩展指标）、SIMT VF 指令 stall 与寄存器利用率统计（含板级代码热点图扩展指标）、SIMT VF 指令发射效率与负载均衡分析（含计算访存热图-核间负载分析扩展指标）。
4. **msSanitizer 新增 7 类检测语义**: LocalTensor 在 AscendC 一元/二元/数据搬移 API 的越界检测、SIMT 与 Main-Scalar 流水线间内存破坏检测、SIMTR VF 内线程竞争检测、冗余 SET_FLAG 指令检测、新增 SET_FLAG/WAIT_FLAG/SET_FLAGI/WAIT_FLAGI/HSET/HWAIT/GET_BUF/RLS_BUF 八条同步指令的核内/核间竞争检测增强。
5. **构建/安全基线统一**: root 用户安装目录最小权限改为 **700**;安装包命名统一;新增 `libform.so.5` 交付物;新增 Unix Makefiles 构建支持;UT 调试编译模式默认开启。
6. **msOpGen**: 仅说明"适配新的 AscendC 算子工程",无细节。

---

## 【关键机制与数据】

- **性能数据(原文)**: msOpProf 依赖仓下载函数经优化后,下载速度提升 **10x**;msSanitizer UT 依赖下载速度提升 **10x** 且彻底解决概率性失败问题。
- **编译器适配(原文)**: 修复 GCC 7/12 下 UT 编译失败;适配 CANN 镜像中的 GCC 12.x 变更;msSanitizer 适配 GCC 11.x。
- **新交付物路径(原文)**: `sanitizer_report.h` 头文件被打入安装包;mstx 内核侧接口经此头文件暴露。
- **mstx 接口解耦(原文)**: mstx 的内存池信息上报接口**解除了 region 与 heap 的绑定限制**,支持直接注册 region。
- **新命令行选项(原文)**: msSanitizer 新增 `--demangle`,用于控制用户界面中函数名的展示格式(并修复了原"调用栈回溯命令行选项名不符合业界惯例"的命名问题)。
- **板级调试前置条件变更(原文)**: 不再强制要求设置 kernel object 路径。
- **依赖库路径修正(原文)**: 修复编译过程中 `libtinfo` 动态库路径错误。

---

## 【表格解读】

### 表 1: 产品版本信息(Product Version Information)

| Product Name | Product Version | Version Type |
|------|-------|------|
| msOT | 26.0.0 | Internal Beta |
| msOT | 8.3.0 | Official Release |

**逐行解读**:
- 第一行: msOT 26.0.0 为 **内部测试版**,是本次文档的主体变更集。
- 第二行: msOT 8.3.0 为 **正式发布版**,作为兼容旧版 CANN 用户的稳定分支存在(参见表 2)。

### 表 2: 相关产品版本兼容性(Related Product Version Compatibility)

| msOT Version | CANN Version | Python Version |
|----------|-----------------|----------|
| 26.0.0 | 9.0.0 and above recommended | Python 3.11 and above recommended |
| 8.3.0 | 8.2.RC1 and above | Python 3.11 and above recommended |

**逐行解读**:
- 第一行: msOT 26.0.0 必须配套 **CANN 9.0.0 及以上**(推荐),Python 3.11+(推荐);定位为面向新芯片规范与 BiSheng 编译器选项变更的版本。
- 第二行: msOT 8.3.0 兼容 CANN **8.2.RC1 及以上**,Python 3.11+(推荐);作为稳定/维护分支。
- 两行共同点: **Python 基线一致(3.11+)**,反映工具链已统一收敛到该 Python 版本;**CANN 主版本分裂**(8.x vs 9.x)意味着两条分支在底层芯片标识符与编译器行为上不可互换。

---

## 【公式解读】

**原文无公式**。

(注:文中 msOpProf 提到"优化了部分芯片型号的理论带宽值与性能指标公式",但**并未给出具体公式形式**,因此不进行虚构展开。)

---

## 【关联】

文档为发版说明体裁,**原文未提供内部链接**(如 commit、issue、文档跳转)。可从文本中析出的关联关系如下:

- **msDebug ↔ BiSheng 编译器 / asc 编译器**: 26.0.0 的核心兼容动因是"适配 BiSheng 编译器编译选项变更",并新增对 asc 编译算子的 coredump 与板级调试能力。
- **msDebug ↔ 芯片标识符**: 26.0.0"适配多种新芯片规格,兼容 CANN 芯片标识符变更",意味着子命令(如 `ascend info cores`)的目标识别逻辑被重写。
- **msSanitizer ↔ AscendC 算子 API**: 检测面覆盖 AscendC 的 Unary/Binary/DataMovement API(LocalTensor 越界)与同步原语(SET_FLAG/WAIT_FLAG 等),且 bugfix 多次涉及 AscendC API 内部实现栈的屏蔽问题(项 7)。
- **msSanitizer ↔ mstx 内核接口**: mstx 增加跨核 barrier 与 set_flag/wait_flag 语义上报接口,通过新交付的 `sanitizer_report.h` 暴露给用户集成。
- **msOpProf ↔ AscendC 自定义算子融合框架**: 通过 AscendC API 插桩生成 compute pipeline graph,即在 AscendC 编译产物上做后置插桩以提取融合流水。
- **msOpGen ↔ AscendC 算子工程**: 仅声明"适配新的 AscendC 算子工程",具体生成模板/工程结构未在文中展开。
- **msDebug / msSanitizer ↔ 安装器**: 两者均涉及 root 安装权限收敛(700)与安装包命名统一,反映工具链安装层面的统一治理。

---

## 【使用方法】

原文直接涉及的可执行入口与配置项:

- **msSanitizer 命令行参数**:
  - `--demangle`: 控制用户界面中函数名的显示格式(原文: "Added the --demangle command-line option")。
  - 调用栈回溯命令行选项被**重命名**以符合业界惯例(原文仅说明"fixed ... updated the command-line option name",未给出原名/新名)。
- **msOpProf 安装包名**: 由旧名变更为 **`mindstudio-opprof_linux.run`**(原文: "Changed the installation package name to mindstudio-opprof_linux.run")。
- **msOpProf 文档入口**: 安装指南被重命名为 **`msopprof_install_guide.md`**;新增依赖 `pigz` 的说明(原文: "Added a dependency note for pigz in the installation documentation")。
- **msOpProf 调试编译**: 新增调试编译选项以支持对编译产物进行断点调试(原文: "Added a debug compilation option to support breakpoint debugging of compiled artifacts")。
- **msSanitizer 调试构建**: 新增调试编译能力,**支持 VSCode 断点调试**;UT 编译**默认开启 debug 编译模式**。
- **msDebug 板级调试前置**: "Supported on-board debugging **without setting the kernel object path**"。
- **msSanitizer 内核侧集成**: 用户可通过 `sanitizer_report.h` 头文件按需集成 mstx 上报接口。
- **msSanitizer mstx 内存池**: region 注册**不再要求与 heap 绑定**,支持直接注册。

未涉及项:环境变量名、配置文件路径、运行时参数阈值(如检测灵敏度档位)等**原文均未给出**。
