# 非均匀 Ulysses CP 切分

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/unaligned_ulysses_cp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/unaligned_ulysses_cp.md

# 非均匀 Ulysses CP 切分 — 一体化深度解读

---

## 【定位】

这篇文档描述 mindspeed-mm 在 Ulysses CP（Context Parallel，序列并行）切分方向上对**非均匀序列长度**场景的适配能力：基于 All2All 算子对输入/输出 List 按序列长度做非均匀切分，从而让 Ulysses 序列并行算法在多模态模型常见的「各卡序列长度不一致」场景下能正常生效，无需额外配置。

---

## 【技术要点】

1. **核心机制 — All2All 的非均匀切分**
   原文："Ulysses CP算法基于All2All算子，对All2All算子的Input List与Output List根据序列长度进行非均匀切分，使能Ulysses算法。" 即不是按等分（balanced）方式拆分序列维度，而是按各 rank 的实际序列长度来切分 All2All 的输入/输出 List。

2. **双后端原生支持**
   原文："Ulysses CP 在 FSDP2 与 MCORE 两个后端均支持，各卡序列长度不一致（非均匀）时也能正常切分，无需额外配置。" FSDP2 与 MCORE（Megatron）两条后端路径均已适配，**非均匀场景不需任何额外开关**。

3. **FSDP2 后端 — 并行度配置**
   - `parallel.ulysses_parallel_size`：默认 `1`，**大于 1 时启用** Ulysses CP，示例值 `2`。
   - 必须配合 `model.attn_implementation: flash_attention_2`，否则开启 Ulysses CP 不合法。

4. **MCORE 后端 — 通过启动参数启用**
   - 在 `examples/qwen2.5vl/finetune_qwen2_5_vl_72b.sh` 中默认设置 `CP=1`，按需调整。
   - 在同一脚本的 `GPT_ARGS` 中追加 `--context-parallel-algo ulysses_cp_algo`。

5. **典型参考配置**
   - FSDP2 端参考 `examples/qwen3vl/qwen3vl_30B_config_v1.yaml`。
   - MCORE 端参考 `examples/qwen2.5vl/finetune_qwen2_5_vl_72b.sh`。

---

## 【关键机制与数据】

- **问题动因（原文）**：CP 是一种针对长序列数据的并行化技术，处理长序列具有显著优势；而"多模态模型存在大量序列长度非均匀场景，需要进行相应的适配。" 这是引入非均匀切分的直接动机。

- **工作原理（原文）**：Ulysses CP 算法基于 All2All 算子，对 All2All 算子的 Input List 与 Output List **根据序列长度**进行非均匀切分，使能 Ulysses 算法。文档中配有一张示意图 `ulysses.png`（位于 `sources/images/`），但文档正文未给出该图的具体数据流说明。

- **数据流要点**：非均匀切分的核心是让 All2All 的输入/输出 List 反映各 rank 的实际序列长度差异，而非固定等分，从而在 All2All 通信阶段保持正确性。

- **性能数据**：原文未给出任何基准测试数字（如加速比、吞吐、通信开销等），本节不臆造。

---

## 【表格解读】

**原文无表格**。文档中不存在任何参数对照表、性能对比表或配置矩阵，所有配置均以 YAML 代码片段和 shell 命令行内嵌形式给出。

---

## 【公式解读】

**原文无公式**。文档未给出任何 LaTeX 公式或伪代码形式的数学表达。All2All 非均匀切分的具体数学定义（如输入 List $L_{in}$ 与输出 List $L_{out}$ 的映射关系）未在文档中显式给出。

---

## 【关联】

文档通过示例脚本指向具体的模型/配置资产，构成与仓内其他模块的上下游关联：

- **FSDP2 后端 → 参考配置**：`examples/qwen3vl/qwen3vl_30B_config_v1.yaml`（Qwen3-VL 30B 模型 YAML 配置示例，用于查看 `parallel.ulysses_parallel_size` 与 `model.attn_implementation` 的实际写法的上下文）。
- **MCORE 后端 → 启动脚本**：`examples/qwen2.5vl/finetune_qwen2_5_vl_72b.sh`（Qwen2.5-VL 72B 的 Megatron 微调脚本，需在其中设置 `CP=1` 并追加 `--context-parallel-algo ulysses_cp_algo`）。
- **依赖注意力实现**：`flash_attention_2` 是 Ulysses CP 在 FSDP2 后端的硬性要求，隐含与仓内 attention 后端实现的耦合。
- **示意图资源**：`sources/images/ulysses.png` 与该 feature 直接绑定。

文档末尾的「内部链接: (无)」说明本 feature 文档未通过 markdown 内部链接交叉引用其他文档，但通过示例路径隐式关联了上述配置/脚本资产。

---

## 【使用方法】

### 1. 原生 FSDP2 后端（推荐）

在模型 YAML 配置文件的 `parallel` 段与 `model` 段分别设置：

```yaml
parallel:
  ulysses_parallel_size: 2   # 默认 1，大于 1 时启用 Ulysses CP

model:
  attn_implementation: flash_attention_2
```

要点：
- `ulysses_parallel_size`：默认 `1`；**大于 1** 时启用 Ulysses CP。
- 启用 Ulysses CP 时，`model.attn_implementation` **必须为** `flash_attention_2`。
- 参考：`examples/qwen3vl/qwen3vl_30B_config_v1.yaml`。

### 2. MCORE（Megatron）后端

以 Qwen2.5-VL-72B 为例，编辑 `examples/qwen2.5vl/finetune_qwen2_5_vl_72b.sh`：

**步骤 1** — 设置 CP 大小（默认 `1`）：

```shell
CP=1
```

**步骤 2** — 在 `GPT_ARGS` 中追加：

```shell
    --context-parallel-algo ulysses_cp_algo
```

### 3. 非均匀序列长度的零额外配置

无论 FSDP2 还是 MCORE 后端，当各卡序列长度不一致时，**无需任何额外配置**，Ulysses CP 即可正确完成非均匀切分。

## 图文联合解读

- `ulysses.png`: **图文联合解读**

1) 图示Ulysses注意力数据流，X[N,d]按序列切成N/P，经WQ/WK/WV得Q/K/V；两次AlltoAll（红箭头）将Q、K^T由[N/P, d]转为按头切分的[1, d/P]，完成Q_hK_h^T→softmax→×V_h→P_h后再AlltoAll还原为[N/P, d]，最后乘WO输出O；假设P=hc=4。

2) 论证Ulysses通过AlltoAll在"序列并行"与"头并行"间切换，使注意力在子空间计算可降低显存。

3) 图中两个AlltoAll正是文档所述"按序列长度非均匀切分Input/Output List"的改造点，为多模态变长序列场景提供机制基础。
