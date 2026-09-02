# Chapter 4: Matching Payload with Transform Operations

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/transform/Ch4.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/transform/Ch4.md

# 一体化深度解读: MLIR Transform Dialect Ch4 - Matching Payload with Transform Operations

---

## 【定位】

本篇文档解决的是 **Transform Dialect 脚本在调用时必须依赖外部机制 (C++ 代码或 pass 参数) 来关联 payload 操作的痛点**, 通过引入 `match` 操作和命名序列 (`named_sequence`) + `collect_matching` 组合子, 在 Transform Dialect 内部自洽地完成 payload 操作的自动匹配, 消除了 C++ 接口与 Transform 接口双重操作的开销。

---

## 【技术要点】

1. **Match 操作的本质定义**: Match 操作是 Transform 操作的子集, 具有两条额外保证 —— **不修改 payload IR**, 且当其操作数 (payload 操作句柄) 不满足期望属性 (操作名、操作数类型等) 时 **产生 silenceable failure**。

2. **核心组合子 `transform.collect_matching`**: 该操作以命名序列形式组织匹配逻辑, 在 payload 根操作下搜索匹配的子操作; 若命名序列产生 silenceable failure 则**静默** (失败消息转发到 debug 流), 若成功则将其结果附加到当前操作的结果中。

3. **命名序列与模块属性**: 包含命名序列的模块必须携带 `transform.with_named_sequence` 属性以启用 verification; 入口点 `@__transform_main` 接收唯一的 `!transform.any_op` 参数 (通常为 pass 根操作)。

4. **三类命名序列角色**:
   - **入口序列**: `@__transform_main`, 调度 collect_matching 与重写;
   - **匹配序列** (matcher sequence): 如 `@match_elemwise`、`@match_matmul`、`@match_matmul_elemwise`, 嵌套操作全部成功才视为匹配成功, yield 出匹配结果;
   - **重写序列** (rewriter sequence): 如 `@print_elemwise`、`@print_matmul`, 接收匹配到的句柄执行实际变换。

5. **链式匹配机制 (`get_producer_of_operand`)**: 通过 `transform.get_producer_of_operand %op[0]` 沿 use-def 链向上回溯, 获取某操作第 N 个操作数的定义者句柄, 从而实现 **从 use-def 链末端 (ReLU) → 中间 (add) → 源头 (matmul) 的逆向链式匹配**。

6. **关键替换关系**: Ch1 中需用 `--transform-interpreter` 的 `bind-first-extra-to-ops=linalg.matmul bind-second-extra-to-ops=linalg.elemwise_binary` 两个 pass 参数手工关联句柄, Ch4 中则完全去掉这些 flag, 仅需 `mlir-opt --transform-interpreter`; Ch1 脚本中只需将 `%arg1` 替换为 `%matmul`、`%arg2` 替换为 `%elemwise` 即可复用。

---

## 【关键机制与数据】

**匹配与重写的两阶段流水线** (基于命名序列):

```
[Entry: @__transform_main]
        │
        ├──> transform.collect_matching @match_elemwise in %root
        │       │
        │       └──> [Matcher Sequence: @match_elemwise]
        │               ├── transform.match.operation_name %entry
        │               │       ["linalg.elemwise_binary"]
        │               └── transform.yield %entry
        │
        ├──> transform.collect_matching @match_matmul in %root
        │       │
        │       └──> [Matcher Sequence: @match_matmul]
        │               ├── transform.match.operation_name %entry
        │               │       ["linalg.matmul"]
        │               └── transform.yield %entry
        │
        ├──> transform.include @print_elemwise failures(propagate) (%elemwise)
        ├──> transform.include @print_matmul   failures(propagate) (%matmul)
        └──> transform.yield
```

**链式匹配的逆向 use-def 回溯** (核心新机制, 对应 `@match_matmul_elemwise`):

| 步骤 | 操作 | 含义 |
|---|---|---|
| 1 | `transform.match.operation_name %last ["linalg.elemwise_binary"]` | 末端操作必须是 `linalg.elemwise_binary` |
| 2 | `%middle = transform.get_producer_of_operand %last[0]` | 取 `%last` 第 0 个操作数的定义者 |
| 3 | `transform.match.operation_name %middle ["linalg.elemwise_binary"]` | 中间操作也必须是 `linalg.elemwise_binary` |
| 4 | `%matmul = transform.get_producer_of_operand %middle[0]` | 再次回溯一层 |
| 5 | `transform.match.operation_name %matmul ["linalg.matmul"]` | 源头必须是 `linalg.matmul` |
| 6 | `transform.yield %matmul, %middle, %last` | 分别 yield matmul/中间 elemwise/末端 elemwise 三个句柄 |

> 原文明确说明方向选择: *"It starts matching from the last operation in the use-def chain and goes back because each operand (use) has exactly one definition."*

**失败信号流**:
- **Silenceable failure** (来自 `match.operation_name` 检查失败): 被 `collect_matching` 静默并转发到 debug 流;
- **Propagated failure** (`failures(propagate)` 在 `transform.include` 中): 直接向上传播。

**Debug 调试输出样例** (原文摘录):
```
[transform-matcher] matching %0 = linalg.matmul ins(%arg0, %arg1 : tensor<512x512xf32>, tensor<512x512xf32>) outs(%arg3 : tensor<512x512xf32>) -> tensor<512x512xf32> @0x5622eee08410
[transform-matcher] matcher match_elemwise failed: wrong operation name
```
这表明 `match_elemwise` 在遍历到 `linalg.matmul` 时因操作名不匹配 (期望 `linalg.elemwise_binary`) 而失败。

**匹配粒度的局限性** (原文明确指出):
> *"The matcher above remains naive as it matches all operations of the certain kind under the payload root. These operations may or may not be related, and may, for example, belong to different functions."*

即朴素匹配无法区分不同函数或同一函数内的多组同类操作, 这正是引入链式匹配 (`@match_matmul_elemwise`) 的动机。

---

## 【表格解读】

**原文无表格**。

(原文中所有结构化信息均通过 MLIR 代码示例呈现, 没有任何 markdown 表格、参数表、性能对比表或配置表。)

---

## 【公式解读】

**原文无公式**。

(原文中不存在任何数学公式、LaTeX 表达式或伪代码公式。仅包含 MLIR 操作语法和类型签名。)

---

## 【关联】

| 关联对象 | 关系说明 |
|---|---|
| **Ch1 (Chaining Transformations with Handles)** | 直接前驱章节; Ch4 用 match 机制替代了 Ch1 中 `bind-first-extra-to-ops=linalg.matmul bind-second-extra-to-ops=linalg.elemwise_binary` 这两个 pass 参数的手工句柄关联, Ch1 脚本仅做 `%arg1` → `%matmul`、`%arg2` → `%elemwise` 的变量替换即可在 Ch4 框架下复用 |
| **`mlir/test/Examples/transform/Ch4`** (持续集成测试目录) | 本章所有 MLIR 文件的持续测试位置, 文档首行即给出该路径作为权威参考 |
| **linalg.matmul / linalg.elemwise_binary** | payload IR 中的被匹配操作; 链式匹配模板要求 matmul 的结果被一个 elemwise_binary 消费, 该 elemwise_binary 的第一个操作数又必须来自前一个 elemwise_binary (形成 matmul → add → max_signed 的 use-def 链) |
| **Transform Dialect Interpreter Pass** (`--transform-interpreter`) | 执行入口; 接收 root operation 后调用 `@__transform_main` 命名序列 |
| **`transform.with_named_sequence` 模块属性** | 启用命名序列 verification 的强制属性, 缺失则命名序列无法被合法解析 |
| **`failures(propagate)` 修饰符** | 在 `transform.include` 中控制失败传播策略 —— 与 `collect_matching` 的 silenceable failure 静默机制形成对比 |
| **Debug 子系统** (`-debug-only=transform-matcher`) | 提供匹配过程的细粒度可观测性, 输出 silenceable failure 消息 |

---

## 【使用方法】

**(一) 启用模块验证 (强制)**:
```mlir
module @transforms attributes { transform.with_named_sequence } { ... }
```

**(二) 执行命令**:
```bash
mlir-opt --transform-interpreter <input.mlir>
```
相比 Ch1, **不再需要** `bind-first-extra-to-ops` / `bind-second-extra-to-ops` 等参数。

**(三) 调试匹配过程**:
```bash
mlir-opt --transform-interpreter -debug-only=transform-matcher <input.mlir>
```
仅在 debug 构建中可用, 会将所有 silenceable failure 消息打印到 debug 流。

**(四) 核心 transform 操作清单** (按本文出现顺序):

| 操作 | 作用 |
|---|---|
| `transform.named_sequence` | 定义可复用的命名序列 (匹配序列 / 重写序列 / 入口序列) |
| `transform.collect_mating @name in %root` | 在根操作下搜索匹配 `@name` 命名序列的 payload 操作 |
| `transform.match.operation_name %op ["..."]` | 检查操作名是否匹配 |
| `transform.get_producer_of_operand %op[N]` | 取操作第 N 个操作数的定义者句柄 |
| `transform.include @name failures(propagate) (%h)` | 调用另一命名序列, 可指定失败传播策略 |
| `transform.debug.emit_remark_at %op, "msg"` | 在指定操作位置发射 remark |
| `transform.yield` / `transform.yield %v` | 命名序列结束, 可选地返回值 |

**(五) 原文未涉及的方面**: 
- 自定义属性匹配 (如匹配 `binary_fn<add>` 而非 `binary_fn<max_signed>` 的 elemwise_binary) 在原文中未给出具体语法;
- 多结果命名序列返回值的精确使用模式 (文中 `%match_matmul_elemwise` 末尾被截断, yield 的三值如何被 collect_matching 接收未完整展示);
- 性能数据/基准测试 —— 原文未涉及任何量化性能指标。
