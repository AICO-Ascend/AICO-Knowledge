# 1. 概述

> 仓 `ascend-deployer` · 路径 `docs/feature/openclaw一体机扩容功能.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascend-deployer/docs/feature/openclaw一体机扩容功能.md

# Ascend-Deployer「OpenClaw 一体机扩容功能」Feature 文档深度解读

---

## 【定位】

这篇文档描述 **Ascend-Deployer 工具中 OpenClaw（MindClaw 推理服务集群）在线扩容（Scale Out）能力的设计方案**——通过复用既有 `--install=openclaw` 命令入口、引入 `SCALE` 变量与磁盘空间预检机制，实现集群实例数的动态扩增，降低多节点 Docker 手动扩容的运维成本。

---

## 【技术要点】

1. **命令入口复用 + SCALE 变量分流**：不新增 CLI 参数，复用 `--install=openclaw` 入口；通过 `inventory_file` 中的 `SCALE="true"` 触发扩容，`install_openclaw.yml` 内通过 `when: scale | bool` 在安装路径与扩容路径之间分流。`SCALE` 默认 `false`，对既有流程零影响。
2. **配置持久化（mindclaw.json）**：扩容所需参数**仅从**部署时持久化的 `~/.ascend_deployer/openclaw-config/mindclaw.json` 读取（`openclaw_scale_count` 除外），关键参数缺失即终止操作，从源头保证扩容实例与已有实例的配置一致性；扩容成功后自动回写 `openclaw_instance_count`。
3. **磁盘空间预检**：在 `process_check.yml` 的 `check_for_install` 中调用 `check_disk_space_for_scale()`，根据当前已用与新增实例所需空间计算可扩容上限，不足时通过 `check_result.fail_flag` 阻止扩容。
4. **多节点批量扩容**：依托既有 Ansible `hosts_name`（worker 组）机制，扩容任务在每个 worker 节点上独立执行，无需逐台 SSH。
5. **二阶段架构 + 跳过开关**：预检阶段（`process_check.yml`，可通过 `--skip-check` 跳过，集中完成参数校验与磁盘检查）与执行阶段（`install_openclaw.yml`，不可跳过，仅含执行任务）严格分离，所有 check 逻辑集中在预检阶段。
6. **is_scale 类型安全解析**：`OpenClawCheck.__init__` 采用三段兼容（bool / str / 兜底 `bool()`），应对不同 Ansible 版本对 playbook bool 的自动转换差异。

---

## 【关键机制与数据】

### 1. 工作原理（两阶段流水线）

- **入口解析（CLI 层）**：`start_deploy.py` 调用 `_check_scale_from_inventory()` 读取 `inventory_file` 中的 `SCALE` 变量，将其以**字符串 `"true"` / `"false"`** 形式写入 `is_scale` 环境变量，再调用 `jobs.process_install`。
- **预检阶段（`process_check.yml`，可 `--skip-check` 跳过）**：`check_for_install` 模块接收 `is_scale` → `OpenClawCheck.__init__` 做类型安全解析 → 调用 `_load_mindclaw_config_for_scale()` 加载 `mindclaw.json` → 进入 `_check_scale_phase()` 完成全面参数校验与 `check_disk_space_for_scale()` 磁盘预检；校验失败通过 `check_result.fail_flag` 阻断后续流程。
- **执行阶段（`install_openclaw.yml`，不可跳过）**：根据 Ansible 自动解析的 `scale` 变量（来自 `inventory_file` 中的 `SCALE`），由 `when: scale | bool` 分流：
  - `scale=false` → load image → launch cluster（既有安装路径）
  - `scale=true` → 走扩容路径：`_load_config(exclude=["openclaw_instance_count"])` 加载 → `_build_deploy_cmd(action="scale")` 构建命令 → 执行 `deploy.sh scale` → `_save_scale_config()` 更新 `instance_count`。

> 原文：「所有校验逻辑集中在 `process_check.yml`」，`install_openclaw.yml` 只负责执行，不包含任何 check 任务；`--skip-check` 跳过全部校验（含参数校验和磁盘检查）直接进入执行。

### 2. 数据流（端到端路径）

```
用户命令行 (--install=openclaw, inventory_file: SCALE="true", openclaw_scale_count=2)
    ↓
start_deploy.py  (_check_scale_from_inventory → 设置 is_scale='true' 环境变量 → jobs.process_install)
    ↓
process_check.yml (check_for_install → OpenClawCheck → _load_mindclaw_config_for_scale → _check_scale_phase → check_disk_space_for_scale)
    ↓           [校验失败 → check_result.fail_flag 阻止]
install_openclaw.yml (when: scale | bool → 命中 "scale openclaw cluster" task)
    ↓
install_openclaw.py (action="scale": _load_config → _ensure_mindclaw_scripts → _build_deploy_cmd → deploy.sh scale → _save_scale_config)
    ↓
mindclaw/scripts/deploy.sh (scale 动作：执行实例扩容逻辑，输出实例：openclaw-3、openclaw-4 ...)
```

### 3. 性能数据

- **原文无性能基准数据**（无 IOPS、时延、并发量等量化指标）。文档只提到扩容输出示例："输出实例：openclaw-3、openclaw-4 ..."。

---

## 【表格解读】

### 表 1：现有功能局限（Section 1.2）

| 场景 | 现状 | 差距 |
| ---- | ---- | ---- |
| 安装部署 | 支持 `--install=openclaw` | ✓ |
| 升级 | 支持 `--upgrade=openclaw`（镜像升级或批量配置更新） | ✓ |
| 扩容 | 不支持 | 需手动操作 Docker，运维成本高 |

**解读**：现状对比表揭示了 Ascend-Deployer 在 OpenClaw 集群生命周期管理上的能力缺口——安装与升级已具备工具化能力，唯独扩容仍依赖手工操作 Docker；本提案正是为了填补"扩容"这一行的 ✓，把 Docker 命令的运维成本交还给工具。

---

### 表 2：核心设计策略（Section 2.1）

| 适配点 | 现有逻辑 | 扩容逻辑 | 适配方式 |
| ---- | ---- | ---- | ---- |
| 命令入口 | `--install=openclaw` 执行安装 | 复用入口，`SCALE="true"` 时执行扩容 | 入口复用 |
| 流程分流 | playbook 直接执行 install+launch | `install_openclaw.yml` 通过 `when: scale \| bool` 分流安装/扩容 | 条件分流 |
| 参数校验与磁盘检查 | `process_check.yml` → `check_for_install` | 复用同一入口，`is_scale` 触发扩容专用校验路径 | 预检扩展 |
| 参数来源 | 仅 `inventory_file` | 仅 `mindclaw.json`，`openclaw_scale_count` 例外 | 配置持久化 |
| 多节点执行 | Ansible hosts 机制 | 每节点独立执行扩容 | hosts 复用 |

**解读**：该表是设计方案的"路线图"，五行对应五个改造点，全部采用"复用而非新建"的策略——复用命令入口、复用 playbook 入口、复用预检入口、复用 hosts 机制，唯一新增的是"配置持久化"（`mindclaw.json`）作为扩容参数的单一可信源，体现了"小改动、高复用、低风险"的设计哲学。`openclaw_scale_count` 是表中唯一不来自 `mindclaw.json` 的参数，因为它正是用户本次扩容操作要设定的输入。

---

### 表 3：SCALE 变量流转路径（Section 2.3.1）

| 阶段 | 变量来源 | 作用 |
| ---- | ---- | ---- |
| CLI 解析 | `_check_scale_from_inventory()` 读取 inventory_file | 设置 `is_scale` 环境变量（字符串 `"true"` / `"false"`） |
| 预检 (process_check) | `is_scale` 通过 playbook 传入 `check_for_install` 模块 | `OpenClawCheck.__init__` 做类型安全解析（兼容 bool/str/int → bool） |
| Playbook 分流 | Ansible 自动解析 inventory_file 中的 `SCALE` | `when: scale \| bool` 分流任务 |
| 执行 (scale) | `_load_config(exclude=["openclaw_instance_count"])` 读 mindclaw.json | 获取扩容参数 |

**解读**：这是 SCALE 变量从配置到执行的"全链路追踪表"。注意 CLI 层以**字符串**发出 `is_scale`，但在预检层由 `OpenClawCheck.__init__` 做三段兼容解析（bool/str/兜底），原因是不同 Ansible 版本对 playbook 内的 bool 值会做不同形式的自动类型转换；Playbook 分流层则由 Ansible 直接消费 inventory 中的 `SCALE` 并解析为 `bool`，故使用 `when: scale | bool`；执行层的参数则来自 `mindclaw.json` 而非 `SCALE` 本身，体现了"控制信号"与"业务参数"分离的设计。

---

### 表 4：持久化参数列表（Section 2.3.2，**原文此表被截断**）

| 参数 | 说明 |
| ---- | ---- |
| （原文未列出） | （原文未列出） |

**解读**：原文在 Section 2.3.2「持久化参数列表」处表格仅有表头 `| 参数 | 说明 |` 与分隔行 `----`，数据行**原文未列出**（文档在此处被截断）。从上下文可推断：此表本应列出 launch 时写入 `~/.ascend_deployer/openclaw-config/mindclaw.json` 的所有 OpenClaw 相关参数（如 `openclaw_base_port`、`openclaw_model_name`、`openclaw_infer_url`、`openclaw_image_name`、`openclaw_image_file`、`openclaw_model_provider`、`openclaw_instance_prefix`、`openclaw_api_key`、`openclaw_subnet`、`openclaw_gateway_token`、`openclaw_config_dir` 等——这些参数在扩容路径的 YAML task 中均以 `| default('', true)` 出现，强烈暗示它们都来自 `mindclaw.json`），但因原文截断不能据此声称具体条目。

---

## 【公式解读】

### 公式 1：`is_scale` 类型安全解析（Section 2.3.1，Python 伪代码）

```python
if isinstance(is_scale_param, bool):
    self.is_scale = is_scale_param          # Ansible 做了 bool 转换
elif isinstance(is_scale_param, str):
    self.is_scale = is_scale_param.lower() == 'true'  # 原始字符串
else:
    self.is_scale = bool(is_scale_param) if is_scale_param else False  # 兜底
```

**符号与作用解读**：

- `is_scale_param`：从 playbook 传入的参数实际值，可能是 `bool`、`str`、`int` 或 `None`（不同 Ansible 版本对 inventory bool 的自动转换结果不同）。
- `self.is_scale`：标准化后的目标布尔属性，后续 `_check_scale_phase()` 据此分流。
- 第一分支 `isinstance(is_scale_param, bool)`：若 Ansible 已自动转为 `True` / `False`，原样使用，**避免对 bool 调用 `.lower()` 抛错**。
- 第二分支 `isinstance(is_scale_param, str)`：CLI 层以字符串 `"true"` / `"false"` 发出，`.lower() == 'true'` 实现大小写无关的精确比对。
- 第三分支（兜底）：`bool(is_scale_param) if is_scale_param else False` 对 `None`、`0`、`""` 等异常输入返回 `False`，避免对 `None` 调用 `bool(None)` 后产生 `False` 之外的歧义值；同时 `if is_scale_param` 先做存在性检查，确保只有真值才调用 `bool()`。
- **设计意图**：原文说明"同理处理 `is_upgrade` 和 `do_batch_config_update`"，即该三元兼容模式被复用到其他布尔开关变量。

---

### 公式 2：Playbook 执行分流（Section 2.3.1，YAML）

```yaml
- hosts: '{{ hosts_name }}'           # worker 组
  name: install or scale openclaw cluster
  gather_facts: true
  tasks:
    # 正常安装（scale=false）
    - name: load openclaw image
      install_openclaw:
        action: "install"
        resources_dir: "{{ resources_dir }}"
        openclaw_image_name: "{{ openclaw_image_name | default('') }}"
        openclaw_image_file: "{{ openclaw_image_file | default('') }}"
      when: not (scale | default(false) | bool)

    - name: launch openclaw cluster
      install_openclaw:
        action: "launch"
        ...
        openclaw_model_provider: "{{ openclaw_model_provider | default('local') }}"
        openclaw_instance_prefix: "{{ openclaw_instance_prefix | default('openclaw') }}"
        openclaw_api_key: "{{ openclaw_api_key | default('') }}"
        openclaw_subnet: "{{ openclaw_subnet | default('') }}"
      environment:
        API_KEY: "{{ openclaw_api_key | default('') }}"
        SUBNET: "{{ openclaw_subnet | default('') }}"
      when: not (scale | default(false) | bool)

    # 扩容执行（scale=true）
    - name: scale openclaw cluster
      install_openclaw:
        action: "scale"
        resources_dir: "{{ resources_dir }}"
        openclaw_scale_count: "{{ openclaw_scale_count | default(0, true) | int }}"
        openclaw_config_dir: "{{ openclaw_config_dir | default('', true) }}"
        ...
        openclaw_instance_prefix: "{{ openclaw_instance_prefix | default('openclaw', true) }}"
      when: scale | default(false) | bool
```

**符号与作用解读**：

- `hosts: '{{ hosts_name }}'`：Ansible worker 组，对应现有 `inventory_file` 中定义的 worker 节点列表，扩容时每节点独立执行。
- `when: not (scale | default(false) | bool)`：安装路径的两个任务（load image、launch cluster）仅在 `scale` 为假时执行。
- `when: scale | default(false) | bool`：扩容任务仅在 `scale` 为真时执行，与安装路径**互斥**。
- `scale | default(false) | bool`：三层防御——`default(false)` 兼容 `SCALE` 未定义情形；`| bool` 兼容 Ansible 自动转换；保证 `when` 表达式始终得到标准 Python bool。
- `openclaw_scale_count: "{{ openclaw_scale_count | default(0, true) | int }}"`：扩容实例数，使用第二参数 `true` 的 `default()`（即变量未定义或为空时返回默认值 0），再 `| int` 强制整型化。
- `action: "install" / "launch" / "scale"`：动作分发字段，分别对应加载镜像、启动集群、扩容三个语义，由 `install_openclaw` Python action plugin 接收。
- `environment: { API_KEY, SUBNET }`：仅在 launch 任务中向子进程注入环境变量（`openclaw_api_key`、`openclaw_subnet` 的 Jinja2 注入），扩容与 install 任务无此环境块。
- `hostvars[inventory_hostname].openclaw_image_name | default(openclaw_image_name)`：launch 任务中优先取当前 host 的 hostvars 值，缺失则回退到组变量，适配多镜像节点场景；扩容任务则直接使用组变量。

---

### 公式 3：预检阶段的参数传递（Section 2.3.1，YAML）

```yaml
# process_check.yml 中向 check_for_install 传递的扩容相关参数：
is_scale: "{{ is_scale | default('false') }}"
is_upgrade: "{{ is_upgrade | default('false') }}"
openclaw_scale_count: "{{ openclaw_scale_count | default(0, true) | int }}"
openclaw_base_port: "{{ openclaw_base_port | default(0, true) | int }}"
openclaw_model_name: "{{ openclaw_model_name | default('', true) }}"
openclaw_infer_url: "{{ openclaw_infer_url | default('', true) }}"
openclaw_image_name: "{{ openclaw_image_name | default('', true) }}"
# ...其他 openclaw_* 参数
```

**符号与作用解读**：

- `is_scale: "{{ is_scale | default('false') }}"`：以**字符串**形式透传（与 Section 2.3.1 中"`is_scale` 从 CLI 以字符串 `"true"` / `"false"` 发出"一致），由 `OpenClawCheck.__init__` 后续做类型安全解析；默认值用**字符串** `'false'` 而非 bool `false`，与上游保持类型一致。
- `is_upgrade: "{{ is_upgrade | default('false') }}"`：同 `is_scale` 的字符串透传模式。
- `openclaw_scale_count: "{{ openclaw_scale_count | default(0, true) | int }}"`：扩容实例数缺省为 0，`default()` 第二参数 `true` 表示变量为 `undefined` 或空字符串时使用默认值，`| int` 强制整型。
- `openclaw_model_name / openclaw_infer_url / openclaw_image_name` 等均使用 `default('', true)`：以空串兜底，表示"未配置"语义，便于后续在 Python 侧判断关键参数是否缺失。
- `# ...其他 openclaw_* 参数`：原文未完整列出其余参数，从扩容路径 YAML 可推断至少还包括 `openclaw_image_file`、`openclaw_model_provider`、`openclaw_instance_prefix`、`openclaw_config_dir`、`openclaw_gateway_token` 等。
- **设计意图**：此段是预检层的"参数清单契约"——所有扩容所需的参数在此统一传递给 `check_for_install`，由其根据 `tags: ['openclaw']` 触发 `OpenClawCheck.check_openclaw()`，再按 `is_scale` / `is_upgrade` 分流到不同校验阶段；校验失败通过 `check_result.fail_flag` 阻止后续安装/扩容流程。

---

## 【关联】

本 RFC 与文中其他模块/特性的关系（基于文档描述梳理）：

1. **上游（被复用的既有能力）**
   - **`--install=openclaw` 命令入口**：扩容复用此入口，未新增 CLI 参数。
   - **`--upgrade=openclaw`（镜像升级或批量配置更新）**：现状表中的同级能力，扩容补齐后形成"安装 / 升级 / 扩容"三件套。
   - **Ansible `hosts_name` / `inventory_file` 机制**：扩容多节点批量执行依赖此机制。
   - **`process_check.yml` + `check_for_install` 预检框架**：扩容专用校验通过 `is_scale` 在该框架内分流。
   - **`install_openclaw` Ansible action plugin**：扩容通过 `action: "scale"` 调用。
   - **`mindclaw.json` 持久化机制**：扩容参数的单一可信源，由 launch 时首次写入 `~/.ascend_deployer/openclaw-config/mindclaw.json`。
   - **`mindclaw/scripts/deploy.sh`**：扩容路径的最终执行者（`deploy.sh scale`）。

2. **下游（被扩容直接影响的实例）**
   - **OpenClaw 容器实例**：扩容产出形如 `openclaw-3`、`openclaw-4 ...`（原文示例）。`openclaw_instance_prefix` 默认值为 `'openclaw'`，故新实例按数字后缀递增命名。

3. **设计上的并列/互斥关系**
   - 与 **`--upgrade=openclaw` 互斥**：`is_scale` 与 `is_upgrade` 在预检层由 `OpenClawCheck.__init__` 同模式处理（均采用三元兼容 bool/str/兜底），但语义上扩容不应与升级同时进行。
   - **`--skip-check` 跳过范围**：跳过 `process_check.yml` 中**全部**校验（参数校验 + 磁盘检查），但**不跳过** `install_openclaw.yml` 的执行。

4. **文档未给出的关联信息**
   - 与 OpenClaw **缩容（Scale In）** 功能：原文明确列为**非目标**（"本提案不涉及 OpenClaw 集群的缩容功能"），未来可能成为独立 RFC。
   - 与**跨版本扩容兼容性**：原文明确列为**非目标**（"扩容时镜像版本应与现有实例一致"），由用户在 inventory 中保证。
   - **内部链接**：原文文末标注 "(无)"，即本 RFC 文档未挂载任何内部交叉引用链接。

---

## 【使用方法】

### 启用方式（基于文档原文梳理）

**步骤 1：在 `inventory_file` 中启用扩容模式并设定扩容数量**

```ini
[all:vars]
SCALE="true"             # 触发扩容路径；省略或设为 "false" 时执行安装（向后兼容）
openclaw_scale_count=2   # 本次扩容增加的实例数
```

> 原文：「SCALE 默认为 false，不影响现有安装流程」；「`openclaw_scale_count` 例外」于"仅从 `mindclaw.json` 读取"的约束之外，作为本次扩容的输入参数。

**步骤 2：执行与安装相同的命令入口**

```bash
ascend-deployer --install=openclaw
```

> 原文："复用 `--install=openclaw` 命令入口，新增 `SCALE` 变量控制执行路径"。

**步骤 3：（可选）跳过预检**

```bash
ascend-deployer --install=openclaw --skip-check
```

> 原文："`--skip-check` 跳过 `process_check.yml` 全部校验（含参数校验和磁盘检查），直接进入 `install_openclaw.yml` 执行"。⚠️ 跳过预检意味着磁盘空间与参数一致性检查均被绕过，扩容安全性下降。

### 配置项（按文档原文梳理）

| 配置项 | 作用 | 默认值 | 来源 |
| ---- | ---- | ---- | ---- |
| `SCALE` | 扩容开关；`"true"` 触发扩容，`"false"` 触发安装 | `"false"`（向后兼容） | inventory_file |
| `openclaw_scale_count` | 本次扩容增加的实例数 | `0` | inventory_file |
| `is_scale`（内部环境变量） | 由 `start_deploy.py` 从 `SCALE` 转换而来，字符串 `"true"` / `"false"` | — | 环境变量 |
| `mindclaw.json` 中的 `openclaw_instance_count` | 扩容成功后自动更新 | — | `~/.ascend_deployer/openclaw-config/mindclaw.json` |
| `openclaw_*` 其余参数（如 `openclaw_base_port`、`openclaw_model_name`、`openclaw_infer_url`、`openclaw_image_name`、`openclaw_model_provider`、`openclaw_instance_prefix` 等） | 扩容时仅从 `mindclaw.json` 读取，用于保证参数一致性 | 各参数默认值（如 `openclaw_model_provider='local'`、`openclaw_instance_prefix='openclaw'`） | `mindclaw.json` |

### 命令（原文涉及的关键命令/调用链）

- **CLI 入口**：`--install=openclaw`
- **预检模块**：`check_for_install`（含 `OpenClawCheck.check_openclaw()` → `_check_scale_phase()` → `check_disk_space_for_scale()`）
- **执行任务**：`install_openclaw.yml` 中 `install_openclaw` action plugin，调用 `action: "scale"`
- **部署脚本**：`deploy.sh scale`（产出实例 `openclaw-3`、`openclaw-4 ...`）

### 未涉及的内容

- 原文**未涉及**：具体的磁盘空间计算公式（如每实例所需 GB 数、可用阈值比例）、`mindclaw.json` 中各参数的具体持久化字段清单（Section 2.3.2 持久化参数表在原文中被截断，仅有表头）、`check_disk_space_for_scale()` 的内部实现细节、扩容失败的回滚机制、扩容过程的进度输出格式与日志规范、具体的 Ansible playbook 文件路径与 Python 模块文件路径（文档以代码片段形式给出逻辑，但未标注仓库内的具体文件位置）。
- 原文**未涉及**：缩容（Scale In）的对应操作命令、跨版本扩容的兼容性处理、指定实例 ID 扩容等实例级精细化操作。
