# 抽象硬件架构

> 仓 `agent-skills` · 路径 `community/Op/ascendc-operator-design/references/hardware-architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/community/Op/ascendc-operator-design/references/hardware-architecture.md

# ascend910b/ascend910_93 (A2/A3) 抽象硬件架构 · 一体化深度解读

---

## 【定位】

本文档作为 **Op/ascendc-operator-design** 知识库下的 *references/* 章节内容,系统抽象并描述了昇腾 910B1/B2/B3/B4(即 A2/A3 系列)AI Core 的硬件组成,目的是为上层 AscendC 算子开发者提供**底层硬件拓扑与数据通路的事实参照**,从而指导算子在向量化、向量化切分、双 buffer 流水线、搬运同步等方面的设计与优化。

---

## 【技术要点】

1. **AI Core 三类核心组件构成**:每一颗 AI Core 由**计算单元**(Scalar / Vector / Cube)、**存储单元**(多级 Local Memory)与**搬运单元**(DMA)三类硬件资源共同构成,这是昇腾 NPU 抽象编程模型的物理基础。
2. **计算单元分工与数量差异**:Scalar 负责标量计算与指令发射/控制;Vector 负责元素级向量运算(910B1/B2 各 **48** 个 vector core,910B3/B4 各 **40** 个);Cube 负责矩阵乘加等密集计算(910B1/B2 各 **24** 个 cube core,910B3/B4 各 **20** 个 —— 原文即如此措辞)。
3. **多级片上存储层次**:Local Memory 内部呈典型 **UB → L1 → L0A/L0B → L0C** 的金字塔结构,关键容量为 L1 Buffer = **512 KB**、L0A 与 L0B 各 **64 KB**、L0C = **128 KB**、Unified Buffer = **192 KB**(示例值,实际编码时通过 AscendC 接口动态获取)。
4. **DMA 承担搬运职责**:在 GM、Local Memory 与各 Buffer 之间,DMA 是唯一的"显式"高速搬运通道,这是算子设计中 MTE 阶段(数据搬运)建模的硬件依据。
5. **三流并行的异步执行模型**:Scalar 发射的**指令流**、保证顺序与一致性的**同步信号流**、以及在存储/计算单元之间流转的**数据流**三者解耦,这正是 AscendC 算子可以做双 buffer/双流水(software pipeline)的根本硬件机制。
6. **完整数据通路**:数据典型生命周期为 **GM → Local Memory → 计算单元 → Local Memory → GM**,即外部访存 → 板上缓存 → 计算 → 回写缓存 → 外部访存,所有计算均以 Local Memory 为中心。

---

## 【关键机制与数据】

### 数据流与执行流(三流并行,原文)
- **指令流**:Scalar 计算单元作为"指挥中枢",向 Vector/Cube/DMA 等其它单元下发指令。
- **同步信号流**:在不同单元之间传递"完成/就绪"信号,保证指令顺序与数据一致性 —— 这是 AscendC 中 `WaitFlag` / `SetFlag` 类同步原语的物理对应。
- **数据流**:数据沿 **GM → Local Memory → 计算单元 → Local Memory → GM** 的路径搬运。

### 存储层次(原文数值)
| 层级 | 容量(原文) | 用途推断 |
|---|---|---|
| L1 Buffer | 512 KB | 计算单元与外部之间的大容量交换区 |
| L0A / L0B Buffer | 各 64 KB | Cube 单元两侧输入缓冲 |
| L0C Buffer | 128 KB | Cube 单元结果累加缓冲 |
| Unified Buffer (UB) | 192 KB(示例值,实际以接口为准) | Vector 单元的主工作区,AscendC 中 `AscendC::TPipe`/`InitBuffer` 面向的对象 |

### 计算资源规模(原文)
- Vector core:910B1/910B2 = **48**,910B3/B4 = **40**。
- Cube core:910B1/910B2 = **24**,910B3/B4 = **20**(原文措辞为"20个vector core",但其位于 Cube 单元条目之下,应为原文笔误,本文忠实保留不做臆测性修正)。

---

## 【表格解读】

**原文无表格。**

(原文中所有容量、核心数量信息均以项目符号列表形式给出,未以表格结构呈现。)

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

文档**自身未提供**文末内部链接(本次给定元数据中标注为"无")。从其作为 *references/hardware-architecture.md* 的角色来看,本文是 **ascendc-operator-design** 知识库下"硬件事实层"的根参考,通常会被以下方向的内容反向引用,但原文未直接给出这些链接:

- 算子 Tiling 与切分策略(依据 L1 / UB 容量做 tile 大小选择);
- 双 buffer / 软件流水设计(依据三流异步机制);
- MTE(数据搬运)与 Cube/Vector 流水编排(依据 DMA 与 L0A/L0B/L0C 通路)。

具体上下游链接需结合仓库其它章节确认,**原文未涉及**。

---

## 【使用方法】

- **UB 容量的真实取值**:**原文提示**"Unified Buffer (UB):192KB(示例值,实际编码时通过接口获取)",即在 AscendC 算子代码中应通过运行时/平台接口(而非硬编码 192 KB)获取 UB 实际容量,这是编写可移植算子的关键约束。
- **其它容量参数**(L1 = 512 KB、L0A/L0B = 64 KB、L0C = 128 KB)以及 Vector/Cube core 数量在原文中均以静态数值给出,**原文未涉及**对应的运行时查询命令或 AscendC 配置项。
- 启用方式 / 编译命令 / 环境变量等内容,**原文未涉及**。
