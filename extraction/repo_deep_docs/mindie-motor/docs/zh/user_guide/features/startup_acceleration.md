# D2D 权重加载

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/startup_acceleration.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/startup_acceleration.md

# D2D 权重加载 文档深度解读

## 【定位】

这篇文档描述 MindIE Motor 提供的 **D2D（Device-to-Device）权重加载启动加速能力**——新实例启动时绕过全量磁盘加载，直接从集群内同角色 ACTIVE 实例经网络拉取权重分片，从而缩短大模型推理实例的冷启动耗时；当前仅 vLLM 引擎支持。

---

## 【技术要点】

- **核心加速机制**：以 `netloader` 方式从同角色 ACTIVE peer 拉取权重分片，替代从本地磁盘全量读取；首个实例充当 seed（仍从磁盘加载并对外提供权重服务），后续实例走 D2D 拉取路径。
- **Peer 自动发现**：由 Controller 自动发现同角色 ACTIVE 实例并下发给 NodeManager，**无需手动填写 peer IP**；peer 匹配要求同角色且状态 ACTIVE，排除自身。
- **关键配置项**：在 `motor_engine_*_config.engine_config.model_loader_extra_config` 下设置 `source="auto"`（固定值，表示由 Controller 自动填充 peer 地址）+ `listen_port`（权重服务起始端口），三者同时满足才会被 Controller 判定 D2D 开启，并自动设置 `load_format="netloader"`。
- **端口偏移规则**：各 device 实际端口 = `listen_port + device_rank`（含 dp 偏移）；启用投机推理（MTP）时 draft 模型权重服务端口在 `listen_port` 基础上**自动偏移 10000**，建议 `port` 配置 `< 55535 - device_rank`。
- **可选优化**：可启用 INT8 缓存（`int8_cache` + `int8_cache_name`）压缩传输量，默认不开启、走全量参数直传；`output_prefix` 用于权重输出前缀。
- **主/草稿模型共享配置**：启用 `speculative-config` / MTP 时，主模型与 draft 模型**共用同一组 `source` 和 `listen_port`**，无需额外配置。
- **字段大小写兼容**：`listen_port` 与 `LISTEN_PORT` 等价。

---

## 【关键机制与数据】

**工作原理数据流**（原文步骤）：

1. 用户在 `user_config.json` 的 `engine_config.model_loader_extra_config` 中写入 `source:"auto"` 与 `listen_port`。
2. **首个实例（seed）**：无可用 peer → Engine 从本地磁盘加载权重 → 自身以 `listen_port` 对外提供权重服务。
3. **后续实例**：Controller 收集同角色 ACTIVE 实例 IP → 下发 NodeManager → Engine 以 `netloader` 从 peer 拉取对应分片权重。
4. 整个 peer 发现 + 路由过程由 Controller / NodeManager 自动完成。

**Controller 启用判定（同时满足，原文）**：

- `model_loader_extra_config` 存在且为合法 JSON 对象；
- `source == "auto"`；
- `listen_port` 已配置。

**性能/数字信息**：原文未给出加速倍率、耗时对比、带宽占用等量化性能数据，仅给出端口计算公式与偏移常量 `10000`、上限建议 `55535 - device_rank`。

---

## 【表格解读】

### 表 1：关键字段表（逐字还原）

| 字段 | 必填 | 说明 |
|------|------|------|
| `source` | 是 | 固定为 `"auto"`，表示 peer 地址由 Controller 自动填充 |
| `listen_port` | 是 | 本实例对外提供权重服务的起始端口；各 device 实际端口为 `listen_port + device_rank(含dp偏移)` |

**逐行解读**：
- `source`：唯一合法取值为字符串 `"auto"`，是 Controller 判断是否走 D2D 路径的硬性条件；其语义是"放弃手工指定 peer，把地址解析权交给 Controller"。
- `listen_port`：必填的起始端口；端口并非直接绑定在该数字上，而是按 device rank 偏移（含 DP 偏移），所以同一实例多 device 实际监听的是连续端口段。

### 表 2：可选字段表（逐字还原）

| 字段 | 说明 |
|------|------|
| `int8_cache` | 是否启用 INT8 缓存，默认不开启，全量参数直传 |
| `int8_cache_name` | INT8 缓存名称 |
| `output_prefix` | 权重输出前缀 |

**逐行解读**：
- `int8_cache`：传输层压缩开关，开启后权重以 INT8 量化后传输以节省带宽；默认关闭意味着默认走 fp 直传以避免精度损失。
- `int8_cache_name`：与 `int8_cache` 配套使用，命名缓存以便复用。
- `output_prefix`：仅控制权重落盘/输出的前缀路径，不影响 D2D 拉取行为本身。

### 表 3：已测试模型表（逐字还原）

| 模型 | 配置目录(参考) |
|------|----------|
| Qwen3-30B | `examples/infer_engines/vllm/models/qwen_235b/` |
| DeepSeek-V3.1-w8a8-mtp | `examples/infer_engines/vllm/models/deepseek_v3.1/` |
| Deepseekv4-flash-w8a8-mtp | `examples/infer_engines/vllm/models/deepseek_v4_flash/` |
| DeepSeek-V4-Pro-w4a8 | `examples/infer_engines/vllm/models/deepseek_v4_pro/` |
| GLM-5.1-w4a8 | `examples/infer_engines/vllm/models/glm_5.1/` |
| GLM-5.1-w8a8 | `examples/infer_engines/vllm/models/glm_5.1/` |

**逐行解读**：
- 覆盖 Qwen3、DeepSeek-V3.1/V4-flash/V4-Pro、GLM-5.1 等典型大模型；其中 DeepSeek-V3.1-w8a8-mtp、Deepseekv4-flash-w8a8-mtp 显式带 `mtp` 后缀，验证了**投机推理场景下主/草稿模型共享配置**这一特性。
- GLM-5.1 同一目录承载 w4a8 与 w8a8 两个量化变体，意味着 INT8 缓存（`int8_cache`）路径在 MindIE Motor 示例配置中具备可用参考。
- 表格意在说明 D2D 已具备端到端示例，非全模型覆盖；未列出的模型仍需自行验证，可通过官方 ISSUE 反馈。

---

## 【公式解读】

原文无公式（仅有以文字描述的端口偏移规则 `listen_port + device_rank` 与 draft 偏移常量 `10000`，未以数学/LaTeX 形式给出）。

---

## 【关联】

- **角色与配置键**：文中所有配置示例均落在 `motor_engine_prefill_config` / `motor_engine_decode_config` / `motor_engine_union_config` 三个角色配置键下，说明 D2D 与 MindIE Motor 的 Prefill / Decode / Union 三角色部署模型直接耦合；D2D 的"同角色匹配"约束正是这三角色配置的语义体现。
- **引擎层**：`load_format = "netloader"` 是 vLLM 侧的官方加载格式之一，文档表明 MindIE Motor 在 D2D 模式下将该字段透明注入到 vLLM engine_config。
- **投机推理路径**：与 `speculative-config` / MTP 共享同一组 `source`/`listen_port`、并自动偏移 10000，说明 D2D 与投机解码（MTP/draft 模型）在同一启动流程内联。
- **Controller / NodeManager**：peer 发现、IP 收集、port 下发、状态判定（ACTIVE）均由 MindIE Motor 的控制面完成，D2D 是其上构建的应用层能力。
- **示例代码库**：表格中的 `examples/infer_engines/vllm/models/...` 是该特性的端到端参考样例；其余模型在该目录未覆盖。
- **内部链接**：原文未提供任何内部链接。

---

## 【使用方法】

**启用方式**（原文给出）：

1. 在 `user_config.json` 中为对应角色（Prefill / Decode / Union）添加：

   ```json
   {
     "motor_engine_prefill_config": {
       "engine_type": "vllm",
       "engine_config": {
         "model": "/data01/models/DeepSeek-V3.1",
         "model_loader_extra_config": {
           "source": "auto",
           "listen_port": 10000
         }
       }
     }
   }
   ```

2. 部署首个实例，等待进入 ACTIVE 状态（此时 seed 模式从磁盘加载并暴露权重服务）。
3. 扩容或部署同角色新实例，Controller 自动下发 peer IP，新实例走 `netloader` 拉取。

**配置项命令/约束**（原文给出）：

- `source`：固定 `"auto"`，否则 Controller 不开启 D2D。
- `listen_port`：必填；需在集群网络内可达且不与已有服务端口冲突。
- 投机推理 / MTP：主模型与 draft 模型共用同一组配置，draft 端口在 `listen_port` 基础上自动 +10000，建议 `port < 55535 - device_rank`。
- 可选 `int8_cache` / `int8_cache_name` / `output_prefix`，默认不启用 INT8 缓存、全量参数直传。
- 字段大小写不敏感（`listen_port` ≡ `LISTEN_PORT`）。
- 引擎限制：仅 vLLM。
- peer 匹配：同角色 + ACTIVE + 排除自身。
- 首个实例（seed）仍需可访问本地模型权重目录；后续实例可仅依赖 D2D。

原文未提供 CLI 命令、API endpoint 或 RPM/DEB 安装步骤。
