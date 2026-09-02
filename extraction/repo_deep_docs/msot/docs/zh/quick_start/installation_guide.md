# 昇腾 AI 算子开发工具链学习环境安装指南

> 仓 `msot` · 路径 `docs/zh/quick_start/installation_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/zh/quick_start/installation_guide.md

# 深度解读：昇腾 AI 算子开发工具链学习环境安装指南

## 【定位】

本指南系统性地解决"如何在一台配备昇腾 NPU 的 Linux 服务器上，从零搭建可用于学习算子开发工具链（CANN）的容器化环境"这一问题，覆盖从芯片识别、镜像拉取、容器启动、示例代码克隆到 SoC 型号注册与自检的全链路部署流程。

---

## 【技术要点】

1. **芯片-镜像自动映射机制**：通过 `lspci -n -D` 读取 NPU 的 PCI Device ID，将设备 ID 与 CANN 官方镜像一一绑定——`d500→310P`、`d802→910B`、`d803→A3`，匹配结果写入环境变量 `MY_STUDY_VAR_CANN_IMAGE` 与 `MY_CHIP_NAME`，避免手工选择出错。

2. **CANN 镜像格式与版本固定**：所有镜像统一为 `cann:9.0.0-{chip}-openeuler24.03-py3.11-devel`（CANN 9.0.0，操作系统 openEuler 24.03，Python 3.11，devel 变体），由华为云 AscendHub 托管（地址：`swr.cn-south-1.myhuaweicloud.com/ascendhub/cann`）。

3. **强容器化约束**：文档明确声明"仅支持容器化部署"，不支持裸机/虚拟机等非容器环境，因为算子编译环境依赖复杂。

4. **SoC 型号运行时探测**：在容器内通过 Python 调用 CANN ACL 接口 `acl.get_soc_name()` 动态获取 SoC 名称，并去除 `Ascend` 前缀后存入 `MY_STUDY_VAR_CHIP_SOC_TYPE`，写入 `/etc/profile.d/custom-env.sh` 实现持久化。

5. **环境变量作用域隔离**：宿主机使用 `MY_STUDY_VAR_CANN_IMAGE`/`MY_CHIP_NAME`（仅当次拉取/启动用），容器内使用 `MY_STUDY_VAR_CHIP_SOC_TYPE`（供后续算子编译引用），文档明确警告这两套变量"仅适用于本快速入门教程，请勿在商业开发中使用"。

6. **三级内网降级方案**：公网→Docker HTTP 代理（修改 `/etc/systemd/system/docker.service.d/http-proxy.conf` 并 `systemctl daemon-reload && systemctl restart docker`）→离线 `docker save/load` 跨机搬运 `cann.tar`，逐级覆盖不同隔离级别的环境。

---

## 【关键机制与数据】

### 工作原理与数据流

**完整数据流**（原文 §1–§6）：

```
┌────────────────────────────────────────────────────────────────┐
│ 宿主机侧 (Host)                                                │
│  ① lspci -n -D 解析 PCI ID ──→ dev_id (d500/d802/d803)        │
│  ② case 匹配 ──→ 写入 MY_STUDY_VAR_CANN_IMAGE + MY_CHIP_NAME   │
│  ③ docker pull ${MY_STUDY_VAR_CANN_IMAGE}                     │
│  ④ curl -fLO ctr_in.py && chmod +x                            │
│  ⑤ ~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}  → 启动容器         │
└────────────────────────┬───────────────────────────────────────┘
                         │ docker exec / docker cp 边界
┌────────────────────────▼───────────────────────────────────────┐
│ 容器内 (Container)                                              │
│  ⑥ git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot│
│  ⑦ acl.get_soc_name() 去除 "Ascend" 前缀                       │
│     ──→ 写入 /etc/profile.d/custom-env.sh                      │
│     ──→ export MY_STUDY_VAR_CHIP_SOC_TYPE                      │
│  ⑧ 自检 [ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] &&                │
│     [ -d ~/ot_demo/msot/example/quick_start ]                   │
└────────────────────────────────────────────────────────────────┘
```

**关键数据点**（原文 §1–§3）：
- 硬件推荐：昇腾 910B（最低 1 张 NPU 卡，需驱动/固件正确安装）
- Docker 建议版本：≥ 18.x
- 示例代码克隆地址：`https://gitcode.com/Ascend/msot.git`
- 示例代码放置路径：`~/ot_demo/msot`（其中 `example` 子目录是后续操作对象）
- 容器启动脚本：`ctr_in.py`，来源 `https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py`，下载时 `--retry 3`

**性能/系统信息数据**（原文 §3.2 预期输出示例）：
- 内核版本示例：`5.10.0-60.139.0.166.oe2203.aarch64`（aarch64 架构）
- 系统时间示例：`Mon Jun 29 15:21:01 UTC 2026`
- 系统负载示例：`System load: 8.44`，内存使用率：`1.5%`，Swap 使用：`0%`，磁盘使用：`27%`

> **注**：上述数字为文档给出的"预期输出"样例，并非性能基准数据。

---

## 【表格解读】

原文 §1 含一张前置条件表，逐字还原如下：

| 项目   | 要求                                                                  | 验证方法                           |
|------|---------------------------------------------------------------------|--------------------------------|
| **硬件算力** | Linux 服务器配备至少 1 张 NPU 卡（基于昇腾 910B/310P/A3 芯片，**推荐 910B**），驱动与固件已正确安装 | 执行 `npu-smi info`，确认 NPU 卡状态正常 |
| **容器运行** | 已安装并运行 Docker（建议版本 ≥ 18.x）                                          | 执行 `docker ps`，无报错即表示服务正常启动    |
| **执行用户** | 使用普通用户账户启动容器                                                        | 执行 `whoami`，返回非 `root` 的用户名    |
| **脚本执行** | 已安装 Python 3（任意版本）                                                  | 执行 `python3 -V`，有版本信息输出即表示已安装  |
| **网络通信** | 已安装 curl（任意版本）                                                      | 执行 `curl -V`，有版本信息输出即表示已安装     |

**逐行解读**：

- **硬件算力行**：限定了芯片系列为 910B/310P/A3 三选一，明确推荐 910B 为首选学习目标硬件，验证手段是华为 NPU 工具链中的 `npu-smi info`，与系统级 `nvidia-smi` 类比——它能枚举 NPU 卡的状态、显存、温度等。
- **容器运行行**：Docker 是后续所有部署动作的承载层（`docker pull`、运行 CANN 镜像等），版本门槛 18.x 保证了 BuildKit/健康检查等现代特性可用。
- **执行用户行**：要求"普通用户"启动容器，反映了容器安全最佳实践——避免以 root 运行无权限隔离的工作负载，验证方法 `whoami` 输出非 `root`。
- **脚本执行行**：Python 3 用于后续 §5 中调用 ACL 接口 `acl.get_soc_name()`，因此是必需的；任意版本说明此处不依赖具体 Python 版本特性。
- **网络通信行**：`curl` 用于 §3.1 下载 `ctr_in.py` 启动脚本，需具备基础网络/下载能力。

> 此外，§2.1 的 `case` 语句本质上是一张**"PCI ID → 镜像"映射表**，虽以代码形式呈现，与前置条件表功能对等：

| PCI Device ID | 芯片型号 | CANN 镜像（完整） |
|---|---|---|
| d500 | 310P | `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-310p-openeuler24.03-py3.11-devel` |
| d802 | 910B | `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel` |
| d803 | A3 | `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-a3-openeuler24.03-py3.11-devel` |
| 其他 | 不支持 | 输出 `[FAIL]` 错误信息 |

---

## 【公式解读】

**原文无公式。**

文档没有出现 LaTeX 数学表达式或伪代码算法公式。最接近"形式化定义"的是 §2.1 的 bash `case` 分支语句和 §5 中 `acl.get_soc_name().replace("Ascend", "")` 的字符串处理操作，但二者均为可执行的 shell/Python 语句，并非数学或算法公式，故按原文无公式处理。

---

## 【关联】

文档在多处通过锚点链接与本指南其他章节以及外部资源形成上下游关系：

1. **§2.1 → 外部资源**：链接到 [CANN 官方镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884)，是镜像选型的唯一权威来源。

2. **§2.2 → §8.1**：当 `docker pull` 在企业内网失败时，引用 §8.1 的代理/离线导入两种降级方案。

3. **§3.1 → §8.2**：当 `curl -fLO ctr_in.py` 失败时，引用 §8.2 的手工下载/拷贝方案。

4. **§3.2 → §2.1**：若容器启动出现容器选择界面或错误，提示回 §2.1 检查 `MY_STUDY_VAR_CANN_IMAGE` 是否正确，形成回路。

5. **§4 → §8.3**：`git clone` 失败时引用 §8.3 的 zip 包手动传输方案。

6. **§6 → 快速入门文档**：自检通过后引导用户"返回快速入门文档继续后续操作"，表明本指南是快速入门（quick_start）的前置章节，与 docs/zh/quick_start 下其它文档（如算子开发示例、Ascend C 教程等）形成**串联关系**。

7. **§7.1 ↔ §3.2**：FAQ 中的"重新进入容器"方法是 §3.2 启动流程的反向操作，依赖同一脚本 `~/ctr_in.py`。

8. **§8.1 方案二 → §2.1 + §3**：离线导入镜像后必须回到第 3 章继续容器启动流程，构成一个完整的"离线分支路径"。

9. **§8.3 → §5**：离线传输示例代码 zip 包并解压到 `~/ot_demo/msot` 后，需回到 §5 完成 SoC 型号注册。

> **上下游模块概览**：`msot` 仓库（`gitcode.com/Ascend/msot`）→ 本指南部署环境 → 快速入门后续章节（基于 `~/ot_demo/msot/example` 中的算子示例进行编译与运行）。

---

## 【使用方法】

以下命令均为原文给出的可执行步骤，按章节顺序汇总：

### §1 前置条件验证

```bash
npu-smi info        # 验证 NPU 卡状态
docker ps           # 验证 Docker 服务
whoami          # 验证当前用户非 root
python3 -V          # 验证 Python 3
curl -V             # 验证 curl
```

### §2 宿主机：CANN 镜像选择与拉取

```bash
# §2.1 自动识别芯片并写入环境变量（一行 source 命令，原文完整保留）
source /dev/stdin <<< "$(dev_id=$(lspci -n -D | grep -o '19e5:d[0-9a-f]\{3\}' | head -n1 | cut -d: -f2); case "$dev_id" in 'd500' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-310p-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=310P";; 'd802' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=910B";; 'd803' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-a3-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=A3";; * ) echo "unset MY_STUDY_VAR_CANN_IMAGE MY_CHIP_NAME; echo >&2; echo -e '\033[31m[FAIL] Get device ID: $dev_id. Learning is not supported in the current environment.\033[0m' >&2";; esac)"
[ -n "$MY_STUDY_VAR_CANN_IMAGE" ] && echo -e "\e[32m[PASS] Successfully identified chip [$MY_CHIP_NAME] and auto-selected image:\n    $MY_STUDY_VAR_CANN_IMAGE\e[0m"

# §2.2 拉取镜像
docker pull ${MY_STUDY_VAR_CANN_IMAGE}
```

### §3 宿主机：下载脚本并启动容器

```bash
# §3.1 下载启动脚本
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py

# §3.2 启动容器（容器内 Shell 出现后，§4–§6 均在容器内执行）
~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}
```

### §4 容器内：克隆示例代码

```bash
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
# 示例代码路径：~/ot_demo/msot/example
```

### §5 容器内：设置芯片 SoC 型号

```bash
echo 'export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c "import acl; print(acl.get_soc_name().replace(\"Ascend\", \"\"))")' > /etc/profile.d/custom-env.sh && chmod +x /etc/profile.d/custom-env.sh && source /etc/profile.d/custom-env.sh && { [ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip SoC type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e '\033[31m[FAIL] Failed to set environment variable $MY_STUDY_VAR_CHIP_SOC_TYPE!\033[0m'; }
```

### §6 安装自检

```bash
[ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip SoC type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e "\033[31m[FAIL] Missing environment variable MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m"
[ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] Example code repository OK\033[0m" || echo -e "\033[31m[FAIL] Example code repository missing\033[0m"
```

### §7 FAQ 操作

```bash
# §7.1 重新进入容器
~/ctr_in.py
# 或
docker exec -it alice_YYMMDD_HHMMSS bash

# §7.2 修复 Docker 权限（需 root）
sudo usermod -aG docker <当前用户名>
# 然后重新登录，或
newgrp docker
```

### §8 内网环境配置项

**Docker 代理配置**（`/etc/systemd/system/docker.service.d/http-proxy.conf`）：
```ini
[Service]
Environment="HTTP_PROXY=http://username:password@proxy.example.com:8080"
Environment="HTTPS_PROXY=http://username:password@proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1,.example.com"
```
生效命令：
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**离线镜像导入**（在线机 → 内网机）：
```bash
# 在线机
docker pull <MY_STUDY_VAR_CANN_IMAGE>
docker save -o cann.tar <MY_STUDY_VAR_CANN_IMAGE>

# 内网机
docker load -i cann.tar
docker images | grep cann
```

**离线代码导入**（容器内）：
```bash
unzip <MSOT_ZIP> -d ~/ot_demo
mv ~/ot_demo/msot-* ~/ot_demo/msot
ls ~/ot_demo/msot/example/quick_start
```

### 关键配置项汇总

| 配置项 | 取值/形式 | 作用范围 |
|---|---|---|
| `MY_STUDY_VAR_CANN_IMAGE` | 完整镜像 URL（含 tag） | 宿主机本次会话，`docker pull` 用 |
| `MY_CHIP_NAME` | `310P`/`910B`/`A3` | 宿主机本次会话，日志标识 |
| `MY_STUDY_VAR_CHIP_SOC_TYPE` | `acl.get_soc_name()` 去前缀值 | 容器内 `/etc/profile.d/custom-env.sh` 持久化，供后续算子编译使用 |
