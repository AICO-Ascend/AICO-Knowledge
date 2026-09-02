# 手动扩缩容

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/manual_scaling.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/manual_scaling.md

# 「手动扩缩容」文档深度解读

## 【定位】

本文档描述 MindIE Motor 在 K8s 集群上**对已部署 PD 分离 / PD 混部推理服务的 engine 实例数量进行手动调整**的操作流程——通过修改 `user_config.json` 中的实例数字段并执行扩缩容命令，在不影响 controller / coordinator 的前提下实现实例数量的增减。

---

## 【技术要点】

1. **三字段白名单**：扩缩容仅允许修改 `motor_deploy_config.p_instances_num`（PD 分离 P 端）、`motor_deploy_config.d_instances_num`（PD 分离 D 端）、`motor_deploy_config.hybrid_instances_num`（PD 混部）。任何其他字段变动会触发 `user_config changes detected beyond instance numbers` 报错。
2. **实例数硬约束**：上述三个字段值须 **大于 0 且不超过 16**，否则部署或扩缩容会报错。
3. **ConfigMap 基线机制**：集群内 ConfigMap `motor-config` 持久化当前已部署的 `user_config` 作为基线；扩缩容时把"基线"与"当前输入"做 diff，仅允许实例数差异。
4. **差异化执行策略**：扩容仅对**新增 index** 的实例执行 `kubectl apply`，已运行实例不会被重新拉起；缩容**从 index 大的实例开始依次删除**，并同步删除 `output/deployment/` 下对应的 engine YAML 文件。
5. **扩缩容后基线刷新**：成功后 ConfigMap `motor-config` 会更新为本次输入的 `user_config.json`，作为下一次扩缩容 / 刷新的新基线。
6. **作用域隔离**：扩缩容**只影响 engine 实例**，controller / coordinator 不在扩缩容路径中更新；如需改镜像、挂载路径等非实例数配置，必须**重新部署**而非扩缩容。

---

## 【关键机制与数据】

**基线读取 → diff → 执行 → 回写** 四步流程：

- **基线来源**（原文：集群内 ConfigMap `motor-config`，含"当前已部署的 user_config"）。
- **diff 范围**（原文："与当前输入对比，仅允许实例数变化"）——这是扩缩容路径的硬性约束，决定其与"全量重部署"的本质差异。
- **扩容执行**（原文："仅对新增实例 index 执行 `kubectl apply`，已运行实例不会被重拉"）——保证在线服务的副本不被重启，避免推理中断。
- **缩容执行**（原文："从 **index 大的实例开始** 依次删除，并同步删除 `output/deployment/` 下对应的 engine YAML 文件"）——确定性的删除顺序避免索引空洞带来的歧义；同步清理本地 YAML 保持 `output/deployment/` 与集群实际状态一致。
- **回写基线**（原文："成功后 ConfigMap 会更新为当前输入的 `user_config.json`"）——使下一次扩缩容的 diff 起点正确。
- **Prefix Cache 性能影响**（原文："Prefix Cache 特性默认开启，该特性会复用已计算好的 KV Cache，用于提高推理性能。新扩容的实例没有 KV Cache 缓存，因此该实例的推理性能可能出现小幅度劣化并在一段时间后恢复"）——这是文档中唯一的"性能数据形态"信息，但未给出具体百分比 / 时长数字，仅定性描述"小幅度劣化并恢复"。

文档未提供量化性能指标（如吞吐、时延、P99 数值等），亦未给出扩容 / 缩容操作的预计耗时。

---

## 【表格解读】

**原文无表格**。文档以命令块、列表和段落形式组织，未出现 markdown 表格或结构化参数对照表。配置字段、命令、报错信息均通过代码块 / 项目符号呈现。

---

## 【公式解读】

**原文无公式**。文档不含任何数学公式、伪代码表达式或带运算符的量化模型。所有约束（实例数范围 0–16）和策略（缩容从大 index 起删）均以自然语言陈述。

---

## 【关联】

- **PD 混部服务部署**：文末内部链接 `../deployment/k8s/pd_aggregation_deployment.md`（原文："PD 混部完整部署流程和配置说明请参考 [PD 混部服务部署](../deployment/k8s/pd_aggregation_deployment.md)"）——该文档负责 PD 混部的首次全量部署流程与配置项说明，本文档中的 `hybrid_instances_num`、PD 混部配置目录 `examples/deployer/../infer_engines/vllm/pd_hybrid` 均依赖其定义。
- **PD 分离部署路径**：本文档中 `--config_dir ../infer_engines/vllm` 对应 PD 分离的全量部署与扩缩容入口，与 PD 混部目录 `pd_hybrid` 形成并列分支。
- **ConfigMap `motor-config`**：作为扩缩容的基线持久化层，是本文档与"全量部署 / 刷新"功能共享的状态源；其缺失直接触发"首次部署前置条件"检查。
- **engine YAML（`output/deployment/`）**：扩缩容的本地副产物目录，与集群 engine 实例一一对应，缩容时同步清理；首次部署时由 `deploy.py` 生成。
- **Prefix Cache 特性**：被本文档点名为扩缩容性能行为的影响因素，新实例因缺失 KV Cache 缓存出现短期性能劣化——表明扩缩容特性与推理引擎缓存机制存在隐式耦合。

---

## 【使用方法】

### 启用前置条件（原文）
- 集群内已存在 ConfigMap `motor-config`（即至少完成过一次全量部署）。
- 操作者具备 `kubectl` 权限。

### 首次全量部署（原文命令）
```bash
cd examples/deployer

# PD 分离（方式一，推荐：指定配置目录）
python3 deploy.py --config_dir ../infer_engines/vllm

# PD 混部（方式一，推荐：指定配置目录）
python3 deploy.py --config_dir ../infer_engines/vllm/pd_hybrid

# PD 分离（方式二：单独指定配置文件）
python3 deploy.py --user_config_path ../infer_engines/vllm/user_config.json \
                  --env_config_path ../infer_engines/vllm/env.json

# PD 混部（方式二：单独指定配置文件）
python3 deploy.py --user_config_path ../infer_engines/vllm/pd_hybrid/user_config.json \
                  --env_config_path ../infer_engines/vllm/pd_hybrid/env.json
```

### 扩缩容操作步骤（原文命令）
1. 修改 `user_config.json` 中三个白名单字段之一：
   - PD 分离：`p_instances_num`、`d_instances_num`
   - PD 混部（CRD 默认）：`hybrid_instances_num`
   - 取值约束：**大于 0 且不超过 16**。
2. 在 `examples/deployer` 目录下执行扩缩容：
```bash
cd examples/deployer

# PD 分离
python3 deploy.py --config_dir ../infer_engines/vllm --update_instance_num

# PD 混部
python3 deploy.py --config_dir ../infer_engines/vllm/pd_hybrid --update_instance_num
```
若首次部署使用了方式二（指定 `--user_config_path` / `--env_config_path`），扩缩容时也需同样带上这两个参数。

### 常见报错处理（原文）
- **`ConfigMap motor-config not found or has no user_config in cluster`** → 尚未全量部署，先执行 `python3 deploy.py --config_dir ../infer_engines/vllm`（PD 混部同理用 `pd_hybrid`）。
- **`user_config changes detected beyond instance numbers`** → 改动超出白名单字段，需回退只修改 `p_instances_num` / `d_instances_num` / `hybrid_instances_num`。

### 注意事项（原文要点摘录）
- 扩缩容**只影响 engine 实例**，controller / coordinator 不更新。
- 改镜像 / 挂载路径等非实例数配置必须走**重新部署**流程。
- 缩容从高 index 起删，并清理 `output/deployment/` 下对应 YAML。
- 基线为集群内 ConfigMap `motor-config` 中的 `user_config`。
- Prefix Cache 默认开启，**新扩容实例因无 KV Cache 缓存会出现短期小幅性能劣化**，运行一段时间后恢复。
