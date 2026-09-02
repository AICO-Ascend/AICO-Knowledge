# Endpoint Plugins

> 仓 `vllm` · 路径 `docs/design/endpoint_plugins.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/endpoint_plugins.md

# vLLM Endpoint Plugins 设计文档深度解读

## 【定位】

本文档定义了 vLLm 的 **Endpoint Plugin** 机制——一种允许**外部包**（out-of-tree packages）向 OpenAI 兼容的 API 服务器**注册自定义 HTTP 路由**的可插拔扩展点，其作用域被显式限定在 **HTTP 路由层**，不引入新的引擎访问路径。

---

## 【技术要点】

1. **协议接口 `EndpointPlugin`**：运行时可检查的 `Protocol`，包含四个成员：`name`（唯一标识）、`required_tasks`（任务依赖）、`attach_router`（路由注册）、`async init_state`（状态初始化）。
2. **两阶段生命周期**：A 阶段路由注册（引擎尚未就绪，由 `build_app()` 触发）+ B 阶段状态初始化（引擎通常可用，由 `init_app_state()` 触发）。
3. **默认禁用 + 显式白名单**：与 `vllm.general_plugins` 等其它插件组"默认全加载、VLLM_PLUGINS 缩小范围"相反，**endpoint plugins 默认完全不加载**，必须通过环境变量 `VLLM_PLUGINS` 显式命名才可启用。
4. **入口点分组 `vllm.endpoint_plugins`**：通过 `pyproject.toml` 或 `setup.py` 的 `[project.entry-points."vllm.endpoint_plugins"]` 注册零参数工厂函数，**白名单匹配的是入口点名称而非插件 `name` 属性**。
5. **引擎可达性**：插件通过启动时获得的 `EngineClient`（典型调用方式 `engine_client.collective_rpc(...)`）访问引擎；CPU only 的 render server 无 `EngineClient`，此时 `init_state` 收到 `engine_client=None`，需在路由处理器中处理 503 降级或通过 `required_tasks` 排除 `"render"` 任务。
6. **与 `vllm.general_plugins` 的分离**：endpoint_plugins 仅覆盖 HTTP 前端；如需新增 worker 侧 RPC 方法或自定义 stat，应单独通过 `vllm.general_plugins` 入口点注册，二者独立加载、互不蕴含。

---

## 【关键机制与数据】

- **作用域边界**（原文）："Their scope is the **HTTP surface only** registering routes and optionally per app state used by those routes." 引擎访问路径与 in-tree 处理器完全一致，不新增独立通道。
- **`app.state` 等同关系**（原文）："Because `app.state` *is* the `state` object passed to `init_app_state()`"，A 阶段存储的对象在 B 阶段可见，B 阶段存储的对象在请求时通过 `request.app.state` 可见——与 in-tree 端点模式相同。
- **典型调用链**（原文代码示例）：路由处理器 `scheduler_config` 在请求时通过 `raw_request.app.state.my_engine_client` 取出 handler，再调用 `engine_client.collective_rpc("get_scheduler_config")`。
- **工厂失败处理**（原文）："A factory that raises an issue during instantiation is logged and skipped. It does not abort server startup."——单插件失败不阻塞服务启动。
- **进程作用域**（原文）："Only the front end API server process loads endpoint plugins. There is no need to guard for worker or engine core processes."
- **示例与测试**（原文）：`tests/plugins/vllm_add_dummy_endpoint_plugin` 演示了引擎为 None 时返回 HTTP 503 的做法；其端到端测试（含真实 HTTP 请求）在 `tests/plugins_tests/test_endpoint_plugins.py`。
- **路径冲突**（原文）：当前**无路由冲突强制机制**（tracked as a follow-up to RFC [#46565](https://github.com/vllm-project/vllm/issues/46565)），后注册的路由胜出。
- **稳定性边界**（原文）："`FastAPI`, `EngineClient` and the `EndpointPlugin` protocol itself are the supported surface"；in-tree `OpenAIServing*` 类的内部结构不在稳定契约内，跨版本可能变更。

---

## 【表格解读】

原文包含一个生命周期阶段表（Phase Lifecycle），逐字还原如下：

| Phase | Called from | `engine_client` available? | Work |
| --- | --- | --- | --- |
| A. Route registration | `build_app()` | No | `attach_router(app)` add routes. Do not touch the engine here. |
| B. State init | `init_app_state()` | Usually but `None` on the CPU only render server | `init_state(engine_client, state, args)` build a serving handler holding `engine_client` and store it on `state`. |

**逐行解读**：

- **Phase A 行**：发生在 `build_app()` 调用栈中，此刻引擎尚未启动，因此 `engine_client` 不可用。这一阶段仅允许执行 `attach_router(app)` 来挂载路由，文档明确警告"Do not touch the engine here"——因为引擎对象此刻尚不存在。
- **Phase B 行**：发生在 `init_app_state()` 调用栈中。`engine_client` 一般可用（"Usually"），但在 CPU only 的 render server 上会显式传入 `None`，因此插件必须能在两种情况下安全降级。Work 列描述了典型模式：构建一个持有 `engine_client` 的小型 serving handler，然后挂到 `state`（即 `app.state`）上，供后续路由处理器在请求时读取。
- 两阶段的设计根因（原文）："Routes are registered before the engine exists."——路由注册必须先于引擎存在，因此协议必须拆分为时间点不同的两个钩子。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **安全姿态** [`../usage/security.md#endpoint-plugins`]：本文档开篇即用 warning block 引导读者查阅该链接，特别强调"route shadowing warning"（路由遮蔽风险）——即后注册的同名路径会覆盖核心路由，这正是后文 Path-prefix convention 一节要求"命名空间化"的动机。
- **插件系统总览** [`plugin_system.md`]：在两处被引用——
  1. 入口点命名约定段落，明确 `VLLM_PLUGINS` 白名单"matching on the **entry point name**"沿用与 `vllm.general_plugins` 相同的约定；
  2. "Pairing with `vllm.general_plugins`" 一节，详细说明一个完整插件应同时注册两个入口点：HTTP 路由走 `vllm.endpoint_plugins`，worker 侧方法走 `vllm.general_plugins`，二者独立加载。
- **上游 RFC** [#46565](https://github.com/vllm-project/vllm/issues/46565)：作为"路径冲突强制机制"的待办事项来源，目前状态为"tracked as a follow-up"，意味着当前路径命名空间规范尚属约定而非强制。
- **代码符号引用**：文档多次交叉引用代码内符号 `vllm.plugins.endpoint_plugins.interface.EndpointPlugin`、`vllm.plugins.load_endpoint_plugins`、`engine_client.collective_rpc(...)`，以及测试目录 `tests/plugins/` 与 `tests/plugins_tests/`，共同构成"协议 + 加载器 + 测试夹具"的完整闭环。
- **兼容性边界**：与 in-tree 的 `OpenAIServing*` 类形成对比——后者是内部实现细节，前者是稳定支持的契约面，二者的边界在文档结尾的"Compatibility"小节被明确划定。

---

## 【使用方法】

**1. 实现插件类**（原文 Python 示例）：

```python
class MyAdminEndpointPlugin:
    name = "my_admin_endpoint_plugin"
    required_tasks: tuple[str, ...] | None = None

    def attach_router(self, app: FastAPI) -> None:
        @app.get("/plugins/my_admin_endpoint_plugin/scheduler_config")
        async def scheduler_config(raw_request: Request):
            engine_client = raw_request.app.state.my_engine_client
            results = await engine_client.collective_rpc("get_scheduler_config")
            return {"scheduler_config": results}

    async def init_state(self, engine_client, state, args) -> None:
        state.my_engine_client = engine_client
```

**2. 注册入口点**（原文两种方式）：

```toml
# pyproject.toml
[project.entry-points."vllm.endpoint_plugins"]
my_admin_api = "my_pkg.endpoints:MyAdminEndpointPlugin"
```

```python
# setup.py 等价写法
setup(
    name="my_pkg",
    entry_points={
        "vllm.endpoint_plugins": [
            "my_admin_api = my_pkg.endpoints:MyAdminEndpointPlugin"
        ]
    },
)
```

**3. 启用插件（运行时白名单）**：通过环境变量 `VLLM_PLUGINS` 显式列出入口点名称（注意是 `my_admin_api` 而非 `name="my_admin_endpoint_plugin"`）。

**4. 任务过滤**：通过 `required_tasks` 元组声明服务必须支持的任务集合（如 `("generate", "embed")`）；设为 `None` 表示无任务要求；包含或等于 `None` 即被 render server 加载（需在 `init_state` / 路由处理器内处理 `engine_client=None`，例如返回 HTTP 503，参见 `tests/plugins/vllm_add_dummy_endpoint_plugin`）。

**5. 路径命名建议**（原文）：优先使用 `/plugins/<plugin-name>/...` 这样的独立前缀；若必须使用 `/v1/...` 等核心前缀，需在文档中明确告知运维人员这是有意覆盖行为。

**6. 与 worker 侧插件配对**（原文建议的发布形态）：

```toml
[project.entry-points."vllm.general_plugins"]
my_admin_engine = "my_pkg.engine:register"      # 新增 worker 侧方法
[project.entry-points."vllm.endpoint_plugins"]
my_admin_api = "my_pkg.endpoints:MyAdminEndpointPlugin"  # 新增 HTTP 路由
```
