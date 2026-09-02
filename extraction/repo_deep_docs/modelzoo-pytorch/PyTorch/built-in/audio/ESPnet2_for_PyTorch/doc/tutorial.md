# run.sh

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/audio/ESPnet2_for_PyTorch/doc/tutorial.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/audio/ESPnet2_for_PyTorch/doc/tutorial.md

# 一体化深度解读：ESPnet 使用教程（tutorial.md）

---

## 【定位】

这篇文档是 ESPnet 端到端语音处理工具包的「使用上手指南」,系统讲解如何通过 `egs/` 下的 recipe (以 AN4 数据集为例) 执行完整的 ASR 训练-解码流程,涵盖目录结构、脚本执行、训练日志监控、命令行参数覆盖、GPU 使用、多 GPU 注意事项、阶段化执行,以及 CTC/attention/hybrid 训练-解码模式的切换配置。

---

## 【技术要点】

1. **目录组织与 recipe 机制**: `espnet/` (Python 模块)、`utils/` (Kaldi 风格脚本)、`egs/<corpus>/<task>1/{run.sh, cmd.sh, path.sh, conf/, steps/, utils/}` 是每个 ASR/TTS 实验的最小可执行单元;AN4 因小巧且免费被指定为教程用数据集。

2. **执行入口与后端切换**:`cd egs/an4/asr1` 后,`./run.sh --backend chainer` 或 `./run.sh --backend pytorch` 触发全流程——数据下载 → Kaldi 风格 data prep 与特征抽取 → 字典与 JSON 格式准备 → 训练 → 识别与打分。

3. **训练日志双通道**:
   - 文本日志:`tail -f exp/${expdir}/train.log`,输出 epoch、iteration、各类 loss、validation loss/acc、elapsed_time、lr 等列;
   - 视觉化:Tensorboard 事件自动写入 `tensorboard/${expname}/`,通过 `tensorboard --logdir tensorboard` 启动,默认监听 `localhost:6006`。

4. **命令行参数机制**:借用 Kaldi 的 `utils/parse_options.sh`,在 `run.sh` 中以 `变量=默认值` 形式声明选项,即可通过 `./run.sh --<var> <value>` 覆盖,例如 `ngpu=1` → `./run.sh --ngpu 2`。

5. **GPU 与多 GPU 限制**:
   - 训练用 `--ngpu` 控制 GPU 数量 (默认 1),`--ngpu 0` 走 CPU;多卡需 `CUDA_VISIBLE_DEVICES` 指定;
   - 多 GPU 训练依赖 NCCL;**espnet1 仅支持单节点多卡,跨节点分布式只在 espnet2 支持**;
   - 不支持多 GPU 推理,需拆分任务分发;若 GPU-Util 低说明 I/O 是瓶颈,可加 `--n-iter-processes 2` 启用数据预取 (会大量消耗 CPU 内存)。

6. **训练-解码模式三态切换**:通过 `mtlalpha` (训练配置) 与 `ctc-weight` (解码配置) 控制:
   - `mtlalpha: 0.3` / `ctc-weight: 0.3, beam-size: 10` → hybrid (默认);
   - `mtlalpha: 1.0` / `ctc-weight: 1.0` → CTC,且 CTC 有 v1 (best path) 与 v2 (prefix search beam) 两套 API;
   - `mtlalpha: 0.0` / `ctc-weight: 0.0` → 纯 attention,需配 `maxlenratio`/`minlenratio` (插入错多则降 `maxlenratio`,删除错多则升 `minlenratio`)。

7. **阶段化执行**:`./run.sh --stage 3 --stop-stage 5` 可从第 3 阶段开始、第 5 阶段停止,便于失败重跑或跳过已完成的步骤。

---

## 【关键机制与数据】

**工作原理与数据流**(以一次 `./run.sh --backend pytorch` 为例):

1. `path.sh` 设定环境变量;`cmd.sh` 选定任务调度后端;
2. 按 `run.sh` 内置 stage 顺序依次执行 data prep → feature extraction → 字典与 JSON 生成 → 模型训练 (chainer/pytorch) → 解码打分;
3. 训练过程同步写出 `train.log` 与 `tensorboard/${expname}/` 事件;
4. `--stage/--stop-stage` 允许任意切片执行,`--ngpu` 与 `CUDA_VISIBLE_DEVICES` 控制硬件分配。

**原文给出的训练日志样例**(第 6–7 epoch,iteration 89700–91300):
```
epoch       iteration   main/loss   main/loss_ctc  main/loss_att  validation/main/loss  validation/main/loss_ctc  validation/main/loss_att  main/acc    validation/main/acc  elapsed_time  eps
6           89700       63.7861     83.8041        43.768                                                                                   0.731425                         136184        1e-08
6           89800       71.5186     93.9897        49.0475                                                                                  0.72843                          136320        1e-08
6           89900       72.1616     94.3773        49.9459                                                                                  0.730052                         136473        1e-08
7           90000       64.2985     84.4583        44.1386        72.506                94.9823                   50.0296                   0.740617    0.72476              137936        1e-08
7           90100       81.6931     106.74         56.6462                                                                                  0.733486                         138049        1e-08
7           90200       74.6084     97.5268        51.6901                                                                                  0.731593                         138175        1e-08
```

**原文给出的进度摘要**:`total 35.54% / this epoch 10.84% / 91300 iter, 7 epoch / 20 epochs / 0.71428 iters/sec / Estimated time to finish: 2 days, 16:23:34.613215`。

**关键数值含义**(原文隐含):
- validation 行仅在每 epoch 边界出现一次 (例如 iter 90000);
- 学习率 `eps = 1e-08`;
- CTC/attention hybrid 模式下,`main/loss ≈ main/loss_ctc + main/loss_att`;
- 训练 acc 与 validation acc 在 0.71–0.74 区间波动。

---

## 【表格解读】

**原文无表格**。

(文档以日志样例、命令块、配置片段形式呈现信息,未给出任何结构化表格;日志虽呈表格化外观,但属于终端输出截图引用,不属于文档内嵌的 markdown 表格。)

---

## 【公式解读】

**原文无公式**。

(本文是使用指南而非算法推导文档,所有数值关系 (如 `mtlalpha` 对 loss 加权) 仅以 YAML/配置项形式给出,未以 LaTeX 或伪代码公式表达。)

---

## 【关联】

**内部链接**:
- `./parallelization.md` —— 文档明确指引「集群上使用 Job scheduling system」时跳转此文件,说明本教程只覆盖单机使用,集群并行细节由 `parallelization.md` 承接。

**与文中提到的其他模块/特性的关系**:
- **Kaldi 兼容层**: `run.sh` 借用 Kaldi 的 `utils/parse_options.sh` (链接至 https://github.com/kaldi-asr/kaldi/blob/master/egs/wsj/s5/utils/parse_options.sh);data preparation 与 feature extraction 步骤遵循 Kaldi 数据准备与特征抽取规范 (http://kaldi-asr.org/doc/data_prep.html 与 http://kaldi-asr.org/doc/feat.html);
- **后端抽象**: 同一份 `run.sh` 通过 `--backend chainer` / `--backend pytorch` 切换训练后端,链接至 chainer.org 与 pytorch.org;
- **espnet1 ↔ espnet2 边界**: 文中明确指出「跨节点分布式训练只在 espnet2 支持 (https://espnet.github.io/espnet/espnet2_distributed.html)」,意味着本文其余多 GPU 指南只适用于 espnet1 单节点场景;
- **Tensorboard 集成**: 日志通过 `tensorboard/${expname}/` 与 TensorFlow/Tensorboard (https://www.tensorflow.org/guide/summaries_and_tensorboard) 解耦,ESPnet 不内置 Tensorboard 安装,需用户自行 `pip install tensorflow; pip install tensorboard`;
- **训练配置联动**: CTC/attention/hybrid 切换通过 [training configuration](https://github.com/espnet/espnet/blob/7dc9da2f07c54b4b0e878d8ef219fcd4d16a5bec/doc/tutorial.md#changing-the-training-configuration) 中的 `mtlalpha` 控制,与解码侧 `ctc-weight` 必须配对设置;
- **GPU 解码**依赖 `asr_recog.py` 中的 `--batchsize` 设置,与训练侧的 `--ngpu` 是两个独立开关。

---

## 【使用方法】

(以下为原文明确给出的启用方式与配置项汇总)

| 类别 | 命令 / 配置 | 说明 |
|---|---|---|
| 切换到 ASR 示例目录 | `cd egs/an4/asr1` | AN4 教程用 recipe |
| 选择训练后端 | `./run.sh --backend chainer` 或 `./run.sh --backend pytorch` | 决定训练框架 |
| 监控训练日志 | `tail -f exp/${expdir}/train.log` | 实时文本日志 |
| 关闭 verbose | `./run.sh --verbose 0` | (an4 默认 `--verbose 1`,因常用于调试) |
| Tensorboard 启动 | `tensorboard --logdir tensorboard` | 默认监听 `localhost:6006` |
| 覆盖脚本选项 (示例) | `./run.sh --ngpu 2` | 配合 `utils/parse_options.sh` 解析 |
| 单 GPU 训练 | `./run.sh --ngpu 1` | 默认配置 |
| 多 GPU 训练 | `./run.sh --ngpu 3` | 需预先安装 NCCL |
| 指定 GPU | `CUDA_VISIBLE_DEVICES=0,1,2 ./run.sh --ngpu 3` | Slurm 下无需手动设 |
| CPU 训练 | `./run.sh --ngpu 0` | — |
| GPU 解码 | 删去 `run.sh` 中 `ngpu=0`,给 `asr_recog.py` 设 `--batchsize ≥1`,执行 `./run.sh --stage 5 --ngpu 1` | 显著提速 |
| 数据预取 | `--n-iter-processes 2` | 缓解多 GPU I/O 瓶颈,会大量占 CPU 内存 |
| 阶段化执行 | `./run.sh --stage 3 --stop-stage 5` | 从第 3 阶段跑到第 5 阶段 |
| hybrid CTC/attention | `mtlalpha: 0.3` / `ctc-weight: 0.3, beam-size: 10` | 默认模式 |
| 纯 CTC 训练 | `mtlalpha: 1.0` | 不计算 validation acc,以 `model.loss.best` 选最佳模型 |
| CTC 解码 (best path) | `ctc-weight: 1.0, api: v1` (可省略) | — |
| CTC 解码 (prefix search beam) | `ctc-weight: 1.0, api: v2, beam-size: 10` | — |
| 纯 attention 训练 | `mtlalpha: 0.0` | — |
| 纯 attention 解码 | `ctc-weight: 0.0, beam-size: 10, maxlenratio: 0.8, minlenratio: 0.3` | 插入错多则降 `maxlenratio`,删除错多则升 `minlenratio`;`maxlenratio` 取负可设为与输入帧数无关的固定最大长度 |

**前置安装(原文未涉及)**: 文档对 Tensorboard 安装明确给出 `pip install tensorflow; pip install tensorboard`;多 GPU 需先装 NCCL (https://developer.nvidia.com/nccl),其余依赖安装本文未给出,应在 `parallelization.md` 或上层 README 中查取。

## 图文联合解读

- `50175839-2491e280-02fe-11e9-8dfc-de303804034d.png`: 1）TensorBoard标量页并列展示两后端训练/验证：acc上升，loss、loss_att、loss_ctc下降，cer/wer近零，步骤点可查看数值。  
2）蓝（PyTorch）、橙（Chainer）走势及末值接近；PyTorch训练acc略高、loss略低，验证差距很小。  
3）说明run.sh启动的完整ASR流程可统一监控不同后端，支持切换与结果对比。
