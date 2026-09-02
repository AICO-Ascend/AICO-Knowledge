# Compute部分设计文档

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/Compute.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/Compute.md

# Compute 设计文档深度解读

---

## 【定位】

本文档定义了 msinsight 中 **Compute（算子调优）模块**的数据导入格式、二进制数据块编码方案以及多个可视化视图（Timeline、热点指令、内存负载等）的开发约定，作为该子系统的统一设计与实现指南。

---

## 【技术要点】

1. **JSON 格式判定**：JSON 文件需在**第一个数组开始前**包含 `"profilingType"` 和 `"op"` 关键字；内容格式复用 **Trace Event Format**（含 `traceEvents` 数组、`ph`/`pid`/`tid`/`ts`/`dur` 等字段），等同于 Timeline 的 JSON 文件结构。

2. **二进制文件判定**：以 `*.bin` 后缀的单文件导入即认定为 Compute 二进制数据；其内部按 **数据块编码** 区分子页面类型。

3. **数据块编码规则**：visualize_data.bin 中各组件按"**每个组件一次性分配 16 个位置**"原则编码，预留空间避免不同组件开发冲突。已定义 0x00–0x0D 共 14 种数据块类型。

4. **JSON 字段动态解析约束**：`Files Dtype` / `Instructions Dtype` 中支持动态解析的键值对**必须是单个值或一维数组**；二维数组（如 `Address Range`）**不支持动态解析**，需单独约定。数据类型枚举为：`skip=0`（界面不显示）、`int=1`、`float=2`、`string=3`。

5. **基本运算单元与数组对齐**：核心指令列表中 `Cycles`、`Instructions Executed`、`TheoreticalStallCycles`、`RealStallCycles` 等数组的顺序**必须与 `Cores` 字段顺序保持一致**，含义以"数据生产端和解析端约定为准"。

6. **算子 block 互斥规则**：`block_detail`（aic/aiv 有效）与 `mix_block_detail`（mix 有效）**二者只会有一项有效**，二者均为可包含 0~N 个 dict/map 的列表结构。

---

## 【关键机制与数据】

**整体工作流程**（原文图示 `compute_endToend_process`）：
- **端到端流程**分为两阶段：① 性能数据采集 → ② 性能数据可视化。
- **后端业务**进一步拆分为：文件解析 → 数据请求 → 业务逻辑处理（见 `compute_file_parsing`、`compute_data_request`、`compute_logic_sequence_1/2`）。

**JSON 数据流**（timeline/traceEvents）：
- 典型事件字段示意（原文示例）：`name="MOV_XD_IMM"`、`ph="X"`、`ts=3.568000078201294`、`dur=0.0010000000474974513`、`pid="core2.veccore1"`、`tid="SCALAR"`、`cname="startup"`。
- `args` 中携带 `code`（源码路径+行号）、`detail`（指令级注释如 `XD:X29=0x7fa0,IMM:0x7fa0,`）、`pc_addr`（PC 地址如 `"0x10d0d000"`）。

**Bin 数据流**（二进制数据块）：
- 每个数据单元形如 `compute_bin` 图所示，结构含可选的 **4096 字节附加数据块**用于存储文件路径信息，路径以 UTF-8 JSON 字符串形式存放（如 `"/home/matmul_leakyrelu_custom.cpp"`），其后跟随数据块正文（C++ 源码/JSON 结构负载等）。
- 0x01 代码文件功能页对应 `compute_json.png`，二进制正文为 C++ 源码片段（如 `# include "kernel_operator.h"\n# include "lib/matmul_intf.h"\n\nusing namespace ...`）。

**算子基本信息**（0x05，原文示例字段类型）：
- `block_dim: uint16`、`mix_block_dim: uint16`、`duration: float32`、`device_id: uint16`；
- `op_type` 为枚举：`aic / aiv / mix`；
- `pid` 类型为 `str`（进程号）；
- `block_detail[].block_id: uint16`、`core_type: enum`（aic / aiv）、`duration: float32`；
- `mix_block_detail[].duration` 为 `[float32, float32, float32]`，依次表示 **aic、aiv0、aiv1** 三个 sub block 耗时；
- `advice` 字段当前为空，预留为建议列表。

**计算负载图/表**（0x06 / 0x07）：
- 字段集相同（`block_id: uint8`、`block_type: enum`、aic/aiv/aiv0/aiv1、`name: string`、`value: float32`、`origin_value: float32`）；
- 区别仅在 `unit` 枚举值：0x06 图单位为 `enum:"%"`；0x07 表单位为 `enum:"us, instructions, 数据量(Byte)"`。

**Timeline 关联**（0x02）：
- 数据源标注为 `tracing.json`，必须满足 **Trace Event Format**；原文示例事件含 `name="block0"`、`ts=1`、`dur=20`、`name="hccl::prepare"`、`dur=5`、`ts=2`、`name="hccl::wait"`、`dur=5`、`ts=10`。

**稳定性声明**（原文）：
- 0x0A 内存读写时序图与 0x0B L2Cache 图**当前按 POC 能力记录**，**稳定性以实现和测试为准**。
- 示例路径均为脱敏路径，**真实路径以导入数据为准**。

---

## 【表格解读】

**表 1：visualize_data.bin 数据块编码分配表**（原文表格**逐字还原**）

| 数据块编码 | 数据块内容 |
|---|---|
| 0x00 | 数据块无效 |
| 0x01 | 代码文件 |
| 0x02 | 流水图 tracing.json。 |
| 0x03 | 热点图映射文件 api.json 的 files 部分。 |
| 0x04 | 热点图映射文件 api.json 的 instructions 部分。 |
| 0x05 | 基本信息 |
| 0x06 | 计算负载图 |
| 0x07 | 计算负载表格。 |
| 0x08 | 访存热力图。 |
| 0x09 | 访存表格。 |
| 0x0A | 内存读写时序图（TraceKit）。 |
| 0x0B | L2Cache 图（TraceKit）。 |
| 0x0C | 核间负载。 |
| 0x0D | roofline 模型。 |

**逐行解读**：
- **0x00**：占位/无效标识，遇到此编码时该数据块应被解析端跳过。
- **0x01–0x02**：算子**源码与执行时序**数据，分别支撑"代码文件"页和 Timeline 视图，0x02 明确数据源为 `tracing.json`。
- **0x03–0x04**：热点图（hotspot）的**双视图映射源数据**，一为 `files` 部分（源代码行 → 指令地址/Cycles/执行数），一为 `instructions` 部分（指令级明细，含 Stall 与 L2Cache Hit Rate）。
- **0x05**：算子**元信息**（名称、SoC、op_type、block_dim、duration、device_id 等），整个 Compute 页面的入口摘要。
- **0x06–0x07**：**计算负载**的图与表双视图，单位语义不同（图用百分比 %，表用 us / instructions / Byte）。
- **0x08–0x09**：**访存（memory access）**的热力图与表格，与 0x06/0x07 形成对称的图/表设计。
- **0x0A–0x0B**：标注 **TraceKit**，均按 **POC 能力**开发，**稳定性以实现和测试为准**——属于探索性能力。
- **0x0C**：跨核负载，文档未给出字段细节。
- **0x0D**：roofline 模型，文档未给出字段细节。

> 注：原文中"分配原则"原文为"**后续按照每个组件一次性分配 16 个位置，防止不同组件开发冲突**"——即每个组件被预留 16 个连续编码槽位，当前 Compute 占用了 0x00–0x0D（14 个编码），仍留有 2 个（0x0E、0x0F）扩展空间。

---

## 【公式解读】

**原文无公式**（无 LaTeX 数学式或伪代码形式的公式定义；数据格式约定以 JSON Schema 与字段注释形式给出）。

---

## 【关联】

原文文档**未提供文末内部链接**（"内部链接: (无)"）。文档内部自身存在的功能/视图关联如下：

- **Trace Event Format 复用**：0x02 Timeline 与 JSON 导入判定共同依赖此标准，是与上游 Profiling 数据采集端及前端 Timeline 组件的**共享契约**。
- **TraceKit 能力**（0x0A 内存读写时序、0x0B L2Cache）：原文标注"**按 POC 能力记录**"，表明其为**试验性模块**，与正式编码（0x00–0x09）的稳定视图在质量基线上有所区分。
- **数据生产端 ↔ 解析端约定**：原文多处强调"**数组顺序需与 `Cores` 字段顺序保持一致；具体含义以数据生产端和解析端约定为准**"——表明该文档与上游算子 Profiler 之间存在**强耦合约定**。
- **数据视图对齐**：0x03/0x04 → 热点图；0x06/0x07 → 计算负载图/表；0x08/0x09 → 访存热力图/表；三组均呈"图/表"成对设计，便于前端复用同一份数据双视图呈现。
- **二进制 ↔ JSON 关系**：0x01 代码文件使用 **4096 字节附加数据块**存放路径字符串 + JSON 结构，C++ 源码以字符串负载嵌入——这是 Bin ↔ 内存对象互转的关键约定。

---

## 【使用方法】

原文未给出启用方式/CLI 命令/前端配置项等内容，"启用方式/配置项/命令"层面——**原文未涉及**。

文档仅说明：
- 数据导入路径示例为**脱敏路径**，以实际导入为准；
- 实际开发需遵循"**每个组件一次性分配 16 个位置**"的编码分配原则以避免冲突；
- 0x0A / 0x0B 当前稳定性**以实现和测试为准**。

## 图文联合解读

- `compute_endToend_process.png`: **图文解读：**

1) **图示内容**：展示从"算子"出发，经 msProf（仿真/上板两条路径）和 msTraceKit 采集数据，输出至 MindStudio Insight 的端到端数据流。输出物含 visualize_data.bin（代码热点/计算内存热点/Roofline）、trace.json（指令流水）、memory_records.bin 与 cache_data.bin（后者属 POC 特性）。

2) **技术结论**：算子调优采用双采集链路——msProf 负责算子级指令与计算数据，msTraceKit 负责内存/Cache 时序；数据分 JSON 与 Bin 两类格式分别承载事件流与二进制块，仿真与上板共用同一可视化数据格式。

3) **与文档对应**：佐证文档"JSON 复用 Trace Event Format、Bin 按数据块编码区分页面、0x0A/0x0B 按 POC 记录"的论点，是"性能数据采集与可视化"流程的图示化总览。
- `compute_file_parsing.png`: **图解联合解读：**

1）图为双分支流程图：左支"BIN文件"经"文件末尾？"判断→协议头解析→获取类型/长度→SOURCE类型+4096→缓存块位置→跳转循环；右支"JSON文件"校验`profilingType:"op"`→初始化DB→内容切片→逐片解析→入库。

2）论证结论：BIN采用流式分块循环解析（带位置缓存、SOURCE类型扩展）；JSON采用切片并行解析，两者解析路径互不耦合。

3）与文档关系：对应"文件解析流程"章节，落实JSON复用Trace Event Format、BIN按数据块编码区分页面的约定。
- `compute_data_request.png`: **图解读：**

该流程图展示数据请求流程：查询数据→调用Handler→判断"请求指令流水数据？"。若**是**，直接从DB查询后结束；若**否**，则走缓存查找数据块起始位置→调用Parser→从bin文件解析的完整路径。

**技术结论：** 系统采用双路数据源策略——指令流水数据走DB快速通道，其他算子数据走"缓存定位+bin解析"的二进制通道，体现按数据特性分流的性能优化设计。

**与文档关系：** 对应文档"数据请求流程"(compute_data_request)章节，印证了Bin文件通过数据块编码区分页面、二进制与JSON混合存储的设计约定。
- `compute_logic_sequence_1.png`: **图解：**
1）图示UML时序图，展示Compute模块文件解析流程，参与者含ImportActionHandler、ParserFactory、ParserJson/ParserBin等；按`opt JSON`/`opt BIN`两分支，JSON路径经GetParseFileByImportFile→Parser→Parse→SplitFile，BIN路径经HandleCompute→ParseDataBlocks→ParseTask→SplitFile，均汇入JsonFileProcess。

2）论证采用工厂+策略模式：ParserFactory根据类型分派Json/Bin解析器，二者下游均依赖SplitFile统一封装；Bin解析层次更深，体现数据块编码的复杂度。

3）对应文档"文件解析流程"，佐证Json复用Trace Event Format、Bin通过数据块区分页面的设计。
- `compute_logic_sequence_2.png`: # 图文联合解读

**1) 图内容**：时序图展示三级调用链——`XXXHandler`→`SourceFileParser`→`XXXParser`，依次发起 `GetData` 请求并回传 `data`，形成两次连续的方法调用与数据返回。

**2) 技术结论**：数据请求采用**分层委托/链式解析模式**，Handler 作为入口不直接解析文件，而是委派给 SourceFileParser；后者再细粒度调用具体 XXXParser，体现职责分离与可扩展性，便于按文件类型复用不同 Parser。

**3) 与文档关系**：对应"后端业务代码流程-数据请求流程"章节，阐释后端自顶向下逐层下钻解析文件的调用约定，支撑 Compute 数据可视化的请求链路设计。
- `compute_bin.png`: # 图文联合解读

**1) 图中内容**
该图描述 Bin 文件中一个**数据块**的二进制布局，总长度含 4 字节信息头 + 内容体：
- **数据块内容长度**（8Byte，unsigned64）：记录 JSON 内容字节数。
- **数据块类型**（1Byte，值 0x05）：标识此块为"JSON 结构数据流"。
- **数据块补零长度**（1Byte）：内容末尾对齐填充字节数。
- **保留字段**（2Byte）：reverse，预留扩展。
- **数据块内容**：json 结构数据流，即 traceEvents 数组。

**2) 技术结论**
Bin 文件采用 **TLV/Type-Length-Reserved 风格的分块编码**：固定 12 字节头描述内容大小与类型，使解析器可流式识别不同页面（timeline / 热点指令 / 内存负载等）数据，实现多视图数据混存于同一文件。

**3) 与文档论点关系**
呼应文档"**Bin 数据通过数据块编码区分不同页面数据**"的核心约定：图中 0x05 即为一种页面类型标识，证明 Bin 通过 type 字段 + 长度前缀实现**异构页面的统一存储与按需解码**，是 Compute 后端文件解析流程的数据格式基础。
- `compute_json.png`: **图文联合解读：**

**图示内容：** UI 展示算子调优的"热点指令视图"，采用双栏对照布局。左侧为源码视图（add_custom.cpp），逐行标注 Instructions Executed 与 Cycles；右侧为对应汇编指令表，列出 Address、Pipe 类型（SCALAR/VECTOR/MTE2）、汇编指令、指令数与 Cycles。顶部含 Core/Source 下拉筛选及"Only Related Instructions"过滤开关。

**技术结论：** 该视图实现了**源码行到汇编指令的反向映射**，并按指令类型和执行周期量化性能开销，便于定位热点代码行（如 Init 函数中 `pipe.InitBuffer` 对应多条 SCALAR/MTE2 指令）。

**与文档关系：** 直接支撑文档"功能涉及与实现"中"热点指令视图"的能力说明，验证了 Bin/JSON 数据经后端解析后可在前端以源码-指令双视图呈现调优所需的细粒度性能数据。
- `compute_json_binary.png`: 1) **图示内容**：展示二进制数据块结构，类型标识为0x01，专门存储文件路径信息。结构包括：8字节内容长度（uint64）、1字节类型（0x01）、1字节长度字段、2字节保留位（共12字节头），加4096字节路径存储区，内容示例为xxx.cpp，整体按4字节对齐。

2) **技术结论**：采用"块类型+长度+内容"的自描述格式，通过类型码0x01区分不同页面数据块；固定4096字节路径区统一处理变长路径，简化了解析逻辑。

3) **与文档关系**：直接印证文档"Bin数据通过数据块编码区分不同页面数据"的约定，呼应前端解析流程中按块类型分发处理的实现机制。
- `compute_source.png`: **图文联合解读：**

**1) 图中内容**：展示热点指令视图UI，左栏为Ascend C源码（含`AddKernel`类、行号及Instructions/Cycles列），右栏为对应反汇编指令（含#、Address、Pipe（VECTOR/SCALAR/MTE2）、Source、Instructions Executed、Cycles列）。顶部支持Core、Source筛选及"Only Related Instructions"过滤。

**2) 技术结论**：源码行与汇编指令实现双向映射，可按Pipe类别分桶统计指令执行数与Cycles，直观定位热点代码行（如第13行113条指令、42 cycle）。

**3) 与文档关系**：佐证文档"热点指令视图"功能论点，验证Trace Event Format中`code`/`pc_addr`字段支撑源码-汇编联动分析的实现约定。
- `compute_source_binary.png`: **图文联合解读：**

1）图中绘制了 Bin 文件的**数据块结构**：整体 4 字节对齐，包含「数据块内容长度(uint64, 8Byte)」「数据块类型(uint8, 0x03)」「长度(uint8, 1Byte)」「保留位 reverse(2Byte)」四个头部字段，以及「数据块内容：api.json 的 files 部分」。

2）论证了 Bin 文件采用**类型化分块编码**：0x03 类型标识用于承载 api.json 的 files 元数据，固定头部 + 可变内容的设计实现了「不同页面数据通过块类型区分」。

3）呼应文档中「Bin 数据通过数据块编码区分不同页面数据」的约定，是该机制的具体结构化呈现。
- `compute_instruction.png`: **1) 图中内容**
热点指令视图：左侧为源码行（带"指令执行数/Cycles"两列），右侧为指令详情表（PC地址、Pipe类型：VECTOR/SCALAR/MTE2、源码引用、指令数、Cycles），顶部含Core/source下拉与"Only Related Instructions"过滤。

**2) 技术结论**
实现源码行↔硬件指令的双向映射，按core与源文件过滤，可量化每条指令的执行次数与耗时，支撑瓶颈定位。

**3) 与文档论点关系**
印证文档"热点指令视图"约定，体现JSON traceEvents中`pc_addr`、`name`、`dur`等字段在UI层的呈现与聚合方式。
- `compute_instruction_binary.png`: 1) **结构描述**：图示为Bin文件的"数据块"格式，整体4字节对齐；头部由8Byte内容长度（unsigned64）+ 1Byte类型(0x04) + 1Byte补零长度 + 2Byte保留位（共12Byte）组成，载荷为api.json的instructions部分。

2) **技术结论**：通过类型字节(0x04)实现多页面数据区分，配合固定头部元数据（长度/类型/对齐）和指令载荷，支持算子调优指令数据的二进制紧凑存储与解析。

3) **文档论点对应**：印证了文档"通过数据块编码区分不同页面数据"的Bin数据约定，0x04即对应热点指令视图(instructions)页面的类型标识。
- `compute_timeline.png`: **图示解读：**

1) **画面结构**：Compute Timeline 视图，纵轴为 core0–core7 多核泳道，core0 展开细分为 SCALAR/MTE2/VECTOR/MTE3/CACHEMISS 五条指令子轨；横轴时间刻度为 11.250μs–36.250μs（窗口 37.9μs），用三角标记瞬时事件、矩形条表持续时长。

2) **技术结论**：验证算子可在 8 核并行上按 SIMT 流水线执行，SCALAR/VECTOR 计算与 MTE2/MTE3 搬入搬出交错重叠，CACHEMISS 单独成轨便于定位访存瓶颈。

3) **与文档关系**：直观落地文档"Timeline 视图"与"JSON 复用 traceEvents"约定，是算子调优可视化的核心呈现。
- `compute_timeline_binary.png`: **图文联合解读：**

1) **图示内容**：Bin文件中"数据块=0x02"（指令流水）的二进制布局。首部12字节对齐4字节边界：8B内容长度（uint64） + 1B类型（0x02） + 1B补零长度 + 2B保留位；其后再装载指令流水的JSON文本。

2) **技术结论**：Bin采用「固定头+变长体」的分块编码，头部标识类型以区分不同页面数据，载荷直接复用Json文本，实现结构与语义的解耦。

3) **与文档关系**：直接印证"Bin数据通过数据块编码区分不同页面数据"的约定，并以0x02示例落地长度/类型/补零/保留四字段规范。
- `compute_operator.png`: **图示解读：**
该图为Compute详情面板，分三区块：①Base Info（算子名matmul_custom、Duration 1100.92μs、cube类型）；②Compute Workload Analysis（Pipe Utilization柱状图显示WAIT占比近2%最高，FP/ALL_ACTIVE极低，附CUBE0指令表：FP 128条、INT 0、数据量644MB）；③Memory Workload Analysis（带宽视图，含2.35GB/s峰值与LOC标注）。

**技术结论：** 算子以cube核心执行，瓶颈在WAIT等待而非计算，FP指令占满但内存带宽未饱和，揭示访存/调度延迟是主要优化点。

**与文档关系：** 印证文档所述"Timeline视图、热点指令视图和内存负载视图"的端到端可视化设计，即采集的traceEvents与Bin数据经解析后在此面板呈现多维度调优依据。
- `compute_operator_binary.png`: **图文联合解读：**

1) **图示内容**：展示Bin文件数据块结构，整体按4字节对齐，由5部分组成：8字节内容长度（uint64）+ 1字节类型标识（uint8=0x05，标识JSON数据流）+ 1字节补零长度（uint8）+ 2字节保留字段（reverse），其下承载JSON结构数据流。

2) **技术结论**：采用"长度前缀+类型标签+载荷"的TLV式二进制编码，类型字节（0x05）作为页面区分依据，长度字段支持变长数据，保留字段预留扩展能力，体现自描述、强兼容的二进制协议设计。

3) **与文档论点对应**：直接印证文档"Bin数据通过数据块编码区分不同页面数据"的约定，是后端文件解析流程中Bin格式规范化的可视化依据。
- `compute_calculate_load.png`: **图文联合解读：**

1）**画面内容**：Details 视图下展示"Compute Workload Analysis"面板。顶部列出算子名 matmul_custom、时间戳、Core Type=cube 及 Block ID 表（含 0 号 cube 块，时长 541.37μs）。中部为 Pipe Utilization 横向柱状图，按 WAIT、FP、ALL_ACTIVE、INT 四条流水线统计占比（WAIT≈2.9%，其余极小）。底部表格按 CUBE0 列出各管线指令数（FP/ALL_ACTIVE 各 128 条，INT 为 0）及 COMPUTE DATA SIZE=644874240 字节。

2）**技术结论**：该 cube 核几乎全程处于 WAIT 状态（≈2.9%），FP/INT 实际利用率极低，说明算子瓶颈在访存/调度等待而非计算本身，64MB 数据搬运耗时是主导因素。

3）**与文档关系**：对应文档"热点指令视图/内存负载视图"章节，通过 Pipe Utilization 与指令数、Data Volume 三者联动，直观呈现 Compute 数据的可视化呈现约定与瓶颈定位方法。
- `compute_calculate_load_binary.png`: **图解：**

1) 图示为Bin文件中单个数据块的二进制布局：头部8字节存内容长度（uint64），随后依次为1字节类型标识（0x06）、1字节补零长度、2字节保留字段，剩余空间承载JSON数据流，整体按4字节对齐。

2) 论证结论：通过「长度+类型+内容」的通用块头设计，可让单一Bin文件承载多页异构数据（页码由类型码区分），实现灵活复用与解析。

3) 对应文档「Bin数据通过数据块编码区分不同页面数据」的论点，是其具体落地的字节级规范。
- `compute_overload.png`: **图文联合解读**

**图示内容**：Compute Details 面板展示算子 `matmul_custom`（cube 类型，总耗时 1100.92μs）；Pipe Utilization 条形图中 **WAIT 占≈3% 主导**，FP / ALL_ACTIVE / INT 近乎为零；底部 CUBE0 表显示 FP=128 条指令、INT=0、计算数据量 644MB。

**技术结论**：该 cube 算子执行期间流水线严重空转，计算单元利用率极低，存在数据供给或流水线调度瓶颈。

**与文档关系**：印证文档中"Compute Workload Analysis 通过指令数 + Pipe 利用率量化算子调优空间"的设计主张，是性能可视化诊断的核心证据。
- `compute_overload_binary.png`: **图解：**

1) **结构**：展示Bin文件中数据块=12字节头部+JSON内容体。头部依次为：内容长度(uint64, 8B)、类型(uint8, 0x07)、补零长度(uint8, 1B)、保留(reverse, 2B)；尾部为JSON数据流，整体4字节对齐。

2) **技术结论**：通过类型字段0x07标识该块承载JSON数据，长度字段为大体积JSON预留空间，补零+保留字段保证对齐与扩展性，实现"按数据块类型区分页面数据"。

3) **与文档关系**：直接对应"Bin数据通过数据块编码区分不同页面数据"约定，与上文JSON文件格式互补——JSON存原始traceEvents，Bin通过0x07类型块编码封装，供Timeline等视图按需解析。
- `compute_heat_diagram.png`: **图解：**

1. **画面结构**：Memory Workload Analysis 内存负载分析视图，包含 Block ID 与 Bandwidth 显示控件。左侧 GM（全局内存）经 L2 Cache（命中率20%）流入 L1，再分流至 L0A/L0B 喂入 Cube，L0C 与 Cube 双向交互并旁路 L2。箭头标注带宽数值（如 L1→Cube 57.72 GB/s），右侧 Peak(%) 色阶表征利用率。

2. **技术结论**：呈现昇腾 AI 处理器核内存储层级（GM→L2→L1→L0A/B/C→Cube）的数据流与各级带宽瓶颈，可视化识别访存热点。

3. **与文档关系**：对应文档"内存负载视图"功能，佐证 0x0A 内存读写与 L2Cache 视图设计落地，通过带宽与命中率量化算子调优依据。
- `compute_heat_diagram_binary.png`: **图文联合解读：**

1）图示为Bin文件中单个数据块的二进制结构，整体按4字节对齐；头部由"内容长度(8B unsigned64)+类型(1B uint8=0x08)+补零长度(1B uint8)+保留(2B)"组成，共12B，尾部为JSON结构数据流内容。

2）论证了通过固定头部（含类型标识0x08）即可在Bin流中定位与区分不同页面数据块，无需依赖外部索引。

3）对应文档"Bin数据通过数据块编码区分不同页面数据"的论点，为后端解析Bin、定位各页面（如Timeline/热点指令等视图数据）提供编解码约定依据。
- `compute_heat_table.png`: **1) 图中内容**
图为「内存负载视图」的渲染效果：上方以拓扑图展示 GM→L2 Cache→L1→LOA/LOB→Cube→LOC 的数据通路，连线上标注实时带宽（GB/s），L2 旁显示 Hit Rate 20%；右侧 Peak(%) 颜色条映射吞吐强度；下方表格分 Cache、Cube、HBM、LOA、LOB 五大分区，按 Hit/Miss/Requests/Throughput 列统计。

**2) 技术结论**
可视化同时呈现"宏观通路"与"微观指标"：拓扑揭示瓶颈环节（如 L2→L1 仅 5.28 GB/s，LOA→Cube 14.43 GB/s，GM 读写近乎 0），表格定量佐证命中率与吞吐，证实 GM 利用率极低、Cube 单元负载较重。

**3) 与文档关系**
对应文档「0x0A 内存读写时序图 / 0x0B L2Cache 图」按 POC 能力记录的开发约定，验证了从 Bin 数据块解码带宽、命中率等核心指标并以拓扑+表格双视图落地的可行性，为稳定性与测试提供依据。
- `compute_heat_table_binary.png`: **图示解读**

图示内容：Bin 文件中 0x09 类型数据块的包头结构，自左至右为：内容长度（uint64，8B）＋类型标识（uint8=0x09，1B）＋补零长度（uint8，1B）＋保留字段（2B），合计 12B 满足 4 字节对齐；其后接「数据块内容：json 结构数据流」。

**技术结论**

论证了 Bin 二进制容器可借 0x09 数据块承载 JSON 结构数据，实现「二进制封装 + 文本负载」的混合编码；补零与保留字段为后续扩展与对齐预留空间。

**与文档论点关系**

呼应文档「Bin 数据通过数据块编码区分不同页面数据」的约定，说明 JSON 性能数据可经统一 Bin 通道下发，便于后端按块解析。
- `compute_memory_timing_diagram.png`: # 图文联合解读

## 1) 图中内容
该图为**内存负载视图**(0x0A 内存读写时序图)：横轴为时间戳(215~2401)、纵轴为内存地址(0x0~0x32666)。绿色竖线代表 LOAD、红色代表 STORE 操作；选中第 499 时间点弹出悬浮框，显示起始地址 0x1b800、大小 512、操作类型 LOAD、PC 行地址 0x15be0 及五层调用栈(指向 matmul_leakyrelu_kernel.cpp 等算子源文件)。顶部提供核ID/按类型/地址类型筛选，底部有缩略导航条。

## 2) 技术结论
该视图将算子运行期间对 UB(统一缓冲区)的访存事件按"地址×时间"二维映射，能直观暴露访存热点、读写比例及带宽占用，并通过悬浮框把底层访存回溯到 PC 与源码行号，实现"地址—指令—源码"三级溯源。

## 3) 与文档关系
对应文档"内存负载视图"功能实现，证明设计目标(POC 级能力)已落地：可视化、交互筛选、调用栈溯源均与"内存读写时序图按 POC 能力记录"的描述一致。
- `compute_memory_timing_diagram_binary_1.png`: **图文联合解读：**

1）图示内容：描绘了一个二进制数据块的整体布局，顶部标注"整体四字节倍数"。表头包含四个字段：数据块内容长度（unsigned64，8Byte）、数据块类型（uint5，0x0A）、长度（uint8，1Byte）、保留位（reverser，2Byte）；下方为"数据块内容：二进制流"。

2）技术结论：该图定义了Bin文件中数据块的统一编码格式——通过"块类型"字段（如0x0A）区分不同业务页面，通过"内容长度"字段定位变长负载，并设置保留位以支持未来扩展，体现"数据块头+二进制流负载"的可扩展二进制协议设计。

3）与文档关系：直接对应文档"数据文件格式 > Bin文件"章节及"通过数据块编码区分不同页面数据"的设计约定，是0x0A内存读写时序、0x0B L2Cache等POC能力数据的底层承载格式说明。
- `compute_memory_timing_diagram_binary_2.png`: ## 图文联合解读

**1) 图中内容**
展示 `memory_records.bin` 二进制文件的内存布局：由多个数据块串联组成，每个块包含三段式结构——`BinaryBlockHeader`（块头）→ `uint64_t`（记录本块数据长度）→ 数据载荷（如 `TraceRecord`、`CacheRecord`、`CallStack map JSON`），箭头明确标注 `uint64_t` 字段表示对应数据段的长度。

**2) 论证的技术结论**
Bin 文件采用**「块头+长度前缀+数据」的可变长分块编码**方案：长度字段让解析器无需预知整体结构即可定位下一块；通过块头可区分不同页面（Trace / Cache / CallStack）类型。

**3) 与文档论点的关系**
呼应文档中"Bin 数据通过数据块编码区分不同页面数据"的核心约定，说明 0x0A 内存读写时序与 0x0B L2Cache 的记录在落盘时共享统一的多块结构，仅块头类型与数据载荷不同，从而保证二进制解析的通用性与扩展性。
- `compute_L2Cache.png`: 图示为六面板热力图，标题含读取事件、写入事件、命中、未命中、缓存分配、读写空间；X轴为事件计数百分比（0-120），Y轴为地址索引（0-126），色阶由暗至红表示访问强度。

论证结论：写事件、命中与缓存分配区域（Y≈60-108）呈高密度红色块，说明该地址范围为热访问区；读取事件热区集中在Y≈45附近，呈细长条带；未命中沿Y≈45及底部零星分布，提示存在缓存替换热点。

与文档关系：对应文档中0x0A内存读写时序与0x0B L2Cache视图的可视化输出，展示不同内存操作类型下访存热点的空间分布特征，支撑Compute算子调优中内存负载与缓存行为的分析能力。
- `compute_L2Cache_binary.png`: **图解：** 二进制数据块头部为 `unsigned64`长度(8B)+类型`0x0B`(uint8)+补零长度(1B)+保留位(2B)，整体按4字节对齐，载荷为"结构体数组"。

**结论：** 0x0B L2Cache 数据块采用"头部元数据+结构体数组"分层编码，类型字段实现页面区分。

**对应论点：** 印证文档"通过数据块编码区分不同页面数据"的约定。
- `compute_innerCore_load.png`: **图示解读：**

**1) 图中内容**：MindStudio Insight"详情"页"核间负载分析"视图，以时钟周期为度量单位，展示Core0–Core23中各Cube0/Vector0/Vector1单元负载；右侧颜色等级(0-10)映射活跃度(绿高红低)。Core0-3的Vector单元显示为绿色高负载（8633/8038/8463/8136；8111/8608/8727/8624），其余核呈灰色空闲。

**2) 技术结论**：算子调优的负载分布可视化——可直观识别核间负载不均（仅前4核活跃）与单元瓶颈，辅助性能定位与并行优化。

**3) 与文档关联**：对应"热点指令视图"功能，印证JSON Trace Event Format数据经解析可渲染为多核多单元负载热力图。
- `compute_innerCore_load_binary.png`: # 图文联合解读

**1) 图示内容**：展示 Bin 数据块的二进制编码结构，由头部和数据块内容组成。头部固定为四字节倍数对齐，依次为 8Byte 的 unsigned64「数据块内容长度」、1Byte 的 uint8「数据块类型(0x0C)」、1Byte 的「长度」、2Byte「保留位」，其后为二进制流形式的数据块内容。

**2) 技术结论**：数据块通过类型字段(0x0C)与长度字段实现自描述，不同页面数据得以统一编码解析；保留位预留扩展空间，保证协议向前兼容。

**3) 与文档论点关系**：呼应「Bin 数据通过数据块编码区分不同页面数据」的约定，为 0x0A 内存读写、0x0B L2Cache 等多类型数据块提供统一的帧格式支撑。
- `compute_roofline.png`: **图文联合解读：**

1）图中内容：Roofline瓶颈分析-内存单元视图，双对数坐标（X：Ops/Byte 0.01~10⁷；Y：TOps/s 0.1~100），绘制11条内存操作屋顶线（L1/L0C/L1/UB读写、Vector读写等），数据点（Cube_FP 99.88%、Vec_MISC 82.61%等）均落在y=1附近水平线，底部提示"memory bound"。

2）技术结论：各指令实际算力远低于内存峰值带宽上限（约100 TOps/s），算子受限于内存带宽而非计算单元，属典型memory-bound瓶颈。

3）文档关联：印证Compute模块"内存负载视图"的设计目标——通过Roofline模型直观区分计算受限与访存受限，指导算子调优方向，与文档阐述的Timeline/热点指令/内存负载多视图协同定位瓶颈一致。
- `compute_roofline_binary.png`: **1) 图中内容：** 展示 Bin 文件数据块结构，由头部（8Byte 长度+1Byte 类型 0x0D+1Byte 长度字段+2Byte 保留位）和二进制流内容组成，整体要求四字节对齐。

**2) 技术结论：** 通过 0x0D 魔术字标识块类型，配合长度字段实现变长数据分块读取；保留位为后续扩展预留空间；四字节对齐保证内存访问效率。

**3) 与文档关系：** 印证文档"Bin 数据通过数据块编码区分不同页面数据"的约定，是该机制的具体二进制布局落地，与 Json 格式（traceEvents）形成互补的双格式设计方案。
- `compute_data_type.png`: **图文联合解读:**

1) **图示内容**: Kotlin 枚举 `DataTypeEnum`,定义 9 种数据类型: SOURCE=1(数据源)、TRACE=2(Trace 事件)、API_FILE=3/API_INSTR=4(API 文件与指令)、DETAILS_BASE_INFO=5(基础信息)、DETAILS_COMPUTE_LOAD_GRAPH=6 / TABLE=7(算子负载图与表)、DETAILS_MEMORY_GRAPH=8 / TABLE=9(内存负载图与表)。当前光标选中了 TRACE。

2) **技术结论**: 后端按整型 ID 区分二进制数据块(Bin)的页面内容,实现了"数据块编码区分不同页面"的设计约定;Trace、算子负载、内存负载、API 各有图与表两类呈现,数据语义与视图一一绑定。

3) **与文档关系**: 枚举值对应文档"功能涉及与实现"章节——TRACE 对应 Timeline/Trace Event Format,DETAILS_COMPUTE_LOAD 对应热点指令视图,DETAILS_MEMORY 对应内存负载视图,印证文档"Bin 数据通过数据块编码区分不同页面数据"的论点。
- `compute_data_structure.png`: ## 图文联合解读

**1) 图中内容**
该图描绘了 Compute 模块 Bin 文件中**指令流水（Pipeline）数据块**的二进制布局：头部 4 字节由四个字段组成——`数据块类型(0x02)`、`数据块补零长度(1Byte)`、`保留位(2Byte)`，加上前置的 8 字节 `数据块内容长度(unsigned64)`；紧随其后是变长的 `数据块内容：指令流水的json文本`。

**2) 技术结论**
论证了 Bin 文件采用**「长度+类型头 + JSON 文本载荷」**的混合编码方式：通过类型字节(0x02)区分不同页面/数据块语义，借助长度字段实现变长 JSON 文本的定界读取，并预留保留位以兼容后续扩展。

**3) 与文档论点关系**
紧扣文档"Bin 数据通过数据块编码区分不同页面数据"的论点，是该约定在**指令流水页面**的具体落地示例，补充说明了头部固定 4 字节的信息组织规则。
- `compute_hot_instructions_data_type.png`: **图文联合解读：**

**1) 图中内容：** Kotlin `enum class DataTypeEnum : int`，枚举值 1–9 分别对应 SOURCE、**TRACE(2，高亮选中)**、API_FILE、API_INSTR、DETAILS_BASE_INFO，以及 DETAILS_COMPUTE_LOAD_GRAPH/TABLE、MEMORY_GRAPH/TABLE。

**2) 技术结论：** 该枚举作为 Bin 文件数据块类型标识，将二进制页面按"源码、Trace、API、详情图/表"分类编码，与 JSON 中 `profilingType` 形成类型映射；TRACE=2 对应 Timeline 视图（`traceEvents`），DETAILS_* 6/8 对应计算负载与内存图块。

**3) 与文档关系：** 直接印证文档"Bin 数据通过数据块编码区分不同页面数据"及"0x0A 内存时序、0x0B L2Cache"的约定，是 Bin 解析与前端视图分发的类型字典。
- `compute_hot_instructions_source_binary.png`: 图示解读：

1) 结构：二进制数据块格式，含头部（内容长度8B + 类型0x01 + 长度1B + 保留2B）、4096B文件路径区、内容区，整块4字节对齐。
2) 论证：通过类型字节(0x01)区分不同页面数据块，路径与内容分离存储，便于解码时定位源码文件。
3) 对应文档"Bin数据通过数据块编码区分不同页面数据"的约定，是0x01类（代码路径块）的具体布局实现。
- `compute_hot_instructions_api_file_binary.png`: **图文联合解读：**

1) **图示内容**：展示 Bin 文件中一个数据块（block）的二进制布局结构。整体长度要求 4 字节对齐，由头部（4 字段）和内容体两部分组成：① 8Byte 内容长度（uint64）；② 1Byte 类型标识 `0x03`；③ 1Byte 补零长度；④ 2Byte 保留位（reverse）。内容体承载 `api.json` 的 files 段。

2) **技术结论**：块头采用"长度+类型+填充+保留"四段定长 12 字节小端编码，类型 `0x03` 即对应 api 文件分支；保留位与补零位预留扩展空间，保证按 4 字节对齐，便于流式解析与未来类型增补。

3) **与文档论点关系**：呼应文档"通过数据块编码区分不同页面数据"的约定，是 `0x03` 类型块指向 api.json files 部分的事实依据，支撑端到端 Bin 文件解析与按页分发读取的实现设计。
- `compute_hot_instructions_api_instr_binary.png`: **1) 图中内容：** 展示Bin文件中一个数据块的二进制结构布局。顶部标注"整体4字节倍数"对齐要求；头部从左至右依次为：内容长度（unsigned64，8Byte）、数据类型（uint8，值为0x04）、补零长度（uint8，1Byte）、保留位（reverse，2Byte）；下方为数据块载荷"api.json的instructions部分"。

**2) 技术结论：** 确立了指令数据块的二进制编码规范——通过类型字段0x04标识该块为instructions内容，固定头部+变长载荷，并满足4字节对齐约束。

**3) 与文档关系：** 印证文档"Bin数据通过数据块编码区分不同页面数据"的论点，给出instructions块的具体编码实例。
- `compute_memory_view.png`: **图示解读：**

1）图中定义 `DataTypeEnum` 枚举类，通过整型 ID 区分 9 种数据类型：source(1)、TRACE(2)、API_FILE(3)、API_INSTR(4)，以及 4 类详情页数据：BASE_INFO(5)、COMPUTE_LOAD_GRAPH/TABLE(6/7)、MEMORY_GRAPH/TABLE(8/9)。

2）论证：Bin 文件通过统一的 TypeID 字段作为数据块路由标识，前端依据 TypeID 解析对应负载（图/表/基础信息）。

3）呼应文档论点——"Bin 数据通过数据块编码区分不同页面数据"，枚举即该编码的具体实现，同时覆盖 Timeline 视图(TRACE)、热点指令(API_INSTR)与内存负载图(MEMORY_GRAPH)等所有功能页。
- `compute_details_base_info_binary.png`: **图解读：**

1) **结构**：图为Bin二进制数据块帧格式。头部长12字节（强制4字节对齐），由四字段组成：64位内容长度(8B)、uint8类型标识(此处为`0x05`，1B)、uint8补零长度(1B)、uint2字节保留位；下方承载JSON结构数据流。

2) **技术结论**：Bin采用「定长头+变长体」TLV式编码，类型号(0x05)实现多页数据分类，保留位预留扩展，体现自描述、可扩展的二进制容器设计。

3) **与文档呼应**：对应"Bin数据通过数据块编码区分不同页面数据"的约定，支撑JSON与Bin混合解析的文件结构设计。
- `compute_load_graph_binary.png`: **图解：**
该图描绘Bin文件中JSON数据块（类型0x06）的二进制头部结构：8字节长度字段（uint64）+ 1字节类型（0x06）+ 1字节补零长度 + 2字节保留，共12字节头，强制4字节对齐；其后为JSON结构数据流。

**技术结论：**
通过定长头+类型标识（0x06）区分页面数据，长度与补零保证块解析的对齐与边界安全，实现多类型数据块在同一Bin文件中共存。

**文档关系：**
对应文档"Bin数据通过数据块编码区分不同页面数据"的约定，支撑Compute模块将Json与Bin格式结合的混合存储设计。
- `compute_load_table_binary.png`: **图文联合解读：**

1) 图中展示了一个Bin二进制数据块结构，总长4字节对齐。头部依次为：8字节的`unsigned64`内容长度、1字节`uint8`类型码（0x07）、1字节补零长度、2字节保留字段；载荷部分承载json结构数据流。

2) 论证了Bin文件中通过统一头部+载荷的封装方式，将不同页面类型（如0x07=JSON页）以类型码区分，长度字段指明载荷边界，便于解析端定位。

3) 与文档"Bin数据通过数据块编码区分不同页面数据"论点对应，是其具体编码实例：JSON traceEvents以0x07类型块写入Bin，前后端依此解析。
- `compute_memory_graph_binary.png`: **图文联合解读：**

图示为Bin文件中单个数据块的二进制布局：4字节对齐，头部依次为8B内容长度(uint64)、1B类型标记(0x08)、1B补零长度、2B保留位，载荷为json结构数据流。

技术结论：采用"长度+类型+载荷"的自描述块结构，通过类型字节区分不同页面（如timeline、热点指令、内存视图），实现多类数据按块混合存储。

与文档关系：印证"Bin数据通过数据块编码区分不同页面数据"的设计约定，为0x08块类型对应json数据流提供格式依据。
- `compute_memory_table_binary.png`: **图解分析：**

**1) 图中内容：** 展示Bin文件数据块头部结构，标注"整体4字节倍数"对齐约束。自左至右依次为：8Byte的`unsigned64`内容长度、1Byte的`uint8`类型标识(0x09)、1Byte补零长度、2Byte保留字段；下方为承载`json结构数据流`的数据块内容区。

**2) 技术结论：** 采用类TLV定长头部（12Byte）+变长负载的混合编码。类型码`0x09`标识该块承载JSON数据，多个块串联即可在同一Bin文件中按类型分页。

**3) 与文档关系：** 对应文档"数据块编码区分不同页面数据"约定，是Bin文件中除JSON之外的二进制存储规范，体现Compute后端对多源性能数据的统一分块管理。
- `compute_memory_rw_time_diagram.png`: **图文联合解读：**

图示了 `memory_records.bin` 的二进制布局：起始为 `BinaryBlockHeader`，后接 `uint64_t`（TraceRecord 段长度）→ `TraceRecord`，再接 `uint64_t`（CallStack map 段长度）→ `CacheRecord` → `CallStack map JSON`。每段前置长度字段，实现定长切割与跳读。

论证结论：Bin 文件采用**长度前缀分段编码**方案，便于解析器按块读取、跳转定位不同页面数据，无需依赖定界符。

与文档关系：直接对应文档"数据文件格式→Bin 文件"章节及"Bin 数据通过数据块编码区分不同页面数据"的论点，是该机制的可视化实例。
- `compute_cache_hit_binary.png`: **图文解读：**

1）图示Bin文件的数据块头结构：含4字节对齐的总长度(8B unsigned64)、类型标识(uint8=0x0b，对应L2Cache页)、补零长度(1B)和保留位(2B)，其后接结构体数组内容。

2）论证了Bin文件通过"长度+类型+补零+保留位"的块头编码机制，区分不同页面数据（如0x0B L2Cache页）。

3）与文档"Bin数据通过数据块编码区分不同页面数据"的论点直接对应，是该约定的具体结构化实现说明。
