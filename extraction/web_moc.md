# 网页域知识地图（web-extraction MOC）

> 第三知识域：官方文档站 / 厂商文档中心网页的抓取 + M3 七节深读。
> 注册表：`web_index.json` ｜ 原文：`web_docs/` ｜ 深读：`web_deep_docs/`
> 首批试跑 2026-09-02（5 页全通）。

## 页面清单

| 页面 | 来源 | 版本线 | 抓取路由 | 深读 |
|---|---|---|---|---|
| vLLM serve CLI 参数手册 | docs.vllm.ai | latest | direct-html | [web_deep_docs/vllm-cli-serve.md](web_deep_docs/vllm-cli-serve.md) |
| vllm-ascend 快速上手（中文） | docs.vllm.ai | latest | direct-html | [web_deep_docs/vllm-ascend-quickstart.md](web_deep_docs/vllm-ascend-quickstart.md) |
| Ascend Extension for PyTorch 环境变量参考 | hiascend | Pytorch 2600 | hiascend-source | [web_deep_docs/ascend-pytorch-envvars.md](web_deep_docs/ascend-pytorch-envvars.md) |
| CANN 环境变量参考 · 商用版 | hiascend | canncommercial 900 | hiascend-source | [web_deep_docs/ascend-cann-commercial-envvars.md](web_deep_docs/ascend-cann-commercial-envvars.md) |
| CANN 环境变量参考 · 社区版 | hiascend | CANNCommunityEdition 910beta1 | hiascend-source | [web_deep_docs/ascend-cann-community-envvars.md](web_deep_docs/ascend-cann-community-envvars.md) |

## 版本对照结论（机械 diff · 2026-09-02）

**CANN 商用版 900 与社区版 910beta1 的环境变量索引页内容一致**：URL 归一化后 diff 仅 4 行，
且全部为站内链接锚点 ID（`ZH-CN_TOPIC_…`）差异，环境变量名/分组/简介逐字相同。
→ 环境变量清单知识可跨版复用；后续若某版新增变量，重跑 web_fetch 后 diff 会直接暴露。

## 跨域关联（网页 ↔ 论文/代码仓）

- **vllm-ascend-quickstart** ↔ 代码仓域 [deep/repo-vllm-ascend.md](deep/repo-vllm-ascend.md)
  （网页给容器化上手，仓卡片给版本线 v0.25.1rc1 + ChunkKdaFwd 设计文档）
- **vllm-cli-serve** ↔ 代码仓域 [deep/repo-vllm.md](deep/repo-vllm.md)
  （`--kda-prefill-backend` 等参数 ↔ KDA 特性；论文域 KDA/DSA 方法源见 MOC.md）
- **ascend-pytorch-envvars**（网页版环境变量表）↔ 代码仓域 `repo_docs/pytorch/docs/zh/api/environment_variable/`
  （同源文档 docs-as-code；网页抓取版含最新 hiascend 链接，仓内版随 git tag 固定 —— 版本快照互补）
- **CANN 环境变量两页** ↔ 仓内无同源（CANN toolkit 文档未开源进 134 仓）→ 纯 web 增量，正是本域价值
