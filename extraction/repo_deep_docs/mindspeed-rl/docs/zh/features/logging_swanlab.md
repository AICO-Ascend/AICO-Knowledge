# MindSpeed RL 训练指标可视化

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/logging_swanlab.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/logging_swanlab.md

# 「MindSpeed RL 训练指标可视化（SwanLab）」深度解读

---

## 【定位】

这篇文档解决的是 MindSpeed RL 用户**如何在训练过程中对训练指标进行可视化追踪**的问题，介绍了借助 SwanLab（与 WandB 二选一）这一开源实验跟踪工具，从安装、参数配置、云端/本地模式启用到查看可视化结果的一整套操作流程。

---

## 【技术要点】

1. **工具二选一原则**：SwanLab 和 WandB 在 MindSpeed RL 中是互斥的可视化方案，使用者二选其一。SwanLab 相对 WandB 部署更易、更安全，并支持离线模式。
2. **依赖安装**：推荐安装新版 board 扩展 `swanlab[board]`，并搭配日志库 `loguru`；旧版可使用 `swanlab[dashboard]`。
3. **互斥开关机制**：在 yaml 的 `rl_config` 字段中，`use_tensorboard: true` 与 `use_swanlab: true` 同时为 True 时，tensorboard 不生效。
4. **四类必填配置项**：当 `use_swanlab: true` 时，`swanlab`（模式）、`swanlab_project`（项目名）、`swanlab_exp_name`（实验名）、`swanlab_save_dir`（本地保存路径，建议绝对路径）四个字段均必填。
5. **双模式支持**：`swanlab` 字段取值为 `local`（本地）或 `cloud`（云端，需网络）。
6. **本地看板启动**：通过 `swanlab watch . -host xxxx -port xxxx` 命令，在本地日志保存路径下启动可视化看板，访问对应 IP:端口即可查看训练可视化内容。

---

## 【关键机制与数据】

- **工作原理（原文）**：MindSpeed RL 通过调用开源库 SwanLab 的能力，将训练过程产生的指标写入 SwanLab 的记录体系；用户既可上传到 SwanLab 云端（`cloud` 模式），也可落地到本地路径（`local` 模式），再通过 `swanlab watch` 命令在本地拉起一个看板服务进行可视化浏览。
- **数据流（原文）**：训练 yaml 中 `rl_config` 字段开启 `use_swanlab` → 选定 `local` / `cloud` 模式 → 写入 `swanlab_save_dir` 指定目录（或上传云端）→ `cd` 进入该路径 → `swanlab watch` 启动本地看板 → 浏览器访问 IP:端口查看指标。
- **性能数据**：原文未涉及任何性能数据（如速度提升、吞吐等）。

---

## 【表格解读】

原文无表格。（文档中所有信息均以 yaml 代码块、bash 命令和文字说明形式呈现，未出现任何参数表、性能对比表或配置项汇总表。）

---

## 【公式解读】

原文无公式。（文档全部内容为配置示例与命令指引，未涉及任何数学公式或伪代码形式的推导。）

---

## 【关联】

- **与 TensorBoard 的关系**：互斥关系。在 `rl_config` 字段中，若 `use_tensorboard` 与 `use_swanlab` 同时为 `true`，tensorboard 不生效。
- **与 WandB 的关系**：替代关系。SwanLab 和 WandB 是 MindSpeed RL 提供的两种训练指标可视化方案，用户根据需求二选一。
- **与 rl_config 字段的关系**：所有可视化相关开关（SwanLab / TensorBoard）都挂载在训练 yaml 文件的 `rl_config` 字段之下，是统一配置入口。
- **与 SwanLab 云端的关联**：选择 `cloud` 模式时，存在一条前置依赖——必须先执行 `swanlab login`，否则无法上传数据。
- **文档内部链接**：原文未提供其他特性的内部链接（即文末链接信息为"无"），因此本文档与其他 feature 文档之间的引用关系在本篇中未明确体现。

---

## 【使用方法】

### 前置安装
```bash
pip install "swanlab[board]"
pip install loguru
# 旧版兼容
# pip install "swanlab[dashboard]"
# pip install loguru
```

### yaml 参数配置（`rl_config` 字段）
```yaml
# tensorboard 与 swanlab 二选一，同时为 true 时 tensorboard 不生效
use_tensorboard: true

# 开启 SwanLab
use_swanlab: true

# SwanLab 模式：local 或 cloud，开启时必填
swanlab: local  # 或 swanlab: cloud

# SwanLab 项目名称，开启时必填
swanlab_project: "The_swanlab_project_name"

# SwanLab 实验名称，开启时必填
swanlab_exp_name: "The_swanlab_experiment_name"

# SwanLab 本地日志保存路径（建议绝对路径），开启时必填
swanlab_save_dir: "Path_to_save_the_swanlab_results_locally"
```

### 云端模式额外步骤
```bash
swanlab login
# 详细指引见 https://docs.swanlab.cn/guide_cloud/general/quick-start.html
```

### 查看可视化指标
Step 1 — 进入本地日志保存路径：
```bash
cd "Path_to_save_the_swanlab_results_locally"
```

Step 2 — 启动本地看板：
```bash
swanlab watch . -host xxxx -port xxxx
```

启动成功后，按提示访问对应 IP:端口即可看到训练可视化内容。

### 已知问题修复（原文）
若遇到：
```
TypeError: sequence item 0: expected str instance, Text found
```
可修改 `/usr/local/lib/python3.11/site-packages/swanboard/run/run.py`，注释掉 81–85 行，并在第 86 行替换为：
```python
tip = URL(host, port).__str__()
```

## 图文联合解读

- `img.png`: **图文联合解读：**

**图示内容：** 截图展示训练 YAML 配置文件中 `rl_config` 字段的 SwanLab 可视化参数配置块（红框标注），包含 7 个关键键值对：
- `use_tensorboard: true`、`use_swanlab: true`（二选一开关）
- `swanlab_mode: local`（本地模式）
- `swanlab_project: "MSRL-lab"`、`swanlab_exp_name: "MSRL-experiment"`（项目/实验名）
- `swanlab_save_dir: "/data/wql/msrl-rc3/MindSpeed-RL/swanlab-logs"`（绝对路径）

**技术结论：** 该配置验证了 SwanLab 离线部署的最小可用参数集——仅需 mode（local/cloud）、project、exp_name、save_dir 四个必填项，即可启动本地可视化记录，无需云端账号。

**与文档关系：** 直观对应"前置准备"章节中 SwanLab 本地模式的 YAML 配置示例，佐证"SwanLab 比 WandB 更易部署、更易离线使用"的核心论点，为后续 `swanlab watch` 命令查看可视化图表提供配置入口。
- `img_2.png`: # 图文联合解读

## 1) 图中内容
终端 `ls -la` 输出，展示 SwanLab 本地日志保存目录的文件结构：
- **`run-20251210_xxx-xxx/`**：多个训练运行记录目录（时间戳+唯一标识），每个对应一次实验
- **`.venv/`**：Python 虚拟环境目录
- **`runs.swanlab`、`runs.swanlab-shm`、`runs.swanlab-wal`**：SwanLab 的 SQLite 数据库三件套（主库、共享内存、WAL 日志），用于持久化指标

## 2) 技术结论
该目录结构证明：
- SwanLab **local 模式**确实将实验数据落盘到本地（无需联网）
- 数据按"一次训练=一个 run 目录+统一数据库"组织，便于多实验对比
- 可直接通过 `swanlab watch .` 启动本地服务读取这些数据

## 3) 与文档论点的关系
此图正是文档 **Step1**（`cd 进入本地日志保存路径`）的可视化佐证，呼应了"offline / 本地部署"的特性，说明用户配置 `swanlab_save_dir` 后，训练产物会以 run 目录+SQLite 库的形式落地，为下一步 `swanlab watch` 启动可视化看板奠定数据基础。
- `img_3.png`: **图解分析：**

1) **画面内容**：终端命令行输出，显示 SwanLab 本地看板启动成功的日志信息。包含三行关键信息——版本与启动耗时（`v0.7.3 ready in 236ms`）、监听地址（`Network: http://0.0.0.0:1025`）以及退出快捷键提示（`press ctrl + c to quit`）。

2) **技术结论**：证明 `swanlab watch` 命令成功拉起了本地 Web 服务，监听在 `0.0.0.0:1025` 端口，236ms 内完成启动，响应迅速且支持局域网访问。

3) **与文档关系**：对应文档 "Step2" 中执行 `swanlab watch` 命令"成功后会显示"的提示截图，是用户从日志目录切换到浏览器可视化页面的关键中间环节，衔接了「配置路径」与「访问 IP:端口查看训练指标」的下一步操作。
- `img_1.png`: 图里画了什么：SwanLab 本地看板，左侧项目/实验导航（MSRL-experiment 运行中），右侧网格化展示 6 个 timing 类指标（resharding_to_infer/train、adv、non_overlap_adv、resharding_enter/exit_infer）与 1 个 acc_for_dapo_rewards/mean 奖励曲线，横轴为 Step（0–25），均呈绿色折线实时更新。

论证结论：SwanLab 能稳定采集并可视化 RL 训练中的时序与奖励指标，数据流通畅、刷新正常。

与文档关系：作为"参数配置 + `swanlab watch` 命令"步骤的可视化成果佐证，证明 local 模式下指标面板可正常访问。
- `img_4.png`: # 图文联合解读

## 1) 图中内容
图片展示了一段 Python 代码（第 81-86 行），用于构造 SwanLab 本地服务的访问地址：
- **分支判断**：若 URL 为 `zero_ip`（即 0.0.0.0），则遍历本机所有 IPv4 地址，与端口拼接成多个访问地址列表；
- **默认分支**：直接用 `URL(host, port)` 拼接单一访问地址 `tip`。
- 逻辑目的是将服务器监听地址转换为用户可访问的 URL。

## 2) 技术结论
该代码实现的是 **SwanLab 本地看板的多地址提示逻辑**，避免 0.0.0.0 监听时用户无法直接访问，确保输出可点击/可复制的浏览器 URL。

## 3) 与文档论点关系
对应文档"成功后会显示"步骤——`swanlab watch` 启动后，正是这段代码负责生成控制台输出的 IP:端口提示，衔接 `img_3.png`（启动成功界面）与 `img_1.png`（可视化页面），是**用户从命令到可视化页面的桥梁实现**。

⚠️ 备注：图片与文档描述的 SwanLab 配图（应为 dashboard 截图）不一致，建议替换为对应的可视化截图以保证图文匹配。
