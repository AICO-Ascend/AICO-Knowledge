# Tensor Parallel

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/tensor_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/tensor_parallel.md

# Tensor Parallel (TP) 特性文档深度解读

---

## 【定位】

本文档描述了 MindIE LLM 推理引擎中 **Tensor Parallel（张量并行，TP）** 的能力及其在昇腾 Atlas 800I A2/A3 服务器上的部署方法，重点聚焦于 DeepSeek-V3 / DeepSeek-R1 / DeepSeek-V3.1 系列大模型上的 **LmHead 矩阵 local TP 切分** 与 **O project 矩阵 local TP 切分** 两类细粒度切分开关的配置方式与约束关系。

---

## 【技术要点】

1. **TP 定义与作用**：通过将权重矩阵、激活值等张量切分到多张 NPU 上进行分布式推理，属于**模型并行**策略。
2. **硬件与机型约束**：仅 **Atlas 800I A2 推理服务器** 和 **Atlas 800I A3 超节点服务器** 支持此特性。
3. **模型适用范围**：DeepSeek-V3、DeepSeek-R1、DeepSeek-V3.1 三种模型才支持 `lm_head_local_tp` 与 `o_proj_local_tp` 两类细粒度切分。
4. **切分粒度参数范围**：两个切分参数的取值范围均为 `[1, worldSize / 节点数]`，默认值为 `-1`（表示不开启切分）。
5. **互斥约束**：当 `tp > 1` 时，**不可**与 `o_proj_local_tp` 同时开启，**不建议**与 `lm_head_local_tp` 同时开启。
6. **PD 分离场景优化**：在 PD 分离且 D 节点为分布式时，开启 LmHead / O project 切分可**减少矩阵计算时间、降低推理时延**；D 节点为分布式低时延场景下，`tp > 1` 时支持 MLA 的 TP 切分，可减少小 batch decode 时延。

---

## 【关键机制与数据】

- **切分对象**：权重矩阵（如 LmHead、Attention O projection）和激活值。
- **工作原理**：通过把单个大张量沿特定维度切分到多张 NPU 上，使每张 NPU 仅承担部分计算，再通过集合通信汇聚结果，从而扩展可承载的模型规模并提升吞吐。
- **PD 分离下的收益机制**：在 PD 分离 + D 节点分布式的场景中，LmHead / O project 矩阵的 local TP 切分能**减少矩阵计算时间、降低推理时延**；在 D 节点低时延场景下，`tp > 1` 时支持 MLA 的 TP 切分，能在小 batch decode 低时延场景中减少 decode 时延。
- **性能数据**：原文未提供具体数字性能数据（如加速比、吞吐提升比例），仅描述机制层面的作用。

---

## 【表格解读】

### 表 1：Lmhead 矩阵 local TP 切分补充参数（ModelConfig.models）

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| **deepseekv2** | - | - | - |
| **parallel_options** | - | - | - |
| `lm_head_local_tp` | int | `[1, worldSize / 节点数]` | 表示 LmHead 张量并行切分数。<br><ul><li>仅 DeepSeek-R1、DeepSeek-V3 和 DeepSeek-V3.1 模型支持此特性。</li><li>默认值：`-1`，表示不开启切分。</li></ul> |

**逐行解读**：
- 第一、二行 `deepseekv2`、`parallel_options` 是 JSON 配置中的**层级路径**标识，对应 `models.deepseekv2.parallel_options` 这条嵌套层级，并非真正的可配置参数。
- 第三行 `lm_head_local_tp` 是 LmHead 矩阵切分的核心开关：
  - 取值类型为 int，取值范围为 `[1, worldSize / 节点数]`，即**每节点上的切分数上限**受总 worldSize 与节点数之比约束。
  - 默认值 `-1` 代表关闭切分；传入正整数即按该值做 local TP 切分。
  - 仅适用于 DeepSeek-R1、V3、V3.1 三种模型。

### 表 2：O project 矩阵 local TP 切分补充参数（ModelConfig.models）

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| **deepseekv2** | - | - | - |
| **parallel_options** | - | - | - |
| `o_proj_local_tp` | int | `[1, worldSize / 节点数]` | 表示 Attention O 矩阵切分数。<br><ul><li>仅 DeepSeek-R1、DeepSeek-V3 和 DeepSeek-V3.1 模型支持此特性。</li><li>默认值：`-1`，表示不开启切分。</li></ul> |

**逐行解读**：
- 前两行同样是配置层级路径标识，对应 `models.deepseekv2.parallel_options`。
- 第三行 `o_proj_local_tp` 控制 **Attention 输出投影（O projection）矩阵**的切分粒度：
  - 含义为 Attention O 矩阵切分数；取值范围同样是 `[1, worldSize / 节点数]`。
  - 默认值 `-1` 表示关闭；正整数即为开启切分。
  - 与 `lm_head_local_tp` 的模型适用范围保持一致（DeepSeek-R1/V3/V3.1）。

---

## 【公式解读】

原文无公式。

> 注：取值范围 `[1, worldSize / 节点数]` 表达的是一种**整数区间约束**，并非数学公式；其语义为：local TP 切分数的合法值为 1 到"总进程数 / 节点数"之间的整数。

---

## 【关联】

- **PD 分离（Prefill-Decode Disaggregation）**：文档在"限制与约束"中多次强调 TP 切分与 PD 分离场景的耦合关系，说明本特性是 PD 分离部署模式下降低 D 节点时延的关键开关之一。
- **MLA（Multi-Latent Attention）**：在 D 节点分布式低时延场景下，`tp > 1` 时支持 MLA 的 TP 切分，关联到 DeepSeek 系列模型使用的注意力机制。
- **ModelConfig 与服务化配置**：参数配置位置在 `ModelDeployConfig.ModelConfig[].models.deepseekv2.parallel_options` 嵌套结构中，与基础 TP（`tp` 字段）、`worldSize` 等参数共同控制并行拓扑。
- **Atlas 800I A2 / A3 硬件**：作为机型约束，决定了本特性可部署的物理环境。
- **服务化参数说明**：文档末尾指引至 `../user_manual/service_parameter_configuration.md`（即 `服务化参数说明`），用于了解 `config.json` 顶层服务化参数的语义。

---

## 【使用方法】

**启用方式**：

1. **修改配置文件**：编辑 Server 的 `config.json`。
   - whl 包路径：`{MindIE 安装目录}/mindie_llm/conf/config.json`
   - run 包路径：`{MindIE 安装目录}/latest/mindie-service/conf/config.json`

2. **配置项写入**（以 DeepSeek-R1 为例，开启 `tp=2`，关闭 Lmhead 与 O project 切分）：

    ```json
    "ModelDeployConfig" :
    {
       "maxSeqLen" : 2560,
       "maxInputTokenLen" : 2048,
       "truncation" : 0,
       "ModelConfig" : [
         {
             "modelInstanceType" : "Standard",
             "modelName" : "DeepSeek-R1_w8a8",
             "modelWeightPath" : "/data/weights/DeepSeek-R1_w8a8",
             "worldSize" : 8,
             "cpuMemSize" : 5,
             "npuMemSize" : -1,
             "backendType" : "atb",
             "trustRemoteCode" : false,
             "tp": 2,
             "models": {
                "deepseekv2": {
                    "parallel_options": {
                        "lm_head_local_tp": -1,
                        "o_proj_local_tp": -1
                    }
                }
             }
          }
       ]
    }
    ```

    **关键参数说明**：
    - `tp: 2`：开启基础张量并行度为 2。
    - `lm_head_local_tp: -1`：关闭 LmHead 矩阵切分。
    - `o_proj_local_tp: -1`：关闭 O project 矩阵切分。
    - 若要开启 LmHead / O project 切分，将 `-1` 替换为 `[1, worldSize / 节点数]` 范围内的正整数即可。

3. **启动服务**：
   - whl 包方式：`mindie_llm_server`
   - run 包方式：`./bin/mindieservice_daemon`

> 服务化参数（如 `ModelDeployConfig` 下顶层参数）的详细说明请参见内部链接 `../user_manual/service_parameter_configuration.md`。
