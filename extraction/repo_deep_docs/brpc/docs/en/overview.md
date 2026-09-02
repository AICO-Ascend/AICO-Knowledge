# What is RPC?

> 仓 `brpc` · 路径 `docs/en/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/brpc/docs/en/overview.md

# brpc `docs/en/overview.md` 一体化深度解读

---

## 【定位】

**一句话**：本篇文档以"为什么需要 RPC"为切入，系统阐释 RPC 抽象所解决的连接复用、服务发现、序列化、负载均衡、容错等问题，并在此基础上介绍 baidu-rpc（即 brpc）作为"工业级 RPC 框架"的能力边界、适用场景与设计哲学（友好 API、可维护性、更好延迟与吞吐），是 brpc 文档体系的**总入口**与全貌导论。

---

## 【技术要点】

以下要点均直接摘自原文，未引入外部信息：

1. **RPC 解决 TCP/IP 之上的四大抽象问题**（原文要点）：
   - 数据格式（字节序、字段增删兼容）→ 由 **protobuf** 负责序列化（HTTP 服务用 **json**）。
   - 连接复用与多请求并发 → 用户透明，但可选 **short / pooled / single** 三种连接类型（`client.md#connection-type`）。
   - 集群寻址 → **Naming Service**，支持 **DNS、ZooKeeper、etcd**，百度内部用 **BNS（Baidu Naming Service）**，brpc 还提供 **list://、file://**。
   - 容错 → **连接断开自动重试**；**超时**则客户端以 timeout error 失败。

2. **负载均衡策略**（原文要点）：
   - 包含 **round-robin（轮询）、randomized（随机）、consistent-hashing（一致性哈希，murmurhash3 或 md5）、locality-aware（局部性感知）**。
   - 对应链接：`../cn/consistent_hashing.md`、`../cn/lalb.md`。

3. **brpc 多协议同端口能力**（原文要点）：
   - restful **http/https、h2/gRPC**（"在 brpc 中用 http/h2 比 libcurl 友好得多"）。
   - **redis、memcached**（线程安全，比官方客户端更友好、更高性能）。
   - **rtmp/flv/hls**（用于构建流媒体服务）。
   - **thrift**（线程安全，比官方更友好、更高性能）。
   - 百度内部协议族：**baidu_std、streaming_rpc、hulu_pbrpc、sofa_pbrpc、nova_pbrpc、public_pbrpc、ubrpc、nshead-based**。
   - 计划开源：**hadoop_rpc、rdma**。

4. **服务端与客户端调用模型**（原文要点）：
   - 服务端：**同步** 或 **异步** 处理请求（`server.md`、`server.md#asynchronous-service`）。
   - 客户端：**同步、异步、半同步**，并可用 **combo channels**（`combo_channel.md`）以声明式简化分片/并行访问。

5. **可观测性与调试**（原文要点）：
   - **HTTP 调试** 服务（`builtin_service.md`），可用浏览器或 curl 查看内部状态。
   - **cpu、heap、contention** 三类 profiler（`../cn/cpu_profiler.md`、`../cn/heap_profiler.md`、`../cn/contention_profiler.md`）。
   - **bvar** 统计指标，可在 `/vars` 页面查看（`bvar.md`、`vars.md`）。

6. **核心 API 仅有 3 个用户头文件**（原文要点）：
   - **Server**（服务端，`server.h`）、**Channel**（客户端，`channel.h`）、**Controller**（参数集，`controller.h`）。
   - Controller **server 与 channel 共用**，其方法按"client-side / server-side / both-side"三类组织。
   - **命名服务调用示例**（原文逐字保留）：
     - BNS：`Init("bns://node-name", ...)`
     - DNS：`Init("http://domain-name", ...)`
     - 本地列表：`Init("file:///home/work/server.list", ...)`

---

## 【关键机制与数据】

### 1. RPC 抽象工作原理（原文流程）

原文描述的 RPC 调用链路：
> "client sends a request to server, wait until server receives -> processes -> responds to the request, then do actions according to the result."

由 brpc 内部机制承担透明动作：
- **序列化/反序列化**：protobuf（通用）/ json（HTTP）。
- **连接管理**：建立、复用、断连重试对用户透明；用户可显式选择 short/pooled/single。
- **寻址**：通过 Naming Service 拿到集群机器列表。
- **负载均衡**：按所选策略从机器列表中选一台。
- **重试**：连接断开时自动重试；超时则失败。

### 2. 性能/规模数据（原文标注）

- **brpc 部署规模**（原文："with 1,000,000+ instances(not counting clients) and thousands kinds of services"）：
  - 部署实例 **1,000,000+（不含 client）**；
  - 服务种类 **数千**；
  - 百度内部代号 **baidu-rpc**，**目前开源的仅 C++ 实现**。
- **可扩展性**：可通过 `new_protocol.md` 快速接入组织内部协议，并可自定义 Naming Service（dns/zk/etcd）与负载均衡器（rr/random/consistent hashing）。

> 原文未给出具体 QPS、延迟 P99 等 benchmark 数字（文档在 "Better latency and throughput" 段被截断，以"To unify co"结尾）。**原文未涉及**具体的 RTT/P99/QPS 数值，本节据实留白，不臆造。

### 3. 使用场景覆盖度（原文表述）

> "Almost all network communications."

但有边界——以下三类"对 RPC 的常见质疑"原文逐条回应：
- **二进制大对象+protobuf 会慢？** 原文："First, this is possibly a wrong feeling … Second, many protocols support carrying binary data along with protobuf requests and bypass the serialization."
- **流式数据不能走 RPC？** 原文列举可处理流式的协议：**ProgressiveReader (http)**、**h2 streams**、**streaming_rpc**、**RTMP**。
- **不需要回复？** 原文建议："Even if you don't need the reply, we recommend sending back small-sized replies … provide valuable clues when debugging complex bugs."

### 4. 可靠性背书（原文表述）

> "brpc is extensively used in Baidu: map-reduce service & table storages; high-performance computing & model training; all sorts of indexing & ranking servers; …. It's been proven."

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

依据文末/文中链接，brpc overview 与以下文档/模块构成体系关系：

| 关联模块 | 关系/作用 |
|---|---|
| `../cn/overview.md` | 中文版 overview，平行姊妹文档 |
| `client.md#connection-type` | 详解 short / pooled / single 三种连接类型的选择 |
| `client.md#naming-service` | 详解 `list://`、`file://` 等命名服务 URI 形式 |
| `../cn/consistent_hashing.md` | 一致性哈希负载均衡（含 murmurhash3/md5）的实现细节 |
| `../cn/lalb.md` | locality-aware（局部性感知）负载均衡 |
| `../cn/cpu_profiler.md` | CPU 热点分析（亦见 `../cn/heap_profiler.md`、`../cn/contention_profiler.md`） |
| `http_client.md#progressively-download` | HTTP 流式下载能力（ProgressiveReader） |
| `streaming_rpc.md` | 流式 RPC 协议与用法 |
| `redis_client.md` | Redis 客户端接入（线程安全、更友好） |
| `memcache_client.md` | Memcached 客户端接入（线程安全、更友好） |

**横向能力关联（原文层面）**：
- **多协议同端口**：overview 罗列协议（http/h2/gRPC、redis、memcached、rtmp/flv/hls、thrift、baidu_std、streaming_rpc、hulu_pbrpc/sofa_pbrpc/nova_pbrpc/public_pbrpc/ubrpc、nshead），它们各自对应独立的 client/server 文档。
- **分布式高可用**：overview 提到通过 `braft`（基于 RAFT 共识）构建 HA 服务，但 braft 是独立仓库，brpc 仅提供工业级集成。
- **可观测性三件套**：HTTP builtin_service + cpu/heap/contention profiler + bvar（在 `/vars` 查看），构成完整的"线上诊断—性能分析—指标导出"链路。
- **扩展点**：`new_protocol.md` 提供自定义协议入口，`../cn/load_balancing.md#命名服务` 与 `../cn/load_balancing.md#负载均衡` 暴露命名服务/负载均衡的自定义接口。

---

## 【使用方法】

> 注：本文为 overview，未展开配置/命令细节；以下"启用方式"仅整理**原文正文出现**的入口或调用形态，不引入原文未涉及的配置项。

### 1. 启用 brpc 三大用户头文件（原文逐字示例）

- **构建服务（服务端）**：
  > "include `brpc/server.h` and follow the comments or `examples`."
- **访问服务（客户端）**：
  > "include `brpc/channel.h` and follow the comments or `examples`."
- **调整参数**：
  > "Checkout `brpc/controller.h`. Note that the class is shared by server and channel. Methods are separated into 3 parts: client-side, server-side and both-side."

### 2. 命名服务 URI 写法（原文逐字保留）

```
Init("bns://node-name", ...)
Init("http://domain-name", ...)
Init("file:///home/work/server.list", ...)
```

含义分别为 **BNS、DNS、本地机器列表**。

### 3. 客户端连接类型选择（原文给出的选项名）

- **short**
- **pooled**
- **single**

详细语义见 `client.md#connection-type`。

### 4. 客户端调用模式（原文给出的选项名）

- **synchronous**（`client.md#synchronus-call`）
- **asynchronous**（`client.md#asynchronous-call`）
- **semi-synchronous**（`client.md#semi-synchronous-call`）
- **combo channels**（`combo_channel.md`）

### 5. 服务端处理模式（原文给出的选项名）

- **synchronous**（`server.md`）
- **asynchronous**（`server.md#asynchronous-service`）

### 6. 调试与统计入口（原文给出的入口路径）

- HTTP 调试：`builtin_service.md`
- Profiler：`../cn/cpu_profiler.md`、`../cn/heap_profiler.md`、`../cn/contention_profiler.md`
- 指标：`bvar.md`，HTTP 路径 `/vars`（`vars.md`）

### 7. 协议/特性启用

原文以**"you can use it to"** + 项目符号形式罗列，未给出配置文件或编译开关。具体启用方式需进入各协议对应专题文档（`http_client.md`、`redis_client.md`、`streaming_rpc.md` 等），**原文未涉及**统一配置项/编译开关说明。

## 图文联合解读

- `rpc.png`: **图文联合解读：**

1）**图示内容**：两个圆圈代表 SERVER 与 CLIENT，分别由两条方向相反的箭头连接——上方"requests"由 CLIENT 发往 SERVER，下方"responses"由 SERVER 返回 CLIENT，构成最简请求-响应循环。

2）**技术结论**：将网络通信抽象为"客户端调用服务端函数"，即一次 RPC 包含单向请求与单向响应两个阶段，通信双方角色明确、流程对称。

3）**与文档论点关系**：呼应文档核心观点——RPC 把 TCP/IP 字节传输封装为函数调用语义，使开发者只需关心"发请求、等响应"，无需处理字节序、连接复用、断连重试等底层问题，从而简化分布式服务构建。
- `logo.png`: ⚠️ **图片与文档不匹配**

您提供的图片实际上是 **brpc 项目的 Logo**（顶部是三个蓝色节点连成的网络拓扑示意，下方是 "bRPC" 字样和 "better" 标语），而非文档所引用的 `figures/rpc.png`。

根据文档上下文，真正的配图 `rpc.png` 应展示的是 **RPC 客户端—服务器通信流程**，通常包含：

1. **结构内容**：
   - Client 端调用本地 stub/proxy
   - 通过网络（TCP）发送 Request（protobuf 序列化）
   - Server 端 stub 反序列化并调用实际函数
   - Result 经序列化回传 Client

2. **论证的技术结论**：
   - RPC 把"网络通信"抽象成"调用远端函数"
   - 解决了文档列出的字节序、版本兼容、连接复用、集群寻址、故障重试等问题

3. **与文档论点关系**：
   - 是文字"RPC abstracts network communications as clients accessing functions on servers"的**可视化佐证**。

📎 **建议**：请重新上传 `brpc/docs/images/figures/rpc.png`（在 GitHub 仓库路径 `docs/figures/rpc.png` 下），我可以基于真实配图做精准解读。
