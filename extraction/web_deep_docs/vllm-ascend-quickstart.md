# Quick Start

> 来源 https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/latest/quick_start.html
> 抓取路由 direct-html · 2026-09-02 17:37 · 原文 25861 字符 · 0 图
> MiniMax-M3 七节深读 · ver=v1 · 原文: extraction/web_docs/vllm-ascend-quickstart.md

# vLLM Ascend 快速上手 — 一体化深度解读

## 【定位】

本页面是 vLLM Ascend（昇腾 NPU 上的 vLLM 推理框架）的"快速上手"入门文档，面向**已在装有昇腾硬件的主机上**准备以 Qwen3-0.6B 为例跑通首次离线推理（offline inference）或部署在线服务（online serving）的使用者，覆盖从镜像拉取、容器启动、环境校验到最小可运行示例的全链路步骤。

---

## 【技术要点】

1. **运行环境硬性条件**（原文："Requirements"）：操作系统 Linux；Python `>= 3.10, < 3.13`；需要 Docker；硬件限定为四类昇腾系列（A2 / A3 / 推理系列 300I DUO & 200I Pro / 950DT）。
2. **软件栈组成**：镜像预装经验证的 Python + 昇腾用户态软件栈，原文明确包含 **CANN、NNAL、PyTorch、TorchNPU、vLLM、vLLM Ascend**；A2 / A3 / 950DT 额外含匹配的 **Triton Ascend runtime**，而 **Atlas 300I DUO 与 Atlas 200I Pro 不使用 Triton Ascend**。
3. **镜像默认源与加速镜像**：默认从 `quay.io` 拉取 `quay.io/ascend/vllm-ascend:<TAG>`，可替换为 `m.daocloud.io/quay.io/ascend/vllm-ascend:$TAG` 或 `quay.nju.edu.cn/ascend/vllm-ascend:$TAG`；规则是**只替换 registry 前缀，保留完整原始 tag 后缀**（如 `-a3`、`-310p`、`-950dt`、`-openeuler`）。
4. **按硬件分发的镜像标签**：A2 用 `v0.23.0`（Ubuntu）与 `v0.23.0-openeuler`；A3 用 `v0.23.0-a3` / `v0.23.0-a3-openeuler`；Atlas 300I DUO 用 `v0.23.0-310p` / `v0.23.0-310p-openeuler`；Atlas 200I Pro 同 300I DUO 的 `-310p` tag，但容器启动参数不同；950DT 用 `v0.23.0-a5` / `v0.23.0-a5-openeuler`。
5. **A3 启动特殊性**：A3 采用 **dual-DIE 设计**，必须传入两个昇腾设备节点（如 `/dev/davinci0` 和 `/dev/davinci1`）。
6. **Atlas 200I Pro 启动特殊性**：需附加挂载 `/dev/ascend_manager`、`/dev/user_config`、系统版本/日志/驱动库等若干宿主机文件，需 `--privileged`，且 `--shm-size=10g`（其他硬件用 `1g`），且提示"启动前需确认宿主机路径都存在"。
7. **950DT 启动特殊性**：容器增加 `--net=host`，并额外挂载 `/usr/local/Ascend/driver/tools/hccn_tool`，且**不映射** `-p 8000:8000`（因为 net=host 已暴露端口）。
8. **Atlas 300I DUO / Atlas 200I Pro 推理运行时约束**（原文："Runtime requirements for this hardware path"）：必须使用 `float16`；使用 `FULL_DECODE_ONLY` 模式并限制 graph capture sizes 为 `[1, 2, 4, 8]`；`enable_npugraph_ex` 不支持，必须通过 `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex":false}}'` 关闭。
9. **模型源切换**：若无法稳定访问 Hugging Face，可设 `VLLM_USE_MODELSCOPE=True` 并安装 `modelscope>=1.18.1,<1.38`，或将示例中的模型 ID 替换为本地目录。
10. **在线服务生命周期**：`vllm serve Qwen/Qwen3-0.6B &` 后台启动；停止用 `VLLM_PID=$(pgrep -f "vllm serve"); kill -2 "$VLLM_PID"`（等同于前台 `Ctrl+C`），最后 `Ctrl+D` 退出容器。

---

## 【关键机制与数据】

- **工作原理（原文："Software stack included in the vLLM Ascend image"）**：vLLM Ascend 镜像是一个**预先对齐好版本的 Python + 昇腾用户态栈**，覆盖驱动以上到模型推理的所有层（PyTorch → TorchNPU → CANN/NNAL → vLLM → vLLM Ascend 插件）。A2/A3/950DT 额外含 Triton Ascend runtime，说明这些芯片支持 Triton 算子调度路径；而 300I DUO / 200I Pro 走的是非 Triton 路径，因此 `enable_npugraph_ex`（与 Triton 算子编译/捕获相关）被显式禁用。
- **配置语义**：Atlas 300I DUO / 200I Pro 的 `cudagraph_mode="FULL_DECODE_ONLY"` 表示**仅在 decode 阶段做 CUDA Graph 捕获**，规避 prefill 阶段的图捕获兼容性问题；`cudagraph_capture_sizes=[1, 2, 4, 8]` 限定可被捕获的 batch size 集合；`max_num_seqs=8` 把并发上限设为 8（与最大 graph capture size 对齐）。
- **版本差异**：原文给出 `v0.23.0` 系列 tag，并通过 `-a3`、`-310p`、`-a5`、`-openeuler` 后缀区分硬件/OS 组合；A2 默认 tag 无后缀，A3 后缀 `-a3`，Atlas 推理系列后缀 `-310p`，950DT 后缀 `-a5`，openEuler 镜像一律在末尾追加 `-openeuler`。
- **A3 双设备挂载语义**（原文："A3 container startup requirements"）：A3 dual-DIE 必须同时 `--device "$DEVICE0"` 与 `--device "$DEVICE1"`，与 A2/A3/300I/200I 单设备的 `DEVICE=/dev/davinci0` 形式相对。
- **200I Pro 容器启动前置条件**（原文："Atlas 200I Pro container startup requirements"）："Before starting the container, make sure that all host paths mounted by the command below exist." —— 该型号必须在宿主机上保证所挂载的系统文件/库文件全部存在，否则容器启动会失败。
- **平台插件激活机制**（原文日志）：`Available plugins for group vllm.platform_plugins: - ascend -> vllm_ascend:register`，然后 `Platform plugin ascend is activated`——vLLM 通过 `vllm.platform_plugins` 注册机制发现 `vllm_ascend`，并可用 `VLLM_PLUGINS` 控制加载哪些插件。

---

## 【表格解读】

原文仅有一张硬件支持表，逐字还原如下：

| Type | Common products |
| --- | --- |
| Atlas A2 series products | Atlas 800T A2, Atlas 900 A2 PoD, Atlas 200T A2 Box16, Atlas 300T A2, Atlas 800I A2, and others |
| Atlas A3 series products | Atlas 800T A3, Atlas 900 A3 SuperPoD, Atlas 9000 A3 SuperPoD, Atlas 800I A3, and others |
| Atlas inference series products | Atlas 300I DUO and Atlas 200I Pro |
| Atlas 950DT series products | Atlas 950DT |

**逐类解读**：

- **Atlas A2 系列**：训练/推理通用的高端卡族，含服务器形态（800T A2 / 900 A2 PoD）、边缘盒子（200T A2 Box16）、工作站卡（300T A2）、推理设备（800I A2）；对应文档章节使用镜像 `v0.23.0`、单设备 `/dev/davinci0`、含 Triton Ascend runtime。
- **Atlas A3 系列**：相比 A2 更新一代的卡族，含 800T A3 服务器、900 A3 SuperPoD / 9000 A3 SuperPoD 超节点、800I A3 推理设备；**特殊点是 dual-DIE 设计**，容器启动需挂载两个 davinci 设备节点，对应镜像 `v0.23.0-a3`，含 Triton Ascend runtime。
- **Atlas 推理系列（300I DUO & 200I Pro）**：定位偏向边缘/推理卡的设备族，型号较少（仅 300I DUO 和 200I Pro 两个具体型号）；**特殊点是两型号使用同一镜像 tag `-310p`，但容器挂载差异很大**——300I DUO 走类似 A2 的轻量挂载（shm 1g、非 privileged），200I Pro 必须 `--privileged`、`--shm-size=10g`，且需要挂载大量宿主系统文件（sys_version.conf、slog 配置、libmmpa、libcrypto.so.1.1、libstackcore、libtensorflow 等）；二者**均不使用 Triton Ascend runtime**，因此推理配置必须用 `FULL_DECODE_ONLY` 并禁用 `enable_npugraph_ex`。
- **Atlas 950DT 系列**：表中只列出 Atlas 950DT 一个具体型号，对应镜像 `v0.23.0-a5`；容器启动时启用 `--net=host` 并挂载 `hccn_tool`，端口不再走 `-p 8000:8000`，含 Triton Ascend runtime。

除硬件支持表外，原文其余信息以命令行 / Python 代码块形式呈现（见【使用方法】），未出现额外的参数表或环境变量表。

---

## 【公式解读】

原文无 LaTeX 或伪代码公式。涉及可被"公式化"的只有几处 JSON 配置字面量，原文逐字给出：

- `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex":false}}'`
- `--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY","cudagraph_capture_sizes":[1,2,4,8]}'`

符号语义说明（仅就字面量含义解释，不引入原文未给的概念）：
- `ascend_compilation_config.enable_npugraph_ex` —— 控制是否启用 NPU Graph 扩展（ex）模式；在 300I DUO / 200I Pro 上被强制设为 `false`。
- `cudagraph_mode` 取值 `"FULL_DECODE_ONLY"` —— 仅在 decode 阶段启用 CUDA Graph 捕获。
- `cudagraph_capture_sizes` 取值 `[1, 2, 4, 8]` —— 显式枚举允许捕获的 batch size 集合，最大值为 8，对应 `max_num_seqs=8`。

---

## 【关联】

- 链接 **[Installation Guide > Hardware and software stack](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/latest/installation.html#installation-hardware-software-stack)** —— 提供与 Quick Start 中各 tag 对应的**已验证软件栈精确版本**，是 Quick Start "Requirements" 小节的延伸。
- 链接 **[Docker installation guide](https://docs.docker.com/get-started/get-docker/)** —— Quick Start 假设宿主机已装 Docker，若未装则跳转此处。
- 链接 **[Supported Models](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/user_guide/support_matrix/supported_models.html)** —— 给出 vLLM Ascend 已验证可推理的模型矩阵，是把 Qwen3-0.6B 替换为其它模型时的入口。
- 链接 **[Model Tutorials](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/tutorials/models/index.html)** —— 提供具体模型的部署教程，承接 Quick Start 的最小示例。
- 链接 **[Installation Guide > Set up the software environment](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/latest/installation.html#installation-software-environment)** —— 提供 pip / CANN / 源码三种非容器安装路径，与 Quick Start 的容器路径并列。
- 链接 **[Feature Tutorials](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/tutorials/features/index.html)** —— 介绍分布式部署和高级特性，是 Quick Start 单机示例之后的进阶入口。
- 链接 **[FAQ](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/faqs.html)** —— 排查常见部署问题，对应 Quick Start "Verify the container environment" / 服务启动失败场景。

---

## 【使用方法】

下列命令/配置均直接源自原文，可照抄执行。

### 1. 镜像加速（适用于所有硬件型号）

```bash
# Replace with tag you want to pull
TAG=v0.23.0
# use
docker pull m.daocloud.io/quay.io/ascend/vllm-ascend:$TAG
# or
docker pull quay.nju.edu.cn/ascend/vllm-ascend:$TAG
```

### 2. 各硬件拉取镜像（Ubuntu / openEuler 二选一）

**A2：**
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0
docker pull "$IMAGE"
```
或
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-openeuler
docker pull "$IMAGE"
```

**A3：**
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a3
docker pull "$IMAGE"
```
或
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a3-openeuler
docker pull "$IMAGE"
```

**Atlas 300I DUO：**
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-310p
docker pull "$IMAGE"
```
或
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-310p-openeuler
docker pull "$IMAGE"
```

**Atlas 200I Pro：** 同上 `v0.23.0-310p` tag，但启动命令见下。

**950DT：**
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a5
docker pull "$IMAGE"
```
或
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a5-openeuler
docker pull "$IMAGE"
```

### 3. 容器启动

**A2 / 300I DUO / 200I Pro（单设备，Ubuntu 示例，200I Pro 见下方专用）：**
```bash
export DEVICE=/dev/davinci0
export MODEL_CACHE="${HOME}/.cache"

mkdir -p "$MODEL_CACHE"

docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --device "$DEVICE" \
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

**A3（双设备，Ubuntu 示例）：**
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

**Atlas 200I Pro（Ubuntu 示例，原文整段照抄）：**
```bash
export MODEL_CACHE="${HOME}/.cache"

mkdir -p "$MODEL_CACHE"

docker run --rm \
    --privileged \
    --name vllm-ascend \
    --shm-size=10g \
    --device=/dev/davinci0:/dev/davinci0 \
    --device=/dev/davinci_manager \
    --device=/dev/ascend_manager \
    --device=/dev/user_config \
    -v /etc/sys_version.conf:/etc/sys_version.conf \
    -v /etc/ld.so.conf.d/mind_so.conf:/etc/ld.so.conf.d/mind_so.conf \
    -v /etc/hdcBasic.cfg:/etc/hdcBasic.cfg \
    -v /var/dmp_daemon:/var/dmp_daemon \
    -v /usr/lib64/libmmpa.so:/usr/lib64/libmmpa.so \
    -v /usr/lib64/libcrypto.so.1.1:/usr/lib64/libcrypto.so.1.1 \
    -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
    -v /usr/lib64/libstackcore.so:/usr/lib64/libstackcore.so \
    -v /usr/lib/aarch64-linux-gnu/libyaml-0.so.2:/usr/lib64/libyaml-0.so.2 \
    -v /etc/slog.conf:/etc/slog.conf \
    -v /var/slogd:/var/slogd \
    -v /usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64 \
    -v /usr/lib64/libtensorflow.so:/usr/lib64/libtensorflow.so \
    -v "$MODEL_CACHE:/root/.cache" \
    -p 8000:8000 \
    -it "$IMAGE" bash
```

**950DT（Ubuntu 示例，原文未映射端口，使用 `--net=host`）：**
```bash
export MODEL_CACHE="${HOME}/.cache"

mkdir -p "$MODEL_CACHE"

docker run --rm \
    --name vllm-ascend \
    --net=host \
    --shm-size=1g \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v "$MODEL_CACHE:/root/.cache" \
    -it "$IMAGE" bash
```

### 4. 容器环境校验（所有硬件通用）

```bash
npu-smi info

python3 - <<'PY'
import torch
import vllm
import vllm_ascend

assert torch.npu.is_available(), "No available Ascend NPU detected in the container"
print("vLLM Ascend environment: OK")
PY
```
成功标志：输出包含 `vLLM Ascend environment: OK`。

### 5. 模型源切换（若 Hugging Face 受限）

```bash
export VLLM_USE_MODELSCOPE=True
pip install "modelscope>=1.18.1,<1.38"
```

### 6. 离线推理示例 — A2 / A3 / 950DT（容器内 `example.py`）

```python
from vllm import LLM, SamplingParams

prompts = [
    "Hello, my name is",
    "The future of AI is",
]

sampling_params = SamplingParams(
    temperature=0.0,
    max_tokens=32,
)

llm = LLM(model="Qwen/Qwen3-0.6B")
outputs = llm.generate(prompts, sampling_params)

assert len(outputs) == len(prompts)

for output in outputs:
    generated_text = output.outputs[0].text
    assert generated_text.strip()
    print(f"Prompt: {output.prompt!r}, Generated text: {generated_text!r}")
```

```bash
python3 example.py
```

### 7. 离线推理示例 — Atlas 300I DUO / Atlas 200I Pro（容器内 `example.py`）

```python
from vllm import LLM, SamplingParams

MODEL = "Qwen/Qwen3-0.6B"

prompts = [
    "Hello, my name is",
    "The future of AI is",
]

llm = LLM(
    model=MODEL,
    dtype="float16",
    max_num_seqs=8,
    compilation_config={
        "cudagraph_mode": "FULL_DECODE_ONLY",
        "cudagraph_capture_sizes": [1, 2, 4, 8],
    },
    additional_config={
        "ascend_compilation_config": {
            "enable_npugraph_ex": False,
        },
    },
)

sampling_params = SamplingParams(
    temperature=0.0,
    max_tokens=32,
)

outputs = llm.generate(prompts, sampling_params)

assert len(outputs) == len(prompts)

for output in outputs:
    generated_text = output.outputs[0].text
    assert generated_text.strip()
    print(f"Prompt: {output.prompt!r}, Generated text: {generated_text!r}")
```

```bash
python3 example.py
```

### 8. 在线服务 — A2 / A3 / 950DT

```bash
vllm serve Qwen/Qwen3-0.6B &
```

启动成功标志（原文日志）：
```
INFO:     Started server process [3594]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**查询模型列表：**
```bash
curl http://localhost:8000/v1/models | python3 -m json.tool
```

**发送 prompt：**
```bash
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen3-0.6B",
        "prompt": "Beijing is a",
        "max_completion_tokens": 5,
        "temperature": 0
    }' | python3 -m json.tool
```

**优雅停止服务：**
```bash
VLLM_PID=$(pgrep -f "vllm serve")
kill -2 "$VLLM_PID"
```

最后在容器终端 `Ctrl+D` 退出容器。

### 9. 在线服务 — Atlas 300I DUO / Atlas 200I Pro

```bash
vllm serve Qwen/Qwen3-0.6B \
    --dtype float16 \
    --max-num-seqs 8 \
    --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY","cudagraph_capture_sizes":[1,2,4,8]}' \
    --additional-config '{"ascend_compilation_config":{"enable_npugraph_ex":false}}' &
```

查询与停止命令同 A2/A3/950DT 路径。
