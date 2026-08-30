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
