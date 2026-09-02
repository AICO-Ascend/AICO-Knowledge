# 快速入门

> 仓 `mind-cluster` · 路径 `docs/zh/faultdiag/ascend-faultdiag-toolkit/03_quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/zh/faultdiag/ascend-faultdiag-toolkit/03_quick_start/quick_start.md

# 「mind-cluster」Quick Start 文档一体化深度解读

---

## 【定位】

本文档为 `ascend-faultdiag-toolkit`（ascend-fd-tk）首次使用的入门指引，旨在以交换机离线日志为示例，端到端演示「下载安装 → 清理缓存 → 配置离线数据源并一键诊断 → 查看报告」的完整最小闭环，让用户在 Linux 环境下无需复杂配置即可快速完成链路故障诊断。

---

## 【技术要点】

1. **环境前置**：仅需 Linux + Python 3.8 及以上 + 对应 `pip3` + `unzip` 解压工具，且安装过程需联网拉取三方依赖库。

2. **软件包获取与版本**：下载版本为 **v26.1.0** 的故障诊断 ZIP 包（`Ascend-mindxdl-faultdiag_26.1.0_linux-aarch64.zip`），文档特别指出 ascend-fd-tk Whl 安装包不区分架构，示例直接采用 aarch64 包；通过 `pip3 install ascend_faultdiag_toolkit-26.1.0-py3-none-any.whl` 安装，成功回显为 `Successfully installed ascend-faultdiag-toolkit-26.1.0`。

3. **安装验证命令**：`ascend-fd-tk about`，期望输出 `MindCluster ascend-faultdiag-toolkit诊断工具版本：26.1.0`，作为版本正确性确认。

4. **缓存清理命令**：`ascend-fd-tk clear_cache`，成功回显 `清理完成`，用于首次使用或重新诊断前消除上次诊断残留影响。

5. **离线数据源 + 一键诊断命令**：`ascend-fd-tk set_switch_dump_log /temp/switch_logs auto_collect_diag`，工具支持自动解压压缩包，无需用户预先解压；成功回显为 `设置成功 ... 诊断完成`。

6. **报告落盘路径**：诊断完成后报告自动生成至 `~/.ascend-faultdiag-toolkit/report/diag_report_{YYYYMMDD_HHMMSS}.xlsx`，文件名带时间戳（`YYYYMMDD_HHMMSS`），格式为 xlsx。

---

## 【关键机制与数据】

- **离线模式数据流**：用户下载两份交换机离线诊断日志 ZIP（`diagnostic_information_NAME-D01-XX.224_20260327113617.zip` 与 `diagnostic_information_NAME-D01-XX.254_20260327113617.zip`，源自 `gitcode.com/Ascend/mind-cluster` 的 blobs 路径）放入 `/temp/switch_logs` 目录；`ascend-fd-tk` 通过 `set_switch_dump_log` 命令注册该目录作为离线数据源，再触发 `auto_collect_diag` 子命令完成"日志清洗 + 故障诊断"流水线，期间自动解压压缩包，无需用户手工解压。

- **缓存机制**：工具内部维护诊断缓存（路径隐含在 `~/.ascend-faultdiag-toolkit/` 目录下），因此文档显式要求首次诊断或重新诊断前调用 `clear_cache` 子命令以避免历史结果污染本次结果（原文：「建议清理缓存以避免上次诊断结果影响本次诊断」）。

- **架构无关的 Whl 包**：原文强调 ascend-fd-tk Whl 包不区分架构（原文：「ascend-fd-tk Whl 安装包不区分架构，所以以下示例直接下载 aarch64 架构的」），即同一 whl 可在多种 Linux 架构上安装。

- **诊断对象范围（由示例推导）**：报告示例图包括「交换机故障分析报告」与「交换机间端口连接光模块信息报告」，说明该工具至少能覆盖交换机层面故障与端口/光模块连接信息两类输出。

> 注：原文未提供性能数据（如诊断耗时、资源占用、并发数等），本文不臆造。

---

## 【表格解读】

**原文无表格**（全文未出现任何参数表、对比表、配置项表格，仅以命令、代码块、图示及散文描述呈现）。

---

## 【公式解读】

**原文无公式**（全文未出现任何数学公式或算法伪代码）。

---

## 【关联】

文档通过文末链接构建了一条由"入门 → 深入"的导航链，定位关系如下：

| 链接 | 路径角色 | 与本文档的关系 |
|---|---|---|
| `../../../resource/switch_logs` | 资源侧 | 提供 Step 3 中"交换机示例离线日志"原始资源包，是本文档离线诊断演示的输入数据源。 |
| `../05_usage/06_fault_analysis_report.md` | 使用侧（下游） | Step 4 报告字段含义与解读方法的承接文档，本文仅给出报告路径与示例图，详细字段解析在该处。 |
| `../04_installation_guide/01_installation.md` | 安装侧（横向深化） | 「下一步」指引文档，详细安装说明（含依赖、平台差异等）的完整版，本文仅给出最小安装步骤。 |
| `../05_usage/01_usage_overview.md` | 使用侧（功能横向） | 「下一步」指引文档，介绍工具更多功能，本文只演示交换机链路诊断这一条主线。 |
| `../06_api/01_api_overview.md` | API 侧（命令横向） | 「下一步」指引文档，介绍更多命令，本文只用到 `about / clear_cache / set_switch_dump_log / auto_collect_diag` 等少数子命令。 |

可理解为：本文档是「安装指南 → 快速入门 → 使用概览/报告说明/API 概述」体系中的入门环节，向上承接安装、向下游辐射至具体功能与 API。

---

## 【使用方法】

**启用方式（最小闭环命令序列，原文逐字保留）：**

```bash
# 步骤 1 - 下载与安装
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.1.0/Ascend-mindxdl-faultdiag_26.1.0_linux-aarch64.zip
unzip Ascend-mindxdl-faultdiag_26.1.0_linux-aarch64.zip
pip3 install ascend_faultdiag_toolkit-26.1.0-py3-none-any.whl
ascend-fd-tk about

# 步骤 2 - 清理缓存
ascend-fd-tk clear_cache

# 步骤 3 - 准备离线日志并一键诊断
mkdir -p /temp/switch_logs && cd /temp/switch_logs
wget \
  https://raw.gitcode.com/Ascend/mind-cluster/blobs/19ab0e6d1acc5b64e5153d479f632302e9d82827/switch_logs/diagnostic_information_NAME-D01-XX.224_20260327113617.zip \
  https://raw.gitcode.com/Ascend/mind-cluster/blobs/afd88c0586ad298f1eb46f3f515e82f9b5dd47ab/switch_logs/diagnostic_information_NAME-D01-XX.254_20260327113617.zip

cd /temp/
ascend-fd-tk set_switch_dump_log /temp/switch_logs auto_collect_diag
```

**关键配置项/约定（原文有据可查）：**

- 数据源目录：示例为 `/temp/switch_logs`，传入 `set_switch_dump_log` 的第一个位置参数即离线日志根目录。
- 触发模式：`auto_collect_diag` 作为 `set_switch_dump_log` 的子命令参数，表示"自动采集并诊断"。
- 工具调用入口：`ascend-fd-tk`（统一 CLI），各子命令为 `about` / `clear_cache` / `set_switch_dump_log ... auto_collect_diag`。
- 报告输出位置：`~/.ascend-faultdiag-toolkit/report/diag_report_{YYYYMMDD_HHMMSS}.xlsx`（用户家目录下 `.ascend-faultdiag-toolkit` 隐藏目录的 `report` 子目录）。

**报告查看方式**：诊断完成后直接打开上述 xlsx 报告；字段含义与解读详见[诊断 / 巡检报告说明](../05_usage/06_fault_analysis_report.md)。

## 图文联合解读

- `交换机故障分析-case.png`: **图文联合解读：**

图示为故障诊断工具生成的Excel报告，结构包含两层Sheet（交换机故障分析、同端口光模块信息），当前表以交换机为维度，记录ID、端口、故障码、光功率实测值（7.98/7.79/5.51 dBm）与阈值（7.00/5.50）、处理建议及根因判定（未知）等字段。

技术结论：该截图论证了 **ascend-fd-tk 能对离线交换机日志进行自动化光功率异常诊断**，定位到 NAME-D01-XX.224 端口 400GE1/0/25 双端Lane0收发光超阈值，并给出排查建议。

与文档论点关系：作为"步骤3一键诊断"的结果截图，**印证了快速入门所演示的"下载日志→一键诊断→产出结构化诊断报告"完整闭环**。
- `交换机间端口连接光模块信息-case.png`: **1) 图示内容**
Excel诊断报表，含两个页签（L1&L2&RoCE链路分析、光模块信息）。列涵盖本端交换机ID/SN、端口（400GE1/0/25/27/29）、光模块厂商型号SN、温度、TX/RX Power（Lane0/1）与SNR。三个端口数据行中，**400GE1/0/25 的 TX Power Lane0=7.98 被红色高亮并标注阈值 "> 7.00"**，其余数值以绿色填充（正常）。

**2) 技术结论**
工具能基于离线交换机日志自动解析光模块多Lane收发功率与SNR，并以阈值对比＋色块标注方式定位链路异常（如发射功率越界）。

**3) 与文档论点关联**
对应"步骤3：一键式诊断命令"的输出结果，可视化印证 ascend-fd-tk 可在离线模式下完成链路故障的自动发现与定位。
