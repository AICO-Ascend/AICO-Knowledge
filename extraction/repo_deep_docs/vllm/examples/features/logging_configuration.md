# Logging Configuration

> 仓 `vllm` · 路径 `examples/features/logging_configuration.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/examples/features/logging_configuration.md

# vLLM Logging Configuration 文档深度解读

## 【定位】
本文档系统阐述 vLLM 如何通过 Python `logging.config.dictConfig` 机制对内部日志系统进行灵活配置，覆盖从"完全禁用日志"到"自定义 JSON 配置"的多档使用场景，重点解决生产环境中日志格式定制、噪声日志抑制以及健康检查端点访问日志过滤等运维需求。

---

## 【技术要点】

1. **两大环境变量控制配置行为**
   - `VLLM_CONFIGURE_LOGGING`：是否启用 vLLM 自身的日志配置逻辑（默认启用，设为 `0` 表示禁用）
   - `VLLM_LOGGING_CONFIG_PATH`：自定义 JSON 日志配置文件路径（需配合 `VLLM_CONFIGURE_LOGGING` 启用时使用）

2. **三档配置粒度**（由两个环境变量组合控制）
   - 关闭 vLLM 日志：`VLLM_CONFIGURE_LOGGING=0` 且 `VLLM_LOGGING_CONFIG_PATH` 不设置
   - vLLM 默认配置：`VLLM_CONFIGURE_LOGGING` 不设置或设为 `1`，且不指定配置文件路径
   - 细粒度自定义：`VLLM_CONFIGURE_LOGGING` 启用 + `VLLM_LOGGING_CONFIG_PATH=<path-to-logging-config.json>`

3. **配置载体为 JSON 文件**，遵循 Python [logging configuration dictionary schema](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details)，主要字段包括 `formatters`、`handlers`、`loggers`、`version`

4. **根日志器（root vLLM logger）的级联机制**
   - 默认配置下，只有根 logger 被配置，其他 vLLM logger **defer to（委托给）** 根 logger 决策
   - 提供任何自定义 logger 配置都会**覆盖**内置默认配置，因此自定义时必须同时配置根 logger

5. **CLI 端点访问日志过滤选项**：`--disable-access-log-for-endpoints`，接受逗号分隔的端点列表（注意：**不能含空格**），仅作用于 uvicorn 访问日志而不影响 vLLM 应用日志

6. **端点匹配规则**：使用 **exact path matching**（精确路径匹配），查询参数被忽略（例如 `/health?verbose=true` 仍匹配 `/health`）

---

## 【关键机制与数据】

### 启动期配置决策流（原文语义重构）

1. **原文："If `VLLM_CONFIGURE_LOGGING` is enabled and no value is given for `VLLM_LOGGING_CONFIG_PATH`, vLLM will use built-in default configuration to configure the root vLLM logger."**
   → 仅有根 logger 被显式配置，其余 vLLM logger 通过 Python logging 默认传播机制继承根 logger 设置

2. **原文："If `VLLM_CONFIGURE_LOGGING` is disabled and a value is given for `VLLM_LOGGING_CONFIG_PATH`, an error will occur while starting vLLM."**
   → 两个变量存在**互斥校验关系**：禁用配置但又给出配置路径 = 启动错误

3. **原文："When custom configuration is provided for any logger, it is also necessary to provide configuration for the root vLLM logger since any custom logger configuration overrides the built-in default logging configuration used by vLLM."**
   → 自定义配置是**整体替换**而非增量叠加，必须显式声明根 logger

4. **访问日志过滤的实际场景数据（原文）**
   - Prometheus 抓取 `/metrics` 频率：**every 15-60s**
   - 健康检查来源：Kubernetes liveness/readiness probes, load balancers
   - 完全禁用所有访问日志的备选方案：`--disable-uvicorn-access-log`

5. **示例 2 中根 logger 的日志级别**：被设置为 `"DEBUG"`（原文 JSON 字段值），表明自定义场景下可灵活调整日志详细度

---

## 【表格解读】

原文包含一个关于"常用需过滤端点"的表格，**逐字还原**如下：

| Endpoint   | Description            | Typical Caller                                       |
| ---------- | ---------------------- | ---------------------------------------------------- |
| `/health`  | Health check           | Kubernetes liveness/readiness probes, load balancers |
| `/metrics` | Prometheus metrics     | Prometheus scraper (every 15-60s)                    |
| `/ping`    | SageMaker health check | SageMaker infrastructure                             |
| `/load`    | Server load metrics    | Custom monitoring                                    |

### 逐行解读

| 行号 | 解读要点 |
|------|----------|
| `/health` | Kubernetes 存活/就绪探针与负载均衡器周期性调用，用于判定服务是否健康可路由；高频轮询会污染日志 |
| `/metrics` | Prometheus 抓取器以 **15-60 秒** 为典型间隔抓取监控指标，每分钟产生 1-4 条访问日志，部署在多副本 + 高频抓取场景下噪声显著 |
| `/ping` | AWS SageMaker 基础设施用于健康探活；在 SageMaker 部署场景必须过滤，否则日志被 SageMaker 调用淹没 |
| `/load` | 自定义监控用途的服务器负载指标端点，使用频率与监控策略相关，由用户自定义 |

**表格作用**：指导运维人员识别哪些端点在哪些基础设施下需要加入 `--disable-access-log-for-endpoints` 列表，减少日志噪声同时保留业务请求访问日志。

---

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的公式表达）。

---

## 【关联】

原文文末"Additional resources"仅提供一条**外部链接**：
- Python 官方文档：[`logging.config` Dictionary Schema Details](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details)

**内部模块关联**（基于原文提及的符号推断）：
- `vllm.logging_utils.NewLineFormatter`：在示例 2 中被引用为内置 formatter 类，用于格式化 vLLM 日志输出（属于 vllm.logging_utils 模块）
- `pythonjsonlogger.jsonlogger.JsonFormatter`：示例 1 中引用的第三方 formatter，原文注明 "(which is part of the container image)"，说明该包已预装在 vLLM 容器镜像中
- uvicorn 访问日志系统：受 `--disable-access-log-for-endpoints` 与 `--disable-uvicorn-access-log` 两个 CLI 选项控制，是与 vLLM 应用日志**并行存在但相互独立**的日志通道（原文："This option only affects uvicorn access logs, not vLLM application logs"）

文末内部链接字段标注为"(无)"，即文档未在 vLLM 仓内交叉链接其他 markdown 文档。

---

## 【使用方法】

### 方式一：完全禁用 vLLM 日志（原文 Example 3）

```bash
VLLM_CONFIGURE_LOGGING=0 \
    vllm serve mistralai/Mistral-7B-v0.1 --max-model-len 2048
```

### 方式二：使用默认日志配置（原文）

```bash
# VLLM_CONFIGURE_LOGGING 不设置或设为 1，且不设置 VLLM_LOGGING_CONFIG_PATH
vllm serve mistralai/Mistral-7B-v0.1 --max-model-len 2048
```

### 方式三：自定义 JSON 日志配置（原文 Example 1 & 2）

**步骤 1**：创建 JSON 配置文件 `/path/to/logging_config.json`，遵循 Python logging dict schema
- Example 1：使用 `pythonjsonlogger.jsonlogger.JsonFormatter` 输出 JSON 格式至 STDOUT
- Example 2：使用 `vllm.logging_utils.NewLineFormatter` 并通过 `vllm.example_noisy_logger` 的 `"propagate": false` 静默特定子 logger

**步骤 2**：通过环境变量指定路径启动

```bash
VLLM_LOGGING_CONFIG_PATH=/path/to/logging_config.json \
    vllm serve mistralai/Mistral-7B-v0.1 --max-model-len 2048
```

### 方式四：过滤特定端点的访问日志（原文 Example 4）

```bash
vllm serve mistralai/Mistral-7B-v0.1 --max-model-len 2048 \
    --disable-access-log-for-endpoints /health,/metrics,/ping
```

**关键约束（原文标注）**：
- 仅影响 uvicorn 访问日志，不影响 vLLM 应用日志
- 多个端点使用**逗号分隔，无空格**
- 路径精确匹配，查询参数被忽略
- 若需完全禁用所有访问日志，改用 `--disable-uvicorn-access-log`

### 方式五：完全禁用 uvicorn 访问日志（原文）

原文未给出完整示例命令，但提示可使用 `--disable-uvicorn-access-log` 选项替代。
