# KV Cache池化使用指导

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/mempool.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/mempool.md

# KV Cache池化使用指导 — 一体化深度解读

## 【定位】

这篇文档解决如何在 MindIE 推理引擎中开启并使用 KV Cache 池化特性，通过将 Prefix Cache 由仅依赖片上显存扩展到更大容量的外部存储介质，突破单卡 HBM 容量上限，从而提高 Prefix Cache 命中率并降低大模型推理成本。

---

## 【技术要点】

1. **存储层级扩展机制**：在 Prefix Cache 仅能使用片上显存的基础上，通过 KV Cache 池化将更大容量的存储介质纳入前缀缓存池，以扩容缓存容量。
2. **启用前置依赖**：KV Cache 池化特性必须依赖于 Prefix Cache 特性，仅当 Prefix Cache 已开启且正确配置 `kvPoolConfig` 字段后，KV Cache 池化才会生效。
3. **配置入口与字段**：在 MindIE 的 `config.json` 中 `BackendConfig` 部分，通过 `kvPoolConfig` 配置池化后端；核心字段为 `backend`（指定池化后端）、`configPath`（后端配置文件路径）、`asyncWrite`（是否开启异步写，默认 `false`/同步写）。
4. **已支持后端：Mooncake（Ascend Direct Transport）**：通过 `cmake -DUSE_ASCEND_DIRECT=ON -DBUILD_SHARED_LIBS=ON -DBUILD_UNIT_TESTS=OFF` 编译选项启用 NPU 亲和传输；编译后需将 `libmooncake_common.so`、`libtransfer_engine.so`、`libmooncake_store.so` 拷贝至 `mooncake` Python 安装路径；并强制要求容器内存在 `/etc/hccn.conf`。
5. **Mooncake Master 启动参数**：`eviction_high_watermark_ratio=0.8`、`eviction_ratio=0.05`、`rpc_thread_num=128`；其中 `rpc_thread_num` 建议调高以处理高并发。
6. **模型与特性叠加约束**：`asyncWrite=true` 仅在 Qwen 稠密（非 MoE）与 DeepSeek（V3/V3.1/R1）上经过验证；可叠加特性按模型分组列出；已确定不支持 SplitFuse、Micro Batch、Multi-Lora 三种特性的任意组合。

---

## 【关键机制与数据】

**工作原理（原文）：** Pooling 以 Prefix Cache 机制为基础，将 KV Cache 数据除了保存在片上显存外，再下沉到由 `backend` 指定的外部存储介质，构成多级缓存池；其容量上限不再受单卡 HBM 限制。

**数据流（原文）：**

- `kvPoolConfig.backend` → 选择池化后端（已支持：`mooncake`）
- `kvPoolConfig.configPath` → 指向后端专属 JSON 配置（如 `mooncake.json`）
- 客户端/服务端连接：`master_server_address: master_server_ip:50051`，`mooncake_master` 通过 `--port 12345` 启动
- 写入策略：`asyncWrite` 字段在 `false`（默认）时为同步写，在 `true` 时为异步写

**关键配置数据（原文）：**

- `global_segment_size = 268435456`（约 256 MiB，由 Mooncake client 配置 `mooncake.json` 给出）
- `protocol = "ascend"`、`metadata_server = "P2PHANDSHAKE"`、`use_ascend_direct = true`
- 环境变量 `ASCEND_BUFFER_POOL=4:8`（在终端2拉起 MindIE 服务时设置）
- `LD_LIBRARY_PATH` 追加 `: /usr/local/lib/python3.11/site-packages/mooncake`
- 可选 `LD_PRELOAD="path_to_file/libjemalloc.so:$LD_PRELOAD"`（建议在池化场景开启以优化内存）

**性能/容量结论性陈述（原文）：** "突破片上内存的容量限制" / "有效提升 Prefix Cache 的命中率，显著降低大模型推理的成本"（原文未给出具体的命中率提升数字或延时数据）。

---

## 【表格解读】

**原文无表格**。原文通过 JSON 配置片段、shell 命令列表和分级条目表达配置/命令信息，未使用表格形式呈现。

---

## 【公式解读】

**原文无公式**。原文未涉及任何数学公式或伪代码表达式。

---

## 【关联】

按照原文显式提及与其他特性的依赖与叠加关系：

| 关联对象 | 关系类型 | 原文描述 |
|---|---|---|
| Prefix Cache | 强依赖 | "KV Cache 池化特性依赖于 Prefix Cache 特性" |
| 异步调度 | 可叠加（仅 Qwen 稠密） | 当异步写特性开启时可与异步调度组合 |
| 异步推理 | 可叠加（仅 DeepSeek V3/V3.1/R1） | 当异步写开启时可与异步推理组合 |
| Context Parallel | 可叠加（仅 DeepSeek） | 与异步写组合时支持 |
| Sequence Parallel | 可叠加（仅 DeepSeek） | 与异步写组合时支持 |
| Function Call / 思考解析 / Yarn | 可叠加（仅 Qwen 稠密） | 与异步写组合时支持 |
| SplitFuse | 不兼容 | 已确定不支持与异步写叠加 |
| Micro Batch | 不兼容 | 已确定不支持与异步写叠加 |
| Multi-Lora | 不兼容 | 已确定不支持与异步写叠加 |
| Mooncake（kvcache-ai/Mooncake） | 外部后端 | 通过 `USE_ASCEND_DIRECT=ON` 编译选项接入；`hccn.conf`、Ascend Direct Transport、Pluggable Caching Engine 等为其能力来源 |
| 宿主机 `/etc/hccn.conf` | 部署前置 | Mooncake Ascend Direct Transport 强制要求 |

原文未提供指向其他文档章节的内部链接（仅文档内锚点 `#使用介绍`、`#二准备mooncake-client配置文件`，用于本篇内跳转）。

---

## 【使用方法】

**1. 配置文件改动**（原文）：

```json
"kvPoolConfig" : {"backend":"", "configPath":""}
```

或含异步写：

```json
"kvPoolConfig" : {"backend":"", "configPath":"", "asyncWrite": true}
```

启用条件：在 Prefix Cache 已开启的前提下，并设置非空 `backend` 与 `configPath`。

**2. Mooncake 后端安装（原文摘录）**：

```shell
git clone https://github.com/kvcache-ai/Mooncake.git
cd Mooncake && mkdir build && cd build
cmake -DUSE_ASCEND_DIRECT=ON -DBUILD_SHARED_LIBS=ON -DBUILD_UNIT_TESTS=OFF ..
make -j && make install
```

编译产物拷贝、容器内 `hccn.conf` 拷贝、以及验证命令（`mooncake_master --port 12345`）均按原文 Step2–Step4 执行。

**3. MoonCake client 配置文件**（原文 JSON 字段已逐字保留如下）：

| 字段 | 值 |
|---|---|
| `local_hostname` | `"localhost"` |
| `metadata_server` | `"P2PHANDSHAKE"` |
| `global_segment_size` | `268435456` |
| `protocol` | `"ascend"` |
| `device_name` | `""` |
| `master_server_address` | `"master_server_ip:50051"` |
| `use_ascend_direct` | `true` |

**4. 服务拉起顺序（原文）**：

```bash
# 终端1：Master
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/python3.11/site-packages/mooncake
mooncake_master --port 12345 --eviction_high_watermark_ratio 0.8 --eviction_ratio 0.05 --rpc_thread_num 128

# 终端2：MindIE 服务
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/python3.11/site-packages/mooncake
export ASCEND_BUFFER_POOL=4:8
export LD_PRELOAD="path_to_file/libjemalloc.so:$LD_PRELOAD"   # 可选, 池化场景建议开启
```

**5. 未涉及内容**：

- 原文未提供 MindIE 端 `config.json` 中 `Prefix Cache` 相关的具体字段名与字段值（仅要求"已开启"）。
- 原文未给出具体的命中率提升、吞吐数字或延时基准。
- 原文未给出除 Mooncake 之外的其他池化后端实现说明。
