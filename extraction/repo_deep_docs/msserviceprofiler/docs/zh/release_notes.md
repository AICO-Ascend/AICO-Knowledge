# 版本说明

> 仓 `msserviceprofiler` · 路径 `docs/zh/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/docs/zh/release_notes.md

# 一体化深度解读：msserviceprofiler Release Notes

---

## 【定位】

本文档是 MindStudio-Service-Profiler（msserviceprofiler）推理服务化性能数据采集工具的**版本发布说明（changelog）**，用于记录已发布版本号、发布时间、Tag、兼容的昇腾 CANN 版本范围，并提供对应安装包的 MD5 校验值，**目的是为使用者提供版本溯源、兼容性核对与安装包完整性验证的依据**。

---

## 【技术要点】

1. **两个发布版本并存**：当前文档包含 `26.0.T2.B100_001`（正式/稳定 Tag，2026/04/07）与 `26.0.0-alpha.1`（Alpha 预发布版本，2026/02/06）两个版本。
2. **Tag 命名规范**：完整发布 Tag 分别为 `tag_MindStudio_26.0.T2.B100_001` 与 `tag_MindStudio_26.0.0-alpha.1`，遵循"tag_MindStudio_<版本号>"模式。
3. **兼容性约束**：两个版本均明确声明**兼容昇腾 CANN 8.5.0 及以前版本**，并以外部链接指向 `https://www.hiascend.com/cann` 获取 CANN 安装包。
4. **安装包双格式分发**：
   - 正式版 `26.0.T2.B100_001` 使用 `.run` 离线安装包形式分发；
   - Alpha 版 `26.0.0-alpha.1` 使用 `.whl`（Python wheel）包形式分发。
5. **CPU 架构双覆盖**：两个版本均提供 `aarch64`（ARM）与 `x86_64` 两种架构的安装包，确保在不同硬件平台上的可部署性。
6. **附属组件包**：`26.0.0-alpha.1` 除主包 `ms_service_profiler` 外，还附带一个独立发布的辅助包 `ms_serviceparam_optimizer-26.0.0a1-py3-none-any.whl`（架构无关的纯 Python 包）。

---

## 【关键机制与数据】

原文无性能数据或运行机制描述，仅记录版本元信息（版本号/日期/Tag/兼容性/MD5）。**无工作原理、数据流或性能指标可解读**。

---

## 【表格解读】

### 表格 1：发布版本清单（原文逐字还原）

| 发布版本         | 发布时间   | 发布Tag                          | 兼容性说明                                                                                                            |
| ---------------- | ---------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 26.0.T2.B100_001 | 2026/04/07 | tag_MindStudio_26.0.T2.B100_001  | 兼容昇腾CANN 8.5.0及以前版本。请参见[CANN安装指南](https://www.hiascend.com/cann)获取CANN安装包。                     |
| 26.0.0-alpha.1   | 2026/02/06 | tag_MindStudio_26.0.0-alpha.1    | 兼容昇腾CANN 8.5.0及以前版本。请参见[CANN安装指南](https://www.hiascend.com/cann)获取CANN安装包。                     |

**逐行解读**：
- **第 1 行（26.0.T2.B100_001）**：正式 Tag 版本，按"YY.T.Build.Revision"四段式编号策略发布；Tag 后缀 `_001` 表明这是该 T2.B100 基线的首个正式发布；发布日期晚于 alpha 版约两个月，**说明其属于 alpha 之后的稳定/正式迭代**。
- **第 2 行（26.0.0-alpha.1）**：采用语义化版本（SemVer）的预发布标识 `-alpha.1`，明确标识为非稳定预发布版本；时间最早（2026/02/06），是该轮迭代的首发版本。
- **兼容性列**：两版兼容范围一致，均限定为"昇腾 CANN 8.5.0 及以前"，意味着两版在同一 CANN 生态下可互换部署；兼容性说明均通过外链 `https://www.hiascend.com/cann` 引导用户查阅 CANN 安装指引。

---

### 表格 2：26.0.T2.B100_001 安装包 MD5（原文逐字还原）

| 文件名 | MD5 |
| --- | --- |
| `mindstudio-service-profiler_26.0.0_aarch64.run` | `bae649cdb94c376d8aa2ebb83adef18f` |
| `mindstudio-service-profiler_26.0.0_x86_64.run` | `8e71fb58717c79b34b9591411eb41078` |

**逐行解读**：
- **第 1 行**：正式版的 ARM64 架构 `.run` 离线安装包，包内版本号字段写作 `26.0.0`（而非外部 Tag 的 `26.0.T2.B100_001`），**说明 `.run` 安装包内部版本号与对外 Tag 采用了不同编号体系**；MD5 用于校验文件完整性。
- **第 2 行**：正式版的 x86_64 架构 `.run` 安装包，命名规则与 aarch64 完全对称，**仅架构标识不同**，便于在两类服务器上部署同一功能组件。

---

### 表格 3：26.0.0-alpha.1 安装包 MD5（原文逐字还原）

| 文件名 | MD5 |
| --- | --- |
| `ms_service_profiler-26.0.0a1-py3-none-linux_aarch64.whl` | `6111275d0653b4d7153a4268969dccd6` |
| `ms_service_profiler-26.0.0a1-py3-none-linux_x86_64.whl` | `c26ff021957dc400a593350856b381ea` |
| `ms_serviceparam_optimizer-26.0.0a1-py3-none-any.whl` | `9050b01a0dfd7b2abc32208199911c3b` |

**逐行解读**：
- **第 1 行**：Alpha 版主包（ms_service_profiler）的 ARM64 平台 wheel 包，文件名遵循 PEP 491 规范 `pkg-version(-prerelease)-pyX-none-<platform>.whl`，可解读为"包名 `ms_service_profiler`，版本 `26.0.0a1`（alpha 标记），Python 3，无 ABI 限制，仅限 linux aarch64 平台"。
- **第 2 行**：与第 1 行同包同版本，但目标平台为 linux x86_64，**命名规范一致以保证跨架构一致的使用方式**。
- **第 3 行**：附属包 `ms_serviceparam_optimizer`（服务参数优化器）的 wheel 包，文件名中 `none-any` 表示**纯 Python 实现、不绑定 ABI、不绑定平台**，可跨架构通用安装，**说明该组件与硬件架构解耦**，是更高层的可移植工具。

---

## 【公式解读】

原文无公式。**原文无公式**。

---

## 【关联】

本文档内容本身**未提供内部链接**，但基于文档可推断以下外部/上下游依赖：
- **上游兼容性依赖**：CANN（昇腾 CANN）8.5.0 及以前版本，外部参考链接为 `https://www.hiascend.com/cann`；msserviceprofiler 需运行在已安装指定版本 CANN 的昇腾硬件（aarch64/x86_64 主机）之上。
- **配套组件关联**：Alpha 版同时发布 `ms_serviceparam_optimizer` 包，表明在 alpha 阶段 msserviceprofiler 与服务参数优化器**协同打包/同步发布**，二者构成性能数据采集与分析的组合工具集。
- **包形式演进关联**：从 alpha（`.whl` Python wheel）到正式版（`.run` 离线安装包），**说明发布流程从开发期 Python 包形式向生产期离线打包形式过渡**，与版本成熟度递进相对应。

---

## 【使用方法】

- **安装包完整性校验**：用户可使用文档中提供的 MD5 值（如 `bae649cdb94c376d8aa2ebb83adef18f`、`8e71fb58717c79b34b9591411eb41078`、`6111275d0653b4d7153a4268969dccd6`、`c26ff021957dc400a593350856b381ea`、`9050b01a0dfd7b2abc32208199911c3b`）**自行校验下载文件的完整性**。
- **CANN 版本对齐**：部署前需确认环境中已安装**昇腾 CANN 8.5.0 或更早版本**，否则可能存在兼容性问题；安装包获取方式见 `https://www.hiascend.com/cann`。
- **架构选型**：根据主机 CPU 架构选择 `aarch64`（ARM 服务器）或 `x86_64`（x86 服务器）对应的安装包文件。
- **正式版 vs Alpha 版选型**：生产环境建议选用 `26.0.T2.B100_001`（2026/04/07，`.run` 包）；试用体验可选 `26.0.0-alpha.1`（2026/02/06，`.whl` 包）。

原文未涉及具体命令行启动方式、采集开关配置项或 API 调用方法。
