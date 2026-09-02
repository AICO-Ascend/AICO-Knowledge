# **MindStudio Ops System Test Quick Start**<a id="ZH-CN_TOPIC_0000002539355243"></a>

> 仓 `msopgen` · 路径 `docs/en/quick_start/msopst_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopgen/docs/en/quick_start/msopst_quick_start.md

# 一体化深度解读: msopst Quick Start

## 【定位】

本文档解决 **算子开发完成后的初步功能验证与性能分析问题**: 通过 `msopst` (MindStudio Ops System Test) 工具, 在基于 AscendCL API 流程生成单算子 `.om` 文件后, 自动生成测试用例定义 JSON, 并在真实 NPU 硬件环境上执行该 `.om` 文件以验证算子执行结果, 从而提升算子执行效率、降低开发成本。

---

## 【技术要点】

1. **核心工具与两条主命令** —— 工具名为 `msopst`, 提供两条子命令:
   - `msopst create`: 解析 Host 侧算子实现文件 (`.cpp`), 自动生成 ST (System Test) 测试用例定义 JSON。
   - `msopst run`: 基于测试用例定义, 在真实硬件环境运行算子, 输出测试报告。

2. **必备运行环境** —— 需准备一台 Atlas A2 训练或推理服务器, 安装 NPU 驱动固件、CANN Toolkit 与 ops 算子包, 配置 CANN 环境变量; 若需用 MindStudio Insight 查看结果, 还需单独安装 MindStudio Insight 软件包。

3. **SOC 名称格式约定** —— 通过 `npu-smi info` 获取芯片名称 (如 `xxxyy`), 实际使用时需在前面加 `Ascend` 前缀, 即 `Ascendxxxyy`; Quick Command Reference 示例中使用的具体型号为 `Ascend910B4`。

4. **`msopst create` 参数详解**:
   - `-i, --input` (必填): Host 侧算子实现 `.cpp` 路径。
   - `-out, --output` (可选): 测试用例输出目录, 默认当前目录。
   - `-m, --model` (可选): TensorFlow 模型文件路径, 用于自动抽取 shape 信息。
   - `-q, --quiet` (可选): 静默模式, 跳过交互式确认。

5. **`msopst run` 参数详解**:
   - `-i, --input` (必填): 测试用例定义 `.json` 路径。
   - `-soc, --soc_version` (必填): AI 处理器芯片类型 (如 `Ascendxxxyy`)。
   - `-out, --output` (可选): 测试结果输出目录。
   - `-c, --case_name` (可选): 指定要执行的 case 名, 逗号分隔, 默认执行全部。
   - `-d, --device_id` (可选): NPU 设备 ID, 默认 `0`。
   - `-err_thr, --error_threshold` (可选): 自定义精度阈值, 默认 `"[0.01,0.05]"`。

6. **执行 ST 前的环境变量** —— 需基于 CANN 包路径设置:
   - `export DDK_PATH=${INSTALL_DIR}`
   - `export NPU_HOST_LIB=${INSTALL_DIR}/{arch-os}/devlib`, 其中 `{arch-os}` 中的 `arch` 选填 OS 架构, `os` 选填操作系统。
   - `${INSTALL_DIR}` 实指 CANN 安装路径, root 用户默认 `/usr/local/Ascend/cann`。

---

## 【关键机制与数据】

**整体工作原理 (两阶段流水线)**:
1. **用例生成阶段 (`msopst create`)**: 工具解析 Host 侧 `add_custom.cpp` 中的 AscendC 算子原型定义 → 校验 op info 合法性 → 自动写出 `AddCustom_case_{TIMESTAMP}.json` 到指定输出目录 (如 `./st`)。该阶段衔接 `msopgen` (MindStudio Ops Generator) 完成算子工程脚手架之后的工作流。
2. **用例执行阶段 (`msopst run`)**: 以生成的 JSON 为输入, 指定 SOC 版本, 在真实 NPU 上编译并运行 `.om`, 输出执行结果与测试报告到指定目录 (如 `./st/out`)。

**原文日志样例 (原文: Procedure 步骤 1.2)**:
```
2024-09-10 19:47:15 (3995495) - [INFO] Start to parse AscendC operator prototype definition in $HOME/AddCustom/op_host/add_custom.cpp.
2024-09-10 19:47:15 (3995495) - [INFO] Start to check valid for op info.
2024-09-10 19:47:15 (3995495) - [INFO] Finish to check valid for op info.
2024-09-10 19:47:15 (3995495) - [INFO] Generate test case file $HOME/AddCustom/st/AddCustom_case_20240910194715.json successfully.
2024-09-10 19:47:15 (3995495) - [INFO] Process finished!
```
该日志展示了从解析 → 校验 → 生成 → 完成 的完整流程, PID 为 `3995495`, 生成的 JSON 文件名包含时间戳 `20240910194715`。

**默认精度阈值 (原文:)**`[0.01, 0.05]` —— 表示 `msopst run` 在不显式指定 `-err_thr` 时, 使用 `[0.01, 0.05]` 作为默认精度判定标准。

**默认设备 ID (原文:)** `0` —— `-d, --device_id` 不指定时使用第 0 号 NPU。

**性能数据**: 原文未提供具体性能数据 (如算子执行时延、吞吐、内存占用等基准数字)。

---

## 【表格解读】

### Quick Command Reference 表 (逐字还原)

| Command | Function | Example |
|------|------|------|
| `msopst create` | Generate ST test cases from Host-side .cpp | `msopst create -i add_custom.cpp -out ./st` |
| `msopst run` | Execute ST test cases | `msopst run -i ./st/case.json -soc Ascend910B4 -out ./out` |

**逐行解读**:

- **第 1 行 —— `msopst create`**:
  - Command: `msopst create` (生成 ST 用例子命令)。
  - Function: 从 Host 侧 `.cpp` 文件生成 ST 测试用例 JSON, 体现"生成"语义。
  - Example: 仅指定输入 `add_custom.cpp` 与输出 `./st`, 不指定 SOC、不指定模型、不启用静默模式, 是最简调用。

- **第 2 行 —— `msopst run`**:
  - Command: `msopst run` (执行 ST 用例子命令)。
  - Function: 执行 ST 测试用例, 即在硬件上实际跑算子并产出报告。
  - Example: 输入 JSON、显式指定 SOC 为 `Ascend910B4`、输出到 `./out`。注意此处示例 SOC 与正文 Procedure 中示例 `Ascendxxxyy` 的占位写法不同 —— Quick Command Reference 给出了一个真实型号 `Ascend910B4`, Procedure 给出了占位通用写法 `Ascendxxxyy`。

---

## 【公式解读】

**原文无公式** (全文未出现 LaTeX 或伪代码形式的数学公式)。

---

## 【关联】

依据文末内部链接及正文中外链信息, 该工具/文档的上下游关系如下:

1. **直接上游 —— MindStudio Ops Generator (`msopgen_quick_start.md`)**: 本文档 Procedure 步骤 1 明确指出 "`msopst create` 在 [MindStudio Ops Generator Quick Start](msopgen_quick_start.md) 步骤 2 完成后运行", 即 `msopgen` 先生成算子工程脚手架 (含 Host 侧 `.cpp`), `msopst` 再对该 `.cpp` 生成测试用例。该内部链接在原文中出现两次, 是本文档的**唯一强依赖前置文档**。

2. **运行环境依赖**:
   - **CANN Software Installation Guide** (外链, 指向 CANN CommunityEdition 83RC1 安装指南): 提供 NPU 驱动固件、CANN Toolkit、ops 算子包的安装与环境变量配置方法。
   - **MindStudio Insight User Guide** (外链, 指向 mindstudio 82RC1): 可选可视化查看测试结果。
   - **硬件**: Atlas A2 训练或推理服务器 (必需), 需通过 `npu-smi info` 查询实际芯片名。

3. **同仓路径 (NA 代码仓 `docs/en/quick_start/`)**:
   - `msopst_quick_start.md` (本文)
   - `msopgen_quick_start.md` (上游算子生成 quick start)
   两者在 `quick_start` 子目录下并列, 形成 "生成 → 测试" 的两阶段开发者 quick start 链路。

---

## 【使用方法】

### 1. 环境准备
- 准备 Atlas A2 训练/推理服务器, 安装 NPU 驱动与固件 (参考 CANN Software Installation Guide)。
- 安装 CANN Toolkit 与 ops 算子包, 配置 CANN 环境变量。
- (可选) 安装 MindStudio Insight 软件包用于可视化查看。
- 执行 `npu-smi info` 获取芯片名, 在 `msopst run` 时使用 `Ascend` 前缀形式 (如 `Ascend910B4`)。

### 2. 阶段一: 生成 ST 用例
```sh
# 标准调用 (依 Quick Command Reference)
msopst create -i add_custom.cpp -out ./st

# 完整上下文示例 (依 Procedure, 在 msopgen 步骤 2 完成后)
msopst create -i "$HOME/AddCustom/op_host/add_custom.cpp" -out ./st
```
可选参数按需追加: `-m <tf_model>.pb` 自动抽取 shape; `-q` 跳过交互确认。

### 3. 阶段二: 执行 ST
设置 CANN 环境变量:
```sh
export DDK_PATH=${INSTALL_DIR}
export NPU_HOST_LIB=${INSTALL_DIR}/{arch-os}/devlib
# root 默认: ${INSTALL_DIR} = /usr/local/Ascend/cann
```

执行测试:
```sh
# Quick Command Reference 示例
msopst run -i ./st/case.json -soc Ascend910B4 -out ./out

# Procedure 通用占位示例
msopst run -i ./st/AddCustom_case_{TIMESTAMP}.json -soc Ascendxxxyy -out ./st/out
```

可选参数:
- `-c caseA,caseB`: 仅运行指定 case。
- `-d 1`: 选择第 1 号 NPU。
- `-err_thr "[0.001,0.01]"`: 自定义精度阈值 (覆盖默认 `[0.01,0.05]`)。

### 4. 结果查看
- 测试结果输出至 `-out` 指定目录 (如 `./st/out`)。
- 若已安装 MindStudio Insight, 可单独打开该软件进行可视化分析 (MindStudio Insight 本身不参与测试执行, 仅用于查看)。

原文未涉及 CI/CD 集成、批量回归测试、远端设备调度等高级用法, 也未提供容器化或 Docker 化部署方式。
