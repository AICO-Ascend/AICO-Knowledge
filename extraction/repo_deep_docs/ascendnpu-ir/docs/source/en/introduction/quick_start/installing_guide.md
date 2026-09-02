# Build and Installation

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/introduction/quick_start/installing_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/introduction/quick_start/installing_guide.md

# AscendNPU-IR 构建与安装指南深度解读

## 【定位】

这篇文档解决如何从零开始为 AscendNPU-IR 项目搭建编译环境、获取源码与依赖、执行源码构建或二进制安装,以及如何运行 BiShengIR 测试套件的完整工程问题,描述了 AscendNPU-IR (基于 MLIR,面向昇腾亲和算子编译的中间表示) 在 x86 A3 环境下的端到端可运行能力。

## 【技术要点】

1. **构建工具链基线要求**: CMake >= 3.28,Ninja >= 1.12.0;推荐使用 Clang >= 10 与 LLD >= 10,文档明确指出 LLVM LLD 能显著加速构建。

2. **子模块依赖管理**: 项目依赖 LLVM、Torch-MLIR 等第三方库,必须通过 `git submodule update --init --recursive` 拉取到指定 commit ID,并在首次构建时通过 `--apply-patches` 选项 (或手动 `source build-tools/apply_patches.sh`) 应用补丁。

3. **CANN 运行时依赖**: AscendNPU-IR 端到端运行依赖 CANN 环境,需安装 toolkit 包与 ops 包 (以 9.0.0 版本为例),环境变量脚本路径在 8.5.0 前后不同 (新版为 `${PATH-TO-CANN}/cann/set_env.sh`)。

4. **构建入口抽象**: 推荐使用 `./build-tools/build.sh` 一体化脚本,自动处理 CMake 配置、Ninja 编译与 install 三阶段;高级用户可使用手动 CMake + Ninja 方式,指定 `LLVM_ENABLE_PROJECTS="mlir"`、`LLVM_EXTERNAL_PROJECTS="bishengir"`、`DBSPUB_DAVINCI_BISHENGIR=ON` 等关键选项。

5. **并行度自适应策略**: 默认并行线程数为 CPU 核数的 3/4,脚本同时暴露 `-j N` 显式覆盖 (如示例中 `-j 256`);`--disable-ccache` 默认在已安装时启用 ccache 加速。

6. **测试判定闭环**: 通过 `check-mlir;check-bishengir` 复合目标运行 llvm-lit,Pass 条件为退出码 0 且 Failed=0 (PASS/UNSUPPORTED/XFAIL 均算 Pass),Fail 条件为退出码非 0 或 Failed>0 (FAIL/XPASS/UNRESOLVED/TIMEOUT 算 Fail)。

## 【关键机制与数据】

**构建工作流数据流** (整合自原文):

源码获取 → 子模块初始化/打补丁 → CANN 安装 → 调用 build.sh → CMake 配置 (LLVM MLIR + BiShengIR 外挂项目) → Ninja 并行编译 → install → 可执行的 lit 测试。

- 原文: 测试通过样例输出 — `Total Discovered Tests: 388`,`Unsupported: 89 (22.94%)`,`Passed: 299 (77.06%)`,`Testing Time: 45.23s`,并行 worker 数 8。
- 原文: 测试失败样例输出 — 同样发现 388 个测试,`Unsupported: 86 (22.16%)`,`Passed: 300 (77.32%)`,`Failed: 2 (0.52%)`,`Testing Time: 38.12s`,并列出失败用例 `test/failing-case1.mlir` 与 `test/failing-case2.mlir`。
- 原文: 模板库启用门槛 — `-t`/`--build-bishengir-template` 是 E2E 案例运行的前置条件,且必须先安装 CANN 9.0.0。
- 原文: 版本兼容开关 — LLVM 21 及以上版本必须加 `-DLLVM_MAJOR_VERSION_21_COMPATIBLE=ON` 才可编译。

## 【表格解读】

### 表格一: build.sh 脚本参数

| Parameter | Description | Default Value |
|------|------|--------|
| `-o`, `--build PATH` | Build output directory. | `./build` |
| `--build-type TYPE` | Build type. | `Release` |
| `--apply-patches` | Apply patches to third-party submodules; required for the first build. | Off |
| `-r`, `--rebuild` | Clear the build directory and reconfigure it. | Off |
| `-j`, `--jobs N` | Number of parallel build threads. | 3/4 of CPU cores |
| `--install-prefix PATH` | Installation path. | `BUILD_DIR/install` |
| `--c-compiler PATH` | C compiler path. | `clang` |
| `--cxx-compiler PATH` | C++ compiler path. | `clang++` |
| `--llvm-source-dir DIR` | LLVM source code directory. | `third-party/llvm-project` |
| `--build-test` | Build and run tests. | Off |
| `--build-bishengir-doc` | Build BiShengIR documentation. | Off |
| `-t`, `--build-bishengir-template` | Build the BiShengIR template library, **required for E2E cases. To enable this option, you need to install CANN 9.0.0.** | Off |
| `--bisheng-compiler PATH` | Path to the BiSheng compiler, required when building the template library. | None |
| `--build-torch-mlir` | Also build torch-mlir. | Off |
| `--python-binding` | Enable MLIR python-binding. | Off |
| `--enable-cpu-runner` | Enabling CPU runner. | Off |
| `--disable-ccache` | Disable ccache. | On (if installed) |
| `--enable-assertion` | Enable assertions. | Off |
| `--fast-build` | Skip the installation step. | Off |
| `--add-cmake-options OPTIONS` | Append CMake options. | None |

**逐行解读**:
- `-o/--build`: 指定构建产物输出目录,默认在项目根下 `./build`。
- `--build-type`: 构建类型,默认 Release,调试场景需切到 Debug。
- `--apply-patches`: 首次构建必备,向 LLVM/Torch-MLIR 等第三方子模块打补丁,后续构建无需重复。
- `-r/--rebuild`: 彻底清理 build 目录后重新 CMake 配置,常用于 ninja 报 "No such file or directory" 时 (FAQ 中第一条对应)。
- `-j/--jobs`: 并行编译线程,默认自适应 CPU 核数的 3/4,大机器可手动调高到 256。
- `--install-prefix`: install 安装前缀,默认相对 build 目录的 `install` 子目录。
- `--c-compiler`/`--cxx-compiler`: C/C++ 编译器路径,默认 `clang`/`clang++`,可显式指向如 `/usr/bin/clang-15`。
- `--llvm-source-dir`: LLVM 源码位置,默认使用项目内的 `third-party/llvm-project`。
- `--build-test`: 同时构建并运行测试,等价于编译 check 目标。
- `--build-bishengir-doc`: 构建 BiShengIR 项目自身文档,默认关闭。
- `-t/--build-bishengir-template`: 构建模板库,文档用粗体强调 "E2E 案例运行所必需",且硬依赖 CANN 9.0.0。
- `--bisheng-compiler`: 启用模板库时必填,指向 BiSheng 编译器可执行文件。
- `--build-torch-mlir`: 同时编译 Torch-MLIR 子模块,默认只构建 BiShengIR 自身。
- `--python-binding`: 启用 MLIR 的 Python 绑定,默认关闭。
- `--enable-cpu-runner`: 启用 CPU runner,便于本地无 NPU 时跑通算子。
- `--disable-ccache`: 反向开关 — 即默认行为是启用 ccache 加速,只有显式传该参数才禁用。
- `--enable-assertion`: 启用 LLVM/MLIR 内部断言,通常 Debug 构建时配合使用。
- `--fast-build`: 跳过 install 步骤,仅完成编译,适合开发迭代。
- `--add-cmake-options`: 兜底追加任意 CMake 选项,弥补脚本未覆盖的特殊配置。

### 表格二: 手动构建可选 CMake 选项

| Optional Option | Description |
|----------|------|
| `-DCMAKE_INSTALL_PREFIX="${PWD}/install"` | Installation path. |
| `-DLLVM_MAJOR_VERSION_21_COMPATIBLE=ON` | Required when the LLVM version is 21 or later. |
| `-DLLVM_ENABLE_ASSERTIONS=ON` | Enable assertions (common for debug). |
| `-DMLIR_ENABLE_BINDINGS_PYTHON=ON` | Enable MLIR python-binding. |
| `-DLLVM_TARGETS_TO_BUILD="host;Native"` | Enabling CPU runner. |
| `-DBISHENGIR_PUBLISH=OFF` | Disable unpublished functions. |
| `-DBISHENGIR_BUILD_TEMPLATE=ON -DBISHENG_COMPILER_PATH=...` | Build the BiShengIR template library. |

**逐行解读**:
- `CMAKE_INSTALL_PREFIX`: 自定义安装路径,默认 `${PWD}/install`。
- `LLVM_MAJOR_VERSION_21_COMPATIBLE`: LLVM 21+ 版本兼容性开关,缺失将导致与最新 LLVM 主线 API 不兼容。
- `LLVM_ENABLE_ASSERTIONS`: 启用运行时断言,用于 Debug 期问题定位。
- `MLIR_ENABLE_BINDINGS_PYTHON`: 打开 Python 绑定,允许从 Python 脚本调用 MLIR 工具链。
- `LLVM_TARGETS_TO_BUILD`: 限定 LLVM 后端目标,`host;Native` 表示同时支持宿主架构与本地 NPU 后端。
- `BISHENGIR_PUBLISH`: 关闭未发布/实验性功能,用于对外交付稳定构建。
- `BISHENGIR_BUILD_TEMPLATE` + `BISHENG_COMPILER_PATH`: 启用模板库构建,需配合 BiSheng 编译器路径,E2E 流程的前置。

## 【公式解读】

原文无公式。

## 【关联】

- 与 **BiShengIR** (即 bishengir) 项目的关系: BiShengIR 是 AscendNPU-IR 的核心编译对象,文档中所有构建选项 (如 `--build-bishengir-template`、`--build-bishengir-doc`、`BISHENGIR_PUBLISH`)、LLVM 外挂项目声明 (`-DLLVM_EXTERNAL_PROJECTS="bishengir"`)、测试目标 (`check-bishengir`) 都围绕它展开;可以说本指南是 BiShengIR 在昇腾场景的构建入口。
- 与 **LLVM/MLIR** 的关系: 通过 `LLVM_ENABLE_PROJECTS="mlir"` 与子模块 `third-party/llvm-project` 拉取,BiShengIR 作为 LLVM 的 external project 接入,因此 LLVM 版本 (特别是 21+) 与补丁策略直接影响 AscendNPU-IR 的可用性。
- 与 **Torch-MLIR** 的关系: 作为可选子模块,默认不构建,通过 `--build-torch-mlir` 启用,服务于 PyTorch 前端对接场景。
- 与 **CANN Toolkit** (昇腾异构计算架构) 的关系: AscendNPU-IR 端到端运行离不开 CANN (Toolkit + Ops + 9.0.0+ 版本),环境变量脚本 `cann/set_env.sh` 是运行时的承载;BiSheng 编译器 (`--bisheng-compiler`) 也由 CANN 包提供。
- 与 **测试组件 llvm-lit** 的关系: 通过 `check-mlir` 与 `check-bishengir` 两个 target 调用 llvm-lit,执行 `bishengir/test` 目录下的 `.mlir` 用例;389 个测试用例的统计 (388 Discovered,8 workers) 即由 llvm-lit 报告。

## 【使用方法】

**启用方式与配置项** (均摘自原文):

- 首次构建 (含子模块补丁):
  ```bash
  ./build-tools/build.sh -o ./build --build-type Release --apply-patches
  ```
- 增量构建:
  ```bash
  ./build-tools/build.sh -o ./build --build-type Release
  ```
- 完全重建 (清空 build 目录):
  ```bash
  ./build-tools/build.sh -o ./build --build-type Release -r
  ```
- Debug + 测试 + 补丁:
  ```bash
  ./build-tools/build.sh -o ./build --build-type Debug --apply-patches --build-test
  ```
- 指定编译器与线程:
  ```bash
  ./build-tools/build.sh -o ./build --c-compiler /usr/bin/clang-15 --cxx-compiler /usr/bin/clang++-15 -j 256
  ```
- 快速构建 (跳过 install):
  ```bash
  ./build-tools/build.sh -o ./build --fast-build
  ```
- 重建 + 模板库 (E2E 必备):
  ```bash
  ./build-tools/build.sh -r -o ./build --fast-build -t --bisheng-compiler=/usr/Ascend/cann/bin
  ```
- 手动 CMake + Ninja 完整流程 (高级):
  ```bash
  mkdir -p build && cd build
  export LLVM_SOURCE_DIR="$(realpath ../third-party/llvm-project)"
  cmake ${LLVM_SOURCE_DIR}/llvm -G Ninja \
      -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
      -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="mlir" \
      -DLLVM_EXTERNAL_PROJECTS="bishengir" \
      -DLLVM_EXTERNAL_BISHENGIR_SOURCE_DIR="$(realpath ..)" \
      -DBSPUB_DAVINCI_BISHENGIR=ON
  ninja -j32
  ```
- 运行测试 (在 build 目录内):
  ```bash
  cmake --build . --target "check-mlir;check-bishengir"
  ```
- 直接运行 llvm-lit 指定测试路径:
  ```bash
  ./bin/llvm-lit ../bishengir/test
  ./bin/llvm-lit ../bishengir/test/bishengir-compile/commandline.mlir
  ```
- CANN 安装 (x86 A3,版本以 9.0.0 为例):
  ```bash
  chmod +x Ascend-cann_{version}_linux-x86_64.run
  chmod +x Ascend-cann-A3-ops_{version}_linux-x86_64.run
  ./Ascend-cann_{version}_linux-x86_64.run --full [--install-path=${PATH-TO-CANN}]
  ./Ascend-cann-A3-ops_{version}_linux-x86_64.run --install [--install-path=${PATH-TO-CANN}]
  source ${PATH-TO-CANN}/cann/set_env.sh
  ```
- 二进制安装: 随 CANN Toolkit 一同安装,详细步骤复用 CANN 包安装章节。
- FAQ 中提示的 ninja 报错修复 (原文末尾被截断): 给 `build-tools/build.sh` 加 `-r` 选项重建 build 目录即可 (原文未涉及更多内容)。
