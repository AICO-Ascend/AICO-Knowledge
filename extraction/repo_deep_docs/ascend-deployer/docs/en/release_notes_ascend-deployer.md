# Release Notes

> 仓 `ascend-deployer` · 路径 `docs/en/release_notes_ascend-deployer.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascend-deployer/docs/en/release_notes_ascend-deployer.md

# 深度解读：MindCluster Ascend Deployer 26.0.0 Release Notes

## 【定位】

本文档是 **MindCluster Ascend Deployer 26.0.0** 的版本发布说明（Release Notes），用于说明该版本的产品版本信息、配套组件版本映射、软件兼容矩阵、新增能力、升级影响以及同步附带的下载源迁移说明，作为本次发版的变更基线和配套查阅入口。

---

## 【技术要点】

1. **下载源迁移**：MindCluster 7.3.0 与 26.0.0 版本在 GitCode releases 上发布的"集群调度组件"的默认下载源，由 **Huawei Cloud OBS** 迁移至 **GitCode**；TorchNPU 的 **15 个版本、共 104 个 wheel 包**的默认下载源同样迁移到 GitCode。包名、SHA256 校验值、离线部署目录均保持不变。
2. **网络放通要求**：若出网受防火墙/白名单控制，从 GitCode 下载 MindCluster 或 TorchNPU 软件包前，需放通 `gitcode.com` 与 `file-cdn.gitcode.com` 两个域名。
3. **新特性**：适配最新版 Ascend 软件下载；支持在 **Atlas 350 标准卡**上安装 Ascend 软件；适配 **Python 3.12**；支持 **Atlas 350 标准卡 MAMI 包** 的安装部署。
4. **本版本属于正式发布版（Release version）**，与 MindCluster 26.0 路线图（26.0.0 / 26.1.0 / 26.2.0 / 26.3.0）的首版对齐。
5. **配套组件版本**：CANN 9.0.0；Ascend HDK 中 Atlas 350 加速卡为 25.7.RC1，其他产品为 26.0.RC1。
6. **兼容性范围**：可与 MindCluster 7.0.RC1 / 7.1.RC1 / 7.2.RC1 / 7.3.0、CANN 8.5.0 / 9.0.0、Ascend HDK 25.5.0 / 25.7.RC1 / 26.0.RC1 组合使用，**各组件必须配套，禁止跨版本混用**。

---

## 【关键机制与数据】

- **原文**：MindCluster 7.3.0 与 26.0.0 在 GitCode releases 上发布的"集群调度组件"默认下载源由 Huawei Cloud OBS 迁移至 GitCode。
- **原文**：TorchNPU 共有 **15 个版本、104 个 wheel 包**的默认下载源迁移至 GitCode；PyTorch 上游 wheel 以及未在 GitCode 发布资产的 TorchNPU 版本保留原下载源。
- **原文**：迁移过程中"包名、SHA256 校验值、离线部署目录"三项保持不变 → 表明该迁移仅替换远端获取地址，不改动产物完整性校验与本地布局。
- **原文**：病毒扫描通过（Virus Scan Results：passed）。
- **原文**：新特性中"适配 Python 3.12"与"Atlas 350 标准卡 MAMI 包安装部署"为本次主版本可见的实质性能力扩展；Key Feature Changes / API Changes / Resolved Issues / Known Issues / Upgrade Impact / Vulnerability Fixes 均为 **None**。

---

## 【表格解读】

### 表格 1：Product Version Information（原文 HTML 表格，逐字还原）

| Product Name | Product Version | Version Type |
|---|---|---|
| MindCluster Ascend Deployer | 26.0.0 | Release version |

**逐行解读**：
- **Product Name = MindCluster Ascend Deployer**：标识本发布说明对应的产品名。
- **Product Version = 26.0.0**：本次发版号；并对应 NOTE 中 "MindCluster 26.0 路线图" 的首版。
- **Version Type = Release version**：表明这是正式发布版（而非 RC/Beta 等）。

---

### 表格 2：Related Product Version Mapping（配套产品版本映射）

| Product Name | Version |
|---|---|
| Ascend HDK | Atlas 350 accelerator card: 25.7.RC1<br>Other products: 26.0.RC1 |
| CANN | 9.0.0 |

**逐行解读**：
- **Ascend HDK 行**：列出与本版配套的驱动/固件基线。Atlas 350 加速卡为 25.7.RC1，其余产品为 26.0.RC1 —— 表明本版同时纳入了 Atlas 350 这一新硬件形态，与新特性中"支持 Atlas 350 标准卡安装"互为印证。
- **CANN 行**：配套 CANN 版本为 9.0.0，作为上层 AI 框架与硬件之间的运行时基线。

---

### 表格 3（Table 1）：Software version compatibility（软件版本兼容性矩阵）

| MindCluster Ascend Deployer Version | MindCluster Version to Upgrade | CANN Version | Ascend HDK Version |
|---|---|---|---|
| MindCluster Ascend Deployer 26.0.0 | MindCluster 7.0.RC1<br>MindCluster 7.1.RC1<br>MindCluster 7.2.RC1<br>MindCluster 7.3.0 | CANN 8.5.0<br>CANN 9.0.0 | Ascend HDK 25.5.0<br>Ascend HDK 26.0.RC1<br>Ascend HDK 25.7.RC1 |

**逐行解读**：
- **MindCluster Ascend Deployer 26.0.0 列**：本次发版号。
- **MindCluster Version to Upgrade 列**：原文中强调"MindCluster Ascend Deployer components must be used together. Do not mix components from different versions"，故允许同时挂载 MindCluster 7.0.RC1 / 7.1.RC1 / 7.2.RC1 / 7.3.0 共 4 个版本作为升级来源；其中 **MindCluster 7.3.0** 即正文头提到的下载源迁移至 GitCode 的版本之一。
- **CANN Version 列**：可选用 CANN 8.5.0 或 CANN 9.0.0，覆盖平滑过渡到 9.0.0 的迁移路径。
- **Ascend HDK Version 列**：可选用 25.5.0 / 25.7.RC1 / 26.0.RC1，其中 25.7.RC1 对应 Atlas 350 加速卡，26.0.RC1 对应其他产品。

---

### 表格 4：26.0.0 Documentation（本次发版配套文档）

| Document | Description | Release Notes |
|---|---|---|
| [MindCluster Ascend Deployer User Guide](./introduction.md) | Provides automated download of OS dependencies and Docker, along with one-click installation. Supports online and offline download, installation, and upgrade of drivers, firmware, CANN, MindCluster components (performance testing, fault diagnosis, and cluster scheduling), AI frameworks (TensorFlow, MindSpore, and PyTorch), MindIE images, and other software packages. | Added Python 3.12, MAMI package installation and deployment, etc. For details on other changes, see [MindCluster Ascend Deployer User Guide](./introduction.md). |

**逐行解读**：
- **Document 列**：唯一一份随本版本同步更新的配套文档，定位为用户指南（User Guide）。
- **Description 列**：阐明工具能力面——覆盖 OS 依赖与 Docker 自动下载、一键安装，并支持驱动/固件/CANN/MindCluster 组件（性能测试、故障诊断、集群调度）/TensorFlow、MindSpore、PyTorch/MindIE 镜像等的在线+离线下载、安装、升级。
- **Release Notes 列**：本版本在用户指南中相对前版的新增点摘要为 "Python 3.12、MAMI 包安装部署等"；其余细节跳转至 User Guide 原文。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 User Guide 的引用关系**：本 Release Notes 在 "26.0.0 Documentation" 表格中 **两次** 链接至 `./introduction.md`（即 MindCluster Ascend Deployer User Guide）。一处作为"本版本配套文档"，一处作为"详细变更说明的查阅入口"。因此 `./introduction.md` 是理解本次"新增 Python 3.12、MAMI 包安装部署"等能力落地细节的**下游主文档**。
- **与 MindCluster 的关系**：文中以"MindCluster Version to Upgrade"列出 4 个兼容版本（7.0.RC1/7.1.RC1/7.2.RC1/7.3.0），且强调"components must be used together. Do not mix components from different versions" —— 表明 MindCluster Ascend Deployer 是 **MindCluster 上游的安装/部署载体**，组件必须同版本同包使用。
- **与 CANN / Ascend HDK 的关系**：兼容性矩阵将 CANN（8.5.0/9.0.0）与 Ascend HDK（25.5.0/25.7.RC1/26.0.RC1）并列为可替换的运行时/驱动基线，呈现"上层 Deployer ↔ 中层 MindCluster ↔ 底层 CANN+HDK"的三层组合关系；其中 HDK 25.7.RC1 与 26.0.RC1 在"配套产品版本"小节进一步按 Atlas 350 vs 其他产品做区分。
- **与 GitCode / Huawei Cloud OBS 的关系**：下载源从 Huawei Cloud OBS 迁移至 GitCode，涉及 MindCluster 7.3.0、26.0.0 的集群调度组件，以及 TorchNPU 15 个版本/104 个 wheel；PyTorch 上游 wheel 与未在 GitCode 发版的 TorchNPU 版本保持原下载源，构成"GitCode 优先、原源兜底"的双源策略。
- **与 MindCluster 26.0 路线图的关系**：注释（NOTE）中列出 MindCluster 26.0.0 / 26.1.0 / 26.2.0 / 26.3.0 共 4 个版本，本版本处于该路线图的首发位。

---

## 【使用方法】

- **版本组合启用**：按 "Table 1 Software version compatibility" 选择一组"MindCluster Ascend Deployer 26.0.0 + MindCluster 7.x + CANN 8.5.0/9.0.0 + Ascend HDK"组合部署；原文强调 **"MindCluster Ascend Deployer components must be used together. Do not mix components from different versions"**，不得跨版本混用组件。
- **下载源配置**：当使用 MindCluster 7.3.0 或 26.0.0、以及 TorchNPU 15 个版本的 GitCode releases 资源时，默认下载源已迁移至 GitCode；若网络受防火墙/白名单控制，需在下载前放通 `gitcode.com` 与 `file-cdn.gitcode.com`。
- **离线部署**：原文指出 SHA256 校验值与离线部署目录均未变化，原有离线包路径与校验流程可直接沿用（原文未给出新的具体命令）。
- **Atlas 350 标准卡启用**：新特性支持在 Atlas 350 标准卡上安装 Ascend 软件并部署 MAMI 包，配套 Ascend HDK 版本使用 25.7.RC1（具体安装命令原文未涉及）。
- **Python 3.12 启用**：本版本已适配 Python 3.12（具体切换方式见 `./introduction.md`，本文未列具体命令）。
- **查阅更详细操作步骤**：配置项与命令级内容请跳转至 `./introduction.md`（MindCluster Ascend Deployer User Guide）查阅 —— 原文在"26.0.0 Documentation"小节两次指向该入口。
