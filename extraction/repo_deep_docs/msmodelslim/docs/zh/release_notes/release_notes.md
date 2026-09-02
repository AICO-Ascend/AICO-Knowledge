# 版本说明

> 仓 `msmodelslim` · 路径 `docs/zh/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodelslim/docs/zh/release_notes/release_notes.md

# 一体化深度解读：msModelSlim 版本说明文档

---

## 【定位】

本文档是 **msModelSlim（MindStudio-ModelSlim）量化压缩工具**的版本发布说明，描述三个版本（26.0.0.alpha02、26.0.0.alpha01、8.3.0）的产品版本信息、与 CANN/PyTorch/TorchNPU/Python/Transformers 的配套关系、whl 包下载与校验码、以及各版本新增的量化能力与模型支持清单，作为用户选择版本与环境的依据。

---

## 【技术要点】

1. **插件化基础架构**：26.0.0.alpha02 引入"通过 entry point 引入自定义 practice 目录，搭建 model_adapter 插件化能力基础"，为后续自定义模型适配器提供标准接入点。
2. **自动调优双能力**：
   - 26.0.0.alpha02 优化自动调优功能；
   - 26.0.0.alpha01 新增"量化精度反馈自动调优，可根据精度需求自动搜索最优量化配置"。
3. **量化精度方案扩展**：覆盖 **W8A8、W4A8、W8A8C8、W4A8C8** 四类精度组合，针对不同模型规模与硬件约束选取。
4. **大模型分布式量化**：26.0.0.alpha01 支持"一键量化支持多卡量化，支持分布式逐层量化，提升大模型量化效率"。
5. **多模态/混合专家量化**：覆盖 Qwen3-VL-32B-Instruct、Qwen3-VL-235B-A22B、Qwen2.5-Omni-7B、Qwen3-Omni-30B-A3B（多模态）、Qwen3.5 MOE（混合专家）、DeepSeek-V3.2/V3.2-Exp/R1-0528/V3.1、GLM-4.7/5 等典型模型。
6. **硬件约束明确化**：DeepSeek-V3.2（W8A8）与 DeepSeek-V3.2-Exp（W4A8）均标注"**单卡 64G 显存、100G 内存即可执行**"，对消费级或单卡工作站部署具有指导意义。

---

## 【关键机制与数据】

- **版本类型分层**：alpha01/alpha02 为"内测版本"，8.3.0 为"正式版本"。
- **配套关系（26.0.0.alpha 系列）**：原文明确"不依赖特定版本"CANN，PyTorch/TorchNPU/Transformers 均"与具体模型有关，请参考相关模型资料"。
- **配套关系（8.3.0）**：要求 CANN **8.2.RC1 及以上版本**。
- **Python 版本**：均支持 **Python 3.10、3.11**。
- **原文数据/参数**：见下表"关键机制参数汇总"。

| 项 | 原文数据 |
|---|---|
| DeepSeek-V3.2（W8A8）硬件 | 单卡 64G 显存、100G 内存 |
| DeepSeek-V3.2-Exp（W4A8）硬件 | 单卡 64G 显存、100G 内存 |
| whl 校验算法 | SHA256（64 位十六进制哈希值） |
| 8.3.0 依赖 CANN 下限 | 8.2.RC1 |

---

## 【表格解读】

### 表 1：产品版本信息（原文逐字还原）

| 产品名称 | 产品版本 | 版本类型 |
|---|---|---|
| msModelSlim | 26.0.0.alpha02 | 内测版本 |
| msModelSlim | 26.0.0.alpha01 | 内测版本 |
| msModelSlim | 8.3.0 | 正式版本 |

**逐行解读**：
- 第 1 行：26.0.0.alpha02 是当前最新的 alpha 内测版本，紧随 alpha01 之后。
- 第 2 行：26.0.0.alpha01 为首个公开 alpha 内测版本。
- 第 3 行：8.3.0 为正式版本（相对 alpha 系列是稳定基线）。三条记录说明文档同时维护 alpha 与正式两条演进线。

### 表 2：相关产品版本配套说明（原文逐字还原）

| msModelSlim版本 | CANN版本 | PyTorch版本 | TorchNPU版本 | Python版本 | Transformers版本 |
|---|---|---|---|---|---|
| 26.0.0.alpha02 | 不依赖特定版本 | 与具体模型有关，请参考相关模型资料 | 与具体模型有关，请参考相关模型资料 | Python 3.10、3.11 | 与具体模型有关，请参考[example](../../../example)目录下对应模型的案例说明 |
| 26.0.0.alpha01 | 不依赖特定版本 | 与具体模型有关，请参考相关模型资料 | 与具体模型有关，请参考相关模型资料 | Python 3.10、3.11 | 与具体模型有关，请参考[example](../../../example)目录下对应模型的案例说明 |
| 8.3.0 | 8.2.RC1及以上版本 | 与具体模型有关，请参考相关模型资料 | 与具体模型有关，请参考相关模型资料 | Python 3.10、3.11 | 与具体模型有关，请参考[example](../../../example)目录下对应模型的案例说明 |

**逐行解读**：
- 第 1 行：26.0.0.alpha02 在 CANN 层面松绑（不依赖特定版本），但 PyTorch/TorchNPU/Transformers 与模型绑定，需通过 example 目录查阅。
- 第 2 行：26.0.0.alpha01 配套策略与 alpha02 完全一致。
- 第 3 行：8.3.0 是唯一对 CANN 有明确下限要求的版本（≥8.2.RC1），其余依赖均通过模型级 example 文档传递。

### 表 3：whl 包获取（原文逐字还原）

| 版本 | 下载链接 | 校验码 |
|---|---|---|
| 26.0.0-alpha.2 | [msmodelslim-26.0.0a2-py3-none-any.whl](https://gitcode.com/Ascend/msmodelslim/releases/download/tag_mindstudio_26.0.0.alpha02/msmodelslim-26.0.0a2-py3-none-any.whl) | 4711edb30c4354fcb99fb69a2e0351561b013bb1298d6f54a0ee409bf979a264 |
| 26.0.0-alpha.1 | [msmodelslim-26.0.0a1-py3-none-any.whl](https://gitcode.com/Ascend/msmodelslim/releases/download/tag_MindStudio_26.0.0-alpha.1/msmodelslim-26.0.0a1-py3-none-any.whl) | 60383c42bf103cf2f78304b3b974e2dac0190f0f20706a5ef347e55855048f42 |

**逐行解读**：
- 第 1 行：26.0.0-alpha.2 的 whl 包来自 gitcode release tag `tag_mindstudio_26.0.0.alpha02`，文件名遵循 PEP 440 规范（a2 表示 alpha 2），校验码长度为 64 字符，对应 SHA256。
- 第 2 行：26.0.0-alpha.1 对应 tag `tag_MindStudio_26.0.0-alpha.1`，校验码同样为 SHA256。
- 备注：8.3.0 正式版本未在本表列出 whl 下载链接（原文未提供，仅在文末以 release 列表形式给出"更多详情"）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 example 目录的关系**：表 2 中三个版本均通过内部链接 `../../../example` 指向模型级案例说明，作为 PyTorch/TorchNPU/Transformers 版本选择与 Transformers 配套的实际查询入口；这意味着本文档不锁定具体依赖版本号，而是依赖模型示例下沉管理依赖。
- **与 release 页面的关系**：文末给出 `https://gitcode.com/Ascend/msmodelslim/releases?...` 链接，用于查阅更完整的发布历史（presetConfig 中 tags=32, release=2）。
- **版本演进关系**：
  - 8.3.0（正式版）→ 26.0.0.alpha01（内测）→ 26.0.0.alpha02（内测），alpha 系列在 CANN 依赖上做出松绑（不依赖特定版本），同时引入 entry point 插件化基础与自动调优优化。
  - DeepSeek-V3.2-Exp 模型在 8.3.0 已支持 W8A8，在 26.0.0.alpha01 升级支持 W4A8；DeepSeek-V3.2 是 alpha01 新增。
- **量化能力演进**：从 8.3.0 的 W8A8C8、W4A8C8 组合 → alpha01 的分布式逐层量化与精度反馈自动调优 → alpha02 的插件化扩展，能力逐层叠加。

---

## 【使用方法】

1. **版本选择**：若需稳定环境选 8.3.0；若需 entry point 插件化、Qwen3-Coder-480B W4A8、GLM-4.7/5 等新增能力，选 26.0.0.alpha02。
2. **环境检查（8.3.0）**：原文要求 CANN **8.2.RC1 及以上版本**；所有版本均需 **Python 3.10 或 3.11**。
3. **依赖对齐**：PyTorch/TorchNPU/Transformers 具体版本号不固定在本文档，需进入 `example` 目录查阅目标模型的 case 说明。
4. **whl 安装与校验**：通过表 3 给出的 gitcode 链接下载 whl，使用同表给出的 64 位校验码（SHA256）校验包完整性，例如：
   - `26.0.0-alpha.2` 包名 `msmodelslim-26.0.0a2-py3-none-any.whl`
   - `26.0.0-alpha.1` 包名 `msmodelslim-26.0.0a1-py3-none-any.whl`
5. **硬件准备**：运行 DeepSeek-V3.2（W8A8）与 DeepSeek-V3.2-Exp（W4A8）量化需 **单卡 64G 显存 + 100G 内存**（原文标注）。
6. **更多发布历史**：原文末尾链接 `https://gitcode.com/Ascend/msmodelslim/releases?...` 用于查阅完整 release 列表。
7. **入口方式（26.0.0.alpha02 起）**：原文未提供具体 entry point 名称或注册命令，仅说明"通过 entry point 引入自定义 practice 目录"，具体接入规范需在后续文档/代码中确认（原文未涉及）。
