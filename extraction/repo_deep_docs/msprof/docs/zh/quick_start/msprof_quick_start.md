# msProf 快速入门

> 仓 `msprof` · 路径 `docs/zh/quick_start/msprof_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprof/docs/zh/quick_start/msprof_quick_start.md

# msprof 快速入门文档深度解读

---

## 【定位】

本篇文档是 **msProf（MindStudio Profiler）面向昇腾 AI 处理器的 10 分钟端到端性能数据采集与分析快速上手指南**，通过"环境准备 → 数据采集与 CSV 查看 → 可视化分析（可选）"三段闭环流程，让初次用户在一个标准化的 CANN 容器内完整跑通一次 ResNet50 训练的性能剖析链路。

---

## 【技术要点】

1. **三段式体验地图（约 10 分钟）**：环境准备 5 分钟（必做）→ msProf 命令行采集与 CSV 查看 2 分钟 → MindStudio Insight 可视化分析 3 分钟（可选），对应核心工具分别为 CANN 容器、msProf CLI、MindStudio Insight。  
2. **强制运行环境约束**：教程**仅支持**在标准化 CANN 容器内执行，**不支持**裸机、虚拟机或其他非标准容器；硬件仅支持昇腾 **310P、A2、A3、950** 系列（通过 `lspci` 的 PCI ID 后 4 位进行匹配：`d500→310P`、`d802→910B`、`d803→A3`、`d806→950`，其它均判定为 `[FAIL]`）。  
3. **环境变量自动注入机制**：通过 `source /dev/stdin <<< "..."` 一次性完成"读取 NPU PCI ID → 匹配镜像版本 → 写入 `MY_STUDY_VAR_CANN_IMAGE` 与 `MY_CHIP_NAME`"，从而驱动后续 `docker pull`、`~/ctr_in.py`、`pip3 install` 等命令无需手动拼接。  
4. **依赖锁定版本**：容器内安装固定组合 `networkx==3.6.1`、`pillow==12.2.0`、`torch==2.7.1+cpu`（cp311、manylinux_2_28）、`torchvision==0.22.1`、`torch_npu-2.7.1.post4`，配套镜像基线为 CANN `9.0.0-* -openeuler24.03-py3.11-devel`。  
5. **采集与解析合一的 CLI 入口**：`msprof --application="python3 ${HOME}/train.py" --output=${HOME}/prof_output` 一次性完成"启动训练 + 采集 + 自动解析 + 导出"，无需额外解命令；输出目录命名遵循 `PROF_<id>_<timestamp>_<hash>` 规则（示例：`PROF_000001_20260323031749197_00815596RKPKAHRB`），最终落盘于 `/home/prof_output/PROF_*/` 之下。  
6. **自动空闲设备探测与训练脚本模板**：示例代码 `~/train.py` 通过解析 `npu-smi info` 输出中的 `No running processes found in NPU\s+(\d+)` 正则动态挑选空闲 NPU；以 ResNet50 在 `npu:{device}` 上跑 **2 个 epoch**、**batch_size=8**、**lr=1e-3**、**freeze_backbone=True**，数据集为随机生成的 80 张 3×224×224 图像与 10 分类标签，仅用于产出可剖析的负载而非追求精度。  
7. **结果查看方式**：`PROF_DIR=$(ls -dt "${HOME}"/prof_output/PROF_* | head -n 1)` 获取最新目录，配合 `tree -L 1` 同时查看 `PROF_XXX` 与 `mindstudio_profiler_output` 两层；后者核心文件为 `msprof_{timestamp}.json`（Chrome Trace Timeline）、`op_statistic_{timestamp}.csv`（按算子类型聚合）、`op_summary_{timestamp}.csv`（AI Core / AI CPU 明算）。

---

## 【关键机制与数据】

- **数据流（原文）：** `train.py`（ResNet50 训练）→ msProf CLI 包装 `python3 ${HOME}/train.py` 启动 → 在 host/device 双侧采集原始 trace → 自动解析 → 输出到 `${HOME}/prof_output/PROF_<id>_<ts>_<hash>/`，其中 `host/data` 与 `device_{id}/data` 为原始性能数据（快速入门阶段通常无需关注），`msprof_{timestamp}.db` 为数据库格式汇总，`mindstudio_profiler_output/` 下导出 JSON 时间线与两类 CSV。  
- **采集落盘信息（原文）：** 日志显示采集会产生 host 与 `device_0` 两条 Job Info 行，时间戳示例为 `2026-03-23 03:17:50.944273`（host）与 `2026-03-23 03:17:50.954390`（device_0），Model ID / Iteration Number / Top Time Iteration / Rank ID 字段在示例中均为 `N/A` 或 `-1`，最终保存路径为 `/home/prof_output/PROF_000001_20260323031749197_00815596RKPKAHRB`。  
- **示例损失数据（原文）：** `[Epoch 1/2] Average Loss: 2.4961`、`[Epoch 2/2] Average Loss: 2.2166`，仅用于演示剖析链路，并非训练质量指标。  
- **超时判定（原文）：** 若超过 **5 分钟**不出现 `Profiling finished`，提示 NPU 异常或被抢占，需重新执行或更换空闲 NPU。  
- **典型结果分析动作（原文）：** 对 `op_statistic_*.csv` 按 `Total Time(us)` 降序排列，优先关注耗时占比高的算子类型，评估其优化潜力（字段随产品版本和采集参数变化，示例仅供学习参考）。

---

## 【表格解读】

### 表 1：体验地图（核心操作约需 10 分钟）

> 原文逐字还原：

| 步骤 | 环节 | 核心工具 | 参考操作耗时 | 建议原理学习耗时 |
|:---:|:---|:---|:---:|:---:|
| **1** | **环境准备** | CANN 容器环境 | 5 分钟 | 5 分钟 |
| **2** | **数据采集与 CSV 结果查看** | msProf 命令行工具 | 2 分钟 | 10 分钟 |
| **3** | **可视化性能分析（可选）** | MindStudio Insight | 3 分钟 | 10 分钟 |

**解读**：该表为整篇文档的"路线图"。第 1 步是必做的环境前置（约 5 分钟）；第 2 步通过 msProf CLI 完成采集+解析+CSV 导出（约 2 分钟操作 + 10 分钟原理学习）；第 3 步是可选的 Insight 可视化（3 分钟操作 + 10 分钟原理学习）。三步合计操作约 10 分钟，原理学习合计约 25 分钟，提示用户"操作可快、理解需慢"。

### 表 2：前置条件

> 原文逐字还原：

| 项目 | 要求 | 验证方法 |
|---|---|---|
| **硬件算力** | Linux 服务器配备至少 1 张 NPU 卡，驱动与固件已安装 | 执行 `npu-smi info`，确认 NPU 卡状态正常 |
| **容器运行** | 已安装并运行 Docker（建议版本 ≥ 18.0） | 执行 `docker ps`，无报错即表示服务正常启动 |
| **脚本执行** | 宿主机已安装 Python 3 | 在宿主机执行 `python3 -V`，有版本信息输出即表示已安装 |
| **网络通信** | 已安装 curl（任意版本） | 执行 `curl -V`，有版本信息输出即表示已安装 |

**解读**：该表列出 4 项前置检查：① 至少 1 张 NPU 卡且驱动固件就绪（验证命令 `npu-smi info`）；② Docker ≥ 18.0（验证 `docker ps`）；③ 宿主机 Python 3（验证 `python3 -V`）；④ 任意版本 curl（验证 `curl -V`）。四项通过后即可 Copy/Paste 后续命令，避免输入错误。

### 表 3：输出目录结构（目录树，code block）

> 原文逐字还原（非 markdown 表格，但作为结构化清单保留）：

```
PROF_XXX
├── host                        # Host 侧性能原始数据，快速入门阶段通常无需关注
│   └── data
├── device_{id}                 # Device 侧性能原始数据，快速入门阶段通常无需关注
│   └── data
├── msprof_{timestamp}.db       # 数据库格式的性能数据
└── mindstudio_profiler_output  # Host 侧和各 Device 侧性能数据汇总
    ├── msprof_{timestamp}.json         # Chrome Trace 格式的 Timeline 数据
    ├── op_statistic_{timestamp}.csv    # 按算子类型聚合的统计数据
    ├── op_summary_{timestamp}.csv      # AI Core 和 AI CPU 算子明细数据
    └── ...
```

**解读**：`PROF_XXX` 是同时承载"原始数据 + 解析导出结果"的根目录。第一层 `host/data` 与 `device_{id}/data` 是 host/device 双侧原始性能二进制，快速入门阶段通常无需关心；第二层是面向用户的分析层：`msprof_{timestamp}.db` 提供数据库查询入口；`mindstudio_profiler_output/` 下的 `msprof_{timestamp}.json` 可在 Chrome `tracing` 页加载做时间线分析，`op_statistic_*.csv` 用于按类型聚合排查瓶颈，`op_summary_*.csv` 用于 AI Core / AI CPU 算子级明细定位。`...` 表示实际文件随采集内容/导出类型动态变化。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **内嵌外部链接**：文档指向华为云 AscendHub 上的 [CANN 官方镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884)，用于了解 `MY_STUDY_VAR_CANN_IMAGE` 所选镜像的版本与组成。
- **本章节内部跳转**：
  - `#31-docker-镜像在隔离内网的获取方法` —— 当 `docker pull` 在企业内网失败时的备选方案（位于本篇第 3.1 节）；
  - `#32-传输容器启动脚本` —— `ctr_in.py` 因网络限制无法下载时的备选方案（位于本篇第 3.2 节）；
  - `#33-离线安装-python-依赖` —— 当 `pip3 install` 在企业内网失败时的备选方案（位于本篇第 3.3 节）；
  - `#212-宿主机自动识别并配置镜像环境变量` —— 当容器启动报错或出现选择界面时，回溯检查 PCI ID 自动识别是否输出 `[PASS]`。
- **上下游关联文档**（按提供的内部链接）：
  - `../user_guide/profile_data_file_references.md` —— **profile_data_file_references.md**：定位为"`PROF_XXX` 目录内各种性能数据文件的字段含义与引用关系参考"。本篇的 `tree -L 1` 输出、`op_statistic_*.csv`、`op_summary_*.csv`、`msprof_*.json`、`msprof_*.db` 等文件，都需要在该文档中查阅每一种文件的字段定义、生成条件与使用场景，是从"能跑出来"过渡到"看得懂每一列含义"的关键下游文档。
- **关联工具链**：CANN 容器（运行环境） → msProf CLI（采集与解析） → MindStudio Insight（可视化），三者在本文体验地图里被显式串联为三步。

---

## 【使用方法】

### 启用方式（原文流程）

1. **宿主机（环境识别）**：执行"自动识别并配置镜像环境变量"命令，预期看到 `[PASS] Successfully identified chip [...] and auto-selected image: ...`。
2. **宿主机（拉镜像）**：`docker pull ${MY_STUDY_VAR_CANN_IMAGE}`。
3. **宿主机（下载启动脚本）**：`cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py`。
4. **宿主机（启动容器）**：`~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}`，预期进入 `[root@xxxxxx ~]#` 提示符。
5. **容器内（安装 Python 依赖）**：
   ```bash
   pip3 install networkx==3.6.1 pillow==12.2.0
   pip3 install https://inst.obs.cn-north-4.myhuaweicloud.com/env/mirror/$(arch)/download.pytorch.org/whl/cpu/torch-2.7.1%2Bcpu-cp311-cp311-manylinux_2_28_$(arch).whl
   pip3 install torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cpu
   pip3 install https://gitcode.com/Ascend/pytorch/releases/download/v26.0.0-pytorch2.7.1/torch_npu-2.7.1.post4-cp311-cp311-manylinux_2_28_$(arch).whl
   ```
6. **容器内（环境校验）**：`python3 -c 'import torch, torch_npu, torchvision; assert torch.npu.is_available(), "NPU is unavailable"; print("PyTorch:", torch.__version__)' && echo -e "\e[32m[PASS] NPU environment check passed.\e[0m"`。
7. **容器内（生成训练脚本）**：`cat > ~/train.py << 'EOF' ... EOF`，脚本会自动 `find_idle_npu()` 选取设备；如需指定 NPU，将 `find_idle_npu()` 替换为编号（如 `0`）。

### 核心配置项/命令（原文）

- **采集入口命令**：`msprof --application="python3 ${HOME}/train.py" --output=${HOME}/prof_output`
  - `--application`：被剖析的应用入口，本例为 `python3 ${HOME}/train.py`；
  - `--output`：剖析结果的输出根目录，本例为 `${HOME}/prof_output`。
- **结果查看命令**：
  ```bash
  PROF_DIR=$(ls -dt "${HOME}"/prof_output/PROF_* | head -n 1)
  echo "${PROF_DIR}"
  tree -L 1 "${PROF_DIR}"
  tree -L 1 "${PROF_DIR}/mindstudio_profiler_output"
  ```
  用于按时间倒序取最新 `PROF_*` 目录并打印一二级结构。
- **企业内网失败时的备选（原文指向 3.1/3.2/3.3 节）**：原文未涉及具体离线镜像/脚本/依赖包内容，仅以链接形式给出。

### 注意事项（原文）

- ⚠️ 跳过"环境准备"会导致后续多项操作失败；
- ⚠️ 仅在标准化 CANN 容器内执行，不支持裸机/虚拟机/其他容器；
- ⚠️ 若 5 分钟内未出现 `Profiling finished`，视为异常，需更换设备重试；
- ⚠️ 默认 `find_idle_npu()` 自动选空闲 NPU；多 NPU 抢占时可手动指定设备编号。

## 图文联合解读

- `zh-cn_image_0000002534398593.png`: **1) 图示内容：** 一张 CSV 算子性能表，列出 Device id、OP Type（TransData/Conv2D/BatchNormV3 等）、Core Type（AI_VECTOR_CORE / MIX_AIV）、Count、Total/Min/Avg/Max Time(us) 及 Ratio(%)，TransData 占比最高(39.45%)。

**2) 技术结论：** msProf 在昇腾 NPU 上按算子粒度采集核类型、调用次数与耗时统计，支持热点定位（向量核为主、含少量 MixAIV）。

**3) 与文档关系：** 对应第 2 步"数据采集与 CSV 结果查看"，展示命令行采集后的可读结果样例。
- `zh-cn_image_0000002502718556.png`: **1) 图示内容**：msProf 输出的 CSV 结果表，含 Device_id/Task ID/Stream ID/OP Name（如 Conv2D、trans_TransData、aclnnBatchNorm）/Task Type（AI_VECTOR、AI_CORE）/Task Start、Task Dur（μs）/Input·Output Shape 与 Format（NCHW、FLOAT）等列，逐行列出各算子的时延、阻塞、Shape 流向。

**2) 技术结论**：msProf 能以算子粒度采集昇腾 NPU 上 AI 任务的 Task 类型、起止时间、Dura­tion、Block 阻塞、输入/输出 Tensor 的 Shape 与 Format，量化呈现算子级性能瓶颈与数据搬运开销。

**3) 与文档关系**：对应快速入门"步骤 2——数据采集与 CSV 结果查看"的成果展示，证明 msProf 命令行输出可直接用于定位算子耗时与瓶颈。
- `zh-cn_image_0000002502558722.png`: ## 图文联合解读

**① 图中内容**
图为 MindStudio Insight 的 Timeline 视图，标注三个区域：
- **区域一**（软件层）：CANN 节点下的 CPU 线程（Thread 809060/809566/809567/809935），展示 `aclInplaceRelu`、`Node@launch`、`MaxPool2dWithMaskGetWorkspaceSize` 等 API 调用与算子调度的时间条。
- **区域二**（硬件层）：Ascend Hardware 的 NPU 0，含 Stream 46、Stream 49，呈现算子在设备侧的执行流。
- **区域三**（详情面板）：选中条目的 Slice Detail，显示 Title=aclnnInplaceRelu_Relu_Relu，Wall Duration=14μs800ns，Task Type=AI_VECTOR_CORE，Physic Stream Id=46。

**② 技术结论**
视图通过时间轴对齐，建立了"Host API 调用 → 调度下发 → NPU Stream 执行"的三级映射；用户可在微秒级粒度从宏观调用链钻取到单算子的硬件执行信息。

**③ 与文档关系**
对应"体验地图"第 3 步**可视化性能分析**，印证 msProf 采集的数据可经 MindStudio Insight 实现端到端溯源分析。
