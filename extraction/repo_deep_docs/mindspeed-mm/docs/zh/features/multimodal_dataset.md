# MultiModal Dataset

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/multimodal_dataset.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/multimodal_dataset.md

# 多模态数据集 (MultiModal Dataset) 一体化深度解读

## 【定位】
本文档解决多模态训练中「单/多数据集灵活切换」与「新模型数据模块接入」的工程问题，描述 mindspeed-mm 套件在多模态数据加载与预处理层面的扩展能力。

## 【技术要点】
1. **多数据集配置方式**：以 InternVL 为例，将 `basic_parameters` 由对象改为列表，每一项独立配置 `data_path` / `data_folder` / `repeat_time`，即可同时训练多个数据集（如 dataset1 与 dataset2）。
2. **`repeat_time` 比例控制**：`repeat_time` 大于 1 时样本重复相应倍数；小于 1 时仅取前侧相应比例的样本，用于调整不同数据集在训练中的占比。
3. **两类 dataset_type 的多数据集用法**：`dataset_type: multimodal`（如 InternVL）使用列表式 `basic_parameters`；`dataset_type: huggingface`（如 Qwen 系列）多数据集需按逗号分隔方式配置，参见 `building_data_for_VLModel.md`。
4. **数据模块三段式接入流程**：图像视频预处理 → 数据集 `__getitem__` 字典封装 → 通用 utils 预处理方法，分别落在三个文件路径下，便于按模型拆分职责。
5. **返回字典的字段约束**：`multimodal_dataset.py` 在 `__getitem__` 中通过 `_init_return_dict` 初始化返回字典，并在 return 前由 `_filter_return_dict_keys` 过滤多余 key；新增 key 必须在 `_init_return_dict` 中显式登记。
6. **默认返回字段示例**：`pixel_values`、`image_flags`、`input_ids`、`labels`、`attention_mask` 等（原文以 `...` 省略其余字段）。

## 【关键机制与数据】
- **工作机制**：在 `multimodal_dataset.py` 的 `__getitem__` 调用链中，先用 `_init_return_dict` 建立一个含有所有预期键的字典框架，模型专属的预处理逻辑填充这些字段；return 时 `_filter_return_dict_keys` 负责剔除模型不需要的 key，保证下游 collator/模型只看到有效字段。
- **数据流方向**：`multimodal_image_video_preprocess.py`（图像/视频预处理）→ `multimodal_dataset.py`（样本级组装与过滤）→ `utils.py`（模型级 preprocess）→ 训练循环。该流程决定了新模型接入时需要分别改三个文件，缺一不可。
- **数据样本过滤语义**：`repeat_time < 1` 取前侧比例样本，相当于对数据集做截断采样，可与不同数据集轮次混合以调整比例；原文未给出具体数值示例，仅给出语义说明。

> 原文未提供任何性能/吞吐/精度类数据。

## 【表格解读】
**原文无表格。** 所有参数都以 JSON 代码块形式给出，未以表格形式呈现。

## 【公式解读】
**原文无公式。** 文中未出现任何 LaTeX 或伪代码公式。

## 【关联】
- 文档显式引用了 `./building_data_for_VLModel.md`（标题：针对VL模型的数据构造），用于说明 `dataset_type: huggingface`（Qwen 系列）场景下多数据集的逗号分隔配置方式，与本文 `multimodal_dataset_type` (InternVL) 的列表式配置形成互补。
- 与多模态数据模块的三个文件强耦合：
  - `mindspeed_mm/data/data_utils/multimodal_image_video_preprocess.py`：图像/视频预处理
  - `mindspeed_mm/data/datasets/multimodal_dataset.py`：数据集 `__getitem__` 与字典封装
  - `mindspeed_mm/data/data_utils/utils.py`：模型 preprocess
- 与示例配置 `examples/internvl3.5/data.json` 配套使用，是 InternVL3.5 模型数据准备的入口。

## 【使用方法】

**多数据集训练（以 InternVL 为例）：**

将单数据集配置：
```json
"basic_parameters": {
    "data_path": "/path/dataset_json_path",
    "data_folder": "/path/dataset_root_path",
    "repeat_time": 1
}
```
改为列表配置：
```json
"basic_parameters": [{
    "data_path": "/path/dataset1_json_path",
    "data_folder": "/path/dataset1_root_path",
    "repeat_time": 1
},
{
    "data_path": "/path/dataset2_json_path",
    "data_folder": "/path/dataset2_root_path",
    "repeat_time": 1
}]
```

**`repeat_time` 行为：**
- `> 1`：样本重复相应倍数。
- `< 1`：仅取前侧相应比例的样本。

**适用类型：**
- `dataset_type: multimodal`（如 InternVL）：使用上述列表方式。
- `dataset_type: huggingface`（如 Qwen 系列）：按逗号分隔方式配置，详见 `./building_data_for_VLModel.md`。

**新模型数据模块添加流程（3 步）：**
1. 在 `mindspeed_mm/data/data_utils/multimodal_image_video_preprocess.py` 添加对应模型的图像和视频预处理逻辑。
2. 在 `mindspeed_mm/data/datasets/multimodal_dataset.py` 中，若 `__getitem__` 返回需要新增 key，必须在 `_init_return_dict` 中显式添加（返回字典默认包含 `pixel_values`、`image_flags`、`input_ids`、`labels`、`attention_mask` 等字段，return 前会经过 `_filter_return_dict_keys` 过滤多余 key）。
3. 在 `mindspeed_mm/data/data_utils/utils.py` 添加对应模型的 preprocess 方法。
