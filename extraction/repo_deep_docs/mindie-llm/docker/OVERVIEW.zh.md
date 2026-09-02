# MindIE Docker

> 仓 `mindie-llm` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docker/OVERVIEW.zh.md

# MindIE Docker 文档一体化深度解读

---

## 【定位】

本文档是 MindIE 推理加速套件的 **Docker 镜像构建总览**，阐述如何通过自动化脚本与多阶段 Dockerfile，从源码/二进制包构建出可运行的 MindIE 推理服务镜像，覆盖 Ubuntu 与 openEuler 两种 OS、昇腾 310/910/A3 三类芯片、x86_64/aarch64 两种架构的组合矩阵，并提供 Tag 规范、构建参数、并行下载、多阶段构建图等完整构建指引。

---

## 【技术要点】

1. **Tag 五段式命名规范**：`mindie:<MindIE版本>-<产品系列>-<python版本>-<操作系统>-<架构类型>`，例如 `mindie:3.0.0-800I-A2-py3.11-ubuntu24.04-x86_64`，由 MindIE 版本号统一驱动 LLM / SD / Motor 三个组件。

2. **Chip 到产品系列的三组映射**：`310 → 300I-Duo`（Atlas 300I Duo）、`910 → 800I-A2`（Atlas 800I A2）、`A3 → 800I-A3`（Atlas 800I A3）。

3. **9 个构建参数 + 6 个必填项**：必填项为 `--os`、`--chip`、`--arch`、`--mindie`、`--cann`、`--pta-tag`；可选 `--type`（默认 `whl`，可选 `run`）、`--python`（默认 `3.11.10`）、`--dry-run`（默认 `false`）。

4. **8 路并行下载机制**：`download.sh` 并行拉取 PTA、Python 源码（仅 Ubuntu）、CANN Toolkit/CANN NNAL/CANN Kernels、MindIE-LLM、MindIE-SD、MindIE-Motor 多个组件包。

5. **Dockerfile 多阶段构建（7 阶段 + 2 基础分支）**：Stage 1a (base-ubuntu)、Stage 1b (base-openeuler)、Stage 2 (base)、Stage 3 (cann)、Stage 4 (pta)、Stage 4.5 (mindstudio)、Stage 5 (mindie)。

6. **基镜像加速与多源分发**：基镜像支持通过 `swr.cn-north-4.myhuaweicloud.com/inference` 镜像仓库加速；下载源覆盖 gitcode（MindIE 全系 + PTA）、昇腾 OBS（CANN）、华为云 PyPI（Python 源码）。

7. **运行环境关键变量**：`ASCEND_TOOLKIT_HOME`、`MINDIE_LLM_HOME_PATH`、`MIES_INSTALL_PATH`、`ATB_SPEED_HOME_PATH`、`MINDIE_LLM_CONTINUOUS_BATCHING`（默认 1）、`ASCEND_GLOBAL_LOG_LEVEL`（默认 3）。

---

## 【关键机制与数据】

**构建流程四步链**（原文）：

1. **参数解析与校验**：`build.sh` 解析命令行参数，调用 `config.sh` 校验 OS/Chip/Arch/Type 合法性。
2. **并行下载（8 路）**：`download.sh` 并行下载 PTA / Python / CANN Toolkit / CANN NNAL / CANN Kernels / MindIE-LLM / MindIE-SD / MindIE-Motor。
3. **Docker 多阶段构建**：`build_image.sh` 调用 Dockerfile 执行 7 阶段构建（base-ubuntu 或 base-openeuler → base → cann → pta → mindstudio → mindie）。
4. **镜像导出**：构建产物保存为 `output/` 目录下的 `.tar.gz` 文件。

**多阶段构建拓扑**（原文）：
```text
base-ubuntu ──┐
              ├──> base ──> cann ──> pta ──> mindstudio ──> mindie
base-openeuler┘
```

**前置资源约束**（原文）：
- Docker 版本 ≥ 24.x.x
- 构建目录磁盘空间 **约 50GB+**（下载包 + 构建缓存）

**Python 处理差异**（原文）：Ubuntu 分支需从源码编译 Python；openEuler 分支预装 Python，跳过源码下载。

**包类型差异**（原文）：`MindIE-LLM` 同时支持 `whl` 与 `run` 两种包；`MindIE-SD`、`MindIE-Motor` 仅支持 `whl`。

---

## 【表格解读】

### 表 1：文件说明（原文）

| 文件 | 说明 |
|------|------|
| [build.sh](./build.sh) | 主入口脚本，负责参数解析、校验、下载编排与构建调用 |
| [Dockerfile](./Dockerfile) | 多阶段 Docker 构建文件（7 个阶段） |
| [modules/config.sh](./modules/config.sh) | 集中配置：URL 模板、日志、校验、架构检测、Chip/OS 元数据 |
| [modules/download.sh](./modules/download.sh) | 下载层：8 路并行下载 PTA / Python / CANN / MindIE-LLM / MindIE-SD / MindIE-Motor 包 |
| [modules/build_image.sh](./modules/build_image.sh) | 构建编排层：镜像 Tag 计算、Docker 构建、镜像导出 |

**解读**：Docker 子目录采用经典的分层架构——`build.sh` 是面向用户的入口，`config.sh` 集中存放元数据与校验逻辑（便于版本切换时单点修改），`download.sh` 与 `build_image.sh` 分别承担"获取依赖"和"组装镜像"两个职责。模块化拆分让 URL 模板、日志、Chip/OS 元数据等共享配置集中管理。

---

### 表 2：Tag 字段说明（原文）

| 字段 | 示例值 | 说明 |
|------|--------|------|
| `MindIE版本` | `3.0.0` | MindIE 版本号（驱动 LLM / SD / Motor） |
| `产品系列` | `800I-A2`、`800I-A3`、`300I-Duo` | 目标昇腾产品系列 |
| `python版本` | `py3.11` | Python 版本 |
| `操作系统` | `ubuntu24.04`、`openeuler` | 基础操作系统 |
| `架构类型` | `x86_64`、`aarch64` | CPU 架构类型 |

**解读**：Tag 把 5 个变量压缩为一个字符串，足以唯一标识一份镜像的运行目标。Python 字段使用简化写法 `py3.11`，而 OS 字段则使用完整版本号 `ubuntu24.04`——这种"语义不同 → 精度不同"的设计让 Tag 既可读又可精确锁定环境。MindIE 版本号同时驱动 LLM/SD/Motor 三个组件，意味着三者必须版本对齐发布。

---

### 表 3：产品系列映射（原文）

| Chip 参数 | 产品系列 | 说明 |
|-----------|----------|------|
| `310` | `300I-Duo` | Atlas 300I Duo |
| `910` | `800I-A2` | Atlas 800I A2 |
| `A3` | `800I-A3` | Atlas 800I A3 |

**解读**：这是 `--chip` 参数到 Tag 第二段产品系列字段的映射表。注意命名不一致：`A3` 是字母而非纯数字——这是因为 A3 是较新的昇腾芯片代号，与传统 310/910 数字序列并列。三个系列均可在 ARM64 上运行，Atlas 300I Duo 额外支持 x86_64（异构）。

---

### 表 4：构建参数（原文）

| 参数 | 说明 | 是否必填 | 默认值 | 示例值 |
|------|------|----------|--------|--------|
| `--os` | 服务器操作系统 | 是 | — | ubuntu / openeuler |
| `--chip` | 昇腾设备型号 | 是 | — | 310 / 910 / A3 |
| `--arch` | 系统架构 | 是 | — | x86_64 / aarch64 |
| `--mindie` | MindIE 版本号（驱动 LLM / SD / Motor） | 是 | — | 3.0.0 |
| `--cann` | CANN 版本号 | 是 | — | 9.0.0 |
| `--pta-tag` | PTA 发布 Tag | 是 | — | v26.0.0-pytorch2.9.0 |
| `--type` | 包类型 | 否 | `whl` | whl / run |
| `--python` | Python 版本 | 否 | `3.11.10` | 3.11.6 |
| `--dry-run` | 仅校验参数并展示配置 | 否 | `false` | — |

**解读**：9 个参数中 6 个为必填，构成"镜像身份"——OS、芯片、架构决定镜像运行平台，MindIE/CANN/PTA 三个版本号决定软件栈。`--type` 区分 wheel 包和 run 自解压包，影响 MindIE-LLM 的安装路径；`--python` 仅对 Ubuntu 分支有意义（openEuler 走预装路径）；`--dry-run` 提供试运行能力，方便在生产前确认参数无误。

---

### 表 5：下载源（原文）

| 组件 | 下载源 |
|------|--------|
| MindIE-LLM | `https://gitcode.com/Ascend/MindIE-LLM/releases/download` |
| MindIE-SD | `https://gitcode.com/Ascend/MindIE-SD/releases/download` |
| MindIE-Motor | `https://gitcode.com/Ascend/MindIE-Motor/releases/download` |
| PTA (torch_npu) | `https://gitcode.com/Ascend/pytorch/releases/download` |
| CANN | `https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/CANN` |
| Python 源码 | `https://mirrors.huaweicloud.com/python` |

**解读**：下载源呈现"开源组件走 gitcode、昇腾官方走 OBS、Python 走华为云镜像"的三段式策略。gitcode 是 MindIE 三组件（LLM/SD/Motor）和 PTA 的统一发布通道（与文首"问题反馈"中的 gitcode URL 形成回路），CANN 从昇腾 OBS 直拉，Python 从华为云 PyPI 镜像拉取——这种分工既保证了版本与官方同步，又规避了外网访问不稳定。

---

### 表 6：支持的硬件（原文）

| 芯片系列 | 产品示例 | 架构 |
|----------|----------|------|
| 昇腾 910 | Atlas 800I A2 | ARM64 |
| 昇腾 A3 | Atlas 800I A3 | ARM64 |
| 昇腾 310 | Atlas 300I Duo | ARM64 / x86_64 |

**解读**：910 与 A3 是面向数据中心的高算力推理芯片（ARM64 单架构），310 则覆盖推理边缘/入门级场景同时支持 ARM64 与 x86_64 双架构。架构覆盖度与表 3 中的 `--arch` 参数（`x86_64 / aarch64`）一一对应。

---

### 表 7：容器内环境变量（原文）

| 变量 | 说明 |
|------|------|
| `ASCEND_TOOLKIT_HOME` | CANN 工具链安装路径 |
| `MINDIE_LLM_HOME_PATH` | MindIE-LLM 服务安装路径 |
| `MIES_INSTALL_PATH` | MindIE-Motor（mindie-service）安装路径 |
| `ATB_SPEED_HOME_PATH` | ATB-LLM 加速库路径 |
| `MINDIE_LLM_CONTINUOUS_BATCHING` | 连续批处理开关（默认 1） |
| `ASCEND_GLOBAL_LOG_LEVEL` | 全局日志级别（默认 3） |

**解读**：环境变量分为三类——前三项定位安装路径（CANN、MindIE-LLM、MindIE-Motor、ATB 加速库），后两项控制运行时行为（`MINDIE_LLM_CONTINUOUS_BATCHING=1` 默认开启连续批处理，`ASCEND_GLOBAL_LOG_LEVEL=3` 对应昇腾日志等级体系中的 ERROR 级或 WARNING 级，按 CANN 文档约定）。`ATB_SPEED_HOME_PATH` 体现了 MindIE 底层依赖 ATB（Ascend Transformer Boost）加速库这一关键架构选型。

---

## 【公式解读】

**原文无数学公式**，但有两处类公式化的模式定义：

### 模式 1：Tag 格式模式

```text
mindie:<MindIE版本>-<产品系列>-<python版本>-<操作系统>-<架构类型>
```

- `<MindIE版本>`：形如 `3.0.0` 的 SemVer 版本号，同时决定 LLM/SD/Motor 三组件版本
- `<产品系列>`：`800I-A2`、`800I-A3`、`300I-Duo` 三选一，由 `--chip` 决定
- `<python版本>`：简写 `py3.11`
- `<操作系统>`：`ubuntu24.04` 或 `openeuler`
- `<架构类型>`：`x86_64` 或 `aarch64`
- **作用**：唯一标识一个可发布的 MindIE 镜像，五段中任意一段变化都会生成一个新镜像。

### 模式 2：多阶段构建流图

```text
base-ubuntu ──┐
              ├──> base ──> cann ──> pta ──> mindstudio ──> mindie
base-openeuler┘
```

- `base-ubuntu` / `base-openeuler`：两个并列的基础阶段，分别对应 Ubuntu 24.04 + 源码编译 Python 与 OpenEuler 24.03 + 预装 Python 两种基线
- `base`：动态 OS 选择阶段（继承自上一步两选一），负责导入所有下载包
- `cann`：安装 CANN Toolkit + Kernels + NNAL
- `pta`：安装 PyTorch + torch_npu
- `mindstudio`：安装开发工具（git/cmake/gcc/ffmpeg 等）
- `mindie`：安装 MindIE 组件（LLM/SD/Motor），作为最终阶段输出
- **作用**：以 DAG（有向无环图）形式表达 Stage 之间的依赖关系，OS 分支在最早期分流，后续所有阶段共享同一条主干。

---

## 【关联】

### 仓库内部文件依赖链

- **[`./OVERVIEW.md`](./OVERVIEW.md)**：英文版总览，与本文互为镜像。
- **[`./build.sh`](./build.sh)**：主入口，所有 CLI 参数的承接者；同时调用 `config.sh`、`download.sh`、`build_image.sh` 三个模块。
- **[`./Dockerfile`](./Dockerfile)**：被 `build_image.sh` 调用，承载 7 阶段构建流程；其 Stage 4.5 (mindstudio) 与 Stage 5 (mindie) 的环境变量直接对应表 7。
- **[`./modules/config.sh`](./modules/config.sh)**：被 `build.sh` 调用，承担参数校验与元数据维护；其 Chip/OS 元数据决定了表 3 的映射。
- **[`./modules/download.sh`](./modules/download.sh)**：被 `build.sh` 调用，8 路并行实现表 5 的所有下载源拉取。
- **[`./modules/build_image.sh`](./modules/build_image.sh)**：被 `build.sh` 调用，依赖 Dockerfile 完成镜像组装与导出。

### 仓库外部组件关联

- **MindIE-LLM / MindIE-SD / MindIE-Motor** 三仓库镜像发布链路与本文的 Tag 规范一一对应，是 docker 构建产物的最终使用者。
- **昇腾社区 / MindIE 镜像仓库**：分别提供 CANN 版本查询、预构建镜像（如果不想自行构建可直接拉取 swr.cn-north-4 仓库）。
- **PTA（torch_npu）**：PyTorch 在昇腾 NPU 上的后端，`--pta-tag` 形如 `v26.0.0-pytorch2.9.0` 同时携带 CANN 与 PyTorch 两个版本信息，是 PTA 与 PyTorch 版本耦合的体现。
- **[`../LICENSE.md`](../LICENSE.md)**：项目根目录许可证文件，决定本文构建产物的合规边界。

---

## 【使用方法】

### 三种典型构建命令（原文）

```bash
# 模式 1：完整参数（whl 包，默认 Python 3.11.10）
bash build.sh \
    --os=ubuntu \
    --chip=910 \
    --arch=x86_64 \
    --mindie=3.0.0 \
    --cann=9.0.0 \
    --pta-tag=v26.0.0-pytorch2.9.0

# 模式 2：run 包 + 自定义 Python（openEuler + aarch64 + 310）
bash build.sh \
    --os=openeuler \
    --chip=310 \
    --arch=aarch64 \
    --mindie=3.0.0 \
    --cann=9.0.0 \
    --pta-tag=v26.0.0-pytorch2.9.0 \
    --type=run \
    --python=3.11.6

# 模式 3：仅校验，不执行
bash build.sh \
    --os=ubuntu \
    --chip=910 \
    --arch=x86_64 \
    --mindie=3.0.0 \
    --cann=9.0.0 \
    --pta-tag=v26.0.0-pytorch2.9.0 \
    --dry-run
```

### 启用要点（原文）

1. **执行位置**：必须在 `docker/` 目录下执行 `build.sh`，因为脚本的相对路径假设当前目录即为仓库的 `docker/` 子目录。
2. **参数获取渠道**：
   - `cann` 版本号 → 昇腾社区下载页
   - `pta-tag` → Pytorch-NPU 社区 Releases
   - `mindie` 版本号 → MindIE-LLM / MindIE-SD / MindIE-Motor 各自的 Releases 页面
3. **镜像拉取加速**：基镜像可改走 `swr.cn-north-4.myhuaweicloud.com/inference` 镜像仓库。
4. **环境变量生效**：上述表 7 全部变量在 Stage 5 (mindie) 完成后即写入容器，运行时无需手动 export。
5. **构建产物**：最终镜像以 `.tar.gz` 形式存放在 `output/` 目录，可通过 `docker load` 导入。
