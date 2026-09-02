# msModelSlim 快速入门

> 仓 `msmodelslim` · 路径 `docs/zh/quick_start/quantization_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodelslim/docs/zh/quick_start/quantization_quick_start.md

# msModelSlim 量化快速入门 —— 一体化深度解读

---

## 【定位】

本文是一篇面向昇腾生态用户、以 **Qwen3.6-27B 模型** 为示例的 **量化压缩"一键体验"教程**，目标是在约 10 分钟内（不计网络传输）走通"容器环境准备 → 模型下载 → msModelSlim 一键量化 → vLLM-Ascend 推理验证"的全链路，并通过 W8A8（权重量化与激活动化均量化为 8-bit）的量化展示模型体积压缩与可部署性。

---

## 【技术要点】

1. **量化对象与精度格式**：以 `Qwen3.6-27B` 模型为例，采用 **W8A8** 模式（权重与激活均量化到 8-bit，输出为 **INT8 量化权重分片**，共 9 个 safetensors 分片）。
2. **运行环境约束**：教程**仅支持**在标准化 `vLLM-Ascend` 容器内运行；不支持裸机、虚拟机或其他非标准容器；硬件至少 **2 张 NPU 卡（A2 或 A3 系列）**；磁盘至少 **100GB** 空闲。
3. **镜像自动选择机制**：通过 `lspci` 抓取 NPU 的 PCI Device ID（`19e5:d802` → A2 系列；`19e5:d803` → A3 系列），自动匹配 `quay.io/ascend/vllm-ascend:v0.18.0`（A2）或 `v0.18.0-a3`（A3）官方镜像，并写入 `MY_STUDY_VAR_VLLM_IMAGE` 环境变量。
4. **依赖版本切换**：
   - 量化阶段：`transformers==5.2.0` + `msmodelslim-26.1.0`（`MindStudio_26.1.0.B100_002` tag）。
   - 推理阶段：需降级回 `transformers==4.57.6`，以兼容 `vLLM` 运行依赖。
5. **NPU 可见设备隔离**：通过 `ASCEND_RT_VISIBLE_DEVICES` 环境变量控制进程可见的 NPU 列表；设置后**逻辑索引从 0 重新编号**（如 `=1` → 新索引 0；`=1,2,3` → 新索引 0、1、2）。原文标注该特性为**试用特性，不建议用于生产环境**。
6. **量化产物结构**：`quant_model_description.json`（量化元数据）+ `quant_model_weights-NNNNN-of-00009.safetensors`（9 个 INT8 分片）+ `*_best_practice.yaml`（量化配置协议，可复现方案）+ 原始的 `config.json` / `tokenizer*` / `chat_template.jinja` / `generation_config.json`。

---

## 【关键机制与数据】

- **量化压缩效果**（原文）：原始模型权重"约 50+GB"，量化后"约 30+GB"，体积缩减"约 40%"。
- **时间预算**（原文体验地图）：
  - 容器环境准备：约 1 分钟（不含镜像下载）
  - 模型文件准备：约 1 分钟（不含模型下载）
  - 模型量化：约 3 分钟
  - 量化结果验证：约 5 分钟
  - 模型下载侧记：千兆带宽满速下载约需 10 分钟。
- **NPU 占用**：量化阶段单卡即可（自动选 1 张空闲卡）；vLLM 推理阶段需 **2 张卡做张量并行**（`--tensor-parallel-size 2`）。
- **数据流**：原始权重（HF 格式，~50GB） → msModelSlim 读取 → 内部最佳实践配置匹配（按 `model_type=Qwen3.6-27B`、`quant_type=w8a8` 自动加载） → 写入 INT8 分片权重 + 元数据 + 配置协议 → vLLM-Ascend 通过 `--quantization ascend` 后端加载量化权重。
- **成功标志**（原文）：日志出现 `===========SUCCESS===========`，量化耗时"约 4 分钟"。
- **故障兜底**：NPU Health 非 OK / 卡被占用 → 换卡；`ASCEND_RT_VISIBLE_DEVICES` 无效 → 重新解析；OOM → 切换空闲卡（原文未给出具体单卡显存阈值）。
- **量化配置协议可复现性**：原文指出 `Qwen3.6-27B_best_practice.yaml` 记录"本次量化的完整配置信息，可用于方案复现"。

---

## 【表格解读】

### 表 1：体验地图（4 步全流程耗时与原理学习）

> **原文逐字还原**：

| 步骤 | 环节 | 核心工具           |       操作耗时       | 原理学习 |
|:--:|:-------|:---------------|:----------------:|:-----:|
| 1 | 容器环境准备 | vLLM-Ascend 容器 | 约 1 分钟（不含镜像下载时间） | 5 分钟 |
| 2 | 模型文件准备 | modelscope     | 约 1 分钟（不含模型下载时间） | 2 分钟 |
| 3 | 模型量化 | msModelSlim    |      约 3 分钟      | 5 分钟 |
| 4 | 量化结果验证 | vLLM-Ascend    |      约 5 分钟      | 10 分钟 |

**逐行解读**：
- **行 1（容器准备）**：核心工具是 `vLLM-Ascend` 官方容器镜像（自动按 A2/A3 选择 v0.18.0 或 v0.18.0-a3），操作耗时仅指容器创建与脚本拉取（约 1 分钟），不含镜像层下载；"原理学习"列的 5 分钟指理解镜像自动选择、NPU 可见设备隔离等机制。
- **行 2（模型准备）**：通过 `modelscope` CLI 下载 `Qwen/Qwen3.6-27B`，"约 1 分钟"指执行 download 命令本身，不含 ~50GB 权重传输时间；原理学习只需 2 分钟（即理解 ModelScope 的下载行为）。
- **行 3（模型量化）**：使用 `msmodelslim quant` 一键命令，文档给出的实际耗时"约 4 分钟"（与表中"约 3 分钟"略有出入，原文量化小节明确写为"约 4 分钟"）；原理学习 5 分钟，对应理解 W8A8、最佳实践配置匹配、量化产物结构。
- **行 4（结果验证）**：使用 `vLLM-Ascend` 在线服务跑一次推理；耗时 5 分钟主要来自服务冷启动（~4 分钟）与一次推理请求；原理学习 10 分钟最长，涵盖张量并行、`--quantization ascend` 后端、`FULL_DECODE_ONLY` 图模式、NUMA 亲和等推理端概念。

### 表 2：前置条件清单

> **原文逐字还原**：

| 项目       | 要求                                           | 验证方法                              |
|----------|----------------------------------------------|-----------------------------------|
| **硬件算力** | Linux 服务器配备至少 2 张 NPU 卡（A2 或 A3 系列），驱动与固件已安装 | 执行 `npu-smi info`，确认 NPU 卡状态正常    |
| **容器运行** | 已安装并运行 Docker（建议版本 ≥ 18.0）                   | 执行 `docker ps`，无报错即表示服务正常启动       |
| **脚本执行** | 宿主机已安装 Python 3（任意版本）                        | 在宿主机执行 `python3 -V`，有版本信息输出即表示已安装 |
| **网络通信** | 已安装 curl（任意版本）                               | 执行 `curl -V`，有版本信息输出即表示已安装        |
| **磁盘空间** | 至少 100GB 空闲磁盘空间（用于模型权重下载）                    | 执行 `df -h`，查看磁盘空间使用情况                     |

**逐行解读**：
- **硬件算力**：硬性下限 2 张 NPU（A2 = `d802`，A3 = `d803`），缺一不可；验证命令 `npu-smi info` 同时承担"看 NPU 是否在位 + 驱动是否加载"双重诊断。
- **容器运行**：Docker ≥ 18.0 为建议值而非硬约束，原文未给出严格最低版本；`docker ps` 即最小健康检查。
- **脚本执行**：Python 3 仅在**宿主机**要求，用于执行 `ctr_in.py` 启动脚本；容器内的 Python 版本由镜像决定。
- **网络通信**：`curl` 用于拉取容器启动脚本 `ctr_in.py`，版本无要求。
- **磁盘空间**：100GB 阈值是为容纳 ~50GB 原始权重 + ~30GB 量化权重 + 容器/依赖缓存；`df -h` 需关注挂载点可用空间而非分区总量。

---

## 【公式解读】

**原文无公式**（文档为操作教程，未出现任何数学公式或伪代码推导）。

---

## 【关联】

本文处于 msModelSlim 文档体系的"快速上手"入口层，与上下游的关系如下：

- **上游 / 同级入口**：通过文末内部链接 `../user_guide/README.md` 跳转至 **User Guide**（用户指南），后者承载更系统的功能说明、最佳实践原理、量化算法细节等——本教程中的"原理学习"列所引用的 5 分钟/10 分钟原理学习内容，正是 User Guide 中对应章节的导读。
- **下游 / 排错章节**：文末相对链接
  - `#31-docker-镜像在隔离内网的获取方法` —— 企业内网无公网时获取镜像的备用路径；
  - `#32-传输容器启动脚本` —— 内网下手动传输 `ctr_in.py`；
  - `#33-离线安装-python-依赖` —— 内网下离线安装 `msmodelslim` 与 `transformers`。
- **外部依赖模块**：
  - **vLLM-Ascend**：推理引擎，本文仅作为量化结果验证载体；其官方镜像仓库为 [quay.io/ascend/vllm-ascend](https://quay.io/repository/ascend/vllm-ascend?tab=tags)。
  - **ModelScope**：模型下载来源；本文只使用其 CLI `modelscope download`。
  - **昇腾驱动 / 固件 / CANN**：通过 `npu-smi info` 与 `torch_npu` 间接验证，不在本文档展开。
- **与同仓其他特性的关系**：本文档聚焦"W8A8 + 一键量化"路径，未涉及 msModelSlim 支持的 **MoE 量化、多模态模型量化、稀疏化、KV cache 量化** 等其他能力；这些能力在 User Guide 中展开（由 `../user_guide/README.md` 链接承接）。

---

## 【使用方法】

> 以下命令均按原文出现顺序整理；原文未覆盖的细节（如停服、清理容器、离线包校验等）已标注为"原文未涉及"。

### 1. 镜像自动选择（宿主机）
```bash
dev_id=$(lspci -n -D | grep -o '19e5:d[0-9a-f]\{3\}' | head -n1 | cut -d: -f2)
source /dev/stdin <<< "$( ... d802→v0.18.0 / d803→v0.18.0-a3 / 其他→[FAIL] ... )"
```

### 2. 拉取并启动容器（宿主机）
```bash
docker pull ${MY_STUDY_VAR_VLLM_IMAGE}
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
~/ctr_in.py ${MY_STUDY_VAR_VLLM_IMAGE}
```

### 3. 安装量化环境（容器内）
```bash
pip install -i https://repo.huaweicloud.com/repository/pypi/simple/ \
    transformers==5.2.0 \
    https://gitcode.com/Ascend/msmodelslim/releases/download/tag_MindStudio_26.1.0.B100_002/msmodelslim-26.1.0-py3-none-any.whl
```

### 4. 环境验证（容器内）
```bash
python3 -c 'import torch, torch_npu; assert torch.npu.is_available(), "NPU is unavailable"; print("PyTorch:", torch.__version__)' && msmodelslim --help >/dev/null && echo -e "\e[32m[PASS] NPU environment and msmodelslim check passed.\e[0m"
```

### 5. 下载模型（容器内）
```bash
modelscope download --model Qwen/Qwen3.6-27B --local_dir ~/qwen36_27b_base
```

### 6. 选择空闲 NPU（容器内，量化阶段需 1 张）
```bash
free_npu=$(npu-smi info | grep -oE "No running processes found in NPU\s+[0-9]+" | head -n 1 | awk '{print $NF}')
[ -n "$free_npu" ] && export ASCEND_RT_VISIBLE_DEVICES=$free_npu
```

### 7. 一键量化（容器内，核心命令）
```bash
msmodelslim quant \
    --model_path ~/qwen36_27b_base \
    --save_path ~/qwen36_27b_w8a8 \
    --device npu \
    --model_type Qwen3.6-27B \
    --quant_type w8a8 \
    --trust_remote_code true
```
关键参数含义（原文）：
- `--model_type Qwen3.6-27B` 与 `--quant_type w8a8`：触发 msModelSlim 自动匹配该模型的 W8A8 最佳实践配置；
- `--trust_remote_code true`：允许加载 Qwen 自定义模型代码。

### 8. 校验产物（容器内）
```bash
ls -al ~/qwen36_27b_w8a8
du -sh ~/qwen36_27b_base ~/qwen36_27b_w8a8
```

### 9. 切换 transformers 版本以适配 vLLM（容器内）
```bash
pip install -i https://repo.huaweicloud.com/repository/pypi/simple/ transformers==4.57.6
```

### 10. 选择 2 张空闲 NPU（容器内，推理阶段）
```bash
free_npus_raw=$(npu-smi info | grep -oE "No running processes found in NPU\s+[0-9]+" | head -n 2 | awk '{print $NF}')
npu_count=$(echo "$free_npus_raw" | wc -w)
[ "$npu_count" -eq 2 ] && export ASCEND_RT_VISIBLE_DEVICES=$(echo "$free_npus_raw" | paste -s -d ',')
```

### 11. 启动 vLLM-Ascend 在线推理服务（容器内，命令会持续占用终端）
```bash
vllm serve ~/qwen36_27b_w8a8 \
    --port 5678 \
    --served-model-name Qwen3.6-27B-W8A8 \
    --quantization ascend \
    --tensor-parallel-size 2 \
    --max-model-len 8192 \
    --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' \
    --additional-config '{"enable_cpu_binding":true}'
```
关键参数含义（原文）：
- `--quantization ascend`：指定 Ascend 量化推理后端，加载 msModelSlim 产出的 W8A8 权重；
- `--tensor-parallel-size 2`：2 卡张量并行；
- `--max-model-len 8192`：最大序列长度；
- `--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`：Decode 阶段编译为静态图加速；
- `--additional-config '{"enable_cpu_binding":true}'：CPU-NPU NUMA 亲和，降低 Host-Device 通信延迟。

### 原文未涉及的事项
- 客户端推理请求样例（curl / OpenAI SDK 调用命令）：**原文在"启动约需 4~"处截断，未给出**；
- 服务停止 / 容器清理命令：**原文未涉及**；
- 离线包完整性校验（SHA256、签名校验）：**原文未涉及**；
- W8A8 之外的其他量化格式（如 W4A16、KV cache 量化、混合精度）的调用示例：**原文未涉及**，应前往 `../user_guide/README.md` 查看。
