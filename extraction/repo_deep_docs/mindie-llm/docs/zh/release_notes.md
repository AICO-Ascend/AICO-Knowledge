# 版本说明书

> 仓 `mindie-llm` · 路径 `docs/zh/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/release_notes.md

# 深度解读：MindIE LLM 3.1.0 版本说明书

## 【定位】

本篇文档是 MindIE LLM（昇腾自研大模型推理引擎）**v3.1.0 正式版本**的发布说明（changelog），系统说明该版本的**配套组件关系、兼容性矩阵、新增/修改/删除特性、接口变更、未来日落（sunset）计划、升级影响与漏洞修补**，用于指引用户正确选型、升级与规避兼容性风险。

---

## 【技术要点】

1. **产品版本与维护周期**：MindIE LLM 3.1.0 为正式版本，维护周期为**三个月**。
2. **配套版本基线**：CANN 9.0.1、MindCluster 26.0.0、Ascend Extension for PyTorch 26.0.0、iMaster CCAE V100R026C10SPC100；强调"各组件需要配套使用，请勿跨版本混用"。
3. **AclGraph 后端引入**：基于 AclGraph 支持 DeepSeek-V3.2 基本功能与性能优化；`config.json` 中的 `backendType` 新增支持 `"torch"` 字段，用于指定使用 AclGraph 后端。
4. **量化叠加能力**：Qwen3 系列模型支持 **LoRA + int8 量化叠加**。
5. **算子级性能优化**：
   - DeepSeek-V3.2 Decode 阶段使用 Triton 算子 `rope_forward_triton_siso` 替代原 `npu_rotary_mul`，降低 RoPE 计算开销。
   - 采样 Top-K/Top-P 改用**自定义 NPU 算子**，替代 PyTorch 软件 `softmax + sort`，降低 TPOT。
   - PluginManager 新增**异步 D2H（Device-to-Host）拷贝机制**，采样输出通过独立 NPU Stream 异步搬移到 Host，减少推理主路径阻塞。
6. **PD 混部新增约束**：Prefix Cache、SplitFuse 与 DP（数据并行，**dp>1**）**不可同时开启**；PD 分离场景不受此限制。
7. **2027 年 3 月日落预告**：run 包部署方式、Torch 2.1.0、abi0 软件包、W4A16 量化、ModelTest/Benchmark 工具（归一至 AISBench），以及一组指定模型（含 MiniCPM 系列、Qwen/1.5/2 系列、ChatGLM2/3 系列、Llama3.2、llava-1.5/1.6 等）。
8. **CVE 修复**：覆盖 Transformers（CVE-2023-6730、CVE-2023-7018、CVE-2024-12720，均通过升级至 ≥4.36/≥4.48.0 解决）、Requests（CVE-2024-47081，依赖升级至 ≥2.32.4）以及 CPython tarfile 相关漏洞。

---

## 【关键机制与数据】

- **原文：AclGraph 后端路径**：`config.json` 中 `backendType` 新增 `"torch"` 字段以启用 AclGraph 后端，与 DeepSeek-V3.2 的基本功能/性能优化直接挂钩。
- **原文：算子替换**：`npu_rotary_mul` → `rope_forward_triton_siso`，作用域为 DeepSeek-V3.2 的 **Decode 阶段**。
- **原文：采样优化路径**：原 PyTorch `softmax + sort` → 自定义 NPU 算子实现 Top-K/Top-P，目标是**降低 TPOT**（per-output-token 时延）。
- **原文：异步 D2H 路径**：PluginManager 引入异步 D2H 拷贝；采样输出经由"独立 NPU Stream"搬移到 Host，避免与推理主路径串行阻塞。
- **原文：PD 混部冲突域**：Prefix Cache、SplitFuse、DP（dp>1）三者互斥；PD 分离场景不受限。
- **原文：升级对业务的影响**："软件版本升级过程中会导致业务中断"；对网络通信无影响。
- **原文：漏洞修补清单（节选）**：见下表"漏洞修补列表"逐字还原部分。
- **注意**：原文 CVE 表在 CPython tarfile 行被截断（"0 至 \<3.8.20；3.9.0 至 \<3"），本解读不补充未给出的内容。

---

## 【表格解读】

### 表格 A：产品版本信息（逐字还原）

| 产品名称 | 产品版本 | 版本类型 | 维护周期 |
| --- | --- | --- | --- |
| MindIE LLM | 3.1.0 | 正式版本 | 三个月 |

**逐行解读**：
- **产品名称 = MindIE LLM**：与路径名一致，定位为"大模型推理引擎"。
- **产品版本 = 3.1.0**：本次 changelog 的主体版本。
- **版本类型 = 正式版本**：非 RC/Beta，建议生产直接采用。
- **维护周期 = 三个月**：暗示 bug 修复/安全补丁窗口；与下方 2027 年日落计划无关——日落属于"特性退役"，而非本次版本的维护终止。

---

### 表格 B：相关产品版本配套说明（逐字还原）

| 产品名称 | 版本 |
| --- | --- |
| CANN | 9.0.1 |
| MindCluster | 26.0.0 |
| Ascend Extension for PyTorch | 26.0.0 |
| CCAE | iMaster CCAE V100R026C10SPC100 |

**逐行解读**：
- **CANN 9.0.1**：昇腾异构计算架构，为推理引擎的底层算子/运行时依赖。
- **MindCluster 26.0.0**：集群管理与调度组件（26.x 系列）。
- **Ascend Extension for PyTorch 26.0.0**：PyTorch 的昇腾扩展，与 MindCluster 版本号同步。
- **CCAE V100R026C10SPC100**：iMaster 智能运维/集群管理组件的特定 R026C10SPC100 补丁包。

---

### 表格 C：MindIE LLM 与 CANN 版本兼容性矩阵（逐字还原）

| MindIE LLM 版本 | CANN 9.1.0 | CANN 9.0.1 | CANN 9.0.0 | CANN 8.5.1 | CANN 8.5.0 |
| --- | --- | --- | --- | --- | --- |
| 3.1.0 | Y | Y | Y | / | / |
| 3.0.0 | / | / | Y | Y | Y |
| 2.3.0 | / | / | / | / | Y |

**逐行解读**：
- **3.1.0 行**：覆盖 CANN 9.0.x 与 9.1.0；不再支持 8.5.x（即 3.1.0 放弃了 CANN 8.x 的兼容性）。
- **3.0.0 行**：覆盖 CANN 9.0.0 与 8.5.x，是 8.5.x 用户升 3.0.0 的兼容入口。
- **2.3.0 行**：仅与 CANN 8.5.0 兼容，是 8.5.0 老用户的最后一个支持版本。
- **演进规律**：MindIE LLM 每次大版本均向前兼容一个 CANN 主版本；本次 3.1.0 完成了"CANN 8.x → CANN 9.x"的代际切换。

---

### 表格 D：MindIE LLM 与 MindCluster 版本兼容性矩阵（逐字还原）

| MindIE LLM 版本 | MindCluster 26.1.0 | MindCluster 26.0.0 | MindCluster 7.3.0 |
| --- | --- | --- | --- |
| 3.1.0 | Y | Y | Y |
| 3.0.0 | / | Y | Y |
| 2.3.0 | / | / | Y |

**逐行解读**：
- **3.1.0 行**：同时兼容 MindCluster 26.x 新版（26.0/26.1）与 7.3.0 长尾旧版，呈现"宽兼容"策略。
- **3.0.0 行**：不接 26.1.0，仅 26.0.0 与 7.3.0。
- **2.3.0 行**：仅 7.3.0，标志 MindCluster 7.3.0 是 LTS 基线。

---

### 表格 E：MindIE LLM 与 iMaster CCAE 版本兼容性矩阵（逐字还原）

| MindIE LLM 版本 | iMaster CCAE V100R026C10SPC100 | iMaster CCAE V100R026C00SPC010 | iMaster CCAE V100R025C30SPC100 |
| --- | --- | --- | --- |
| 3.1.0 | Y | Y | Y |
| 3.0.0 | / | Y | Y |
| 2.3.0 | / | / | Y |

**逐行解读**：
- **3.1.0 行**：覆盖 R026C10SPC100（默认配套）、R026C00SPC010 与 R025C30SPC100，向下兼容两个补丁代际。
- **3.0.0 行**：未接 R026C10SPC100（最新补丁），覆盖 R026C00/R025C30。
- **2.3.0 行**：仅 R025C30SPC100，与 MindCluster 表呈现一致的"老版本收口到老补丁"模式。

---

### 表格 F：v3.1.0 新增特性（逐字还原）

| 编号 | 特性 | 具体内容 |
| --- | --- | --- |
| 1 | 功能 | 基于 AclGraph，支持 DeepSeek-V3.2 基本功能及性能优化。 |
| 1 | 功能 | Qwen3 系列模型支持 LoRA+int8 量化叠加。 |
| 2 | 性能提升 | DeepSeek-V3.2 Decode 阶段使用 Triton RoPE 算子（rope_forward_triton_siso）替代原有 npu_rotary_mul，降低 RoPE 计算开销。 |
| 2 | 性能提升 | 采样 Top-K/Top-P 使用自定义 NPU 算子实现，替代 PyTorch 软件 softmax+sort 实现，降低 TPOT。 |
| 2 | 性能提升 | PluginManager 新增异步 D2H（Device-to-Host）拷贝机制，采样输出通过独立 NPU Stream 异步搬移到 Host，减少推理主路径阻塞。 |

**逐行解读**：
- **编号 1 / 功能**：AclGraph 是 NPU 图捕获优化栈；DeepSeek-V3.2 是当前主推模型，本次以"基本功能 + 性能"双维度落地；Qwen3 的 LoRA+int8 叠加为参数高效微调与量化压缩共存提供了官方路径。
- **编号 2 / 性能提升**：
  - 第 1 条：算子替换发生在 Decode 阶段，目标是减少每 token 的 RoPE 开销。
  - 第 2 条：采样阶段把 PyTorch 软实现下沉为 NPU 算子，直接作用于 TPOT。
  - 第 3 条：把 D2H 搬移从主路径剥离，是典型的"通信-计算重叠"做法。

---

### 表格 G：日落特性（2027 年 3 月日落，逐字还原）

| 编号 | 特性 | 详细 |
| --- | --- | --- |
| 1 | 部署形态 | MindIE LLM 将不再支持基于 run 包的部署方式。Torch 2.1.0 版本将随 run 包日落。abi0 软件包将随 run 包日落。 |
| 2 | 量化 | W4A16 量化特性。 |
| 3 | 测试脚本 | ModelTest 和 Benchmark 工具将日落，归一至 AISBench 工具。 |
| 4 | 模型 | MiniCPM-1B、MiniCPM-2B、MiniCPM3-4B、Starcoder2、StableLM、yizhao、chatglm2-6b、chatglm3-6b、chatglm3-6b-32K、Qwen 系列、Qwen1.5 系列、Qwen2 系列、Qwen2 Coder、Hunyuan、Skywork、DBRX、grok-1、Llama3.2、llava-1.5、llava-1.6、Yi-VL、VITA-1.5。 |

**逐行解读**：
- **部署形态**：明确"run 包"这一历史分发渠道整体退出，Torch 2.1.0 与 abi0 软件包随之下线。
- **量化**：W4A16 被点名日落，暗示后续将以 W4A8/A16 等更细分方案取代或被 W8A8 等更主流方案替代。
- **测试脚本**：ModelTest 与 Benchmark 收口到 AISBench，体现工具链收敛策略。
- **模型**：列出 22 个模型/系列进入日落名单，多为 2023–2024 早期版本（ChatGLM2/3、Qwen1.5/2、Llama3.2、llava-1.5/1.6 等），覆盖 LLM、VLM、代码模型与多模态。

---

### 表格 H：接口变更说明（逐字还原）

| 变更类型 | 接口名称 | 变更说明 |
| --- | --- | --- |
| 修改 | backendType 支持传入 "torch" 字段 | config.json 中的 backendType 新增支持 "torch" 字段，用于指定使用 AclGraph 后端。 |

**逐行解读**：
- 唯一接口变更是 `backendType` 取值扩展：新增 `"torch"` 语义指向 AclGraph 后端，是本次 DeepSeek-V3.2 优化的入口开关。

---

### 表格 I：漏洞修补列表（逐字还原，原文在 CPython tarfile 行被截断）

| 软件名称 | 软件版本 | CVE 编号 | 实际 CVSS 得分 | 漏洞描述 | 解决版本 |
| --- | --- | --- | --- | --- | --- |
| Transformers | unspecified 至 <4.36 | CVE-2023-6730 | 0 | Deserialization of Untrusted Data in huggingface/transformers prior to 4.36. The vulnerability exists in the RagRetriever.from_pretrained method, which allows remote attackers to execute arbitrary code via a crafted pickle file during model loading. | MindIE 3.1.0 |
| Transformers | unspecified 至 <4.36 | CVE-2023-7018 | 0 | Deserialization of Untrusted Data in huggingface/transformers prior to 4.36. The vulnerability exists in the automatic loading of vocab.pkl files from remote repositories without restrictions, allowing attackers to load malicious files and achieve remote code execution. | MindIE 3.1.0 |
| Transformers | unspecified 至 <4.48.0 | CVE-2024-12720 | 0 | A Regular Expression Denial of Service (ReDoS) vulnerability was identified in huggingface/transformers, specifically in tokenization_nougat_fast.py. The post_process_single() function uses a regex exhibiting exponential time complexity under certain conditions, leading to excessive backtracking and potential application downtime. | MindIE 3.1.0 |
| Requests | < 2.32.4 | CVE-2024-47081 | 0 | Requests is a HTTP library. Due to a URL parsing issue, Requests releases prior to 2.32.4 may leak .netrc credentials to third parties for specific maliciously-crafted URLs. | MindIE 3.1.0 |
| CPython tarfile | 0 至 \<3.8.20；3.9.0 至 \<3 | — | — | （原文此处截断，未给出） | MindIE 3.1.0 |

**逐行解读**：
- **Transformers 三连**：两个反序列化漏洞（CVE-2023-6730 通过 RagRetriever，CVE-2023-7018 通过 vocab.pkl 自动加载）+ 一个 ReDoS（CVE-2024-12720，tokenization_nougat_fast.py 的 `post_process_single()` 正则回溯）。
- **Requests**：URL 解析缺陷导致 `.netrc` 凭据泄露，需 ≥2.32.4 修复。
- **CVSS 实际得分均为 0**：以原文为准（可能是官方评分口径或暂未评定的占位）。
- **CPython tarfile 行**：原文被截断，本表仅按原文已披露内容呈现，未补全。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **AclGraph ↔ DeepSeek-V3.2 ↔ `backendType="torch"`**：三者构成一条完整链路——`config.json` 的 `backendType` 切换到 `"torch"`，激活 AclGraph 后端，进而支撑 DeepSeek-V3.2 的功能与性能优化（表格 F、H 共同佐证）。
- **PluginManager 异步 D2H ↔ NPU Stream ↔ 采样算子**：PluginManager 提供的异步 D2H 通道，配合"独立 NPU Stream"与自定义 NPU Top-K/Top-P 算子，组成 Decode 阶段的"采样-搬移"重叠栈，三者同列于"性能提升"分组。
- **PD 混部约束 ↔ Prefix Cache / SplitFuse / DP**：修改特性明确三者互斥（dp>1 触发），是 Prefill-Decode 混部策略的硬约束；与"PD 分离场景不受此限制"形成互补语义。
- **日落特性 ↔ 3.0.0 release_notes**：原文给出指向 [3.0.0 release_notes 的 GitCode 链接](https://gitcode.com/Ascend/MindIE-LLM/blob/v3.0.0/docs/zh/release_notes.md#%E6%97%A5%E8%90%BD%E7%89%B9%E6%80%A7)，表明 3.1.0 日落名单是 3.0.0 日落名单的**继承延续**（按原文 "继承自 3.0.0 版本的日落特性"）。
- **配套组件关系**：CANN 9.0.1、MindCluster 26.0.0、Ascend Extension for PyTorch 26.0.0、CCAE V100R026C10SPC100 是 3.1.0 的默认基线；任何一项偏离都会落入兼容性矩阵（表格 C/D/E）的 `/`（不兼容）格。

---

## 【使用方法】

原文未给出具体的命令行/配置模板，但给出了**可被直接采用的配置变更点**：

- **启用 AclGraph 后端**（即触发 DeepSeek-V3.2 的优化路径）：在 `config.json` 中将 `backendType` 字段设置为 `"torch"`。
  - 原文依据：表格 H"接口变更说明"。
- **使用 Qwen3 系列 LoRA + int8 量化叠加**：按原文"新增特性"条目启用，无需额外命令（原文未提供配置样例）。
- **PD 混部约束使用提示**：若同时启用 Prefix Cache、SplitFuse 与 DP（dp>1），部署将被拒绝；如需 DP>1，应迁移至 PD 分离形态或关闭 Prefix Cache/SplitFuse。
- **安全修复消费方式**：升级至 MindIE 3.1.0 即可获得表格 I 列出的全部 CVE 修复；间接依赖侧需 Transformers ≥4.48.0（含 4.36 修复）与 Requests ≥2.32.4。

> 备注：除上述 `backendType="torch"` 字段外，原文未给出其他具体 CLI 命令、参数样例或完整配置文件片段。
