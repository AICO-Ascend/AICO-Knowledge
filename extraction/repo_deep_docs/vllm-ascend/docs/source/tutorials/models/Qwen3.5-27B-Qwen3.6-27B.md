# Qwen3.5-27B & Qwen3.6-27B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3.5-27B-Qwen3.6-27B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3.5-27B-Qwen3.6-27B.md

# Qwen3.5-27B & Qwen3.6-27B 部署指南深度解读

## 【定位】

这篇文档描述了 **Qwen3.5-27B 与 Qwen3.6-27B 这两个 dense hybrid Mamba-Transformer 语言模型** 在 Ascend NPU 上的端到端部署与验证流程,涵盖特性支持矩阵、环境准备、单节点/多节点部署、精度与性能评估等环节,作为面向这两种具体模型的实操教程型 guide。

## 【技术要点】

1. **模型族与架构**: 两者均属于 Qwen3.5/Qwen3.6 系列的 dense hybrid Mamba-Transformer LLM,采用统一的混合注意力设计 (GDN + full attention),因此在 Ascend NPU 上部署路径一致。典型用例为通用文本生成:对话、内容创作、代码生成。

2. **版本基线要求**:
   - `Qwen3.5-27B` 首次支持: `vllm-ascend:v0.17.0rc1`
   - `Qwen3.6-27B` 首次支持: `vllm-ascend:v0.18.0rc1`
   - Atlas 300I DUO 与 Ascend950DT 系列支持起点: `vllm-ascend:v0.23.0rc1`
   - 强烈推荐使用最新 rc 或正式版本。

3. **硬件/HBM 配置矩阵** (按模型权重 × 精度版本划分):
   - Qwen3.5-27B (BF16) 与 w8a8: 1× Atlas 800 A3 (64GB×16) / 1× Atlas 800 A2 (64GB×8) / Atlas 300I DUO
   - Qwen3.6-27B (BF16): 1× Ascend 950DT (96GB×8) / 1× A3 (64GB×16) / 1× A2 (64GB×8) / 300I DUO
   - Qwen3.6-27B-w8a8: A3 (64GB×16) 或 A2 (64GB×8)
   - Qwen3.6-27B-w8a8-mxfp8: Ascend950DT (96GB×8)
   - Qwen3.6-27B-w8a8-310p: Atlas 300I DUO
   - 权重建议落盘到多节点共享目录,例如 `/root/.cache/`。

4. **镜像后缀按硬件族分支**:
   - A3 系列 → `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`,Qwen3.6-27B 需用 `v0.18.0rc1-a3` 及之后 `-a3` 镜像
   - A2 系列 → 无后缀,默认 tag
   - Atlas 300I DUO → `-310p` 后缀,需 `v0.23.0rc1-310p` 及之后
   - Ascend950DT → `-a5` 后缀

5. **多节点部署前置条件**: 必须按 `installation.md#installation-multi-node-interconnect` 验证多节点互联通信。

6. **容器化能力暴露**: Docker 启动需 mount/透传的关键设备包括 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,A2/A3/A5 显式列出 0–15 (A3) 或 0–7 (其余) 个 `/dev/davinci*` 设备,并挂载 `/usr/local/dcmi`、`hccn_tool`、`npu-smi`、driver `lib64`、driver `version.info`、`/etc/ascend_install.info`、模型缓存 `/root/.cache`。A5 系列额外挂载 `/usr/local/Ascend/driver`、`/etc/hccl_rootinfo.json`、`/etc/hixlep/`、`/usr/lib64` 等。Atlas 300I DUO 需额外 `-p 8080:8080` 暴露端口 (无 `--net=host`)。

## 【关键机制与数据】

- **多节点路径**: 文档明示当需要多节点环境时,需先依据 `installation.md#installation-multi-node-interconnect` 校验互联链路。这是 gRPC/HCCL 类集合通信的前置检查步骤 (原文只描述 "验证",无具体吞吐数字)。
- **容量评估隐含逻辑**: 64GB×16 与 64GB×8 对应不同 NPU 拓扑形态,A3 (16 卡) 与 A2 (8 卡) 在 BF16 与 w8a8 下都能容纳 27B 模型权重,说明 27B 权重的 HBM 占用恰好落在这两类配置可服务的预算内 (原文未给出具体权重字节数)。
- **950DT 的差异化能力**: 仅 950DT 能跑 `w8a8-mxfp8` 量化版,说明该量化算子或 kernel 在 Ascend950DT 上被引入,而 A3/A2/300I DUO 尚不支持——这是硬件族 × 量化格式的兼容性约束。
- **数据流**: 文档引用的入口为容器化方案 (Docker) 与源码安装两条路径。容器路径以 `--net=host` (A2/A3/A5) 或 `-p 8080:8080` (300I DUO) 形成对外服务通道,挂载 `/root/.cache` 实现权重跨节点共享。
- **性能数据**: **原文未涉及具体的吞吐量、时延、token/s 等数字**;原文仅声明 "将演示 … 精度与性能评估" 的章节意图,实际章节内容在节选范围之外被截断。

## 【表格解读】

原文以 Markdown 项目符号列示模型权重与硬件组合,**未呈现结构化表格**。

> 原文无表格。

但为了便于读者快速对照,根据原文 Project List 整理出的**派生矩阵**(基于原文条目,非额外数字):

| 模型权重 (模型名) | 精度/量化 | 节点与硬件要求 | ModelScope 路径 |
|---|---|---|---|
| Qwen3.5-27B | BF16 | 1× Atlas 800 A3 (64GB×16) / 1× Atlas 800 A2 (64GB×8) / Atlas 300I DUO | `Qwen/Qwen3.5-27B` |
| Qwen3.5-27B-w8a8 | w8a8 量化 (含 mtp) | 同上 | `Eco-Tech/Qwen3.5-27B-w8a8-mtp` |
| Qwen3.6-27B | BF16 | 1× Ascend 950DT (96GB×8) / 1× A3 (64GB×16) / 1× A2 (64GB×8) / 300I DUO | `Qwen/Qwen3.6-27B` |
| Qwen3.6-27B-w8a8 | w8a8 量化 | 1× A3 (64GB×16) / 1× A2 (64GB×8) | `Eco-Tech/Qwen3.6-27B-w8a8` |
| Qwen3.6-27B-w8a8-mxfp8 | w8a8 mxfp8 量化 | 1× Ascend950DT (96GB×8) | `Eco-Tech/Qwen3.6-27B-w8a8-mxfp8` |
| Qwen3.6-27B-w8a8-310p | w8a8 量化 (310P 适配) | Atlas 300I DUO | `Eco-Tech/Qwen3.6-27B-W8A8-310P` |

逐行解读:
- 第 1 行:这是 Qwen3.5-27B 的标准 BF16 部署形态,在 A3/A2 单节点或 300I DUO 都能承载。
- 第 2 行:量化版指向 `-mtp` 仓库名,表明 w8a8 通路连带 Multi-Token Prediction 能力。
- 第 3 行:Qwen3.6-27B BF16 是覆盖面最广的一档,950DT 是其独享硬件,而 300I DUO 同样支持 BF16。
- 第 4 行:w8a8 量化把可运行硬件收窄到 A3/A2,说明该量化 kernel 在 950DT/300I DUO 暂未提供。
- 第 5 行:`mxfp8` 是 950DT 专属格式,反映新型量化在该硬件族的首发。
- 第 6 行:`-310p` 是为 300I DUO 单独编译的量化变体,通过专属仓库名实现硬件族 → 量化格式的精确映射。

## 【公式解读】

> 原文无公式。

## 【关联】

依据文末内部链接梳理出的上下游与配套模块关系:

- **支持矩阵 (上游)**: `supported_models.md` 定义哪些权重/精度在哪些硬件族上受支持,与本文"硬件/HBM 配置矩阵"一一对应,可作为读者反向校验入口。
- **特性配置 (特性集)**: `feature_guide/index.md` 描述 vllm-ascend 可用特性 (采样、推测解码、并行策略等),本文第 2 节明确把特性配置细节委托到该页,从而避免重复维护。
- **安装与多节点互联 (部署前置)**:
  - `installation.md#installation-multi-node-interconnect` — 多节点 HCCL/网络校验流程
  - `installation.md#installation-prebuilt-image` — 预构建镜像使用规范 (被本文 Docker 启动片段引用)
  - `installation.md` — 总安装入口,被 §4 引用
- **PD 分离 (高级特性)**:
  - `../features/pd_disaggregation_mooncake_multi_node.md`(出现两次,均指向同一文件) — Prefill/Decode 分离 + Mooncake 传输的多节点方案。Qwen3.5/3.6-27B 作为候选 LLM,可加入 PD 分离流水线以提升吞吐;本文通过该链接暗示这些大模型可与 PD 分离协同部署。
- **FAQ**:
  - `../../faqs.md` 出现三次,说明 Qwen3.5/3.6-27B 在部署中可能触发的常见问题 (权重加载失败、版本不匹配、量化失败等) 都被汇总到 FAQ。

文档处于 "tutorials/models/" 体系下,自身定位为 **某一类具体模型 (Qwen3.5/3.6-27B)** 的端到端 playbook,向上接 `feature_guide` 与 `supported_models`,向下接 `installation` 与 `faqs`,横向接 `pd_disaggregation_mooncake_multi_node` 等上层特性。

## 【使用方法】

原文直接给出的启用方式:

1. **下载权重**: 依精度版本选择上述 ModelScope 仓库之一,推荐放置到多节点共享的 `/root/.cache/`。

2. **校验多节点通信** (仅多节点场景): 遵循 `installation.md#installation-multi-node-interconnect`。

3. **使用 Docker 镜像启动 (推荐路径)**:
   - A3: `export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`,再 `docker run --rm --name vllm-ascend --shm-size=1g --net=host … $IMAGE bash`,挂载 16 个 `/dev/davinci0..15` 及 manager/svm/hdc。
   - A2: `export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`,挂载 8 个 `/dev/davinci0..7`。
   - Atlas 300I DUO: `export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p`,不需要 `--net=host`,额外 `-p 8080:8080`。
   - Ascend950DT: `export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a5`,额外挂载 `/usr/local/Ascend/driver`、`/etc/hccl_rootinfo.json`、`/etc/hixlep/`、`/usr/lib64`,并透传 `/dev/ummu`、`/dev/uburma`。
   - 启动后通过 `docker ps` 确认 `vllm-ascend` 容器 `Up`。

4. **版本选择 (最小基线)**:
   - Qwen3.5-27B → `vllm-ascend:v0.17.0rc1` 或更新
   - Qwen3.6-27B → `vllm-ascend:v0.18.0rc1` 或更新;在 Atlas 800 A3 上需匹配 `-a3` 后缀
   - Atlas 300I DUO 与 Ascend950DT → `vllm-ascend:v0.23.0rc1` 或更新 (DUO 用 `-310p`)
   - 强烈建议使用最新 rc/正式版本以获得最佳兼容性与新特性。

5. **源码安装**: 文档第 4.2 节给出备选路径,需 Clone 仓库并进行源码编译 (节选中该节被截断,具体命令在原文后续部分)。

6. **后续动作**: 精度与性能评估章节被原文声明为本文档覆盖范围,但具体步骤在节选外;特性启用遵循 `feature_guide/index.md`;支持矩阵以 `supported_models.md` 为准;运行期问题查阅 `faqs.md`。
