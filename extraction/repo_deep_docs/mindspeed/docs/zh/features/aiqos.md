# AI QoS差异化调度特性说明

> 仓 `mindspeed` · 路径 `docs/zh/features/aiqos.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/aiqos.md

## 【定位】

本文面向大模型分布式训练中的 UB 网络流量冲突，介绍 AI QoS 通过虚拟通道隔离与严格优先级调度实现差异化调度、提升整体算效的能力。

## 【技术要点】

1. **流量冲突来源**：TP（张量并行）、EP（专家并行）、DP（数据并行）、PP（流水线并行）等混合并行会产生 D2D 流量，H2D Swap 等流量则可能与 D2D 流量同时到达 UB Switch，形成 incast 网络冲突和拥塞。
2. **VL 隔离与 SP 调度**：不同类型流量被映射到不同虚拟通道（VL）以隔离拥塞，并在 VL 间采用 SP（Strict Priority）调度；流量同时到达时，先排空高优先级 VL，再处理下一级队列。
3. **自动模式**：通过 `--aiqos --aiqos-mode auto` 启用，感知流量类型、通信域、通信量和算效贡献，自动选择冲突度较低的 VL 映射及算效优先的差异化 QoS 调度；当前支持 TP、PP、DP、EP、CP 典型并行策略。
4. **手动模式**：通过 `--aiqos --aiqos-mode manual --aiqos-schedule {tp:high,pp:middle,dp:low}` 配置各并行策略的优先级，支持 `Low/Middle/High` 三档；D2D 流量以并行策略为粒度下发 QoS，而 H2D 流量只支持通道级整体优先级，暂不支持算子级区分。
5. **端到端 QoS 映射**：D2D 流量在创建 Group 时向 TorchNPU 下发 QoS 标记，依次经过 CANN、NPU 并封装到 UB 报文；H2D/D2H 流量可借助 DCMI 接口设置 QoS，UB Switch 再依据 QoS 值将流量映射到相应 VL。
6. **A3 DCMI 融合约束**：A3 代际 NPU 将控制面 `mpam QoS` 与训练脚本下发的随路 QoS 取最大值，通过设置带宽水线使控制面 QoS 低于随路 QoS；接口支持 `low → 2`、`middle → 4`，`mpamid` 范围为 `0-31`，默认 `bitmap` 为 `[0x1, 0, 0, 0]`。

## 【关键机制与数据】

原文：不同流量对算效的贡献和可掩盖程度并不相同。H2D Swap、D2D DP 等流量可以由上层机制进行较好的通算掩盖，而部分 D2D 流量难以掩盖或掩盖程度较低，因此需要按照流量类型实施差异化 QoS。

原文：典型 SP 调度并不是同时按固定比例服务所有 VL，而是在不同类型流量同时到达 UB Switch 时，先将高优先级 VL 调度排空，再调度下一级队列，依次形成高到低的调度顺序。

原文：手动模式按照用户指定的任务级 QoS 优先级，经过多层传递和 QoS 语义映射，将其转换为 UB 协议 QoS 语义，写入 UB 报文，再映射至 UB Switch 中对应的 VL。

原文：D2D 流量以并行策略为粒度，在创建 Group 时向 TorchNPU 下发 QoS 标记，经 CANN 传递至 NPU，最终封装到 UB 报文；H2D 流量只支持通道级全局 QoS 优先级，不包含算子下发的 H2D 流量，暂不能在同为 H2D 的不同算子之间设置不同优先级。

原文：A3 代际 NPU 使用 DCMI 接口融合控制面 QoS 与细粒度随路 QoS，融合方式为取二者最大值；通过令 `mpam QoS` 低于随路 QoS，保证 AI QoS 自动或手动模式指定的随路 QoS 成为 NPU 最终接受的 QoS。

原文：`fusion_qos` 中，`bw_low=10` 为水线下限，`bw_high=50` 为水线上限，`target=0` 为 `mpamid` 且只能为 `0`，`hardlimit=0` 表示不进行带宽硬件限制。

原文：`set_h2d_qos` 中，字符串 QoS 仅支持 `low` 和 `middle`，分别映射为灵衢网络 QoS 值 `2` 和 `4`；`mpamid` 必须处于 `0-31`，默认 `bitmap=[0x1, 0, 0, 0]`，表示 H2D 流量所在的流量通道。

原文：UB Switch 已预置 QoS 模板，模板包含 QoS 值到 VL 的映射关系及 VL 间调度策略，同时允许用户通过开放模板自行指定这两项配置。

原文：文档未提供吞吐、时延、拥塞率或算效提升比例等实测性能数据；已给出的数值均为协议、配置或支持范围参数，而非性能收益数据。

## 【表格解读】

| 软件        | 配套版本                          |
| :---------- | :-------------------------------- |
| TorchNPU   | 7.3.RC1*                          |
| CANN        | CANN 8.6*                         |
| UB Switch   | LingQu Computing Network 1.6.0*   |

- **表头“软件 / 配套版本”**：定义软件组件及其配套版本范围。
- **TorchNPU / 7.3.RC1***：TorchNPU 负责承接 D2D 流量以并行策略为粒度下发的 QoS 标记，并参与后续向 CANN 和 NPU 的传递。
- **CANN / CANN 8.6***：CANN 负责传递 QoS 语义，使任务级优先级能够继续转换为 NPU 和 UB 协议侧的 QoS 语义。
- **UB Switch / LingQu Computing Network 1.6.0***：UB Switch 负责依据 UB 报文中的 QoS 值映射 VL，并执行预置或用户配置的 VL 调度策略。
- `*预计配套版本，具体版本待相关组件正式发布后进行更新`：三个版本均为预计配套版本，不是已完全固化的最终版本承诺。

## 【公式解读】

原文无公式。

文档仅以文字说明 A3 DCMI 采用“控制面 QoS 值与随路 QoS 值的最大值”融合策略，没有给出带符号的等式、伪代码或计算表达式。

## 【关联】

原文未提供内部链接，以下关系均根据正文中的数据传递和依赖关系整理：

- **训练脚本 → AI QoS**：通过 `--aiqos` 开启特性，并使用 `--aiqos-mode auto` 或 `manual` 选择调度模式。
- **并行策略 → D2D 流量 → TorchNPU/CANN/NPU**：并行策略决定 D2D 流量的分类和优先级粒度；QoS 标记从 Group 创建流程进入 TorchNPU，经 CANN 传递至 NPU。
- **AI QoS → UB 报文 → UB Switch**：任务级或自动模式生成的 QoS 语义被写入 UB 报文，UB Switch 再将 QoS 值映射为相应 VL。
- **H2D/D2H → DCMI**：DCMI 负责设置相关流量的 QoS；A3 NPU 还通过 DCMI 下发控制面 `mpam QoS`。
- **随路 QoS 与控制面 QoS → A3 NPU 最终 QoS**：二者按最大值融合，再通过 `bw_low`、`bw_high` 等水线配置保证随路 QoS 生效。
- **AI QoS 与 UB 模板**：QoS 模板决定“QoS 值—VL”关系和“VL—调度策略”关系，因此 AI QoS 的语义最终依赖 UB Switch 侧模板落地。
- **软件依赖关系**：TorchNPU、CANN 和 UB Switch 的配套版本共同决定该特性可用性；同时要求 Atlas 800T A3 超节点服务器或 Atlas 900 A3 SuperPoD 集群环境。

## 【使用方法】

### 自动模式

在训练脚本中添加：

```shell
--aiqos          # AI QoS特性开关
--aiqos-mode auto  # 配置AI QoS模式为自动模式
```

自动模式当前支持：

```text
TP PP DP EP CP
```

### 手动模式

在训练脚本中添加：

```shell
--aiqos          # AI QoS特性开关
--aiqos-mode manual  # 配置AI QoS模式为手动模式
--aiqos-schedule {tp:high,pp:middle,dp:low}  # 配置不同并行策略的QoS优先级
```

上述配置表示：

- `tp:high`：TP 优先级为高。
- `pp:middle`：PP 优先级为中。
- `dp:low`：DP 优先级为低。

手动模式支持三档 QoS 优先级：

```text
Low / Middle / High
```

当前支持以下并行策略：

```text
dp
dp-cp
intra-dp-cp
inter-dp-cp
cp
mp
tp
pp
embd
pos-embd
tp-dp-cp
tp-dp
tp-cp
ep
ep-tp
tp-ep-mp
tp-ep-pp
ep-dp
hcp
```

H2D 流量只支持通道级整体 QoS，不支持算子级 QoS；D2D 流量则按并行策略粒度进行 QoS 标记。

### DCMI 接口

编译前进入 `mindspeed/ops/csrc/qos` 目录，将 `CMakeLists.txt` 中的 `pybind11_install_dir` 修改为 pybind11 安装目录，然后执行：

```shell
mkdir build
cd build
cmake ..
make -j
```

编译完成后在 `output` 目录生成 SO。

示例配置使用：

```python
import aiQos

CARD_ID_LIST = [0, 1, 2, 3, 4, 5, 6, 7]
DEVICE_ID_LIST = [0, 1]
```

融合 QoS 的默认配置为：

```python
fusion_qos(bw_low=10, bw_high=50, target=0, hardlimit=0)
```

接口调用包括：

```python
aiQos.init()
aiQos.set_gbl_qos(card_id=card_id, device_id=device_id, mode=1)
aiQos.set_bw(
    target=target,
    bw_low=bw_low,
    bw_high=bw_high,
    hardlimit=hardlimit,
    card_id=card_id,
    device_id=device_id
)
```

其中，正文明确说明 `target` 是 `mpamid` 值，只能为 `0`；`hardlimit=0` 表示不对带宽进行硬件限制。

H2D QoS 示例：

```python
set_h2d_qos('low', 20)
```

该调用使用默认 `bitmap=[0x1, 0, 0, 0]`，对应灵衢网络 QoS 值 `2`。接口也会将 `middle` 映射为 QoS 值 `4`；`mpamid` 可在 `0-31` 范围内选择。

## 图文联合解读

- `aiqos1.png`: **图文解读：**

图示超节点拓扑（CPU板+UB交换板+NPU板），用黄、深蓝、红三色箭头区分**节点内D2D、H2D、跨节点D2D**三类流量，多色线条汇聚至同一UB Switch处形成星形爆发点，标示incast拥塞冲突。

论证：不同并行策略（TP/EP/DP/PP及Swap）在UB Switch处存在多类流量竞争，单一调度无法兼顾算效。

与文档关系：直接支撑"在UB Switch采用VL隔离+SP差异化调度"的核心论点，为QoS优先级映射提供流量场景依据。
- `aiqos2.png`: **图文联合解读：**

图示展示三条虚拟通道VL1/VL2/VL3分别承载高/中/低优先级流量（各含4个分组），汇聚至SP调度模块（调度能力为4）。论证了**严格优先级调度**机制：高优先级VL先被排空，再依次调度次级队列。该图正是文档所述"差异化QoS调度"方案中SP调度方式的具象化说明，通过VL隔离与优先级排序，避免流量冲突时的拥塞扩散，从而实现算效最优的QoS映射目标。
- `aiqos3.png`: **1) 图中内容：** 自上而下分层架构——训练脚本（手动/自动模式）→ MindSpeed AI QoS模块 → 框架层（Pytorch/torch_npu，D2D通信域QoS标记）→ CANN层（API/HCCL，H2D QoS标记）→ Host→NPU（QoS模块→流量发送模块），最终通过携带QoS值的UB报文进入UB Switch（QoS配置接口+调度模块），用户QoS配置模板旁路输入。

**2) 技术结论：** QoS语义从任务级经多层映射传递到UB协议级，H2D与D2D流量在NPU侧标记不同QoS值，UB Switch据此分VL调度，实现差异化QoS。

**3) 与文档关系：** 图示论证了"方案介绍"中两种模式（手动/自动）、H2D与D2D差异化QoS及三层传递映射的具体落地路径。
