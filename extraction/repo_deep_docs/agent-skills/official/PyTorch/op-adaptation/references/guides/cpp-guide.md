# C++ Implementation Guide

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/cpp-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/cpp-guide.md

# 深度解读：official/PyTorch/op-adaptation/references/guides/cpp-guide.md

## 【定位】

本文档是昇腾（Ascend）PyTorch op-plugin 中 **C++ 算子适配实现** 的标准化指南，规定 aclnn 算子接入 op_api 命名空间时必须遵循的函数签名、类型映射、代码结构、变体模式（`_out`/`_inplace`/多输出）、workspace 管理及约束自检流程，用于保证 C++ 实现与生成接口契约一致、产出可被下游 C-meta 阶段直接消费的标准实现。

---

## 【技术要点】

1. **函数签名强约束**：C++ 实现函数签名必须与 `build/pytorch/third_party/op-plugin/op_plugin/OpApiInterface.h` 中生成的接口完全一致，否则无法被自动注册流程识别。

2. **类型映射四规则**（原文明确列出 NOT 写法）：
   - `int[]?` → `c10::OptionalIntArrayRef`（**不能**用 `c10::optional<at::IntArrayRef>`）
   - `str` → `c10::string_view`（**不能**用 `std::string`）
   - `ScalarType?` → `c10::optional<at::ScalarType>`
   - `Tensor?` → `const c10::optional<at::Tensor>&`

3. **必含头文件**：`op_plugin/OpApiInterface.h`（aclnn 算子接口）+ `op_plugin/utils/op_api_common.h`（宏与工具）；仅当需 `DO_COMPATIBILITY` 回退时才引入 `op_plugin/AclOpsInterface.h`。

4. **实现前先查相似算子**：按类别（`*Quant*.cpp`、`*Matmul*.cpp`、`*Mm*.cpp`、`*Attention*.cpp`、`*Flash*.cpp`）或参数模式（`OptionalIntArrayRef`、`c10::string_view`、`TensorWrapper`）搜索；推荐先读 `TanhKernelNpuOpApi.cpp`（最简）、`TopKKernelNpuOpApi.cpp`（多输出）、`DynamicBlockQuantNpuOpApi.cpp`（量化 + `TensorWrapper`）。

5. **标准代码结构五步**：① `TORCH_CHECK` 校验输入 → ② 处理 optional（`has_value()` + `defined()`） → ③ `calc_output_size` 计算输出形状 → ④ `npu_preparation::apply_tensor_without_format` 创建输出张量 → ⑤ `EXEC_NPU_CMD(aclnnOperatorName, ...)` 执行。

6. **变体三件套**：`_out` 通过 `DO_COMPATIBILITY` 宏做兼容性回退后调用 `aclnnOpName`；`_`（inplace）走 `npu_operator_name_out(self, param, self)` 复用 out 逻辑；多输出用 `std::tuple<at::Tensor, at::Tensor>` 配多个 `apply_tensor_without_format`。

7. **输出尺寸/类型自定义函数**：YAML 中 `size:` 引用时必须在 `op_plugin/utils/KernelNpuOutputSize.h` 声明、`.cpp` 实现，签名形如 `OP_PLUGIN_HIDDEN c10::SmallVector<int64_t, SIZE> npu_operator_out_size(const at::Tensor&, int64_t)`；dtype 同理走 `KernelNpuOutputDtype.h/.cpp`。

8. **约束自检硬性要求**：C++ 实现完成 → 进入 C-meta 前，须对 CHECKLIST.md "Constraint Logic Checklist" 每条规则在 C++ 中找到对应 `TORCH_CHECK` 或校验逻辑；缺失必须补齐；`.md` 参数描述表中的所有使用限制都需 `TORCH_CHECK`；并在 CHECKLIST.md "Constraint Coverage Self-Check" 表的 "C++ (C-cpp)" 列打标。

---

## 【关键机制与数据】

**工作流（原文章节顺序还原）**：

- **类型契约生效路径**：YAML 描述 → 自动生成 `OpApiInterface.h` 接口 → C++ 实现签名逐字对齐 → 注册到 `op_api` 命名空间。任一环节类型不匹配（如把 `int[]?` 写成 `c10::optional<at::IntArrayRef>`）即破坏契约，原文通过加粗 "NOT" 强调这是高频踩坑点。

- **运行时执行链**：`npu_preparation::apply_tensor_without_format(output_shape, input.options())` 申请 NPU 格式输出 → `EXEC_NPU_CMD` 宏展开调用 aclnn 算子 → 返回新张量（或引用）。其中 `apply_tensor_without_format` 不强制 NPU 内部格式，与 `apply_tensor` 区分。

- **Workspace 管理（量化等大算子必备）**：先调用 `aclnnOperatorNameGetWorkspaceSize(..., &workspace_size, &executor)` 探尺寸 → 仅当 `workspace_size > 0` 时按 `dtype(at::kByte)` 申请 1 维 workspace 张量 → 再走 `EXEC_NPU_NO_FORMAT_CHECK_CMD(aclnnOperatorName, workspace, workspace_size, executor, ...)` 真正执行（该宏绕开 format 检查，适配裸 workspace 指针语义）。

- **量化自定义 dtype 桥接**：`aclDataType`（昇腾 ACL 类型） → `GetAclDataType(dst_type)` → `convert_to_scalar_type` 转为 `at::ScalarType` → 用 `c10::dtype(y_dtype)` 建张量 → 再用 `TensorWrapper{y, y_acltype}` 二次包装把 acltype 注入算子调用，使 aclnn 看到正确目标 dtype。

- **Out/Inplace 复用机制**：`_out` 版本是单一事实源，`_`（inplace）通过把 `self` 同时作为输入与输出传给 `_out` 实现（`npu_operator_name_out(self, param, self)`），避免重复实现 in-place 路径。

- **输出尺寸函数校验规则**：每个传给 `_out_size` 的 Tensor 参数**即便不直接参与形状计算**，也必须带 `TORCH_CHECK` 维度校验，原文标注原因是 "ensures bad inputs produce clear error messages rather than obscure downstream ACL errors"。

- **Constraint 自检闭环**：C++ 完成后未通过自检 → 不得进入 C-meta 阶段；这是文档强调的 "create mode only" 流程门禁。

**性能/数字类数据**：原文未提供具体的性能指标、benchmark 数据或具体数值参数（如延迟、吞吐、M 个例子数等），仅有 `SIZE`、`SIZE` 等模板占位、`int64_t`、`uint64_t` 等类型级常量，故本节不臆造任何数字。

---

## 【表格解读】

**原文无表格**。

（说明：原文采用代码块 + 加粗规则列表形式表达约束与结构，未出现任何 markdown 表格或类表格数据，故严格按指令标注"原文无表格"。）

---

## 【公式解读】

**原文无公式**。

（说明：原文不涉及数学公式、LaTeX 表达式或伪代码公式；最接近"表达式"的只有类型映射规则与 `c10::SmallVector<int64_t, SIZE>` 这类类型签名，已在【技术要点】中作为规则逐条列出。）

---

## 【关联】

文档内部链接信息原文标注为 "(无)"。可从内容中梳理出以下**文档自述的上下游/模块依赖关系**（基于原文措辞推断，非外部链接）：

- **上游契约源**：`build/pytorch/third_party/op-plugin/op_plugin/OpApiInterface.h` —— 自动生成的接口文件，C++ 实现须与之对齐。
- **同仓库参考实现**：
  - `op_plugin/ops/opapi/` 下 `TanhKernelNpuOpApi.cpp`（最简模板）
  - `op_plugin/ops/opapi/` 下 `TopKKernelNpuOpApi.cpp`（多输出参考）
  - `op_plugin/ops/opapi/` 下 `DynamicBlockQuantNpuOpApi.cpp`（量化 + `TensorWrapper` 参考）
- **配套工具/头文件**：
  - `op_plugin/utils/op_api_common.h`（宏，如 `EXEC_NPU_CMD`、`EXEC_NPU_NO_FORMAT_CHECK_CMD`、`OPS_ERROR(ErrCode::PARAM)`、`TORCH_CHECK`）
  - `op_plugin/utils/KernelNpuOutputSize.h` + `.cpp`（自定义输出尺寸）
  - `op_plugin/utils/KernelNpuOutputDtype.h` + `.cpp`（自定义输出 dtype）
  - `op_plugin/AclOpsInterface.h`（仅 `DO_COMPATIBILITY` 回退路径引入）
- **协作流程上下游**：
  - **上游**：YAML 算子描述（`size:` / `dtype:` 字段引用自定义函数）→ 生成接口
  - **下游**：C-meta 阶段（必须先完成 C++ Constraint 自检才能进入）
  - **横向**：`CHECKLIST.md` 的 "Constraint Logic Checklist" 表与 "Constraint Coverage Self-Check" 表（"C++ (C-cpp)" 列需打标）
- **关联命名空间**：`namespace op_api` 与 `at_npu::native::OpPreparation`（`npu_preparation` 别名）、`acl_op`（兼容回退命名空间）。

---

## 【使用方法】

原文直接给出的启用方式/配置/命令：

1. **启用 C++ 实现的标准引入**（在新建的 `op_plugin/ops/opapi/<OpName>KernelNpuOpApi.cpp` 顶部）：
   ```cpp
   #include "op_plugin/OpApiInterface.h"
   #include "op_plugin/utils/op_api_common.h"
   // 仅 DO_COMPATIBILITY 回退时打开：
   // #include "op_plugin/AclOpsInterface.h"
   ```

2. **实现前的检索命令模式**（原文以"Search for"形式给出，无完整 shell 命令）：
   - 类别：`Quant*.cpp` / `Matmul*.cpp` / `Mm*.cpp` / `Attention*.cpp` / `Flash*.cpp`
   - 参数模式：grep `OptionalIntArrayRef` / `c10::string_view` / `TensorWrapper`

3. **执行入口宏（按场景选用）**：
   - 标准路径：`EXEC_NPU_CMD(aclnnOperatorName, ...)`
   - Workspace 路径：`EXEC_NPU_NO_FORMAT_CHECK_CMD(aclnnOperatorName, workspace, workspace_size, executor, ...)`
   - 兼容性回退：`DO_COMPATIBILITY(aclnnOpName, acl_op::npu_operator_name_out(input, param, result));`

4. **输出张量创建**：
   - 标准：`npu_preparation::apply_tensor_without_format(output_shape, input.options())`
   - 自定义 dtype：`apply_tensor_without_format(y_shape, c10::dtype(y_dtype))`

5. **输出尺寸/dtype 自定义函数的声明与定义位置**（YAML `size:` / `dtype:` 引用时）：
   - 声明：`op_plugin/utils/KernelNpuOutputSize.h`（用宏 `OP_PLUGIN_HIDDEN`）
   - 定义：`op_plugin/utils/KernelNpuOutputSize.cpp`
   - dtype 同理：`KernelNpuOutputDtype.h` / `KernelNpuOutputDtype.cpp`

6. **流程门禁**：完成 C++ → 对照 CHECKLIST.md "Constraint Logic Checklist" 逐条搜索 `TORCH_CHECK` → 缺失项立即补齐 → 在 "C++ (C-cpp)" 列打标 → **方可进入 C-meta 阶段**（原文强调 "Create mode only"）。

7. **最佳实践指令**：在 `op_plugin/ops/opapi/` 中查找相似算子后复用模式，而非自行发明新写法。

> 备注：原文 Troubleshooting 节为空（标注 "Accumulate from cases"），未提供具体命令或排错步骤，故不补充臆造内容。
