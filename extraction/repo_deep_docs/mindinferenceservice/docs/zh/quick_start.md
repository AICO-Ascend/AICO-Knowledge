# 快速入门<a name="ZH-CN_TOPIC_0000002463251810"></a>

> 仓 `mindinferenceservice` · 路径 `docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindinferenceservice/docs/zh/quick_start.md

# docs/zh/quick_start.md 深度解读

## 【定位】

本文档是 MindInferenceService（MIS，推理微服务）的"快速入门"指南，解决**如何在 Atlas 800I A2 推理服务器上，从零开始完成环境准备、模型权重配置并启动提供 OpenAI API 兼容接口的推理微服务**这一端到端首次部署问题。

---

## 【技术要点】

1. **硬件与软件栈基线**：目标平台为 **Atlas A2 推理系列产品**（文档示例为 Atlas 800I A2），需配套安装 **NPU 驱动与固件**、**CANN Toolkit**，并通过 CANN 社区版或商用版的 set_env.sh 完成环境变量加载。

2. **服务运行依赖（Python 包，固定版本）**：
   - fastapi **0.121.1**
   - numpy **1.26.4**
   - pydantic **2.12.2**
   - PyYAML **6.0.3**
   - starlette **0.49.1**
   - uvloop **0.21.0**
   - vllm **0.11.0rc3**
   - vllm-ascend **0.11.0rc0**

3. **三个核心环境变量**：
   - `MIS_CACHE_PATH`：MIS 权重缓存根目录，原文示例为 `/data`（假设模型放在 `/data/Qwen3-8B`）。
   - `MIS_MODEL`：指定运行的模型名，原文示例为 `Qwen3-8B`。
   - CANN / ATB 运行库路径，通过 `source $HOME/Ascend/cann/set_env.sh` 与 `source $HOME/Ascend/nnal/atb/set_env.sh` 注入。

4. **启动方式**：进入 MIS 安装路径（示例 `$HOME/Ascend/mis/7.3.0`），执行 `./mis.pyz` 或 `python3 mis.pyz` 完成部署。

5. **API 接入**：服务监听 **127.0.0.1:8000**，对外提供 OpenAI 兼容的 `/openai/v1` 路径，原文示例 `base_url="http://127.0.0.1:8000/openai/v1"`，`api_key="dummy_key"`（占位，不作为认证凭据）。

6. **安全与权限约束（"须知"清单）**：权重来源可信且为 **safetensors** 类型；权重路径 / 安装路径 / 所有文件属主与运行用户一致；参数配置文件**非软链接**且路径字符串长度 **≤1024**；权重目录权限 **750**，权重文件权限 **640**；服务默认仅本地回环访问，需配合上游组件形成完整系统。

---

## 【关键机制与数据】

- **工作原理（原文）**：MIS 以 OpenAI API 兼容接口的形式对外暴露，用户只需完成环境初始化与模型路径配置，通过标准 API（如 `client.chat.completions.create(model="Qwen3-8B", messages=[...], max_tokens=100)`）即可发起推理请求，实现快速验证与集成。
- **数据流（原文）**：模型权重下载（魔乐社区 / Huggingface，类型为 safetensors）→ 放置于本地 `MIS_CACHE_PATH`（例 `/data`）下 → 通过 `MIS_MODEL` 指定具体子目录（例 `Qwen3-8B`）→ 执行 `mis.pyz` 加载 vllm/vllm-ascend 推理栈 → 监听 `127.0.0.1:8000` 的 `/openai/v1` 端点 → 客户端以 OpenAI SDK 调用 `chat.completions` 获得响应。
- **性能数据**：原文未提供吞吐量、时延、显存占用等任何 benchmark 数字；本文档不涉及性能指标。

---

## 【表格解读】

**原文无表格**（文档以分步骤文字 + 代码片段组织，无 markdown 表格）。

---

## 【公式解读】

**原文无公式**（文档未给出 LaTeX 或伪代码公式）。

---

## 【关联】

依据文末给出的两条内部链接，文档在整体知识库中处于如下上下游位置：

| 链接目标 | 关系定位 |
|---|---|
| `installation_guide.md#安装部署` | **上游 / 前置**：负责 MIS 软件包本体及其依赖的安装步骤，本文档"环境准备"一节明确将 MIS 的安装指向该文档。 |
| `security_hardening.md#推理微服务安全加固` | **下游 / 强化**：由于 MIS 默认监听 `127.0.0.1`、需以组件集成方式与其他系统配合，安全加固细节（认证、网络隔离等）由该文档承接。 |

此外，文档将 NPU 驱动/固件与 CANN Toolkit 的安装指向**昇腾官方《CANN 软件安装指南》**的商用版与社区版两套外部链接（区分 `canncommercial` 与 `CANNCommunityEdition` 路径），说明本快速入门假设读者已具备或同时具备 CANN 基础软件栈。

---

## 【使用方法】

按原文步骤复现如下（命令与原式一致）：

**1. 准备权重与缓存路径变量**
```shell
export MIS_CACHE_PATH=/data
```
（原文：假设模型权重下载路径为 `/data/Qwen3-8B`，将 `MIS_CACHE_PATH` 设置为 `/data`）

**2. 加载 CANN / ATB 运行库环境变量**
```shell
source $HOME/Ascend/cann/set_env.sh      # 示例路径，按实际安装路径修改
source $HOME/Ascend/nnal/atb/set_env.sh  # 示例路径，按实际安装路径修改
```

**3. 指定运行模型**
```shell
export MIS_MODEL=Qwen3-8B
```

**4. 进入 MIS 安装路径并启动**
```shell
cd $HOME/Ascend/mis/7.3.0
./mis.pyz
# 或
python3 mis.pyz
```

**5. 发起 OpenAI 兼容对话请求**
```python
from openai import OpenAI
client = OpenAI(
    base_url="http://127.0.0.1:8000/openai/v1",
    api_key="dummy_key"  # 占位字段，不作为认证凭据
)
response = client.chat.completions.create(
    model="Qwen3-8B",
    messages=[
        {"role": "system", "content": "你是一个友好的AI助手。"},
        {"role": "user", "content": "你好"},
    ],
    max_tokens=100
)
print(response.choices[0].message)
```

**6. 强制约束（原文须知）**
- 权重来源可信、类型必须为 `safetensors`。
- 权重路径、MIS 安装路径及所有文件属主与运行用户一致。
- 参数配置文件**不是软链接**，路径字符串长度 **≤1024**。
- 权重目录权限 **750**，权重文件权限 **640**。
- MIS 仅监听 `127.0.0.1`，需通过上游组件集成形成完整推理服务系统（详见 `security_hardening.md#推理微服务安全加固`）。
