# Torchvision Adapter插件 快速入门

> 仓 `vision` · 路径 `docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vision/docs/zh/quick_start.md

# Torchvision Adapter 插件快速入门 — 一体化深度解读

## 【定位】
这篇文档解决"如何让用户用最小的代码改动，将原本在 CPU/CUDA 上运行的 Torchvision 算子迁移到昇腾 NPU 上运行"的问题——即 Torchvision Adapter 插件的首次上手引导。

## 【技术要点】

1. **CANN 环境变量初始化**：插件运行前必须先 source 昇腾 CANN 工具链的环境脚本，原文给出默认路径 `/usr/local/Ascend/ascend-toolkit/set_env.sh`，并提示用户应根据实际安装路径替换。

2. **零侵入式 API 调用方式**：插件采用"导入即接管"的设计——**只需新增一行 `import torchvision_npu`**，算子的调用语法（如 `torchvision.ops.nms(boxes, scores, iou_threshold)`）保持完全一致，CUDA/CPU 版本与 NPU 版本共用同一接口签名。

3. **隐式的后端切换机制**：调用方式不变，但底层算子实现通过导入动作被替换——原文示例中，CUDA/CPU 调用时 `boxes` 和 `scores` 为 `CPU/CUDA Tensor`，启用插件后变为 `NPU Tensor`，无需修改任何业务代码。

4. **NPU 版本的依赖链**：在 CUDA/CPU 基础上额外引入 `torch_npu` 和 `torchvision_npu`，构成完整的 NPU 适配导入链：`torch` → `torch_npu` → `torchvision` → `torchvision_npu`。

5. **DVPP 容器化运行要求**：在 Docker 中使用 DVPP（数字视觉预处理）功能时，需要将宿主机的 `/dev/dvpp_cmdlist` 设备文件映射进容器，原文附外链指向《对 Docker 进行安全加固》作为权限说明参考。

6. **默认路径假设**：示例命令以 **root 用户** 安装的默认路径为前提，暗示非 root 安装或自定义路径用户需自行调整 `set_env.sh` 的源路径。

## 【关键机制与数据】

**工作原理（基于原文推断的设计逻辑）**：插件借助 Python 的模块导入副作用机制——`import torchvision_npu` 这一行在被解释器加载时，会以 monkey-patch（运行时替换）的方式将 `torchvision.ops` 子模块中已适配算子的实现覆盖原 CUDA/CPU 版本。因此用户在编写或迁移代码时，**调用入口字符串不变**（例如 `torchvision.ops.nms`），变化的只有两件事：①导入语句多一行；②输入 Tensor 所在设备从 `cpu()`/`cuda()` 变为 `npu()`。

**数据流（以 NMS 为例）**：

- 原文未给出性能数据。
- 原文：CUDA/CPU 版本 — `torch` + `torchvision` → `torchvision.ops.nms(boxes, scores, iou_threshold)`，输入为 CPU/CUDA Tensor。
- 原文：NPU 版本 — 在上述基础上追加 `torch_npu` 和 `torchvision_npu`，输入改为 NPU Tensor，调用入口与参数列表完全一致。

**示例算子**：`torchvision.ops.nms(boxes, scores, iou_threshold)`，其中 `iou_threshold` 是 NMS 算法的 IoU 阈值参数（原文未给出取值范围或默认值）。

## 【表格解读】

**原文无表格**。

## 【公式解读】

**原文无公式**。

## 【关联】

- **CANN 工具链（昇腾 Compute Architecture for Neural Networks）**：`/usr/local/Ascend/ascend-toolkit/set_env.sh` 是 CANN Toolkit 提供的环境初始化脚本，提供驱动、运行时库、算子库等核心依赖，是 Torchvision Adapter 运行的基础设施。
- **`torch_npu`**：昇腾官方 PyTorch 适配插件，为 PyTorch 提供 NPU 张量与设备支持，是 Torchvision Adapter 的下游依赖。
- **DVPP（Digital Vision Pre-Processing）**：昇腾内置的硬件视频/图像预处理加速单元，通过 `/dev/dvpp_cmdlist` 字符设备与驱动通信——这是插件在视觉预处理链路上的潜在加速点，原文通过 Note 提示了容器场景下的设备文件映射要求。
- **外部文档《对 Docker 进行安全加固》**（https://www.hiascend.com/document/detail/zh/mindcluster/730/clustersched/dlug/mxdlug_com_022.html）：原文将其作为 `/dev/dvpp_cmdlist` 设备文件权限配置的参考入口，属于 MindCluster 调度平台的安全加固文档范畴。
- **上游 Torchvision**：`torchvision.ops.nms` 等算子本身由 Torchvision 项目提供，Torchvision Adapter 仅做 NPU 后端实现替换，不修改 Torchvision 上游 API 契约。

## 【使用方法】

**1. 环境变量初始化（任意 NPU 任务启动前必做）**：

```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

> 路径以 root 默认安装为例，需按实际替换。

**2. 插件安装**：原文仅写"安装 Torchvision Adapter 插件之后"，未列出具体的 `pip install` 或 `whl` 安装命令——属于前置依赖，假定读者已完成。

**3. 代码改造（仅增加 1 行 import）**：

- **CUDA/CPU 版本**：

```python
import torch
import torchvision
torchvision.ops.nms(boxes, scores, iou_threshold)  # boxes、scores 为 CPU/CUDA Tensor
```

- **NPU 版本**：

```python
import torch
import torch_npu
import torchvision
import torchvision_npu
torchvision.ops.nms(boxes, scores, iou_threshold)  # boxes、scores 为 NPU Tensor
```

**4. Docker + DVPP 场景的额外配置**：使用 `--device` 或 `-v` 将宿主机的 `/dev/dvpp_cmdlist` 映射进容器，并按外链文档调整文件权限。

**5. 原文未涉及的配置项**：插件版本兼容性矩阵、`boxes`/`scores` 的 dtype/维度约束、`iou_threshold` 取值范围、NMS 算子在 NPU 上的精度模式（fp16/amp）开关等均未在本文档中说明。
