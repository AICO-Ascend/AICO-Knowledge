# Design Document: A3 RoCE Device Profile 新增支持

> 仓 `msmodeling` · 路径 `docs/design/a3_roce_device_profile_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/a3_roce_device_profile_design.md

# 一体化深度解读：A3 RoCE Device Profile 新增支持

## 【定位】

本文档解决的是 msmodeling 在"双机 ATLAS 800 A3 + RoCE 互联"这一特定部署拓扑下的性能建模缺失问题——原 A3 die Profile 基于 HCCS 互联（196 GB/s，48 节点），无法准确刻画 RoCE 替代 HCCS 后的实际带宽与拓扑规模，文档提出通过复用算力 Profile + 替换通信网格的零侵入方式，新增 `A3_INTERCONNECT_ROCE` 与 `A3_560T_128G_DIE_ROCE`，将其纳入既有 `DeviceProfile`/`CommGrid` 框架。

---

## 【技术要点】

1. **通信网格规模收窄**：将 grid 第一维从 48 降为 2，即 `(2, 8, 2)`，从拓扑层面硬性约束最大节点数为 2、最大 die 数为 32（双机），杜绝被配置为超过双机的规模。
2. **节点间带宽降为 HCCS 的 1/8**：使用浮点表达式 `196 * 1e9 / 8` 推导出 24.5 GB/s 作为 RoCE tier 0 带宽（而非硬编码），保证可追溯性；tier 0 延迟保持 `5.5 μs`，通信效率 `0.7`。
3. **机内与板内拓扑完全复用**：tier 1（机内 CLOS，196 GB/s，0.5 μs）、tier 2（板内 SIO，224 GB/s，0.2 μs）与原 `A3_INTERCONNECT` 一致，唯一差异点限定在 tier 0。
4. **算力/显存 Profile 零修改**：560T die 的 `mma_ops`（float32: 75T / bfloat16: 245.8T / half: 280T / int8: 560T）、`gp_ops`（float32: 8T / bfloat16/half: 16T）、64 GB 显存、1.6 TB/s 带宽、compute=0.7 / memory=0.6 效率，均沿用 `A3_560T_128G_DIE`，仅切换 `comm_grid`。
5. **自动注册机制**：借助 `DeviceProfile.__post_init__`，新增 Profile 无需手动注册即可进入 `all_device_profiles`，CLI 与 Web UI 可直接消费，对既有 API/CLI 零破坏。
6. **测试覆盖三维**：单元测试（grid shape、tier 参数、Profile 属性、注册校验、CommGrid 校验、Topology/StaticCost 默认值）+ 集成测试（29 passed, 52 subtests passed）+ 端到端 CLI（`Qwen/Qwen3-32B` + `--device ATLAS_800_A3_560T_128G_DIE_ROCE`）。

---

## 【关键机制与数据】

**工作原理（原文: "复用算力参数 + 替换通信网格"）**

建模时 msmodeling 将设备抽象为两层——计算属性（算力/显存/效率，绑定在 DeviceProfile 上）和通信属性（节点内/板内的层级拓扑，绑定在 CommGrid 上）。由于 RoCE 与 HCCS 的差异只发生在节点间（tier 0），其余维度（HCCS 一级 CLOS、板内 SIO）相同，故无需重写算力 spec，只需新定义一个 grid 第一维为 2、tier 0 带宽为 24.5 GB/s 的 `A3_INTERCONNECT_ROCE`，并把既有 `A3_560T_128G_DIE` 的 `comm_grid` 字段切到新网格即可。整个变更局限在 `tensor_cast/device.py` 的 `ATLAS_800` 类内 ~50 行。

**关键数据流（原文: "仿真结果中节点间通信带宽按 RoCE 的 24.5 GB/s 计算，而非原始 HCCS 的 196 GB/s"）**

- 上游：用户在 CLI 或编程接口通过名称 `ATLAS_800_A3_560T_128G_DIE_ROCE` 选定设备 → `DeviceProfile.all_device_profiles` 查表返回实例 → 读取其 `comm_grid`（即 `A3_INTERCONNECT_ROCE`）。
- 下游：仿真器沿 grid 的三阶拓扑逐层计算通信耗时——tier 0（RoCE，5.5 μs 延迟 + 24.5 GB/s 带宽）、tier 1（CLOS，0.5 μs + 196 GB/s）、tier 2（SIO，0.2 μs + 224 GB/s）；相比 HCCS，**仅 tier 0 段耗时显著上升**，因此整模型通信耗时占比变高（端到端成功标准第 4 条明示此预期）。

**性能/规模数据**（原文逐字保留）

- 最大 die 数：32（双机 × 8 SIO × 2 die/SIO）
- tier 0 带宽：24.5 GB/s；延迟：5.5 μs；效率：0.7
- tier 1 带宽：196 GB/s；延迟：0.5 μs
- tier 2 带宽：224 GB/s；延迟：0.2 μs
- mma_ops（FLOPs）：float32 75T / bfloat16 245.8T / half 280T / int8 560T
- gp_ops：float32 8T / bfloat16&half 16T
- memory：64 GB @ 1.6 TB/s
- efficiency：compute 0.7 / memory 0.6
- `ATLAS_800.STATIC_COST`（mma/gp/comm）：5 μs / 2 μs / 10 μs
- 测试结果：`29 passed, 52 subtests passed`（覆盖 7 个测试类）

---

## 【表格解读】

### 表 1：修订记录（原文逐字还原）

| Date (日期) | Version (修订版本) | Change Description (修改描述) | Author (作者) | RFC Document (RFC文档) |
| --- | --- | --- | --- | --- |
| 2026-05-21 | 1.0 | 初稿完成，支持800I A3双机RoCE直连 | huqixing | — |

**逐行解读**：仅有一条初稿记录，日期为 2026-05-21，版本 1.0，作者 huqixing，明确本文档支持的是 **800I A3 双机 RoCE 直连**场景，RFC 文档尚未关联（"—"）。

---

### 表 2：A3_INTERCONNECT vs A3_INTERCONNECT_ROCE 对比（原文逐字还原）

| 项目 | A3_INTERCONNECT (原始) | A3_INTERCONNECT_ROCE (新增) |
| --- | --- | --- |
| **grid 形状** | `(48, 8, 2)` | `(2, 8, 2)` |
| **最大设备数** | 768 dies | 32 dies（仅双机） |
| **tier 0（节点间）** | 两级 CLOS，196 GB/s，5.5 μs | **RoCE，24.5 GB/s，5.5 μs** |
| **tier 1（机内）** | 一级 CLOS，196 GB/s，0.5 μs | 一级 CLOS，196 GB/s，0.5 μs（不变） |
| **tier 2（板内 SIO）** | SIO，224 GB/s，0.2 μs | SIO，224 GB/s，0.2 μs（不变） |

**逐行解读**：

- **grid 形状**：原始为 `(48, 8, 2)`（48 节点 × 8 SIO × 2 die），新增为 `(2, 8, 2)`。第一维从 48 缩到 2 是文档"关键设计决策 1"的核心动作，物理含义是限定最多 2 个节点。
- **最大设备数**：从 768 dies（48×8×2）降到 32 dies（2×8×2），降幅 96%，体现 RoCE 部署仅限双机的硬约束。
- **tier 0（节点间）**：原始用两级 CLOS + 196 GB/s；新增改为 **RoCE + 24.5 GB/s**，延迟同为 5.5 μs，但带宽降至 1/8，这是性能仿真上"通信变慢"的全部来源。延迟保持不变是因为 RoCE 替代的是传输介质，时延特性在文档建模中视为与 HCCS 一致。
- **tier 1（机内）**：两级都采用一级 CLOS + 196 GB/s + 0.5 μs，机内拓扑与原 A3 完全一致，证明差异被严格隔离在 tier 0。
- **tier 2（板内 SIO）**：均为 SIO + 224 GB/s + 0.2 μs，板内互联亦不动。

---

### 表 3：代码组织结构（原文逐字还原）

| 新增项 | 行位置 | 说明 |
| --- | --- | --- |
| `A3_INTERCONNECT_ROCE` | ~L184 | RoCE 通信网格定义 |
| `A3_560T_128G_DIE_ROCE` | ~L383 | 560T die + RoCE |

**逐行解读**：

- 通信网格定义集中在 `tensor_cast/device.py` 约第 184 行，紧邻原 `A3_INTERCONNECT`，便于读者对照差异。
- 设备 Profile 定义在约第 383 行，与 `A3_560T_128G_DIE` 同区域，仅切 `comm_grid` 字段。两处都落在同一个 `ATLAS_800` 类内，~50 行总量符合"零侵入"承诺。

---

### 表 4：`A3_560T_128G_DIE_ROCE` 设备 Profile 定义（原文为字段块，按 spec 形态还原）

| 字段 | 值 |
| --- | --- |
| name | `ATLAS_800_A3_560T_128G_DIE_ROCE` |
| vendor | `HUAWEI` |
| comm_grid | `A3_INTERCONNECT_ROCE` |
| mma_ops.float32 | 75T |
| mma_ops.bfloat16 | 245.8T |
| mma_ops.half | 280T |
| mma_ops.int8 | 560T |
| gp_ops.float32 | 8T |
| gp_ops.bfloat16/half | 16T |
| memory | 64 GB @ 1.6 TB/s |
| efficiency.compute | 0.7 |
| efficiency.memory | 0.6 |

**逐行解读**：

- **name**：新增 Profile 名以 `_ROCE` 后缀与原 `ATLAS_800_A3_560T_128G_DIE` 区分，便于 CLI/UI 直接点名。
- **vendor**：维持 `HUAWEI`，与既有 A3 系列一致。
- **comm_grid**：唯一与原 Profile 不同的字段，指向 `A3_INTERCONNECT_ROCE`，承担全部通信差异。
- **mma_ops**：覆盖四种典型精度（fp32/bf16/fp16/int8），其中 int8 560T 与 Profile 名中"560T"对应（命名约定）；bf16 245.8T 与原 Profile 相同。
- **gp_ops**：通用矩阵乘以外算力仅给两组精度（bf16 与 half 共享 16T），体现通用算力的精度合并策略。
- **memory**：64 GB 容量 + 1.6 TB/s 带宽，与 die 级 Profile 保持一致。
- **efficiency**：compute 0.7 / memory 0.6，复用既有 A3 die 效率系数。

---

## 【公式解读】

**公式 1（原文: "tier 0 带宽降为 1/8：`196 * 1e9 / 8 = 24.5 GB/s`"）**

$$ \text{tier0\_bandwidth} = \frac{196 \times 10^{9}}{8} = 24.5 \text{ GB/s} $$

- `196`：HCCS 节点间原始带宽数值（单位 GB/s 标称，对应原始表 tier 0 的 196 GB/s）。
- `1e9`（即 $10^9$）：将标称的"GB/s 量级"按十进制换算引入表达式，使推导以国际单位制 SI 形式可追溯（按 1 GB = $10^9$ Byte）。
- `/ 8`：原文明确给出的衰减系数——RoCE 实际带宽约为 HCCS 的 1/8。
- `= 24.5 GB/s`：推导结果，对应新增 CommGrid tier 0 的设定带宽。

**作用**：用浮点表达式而非硬编码写入 Profile，便于后续维护时回溯"24.5 是怎么来的"。若 HCCS 基准值修订或衰减系数调整，只需改动一处常量。

---

## 【关联】

文档未提供文末内部链接（"内部链接: (无)"），但正文多处点名了与本文变更相关的模块与机制，构成上下游关系网：

- **既有框架**：`DeviceProfile` / `CommGrid` / `InterconnectTopology` / `StaticCost` —— 本文严格遵循既有 dataclass 与自动注册路径，不引入新框架。
- **既有 Profile / CommGrid**：`A3_560T_128G_DIE`、`A3_INTERCONNECT` —— 本文通过"复用前者 + 替换后者字段"派生新增项，避免重复定义算力。
- **注册与分发机制**：`DeviceProfile.__post_init__` → `all_device_profiles` → CLI（`cli.inference.text_generate`）+ Web UI —— 本文变更自动获得 CLI/Web UI 可见性，无需手工注册。
- **测试体系**：`tests/test_tensor_cast/test_device.py`（参数化覆盖 `_DEVICE_PROFILE_SPECS`）—— 验证集随新增 Profile 自动扩展，确保后续维护不退化。
- **上层业务示例**：`Qwen/Qwen3-32B` 文本生成 —— 端到端验证选取的具体模型，代表性地演示 RoCE 拓扑在大模型推理仿真下的链路可达性。
- **上游设计约束**：A2 / A3 die 已存在的硬件建模（`ATLAS 800` 系列）—— 本文是同框架内的"互联方式"扩展，未来如需支持更多节点 RoCE，需新建如 `(N, 8, 2)` 形态的 CommGrid（见 §3.3 约束 3）。

---

## 【使用方法】

**原文有明确启用方式，整理如下：**

### CLI 启用

```powershell
python -m cli.inference.text_generate Qwen/Qwen3-32B \
    --device ATLAS_800_A3_560T_128G_DIE_ROCE \
    --num-queries 2 \
    --query-length 3500
```

### 编程接口启用

```python
from tensor_cast.device import DeviceProfile
import torch

profile = DeviceProfile.all_device_profiles["ATLAS_800_A3_560T_128G_DIE_ROCE"]
print(profile.comm_grid.grid.shape)  # (2, 8, 2)
print(profile.mma_ops[torch.bfloat16])  # 245.8e12
```

### 端到端验证命令（按 §4.3）

```bash
python -m cli.inference.text_generate <model_id> \
    --device ATLAS_800_A3_560T_128G_DIE_ROCE \
    --num-devices 32 \
    --num-queries 32 \
    --query-length 4 \
    --num-mtp-tokens 3 \
    --context-length 4352 \
    --compile \
    --tp-size 16 \
    --dp-size 2 \
    --ep-size 32 \
    --quantize-linear-action W8A8_DYNAMIC
```

### 单元/集成测试

```bash
python -m pytest tests/test_tensor_cast/test_device.py -v
```

### 约束与限制（§3.3 原文）

1. 仅支持双机（grid 第一维硬编码为 2）；
2. 仅 die 层级，与 `A3_560T_128G_DIE` 一致，不涵盖整芯片层级；
3. 不支持 RoCE 超 2 节点；如需支持，需新增 grid 第一维为 N 的 CommGrid（如 `(N, 8, 2)`）。
