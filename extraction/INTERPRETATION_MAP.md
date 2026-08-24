# 解读与索引关系速查（人肉检查入口）

> 每张图/表/公式的「原始图片 → M3 解读 → 引用串」三者的对应关系都在这里查。

## 一张图的三层产物在哪

以 `scalable-moe` 的 Figure 1 为例：

| 层 | 文件 | 内容 |
|---|---|---|
| **原始图（整页）** | `extraction/assets/<slug>-p09.png` | 150 DPI 整页渲染 |
| **裁剪单图** | `extraction/assets/crops/<slug>-fig01.png` | 只含该 figure 的干净单图（报告直接插入） |
| **M3 解读** | `extraction/minimax_captions.json` 里 key=`extraction/assets/crops/<slug>-fig01.png`（无则用页级 `...-p09.png`） | MiniMax-M3 vision 的文字解读 |
| **引用元数据** | `extraction/visuals.json` → `<slug>.figures[num=1]` | `{num, page, caption, path}` |

表格同理：`crops/<slug>-tabNN.png` + `visuals.json` 的 `tables[]`。公式截图：`crops/<slug>-eqNN.png` + `formulas[]`。

## 程序化查询（不用手翻 JSON）

```bash
python3 - <<'PY'
import json
caps = json.load(open('extraction/minimax_captions.json'))
vis  = json.load(open('extraction/visuals.json'))
slug = 'scalable-training-of-mixture-of-experts-models-with-megatron-core'
v = vis[slug]
f = v['figures'][0]   # Figure 1
print("裁剪图:", f['path'])
print("caption:", f['caption'])
key = 'extraction/' + f['path']
print("M3 解读:", (caps.get(key) or caps.get(f"extraction/assets/{slug}-p{f['page']:02d}.png"))[:200])
PY
```

## 索引关系图

```
论文 MD (extraction/<slug>.md)
├── 图表节：![[assets/crops/<slug>-figNN.png]] + caption + [!tip] M3 解读
├── 表格节：![[assets/crops/<slug>-tabNN.png]] + caption + [!tip] M3 解读
├── 关键公式节：$$ LaTeX $$（权威源）或 ![[crops/<slug>-eqNN.png]]（无源截图）
└── ![[deep/<slug>]] → 6 段深读（图/表/公式解读已织入对应机制段）

figures_index.md          ← 全部图表的主索引（⭐=有 M3 解读）
visuals.json              ← crop → page/caption 映射（机器可读）
minimax_captions.json     ← 图片路径 → M3 解读文本（1576 条，裁剪图 100% 图文联合解读）
formulas.json             ← slug → LaTeX 公式列表（58 篇 479 条，权威源）
ar5iv_crops.json          ← 坏字体论文的 ar5iv 原图裁剪登记（54 张，重裁 overlay 保护）
papers.json               ← 论文 manifest（RAG 摄取入口）
```

## M3 解读的 key 规则（检查对应关系时用这个）

- `minimax_captions.json` 的 key = **图片相对 repo 的路径**（如 `extraction/assets/crops/xxx-tab01.png`）
- 查某张图有没有解读：`python3 -c "import json; print('extraction/assets/crops/xxx.png' in json.load(open('extraction/minimax_captions.json')))"`
- **【图文联合解读】前缀 = 上下文增强版**（2026-08-24 起）：crop 图 + 论文 caption + 正文中引用该图/表的段落联合喂 M3，解读锚定论文自己的论述，不再只看孤立图片。`context_caption.py` 幂等（有前缀即跳过），full_pipeline step 4 自动跑。
- **fig 裁剪图可能没有自己的 key**——它继承同页整页图（`assets/<slug>-pNN.png`）的解读（同一内容，不重复解读省 token）。表格/公式裁剪图**都有**自己的 key。
- **乱码 PDF 的裁剪来自 ar5iv 原图**（登记在 `ar5iv_crops.json`）：源头字体坏的论文（kv-management survey、deepseek-r1、dynamic-lcm 等 6 篇 19 张）从 arxiv HTML 取原始图/表重新生成，内容以 ar5iv 为准。
- 引用串格式：`[slug, Fig.N, p.X]`（arxiv 号在 `papers.json` 或 MD frontmatter）

## 全量覆盖率自查

```bash
python3 - <<'PY'
import json, glob
caps = json.load(open('extraction/minimax_captions.json'))
KEYS = set(caps) | {k.replace('extraction/','') for k in caps}
crops = glob.glob('extraction/assets/crops/*.png')
tabeq = [p for p in crops if '-tab' in p or '-eq' in p]
unc = [p for p in tabeq if p not in KEYS and p.replace('extraction/','') not in KEYS]
print(f"crop 总数 {len(crops)}；tab+eq {len(tabeq)} 张，未解读 {len(unc)} 张（应为 0）")
PY
```
