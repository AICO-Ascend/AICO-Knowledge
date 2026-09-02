# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/1_config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/1_config.md

# 一体化深度解读：Tutorial 1: Learn about Configs

## 【定位】

本教程系统阐述 MMAction2 (R(2+1)D 所属代码仓) 的 **配置系统使用规范**，教用户如何阅读、修改、继承和命名 Python 风格的配置文件，以便高效组织视频理解（动作识别 / 时空动作检测 / 动作定位）实验。

---

## 【技术要点】

1. **配置文件形态**：使用 Python 文件作为配置，融合**模块化 + 继承**设计；所有配置位于 `$MMAction2/configs` 目录下，查看完整配置可执行：
   ```
   python tools/analysis/print_config.py /PATH/TO/CONFIG
   ```

2. **命令行就地修改配置 `--cfg-options`**（支持三类更新）：
   - 修改 dict 键值，例如 `--cfg-options model.backbone.norm_eval=False`（将 backbone 中所有 BN 模块切回 train 模式）
   - 更新 list 中某一项，例如 `--cfg-options data.train.pipeline.0.type=DenseSampleFrames`（将第 0 个 pipeline 由 `SampleFrames` 换成 `DenseSampleFrames`）
   - 更新 list/tuple 值，例如 `--cfg-options workflow="[(train,1),(val,1)]"`（注意引号**必须加**且引号内**不允许出现空白字符**）

3. **三类基础组件（位于 `config/_base_`）**：`model`、`schedule`、`default_runtime`；由这三者各取一个即可组装出 TSN、I3D、SlowOnly 等方法，称为 **_primitive_** 配置。

4. **继承深度约束**：同一文件夹下推荐**仅保留一个 _primitive_**，其余配置通过 `_base_ = ../xxx/yyy.py` 继承，最大继承层数 = **3**；建议新方法继承已有方法（如 TSN）的结构后再做修改；若与现有方法完全不共享结构，则在 `configs/TASK` 下新建文件夹。

5. **配置文件命名约定**（必填字段 `{}`，可选字段 `[]`）：
   ```
   {model}_[model setting]_{backbone}_[misc]_{data setting}_[gpu x batch_per_gpu]_{schedule}_{dataset}_{modality}
   ```
   - `{model}`：`tsn` / `i3d` 等
   - `{backbone}`：如 `r50`（ResNet-50）
   - `{data setting}`：帧采样设置，格式 `{clip_len}x{frame_interval}x{num_clips}`，例如 `1x1x3`
   - `[gpu x batch_per_gpu]`：GPU 数 × 每 GPU batch
   - `{schedule}`：训练 schedule，如 `20e` 表示 20 epochs
   - `{dataset}`：`kinetics400`、`mmit` 等
   - `{modality}`：`rgb`、`flow` 等

6. **动作定位（BMN）配置样例关键参数**（原文给出）：
   - 模型：`type='BMN'`，`temporal_dim=100`，`boundary_ratio=0.5`，`num_samples=32`，`num_samples_per_bin=3`，`feat_dim=400`
   - 后处理：`soft_nms_alpha=0.4`，`soft_nms_low_threshold=0.5`，`soft_nms_high_threshold=0.9`，`post_process_top_k=100`
   - 数据：`dataset_type='ActivityNetDataset'`，`data_root='data/activitynet_feature_cuhk/csv_mean_100/'`，三个标注文件分别对应 train/val/test（`anet_anno_{train,val,test}.json`）
   - Pipeline 顺序：`LoadLocalizationFeature → GenerateLocalizationLabels → Collect(keys=['raw_feature','gt_bbox'], meta_name='video_meta') → ToTensor(keys=['raw_feature']) → ToDataContainer(fields=[{key:'gt_bbox', stack:False, cpu_only:True}])`；测试时省略 `GenerateLocalizationLabels`，Collect 的 keys 仅保留 `['raw_feature']`，meta_keys 增加 `duration_second / duration_frame / annotations / feature_frame`

---

## 【关键机制与数据】

- **配置继承的工作原理**：`_base_` 字段以路径形式指向父配置，加载时按字段覆盖（dict 层级合并、list 整体替换）；通过 `_base_ = ../tsn/tsn_r50_1x1x3_100e_kinetics400_rgb.py` 这种形式即可继承父配置的 model/schedule/default_runtime 等组件，仅在子配置里覆写需要差异化的字段。
- **Pipeline 列表的索引式覆盖**：`data.train.pipeline.0.type` 这种语法通过下标定位 list 内元素并替换特定 key，避免了整体重写 list，是 `--cfg-options` 最常用的精细化修改方式。
- **train_cfg / test_cfg 区分**：`train_cfg` 控制训练期行为（如 BMN 设为 `None`），`test_cfg` 控制推理期行为（BMN 设为 `dict(average_clips='score')`），两者解耦使同一模型在 train/test 阶段可拥有不同超参。
- **关于性能数据**：原文未提供任何 benchmark 指标或训练时长数字，仅在命名约定中隐含了如 `100e`（100 epochs）这种 schedule 写法，因此本节无具体性能数据可引用。

---

## 【表格解读】

**原文无表格**。

（虽存在伪表格化的命名约定模板与 BMN 参数列表，但它们以代码块/枚举形式呈现，并非 markdown 表格，故按规定标注"原文无表格"。若需对照，可参考上方【技术要点】第 5 条命名模板与第 6 条 BMN 参数。）

---

## 【公式解读】

**原文无公式**。

（无 LaTeX 数学式，亦无伪代码公式。命名约定 `{clip_len}x{frame_interval}x{num_clips}` 仅是字符串模板，不是数值公式；因此按规定标注"原文无公式"。）

---

## 【关联】

由于题目给出的内部链接信息为「(无)」，本节仅基于文档自身上下文做最小关联说明：

- **上游工具链**：本教程强依赖 `tools/train.py` 与 `tools/test.py` 来消费 `--cfg-options`；依赖 `tools/analysis/print_config.py` 来可视化合并后的完整配置。
- **依赖文档**：完整 Config 字段语义参考外部链接 [mmcv config 文档](https://mmcv.readthedocs.io/en/latest/utils.html#config)；模型/组件 API 详细参数参考 [mmaction2 API documentation](https://mmaction2.readthedocs.io/en/latest/api.html)（原文此处为外部链接）。
- **配置系统三分支**：本文档 TOC 预告了三个并列的配置子系统——
  - Config System for Action **localization**（已展开，以 BMN 为例）
  - Config System for Action **Recognition**（原文未在所提供片段中展开）
  - Config System for **Spatio-Temporal Action Detection**（原文未在所提供片段中展开）
- **同教程其他章节**：TOC 还预告「FAQ / Use intermediate variables in configs」等小节（原文未在所提供片段中展开）。

---

## 【使用方法】

**1. 查看任意配置的最终合并结果**
```
python tools/analysis/print_config.py /PATH/TO/CONFIG
```

**2. 通过脚本参数就地修改（无需改动源 .py 文件）**

| 场景 | 命令示例 |
| --- | --- |
| 修改 dict 中布尔开关 | `--cfg-options model.backbone.norm_eval=False` |
| 替换 pipeline list 第 0 项的 type | `--cfg-options data.train.pipeline.0.type=DenseSampleFrames` |
| 改写 list/tuple 类型值 | `--cfg-options workflow="[(train,1),(val,1)]"`（注意：**必须**加引号，引号内**禁止**空白字符） |

**3. 构建新实验配置（继承式）**：在 `configs/<TASK>/<method>/` 下新建 `.py` 文件，文件头写
```python
_base_ = '../tsn/tsn_r50_1x1x3_100e_kinetics400_rgb.py'
```
然后只覆写需要变更的字段即可；同一目录建议只保留 1 个 _primitive_，继承层数 ≤ 3。

**4. 完全新增方法**：若新方法与 TSN / I3D / SlowOnly 等不共享结构，则在 `configs/TASK` 下新建文件夹自行编写全部 `_base_` 组件。

**5. 命名约束**：新建配置文件须遵循 `{model}_[model setting]_{backbone}_[misc]_{data setting}_[gpu x batch_per_gpu]_{schedule}_{dataset}_{modality}` 模板，否则与社区风格不一致。

> 备注：原文「Config System for Action Recognition」「Config System for Spatio-Temporal Action Detection」「FAQ」等小节内容在本提供片段中**已被截断未出现**，故对应使用方法暂以"原文未涉及"处理；如需补充解读，请提供后续片段。
