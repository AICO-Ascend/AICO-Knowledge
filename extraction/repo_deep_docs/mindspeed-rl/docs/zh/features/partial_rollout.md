# partial rollout

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/partial_rollout.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/partial_rollout.md

# 「partial rollout」特性文档深度解读

## 【定位】
本文档描述 mindspeed-rl 中 **partial rollout（部分 rollout）能力**：针对长序列推理场景中的长尾 long response 样本，通过"提前中断 + 下次迭代续推"的断点续推机制，避免单一长尾样本独占推理资源，从而降低长序列推理中长尾样本对端到端训练性能的拖累。

---

## 【技术要点】

1. **核心思想**：对长序列 response 的推理样本做**提前中断**，并在下次推理过程中对当前样本**续推**，避免单一长尾样本对推理过程造成资源浪费；目标是降低长尾样本对端到端性能的影响。

2. **启用配置**（YAML 单行配置）：
   ```yaml
   rl_config:
     partial_rollout_max_split: N   # 设置 N>1，即可在 N 轮内完全推理完成最长序列
   ```
   语义：`N` 是单个样本允许被拆分续推的最大轮次数，`N>1` 即启用 partial rollout。

3. **TransferDock 中转机制**：被截断的样本不直接丢弃，而是被放入 **TransferDock** 暂存，作为下一轮推理的优先取样来源；这是断点续推的载体。

4. **同步推理引擎方案**两大关键技术点：
   - **长序列推理截断机制**：根据**最大推理长度和次数**设置推理截断点，将截断样本放入 TransferDock；当满足 **≥GBS（Global Batch Size）** 个 prompt 已完成全部推理，则进入后续计算任务，否则从 TransferDock 取数据再次推理。
   - **基于优先级的混合数据重排和采样**：下一轮推理时**优先取出被截断样本**进行推理，以避免影响效果和收敛性。

5. **异步推理引擎方案**三大关键技术点（在同步方案基础上扩展）：
   - **实时长序列推理截断机制**：与推理引擎实时交互，**动态确定长尾序列被截断长度**；当 ≥GBS 个 prompt 完成后即中断推理，截断样本放入 TransferDock，避免长尾拖慢整体推理。
   - **基于优先级的混合数据重排和采样**：下一轮推理优先取出被截断样本，并**混合新样本**进行推理。
   - **收敛性和稳定性保证**：实现样本在**规定的迭代轮数内**完成推理。

6. **注意事项**：当前该特性**暂不支持和 VPP 特性同时启用**。

---

## 【关键机制与数据】

### 工作原理（数据流）

**同步引擎（数据按批处理，批次内全部完成后统一返回）：**
- 数据按批进入推理引擎 → 引擎在达到**最大推理长度 / 最大推理次数**的截断点时，将未完成样本截断并放入 **TransferDock** → 判断已完成的 prompt 数是否 **≥GBS**：
  - 是 → 进入后续计算任务；
  - 否 → 从 TransferDock 取数据再次进入本轮推理 → 直至凑够 ≥GBS 个完整 prompt 后统一返回。
- 下一轮训练触发新推理时，**优先**从 TransferDock 取上次被截断的样本续推。

**异步引擎（数据按批次进入，可异步按样本粒度返回）：**
- 数据按批次进入推理引擎 → 引擎与调度器实时交互，**动态确定**长尾样本的截断长度 → 一旦 ≥GBS 个 prompt 完成推理即**中断**当前推理 → 截断样本存入 TransferDock → 下一轮推理**优先**取截断样本，并混合新样本一起推理 → 同时通过迭代轮数限制保证**规定迭代轮数内完成推理**，以维持收敛性。

### 性能/验证数据
- **原文**：仅给出 **图5「同步引擎验证结果」**（`figures/sync_partial_compare_result.png`），文档未提供具体的数字指标/对比数值。异步引擎**原文未给出**验证数据或图表。

---

## 【表格解读】

**原文无表格。** 文档全部以示意图 / 流程图（图1–图5）和 YAML 配置示例呈现，未出现任何参数表或性能对比表。

---

## 【公式解读】

**原文无公式。** 文档以文字描述机制为主，未给出任何 LaTeX 公式或伪代码形式的数学表达式。

---

## 【关联】

由于本篇文档是单特性 feature 文档，文末**未提供内部链接**（用户提供的内部链接信息为"无"）。基于文档自身内容，可归纳出以下模块/概念关联：

- **TransferDock**：partial rollout 的核心载体，被同步和异步两套方案共同使用，是"截断—续推"链路上的关键数据结构。
- **GBS（Global Batch Size）**：作为推理阶段"是否进入后续计算"的判据，与上游 batch 调度直接相关。
- **同步推理引擎 / 异步推理引擎**：本文给出的两套并行方案均围绕同一思想（断点续推 + 跨迭代长尾调度），区别在于调度粒度（批次级 vs 样本级）。
- **VPP 特性**：被显式标注为**当前不兼容**，属于互斥约束关系。
- **断点续推的最大轮数 N**（即 `partial_rollout_max_split`）：直接决定样本是否被强制收敛，与"收敛性和稳定性"约束联动。

---

## 【使用方法】

**启用方式（原文给出）：**

在 RL 训练配置 YAML 中启用，示例：
```yaml
rl_config:
  partial_rollout_max_split: N    # N > 1 即可在 N 轮内完全推理完成最长序列
```

**配置项语义（原文给出）：**
- `partial_rollout_max_split`：单个样本可被截断续推的最大轮次数；`N>1` 即启用 partial rollout 能力。

**互斥约束（原文给出）：**
- 目前此特性**暂不支持与 VPP 特性同时启用**。

**原文未涉及**的内容：具体的环境变量、CLI 命令入口、默认值、推荐取值区间、调用 API 等，均未在本文档中出现。

## 图文联合解读

- `sync.png`: 1) 图示跨2个iteration的同步引擎流程：每轮vLLM engine1/2推理至0.5max_tokens处截断（红虚线），未完成样本经TransferDock（2GBS）续推，循环直至N_ready≥GBS后进入Ref/Reward/Update与parameter update。
2) 论证长序列在0.5max_tokens截断后通过TransferDock跨轮续推，可避免长尾样本独占推理资源。
3) 直观对应文档"断点续推+跨迭代长尾调度"核心论点，展示partial_rollout_max_split=N机制下的资源利用与数据流转路径。
- `sync_1.png`: ## 图文联合解读

**1) 图中内容**：异步引擎流程图。右侧主循环从 actor rollout → partial rollout 判断（开启则 ready_num=0）→ while ready_num<GBS 循环内：dispatch_data 取 prompt+response 并设 max_tokens=max_tokens_config/max_split_times → llm.generate → 判断 response[-1]==eod 或 prompt_len+response_len≥max_model_len 或 response_len==max_tokens_config，Y 则 rollout_completed=True、N 则 False → 写入 TransferDock；累计 ready_num 达标后 dispatch_data(get_n_samples=True) → ref log prob / reward / update → pop experiences、按 age 排序 → new iteration 首轮 load 1GBS prompts，否则 load 2GBS。

**2) 技术结论**：验证了"动态截断+续推"可行性——长尾样本分片推理结果带 completed 标记入 TD，下轮优先取续推，避免拖慢整体节奏。

**3) 与文档关系**：对应文档"异步推理引擎方案"图4，落地"截断机制+优先级混合采样+收敛性保证"三大关键点。
- `async.png`: ## 图文联合解读

**图示内容**：展示异步引擎两轮迭代流程，含2个并行vLLM引擎、TransferDock（容量2GBS）、Ref/Reward/Update模块及参数更新环节。白色斜纹为prompt，彩色块为已生成response，灰色块为待续推长尾样本；红色虚线标注"if N_ready ≥ GBS: send stop_signal"。

**技术结论**：长尾序列被截断暂存TransferDock，待凑齐≥GBS个完成样本即触发停止信号，避免推理资源空置；下轮优先续推被截断样本。

**与文档关系**：对应"异步推理引擎方案"图3，论证"断点续推+跨迭代长尾调度"机制如何解决长尾样本拖慢整体推理的痛点。
- `async_1.png`: 图示异步引擎partial rollout流程：右侧actor rollout循环→llm.generate→判定eod/超长截断→未完成样本回传TD→累计ready_num≥GBS且max_age内完成则stop_signal停推；左侧Trainer按age排序消费经验。论证断点续推可避免长尾样本拖慢整体推理，对应文档"实时截断机制"与"基于优先级混合数据重排采样"两个关键技术点。
- `sync_partial_compare_result.png`: **图示内容**：六组对比曲线（Timing all、Response length mean/max、Grpo score mean、Actor pg loss、Timing rollout），蓝线为 `sync_partial_2.txt`（启用 partial rollout），红线为 `training[1,False,True].log`（基线），下方配以 Error 残差图，标注 Mean Error 与 MSE，并标记 GRPO score 残差点 t0s=0.0117。

**论证结论**：两种配置下响应长度、GRPO 分数、Actor 损失等关键训练曲线高度吻合；GRPO score 残差均值仅 0.0019，Response length 残差均值 -42.8，actor pg loss 残差 0.0029，说明 partial rollout 未改变模型收敛行为。

**与文档关系**：作为图5"同步引擎验证结果"，佐证断点续推 + 跨迭代长尾调度机制在保持训练一致性的同时降低端到端时延，支撑文档"避免长尾样本造成资源浪费"的论点。
