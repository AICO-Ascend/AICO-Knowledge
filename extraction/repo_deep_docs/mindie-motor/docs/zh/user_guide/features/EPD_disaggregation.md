# EPD分离部署能力说明

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/EPD_disaggregation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/EPD_disaggregation.md

# 一体化深度解读：EPD分离部署能力说明

## 【定位】

这篇文档描述了 MindIE Motor 在多模态大语言模型场景下，将视觉编码器（Encoder）、预填充（Prefill）、解码（Decode）三个阶段分别部署为独立 vLLM 进程/实例的能力，并给出了基于 `user_config.json` + `deploy.py` 的部署方法（以 Qwen3-VL-30B-A3B-Instruct 为示例）。

## 【技术要点】

- **三段式分离架构**：Encode instance → Prefill instance → Decode instance，各自作为独立 vLLM 实例部署，中间通过两类 Transfer Engine 衔接。
- **两种 Transfer Engine**：Encode→Prefill 之间是 **Encoder Cache Transfer Engine**（视觉编码特征传递）；Prefill→Decode 之间是 **KV Cache Transfer Engine**（KV 缓存传递）。
- **支持的部署模式**：`infer_service_set` 和 `multi_deployment` 两种模式均可使用 EPD 分离。
- **支持的调度模式**：`CPCD` 与 `CDP` 两种调度模式都可用，且 **总是优先调度 E 实例**，之后才按原有调度逻辑进行。
- **关键配置入口**：通过修改 `user_config.json` 中的 `motor_deploy_config`（实例/Pod/NPU 数量）以及新增的 `motor_engine_encode_config`（配合 `ec-transfer-config`）来启用 EPD 分离，最后通过 `deploy.py` 完成部署。
- **示例配置数字**：示例中使用 `e_instances_num=2`、`p_instances_num=1`、`d_instances_num=1`，各实例均为 `single_*_instance_pod_num=1`、`*_pod_npu_num=2`；Encode 端 `tensor_parallel_size=1`，Prefill/Decode 端 `tensor_parallel_size=2`；`max_model_len=128000`、`gpu_memory_utilization=0.9`、`seed=1024`。

## 【关键机制与数据】

- **工作原理**（原文架构图）：三个独立 vLLM 实例（Encode / Prefill / Decode）通过两种 Transfer Engine 串成流水线——Encoder Cache Transfer Engine 将视觉编码特征从 Encode 送至 Prefill，KV Cache Transfer Engine 将 KV 缓存从 Prefill 送至 Decode。原文示意图明确呈现了 "Encode instance ──Encoder Cache Transfer Engine──► Prefill instance ──KV Cache Transfer Engine──► Decode instance" 的链路。
- **调度顺序**：两种调度模式（CPCD / CDP）下，**先调度 E 实例**，再沿用原有 P/D 调度逻辑（原文：原文"在两种调度模式下都是先调度E实例，然后再按照之前逻辑进行调度"）。
- **角色配对**（producer/consumer）：
  - Encode 端 `ec_role = ec_producer`
  - Prefill 端 `ec_role = ec_consumer`、`kv_role = kv_producer`
  - Decode 端 `kv_role = kv_consumer`
- **Encoder Cache 共享存储**：`shared_storage_path = /mnt/share/patch/ec_cache`，作为 ECExampleConnector 的共享缓存目录。
- **KV Cache 传输参数**：`kv_connector = MooncakeConnectorV1`、`kv_buffer_device = npu`、`kv_port = 30001`、`kv_parallel_size = 1`、`engine_id = 0`、`kv_rank = 0`。
- **多模态输入路径**：`allowed-local-media-path = /mnt/share/patch/media_path/`，`trust-remote-code = true`，`enforce_eager = true`（仅 Encode 端）。
- **部署执行**：`cd examples/deployer`，运行 `python deploy.py --config_dir ../infer_engines/vllm` 或 `python deploy.py --user_config_path ../infer_engines/vllm/user_config.json --env_config_path ../infer_engines/vllm/env.json`，输出 `...... all deploy end.` 即成功。
- **注意点**（原文）：① 模型权重需支持多模态；② vLLM Ascend 当前支持两种 connector，原文示例使用 `ECExampleConnector`。

## 【表格解读】

原文无表格（仅以 JSON 配置文件呈现配置项，无 markdown 表格 / 性能对比表 / 参数表形式的内容）。原文涉及的"结构化配置"以 JSON 给出，但不属于表格范畴，因此不另行转写。

## 【公式解读】

原文无公式。

## 【关联】

- **../quick_start.md（MindIE Motor 快速开始）**：文档显式声明"以 MindIE Motor 快速开始 中实例 user_config.json 为参考基线"，说明本文的 EPD 部署配置是快速开始章节配置模板的扩展；用户应先阅读快速开始以理解基础 `user_config.json` 结构，再按本文增补 E/P/D 三段相关字段。
- **vLLM Ascend EPD分离特性说明（外部链接 `https://docs.vllm.ai/projects/ascend/en/latest/user_guide/feature_guide/epd_disaggregation.html`）**：作为上游 vLLM Ascend 的特性参考，详细描述了"分离式编码器"的收益与 connector 机制，本文在 E 端 `ec-transfer-config` / `ec_role` 的语义上明确指向该链接。
- **MindIE Motor 自身组件**：`motor_deploy_config` 控制 Pod/NPU/实例拓扑；`motor_engine_encode_config` / `motor_engine_prefill_config` / `motor_engine_decode_config` 三个 engine 配置块分别对应三段 vLLM 实例；`motor_controller_config` 与 `motor_coordinator_config` 在示例中保持空对象（`{}`）。
- **examples/deployer 部署脚本**：与快速开始章节共享同一 `deploy.py` 入口，本文给出两种传参方式（`--config_dir` 与 `--user_config_path` + `--env_config_path`）。

## 【使用方法】

**启用方式与配置项**（原文给出）：

1. **准备模型权重**：使用支持多模态理解的模型，原文示例为 `Qwen3-VL-30B-A3B-Instruct`，挂在 `/mnt/weight/`。
2. **编辑 `user_config.json`**：
   - 在 `motor_deploy_config` 中填写 E/P/D 实例数、Pod 数、每 Pod NPU 数（如 `e_instances_num=2 / p_instances_num=1 / d_instances_num=1`、`*_pod_npu_num=2`、`deploy_mode=multi_deployment`、`hardware_type=800I_A2`）。
   - 新增 `motor_engine_encode_config`，其中 `engine_config` 内增加：
     - `ec-transfer-config`：`ec_connector=ECExampleConnector`、`ec_role=ec_producer`、`ec_connector_extra_config={"shared_storage_path": "/mnt/share/patch/ec_cache"}`。
     - Encode 特有项：`tensor_parallel_size=1`、`enforce_eager=true`、`no-enable-prefix-caching=true`。
   - 在 `motor_engine_prefill_config.engine_config` 中增加 `ec-transfer-config`（`ec_role=ec_consumer`，共享存储同上）和 `kv_transfer_config`（`kv_connector=MooncakeConnectorV1`、`kv_buffer_device=npu`、`kv_role=kv_producer`、`kv_parallel_size=1`、`kv_port=30001`、`engine_id=0`、`kv_rank=0`、`tensor_parallel_size=2`）。
   - 在 `motor_engine_decode_config.engine_config` 中增加 `kv_transfer_config`（`kv_role=kv_consumer`，其余 KV 参数与 Prefill 端对齐，`tensor_parallel_size=2`）。
3. **执行部署脚本**（`cd examples/deployer`）：
   - 推荐：`python deploy.py --config_dir ../infer_engines/vllm`
   - 备选：`python deploy.py --user_config_path ../infer_engines/vllm/user_config.json --env_config_path ../infer_engines/vllm/env.json`
4. **成功标志**：终端输出 `...... all deploy end.`。

**调度/部署模式相关**（原文涉及）：支持 `infer_service_set` 与 `multi_deployment` 两种 `deploy_mode`；支持 `CPCD` 与 `CDP` 两种调度模式，二者均按"先 E、后常规"顺序调度。
