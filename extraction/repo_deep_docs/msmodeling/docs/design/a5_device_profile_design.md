# 特性设计：A5 系列硬件 Device Profile 新增支持

> 仓 `msmodeling` · 路径 `docs/design/a5_device_profile_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/a5_device_profile_design.md

# A5 系列硬件 Device Profile 新增支持 — 一体化深度解读

## 【定位】

本文档描述 msmodeling 框架如何新增支持 ATLAS A5 系列硬件（350/850/850E/950，共 17 个 DeviceProfile）的性能建模能力，通过"组合模式"将算力、显存、互联三维度解耦，使框架可对基于 A5 硬件的推理场景进行吞吐、延迟仿真。

## 【技术要点】

1. **组合模式架构**：将硬件参数拆分为 `Chip`（算力）、`Mem`（显存）、`Interconnect`（通信拓扑）三个正交类，每个 DeviceProfile 通过 `**Chip.Cxxx + **Mem.Mxxx` 字典解包 + `comm_grid` 三行即可定义。
2. **覆盖 17 个 Profile**：横跨 4 个产品线，组合上限为 2 芯片 × 5 显存 × 6 拓扑（实际组合根据产品定位裁剪）。
3. **两类芯片算力**：
   - C486T：bf16/half MMA 432 TFLOPS、int8/FP8 MMA 865 TFLOPS、FP4 MMA 1730 TFLOPS、float32 GP 27 TFLOPS、bf16/half GP 54 TFLOPS；float32 MMA 使用 HF32 为 216 TFLOPS；计算效率 0.9。
   - C425T：bf16/half MMA 378 TFLOPS、int8/FP8 MMA 756 TFLOPS、FP4 MMA 1512 TFLOPS、float32 GP 24 TFLOPS、bf16/half GP 47 TFLOPS；HF32 189 TFLOPS；计算效率 0.9。
   - 量化加速比遵循标准规律：FP8 = bf16 × 2，FP4 = bf16 × 4；GP ops ≈ MMA × (1/8 ~ 1/6)；计算效率 0.9 相对 ATLAS_800 的 0.7 提升体现新硬件架构改进。
4. **五种显存规格**：M144G_4T（144 GB / 4.0 TB/s）、M128G_1_6T（128 GB / 1.6 TB/s）、M112G_1_4T（112 GB / 1.4 TB/s）、M96G_4_0T（96 GB / 4.0 TB/s）、M84G_1_4T（84 GB / 1.4 TB/s）；效率统一 0.8。
5. **六种通信拓扑**：PCIE2_UB4（最多 16 卡）、SERVER_ROCE_64（最多 64 卡）、SERVER_UB_128（最多 128 卡）、SERVER_UB_1K（最多 1024 卡）、SERVER_FM16（最多 16 卡）、POD_1K（最多 1024 卡）。
6. **零侵入注册**：所有新增代码位于单文件 `tensor_cast/device.py`，以 `class A5:` 组织，通过 `DeviceProfile.__post_init__` 自动注册，不改动现有代码。
7. **静态调度开销**：mma=5μs、gp=2μs、comm=5μs。
8. **PCle 折扣因子**：PCle 链路在效率上额外乘以 0.7，反映协议开销。

## 【关键机制与数据】

- **组合方式（原文）**：`Chip` 提供算力字典（float32_mma、bf16_mma、int8_mma、fp8_mma、fp4_mma、float32_gp、bf16_gp、compute_efficiency 等键），`Mem` 提供显存字典（capacity、bandwidth、efficiency 等键），`Interconnect` 提供 `CommGrid` 对象（三维 Grid 表示层级拓扑，每维含带宽、延迟、效率、互联方式说明）。三者通过 Python `**` 解包合成一个 `DeviceProfile`。
- **拓扑层级带宽聚合（原文）**：单机内卡间采用 FullMesh，单链路 56 GB/s（或板内 UB 53 GB/s），聚合带宽等于链路数 × 单链路带宽；机间/节点间通过 5808、Unions、5808+Unions 两级或 RoCE 进行交换。
- **延迟模型（原文）**：FullMesh 层延迟 1.5 μs（含 5808 路由时为 3.0 μs，经 Unions 路由时为 2.3 μs）；CPU 间 PCIe 延迟 3.0 μs，跨 CPU 延迟 4.5 μs；RoCE 延迟 10.0 μs。
- **效率分层（原文）**：所有互联层基础效率 0.85；PCle 链路额外乘 0.7 折扣因子 → CPU 到 CPU 效率 0.75×0.7、CPU 到设备效率 0.8×0.7；显存效率统一 0.8；计算效率统一 0.9。
- **产品定位差异（原文）**：
  - **ATLAS 350**：工作站级，PCIE2_UB4 拓扑，最大 16 卡，对应 C425T + M112G_1_4T 或 M84G_1_4T 组合。
  - **ATLAS 850**：服务器级，标准 SERVER_UB_1K（1024 卡），对应 C486T + M112G_1_4T 或 M128G_1_6T。
  - **ATLAS 850E**：服务器级 HBM2e 高带宽版（96 GB / 4.0 TB/s），同样 SERVER_UB_1K。
  - **ATLAS 850 RoCE/FM16 变体**：分别用 SERVER_ROCE_64（最大 64 卡）和 SERVER_FM16（最大 16 卡）。
  - **ATLAS 950**：千卡 POD，POD_1K 三级拓扑，最大 1024 卡，覆盖 M144G_4T / M128G_1_6T / M112G_1_4T / M96G_4_0T 四种显存。

## 【表格解读】

### 表 1：修订记录

| Date | Version | Change Description | Author | RFC Document |
|---|---|---|---|---|
| 2026-06-09 | 1.0 | 初稿完成，支持 ATLAS 350（A350_112G / A350_84G）硬件建模 | huqixing | — |
| 2026-08-24 | 1.1 | 补充 ATLAS 850 / 850E / 950 系列及 RoCE、FM16、POD 拓扑 | — | — |
| 2026-08-24 | 1.2 | 补充 ATLAS_950_486T_144G 设备画像 | — | — |

**解读**：1.0 仅覆盖工作站级 A350；1.1 扩展到服务器级 850/850E/950 及三种附加拓扑；1.2 补充 950 系列中的 144 GB 显存高端画像。

### 表 2：芯片算力规格（Chip）

| 规格 | bf16/half MMA | int8 / FP8 MMA | FP4 MMA | float32 GP | bf16/half GP | 计算效率 |
|---|---|---|---|---|---|---|
| **C486T** | 432 TFLOPS | 865 TFLOPS | 1730 TFLOPS | 27 TFLOPS | 54 TFLOPS | 0.9 |
| **C425T** | 378 TFLOPS | 756 TFLOPS | 1512 TFLOPS | 24 TFLOPS | 47 TFLOPS | 0.9 |

**解读**：C486T 与 C425T 比例约 432:378 ≈ 1.143；两者 GP/MMA 比分别约为 27/432≈0.063、24/378≈0.063（约 1/16），处于原文所述 1/8~1/6 区间偏低位；FP8/bf16 = 2、FP4/bf16 = 4 严格遵循标准加速比。

### 表 3：显存规格（Mem）

| 规格 | 容量 | 带宽 | 效率 | 使用方 |
|---|---|---|---|---|
| **M144G_4T** | 144 GB | 4.0 TB/s | 0.8 | A950_486T_144G |
| **M128G_1_6T** | 128 GB | 1.6 TB/s | 0.8 | A850_486T_128G, A850_486T_128G_ROCE, A850_486T_128G_FM16, A950_486T_128G |
| **M112G_1_4T** | 112 GB | 1.4 TB/s | 0.8 | A350_112G, A850_486T_112G, A850_486T_112G_ROCE, A850_486T_112G_FM16 |
| **M96G_4_0T** | 96 GB | 4.0 TB/s | 0.8 | A850E_486T_96G, A850E_425T_96G, 以及对应 ROCE/FM16 变体, A950_486T_96G |
| **M84G_1_4T** | 84 GB | 1.4 TB/s | 0.8 | A350_84G |

**解读**：带宽分为两档——1.4~1.6 TB/s 为普通 DDR 级（M84G/M112G/M128G_1_6T），4.0 TB/s 为 HBM 级（M144G/M96G_4_0T），后者面向带宽敏感型大 batch prefill；M96G_4_0T 在 850E 与 950 系列共用，850E 借此实现 96 GB + 4 TB/s 的高带宽组合。

### 表 4：PCIE2_UB4 拓扑参数

| 层级 | 互联方式 | 带宽 | 延迟 | 效率 |
|---|---|---|---|---|
| dim 2 | 3 路 UB FullMesh | 159 GB/s | 1.5 μs | 0.85 |
| dim 1 | 2 路 PCIe x16 到 CPU | 32 GB/s | 3.0 μs | 0.8 × 0.7 |
| dim 0 | CPU 间 3 路 PCIe x16 | 24 GB/s | 4.5 μs | 0.75 × 0.7 |

**解读**：Grid=(2,2,4) 共 16 卡；dim 2 单链路 53 GB/s × 3 路 = 159 GB/s 为板内最高带宽；dim 1 跨 CPU 通道走 PCIe x16，效率叠加 0.7 折扣因子，体现 PCIe 协议开销；dim 0 跨两 CPU 仅 24 GB/s，是 PCIE2_UB4 拓扑的最弱扩展维度。

### 表 5：SERVER_ROCE_64 拓扑参数

| 层级 | 互联方式 | 带宽 | 延迟 | 效率 |
|---|---|---|---|---|
| dim 1 | 7 路 UB FullMesh | 392 GB/s | 1.5 μs | 0.85 |
| dim 0 | RoCE | 50 GB/s | 10.0 μs | 0.85 |

**解读**：Grid=(8,8) 共 64 卡（8 机 × 8 卡）；机内 56 GB/s × 7 = 392 GB/s 远高于机间 RoCE 50 GB/s，反映机内/机间带宽不对称；RoCE 延迟 10.0 μs 是六种拓扑中最高的单链路延迟。

### 表 6：SERVER_UB_128 拓扑参数

| 层级 | 带宽 | 延迟 | 效率 | 说明 |
|---|---|---|---|---|
| dim 1 | 840 GB/s | 3.0 μs | 0.85 | 计入 5808 路由延迟 |
| dim 0 | 448 GB/s | 3.0 μs | 0.85 | |

**解读**：Grid=(16,8) 共 128 卡；机内 8 卡 FullMesh 15 × 56 = 840 GB/s；机间 16 节点经 5808 交换 8 × 56 = 448 GB/s；与 1K 拓扑相比延迟均为 3.0 μs（无 Unions 中间层）。

### 表 7：SERVER_UB_1K 拓扑参数

| 层级 | 带宽 | 延迟 | 效率 | 说明 |
|---|---|---|---|---|
| dim 1 | 840 GB/s | 2.3 μs | 0.85 | Unions 路由延迟短于 5808 |
| dim 0 | 448 GB/s | 4.5 μs | 0.85 | 经 5808 + Unions 两级交换 |

**解读**：Grid=(128,8) 共 1024 卡；与 128 卡版本相比，机内延迟从 3.0 μs 降至 2.3 μs（Unions 路由更短），但机间因两级交换延迟升至 4.5 μs；适用于 ATLAS 850/850E 标准千卡组网。

### 表 8：SERVER_FM16 拓扑参数

| 层级 | 带宽 | 延迟 | 效率 |
|---|---|---|---|
| dim 0 | 840 GB/s | 1.5 μs | 0.85 |

**解读**：Grid=(16,) 共 16 卡全互联，56 GB/s × 15 = 840 GB/s；单层 FullMesh，无机间交换，延迟最低（1.5 μs），代表单机 16 卡最佳带宽/延迟组合。

### 表 9：POD_1K 拓扑参数

| 层级 | 带宽 | 延迟 | 效率 | 说明 |
|---|---|---|---|---|
| dim 2 | 840 GB/s | 2.3 μs | 0.85 | 机内互联 |
| dim 1 | 448 GB/s | 4.5 μs | 0.85 | Union 级 |
| dim 0 | 224 GB/s | 4.5 μs | 0.85 | 跨 POD 5808 交换，带宽为其他两层的 1/2 |

**解读**：Grid=(16,8,8) 共 1024 卡，三级层级依次为机内 → Union → POD；机内 840 GB/s、Union 级 448 GB/s、POD 间 224 GB/s（仅 4 × 56），带宽随层级递减；POD 间延迟 4.5 μs 与 Union 级相同，是六种拓扑中唯一显式标注"带宽为其他两层 1/2"的层级。

### 表 10：ATLAS 350 系列 Profile 清单

| Profile 名称 | 芯片 | 显存 | 互联 | 最大卡数 |
|---|---|---|---|---|
| `ATLAS_350_425T_112G` | C425T | M112G_1_4T | PCIE2_UB4 | 16 |
| `ATLAS_350_425T_84G` | C425T | M84G_1_4T | PCIE2_UB4 | 16 |

**解读**：350 系列仅用 C425T + 112G/84G + PCIE2_UB4，定位工作站级，不支持服务器级拓扑。

### 表 11：ATLAS 850 系列 Profile 清单

| Profile 名称 | 芯片 | 显存 | 互联 | 最大卡数 |
|---|---|---|---|---|
| `ATLAS_850_486T_112G` | C486T | M112G_1_4T | SERVER_UB_1K | 1024 |
| `ATLAS_850_486T_128G` | C486T | M128G_1_6T | SERVER_UB_1K | 1024 |

**解读**：850 系列使用 C486T 满血芯片 + 1.4/1.6 TB/s 显存 + 千卡 UB 拓扑，对应服务器级标准组网。

### 表 12：ATLAS 850E 系列 Profile 清单

| Profile 名称 | 芯片 | 显存 | 互联 | 最大卡数 |
|---|---|---|---|---|
| `ATLAS_850E_486T_96G` | C486T | M96G_4_0T | SERVER_UB_1K | 1024 |
| `ATLAS_850E_425T_96G` | C425T | M96G_4_0T | SERVER_UB_1K | 1024 |

**解读**：850E 与 850 区别仅在显存（96 GB / 4.0 TB/s HBM2e vs 112~128 GB / 1.4~1.6 TB/s）；同卡数和拓扑，意味着 850E 牺牲容量换带宽，面向带宽敏感型推理。

### 表 13：ATLAS 850 RoCE 变体 Profile 清单

| Profile 名称 | 芯片 | 显存 | 互联 | 最大卡数 |
|---|---|---|---|---|
| `ATLAS_850_486T_112G_ROCE` | C486T | M112G_1_4T | SERVER_ROCE_64 | 64 |
| `ATLAS_850_486T_128G_ROCE` | C486T | M128G_1_6T | SERVER_ROCE_64 | 64 |
| `ATLAS_850E_486T_96G_ROCE` | C486T | M96G_4_0T | SERVER_ROCE_64 | 64 |
| `ATLAS_850E_425T_96G_ROCE` | C425T | M96G_4_0T | SERVER_ROCE_64 | 64 |

**解读**：将 850/850E 显存组合映射到 SERVER_ROCE_64 拓扑，最大卡数从 1024 降至 64（8 机 × 8 卡）；用于 RoCE 直连部署场景。

### 表 14：ATLAS 850 FM16 变体 Profile 清单（原文截断）

| Profile 名称 | 芯片 | 显存 | 互联 | 最大卡数 |
|---|---|---|---|---|
| `ATLAS_850_486T_112G_FM16` | C486T | M11…（原文截断） | — | — |

**解读**：原文此表仅展示开头一行即被截断，未完整呈现 16 卡 FullMesh 变体的全部 Profile；按命名规律推断应包含 C486T/C425T × 112G/128G/96G 多种组合映射到 SERVER_FM16（最大 16 卡），但原文未给出完整清单与最大卡数列，故仅可确认 `ATLAS_850_486T_112G_FM16` 这一个 Profile 的存在与命名规则。

## 【公式解读】

原文**无**独立 LaTeX 公式或伪代码公式块，但文中嵌入了若干**带宽聚合运算**用于表达 FullMesh 拓扑聚合带宽：

- `53 GB/s × 3 = 159 GB/s`（PCIE2_UB4 dim 2：板内 3 路 UB FullMesh 聚合带宽）
- `32 GB/s`（PCIE2_UB4 dim 1：两组 4 卡通过 2 路 PCIe x16 连接到 CPU 的有效带宽，原文直接给出结果）
- `24 GB/s`（PCIE2_UB4 dim 0：双 CPU 间等效 3 路 PCIe x16 有效带宽）
- `56 GB/s × 7 = 392 GB/s`（SERVER_ROCE_64 dim 1：机内 8 卡间 7 路 UB FullMesh）
- `50 GB/s`（SERVER_ROCE_64 dim 0：8 节点间 RoCE 单链路带宽）
- `56 GB/s × 15 = 840 GB/s`（SERVER_UB_128 / SERVER_UB_1K / SERVER_FM16 / POD_1K dim 2：机内 8 卡 FullMesh 15 路聚合）
- `56 GB/s × 8 = 448 GB/s`（SERVER_UB_128 / SERVER_UB_1K dim 0：节点间 5808 交换 8 路聚合；POD_1K dim 1：Union 级 8 节点间互联 8 路聚合）
- `56 GB/s × 4 = 224 GB/s`（POD_1K dim 0：16 Union 组间 5808 交换 4 路聚合）
- `216 TFLOPS = 432 TFLOPS / 2`（C486T float32 MMA 为 bf16 的一半，采用 HF32 表示）
- `189 TFLOPS = 378 TFLOPS / 2`（C425T float32 MMA 同理）

其中符号含义统一为：`单链路带宽 × 链路数 = 聚合有效带宽`，单链路在板内为 53 GB/s（UB），跨设备为 56 GB/s（UB/5808/Unions），跨节点远程为 50 GB/s（RoCE）。

## 【关联】

- **DeviceProfile**：是 msmodeling 中描述单个硬件画像的核心数据结构，本设计通过 `DeviceProfile.__post_init__` 自动注册新 Profile，实现零侵入。
- **Chip / Mem / Interconnect 三个内嵌类**：组织于 `tensor_cast/device.py` 单文件 `class A5:` 命名空间下，提供原子化规格字典。
- **CommGrid**：Interconnect 类内部使用的拓扑描述对象，承载 Grid 维度与每维的带宽/延迟/效率/说明。
- **CLI 模块 `cli.inference.text_generate`**：用户入口，使用示例在第 1.3 节给出（Qwen3-8B + ATLAS_350_425T_112G + TP=2 + MXFP4 量化）。
- **上游已支持型号**：ATLAS 800 系列（A2 / A3），本次扩展为 A5 系列，组合模式设计使后续扩展新一代硬件（A6 或更高）只需新增对应 Chip/Mem/Interconnect 字典项即可。
- **下游性能仿真**：用户调用时配合 `--num-devices`、`--tp-size`、`--compile`、`--quantize-linear-action` 等参数对推理策略做吞吐/延迟预测。

## 【使用方法】

原文示例（CLI 方式）：

```bash
python -m cli.inference.text_generate Qwen/Qwen3-8B \
    --num-queries 8 --query-length 1024 \
    --device ATLAS_350_425T_112G \
    --num-devices 2 --tp-size 2 --compile \
    --quantize-linear-action MXFP4
```

要点（原文涉及）：
- 通过 `--device` 指定 A5 Profile 名称（如 `ATLAS_350_425T_112G`）；
- 通过 `--num-devices`、`--num-queries`、`--query-length` 控制规模；
- 通过 `--tp-size` 设置张量并行度；
- 通过 `--compile` 启用编译优化；
- 通过 `--quantize-linear-action MXFP4` 指定线性层量化方式；
- 编程接口（原文未给出具体 API 示例，但明确"用户可通过 CLI **或编程接口**指定 A5 硬件"）。

> 注：原文 ATLAS 950 系列的完整 Profile 清单、ATLAS 850 FM16 变体的完整 Profile 清单与最大卡数因文档末尾截断未完整呈现，故本解读中相关条目以"原文截断"或基于命名规律谨慎推断，并明确标注不确定性。
