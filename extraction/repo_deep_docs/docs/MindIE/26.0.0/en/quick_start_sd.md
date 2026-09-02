# Quick Start

> 仓 `docs` · 路径 `MindIE/26.0.0/en/quick_start_sd.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/docs/MindIE/26.0.0/en/quick_start_sd.md

# MindIE SD 快速上手文档深度解读

## 【定位】

本文档以 Atlas 800I A2 推理服务器 + Wan2.1 模型为示例,提供 MindIE SD(Stable Diffusion 类服务)在昇腾 NPU 上一站式完成「环境校验 → 权重准备 → 容器启动 → 文生视频推理」全流程的快速入门指引,核心解决用户在物理机上从零部署 MindIE SD 并跑通文生视频(及图生视频)推理的问题。

---

## 【技术要点】

1. **环境前置检查**:通过 `npu-smi info` 校验 NPU 驱动/固件是否安装,通过 `docker ps` 校验 Docker 是否就绪;推荐硬件为 Atlas 800I A2 推理服务器。
2. **模型权重与权限约束**:Wan2.1 系列权重需放置在 `/home/<username>/example/` 下;MindIE SD 对输入文件做权限校验——**权重/配置文件权限 ≤ 640** 且与执行用户属主一致,**其所在文件夹权限 ≤ 750** 且与执行用户属主一致。
3. **容器镜像预装组件**:镜像 `mindie:3.0.0-800I-A2-py311-openeuler24.03-lts` 已内置 CANN、CANN-NNAL-ATB、MindIE、ATB Models 基础环境,免去手工部署。
4. **容器设备挂载要求**:NPU 设备(`/dev/davinci0`–`davinci3`)、`davinci_manager`、`hisi_hdc`、`devmm_svm` 必须以 `rwm` 权限挂载;`rw` 在 A2/A3 上分别会触发 `npu-smi` 报错及 `torch.npu.set_device()` 失败。
5. **多卡并行推理范式**:采用 `torchrun --nproc_per_node=8` 启动 8 卡并行,启用 `--dit_fsdp --t5_fsdp` 对 DiT 与 T5 做分片,并以 `--ulysses_size 8 --vae_parallel` 实现 Ulysses 序列并行与 VAE 并行。
6. **AttentionCache 加速机制**:通过 `--use_attentioncache --start_step --attentioncache_interval --end_step` 在指定去噪步区间内启用缓存,显著降低 attention 计算开销。

---

## 【关键机制与数据】

- **工作原理(原文:多卡分布式推理流水线)**:T2V/I2V 推理采用 **8 卡 FSDP + Ulysses 序列并行 + VAE 并行** 的混合并行策略,文本编码(T5)与 DiT 主干均按 FSDP 分片,Ulysses size=8 将长序列切分到 8 卡协同 attention,VAE 解码阶段亦并行执行。
- **采样与缓存参数(原文:T2V-14B)**:采样步数 `--sample_steps 50`,AttentionCache 覆盖区间为 **第 20 步到第 47 步**,间隔 `--attentioncache_interval 2`,即在该区间每隔 2 步复用一次 attention 缓存。
- **采样与缓存参数(原文:I2V-14B-480P)**:采样步数 `--sample_steps 40`,帧数 `--frame_num 81`,AttentionCache 起始步为 **第 12 步**,CFG 关闭(`--cfg_size 1`),文本条件不进行 classifier-free guidance。
- **性能数据**:原文未提供具体的吞吐量/时延/QPS 等性能数字。

---

## 【表格解读】

### Table 1 Atlas A2 inference products(原文逐字还原)

|Product Model|References|
|--|--|
|Atlas 800I A2||

**逐行解读**:
- **Atlas 800I A2**:本文档示例采用的推理服务器型号,References 列在原文中为空(无附加跳转链接),仅作型号标识用。

### Table 2 Model weight(原文逐字还原)

|Model|Description|Weight File|
|--|--|--|
|Wan2.1-T2V-14B|Text-to-video model|Click the link to obtain the weight file.|
|Wan2.1-I2V-14B-480P|Image-to-video model|Click the link to obtain the weight file.|
|Wan2.1-I2V-14B-720P|Image-to-video model|Click the link to obtain the weight file.|

**逐行解读**:
- **Wan2.1-T2V-14B**:14B 参数规模的 **文生视频(T2V)** 模型,本文档推理示例的主用例,1280×720 分辨率。
- **Wan2.1-I2V-14B-480P**:14B 参数规模的 **图生视频(I2V)** 模型,输出 832×480 分辨率,以单张参考图驱动生成 81 帧视频。
- **Wan2.1-I2V-14B-720P**:14B 参数规模的 **图生视频(I2V)** 模型,目标更高分辨率版本(具体分辨率原表未给出)。
- 三个 Weight File 列在原文中均以"Click the link to obtain the weight file"占位,指向可点击下载入口。

### Table 3 Installation path of each component in the container(原文逐字还原)

|Component|Installation Path|
|--|--|
|CANN|/usr/local/Ascend/cann|
|CANN-NNAL-ATB|/usr/local/Ascend/nnal/atb|
|MindIE|/usr/local/Ascend/mindie|
|ATB Models|/usr/local/Ascend/atb-models|

**逐行解读**:
- **CANN**(昇腾异构计算架构)位于 `/usr/local/Ascend/cann`,提供底层算子与运行时。
- **CANN-NNAL-ATB**(ATB 加速库)位于 `/usr/local/Ascend/nnal/atb`,负责 Transformer 类算子融合加速。
- **MindIE**(推理引擎主体)位于 `/usr/local/Ascend/mindie`,对外提供推理服务能力。
- **ATB Models**(模型适配层)位于 `/usr/local/Ascend/atb-models`,承载具体模型的算子图与实现。

### Table 4 Parameters(原文逐字还原)

|Parameters|Description|
|--|--|
|--name|Specifies the container name.|
|--device|Mounts one or multiple devices.<br>The devices to be mounted are as follows: <ul><li>`/dev/davinciX`: NPU device. X indicates the ID, for example, `davinci0`. </li><li>/`dev/davinci_manager`: Da Vinci-related management device. </li><li>`/dev/hisi_hdc`: HDC management device. </li><li>`/dev/devmm_svm`: memory management device. </li></ul> You can run the following command to query the number of devices and the device name mode, bind devices as required, and modify `--device=****` in the preceding command.<br>`ll /dev/ \| grep davinci`|
|-v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro|Mounts the host directory `/usr/local/Ascend/driver` to the container. Change it according to the actual driver path.|
|-v /usr/local/sbin/:/usr/local/sbin/:ro|Mounts the host tool `/usr/local/sbin` to the container in read-only mode. Change it as required.|
|-v /path-to-weights:/path-to-weights:ro|Sets the weight mounting path as required.<br>**Place the weight file and dataset file in the same path.**|

**逐行解读**:
- **`--name`**:设置容器名,便于后续 `docker exec` 进入。
- **`--device`**:逐个挂载 NPU 计算/管理设备;`/dev/davinciX` 是 NPU 计算卡(X 为编号)、`davinci_manager` 是 Da Vinci 管理设备、`hisi_hdc` 是 HDC 管理通道、`devmm_svm` 是 SVM 内存管理设备;可通过 `ll /dev/ | grep davinci` 自适应调整。
- **`-v /usr/local/Ascend/driver:...`**:将宿主机驱动目录以只读方式挂入容器,确保容器内 NPU 驱动可见且不被篡改。
- **`-v /usr/local/sbin/:...`**:只读挂载宿主机 sbin 工具(含 `npu-smi` 等命令行),便于容器内诊断。
- **`-v /path-to-weights:...`**:只读挂载权重路径,**要求权重文件与数据集文件放在同一目录下**(满足 MindIE SD 的权限校验和路径解析逻辑)。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 MindIE 主体的关系**:本文档是 MindIE SD 子组件在 Atlas 800I A2 上的部署/使用指南,镜像中已预装 MindIE 主体(`/usr/local/Ascend/mindie`),SD 通过调用 MindIE 推理引擎完成实际推理。
- **与 ATB Models 的关系**:Wan2.1 的算子图实现位于 `/usr/local/Ascend/atb-models`,MindIE SD 在执行文生/图生视频推理时依赖 ATB Models 提供的模型适配。
- **与 CANN / CANN-NNAL-ATB 的关系**:底层依赖 CANN 提供运行时与算子,CANN-NNAL-ATB 在此之上提供 Transformer 加速(AttentionCache 与并行策略均运行于此层)。
- **与 Atlas 800I A2 / A3 硬件的依赖**:镜像 tag 含 `800I-A2` 标识,设备挂载与 `rwm` 权限建议均与 A2/A3 硬件管理模型强绑定;切换 A3 SuperPoD 需注意 `rwm`/`rw` 差异。
- **容器编排依赖**:容器启动使用 `ascend-docker-image` 仓库规范,文末给出 `https://gitee.com/ascend/ascend-docker-image/tree/dev/mindie` 的「Starting a Container」参考入口(原文链接,提示属于跨文档外链而非仓库内链)。
- **注**:用户给出的内部链接信息标注为"(无)",因此本节不再补充其他内部锚点。

---

## 【使用方法】

### 1. 环境校验命令(原文有)

```bash
npu-smi info        # 校验 NPU 驱动/固件
docker ps           # 校验 Docker
```

### 2. 权重下载与路径(原文有)

- 模型仓库: `git clone https://modelers.cn/MindIE/Wan2.1.git`
- 推荐存放路径:`/home/<username>/example/Wan2.1-T2V-14B`(或 I2V-14B-480P / I2V-14B-720P)
- 权限要求:文件 ≤ 640、文件夹 ≤ 750,且与执行用户属主一致。

### 3. 容器启动命令(原文有)

```bash
docker run -it -d --net=host --shm-size=1g \
       --name <container-name> \
       -w /home \
       --device=/dev/davinci0:rwm --device=/dev/davinci1:rwm \
       --device=/dev/davinci2:rwm --device=/dev/davinci3:rwm \
       --device=/dev/davinci_manager:rwm --device=/dev/hisi_hdc:rwm \
       --device=/dev/devmm_svm:rwm \
       -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro \
       -v /usr/local/dcmi:/usr/local/dcmi:ro \
       -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi:ro \
       -v /usr/local/sbin/:/usr/local/sbin:ro \
       -v /path-to-weights:/path-to-weights:ro \
       mindie:3.0.0-800I-A2-py311-openeuler24.03-lts bash
```

进入容器:

```bash
docker exec -it <container-name> /bin/bash
```

### 4. 推理命令(原文有,共两段)

**T2V-14B 文生视频(8 卡)**:

```bash
Model_base="/home/{Username}/example/Wan2.1-T2V-14B"
torchrun --nproc_per_node=8 generate.py \
      --task t2v-14B --size 1280*720 --ckpt_dir ${model_base} \
      --dit_fsdp --t5_fsdp --sample_steps 50 --ulysses_size 8 \
      --vae_parallel \
      --prompt "..." \
      --use_attentioncache --start_step 20 --attentioncache_interval 2 --end_step 47
```

**I2V-14B-480P 图生视频(8 卡)**:

```bash
Model_base="/home/{Username}/example/Wan2.1-I2V-14B-480P/"
torchrun --nproc_per_node=8 generate.py \
      --task i2v-14B --size 832*480 --ckpt_dir ${model_base} \
      --frame_num 81 --sample_steps 40 --dit_fsdp --t5_fsdp \
      --cfg_size 1 --ulysses_size 8 --vae_parallel \
      --image examples/i2v_input.JPG --base_seed 0 \
      --prompt "..." \
      --use_attentioncache --start_step 12 --attentioncache <(原文此处被截断,后续参数未给出)>
```

### 5. 关键开关与配置项速查(原文有)

|配置项|作用|原文取值|
|--|--|--|
|`--nproc_per_node`|单机进程数(卡数)|8|
|`--dit_fsdp`|对 DiT 主干做 FSDP 分片|启用|
|`--t5_fsdp`|对 T5 文本编码器做 FSDP 分片|启用|
|`--ulysses_size`|Ulysses 序列并行规模|8|
|`--vae_parallel`|VAE 解码阶段并行|启用|
|`--cfg_size`|CFG 数量|I2V 示例中为 1(关闭)|
|`--use_attentioncache`|启用 AttentionCache|启用|
|`--start_step / --end_step`|AttentionCache 起止去噪步|T2V: 20–47;I2V: 12–?|
|`--attentioncache_interval`|缓存复用间隔步|T2V: 2|

> 备注:原文在 I2V-14B-480P 示例命令末尾被截断(`--attentioncache` 后内容缺失),后续 `--end_step` 等参数未给出,如需完整命令请参照官方仓库 `Wan2.1/generate.py` 的 argparse 定义。

## 图文联合解读

- `command_output.png`: **图释**：终端执行`npu-smi info`命令，输出8颗NPU芯片（ID 0-7）的状态表，涵盖健康状态、功耗（约95-102W）、温度（48-52℃）、HBM显存（约3050/65536MB）等关键指标。

**结论**：表明NPU驱动与固件已正确安装部署，且8颗芯片全部"OK"健康可用。

**与文档关系**：作为前置条件验证的视觉证据，印证环境就绪，可进入后续模型部署流程。
