# MindSpeed安装指导

> 仓 `mindspeed` · 路径 `docs/zh/user-guide/install_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/user-guide/install_guide.md

# MindSpeed 安装指导 — 一体化深度解读

---

## 【定位】

本文档是「MindSpeed Core（大模型训练加速库）」基于 PyTorch 框架的官方**安装指引**，解决用户在昇腾 NPU 硬件上从零搭建 MindSpeed 训练环境（涵盖驱动固件、CANN、PyTorch/TorchNPU、Megatron-LM、MindSpeed 主体）的全流程问题。

---

## 【技术要点】

1. **硬件配套范围严格收窄**：在训练场景下，文档明确仅支持 `<term>Ascend 950 系列产品</term>`、`<term>Atlas A3 训练系列产品</term>`、`<term>Atlas A2 训练系列产品</term>` 三类硬件；其余推理产品（Atlas A3/A2 推理、Atlas 200I/500 A2、Atlas 推理/训练系列产品）均标记为「x」不支持。

2. **两条并行安装路径**：
   - **方式一（镜像安装）**：基于 Python 3.11、aarch64 架构、配套镜像已预装 **CANN 9.0.0** 与 **TorchNPU 26.0.0**，对应分支 `26.0.0_core_r0.12.1`；
   - **方式二（源码安装）**：基于 Python 3.10，wheel 包名后缀为 `cp310`，需要用户自行安装 CANN（Toolkit、ops、NNAL）与 PyTorch/TorchNPU。

3. **源码安装的版本锚点**：示例明确给出 `torch-2.7.1-cp310-cp310-manylinux_2_28_aarch64.whl` 与 `torch_npu-2.7.1post4-cp310-cp310-manylinux_2_28_aarch64.whl`，并要求 Megatron-LM 切换到 `core_v0.12.1` 分支，MindSpeed 本体通过 `pip install -e MindSpeed` 以可编辑模式安装。

4. **CANN 环境变量必须显式 source**：训练或推理业务代码调用 NPU 前必须执行：
   - `source /usr/local/Ascend/cann/set_env.sh`
   - `source /usr/local/Ascend/nnal/atb/set_env.sh`
   否则业务代码无法执行（原文直接给出了该强约束说明）。

5. **安全与权限规范**：建议**非 root** 用户安装，目录权限 `750`、文件权限 `640`，可通过 `umask 0027` 控制；并指引用户参考《安全声明》中关于「文件权限控制」的内容。

6. **固件与驱动安装脚本模板**：以 `chmod +x` + `--full --force` 参数运行 NPU 驱动与固件 `.run` 包，要求 `--full` 完整安装。

---

## 【关键机制与数据】

- **镜像/源码双轨机制**：原文明确指出"master 分支后续会更新新的镜像"，源码安装路径作为镜像不兼容时的回退方案。
- **环境变量继承路径**：容器默认在 `~/.bashrc` 中初始化 NPU 驱动与 CANN 环境，用户可在容器内替换或手动 `source` 新版本。
- **驱动/固件默认挂载点**：原文档说明默认配置驱动和固件安装在 `/usr/local/Ascend`，容器通过 `-v /usr/local/Ascend/driver:/usr/local/Ascend/driver` 与 `-v /usr/local/Ascend/firmware:/usr/local/Ascend/firmware` 双向挂载以保证 NPU 设备可见。
- **NPU 健康检查命令**：原文给出 `npu-smi info` 用于在容器内确认 NPU 是否可正常使用。
- **镜像拉取验证命令**：`docker image list` 用于确认镜像是否成功拉取。
- **性能数据**：原文**未涉及**任何性能基准数据（如吞吐、加速比等）。

---

## 【表格解读】

**表 1 产品硬件支持列表**（逐字还原）：

|产品|是否支持（训练场景）|
|--|:-:|
|<term>Ascend 950 系列产品</term>|√|
|<term>Atlas A3 训练系列产品</term>|√|
|<term>Atlas A3 推理系列产品</term>|x|
|<term>Atlas A2 训练系列产品</term>|√|
|<term>Atlas A2 推理系列产品</term>|x|
|<term>Atlas 200I/500 A2 推理产品</term>|x|
|<term>Atlas 推理系列产品</term>|x|
|<term>Atlas 训练系列产品</term>|x|

**逐行解读**：

- **Ascend 950 系列产品**：√ 支持，是当前文档覆盖的最新一代昇腾训练硬件。
- **Atlas A3 训练系列产品**：√ 支持，对应镜像标签含 `-a3-` 后缀（如 `26.0.0_core_r0.12.1-a3-openeuler24.03-py3.11-aarch64`）。
- **Atlas A3 推理系列产品**：x 不支持，文档聚焦训练场景，明确将推理产品排除。
- **Atlas A2 训练系列产品**：√ 支持，对应镜像标签 `-910b-`（如 `26.0.0_core_r0.12.1-910b-openeuler24.03-py3.11-aarch64`）。
- **Atlas A2 推理系列产品**：x 不支持。
- **Atlas 200I/500 A2 推理产品**：x 不支持（边缘/推理定位）。
- **Atlas 推理系列产品**：x 不支持（上一代推理产品族）。
- **Atlas 训练系列产品**：x 不支持（上一代训练产品族，仅新一代训练产品受支持）。

脚注说明：√ 代表支持，x 代表不支持。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文末内部链接，本文档与以下模块存在直接引用关系：

1. **`../release_notes_core.md#相关产品版本配套说明`**（安装前准备章节引用）：
   - 上游版本配套依据：在安装 MindSpeed 前，必须先查阅《版本说明》中的「相关产品版本配套说明」，确认 CANN、TorchNPU、PyTorch、Megatron-LM 等组件的版本对应关系，避免不兼容。

2. **`../SECURITYNOTE.md`**（安装前准备章节引用）：
   - 安全声明支撑：文档中关于「文件夹权限 750、文件权限 640、umask 0027、非 root 用户安装」的约束，详细技术说明需查阅《安全声明》中各组件关于「文件权限控制」的章节。

3. **`../../../docker/OVERVIEW.zh.md`**（方式一镜像安装章节引用）：
   - 自定义镜像构建入口：当官方预置镜像不满足需求时（如自定义环境、需要镜像底包升级等），文档指引用户跳转至《镜像概述》查阅自定义构建镜像的方法。

4. **外部权威链接**（兼容性查询）：
   - `https://www.hiascend.com/hardware/compatibility`（物理机操作系统兼容）
   - 《CANN 软件安装》之「操作系统兼容性说明」（虚拟机/容器操作系统兼容）
   - `https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/softwareinst/instg/instg_0000.html`（CANN 安装手册，源码安装章节引用）
   - 《TorchNPU 软件安装》之「安装 PyTorch」（PyTorch/TorchNPU 安装指引，源码安装章节引用）
   - `https://gitcode.com/Ascend/MindSpeed/tree/26.0.0_core_r0.12.1`（镜像配套的源码分支）
   - `https://www.hiascend.com/developer/ascendhub/detail/4ad248a439a44b4bb72e0534bfda8e2a`（镜像仓库地址）

---

## 【使用方法】

**启用方式与配置项命令清单**（按文档出现顺序整理）：

### 一、固件与驱动安装（前置条件）

```shell
chmod +x Ascend-hdk-<chip_type>-npu-driver_<version>_linux-<arch>.run
chmod +x Ascend-hdk-<chip_type>-npu-firmware_<version>.run
./Ascend-hdk-<chip_type>-npu-driver_<version>_linux-<arch>.run --full --force
./Ascend-hdk-<chip_type>-npu-firmware_<version>.run --full
```

### 二、镜像安装路径

```bash
# 1. 拉取镜像
docker pull mindspeed-core:26.0.0_core_r0.12.1-a3-openeuler24.03-py3.11-aarch64
# 验证
docker image list

# 2. 创建并启动容器
docker run -itd \
   --name mindspeed \
   --privileged \
   --network host \
   --ipc=host \
   -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
   -v /usr/local/dcmi:/usr/local/dcmi \
   -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
   -v /etc/ascend_install.info:/etc/ascend_install.info \
   -v /home:/home \
   -v /data:/data \
   -v /mnt:/mnt \
   mindspeed-core:26.0.0_core_r0.12.1-a3-openeuler24.03-py3.11-aarch64

# 3. 进入容器并验证 NPU
docker exec -it 容器名 bash
npu-smi info
```

### 三、源码安装路径

```shell
# 1. 配置 CANN 环境变量
source /usr/local/Ascend/cann/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh

# 2. 安装 PyTorch + TorchNPU（Python 3.10 示例）
pip3 install torch-2.7.1-cp310-cp310-manylinux_2_28_aarch64.whl
pip3 install torch_npu-2.7.1post4-cp310-cp310-manylinux_2_28_aarch64.whl

# 3. 克隆 MindSpeed 源码并切换 master 分支
git clone https://gitcode.com/Ascend/MindSpeed.git
cd MindSpeed
git checkout master
cd ..

# 4. 安装 MindSpeed（可编辑模式）
pip install -e MindSpeed

# 5. 克隆 Megatron-LM 并切换到 core_v0.12.1 分支
git clone https://github.com/NVIDIA/Megatron-LM.git
cd Megatron-LM
git checkout core_v0.12.1
cd ..
```

### 四、卸载

```shell
pip uninstall -y mindspeed   # 注意命令中为小写 mindspeed
```

### 五、关键约束汇总

|项|约束|
|--|--|
|架构|最新镜像仅支持 aarch64（通过 `uname -a` 验证）|
|驱动/固件路径|默认 `/usr/local/Ascend`，需按实际修改|
|安装用户|建议非 root；目录权限 750，文件权限 640，`umask 0027`|
|Python 版本|镜像路径 = 3.11（`py3.11` 标签）；源码路径示例 = 3.10（`cp310` wheel）|
|Megatron-LM 分支|`core_v0.12.1`|
|MindSpeed 分支|`master`（镜像路径固定到 `26.0.0_core_r0.12.1`）|
