# Beyond Ten Turns — 技术点深读（DEEP 2026-08-18, rewrite；2026-08-20 全文回填增强）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with Large-Scale Asynchronous RL · arXiv:2508.07976v4 (26 Oct 2025)
> 作者：Jiaxuan Gao, Wei Fu, Minyang Xie, Shusheng Xu, Chuyi He, Zhiyu Mei, Banghua Zhu, Yi Wu · IIIS Tsinghua + Ant Group + UW
> 开源：https://github.com/inclusionAI/ASearcher（模型、训练数据、代码全开源）
> 数据源声明：**全文已回填（67271 字符，覆盖正文页 2–21，含 Table 1/2/3/4/5、§3.4 GRPO Eq.1、训练配置、合成数据统计、Appendix A 完整 case study）。** 9 张图 M3 caption 已补（p01/p03/p04/p07/p09/p10/p14/p15/p16/p20，其中 p15 同时覆盖 Fig.9 与 Fig.10）。下文精确数字一律引 fulltext `.txt` 为权威源。论文未给的字段（GRPO 组大小 G、turn-limit 系统消融、7B/14B GPU hours）仍标 not-available，已逐一与全文核对确认确实未给，未臆造。
> 公式源声明：formulas.json 该篇收录 0 条公式。故 GRPO Eq.1 等按 fulltext `.txt` 原文引用，**不渲染 `$$`**（LaTeX 双源校验：formulas.json 空 ↔ .txt 含 Eq.1 伪排版，以 .txt 为准）。
> M3 caption 注：p01（Figure 1）的 M3 caption 误识为 "DEPA / Stage 1 vs Stage 2 / Avg@4"，且 M3 自述 "text is heavily overlapping/garbled ... a clean verbatim transcription is not possible"。该 M3 描述与 Figure 1 实际内容不符，判为不可靠并弃用；Figure 1 解读以 fulltext page 1 verbatim caption + §4.2 为准（见下，并标注 Figure 1 caption 与 §4.2 的数字不一致）。其余 9 张 M3 caption 可靠，已织进相关节。

## 核心问题

ASearcher 攻击的是**开源搜索智能体无法达到 expert-level Search Intelligence** 这一机制级缺陷。Search Intelligence 定义（§1）：在 noisy/conflicting 在线信息下，能 (a) resolve ambiguous queries、(b) generate precise searches、(c) analyze results、(d) conduct thorough exploration。论文用 GAIA 上一道含 **2 conditions / 4 unknown variables**（Appendix A 明确 "given 2 conditions and 4 unknown variables"，U1=species、U2=2021 article、U3.1/U3.2=两人 papers）的题目（"find a specific animal"）做 case study（§2 + Appendix A, Fig.3 / Fig.12）：正确路径要先定位 species U1（条件 C1：genus named for Copenhagen）→ 定位 2021 multicenter randomized double-blind article U2（靠 U1 的 Wikipedia 页引用 + 条件 C2）→ 找出 U3.1/U3.2 的 papers → 跨文档比对得出 "Mice"。其间存在 misleading answer（"pigs"）。作者识别出**两道机制性障碍**：

- **障碍 1 — 现有 online RL 的搜索 turn 上限过低，扼杀复杂策略学习（§1, §2）。** Search-R1 [11] 等人为限定 trajectory 内 search turns ≤ 10；case study 里 Search-R1-32B 训练时 turn limit 仅设 **4**（§2 .txt 原文 "since the turn limit is set as a small value, e.g. 4, during training, the model only exhibits a short tool-use horizon"），导致它无法分解复杂 query、生成 redundant/ambiguous query、严重 hallucinate。即"短 horizon RL → 只学到 elementary search strategy"，且 Search-R1-32B 在 GAIA Avg@4 仅 28.6（Table 4）。复杂 query 的多步推理+多轮工具调用被 turn budget 直接切断。
- **障碍 2 — 缺乏大规模、高质量、高难度的 QA 对（§1, §3.2）。** 现有开源 search-agent 数据集（HotpotQA 等）过时、过简化、过小，无法在 RL 下刺激复杂 search behavior。

更进一步，**prompt-based LLM agent 路线也失败**（§2）：Search-o1(QwQ) 能靠 QwQ-32B 内置 reasoning 做大量 tool calls 找到 U1/U2/U3，但"easily misses key information"、被先前错误结论误导、**无法 verify 错误结论**——即"未经 agentic 训练的开源模型能调工具但做不到 expert-level reasoning over retrieved contents"。最后，offline RL 微调 prompt-based agent 的近作（WebThinker/SimpleDeepSearcher）已被证在更广域下弱于 online RL（§1 引 [43,6,31]）。

机制级根因一句话：**online RL 想解锁 search intelligence，必须同时突破 (i) trajectory 长度上限、(ii) 长 trajectory 引发的 batch 同步 GPU 闲置、(iii) 训练数据难度** —— 三者耦合（§3.3.1 经验验证：复杂任务需长 trajectory；长 trajectory 又导致执行时间方差跨 2 个数量级，传统 batch-generation RL 系统 [one-step-off, ref 21] 必被 batch 内最慢 trajectory 阻塞，见 Fig.7）。

〔Figure 3 / Figure 12 M3 caption 织入〕M3 对 p04（Fig.3）与 p20（Fig.12）的三栏 case study 描述一致：Search-R1-32B（左）无法分解 query、hallucinate（误报 "Pigs/Goats"）；Search-o1(QwQ)（中）能定位 genus 但 miss key info、无法 verify；ASearcher-Web-QwQ（右）走 focused search → key-info extraction → uncertainty-aware source identification → cross-document inference → grounded verification，得正确答案 "Mice"。M3 caption 与 .txt §2/Appendix A 自洽。

## 关键创新点

1. **全异步 agentic RL 训练（built on AReaL [7]），把 turn limit 从 ≤10 放宽到 128（QwQ）/ 32（7B/14B）。** 机制（§3.3.2 + Fig.7）：异步在两个层面 — (a) **Asynchronous Trajectory Rollouts**：各 trajectory 独立并行向 LLM engine 与 tool server 发请求，互不等待；(.txt 原文 "Each trajectory independently sends tool calling requests to corresponding servers and LLM generation requests to the LLM inference engine.") (b) **Decoupled Rollout and Training**：rollout 与 model update 完全解耦，一条 training step 只要 buffer 凑够 batch 即启动，**长 trajectory 不阻塞 generation、可跨越多个 policy version**（Fig.7 中 trajectory 7 慢时，training 直接走 trajectory 9，达到 near-full GPU utilization）。vs one-step-off RL [21]（batch 内仍需等最慢 trajectory，Fig.7 左侧 GPU idle 大）。效果（§1 abstract + §4.2）：RL 训练后 ASearcher-Web-QwQ 在 GAIA/xBench/Frames 上 Avg@4 增益见下方"数字不一致说明"。QwQ 训练动态（§4.3, Fig.6）：峰值 ~40 calls @ 200th step、极值 70 calls、单 trajectory >150k tokens（.txt 原文 "a maximum of over 150k tokens"）。abstract 另称训练时极值 "tool calls exceeding 100 turns and output tokens exceeding 400k"。ASearcher-Web-QwQ 总训练成本 ~16k H800 GPU hours（§4.1 .txt 原文 "Training of ASearcher-Web-QwQ takes approximated 16k H800 GPU hours in total"）。

   **〔Figure 1 / Figure 8 / Figure 6 caption 织入 + 数字不一致说明〕** Figure 1 caption（page 1 verbatim）称 RL 带来 "+15.0, +2.4, and +15.6 improvements on GAIA, xBench, and Frames"；但 §4.2 "Effect of RL Training" 称 "+15.0, +22.4, and +14.6 improvements on GAIA, xBench-DeepSearch and Frames respectively"，Pass@4 在 xBench +24.0。两处不一致：xBench 增益 Figure 1 写 +2.4、§4.2 写 +22.4；Frames 增益 Figure 1 写 +15.6、§4.2 写 +14.6。以 §4.2 + Figure 8（M3, p14）数据为准——Figure 8 M3 caption 佐证 xBench Avg@4 "28.7 → 42.1 → 51.1"（before-RL prompt-agent 28.7 → v1 42.1 → v2 51.1，增益 51.1−28.7=22.4 ✓）、Pass@4 "51.0 → 75.0"（+24.0 ✓）。故 Figure 1 caption 的 "+2.4" 判为 typo（应为 +22.4）、"+15.6" 判为 typo（应为 +14.6）。〔Figure 1 M3 caption 不可靠，已弃用。Figure 8 M3 caption 可靠，已采用。〕

   〔Figure 7 M3 caption 织入〕p10（Fig.7）M3 描述两范式：One-Step-Off RL（上）12 条 trajectory 中 batch 被 Traj 7 阻塞产生 Idle Time；Fully Async RL（下）无同步 barrier，Train Step N/N+1/N+2 一旦凑够 batch 即启动，Traj 7 可跨多个 policy version。与 .txt §3.3.2 一致。

   〔Figure 6 M3 caption 织入〕p09（Fig.6）三面板：(Left) Accuracy（~52–55%）随 enforced minimum tool-call turns（6–12）单调上升；(Middle) #Tool calls vs training step（0–200），MAX ~70 而 AVG ~10；(Right) #Generated tokens（log 10³–10⁵），MAX ~10⁵、MIN ~10³，跨 2 数量级。佐证"长 trajectory 运行时方差极大"。

2. **可规模化 QA 合成 Agent（§3.2.2, Fig.4 / Fig.5）。** 机制：从 seed QA 出发，迭代式地在两种 action 间选择 — **Injection**（选问题中一个 entity，从 Wikipedia 取一条 related fact 注入问题，增加 complexity）+ **Fuzzing**（把精确信息模糊化，如 "Catskill Mountain Railroad"→"a historic mountain railway"，"1934"→"the early 1930s"，增加 uncertainty）。每次修改后跑 3 步 verification：(i) **Basic Quality**（LLM 检 clarity + QA 是否 grounded in supporting facts）；(ii) **Difficulty Measurement**（cutting-edge LRM 如 QwQ-32B 无工具直接答，用作难度标尺）；(iii) **Answer Uniqueness**（检查 fuzz 后是否产生 alternative valid answers）。最后**滤掉 LRM 无工具即可答对的题**。效果（§3.2.2 .txt 精确数字）：**14,107 seed** → 合成 pool 共 **134k** 高质量样本（平均 **6.3 injections + 3.2 fuzzes** per seed）→ 选最多 3 个 variation/seed → **最终 25,624 entries**（平均 **4.27 injections + 2.10 fuzzes**），其中"require external tools for resolution"即 25.6k。开源数据侧（§3.2.1）：HotpotQA + 2WikiMultiHopQA 共 **304k** → 用已训模型每题生成 **16 responses** 后过滤（全错即 16 次均不对 / ≥50% 准确 / ≤1 turn 即可解的都丢）→ 留 **16k challenging samples**；另加 WebWalkerQA [40] 小子集训练真实网页定位能力。两份训练集（7B/14B 与 QwQ）各 **35k**（§4.1 .txt "These two datasets are both of 35k sizes and open-sourced"）。

   〔Figure 4 M3 caption 织入〕p07（Fig.4）M3 描述：Synthetic QA & Facts（左）→ LLM agent → 两个 action 分支（Extract Fact & Inject 顶部 / Select Info. & Fuzz 底部）→ Quality Verification（右）三步序贯检查（Basic Quality → Difficulty Measurement → Answer Uniqueness）→ loop until pass。与 .txt §3.2.2 完全一致。Figure 5（合成统计三面板：supporting facts 数分布 / fuzz+injection 数分布 / QwQ-32B 无工具答题准确率分布）.txt 有 caption 引用但无 M3 caption（p08 未生成），按 .txt 描述引用。

3. **极简 agent 设计 + 端到端 RL（§3.1, Fig.2）。** 仅两个 tool：search engine（输入 query 返回 snippets+URL）+ web browser（输入 URL 返回 page content）；**网页 summarization 也由 agent 自己做，并在 RL 中一并优化**（.txt 原文 "all LLM-generated responses... including thinking, tool calling, and summarization, are trained using RL in an end-to-end manner"）。**不依赖任何 external LM**。两套 instantiation：(a) **base LLMs（Qwen2.5-7B/14B）**——append-only prompting，system prompt 后按时间序 append 所有 responses/search results/webpage summaries；(b) **LRMs（QwQ-32B）**——为不同子任务（tool selection / summarization / answering）分别 prompt；**丢弃 thinking 过程、保留 summarized thoughts + tool calls**；只把**最近 25k characters** 历史喂给 LRM，保证输入 ≤**10k tokens**，为 LRM 留足生成 budget（.txt 精确数字 "only the most recent 25k characters ... input of at most 10k tokens"）。

   〔Figure 2 M3 caption 织入〕p03（Fig.2）M3 描述：Search-R1（左）单 loop：User Query → Trainable LLM Gen → Tool Calling → Search Query → External Search Engine → Top-K Entries，≤10 turns 循环回 Answer；ASearcher（右）双 tool：同一 LLM Gen / Tool Calling 可 dispatch Search tool（→ Search Engine → Top-K Entries）**或** Browser tool（→ Webpage ~100K chars → Summarize ~100 chars），允许 **128 turns**。图例：trainable（蓝 LLM Gen）、external tools（粉）、external info（绿）、tool-calling logic（橙）。与 .txt §3.1 一致。

4. **两阶段 curriculum RL（§4.1）。** Stage 1：混合难度数据（含少量 tool call 即可解的简单题）。Stage 2：**仅保留需要 ≥5 tool calls 才能解的题**（.txt 原文 "retain only the questions that require at least 5 tool calls to solve"），进一步激活 long-horizon 能力。产出 v1/v2 两个 checkpoint。Keyword analysis（§4.4, Fig.11）佐证：reflection 关键词（"alternatively"/"however"/"wait"）训练中持续上升；external-reference 关键词（"doc"/"mention"）在 stage 2（step 200 后）显著上升——agent 学会**refer to external information**。

   〔Figure 11 M3 caption 织入〕p16（Fig.11）M3 描述：左面板 6 个 reflection 关键词（search/alternatively/wait/check/confirm/however），"search" 在 step ~250 后飙升至 ~8k occurrences/traj；右面板 5 个 external-reference 关键词（doc/mention/source/earlier/previous），"doc" 在 step 250 后升至 ~2.5k。两图在 step ~250 同步 inflection，对应 stage 2 启动。与 .txt §4.4 一致。

5. **MDP + GRPO 训练配方（§3.4）。** MDP `(S,A,T,R)`（.txt 原文 "an MDP is defined by the tuple (S; A; T; R)"），action 含可被 tag 提取的 tool call（如 `<search> search query </search>`）。用 GRPO [29]（Eq.1，.txt 原文伪排版，**此处按 .txt 引用不渲染 $$**）：对每个输入 x 生成 G 条 trajectory τ₁..τ_G，loss 为组内 token-level PPO clip + advantage `Â_i` 基于"relative rewards of all trajectories within each group"（.txt 原文）；clip 范围 `[1−ε, 1+ε]`，ε 为超参。**G 的具体值论文未给（全文已核对，§3.4 仅写符号 G，not-available）**——继承 DeepSeek-R1/DeepSeekMath GRPO 路线（弃 GAE + value model）。**Dynamic Filtering**：移除组内 reward 全相同（zero advantage）的 query（含已高准确率题与标错答案题）。**Reward**：base LLM = format reward × F1（乘法组合）；LRM = LLM-as-Judge [20][38]（Qwen2.5-72B-Instruct），**省略 format reward**（LRM 自身能保持格式）。sparse reward，trajectory 完成才结算。

6. **端到端效果（§4.2, Table 4/5, Fig.8）。** ASearcher-Web-QwQ-v2 在 GAIA/xBench-DeepSearch/Frames 上 Avg@4 = **58.7 / 51.1 / 74.5**，Pass@4 = **74.7 / 75.0 / 85.5**——**开源 32B agent SOTA**（次强 Search-o1(QwQ) 48.1/40.3/63.6；SimpleDS-QwQ 47.6/35.8/67.0；WebDancer-QwQ 47.4/40.0/63.8；WebThinker-QwQ 42.5/32.8/57.7；Search-R1-32B 仅 28.6/19.5/44.1；QwQ-32B Direct Gen 23.1/11.8/29.9）。RL 训练带来绝对增益 +15.0（GAIA）/ +22.4（xBench）/ +14.6（Frames）Avg@4（§4.2 权威值，见创新点 1 的不一致说明），Pass@4 在 xBench +24.0（Fig.8）。intro 另报相对增益 xBench **78.0%**、GAIA **34.3%**（.txt 原文 "78.0% and 34.3% improvements on xBench-DeepSearch and GAIA"）。零样本外挂 DeepSeek-V3 做 summarizer → 60.3/56.4/76.6；再叠 K=16 test-time search（用 DeepSeek-V3 聚合）→ **71.8/75.0/83.4**，HLE-500 21.5→23.4→24.6，**逼近 Kimi-Researcher（69.0/78.8/26.9）/ OpenAI DeepResearch（67.0/26.6）/ OpenAI-o3（70.5/66.7/84.0/20.2）/ Claude-4-Sonnet（68.3/64.6/80.7/20.3）/ DeepSeek-R1（55.0/82.0/24.8）/ Qwen3-235B-A22B（45.6/46.0/20.0）/ Qwen3-30B-A3B（35.9/32.0/56.4/13.2）**（Table 5，†为官方报告值）。

7. **RL 训练后 local→web 的 zero-shot 泛化（§4.2, Table 3）。** ASearcher-Local-14B（仅用本地 Wikipedia 2018 RAG 训练）直接放进真实 web 环境 zero-shot 评估，avg F1 60.0 / LasJ 65.6——**超过 SimpleDS-QwQ（58.4/65.3）、Search-o1(QwQ)（55.8/64.9）、Search-R1-32B（60.4/62.5）等所有同/大规模 baseline**，证明 ASearcher 学到的是 source-agnostic 的 search strategy，而非记忆本地库。

8. **7B vs 14B 容量边界（§4.3, Fig.9/10）。** 7B/14B 训练中都观察到 length increment + tool call 增多，search queries 数量上限到 **6**（.txt 原文 "the number of search queries scale up to 6, which is higher than the numbers reported by prior works [11, 30]"）。但 **7B 学不会 webpage browsing**（.txt 原文 "the model capacity is too small to stably learning summarize lengthy webpages in a zero RL training setting"），14B 在训练后期才学会——直接给出"web summarization 这一端到端 RL 能力存在 scale 门槛"。

   〔Figure 9/10 M3 caption 织入〕p15（Fig.9=7B / Fig.10=14B）M3 描述：各三面板 (a) Generated Tokens（7B 上至 1000、14B 上至 800）、(b) Search Queries（0–6）、(c) URL Accesses，红曲线为均值。两模型均现 emergent scaling——tokens 与 search-query 数随训练增长（tokens 呈 U 形：先降后升），说明 RL 自发诱导更长、更 tool-intensive 的推理链。与 .txt §4.3 一致。

## 表格（原文结构化，数字均引 fulltext .txt）

### Table 4 — GAIA / xBench-DeepSearch / Frames 主结果（§4.2, Avg@4 / Pass@4，LLM-as-Judge，baselines 跑 4 seeds）

| Method | GAIA Avg@4 | GAIA Pass@4 | xBench Avg@4 | xBench Pass@4 | Frames Avg@4 | Frames Pass@4 |
|---|---|---|---|---|---|---|
| QwQ-32B Direct Gen. | 23.1 | 31.1 | 11.8 | 23.0 | 29.9 | 39.9 |
| Search-R1-32B | 28.6 | 43.7 | 19.5 | 37.0 | 44.1 | 61.0 |
| WebThinker-QwQ | 42.5 | 57.3 | 32.8 | 52.0 | 57.7 | 79.5 |
| Simple DS-QwQ | 47.6 | 64.1 | 35.8 | 61.0 | 67.0 | 82.2 |
| WebDancer-QwQ | 47.4 | 61.2 | 40.0 | 68.0 | 63.8 | 81.4 |
| Search-o1 (QwQ) | 48.1 | 67.0 | 40.3 | 65.0 | 63.6 | 81.1 |
| **ASearcher-Web-QwQ-v1** | 52.8 | 70.1 | 42.1 | 68.0 | 70.9 | 84.0 |
| **ASearcher-Web-QwQ-v2** | **58.7** | **74.7** | **51.1** | **75.0** | **74.5** | **85.5** |

### Table 5 — Pass@1 + 商业系统对照（§4.2, 零样本外挂 summarizer + K=16 test-time search；†=官方报告）

| Method | GAIA | xBench-DeepSearch | Frames | HLE-500 |
|---|---|---|---|---|
| Kimi-Researcher (commercial) | — | 69.0† | 78.8† | 26.9† |
| OpenAI DeepResearch (commercial) | 67.0† | — | 26.6† | — |
| OpenAI-o3 | 70.5† | 66.7† | 84.0† | 20.2† |
| Claude-4-Sonnet | 68.3† | 64.6† | 80.7† | 20.3† |
| DeepSeek-R1 | — | 55.0† | 82.0† | 24.8† |
| Qwen3-235B-A22B | 45.6† | 46.0† | — | 20.0† |
| Qwen3-30B-A3B | 35.9† | 32.0† | 56.4† | 13.2† |
| ASearcher-Web-QwQ-v2 (single-model) | 58.7 | 51.1 | 74.5 | 21.5 |
| + Summary=DeepSeek-V3 | 60.3 | 56.4 | 76.6 | 23.4 |
| + Test-time Search (K=16) | **71.8** | **75.0** | **83.4** | **24.6** |

### Table 3 — Web-based Search & Browsing（§4.2, Avg F1 / Avg LasJ，含 per-benchmark）

| Method | Training | Setting | 2WikiMQA F1/LasJ | HotpotQA F1/LasJ | Bamboogle F1/LasJ | MuSiQue F1/LasJ | NQ F1/LasJ | TriviaQA F1/LasJ | PopQA F1/LasJ | Avg F1 | Avg LasJ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen-2.5-7B Direct Gen. | — | — | 30.8/30.9 | 28.6/29.5 | 37.2/39.6 | 10.6/1.9 | 29.6/29.9 | 51.2/59.3 | 19.8/17.4 | 29.7 | 29.8 |
| Search-R1-7B | local | local | 58.9/64.8 | 59.0/62.8 | 66.3/73.6 | 29.4/25.4 | 58.4/51.1 | 73.1/84.1 | 53.0/51.3 | 56.9 | 59.0 |
| R1-Searcher-7B | local | local | 66.6/69.4 | 56.8/61.6 | 62.8/72.0 | 28.7/25.3 | 49.6/48.7 | 67.6/79.5 | 46.5/45.2 | 54.1 | 57.4 |
| DeepResearcher-7B | web | web | 61.0/64.1 | 57.1/61.0 | 68.8/76.8 | 26.8/24.5 | 52.0/52.9 | 70.0/82.8 | 48.9/45.7 | 54.9 | 58.3 |
| Simple DS-7B | web | web | 67.4/73.9 | 57.6/62.5 | 61.5/72.0 | 26.4/26.2 | 43.9/53.1 | 73.9/85.4 | 43.7/48.8 | 53.5 | 60.3 |
| ASearcher-Local-7B (zero-shot web) | local | local | 69.1/75.5 | 61.6/67.1 | 66.2/76.0 | 33.3/30.7 | 54.7/53.7 | 75.2/87.3 | 52.9/49.7 | 59.0 | 62.9 |
| ASearcher-Web-7B | web | web | 67.5/73.3 | 61.7/67.2 | 66.4/72.0 | 32.9/29.6 | 55.2/55.4 | 74/85.7 | 52.4/48.9 | 58.6 | 61.7 |
| QwQ-32B Direct Gen. | — | — | 33.7/33.4 | 39.1/42.1 | 56.9/57.9 | 18.8/19.3 | 37.8/43.0 | 63.8/74.2 | 25.9/24.5 | 39.4 | 42.1 |
| Search-o1 (QwQ-32B) | — | — | 68.9/77.8 | 58.4/65.3 | 68.6/82.4 | 31.8/33.5 | 43.1/57.2 | 76.3/89.6 | 43.2/48.3 | 55.8 | 64.9 |
| Search-R1-14B | local | local | 51.8/53.8 | 55.3/58.6 | 67.4/75.2 | 29.8/26.9 | 57.7/49.6 | 74.4/83.9 | 51.0/49.8 | 55.4 | 56.8 |
| Search-R1-32B | local | local | 63.7/69.3 | 60.3/64.2 | 76.4/81.6 | 33.0/30.8 | 58.6/51.1 | 76.2/86.6 | 55.0/53.6 | 60.4 | 62.5 |
| Simple DS-QwQ | web | web | 71.7/80.4 | 62.0/67.5 | 73.2/83.2 | 33.3/32.9 | 45.7/55.3 | 77.2/90.2 | 45.5/47.8 | 58.4 | 65.3 |
| ASearcher-Local-14B (zero-shot web) | local | local | 70.4/79.8 | 63.6/70.5 | 68.7/80.8 | 35.1/33.8 | 53.5/55.4 | 76.1/88.5 | 52.5/50.5 | **60.0** | **65.6** |
| ASearcher-Web-14B | web | web | 76.1/80.7 | 63.5/68.5 | 69.9/75.2 | 36.6/33.7 | 56.0/55.5 | 75.4/87.6 | 52.9/50.0 | **61.5** | 64.5 |

### Table 2 — Local Knowledge Base + RAG（§4.2, Avg F1 / Avg LasJ，含 per-benchmark）

| Method | Scale | 2WikiMQA F1/LasJ | HotpotQA F1/LasJ | Bamboogle F1/LasJ | MuSiQue F1/LasJ | NQ F1/LasJ | TriviaQA F1/LasJ | PopQA F1/LasJ | Avg F1 | Avg LasJ |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen-2.5-7B Direct Gen. | 7B | 30.4/29.4 | 29.2/30.9 | 37.2/42.4 | 11.8/11.0 | 27.9/29.4 | 50.4/59.8 | 21.5/20.5 | 29.8 | 31.9 |
| Search-R1-7B | 7B | 54.7/58.1 | 57.6/60.8 | 55.8/58.4 | 28.2/27.1 | 58.7/49.9 | 68.0/78.0 | 57.3/55.7 | 54.3 | 55.4 |
| R1-Searcher-7B | 7B | 64.0/67.1 | 57.1/61.0 | 51.8/56.0 | 28.7/27.3 | 51.2/49.1 | 62.0/72.8 | 50.9/49.5 | 52.2 | 54.7 |
| ASearcher-Local-7B | 7B | 72.3/77.6 | 62.6/67.6 | 55.0/60.0 | 34.4/32.6 | 55.6/54.5 | 68.1/79.3 | 57.9/55.9 | **58.0** | **61.0** |
| QwQ-32B Direct Gen. | 32B | 34.6/35.4 | 37.1/40.2 | 56.9/61.6 | 16.8/16.1 | 36.9/38.2 | 65.4/75.8 | 27.9/26.3 | 39.4 | 41.9 |
| Search-R1-14B | 14B | 48.2/49.8 | 56.2/58.9 | 52.8/51.2 | 27.0/25.7 | 60.0/51.2 | 71.0/79.9 | 56.1/54.3 | 53.0 | 53.0 |
| Search-R1-32B | 32B | 63.1/67.5 | 60.5/64.0 | 60.0/61.6 | 34.4/32.9 | 60.8/52.2 | 72.0/82.1 | 60.3/58.2 | 58.7 | 59.8 |
| ASearcher-Local-14B | 14B | 72.2/79.1 | 65.1/71.0 | 59.4/64.8 | 35.6/34.6 | 56.6/56.1 | 71.6/84.0 | 57.6/55.9 | **59.7** | **63.6** |

### 训练配置（§3.4, §4.1，全文核对）

| 项 | 7B/14B | ASearcher-Web-QwQ |
|---|---|---|
| Turn limit | 32 | 128 |
| Batch size | 128 | 64 |
| 训练数据规模 | 35k | 35k |
| 总 GPU hours | not-available（全文仅给 QwQ 的 16k H800） | ~16k H800 |
| RL 算法 | GRPO（Eq.1，token-level PPO clip `[1−ε,1+ε]` + 组内 advantage `Â_i`；组大小 G = not-available，全文仅写符号 G 未给值） | 同 |
| Reward | format × F1（乘法） | LLM-as-Judge（Qwen2.5-72B-Instruct，无 format reward） |
| 过滤 | Dynamic Filtering（zero-advantage query 移除） | 同 |
| Curriculum | — | 两阶段：stage1 混合难度 / stage2 仅 ≥5 tool calls 题 |
| Base model | Qwen2.5-7B / 14B | QwQ-32B（prompt-based LRM agent） |
| 评测 benchmark 配置 | HotpotQA/2WikiMQA/MuSiQue 各 1000 随机采样；Bamboogle/Frames/GAIA/xBench 用 full test；GAIA 用 103 题 text-only validation subset [18] | 同 |

## 与同类对比

- **vs Search-R1 [11]（RL+search 直接对标）。** 机制差异：(i) Search-R1 **仅 search tool、无 browsing**；ASearcher search + browser 双 tool 且网页 summarization 端到端 RL 训练（Fig.2）。(ii) Search-R1 turn limit ≤ 10（训练时仅 4）；ASearcher 放到 32（7B/14B）/ 128（QwQ）。(iii) Search-R1 用 retrieved token masking 隔离检索文档梯度；ASearcher 走另一极端——**summarization 也是 LLM 生成、也参与 RL 梯度**。效果差距（Table 4）：GAIA Avg@4 ASearcher-Web-QwQ-v2 58.7 vs Search-R1-32B 28.6（+30.1）；xBench 51.1 vs 19.5（+31.6）；Frames 74.5 vs 44.1（+30.4）。在 multi-hop QA 上 ASearcher-Local-7B F1 58.0 vs Search-R1-7B 54.3（Table 2）。
- **vs Search-o1 (QwQ) [18]（prompt-based LRM agent，无 agentic 训练）。** 机制差异：Search-o1 直接用 QwQ-32B 的内置 reasoning 拼 tool-use prompt，**不训练**；ASearcher 在 QwQ 上做端到端 RL fine-tune。case study（§2/Appendix A）显示 Search-o1 能做大量 tool calls 但**不能 verify 错误结论**、易 miss key info；ASearcher 学到 uncertainty-aware reasoning + grounded verification。效果（Table 4）：GAIA 58.7 vs 48.1，xBench 51.1 vs 40.3，Frames 74.5 vs 63.6。
- **vs SimpleDeepSearcher-QwQ [32] / WebThinker-QwQ [19] / WebDancer-QwQ [39]（offline-RL/SFT 微调 prompt-based agent）。** 机制差异：这些走 **offline RL / SFT on simulated trajectories**；ASearcher 走 **online RL**（§1 引 [43,6,31] online > offline）。Table 4 全部被 ASearcher 超越：WebThinker 42.5/32.8/57.7、SimpleDS 47.6/35.8/67.0、WebDancer 47.4/40.0/63.8 vs ASearcher 58.7/51.1/74.5。
- **vs R1-Searcher [30] / DeepResearcher [49]（7B RL search agent）。** ASearcher-Local-7B 在 multi-hop/single-hop QA suite 上 F1 58.0 / LasJ 61.0 全面领先 R1-Searcher-7B（52.2/54.7）与 DeepResearcher-7B（54.9/58.3）（Table 2/3）。
- **vs 商业 deep research 系统。** 单模型 ASearcher-Web-QwQ-v2 仍落后 Kimi-Researcher / OpenAI DeepResearch / o3 / Claude-4-Sonnet；但 **+ Summary=DeepSeek-V3 + K=16 test-time search** 后 GAIA 71.8（超 DeepResearch 67.0、Claude-4-Sonnet 68.3、逼近 o3 70.5）、xBench 75.0（超 o3 66.7、Claude-4 64.6，逼近 Kimi-Researcher 69.0）、Frames 83.4（逼近 o3 84.0），HLE-500 24.6 仍落后 Kimi-Researcher 26.9。作者强调这是 **zero-shot transfer manner**——summarizer 与 test-time 聚合都未参与训练。

## 跨论文关系（→ MOC 谱系）

- **直接建立在 [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] 之上**（§1 .txt 原文 "Building up on AReaL [7], our fully asynchronous system avoids long trajectories from blocking the training by decoupling trajectory execution from model updates"）。AREAL 提供 async-RL 系统底座（rollout/train decouple + staleness-aware rate limiting + decoupled PPO），ASearcher 把它从 long-CoT reasoning 迁到 long-horizon agentic search，并把 turn limit 从 R1 式 reasoning 长度问题推广到 tool-call horizon 问题（turn 128 / output >400k tokens）。AREAL §8 自限单 turn reasoning，留 multi-turn agentic 给后续工作——ASearcher 正是这一展望的产出。
- **算法层承接 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]（R1 outcome-RL 根）**：GRPO + sparse outcome reward + dynamic filtering 直接承 R1/DeepSeekMath GRPO 路线（弃 GAE + value model，见 [[high-dimensional-continuous-control-using-generalized-advantage-estimation]] → GRPO 演化）。把 outcome-RL 从"数学/代码可验证 reward"推广到"LLM-as-Judge 软 reward"（LRM 训练用 Qwen2.5-72B-Instruct 作 judge）。
- **直接对标并突破 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]（Search-R1，RL+search 范式根）**：Search-R1 的 B=4 action budget / ≤10 turn 是 ASearcher 要打破的边界。Search-R1 确立 outcome-RL + tool-use rollout + retrieved token masking 范式；ASearcher 选择 **不 mask** retrieved token 而是让 LLM 自己 summarize 网页（end-to-end RL），是 Search-R1 范式的另一分支演化。Table 4 GAIA +30.1 abs 提升。
- **与 [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]（SAO）形成 async-RL 系统层 vs 算法层互补**：AREAL=系统层 async substrate、SAO=算法层（单 rollout async + DIS decoupled importance sampling + value 设计，修正 R1/GRPO group-wise 在异步场景失效）；ASearcher 复用 AREAL 系统底座但 RL 算法仍用标准 GRPO（未做 SAO 式算法层修正）——是 AREAL 系统在 agentic search workload 的应用实例，未触及 SAO 解决的 group-wise advantage 在 staleness 下的失效问题（注：ASearcher 用 LLM-as-Judge 软 reward + dynamic filtering 部分规避，但未理论处理 staleness）。
- **与 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]→[[kimi-k2-open-agentic-intelligence]] / [[kimi-k2-5-visual-agentic-intelligence]] agentic RL 模型线对照**：Kimi-Researcher（Moonshot）作为商业 baseline 出现在 Table 5（xBench 69.0 / Frames 78.8 / HLE-500 26.9），是 ASearcher 零样本 + test-time scaling 追赶的目标；K2/K2.5 走 MoE backbone + MuonClip + K1.5 online mirror descent RL 路线，ASearcher 走 dense QwQ-32B + GRPO + AREAL async 路线——两条独立的开源 agentic RL 路径。
- **与 [[high-dimensional-continuous-control-using-generalized-advantage-estimation]] 间接关联**：GAE 是 PPO 默认 advantage estimator；ASearcher 走 GRPO 路线（弃 GAE + value model），继承自 R1/DeepSeekMath 的简化反应。
- **case study 中 Search-R1-32B 失败模式（无法分解 query、hallucinate、短 horizon）** 正是 Search-R1 B=4 turn limit 的直接后果，构成对 [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] 边界的经验证伪。

## 局限与边界

- **未做算法层 async 修正。** ASearcher 复用 AREAL 的系统层 async（rollout/train decouple），但 RL 算法仍是标准 GRPO（Eq.1，group-wise advantage，single π_old）。当 trajectory 跨多 policy version 时（AREAL §4.2 / SAO 都指出问题），group-wise advantage 在 staleness 下理论上失效——ASearcher 用 LLM-as-Judge 软 reward + dynamic filtering 工程性缓解，但未如 SAO 那样做 decoupled importance sampling 的理论修正。是否在更大 staleness 下仍稳定，全文未给消融（not-available，已核对）。
- **单模型仍落后商业 deep research。** ASearcher-Web-QwQ-v2 单模型 GAIA 58.7 / xBench 51.1 / Frames 74.5 / HLE-500 21.5，全面落后 Kimi-Researcher（69.0/78.8/26.9）、o3（70.5/66.7/84.0/20.2）、Claude-4-Sonnet（68.3/64.6/80.7/20.3）、OpenAI DeepResearch（67.0）。追平需外挂 DeepSeek-V3 summarizer + K=16 test-time search——后者本质是 inference-time 算力换分，非模型本身能力。
- **7B 学不会 webpage browsing（§4.3）。** 7B 在 zero RL 训练 setting 下 capacity 不足以稳定学会 summarize lengthy webpages，14B 在训练后期才习得。说明 end-to-end RL web summarization 存在 scale 门槛，7B 以下不可用——全文未给 7B 的补救方案（如蒸馏 summarizer，not-available，已核对）。
- **数据合成仍依赖 seed 质量 + 强 LRM。** 合成 pipeline 从 14,107 seed 出发，依赖 Wikipedia 取 related fact + QwQ-32B 做 difficulty measurement；seed 偏向（HotpotQA/2WikiMultiHopQA 风格）会限制合成题分布。3 步 verification 也依赖 LLM 判断，error 可累积。25,624 最终合成集相对 R1 类工作规模仍偏小。
- **turn limit 128 是工程设定非理论上界。** 全文给出"tool calls >100、tokens >400k"是训练时极值（abstract 原文），并未系统消融 turn limit ∈ {32, 64, 128, 256} 的边际收益曲线（not-available，已核对）；Fig.6 (Left) 只在推理时给 minimum-turn scaling（6–12）的 accuracy 增益，未给训练 turn limit 的 ablation。
- **LLM-as-Judge reward 的偏差未充分讨论。** LRM 训练用 Qwen2.5-72B-Instruct 作 judge，judge 自身的 bias / 与被评模型同源（都属 Qwen 系）可能高估；全文未做 judge 与 policy 解耦的稳健性检验（not-available，已核对）。
- **未触及 multi-modal search / 长文档理解。** GAIA 含图像/PDF 任务，ASearcher 仅做 text-only 103 题 validation subset（§4.1 .txt "we use the 103 examples from the text-only validation subset"）；对多模态 GAIA 任务未评估。
- **local→web 泛化仅在 Wikipedia 2018 vs real web 上验证。** ASearcher-Local-14B zero-shot web 表现好（F1 60.0 / LasJ 65.6），但未测试 local→web 在 distribution shift 更大（如非英文、时效性强）的查询上是否仍泛化（not-available，已核对）。
- **GRPO 群体采样未给 G 的大小与样本效率分析。** Eq.1 中 G 条 trajectory 的具体值、与样本效率/收敛速度的关系未讨论（继承 R1 默认，未消融，not-available，全文已核对 §3.4 仅写符号 G）。
