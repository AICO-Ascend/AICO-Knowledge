# **MindStudio Ops System Test快速入门**<a id="ZH-CN_TOPIC_0000002539355243"></a>

> 仓 `msopgen` · 路径 `docs/zh/quick_start/msopst_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopgen/docs/zh/quick_start/msopst_quick_start.md

# 深度解读：MindStudio Ops System Test (msOpST) 快速入门

## 【定位】
本文档描述 msOpST（MindStudio Ops System Test）工具的能力与用法，用于在算子开发完成后，基于 AscendCL 接口流程生成单算子 OM 文件并执行，以对算子功能做初步的正确性验证与性能分析，属于 msopgen 算子工程化流水线的**测试验证阶段**。

---

## 【技术要点】

1. **工具定位与两个核心子命令**：`msopst create`（从 Host 侧 `.cpp` 自动生成 ST 测试用例 JSON）、`msopst run`（在真实硬件上执行测试用例并输出报告）。
2. **依赖链路前提**：必须在《MindStudio Ops Generator 快速入门》步骤 2 创建算子工程之后执行，Host 侧算子实现文件由 msopgen 工程提供（路径示例：`$HOME/AddCustom/op_host/add_custom.cpp`）。
3. **硬件与软件环境**：昇腾 A2 系列服务器 + NPU 驱动固件 + 对应版本的 CANN Toolkit 开发套件包与 ops 算子包；可选安装 MindStudio Insight 进行结果可视化。
4. **Chip Name 解析规则**：通过 `npu-smi info` 取回 `Chip Name`（如 `xxxyy`），实际配置值前缀 `Ascend`，即 `Ascendxxxyy`（如示例命令中的 `Ascend910B4`）。
5. **运行环境变量（msopst run 前必设）**：`DDK_PATH=${INSTALL_DIR}`、`NPU_HOST_LIB=${INSTALL_DIR}/{arch-os}/devlib`（`{arch-os}` 需按运行环境的架构/OS 实际替换）。
6. **关键默认参数**：`-out` 默认当前目录、`-d` 默认设备 0、`-err_thr`（精度阈值）默认 `"[0.01,0.05]"`；`${INSTALL_DIR}` 默认 `/usr/local/Ascend/cann`（root 安装）。

---

## 【关键机制与数据】

**工作原理（数据流，基于原文逐步梳理）：**

1. **用例生成阶段（`msopst create`）**：
   - 解析 Host 侧 `.cpp` 文件中 **AscendC 算子原型（operator prototype）定义** → 原文：`Start to parse AscendC operator prototype definition in ...`
   - 对算子信息做合法性校验 → 原文：`Start to check valid for op info` → `Finish to check valid for op info`
   - 生成命名规则为 `<OpName>_case_<TIMESTAMP>.json` 的测试用例定义文件 → 原文示例：`AddCustom_case_20240910194715.json`（时间戳 `2024-09-10 19:47:15`，PID `3995495`）
   - 可选 `-m` 参数：传入 TensorFlow 模型文件，自动提取 shape 信息填充用例。

2. **用例执行阶段（`msopst run`）**：
   - 输入测试用例 JSON + 指定 `-soc` 芯片型号 → 加载对应平台的算子二进制/OM → 在 NPU 设备（默认 device 0）上真实运行 → 输出至 `-out` 指定目录。
   - 精度判定通过 `-err_thr` 自定义阈值（默认 `"[0.01,0.05]"`），用于判定算子输出与参考实现的偏差是否在容忍区间内。

**原文日志样例（验证数据流）：**
```
2024-09-10 19:47:15 (3995495) - [INFO] Start to parse AscendC operator prototype definition in $HOME/AddCustom/op_host/add_custom.cpp.
2024-09-10 19:47:15 (3995495) - [INFO] Start to check valid for op info.
2024-09-10 19:47:15 (3995495) - [INFO] Finish to check valid for op info.
2024-09-10 19:47:15 (3995495) - [INFO] Generate test case file $HOME/AddCustom/st/AddCustom_case_20240910194715.json successfully.
2024-09-10 19:47:15 (3995495) - [INFO] Process finished!
```

> 注：原文未提供性能数据（如吞吐、时延、显存占用等），故此处不补造。

---

## 【表格解读】

原文包含 1 张速查表，已逐字还原：

| 命令 | 功能 | 示例 |
|------|------|------|
| `msopst create` | 从 Host 侧 .cpp 生成 ST 测试用例 | `msopst create -i add_custom.cpp -out ./st` |
| `msopst run` | 执行 ST 测试用例 | `msopst run -i ./st/case.json -soc Ascend910B4 -out ./out` |

**逐行解读：**

- **第 1 行 — `msopst create`**：该命令以 `add_custom.cpp` 为输入（`-i`），输出到 `./st` 目录（`-out`），对应"解析 AscendC 原型 → 生成 JSON 测试用例"链路；这是用 msopgen 生成算子工程后的第一步动作。
- **第 2 行 — `msopst run`**：以生成的 `case.json` 为输入（`-i`），指定 SOC 版本 `Ascend910B4`（`-soc`），输出到 `./out`（`-out`）；这是验证算子在真实硬件上功能正确性的第二步动作。
- 两行命令合起来构成 **"生成 → 执行"** 的完整闭环，与文末操作步骤的 1.x 和 2.x 子流程一一对应。

---

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的数学表达式）。

---

## 【关联】

**内部链接（文中两处指向）：**

- `msopgen_quick_start.md`（出现 2 次，均在步骤 1.1 中）：
  1. 作为**前置依赖**——"在《MindStudio Ops Generator 快速入门》创建算子工程中的步骤 2 执行完成后，再执行以下命令"；msOpST 必须消费 msopgen 已生成的算子工程目录结构与 Host 侧 `.cpp` 文件。
  2. 作为**路径替换依据**——"根据《MindStudio Ops Generator 快速入门》步骤 1 的第四点生成的目录替换命令路径"；命令中的 `$HOME/AddCustom` 路径并非固定值，须按 msopgen 实际生成的目录名替换。

**上下游链路（基于原文表述梳理）：**

```
msopgen (算子工程生成)  →  msOpST create (生成用例 JSON)  →  msOpST run (硬件执行验证)
        ↑                                                       ↓
   Host 侧 .cpp                                        测试报告 / 可视化
                                                       (MindStudio Insight)
```

**配套依赖（外部链接，原文引用）：**

- 《CANN 软件安装指南》——提供 NPU 驱动固件、Toolkit、ops 包的安装流程。
- 《MindStudio Insight 工具用户指南》——用于结果可视化（可选）。

---

## 【使用方法】

**1. 生成 ST 测试用例**

```sh
msopst create -i "$HOME/AddCustom/op_host/add_custom.cpp" -out ./st
```
参数说明（原文）：
- `-i, --input`：Host 侧算子实现文件路径（.cpp），**必选**
- `-out, --output`：测试用例输出目录，可选（默认当前目录）
- `-m, --model`：TensorFlow 模型文件路径，可选（用于自动提取 shape 信息）
- `-q, --quiet`：静默模式，不进行人机交互确认，可选

**2. 设置运行环境变量**

```sh
export DDK_PATH=${INSTALL_DIR}
export NPU_HOST_LIB=${INSTALL_DIR}/{arch-os}/devlib
```
其中 `{arch-os}` 需按实际 OS 与架构替换；`${INSTALL_DIR}` 默认 `/usr/local/Ascend/cann`（root 安装）。

**3. 执行 ST 测试**

```sh
msopst run -i ./st/AddCustom_case_{TIMESTAMP}.json -soc Ascendxxxyy -out ./st/out
```
参数说明（原文）：
- `-i, --input`：测试用例定义文件（.json）路径，**必选**
- `-soc, --soc_version`：AI 处理器芯片类型，**必选**（实际取值如 `Ascend910B4`）
- `-out, --output`：测试输出目录，可选
- `-c, --case_name`：指定执行的 case 名称，多个用逗号分隔，可选（默认执行全部）
- `-d, --device_id`：NPU 设备 ID，可选（默认 `0`）
- `-err_thr, --error_threshold`：自定义精度标准，可选（默认 `"[0.01,0.05]"`）
