# Torchvision Adapter Plug-in Quick Start

> 仓 `vision` · 路径 `docs/en/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vision/docs/en/quick_start.md

# Torchvision Adapter Plug-in Quick Start — 一体化深度解读

---

## 【定位】

本指南描述**如何快速启用 Torchvision Adapter 插件**，使原生 `torchvision` 算子能够在昇腾 NPU 上以"原生调用方式"直接运行——即无需修改调用代码，仅通过 `import torchvision_npu` 一行即可把已有的 Torchvision 算子调用切换到 NPU 后端。

---

## 【技术要点】

1. **CANN 环境变量初始化**
   通过 `source /usr/local/Ascend/ascend-toolkit/set_env.sh`（root 用户默认路径，需按实际替换）来激活 CANN 工具链环境。

2. **Docker 使用 DVPP 时需要设备映射**
   Docker 容器场景下使用 DVPP 功能时，必须将宿主机的 `/dev/dvpp_cmdlist` 设备文件映射进容器，并按《Docker 安全加固》文档要求处理文件权限。

3. **NPU 适配的核心机制：原生调用 + 自动后端切换**
   CUDA/CPU 环境下，原文示例算子 `torchvision.ops.nms(boxes, scores, iou_threshold)` 接收 CPU/CUDA Tensor；安装 Torchvision Adapter 插件后，仅追加 `import torchvision_npu`（同时仍保留 `import torch_npu`）即可让相同调用语法自动落到 NPU 后端，boxes/scores 变为 NPU Tensor。

4. **导入顺序要求**
   原文示例代码中显式列出四条导入：`torch`、`torch_npu`、`torchvision`、`torchvision_npu`，且 NPU 版本的示例同时引入了 `torch_npu` 与 `torchvision_npu`，暗示二者需配合加载。

5. **调用接口保持不变**
   同一函数签名 `torchvision.ops.nms(boxes, scores, iou_threshold)` 在 NPU 下被透传，仅参数 Tensor 的设备类型由 CPU/CUDA 变为 NPU。

---

## 【关键机制与数据】

- **原文机制描述**：在 CUDA/CPU 版本中，`torchvision.ops.nms` 由 CUDA/CPU 算子实现；在安装 Torchvision Adapter 插件后，调用栈被改写为 NPU 算子实现。原文通过 NMS 这一个典型算子示例来说明该适配机制，因此可推断其底层采用"算子级重定向"思路——注册同名算子到 NPU 后端，使得 `torchvision.ops.*` 的调用点无需改动。
- **原文数据**：本指南**未提供**任何性能数字、吞吐、延迟等量化数据，亦未给出适配算子的具体数量/覆盖范围/版本号。
- **环境依赖（原文给出）**：昇腾 CANN 工具包路径 `/usr/local/Ascend/ascend-toolkit/set_env.sh`；Docker 下 DVPP 依赖 `/dev/dvpp_cmdlist` 设备文件。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **CANN 环境层**：文档开头要求 `source ascend-toolkit/set_env.sh`，说明 Torchvision Adapter 插件**依赖 CANN 工具链**所提供的运行时与算子库，是其底层执行环境。
- **DVPP 与 Docker 集成**：NOTE 中指向外部文档 *Docker security hardening*（链接 `https://www.hiascend.com/document/detail/en/mindcluster/730/clustersched/dlug/mxdlug_com_022.html`），表明在容器化部署场景下，本指南与 MindCluster 的 Docker 加固流程**存在上下游依赖**——容器需正确映射 `/dev/dvpp_cmdlist` 后，DVPP 相关 Torchvision 算子才能在 NPU 上正常工作。
- **Torchvision → Torchvision Adapter 插件**：以 `torchvision.ops.nms` 为示例，展示了 Torchvision 上层 API 与 Torchvision Adapter 插件之间的**算子级替换关系**，原文中提到的内部链接信息为"无"。

---

## 【使用方法】

**1. 初始化 CANN 环境变量（原文给出）**

```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```
> 默认以 root 用户安装路径为例，实际以本机 `set_env.sh` 路径为准。

**2. Docker + DVPP 设备映射（原文给出）**

需将宿主机的 `/dev/dvpp_cmdlist` 映射至容器内部，并按照 Docker 安全加固文档设置文件权限。

**3. 启用 NPU 适配（原文给出）**

CUDA/CPU 版本调用方式（原文示例）：
```python
import torch
import torchvision

...
torchvision.ops.nms(boxes, scores, iou_threshold)  # boxes and scores are CPU/CUDA Tensors.
```

NPU 版本调用方式（原文示例）——**仅在原有导入基础上增加 `torchvision_npu`（并按需引入 `torch_npu`）**：
```python
import torch
import torch_npu
import torchvision
import torchvision_npu

...
torchvision.ops.nms(boxes, scores, iou_threshold)  # boxes and scores are NPU Tensors.
```

**4. 配置项 / 命令开关**：原文未涉及具体的配置文件路径、环境变量名、开关参数等额外配置项。
