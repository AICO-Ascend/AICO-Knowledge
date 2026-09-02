# Version Mapping

> 仓 `multimodalsdk` · 路径 `docs/en/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/multimodalsdk/docs/en/release_notes.md

# 深度解读: Multimodal SDK 26.0.0 Release Notes

## 【定位】
本篇文档描述了 Multimodal SDK 26.0.0 这一首版(Release)发布物的**产品版本映射、依赖兼容性、新增能力清单与升级影响**,作为该版本面向 Atlas 800I A2 推理服务器的发布声明与配套文档入口。

---

## 【技术要点】

1. **Tensor 类双向互转**: 新增自定义 `Tensor` 类,支持与 `numpy.ndarray` 和 `torch.Tensor` 双向转换 —— 建立 Python 多模态生态与原生 SDK 数据结构之间的桥梁层。
2. **Image 类多源互转 + 几何变换**: 新增自定义 `Image` 类,支持与 `numpy`、`torch.Tensor`、PIL Image 三种主流图像表示**双向**互转,且原生支持 `resize`(缩放)与 `crop`(裁剪)操作。
3. **多媒体解码能力成体系**: 新增 `video decoding`(视频解码)与 `audio decoding`(音频解码)两条并行管线,使 SDK 从单一图像工具扩展为"视/音/图"三模态接入层。
4. **Tensor 对象归一化**: 新增 `tensor object normalization`(张量对象归一化),为多源数据统一数值尺度提供内建支持。
6. **日志注册机制**: 新增 `log registration`(日志注册),为上层应用提供可观测性接入点。
7. **运行环境锁定**: 配套依赖固定为 Ascend HDK 26.0.RC1 + CANN 9.0.0(及其 patch 版本),且声明**无任何兼容性破坏**(no compatibility issues)。

---

## 【关键机制与数据】

- **原文:** "This release has no compatibility issues." —— 表示 26.0.0 的发布对既有功能无破坏性变更。
- **原文:** "Software version compatibility means that when the product software version is upgraded, other related software does not need to be upgraded or patched at the same time, and existing functions remain supported." —— 明确"软件版本兼容"的判定标准:升级时相关软件无需同步升级/打补丁,既有功能仍受支持。
- **数据流视角**(基于原文罗列能力还原,不做臆造): 外部数据源 (`numpy` / `torch.Tensor` / PIL / `音频流` / `视频流`) → Multimodal SDK 自定义 `Tensor` / `Image` 对象(可进行归一化、resize、crop) → 交由依赖层 CANN 9.0.0 + Ascend HDK 26.0.RC1 调度到 Atlas 800I A2 推理服务器执行。
- **性能数据**: 原文未提供吞吐量、时延、精度等量化指标。
- **Bug/漏洞数据**: 原文明确"Resolved Issues: None"、"Known Issues: None"、"Fixed Vulnerabilities: None"。

---

## 【表格解读】

### 表 1 · Product Version Mapping(逐字还原)

| Product Name | Product Version | Version Type |
|---|---|---|
| Multimodal SDK | 26.0.0 | Release version |

**逐行解读:**
- **Product Name = Multimodal SDK**: 本次发布的产品名称,与本文档标题一致。
- **Product Version = 26.0.0**: 本次发布的版本,采用 `<主版本.次版本.修订>` 三段式编号,且为 `26` 大版本的首个 Release 版本。
- **Version Type = Release version**: 表示这是正式发布版本(而非 RC/Beta/Alpha),意味着用户可在业务环境采用。

---

### 表 2 · Related Product Versions(逐字还原)

| Product Name | Version |
|---|---|
| Ascend HDK | 26.0.RC1 |
| CANN | 9.0.0 |

**逐行解读:**
- **Ascend HDK 26.0.RC1**: 硬件驱动与固件栈版本为 `26.0.RC1`,与 Multimodal SDK 处于同一大版本号体系(`26.0.x`),但 HDK 仍处于 RC(候选发布)阶段。
- **CANN 9.0.0**: 昇腾计算架构(CANN)主版本为 `9.0.0`,与 SDK 的 `26.0.0` 处于不同的版本号体系,需通过"配套关系表"确认对应。

---

### 表 3 · Software Version Compatibility(逐字还原,原文标注为 **Table 1**)

| Multimodal SDK Software Version | Multimodal SDK Versions to Upgrade | CANN Version Compatibility | Ascend HDK Version Compatibility |
|---|---|---|---|
| Multimodal SDK 26.0.0 | Not applicable | CANN 9.0.0 and patch version | Ascend HDK 26.0.RC1 and patch version |

**逐行解读:**
- **Multimodal SDK Software Version = Multimodal SDK 26.0.0**: 当前发布的 SDK 版本。
- **Multimodal SDK Versions to Upgrade = Not applicable**: 因是首版 Release,无需"自旧版本升级"路径;此处"No applicable"指无前置版本可被升级至此。
- **CANN Version Compatibility = CANN 9.0.0 and patch version**: SDK 26.0.0 兼容 CANN 9.0.0 主版本及其后续 patch 版本。
- **Ascend HDK Version Compatibility = Ascend HDK 26.0.RC1 and patch version**: SDK 26.0.0 兼容 Ascend HDK 26.0.RC1 主版本及其后续 patch 版本。

---

### 表 4 · New Features(逐字还原)

| Feature Name | Feature Description | Supported Product Model |
|---|---|---|
| Multimodal SDK | <ul><li>Adds a custom `Tensor` class that supports bidirectional conversion with `numpy` and `torch.Tensor`.</li><li>Adds a custom `Image` class that supports bidirectional conversion with `numpy`, `torch.Tensor`, and PIL images, and supports image resizing and cropping.</li><li>Adds support for log registration.</li><li>Adds support for video decoding.</li><li>Adds support for tensor object normalization.</li><li>Adds support for audio decoding.</li></ul> | Atlas 800I A2 inference server |

**逐行解读:**
- **Feature Name = Multimodal SDK**: 本次 Feature 行项统一归属于产品本身,而非子模块。
- **Feature Description(六条新增能力,逐条解读)**:
  - ① `Tensor` ↔ `numpy` / `torch.Tensor` **双向**转换:打通 Python AI 栈两大主流张量表示。
  - ② `Image` ↔ `numpy` / `torch.Tensor` / **PIL Image** 双向转换 + 原生 `resize` / `crop`:在图像域进一步覆盖计算机视觉生态最常用的 PIL 表示,并把预处理几何操作内建到 SDK。
  - ③ **log registration**(日志注册):为可观测性提供注册入口。
  - ④ **video decoding**(视频解码):扩展模态由"静态图像"到"视频流"。
  - ⑤ **tensor object normalization**(张量归一化):内建数值尺度统一能力,降低用户预处理负担。
  - ⑥ **audio decoding**(音频解码):与视频解码并列,使 SDK 覆盖"视+音"双通道输入。
- **Supported Product Model = Atlas 800I A2 inference server**: 本版本能力所对应的硬件载体,目前仅在 Atlas 800I A2 推理服务器上获得支持。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **硬件依赖**: 文档通过"Related Product Versions"与"Software Version Compatibility"两个表,将 Multimodal SDK 26.0.0 锚定到 **Ascend HDK 26.0.RC1** 与 **CANN 9.0.0**,三者构成完整的运行时栈(驱动 + 加速库 + 多模态 SDK)。
- **下游文档入口**: 文档末尾"26.0.0 Documentation"小节给出唯一一篇配套文档链接 `./installation_guide.md`(Multimodal SDK 26.0.0 User Guide),内容覆盖**安装部署、应用开发流程、Python API 说明**;读者若需了解任何一条新增能力(`Tensor` / `Image` / 日志注册 / 视频解码 / 音频解码 / 归一化)的具体 API 用法,必须跳转至该 User Guide。
- **能力组合关系**: 文档内部将新增能力按"对象(`Tensor`、`Image`)+ 能力方法(resize、crop、normalization)+ 输入源(numpy、torch、PIL、视频、音频)+ 横切关注点(日志)"分层罗列,可推断 SDK 的 API 形态很可能围绕 `Tensor`、`Image` 两个核心类展开,其余能力作为类内方法或独立模块挂载。
- **升级/迁移路径**: "Versions to Upgrade = Not applicable" + "Impact on the System during/After the Upgrade = None" 表明这是首版 Release,**不存在**升级路径与升级影响,也不涉及已修复漏洞或已知问题。

---

## 【使用方法】

原文未涉及具体的启用方式、配置项或命令(本文档仅声明"新增了什么",而**如何调用**这些能力需参见 `./installation_guide.md` User Guide,原文未在本文件给出 API、CLI 或配置样例)。
