# 版本说明

> 仓 `mindspeed` · 路径 `docs/zh/release_notes_core.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/release_notes_core.md

# mindspeed `docs/zh/release_notes_core.md` 深度解读

## 【定位】
本篇文档是 MindSpeed Core 26.1.0_core_r0.12.1 版本的正式发布说明(changelog),用于告知用户该版本的产品配套关系、新增/删除特性、已修复问题、升级影响,并为版本选型与兼容性核对提供单一权威来源。

---

## 【技术要点】

1. **版本基线与维护周期**:产品版本 26.1.0_core_r0.12.1,类型为"正式版本",发布时间 2026 年 7 月,维护周期 6 个月。
2. **核心配套依赖**(本版 26.1.0_core_r0.12.1):CANN 9.1.0、TorchNPU 26.1.0、Python 3.10、PyTorch 2.7.1;Python/PyTorch 在 `master`、`26.0.0_core_r0.12.1`、`26.1.0_core_r0.12.1` 三个分支保持一致。
3. **低精度格式扩展**:新增 FP8 / MXFP8 / HiFloat8 三种低精度训练格式,以及 w8a16 量化支持;并新增 MXFP8-32x32 量化与 FSDP 联动,量化后释放 bf16 权重以优化内存。
4. **优化器与模型族扩展**:新增 SwapMuon 与 mcore muon 特性,支持 checkpoint 保存与加载;新增 DeepSeek V4 模型适配及自定义 PP(流水线并行)布局;TE 算子层新增 Hamilton attention 实现。
5. **历史算子清理**:删除 SFA/SFAG/SLI 临时版本算子适配(由正式算子承载);删除 `mindspeed/lite` 模块,Triton 算子迁移至 `mindspeed/ops/triton` 目录。
6. **缺陷修复集合**:涉及 TE 分支 LayerNormLinear 初始化顺序与 NVTE 不一致、LayerNorm 偏置未初始化为零;GMM 算子、NPU `sparse_attn_sharedkv` 算子异常;`l2norm` 批量一致性、`recompute_w_u_fwd` NaN 错误;fboverlap 场景异常内存占用;Triton `chunk_bwd_dqkwg` 时间退化;VeRL 场景 HCCL 缓冲区错误。

---

## 【关键机制与数据】

- **兼容性矩阵设计**:文档给出两个 2×4 兼容矩阵(原文表 2、表 3),`Y` 表示可配套,`/` 表示不可配套。两个矩阵的行均为 `26.0.0_core_r0.12.1` 与 `26.1.0_core_r0.12.1` 两个 MindSpeed Core 版本;列分别为 TorchNPU 的 7.2.0/7.3.0/26.0.0/26.1.0 与 CANN 的 8.3.RC1/8.5.0/9.0.0/9.1.0。
- **升级对业务的影响**:原文:"软件版本升级过程中会导致业务中断"(升级过程中);"对通信无影响"(对网络通信)。
- **MXFP8 内存优化机制**(原文:"MXFP8-32x32 量化及 FSDP 支持,量化后释放 bf16 权重优化内存"):仅描述"释放 bf16 权重"以省内存,未给出具体节省比例数字。
- **性能数据**:原文未给出任何 benchmark 数字或训练吞吐/延迟数据。
- **病毒扫描时间**:扫描时间统一为 2026-07-06,涵盖 QiAnXin 8.0.5.5260、Kaspersky 12.0.0.6672、Bitdefender 7.5.1.200224 三款杀毒软件,结果均为"无病毒,无恶意"。

---

## 【表格解读】

### 表 1(原文"产品版本信息")

| 产品名称 | 产品版本 | 版本类型 | 发布时间 | 维护周期 |
|---|---|---|---|---|
| MindSpeed | 26.1.0_core_r0.12.1 | 正式版本 | 2026年7月 | 6个月 |

**解读**:这是该 changelog 所描述版本的基础元数据。版本号采用 `<YY>.<M>.<P>_core_r<n>.<p>` 命名格式,主干版本号 26.1.0 与 CANN/TorchNPU 的 26.x 系列对齐;`_core_r0.12.1` 表明这是核心代码 0.12.1 的第 1 次再发布(release),可与文末"分支维护策略"链接配合理解生命周期。

---

### 表 2(原文"表 1 MindSpeed Core 软件版本配套表")

| MindSpeed Core 代码分支名称 | CANN 版本 | TorchNPU 版本 | Python 版本 | PyTorch 版本 |
|---|---|---|---|---|
| master(在研版本) | 在研版本 | 在研版本 | Python 3.10 | 2.7.1 |
| 26.1.0_core_r0.12.1 | 9.1.0 | 26.1.0 | Python 3.10 | 2.7.1 |
| 26.0.0_core_r0.12.1 | 9.0.0 | 26.0.0 | Python 3.10 | 2.7.1 |

**逐行解读**:
- **master(在研)**:开发者分支,CANN/TorchNPU 均未锁版本,Python 与 PyTorch 与正式分支保持一致(3.10 / 2.7.1)。
- **26.1.0_core_r0.12.1**:本 changelog 主体描述的版本,要求 CANN 9.1.0 + TorchNPU 26.1.0,Python 3.10,PyTorch 2.7.1。
- **26.0.0_core_r0.12.1**:上一正式版本,要求 CANN 9.0.0 + TorchNPU 26.0.0,其余依赖与本版本一致——意味着跨小版本升级时只需同步替换 CANN/TorchNPU,Python/PyTorch 栈无需变动。

---

### 表 3(原文"表 2 MindSpeed Core 与 TorchNPU 版本兼容")

| MindSpeed Core \ TorchNPU | 7.2.0 | 7.3.0 | 26.0.0 | 26.1.0 |
|---|---|---|---|---|
| 26.0.0_core_r0.12.1 | Y | Y | Y | / |
| 26.1.0_core_r0.12.1 | Y | Y | Y | Y |

**逐行解读**:
- `26.0.0_core_r0.12.1` 兼容 TorchNPU 7.2.0 / 7.3.0 / 26.0.0,**不兼容** 26.1.0——表明它发布时尚无 TorchNPU 26.1.0,因此不能与之配套。
- `26.1.0_core_r0.12.1` 对四列 TorchNPU 全部标 Y,即向下兼容至 7.2.0 同时向上覆盖到 26.1.0,兼容性窗口更宽。
- 单元格含义:`Y` = 可配套,`/` = 不可配套(原文 NOTE 中已说明)。

---

### 表 4(原文"表 3 MindSpeed Core 与 CANN 版本兼容")

| MindSpeed Core \ CANN | 8.3.RC1 | 8.5.0 | 9.0.0 | 9.1.0 |
|---|---|---|---|---|
| 26.0.0_core_r0.12.1 | Y | Y | Y | / |
| 26.1.0_core_r0.12.1 | Y | Y | Y | Y |

**逐行解读**:
- 26.0.0_core_r0.12.1 仅兼容到 CANN 9.0.0,9.1.0(`/`)尚未验证。
- 26.1.0_core_r0.12.1 对 CANN 8.3.RC1 / 8.5.0 / 9.0.0 / 9.1.0 全部兼容,横向覆盖四个 CANN 大版本,适合异构环境或滚动升级。
- 两个矩阵的行/列对应关系一致,可对照确认"MindSpeed Core ↔ CANN ↔ TorchNPU"三者的笛卡尔积是否被实际支持。

---

### 表 5(原文"配套文档")

| 文档名称 | 内容简介 | 更新说明 |
|---|---|---|
| 《MindSpeed快速入门》(../zh/user-guide/quickstart.md) | 介绍基于 MindSpeed 如何实现 Megatron-LM 在昇腾设备上的高效运行 | - |
| 《MindSpeed安装指导》(../zh/user-guide/install_guide.md) | 指导如何在 NPU 上基于 PyTorch 框架完成 MindSpeed 的安装,内容涵盖硬件与操作系统兼容性说明、驱动固件及 CANN 基础软件安装的完整安装流程,帮助用户快速搭建大模型分布式训练环境 | - |

**逐行解读**:
- 快速入门指向运行入口,需先完成 install_guide 的环境搭建。
- 安装指导是 changelog 的真正前置步骤:文档显式列出"硬件与操作系统兼容性、驱动固件、CANN 基础软件"三层依赖,需严格按此完成才能进入本版本(26.1.0_core_r0.12.1)的部署。"更新说明"列为 `-` 表示本次未单独标注变更。

---

### 表 6(原文"病毒扫描结果")

| 防病毒软件名称 | 防病毒软件版本 | 病毒库版本 | 扫描时间 | 扫描结果 |
|---|---|---|---|---|
| QiAnXin | 8.0.5.5260 | 2026-04-01 08:00:00.0 | 2026-07-06 | 无病毒,无恶意 |
| Kaspersky | 12.0.0.6672 | 2026-04-02 10:05:00 | 2026-07-06 | 无病毒,无恶意 |
| Bitdefender | 7.5.1.200224 | 7.100588 | 2026-07-06 | 无病毒,无恶意 |

**逐行解读**:三家厂商(国产 QiAnXin + 国际 Kaspersky / Bitdefender)在 2026-07-06 当天统一完成扫描,均无恶意成分,作为发布前的安全合规证据附在 changelog 末尾。

---

## 【公式解读】

**原文无公式。** 全文未出现 LaTeX 公式或伪代码表达式,本节无内容。

---

## 【关联】

- **配套文档关联**:本 changelog 在"配套文档"一节显式指向两条内部链接:
  - 《[MindSpeed快速入门](../zh/user-guide/quickstart.md)》——Megatron-LM 在昇腾上的运行入口,与本 release 配套使用,应作为使用本版本 26.1.0_core_r0.12.1 的首站阅读材料。
  - 《[MindSpeed安装指导](../zh/user-guide/install_guide.md)》——安装本版本的前置依赖(NPU 驱动、固件、CANN 基础软件)的标准流程,与表 1/表 2 的 CANN 9.1.0、TorchNPU 26.1.0、Python 3.10、PyTorch 2.7.1 形成"文档↔依赖矩阵"的闭环。
- **外部链接关联**:文档指向 Ascend/MindSpeed 在 gitcode 上的 26.1.0_core_r0.12.1 分支"分支维护策略",用于回答"维护周期 6 个月"具体含义。
- **特性间关联**:
  - "MXFP8-32x32 量化 + FSDP"与"删除 mindspeed/lite、Triton 算子迁移至 mindspeed/ops/triton"暗示算子目录在重构,后续新特性(Hamilton attention、w8a16)的算子实现预计都注册到新目录。
  - "DeepSeek V4 自定义 PP 布局"与 "SwapMuon / mcore muon" 在新增特性中并列出现,两者均涉及 checkpoint 保存/加载,提示该版本统一扩展了大规模训练的并行与恢复能力。
- **删除与替代关联**:删除 SFA/SFAG/SLI 临时算子由"正式算子"承载;删除 `mindspeed/lite` 后,Triton 算子统一收敛到 `mindspeed/ops/triton`。用户从旧版本升级时若有自研代码引用上述模块,需迁移路径(原文未给出迁移命令)。

---

## 【使用方法】

**原文未涉及具体的启用命令、配置项或脚本。** 本篇是 release notes,正文中并未提供启动训练或开启新特性(如 FP8/MXFP8/SwapMuon/DeepSeek V4 适配)的开关、环境变量或配置开关名;这些信息需要参考《MindSpeed快速入门》(`../zh/user-guide/quickstart.md》)与《MindSpeed安装指导》(`../zh/user-guide/install_guide.md》)获取。原文仅在"配套文档"小节告知用户:"用户可根据需要选择 MindSpeed 代码分支下载源码并进行安装"(即选择 `master` / `26.1.0_core_r0.12.1` / `26.0.0_core_r0.12.1` 之一,具体命令见安装指导)。
