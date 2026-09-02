# FA3量化

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/fa3_quantization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/fa3_quantization.md

# FA3量化 文档深度解读

---

## 【定位】

本篇文档描述昇腾自研大模型推理引擎 MindIE-LLM 中 **Flash Attention 3（FA3）量化**特性：针对 DeepSeek MLA 架构下 K rope 张量数值范围剧烈波动、不适合量化的特点，将 K 的非 rope 张量量化为 8bit、K rope 张量保持原精度，配合 per-head 量化方案降低 KV Cache 显存占用，并加速 decode 阶段 attention 算子、提升吞吐。

---

## 【技术要点】

1. **量化对象差异（相对 Attention 量化）**：DeepSeek 使用 MLA 算法，k rope 取值变化过大不适合量化；本特性仅把 **k 的非 rope 张量量化为 8bit**，k 的 rope 张量不量化。
2. **量化方案**：**per-head 量化**（按 head 维度独立设置 scale/offset）。
3. **组合约束**：必须与 **W8A8 量化配合**使用；新增权重描述字段 `fa_quant_type: "FAKQuant"`、`self_attn` 子结构（含 `input_scale`/`input_offset`/`quant_bias`/`deq_scale`）。
4. **硬件/型号边界**：仅支持 **Atlas 800I A2 推理服务器**、**Atlas 800I A3 超节点服务器**；仅支持 **DeepSeek R1、DeepSeek V3、DeepSeek-R1-0528**；**仅支持 float16**。
5. **运行时强制项**：必须开启 **KV Cache NZ 格式**（PD 分离推理场景同样要求 `enable_nz=true`）。
6. **算子收益定位**：通过对 K 的部分量化 **减少 KV Cache 显存占用**，并 **优化 decode 阶段 attention 算子速度、提升吞吐**。

---

## 【关键机制与数据】

- **Q/K 量化-反量化闭环**：原文：`input_scale` 用于将 q、k 特征量化为 int8 类型；`deq_scale` 用于将 q、k 输出反量化成浮点类型。即前向过程为「浮点 → int8 量化 → 反量化回浮点 → attention 计算」。
- **相对 W8A8 的差异点**：原文：相比 W8A8 量化权重，新增 `fa_quant_type` 描述字段；新增 `self_attn` 字段及下面包含的内容。
- **量化粒度与张量形状（表 1）**：q 与 k 的 scale/offset 都按 head 维度展开，分别对应 `q_head_num` 与 `kv_head_num`（MLA 下两者通常不等），shape 中第二维为 `head_dim`，dtype 为 float16。
- **推理流程图（图 1）**：文档以 `figures/fa3_quantization.png` 给出"FA3 量化权重推理时流程"，描述从量化权重加载到 Q/K 量化、反量化、attention 计算再到 KV Cache 存取的整体路径（原文仅给出图，未附流程文字描述）。
- **量化输出产物**：原文：`quant_model_weight_w8a8.safetensors`（权重文件）+ `quant_model_description.json`（权重描述文件）；目录中其余 `config.json` / `tokenizer_*` 为推理配置/词表，**不同模型略有差异**。
- **性能数据**：原文未提供量化前后显存占用节省比例、吞吐加速比等量化数值。

---

## 【表格解读】

### 表 1　float16 权重量化后 dtype 及 shape 信息（假设原始权重的 shape 为 [n, k]）

| Tensor 信息 | dtype   | shape                          |
|-------------|---------|--------------------------------|
| q_scale     | float16 | [q_head_num, head_dim]         |
| q_offset    | float16 | [q_head_num, head_dim]         |
| k_scale     | float16 | [kv_head_num, head_dim]        |
| k_offset    | float16 | [kv_head_num, head_dim]        |

**逐行解读**：

- **q_scale**：Q 端的量化 scale，dtype 保持 float16；shape 为 `[q_head_num, head_dim]`，即**按每个 Q head 的每个 head_dim 元素**各持一份 scale，体现 per-head 量化粒度。
- **q_offset**：Q 端的量化 offset，与 q_scale 同 dtype、同 shape，配套使用以将浮点 Q 特征映射到 int8 区间。
- **k_scale**：K 端的量化 scale。注意 shape 为 `[kv_head_num, head_dim]` 而非 `[q_head_num, head_dim]`——这是 MLA 架构下 Q head 数与 KV head 数（GQA/MQA 语义下的"逻辑 head 数"）不一致的直接体现；原文亦在此以两个不同变量名 `q_head_num` / `kv_head_num` 区分。
- **k_offset**：K 端的量化 offset，与 k_scale 配套，shape 一致。

> **注**：表头给出"原始权重 shape 为 [n, k]"是泛化假设，本特性实际只展示 scale/offset 这些与量化粒度相关的元信息张量；`n, k` 与 `head_dim` 之间的代数映射关系**原文未给出**，需结合 MLA 模型定义推断。

---

## 【公式解读】

**原文无公式**（未出现 LaTeX 数学式或伪代码量化公式）。表 1 中的 shape 已在上节以表格形式呈现。

---

## 【关联】

文档虽未在文末列出内部链接，但从正文中可梳理如下上下游/相关模块关系：

- **与 W8A8 量化的关系**：FA3 量化**不是独立使用**，而是 W8A8 量化在 attention 维度的扩展——必须先有 W8A8 量化权重（`quant_model_weight_w8a8.safetensors`），FA3 量化在此基础上叠加 K 的非 rope 部分 int8 量化。
- **与 msModelSlim 工具的关系**：FA3 量化权重通过外部工具 msModelSlim 生成（而非 MindIE-LLM 内部产出），入口脚本为 `msmodelslim/example/DeepSeek/quant_deepseek_w8a8.py`，并通过 `--fa_quant --mindie_format` 两个 CLI 参数显式启用 FA3 与 MindIE 目录布局。
- **与 KV Cache NZ 格式的关系**：FA3 量化**强依赖** KV Cache NZ（`enable_nz=true`），属于 attention 计算路径对存储布局的硬性要求；纯模型推理与服务化推理两条链路都需显式打开。
- **与 DeepSeek MLA 算法的关系**：FA3 量化是为 MLA 量身定制的子方案——MLA 下 K 由 rope 分量与非 rope 分量组成，FA3 仅对后者量化；这也解释了为何本特性**只支持 DeepSeek R1 / V3 / R1-0528**。
- **与推理后端的关系**：服务化推理示例配置中指定 `backendType: "atb"`，并涉及 MTP 投机解码参数（`plugin_type: mtp`、`num_speculative_tokens: 1`），说明 FA3 量化在 atb 后端下、可与 MTP 联合部署。
- **与 PD 分离推理的关系**：原文明确"PD 分离推理时，需要在配置文件中将 `enable_nz` 设置为 `true`"，FA3 量化在 PD 分离场景同样适用。

---

## 【使用方法】

### 生成权重（量化侧）

1. 安装 msModelSlim 工具；
2. 按 msit 仓 `msmodelslim/example/DeepSeek/README.md` 完成 DeepSeek-V3/R1 运行前必检；
3. 在 `msmodelslim/example/DeepSeek/` 目录下执行：

```bash
python3 quant_deepseek_w8a8.py --model_path {浮点权重路径} --save_path {W8A8量化权重路径} --batch_size 4 --fa_quant --mindie_format
```

生成结果须在 `quant_model_description.json` 中包含 `"fa_quant_type": "FAKQuant"` 键值对。

### 执行推理（部署侧）

1. **开启 KV Cache NZ 格式**：
   - 纯模型推理：编辑 `${ATB_SPEED_HOME_PATH}/atb_llm/conf/config.json`，将 `enable_nz` 设为 `true`；
   - 服务化推理：在 `${MindIE安装目录}/mindie_llm/conf/config.json` 的 `ModelConfig` 字段下添加 `enable_nz`（示例片段在原文，含 `modelName: deepseekr1`、`tp: 8`、`dp: 2`、`moe_ep: 4`、`moe_tp: 4`、MTP 插件、`models.deepseekv2.kv_cache_options.enable_nz: true` 等）；
   - PD 分离推理同样需将 `enable_nz` 设为 `true`。

2. **对话测试**：

```bash
cd ${ATB_SPEED_HOME_PATH}
bash examples/models/deepseekv2/run_pa.sh {W8A8量化权重路径}
```

> 注：上述配置项、命令、参数均直接出自原文；具体配置文件中其余字段（如 `cpuMemSize`、`npuMemSize` 等）在原文示例中给出，但本特性未对其做单独解释，故仅作为示例保留，不做扩展解读。

## 图文联合解读

- `fa3_quantization.png`: **图示解读：**

1. **图中内容**：FA3注意力计算数据流图。顶部四个输入：Q(int8)、K\V(int8)、Q_ROPE(fp16)、K_ROPE(fp16)；两条并行矩阵乘路径——S1=Q^T·K（量化）、S2=Q_rope^T·K_rope（fp16）；中间绿色区：Dequant→Softmax(fp32)→分块量化得P(int8)；再与V(int8)相乘得Io，经Dequant后聚合为最终输出O(fp16)。

2. **技术结论**：K的非rope张量量化、K的rope张量保留fp16；Softmax结果P采用分块量化；实现per-head量化与混合精度计算。

3. **与文档关系**：图示印证"K的rope不量化、非rope量化为8bit"的per-head方案，解释减少KV Cache显存与加速decode的设计原理。
