# 安装说明

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/install/installation_introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/install/installation_introduction.md

# 深度解读：mindie-llm 安装说明文档

## 【定位】

本文档是 MindIE LLM（昇腾自研大模型推理引擎）面向用户的总入口级安装指南，定位为"快速完成 MindIE LLM 软件安装"的引导说明，核心任务是在用户动手安装之前，帮他**选择合适的安装方案**、**确认所用硬件是否在支持清单内**，并给出对应的部署架构示意图。文档不展开具体安装步骤（这些由其他子文档承担），而是以"概览 + 选型表"的方式提供决策依据。

---

## 【技术要点】

1. **三种安装方案的并列提供**：镜像安装、离线安装、源码安装对应不同的使用诉求：
   - 镜像安装：完整预装 CANN、PyTorch、MindIE 等必要依赖与软件，"拉取镜像并启动容器即可"，**支持 run 包**。
   - 离线安装：把 CANN、PyTorch、MindIE 等软件与依赖安装到**物理机或容器**，**支持 run 包和 whl 包**两种载体。
   - 源码安装：从本仓库代码自行编译，**支持 whl 包方式**，用于"体验最新功能 / 对源码修改增强"。

2. **安装包形态映射（基于原文 NOTE）**：
   - **新用户** → 推荐 **whl 包** 方式。
   - **老用户升级** → 推荐 **run 包** 方式。
   - 这是文档中唯一出现的"用户角色→安装包形态"决策建议。

3. **操作系统识别命令**（安装前确认 OS 是否受支持）：
   ```bash
   uname -m && cat /etc/*release
   ```
   文档提示："如果查询的操作系统版本不在对应产品列表中，请替换为支持的操作系统。"——这是原文中明确给出的**前置校验流程**。

4. **受支持硬件-OS 矩阵**（详见表格解读）：覆盖 4 类昇腾硬件 + 多达 30+ 个 OS/内核版本组合；OS 区分 AArch64 与 X86_64 两套架构。

5. **部署架构图（figure1）**：原文插入 `mindie_installation_diagram.png`，说明"部署架构如[图1]所示"，但**未在文本中给出对图的具体字段解读**（图中元素需读者自行查看）。

6. **安装前置依赖栈**：在镜像/离线两种方案中均隐含依赖栈 = **CANN + PyTorch + MindIE**；源码方案则由用户自行编译 MindIE 三件套。

---

## 【关键机制与数据】

本文档为 overview 性质，**不含性能数据、benchmark、无 runtime 数据流**。可以视为"数据"的内容有两类：

- **决策流（基于原文）**：
  1. 用户先用 `uname -m && cat /etc/*release` 确认 OS 架构与发行版；
  2. 在 **表 1 操作系统支持列表** 中查找"硬件 × OS"是否命中；
  3. 依据使用场景（最简部署 / 离线环境 / 改源码）在"镜像/离线/源码"三方案中选型；
  4. 依据用户身份（新用户/老用户升级）选 run 包或 whl 包。

- **依赖拓扑（基于原文隐含声明）**：镜像/离线安装方案的最小依赖集合 = `{CANN, PyTorch, MindIE}`，其中 CANN 与 PyTorch 由昇腾社区/官方提供，MindIE 即本仓库产物。

> 原文未给出任何推理吞吐、显存占用、模型支持清单等运行时关键数据。

---

## 【表格解读】

**表 1 操作系统支持列表**（原文已使用 markdown 表格 + `<li>` 列表结构逐字保留如下）：

| 硬件 | 操作系统 |
|------|----------|
| Atlas 800I A2 推理服务器 | AArch64：<br><li>CentOS 7.6</li><li>CTYunOS 23.01</li><li>CULinux 3.0</li><li>Kylin V10 GFB</li><li>Kylin V10 SP2</li><li>Kylin V10 SP3</li><li>Kylin V10 SP3 2403 4.19.90-89.11.v2401</li><li>Kylin V11</li><li>Ubuntu 22.04</li><li>AliOS3</li><li>BCLinux 21.10 U4</li><li>Ubuntu 24.04 LTS</li><li>openEuler 22.03 LTS</li><li>openEuler 24.03 LTS SP1</li><li>openEuler 22.03 LTS SP4</li><li>Alibaba Cloud Linux 3.2104 U10</li><li>AntOS 6.6</li><li>UOS V25（内核6.6）</li> |
| Atlas 300I Duo 推理卡+Atlas 800 推理服务器（型号 3000） | AArch64：<br><li>BCLinux 21.10</li><li>Debian 10.8</li><li>Kylin V10 SP1</li><li>Kylin V10 SP3 2403 4.19.90-89.11.v2401</li><li>Kylin V11</li><li>Ubuntu 20.04</li><li>Ubuntu 22.04</li><li>UOS20-1020e</li><li>openEuler 24.03 SP1</li><li>openEuler 22.03 LTS SP4</li> |
| Atlas 300I Duo 推理卡+Atlas 800 推理服务器（型号 3010） | X86_64：<br><li>Ubuntu 22.04</li> |
| Atlas 800I A3 超节点服务器 | AArch64：<br><li>openEuler 22.03</li><li>CULinux 3.0</li><li>Kylin V10 SP3 2403</li><li>Kylin V11</li><li>BCLinux 21.10 U4（内核版本：5.10.0-200.0.0.131.30）</li><li>CTyunOS 3</li><li>UOS V25（内核6.6）</li> |
| Atlas 200I Pro 加速模块 | AArch64：<br><li>Ubuntu 22.04</li><li>openEuler 22.03 LTS</li> |

逐行解读：

- **Atlas 800I A2 推理服务器**：覆盖范围最广（18 个 OS 条目），全部跑在 AArch64 上；典型发行版包括 CentOS 7.6、Ubuntu 22.04/24.04 LTS、openEuler 22.03/24.03 LTS（含 SP1/SP4）、Kylin V10 全系列（含 GFB/SP2/SP3 及带具体内核号的 SP3 2403 2401 补丁）、Alibaba/UOS/CTYunOS/CULinux 等"国产生根"系。是**唯一同时覆盖 Ubuntu 22.04 + Ubuntu 24.04 LTS** 的硬件，也是文档中 OS 数量最多的平台。

- **Atlas 300I Duo 推理卡 + Atlas 800 推理服务器（型号 3000）**：同样仅 AArch64，但 OS 数量缩窄到 10 个；保留 Kylin V10 SP1、SP3 2403（含具体内核号 `4.19.90-89.11.v2401`）以及 Debian 10.8、Ubuntu 20.04/22.04 等。注意表中**单独列出了内核号补丁版本**（Kylin V10 SP3 2403 4.19.90-89.11.v2401），证明此型号对内核细节敏感，是安装前需要重点核对的硬件。

- **Atlas 300I Duo 推理卡 + Atlas 800 推理服务器（型号 3010）**：仅有 **X86_64 + Ubuntu 22.04** 一条记录，是列表中**唯一的 X86_64 行**，也是文档明确支持的唯一 x86 部署形态；其他型号均要求 AArch64。这条信息对想在非 ARM 机器上试用 MindIE 的用户是关键的"特例"提示。

- **Atlas 800I A3 超节点服务器**：AArch64，共 7 个 OS；包含对**内核号精确指定**的 BCLinux 21.10 U4（`5.10.0-200.0.0.131.30`），以及较新的 openEuler 22.03 与 CULinux 3.0；覆盖 CTyunOS 3、UOS V25（内核 6.6）。Supernode 形态通常用于大规模推理，OS 选型相对收敛。

- **Atlas 200I Pro 加速模块**：AArch64，仅 2 个 OS（Ubuntu 22.04 + openEuler 22.03 LTS），是列表中**OS 数量最少**的硬件——通常对应边缘/嵌入式场景，对 OS 选型最严格。

**整表横向规律**（基于原文事实归纳）：
- 全文**只有 X86_64 1 条**，**AArch64 占绝对主流**，意味着 MindIE LLM 默认部署目标为 ARM 服务器；
- 对**国产化 OS**（Kylin、openEuler、UOS、BCLinux、CTYunOS、CULinux、Alibaba Cloud Linux、AntOS、AliOS）有大量覆盖，表明该软件定位明确面向信创/政企场景；
- 表格中两次出现**精确内核号/补丁号**（`4.19.90-89.11.v2401`、`5.10.0-200.0.0.131.30`），这是用户**安装前必须逐字核对**的版本细节，否则文档已隐含"未命中则不保证可用"的结论。

---

## 【公式解读】

**原文无公式。** 全文为说明性 + 表格 + 命令 + 图像引用，无任何 LaTeX 数学公式或伪代码公式。

---

## 【关联】

文档内**唯一的内部链接**为：

- `(#figure1)` → 指向**图 1：部署架构**（位于同文件）。该图本身是二进制资源 `figures/mindie_installation_diagram.png`，文中未对其内容做字段级解释；用户通过该图可读出"硬件 → OS → CANN/PyTorch/MindIE 依赖 → MindIE LLM 推理服务"这种自底向上的部署架构关系。

文档作为 overview，**与本仓其他章节的隐式上下游关系**可由原文推断（仅基于文档可见线索，不再臆造具体链接路径）：

- **向上游**：本文提到"下载已经打包好的镜像"（昇腾社区）、"CANN、PyTorch、MindIE"三类依赖——这些是 MindIE LLM 的运行时前置栈，文档不展开获取方式，留给上游组件说明；
- **向同层**：本文给出的"镜像安装 / 离线安装 / 源码安装"是三套**并列子方案**，每条方案都应在仓内具备独立子页面承载具体步骤（镜像拉取命令、whl/run 包安装命令、源码编译流程等），但本 overview **未在末尾列出这些子链接**（"内部链接：(无)"），所以无法在本节进一步定位具体子文档文件名。

---

## 【使用方法】

本节仅汇总原文明确给出的"如何开始安装"的可执行信息，不引入文档外步骤：

1. **确认硬件与 OS**：在 `Atlas 800I A2`、`Atlas 300I Duo + Atlas 800 推理服务器（型号 3000 / 3010）`、`Atlas 800I A3 超节点服务器`、`Atlas 200I Pro 加速模块` 五种硬件中确认自己的型号；
2. **执行原文命令确认 OS**：
   ```bash
   uname -m && cat /etc/*release
   ```
   与**表 1** 命中后再继续；
3. **按身份选择安装包形态**（原文 NOTE）：
   - 新用户 → **whl 包**；
   - 老用户升级 → **run 包**；
4. **按使用场景选择安装方案**（原文三大方案）：
   - 希望"一键完成" → **镜像安装**（run 包）；
   - 无外网 / 需装到物理机或自有容器 → **离线安装**（run 包或 whl 包）；
   - 体验最新版 / 改源码 → **源码安装**（whl 包，由仓库自行编译）。

具体的拉取命令、whl 文件路径、容器启动脚本、源码构建指令在**原文中均未给出**（这是本文作为 overview 的天然边界），它们由对应子文档承担，本节不补全。

## 图文联合解读

- `mindie_installation_diagram.png`: **图文联合解读：**

1）**图示内容**：分层架构图，自下而上展示昇腾AI设备（Linux OS）上的软件栈——底层为npu-driver与npu-fireware固件驱动；中层为Ascend CANN套件（toolkit、ops、nnal）；上层并列MindIE组件（Motor/LLM/SD）与依赖（PyTorch、Torch_NPU、Python三方库）。

2）**技术结论**：MindIE运行依赖自下而上的完整栈链：硬件驱动→CANN算子层→MindIE业务层，缺一不可。

3）**与文档论点关系**：该图直观佐证"安装方案"章节所述三种安装方式（镜像/离线/源码）正是对上述多层依赖的不同打包策略，新老用户选型需权衡依赖完整性。
