# (add --user if you don't have permission)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/install.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/install.md

# 深度解读:Detectron2 安装指南

## 【定位】
这篇文档是 Detectron2 的官方**安装手册**,系统性地说明如何在不同操作系统、CUDA 与 PyTorch 版本组合下安装 Detectron2,覆盖从源码编译、预编译包选择到常见安装错误的排查全流程,目的是让用户能根据自身环境选择正确的安装路径并解决构建/运行时的兼容性问题。

---

## 【技术要点】

1. **基础环境要求**:Linux 或 macOS,Python ≥ 3.6;PyTorch ≥ 1.6,且 torchvision 必须与 PyTorch 安装版本严格匹配(建议在 pytorch.org 一同安装)。
2. **可选依赖**:OpenCV 仅在 demo 与可视化场景下需要。
3. **源码构建依赖**:gcc & g++ ≥ 5.4;推荐安装 ninja 以加速编译。
4. **源码安装方式**:三条命令路径——GitHub 远程 pip 安装、本地 clone 后 `pip install -e` 可编辑安装、macOS 平台需通过 `CC=clang CXX=clang++ ARCHFLAGS="-arch x86_64"` 指定编译器。
5. **重新构建清理**:`rm -rf build/ **/*.so`(在本地 clone 场景下),且每次重装 PyTorch 后通常需重新编译。
6. **预编译包定位**:仅 Linux 可用,版本为 v0.4(Mar 2021),提供 CUDA × PyTorch 的 6×3 组合矩阵,需严格对齐官方 PyTorch 包。
7. **排查工具命令**:统一环境信息收集命令 `python -m detectron2.utils.collect_env`,以及 `TORCH_CUDA_ARCH_LIST` 环境变量控制 GPU 架构编译。

---

## 【关键机制与数据】

- **预编译包版本基线**:`v0.4 (Mar 2021)`(原文)。
- **PyTorch 适配范围**:1.6 / 1.7 / 1.8(原文)。
- **CUDA 适配范围**:9.2 / 10.1 / 10.2 / 11.0 / 11.1 / cpu(原文)。
- **CUDA 与 PyTorch 不一致时的诊断链路**(原文):
  1. 查"Detectron2 CUDA Compiler" / "CUDA_HOME" / "PyTorch built with - CUDA"三项必须同版本;
  2. 查 "architecture flags" 包含当前 GPU 的 SM 架构;
  3. 若需重编,设 `TORCH_CUDA_ARCH_LIST` 环境变量,例如原文给出的样例 `export TORCH_CUDA_ARCH_LIST="6.0;7.0"` 对应 P100s 与 V100s。
- **CUDA_HOME 验证命令**(原文):
  ```
  python -c 'import torch; from torch.utils.cpp_extension import CUDA_HOME; print(torch.cuda.is_available(), CUDA_HOME)'
  ```
  输出应为 `(True, a directory with cuda)`。
- **CPU 推理兜底**(原文):多数模型可无 GPU 运行推理但不能训练,通过配置 `MODEL.DEVICE='cpu'` 切换。
- **报错定位命令**(原文):`gdb -ex "r" -ex "bt" -ex "quit" --args python -m detectron2.utils.collect_env`,当用户无法自行解决时附在 issue 中提交。
- **GLIBCXX 类问题的修复链**(原文):老旧 anaconda 易触发,先 `conda update libgcc` 再重编;根本方案是用 `LD_PRELOAD=/path/to/libstdc++.so` 加载正确 C++ runtime。

---

## 【表格解读】

下表逐字还原原文"Install Pre-Built Detectron2 (Linux only)"中按 **CUDA × torch** 维度给出的预编译 pip 索引 URL:

| CUDA | torch 1.8 | torch 1.7 | torch 1.6 |
|---|---|---|---|
| **11.1** | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.8/index.html` | — | — |
| **11.0** | — | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu110/torch1.7/index.html` | — |
| **10.2** | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.8/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.7/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.6/index.html` |
| **10.1** | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu101/torch1.8/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu101/torch1.7/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu101/torch1.6/index.html` |
| **9.2** | — | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu92/torch1.7/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu92/torch1.6/index.html` |
| **cpu** | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.8/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.7/index.html` | `python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.6/index.html` |

**逐行解读**:
- **行维度(CUDA)**:11.1 与 11.0 仅覆盖最高两个 torch 版本,说明它们发布较晚;CUDA 10.2 是覆盖范围最广的版本,三列 torch 全部支持,适合使用较旧但仍需 GPU 训练的环境;9.2 跳过 torch 1.8,因已退出主流;**cpu** 行独立成项,说明 Detectron2 官方为纯 CPU 推理场景专门打包了一组 wheel。
- **列维度(torch)**:torch 1.7 列覆盖最全,6 个 CUDA 类别均有对应;torch 1.8 缺少 CUDA 11.0 与 9.2 的 wheel;torch 1.6 缺少 CUDA 11.1 与 11.0 的 wheel。**任意一格空白**即表示该组合官方未提供预编译包,必须**从源码构建**。
- **URL 命名规则**(URL 透出的命名规则,可作为理解索引规律的依据):`https://dl.fbaipublicfiles.com/detectron2/wheels/{cuda-tag}/torch{torch版本}/index.html`,即 wheel 路径同时绑定 CUDA 版本与 torch 版本,**两者必须与本地环境完全对齐**,否则会复现后文"Undefined symbols"系列错误。
- **命令通用结构**:`python -m pip install detectron2 -f <url>`,通过 `-f`(find-links) 指定一个额外的 wheel 索引源,无需先 git clone,适合快速在 Linux 上拉起一致环境。
- **表格外的两条注释**(原文):① 预编译包必须与对应的 CUDA 版本和 PyTorch 官方包组合使用,否则需改走源码编译;② 新包每数月发布一次,可能滞后于 master 分支,不保证与下游 research 项目(如 projects 列表中依赖 master 的项目)兼容。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **`projects`**:原文在"pre-built package may not be compatible with the master branch of a research project (e.g. those in [projects](projects))"中明确指向 `projects` 索引页,说明该安装手册是 Detectron2 整个教程体系的最上游文档,**`projects/`** 下基于 master 分支开发的研究型项目(如本仓的 centernet2)可能需要从源码构建,而不能依赖这里的 v0.4 预编译包。
- **`docker`**:文末"内部链接"提示存在 docker 相关文档页,意味着本安装说明之外还有镜像化的部署路径,适合规避本地 CUDA/gcc 兼容问题的用户。
- **`detectron2.utils.collect_env`**:本指南中反复出现的环境自检入口,既被作为排查命令使用,也作为 issue 提交的诊断附件,属于 Detectron2 工具链的统一信息源,被多个 troubleshooting 段落共同依赖。
- **`pytorch.org`**:外部依赖入口,与本仓的 `torchvision` 协同安装,作为版本匹配的权威来源,出现于 Requirements 段和"Undefined symbols"排查段。

---

## 【使用方法】

### 启用方式 / 配置项 / 命令(全部源自原文)

#### 1. 准备基础环境
- 操作系统:Linux 或 macOS。
- Python ≥ 3.6。
- 前往 `pytorch.org` 一同安装 PyTorch ≥ 1.6 与对应版本的 torchvision。
- 可选安装 OpenCV(用于 demo 与可视化)。
- 源码构建额外要求: gcc & g++ ≥ 5.4;推荐安装 `ninja`。

#### 2. 从源码构建 Detectron2(三选一)
```
# (a) 远程直接 pip 安装
python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
# (add --user if you don't have permission)

# (b) 本地 clone 后可编辑安装
git clone https://github.com/facebookresearch/detectron2.git
python -m pip install -e detectron2

# (c) macOS 上指定 clang 工具链
CC=clang CXX=clang++ ARCHFLAGS="-arch x86_64" python -m pip install ......
```
重新构建前先清理:
```
rm -rf build/ **/*.so
```

#### 3. 安装预编译 Detectron2(Linux only,v0.4)
按"表格解读"中给出的矩阵,**用 `-f` 指定与本地 CUDA / torch 版本严格对应的 wheel 索引**,示例:
```
python -m pip install detectron2 -f \
  https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.8/index.html
```

#### 4. 常见安装问题对应处理(原文逐条)
| 错误现象 | 处理命令 / 措施(原文) |
|---|---|
| Undefined symbols (TH/aten/torch/caffe2)、Missing torch dynamic libraries、Segmentation fault | 卸载重装匹配版本的 torchvision/pytorch;预编译 detectron2 时核对 release notes;源码构建时清理 `build/`、`**/*.so` 后重建;无法解决时附 `gdb -ex "r" -ex "bt" -ex "quit" --args python -m detectron2.utils.collect_env` 输出提交 issue。 |
| Undefined C++ symbols (如 `GLIBCXX`) | `conda update libgcc` 后重编;或 `LD_PRELOAD=/path/to/libstdc++.so`。 |
| "nvcc not found" / "Not compiled with GPU support" / "Detectron2 CUDA Compiler: not available" | 编译时确认 `python -c 'import torch; from torch.utils.cpp_extension import CUDA_HOME; print(torch.cuda.is_available(), CUDA_HOME)'` 输出 `(True, a directory with cuda)`;纯 CPU 推理设 `MODEL.DEVICE='cpu'`。 |
| "invalid device function" / "no kernel image is available for execution" | 用 `python -m detectron2.utils.collect_env` 比对 Detectron2 CUDA Compiler / CUDA_HOME / PyTorch built with - CUDA 三者版本一致性;必要时重装/重编对齐本地 CUDA;GPU 架构不匹配时设置 `TORCH_CUDA_ARCH_LIST`,例如 `export TORCH_CUDA_ARCH_LIST="6.0;7.0"`(对应 P100s 与 V100s)。 |
| Undefined CUDA symbols; Cannot open libcudart.so | (原文此条被截断,未给出完整处理) |
