# 进入项目根目录

> 仓 `slime-ascend` · 路径 `docs/ascend_tutorial/get_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/slime-ascend/docs/ascend_tutorial/get_started/quick_start.md

# 「slime-ascend / docs/ascend_tutorial/get_started/quick_start.md」一体化深度解读

> 原文起首含 `﻿`（UTF-8 BOM 标记），表明源文件由 Windows 工具保存，下文解读以 BOM 去除后的正文为准。

---

## 【定位】

本文档是 **slime-ascend 项目在华为昇腾 NPU 上的“一小时快速上手”入门指南**，向开发者说明：使用何种 Atlas 硬件、需要哪些组件版本（CANN、torch/torch_npu、SGLang、Megatron 栈等），以及如何通过 Docker 或本地脚本两种方式完成环境搭建，从而启动 GRPO 训练并衔接后续模型示例文档。

---

## 【技术要点】

1. **硬件覆盖范围**：仅正式验证 **Atlas 800T A2** 与 **Atlas 800T A3** 两种昇腾硬件；**A5 支持度暂未验证，待 Q3 正式更新**（原文以 `>` blockquote 强调）。
2. **CANN 版本要求**：推荐 **CANN 9.0.0 或更高版本**；Py3.11 链路使用 CANN 9.0.0，Py3.12 链路使用 **CANN 9.1.0**。
3. **NPU 上 Megatron-LM 适配方案的切换**：本版本“已使用 **MegatronAdaptor** 和 **TransformerEngineNPU** 代替 **MindSpeed** 进行 NPU 上 Megatron-LM 的适配支持”，这是相对其他同类项目的关键架构差异。
4. **两条部署路径**：
   - **Docker（推荐）**：以 `Dockerfile.a3.ubuntu22.04.cann90.latest` 为模板构建镜像，并以三条 `--device=` 设备映射（`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`）暴露 NPU。
   - **本地一键安装**：`quick_install.sh` 自动完成 SGLang 源码安装、torch/torch_npu/triton_ascend/sgl-kernel-npu、mbridge、Megatron-Bridge、Megatron-LM、MegatronAdaptor+TransformerEngineNPU、slime-ascend 本体以及全部 NPU 补丁的部署。
5. **训练算法与模型矩阵（均为 Preview）**：GRPO ×（GLM-4.7-Flash、Qwen3-8B、Qwen3-VL-8B、Qwen3.5-9B），并未给出 Released 状态条目。
6. **关键调优参数提示**：显存不足时调整 `--sglang-mem-fraction-static` 参数，建议区间 **0.6–0.8**；HCCL 通信异常时关注 `HCCL_HOST_SOCKET_PORT_RANGE` / `HCCL_NPU_SOCKET_PORT_RANGE` 端口段。

---

## 【关键机制与数据】

本文档为**面向新手的快速上手文档**，不涉及性能数据、吞吐量或基准测试结果，其“关键机制”集中在**部署/环境**层面：

- **数据流（安装流程）**：conda 创建 `slime-ascend` 环境 → 设置 `CANN_INSTALL_PATH=/usr/local/Ascend`、`NPU_DEVICE=A3` → `source ascend-toolkit/set_env.sh` 与 `nnal/atb/set_env.sh` 加载 CANN 环境 → 执行 `quick_install.sh`，该脚本按 8 步顺序安装组件并应用 NPU 补丁（原文明确列出 1–8 步）。
- **Docker 数据流**：构建阶段仅给出 `docker build` 命令；运行阶段通过 `-v` 将宿主机的 `/usr/local/Ascend/driver`、`/usr/local/Ascend/add-ons` 与当前工作目录挂入容器，工作目录设为 `/workspace`，从而在容器内复用宿主机驱动并保持代码同步。
- **设备发现机制**：原文将 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 三个字符设备直通进容器，这是昇腾 NPU 在 Docker 内的标准设备暴露方式；运行时则依赖 `ASCEND_RT_VISIBLE_DEVICES` 与 `npu-smi info` 进行可见性与健康验证（原文只列命令名，未给出具体输出）。
- **Megatron 栈适配机制**：用 **MegatronAdaptor + TransformerEngineNPU** 替代 MindSpeed 完成 Megatron-LM 在 NPU 上的适配，结合 **Megatron-Bridge (dev_rl)**、**mbridge (89eb1088)** 进行桥接，二者版本号（A2/A3 同列）锁死，保证训练与推理栈一致。

---

## 【表格解读】

原文共 **3 张关键表格**，逐字还原并逐行解读如下：

### 表 1：组件版本对照表（Python 3.11 链路）

| 组件 | A2 版本 | A3 版本 |
| --- | --- | --- |
| 基础镜像 | Ubuntu 22.04 | Ubuntu 22.04 |
| Python | 3.11 | 3.11 |
| CANN | 9.0.0 | 9.0.0 |
| torch | 2.10.0 | 2.10.0 |
| torch_npu | 2.10.0 | 2.10.0 |
| torchvision | 0.25.0 | 0.25.0 |
| Megatron-LM | 1dcf0dafa | 1dcf0dafa |
| Megatron-Bridge | dev_rl | dev_rl |
| triton-ascend | 3.2.1 | 3.2.1 |
| mbridge | 89eb1088 | 89eb1088 |
| SGLang | v0.5.13 | v0.5.13 |
| sgl-kernel-npu | 2026.6.1 | 2026.6.1 |
| nvidia-modelopt | >=0.37.0 | >=0.37.0 |
| Slime | v0.3.0 | v0.3.0 |

**解读**：A2/A3 在 Py3.11 链路下所有组件版本**完全一致**，使用 CANN 9.0.0、torch/torch_npu 2.10.0、Megatron-LM 锁到 commit `1dcf0dafa`、Megatron-Bridge 取 `dev_rl` 分支（带 RL 适配），sgl-kernel-npu 版本为 `2026.6.1`，nvidia-modelopt 最低 `>=0.37.0`。

### 表 2：组件版本对照表（Python 3.12 链路）

| 组件 | A2 版本 | A3 版本 |
| --- | --- | --- |
| 基础镜像 | Ubuntu 22.04 | Ubuntu 22.04 |
| Python | 3.12 | 3.12 |
| CANN | 9.1.0 | 9.1.0 |
| torch | 2.10.0 | 2.10.0 |
| torch_npu | 2.10.0 | 2.10.0 |
| torchvision | 0.25.0 | 0.25.0 |
| Megatron-LM | 1dcf0dafa | 1dcf0dafa |
| Megatron-Bridge | dev_rl | dev_rl |
| triton-ascend | 3.2.1 | 3.2.1 |
| mbridge | 89eb1088 | 89eb1088 |
| SGLang | v0.5.13 | v0.5.13 |
| sgl-kernel-npu | 2026.8.17 | 2026.8.17 |
| nvidia-modelopt | >=0.37.0 | >=0.37.0 |
| Slime | v0.3.0 | v0.3.0 |

**解读**：相比 Py3.11 链路，Py3.12 链路只升了 **CANN 9.0.0 → 9.1.0** 与 **sgl-kernel-npu 2026.6.1 → 2026.8.17**，其余组件版本（包括 torch/torch_npu、Megatron-LM、mbridge、Slime）保持一致；A2/A3 同样无差异。

### 表 3：训练算法 × 模型 × 发布状态

| 训练算法 | 支持模型 | 发布状态 |
| --- | --- | --- |
| GRPO | [GLM-4.7-Flash](../examples/glm4.7-30B-A3B.md) | Preview |
| GRPO | [Qwen3-8B](../examples/qwen3-8B.md) <br> [Qwen3-VL-8B](../examples/qwen3-vl-8B.md) <br> [Qwen3.5-9B](../examples/qwen3.5-9B.md) | Preview |

**解读**：当前仅开放 **GRPO** 一种 RL 算法；模型端共 4 个（GLM-4.7-Flash、Qwen3-8B、Qwen3-VL-8B、Qwen3.5-9B），**全部处于 Preview 预览状态**，尚无任何 Released 正式发布条目。表格底部以注释明确 Preview 与 Released 的语义差别。

---

## 【公式解读】

**原文无公式。**

（本文档未出现任何 LaTeX 数学表达式或伪代码算法公式，其内容全部为自然语言 + 命令行 + 表格。）

---

## 【关联】

依据原文给出的内部链接，可梳理如下上下游关系：

- **训练示例文档（下游/正文主体）**
  - [GLM-4.7-Flash](../examples/glm4.7-30B-A3B.md)：作为 NPU 训练脚本示例被明确点名（"参照 `glm4.7-30B-A3B.md`"），是本文训练章节的承接对象。
  - [Qwen3-8B](../examples/qwen3-8B.md)、[Qwen3-VL-8B](../examples/qwen3-vl-8B.md)、[Qwen3.5-9B](../examples/qwen3.5-9B.md)：与 GLM-4.7-Flash 同列于表 3，覆盖纯文本与多模态两种 Qwen 系列。
- **环境基础设施**
  - [Dockerfile 构建指南（A3 v0.3.0）](../../../docker/npu_docker/v0.3.0/dockerfile_build_guidance.md)：方法一（Docker）的实现细节入口，与本文档的 `docker build` / `docker run` 命令对应。
  - [一键安装脚本](../../../scripts/ascend_script/quick_install.sh)：方法二（本地安装）的实现细节入口，对应 8 步安装流程。
- **排错/支持**
  - [Q&A 文档（中文）](../../zh/get_started/qa.md)：本文末尾显式指向"更多常见问题请参考 Q&A"，承担排错补完角色，与本文"常见问题排查"小节互补。

---

## 【使用方法】

> 以下命令与配置均**逐字取自原文**，未做改写。

### 1. Docker 方式（推荐）

```bash
# 镜像构建
cd {slime-ascend-root-path}
docker build -f Dockerfile.a3.ubuntu22.04.cann90.latest \
  -t slime-ascend:9.0.0-a3-ubuntu22.04-py3.11-latest .

# 启动容器（以 A3 为例）
docker run -it --rm \
  --device=/dev/davinci_manager \
  --device=/dev/devmm_svm \
  --device=/dev/hisi_hdc \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/Ascend/add-ons:/usr/local/Ascend/add-ons \
  -v $(pwd):/workspace \
  -w /workspace \
  slime-ascend:9.0.0-a3-ubuntu22.04-py3.11-latest
```

**关键开关/参数**：
- `-t slime-ascend:9.0.0-a3-ubuntu22.04-py3.11-latest` —— 镜像名内嵌 CANN、硬件、OS、Python 版本四个维度。
- 三条 `--device=` 直通设备：`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`（昇腾 Docker 标准三元组）。
- `-v` 挂载：`driver` 与 `add-ons` 必须来自宿主 `/usr/local/Ascend`，保证容器复用宿主驱动。

### 2. 本地安装脚本方式

```bash
conda create -n slime-ascend python=3.11
conda activate slime-ascend
git clone https://gitcode.com/Ascend/slime-ascend.git
export CANN_INSTALL_PATH=/usr/local/Ascend
export NPU_DEVICE=A3
source ${CANN_INSTALL_PATH}/ascend-toolkit/set_env.sh
source ${CANN_INSTALL_PATH}/nnal/atb/set_env.sh
bash slime-ascend/scripts/ascend_script/quick_install.sh
```

**关键配置项**：
- `CANN_INSTALL_PATH=/usr/local/Ascend`（需根据实际修改）。
- `NPU_DEVICE=A3`（A2 需替换为 `A2`）。
- `quick_install.sh` 内部一次性完成 SGLang 源码、torch/torch_npu、triton_ascend、sgl-kernel-npu、mbridge、Megatron-Bridge、Megatron-LM、MegatronAdaptor+TransformerEngineNPU、slime-ascend 与全部 NPU 补丁。

### 3. 训练脚本启用

文档未在本路径下给出可直接执行的训练命令，而是**指向**具体模型的训练脚本文档：

> "我们提供了 GLM-4.7 在 NPU 上的训练脚本示例，参照 [glm4.7-30B-A3B.md](../examples/glm4.7-30B-A3B.md)。"

也就是说，**训练启动的具体命令/参数配置不在本文档范围内**，需要跳转至 `examples/` 下的各模型示例文档查看。

### 4. 常见故障排查命令/参数

- `source ${CANN_INSTALL_PATH}/ascend-toolkit/set_env.sh` —— 加载 CANN 环境。
- 检查 `ASCEND_TOOLKIT_HOME` —— 验证环境变量。
- 检查 `ASCEND_RT_VISIBLE_DEVICES` —— 控制 NPU 可见性。
- `npu-smi info` —— 查看 NPU 设备状态。
- `--sglang-mem-fraction-static`（建议 **0.6–0.8**）—— 显存不足时调整。
- `HCCL_HOST_SOCKET_PORT_RANGE` / `HCCL_NPU_SOCKET_PORT_RANGE` —— 分布式通信端口范围设置。

> 提示：本文末尾明确将更完整的排错指引指向 [Q&A](../../zh/get_started/qa.md)，本文未涉及的故障需在该文档查阅。
