# MindSpeed-MM 评测框架使用指南

> 仓 `mindspeed-mm` · 路径 `docs/zh/guides/development/evaluation_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/guides/development/evaluation_guide.md

# MindSpeed-MM 评测框架使用指南 — 深度解读

## 【定位】

本文档系统阐述了 MindSpeed-MM 基于 PyTorch FSDP2 后端构建的评测框架，以 Qwen3.5 MoE 模型在 VQA v2.0 验证集上的端到端评测为示例，串联起"数据集准备 → 启动脚本 → YAML 配置 → 参数说明 → 结果输出 → 适配范围 → 新任务接入"的全链路流程，旨在为多模态大模型在训练阶段的效果验证提供一个可复用、可扩展的标准评测范式。

---

## 【技术要点】

1. **三段式评测工程结构**：评测任务由"数据集目录 + Shell 启动脚本 + YAML 配置文件"三件套共同构成；其中 YAML 中 `parallel.model.inference.evaluation` 四段分别承担切分计划、模型声明、推理参数、评测任务的核心职责。

2. **FSDP2 全分片配置**：通过 `fully_shard_parallel_size: auto`、`fsdp_plan.apply_modules/hook_modules` 实现按模块粒度的分片；关键参数包括 `param_dtype: bf16`、`reduce_dtype: fp32`、`reshard_after_forward: true`、`num_to_forward_prefetch: 1`、`num_to_backward_prefetch: 0`、`cpu_offload: false`，并通过 `ulysses_parallel_size: 1` 与 `expert_parallel_size: 1` 控制序列并行与专家并行维度，专家路由通过 `ep_plan.dispatcher: alltoall` 实现。

3. **内置 VQA2 数据加载机制**：`VQA2ValDataset` 通过 `image_id` 在 `val2014/` 目录构造图片路径，并在问题之后追加约束文本 `"Answer the question using a single word or phrase."`，强制模型以短语/单词形式作答以匹配 VQA v2.0 计分规范。

4. **评测注册表双字典机制**：在 `eval_dataset_dict`（数据集类）和 `eval_impl_dict`（评测器类）中使用相同 key 进行注册，YAML 中通过 `evaluation.dataset_type` 一字段即可同时选择数据集与评测器，新增任务只需在两字典添加同名键即可贯通。

5. **评测框架复用推理框架**：复用 `InferenceRunner` 完成模型构建、FSDP2 分片、权重加载与文本生成，新增"评测语义层"通过 `BaseEvaluator` 的 `update`/`finalize` 双方法累计状态并产出指标，做到推理与评测解耦。

6. **推理与生成参数**：Qwen3.5 MoE 评测配置 `attn_implementation: flash_attention_2`、`gdn_implementation: eager`、`causal_conv1d_implementation: eager`、`use_grouped_expert_matmul: true`、`enable_thinking: false`，生成阶段 `max_new_tokens: 32`、`do_sample: false`、`repetition_penalty: 1.0`、`use_cache: true`，并通过 `init_model_with_meta_device: true` 与 `use_deter_comp: false` 控制初始化方式。

---

## 【关键机制与数据】

### 工作原理（评测时序）
原文以 Mermaid 时序图刻画了 `User → EvaluationRunner → Registry → EvalDataset → InferenceRunner → ModelAdapter → FSDP2 模型 → BaseEvaluator` 的七方协作流程：

- **User → Runner**：读取 YAML 启动评测；
- **Runner → Infer**：初始化模型、应用切分计划并加载权重；
- **Runner → Registry**：根据 `dataset_type` 获取已注册的 Dataset 与 Evaluator；
- **逐样本循环**：依次执行 `Dataset 获取样本 → Adapter.preprocess(messages) → Model.generate(**inputs, **generation) → Adapter.decode(inputs, outputs)`；
- **rank 0 汇总**：在 rank 0 上对每个推理结果调用 `Evaluator.update(item, prediction)`，最后调用 `Evaluator.finalize()` 输出预测文件与指标文件。

### 数据流
- **输入侧**：YAML → Runner → Registry 解析；Dataset 从 `dataset_path` 读取样本；
- **推理侧**：Adapter 负责多模态消息的多模态预处理与文本解码；
- **评测侧**：样本标注与模型预测进入 Evaluator，写出 `*_predictions.json` 与 `*_metrics.json`。

### 性能/示例数据（原文示例输出）
> ⚠ 以下数字来自文档内嵌的"评测指标文件内容示例"，**非文档承诺的真实基准**。

- 原文示例 `overall` 准确率为 **87.1**。
- `answer_type` 分布：`number` 90.0、`other` 77.21、`yes/no` 96.5。
- `question_type` 中 `none of the above` 72.5、`what` 15.0、`where is the` 30.0、`why is the` 60.0、`how many` 89.38、`what is` 84.0 等若干题型准确率从 15.0 到 100.0 不等。
- 启动脚本核心环境变量：`NON_MEGATRON=true`、`MULTI_STREAM_MEMORY_REUSE=2`、`TASK_QUEUE_ENABLE=2`、`ASCEND_LAUNCH_BLOCKING=0`、`ACLNN_CACHE_LIMIT=100000`、`CPU_AFFINITY_CONF=1`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`。
- 分布式参数：`NPUS_PER_NODE=8`、`MASTER_PORT=6000`、`NNODES=1`。
- 生成参数：最长 32 token，关闭采样，重复惩罚 1.0，启用 cache。

---

## 【表格解读】

### 表 1：evaluation 配置段参数说明（原文逐字还原）

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `dataset_type` | str | `vqa2_val` | 评测任务注册名，用于选择评测数据集和评测器。须同时与 `eval_dataset_dict` 和 `eval_impl_dict` 中注册的 key 一致。 |
| `dataset_path` | str | — | 评测数据集的根目录或数据文件路径。 |
| `max_samples` | int \| null | `null` | 最多参与评测的样本数。`null` 表示使用完整评测数据集，可在功能调试时设置较小值。 |
| `result_output_path` | str | `./evaluation_outputs` | 预测结果和评测指标的保存目录。 |

**逐行解读**：
- `dataset_type`：作为评测入口路由键，必须满足"数据集字典 key == 评测器字典 key == YAML 字段值"三一致，否则注册表查询失败。
- `dataset_path`：仅指向根目录，具体内部布局（图片目录、JSON 文件）由对应 `EvalDataset` 子类决定，例如 VQA 需含 `val2014/` 与两个 JSON 标注文件。
- `max_samples`：调试友好型开关，置 `null` 走全量；设为正整数可在功能调试阶段快速验证流程是否跑通。
- `result_output_path`：双产物目录，预测文件按 `<model_id>_<dataset_name>_predictions.json` 命名，指标文件按 `<model_id>_<dataset_name>_metrics.json` 命名。

### 表 2：评测数据集与评测指标适配清单（原文逐字还原）

| 评测数据集 | 注册名称 | 评测指标 | 说明 |
| :--- | :--- | :--- | :--- |
| VQA v2.0 验证集 | `vqa2_val` | `overall`、`answer_type`、`question_type` | 按 VQA v2.0 官方计分规则统计整体准确率，并分别按答案类型和问题类型汇总。 |

**逐行解读**：
- 当前仅一行记录，说明原生支持的评测任务处于"vqa2_val 单点突破"阶段，其他任务（如文档 MME、MMBench 等常见榜单）需通过后续"评测任务适配"流程扩展。
- 三类指标 `overall / answer_type / question_type` 完整覆盖了 VQA v2.0 官方评测的三个切面：全局、按答案词性类别细分、按问题首词型细分。

---

## 【公式解读】

**原文无公式**。文档以 Mermaid 时序图与 YAML 配置形式描述机制，未给出 LaTeX 或伪代码形式的公式化表达。

---

## 【关联】

- **PyTorch FSDP2 后端**：本文评测框架建立在 FSDP2 全分片方案之上，与 `parallel.fully_shard_parallel_size`、`fsdp_plan` 配置直接耦合；该能力由同仓其他 FSDP 模块提供（详见 `mindspeed_mm/fsdp/` 目录下的训练/推理实现，文档未给出内部跳转链接）。
- **推理框架（InferenceRunner）**：评测框架"复用"推理框架完成模型构建、分片、权重加载与生成，新增内容仅为 `BaseEvaluator` 评测语义层，与 `mindspeed_mm/fsdp/inference/` 体系共享模型 Adapter。
- **多模态插件体系**：YAML 中 `plugin` 字段指向 `mindspeed_mm/fsdp/models/qwen3_5_moe`，表明评测框架与模型插件统一在 `mindspeed_mm/fsdp/models/` 下注册，与训练/推理共享同一套模型实现。
- **评测注册表**：`mindspeed_mm/fsdp/evaluation/eval_datasets/__init__.py` 与 `mindspeed_mm/fsdp/evaluation/eval_impl/__init__.py` 中的 `eval_dataset_dict` 与 `eval_impl_dict` 构成评测任务双注册表，新增任务必须同步向两者注册。
- **模型 README**：启动脚本前置条件中要求"运行前需按照模型 README 完成环境配置"，说明评测流程与各模型 README 存在隐式依赖。

（文档内部未提供锚点链接，以上关联关系基于目录结构与配置字段推断。）

---

## 【使用方法】

### 启用方式

**Step 1 — 准备数据集**：按文档给出的目录布局准备 VQA v2.0 验证集：`data/vqa2_val/{v2_OpenEnded_mscoco_val2014_questions.json, v2_mscoco_val2014_annotations.json, val2014/*.jpg}`。

**Step 2 — 创建启动脚本 `examples/qwen3_5/qwen3_5_moe_evaluation.sh`**：脚本需 source 昇腾 CANN 环境，并设置 7 个环境变量（`NON_MEGATRON=true`、`MULTI_STREAM_MEMORY_REUSE=2`、`TASK_QUEUE_ENABLE=2`、`ASCEND_LAUNCH_BLOCKING=0`、`ACLNN_CACHE_LIMIT=100000`、`CPU_AFFINITY_CONF=1`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`），按 `NPUS_PER_NODE=8 / NNODES=1` 启动 `torchrun` 调用 `mindspeed_mm/fsdp/evaluation/evaluation_runner.py`，并通过 `config_path=examples/qwen3_5/qwen3_5_moe_evaluation.yaml` 指定配置。

**Step 3 — 创建 YAML 配置 `examples/qwen3_5/qwen3_5_moe_evaluation.yaml`**：将 `model.model_name_or_path` 替换为实际 Hugging Face 模型路径（原文采用 YAML 锚点 `&HF_MODEL_LOAD_PATH` 与 `processor_path: *HF_MODEL_LOAD_PATH` 实现复用），`inference.load` 同样指向该路径，`evaluation.dataset_path` 指向数据集根目录。

**Step 4 — 启动评测**：在仓库根目录执行 `bash examples/qwen3_5/qwen3_5_moe_evaluation.sh`。

**Step 5 — 查看输出**：在 `evaluation.result_output_path`（默认 `./evaluation_outputs`）下检查 `*_predictions.json` 与 `*_metrics.json`，控制台同步打印结果文件路径与最终评测指标。

### 调试模式

如需快速验证流程，将 YAML 中 `evaluation.max_samples` 由 `null` 改为较小正整数即可启用子集评测。

### 新任务接入流程

1. 在 `mindspeed_mm/fsdp/evaluation/eval_datasets/<dataset_name>.py` 新增数据集类（须实现 `__init__(dataset_path, max_samples=None)`、`__len__`、`__getitem__`），返回字段至少包含 `"text"`、`"image"`、`"sample_id"`、`"answers"`；
2. 在 `mindspeed_mm/fsdp/evaluation/eval_impl/<dataset_name>.py` 新增评测器类，继承 `BaseEvaluator`，实现 `__init__(result_output_path, model_name, dataset_name)`、`update(item, prediction)`、`finalize()`；
3. 分别在 `eval_datasets/__init__.py` 的 `eval_dataset_dict` 与 `eval_impl/__init__.py` 的 `eval_impl_dict` 中使用**同名 key** 完成注册；
4. 修改待评测任务的 YAML，将 `evaluation.dataset_type` 切换为新 key 即可触发。

### 注意事项（原文强调）

1. 文档明确指出本评测流程"仅适用于模型训练阶段的效果验证与结果比对，未针对线上部署场景做性能优化"，存在性能加速需求时建议替换专业推理加速库及对应优化组件。
