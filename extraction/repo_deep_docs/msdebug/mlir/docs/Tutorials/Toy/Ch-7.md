# Chapter 7: Adding a Composite Type to Toy

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/Toy/Ch-7.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/Toy/Ch-7.md

# Ch-7.md 一体化深度解读

## 【定位】
本篇文档解决「Toy 语言/MLIR 中缺少复合类型」问题——通过在 Toy 前端语法中新增 `struct` 关键字、并对应地在 MLIR 中自定义 `StructType` (含存储类、Type 类、ODS 暴露、parse/print 钩子),使 MLIR 能表达并识别 Toy 的复合结构类型,衔接此前 [Ch-6](Ch-6.md) 已打通的端到端 Toy→LLVM IR 流程。

## 【技术要点】
1. **Toy 源码语法**:用 `struct <Name> { var a; var b; … }` 定义;使用 `Name` (而非 `var`) 作为变量/形参类型;成员访问使用 `.` 操作符;值可用 `{ init1, init2, … }` 形式的 composite initializer 初始化,且元素可嵌套先前定义的 struct。
2. **MLIR 端 Type 设计原则**:MLIR 无现成类型可复用,因此自定义为「未命名字段容器」,只存元素类型列表(`elementTypes`),结构名称仅供 Toy AST 使用,不进入 MLIR 表示。
3. **存储类 `StructTypeStorage` 必须派生自 `mlir::TypeStorage`**,且:
   - `using KeyTy = llvm::ArrayRef<mlir::Type>;` (按结构进行 uniquing)
   - 需提供 `operator==(const KeyTy&)`、`static llvm::hash_code hashKey(const KeyTy&)`、`static KeyTy getKey(...)`、`static StructTypeStorage* construct(TypeStorageAllocator&, const KeyTy&)`。
   - `construct` 中所有动态分配必须经由 `TypeStorageAllocator` (例如 `allocator.copyInto(key)`、`allocator.allocate<StructTypeStorage>()`)。
4. **Type 类 `StructType` 采用 CRTP**:继承 `mlir::Type::TypeBase<StructType, mlir::Type, StructTypeStorage>`,三个模板参数分别对应「具体子类 `StructType`」「基类 `mlir::Type`」「存储类 `StructTypeStorage`」。
5. **构造入口约束**:`StructType::get(llvm::ArrayRef<mlir::Type>)` 内有 `assert(!elementTypes.empty() && "expected at least 1 element type");` —— struct 至少 1 个元素;并通过 `Base::get(ctx, elementTypes)` 由 `MLIRContext` 完成 uniquing。
6. **Dialect 注册**:在 `ToyDialect::initialize()` 中调用 `addTypes<StructType>()`;原文强调「注册类型时,存储类的定义必须可见」。
7. **ODS 暴露**:`def Toy_StructType : DialectType<Toy_Dialect, CPred<"$_self.isa<StructType>()">, "Toy struct type">;`,并用 `def Toy_Type : AnyTypeOf<[F64Tensor, Toy_StructType]>;` 把新类型纳入 Toy dialect 可用类型集合。

## 【关键机制与数据】
- **Uniquing 工作原理**(原文):`Type` 对象是值类型(value-typed),内部包装一个 `TypeStorage`,在 `MLIRContext` 范围内被 uniquing;构造 `Type` 即构造并 uniquing 一个存储实例。Sentinel 类(如 `index` 类型)无附加数据时直接使用默认 `TypeStorage`,无需自派生。
- **KeyTy 的角色**(原文):「提供 storage 实例的接口,uniquing 时使用」;本例按 elementTypes 进行结构型 uniquing。
- **动态内存归属**(原文):`construct` 中「*所有*必要的动态分配必须使用给定的 allocator」。
- **CRTP 三参数语义**(原文,逐字):「All derived types in MLIR must inherit from the CRTP class 'Type::TypeBase'. It takes as template parameters the concrete type (StructType), the base class to use (Type), and the storage class (StructTypeStorage).」
- **`getImpl()` 作用**(原文):「returns a pointer to the internal storage instance」,是访问 `elementTypes` 字段的入口。
- **ODS 谓词**(原文):通过 `CPred<"$_self.isa<StructType>()">` 在生成期判定 `$_self` 是否为 `StructType`。
- 原文未提供任何性能数字/benchmark/复杂度数据。

## 【表格解读】
**原文无表格。**(文档中有一处 `tablegen` 代码块用于定义 `Toy_StructType` 与 `Toy_Type`,但其语义是 ODS 定义语句而非参数/性能/配置表格,因此不进行表格还原。)

## 【公式解读】
**原文无公式。**(文中出现的均为 C++ 与 TableGen 代码,无 LaTeX 或伪代码形式的公式;涉及的「key == elementTypes」比较与「`llvm::hash_value(key)`」哈希计算均为表达式,不是公式。)

## 【关联】
- **[Ch-6.md](Ch-6.md)**:上一章,负责 Toy→LLVM IR 端到端编译流程;Ch-7 在此基础上为 Toy 引入复合类型,使更丰富的 Toy 程序可被翻译。
- **[Ch-2.md](Ch-2.md)**:Ch-7 中关于 `Type` 类的「value-typed + 内部 `TypeStorage`」论述即源自 Ch-2 的铺垫;Ch-7 是其具体落地示例。
- **[../../LangRef.md/#type-system](../../LangRef.md/#type-system)**:MLIR 通用类型系统的权威定义,`Type` 抽象与 uniquing 机制以此为基础。
- **[../../Dialects/Builtin.md/#indextype](../../Dialects/Builtin.md/#indextype)**:作为「无附加数据、无需存储类」的 singleton 类型范例,与 Ch-7 的 `StructType` 形成对照。
- **[../../LangRef.md/#dialect-types](../../LangRef.md/#dialect-types)**:Dialect 自定义类型在 LangRef 中的总体规则说明,与 Ch-7 的「Toy dialect 自定义 `StructType`」实践对应。
- **[../../DefiningDialects/AttributesAndTypes.md](../../DefiningDialects/AttributesAndTypes.md)**:正规定义 Dialect 中 Attributes 与 Types 的指南,Ch-7 的「`Type::TypeBase` CRTP 三参数」以及「`addTypes<>()` 注册」是其子集应用。
- **[Ch-3.md](Ch-3.md)** 与 **[../../Dialects/Builtin.md/#arrayattr](../../Dialects/Builtin.md/#arrayattr)**:出现在文档内部链接列表中,但在正文中未被显式讨论,推测作为 MLIR 中处理"列表型数据"(`ArrayRef`/`ArrayAttr`)的参考,与 `KeyTy = llvm::ArrayRef<mlir::Type>` 的存储形态相关。
- **`ToyDialect::initialize()`**:Ch-7 的注册入口,与后续章节的操作/类型注册机制共享同一初始化钩子。
- **下游**(文档末尾被截断):解析与打印 `.mlir` 的支持 — 通过 override `parse…` (原文在 "overriding the `parse" 处截断,需结合后续章节或示例代码 `examples/toy/Ch7/mlir/MLIRGen.cpp` 补全)。

## 【使用方法】
- **Toy 源码侧**:在 `.toy` 文件中使用 `struct <Name> { var <field>; … }` 声明,字段可为先前定义的 struct 或基本变量;以 `{ init1, init2, … }` 复合初始化器实例化;以 `.<field>` 读取字段;以 `<Name>` 作为变量/形参类型。
- **Dialect 注册侧**:在 `ToyDialect::initialize()` 内追加 `addTypes<StructType>();`(原文:必须保证 `StructTypeStorage` 的定义在该调用点之前可见)。
- **构造接口**:在 C++ 中通过 `StructType::get(llvm::ArrayRef<mlir::Type>)` 获得(原文:至少 1 个元素),通过 `getElementTypes()` / `getNumElementTypes()` 读取。
- **ODS 侧**:在 Toy 的 `Types.td`(或等价 ODS 文件)中放入:
  ```tablegen
  def Toy_StructType :
      DialectType<Toy_Dialect, CPred<"$_self.isa<StructType>()">,
                  "Toy struct type">;
  def Toy_Type : AnyTypeOf<[F64Tensor, Toy_StructType]>;
  ```
  以便在后续 operation 定义中像 `Tensor`/`MemRef` 一样直接使用 `Toy_StructType`。
- **解析/打印 `.mlir`**:原文指明需 override `parse…`(原文在 `parse` 处截断,具体函数名与签名未给出;实际启用方式以 `examples/toy/Ch7/mlir/MLIRGen.cpp` 及后续章节为准)——原文未涉及完整命令/选项。
