# 什么是RPC?

> 仓 `brpc` · 路径 `docs/cn/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/brpc/docs/cn/overview.md

# 「docs/cn/overview.md」深度解读

## 【定位】

本篇是 brpc 项目的总纲性 overview 文档,采用"由抽象到具象"的双层结构:先向读者普及 RPC 概念并回应"RPC 是否万能"的常见质疑,再落到 brpc 自身的协议覆盖、接口设计、可靠性与性能优势,目标是让读者在最短时间内建立"为什么需要 RPC / 为什么选 brpc"的整体认知,并通过文末内链索引到具体子模块深入学习。

## 【技术要点】

1. **序列化方案**:数据通过 [protobuf](https://github.com/google/protobuf) 序列化(前后兼容),request/response 均为 `protobuf::Message` 类型;HTTP 场景使用 [json](http://www.json.org/);另支持二进制旁路以绕开序列化开销。
2. **三种连接方式**(链接到 `client.md#连接方式`):短连接、连接池、单连接,用户无需关心底层 socket 细节。
3. **命名服务与负载均衡**(链接到 `client.md#命名服务`、`consistent_hashing.md`、`lalb.md`):支持 DNS / ZooKeeper / etcd / BNS(百度内),以及 brpc 自有的 `"list://"` 与 `"file://"`;负载均衡算法包括 round-robin、randomized、[consistent-hashing](consistent_hashing.md)(murmurhash3 或 md5)、[locality-aware](lalb.md)。
4. **可靠性机制**:连接断开可重试;server 未在给定时间内回复时,client 返回超时错误。
5. **三大用户类**(`brpc/server.h`、`brpc/channel.h`、`brpc/controller.h`):Server(服务端)、Channel(客户端)、Controller(参数集合,Client-side / Server-side / Both-side 三段标记),无需记忆 "XXXManager / XXXContext" 等组合关系。
6. **多协议单端口**:同一 Server 可同时承载 restful http/https、h2/gRPC、redis、memcached、rtmp/flv/hls、hadoop_rpc、rdma、thrift、baidu_std、streaming_rpc、hulu_pbrpc、sofa_pbrpc、nova_pbrpc、public_pbrpc、ubrpc 以及 nshead 系列协议;通过 braft 实现基于工业级 RAFT 算法的高可用。
7. **流式与异步模型**:支持同步/异步 Server、同步/异步/半同步 Client,以及组合 channels(combo_channel)简化分库/并发访问;流式场景覆盖 `http://ProgressiveReader`(`http_client.md#持续下载`)、h2 streams、[streaming_rpc](streaming_rpc.md)、RTMP。
8. **运行期可观测性**:内置 HTTP 调试界面,集成 cpu / heap / contention profiler,以及通过 [bvar](bvar.md) + `/vars` 查看运行时指标。
9. **高性能 IO 模型**(无 IO/处理线程之分):对不同 fd 的读取完全并发;对同一 fd 中不同消息的解析并发;多线程对同一 fd 写出采用 [wait-free](http://en.wikipedia.org/wiki/Non-blocking_algorithm#Wait-freedom) 委托。
10. **线程自适应**:每个请求运行在新建的 [bthread](bthread.md) 中,请求结束线程即结束,线程数天然随负载伸缩。

## 【关键机制与数据】

- **RPC 工作原理(原文图示与文字说明)**:client 向 server 发送 request 后阻塞等待,server 接收、处理、回复,client 恢复并基于 response 反应 —— 类比为"client 访问 server 上的函数"。
- **生产规模(原文)**:"百度内最常使用的工业级RPC框架, 有 **1,000,000+ 个实例(不包含client)** 和上千种服务, 在百度内叫做 baidu-rpc"。
- **百度内应用面(原文)**:map-reduce 服务、table 存储、高性能计算、模型训练、各种索引和排序服务。
- **并发能力(原文)**:"多个线程在高度竞争下仍可以在 **1 秒内对同一个 fd 写入 500 万个 16 字节的消息**"。
- **QPS 容忍度(原文)**:"即使服务的 QPS 超过 **50 万**, 用户也很少在 contention profiler 中看到框架造成的锁竞争"。
- **可用性指标(原文提到但为对比背景)**:"工业级在线检索要求 **99.99% 以上**的可用性",brpc 通过避免"IO 线程 fd 散列"导致的同线程阻塞来实现此目标。
- **典型 URI 写法(原文示例)**:BNS 用 `"bns://node-name"`,DNS 用 `"http://domain-name"`,本地文件列表用 `"file:///home/work/server.list"`。
- **写冲突处理流程(原文)**:"当多个线程都要对一个 fd 写出时(常见于单连接), 第一个线程会直接在原线程写出, 其他线程会以 wait-free 的方式托付自己的写请求"。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

本文作为 overview,通过文末密集的内链将"概念 → 模块文档"建立索引关系,核心上下游依赖如下:

- **协议扩展链**:概述中提到的每个协议/能力均指向独立文档 —— `redis_client.md`(redis 支持)、`memcache_client.md`(memcached 支持)、`http_client.md#持续下载`(HTTP 流式 ProgressiveReader)、`streaming_rpc.md`(流式 RPC,百度内标准与通用流式)、`thrift.md`(thrift 协议)、`baidu_std.md`(百度内协议),以及 `new_protocol.md`(把组织自有协议接入 brpc)。
- **客户端相关**:`client.md#连接方式`(短连接/连接池/单连接)、`client.md#同步访问` / `client.md#异步访问` / `client.md#半同步`、`combo_channel.md`(组合 channels)、`load_balancing.md#命名服务` 与 `load_balancing.md#负载均衡`(对应文中 dns/zk/etcd 与 rr/random/consistent hashing)。
- **一致性哈希与局部性**:`consistent_hashing.md` 对应 consistent-hashing(murmurhash3/md5),`lalb.md` 对应 locality-aware 负载均衡。
- **服务端与高可用**:`server.md`(同步)、`server.md#异步service`;高可用通过外部项目 [braft](https://github.com/brpc/braft) 提供,本文给出跳转。
- **可观测性**:`builtin_service.md`(HTTP 调试界面)、`cpu_profiler.md`、`heap_profiler.md`、`contention_profiler.md`、`bvar.md` 与 `/vars`(`vars.md`)。
- **底层支撑**:`io.md#收消息` 与 `io.md#发消息`(详细解释为何 fd 间读取/写出并发以及 wait-free 写)、`bthread.md` / `memory_management.md` / `timer_keeping.md` / `bthread_id.md`(锁竞争与并发基础设施)。
- **英文版本对照**:文首 `[English version](../en/overview.md)` 给出与英文总览的对应入口。

## 【使用方法】

原文未涉及具体启用步骤、配置项或命令行,仅以"使用示例"形式给出工程级别的接入路径(可视为"使用方法"的入口):

- **建服务**(原文):包含 `brpc/server.h`,参考注释或 `example/echo_c++/server.cpp`。
- **访问服务**(原文):包含 `brpc/channel.h`,参考注释或 `example/echo_c++/client.cpp`。
- **调整参数**(原文):查阅 `brpc/controller.h`,注意该类被 Server 与 Channel 共用,内部按 `Client-side` / `Server-side` / `Both-side methods` 三段标注。
- **命名服务 URI**(原文示例,等同于配置入口):
  - BNS:`bns://node-name`
  - DNS:`http://domain-name`
  - 本地文件列表:`file:///home/work/server.list`
- **运行时调试**(原文):通过浏览器或 curl 访问 server 内置 HTTP 调试界面(`builtin_service.md`),并启用 cpu / heap / contention profiler 与 `bvar` + `/vars`。

> 注:具体的启动参数(如 `-log_dir`、`-bthread_concurrency`、`-max_concurrency`)、超时/重试字段(`Controller::set_timeout_ms`、`set_max_retry`)等配置项均位于 `client.md` / `server.md` / `brpc/controller.h` 子文档,本文 overview 不展开。

## 图文联合解读

- `rpc.png`: **图文联合解读：**

1) 图中画了两个圆圈"SERVER"和"CLIENT"，中间有两条带方向箭头："requests"从客户端指向服务端，"responses"从服务端指回客户端，形成一次请求-应答闭环。

2) 论证的技术结论：RPC的本质是**请求/响应模式的同步调用**——客户端发送请求后阻塞等待，服务端处理后返回结果，网络交互被抽象为函数调用。

3) 与文档的关系：该图直观呈现了文中"client向server发送request后开始等待，直到server回复"的抽象比喻，回应了开篇提出的TCP/IP原生交互未解决的序列化、多路复用、命名、容错等问题——RPC把它们封装成一次"函数调用"，使图中简单的双向箭头背后能承载复杂的分布式逻辑。
- `logo.png`: 需要指出的是，这张图实际上**并非 RPC 交互示意图，而是 brpc 项目的 logo**：

**图中内容**
- 顶部：4 个蓝色圆点用直线连接，呈折线/网络拓扑状，象征"多节点互联"。
- 中部："brpc" 字样，灰色"b" + 黑色"RPC"。
- 底部：斜体小字 "etter"（与上方 "b" 组合成 "better"），为项目口号。

**与文档论点关系**
文档原本引用的是 `figures/rpc.png`（应为 client→server 双向箭头的 RPC 调用流程图），但当前嵌入的却是品牌 logo，因此**无法承担"展示 RPC 数据流"的论证职能**。

**结论**
该图未呈现任何序列化、请求/响应、连接复用等技术信息，无法与"RPC 解决序列化、连接管理、超时重试"等段落形成图文互证。建议核实文档配图路径，确认是否误将 logo 上传。
