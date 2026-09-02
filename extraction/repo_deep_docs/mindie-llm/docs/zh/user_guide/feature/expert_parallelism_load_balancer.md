# 负载均衡

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/expert_parallelism_load_balancer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/expert_parallelism_load_balancer.md

# 深度解读：MindIE-LLM MOE 负载均衡特性

## 【定位】

本篇文档描述 MindIE-LLM 在 MOE（Mixture-of-Experts）架构推理中，通过**静态冗余负载均衡**与**强制负载均衡**两种机制，降低因热门/冷门专家不均导致的 AlltoAll 通信与算力负载不均衡，从而提升大模型推理性能的能力及使用流程。

---

## 【技术要点】

- **两种负载均衡策略**：「静态冗余负载均衡」通过额外部署冗余专家分散热点；「强制负载均衡」通过 mock topk 输出制造"假"的绝对均衡 tensor，仅供理论上限评估。
- **硬件与模型约束**：仅支持 Atlas 800I A2/A3 推理服务器；仅 DeepSeek R1/V3、Qwen-moe 模型支持；仅在 MOE All2All 通信场景（`ep_level=2`）下生效。
- **PD 分离特殊性**：Prefill 与 Decode 通常采用不同集合通信方式，负载均衡配置参数需**分别设置**；冗余专家部署表也要分别生成。
- **显存代价**：静态冗余负载均衡每卡多部署 1 个冗余专家，**需额外占用 2.4 GB 显存**。
- **三步使用流程**：专家热点信息采集 → 冗余专家部署表生成 → 负载均衡参数配置；强制负载均衡可跳过前两步。
- **核心工具**：依赖 `msit` 工具的 `elb` 组件，提供 C2LB 与 speculative-moe interface 两种算法，当前 **speculative-moe level 2（`al 5`）取得最优**。
- **典型命令**：`msit elb -icp input_dir_path -o output_file_path -nre 64 -nd 8 -nn 64 -al 5 -dt a2`（8 机 64 卡）。
- **强制负载均衡的业务禁区**：原文明确「强制负载均衡只是为负载均衡提供了理论上限，改变了模型专家实际路由，不能在正式业务中使用」。

---

## 【关键机制与数据】

### 工作原理（数据流）

1. **专家热点采集**：在不开负载均衡时推理业务，通过环境变量 `MINDIE_ENABLE_EXPERT_HOTPOT_GATHER=1` 与 `MINDIE_EXPERT_HOTPOT_DUMP_PATH=<path>` 导出 csv。每个 NPU 生成一个 csv，内含 `num_moe_layer × 单NPU专家数` 的矩阵，每数字代表该 layer 中该 expert 计算的 token 数，**每 8 个 token 追加一次该矩阵**。Prefill 与 Decode 分别保存。原文：
> "矩阵中的每个数字代表该layer中该专家所计算的token数，每8个token会在采集文件中追加该矩阵。"

2. **冗余专家部署表生成**：使用 `msit elb` 组件处理采集的 csv，原文：
> "msit工具提供两种负载均衡算法：计算通信负载均衡算法（C2LB）和speculative-moe interface algorithm。当前speculative-moe level 2 混置算法（al 5）取得最优."

3. **参数生效**：将生成的部署表写入 atb-models 的 `config.json` 的 `models/deepseekv2/eplb` 字段下，开启相应 `level`。

### 性能与代价数据（原文）

- 每卡额外显存：**2.4 GB**（静态冗余负载均衡）。
- 热点文件粒度：每 8 个 token 采样一次。
- 典型部署规模：8 机 64 卡（`-nre 64 -nd 8 -nn 64 -al 5 -dt a2`）。
- OOM 兜底建议：「如果长序列场景下采集专家热点信息时遇到OOM的情况，建议减少序列长度采集」（原文）。

### 注意事项（原文）

> "强制负载均衡只能作为负载均衡的理论上限，不能在正式业务中使用。"

> "如果是服务化采集，数据集跑完后请及时关闭服务化。"

---

## 【表格解读】

原文包含一张参数配置表，逐字还原如下：

|配置项|取值类型|取值范围|配置说明|
|--|--|--|--|
|level|int|[0, 3]|0 : 不开启负载均衡<br>1 : 开启静态冗余负载均衡<br>2 : 开启动态冗余负载均衡（暂不支持）<br>3 : 开启强制负载均衡<br>默认值：0|
|expert_map_file|string|该文件路径存在|静态冗余负载专家部署表路径。<br>默认值：""|

**逐行解读：**

- **level（int，[0, 3]，默认 0）**：负载均衡的总开关枚举。`0` 不开启；`1` 开启静态冗余（生产可用）；`2` 动态冗余但原文标注「暂不支持」；`3` 强制负载均衡，仅作理论上限。该字段同时决定了 `expert_map_file` 是否被消费（仅 level=1 需要）。
- **expert_map_file（string，默认 ""）**：静态冗余专家部署表的 JSON 文件路径，由前述 `msit elb` 命令生成。该字段无取值范围（仅校验路径是否存在），意味着必须保证路径可访问，否则加载阶段会报错。

> 原文在表格之前的说明文字中还列举了其他可配置项：`rep_per_rank`、`aggregate_threshold`、`buffer_expert_layer_num`、`num_expert_update_ready_countdown`，但原文表格中**仅详细列出了 `level` 与 `expert_map_file` 两项**，其余参数未给出取值范围与说明，未在原文表格中体现，故不在此处臆造补充。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

本节基于原文显式提及的模块/上下文进行梳理（无内部链接提供）：

- **msit 工具链（外部）**：本特性的部署表生成依赖 `msit` 的 `elb` 组件（仓库 `https://gitcode.com/Ascend/msit`），并提供了配套的「负载均衡亲和专家寻优指南」。其姊妹组件如 `msit-surgeon / msit-analyze / msit-convert / msit-profile` 等在原文中仅以安装回显形式被列出，不直接参与本特性流程。
- **MOE All2All 集合通信**：本特性仅在 `ep_level=2` 场景下生效，与 MOE 的专家并行通信模式耦合。
- **PD 分离场景**：Prefill 与 Decode 采用不同通信方式，因此热点采集、部署表生成、参数配置三步均需**分别**执行；PD 混合场景则可仅生成 Decode 表。
- **MindIE 服务化配置**：通过 `examples/kubernetes_deploy_scripts/conf/mindie_env(_a3).json` 中的 `mindie_server_prefill_env` 与 `mindie_server_decode_env` 注入热点采集环境变量。
- **atb-models 配置层**：参数最终落点到 `{ATB安装路径}/atb-models/atb_llm/conf/config.json` 的 `models/deepseekv2/eplb` 字段，与 atb-models 推理框架耦合。
- **支持的模型族**：DeepSeek R1/V3、Qwen-moe，提示特性针对具体模型结构做过适配。

---

## 【使用方法】

### 一、专家热点信息采集（仅静态冗余负载均衡需要）

在 `examples/kubernetes_deploy_scripts/conf/mindie_env(_a3).json` 的 `mindie_server_prefill_env` / `mindie_server_decode_env` 中追加：

```json
{
    "MINDIE_ENABLE_EXPERT_HOTPOT_GATHER": 1,
    "MINDIE_EXPERT_HOTPOT_DUMP_PATH": "单个实例可选择共享盘路径，否则必须存储在非共享盘"
}
```

运行推理业务后生成 csv；多机数据需手工汇总至同一文件夹，或使用共享盘路径。

### 二、生成冗余专家部署表

```bash
# 1. 安装 msit 与 elb 组件
git clone https://gitcode.com/Ascend/msit.git
cd msit/msit
pip install .
msit install elb
msit check elb

# 2. 8机64卡典型配置示例
msit elb -icp input_dir_path -o output_file_path -nre 64 -nd 8 -nn 64 -al 5 -dt a2
```

PD 分离分别生成 Prefill 与 Decode 的表；PD 混合仅生成 Decode 表。

### 三、配置负载均衡参数

编辑 `{ATB安装路径}/atb-models/atb_llm/conf/config.json`，在 `models/deepseekv2/eplb` 下设置（典型静态冗余负载均衡配置）：

```json
{
    "models": {
        "deepseekv2": {
            "eplb": {
                "level": 1,
                "expert_map_file": "xxxx.json"
            }
        }
    }
}
```

可选附加字段（原文提及但未详细说明）：`rep_per_rank`、`aggregate_threshold`、`buffer_expert_layer_num`、`num_expert_update_ready_countdown`，**原文未涉及** 其取值与含义。

### 强制负载均衡

直接配置 `level: 3` 即可启用，**无需采集热点与生成部署表**，但仅供理论上限评估，不可用于正式业务（原文）。

## 图文联合解读

- `load_balancing_process.png`: **图示解读：**

图描绘静态冗余负载均衡三步流程：①MindIE采集专家热点 → 输出`热点信息.csv` → ②msIT生成冗余部署表 → 输出`专家部署表.json` → ③MindIE配置负载均衡参数。表明该特性由MindIE（采集与配置）与msIT（部署表生成）协同完成，论证"采-算-配"分工落地的技术可行性，支撑文档所述使用流程。
- `expert_hotspot_information_collection.png`: 1) 图示为 JSON 配置文件，分别在 `mindie_server_prefill_env` 和 `mindie_server_decode_env` 中红框标注新增的两个环境变量 `MINDIE_ENABLE_EXPERT_HOTPOT_GATHER=1` 和 `MINDIE_EXPERT_HOTPOT_DUMP_PATH`，前者注"放在非共享盘"，后者注"可放在共享盘"。

2) 论证 PD 分离部署下，Prefill 与 Decode 需独立配置热点采集，且因实例特性不同，Dump 路径选择有所差异。

3) 对应文档"专家热点信息采集"步骤 1 的配置示例，呼应"PD 分离场景参数需分别设置"的约束。
