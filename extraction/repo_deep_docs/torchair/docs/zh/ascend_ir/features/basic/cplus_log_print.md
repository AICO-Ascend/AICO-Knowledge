# TorchAir C++层日志打印

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/cplus_log_print.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/cplus_log_print.md

# TorchAir C++层日志打印 深度解读

## 【定位】
这篇文档描述了 TorchAir 在昇腾 NPU 上进行图模式推理时，如何通过环境变量 `TNG_LOG_LEVEL` 控制 C++ 层（图执行过程中）的日志输出级别，从而实现 C++ 层功能调试与问题定位的能力。

---

## 【技术要点】

1. **核心开关机制**：通过单一环境变量 `TNG_LOG_LEVEL` 控制 C++ 层日志输出，是 C++ 层唯一的日志级别控制入口。
2. **五级日志体系**：从细到粗依次为 DEBUG → INFO → WARNING → ERROR → EVENT，对应数值 0、1、2、3、4，数值越大输出越精简。
3. **级别输出规则**：每一级开启后会**包含本级及更低级别的所有日志**（例如 DEBUG 级输出 DEBUG/INFO/WARNING/ERROR 四类日志）。
4. **默认值**：环境变量 `TNG_LOG_LEVEL` 的默认值为 `"3"`，即默认仅输出 ERROR 日志，调试时需要主动下调级别。
5. **事件专用级别**：EVENT（值为 4）是独立分支——该级别开启后输出 ERROR 和 EVENT 两类日志（不含 WARNING/INFO/DEBUG），与其他级别的"渐进包含"规则不同。
6. **两种环境变量注入路径**：支持 shell 内 `export` 设置，也支持 Python 脚本中 `os.environ` 设置，但 Python 方式**必须早于 `import torchair`** 才能生效。

---

## 【关键机制与数据】

### 工作原理
- **过滤式日志输出**：C++ 层在图执行过程中（如算子转换、图装配、会话加载、图执行等环节）持续产生日志条目，最终通过 `TNG_LOG_LEVEL` 进行级别过滤，最终仅向用户输出不低于所设置级别的条目。
- **覆盖范围**（原文）：文档明确该日志涵盖「图执行过程中的日志信息」，从样例可看出覆盖 `static_npu_graph_executor.cpp`（算子装配合输出创建）、`concrete_graph/session.cpp`（session 加载/执行图）等关键路径。

### 日志格式（原文样例结构）
每条日志遵循统一格式：

```
[<级别>] TORCHAIR(<进程ID>,python):<时间戳> [<源文件>:<行号>]<线程ID> <消息内容>
```

样例中可解析出的字段：
- **进程标识**：`2250956`（多次出现，表明同一进程内的多线程序号）
- **时间戳粒度**：`2025-02-06-15:44:53.084.205`（毫秒.微秒级）
- **来源文件及行号**：`static_npu_graph_executor.cpp:46`、`static_npu_graph_executor.cpp:130`、`concrete_graph/session.cpp:238` 等

### 性能/数据维度（原文未涉及）
原文未给出任何性能开销数字、日志输出速率或存储占用等量化数据。

---

## 【表格解读】

**原文无表格**。

原文日志级别虽然具备「数值 ↔ 级别名 ↔ 输出范围」三列对照关系，但并非以 markdown 表格呈现，而是以无序列表形式列出。为便于对照，下面将其内容整理（非还原）：

| 数值 | 级别 | 开启后输出内容 |
|------|------|----------------|
| 0 | DEBUG | DEBUG、INFO、WARNING、ERROR |
| 1 | INFO | INFO、WARNING、ERROR |
| 2 | WARNING | WARNING、ERROR |
| 3 | ERROR | ERROR（默认值） |
| 4 | EVENT | ERROR、EVENT |

逐行解读：
- **0/DEBUG**：最详尽模式，包含 4 类日志，适合首次接入或异常排查初期阶段。
- **1/INFO**：去噪，保留运行轨迹摘要（如图执行成功信息），适合日常回归。
- **2/WARNING**：仅关注潜在异常信号。
- **3/ERROR**：默认上线级别，仅输出错误信息，避免日志爆炸。
- **4/EVENT**：独立事件追踪分支，仅记录预定义的关键事件与错误，**不再遵循"渐进包含"规则**，这一特殊点须特别注意。

---

## 【公式解读】

**原文无公式**。

文档不涉及任何数学公式或伪代码表达式，日志格式属于纯文本结构而非公式形式。

---

## 【关联】

文档**未提供内部链接**，也未显式指向上下游模块。但从内容交叉点可推断以下隐含关联：

- **`static_npu_graph_executor.cpp`**：在样例日志中高频出现（第 46、130、138、256 行），是 C++ 层负责「aten Tensor ↔ ge::Tensor 装配」与「静态图执行器」的核心组件，与 `Assemble aten device input`、`Create empty output`、`Assemble torch output`、`Static npu graph executor run graph` 等消息一一对应。
- **`concrete_graph/session.cpp`**：负责会话管理层面的图加载与执行（`Start to session load graph`、`Start to session execute graph`）。
- **`import torchair` 触发顺序**：文档强调 Python 方式设置环境变量必须早于 `import torchair`，这意味着该环境变量在 `torchair` 包导入初始化阶段被读取，与 `torchair` 包内部初始化流程存在时序耦合。

---

## 【使用方法】

### 方式 1：Shell 环境变量（原文）
安装完软件包后，以运行用户身份登录环境：
```bash
export TNG_LOG_LEVEL=0
```
此方式对当前 shell 会话及其子进程全部生效。

### 方式 2：Python 脚本设置（原文）
在 Python 脚本最早期设置，必须早于 `import torchair`：
```python
import os
os.environ['TNG_LOG_LEVEL'] = '0'
```
> [!NOTE] 说明
> 该方式设置环境变量时，须早于 `import torchair`，否则影响日志打印。

### 级别选用建议（基于原文规则）
- DEBUG 排查：`TNG_LOG_LEVEL=0`
- 日常运行监控：`TNG_LOG_LEVEL=1`
- 仅看告警：`TNG_LOG_LEVEL=2`
- 默认生产：`TNG_LOG_LEVEL=3`（默认）
- 关键事件追踪：`TNG_LOG_LEVEL=4`
