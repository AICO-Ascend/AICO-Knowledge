# Ascend AI Operator Development Toolchain Learning Environment Installation Guide

> 仓 `msot` · 路径 `docs/en/quick_start/installation_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/en/quick_start/installation_guide.md

# 深度解读：Ascend AI 算子开发工具链学习环境安装指南

---

## 【定位】

这篇文档解决"如何在已装配 Ascend NPU 的 Linux 服务器上搭建 **msot (Ascend AI Operator Development Toolchain) 学习环境**"的问题，覆盖工具链安装、工作区初始化、芯片 SoC 模型获取、Python 依赖安装四个步骤，为后续快速上手算子开发提供前置环境基础。

---

## 【技术要点】

1. **工具链两种部署方式**：推荐容器化运行环境（Docker 正常时约 **5 分钟**完成），裸金属/虚拟机方式复杂且易出现多用户冲突。
2. **工作区目录固定路径**：示例与工作目录分别为 `~/ot_demo/msot/example` 与 `~/ot_demo/workspace`，其中 `ot` 为 Operator Tool 的缩写。
3. **芯片 SoC 模型统一注入环境变量**：变量名 `MY_STUDY_VAR_CHIP_SOC_TYPE`，**需去掉 "Ascend" 前缀**，正确值示例 `910B4`、`910_9392`；错误值为 `Ascend910B4`、`Ascend910_9392`。
4. **SoC 模型两种获取路径**：
   - 自动：`python3 ~/ot_demo/msot/example/quick_start/public/get_ai_soc_version.py` 后执行 `source set_chip_env_var.sh`；
   - 手动：参看 `get_chip_soc_type.md`，再 `echo "export MY_STUDY_VAR_CHIP_SOC_TYPE=<YOUR_CHIP_NAME>" >> ~/.bashrc && source ~/.bashrc`。
5. **Python 依赖安装命令（强制使用阿里源）**：
   ```shell
   pip3 install -r ~/ot_demo/msot/example/quick_start/public/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
   ln -sf /usr/local/bin/python3 /usr/bin/python3
   ```
   若阿里源不可用或不被信任，可去掉 `-i xxx` 回退默认源。
6. **仓库下载方式**：`git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot`；若 git 失败，可下载压缩包并保持目录结构正确。

---

## 【关键机制与数据】

- **运行环境前置条件（原文）：**"Linux server equipped with at least one Ascend NPU card, with the NPU driver and firmware already installed" —— 即 NPU 驱动与固件为本文档前置依赖，不在本文档范围内。
- **容器化方式效率数据（原文）：**"can be completed within 5 minutes when the Docker service is running normally" —— 容器化路径仅在 Docker 服务正常时成立。
- **数据流（原文）：** 自动获取 SoC 流程为 `执行探测脚本 → 触发 set_chip_env_var.sh → 将去前缀的芯片型号写入 MY_STUDY_VAR_CHIP_SOC_TYPE → 供后续命令统一引用`；手动流程为 `用户查询文档获得 SoC → 手动 echo 写入 ~/.bashrc → source 加载到当前 shell`。
- **持久化机制（原文）：** 手动方式通过 `>> ~/.bashrc` 将环境变量持久化到登录 shell；自动方式则依赖 `set_chip_env_var.sh` 的副作用（原文未明示是否写入 bashrc，由脚本决定）。
- **范围限制（原文）：** 环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` "**only used for this quick start tutorial. Do not use this variable in commercial development**"，属教学专用占位符。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **与 CANN 容器环境的关系**：当用户选择 1.1 节第 1 种安装方式时，文档显式跳转到 `./cann_container_setup.md`，即本文档只做路径指引，**容器化部署的具体步骤（镜像拉取、容器启动、工具链挂载等）由该子文档承担**。
- **与芯片 SoC 模型获取方法的关系**：当自动脚本不可用或用户希望理解 SoC 概念时，文档跳转 `get_chip_soc_type.md`，**人工查询流程（NPU 型号查询命令、典型型号表）由该子文档承担**。
- **与外部 CANN 官方安装文档的关系**：当选择裸金属/虚拟机方式时，文档指向 `https://www.hiascend.com/cann/download` 外部链接，**不依赖仓内任何子文档**，因为此方式与本仓示例无强绑定。
- **与 msot 示例代码的关系**：所有命令路径（`~/ot_demo/msot/example/quick_start/public/...`）均假定已完成 1.2 节的仓库克隆，意味着本文档与 msot 仓库的 `example/quick_start/public` 子目录构成强耦合前置关系。

---

## 【使用方法】

下列命令均**逐字还原**自原文，可按顺序执行：

```shell
# 1. 创建工作区（存放示例运行产物）
mkdir -p ~/ot_demo/workspace

# 2. 克隆仓库（若 git 失败，可手动下载 zip 并保证目录结构）
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot

# 3. 自动获取芯片 SoC 模型（推荐快速体验路径）
python3 ~/ot_demo/msot/example/quick_start/public/get_ai_soc_version.py
source set_chip_env_var.sh

# 3'. 手动获取 SoC 模型（需先参看 get_chip_soc_type.md）
# 将 <YOUR_CHIP_NAME> 替换为去前缀的型号，例如 910B4
echo "export MY_STUDY_VAR_CHIP_SOC_TYPE=<YOUR_CHIP_NAME>" >> ~/.bashrc && source ~/.bashrc

# 4. 安装 Python 依赖（默认走阿里源；不可用时去掉 -i 参数）
pip3 install -r ~/ot_demo/msot/example/quick_start/public/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
ln -sf /usr/local/bin/python3 /usr/bin/python3
```

> **配置项与启用方式说明（原文）：**
> - 工具链本体启用方式取决于 §1.1 选择：**容器方式 → ./cann_container_setup.md**；**裸金属方式 → 外部 CANN 安装指南**。
> - SoC 模型配置项：`MY_STUDY_VAR_CHIP_SOC_TYPE`（教学专用，**严禁用于商业开发**）。
> - Python 源配置项：`-i https://mirrors.aliyun.com/pypi/simple/`（默认启用，可移除以恢复默认源）。
> - Python 软链配置项：`ln -sf /usr/local/bin/python3 /usr/bin/python3`（原文未解释具体作用，仅作为命令的一部分给出）。
