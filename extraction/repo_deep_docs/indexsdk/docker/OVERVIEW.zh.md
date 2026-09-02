# Index SDK

> 仓 `indexsdk` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/indexsdk/docker/OVERVIEW.zh.md

# Index SDK Docker 镜像 OVERVIEW 一体化深度解读

## 【定位】
这篇文档解决"如何在华为昇腾 NPU 上以 Docker 容器化方式部署与运行 Index SDK（基于昇腾的高效向量特征检索引擎）"的问题，给出镜像 Tag 规范、设备挂载方式、算子生成、入门用例编译运行及本地构建的完整开箱流程。

---

## 【技术要点】

1. **镜像 Tag 命名规范**：`{indexsdk版本}-{芯片系列}-{操作系统}-{python版本}`，示例 `26.1.0-cann9.1.0-910b-ubuntu22.04-py3.12`。版本号 `26.1.0`，芯片系列覆盖 `950 / 910b / a3 / 310p` 四款，操作系统为 `ubuntu22.04` 与 `openeuler24.03` 两种，Python 仅支持 `py3.12`。

2. **驱动与 Docker 版本前置**：宿主机的 NPU 驱动必须与容器内 CANN 版本兼容（参照 [CANN 兼容性矩阵](https://www.hiascend.com/document)），Docker 版本"建议不低于 24.0.x"。

3. **设备/驱动挂载策略**：NPU 加速卡 `/dev/davinci` 按需挂载（如样例中 `--device /dev/davinci1` 表示挂载 1 号设备），NPU 管理设备 `/dev/davinci_manager /dev/devmm_svm /dev/hisi_hdc` 全部挂载；驱动与工具链（`/usr/local/Ascend/driver`、`/usr/local/bin/npu-smi`、`/usr/local/dcmi` 等）以只读方式挂载，确保容器内运行环境与宿主机一致。

4. **算子生成流水线**：在容器内 `/usr/local/Ascend/mxIndex/ops` 执行 `custom_opp_*.run`，再切换到 `tools` 目录运行 `aicpu_generate_model.py -t npu-type` 与 `flat_generate_model.py -t npu-type -d 512`，最后将生成的模型 `mv op_models/* $MX_INDEX_MODELPATH`。其中 `-d 512` 为显式参数。

5. **入门用例编译命令链**：`g++ --std=c++11 -fPIC -fPIE -fstack-protector-all -Wall -D_FORTIFY_SOURCE=2 -O3` 启用 C++11、栈保护、源码级加固与 O3；链接 `-lfaiss -lascendfaiss -lopenblas -lc_sec -lascendcl -lascend_hal -lascendsearch -lock_hmm`，体现 Index SDK 在 CPU 侧对 FAISS、OpenBLAS 与昇腾 HAL/CL 的协同依赖。

6. **关键路径常量**：`MX_INDEX_INSTALL_PATH` 默认 `/usr/local/Ascend/mxIndex`（Index SDK 安装路径），`ASCEND_HOME_PATH` 默认 `/usr/local/Ascend/cann`（Toolkit 安装路径）。

7. **本地构建镜像命令**：`docker build -t {your_repo}/index:latest -f Dockerfile .`，即用仓库根目录下的 Dockerfile 产出本地标签镜像。

---

## 【关键机制与数据】

**工作原理与数据流（原文表述的部署链）**：

- 文档未涉及向量索引的算法机制（如 IVF/HNSW/Flat 等），其描述的是**容器化交付与运行链**：
  - **静态资产层**：镜像内置 `toolkit + Index SDK` 两类组件，对应 §2.2 表格中每一行的"镜像内容"列。
  - **运行时桥接层**：通过 `--device` 把宿主机的 NPU 字符设备透传给容器，并通过 `-v` 把驱动库、版本信息文件、`npu-smi` 工具等以只读卷挂入，使容器内进程看到的驱动版本、ABI 与宿主机保持一致。
  - **算子即席生成层**：进入容器后，Operator 通过 `custom_opp_*.run` + `aicpu_generate_model.py` + `flat_generate_model.py -d 512` 流程在运行时按当前 NPU 类型（`-t npu-type`）产出算子模型，并放入 `MX_INDEX_MODELPATH` 环境变量指向的路径供 Index SDK 加载。
  - **应用层**：Demo 使用 `g++` 直接编译 C++ 源码链接 `-lascendsearch -lascendfaiss` 等库，完成一次端到端的检索调用（`./demo`）。

**性能数据**：原文未给出 QPS、召回率、延迟等任何性能数字，亦未给出测试条件。**（原文无性能数据）**

---

## 【表格解读】

### 表 1：Tag 字段规范（§2.1，原文表格逐字还原）

| 字段         | 示例值                          | 说明             |
| ------------ | ------------------------------- | ---------------- |
| `indexsdk版本`   | `26.1.0`              | Index SDK 版本号      |
| `芯片系列`   | `950`、`910b`、`a3`、`310p`            | 目标芯片系列 |
| `操作系统`   | `ubuntu22.04`、`openeuler24.03` | 基础操作系统     |
| `python版本` | `py3.12`    | Python 版本      |

**逐行解读**：

- **`indexsdk版本` = `26.1.0`**：标识 Index SDK 自身的语义化版本号，是 Tag 的最高层级，决定 SDK API 与算子格式。
- **`芯片系列` ∈ {`950`, `910b`, `a3`, `310p`}`**：列出 4 款目标 NPU，每款对应一份独立的 Dockerfile（见表 2），意味着镜像内 CANN Tookit 与算子包均按芯片系列差异化编译。
- **`操作系统` ∈ {`ubuntu22.04`, `openeuler24.03`}`**：基础 OS 二选一，每款芯片都分别提供 Ubuntu 与 openEuler 两份 Dockerfile（合计 4 × 2 = 8 份）。
- **`python版本` = `py3.12`**：当前唯一受支持的 Python 版本，Tag 字段为强制项。

### 表 2：CANN 9.1.0 + 26.1.0 Index SDK 镜像清单（§2.2，原文表格逐字还原）

| Tag                                | Dockerfile                                                   | 镜像内容        |
| ---------------------------------- | ------------------------------------------------------------ | --------------- |
| `26.1.0-cann9.1.0-910b-ubuntu22.04-py3.12`    | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.910b.ubuntu) | toolkit + Index SDK |
| `26.1.0-cann9.1.0-310p-ubuntu22.04-py3.12`    | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.310p.ubuntu)      | toolkit + Index SDK |
| `26.1.0-cann9.1.0-a3-ubuntu22.04-py3.12`    | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.a3.ubuntu)         | toolkit + Index SDK |
| `26.1.0-cann9.1.0-950-ubuntu22.04-py3.12`    | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.950.ubuntu)         | toolkit + Index SDK |
| `26.1.0-cann9.1.0-910b-openeuler24.03-py3.12`    | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.910b.openeuler) | toolkit + Index SDK |
| `26.1.0-cann9.1.0-310p-openeuler24.03-py3.12`    | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.310p.openeuler)      | toolkit + Index SDK |
| `26.1.0-cann9.1.0-a3-openeuler24.03-py3.12`    | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.a3.openeuler)         | toolkit + Index SDK |
| `26.1.0-cann9.1.0-950-openeuler24.03-py3.12`    | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.950.openeuler)         | toolkit + Index SDK |

**逐行解读**：

- 8 条 Tag **全部固定** `26.1.0-cann9.1.0-{chip}-{os}-py3.12`，即同一份 SDK（26.1.0） + 同一份 CANN（9.1.0） + 同一份 Python（3.12），仅在芯片（910b/310p/a3/950）与操作系统（ubuntu22.04/openeuler24.03）维度上正交展开。
- 每行"镜像内容"列均为 `toolkit + Index SDK`：意味着用户拿到任一镜像，**无需额外安装 CANN Tookit** 即可使用 Index SDK；这是该容器化方案的核心价值（避免用户手工安装 CANN）。
- 每行均提供对应 Dockerfile 直链，便于审计镜像构建步骤或基于其二次定制。
- 镜像 Tag 中实际拼接的是 `cann9.1.0` 字样，但 §2.1 的 Tag 规范模板只列出 4 个字段。`cann9.1.0` 是 **隐含在镜像 Tag 内但未列入规范表** 的额外维度——文档未明示其来源，使用时应注意。

---

## 【公式解读】

**原文无公式。**（文档为 Docker 部署/运行指南，不涉及数学推导或算法公式）

---

## 【关联】

> 内部链接: (无)（用户已标注）

虽然文末未提供任何内部相对链接，但文档通过外部超链接与以下生态资源/模块形成上下游与配套关系：

- **上游/基础设施**：[CANN 兼容性矩阵](https://www.hiascend.com/document)（§3.1.1）——决定宿主机 NPU 驱动版本的选取依据，是容器能够正常加载 NPU 的前提。
- **代码与 API**：[IndexSDK 代码](https://gitcode.com/Ascend/IndexSDK)、[IndexSDK API 参考](https://gitcode.com/Ascend/IndexSDK/blob/master/docs/zh/api/README.md)、[IndexSDK 文档](https://www.hiascend.com/document/detail/zh/mindsdk/730/indexn/indexug/mxindexfrug_0002.html)——镜像内的 `Index SDK` 二进制对应的源码、API 与用户手册。
- **镜像分发**：[镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/indexsdk/)（§1）、样例 `-it swr.cn-south-1.myhuaweicloud.com/ascendhub/indexsdk:26.1.0-...`——文档 Tag 的实际拉取源。
- **示例与算子生成配套文档**：[算子生成](https://gitcode.com/Ascend/IndexSDK/blob/master/docs/zh/05_user_guide.md#%E8%87%AA%E5%AE%9A%E4%B9%89%E7%AE%97%E5%AD%90%E4%BB%8B%E7%BB%8D)（§3.3）、[demo 用例](https://gitcode.com/Ascend/IndexSDK/blob/master/docs/zh/05_user_guide.md#%E4%BD%BF%E7%94%A8%E6%A0%B7%E4%BE%8B)（§3.4）——容器内 `custom_opp_*.run` 与 g++ 编译命令所对应的官方用户指南章节。
- **许可链**：[cann-container-image LICENSE](https://github.com/Ascend/cann-container-image/blob/main/LICENSE)（§4）——镜像中预装的 CANN / Mind 系列软件的许可证源。
- **社区支持**：[issue 反馈](https://gitcode.com/Ascend/IndexSDK/issues)、[社区](https://www.hiascend.com/)（§1）——使用过程中遇到 NPU 设备挂载、算子生成失败、链接错误等问题时的求助通道。

---

## 【使用方法】

**1. 选择镜像 Tag（§2）**：按 `NPU 型号 → 操作系统` 选定 8 个 Tag 之一，例如 910b + Ubuntu 选 `26.1.0-cann9.1.0-910b-ubuntu22.04-py3.12`。

**2. 准备宿主机前置条件（§3.1）**：
- 安装与容器内 CANN 9.1.0 兼容的 NPU 驱动。
- Docker 版本 ≥ 24.0.x。

**3. 启动容器（§3.2）**：
```bash
docker run \
    --name index_container \
    --device /dev/davinci1 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -it atlas/index:tag bash
```
- `--device /dev/davinci<N>`：按需替换 `1` 为所需 NPU 编号；多卡场景需多次声明。
- 全部 3 个管理设备 (`davinci_manager / devmm_svm / hisi_hdc`) 必须保留。
- `-v` 全部为只读挂载（文档表述"以只读方式挂载"），保证容器内 ABI 与宿主机一致。

**4. 容器内生成算子（§3.3）**：
```bash
cd /usr/local/Ascend/mxIndex/ops
./custom_opp_*.run
cd ../tools
python3 aicpu_generate_model.py -t npu-type
python3 flat_generate_model.py -t npu-type -d 512
mv op_models/* $MX_INDEX_MODELPATH
```
- `-t npu-type`：替换为当前 NPU 类型标识（如 `910b` / `310p` 等）。
- `-d 512`：flat 算子维度参数，原文显式给出。
- `$MX_INDEX_MODELPATH`：用户需自行 export 的环境变量，指向算子模型落盘目录。

**5. 编译入门用例（§3.4）**：
```bash
export MX_INDEX_INSTALL_PATH=/usr/local/Ascend/mxIndex

g++ --std=c++11 -fPIC -fPIE -fstack-protector-all -Wall -D_FORTIFY_SOURCE=2 -O3 -Wl,-z,relro,-z,now,-z,noexecstack -s -pie \
  -o demo demo.cpp \
  -I$MX_INDEX_INSTALL_PATH/include \
  -I/usr/local/faiss/include \
  -I/usr/local/Ascend/driver/include \
  -I/opt/OpenBLAS/include \
  -L$MX_INDEX_INSTALL_PATH/host/lib \
  -L/usr/local/faiss/lib \
  -L/usr/local/Ascend/driver/lib64 \
  -L/usr/local/Ascend/driver/lib64/driver \
  -L/opt/OpenBLAS/lib \
  -L$ASCEND_HOME_PATH/lib64 \
  -lfaiss -lascendfaiss -lopenblas -lc_sec -lascendcl -lascend_hal -lascendsearch -lock_hmm
```
- 需额外 export `ASCEND_HOME_PATH`（默认 `/usr/local/Ascend/cann`）。
- 编译标志强调安全加固（`-fstack-protector-all -D_FORTIFY_SOURCE=2 -Wl,-z,relro,-z,now,-z,noexecstack -pie`）与 O3 优化。

**6. 运行入门用例（§3.5）**：
```bash
./demo
```

**7. 本地自定义构建（§3.6）**：
```bash
docker build -t {your_repo}/index:latest -f Dockerfile .
```
- `{your_repo}` 替换为用户自有镜像仓库地址。
- `-f Dockerfile`：使用当前目录下的 Dockerfile 构建（注意：若构建的是芯片系列特定镜像，需指定 `Dockerfile.<chip>.<os>`）。

**8. 故障排查路径**（依据文档§1 列出但未给出具体命令）：通过 [issue 反馈](https://gitcode.com/Ascend/IndexSDK/issues) 或 [社区](https://www.hiascend.com/) 寻求支持。
