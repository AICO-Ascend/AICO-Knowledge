# MindSpeed-Bridge 自动加载原理

> 仓 `mindspeed-bridge` · 路径 `docs/zh/feature/autoload_installer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-bridge/docs/zh/feature/autoload_installer.md

# MindSpeed-Bridge 自动加载原理 — 一体化深度解读

## 【定位】

这篇文档说明 MindSpeed-Bridge 安装后, MindSpeed 补丁、模型适配代码与训练 step 三类资源分别在何时、以何种触发方式被加载; 核心目的是**避免两套隐式触发机制共存**, 通过 `.pth` 仅监听 AutoBridge, 而把训练入口 (recipe / step) 的加载留给 `run_recipe.py` 显式完成。

---

## 【技术要点】

1. **双入口拆分设计**: `.pth` 启动文件**只**监听 AutoBridge 模块导入 (含 `register_mindspeed_adaptor` 等能力), 不负责训练入口; 训练所需的 recipe 与 step 由 `mindspeed_bridge/scripts/training/run_recipe.py` 主动加载。
2. **模型适配按需触发**: 首次调用 `AutoBridge.from_hf_pretrained` / `from_hf_config` 时, runtime 才扫描并加载文件名以 `_bridge.py` 或 `_provider.py` 结尾的模型适配模块; 模型实现 (`mindspeed_bridge/models`) 和 `*_step.py` 在该路径下**不会**被加载。
3. **step 收集只在 run_recipe 链路**: 只有启动 `run_recipe` 时才会扫描 `mindspeed_bridge/models/<model>/<model>_step.py` 并合并到上游 `STEP_FUNCTIONS`; 安装包、AutoBridge 调用、运行 `compare.py` 均不扫描 step。
4. **环境变量开关**: `MINDSPEED_BRIDGE_AUTOREG_MODE` 默认 `auto`, 提供 `auto / strict / debug / eager / off` 五种模式, 仅此一个自动加载配置。
5. **诊断与测试命令**: 安装诊断用 `mindspeed-bridge-register`(独立进程依次尝试 adaptor、bridge/provider、recipe); 本地 UT 用 `bash tests/ut/ut_run.sh`, runtime UT 单独跑 `tests/ut/runtime/test_runtime_registration.py`。
6. **失败隔离策略**: 可选模型加载失败仅记录原因不影响其他; 必需入口使用 `strict=True` 让缺失依赖立即暴露; `mindspeed_bridge.models` 顶层包不导入具体模型。

---

## 【关键机制与数据】

### 1. 总体触发分流 (`原文: §1 mermaid 流程图`)

Python 启动后经 `.pth` 只监听 AutoBridge 模块, 随后按程序行为三分流:

- 调用 AutoBridge → 启用 MindSpeed adaptor + 加载模型 bridge/provider
- 启动 `run_recipe` → 主动加载 recipe + 扫描合并 `*_step.py`
- 运行其他 Python 程序 → 既不加载 MindSpeed 也不加载模型代码

**核心原则**: `.pth` 只监听 AutoBridge, 不负责训练入口; 训练 recipe 与 step 由 `run_recipe.py` 明确加载, 避免隐式触发机制重复。

### 2. 安装产物结构 (`原文: §2`)

```text
mindspeed_bridge/
├── runtime/                  # 按需启用补丁、发现模型和训练 step
├── scripts/training/
│   └── run_recipe.py        # 对齐上游目录的训练入口
├── models/                   # provider、bridge、模型贡献文件
└── recipes/                  # 训练配置
setup.py
pyproject.toml
```

安装命令: `pip install -e . --no-deps`(`--no-deps` 适用于已具备 MindSpeed、Megatron-LM、Megatron-Bridge 的联合环境)。

### 3. AutoBridge 调用链 (`原文: §4 sequenceDiagram`)

外部程序 → `from megatron.bridge import AutoBridge` → `AutoBridge.from_hf_pretrained(model_path)` → 导入监听触发 → runtime 启用 MindSpeed adaptor → 查找 `_bridge.py` / `_provider.py` → AutoBridge 按 HF 配置匹配 Bridge → 返回。调用方**不需要**手工导入 `mindspeed_bridge.models`。

### 4. run_recipe 调用链 (`原文: §5 flowchart`)

`run_recipe` 启动 → 启用 MindSpeed adaptor → 加载上游 `run_recipe.py` → 加载 MindSpeed-Bridge recipes → 扫描 `models` 下 `*_step.py` → 合并到上游 `STEP_FUNCTIONS` → 调用上游 main。新增 step 的位置: `mindspeed_bridge/models/<model>/<model>_step.py`; 文件名默认作为 `--step_func` 值 (例 `glm5_step.py` → `--step_func glm5_step`); 函数默认必须叫 `forward_step`, 自定义名需通过 `STEP_FUNCTIONS = {"glm5_step": forward_abc}` 显式映射。`compare.py` 自带 `vlm_forward_step()`, 不需要 `qwen3_vl_step`, 只需 MindSpeed adaptor + AutoBridge 找到的 bridge/provider。

### 5. 诊断命令行为 (`原文: §6`)

`mindspeed-bridge-register` 在独立进程中依次尝试: ① 启用 MindSpeed ② 加载全部 bridge/provider ③ 加载全部 recipe, 然后打印成功项与错误信息。该"一次检查全部"过程**不属于** AutoBridge 或 `run_recipe` 正常调用链, 业务代码不应调用。CI runtime UT 用 mock 模块验证扫描规则、注册顺序、step 合并、错误记录, **不要求 NPU 环境**。

---

## 【表格解读】

### 表 1: runtime 各文件负责什么 (`原文: §3`)

| 处理阶段 | 文件 | 作用 |
|---|---|---|
| Python 启动 | `build_backend.py`、`autoload.py` | 通过 `.pth` 监听 AutoBridge, 但不提前加载 Megatron 和模型代码 |
| 查找模型 | `plugin_scanner.py`、`plugin_registry.py` | 调用 AutoBridge 时加载各模型的 provider 和 bridge |
| 扩展入口 | `adapters.py`、`entrypoints/steps.py` | 对上游模块做少量修改, 或把各模型提供的 step 合并到入口中 |
| 运行记录 | `state.py`、`utils.py` | 避免同一操作重复执行, 并保存加载失败的原因 |

**解读**: `auto_register.py` 作为 runtime 对外提供函数的统一位置, 初始化函数从此处被调用; 模型实现、step 收集、模块修改分别落在上表四类文件中, 避免把所有逻辑堆入单一文件。这是一种典型的**关注点分层**: 监听 (启动期) → 查找 (AutoBridge 触发期) → 扩展 (入口合并) → 记录 (幂等与失败追踪)。

### 表 2: 初始化函数使用时机 (`原文: §6`)

| 能力 | 何时使用 |
|---|---|
| `register_mindspeed_adaptor()` | 在 Megatron 加载 GPU 实现前启用 MindSpeed 补丁 |
| `install_config_validate_patch()` | 本地入口自己创建并校验 `ConfigContainer` 时使用 |

**解读**: 文档明确告诫"不要因为函数存在就全部调用", 入口只启用自己需要的能力——前者是补丁启用, 后者是本地 ConfigContainer 校验, 各自服务于不同调用链。

### 表 3: `MINDSPEED_BRIDGE_AUTOREG_MODE` 取值 (`原文: §7`)

| 值 | 行为 | 使用场景 |
|---|---|---|
| `auto` | 按需启用 adaptor 和模型适配, 导入失败时记录错误 | 默认运行方式 |
| `strict` | 按需加载, 任何导入失败立即抛出原始异常 | RL、权重转换和 CI 排障 |
| `debug` | 等同严格模式, 并输出插件导入过程 | 定位实际加载了哪些模块 |
| `eager` | Python 启动时立即加载 adaptor | 兼容必须提前打补丁的特殊程序 |
| `off` | 不安装 AutoBridge 导入监听 | 确认问题是否由自动加载引起 |

**解读**: 默认 `auto` 提供宽松容错; `strict/debug` 用于排障, 二者区别仅在于 `debug` 多输出插件导入过程日志; `eager` 会让**所有 Python 进程**启动时尝试加载 MindSpeed, 可能影响同环境其他框架, 默认不要使用; `off` 是隔离验证手段——此模式下 RL 直接调用 AutoBridge 时不会自动启用 MindSpeed, 也不会自动加载 MindSpeed-Bridge 模型适配, 仅用于确认问题来源。

---

## 【公式解读】

**原文无公式**。文档涉及的关键参数均为命名标识 (文件名后缀 `_bridge.py`/`_provider.py`/`*_step.py`、环境变量值 `auto/strict/debug/eager/off`、函数名 `forward_step`) 与命令字符串, 没有数学公式或伪代码算法表达式。

---

## 【关联】

- **开发指南**: 文档开头明示"如何新增入口见 [autoload_installer_dev_guide.md](../develop/autoload_installer_dev_guide.md)"——本篇描述**运行时行为**, 该开发指南对应**新增入口的实现方式**, 二者构成"原理 + 扩展"配对。
- **上游对齐**: `mindspeed_bridge/scripts/training/run_recipe.py` 标注为"对齐上游目录的训练入口", 加载上游 `run_recipe.py` 与合并到上游 `STEP_FUNCTIONS` 表明 MindSpeed-Bridge 通过 wrapper 方式桥接到 Megatron-Bridge / Megatron-LM 既有体系, 而非另起炉灶。
- **三处差异化的加载路径**:
  - AutoBridge 路径 → 触发 `_bridge.py` / `_provider.py` 加载 (§4)
  - `run_recipe` 路径 → 额外加载 recipes 并扫描 `*_step.py` (§5)
  - `compare.py` → 自带 `vlm_forward_step()`, 仅需 adaptor + bridge/provider, 不需要 `qwen3_vl_step` (§5 末段)
- **诊断 / 测试侧**: `mindspeed-bridge-register` 命令与 `tests/ut/runtime/test_runtime_registration.py` 形成"生产排障 + CI mock 验证"双轨——前者基于真实依赖, 后者基于 mock 验证扫描规则、注册顺序、step 合并、错误记录四类行为。

---

## 【使用方法】

### 安装 (`原文: §2`)

```bash
pip install -e . --no-deps
```

适用条件: 已准备好 MindSpeed、Megatron-LM 和 Megatron-Bridge 的联合环境。

### 训练启动 (`原文: §9`)

```bash
torchrun <distributed_args> --module mindspeed_bridge.scripts.training.run_recipe \
    --recipe <recipe_name> \
    --step_func <step_name>
```

### 诊断 (`原文: §9`)

```bash
mindspeed-bridge-register
```

### 排障 — 列出实际加载的模块 (`原文: §7`)

```bash
MINDSPEED_BRIDGE_AUTOREG_MODE=debug \
python your_rl_or_conversion_script.py
```

### 本地 UT (`原文: §6`)

```bash
# 全部 UT
bash tests/ut/ut_run.sh
# 仅 runtime UT
bash tests/ut/ut_run.sh tests/ut/runtime/test_runtime_registration.py
```

### 环境变量 (`原文: §7`)

正常 AutoBridge / RL / 权重转换 / `run_recipe` 使用**不需要**设置环境变量; 唯一保留的自动加载配置为 `MINDSPEED_BRIDGE_AUTOREG_MODE`, 默认 `auto`。`run_recipe` 通过已安装的 `megatron.bridge` 自动定位上游脚本, 不提供额外路径变量。

### 一句话总结 (`原文: §9`)

> **安装时只监听 AutoBridge; 调用 AutoBridge 时加载模型适配; 启动 run_recipe 时才加载 recipe 并收集 step。**
