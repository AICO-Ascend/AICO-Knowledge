#!/usr/bin/env python3
"""publish_pages.py — GitHub Pages 发布装配层。

背景: gitcode/gitee 已取消 Pages; GitHub Pages 走独立 gh-pages 分支
(main 的 docs/ 是设计文档目录, 不做发布源; 全仓 4.8GB 超 Pages 1GB 上限, 不能整仓发布)。
本脚本把可发布的 HTML 装配进 build/pages/ (gitignored), 由人工/脚本拷入 gh-pages 分支:

  build/pages/index.html                 落地页 (生成)
  build/pages/pages/ascend_infra.html    AscendInfra 专区 (链接重写: 仓内相对路径 → gitcode 绝对链接)
  build/pages/pages/tools/*.html         自建小工具 (自包含, 原样拷贝)
  build/pages/.nojekyll                  关闭 Jekyll (否则构建慢且下划线目录被吞)

新增可发布页面: 在 PUBLISH 里加一行 (源, 目标) 即可, 幂等重跑。
gh-pages 分支更新: 构建后拷入 gh-pages worktree 提交推送 (gitcode 镜像同步到 GitHub)。
"""
import re, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / 'build' / 'pages'
GITCODE_BLOB = 'https://gitcode.com/AICO-Ascend/AICO-knowledge/blob/main'

PUBLISH = [  # (源文件, 发布相对路径)
    ('bookshelf/ascend_infra.html', 'pages/ascend_infra.html'),
    ('bookshelf/tools/mfu_calculator.html', 'pages/tools/mfu_calculator.html'),
    ('bookshelf/tools/kv_memory_calculator.html', 'pages/tools/kv_memory_calculator.html'),
]
ASSETS = [  # 二进制资产 (原样拷贝)
    ('docs/images/ai_core_datapath.gif', 'assets/ai_core_datapath.gif'),
]


def rewrite_links(html):
    """仓内相对链接 → gitcode 绝对链接 (Pages 站点不含 extraction/ 等内容);
    ../docs/images/X → ../assets/X (随 ASSETS 拷贝)"""
    html = re.sub(r'src="\.\./docs/images/([^"]+)"', r'src="../assets/\1"', html)
    def repl(m):
        href = m.group(1)
        if href.startswith(('http://', 'https://', '#', 'mailto:')):
            return m.group(0)
        if href.startswith('../extraction/'):
            return f'href="{GITCODE_BLOB}/{href[3:]}"'
        if re.match(r'^[\w-]+\.md', href):  # SHELF.md / nvidia_infra.md 等 bookshelf 同目录 md
            return f'href="{GITCODE_BLOB}/bookshelf/{href}"'
        return m.group(0)
    return re.sub(r'href="([^"]+)"', repl, html)


INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AICO-Knowledge · 在线可视化与工具</title>
<style>
 body{font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;
      background:#f7f9fc;color:#1f2937;max-width:880px;margin:0 auto;padding:48px 24px}
 h1{font-size:26px;margin-bottom:4px}
 .sub{color:#6b7280;margin-bottom:32px}
 .card{display:block;background:#fff;border:1px solid #e2e8f0;border-radius:12px;
       padding:20px 24px;margin-bottom:16px;text-decoration:none;color:inherit;
       transition:box-shadow .15s}
 .card:hover{box-shadow:0 4px 16px rgba(30,64,175,.10);border-color:#bfdbfe}
 .card h2{font-size:18px;margin:0 0 6px}
 .card p{margin:0;color:#6b7280;font-size:14px;line-height:1.6}
 .tag{display:inline-block;font-size:12px;background:#eff6ff;color:#1d4ed8;
      border-radius:4px;padding:1px 8px;margin-left:8px;vertical-align:middle}
 footer{margin-top:40px;color:#9ca3af;font-size:13px}
 a.src{color:#4b5563}
</style></head><body>
<h1>AICO-Knowledge · 在线可视化与工具</h1>
<p class="sub">昇腾亲和的 AI Infra 知识库 —— 本页是由 GitHub Pages 托管的在线入口（代码主仓在 gitcode）</p>

<a class="card" href="pages/ascend_infra.html">
  <h2>♨️ AscendInfra 昇腾全栈知识专区<span class="tag">可视化</span></h2>
  <p>AI Core 架构与数据通路 · AscendC 概念体系 · 算子全景 · CANN/HCCL 手册速查 ·
     训推框架与模型落地映射 · 知识对照表——全部内容链回知识库深读资产。</p>
</a>

<a class="card" href="pages/tools/mfu_calculator.html">
  <h2>🧮 MFU 计算器<span class="tag">工具</span></h2>
  <p>6ND 公式在线估算训练算力利用率与训练时长，内置 H800 / A800 / 910B 预设。</p>
</a>

<a class="card" href="pages/tools/kv_memory_calculator.html">
  <h2>🧮 推理显存 & KV Cache 计算器<span class="tag">工具</span></h2>
  <p>权重 + KV cache 显存估算，支持 MHA / GQA / MLA 三种注意力结构对照。</p>
</a>

<footer>
  知识库主仓（论文/代码仓/网页三域深读资产）：
  <a class="src" href="https://gitcode.com/AICO-Ascend/AICO-knowledge">gitcode.com/AICO-Ascend/AICO-knowledge</a>
  · 本页由 <code>skills/bookshelf/publish_pages.py</code> 装配生成
</footer>
</body></html>
"""


def main():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    (OUT_DIR / '.nojekyll').parent.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / '.nojekyll').touch()
    n = 0
    for src, dst in PUBLISH:
        s, d = REPO / src, OUT_DIR / dst
        d.parent.mkdir(parents=True, exist_ok=True)
        content = s.read_text(encoding='utf-8')
        if src == 'bookshelf/ascend_infra.html':
            content = rewrite_links(content)
        d.write_text(content, encoding='utf-8')
        n += 1
    for src, dst in ASSETS:
        d = OUT_DIR / dst
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / src, d)
        n += 1
    (OUT_DIR / 'index.html').write_text(INDEX_HTML, encoding='utf-8')
    print(f'✓ 发布装配完成: index.html + {n} 页面 + .nojekyll → build/pages/')
    print('  下一步: 拷入 gh-pages 分支推送; GitHub 侧 Settings → Pages → gh-pages /(root)')


if __name__ == '__main__':
    main()
