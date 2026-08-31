# glm53-flash deck v10 备份 (2026-08-30)

v10 = v9 + 用户 4 点优化:
1. KB 证据图放大 (kbstrip 210-340px 小条 → 46% 大图块 + M3 三段式展开解读)
2. 稀疏页填充闭环 (check_fill2 img uid 正则修复后重测: 全页 ≥75%, zoom ≤1.45 + 章扉/目录垂直居中)
3. M3 全页审核闭环 (35 页 × MiniMax-M3 → 抓到 8 处真问题: DSV3 fig05→fig02 错配、GDN tab04 caption 错、
   SSM 32→64×128×128、fig13 柱值 5→33、fig08 mono 无 CJK 方框、fig12 饼图描述错、目录页数口径、
   quarot 三条/四条右旋矛盾; 误报 6 处经 ground-truth 复核驳回)
4. 人工 PPTX 要点吸收 (prefix cache 难兼容 / 128→257 重构 / 量化直觉例子 x=[100,0.5,-0.2,0.3] /
   MTP 权重适配前置 + 定制化验证内核 + 单级 15% / 吞吐 21× vs TPOT 24.1× 口径 / 量化 ~50% 收益)

交付物: /mnt/project/g00952465/AI_Base_k3/glm53-flash-report/glm53-deck-v10.{html 为 glm53-flash-deck.html, pdf, pptx}
工具修复(已沉淀进 AICO-PPT skills): check_fill2 uid 正则 / export_deck fixed logo 克隆注入 /
verify_captions containment 度量 + marker「同源证据 ·」/ deck-content-gate 闸门 5 M3 审核 + FM8-FM10

## v10.1 (2026-08-31) — 用户第二轮 5 页布局 + 去刻意化
- P11 ch2-dsa: DSV3 Fig.2 整图(竖版)被 max-height 压扁 → 从原图裁 MLA 子模块(横版 1.76:1)，大图可读
- P12 ch2-mhc / P26 ch4-mtp: 窄栏内横式图条 → kbstrip 竖式(图上 100% 栏宽 + 文下)
- P31 深读-kb: 卡片横排(图 47%) → 竖排(图 100% 卡宽, contain 215px)
- P32 深读2-kb: object-fit:cover(裁切) → contain(完整)
- 正文去刻意化: 「同源证据·展开解读」→「方法出处·展开解读」；删「一图一出处」「M3 图文联合解读」尾巴；
  「同源代理/直接同源」→「方法同族/直接采用」；深读 foot 保留闭源声明(实质性)
- M3 复审又抓 1 真: arXiv:2512.24880 = 2025-12, 「Xie et al., 2026」→ 2025 (3 处)
- 工具: export_deck scrollIntoViewIfNeeded 超时 → evaluateHandle + scrollIntoView({block:'center'}) + try/catch (技能仓同步)
- verify_captions marker 同步为「方法出处 ·」; K2 caption 补源措辞过闸门 (0.177→0.228)
