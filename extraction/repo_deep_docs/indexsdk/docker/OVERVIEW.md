# Index SDK

> 仓 `indexsdk` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/indexsdk/docker/OVERVIEW.md

# Index SDK Docker Overview 深度解读

## 【定位】
本文档是 Index SDK 在华为昇腾平台上的**Docker 镜像总览与快速上手指南**,核心解决两个问题:**1) 告知用户有哪些可用的容器化镜像标签(Tag)及其与不同 NPU 芯片/OS 的对应关系**;**2) 指导用户如何从拉取镜像、运行容器、生成算子模型,到编译并执行 Demo 的完整流程**,让用户能在隔离的容器环境中快速部署并体验 Index SDK 的向量检索能力。

---

## 【技术要点】

1. **镜像 Tag 命名规范**: `<indexsdk_version>-<chip_series>-<os>-<python_version>`,四段式拼接,例如 `26.1.0-cann9.1.0-310p-ubuntu22.04-py3.12`。
2. **支持的芯片族(chip_series)**: `950`、`910b`、`a3`、`310p` 四种 Atlas NPU。
3. **支持的操作系统(os)**: `ubuntu22.04`、`openeuler24.03` 两种。
4. **支持版本组合**: 索引 SDK 版本 `26.1.0`,CANN 版本 `9.1.0`,Python `py3.12`,共组合出 8 个官方 Tag(4 芯片 × 2 OS)。
5. **Docker 引擎版本要求**: **不低于 24.0.x**;主机必须预装与容器 CANN 版本兼容的 Atlas NPU 驱动。
6. **设备挂载要求**: 需使用 `--device` 把 `/dev/davinci`(加速卡,按需)、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`(管理设备,必须全部挂载)映射进容器;并以 `-v` 只读挂载 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`version.info`、`/etc/ascend_install.info` 等驱动与工具链文件。
7. **算子生成三步流程**: ① 在 `/usr/local/Ascend/mxIndex/ops` 执行 `custom_opp_*.run`;② 在 `../tools` 跑 `aicpu_generate_model.py -t npu-type` 和 `flat_generate_model.py -t npu-type -d 512`;③ 把 `op_models/*` 移到 `$MX_INDEX_MODELPATH`。
8. **Demo 编译链接库清单**: `libfaiss`、`libascendfaiss`、`libopenblas`、`libc_sec`、`libascendcl`、`libascend_hal`、`libascendsearch`、`libc_sec`(含 HMM 锁),头文件来自 mxIndex、faiss、Ascend driver、OpenBLAS 四处。
9. **关键环境变量**: `MX_INDEX_INSTALL_PATH`(默认 `/usr/local/Ascend/mxIndex`)、`ASCEND_HOME_PATH`(默认 `/usr/local/Ascend/cann`)。
10. **本地构建命令**: `docker build -t {your_repo}/index:latest -f Dockerfile .`。

---

## 【关键机制与数据】

### 镜像组合矩阵
- 原文:**CANN 9.1.0 + 26.1.0 Index SDK 共 8 个镜像 tag**,分别覆盖 `910b / 310p / a3 / 950` 四种芯片 × `ubuntu22.04 / openeuler24.03` 两种 OS。
- 原文:每种 chip×OS 组合都对应一个独立的 `Dockerfile.<chip>.<os>` 文件(例如 `Dockerfile.310p.ubuntu`、`Dockerfile.910b.openeuler` 等),镜像内容均为 **toolkit + Index SDK**。

### 容器运行时数据流(原文:运行容器章节)
- **驱动一致性**: 容器镜像内的 CANN 工具链版本,必须与**主机侧已安装的 Atlas NPU 驱动**版本相对应,需查阅 CANN Compatibility Matrix 确认映射关系。
- **设备可见性**: 通过 `--device` 把字符设备文件直接透传到容器,使容器内进程能与 NPU 硬件交互;`/dev/davinci` 按需挂载(例如示例中仅挂 `/dev/davinci1`),而管理类设备全部挂载。
- **驱动只读挂载**: `/usr/local/Ascend/driver/lib64/`、`version.info` 等以 `-v` 只读方式挂载,保证容器内运行环境与宿主机完全一致。

### 算子生成机制(原文:3.3 节)
- **生成产物路径**: `/usr/local/Ascend/mxIndex/ops`(安装包)→ `/usr/local/Ascend/mxIndex/tools`(生成脚本)→ `$MX_INDEX_MODELPATH`(运行时模型目录)。
- **flat_generate_model.py 参数**: `-t npu-type`(指定目标 NPU 类型),`-d 512`(维度参数,原文数值)。

### 编译安全标志(原文:3.4 节 g++ 命令)
- 原文中实际使用的安全加固标志包括: `-fstack-protector-all`、`-D_FORTIFY_SOURCE=2`、`-Wl,-z,relro,-z,now,-z,noexecstack`、`-pie`、`-fPIC`、`-fPIE`、`-O3`,以及 C++11 标准与 `-Wall` 警告。

---

## 【表格解读】

### 表 1: Tag 命名规范字段说明(原文 §2.1)

| Field              | Example Values                | Description           |
| ------------------ | ----------------------------- | --------------------- |
| `indexsdk_version` | `26.1.0`                      | IndexSDK version      |
| `chip_series`      | `950`, `910b`, `a3`, `310p`   | Target chip family    |
| `os`               | `ubuntu22.04`, `openeuler24.03` | Base operating system |
| `python_version`   | `py3.12`                      | Python version        |

**逐行解读**:
- `indexsdk_version`: 镜像内置的 IndexSDK 软件包版本号,示例为 `26.1.0`,对应文末镜像表中所有 Tag 的统一前缀。
- `chip_series`: 目标加速芯片家族代号,涵盖华为昇腾四大主力芯片 — `950`(高端训练/推理)、`910b`(Atlas 800/900 系列训练主力)、`a3`(Atlas 300I 推理卡系列)、`310p`(Atlas 300I Pro 推理卡)。
- `os`: 基础操作系统镜像,`ubuntu22.04` 与 `openeuler24.03` 两个发行版以适配不同政企/云场景。
- `python_version`: Python 解释器主次版本,当前统一为 `py3.12`,保证上层 Faiss/PyTorch 接口一致性。

### 表 2:CANN 9.1.0 + 26.1.0 Index SDK 镜像清单(原文 §2.2)

| Tag                                              | Dockerfile                                                                              | Image Content      |
| ------------------------------------------------ | --------------------------------------------------------------------------------------- | ------------------ |
| `26.1.0-cann9.1.0-910b-ubuntu22.04-py3.12`        | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.910b.ubuntu) | toolkit + Index SDK |
| `26.1.0-cann9.1.0-310p-ubuntu22.04-py3.12`        | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.310p.ubuntu) | toolkit + Index SDK |
| `26.1.0-cann9.1.0-a3-ubuntu22.04-py3.12`          | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.a3.ubuntu)   | toolkit + Index SDK |
| `26.1.0-cann9.1.0-950-ubuntu22.04-py3.12`         | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.950.ubuntu)  | toolkit + Index SDK |
| `26.1.0-cann9.1.0-910b-openeuler24.03-py3.12`     | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.910b.openeuler) | toolkit + Index SDK |
| `26.1.0-cann9.1.0-310p-openeuler24.03-py3.12`     | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.310p.openeuler) | toolkit + Index SDK |
| `26.1.0-cann9.1.0-a3-openeuler24.03-py3.12`       | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.a3.openeuler)  | toolkit + Index SDK |
| `26.1.0-cann9.1.0-950-openeuler24.03-py3.12`      | [Dockerfile](https://gitcode.com/Ascend/IndexSDK/tree/master/docker/Dockerfile.950.openeuler) | toolkit + Index SDK |

**逐行解读**:
- 第 1 行:`910b` 芯片 + Ubuntu 22.04 基础镜像,镜像内同时打包 CANN toolkit 与 Index SDK,通过 `Dockerfile.910b.ubuntu` 构建。
- 第 2 行:`310p` 芯片 + Ubuntu 22.04 基础镜像,使用 `Dockerfile.310p.ubuntu` 构建,内容同上。
- 第 3 行:`a3` 芯片 + Ubuntu 22.04 基础镜像,使用 `Dockerfile.a3.ubuntu` 构建,内容同上。
- 第 4 行:`950` 芯片 + Ubuntu 22.04 基础镜像,使用 `Dockerfile.950.ubuntu` 构建,内容同上。
- 第 5 行:`910b` 芯片 + openEuler 24.03 基础镜像(国产生态),使用 `Dockerfile.910b.openeuler` 构建。
- 第 6 行:`310p` 芯片 + openEuler 24.03,使用 `Dockerfile.310p.openeuler` 构建。
- 第 7 行:`a3` 芯片 + openEuler 24.03,使用 `Dockerfile.a3.openeuler` 构建。
- 第 8 行:`950` 芯片 + openEuler 24.03,使用 `Dockerfile.950.openeuler` 构建。
- **共性**:所有 Tag 的 Image Content 均为 **toolkit + Index SDK**,即已预装 CANN toolkit(驱动运行时依赖)与 Index SDK 主软件,用户拉取后可直接进入 mxIndex 工作流而无需额外安装。

---

## 【公式解读】

原文无公式。(文档性质为 Docker 镜像使用说明,未出现数学公式或伪代码公式。)

---

## 【关联】

- **与算子生成子模块的关联**: §3.3 "Generate Operators" 引用 [Operator Generation](https://gitcode.com/Ascend/IndexSDK/blob/master/docs/zh/05_user_guide.md#%E8%87%AA%E5%AE%9A%E4%B9%89%E7%AE%97%E5%AD%90%E4%BB%8B%E7%BB%8D) 详细文档,说明本 README 只是一键命令摘要,深入的自定义算子(`custom_opp_*.run`、`aicpu_generate_model.py`、`flat_generate_model.py`)用法在 `05_user_guide.md` 中展开。
- **与 Demo 示例的关联**: §3.4 "Compile Demo" 链向 [Demo Example](https://gitcode.com/Ascend/IndexSDK/blob/master/docs/zh/05_user_guide.md#%E4%BD%BF%E7%94%A8%E6%A0%B7%E4%BE%8B),表示本 README 给出的编译命令只是入口演示,完整 demo 代码与运行说明在用户指南同节。
- **与 CANN 兼容性矩阵的关联**: §3.1.1 提示宿主机的 Atlas NPU 驱动  容器内 CANN 版本必须匹配,需查 [CANN Compatibility Matrix](https://www.hiascend.com/document),这是选择正确 Tag 的前置条件。
- **与许可协议的关联**: §4 指向 [CANN/MindSeries LICENSE](https://github.com/Ascend/cann-container-image/blob/main/LICENSE),提示镜像内预装包(Python、系统库等)有各自许可。
- **与上层支持资源的关联**: §1 Quick Reference 列出 Issue、代码库、API 参考、全量文档、镜像仓库、社区论坛 6 类帮助入口,构成本 README 的"求助链路"。
- **与 API 参考的关联**: 链接到 [IndexSDK API Reference](https://gitcode.com/Ascend/IndexSDK/blob/master/docs/zh/api/README.md),说明 Docker 镜像中已经包含了完整的 SDK API,可直接被应用代码 import。
- **与昇腾镜像仓库的关联**: 镜像实际拉取地址示例为 `swr.cn-south-1.myhuaweicloud.com/ascendhub/indexsdk:<tag>`,而用户也可通过 [Image Repository](https://www.hiascend.com/developer/ascendhub/detail/indexsdk/) 浏览所有变体。

---

## 【使用方法】

### 1. 启用方式:运行 Index 容器(原文 §3.2)

**前置条件**:
- 主机已装与容器 CANN 版本匹配的 Atlas NPU 驱动。
- Docker ≥ 24.0.x。

**完整启动命令**:
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
- 启动后通过 `bash` 进入容器交互式 Shell。
- `-it` 后的 tag 需替换为实际版本,例如 `swr.cn-south-1.myhuaweicloud.com/ascendhub/indexsdk:26.1.0-cann9.1.0-310p-ubuntu22.04-py3.12`(原文示例)。

### 2. 配置项(关键环境变量,原文 §3.4)

| 变量名 | 默认值 | 作用 |
| --- | --- | --- |
| `MX_INDEX_INSTALL_PATH` | `/usr/local/Ascend/mxIndex` | Index SDK 安装路径,g++ 编译时通过 `-I/-L` 引用其头文件与 host 库 |
| `ASCEND_HOME_PATH`     | `/usr/local/Ascend/cann`   | Toolkit 安装路径,g++ 链接阶段追加 `-L$ASCEND_HOME_PATH/lib64` |

### 3. 算子生成(原文 §3.3)
```bash
cd /usr/local/Ascend/mxIndex/ops
./custom_opp_*.run
cd ../tools
python3 aicpu_generate_model.py -t npu-type
python3 flat_generate_model.py -t npu-type -d 512
mv op_models/* $MX_INDEX_MODELPATH
```
- `npu-type` 需替换为 `310p / 910b / a3 / 950` 之一;`-d 512` 为维度参数(原文值)。
- `$MX_INDEX_MODELPATH` 必须指向运行时模型目录。

### 4. Demo 编译(原文 §3.4)
```bash
export MX_INDEX_INSTALL_PATH=/usr/local/Ascend/mxIndex

g++ --std=c++11 -fPIC -fPIE -fstack-protector-all -Wall \
    -D_FORTIFY_SOURCE=2 -O3 \
    -Wl,-z,relro,-z,now,-z,noexecstack -s -pie \
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
    -lfaiss -lascendfaiss -lopenblas -lc_sec -lascendcl -lascend_hal -lascendsearch -lc_sec
```
- 链接顺序固定为:Faiss → AscendFaiss → OpenBLAS → c_sec → AscendCL → Ascend HAL → AscendSearch → c_sec(HMM 锁)。

### 5. 运行 Demo(原文 §3.5)
```bash
./demo
```

### 6. 本地构建镜像(原文 §3.6)
```bash
docker build -t {your_repo}/index:latest -f Dockerfile .
```
- 用户可基于仓库根目录的 `Dockerfile` 自行定制并推送到 `{your_repo}` 命名的私有仓库。
