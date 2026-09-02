# Test model, please specify the model you want to test by --checkpoint

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/audio/Wenet_Conformer_for_Pytorch/docs/tutorial_librispeech.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/audio/Wenet_Conformer_for_Pytorch/docs/tutorial_librispeech.md

# LibriSpeech Tutorial 深度解读

## 【定位】
本文档是 WeNet 端到端语音识别框架在 **LibriSpeech 数据集** 上的标准训练教程，描述了从数据下载、特征准备、词典构建、数据格式转换到神经网络训练的完整 9 阶段（Stage -1 至 Stage 7）流水线流程，目的是帮助用户基于 `example/librispeech/s0/run.sh` recipe 在 LibriSpeech 上复现并理解 WeNet 端到端 ASR 的全流程训练方法。

---

## 【技术要点】

1. **数据来源与变量**：使用 OpenSLR 上的 LibriSpeech 数据，原始数据路径为 `$datadir=/export/data/en-asr-data/OpenSLR/`，下载地址 `data_url=www.openslr.org/resources/12`，包含 7 个子集：`dev-clean`、`test-clean`、`dev-other`、`test-other`、`train-clean-100`、`train-clean-360`、`train-other-500`。

2. **阶段式流水线控制**：通过 `run.sh --stage N --stop_stage N` 控制单阶段执行，整体可通过 `bash run.sh --stage -1 --stop_stage 7` 一键执行；可分阶段执行以调试每个环节的中间结果。

3. **数据准备 (Stage 0)**：使用 `local/data_prep_torchaudio.sh` 将原始数据组织成两个标准文件 —— **`wav.scp`**（`wav_id \t wav_path`）与 **`text`**（`wav_id \t text_label`）。自定义数据只需组织成这两个文件即可从 Stage 1 继续。

4. **CMVN 特征归一化 (Stage 1)**：合并 3 个训练子集得到 `train_960`（对应 100+360+500 小时）、合并 dev 子集得到 `dev`，通过 `tools/compute_cmvn_stats.py --num_workers 16 --train_config $train_config --in_scp .../wav.scp --out_cmvn .../global_cmvn` 提取全局 CMVN（cepstral mean and variance normalization）统计量；可通过设置 `cmvn=false` 跳过。

5. **BPE 词典构建 (Stage 2)**：使用 [sentencepiece](https://github.com/google/sentencepiece) 在训练文本上训练 BPE 模型；词典前三行为 `<blank> 0`（CTC 空白符）、`<unk> 1`（OOV token）、`<sos/eos>`（注意力编解码器共享 id，紧跟词典末尾）；BPE 单元数由变量 `${nbpe}` 控制，模式由 `${bpemode}` 控制，词典最终会包含 `<sos/eos>` 等特殊符号（如示例中词典大小为 5002，`▁YOU=4995`，`<sos/eos>=5001`）。

6. **数据格式转换与大规模扩展 (Stage 3)**：通过 `tools/make_raw_list.py` 生成 WeNet 所需的 `data.list`（每行为 JSON，包含 `key`、`wav`、`txt` 三字段）；对于超大数据集（>5k 小时），另有 `shard` 格式的 `data.list`，参考 [gigaspeech](https://github.com/wenet-e2e/wenet/tree/main/examples/gigaspeech/s0)（10k 小时）或 [wenetspeech](https://github.com/wenet-e2e/wenet/tree/main/examples/wenetspeech/s0)（10k 小时）两个 example。

7. **分布式训练 (Stage 4，部分截断)**：支持 NCCL/Gloo 分布式后端，通过 `ddp_init` 文件初始化分布式进程；根据 `$CUDA_VISIBLE_DEVICES` 自动检测 GPU 数量，逐卡启动 `python wenet/bin/train.py --gpu ... --config $train_config`；训练完成后 `train.py` 会将 `$train_config` 写入 `$dir/train.yaml`（含输入输出维度）以供推理与模型导出使用。

---

## 【关键机制与数据】

- **原文**: WeNet 端到端 ASR 的核心建模单元可选 char 或 BPE，原文明确指出"BPE typically shows better result"，因此本 recipe 选用 BPE 作为建模单元。BPE 由 sentencepiece 在 librispeech 训练文本上训练得到，并通过 `tools/spm_encode` 编码后映射为整数索引写入词典。

- **原文**: 三类特殊 token 在词典中具有固定语义与索引位置：
  - `<blank>` → 索引 0（CTC 的空白符号）
  - `<unk>` → 索引 1（OOV 兜底符号）
  - `<sos/eos>` → 紧跟词典末尾的最后一个 id（注意力编解码器训练的 SOS/EOS 共享 id）

- **原文**: LibriSpeech 数据流的完整链路为：原始 .flac 音频 → `data_prep_torchaudio.sh` 整理为 `wav.scp` + `text` → 合并为 `train_960`/`dev` → 提取全局 CMVN → sentencepiece 训练 BPE → `make_raw_list.py` 生成 `data.list`（JSON 格式，每行含 `key`/`wav`/`txt`）→ `train.py` 读取进行分布式训练。

- **原文**: 关于性能数字，原文未给出具体的 WER/CER 等指标数据，仅描述机制与流程。

---

## 【表格解读】

原文无表格（无参数表、性能对比表或配置项表格）。仅以代码块与列表形式呈现了：
- 7 个 LibriSpeech 子集的列表
- `wav.scp` 文件示例
- `text` 文件示例
- 词典示例（`<blank> 0` 至 `<sos/eos> 5001`）
- `data.list` JSON 行示例

这些均不是结构化的 markdown 表格，故按要求标注为"原文无表格"。

---

## 【公式解读】

原文无公式（无 LaTeX 数学公式或伪代码形式的公式定义）。原文仅包含 shell 命令、文件路径、JSON 示例和解释性文本。

---

## 【关联】

本文档是 WeNet 项目 LibriSpeech recipe 的教程入口，与以下上下游模块/资源存在关联（基于文末的内部与外部链接信息）：

- **上游依赖**：[WeNet Installation](https://github.com/wenet-e2e/wenet#installation) — 完成 WeNet 环境安装是运行本教程的前提。
- **同类数据集扩展**：[gigaspeech example](https://github.com/wenet-e2e/wenet/tree/main/examples/gigaspeech/s0) 与 [wenetspeech example](https://github.com/wenet-e2e/wenet/tree/main/examples/wenetspeech/s0) — 当数据规模超过 5k 小时（这两份均为 10k 小时）时，需使用 WeNet 的 `shard` 格式 `data.list`；本教程 Stage 3 中明确提及这两个 reference recipe。
- **依赖工具链**：
  - [sentencepiece](https://github.com/google/sentencepiece) — 用于 Stage 2 中 BPE 子词单元的训练与编码；原文注明"We borrowed these code and scripts which are related bpe from ESPnet"，表明该 BPE 处理流程借鉴自 ESPnet。
  - torchaudio — 用于 Stage 0 的 `data_prep_torchaudio.sh` 音频数据预处理。
  - Kaldi — Stage 1 注释中提到"You can utilize Kaldi recipes in most cases"，可在设计 train/dev 划分时参考 Kaldi 风格脚本。
- **问题反馈渠道**：教程开头给出 [GitHub issues](https://github.com/mobvoi/wenet/issues) 作为问题反馈入口。
- **代码仓定位**：本文档位于 `modelzoo-pytorch` 仓的 `PyTorch/built-in/audio/Wenet_Conformer_for_Pytorch/docs/tutorial_librispeech.md`，是模型仓对上游 WeNet `examples/librispeech/s0/run.sh` recipe 的迁移/适配文档。

---

## 【使用方法】

### 启动方式（原文 Stage 0 起逐阶段执行）

```bash
cd example/librispeech/s0
bash run.sh --stage -1 --stop_stage -1   # 下载数据
bash run.sh --stage 0 --stop_stage 0     # 准备 wav.scp/text
bash run.sh --stage 1 --stop_stage 1     # 提取 CMVN
bash run.sh --stage 2 --stop_stage 2     # 训练 BPE 与生成词典
bash run.sh --stage 3 --stop_stage 3     # 生成 WeNet data.list
bash run.sh --stage 4 --stop_stage 4     # 神经网络训练
bash run.sh --stage 5 --stop_stage 5     # （原文被截断）
bash run.sh --stage 6 --stop_stage 6
bash run.sh --stage 7 --stop_stage 7
```

或一键运行全部阶段：
```bash
bash run.sh --stage -1 --stop_stage 7
```

### 关键配置项（脚本中变量）

- `$data`（即 `$datadir`）：数据根目录，默认 `/export/data/en-asr-data/OpenSLR/`；若已下载数据需修改此变量并从 `--stage 0` 启动。
- `$train_config`：训练配置文件路径，传给 `train.py --config`。
- `$wave_data`：处理后数据目录，默认 `data`。
- `$train_set`：训练集名称（`train_960`）。
- `${nbpe}` / `${bpemode}`：BPE 词表大小与模式，控制 `tools/spm_train` 与词典生成。
- `cmvn`（布尔）：控制是否提取 CMVN 特征；设为 `false` 可跳过 Stage 1。
- `$CUDA_VISIBLE_DEVICES`：控制训练时使用的 GPU，Stage 4 通过此环境变量自动检测 `num_gpus` 并逐卡启动分布式训练。
- `$dir`：训练输出目录，保存 checkpoint、`train.yaml`（含输入输出维度，供推理与模型导出使用）等。

### 训练命令示例（Stage 4，原文部分截断）

```bash
INIT_FILE=$dir/ddp_init
rm -f $INIT_FILE
init_method=file://$(readlink -f $INIT_FILE)
dist_backend="nccl"
num_gpus=$(echo $CUDA_VISIBLE_DEVICES | awk -F "," '{print NF}')
for ((i = 0; i < $num_gpus; ++i)); do
  gpu_id=$(echo $CUDA_VISIBLE_DEVICES | cut -d',' -f$[$i+1])
  python wenet/bin/train.py --gpu $gpu_id --config $train_config ...
done
```

### 启用前置条件
- 必须先按照 [WeNet Installation](https://github.com/wenet-e2e/wenet#installation) 完成环境安装。
- 自定义数据集：仅需组织为 `wav.scp` + `text` 两个文件，然后从 Stage 1 开始执行。
- 大数据集（>5k 小时）：需使用 `shard` 格式 `data.list`，参考 gigaspeech/wenetspeech recipe。

> 注：原文 Stage 5/6/7 的具体内容在提供的片段中已被截断，故上述使用方法中 Stage 5 及之后的具体命令以"原文未涉及"对待；Stage 4 的 `train.py` 命令行参数（如 `--config` 后的其余 flag）也因截断未能完整呈现。
