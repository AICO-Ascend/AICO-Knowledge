# Quick Start

> 仓 `triton-ascend` · 路径 `docs/en/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-ascend/docs/en/quick_start.md

# Triton-Ascend Quick Start 深度解读

## 【定位】

本文档是 Triton-Ascend（面向华为 Ascend NPU 的 Triton 适配版本）的快速入门指南，解决的是"如何在 Atlas A2/A3 NPU 上从零搭建 Triton-Ascend 运行环境并跑通首个示例"的问题，覆盖硬件/软件依赖、pip 安装、Docker 镜像构建、示例运行与结果验证全流程。

---

## 【技术要点】

1. **硬件平台范围**：仅支持 Linux（AArch64 / x86_64）+ Ascend Atlas A2/A3 系列；单设备最小显存 32 GB（原文标注为"recommended"）。
2. **软件依赖链路**：Python 3.9–3.13（Python 3.9 **不支持 AArch64**）+ CANN_TOOLKIT + CANN_OPS + `requirements.txt` + `requirements_dev.txt`；CANN 推荐版本 **9.0.0**，安装耗时原文记为"about 5 to 10 minutes"。
3. **包安装路径默认值**：root 用户安装到 `/usr/local/Ascend`；非 root 用户安装到 `${HOME}/Ascend`（`${HOME}` 为当前用户家目录），环境变量通过 `source ${HOME}/Ascend/ascend-toolkit/set_env.sh` 在当前终端会话生效。
4. **版本共存机制（自 3.5 起）**：Triton-Ascend 声明 Triton 为安装依赖，先装社区版 Triton、再由 Triton-Ascend 覆盖共享包目录，避免后续 Triton 重装覆盖 Triton-Ascend；x86 依赖 `triton==3.2.0`，arm 依赖 `triton==3.5.0`（原文解释：arm 安装包自 Triton 3.5 起才在社区可用）。
5. **Docker 构建可调参数**：`CHIP_TYPE`（A3 / 910B，默认 A3）、`CANN_VERSION`（9.0.0 / 8.5.0 / 8.3.RC1 / 8.3.RC2 / 8.2.RC1 / 8.2.RC2，默认 9.0.0）。
6. **示例验证成功判据**：运行 `01-vector-add.py` 后输出含 `The maximum difference between torch and triton is 0.0` 即视为环境配置正确。

---

## 【关键机制与数据】

- **覆盖式安装流程**：原文："When Triton-Ascend is installed, community Triton is installed first, and then Triton-Ascend overwrites the shared package directory." 这是 3.5 版本起引入的"声明依赖 → 先装后覆盖"机制，用于避免被其他依赖 Triton 的软件包在后续安装时覆盖。
- **覆盖式安装的局限**：原文："This solution mitigates the installation overwrite issue, but it does not completely eliminate the conflict caused by community Triton and Triton-Ascend sharing the same top-level `triton` package directory." 即若后续显式 reinstall/upgrade 社区 Triton，仍可能影响 Triton-Ascend，此时需先卸载二者再重装 Triton-Ascend。
- **Docker 自动下载**：原文："During installation, the corresponding CANN Toolkit and Kernel packages will be automatically downloaded from the official CANN website." 即构建过程会按 `CHIP_TYPE` / `CANN_VERSION` 自动拉取对应 CANN 组件，无需手动预装。
- **NPU 型号查询命令**：原文给出 `npu-smi` 用于在主机侧查看 NPU 型号。
- **运行时容器设备透传**：docker run 命令显式透传 8 个 `/dev/davinci0..7` 设备 + `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并挂载 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/sbin/npu-smi`、`/usr/local/Ascend/driver`、`/home`、`/etc/ascend_install.info`，配合 `--shm-size=512g`、`--privileged`、`--security-opt seccomp=unconfined`、`--net=host` 以提供 NPU 调度与驱动访问能力。
- **性能/数据相关**：原文未提供基准性能数据（如 FLOPS、带宽、时延数字），仅给出示例输出片段（`tensor([...], device='npu:0')`）和差值上限 `0.0` 作为正确性判据。

---

## 【表格解读】

### 表格 1：Docker 构建参数

**逐字还原**：

| Parameter Name | Default Value       | Available Options                                |
|----------------|---------------------|--------------------------------------------------|
| CHIP_TYPE      | A3                  | A3, 910B                                         |
| CANN_VERSION   | 9.0.0 (Recommended) | 9.0.0, 8.5.0, 8.3.RC1, 8.3.RC2, 8.2.RC1, 8.2.RC2 |

**逐行解读**：
- `CHIP_TYPE`：`A3`（默认）/ `910B`，决定构建时下载哪一款 CANN Toolkit + Kernel 组合；需与宿主机实际 NPU 型号对齐。
- `CANN_VERSION`：默认 `9.0.0 (Recommended)`，可选 `9.0.0 / 8.5.0 / 8.3.RC1 / 8.3.RC2 / 8.2.RC1 / 8.2.RC2` 共 6 个版本，按 NPU 卡型与官方兼容性选择。

### 表格 2：CHIP_TYPE 取值与对应服务器/产品系列

**逐字还原**：

| Option No. | **CHIP_TYPE Value** | Corresponding Server/Product Series | Typical Server Model |
|:----------:|:-------------------:|:----------------------------------:|:-----------------------------------:|
| 1 | `A3` | Atlas A3 Training Series | Atlas 900 A3 SuperPoD |
| 2 | `A2` | Atlas A2 Training Series | Atlas 800T A2 |

**逐行解读**：
- 第 1 行：`CHIP_TYPE=A3` 对应 Atlas A3 Training Series，典型服务器为 Atlas 900 A3 SuperPoD。
- 第 2 行：`CHIP_TYPE=A2` 对应 Atlas A2 Training Series，典型服务器为 Atlas 800T A2。

> 注意：表格 1 的 `Available Options` 中并未列出 `A2`，但表格 2 中 `CHIP_TYPE` 出现了 `A2` 取值，原文未对二者关系做进一步说明，遵循"不臆造"原则，此处仅做"原文存在"层面的标注。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **内部依赖文件**：[`../../requirements.txt`](../../requirements.txt) 与 [`../../requirements_dev.txt`](../../requirements_dev.txt)：分别在"Software Dependency"小节与 `pip install -r requirements.txt -r requirements_dev.txt` 命令中引用，是 pip 安装链路的 Python 包清单来源。
- **关联文档 [`installation_guide.md`](installation_guide.md)**：在 "Environment Setup" 小节被指向，其"Preparing the Environment"段落是本指南环境搭建步骤的更详细出处（即本文仅给出指引，详细步骤委派给该文档）。
- **示例脚本 [`../../third_party/ascend/tutorials/01-vector-add.py`](../../third_party/ascend/tutorials/01-vector-add.py)**：在 "Running Triton Examples" 小节作为首个可执行示例被引用，承担"验证环境正确性"的角色——其正确性指标（PyTorch vs Triton 最大差为 0.0）被原文化为成功判据。
- **外部依赖**：在线文档 https://triton-ascend.readthedocs.io/zh-cn/latest/index.html 与华为官方 CANN 安装说明 https://www.hiascend.com/document/detail/zh/canncommercial/850/softwareinst/instg/instg_0000.html，构成"在线文档 + CANN 安装指引"的上下游；PyPI 项目页 https://test.pypi.org/project/triton-ascend/#history 提供 nightly 包下载。
- **生态模块边界**：作为 Triton 的派生版本，Triton-Ascend 与上游社区 Triton 共享顶层 `triton` 包目录（原文明确指出此即覆盖冲突根源），因此与社区 Triton 之间存在"先装后覆盖"的紧耦合关系。

---

## 【使用方法】

**1. pip 安装（稳定版）**
```shell
pip install triton-ascend
```

**2. pip 安装（nightly 版，需先在 https://test.pypi.org/project/triton-ascend/#history 下载对应 Python 版本与 AArch64/x86_64 架构的 wheel）**

**3. 安装 Python 依赖**
```shell
pip install -r requirements.txt -r requirements_dev.txt
```

**4. 使 CANN 环境变量生效（默认 root 安装路径示例）**
```shell
source /usr/local/Ascend/ascend-toolkit/set_env.sh
# 非 root 用户：source ${HOME}/Ascend/ascend-toolkit/set_env.sh
```
可按需写入 `.bashrc` 等环境变量配置文件以跨会话生效。

**5. 查询 NPU 型号**
```shell
npu-smi
```

**6. Docker 镜像构建**
```bash
git clone https://gitcode.com/Ascend/triton-ascend.git && cd triton-ascend
docker build \
--build-arg CHIP_TYPE=A3 \
--build-arg CANN_VERSION=9.0.0 \
-t triton-ascend-image:latest -f ./docker/Dockerfile .
```

**7. 启动并进入容器**
```bash
docker run -u 0 -dit --shm-size=512g --name=triton-ascend_container --net=host --privileged \
--security-opt seccomp=unconfined \
--device=/dev/davinci0 --device=/dev/davinci1 --device=/dev/davinci2 --device=/dev/davinci3 \
--device=/dev/davinci4 --device=/dev/davinci5 --device=/dev/davinci6 --device=/dev/davinci7 \
--device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc \
-v /usr/local/dcmi:/usr/local/dcmi \
-v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
-v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
-v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
-v /home:/home \
-v /etc/ascend_install.info:/etc/ascend_install.info \
triton-ascend-image:latest \
/bin/bash

docker exec -u root -it triton-ascend_container /bin/bash
```

**8. 运行向量加示例并验证**
```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
git clone https://gitcode.com/Ascend/triton-ascend.git
python3 ./triton-ascend/third_party/ascend/tutorials/01-vector-add.py
```
预期输出含 `The maximum difference between torch and triton is 0.0` 即视为环境配置正确。

**9. 冲突修复（当社区 Triton 被显式重装/升级覆盖了 Triton-Ascend 时）**
按原文说明需先卸载社区 Triton 与 Triton-Ascend，再重装 Triton-Ascend。原文未涉及具体卸载命令。
