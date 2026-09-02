# GLM-5.3 (Experimental)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/GLM5.3.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/GLM5.3.md

# GLM-5.3 文档深度解读

## 【定位】

本文档是 vllm-ascend 项目中针对 GLM-5.3（实验性版本）模型在 Ascend NPU 上的部署、特性支持、环境准备、多节点部署、精度与性能评估的端到端验证指南,目标是帮助用户在 Atlas 800 A3/A2 硬件上以多节点同位（co-located）模式跑通 GLM-5.3（w8a8c8 量化变体）。

---

## 【技术要点】

1. **模型定位**: GLM-5.3 与 GLM-5.2 使用相同的基座模型,所有改进来自后训练(post-training),在复杂编码与长程任务(long-horizon)上更强。
2. **官方镜像与版本约束**: 仅在 `quay.io/ascend/vllm-ascend:v0.23.0-a3` 与 `quay.io/ascend/vllm-ascend:v0.23.0` 两个官方 Docker 镜像上经过测试,仅在多节点同位场景下验证,基于 v0.23.0 标签。
3. **硬件要求（GLM-5.3-w8a8c8）**:
   - §3.1 列出需要 **2 个 Atlas 800 A3 (128GB × 8)** 节点 **或** **4 个 Atlas 800 A2 (64GB × 32)**
   - §5.1.1 列出 A3 系列可在 **2 个 Atlas 800 A3 (64GB × 16)** 上部署
4. **多节点并行拓扑**: `--data-parallel-size 8` + `--data-parallel-size-local 4` + `--tensor-parallel-size 4` + `--enable-expert-parallel`,即两节点各贡献 4 卡,TP=4,DP 跨节点 8,叠加专家并行(MoE)。
5. **量化**: 使用 `msmodelslim` 生成 w8a8c8(权重 8bit / 激活 8bit / cube 8bit)量化权重,启动时通过 `--quantization ascend` 加载。
6. **推测解码**: 启用 `deepseek_mtp` 方法,`num_speculative_tokens=3`,`enforce_eager=true`,MTP 全名 Multi-Token Prediction。
7. **附加 ascend 配置项**: 启用 `enable_dsa_cp / enable_sparse_sfa_c8 / enable_sparse_li_c8 / enable_balance_scheduling / enable_fused_mc2=1 / enable_flashcomm1=true`,以及 `VLLM_ASCEND_ENABLE_MLAPO=1`(MLAPO 加速),`cudagraph_mode: FULL_DECODE_ONLY`。
8. **HCCL 通信环境变量**: `HCCL_OP_EXPANSION_MODE=AIV`,`HCCL_BUFFSIZE=400`,三个 timeout 分别 600/3600/3600 秒。

---

## 【关键机制与数据】

- **工作原理(原文表述)**:
  - "Current status and constraints" — 仅在多节点同位场景下验证;`Supported Features` 仅指本文档中的部署命令所启用的特性,**不**意味着所有特性都受支持。
  - `msmodelslim` 用于直接量化生成 `w8a8c8` 权重。
  - 推荐把权重放在多节点共享目录,如 `/root/.cache/`。
- **数据流(原文命令可推断)**:
  - 容器挂载了 8~16 个 `/dev/davinci*` 设备以及 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,并挂载 host 的 dcmi、hccn_tool、npu-smi、driver lib64、version.info、ascend_install.info。
  - master(node0)与 node1 通过 `data-parallel-address` + `data-parallel-rpc-port 12980` + `HCCL_IF_IP` 互联。
- **性能数据**: 原文未提供具体性能数字(吞吐量、延迟、token/s 等);文档第 6 章(精度)/ 第 7 章(性能评估)在提供的原文片段中已被截断,后续内容不存在于本次输入。
- **容量配置(原文给出)**:
  - `--max-model-len 202752`,`--max-num-batched-tokens 4096`,`--max-num-seqs 6`,`--gpu-memory-utilization 0.90`。
  - `--safetensors-load-strategy prefetch`,`--seed 1024`,`--served-model-name glm-5`,`--tool-call-parser glm47`,`--reasoning-parser glm45`,`--enable-auto-tool-choice`,`--trust-remote-code`。

---

## 【表格解读】

原文无表格。文档中只有文本、警告框与代码块;没有 markdown 表格元素。

(可视为隐含表格的硬件要求,在 §3.1 与 §5.1.1 中以列表/段落形式出现,而非表格形式,故按要求写"原文无表格"。)

---

## 【公式解读】

原文无公式。文档未出现任何数学表达式、LaTeX 或伪代码公式。

---

## 【关联】

- **`../../user_guide/support_matrix/supported_models.md`**: §2 引用,说明本模型的实际支持矩阵需查此总表。
- **`../../user_guide/feature_guide/index.md`**: §2 引用,获取 Feature 配置方法(如 MTP、专家并行、量化等)。
- **`../../installation.md#verify-multi-node-communication`**: §3.2 与 §5.1 引用,多节点部署前的环境验证步骤。
- **`../../installation.md`**: §4.2 引用,源码安装入口(不走 Docker 时使用)。
- **`../../faqs.md`**: §5.1 公共 FAQ,部署中遇问题先查这里。
- **`../../developer_guide/evaluation/using_ais_bench.md`** 与 **`using_ais_bench.md#execute-performance-evaluation`**: 文末列出的链接(原文此处被截断但链接存在),用于在后续章节做精度与性能评估(使用 ais_bench)。

---

## 【使用方法】

> 原文给出多节点 A3 同位场景下 node0 的完整 `vllm serve` 命令;node1 的脚本在原文片段中被截断(只显示了环境变量与 `vllm serve` 头部)。下游章节(精度验证 / 性能评估 / Declaration)在原文片段中同样缺失。

### 1. 模型权重
- 下载 `GLM-5.3-w8a8c8`: <https://www.modelscope.cn/models/Eco-Tech/GLM-5.3-w8a8c8>
- 也可使用 [`msmodelslim`](https://gitcode.com/Ascend/msmodelslim) 自己量化。
- 推荐路径:`/root/.cache/`(共享目录)

### 2. Docker 启动(A3 series,每个节点执行)
```shell
export IMAGE=quay.io/ascend/vllm-ascend:v0.23.0-a3
export NAME=vllm-ascend
docker run --rm --name $NAME --net=host --shm-size=1g \
  --device /dev/davinci0 … --device /dev/davinci15 \
  --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /root/.cache:/root/.cache \
  -it $IMAGE bash
```
(A2 series 用 `vllm-ascend:v0.23.0`,挂载 davinci0~7 共 8 个设备,命令与 A3 类似。)

### 3. 多节点启动关键环境变量(node0 / node1 各自设置)
```shell
export HCCL_OP_EXPANSION_MODE="AIV"
export HCCL_IF_IP=$local_ip
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=$nic_name
export HCCL_TRANSFER_TIMEOUT=600
export HCCL_EXEC_TIMEOUT=3600
export HCCL_CONNECT_TIMEOUT=3600
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export HCCL_BUFFSIZE=400
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export VLLM_ASCEND_ENABLE_MLAPO=1
```

### 4. vLLM Serve 启动参数(node0,A3,context < 1M,GLM-5.3-w8a8c8,2 × Atlas 800 A3 64GB×16)
```shell
vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/GLM-5.3-w8a8c8 \
    --host 0.0.0.0 \
    --port 8077 \
    --safetensors-load-strategy prefetch \
    --api-server-count 1 \
    --data-parallel-size 8 \
    --data-parallel-start-rank 0 \
    --data-parallel-size-local 4 \
    --data-parallel-address $node0_ip \
    --data-parallel-rpc-port 12980 \
    --tensor-parallel-size 4 \
    --enable-expert-parallel \
    --seed 1024 \
    --served-model-name glm-5 \
    --tool-call-parser glm47 \
    --reasoning-parser glm45 \
    --enable-auto-tool-choice \
    --max-num-seqs 6 \
    --max-model-len 202752 \
    --max-num-batched-tokens 4096 \
    --trust-remote-code \
    --gpu-memory-utilization 0.90 \
    --quantization ascend \
    --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
    --additional-config '{"enable_dsa_cp": true, "enable_sparse_sfa_c8": true, "enable_sparse_li_c8": true, "enable_balance_scheduling": true, "enable_fused_mc2": 1, "enable_flashcomm1": true}' \
    --speculative-config '{"num_speculative_tokens": 3, "method": "deepseek_mtp", "enforce_eager": true}'
```

### 5. node1 关键差异(原文片段中以下部分被截断,但根据上下文可知)
- `--data-parallel-start-rank` 应与 node0 配合(具体值未在原文片段中给出)。
- 其余参数与 node0 基本一致。

### 6. 精度 / 性能评估
原文片段中 `using_ais_bench.md` 与 `using_ais_bench.md#execute-performance-evaluation` 链接存在,但对应的命令段落(§6/§7)在本次输入里缺失,**原文未涉及具体命令**。

### 7. 注意事项(原文)
- 仅在 `v0.23.0-a3` 与 `v0.23.0` 镜像、多节点同位场景下验证。
- main 分支的参数可能已变更,使用 main 分支需自行核对。
- 这是 early-access 版本,性能优化与可靠性验证仍在进行中。
