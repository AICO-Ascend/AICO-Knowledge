# 版本配套说明

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/introduction/quick_start/version_compatibility.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/introduction/quick_start/version_compatibility.md

# AscendNPU-IR 版本配套说明 深度解读

---

## 【定位】
这篇文档解决的是 **AscendNPU IR 各版本与底层 CANN 软件栈、硬件平台、Python 运行时之间的版本配套关系问题**，为开发者提供经过验证的推荐版本组合以及在 CANN 版本不替换时混用新特性的工程化操作路径。

---

## 【技术要点】

1. **三档版本的 CANN 配套**：AscendNPU IR `v1.0.0` / `v1.1.0` / `v1.2.0` 分别对应 CANN `8.5.0` / `9.0.0` / `9.1.0`，版本号与 CANN 主版本号呈递增对应关系。

2. **硬件分层支持**：硬件平台从 `v1.0.0` 起即支持 Atlas A3（训练/推理）与 Atlas A2（训练/推理）系列产品；`v1.1.0` 起新增 **Ascend 950PR / Ascend 950DT** 支持（对应 `feature_a5` 分支）；`v1.2.0` 同样支持 Ascend 950PR / 950DT，但对应分支切换为 `feature/regbase`。

3. **Gitcode 分支命名规范**：每个发布版本对应一个固定的 Gitcode 分支名（`release/v1.0.0`、`release/v1.1.x`、`release/v1.2.x`），用于源码获取与对齐。

4. **CANN 不升级的混用方案**：使用 `bash xxx.run --noexec --extract=<dir>` 解包 `.run` 安装包，分别将新版 AscendNPU IR（路径 `bishengir/`）与 BiSheng Compiler（`v1.2.0` 之前位于 `bisheng_compiler/`，9.1.0 之后路径变更为 `tools/bisheng_compiler/`）以 `cp -r` 的方式覆盖旧 CANN 安装目录下的 `tools/bishengir/` 与 `tools/bisheng_compiler/` 路径，实现"保留旧 CANN 主干，仅替换两个关键目录"的就地升级。

5. **Python 配套节奏**：Python 版本支持随 AscendNPU IR 演进逐步上移——`v1.0.0` 支持 `>=3.9, <=3.12`，`v1.1.0` 升级到 `>=3.10, <=3.13`；`v1.2.0` 在该文档中**未列出** Python 版本信息。

6. **Python 包发布形式**：AscendNPU IR 同时通过 `pip install ascendnpu-ir` 提供 wheel 包分发。

---

## 【关键机制与数据】

### 工作原理（CANN 混用方案的数据流）

原文操作序列体现了"提取 → 复制 → 清理"三段式就地替换流程：

1. **提取阶段**：`bash ${NEW_CANN_PKG} --noexec --extract=cann900` 将新版 CANN 9.0.0 安装包解包到 `cann900/` 目录，但不实际安装；
2. **二次提取**：`bash cann900/run_package/ascendnpu-ir_*.run --noexec --extract=$TMP_PATH` 进一步解出 AscendNPU IR 内容到 `$TMP_PATH/bishengir/`；
3. **覆盖写入**：`cp -r $TMP_PATH/bishengir/* ${OLD_CANN_PATH}/tools/bishengir/` 将新 IR 内容复制到旧版 CANN（8.5.0）的 `tools/bishengir/` 目录；
4. **可选扩展**：如仍有兼容问题，再次解包 `cann-bisheng-compiler_*.run`，并将其内容复制到 `${OLD_CANN_PATH}/tools/bisheng_compiler/`；
5. **清理**：`rm -rf $TMP_PATH` 删除临时目录。

> 原文数据/参数：`NEW_CANN_PKG` 指向 `Ascend-cann-toolkit_9.0.0_linux-aarch64.run`；`OLD_CANN_PATH` 指向 `${CANN_850_PATH}/Ascend/cann-8.5.0`；BiShengCompilerPath 在 CANN 9.1.0 后由 `bisheng_compiler/` 变更为 `tools/bisheng_compiler/`。

### 性能数据
原文无性能数据。

---

## 【表格解读】

### 表 1：CANN 配套关系表（原文逐字还原）

| AscendNPU IR版本 | Gitcode分支 | 依赖CANN版本 | 硬件支持 |
| --- | --- | --- | --- |
| `v1.2.0` | `release/v1.2.x` | CANN 9.1.0 | <ul><li>Ascend 950PR/Ascend 950DT(branch `feature/regbase`)</li><li>Atlas A3训练系列产品/Atlas A3推理系列产品</li><li>Atlas A2训练系列产品/Atlas A2推理系列产品</li></ul> |
| `v1.1.0` | `release/v1.1.x` | CANN 9.0.0 | <ul><li>Ascend 950PR/Ascend 950DT(branch `feature_a5`)</li><li>Atlas A3训练系列产品/Atlas A3推理系列产品</li><li>Atlas A2训练系列产品/Atlas A2推理系列产品</li></ul> |
| `v1.0.0` | `release/v1.0.0` | CANN 8.5.0 | <ul><li>Atlas A3训练系列产品/Atlas A3推理系列产品</li><li>Atlas A2训练系列产品/Atlas A2推理系列产品</li></ul> |

**逐行解读**：

- **v1.2.0 行**：CANN 升级到 9.1.0，硬件新增 Ascend 950PR / 950DT 系列（注意分支名为 `feature/regbase`），同时保留 Atlas A3/A2 全系列产品支持；Gitcode 分支 `release/v1.2.x` 为浮动分支，可跟随后续修订。
- **v1.1.0 行**：CANN 9.0.0，是首次引入 Ascend 950PR / 950DT 的版本（分支名 `feature_a5`，注意下划线命名而非斜杠）；其余硬件覆盖与 `v1.2.0` 相同；Gitcode 分支同样为浮动形式 `release/v1.1.x`。
- **v1.0.0 行**：最早的稳定版本，对应 CANN 8.5.0，**不支持** Ascend 950 系列，仅覆盖 Atlas A3/A2 训练+推理产品；Gitcode 分支为固定形式 `release/v1.0.0`（非 `x` 浮动），表明该分支已冻结。

### 表 2：Python 配套关系表（原文逐字还原）

| AscendNPU IR版本 | Python版本支持 |
| --- | --- |
| `v1.0.0` | `>=3.9，<=3.12` |
| `v1.1.0` | `>=3.10，<=3.13` |

**逐行解读**：

- **v1.0.0 行**：支持 Python 3.9 至 3.12（包含 3.9 与 3.12 边界）。
- **v1.1.0 行**：版本窗口整体上移一档，最低 3.10、最高 3.13。`v1.2.0` 的 Python 支持在原文中**未给出**。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档定位于 AscendNPU IR 的"快速上手 → 版本配套"环节，与以下外部依赖和上下游存在强耦合：

- **上游/底层依赖**：华为 CANN 软件栈（`cann-8.5.0` / `cann-9.0.0` / `cann-9.1.0`），其中具体子目录 `tools/bishengir/`（AscendNPU IR）与 `tools/bisheng_compiler/`（BiSheng 编译器，CANN 9.1.0 后路径变更）是两个核心挂载点。
- **下游/硬件目标**：Atlas A3 训练/推理、Atlas A2 训练/推理、Ascend 950PR / 950DT 系列产品，分别覆盖服务器级训练与边缘推理场景。
- **关联模块**：文档隐含指向 AscendNPU IR 中的 **bishengir 工具链** 与 **BiSheng Compiler** 两层——前者是 MLIR 编译时使用的中介表示层，后者是基于 LLVM 的前端编译器；二者共同构成 AscendNPU IR 的编译栈。
- **分发渠道**：通过 PyPI 的 `ascendnpu-ir` wheel 包进行 Python 形态分发（与 CANN 二进制包共存）。
- **Gitcode 分支策略**：`release/v1.x.x` 浮动分支与 `release/v1.x.0` 固定分支并存，体现版本维护节奏。
- **内部链接**：原文未提供内部链接（"内部链接: (无)"）。

---

## 【使用方法】

### CANN 环境配置（按版本选择）
- 若使用 `v1.2.0`：安装 **CANN 9.1.0**，代码拉取 `release/v1.2.x` 分支。
- 若使用 `v1.1.0`：安装 **CANN 9.0.0**，代码拉取 `release/v1.1.x` 分支。
- 若使用 `v1.0.0`：安装 **CANN 8.5.0**，代码拉取 `release/v1.0.0` 分支。

### Python 包安装
```bash
pip install ascendnpu-ir
```
- v1.0.0 需 Python `>=3.9, <=3.12`；
- v1.1.0 需 Python `>=3.10, <=3.13`。

### CANN 不替换时的就地混用（保留旧 CANN，使用新 IR）
原文给出完整命令序列：

```bash
NEW_CANN_PKG="PATH-TO/Ascend-cann-toolkit_9.0.0_linux-aarch64.run"
TMP_PATH="tmp_pkg_files"
OLD_CANN_PATH="${CANN_850_PATH}/Ascend/cann-8.5.0"

bash ${NEW_CANN_PKG} --noexec --extract=cann900
bash cann900/run_package/ascendnpu-ir_*.run --noexec --extract=$TMP_PATH
cp -r $TMP_PATH/bishengir/* ${OLD_CANN_PATH}/tools/bishengir/
rm -rf $TMP_PATH

# 一般执行完上述就会基本可行了，如果还有问题，可以进一步尝试
bash cann900/run_package/cann-bisheng-compiler_*.run --noexec --extract=$TMP_PATH
BiShengCompilerPath="${TMP_PATH}/bisheng_compiler" # CANN 9.1.0 后路径为 "tools/bisheng_compiler/"
cp -r $BiShengCompilerPath/* ${OLD_CANN_PATH}/tools/bisheng_compiler/
rm -rf $TMP_PATH
```

关键参数：
- `--noexec --extract=<dir>`：解包但不执行安装。
- `CANN_850_PATH`：旧 CANN 8.5.0 的安装根环境变量。
- `PATH-TO/`：需替换为新版 `.run` 安装包的实际存放路径。
- 注释提示：CANN 9.1.0 起，BiSheng Compiler 在 `.run` 包内路径为 `tools/bisheng_compiler/`（不再是顶层的 `bisheng_compiler/`）。

### 配套注意事项
- `v1.2.0` 对应 Ascend 950 系列需切换到 `feature/regbase` 分支代码，而 `v1.1.0` 使用 `feature_a5` 分支——硬件启用分支不可混用。
- `v1.0.0` 不支持 Ascend 950PR / 950DT 系列硬件。
