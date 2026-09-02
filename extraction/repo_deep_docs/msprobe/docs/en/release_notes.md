# Release Notes

> 仓 `msprobe` · 路径 `docs/en/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprobe/docs/en/release_notes.md

# msprobe Release Notes 深度解读

## 【定位】
本文档是 msprobe（昇腾全场景精度工具链）官方 release notes，**集中声明各版本号对应的发布日期、Python/PyTorch/MindSpore 兼容矩阵、CANN 固件驱动依赖以及官方 wheel 包下载链接与 SHA-256 校验值**，用于帮助用户在做精度调测环境搭建前对齐软硬件依赖并校验下载完整性。

---

## 【技术要点】

1. **支持的 PyTorch 上游**：msprobe 要求 Ascend PyTorch **2.1.0 或更高版本**（即 PyTorch 2.1.0 起的 Ascend 适配版），版本对照需查阅 [Ascend Extension for PyTorch](https://gitcode.com/Ascend/pytorch)。
2. **支持的 MindSpore 上游**：msprobe 要求 MindSpore **2.4.0 或更高版本**，版本对照见 [MindSpore Version Release List](https://www.mindspore.cn/versions/en)。
3. **支持的 MSAdapter 版本**：msprobe 支持 **MSAdapter 2.1.0**。
4. **固件与驱动依赖**：msprobe 的固件/驱动版本**与 CANN 完全一致**，不另行规定，需从昇腾社区的 Firmware and Drivers 页面查询。
5. **Python 兼容范围（最新 alpha 版）**：**3.8 / 3.9 / 3.10 / 3.11 / 3.12**；早期 `26.0.0-alpha.1` 仅覆盖 3.8/3.9/3.10/3.11，未列 3.12。
6. **PyTorch 兼容范围（最新 alpha 版）**：**2.1 / 2.2 / 2.5 / 2.6 / 2.7 / 2.8 / 2.9**（注意 2.3、2.4 缺席）；早期 `alpha.1` 仅到 2.8，未含 2.9。
7. **MindSpore 兼容范围**：**2.4.0 / 2.5.0 / 2.6.0 / 2.7.1**（三个 alpha 版一致）。
8. **包命名与校验**：发布包统一为 `mindstudio_probe-<version>-py3-none-any.whl`，位于 `https://ptdbg.obs.cn-north-4.myhuaweicloud.com/msprobe/<version>/` 路径，并附带 SHA-256 校验码（64 位 hex）用于完整性核验。

---

## 【关键机制与数据】

- **版本演进路径（原文）**：
  - `26.0.0-alpha.1` → 发布日 **2026.2.4**
  - `26.0.0-alpha.2` → 发布日 **2026.3.2**
  - `26.0.0-alpha.3` → 发布日 **2026.4.8**
  - 三次迭代间隔约为 **1 个月**（2.4→3.2→4.8），属于高频 alpha 节奏。
- **数据流 / 工作原理（原文）**：本文档不涉及运行机制描述，仅声明依赖矩阵与下载物；具体的精度比对、dump、统计等数据流由 msprobe 其他功能模块（如 mindspore/pytorch adapter 与工具脚本）承担，本文未展开。
- **性能数据（原文）**：**未提供**任何 benchmark 数字、吞吐/延迟/显存占用等指标。

---

## 【表格解读】

下表为原文表格的**逐字还原**：

|       Version      |   Release Date  |       Supported Python Version      |         Supported PyTorch Version        |      Supported MindSpore Version     |                                                                          Download Link                                                                         |                               Checksum                               |
|:--------------:|:--------:|:----------------------:|:---------------------------:|:-----------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------:|
| 26.0.0-alpha.3 | 2026.4.8 | 3.8/3.9/3.10/3.11/3.12 | 2.1/2.2/2.5/2.6/2.7/2.8/2.9 | 2.4.0/2.5.0/2.6.0/2.7.1 | [mindstudio_probe-26.0.0a3-py3-none-any.whl](https://ptdbg.obs.cnorth-4.myhuaweicloud.com/msprobe/26.0.0/mindstudio_probe-26.0.0a3-py3-none-any.whl) | 073a07ac201e2e284f578c16ed524b36b5be98b4a5a60d8eaf5df46e7adad438 |
| 26.0.0-alpha.2 | 2026.3.2 | 3.8/3.9/3.10/3.11/3.12 | 2.1/2.2/2.5/2.6/2.7/2.8/2.9 | 2.4.0/2.5.0/2.6.0/2.7.1 | [mindstudio_probe-26.0.0a2-py3-none-any.whl](https://ptdbg.obs.cn-north-4.myhuaweicloud.com/msprobe/26.0.0/mindstudio_probe-26.0.0a2-py3-none-any.whl) | 6f84ebc8424841b3eb7e1c0a67d0cf4d1fbcb385185b8d208f9f47022559e9ce |
| 26.0.0-alpha.1 | 2026.2.4 |   3.8/3.9/3.10/3.11    |   2.1/2.2/2.5/2.6/2.7/2.8   | 2.4.0/2.5.0/2.6.0/2.7.1 | [mindstudio_probe-26.0.0a1-py3-none-any.whl](https://ptdbg.obs.cn-north-4.myhuaweicloud.com/msprobe/26.0.0/mindstudio_probe-26.0.0a1-py3-none-any.whl) | 52512b082dcb0a0c5de62684b770d24741b9aa0ab89c73763a882a8ded3ad8c3 |

> 注：原文中 alpha.3/alpha.2 的 PyTorch 列写为 `2.1/2.2/2.5/2.6/2.7/2.8/2.9`；上表已**逐字保留**该 7 段连写形式（未拆分）。

**逐行解读**：

- **行 1 — 26.0.0-alpha.3**：
  - 发布时间 **2026.4.8**，是当前表格中**最新**的 alpha 版本。
  - Python 支持最宽，新增了 **3.12**。
  - PyTorch 支持跨度最大，**首次新增 2.9**。
  - MindSpore 与前两个 alpha 一致（2.4.0 / 2.5.0 / 2.6.0 / 2.7.1）。
  - 下载对象 `mindstudio_probe-26.0.0a3-py3-none-any.whl`，校验码 `073a07ac…438`，用户可据此验证下载完整性。
- **行 2 — 26.0.0-alpha.2**：
  - 发布时间 **2026.3.2**，相较 alpha.1 在 Python 上**首次引入 3.12**，PyTorch 兼容矩阵与 alpha.3 完全一致（到 2.9），MindSpore 与其他版本相同。
  - 校验码 `6f84ebc8…9ce`。
- **行 3 — 26.0.0-alpha.1**：
  - 发布时间 **2026.2.4**，是表格中**最早**的 alpha 版本。
  - Python 仅覆盖到 **3.11**，未列 3.12。
  - PyTorch 上限为 **2.8**，未含 2.9。
  - 校验码 `52512b08…8c3`。

**横向共性 / 差异小结**：
- 三个 alpha 版本 **MindSpore 兼容矩阵完全相同**（2.4.0/2.5.0/2.6.0/2.7.1）。
- 包名前缀固定 `mindstudio_probe-`，平台 tag `py3-none-any`（纯 Python wheel，跨平台）。
- 三次迭代的核心变化是 **Python 与 PyTorch 兼容范围的扩展**（3.12、PyTorch 2.9 的引入），而 MindSpore 侧保持稳定。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档作为 release notes，处于 msprobe 文档体系的**版本元数据层**，与其上下游模块的关联如下：

- **上游兼容性文档**：
  - [Ascend Extension for PyTorch](https://gitcode.com/Ascend/pytorch) — 提供 msprobe 强依赖的 Ascend PyTorch 与 CANN 的对应关系。
  - [MindSpore Version Release List](https://www.mindspore.cn/versions/en) — 提供 msprobe 强依赖的 MindSpore 与 CANN 的对应关系。
  - 昇腾社区 **Firmware and Drivers** 页 — 提供 msprobe 间接依赖的固件/驱动版本（与 CANN 同版本）。
- **下游使用对象**：
  - msprobe 自身的 **PyTorch 适配模块**（依赖 Ascend PyTorch 2.1.0+）。
  - msprobe 自身的 **MindSpore 适配模块**（依赖 MindSpore 2.4.0+）。
  - **MSAdapter 2.1.0** — msprobe 作为其支持版本之一，需在 MSAdapter 调用链中保持对齐。
- **文档内链**：原文仅以 `<>` 形式占位了 Firmware and Drivers 跳转链接（未填实际 URL），故本文档**未提供其他内部 docs 之间的显式超链**，更多关系需结合仓库内 `docs/` 下的功能说明（如安装指南、API 参考）共同阅读。

---

## 【使用方法】

原文未涉及具体的命令行启用方式、API 调用示例或配置项写法。

但可基于原文直接派生出以下最小化使用流程（仅复述原文事实）：

1. **校验下载完整性**：使用 `sha256sum mindstudio_probe-<ver>-py3-none-any.whl` 与上表 Checksum 列比对。
2. **安装 wheel**：
   ```bash
   pip install mindstudio_probe-26.0.0a3-py3-none-any.whl
   ```
   （Python 版本需落入上表 Supported Python Version 列所列范围之一。）
3. **运行前环境对齐**：确保宿主已安装上表 Supported PyTorch Version / Supported MindSpore Version 中任一指定版本，并使 CANN 固件/驱动与之匹配（参考上述外部链接）。
4. **MSAdapter 配套**：若通过 MSAdapter 调用，需固定到 **2.1.0** 版本。

> 原文未给出 msprobe 自身的 `msprobe --help`、配置文件路径、API 入口或环境变量列表等具体启用指令，故更细粒度的使用方法**本文档未涉及**。
