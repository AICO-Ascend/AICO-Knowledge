# (add --user if you don't have permission)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/install.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/install.md

# PointRend 安装指南深度解读

## 【定位】

本文档是 PointRend (语义分割模型) 的依赖框架 Detectron2 的安装与排障手册, 系统阐述了在 Linux/macOS 上构建或安装预编译 Detectron2 的多种路径, 并针对版本不匹配、CUDA 缺失、动态库错误等典型问题给出排查方案。

## 【技术要点】

1. **运行环境约束**: Python ≥ 3.6, PyTorch ≥ 1.7, torchvision 必须与 PyTorch 版本严格匹配, 推荐从 pytorch.org 一同安装以保证兼容性。
2. **源码编译依赖**: gcc & g++ ≥ 5.4 为必需, ninja 为可选 (但推荐以加速编译)。
3. **源码安装命令**: 通过 `python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'` 直接安装, 或本地克隆后 `python -m pip install -e detectron2` 可编辑安装。
4. **macOS 特殊处理**: 需在命令前预置环境变量 `CC=clang CXX=clang++ ARCHFLAGS="-arch x86_64"`。
5. **重建机制**: 源码本地安装后需重建时, 先用 `rm -rf build/ **/*.so` 清理旧构建产物; 重装 PyTorch 后通常必须重建。
6. **预编译包 (Linux only)**: 仅有 v0.5 (Jul 2021) 一版, 必须严格匹配 CUDA 与 PyTorch 的版本组合, 否则必须从源码编译。
7. **可选依赖**: OpenCV 可选, 但 demo 与可视化功能依赖它。
8. **GPU 架构控制**: 通过环境变量 `TORCH_CUDA_ARCH_LIST` 指定 SM 架构, 例如 `export TORCH_CUDA_ARCH_LIST="6.0;7.0"`。

## 【关键机制与数据】

**工作原理 (版本耦合机制)**
- Detectron2 预编译包通过 CUDA × PyTorch 的二维版本矩阵分发, 任一维度不匹配都会触发运行期符号错误 (如 `TH`, `aten`, `torch`, `caffe2` 未定义)。
- 源码构建时, PyTorch/torchvision/Detectron2 自动检测 GPU 设备并仅针对该设备编译, 意味着编译产物可能无法在其他 GPU 上运行。
- 大多数模型可在无 GPU 支持下做推理 (但不能训练), 通过配置 `MODEL.DEVICE='cpu'` 切换。

**性能/版本数据 (原文未提供具体性能数字, 仅有的版本/版本组合信息)**
- 原文: 预编译包对应 `v0.5 (Jul 2021)`。
- 原文: "New packages are released every few months", 即每隔数月发布新包, 因此预编译包可能落后于 master 分支最新特性。
- 原文: 预编译包矩阵中, CUDA 11.0 仅与 torch 1.7 组合有 wheel, CUDA 11.1 与 torch 1.9/1.8 组合; CUDA 9.2 仅与 torch 1.7 组合。

**排障定位流程**
- 验证 CUDA 可用性: `python -c 'import torch; from torch.utils.cpp_extension import CUDA_HOME; print(torch.cuda.is_available(), CUDA_HOME)'`, 原文要求输出 `(True, a directory with cuda)`。
- 环境信息收集: `python -m detectron2.utils.collect_env`, 需比对 "Detectron2 CUDA Compiler" / "CUDA_HOME" / "PyTorch built with - CUDA" 三处版本是否一致。
- C++ 运行时修复: `conda update libgcc` 或 `LD_PRELOAD=/path/to/libstdc++.so`。

## 【表格解读】

原文表格为 Detectron2 v0.5 (Jul 2021) 预编译包在 Linux 上的 CUDA × PyTorch 版本矩阵, 逐字还原如下:

| CUDA \ torch | torch 1.9 | torch 1.8 | torch 1.7 |
|:---:|:---:|:---:|:---:|
| **11.1** | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.9/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.8/index.html` | — |
| **11.0** | — | — | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu110/torch1.7/index.html` |
| **10.2** | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.9/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.8/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.7/index.html` |
| **10.1** | — | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu101/torch1.8/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu101/torch1.7/index.html` |
| **9.2** | — | — | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu92/torch1.7/index.html` |
| **cpu** | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.9/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.8/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.7/index.html` |

**逐行解读**:
- **CUDA 11.1 行**: 同时支持 torch 1.9 与 1.8, 但无 1.7 包, 体现较新 CUDA 版本对较旧 PyTorch 的支持已收缩。
- **CUDA 11.0 行**: 仅与 torch 1.7 配对, 是矩阵中唯一组合, 用户升级 PyTorch 1.8/1.9 后将无 11.0 预编译包可用。
- **CUDA 10.2 行**: 兼容性最好, torch 1.7/1.8/1.9 三版本全部提供 wheel, 是兼容性最广的 LTS 级别 CUDA。
- **CUDA 10.1 行**: 不支持 torch 1.9, 仅 1.7/1.8 可用。
- **CUDA 9.2 行**: 仅与 torch 1.7 组合, 已基本是历史遗留组合。
- **cpu 行**: 三种 torch 版本均提供纯 CPU 包, 用于无 GPU 推理场景, 仍受 PyTorch 版本约束。
- 表格中所有单元格的安装命令统一使用 `pip install detectron2 -f <wheel index URL>`, 通过 `-f` 指向 fbaipublicfiles 上的目录索引, 而非直接下载 whl, pip 会自动选取匹配 Python 版本与平台的包。

## 【公式解读】

原文无公式。

## 【关联】

- **`projects` 链接**: 文档明确提到预编译包 "may not be compatible with the master branch of a research project that uses detectron2 (e.g. those in [projects](projects))", 即指向 docs/tutorials 下的 projects 索引页, 列出基于 detectron2 的研究项目 (PointRend 本身即属此类)。该链接暗示: 若用户使用了 master 分支的最新特性, 必须从源码构建而非使用预编译包。
- **`docker` 引用**: 在排障章节, 当现有方案无法解决问题时, 原文要求用户 "please provide an environment (e.g. a dockerfile) that can reproduce the issue", 即建议通过 Dockerfile 复现问题, 这是与上游 issue 协作的关键工具, 但本文档本身未提供 Dockerfile 模板。
- **上游依赖链**: PointRend → Detectron2 → PyTorch/torchvision → CUDA, 任一环节版本错位都会导致运行失败; 本文档即为这一耦合关系在 PointRend 项目语境下的安装门户。
- **配套链接**: pytorch.org (安装匹配的 PyTorch+torchvision)、ninja-build.org (加速构建)、developer.nvidia.com/cuda-gpus (查询 GPU SM 架构)、detectron2 releases (查预编译包与 release notes) 共同构成完整安装知识图谱。

## 【使用方法】

**启用方式 (按平台选其一)**:

1. **Linux/macOS 源码安装 (推荐, 兼容性最强)**
   ```
   python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
   # 或本地克隆:
   git clone https://github.com/facebookresearch/detectron2.git
   python -m pip install -e detectron2
   ```

2. **Linux 预编译安装 (v0.5, Jul 2021)**: 严格按 CUDA × torch 矩阵选择命令, 示例 (CUDA 10.2 + torch 1.8):
   ```
   python -m pip install detectron2 -f \
     https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.8/index.html
   ```

3. **macOS**: 在上述命令前加 `CC=clang CXX=clang++ ARCHFLAGS="-arch x86_64"`。

**关键配置项/命令**:
- `MODEL.DEVICE='cpu'`: 切到 CPU 推理 (仅推理, 不能训练)。
- `export TORCH_CUDA_ARCH_LIST="6.0;7.0"`: 源码构建时指定 GPU SM 架构。
- `rm -rf build/ **/*.so`: 重建前清理产物。
- `python -m detectron2.utils.collect_env`: 收集环境信息, 比对三处 CUDA 版本是否一致。
- `LD_PRELOAD=/path/to/libstdc++.so`: 指定 C++ 运行时。
- `conda update libgcc`: 升级 anaconda 自带的 C++ 运行时。
- `python -c 'import torch; from torch.utils.cpp_extension import CUDA_HOME; print(torch.cuda.is_available(), CUDA_HOME)'`: 构建前验证 CUDA 是否就绪。
