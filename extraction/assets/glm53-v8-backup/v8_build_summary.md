# GLM 5.3-flash deck v8 重建总结 (2026-08-28)

## v7 → v8 关键变化
- **v7 问题**: 内容稀疏 (200 字/页), 插图与论点脱钩 (12 张同源代理图但与本页 "主论点" 贴合度低), 缺少图旁注解与参考文献汇总
- **v8 目标**: 全面仿 v9 设计模式 — 每节扩到 800-1500 字, PILLAR×3 + 图+caption + dark-table + 小白话 + 数据结论 + 加 7 辅助页

## v8 设计模式 (仿 v9)
1. **PILLAR 1/2/3 三栏卡片** (浅色背景 + 深色 border + 关键词红字)
2. **dark-header 对照表** (bg #1b2333, highlight 列 #2a1416/#e8b4b8)
3. **图 + 图旁 caption + 引用出处** (三段式: 图说 + arXiv ID + 同源代理声明)
4. **小白话** (浅黄底 + 👶 标识 + 通俗比喻)
5. **数据结论块** (浅蓝底 + 📌 标识 + 量化对比)
6. **参考文献末页** (按主题分组 + arXiv 逐篇验证)

## v8 结构 (19 sections, 5 chapters)
| idx | label | chapter | 内容 |
|---|---|---|---|
| 1 | 封面 | CH1 门面 | 渐变背景 + 标题 + 3 PILLAR 卡 + KB 标注 |
| 2 | 目录 | CH1 门面 | 5 章 19 页一图速览 |
| 3 | 关键技术总览 | CH1 门面 | 12 项技术 + 5 列 dark-table (highlight 一句话核心) |
| 4 | ch1-attn | CH1 门面 | PILLAR×3 + IndexCache 图 + 5 行 dark-table + 小白话 + 数据结论 |
| 5-9 | ch2 五件 | CH2 五件套 | kda/mhc/dsa/kpool/swiglu 每节 PILLAR×3 + KB 图 + 小白话 + 数据结论 |
| 10-11 | ch3 | CH3 训练调度 | pipeline/rot 同模式 |
| 12-15 | ch4 | CH4 推理部署 | ladder/graph/kpool/mtp 同模式 |
| 16 | 性能对照 | CH5 收尾 | 8 个大数字 VS (4 推理 + 2 训练 + 2 下游) |
| 17 | 总结 | CH5 收尾 | 4 件套 TAKEAWAY (深底黑块终极结论) |
| 18 | 术语速查 | CH5 收尾 | 26 项核心术语 3 栏 grid |
| 19 | 参考文献 | CH5 收尾 | 12 篇同源论文按 6 主题分组 |

## 12 张 KB 原图 (全部来自 AICO-knowledge/extraction/assets/)
| 章节 | 论文 | arXiv |
|---|---|---|
| ch1-attn | IndexCache · Fig.1 | arXiv:2608.02288 |
| ch2-kda | Kimi K3 · Fig.3 | Kimi K3 2026/7 |
| ch2-mhc | HC · Fig.1 | arXiv:2512.24880 |
| ch2-dsa | DeepSeek-V3 · Fig.5 | arXiv:2412.19437 |
| ch2-kpool | IndexCache · p.3 整页 | arXiv:2608.02288 |
| ch2-swiglu | Kimi K2 · Fig.2 | arXiv:2507.20534 |
| ch3-pipeline | Megatron-LM · Fig.4 | arXiv:2104.04473 |
| ch3-rot | HC · Fig.2 | arXiv:2512.24880 |
| ch4-ladder | Kimi Linear · Fig.6 | arXiv:2510.26692 |
| ch4-graph | DeepSeek-V3 · Fig.2 | arXiv:2412.19437 |
| ch4-kpool | Gated Delta · Tab.4 | arXiv:2412.06464 |
| ch4-mtp | DeepSeek-V3 · Fig.3 | arXiv:2412.19437 |

## 关键技术沉淀 (本次踩坑)
1. **NFS soft quota** — `mod.save()` 的 fclose 触发 `[Errno 122] Disk quota exceeded` 报错但实际写入成功; 改用 staging 文件 + `cp` 命令绕过
2. **deck corruption** — v7 deck 中途保存损坏 (template script tag 丢失, 18MB 内容跑光); 修复: 用 tech-share-deck.html (14MB 空白模板) 作底版, 直接 set_template + 灌入新 sections
3. **manifest JSON escaping** — `dump_template()` 必须 `</` → `</` 转义, 否则 manifest 解析失败

## 交付物
- `/mnt/project/g00952465/AI_Base_k3/glm53-flash-report/glm53-flash-deck.html` (15.5MB)
- `glm53-deck-v8.pdf` (7.4MB, 19 页)
- `glm53-deck-v8.pptx` (11MB, 19 slides)
- 仓内备份: `extraction/assets/glm53-v8-backup/` (deck + 19 PNG + build script + sections data)

## 后续可选优化
- M3 内容审核 (slide-04..19): 表格比例 / 图文联合 / 表达准确性
- check_overflow.mjs: 检测 slide-04..15 的 caption + table 是否超框
- 进一步把同源代理标注统一改为 "📚 {slug}" 风格 chip
