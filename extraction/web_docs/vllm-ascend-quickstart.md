# Quick Start

This guide uses Qwen3-0.6B as an example to help you run your first offline inference workload or deploy an online service on a prepared Ascend host using a prebuilt vLLM Ascend container.

## Requirements

* Operating system: Linux
* Python: >= 3.10, < 3.13
* Docker
* Supported hardware:

| Type | Common products |
| --- | --- |
| Atlas A2 series products | Atlas 800T A2, Atlas 900 A2 PoD, Atlas 200T A2 Box16, Atlas 300T A2, Atlas 800I A2, and others |
| Atlas A3 series products | Atlas 800T A3, Atlas 900 A3 SuperPoD, Atlas 9000 A3 SuperPoD, Atlas 800I A3, and others |
| Atlas inference series products | Atlas 300I DUO and Atlas 200I Pro |
| Atlas 950DT series products | Atlas 950DT |

Software stack included in the vLLM Ascend image

The prebuilt image includes a validated Python and Ascend user-space software stack, including CANN, NNAL, PyTorch, TorchNPU, vLLM, and vLLM Ascend.

A2, A3, and 950DT images also include the matching Triton Ascend runtime. Atlas 300I DUO and Atlas 200I Pro do not use Triton Ascend.

For the exact validated versions, see [Installation Guide > Hardware and software stack](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/latest/installation.html#installation-hardware-software-stack).

## Installation

Before using containers, make sure Docker is installed on your system. If Docker is not installed, please refer to the [Docker installation guide](https://docs.docker.com/get-started/get-docker/) for installation instructions.

A2A3Atlas 300I DUOAtlas 200I Pro950DT

#### Pull the image

If image downloads are slow

vLLM Ascend images are downloaded from `quay.io` by default. If direct access is slow, use one of the following registry mirrors to accelerate the download.

For example, the original image address is:

```
quay.io/ascend/vllm-ascend:<TAG>
```

You can replace it with:

```
# Replace with tag you want to pull
TAG=v0.23.0
# use
docker pull m.daocloud.io/quay.io/ascend/vllm-ascend:$TAG
# or
docker pull quay.nju.edu.cn/ascend/vllm-ascend:$TAG
```

Replace only the registry prefix and preserve the complete original image tag, including suffixes such as `-a3`, `-310p`, `-950dt`, and `-openeuler`.

UbuntuopenEuler

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0
docker pull "$IMAGE"
```

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-openeuler
docker pull "$IMAGE"
```

#### Start the container

UbuntuopenEuler

```
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

```
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

#### Verify the container environment

Run the following commands in the container. The container is ready when the output includes `vLLM Ascend environment: OK`.

```
npu-smi info

python3 - <<'PY'
import torch
import vllm
import vllm_ascend

assert torch.npu.is_available(), "No available Ascend NPU detected in the container"
print("vLLM Ascend environment: OK")
PY
```

#### Pull the image

If image downloads are slow

vLLM Ascend images are downloaded from `quay.io` by default. If direct access is slow, use one of the following registry mirrors to accelerate the download.

For example, the original image address is:

```
quay.io/ascend/vllm-ascend:<TAG>
```

You can replace it with:

```
# Replace with tag you want to pull
TAG=v0.23.0
# use
docker pull m.daocloud.io/quay.io/ascend/vllm-ascend:$TAG
# or
docker pull quay.nju.edu.cn/ascend/vllm-ascend:$TAG
```

Replace only the registry prefix and preserve the complete original image tag, including suffixes such as `-a3`, `-310p`, `-950dt`, and `-openeuler`.

UbuntuopenEuler

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a3
docker pull "$IMAGE"
```

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a3-openeuler
docker pull "$IMAGE"
```

#### Start the container

A3 container startup requirements

A3 uses a dual-DIE design and requires two Ascend device nodes, such as `/dev/davinci0` and `/dev/davinci1`.

UbuntuopenEuler

```
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

```
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

#### Verify the container environment

Run the following commands in the container. The container is ready when the output includes `vLLM Ascend environment: OK`.

```
npu-smi info

python3 - <<'PY'
import torch
import vllm
import vllm_ascend

assert torch.npu.is_available(), "No available Ascend NPU detected in the container"
print("vLLM Ascend environment: OK")
PY
```

#### Pull the image

If image downloads are slow

vLLM Ascend images are downloaded from `quay.io` by default. If direct access is slow, use one of the following registry mirrors to accelerate the download.

For example, the original image address is:

```
quay.io/ascend/vllm-ascend:<TAG>
```

You can replace it with:

```
# Replace with tag you want to pull
TAG=v0.23.0
# use
docker pull m.daocloud.io/quay.io/ascend/vllm-ascend:$TAG
# or
docker pull quay.nju.edu.cn/ascend/vllm-ascend:$TAG
```

Replace only the registry prefix and preserve the complete original image tag, including suffixes such as `-a3`, `-310p`, `-950dt`, and `-openeuler`.

UbuntuopenEuler

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-310p
docker pull "$IMAGE"
```

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-310p-openeuler
docker pull "$IMAGE"
```

#### Start the container

UbuntuopenEuler

```
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

```
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

#### Verify the container environment

Run the following commands in the container. The container is ready when the output includes `vLLM Ascend environment: OK`.

```
npu-smi info

python3 - <<'PY'
import torch
import vllm
import vllm_ascend

assert torch.npu.is_available(), "No available Ascend NPU detected in the container"
print("vLLM Ascend environment: OK")
PY
```

#### Pull the image

If image downloads are slow

vLLM Ascend images are downloaded from `quay.io` by default. If direct access is slow, use one of the following registry mirrors to accelerate the download.

For example, the original image address is:

```
quay.io/ascend/vllm-ascend:<TAG>
```

You can replace it with:

```
# Replace with tag you want to pull
TAG=v0.23.0
# use
docker pull m.daocloud.io/quay.io/ascend/vllm-ascend:$TAG
# or
docker pull quay.nju.edu.cn/ascend/vllm-ascend:$TAG
```

Replace only the registry prefix and preserve the complete original image tag, including suffixes such as `-a3`, `-310p`, `-950dt`, and `-openeuler`.

UbuntuopenEuler

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-310p
docker pull "$IMAGE"
```

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-310p-openeuler
docker pull "$IMAGE"
```

#### Start the container

Atlas 200I Pro container startup requirements

Atlas 200I Pro requires additional device nodes, driver libraries, and host configuration files. Before starting the container, make sure that all host paths mounted by the command below exist.

UbuntuopenEuler

```
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

```
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
    -v /usr/lib64/libsemanage.so.2:/usr/lib64/libsemanage.so.2 \
    -v /usr/lib64/libmmpa.so:/usr/lib64/libmmpa.so \
    -v /usr/lib64/libcrypto.so.1.1:/usr/lib64/libcrypto.so.1.1 \
    -v /usr/lib64/libyaml-0.so.2.0.9:/usr/lib64/libyaml-0.so.2 \
    -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
    -v /usr/lib64/libstackcore.so:/usr/lib64/libstackcore.so \
    -v /etc/slog.conf:/etc/slog.conf \
    -v /var/slogd:/var/slogd \
    -v /usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64 \
    -v /usr/lib64/libtensorflow.so:/usr/lib64/libtensorflow.so \
    -v "$MODEL_CACHE:/root/.cache" \
    -p 8000:8000 \
    -it "$IMAGE" bash
```

#### Verify the container environment

Run the following commands in the container. The container is ready when the output includes `vLLM Ascend environment: OK`.

```
npu-smi info

python3 - <<'PY'
import torch
import vllm
import vllm_ascend

assert torch.npu.is_available(), "No available Ascend NPU detected in the container"
print("vLLM Ascend environment: OK")
PY
```

#### Pull the image

If image downloads are slow

vLLM Ascend images are downloaded from `quay.io` by default. If direct access is slow, use one of the following registry mirrors to accelerate the download.

For example, the original image address is:

```
quay.io/ascend/vllm-ascend:<TAG>
```

You can replace it with:

```
# Replace with tag you want to pull
TAG=v0.23.0
# use
docker pull m.daocloud.io/quay.io/ascend/vllm-ascend:$TAG
# or
docker pull quay.nju.edu.cn/ascend/vllm-ascend:$TAG
```

Replace only the registry prefix and preserve the complete original image tag, including suffixes such as `-a3`, `-310p`, `-950dt`, and `-openeuler`.

UbuntuopenEuler

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a5
docker pull "$IMAGE"
```

```
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a5-openeuler
docker pull "$IMAGE"
```

#### Start the container

UbuntuopenEuler

```
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

```
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

#### Verify the container environment

Run the following commands in the container. The container is ready when the output includes `vLLM Ascend environment: OK`.

```
npu-smi info

python3 - <<'PY'
import torch
import vllm
import vllm_ascend

assert torch.npu.is_available(), "No available Ascend NPU detected in the container"
print("vLLM Ascend environment: OK")
PY
```

## Inference

The following sections provide offline inference and online serving examples. Choose the method you need to get started.

If Hugging Face access is restricted

If your environment cannot reliably access Hugging Face, model downloads may fail due to connection timeouts, DNS errors, or other network issues. You can switch to ModelScope:

```
export VLLM_USE_MODELSCOPE=True
pip install "modelscope>=1.18.1,<1.38"
```

If the model has already been downloaded locally, replace the model ID in the examples below with the local directory. You do not need to set this environment variable.

### Offline inference

A2 / A3 / 950DTAtlas 300I DUO / Atlas 200I Pro

The following Qwen3-0.6B example has been validated using the default model loading configuration.

In the container terminal, create `example.py` with the following code:

```
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

Run the example:

```
python3 example.py
```

The following output shows that vLLM has successfully detected the Ascend platform:

```
INFO 05-27 11:40:38 [__init__.py:44] Available plugins for group vllm.platform_plugins:
INFO 05-27 11:40:38 [__init__.py:46] - ascend -> vllm_ascend:register
INFO 05-27 11:40:38 [__init__.py:49] All plugins in this group will be loaded. Set `VLLM_PLUGINS` to control which plugins to load.
INFO 05-27 11:40:38 [__init__.py:238] Platform plugin ascend is activated
```

The following output shows the generated results:

```
Prompt: 'Hello, my name is', Generated text: ' Lucy and I am an 8 year old who loves to draw and write stories'
Prompt: 'The future of AI is', Generated text: ' a topic that is being discussed in various contexts. In the business world, AI'
```

The following messages show the process exiting after offline inference and do not affect the inference results:

```
(EngineCore pid=970) INFO 05-12 11:36:00 [core.py:1201] Shutdown initiated (timeout=0)
(EngineCore pid=970) INFO 05-12 11:36:00 [core.py:1224] Shutdown complete
ERROR 05-12 11:36:01 [core_client.py:704] Engine core proc EngineCore died unexpectedly, shutting down client.
sys:1: DeprecationWarning: builtin type swigvarlink has no __module__ attribute
```

The following Qwen3-0.6B example has been validated on Atlas 300I DUO and Atlas 200I Pro.

Runtime requirements for this hardware path

* Use `float16`.
* Use `FULL_DECODE_ONLY` and limit the graph capture sizes.
* `enable_npugraph_ex` is not supported. Set `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex":false}}'`.

In the container terminal, create `example.py` with the following code:

```
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

Run the example:

```
python3 example.py
```

The following output shows that vLLM has successfully detected the Ascend platform:

```
INFO 05-27 11:40:38 [__init__.py:44] Available plugins for group vllm.platform_plugins:
INFO 05-27 11:40:38 [__init__.py:46] - ascend -> vllm_ascend:register
INFO 05-27 11:40:38 [__init__.py:49] All plugins in this group will be loaded. Set `VLLM_PLUGINS` to control which plugins to load.
INFO 05-27 11:40:38 [__init__.py:238] Platform plugin ascend is activated
```

The following output shows the generated results:

```
Prompt: 'Hello, my name is', Generated text: ' Lucy and I am an 8 year old who loves to draw and write stories'
Prompt: 'The future of AI is', Generated text: ' a topic that is being discussed in various contexts. In the business world, AI'
```

The following messages show the process exiting after offline inference and do not affect the inference results:

```
(EngineCore pid=970) INFO 05-12 11:36:00 [core.py:1201] Shutdown initiated (timeout=0)
(EngineCore pid=970) INFO 05-12 11:36:00 [core.py:1224] Shutdown complete
ERROR 05-12 11:36:01 [core_client.py:704] Engine core proc EngineCore died unexpectedly, shutting down client.
sys:1: DeprecationWarning: builtin type swigvarlink has no __module__ attribute
```

### Online serving

A2 / A3 / 950DTAtlas 300I DUO / Atlas 200I Pro

The following Qwen3-0.6B example has been validated using the default model loading configuration.

```
vllm serve Qwen/Qwen3-0.6B &
```

If you see the following logs:

```
INFO:     Started server process [3594]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Congratulations! You have successfully started the vLLM server.

You can query the model list:

```
curl http://localhost:8000/v1/models | python3 -m json.tool
```

You can also send a prompt to the model:

```
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen3-0.6B",
        "prompt": "Beijing is a",
        "max_completion_tokens": 5,
        "temperature": 0
    }' | python3 -m json.tool
```

vLLM is running as a background process. You can use `kill -2 $VLLM_PID` to stop it gracefully, which is similar to pressing `Ctrl+C` for a foreground vLLM process:

Confirm the process before stopping the service

If other `vllm serve` processes are running in the current environment, `pgrep -f "vllm serve"` may also match those vLLM services.

Before running `kill`, confirm that `VLLM_PID` is the service started by this example to avoid stopping another running vLLM process by mistake.

```
VLLM_PID=$(pgrep -f "vllm serve")
kill -2 "$VLLM_PID"
```

The output is as follows:

```
INFO:     Shutting down FastAPI HTTP server.
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
```

Finally, press `Ctrl+D` to exit the container.

The following Qwen3-0.6B example has been validated on Atlas 300I DUO and Atlas 200I Pro.

Runtime requirements for this hardware path

* Use `float16`.
* Use `FULL_DECODE_ONLY` and limit the graph capture sizes.
* `enable_npugraph_ex` is not supported. Set `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex":false}}'`.

```
vllm serve Qwen/Qwen3-0.6B \
    --dtype float16 \
    --max-num-seqs 8 \
    --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY","cudagraph_capture_sizes":[1,2,4,8]}' \
    --additional-config '{"ascend_compilation_config":{"enable_npugraph_ex":false}}' &
```

If you see the following logs:

```
INFO:     Started server process [3594]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Congratulations! You have successfully started the vLLM server.

You can query the model list:

```
curl http://localhost:8000/v1/models | python3 -m json.tool
```

You can also send a prompt to the model:

```
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen3-0.6B",
        "prompt": "Beijing is a",
        "max_completion_tokens": 5,
        "temperature": 0
    }' | python3 -m json.tool
```

vLLM is running as a background process. You can use `kill -2 $VLLM_PID` to stop it gracefully, which is similar to pressing `Ctrl+C` for a foreground vLLM process:

Confirm the process before stopping the service

If other `vllm serve` processes are running in the current environment, `pgrep -f "vllm serve"` may also match those vLLM services.

Before running `kill`, confirm that `VLLM_PID` is the service started by this example to avoid stopping another running vLLM process by mistake.

```
VLLM_PID=$(pgrep -f "vllm serve")
kill -2 "$VLLM_PID"
```

The output is as follows:

```
INFO:     Shutting down FastAPI HTTP server.
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
```

Finally, press `Ctrl+D` to exit the container.

## Next steps

* See [Supported Models](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/user_guide/support_matrix/supported_models.html) to choose another model.
* See [Model Tutorials](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/tutorials/models/index.html) for deployment instructions for specific models.
* See [Installation Guide > Set up the software environment](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/latest/installation.html#installation-software-environment) for pip, CANN, and source installation methods.
* See [Feature Tutorials](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/tutorials/features/index.html) for distributed deployment and advanced features.
* See [FAQ](https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/faqs.html) to troubleshoot common deployment issues.