# msOpGen算子调试工具快速入门

> 仓 `msopgen` · 路径 `docs/zh/quick_start/msopgen_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopgen/docs/zh/quick_start/msopgen_quick_start.md

# msOpGen算子调试工具快速入门 — 一体化深度解读

> ⚠️ 说明：原文档在最后一个代码块尾部被截断（"...but WITHOUT ANY WA"），因此 §2.3.3 之后的内容以及可能存在的 §3 编译/运行章节未呈现，本解读严格基于已展示内容。

---

## 【定位】

这篇文档解决"算子开发从零搭建工程繁琐"的问题——以一个简易加法算子（AddCustom）为示例，演示如何使用 `msOpGen` 工具根据一份 JSON 配置文件自动生成完整的 Ascend C 自定义算子工程框架（含 Host 侧 / Kernel 侧 / Tiling / 编译脚本等目录骨架），并指导用户在其中 3 个标为【用户扩展点】的 C++ 文件中实现算子核心逻辑，从而让开发者聚焦算法本身。

---

## 【技术要点】

1. **强制容器环境前置**：教程仅支持标准化 CANN 容器环境，不兼容裸机 / 虚拟机 / 其他非标准容器；环境自检脚本必须全部输出 `[PASS]` 才可继续。原文外网可达环境预计耗时："约 3 分钟"。
2. **JSON 输入配置驱动工程生成**：配置声明算子的"函数签名"——`op` 名称、`language`（如 cpp）、`input_desc`/`output_desc`（含 `name`/`param_type`/`format`/`type`）。算子函数体由用户实现，其余代码由工具生成。
3. **`msopgen gen` 命令三要素**：`msopgen gen -i msopgen_demo.json -c xxx -lan cpp -out AddCustom`，其中 `-c` 参数格式必须为 `aicpu` 或 `ai_core-{首字母小写芯片SoC型号}`（注意下划线 `_` 与减号 `-` 不能错，例如 `ai_core-ascendxxx`）。芯片型号通过 `python3 -c "import acl; print(acl.get_soc_name())"` 动态获取。
4. **三个【用户扩展点】文件**：工程生成后仅有 3 个文件需用户修改：
   - `op_host/add_custom.cpp`（算子原型注册、shape 推导、信息库、tiling 实现）
   - `op_kernel/add_custom_tiling.h`（Tiling 分块策略数据结构定义）
   - `op_kernel/add_custom.cpp`（算子 Kernel 侧具体计算实现）
6. **Tiling 分块策略核心数字**：`TILE_NUM = 8`（每个核上分 8 个 tile）、`BLOCK_DIM = 8`（使用 8 个 AI Core 核并行计算）；TilingData 结构包含 `uint32_t totalLength`（数据总量）和 `uint32_t tileNum`（分块个数）两个字段。
7. **Kernel 侧计算三段式数据流**：原文明确给出"GM → UB 搬运 → 向量加法 → UB → GM 写回"，即从 Global Memory 搬运到 Unified Buffer，执行向量加法后写回 GM。

---

## 【关键机制与数据】

- **Host / Kernel 职责划分（原文）：** "Host侧：运行于CPU的代码，负责数据预处理、任务调度及算子调用；Kernel侧：运行于NPU的代码，负责执行实际的大规模并行计算逻辑。"
- **Tiling 机制（原文）：** "Tiling：将大规模数据分块处理，以提高 Local Memory 利用率并优化内存访问效率。"
- **TilingFunc 工作两步（原文代码注释）：** 
  - 第一步：把 `totalLength` 与 `tileNum` 两个数字信息写入 `context`；
  - 第二步：把 `BLOCK_DIM`（使用多少个 AICore）写入 `context`。
- **TilingData 字段含义（原文）：** `totalLength` = 总计算数据量；`tileNum` = 每个核上总计算数据分块个数。
- **算子输入输出规格（原文 JSON）：** 两个输入 `x` / `y` + 一个输出 `z`，均 `param_type: required`、`format: ND`、`type: float16`，对应 Host 侧注册为 `ge::DT_FLOAT16` / `ge::FORMAT_ND`、`REQUIRED`。
- **AICore 配置兼容性（原文）：** 原 op_host 生成代码会包含 `this->AICore().AddConfig("xxx")` 形式的具体 SoC 行（如 `ascend910_93` / `ascend910b`），需用真实查询结果替换，不可硬编码。
- **性能数据**：原文未给出任何 benchmark / 时延 / 吞吐数字。
- **环境检查关键路径**：`[ -f /.dockerenv ]`（容器标识）、`$ASCEND_HOME_PATH`、`$ATB_HOME_PATH`（CANN 环境变量）、`~/ot_demo/msot/example/quick_start`（示例代码仓）。

---

## 【表格解读】

**原文无正式表格**，但含一段目录结构图（以 `text` 代码块呈现），按 markdown 表格**逐字还原**如下：

| 层级 / 路径 | 类型 | 说明（原文标注） |
|---|---|---|
| `AddCustom/` | 目录 | 算子工程根目录 |
| `├── build.sh` | 文件 | 编译入口脚本 |
| `├── CMakeLists.txt` | 文件 | 算子工程的 CMakeLists.txt |
| `├── framework/` | 目录 | 算子插件实现文件目录，单算子模型文件的生成不依赖算子适配插件，无需关注 |
| `│   ├── CMakeLists.txt` | 文件 | （框架子 CMake） |
| `│   └── tf_plugin` | 项 | （框架子目录） |
| `├── op_host/` | 目录 | Host 侧实现文件 |
| `│   ├── add_custom.cpp` | 文件 | **【用户扩展点】** 算子原型注册、shape 推导、信息库、tiling 实现等内容文件 |
| `│   └── CMakeLists.txt` | 文件 | （Host 侧 CMake） |
| `├── op_kernel/` | 目录 | Kernel 侧实现文件 |
| `│   ├── add_custom.cpp` | 文件 | **【用户扩展点】** 算子代码实现文件 |
| `│   ├── add_custom_tiling.h` | 文件 | **【用户扩展点】** 算子 tiling 定义文件 |
| `│   └── CMakeLists.txt` | 文件 | （Kernel 侧 CMake） |
| `└── CMakePresets.json` | 文件 | 编译配置项 |

**逐行解读：**

- **根目录顶层 3 项**（`build.sh` / `CMakeLists.txt` / `CMakePresets.json`）构成"编译入口 + CMake 主配置 + 预设配置"三件套，是用户后续执行 `bash build.sh` 编译的入口。
- **`framework/` 目录**原文已明确"无需关注"——它对应 TF 算子适配插件，单算子模型（单算子编译运行）路径下不依赖，目的是让用户聚焦核心三件套。
- **`op_host/` 目录**承担算子从框架视角的"对外契约"：算子原型注册让框架认识 AddCustom；tiling 函数在此处定义并通过 `SetTiling` 注入；`AddConfig` 决定兼容哪些 SoC。
- **`op_kernel/` 目录**是真正在 NPU 上跑的代码，其中：
  - `add_custom_tiling.h` 仅声明**数据结构**（TilingData），不写逻辑；
  - `add_custom.cpp` 写**实际计算**（GM→UB→加法→UB→GM）；
  - 两个文件通过 Host 侧 `TilingFunc` 中的 `tiling.SaveToBuffer(...)` 形成"Host 算 → Kernel 读"的桥梁。
- 3 个【用户扩展点】的位置非常关键：`host` 端 1 个、`kernel` 端 2 个（其中一个是头文件）——这是文档希望用户每次只改这 3 处的核心意图。

---

## 【公式解读】

**原文无数学公式**，但出现一组 C++ 宏定义（可视为"算子配置 DSL 公式"），逐字保留原式并解读：

| 原式（原文宏） | 符号 / 元素 | 含义与作用 |
|---|---|---|
| `BEGIN_TILING_DATA_DEF(TilingData)` | `BEGIN_TILING_DATA_DEF` | 宏：声明 Tiling 结构体的**名称**为 `TilingData`，开启字段定义块 |
| `TILING_DATA_FIELD_DEF(uint32_t, totalLength)` | `TILING_DATA_FIELD_DEF` `(uint32_t, totalLength)` | 宏：声明结构体成员——**类型** `uint32_t`，**名称** `totalLength`，含义"总计算数据量" |
| `TILING_DATA_FIELD_DEF(uint32_t, tileNum)` | `(uint32_t, tileNum)` | 宏：声明成员——类型 `uint32_t`，名称 `tileNum`，含义"每个核上分块个数" |
| `END_TILING_DATA_DEF` | `END_TILING_DATA_DEF` | 宏：结束 Tiling 结构体字段定义 |
| `REGISTER_TILING_DATA_CLASS(AddCustom, TilingData)` | `(AddCustom, TilingData)` | 宏：将 `TilingData` 类**注册**到名为 `AddCustom` 的算子上，建立"算子名 → TilingData 类型"的映射，使框架能找到对应的反序列化类型 |

**伪代码视角的总公式**（原文 TilingFunc 逻辑浓缩）：

```
input_shape_size = context.GetInputShape(0).GetOriginShape().GetShapeSize()   // 读：输入张量元素总数
tile_num         = 8                                                          // 常量：每个核分块数
block_dim        = 8                                                          // 常量：使用核数

tiling.totalLength = input_shape_size                                         // 写：写入 TilingData
tiling.tileNum     = tile_num
tiling.SaveToBuffer(context.GetRawTilingData().GetData(),
                     context.GetRawTilingData().GetCapacity())
context.GetRawTilingData().SetDataSize(tiling.GetDataSize())

context.SetBlockDim(block_dim)                                                // 写：写入并行核数
return GRAPH_SUCCESS
```

每个符号作用已在上文表中给出；该公式的作用是把"输入规模 → 切分策略 + 并行度"这一组数字传递给核函数。

---

## 【关联】

文档涉及 3 个明确的外部引用 / 上下游关系：

1. **前置依赖（文档顶部声明）：** 已完成《算子开发工具链快速入门》全流程操作（链接：`docs/zh/quick_start/op_tool_quick_start.md`）。本教程默认读者已具备算子开发工具链的基础认知，并已在 `~/ot_demo/msot/example/quick_start` 拥有示例代码仓。
2. **环境安装依赖（§2.1.1 引用）：** 《昇腾 AI 算子开发工具链学习环境安装指南》（链接：`docs/zh/quick_start/installation_guide.md`）——是产生"标准化 CANN 容器 + 预装工具/示例/依赖"的基础。
3. **深度学习资源（§2.3 多次引用）：** 《昇腾 Ascend C 编程入门教程（纯干货）》外部博客（`hiascend.com`）——用于理解 3 个用户扩展点文件的功能与协作机制，以及 Tiling / Host-Kernel 协作原理。
4. **模块内部关系：** `msOpGen`（代码生成）→ 用户在 `op_kernel/add_custom_tiling.h`（声明 TilingData 数据结构）→ 在 `op_host/add_custom.cpp` 的 `TilingFunc` 中**填充**该数据结构并设置 `BLOCK_DIM` → 在 `op_kernel/add_custom.cpp` 中**消费**该数据并执行 GM↔UB 搬运与向量加法 → 通过 `build.sh` 编译。
5. **运行时上下游：** `AddConfig("ascend910b")` / `AddConfig("ascend910_93")` 这类 SoC 字符串决定了该算子可在哪些昇腾芯片 AI Core 上运行；它通过 `python3 -c "import acl; print(acl.get_soc_name())"` 在运行时动态获取，不可硬编码。

---

## 【使用方法】

**原文有明确命令，全部列出：**

| 步骤 | 命令 / 配置 | 作用 |
|---|---|---|
| §2.1.2 环境自检（容器） | `[ -f /.dockerenv ] && [ -n "$ASCEND_HOME_PATH" ] && [ -n "$ATB_HOME_PATH" ] && echo -e "\033[32m[PASS] CANN 容器环境 OK \033[0m" \|\| echo -e "\033[31m[FAIL] 非标容器或未进入容器！\033[0m"` | 检测是否处于 CANN 容器 |
| §2.1.2 环境自检（示例仓） | `[ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] 示例代码仓 OK\033[0m" \|\| echo -e "\033[31m[FAIL] 代码仓缺失\033[0m"` | 检测示例代码仓是否存在 |
| §2.2.1 创建源码根目录 | `rm -rf ~/ot_demo/workspace/src && mkdir -p ~/ot_demo/workspace/src && cd ~/ot_demo/workspace/src` | 建立算子源码工作区 |
| §2.2.2 写配置 | 将给定的 JSON 保存为 `msopgen_demo.json`（含 `op: AddCustom`、2 个 ND/float16 输入、1 个 ND/float16 输出） | 声明算子签名 |
| §2.2.3 查询 SoC | `python3 -c "import acl; print(acl.get_soc_name())"` | 取芯片 SoC 名，用于拼接 `-c` |
| §2.2.3 生成工程 | `msopgen gen -i msopgen_demo.json -c xxx -lan cpp -out AddCustom`（`xxx` 替换为 `aicpu` 或 `ai_core-{小写SoC}`） | 自动生成算子工程骨架 |
| §2.3.1 Tiling 数据结构 | 用 `BEGIN_TILING_DATA_DEF` / `TILING_DATA_FIELD_DEF` / `END_TILING_DATA_DEF` / `REGISTER_TILING_DATA_CLASS(AddCustom, TilingData)` 宏声明 `totalLength` 与 `tileNum` | 定义 TilingData 结构并注册到 AddCustom |
| §2.3.2 Host 侧 | 编写 `TilingFunc`（设置 `TILE_NUM=8` / `BLOCK_DIM=8`），并通过 `Input/Output/ParamType/DataType/Format/AICore().SetTiling/AddConfig` 注册算子原型 | 完成算子原型 + Tiling 计算 |
| §2.3.3 Kernel 侧 | 修改 `op_kernel/add_custom.cpp`（原文代码块被截断，未给出完整内容） | 实现 GM→UB→加法→UB→GM 计算逻辑 |

**配置项 / 开关（原文已明示的）：**
- `language: "cpp"`（仅展示了 cpp 路径，Ascend C 算子）
- `format: ["ND"]`（数据排布格式）
- `type: ["float16"]`（数据类型）
- `param_type: "required"`（参数是否必填）
- `TILE_NUM = 8` / `BLOCK_DIM = 8`（分块与并行度常量）
- `AddConfig("...")` 中可填多个 SoC 字符串以支持多芯片兼容
- `ge::DT_FLOAT16` / `ge::FORMAT_ND` / `REQUIRED`（Host 侧注册常量）

**编译入口（原文目录结构中标注但具体命令被截断）：** `AddCustom/build.sh` 为编译入口脚本；`CMakePresets.json` 为编译配置项；具体 `bash build.sh` / `-c` 等详细命令在文档未展示的章节给出。
