# 分层ZeRO

> 仓 `mindspeed` · 路径 `docs/zh/features/LayerZeRO.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/LayerZeRO.md

# 分层ZeRO (LayerZeRO) 深度解读

## 【定位】

这篇文档描述的是 mindspeed (昇腾大模型加速库) 中针对**多模态场景下 ZeRO3 通信域过大引入额外通信开销**问题而设计的"分层 ZeRO"优化特性——它在每个 micro-batch 内用 ZeRO3 进行参数重建与销毁，跨 micro-batch 之间用 ZeRO1 划分优化器状态与梯度，从而在保持与 TP+ZeRO1 相当的内存节省效果的同时，借助更大的 CP 并行度加速长序列训练。

---

## 【技术要点】

1. **通信域双层划分**：ZeRO1 通信组覆盖**全部 DP** 并行域，ZeRO3 通信组是 ZeRO1 的**子集**（一般配置在机内，`zero3_size: int > 0`），每个设备上的 LayerZeRO 状态由这两部分共同组成。
2. **ZeRO1 / ZeRO3 分工**：**优化器状态**沿用 ZeRO1 的一维均匀划分；**前向 / 反向运行时参数**则使用 ZeRO3 分片并按需重建，使用完毕后立即销毁完整参数。
3. **跨阶段 hook 注册**：在运行的多个阶段注册 hook 函数，实现 (a) 参数预取/重建/销毁、(b) 梯度内存申请/释放、(c) 梯度同步、(d) 优化器梯度同步这四类逻辑。
4. **ZeRO3 分片一致性约束**：不同 ZeRO3 通信组内 **local rank 一致**的设备必须保存**相同的参数分片**，且所有 ZeRO3 分片在 DP 域内进行划分。
5. **同步时序**：每次优化器更新**前**将梯度同步到 ZeRO1，更新**后**再将 ZeRO1 参数同步回 ZeRO3，从而在跨 micro-batch 边界实现通信隐藏。
6. **使用入口**：通过 `--layerzero --layerzero-config config.yml` 命令行参数启用，行为由 YAML 配置文件驱动；支持的并行组合为 TP + CP + PP (1F1B) + 梯度累积 + 梯度 Offload。

---

## 【关键机制与数据】

**工作原理与数据流（按 micro-batch 内时序梳理）：**

1. **参数重建（ZeRO3 路径）**：进入 micro-batch 前，依据当前层/模块从 ZeRO3 分片中重建完整参数；运行时所有前向、反向计算都以这份"重建参数"的视图（view）进行，避免长期持有完整参数。
2. **计算与梯度累积**：在重建参数上完成前向、反向；反向产生的梯度按 LayerZeRO 的分片规则就地保存，并通过 hook 管理"梯度内存申请 / 销毁"。
3. **梯度同步到 ZeRO1（ZeRO1 路径）**：在每次优化器更新**前**，hook 触发将梯度在 **ZeRO1 通信组（全部 DP 域）**内做 all-reduce 同步，此时完整的梯度暂驻或可选择 Offload（`offload_grads: bool=False`）。
4. **优化器更新**：在 ZeRO1 划分下就地更新优化器状态与参数（这是 ZeRO1 路径，通信域等于全 DP，开销已被 CP 切分序列带来的通信吸收）。
5. **ZeRO1 → ZeRO3 反向同步**：更新完成后，再将 ZeRO1 上持有的最新参数同步回 ZeRO3 分片，供下一个 micro-batch 重建使用；这一步同样在 ZeRO1 通信组内完成。
6. **重建参数销毁**：当层/模块的使用窗口结束，完整参数被立即销毁，内存释放，跨 micro-batch 仍只持久化 ZeRO3 分片 + ZeRO1 优化器状态。

由此形成"ZeRO3 提供重建 → 计算 → 梯度 → ZeRO1 同步 → 优化器 → 反向同步回 ZeRO3 → 销毁"的闭环，将原本 ZeRO3 在全 DP 域上的大通信域拆成**仅在机内的小通信域**，把跨机通信尽量收敛到 ZeRO1 一步。

**性能数据（原文）：**

- 实验对象：MM-OpenSoraPlan1.3 模型训练场景。
- 对比基线：`TP=8 + ZeRO1`；实验组：`CP=8 + 分层ZeRO`。
- 内存对比：两组**内存使用情况基本一致**（即分层 ZeRO 达到与 TP+ZeRO1 近似的内存节省效果）。
- 端到端性能：实验组相对基线提升 **9.7%**。

---

## 【表格解读】

**原文无表格。** 不过原文 YAML 片段本身就是一份"配置项速查表"，下面把它**逐字还原**并逐项解读，作为对原文配置结构的辅助说明（内容完全来自原文 YAML，未做任何增删）：

| 字段 | 类型 / 取值 | 默认 | 含义解读 |
|---|---|---|---|
| `zero3_size` | `int`（大于 0 的整数） | 无默认值 | ZeRO3 通信组的大小；原文建议"一般在机内进行 ZeRO3"，即用机内设备数配置，使 ZeRO3 通信域限制在单机内，从而避开跨机带宽瓶颈。 |
| `transformer_layers` | `Optional[Iterable[torch.nn.Module]]` | `None` | 需要被包装的层 class 的层级 name（`module.submodule.class`）；用于告诉分层 ZeRO 哪些层需要按"重建 → 使用 → 销毁"的窗口化管理。 |
| `param_dtype` | `Optional[Literal["fp16", "bf16", "fp32"]]` | `"fp16"` | 运行时（重建视图后）参数精度，与混合精度策略相关。 |
| `reduce_dtype` | `Optional[Literal["fp16", "bf16", "fp32"]]` | `"fp16"` | 运行时梯度精度（reduce 通信所用精度），同样属于混合精度配置。 |
| `ignored_modules` | `Optional[Iterable[str]]` | `None` | 模型中**不**被分层 ZeRO 管理的模块名（属性名即可）。原文要求：若这些模块需要训练，用户需自行处理梯度/参数同步；若只是不需要分片的非训练模块，也要显式列在这里以避免被分片。原文同时指出非法情况下默认失效为 `None`。 |
| `offload_grads` | `bool` | `False` | 在梯度累积过程中是否 Offload 完整梯度，开启后可进一步压低峰值显存。 |
| `ckpt_load_path` | `str` | `None` | 分层 ZeRO 在相同配置下的 ckpt 绝对路径，用于断点续训。 |
| `autocast_input` | `bool` | `True` | 是否自动把输入 cast 到混合精度。 |
| `autocast_output` | `bool` | `True` | 是否把输出 cast 回 `fp32`。 |

---

## 【公式解读】

**原文无公式。**

原文未给出任何数学公式或伪代码表达式；其核心机制全部用文字 + YAML 配置描述。整套逻辑可视为一个时序过程：

> 重建（ZeRO3）→ 计算 → 梯度 → 同步到 ZeRO1 → 优化器更新 → 同步回 ZeRO3 → 销毁

但这只是文字化的流程描述，并非原文给出的公式或伪代码。

---

## 【关联】

原文未提供任何内部链接，但从内容可以识别出以下**与文中其他特性/模块的耦合关系**（仅基于原文表述）：

- **TP（Tensor Parallel，张量并行）**：原文指出多模态场景 TP 开销"远大于 LLM 场景"，因此 LayerZeRO 的设计目标是**降低对 TP 的依赖**，转而通过 CP 获得并行度——即与 TP 形成"替代/互补"关系，原文明确说目标是达到"与 TP+ZeRO1 近似"的内存效果，但用更小的 TP/更大的 CP 实现。
- **CP（Context Parallel，序列并行）**：原文"使用场景"明确把 CP 作为 LayerZeRO 的协同并行维度，给出的性能对比也是 `CP=8 + 分层ZeRO` vs `TP=8 + ZeRO1`。
- **PP（Pipeline Parallel, 1F1B）**：原文"注意事项"第 1 条列出了支持 TP + CP + PP(1F1B) 并行组合。
- **梯度累积 / 梯度 Offload**：原文在注意事项第 1 条与配置项 `offload_grads` 中同时提及，表明 LayerZeRO 与梯度累积、Offload 是叠加使用的。
- **MegatronModule**：原文"注意事项"第 2 条指出，启用 LayerZeRO 后模型包装从 `MegatronModule` 替换为分层 ZeRO，**依赖 MegatronModule 的开发部分可能失效**——这是一个明确的破坏性变更提示。
- **OpenSoraPlan1.3 / VAE / text_encoder**：原文"注意事项"第 3 条针对 OpenSoraPlan1.3，要求通过 `ignored_modules` 排除 vae 和 text_encoder，避免对它们做参数重建（这两类模块在多模态模型中通常以独立子网络形式存在，无需参与 ZeRO 管理）。
- **ZeRO1 / ZeRO3**：作为机制依赖，ZeRO1 提供优化器状态与梯度的全 DP 域划分与同步；ZeRO3 提供机内（子集 DP）参数分片与重建。LayerZeRO 是这两者的组合封装。
- **Checkpoint / pickle 安全**：原文"注意事项"第 4 条提示序列化链路依赖 pickle，要求 UnderFS 存储目录及上层目录的写权限严格管控，避免反序列化注入。

---

## 【使用方法】

**启用命令（原文）：**

```bash
--layerzero
--layerzero-config config.yml
```

即通过 `--layerzero` 开关启用特性，并通过 `--layerzero-config` 指定 YAML 配置文件路径。配置文件的全部可选项已在上文"表格解读"中**逐字还原**，包括 `zero3_size`、`transformer_layers`、`param_dtype`、`reduce_dtype`、`ignored_modules`、`offload_grads`、`ckpt_load_path`、`autocast_input`、`autocast_output`。

**额外的模型级配置要点（原文注意事项）：**

1. **支持的并行组合**：TP + CP + PP(1F1B) + 梯度累积 + 梯度 Offload。
2. **模型包装替换**：模型从 `MegatronModule` 替换为分层 ZeRO 包装，原依赖 `MegatronModule` 的代码可能失效。
3. **OpenSoraPlan1.3 特殊配置**：需额外设置 `ignored_modules`，**按属性名**填入需要排除的模块（如 vae、text_encoder 对应的子模块），以避免这些模块被纳入参数重建。
4. **Checkpoint 安全约束**：CheckPoint 序列化依赖 pickle 组件，必须严格控制 UnderFS 存储目录及上层目录的写权限，禁止未授权写访问，以规避 pickle 反序列化注入风险。

> 原文未提供除上述 YAML 字段与命令行参数之外的"环境变量 / API 调用 / 编程接口"等其它启用方式。
