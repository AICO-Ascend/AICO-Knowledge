# Quick Start

> 仓 `model-agent` · 路径 `skills/deployment/cubeai-vit-classification-npu-deploy/scripts/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/deployment/cubeai-vit-classification-npu-deploy/scripts/quickstart.md

# cubeai-vit-classification-npu-deploy · Quick Start 一体化深度解读

---

## 【定位】

**一句话**：本篇文档是「model-agent」仓库中 `cubeai-vit-classification-npu-deploy`（昇腾 NPU 上的 ViT 图像分类部署技能）的快速上手指南，面向开发者给出从环境依赖安装、模型下载、CPU/NPU 推理、精度对比到批量执行模型全流程的最小可运行命令集合。

---

## 【技术要点】

1. **依赖安装**：通过 `pip` 安装 7 个关键包 —— `torch`、`torch_npu`（昇腾 NPU 适配）、`transformers`（HuggingFace 模型接口）、`safetensors`（安全张量序列化）、`Pillow`（图像解码）、`numpy`（数值计算）、`modelscope`（魔搭模型仓库客户端）。
2. **NPU 可用性自检**：通过 `python3 -c "import torch; import torch_npu; print('NPU available:', torch.npu.is_available())"` 一行命令验证昇腾 NPU 驱动与 `torch_npu` 是否正常挂载。
3. **批量模型下载**：使用 `modelscope.snapshot_download` 一次性拉取 11 个 `cubeai/` 命名空间下的 ViT 图像分类模型，涵盖动物、植物、昆虫、鸟类、真菌等分类场景。
4. **推理入口 `scripts/run_inference.py`**：暴露三个 CLI 参数 —— `--model-path`（模型目录路径）、`--image`（待推理图像路径）、`--device`（取值 `cpu` 或 `npu`），分别演示 CPU 与 NPU 两种运行模式。
5. **精度对比入口 `scripts/run_compare.py`**：以同一 `--model-path` 与 `--image` 触发精度比对流程（未指定 `--device`，隐含由脚本内部决定）。
6. **批量执行入口 `scripts/run_all.sh`**：通过一个 bash 脚本串联所有模型的批量推理，便于回归或压测。

---

## 【关键机制与数据】

- **工作原理（原文描述的链路）**：
  1. **环境准备** → 安装 `torch` + `torch_npu` 双栈，将昇腾 NPU 纳入 PyTorch 设备体系；`transformers` 负责加载 ViT 权重，`safetensors` 提供权重文件格式支持。
  2. **模型获取** → `modelscope.snapshot_download` 按列表逐个下载 11 个 cubeai 系列分类模型到本地缓存。
  3. **单模型推理** → `scripts/run_inference.py` 读取 `--model-path` 与 `--image`，根据 `--device` 在 CPU 或 NPU 上前向传播。
  4. **精度对比** → `scripts/run_compare.py` 触发对照流程（文档未给出对比基线，疑为与参考实现/FP32 比对）。
  5. **批量运行** → `scripts/run_all.sh` 把上述流程编排为一次执行。

- **数据流（原文隐含）**：`image.jpg` → `Pillow` 解码 → `numpy`/`torch.Tensor` → `transformers` ViT 前向 → 类别概率输出；NPU 分支会由 `torch_npu` 将张量与算子下发到昇腾设备。

- **性能数据**：原文未提供任何数值（如吞吐、时延、Top-1/Top-5 准确率），故此处不臆造。

- **模型清单（原文全部 11 条，逐字保留）**：
  - `cubeai/cv_level1_protected_animals_classification`
  - `cubeai/67_cat_breeds_image_detection`
  - `cubeai/brain_model`
  - `cubeai/133_dog_breeds_image_detection`
  - `cubeai/bird_species_image_detection`
  - `cubeai/bug_classifier`
  - `cubeai/cv_edible_wild_plants_classification`
  - `cubeai/cv_forest_pest_detection`
  - `cubeai/100_butterfly_types_image_detection`
  - `cubeai/215_mushroom_types_image_detection`
  - `cubeai/birds_transform_full`

---

## 【表格解读】

**原文无表格**。本文档全部以 bash 与 Python 代码块形式承载命令，未出现 markdown 表格或参数表结构。

---

## 【公式解读】

**原文无公式**。文档不涉及任何数学公式、伪代码算法描述或 LaTeX 表达式，仅为命令行调用说明。

---

## 【关联】

由于本文档为部署技能 `cubeai-vit-classification-npu-deploy` 下的 `quickstart.md`，且题目给出 **内部链接: (无)**，故可结合以下上下文进行关联：

1. **同级脚本（同一 skills 目录下的依赖文件）**：
   - `scripts/run_inference.py` —— 本文第 3 步调用的核心推理脚本，承担 CPU/NPU 双设备前向逻辑。
   - `scripts/run_compare.py` —— 本文第 4 步调用的精度比对脚本，与 `run_inference.py` 共用模型与图像参数接口。
   - `scripts/run_all.sh` —— 本文第 5 步调用的批处理入口，通常内部循环调用 `run_inference.py` 或 `run_compare.py`。
2. **上游适配层**：依赖 `torch_npu`（华为昇腾在 PyTorch 生态的适配层）与 `transformers`（HuggingFace ViT 模型装载入口），属于「model-agent」所称的「查适配」环节。
3. **下游能力延伸**：本指南仅给出 inference & compare 路径，与同仓其他技能（如调优、文档一键生成、稳上线）通过 `model-agent` 主控串联，本文不展开。
4. **模型来源**：所有模型均来自 ModelScope 平台的 `cubeai` 命名空间，属于 CV 分类任务集合，类别数从名称可推测（如 `67_cat_breeds`、`133_dog_breeds`、`100_butterfly_types`、`215_mushroom_types`），但**原文未给出实测准确率或类别数官方说明**，此处不强行赋数字。

---

## 【使用方法】

> 以下命令均逐字摘自原文，可直接复制执行。

**① 环境安装**
```bash
pip install torch torch_npu transformers safetensors Pillow numpy modelscope
```

**② NPU 自检**
```bash
python3 -c "import torch; import torch_npu; print('NPU available:', torch.npu.is_available())"
```

**③ 批量下载 11 个 cubeai 模型**
```python
from modelscope import snapshot_download
models = [
    "cubeai/cv_level1_protected_animals_classification",
    "cubeai/67_cat_breeds_image_detection",
    "cubeai/brain_model",
    "cubeai/133_dog_breeds_image_detection",
    "cubeai/bird_species_image_detection",
    "cubeai/bug_classifier",
    "cubeai/cv_edible_wild_plants_classification",
    "cubeai/cv_forest_pest_detection",
    "cubeai/100_butterfly_types_image_detection",
    "cubeai/215_mushroom_types_image_detection",
    "cubeai/birds_transform_full",
]
for m in models:
    snapshot_download(m)
```

**④ CPU 推理**
```bash
python scripts/run_inference.py \
  --model-path /path/to/model_dir \
  --image /path/to/image.jpg \
  --device cpu
```

**⑤ NPU 推理**
```bash
python scripts/run_inference.py \
  --model-path /path/to/model_dir \
  --image /path/to/image.jpg \
  --device npu
```

**⑥ 精度对比**
```bash
python scripts/run_compare.py \
  --model-path /path/to/model_dir \
  --image /path/to/image.jpg
```

**⑦ 一键批量运行所有模型**
```bash
bash scripts/run_all.sh
```

**配置项（原文 CLI 参数一览）**

| 参数 | 所属脚本 | 取值/含义 | 来源 |
|---|---|---|---|
| `--model-path` | `run_inference.py`、`run_compare.py` | 模型目录绝对路径 | 原文 |
| `--image` | `run_inference.py`、`run_compare.py` | 待推理图像绝对路径 | 原文 |
| `--device` | `run_inference.py` | `cpu` 或 `npu`，二选一 | 原文 |

> 注：上表为对原文 CLI 字段的提取汇总，原文本身以代码块形式呈现，未以表格形式给出。
