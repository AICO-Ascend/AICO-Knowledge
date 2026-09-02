# atlas-a3.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/ascend_image/atlas-a3.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-a3.inc.md

# vllm-ascend · Atlas A3 快速启动指南 · 深度解读

---

## 【定位】

这篇文档描述了 **在 Atlas A3 硬件平台上获取并启动 vllm-ascend Docker 容器** 的完整步骤,涵盖镜像拉取与容器启动两类操作,并提供 Ubuntu 与 openEuler 两种操作系统变体的并行配置。

---

## 【技术要点】

1. **镜像仓库与标签**: 镜像来源于 `quay.io/ascend/vllm-ascend`,标签分别为 `{{ vllm_ascend_version }}-a3`(Ubuntu)与 `{{ vllm_ascend_version }}-a3-openeuler`(openEuler),其中 `{{ vllm_ascend_version }}` 为文档模板变量,实际渲染时会被替换为具体版本号。

2. **双 DIE 硬件约束 (核心)**:
   - A3 采用 **dual-DIE design** (双 DIE 设计)
   - 必须挂载 **两个 Ascend 设备节点**,例如 `/dev/davinci0` 与 `/dev/davinci1`
   - 此为容器启动的前置硬性要求 (warning 框标注)

3. **共享内存配置**: `--shm-size=1g`,为 PyTorch 等框架的多进程数据加载预留 1 GB 的 /dev/shm。

4. **设备透传列表** (共 3 个特殊设备 + 2 个 NPU 设备):
   - `/dev/davinci0`、`/dev/davinci1` — 计算设备
   - `/dev/davinci_manager` — 设备管理器
   - `/dev/devmm_svm` — 内存管理(SVM)
   - `/dev/hisi_hdc` — HDC 通信通道

5. **驱动/运行时卷挂载** (共 4 个关键路径):
   - `/usr/local/dcmi` — DCMI(设备控制与监控接口)
   - `/usr/local/bin/npu-smi` — NPU 系统管理工具
   - `/usr/local/Ascend/driver/lib64/` — Ascend 驱动库
   - `/usr/local/Ascend/driver/version.info` — 驱动版本标识
   - `/etc/ascend_install.info` — 安装信息

6. **模型缓存与端口**: `$MODEL_CACHE`(默认为 `${HOME}/.cache`)挂载到容器内 `/root/.cache`;宿主端口 `8000` 映射至容器 `8000`(vLLM 默认 HTTP 服务端口)。

---

## 【关键机制与数据】

**数据流 / 工作原理 (基于原文可推断的部分)**:

- **镜像分发机制**: 文档引用了 `image_download_mirror.inc.md` 这一被 `{% include %}` 指令嵌入的片段 (原文用了 `{% filter indent(4, true) %}` 进行 4 空格缩进过滤),说明该仓库的镜像下载方式是通过单独子文档集中维护、再被多处复用。镜像本身位于 `quay.io` 公有仓库的 `ascend` organization 下。

- **容器-宿主设备透传**: 通过 `--device` 参数将宿主机的 Ascend NPU 设备字符设备直接透传到容器命名空间,使容器内的 vllm-ascend 进程能够通过标准昇腾驱动栈访问 NPU 硬件。该机制依赖宿主机已经安装好 `/usr/local/dcmi`、`/usr/local/Ascend/driver/` 等运行时组件——这些组件通过 `-v` 方式以**只读路径挂载**方式注入容器,避免容器自带的运行时与宿主机版本冲突。

- **模型缓存路径约定**: `${HOME}/.cache` 是 HuggingFace 等模型加载库的默认缓存目录,挂载到容器内的 `/root/.cache` 可以让模型在多次容器启动间复用,避免重复下载。

**性能数据**: 原文未提供任何量化性能指标(如吞吐量、时延、TPS 等),仅给出 `--shm-size=1g` 这一个资源配额数值。

---

## 【表格解读】

**原文无表格。** 文档仅由代码块、警告框与说明文字构成,未出现任何 markdown 表格或对比矩阵。

---

## 【公式解读**

**原文无公式。** 文档不涉及任何数学表达式、LaTeX 或伪代码算法,所有内容均为 shell 命令与文字说明。

---

## 【关联】

> 用户提供的提示中明确标注:**内部链接: (无)**。

根据文末提示,本文档不包含其他内部链接。不过从文档结构可观察到以下隐含关联(均基于原文 `{% include %}` 标签可观察到的引用,非外部链接):

- **`getting_started/quick_start/ascend_image/image_download_mirror.inc.md`**: 镜像下载说明子文档,被本文件通过 `{% include %}` 引入,说明仓库采用"公共片段抽取"模式管理跨硬件平台的镜像获取说明。本文件与 Atlas A2 / 其他型号的快速启动文档**共用**这一片段。

- **镜像标签的 `-a3` / `-a3-openeuler` 后缀**: 暗示仓库存在 `-a2`、`-a3`、`-openeuler` 等区分硬件型号与 OS 的多镜像矩阵,本文档仅覆盖 A3 路径。

- **`#quick-start-atlas-a3-ubuntu`、`#quick-start-atlas-a3-openeuler`、`#quick-start-atlas-a3-container` 三个 anchor (`:id` 显式定义)**: 表明这些小节可能被父级索引页或 README 通过锚点链接引用,但用户提供的元数据中未列出这些外部链接。

---

## 【使用方法】

> 全部内容均源自原文命令块,无任何原文未涉及的扩展。

### 步骤一: 拉取镜像

**Ubuntu**:
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
docker pull "$IMAGE"
```

**openEuler**:
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3-openeuler
docker pull "$IMAGE"
```

> 实际使用时需将 `{{ vllm_ascend_version }}` 替换为具体版本字符串(如 `v0.7.0` 等),原文未给出当前推荐版本号。

### 步骤二: 启动容器 (Ubuntu / openEuler 命令完全一致)

**前置环境变量**:
| 变量 | 值 | 作用 |
|---|---|---|
| `DEVICE0` | `/dev/davinci0` | 第一块 Ascend NPU |
| `DEVICE1` | `/dev/davinci1` | 第二块 Ascend NPU (A3 双 DIE 必需) |
| `MODEL_CACHE` | `${HOME}/.cache` | 宿主机模型缓存根目录 |

**启动命令** (Ubuntu 与 openEuler 共用):

```bash
export DEVICE0=/dev/davinci0
export DEVICE1=/dev/davinci1
export MODEL_CACHE="${HOME}/.cache"

mkdir -p "$MODEL_CACHE"

docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --device "$DEVICE0" \
    --device "$DEVICE1" \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v "$MODEL_CACHE:/root/.cache" \
    -p 8000:8000 \
    -it "$IMAGE" bash
```

### 关键配置项说明 (源自原文)

| docker run 参数 | 原文取值 | 含义 |
|---|---|---|
| `--rm` | (开关) | 容器退出后自动清理 |
| `--name` | `vllm-ascend` | 容器名称 |
| `--shm-size` | `1g` | 共享内存大小 |
| `--device` × 5 | 2 个 NPU + 3 个管理设备 | 设备透传 |
| `-v` × 6 | 驱动库/工具/版本文件 + 模型缓存 | 卷挂载 |
| `-p` | `8000:8000` | 端口映射 (vLLM HTTP 服务) |
| `-it` | (开关) | 交互式 TTY |
| 镜像参数 | `$IMAGE` bash | 以 bash 进入容器 |

### 注意事项 (原文 warning 框)

- **A3 必须提供两个 Ascend 设备节点**,因其 dual-DIE 设计需要;若设备号不是 `0`/`1`,需相应修改 `DEVICE0`、`DEVICE1` 的值(原文仅以 `/dev/davinci0`、`/dev/davinci1` 为示例)。
