# MindSpeed Core Docker Image Overview

> 仓 `mindspeed` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docker/OVERVIEW.md

# MindSpeed Core Docker Image Overview 深度解读

## 【定位】
本篇文档解决的核心问题是：**如何构建、获取并运行 MindSpeed Core 的 Docker 镜像**，为昇腾 NPU 大模型训练与开发场景提供一份覆盖"镜像规格 → 标签规范 → 构建参数 → 启动命令 → 兼容性说明"的标准化使用指南。

---

## 【技术要点】

1. **镜像命名与基镜像**  
   - 镜像名称：`mindspeed-core`  
   - 默认基镜像：`swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.11`（可配置）  
   - 默认工作目录：`/MindSpeed`

2. **标签 (Tag) 命名模板**  
   - 模板：`{mindspeed_version}-cann{cann_version}-torch_npu{TorchNPU_version}-{npu_type}-{os}-py{python_version}`  
   - NPU 类型必须小写：`a3`、`910b`、`950`  
   - 示例：`v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-910b-ubuntu22.04-py3.11`

3. **多架构镜像 (multi-arch)**  
   - 镜像构建后会生成 `-aarch64` / `-x86_64` 后缀  
   - 已发布的 6 个标签（原文表格）均同时支持 x86 与 aarch64

4. **统一 Dockerfile + 构建脚本结构**  
   - 入口：`docker/build.sh`  
   - 通过参数选择 CANN 基镜像的 OS、NPU 类型、Python 版本、CANN 版本、目标架构

5. **构建参数 (build script) 默认值**  
   - `--npu-type`: `910b`；`--os`: `openeuler24.03`；`--arch`: 当前主机架构  
   - `--base-image-version`: `9.1.0`；`--python-version`: `3.11`  
   - `--torch-version`: `2.7.1`；`--torch-npu-version`: `2.7.1.post8`  
   - `--numpy-version`: `1.26.0`（在所有依赖安装完成后"恢复"）  
   - `--mindspeed-branch`: `v26.1.0_core_r0.12.1`；`--megatron-branch`: `core_v0.12.1`

6. **容器运行与挂载**  
   - 必须挂载的驱动/信息目录：`/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info`  
   - 必须挂载的数据目录：`{path-to-data}:/data`、`{path-to-weights}:/weights`  
   - 运行时参数：`--privileged --network host --ipc=host`

7. **代理变量透传**  
   - 若宿主机设置了 `http_proxy` / `https_proxy` / `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` / `no_proxy`，`build.sh` 会自动作为 build-arg 转发，且**不持久化**进最终镜像。

---

## 【关键机制与数据】

### 镜像版本与软件栈（原文）
- MindSpeed Core 版本：`v26.1.0_core_r0.12.1`
- CANN 基镜像版本：`9.1.0`
- TorchNPU 版本：`2.7.1.post8`
- Megatron-LM ref：`core_v0.12.1`
- 操作系统组合：`openeuler24.03` 与 `ubuntu22.04`
- NPU 类型组合：`a3`、`910b`、`950`
- Python 版本：`py3.11`

### 标签生成机制（原文）
- 多架构镜像构建完成后，会自动追加架构后缀：`-aarch64` 或 `-x86_64`  
- 示例：`v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.11-aarch64`

### `--base-image` 与 `--base-image-version` 关系（原文）
- `--base-image` 优先级**高于** `--base-image-version`；其值**按原样透传**，因此必须**完全匹配**已发布的 CANN 镜像名；脚本会尝试从 tag 中自动识别 CANN 版本、NPU 类型、操作系统与 Python 版本。

### 软件安装顺序（原文）
- 依次安装 PyTorch → TorchNPU → MindSpeed Core → Megatron-LM → `requirements.txt` 中的 Python 依赖 → 恢复并校验 PyTorch / TorchNPU / NumPy 版本（NumPy 在所有依赖完成后回滚到 `1.26.0`）。

### 容器代码克隆路径（原文）
- MindSpeed 克隆至 `/MindSpeed`
- Megatron-LM 克隆至 `/Megatron-LM`

> 文档未提供性能数据、吞吐/延迟等基准指标。

---

## 【表格解读】

### 表格 1：Quick Reference（逐字还原）

| Name | Description |
| ------ | ------ |
| Image name | `mindspeed-core` |
| Source repository | [https://gitcode.com/Ascend/MindSpeed](https://gitcode.com/Ascend/MindSpeed) |
| Dockerfile path | `docker/Dockerfile` |
| Default scenario | MindSpeed Core training and development |
| Base image | Configurable CANN image, defaulted to `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.11` |
| Default working directory | `/MindSpeed` |

**逐行解读**  
- **Image name**: 镜像名固定为 `mindspeed-core`，所有版本都共用该仓库名，差异仅在 tag。  
- **Source repository**: 上游仓库地址，对应 Megatron-LM 加速库 MindSpeed。  
- **Dockerfile path**: 所有版本共用同一 Dockerfile (`docker/Dockerfile`)，通过 build script 传入不同参数切换变体。  
- **Default scenario**: 该镜像默认面向 MindSpeed Core 的训练与开发用途。  
- **Base image**: 唯一默认基镜像为 CANN 9.1.0 + 910B + openEuler 24.03 + Python 3.11，可被覆盖。  
- **Default working directory**: 容器内默认工作路径 `/MindSpeed`，与 MindSpeed 源码 clone 路径一致。

---

### 表格 2：Latest CANN 9.1.0（逐字还原）

| Tag | Dockerfile | Content |
| ------ | ------ | ------ |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-ubuntu22.04-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-910b-ubuntu22.04-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-950-openeuler24.03-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-950-ubuntu22.04-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |

**逐行解读**  
- 第 1 行：A3 芯片 + openEuler 24.03 组合的预构建镜像。  
- 第 2 行：A3 芯片 + Ubuntu 22.04 组合，预构建镜像。  
- 第 3 行：910B 芯片 + openEuler 24.03 组合（即默认基镜像组合）。  
- 第 4 行：910B 芯片 + Ubuntu 22.04 组合。  
- 第 5 行：950 芯片 + openEuler 24.03 组合（针对新一代 950 NPU）。  
- 第 6 行：950 芯片 + Ubuntu 22.04 组合。  
- **共同点**：所有 6 个 tag 都共享相同的 MindSpeed / CANN / TorchNPU 版本，差异仅在 NPU 型号与 OS；所有 Dockerfile 链接都指向同一份源码中的 `docker/Dockerfile`，印证"统一 Dockerfile + 多参数变体"的机制；Content 字段均为 `MindSpeed-Core/Megatron-LM`，说明镜像同时打包了 MindSpeed Core 与上游 Megatron-LM。

---

### 表格 3：Build Parameters（逐字还原）

| Name | Description | Default Value |
| ------ | ------ | ------ |
| `-t, --npu-type` | NPU type: `a3`, `910b`, or `950` | `910b` |
| `-o, --os` | Operating system: `openeuler24.03` or `ubuntu22.04` | `openeuler24.03` |
| `-a, --arch` | Target architecture: `aarch64` or `x86_64` | Current host architecture |
| `--base-image-version` | CANN base image version | `9.1.0` |
| `--base-image` | Full CANN base image name, which takes precedence over `--base-image-version`; it is passed through as-is | Empty |
| `--python-version` | Python tag in the CANN base image | `3.11` |
| `--torch-version` | PyTorch version | `2.7.1` |
| `--torch-npu-version` | TorchNPU version | `2.7.1.post8` |
| `--numpy-version` | NumPy version restored after all dependency installation steps | `1.26.0` |
| `--mindspeed-branch` | MindSpeed branch/tag/ref to clone | `v26.1.0_core_r0.12.1` |
| `--megatron-branch` | Megatron-LM branch/tag/ref to checkout | `core_v0.12.1` |
| `--image-version` | MindSpeed version field used in the default image tag | `v26.1.0_core_r0.12.1` |

**逐行解读**  
- `-t / --npu-type`：唯一允许的三个取值 `a3 / 910b / 950`，默认 `910b`，与 CANN 镜像名必须保持一致。  
- `-o / --os`：仅支持 `openeuler24.03` 与 `ubuntu22.04` 两种发行版。  
- `-a / --arch`：决定最终 tag 的后缀；若不指定，则跟随宿主机架构（动态识别）。  
- `--base-image-version`：缺省 CANN 版本 `9.1.0`，用于从基镜像仓库按版本号拼接镜像名。  
- `--base-image`：当用户给定完整 CANN 镜像名时，**直接覆盖** `--base-image-version`，并且不会做任何改写；这是用户级"硬指定"机制。  
- `--python-version`：从基镜像中提取 Python tag 的依据，默认 `3.11`。  
- `--torch-version` / `--torch-npu-version`：分别决定 PyTorch 与 TorchNPU 安装版本，二者必须协同对应（TorchNPU 必须为 `post8` 后缀版本以匹配 `2.7.1`）。  
- `--numpy-version`：特殊处理——在 MindSpeed / Megatron-LM / requirements 等所有依赖**安装完成后再回退**到 `1.26.0`，避免依赖图把 NumPy 升级到不兼容版本。  
- `--mindspeed-branch`：从仓库拉取的 MindSpeed 源码 ref，默认与当前发布版本一致。  
- `--megatron-branch`：与 MindSpeed Core 协同的 Megatron-LM 分支，默认 `core_v0.12.1`。  
- `--image-version`：用于在缺省 tag 模板里填充 `{mindspeed_version}` 字段，默认与 `--mindspeed-branch` 一致。

---

## 【公式解读】

原文无公式。

---

## 【关联】

虽然用户提示"内部链接: (无)"，但文档本身在文末与正文中提到了多个外链，可视为该 overview 与仓内其他模块的关联：

1. **上游源代码**：[https://gitcode.com/Ascend/MindSpeed](https://gitcode.com/Ascend/MindSpeed)  
   - 文档中所有 Dockerfile、build script、MindSpeed 源码、Megatron-LM 子模块都源自该仓库。

2. **Dockerfile**：[`docker/Dockerfile`](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile)  
   - 是本 overview 所描述的所有变体（a3/910b/950 × openeuler/ubuntu）的**唯一**定义源；本篇文档是它的"用户视角说明"。

3. **历史版本标签表**：[`docker/support_tags.md`](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/support_tags.md)  
   - 文档将历史版本的 tag 集合托管在该页面，作为对本文"CANN 9.1.0 最新表"的补集。

4. **构建脚本 `docker/build.sh`**  
   - 是文档中所有"构建参数"、"Quick Start"、"代理透传"机制的运行时实现。

5. **`/Megatron-LM` 子模块**  
   - 通过 `--megatron-branch` 参数控制，与 MindSpeed Core 在容器内一同被打包，构成"MindSpeed-Core/Megatron-LM" 内容组合（与上文 6 行 tag 表的 Content 字段对应）。

6. **昇腾驱动与 dcmi 主机路径**  
   - 文档要求挂载的 `/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info` 均为**宿主机昇腾运行环境**的标准路径——这是镜像与外部 Ascend 驱动栈的边界接口。

7. **许可证**：[`LICENSE`](https://gitcode.com/Ascend/MindSpeed/blob/master/LICENSE)  
   - MindSpeed 主体遵循 Apache License 2.0；镜像内还可能包含其他许可证（如 base 发行版里的 Bash）。

---

## 【使用方法】

### 1. 默认构建（原文）
```bash
cd docker
bash build.sh
```
等价于使用所有参数默认值（910B / openEuler 24.03 / 当前主机架构 / CANN 9.1.0 / Python 3.11）。

### 2. 指定 NPU + OS + 架构（原文）
```bash
cd docker
bash build.sh -t a3 -o openeuler24.03 -a aarch64
```
用于构建 A3 + openEuler + aarch64 + CANN 9.1.0 的基镜像。

### 3. 直接传入完整基镜像名（原文）
```bash
cd docker
bash build.sh \
  --arch aarch64 \
  --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.11
```
脚本将自动从 tag 解析出 CANN 版本 / NPU 类型 / OS / Python 版本。

### 4. 拉取已发布镜像（原文）
```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/mindspeed-core:v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11
```

### 5. 启动容器（原文，需替换 `{path-to-data}` 与 `{path-to-weights}`）
```bash
docker run -it -d \
  --name mindspeed-core \
  --privileged \
  --network host \
  --ipc=host \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v {path-to-data}:/data \
  -v {path-to-weights}:/weights \
  swr.cn-south-1.myhuaweicloud.com/ascendhub/mindspeed-core:v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11 \
  bin/bash
```

### 6. 进入运行中的容器（原文）
```bash
docker exec -it mindspeed-core /bin/bash
```

### 7. 兼容性切换路径（原文）
可通过 `docker/build.sh` 切换：操作系统、`a3 / 910b / 950` NPU 类型、目标架构（aarch64 / x86_64）、CANN 基镜像版本。其余可配置维度（如 MindSpeed 分支、Megatron-LM 分支、PyTorch / TorchNPU / NumPy 版本）通过对应参数注入。
