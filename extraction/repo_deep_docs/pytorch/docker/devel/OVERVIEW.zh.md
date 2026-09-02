# TorchNPU devel

> 仓 `pytorch` · 路径 `docker/devel/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docker/devel/OVERVIEW.zh.md

# 一体化深度解读：TorchNPU devel 镜像说明文档

## 【定位】

本文档解决的是 **TorchNPU 二次开发与 wheel 编译的容器化环境问题**：描述了 `torch-npu-devel` 开发镜像的能力边界、Tag 规范、构建参数矩阵、运行期设备透传方式以及基于该镜像进行二次扩展的工程模板。

## 【技术要点】

1. **镜像定位**：在 `builder` 镜像（manylinux + Python + gcc-toolset + cmake + PyTorch CPU 依赖）基础上叠加 CANN 工具包（Toolkit + Ops，可选 NNAL），用于在容器内完成 TorchNPU wheel 编译并直接在 NPU 上运行。镜像本身不含 Driver，需宿主机自行安装。

2. **Tag 命名规范**：`<PyTorch版本号>-<CANN版本>-<硬件信息（芯片）>-<操作系统>`，以 `2.13.0-cann9.1.0-910b-manylinux_2_28` 为代表，将版本/芯片/OS 信息编码进镜像标识。

3. **硬件覆盖范围**：CANN 产品映射表覆盖 5 款昇腾硬件：`910b` → Atlas A2 系列、`910` → Atlas 训练系列、`310p` → Atlas 推理系列、`A3` → Atlas A3 系列、`950` → Atlas 350 加速卡。

4. **Python 多版本支持**：支持 `3.10 / 3.11 / 3.12 / 3.13 / 3.14`，默认 `3.10`；通过 `PY_VERSION` 构建参数控制；切换方式为重定向 `python`/`pip` 软链到 `/opt/python/cpXY-cpXY`。

5. **关键构建参数 `CANN_RELEASE_TRAIN`**：当 `CANN_VERSION` 与默认值 `9.1.0` 不同时，必须同时指定 `CANN_RELEASE_TRAIN`（如 `CANN%209.1.0`），原因是 OBS 上 `.run` 包按 release train 分目录存放（如 `CANN%209.1.T1`、`CANN%209.1.0`），目录名无法由版本号自动推导，否则构建报错退出。

6. **容器运行期设备透传**：必须挂载 `/dev`、`/usr/local/Ascend/driver`、`/usr/local/Ascend/add-ons`、`/usr/local/sbin/npu-smi` 到容器、挂载 `/var/log/npu` 到 `/usr/slog`，并通过 `LD_LIBRARY_PATH` 串联 driver 的 `lib64`/`lib64/base`/`lib64/common`/`lib64/driver` 四个目录。

## 【关键机制与数据】

- **工作原理（原文）**：`torch-npu-devel` 镜像在 `builder` 镜像基础上集成 CANN 工具包，使用户可在容器内完成 TorchNPU wheel 编译，并直接在 NPU 上运行。
- **数据流 / 编译路径（原文）**：编译流程、参数与脚本使用方式详见镜像内的 README.md 与 `Dockerfile` + `builder.sh`。
- **设备验证命令（原文）**：`docker exec torch-npu-devel npu-smi info`，输出 NPU 卡列表则挂载成功。
- **最小权限替代（原文）**：可改用显式 `--device=/dev/davinci0 --device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc`，每张卡需单独 `--device`。
- **性能数据**：原文未涉及。
- **代理支持（原文）**：若构建环境需代理，通过 `--build-arg HTTP_PROXY/HTTPS_PROXY/NO_PROXY` 传入。

## 【表格解读】

### 表格 1：Tag 字段规范

| 字段            | 值                          | 说明                      |
|-----------------|----------------------------|---------------------------|
| PyTorch 版本号 | 2.13.0                     | 镜像内预装的PyTorch版本 |
| CANN 版本       | 9.1.0                      | 镜像内预装的CANN版本 |
| 硬件信息（芯片） | 310p / 910 / 910b / a3 / 950 | 镜像适用的昇腾芯片型号        |
| 操作系统        | manylinux_2_28              | 基础镜像所使用的操作系统发行版 |

**解读**：四段式 Tag 是镜像唯一标识，前两段是软件栈版本（PyTorch + CANN），第三段是目标硬件（决定 `CANN_PRODUCT` 取值），第四段是基础 OS。Python 版本（默认 3.10）通过 `PY_VERSION` 构建参数控制，不进入 Tag。

### 表格 2：Dockerfile 构建参数

| 参数               | 说明                                                                | 必填 | 参考来源            | 参数取值                       |
|--------------------|------------------------------------------------------------------|----|-------------------|----------------------------|
| PY_VERSION         | Python 版本，仅安装对应版本依赖                                          | 是  | manylinux 镜像      | 3.10                        |
| TORCH_VERSION      | PyTorch 版本，格式 `x.x.x`（如 `2.13.0`）或 dev 版本（如 `2.13.0.dev20260610`） | 是  | TorchNPU 仓库发行版  | 2.13.0                      |
| DEVTOOLSET_VERSION | GCC toolset 版本                                              | 否  | Dockerfile 默认值   | 13                          |
| CANN_VERSION       | 昇腾 CANN 工具包版本                                               | 是  | CANN 基础镜像仓库   | 9.1.0                       |
| CANN_PRODUCT       | CANN 算子包产品类型                                               | 是  | CANN 产品映射       | 910b                        |
| INSTALL_NNAL       | 是否安装 NNAL 神经网络加速库                                         | 否  | Dockerfile 默认值   | 0                           |
| CANN_RELEASE_TRAIN | CANN 发布版本号，当 `CANN_VERSION` 与默认值不同时需手动指定                  | 否  | CANN 下载目录       | CANN%209.1.0                |

**解读**：参数分为三类：① 必填软件栈参数（`PY_VERSION`、`TORCH_VERSION`、`CANN_VERSION`、`CANN_PRODUCT`），对应 Tag 中的前三段；② 可选默认值参数（`DEVTOOLSET_VERSION=13`、`INSTALL_NNAL=0`），用于微调构建；③ 条件必填参数 `CANN_RELEASE_TRAIN`，仅当 CANN 版本非默认值时启用，对应 OBS 下载目录的 URL 编码命名。

### 表格 3：CANN 产品映射

| 产品代码   | 对应产品              |
|------------|-----------------------|
| `910b`     | Atlas A2 系列         |
| `910`      | Atlas 训练系列        |
| `310p`     | Atlas 推理系列        |
| `A3`       | Atlas A3 系列         |
| `950`      | Atlas 350 加速卡      |

**解读**：这是 `CANN_PRODUCT` 与昇腾硬件产品线的对应表，决定了构建时下载哪一套算子包。需注意产品代码大小写敏感（`910b`、`910`、`310p` 全小写，`A3`、`950` 全大写），与 Tag 中的芯片段保持一致。

### 表格 4：构建命令矩阵（5 个 Tag 各对应一行完整 `docker build` 命令）

| 镜像 Tag | 构建命令（核心字段） |
|---|---|
| `2.13.0-cann9.1.0-310p-manylinux_2_28` | `docker build --target dev --build-arg PY_VERSION=3.10 --build-arg TORCH_VERSION=2.13.0 --build-arg CANN_VERSION=9.1.0 --build-arg CANN_PRODUCT=310p --build-arg CANN_RELEASE_TRAIN="CANN%209.1.0" -t <registry>/torch-npu-devel:2.13.0-cann9.1.0-310p-manylinux_2_28 --push .` |
| `2.13.0-cann9.1.0-910-manylinux_2_28` | `--build-arg CANN_PRODUCT=910`，其余同上 |
| `2.13.0-cann9.1.0-910b-manylinux_2_28` | `--build-arg CANN_PRODUCT=910b`，其余同上 |
| `2.13.0-cann9.1.0-a3-manylinux_2_28` | `--build-arg CANN_PRODUCT=A3`，其余同上 |
| `2.13.0-cann9.1.0-950-manylinux_2_28` | `--build-arg CANN_PRODUCT=950`，其余同上 |

**解读**：5 条命令除 `CANN_PRODUCT` 与 Tag 名外完全一致，体现了参数化构建的设计：版本号/操作系统/Python 锁定后，硬件差异通过单参数切换。多架构（x86 + arm）需分别制作后合并。

### 表格 5：二次开发场景对照

| 场景 | 目标镜像 | 说明 |
|------|----------|------|
| 仅编译 TorchNPU wheel | `builder` | manylinux + Python + gcc-toolset + cmake + PyTorch CPU 依赖，不含 CANN；无需 NPU 驱动 |
| 编译并运行于 NPU | `dev` | 在 `builder` 基础上叠加 CANN（Toolkit + Ops，可选 NNAL）；需宿主机已安装 NPU 驱动 |

**解读**：将用户场景拆成「纯编译」与「编译+运行」两类，引导用户按是否需要 NPU 实机验证来选择基镜像，避免给纯编译场景引入不必要的 CANN 与驱动依赖。

## 【公式解读】

原文无公式。

## 【关联】

- **同目录上位文档 `./OVERVIEW.md`**：本文档是其中文翻译/镜像版本，提供英文原文以便交叉核对。
- **构建细节 `./README.md`**：本文档把"Dockerfile 及构建脚本的更多细节"显式下转给该 README；同时，二次开发章节也指向 `https://gitcode.com/Ascend/pytorch/blob/master/docker/devel/README.md` 作为镜像内构建流程、参数与脚本使用方式的权威说明。
- **上下游模块**：
  - 上游：`builder` 镜像（manylinux + Python + gcc-toolset + cmake + PyTorch CPU 依赖），是 `dev` 镜像的基底；
  - 下游：用户在 `dev` 镜像上 `FROM` 自定义层叠加自有软件（如 `yum install -y gcc ...`）以生产业务镜像；
  - 配套组件：CANN Toolkit + Ops（强制）、NNAL（可选）、NPU Driver（宿主机侧，不在镜像内）。
- **社区资源链接**：AscendHub 镜像仓库、TorchNPU 官方文档、昇腾开发者社区、gitcode 问题反馈入口，构成完整的支持链路。

## 【使用方法】

### 1. 构建镜像（以 `2.13.0-cann9.1.0-910b-manylinux_2_28` 为例）

```bash
docker build \
  --target dev \
  --build-arg PY_VERSION=3.10 \
  --build-arg TORCH_VERSION=2.13.0 \
  --build-arg CANN_VERSION=9.1.0 \
  --build-arg CANN_PRODUCT=910b \
  --build-arg CANN_RELEASE_TRAIN="CANN%209.1.0" \
  -t image_name:tag \
  -f Dockerfile .
```

需代理时追加：`--build-arg HTTP_PROXY=… --build-arg HTTPS_PROXY=… --build-arg NO_PROXY=localhost,127.0.0.1`。

### 2. 运行容器（含 NPU 透传）

```bash
docker run -d --rm \
    --name torch-npu-devel \
    --privileged \
    -v /dev:/dev \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /usr/local/Ascend/add-ons:/usr/local/Ascend/add-ons \
    -v /usr/local/sbin/npu-smi:/usr/local/bin/npu-smi \
    -v /var/log/npu:/usr/slog \
    -e LD_LIBRARY_PATH=/usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64/base:/usr/local/Ascend/driver/lib64/common:/usr/local/Ascend/driver/lib64/driver \
    -it torch-npu-devel:2.13.0-cann9.1.0-910b-manylinux_2_28 \
    tail -f /dev/null
```

验证：`docker exec torch-npu-devel npu-smi info`。

### 3. 基于 `dev` 镜像二次扩展（示例）

```dockerfile
FROM <your-registry>/torch-npu-devel:2.13.0-cann9.1.0-910b-manylinux_2_28
RUN yum install -y gcc ...
```

### 4. Python 版本切换

- 默认 `3.10`；支持 `3.10 / 3.11 / 3.12 / 3.13 / 3.14`；
- 切换方式：将 `python`/`pip` 软链重新指向 `/opt/python/cpXY-cpXY` 解释器；
- 切换为非默认 Python 后需手动重新下载对应的编译与开发依赖；
- torch CPU whl 的 ABI 标签（`cp310`/`cp311`/`cp312`/`cp313`/`cp314`）由 `pip` 根据当前解释器自动选择，无需手动指定。

### 5. 最小权限运行（原文有则写）

将 `--privileged` 替换为显式设备透传：`--device=/dev/davinci0 --device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc`（每张卡单独 `--device`）。
