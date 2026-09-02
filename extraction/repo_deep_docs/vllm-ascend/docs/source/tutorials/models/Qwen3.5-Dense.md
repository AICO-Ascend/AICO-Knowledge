# Qwen3.5-Dense (Qwen3.5-2B/4B/9B)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3.5-Dense.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3.5-Dense.md

```markdown
# 一体化深度解读:Qwen3.5-Dense (Qwen3.5-2B/4B/9B) 部署与验证指南

## 【定位】
本文档解决如何在 **Atlas 300I DUO** 与 **Atlas 200I Pro** 两款 Atlas 300I 系列加速硬件上,对 **Qwen3.5-2B/4B/9B**(基于 GDN + 全注意力混合架构的 Dense 混合 Mamba-Transformer 模型)进行环境准备、Docker 安装、单节点在线部署、功能验证及调优参考的问题,并明确自 `vllm-ascend:v0.23.0rc1` 起对该型号的支持基线。

---

## 【技术要点】

1. **模型家族与架构**:Qwen3.5-2B、Qwen3.5-4B、Qwen3.5-9B 均为 **Dense 混合 Mamba-Transformer 语言模型**,采用统一的 **混合注意力设计(GDN + full attention)**;面向通用文本生成(对话、内容创作、代码生成)。

2. **支持的硬件与最低版本**:支持硬件为 **Atlas 300I DUO** 或 **Atlas 200I Pro**;支持起点为 `vllm-ascend:v0.23.0rc1`,推荐使用最新版 rc 或正式版。Docker 镜像至少使用 `vllm-ascend:v0.23.0rc1-310p`(或更新的 `-310p` 后缀);Atlas 200I Pro 在 openEuler 平台需使用 `-310p-openeuler` 镜像变体。

3. **权重与精度**:ModelScope 上的官方发布权重为 **INT8(W8A8-310P)量化版本**(三条 `-W8A8-310P` 链接分别对应 2B/4B/9B);运行示例使用 **FP16** 权重(`--dtype float16`、`--mamba-ssm-cache-dtype float16`),并通过 `VLLM_USE_MODELSCOPE=True` 启用 ModelScope 加载。

4. **并行模式与设备可见性**:目前仅支持 **TP(Tensor Parallel)** 场景,可选 **TP=1 或 TP=2**(按可用设备数选择);在 **Atlas 200I Pro 仅有一张可见 NPU** 时使用 **TP=1**。Atlas 300I DUO 容器挂载 `davinci0`-`davinci7` 共 8 个 davinci 设备外加 `davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`;Atlas 200I Pro(两种 OS)仅挂载 `davinci0`、`davinci_manager`、`/dev/ascend_manager`、`/dev/user_config`。

5. **关键部署参数(以 Qwen3.5-2B 启动命令为准)**:`--max-num-seqs 32`、`--max-model-len 16384`、`--gpu-memory-utilization 0.90`、`--trust-remote-code`;启用 **MTP 投机解码**:`--speculative-config '{"method": "qwen3_5_mtp","num_speculative_tokens":1}'`;CUDA Graph 限制为 **FULL_DECODE_ONLY** 并仅捕获 size=2 与 size=16:`--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes": [2,16]}'`;并通过 `--additional-config '{"ascend_compilation_config": {"enable_npugraph_ex": false}}'` 显式关闭 `enable_npugraph_ex`。

6. **源码安装注意项**:在 Atlas 300I DUO / Atlas 200I Pro 上从源码安装 `vllm-ascend` 时,需要先卸载 `triton-ascend` 与 `triton` 以避免依赖冲突(`pip uninstall -y triton-ascend triton`)。

> **原文截断提示**:本指南原文在 `Qwen3.5-4B` 启动命令处被截断(`vllm serve $MODEL_P` 后无后续内容),因此本文档中未给出 **Qwen3.5-4B 完整启动命令** 与 **Qwen3.5-9B 的完整启动命令**。解读仅基于原文实际给出的 `Qwen3.5-2B` 示例。

---

## 【关键机制与数据】

### 工作原理(原文机制点)

- **混合注意力层叠(原文)**:Qwen3.5 Dense 系列共享同一套混合注意力设计,即 **GDN(用于 Mamba 状态空间层)+ full attention(用于 Transformer 自注意力层)**。GDN 路径带来 O(1) 的状态空间缓存,full attention 路径则负责全局上下文建模。

- **Mamba SSM 缓存精度(原文)**:`--mamba-ssm-cache-dtype float16` 控制 Mamba SSM 状态缓存的数据类型,与 `--dtype float16` 共同决定推理时的内存占用与吞吐取舍。

- **投机解码通路(原文)**:`--speculative-config` 启用 `qwen3_5_mtp` 方法,`num_speculative_tokens=1` 表示每步预测 1 个候选 token(用于在 Atlas 300I/200I 上分摊调度开销)。

- **CUDA Graph 与 NPUGraph 限制(原文)**:`cudagraph_mode: FULL_DECODE_ONLY` 表示仅在 **Decode 阶段** 捕获 CUDA Graph,且只捕获 size ∈ {2, 16};同时 `--additional-config` 中 `ascend_compilation_config.enable_npugraph_ex = false` 显式关闭 NPUGraph 扩展以避免在该硬件上产生兼容性问题。

- **服务端口与主机(原文)**:`--host 127.0.0.1`、`--port 8080`,容器映射 `-p 8080:8080`,对外暴露 8080 端口提供 OpenAI 兼容 API。

### 数据流(原文)

- **容器↔主机卷挂载(原文)**:Atlas 300I DUO 将 `/usr/local/dcmi`、`npu-smi`、`Ascend/driver/lib64`、`Ascend/driver/version.info`、`/etc/ascend_install.info` 与 `/root/.cache` 全部挂入容器;Atlas 200I Pro 在两种 OS 下挂载 `/etc/sys_version.conf`、`/etc/ld.so.conf.d/mind_so.conf`、`/etc/hdcBasic.cfg`、`/var/dmp_daemon`、`libmmpa.so`、`libcrypto.so.1.1`、`npu-smi`、`libstackcore.so`、`/etc/slog.conf`、`/var/slogd`、`Ascend/driver/lib64`、`libtensorflow.so` 与 `/root/.cache`,把宿主机 NPU 驱动/固件、模型缓存暴露进容器,保证 NPU 设备与运行时在容器内可用。

### 性能数据(原文)

- **原文**:本文档未提供吞吐量、时延、显存占用等具体性能数字。性能评估流程通过 `../../developer_guide/evaluation/using_ais_bench.md` 及 `#execute-performance-evaluation` 章节指引;调优手段参考 `../../developer_guide/performance_and_debug/optimization_and_tuning.md`。**(此节为指引性引用,非具体数值)**

---

## 【表格解读】

### 表 1:Model Weight(3.1 节)

原文逐字还原:

| Model | Version | Hardware Requirement | Download |
|-------|---------|----------------------|----------|
| Qwen3.5-2B | INT8 | Atlas 300I DUO or Atlas 200I Pro | [Download](https://www.modelscope.cn/models/Qwen/Qwen3.5-2B-W8A8-310P) |
| Qwen3.5-4B | INT8 | Atlas 300I DUO or Atlas 200I Pro | [Download](https://www.modelscope.cn/models/Qwen/Qwen3.5-4B-W8A8-310P) |
| Qwen3.5-9B | INT8 | Atlas 300I DUO or Atlas 200I Pro | [Download](https://www.modelscope.cn/models/Qwen/Qwen3.5-9B-W8A8-310P) |

逐行解读:

- **Qwen3.5-2B 行**:INT8 量化版本(`Qwen3.5-2B-W8A8-310P` 中的 `W8A8` 表明 Weight/Activation 均为 8 bit,`310P` 表明该权重针对 Atlas 310P NPU 编译),可在 Atlas 300I DUO 或 Atlas 200I Pro 上加载;下载入口指向 ModelScope。
- **Qwen3.5-4B 行**:与 2B 同精度、同硬件兼容位,区别在于参数量提升至 4B;模型 ID 为 `Qwen/Qwen3.5-4B-W8A8-310P`。
- **Qwen3.5-9B 行**:三档中参数量最大,仍采用同一份 W8A8-310P INT8 格式,适用于两块 Atlas 硬件,ModelScope ID 为 `Qwen/Qwen3.5-9B-W8A8-310P`。

> 表格下方原文补充:"It is recommended to download the model weight to a local directory such as `/root/.cache/` or `/home/data/`。"——建议把权重缓存到 `/root/.cache/` 或 `/home/data/` 等本地目录,后续可通过 `MODEL_PATH` 变量或 `-v /root/.cache:/root/.cache` 卷挂载复用。

---

## 【公式解读】

**原文无公式**。本文档为部署/调优操作型指南,所有数学表达均通过命令行参数(如 `--mamba-ssm-cache-dtype`、`num_speculative_tokens`、`cudagraph_capture_sizes`)呈现,未涉及任何 LaTeX 数学式或伪代码算法式。

---

## 【关联】

本文档在文中显式引用了下述内部链接,体现了在更大知识库结构中的上下游依赖:

- **模型兼容性矩阵**:`../../user_guide/support_matrix/supported_models.md` —— 用于查询 Qwen3.5-2B/4B/9B 在更多 Atlas 硬件上的支持范围(本文档 §2)。
- **特性配置指南**:`../../user_guide/feature_guide/index.md` —— 用于查询本文档中未展开的特性(如 MTP、CUDA Graph 模式等)的详细配置(本文档 §2)。
- **Docker 镜像安装总览**:`../../getting_started/installation.md#installation-prebuilt-image` —— 本文 §4.1 中 "Select an image based on your machine type…" 直接锚定此节。
- **完整安装流程**:`../../getting_started/installation.md` —— 本文 §4.2 源码安装路径的完整参考。
- **FAQ**:`../../faqs.md` —— 用于查阅 Qwen3.5 Dense 在 Atlas 300I DUO / 200I Pro 上的常见问题与踩坑(文末关联列表中两次出现,体现其作为部署排错的主入口)。
- **使用 AIS Bench 进行性能评估**:`../../developer_guide/evaluation/using_ais_bench.md` 与其 `#execute-performance-evaluation` 锚点 —— 用于在部署完成后执行端到端性能评测,弥补本文档未给出性能数字的缺口。
- **性能调优指南**:`../../developer_guide/performance_and_debug/optimization_and_tuning.md` —— 用于解释本文中 `--gpu-memory-utilization 0.90`、CUDA Graph 限制、`enable_npugraph_ex=false` 等调参项的背景与权衡。
- **特性矩阵**:`../../user_guide/support_matrix/feature_matrix.md` —— 用于对照 Qwen3.5 Dense 是否支持 MTP、CUDA Graph、TP 等特性(与 `supported_models.md` 形成 "模型×特性" 二维查询)。

**模块上下游关系(从原文还原)**:
- 上游(被依赖):`vllm-ascend:v0.23.0rc1` 起 + Atlas 300I/200I NPU 驱动与固件 + INT8/FP16 Qwen3.5 权重。
- 中游(本文档主体):容器化/源码安装 → 单节点 TP 部署(vllm serve) → 投机解码与 CUDA Graph 策略 → 端口 8080 对外服务。
- 下游(本文档未完成,指引到其他文档):AIS Bench 评测、性能调优、FAQ 排错。

---

## 【使用方法】

### 启用方式(原文)

1. **Docker 方式(原文 §4.1)**:根据硬件选择对应 `--device` 与镜像 tag(`-310p` 或 `-310p-openeuler`),运行提供的 `docker run` 命令,期望 `docker ps` 显示 `vllm-ascend` 状态为 `Up`。
2. **源码方式(原文 §4.2)**:`git clone https://github.com/vllm-project/vllm-ascend.git && cd vllm-ascend && pip install -e .`,安装后用 `pip show vllm-ascend` 校验版本;在 Atlas 300I DUO / 200I Pro 上需先执行 `pip uninstall -y triton-ascend triton`。

### 关键配置项(原文 §5.1,Qwen3.5-2B 示例)

| 配置项 | 原文取值 | 说明 |
|--------|----------|------|
| `VLLM_USE_MODELSCOPE` | `True` | 走 ModelScope 加速下载 |
| `MODEL_PATH` | `Qwen/Qwen3.5-2B` | 也可换成本地权重目录 |
| `--host` / `--port` | `127.0.0.1` / `8080` | 与容器 `-p 8080:8080` 对应 |
| `--tensor-parallel-size` | `1` | Atlas 200I Pro 单卡 / 3DUO 取 1 或 2 |
| `--served-model-name` | `qwen3.5` | OpenAI 客户端调用的模型名 |
| `--max-num-seqs` | `32` | 并发序列上限 |
| `--max-model-len` | `16384` | 最大上下文长度 |
| `--trust-remote-code` | (flag) | 信任仓库内自定义模型代码 |
| `--gpu-memory-utilization` | `0.90` | NPU 显存占用比 |
| `--mamba-ssm-cache-dtype` | `float16` | Mamba SSM 状态缓存精度 |
| `--dtype` | `float16` | 推理主精度 |
| `--speculative-config` | `{"method": "qwen3_5_mtp","num_speculative_tokens":1}` | 启用 Qwen3.5 MTP 投机解码,候选 1 token |
| `--compilation-config` | `{"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes": [2,16]}` | 仅在 Decode 阶段、size=2/16 时捕获 CUDA Graph |
| `--additional-config` | `{"ascend_compilation_config": {"enable_npugraph_ex": false}}` | 关闭 NPUGraph 扩展 |

### 命令(原文给出的完整命令)

- **Qwen3.5-2B 单节点在线部署(FP16,TP=1,Atlas 300I DUO / 200I Pro 通用)** —— 见上文【技术要点】第 5 条,命令体使用 `vllm serve $MODEL_PATH` 并附带上述全部 flags。
- **Qwen3.5-4B 单节点在线部署** —— **原文截断**(命令停在 `vllm serve $MODEL_P`,未给出完整 flags)。**原文未涉及**完整命令。
- **Qwen3.5-9B 单节点在线部署** —— **原文未涉及**完整命令(4B 之后的章节在原文中被截断)。
- **容器/安装完整性校验**:`docker ps`(期望 `vllm-ascend` 状态为 `Up`);`pip show vllm-ascend`(期望显示已安装的版本号)。

> 提示:Qwen3.5-4B 与 9B 的部署建议在原始文档补全后参考其完整命令;在补全之前,可按 Qwen3.5-2B 的模板将 `MODEL_PATH` 替换为 `Qwen/Qwen3.5-4B` 或 `Qwen/Qwen3.5-9B` 试运行,其余参数的可移植性需以官方文档为准(此为方法论建议,**非原文内容**)。
```
