# Quickstart: Building with CMake

> 仓 `gperftools` · 路径 `vendor/googletest/docs/quickstart-cmake.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/gperftools/vendor/googletest/docs/quickstart-cmake.md

# gperftools 代码仓文档深度解读

## 【定位】

这篇文档是 GoogleTest 框架基于 **CMake 构建系统**的入门级教程，旨在指导用户从零开始创建一个 C++ 项目，使用 CMake 的 `FetchContent` 模块拉取并构建 GoogleTest 依赖，编写首个测试用例，并通过 `ctest` 运行测试。

---

## 【技术要点】

1. **环境前置条件**：
   - 兼容操作系统：Linux、macOS、Windows
   - C++ 编译器必须支持 **C++17** 及以上
   - 构建工具可选 **Make**、**Ninja** 等（详见 CMake Generators 文档）

2. **CMake 版本与项目声明**：
   - `cmake_minimum_required(VERSION 3.14)` —— 指定最低 CMake 版本
   - `project(my_project)` —— 声明项目名
   - `set(CMAKE_CXX_STANDARD 17)` + `set(CMAKE_CXX_STANDARD_REQUIRED ON)` —— 强制 C++17

3. **GoogleTest 依赖获取方式**：
   - 使用 `FetchContent` 模块从 GitHub 直接拉取源码
   - 锁定 Git 提交哈希：`03597a01ee50ed33e9dfd640b249b4be3799d395`
   - Windows 平台特殊配置：`set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)`

4. **测试二进制构建配置**：
   - `enable_testing()` —— 启用 CMake 测试子系统
   - `add_executable(hello_test hello_test.cc)` —— 声明可执行目标
   - `target_link_libraries(hello_test GTest::gtest_main)` —— 链接 GoogleTest 主库
   - `include(GoogleTest)` + `gtest_discover_tests(hello_test)` —— 注册测试发现机制

5. **构建与执行命令链**：
   - `cmake -S . -B build` —— 配置阶段（生成构建目录）
   - `cmake --build build` —— 编译阶段
   - `cd build && ctest` —— 测试执行阶段

6. **示例测试用例结构**：
   - 包含头文件 `#include <gtest/gtest.h>`
   - 使用 `TEST(HelloTest, BasicAssertions)` 宏定义测试
   - 演示两类断言：`EXPECT_STRNE`（字符串不等）与 `EXPECT_EQ`（数值等）

---

## 【关键机制与数据】

**原文: 配置到执行的完整数据流**

```
CMakeLists.txt 编写
    ↓
FetchContent_Declare + FetchContent_MakeAvailable
    ↓ (下载 googletest 仓库 zip 到构建目录)
include(GoogleTest) → gtest_discover_tests(hello_test)
    ↓ (注册测试到 ctest)
cmake -S . -B build  → cmake --build build  → ctest
```

**原文: 实测运行输出数据**

| 指标 | 原文数值 |
|------|---------|
| 测试名称 | `HelloTest.BasicAssertions` |
| 单测试耗时 | `0.00 sec` |
| 测试通过率 | `100% tests passed, 0 tests failed out of 1` |
| 总测试时间（real） | `0.01 sec` |
| 编译器示例 | GNU 10.2.1 |

**原文: 工作原理说明**

- `FetchContent_MakeAvailable(googletest)` 在配置阶段执行下载与子项目构建，等价于将 GoogleTest 作为子目录嵌入主项目编译。
- `GTest::gtest_main` 是 GoogleTest 提供的**带 main 入口的链接目标**，使用它可省略自行编写测试程序入口。
- `gtest_discover_tests()` 在**构建时**（而非运行时）枚举二进制中的测试用例并生成 CTest 测试条目，从而支持通过 `ctest -R` 按名过滤、`-j` 并行等高级特性。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文末"Next steps"段落及正文内嵌链接，本文档与以下文档/模块存在直接上下游关系：

| 关联文档 | 关系性质 | 关联内容 |
|---------|---------|---------|
| `quickstart-bazel.md` | **平行替代方案** | 项目若使用 Bazel 而非 CMake，应跳转至该文档 |
| `platforms.md` | **前置依赖** | 提供 GoogleTest 支持的平台兼容性矩阵，决定能否运行本教程 |
| `primer.md#assertions` | **断言机制深挖** | 本教程仅演示 `EXPECT_STRNE`/`EXPECT_EQ`，完整断言体系见 Primer 锚点 |
| `primer.md` | **进阶入口** | "Next steps"明确指引读者学习如何编写更复杂的测试 |
| `samples.md` | **示例代码库** | 提供 GoogleTest 各特性的实际用例（含本教程未覆盖的功能） |
| `FetchContent` (CMake 官方模块) | **构建机制依赖** | 决定依赖下载与嵌入方式 |
| `GoogleTest` (CMake 官方模块) | **测试发现机制依赖** | 提供 `gtest_discover_tests` 等辅助函数 |
| `GTest::gtest_main` (target) | **链接目标** | 提供预置 main 函数，避免重复样板代码 |

---

## 【使用方法】

**原文完整配置流程**：

1. **创建项目目录**：
   ```
   $ mkdir my_project && cd my_project
   ```

2. **编写 `CMakeLists.txt`**（完整原文内容）：
   ```cmake
   cmake_minimum_required(VERSION 3.14)
   project(my_project)
   set(CMAKE_CXX_STANDARD 17)
   set(CMAKE_CXX_STANDARD_REQUIRED ON)
   include(FetchContent)
   FetchContent_Declare(
     googletest
     URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
   )
   set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
   FetchContent_MakeAvailable(googletest)
   ```

3. **编写测试源文件 `hello_test.cc`**（完整原文内容）：
   ```cpp
   #include <gtest/gtest.h>
   TEST(HelloTest, BasicAssertions) {
     EXPECT_STRNE("hello", "world");
     EXPECT_EQ(7 * 6, 42);
   }
   ```

4. **在 `CMakeLists.txt` 末尾追加**：
   ```cmake
   enable_testing()
   add_executable(hello_test hello_test.cc)
   target_link_libraries(hello_test GTest::gtest_main)
   include(GoogleTest)
   gtest_discover_tests(hello_test)
   ```

5. **执行命令链**（原文逐字保留）：
   ```
   cmake -S . -B build
   cmake --build build
   cd build && ctest
   ```

**关键配置项说明（原文出现）**：

- `03597a01ee50ed33e9dfd640b249b4be3799d395` —— 文档建议**频繁更新**该哈希以指向最新版本（原文："we recommend updating the hash often to point to the latest version"）。
- `gtest_force_shared_crt` —— Windows 专用配置，防止子项目覆盖父项目的编译器/链接器设置。
