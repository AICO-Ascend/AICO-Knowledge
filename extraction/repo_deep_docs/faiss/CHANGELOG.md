# Changelog

> 仓 `faiss` · 路径 `CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/faiss/CHANGELOG.md

# faiss CHANGELOG.md 一体化深度解读

## 【定位】

本文档是一份覆盖三个连续版本（v1.13.0 / v1.13.1 / v1.13.2）的累积变更日志，核心围绕 **RaBitQ 量化的多比特化与 FastScan 化**、**Panorama 索引族的补全**、**Intel SVS 与 NVIDIA cuVS 的硬件加速接入**，以及序列化/构建/链接层面的杂项修复,系统性地追踪了 faiss 在量化压缩、图索引与异构加速后端三个方向上的演进。

---

## 【技术要点】

1. **RaBitQ 多比特化**: v1.13.1 引入 `nb_bits 2-9` 的多比特 RaBitQ 量化 (#4679);v1.13.2 将多比特能力分别扩展至 `IndexRaBitQFastScan` (#4721) 与 `IndexIVFRaBitQFastScan` (#4722)。
2. **Panorama 索引族补全**: 横跨三个版本依次落地 `IndexFlatPanorama` (#4694 / 配套 #4645 的 L2 变体)、`IndexIVFFlatPanorama` 序列化 (#4636) 与集成 (#4606)、`IndexHNSWFlatPanorama` 集成 (#4621) 与向后兼容序列化 (#4692),并在 v1.13.2 收官补上 `IndexRefinePanorama` (#4683)。
3. **硬件加速后端双开**: v1.13.2 同时启用 `Intel ScalableVectorSearch` (#4548, SVS binary 更新至 **v0.1.0** #4726) 与 `cuVS in Faiss` (#4729),v1.13.0 已将 cuVS 升级到 **25.10** 并以 **CUDA 12.6** 打包 (#4639)。
4. **量化性能关键优化**: v1.13.1 简化 `rabitq_simd.h` SIMD helper、采用更快的 popcount (#4573) 并简化 RaBitQ 主体逻辑以提速提召回 (#4550);v1.13.0 将 `IVFRaBitQFastScan` 查询因子从 `n*nlist` 改写为 `n*nprobe` (#4643)。
5. **可观测性与扩展接口**: 新增 `RaBitQStats` 追踪两阶段搜索过滤有效性 (#4723)、`PanoramaStats` (#4628)、`PCAMatrix balanced_bins` getter/setter (#4630),扩展 API 后缀由 `Ex` 改为 `_ex` (#4530)。
6. **工程治理与发布基线**: DINO10B 数据集入库 (#4686)、ROCm7 构建适配 (#4567)、numpy2 升级 (#4523)、clang-format-21 工作流 (#4644)、启用 `-Wunused-exception-parameter` 等编译告警 (#4730)。

---

## 【关键机制与数据】

- **查询因子访存优化**: 原文(v1.13.0 Changed 第 2 条):`Optimize IVFRaBitQFastScan query factors: n*nlist to n*nprobe (#4643)` —— 将原本与倒排桶总数相关的因子计算复杂度收敛到与查询探查桶数相关,降低单 query 计算量。
- **多比特 RaBitQ 比特区间**: 原文(v1.13.1 Added 第 2 条):`Implement multi-bit RaBitQ quantization (nb_bits 2-9) (#4679)` —— 单比特 RaBitQ 之外的连续比特支持范围。
- **SVS binary 版本**: 原文(v1.13.2 Changed 第 3 条):`Update SVS binary to v0.1.0 (#4726)`。
- **cuVS / CUDA 基线**: 原文(v1.13.0 Changed 第 1 条):`Upgrade cuVS to 25.10 and build pkg with CUDA=12.6 (#4639)`。
- **两阶段搜索统计**: 原文(v1.13.2 Added 第 1 条):`Add RaBitQStats for tracking two-stage search filtering effectiveness (#4723)` —— 为粗筛→精排两阶段管线提供命中率/通过率观测。
- **FastScan 关键修复**: 原文(v1.13.0 Fixed):`Fix IndexIVFRaBitQFastScan nprobe handling in search_with_parameters (#4629)` 与 `Fix IndexIVFRaBitQFastScan by overriding search_preassigned (#4618)` —— 暴露该实现涉及 `search_preassigned` 与 `search_with_parameters` 两条代码路径。
- **算子后端覆盖**: 原文条目同时出现 `ScalarQuantizer` 优化 (#4652)、`InvertedListScanner for IVFPQFastScan` (#4537)、`RaBitQ Fast Scan` (#4595),共同支撑向量检索的「量化→倒排扫描→图细化」三层链路。

> 原文未提供吞吐量/QPS/recall@K 等具体性能数字,故本节不臆造。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

虽然原文末尾标注"(无)"内部链接,但 changelog 文本本身高度模块化,模块间依赖可归纳如下:

- **Panorama 主线**:`PanoramaStats` (#4628) 提供统计底座 → `IndexFlatPanorama` (#4694) / `IndexFlatL2Panorama` (#4645) / `IndexIVFFlatPanorama` (#4606 + 序列化 #4636) / `IndexHNSWFlatPanorama` (#4621 + 向后兼容 #4692) / `IndexRefinePanorama` (#4683) 构成完整的"平铺→倒排→图→精修"索引谱系。
- **RaBitQ 主线**:`RaBitQ Fast Scan` (#4595) → SIMD helper + popcount 优化 (#4573 / #4550) → 多比特化 (#4679) → 扩展至 `IndexRaBitQFastScan` (#4721) 与 `IndexIVFRaBitQFastScan` (#4722, #4596) → 因子重写 (#4643) → 命名清理 (#4730),并由 `RaBitQStats` (#4723) 提供运行时观测。
- **PQ 倒排扫描增强**:`InvertedListScanner for IVFPQFastScan` (#4533 / #4537) 与 `ScalarQuantizer` 优化 (#4652) 共同服务 PQ 系列,与 FastScan 路径形成"量化编码→倒序列表扫描"的上下游关系。
- **CAGRA / cuVS / SVS 三方加速**:`Set NN Descent Metric From CAGRA Params` (#4540) 与 `Expose Remaining IVF-PQ params for CAGRA` (#4593) 暴露图索引参数 → `Enable cuVS in Faiss` (#4729) + cuVS 25.10 + CUDA 12.6 (#4639) 提供 NVIDIA 后端 → `Enable Intel ScalableVectorSearch support` (#4548) + SVS binary v0.1.0 (#4726) 提供 Intel 后端。
- **Python / 构建 / 平台治理**:cmake FindPython 升级 (#4549)、c_api CMake 文档 (#4702)、Windows c++20 编译 (#4612)、AIX 构建 (#4602, #4587)、ROCm7 构建 (#4567)、ARM64 编译 (#4611),构成多平台一致性保障,与上方的功能模块通过 wheel/so 包共同对外发布。
- **回归与序列化兼容**:`Index serialization backward compatibility test` (#4706) 与 `backwards compatible check for binary` (#4714) 是上述 Panorama/RaBitQ/PQ 索引持久化格式的"安全网",与改名 PR (#4730)、API 后缀 `_ex` (#4530) 直接挂钩。

---

## 【使用方法】

原文未涉及具体启用方式、配置项或命令。本 changelog 仅以 PR 标题形式记录变更,未提供 `cmake` 编译选项、Python 安装命令、`IndexRefinePanorama` 构造示例或 `RaBitQStats` 调用方法等使用层信息。如需了解 SVS/cuVS/RaBitQ FastScan 等特性的接入方式,需结合仓库 `INSTALL.md`(changelog 中已提及相关文档链接修复 #4724)与各 PR 的代码示例。
