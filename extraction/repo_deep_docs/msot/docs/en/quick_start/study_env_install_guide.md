# Ascend AI Operator Development Toolchain Learning Environment Installation Guide

> 仓 `msot` · 路径 `docs/en/quick_start/study_env_install_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/en/quick_start/study_env_install_guide.md

# 「Ascend AI Operator Development Toolchain 学习环境安装指南」一体化深度解读

---

## 【定位】

这篇文档解决的是**如何为 msot (Ascend AI Operator Development Toolchain) 的 quick_start 学习路径搭建可运行的实验环境**，覆盖 CANN 工具安装、工作目录初始化、芯片 SoC 模型采集、Python 依赖安装四个预备步骤，目的是让用户在最短时间内（推荐容器方式 5 分钟内）具备运行 msot 示例的能力。

---

## 【技术要点】

1. **前置硬件与系统要求**：需要一台 Linux 服务器，至少配备一张 Ascend NPU 卡，且 NPU driver 与 firmware 已预装完成（原文未涉及具体驱动版本号）。
2. **CANN / Operator Tool 两种安装方式**：
   - **容器化方式（推荐）**：Docker 服务正常时可在 **5 分钟**内完成，详见 `./cann_container_setup.md`。
   - **裸机/虚拟机方式**：流程复杂、易引发多用户冲突，故障排查困难，需参考昇腾官方 CANN 安装文档，使用较新版本即可。
3. **工作目录约定**：`~/ot_demo/workspace`（"ot" 为 Operator Tool 缩写），使用 `mkdir -p` 创建。
4. **仓库克隆**：`git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot`，示例路径为 `~/ot_demo/msot/example`；若 git 下载失败可下载压缩包手动上传。
5. **芯片 SoC 模型统一采集**：通过环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 持久化（仅限本次学习用途），值**必须去掉 "Ascend" 前缀**，合法示例 `910B4`、`910_9392`，非法示例 `Ascend910B4`、`Ascend910_9392`。
6. **Python 依赖安装**：使用阿里云镜像源（`https://mirrors.aliyun.com/pypi/simple/`），pip 命令安装 `~/ot_demo/msot/example/quick_start/public/requirements.txt`，并创建 `/usr/bin/python3 → /usr/local/bin/python3` 的软链接以避免默认 python3 路径冲突。

---

## 【关键机制与数据】

1. **SoC 模型采集机制（自动模式）**：
   - 原文：执行 `python3 ~/ot_demo/msot/example/quick_start/public/get_ai_soc_version.py` 后，运行 `source set_chip_env_var.sh`，脚本会将去掉 "Ascend" 前缀的 SoC 名（如 910B4、910_9392）写入 `MY_STUDY_VAR_CHIP_SOC_TYPE`。
   - 原文：SoC 模型在后续命令中被频繁引用，因此前置统一采集可避免重复输入。
2. **SoC 模型采集机制（手动模式）**：
   - 原文：通过 `echo "export MY_STUDY_VAR_CHIP_SOC_TYPE=<YOUR_CHIP_NAME>" >> ~/.bashrc && source ~/.bashrc` 写入用户级 shell 配置，持久化到 `~/.bashrc`。
3. **数据流（隐含）**：硬件 NPU → 驱动/固件 → CANN/Operator Tool → Python 工具链（msot 仓库 example）→ 算子构建/运行；环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 作为"硬件身份标识"在整条链路中被 msot 各子命令消费。
4. **性能数据**：仅出现一处 —— 容器化安装可在 **5 分钟**内完成（原文：Docker 服务正常时）。原文未提供其它性能/资源占用数据。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

1. **CANN 容器环境搭建 → `./cann_container_setup.md`**：
   - 文档在 "1.1 Operator Tool Installation" 的"容器化方式"中明确要求跳转到该子文档执行具体的容器部署步骤；本指南只负责"指路"，不展开容器命令细节，两者构成"顶层指南 → 具体环境搭建"的依赖关系。

2. **芯片 SoC 模型采集 → `get_chip_soc_type.md`**：
   - 文档在 "1.3.2 手动获取芯片 SoC 模型" 章节中将该文档作为"概念与采集方法"的参考入口；自动路径（`get_ai_soc_version.py` + `set_chip_env_var.sh`）是该流程的封装版，手动路径则向用户暴露 SoC 名构成（如 `Ascend910B4` → `910B4`）。

3. **下游消费者（隐式关联）**：
   - 原文指出 SoC 模型"在后续命令中被频繁使用"，意味着 `MY_STUDY_VAR_CHIP_SOC_TYPE` 是 msot 仓库 `example/quick_start` 路径下后续各算子开发/调优示例的公共输入参数，本文档为其前置依赖。

4. **msot 仓库结构关联**：
   - `~/ot_demo/msot/example/quick_start/public/` 目录下沉淀了三个关键资产：`get_ai_soc_version.py`（SoC 自动采集）、`set_chip_env_var.sh`（环境变量写入）、`requirements.txt`（Python 依赖），构成 quick_start 学习的"公共工具三件套"。

---

## 【使用方法】

**原文涉及的所有命令/配置项汇总（按章节顺序）：**

### 1.1 安装 Operator Tool（两条路径二选一）
- **路径 A（推荐 · 容器化）**：跳转 `./cann_container_setup.md`，原文未给出具体命令。
- **路径 B（裸机/虚拟机）**：跳转 https://www.hiascend.com/document/detail/en/canncommercial/800/quickstart/index/index.html ，原文未给出具体命令。

### 1.2 创建工作目录
```shell
mkdir -p ~/ot_demo/workspace
```

### 1.2 克隆仓库
```shell
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```
或手动下载 gitcode.com 压缩包上传至服务器并保持目录结构一致。

### 1.3.1 自动获取 SoC
```shell
python3 ~/ot_demo/msot/example/quick_start/public/get_ai_soc_version.py
source set_chip_env_var.sh
```

### 1.3.2 手动获取 SoC
```shell
echo "export MY_STUDY_VAR_CHIP_SOC_TYPE=<YOUR_CHIP_NAME>" >> ~/.bashrc && source ~/.bashrc
```
- 合法值（去掉 Ascend 前缀）：`910B4`、`910_9392`
- 非法值：`Ascend910B4`、`Ascend910_9392`

### 1.4 安装 Python 依赖
```shell
pip3 install -r ~/ot_demo/msot/example/quick_start/public/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
ln -sf /usr/local/bin/python3 /usr/bin/python3
```
若无法访问阿里源或存在安全顾虑，可去掉 `-i https://mirrors.aliyun.com/pypi/simple/` 参数以使用默认源。

### 配置项约束（原文提示）
- `MY_STUDY_VAR_CHIP_SOC_TYPE` **仅限本次 quick_start 学习使用**，禁止用于商业开发（原文 CAUTION 声明）。
