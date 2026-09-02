# 虚拟流水线并行

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/virtual_pipeline_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/virtual_pipeline_parallel.md

# 虚拟流水线并行 (Virtual Pipeline Parallel, VPP) 一体化解读

---

## 【定位】

本文档描述了在 Pipelined Pipeline Parallel (Pipedream) 切分粒度过粗、空泡 (bubble) 较大时，如何通过虚拟流水线并行（VPP）将流水线进一步细分到 PP×VPP 个阶段，从而以更多通信开销换取空泡率降低；并以 Qwen2VL-7B 为例展示了 MindSpeed MM 所支持的**非均匀** VPP 切分方案的配置方法。

---

## 【技术要点】

1. **核心动机**：Pipedream 风格流水线切分粒度过大，运行中仍存在大量空泡，硬件算力利用率受限。
2. **基本思路**：在设备数不变的前提下，将单个流水线阶段进一步切细，分出更多流水线阶段，**以更多通信量换空泡率下降**。
3. **阶段数量公式**：模型被切分为 `PP × VPP` 个阶段（原文："模型会被分为 4 * 3 = 12 个阶段"），其中 PP 为流水线并行大小，VPP 为虚拟流水线大小。
4. **关键参数**：以 Qwen2VL-7B 为例，TP=1，PP=4，VPP=3；同时支持**非均匀切分**，每阶段的层数可自定义。
5. **双模块独立切分**：视觉模块 (vit) 与语言模块 (llm) 分别配置 `vit_pp_layers` 与 `llm_pp_layers` 两个二维列表，行表示 VPP 索引，列表示 PP 索引。
6. **非均匀切分扩展**：原文明确指出"Megatron 原生只支持 vpp 均匀切分"，MindSpeed MM 对其做了扩展，允许通过 `pipeline_num_layers`、`VP_SIZE` 环境变量与权重转换工具联合配置任意切分。

---

## 【关键机制与数据】

**阶段模型（原文："模型会被分为 4 * 3 = 12 个阶段"）**

- 每个 (device, vpp) 二元组对应一段连续层。
- 在 Qwen2VL-7B 例子里，视觉模块共 32 层，语言模块共 28 层，被切到 4 (device) × 3 (vpp) = 12 个槽位，每个槽位存储 vit 层数 + llm 层数。

**前向数据流（原文："前向的顺序为 D0V0 -> D1V0 -> D2V0 -> D3V0 -> D0V1 -> D1V1 -> D2V1 -> D3V1 -> D0V2 -> D1V2 -> D2V2 -> D3V2"）**

- 先沿着 device 维度（PP 流水）跑完 V0，再依次跑 V1、V2。
- 即：同一 VPP 切片先经过所有设备，再切换到下一个 VPP 切片，这是 VPP 经典交错顺序，用以减少空泡。

**性能结论（原文："空泡比率进一步减小"）**

- 文档仅给出定性结论，未列出具体加速比或空泡率数值。

---

## 【表格解读】

原文"每 device×每 vpp 的模型层数分布"以代码块列出。下面按原文逐行转写并标注 vpp × pp 二维索引：

| Device | V0 (vpp=0) | V1 (vpp=1) | V2 (vpp=2) | 合计 vit | 合计 llm |
|--------|-----------|-----------|-----------|----------|----------|
| D0 | 10 vit + 0 llm | 0 vit + 4 llm | 0 vit + 4 llm | 10 | 8 |
| D1 | 10 vit + 0 llm | 0 vit + 4 llm | 0 vit + 3 llm | 10 | 7 |
| D2 | 10 vit + 0 llm | 0 vit + 4 llm | 0 vit + 2 llm | 10 | 6 |
| D3 | 2 vit + 1 llm | 0 vit + 4 llm | 0 vit + 2 llm | 2 | 7 |
| **合计** | — | — | — | **32** | **28** |

**逐行解读：**

- **D0V0**：承担视觉主干起始 10 个 vit 层，对应 vit 配置矩阵第 0 行 `[10,10,10,2]` 第 0 列；该阶段同时承担 0 个 llm 层，对应 llm 矩阵第 0 行第 0 列 `0`。
- **D1V0 / D2V0**：与 D0V0 类似，分别承担视觉主干后续各 10 层；至此 3 个 D 已消化 30 个 vit 层。
- **D3V0**：承接剩余 2 层 vit（视觉主干尾部），同时因 llm 矩阵第 0 行第 3 列为 `1`，故 D3V0 还承担 1 层 llm——这是非均匀切分的体现，把 1 层语言层挤进含尾段 vision 的同一阶段以减少跨阶段碎层。
- **D0V1 / D1V1 / D2V1 / D3V1**：由 llm 矩阵第 1 行 `[4,4,4,4]` 可知，4 个设备均承担 4 层 llm（共 16 层），vit 在此行全为 0；该 VPP 槽位承担语言模块的主体段。
- **D0V2**：4 层 llm；**D1V2**：3 层 llm；**D2V2**：2 层 llm；**D3V2**：2 层 llm——对应 llm 矩阵第 2 行 `[4,3,2,2]`，总和 11，连同 V0 那 1 层正好凑齐 28 层语言模块。
- **vit 列求和** = 10+10+10+2 = 32，与 Qwen2VL-7B 的"视觉模块层数是 32"一致；**llm 列求和** = 0+4+4+0+4+3+0+4+2+1+4+2 = 28，与"语言模块层数是 28"一致。

原文同时给出了两个**切分矩阵**：

| 矩阵 | 取值（原文逐字） | 行索引含义 | 列索引含义 | 行内求和 |
|------|----------------|-----------|-----------|----------|
| `vit_pp_layers` | `[[10, 10, 10, 2],[0, 0, 0, 0],[0, 0, 0, 0]]` | vpp 索引（0/1/2） | pp 索引（D0/D1/D2/D3） | 每行和分别 = 32 / 0 / 0 |
| `llm_pp_layers` | `[[0, 0, 0, 1],[4, 4, 4, 4],[4, 3, 2, 2]]` | vpp 索引（0/1/2） | pp 索引（D0/D1/D2/D3） | 每行和分别 = 1 / 16 / 11 |

---

## 【公式解读】

原文无显式数学公式。但有两条隐含的**量化关系**，按原文逐字保留并解释符号含义：

**(a) 阶段总数关系**（原文："模型会被分为 4 * 3 = 12 个阶段"）

```
stage_count = PP_size × VPP_size
```

- `PP_size` = 流水线并行大小（同一示例取值为 4，对应 D0/D1/D2/D3 四个 device）。
- `VPP_size` = 虚拟流水线大小（同一示例取值为 3，对应 V0/V1/V2 三个 micro-stage）。
- 作用：决定每条 sample 在网络中被细分为多少个连续 micro-stage，是 VPP 切分粗细的直接旋钮。

**(b) 模块层守恒**（原文："视觉模块层数是 32，语言模块层数是 28" + 切分矩阵）

```
Σ_{d ∈ [0,PP)} layer_module_v0[d] + layer_module_v1[d] + layer_module_v2[d] = total_module_layers
```

- module ∈ {vit, llm}；v_k 表示第 k 个 VPP 行；d 为 PP 索引。
- 原文 vit 矩阵各列求和 = 32，llm 矩阵各列求和 = 28，即两模块独立守恒。
- 作用：保证非均匀切分后模型总层数不被破坏；同时为权重转换工具提供校验基准。

---

## 【关联】

- **底层技术**：原文给出的链接 `https://people.eecs.berkeley.edu/~matei/papers/2021/sc_megatron_lm.pdf` 指向上游 Megatron-LM 论文（SC21），该论文首次系统化提出虚拟流水线并行（interleaved 1F1B）。
- **上游策略**：文档称"PipelineDream 流水线并行切分粒度过大"，表明本文是上一级流水线并行方案的**细化扩展**——同一仓库中应存在基础流水线并行（PP）相关 feature 文档。
- **并行维度组合**：示例显式说明 `tp_size = 1`、`PP = 4`、`VPP = 3`，VPP 与 TP、PP 正交叠加，与分布式训练中的张量并行（TP）、流水线并行（PP）共存。
- **权重一致性约束**：原文注意事项 2 指出 "Megatron 虚拟流水并行 vpp 影响权重切分方式，保存、加载权重时需保证 vpp 配置一致"——说明 VPP 与权重转换/加载流程强耦合，关联到 `mm-convert` 权重转换工具链路。
- **MindSpeed MM 的差异化价值**："Megatron 原生只支持 vpp 均匀切分，为了支持 vpp 非均匀切分"——本文所描述的能力是 MindSpeed MM 相对上游 Megatron 的增强点。

由于文末"内部链接"为空（原文标记"无"），上述关联均依据正文叙述推导，未额外推断其他仓库特性。

---

## 【使用方法】

> 原文以 Qwen2VL-7B 为例，分三步启用 VPP。

**步骤 1 — 配置切分规则并运行权重转换（原文命令逐字保留）**

```shell
mm-convert  Qwen2VLConverter hf_to_mm \
  --cfg.mm_dir "ckpt/mm_path/Qwen2-VL-7B-Instruct-vpp" \
  --cfg.hf_config.hf_dir "ckpt/hf_path/Qwen2-VL-7B-Instruct" \
  --cfg.parallel_config.llm_pp_layers [[0,0,0,1],[4,4,4,4],[4,3,2,2]] \
  --cfg.parallel_config.vit_pp_layers [[10,10,10,2],[0,0,0,0],[0,0,0,0]] \
  --cfg.parallel_config.tp_size 1
```

**步骤 2 — 在 `model.json` 中同步 `pipeline_num_layers`（必须与权重转换时一致）**

```json
// text_decoder
"pipeline_num_layers": [[0, 0, 0, 1],[4, 4, 4, 4],[4, 3, 2, 2]]

// vision_encoder
"pipeline_num_layers": [[10, 10, 10, 2],[0, 0, 0, 0],[0, 0, 0, 0]]
```

**步骤 3 — shell 中开启 VPP（原文命令逐字保留）**

```shell
export VP_SIZE=3
GPT_ARGS="
    --virtual-pipeline-model-parallel-size 3
    ..."
```

**关键配置项摘要**：

| 配置/变量 | 作用 | 取值要求 |
|----------|------|---------|
| `llm_pp_layers` | 语言模块按 (vpp, pp) 的层数切分矩阵 | 自定义，需保证列总和 = 28 |
| `vit_pp_layers` | 视觉模块按 (vpp, pp) 的层数切分矩阵 | 自定义，需保证列总和 = 32 |
| `tp_size` | 张量并行大小 | 示例 = 1 |
| `model.json:pipeline_num_layers` | 模型配置中的层切分 | 须与权重转换完全一致 |
| `VP_SIZE` 环境变量 | VPP 大小（MindSpeed 扩展点） | 等于 `pipeline_num_layers` 矩阵的行数 |
| `--virtual-pipeline-model-parallel-size` | Megatron 原生 VPP 开关 | 必须与 `VP_SIZE` 相同 |
| `pp_size` (隐含) | 流水线并行大小 | 示例中 = 4 |

**启用场景判定（原文"使用场景"）**：当需要"进一步减小空泡比率，提升性能"时启用；MindSpeed MM 提供非均匀切分以适配视觉编码器 + 语言解码器这种**双模块、层数不对齐**的多模态模型。

## 图文联合解读

- `virtual_pipeline.png`: **图文联合解读：**

1）**图示内容**：四设备（Device 1-4）的二维时间轴调度图，蓝色块代表前向传播（Forward Pass），绿色块代表反向传播（Backward Pass），灰色块为空泡（bubble），数字 1–16 为微批次编号，中部竖线分隔暖机阶段（前向为主）与排空阶段（反向为主）。

2）**技术结论**：通过将每个流水线阶段细分为多个虚拟阶段并交错执行微批次前向/反向，灰色空泡区域被显著压缩，前向与反向块在设备间紧密交错排列，验证了"以更多通信换更低空泡率"的优化效果。

3）**与文档关系**：直观佐证文档论点——相比 Pipedream 粗粒度切分仍有大量空泡，VPP 细分计算后空泡比例明显下降，提升计算资源利用率。
