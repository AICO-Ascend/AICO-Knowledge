# Plugin System

> 仓 `vllm` · 路径 `docs/design/plugin_system.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/plugin_system.md

# vLLM 插件系统设计文档深度解读

## 【定位】
本文档描述 vLLM 提供的**插件机制（Plugin System）**，即如何让用户在**不修改 vLLM 主体代码**的前提下，通过 Python 标准的 `entry_points` 机制注册自定义能力（模型、平台、IO 处理器、统计日志器、HTTP 端点等），并规定各插件的发现方式、加载语义与编写规范。

---

## 【技术要点】

1. **基于 Python 标准 `entry_points` 的发现机制**：vLLM 完全依赖 `setuptools` 的 entry_points 机制，开发者只需在自己的 Python 包 `setup.py` 中声明 `entry_points` 字典，键为 vLLM 约定的"插件组（plugin group）"，值为 `"插件名 = 模块路径:可调用对象"`。
2. **每个进程都会加载插件**：由于 vLLM 涉及多进程（分布式推理 + 多种并行技术），插件函数会在 vLLM 创建的**每个进程**中被调用；加载由 `vllm.plugins.load_plugins_by_group` 函数完成。插件函数必须是**可重入（re-entrant）**的。
3. **插件过滤环境变量 `VLLM_PLUGINS`**：可通过设置该环境变量为插件名，仅加载特定插件（即按 plugin name 过滤）。
4. **五类受支持的插件组（plugin group）**：
   - `vllm.general_plugins` —— 注册**自定义模型**（调用 `ModelRegistry.register_model`）。
   - `vllm.platform_plugins` —— 注册**自定义平台**（返回 `None` 或平台类的完全限定名）。
   - `vllm.io_processor_plugins` —— 注册**pooling 模型的输入/输出预处理器**，返回 IOProcessor 类的完全限定名。
   - `vllm.stat_logger_plugins` —— 注册**自定义统计日志器**，entry point 须为 `StatLoggerBase` 子类。
   - `vllm.endpoint_plugins` —— 注册**自定义 HTTP 路由**，仅在 API server 前端进程加载，且**默认不加载**（需 opt-in）。
5. **插件三要素**：Plugin group（entry_points 的 key，必须是 `vllm.general_plugins` 等约定值）、Plugin name（entry_points 字典里的 value 名字，可被 `VLLM_PLUGINS` 过滤）、Plugin value（待注册的函数或模块的完全限定名）。
6. **平台插件须实现的最小函数集**（继承 `vllm.platforms.interface.Platform`）：`_enum`（通常为 `PlatformEnum.OOT`，表示 out-of-tree）、`device_type`、`device_name`、`check_and_update_config`（其中**必须设置 `worker_cls`**）、`get_attn_backend_cls`、`get_device_communicator_cls`。
7. **Worker 插件须实现的基础函数**（继承 `vllm.v1.worker.worker_base.WorkerBase`）：`init_device`、`initialize_cache`、`load_model`、`get_kv_cache_spec`、`determine_available_memory`、`initialize_from_config`、`execute_model`；可选支持 sleep/wakeup（睡眠模式）、`compile_or_warm_up_model`（graph mode）、`take_draft_token_ids`（投机解码）、`add_lora`/`remove_lora`/`list_loras`/`pin_lora`（LoRA）等特性。

---

## 【关键机制与数据】

**插件发现与加载流程**（原文无显式数据流图，但可按原文还原）：
1. 用户在自己包的 `setup.py` 中声明 `entry_points = {'vllm.general_plugins': ["register_dummy_model = vllm_add_dummy_model:register"]}`；
2. vLLM 启动时，`vllm.plugins.load_plugins_by_group` 读取该 entry point 组，过滤 `VLLM_PLUGINS` 环境变量指定的插件名；
3. **vLLM 创建的每一个进程**（worker、engine、API server 进程等）都会调用该插件函数；
4. 插件函数被执行，副作用地修改 vLLM 内部状态（例如注册新模型 `MyLlava` 到 `ModelRegistry`）。

**示例数据流**（原文）：
- 模型注册：插件 `register()` 函数读取 `vllm.ModelRegistry`，检查 `"MyLlava" not in ModelRegistry.get_supported_archs()`，然后调用 `ModelRegistry.register_model("MyLlava", "vllm_add_dummy_model.my_llava:MyLlava")`。
- 平台插件返回值约定：函数 `register()` 必须**返回一个字符串**（平台类的完全限定名，如 `"vllm_add_dummy_platform.my_dummy_platform.MyDummyPlatform"`），以让 vLLM 实例化该平台；**平台不支持时返回 `None`**。

**性能/数字数据**：原文未提供任何性能基准、数字或量化指标。

---

## 【表格解读】

**原文无表格**。

不过文档中存在可结构化的对照信息（用代码块给出），下面以表格形式**忠实复现**文档中关于"插件组 vs 用途 vs 返回值约定"的语义对照，便于阅读（内容完全来自原文各段落的并列叙述，不引入新信息）：

| 插件组（Plugin group） | 主要用途 | 加载语义 / 返回值约定（原文） |
|---|---|---|
| `vllm.general_plugins` | 注册自定义、out-of-the-tree 模型 | 调用 `ModelRegistry.register_model` 注册模型；官方示例见 `bart-plugin`（为 `BartForConditionalGeneration` 增加支持） |
| `vllm.platform_plugins` | 注册自定义、out-of-the-tree 平台 | 平台不支持当前环境时返回 `None`；支持时返回平台类的完全限定名字符串 |
| `vllm.io_processor_plugins` | 为 pooling 模型注册自定义 prompt/model output 的预/后处理 | 插件函数返回 IOProcessor 类的完全限定名 |
| `vllm.stat_logger_plugins` | 注册自定义、out-of-the-tree 日志器 | entry point 须为 `StatLoggerBase` 的子类（一个类） |
| `vllm.endpoint_plugins` | 在 OpenAI 兼容 API server 上注册自定义 HTTP 路由 | **仅在 API server 前端进程加载；默认不加载**（需 opt-in） |

---

## 【公式解读】

**原文无公式**（文档无 LaTeX 数学式或伪代码算法式表达）。仅有 Python 代码片段（`setup.py` 与 `register()` 示例），不属于公式范畴，故不展开。

---

## 【关联】

依据文末内部链接与文中交叉引用：

- **[Arch Overview](arch_overview.md)**：被第一节"How Plugins Work in vLLM"显式引用，理由是插件机制依赖于 vLLM 的进程架构——分布式推理与并行技术会让 vLLM 创建多个进程，因此插件必须在所有进程中被加载。**Plugin System 是 Arch Overview 所描述架构之上的一种用户级扩展面**。
- **[Endpoint Plugins](endpoint_plugins.md)**：被"Types of supported plugins"中关于 `vllm.endpoint_plugins` 的条目引用，用于说明 endpoint plugin 的**接口规范**。Plugin System 是 Endpoint Plugins 的注册/发现基础设施；Endpoint Plugins 文档则定义了该组插件的具体接口契约。
- **[Security — Endpoint Plugins](../usage/security.md#endpoint-plugins)**：被同一段落引用，说明 endpoint plugins 的**opt-in 机制与信任模型**（即默认不加载、需用户主动启用，并涉及安全考量）。Plugin System 文档本身只声明"endpoint plugins 默认不加载"，详细的安全策略、opt-in 步骤与信任边界在 `security.md#endpoint-plugins` 中。
- **`vllm.plugins.load_plugins_by_group`**：是 Plugin System 在 vLLM 代码层面的实际入口，文档将其点名为"完成插件跨进程加载"的函数。
- **`ModelRegistry.register_model`**：是 `vllm.general_plugins` 组插件的副作用入口；`bart-plugin` 仓库则是该组插件的官方参考实现。
- **`vllm.platforms.interface.Platform` 与 `vllm.v1.worker.worker_base.WorkerBase`**：是平台插件与 worker 插件必须继承的基类，构成 Plugin System 与 vLLM Platform/Worker 抽象层的接口契约。

---

## 【使用方法】

**启用方式 / 配置项（原文覆盖范围内）：**

1. **安装侧（开发者/使用者打包自己的插件包）**：在自己的包 `setup.py` 中声明 `entry_points`：
   ```python
   setup(
       name='vllm_add_dummy_model',
       version='0.1',
       packages=['vllm_add_dummy_model'],
       entry_points={
           'vllm.general_plugins':
           ["register_dummy_model = vllm_add_dummy_model:register"]
       })
   ```
   随后在该包 `__init__.py` 提供 `register()` 函数，调用 `vllm.ModelRegistry.register_model("MyLlava", "vllm_add_dummy_model.my_llava:MyLlava")`。

2. **加载侧（环境变量过滤）**：
   - 设置 `VLLM_PLUGINS=<plugin_name>`，仅加载指定名字的插件（按 entry point 字典中的 plugin name 过滤）。

3. **插件组选择**：按需选取下列组名之一作为 `entry_points` 的 key —— `vllm.general_plugins`、`vllm.platform_plugins`、`vllm.io_processor_plugins`、`vllm.stat_logger_plugins`、`vllm.endpoint_plugins`。

4. **平台插件项目结构（原文给出的样板）**：
   ```shell
   vllm_add_dummy_platform/
   ├── vllm_add_dummy_platform/
   │   ├── __init__.py
   │   ├── my_dummy_platform.py
   │   ├── my_dummy_worker.py
   │   ├── my_dummy_attention.py
   │   ├── my_dummy_device_communicator.py
   │   ├── my_dummy_custom_ops.py
   ├── setup.py
   ```
   `setup.py` 声明 `entry_points = {"vllm.platform_plugins": ["my_dummy_platform = vllm_add_dummy_platform:register"]}`，并保证 `register` 是**可调用的**，返回 `"vllm_add_dummy_platform.my_dummy_platform.MyDummyPlatform"`（字符串）。

5. **Endpoint 插件**（`vllm.endpoint_plugins`）：**默认不加载**；opt-in 方式与安全模型需参见 [`endpoint_plugins.md`](endpoint_plugins.md) 与 [`../usage/security.md#endpoint-plugins`](../usage/security.md#endpoint-plugins)，**原文未给出具体的环境变量名或启用命令**。

6. **编写规范**：
   - 插件函数必须**可重入（re-entrant）**，因为它在某些进程里会被调用多次。
   - 平台插件 `_enum` 属性通常填 `PlatformEnum.OOT`（out-of-tree）。
   - `check_and_update_config` 中**必须**设置 `worker_cls`；此处还可更新 block size、graph mode config 等 vLLM 配置。
   - Worker 插件按需选择性实现 sleep/wakeup（睡眠模式）、`compile_or_warm_up_model`（graph mode）、`take_draft_token_ids`（投机解码）、LoRA 系列函数（`add_lora`/`remove_lora`/`list_loras`/`pin_lora`）等可选特性。

> 注：原文末尾被截断（"If the plugin wants to support data paralleli…"），关于 data parallel 的具体说明**原文未涉及**，故此处不补充。
