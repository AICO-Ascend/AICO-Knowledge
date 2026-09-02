# Quick Start

> 仓 `msprof-analyze` · 路径 `docs/en/getting_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprof-analyze/docs/en/getting_started/quick_start.md

# msprof-analyze 快速入门文档深度解读

## 【定位】

本篇文档解决如何"零门槛"上手 msprof-analyze 的问题：通过一个最小可运行示例（ResNet-50 训练），串联起「采集性能数据 → 执行 advisor 分析 → 查看 HTML/XLSX 报告」的端到端工作流，让首次使用者在一个完整流程中理解工具的核心能力。

## 【技术要点】

1. **安装方式**：通过 `pip install -U msprof-analyze` 一行命令安装，详细安装方式见 `install_guide.md`。
2. **示例数据生成**：运行附录 `train_sample.py`，使用 `torch_npu.profiler` 采集 ResNet-50（默认 5 个 epoch，batch_size=8，lr=1e-3，冻结 backbone）训练的性能数据，结果输出到 `./result` 目录。
3. **advisor 完整分析命令**：`msprof-analyze advisor all -d ./result/{..._ascend_pt} -o ./advisor_output`，其中 `-d` 指定性能数据目录，`-o` 指定结果输出目录，`advisor all` 表示同时分析计算、调度、通信和整体瓶颈。
4. **输出产物**：在 `./advisor_output` 下生成两份结果——`mstt_advisor_<timestamp>.html`（用于快速概览结论与优化建议）和 `log/mstt_advisor_<timestamp>.xlsx`（用于查看详细数据）。
5. **profiler 配置关键参数**：`schedule=torch_npu.profiler.schedule(wait=0, warmup=1, active=3, repeat=1, skip_first=0)`，`profiler_level=Level1`，`activities=[CPU, NPU]`，并通过 `_ExperimentalConfig` 控制 `mstx=False`、`aic_metrics=AiCoreNone`、`data_simplification=True` 等开关。
6. **典型瓶颈识别**：示例报告中工具识别出 DataLoader 数据加载延迟为最高优先级瓶颈，并给出对应的优化建议。

## 【关键机制与数据】

**工作原理与数据流（原文）：**

1. **数据采集**：`train_sample.py` 内调用 `torch_npu.profiler.profile` 上下文管理器，按 `schedule` 的 `wait=0, warmup=1, active=3, repeat=1, skip_first=0` 配置触发 profiler 步进；通过 `tensorboard_trace_handler("./result")` 将 trace 写出。
2. **采集后目录结构**（原文）：
   ```
   msprof_3978075_20260324035119296_ascend_pt/
   ├── ASCEND_PROFILER_OUTPUT
   ├── FRAMEWORK
   ├── logs
   └── PROF_000001_20260324035119333_03978075KFFEDFAM
   ```
   该 `*_ascend_pt` 目录即为后续 `advisor` 分析的输入。
3. **分析阶段**：`msprof-analyze advisor all` 读取上述目录，按计算/调度/通信/整体四个维度同时分析，产物落盘至 `./advisor_output`。
4. **解析耗时数据（原文日志原文摘录）**：
   - CANN profiling 解析耗时：`0:00:08.090306`（约 8.09 秒）
   - 全部 profiling 解析总耗时：`0:00:12.392744`（约 12.39 秒）
5. **示例训练的 Loss 收敛曲线（原文）**：
   | Epoch | Average Loss |
   |-------|--------------|
   | 1/5   | 2.5849       |
   | 2/5   | 2.5526       |
   | 3/5   | 2.2174       |
   | 4/5   | 2.0562       |
   | 5/5   | 1.9166       |
6. **设备自动选择逻辑（原文代码）**：依次探测 `torch.npu.is_available()` → `torch.cuda.is_available()` → `cpu`，优先 NPU > CUDA > CPU；示例运行日志输出 `[INFO] Using device: npu:0`。
7. **报告样例（原文图示）**：`figures/quick_start_dataloader.png` 展示了 advisor 报告页面将 "DataLoader 数据加载延迟高" 标识为 Top-1 优化项。

## 【表格解读】

原文无传统 markdown 表格。文中以代码块形式呈现了两类结构化信息：

- **profiling 输出目录结构**（见上文「关键机制与数据」第 2 条），代表 `*_ascend_pt` 目录下含 `ASCEND_PROFILER_OUTPUT`、`FRAMEWORK`、`logs`、`PROF_<id>_<ts>_<pid>KFFEDFAM` 四类子目录。
- **训练 Loss 输出**（见上文「关键机制与数据」第 5 条），以终端日志形式展示 5 个 epoch 的 Average Loss。

两者均为代码块而非 markdown 表格，故严格意义上「原文无表格」。

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式表达式）。文中仅出现 `loss.item()` 求和后除以 `len(data_loader)` 的均值计算语义，未以公式形式书写。

## 【关联】

依据文末「Related Links」及文内跳转，文档与以下模块存在上下游/并列关系：

1. **[MindStudio Profiler Analyze Installation Guide](./install_guide.md)** — 上游：第 1 步安装环节指向该文档，补充更多安装方式。
2. **[advisor](../user_guide/advisor_instruct.md)** — 横向：本示例中使用的核心分析模块；本教程是其最小化演练，完整功能说明见该文档。
3. **[compare](../user_guide/compare_tool_instruct.md)** — 横向：与 `advisor` 同属 `msprof-analyze` 的并列子工具，本教程未涉及，但用户掌握 quick start 后可进一步使用比较分析。
4. **[cluster_analyse](../user_guide/cluster_analyse_instruct.md)** — 横向：同属 `msprof-analyze` 的并列子工具，面向多节点/集群场景，本教程未涉及。
5. **[Advanced Features](../advanced_features/README.md)** — 下游：完成 quick start 后可进入高级特性章节深入使用。
6. **附录 `[train_sample.py](#appendix)` 锚点** — 内部自引用：跳转到文末附录脚本。

## 【使用方法】

**安装（原文第 1 步）：**
```bash
pip install -U msprof-analyze
```

**生成示例性能数据（原文第 2 步）：**
```bash
python train_sample.py
```
示例脚本关键可调参数：
- `ResNet50(num_classes=10)`：分类头类别数；
- `torch.randn(80, 3, 224, 224)` / `torch.randint(0, 10, (80,))`：伪造样本数 80；
- `DataLoader(batch_size=8, shuffle=True)`：batch size；
- `train(epochs=5, lr=1e-3, freeze_backbone=True)`：训练轮数、学习率、是否冻结 backbone。

**执行 advisor 全量分析（原文第 3 步）：**
```bash
msprof-analyze advisor all \
  -d ./result/{..._ascend_pt} \
  -o ./advisor_output
```
参数说明（原文）：
- `-d`：性能数据目录；
- `-o`：分析结果输出目录；
- `advisor all`：同时分析计算、调度、通信和整体瓶颈。

**查看结果（原文第 4 步）：**
- 打开 `./advisor_output/mstt_advisor_<timestamp>.html` 查看结论与优化建议；
- 打开 `./advisor_output/log/mstt_advisor_<timestamp>.xlsx` 查看详细数据。

## 图文联合解读

- `quick_start_dataloader.png`: **图：**
层级树展示"性能优化建议"，`dataloader`下"Slow Dataloader Issues"标红（High优先级），实测244193.88us/iter远高于常规<10000us，附"检查磁盘I/O移至/cache"与"调整num_workers"两条修复建议。

**结论：**
advisor能自动定位性能瓶颈，并按高/中/低优先级分级输出可操作建议。

**与文档关系：**
该图即Quick Start第三步"查看advisor分析结果"的可视化产物，印证"采集→分析→呈现"的端到端工作流闭环。
