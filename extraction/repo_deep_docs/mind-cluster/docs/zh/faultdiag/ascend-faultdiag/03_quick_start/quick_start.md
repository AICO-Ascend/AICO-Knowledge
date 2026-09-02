# 快速入门

> 仓 `mind-cluster` · 路径 `docs/zh/faultdiag/ascend-faultdiag/03_quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/zh/faultdiag/ascend-faultdiag/03_quick_start/quick_start.md

# mind-cluster ascend-faultdiag 快速入门文档深度解读

---

## 【定位】

本文档是 **ascend-fd（Ascend Fault Diagnosis，昇腾故障诊断工具）** 的快速入门指南，旨在指导用户完成 ascend-fd 的安装、并通过一个最小化的示例（日志清洗 + 故障诊断）体验其核心能力——使用示例日志诊断出 **NPU 光模块不在位** 这一网络类故障。

---

## 【技术要点】

1. **架构与版本支持**：软件包版本为 **v26.1.0**，同时提供 **aarch64** 与 **x86_64** 两种架构的 wheel 包，从 GitCode 开源社区下载并通过 `pip3` 安装。

2. **前置依赖约束**：Linux 系统需自带 `unzip`，Python **≥ 3.7**，必须安装 `pip3`，且安装过程需联网下载三方依赖库。

3. **三大工作流阶段**：
   - **日志清洗（parse）**：`ascend-fd parse -i <log_dir> -o <parse_out>`，将原始日志清洗为结构化的 `parse_out` 目录；
   - **故障诊断（diag）**：`ascend-fd diag -i <root_dir> -o <diag_out>`，对清洗结果执行诊断并生成 `diag_report.json`；
   - **版本核验**：`ascend-fd version`，成功回显形如 `ascend-fd v26.1.0` 即安装成功。

4. **示例日志说明**：仅需**环境检查日志**（environment_check.zip），不依赖 plog（CANN 应用类日志）；无 plog 时 `ROOT_CLUSTER` 任务会失败，但属于可忽略告警。

5. **诊断输出典型示例数据**：故障状态码 `Comp_Network_Custom_05`，故障分类 `Network/Network/Network`，故障设备 `['parse_out device-0', 'parse_out device-4']`，故障名称 "NPU光模块不在位"。

6. **关键传播链**：示例中展示了一条从 `parse_out device-4` 出发的链路 `Comp_Network_Custom_05（NPU光模块不在位）→ Comp_Network_Custom_09（光模块RX/TX无收发光）`。

---

## 【关键机制与数据】

### 工作流程（原文描述）

整个流程被划分为**四个有序步骤**：

| 阶段 | 目的 | 关键产物 |
|---|---|---|
| 步骤 1：安装 ascend-fd | 获取并安装 v26.1.0 软件包 | `ascend_faultdiag-26.1.0-py3-none-linux_*.whl` |
| 步骤 2：准备日志 | 下载 environment_check 示例日志 | `/tmp/faultdiag_demo/log_dir` |
| 步骤 3：日志清洗 | 调用 parse 命令结构化日志 | `/tmp/faultdiag_demo/parse_out` |
| 步骤 4：故障诊断 | 调用 diag 命令输出报告 | `/tmp/faultdiag_demo/diag_out` + `diag_report.json` |

### parse 阶段的内部子作业机制（原文）

- 解析阶段至少包含两个内部 job：`KNOWLEDGE_GRAPH` 与 `ROOT_CLUSTER`。
- **原文**：`These job ['KNOWLEDGE_GRAPH'] succeeded.`——`KNOWLEDGE_GRAPH` 成功。
- **原文**：`Warn: The job ROOT_CLUSTER failed. The error is: [FileNotExistError(502): No plog file that meets the path specifications is found.].`——`ROOT_CLUSTER` 因找不到 plog 文件失败，错误码为 `502 (FileNotExistError)`，**该告警在本示例中可忽略**。

### 诊断报告版本信息（原文回显数据）

| 字段 | 取值 |
|---|---|
| Fault-Diag | 26.1.0 |
| Driver | 23.0.7 |
| Firmware | 7.1.0.11.220 |
| NNAE | 8.0.0 |
| Toolkit | 8.0.RC3 |
| PyTorch | 1.13 |

> 这些版本号是从被诊断环境的日志中**读取**出来的，而非 ascend-fd 工具自身的版本（工具自身版本固定为 26.1.0）。

### 根因节点分析（原文）

- 根因节点：`['Unknown Device']`
- 现象描述：未查找到有效的 Plog 文件，无法定位根因节点。
- **原文**："根因节点显示 `Unknown Device`，是由于日志采集不完整，此处是正常情况。"——这是因为示例缺少 plog，并非 ascend-fd 缺陷。

### 故障事件分析（原文两条说明）

1. 本分析模块下部分分析子项执行失败，诊断结果可能会受到影响从而不准确。失败信息可在 `diag_report.json` 中查询。
2. 关键传播链只展示每个故障设备最长的一条链路。

### 性能/数据特征（原文无）

原文未提供性能基准数据（如诊断耗时、吞吐量、内存占用等），仅展示了**功能正确性**层面的示例。

---

## 【表格解读】

原文中的表格即为步骤 4 输出的**诊断报告 ASCII 表格**。以下**逐字还原**并逐行解读：

### 报告表 1：版本信息

| 版本信息 | 类型 | 版本 |
|---|---|---|
| | Fault-Diag | 26.1.0 |
| | Driver | 23.0.7 |
| | Firmware | 7.1.0.11.220 |
| | NNAE | 8.0.0 |
| | Toolkit | 8.0.RC3 |
| | PyTorch | 1.13 |

**解读**：此表从环境检查日志中提取出的被诊断集群软件栈版本快照，是诊断报告的元数据头。

### 报告表 2：根因节点分析

| 根因节点分析 | 类型 | 描述 |
|---|---|---|
| | 说明 | 未诊断出根因节点，故障事件分析将尝试检测全部设备 |
| | 根因节点 | `['Unknown Device']` |
| | 现象描述 | 未查找到有效的Plog文件，无法定位根因节点。请确认是否存在Plog文件？ |

**解读**：因为本示例缺少 plog，ascend-fd 退化为"全设备扫描"模式；根因节点无法收敛到具体设备，标为 `Unknown Device`。

### 报告表 3：故障事件分析

| 故障事件分析 | 类型 | 描述 |
|---|---|---|
| | 说明 | 1. 本分析模块下部分分析子项执行失败，诊断结果可能会受到影响从而不准确。失败信息可在diag_report.json中查询 |
| | | 2. 关键传播链只展示每个故障设备最长的一条链路 |
| 疑似根因故障 | 状态码 | Comp_Network_Custom_05 |
| | 故障分类 | 类型:Network 组件:Network 模块:Network |
| | 故障设备 | `['parse_out device-0', 'parse_out device-4']` |
| | 故障名称 | NPU光模块不在位 |
| | 故障描述 | 检测到NPU光模块不在位。 |
| | 建议方案 | 1. 建议使用msnpureport工具收集NPU日志，联系华为工程师处理； |
| | 关键日志 | `/usr/local/Ascend/driver/tools/hccn_tool -i 0 -optical -g` |
| | | `present              : not present` |
| | 关键传播链 | `['parse_out device-4']` |
| | | `Comp_Network_Custom_05（NPU光模块不在位）-> Comp_Network_Custom_09（光模块RX/TX无收发光）` |

**逐行解读**：

- **状态码 `Comp_Network_Custom_05`**：Network 组件自定义故障编号 05，索引详见 `已支持故障` 附录。
- **故障设备 `device-0`、`device-4`**：基于清洗产物目录命名的两台 NPU 设备（注意是 `parse_out device-*` 前缀，表示数据源来自清洗输出）。
- **关键日志**：抓取了 `hccn_tool` 命令对设备 0 的查询结果——`present : not present`，即物理光模块不在位，是核心证据。
- **建议方案**：指向 msnpureport 工具及华为工程师支持流程。
- **关键传播链**：展示了 device-4 上"光模块不在位 → 光模块 RX/TX 无收发光"的因果传导。

---

## 【公式解读】

**原文无公式**。

本文档为操作型 quick start，未涉及任何数学公式、伪代码或算法表达式。

---

## 【关联】

文档通过文末的内部链接显式串联了 ascend-fd 的完整文档体系：

1. **日志采集上游**：[`../05_usage/02_log_collection.md`](../05_usage/02_log_collection.md)
   - 在步骤 2 中提及，用于了解 environment_check 日志的采集方式与原理，是 parse 的输入侧说明。

2. **parse 命令参考**：[`../06_api/02_command_parse.md`](../06_api/02_command_parse.md)
   - 在步骤 3 的 NOTE 中指引，用于查阅 parse 命令的完整参数与语义；本文档只演示了 `-i`、`-o` 两个最简参数。

3. **diag 命令参考**：[`../06_api/03_command_diag.md`](../06_api/03_command_diag.md)
   - 在步骤 4 的 NOTE 中指引，用于查阅 diag 命令的完整参数；本文档同样只演示了最小用法。

4. **故障索引附录**：[`../07_references/04_appendix.md#已支持故障`](../07_references/04_appendix.md#已支持故障)
   - 在结果解读章节中指引，用于查阅 `Comp_Network_Custom_05` 等状态码的具体含义。

5. **特性指南入口**：[`../05_usage/menu_usage.md`](../05_usage/menu_usage.md)
   - "下一步"环节指向，提供菜单化的功能导航。

6. **API 参考入口**：[`../06_api/menu_api.md`](../06_api/menu_api.md)
   - "下一步"环节指向，提供命令 API 的总目录。

**上下游关系归纳**：
```
日志采集 (05_usage/02)  →  [示例数据]
                              ↓
                  步骤3: parse (06_api/02)
                              ↓
                  步骤4: diag (06_api/03)
                              ↓
              故障索引 (07_references/04) ← 结果解读
```

本文档处于**入口层**，向上承接"日志采集"，向下导出到"特性指南 / API 参考 / 故障附录"三个深度模块。

---

## 【使用方法】

### 安装方式（原文命令逐字保留）

- **aarch64**：
  ```shell
  wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.1.0/Ascend-mindxdl-faultdiag_26.1.0_linux-aarch64.zip
  unzip Ascend-mindxdl-faultdiag_26.1.0_linux-aarch64.zip
  pip3 install ascend_faultdiag-26.1.0-py3-none-linux_aarch64.whl
  ```

- **x86_64**：
  ```shell
  wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.1.0/Ascend-mindxdl-faultdiag_26.1.0_linux-x86_64.zip
  unzip Ascend-mindxdl-faultdiag_26.1.0_linux-x86_64.zip
  pip3 install ascend_faultdiag-26.1.0-py3-none-linux_x86_64.whl
  ```

### 三条核心命令（原文）

| 命令 | 作用 | 原文示例 |
|---|---|---|
| `ascend-fd version` | 版本校验 | 回显 `ascend-fd v26.1.0` |
| `ascend-fd parse -i <输入> -o <输出>` | 日志清洗 | `ascend-fd parse -i /tmp/faultdiag_demo/log_dir -o /tmp/faultdiag_demo/parse_out` |
| `ascend-fd diag -i <根目录> -o <输出>` | 故障诊断 | `ascend-fd diag -i /tmp/faultdiag_demo -o /tmp/faultdiag_demo/diag_out` |

### 配置项

原文未涉及配置文件、环境变量、调参开关等配置项；仅通过命令行 `-i`/`-o` 两个位置参数完成输入输出路径控制。完整的参数列表原文明确指引到 [`../06_api/02_command_parse.md`](../06_api/02_command_parse.md) 与 [`../06_api/03_command_diag.md`](../06_api/03_command_diag.md) 查阅。

### 异常处理（原文显式声明）

- **可忽略告警**：`ROOT_CLUSTER failed` 因无 plog 文件触发，错误为 `FileNotExistError(502)`，本示例场景下不影响核心诊断结论。
- **诊断失败信息查询路径**：失败的子项详细信息可在 `/tmp/faultdiag_demo/diag_out/fault_diag_result/diag_report.json` 中检索。
