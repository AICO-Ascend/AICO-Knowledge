# 快速开始

> 仓 `docs` · 路径 `MindIE/26.0.0/quick_start_sd.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/docs/MindIE/26.0.0/quick_start_sd.md

# 一体化深度解读：MindIE SD 快速开始（Wan2.1 文生视频）

---

## 【定位】

本文档以 Atlas 800I A2 推理服务器 + Wan2.1 模型为示例，提供从环境准备（NPU 驱动/Docker）、权重获取、容器镜像拉取、容器启动到使用 MindIE SD 接口进行**文生视频（t2v）与图生视频（i2v）**多卡分布式推理的端到端快速上手流程。

---

## 【技术要点】

1. **硬件与平台基线**：物理机部署 Atlas 800I A2 推理服务器，需预装 NPU 驱动固件并部署 Docker；通过 `npu-smi info` 与 `docker ps` 两个命令分别校验 NPU 与 Docker 状态。

2. **模型覆盖范围**：以 Wan2.1 系列模型为例，包含 3 个权重变体——`Wan2.1-T2V-14B`（文生视频）、`Wan2.1-I2V-14B-480P` 与 `Wan2.1-I2V-14B-720P`（图生视频），权重均从 HuggingFace 仓 `Wan-AI/` 下获取。

3. **容器镜像一键化**：昇腾官方镜像 `mindie:3.0.0-800I-A2-py311-openeuler24.03-lts` 已集成 CANN、CANN-NNAL-ATB、MindIE、ATB Models 四大组件，可直接推理而无需额外装环境。

4. **设备挂载与权限**：容器启动需以 `rwm`（非 `rw` 或 `r`）权限挂载 `/dev/davinci*`、davinci_manager、hisi_hdc、devmm_svm 等设备；其中 `davinci*` 的 rwm 设置关系到 `npu-smi` 与 `torch.npu.set_device()` 在多任务占用场景下能否正常运行。

5. **多卡并行策略**：所有示例均采用 **8 卡** 推理，组合策略为 `DiT FSDP + T5 FSDP + Ulysses 并行 + VAE 并行`，并行规模满足约束 `ulysses_size × cfg_size = nproc_per_node`。

6. **AttentionCache 有损加速**：通过 `--use_attentioncache` 配合 `--start_step / --attentioncache_interval / --end_step` 三个参数，对扩散步中前 N 步到后 M 步的中间 attention 状态进行缓存复用，仅在有效区间开启。

---

## 【关键机制与数据】

### 工作原理与数据流（原文事实陈述，无臆造）

- **接口安全校验机制**：原文："MindIE SD接口会对传入的文件或文件夹做权限安全校验"——这是推理前的硬性前置检查，对应权限约束为：
  - 模型权重文件 / 配置文件：三组权限 ≤ **640**，且需与执行用户的所属组、权限保持一致。
  - 上述文件所在文件夹：三组权限 ≤ **750**，且需与执行用户的所属组、权限保持一致。

- **容器内组件分层结构**（表 3 还原）：
  - CANN → `/usr/local/Ascend/cann`
  - CANN-NNAL-ATB → `/usr/local/Ascend/nnal/atb`
  - MindIE → `/usr/local/Ascend/mindie`
  - ATB Models → `/usr/local/Ascend/atb-models`

- **推理数据流概览**（基于示例命令）：
  1. 用户将权重通过 `-v /path-to-weights:/path-to-weights:ro` 只读挂载进容器；
  2. 通过 `git clone https://modelers.cn/MindIE/Wan2.1.git` 获取推理仓，并 `pip install -r requirements.txt`；
  3. 使用 `torchrun --nproc_per_node=8 generate.py` 启动分布式推理；
  4. T2V 走纯文本 prompt → 视频；I2V 走 prompt + 参考图（如 `examples/i2v_input.JPG`）→ 视频。

- **注意力缓存触发区间**（原文示例中的具体数字）：

  | 模型 | sample_steps | start_step | attentioncache_interval | end_step |
  |---|---|---|---|---|
  | Wan2.1-T2V-14B | 50 | 20 | 2 | 47 |
  | Wan2.1-I2V-14B-480P | 40 | 12 | 4 | 37 |
  | Wan2.1-I2V-14B-720P | 40 | 12 | 4 | 37 |

  （注：T2V 默认 `sample_steps=50`、I2V 默认 `sample_steps=40`，与下方"取值"列一致。）

> 原文未提供吞吐量、显存占用、首帧时延等性能数字，因此本节不臆造任何性能数据。

---

## 【表格解读】

### 表 1：Atlas A2 推理系列产品（产品型号 / 参考文档）

|产品型号|参考文档|
|--|--|
|Atlas 800I A2|下载[固件与驱动](https://hiascend.com/hardware/firmware-drivers/community)，请参考《CANN 软件安装》中的"[安装NPU驱动和固件](https://www.hiascend.com/document/detail/zh/canncommercial/850/softwareinst/instg/instg_0005.html?Mode=PmIns&InstallType=local&OS=openEuler)"章节（商用版）或"[安装NPU驱动和固件](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850/softwareinst/instg/instg_0005.html?Mode=PmIns&InstallType=local&OS=openEuler)"章节（社区版）进行安装。|

**解读**：本表仅列出当前文档示例所对应的硬件——Atlas 800I A2，并指向昇腾社区/商用 CANN 的 NPU 驱动固件安装手册的"安装NPU驱动和固件"章节（社区版 openEuler 路径），区分了 CANN 商用版与社区版两份不同文档。

---

### 表 2：模型权重（模型 / 说明 / 权重）

|模型|说明|权重|
|--|--|--|
|Wan2.1-T2V-14B|文生视频模型|权重文件请单击[链接](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B/tree/main)获取。|
|Wan2.1-I2V-14B-480P|图生视频模型|权重文件请单击[链接](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P/tree/main)获取。|
|Wan2.1-I2V-14B-720P|图生视频模型|权重文件请单击[链接](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-720P/tree/main)获取。|

**解读**：
- T2V（Text-to-Video）仅需文本输入；I2V（Image-to-Video）则需文本+参考图。
- I2V 又细分 480P 与 720P 两种分辨率版本，对应不同的训练分辨率与下游推理 `--size` 默认值。
- 所有权重均在 HuggingFace 公开仓 `Wan-AI/` 下，按需下载到本地路径（例如 `/home/{用户名}/example/Wan2.1-T2V-14B`）。

---

### 表 3：容器内各组件安装路径

|组件|安装路径|
|--|--|
|CANN|/usr/local/Ascend/cann|
|CANN-NNAL-ATB|/usr/local/Ascend/nnal/atb|
|MindIE|/usr/local/Ascend/mindie|
|ATB Models|/usr/local/Ascend/atb-models|

**解读**：四个组件形成完整推理栈——CANN 提供底层算子/编译；CANN-NNAL-ATB（ATB 加速库）做算子融合加速；MindIE 是面向昇腾的统一推理服务/SDK 入口；ATB Models 是模型仓库层（包含 Wan2.1 等示例模型实现）。四者默认装在 `/usr/local/Ascend/` 树形目录下，便于容器内统一引用。

---

### 表 4：docker run 参数说明

|参数|参数说明|
|--|--|
|--name|设置容器名称。|
|--device|表示映射的设备，可以挂载一个或者多个设备。<br>需要挂载的设备如下：<ul><li>/dev/davinci*X*：NPU设备，X是ID号，如：davinci0。</li><li>/dev/davinci_manager：davinci相关的管理设备。</li><li>/dev/hisi_hdc：hdc相关管理设备。</li><li>/dev/devmm_svm：内存管理相关设备。</li></ul>可根据以下命令查询device个数及名称方式，根据需要绑定设备，修改上面命令中的"--device=****"。<br>**ll /dev/ \| grep davinci**|
|-v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro|将宿主机目录"/usr/local/Ascend/driver"挂载到容器，请根据驱动所在实际路径修改。|
|-v /usr/local/sbin/:/usr/local/sbin/ro|将宿主机工具"/usr/local/sbin"以只读模式挂载到容器中，请根据实际情况修改。|
|-v /path-to-weights:/path-to-weights:ro|设定权重挂载的路径，需要根据用户的情况修改。<br>**请将权重文件和数据集文件同时放置于该路径下**。|

**解读**：
- `--device` 列覆盖了**算力设备**（davinci\*）、**管理面设备**（davinci_manager、hisi_hdc）和**内存管理设备**（devmm_svm），缺一不可；用户可通过 `ll /dev/ | grep davinci` 查看本机实际 NPU 数量并按需裁剪 `--device` 列表。
- `-v` 全部以 `:ro`（只读）模式挂载宿主机目录，避免容器内误改宿主机文件。
- 特别强调：权重与数据集**必须共置**于同一挂载路径 `/path-to-weights` 内，便于一次挂载后所有节点共享访问。

---

### 表 1（推理参数解释，原文编号与上文重复）

|参数名|参数含义|取值|
|--|--|--|
|model_base|权重路径|模型权重所在路径。|
|task|任务类型|支持"t2v-14B"和"i2v-14B"。|
|size|视频分辨率|生成视频的宽\*高。<ul><li>"t2v-14B"模型默认值为1280*720</li><li>"i2v-14B-480P"模型默认值为[832, 480]、[720, 480]</li><li>"i2v-14B-720P"模型默认值为[1280, 720]</li></ul>|
|frame_num|生成视频的帧数|默认值：81|
|sample_steps|采样步数|扩散模型的迭代降噪步数。<ul><li>t2v模型默认值：50</li><li>i2v模型默认值：40</li></ul>|
|prompt|文本提示词|用户自定义，用于控制视频生成。|
|image|用于生成视频的图片路径|i2v模型推理必须，用户自定义，用于控制视频生成。|
|base_seed|随机种子|用于视频生成的随机种子。|
|use_attentioncache|使能attentioncache算法优化|此优化为有损优化，如需要开启此优化，请设置如下参数：start_step、attentioncache_interval、end_step，分别表示cache开始的step、连续cache数、cache结束的step；如不开启，则无需设置use_attentioncache、start_step、attentioncache_interval、end_step。|
|nproc_per_node|并行卡数|<ul><li>Wan2.1-T2V-14B支持的卡数为1、2、4或8</li><li>Wan2.1-I2V-14B支持的卡数为1、2、4或8</li></ul>|
|ulysses_size|ulysses并行数|默认值为1，ulysses_size * cfg_size = nproc_per_node。|
|cfg_size|cfg并行数|默认值为1，ulysses_size * cfg_size = nproc_per_node。|
|dit_fsdp|DiT使用FSDP|DiT模型是否使用完全分片数据并行（Fully Sharded Data Parallel, FSDP）策略。|
|t5_fsdp|T5使用FSDP|文本到文本传输转换（Te*（原文此处被截断）|

**解读**：
- `size` 字段对三种模型给出不同默认分辨率集合，其中 I2V-480P 支持 `[832, 480]` 和 `[720, 480]` 两种输出。
- `sample_steps` 在不同任务下默认不同（T2V=50、I2V=40），且 `attentioncache` 参数必须与之协同设置。
- `use_attentioncache` 是**有损优化**，开启后必须同时给出 `start_step / attentioncache_interval / end_step` 三个步数参数，否则不生效；不开启时这四个参数均不设置。
- `nproc_per_node` 支持 1/2/4/8 卡多种并行度，所有官方示例均采用 8 卡；总并行度约束为 `ulysses_size × cfg_size = nproc_per_node`。
- `dit_fsdp` 与 `t5_fsdp` 分别对**扩散主干 DiT** 与**文本编码器 T5** 做 FSDP 分片；两者可独立开关。
- 末行 `t5_fsdp` 字段含义被原文截断于"文本到文本传输转换（Te…"，无法逐字还原完整释义。

---

## 【公式解读】

原文**未出现标准 LaTeX 公式**，但存在两处形式化约束/经验式表达，逐字保留并解释如下：

### 1. 并行规模约束（文字形式）

```
ulysses_size * cfg_size = nproc_per_node
```

- **`ulysses_size`**：Ulysses 长序列并行度，默认为 1。Ulysses 是面向 DiT 视频扩散模型的序列维并行策略，将长视频帧序列切分到多卡。
- **`cfg_size`**：Classifier-Free Guidance 并行度，默认为 1。CFG 在推理中通常需要并行跑"有条件 + 无条件"两条分支，再融合。
- **`nproc_per_node`**：单节点内可见的 NPU 卡数（本文档示例均为 8）。
- **作用**：三者必须满足乘积等式，确保总并行度等于实际可见卡数，从而避免资源闲置或超出物理硬件。本文档三个示例均为 `ulysses_size=8, cfg_size=1` 满足 `8×1=8`。

### 2. 文件权限约束（不等式形式）

```
文件/配置文件权限 ≤ 640
文件夹权限 ≤ 750
```

- 三个三元组（owner/group/other）的位与值均不得超过 640（文件）/ 750（文件夹）；
- 且所属组与权限必须**与执行用户完全一致**——本质上是 MindIE SD 出于安全校验的硬性前置条件。

---

## 【关联】

依据原文信息，该文档与以下模块/上游特性存在关联：

- **CANN / CANN-NNAL-ATB / ATB Models**：作为 MindIE 的底层运行时依赖被预装于镜像中（容器内路径见表 3）；ATB Models 仓库提供了本文档示例所调用的 `generate.py` 入口脚本。
- **FrameworkPTAdapter**：原文中作为镜像预装组件之一被提及，但本文档未展开其内部用法。
- **Atlas 800I A2 / A3 推理服务器**：文档同时提及 A2（示例所用）与 A3 超节点；指出 A3 在 `--device` 权限设置为 `rw` 时 `npu-smi` 会报错，故必须使用 `rwm`，这是两代硬件在该挂载语义上的关键差异。
- **昇思 MindIE 全家桶**：本文档聚焦 SD（Stable Diffusion）场景下的快速开始，MindIE 本身还包含 LLM/多模态等其他推理线，SD 只是其中一条业务线（文件名 `quick_start_sd.md` 即体现该定位）。
- **昇腾官方镜像仓库** (`https://www.hiascend.com/developer/ascendhub/detail/af85b724a7e5469ebd7ea13c3439d48f`)：作为镜像分发入口，承载了不同设备型号/操作系统组合的 MindIE 镜像。
- **modelers.cn 模型仓**（`https://modelers.cn/MindIE/Wan2.1.git`）：提供推理示例代码而非权重，权重则在 HuggingFace `Wan-AI/` 仓。
- **ascend-docker-image 仓**：原文注脚指引"更多详细信息，请参考启动容器章节"指向 `https://gitee.com/ascend/ascend-docker-image/tree/dev/mindie`，与本文档 `docker run` 启动命令互为补充。

> 文档提供的内部链接信息为"(无)"，以上关联均根据正文引用得出。

---

## 【使用方法】

### Step 1 · 环境校验（原文命令）

```bash
npu-smi info      # 检查 NPU 驱动固件
docker ps         # 检查 Docker 是否安装并启动（出现 CONTAINER ID/IMAGE/COMMAND…表头即正常）
```

### Step 2 · 权重获取与权限配置

- 从 HuggingFace `Wan-AI/Wan2.1-T2V-14B`（或 480P/720P 的 I2V 变体）仓下载权重至用户自定路径，例如：
  ```
  /home/{用户名}/example/Wan2.1-T2V-14B
  ```
- 配置权限：权重文件/配置 ≤ 640，目录 ≤ 750，所属组与执行用户一致。

### Step 3 · 拉取并启动容器（原文 `docker run`）

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

随后：

```bash
docker exec -it <container-name> /bin/bash
```

### Step 4 · 获取推理仓并安装依赖

```bash
git clone https://modelers.cn/MindIE/Wan2.1.git
cd Wan2.1
pip install -r requirements.txt
```

### Step 5 · 文生视频（T2V-14B，8 卡）原文

```bash
model_base="/home/{用户名}/example/Wan2.1-T2V-14B"
torchrun --nproc_per_node=8 generate.py \
  --task t2v-14B \
  --size 1280*720 \
  --ckpt_dir ${model_base} \
  --dit_fsdp --t5_fsdp \
  --sample_steps 50 \
  --ulysses_size 8 \
  --vae_parallel \
  --prompt "Two anthropomorphic cats in comfy boxing gear and bright gloves fight intensely on a spotlighted stage." \
  --use_attentioncache --start_step 20 --attentioncache_interval 2 --end_step 47
```

### Step 6 · 图生视频（I2V-14B-480P / 720P，8 卡）原文要点

- 公共参数：`--task i2v-14B --frame_num 81 --sample_steps 40 --dit_fsdp --t5_fsdp --cfg_size 1 --ulysses_size 8 --vae_parallel --image examples/i2v_input.JPG --base_seed 0 --use_attentioncache --start_step 12 --attentioncache_interval 4 --end_step 37`；
- 差异项：`--size` 480P 用 `832*480`、720P 用 `1280*720`；其余 `--ckpt_dir` 与 `model_base` 指向对应权重目录。

### 关键配置项汇总（结合原文"取值"列）

| 配置维度 | 关键项 | 文档原文取值 |
|---|---|---|
| 硬件卡数 | `nproc_per_node` | T2V/I2V 均支持 1/2/4/8 |
| 并行切分 | `ulysses_size × cfg_size` | 默认 1×1，需满足乘积 = nproc_per_node |
| 模型切分 | `dit_fsdp` / `t5_fsdp` | 二者可独立启用 |
| 采样 | `sample_steps` | T2V=50，I2V=40 |
| 帧数 | `frame_num` | 81 |
| 注意力缓存 | `use_attentioncache` + `start_step/attentioncache_interval/end_step` | 有损优化；T2V 推荐 20/2/47，I2V 推荐 12/4/37 |

> 文档未提供调优/排错类命令、性能基准测试命令或停止容器命令，因此本节"使用方法"仅以原文已展示的命令为限；其它未涉及之处原文未给出。

## 图文联合解读

- `command_output.png`: **图文联合解读：**

1) **画面内容**：终端执行`npu-smi info`回显，展示8颗NPU芯片（0–7）的状态表，包含Health（均OK）、Power（约95–103W）、Temp（48–52℃）、HBM-Usage（约3050/65536 MB）等关键指标。

2) **技术结论**：证明NPU驱动固件已正确安装，8张加速卡全部健康在位，可支撑后续MindIE SD部署。

3) **与文档关系**：作为"前提条件"中"NPU驱动固件安装"的判定凭证，用户对照此图确认环境就绪后，方可进入模型权重获取与文生视频流程。
