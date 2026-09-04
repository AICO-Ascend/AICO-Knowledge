# AICO-Knowledge 知识书架设计（昇腾亲和 · 双入口）

> **v4 定稿（2026-09-04，用户拍板）**：
> ① **两个入口是两个体系**——SHELF.md 走注册表生成逻辑；AscendInfra 不复用书架逻辑，
>    是独立手工维护的可视化 HTML 页面（bookshelf/ascend_infra.html，自绘 SVG/概念卡/对照表）；
> ② AscendInfra 参考昇腾官方算子可视化平台的形态，但**不出现其名字与链接**；
> ③ SHELF.md 新增「原始出处」列——深读链接之外直链 arXiv 原文 / gitcode 仓内原始文件 / 原始网页。
> 以下为 v3 设计稿存档（生成逻辑部分仍有效，ascend_infra 的 markdown 生成方案已废止）。


> 状态：设计稿 v3（2026-09-04），未动工。
> v3 变更（用户拍板）：
> ① 书架放顶层 `bookshelf/`；
> ② 双入口 = 知识书架 + 昇腾专区，昇腾专区命名 **AscendInfra**（不叫 AscendV，避免抄袭观感；
>    AscendV 平台降级为 AscendInfra 页内引用的外部资源之一）；
> ③ 书架主线改为技术栈自上而下：**Agent → 模型/算法 → 训推框架 → 算子 → 系统软件 → 硬件/集群**；
> ④ 借鉴 InfraTech 的表格行格式（文章超链接 | 知识分类 | 备注[热度/难度/练习]）。
> 参考：InfraTech 开源项目+ AscendV 平台摸底
> （ascendv.openx.huawei.com 直接访问被网络策略拦截，依据用户下载 PDF 4 页全文提取）。

## 1. 双入口架构

```
AICO-Knowledge/
├─ bookshelf/
│  ├─ SHELF.md          入口一 · 知识书架（技术栈主线：六层自上而下 + 横向专题）
│  ├─ ascend_infra.md   入口二 · AscendInfra 昇腾专区（同一技术栈主线的昇腾全栈展开）
│  └─ CURATION.md       策展定义（导语/分级/对照关系）—— 唯一人工维护文件
└─ skills/bookshelf/
   └─ bookshelf_build.py   从三域注册表幂等生成两个入口页
```

README 顶部挂两行入口。书架不新增知识，是三域资产（论文/代码仓/网页）按技术栈的投影。

### 与既有入口的分工

| 入口 | 受众 | 组织维度 |
|---|---|---|
| README.md | 评估者 | 能力与规模 |
| extraction/index.md | LLM agent | 主题→论文 |
| extraction/MOC.md | Obsidian 探索 | 图谱聚类 |
| **bookshelf/SHELF.md** | **人类学习者** | **技术栈主线（Agent→…→硬件集群）+ 学习路径** |
| **bookshelf/ascend_infra.md** | **昇腾开发者** | **同一技术栈主线的昇腾全栈 + 外部资源（AscendV 等）引用** |

两个入口共用一条技术栈主线 —— 读者从 SHELF.md 任意一层可横跳 ascend_infra.md 对应层
（"这个算法在昇腾上怎么落"），从 ascend_infra.md 可上钻 SHELF.md 对应层（"这个算子服务的算法是什么"）。

## 2. 技术栈主线（六层，自上而下）

```
L1 Agent        智能体系统（RL 训推/工具调用/Agentic 工作流）
L2 模型/算法     架构与算法（MLA/DSA/KDA/MoE/线性注意力/投机解码/多模态）
L3 训推框架      训练框架（Megatron/MindSpeed）+ 推理框架（vLLM/SGLang/MindIE）
L4 算子          算子库与算子开发（CUTLASS/Triton/AscendC/算子全景）
L5 系统软件      驱动/运行时/编译器/通信库（CUDA·NCCL / CANN·HCCL）
L6 硬件/集群     芯片架构/服务器/超节点/集群组网（GPU / Atlas A2·A3·950DT）
```

主线逻辑：**一个 Agent 需求往下钻**——用什么模型（L2）→ 怎么训怎么推（L3）→
落在哪些算子上（L4）→ 跑在什么系统软件栈上（L5）→ 最终钉在什么硬件与集群拓扑上（L6）。
读者可以任一层进入，向上理解"为什么需要它"，向下理解"它怎么落地"。

## 3. SHELF.md 主书架结构

### 六层内容映射

| 层 | 内容来源（自有资产） | 代表条目 |
|---|---|---|
| L1 Agent | 论文域 rl 簇（R1/GRPO/DAPO/AREAL/HybridFlow/CUDA-Agent）+ repo 域 MindSpeed-RL 深读 | RL 训推共卡调度、权重同步机制 |
| L2 模型/算法 | 论文域 69 篇深读 + 19 页概念页 + 685 裁剪图 + 479 公式 | MLA/DSA/KDA 深读（挂架构裁剪图）；投机解码学习路径 EAGLE→EAGLE-3→LongSpec；MoE 簇 |
| L3 训推框架 | repo 域 MindSpeed 全家桶/vllm/vllm-ascend/MindIE 卡片 + 1719 篇深读 + web 域 vllm serve CLI 手册（312 参数）、vllm-ascend 快速上手 | fb-overlap 通信掩盖（3 图 M3 解读）、vLLM V1 调度、PD 分离 |
| L4 算子 | repo 域算子仓（triton-ascend/catlass/TensorBoost/torch_npu_ops/xllm_ops）深读 | FlashAttention 实现族、MoE dispatch/combine 算子、ChunkKdaFwd |
| L5 系统软件 | web 域 CANN 环境变量手册（商用 900/社区 910beta1，132 表行+两版一致结论）+ PyTorch NPU 2600 环境变量（22 变量） | HCCL 通信配置、图编译 DUMP、内存复用开关 |
| L6 硬件/集群 | web 域 vllm-ascend 硬件支持表 + repo 域 hccl_transfer 等 | Atlas A2/A3/950DT/300I DUO 支持矩阵、A3 超节点组网（HCCL_LOGIC_SUPERPOD_ID 原文） |

### 横向专题（InfraTech 式章节，跨层主题的学习路径）

- **投机解码专题**：EAGLE→EAGLE-3→LongSpec（L2）→ vllm serve 投机参数（L3）
- **KV Cache 专题**：Mooncake/CacheBlend（L2）→ vLLM KV 管理（L3）→ CANN 内存环境变量（L5）
- **通信与并行专题**：DualPipe/fb-overlap（L3）→ HCCL 配置（L5）→ 超节点（L6）
- **量化专题**：GPTQ/AWQ 论文（L2）→ msmodelslim 仓（L3）→ 量化算子（L4）

### 条目行格式（借鉴 InfraTech 表格制）

InfraTech 的行 = `| 📜 文件 | 📖 知识分类 | 📜 备注 |`，备注里塞 🔥 热度与练习链接。借鉴并扩展：

```markdown
| 📚 条目（超链接） | 📖 知识分类 | 🔧 层次 | 📜 备注（热度/难度/资产/昇腾亲和） |
|---|---|---|---|
| [EAGLE: 投机解码](../extraction/deep/xxx.md) | 投机解码 | L2 算法 | 🔥🔥🔥 ⚡⚡⚡ · [架构图](../extraction/assets/crops/xxx.png) · [公式](../extraction/xxx.md#关键公式) · 昇腾: vllm-ascend 实验性支持 |
| [fb-overlap 通信掩盖](../extraction/repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md) | 通信掩盖 | L3 训推框架 | 🔥🔥 ⚡⚡⚡ · [3 图 M3 解读] · 昇腾: MindSpeed 原生 |
```

- **条目**：超链接直达自有深读（不复制内容，点开即全文/图/公式）——对 InfraTech 外链知乎的差异化
- **知识分类**：InfraTech 式二级分类（Attention/推理基础/并行推理/量化…）
- **层次**：L1-L6 技术栈层标签（本书架的主线刻度）
- **备注**：🔥 热度 + ⚡ 难度（初版人工标注进 CURATION.md，禁止机械臆造）+ 资产链接（裁剪图/公式/逐字表）+ 昇腾亲和注记
- 每个分区表前有**策展导语**（学习路径建议，如"先读 EAGLE 原文再读 EAGLE-3 演进"）

### 模型卡片（InfraTech 式一行卡片，保留）

| 模型 | 架构关键词 | 入口 |
|---|---|---|
| DeepSeek V3 / V3.2 | MLA+MoE / +DSA | [论文深读](../extraction/deep/deepseek-v3-technical-report.md) · [MLA 裁剪图](../extraction/assets/crops/deepseek-v3-technical-report-fig02-mla.png) |
| GLM 5.3-Flash | KDA+DSA | 论文深读 · xllm day-0 适配时间线（repo 卡片） |

## 4. ascend_infra.md 昇腾专区（AscendInfra）

**命名说明**：AscendInfra = 昇腾 Infra 知识专区，是自有品牌；
AscendV 平台（ascendv.openx.huawei.com）作为专区引用的外部可视化资源之一出现，不冠名。

### 结构：同一技术栈主线的昇腾全栈展开（L6→L1 自下而上，贴近开发者视角）

| 层 | 已有素材（直接挂自有资产） | 外部资源引用 | 缺口（→ webs 清单反哺） |
|---|---|---|---|
| L6 硬件/集群 | Atlas A2/A3/950DT/300I DUO 支持表（web 域） | **AscendV 硬件可视化**（910_95/910B/310P 三代 AI Core 架构动画：Cube/Vec/MTE1-3/FixPipe/L0A-L0C/UB） | 达芬奇架构官方手册页 |
| L5 系统软件 | CANN 双版环境变量手册（132 表行逐字还原，**900↔910beta1 一致结论独家**）+ PyTorch NPU 22 变量 | AscendV 知识可视化（HCCL/集合通信概念） | HCCL 调优指南、HCCL vs NCCL 对照 |
| L4 算子 | triton-ascend/catlass/TensorBoost/torch_npu_ops/xllm_ops 仓深读 | **AscendV 算子可视化 + AscendC API 可视化**（数据搬运/单目/双目/排序等 API 族 + GM→L0A→L0C 通路标注）+ **精度/性能 12 步方法论 + FCodeQ FAQ** | 昇腾算子开发模型总览 |
| L3 训推框架 | MindSpeed×8 + MindIE×4 + vllm-ascend 卡片与 497 篇特性文档深读；vllm-ascend 中文快速上手（web） | — | MindIE vs vllm-ascend 选型对照 |
| L2 模型/算法 | KDA/DSA/MoE 论文深读（挂"昇腾算子需求"注记：DSA→稀疏 gather、KDA→chunkwise 线性注意力） | **AscendV 模型可视化**（DeepSeek-R1/Qwen3/Pangu 卡片） | GLM 5.3-Flash 类新模型适配指南 |
| L1 Agent | MindSpeed-RL 深读 + RL 训推共卡 | — | 昇腾 Agentic RL 实践 |

### 知识对照表（专区的核心价值，策展层人工维护）

| 概念 | 外部可视化（AscendV 等） | 本库深读/手册 | 仓实现锚点 |
|---|---|---|---|
| double buffer | AscendV 知识可视化 | MindSpeed fb-overlap 特性文档七节深读 | repos_src/mindspeed 特性实现 |
| 通信掩盖流水 | AscendV 算子运行图（MTE/Cube 流水动画） | DeepSeek-V3 DualPipe 论文深读+裁剪图 | mindspeed fb-overlap |
| 线性注意力算子 | AscendV Attention 算子全景图 | KDA/DSA 论文深读 + GLM 5.3 报告 | vllm-ascend ChunkKdaFwd 设计文档 |
| tiling 切分 | AscendV 知识可视化 tiling | CANN 环境变量 tiling 相关条目 | catlass/triton-ascend 深读 |
| 集合通信 | AscendV HCCL 概念条目 | CANN HCCL 环境变量 132 表行（超节点/重传/RDMA 默认值全保真） | hccl_transfer 仓卡片 |
| Cube/Vector 同步 | AscendV FCodeQ Q1（含代码片段） | （缺口，待抓 CANN 开发文档） | — |

### AscendV 引用风险处理

ascendv.openx.huawei.com 被本环境网络策略拦截，疑似内网/半公开平台。
ascend_v 引用一律写成「模块名 + 一句话定位 + URL」，即使链接不可点，模块名本身仍有导航价值；
读者在有权限的网络下可自行访问。不嵌入其图片/内容（版权与可达性双重考虑）。

## 5. 生成机制

```
CURATION.md (人工: 分区导语/学习路径/热度难度/昇腾亲和注记/对照表)
        │
        ▼
skills/bookshelf/bookshelf_build.py
        │  读: papers.json · repo_inventory.json · repo_deep_index.json
        │      · web_index.json · minimax_captions.json · formulas.json
        ▼
bookshelf/SHELF.md + bookshelf/ascend_infra.md   （机械层幂等重生成，策展层注入不覆盖）
```

- 双层写入（extract_phase1-overwrite 教训制度化）：条目表机械重生成，导语/路径/分级/对照注入自 CURATION.md
- 生成后死链 lint（资产文件存在性检查），死链报错不静默
- 触发：三域 ingest 后跑一次；稳定后可并入 full_pipeline 尾部可选 step
- **缺口反哺闭环**：书架暴露的缺口 → webs_download_list.txt → web 流水线入库 → 书架重刷自动挂上

## 6. 对外叙述口径

> InfraTech 是 GPU 生态的外链书架（文章在知乎）；
> AscendInfra 书架是**昇腾亲和的自有知识书架**：技术栈六层主线（Agent→模型→训推框架→算子→系统软件→硬件集群），
> 条目挂自有深读资产（点开即全文/图/公式），与 AscendV 官方可视化平台共生互链——
> 动画案例去 AscendV，论文机制/版本血缘/环境变量手册留这里。

## 7. 落地阶段

| 阶段 | 内容 | 产出 |
|---|---|---|
| **P1** | CURATION.md 骨架 + bookshelf_build.py + 两入口页从注册表生成 + 死链 lint | 书架 v1 |
| **P2** | 策展填充：导语/学习路径/热度难度/昇腾亲和注记/对照表 | 书架 v1.1 |
| **P3** | 缺口补抓（达芬奇手册/HCCL 调优/MindIE 选型 → webs 清单 → web 流水线） | 昇腾层补齐 |
| **P4** | README 挂双入口 + 记忆沉淀 + token 安全提交推送 | 闭环 |

## 8. 已拍板与遗留

已拍板：书架顶层 `bookshelf/` ✓ · 双入口（SHELF.md + ascend_infra.md）✓ ·
专区命名 AscendInfra ✓ · 技术栈主线六层（Agent→模型算法→训推框架→算子→系统软件→硬件集群）✓ ·
借鉴 InfraTech 表格行制 ✓

遗留（P2 前确认即可）：
1. 热度/难度标注量：推荐路径条目（~60 条）先标 vs 全量（~200 条）
2. 昇腾亲和注记的粒度：分区级默认+例外（推荐起步）vs 逐条目
