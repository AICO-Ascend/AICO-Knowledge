# 🔄 回灌协议（反向回灌质检规范）

> 其他 project 用本仓做材料时（如做汇报 deck），会产出高质量裁剪图、公式重建、页位记录、跨论文关系等。
> 这些是本仓的**增量价值**，反向回灌可丰富知识库。但必须质检——只收高质量、可追溯的回灌，拒绝臆造。

## 标记格式（每条回灌必须带）

```
[来源] <源 project 绝对路径>  [日期] YYYY-MM-DD  [质检] ✅通过/⚠️存疑/✗拒绝
[内容] 裁剪图 / 公式重建 / 页位映射 / 跨论文关系
[源论文] <slug> · arXiv:<ID>（ID 须逐篇验证）
[原定位] Fig.N / p.X / Eq.N
```

## 质检标准（全过才接收，任一不过就标⚠️存疑或✗拒绝）

1. **裁剪图**：精确裁剪自原 PDF（`fitz` 区域裁剪，**非整页截图**），内容清晰可辨；命名含源论文 slug 便于追溯；落地 `extraction/assets_cropped/<源论文slug>__<图内容>.png`。整页截图本仓已有（`extraction/assets/`），回灌只收"精确裁剪/有损重建"的增量。
2. **公式重建**：从 e-print LaTeX 源（`eprint_formulas.py`）或 PDF 页面文本人工核对重建，与原文一致；**不接受 fulltext txt 的碎片拼接**（两栏 PDF 会断行错位）。重建的公式追加进 `extraction/formulas.json`（对应 slug）+ 论文 MD 公式块。
3. **页位映射**：标注**当前 deck 实际页位**（如 v4 deck P16/17）；旧版页位标签（如 v1 的 P7/P10）明确标"已过期/勿用"。不混用新旧页位。
4. **arXiv ID**：逐篇验证可访问（`arxiv.org/abs/<id>` 返回正确论文）；存疑 ID 标"⚠️存疑勿用"并**不引用**（绕开，如 Gated DeltaNet-2 / POD-Attention）。
5. **不猜来源**：无法验证出处的回灌，标"待确认"如实记录，**绝不臆造来源**（与本仓铁律一致）。

## 落地位置

| 回灌类型 | 落地位置 |
|---|---|
| 精确裁剪图 | `extraction/assets_cropped/<源slug>__<描述>.png` |
| 公式重建 | `extraction/formulas.json`（对应 slug）+ 论文 MD |
| 页位/技术点映射 | 对应 deck_references 文件（如 `uniinfer_deck_references.md`）+ `extraction/backfill_log.md` |
| 跨论文关系 | `extraction/MOC.md`（topic graph 补连线）+ `backfill_log.md` |

## 回灌日志

每次回灌追加一条到 `extraction/backfill_log.md`（日期、来源、内容清单、质检结果、剩余 gap）。
这是回灌的**审计轨迹**——下次再刷材料时可对照"哪些已回灌、哪些还缺"。

## 边界（回灌收不进的，仍需人工）

- **页图缺口**：仓内整页渲染不全（如 DSV3 只抽 p12/15/48，MTP 在 p10）——回灌裁剪图补缺口；其余用 `fitz` 从 `papers/<slug>.pdf` 现裁。
- **公式有损**：fulltext 抽公式会碎——精确公式必须走 e-print LaTeX 或人工核对。
- **存疑 ID**：验证不了的 ID 永远标存疑、不引用，等正确 ID 出现再更新。
