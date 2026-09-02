# EPLB 背景介绍

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/EPLB.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/EPLB.md

# EPLB 特性文档深度解读

---

## 【定位】

本篇文档描述 **EPLB（Expert Parallelism Load Balancer，专家并行负载均衡器）** 这一特性的完整使用方法：在 MoE 架构下，通过"采集 token→expert 的路由分布 → 用 EPLB 策略生成冗余专家映射 → 在推理阶段按映射表 P2P 重新分发专家权重"三步流程，解决因专家接收 token 数量不均而导致的 GPU/NPU 算力浪费问题，提升 MoE 模型推理与训练效率。

---

## 【技术要点】

1. **三步流水线（Step1→Step2→Step3）**：MoE Token Collect → EPLB Map Generate → EPLB Usage，分别承担"采集路由数据"、"生成冗余专家映射表"、"按映射表重发专家权重"职责。

2. **MoE Token Collect**：拦截 `AscendUnquantizedFusedMoEMethod.apply` 调用，按 layer 累计统计 `topk_ids`（每个 token 被路由到的 expert ID）；每个 rank 在各自所在节点保存一份 `eplb_token_collects_{rank}.json` 文件，文件中按"外层 key=MoE 层号 / 内层 key=expert ID / 值=被分配的 token 数"组织。

3. **多机 JSON 汇总**：在主节点执行 `examples/eplb/collect_json_file.sh`，脚本通过 `SERVERS` 列表（如 `"root@IP"` 格式）将各节点的 JSON 文件统一收集到主节点；共享存储场景下无需运行此脚本。

4. **EPLB 映射生成策略**（源自 DeepSeek 开源 EPLB）：分层负载均衡——先在节点间均匀分配专家 → 接着在节点内复制专家 → 再将复制后的专家分配到各 NPU；并对每个 NPU 内部做去重，确保同一 NPU 不重复分配专家。

5. **冗余专家参数化配置**（`eplb.sh` 中调用 `eplb_generate_map_ds.py`）：关键参数为 `--num_replicas 40`（冗余专家总数，含原始专家）、`--num_groups 4`（分组数，要求能被 num_gpus 整除）、`--num_nodes 1`、`--num_gpus 8`、`--output_path mindspeed_rl/workers/eplb/expert_map.json`。

6. **推理阶段权重重发**：基于分布式并行策略先生成初始专家映射（即推理侧初始权重存放情况），再以 Step2 输出的 `expert_map.json` 为目标，通过 **P2P 通信**将专家权重从初始状态迁移到目标状态。

---

## 【关键机制与数据】

### 数据流（端到端）

```
MoE 前向计算
    └─ 拦截 AscendUnquantizedFusedMoEMethod.apply
         └─ 统计 topk_ids，按 layer 累计
              └─ 每个 rank → 本地写 eplb_token_collects_{rank}.json   [Step1]
                   └─ 主节点运行 collect_json_file.sh
                        └─ 各节点 JSON 汇总到主节点 json_folder
                             └─ eplb_generate_map_ds.py 执行 EPLB 策略
                                  └─ 输出 expert_map.json（冗余专家→NPU 映射）   [Step2]
                                       └─ 推理启动时按 expert_map.json 做 P2P 重发权重   [Step3]
```

### 关键机制说明（均来自原文）

- **Step1 采集机制（原文）**：「在 MoE 前向计算时，系统会拦截 `AscendUnquantizedFusedMoEMethod.apply` 调用」「自动统计 `topk_ids`……并按 layer 累计」「每个 rank 的数据会收集各自所在的节点上，并保存各自对应的 JSON 文件」。
- **Step2 映射生成机制（原文）**：「使用分层负载均衡策略来分配专家。首先将专家均匀分配到各个节点，确保不同节点的负载保持平衡。接着，在每个节点内部复制专家。最后，将这些复制后的专家分配到各个 npu 上」「去重处理：每个 NPU 内部不重复分配专家」。
- **Step3 权重重发机制（原文）**：「基于推理的分布式并行策略生成初始化的专家映射表，代表推理侧的初始权重存放情况」「Step2 生成的 Eplb_map 作为权重分配的目标映射表，将权重从初始状态重新收发，达到目标状态」「专家权重的收发采用 p2p 实现」。
- **文件写入安全（原文）**：「采用临时文件 + 原子替换，避免因进程异常退出导致 JSON 文件损坏」。
- **性能开销（原文）**：「开启采集后会增加统计与 JSON I/O，建议在 profiling 或 debug 时使用」「涉及 `P2P` 通信，建议在资源充足时使用」。

### 性能数据

原文未给出任何具体性能数字（如加速比、吞吐提升百分比等），仅以文字形式提示了 I/O 与 P2P 通信开销。

---

## 【表格解读】

原文无结构化表格（含表头的对照表）。

但原文在 Step1 与 Step2 中各自展示了一份 **JSON 文件结构示例**，可视为结构化数据约定。为保留原文样貌，逐字还原如下：

### 表 1：Step1 输出 JSON 结构（原文逐字还原）

```json
{
  "0": {
    "0": 123,
    "1": 256,
    "2": 89,
    ...
  },
  "1": {
    "0": 88,
    "1": 190,
    ...
  }
}
```

逐行解读：
- 外层 key `"0"`、`"1"` —— **MoE 层号**（原文：「外层 key 表示 MoE 层号」）。
- 内层 key `"0"`、`"1"`、`"2"` —— **expert ID**（原文：「内层 key 表示 expert ID」）。
- 内层 value（如 `123`、`256`、`89`、`88`、`190`）—— **该 expert 被分配的 token 数**（原文：「值为该 expert 被分配的 token 数」）。
- 文件命名约定：`eplb_token_collects_{rank}.json`，由各 rank 分别写入。

### 表 2：Step2 输出 JSON 结构（原文逐字还原）

```json
{
    "moe_layer_count": 1,
    "layer_list": [
        {
            "layer_id": 0,
            "device_count": 2,
            "device_list": [
                {
                    "device_id": 0,
                    "device_expert": [0, 1, 2, 3, 5]
                },
                {
                    "device_id": 1,
                    "device_expert": [5, 6, 7, 8, 1]
                }
            ]
        }
    ]
}
```

逐行解读：
- `moe_layer_count: 1` —— **总 MoE 层数**（原文：「moe_layer_count 表示总 MOE 层数」）。
- `layer_list` —— **每层的专家映射表列表**（原文：「layer_list 表示每层的专家映射表」）。
  - `layer_id: 0` —— **MoE 层号**（原文：「layer_id 表示 MOE 层号」）。
  - `device_count: 2` —— **NPU 总数**（原文：「device_count 表示 npu 总数」）。
  - `device_list` —— **该 MoE 层中每个 NPU 的专家映射表**（原文同义）。
    - `device_id: 0 / 1` —— **NPU rank**（原文：「device_id 表示 npu rank」）。
    - `device_expert: [0,1,2,3,5]` / `[5,6,7,8,1]` —— **该 NPU 上分配的 expert ID**（原文：「device_expert 表示该 npu 上分配的 expert ID」）。
  - 由示例可看出：同一 expert ID（如 `5`、`1`）可出现在多个 device 的 `device_expert` 中，体现"冗余副本"思想；同时同一 device 内 expert ID 不重复，体现"NPU 内去重"约束。

---

## 【公式解读】

原文无公式（含 LaTeX 或伪代码形式），仅以 YAML 参数与 JSON 结构表达配置与输出。原文无公式。

---

## 【关联】

文末内部链接信息标注为"（无）"，因此本节仅依据正文行文中可识别的关联点整理：

- **与 MoE 推理/训练主流程的关联**：Step1 通过拦截 `AscendUnquantizedFusedMoEMethod.apply` 挂接到 MoE 前向计算路径，属于"旁路统计型"插件；Step3 则在推理启动时介入，通过 `expert_map_path` 控制专家权重的初始放置。
- **与分布式并行策略的关联**：Step3「基于推理的分布式并行策略生成初始化的专家映射表」，说明其依赖并作用于已有的分布式并行框架（具体并行策略在文档外）。
- **与配置系统（YAML）的关联**：Step1 与 Step3 都通过 yaml 的 `generate` 节点配置（`token_collects`、`token_save_path`、`expert_map_path`）；Step1 的 `token_save_path` 又与 Step2 的 `json_folder` 保持路径一致，形成数据传递链。
- **与脚本/工具的关联**：
  - `examples/eplb/collect_json_file.sh` —— 多机 JSON 汇总脚本（Step1 末端）。
  - `examples/eplb/eplb.sh` —— 调用 `mindspeed_rl/workers/eplb/eplb_generate_map_ds.py` 执行 Step2。
  - `examples/eplb/grpo_trainer_deepseek_r1_671b_eplb.sh` + `grpo_deepseek_r1_671b_A3_eplb.yaml` —— Step3 的运行入口与配置文件。
- **与上游开源实现的关系**：Step2 明确指出使用「DeepSeek 开源的 EPLB 策略」。

---

## 【使用方法】

### 启用 Step1：MoE Token Collect

1. yaml 配置（`generate` 节点）：
```yaml
generate:
  token_collects: true                # 是否开启 token 收集
  token_save_path: "/path/to/save"    # JSON 文件保存目录, 默认为 json_file
```
- `token_collects`：`true` 开启，`false` 默认关闭（避免不必要 I/O）。
- `token_save_path`：必填，指定 JSON 存储目录；各 rank 在各自节点写入 `eplb_token_collects_{rank}.json`。

2. 多机环境配置 `examples/eplb/collect_json_file.sh`：
```yaml
SERVERS = (
      "root@IP"
      "root@IP"
      )
```
- `SERVERS`：必填，远程服务器列表（`user@ip` 格式）；共享存储场景下无需运行此脚本。

3. 运行推理或训练 → 各 rank 本地写 JSON → 主节点执行 `bash examples/eplb/collect_json_file.sh` 汇总。

### 启用 Step2：EPLB Map Generate

执行 `examples/eplb/eplb.sh`（原文脚本片段）：
```bash
python  mindspeed_rl/workers/eplb/eplb_generate_map_ds.py \
--json_folder ./json_file \
--num_replicas 40  \
--num_groups  4 \
--num_nodes  1 \
--num_gpus 8 \
--output_path mindspeed_rl/workers/eplb/expert_map.json \
```
参数含义（原文）：
- `json_folder`：主节点上 `eplb_token_collects_{rank}.json` 所在目录（与 Step1 的 `token_save_path` 一致）。
- `num_replicas`：冗余专家总数（含原始专家），示例 `40`。
- `num_groups`：负载均衡策略中的专家分组数，示例 `4`；**要求能被 `num_gpus` 整除**。
- `num_nodes`：机器数，示例 `1`。
- `num_gpus`：总 NPU 数，示例 `8`。
- `output_path`：生成的 JSON 文件路径，示例 `mindspeed_rl/workers/eplb/expert_map.json`。

### 启用 Step3：EPLB Usage

1. 关闭 Step1 相关配置：
```yaml
generate:
  #token_collects: true                # 是否开启 token 收集
  #token_save_path: "/path/to/save"    # JSON 文件保存目录
```

2. 在 `grpo_deepseek_r1_671b_A3_eplb.yaml` 的 `generate` 节点下指定：
```yaml
expert_map_path: /file/to/save
```
- `expert_map_path`：必填，专家映射表文件路径（与 Step2 `eplb.sh` 的 `output_path` 一致）。

3. 启动：
```bash
bash examples/eplb/grpo_trainer_deepseek_r1_671b_eplb.sh
```

### 使用限制（原文）
- 推理目前只支持**单实例**。
- 每个 NPU 上的专家数需要保持一致（Step2 约束）。
- Step3 涉及 P2P 通信，建议在资源充足时使用。
