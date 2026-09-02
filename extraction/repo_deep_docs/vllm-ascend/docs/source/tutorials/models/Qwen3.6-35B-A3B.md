# Qwen3.6-35B-A3B

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3.6-35B-A3B.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3.6-35B-A3B.md

# 「Qwen3.6-35B-A3B」文档一体化深度解读

> 说明:用户提供原文在此处被截断,止于 `--max-num-batched-tokens is the maximum number of tokens processed in one scheduler step. A larger value can` 一句;原文档其余章节(Online Deployment 后续、Functional Verification、Accuracy / Performance Evaluation、Performance Tuning、FAQs)在提供的文本中并未出现,以下解读仅基于已给出的原文内容,凡原文未涉及的均明确标注。

---

## 【定位】

这篇文档为 vLLM-Ascend 在 Ascend 硬件上落地 **Qwen3.6-35B-A3B**(稀疏 MoE、35B 总参 / 每 token 约 3B 激活、Qwen3.5 风格 hybrid attention)模型提供端到端的验证与部署范式:从特性矩阵、模型权重、前提硬件、Docker/源码安装,到单节点在线服务启动与关键参数说明,使长上下文(最大 262144)在线推理可在 Atlas A2 / A3 / 300I DUO 上落地。

---

## 【技术要点】

1. **模型族系与定位**(原文 1):Qwen3.6-35B-A3B 属 Qwen3.6 家族,**35B 总参数 / 每 token ≈3B 激活参数**;采用 Qwen3.5 风格的 hybrid attention,面向 Ascend 硬件的**长上下文在线服务**场景。
2. **首次支持版本**(原文 1):该模型在 `vllm-ascend:v0.18.0rc1` 首次受支持,需使用 `v0.18.0rc1` 或更高版本;示例使用文档构建系统的版本占位符 `{{ vllm_ascend_version }}`。
3. **支持特性矩阵**(原文 2):BF16、W8A8 量化、chunked prefill、automatic prefix caching、asynchronous scheduling、tensor parallelism、expert parallelism、ACLGraph;特性详情指向 `supported_features.md` 与 `feature_guide/index.md`。
4. **硬件前提与权重**(原文 3.1):BF16 与 W8A8 两版均要求 **1 节点 Atlas A3(64G ×16)、1 节点 Atlas A2(64G ×8)或 Atlas 300I DUO**;BF16 权重来自 `modelscope.cn/models/Qwen/Qwen3.6-35B-A3B`,W8A8 来自 `Eco-Tech/Qwen3.6-35B-A3B-w8a8`,建议下载到 `/root/.cache/`。
5. **三套镜像与容器配置**(原文 4.1):Atlas A2 用 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`、Atlas A3 用后缀 `-a3`、Atlas 300I DUO 用后缀 `-310p`;三类容器均 `--device` 注入 `/dev/davinci*` 等设备并挂载 `/usr/local/dcmi`、`/usr/local/Ascend/driver/...` 与 `/root/.cache`;300I DUO 额外启用 `--shm-size=10g` 与端口映射 `-p 8080:8080`。
6. **单节点在线服务关键参数**(原文 5.1):`vllm serve Eco-Tech/Qwen3.6-35B-A3B-w8a8 --tensor-parallel-size 2 --data-parallel-size 1 --enable-expert-parallel --quantization ascend --max-model-len 262144 --max-num-seqs 128 --max-num-batched-tokens 16384 --gpu-memory-utilization 0.90 --enable-prefix-caching --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' --additional-config '{"enable_cpu_binding":true, "multistream_overlap_shared_expert": true}'`;并通过环境变量 `HCCL_OP_EXPANSION_MODE="AIV"`、`HCCL_BUFFSIZE=1024`、`OMP_NUM_THREADS=1`、`TASK_QUEUE_ENABLE=1`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`VLLM_USE_MODELSCOPE=True`、`LD_PRELOAD=.../libjemalloc.so.2:$LD_PRELOAD` 以及 `performance` 调速器 + `vm.swappiness=0` / `kernel.numa_balancing=0` / `kernel.sched_migration_cost_ns=50000` 进行系统与运行时调优。

---

## 【关键机制与数据】

- **稀疏 MoE 激活模式**(原文 1):35B 总参数中**每 token 约 3B 参数激活**,体现稀疏激活特性;需通过 expert parallelism(EP)支撑 MoE 层(原文 5.1:"--enable-expert-parallel enables expert parallelism for MoE layers. Do not mix MoE tensor parallelism and expert parallelism in the same MoE layer.")。
- **数据流与并行策略**(原文 5.1):单节点部署下,`--data-parallel-size 1` 与 `--tensor-parallel-size 2` 组合设置 DP/TP;`--max-num-seqs 128` 为每个 DP 组的最大并发请求数;`--max-num-batched-tokens 16384` 为单次调度可处理 token 数上限。
- **上下文长度上限**(原文 5.1):`--max-model-len 262144`,且原文注明"Increase it only when enough KV cache is available"——表明 KV cache 容量是长上下文开启的前置约束(性能数据原文未涉及)。
- **量化链路**(原文 3.1、5.1):W8A8 量化版必须配 `--quantization ascend`;BF16 版无需该参数(原文未给出 BF16 版的具体启动命令,具体差异本节不臆造)。
- **编译图模式**(原文 5.1):`--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`——仅在 decode 阶段启用 cudagraph,以平衡显存与首 token 时延。
- **专家并行下的多流共享专家**(原文 5.1):`--additional-config '{"enable_cpu_binding":true, "multistream_overlap_shared_expert": true}'` 启用 CPU 绑定与共享专家多流 overlap,面向 MoE 推理的微优化。
- **环境/系统调优组合**(原文 5.1):`HCCL_OP_EXPANSION_MODE="AIV"` + `HCCL_BUFFSIZE=1024` 调整集合通信;`OMP_NUM_THREADS=1` 限制 OpenMP 线程;`TASK_QUEUE_ENABLE=1` 启用任务队列;`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True` 减少 NPU 显存碎片;`LD_PRELOAD` 注入 jemalloc 改善内存分配;CPU 调速器设为 `performance`,`vm.swappiness=0`、`kernel.numa_balancing=0`、`kernel.sched_migration_cost_ns=50000` 优化内存与调度行为。
- **源码安装的 300I DUO 注意事项**(原文 4.2):需 `pip uninstall -y triton-ascend triton` 后再运行 vLLM-Ascend,以避免不兼容依赖。
- **首次进入容器验证**(原文 4.1 末尾):`python -c "import vllm, vllm_ascend; print('vllm and vllm_ascend are ready')"`——最小依赖健康检查。

> 性能基准数据(吞吐、TTFT、TPOT 等)与精度评估结果在原文截断部分未出现,标注:**原文未涉及**。

---

## 【表格解读】

**原文无表格**(全文为叙述、命令与参数列表,未出现任何 markdown 表格)。

---

## 【公式解读】

**原文无公式**(全文未出现 LaTeX 公式或伪代码形式数学表达式)。

---

## 【关联】

文档自身的章节引用(均见原文):

- **Supported Features 矩阵与配置详情** → `../../user_guide/support_matrix/supported_features.md`、`../../user_guide/feature_guide/index.md`(原文 2,用于查询 BF16/W8A8、chunked prefill、自动前缀缓存、异步调度、TP、EP、ACLGraph 等)。
- **Docker 镜像安装完整指南** → `../../getting_started/installation.md#installation-prebuilt-image`(原文 4.1)。
- **源码安装流程** → `../../getting_started/installation.md#installation-existing-cann-install`(原文 4.2)。

文档提到但未在截断正文中展开、依赖其他文档补全的章节(原文 1 列举:supported features、prerequisites、installation、single-node online deployment、functional verification、accuracy and performance evaluation、performance tuning、FAQs),与以下内部链接存在预期关联:

- **功能/特性总览**:`../../user_guide/support_matrix/feature_matrix.md`、`../../user_guide/support_matrix/supported_features.md`、`../../user_guide/feature_guide/index.md`。
- **安装入口**:`../../getting_started/installation.md#installation-prebuilt-image`、`../../getting_started/installation.md#installation-existing-cann-install`。
- **精度与性能评估**(原文未给出的章节将引向此处):`../../developer_guide/evaluation/using_ais_bench.md`、`../../developer_guide/evaluation/using_lm_eval.md`、`../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation`。
- **性能调优与 FAQ**:`../../developer_guide/performance_and_debug/optimization_and_tuning.md`、`../../faqs.md`。

依赖/并列关系小结:
- 与 **A2 / A3 / 300I DUO 三类硬件**并列提供镜像变体(`-a3` / 默认 / `-310p`)。
- 与 **MoE 专家并行**(`--enable-expert-parallel`)与 **TP**(`--tensor-parallel-size 2`)并列构成该模型的并行策略,并明确禁止在同层混用。
- 与 **chunked prefill / 自动前缀缓存 / 异步调度 / ACLGraph(`FULL_DECODE_ONLY`)** 等特性共同构成"长上下文在线服务"能力组合(均来自原文 2 的特性矩阵)。

---

## 【使用方法】

**启用方式 / 配置项 / 命令**(原文 5.1 实际给出的命令):

```shell
# 环境变量与系统调优
export VLLM_USE_MODELSCOPE=True
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_OP_EXPANSION_MODE="AIV"
export HCCL_BUFFSIZE=1024
export OMP_NUM_THREADS=1
export TASK_QUEUE_ENABLE=1
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
sysctl -w vm.swappiness=0
sysctl -w kernel.numa_balancing=0
sysctl kernel.sched_migration_cost_ns=50000
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD

# 单节点启动(W8A8,Atlas A2 / A3,最大 262144 上下文)
vllm serve Eco-Tech/Qwen3.6-35B-A3B-w8a8 \
  --host 0.0.0.0 \
  --port 8000 \
  --data-parallel-size 1 \
  --tensor-parallel-size 2 \
  --enable-expert-parallel \
  --seed 1024 \
  --quantization ascend \
  --served-model-name qwen3.6 \
  --max-num-seqs 128 \
  --max-model-len 262144 \
  --max-num-batched-tokens 16384 \
  --trust-remote-code \
  --gpu-memory-utilization 0.90 \
  --enable-prefix-caching \
  --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' \
  --additional-config '{"enable_cpu_binding":true, "multistream_overlap_shared_expert": true}'
```

**关键开关释义**(原文 Key parameters 段,逐字保留原文措辞):

- `--data-parallel-size 1` 与 `--tensor-parallel-size 2`:设置默认单节点服务的 DP 与 TP。
- `--enable-expert-parallel`:为 MoE 层开启 expert parallelism;**不要在同一 MoE 层混合 MoE tensor parallelism 与 expert parallelism**。
- `--max-model-len`:单请求最大输入+输出长度,**仅在 KV cache 充足时增大**。
- `--max-num-seqs`:每个 DP 组调度的最大活跃请求数;性能测试时 `--max-num-seqs * --data-parallel-size` 应**大于等于测试并发**。
- `--max-num-batched-tokens`:单次调度步处理 token 数上限;更大的值可以…(原文于此处截断,后续说明**原文未涉及**)。

**容器级启用**(原文 4.1):选对应镜像 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}[-a3|-310p]`,按原文 docker run 模板挂载设备与 `/root/.cache`,进入后执行 `python -c "import vllm, vllm_ascend; print('vllm and vllm_ascend are ready')"` 校验。

**源码安装时的额外清理**(原文 4.2 note):在 Atlas 300I DUO 上源码安装后需 `pip uninstall -y triton-ascend triton` 再运行 vLLM-Ascend。

**功能性验证 / 精度评估 / 性能测试 / 性能调优 / FAQ 的具体步骤**:原文 1 章节目录已声明,但**提供的原文被截断,具体启用方式/命令/配置项原文未涉及**;按文档预期应跳转至 `../../developer_guide/evaluation/using_ais_bench.md`、`../../developer_guide/evaluation/using_lm_eval.md`、`../../developer_guide/performance_and_debug/optimization_and_tuning.md`、`../../faqs.md`。
