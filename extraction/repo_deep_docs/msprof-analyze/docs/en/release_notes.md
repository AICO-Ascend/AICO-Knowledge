# Release Notes

> 仓 `msprof-analyze` · 路径 `docs/en/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprof-analyze/docs/en/release_notes.md

# msprof-analyze Release Notes 深度解读

## 【定位】

本文档是 MindStudio Profiler Analyze（`msprof-analyze`）的版本发布说明（changelog），用于明确工具与 AscendPyTorch、MindSpore、CANN、固件/驱动的版本兼容关系，并提供从 1.0 至 8.2.0 共 21 个历史版本的下载链接与校验码，以便用户按需下载并验证包完整性。

## 【技术要点】

1. **AscendPyTorch 兼容起点**：`msprof-analyze` 支持 AscendPyTorch **1.11.0 及以上**版本；PyTorch、CANN、Python 三者之间的具体版本映射关系需参考 Ascend Extension for PyTorch 仓。
2. **MindSpore 兼容起点**：`msprof-analyze` 支持 MindSpore **2.4.0 及以上**版本；MindSpore、CANN、Python 之间的版本映射关系需参考 MindSpore Release List。
3. **固件/驱动继承规则**：固件与驱动版本**等同于其所对应 CANN 软件包所支持的版本**，因此用户须先确定产品型号与 CANN 版本，再去 Ascend Community 的 Firmware and Drivers 页面获取配套固件与驱动。
4. **包格式**：所有发布产物均为 `msprof_analyze-<version>-py3-none-any.whl`，属于 Python 3 通用 wheel 包（`none-any` 表示与平台无关的纯 Python 包）。
5. **下载域分离**：8.x 版本使用 `ptdbg.obs.cn-north-4.myhuaweicloud.com`（华北-4 region），2.0.x / 1.x 版本使用 `ptdbg.obs.myhuaweicloud.com`（默认 region），两个 OBS 桶并存提供下载。
6. **完整性校验**：每个发行包均附带 **SHA256 校验码**（64 位十六进制字符串），用户下载后可校验哈希以确认包未被篡改或下载损坏。

## 【关键机制与数据】

**原文:** 本文档是一篇纯版本信息型 changelog，不描述具体的工作原理、数据流或性能数据。其信息可拆为三条主轴：

- **兼容矩阵轴**：`msprof-analyze ↔ AscendPyTorch ≥ 1.11.0`、`msprof-analyze ↔ MindSpore ≥ 2.4.0`、`固件/驱动 ↔ CANN ↔ 产品型号 ↔ 驱动版本`（示例：Firmware and Drivers URL 中给出了 `product=2&model=28&cann=8.0.RC3.alpha003&driver=1.0.25.alpha` 的查询参数）。
- **版本时间轴**：自 **2024-05-10（v1.0）首发**至 **2025-11-29（v8.2.0）**，跨度约 18 个月，期间共发布 21 个版本（含 v8.1.0 → v8.2.0 之间 4 个月间隔）。
- **命名演进**：版本号从 1.x → 2.0.x → 8.x，期间存在一次主版本号跳跃（从 2.0.2 直接到 8.1.0），未在原文中说明原因。

## 【表格解读】

原文包含一个核心表格《Release Package Download Links》，逐字还原如下：

| `msprof-analyze` Version | Release Date | Download Link | Checksum |
| --- | --- | --- | --- |
| 8.2.0 | 2025-11-29 | [msprof_analyze-8.2.0-py3-none-any.whl](https://ptdbg.obs.cn-north-4.myhuaweicloud.com/profiler/package/8.2.0/msprof_analyze-8.2.0-py3-none-any.whl) | 82e29632cb0b4445f631b0434e1e2be17c89d1b444938dbd4da38450aa4c5fc8 |
| 8.1.0 | 2025-07-30 | [msprof_analyze-8.1.0-py3-none-any.whl](https://ptdbg.obs.cn-north-4.myhuaweicloud.com/profiler/package/8.1.0/msprof_analyze-8.1.0-py3-none-any.whl) | 064f68ff22c88d91d8ec8c47045567d030d1f9774169811c618c06451ef697e4 |
| 2.0.2 | 2025-03-31 | [msprof_analyze-2.0.2-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/2.0.2/msprof_analyze-2.0.2-py3-none-any.whl) | 4227ff628187297b2f3bc14b9dd3a8765833ed25d527f750bc266a8d29f86935 |
| 2.0.1 | 2025-02-28 | [msprof_analyze-2.0.1-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/2.0.1/msprof_analyze-2.0.1-py3-none-any.whl) | 82dfe2c779dbab9015f61d36ea0c32d832b6d182454b3f7db68e6c0ed49c0423 |
| 2.0.0 | 2025-02-08 | [msprof_analyze-2.0.0-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/2.0.0/msprof_analyze-2.0.0-py3-none-any.whl) | 8e44e5f3e7681c377bb2657a600ad9841d3bed11061ddd7844c30e8a97242101 |
| 1.3.4 | 2025-01-20 | [msprof_analyze-1.3.4-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.3.4/msprof_analyze-1.3.4-py3-none-any.whl) | 8de92188d1a97105fb14cadcb0875ccd5f66629ee3bb25f37178da1906f4cce2 |
| 1.3.3 | 2024-12-26 | [msprof_analyze-1.3.3-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.3.3/msprof_analyze-1.3.3-py3-none-any.whl) | 27676f2eee636bd0c65243f81e292c7f9d30d7f985c772ac9cbaf10b54d3584e |
| 1.3.2 | 2024-12-20 | [msprof_analyze-1.3.2-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.3.2/msprof_analyze-1.3.2-py3-none-any.whl) | ceb227e751ec3a204135be13801f1deee6a66c347f1bb3cdaef596872874df06 |
| 1.3.1 | 2024-12-04 | [msprof_analyze-1.3.1-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.3.1/msprof_analyze-1.3.1-py3-none-any.whl) | eae5548804314110a649caae537f2c63320fc70ec41ce1167f67c1d674d8798e |
| 1.3.0 | 2024-10-12 | [msprof_analyze-1.3.0-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.3.0/msprof_analyze-1.3.0-py3-none-any.whl) | 8b09758c6b5181bb656a95857c32852f898c370e7f1041e5a08e4f10d5004d48 |
| 1.2.5 | 2024-09-25 | [msprof_analyze-1.2.5-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.2.5/msprof_analyze-1.2.5-py3-none-any.whl) | aea8ae8deac07b5b4980bd2240da27d0eec93b9ace9ea9eb2e3a05ae9072018b |
| 1.2.4 | 2024-09-19 | [msprof_analyze-1.2.4-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.2.4/msprof_analyze-1.2.4-py3-none-any.whl) | 7c392e72c3347c4034fd3fdfcccb1f7936c24d9c3eb217e2cc05bae1347e5ab7 |
| 1.2.3 | 2024-08-29 | [msprof_analyze-1.2.3-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.2.3/msprof_analyze-1.2.3-py3-none-any.whl) | 354a55747f64ba1ec6ee6fe0f05a53e84e1b403ee0341ec40cc216dd25fda14c |
| 1.2.2 | 2024-08-23 | [msprof_analyze-1.2.2-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.2.2/msprof_analyze-1.2.2-py3-none-any.whl) | ed92a8e4eaf5ada8a2b4079072ec0cc42501b1b1f2eb00c8fdcb077fecb4ae02 |
| 1.2.1 | 2024-08-14 | [msprof_analyze-1.2.1-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.2.1/msprof_analyze-1.2.1-py3-none-any.whl) | 7acd477417bfb3ea29029dadf175d019ad3212403b7e11dc1f87e84c2412c078 |
| 1.2.0 | 2024-07-25 | [mspdf_analyze-1.2.0-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.2.0/msprof_analyze-1.2.0-py3-none-any.whl) | 6a4366e3beca40b4a8305080e6e441d6ecafb5c05489e5905ac0265787555f37 |
| 1.1.2 | 2024-07-12 | [msprof_analyze-1.1.2-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.1.2/msprof_analyze-1.1.2-py3-none-any.whl) | af62125b1f9348bf491364e03af712fc6d0282ccee3fb07458bc9bbef82dacc6 |
| 1.1.1 | 2024-06-20 | [msprof_analyze-1.1.1-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.1.1/msprof_analyze-1.1.1-py3-none-any.whl) | 76aad967a3823151421153d368d4d2f8e5cfbcb356033575e0b8ec5acea8e5e4 |
| 1.1.0 | 2024-05-28 | [msprof_analyze-1.1.0-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.1.0/msprof_analyze-1.1.0-py3-none-any.whl) | b339f70e7d1e45e81f289332ca64990a744d0e7ce6fdd84a8d82e814fa400698 |
| 1.0 | 2024-05-10 | [msprof_analyze-1.0-py3-none-any.whl](https://ptdbg.obs.myhuaweicloud.com/profiler/package/1.0/msprof_analyze-1.0-py3-none-any.whl) | 95b2f41c8c8e8afe4887b738c8cababcb4f412e1874483b6adae4a025fcbb7d4 |

逐行解读：

| 版本 | 发布日期 | 解读 |
|---|---|---|
| 8.2.0 | 2025-11-29 | 表格中最新版本，使用华北-4 桶；checksum 前缀 `82e296…`，与 2.0.1 同前缀但内容不同。 |
| 8.1.0 | 2025-07-30 | 8.x 系列首发版本，使用华北-4 桶；与 8.2.0 间隔约 4 个月。 |
| 2.0.2 | 2025-03-31 | 2.x 系列最后一个版本，使用默认桶；与后续 8.1.0 间隔近 4 个月，可能对应 CANN 8.x 系列配套。 |
| 2.0.1 | 2025-02-28 | 2.0.0 的首个补丁版；checksum `82dfe2c…`。 |
| 2.0.0 | 2025-02-08 | 2.x 主版本首发，标志着从 1.x 跨入 2.x。 |
| 1.3.4 | 2025-01-20 | 1.3.x 系列最后一个版本，发布于 2025 年初。 |
| 1.3.3 | 2024-12-26 | 仅距 1.3.2 6 天的快速补丁。 |
| 1.3.2 | 2024-12-20 | 1.3.1 后的又一次补丁。 |
| 1.3.1 | 2024-12-04 | 1.3.0 后的快速跟进。 |
| 1.3.0 | 2024-10-12 | 1.3 主版本首发，距 1.2.5 约 17 天，是一次较快的功能演进。 |
| 1.2.5 | 2024-09-25 | 1.2.x 的最后一个补丁版本。 |
| 1.2.4 | 2024-09-19 | 1.2.3 后的 6 天补丁。 |
| 1.2.3 | 2024-08-29 | 1.2.2 后 6 天补丁，反映发布节奏密集。 |
| 1.2.2 | 2024-08-23 | 1.2.1 后 9 天补丁。 |
| 1.2.1 | 2024-08-14 | 1.2.0 后 20 天的首个补丁。 |
| 1.2.0 | 2024-07-25 | 1.2 主版本首发。 |
| 1.1.2 | 2024-07-12 | 1.1.x 系列末版。 |
| 1.1.1 | 2024-06-20 | 1.1.0 后的 23 天补丁。 |
| 1.1.0 | 2024-05-28 | 1.1 主版本首发，距 1.0 仅 18 天。 |
| 1.0 | 2024-05-10 | 项目首个 GA 版本，checksum `95b2f41c…`。 |

**列定义解读**：
- **`msprof-analyze` Version**：语义化版本号（MAJOR.MINOR.PATCH），1.0 例外仅含单段。
- **Release Date**：ISO 8601 短日期格式（YYYY-MM-DD）。
- **Download Link**：OBS 对象存储上的 wheel 包直链，路径模板 `profiler/package/<version>/msprof_analyze-<version>-py3-none-any.whl`。
- **Checksum**：64 位十六进制 SHA256 哈希值，用于完整性校验。

## 【公式解读】

原文无公式。

## 【关联】

本文档自身不引用仓内其他模块链接（内部链接: 无），仅通过外部链接建立了与上下游生态的依赖与配套关系：

- **上游框架**：
  - [Ascend Extension for PyTorch](https://gitcode.com/Ascend/pytorch) — 提供 AscendPyTorch 的版本映射，是 PyTorch 兼容性查询的源头。
  - [MindSpore Release List](https://www.mindspore.cn/versions/en) — 提供 MindSpore 的版本映射，是 MindSpore 兼容性查询的源头。
- **底层硬件/CANN**：
  - [Firmware and Drivers 页面](https://www.hiascend.com/hardware/firmware-drivers/community?product=2&model=28&cann=8.0.RC3.alpha003&driver=1.0.25.alpha) — Ascend Community 上的固件/驱动下载入口，URL 中的 `product=2&model=28&cann=8.0.RC3.alpha003&driver=1.0.25.alpha` 查询参数表明其按"产品族 → 型号 → CANN 版本 → 驱动版本"四级过滤。
- **包存储（CDN/OBS）**：
  - `https://ptdbg.obs.cn-north-4.myhuaweicloud.com/profiler/...` — 8.x 版本存放桶（华北-4 region）。
  - `https://ptdbg.obs.myhuaweicloud.com/profiler/...` — 1.x / 2.0.x 版本存放桶（默认 region）。

整张关联图可概括为：`msprof-analyze wheel` ↔ `MindStudio Profiler` ↔ `AscendPyTorch / MindSpore` ↔ `CANN` ↔ `Firmware/Driver` ↔ `Ascend 硬件`，文档是这条链路中的"包分发与兼容性"节点。

## 【使用方法】

原文未涉及具体的启用命令、配置项或 API 调用方式；其内容仅限于：

1. **下载**：从表格对应行的 `Download Link` 列点击或使用 `wget`/`curl` 获取 `msprof_analyze-<version>-py3-none-any.whl`。
2. **校验**：使用 `sha256sum msprof_analyze-<version>-py3-none-any.whl` 比对表格 `Checksum` 列的 64 位十六进制值。
3. **安装（推断为标准 Python wheel 操作，原文未直接给出）**：`pip install msprof_analyze-<version>-py3-none-any.whl`。
4. **版本选型**：根据使用的 AscendPyTorch（≥ 1.11.0）或 MindSpore（≥ 2.4.0）以及所对应 CANN 版本，从 Firmware and Drivers 页面拉取匹配固件/驱动，再安装配套的 `msprof-analyze` wheel。

具体的 CLI 命令、子命令、配置参数等使用细节需参考仓内其他文档（原 release notes 未提供）。
