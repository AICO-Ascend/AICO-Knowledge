# msSanitizer Quick Start

> 仓 `mssanitizer` · 路径 `docs/en/quick_start/mssanitizer_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mssanitizer/docs/en/quick_start/mssanitizer_quick_start.md

# msSanitizer Quick Start 文档深度解读

## 【定位】
本文档是一篇面向 Ascend AI Processor 单算子开发场景的 **msSanitizer 异常检查工具快速上手指南**，通过一个简单 AddCustom 加法算子示例，演示如何检测运行时的内存越界、竞争、未初始化和同步异常等严重缺陷。

## 【技术要点】

1. **工具定位与覆盖范围**：msSanitizer 基于 Ascend AI Processor，提供 **memory check、race check、uninitialization check、synchronization check** 四类异常检查能力，作用于单算子开发场景。
2. **前置依赖检查**：通过 `python3 -c` 一行命令验证 `numpy`（≤1.26.4）、`sympy`、`scipy`、`attrs`、`psutil`、`decorator` 等 Python 依赖是否完整。
3. **编译选项注入**：在 kernel 侧 `CMakeLists.txt` 第 1 行插入 `add_ops_compile_options(ALL OPTIONS -sanitizer)`，并在原文件备份 `.orig.bak` 后通过 `sed -i` 注入检测桩代码。
4. **故障注入演示**：将 `CopyOut` 中 `DataCopy` 的拷贝长度从 `TILE_LENGTH` 改为 `2 * TILE_LENGTH`，人为制造越界错误。
5. **三种检测子工具入口**：`mssanitizer --tool=memcheck`、`--tool=racecheck`、`--tool=initcheck` 三种检查模式，通过 `bash run.sh` 触发运行。
6. **结果复现链路**：`bash ./build.sh` 构建 → `find` 定位 `custom_opp_*.run` 安装包 → `bash $MY_OP_PKG` 部署 → 进入 `caller` 目录执行检测命令。

## 【关键机制与数据】

- **内存越界错误报告样例**（原文 memcheck 输出）：
  - 报错类型：`out of bounds of size 256`
  - 写入位置：`at 0x12c0c0026000 on GM`，位于 `AddCustom_ab1b6750d7f510985325b603cb06dc8b_0`
  - 发生块：`block aiv(1) on device 0`
  - PC 位置：`pc current 0x1e28 (serialNo:87)`
  - 调用栈 5 层，最终定位到 `/root/ot_demo/workspace/src/AddCustom/op_kernel/add_custom.cpp:128:10`、`63:14`、`169:9`

- **竞争错误报告样例**（原文 racecheck 输出）：
  - 报错类型：`Potential WAR hazard detected at UB`（Write-After-Read 竞争）
  - 触发位置：`PIPE_MTE3 Read at WAR()+0x400 in block 0 (aiv) on device 0`
  - PC 位置：`pc current 0x1e28 (serialNo:31)`
  - 调用栈同样指向 `add_custom.cpp:128:10 / 63:14 / 169:9`

- **未初始化错误报告样例**（原文 initcheck 输出）：
  - 报错类型：`uninitialized read of size 256`
  - 读取位置：`at 0x400 on UB`
  - 发生块：`block aiv(0-7) on device 3`
  - PC 位置：`pc current 0x1e34 (serialNo:241)`
  - CANN 版本路径：`/usr/local/Ascend/cann-8.5.0/aarch64-linux/asc/impl/basic_api/dav_c220/kernel_operator_data_copy_impl.h:124:9`
  - 调用栈指向 `add_custom.cpp:126:9 / 63:13 / 167:8`

- **运行环境版本线索**：错误堆栈中出现的工具链路径涉及 `ascend-toolkit/8.3.RC1` 与 `cann-8.5.0` 两个版本（原文未明示统一，仅作路径标注）。

## 【表格解读】
**原文无表格**。原文中所有信息均通过文本段落、命令块、错误报告样例呈现，未使用任何表格结构。

## 【公式解读】
**原文无公式**。原文中仅存在 `2 * this->tileLength` 这样的代码修改表达式，并非数学/算法公式；其作用仅是构造越界错误的代码改动，无符号定义或推导含义需要展开。

## 【关联】

本文档作为 mssanitizer 工具链的 Quick Start 入口，依赖并指向多个上下游模块（均为外部链接，文末内部链接区标注"无"，但文中多处出现相对/绝对外链）：

| 关联资源 | 关联位置 | 作用 |
|---|---|---|
| **Ascend Operator Development Toolchain Quick Start**（op_tool_quick_start.md） | 第 1.1 节、第 2.2 节 | 前置教程：本文档假定读者已完成该教程；第 2.2 节要求完成其 2.1 和 2.3 节才能进行算子项目准备 |
| **Ascend AI Operator Development Toolchain Learning Environment Installation Guide**（installation_guide.md） | 第 1.2 节 | 环境安装与工作区配置：作者强调即使已有类似环境也须重做以保证依赖与变量一致 |
| **自定义算子 `AddCustom`** | 第 2.3 节全程 | 演示载体：所有故障注入与检测均在该算子（`op_kernel/add_custom.cpp`、`op_kernel/CMakeLists.txt`）上执行 |
| **`run.sh` 调用脚本** | 第 2.3.4/2.3.5/2.3.6 节 | 检测入口：作为 `mssanitizer` 包装的执行体被反复调用 |

## 【使用方法】

**1. 环境依赖验证（原文 2.1.1）**
```shell
python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"
```

**2. 编译选项启用 sanitizer（原文 2.3.1）**
```shell
cd ~/ot_demo/workspace/src/AddCustom
\cp -f op_kernel/CMakeLists.txt op_kernel/CMakeLists.txt.orig.bak
sed -i "1i\\add_ops_compile_options(ALL OPTIONS -sanitizer)" op_kernel/CMakeLists.txt
```

**3. 故障注入（原文 2.3.2）**
修改 `op_kernel/add_custom.cpp` 的 `CopyOut`：
```diff
- AscendC::DataCopy(zGm[progress * this->tileLength], zLocal, this->tileLength);
+ AscendC::DataCopy(zGm[progress * this->tileLength], zLocal, 2 * this->tileLength);
```

**4. 重新构建与部署（原文 2.3.3）**
```shell
bash ./build.sh
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

**5. 三种检测命令（原文 2.3.4 ~ 2.3.6）**
```shell
cd ~/ot_demo/workspace/src/caller
mssanitizer --tool=memcheck bash run.sh    # 内存检查
mssanitizer --tool=racecheck bash run.sh   # 竞争检查
mssanitizer --tool=initcheck bash run.sh   # 未初始化检查
```

**6. 恢复现场（原文 2.3.7）**
```shell
cd ~/ot_demo/workspace/src/AddCustom
\cp -f op_kernel/CMakeLists.txt.orig.bak op_kernel/CMakeLists.txt
```
