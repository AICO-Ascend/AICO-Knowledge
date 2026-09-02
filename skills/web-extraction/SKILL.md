---
name: web-extraction
description: Use when archiving web pages (official docs sites, vendor doc centers) into the AICO-Knowledge knowledge base — fetch server-rendered or SPA pages (hiascend Nuxt SPA via its doc_center/source raw route), normalize HTML to clean markdown (tables/links/anchors preserved, links absolutized), then MiniMax-M3 seven-section deep read with verbatim table restoration. Third knowledge domain alongside paper-extraction (arXiv PDFs) and repo-extraction (git repos). Entry point is webs_download_list.txt.
---

# web-extraction — 网页知识抓取与深度归档

## 这是什么

把**网页文档**（官方文档站 / 厂商文档中心）纳入 AICO-Knowledge 的第三条流水线，与
`paper-extraction`（论文 PDF）、`repo-extraction`（代码仓）并列、同一纪律：
机械层零臆造、LLM 深读带出处（URL）、产物全部登记进 extraction/ 注册表。

典型对象：工具 CLI 参数手册、环境变量参考、快速上手指南 —— 论文里没有、仓里也没有
（或版本不对齐）的官方运维知识。

## 输入：webs_download_list.txt

镜像 papers/repos 清单，每行一页：

```
# slug | url | 备注
vllm-cli-serve | https://docs.vllm.ai/en/latest/cli/serve/ | vLLM serve CLI 参数完整参考
```

## 两阶段流水线

```bash
# phase 1: 抓取与规范化 (零 LLM)
python3 skills/web-extraction/web_fetch.py [--only slug1,slug2]
#   → extraction/web_docs/<slug>.md   规范化 markdown (表格 pipe 还原 / 链接绝对化)
#   → extraction/web_index.json       注册表 (url/标题/抓取路由/字数/表行数/抓取时间/版本线索)

# phase 2: M3 七节深读 (同 repo_deep_read 规格)
python3 skills/web-extraction/web_deep_read.py [--only slug1]
#   → extraction/web_deep_docs/<slug>.md  七节深读 (ver=v1 幂等)
#     【定位】【技术要点】【关键机制与数据】【表格逐字还原解读】【公式逐字保留解读】【关联】【使用方法】
#   → web_index.json 每页回写 deep_note 字段 (单一注册表)
```

## 抓取策略（按序降级，2026-09-02 实测）

| 路由 | 判定 | 适用 |
|---|---|---|
| `direct(raw-md)` | URL 以 `.md` 结尾且返回体不是 HTML 壳 | hiascend 文档中心的 .md 直出页 |
| `direct-html` | curl 取 HTML 后内容探测（article/table/h1/pre 密度 ≥3） | docs.vllm.ai 等服务端渲染站 |
| `hiascend-source` | SPA 壳内容稀薄时，`document/detail/` 改写为 `doc_center/source/` 同源路径 | hiascend Nuxt SPA（见下） |

**hiascend SPA 路线（关键经验）**：`www.hiascend.com/document/detail/...` 是 Nuxt SPA，
原始 HTML 无正文，headless 渲染在受限网络下超时不可用。但内容 API 的原始内容路由
`/doc_center/source/` + 同路径直接可 curl（带浏览器 UA），实测 80KB 全表格正文完整。
注意：内容 API（ascendgateway）有 Referer 校验（406），raw 路由则无此限制。

**规范化三步**（`_cleanup`）：剥 mkdocs `[¶](#… "Permanent link")` 锚点 →
剥 `<term>` 等自定义标签 → 相对链接 `urljoin` 绝对化（站内互链是知识关联的出处，必须可点）。

## 与另外两域的纪律对齐

- **表格/公式同级要求**：深读 prompt 强制表格逐字还原（变量名/取值/默认值原样）+ 公式逐字保留 —— 与 repo 域 v2 prompt 同源
- **版本关联**：URL 中的版本段（`canncommercial/900`、`910beta1`、`Pytorch/2600`、`latest`）机械提取为 version_hints 原样进深读上下文，不做解读
- **幂等**：`ver=v1` 标记，升级 prompt 后自动重生成；web_index.json 单一注册表（不像 repo 域分两份）
- **长文全量**：参考手册类页面不截断（上限 100k 字符 ≈ M3 长上下文内），截断 = 丢表格
- **图**：网页 UI 图标（`public_sys-resources` 类）是装饰不是知识图，跳过；真实配图才走 M3 vision 图文关联（本批无）
- **同源优先**：网页内容优先在已有仓内找同源（如 pytorch 环境变量页内容已存在于 `repos_src/pytorch` docs）—— 避免重复归档，web 抓取只做仓内没有的增量

## 已知边界

- SPA 渲染兜底（playwright）代码位留白未启用 —— 现有 3 类路由已覆盖全部已知源，遇到新 SPA 站再补
- web 图稳定性差，默认不批量下载图；深读需要时按需 curl（同 repo 域 web 图策略）

## 试跑基线（2026-09-02 · 5 页）

- 5/5 ok：vLLM serve CLI（95k 字符全量深读，312 参数项）· vllm-ascend 中文快速上手 ·
  Ascend PyTorch 2600 环境变量表（22 变量全还原）· CANN 商用 900 / 社区 910beta1 环境变量索引（132 表行）
- **版本对照发现**：CANN 商用版 900 与社区版 910beta1 的环境变量索引页 diff 仅 4 行且全为
  站内锚点 ID 差异 → **两版环境变量清单内容一致，知识可跨版复用**（登记于 extraction/web_moc.md）
