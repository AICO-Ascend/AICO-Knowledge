# 构建安装

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/introduction/quick_start/installing_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/introduction/quick_start/installing_guide.md

# AscendNPU IR 构建安装文档深度解读

## 【定位】

本篇文档解决的是 AscendNPU IR（基于 MLIR 的昇腾亲和算子编译中间表示）从源码到可执行产物的全链路构建与安装问题，给出环境依赖准备、两种构建方式（一键脚本 / 手动 CMake+Ninja）、二进制复用、Docker 镜像以及测试运行与判定的完整工程化指导。

---

## 【技术要点】

1. **工具链基线**：CMake ≥ 3.28、Ninja ≥ 1.12.0；推荐 Clang ≥ 10、LLD ≥ 10（原文注明"使用 LLVM LLD 将显著提升构建速度"）。

2. **三方依赖与子模块**：项目依赖 LLVM、Torch-MLIR 等三方库，需通过 `git submodule update --init --recursive` 拉取到指定 commit id；LLVM 源码路径固定为 `third-party/llvm-project/llvm`，`bishengir` 作为外部 LLVM 项目接入。

3. **CANN 端到端依赖**：AscendNPU IR 端到端运行依赖 CANN 环境，需安装 Toolkit 包和与硬件对应的 ops 包；CANN 9.0.0+ 与 8.5.0 及更早版本的环境变量脚本路径不同（`cann/set_env.sh` vs `ascend-toolkit/set_env.sh`）。

4. **`build.sh` 一键脚本**：封装 CMake 配置 + Ninja 编译 + 安装三步；默认 `-o ./build`、`--build-type Release`，并行线程默认 CPU 核心数的 3/4，默认使用 `clang`/`clang++` 与 ccache；`-t/--build-bishengir-template` **必须**安装 CANN 9.0.0，且运行端到端用例必须启用。

5. **手动 CMake+Ninja 模式**：核心开关包括 `-DLLVM_ENABLE_PROJECTS="mlir"`、`-DLLVM_EXTERNAL_PROJECTS="bishengir"`、`-DBSPUB_DAVINCI_BISHENGIR=ON`；`LLVM_MAJOR_VERSION_21_COMPATIBLE=ON` 仅在 LLVM ≥ 21 时添加；模板库需 `-DBISHENGIR_BUILD_TEMPLATE=ON` 并配 `-DBISHENG_COMPILER_PATH=...`。

6. **测试运行机制**：通过 CMake target `check-mlir;check-bishengir` 或 `llvm-lit` 触发，测试通过以"退出码 = 0 且 Failed = 0"为判定，UNSUPPORTED/XFAIL 计入通过，FAIL/XPASS/UNRESOLVED/TIMEOUT 计入失败；典型规模为 388 个测试用例 / 8 个 worker。

7. **Docker 路径**：可复用 `quay.io` 上 `ascend/cann:<version>-<arch>-<os>-py<ver>` 标签的 CANN 镜像（自带完整 AscendNPU IR 二进制），也可在 `docker/` 目录下基于 `ubuntu:22.04`（x86_64）或 `openeuler/openeuler:24.03`（aarch64）本地构建；运行时需挂载 `/dev/davinci0–7`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 等 NPU 设备节点。

---

## 【关键机制与数据】

### 1. 构建数据流（build.sh 路径）

```
git clone → git submodule update --init --recursive
        ↓
   build.sh -o ./build --build-type Release [-r] [-j N] [-t] [--build-test] …
        ↓
   自动调用 cmake (LLVM_ENABLE_PROJECTS=mlir, LLVM_EXTERNAL_PROJECTS=bishengir, BSPUB_DAVINCI_BISHENGIR=ON)
        ↓
   ninja -j N  →  产物落地 ./build/install
        ↓
   check-mlir ; check-bishengir  → llvm-lit 驱动 BiShengIR 测试套
```

### 2. 手动构建数据流（CMake+Ninja 路径）

```
export LLVM_SOURCE_DIR="$(realpath ../third-party/llvm-project)"
cmake ${LLVM_SOURCE_DIR}/llvm -G Ninja
    -DLLVM_ENABLE_PROJECTS="mlir"
    -DLLVM_EXTERNAL_PROJECTS="bishengir"
    -DLLVM_EXTERNAL_BISHENGIR_SOURCE_DIR="$(realpath ..)"
    -DBSPUB_DAVINCI_BISHENGIR=ON
    [可选项见原文表格]
        ↓
ninja -j32
```

关键语义：`LLVM_EXTERNAL_PROJECTS="bishengir"` + `LLVM_EXTERNAL_BISHENGIR_SOURCE_DIR` 把 `bishengir` 注册为 LLVM 的外部子项目，使其参与 LLVM 整体构建图；`BSPUB_DAVINCI_BISHENGIR=ON` 是 AscendNPU IR 的功能开关。

### 3. 性能 / 测试数据（原文样例）

**原文（通过场景）**：

```
-- Testing: 388 tests, 8 workers --
...
Testing Time: 45.23s
Total Discovered Tests: 388
  Unsupported: 89  (22.94%)
  Passed     : 299 (77.06%)
```

**原文（失败场景）**：

```
-- Testing: 388 tests, 8 workers --
...
Testing Time: 38.12s
Total Discovered Tests: 388
  Unsupported:  86 (22.16%)
  Passed     : 300 (77.32%)
  Failed     :   2 (0.52%)
```

原文以"388 tests / 8 workers"作为典型规模示例说明，两次运行仅用时 45.23s 与 38.12s，体现通过率与失败计数在统计输出中的对照关系。

### 4. Docker 镜像 tag 样例（原文）：

- `ascend/cann:9.0.0-a3-openeuler24.03-py3.12` —— 对应 A3 系列硬件 + openEuler 24.03 + Python 3.12 的现成 CANN 镜像（含完整 AscendNPU IR 二进制）。
- 本地构建：`docker build -t ascendnpu-ir:latest -f docker/Dockerfile.x86_64 .`

---

## 【表格解读】

### 表格 1：`build.sh` 脚本参数说明（原文逐字还原）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-o`, `--build PATH` | 构建产物输出目录 | `./build` |
| `--build-type TYPE` | 构建类型 | `Release` |
| `-r`, `--rebuild` | 清空构建目录并重新配置 | 关闭 |
| `-j`, `--jobs N` | 并行编译线程数 | CPU 核心数的 3/4 |
| `--install-prefix PATH` | 安装路径 | `BUILD_DIR/install` |
| `--c-compiler PATH` | `C` 编译器路径 | clang |
| `--cxx-compiler PATH` | C++ 编译器路径 | clang++ |
| `--llvm-source-dir DIR` | LLVM 源码目录 | `third-party/llvm-project` |
| `--build-test` | 构建并运行测试 | 关闭 |
| `--build-bishengir-doc` | 构建 BiShengIR 文档 | 关闭 |
| `-t`, `--build-bishengir-template` | 构建 BiShengIR 模板库，**启用该选项需要安装 CANN 9.0.0，运行端到端用例必须启用** | 关闭 |
| `--bisheng-compiler PATH` | bisheng 编译器所在目录，**构建模板库时需指定** | 无 |
| `--build-torch-mlir` | 同时构建 torch-mlir | 关闭 |
| `--python-binding` | 启用 MLIR python-binding | 关闭 |
| `--enable-cpu-runner` | 启用 CPU runner | 关闭 |
| `--disable-ccache` | 禁用 ccache | 启用（若已安装） |
| `--enable-assertion` | 启用断言 | 关闭 |
| `--fast-build` | 跳过安装步骤 | 关闭 |
| `--add-cmake-options OPTIONS` | 追加 CMake 选项 | 无 |

**逐行解读**：

- **前 4 行（输出与并发）**：`-o`/`--build-type` 控制产物位置与构建模式（Release 是默认推荐）；`-r` 用于彻底清理后重配，适合环境变更或升级 LLVM 后；`-j` 默认 3/4 核心数是对编译耗时与内存占用的折衷。
- **`--install-prefix` + `--fast-build`**：前者决定 `BUILD_DIR/install` 的安装根，后者跳过 install 步骤以加快迭代编译；二者配合可在开发期反复 ninja 而不安装。
- **编译器与 LLVM 路径**：`--c-compiler`/`--cxx-compiler` 默认 clang/clang++，可显式指定版本（如示例中 `clang-15`）；`--llvm-source-dir` 指向子模块化的 LLVM 源码根。
- **`--build-test` / `--build-bishengir-doc` / `-t` / `--build-torch-mlir`**：四个构建范围开关；`-t`（模板库）是最强约束——它隐含要求 CANN 9.0.0，并要求 `--bisheng-compiler` 指定 bisheng 编译器路径，端到端用例运行是模板库的硬依赖。
- **`--python-binding` / `--enable-cpu-runner`**：分别对应 MLIR Python 绑定和 CPU runner（对应手动 CMake 中的 `-DMLIR_ENABLE_BINDINGS_PYTHON=ON` / `-DLLVM_TARGETS_TO_BUILD="host;Native"`）。
- **`--disable-ccache` / `--enable-assertion`**：默认启用 ccache 加速重复构建；`--enable-assertion` 用于 Debug 场景（对应 `-DLLVM_ENABLE_ASSERTIONS=ON`）。
- **`--add-cmake-options OPTIONS`**：作为逃生口，允许透传任意未被脚本封装的 CMake 变量，避免脚本本身随构建需求持续膨胀。

### 表格 2：手动 CMake 可选扩展参数（原文逐字还原）

| 可选参数 | 说明 |
|----------|------|
| `-DCMAKE_INSTALL_PREFIX="${PWD}/install"` | 安装路径 |
| `-DLLVM_MAJOR_VERSION_21_COMPATIBLE=ON` | LLVM 版本 ≥ 21 时需添加 |
| `-DLLVM_ENABLE_ASSERTIONS=ON` | 启用断言（Debug 时常用） |
| `-DMLIR_ENABLE_BINDINGS_PYTHON=ON` | 启用 MLIR python-binding |
| `-DLLVM_TARGETS_TO_BUILD="host;Native"` | 启用 CPU runner |
| `-DBISHENGIR_PUBLISH=OFF` | 关闭未发布功能 |
| `-DBISHENGIR_BUILD_TEMPLATE=ON -DBISHENG_COMPILER_PATH=...` | 构建 BiShengIR 模板库 |

**逐行解读**：

- **`CMAKE_INSTALL_PREFIX`**：与 `build.sh` 的 `--install-prefix` 等价，但 `install` 子目录置于当前 build 目录下。
- **`LLVM_MAJOR_VERSION_21_COMPATIBLE`**：LLVM 21 引入了破坏性变更，该开关用于在新版 LLVM 上保持 BiShengIR 的源码兼容性。
- **`LLVM_ENABLE_ASSERTIONS`**：等价 `build.sh` 的 `--enable-assertion`，是 Debug 构建的标准配套。
- **`MLIR_ENABLE_BINDINGS_PYTHON` / `LLVM_TARGETS_TO_BUILD`**：分别对应 Python 绑定和 CPU 后端；后者是 `--enable-cpu-runner` 的 CMake 层入口。
- **`BISHENGIR_PUBLISH=OFF`**：关闭未发布（实验性）功能，构建更稳定、依赖更小。
- **`BISHENGIR_BUILD_TEMPLATE` + `BISHENG_COMPILER_PATH`**：等价 `build.sh` 的 `-t` + `--bisheng-compiler`，是端到端用例（依赖模板库）执行的前置条件。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档末尾给出唯一一条内部链接：

- **[FAQ-构建与安装](../../faq/faq.md#构建与安装)**：将"构建安装过程中的常见问题"指向 FAQ 文档的"构建与安装"小节，作为本指南的问题排查兜底。
- **CANN 包安装**：与环境依赖准备章节的 `CANN Toolkit` + `ops` 包安装步骤闭环，二进制安装路径正是"复用 CANN Toolkit 包自带的 AscendNPU IR 二进制"。
- **Docker 镜像**：复用 `quay.io/ascend/cann` 上的 CANN 镜像即可获得 AscendNPU IR 二进制，也可基于本地 `docker/Dockerfile.*` 自构建含完整 CANN + AscendNPU IR 的开发镜像；进入容器后可直接调用 `bishengir-compile --version`。
- **测试目标与 MLIR/BiShengIR 主体**：`check-mlir` 与 `check-bishengir` 由 `llvm-lit` 驱动，测试根目录位于 `../bishengir/test`，是验证 MLIR 与 BiShengIR 编译产物正确性的标准入口。

---

## 【使用方法】

### 1. 准备环境
```bash
# 工具链基线
CMake >= 3.28、Ninja >= 1.12.0；Clang >= 10、LLD >= 10

# 克隆与子模块
git clone https://gitcode.com/Ascend/ascendnpu-ir.git
cd ascendnpu-ir
git submodule update --init --recursive
```

### 2. 安装 CANN（端到端运行依赖）
```bash
chmod +x Ascend-cann_{version}_linux-x86_64.run
chmod +x Ascend-cann-A3-ops_{version}_linux-x86_64.run
./Ascend-cann_{version}_linux-x86_64.run --full [--install-path=${PATH-TO-CANN}]
./Ascend-cann-A3-ops_{version}_linux-x86_64.run --install [--install-path=${PATH-TO-CANN}]
source ${PATH-TO-CANN}/cann/set_env.sh   # 8.5.0 及更早版本路径为 ascend-toolkit/set_env.sh
```

### 3. 构建（推荐 `build.sh`）
```bash
# 首次构建
./build-tools/build.sh -o ./build --build-type Release
# 增量编译
./build-tools/build.sh -o ./build --build-type Release
# 清空重建
./build-tools/build.sh -o ./build --build-type Release -r
# Debug + 测试
./build-tools/build.sh -o ./build --build-type Debug --build-test
# 指定编译器与线程
./build-tools/build.sh -o ./build --c-compiler /usr/bin/clang-15 --cxx-compiler /usr/bin/clang++-15 -j 256
# 快速构建（不安装）
./build-tools/build.sh -o ./build --fast-build
# 端到端用例：清空 + 快速构建 + 模板库 + 指定 bisheng 编译器
./build-tools/build.sh -r -o ./build --fast-build -t --bisheng-compiler=/usr/Ascend/cann/bin
```

### 4. 手动 CMake+Ninja（精细化）
```bash
mkdir -p build && cd build
export LLVM_SOURCE_DIR="$(realpath ../third-party/llvm-project)"
cmake ${LLVM_SOURCE_DIR}/llvm -G Ninja \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_ENABLE_PROJECTS="mlir" \
    -DLLVM_EXTERNAL_PROJECTS="bishengir" \
    -DLLVM_EXTERNAL_BISHENGIR_SOURCE_DIR="$(realpath ..)" \
    -DBSPUB_DAVINCI_BISHENGIR=ON
# 按需启用：-DLLVM_MAJOR_VERSION_21_COMPATIBLE=ON / -DLLVM_ENABLE_ASSERTIONS=ON
#            -DMLIR_ENABLE_BINDINGS_PYTHON=ON / -DLLVM_TARGETS_TO_BUILD="host;Native"
#            -DBISHENGIR_PUBLISH=OFF
#            -DBISHENGIR_BUILD_TEMPLATE=ON -DBISHENG_COMPILER_PATH=/path/to/bisheng-compiler
ninja -j32
```

### 5. 二进制安装（免编译）
原文：AscendNPU IR 二进制随 CANN Toolkit 包一起安装，详见"CANN 包安装"段落。

### 6. Docker 镜像
```bash
# 复用 CANN 镜像（自带 AscendNPU IR）
docker run -it --net=host --privileged \
  --security-opt seccomp=unconfined \
  --device=/dev/davinci0 … --device=/dev/davinci7 \
  --device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  --name ascendnpu-ir -v $(pwd):/workspace -w /workspace \
  ascend/cann:9.0.0-a3-openeuler24.03-py3.12 /bin/bash

# 本地构建
docker build -t ascendnpu-ir:latest -f docker/Dockerfile.x86_64 .

# 验证
bishengir-compile --version
```

### 7. 运行测试
```bash
# CMake target 方式（同时跑 check-mlir 与 check-bishengir）
cmake --build . --target "check-mlir;check-bishengir"

# llvm-lit 方式
./bin/llvm-lit ../bishengir/test
./bin/llvm-lit ../bishengir/test/bishengir-compile/commandline.mlir
```

### 8. 常见问题
原文给出跳转入口：[FAQ-构建与安装](../../faq/faq.md#构建与安装)。
