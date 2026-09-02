# 教程 1：如何编写配置文件

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/1_config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/1_config.md

# 一体化深度解读：MMAction2 配置文件编写教程

---

## 【定位】

本教程系统说明 MMAction2（OpenMMLab 视频理解工具箱）如何以 **Python 文件作为配置文件**，通过模块化 + 继承的设计，支撑动作识别 / 时序动作检测 / 时空动作检测三大任务的实验配置编写与命令行覆写。

---

## 【技术要点】

1. **Python 风格的配置文件 + 继承层级**  
   - 所有配置文件置于 `$MMAction2/configs`，通过 `_base_` 字段引用父配置，最大继承深度为 **3 层**。
   - `config/_base_` 下预置三类基本组件：`model`、`schedule`、`default_runtime`；TSN、I3D、SlowOnly 等方法均由这三类组件组合而成，被称作**原始配置（primitive）**。

2. **配置打印命令**  
   ```bash
   python tools/analysis/print_config.py /PATH/TO/CONFIG
   ```
   用于展开继承关系后查看完整的最终配置。

3. **命令行覆写 `--cfg-options`**（`tools/train.py`、`tools/test.py` 时使用）  
   - 改字典：`--cfg-options model.backbone.norm_eval=False`（会影响 `train` 模式下 backbone 中所有 BN 模块）。
   - 改列表中字典键：`--cfg-options data.train.pipeline.0.type=DenseSampleFrames`。
   - 改列表/元组：**必须加引号，且引号内不能有空格**，例如 `--cfg-options workflow="[(train,1),(val,1)]"`。

4. **配置文件命名规则模板**  
   ```
   {model}_[model setting]_{backbone}_[misc]_{data setting}_[gpu x batch_per_gpu]_{schedule}_{dataset}_{modality}
   ```
   `{xxx}` 为必要域，`[yyy]` 为可选域。

5. **三类任务的独立子文件系统**  
   - 时序动作检测（以 BMN 为例）；
   - 动作识别（以 TSN 为例，**原文示例被截断**，仅余 "```pyt" 起始标记）；
   - 时空动作检测（在原文目录中列出，但本节正文中**原文未涉及**示例代码）。

6. **新方法的目录约定**  
   - 若实现独立新方法，应在 `configs/TASK`（如 `configs/recognition`、`configs/detection`）下新建文件夹，而非寄生于现有方法目录。

---

## 【关键机制与数据】

- **配置继承与组合机制**（原文：每个 `_base_` 文件夹下组件可被任意组合；同目录下应只存在 **一个** 原始配置，其它配置继承该原始配置以保证继承深度 ≤ 3）。
- **覆写语义**（原文：字典键按原始顺序覆写；列表中的字典可通过下标索引覆写；列表/元组必须加引号，且引号内不允许空格）。
- **BMN（时序动作检测）配置关键参数**（原文以注释形式给出）：
  - 模型：`type='BMN'`，`temporal_dim=100`，`boundary_ratio=0.5`，`num_samples=32`，`num_samples_per_bin=3`，`feat_dim=400`。
  - NMS 与后处理：`soft_nms_alpha=0.4`，`soft_nms_low_threshold=0.5`，`soft_nms_high_threshold=0.9`，`post_process_top_k=100`。
  - 数据：`dataset_type='ActivityNetDataset'`；特征根目录 `data/activitynet_feature_cuhk/csv_mean_100/`；标注文件分别对应 `anet_anno_train.json` / `_val.json` / `_test.json`。
  - 数据加载：`videos_per_gpu=8`（训练）、`videos_per_gpu=1`（验证）、`videos_per_gpu=2`（测试）；`workers_per_gpu=8`；训练 `drop_last=True`。
  - 训练流水线：`LoadLocalizationFeature` → `GenerateLocalizationLabels` → `Collect(keys=['raw_feature','gt_bbox'])` → `ToTensor(keys=['raw_feature'])` → `ToDataContainer(fields=[dict(key='gt_bbox', stack=False, cpu_only=True)])`。验证流水线额外携带 `video_name / duration_second / duration_frame / annotations / feature_frame` 等 meta；测试流水线省略标签生成步骤。
  - 优化器：`type='Adam'`，`lr=0.001`，`weight_decay=0.0001`，`grad_clip=None`。
  - 学习率：`policy='step'`，`step=7`。
  - 训练时长：`total_epochs=9`；`checkpoint_config.interval=1`；`evaluation.interval=1`，`metrics=['AR@AN']`。
  - 日志：`log_config.interval=50`，使用 `TextLoggerHook`，并注释可启用 `TensorboardLoggerHook`。
  - 分布式：`dist_params=dict(backend='nccl')`；`log_level='INFO'`；`workflow=[('train', 1)]`。
  - 输出：`output_config=dict(out=f'{work_dir}/results.json', output_format='json')`。

> 说明：性能/精度数据（如 mAP、AR@AN 数值）原文未给出，故此处不补全。

---

## 【表格解读】

### 表 1：配置文件命名域含义（按原文逐字还原）

| 命名域（原文格式） | 是否必选 | 含义（原文） | 示例 |
|---|---|---|---|
| `{model}` | 必要 | 模型类型 | `tsn`、`i3d` |
| `[model setting]` | 可选 | 一些模型上的特殊设置 | — |
| `{backbone}` | 必要 | 主干网络类型 | `r50`（ResNet-50） |
| `[misc]` | 可选 | 模型的额外设置或插件 | `dense`、`320p`、`video` |
| `{data setting}` | 必要 | 采帧数据格式，形如 `{clip_len}x{frame_interval}x{num_clips}` | `1x1x3`（在 TSN 命名示例中出现） |
| `[gpu x batch_per_gpu]` | 可选 | GPU 数量以及每个 GPU 上的采样 | `2x8`（在 BMN 命名示例中出现） |
| `{schedule}` | 必要 | 训练策略设置 | `20e` 表示 20 个 epoch |
| `{dataset}` | 必要 | 数据集名 | `kinetics400`、`mmit` |
| `{modality}` | 必要 | 帧的模态 | `rgb`、`flow` |

**逐行解读**：
- `{model}` 与 `{backbone}` 共同锁定"算法族 + 主干"，是同名不同 backbone 复用的关键。
- `[misc]` 容纳与具体模型强耦合的插件（如 `dense` 对应 dense sampling，`320p` 标识输入分辨率），命名约定使其与原生 MM 系列保持一致。
- `{data setting}` 用 `clip_len x frame_interval x num_clips` 三元组直接刻画**采帧策略**——这是时序建模的核心超参。
- `[gpu x batch_per_gpu]` 让读者一眼读出**训练资源与 batch 组合**，便于复现与算力评估。
- `{schedule}` 强制写明 epoch 数（`e` 表示 epoch），与学习率 `policy='step'`、`step` 等超参配套阅读。
- `{dataset}` 与 `{modality}` 区分了**数据来源**与**输入模态**（RGB 帧 / 光流），后者直接决定是否需要 I3D/TSN 双流结构。

> 其它原文代码段（BMN 的 `model / train_pipeline / data / optimizer` 等）为参数字典而非表格形式，故不强行转为表格。

---

## 【公式解读】

### 式 1：配置文件命名模板（原文逐字保留）

```
{model}_[model setting]_{backbone}_[misc]_{data setting}_[gpu x batch_per_gpu]_{schedule}_{dataset}_{modality}
```

**符号说明**：
- `{model}`：算法名称（必要）。例：`tsn`、`i3d`、`bmn`。
- `[model setting]`：模型专属变体（可选）。例：`slowfast` 中的 `slow`/`fast` 区分。
- `{backbone}`：主干网络（必要）。例：`r50`。
- `[misc]`：额外插件或设置（可选）。例：`dense`、`320p`、`video`。
- `{data setting}`：采帧三元组 `clip_len × frame_interval × num_clips`（必要）。例：`8x8x1` 表示每段 8 帧、间隔 8、采样 1 段。
- `[gpu x batch_per_gpu]`：GPU 数 × 每 GPU 批大小（可选）。例：`8x16` 表示 8 卡、每卡 16。
- `{schedule}`：训练周期（必要）。例：`20e`、`100e`。
- `{dataset}`：训练数据集（必要）。例：`kinetics400`、`activitynet`。
- `{modality}`：输入模态（必要）。例：`rgb`、`flow`。

> 原文未给出其它数学公式。

---

## 【关联】

- **`config/_base_` 三组件 → `model` / `schedule` / `default_runtime`**：所有方法（TSN、I3D、SlowOnly、BMN 等）的配置文件都通过组合这三类原始组件来构建，并推荐同目录只保留 **一个** 原始配置以控制继承深度。
- **配置与训练脚本**：覆写语法服务于 `tools/train.py` 与 `tools/test.py` 的 `--cfg-options` 参数入口。
- **配置与运行时分析**：`tools/analysis/print_config.py` 用于展开并打印最终配置，是调试 `_base_` 继承链的工具。
- **配置与数据流**：配置中的 `pipeline`（如 `train_pipeline / val_pipeline / test_pipeline`）直接驱动 `LoadLocalizationFeature → GenerateLocalizationLabels → ToTensor → ToDataContainer` 等数据预处理类；这些类的细节指向 [API 文档](https://mmaction2.readthedocs.io/en/latest/api.html)。
- **配置与优化/调度**：`optimizer / optimizer_config / lr_config` 的字段命名规则与 mmcv 中 `mmcv/runner/optimizer/default_constructor.py` 与 `mmcv/runner/hooks/lr_updater.py` 一一对应；`checkpoint_config` 关联 `mmcv/runner/hooks/checkpoint.py`。
- **配置与新模块扩展**：教程末尾指向 `tutorials/5_new_modules.md`，说明配置系统与自定义 Optimizer/Model 等扩展机制同源。
- **配置与底层 mmcv 工具**：更深层的字段语义（如 `_base_`、环境变量）参考 [mmcv config 文档](https://mmcv.readthedocs.io/en/latest/utils.html#config)。
- **三大任务分支**：
  - 时序动作检测 → BMN 示例（ActivityNet 特征输入）；
  - 动作识别 → TSN 示例（原文被截断，仅余代码块起始）；
  - 时空动作检测 → 原文**仅在目录与命名章节列出**，本节未给出示例。

---

## 【使用方法】

1. **查看完整配置（展开继承）**
   ```bash
   python tools/analysis/print_config.py /PATH/TO/CONFIG
   ```

2. **命令行覆写配置**
   - 启动训练/测试：`python tools/train.py` 或 `python tools/test.py`；
   - 覆写字典：`--cfg-options model.backbone.norm_eval=False`；
   - 覆写列表中的字典键（按下标）：`--cfg-options data.train.pipeline.0.type=DenseSampleFrames`；
   - 覆写列表/元组（必须加引号，**引号内不允许空格**）：`--cfg-options workflow="[(train,1),(val,1)]"`。

3. **新建/修改配置**
   - 复用现有方法：先 `_base_ = '../tsn/tsn_r50_1x1x3_100e_kinetics400_rgb.py'`，再覆写必要字段；
   - 全新方法：在 `configs/TASK/`（如 `configs/recognition/`、`configs/detection/`）新建文件夹，并遵循"同目录仅一个原始配置、继承深度 ≤ 3"的约束；
   - 字段含义与新增模块的注册：参考 `tutorials/5_new_modules.md` 与 [API 文档](https://mmaction2.readthedocs.io/en/latest/api.html)；
   - 底层字段规范与 `_base_` 语法：参考 [mmcv config 文档](https://mmcv.readthedocs.io/en/latest/utils.html#config)。

> 原文未涉及关于本教程路径 `R(2+1)D/` 自身专属配置项的任何信息（该子目录未在教程正文中出现），故 R(2+1)D 模型具体配置文件细节**原文未涉及**。
