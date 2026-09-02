# Version Compatibility

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/introduction/quick_start/version-compatibility.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/introduction/quick_start/version-compatibility.md

# AscendNPU-IR 版本兼容性文档深度解读

## 【定位】
本文档解决的是 AscendNPU-IR 各版本与 CANN（Compute Architecture for Neural Networks）软件栈、硬件驱动、Python 解释器之间的版本对应与兼容性问题，为开发者在搭建昇腾亲和算子编译环境时提供经过验证的推荐配置组合，并给出在不升级 CANN 主版本的前提下替换 BiShengIR 组件的实操路径。

---

## 【技术要点】

1. **版本-分支-CANN 硬性绑定**：AscendNPU-IR v1.0.0 必须搭配 CANN 8.5.0，对应 Gitcode 分支 `release/v1.0.0`；v1.1.0 必须搭配 CANN 9.0.0，对应分支 `release/v1.1.0`。版本错配会导致编译或运行不稳定（原文："To ensure compilation and runtime stability, please strictly follow the version compatibility relationships..."）。

2. **硬件代际支持差异**：v1.0.0 仅支持 Ascend A2/A3；v1.1.0 在此基础上额外通过分支 `feature_a5` 支持 950 Series。950 Series 的支持并未合入 `release/v1.1.0` 主线，需要切换到特性分支。

3. **CANN 原地组件替换机制（重要降级路径）**：在不升级整个 CANN 安装包的前提下，可将 CANN 9.0.0 安装包中的 `bishengir`（以及必要时 `bisheng_compiler`）目录内容，复制覆盖到旧版 CANN 8.5.0 的 `tools/bishengir/`（及 `tools/bisheng_compiler/`）目录下，从而让 AscendNPU-IR 的新功能运行在旧 CANN 之上。

4. **Python 解释器范围扩展**：v1.0.0 支持 Python ≥3.9 且 ≤3.12；v1.1.0 收紧下限到 ≥3.10、上限扩展到 ≤3.13，反映出对新版 CPython 特性的依赖。

5. **Python 发行包名称固定**：`pip install ascendnpu-ir` 这一命令在两个版本中一致，包名并未随版本变化。

6. **回退方案分层**：当主路径（替换 `tools/bishengir/`）仍异常时，可执行二次替换 `tools/bisheng_compiler/`，并提示该路径在 CANN 9.1.0+ 中变更为 `tools/bisheng_compiler/`（隐含路径布局版本敏感性）。

---

## 【关键机制与数据】

**工作原理（按原文操作流程）**：

1. **离线解包（noexec 模式）**：`bash ${NEW_CANN_PKG} --noexec --extract=cann900` 不真正执行安装，仅将 CANN 9.0.0 run 包解包到 `cann900/` 目录，目的是拿到内嵌的 `ascendnpu-ir_*.run` 与 `cann-bisheng-compiler_*.run` 子包。

2. **二级解包子包**：`bash cann900/run_package/ascendnpu-ir_*.run --noexec --extract=$TMP_PATH` 进一步将 BiShengIR 子包解包到 `$TMP_PATH/bishengir/`。

3. **目录覆盖（cp -r）**：`cp -r $TMP_PATH/bishengir/* ${OLD_CANN_PATH}/tools/bishengir/` 把新 BiShengIR 内容原子写入到 CANN 8.5.0 安装目录的 `tools/bishengir/` 子树下。`rm -rf $TMP_PATH` 清理临时文件。

4. **回退分支（fallback）**：若主步骤仍有问题，针对 CANN 9.0.0 解出的 `cann-bisheng-compiler_*.run` 再次解包，并将结果目录 `bisheng_compiler` 内容覆盖到 `${OLD_CANN_PATH}/tools/bisheng_compiler/`。原文提示：CANN 9.1.0+ 中该路径会变成 `tools/bisheng_compiler/`，意味着 CANN 内部目录布局从 9.0.0 到 9.1.0+ 发生过重命名/重构。

**数据/约束（原文摘录的关键数字与路径）**：
- 环境变量：`CANN_850_PATH`（旧 CANN 安装根）、`NEW_CANN_PKG`（新 run 包路径）、`OLD_CANN_PATH`（默认 `${CANN_850_PATH}/Ascend/cann-8.5.0`）、`TMP_PATH`（默认 `tmp_pkg_files`）。
- Python 范围：v1.0.0 ∈ [3.9, 3.12]；v1.1.0 ∈ [3.10, 3.13]。
- 涉及版本号：CANN 8.5.0、CANN 9.0.0、CANN 9.1.0+（仅作为路径变更提示）。

---

## 【表格解读】

### 表 1：CANN 兼容性矩阵（逐字还原）

| AscendNPU-IR Version | Gitcode Branch | Required CANN Version | Hardware Support |
| --- | --- | --- | --- |
| v1.0.0 | release/v1.0.0 | CANN 8.5.0 | Ascend A2/A3 |
| v1.1.0 | release/v1.1.0 | CANN 9.0.0 | Ascend A2/A3;<br> 950 Series (branch feature_a5) |

**逐行解读**：
- **第 1 行（v1.0.0）**：作为基线版本，分支 `release/v1.0.0` 与 CANN 8.5.0 一一锁定；硬件仅覆盖 A2/A3 两个代际，未提及 950 Series。
- **第 2 行（v1.1.0）**：在保持 A2/A3 支持的同时，新增 950 Series 支持，但需使用专用分支 `feature_a5`，而非 `release/v1.1.0` 主线。这表明 950 Series 的后端/算子适配在主线分支尚未稳定或尚未合并。配套 CANN 从 8.5.0 跃迁到 9.0.0，对应一组 ABI/接口级升级。

### 表 2：Python 兼容性矩阵（逐字还原）

| AscendNPU-IR Version | Python Version Support |
| --- | --- |
| v1.0.0 | >=3.9, <=3.12 |
| v1.1.0 | >=3.10, <=3.13 |

**逐行解读**：
- **v1.0.0**：覆盖 Python 3.9 至 3.12，共四个次版本，区间较宽以兼容既有发行版。
- **v1.1.0**：下限抬升至 3.10（放弃 3.9），上限放宽至 3.13，覆盖 3.10、3.11、3.12、3.13 四个次版本。下限上调意味着 1.1.0 的 Python 绑定可能依赖 3.10 引入的类型注解/语法或标准库变更。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 CANN 软件栈的关联**：AscendNPU-IR 是基于 MLIR 的昇腾亲和算子编译中间表示，其运行时/编译链路深度依赖 CANN 提供的驱动、算子库与编译器；本文档定义的兼容性本质上是 AscendNPU-IR ↔ CANN ↔ 硬件 三者之间的契约。
- **与 BiShengIR/BiShengCompiler 的关联**：文档中提到的 `tools/bishengir/` 与 `tools/bisheng_compiler/` 是 CANN 安装包内嵌的子模块；替换路径显示 AscendNPU-IR 发行包以 `ascendnpu-ir_*.run` 形式打包，并依赖 CANN 9.0.0+ 引入的 `bisheng_compiler` 目录布局。
- **与硬件代际的关联**：A2/A3 与 950 Series 分别对应不同代际的达芬奇架构，文档中通过分支差异（`release/v1.1.0` vs `feature_a5`）来区分后端代码路径，反映出多代际硬件支持在同一仓库中并存但解耦的管理方式。
- **与 Python 生态的关联**：`pip install ascendnpu-ir` 表明 AscendNPU-IR 提供 wheel 包，是上层 Python 脚本或前端框架（如对接 PyTorch/TensorFlow 算子融合层）的接入入口；其 Python 版本范围与主流 ML 框架的 Python 支持节奏一致。
- **上下游关系（隐含）**：上游为 MLIR/LLVM/AscendNPU 硬件驱动；下游为调用 AscendNPU-IR 的前端编译器或算子融合 Pass；横向依赖 CANN 中的 TBE/AICore 算子实现。本文档处于"环境约束层"，对上下游的版本选择具有强制约束力。

---

## 【使用方法】

**1. 基础安装（按版本选择）**：
- v1.0.0 用户：安装 CANN 8.5.0，克隆 `release/v1.0.0` 分支，确保 Python 在 3.9–3.12 之间。
- v1.1.0 用户（仅 A2/A3）：安装 CANN 9.0.0，克隆 `release/v1.1.0` 分支，Python 在 3.10–3.13 之间。
- v1.1.0 用户（需 950 Series）：在 `release/v1.1.0` 基础上额外切到 `feature_a5` 分支获取 950 后端支持。

**2. Python wheel 安装**：
```bash
pip install ascendnpu-ir
```
（包名固定，不随版本变化。）

**3. CANN 不升级情况下的组件替换（原文脚本，逐字保留关键命令）**：
```bash
NEW_CANN_PKG="PATH-TO/Ascend-cann-toolkit_9.0.0_linux-aarch64.run"
TMP_PATH="tmp_pkg_files"
OLD_CANN_PATH="${CANN_850_PATH}/Ascend/cann-8.5.0"

bash ${NEW_CANN_PKG} --noexec --extract=cann900
bash cann900/run_package/ascendnpu-ir_*.run --noexec --extract=$TMP_PATH
cp -r $TMP_PATH/bishengir/* ${OLD_CANN_PATH}/tools/bishengir/
rm -rf $TMP_PATH

# 回退方案（如主步骤仍异常）：
bash cann900/run_package/cann-bisheng-compiler_*.run --noexec --extract=$TMP_PATH
BiShengCompilerPath="${TMP_PATH}/bisheng_compiler" # CANN 9.1.0+ 时路径为 "tools/bisheng_compiler/"
cp -r $BiShengCompilerPath/* ${OLD_CANN_PATH}/tools/bisheng_compiler/
rm -rf $TMP_PATH
```

**4. 注意事项（原文明确）**：
- `PATH-TO/` 需替换为本地真实的 CANN 9.0.0 run 包绝对路径。
- `CANN_850_PATH` 需设置为旧 CANN 8.5.0 的安装根目录。
- 回退路径中"CANN 9.1.0+ path is `tools/bisheng_compiler/`"是版本差异提示，使用 CANN 9.0.0 资源时按 `bisheng_compiler` 取即可。
- 原文未给出具体的验证命令（如 `npu-smi info`、`ascend-dmi` 等），也未给出 Python 端的 import 验证语句。
