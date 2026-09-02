# MVP 采集器设计

> 仓 `msagent` · 路径 `skills/profiler/mindstudio-cpu-binding/docs/collector-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msagent/skills/profiler/mindstudio-cpu-binding/docs/collector-design.md

# 深度解读：`skills/profiler/mindstudio-cpu-binding/docs/collector-design.md`

## 【定位】
本文档定义 **msagent 中 "MindStudio 智能体 — CPU 绑核分析" 模块下的 MVP Snapshot 采集器** 的设计契约：它以**只读、低侵入、可追溯**为目标，在目标 NPU 主机上采集 CPU/NUMA/SMT 拓扑、进程/线程亲和度、cgroup 限制、NPU 拓扑、PyTorch 运行时环境与运行时采样，并输出符合 `snapshot-schema.md` 的 JSON 证据，供上游 Agent 触发绑核诊断规则——**采集器本身不做诊断、不修改系统、不自动优化**。

---

## 【技术要点】

1. **三大约束**：默认只读、不要求 root、禁止依赖 ftrace/eBPF/perf；缺失权限或外部命令时降级到 `/proc` 与 `/sys` 文件，并把失败信息写入 `availability.errors / availability.missing`，保证 Snapshot 始终可用（除非目标 PID 不存在）。
2. **目录与入口**：完整设计目标形态为 `collector/collect.py` + `adapters/{linux_cpu, linux_proc, linux_cgroup, npu_topology, runtime_env}.py`；当前阶段已落地的两个只读原型是 `scripts/topology_collect.py` 与 `scripts/process_discovery.py`，由 `scripts/cli.py` 统一暴露 `collect-topology` / `discover-processes` / `collect` 三个子命令。
3. **采样运行时参数**：`--sample-seconds` 默认 **10** 秒，`--pid` 可重复以覆盖多 PID rank；`--rank-map` 形如 `rank0=12345:npu0,rank1=12346:npu1`，用于把 rank/PID/NPU 三元组建立映射；`--optimization-goal` 取值四档 `throughput / latency / stability / isolation`，`--framework` MVP 默认 `pytorch`，`--device-type` MVP 默认 `npu`。
4. **NUMA 与 NPU 拓扑采集策略**：`lscpu`、`lscpu -e=...`、`numactl -H` 为主，`/sys/devices/system/cpu/cpu*/topology/*` 与 `/sys/devices/system/node/node*/cpulist|meminfo` 为备；NPU 拓扑支持三种方式 —— 平台命令（`npu-smi info` / `npu-smi info -t topo`）、用户 JSON 映射文件、CLI `--rank-map`；`numactl` 缺失时降级到 `/sys`，`npu-smi` 缺失时 `npu_topology.devices=[]` 并记 missing，**绝不猜测 NUMA**。
5. **进程/线程亲和度与 role_hint 推断**：从 `/proc/<pid>/status` 的 `Cpus_allowed_list / Mems_allowed_list` 读亲和集，从 `/proc/<tid>/stat` 的 `processor` 读 `current_cpu`，从 `/proc/<tid>/status` 读 voluntary / nonvoluntary ctxt switches；线程角色按"保守匹配"规则推断 —— TID==PID → `main`、名含 `DataLoader/worker` → `dataloader`、含 `omp/OpenMP` → `openmp_worker`、含 `blas/mkl` → `blas_worker`、含 `hccl/comm/communication` → `communication`，其余 `unknown`。
6. **cgroup v1/v2 双兼容**：从 `/proc/<pid>/cgroup` 入手，分别读 `cpuset.cpus(.effective)` / `cpuset.mems(.effective)` / `cpu.max` (v2) / `cpu.cfs_quota_us` / `cpu.cfs_period_us` / `cpu.stat` (v1) / `cpuacct.usage`；v1/v2 字段不一致时"只填可用字段"，容器里访问不到 `/sys/fs/cgroup` 全部子目录则记 partial。
7. **运行时低侵入采样与迁移判定**：`pidstat -t -p <pid> 1 <seconds>` + `mpstat -P ALL 1 <seconds>` 为主，`/proc/stat` 与 `/proc/<pid>/task/<tid>/stat` 为备；`cpu_migration_observed` 的判定简单到——同一 TID 在采样窗口内 `current_cpu` 出现多个不同值即认为发生迁移。
8. **安全边界硬约束**：禁止写 `/proc`、`/sys`、`/sys/fs/cgroup`；禁止执行 `taskset -cp`、`numactl` 启动、修改 env 重启进程、修改 K8s/Docker/Slurm 配置、使用 ftrace/eBPF/perf、向外发送数据；外部 `environ` 读不到时 PyTorch env 标记 partial**而不是**伪造。
9. **可追溯性**：所有外部命令与 `/proc` 原始输出落盘到 `raw_refs`（示例目录 `snapshot-output/raw/`），含 `lscpu.txt`、`lscpu-e.txt`、`numactl-H.txt`、`proc-12345-status.txt`、`proc-12345-task/<tid>-*`、`cgroup-12345.txt`、`npu-topology.txt`、`pidstat.txt`、`mpstat.txt`，便于事后回溯与差异对比。

---

## 【关键机制与数据】

### 工作原理（10 步流水线）
原文第 6 节明确给出 Snapshot 生成流程：
> `1. 解析 CLI 参数 → 2. 初始化 collection 和 workload → 3. 采集 system / cpu_topology / numa_topology → 4. 采集 npu_topology → 5. 采集 processes / threads → 6. 采集 cgroup → 7. 采集 pytorch env → 8. 运行 runtime sample → 9. 汇总 availability.missing / errors / warnings → 10. 写出 snapshot.json 和 raw_refs`

### 数据流
```
CLI 参数 (pid / scenario / framework / device-type / optimization-goal / rank-map / sample-seconds)
        │
        ▼
  Adapters (linux_cpu → linux_proc → linux_cgroup → npu_topology → runtime_env → runtime_sample)
        │            │
        │            └─ 原始命令输出 → raw/<name>.txt (raw_refs)
        ▼
  Snapshot JSON (符合 snapshot-schema.md)
        │
        ▼
  Agent 层（触发绑核诊断规则：未绑核 / 跨 NUMA / PyTorch 线程池过载 / cgroup-cpuset 冲突）
```

### 性能/规模数据
- 单次采样时长：`--sample-seconds` 默认 **10 秒**（原文：第 3 节"运行期采样时长，默认 10 秒"）。
- 迁移检测窗口 = 采样窗口，**同一 TID 在窗口内出现 ≥2 个不同 `current_cpu`** 即判定迁移（原文：第 5.6 节）。
- 线程池规模只能由外部用户/启动脚本/应用内探针补：`--torch-num-threads 16`、`--torch-num-interop-threads 2`、`--dataloader-workers 8`、`--dataloader-pin-memory true`、`--dataloader-prefetch-factor 2`（原文：第 5.5 节"用户补充信息"）。

> 注：原文中没有给出 CPU/内存开销、采样精度等量化性能数字；不臆造。

---

## 【表格解读】

### 表 A — CLI 参数表（第 3 节）

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

**逐行解读：**
- `--pid`（**必填、可重复**）：是整个采集的锚点；多 PID 直接对应多 rank 场景（如 DDP 训练），可重复以覆盖 `--rank-map` 中的全部 rank PID。
- `--scenario`：枚举三态，决定 Agent 后续判定的优化目标权重（吞吐 vs 时延 vs 不确定）。
- `--framework` / `--device-type`：MVP **写死默认** `pytorch` 与 `npu`，意味着第一版只服务 Ascend NPU + PyTorch 组合；其它框架/设备类型需扩展 adapter 而非修改 Agent 层。
- `--optimization-goal`：四档枚举 `throughput / latency / stability / isolation`，是 Agent 端规则触发顺序与严重度排序的依据。
- `--rank-map`：以 `rank0=PID:npuX` 串接的紧凑格式，**覆盖** `--pid` 单纯采样的不足；用于打通 `rank ↔ process ↔ device` 三元映射。
- `--sample-seconds`：默认 **10** 秒，影响 `runtime_sample.*` 与 `cpu_migration_observed` 的统计窗口。
- `--output`（**必填**）：Snapshot JSON 落盘路径。
- `--raw-dir`（可选）：指定 `raw_refs` 落盘目录，与 `--output` 解耦，便于把原始证据独立归档。

> 注：原文 CLI 参数表里写的是 `--output`，但第 3 节顶部示例命令中使用的是 `--out`，表格与示例存在命名差异——这里**逐字还原原文表格**，未做合并修正。

---

### 表 B — `/proc` 字段到 Snapshot 字段映射（第 5.2 节）

| 来源 | Snapshot 字段 |
|------|---------------|
| `/proc/<pid>/status` `Cpus_allowed_list` | `processes[*].cpus_allowed_list` |
| `/proc/<pid>/status` `Mems_allowed_list` | `processes[*].mems_allowed_list` |
| `/proc/<tid>/stat` processor | `threads[*].current_cpu` |
| `/proc/<tid>/status` ctxt switches | `threads[*].voluntary_ctxt_switches` / `nonvoluntary_ctxt_switches` |
| `/proc/<tid>/comm` | `threads[*].name` |

**逐行解读：**
- `Cpus_allowed_list` → `cpus_allowed_list`：进程级 CPU 亲和集，是判断"是否绑核"的核心证据。
- `Mems_allowed_list` → `mems_allowed_list`：进程级 NUMA 亲和集，是判断"是否跨 NUMA"的核心证据。
- `/proc/<tid>/stat` 的 `processor` → `threads[*].current_cpu`：线程当前真实运行在哪个 CPU，是**实际亲和度**而非"声明"亲和度。
- `ctxt switches` → `voluntary_ctxt_switches` / `nonvoluntary_ctxt_switches`：自愿 vs 抢占切换，配合 `current_cpu` 变化可用于评估调度抖动。
- `/proc/<tid>/comm` → `threads[*].name`：线程名，作为 `role_hint` 推断的输入。

---

### 表 C — `role_hint` 推断规则（第 5.2 节）

| 条件 | role_hint |
|------|-----------|
| TID 等于 PID | `main` |
| 线程名包含 `DataLoader` / `worker` | `dataloader` |
| 线程名包含 `omp` / `OpenMP` | `openmp_worker` |
| 线程名包含 `blas` / `mkl` | `blas_worker` |
| 线程名包含 `hccl` / `comm` / `communication` | `communication` |
| 其他 | `unknown` |

**逐行解读：**
- TID==PID ⇒ `main`：主线程 sentinel，不依赖名称匹配，最稳健。
- `DataLoader` / `worker` ⇒ `dataloader`：覆盖 PyTorch `DataLoader` 及其 `DataLoader worker` 命名约定。
- `omp` / `OpenMP` ⇒ `openmp_worker`：识别 PyTorch 内部或外部 OpenMP 线程池（如 `OMP_NUM_THREADS` 控制的并行区）。
- `blas` / `mkl` ⇒ `blas_worker`：识别底层线性代数库线程池（与上条互斥，但同一线程也可能同名前缀）。
- `hccl` / `comm` / `communication` ⇒ `communication`：识别集合通信线程（NPU 场景下与 `hccl` 强相关）。
- 其余 ⇒ `unknown`：**保守兜底**，绝不臆造。

> 设计哲学：表 C 是**纯静态 / 无副作用**推断；任意匹配不到的线程一律 `unknown`，由 Agent 端基于 `unknown` + `current_cpu`/`cpus_allowed_list` 自行决定后续策略。

---

## 【公式解读】

原文无公式。

（本文档全部为接口契约、命令清单与字段映射，没有数学公式或 LaTeX 表达式；亦无伪代码形式的状态转移/判定公式可逐字引用。）

---

## 【关联】

> 原文内部链接：用户标注 **(无)**。以下"关联"基于文档中显式提及的模块名/路径，属原文证据，不是外部臆测。

### 上游契约
- **`snapshot-schema.md`**（原文第 1 节）：本采集器输出必须符合该 Schema；所有 adapter 的"输出字段"小节（`system.*`、`cpu_topology.*`、`numa_topology.*`、`processes[*]`、`threads[*]`、`cgroup.*`、`npu_topology.*`、`runtime_sample.*`）都是对该 Schema 的字段子集承诺。

### 上下游原型（已实现部分）
- **`scripts/topology_collect.py`**（原文第 1、2 节）：已实现的拓扑采集原型，独立入口验证 live 输出。
- **`scripts/process_discovery.py`**（原文第 1、2 节）：已实现的进程发现原型，与 `topology_collect.py` 共同验证"数据契约"。
- **`scripts/cli.py`**（原文第 2、3 节）：统一 CLI 入口，提供 `collect-topology` / `discover-processes` / `collect` 三个子命令。

### 未来完整形态（设计目标）
- **`collector/collect.py`** + **`collector/adapters/*.py`**（原文第 2 节）：完整 Snapshot collector 应复用 `scripts/topology_collect.py` 与 `scripts/process_discovery.py` 的 parser 与输出结构。

### 下游消费方
- **Agent 层**（原文第 5.4 节"不应在 Agent 层硬编码"、第 10 节第 6 条）：基于本 Snapshot 触发至少 4 条规则 —— 进程未绑核、跨 NUMA 运行、PyTorch 线程池过载、cgroup/cpuset 冲突；NPU 平台相关命令适配放在 adapter，**不耦合到 Agent**。

### 外部可识别环境变量清单（第 5.5 节）
与分布式训练/线程池相关的可识别 env：`LOCAL_RANK`、`RANK`、`WORLD_SIZE`、`MASTER_ADDR`、`MASTER_PORT`、`OMP_NUM_THREADS`、`MKL_NUM_THREADS`、`OPENBLAS_NUM_THREADS`、`GOTO_NUM_THREADS`、`KMP_AFFINITY`、`KMP_BLOCKTIME`、`ASCEND_VISIBLE_DEVICES`、`CUDA_VISIBLE_DEVICES` —— 这些是 Agent 端判断 PyTorch/HCCL/OpenMP/MKL 线程池配置冲突的依据。

---

## 【使用方法】

> 以下命令与配置项均来自原文第 2、3、5.4、5.5 节。

### 1. 离线示例验证（使用仓库自带 `samples/*.txt`，无需真实 NPU 节点）
```bash
cd skills/mindstudio-cpu-binding
python scripts/cli.py collect-topology --lscpu-file samples/lscpu.sample.txt --npu-smi-topo-file samples/npu-smi-topo.sample.txt --out out/topology.json
python scripts/cli.py discover-processes --ps-file samples/ps.sample.txt --npu-smi-info-file samples/npu-smi-info.sample.txt --out out/processes.json
```

### 2. Live 只读原型入口（真实 Linux NPU 节点）
```bash
cd skills/mindstudio-cpu-binding
python scripts/topology_collect.py --out out/topology.json
python scripts/process_discovery.py --out out/processes.json
```

### 3. 完整 Snapshot 采集（设计目标 CLI）
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

### 4. 用户手动提供 NPU 映射文件格式（第 5.4 节）
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

### 5. 用户补充 PyTorch 线程池/数据加载器配置（第 5.5 节）
```bash
--torch-num-threads 16
--torch-num-interop-threads 2
--dataloader-workers 8
--dataloader-pin-memory true
--dataloader-prefetch-factor 2
```

### 6. 输出目录建议（第 7 节）
```
snapshot-output/
├── snapshot.json
└── raw/
    ├── lscpu.txt
    ├── lscpu-e.txt
    ├── numactl-H.txt
    ├── proc-12345-status.txt
    ├── proc-12345-cmdline.txt
    ├── proc-12345-task/
    │   ├── 12345-status.txt
    │   ├── 12345-stat.txt
    │   └── 12345-comm.txt
    ├── cgroup-12345.txt
    ├── npu-topology.txt
    ├── pidstat.txt
    └── mpstat.txt
```

### 7. 启用要点 / 注意事项（综合自第 4、8 节"采集原则"与"安全边界"）
- 无需 root；缺权限时由 adapter 自动降级到 `/proc` / `/sys`，并在 `availability.errors` 中记录。
- 不要把采集器运行在会触发 `taskset -cp` / `numactl` 启动 / 写 cgroup / 写 sysctl 的环境中——本采集器**只读**，对这些动作零容忍。
- 若需自定义 NPU 平台命令，应新增 adapter 而**非**在 Agent 层硬编码命令字符串。
