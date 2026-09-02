# Architecture Overview

> 仓 `vllm` · 路径 `docs/design/arch_overview.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/arch_overview.md

# vLLM 架构总览文档深度解读

## 【定位】
本文档系统性地描绘了 vLLM 系统的整体架构,涵盖两大入口（离线 `LLM` 类与在线 `vllm serve` 服务）、V1 多进程分层（API Server / Engine Core / GPU Worker / DP Coordinator）、核心引擎 (`LLMEngine` / `AsyncLLMEngine`)、Worker–Model Runner–Model 三层关系以及类层级设计原则,目的是帮助使用者从宏观结构层面正确理解 vLLM 的运行模型,并据此进行部署资源的合理规划。

---

## 【技术要点】

1. **双入口接口**: 离线场景使用 `vllm.LLM` 类 (Python 直接调用),在线场景使用 `vllm serve <model>` 命令启动 OpenAI 兼容 HTTP 服务;两者最终都汇聚到同一套底层引擎。

2. **V1 多进程分层架构**: 四个核心进程类型——API Server、Engine Core、GPU Worker、DP Coordinator——分别承担 HTTP I/O、调度 + KV cache 管理、模型前向计算、跨 DP rank 负载均衡的职责。

3. **进程数与并行度的精确对应关系**:
   - API Server 数 = `A`,默认 = `DP`;可通过 `--api-server-count` 手动配置。
   - Engine Core 数 = `DP`,默认 1。
   - GPU Worker 数 = `N = DP × PP × TP`,每 GPU 一个进程。
   - DP Coordinator 仅当 `DP > 1` 时存在,数量为 1。

4. **进程间通信**: API Server 与 Engine Core 通过 **ZMQ socket** 建立**多对多 (many-to-many)** 拓扑,任意 API server 可将请求路由到任意 engine core。

5. **媒体加载线程数可调**: 通过环境变量 `VLLM_MEDIA_LOADING_THREAD_COUNT` 控制,默认值为 **8**;每个 API server 进程会使用该数量的 CPU 线程做多模态数据加载。

6. **Worker 标识**: 每个 worker 由 `rank` (全局编排) 与 `local_rank` (设备绑定、本地资源访问) 两个标识符区分;遵循"一进程一加速器"的常规做法。

7. **AsyncLLMEngine 异步封装**: 基于 `asyncio` 创建后台循环处理并发请求并向客户端流式输出,OpenAI 兼容 API server 与之绑定。

---

## 【关键机制与数据】

- **离线 LLM 调用流程** (原文): 用户定义 `SamplingParams(temperature=0.8, top_p=0.95)`,实例化 `LLM(model="facebook/opt-125m")`,调用 `llm.generate(prompts, sampling_params)`,最终通过 `output.outputs[0].text` 取出生成文本。

- **Engine Core 工作机制** (原文): 运行一个 busy loop,持续调度请求并将工作分派给其下属的 GPU worker;同时管理 KV cache 并协调跨 worker 的模型执行。

- **API Server ↔ Engine Core 拓扑** (原文): 默认 1 个 API server,但启用数据并行时 API server 数量自动随 DP size 扩展;每个 API server 通过 ZMQ 连接**全部** engine core,构成 many-to-many 路由拓扑。

- **典型部署进程数实例** (原文):
  - 4 GPU 单节点 (`vllm serve -tp=4`): **1 API server + 1 engine core + 4 GPU workers = 6 个进程**。
  - 8 GPU 数据并行 (`vllm serve -tp=2 -dp=4`): **4 API servers + 4 engine cores + 8 GPU workers + 1 DP coordinator = 17 个进程**。

- **DP Coordinator 触发条件** (原文): 仅当使用数据并行 (`--data-parallel-size > 1`) 时存在,负责跨 DP rank 的负载均衡并协调 MoE 模型的同步前向计算。

- **类层级设计原则** (原文,截断处): 层级中所有类都接受一个包含全部必要信息的配置对象,即 `VllmConfig` 类,作为可扩展性的基础 (extensibility)。

---

## 【表格解读】

原文包含一个 "Process Count Summary" 表格,逐字还原如下:

| Process Type | Count | Notes |
| - | - | - |
| API Server | `A` (default `DP`) | Handles HTTP requests and input processing |
| Engine Core | `DP` (default 1) | Scheduler and KV cache management |
| GPU Worker | `N` (= `DP x PP x TP`) | One per GPU, executes model forward passes |
| DP Coordinator | 1 if `DP > 1`, else 0 | Load balancing across DP ranks |
| **Total** | **`A + DP + N` (+ 1 if DP > 1)** | |

**逐行解读**:

- **API Server 行**: 数量记作 `A`,默认与数据并行度 `DP` 相等 (即 DP 增大时自动横向扩展);职责是处理 HTTP 请求和输入预处理 (tokenization、多模态数据加载)。

- **Engine Core 行**: 数量为 `DP`,默认 1 (即单 DP 时只有一个核心调度器);承担调度器逻辑与 KV cache 管理,是 GPU worker 与外部请求的中枢。

- **GPU Worker 行**: 数量记作 `N`,等于 `DP × PP × TP`(数据并行 × 流水线并行 × 张量并行的全组合);每张 GPU 一个进程,执行模型前向传播。

- **DP Coordinator 行**: 数量为条件值——`DP > 1` 时为 1,否则为 0;负责跨 DP rank 负载均衡,以及 MoE 模型所需的同步前向。

- **Total 行**: 总进程数公式 `A + DP + N`,当启用 DP 时再额外加 1 个 coordinator。该行加粗,作为部署容量规划的速算公式。

---

## 【公式解读】

原文未使用 LaTeX 或伪代码块书写正式公式,但表格中存在进程计数的代数关系,逐字保留并解释:

**式 1**: `N = DP x PP x TP`

- `N`: GPU Worker 进程总数 (原文记号)。
- `DP`: 数据并行度 (data parallel size)。
- `PP`: 流水线并行度 (pipeline parallel size)。
- `TP`: 张量并行度 (tensor parallel size)。
- 作用: 用于计算任意部署配置下所需的 GPU worker 数量,即每张 GPU 都对应一个独立 worker 进程。

**式 2**: `Total = A + DP + N (+ 1 if DP > 1)`

- `A`: API Server 进程数 (默认等于 `DP`)。
- `DP`: Engine Core 进程数,同时也代表 DP rank 数量。
- `N`: GPU Worker 进程数,由式 1 计算。
- 末尾 `(+ 1 if DP > 1)`: 启用数据并行时多出的 1 个 DP Coordinator 进程。
- 作用: 部署前快速估算系统总进程数,用于 CPU/内存资源规划。

---

## 【关联】

本文档作为架构总览,串联起以下上下游模块/文档:

- **Offline Inference API 文档** (`../api/README.md#offline-inference`): `LLM` 类的详细 API 说明,本文档对离线场景只给出最小示例,具体参数与返回值需查阅该文档。

- **`vllm/entrypoints/llm.py`**: `LLM` 类的实现源码入口,与本文档"LLM Class"小节直接对应。

- **`vllm/entrypoints/cli/main.py`**: `vllm` CLI 命令的注册与分发实现,本文档"Online Serving"小节中 `vllm serve` 命令的代码定位。

- **Online Serving 文档** (`../serving/online_serving/README.md`): API server 的部署、API 协议、客户端示例等细节,本文档仅作总览,具体配置需跳转此文档。

- **`vllm/entrypoints/launchers/api_server`**: API Server 进程的启动器实现,负责多 API server 场景下的进程拉起,与 `VLLM_MEDIA_LOADING_THREAD_COUNT` 等运行时配置相关。

- **`vllm/v1/utils.py`**: V1 架构通用工具函数,与 API Server 进程的内部行为配合。

- **`vllm/v1/engine/core.py`** 与 **`vllm/v1/engine/utils.py`**: Engine Core 进程的核心实现——调度循环、KV cache 管理、与 GPU worker 的通信等。

- **`vllm/v1/executor/multiproc_executor.py`**: 多进程执行器,负责在 Engine Core 下属创建并管理多个 GPU worker 进程,本文档"GPU Worker Processes"小节的代码定位。

- **`vllm/v1/worker/gpu_worker.py`**: 单 GPU worker 的具体实现,负责加载权重、执行前向、管理显存。

- **`vllm/v1/engine/coordinator.py`** (文中提及但未列入内部链接列表): DP Coordinator 进程实现,仅当 `--data-parallel-size > 1` 时启用。

- **辅助模块**: `vllm/engine/llm_engine.py` (`LLMEngine` 实现)、`vllm/engine/async_llm_engine.py` (`AsyncLLMEngine` 实现)、`examples/applications/api_server/server.py` (简化版 demo server)、`docs/design/huggingface_integration.md` (HuggingFace 模型集成说明,与"Model"小节关联)。

- **横向配置文档**: `../configuration/optimization.md#cpu-resources-for-gpu-deployments` 提供 V1 多进程架构下的 CPU 资源规划建议,本文档进程计数表是其前置依据。

---

## 【使用方法】

**离线推理调用** (原文):

```python
from vllm import LLM, SamplingParams

llm = LLM(model="facebook/opt-125m")
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
outputs = llm.generate(prompts, sampling_params)
```

**在线服务启动** (原文):

```bash
vllm serve <model>
```

**关键配置项 / 命令行参数** (原文):

- `--api-server-count`: 手动指定 API Server 进程数,默认随 DP 自动扩展。
- `--data-parallel-size` (示例 `-dp=4`): 数据并行度,决定 Engine Core 数量,大于 1 时额外拉起 DP Coordinator。
- `-tp` / 张量并行度 (示例 `-tp=4`): 每 DP rank 内的张量并行度,乘以 GPU 数决定每引擎下的 worker 数。
- 隐含的 `-pp` / 流水线并行度: 与 TP 共同决定 `N = DP × PP × TP`。

**环境变量** (原文):

- `VLLM_MEDIA_LOADING_THREAD_COUNT`: 每个 API server 进程用于多模态加载的 CPU 线程数,默认 **8**。

**典型启动组合** (原文示例):

- `vllm serve -tp=4` —— 单节点 4 GPU 部署,产生 6 个进程。
- `vllm serve -tp=2 -dp=4` —— 8 GPU 数据并行部署,产生 17 个进程。

## 图文联合解读

- `entrypoints.excalidraw.png`: **图意解读**

图以虚线分两层：上层为用户接口层（LLM类、OpenAI-compatible API Server），下层为引擎层（LLMEngine类、AsyncLLMEngine类）。箭头表明LLM类直接调用LLMEngine；API Server经AsyncLLMEngine间接调用LLMEngine。

**技术结论**

vLLM以同一底层LLMEngine统一支撑离线（Python）与在线（HTTP）两类入口，AsyncLLMEngine是同步引擎的异步包装，体现"一核双用"的分层设计。

**与文档关系**

直观印证"vLLM提供多个入口与系统交互"的核心论点，为后续LLM类与Online Service详解提供架构总览。
- `v1_process_architecture_tp4.png`: **图解**：
图示V1架构（4 GPU, TP=4）数据流：HTTP请求→API Server（输入处理/分词/流式输出）→经ZMQ双向通信→Engine Core（调度器、KV缓存管理）→分发至4个GPU Worker（模型执行、前向传播）。总计6个进程。

**论证结论**：V1采用多进程分层解耦设计，将接口层、调度层、计算层分离；通过ZMQ跨进程通信，并支持张量并行（TP=4）将单模型拆分到多GPU。

**与文档关系**：对应Online Serving入口点章节，揭示vLLM在线服务的端到端请求路径与进程拓扑，佐证其"多入口统一引擎核心、并行扩展GPU"的架构论点。
- `v1_process_architecture_tp2_dp4.png`: **图示解读：**

1) **图里画了什么**：V1 进程架构（8 GPU，TP=2 张量并行，DP=4 数据并行）。HTTP 请求经 4 个 **API Server** 通过 **ZMQ** 全交叉连接至 4 个 **DP Rank**（Engine Core 0–3），每 Core 通过 TP=2 管理 2 个 **GPU Worker**（共 8 卡 GPU 0–7）；顶部 **DP Coordinator** 负责负载均衡；总计 17 个进程。

2) **技术结论**：vLLM V1 采用**进程级解耦**架构——API 服务、引擎调度、GPU 计算三层独立，ZMQ 消息总线实现灵活的 DP×TP 二维扩展，Coordinator 统一调度负载。

3) **与文档关系**：对应"Online Serving"入口，展示 vLLM 如何通过分层多进程模型支撑高吞吐在线推理，印证其分布式可扩展设计。
- `llm_engine.excalidraw.png`: **图示解读：**

1) **结构与数据流**：标题"LLM Engine"下分三层。上层为两个入口——左侧`LLM class`（离线）、右侧`OpenAI-compatible API Server`（在线）；中层为统一的`LLMEngine`核心，以及包裹它的异步版本`AsyncLLMEngine`（API Server→AsyncLLMEngine→LLMEngine）；底层为`LLMEngine`驱动的四个处理模块：Input Processing、Scheduling、Model Execution、Output Processing。

2) **技术结论**：vLLM采用"多入口、单引擎"架构，无论同步离线调用还是异步在线服务，最终都汇聚到同一个`LLMEngine`，共享输入处理、调度、模型执行、输出处理的完整流水线。

3) **与文档关系**：直观印证了文档"vLLM provides a number of entrypoints"的核心论点，揭示各入口与底层引擎的层级调用关系。
- `hierarchy.png`: **图文联合解读：**

图示为vLLM推理栈的自顶向下分层结构：**LLM Engine → Executor → Worker(Rank 0…N-1) → Model Runner → Model**，各层均以`vllm_config`为入参，Executor向多Rank分发Worker，体现分布式并行（张量/流水线并行）拓扑。

**技术结论：** 单进程入口（LLM类）通过Executor-Worker抽象屏蔽底层多卡并行细节，实现"一份接口、分布式执行"的可扩展架构。

**与文档关系：** 对应"Entrypoints"章节，直观印证LLM离线接口背后并非单卡执行，而是统一的Engine→Executor→Worker→Model分层调度链，为后续Online Serving的Server/AsyncLLMEngine奠定同一执行骨架。
