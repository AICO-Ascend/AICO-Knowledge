# Quick Start Guide

> 仓 `mindspeed-ops` · 路径 `tools/skills/operator-performance-profile/QUICKSTART.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-ops/tools/skills/operator-performance-profile/QUICKSTART.md

# operator-performance-profile Quick Start 深度解读

## 【定位】

这篇文档是 `mindspeed-ops` 仓库中 `tools/skills/operator-performance-profile/` 目录下 `operator_performance_profile.py` 工具的快速上手指南,旨在帮助用户在昇腾 (Ascend) 环境下对自定义算子的不同实现 (Triton / ACLNN / TileLang) 进行性能对比与基准测试。

## 【技术要点】

1. **环境前置依赖**: 必须存在 `msprof` 工具 (`which msprof` 校验), 并设置 `ASCEND_HOME_PATH=/usr/local/Ascend`, 将 `$ASCEND_HOME_PATH/bin` 加入 `PATH`。
2. **Python 依赖**: 强制依赖 `torch`、`torch_npu`;可选依赖 `pyyaml`、`pandas`(用于高级特性)。
3. **安装方式**: 以开发模式安装 MindSpeed-Ops (`pip install -e .`),便于本地修改即时生效。
4. **API 路径格式**: 严格要求 `"from <module_path> import <function_name>"` 的完整 import 串,例如 `from mindspeed_ops.api.triton.add import add`。
5. **输入模式**: 支持 `random`(默认,根据 shape/dtype 随机生成)和 `file`(从 `.pth` 文件加载)两种;输入条目通过 `--input` 重复指定,每条含 `shape name dtype` 三元组或 `file_path name`。
6. **可选参数透传**: 通过 `--other-optional-params` 传入 JSON 字符串,支持标量 (`alpha`/`block_size`/`inplace`)、张量描述符 `{"is_tensor": true, "shape": [...], "dtype": "..."}` 以及二者混合。
7. **结果来源**: 工具消费 `msprof` 导出的 `op_statistic_*.csv` 数据,过滤展示 `OP_Type, Core_Type, Min_Time, Avg_Time, Max_Time, Count` 列。

## 【关键机制与数据】

- **工作流**: 用户通过 CLI 指定 API 路径 + 输入规格 → 工具动态 import 该 API → 调用算子若干次( Python API 默认 `iterations=100`) → 借助 `msprof` 采集算子级 profiling CSV → 解析并以文本/JSON 输出。
- **随机种子保证可复现**: 默认 `seed=42`,可通过 `--seed` 覆盖,确保每次运行生成相同的随机 tensor。
- **跨实现对比能力**: 通过替换 `--api` 中的子路径(如 `triton.*` / `aclnn.*` / `tilelang.*`),可在相同输入规格下对比不同算子后端实现的性能。
- **批测模式**: 借助 shell `for` 循环对多个 API 串行测试,结果以 `${api}_results.json` 分文件落盘。
- **原文输出样例数据**(Output Examples 章节文本报告)对一个 `Add` 算子 (float32+float16 输入, 10×10) 给出: `Min Time 12.45us`, `Avg Time 15.23us`, `Max Time 18.91us`, `Count 100`,统计源文件为 `op_statistic_0.csv`。
- **JSON 输出结构**: 顶层含 `api_path / module / function / seed`,核心字段为 `implementations`,键由数据类型组合构成(如 `"float32_float16"`),值内含 `source_file`、`is_op_statistic`、`columns`、`data` 数组。

## 【表格解读】

原文输出示例章节包含一段文本格式的统计表,逐字还原如下:

| OP Type | Core Type | Min Time(us) | Avg Time(us) | Max Time(us) | Count |
|---|---|---|---|---|---|
| Add | AI Core | 12.45 | 15.23 | 18.91 | 100 |

逐行解读:
- **OP Type = Add**: 被 profiling 的算子类型(对应本次调用的 `mindspeed_ops.api.triton.add`)。
- **Core Type = AI Core**: 该算子实际执行的硬件核类型,确认运行在昇腾 AI Core 而非其他协处理器。
- **Min Time(us) = 12.45**: 100 次迭代中的最短单次耗时(微秒),反映最佳情况。
- **Avg Time(us) = 15.23**: 平均单次耗时,是性能对比的主指标。
- **Max Time(us) = 18.91**: 最差单次耗时,反映尾部延迟。
- **Count = 100**: 采样次数,与 Python API 的 `iterations=100` 对应。

> 备注:原文实际为等宽字符表头(包含 `OP_Type, Core_Type, MinTime, Avg_Time, Max_Time, Count`),此处按文档中实际分隔符列名转写为 markdown 表格;字段语义与原表完全一致。

## 【公式解读】

原文无公式。

## 【关联】

- **与多算子后端实现的耦合**: 文档示例覆盖 `mindspeed_ops.api.triton.*`、`mindspeed_ops.api.aclnn.*`、`mindspeed_ops.api.tilelang.*` 三大子模块,说明该工具面向整个 `mindspeed-ops` 自定义算子生态,可在不同实现间做 A/B 性能对比。
- **与 `msprof` profiling 流水线的关联**: 工具下游依赖昇腾官方 `msprof` 的 `op_statistic` CSV 输出 (`op_statistic_0.csv`),所以必须先满足 Ascend 工具链环境变量(`ASCEND_HOME_PATH`)与 `msprof` 可用性。
- **Python 编程入口 `OperatorPerformanceComparator`**: 文档末尾给出同名类的 `compare_single_api()` 方法签名,作为 CLI 之上的 SDK 入口,便于嵌入更大的自动化测试流水线。
- **与训练业务算子的可观测性**: 作为 `tools/skills/operator-performance-profile/` 的 skill 文档,它服务于仓库更上层的训练优化闭环: 自定义算子 → 性能 profile → 调优决策。

## 【使用方法】

启用方式与配置项(原文整理):

- **CLI 主入口**: `python operator_performance_profile.py`,关键参数:
  - `--api "<import 串>"`:必填,格式 `"from <module> import <func>"`。
  - `--input [shape] <name> <dtype>`:可重复,定义随机模式下的张量规格。
  - `--input <file.pth> <name>`:可重复,文件模式下的张量来源。
  - `--input-mode {random|file}`:默认 `random`。
  - `--other-optional-params '<json>'`:透传给算子的额外参数(标量或张量描述符)。
  - `--seed <int>`:默认 `42`。
  - `--output-format {text|json}`:输出格式。
  - `--output-file <path>`:JSON 输出文件路径(如 Example 5)。
- **Python SDK**:
  - `from operator_performance_profile import OperatorPerformanceComparator`
  - `comparator.compare_single_api(api_path=..., inputs=[...], iterations=100, optional_params={...}, seed=42)`
  - `inputs` 元素字典字段: `name`、`shape`、`dtype`、`mode`(取值 `random`/`file`),文件模式下使用 `file_path` 代替 `shape/dtype`。
- **批测脚本模板**(Example 5):
  ```bash
  for api in "triton.add" "aclnn.matmul" "tilelang.custom_op"; do
      python operator_performance_profile.py \
           --api "from mindspeed_ops.api.$api import $(echo $api | cut -d. -f2)" \
           --input [256,256] x float32 \
           --input [256,256] y float32 \
           --output-format json \
           --output-file ${api}_results.json
  done
  ```
- **常见错误处理**(原文 Troubleshooting 已列示但末尾被截断,原文未涉及更多):API import 失败需检查模块路径;Function not found 需检查函数导出;Invalid API path format 必须使用 `"from module.path import function"` 完整带引号串;File not found 原文片段被截断,原文未涉及具体方案。
