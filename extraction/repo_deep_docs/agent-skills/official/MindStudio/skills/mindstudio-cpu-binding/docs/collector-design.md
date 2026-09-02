# MVP 采集器设计

> 仓 `agent-skills` · 路径 `official/MindStudio/skills/mindstudio-cpu-binding/docs/collector-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/MindStudio/skills/mindstudio-cpu-binding/docs/collector-design.md

# 深度解读：MVP 采集器设计

## 【定位】
本文档定义了 MindStudio CPU 绑核分析场景下的 MVP 采集器（collector）设计：一份在目标机器上以**只读、低侵入、可追溯**方式采集 Host CPU 拓扑、NPU 拓扑、进程/线程亲和性、cgroup 限制、运行时环境与 CPU 采样数据，并输出符合 `snapshot-schema.md` 的 JSON 报告的 Python CLI 设计。它本身不做诊断、不做修改、不做自动优化，仅作为下游 Agent 规则触发（如"未绑核""跨 NUMA""线程池过载""cgroup/cpuset 冲突"）的证据采集层。

---

## 【技术要点】

1. **采集器交付形态**：第一版规划为 Python CLI，目录结构为 `mindstudio-cpu-binding/collector/` 下包含 `collect.py` 与五个 adapter（`linux_cpu.py`、`linux_proc.py`、`linux_cgroup.py`、`npu_topology.py`、`runtime_env.py`）。当前仓库仅先实现 `scripts/topology_collect.py` 与 `scripts/process_discovery.py` 两个只读原型以验证数据契约，完整 collector 后续复用其 parser。

2. **完整 Snapshot 采集 CLI 主入口参数**：使用 `python scripts/cli.py collect`，必填 `--pid`，可选 `--scenario`（`training`/`inference`/`unknown`）、`--framework`（MVP 默认 `pytorch`）、`--device-type`（MVP 默认 `npu`）、`--optimization-goal`（`throughput`/`latency`/`stability`/`isolation`）、`--rank-map`（rank/PID/NPU 映射）、`--sample-seconds`（默认 10 秒）、`--output`（必填）、`--raw-dir`（可选）。

3. **六大采集模块的优先/降级数据源**：
   - `linux_cpu.py`：优先 `lscpu` / `lscpu -e=...` / `numactl -H`，备用 `/sys/devices/system/cpu/online`、`/sys/devices/system/cpu/cpu*/topology/*`、`/sys/devices/system/node/node*/{cpulist,meminfo}`。
   - `linux_proc.py`：优先 `/proc/<pid>/{status,stat,cmdline}` 与 `/proc/<pid>/task/<tid>/{status,stat,comm}`，可选 `ps -eLo pid,tid,psr,pcpu,stat,comm`。
   - `linux_cgroup.py`：从 `/proc/<pid>/cgroup` 与 `/sys/fs/cgroup/**/` 下 cpuset/cpu 相关文件采集。
   - `npu_topology.py`：支持三种方式——平台命令（`npu-smi info`、`npu-smi info -t topo`）、用户映射文件、CLI `--rank-map`。
   - `runtime_env.py`：从 `/proc/<pid>/environ`、`/proc/<pid>/cmdline` 读取 12 类可识别环境变量（`LOCAL_RANK`/`RANK`/`WORLD_SIZE`/`MASTER_ADDR`/`MASTER_PORT`/`OMP_NUM_THREADS`/`MKL_NUM_THREADS`/`OPENBLAS_NUM_THREADS`/`GOTO_NUM_THREADS`/`KMP_AFFINITY`/`KMP_BLOCKTIME`/`ASCEND_VISIBLE_DEVICES`/`CUDA_VISIBLE_DEVICES`），并接受 `--torch-num-threads` 等用户补充参数。
   - `runtime_sample.py`：优先 `pidstat -t -p <pid> 1 <seconds>` 与 `mpstat -P ALL 1 <seconds>`，备用 `/proc/stat` 与 `/proc/<pid>/task/<tid>/stat`。

4. **role_hint 保守推断规则**：基于 TID 与线程名匹配 6 类标签——`main`（TID==PID）、`dataloader`（含 `DataLoader`/`worker`）、`openmp_worker`（含 `omp`/`OpenMP`）、`blas_worker`（含 `blas`/`mkl`）、`communication`（含 `hccl`/`comm`/`communication`），其他归为 `unknown`。

5. **cpu_migration_observed 判定**：MVP 简单逻辑——同一 TID 在采样窗口中 `current_cpu` 出现多个不同值，即认为发生 CPU 迁移。

6. **采集原则与安全边界**：默认只读、不要求 root（缺权限时记 `availability.errors`）、禁止执行 `taskset -p`/`numactl` 启动/`sysctl`/写 cgroup 文件、禁止使用 ftrace/eBPF/perf、禁止发送数据到外部服务；外部命令缺失时降级到 `/proc`、`/sys` 文件；原始输出统一落盘 `raw_refs` 便于追溯。

---

## 【关键机制与数据】

### 工作原理

1. **Snapshot 生成流程（10 步）**：解析 CLI 参数 → 初始化 collection 和 workload → 采集 system/cpu_topology/numa_topology → 采集 npu_topology → 采集 processes/threads → 采集 cgroup → 采集 pytorch env → 运行 runtime sample → 汇总 `availability.missing`/`errors`/`warnings` → 写出 `snapshot.json` 与 `raw_refs`。

2. **数据契约（已实现原型的离线验证）**：以 `samples/*.txt` 作为输入，运行：
   ```bash
   python scripts/cli.py collect-topology --lscpu-file samples/lscpu.sample.txt --npu-smi-topo-file samples/npu-smi-topo.sample.txt --out out/topology.json
   python scripts/cli.py discover-processes --ps-file samples/ps.sample.txt --npu-smi-info-file samples/npu-smi-info.sample.txt --out out/processes.json
   ```
   真实节点上则用 `python scripts/topology_collect.py --out out/topology.json` 与 `python scripts/process_discovery.py --out out/processes.json` 独立原型入口跑 live 只读输出。

3. **NUMA 缺失的不猜测策略**：当 `npu_topology` 无法采集时，不臆造 NUMA，写入 `{"vendor":"unknown","devices":[],"source":null}`，并在 `availability.missing` 中记录 `npu_topology.devices[*].numa_node`（原文明确指出"无法采集时不要猜测 NUMA"）。

4. **进程外不可读的明确边界**：`torch.get_num_threads()`、`torch.get_num_interop_threads()`、DataLoader 实例参数从外部进程通常无法可靠读取，原文要求这些字段"应优先由用户提供、启动脚本静态分析或应用内探针补充"，MVP 外部采集不到时必须标记缺失。

5. **cgroup v1/v2 字段不一致的处理**：原文规定"只填可用字段"，并对容器中无法访问完整 `/sys/fs/cgroup` 的场景记录 `availability.errors`，将 cgroup 段标记为 `partial`。

### 性能数据

**原文未涉及**具体的性能数据（如采样开销、JSON 大小、采样精度等量化指标）。

### 输出目录结构（原文 §7）
```
snapshot-output/
├── snapshot.json
└── raw/
    ├── lscpu.txt
    ├── lscpu-e.txt
    ├── numactl-H.txt
    ├── proc-12345-status.txt
    ├── proc-12345-cmdline.txt
    ├── proc-12345-task/{12345-status.txt, 12345-stat.txt, 12345-comm.txt}
    ├── cgroup-12345.txt
    ├── npu-topology.txt
    ├── pidstat.txt
    └── mpstat.txt
```

---

## 【表格解读】

### 表 1：CLI 参数表（原文 §3）

| 参数 | 必填 | 说明 |
|------|------|------|
| `--pid` | 是 | 目标 PID，可重复。 |
| `--scenario` | 否 | `training` / `inference` / `unknown`。 |
| `--framework` | 否 | MVP 默认为 `pytorch`。 |
| `--device-type` | 否 | MVP 默认为 `npu`。 |
| `--optimization-goal` | 否 | `throughput` / `latency` / `stability` / `isolation`。 |
| `--rank-map` | 否 | rank、PID、NPU 设备映射。 |
| `--sample-seconds` | 否 | 运行期采样时长，默认 10 秒。 |
| `--output` | 是 | Snapshot JSON 输出路径。 |
| `--raw-dir` | 否 | 原始命令输出目录。 |

**逐行解读**：
- `--pid` 为唯一硬必填项，且文档明确"可重复"，意味着多 PID（多 rank 进程）通过多次传参实现，原文未指定上限。
- `--scenario` 的 `unknown` 兜底值允许在调用方对训练/推理不确定时仍可发起采集，避免采集器自身做业务判断。
- `--framework` 与 `--device-type` 都以"MVP 默认"措辞标注，意味着该参数为后续扩展位（MVP 仅支持 PyTorch+NPU 组合）。
- `--optimization-goal` 的 4 个枚举值（吞吐/时延/稳定性/隔离）与绑核决策的目标对齐，是下游诊断器选择规则的输入。
- `--rank-map` 用 `rank0=12345:npu0,rank1=12346:npu1` 形式承载分布式 rank→PID→NPU 设备的三元映射，是多卡场景必备。
- `--sample-seconds` 默认 10 秒为运行时采样窗口，与 `runtime_sample.py` 中 `pidstat/mpstat` 的采样周期对应。
- `--output` 是必填项，区别于可选的 `--raw-dir`（原始命令落盘目录），二者路径独立。

### 表 2：linux_proc.py 字段映射表（原文 §5.2）

| 来源 | Snapshot 字段 |
|------|---------------|
| `/proc/<pid>/status` `Cpus_allowed_list` | `processes[*].cpus_allowed_list` |
| `/proc/<pid>/status` `Mems_allowed_list` | `processes[*].mems_allowed_list` |
| `/proc/<tid>/stat` processor | `threads[*].current_cpu` |
| `/proc/<tid>/status` ctxt switches | `threads[*].voluntary_ctxt_switches` / `nonvoluntary_ctxt_switches` |
| `/proc/<tid>/comm` | `threads[*].name` |

**逐行解读**：
- 前两行对应进程级亲和性：`cpus_allowed_list`（CPU 允许集）与 `mems_allowed_list`（NUMA 允许集）从 `/proc/<pid>/status` 直接解析，决定进程能否在目标 CPU/NUMA 上运行。
- 第 3 行 `processor` 字段映射为 `threads[*].current_cpu`，这是判断"是否跨 CPU 迁移"的关键字段。
- 第 4 行 ctxt switches 拆分为 voluntary（主动让出，如等待 IO）与 nonvoluntary（被调度器抢占）两个字段，是后续判断线程是否被频繁迁移的输入。
- 第 5 行 `comm` 是线程名，将作为 §5.2 role_hint 推断的输入。

### 表 3：role_hint 推断表（原文 §5.2）

| 条件 | role_hint |
|------|-----------|
| TID 等于 PID | `main` |
| 线程名包含 `DataLoader` / `worker` | `dataloader` |
| 线程名包含 `omp` / `OpenMP` | `openmp_worker` |
| 线程名包含 `blas` / `mkl` | `blas_worker` |
| 线程名包含 `hccl` / `comm` / `communication` | `communication` |
| 其他 | `unknown` |

**逐行解读**：
- 推断顺序隐含优先级：原文表述"MVP 仅做保守推断"，未显式规定优先级，但从条件互斥性看应按表中自上而下匹配。
- `main` 通过 TID==PID 识别主线程；其余 4 类通过大小写子串匹配线程名，覆盖 PyTorch 训练常见线程类型（数据加载、OpenMP 算子、BLAS/MKL 算子、HCCL 集合通信——昇腾 NPU 分布式通信库）。
- `hccl` 标识昇腾特有的集合通信实现，这是文档专门识别 NPU 异构性的关键证据。
- 兜底值 `unknown` 体现"保守"原则：未匹配时不下结论，由下游诊断器进一步处理。

### 表 4：采集失败策略表（原文 §9）

| 失败项 | 行为 |
|--------|------|
| 目标 PID 不存在 | 退出失败。 |
| `numactl` 不存在 | 使用 `/sys`，记录 warning。 |
| `npu-smi` 不存在 | `npu_topology.devices=[]`，记录 missing。 |
| 无权限读取 environ | PyTorch env 标记 partial。 |
| 无法访问 cgroup 文件 | cgroup 标记 partial。 |
| `pidstat` 不存在 | 使用 `/proc` 采样。 |

**逐行解读**：
- 唯一硬失败项是"目标 PID 不存在"——这是采集对象本身缺失，必须终止；其余失败均采用"降级+标记"而非终止，确保 Snapshot 仍可输出。
- `numactl` 缺失降级到 `/sys/devices/system/node`（与 §5.1 linux_cpu.py 一致）；`pidstat` 缺失降级到 `/proc/stat` 与 `/proc/<pid>/task/<tid>/stat`（与 §5.6 runtime_sample.py 一致）。
- `npu-smi` 缺失时 `npu_topology.devices` 留空数组而非抛错，保证 NPU 命令不可用的环境仍能完成其他维度采集。
- `environ` 与 `cgroup` 读取失败统一标记 `partial`，与 §5.5/§5.3 的失败处理约定一致（容器中 `/sys/fs/cgroup` 访问受限是已知场景）。

---

## 【公式解读】

**原文无公式**。文档未包含任何数学公式、LaTeX 表达式或伪代码形式算法。其工作机制以"采集步骤列表""条件→输出字段映射表""采集源→Snapshot 字段映射表"等结构化文本形式表达。

唯一可视为准算法的描述是 §5.6 的 `cpu_migration_observed` 判断："同一 TID 在采样窗口中 `current_cpu` 出现多个值，即认为发生迁移"——这是集合基数判断（`|unique(current_cpu)| > 1`），但原文未以公式或伪代码形式给出。

---

## 【关联】

文档本身在文末标注"内部链接: (无)"，未给出超链接，但其文本中明确提及以下相关模块/契约，构成上下游关系：

1. **数据契约：`snapshot-schema.md`**：所有采集模块的输出字段（`system.*`、`cpu_topology.*`、`numa_topology.*`、`processes[*]`、`threads[*]`、`cgroup.*`、`npu_topology.*`、`runtime_sample.*`）均以"符合 snapshot-schema.md 的 JSON"为最终形态，collector 是 schema 的"生产者"。

2. **已实现的离线原型：`scripts/topology_collect.py`**：用于先验证拓扑采集解析的数据契约，输出 `out/topology.json`，对应 `collect-topology` 子命令。
   关联命令：
   ```bash
   python scripts/topology_collect.py --out out/topology.json
   ```

3. **已实现的离线原型：`scripts/process_discovery.py`**：用于验证进程发现的数据契约，输出 `out/processes.json`，对应 `discover-processes` 子命令。
   关联命令：
   ```bash
   python scripts/process_discovery.py --out out/processes.json
   ```

4. **CLI 调度器：`scripts/cli.py`**：承载所有子命令（`collect-topology`、`discover-processes`、`collect`），是采集器对用户的统一入口。完整 Snapshot collector 入口 `python scripts/cli.py collect ...` 与离线原型共用同一调度器。

5. **下游消费者（Agent 规则）**：§10 验收标准第 6 条明确 Agent 能基于 Snapshot 输出触发至少 4 类规则——"进程未绑核""跨 NUMA 运行""PyTorch 线程池过载""cgroup/cpuset 冲突"。这是 collector 与诊断/优化模块之间的契约：collector 只负责证据采集，决策与告警由 Agent 完成。

6. **上游/伴生模块（隐含）**：文档提到 `mindstudio-cpu-binding/collector/adapters/{linux_cpu,linux_proc,linux_cgroup,npu_topology,runtime_env}.py` 与未在 §5 中展开的 `runtime_sample.py`（§5.6），构成完整 collector 的实现清单；当前阶段这些 adapter 是设计态而非实现态。

7. **昇腾生态依赖**：`npu-smi info`、`npu-smi info -t topo`、`hccl` 线程名匹配，指向昇腾 NPU 平台的运行时命令与集合通信库，是该 collector 区别于通用 GPU 采集器的关键异构点。

---

## 【使用方法】

### 1. 仓库当前阶段可用的离线/原型入口（使用 samples/ 文本作为输入）

```bash
cd skills/mindstudio-cpu-binding
python scripts/cli.py collect-topology \
  --lscpu-file samples/lscpu.sample.txt \
  --npu-smi-topo-file samples/npu-smi-topo.sample.txt \
  --out out/topology.json

python scripts/cli.py discover-processes \
  --ps-file samples/ps.sample.txt \
  --npu-smi-info-file samples/npu-smi-info.sample.txt \
  --out out/processes.json
```

### 2. 真实 Linux NPU 节点上的 live 只读原型入口

```bash
cd skills/mindstudio-cpu-binding
python scripts/topology_collect.py --out out/topology.json
python scripts/process_discovery.py --out out/processes.json
```

### 3. 完整 Snapshot collector 入口（设计态，当前仓库尚未实现完整 `collector/collect.py`）

```bash
cd skills/mindstudio-cpu-binding
python scripts/cli.py collect \
  --pid 12345 \
  --scenario training \
  --framework pytorch \
  --device-type npu \
  --optimization-goal throughput \
  --rank-map rank0=12345:npu0,rank1=12346:npu1 \
  --sample-seconds 10 \
  --out out/snapshot.json
```

可选：`--raw-dir <dir>` 指定原始命令输出目录；用户可通过 `--rank-map` 或外部映射文件提供 NPU rank→设备映射（如 `npu-smi info` 不可用时）。

### 4. 用户补充 PyTorch 配置（通过 CLI 参数，非从 /proc 读取）

```bash
--torch-num-threads 16
--torch-num-interop-threads 2
--dataloader-workers 8
--dataloader-pin-memory true
--dataloader-prefetch-factor 2
```

### 5. NPU 拓扑用户映射文件格式（用于 `npu-smi` 不可用场景）

```json
{
  "vendor": "ascend",
  "devices": [
    {
      "device_id": "0",
      "pci_bus_id": "0000:81:00.0",
      "numa_node": 0,
      "local_cpus": "0-31,64-95"
    }
  ]
}
```

### 6. 启用前置条件
- **不需要 root**（原文 §4、§10 验收标准第 4 条）。
- 缺权限时通过 `availability.errors` 标记，不阻断采集。
- 外部命令（`lscpu`、`numactl`、`npu-smi`、`pidstat`、`mpstat`）可缺失，缺失时会按 §9 表降级到 `/proc`、`/sys` 文件。
- 用户提供的 NPU 映射文件或 `--rank-map` 在 NPU 命令不可用时为必需输入。
