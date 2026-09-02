# A Fortran feature history cheat sheet

> 仓 `msdebug` · 路径 `flang/docs/FortranFeatureHistory.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/flang/docs/FortranFeatureHistory.md

# 深度解读: flang/docs/FortranFeatureHistory.md

## 【定位】

本文档是 LLVM 项目的 flang 前端(NA, New Analyer)随附的一份 **Fortran 语言特性"作弊表"/历史年表**,以时间顺序梳理自 1957 年 IBM 704 FORTRAN 起,到 FORTRAN II/IV、FORTRAN 66/77、MIL-STD-1753、Fortran 90/95、Fortran 2003、Fortran 2008 每一代标准所引入、明确化、或被标记为废弃/移除的特性,目的是为 flang 开发者提供一份"哪个特性最早出现在哪一代"的快速对照参考。

---

## 【技术要点】

1. **源码形式演进**: 704 时代固定列宽形式(fixed form)、注释卡 / 续行卡 → Fortran 90 引入自由格式(free form)与 `!` 行内注释;固定格式在 Fortran 90 被列为废弃。
2. **类型系统逐步扩充**: INTEGER/REAL(704)→ DOUBLE PRECISION + COMPLEX(FORTRAN II)→ LOGICAL(FORTRAN IV)→ CHARACTER(FORTRAN IV/77)→ 用户派生 TYPE(90)→ KIND/LEN 参数化派生类型、FIRST/FINAL 子例程、类型绑定过程(2003)→ 内在类型作为 TYPE 参数(2008, 如 `TYPE(INTEGER)`)。
3. **数组语义分阶段放宽**:
   - FORTRAN 66: 最多 3 维,下标只允许 `C*V+K` 形式,所有下界默认为 1;
   - FORTRAN 77: 下界可任意,引入隐含形状 / 可调维;
   - Fortran 90: ALLOCATABLE / 自动数组 / 数组表达式与赋值;
   - Fortran 2003: 对可分配标量也可 ALLOCATE,赋值时自动重分配;
   - Fortran 2008: 最大维数 **15**(`Max rank now 15`),CONTIGUOUS、implied-shape(如 `INTEGER :: x(0:*) = [0, 1, 2]`)、Simply contiguous arrays。
4. **过程模型抽象层级提升**: SUBROUTINE/FUNCTION(II)→ MODULE PROCEDURE / ENTRY / alternate RETURN(IV)→ MODULE(90)→ INTERFACE 块 + 递归过程(90,FORTRAN 77 时期已作为非标准可选)→ TYPE-bound 过程 + 抽象接口 + PROCEDURE 指针(2003)→ SUBMODULE + MODULE PROCEDURE(2008)。
5. **I/O 模型逐步丰富**: 格式化/非格式化(704)→ OPEN/CLOSE/INQUIRE / 直接访问(77)→ 流访问 `OPEN(ACCESS='STREAM')`、NAMELIST、派生类型 I/O、DT 编辑符、IEEE-754 负零/无穷/NaN 的 I/O(2003)→ `OPEN(NEWUNIT=u)`、G0 编辑符、`(*(...))` 无限制重复格式项(2008);recursive I/O 在 2003 与 2008 都被提及。
6. **并行与共阵列雏形**: Fortran 2008 引入 coarray 引用与 image 控制语句、以及非并行语义的 `DO CONCURRENT`,为 2018 并行语义奠基;2003 引入 ASYNCHRONOUS 属性与 WAIT,2008 引入 `MINLOC(BACK=...)` / `MAXLOC(BACK=...)` / `FINDLOC` 用于并行归约/查找。
7. **常量与字面量**: Hollerith 常量(704,77 列为废弃)→ 引用字符串(IV)→ Unicode + `SELECTED_CHAR_KIND()`(2003)→ BOZ 常量可在 INT/REAL/CMPLX/DBLE 内置调用中使用(2003)。

---

## 【关键机制与数据】

本文档是一份**纯特性清单/历史年表**,原文不涉及数据流图、性能基准、内存布局或控制流图,故无"性能/吞吐/时延"类数据。所有"数据"都是语言层符号与约束:

- 原文: FORTRAN 66 的下标形式约束为 `C*V+K`(C、K 为整数常量,V 为变量);
- 原文: FORTRAN II 标识符上限 **6 字符**;Fortran 2003 提升至 **63 字符名 + 256 行语句**;
- 原文: Fortran 2008 数组最大 rank = **15**;同时要求 `SELECTED_INT_KIND(18)` 给出 64 位整数;
- 原文: 原始 704 的 DO 循环必须为正表达式、且最少执行 1 次(`1 trip minimum`);FORTRAN 77 引入负表达式与 0 次循环;
- 原文: 内部过程(internal procedures)从 2008 起才允许作为实参传递或赋给过程指针;
- 原文: `CALL MOVE_ALLOC(from, to)` 是 Fortran 2003 引入的移动分配内置子例程;
- 原文: `OPEN(ACCESS='STREAM')`、`OPEN(ROUND=mode)`、`OPEN(DECIMAL='COMMA'|'POINT')`、`OPEN(SIGN=)` 均为 2003 引入的连接控制选项;
- 原文: IEEE-754 负零、无穷、NaN 的 I/O 自 2003 起支持;
- 原文: `INTEGER :: x(0:*) = [0, 1, 2]` 是 Fortran 2008 的隐含形状(implied-shape)声明;
- 原文: Fortran 2008 `STOP` 语句常量被泛化(不再局限于数)。

---

## 【表格解读】

**原文无表格**。

原文全部内容为按 Fortran 版本分节的 Markdown 项目符号列表,不包含任何 markdown 表格、参数表或性能对比表。为便于阅读,可将版本演进压缩成如下派生对照(此表**非原文**,仅为辅助理解):

| 标准版本 | 年份近似 | 关键引入(选) | 关键移除/废弃(选) |
|---|---|---|---|
| IBM 704 FORTRAN | 1957 | INTEGER/REAL、DIMENSION/EQUIVALENCE、FORMAT、DO(正,1 trip) | — |
| FORTRAN II | 1958 | SUBROUTINE/FUNCTION、COMMON、DOUBLE PRECISION/COMPLEX、6 字符标识符 | — |
| FORTRAN IV | 1962 | DATA、labeled COMMON、LOGICAL、quoted string、NAMELIST、ENTRY | 移除 704 时代奇异特性 |
| FORTRAN 66 | 1966 | 可调维数组哑元(初版) | 下标仅 `C*V+K`、最多 3 维 |
| FORTRAN 77 | 1978 | `IF...END IF`、DO 含负/零次、OPEN/CLOSE/INQUIRE、CHARACTER、PARAMETER、SAVE、generic 内部名 | Hollerith、H 编辑符、overindexing、扩展范围 DO |
| MIL-STD-1753 | 1978 | `DO WHILE`、`INCLUDE`、`IMPLICIT NONE`、位操作内在函数 | — |
| Fortran 90 | 1991 | 自由格式、`!` 注释、模块、ALLOCATABLE/POINTER/TARGET、派生 TYPE、数组表达式、SELECT CASE、INTENT | 备用 RETURN、computed GO TO、statement function、固定格式 等标记废弃 |
| Fortran 95 | 1997 | FORALL、嵌套 WHERE、PURE、derived type 缺省初值、指针 → NULL() 初值 | 浮点 DO 索引、ASSIGN、assigned GO TO、PAUSE、H 编辑符等 |
| Fortran 2003 | 2004 | 参数化派生类型、PROCEDURE 指针、类型绑定过程、ENUM、ASSOCIATE、CLASS、ABSTRACT 接口、MOVE_ALLOC、IEEE I/O、流访问、ISO_FORTRAN_ENV、63-char 标识符、Unicode | — |
| Fortran 2008 | 2010 | SUBMODULE、coarray + image 控制、DO CONCURRENT、CONTIGUOUS、BLOCK、rank≤15、`SELECTED_INT_KIND(18)`、G0 编辑符、Bessel/ERF/GAMMA/HYPOT/NORM2、EXECUTE_COMMAND_LINE、recursive I/O | — |

---

## 【公式解读】

**原文无公式**。原文中仅出现**代码/语法片段**(非数学公式),列举以示区别:

- `C*V+K` — FORTRAN 66 下标约束形式(非算式约束,合法下标只能表达为"常量×变量+常量")。
- `INTEGER :: x(0:*) = [0, 1, 2]` — Fortran 2008 隐含形状数组声明语法。
- `CALL MOVE_ALLOC(from, to)` — Fortran 2003 移动分配子例程调用语法。
- `OPEN(ACCESS='STREAM')`、`OPEN(NEWUNIT=u)`、`OPEN(ROUND=mode)`、`OPEN(DECIMAL='COMMA')`、`OPEN(SIGN=)` — Fortran 2003/2008 连接单元选项语法。
- `2P[,]2E12.4`、`(*(...))` — 编辑描述符(2003 / 2008);其中 `2P[,]2E12.4` 展示了 2003 引入的 Fortran 66 风格"可选逗号"在比例因子 2P 下的 `2E12.4` 形式,逗号可有可无。
- `INTEGER(kind) :: ...`、`TYPE(INTEGER)` — Fortran 2008 类型参数化语法。
- `STOP n`、`BGE/BGT/BLE/BLT`、`DSHIFTL/DSHIFTR`、`LEADZ/POPCNT/POPPAR/TRAILZ`、`MASKL/MASKR`、`SHIFTL/SHIFTR/SHIFTA`、`MERGE_BITS`、`IALL/IANY/IPARITY`、`STORAGE_SIZE`、`NORM2`、`PARITY`、`ERF/ERFC/ERFC_SCALED/GAMMA/HYPOT/LOG_GAMMA`、`ACOSH/ASINH/ATANH`、`ATAN(x,y)`(`ATAN2` 的同义)、`FINDLOC` — Fortran 2008 引入的内在过程/过程调用语法。

---

## 【关联】

原文为"扁平年表",**未提供任何内部链接**,因此无法基于文末链接建立上下游图谱。但从特性交叉维度仍可识别以下关联:

1. **数据抽象层叠**:
   - MODULE(Fortran 90)→ SUBMODULE / MODULE PROCEDURE(Fortran 2008);
   - 派生 TYPE(90)→ 参数化派生 TYPE + 类型绑定过程 + FINAL(2003)→ 抽象接口允许 DEFERRED 方法(2003);
   - INTERFACE(90)→ GENERIC 解析规则在 2008 进一步精化("Refinement of GENERIC resolution rules on pointer/allocatable, data/proced");
   - 上述特性共同支撑 flang 中过程/类型/泛型解析器的语义检查模块。
2. **内存模型演进**:
   - COMMON / EQUIVALENCE(704/II)→ POINTER + TARGET(90)→ 自动 DEALLOCATE 作用域结束(95)→ INTENT 允许出现在 POINTER 哑元上(2003,指代指针本身而非目标)→ 2008 允许把非指针 TARGET 实参关联到 `POINTER INTENT(IN)` 哑元。
3. **I/O 子系统**:
   - 原始 FORMAT/READ/WRITE/PRINT/PUNCH(704)→ NAMELIST(IV)→ 直接访问(77)→ 流访问 / 异步 / 派生类型 I/O(2003)→ `NEWUNIT=` 与 G0(2008);IEEE-754 负零、无穷、NaN 的 I/O 与 IEEE underflow 控制(2003)在 flang runtime 中是相互依赖的支持点。
4. **并行雏形**:
   - ASYNCHRONOUS + WAIT(2003)→ coarray + image 控制 + DO CONCURRENT(2008),为后续 Fortran 2018 并行 DO CONCURRENT、teams/events 奠基。
5. **类型字面量与字面常量**:
   - BOZ(2003)、Unicode + `SELECTED_CHAR_KIND`(2003)、负零支持 `ATAN2/LOG/SQRT`(2003)三者共同影响 flang 字面量解析与字面常量求值模块。
6. **跨代"复活/正式化"**: IMPLICIT NONE(MIL-STD-1753, 1978)在 Fortran 90 正式标准化;递归(F77 非标准)在 Fortran 90 标准化;CHARACTER(IV 已出现)在 FORTRAN 77 标准化时归位;`(*(...))` 无限重复格式项(2008)是对早期 FORMAT 能力的扩展。

---

## 【使用方法】

**原文未涉及**。

本文档是说明性/历史参考材料,不涉及编译开关、命令行选项、CMake 配置、`-fxxx` 标志或 flang 驱动的使用方式。所有内容均为语言标准层面的特性罗列,既不绑定到具体编译器实现,也不绑定到任何运行时开关。
