# ascend-deployer适配OpenClaw组件安装部署与升级

> 仓 `ascend-deployer` · 路径 `docs/feature/支持openclaw安装部署.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascend-deployer/docs/feature/支持openclaw安装部署.md

# ascend-deployer 适配 OpenClaw 安装部署与升级 — 一体化深度解读

## 【定位】

本文档描述 ascend-deployer 对 OpenClaw 集群组件的"一键式安装、升级与批量配置热更新"能力：通过统一 inventory_file 参数录入 + Ansible playbook（`install_openclaw.yml` / `upgrade_openclaw.yml`）编排，覆盖从镜像加载、多实例容器拉起、删除重建升级到基于 JSON 的逐项 `config set/unset` 热更新全流程，降低 OpenClaw 集群的部署与运维复杂度。

---

## 【技术要点】

1. **三套主流程并列**：安装（`action=install` + `action=launch`，编排于 `install_openclaw.yml`）、删除重建升级（`upgrade_openclaw.yml` 中未提供 `openclaw_batch_config_file` 时执行）、批量配置热更新（提供 `openclaw_batch_config_file` 时执行，仅 `upgrade` 场景生效）。
2. **镜像加载双模式**：通过 `openclaw_image_file` 走 `docker load -i <file>` 从 tar 文件加载（要求文件存在且非软链接），否则直接使用 `openclaw_image_name`（必须带 tag，已通过 `docker images` 验证）。加载后从输出中解析 `Loaded image:` 后字符串记录镜像名至 ansible facts。
3. **实例保护与配置目录管理**：安装阶段若 `openclaw_config_dir` 下已存在 `docker-compose.yml` 或 `instance-*` 目录则判定为已有实例并终止安装以保护数据；通过校验后删除默认 `~/.ascend_deployer/openclaw-config`（或用户指定目录）确保干净启动。**升级阶段不清理配置目录**，并从 `mindclaw.json` 加载历史参数保证升级前后参数一致性。
4. **端口规划**：每个 OpenClaw 实例占用 4 个端口（Gateway、SFTP、mDNS、Reserved），实例之间端口间隔为 4；起始端口 `openclaw_base_port` 必须落在 1-65535 且未被占用。
5. **deploy.sh 容器编排命令**：
   ```shell
   bash deploy.sh up -n <count> -p <base_port> -m <model> --model-provider <provider> -u <infer_url> -c <config_dir> -i <image> --name <prefix> --skills [--token <token>]
   ```
   其中 `--skills` 会拷贝宿主机 mindclaw 下 `skills` 目录到容器；`--token` 仅在提供 `openclaw_gateway_token` 时追加；环境变量 `API_KEY`（来自 `openclaw_api_key`）和 `SUBNET`（来自 `openclaw_subnet`）通过 `environ_update` 透传。
6. **批量配置热更新机制**：遍历实例 `1..openclaw_instance_count`，按容器名 `<prefix>-<i>`（默认 `openclaw-1` 等）执行 `docker exec <container> openclaw config set <path> <value>`（含 `value`）或 `openclaw config unset <path>`（不含 `value`）；遇到 `Config validation failed` / `Unrecognized key`（set）或 `Config path not found`（unset）仅记录告警/提示并跳过，不中断流程；完成后执行 `bash deploy.sh stop -c <config_dir>` + `bash deploy.sh start -c <config_dir>` 重启集群。

---

## 【关键机制与数据】

- **playbook 编排文件**：`install_openclaw.yml`、`upgrade_openclaw.yml`；部署脚本：`mindclaw/scripts/deploy.sh`（可由 `resources_dir` 分发到 `TmpPath.ROOT/mindclaw/scripts/deploy.sh`）。
- **状态持久化文件**：`mindclaw.json`（保存于配置目录），升级删除重建模式下调用 `_save_config(update_image_only=True)`，**仅更新 `openclaw_image_name` 字段**，其余字段保持不变。
- **配置目录默认路径**：`~/.ascend_deployer/openclaw-config`（原文）。
- **批量配置 JSON 格式**（原文示例）：
  ```json
  [
    {"path": "agents.defaults.maxConcurrent", "value": 4},
    {"path": "browser.enabled", "value": true},
    {"path": "plugins.disabled_plugins"}
  ]
  ```
  数组中每个元素含 `path`；含 `value` 为新增/修改，不含为删除。
- **成功返回消息差异**（原文）：
  - 安装：`Launch OpenClaw cluster success`
  - 删除重建升级：`Upgrade OpenClaw cluster success`
  - 批量配置热更新：`Batch config update and restart success`
- **前置依赖**（原文）：目标机器已安装 Docker、docker-compose（或 docker compose 子命令）、openssl；`mindclaw/scripts/deploy.sh` 就绪；tar 镜像文件存在且非软链接；本地镜像名包含 tag 并经 `docker images` 验证。

> 性能数据：原文未提供任何吞吐、时延或资源占用数字。

---

## 【表格解读】

原文"关键参数说明"表格逐字还原：

| 参数                         | 说明                                | 默认值                                    |
| -------------------------- | --------------------------------- | -------------------------------------- |
| `openclaw_image_name`      | 镜像名（必须带tag）                        | -                                      |
| `openclaw_image_file`      | 镜像tar文件路径                          | -                                      |
| `openclaw_instance_count`  | 实例数量（正整数）                          | 必填                                     |
| `openclaw_base_port`       | 起始端口（1-65535）                      | 必填。每个实例占用4个端口（Gateway、SFTP、mDNS、Reserved），实例间端口间隔为4 |
| `openclaw_model_name`      | 模型名称                              | 必填                                     |
| `openclaw_infer_url`       | 推理服务URL                           | 必填                                     |
| `openclaw_gateway_token`   | 网关令牌（选填，不填自动生成）                    | -                                      |
| `openclaw_config_dir`      | 配置目录                              | `~/.ascend_deployer/openclaw-config`   |
| `openclaw_model_provider`  | 模型供应商                             | `local`                                |
| `openclaw_instance_prefix` | 实例名前缀                             | `openclaw`                             |
| `openclaw_api_key`         | API Key（选填）                      | -，透传为容器环境变量`API_KEY`                  |
| `openclaw_subnet`          | Docker子网（选填）                     | -，透传为容器环境变量`SUBNET`                   |
| `openclaw_batch_config_file`| 批量配置文件路径（选填）                      | -，仅在upgrade场景生效                        |

**逐行解读**：
- `openclaw_image_name` / `openclaw_image_file`：二者择一决定镜像来源，前者必须带 tag（如 `openclaw:custom`），后者为 tar 文件路径。
- `openclaw_instance_count`：正整数约束；与 `openclaw_base_port` 共同决定监听端口范围。
- `openclaw_base_port`：1-65535；端口规划公式化 — 第 N 个实例起始端口 = `base_port + 4*(N-1)`，每个实例连续占用 Gateway / SFTP / mDNS / Reserved 四个端口。
- `openclaw_model_name` / `openclaw_infer_url`：分别对应模型标识与推理服务 endpoint，二者均为必填。
- `openclaw_gateway_token`：选填；不填时由 `deploy.sh` 自动生成，仅在传入时追加 `--token`。
- `openclaw_config_dir`：决定 `docker-compose.yml` 与 `mindclaw.json` 落盘位置，默认 `~/.ascend_deployer/openclaw-config`。
- `openclaw_model_provider`：默认 `local`，透传为 `deploy.sh up --model-provider`。
- `openclaw_instance_prefix`：默认 `openclaw`，决定容器命名 `<prefix>-<i>`。
- `openclaw_api_key` / `openclaw_subnet`：通过 `environ_update` 注入为容器环境变量 `API_KEY` / `SUBNET`，仅起环境变量透传作用，不参与 `deploy.sh` 命令行参数拼接。
- `openclaw_batch_config_file`：仅 upgrade 场景生效；提供时走批量配置热更新分支，未提供时走删除重建分支。

---

## 【公式解读】

原文无公式。`bash deploy.sh up` 命令行与端口间隔 4 属于命令与参数说明，非数学公式。

---

## 【关联】

原文未提供内部链接或与其他特性/模块的引用关系（文末"内部链接: (无)"）。从文档内容可推断的上下游依赖关系：

- **上游触发**：仓库统一的安装入口 `bash install.sh --install=openclaw` / `bash install.sh --upgrade=openclaw`，与仓库内其他组件（驱动、固件、CANN、MindCluster 等）的安装命令同源，由 install.sh 统一调度分发。
- **依赖脚本**：`mindclaw/scripts/deploy.sh`（由 `resources_dir/mindclaw` 目录分发），是该特性容器编排的核心入口。
- **状态文件**：`mindclaw.json` 与 `openclaw_config_dir` 下的 `docker-compose.yml` 是安装/升级间持久化与实例保护的依据。
- **目标集群**：OpenClaw 集群（多实例 Docker 容器组成的推理/网关集群）。

---

## 【使用方法】

**启用方式（原文命令）**：
```shell
bash install.sh --install=openclaw      # 触发安装部署
bash install.sh --upgrade=openclaw     # 触发升级（根据 openclaw_batch_config_file 是否提供，自动选择删除重建或批量配置热更新）
```

**核心配置项（在 inventory_file 中填写）**：
- 镜像相关：`openclaw_image_name`（必填带 tag）、`openclaw_image_file`（二选一，tar 文件路径）。
- 实例与端口：`openclaw_instance_count`（正整数，必填）、`openclaw_base_port`（1-65535，必填）。
- 模型与推理：`openclaw_model_name`（必填）、`openclaw_infer_url`（必填，合法 http/https）、`openclaw_model_provider`（默认 `local`）。
- 命名与认证：`openclaw_instance_prefix`（默认 `openclaw`）、`openclaw_gateway_token`（选填，不填自动生成）。
- 路径与网络：`openclaw_config_dir`（默认 `~/.ascend_deployer/openclaw-config`）、`openclaw_api_key`（选填，透传 `API_KEY`）、`openclaw_subnet`（选填，透传 `SUBNET`）。
- 批量配置：`openclaw_batch_config_file`（选填，仅 upgrade 场景生效，**需自行分发到各目标节点指定路径**，Ansible 不会自动分发）。

**触发后行为（原文）**：
- 安装：自动完成镜像加载 + 集群拉起；存在已有实例时终止以保护数据。
- 升级（未提供批量配置）：删除重建，使用历史配置参数 + 新镜像重启集群。
- 升级（提供批量配置）：逐实例执行 `config set/unset`，错误配置项跳过，最后 stop+start 重启。
