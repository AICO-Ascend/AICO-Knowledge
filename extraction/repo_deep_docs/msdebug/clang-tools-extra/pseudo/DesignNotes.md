# Error recovery (2022-05-07)

> 仓 `msdebug` · 路径 `clang-tools-extra/pseudo/DesignNotes.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/clang-tools-extra/pseudo/DesignNotes.md

# Error Recovery Design Document 深度解读

## 【定位】

这篇文档设计了在 GLR 解析器中**统一的错误恢复 (error recovery) 框架**,将原本被视为两类的"括号匹配恢复"与"序列元素恢复"统一为同一套机制,通过在文法规则上标注 recovery 策略、在 GSS (Graph-structured Stack) 节点死亡时触发恢复,使解析器能在不污染周围代码的前提下,将"无法解析的代码片段"包装为不透明 (opaque) 森林节点继续推进。

## 【技术要点】

1. **两类待统一场景**:序列 (sequence),如 `int x; this is absolute garbage; x++;`;括号 (bracket),如 `void foo() { this is garbage too }`。
2. **括号恢复的规则标注**:在文法规则 `{ stmt-seq }` 上加注恢复动作,形如 `{ stmt-seq [recovery] }`,可推广为 `{ stmt-seq [recovery=rbrace] }`,通过 **策略 (strategy)** 来寻找恢复点。
3. **序列恢复的规则改造**:对右递归序列 `param-list := param` / `param-list := param , param-list` 的**两条规则**都需要恢复;若希望恢复 `int x int y` 为两个参数,可抽取 `param-and-comma` 子规则供恢复操作。
4. **左/右递归选择**:作者经反思后决定**允许两条规则同时恢复**——"错误"那条恢复会产出"自取灭亡"的解析头,从而被自动淘汰。
5. **GLR 集成点**:恢复应在某高层解析的**所有变体 (variants) 都即将被放弃**时触发,具体表现为 GSS 父节点的死亡。
6. **恢复头激活策略**:最简方案是**仅在没有任何普通解析头存活时才创建恢复头**;复杂方案是记录恢复机会并在最后一个解析头死亡时选**最右端点 (rightmost endpoint)** 那一个。

## 【关键机制与数据】

### 括号恢复流程

原文:
- 若在 `{ . stmt-seq }` 处失败
- 且能找到匹配的 `}`
- 则将到该 token 为止的内容视为一个不透明 (opaque) 的、被损坏的 `stmt-seq`
- 并将解析状态推进到 `{ stmt-seq . }`

### GSS 节点 refcount 与死亡检测

原文指出:
> we need a refcount in GSS nodes so we can recognize never-reduced node death

节点死亡时,从 action 表中查其对应的恢复动作集 (该节点各项 item 的恢复动作的并集),形式为:
```
actions[State, death] = Recovery(type, matching-angle-bracket)
```

### 恢复执行步骤

原文描述:
1. 依次尝试每种策略,以死亡节点起始位置的 token (例如 `foo`) 作为输入
2. 策略返回一个**结束位置** (例如 `>`)
3. 构造一个以正确 symbol (`type`) 为根、跨越 `[start, end)` 的不透明森林节点
4. 在 Goto 表中按通常方式查到新状态,生成代表恢复后状态的 GSS 节点

### 示例: `static_cast<foo bar baz>(1)`

原文给出了 GSS 结构示意:在解析到 `bar` 时,"foo... 是类名"和"foo... 是模板 ID"两条头都将死亡,父 GSS 节点死亡即触发恢复;恢复后:
```
{expr := static_cast < type . > (expr)}
```
其注释为"`foo bar baz` is an unparseable type"。

### 恢复头激活的取舍

原文提到合法但易误判的反例:`(int *)(x)` 既是合法的强制类型转换,也可能被尝试解析成"参数为破损 expr 的函数调用";最简方案是仅在解析完全卡死时启用恢复,但原文也指出这在"错误解析比正确解析多走一点"时会脆弱。

## 【表格解读】

**原文无表格**。

(文档中出现的伪代码/ASCII 图示为 GSS 状态结构示例,非表格;语法规则如 `param-list := param` 为 BNF 风格的产生式,亦非参数表或性能对比表。)

## 【公式解读】

**原文无公式**。

(原文中出现的形式化表达仅为 EBNF 风格产生式 `compound-stmt := { stmt-seq }`、`param-list := param` 等,以及 GSS 节点 `{expr := static_cast < . type > ( expr )}` 的项集表示法,不属于数学公式;恢复动作形式 `actions[State, death] = Recovery(type, matching-angle-bracket)` 是带索引的查表伪代码,同样非数学公式。)

## 【关联】

- **GLR 解析器**:本文讨论的所有恢复机制都以 GLR 的"多解析头 + GSS"模型为基础,并依赖 GLR 自身对错误解析头的自然淘汰。
- **GSS (Graph-structured Stack)**:恢复触发点为父 GSS 节点的"死亡";恢复成功后新生成一个 GSS 节点;需要为 GSS 节点引入 **refcount** 才能识别"从未被归约"的死亡。
- **Action 表与 Goto 表**:恢复动作以 `actions[State, death]` 形式存储于 action 表中;恢复后目标状态通过 Goto 表按常规方式查出。
- **Opaque forest node (不透明森林节点)**:恢复产物的承载形式——一段无法解析但语义上需作为整体跳过的代码被封装为对应 symbol 的森林节点。
- **歧消解 (disambiguation)**:原文末尾讨论过"把所有恢复都放进解析森林,让歧消解选 broken-but-likely",这表明恢复与上层的歧消解机制之间存在取舍关系。
- **文法改造**:左递归可改写为右递归;为使恢复可操作,可能需要抽取如 `param-and-comma` 这类辅助非终结符。

(文末给出的内部链接列表为"无",故此处未引用具体锚点或文档路径。)

## 【使用方法】

**原文未涉及**。

本文为设计构思文档,讨论的是机制原理与取舍,而非启用方式、配置项或命令行。文档中出现的"配置"形式仅为**文法规则上的标注**,例如:
- `{ stmt-seq [recovery] }` — 启用括号恢复
- `{ stmt-seq [recovery=rbrace] }` — 指定具体的恢复策略(如 `rbrace`)

这些是供文法作者使用的语法标记,具体的"如何打开恢复功能、如何编译/链接、如何在 CLI 调用"的工程细节本文并未给出。
