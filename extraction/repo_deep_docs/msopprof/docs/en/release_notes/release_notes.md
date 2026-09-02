# MindStudio Ops Profiler Release Notes

> 仓 `msopprof` · 路径 `docs/en/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopprof/docs/en/release_notes/release_notes.md

# msOpProf Release Notes 深度解读

## 【定位】

本文档是华为 **MindStudio Ops Profiler (msOpProf)** 工具的发布说明 (Release Notes),记录了 `26.0.0` 内部测试版与 `8.3.0` 官方正式版两个版本的产品定位、版本依赖、新增/优化/删除特性以及构建发布变更,为开发者与运维人员提供版本差异、依赖兼容性和升级参考。

---

## 【技术要点】

1. **算子库性能调优扩展**:在 `26.0.0` 中新增对 `shmem` 与 `asc` 算子库 (operator libraries) 的性能调优支持 (原文 §26.0.0 新特性 #1)。
2. **自定义通算一体框架分析**:通过 **AscendC API 插桩 (instrumentation)** 生成通信与计算流水图 (pipeline charts),实现自定义通算一体框架的性能分析 (原文 §26.0.0 新特性 #2)。
3. **Scalar 单元细粒度分析**:新增 Scalar 单元细粒度性能数据分析,用于定位 Scalar 单元瓶颈位置,并在**性能数据文件**与**计算内存热力图 (memory heatmap) - 内存负载分析**中扩展相关性能指标 (原文 §26.0.0 新特性 #3)。
4. **SIMT VF 指令分析双能力**:新增 SIMT VF 指令**停顿分析 (stall analysis) 与寄存器利用率显示** (板上代码热点图扩展指标);同时新增 SIMT VF 指令**发射效率统计 (issue efficiency) 与负载均衡分析** (计算内存热力图 - 核占用视图扩展指标) (原文 §26.0.0 新特性 #4、#5)。
5. **依赖下载提速**:优化依赖仓库下载功能,下载速度提升 **10 倍** (原文 §26.0.0 构建与发布 #1)。
6. **多版本版本矩阵差异**:`8.3.0` 与 `26.0.0` 对 CANN 版本要求不同——前者要求 `8.2.RC1 or later`,后者要求 `9.0.0 or later (recommended)`;Python、JSON、SecureC、Makeself、llvm-project 版本要求两版本相同 (原文表格 §Related Product Versions)。

---

## 【关键机制与数据】

- **芯片兼容性机制 (原文 §26.0.0 Version Compatibility)**:适配 BiSheng Compiler 选项变更;新增对多种新芯片规格与模型变体的兼容性,并随 CANN 芯片识别变更同步更新。
- **通算流水图生成机制 (原文 §26.0.0 新特性 #2)**:通过 AscendC API 插桩 → 采集算子块上代码的实际执行时间 → 用于通信与计算算子的性能分析与优化。
- **Scalar 瓶颈定位机制 (原文 §26.0.0 新特性 #3)**:细粒度数据 → 识别 Scalar 单元瓶颈点 → 性能数据文件 + 计算内存热力图(内存负载分析)双重指标扩展。
- **SIMT VF 双维度分析 (原文 §26.0.0 新特性 #4、#5)**:停顿+寄存器利用率 → 板上代码热点图指标扩展;发射效率+负载均衡 → 计算内存热力图(核占用视图)指标扩展。
- **构建安全增强机制 (原文 §26.0.0 优化 #5)**:更新构建产物与输出文件的权限和组,提升软件安全性。
- **可视化渲染优化 (原文 §26.0.0 优化 #2、#3、#4)**:优化部分芯片型号的理论带宽值与性能指标公式;优化仿真流水线图中的 lane 排序与指令着色;优化代码热点图中指令信息排序。
- **构建调试能力 (原文 §26.0.0 构建与发布 #2)**:新增 debug 构建选项,以支持构建产物的断点调试。
- **性能数据维度 (原文 §8.3.0 新特性)**:msOpProf mode 提供计算内存热力图、Roofline 瓶颈分析图、MC2 算子通算流水图、流水线图、算子代码热点图、Cache 热力图、Profile 数据文件;msOpProf simulator mode 提供指令流水线图、算子代码热点图、内存通道吞吐波形图 (MTE log 通道)。
- **依赖仓库下载性能 (原文 §26.0.0 构建与发布 #1)**:下载速度提升 **10 倍**(原文唯一明确性能数字)。

---

## 【表格解读】

### 表 1:Product Versions(产品版本)

| Product Name | Version | Version Type |
|---|---|---|
| msOpProf | 26.0.0 | Internal test version |
| msOpProf | 8.3.0 | Official version |

**逐行解读**:
- 第 1 行:`msOpProf` 产品名,版本 `26.0.0`,类型为**内部测试版本 (Internal test version)**,为本次新发布的尝鲜版本。
- 第 2 行:`msOpProf` 产品名,版本 `8.3.0`,类型为**官方正式版本 (Official version)**,为本文档中第一个正式发布版本。
- **要点**:同一产品存在"内测先行 + 正式并轨"的双轨发布节奏,用户可基于成熟度需求选择版本。

### 表 2:Related Product Versions(相关产品版本)

| msOpProf Version | CANN Version | Python Version | JSON Version | SecureC Version | Makeself Version | llvm-project Version |
|---|---|---|---|---|---|---|
| 26.0.0 | 9.0.0 or later (recommended) | 3.11 or later (recommended) | v3.12.0 or later | v1.1.16 or later | release-2.5.0 or later | 22.1.2 or later |
| 8.3.0 | 8.2.RC1 or later | 3.11 or later (recommended) | v3.12.0 or later | v1.1.16 or later | release-2.5.0 or later | 22.1.2 or later |

**逐行解读**:
- 第 1 行(`26.0.0` 行):
  - **CANN**:要求 `9.0.0 or later (recommended)`,即 CANN 9.0.0 及以上,**推荐**使用 9.0.0;
  - **Python**:要求 `3.11 or later (recommended)`,**推荐** 3.11 及以上;
  - **JSON**:要求 `v3.12.0 or later`;
  - **SecureC**:要求 `v1.1.16 or later`;
  - **Makeself**:要求 `release-2.5.0 or later`;
  - **llvm-project**:要求 `22.1.2 or later`。
- 第 2 行(`8.3.0` 行):
  - **CANN**:要求 `8.2.RC1 or later`,起步版本低于 `26.0.0`;
  - **Python**、**JSON**、**SecureC**、**Makeself**、**llvm-project**:与 `26.0.0` 行完全一致。
- **跨版本要点**:两个版本唯一差异是 **CANN 最低版本**——`26.0.0` 必须 ≥9.0.0(推荐),`8.3.0` 可从 8.2.RC1 起。这与 §Version Compatibility 中"26.0.0 适配 CANN 芯片识别变更"相呼应,说明新功能依赖新 CANN 内部机制。

---

## 【公式解读】

**原文无公式**。

文中仅出现"理论带宽值与性能指标公式"(原文 §26.0.0 优化 #2)这一**概念性表述**,并未给出具体的 LaTeX 或伪代码公式,因此不作无依据的展开。

---

## 【关联】

- **CANN(昇腾异构计算架构)**:msOpProf 26.0.0 与 CANN 9.0.0+ 强耦合,需随 CANN 芯片识别变更同步更新;8.3.0 兼容 CANN 8.2.RC1+。CANN 是上游依赖。
- **BiSheng Compiler(毕昇编译器)**:26.0.0 中"适配了 BiSheng Compiler 选项变更",编译器选项变化是触发 msOpProf 兼容性变更的上游事件。
- **AscendC API**:为 msOpProf 通算流水图与 MC2 算子性能标注提供插桩入口,是用户实现自定义性能采集的关键 API。
- **`shmem` / `asc` 算子库**:26.0.0 新增调优支持的目标对象,通常与集合通信 / 加速库场景相关。
- **SIMT VF 单元 / Scalar 单元 / MTE log 通道**:均为片上 (on-board) 子模块,分别对应"停顿与寄存器利用"、"细粒度瓶颈"、"内存通道吞吐统计"三类分析能力,共同构成算子级性能剖析的硬件视角。
- **`pigz` 依赖**:安装文档新增提示,说明 msOpProf 安装/解包流程依赖 `pigz` 并行解压缩工具。
- **安装与文档仓库**:
  - 安装包由原名重命名为 `mindstudio-opprof_linux.run`;
  - 安装指南重命名为 `msopprof_install_guide.md`;
  - README 链接更新,新增用户指南与图片,并迁移至 `docs` 仓库;
  - 新增快速入门 (quick start) 文档。
- **版本间内部链接**:本文未提供内部超链接;版本之间的差异通过表格与特性列表对应。

---

## 【使用方法】

原文**直接命令/CLI 调用方式未涉及**,但给出了以下与启用、构建、配置相关的提示:

1. **安装包名称**(原文 §26.0.0 构建与发布 #3):安装包已重命名为 **`mindstudio-opprof_linux.run`**。
2. **安装指南**(原文 §26.0.0 文档 #2、#3):重命名为 **`msopprof_install_guide.md`**;文档中提示新增 **`pigz`** 依赖。
3. **构建选项**(原文 §26.0.0 构建与发布 #2):新增 **debug 构建选项**,可对构建产物进行**断点调试**。
4. **理论带宽值与公式**(原文 §26.0.0 优化 #2):针对部分芯片型号优化了理论带宽值与性能指标公式——若依赖旧公式生成的指标需注意刷新。
6. **依赖版本要求**(原文 §Related Product Versions):严格按表中列出版本组合部署,尤其注意 CANN 版本(`8.3.0` 用 8.2.RC1+,`26.0.0` 用 9.0.0+)。
7. **帮助信息**(原文 §26.0.0 优化 #1):基于不同芯片所支持特性提供差异化帮助信息显示,实际命令帮助输出随芯片而变。
8. **快速入门**(原文 §26.0.0 文档 #4):新增 quick start 文档以辅助首次使用。

> 注:本文档为 changelog 性质,具体的 `msOpProf` 子命令、profile 触发流程、性能数据文件生成命令等,未在此处给出,需查阅用户指南与快速入门文档。
