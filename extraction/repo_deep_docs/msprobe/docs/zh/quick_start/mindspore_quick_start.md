# MindSpore场景精度调试工具快速入门

> 仓 `msprobe` · 路径 `docs/zh/quick_start/mindspore_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprobe/docs/zh/quick_start/mindspore_quick_start.md

# msprobe MindSpore 场景精度调试工具快速入门 — 深度解读

---

## 【定位】

本文档是 msprobe 工具链在 **MindSpore 场景**下的快速入门指引，聚焦"**精度数据采集 + 精度比对**"两个最常用环节，示范从环境准备、配置 dump、训练脚本埋点到调用 `compare`/`graph_visualize` 完成 NPU vs 标杆数据差异定位的最小可用闭环，帮助昇腾训练场景下的用户（MindSpore 2.6.0/2.7.0）快速完成精度问题定界。

---

## 【技术要点】

1. **完整五步精度调试流程**：`训练前配置检查 → 训练状态监测 → 精度数据采集 → 精度预检 → 精度比对`，本文档仅展开后两步快速入门，其余步骤通过内部链接指向详细章节。
2. **环境基线**：依赖昇腾 NPU 服务器 + NPU 驱动/固件 + 配套版本 CANN（Toolkit + ops 包），MindSpore 以 **2.6.0 和 2.7.0** 为示例版本，msprobe 通过 `pip install mindstudio-probe` 安装。
3. **数据采集三件套接口**：`PrecisionDebugger(config_path="./config.json")` 实例化 → `debugger.start(model)` 开启 dump → `debugger.stop()` 关闭单次 dump → `debugger.step()` 切到下一个 step；采集目录命名规则为单卡 `proc{pid}`，多卡 `rank{id}`。
4. **dump 配置文件（config.json）关键参数**：`task="statistics"`、`dump_path="/home/dump/dump_data"`、`rank=[]`、`step=[0,1]`、`level="L1"`、`async_dump=false`，statistics 子段含 `scope`/`list`/`tensor_list`/`data_mode=["all"]`；可视化构图场景需把 `level` 改为 `"L0"` 或 `"mix"`。
5. **精度比对双模式**：
   - `msprobe compare -tp <npu_dump.json> -gp <baseline_dump.json> -o <out_dir>`（CSV 比对结果）
   - `msprobe graph_visualize -tp <npu_dir> -gp <baseline_dir> -o <output_dir>`（生成 vis 文件 + TensorBoard 可视化）
6. **落盘数据三件套**：`construct.json`（Module 层级关系，本样例为空）/ `dump.json`（前反向 API 输入输出的统计量与溢出信息）/ `stack.json`（API 调用栈）。**磁盘空间风险被明确警告**：精度数据占用与模型参数、采集开关配置、迭代数量强相关。

---

## 【关键机制与数据】

### 数据流（原文驱动链）

- **入口**：`msprobe.mindspore.PrecisionDebugger(config_path="./config.json")` 加载 JSON 配置 → 在训练循环中通过 hook 机制挂载到模型（原文日志："The api statistics hook function is successfully mounted to the model."）。
- **采集动作**：`debugger.start(model)` 打开 dump 开关 → `train_step(data, label)` 训练一次 → `debugger.stop()` 关闭本次 dump（采集落盘到同一 step）→ `debugger.step()` 切到下一个 step。
- **原文采集成功示例日志**：
  ```
  The api statistics hook function is successfully mounted to the model.
  msprobe: debugger.start() is set successfully
  Dump switch is turned on at step 0.
  Dump data will be saved in /home/dump/dump_data/step0.
  ```
- **比对流向（compare 模式）**：以 MindSpore 2.7.0 为 `tp`（待测/NPU 侧）、2.6.0 为 `gp`（标杆/参考侧），输出 `compare_result_{timestamp}.csv`，含 Result、Err_Message 字段供定位可疑算子。
- **可视化流向（graph_visualize 模式）**：以"目录级"输入（而非单文件 `dump.json`），输出 `vis` 后缀文件，配合 TensorBoard **2.20.0** 在 6006 端口展示分级图比对（原文图 1：`figures/vis_result.png`）。

### 性能/版本数据（原文有的）

- MindSpore 支持版本：**2.6.0、2.7.0**。
- TensorBoard 版本：**2.20.0**，访问地址样例 `http://ubuntu:6006/`（实际替换为服务器 IP，如 `http://192.168.1.10:6006/`）。
- 单卡进程 PID 样例：`proc1280778`（原文 dump 路径）/ `proc1280779`（2.7.0 路径中）。
- 采集 step 数：原文示例 `step=[0,1]`，即采集两个迭代。

### 工作原理要点

- **精度调试本质**：训练 loss 等指标无法精确定位异常模块，需采集 API/Module 层级前反向输入输出做"逐算子"差异分析。
- **比对判定原则**：每种指标有各自判定标准，CSV 中"Result"+"Err_Message"需结合实际情况判断（原文强调）。
- **可视化分级**：`level` 取值 `L0/L1/mix` 决定 dump 粒度——L0 偏 Module 级构图、`mix` 混合粒度、`L1` 为普通 API 级（默认示例）。

---

## 【表格解读】

**原文无表格**（原文中仅含 JSON 配置块、命令行代码块和目录树代码块，未出现任何 markdown 表格结构）。

---

## 【公式解读**

**原文无公式**（全文无 LaTeX 数学公式或伪代码数学表达式，仅有 Python 训练循环伪代码与 JSON 配置定义，不属于数学公式范畴）。

---

## 【关联】

| 文档内引用模块 | 关联路径 | 关系性质 |
|---|---|---|
| 训练前配置检查 | `../user_guide/config_check_instruct.md` | msprobe 精度调试流程第 1 步（识别两个环境影响精度的配置差异），本文未展开，仅指引 |
| 训练状态监测 | `../user_guide/monitor_instruct.md` | 流程第 2 步（监测计算/通信/优化器异常），本文未展开 |
| 数据采集（dump） | `../user_guide/dump/mindspore_data_dump_instruct.md` | 流程第 3 步；本文档展开"快速入门"版本，详尽用法需参考该文档 |
| 精度预检 | `../user_guide/accuracy_checker/mindspore_accuracy_checker_instruct.md` | 流程第 4 步（扫描 API 数据找精度问题），本文档快速入门不涉及 |
| 精度比对 compare | `../user_guide/accuracy_compare/mindspore_accuracy_compare_instruct.md` | 流程第 5 步；本文档展示 `msprobe compare` 用法，参数细节指向 `#参数说明`、输出细节指向 `#输出结果文件说明` |
| 双图比对可视化 | `../user_guide/accuracy_compare/mindspore_visualization_instruct.md#双图比对` | `msprobe graph_visualize` 命令的详细参数说明来源 |
| msprobe 安装指南 | `../install_guide/msprobe_install_guide.md` | `pip install mindstudio-probe` 之外的完整安装说明 |
| CANN 安装 | https://www.hiascend.com/cann/download（外部链接） | 环境准备的第 2 步依赖 |
| MindSpore 安装 | https://www.mindspore.cn/install/（外部链接） | 环境准备的第 3 步依赖 |

**上下游定位**：本文档处于 msprobe 文档体系的"快速入门"层，是从安装 → 流程概览 → 实操第一步的引导；其展开后的完整用法分流到 `user_guide/` 各专题文档（dump、compare、visualization、accuracy_checker、monitor、config_check）。文档内部 `MindSpore精度数据采集代码样例` 锚点、`精度数据采集`、`精度比对`、`环境准备` 锚点构成段间互引。

---

## 【使用方法】

### 一、安装

```bash
pip install mindstudio-probe
```
原文同时要求：昇腾 NPU 驱动 + 配套 CANN（Toolkit + ops 包，环境变量配置）+ MindSpore 2.6.0/2.7.0 框架。

### 二、精度数据采集（最小流程）

1. **准备训练脚本**：命名为 `mindspore_main.py`，完整代码参见文末「MindSpore精度数据采集代码样例」章节。
2. **创建 `config.json`**（与训练脚本同目录）：
   ```json
   {
       "task": "statistics",
       "dump_path": "/home/dump/dump_data",
       "rank": [],
       "step": [0,1],
       "level": "L1",
       "async_dump": false,
       "statistics": {
           "scope": [],
           "list": [],
           "tensor_list": [],
           "data_mode": ["all"]
       }
   }
   ```
   - 可视化构图场景须改 `level` 为 `"L0"` 或 `"mix"`。
3. **脚本埋点**：
   ```python
   from msprobe.mindspore import PrecisionDebugger
   debugger = PrecisionDebugger(config_path="./config.json")
   ...
   debugger.start(model)        # 开启 dump
   train_step(data, label)
   debugger.stop()              # 关闭本次 dump（同一 step）
   debugger.step()              # 进入下一个 step
   ```
4. **执行训练**：
   ```bash
   python mindspore_main.py
   ```
   出现 `Dump data will be saved in /home/dump/dump_data/step0.` 表示成功。

### 三、精度比对 — compare 模式（API 级 CSV 比对）

```bash
msprobe compare \
  -tp /home/dump/dump_data_2.7.0/step0/proc1280779/dump.json \
  -gp /home/dump/dump_data_2.6.0/step0/proc1280778/dump.json \
  -o ./compare_result/accuracy_compare
```
输出文件：`compare_result_{timestamp}.csv`，列含 `Result`、`Err_Message`，逐算子可疑定位 → 详见 `../user_guide/accuracy_compare/mindspore_accuracy_compare_instruct.md#输出结果文件说明`。

### 四、精度比对 — graph_visualize 模式（分级可视化构图）

```bash
msprobe graph_visualize \
  -tp /home/dump/dump_data_2.7.0 \
  -gp /home/dump/dump_data_2.6.0 \
  -o /home/dump/output
```
随后：
```bash
tensorboard --logdir /home/dump/output --bind_all
```
浏览器打开 `http://<server_ip>:6006/`（TensorBoard 2.20.0），呈现分级可视化构图比对。

### 五、关键注意事项（原文明确警告）

- **磁盘空间风险——精度数据占据大量磁盘空间，可能写满导致服务器不可用**，需根据模型参数、采集开关配置、迭代数量自行保证可用空间。
- `level` 决定 dump 粒度，普通采集用 `"L1"`，可视化构图需 `"L0"` 或 `"mix"`。
- `compare` 用单文件 `dump.json` 作输入；`graph_visualize` 用整个 dump 数据目录作输入。
- 比对结果判定需结合每种指标的判定标准与实际情况，不能只看 `Result`/`Err_Message` 自动结论。

## 图文联合解读

- `vis_result.png`: ## 图文联合解读

**1) 图中内容：** TensorBoard GRAPH_ASCEND可视化界面，左右并列展示"调试侧缩略图"与"标杆侧缩略图"，呈现DefaultModel的Conv2d→BatchNorm2d→ReLU→MaxPool→Sequential等模块层级结构；下方"比对详情"表格列出标杆/目标节点的name、type、dtype、shape、Max/Min/Mean、Norm、Cosine、EucDist、MaxAbsErr、MaxRelativeE等指标，含"已匹配/未匹配"标识。

**2) 技术结论：** msProbe通过双侧图结构并排+节点级张量统计指标比对，Cosine=1.0且MaxAbsErr=0.0证明两环境BatchNorm2d节点精度完全一致，实现逐节点精度差异可视化。

**3) 与文档关系：** 印证文档"精度比对"环节——采集后通过该工具对照NPU与标杆API数据，快速定界精度问题模块（如高亮蓝框节点）。
