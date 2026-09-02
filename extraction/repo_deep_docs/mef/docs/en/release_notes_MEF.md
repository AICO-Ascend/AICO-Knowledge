# Version Mapping Description<a name="ZH-CN_TOPIC_0000002492283802"></a>

> 仓 `mef` · 路径 `docs/en/release_notes_MEF.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mef/docs/en/release_notes_MEF.md

# MEF 26.0.0 Release Notes 深度解读

## 【定位】

本文档是 MEF（边缘AI业务使能框架）**首个开源版本 26.0.0 的版本配套说明（Version Mapping Description）**，明确该版本与 Ascend HDK 9.0.0（26.0.RC1）和 CANN 9.0.0 的配套关系，并集中罗列首发版本所提供的新特性范围。

## 【技术要点】

- **产品版本**：MEF 26.0.0，类型为 **Release Version**（首发版本）。
- **配套依赖**：
  - **Ascend HDK = 26.0.RC1**
  - **CANN = 9.0.0**
- **版本兼容性说明**：本文明确"**The first open-source version does not involve version upgrades.**"，即本次为首个开源发布，不存在从更早商用版本升级的场景。
- **病毒扫描**：Virus scan passed（安全检查通过）。
- **首发特性范围（5 项）**：
  1. 云侧管理边节点（cloud-side management of edge nodes）
  2. 边节点 onboarding + 容器化应用生命周期管理
  3. 云边一体的告警与事件管理
  4. 云边组件升级能力
  5. 云侧 [API 接口](./user_guide/RESTful.md)
- **其余子章节**（Service Interface Changes / Key Feature Changes / Resolved Issues / Known Issues / Upgrade Impact / Vulnerability Patch List）均标注 **None**——表明这是一份"基线发布"型说明，不涉及差分变更。

## 【关键机制与数据】

原文未给出任何性能数据、量化指标或运行时数据流，仅提供：

- 原文："**The first open-source version does not involve version upgrades.**" —— 表明该版本是开源基线，不存在升级路径上的兼容性负担。
- 原文注释 NOTE：「Software version compatibility means that when the product software version is upgraded, other associated software does not need to be upgraded or patched simultaneously and can still support existing functions.」—— 给出 MEF 对"版本兼容"的官方定义，但当前版本并不触发该条款。
- 原文："**Virus scan passed.**" —— 发布包病毒扫描结论。

## 【表格解读】

原文共包含 **3 张表格**，逐字还原并逐行解读如下。

### 表 1：Product Version Information（产品版本信息表）

| Product Name | Product Version | Version Type |
|---|---|---|
| MEF | 26.0.0 | Release Version |

**逐行解读**：

- **Product Name = MEF**：明确本说明文档所对应的产品实体是 MEF 这一边云协同框架。
- **Product Version = 26.0.0**：该版本号采用"年.次.修订"风格的语义化编号（26 表示 2026 年），是首个被开源社区可见的稳定基线。
- **Version Type = Release Version**：区别于 RC/Beta/Alpha，表示该版本作为 GA（正式发布）对外可用。

### 表 2：Related Product Version Mapping Description（关联产品版本配套说明表）

| Product Name | Version |
|---|---|
| Ascend HDK | 26.0.RC1 |
| CANN | 9.0.0 |

**逐行解读**：

- **Ascend HDK = 26.0.RC1**：MEF 26.0.0 适配的底层硬件开发套件版本为 26.0.RC1（注意带 `RC1` 后缀，是 Release Candidate 而非 GA，提示用户 MEF 自身首发时其依赖的 HDK 仍处候选阶段）。
- **CANN = 9.0.0**：MEF 26.0.0 适配的昇腾异构计算架构版本为 CANN 9.0.0（与 HDK 主版本号 26 存在差异，说明 MEF 与 CANN 的版本号体系是独立的，但需在该组合下验证可用）。
- **配套关系**：MEF 作为上层"边云协同平台"框架，向下层对接 Ascend HDK（驱动/固件层）与 CANN（算子/运行时层），构成"端边云"中的"边云"层。

### 表 3：Version Mapping Document（版本映射文档清单表）

| Document Name | Content Description | Release Notes |
|---|---|---|
| [MEF](https://gitcode.com/Ascend/MEF) | Introduces MEF-related functions and usage, and provides detailed interface descriptions. | None |

**逐行解读**：

- **Document Name**：指向 `gitcode.com/Ascend/MEF`，即 MEF 在 gitcode 平台的开源仓库地址，作为该版本的源码与文档主入口。
- **Content Description**：说明该文档（仓库）覆盖"MEF 相关功能与使用方法，并提供详细接口描述"——即功能介绍 + 用户指南 + API 描述三层内容。
- **Release Notes = None**：本子表无附加变更说明，符合本版本作为首发基线的特性。

## 【公式解读】

原文无公式。

## 【关联】

依据原文可识别的关联关系：

- **依赖关系（向下）**：MEF 26.0.0 显式依赖 Ascend HDK 26.0.RC1 与 CANN 9.0.0，构成"HDK / CANN → MEF"的下层依赖链。MEF 作为上层框架，依托 Ascend 生态提供边端算力与异构计算能力。
- **云边协同定位**：原文新特性 1/3/4（cloud-side 边节点管理、云边告警事件、云边组件升级）均体现"云"对"边"的管理能力；特性 2/5（边节点容器 onboarding + 容器化应用生命周期、云侧 API）则体现"边"端的容器化承载与"云"端的控制面接口。
- **接口文档链接**：原文新特性第 5 条「Offers cloud-side API interfaces」配套超链接 `./user_guide/RESTful.md`，指向 RESTful 接口用户指南——意味着该版本的"云侧 API"以 **RESTful 形式**对外暴露，是 MEF 与上层业务平台对接的契约来源。
- **开源仓入口**：通过表 3 指向 `https://gitcode.com/Ascend/MEF`，为后续 issue/PR/版本演化的上游入口。
- **基线版本含义**：原文反复以 "None" 标识各变更/影响/补丁子节，并明确"首个开源版本不涉及版本升级"，表明本文档定义的是 MEF 在开源生态的 **起点基线**，后续版本将在此基线上叠加差异变更。

## 【使用方法】

原文未涉及具体的启用方式、配置项或命令。

（本文档仅给出版本配套与特性清单，未提供安装步骤、参数配置或操作命令；具体使用方式需参照文末链接 `https://gitcode.com/Ascend/MEF` 仓库以及 `./user_guide/RESTful.md` 接口指南。）
