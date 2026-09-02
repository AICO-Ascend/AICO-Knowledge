# AscendStorageRewrite Pass 设计文档

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_storage_rewrite_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_storage_rewrite_design.md

# AscendStorageRewrite Pass 设计文档 — 一体化深度解读

---

## 【定位】

本篇文档描述 TileLang-Ascend 将 TVM 原生 `StorageRewrite` Pass 收编为自有 `AscendStorageRewrite` 的设计：解决在 Ascend 纯 vector 算子上原生复用策略按"物理位宽兼容即可复用"导致的"不同 dtype/不同语义的临时变量被错误规划到同一 backing storage"问题，同时在 NPU 平台关闭高风险 allocation reuse、保留 `tl.local_var_init` 注解透传与 `PointerValueTypeRewrite` 等仍然必要的 IR 重写职责。

---

## 【技术要点】

1. **Pass 来源**：实现迁移自 TVM commit `c2921fd`，接入关键变更是 commit `508db7cffd776aa20d8f9ba821cdcf8634d978db`。文档声明不重写原生算法，只解释 TileLang-Ascend 的改动。

2. **流水线接入位置**：在 `tilelang/engine/phase.py` 第 L100 行附近，将通用 `tir.transform.StorageRewrite()` 替换为 `tilelang.transform.AscendStorageRewrite(is_npu=check_npu_availability())`。该 Pass 处于 `FlattenBuffer` 之后、`UnrollLoop` 之前（第 L97–L101 行）。

3. **Bug 触发机制**：`FindAlloc()` 在"已有 allocation 大于等于当前申请容量"的复用路径中，默认只检查 attach scope、storage scope 与 `bits_offset` 是否能被当前元素位宽整除，并未强制 base dtype 一致。`reuse_require_exact_matched_dtype` 仅在显式开启时才额外要求 dtype 精确匹配（第 L1081 行）。因此 `fp16` 旧 allocation 可被 `fp32/int32` 新变量复用。

4. **NPU 平台策略**：在 `src/transform/ascend_storage_rewrite.cc` 第 L1930–L1932 行，NPU 目标下直接设置 `enable_reuse = false;`，关闭基于 free list 的常规 allocation reuse，阻断错误复用来源。

5. **注解透传**：第 L1935–L1938 行从 PrimFunc attrs 读取 `tl.local_var_init`，第 L664 行的 `MakeAllocateAnnotations()` 把它重新挂回新生成的 `Allocate` 上，确保初始化语义不丢。

6. **保留职责**：
   - `InplaceOpVerifier` 检测发生在 `FindAlloc()` 之前（第 L959–L979 行），所以即使关闭 `enable_reuse`，安全的 `dst[index] = f(src[index])` 模式仍可复用源 `StorageEntry`。
   - `PointerValueTypeRewrite()`（第 L1953 行）继续执行 buffer/pointer 元素类型与 shape 的向量化修正。
   - `VisitBufferAccess()`、`VisitExpr_(VarNode)`、`VisitExpr_(CallNode)`（第 L457–L530 行）统一处理 buffer remap、索引、`tvm_access_ptr`。

---

## 【关键机制与数据】

**工作原理（原生算法骨架，原文 L20–L22）**：
1. 线性化访问序列，分析每个临时 buffer 的 live range；
2. 对生命周期不重叠的 allocation 尝试复用同一块 backing storage；
3. 在需要时执行地址重映射和指针/Buffer 类型修正。

**Bug 数据流（纯 vector 错误复用，原文 L33–L48）**：
- 触发条件：同一 attach scope + storage scope + live range 不重叠 + 后者空间需求落入前者复用匹配区间。
- 复用条件（`FindAlloc()`，原文 L36–L41）：attach scope 一致、storage scope 一致、`bits_offset` 可被当前元素位宽整除；只有 `reuse_require_exact_matched_dtype` 显式开启时才要求 dtype 精确匹配。
- 冲突本质（原文 L46–L48）：原生按"物理位宽兼容"复用 vs Ascend 纯 vector 路径要求"变量类型语义稳定"。

**Bit 容量示例数据（原文 L70–L73）**：
- `temp_fp16` allocation：256 × 16 = 4096 bits；
- `temp_fp32` allocation：128 × 32 = 4096 bits。
- 二者 bit 容量相等，恰好落入"已有 allocation 大于等于当前申请容量"的复用路径。

**入口控制流（原文 L100–L106 流程图）**：`FlattenBuffer 后的 PrimFunc` → `AscendStorageRewrite 入口` → 判断目标平台是否 NPU → 是则关闭 `enable_reuse`，否则保留原生 reuse 策略 → 进入 `StoragePlanRewriter` → 注解透传与地址重写 → `PointerValueTypeRewrite` → 输出 `PrimFunc`。

**修改后处理逻辑（原文 L116–L120）**：
1. 入口阶段读取 `merge_static_smem`、目标平台、`tl.local_var_init`（第 L1906–L1938 行）；
2. 若 NPU，则关闭 `enable_reuse`（第 L1930–L1932 行）；
3. 在新 `Allocate` 上重挂 `tl.local_var_init`（第 L664 行 `MakeAllocateAnnotations`）；
4. 继续执行 `PointerValueTypeRewrite()`（第 L1953 行）。

**性能数据**：原文未涉及。该文档关注功能正确性与 IR 语义保持，未提供 benchmark / 加速比 / 内存节省等性能数字。

---

## 【表格解读】

原文无表格。文档中存在的唯一结构化表达是一个 Mermaid 流程图（"整体设计"一节，描述从 `FlattenBuffer` 到 `PointerValueTypeRewrite` 的 Pass 入口分流），并非参数/性能/配置类的表格。该流程图已在【关键机制与数据】中以文字形式还原。

---

## 【公式解读】

原文无标准数学公式，但有两处位宽计算等价于"bit 容量 = 元素数 × 单元素 bit 宽"的形式，原文逐字给出：

1. **原文逐字保留**：`temp_fp16 的 allocation 大小是 256 * 16 = 4096 bits`

   - 符号含义：
     - `256`：第一段循环长度（`for i in T.serial(0, 256)`），也是 `temp_fp16` buffer 的元素个数；
     - `16`：dtype `float16` 的位宽（bit 宽）；
     - `4096 bits`：该 allocation 的总物理位容量，等于 256 × 16。

2. **原文逐字保留**：`temp_fp32 的 allocation 大小是 128 * 32 = 4096 bits`

   - 符号含义：
     - `128`：第二段循环长度（`for i in T.serial(0, 128)`），也是 `temp_fp32` buffer 的元素个数；
     - `32`：dtype `float32` 的位宽（bit 宽）；
     - `4096 bits`：该 allocation 的总物理位容量，等于 128 × 32。

这两条算式被作者用作论证：当 `FindAlloc()` 按"已有 allocation bit 容量 ≥ 当前申请 bit 容量"的分支选择复用候选时，`temp_fp16` 与 `temp_fp32` 的位容量恰好相等（4096 bits = 4096 bits），完全满足复用前置条件，从而命中原文所描述的"按物理位宽兼容即可复用"的高风险路径。这并非设计目标，而是反例所需的关键数值证据。

---

## 【关联】

文档明确涉及的上下游 Pass 与模块（在文末"内部链接"标注为"无"的情况下，下列关系均为文档正文中以源文件路径/行号形式给出的外部 GitHub 链接，整理如下）：

- **上游 Pass — `FlattenBuffer`**：`AscendStorageRewrite` 在流水线中位于其之后（`tilelang/engine/phase.py` 第 L97 行）。它把 buffer 的多维访问展平，是 storage rewrite 进行 live range 与地址重写的前提。

- **下游 Pass — `UnrollLoop`**：`AscendStorageRewrite` 位于其之前（`tilelang/engine/phase.py` 第 L101 行）。即先完成 storage/inplace 重写与指针类型修正，再做循环展开。

- **Pass 注册与暴露入口**：
  - Python FFI 暴露：`tilelang/transform/__init__.py` 第 L482 行新增 `AscendStorageRewrite(is_npu: bool = False)`；
  - C++ 注册：`src/transform/ascend_storage_rewrite.cc` 第 L1960 行注册 `tl.transform.AscendStorageRewrite`。

- **NPU 平台能力探测**：`tilelang/engine/phase.py` 第 L100 行通过 `check_npu_availability()` 决定 `is_npu` 取值，进而决定是否在 Pass 内关闭 `enable_reuse`。该探测函数本身未被本文档展开。

- **TVM 原生 Pass 算法骨架**：`StoragePlanRewriter`、`InplaceOpVerifier`（第 L959–L979 行）、`FindAlloc()`（第 L1034、L1081 行）、`MakeAllocateAnnotations()`（第 L664 行）、`PointerValueTypeRewrite()`（第 L1953 行）、`VisitBufferAccess()`/`VisitExpr_(VarNode)`/`VisitExpr_(CallNode)`（第 L457–L530 行）均继承自 TVM 原生实现，本文档把它们作为被收编的"既有模块"引用，不重述其内部算法。

- **Ascend 特有语义注解 — `tl.local_var_init`**：由 PrimFunc attr 携带，在 Pass 入口（第 L1935–L1938 行）读取、在新 `Allocate` 上（第 L664 行 `MakeAllocateAnnotations`）回写，是 Ascend 后端识别"局部变量是否需要初始化"的关键信号。其具体语义与后端消费方文档未在本文档中展开。

- **原生配置开关 — `merge_static_smem`、`reuse_require_exact_matched_dtype`**：在 Pass 入口（第 L1906–L1938 行附近）被读取。`reuse_require_exact_matched_dtype` 在原文中被明确指出"只有显式开启时才要求 dtype 精确匹配"，是触发纯 vector 错误复用的关键开关之一。

---

## 【使用方法】

1. **Pass 调用入口（Python 流水线侧）**：
   - 文件：`tilelang/engine/phase.py`
   - 替换方式（原文 L97–L101 上下文）：将 `tir.transform.StorageRewrite()` 替换为
     `tilelang.transform.AscendStorageRewrite(is_npu=check_npu_availability())`。
   - 含义：`is_npu` 由平台探测函数决定，命中 NPU 时 Pass 自动关闭 allocation reuse。

2. **Python API 暴露（外部调用方）**：
   - 文件：`tilelang/transform/__init__.py` 第 L482 行；
   - 接口签名：`AscendStorageRewrite(is_npu: bool = False)`；
   - C++ 注册名：`tl.transform.AscendStorageRewrite`（`src/transform/ascend_storage_rewrite.cc` 第 L1960 行）。

3. **NPU 平台策略开关**：
   - 文件：`src/transform/ascend_storage_rewrite.cc` 第 L1930–L1932 行；
   - 行为：当 `is_npu=true` 时，入口直接设置 `enable_reuse = false;`，关闭基于 free list 的常规 allocation reuse。
   - 同时保留：`InplaceOpVerifier` 触发的安全 inplace 复用、`tl.local_var_init` 注解透传、`PointerValueTypeRewrite()`。

4. **注解透传配置**：
   - 文件：`src/transform/ascend_storage_rewrite.cc` 第 L1935–L1938 行（读取 PrimFunc attr）、第 L664 行（`MakeAllocateAnnotations` 写回新 `Allocate`）；
   - 不需要用户额外传参，由 Pass 自动从 PrimFunc attrs 收集并在新生成的 `Allocate` 上重挂。

5. **配置项/命令行开关**：原文未涉及。本文档未列出 CLI 命令、环境变量或 `PassInstrument` 级别的开关；`merge_static_smem`、`reuse_require_exact_matched_dtype` 等原生开关被读取，但其调用与覆盖方式未被本文档进一步说明。
