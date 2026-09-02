# 功能介绍

> 仓 `mindie-motor` · 路径 `examples/features/observability/REAME.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/examples/features/observability/REAME.md

# mindie-motor · examples/features/observability/README.md 深度解读

## 【定位】
这篇文档描述 **Motor 推理服务如何通过 CCAE Reporter 接入华为自研的 CCAE (Cluster Computing Autonomous Engine) 集群自智引擎**,实现运行时信息(告警、日志、实例信息、metrics)的上报与纳管,并给出对接配置与热加载更新方法。

---

## 【技术要点】

1. **CCAE 纳管机制**:Motor 作为推理服务可被纳入 CCAE 集群自智引擎体系,CCAE Reporter 是对接入口,负责"采→传"全过程——采集 Motor 运行信息后上报到 CCAE。
2. **采集对象范围**:Reporter 上报的内容包含**告警、日志、实例信息和 metrics** 四类(原文:"告警、日志、实例信息和 metrics 等")。
3. **双向 TLS 安全通道**:通过 `motor_deploy_config.tls_config.north_tls_config` 配置南北向 TLS,字段包括 `enable_tls / ca_file / cert_file / key_file / passwd_file`,其中 `enable_tls=true` 表示启用。
4. **北向对接配置 `north_config`**:对接 CCAE Reporter 的连接参数,关键字段为 `name="ccae_reporter"`、`ip="xxx"`、`port=31948`(其中 IP 为占位符需替换为实际地址)。
5. **动态生效能力**:原文明确指出"该配置支持动态修改,Motor 运行过程中可以直接对接 CCAE,**无需重启 Motor 推理服务**",这意味着配置变更走的是热加载通道。
6. **两条配置下发路径**:通过 `examples/deployer` 下的 `deploy.py` 提供两种更新方式——`--config_dir` 目录级更新(推荐)与 `--user_config_path / --env_config_path` 单文件级更新,均以 `--update_config` 标记动作。

---

## 【关键机制与数据】

**工作原理 / 数据流(基于原文逻辑链):**

```
Motor 推理服务
      │
      │  ① CCAE Reporter 主动采集
      ▼
采集对象 = {告警, 日志, 实例信息, metrics}
      │
      │  ② 通过 north_tls_config 建立的加密通道(TLS)
      ▼
north_config 定位的 CCAE 端点(name=ccae_reporter, port=31948)
      │
      ▼
CCAE(Cluster Computing Autonomous Engine)集群自智引擎
```

- **接入链路定位**:Reporter 在 Motor 侧是"北向"组件(原文使用 `north_tls_config` / `north_config` 命名),对接方向为 Motor → CCAE。
- **配置热加载**:在 `user_config.json` 修改完毕后,无需重启推理进程,通过 deployer 的 `--update_config` 命令即可使新配置生效(原文:"Motor 运行过程中可以直接对接 CCAE,无需重启 Motor 推理服务")。
- **性能数据**:原文未提供任何性能指标(如上报频率、吞吐、时延等),**原文无性能数据**。

---

## 【表格解读】

**原文无表格。**

(原文中以 JSON 配置块与 shell 命令块形式给出配置与命令,未出现 markdown 表格或结构化对比表;最接近"参数清单"的是下列两块代码,在此**逐字还原**以便参考,但不属于表格范畴。)

**原文 user_config.json 配置块(逐字还原):**
```json
{
  "motor_deploy_config": {
    "tls_config": {
      "north_tls_config": {
        "enable_tls": true,
        "ca_file": "",
        "cert_file": "",
        "key_file": "",
        "passwd_file": ""
      }
    }
  },
  "north_config": {
    "name": "ccae_reporter",
    "ip": "xxx",
    "port": 31948
  }
}
```

字段含义逐行解读:
- `motor_deploy_config.tls_config.north_tls_config.enable_tls = true`:开启北向 TLS 加密链路。
- `ca_file / cert_file / key_file / passwd_file` 留空字符串:表示当前样例未给出具体证书路径,实际部署时需替换为有效路径。
- `north_config.name = "ccae_reporter"`:对接组件名固定为 ccae_reporter。
- `north_config.ip = "xxx"`:CCAE 端点 IP 占位符,需替换为实际地址。
- `north_config.port = 31948`:CCAE 监听端口。

**原文 deployer 更新配置命令(逐字还原):**
```bash
cd examples/deployer
# 方式一:指定配置目录(推荐)
python deploy.py --config_dir ../infer_engines/vllm --update_config

# 方式二:单独指定配置文件
python deploy.py --user_config_path ../infer_engines/vllm/user_config.json --env_config_path ../infer_engines/vllm/env.json --update_config
```

---

## 【公式解读】

**原文无公式。**

(全文未出现任何数学公式、伪代码逻辑式,亦无 LaTeX 形式表达式。)

---

## 【关联】

**与文中提到的上下游模块/特性的关系:**

- **CCAE(Cluster Computing Autonomous Engine)**:华为自研的集群自智引擎系统,是 Motor 的上层纳管方;本文档定位为"Motor ↔ CCAE 对接"的特性说明。
- **CCAE Reporter**:本特性的核心组件,职责是采集 Motor 侧数据并转发至 CCAE;在 `north_config.name` 中被命名为 `ccae_reporter`,在配置层面是该特性的"代言人"。
- **TLS 安全层(`north_tls_config`)**:为 Reporter ↔ CCAE 通信提供加密,属于部署层依赖,与 `motor_deploy_config` 体系耦合。
- **deployer(`examples/deployer/deploy.py`)**:配置下发的执行入口,负责把修改后的 `user_config.json` 推送至运行中的 Motor,实现热加载;在命令链路中位于本特性的"配置交付"环节。
- **`infer_engines/vllm/user_config.json` / `env.json`**:本特性示例所引用的目标配置文件路径,说明该对接特性以 vllm 作为示例推理引擎落地。

> 内部链接:文档未提供任何链接信息(原文标注"内部链接: (无)")。

---

## 【使用方法】

**启用方式(原文步骤):**

1. **编辑 `user_config.json`**,在 `motor_deploy_config` 下补全 `tls_config.north_tls_config`(TLS 证书相关字段),并在顶层添加 `north_config`(指定 `name=ccae_reporter`、`ip` 实际地址、`port=31948`)。
2. **进入 deployer 目录**:`cd examples/deployer`。
3. **下发更新配置(择一执行)**:
   - 方式一(推荐):`python deploy.py --config_dir ../infer_engines/vllm --update_config`
   - 方式二:`python deploy.py --user_config_path ../infer_engines/vllm/user_config.json --env_config_path ../infer_engines/vllm/env.json --update_config`
4. **验证**:无需重启 Motor 推理服务,新配置即可动态生效,CCAE Reporter 将自动开始采集并上报告警、日志、实例信息与 metrics 至 CCAE。

> **原文未涉及**:开启该特性所需的集群侧 CCAE 服务部署细节、证书签发流程、IP/端口选取规则、上报频率/采样策略、兼容性矩阵等均未在本文档中给出。
