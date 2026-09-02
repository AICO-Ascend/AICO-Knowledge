# AI QoS Feature

> 仓 `vllm-ascend` · 路径 `docs/source/user_guide/feature_guide/Ai_QoS_introduction_en.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/user_guide/feature_guide/Ai_QoS_introduction_en.md

# 一体化深度解读: vllm-ascend AI QoS Feature 文档

---

## 【定位】

这篇文档介绍了 vLLM-Ascend 提供的 **AI QoS (Quality of Service) 功能**, 用于解决推理场景中不同类型流量 (算子下发、集合通信、KVCache) 在 UB 交换机上互相抢占带宽、导致推理延迟升高与 SLO 受影响的问题。该功能通过在 UB 交换机侧引入 **Virtual Lane (VL) 隔离 + Strict Priority (SP) 调度**, 实现三类关键流量 (AIV / SDMA / PCIEDMA) 的差异化服务质量保障。

---

## 【技术要点】

1. **问题场景**: 推理过程中存在三类竞争流量——算子下发 (operator delivery)、集合通信 (collective communication)、KVCache 传输; 在 Agentic AI 长上下文场景下, KVCache 因体积增长被 offload 到 DDR, 又叠加"以计算掩盖 KVCache 预取" 的流水线编排, 进一步放大了流量冲突。

2. **冲突发生位置**: UB 交换机侧, 同时汇聚了节点内 D2D (device-to-device) 流量、节点内 H2D (host-to-device) 流量、跨节点 D2D 流量 (原文配图 ai_qos1.png)。

3. **核心机制 — VL 隔离 + SP 调度**: 在 UB 交换机侧把不同类型流量映射到不同 VL, 并通过 SP (strict priority) 严格优先级调度——高优先级 VL 流量优先调度, 其次中优先级, 依次类推, 从而避免拥塞蔓延并实现差异化调度 (原文配图 ai_qos2.png)。

4. **三层映射闭环**:
   - (1) 在 host 侧为不同 NPU channel 设置优先级;
   - (2) 建立 NPU channel 优先级 ↔ UB 交换机 VL 的映射;
   - (3) 在 UB 交换机侧基于优先级在 VL 之间做差异化调度。

5. **两种运行模式**: **Auto 模式** (默认, `python -m tools.ai_qos`) 自动分类并生成 QoS tag; **Manual 模式** (`--mode manual --AIV {p} --SDMA {p} --PCIEDMA {p}`) 接受用户指定的三类流量优先级。

6. **启用门槛**: 必须先编译安装 `tools/ai_qos` 扩展 (依赖 DSMI 头文件 `dsmi_common_interface.h` 与库文件 `libdrvdsmi_host.so`), 然后在运行推理任务之前执行上述命令, 生成的 UB 交换机配置需要管理员手动登录交换机粘贴执行——配置会**覆盖**交换机当前 QoS 配置, 故操作前需备份。

---

## 【关键机制与数据】

**工作原理 (原文 Introduction 段)**

- 流量隔离机制: 不同流量经由不同 channel 传输 → AI QoS 方案通过**设置 host 侧 NPU channel 优先级**、**建立 NPU channel 优先级到 UB 交换机 VL 的映射**、**在 UB 交换机不同 VL 间做差异化调度**, 完成流量隔离与差异化调度。
- 调度算法: **Strict Priority (SP)**, 多 VL 同时到达时按"高 → 中 → 低" 优先级依次调度, 直至全部排空。
- 流量映射关系 (由 Manual 模式参数定义):
  - **AIV** = AIV-based D2D 通信 (dispatch / combine) + AIV-based 算子下发;
  - **SDMA** = SDMA-based D2D 通信 (Allreduce / Allgather) + H2D/D2H 通信 (KVCache offload 与 prefetch);
  - **PCIEDMA** = PCIe DMA-based 算子下发。

**性能数据 / 量化指标**

- 原文**未提供**具体的延迟、带宽、TPS 等量化性能数字, 也未给出 VL 数量、priority 等级数等结构参数。文档仅定性指出该机制用于"防止拥塞扩散"、"实现差异化调度"、"减少推理延迟, 满足 SLO"。

---

## 【表格解读】

### 表格 1 — Manual 模式参数表 (原文逐字还原)

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| mode | str | auto | The mode of AI QoS, default mode is "auto", another mode is "manual", some parameters need to be configured if you choose "manual" mode. |
| AIV、SDMA、PCIEDMA | str | AIV: high,<br />SDMA: low,<br />PCIEDMA: high | Parameters for "manual" mode that determine the QoS priority of different traffic types.<br />The default configuration is the same as "auto" mode.<br />AIV covers AIV-based Device-to-Device communication, such as dispatch and combine, and AIV-based operator delivery.<br />SDMA covers SDMA-based Device-to-Device communication, such as Allreduce and Allgather, and Host-to-Device/Device-to-Host communication, such as KVCache offloading and prefetching.<br />PCIEDMA covers PCIe DMA-based operator delivery.<br />All three parameters support "high/middle/low". |

**逐行解读**

- **mode 行**: 唯一顶层模式开关, 字符串类型, 默认 `"auto"`; 选 `"manual"` 时必须配套给出 AIV/SDMA/PCIEDMA 三个优先级参数。
- **AIV、SDMA、PCIEDMA 行**: 三个流量类型共用同一行展示 (因参数语义同质), 默认值就是 Auto 模式自动生成的策略——**AIV 与 PCIEDMA 为 high, SDMA 为 low**; 三者均支持 `"high/middle/low"` 三档优先级。该行还顺带定义了每类流量涵盖的物理操作: AIV 负责 D2D (dispatch/combine) 与算子下发; SDMA 负责集合通信 (Allreduce/Allgather) 与 KVCache 上下传; PCIEDMA 负责 PCIe DMA 算子下发。

### 表格 2 — 软件版本兼容表 (原文逐字还原)

| Software | Matched Version |
| :---: | :---: |
| Ascend HDK | 25.5.2 or later |
| UB Switch | LingQu Computing Network 1.5.1 or later |

**逐行解读**

- **Ascend HDK**: 驱动/CANN 栈版本要求 **25.5.2 或更高**, 否则无法获得底层 DSMI 接口支持 (这是 QoS 配置下发的前提)。
- **UB Switch**: "灵衢 Computing Network 1.5.1 或更高", 这与文档中反复提到的"登录 UB 交换机粘贴配置" 流程一致——QoS 策略的最终执行点在交换机侧的固件/操作系统版本。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文**未提供**任何内部超链接, 但从内容本身可识别出以下模块/组件之间的上下游关系:

- **tools/ai_qos (Python 入口) ↔ tools/ai_qos (C/C++ 扩展)**: 文档开篇要求先用 CMake 构建并 `cmake --install` 安装到 `${PWD}/vllm_ascend`, 之后才能调用 `python -m tools.ai_qos`; 表明 `ai_qos` 是一个 Python 包 + C 扩展的混合模块, 扩展依赖 DSMI 主机侧库与头文件 (`dsmi_common_interface.h`、`libdrvdsmi_host.so`)。
- **AI QoS ↔ UB 交换机**: AI QoS 工具只**生成并打印**UB 交换机的 QoS 配置命令, **不直接下发**; 需要管理员手动登录交换机粘贴执行, 且 `unset` (禁用) 也是同样模式。配置具有**覆盖性**, 操作前需备份交换机原 QoS 配置。
- **AI QoS ↔ NPU Channel**: 工具运行时通过 DSMI 在 host 侧为 NPU channel 设优先级, 是 host 端的 NPU channel 优先级配置源点。
- **AI QoS ↔ KVCache offload/prefetch**: 文档背景明确将 KVCache 的 DDR offload 与"以计算掩盖 KVCache 预取" 的流水线编排列为冲突的根源, 因此 AI QoS 是 KVCache 卸载特性的配套 QoS 保障。
- **AI QoS ↔ Atlas 800T A3 / Atlas 900 A3 SuperPoD**: 仅支持这两类硬件平台, 且需以**特权容器** (privileged container) 方式运行——`DSMI_INCLUDE_DIR`、`DSMI_LIBRARY` 需在容器创建时挂载进容器文件系统。
- **AIV 通道 ↔ 驱动限制**: 当前底层驱动版本下 AIV 的 QoS 配置**不生效**, 需等待后续驱动版本适配——这意味着 AI QoS 当前在 AIV 流量上实际是"占位但未生效" 的状态。

---

## 【使用方法】

### 1. 编译安装 AI QoS 扩展 (在 vLLM-Ascend 仓库根目录执行)

```bash
cmake -S tools/ai_qos -B tools/ai_qos/build \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=${PWD}/vllm_ascend \
  -DDSMI_INCLUDE_DIR=YOUR_DSMI_INCLUDE_DIR \
  -DDSMI_LIBRARY=YOUR_DSMI_LIBRARY_FILE
cmake --build tools/ai_qos/build -j
cmake --install tools/ai_qos/build
```

需先将 `YOUR_DSMI_INCLUDE_DIR` (例如 `/usr/local/Ascend/driver/include`) 与 `YOUR_DSMI_LIBRARY_FILE` (例如 `/usr/local/Ascend/driver/lib64/driver/libdrvdsmi_host.so`) 替换为本机实际路径; 通常在容器内执行, 因此容器创建时需把这两个目录挂载进去, 否则 CMake 找不到文件。

### 2. Auto 模式 (运行推理任务前, 在 vLLM-Ascend 安装目录下)

```bash
python -m tools.ai_qos
```

自动分类三类流量优先级并生成 QoS tag, 同时打印 UB 交换机配置——复制输出后登录 UB 交换机粘贴执行 (会覆盖既有 QoS 配置)。

### 3. Manual 模式

```bash
python -m tools.ai_qos --mode manual --AIV {priority} --SDMA {priority} --PCIEDMA {priority}
```

`{priority}` 取值为 `high / middle / low`; 同样会把 UB 交换机配置打印到屏幕, 需手动登录交换机执行。

### 4. 关闭 AI QoS

```bash
python -m tools.ai_qos unset
```

屏幕会打印禁用命令, 登录 UB 交换机执行即可关闭。

### 5. 关键约束 (原文 Usage Constraints 段)

- AIV 的 QoS 配置**当前因驱动限制不生效**, 需后续驱动版本支持后通过模块升级交付;
- 仅支持 **Atlas 800T A3 服务器**与 **Atlas 900 A3 SuperPoD 集群**;
- 必须运行于**特权容器**中;
- 配套软件版本: **Ascend HDK 25.5.2+**, **UB Switch 灵衢 Computing Network 1.5.1+**。

## 图文联合解读

- `ai_qos1.png`: 图示CPU板、两块NPU板及多个UB交换机；黄、蓝、红粗箭头分别表示节点内D2D、H2D和节点间D2D流量，并在UB交换处冲突。结论是需利用UB平面VL隔离并差异化调度各类流量，降低推理时延、保障SLO，直接支撑文档的AI QoS论点。
- `ai_qos2.png`: 1）高、中、低优先级流量分别进入VL1/2/3队列，每队4个单元；2）经“US”调度器统一输出，本轮4个单元均来自VL1；3）说明按优先级可保障关键流，但可能导致低优先级延迟甚至饥饿，对应文档利用虚拟通道隔离流量并实施差异化QoS的方案。
