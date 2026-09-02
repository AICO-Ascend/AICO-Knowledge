# tutorial_aishell

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/audio/Wenet_Conformer_for_Pytorch/docs/tutorial_aishell.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/audio/Wenet_Conformer_for_Pytorch/docs/tutorial_aishell.md

# 一体化深度解读: Tutorial on AIShell

## 【定位】

这篇文档是 WeNet 语音识别工具包在 AISHELL-1 中文语音数据集上的端到端实战教程, 目标读者是希望快速跑通从数据准备到模型导出全流程 ASR 实验的工程师/研究人员, 通过分阶段执行 `example/aishell/s0/run.sh` 让用户理解整个训练-解码-导出的流水线。

---

## 【技术要点】

1. **完整的 8 阶段流水线** (Stage -1 到 Stage 6), 每个阶段都是 `run.sh` 中的一个子任务, 既可逐步手动执行也可一键全跑 (`--stage -1 --stop_stage 6`)。

2. **原始 wav 作为输入, TorchAudio 实时提特征**: `example/aishell/s0` 使用原始 wav 作为输入, 通过 TorchAudio 在 dataloader 中即时 (just-in-time) 提取特征, 配合 `tools/compute_cmvn_stats.py` 计算全局 CMVN (cepstral mean and variance normalization) 统计量用于特征归一化; 设置 `cmvn=false` 可跳过该步骤。

3. **标签字典采用字符级 (AISHELL-1 用汉字字符)**: 字典是 label token 与整数索引的映射, 包含三个特殊 token: `<blank>` (CTC 空白符, id 0)、`<unk>` (未登录词, id 1)、`<sos/eos>` (语音开始/结束符, 共享同一 id, 例中 id 4232), 普通汉字按序分配 id (例: 一=2, 丁=3, ..., 龚=4230, 龟=4231)。

4. **WeNet 数据格式 `data.list` 为 JSON 行**: 每行包含三个字段 — `key` (utterance 标识)、`wav` (音频绝对路径)、`txt` (归一化后的转写文本, 在训练阶段 on-the-fly 切分为模型单元); 另提供 `shard` 格式用于 5k 小时以上大数据训练。

5. **多 GPU DDP 训练配置**: 推荐 `dist_backend="nccl"`, 不兼容时回退 `gloo` 或 `torch==1.6.0`; 通过 `CUUDA_VISIBLE_DEVICES="0,1,2,3,6,7"` 选择物理卡; 支持断点续训, 设置 `checkpoint=exp/your_exp/$n.pt` 后从 `$n+1.pt` 继续。

6. **四种解码方式**: `ctc_greedy_search`、`ctc_prefix_beam_search`、`attention`、`attention_rescoring` (其中 `attention_rescoring` 一般为最佳); `--beam_size` 越大结果可能越好但计算开销越高; `--batch_size` 仅对 `ctc_greedy_search` 和 `attention` 可大于 1, `ctc_prefix_beam_search` 和 `attention_rescoring` 必须为 1。

---

## 【关键机制与数据】

### 工作原理与数据流 (原文):

1. **Stage -1 (下载数据)**: 将 aishell-1 数据下载到本地 `$data` 路径 (需设置**绝对路径**, 如 `/home/username/asr-data/aishell/`), 若已下载则修改 `$data` 变量并从 Stage 0 开始。

2. **Stage 0 (数据组织)**: `local/aishell_data_prep.sh` 将原始 aishell-1 数据组织成两个制表符分隔的文件:
   - `wav.scp`: `wav_id` + `wav_path`
   - `text`: `wav_id` + `text_label`

3. **Stage 1 (CMVN 提取)**: 仅将训练集 `wav.scp` 和 `text` 复制到 `raw_wav/train/` 目录, 因为特征由 TorchAudio 在 dataloader 中即时计算; 同时用 `tools/compute_cmvn_stats.py` 计算全局 CMVN 统计量。

4. **Stage 2 (字典生成)**: 生成 token→id 映射字典, 三个特殊符号固定位置: `<blank>`=0、`<unk>`=1、`<sos/eos>`=最后一 id (共享)。

5. **Stage 3 (WeNet 数据格式)**: 输出 `data/train/data.list`, 每行为一个 JSON 对象; `txt` 在训练时 on-the-fly 切分; 文本已**归一化**。

6. **Stage 4 (NN 训练)**: YAML 配置文件位于 `conf/`, 提供 transformer 与 conformer 等多种模型 (参考 `conf/train_conformer.yaml`); 通过 TensorBoard 监控 loss。

7. **Stage 5 (识别)**: 若 `${average_checkpoint}=true`, 取交叉验证集上最好的 `${average_num}` 个模型做平均; 解码后将结果送入 `tools/compute-wer.py` 计算 WER/CER。

8. **Stage 6 (模型导出)**: `wenet/bin/export_jit.py` 用 Libtorch 导出训练好的模型, 供 C++ 等其他语言用于推理。

### 性能数据 (原文有的):
- **原文:** 8 张 2080 Ti 机器上, 50 个 epoch 训练**不到一天**可完成。
- **原文:** 不修改 recipe 直接运行, WER ≈ **5%**。

---

## 【表格解读】

**原文无表格** (文档中仅有 wav.scp、text、字典、data.list 等代码块示例, 无 markdown 表格结构)。

---

## 【公式解读】

**原文无公式** (文档未包含任何 LaTeX 数学公式或伪代码算法表达式)。

---

## 【关联】

该文档作为 AIShell-1 教程, 与以下外部特性/模块存在关联 (文末链接信息):

1. **上游/安装指引**: 引用 WeNet 主仓 `Installation` (https://github.com/wenet-e2e/wenet#installation) 作为环境准备的前置步骤。

2. **大数据集 recipe**: Stage 3 中提到 `shard` 格式 `data.list`, 用于超过 5k 小时的大规模训练, 并指引到:
   - `gigaspeech` recipe (10k 小时, https://github.com/wenet-e2e/wenet/tree/main/examples/gigaspeech/s0)
   - `wenetspeech` recipe (10k 小时, https://github.com/wenet-e2e/wenet/tree/main/examples/wenetspeech/s0)

3. **特征提取依赖**: Stage 1 中引用 TorchAudio (https://pytorch.org/audio/stable/index.html) 作为即时特征提取器。

4. **解码算法理论依据**: Stage 5 中四种解码方法的细节指向 [U2 paper](https://arxiv.org/pdf/2012.05481.pdf)。

5. **社区反馈渠道**: 文档开头给出 GitHub [issues](https://github.com/mobvoi/wenet/issues) 作为问题反馈入口。

---

## 【使用方法】

### 启用方式 / 命令 (原文有则写):

```bash
# 切换到 recipe 目录
cd example/aishell/s0

# 方式 1: 分阶段手动执行 (建议新手使用)
bash run.sh --stage -1 --stop_stage -1   # 下载数据
bash run.sh --stage 0 --stop_stage 0     # 准备训练数据
bash run.sh --stage 1 --stop_stage 1     # 提取 CMVN
bash run.sh --stage 2 --stop_stage 2     # 生成字典
bash run.sh --stage 3 --stop_stage 3     # 准备 WeNet 数据格式
bash run.sh --stage 4 --stop_stage 4     # NN 训练
bash run.sh --stage 5 --stop_stage 5     # 识别与解码
bash run.sh --stage 6 --stop_stage 6     # 导出模型

# 方式 2: 一键全跑
bash run.sh --stage -1 --stop_stage 6
```

### 关键配置项 (原文):

- **数据路径**: `run.sh` 中的 `$data` 变量必须设为**绝对路径**, 如 `/home/username/asr-data/aishell/`。
- **GPU 选择**: `export CUDA_VISIBLE_DEVICES="0,1,2,3,6,7"` (示例: 使用物理卡 0,1,2,3,6,7)。
- **分布式后端**: `dist_backend="nccl"` (推荐), 不兼容时改 `gloo` 或 `torch==1.6.0`。
- **断点续训**: `checkpoint=exp/your_exp/$n.pt`, 然后执行 `run.sh --stage 4`。
- **CMVN 开关**: `cmvn=false` 跳过 CMVN 计算。
- **模型配置**: YAML 文件位于 `conf/`, 参考 `conf/train_conformer.yaml`。
- **模型平均**: `${average_checkpoint}=true` 时, 取交叉验证集上最好的 `${average_num}` 个模型平均。
- **解码参数**: `--beam_size` (beam 越大越好但越慢)、`--batch_size` (CTC greedy/attention 可 >1, CTC prefix beam/attention rescoring 必须 =1)。
- **TensorBoard 监控**: `tensorboard --logdir tensorboard/$your_exp_name/ --port 12598 --bind_all`。
- **自定义数据**: 把数据组织成 `wav.scp` + `text` 两个文件, 从 Stage 1 开始。
