# msProbe PyTorch 场景快速入门

> 仓 `msprobe` · 路径 `docs/zh/quick_start/pytorch_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprobe/docs/zh/quick_start/pytorch_quick_start.md

# msProbe PyTorch 场景快速入门 深度解读

## 【定位】

这篇文档是 msProbe（MindStudio Probe）在 PyTorch 框架下的快速入门指南，以 ResNet-50 模型训练为例，端到端演示 NPU/GPU 数据采集、精度比对及分级可视化构图比对的标准流程，帮助用户掌握数值溢出、Loss 异常、模型不收敛等典型精度问题的排查方法。

---

## 【技术要点】

1. **标准化容器前置约束**：NPU 侧操作仅支持在标准化 CANN 容器内执行，不支持裸机、虚拟机或非标准容器；通过 `lspci -n -D` 读取 PCI Device ID 自动匹配 CANN 镜像，支持昇腾 310P（`d500`）、910B（`d802`）、A3（`d803`）、950（`d806`）四款芯片。

2. **环境变量驱动的镜像自适配**：通过 `MY_STUDY_VAR_CANN_IMAGE` 和 `MY_CHIP_NAME` 两个环境变量解耦"硬件识别→镜像选择→容器启动"链路，镜像地址全部来自华为云 AscendHub 的 CANN 官方仓库。

3. **基于 `statistics` 任务的轻量采集**：`config.json` 中 `task="statistics"`、`async_dump=false`、`level="mix"`、`step=[0,1]`，仅保存 Tensor 统计量不保存完整 Tensor 数据，目标是"同时支持精度比对和分级可视化构图比对"，降低磁盘占用。

4. **`PrecisionDebugger` 三段式集成**：训练循环中按 `debugger.start(model)` → 前向/反向训练 → `debugger.stop()` → `debugger.step()` 调用，配合 `seed_all(seed=1234, mode=True)` 固定随机种子，保证 NPU 与 GPU 端数据可对齐比对。

5. **训练采样参数**：使用 `torchvision.datasets.FakeData` 构造 1,281,167 张训练样本、50,000 张验证样本，`batch_size=32`、`num_workers=4`、`pin_memory=True`，SGD 优化器 `lr=0.1`、`momentum=0.9`、`weight_decay=1e-4`，`StepLR(step_size=30, gamma=0.1)`。

6. **依赖版本钉死**：Python 3.11 环境，`torch==2.7.1+cpu`、`torch_npu==2.7.1.post4`、`torchvision==0.22.1`、`networkx==3.6.1`、`pillow==12.2.0`，Torch 通过华为云 obs 镜像安装 CPU 版以避免误装 GPU 版冲突。

---

## 【关键机制与数据】

**工作原理与数据流（原文）：**

- **硬件识别 → 镜像选择（原文）**：脚本先执行 `lspci -n -D | grep -o '19e5:d[0-9a-f]\{3\}' | head -n1 | cut -d: -f2` 提取 NPU PCI ID，再以 `case` 分支匹配 `d500/d802/d803/d806` 四个 Device ID，分别写入对应的 `MY_STUDY_VAR_CANN_IMAGE`（CANN 9.0.0 系列）和 `MY_CHIP_NAME`；若未命中则 `unset` 两个变量并输出红色 `[FAIL]`。

- **采集数据落盘路径（原文）**：默认采集目录为 `${HOME}/msprobe_dump_npu`，单卡训练下数据存放在 `proc{pid}` 子目录，多卡训练下存放在 `rank{id}` 子目录，每个 step 目录下包含 `construct.json` 与 `dump.json`（原文结尾被截断，未给出完整树）。

- **采集步骤控制（原文）**：`step=[0, 1]` 表明 msProbe 仅在第 0、1 两个迭代触发采集并打印 `dump.json is at /root/msprobe_dump_npu/step1` 等 INFO 日志；从 step2 起停止采集，仅剩训练脚本自身日志（如 `Current Step: 10 (Progress: 0.01%)`），此时按 `Ctrl + C` 终止不会破坏已落盘数据。

- **环境验证链路（原文）**：`python3 -c '...'` 同时验证 `torch.npu.is_available()`、`msprobe` 导入、`tensorboard --help`，三者全部通过才会输出绿色 `[PASS] NPU environment, msProbe and TensorBoard check passed.`，否则整条命令以非 0 退出。

**性能/耗时数据（原文）：**

| 步骤 | 操作耗时 | 原理学习 |
| :---: | :---: | :---: |
| 环境准备 | 5 min | 5 min |
| NPU 数据采集 | 1 min | 10 min |
| GPU 标杆采集 | 0.5 min | 5 min |
| 精度比对 | 1 min | 10 min |
| 可视化构图比对 | 2 min | 10 min |

全流程核心操作约需 10 分钟，原文指出"基于 ResNet-50 + FakeData 训练"以保证可复现。

---

## 【表格解读】

### 表 1：体验地图

| 步骤 | 环节 | 核心工具 | 操作耗时 | 原理学习 |
| :---: | :--- | :--- | :---: | :---: |
| 1 | 环境准备 | CANN 容器 | 5 min | 5 min |
| 2 | NPU 数据采集 | PrecisionDebugger | 1 min | 10 min |
| 3 | GPU 标杆采集 | PrecisionDebugger | 0.5 min | 5 min |
| 4 | 精度比对 | msProbe compare | 1 min | 10 min |
| 5 | 可视化构图比对 | graph_visualize / TensorBoard | 2 min | 10 min |

**逐行解读：**
- **步骤 1**：使用 CANN 容器作为运行环境基础；操作耗时 5 min，主要开销在镜像拉取与依赖安装；原理部分需额外 5 min 理解容器化思路。
- **步骤 2**：通过 `PrecisionDebugger` 在 NPU 端采集统计量，1 min 完成，原理学习 10 min（理解 `task`/`level`/`step` 等配置字段含义）。
- **步骤 3**：同样使用 `PrecisionDebugger` 在 GPU 端采集"标杆"数据，仅 0.5 min，体现 GPU 端采集耗时更短；原理学习 5 min。
- **步骤 4**：调用 `msprobe compare` 子命令比对 NPU/GPU 两端统计量，1 min 完成，原理学习 10 min（理解比对指标与判定阈值）。
- **步骤 5**：调用 `graph_visualize` 或在 TensorBoard 中查看分级构图，2 min 完成，原理学习 10 min（理解构图节点与精度问题定位）。

### 表 2：前置条件

| 项目 | 要求 | 验证方法 |
| --- | --- | --- |
| **硬件算力** | Linux 服务器配备至少 1 张 NPU 卡，驱动与固件已安装 | 执行 `npu-smi info`，确认 NPU 卡状态正常 |
| **容器运行** | 已安装并运行 Docker（建议版本 ≥ 18.0） | 执行 `docker ps`，无报错即表示服务正常启动 |
| **脚本执行** | 宿主机已安装 Python 3 | 在宿主机执行 `python3 -V`，有版本信息输出即表示已安装 |
| **网络通信** | 已安装 curl（任意版本） | 执行 `curl -V`，有版本信息输出即表示已安装 |

**逐行解读：**
- **硬件算力**：必备条件，最低 1 张 NPU；`npu-smi info` 是 CANN 体系下查看设备状态的标准命令。
- **容器运行**：Docker ≥ 18.0 是为了兼容新版 docker 命令语法；`docker ps` 检查守护进程是否存活。
- **脚本执行**：宿主机需 Python 3，因为 `ctr_in.py` 启动脚本是 Python 写的。
- **网络通信**：curl 用于下载 `ctr_in.py` 与 pip 离线包，任意版本即可。

---

## 【公式解读】

原文无公式。

但配置 JSON 中存在一组"伪公式化"的采集参数表达式，可视为采集行为的"配置方程"，逐字段解读如下：

```json
{
    "task": "statistics",
    "dump_path": "${HOME}/msprobe_dump_npu",
    "rank": [],
    "step": [0, 1],
    "level": "mix",
    "async_dump": false,
    "statistics": {
        "scope": [],
        "list": [],
        "data_mode": ["all"],
        "summary_mode": "statistics"
    }
}
```

**字段含义与作用：**
- `task = "statistics"`：采集任务类型为"统计量"，仅产出 mean/max/min/nan/inf 等统计信息而非完整 Tensor，**降低磁盘占用**。
- `dump_path = "${HOME}/msprobe_dump_npu"`：采集数据根目录，`$HOME` 在容器内即 `/root`。
- `rank = []`：空列表表示不按 rank 过滤，适配单卡场景；多卡时需填具体 rank id。
- `step = [0, 1]`：仅在第 0、1 个训练迭代触发采集；**控制采样窗口**。
- `level = "mix"`：同时采集 Module 层级与 API 层级的前向/反向输入输出。
- `async_dump = false`：同步落盘，保证 step1 结束后数据一定写入磁盘后才继续。
- `statistics.scope = []`：空表示对所有算子生效；填入算子名列表可缩小范围。
- `statistics.list = []`：配合 `scope` 使用，定义需要采集的具体 API/Module。
- `statistics.data_mode = ["all"]`：统计输入 + 输出。
- `statistics.summary_mode = "statistics"`：汇总方式为统计量（区别于 `markdown` 等展示形式）。

---

## 【关联】

文档内部链接映射出 msProbe 的完整功能拓扑：

| 内部链接 | 关联模块 | 关系性质 |
| --- | --- | --- |
| [mindspore_quick_start.md](mindspore_quick_start.md) | MindSpore 场景快速入门 | **框架对位**：本文是 PyTorch 版本，MindSpore 是平行的姊妹教程 |
| `../user_guide/accuracy_compare/pytorch_accuracy_compare_instruct.md#精度比对结果分析` | 精度比对结果分析 | **下游消费**：本教程步骤 4 调用 `msprobe compare` 后，需要进入该文档解读比对报告 |
| `../user_guide/accuracy_compare/pytorch_visualization_instruct.md` | PyTorch 可视化构图比对 | **下游消费**：本教程步骤 5 的可视化原理与操作细节在该文档展开 |
| `../user_guide/config_check_instruct.md` | 环境/配置检查 | **旁路校验**：可作为环境异常的诊断工具，与本教程 2.1.7 检查命令互补 |
| `../user_guide/monitor_instruct.md` | 训练监控 | **横向能力**：用于监控 Loss、梯度等指标，与本教程精度数据互为佐证 |
| `../user_guide/dump/pytorch_data_dump_instruct.md` | PyTorch 数据采集详细说明 | **上游深入**：本教程 2.2 节采集流程的字段、API 完整文档 |
| `../user_guide/accuracy_compare/pytorch_accuracy_compare_instruct.md` | 精度比对完整指令 | **下游消费**：本教程步骤 4 比对命令的完整参数说明 |
| `../user_guide/accuracy_compare/pytorch_visualization_instruct.md` | 可视化构图比对完整指令 | **下游消费**：本教程步骤 5 构图比对的详细用法 |

**流程串联**：本教程（采集 + 比对 + 可视化快速路径）→ `pytorch_data_dump_instruct.md`（采集原理深挖）→ `pytorch_accuracy_compare_instruct.md`（比对原理）→ `pytorch_visualization_instruct.md`（可视化原理）。`config_check_instruct.md` 与 `monitor_instruct.md` 是旁路辅助模块。

---

## 【使用方法】

### 启动流程（原文命令）

**① 宿主机配置环境变量：**
```bash
source /dev/stdin <<< "$(dev_id=$(lspci -n -D | grep -o '19e5:d[0-9a-f]\{3\}' | head -n1 | cut -d: -f2); case "$dev_id" in ... esac)"
```
输出 `[PASS]` 即镜像与芯片识别成功。

**② 宿主机拉取并启动容器：**
```bash
docker pull ${MY_STUDY_VAR_CANN_IMAGE}
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}
```

**③ 容器内安装依赖：**
```bash
pip3 install networkx==3.6.1 pillow==12.2.0
pip3 install https://inst.obs.cn-north-4.myhuaweicloud.com/env/mirror/$(arch)/download.pytorch.org/whl/cpu/torch-2.7.1%2Bcpu-cp311-cp311-manylinux_2_28_$(arch).whl
pip3 install https://gitcode.com/Ascend/pytorch/releases/download/v26.0.0-pytorch2.7.1/torch_npu-2.7.1.post4-cp311-cp311-manylinux_2_28_$(arch).whl
pip3 install torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cpu
pip3 install -U mindstudio-probe
```

**④ 写入采集配置 `~/config.json`：** 见上文"公式解读"中的 JSON 块。

**⑤ 写入并执行训练脚本：**
```bash
python3 ${HOME}/precision_sample.py --gpu 0
```

**关键配置项（原文）：**
| 配置项 | 取值 | 含义 |
| --- | --- | --- |
| `task` | `statistics` | 仅采统计量 |
| `dump_path` | `${HOME}/msprobe_dump_npu` | 数据落盘根目录 |
| `step` | `[0, 1]` | 采集窗口 |
| `level` | `mix` | Module + API 层级 |
| `async_dump` | `false` | 同步落盘 |
| `statistics.data_mode` | `["all"]` | 输入输出全采集 |
| `statistics.summary_mode` | `statistics` | 汇总为统计量 |

**关键调用（原文 Python 代码）：**
- `from msprobe.pytorch import PrecisionDebugger, seed_all`
- `seed_all(seed=1234, mode=True)` —— 固定随机种子
- `debugger = PrecisionDebugger(config_path=os.path.expanduser("~/config.json"))`
- `debugger.start(model)` → `debugger.stop()` → `debugger.step()`

**注意事项（原文）：**
- 第 2.2.3 节见到 `msprobe ends successfully` 日志即可按 `Ctrl + C` 安全终止，无需等所有 epoch 跑完。
- GPU 端需将代码中 `cuda` 设备切换为 `npu`，或通过 `torch_npu.contrib.transfer_to_npu` 自动转换（代码中已 try-import）。
- 离线/内网环境需参考"第 3.1 / 3.2 / 3.3 节"获取镜像与依赖（原文已截断，未给出离线步骤明细）。

## 图文联合解读

- `compare_result_quick_start.png`: **图文联合解读：**

图示为 PrecisionDebugger 输出的 **NPU vs Bench（GPU 标杆）精度比对表**，逐行列出 `Functional.conv2d.forward.input/output` 及 `Module.conv1/conv2d` 各张量节点的 Max_diff、Mean_diff、L2norm_diff 等差异指标，并以 Result 列标记 `pass`/`warning`，Err_message 展示溢出告警。

论证结论：**NPU 与 GPU 在 conv2d 算子上整体数值一致**（绝大多数 Result=pass），但 `input.1` 出现 Min_diff=-7.45e+5 量级偏差、`output.0` 触发 warning，提示存在**数值溢出/精度异常点**，需重点排查。

与文档关系：对应步骤 4「精度比对」产物，是后续定位精度问题的依据。
- `vis_quick_start.png`: **图解读：**

**1) 图内容**：TensorBoard 界面展示 NPU（调试侧）与 GPU（标杆侧）并排的 DefaultModel 构图比对，两者层级结构一致（Conv2d→BatchNorm2d→ReLU→MaxPool2d→Sequential…）。左侧"Module.conv1.Conv2d.forward.0"被标黄（Warning），下方比对详情列出 weight 与 output.0 的张量统计（max/min/相似度 954.37、误差 0.002255%、0.001014%）。

**2) 技术结论**：通过逐算子级可视对比与数值比对，可精确定位到首个 conv1 出现 Warning 误差，结合相似度指标量化偏差程度。

**3) 与文档关系**：对应文档"步骤5 可视化构图比对"，用图形化方式直观展示 NPU/GPU 精度差异，支撑"数值溢出、Loss 异常等精度问题排查"的核心目标。
