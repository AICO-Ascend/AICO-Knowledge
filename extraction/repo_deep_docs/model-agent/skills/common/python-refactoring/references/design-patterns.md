# Skill: Python 常用设计模式应用

> 仓 `model-agent` · 路径 `skills/common/python-refactoring/references/design-patterns.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/common/python-refactoring/references/design-patterns.md

# 「Python 常用设计模式应用」设计文档深度解读

---

## 【定位】

本文档定位为 Python 重构场景下的"设计模式选用指南"——回答的不是"模式是什么"，而是"何时引入、用哪种、怎样写最 Pythonic"，核心解决**过度设计（over-engineering）**与**生搬硬套 GoF 范式**两个常见反模式问题。

---

## 【技术要点】

以下六条为本文档贯穿始终的核心机制，保留原文关键数字/参数/命令：

1. **模式引入门槛三原则**（原文"核心原则"）：
   - "只在模式能明确简化代码时才引入"
   - "优先使用 Python 语言特性（装饰器、上下文管理器、生成器等）"
   - "引入模式后代码行数不应显著增加"

2. **注册表工厂**（§1.1）：用 `dict[str, type[Serializer]]` 替代 if-elif 链；进阶方案为 `@register(name)` 装饰器实现自注册。Bad/Good 对照展示了 `raise ValueError(f"Unsupported format: {format_type}")` 的统一错误处理。

3. **单例两种 Pythonic 实现**（§1.2）：
   - 模块级变量 + 惰性初始化（`_config = None` → `get_config()`）
   - `@lru_cache(maxsize=1)` 装饰器函数
   备选方案优先级：模块级 > lru_cache > Singleton 类。

4. **Builder 替代为 dataclass**（§1.3）：触发条件为"构造参数超过 5 个"；通过 `@classmethod` 提供命名构造器（如 `simple()`、`paginated()`），默认参数 `size: int = 20` 用 `field(default_factory=lambda: ["*"])` 规避可变默认值陷阱。

5. **重试装饰器参数化**（§2.1）：`retry(max_attempts: int = 3, delay: float = 1.0)`，采用 `time.sleep(delay * (attempt + 1))` **线性退避**策略（attempt 0→delay×1, attempt 1→delay×2），而非指数退避。

6. **singledispatch 双层用法**（§3.4）：
   - 函数级：`@functools.singledispatch` + `@serialize.register`
   - 方法级：`@singledispatchmethod` 装饰在类方法上
   默认分支必须显式 `raise TypeError(...)`，避免未注册类型静默通过。

---

## 【关键机制与数据】

本文档以**代码范例**为载体传递机制，没有显式性能数据或 benchmark 数字，列出原文明确出现的关键工作原理与参数：

- **原文：注册表工厂工作原理** — `_SERIALIZERS.get(format_type)` 查表 → `cls is None` 时 raise → 否则 `cls()` 实例化；自注册版本通过 `@register("json")` 在类定义时即写入 `_REGISTRY[name] = cls`，**导入即注册**，无需在工厂函数内集中维护映射表。

- **原文：单例惰性加载原理** — `_config = None` 模块全局变量 + `if _config is None:` 判断；`lru_cache(maxsize=1)` 变体把判断逻辑下放到装饰器，函数返回结果被缓存，**第二次调用直接命中缓存不进入函数体**。

- **原文：Builder 触发阈值** — "构造参数超过 5 个，且有多种合法组合"；`paginated()` 用 `offset=page * size` 隐式实现分页偏移计算。

- **原文：装饰器 retry 退避公式** — `time.sleep(delay * (attempt + 1))`，第 i 次失败后等待 `delay × (i+1)` 秒；最终失败抛 `raise last_exc`。

- **原文：上下文管理器资源恢复语义** — `temporary_env` 中 `if old is None: del os.environ[key] else: os.environ[key] = old`，区分**环境变量原本不存在 vs 存在但被覆盖**两种恢复路径。

- **原文：观察者模式数据结构** — `_listeners: dict[str, list[Callable]]`，`setdefault(event, []).append(callback)` 一行完成懒初始化与注册；`emit` 遍历副本（隐式依赖 `get` 返回新列表）保证迭代期间修改不抛异常。

- **原文：模板方法骨架** — `DataPipeline.run()` 固定调用 `extract → transform → load`，三个 `@abstractmethod` 子类化时实现。

- **原文：迭代器生成器分页** — `paginated_fetch(url, page_size: int = 100)`，`page` 从 0 自增，`if not items: break` 终止条件；`yield from items` 平铺单页结果，调用方用 `for item in ...:` 惰性消费。

- **原文：执行流程五步**（文末）— ① 分析结构性问题 → ② 判断模式适用性 → ③ 选择 Pythonic 实现（**优先级：函数 > Protocol > ABC > 完整类层次**）→ ④ 实施重构保接口兼容 → ⑤ 验证行数与复杂度。

> 文档**未提供任何 benchmark / 性能数字 / 复杂度度量**，故无量化性能数据可标注。

---

## 【表格解读】

原文仅含 1 个表格（§4 反模式警示），逐字还原并逐行解读：

| 场景 | 错误做法 | 正确做法 |
|------|----------|----------|
| 只有一种实现 | 创建 Interface + Factory | 直接用具体类 |
| 简单条件分支（2-3 个） | 策略模式 | if-elif 即可 |
| 无需运行时切换 | 抽象工厂 | 直接实例化 |
| 只有一个观察者 | 完整事件系统 | 直接调用 |

**逐行解读：**

- **第 1 行 — "只有一种实现"**：当代码中仅存在单一实现类时，预先抽象出 `Interface` + `Factory` 属于"为未来可能性买单"，违反 YAGNI；正确做法是先用具体类，等真出现第二实现再抽取接口。**这是文档强调的"不为用模式而用模式"原则的最常见违反场景。**

- **第 2 行 — "简单条件分支（2-3 个）"**：原文明确划线，2–3 个分支属于 `if-elif` 合理范围；策略模式（Strategy）会引入 `Strategy` 协议/类 + 注册机制 + 调用点参数化，**代码行数显著膨胀**，违背"行数不应显著增加"原则。

- **第 3 行 — "无需运行时切换"**：抽象工厂（Abstract Factory）的价值在于**运行时根据配置/上下文切换整组产品族**；若实例化时机固定、类型确定，直接 `ClassName(...)` 即可，抽象层级无收益。

- **第 4 行 — "只有一个观察者"**：`EventEmitter` + 回调列表的开销（注册、emit 遍历、解耦）远超**直接函数调用**；只有当观察者 ≥ 2 且可能动态增减时才划算。

四行合起来构成文档的**否定式决策树**——用"反例"反向界定模式引入边界，与正文"触发条件 → 目标 → 原则"形成正反对照。

---

## 【公式解读】

**原文无公式。**

文档中出现的所有数学表达均隐式嵌入代码：
- 重试退避仅以 `time.sleep(delay * (attempt + 1))` 代码片段形式呈现，未抽象为显式公式；
- 分页偏移 `offset=page * size` 同理；
- 文档未使用任何 LaTeX / 伪代码公式块。

---

## 【关联】

原文文末声明：**内部链接: (无)**。

文档本身定位为**自包含的指导手册**，未显式引用仓内其他模块、上下游 skill 或前置文档。从主题推断（仓名 `model-agent`，路径 `skills/common/python-refactoring/references/`），可推测其**上下游关系**（非原文断言，仅基于路径信息）：

- **上游（调用方）**：`skills/common/python-refactoring/` 同级或上层 skill（如 SKILL.md、INDEX）应包含触发该文档的条件判断逻辑。
- **平行（同级 references）**：同目录可能存在其他重构参考资料（如命名规范、类型注解、性能优化等）。
- **下游（被引用）**：本文档为 references 级，被实际重构执行流程引用，但不直接调用仓内代码。

> **原文未给出任何超链接、模块路径交叉引用或"参见 X 文档"指引**，故严格依据原文无可写。

---

## 【使用方法】

原文"触发条件"与"执行流程"两节即为使用方法，逐条还原：

**触发条件（原文逐字）：**
> "当用户要求'应用设计模式'、'用模式重构'、'design pattern refactoring'，或代码中出现明显可用模式优化的结构时触发。"

**关键词触发清单**：
- 中文：`应用设计模式`、`用模式重构`
- 英文：`design pattern refactoring`
- 隐式触发：代码中出现 `重复分支` / `硬编码依赖` / `紧耦合`（见执行流程第 1 步）

**执行流程（原文五步）：**

1. 分析代码中的结构性问题（重复分支、硬编码依赖、紧耦合）
2. 判断是否有合适的模式可以简化问题
3. 选择最 Pythonic 的实现方式（优先级链：**函数 > Protocol > ABC > 完整类层次**）
4. 实施重构，确保接口兼容
5. 验证重构后代码行数未显著膨胀，复杂度确实降低

**配置项 / 命令**：原文未涉及——本文档为指引型 skill，无独立 CLI 命令、配置文件或开关项；其所有"配置"已内嵌在代码示例的参数默认值中（如 `max_attempts: int = 3`、`delay: float = 1.0`、`page_size: int = 100`、`size: int = 20`、`maxsize=1` 等）。
