# 快速入门

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/quick_start/quick_start.md

# 深度解读：MindIE 快速入门文档

---

## 【定位】

本文档是一篇面向首次使用 MindIE 推理引擎的开发者的**最小可跑通（minimal runnable）入门指南**，以 Atlas 800I A2 推理服务器 + Qwen2-7B 模型为示例，端到端串起"环境验证 → 模型准备 → 镜像获取 → 容器启动"四大前置步骤，使读者能在最短时间内完成物理机部署场景下的推理环境初始化（不涉及后续服务化配置与请求发送，因原文末尾被截断）。

---

## 【技术要点】

1. **物理机环境双校验**：通过 `npu-smi info` 检查 NPU 驱动固件（原文：图 1 为正常回显示例），通过 `docker ps` 检查 Docker 已安装且启动。
2. **模型权重获取与授权**：从 HuggingFace 拉取 Qwen2-7B 权重至服务器任意目录（如 `/home/weight/qwen2-7b`），并以 `chmod -R 755` 修改权限。
3. **一体化镜像预装栈**：昇腾官方镜像已包含 CANN、FrameworkPTAdapter、MindIE、ATB Models 四大基础组件，免去手动配置依赖链。
4. **容器启动命令中的 NPU 设备透传**：必须以 `--device=/dev/davinci*X*` 形式挂载具体 NPU 设备、davinci_manager、hisi_hdc、devmm_svm 四类设备文件。
5. **设备挂载权限关键差异**：挂载权限必须使用 `rwm` 而非 `rw` 或 `r`——对 Atlas 800I A2 而言，`rw` 在 NPU 被占用时 `npu-smi` 会报错且 `torch.npu.set_device()` 失败；对 A3 超节点服务器而言 `rw` 模式下任何调用都会失败。
6. **共享内存（`--shm-size`）与数据并行（DP）的耦合关系**：DP 增大时 `--shm-size` 必须按比例放大，原文给出 DP=2/4/8/16 时的最小值（2g/3g/5g/9g），且多模态理解模型在高并发场景下建议 `≥100g`。
7. **两种安装包形态的路径差异**：whl 包 vs run 包安装 MindIE-LLM 与 ATB Models 的路径完全不同（详见表格解读）。

---

## 【关键机制与数据】

### 镜像组件构成（原文）

容器镜像内置四大组件，构成 MindIE 推理所需的完整软件栈：

| 层级 | 组件 | 作用 |
|---|---|---|
| 驱动/底层 | CANN | 昇腾异构计算架构 |
| 加速库 | CANN-NNAL-ATB | ATB 算子加速库 |
| 推理引擎 | MindIE（含 MindIE-LLM） | 大模型推理主体 |
| 模型仓库 | ATB Models | 模型实现/适配 |

### DP 与 `--shm-size` 配比数据（原文）

原文明确给出数据并行度与最小共享内存的对应关系，体现 KV cache 等中间状态在多 DP 复制时对 `/dev/shm` 的线性放大需求：

| DP 度 | `--shm-size` 最小值 |
|---|---|
| 2 | 2g |
| 4 | 3g |
| 8 | 5g |
| 16 | 9g |
| 多模态高并发 | ≥100g |

### 设备挂载权限约束（原文）

> 原文："对于 `--device` 参数，挂载权限设置为 `rwm`，而非权限较小的 `rw` 或 `r`"

机制解释：A2 上 `rw` 在 NPU 被占用时会触发 `npu-smi` 报错与 `torch.npu.set_device()` 失败；A3 超节点上 `rw` 进入容器即报错。`m` 权限（mknod 能力）是 NPU 设备创建/dev 节点所必需。

> ⚠️ **原文截断提示**：本文档在 `-v /home/w...` 处被截断，缺少容器启动命令的剩余 `-v` 卷挂载说明、参数说明表的后续行、以及「启动容器」之后的"运行推理/服务化"等下游章节。下列解读仅基于现有原文。

---

## 【表格解读】

### 表 1（前提条件章节）：Atlas A2 推理系列产品参考文档

| 产品型号 | 参考文档 |
|---|---|
| Atlas 800I A2 | 下载[固件与驱动](https://hiascend.com/hardware/firmware-drivers/community)，安装请参考《CANN 软件安装》中的"[安装 NPU 驱动和固件](https://www.hiascend.com/document/detail/zh/canncommercial/850/softwareinst/instg/instg_0005.html?Mode=PmIns&InstallType=local&OS=openEuler)"章节（商用版）或"[安装 NPU 驱动和固件](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850/softwareinst/instg/instg_0005.html?Mode=PmIns&InstallType=local&OS=openEuler)"章节（社区版）。 |

**逐行解读**：
- **Atlas 800I A2**：本文档示例硬件。表格仅列一个产品型号，但表标题"Atlas A2 推理系列产品"暗示该系列含多个 SKU，原文未提供完整型号清单。
- **参考文档列**：提供两条安装路径——商用版走 `canncommercial` 域名，社区版走 `CANNCommunityEdition` 域名，均锚定到同一 openEuler 系统的 local 模式安装指南；还提供固件驱动下载的统一入口 `hiascend.com/hardware/firmware-drivers/community`。
- **表标题编号异常**（原文问题）：本文档使用了两个"表 1"——第一个在前提条件章节指 Atlas A2 系列产品表，第二个在容器启动章节指 docker run 参数说明表。这是原文中的标题编号冲突，下文第二个"表 1"按原文标注还原。

### 表 2：容器内各组件安装路径

| 组件 | 安装路径 |
|---|---|
| CANN | /usr/local/Ascend/cann |
| CANN-NNAL-ATB | /usr/local/Ascend/nnal/atb |
| MindIE | /usr/local/Ascend/mindie |
| ATB Models | /usr/local/Ascend/atb-models |

**逐行解读**：
- **CANN** 位于 `/usr/local/Ascend/cann`：根级软件栈，后续三个组件均依赖它。
- **CANN-NNAL-ATB** 位于 `/usr/local/Ascend/nnal/atb`：与 CANN 同级而非内置，反映 NNAL（Neural Network Acceleration Library）作为独立子模块的部署惯例。
- **MindIE** 位于 `/usr/local/Ascend/mindie`：推理引擎根目录。原文 NOTE 补充说明——whl 包形态下 MindIE-LLM 实际在 `{site_packages}/mindie_llm/`，run 包形态下在 `/usr/local/Ascend/mindie/latest/mindie-llm/`，两者拉起方式不同。
- **ATB Models** 位于 `/usr/local/Ascend/atb-models`：whl 包形态下为 `/usr/local/Ascend/atb_llm`，与 MindIE-LLM 同名/易混淆，需注意区分。

### 表 1（容器启动章节）：docker run 参数说明

> ⚠️ 原文此处亦标注为"表 1"，与上一节 Atlas A2 产品表重号，原文存在编号重复。

| 参数 | 参数说明 |
|---|---|
| -it | 表示启动一个交互式终端（`-i`）并将其连接到容器的标准输入输出（`-t`），能够与容器内部进行交互，如运行命令行操作。 |
| -d | 表示容器将以后台模式运行，即容器在后台启动。使用该参数后不会阻塞当前终端的操作，可以在启动容器后继续进行其他操作。 |
| --net | 表示容器将使用宿主机的网络配置（网络共享），使容器能够直接访问宿主机的网络接口，适用于需要进行低延迟、直接访问网络资源的场景。 |
| --shm-size | 表示指定容器的共享内存（`/dev/shm`）大小，用户可自行设置，`1g` 为示例值。对于多模态理解模型，若业务最大并发数较高，`--shm-size` 建议设置不小于 `100g`。<br>该值不能超过宿主机剩余的物理内存总量，可使用 `free -h` 命令查看。当开启数据并行（即 DP > 1 时），需要随 DP 增大调整共享内存大小：<br>当 DP=2 时，shm-size 至少为 2g<br>当 DP=4 时，shm-size 至少为 3g<br>当 DP=8 时，shm-size 至少为 5g<br>当 DP=16 时，shm-size 至少为 9g |
| --name | 表示给容器指定一个名称。`<container-name>` 是容器的标识符，可以自行设置，且在当前系统中具有唯一性。如果不设置，Docker 会自动分配一个随机名称。 |
| --device | 表示映射的设备，可以挂载一个或者多个设备。<br>需要挂载的设备如下：<ul><li>`/dev/davinci*X*`：NPU 设备，X 是 ID 号，如：`davinci0`。</li><li>`/dev/davinci_manager`：davinci 相关的管理设备。</li><li>`/dev/hisi_hdc`：hdc 相关管理设备。</li><li>`/dev/devmm_svm`：内存管理相关设备。</li></ul>可根据 `ll /dev/ \| grep davinci` 命令查询 device 个数及名称，根据需要绑定设备，修改上面命令中的 `--device=****`。 |
| -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro | 将宿主机目录 `/usr/local/Ascend/driver` 挂载到容器，请根据驱动所在实际路径修改。 |
| -v /usr/local/sbin:/usr/local/sbin:ro | 将宿主机工具 `/usr/local/sbin/` 以只读模式挂载到容器中，请根据实际情况修改。 |

**逐行解读**：
- **-it / -d**：分别提供交互式前台与后台运行模式；`docker run` 命令中两者并列使用，是后台 + TTY 的常见组合。
- **--net=host**：使用 host 网络栈，避免容器内端口映射的 NAT 开销，对推理服务的低延迟网络通信有利。
- **--shm-size**：是本表最重要的一行，其多模态高并发 `≥100g` 阈值与 DP 缩放规则是实际部署的关键决策点，且硬性约束为"不超过宿主机剩余物理内存"。
- **--name**：唯一性约束意味着同一宿主机不能同时存在两个同名容器——在多容器实验时需注意命名冲突。
- **--device**：列出 NPU 设备透传所需四类设备文件的语义：davinci* 为算力设备，davinci_manager 为设备管理面，hisi_hdc 为昇腾主机-设备通道，devmm_svm 为共享虚拟内存设备。原文给出通过 `ll /dev/ | grep davinci` 自助查询设备编号的方法。
- **两个 -v 挂载行**：均为宿主机驱动与工具以 `:ro` 只读方式透传至容器，保证容器内可调用宿主机的 npu-smi 与驱动库但不可篡改。

> ⚠️ 原文此表在 `-v /usr/local/sbin:...ro` 后被截断（行尾为"-v /home/w..."），表中其余 `-v` 卷挂载（如 `/usr/local/dcmi`、`/home/weight` 等已在 docker run 命令中体现但缺参数说明）未在表中列出。

---

## 【公式解读】

原文无数学公式或伪代码公式。

> 可视为"准公式"的**DP-shm 配比规则**以分段阈值形式表述，并非代数式，故不归入公式类，已在【关键机制与数据】与【表格解读】中保留原文数值（DP=2/4/8/16 → shm 至少 2g/3g/5g/9g；多模态高并发 → ≥100g）。

---

## 【关联】

本文档位于"用户指南 / 快速入门"路径下，作为整条 MindIE 使用链路的最上游入口：

- **前置依赖 → 内部文档**：
  - `../install/source/docker_installation.md`（前提条件章节明确"Docker 的安装可参见"该文档）——本文档假设读者已通过该文档完成 Docker 安装，因此不再展开 Docker 本身的安装步骤。

- **下游文档 → 内部文档**（依据文末提供的内部链接清单推断）：
  - `../user_manual/service_parameter_configuration.md`——本文档完成"环境与容器启动"后，下一步应进入服务化参数配置（如 model_path、tensor_parallel_size、max_batch_size 等服务启动参数），该文档承接本指南的下游。

- **外部依赖**：
  - 昇腾官方镜像仓库 `hiascend.com/developer/ascendhub/...`——提供与硬件型号匹配的 MindIE 容器镜像。
  - HuggingFace `huggingface.co/Qwen/Qwen2-7B`——模型权重源。
  - 昇固件与驱动下载页 `hiascend.com/hardware/firmware-drivers/community`——NPU 驱动固件来源。
  - CANN 软件安装指南（商用版/社区版双链接）——Atlas A2 设备的固件驱动安装指引。

- **模块关系**：
  - 文档中涉及 CANN → CANN-NNAL-ATB → MindIE（MindIE-LLM）→ ATB Models 四层组件依赖关系，体现 MindIE 不是单一可执行文件而是建立在 CANN 异构计算栈之上的整体方案。

---

## 【使用方法】

> 以下均严格依据原文命令/参数还原；末尾被截断部分以"原文未涉及"标注。

### 1. NPU 驱动固件校验（原文）

```bash
npu-smi info
```
若回显 NPU 设备列表（图 1）即已安装；否则按表 1 链接下载并安装 Atlas 800I A2 对应的固件与驱动。

### 2. Docker 状态校验（原文）

```bash
docker ps
```
若回显表头行（`CONTAINER ID IMAGE COMMAND ...`）即 Docker 已运行。

### 3. 获取模型权重（原文）

- 从 `https://huggingface.co/Qwen/Qwen2-7B/tree/main` 下载权重并上传至服务器（如 `/home/weight/qwen2-7b`）。
- 修改权限：
  ```bash
  chmod -R 755 /home/weight/qwen2-7b
  ```

### 4. 获取容器镜像（原文）

进入昇腾官方镜像仓库（`https://www.hiascend.com/developer/ascendhub/detail/af85b724a7e5469ebd7ea13c3439d48f`），按设备型号下载对应 MindIE 镜像，使用 `docker images` 查询 `{IMAGE_ID}`。

### 5. 启动容器（原文，被截断）

```bash
docker run -it -d --net=host --shm-size=500g \
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
       -v /home/weight:/home/weight:ro \
       {IMAGE_ID} bash
```

**关键参数替换指引**（原文）：
- `{IMAGE_ID}` → 用 `docker images` 查到的实际镜像 ID 替换。
- `<container-name>` → 自定义容器名称（必须唯一）。
- `--device` 中的 davinci 编号 → 按 `ll /dev/ | grep davinci` 实际结果增减。
- `--shm-size=500g` → 原文示例值；按 DP 与多模态需求调整（参见表 1 的 DP 配比与 ≥100g 多模态建议）。
- `--device` 权限必须保留 `rwm` 后缀。
- 所有 `-v` 的宿主机路径需根据实际安装位置调整。

### 6. 后续步骤（原文未涉及）

启动容器后的"进入容器执行 MindIE-LLM 服务化 → 发送推理请求 → 查看日志/调参"等步骤，原文因截断未提供；按内部链接关系，下游应参见 `../user_manual/service_parameter_configuration.md`。

## 图文联合解读

- `command_output.png`: **图示内容**：终端执行 `npu-smi info` 的回显，以表格列出 8 颗 NPU 芯片（编号 0–7）的状态，关键字段包括 Health（全部 OK）、Bus-Id（如 0000:C1:00.0）、Power（95–102W）、Temp（48–52℃）、AICore%、Hugepages-Usage 与 HBM-Usage（约 3050/65536 MB）。

**技术结论**：NPU 驱动固件已正确安装，8 卡全部在线健康，功耗、温度、显存占用均处于正常空闲基线，可直接用于后续推理部署。

**与文档关系**：作为「图 1」印证「前提条件」中"驱动固件已安装"的判断依据，读者比对回显即可确认环境就绪。
