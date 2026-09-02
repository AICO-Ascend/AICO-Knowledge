# KV Cache池化

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/kv_cache_pool.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/kv_cache_pool.md

# KV Cache 池化特性文档深度解读

## 【定位】

本篇文档描述 MindIE 在 KV Cache 与 Prefix Cache 基础上进一步扩展存储层级的"KV Cache 池化"能力——将容量更大的 DRAM（乃至未来扩展到 SSD）纳入前缀缓存池，用以突破片上内存容量上限、提升 Prefix Cache 命中率、降低大模型推理成本；同时给出配套的 HCCL 单边通信资源占用估算、参数配置与部署执行流程。

---

## 【技术要点】

1. **特性依赖与叠加**：当前版本"仅支持 DRAM 池化"，与 Prefix Cache 叠加形成"片上内存 + DRAM"两级缓存；启用 KV Cache 池化必须同时打开 Prefix Cache 特性。
2. **硬件适配范围**：支持 Atlas 800I A2 推理服务器与 Atlas 300I Duo 推理卡；其余约束同 Prefix Cache。
3. **底层通信机制**：采用基于 HCCL 单边通信的池化后端；每条 HCCL 链路占用 **4MB** 显存，单次建链数上限为 **512 条**（受 HCCL 底层能力限制）。
4. **显存占用公式**：HCCL 建链额外显存占用 = **（参与池化节点的总卡数/总die数 − 1）× 4MB**；举例 Atlas 800I A3 服务器 4机+4机场景为 **(8×16 − 1)×4MB = 508MB**。
5. **显存因子下调**：每下调 **0.01** 可释放约 **600MB** 显存；当前池化建链数上限所需下调幅度最大 **0.01**；为兼容扩容场景建议预留下调 **0.04**（即默认 0.92 → 0.08）；下调会同步降低支持的上下文长度。
6. **核心配置项**：在 `BackendConfig` 中新增 `kvPoolConfig`（`std::string`），含 `backend`（后端名称，置空即关闭）、`configPath`（后端配置文件路径）、`asyncWrite`（KV Cache 异步写开关，默认 false）。

---

## 【关键机制与数据】

**工作原理层级化展开**（综合原文"特性介绍"与"限制与约束"）：

- Prefix Cache 默认仅使用片上内存，单机容量有限，难以缓存大量前缀；
- KV Cache 池化将 DRAM 纳入前缀缓存池，使缓存可在片上内存与 DRAM 之间分层；
- 原文："该机制有效提升了 Prefix Cache 的命中率，显著降低大模型推理的成本"；
- 原文："片上内存命中率优先级高于 DRAM 池化，如果需要真实从池子命中，需要保证片上内存中无法命中"——即请求先查片上、再查 DRAM，体现层级化缓存语义。

**HCCL 通信资源占用**（原文具体数字）：

- 每条 HCCL 链路 = **4MB** 显存；
- 最大建链数 = **512**；
- 显存因子每下调 **0.01** ≈ 释放 **600MB**；
- 扩容预留：**0.04**（默认 0.92 → 0.08）；
- 实例：Atlas 800I A3、4机+4机 = 8 台，每台 16 卡 → 额外显存 (8×16−1)×4 = **508MB**，下调 0.01 即可满足（约 600MB > 508MB）。

**池规模建议**：原文指出建议 **总卡/die 数量 ≤ 512**，避免长时间运行中频繁断链/重建链导致性能下降。

**数据流/调用流程**（原文"执行推理"）：

1. 修改 `conf/config.json` 加入 `kvPoolConfig` 与 Prefix Cache 相关插件参数（`plugin_params: {"plugin_type":"prefix_cache"}`）；
2. 拉起池化后端的中心化 Master Service（部署细节见 mempool.md）；
3. 启动 `mindie_llm_server`（whl 包）或 `./bin/mindieservice_daemon`（run 包）；
4. 第一次请求构建前缀；后续请求需与首请求有公共前缀（多轮对话、few-shot 等场景）以触发池命中，且需保证片上内存无法命中才能验证 DRAM 池路径。

---

## 【表格解读】

**原文表 1（KV Cache 池化特性补充参数：BackendConfig 中的参数）逐字还原：**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| kvPoolConfig | std::string | `{"backend":"*kv_pool_backend_name*",`<br>`"configPath":"*/path/to/your/config/file*"，`<br>`"asyncWrite":false}` | <li>`backend` 为指定的 KV Cache 池化后端。<ul><li>设置为 `""`，表示关闭 KV Cache 池化。</li><li>设置为对应池化后端的名称，表示开启 KV Cache 池化。</li></ul></li><li>`configPath` 为传入池化后端所需的配置文件路径。</li><li>`asyncWrite` 为池化 KV Cache 异步写开关。<ul><li>不设置或设置为 `false`，表示关闭 KV Cache 的异步写。</li><li>设置为 `true`，表示开启 KV Cache 的异步写。</li></ul></li> |

**逐行解读**：

- **配置项 `kvPoolConfig`**：本特性唯一的顶层开关字段，挂在 `BackendConfig` 下；类型为字符串但内容是 JSON 字典，体现"键值即配置"的灵活结构。
- **取值类型 `std::string`**：表示这是一个字符串型配置项；服务端按 JSON 解析内部字段。
- **`backend`**：核心开关字段，控制是否启用池化后端；空串=关闭，非空=启用且使用指定后端（具体可用名称由池化后端实现定义，原文以 `kv_pool_backend_name` 占位符表示）。
- **`configPath`**：池化后端自身的配置文件路径（与 Server 的 `config.json` 是两层配置——后者管 MindIE，前者管后端），需要由用户根据所选后端准备。
- **`asyncWrite`**：异步写开关；默认关闭，开启后 KV Cache 以异步方式写入池，可降低写延迟对推理路径的阻塞（具体收益依后端实现而定，原文未给数字）。
- **配置语义**：三个字段职责分离——开关由 `backend` 决定，行为细节由 `configPath` 指向的文件承载，写策略由 `asyncWrite` 控制；用户启用前必须满足前置条件（开启 Prefix Cache + Master Service 拉起）。

---

## 【公式解读】

**公式 1（原文照录）**：

$$
\text{额外显存占用} = \left(\frac{\text{参与池化节点的总卡数}}{\text{总 die 数}} - 1\right) \times 4\,\text{MB}
$$

**符号与含义**：

- **参与池化节点的总卡数**：纳入 KV Cache 池化拓扑的所有加速卡（含多机多卡场景下的所有节点卡）的总数量；
- **总 die 数**：底层 HCCL 建链所识别的"目标节点/对端数"，原文用"die"作为计数单位（不同硬件拓扑中一台加速器可能含多个 die）；
- **−1**：扣除自身链路后所需的"对端"链路数；体现"单边通信"建链数 = N−1（N 个对端 + 自身 → N−1 条对外链路）；
- **× 4MB**：每条 HCCL 链路消耗的固定显存；
- **作用**：估算启用池化所需的额外片上显存，据此决定 `显存因子` 的下调幅度。

**算例（原文）**：

$$
(8 \times 16 - 1) \times 4\,\text{MB} = 508\,\text{MB}
$$

注：原文算例显示为 `8×16`，与公式中"/总 die 数"的字面写法在数值上不完全自洽；以原文算例为准时，括号内实际取值为 `8×16 − 1 = 127`，对应 127 条对端链路。**解读时应以算例数值（508MB）作为容量规划基准**，再据"每下调 0.01 释放 600MB"规则反推下调幅度。

**公式 2（隐含，由"下调显存因子 → 释放显存 → 上下文长度"构成）**：

- 显存因子下调 0.01 → 释放约 600MB → 上下文长度同步降低；
- 扩容场景预留下调 0.04 → 默认 0.92 → 设为 0.08；
- 该关系在原文中以叙述形式给出，未以数学式表达。

---

## 【关联】

- **`prefix_cache.md`**（多个锚点）：本特性是 Prefix Cache 的存储层级扩展——启用前提、参数表与请求复用语义均依赖 Prefix Cache。
  - `prefix_cache.md#限制与约束`：硬件/机型/上下文等通用约束直接继承；
  - `prefix_cache.md#table1` ~ `prefix_cache.md#table3`：Prefix Cache 本身的参数配置（与本文表 1 共同构成完整 `config.json` 设置）；
  - `prefix_cache.md` 发送请求章节：第二步及第五步请求命令直接复用。
- **`../user_manual/service_parameter_configuration.md`**：除 Prefix Cache 与 `kvPoolConfig` 之外，其他服务化参数（`maxSeqLen`、`maxInputTokenLen`、`worldSize`、`tp/sp/dp`、`moe_ep/moe_tp`、`async_scheduler_wait_time`、`kv_trans_timeout`、`kv_link_timeout` 等）参见该手册；示例 config.json 中已给出 DeepSeek-R1 + W8A8 MTP 的代表性取值。
- **`mempool.md`**：第三步拉起的"池化后端对应的中心化服务 Master Service"的安装与启动命令详见该文档；本文仅给出引用，不展开。
- **推理后端 / 模型插件链路**：`backendName: "mindieservice_llm_engine"` + `plugin_params: "{\"plugin_type\":\"prefix_cache\"}"` 表明 Prefix Cache 插件 + 池化后端在 ATB 后端（`backendType: "atb"`）上协同工作；DeepSeek-R1 配置中出现的 `enable_mlapo_prefetch`、`enable_nz` 等参数属模型部署级 KV Cache 优化，与池化特性解耦但同时存在。

---

## 【使用方法】

**启用条件**（原文明确）：
- 硬件：Atlas 800I A2 推理服务器 或 Atlas 300I Duo 推理卡；
- 必须同时开启 Prefix Cache（`plugin_params: {"plugin_type":"prefix_cache"}`）；
- 当前仅 DRAM 池化；
- 需提前拉起 Master Service。

**配置项**（原文表 1）：
- `BackendConfig.kvPoolConfig.backend` → 设为对应池化后端名称（非空启用 / 空字符串关闭）；
- `BackendConfig.kvPoolConfig.configPath` → 池化后端配置文件路径；
- `BackendConfig.kvPoolConfig.asyncWrite` → `true` 开启异步写，`false` 或缺省关闭；
- 容量规划：按公式 `(总卡/die − 1)×4MB` 估算 HCCL 额外显存，按"0.01 → 600MB"规则下调显存因子，扩容场景预留下调 0.04。

**部署命令**（原文"执行推理"）：
- whl 包：编辑 `{MindIE安装目录}/mindie_llm/conf/config.json`，启动 `mindie_llm_server`；
- run 包：编辑 `{MindIE安装目录}/latest/mindie-service/conf/config.json`，启动 `./bin/mindieservice_daemon`；
- 中间步骤：通过 `mempool.md` 安装并拉起 Master Service；
- 验证：先发第一轮请求（写入前缀），后续请求需含公共前缀（多轮对话 / few-shot），并刻意使片上内存不命中以验证 DRAM 池命中路径。

**示例片段**（原文 DeepSeek-R1 配置，已在文档中完整给出）：`maxSeqLen=20000`、`maxInputTokenLen=4096`、`worldSize=8`、`tp=8`、`dp=2`、`sp=1`、`moe_ep=4`、`moe_tp=4`、`async_scheduler_wait_time=120`、`kv_trans_timeout=10`、`kv_link_timeout=1080`；权重路径形如 `/*权重路径*/deepseek_r1_w8a8_mtp`；`kvPoolConfig` 仅设置 `backend` 与 `configPath`，未设置 `asyncWrite`（按原文语义为默认关闭）。
