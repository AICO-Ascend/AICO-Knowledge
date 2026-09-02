# NIXL push-mode KV transfer

> 仓 `vllm` · 路径 `docs/design/nixl_kv_push_connector.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/nixl_kv_push_connector.md

# NIXL push-mode KV transfer 设计文档深度解读

---

## 【定位】

本文档描述 vLLM 中 **NIXL 推送式 KV 传输连接器** (`NixlPushConnector`) 的线程模型、消息队列与调度交互机制——它作为默认 pull-based NIXL 连接器的替代方案，由 prefill (P) 端通过 `NIXL WRITE` 将 KV 块直接写入 decode (D) 端预先分配好的显存, 而非 D 端通过 `NIXL READ` 反向拉取。

---

## 【技术要点】

1. **模式对比**: 默认 NIXL 连接器为 **pull-based**(D 通过 `NIXL READ` 在 prefill 完成后拉取 KV);`NixlPushConnector` 提供 **push-based** 替代方案(P 通过 `NIXL WRITE` 直接写入 D 预先分配的内存)。pull-mode 整体设计不变,push 连接器在握手、NIXL agent 初始化和元数据路径上尽量复用。

2. **每 rank 一个 writer 线程**: `NixlPushConnectorWorker` 为每个 worker (即每个 TP rank) 引入一个名为 `nixl-push-writer` 的专用后台线程。该线程独占地执行 push 专属 NIXL 操作:`nixl_wrapper.get_new_notifs()` 接收通知;`nixl_wrapper.send_notif(...)` 发送 `PUSH_REG:<msgpack>` (D 侧) 与 per-WRITE 完成通知 (P 侧);`nixl_wrapper.make_prepped_xfer(...) / transfer(...)` 提交 WRITE 本身。**心跳仍由引擎主线程**通过 base-worker 中已有的 `_send_heartbeats` 通路在 `start_load_kv` 内发出。

3. **三路唤醒 + 1 ms 自轮询**: writer 线程空闲时阻塞于 `threading.Event` `_push_writer_wake`,由三个调用方唤醒 ——
   - (a) **新传输唤醒**:`start_load_kv` (worker 主线程, 每个 engine step 一次),仅当 `meta.push_registrations` 或 `meta.push_finished_blocks` 非空时设置事件;
   - (b) **排空通知唤醒**:`get_finished` (worker 主线程, 每个 engine step 一次),总设置事件,以便 drain 入站通知(心跳、WRITE 完成通知、迟到的 `PUSH_REG`);
   - (c) **握手回调唤醒**: D→P 握手(发 `PUSH_REG` 前)和 P→D 握手(WWRITE 前)都在后台 handshake executor 上运行,其 done-callback 将延迟操作重新入队并设置事件;第二次执行时 `_ensure_handshake` 返回 `None`,此时 writer 直接发送 `PUSH_REG`/发起 WRITE;**握手失败则 fail/drop 请求,不重试**(见 Failure handling)。
   - **额外自轮询**:`_PUSH_WRITER_POLL_INTERVAL_MS = 1.0` ms,在有 P 侧 finished blocks 等待匹配 `PUSH_REG` 时持续自轮询。

4. **双向匹配表**: writer 持有两张表:
   - `_pending_d_registrations`: 来自远端 D 的注册,等待 P 的 blocks;
   - `_push_finished_blocks`: 由 P 调度器 stage,等待远端 D 的注册。
   任意一侧都可能先到;writer 在两个方向上都做匹配。

5. **request_id 匹配带 fallback**: 优先按精确 `request_id` 查找,然后 fallback 到调用 `get_base_request_id` 去掉尾部每 engine 随机化后缀(8-hex)后再比较。该 fallback 是因为 Proxy 给两腿下发相同的 `X-Request-Id`,P 与 D 分别把它包装成相同的 `cmpl-<uuid>-<index>` 形式,仅末尾 8-hex 随机化后缀不同 —— 该逻辑在 `VLLM_DISABLE_REQUEST_ID_RANDOMIZATION` 是否设置的情况下都成立(该环境变量在 upstream 计划移除)。

6. **Wire format (`PUSH_REG:<msgpack-encoded dict>`) 与 logical→physical 展开**: Push 注册以 `PUSH_REG:<msgpack-encoded dict>` NIXL notification 形式发送,**D 发送 logical block ids**,P 在 WRITE-submission 时利用 NIXL 握手中学到的 `remote_physical_blocks_per_logical` 比值将其展开为物理 block ids —— 这与 pull-mode 契约一致(调度器发 logical id,worker 在提交时展开为 physical)。

---

## 【关键机制与数据】

### 数据流 / 工作原理(原文 mermaid 序列图还原)

> **原文**: 以 mermaid `sequenceDiagram` 形式给出完整时序,核心阶段如下:

1. **请求派发(Proxy)**——Client → Proxy 发 `POST /v1/completions` → Proxy 同时派发:
   - 预填腿给 P 调度器:`do_remote_decode=True, max_tokens=1`;
   - 解码腿给 D 调度器:`do_remote_prefill=True, P coordinates`。

2. **D 侧注册(原文: `note over DSched,DWriter: D side - register blocks with P`)**
   - `DSched: update_state_after_alloc, stash registration, arm watchdog`;
   - `DSched → DWorker: build_connector_meta → meta.push_registrations`;
   - `DWorker → DWriter: enqueue (req_id, reg_data) on _reg_send_inbox`;
   - `DWriter → PWriter: NIXL send_notif PUSH_REG msgpack`。

3. **P 侧 prefill 与 stage(原文: `note over PSched,PWriter: P side - prefill, stage finished blocks`)**
   - `PSched: request_finished, stash blocks`;
   - `PSched → PWorker: build_connector_meta → meta.push_finished_blocks`;
   - `PWorker → PWriter: enqueue (req_id, blocks) on _finished_blocks_inbox`。

4. **P 侧匹配并发起 WRITE(原文: `note over PWriter: P writer matches and WRITEs`)**
   - `get_new_notifs` 返回 `PUSH_REG`,通过 `_handle_push_reg_notif` 路由;
   - 当 `PUSH_REG` 与 finished blocks 同时存在:`pop matching pair, fire WRITE`;
   - 仅单边存在:`stash and wait, self-poll only when blocks unmatched`;
   - `_ensure_handshake` to D(异步;**延迟 WRITE**);
   - handshake callback 将操作重新入队到 `_deferred_push_inbox` 并 wake;
   - `NIXL WRITE direct to D GPU + completion notif`。

5. **D 侧完成记账(原文: `note over DWorker,DWriter: D side - completion accounting`)**
   - `DWriter → DWorker: forward HB and completion notifs via _pending_completion_notifs`;
   - `DWorker: _get_new_notifs drains, HB extends lease, completion marks recv done`;
   - `DWorker → DSched: update_connector_output(finished_recving)`;
   - `DSched: clear watchdog deadline`。

6. **P 侧回收(原文: `note over PWorker,PWriter: P side - reclaim`)**
   - `PWorker: get_finished, drain _sending_transfers, queue eviction`;
   - `PWriter: drain _evict_finished_inbox, drop stale state`;
   - `PWorker → PSched: update_connector_output(finished_sending)`;
   - `PSched: free lease`。
   
   流式回包:`DWorker → Proxy: stream decode tokens` → `Proxy → Client: response`。

### 关键性能/计时数字(原文给出者)
- `_PUSH_WRITER_POLL_INTERVAL_MS = 1.0` ms —— P 侧有 finished blocks 但尚未匹配到 `PUSH_REG` 时,writer 自轮询间隔。
- 8-hex per-engine request id 随机化后缀 —— `get_base_request_id` 仅剥离该后缀以归一化两侧 id,同时保留 completion index 以区分多 prompt 子请求。
- proxy 给两腿下发同一 `X-Request-Id` —— 这是 fallback 匹配的根因。
- 完成索引前缀 `cmpl-<uuid>-<index>` —— P 与 D 两端包装格式相同,只是末尾随机化后缀不同。

### 失败处理(原文: `If a handshake *failed*, the callback fails or drops the request instead of re-enqueuing, so there is no retry loop`)
握手**失败**时,callback 直接 fail/drop 请求,**不再入队** —— 主动避免了重试循环。

> 备注:原文在"The completion notif"处被截断,**完成通知的具体 wire 格式与字段表**未给出,后续小节不可读。

---

## 【表格解读】

### 表 1: Writer-local matching tables(逐字还原)

| Table                          | Owner            | Holds                                                                  |
|--------------------------------|------------------|------------------------------------------------------------------------|
| `_pending_d_registrations`     | writer           | D registrations received from a remote D, waiting for P's blocks       |
| `_push_finished_blocks`        | writer           | P blocks staged by the scheduler, waiting for a remote D registration  |

**逐行解读**:
- `_pending_d_registrations` —— 由 writer 独占持有,语义为"来自远端 D 端的注册尚在等待 P 端 blocks 出现"。这一侧由 PUSH_REG 通知到达触发填充。
- `_push_finished_blocks` —— 由 writer 独占持有,语义为"P 端调度器已 stage、但尚未收到远端 D 注册的 KV blocks 列表"。这一侧由 P 调度器在 `request_finished` 时填充。

二者构成 push 模式的核心匹配空间 —— **无论 PUSH_REG 与 finished blocks 哪个先到**,writer 都能在两个方向上做 lookup,并在双方都到齐时 pop pair 触发 WRITE。该匹配的存在意味着 push 模式不依赖严格的端到端时序,降低了 stall 概率。

### 表 2: Wire format 字段(逐字还原)

| Field                | Set by | Meaning                                                                |
|----------------------|--------|------------------------------------------------------------------------|
| ``request_id``       | D      | D's own vLLM request id; P's match key, echoed in the completion notif |
| ``decode_engine_id`` | D      | D's engine id (P uses this for the reverse handshake)                  |
| ``decode_host``      | D      | D's NIXL side-channel host                                             |
| ``decode_port``      | D      | D's NIXL side-channel port                                             |
| ``decode_tp_size``   | D      | D's tensor-parallel size                                               |
| ``local_block_ids``  | D      | per-group lists of D's *logical* block ids (preallocated)              |
| ``remote_engine_id`` | D      | P's engine id (for the existing P-side handshake)                      |
| ``remote_host``      | D      | P's NIXL side-channel host                                             |
| ``remote_port``      | D      | P's NIXL side-channel port                                             |
| ``remote_tp_size``   | D      | P's tensor-parallel size                                               |

**逐行解读**:
- 所有字段均由 **D 端** 设置(`Set by: D`),意味着 PUSH_REG 是 D→P 方向推送。
- `request_id` —— 双身份字段:在 PUSH_REG 内是 P 的**匹配键**;在 WRITE 完成通知中以"echoed"形式回送,供 D 侧把收到的完成事件与请求 ID 关联起来。
- `decode_engine_id` / `decode_host` / `decode_port` / `decode_tp_size` —— 把 D 端的 NIXL 寻址信息告诉 P,**用于 P→D 反向握手**(因为 P 后续要把 WRITE 直接打到 D GPU)。
- `local_block_ids` —— D 已经预先分配的 **logical** block ids(按 group 组织的 per-group 列表)。**关键设计**:此处不发物理 block ids。
- `remote_engine_id` / `remote_host` / `remote_port` / `remote_tp_size` —— 把 P 端信息告诉 D,沿用现成的 **P-side handshake**(d 端主动握手到 P,而非 P 来握手 D,因为 WRITE 数据面与反向握手复用 P 端已经具备的 side-channel)。

**关键设计意图(原文)**:"D ships **logical** block ids; P expands them to physical block ids at WRITE-submission time using the ratio learned during the NIXL handshake (`remote_physical_blocks_per_logical`). This matches the pull-mode contract — schedulers ship logical ids, workers expand to physical at submission." —— 即 push 与 pull 模式共享同一 logical→physical 展开语义,只在 worker 层做,使得调度器代码无需感知模式差异。

---

## 【公式解读】

原文未给出 LaTeX 数学公式或伪代码公式。**原文无公式**。

可视为"公式"的隐含表达式为逻辑块到物理块的展开比(以伪代码 `remote_physical_blocks_per_logical` 表示),但原文未给出具体形式,仅作为 NIXL 握手阶段学到的比值供"WRITE-submission 时展开"使用 —— 无完整表达式,故不单独罗列。

---

## 【关联】

本文档与以下特性/模块存在显式或隐式关联:

- **Pull-mode NIXL connector (默认行为)** —— 文档明确指出 pull 设计不变,push 连接器在握手、NIXL agent 设置和元数据路径上"尽量复用"。push 与 pull 共用:
  - `NIXL agent setup`;
  - `handshake` 通路;
  - `metadata path`;
  - logical→physical 展开契约(`remote_physical_blocks_per_logical`)。
  
- **Proxy 层** —— 负责 `X-Request-Id` 在 prefill 与 decode 两腿的同下发,这是 PUSH_REG ↔ finished blocks 跨进程匹配的前提;Proxy 还用 `do_remote_decode=True, max_tokens=1` 与 `do_remote_prefill=True` 协调两腿语义。

- **D/P Scheduler 与 Worker 分层** —— 调度器负责 `update_state_after_alloc`、`request_finished`、`update_connector_output(finished_recving/sending)`;Worker 负责 `build_connector_meta → meta.push_registrations / meta.push_finished_blocks`,以及 `_send_heartbeats`、`_get_new_notifs`、`get_finished`。

- **NIXL agent 三类操作(集中于 writer 线程)**:
  - `nixl_wrapper.get_new_notifs()`;
  - `nixl_wrapper.send_notif(...)`;
  - `nixl_wrapper.make_prepped_xfer(...) / transfer(...)`。

- **基类 Worker 通路** —— 心跳发送复用 base-worker 的 `_send_heartbeats` (写在 `start_load_kv` 内),不开新线程。

- **环境变量 `VLLM_DISABLE_REQUEST_ID_RANDOMIZATION`** —— 文档明确指出 **"slated for removal upstream"**(upstream 计划移除),因此 request_id fallback 匹配(剥离 8-hex 后缀)在两种配置下都必须正确,显示出对未来去随机化迁移的前瞻性。

- **`input_processor.assign_request_id`** —— 是 per-engine 8-hex 随机化后缀的注入点。

- **6 个 Writer 内部队列/Inbox**(分散命名,无独立链接,但相互耦合):
  - `_reg_send_inbox` (D);
  - `_finished_blocks_inbox` (P);
  - `_deferred_push_inbox` (P,握手后回填);
  - `_evict_finished_inbox` (P 回收);
  - `_pending_completion_notifs` (D);
  - `_sending_transfers` (P)。
  
  以及两张表 `_pending_d_registrations` / `_push_finished_blocks`,加 1 个 Event `_push_writer_wake`。

> 内部链接:(无)。

---

## 【使用方法】

> **原文未涉及完整启用方式与配置项**。文档是纯设计文档,未给出 `--connector` 选择器、API 参数或 CLI flag。

可从原文提取的"使用"层信息(纯命名层面)如下,均以原始措辞为准:

- **连接器类名**: `NixlPushConnector`(默认 NIXL connector 之外的可选项)。
- **Worker 类名**: `NixlPushConnectorWorker` —— 引入专用后台线程 `nixl-push-writer`(每 worker / 每 TP rank)。
- **Wire 格式**:`PUSH_REG:<msgpack-encoded dict>`(NIXL notification)。
- **关键常量**:`_PUSH_WRITER_POLL_INTERVAL_MS = 1.0` ms(自轮询间隔)。
- **关键 Event / Inbox / 表(代码命名口径)**:
  - 唤醒事件:`_push_writer_wake`;
  - 入站队列:`_reg_send_inbox`、`_finished_blocks_inbox`、`_deferred_push_inbox`、`_evict_finished_inbox`;
  - 匹配表:`_pending_d_registrations`、`_push_finished_blocks`。
- **握手方向**:D→P(发 `PUSH_REG` 之前)、P→D(WWRITE 之前);握手均在后台 executor 上异步完成,失败时 **fail/drop,不重试**。
- **逻辑块 vs 物理块**:`local_block_ids` 发送 logical;P 端在 WRITE submission 时用 `remote_physical_blocks_per_logical` 比例扩成 physical。
- **环境变量**:无新增。沿用(且兼容被计划移除的)`VLLM_DISABLE_REQUEST_ID_RANDOMIZATION`。

原文段落"The completion notif"被截断 —— 完成通知的 wire format 字段、具体的 `update_connector_output` 参数契约、以及启用 `NixlPushConnector` 的具体配置入口(如某个 env var、API 参数或 engine arg)在原文范围内**未给出**,故不臆造。
