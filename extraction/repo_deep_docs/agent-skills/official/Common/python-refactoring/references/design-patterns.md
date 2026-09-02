# Skill: Python 常用设计模式应用

> 仓 `agent-skills` · 路径 `official/Common/python-refactoring/references/design-patterns.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/Common/python-refactoring/references/design-patterns.md

# 一体化深度解读：Python 常用设计模式应用

---

## 【定位】

本 Skill 文档为昇腾 AI Agent 在 **代码重构任务** 中提供"何时引入设计模式、以何种 Pythonic 方式实现"的判断准则与具体范式，覆盖创建型、结构型、行为型三大类共 11 种模式，并给出反模式警示清单，避免过度设计。

---

## 【技术要点】

文档以"**模式适用场景 → Pythonic 实现 → 代码示例**"三段式组织，核心机制分条如下：

1. **工厂模式（Factory）**：用 `dict[str, type[Serializer]]` 注册表替代 if-elif 链；进阶方案用装饰器 `@register("json")` 实现**自注册工厂**，类定义即注册。
2. **单例模式（Singleton）**：优先使用**模块级全局变量 + `get_config()` 守卫**；备选用 `@lru_cache(maxsize=1)` 实现惰性单例，无需手写缓存逻辑。
3. **建造者模式（Builder）**：参数超过 5 个时用 `@dataclass` + `@classmethod`（如 `simple()` / `paginated()`）替代 Builder 类。
4. **装饰器模式（Decorator）**：直接使用 Python `@decorator` 语法实现横切关注点，示例 `retry(max_attempts=3, delay=0.5)` 采用**线性递增退避** `delay * (attempt + 1)`。
5. **上下文管理器模式**：`@contextmanager` + `try/finally` 处理资源释放，含 `os.environ` 临时切换的"保存-恢复"范式。
6. **策略 / 观察者 / 模板方法 / 单分发泛函 / 迭代器**：分别以 `Callable`、`Protocol`、ABC + `@abstractmethod`、`@singledispatch`、`yield from` 实现。
7. **反模式红线**：只有一种实现、2-3 个简单分支、无需运行时切换、单一观察者场景**不应**引入模式。

---

## 【关键机制与数据】

### 数据流与工作原理

- **注册表工厂机制**：将"类型名 → 类对象"映射存入 `_SERIALIZERS: dict[str, type[Serializer]]`，调用时 `get()` 取类并实例化，未命中则 `raise ValueError`。
- **自注册机制**：装饰器 `register(name)` 闭包捕获 `name`，将 `cls` 写入 `_REGISTRY`，**返回 `cls` 本身以保持装饰器语义**（类可继续正常实例化）。
- **`@lru_cache(maxsize=1)` 单例**：利用函数缓存槽位只有 1 个的特性，第二次调用直接返回缓存结果，**首次即惰性初始化**。
- **retry 退避机制**：`for attempt in range(max_attempts)` 循环内捕获 `Exception`，保留最后一次异常 `last_exc`，重试间隔按 `delay * (attempt + 1)` 线性增长（**最后一次不 sleep，直接抛异常**）。
- **事件发射机制**：`EventEmitter._listeners: dict[str, list[Callable]]` 按事件名分桶，`on()` 用 `setdefault` 保证桶存在，`emit()` 用 `*args, **kwargs` 透传。
- **单分发机制**：`@singledispatch` 在装饰的基函数内建立"类型 → 处理函数"表，`@serialize.register` 按**首个参数类型**匹配，未命中则调用基函数（示例中 `raise TypeError`）。
- **迭代器机制**：`paginated_fetch` 通过 `yield from items` 将分页结果扁平化输出，调用方用 `for item in ...` **惰性消费**，无一次性加载全部数据。

### 性能与参数（原文有的）

- `retry(max_attempts: int = 3, delay: float = 1.0)` —— 默认最大重试 3 次、初始延迟 1.0 秒；示例 `fetch_data` 使用 `max_attempts=3, delay=0.5`。
- `lru_cache(maxsize=1)` —— 仅保留 1 个缓存项，等同单例。
- `QueryConfig.paginated(..., size: int = 20)` —— 默认页大小 20；`offset = page * size` 计算偏移。
- `paginated_fetch(url, page_size: int = 100)` —— 默认每页 100 条，`page` 从 0 自增，空列表终止循环。
- `Formatter.format` 中 `f"{value:.2f}"` —— 浮点数格式化为 2 位小数；`datetime` 使用 `strftime("%Y-%m-%d")` 格式串。

---

## 【表格解读】

原文第 4 节"反模式警示"包含一张 4 行对比表，**逐字还原**如下：

| 场景 | 错误做法 | 正确做法 |
|------|----------|----------|
| 只有一种实现 | 创建 Interface + Factory | 直接用具体类 |
| 简单条件分支（2-3 个） | 策略模式 | if-elif 即可 |
| 无需运行时切换 | 抽象工厂 | 直接实例化 |
| 只有一个观察者 | 完整事件系统 | 直接调用 |

**逐行解读：**

- **第 1 行（只有一种实现）**：当系统中**不存在多态需求**时，预先建立抽象层（Interface + Factory）会增加间接层却无灵活性收益，违背文档核心原则"只在模式能明确简化代码时才引入"。
- **第 2 行（2-3 个简单分支）**：原文给出的"策略模式适用场景"是"同一操作有多种算法/策略，**运行时可切换**"，分支数仅 2-3 个时 `if-elif` 的可读性反而更高，无需拆成多个 Strategy 类。
- **第 3 行（无需运行时切换）**：抽象工厂用于**一族相关对象的创建**，若所有调用点都使用同一组对象，直接实例化更直接。
- **第 4 行（只有一个观察者）**：`EventEmitter` 的价值在解耦多个独立订阅者，单一订阅者可直接调用，无需事件分发基础设施（键、桶、回调注册）。

此表实质是文档原则"**不为用模式而用模式**"与"**引入模式后代码行数不应显著增加**"的操作化判据。

---

## 【公式解读】

原文**无标准数学公式**，但有两处可视为伪代码/算式的关键表达式，**逐字保留**并解释：

**1. 退避延迟表达式（出现在 `retry` 装饰器 `wrapper` 内）：**

```
time.sleep(delay * (attempt + 1))
```

- `delay`：用户传入的基础延迟秒数（示例为 `0.5`），类型 `float`。
- `attempt`：当前重试轮次（从 0 开始的 `range(max_attempts)` 循环变量）。
- `(attempt + 1)`：将零基索引转为 1 基倍数，第 1 次重试前等待 `delay*1`、第 2 次前等待 `delay*2`……形成**线性递增退避**（非指数）。
- 整体作用：失败次数越多等待越久，**最后一轮 `attempt == max_attempts - 1` 不进入睡眠直接抛 `last_exc`**。

**2. 分页偏移表达式（出现在 `QueryConfig.paginated` 类方法）：**

```
offset = page * size
```

- `page`：第几页（零基索引）。
- `size`：每页条数（默认 20）。
- 整体作用：将"页码"线性映射为"记录偏移量"，配合 `limit=size` 共同构成标准分页查询参数。

**3. 生成器终止条件（出现在 `paginated_fetch`）：**

```
if not items:
    break
```

- `items`：当次请求返回的记录列表（`response.json()["items"]`）。
- 整体作用：当 API 返回空列表时终止 `while True` 循环，避免无限请求；同时在循环体内通过 `page += 1` 自增翻页。

---

## 【关联】

原文未提供内部链接，但内容上与以下 Python 生态机制强耦合，构成隐式上下游关系：

- **`functools` 模块**：被 `lru_cache`、`singledispatch`、`singledispatchmethod`、`wraps` 四个工具直接引用，构成"用 Python 标准库替代 Java 风格 GoF 实现"的核心支撑（呼应文档核心原则第 2 条）。
- **`contextlib.contextmanager`**：用于装饰器式上下文管理器生成器，是"用上下文管理器模式"的官方推荐入口。
- **`abc.ABC` 与 `@abstractmethod`**：模板方法模式中用于声明可被子类覆盖的步骤，构成 ABC 抽象基类流程骨架（`run` 方法调用 `extract → transform → load`）。
- **`dataclasses` 与 `field(default_factory=...)`**：建造者模式中用 `field` 配合 lambda 构造可变默认值列表 `["*"]`，避免经典的可变默认参数陷阱。
- **`typing.Protocol`**：策略模式中用结构化子类型（鸭子类型的静态版）替代抽象基类，使策略实现无需显式继承。
- **`os.environ` 资源**：`temporary_env` 上下文管理器针对环境变量的"读旧值-设新值-恢复"流程，是上下文管理器模式的典型应用领域。
- **HTTP 分页 API**：`paginated_fetch` 展示了"生成器 + 远程 API"的标准集成方式，与请求库 `requests` 配合使用（`requests.get(url, params=...)`）。
- **JSON / ISO 时间**：`datetime.fromisoformat(...)` 用于适配器模式中遗留时间字段的解析，构成"对接遗留接口"的具体手段。

文档整体也呼应自身开头的核心原则——优先选择 **函数 > Protocol > ABC > 完整类层次**（执行流程第 3 步），各类实现方案的"重量"递增。

---

## 【使用方法】

### 启用触发条件（原文"触发条件"节）

- 用户**显式触发**：当用户要求"应用设计模式"、"用模式重构"、"design pattern refactoring"。
- **隐式触发**：代码中出现明显可用模式优化的结构（如 if-elif 创建实例链、硬编码依赖、紧耦合通知逻辑等）。

### 执行流程（原文"执行流程"节，5 步）

1. **分析问题**：识别代码中的结构性问题（重复分支、硬编码依赖、紧耦合）。
2. **判断匹配**：确认是否存在能**真正简化问题**的合适模式。
3. **选择实现**：按 **函数 > Protocol > ABC > 完整类层次** 的优先级选择 Pythonic 方案。
4. **实施重构**：确保接口兼容，不破坏调用方。
5. **验证收益**：确认重构后代码行数**未显著膨胀**、复杂度确实降低。

### 关键判断准则（原文"核心原则"节）

- 只在模式能**明确简化代码**时才引入。
- 优先使用 Python 语言特性（**装饰器、上下文管理器、生成器**等）而非照搬 Java 风格 GoF 实现。
- 引入模式后代码行数不应显著增加；若增加，重新评估是否值得。

原文未涉及具体的配置文件、命令行参数或外部配置项；本 Skill 的"配置"完全内化为上述触发条件与执行流程中的判断准则。
