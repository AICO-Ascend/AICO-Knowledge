# 代码仓卡片 · pytorch

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/Ascend/pytorch.git |
| 分支 / HEAD | `master` @ `4798e98d2110` (2026-09-01) |
| 最新 tag | `v26.2.0-beta.1-pytorch2.13.0` |
| 版本候选 |
  - git_tag: `v26.2.0-beta.1-pytorch2.13.0`
| 文件数 / md 文档 / 图片 | 2776 / 552 / 103 |
| 语言分布 | {"Python": 1477, "Markdown": 552, "C/C++ hdr": 244, "C++": 236, "Shell": 24, "YAML": 10} |
| 备注 | 作为 Ascend for PyTorch 社区的核心组件，TorchNPU 是昇腾专为 PyTorch 打造的深度学习适配插件，使 PyTorch 框架能够直 |

## 1. 定位 (LLM)

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

| 顶层路径 | 文件数 |
|---|---|
| `CMakeLists.txt` | 文件 |
| `COMPATIBILITY.en.md` | 文件 |
| `COMPATIBILITY.md` | 文件 |
| `CONTRIBUTING.en.md` | 文件 |
| `CONTRIBUTING.md` | 文件 |
| `LICENSE` | 文件 |
| `OWNERS` | 文件 |
| `README.md` | 文件 |
| `README.zh.md` | 文件 |
| `SECURITYNOTE.en.md` | 文件 |
| `SECURITYNOTE.md` | 文件 |
| `SUPPORT.en.md` | 文件 |
| `SUPPORT.md` | 文件 |
| `Third_Party_Open_Source_Software_Notice` | 文件 |
| `benchmarks/` | 61 |
| `build_libtorch_npu.py` | 文件 |
| `ci/` | 18 |
| `cmake` | 文件 |

## 3. 功能逻辑 · 特性地图 (机械层: 42 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| (其他) | 42 | AOTInductor、AOTI 特性介绍、CATLASS_EPILOGUE_FUSION （同社区CUTLASS_EPILOGUE_FUSION）、TORCHINDUCTOR_CATLASS_ENABLED_OPS （同社区TORCHINDUCTOR_CUTLASS_ENABLED_OPS）、TORCHINDUCTOR_MAX_AUTOTUNE （同社区）、TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS （同社区）、TORCHINDUCTOR_NPU_CATLASS_DIR （同社区TORCHINDUCTOR_CUTLASS_DIR）、TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING （同社区） … |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

## 5. 版本与演进

  - 版本说明
  - 版本配套说明
  - 产品版本信息
  - 相关产品版本配套说明
  - 版本兼容性说明
  - 更新说明
  - 新增特性
  - 删除特性
  - 接口变更说明
  - Ascend 950DT非兼容变更说明
  - 已解决问题
  - 遗留问题

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| api | 328 |
| doc | 141 |
| feature | 42 |
| readme | 23 |
| overview | 14 |
| faq | 2 |
| guide | 2 |
| changelog | 1 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/pytorch/ (553 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
