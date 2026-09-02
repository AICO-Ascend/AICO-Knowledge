# msprof-analyze 快速入门

> 仓 `msprof-analyze` · 路径 `docs/zh/quick_start/msprof-analyze_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprof-analyze/docs/zh/quick_start/msprof-analyze_quick_start.md

# msprof-analyze 快速入门 深度解读

---

## 【定位】

本篇文档为 msprof-analyze（一款面向昇腾 AI 处理器性能数据的自动分析工具）的快速入门手册：以"一次完整的性能诊断"为示例串联**环境准备 → 性能数据采集 → Advisor 自动分析 → 报告查看**四个环节，目标是让用户在约 10 分钟核心操作时间内跑通端到端流程。

---

## 【技术要点】

1. **强制标准化 CANN 容器环境**：教程明确仅支持在标准化 CANN 容器中执行，不支持裸机、虚拟机或其他非标准容器；前置硬件要求"至少 1 张 NPU 卡，驱动与固件已安装"，Docker ≥ 18.0，宿主机 Python 3、curl。
2. **基于 PCI ID 自动识别芯片**：通过 `lspci -n -D | grep -o '19e5:d[0-9a-f]\{3\}'` 读取 NPU 厂商 ID `19e5` 与设备 ID，按设备号映射芯片系列——`d500→310P`、`d802→910B`、`d803→A3`、`d806→950`，并将匹配的 CANN 镜像写入环境变量 `MY_STUDY_VAR_CANN_IMAGE` 与芯片名变量 `MY_CHIP_NAME`。
3. **固定镜像与依赖版本**：CANN 镜像全部锁定在 **9.0.0** 版本，配套 base OS 为 openeuler 24.03、Python 3.11；Python 依赖锁定 `networkx==3.6.1`、`pillow==12.2.0`、CPU 版 `torch==2.7.1+cpu`、`torchvision==0.22.1`、`torch_npu-2.7.1.post4`；最终通过 `pip3 install -U msprof-analyze` 安装分析工具本体。
4. **示例训练脚本特性**：以 ResNet50（仅 `fc` 层可训练，其余参数冻结）+ Adam(lr=1e-3) + CrossEntropyLoss + 随机 Tensor 数据集 `(80,3,224,224)`、batch_size=8 训练 5 个 epoch，并通过脚本自动 `npu-smi info` 查找空闲 NPU。
5. **Ascend PyTorch Profiler 采集配置**：`activities` 同时采集 CPU 与 NPU；`schedule(wait=0, warmup=1, active=3, repeat=1)` 表示跳过 0 步、预热 1 步、采集 3 步、重复 1 次；`export_type` 同时输出 Text 与 Db；`profiler_level=Level1`；`aic_metrics=AiCoreNone`；输出回调为 `tensorboard_trace_handler("~/result")`。
6. **Advisor 一键分析与产物**：`msprof-analyze advisor all -d "${PROF_DIR}" -o "${HOME}/advisor_output"` 对采集目录执行全维度专家建议分析，产物包含 HTML 报告与 XLSX 明细文件；分析输入为 `*_ascend_pt` 目录（内含 `analysis.db`、`kernel_details.csv`、`operator_details.csv`、`op_statistic.csv`、`step_trace_time.csv`、`trace_view.json` 等）。

---

## 【关键机制与数据】

**工作原理（自动识别镜像，原理分三步）**：
> 原文：「① 读取 NPU PCI ID → ② 匹配镜像版本 → ③ 写入环境变量供后续流程使用」

**端到端数据流**：

```
宿主机 (lspci 识别芯片)
   ↓ docker pull ${MY_STUDY_VAR_CANN_IMAGE}
   ↓ ~/ctr_in.py 启动容器
容器内
   ↓ pip3 install 依赖 + msprof-analyze
   ↓ python3 ~/train_sample.py (ResNet50 5 epoch + Ascend Profiler)
~/result/msprof_<ts>_ascend_pt/  (含 ASCEND_PROFILER_OUTPUT, FRAMEWORK, PROF_XXX)
   ↓ msprof-analyze advisor all -d "${PROF_DIR}" -o "${HOME}/advisor_output"
~/advisor_output/  (HTML 报告 + XLSX 明细)
```

**示例训练实测数据（原文输出截取）**：

| 时间点 | 数据 |
|---|---|
| Epoch 1 平均 Loss | 2.5849 |
| Epoch 2 平均 Loss | 2.5526 |
| Epoch 3 平均 Loss | 2.2174 |
| Epoch 4 平均 Loss | 2.0562 |
| Epoch 5 平均 Loss | 1.9166 |
| CANN profiling 数据解析耗时 | 0:00:08.090306 |
| All profiling data parsed 总耗时 | 0:00:12.392744 |
| Profiling 完成时间戳示例 | 2026-03-24 03:44:40 ~ 03:44:53 |

**关于分析维度**：`msprof-analyze advisor all` 中的 `all` 表示执行全部检查项；该命令的详细说明、可选项与各检查项的语义被链接到 `../user_guide/advisor_instruct.md`。

---

## 【表格解读】

### 表 1：体验地图（步骤—环节—核心工具—耗时）

| 步骤 | 环节 | 核心工具 | 参考操作耗时 | 建议原理学习耗时 |
| :---: | :--- | :--- | :------: | :---: |
| **1** | **环境准备** | CANN 容器环境 | 5 分钟 | 5 分钟 |
| **2** | **性能数据采集** | Ascend PyTorch Profiler | 2 分钟 | 10 分钟 |
| **3** | **自动分析与报告查看** | msprof-analyze Advisor | 3 分钟 | 10 分钟 |

**逐行解读**：
- 第 1 行（环境准备）：操作 5 分钟 + 原理 5 分钟等权重，说明环境本身简单但理解镜像与 PCI 识别逻辑有助于排错。
- 第 2 行（采集）：操作仅需 2 分钟但原理学习需 10 分钟——表明脚本已封装好了 Profiler，**重在理解 Profiler schedule 与 export_type 的含义**（wait/warmup/active/repeat、Text/Db、Level1）。
- 第 3 行（分析）：操作 3 分钟、原理 10 分钟，对应 Advisor 命令虽简单，但其底层各检查项（专家建议规则）需要另行阅读 advisor_instruct 才能理解。

### 表 2：前置条件清单

| 项目 | 要求 | 验证方法 |
| --- | --- | --- |
| **硬件算力** | Linux 服务器配备至少 1 张 NPU 卡，驱动与固件已安装 | 执行 `npu-smi info`，确认 NPU 卡状态正常 |
| **容器运行** | 已安装并运行 Docker（建议版本 ≥ 18.0） | 执行 `docker ps`，无报错即表示服务正常启动 |
| **脚本执行** | 宿主机已安装 Python 3 | 在宿主机执行 `python3 -V`，有版本信息输出即表示已安装 |
| **网络通信** | 已安装 curl（任意版本） | 执行 `curl -V`，有版本信息输出即表示已安装 |

**逐行解读**：
- **硬件算力**：NPU 卡是性能数据采集的物理基础；`npu-smi info` 同时被示例脚本用于"自动查找空闲 NPU"。
- **容器运行**：版本下限 18.0 保证了 docker exec/run 的基础兼容性。
- **脚本执行**：宿主机 Python 仅用于执行 `ctr_in.py` 与辅助命令（不一定需要 NPU 版 torch）。
- **网络通信**：curl 用于下载 `ctr_in.py` 和 PyTorch wheel。

---

## 【公式解读】

**原文无公式**。文档涉及的关键参数化结构是 bash `case` 表达式（PCI ID → 镜像名映射）与 Profiler `schedule(wait, warmup, active, repeat)`，但均为命令/参数形式而非数学公式，故不进行 LaTeX 还原。

如需保留参数语义：
- Profiler schedule：`wait=0, warmup=1, active=3, repeat=1` —— 含义是跳过 0 个 step、预热 1 个 step、采集 3 个 step、整体重复 1 次（仅触发一次"wait→warmup→active"循环）。
- 设备识别映射：`{d500→310P, d802→910B, d803→A3, d806→950}` —— 含义是 PCI 设备 ID 末 4 位十六进制分别对应 4 个昇腾芯片系列。

---

## 【关联】

文档在以下环节链接到仓库其他模块，构成完整学习路径：

| 文中位置 | 内部链接 | 关系定位 |
|---|---|---|
| 第 2.3 节「执行 Advisor 分析」命令语义说明 | `../user_guide/advisor_instruct.md` | **advisor all** 的全量检查项、各维度含义、输出报告结构详解 |
| 体验地图与第 2.3 节均引用 | `../user_guide/advisor_instruct.md`（再次出现） | 同上，作为主用分析入口的官方详细文档 |
| 文中提及"msprof-analyze 多种分析能力" | `../user_guide/compare_tool_instruct.md` | **对比分析工具**：用于多次 profiling 结果对比 |
| 文中提及"集群/多 device 分析能力" | `../user_guide/cluster_analyse_instruct.md` | **集群分析工具**：用于多 NPU/多节点场景 |
| 文末"高级特性"引导 | `../advanced_features/README.md` | **进阶特性入口**：自定义检查项、扩展分析维度等 |

**逻辑链路**：`quick_start`（本文，跑通流程）→ `advisor_instruct`（深入 Advisor 各维度）→ `compare_tool_instruct`（横向多次对比）→ `cluster_analyse_instruct`（纵向集群维度）→ `advanced_features`（自定义扩展）。本文是整条 msprof-analyze 文档树的**最浅入口**。

---

## 【使用方法】

> 原文命令均按章节标注；以下为完整复盘（所有命令均需在容器内或宿主机对应位置执行）。

### A. 环境准备阶段（宿主机 + 容器内）

```bash
# A1. 宿主机：自动识别芯片并写入环境变量
source /dev/stdin <<< "$(dev_id=$(lspci -n -D | grep -o '19e5:d[0-9a-f]\{3\}' | head -n1 | cut -d: -f2); case "$dev_id" in ...)"

# A2. 宿主机：拉取镜像
docker pull ${MY_STUDY_VAR_CANN_IMAGE}

# A3. 宿主机：下载并赋权容器启动脚本
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py

# A4. 宿主机：启动容器
~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}

# A5. 容器内：安装依赖
pip3 install networkx==3.6.1 pillow==12.2.0
pip3 install https://inst.obs.cn-north-4.myhuaweicloud.com/env/mirror/$(arch)/download.pytorch.org/whl/cpu/torch-2.7.1%2Bcpu-cp311-cp311-manylinux_2_28_$(arch).whl
pip3 install torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cpu
pip3 install https://gitcode.com/Ascend/pytorch/releases/download/v26.0.0-pytorch2.7.1/torch_npu-2.7.1.post4-cp311-cp311-manylinux_2_28_$(arch).whl
pip3 install -U msprof-analyze

# A6. 容器内：环境验证
python3 -c 'import torch, torch_npu, torchvision; assert torch.npu.is_available(), "NPU is unavailable"; print("PyTorch:", torch.__version__)' && msprof-analyze --help >/dev/null && echo -e "\e[32m[PASS] NPU environment and msprof-analyze check passed.\e[0m"
```

### B. 性能数据采集阶段（容器内）

```bash
# B1. 生成示例训练脚本（ResNet50 + 5 epoch + Ascend Profiler）
cat > ~/train_sample.py << 'EOF'
# (原文中的 train_sample.py 内容)
EOF

# B2. 启动训练与采集
python3 ~/train_sample.py

# B3. 查看采集结果目录
PROF_DIR=$(ls -dt "${HOME}"/result/*_ascend_pt | head -n 1)
echo "${PROF_DIR}"
tree -L 2 "${PROF_DIR}"
```

### C. Advisor 自动分析（容器内）

```bash
msprof-analyze advisor all -d "${PROF_DIR}" -o "${HOME}/advisor_output"
```

- `-d`：Profiling 数据目录（必须以 `_ascend_pt` 结尾的目录）。
- `-o`：报告输出目录，将生成 HTML 报告与 XLSX 明细文件。

### D. 查看分析结果（容器内）

```bash
tree -L 2 "${HOME}/advisor_output"
# （原文此节在 "tree -L 2 "${HOME}/adv" 处截断，后续 HTML 浏览器打开与 XLSX 明细查阅命令原文未给出）
```

### E. 配置项/关键开关（原文已明确）

| 配置位 | 取值 | 含义 |
|---|---|---|
| `MY_STUDY_VAR_CANN_IMAGE` | 镜像地址 | 通过 PCI ID 自动写入的环境变量 |
| `MY_CHIP_NAME` | 310P / 910B / A3 / 950 | 自动识别的芯片名 |
| Profiler `schedule` | `wait=0, warmup=1, active=3, repeat=1` | 采集步数控制 |
| Profiler `export_type` | `[Text, Db]` | 同时输出文本与数据库格式 |
| Profiler `profiler_level` | `Level1` | 采集层级（Level1） |
| Profiler `aic_metrics` | `AiCoreNone` | AICore 指标采集（None 表示不采集细粒度指标） |
| Profiler `activities` | `[CPU, NPU]` | 同时采集 CPU 与 NPU 端 |
| `msprof-analyze advisor` | `all` | 执行全部 Advisor 检查项 |

> 原文未涉及：自定义 Advisor 检查项开关（如 `--disable`、`--type` 等更细粒度筛选）——这些配置项位于 `../user_guide/advisor_instruct.md`，本文作为 quick start 仅演示 `all` 全量模式。

## 图文联合解读

- `quick_start_dataloader.png`: **图文联合解读：**

1) **图像内容**：Advisor 报告页"Performance Optimization Suggestions"，按"overall → performance problem analysis → dataloader/schedule"层级展示；高/中/低优先级用红/黄/绿标注，其中"Slow Dataloader Issues"标红，附数据（244193.88us/iter，远超10000us阈值）及两条建议（磁盘I/O、调num_workers）。

2) **技术结论**：Advisor 自动定位本次性能瓶颈为 DataLoader 加载耗时过高（约为正常值24倍），并给出可执行优化项。

3) **与文档关系**：对应快速入门第3步"自动分析与报告查看"，验证 msprof-analyze 能从采集数据中自动识别瓶颈并输出分级建议，支撑"10分钟完成端到端诊断"的论点。
