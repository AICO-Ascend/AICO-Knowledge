# MinerU 加速镜像

> 仓 `ragsdk` · 路径 `example/mineru-accelerate/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ragsdk/example/mineru-accelerate/OVERVIEW.zh.md

# MinerU 加速镜像 — 深度解读

## 【定位】
本文档描述了 RAG SDK 中 `mineru-accelerate` 镜像的能力与使用方式——它是一个**基于 vllm-ascend 镜像二次集成、面向文档解析场景的推理加速容器**，把 MinerU2.5 系列模型在昇腾 NPU 上的部署、加速开关与容器化运行流程整体封装好，让用户能"拉镜像、改 config、跑容器"三步在 Atlas 910 硬件上完成 MinerU 加速推理。

---

## 【技术要点】

1. **镜像底座与定位**：在 `vllm-ascend` 镜像之上集成 MinerU 加速优化，专门服务于"文档解析"推理场景，目前仅支持 MinerU2.5 模型。
2. **支持硬件**：仅列示 **Atlas 910** 系列芯片（含 Atlas 800T A2、Atlas 900 A2 PoD），覆盖 **ARM64 / X86_64** 两种架构。
3. **支持模型**：3 个 MinerU2.5 模型（均为 1.2B 参数量级）：
   - `OpenDataLab/MinerU2.5-2509-1.2B`
   - `OpenDataLab/MinerU2.5-Pro-2605-1.2B`
   - `OpenDataLab/MinerU2.5-Pro-2604-1.2B`
4. **Tag 规范**：`mineru镜像版本-操作系统-python版本-架构类型`，示例 `0.1.22-ubuntu22.04-py3.11-aarch64`，其中 `mineru_vl_utils` 版本固定为 **0.1.22**，OS 为 **ubuntu22.04**，Python 为 **py3.11**，架构为 **aarch64**。
5. **加速开关（关键）**：运行容器后必须在 `config.json` 中追加两个字段开启加速：
   ```json
   "prune_encoder": true,
   "process_single_image": true
   ```
   文档明确：以 `MinerU2.5-2509-1.2B` 为例，修改 `{model_path}/MinerU2.5-2509-1.2B/config.json`，在文件末尾、`}` 之前添加上述字段。
6. **加速补丁**：随镜像附带两份 patch，是真正实现加速的关键源码改动：
   - `patch/vllm_adapt.patch` — vllm 适配 MinerU 的补丁，应用于 `/vllm-workspace/vllm/`
   - `patch/mineru_adapt.patch` — `mineru_vl_utils` 加速优化补丁，应用于 `mineru_vl_utils` 安装目录
7. **运行容器命令**：需挂载 NPU 设备与驱动目录，典型参数 `--device=/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm`、`/dev/davinci0`，并把 `/usr/local/Ascend/driver`、`/usr/local/sbin` 只读挂载进去（`/path/to/model` 替换为实际模型目录）。NPU 卡号需按实际情况修改（如 davinci0、davinci4 等）。
8. **本地构建**：通过 `git clone https://gitcode.com/Ascend/RAGSDK.git` → `cd RAGSDK/example/mineru-accelerate` → `docker build -t mineru:0.1.22-ubuntu22.04-py3.11-aarch64 --network host -f Dockerfile .` 在本地重新构建镜像。

---

## 【关键机制与数据】

- **加速实现路径（原文层面可读到的）**：原文未给出量化加速比、tokens/sec、显存占用等性能数字；只描述了"集成 MinerU 加速优化"、"用于文档解析场景的推理加速"，加速主要靠两个补丁叠加 + `config.json` 两个开关来启用。
- **数据流（原文层面）**：
  1. 宿主机挂载 `/usr/local/Ascend/driver`、`/usr/local/sbin` 与 `/path/to/model` 进容器；
  2. NPU 设备（davinci_manager、hisi_hdc、devmm_svm、davinci0）通过 `--device` 直通容器；
  3. 容器启动后，进入模型目录在 `config.json` 注入 `prune_encoder` 与 `process_single_image` 开关；
  4. 在容器内调用 MinerU 推理（MinerU 自身快速开始指南说明）。
- **关键参数（原文中的硬性数字）**：
  - `mineru_vl_utils` 版本：**0.1.22**
  - OS：**ubuntu22.04**
  - Python：**py3.11**
  - 架构：**aarch64**
  - 镜像 Tag 示例：**0.1.22-ubuntu22.04-py3.11-aarch64**
  - 模型参数规模：均为 **1.2B**

> **原文未提供**：推理时延、吞吐（QPS/tokens-per-sec）、与 GPU/CPU 基线的对比数据、显存/显存带宽占用、NPU 利用率等性能指标 — 本文不做臆测。

---

## 【表格解读】

### 表 1 — 支持的硬件（原文逐字还原）

| 芯片系列 | 产品示例 | 架构 |
| -------- | -------- | ---- |
| Atlas 910 | Atlas 800T A2、Atlas 900 A2 PoD | ARM64/ X86_64 |

**逐行解读**：
- **Atlas 910 行**：明确该镜像只面向昇腾 **Atlas 910** 系列（产品示例给出 Atlas 800T A2 和 Atlas 900 A2 PoD 两款），并覆盖 ARM64 与 X86_64 两种主机 CPU 架构。原文未列出其他芯片系列（如 Atlas 300I、Atlas 200 等），即不在本镜像支持范围。

### 表 2 — Tag 规范（原文逐字还原）

| 字段                | 示例值   | 说明                                                         |
| ------------------- | -------- | ------------------------------------------------------------ |
| mineru镜像版本                | 0.1.22     | 支持的mineru_vl_utils版本为0.1.22     |
| 操作系统                | ubuntu22.04   | 目标操作系统                         |
| python版本                | py3.11      | 目标python版本                         |
| 架构类型                | aarch64      | 目标架构类型                         |

**逐行解读**：
- **mineru镜像版本 / 0.1.22**：镜像版本号与 `mineru_vl_utils` 版本号在本文档示例中是同一个值（0.1.22），含义是镜像与底层 `mineru_vl_utils` 版本一一对应。
- **操作系统 / ubuntu22.04**：当前仅给出 Ubuntu 22.04 这一种 OS 选项。
- **python版本 / py3.11**：Python 解释器版本固定 3.11。
- **架构类型 / aarch64**：当前 Tag 示例是 ARM 架构；由于表 1 列出 ARM64/X86_64 均支持，理论上可衍生出 `x86_64` 版本 Tag（但原文 Tag 示例与 Dockerfile 链接仅给了 aarch64）。

### 表 3 — Dockerfile 链接（原文逐字还原）

| Tag                | Dockerfile  |
| ------------------- | -------- |
| 0.1.22-ubuntu22.04-py3.11-aarch64     | [Dockerfile](https://gitcode.com/Ascend/RAGSDK/blob/master/example/mineru-accelerate/Dockerfile)  |

**逐行解读**：
- 唯一一条 Tag 即为上节示例的具体落地：版本 0.1.22 + Ubuntu 22.04 + Python 3.11 + aarch64。其 Dockerfile 指向仓库根路径 `example/mineru-accelerate/Dockerfile`，是本地构建章节使用的同一文件。

### 表 4 — 文件说明（原文逐字还原）

| 文件 | 说明 |
| ---- | ---- |
| Dockerfile | 镜像构建文件 |
| patch/vllm_adapt.patch | vllm 适配 MinerU 的补丁，应用于 /vllm-workspace/vllm/ |
| patch/mineru_adapt.patch | mineru_vl_utils 加速优化补丁，应用于 mineru_vl_utils 安装目录 |

**逐行解读**：
- **Dockerfile**：定义从 `vllm-ascend` 基础镜像到最终 `mineru` 镜像的构建流程（含两份 patch 的打补丁步骤）。
- **patch/vllm_adapt.patch**：让 `vllm` 推理框架对接 MinerU 模型/数据格式；应用根目录为 `/vllm-workspace/vllm/`（即 vllm-ascend 工作区内的 vllm 源码）。
- **patch/mineru_adapt.patch**：对 `mineru_vl_utils` 包进行加速优化；应用位置是其安装目录（即 python site-packages 下的 mineru_vl_utils 路径）。这两份 patch 合起来才是 "加速" 的核心来源，单独靠镜像底座无法获得加速效果。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档内部链接未单独罗列，但通过文中描述可梳理以下关联关系：

- **基础镜像层**：本文镜像**基于 `vllm-ascend` 镜像**构建（原文："基于 vllm-ascend 镜像，集成 MinerU 加速优化"），因此 RAG SDK 中所有面向 vllm-ascend 的上层能力（如 vLLM 推理后端、昇腾 NPU 调度）在本镜像内同样可用。
- **补丁依赖链**：
  - `vllm_adapt.patch` 作用于 **/vllm-workspace/vllm/**（vllm-ascend 工作区内的 vllm 源码），是 vllm 与 MinerU 模型对接的桥梁。
  - `mineru_adapt.patch` 作用于 **mineru_vl_utils 安装目录**，对上一步做了面向昇腾的加速优化。
- **模型 ↔ 容器配置 ↔ 运行时**：
  - 模型层（`MinerU2.5-2509-1.2B` 等）需要**挂载到容器**（`-v /path/to/model:/path/to/model`）；
  - 配置层（`config.json`）需要手动追加 `prune_encoder` 与 `process_single_image`；
  - 运行时层（MinerU 自身推理）需参考外部文档 [MinerU 快速开始使用](https://opendatalab.github.io/MinerU/zh/quick_start/)。
- **硬件层**：仅与 **Atlas 910** 系列芯片（即 Atlas 800T A2、Atlas 900 A2 PoD）配套使用，其它昇腾芯片不在支持之列。
- **NPU 设备透传**：`--device=/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm`、`/dev/davinci0` 是昇腾 NPU 在容器内运行所必需的四类设备节点，与驱动目录 `/usr/local/Ascend/driver` 配合才能完成设备初始化。
- **RAG SDK 仓库上下文**：本镜像属于 RAG SDK（昇腾面向大语言模型的知识增强开发套件）的 `example/` 示例目录，用以解决"大模型知识更新缓慢、垂直领域知识回答弱"问题中**文档解析→知识入库**前置环节的推理加速问题；上游文档解析结果通常会喂给 RAG SDK 的知识库与生成增强模块。
- **反馈/获取渠道**：issue 反馈、RAG SDK 代码仓库、AscendHub 镜像仓库（参见文首"快速参考"）。

---

## 【使用方法】

### 1. 拉取/获取镜像
- 通过 AscendHub 镜像仓库获取 `mineru:0.1.22-ubuntu22.04-py3.11-aarch64`（原文："[镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/mineru)"）。
- 或者从本地构建：
  ```bash
  git clone https://gitcode.com/Ascend/RAGSDK.git && cd RAGSDK/example/mineru-accelerate
  docker build -t mineru:0.1.22-ubuntu22.04-py3.11-aarch64 --network host -f Dockerfile .
  ```

### 2. 运行容器（关键命令，原文逐字保留）
```bash
docker run -u root -itd --name=mineru-accelerate --network=host \
    --device=/dev/davinci_manager \
    --device=/dev/hisi_hdc \
    --device=/dev/devmm_svm \
    --device=/dev/davinci0 \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro \
    -v /usr/local/sbin:/usr/local/sbin:ro \
    -v /path/to/model:/path/to/model \
    mineru:0.1.22-ubuntu22.04-py3.11-aarch64 bash
```
参数要点：
- `/path/to/model`：宿主机上 MinerU 模型目录（如 MinerU2.5-2509-1.2B 模型存放处）。
- `--device=/dev/davinci0`：NPU 卡号，按实际环境改为 `davinci0`/`davinci4` 等。
- `--device=/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm`：NPU 必需的管理/通信设备节点。
- `-v /usr/local/Ascend/driver`、`/usr/local/sbin`：以**只读**方式挂载昇腾驱动目录与系统脚本目录。

### 3. 修改模型配置以启用加速（关键步骤）
进入容器后，在模型目录下的 `config.json` 末尾、`}` 之前追加：
```json
"prune_encoder": true,
"process_single_image": true
```
以 `MinerU2.5-2509-1.2B` 为例，修改路径为 `{model_path}/MinerU2.5-2509-1.2B/config.json`。

### 4. 进入容器
```bash
docker exec -it mineru-accelerate bash
```

### 5. 开始 MinerU 推理
进入容器后，按 [MinerU 快速开始使用](https://opendatalab.github.io/MinerU/zh/quick_start/) 执行文档解析推理。

> **原文未提供**：如 `compose.yaml`、Helm Chart、环境变量列表、健康检查脚本、版本兼容矩阵等更细粒度的运维配置项 — 本文不做臆造。
