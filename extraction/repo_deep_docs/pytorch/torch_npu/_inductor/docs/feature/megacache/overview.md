# MegaCache特性介绍

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/megacache/overview.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/megacache/overview.md

# MegaCache 特性文档深度解读

---

## 【定位】

MegaCache 是面向 `torch.compile` 编译场景的端到端缓存复用能力，将 PyTorch 编译过程中产生的多级缓存（PRECOMPILE / PGO / AOT_AUTOGRAD / INDUCTOR / AUTOTUNE）统一序列化并持久化，从而消除模型冷启动阶段重复执行图捕获、动态图分析、代码生成、Kernel 编译与 Autotune 带来的耗时。

---

## 【技术要点】

1. **两个核心接口**：`torch.compiler.save_cache_artifacts()`（导出）与 `torch.compiler.load_cache_artifacts()`（加载），二者承担 MegaCache 的序列化导出与反序列化注入。
2. **五大缓存类型覆盖**：统一保存与恢复 PRECOMPILE、PGO、AOT_AUTOGRAD、INDUCTOR、AUTOTUNE 五类缓存。
3. **持久化与跨进程/跨机复用**：缓存以二进制 artifact 形式保存，可在满足"硬件型号及软件编译环境一致"的条件下在不同进程乃至机器间传递复用。
4. **动态 Shape 与 Catlass Kernel 缓存复用**：支持动态 Shape 场景下的编译缓存复用，同时纳入 Catlass Kernel 相关编译缓存。
5. **返回结构**：`save_cache_artifacts()` 返回 `(artifact_bytes, cache_info)` 元组；若当前进程无可导出缓存则返回 `None`；`cache_info` 内部按 `inductor` / `aot_autograd` / `autotune` / `precompile` 等分类列举 Artifact Key。
6. **使用约束**：暂不支持 CppWrapper（CppWrapper 会单独保存相关二进制文件，尚未纳入 MegaCache 制品打包范围）。

---

## 【关键机制与数据】

**工作流程（生成与保存阶段）**：原文以 `torch.sin(x) + x` 的 `Model` 为例演示流程——将模型迁移到 NPU 设备（`.npu()`），调用 `torch.compile(model)` 完成编译，使用代表性输入 Shape（`torch.randn(1024, device="npu")`）完成 warm-up 后调用 `save_cache_artifacts()`；返回值为 `(artifact_bytes, cache_info)`，`artifact_bytes` 写入文件 `CACHE_FILE = "megacache_artifacts.bin"`。

**工作流程（加载与使用阶段）**：在新进程/新机器上先读取二进制缓存文件，调用 `load_cache_artifacts(f.read())` 将序列化 Artifact 恢复到对应的编译缓存中；之后**仍需正常调用 `torch.compile`**，由编译链路按原有缓存查询机制判断是否命中。也就是说，加载缓存并非绕过 `torch.compile`，而是让查询阶段命中预先生成的 artifact。

**缓存信息结构（原文 JSON 示例）**：

```json
{
  "artifacts": {
    "inductor":      ["fa5fwpqwtyezsgbqlsfxsvvrcnct4fsexnqjfwuvmyawzomjfsoj"],
    "aot_autograd":  ["a4qzwifxbq5hxx335cg6inm5nnerbioysxdlz4ssceshq5aylm5l"],
    "autotune":      ["yi/8d4a35b42a081de7bb7d107ae87118262b3e7d539e4712b138e6925aefde5ba4.best_config", "..."],
    "precompile":    ["63aed6eacc3c99d2c4dba4bfb80334da1d105563d98bd58ec6da23290fad66c7"]
  }
}
```

**关键数字**：示例输入维度为 `1024`；Artifact Key 以哈希字符串形式呈现（`inductor` 与 `aot_autograd` 为典型 56 字符 SHA-like 标识，`autotune` Key 形如 `<hash>.best_config`，`precompile` Key 为 64 字符十六进制哈希）。原文未提供具体缓存命中耗时或冷启动加速比等性能数据。

---

## 【表格解读】

原文无表格。

（文档中仅含一段 JSON 形式的缓存信息示例，属于数据结构示例而非表格，因此不进行表格逐行还原。）

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档将 MegaCache 定位于 `torch.compile` 编译链路之上，并明确涉及以下关联模块与上下文：

- **上游编译框架**：`torch.compile` 是使用入口，所有缓存复用都建立在已编译产物之上。
- **同层多级缓存**：PRECOMPILE、PGO、AOT_AUTOGRAD、INDUCTOR、AUTOTUNE 五类缓存在 MegaCache 中被统一管理，意味着 MegaCache 不再孤立处理单一层级缓存，而是要确保这些层级间的协同命中。
- **动态 Shape 编译**：MegaCache 将动态 Shape 场景的编译缓存纳入复用范围，呼应 PyTorch 在动态 Shape 场景下的实际诉求。
- **Catlass Kernel**：在 INDUCTOR 编译链路内，会生成面向昇腾硬件的 Catlass Kernel，MegaCache 将其编译缓存也纳入打包范围。
- **硬件与软件一致性约束**：缓存复用要求硬件型号、软件编译环境一致；当前文档明示支持的设备为 **Atlas A5 系列产品**。
- **未覆盖范围**：CppWrapper 单独保存相关二进制文件，目前未纳入 MegaCache 制品打包范围，构成当前的边界。

文档文末未提供内部链接（标注为"无"）。

---

## 【使用方法】

**阶段一：生成并保存缓存**

1. 正常使用 `torch.compile(model)` 编译模型。
2. 使用具有代表性的输入 Shape 对模型进行预热（如 `torch.randn(1024, device="npu")` 触发首次编译）。
3. 调用 `torch.compiler.save_cache_artifacts()` 获取 `(artifact_bytes, cache_info)`。
4. 将 `artifact_bytes` 写入文件（如 `megacache_artifacts.bin`）。
5. 若需启用 experimental 的 precompile 缓存，需配置环境变量：
   ```bash
   export TORCH_CACHING_PRECOMPILE=1
   ```

**阶段二：加载并使用缓存**

1. 在新进程/新机器上读取已保存的二进制缓存文件。
2. 调用 `torch.compiler.load_cache_artifacts(artifact_bytes)` 将序列化 Artifact 恢复到对应编译缓存。
3. 按正常方式调用 `torch.compile(model)` 并运行模型，编译链路会按原有缓存查询机制判断是否命中。

**设备要求**：Atlas A5 系列产品。

**当前不支持项**：CppWrapper 模式。
