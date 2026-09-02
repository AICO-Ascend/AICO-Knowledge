# MindSpeed MM 训练框架介绍

> 仓 `mindspeed-mm` · 路径 `docs/zh/pytorch/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/pytorch/introduction.md

# MindSpeed MM 训练框架介绍 — 一体化深度解读

---

## 【定位】

本篇是 MindSpeed MM（华为昇腾面向大规模分布式训练的多模态大模型套件）的总览级介绍文档，阐述其"硬件—软件—套件"三层架构、组件构成、双分布式后端设计，以及训练任务的端到端调用链路，作为用户快速建立全局认知的入门指引。

---

## 【技术要点】

1. **三层整体架构**：MindSpeed MM 整体分为昇腾硬件基础设施层、软件基础能力层（CANN + HCCL 集合通信库、PyTorch + TorchNPU）、多模态核心套件层（自研 MindSpeed MM），CANN 是"将模型操作高效映射到硬件指令"的核心引擎，HCCL 是"达成近线性加速比"的关键通信库。

2. **模型支持范围（原文数字）**：覆盖 **20+** 开源多模态模型，包括：
   - 生成模型：Wan、HunyuanVideo
   - 理解模型：QwenVL、InternVL
   - 全模态模型：Qwen-Omni
   
   并提供"预训练/微调/评估/在线推理"四阶段启动脚本，可"一键拉起训练任务"。

3. **模型组件分层**：分为**高阶抽象类（组装类）**、**原子模型类**、**公共组件**三层——高阶封装类包括 SoRAModel（多模态生成）、VLModel（多模态理解）、TransformersModel（Transformers）；原子类包括 text_decoder、audio、dit；公共组件 common 包括 norm、rope、embedding、spec。

4. **全生命周期工具链**：涵盖数据预处理与工程、大规模预训练、指令微调与领域适配、模型权重转换、高性能在线推理、自动化评估共 6 个环节。

5. **多模态加速特性 6 大方向**：异构数据管道优化、高效并行算法、通算掩盖、多模态负载均衡、动态显存管理（重计算、分级存储）、长序列优化。

6. **双后端并行策略**：
   - **Megatron 后端**：基于 MindSpeed Core（即 Megatron-LM 内核）的 PTD（Pipeline + Tensor + Data）混合并行，强调"超大规模模型训练中的高效扩展性与系统稳定性"。
   - **FSDP2 后端**：基于 Fully Sharded Data Parallel 2 全分片数据并行，强调"并行策略与模型结构高度解耦、实现简洁且易于扩展"。
   - **启用方式**：当前 FSDP2 训练流程嵌入在 Megatron training 里，需在脚本中编写 `GPT_ARGS、 MM_ARGS、OUTPUT_ARGS` 参数，并通过 `--use-torch-fsdp2` 标志启用。FSDP2 后端已应用于 **Wan2.2、Qwen3VL** 等开源模型。

7. **训练调用栈（5 层）**：训练 bash 脚本 → 训练入口 → MindSpeed MM 接口 → MindSpeed-core 接口 → Megatron 接口。

---

## 【关键机制与数据】

### 1. 架构协同机制（自上而下）

```
┌─────────────────────────────────────────┐
│  多模态核心套件层：MindSpeed MM（自研）        │
│  - 预置模型 / 模型组件 / 加速特性 / 双后端     │
├─────────────────────────────────────────┤
│  软件基础能力层                            │
│  - CANN：高度优化算子 + HCCL 集合通信库      │
│  - PyTorch + TorchNPU：无缝对接昇腾硬件      │
├─────────────────────────────────────────┤
│  昇腾硬件基础设施层                          │
└─────────────────────────────────────────┘
```

**工作原理（原文）：** CANN "将模型中的各类操作高效映射到硬件指令"，通过 HCCL 实现"设备间的高速通信"，从而"达成近线性加速比"；TorchNPU 插件则使开发者"以熟悉的编程范式与 API，利用昇腾的算力优势"。

### 2. 训练流程数据流（按 Mermaid 时序图逐步解析）

| 阶段 | 调用方 → 被调用方 | 关键动作（原文标注） |
|---|---|---|
| 启动 | user → A (pretrain_xxx.py) | 执行 `pretrain_xxx.sh` |
| 自适应 | A → A | `mindspeed.megatron_adaptor`（Megatron 适配） |
| 初始化 | A → B → D → B | `pretrain` → `initialize_megatron` → 返回 `init args/global_vars/distributed` |
| Patch 应用 | B → B | `apply_patches_from_config`（依据配置注入补丁） |
| 模型构造 | B → D → D → A → D | `setup_model_and_optimizer` → `get_model` → 调用 `model_provider`（用户侧） → 返回 model |
| 并行包装 | D → C → D | `torch_fully_sharded_data_parallel_init` → 返回 **FSDP2 model** |
| 优化器与调度器 | C → C → C | `get_megatron_optimizer` → `get_optimizer_param_scheduler` → `load_checkpoint` |
| 数据管线 | C → C → A → C | `build_train_valid_test_data_iterators` → `_loaders` → `_datasets` → 调用用户 `train_valid_test_datasets_provider` → 返回 `train_ds / valid_ds / test_ds` |
| 训练循环 | B → C → C → C → A → B → A → A → C | `train_step` 循环：`train` → `train_step` → `get_forward_backward_func` → `forward_step` → 用户 `get_batch` → `model.forward` → `loss_func` → 返回 loss |
| 保存与评估 | B → C → B → C → B | `save_checkpoint` → `evaluate_and_print_results` |

**关键数据流说明（原文）：** 训练入口文件 (`mindspeed_mm/pretrain_xxx.py`) 主要实现三个 provider 方法：
- `model_provider`：模型初始化
- `data_provider`：数据提供
- `forward_step`：模型前向

### 3. 双后端演化逻辑（原文描述）

- **过去：** Megatron PTD 混合并行是"早期阶段便集成并深度优化"的能力，主打"超大规模模型训练中的高效扩展性与系统稳定性"。
- **现在：** "计算硬件的快速迭代与高速互联网络技术的普及"，"通信瓶颈逐步缓解"；"多模态模型结构日趋多样化和复杂化"，对框架灵活性要求提升。
- **演进结果：** FSDP2 因"并行策略与模型结构高度解耦、实现简洁且易于扩展"，成为"快速适配各类新兴架构的理想选择"；MindSpeed MM "在已有 Megatron 后端的基础上，进一步增强了对 FSDP2 的兼容与优化"，目标是"兼顾训练效率与代码可维护性"。

### 4. 性能与适用场景数据（原文）

- **加速比目标：** CANN + HCCL 实现"近线性加速比"。
- **支持规模：** "20+" 开源多模态模型。
- **已验证模型（FSDP2）：** Wan2.2、Qwen3VL。

---

## 【表格解读】

**原文无表格**（文档中未提供参数表、性能对比表或配置项表格，相关信息以章节文字和 Mermaid 时序图呈现）。

---

## 【公式解读】

**原文无公式**（文档未包含任何 LaTeX 公式或伪代码形式的算法表达式）。

---

## 【关联】

1. **脚本层关联**：`examples/xxx_model/pretrain_xxx.sh` 训练 bash 脚本需按 README 配置三类参数：
   - `DISTRIBUTED_ARGS`（分布式参数）
   - `model.json`（模型配置）
   - `data.json`（数据配置）

2. **训练入口关联（按模型类型）：**
   - 多模态生成模型 → `pretrain_sora.py`
   - 多模态理解模型 → `pretrain_vlm.py`
   - Transformers 模型 → `pretrain_transformers.py`

3. **统一接口层**：`mindspeed_mm/training.py` 提供 `pretrain、train、train_step` 三个最通用基础方法，构成所有模型入口的上层统一调用面。

4. **下游 Megatron 依赖**：通过 MindSpeed-Core 的 **Megatron-adapter**、**patch 能力**，复用 Megatron 的"通信组构建、优化器、PTD 并行、日志、权重加载保存"等基础能力。

5. **外部链接（FSDP2 详细配置）：** 文档指向 `https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/fsdp2.md`，详细说明 FSDP2 配置项；本 introduction 仅给出启用开关 `--use-torch-fsdp2`。

6. **模型组件组合关系**：
   - 高阶组装类（SoRAModel / VLModel / TransformersModel）**由**原子类（text_decoder、audio、dit）+ 公共组件（common：norm、rope、embedding、spec）**组装而成**。
   - 三类高阶类分别对应"多模态生成、多模态理解、Transformers"三大模型族群。

7. **架构图引用**：文中嵌入架构示意图 `mm-arch.png`，呈现三层堆叠结构与组件构成。

---

## 【使用方法】

### 启用 FSDP2 后端训练（原文有提及）

在训练 bash 脚本中：
1. 按 README 配置 `DISTRIBUTED_ARGS`、`model.json`、`data.json`。
2. 在 Megatron 参数校验段（`GPT_ARGS / MM_ARGS / OUTPUT_ARGS`）中加入标志：
   ```bash
   --use-torch-fsdp2
   ```
   该标志"标识使用 FSDP2 训练"。
3. FSDP2 的具体配置项需查阅外部链接文档：
   [FSDP2 使用文档](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/fsdp2.md)

### 启动训练任务

```bash
# 路径：examples/xxx_model/pretrain_xxx.sh
bash examples/xxx_model/pretrain_xxx.sh
```

### 一键拉起能力

原文称 MindSpeed MM 提供"预训练/微调/评估/在线推理启动脚本，用户可以一键拉起训练任务"，但**具体的命令模板、环境变量、依赖安装步骤、参数默认值等启用细节，原文未涉及**，需参考各模型子目录下的 README 与 examples 脚本。
