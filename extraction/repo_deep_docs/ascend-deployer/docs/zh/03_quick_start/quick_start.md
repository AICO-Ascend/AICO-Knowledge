# 快速入门

> 仓 `ascend-deployer` · 路径 `docs/zh/03_quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascend-deployer/docs/zh/03_quick_start/quick_start.md

# ascend-deployer 快速入门文档深度解读

## 【定位】

这篇文档以 **openEuler 22.03 LTS AArch64 + 单台 Atlas 800T A2 训练服务器** 为目标场景，指导开发者通过 7 步流程，使用 `ascend-deployer` 工具完成 **sys_pkg、python、NPU、CANN、toolbox、fault-diag** 等核心组件的快速下载与一键式自动部署（MindCluster 集群调度组件除外，需另行参考）。

---

## 【技术要点】

1. **环境前提**：以 **root 用户**登录待安装设备；系统为 openEuler 22.03 LTS AArch64；硬件为 Atlas 800T A2 训练服务器。
2. **工具安装命令**：`pip3 install ascend-deployer==<version>`，版本号建议参考 [PyPI 官网历史](https://pypi.org/project/ascend-deployer/#history) 选用最新发布版本；若 `pip3` 不存在需自行安装。
3. **软件包下载命令**：`ascend-download --os-list=OpenEuler_22.03LTS_aarch64 --download=NPU,CANN,FaultDiag`，下载完成后统一存放至 `$HOME/ascend-deployer/resources` 目录，内容包括：OS 所需依赖、CANN 软件包、配套驱动与固件包、Docker 软件等。
4. **（可选）安装前检查**：`ascend-deployer --install=<pkg_name> --check`，`<pkg_name>` 取值需参考支持安装及升级的软件包附录。
5. **一键安装命令**：`ascend-deployer --install=sys_pkg,python,npu,toolkit,kernels,toolbox,fault-diag`，可同时指定多个包以英文逗号分隔，自动安装部署全部指定软件包（不含 MindCluster）。
6. **（可选）组件健康检测**：`ascend-deployer --test=all`，检查所有组件版本及能否正常工作。
7. **环境变量配置**：使用 Python 与 CANN 前需 `source` 两条脚本——
   - `source /usr/local/ascendrc`（配置 python 环境变量）
   - `source /usr/local/Ascend/toolbox/set_env.sh`（配置 toolbox 环境变量）

---

## 【关键机制与数据】

**工作流程与数据流向**（原文步骤串联后的整体逻辑）：

- 原文步骤 2：用户通过 pip3 获取 `ascend-deployer` 安装包，提供两个子命令 `ascend-download`（下载）和 `ascend-deployer`（部署）。
- 原文步骤 3：`ascend-download` 根据 `--os-list`（操作系统与架构标识）筛选匹配的 OS 依赖，再根据 `--download` 指定需要下载的组件大类（NPU、CANN、FaultDiag），将下载产物（**OS 依赖、CANN 软件包、驱动与固件包、Docker 软件**）汇总到 `$HOME/ascend-deployer/resources`。
- 原文步骤 4：通过 `--check` 子能力在安装前进行预检，避免环境不满足时直接安装失败。
- 原文步骤 5：核心安装路径 `--install=sys_pkg,python,npu,toolkit,kernels,toolbox,fault-diag` 同时处理 6 类组件：系统包（sys_pkg）、Python 第三方依赖（python）、NPU 驱动固件（npu）、CANN toolkit（toolkit）、CANN 算子库（kernels）、开发与故障诊断工具（toolbox, fault-diag）。
- 原文步骤 6：通过 `--test=all` 对所有已安装组件进行版本与功能性自检。
- 原文步骤 7：通过 `source` 系统级脚本（`/usr/local/ascendrc`、`/usr/local/Ascend/toolbox/set_env.sh`）将 Python 与 toolbox 的运行时路径注入当前 shell，完成"装而可用"的最后一环。

**关键路径数据**（原文明确给出）：
- 资源下载目录：`$HOME/ascend-deployer/resources`（原文步骤 3）
- Python 环境变量脚本：`/usr/local/ascendrc`（原文步骤 7）
- toolbox 环境变量脚本：`/usr/local/Ascend/toolbox/set_env.sh`（原文步骤 7）

原文未给出具体的安装耗时、下载体积、性能基准等量化数据。

---

## 【表格解读】

**原文无表格。**

文档采用编号步骤 + shell 代码块的线性结构展示完整流程，未出现任何参数表、配置项表或性能对比表。可安装组件的清单通过命令 `--install=sys_pkg,python,npu,toolkit,kernels,toolbox,fault-diag` 在命令行参数中以逗号分隔形式列出，但原文并未将其整理为表格形式。

---

## 【公式解读】

**原文无公式。**

文档全部内容为操作步骤与 shell 命令，未涉及任何数学公式或伪代码表达式。

---

## 【关联】

依据文末两处内部链接定位，本文档与其他模块的依赖关系如下：

1. **依赖附录：可安装软件包清单**
   - 链接：`../07_references/appendix/02_installation_and_upgrade_reference.md#支持安装及升级的软件包`
   - 关联点：原文步骤 4 中 `<pkg_name>` 的合法取值范围由此附录定义；同时步骤 5 安装命令中的 6 个组件名（sys_pkg、python、npu、toolkit、kernels、toolbox、fault-diag）也来源于该附录维护的软件包列表。
   - 作用：定位本快速入门未列出的其它可选包（如 MindCluster 等），并获取升级场景下的同名包使用说明。

2. **依赖专题文档：MindCluster 集群调度前置配置**
   - 链接：`../05_installation_and_upgrade/02_install_softwares.md#安装mindcluster集群调度前配置`
   - 关联点：原文步骤 5 明确将 MindCluster 排除在 `ascend-deployer --install` 之外，并指向该专题文档；表明 MindCluster 在部署前需要额外的环境与配置准备（典型如集群节点规划、网络、调度服务依赖等），与本快速入门描述的单机一键流程存在结构性差异。
   - 作用：作为快速入门向"集群化"扩展的入口指引。

整体上，本文档是 `ascend-deployer` 的**最小可用路径（MVP）**，向上承接附录的"完整能力清单"，向下通过 MindCluster 专题文档将用户引导至多节点集群部署场景。

---

## 【使用方法】

### 启用方式

无需额外启用开关，安装工具本身即提供所有能力：

| 阶段 | 命令 | 说明 |
| --- | --- | --- |
| 工具获取 | `pip3 install ascend-deployer==<version>` | 从 PyPI 安装指定版本工具 |
| 资源下载 | `ascend-download --os-list=OpenEuler_22.03LTS_aarch64 --download=NPU,CANN,FaultDiag` | 下载 OS 依赖、驱动固件、CANN、Docker 等 |
| 安装前检查（可选） | `ascend-deployer --install=<pkg_name> --check` | 预检指定包的安装环境 |
| 一键安装 | `ascend-deployer --install=sys_pkg,python,npu,toolkit,kernels,toolbox,fault-diag` | 批量安装 6 类组件，MindCluster 除外 |
| 组件自检（可选） | `ascend-deployer --test=all` | 校验所有组件版本与可用性 |
| 环境变量激活 | `source /usr/local/ascendrc` 与 `source /usr/local/Ascend/toolbox/set_env.sh` | 在当前 shell 中激活 Python 与 toolbox |

### 关键配置项

- **`<version>`**：Ascend Deployer 工具版本号，建议参照 PyPI 官网选用最新发布版本（原文步骤 2）。
- **`--os-list`**：操作系统 + 架构标识，本例为 `OpenEuler_22.03LTS_aarch64`（原文步骤 3）。
- **`--download`**：下载目标组件列表，可选 `NPU`、`CANN`、`FaultDiag` 等，多值以英文逗号分隔（原文步骤 3）。
- **`--install=<pkg_name>`**：安装目标包名，`--check` 子选项开启安装前检查；`pkg_name` 取值见附录（原文步骤 4、5）。
- **`--test=all`**：完整组件健康检查（原文步骤 6）。

### 注意事项（原文明确指出）

- 若系统提示 `pip3` 命令不存在，须用户自行安装。
- MindCluster 集群调度组件不在本快速入门 `--install` 列表中，需参考专题文档 `../05_installation_and_upgrade/02_install_softwares.md#安装mindcluster集群调度前配置`。
- `source` 两条脚本是"使用 Python 与 CANN 之前"的前置条件，仅在当前 shell 会话中生效；若需长期生效，应将其写入 shell 配置文件（原文未明确给出该写法，故归入"原文未涉及"）。
