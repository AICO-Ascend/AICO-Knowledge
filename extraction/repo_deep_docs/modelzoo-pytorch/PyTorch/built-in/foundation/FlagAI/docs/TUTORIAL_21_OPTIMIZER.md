# How to use Optimizer

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_21_OPTIMIZER.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_21_OPTIMIZER.md

# 一体化深度解读: FlagAI 优化器使用指南

---

## 【定位】

这篇文档解决 FlagAI 框架中"如何在 Trainer 训练流程中选择与加载不同优化器（adam / adamw / lion / adan / adafactor / lamb）"的实操问题，并辅以一段背景性文字说明机器学习中优化器的基本概念。

---

## 【技术要点】

1. **优化器定义与作用**：在深度学习训练阶段，优化器通过计算损失函数对模型参数的梯度，沿着降低损失的方向更新参数，目标是为给定任务找到最优参数集合，从而显著提升训练速度与精度。

2. **常见优化算法族**：原文列举 stochastic gradient descent (SGD)、Adagrad、Adam、RMSprop 等算法，并指出各算法有不同的优缺点，需根据问题、数据集规模、模型复杂度等因素综合选择。

3. **FlagAI 当前支持的优化器列表**：`adam`, `adamw`, `lion`, `adan`, `adafactor`, `lamb`，通过 `Trainer` 的 `optimizer_type` 参数进行指定。

4. **依赖安装三分支**：
   - `adan` → `python3 -m pip install git+https://github.com/sail-sg/Adan.git`
   - `lion` → `pip install lion-pytorch`
   - `lamb` → `pip install torch_optimizer`

5. **Trainer 集成方式**：通过 `Trainer(env_type='pytorch', ..., optimizer_type='lion')` 一行参数即加载指定优化器，无需额外子类化或注册回调。

6. **示例 Trainer 配置关键数字**：`epochs=1`、`batch_size=2`、`eval_interval=100`、`log_interval=10`、`lr=1e-4`、`num_gpus=1`、`weight_decay=1e-2`、`save_interval=1000`。

---

## 【关键机制与数据】

**工作原理（原文）**：优化器"通过计算损失函数相对于模型参数的梯度，并利用该梯度信息沿降低损失的方向更新参数"。这是一个标准的基于梯度的参数更新范式。

**梯度 → 参数更新链路（原文隐含表述）**：损失 → 反向传播求梯度 → 优化器消费梯度 → 按各自策略（如动量、二阶矩估计、自适应学习率）更新参数 → 最小化损失。

**性能/数据信息**：原文**未给出**任何基准测试数据、训练速度对比、收敛曲线或量化性能数字。文档定位为概念+操作示例，不包含实验数据。

**数据流**：用户只需声明 `optimizer_type`，优化器在 `Trainer` 内部被实例化并参与每一步参数更新；其余训练超参（学习率 `lr=1e-4`、权重衰减 `weight_decay=1e-2`）通过 `Trainer` 顶层参数统一传入。

---

## 【表格解读】

**原文无表格**。

（注：原文 Trainer 示例可视为一段类配置展示，但并非 markdown 表格结构；为保留信息完整性，将其作为"代码块解读"补充如下）

| 字段 | 原文字面值 | 含义解读 |
|---|---|---|
| `env_type` | `'pytorch'` | 运行后端类型为 PyTorch |
| `epochs` | `1` | 训练总轮数（演示用，设为 1） |
| `batch_size` | `2` | 每批样本数（演示用极小值） |
| `eval_interval` | `100` | 每 100 步进行一次评估 |
| `log_interval` | `10` | 每 10 步打印一次日志 |
| `experiment_name` | `'glm_large_bmtrain'` | 实验名称 |
| `pytorch_device` | `'cuda'` | 使用 GPU |
| `load_dir` | `None` | 不从已有 checkpoint 加载 |
| `lr` | `1e-4` | 学习率 0.0001 |
| `num_gpus` | `1` | 使用 1 块 GPU |
| `weight_decay` | `1e-2` | 权重衰减 0.01 |
| `save_interval` | `1000` | 每 1000 步保存一次 |
| `hostfile` | `'./hostfile'` | 分布式主机文件路径 |
| `training_script` | `__file__` | 当前训练脚本路径 |
| `deepspeed_config` | `'./deepspeed.json'` | DeepSpeed 配置文件 |
| `optimizer_type` | `'lion'` | **本次示例加载的优化器为 Lion** |

---

## 【公式解读】

**原文无公式**。

文档仅以自然语言定性描述优化器机制（"computing the gradients of the loss function with respect to the model parameters, and using this information to update the parameters in the direction that reduces the loss"），未给出任何具体更新公式（如 SGD 的 $\theta \leftarrow \theta - \eta \nabla L$、Adam 的动量/二阶矩估计式等）。

---

## 【关联】

文档**未提供**任何文末内部链接（已注明"内部链接: (无)"），且正文中也未交叉引用 FlagAI 其他教程/模块。但从内容可推断以下**隐含关联**：

- **`Trainer`**：本文核心入口；优化器选择完全通过 `Trainer` 的 `optimizer_type` 参数实现，说明 `Trainer` 是优化器与训练循环的耦合点。
- **`deepspeed_config` (DeepSpeed)**：示例中同时配置了 DeepSpeed，说明 FlagAI 优化器需与 DeepSpeed 的 ZeRO/优化器分区等机制协同工作。
- **`hostfile`** + **`num_gpus`**：暗示支持分布式训练场景下的优化器行为（如分布式梯度同步、Adam 状态分片等）。
- **外部依赖库**：`adan`（Sail-SG/Adan）、`lion-pytorch`（lisztomania/lion-pytorch 仓库）、`torch_optimizer`（PyTorch 官方优化器集合）——FlagAI 自身并未重新实现这些算法，而是依赖第三方实现。

---

## 【使用方法】

**1. 选择优化器**

FlagAI 支持 6 种：`adam`, `adamw`, `lion`, `adan`, `adafactor`, `lamb`，通过 `Trainer(..., optimizer_type=...)` 指定。

**2. 安装依赖（原文命令）**

| 优化器 | 安装命令（原文逐字） |
|---|---|
| adan | `python3 -m pip install git+https://github.com/sail-sg/Adan.git` |
| lion | `pip install lion-pytorch` |
| lamb | `pip install torch_optimizer` |

（注：原文中 adam、adamw、adafactor 的依赖安装命令**未给出**，推测使用 PyTorch 自带实现或 `torch_optimizer` 中已包含 lamb；原文未涉及。）

**3. 在 Trainer 中启用（原文逐字代码）**

```python
trainer = Trainer(env_type='pytorch',
                  epochs=1,
                  batch_size=2,
                  eval_interval=100,
                  log_interval=10,
                  experiment_name='glm_large_bmtrain',
                  pytorch_device='cuda',
                  load_dir=None,
                  lr=1e-4,
                  num_gpus=1,
                  weight_decay=1e-2,
                  save_interval=1000,
                  hostfile='./hostfile',
                  training_script=__file__,
                  deepspeed_config='./deepspeed.json',
                  optimizer_type='lion')  # load optimizer
```

将 `optimizer_type` 替换为上述 6 种合法值之一，即可切换对应优化器；`lr` 与 `weight_decay` 等学习率/正则超参以 Trainer 顶层参数形式统一配置，无需在优化器层单独传入。
