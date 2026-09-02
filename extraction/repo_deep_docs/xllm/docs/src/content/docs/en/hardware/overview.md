# overview

> 仓 `xllm` · 路径 `docs/src/content/docs/en/hardware/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/hardware/overview.md

# xLLM Hardware Platforms Overview 深度解读

---

## 【定位】

本文档是 xLLM 推理引擎「硬件平台支持」的**总索引页 (overview/landing page)**,作用是在用户选型阶段提供六大加速器后端的导航入口,并给出跨平台统一的「容器→构建→启动→模型校验」四步通用工作流,使读者快速定位到对应厂商的具体部署文档。

---

## 【技术要点】

1. **多加速器后端抽象**:xLLM 在「大规模模型推理」场景下同时支持 **6 种** 异构加速器后端 (NVIDIA GPU、Ascend NPU、Cambricon MLU、Hygon DCU、MetaX MACA、Mthreads MUSA),各后端对应不同的运行时与集合通信栈。
2. **NVIDIA GPU 后端**:走 **CUDA** 后端,具体驱动/镜像/启动入口见 `/en/hardware/nvidia_gpu/`。
3. **Ascend NPU 后端**:除硬件设置外,文档明确覆盖 **runtime environment (运行环境)** 与 **HCCL launch notes (集合通信启动注意事项)**,这是华为 NPU 集群推理的必填项。
4. **Cambricon MLU 后端**:寒武纪 MLU 后端设置与启动入口,文档路径 `/en/hardware/cambricon_mlu/`。
5. **Hygon DCU 后端**:海光 DCU 后端设置与启动入口,文档路径 `/en/hardware/dcu/`。
6. **MetaX MACA 后端**:MetaX MACA 后端设置与启动入口,文档路径 `/en/hardware/metax_maca/`。
7. **Mthreads MUSA 后端**:提供 **MUSA GPU image、build、launch** 全链路,且**设备选择显式通过环境变量 `MUSA_VISIBLE_DEVICES`**(类比 NVIDIA 的 `CUDA_VISIBLE_DEVICES` / AMD 的 `HIP_VISIBLE_DEVICES`)。
8. **容器化统一交付**:所有平台均建议先准备「平台专属容器镜像」,再在容器内构建 xLLM 或直接使用预置 `xllm` 的 release 镜像。

---

## 【关键机制与数据】

本文为 overview 索引页,**不含**具体性能数据、吞吐量数字或运行时数据流图。可以提炼的「工作原理」均以**导航式机制**呈现,逐条原文标注如下:

- **平台抽象机制** (原文: "xLLM supports multiple accelerator backends for large-scale model inference. This section collects the hardware-specific entry points for environment setup, runtime device selection, launch scripts, and model support."):xLLM 把环境准备、设备选择、启动脚本、模型支持四件事按**硬件厂商拆分**为独立子文档,overview 仅承担目录作用。
- **设备可见性机制** (原文: "device selection via `MUSA_VISIBLE_DEVICES`",仅在 Mthreads MUSA 条目中显式给出):MUSA 后端通过环境变量进行设备过滤;其余 5 个后端的设备选择方式**未在本页披露**,需进入各自子文档查阅。
- **集合通信机制提示** (原文: "HCCL launch notes",仅在 Ascend NPU 条目中显式给出):Ascend 多卡场景需关注 HCCL 配置;其它后端的集合通信栈 (NCCL / CNCL / RCCL 等) **本页未列出**。
- **工作流机制** (原文 4 步):容器镜像 → 构建或 release 镜像 → 匹配后端启动服务 → 校验模型/模态覆盖。

> 注:任何具体 benchmark 数字、显存占用、QPS、时延等性能数据均**不在本文范围**,需进入各硬件子页或 `/en/supported_models/`。

---

## 【表格解读】

**原文无表格。**

整篇文档以 Markdown 列表 + 工作流步骤形式组织,未包含任何参数表、性能对比表或配置项表。表格化的硬件对比需用户自行对照六个子文档拼合。

---

## 【公式解读】

**原文无公式。**

本页不含任何 LaTeX 公式或伪代码表达式,无符号需要解释。

---

## 【关联】

本页是硬件平台的「目录树根节点」,向下链接至**6 个厂商子文档**,横向链接至**2 个跨平台入口**,形成如下依赖图:

| 关联方向 | 链接 | 关系性质 |
|---|---|---|
| 下游 (硬件子文档) | `/en/hardware/nvidia_gpu/` | NVIDIA CUDA 后端详细配置 |
| 下游 | `/en/hardware/ascend_npu/` | Ascend NPU + HCCL 配置 |
| 下游 | `/en/hardware/cambricon_mlu/` | Cambricon MLU 后端配置 |
| 下游 | `/en/hardware/dcu/` | Hygon DCU 后端配置 |
| 下游 | `/en/hardware/metax_maca/` | MetaX MACA 后端配置 |
| 下游 | `/en/hardware/musa/` | Mthreads MUSA 后端配置 |
| 横向 (启动入口) | `/en/getting_started/launch_xllm/` | 跨平台统一启动服务文档,被 Common Workflow 第 3 步引用 |
| 横向 (模型校验) | `/en/supported_models/` | 模型/模态覆盖矩阵,被 Common Workflow 第 4 步引用 |

**耦合逻辑**:
- 6 个硬件子文档是本文的**事实唯一来源** (single source of truth),所有具体命令、镜像 tag、驱动版本号均下沉到子文档。
- `launch_xllm` 是**后端无关的启动入口**,与硬件子文档形成「硬件专属准备 + 通用启动脚本」的正交关系。
- `supported_models` 是**后端 × 模型** 的能力矩阵,用户在完成 Common Workflow 前 3 步后,必须回到此处确认目标模型在该硬件上是否受支持 (例如某些模型仅在 NVIDIA GPU 上提供量化路径)。

---

## 【使用方法】

原文给出的是**通用 4 步工作流** (Common Workflow),完整还原如下:

1. **准备平台专属容器镜像** (原文: "Prepare the platform-specific container image from the explicit commands in each platform guide.")——具体 `docker pull` / 镜像 tag 在 6 个子文档中给出,本页**未列具体命令**。
2. **在容器内构建 xLLM,或使用预置 release 镜像** (原文: "Build xLLM inside the container, or use a release image that already includes `xllm`.")——两种交付方式二选一;release 镜像内已含可执行 `xllm`。
3. **以匹配设备后端启动服务** (原文: "Start the service with the matching device backend in [Launch xllm](/en/getting_started/launch_xllm/).")——具体启动参数、配置文件、CLI flag 跳转至 `/en/getting_started/launch_xllm/`。
4. **校验模型与模态覆盖** (原文: "Check model and modality coverage in the [Model Support List](/en/supported_models/).")——确认目标 LLM/多模态模型在所选硬件上受支持。

**显式给出的命令/环境变量**:
- `MUSA_VISIBLE_DEVICES`(Mthreads MUSA 设备选择,类 CUDA/HIP 设备可见性变量)。

**原文未涉及的内容**(需在子文档查阅):
- 各平台具体的驱动版本、CUDA/CANN 版本、Python 版本要求。
- NCCL / HCCL / CNCL / RCCL / MCCL 等集合通信库版本约束。
- 镜像仓库地址、镜像 tag 列表、`docker run` 完整命令模板。
- 配置文件 (yaml/toml) 的字段说明。
- 多卡并行 (TP/PP/EP) 的拓扑与配置。
