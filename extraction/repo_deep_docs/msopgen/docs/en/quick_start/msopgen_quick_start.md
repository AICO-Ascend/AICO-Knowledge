# msOpGen Quick Start

> 仓 `msopgen` · 路径 `docs/en/quick_start/msopgen_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopgen/docs/en/quick_start/msopgen_quick_start.md

# msOpGen Quick Start 文档深度解读

## 【定位】

本指南描述 msOpGen 工具的核心能力——通过一份 JSON 配置文件, 自动生成完整的 Ascend NPU 自定义算子工程框架 (host 端 tiling/注册逻辑 + kernel 端计算实现 + 构建脚本), 让开发者只聚焦于算子核心算法实现, 而非重复的脚手架与构建配置工作。

---

## 【技术要点】

1. **依赖自检命令**: 通过单行 Python 命令一次性验证 `numpy / sympy / scipy / attrs / psutil / decorator` 是否齐全, 并强制约束 `numpy.__version__ <= 1.26.4`, 输出 `All is OK` 即视为通过。
2. **工作区约定**: 算子源码根目录固定为 `~/ot_demo/workspace/src`, 通过 `rm -rf … && mkdir -p … && cd …` 一行完成清理与切换。
3. **输入配置 JSON 结构**: 每个算子条目含五大字段——
   - `op`: 算子名, 文档示例为 `AddCustom`
   - `language`: 实现语言, 取值 `cpp`
   - `input_desc` / `output_desc`: 张量描述列表, 每个含 `name` / `param_type`(均为 `required`)/ `format`(均为 `ND`)/ `type`(均为 `float16`)
   - 示例算子定义了两个输入 `x`、`y` 和一个输出 `z`, 均采用 ND 布局的 float16。
4. **代码生成命令**: `msopgen gen -i msopgen_demo.json -c xxx -lan cpp -out AddCustom`, 其中 `-c` 需替换为芯片型号拼接串。
5. **芯片型号拼接格式**: `-c` 选项接受两种形态 —— `aicpu` 或 `ai_core-{SoC_model_in_lowercase}`, 文档给出两个正例 `ai_core-ascend910B4` 与 `ai_core-ascend910_9392`, 并以红色高亮强调**下划线与连字符的正确使用** (`ai_core-ascend910B4`)。
6. **三大用户扩展点 (user extension point)**: 生成的 `AddCustom` 工程仅需开发者修改以下三个 C++ 文件——
   - `op_host/add_custom.cpp`: 算子原型注册、shape 推导、信息库、tiling 实现
   - `op_host/add_custom_tiling.h`: Tiling 策略定义
   - `op_kernel/add_custom.cpp`: kernel 端算子实现

---

## 【关键机制与数据】

**原文: 算子工程自动生成的工作机制**

msOpGen 把一份"类 C 函数声明"形式的 JSON 输入, 翻译成完整的 C++ 工程目录, 目录树如下(原文逐字保留):

```
AddCustom
├── build.sh                 // Entry script for the build
├── cmake                    // Build script
├── CMakeLists.txt           // Build script of the operator project.
├── scripts                  // Directory of scripts used for custom operator project packing
├── framework                // Directory for storing the implementation file of the operator plugin. The generation of single-operator model files does not depend on the operator plugin and can be ignored.
│   ├── CMakeLists.txt
│   └── tf_plugin
├── op_host                  // Implementation file on the host.
│   ├── add_custom.cpp       // [User extension point] Content file for operator prototype registration, shape derivation, information library, and tiling implementation.
│   ├── add_custom_tiling.h  // [User extension point] Operator tiling definition file.
│   └── CMakeLists.txt
├── op_kernel                // Implementation file on the kernel
│   ├── add_custom.cpp       // [User extension point] Operator code implementation file.
│   └── CMakeLists.txt
└── CMakePresets.json        // Build configuration item
```

**原文: host / kernel 划分与 Tiling 概念**

- **On the host**: 运行在 CPU 上的代码, 负责数据预处理、任务调度、算子调用。
- **On the kernel**: 运行在 NPU 上的代码, 负责执行大规模并行计算。
- **Tiling**: 大规模数据按块处理, 提升片上局部存储利用率、优化访存效率。

**原文: Kernel 端数据流**

AddCustom 的 kernel 端实现遵循固定的数据搬运链 —— **GM → UB 搬运 → 向量加法 → UB → GM 写回**。

**原文: Tiling 数据结构示例**

`op_host/add_custom_tiling.h` 中通过宏 `BEGIN_TILING_DATA_DEF(TilingData)` 声明 tiling 结构, 并用 `TILING_DATA_FIELD_DEF(uint32_t, totalLength)` 定义成员 `totalLength`(数据类型 `uint32_t`), 含义为数据总量(原文在此处被截断, 仅给出该片段)。

---

## 【表格解读】

**原文无表格**(整篇文档未出现 markdown 表格; 出现的 JSON 配置与项目目录树均为代码块/列表形式, 非表格)。

---

## 【公式解读】

**原文无公式**(文档未给出 LaTeX 数学公式或伪代码公式; 加法算子的数学表达通过自然语言"向量加法"描述, 未形式化)。

---

## 【关联】

本指南在文中显式指向了如下上下游资料/模块, 构成完整学习链路:

| 关联对象 | 类型 | 关系 |
|---|---|---|
| Ascend Operator Development Toolchain Quick Start (`op_tool_quick_start.md`) | 前置指南 | 假设已完成, 否则先读它 |
| Ascend AI Operator Development Toolchain Learning Environment Installation Guide (`installation_guide.md`) | 环境配置 | 严格按其完成依赖安装与工作区配置, 即便环境类似也建议重做一遍以保证一致 |
| Chip SoC Type Obtaining Method (`get_chip_soc_type.md`) | 工具手册 | 用于查询 `-c` 选项要拼接的芯片型号(如 `Ascend910B4`) |
| Ascend C Programming Guide (hiascend.com 外部博客) | 进阶阅读 | 深入理解三个用户扩展点文件的协作机制 |
| `op_host/add_custom_tiling.h` ↔ `op_host/add_custom.cpp` ↔ `op_kernel/add_custom.cpp` | 内部三文件协作 | 同一算子的 host 端 tiling 策略、host 端注册/调度、kernel 端计算三件套 |
| `framework/` 目录 | 可忽略模块 | 单算子模型文件生成不依赖算子插件, 文档明确说明可忽略 |

msOpGen 本身位于更大的 `Ascend/msot` 工具链中, 本篇只是该工具链的"工程生成"环节; 后续算子编译/运行环节由配套工具(如 build.sh)及 Ascend C 编程框架承接。

---

## 【使用方法】

### 启用方式

1. **环境前置**(原文强制要求):
   - 已完成《Ascend Operator Development Toolchain Quick Start》
   - 已按《Ascend AI Operator Development Toolchain Learning Environment Installation Guide》完成安装

2. **Python 依赖自检**(执行后看到 `All is OK` 方可继续):
   ```shell
   python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"
   ```

3. **创建源码根目录**:
   ```shell
   rm -rf ~/ot_demo/workspace/src && mkdir -p ~/ot_demo/workspace/src && cd ~/ot_demo/workspace/src
   ```

4. **编写输入配置**: 在 `~/ot_demo/workspace/src` 下保存 `msopgen_demo.json`, 内容即上文【技术要点 3】中的 JSON(算子名 `AddCustom`, 语言 `cpp`, 两个 float16/ND 输入 `x`/`y`, 一个 float16/ND 输出 `z`)。

### 配置项(命令参数)

| 选项 | 含义 | 取值示例 |
|---|---|---|
| `-i` | 输入 JSON 配置文件路径 | `msopgen_demo.json` |
| `-c` | 芯片型号(需先查阅 `get_chip_soc_type.md`) | `ai_core-ascend910B4`、`ai_core-ascend910_9392`、`aicpu` |
| `-lan` | 算子实现语言 | `cpp` |
| `-out` | 生成工程名 | `AddCustom` |

### 启动命令

```shell
msopgen gen -i msopgen_demo.json -c xxx -lan cpp -out AddCustom
```

> ⚠️ **注意**: `-c` 的值必须严格按"下划线连接 ai_core, 连字符连接 SoC 型号"拼接, 例如 `ai_core-ascend910B4`, 文档以红字特别标注该位置。

### 后续动作

执行生成命令后, 进入 `AddCustom/` 工程目录, 仅修改三大用户扩展点文件:
- `op_host/add_custom_tiling.h`
- `op_host/add_custom.cpp`
- `op_kernel/add_custom.cpp`

其余目录(`cmake/`、`scripts/`、`framework/`、`CMakePresets.json` 等)为框架代码, 无特殊需求无需改动。
