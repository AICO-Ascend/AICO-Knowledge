# NIXL KV Cache Lease Renewal

> 仓 `vllm` · 路径 `docs/design/nixl_kv_cache_lease.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/nixl_kv_cache_lease.md

# 「NIXL KV Cache Lease Renewal」Design 文档深度解读

## 【定位】

本文档提出 **基于 NIXL 通知的心跳续约机制**,用以解决 vLLm 分离式 prefill/decode 部署中 Prefill 实例(P)在等待 Decode 实例(D)经 RDMA 拉取 KV cache 时,因单一长 timeout 导致的"死块"滞留问题与短 timeout 在流量高峰下引发的"提前释放/无效重算"问题,通过按请求粒度的短期租约 + 周期性心跳续约,在秒级回收失效块与不浪费健康 D 的等待之间取得平衡。

---

## 【技术要点】

1. **问题根因 — 单 timeout 困境**
   - 旧机制仅靠 `VLLM_NIXL_ABORT_REQUEST_TIMEOUT`(默认 **480s**,约 8 分钟)控制 P 端 KV 块的保留时长。D 崩溃/断连时,P 端会持续持有数 GB"死块"至多 8 分钟,期间新请求遭遇缓存容量下降、性能退化。
   - 若简单地缩短该 timeout,在 D 端排队拥塞时(等待调度时间无上界)会出现块被提前释放、KV 被无效重算、prefill 工作浪费的反向故障模式。

3. **租约生命周期(三出口)**
   - **正常完成**:D 完成 KV 拉取后,P 收到 read-completion 通知,**立即释放**。
   - **健康续约**:D 每次心跳将租约延长 `lease_duration * 2/3`(默认配置下约 **20s**),保持块存活无时间上限。
   - **租约到期**:无心跳到达 → 租约到期 → P 回收块。

5. **按请求粒度(per-request)的租约模型**
   - 租约附着在 **每个请求** 上,而非整个 P 实例 —— 关键原因在于 P 在 prefill 时尚不知道请求将由哪个 D 处理,块的所有权关系要等 router 选定 D 后才能解析。按请求建约避免了 load balancer 对 P/D 选择的耦合。同 P 下的多请求以 `remote_engine_id` 分组批量续约。

7. **基于 NIXL 现有通知通道的心跳**
   - 完全复用 `send_notif`/`get_new_notifs` 通知系统,**不引入新的传输层**。
   - 通知载体由 NIXL 根据后端选择(IB/RoCE→TCP 的 fallback 已由 NIXL 自身处理),可跨任意 NIXL 支持的传输工作。
   - P 端解析以 `"HB:"` 前缀开头的消息,路由到 `_handle_heartbeat()`,并以 `max(old_expiry, now + lease_extension)` 更新到期时间 —— **确保租约不会被意外缩短**。

9. **调度器侧提前追踪(避免等待队列死亡区间)**
   - D 端在请求"**进入调度器**"时(而非被调度执行时)即开始心跳追踪。
   - 通过 `NixlConnectorScheduler.on_new_request()` 钩子,识别 `do_remote_prefill=True` 的请求,按 `remote_engine_id` 分组打包。
   - 心跳发送节流:`heartbeat interval = lease_duration // 6`(默认约 **5s**)。
   - 停止追踪时机:① 通过 `update_connector_output` 确认 KV 传输完成;② 通过 `request_finished` 确认请求结束/中止。

11. **前向循环内执行 + 主动握手(proactive handshake)**
    - 心跳的发送与处理均在 forward loop(`start_load_kv` / `get_finished`)中完成,**无后台线程**,避免跨线程锁复杂度。
    - D 在心跳尚未与某 P 握手的场景(请求仍在等待队列中)会触发后台线程的 **主动握手**,这一握手同时也加速了后续真正的 KV 传输。
    - 时间裕量:心跳间隔(~5s)与租约延长(~20s)均 **比典型 forward pass 高至少一个数量级**,因此即便长前向阻塞了心跳节奏也不会丢约。

13. **异构 TP 支持**
    - **P TP > D TP**(如 P=4, D=2):单个 D worker 必须向多个 P worker 发送心跳。
    - **D TP > P TP**:单个 P worker 接收来自多个 D 的通知,等价于对 TTL 多次刷新,**无副作用**。

15. **双向 KV 传输的特殊处理(多轮对话场景)**
    - 下一轮对话的触发时序由客户端决定,**心跳机制不适用**,改用固定 timeout `decoder_kv_blocks_ttl`(默认 **480s**)。
    - D 将到期时间(基于 D 端 `perf_counter`)回传 P,P 通过握手往返估算与 D 的时钟偏移后再与本地时钟比较。
    - 文档明确指出:未来工作可能在该场景引入对称的心跳机制。

---

## 【关键机制与数据】

### 工作原理(原文语义归纳)

- **核心机制**:短初始租约 + 周期性心跳续约。P 在 prefill 完成时授予请求 **30s** 的初始租约;只要 D 健康,D 每 ~5s 发送一次心跳,P 将到期时间延长 ~20s;一旦心跳停止,P 在最后心跳后约 20s 内回收块(而不是旧机制的 480s)。
- **数据流**:
  1. P 完成 prefill → 授予初始租约 → 返回响应(含 `kv_transfer_params`)→ 经路由代理转给 D。
  2. D 收到请求 → `on_new_request()` 钩子立即启动心跳追踪(按 `remote_engine_id` 分组)。
  3. D forward loop 中每 ~5s 一次:`start_load_kv()` 读取 `metadata.heartbeat_by_engine`,经 NIXL 通知通道批量发送心跳(对未握手的 P 触发后台握手)。
  4. P `_get_new_notifs()` 收到 `"HB:"` 前缀消息 → `_handle_heartbeat()` 计算 `max(old_expiry, now + lease_extension)` → 续约。
  5. D 被调度执行 → 发起 RDMA 读 → 传输完成 → `update_connector_output` 停止心跳 → P 立即释放块。
- **关键数字/参数(原文):**
  - `VLLM_NIXL_ABORT_REQUEST_TIMEOUT` 默认 **480s**(旧机制,文档标记为问题根源)。
  - `kv_lease_duration` 默认 **30s**。
  - 心跳延长 = `lease_duration * 2/3` ≈ **20s**。
  - 心跳间隔 = `lease_duration // 6` ≈ **5s**。
  - `decoder_kv_blocks_ttl`(双向场景)默认 **480s**。
- **典型故障恢复时间**(原文:"lease expires (~20s, not 480s)"):D 崩溃后,P 在末次心跳后 **约 20s** 即可回收块;旧机制需等待 480s。

### 三类状态机(Happy Path / Decode Crash / Bidirectional)

| 场景 | 续约机制 | 块回收时机 | 原文要点 |
|---|---|---|---|
| Happy Path | 心跳持续(~5s 一次) | RDMA 传输完成即释放 | 见 "Happy Path" mermaid |
| Decode Crash | 心跳停止 → 租约到期 | 末次心跳后约 20s(原文:"~20s, not 480s") | 见 "Decode Instance Crash" mermaid |
| 双向传输(多轮对话) | **不用心跳**,用 `decoder_kv_blocks_ttl`(480s 固定) | 客户端超时未继续 → 块到期 | D 回传 `perf_counter` 到期值,P 估算时钟偏移 |

---

## 【表格解读】

**原文无表格**(文档以 mermaid 序列图和散文段落呈现机制,未提供参数表/性能对比表/配置表)。

---

## 【公式解读】

原文含有若干嵌入式表达式,逐字保留并解释:

1. **`lease_duration * 2/3`**(约 20s)
   - **符号**: `lease_duration` 为 KV 租约基础时长,默认 **30s**。
   - **作用**: 计算每次心跳对租约的延长量。每个心跳将到期时间往后推 `lease_duration × 2/3`,即默认配置下约 20s。
   - **设计含义**:让租约延长量 > 心跳间隔(后者为 `lease_duration // 6` ≈ 5s),保证只要心跳持续就不会出现"续约赶不上到期"的窗口。

2. **`lease_duration // 6`**(约 5s)
   - **符号**: `lease_duration` 同上,整数除法(`//`)表示向下取整。
   - **作用**: D 端心跳发送的节流间隔。每次 forward step 不会都发心跳,而是按此间隔节流,默认配置下约 5s 一次。
   - **设计含义**:与公式 1 配合,形成 `extension / interval ≈ 4` 的安全冗余比例;`~5s` 心跳 + `~20s` 延长 > forward pass 时延(原文:"seconds vs. milliseconds")。

3. **`max(old_expiry, now + lease_extension)`**
   - **符号**: `old_expiry` 为该请求上一次记录的到期时间;`now` 为 P 端当前时间;`lease_extension` 即公式 1 中的 `lease_duration * 2/3`。
   - **作用**: P 端 `_handle_heartbeat()` 更新到期时间的策略 —— 取"旧到期时间"与"now + 延长量"二者中的较大者。
   - **设计含义**: 防止乱序/迟到心跳把租约意外缩短(原文:"This ensures leases are never accidentally shortened")。

4. **`perf_counter` 时钟偏移估算**(双向场景)
   - **符号**: D 端 `perf_counter` 产生的到期时间戳 `deadline_D`;P 端通过握手往返(round-trip)估算时钟偏移 `offset`,再与 P 端 `perf_counter` 比较。
   - **作用**: 补偿 P、D 处于独立进程、时钟无关的事实,让 P 能正确判断 D 回传的 deadline 是否已到。
   - **设计含义**: 两个引擎独立运行,`perf_counter` 起点不同,直接比较会出错;握手 RTT 提供一次性的偏移估算。

---

## 【关联】

### 与文中提及特性的上下游关系

- **`../features/disagg_prefill.md`(双向 KV 传输)**
  - 在本文档"Bidirectional KV Transfer"小节被显式引用,作为多轮对话场景下 KV cache 在 D 端被 P 复用拉取的背景。
  - 关键差异:该场景下"下一次拉取何时发生"由客户端决定,**心跳续约机制不适用**;文档因此引入独立参数 `decoder_kv_blocks_ttl`(默认 480s)作为固定 timeout,并保留"未来扩展对称心跳"的留白。
  - 时钟偏移问题(`perf_counter` 对齐)是该关联路径带来的工程约束。

- **`../features/nixl_connector_usage.md`(NIXL Connector 使用)**
  - 作为使用侧文档,描述如何在 vLLM 中启用 NIXL KV connector(包括 `do_remote_prefill` / `do_remote_decode` 标记、相关环境变量等)。本文档描述的 lease/心跳机制是其底层的资源回收保障,二者构成"使用层 + 资源管理层"的对应关系。
  - 文档被截断的"Configuration"小节标题前缀为 `kv_connector_extra_con`,推测其指向的正是 `kv_connector_extra_config` 这类在 NIXL connector usage 中会涉及的环境变量/配置项。

### 模块内关键关联点

- **`NixlConnectorScheduler.on_new_request()`**: D 调度器侧的入口钩子,本文档明确要求心跳追踪从这里开始(而非请求被调度执行时),以覆盖"等待队列"这段不可预测长度的延迟。
- **`start_load_kv()`(D 端 worker)**:心跳发送与 KV 拉取的统一入口;同时承担未握手 P 的主动握手触发。
- **`_get_new_notifs()` / `_handle_heartbeat()`(P 端 worker)**:心跳接收与续约的统一入口;以 `"HB:"` 前缀路由心跳消息。
- **`NixlConnectorMetadata.heartbeat_by_engine`**:承载心跳元数据的结构体,由调度器构造、worker 消费。
- **PR #41383**:实现本文档所述机制的代码合并请求。

---

## 【使用方法】

**原文该节被截断**(末尾为:"The lease mechanism is controlled through `kv_connector_extra_con"),完整配置项列表未在所提供的原文片段中给出)。

可从原文已明确涉及到的配置项归纳(均为原文出现过的项):

| 配置项 | 默认值 | 作用 |
|---|---|---|
| `VLLM_NIXL_ABORT_REQUEST_TIMEOUT` | **480s** | 旧机制的单 timeout(本文档标记为问题根源,被新机制替代) |
| `kv_lease_duration` | **30s** | P 端授予每个请求的初始租约时长 |
| 派生:心跳延长 | `lease_duration * 2/3` ≈ **20s** | 每次心跳续约时长(原文表达式) |
| 派生:心跳间隔 | `lease_duration // 6` ≈ **5s** | D 端心跳发送节流(原文表达式) |
| `decoder_kv_blocks_ttl` | **480s** | 双向 KV 传输场景下 D 端 KV 块的固定超时 |

更完整的启用步骤、命令行/环境变量全表、以及是否需要在 vLLM 启动命令中显式开启 lease 模式开关(例如通过 `kv_connector_extra_config` 注入),**原文未涉及**(由截断导致);建议结合 PR #41383 与 `../features/nixl_connector_usage.md` 互补阅读以补全使用细节。
