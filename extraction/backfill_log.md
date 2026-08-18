# 📒 回灌日志（backfill_log）

> 反向回灌的审计轨迹：每次从其他 project 回灌材料到本仓，追加一条。
> 质检规范见 `skills/paper-extraction/BACKFILL_PROTOCOL.md`。

---

## 2026-08-18 · 首次回灌（来自 InferArch/uniinfer_low_latency_gxli_qwen36）

- **来源**：`/mnt/project/g00952465/InferArch/uniinfer_low_latency_gxli_qwen36/task-qwen36-35B-A3B/01_总结与汇报/`
- **触发**：另一 project 用本仓做 Qwen3.6-35B-A3B × UniInfer 攻关汇报 deck v4 时，从原 PDF 精确裁剪了 6 张图 + 建了 TECH_DEEPDIVE_REFERENCES_20260817.md（原图+公式+实测+已验证 arxiv 映射）
- **质检**：✅ 全过（6 图均精确裁剪自 `papers/` 源 PDF；arxiv ID 逐篇验证；2 个存疑 ID 已标注绕开）

### 回灌内容清单

| # | 裁剪图 → 落地路径 | 源论文 / arXiv | 质检 |
|---|---|---|---|
| 1 | `assets_cropped/gated-delta-networks-...__block-design.png` | GDN · 2412.06464 | ✅ Fig.1 GDN block |
| 2 | `assets_cropped/deepseek-v3-technical-report__mtp.png` | DSV3 · 2412.19437 | ✅ Fig.3 MTP 链式 |
| 3 | `assets_cropped/sarathi-...__roofline.png` | Sarathi-Serve · 2403.02310 | ✅ Fig.5 roofline |
| 4 | `assets_cropped/sarathi-...__genstall.png` | Sarathi-Serve · 2403.02310 | ✅ Fig.7 stall 时间线 |
| 5 | `assets_cropped/efficient-memory-management-...__block-table.png` | PagedAttention · 2309.06180 | ✅ Fig.6 块表 |
| 6 | `assets_cropped/parallel-scan-on-ascend-...__910b-aicore.png` | Parallel Scan · 2505.15112 | ✅ Fig.3.1 910B AI Core |

### 页位记录（v4 deck 实际页位，已对位旧 v1 标签）

- v4 **P16/17** — 全链路 NPUGraph（§6 硬件约束）
- v4 **P19** — accept-fold / 免回滚（§1 GDN state + §3 MTP verify）
- v1 的 P7/P10 标签**已过期**（见 `uniinfer_deck_references.md` 回灌段）

### ⚠️ 存疑 ID（仍存疑，本次 deck 已绕开未引用）

- Gated DeltaNet-2 · ~~2605.22791~~ — fla repo 有实现，arxiv ID 搜不到
- POD-Attention · ~~2410.18038~~ — agent 提 ASPLOS'25，ID 搜不到

### 剩余 gap（下次植入前仍需人工）

- DSV3 整页只抽 p12/15/48，MTP 在 p10（本次裁剪图已补 p10 MTP）
- GDN gated delta rule 在 fulltext 断行错位——精确公式已人工核对（见 TECH_DEEPDIVE §1）
- 其余 §2/§3/§4/§5/§7 的 v4 精确页位未在 TECH_DEEPDIVE 显式标注（需去 v4 deck 源文件对位，不从旧标签推断）
