# Quickstart: Building with Bazel

> 仓 `gperftools` · 路径 `vendor/googletest/docs/quickstart-bazel.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/gperftools/vendor/googletest/docs/quickstart-bazel.md

# 深度解读: vendor/googletest/docs/quickstart-bazel.md

## 【定位】
一篇面向**首次使用 GoogleTest + Bazel** 用户的入门教程,目标是让用户在单一 Bazel workspace 内完成依赖声明、`hello_test.cc` 编写、`cc_test` 构建与运行的全链路打通,产出第一个可执行的测试二进制。

---

## 【技术要点】

1. **前置条件 (硬性约束)**:
   - 操作系统兼容 Linux / macOS / Windows 三家。
   - C++ 编译器必须**至少支持 C++17**。
   - 构建系统必须 **Bazel 7.0 或更高**——GoogleTest 团队将其列为推荐构建系统。

2. **Workspace 与依赖管理**:
   - Bazel workspace 是一个目录,顶层须有名为 `MODULE.bazel` 的文本文件(可空,可声明外部依赖)。
   - **自 Bazel 7.0 起**,推荐通过 **[Bazel Central Registry](https://registry.bazel.build/modules/googletest)** 消费 GoogleTest,不再用旧的 `WORKSPACE` 方式。
   - 在 `MODULE.bazel` 中声明:`bazel_dep(name = "googletest", version = "1.17.0")`(原文明确推荐选取该 registry 上"最新可用版本",此处示例即为 1.17.0)。

3. **示例测试源码 (hello_test.cc)**:
   - 包含头文件 `#include <gtest/gtest.h>`。
   - 用宏 `TEST(HelloTest, BasicAssertions)` 定义一个测试用例。
   - 使用两个**断言 (assertion)**:
     - `EXPECT_STRNE("hello", "world")`:期望两个字符串不相等。
     - `EXPECT_EQ(7 * 6, 42)`:期望两个整数相等。

4. **`BUILD` 文件的 `cc_test` 规则**:
   - `name = "hello_test"`、`size = "small"`、`srcs = ["hello_test.cc"]`。
   - **`deps`** 列表包含两个外部 target:
     - `@googletest//:gtest`:GoogleTest 库本体。
     - `@googletest//:gtest_main`:GoogleTest 提供的 `main()` 函数入口(实际由 `gmock_main.cc` 提供)。

5. **构建与运行命令**:
   - 命令:`bazel test --cxxopt=-std=c++17 --test_output=all //:hello_test`
   - `--cxxopt=-std=c++17` 用于 Clang/GCC;MSVC 等价物为 `--cxxopt=/std:c++17`(原文以"callout note"形式标注)。
   - `--test_output=all` 让 Bazel 把测试的标准输出回显出来。

6. **平台差异提示**:
   - Unix shell 提示符 (`$`) 与 Windows 命令行在命令层面是等价的(原文 callout 注明)。
   - 详细语言版本矩阵详见 `platforms.md`(原文链接)。

---

## 【关键机制与数据】

**工作原理(原文给出的因果链路)**:

```
MODULE.bazel (声明 bazel_dep)
        │
        ▼
Bazel 7.0+ 从 Bazel Central Registry 拉取 googletest 1.17.0
        │
        ▼
BUILD 文件 cc_test 引用 @googletest//:gtest 与 gtest_main
        │
        ▼
bazel test --cxxopt=-std=c++17 --test_output=all //:hello_test
        │
        ▼
链接生成可执行测试二进制,运行 HelloTest.BasicAssertions
```

**原文给出的执行期数据(逐字保留)**:

| 维度 | 原文数值 |
|---|---|
| 加载的 packages | 26 |
| 配置的 targets | 362 |
| Elapsed time | 4.190s |
| Critical Path | 3.05s |
| 进程数 | 27(internal 8 + linux-sandbox 19) |
| total actions | 27 |
| 测试用例 PASSED 耗时 | 0.1s |
| 测试用例本体耗时 | 0 ms |
| 测试套件运行总耗时 | 0 ms total |

测试输出中可观察到**两段日志**:
- 第一次:`//:hello_test up-to-date: bazel-bin/hello_test`(缓存命中,只跑测试)。
- 第二次:`INFO: Build completed successfully, 27 total actions`(完整构建信息回显)。

---

## 【表格解读】
**原文无表格。**

(注:虽然执行日志里出现了若干数值,但它们散布在 `bazel test` 的输出段落中,并非结构化表格形式。)

---

## 【公式解读】
**原文无公式。**

---

## 【关联】

原文通过文末与文内链接,串起以下**上下游文档**,构成本教程的完整学习路径:

| 链接(原文标注) | 关联角色 | 在本文中的作用 |
|---|---|---|
| `platforms.md` | 平台兼容性矩阵 | 解答"我的 OS / 编译器版本是否受支持",引用两次(前置条件 + C++ 标准说明) |
| `primer.md#assertions` | GoogleTest 断言字典 | 解释 `EXPECT_STRNE`、`EXPECT_EQ` 的语义,是 `hello_test.cc` 断言的知识源头 |
| `primer.md` | GoogleTest 入门 Primer | 文末"Next steps"第一项,推荐读者下一步系统学习如何编写测试 |
| `samples.md` | 示例代码合集 | 文末"Next steps"第二项,展示更丰富的 GoogleTest 特性用法 |

外部链接(非仓内):
- `https://bazel.build/install`:Bazel 安装指南。
- `https://registry.bazel.build/modules/googletest`:Bazel Central Registry 上的 GoogleTest 版本索引。
- `https://docs.bazel.build/versions/main/tutorial/cpp.html`:Bazel C++ 教程(讲解 `BUILD` 写法)。

模块依赖关系链可总结为:
**本文** → 依赖 `platforms.md`(前置) → 通过 `bazel_dep` 拉取外部 `@googletest//` → 在 `BUILD` 中以 `cc_test` 形式消费 → 跳转到 `primer.md` / `samples.md` 进一步学习。

---

## 【使用方法】

**Step 1 — 创建 workspace 与声明依赖(原文命令)**:
```
$ mkdir my_workspace && cd my_workspace
```
在根目录创建 `MODULE.bazel`,内容为:
```
bazel_dep(name = "googletest", version = "1.17.0")
```

**Step 2 — 编写被测代码**:在 `my_workspace/` 下创建 `hello_test.cc`,包含 `<gtest/gtest.h>` 与 `TEST(HelloTest, BasicAssertions)` 宏。

**Step 3 — 编写 `BUILD` 文件**:
```
cc_test(
    name = "hello_test",
    size = "small",
    srcs = ["hello_test.cc"],
    deps = [
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
```

**Step 4 — 构建并运行(原文命令)**:
```
$ bazel test --cxxopt=-std=c++17 --test_output=all //:hello_test
```
MSVC 平台需替换为 `--cxxopt=/std:c++17`(原文 note 明确给出)。

**配置项摘要**:
- `--cxxopt`:传递给 C++ 编译器的选项(用于指定 C++ 标准)。
- `--test_output=all`:让 Bazel 流式输出测试运行时 stdout/stderr。
- `//:hello_test`:Bazel target 标签,指向 workspace 根下名为 `hello_test` 的 target。

**Next steps(原文给出的后续入口)**:
1. 阅读 `primer.md` 学习如何编写简单测试。
2. 查看 `samples.md` 学习更多 GoogleTest 特性用法。
3. 若需验证平台/语言标准是否被支持,回查 `platforms.md`。
