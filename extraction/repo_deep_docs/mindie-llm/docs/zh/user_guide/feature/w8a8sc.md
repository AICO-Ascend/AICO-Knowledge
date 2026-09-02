# W8A8SC稀疏量化

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/w8a8sc.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/w8a8sc.md

# W8A8SC 稀疏量化文档深度解读

---

## 【定位】

这篇文档描述了 MindIE-LLM 推理引擎中 **W8A8SC（权重8bit + 激活8bit + 稀疏压缩）三阶段联合压缩能力**——即在模型权重上依次执行稀疏、量化、压缩，将大模型权重体积与显存占用进一步压低以提升推理性能，并给出生成压缩权重的全流程命令与产物说明。

---

## 【技术要点】

1. **三段式压缩流程**：稀疏 → 量化 → 压缩三步串联。稀疏算法判定每个权重元素对精度的重要性并置零不重要权重；量化将权重与激活从高位浮点转为 8bit；压缩在切分后的量化权重上进一步编码压缩，生成 `quant_model_weight_w8a8sc.safetensors` 与索引文件。

2. **硬件与模型范围限制**：压缩算法与硬件强绑定，**仅 Atlas 300I Duo 推理卡支持稀疏量化**；**bfloat16 权重不支持稀疏量化**；**仅支持 Qwen3-8B、Qwen3-14B 和 Qwen3-32B** 三款模型。

3. **特性互斥/共存关系**：W8A8SC **仅支持与并行解码、Prefix Cache、Function Call、长序列特性同时使用**（隐含不能与某些其他特性混用，文档未列出禁止项）。

4. **两级目录结构**：
   - 稀疏+量化阶段：单目录包含 `quant_model_weight_w8a8s.safetensors` + `quant_model_description.json`；
   - 压缩阶段：多 TP 切分目录 `part0-of-4 … part3-of-4`，每片均含一份 `quant_model_weight_w8a8sc.safetensors` 和 `quant_model_description.json`，顶层保留 tokenizer 相关文件。

5. **MatMul 量化算子的扩展张量**：量化后的 MatMul 权重新增 4 个辅助张量——`input_scale`、`input_offset`（对激活做量化）、`quant_bias`、`deq_scale`（对 MatMul 结果做反量化）；压缩后相比量化**再新增** `index` 与 `info` 两个 W8A8SC 类型张量用于权重复原。

6. **TP 切分压缩前置**：压缩算法必须在切分（多卡）后的权重上执行，因此 torchrun 的 `--nproc_per_node` **必须与运行时张量并行个数保持一致**。

---

## 【关键机制与数据】

**推理时数据流（图 1 描述，参考原文 w8a8sc.png）**：

1. 加载 `quant_model_weight_w8a8sc.safetensors`（压缩格式）；
2. 通过 `index` / `info` 字段解压缩并复原为稀疏量化权重（仍为 int8）；
3. 加载 `input_scale`、`input_offset`，对激活值做对称/非对称量化（int8）；
4. MatMul 使用 **量化后的 int8 激活值 × int8 量化权重** 计算；
5. 使用 `quant_bias` 与 `deq_scale` 对 MatMul 结果进行反量化，输出浮点结果进入下一层。

**关键字段类型映射（原文）**：
- 量化阶段 MatMul 张量类型：`weight=W8A8S`、`input_scale=W8A8S`、`input_offset=W8A8S`、`quant_bias=W8A8S`、`deq_scale=W8A8S`；embedding 层 `model.embed_tokens.weight` 保持 `FLOAT`。
- 压缩阶段 MatMul 张量类型：`c_attn.weight`、`c_attn.index`、`c_attn.info` 均为 `W8A8SC`；同时保留 `input_scale`、`input_offset`、`deq_scale`、`quant_bias` 四项 `W8A8S` 辅助张量；embedding 层 `transformer.wte.weight` 仍为 `FLOAT`。

**性能/收益定性描述（原文）**：
- 量化"直接将高位浮点数转为 8bit，可以直接降低权重体积，带来性能收益"；
- 压缩"通过压缩算法进一步编码压缩，最大程度地降低权重体积"。

具体加速比、压缩比、吞吐量等数字原文未给出。

---

## 【表格解读】

**原文表 1**：float16 权重量化后 dtype 及 shape 信息（假设原始权重的 shape 为 \[n, k\]）

| Tensor信息 | weight | input_scale | input_offset | quant_bias | deq_scale | index |
|---|---|---|---|---|---|---|
| dtype | int8 | float16 | int8 | int32 | int64 | int8 |
| shape | [x]<br>x 的取值范围为 (0, n * k)。 | [1] | [1] | [n] | [n] | [y]<br>y 由以下计算得出。<br>y = k_index * n_index * 8<br>k_index = ceil(k1 / tilingK)<br>n_index = ceil(n1 / tilingN)<br>k1 = k / 32<br>n1 = n / 16<br>其中，ceil() 为向上取整函数，tilingK 和 tilingN 为稀疏量化默认参数。 |

**逐行解读**：

- **dtype 行**：量化后主权重 `weight` 已经是 `int8`；激活侧的 `input_scale` 为 `float16`（用于反量化时的浮点缩放因子），`input_offset` 为 `int8`（量化零点，对应 int8 数值域）；结果侧的 `quant_bias` 为 `int32`（因 int8 × int8 + bias 累加可能溢出，必须升位），`deq_scale` 为 `int64`（反量化缩放精度更高）。压缩特有的 `index` 为 `int8`。
- **shape 行**：
  - `weight` 形状为 `[x]`，其中 `x` 仅约束范围 `(0, n * k)`——因为稀疏量化会置零部分元素，实际非零/被编码的元素数 `x` 小于等于原始 `n*k`，稀疏率越高 `x` 越接近下界。
  - `input_scale`、`input_offset` 形状为 `[1]`——每个张量对应一组全局量化参数。
  - `quant_bias`、`deq_scale` 形状为 `[n]`——与 MatMul 输出维对齐，每个输出行（行数 n）有独立的 bias 与缩放因子。
  - `index` 形状为 `[y]`，`y` 的计算在下文公式解读中详述。

---

## 【公式解读】

**原文给出的压缩 index 长度计算公式**（来自表 1 shape 列）：

```
y = k_index * n_index * 8
k_index = ceil(k1 / tilingK)
n_index = ceil(n1 / tilingN)
k1 = k / 32
n1 = n / 16
```

**符号含义与作用**（全部来自原文，"tilingK 和 tilingN 为稀疏量化默认参数"）：

| 符号 | 含义 | 作用 |
|---|---|---|
| `n`、`k` | 原始 float16 权重矩阵的行数与列数（shape = [n, k]） | 公式的输入维度 |
| `n1` | `n / 32`（原文直接使用 `/`，未说明是否向下取整，但结合 tiling 一般视为整数除） | 将 n 维按 32 元素为粒度切分 |
| `k1` | `k / 32`（同上） | 将 k 维按 32 元素为粒度切分 |
| `tilingK` | 稀疏量化默认参数（k 方向 tile 大小） | 控制 k 维再切的桶大小 |
| `tilingN` | 稀疏量化默认参数（n 方向 tile 大小） | 控制 n 维再切的桶大小 |
| `ceil()` | 向上取整函数（原文明确说明） | 保证 tile 数量足够覆盖全部元素 |
| `n_index` | `ceil(n1 / tilingN)`，n 方向所需 index 桶数 | 表示 n 维被切成多少段 |
| `k_index` | `ceil(k1 / tilingK)`，k 方向所需 index 桶数 | 表示 k 维被切成多少段 |
| `y` | `k_index * n_index * 8`，index 张量总元素数 | 每个 (tileN, tileK) 组合提供 8 个 int8 索引项，承载非零权重位置的复原信息 |

**作用机制**：压缩算法把 `[n, k]` 的权重按 `n` 维 32 元素一桶、`k` 维 32 元素一桶预先分包，再以 `tilingN × tilingK` 为二级 tile，记录每个 tile 内非零权重位置的索引，因此 `index` 总长是 tile 数量的 8 倍（原文未解释为何"×8"，文档未涉及）。

---

## 【关联】

**前置依赖模块**：

1. **msModelSlim 压缩工具**：稀疏量化和压缩权重的生成完全依赖此外部工具。文档明确指向《msModelSlim 工具》的"[msModelSlim安装](https://gitcode.com/Ascend/msit/blob/master/msmodelslim/docs/%E5%AE%89%E8%A3%85%E6%8C%87%E5%8D%97.md)"章节，需先安装、设置 `LD_LIBRARY_PATH`，才能调用 `msmodelslim quant` 与 `examples.convert.model_slim.sparse_compressor`。
2. **ATB Speed 推理运行时**：最终执行推理时进入 `${ATB_SPEED_HOME_PATH}/examples/models/qwen/run_pa.sh`，说明 W8A8SC 产物被 ATB Speed 后端加载；与文档中提到"稀疏+量化+压缩"步骤合在一起，与 **W8A8S（仅稀疏+量化）权重** 是上下游关系——W8A8SC = W8A8S + compression。

**可叠加的特性（原文）**：并行解码、Prefix Cache、Function Call、长序列。

**硬件关联**：Atlas 300I Duo 推理卡是唯一可用硬件，与 MindIE-LLM 整体昇腾 NPU 适配体系一致。

**模型范围关联**：仅 Qwen3-8B / 14B / 32B 三款，对应 ATB Speed 下 `examples/models/qwen` 路径，与文档中的推理启动脚本路径一致。

---

## 【使用方法】

**原文命令完整保留**：

1. **生成 W8A8S 量化权重**（稀疏+量化，未压缩）：
   ```bash
   msmodelslim quant --model_path ${浮点权重路径} --save_path ${W8A8S量化权重保存路径} --device npu --model_type Qwen3-8B --quant_type w8a8s --trust_remote_code True
   ```
   - 不同模型的最优参数不同，需参考模型 Readme；
   - 完成后需手动将浮点权重目录下的 `special_tokens_map.json` 复制到 W8A8S 量化权重路径。

2. **设置 msModelSlim 的 Python 环境变量**（`{Python Lib Path}` 替换为安装 msModelSlim 时编译步骤中所在的 Python 路径）：
   ```bash
   export LD_LIBRARY_PATH={Python Lib Path}/lib:$LD_LIBRARY_PATH
   ```

3. **对量化权重进行压缩，生成 W8A8SC**（多卡 TP 切分压缩，`{TP数}` 必须与运行时一致）：
   ```bash
   torchrun --nproc_per_node {TP数} -m examples.convert.model_slim.sparse_compressor --model_path {W8A8S量化权重路径} --save_directory {W8A8SC量化权重路径}
   ```

4. **加载 W8A8SC 权重执行推理**（以 Qwen3-8B 对话测试为例，提问 `"What's deep learning?"`）：
   ```bash
   cd ${ATB_SPEED_HOME_PATH}
   bash examples/models/qwen/run_pa.sh -m {W8A8SC量化权重路径} --trust_remote_code true
   ```

**配置/约束清单（原文）**：
- 硬件：仅 Atlas 300I Duo；
- 权重 dtype：仅 float16（bfloat16 不支持）；
- 模型：Qwen3-8B / 14B / 32B；
- 共存特性：并行解码、Prefix Cache、Function Call、长序列；
- TP 数：压缩阶段 `torchrun --nproc_per_node` 需与推理运行时张量并行个数一致。

## 图文联合解读

- `w8a8sc.png`: **图文解读：**

1) 图示展示了W8A8量化计算流程：float16/bfloat16激活值经量化转为int8，与int8权重共同进入MatMul，再经反量化和稀疏改造，最终输出float16/bffloat16结果。

2) 论证W8A8采用"离线量化激活+权重、在线MatMul+反量化"的推理计算路径，并体现稀疏改造需在反量化阶段完成。

3) 与文档对应：图示可视化呈现了`quant_model_description.json`中`input_scale/input_offset`（激活量化）与`quant_bias/deq_scale`（反量化）参数的实际作用环节，补充说明了W8A8SC的MatMul计算原理。
