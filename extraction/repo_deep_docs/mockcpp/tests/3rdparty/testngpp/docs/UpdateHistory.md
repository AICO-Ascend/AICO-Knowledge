# 更新历史 #

> 仓 `mockcpp` · 路径 `tests/3rdparty/testngpp/docs/UpdateHistory.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mockcpp/tests/3rdparty/testngpp/docs/UpdateHistory.md

# testngpp 更新历史深度解读

## 【定位】
**一句话**：这是 testngpp（C++ 轻量级单元测试框架）的更新日志（changelog），按时间顺序记录其从 2010.7 至 2011.3.26 各版本的能力演进与缺陷修复。

---

## 【技术要点】

1. **内存泄露检测机制（两遍运行策略，2011.3.17）**：用例运行第二遍用于验证"第一遍报告的泄露是否稳定复现"——若第二遍无泄露则不报告，若第二遍仍有泄露才报告，从而规避 STL 容器（如 `vector`）析构时才释放内存造成的误报。

2. **内存泄露开关的三层优先级（2011.3.25）**：命令行 `-m` > Fixture `Annotation` 中 `memcheck` > TestCase `Annotation` 中 `memcheck`；具体表现为"Fixture 设置优先级低于 TestCase"（即在 Fixture 关闭后，TestCase 可单独打开）。

3. **浮点相等断言宏（2011.3.20）**：新增 `ASSERT_DBL_EQ` / `ASSERT_DBL_NE` 用于 `float` / `double` / `long double` 相等性判断，比较策略为 `fabs(a-b) < FLT_EPSILON`（**不是** `DBL_EPSILON`）。

4. **Generator 的 `-d` 参数（2010.7~11 月）**：可指定辅助 `.cpp` 文件生成目录；每个测试 `.h` 对应生成一个辅助 `.cpp`，再将多个 `.cpp` 链接为单个测试 `.dll`；同时支持基于时间戳判断的增量编译。

5. **命令行 DLL 加载（2010.7~11 月）**：支持以 `TestModule` 或 `TestModule.dll` 形式直接加载测试 DLL（此前只支持无后缀情况）。

6. **辅助 `.cpp` 文件包含使用相对路径（2010.7~11 月）**：避免测试路径含中文字符时写文件失败；新增 `STOP` / `OPEN_MEM_CHECKER` 两个旧接口被移除（2011.3.25）。

---

## 【关键机制与数据】

**两遍运行防误报机制的工作原理（原文 2011.3.17）：**
- **触发场景**：全局 `vector`（或其它 STL 容器）变量在元素被 `erase` 时并不释放底层内存，仅在容器析构时才归还内存。
- **判定逻辑**：
  - 第一遍运行 → 探测到内存泄露 → **不立即报错**，而是触发**第二次运行**。
  - 第二次运行 → 若无泄露 → 判定为"STL 延迟释放"伪泄露，**静默通过**。
  - 第二次运行 → 仍有泄露 → 判定为真实泄露，**正式报告**。
- **数据流边界**：内存泄露检查发生在 **Fixture 析构之前**，原文明确指出"暂时没有想到 fixture 析构之后检查的简单办法"。

**错误信息输出改进（原文 2010.7~11 月）：**
- 解决"只上报 SEH 异常"的不足——当异常捕获后再次抛出新异常时，原始异常信息会丢失。改进后尽可能打印出有价值的信息。

**Fixture 初始化失败统计（原文 2010.7~11 月）：**
- 此前 Fixture 构造失败时 `testngpp` 不输出任何信息；改进后会输出失败原因与统计信息。

**Generator 增量编译（原文 2010.7~11 月）：**
- 通过"判断是否需要重新生成 `.cpp` 文件"的机制，避免每次全量重生成。

**自动化编译脚本（原文 2010.7~11 月）：**
- `build.sh`：编译并运行测试用例（Linux & Cygwin）。
- `build_install.sh`：编译并安装（Linux & Cygwin）。
- Windows 版本为 PowerShell 脚本。
- 详细用法指向代码根目录的 `BuildGuide`（原文链接字段为空，但内容中明确提及）。

---

## 【表格解读】

**原文无表格。**（原文主要以时间分块 + 编号列表的形式罗列变更项，未出现参数表、对比表或配置矩阵。）

---

## 【公式解读】

**原文无标准公式**（无 LaTeX 形式），仅在 2011.3.20 条目中给出一行关键比较表达式，**逐字保留如下**：

```
fabs(a-b) < FLT_EPSILON
```

**符号含义与作用：**

| 符号 | 含义 | 作用 |
|---|---|---|
| `fabs(...)` | 浮点绝对值函数（C 标准库 `math.h`/`cmath`） | 消除 `a-b` 符号，使差异量化为非负值 |
| `a-b` | 两浮点操作数之差 | 待比较的实际偏差 |
| `< FLT_EPSILON` | 严格小于 `float` 类型的机器 epsilon | 阈值；`FLT_EPSILON` 在 float 类型下能保证 `float` 参与运算时的精度 |

**原文专门提醒**："不能用 `DBL_EPSILON`，否则有 float 参与运算时，精度达不到，就会出现 `0.7 != 0.7` 的情况。"——即当比较两端类型不一致（含 `float`）时，`DBL_EPSILON` 的阈值过大，会导致本应相等的浮点被判为不等。

---

## 【关联】

1. **与代码仓 `mockcpp` 的关系**：原文归属路径为 `tests/3rdparty/testngpp/docs/`，说明 testngpp 是 `mockcpp`（用于支持 MindStudio 等项目的 C++ 单元测试框架）所引用的**第三方测试库**，被嵌入到 `tests/3rdparty` 目录下作为测试基础设施。

2. **与构建系统**：原文中 `build.sh`、`build_install.sh`、Windows PowerShell 脚本的详细用法指向**代码根目录的 `BuildGuide`**——这是 testngpp 自身的构建指南文档，与本 changelog 形成"变更日志 + 构建说明"的互补关系。

3. **与下游使用者**：2011.3.26 标注 "Release 1.1"，意味着上述所有改进（两遍内存泄露检测、`memcheck` 开关、`-d` 参数、`TestModule.dll` 加载、`ASSERT_DBL_EQ/NE`、VS2010 支持等）共同构成了 testngpp **1.1 版本的特性集合**，是下游项目（包括 `mockcpp` 当前使用的 testngpp）所继承的能力基线。

4. **Annotation 系统耦合**：2011.3.25 引入的 `memcheck = on / off` 注解，是挂在已有的 `//@fixture(...)` / `//@test(...)` Annotation 体系上的新增字段，与原有 tags（如 `tags`）共同决定 TestCase 是否启用内存泄露检查。

5. **历史接口废弃**：2011.3.25 明确"去掉了 `STOP` / `OPEN_MEM_CHECKER` 两个接口"——表明这两个旧 API 在 1.1 Release 中已被新的 `memcheck` 注解机制取代。

---

## 【使用方法】

以下为原文中明确给出的启用方式 / 配置项 / 命令：

**1. 命令行 `-m` 选项（2011.3.25）：**
- 加 `-m` → 本次执行**不再检查内存泄露**（覆盖 Fixture/TestCase 级别的 `memcheck = on`）。
- 不加 `-m` → 默认进行内存泄露检查，是否检查取决于 Fixture/TestCase 的 `memcheck` 注解与 tags。

**2. Fixture / TestCase Annotation 中的 `memcheck` 字段（2011.3.25）：**
- `memcheck = on` → 检查内存泄露。
- `memcheck = off` → 不检查内存泄露。
- 两者均未设置 → 视为检查（默认开）。
- **优先级**：Fixture 的设置会被其下每个用例继承，但 **TestCase 的设置可覆盖 Fixture 的设置**。

原文给出的使用示例（逐字保留）：

```
//@fixture(memcheck=on)
FIXTURE(TestFixtureMemCheckOnAnnotation)
{
   TEST(fixture has been set to memcheck on, its tests all memcheck on)
   {
       char *p = new char; // should fail       
   }

   //@test(memcheck=off)
   TEST(fixture has been set to memcheck on, its test can use memcheck off to close mem leak check)
   {
       char *p = new char; // should success
   }
};
```

**3. Generator `-d` 参数（2010.7~11 月）：**
- `generator -d <目录>`：指定辅助 `.cpp` 文件输出目录；每个测试文件生成对应 `.cpp`，并链接为单个测试 `.dll`。

**4. 命令行加载测试 DLL（2010.7~11 月）：**
- `TestModule` 或 `TestModule.dll`：均作为命令行参数加载测试 DLL。

**5. 浮点相等断言（2011.3.20）：**
- 调用 `ASSERT_DBL_EQ` / `ASSERT_DBL_NE` 宏对 `float` / `double` / `long double` 进行相等性判断（比较内部使用 `fabs(a-b) < FLT_EPSILON`）。

**6. 编译与运行脚本（2010.7~11 月）：**
- Linux / Cygwin：`build.sh`（编译并运行测试用例）、`build_install.sh`（编译并安装）。
- Windows：对应的 PowerShell 脚本版本。
- 详细用法"参见代码根目录的 `BuildGuide`"（原文未提供链接，但指明文档位置）。

**7. 已废弃接口（2011.3.25）：**
- `STOP` / `OPEN_MEM_CHECKER`——已被移除，新代码不应再使用，应改用 `memcheck` Annotation。
