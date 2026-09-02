# MindSpeed-Ops Docker 镜像构建指南

> 仓 `mindspeed-ops` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-ops/docker/OVERVIEW.md

# MindSpeed-Ops Docker 镜像构建指南 — 深度解读

---

## 【定位】

这篇文档是 `docker/` 目录的总览说明,解决"如何在昇腾 NPU 环境中,通过 Docker 一键构建并部署 MindSpeed-Ops 算子库镜像"的问题,描述了从三阶段镜像构建、构建脚本参数、ACLNN 算子可选编译、到容器运行与验证的完整能力。

---

## 【技术要点】

1. **三阶段 Docker 构建架构** — Dockerfile 采用 multi-stage:Stage1(base) 配置 CANN 基础镜像 + 系统编译工具链;Stage2(builder) 安装 Python 3.12 + PyTorch/torch-npu/triton-ascend;Stage3(final) 克隆仓库并以 editable 模式安装。

2. **软件版本锁定** — CANN `9.1.0`、PyTorch `2.10.0`、torch-npu `2.10.0`、triton-ascend `3.2.2`、Python `3.12`,通过 `--base-image-version` / `--torch-version` / `--torch-npu-version` / `--triton-ascend-version` / `--python-version` 五个 CLI 参数可覆盖。

3. **三类算子后端 + ACLNN 可选编译** — 算子分 Triton(基于 triton-ascend,主要后端)、TileLang(基于 TileLang)、ACLNN(基于 CANN AscendC 原生算子) 三种后端;只有 ACLNN 需要 `--soc-version` 参数触发 C++ 扩展(pybind11)和 ACLNN 算子包编译。

4. **NPU/OS/Arch 三维矩阵** — 支持 NPU: `A3`、`910B`;OS: `openEuler24.03`、`ubuntu22.04`;CPU 架构: `x86_64`、`aarch64 (ARM)`。`A3` 与 `910B` 通过 `-t/--npu-type` 区分。

5. **镜像 Tag 自动命名规则** — 格式 `{分支}-{NPU类型}-{OS}-py{Python版本}-{架构}`,如 `mindspeed-ops:master-910b-openeuler24.03-py3.12-x86_64`,NPU 类型大小写不敏感(脚本接收 `910B`,Tag 中转小写为 `910b`)。

6. **容器运行时必须挂载 NPU 驱动路径** — `/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`(若宿主机在 `/usr/local/sbin/npu-smi` 则需替换)、`/etc/ascend_install.info`,加 `--privileged --network host --ipc=host` 才能正常使用 NPU。

---

## 【关键机制与数据】

**工作机制 (按构建/运行顺序)**

- **构建入口**:`docker/image_build.sh` 解析 CLI 参数后调用 `docker build`;`Dockerfile` 三阶段串联。
- **ACLNN 编译开关**:`--soc-version` 不传 → 跳过 C++ 扩展和 ACLNN 编译,仅装 Triton/Python 算子;传 `ascend910b1` 等具体值 → 编译 pybind11 扩展和 ACLNN 包,需容器内可访问 NPU 驱动。
- **软件源切换**:`configure_apt_repo.sh`(Ubuntu)与 `configure_yum_repo.sh`(openEuler)将源切换为华为云镜像,以适配内网/国内构建环境。
- **Editable 安装**:Stage3 克隆仓库后用 `pip install -e .`,源码落地 `/workspace/MindSpeed-Ops`,改代码无需重建镜像即可生效。
- **驱动挂载契约**:容器 `/usr/local/Ascend/driver`、`/usr/local/dcmi` 等来自宿主机,保证 ACLNN 算子在运行期调用底层 NPU 设备。

**性能/数值类数据** — 原文未提供任何构建耗时、镜像大小、运行基准(benchmark)数据,故不杜撰。

---

## 【表格解读】

### 表 1 · 软件版本配套

| 组件 | 版本 |
|------|------|
| CANN | 9.1.0 |
| PyTorch | 2.10.0 |
| torch-npu | 2.10.0 |
| triton-ascend | 3.2.2 |
| Python | 3.12 |

> 逐行解读:CANN 9.1.0 是 ACLNN 编译和 AscendC 运行时的根基,文档中所有 `--base-image-version` 默认指向此值;PyTorch 与 torch-npu 同为 2.10.0,说明二者版本需严格对齐才能保证 ABI 兼容;triton-ascend 3.2.2 是 Triton 后端算子的编译器,版本与 torch-npu 同步关系由官方维护;Python 3.12 决定了 `pybind11` 编译产物对 ABI 的依赖。

### 表 2 · 支持的配置

| 配置项 | 支持的值 |
|--------|----------|
| NPU 类型 | A3、910B |
| 操作系统 | openEuler 24.03、Ubuntu 22.04 |
| CPU 架构 | x86_64、aarch64 (ARM) |

> 逐行解读:NPU 类型经 `-t` 传入,影响 Stage1 的基础镜像选择;A3 与 910B 在 CANN 软件栈层面存在差异;OS 通过 `-o` 切换并对应不同的 `configure_*_repo.sh`;x86_64 与 aarch64 都得到支持,意味着同一脚本可覆盖 ARM 服务器场景。

### 表 3 · 构建脚本必选参数

| 参数 | 说明 |
|------|------|
| `-t, --npu-type TYPE` | NPU 类型:`A3` 或 `910B` |

> 逐行解读:`-t` 是脚本唯一必传项,因为 Stage1 必须据此选择不同的 CANN 基础镜像。

### 表 4 · 构建脚本可选参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-i, --image-name NAME` | 自动生成 | 自定义输出镜像名称 |
| `-o, --os OS` | `openEuler24.03` | 操作系统类型:`openEuler24.03` 或 `ubuntu22.04` |
| `-n, --no-cache` | - | 不使用 Docker 构建缓存 |
| `--base-image IMAGE` | - | 完整的基础镜像地址,直接传递给 FROM 指令 |
| `--base-image-version VER` | `9.1.0` | CANN 基础镜像版本 |
| `--python-version VER` | `3.12` | Python 版本 |
| `--torch-version VER` | `2.10.0` | PyTorch 版本 |
| `--torch-npu-version VER` | `2.10.0` | torch-npu 版本 |
| `--triton-ascend-version VER` | `3.2.2` | triton-ascend 版本 |
| `--mindspeed-ops-branch BRANCH` | `master` | MindSpeed-Ops Git 分支/版本 |
| `--soc-version VERSION` | - | 目标芯片型号,用于编译 ACLNN 算子(见下方说明) |
| `--cleanup-on-fail` | - | 构建失败时自动清理悬空镜像 |
| `-h, --help` | - | 显示帮助信息 |

> 逐行解读:`-i` 覆盖默认 Tag 命名,通常用于推送到私有 registry(如示例 `myregistry.com/mindspeed-ops:latest`);`-o` 改变 OS 矩阵;`-n` 强制全量重建;`--base-image` 与 `--base-image-version` 二选一,前者用于完全自定义 FROM(常见于内网 Harbor);后 4 个版本号主要用于 CANN/Triton 新版本适配;`--mindspeed-ops-branch` 既可填分支名(如 `master`)也可填版本 tag(如 `v0.1.0`);`--soc-version` 是触发 ACLNN 编译的关键开关,值见下方 SOC_VERSION 表;`--cleanup-on-fail` 用于减少磁盘残留;`-h` 给出内联帮助。

### 表 5 · ACLNN 算子后端分类

| 后端 | 说明 | 是否需要 SOC_VERSION |
|------|------|----------------------|
| Triton | 基于 triton-ascend 的算子(主要后端) | 不需要 |
| TileLang | 基于 TileLang 的算子 | 不需要 |
| ACLNN | 基于 CANN AscendC 的原生算子 | **需要** |

> 逐行解读:Triton 是默认/主要后端,不指定 SOC_VERSION 时也能用,满足大多数 Python 端使用场景;TileLang 同样无需 SOC_VERSION,但具体启用方式本文未展开;只有 ACLNN 后端需要 `--soc-version`,因 AscendC 算子需要按目标芯片架构编译本地代码。

### 表 6 · SOC_VERSION 取值示例

| 芯片 | SOC_VERSION | 架构 |
|------|------------|------|
| Ascend 910B | `ascend910b1` | arch32 |
| Ascend 910_93 | `ascend910_9391` | arch32 |
| Ascend 950* | `ascend950*` | arch35 |

> 逐行解读:`ascend910b1` 对应文档示例中 910B 芯片,架构 arch32;`ascend910_9391` 对应 A3(910_93 系列),同样 arch32;Ascend 950 系列使用更新的 arch35 架构(原文用通配符 `ascend950*` 表示多个具体子型号),说明 arch35 与 arch32 是不同的指令集,编译产物不可互换。

---

## 【公式解读】

原文无公式。

> 说明:本文档为运维/构建指南,不涉及任何数学公式或伪代码算法,故无公式可解读。

---

## 【关联】

文档涉及的关键上下游关系如下(基于原文叙述):

- **Stage1 基础镜像** ↔ `--base-image` / `--base-image-version` 参数:用户可完全覆盖 CANN 官方基础镜像,使内网 Harbor 镜像源也能纳入构建流程。
- **`configure_apt_repo.sh` / `configure_yum_repo.sh`** ↔ `-o` OS 参数:Ubuntu 走 apt 源切换,openEuler 走 yum 源切换,二者保证在线安装 PyTorch/torch-npu/triton-ascend 的网络可达性。
- **三类算子后端 (Triton / TileLang / ACLNN)** ↔ MindSpeed-Ops 仓库代码本体:ACLNN 路径强依赖 `--soc-version`,与 CANN AscendC 编译器及 NPU 驱动耦合;其他两条路径只依赖 Python 与 triton-ascend wheel。
- **NPU 驱动挂载** ↔ 容器运行:无论构建期是否编译 ACLNN,运行时都需 `-v /usr/local/Ascend/driver:...` 等挂载,否则 ACLNN 算子无法调用底层设备。
- **Editable 安装** ↔ 仓库代码改动:代码位于容器 `/workspace/MindSpeed-Ops`,开发者可直接 mount 宿主机源码实现热更新,无需重建镜像。

(原文未提供内部链接列表,故未额外展开。)

---

## 【使用方法】

> 原文给出了非常完整的命令范式,以下按"构建 → 运行 → 验证"三阶段逐一列出。

### 1. 构建镜像(快速开始)

```bash
cd docker/
bash image_build.sh -t 910B
```

构建完成后自动生成镜像:`mindspeed-ops:master-910b-openeuler24.03-py3.12-x86_64`。

### 2. 场景化构建示例(原文提供)

| 场景 | 命令 |
|------|------|
| 基本构建(910B + openEuler) | `bash image_build.sh -t 910B` |
| A3 + Ubuntu | `bash image_build.sh -t A3 -o ubuntu22.04` |
| 启用 ACLNN 编译(910B) | `bash image_build.sh -t 910B --soc-version ascend910b1` |
| 使用自定义基础镜像 | `bash image_build.sh -t A3 --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-a3-openeuler24.03-py3.12` |
| 指定 MindSpeed-Ops 分支版本 | `bash image_build.sh -t 910B --mindspeed-ops-branch v0.1.0` |
| 自定义镜像名称 | `bash image_build.sh -t 910B -i myregistry.com/mindspeed-ops:latest` |
| 不使用缓存 + 失败清理 | `bash image_build.sh -t 910B --no-cache --cleanup-on-fail` |

### 3. 运行容器

```bash
docker run -itd \
  --name mindspeed-ops \
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
  mindspeed-ops:master-910b-openeuler24.03-py3.12-x86_64 bash
```

进入容器:

```bash
docker exec -it mindspeed /bin/bash
```

> 原文特别提示:若宿主机 `npu-smi` 位于 `/usr/local/sbin/npu-smi`,挂载路径需对应替换。

### 4. 验证安装

```bash
python -c "import mindspeed_ops; print('MindSpeed-Ops loaded successfully')"
python -c "from mindspeed_ops.api.triton import add; print('Triton operators available')"
python -c "import torch_npu; print(f'torch_npu version: {torch_npu.__version__}')"
```

容器内 `import mindspeed_ops` 即可直接使用,因为已以 editable 模式安装在 `/workspace/MindSpeed-Ops`。

### 5. 无 NPU 机器上尝试 ACLNN 编译(原文 FAQ 提供的备选方案)

```bash
docker build --build-arg SOC_VERSION=ascend910b1 \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/Ascend/ascend-toolkit:/usr/local/Ascend/ascend-toolkit \
  --network=host -t mindspeed-ops:aclnn-910b .
```

> 此为绕过"构建环境无 NPU 设备"限制的折中方案,通过挂载驱动目录让容器内可见 CANN Toolkit 与驱动头文件。
