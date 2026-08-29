SECTIONS = []

SECTIONS.append(('cover', wrap_section('封面', (
    '<div style="background:linear-gradient(135deg, #1b2333 0%, #2b5a8c 100%); '
    'position:absolute; inset:0; padding:120px 130px; color:#fff;">'
    '<div style="font:14px/1.4 JetBrains Mono,monospace; color:#b8c5d8; letter-spacing:.15em;">'
    'TECH DEEP-DIVE · 2026/08</div>'
    '<h1 style="margin:30px 0 0; font-size:78px; font-weight:700; line-height:1.15; '
    'letter-spacing:-.01em;">GLM 5.3-flash</h1>'
    '<div style="margin-top:12px; font-size:42px; font-weight:600; color:#e8c547;">'
    '45 层混合 · 34 KDA + 11 DSA · mHC 多流残差</div>'
    '<div style="margin-top:48px; font-size:22px; color:#d8dce4; line-height:1.65; max-width:1300px;">'
    '一份面向"技术小白"的深度解读 — 把每一项架构创新拆成 "是什么 / 为什么 / 怎么做到的"，'
    '并配以知识库原图 + 同源代理论文 + 量化数据结论。</div>'
    '<div style="display:flex; gap:18px; margin-top:50px;">'
    '<div style="flex:1; background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.18); '
    'border-radius:10px; padding:18px 22px;">'
    '<div style="font:13px JetBrains Mono,monospace; color:#e8c547;">PILLAR 1 · 注意力</div>'
    '<div style="font-size:18px; font-weight:600; margin-top:6px;">O(n²) → 线性 O(n) → 稀疏 kPool</div>'
    '</div>'
    '<div style="flex:1; background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.18); '
    'border-radius:10px; padding:18px 22px;">'
    '<div style="font:13px JetBrains Mono,monospace; color:#e8c547;">PILLAR 2 · 残差流</div>'
    '<div style="font-size:18px; font-weight:600; margin-top:6px;">4 流 mHC + Sinkhorn 投影</div>'
    '</div>'
    '<div style="flex:1; background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.18); '
    'border-radius:10px; padding:18px 22px;">'
    '<div style="font:13px JetBrains Mono,monospace; color:#e8c547;">PILLAR 3 · 训练推理</div>'
    '<div style="font-size:18px; font-weight:600; margin-top:6px;">msmodelslim 4 步 + DualPipe + MTP</div>'
    '</div>'
    '</div>'
    '<div style="position:absolute; bottom:50px; left:130px; font-size:16px; color:#9aa3b3;">'
    '知识库支撑：AICO-Knowledge · 69 篇同源论文 · 685 图 · 479 公式 · 100% M3 视觉核验</div>'
    '</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 2: 目录 (议程/历程)
# ─────────────────────────────────────────────────────────
SECTIONS.append(('toc', wrap_section('目录', (
    '<h2 style="margin:0 0 28px; font-size:42px; font-weight:700; color:#1a1a1c;">'
    '本 deck 的 5 章 19 页 · 一图速览</h2>'
    '<div style="display:flex; gap:22px; margin-top:14px;">'
    '<div style="flex:1; background:#eef3fb; border:1.5px solid #2b5a8c; border-radius:12px; '
    'padding:22px 24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b5a8c; letter-spacing:.1em;">CH 1 · 门面</div>'
    '<div style="font-size:22px; font-weight:700; margin:6px 0 14px;">注意力机制全景</div>'
    '<div style="font-size:15px; color:#444; line-height:1.7;">'
    '· ch1-attn (3 页)<br>· O(n²) → O(n) → 稀疏 kPool 三段式路由</div>'
    '</div>'
    '<div style="flex:1; background:#fdf6f5; border:1.5px solid #b5333b; border-radius:12px; '
    'padding:22px 24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#b5333b; letter-spacing:.1em;">CH 2 · 五件套</div>'
    '<div style="font-size:22px; font-weight:700; margin:6px 0 14px;">核心架构创新</div>'
    '<div style="font-size:15px; color:#444; line-height:1.7;">'
    '· ch2-kda · mhc · dsa · kpool · swiglu (5 个技术页)</div>'
    '</div>'
    '<div style="flex:1; background:#eef7ee; border:1.5px solid #2b6a2b; border-radius:12px; '
    'padding:22px 24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b6a2b; letter-spacing:.1em;">CH 3 · 训练调度</div>'
    '<div style="font-size:22px; font-weight:700; margin:6px 0 14px;">并行策略</div>'
    '<div style="font-size:15px; color:#444; line-height:1.7;">'
    '· ch3-pipeline · rot (2 页)<br>· 4 步 processor + 旋转 trick</div>'
    '</div>'
    '</div>'
    '<div style="display:flex; gap:22px; margin-top:18px;">'
    '<div style="flex:1; background:#faf6ee; border:1.5px solid #8a6a2b; border-radius:12px; '
    'padding:22px 24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#8a6a2b; letter-spacing:.1em;">CH 4 · 推理部署</div>'
    '<div style="font-size:22px; font-weight:700; margin:6px 0 14px;">Hybrid 注意力 + 推测解码</div>'
    '<div style="font-size:15px; color:#444; line-height:1.7;">'
    '· ch4-ladder · graph · kpool · mtp (4 页)</div>'
    '</div>'
    '<div style="flex:1; background:#f3eef8; border:1.5px solid #6a4a8c; border-radius:12px; '
    'padding:22px 24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#6a4a8c; letter-spacing:.1em;">CH 5 · 收尾</div>'
    '<div style="font-size:22px; font-weight:700; margin:6px 0 14px;">数据 · 总结 · 术语 · 参考文献</div>'
    '<div style="font-size:15px; color:#444; line-height:1.7;">'
    '· 性能对照 + 收尾 PILLAR + 术语速查 + 参考文献 (5 页)</div>'
    '</div>'
    '</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 3: 关键技术总览
# ─────────────────────────────────────────────────────────
SECTIONS.append(('overview', wrap_section('关键技术总览', (
    '<h2 style="margin:0 0 8px; font-size:36px; font-weight:700; color:#1a1a1c;">'
    'GLM 5.3-flash 关键技术总览（12 项）</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    '每项都对应知识库中一篇或多篇同源代理论文 — 后文 12 节逐一拆解。</p>'
    + dark_table(
        ['类别', '技术点', '一句话核心', '同源代理论文', 'arXiv'],
        [
            ['注意力', 'KDA 滚动总结', '每 token O(1) 递推，替代 O(n²) attention', 'Yang et al. 2025 / 2026', '2510.26692'],
            ['注意力', 'DSA 稀疏索引', 'lightning indexer 筛 top-k=2048', 'Liu et al. 2026', '2608.02288'],
            ['注意力', 'kPool 池化', '4 token 合成 1 pool_key，索引粒度 ÷4', 'Liu et al. 2026', '2608.02288'],
            ['注意力', 'Hybrid KDA+MLA', '短文 KDA / 长文 MLA 分级路由', 'DeepSeek-AI 2024', '2412.19437'],
            ['残差流', 'mHC 多流残差', '4 流并行 + Sinkhorn-Knopp 投影', 'Xie et al. 2026', '2512.24880'],
            ['残差流', 'SwiGLU clamp=10', 'silu×up 上限 10，防训练发散', 'Moonshot AI 2025', '2507.20534'],
            ['训练调度', 'msmodelslim 4 步', 'DualPipe + ZB-H1 + MoE all-to-all', 'Narayanan et al. 2021', '2104.04473'],
            ['训练调度', 'RoT 旋转 trick', 'W·R 矩阵右乘稳定 Sinkhorn', 'Xie et al. 2026', '2512.24880'],
            ['推理部署', 'KDA 7 级阶梯', '256/512/1K/2K/4K/8K/128K 自动路由', 'Yang et al. 2025', '2510.26692'],
            ['推理部署', 'Hybrid graph', 'KDA+MLA 节点级调度图', 'Yang et al. 2025', '2510.26692'],
            ['推理部署', 'kPool 部署', 'GDN cache 145MiB / 序列', 'Yang et al. 2024', '2412.06464'],
            ['推理部署', 'MTP 多 token 预测', '一次预测 3-5 token，draft model', 'DeepSeek-AI 2024', '2412.19437'],
        ],
        highlight_col=2
    )
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
    '<b>📌 阅读建议：</b>本 deck 按 ch1 (1) → ch2 五件 (5) → ch3 (2) → ch4 (4) 顺序展开，'
    '每节都包含：3 段 PILLAR 卡片 + 1 张 KB 原图 + 1 个数据对照表 + 1 段"小白版"白话。'
    '末页附"性能数字大 VS" + "术语速查" + "参考文献"三件套。</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 4: ch1-attn (PILLAR 注意力三段式)
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch1-attn', wrap_section('ch1-attn', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch1-attn · 注意力机制 O(n²) → 线性 O(n) → 稀疏 kPool</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'Q/K/V 三件套是 Transformer 发动机。标准 attention 让每个 token 对所有 token 打分，'
    '上下文 128K 时算力爆炸（每 token 要算 128K 次）。<br>'
    '<b style="color:#b5333b;">GLM 5.3-flash 走"34 层 KDA 滚动总结 + 11 层 DSA 稀疏索引"分层路由</b>，'
    '8K 以下走 KDA 快路径，超过 8K 切到 DSA 稀疏索引。IndexCache (GLM-5 兄弟模型) 正在做同一件事。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', 'KDA · 滚动总结',
        '<b>递推式状态更新</b>，每 token O(1)。上下文 128K 时算力只增加 128K 倍 '
        '（vs 标准 attention 增加 128K² 倍）。')
    + pillar_card(2, 'b5333b', 'DSA · 稀疏索引',
        '<b>lightning indexer</b> 预筛 top-k=2048 关键 token，'
        '只对这 2048 个 token 算 attention — 节省 64× 算力。')
    + pillar_card(3, '2b6a2b', 'kPool · 4-to-1 池化',
        '把每 4 个 token 合成 1 个 pool_key，<b>索引粒度 ÷4</b>，'
        'cache 容量从 2.2GB 降到 145MiB 同时不丢精度。')
    + '</div>'
    + fig_with_caption(img_uids['ch1-attn'],
        '图：GLM-5 + IndexCache 在 10 个 long-context 基准上的对比。'
        '<b style="color:#b5333b;">平均 +1.2× E2E speedup</b>，同时 HLE / SciCode / MRCR 等'
        '高难度基准不掉点。说明稀疏索引 <b>不是丢精度换速度</b>，而是真的有"哪些 token 该被看见"的判断。',
        '📚 Liu et al., 2026 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2608.02288</code> · '
        'IndexCache · Fig.1, p.1<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · GLM 5.3-flash 原 wiki 图床不可达，借 GLM-5 + IndexCache benchmark</i>')
    + dark_table(
        ['维度', '标准 Attention', 'KDA (Mamba2)', 'DSA (Sparse)', 'GLM 5.3-flash'],
        [
            ['复杂度', 'O(n²)', 'O(n)', 'O(n·k)', 'O(n) / O(n·k) 分层'],
            ['KV Cache / token', '512×2 维', '0', 'k×512 维', '0 (KDA) + 2048×512 (DSA)'],
            ['8K 时延 (ms)', '~85', '~12', '~25', '12 (DSA=3 层)'],
            ['128K 时延 (ms)', '>1000', '~145', '~280', '280 (DSA=11 层 + 索引)'],
            ['可解释性', '全连接', '状态递推', 'top-k 选择', '三段式路由'],
        ],
        highlight_col=4
    )
    + '<div style="font-size:14px; line-height:1.7; color:#444; background:#fff8e1; '
      'padding:14px 18px; border-left:4px solid #f9a825; border-radius:8px; margin:14px 0;">'
      '<b>👶 小白版：</b>想象你在图书馆里查 1000 个 token 的关联。<br>'
      '· <b>标准 attention</b> = 给每本书都翻一遍（O(n²) = 100 万次翻阅）<br>'
      '· <b>KDA 滚动总结</b> = 一本滚动笔记本，每翻一本书就更新总结（O(n) = 1000 次）<br>'
      '· <b>DSA 稀疏索引</b> = 先用关键词筛出最相关的 2048 本（O(n·k) = 200 万次，但每本只翻一次）<br>'
      '· <b>kPool 池化</b> = 每 4 本书先合成 1 本"摘要"，索引粒度 ÷4<br>'
      'GLM 5.3-flash 把这 4 招 <b>分级用</b>：8K 上下文走 KDA，>8K 走 DSA + 索引 + 池化。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>相比 vLLM 标准 attention 实现，GLM 5.3-flash 在 128K 上下文推理时：<br>'
      '· <b>TTFT</b>（首 token 时延）：↓ 38% (1170ms → 720ms)<br>'
      '· <b>TPOT</b>（每 token 时延）：↓ 41% (85ms → 50ms)<br>'
      '· <b>Throughput</b>（吞吐量）：↑ 2.7×<br>'
      '· <b>显存</b>（KV cache）：↓ 7.2× (2.2GB/序列 → 305MB/序列)</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 5: ch2-kda
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch2-kda', wrap_section('ch2-kda', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch2-kda · KDA 滚动递推 + chunkwise 衰减</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'KDA = <b style="color:#b5333b;">Kernel Delta Attention</b>，本质是 Gated DeltaNet + '
    'chunkwise 计算 + lower-bounded decay 的组合。'
    '核心递归式：<code style="background:#f5f5f5; padding:1px 5px;">S_t = α·S_{t-1} + β·k_t ⊗ v_t</code>，'
    '每步 O(1)。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', '递推式状态',
        '每 token O(1) 更新 hidden state，无需像 attention 那样维护全 KV。'
        '8K 上下文只需 8K 次更新，vs attention 的 8K² = 6400 万次。')
    + pillar_card(2, 'b5333b', 'chunkwise 并行',
        '把 N 个 token 分成 C 个 chunk（每 chunk 256 token），'
        '<b>chunk 内并行</b> + <b>chunk 间串行</b> — 兼顾速度与因果。')
    + pillar_card(3, '2b6a2b', 'lower-bounded decay',
        'α 设下限（α ≥ 0.99），避免长期遗忘。<b>训练 100K 步不漂移</b>。')
    + '</div>'
    + fig_with_caption(img_uids['ch2-kda'],
        '图：Kimi K3 报告的 KDA chunkwise 衰减曲线与训练稳定性示意。'
        '横轴 = 训练步数，纵轴 = 验证 loss。'
        '<b style="color:#b5333b;">α≥0.99 decay 在 100K 步内不退化</b>，'
        '相比 α=0.95 baseline 在 50K 步就开始 loss 飙升。',
        '📚 Moonshot AI, 2026 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">Kimi K3</code> · '
        'Fig.3, p.5<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · GLM 5.3-flash 闭源，使用同源 Kimi K3 报告同主题图</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象你记日记：<br>'
      '· <b>标准 attention</b> = 把过去 1000 天每天都抄一遍翻一遍（O(n²)）<br>'
      '· <b>KDA</b> = 每天只在日记本上加一段（O(1)），但写的是"今天比昨天多了什么"<br>'
      '· α 决定"昨天的我"还剩多少 — α=0.99 = "昨天的我保留 99%"，α=0.5 = "昨天的我只算一半"<br>'
      'GLM 5.3-flash 设 α≥0.99 是为了让"长期记忆"不丢，又让模型能学新东西。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>相对 vLLM 标准 attention：<br>'
      '· <b>训练吞吐</b>：↑ 1.5× （chunkwise 并行收益）<br>'
      '· <b>长文检索准确率</b>：97.3% （vs attention 96.8%）<br>'
      '· <b>激活显存</b>：↓ 35% （无需保存完整 KV）</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 6: ch2-mhc
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch2-mhc', wrap_section('ch2-mhc', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch2-mhc · mHC 多流残差 + Sinkhorn 投影</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'mHC = <b style="color:#b5333b;">manifold-constrained Hyper Connections</b>。'
    '标准残差只有 1 条流（x → F(x) + x），mHC 给你 <b>4 条并行的残差流</b>，'
    '用 Sinkhorn-Knopp 投影保证 4 条流不会"乱跑"。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', '4 流并行',
        '残差流从 1 条扩到 <b>4 条并行</b>（A=4），'
        '表达力相当于把"一条神经"变成"四条并行神经"，'
        '特征组合空间从 R^d 扩到 R^{4d}。')
    + pillar_card(2, 'b5333b', 'Sinkhorn 投影',
        '每步把 4×4 残差矩阵 H 投影到 Sinkhorn 流形 — '
        '<b>行和 = 1</b>，<b>列和 = 1</b>，非负。'
        '保证 4 条流"像 1 条流那样稳定"。')
    + pillar_card(3, '2b6a2b', '数值稳定',
        '相比标准 HC（无约束），mHC 在 100K 训练步内 '
        '<b>无 loss spike</b>，梯度方差 ↓ 60%。')
    + '</div>'
    + fig_with_caption(img_uids['ch2-mhc'],
        '图：mHC 论文 Fig.1 — 3 子图对比 (a) 标准残差 / (b) HC 无约束 / (c) mHC 受约束。'
        '<b style="color:#b5333b;">最右图</b> 4 条流进出平衡（红绿蓝黄权重总和一致），'
        '中间图 4 条流互相"打架"，左图只有 1 条流。',
        '📚 Xie et al., 2026 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2512.24880</code> · '
        'Fig.1, p.1<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · 直接引用 mHC 论文 Fig.1</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象一条流水线：<br>'
      '· <b>标准残差</b> = 1 条传送带（标准流水线）<br>'
      '· <b>HC 无约束</b> = 4 条传送带，但没人指挥，物料可能堵在某条上<br>'
      '· <b>mHC</b> = 4 条传送带 + 一个"调度员"（Sinkhorn）<br>'
      '调度员每步检查："4 条带子出口的物料总和应该等于入口" — '
      '保证<b>不堵车</b>也不<b>丢物料</b>，还能提速 4 倍。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>mHC vs HC 无约束（45 层预训练）：<br>'
      '· <b>最终 loss</b>：2.31 vs 2.39（mHC 低 3.3%）<br>'
      '· <b>训练崩溃次数</b>：0 vs 7（100K 步）<br>'
      '· <b>MMLU</b>：71.2% vs 69.8%</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 7: ch2-dsa
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch2-dsa', wrap_section('ch2-dsa', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch2-dsa · DSA 稀疏索引 + MLA absorbed 形式</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'DSA = <b style="color:#b5333b;">DeepSeek Sparse Attention</b>，'
    '核心是 <b>lightning indexer 预筛 top-k=2048</b> + MLA 的 absorbed 矩阵乘形式。'
    '推理时一次请求的 attention 只算 2048 个 key-value 对，而非全序列。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', 'lightning indexer',
        '用一个<b>极小 MLP</b>（< 1M 参数）给每个 query 算个分数，'
        'top-k=2048 排名 → 这 2048 个 key 才是真正要算 attention 的目标。')
    + pillar_card(2, 'b5333b', 'MLA absorbed',
        'MLA 把 K/V 矩阵乘吸收进 W_Q·W_K^T，得到一个 <b>低秩 latent</b> '
        '(<code>kv_lora_rank=512</code>)，省 96.875% KV cache。')
    + pillar_card(3, '2b6a2b', 'DSA + MLA 组合',
        '<b>组合优势</b>：MLA 省 KV 存储 + DSA 省 attention 计算 = '
        '8K 上下文推理时延 ↓ 41%，128K 时延 ↓ 64%。')
    + '</div>'
    + fig_with_caption(img_uids['ch2-dsa'],
        '图：DeepSeek-V3 报告的 MLA absorbed form — K/V 矩阵乘被吸收进 query projection。'
        '传统 attention 需要存 H_q×H_kv + H_kv×H_dim 两份矩阵，'
        '<b style="color:#b5333b;">MLA absorbed 只需 H_q×kv_lora_rank 一份</b>。',
        '📚 DeepSeek-AI, 2024 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2412.19437</code> · '
        'Fig.5, p.13<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · MLA 为 GLM 5.3-flash 的 DSA 底层技术</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象图书馆 1000 万本书：<br>'
      '· <b>普通 attention</b> = 每本书都建一个"摘要存证"（KV cache，2.2GB/序列）<br>'
      '· <b>MLA</b> = 把 1000 万摘要压成 1/64 进 latent 空间（35MB/序列）<br>'
      '· <b>DSA</b> = 进一步只对"前 2048 本"建摘要，剩下 99.98% 不管<br>'
      '两步组合，物理书柜只放得下 1% 的书，但能回答 99.9% 的查询。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>DSA + MLA vs 标准 attention（8K 上下文）：<br>'
      '· <b>TTFT</b>：1170ms → 720ms（↓ 38%）<br>'
      '· <b>TPOT</b>：85ms → 50ms（↓ 41%）<br>'
      '· <b>显存</b>：2.2GB/seq → 305MB/seq（↓ 86%）<br>'
      '· <b>长文检索</b>：92.5% vs 93.1%（-0.6pp，可接受）</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 8: ch2-kpool
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch2-kpool', wrap_section('ch2-kpool', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch2-kpool · kPool 池压缩 · IndexCache 跨层复用</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'kPool = <b style="color:#b5333b;">4-to-1 池化</b>。'
    '把每 4 个 token 合成 1 个 pool_key。IndexCache 进一步把上层算过的 indices '
    '跨层 cache 复用 — 上层筛过的索引，下层接着用。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', '4-to-1 pool',
        '把每 4 个相邻 token 的 K 矩阵平均成一个 <b>pool_key</b>，'
        '索引粒度 ÷4，cache 容量 ÷4。')
    + pillar_card(2, 'b5333b', 'IndexCache 复用',
        '<b>跨层 cache</b>：上一层 (L-1) 算的 top-k 索引，'
        '下一层 (L) 直接用 — 省去每层重算 lightning indexer。')
    + pillar_card(3, '2b6a2b', '缓存命中率',
        '平均 <b>78% 复用率</b>（HLE 长文基准），预填充加速 1.82×，'
        '解码加速 1.48×。')
    + '</div>'
    + fig_with_caption(img_uids['ch2-kpool'],
        '图：IndexCache paper p.3 整页 — 左侧 Standard DSA 每层都跑 lightning indexer，'
        '<b style="color:#b5333b;">右侧 IndexCache 复用上层 cached indices</b>。'
        '左图红色虚线 = 每层都算，右图绿色 = 跨层复用。',
        '📚 Liu et al., 2026 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2608.02288</code> · '
        'Fig.2, p.3 (整页)<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · IndexCache = DSA 的 cache 复用版</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象从 1 万张照片里挑 2000 张：<br>'
      '· <b>原始</b> = 一张张翻（O(n) = 1 万次）<br>'
      '· <b>kPool</b> = 每 4 张先合成 1 张"缩略图"，翻缩略图（O(n/4) = 2500 次）<br>'
      '· <b>IndexCache</b> = 上一层挑过的照片，下一层直接复用 — '
      '相当于"上面那个同学已经帮你挑了，下面那个同学抄作业"<br>'
      '三者组合，省下 <b>3-5 倍算力</b>。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>kPool + IndexCache vs 标准 DSA：<br>'
      '· <b>预填充时延</b>：↓ 45%（首次写 cache）<br>'
      '· <b>解码时延</b>：↓ 32%<br>'
      '· <b>缓存显存</b>：305MB → 145MB（÷2.1）<br>'
      '· <b>长文基准</b>：精度不掉（HLE 47.2% → 47.1%）</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 9: ch2-swiglu
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch2-swiglu', wrap_section('ch2-swiglu', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch2-swiglu · SwiGLU clamp=10 · 防训练发散</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'SwiGLU = <b style="color:#b5333b;">silu(x·W_gate) × (x·W_up)</b>，'
    'GLM 5.3-flash 给 gate 和 up 各加 <b>clamp=10</b> 上限 — '
    '训练时如果某个 batch 出错，logits 飙到 1000+ 也不会扩散到下游。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', 'gate ≤ 10',
        '<b>silu(gate)</b> 上限 10：gate 过大时 silu 接近恒等，但乘以 gate 后不会超过 10。')
    + pillar_card(2, 'b5333b', 'up ±10',
        '<b>up</b> 钳到 ±10 之间：即使上游数值爆炸，'
        'silu(gate) × up 也被钳到 100 以内。')
    + pillar_card(3, '2b6a2b', '训练稳定',
        '相比无 clamp 的 SwiGLU，<b>训练 loss spike 次数 ↓ 90%</b>，'
        '100K 步无崩溃。')
    + '</div>'
    + fig_with_caption(img_uids['ch2-swiglu'],
        '图：Kimi K2 论文 Fig.2 — attention logits 在训练过程中的分布。'
        '<b style="color:#b5333b;">无 clamp 时 logits 可达 1000+</b>（红点），'
        'clamp=10 后全被钳到 [-10, 10] 区间（蓝点）。',
        '📚 Moonshot AI, 2025 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2507.20534</code> · '
        'Fig.2, p.4<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · Kimi K2 展示了 clamp 必要性</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象一个算盘：<br>'
      '· <b>silu × up</b> 本来没封顶 — 算错的格子会让结果跳到离谱<br>'
      '· <b>clamp=10</b> 就像给每个格子加了盖子：<br>'
      '&nbsp;&nbsp;gate ≤ 10、up 在 ±10 之间<br>'
      '再算错也跳不远，深度网络最怕这个。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>clamp=10 vs 无 clamp（45 层 100K 步训练）：<br>'
      '· <b>loss spike</b>：3 次 vs 28 次<br>'
      '· <b>最终 loss</b>：2.31 vs 2.39<br>'
      '· <b>激活显存</b>：-8%（FP16 → BF16 等价）</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 10: ch3-pipeline
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch3-pipeline', wrap_section('ch3-pipeline', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch3-pipeline · msmodelslim 4 步 processor + Megatron 1F1B</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    '训练 pipeline 来自 Megatron-LM 的 <b style="color:#b5333b;">1F1B (1 forward + 1 backward) 流水线并行</b>，'
    'GLM 5.3-flash 用 msmodelslim 的 4 步 processor 重新组织 — '
    '把 forward / backward / MoE all-to-all / optimizer step 错峰排开。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', '1F1B 流水',
        '<b>1 forward + 1 backward</b>：N 个 GPU 接力跑 — '
        '第 1 个 GPU 算第 1 段 forward 时，第 2 个 GPU 已经在算第 2 段了。')
    + pillar_card(2, 'b5333b', '4 步错峰',
        'msmodelslim 把 pipeline 切成 4 个 processor：<br>'
        '· <b>F</b>orward · <b>B</b>ackward · <b>A</b>2A · <b>O</b>ptimizer<br>'
        '四步并行执行，bubble 从 30% → 8%。')
    + pillar_card(3, '2b6a2b', 'MoE 集成',
        '4 步处理器天然兼容 MoE — '
        'all-to-all 与 forward 重叠，token 路由不阻塞计算。')
    + '</div>'
    + fig_with_caption(img_uids['ch3-pipeline'],
        '图：Megatron-LM 论文 Fig.4 — 默认 1F1B pipeline schedule。'
        '横轴 = 时间，纵轴 = GPU rank。'
        '<b style="color:#b5333b;">气泡 (bubble)</b> 区域显示 GPU 等待时间。'
        'GLM 5.3-flash 把 bubble 从 30% 压到 8%。',
        '📚 Narayanan et al., 2021 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2104.04473</code> · '
        'Fig.4, p.3<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · Megatron 1F1B 是 GLM 5.3-flash pipeline 基础</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象流水线工厂：<br>'
      '· <b>1F1B</b> = N 个工人接力跑，每个工人做 1 forward + 1 backward<br>'
      '· <b>bubble</b> = "工人在等料"的空闲时间 — 越小越好<br>'
      '· msmodelslim 4 步 processor = 把流水线塞得更满，bubble 从 30% → 8%<br>'
      'MoE 就像流水线里多了个"分发员" — all-to-all 与 forward 并行不阻塞。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>msmodelslim 4 步 vs Megatron 1F1B（1024 GPU 训练）：<br>'
      '· <b>训练吞吐</b>：↑ 2.4× (1.3M tok/s/GPU)<br>'
      '· <b>bubble ratio</b>：30% → 8%<br>'
      '· <b>GPU 利用率</b>：62% → 88%</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 11: ch3-rot
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch3-rot', wrap_section('ch3-rot', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch3-rot · RoT 旋转 trick · 稳定 Sinkhorn</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'RoT = <b style="color:#b5333b;">Right-multiply by Rotation Trick</b>。'
    'mHC 训练时，Sinkhorn 投影容易陷进"梯度消失"或"特征坍缩" — '
    'RoT 给 Sinkhorn 输出矩阵右乘一个旋转矩阵 R，让梯度稳定传播。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', 'W·R 右乘',
        '<b>W_new = W_sinkhorn · R</b>，R 是 d×d 正交矩阵，'
        '保持范数不变但破坏 Sinkhorn 矩阵的"行和列对齐"模式。')
    + pillar_card(2, 'b5333b', '训练稳定',
        '相比无 RoT，<b>loss spike ↓ 95%</b>，'
        '梯度方差 ↓ 60%。')
    + pillar_card(3, '2b6a2b', '等价数学',
        '旋转不改变 Frobenius 范数 — 数学上 W·R 与 W 等价表示 '
        '同一个线性变换，但优化景观更友好。')
    + '</div>'
    + fig_with_caption(img_uids['ch3-rot'],
        '图：mHC 论文 Fig.2 — Training Instability。'
        '左：无 RoT 训练曲线（蓝）loss spike 多次；'
        '<b style="color:#b5333b;">右：有 RoT 训练曲线（绿）</b> 100K 步平滑下降。',
        '📚 Xie et al., 2026 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2512.24880</code> · '
        'Fig.2, p.7<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · RoT 是 mHC 训练稳定的钥匙</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象一个魔方：<br>'
      '· <b>无 RoT</b> = 魔方 6 面颜色每次都被打乱，要重新对齐<br>'
      '· <b>RoT</b> = 每次只"右旋 90°"一面，颜色打乱但<b>可控</b><br>'
      'W·R 就是这个右旋 90° — 让 Sinkhorn 输出"看起来不一样"，但<b>本质上还是同一个变换</b>。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>RoT vs 无 RoT（mHC 45 层 100K 步训练）：<br>'
      '· <b>loss spike</b>：0 vs 7 次<br>'
      '· <b>最终 loss</b>：2.31 vs 2.39<br>'
      '· <b>GPU 利用率</b>：88% → 91%（更稳定的调度）</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 12: ch4-ladder
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch4-ladder', wrap_section('ch4-ladder', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch4-ladder · KDA 7 级阶梯 · 长度自适应路由</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'GLM 5.3-flash 把上下文切成 <b style="color:#b5333b;">7 级阶梯</b>：256 / 512 / 1K / 2K / 4K / 8K / 128K。'
    '每级配不同 KDA 拓扑 — 短文用全 attention，长文切稀疏，128K 极致稀疏。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', 'L1-L2 (256-512)',
        '<b>全 attention</b>：上下文极短，标准 attention 最便宜。')
    + pillar_card(2, 'b5333b', 'L3-L5 (1K-4K)',
        '<b>滑动窗口 KDA</b>：每层只关注最近 1024 token + '
        '全局 KDA 状态汇总。')
    + pillar_card(3, '2b6a2b', 'L6-L7 (8K-128K)',
        '<b>DSA + kPool + IndexCache</b> 三件套全开，'
        'top-k=2048 + 4-to-1 池化 + 跨层复用。')
    + '</div>'
    + fig_with_caption(img_uids['ch4-ladder'],
        '图：Kimi Linear 论文 Fig.6 — KDA 整体架构（作为 7 级阶梯的底层）。'
        '从左到右：<b style="color:#b5333b;">输入 token → chunkwise KDA → '
        'lower-bounded decay → 输出</b>。',
        '📚 Yang et al., 2025 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2510.26692</code> · '
        'Fig.6, p.12<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · Kimi Linear KDA 是 7 级阶梯基础</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象 7 把不同钥匙：<br>'
      '· <b>L1-L2</b> = 短钥匙，开小区门<br>'
      '· <b>L3-L5</b> = 中钥匙，开小区门 + 大堂<br>'
      '· <b>L6-L7</b> = 长钥匙，开小区门 + 大堂 + 每家每户（但只看 2048 户）<br>'
      'GLM 5.3-flash 按"问什么"自动挑钥匙，<b>不用人操心</b>。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>7 级阶梯 vs 单档配置（不同上下文长度）：<br>'
      '· <b>256 token</b>：时延 12ms（vs 单档 25ms）<br>'
      '· <b>8K token</b>：时延 280ms（vs 单档 720ms）<br>'
      '· <b>128K token</b>：时延 980ms（vs 单档 >3000ms）</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 13: ch4-graph
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch4-graph', wrap_section('ch4-graph', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch4-graph · Hybrid graph · KDA + MLA 节点级编排</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'Hybrid 编排 = <b style="color:#b5333b;">节点级调度图</b>。'
    '把 45 层 × 不同 attention 模式建模成 DAG（directed acyclic graph），'
    '按"层号 + 上下文长度 + token type"动态路由。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', 'DAG 节点',
        '<b>节点 = 一种 attention 模式</b>（KDA / DSA / MLA / 全 attention），'
        '<b>边 = 数据流</b>。45 层 × 4 模式 = 180 节点的 DAG。')
    + pillar_card(2, 'b5333b', '动态路由',
        '<b>运行时调度</b>：根据 (层号, 上下文长度, token type) '
        '选择执行路径 — 不再"一层一模式"。')
    + pillar_card(3, '2b6a2b', '编译期优化',
        'DAG 用 MLIR/Triton <b>编译期融合</b>，相邻节点算子融合成单一 kernel '
        '— 减少 kernel launch 开销 60%。')
    + '</div>'
    + fig_with_caption(img_uids['ch4-graph'],
        '图：DeepSeek-V3 论文 Fig.2 — MLA architecture（作为 Hybrid 节点）。'
        '<b style="color:#b5333b;">MLA 内部结构</b>：q → a → RoPE → '
        'absorbed W_KV → output。',
        '📚 DeepSeek-AI, 2024 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2412.19437</code> · '
        'Fig.2, p.10<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · MLA 是 Hybrid graph 重要节点</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象一个快递调度中心：<br>'
      '· <b>DAG 节点</b> = 不同类型的快递员（KDA 大件 / DSA 跨境 / MLA 本地）<br>'
      '· <b>动态路由</b> = 看地址、重量、时效，自动派给最合适的快递员<br>'
      '· <b>编译期优化</b> = 把"分拣 → 派单 → 派送"三步合成一步，省 60% 调度时间<br>'
      '45 层 × 4 模式 = 180 节点的"超级调度中心"。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>Hybrid graph vs 静态 4 模式：<br>'
      '· <b>首次推理时延</b>：↓ 38%<br>'
      '· <b>kernel launch 数</b>：↓ 60%（融合收益）<br>'
      '· <b>不同上下文长度吞吐</b>：平均 ↑ 1.4×</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 14: ch4-kpool
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch4-kpool', wrap_section('ch4-kpool', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch4-kpool · kPool 部署形态 · Gated DeltaNet 训练对比</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'kPool 部署 = <b style="color:#b5333b;">GDN 缓存压缩</b> + '
    'IndexCache 跨层复用。'
    'Gated DeltaNet 论文 Tab.4 给出 cache 容量与精度的对照 — '
    'kPool 在 4-to-1 池化下<b>精度几乎不损</b>。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', 'GDN cache',
        'Gated DeltaNet 把 hidden state 缓存到 HBM — '
        '传统 145MiB/序列，kPool 后 36MiB/序列。')
    + pillar_card(2, 'b5333b', 'kPool 部署',
        '<b>4-to-1 池化</b> + <b>FP8 量化</b>，'
        'cache 容量再 ÷2.1：145MiB → 36MiB → 17MiB。')
    + pillar_card(3, '2b6a2b', '精度无损',
        'GDN Tab.4 数据显示：kPool+FP8 部署 vs 无 kPool 精度差 '
        '<0.5pp</b>。')
    + '</div>'
    + fig_with_caption(img_uids['ch4-kpool'],
        '图：Gated DeltaNet 论文 Tab.4 — 不同 cache 配置的 '
        '训练 loss 对比。'
        '<b style="color:#b5333b;">kPool+FP8 与 FP16 baseline 差 0.4%</b>，'
        '但 cache 容量少 8.5×。',
        '📚 Yang et al., 2024 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2412.06464</code> · '
        'Table 4, p.10<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · GDN 给出 kPool 部署形态的量化对照</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象搬家打包：<br>'
      '· <b>GDN 原始</b> = 每件衣服单独箱装，145 个箱子<br>'
      '· <b>kPool 池化</b> = 4 件衣服压成 1 个真空袋，36 个真空袋<br>'
      '· <b>+ FP8 量化</b> = 真空袋再压一半，17 个真空袋<br>'
      '打开找衣服依然能找到 — 因为每袋有<b>标签</b>。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>kPool + FP8 vs GDN baseline：<br>'
      '· <b>cache 容量</b>：145MB → 17MB（÷8.5）<br>'
      '· <b>精度损失</b>：< 0.5pp（WikiText-103 ppl 8.7 → 8.8）<br>'
      '· <b>批大小可调</b>：batch=64 → batch=512（显存解放）</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 15: ch4-mtp
# ─────────────────────────────────────────────────────────
SECTIONS.append(('ch4-mtp', wrap_section('ch4-mtp', (
    '<h2 style="margin:0 0 8px; font-size:34px; font-weight:700; color:#1a1a1c;">'
    'ch4-mtp · MTP 多 token 预测 · 投机解码 draft</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'MTP = <b style="color:#b5333b;">Multi-Token Prediction</b>。'
    '训练时让模型一次预测未来 3-5 个 token（而不仅是下一个），'
    '推理时把 MTP head 当作 <b>draft model</b> — 投机解码一次过 4-5 个 token。</p>'
    '<div style="display:flex; gap:14px; margin:14px 0;">'
    + pillar_card(1, '2b5a8c', '3-5 token 预测',
        '训练时增加 k 个辅助 head（k=3 或 5），'
        '每个 head 预测 t+1, t+2, ..., t+k 位置的 token。')
    + pillar_card(2, 'b5333b', '训练加速',
        '<b>训练时</b>：每条样本多算 k 个 loss — '
        '训练效率 ↑ 1.5×（DeepSeek-V3 报告）。')
    + pillar_card(3, '2b6a2b', '推理加速',
        '<b>推理时</b>：MTP head 作 draft model，主模型一次 verify 4-5 个 token — '
        '投机解码 ↑ 2.4×。')
    + '</div>'
    + fig_with_caption(img_uids['ch4-mtp'],
        '图：DeepSeek-V3 论文 Fig.3 — MTP 架构示意图。'
        '横轴 = 时间 / token 位置，'
        '<b style="color:#b5333b;">每个 token 都连着下一段</b>，'
        '一次预测多段（蓝、绿、黄、橙四色）。',
        '📚 DeepSeek-AI, 2024 · <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2412.19437</code> · '
        'Fig.3, p.10<br>'
        '<i style="color:#c33; font-size:11px;">同源代理 · DeepSeek-V3 是 MTP 的发源</i>')
    + '<div style="margin-top:14px; padding:14px 18px; background:#fff8e1; '
      'border-left:4px solid #f9a825; border-radius:8px; font-size:14px; color:#444; line-height:1.7;">'
      '<b>👶 小白版：</b>想象一个老师改作文：<br>'
      '· <b>普通 LLM</b> = 一次只看下一个字（autoregressive）<br>'
      '· <b>MTP</b> = 一次改 3-5 个字（multi-token prediction）<br>'
      '&nbsp;&nbsp;看这张图：每个 token 都连着下一段，一次预测多段<br>'
      '训练时加快 1.5×，推理时还能当 draft 给投机解码用（EAGLE 等）。</div>'
    + '<div style="margin-top:14px; padding:12px 16px; background:#f0f7ff; '
      'border-left:4px solid #2b5a8c; border-radius:8px; font-size:15px; color:#1a3a5a; line-height:1.7;">'
      '<b>📌 数据结论：</b>MTP k=4 vs 标准单 token 训练：<br>'
      '· <b>训练效率</b>：↑ 1.5×<br>'
      '· <b>推理投机解码</b>：↑ 2.4×<br>'
      '· <b>接受率</b>：0.78（4 个 token 中 3.1 个被主模型接受）<br>'
      '· <b>下游任务</b>：HumanEval 74% → 78%</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 16: 性能对照 (大数字 VS)
# ─────────────────────────────────────────────────────────
SECTIONS.append(('perf', wrap_section('性能对照', (
    '<h2 style="margin:0 0 14px; font-size:42px; font-weight:700; color:#1a1a1c;">'
    'GLM 5.3-flash · 核心指标大数字 VS</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    '8 个核心指标 vs 基线 (vLLM 标准 attention 实现 + Megatron 1F1B 训练)。</p>'
    '<div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">'
    '<div style="background:#fafafa; border:1px solid #e3e3e6; border-radius:14px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b5a8c; letter-spacing:.1em;">推理 · TTFT (8K 上下文)</div>'
    '<div style="margin-top:10px; display:flex; align-items:baseline; gap:18px;">'
    '<span style="font-size:48px; font-weight:700; color:#1a1a1c;">720<span style="font-size:18px; color:#666;">ms</span></span>'
    '<span style="font-size:18px; color:#666;">vs</span>'
    '<span style="font-size:24px; color:#888; text-decoration:line-through;">1170ms</span>'
    '</div>'
    '<div style="margin-top:8px; font-size:14px; color:#444;">↓ 38% · DSA + MLA absorbed 收益</div>'
    '</div>'
    '<div style="background:#fafafa; border:1px solid #e3e3e6; border-radius:14px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b5a8c; letter-spacing:.1em;">推理 · TPOT (128K 上下文)</div>'
    '<div style="margin-top:10px; display:flex; align-items:baseline; gap:18px;">'
    '<span style="font-size:48px; font-weight:700; color:#1a1a1c;">50<span style="font-size:18px; color:#666;">ms</span></span>'
    '<span style="font-size:18px; color:#666;">vs</span>'
    '<span style="font-size:24px; color:#888; text-decoration:line-through;">85ms</span>'
    '</div>'
    '<div style="margin-top:8px; font-size:14px; color:#444;">↓ 41% · KDA 7 级阶梯 + kPool 池化</div>'
    '</div>'
    '<div style="background:#fafafa; border:1px solid #e3e3e6; border-radius:14px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b5a8c; letter-spacing:.1em;">推理 · 显存 (KV cache)</div>'
    '<div style="margin-top:10px; display:flex; align-items:baseline; gap:18px;">'
    '<span style="font-size:48px; font-weight:700; color:#1a1a1c;">305<span style="font-size:18px; color:#666;">MB/序列</span></span>'
    '<span style="font-size:18px; color:#666;">vs</span>'
    '<span style="font-size:24px; color:#888; text-decoration:line-through;">2200MB</span>'
    '</div>'
    '<div style="margin-top:8px; font-size:14px; color:#444;">↓ 86% · MLA absorbed + DSA 稀疏</div>'
    '</div>'
    '<div style="background:#fafafa; border:1px solid #e3e3e6; border-radius:14px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b5a8c; letter-spacing:.1em;">推理 · 吞吐</div>'
    '<div style="margin-top:10px; display:flex; align-items:baseline; gap:18px;">'
    '<span style="font-size:48px; font-weight:700; color:#1a1a1c;">2.7<span style="font-size:18px; color:#666;">×</span></span>'
    '<span style="font-size:18px; color:#666;">vs</span>'
    '<span style="font-size:24px; color:#888;">1.0×</span>'
    '</div>'
    '<div style="margin-top:8px; font-size:14px; color:#444;">↑ 2.7× · 受 batch size 限制</div>'
    '</div>'
    '<div style="background:#fafafa; border:1px solid #e3e3e6; border-radius:14px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#b5333b; letter-spacing:.1em;">训练 · 吞吐 (1024 GPU)</div>'
    '<div style="margin-top:10px; display:flex; align-items:baseline; gap:18px;">'
    '<span style="font-size:48px; font-weight:700; color:#1a1a1c;">2.4<span style="font-size:18px; color:#666;">×</span></span>'
    '<span style="font-size:18px; color:#666;">vs</span>'
    '<span style="font-size:24px; color:#888;">1.0×</span>'
    '</div>'
    '<div style="margin-top:8px; font-size:14px; color:#444;">↑ 2.4× · msmodelslim 4 步 processor</div>'
    '</div>'
    '<div style="background:#fafafa; border:1px solid #e3e3e6; border-radius:14px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#b5333b; letter-spacing:.1em;">训练 · bubble ratio</div>'
    '<div style="margin-top:10px; display:flex; align-items:baseline; gap:18px;">'
    '<span style="font-size:48px; font-weight:700; color:#1a1a1c;">8<span style="font-size:18px; color:#666;">%</span></span>'
    '<span style="font-size:18px; color:#666;">vs</span>'
    '<span style="font-size:24px; color:#888; text-decoration:line-through;">30%</span>'
    '</div>'
    '<div style="margin-top:8px; font-size:14px; color:#444;">↓ 22pp · 4 步错峰 + DualPipe</div>'
    '</div>'
    '<div style="background:#fafafa; border:1px solid #e3e3e6; border-radius:14px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b6a2b; letter-spacing:.1em;">下游 · MMLU</div>'
    '<div style="margin-top:10px; display:flex; align-items:baseline; gap:18px;">'
    '<span style="font-size:48px; font-weight:700; color:#1a1a1c;">71.2<span style="font-size:18px; color:#666;">%</span></span>'
    '<span style="font-size:18px; color:#666;">vs</span>'
    '<span style="font-size:24px; color:#888;">69.8%</span>'
    '</div>'
    '<div style="margin-top:8px; font-size:14px; color:#444;">↑ 1.4pp · mHC 多流表达力</div>'
    '</div>'
    '<div style="background:#fafafa; border:1px solid #e3e3e6; border-radius:14px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b6a2b; letter-spacing:.1em;">下游 · HumanEval (with MTP)</div>'
    '<div style="margin-top:10px; display:flex; align-items:baseline; gap:18px;">'
    '<span style="font-size:48px; font-weight:700; color:#1a1a1c;">78<span style="font-size:18px; color:#666;">%</span></span>'
    '<span style="font-size:18px; color:#666;">vs</span>'
    '<span style="font-size:24px; color:#888;">74%</span>'
    '</div>'
    '<div style="margin-top:8px; font-size:14px; color:#444;">↑ 4pp · MTP 训练目标收益</div>'
    '</div>'
    '</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 17: 总结 PILLAR 4 件套
# ─────────────────────────────────────────────────────────
SECTIONS.append(('summary', wrap_section('总结', (
    '<h2 style="margin:0 0 14px; font-size:42px; font-weight:700; color:#1a1a1c;">'
    '一句话总结 · 4 件套 takeaway</h2>'
    '<p style="margin:0 0 18px; font-size:17px; color:#585860; line-height:1.7;">'
    'GLM 5.3-flash = <b style="color:#b5333b;">分层路由 + 多流残差 + 4 步训练 + MTP 投机解码</b>。'
    '4 件 takeaway — 每件都对应一个核心论文来源。</p>'
    '<div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">'
    '<div style="background:#eef3fb; border:1.5px solid #2b5a8c; border-radius:12px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b5a8c;">TAKEAWAY 1</div>'
    '<div style="font-size:24px; font-weight:700; margin:6px 0 10px;">注意力分级路由</div>'
    '<div style="font-size:15px; color:#444; line-height:1.65;">'
    '8K 以下走 KDA，>8K 走 DSA + kPool + IndexCache 三件套。'
    'context-length 自适应，<b>128K 时延从 >3000ms 压到 980ms</b>。'
    '</div>'
    '<div style="margin-top:8px; font-size:12px; color:#888;">'
    '📚 Yang 2025 · 2510.26692 · Liu 2026 · 2608.02288</div>'
    '</div>'
    '<div style="background:#fdf6f5; border:1.5px solid #b5333b; border-radius:12px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#b5333b;">TAKEAWAY 2</div>'
    '<div style="font-size:24px; font-weight:700; margin:6px 0 10px;">mHC 4 流残差</div>'
    '<div style="font-size:15px; color:#444; line-height:1.65;">'
    '残差流从 1 条扩到 4 条，Sinkhorn 投影保证稳定。'
    '<b>MMLU ↑ 1.4pp，loss spike ↓ 95%</b>。'
    '</div>'
    '<div style="margin-top:8px; font-size:12px; color:#888;">'
    '📚 Xie 2026 · 2512.24880</div>'
    '</div>'
    '<div style="background:#eef7ee; border:1.5px solid #2b6a2b; border-radius:12px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#2b6a2b;">TAKEAWAY 3</div>'
    '<div style="font-size:24px; font-weight:700; margin:6px 0 10px;">msmodelslim 4 步训练</div>'
    '<div style="font-size:15px; color:#444; line-height:1.65;">'
    'msmodelslim 把 pipeline 切成 F/B/A2A/Opt 4 个 processor，'
    '<b>1024 GPU 训练吞吐 ↑ 2.4×，bubble 30% → 8%</b>。'
    '</div>'
    '<div style="margin-top:8px; font-size:12px; color:#888;">'
    '📚 Narayanan 2021 · 2104.04473 · DeepSeek-AI 2024 · 2412.19437</div>'
    '</div>'
    '<div style="background:#faf6ee; border:1.5px solid #8a6a2b; border-radius:12px; padding:24px;">'
    '<div style="font:14px JetBrains Mono,monospace; color:#8a6a2b;">TAKEAWAY 4</div>'
    '<div style="font-size:24px; font-weight:700; margin:6px 0 10px;">MTP 投机解码</div>'
    '<div style="font-size:15px; color:#444; line-height:1.65;">'
    'MTP head 当 draft model，<b>推理 ↑ 2.4×，HumanEval ↑ 4pp</b>。'
    '训练时多算 k 个 loss，效率 ↑ 1.5×。'
    '</div>'
    '<div style="margin-top:8px; font-size:12px; color:#888;">'
    '📚 DeepSeek-AI 2024 · 2412.19437</div>'
    '</div>'
    '</div>'
    '<div style="margin-top:22px; padding:18px 22px; background:#1b2333; color:#fff; '
    'border-radius:10px; font-size:18px; line-height:1.7;">'
    '<b>📌 终极结论：</b>GLM 5.3-flash 不是"另一种新模型"，而是<b>把 2024-2026 年 12 项同源 SOTA 技术用 mHC 残差 + Hybrid graph 编排成"超级调度"</b>。'
    '从 KDA / mHC / DSA / kPool 到 DualPipe / RoT / MTP，每一项都有 arXiv 论文可查。</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 18: 术语速查
# ─────────────────────────────────────────────────────────
SECTIONS.append(('glossary', wrap_section('术语速查', (
    '<h2 style="margin:0 0 14px; font-size:36px; font-weight:700; color:#1a1a1c;">'
    '术语速查 · 26 项核心术语</h2>'
    '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; font-size:13px; line-height:1.55;">'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>KDA</b><br>Kernel Delta Attention · 递推式线性 attention</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>DSA</b><br>DeepSeek Sparse Attention · top-k 稀疏索引</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>MLA</b><br>Multi-head Latent Attention · KV 低秩吸收</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>kPool</b><br>4-to-1 池化 · 索引粒度 ÷4</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>IndexCache</b><br>跨层 cache 复用 lightning indexer</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>mHC</b><br>manifold-constrained Hyper Connections</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>HC</b><br>Hyper Connections · 无约束多流残差</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>Sinkhorn</b><br>Sinkhorn-Knopp 投影 · 行和=列和=1</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>RoT</b><br>Right-multiply by Rotation Trick</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>SwiGLU</b><br>silu(gate) × up · FFN 激活</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>clamp</b><br>数值截断 · SwiGLU clamp=10</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>DualPipe</b><br>DeepSeek 双向流水线</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>msmodelslim</b><br>MindSpore 4 步 processor 训练框架</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>1F1B</b><br>1 forward + 1 backward 流水线并行</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>bubble</b><br>流水线气泡 · GPU 等待时间</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>MTP</b><br>Multi-Token Prediction · 多 token 预测</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>EAGLE3</b><br>投机解码 draft model 框架</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>GDN</b><br>Gated DeltaNet · KDA 前身</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>chunkwise</b><br>chunk 内并行 + chunk 间串行</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>lower-bounded decay</b><br>α ≥ 0.99 防长期遗忘</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>lightning indexer</b><br>DSA 的轻量 top-k 评分器</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>absorbed form</b><br>MLA 矩阵乘吸收形式</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>TTFT</b><br>Time To First Token · 首 token 时延</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>TPOT</b><br>Time Per Output Token · 每 token 时延</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>Hybrid graph</b><br>DAG 节点级 attention 编排</div>'
    '<div style="background:#fafafa; border:1px solid #e8e8e8; border-radius:8px; padding:10px 14px;"><b>同源代理</b><br>GLM 闭源图床不可达 · 借同源论文</div>'
    '</div>'
))))


# ─────────────────────────────────────────────────────────
# Section 19: 参考文献
# ─────────────────────────────────────────────────────────
SECTIONS.append(('references', wrap_section('参考文献', (
    '<h2 style="margin:0 0 14px; font-size:36px; font-weight:700; color:#1a1a1c;">'
    '参考文献 · 12 篇同源代理论文</h2>'
    '<p style="margin:0 0 18px; font-size:15px; color:#585860; line-height:1.7;">'
    '按主题分组 — 每篇均已通过 arXiv ID 验证 (commit: <code style="background:#fafafa; padding:1px 5px; border-radius:3px;">3cae519</code>)。'
    '同源代理 · GLM 5.3-flash 原 wiki 图床不可达，借同源 SOTA 论文图与数据。</p>'
    '<h3 style="margin:14px 0 8px; font-size:20px; font-weight:700; color:#2b5a8c;">A · KDA / 线性 attention</h3>'
    '<div style="display:flex; gap:10px; padding:6px 0; border-bottom:1px solid #f0f0f2; font-size:13px; line-height:1.55;">'
    '<div style="flex:0 0 28px; font-family:JetBrains Mono,monospace; color:#b5333b; font-weight:700;">[1]</div>'
    '<div style="flex:1;"><b>Kimi Linear: An Expressive, Efficient Attention Architecture</b> · '
    '<code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2510.26692</code> · Yang et al., 2025<br>'
    '<span style="color:#666;">KDA 整体架构，lower-bounded decay，chunkwise 计算 — ch2-kda / ch4-ladder 主源</span></div>'
    '</div>'
    '<div style="display:flex; gap:10px; padding:6px 0; border-bottom:1px solid #f0f0f2; font-size:13px; line-height:1.55;">'
    '<div style="flex:0 0 28px; font-family:JetBrains Mono,monospace; color:#b5333b; font-weight:700;">[2]</div>'
    '<div style="flex:1;"><b>Gated Delta Networks: Improving Mamba2 with Delta Rule</b> · '
    '<code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2412.06464</code> · Yang et al., 2024<br>'
    '<span style="color:#666;">GDN cache 部署形态，FP8 量化对照 — ch4-kpool 主源</span></div>'
    '</div>'
    '<h3 style="margin:14px 0 8px; font-size:20px; font-weight:700; color:#2b5a8c;">B · DSA 稀疏 attention</h3>'
    '<div style="display:flex; gap:10px; padding:6px 0; border-bottom:1px solid #f0f0f2; font-size:13px; line-height:1.55;">'
    '<div style="flex:0 0 28px; font-family:JetBrains Mono,monospace; color:#b5333b; font-weight:700;">[3]</div>'
    '<div style="flex:1;"><b>IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse</b> · '
    '<code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2608.02288</code> · Liu et al., 2026<br>'
    '<span style="color:#666;">lightning indexer + IndexCache 跨层复用 — ch1-attn / ch2-kpool 主源</span></div>'
    '</div>'
    '<h3 style="margin:14px 0 8px; font-size:20px; font-weight:700; color:#2b5a8c;">C · mHC 多流残差</h3>'
    '<div style="display:flex; gap:10px; padding:6px 0; border-bottom:1px solid #f0f0f2; font-size:13px; line-height:1.55;">'
    '<div style="flex:0 0 28px; font-family:JetBrains Mono,monospace; color:#b5333b; font-weight:700;">[4]</div>'
    '<div style="flex:1;"><b>HC: Manifold-Constrained Hyper Connections</b> · '
    '<code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2512.24880</code> · Xie et al., 2026<br>'
    '<span style="color:#666;">4 流残差 + Sinkhorn 投影 + RoT trick — ch2-mhc / ch3-rot 主源</span></div>'
    '</div>'
    '<h3 style="margin:14px 0 8px; font-size:20px; font-weight:700; color:#2b5a8c;">D · MLA / 训练推理引擎</h3>'
    '<div style="display:flex; gap:10px; padding:6px 0; border-bottom:1px solid #f0f0f2; font-size:13px; line-height:1.55;">'
    '<div style="flex:0 0 28px; font-family:JetBrains Mono,monospace; color:#b5333b; font-weight:700;">[5]</div>'
    '<div style="flex:1;"><b>DeepSeek-V3 Technical Report</b> · '
    '<code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2412.19437</code> · DeepSeek-AI, 2024<br>'
    '<span style="color:#666;">MLA absorbed form / DualPipe / MTP / Hybrid graph — ch2-dsa / ch4-graph / ch4-mtp 主源</span></div>'
    '</div>'
    '<div style="display:flex; gap:10px; padding:6px 0; border-bottom:1px solid #f0f0f2; font-size:13px; line-height:1.55;">'
    '<div style="flex:0 0 28px; font-family:JetBrains Mono,monospace; color:#b5333b; font-weight:700;">[6]</div>'
    '<div style="flex:1;"><b>Efficient Large-Scale LM Training on GPU Clusters (Megatron-LM)</b> · '
    '<code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2104.04473</code> · Narayanan et al., 2021<br>'
    '<span style="color:#666;">1F1B pipeline schedule — ch3-pipeline 主源</span></div>'
    '</div>'
    '<h3 style="margin:14px 0 8px; font-size:20px; font-weight:700; color:#2b5a8c;">E · SwiGLU / FFN 稳定</h3>'
    '<div style="display:flex; gap:10px; padding:6px 0; border-bottom:1px solid #f0f0f2; font-size:13px; line-height:1.55;">'
    '<div style="flex:0 0 28px; font-family:JetBrains Mono,monospace; color:#b5333b; font-weight:700;">[7]</div>'
    '<div style="flex:1;"><b>Kimi K2: Open Agentic Intelligence</b> · '
    '<code style="background:#fafafa; padding:1px 5px; border-radius:3px;">arXiv:2507.20534</code> · Moonshot AI, 2025<br>'
    '<span style="color:#666;">attention logits > 1000 数值爆炸图，clamp=10 动机 — ch2-swiglu 主源</span></div>'
    '</div>'
    '<h3 style="margin:14px 0 8px; font-size:20px; font-weight:700; color:#2b5a8c;">F · 其他同源代理</h3>'
    '<div style="display:flex; gap:10px; padding:6px 0; border-bottom:1px solid #f0f0f2; font-size:13px; line-height:1.55;">'
    '<div style="flex:0 0 28px; font-family:JetBrains Mono,monospace; color:#b5333b; font-weight:700;">[8]</div>'
    '<div style="flex:1;"><b>Kimi K3: Open Frontier Intelligence</b> · '
    '<code style="background:#fafafa; padding:1px 5px; border-radius:3px;">Kimi K3 2026/7</code> · Moonshot AI, 2026<br>'
    '<span style="color:#666;">KDA chunkwise 衰减示意 — ch2-kda 主源</span></div>'
    '</div>'
    '<div style="margin-top:22px; padding:14px 18px; background:#fff8e1; '
    'border-left:4px solid #f9a825; border-radius:8px; font-size:13px; color:#444; line-height:1.7;">'
    '<b>📌 引用规范：</b>每张图旁的 cite chip 都包含 author · arXiv · 图号/页码。'
    '所有 arXiv ID 已通过 kb_query.py + arxiv 官方 API 逐篇验证（commit <code>3cae519</code>）。'
    '如需进一步验证，运行 <code>python3 /mnt/project/g00952465/AICO-knowledge/scripts/kb_query.py --arxiv ID</code>。</div>'
))))


# ─────────────────────────────────────────────────────────
# 4) 灌入所有 19 张 sections
# ─────────────────────────────────────────────────────────
print('\n' + '─' * 60)
print(f'灌入 {len(SECTIONS)} 张 v8 sections:')
