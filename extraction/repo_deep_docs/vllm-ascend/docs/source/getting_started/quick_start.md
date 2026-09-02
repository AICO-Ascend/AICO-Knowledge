# Quick Start

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start.md

# vllm-ascend Quick Start 文档深度解读

## 【定位】

这是一篇面向**首次接触 vLLM Ascend 的开发者**的入门指南,以 **Qwen3-0.6B** 为示例模型,指导用户如何在**已就绪的 Ascend 主机**上,通过**预构建容器镜像**完成**首次离线推理(offline inference)或在线服务部署(online serving)**。文档本身更像是"骨架/导航页"——通过 Jinja2 `{% include %}` 标签把按硬件分桶、按场景分桶的子文档片段装配进来。

## 【技术要点】

1. **示例模型**:使用 **Qwen3-0.6B** 作为入门示例(原文:"uses Qwen3-0.6B as an example")。
2. **运行环境硬性要求**(Requirements 段): Python 版本由模板变量 `{{ release_python_version }}` 注入(原文未给出具体数字,因 build 时由 mkdocs/releaser 替换);需 **Docker**;操作系统为 **Linux**。
3. **支持的硬件**(从 include 占位符可推断的五大类):**Atlas A2、A3、950DT、Atlas 300I DUO、Atlas 200I Pro**(具体设备清单在 `supported_hardware.inc.md` 中,本原文未直接列出)。
4. **预构建镜像软件栈**(原文直接列出):CANN、NNAL、PyTorch、TorchNPU、vLLM、vLLM Ascend;**A2、A3、950DT 镜像额外包含 Triton Ascend runtime**;**Atlas 300I DUO 与 Atlas 200I Pro 不使用 Triton Ascend**。
5. **Hugging Face 受限时的降级方案**(原文 tip 块):设置 `export VLLM_USE_MODELSCOPE=True` 并 `pip install "modelscope>=1.18.1,<1.38"` 切换到 ModelScope;若模型已本地下载,直接替换示例中的 model ID 即可,**无需设置该环境变量**。
6. **场景分桶与硬件分桶的双重维度**:
   - 场景维度:**离线推理(Offline inference)** 与 **在线服务(Online serving)**,各占一个小节;
   - 硬件维度:每种场景下分为 **"A2 / A3 / 950DT"** 与 **"Atlas 300I DUO / Atlas 200I Pro"** 两个 tab,后者使用 `qwen3-0.6b-310p.inc.md`(310P 命名暗示是 310P 处理器适配路径)。

## 【关键机制与数据】

> **原文方法论说明**:本原文大量使用 MkDocs Material 的 Jinja2 模板(`{% include %}`、`{% filter indent %}`),正文骨架是"标签+引用",实际可执行的命令/脚本代码全部位于外部 `.inc.md` 片段中,本原文**未直接呈现**这些片段的内容。因此下文只解读原文骨架所揭示的工作流结构。

- **工作流结构(按原文)**:Requirements → Installation → Inference(Offline + Online) → Next steps。
- **安装路径(Installation)**:原文展示了 **5 套 include 引用**(`atlas-a2.inc.md`、`atlas-a3.inc.md`、`atlas-300i-duo.inc.md`、`atlas-200i-pro.inc.md`、`atlas-950dt.inc.md`),每套引用后面紧跟一段 `verify_container.inc.md`,说明容器启动后会调用统一的"容器验证"片段,即**所有硬件共用一套容器验证流程**,而镜像拉取/启动参数按硬件分桶。
- **推理路径(Inference)**:
  - Offline tab "A2/A3/950DT" → `getting_started/quick_start/offline/qwen3-0.6b.inc.md`
  - Offline tab "Atlas 300I DUO / Atlas 200I Pro" → `getting_started/quick_start/offline/qwen3-0.6b-310p.inc.md`
  - Online tab "A2/A3/950DT" → `getting_started/quick_start/online/qwen3-0.6b.inc.md`
  - Online tab "Atlas 300I DUO / Atlas 200I Pro" → `getting_started/quick_start/online/qwen3-0.6b-310p.inc.md`
- **性能数据**:原文无任何 benchmark/吞吐量/延迟数字。
- **数据流/架构图**:原文无。

## 【表格解读】

**原文无表格。** 文档采用 MkDocs Material 的 Admonition(??? note / ??? tip)、Tab(`=== "..."`)以及 Jinja include 来组织信息,没有任何 `<table>` 或 markdown 表格语法。

## 【公式解读】

**原文无公式。**

## 【关联】

文档通过文末 **Next steps** 与正文中的超链接,织出了如下上下游关系网:

| 文档内的引用位置 | 指向路径 | 作用 |
|---|---|---|
| Requirements → Software stack 注释 | `installation.md#installation-hardware-software-stack` | 给出**各硬件对应的 CANN/NNAL/PyTorch/TorchNPU/vLLM/vLLM Ascend 精确已验证版本**(原文:"For the exact validated versions, see Installation Guide > Hardware and software stack") |
| Next steps 第 1 条 | `../user_guide/support_matrix/supported_models.md` | **Supported Models** 索引——在本指南之后,用户据此挑选其它可用模型 |
| Next steps 第 2 条 | `../tutorials/models/index.md` | **Model Tutorials** 索引——具体模型(可能是其它 Qwen、DeepSeek、Llama 等)的部署教程入口 |
| Next steps 第 3 条 | `installation.md#installation-software-environment` | **Installation Guide > Set up the software environment**——pip、CANN、源码三种非容器安装路径(说明本指南的容器路径并非唯一安装方式) |
| Next steps 第 4 条 | `../tutorials/features/index.md` | **Feature Tutorials**——**分布式部署**(distributed deployment)与高级特性,定位高于 Quick Start 的进阶内容 |
| Next steps 第 5 条 | `../faqs.md` | **FAQ**——常见部署问题排查 |
| 正文 Docker 安装提示 | `https://docs.docker.com/get-started/get-docker/` | 外部链接,容器化前置依赖 |
| 容器内的 `<span id="...">` 锚点 | `quick-start-atlas-a2-offline` / `quick-start-atlas-a3-offline` / `quick-start-atlas-950dt-offline` / `quick-start-atlas-300i-duo-offline` / `quick-start-atlas-200i-pro-offline` 与同组 `*-online` | 用于让外部文档/教程精确跳转到"某硬件 × 某场景"的代码片段位置,体现文档对外是**可被深链的模块化导航页** |

**关联总结**:Quick Start 处于"上手层",向上承接 **Installation Guide**(环境与软件栈版本),向下展开到 **Model Tutorials**(具体模型部署)与 **Feature Tutorials**(分布式/高级特性),侧向关联 **Supported Models**(模型选型)与 **FAQ**(故障排查)。它本身不重复这些文档的内容,而是充当**带硬件与场景分桶路由的入口**。

## 【使用方法】

> 本原文大量命令被 `{% include %}` 收纳到外部 `.inc.md`,因此下面的"启用方式/配置项/命令"仅整理**原文骨架中可直接看到的**部分。

**1. 启用方式(总览)**
- 入口是 **预构建的 vLLM Ascend 容器镜像**,而非 pip 安装。
- 镜像内已包含的栈:CANN、NNAL、PyTorch、TorchNPU、vLLM、vLLM Ascend(其中 A2/A3/950DT 还含 Triton Ascend runtime)。

**2. 硬件分支(Installation 段呈现的 include 分桶,原文以 include 标签声明)**
| 硬件分支 | 镜像说明片段 | 容器验证片段 |
|---|---|---|
| Atlas A2 | `getting_started/quick_start/ascend_image/atlas-a2.inc.md` | `getting_started/quick_start/ascend_image/verify_container.inc.md`(缩进 4) |
| Atlas A3 | `.../atlas-a3.inc.md` | 同上 verify_container |
| Atlas 300I DUO | `.../atlas-300i-duo.inc.md` | 同上 verify_container |
| Atlas 200I Pro | `.../atlas-200i-pro.inc.md` | 同上 verify_container |
| Atlas 950DT | `.../atlas-950dt.inc.md` | 同上 verify_container |

**3. 推理分支(Inference 段呈现的 include 分桶)**
| 场景 | 硬件 | 脚本片段(原文 include 标签) |
|---|---|---|
| Offline | A2 / A3 / 950DT | `getting_started/quick_start/offline/qwen3-0.6b.inc.md` |
| Offline | Atlas 300I DUO / Atlas 200I Pro | `getting_started/quick_start/offline/qwen3-0.6b-310p.inc.md` |
| Online | A2 / A3 / 950DT | `getting_started/quick_start/online/qwen3-0.6b.inc.md` |
| Online | Atlas 300I DUO / Atlas 200I Pro | `getting_started/quick_start/online/qwen3-0.6b-310p.inc.md` |

**4. 配置项/命令(原文可直接引用的)**
- **环境变量(可选,仅在 HF 受限时)**:
  ```bash
  export VLLM_USE_MODELSCOPE=True
  pip install "modelscope>=1.18.1,<1.38"
  ```
- **Python 版本**:由 `{{ release_python_version }}` 注入,原文未给出字面量(具体值需查项目 release 配置)。
- **前置软件**:Docker(原文:"make sure Docker is installed on your system"),未给具体 `docker pull` / `docker run` 命令(均在被 include 的 `.inc.md` 中)。
- **本地模型复用**:如模型已下载到本地,把示例中的 model ID **替换为本地目录** 即可,且**不需要** `VLLM_USE_MODELSCOPE`(原文:"replace the model ID in the examples below with the local directory. You do not need to set this environment variable")。

**5. 容器内镜像验证**
- 每个硬件分支在拉起镜像后都会调用同一份 `verify_container.inc.md`(以 4 空格缩进嵌入),说明**验证流程跨硬件统一**。

**6. 模型替换为其它 Qwen3 之外模型**
- 原文未直接给出步骤,而是把读者引向 **`../user_guide/support_matrix/supported_models.md`**(看可用模型)与 **`../tutorials/models/index.md`**(看具体部署);可推断流程为:选模型 → 看 Supported Models 确认支持 → 跳到对应 Model Tutorial → 按其指示替换 model ID。

> 总结:本原文在"使用方法"层面给出的**可直接执行的关键字面量**只有两条——`VLLM_USE_MODELSCOPE=True` 与 `pip install "modelscope>=1.18.1,<1.38"`;其余具体 `docker run` / `vllm serve` / `LLM(...)` 等命令都被 include 隐藏,需查阅被引用的 `.inc.md` 片段才能获得逐字内容。
