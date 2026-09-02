# 虚拟机手动绑核配置介绍

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/user_manual/introduction_to_manual_cpu_binding_for_virtual_machines.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/user_manual/introduction_to_manual_cpu_binding_for_virtual_machines.md

# 虚拟机手动绑核配置介绍 — 深度解读

## 【定位】

本文档解决的是**在虚拟机场景下使用 ATB Models 进行推理时, 如何通过手动绑核 (将 NPU 关联到正确的 NUMA 节点 / CPU 核) 来提升推理性能**的问题, 给出从查 PCI、查 NUMA、到写 sysfs 的端到端手工绑核操作流程。

---

## 【技术要点】

1. **PCI 设备发现 (VM 内)**: 使用 `npu-smi info` 查询 NPU 在虚拟机内的 PCI ID, 例如 npu 0 → `0000:08:00.0`。
2. **物理机—虚拟机 PCI 映射**: 在物理机上用 `virsh list --all` 拿到虚拟机名, 再用 `virsh edit {虚拟机名称}` 查 PCI 透传对应关系, 例: VM 上 `0000:08:00.0` 对应物理机 `0000:C1:00.0`。
3. **NUMA 节点定位 (物理机)**: 用 `cat /sys/bus/pci/devices/{pci id}/numa_node` 查物理机 NUMA 归属, 例: `0000:C1:00.0` → NUMA node `6`。
4. **NUMA → CPU 核清单 (物理机)**: 用 `lscpu` 查到 NUMA node 6 对应物理机 CPU `192-223`。
5. **物理机—虚拟机 NUMA / CPU 映射 (双层查询)**: 同样通过 `virsh edit {虚拟机名称}` 在 `<numa>` 段中读取:
   - 红框 1: VM CPU ↔ 物理机 CPU 对应 (如 VM CPU 191 ↔ 物理 CPU 247)。
   - 红框 2: VM 自身 NUMA cell 定义 (如 cell id='0' → cpus='0-23')。
   - 经推算, 物理机 NUMA node 6 (cpu 192-223) → VM NUMA node 6 (cpu 144-167), 故 npu 0 对应 **VM NUMA node 6**。
6. **写入绑核配置 (VM 内)**: `echo x > /sys/bus/pci/devices/{pci id}/numa_node`, 例: `echo 6 > /sys/bus/pci/devices/0000\:08\:00.0/numa_node`。
7. **结果验证**: 通过查询 MindIE LLM 日志 (参见《MindIE日志参考》「查看日志」章节) 确认绑定成功的 NPU。

---

## 【关键机制与数据】

- **原文**: VM 内 NPU 0 → PCI `0000:08:00.0`; 经 `virsh edit` 映射到物理机 PCI `0000:C1:00.0`。
- **原文**: 物理机读 sysfs 得到 `0000:C1:00.0` → NUMA node `6`。
- **原文**: 物理机 `lscpu` 显示 NUMA node 6 对应 CPU `192-223`。
- **原文**: `virsh edit` 中 VM 配置示例 — VM CPU 191 对应物理 CPU 247; VM NUMA cell id='0' cpus='0-23'。
- **原文**: 经映射, 物理机 NUMA node 6 (cpu 192-223) 对应 VM NUMA node 6 (cpu 144-167), 因此 npu 0 对应 **VM NUMA node = 6**。
- **原文**: 最终生效命令 `echo 6 > /sys/bus/pci/devices/0000:08:00.0/numa_node`, 将 npu 0 的 NUMA 亲和性写到 sysfs。
- **原理性流程 (数据流)**: 查 NPU PCI (VM) → 查 PCI 透传映射 (物理) → 查物理 NUMA → 查物理 NUMA 的 CPU 列表 → 查物理↔虚拟机 NUMA/CPU 双层映射 → 反推得到 VM 端 NUMA node → 写 sysfs 完成 NPU-CPU 亲和性绑定 → 日志验证。

---

## 【表格解读】

**原文无表格。** 原文所有结构化信息均以「图」(figure 1-6) 形式给出 (图片不可读), 文档正文未出现任何 markdown/HTML 表格。

---

## 【公式解读】

**原文无公式。** 文档不涉及任何数学公式或伪代码表达式, 操作完全由 shell 命令与 sysfs 路径表达。

---

## 【关联】

- **ATB Models**: 本文档所述绑核操作是「在虚拟机场景下使用 ATB Models 进行推理」时的性能前置条件, 即绑核为 ATB Models 推理流程的前置调优步骤。
- **MindIE LLM 日志**: 步骤 7 引用了 **《MindIE日志参考》** 的「查看日志」章节, 用以验证绑核是否成功; 日志中显示「绑定成功的 NPU」即图 6 所示内容为判定标志。
- **virsh / libvirt 工具链**: 步骤 2、5 均依赖 `virsh list --all` 与 `virsh edit {虚拟机名称}`, 表明本文档假设运行环境使用 libvirt 管理的虚拟化平台。
- **NUMA / sysfs 内核接口**: 步骤 3、6 通过 `/sys/bus/pci/devices/{pci id}/numa_node` 这一内核导出节点完成 NUMA 亲和性设置, 依赖 Linux 内核对 PCI 设备 NUMA 亲和性的 sysfs 支持。
- **昇腾 NPU 工具链**: 步骤 1 使用的 `npu-smi info` 命令, 表明该方案针对昇腾 NPU 硬件。

---

## 【使用方法】

按文档所述的 7 步流程, 在物理机与虚拟机两端配合操作:

| 步骤 | 位置 | 命令 / 操作 |
|---|---|---|
| 1 | VM 内 | `npu-smi info` → 取 NPU 的 PCI ID |
| 2 | 物理机 | `virsh list --all` 查虚拟机名 → `virsh edit {虚拟机名称}` 查 PCI 透传映射 |
| 3 | 物理机 | `cat /sys/bus/pci/devices/{pci id}/numa_node` 查物理 NUMA node |
| 4 | 物理机 | `lscpu` 查 NUMA node 对应 CPU 列表 |
| 5 | 物理机 | `virsh edit {虚拟机名称}` 查 VM CPU↔物理 CPU 与 VM NUMA cell 映射, 反推 NPU 对应的 VM NUMA node |
| 6 | VM 内 | `echo {x} > /sys/bus/pci/devices/{pci id}/numa_node`, 其中 x 为步骤 5 推得的 VM NUMA node |
| 7 | — | 查询 MindIE LLM 日志 (参见《MindIE日志参考》「查看日志」章节) 验证绑核成功 |

> **关键 sysfs 写入示例 (步骤 6, 原文)**:
> ```bash
> echo 6 > /sys/bus/pci/devices/0000:08:00.0/numa_node
> ```
> 该命令对 npu 0 完成绑核, 使其 NUMA 亲和性指向 VM NUMA node 6 (cpu 144-167)。

文档未提供单独的「配置项 / 配置文件 / 开关」, 也没有提供脚本化或自动化的批量绑核方案 — 所有操作均为**手工逐设备执行**。

## 图文联合解读

- `virtual_machines_figure1.png`: **图文联合解读：**

该图为虚拟机内执行 `npu-smi info` 的终端输出，列出 NPU 0–7 的健康状态、功耗、温度及 PCI Bus-Id，红框标注 **NPU 0 的 PCI ID 为 0000:08:00.0**，下方表格显示各 NPU 无运行进程。

**技术结论：** 通过 `npu-smi info` 可在虚拟机内获取 NPU 设备的 PCI ID，作为后续在物理机上查询 NUMA 节点、CPU 拓扑及虚拟机-物理机映射关系的起点。

**与文档关系：** 此图是文档第 1 步操作的可视化依据，确立"虚拟机 NPU → PCI ID"这一映射链的开端，为后续跨物理-虚拟机的 NUMA/CPU 绑核链路（步骤 2–5）提供入口标识。
- `virtual_pciic_physical_c1.png`: **图解读：**

1. **画面内容**：virsh edit输出的XML配置片段，含多组`<hostdev>`节点，每节点用两个`<address>`分别标注物理机PCI地址（source）与虚拟机PCI地址；红框高亮`bus='0xc1'`（物理机）与`bus='0x08'`（虚拟机）。

2. **技术结论**：证明PCI设备在虚拟化穿透中存在一一映射，物理机bus 0xc1对应虚拟机bus 0x08，可据此实现NPU的PCI ID对应查询。

3. **与文档关系**：即文档图2，支撑"查物理机—虚拟机PCI对应关系"步骤，为后续NUMA节点定位和绑核提供基础依据。
- `numa_node6.png`: **图文联合解读：**

图3展示了物理机上执行命令 `cat /sys/bus/pci/devices/0000\:c1\:00.0/numa_node` 的终端输出，root用户下返回结果为**6**。

**技术结论：** PCI设备 `0000:c1:00.0`（即物理机上对应虚拟机NPU 0的设备）属于NUMA node 6。

**与文档论点关系：** 该图为文档步骤3的配图，证明可通过sysfs查询PCI设备归属的NUMA节点，从而为后续步骤4（用`lscpu`定位该NUMA节点对应的CPU范围192-223）及手动绑核操作提供NPU所在NUMA节点的依据，是虚拟化场景下NPU-CPU绑核的关键中间步骤。
- `numa_node6_cpu_192223.png`: **图解读：**

1）**画面内容：** 终端执行`lscpu`的输出，显示华为鲲鹏920服务器（256核/8 NUMA节点）的硬件拓扑。架构信息：aarch64、HiSilicon、64核/4线程；红框圈出NUMA段，重点标注`NUMA node6 CPU(s): 192-223`。

2）**技术结论：** NPU 0所在物理PCI设备(0000:C1:00.0)对应的NUMA node 6包含32个物理CPU核（192-223），证明该NP
- `virtual_interface.png`: **图示解读：**

图中为`virsh edit`输出的虚拟机XML配置片段，两处红框标注：
- **框1（cputune）**：`vcpupin`定义vCPU到物理cpuset映射，如vCPU 191→cpuset 247。
- **框2（numa）**：`<cell>`列出cell0~7的cpus范围，cell id='6'对应cpus='144-167'。

**技术结论：** 物理NUMA6（cpu192-223）↔虚拟机cell6（cpu144-167），结合图1-4链路推导，证实NPU 0所在虚拟机NUMA node为6。

**与文档关系：** 为步骤6的`echo numa_node > /sys/bus/pci/...`提供numa_node=6的依据，支撑手动绑核方案。
- `successful_npu.png`: **图文联合解读：**

1）图中是一行Python日志代码：`logger.info(f"process {p.pid}, new_affinity is {new_affinity}, cpu count {cpu_num_per_device}")`，记录进程PID、新绑定的CPU亲和性（new_affinity）及每设备CPU数量。

2）该代码是步骤6手动绑核操作的执行结果输出，证实`affinity`绑定接口已被调用并生效，进程成功绑定到指定NUMA节点对应的CPU核。

3）与文档论点呼应：本文档旨在指导虚拟机场景下为提升ATB Models推理性能进行手工绑核，该日志是绑核成功的验证证据，衔接前5步的查询（pci id→物理机NUMA→虚拟机NUMA→cpu号），形成完整操作闭环。
