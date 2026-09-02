# 快速开始

> 仓 `docs` · 路径 `MindIE/26.1.0/zh/quick_start_sd.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/docs/MindIE/26.1.0/zh/quick_start_sd.md

```markdown
# MindIE SD 快速开始文档深度解读

## 【定位】

本文档面向 Atlas 800I A2 推理服务器上的开发者，提供基于 MindIE SD 与 Wan2.1 系列模型（文生视频 T2V-14B、图生视频 I2V-14B-480P/720P）从环境准备、镜像获取、容器启动到 8 卡推理的端到端 quick start 指南。

---

## 【技术要点】

1. **硬件与基础环境前置校验**：物理机部署场景需先安装 NPU 驱动固件并部署 Docker，通过 `npu-smi info` 验证 NPU 驱动、`docker ps` 验证 Docker 运行；Atlas A2 推理系列产品需参照 CANN 软件安装指南。
2. **模型权重与权限约束**：Wan2.1 模型权重从 Hugging Face 下载，用户自定义路径（如 `/home/{用户名}/example/Wan2.1-T2V-14B`）；MindIE SD 接口对权重文件/配置文件执行权限安全校验——文件权限不得超过 **640**、文件夹权限不得超过 **750**，且需与执行用户的所属组和权限保持一致。
3. **容器镜像内置组件**：MindIE 官方镜像已集成 CANN（`/usr/local/Ascend/cann`）、CANN-NNAL-ATB（`/usr/local/Ascend/nnal/atb`）、MindIE（`/usr/local/Ascend/mindie`）、ATB Models（`/usr/local/Ascend/atb-models`）四大组件，无需额外安装。
4. **容器启动的设备挂载策略**：使用 `docker run` 启动容器，挂载 `/dev/davinci0~3`、`/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm` 共 7 个设备；**挂载权限必须设为 `rwm`（而非 `rw` 或 `r`）**——Atlas 800I A2 推理服务器在 `rw` 下会因其它任务占用 NPU 时 `npu-smi` 报错且 `torch.npu.set_device()` 失败，Atlas 800I A3 超节点服务器在 `rw` 下直接进入即报错。
5. **模型仓库与依赖**：通过 `git clone https://modelers.cn/MindIE/Wan2.1.git` 获取推理代码，进入 `Wan2.1` 目录后执行 `pip install -r requirements.txt` 安装依赖。
6. **推理命令三套配置**（均使用 `torchrun --nproc_per_node=8` 启动 8 卡并行）：
   - T2V-14B：1280×720、50 步采样，开启 `--dit_fsdp --t5_fsdp --ulysses_size 8 --vae_parallel --use_attentioncache --start_step 20 --attentioncache_interval 2 --end_step 47`；
   - I2V-14B-480P：832×480、40 步采样、`--frame_num 81`、`--cfg_size 1`、`--start_step 12 --attentioncache_interval 4 --end_step 37`；
   - I2V-14B-720P：1280×720、40 步采样、参数与 480P 类似，分辨率切换为 1280×720。
7. **并行拓扑约束**：`ulysses_size * cfg_size = nproc_per_node`，默认均为 1；支持的并行卡数为 **1/2/4/8**。

---

## 【关键机制与数据】

- **工作原理（数据流，来源原文）**：
  - 启动容器 → 进入容器 → clone 推理代码仓库 → 安装 requirements → 挂载的 `/path-to-weights` 提供模型权重 → `torchrun` 调用 `generate.py` → DiT/T5 模型以 FSDP + Ulysses 并行方式调度 8 张 NPU → 通过 `--use_attentioncache` 启用有损 attention cache 优化（由 `start_step`/`attentioncache_interval`/`end_step` 界定缓存区间）→ 文生视频（T2V）或图生视频（I2V，`--image` 输入图片、`--base_seed` 控制随机性）→ 输出视频。
- **性能/采样相关数据（原文）**：
  - 采样步数：T2V-14B = 50 步，I2V-14B = 40 步。
  - 视频帧数：I2V 模型默认 81 帧。
  - 分辨率：T2V-14B 默认 1280×720；I2V-14B-480P 默认 832×480 或 720×480；I2V-14B-720P 默认 1280×720。
  - 容器共享内存：`--shm-size=1g`。
- **attentioncache 优化机制（原文）**：为有损优化；若开启必须同时设置 `start_step`（cache 开始 step）、`attentioncache_interval`（连续 cache 数）、`end_step`（cache 结束 step）；不开启则无需设置这四项参数。
- **权限校验机制（原文）**：MindIE SD 接口会对传入的文件/文件夹做权限安全校验，因此部署前必须按 640/750 规则设置权限并匹配所属组。

---

## 【表格解读】

### 表 1：Atlas A2 推理系列产品（原文）

| 产品型号 | 参考文档 |
| -- | -- |
| Atlas 800I A2 | 下载[固件与驱动](https://hiascend.com/hardware/firmware-drivers/community)，请参考《CANN 软件安装》中的"[安装NPU驱动和固件](https://www.hiascend.com/document/detail/zh/canncommercial/850/softwareinst/instg/instg_0005.html?Mode=PmIns&InstallType=local&OS=openEuler)"章节（商用版）或"[安装NPU驱动和固件](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850/softwareinst/instg/instg_0005.html?Mode=PmIns&InstallType=local&OS=openEuler)"章节（社区版）进行安装。 |

**解读**：仅列出 Atlas 800I A2 一款产品（与本文示例机型一致），给出固件/驱动下载地址以及 CANN 商用版与社区版的安装指南双入口。

---

### 表 2：模型权重（原文）

| 模型 | 说明 | 权重 |
| -- | -- | -- |
| Wan2.1-T2V-14B | 文生视频模型 | 权重文件请单击[链接](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B/tree/main)获取。 |
| Wan2.1-I2V-14B-480P | 图生视频模型 | 权重文件请单击[链接](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P/tree/main)获取。 |
| Wan2.1-I2V-14B-720P | 图生视频模型 | 权重文件请单击[链接](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-720P/tree/main)获取。 |

**解读**：覆盖一个 T2V 模型与两个 I2V 模型（480P/720P 两个分辨率变体），均从 Hugging Face `Wan-AI` 组织下载；T2V 对应 `--task t2v-14B`、I2V 对应 `--task i2v-14B`。

---

### 表 3：容器内各组件安装路径（原文）

| 组件 | 安装路径 |
| -- | -- |
| CANN | /usr/local/Ascend/cann |
| CANN-NNAL-ATB | /usr/local/Ascend/nnal/atb |
| MindIE | /usr/local/Ascend/mindie |
| ATB Models | /usr/local/Ascend/atb-models |

**解读**：揭示 MindIE 官方镜像内置的四层软件栈路径，从底层昇腾计算架构（CANN）到 ATB 加速库（CANN-NNAL-ATB）、MindIE 推理框架、ATB Models 模型库。

---

### 表 4：docker run 参数说明（原文节选）

| 参数 | 参数说明 |
| -- | -- |
| --name | 设置容器名称。 |
| --device | 表示映射的设备，可以挂载一个或者多个设备。<br>需要挂载的设备如下：<ul><li>/dev/davinci*X*：NPU设备，X是ID号，如：davinci0。</li><li>/dev/davinci_manager：davinci相关的管理设备。</li><li>/dev/hisi_hdc：hdc相关管理设备。</li><li>/dev/devmm_svm：内存管理相关设备。</li></ul>可根据以下命令查询 device 个数及名称方式，根据需要绑定设备，修改上面命令中的"--device=****"。<br>**ll /dev/ \| grep davinci** |
| -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro | 将宿主机目录"/usr/local/Ascend/driver"挂载到容器，请根据驱动所在实际路径修改。 |
| -v /usr/local/sbin/:/usr/local/sbin:ro | 将宿主机工具"/usr/local/sbin"以只读模式挂载到容器中，请根据实际情况修改。 |
| -v /path-to-weights:/path-to-weights:ro | 设定权重挂载的路径，需要根据用户的情况修改。<br>**请将权重文件和数据集文件同时放置于该路径下**。 |

**解读**：四条挂载/参数说明——容器命名、NPU 设备族挂载（4 类设备，davinciX + davinci_manager + hisi_hdc + devmm_svm）、驱动/工具目录只读挂载、权重路径只读挂载（要求权重与数据集同目录）。表中强调 `ro`（只读）模式挂载，与设备 `rwm` 形成对比。

---

### 表 5：generate.py 推理参数解释（原文）

| 参数名 | 参数含义 | 取值 |
| -- | -- | -- |
| model_base | 权重路径 | 模型权重所在路径。 |
| task | 任务类型 | 支持"t2v-14B"和"i2v-14B"。 |
| size | 视频分辨率 | 生成视频的宽\*高。<ul><li>"t2v-14B"模型默认值为 1280*720</li><li>"i2v-14B-480P"模型默认值为 [832, 480]、[720, 480]</li><li>"i2v-14B-720P"模型默认值为 [1280, 720]</li></ul> |
| frame_num | 生成视频的帧数 | 默认值：81 |
| sample_steps | 采样步数 | 扩散模型的迭代降噪步数。<ul><li>t2v 模型默认值：50</li><li>i2v 模型默认值：40</li></ul> |
| prompt | 文本提示词 | 用户自定义，用于控制视频生成。 |
| image | 用于生成视频的图片路径 | i2v 模型推理必须，用户自定义，用于控制视频生成。 |
| base_seed | 随机种子 | 用于视频生成的随机种子。 |
| use_attentioncache | 使能 attentioncache 算法优化 | 此优化为有损优化，如需要开启此优化，请设置如下参数：start_step、attentioncache_interval、end_step，分别表示 cache 开始的 step、连续 cache 数、cache 结束的 step；如不开启，则无需设置 use_attentioncache、start_step、attentioncache_interval、end_step。 |
| nproc_per_node | 并行卡数 | <ul><li>Wan2.1-T2V-14B 支持的卡数为 1、2、4 或 8</li><li>Wan2.1-I2V-14B 支持的卡数为 1、2、4 或 8</li></ul> |
| ulysses_size | ulysses 并行数 | 默认值为 1，ulysses_size * cfg_size = nproc_per_node。 |
| cfg_size | cfg 并行数 | 默认值为 1，ulysses_size * cfg_size = nproc_per_node。 |
| dit_fsdp | DiT 使用 FSDP | DiT 模型是否使用完全分片数据并行（Fully Sharded Data Parallel, FSDP）策略。 |
| t5_fsdp | T5 使用 FSDP | 文本到文本传输转换（Text-To-Text T…（原文截断） |

**解读**：13 个核心推理参数——`model_base` 指定权重；`task` 区分 T2V/I2V；`size` 决定分辨率（三档默认）；`frame_num=81`；`sample_steps` 在 T2V/I2V 分别为 50/40；`prompt` 文本驱动、`image` 仅 I2V 必填、`base_seed` 控制随机性；`use_attentioncache` 为有损优化并配 `start_step`/`attentioncache_interval`/`end_step` 三参；`nproc_per_node` 限定 1/2/4/8 档位；`ulysses_size * cfg_size = nproc_per_node` 为并行拓扑约束；`dit_fsdp`/`t5_fsdp` 分别对 DiT 与 T5 启用 FSDP 策略。

---

## 【公式解读】

**原文无公式**。

（注：文中出现的约束关系 `ulysses_size * cfg_size = nproc_per_node` 为并行拓扑规则，并非数学公式；参数值如 `1280*720`、`832*480` 为字符串形式的分辨率描述，亦非公式。）

---

## 【关联】

由于本文为独立 Quick Start 文档，未在文末提供内部链接；但根据文档内容，可梳理如下上下游与模块关系：

- **上游/前置**：物理机 NPU 驱动固件安装（《CANN 软件安装》文档）、Docker 部署。
- **组件依赖**：容器内含 **CANN** → **CANN-NNAL-ATB** → **MindIE** → **ATB Models** 四层软件栈，MindIE SD 实际调用 ATB Models 中的 Wan2.1 模型实现推理加速。
- **模型来源**：Wan2.1 权重来自 Hugging Face（`Wan-AI` 组织），推理代码托管在 modelers.cn（`MindIE/Wan2.1`）。
- **横向能力**：文末提及更多容器启动细节参考 `gitee.com/ascend/ascend-docker-image` 的"启动容器"章节。
- **同类推理变体**：本指南同时覆盖文生视频（T2V-14B）与图生视频（I2V-14B-480P、I2V-14B-720P）三个模型分支。

---

## 【使用方法】

**环境校验命令**（原文）：
- `npu-smi info` —— 检查 NPU 驱动固件
- `docker ps` —— 检查 Docker 运行

**容器启动命令**（原文）：
```bash
docker run -it -d --net=host --shm-size=1g \
       --name <container-name> \
       -w /home \
       --device=/dev/davinci0:rwm \
       --device=/dev/davinci1:rwm \
       --device=/dev/davinci2:rwm \
       --device=/dev/davinci3:rwm \
       --device=/dev/davinci_manager:rwm \
       --device=/dev/hisi_hdc:rwm \
       --device=/dev/devmm_svm:rwm \
       -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro \
       -v /usr/local/dcmi:/usr/local/dcmi:ro \
       -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi:ro \
       -v /usr/local/sbin/:/usr/local/sbin:ro \
       -v /path-to-weights:/path-to-weights:ro \
       mindie:3.0.0-800I-A2-py311-openeuler24.03-lts bash
```

**进入容器**（原文）：
```bash
docker exec -it <container-name> /bin/bash
```

**推理代码获取与依赖安装**（原文）：
```bash
git clone https://modelers.cn/MindIE/Wan2.1.git
cd Wan2.1
pip install -r requirements.txt
```

**关键配置项（原文）**：
- 镜像名：`mindie:3.0.0-800I-A2-py311-openeuler24.03-lts`（可按实际情况修改）。
- 权限要求：权重/配置文件 ≤ 640、所在文件夹 ≤ 750，且与执行用户所属组一致。
- 并行约束：`ulysses_size * cfg_size = nproc_per_node`，`nproc_per_node ∈ {1,2,4,8}`。
- attentioncache 开关：开启需配套 `start_step`、`attentioncache_interval`、`end_step`；关闭则无需设置。
```

## 图文联合解读

- `command_output.png`: **图文联合解读：**

**1) 图中内容：** 终端执行 `npu-smi info` 的回显，表格列出 8 个 NPU 芯片（NPU 0–7），各列字段包括 Name、Health、Power(W)、Temp(°C)、Memory-Usage(MB)、Hugepages-Usage。

**2) 技术结论：** 全部 8 卡 Health 均为 OK，功耗 95–103W，温度 48–52℃，显存占用约 3050MB / 65536MB，表明 NPU 驱动固件已正确安装且设备运行正常。

**3) 与文档关系：** 作为「前提条件」中 NPU 驱动固件安装成功与否的判定示例图，用户对照自身输出即可确认环境就绪，是后续拉取 Wan2.1 权重、部署 MindIE SD 文生视频推理的前置依据。
