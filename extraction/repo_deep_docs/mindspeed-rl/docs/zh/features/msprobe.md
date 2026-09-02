# 精度分析（msProbe）

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/msprobe.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/msprobe.md

# msProbe 精度分析特性深度解读

## 【定位】

这篇文档描述 mindspeed-rl 中集成的 msProbe（精度分析）能力：在强化学习训练流程中提供**训练配置采集、关键过程数据（prompt/response/kl_loss 等）采集、模型层 I/O 数据采集**与**两次训练比对定位**的能力，用于解决 RL 训练中出现的精度问题（尤其是确定性/精度对齐类问题）的定界与定位。

---

## 【技术要点】

1. **生效前提与场景限制**：msProbe 数据采集**仅支持共卡模式（integrated）场景**，且需依赖外部 msProbe 第三方库，安装指引链接到 Ascend/msprobe 仓库。
2. **统一配置入口**：通过 YAML 中的 `msprobe_config` 段进行开关与路径控制；`msprobe` 总开关为 `false` 时，下面所有采集项不生效。
3. **三类采集能力**：
   - **关键过程数据采集**：`key_data_dump` — 采集 prompt、response、ref_log_prob、advantage、log_prob、kl_loss、loss 的统计量（最大值、最小值、均值、L2norm）与真实数据；
   - **训练配置采集**：`configurations_dump` — 落盘到 `configurations.json`；
   - **模型层输入输出采集**：`actor_infer_dump` / `actor_train_dump` / `reference_dump` / `critic_train_dump` — 按 RL 阶段粒度（actor_generate_sequences、actor_compute_log_prob、actor_update、reference、critic_compute_values、critic_update）抓取张量级数据。
4. **范围裁剪机制**：`token_range_start`/`token_range_end` 控制推理生成 token 的采集区间（两者相等即采单个 token）；`step_start`/`step_end` 控制采集的训练步范围（对 actor_train/reference/actor_generate_sequences/critic_train 生效，相等即采单步），默认均为 0。
5. **落盘目录结构**：按阶段分目录（`actor_generate_sequences/`、`actor_compute_log_prob/`、`critic_compute_values/`、`actor_update/`、`critic_update/`、`reference_compute_log_prob/`），关键过程数据集中在 `data/` 子目录的 `advantages/、kl_loss/、log_prob/、old_log_prob/、loss/、prompts/、ref_log_prob/、responses/、values/` 九类。
6. **核心比对 API**：分两层比对 —— 关键数据用 `msprobe.core.SingleComparator.compare(dump_path1, dump_path2, output_path)`；模型层张量用 `msprobe.pytorch.compare_distributed('./dump_path1/step2', './dump_path2/step2', './output_path')` 输出 `compare_result_{timestamp}.xlsx`。

---

## 【关键机制与数据】

**工作原理（"两次采集 + 双路径比对"模式）**：

- 文档给出的精度对齐流程是一个典型的 **A/B 对比定界法**：同一份代码跑两次（设置不同 `dump_path`），对两份落盘做差分定位。
- 比对是**分层收敛**的：先用 `key_data_dump` 拿到关键阶段统计量与原始数据（`SingleComparator.compare`），在结果表格中**从首个出现差异的项**反推问题源头 —— 例如 `responses` 完全一致但 `ref_log_prob` 存在差异，则将问题定界到 reference model 计算。
- 第二层再用 `reference_dump`（或 `actor_train_dump` 等）结合 `step_start`/`step_end` 锁步采集模型层张量，调用 `compare_distributed` 输出 Excel，从首个差异点定位具体算子/层。

**数据流（原文目录树所示）**：

```
训练流程 (共卡/integrated)
    │
    ├── msprobe 总开关 ──> 训练配置 → configurations.json
    │
    ├── key_data_dump ──> data/{prompts, responses, ref_log_prob,
    │                       advantages, log_prob, old_log_prob,
    │                       kl_loss, loss, values}
    │
    ├── actor_infer_dump ──> actor_generate_sequences/step{step}/
    ├── actor_train_dump ──> actor_compute_log_prob/step{step}/
    │                       + actor_update/step{step}/
    ├── reference_dump ──> reference_compute_log_prob/step{step}/
    └── critic_train_dump ─> critic_compute_values/step{step}/
                              + critic_update/step{step}/
```

**性能数据**：原文未涉及任何性能数据、benchmark 或耗时统计。

**作用域注意**（原文）：`step_start`/`step_end` **只对** `actor_train_dump`、`reference_dump`、`actor_generate_sequences`、`critic_train_dump` 生效；`token_range_start`/`token_range_end` 作用于 `actor_infer_dump`（推理生成 token 范围）。

---

## 【表格解读】

### 配置参数表（原文逐字还原）

| 参数 | 说明 | 可选值 |
|------|------|--------|
| msprobe | 是否使能msprobe | true/false，开启后，下列的采集项才会生效 |
| dump_path | 存储路径 | str，默认值"./msprobe_dump" |
| key_data_dump | 关键过程数据采集 | true/false，默认false，是否采集关键过程数据，包括prompt、response、ref_log_prob、advantage、log_prob、kl_loss、loss的统计量信息（最大值、最小值、均值、L2norm值）和真实数据 |
| configurations_dump | 训练配置采集 | true/false，默认false，是否采集训练配置 |
| actor_infer_dump | actor的推理阶段模型层输入输出 | true/false，默认false，是否采集actor_generate_sequences阶段的模型层数据 |
| token_range_start | 采集推理生成token的开始范围 | int，默认0，与token_range_end搭配使用，表示采集推理生成的从第几个到第几个范围内的token数据 |
| token_range_end | 采集推理生成token的结束范围 | int，默认0，如果只想采某一个token的数据，设置为跟token_range_start一样 |
| actor_train_dump | actor的训练阶段模型层输入输出 | true/false，默认false，是否采集actor_compute_log_prob、actor_update阶段的模型层数据 |
| reference_dump | reference的模型层输入输出 | true/false，默认false，是否采集reference的模型层数据 |
| critic_train_dump | critic的训练阶段模型层输入输出 | true/false，默认false，是否采集critic_compute_values、critic_update阶段的模型层数据 |
| step_start | 采集开始步数 | int，默认0，只对actor_train_dump、reference_dump、actor_generate_sequences、critic_train_dump生效 |
| step_end | 采集结束步数 | int，默认0，只对actor_train_dump、reference_dump、actor_generate_sequences、critic_train_dump生效。如果只想采某一步的数据，设置为跟step_start一样 |

**逐行解读**：

- **msprobe**：全局总闸，决定后续所有采集项是否真正产生落盘动作；`false` 时其余开关即使为 `true` 也无效。
- **dump_path**：所有 dump 的根目录；文档示例默认值 `./msprobe_dump`，两次比对要求使用**不同路径**避免覆盖。
- **key_data_dump**：文档中最核心的"轻量级"采集开关，捕获**9 类** RL 关键数据（prompts、responses、ref_log_prob、advantages、log_prob、old_log_prob、kl_loss、loss、values——前 8 类与表格描述一致，"values" 由落盘目录树补充给出）的**统计量+真实数据**双层信息。
- **configurations_dump**：与上面三类的"运行时数据"不同，这一项落盘的是**静态配置**（如 `configurations.json`）。
- **actor_infer_dump**：映射到 RL 阶段中的 `actor_generate_sequences`（actor 推理生成阶段），产出的是**模型层张量级**数据。
- **token_range_start / token_range_end**：专为 `actor_infer_dump` 设计的长度裁剪工具，半开/闭区间含义在原文"从第几个到第几个"；两者相等 = 单 token 采集。
- **actor_train_dump**：覆盖 actor 的**两个训练阶段**——`actor_compute_log_prob`（再次计算 log prob）与 `actor_update`（策略更新）。
- **reference_dump**：单独开关，专门采集 reference model（参考模型）的模型层数据，**与 key_data 中的 ref_log_prob 对应**——后者是统计量/真实数据，前者是张量级 I/O。
- **critic_train_dump**：覆盖 critic 的**两个训练阶段**——`critic_compute_values` 与 `critic_update`。
- **step_start / step_end**：所有"按步"采集的步级切片器；文档强调它们**仅**作用于 4 类 dump（actor_train/reference/actor_generate_sequences/critic_train），**对 `key_data_dump`、`configurations_dump` 等不生效**；两者相等 = 单步采集。

---

## 【公式解读】

原文无公式。

（文档仅给出 YAML 配置示例与 Python API 调用代码块，不含任何数学表达式或 LaTeX/伪代码形式的公式。）

---

## 【关联】

原文无内部链接。文档提及的**外部依赖与上下游关系**如下：

- **上游 / 依赖**：外部 msProbe 第三方库（仓库 Ascend/msprobe），需通过其 `msprobe_install_guide.md` 完成安装；调用入口为 `msprobe.core.SingleComparator` 与 `msprobe.pytorch`（包含 `compare_distributed` 等）。
- **下游 / 扩展指南**：
  - 关键数据比对指南（key_data_dump）：指向 Ascend/mstt 仓库 `debug/accuracy_tools/msprobe/docs/zh/other_functions/rl_collect_instruct.md`；
  - 模型层数据比对指南（actor_train_dump、reference_dump、critic_train_dump）：指向 Ascend/msprobe 仓库 `docs/zh/user_guide/accuracy_compare/pytorch_accuracy_compare_instruct.md`。
- **运行时约束**：与"共卡模式（integrated）"场景绑定，意味着该特性的启用与 mindspeed-rl 的分布式拓扑/部署模式存在耦合关系 —— 文档未列出独立的 non-integrated 说明。
- **RL 流程对接**：落盘目录直接对应 RL 训练的五个核心阶段（actor_generate_sequences / actor_compute_log_prob / actor_update / reference_compute_log_prob / critic_compute_values / critic_update），表明 msProbe 在 mindspeed-rl 中以"按 RL 阶段挂载采集点"的形式集成，而非通用 PyTorch profiler 模式。
