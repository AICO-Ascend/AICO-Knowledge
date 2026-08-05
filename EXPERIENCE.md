# 经验复盘：55 篇论文知识库的搭建（EXPERIENCE.md）

> 从 Moonlight 剪藏 → 干净索引 → PDF 下载 → 深度萃取 → 图文素材库 → 可复用 skill 的全过程踩坑与解法。
> 配合 `skills/paper-extraction/SKILL.md`（操作手册）阅读；本文是案例式 retrospective。

## 1. 源剪藏清洗（Phase 0）

**坑**：Moonlight 导出的 `paper_source_moonlight.md`（1MB）含 base64 内嵌图、网页导航杂质；初步清洗后的 `papers_index.md` 仍有残留：
- `![\]([base64图片已去除])` 这种破损 markdown 图片标记（base64 被替换成占位符但语法残留）。
- 列错位：很多行的「日期」跑到末尾列、「摘要」塞进了日期列（4 列表格变成错位）。
- `#25 Search-R1` 整行是 base64 图片 + 长摘要混在一起。

**解法**：写 Python 重解析器——按 `|` 分列，用日期正则 `\d{4}[/-]\d{1,2}[/-]\d{1,2}` 在任意列定位日期，其余长字段=摘要；剥除 `![\]([base64图片已去除])`、`![](...)`、arxiv 尾部杂质。重排成 7 列 `| # | title | date | abs_link | pdf_link | local_file | abstract |` → `papers_effective.md`。

**教训**：不要相信「已清洗」标签，自己按结构重解析一遍。

## 2. PDF 下载（Phase 3）—— 最大踩坑区

### 2.1 并行 curl 看似快实则慢
**坑**：为快速下 50 篇，用 `xargs -P 6` 并行 curl arxiv。结果 ~13/50 拿到的是**截断文件**（`%PDF-1.5` 头正常但 `fitz.open().page_count==0`）。识别成「下完了」实则损坏，后续萃取全失败。

**根因**：arxiv 对并发请求限流，连接中途被掐断，留下不完整 PDF（缺 xref 尾表，pymupdf 找不到页）。

**解法**：**别用并行 curl 下 arxiv**。统一用 `chunk_download.py`（HTTP Range 分块 + 每块重试）。看似串行慢，实则避免「下完→发现损坏→重下」的返工，总时间更短。

### 2.2 大文件（>3MB）截断，range 救不回
**坑**：本机网络对 arxiv 单连接有 ~1MB 传输上限——大文件（hyper-connections 7.4MB、let-it-flow 12.3MB）下到 ~1MB 就被掐。1MB 块的 range 请求第 2 块起也失败。

**解法**：`chunk_download.py` 调成 **256KB 小块 + 15 次重试/块 + 90s 超时**。小块完成更快、命中连接断概率低；15 重试+backoff 挺过 arxiv 临时限流。最终 9 篇大文件（最大 12.3MB）全部下成，`verify_pdfs.py` 报 0 截断。

**教训**：`verify_pdfs.py` 先体检再萃取——0 页 `%PDF` 头是**截断下载**，不是「缺失」也不是「HTML 错误页」，别在损坏文件上空跑 Phase 1。

### 2.3 arxiv API 返空
**坑**：`http://export.arxiv.org/api/query?id_list=...` 返回空 XML，解析报错。

**解法**：改抓 `https://arxiv.org/abs/<id>` 的 HTML `<title>` 标签拿标题（可靠）。

### 2.4 bash `$(curl)` 吃 PDF null byte
**坑**：分块下载时用 `bytes=$(curl ...)` bash 变量捕获二进制，null byte 被剥→文件损坏。

**解法**：用 Python `urllib`（二进制安全）或 `curl -o file` 直接写文件，绝不走 bash 变量。

### 2.5 非 arxiv 源的硬墙
- **OpenReview**（`#37 LOTT`）：`ChallengeRequiredError`，Cloudflare JS 挑战。服务器 curl、headless chromium（+stealth）都过不了「Verifying your browser」。**只能人工浏览器下载**，PDF 丢进 `papers/`，再更新索引。
- **ACM DL**（`#10 ZCube`）：`403` 订阅墙，无机构权限下不了。记链接、标 `✗ ACM 订阅墙`。

**教训**：这两类是「真下不了」，别在服务器上死磕——人工补 + 标记即可。

## 3. 深度萃取（Phase 1）

**工具**：PyMuPDF（`fitz`）——抽全文 + 找图表页（regex `Figure N:`）+ 渲染图表页 150DPI PNG + 提取 caption。

**坑 1：两栏 PDF 摘要提取**：`get_text` 在两栏 PDF 上文本顺序乱，`Abstract(.*?)Introduction` 正则常 miss。**解法**：宽松匹配 `Abstract|ABSTRACT`，stop 扩展到 `Keywords:`/`CCS Concepts`；miss 则取正文前 380 字兜底。

**坑 2：图表页 ≠ 架构图**：「Figure 2 所在页」可能是结果柱状图而非方法图。**解法**：按 caption 关键词（overview/architecture/framework/design/method/system/scan）挑架构图，不按图号。

**坑 3：精选图重复**：同一 PNG 承载多个图号（Fig.2 + Fig.4 同页），精选清单会列同一张 N 次。**解法**：按 PNG 路径去重。

**坑 4：GEPA 重复行**：`#16` 和 `#19` 是同一篇论文的两个索引行，指向同一 PDF。**解法**：canonical 一个 slug，两行都指它。

## 4. MiniMax 多模态图解读（Phase 2）

**做法**：核心架构图用 `mcp__minimax-coding-plan__understand_image` 解读——prompt 让它描述架构/组件/数据流 + 技术要点 ≤120 字 + 转录 caption。结果存 `minimax_captions.json`（key=图路径），Phase 1 重跑时 merge 进 MD 的 `[!tip]` + 主索引置顶「⭐ 精选架构图」。

**效率**：MiniMax 调用可并行——一条消息发 4-5 个 `understand_image` 工具调用，比串行快 5×。17 张架构图共 ~4 轮并行搞定。

**价值实证**：`Parallel Scan on Ascend` 那张，MiniMax 准确讲清了 910B AI Core（AIC 矩阵乘 + 2 AIV SIMD + UB scratchpad + MTE）和 scan 的映射，还点出「Cube/Vector 非对称 → 偏好 block-tiled 解耦 scan」——直接可用作技术报告论据。

## 5. 仓结构优化

**改前问题**：`extraction/` 混了 41 MD + 41 txt + 2 脚本 + assets 太乱；`papers_index.md`（清洗前）和 `paper_source_moonlight.md`（1MB 原始剪藏）堆在根；脚本硬编码绝对路径。

**改后**：
```
papers/                    # 源 PDF（<slug>.pdf）
papers_effective.md        # ⭐ 主干净索引
archive/                   # 原始 provenance（清洗前索引、原始剪藏）
skills/paper-extraction/   # SKILL.md + 3 脚本（路径相对，clone 即用）
extraction/                # 生成知识库
  ├── <slug>.md            #   结构化解析
  ├── fulltext/<slug>.txt  #   全文（grep 检索层）
  ├── assets/              #   图表 PNG
  └── figures_index.md     #   ⭐ 图表素材索引
```
**关键**：脚本用 `Path(__file__).resolve().parents[2]` 推 repo 根 → 路径相对 → clone 到别的论文仓即用。

## 6. 推送反复 non-fast-forward

**坑**：用户从别处（另一台机器/session）也在推这个仓，本地 push 常报 non-fast-forward。

**解法**：push 前总先 `git pull --rebase <token-url> main`。token 临时嵌 push URL，推完立刻 `git remote set-url --push origin <clean-url>` 抹掉，避免 token 留 `.git/config`。

## 7. 最终数字

| 指标 | 值 |
|---|---|
| 论文 | 55 篇（50 原始 + 5 用户后续加） |
| 深度萃取 | 55/55（全量，0 截断） |
| 图表 | 472 张 |
| MiniMax 深度解读架构图 | 17 张 |
| 非 arxiv 人工补 | 2（ZCube ACM、LOTT OpenReview） |
| 9 篇大文件截断 → chunk_download 256KB 块解法 | 全部下成 |

## 8. 可复用产出

- `skills/paper-extraction/SKILL.md` — 操作手册（5 阶段 + 决策树 + 约定 + 踩坑/效率）
- `skills/paper-extraction/extract_phase1.py` — 全量深度萃取（merge MiniMax）
- `skills/paper-extraction/chunk_download.py` — arxiv 大文件分块续传（256KB 块 + 15 重试）
- `skills/paper-extraction/verify_pdfs.py` — PDF 体检（截断/损坏/缺失/孤儿），CI gate

**下次任何论文仓做深度萃取 + 图文素材库**：clone `skills/paper-extraction/` 过去，按 SKILL.md 走，本文档当踩坑参考。
