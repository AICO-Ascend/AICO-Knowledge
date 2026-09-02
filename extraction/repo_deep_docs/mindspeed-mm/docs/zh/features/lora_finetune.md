# LoRA 微调简介

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/lora_finetune.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/lora_finetune.md

# LoRA 微调文档深度解读

## 【定位】

本文档面向使用 mindspeed-mm 多模态大模型套件进行模型轻量化微调的用户，系统阐述 LoRA（Low-Rank Adaptation，低秩适配）技术在多模态模型（如 Qwen2-VL）微调任务中的原理、使能方式、权重合并流程及关键参数配置。

---

## 【技术要点】

1. **低秩矩阵替代全量更新**：LoRA 的核心思想是用两个低秩矩阵 $A$ 和 $B$ 的乘积替代对原始权重矩阵的直接更新，即 $W' = W + A \cdot B$，从而显著降低训练参数量与存储开销。

2. **通过 shell 参数使能 LoRA**：在模型微调 shell 脚本中追加 `--lora-target-modules` 参数即可启用 LoRA，示例命令为：
   ```shell
   --lora-target-modules linear_qkv linear_proj linear_fc1 linear_fc2
   ```

3. **mcore 与 legacy 模型的模块选择差异**：
   - mcore 模型可选模块：`linear_qkv`, `linear_proj`, `linear_fc1`, `linear_fc2`
   - legacy 模型可选模块：`query_key_value`, `dense`, `dense_h_to_4h`, `dense_4h_to_h`

4. **关键超参数与推荐值**：
   - `--lora-r`：LoRA rank，决定低秩矩阵维度；过低会限制表达能力。
   - `--lora-alpha`：LoRA 缩放系数，**原文建议保持 `α/r` 为 2**。
   - `--lora-dropout`：LoRA 模块的 dropout 比例，**默认值为 `0`**。

5. **LoRA 权重与原始权重合并**：通过 `merge_lora` 合并脚本执行，需配置四个目录/开关参数：`base_save_dir`（原始权重目录）、`lora_save_dir`（LoRA 权重目录）、`merge_save_dir`（合并权重保存目录）、`use_npu`（是否启用 NPU 加速）。

6. **续训模式的双路径加载**：使用 `--load` 加载 LoRA 权重（路径为 `CKPT_SAVE_DIR`），同时配合 `--load-base-model` 加载原始基础模型权重（路径为 `CKPT_LOAD_DIR`），二者缺一不可。

7. **冻结模块的自动规避**：多模态模型中已被冻结的模块不会参与 LoRA 微调，无需用户额外处理。

---

## 【关键机制与数据】

**工作原理（原文章节结构归纳）：**

- **权重更新分解**：传统微调直接修改权重矩阵 $W$；LoRA 在每一层权重矩阵上"外挂"两个低秩矩阵 $A$ 和 $B$，使权重更新量被参数化为 $A \cdot B$，从而将"对全秩权重 $W$ 的更新"转化为"对低秩乘积 $A \cdot B$ 的学习"。由于 $A$ 和 $B$ 的秩远小于 $W$ 的维度，参数量、显存占用与计算量均显著下降。

- **数据流（基于参数语义推断）**：
  1. 训练阶段：原始权重 $W$ 冻结，仅训练低秩矩阵 $A$、$B$；脚本通过 `--lora-target-modules` 选定要插入 LoRA 的层。
  2. 保存阶段：开启 LoRA 时 `--save` 仅保存 LoRA 模块权重，不保存完整模型。
  3. 续训/合并阶段：`--load` + `--load-base-model` 联合加载；或通过 `merge_lora` 脚本将 LoRA 权重 $A \cdot B$ 合并回原始 $W$，得到 $W' = W + A \cdot B$ 并写入 `merge_save_dir`。

- **性能数据**：原文未提供具体的训练速度、显存占用或吞吐量数据，亦未给出 LoRA 秩与性能对比曲线。

- **结构示意**：原文引用了 `sources/images/lora_finetune/lora_model.png` 作为 LoRA 模型结构示意（图示内容本解读中未呈现）。

---

## 【表格解读】

**原文无表格。**

全文采用平铺的参数说明列表（`--load`、`--load-base-model`、`--lora-r`、`--lora-alpha`、`--lora-dropout`、`--lora-target-modules`、`--save`）逐条展开，未以表格形式组织参数对照或性能对比。

---

## 【公式解读】

原文给出的核心公式：

$$
W' = W + A \cdot B
$$

- **$W'$**：更新后的权重矩阵，是模型在推理时实际使用的等效权重。
- **$W$**：原始预训练权重矩阵，在 LoRA 训练阶段保持冻结，不参与梯度更新。
- **$A$**：第一个低秩矩阵，通常形状为 $(\text{in\_dim}, r)$，随机初始化。
- **$B$**：第二个低秩矩阵，通常形状为 $(r, \text{out\_dim})$，初始化为零矩阵（保证训练初始阶段 $A \cdot B = 0$，即 $\Delta W = 0$，模型起始行为与原始预训练模型一致）。
- **$A \cdot B$**：两个低秩矩阵的乘积，构成对原始权重 $W$ 的低秩更新量 $\Delta W$。
- **$r$**：LoRA 秩（rank），由 `--lora-r` 指定，控制低秩矩阵的"压缩比"；$r$ 越小，参数越省，但表达能力上限越低。
- **$\alpha$（`--lora-alpha`）**：缩放系数，实际生效时通常以 $\frac{\alpha}{r}$ 作为更新量的整体缩放因子，原文建议保持 $\frac{\alpha}{r} = 2$。

**作用**：该公式表明 LoRA 在数学上将"全秩权重更新"近似为"低秩权重更新"，在不改变推理前向计算路径（输出仍为 $W' x$）的前提下，把可训练参数从 $|W|$ 压缩到 $|A| + |B|$，从而实现参数高效微调。

---

## 【关联】

- **上游理论参考**：标注了 LoRA 原论文 [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)，作为方法来源。
- **模型对象关联**：文档示例明确指向 `Qwen2-VL` 微调任务，表明 LoRA 微调在 mindspeed-mm 中已适配 Qwen2-VL 多模态模型。
- **模块体系关联**：可插入 LoRA 的模块按模型后端划分为 **mcore** 与 **legacy** 两套体系，说明 mindspeed-mm 同时支持两种 Megatron 衍生实现路径；多模态场景需根据实际模型结构在两套模块名中选择。
- **配套脚本关联**：`merge_lora` 合并脚本作为 LoRA 权重合并的标准入口，与训练脚本形成"训练→保存→合并"闭环。
- **续训链路关联**：`--load`（加载 LoRA）与 `--load-base-model`（加载原始基础模型）需联合使用，构成 LoRA 续训的标准加载模式。
- **冻结机制关联**：与多模态模型中已存在的"参数冻结"机制耦合——冻结模块自动跳过 LoRA 微调，无需额外配置。
- **原文内部链接**：本文档**未提供任何内部链接**（文末"内部链接: (无)"），与其他 feature 文档之间的跳转关系在原文中未显式给出。

---

## 【使用方法】

**1. 训练阶段使能 LoRA**

在微调任务 shell 脚本中追加 `--lora-target-modules` 参数（以 `Qwen2-VL` 为例）：

```shell
--lora-target-modules linear_qkv linear_proj linear_fc1 linear_fc2
```

可选模块按模型类型区分：
- mcore 模型：`linear_qkv`, `linear_proj`, `linear_fc1`, `linear_fc2`
- legacy 模型：`query_key_value`, `dense`, `dense_h_to_4h`, `dense_4h_to_h`

**2. 关键超参数配置**

| 参数 | 作用 | 原文默认/建议 |
|---|---|---|
| `--lora-r` | 低秩矩阵维度 | 原文未给具体数值 |
| `--lora-alpha` | 缩放系数 | 建议 `α/r = 2` |
| `--lora-dropout` | LoRA 模块 dropout | 默认 `0` |
| `--save` | 权重保存路径 | 开启 LoRA 时仅保存微调模块权重 |

**3. 权重合并**

使用 `merge_lora` 合并脚本，需设置：
- `base_save_dir`：原始权重目录
- `lora_save_dir`：LoRA 权重目录
- `merge_save_dir`：合并权重保存目录
- `use_npu`：是否启用 NPU 加速

**4. 续训加载**

同时指定：
- `--load`：加载 `CKPT_SAVE_DIR` 下的 LoRA 权重
- `--load-base-model`：加载 `CKPT_LOAD_DIR` 下的原始基础模型权重

若不指定 `--load`，模型会随机初始化权重。

**5. 注意事项**

- 多模态模型中被冻结的模块不会参与 LoRA 微调（行为自动，无需额外配置）。

## 图文联合解读

- `lora_model.png`: 图示展示输入 x 经两条并行路径汇成输出 h：左侧为预训练权重 W∈ℝ^(d×d) 全量矩阵，右侧为低秩瓶颈分支，由 A(N(0,σ²) 高斯初始化)与 B(=0) 串接而成，秩 r≪d，两路输出相加。论证 LoRA 通过冻结 W、以低秩 A·B 注入更新实现参数高效微调，与文档公式 W'=W+A·B 完全对应，直观呈现参数量压缩与"训练前等价原模型"的初始化设计。
