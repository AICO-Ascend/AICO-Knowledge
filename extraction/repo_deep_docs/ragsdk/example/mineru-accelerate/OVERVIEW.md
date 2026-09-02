# MinerU Acceleration Image

> 仓 `ragsdk` · 路径 `example/mineru-accelerate/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ragsdk/example/mineru-accelerate/OVERVIEW.md

# MinerU Acceleration Image 文档深度解读

## 【定位】

这篇文档描述的是 RAG SDK 中基于 vllm-ascend 基础镜像二次集成的 MinerU 推理加速镜像，聚焦**文档解析场景**下的 MinerU2.5 模型部署与 NPU 加速能力，告知用户如何拉取/构建镜像、运行容器、修改模型配置以启用加速。

---

## 【技术要点】

1. **基础镜像与加速集成**：在 vllm-ascend 镜像之上集成 MinerU 加速优化,目标场景为文档解析推理加速;当前支持的模型版本为 **MinerU2.5**(原文:"Currently, the MinerU2.5 model is supported.")。
2. **硬件适配范围**:仅适配 **Atlas 910** 系列芯片,代表产品为 **Atlas 800T A2** 与 **Atlas 900 A2 PoD**,支持 **ARM64/X86_64** 两种架构。
3. **支持的模型清单**(均为 1.2B 规模):
   - `OpenDataLab/MinerU2.5-2509-1.2B`
   - `OpenDataLab/MinerU2.5-Pro-2605-1.2B`
   - `OpenDataLab/MinerU2.5-Pro-2604-1.2B`
4. **镜像 Tag 命名规范**:`<image-version>-<os>-<python-version>-<architecture>`,示例 `0.1.22-ubuntu22.04-py3.11-aarch64`,其中 `image-version` 对应 **mineru_vl_utils 0.1.22**。
5. **NPU 设备透传参数**:启动容器需挂载 `/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm` 以及具体 NPU 卡(如 `davinci0`),并以 `--network=host`、`-u root` 方式运行。
6. **模型级加速开关**:在模型目录的 `config.json` 中追加两个字段 `"prune_encoder": true` 与 `"process_single_image": true`,即可开启 MinerU 加速优化(原文未给出额外参数取值范围)。

---

## 【关键机制与数据】

- **工作机制(原文)**:
  1. 镜像在 vllm-ascend 基础上叠加两个 patch:
     - `patch/vllm_adapt.patch`:对 vLLM 做适配,作用于 `/vllm-workspace/vllm/` 目录;
     - `patch/mineru_adapt.patch`:为 `mineru_vl_utils` 提供加速 patch,作用于其安装目录。
  2. 容器内通过挂载宿主机 Ascend 驱动(`/usr/local/Ascend/driver`、`/usr/local/sbin`)使 NPU 设备可用。
  3. 模型目录下 `config.json` 中添加 `"prune_encoder": true` 与 `"process_single_image": true` 是启用 MinerU 加速的必要开关(原文:"to enable acceleration")。
- **数据流(原文)**:宿主机模型目录 → 容器内 `/path/to/model` → 修改 `config.json` 启用 prune_encoder 与 process_single_image → 由 MinerU2.5 + vLLM-Ascend 在 Atlas 910 NPU 上完成文档解析推理。
- **性能数据**:原文未提供任何 TPS、时延、加速比等量化指标,本文不臆造。

---

## 【表格解读】

### 1) Supported Hardware(支持的硬件)

| Chip Series | Product Examples | Architecture |
| ----------- | ---------------- | ------------ |
| Atlas 910 | Atlas 800T A2, Atlas 900 A2 PoD | ARM64/ X86_64 |

**解读**:该表定义镜像的硬件兼容域——仅 **Atlas 910** 系列可用,具体代表机型是 **Atlas 800T A2** 与 **Atlas 900 A2 PoD**,架构同时支持 **ARM64 与 X86_64**,意味着用户不论部署在鲲鹏 ARM 服务器还是通用 X86 服务器上的 Atlas 910 设备均可使用。

### 2) Tag Specification(Tag 字段说明)

| Field | Example | Description |
| ----- | ------- | ----------- |
| image-version | 0.1.22 | The supported mineru_vl_utils version is 0.1.22 |
| os | ubuntu22.04 | Target operating system |
| python-version | py3.11 | Target Python version |
| architecture | aarch64 | Target architecture type |

**解读**:Tag 由四个段拼接而成,逐段含义为:
- `image-version` = **0.1.22**,对应 `mineru_vl_utils` 的 **0.1.22** 版本——这是加速能力所依赖的关键 Python 包版本;
- `os` = **ubuntu22.04**,目标操作系统;
- `python-version` = **py3.11**,目标 Python 解释器版本;
- `architecture` = **aarch64**,目标 CPU 架构(注意此处与 Supported Hardware 表中"ARM64/ X86_64"形成对照:Tag 字段示例当前仅给出 aarch64 一种)。

### 3) Dockerfile Links(镜像 Tag 与 Dockerfile 映射)

| Tag | Dockerfile |
| --- | ---------- |
| 0.1.22-ubuntu22.04-py3.11-aarch64 | [Dockerfile](https://gitcode.com/Ascend/RAGSDK/blob/master/example/mineru-accelerate/Dockerfile) |

**解读**:当前仅维护一个 Tag(`0.1.22-ubuntu22.04-py3.11-aarch64`),其 Dockerfile 位于仓库 `example/mineru-accelerate/Dockerfile`,意味着 x86_64 架构的对应 Tag 暂未在该表中列出。

### 4) File Description(文件清单)

| File | Description |
| ---- | ----------- |
| Dockerfile | Image build file |
| patch/vllm_adapt.patch | vllm adaptation patch for MinerU, applied to /vllm-workspace/vllm/ |
| patch/mineru_adapt.patch | mineru_vl_utils acceleration patch, applied to mineru_vl_utils installation directory |

**解读**:镜像源码目录结构极简,核心只有 3 个文件:
- `Dockerfile` 用于镜像构建;
- 两个 `.patch` 文件分别在镜像构建阶段打到 **vLLM 源码目录** 与 **mineru_vl_utils 安装目录**,二者叠加形成"MinerU 加速"能力,即文档解析性能来源于这两处源代码改动,而非仅靠镜像层级配置。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游基础镜像**:基于 `vllm-ascend` 镜像二次集成,意味着其继承了 vLLM-Ascend 在 Atlas NPU 上的推理能力。
- **加速能力来源**:通过两个 patch 注入到 vLLM 与 `mineru_vl_utils` 中——`vllm_adapt.patch`(作用于 `/vllm-workspace/vllm/`)与 `mineru_adapt.patch`(作用于 `mineru_vl_utils` 安装目录)。
- **上游模型生态**:依赖 ModelScope 上的 OpenDataLab MinerU2.5 系列 1.2B 模型(共 3 个版本)。
- **下游使用指引**:容器内使用流程指向外部文档 [MinerU Quick Start](https://opendatalab.github.io/MinerU/zh/quick_start/),RAG SDK 仓库本身不重复 MinerU 的使用细节。
- **问题反馈渠道**:文末"Quick Reference"列出了 [Issue Feedback](https://gitcode.com/Ascend/RAGSDK/issues) 与 [RAG SDK Code](https://gitcode.com/Ascend/RAGSDK) 仓库入口,以及镜像仓库 [AscendHub - mineru](https://www.hiascend.com/developer/ascendhub/detail/mineru),作为问题追踪与镜像拉取的官方入口。
- **许可证约束**:遵循 [RAGSDK LICENSE](https://gitcode.com/Ascend/RAGSDK/blob/master/LICENSE.md),并提示镜像内预装包(Python、系统库)各有独立 License。

---

## 【使用方法】

### 1) 拉取并运行容器(原文)

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

### 2) 关键配置项(原文)

- **`/path/to/model`**:宿主机上的模型存放目录,需挂载到容器内,例如将 `MinerU2.5-2509-1.2B` 模型文件放入该目录;
- **`--device=/dev/davinci0`**:NPU 卡 ID,需根据实际环境修改(如 `davinci0`、`davinci4` 等);
- **`config.json` 加速开关**:进入容器后,在模型目录的 `config.json` 末尾 `}` 前追加:
  ```json
  "prune_encoder": true,
  "process_single_image": true
  ```
  例:`{model_path}/MinerU2.5-2509-1.2B/config.json`。

### 3) 进入容器(原文)

```bash
docker exec -it mineru-accelerate bash
```

### 4) 镜像本地构建(原文)

```bash
# 在宿主机上克隆仓库并进入 mineru-accelerate 目录
git clone https://gitcode.com/Ascend/RAGSDK.git && cd RAGSDK/example/mineru-accelerate

docker build -t mineru:0.1.22-ubuntu22.04-py3.11-aarch64 --network host -f Dockerfile .
```

### 5) 容器内业务使用

容器启动并完成 `config.json` 修改后,MinerU 解析推理的 API/CLI 用法不在本文档范围内,需参考 [MinerU Quick Start](https://opendatalab.github.io/MinerU/zh/quick_start/)。
